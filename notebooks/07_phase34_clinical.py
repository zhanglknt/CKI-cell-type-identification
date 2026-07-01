"""
CKI Phase 3.4 Supplement: Paired/Unpaired + Clinical Severity Analysis
======================================================================
Completes the reproducibility package with two missing analyses:

Part A: Paired vs Unpaired Tumor-Normal Comparison
  - Identifies patients with both tumor and normal samples
  - Computes paired TN omega (same patient) vs unpaired TN omega
  - Reports paired/unpaired ratio and Mann-Whitney tests per cancer type

Part B: Clinical Severity Stratification
  - LIHC: Edmondson grade (G1-G4), Jonckheere-Terpstra trend test
  - BRCA: PAM50 subtype (Basal/HER2/LumA/LumB/Normal), Kruskal-Wallis
  - LUAD: EGFR/KRAS mutation status, Kruskal-Wallis

Data sources:
  - TCGA TPM: data/tcga/tcga_RSEM_gene_tpm.gz (UCSC Xena)
  - LIHC grade: data/tcga/lihc_patient_clinical.json (cBioPortal export)
  - LUAD mutations: data/tcga/luad_egfr_kras_mutations.json (cBioPortal export)
  - BRCA PAM50: fetched live from cBioPortal API (brca_tcga_pub study)
  - HK genes: data/housekeeping/Human_Mouse_Common.csv

Requirements:
  - Python 3.13.12
  - numpy 2.4.6, scipy 1.17.1, pandas 2.3.3, matplotlib 3.10.9
  - scikit-learn 1.8.0 (for PAM50)
  - cki 0.3.1 (editable install from project root)

Output:
  - results/phase34_clinical_paired_unpaired.csv
  - results/phase34_clinical_severity.csv
  - results/phase34_clinical_plots.png
  - results/phase34_clinical_report.md
"""
import sys, os, json, time, gzip, warnings
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from collections import Counter

from cki.core import compute_omega
from scipy.stats import mannwhitneyu, kruskal

warnings.filterwarnings("ignore")

np.random.seed(42)

# ====================================================================
# Config
# ====================================================================
TCGA_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\tcga_RSEM_gene_tpm.gz")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
PROBEMAP_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\probemap.tsv")
LIHC_CLINICAL_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\lihc_patient_clinical.json")
LUAD_MUTATION_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\luad_egfr_kras_mutations.json")

RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

N_TOP_KF = 200
MAX_PAIRS_TT = 2000
MAX_PAIRS_TN = 2000
RANDOM_SEED = 42

TARGET = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

# Font
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "Microsoft YaHei"
    plt.rcParams["axes.unicode_minus"] = False

# ====================================================================
# 0. Preload gene mappings & clinical data
# ====================================================================
print("=" * 60)
print("0. Loading dependencies...")
print("=" * 60)

pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol

symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)

hk_df = pd.read_csv(HK_FILE)
hk_raw = hk_df.iloc[:, 0].dropna().astype(str)
hk_human = set()
for row in hk_raw:
    parts = row.split(";")
    if len(parts) >= 2:
        hk_human.add(parts[1].strip())
print(f"  HK gene symbols: {len(hk_human)}, probeMap: {len(ens_to_symbol)}")

# Load LIHC clinical data (Edmondson grade)
lihc_grade_map = {}
if LIHC_CLINICAL_FILE.exists():
    with open(LIHC_CLINICAL_FILE) as f:
        lihc_clinical = json.load(f)
    for entry in lihc_clinical:
        if entry["clinicalAttributeId"] == "GRADE":
            patient_id = entry["patientId"]  # TCGA-XX-XXXX
            grade = entry["value"]  # G1-G4
            if grade in ("G1", "G2", "G3", "G4"):
                lihc_grade_map[patient_id] = grade
    print(f"  LIHC grade annotations: {len(lihc_grade_map)} patients")
    grade_counts = Counter(lihc_grade_map.values())
    for g in ("G1", "G2", "G3", "G4"):
        print(f"    {g}: {grade_counts.get(g, 0)}")

# Load LUAD mutation data
luad_mutation_map = {}
if LUAD_MUTATION_FILE.exists():
    with open(LUAD_MUTATION_FILE) as f:
        luad_mut = json.load(f)
    # Map 15-char sample ID -> mutation group
    for sid_full in luad_mut.get("egfr_samples", []):
        sid_short = sid_full[:15]
        luad_mutation_map[sid_short] = "EGFR"
    for sid_full in luad_mut.get("kras_samples", []):
        sid_short = sid_full[:15]
        if sid_short in luad_mutation_map:
            luad_mutation_map[sid_short] = "EGFR+KRAS"
        else:
            luad_mutation_map[sid_short] = "KRAS"
    mut_counts = Counter(luad_mutation_map.values())
    for k, v in sorted(mut_counts.items()):
        print(f"  LUAD {k}: {v}")

# Fetch BRCA PAM50 data from cBioPortal API (with local cache)
pam50_map = {}
PAM50_CACHE = RESULTS_DIR / "phase34_pam50_cache.json"
if PAM50_CACHE.exists():
    print("  Loading BRCA PAM50 from cache...")
    with open(PAM50_CACHE) as f:
        pam50_map = json.load(f)
    print(f"  BRCA PAM50 entries (cached): {len(pam50_map)}")
else:
    print("  Fetching BRCA PAM50 from cBioPortal API...")
    try:
        url = "https://www.cbioportal.org/api/studies/brca_tcga_pub/clinical-data?clinicalDataType=SAMPLE"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            brca_data = json.loads(resp.read())
        for item in brca_data:
            if item.get("clinicalAttributeId") == "PAM50_SUBTYPE":
                sid = item.get("sampleId", "")[:15]
                val = item.get("value", "")
                if val and val not in ("NA", "nan", ""):
                    pam50_map[sid] = val
        print(f"  BRCA PAM50 entries: {len(pam50_map)}")
        # Cache for next run
        with open(PAM50_CACHE, "w") as f:
            json.dump(pam50_map, f)
        print(f"  Cached to {PAM50_CACHE}")
    except Exception as e:
        print(f"  WARNING: cBioPortal API failed ({e})")
        print("  BRCA PAM50 analysis will be skipped. Download manually from:")
        print("  https://www.cbioportal.org/study/summary?id=brca_tcga_pub")
if pam50_map:
    pam50_counts = Counter(pam50_map.values())
    for k, v in sorted(pam50_counts.items()):
        print(f"    {k}: {v}")

# ====================================================================
# 1. Parse TCGA sample metadata (reuse from phase34_v2)
# ====================================================================
print("\n" + "=" * 60)
print("1. Parsing sample metadata...")
print("=" * 60)

TSS_TO_PROJECT = {
    "A1":"TCGA-BRCA","A2":"TCGA-BRCA","A7":"TCGA-BRCA","A8":"TCGA-BRCA",
    "AN":"TCGA-BRCA","AO":"TCGA-BRCA","AQ":"TCGA-BRCA","AR":"TCGA-BRCA",
    "B6":"TCGA-BRCA","BH":"TCGA-BRCA","C8":"TCGA-BRCA","D8":"TCGA-BRCA",
    "E2":"TCGA-BRCA","EW":"TCGA-BRCA","GI":"TCGA-BRCA","WT":"TCGA-BRCA",
    "XX":"TCGA-BRCA","E9":"TCGA-BRCA","GM":"TCGA-BRCA","HN":"TCGA-BRCA",
    "JL":"TCGA-BRCA","LD":"TCGA-BRCA","LL":"TCGA-BRCA","MS":"TCGA-BRCA",
    "OL":"TCGA-BRCA","PE":"TCGA-BRCA","PL":"TCGA-BRCA","S3":"TCGA-BRCA",
    "UL":"TCGA-BRCA","V7":"TCGA-BRCA","W8":"TCGA-BRCA","WV":"TCGA-BRCA",
    "05":"TCGA-LUAD","35":"TCGA-LUAD","38":"TCGA-LUAD","44":"TCGA-LUAD",
    "49":"TCGA-LUAD","50":"TCGA-LUAD","55":"TCGA-LUAD","64":"TCGA-LUAD",
    "67":"TCGA-LUAD","73":"TCGA-LUAD","75":"TCGA-LUAD","78":"TCGA-LUAD",
    "86":"TCGA-LUAD","91":"TCGA-LUAD","93":"TCGA-LUAD","97":"TCGA-LUAD",
    "J2":"TCGA-LUAD","L3":"TCGA-LUAD","L4":"TCGA-LUAD","M1":"TCGA-LUAD",
    "MP":"TCGA-LUAD","MT":"TCGA-LUAD","N1":"TCGA-LUAD","N6":"TCGA-LUAD",
    "O1":"TCGA-LUAD","S2":"TCGA-LUAD","TR":"TCGA-LUAD","TV":"TCGA-LUAD",
    "TQ":"TCGA-LUAD","NJ":"TCGA-LUAD","KN":"TCGA-LUAD","LF":"TCGA-LUAD",
    "18":"TCGA-LUSC","21":"TCGA-LUSC","22":"TCGA-LUSC","33":"TCGA-LUSC",
    "34":"TCGA-LUSC","37":"TCGA-LUSC","39":"TCGA-LUSC","43":"TCGA-LUSC",
    "51":"TCGA-LUSC","52":"TCGA-LUSC","56":"TCGA-LUSC","60":"TCGA-LUSC",
    "63":"TCGA-LUSC","66":"TCGA-LUSC","68":"TCGA-LUSC","70":"TCGA-LUSC",
    "77":"TCGA-LUSC","85":"TCGA-LUSC","90":"TCGA-LUSC","92":"TCGA-LUSC",
    "94":"TCGA-LUSC","96":"TCGA-LUSC","98":"TCGA-LUSC","CC":"TCGA-LUSC",
    "L5":"TCGA-LUSC","N2":"TCGA-LUSC","NK":"TCGA-LUSC","Q1":"TCGA-LUSC",
    "IE":"TCGA-LUSC","IF":"TCGA-LUSC","IG":"TCGA-LUSC",
    "BC":"TCGA-LIHC","DD":"TCGA-LIHC","ED":"TCGA-LIHC","EP":"TCGA-LIHC",
    "ES":"TCGA-LIHC","FV":"TCGA-LIHC","FY":"TCGA-LIHC","G3":"TCGA-LIHC",
    "GJ":"TCGA-LIHC","HP":"TCGA-LIHC","HU":"TCGA-LIHC","K7":"TCGA-LIHC",
    "KR":"TCGA-LIHC","LG":"TCGA-LIHC","NI":"TCGA-LIHC","O8":"TCGA-LIHC",
    "PD":"TCGA-LIHC","QN":"TCGA-LIHC","RC":"TCGA-LIHC","RG":"TCGA-LIHC",
    "T6":"TCGA-LIHC","UB":"TCGA-LIHC","WQ":"TCGA-LIHC","XR":"TCGA-LIHC",
    "YA":"TCGA-LIHC","ZP":"TCGA-LIHC","ZS":"TCGA-LIHC",
    "MI":"TCGA-LIHC","F5":"TCGA-LIHC",
    "A3":"TCGA-KIRC","AK":"TCGA-KIRC","AL":"TCGA-KIRC","AY":"TCGA-KIRC",
    "B0":"TCGA-KIRC","B1":"TCGA-KIRC","B2":"TCGA-KIRC","B3":"TCGA-KIRC",
    "B4":"TCGA-KIRC","B8":"TCGA-KIRC","BP":"TCGA-KIRC","BW":"TCGA-KIRC",
    "CJ":"TCGA-KIRC","CW":"TCGA-KIRC","CZ":"TCGA-KIRC","DV":"TCGA-KIRC",
    "DX":"TCGA-KIRC","EU":"TCGA-KIRC","GK":"TCGA-KIRC","HE":"TCGA-KIRC",
    "I6":"TCGA-KIRC","K6":"TCGA-KIRC","KL":"TCGA-KIRC","MM":"TCGA-KIRC",
    "MW":"TCGA-KIRC","P4":"TCGA-KIRC","Q2":"TCGA-KIRC","RG":"TCGA-KIRC",
    "UZ":"TCGA-KIRC","V5":"TCGA-KIRC","XM":"TCGA-KIRC","YE":"TCGA-KIRC",
}

t0_total = time.time()

with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")
all_sample_ids = header_line[1:]

# Build project -> (tumor_ids, normal_ids) with participant info
proj_tumor = {}
proj_normal = {}
sample_to_participant = {}
sample_to_project = {}

for sid in all_sample_ids:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj is None or proj not in TARGET:
        continue
    sc = parts[3][:2]
    participant = "-".join(parts[:3])  # TCGA-TSS-Participant
    sample_to_participant[sid] = participant
    sample_to_project[sid] = proj
    if sc == "01":
        proj_tumor.setdefault(proj, []).append(sid)
    elif sc == "11":
        proj_normal.setdefault(proj, []).append(sid)

usable = []
for proj in TARGET:
    nt = len(proj_tumor.get(proj, []))
    nn = len(proj_normal.get(proj, []))
    if nt >= 30 and nn >= 10:
        usable.append(proj)
        print(f"  {proj}: T={nt}, N={nn}")
    else:
        print(f"  {proj}: T={nt}, N={nn} -> SKIP")

# ====================================================================
# 2. Data loading (reuse from phase34_v2)
# ====================================================================

def load_cancer_data(cancer, tumor_ids, normal_ids):
    """Load expression matrix for ONE cancer type with per-cancer gene filtering."""
    wanted = set(tumor_ids + normal_ids)
    
    col_idx_map = {}
    for k, sid in enumerate(all_sample_ids, 1):
        if sid in wanted:
            col_idx_map[sid] = k
    
    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)
    
    # Pass 1: count qualifying genes
    gene_names = []
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            has_expr = False
            for ci in col_arr:
                if ci < len(parts):
                    try:
                        if float(parts[ci]) > 0:
                            has_expr = True
                            break
                    except (ValueError, IndexError):
                        pass
            if has_expr:
                gene_names.append(parts[0])
    
    n_genes = len(gene_names)
    
    # Pass 2: fill matrix
    expr = np.zeros((len(sample_list), n_genes), dtype=np.float32)
    gene_idx = 0
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            if gene_idx < n_genes and parts[0] == gene_names[gene_idx]:
                for si, ci in enumerate(col_arr):
                    if ci < len(parts):
                        try:
                            expr[si, gene_idx] = float(parts[ci])
                        except (ValueError, IndexError):
                            pass
                gene_idx += 1
                if gene_idx >= n_genes:
                    break
    
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]
    expr_log = np.log2(np.maximum(expr, 0) + 0.001)
    
    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)
    
    tumor_mask = np.array([s in tumor_ids for s in sample_list])
    normal_mask = np.array([s in normal_ids for s in sample_list])
    
    return expr_log, hk_arr, tumor_mask, normal_mask, genes, sample_list


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


# ====================================================================
# 3. Per-cancer omega computation WITH participant tracking
# ====================================================================
print("\n" + "=" * 60)
print("3. Per-cancer omega analysis (with participant tracking)...")
print("=" * 60)

all_results = {}

for cancer in usable:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")
    
    print(f"  Loading data...")
    expr_log, hk_arr, tumor_mask, normal_mask, genes, sample_list = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal[cancer]
    )
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(normal_mask)[0]
    n_t = len(t_idx)
    n_n = len(n_idx)
    
    # Get participant IDs for each sample
    tumor_sids = [sample_list[i] for i in t_idx]
    normal_sids = [sample_list[i] for i in n_idx]
    tumor_participants = [sample_to_participant[s] for s in tumor_sids]
    normal_participants = [sample_to_participant[s] for s in normal_sids]
    
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}, N={n_n}")
    
    # === TT pairs ===
    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    n_tt_total = len(all_tt)
    np.random.seed(RANDOM_SEED)
    if n_tt_total > MAX_PAIRS_TT:
        tt_pairs = [all_tt[k] for k in np.random.choice(n_tt_total, MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt
    
    omega_tt = np.full((n_t, n_t), np.nan)
    for idx, (i, j) in enumerate(tt_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[t_idx[j], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        omega_tt[i, j] = r["omega"]
        omega_tt[j, i] = r["omega"]
        if (idx + 1) % 500 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)}", end="\r")
    print(f"    TT: {len(tt_pairs)}/{n_tt_total} done")
    
    # === NN pairs ===
    n_nn_total = n_n * (n_n - 1) // 2
    omega_nn = np.full((n_n, n_n), np.nan)
    for i in range(n_n):
        for j in range(i + 1, n_n):
            p1, p2 = expr_log[n_idx[i], :], expr_log[n_idx[j], :]
            id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
            r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
            omega_nn[i, j] = r["omega"]
            omega_nn[j, i] = r["omega"]
    print(f"    NN: {n_nn_total} done")
    
    # === Part A: Paired vs Unpaired TN ===
    all_tn = [(i, j) for i in range(n_t) for j in range(n_n)]
    n_tn_total = len(all_tn)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn
    
    omega_tn = np.full((n_t, n_n), np.nan)
    # Track paired/unpaired for each TN pair
    tn_is_paired = []
    tn_omega_list = []
    
    for idx, (i, j) in enumerate(tn_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[n_idx[j], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        omega_tn[i, j] = r["omega"]
        tn_omega_list.append(r["omega"])
        # Check if same participant
        is_paired = (tumor_participants[i] == normal_participants[j])
        tn_is_paired.append(is_paired)
        if (idx + 1) % 500 == 0:
            print(f"    TN: {idx+1}/{len(tn_pairs)}", end="\r")
    print(f"    TN: {len(tn_pairs)}/{n_tn_total} done")
    
    tn_is_paired = np.array(tn_is_paired)
    tn_omega_arr = np.array(tn_omega_list)
    
    # Compute paired vs unpaired
    paired_omega = tn_omega_arr[tn_is_paired]
    unpaired_omega = tn_omega_arr[~tn_is_paired]
    
    n_paired_pairs = len(paired_omega)
    n_unpaired_pairs = len(unpaired_omega)
    
    paired_mean = np.nanmean(paired_omega) if n_paired_pairs > 0 else np.nan
    unpaired_mean = np.nanmean(unpaired_omega) if n_unpaired_pairs > 0 else np.nan
    paired_unpaired_ratio = paired_mean / unpaired_mean if unpaired_mean > 0 else np.nan
    
    # Mann-Whitney: paired vs unpaired
    if n_paired_pairs >= 5 and n_unpaired_pairs >= 5:
        try:
            _, paired_p = mannwhitneyu(paired_omega, unpaired_omega, alternative="two-sided")
        except:
            paired_p = np.nan
    else:
        paired_p = np.nan
    
    print(f"    Paired TN: n={n_paired_pairs}, mean={paired_mean:.2f}")
    print(f"    Unpaired TN: n={n_unpaired_pairs}, mean={unpaired_mean:.2f}")
    print(f"    Paired/Unpaired ratio: {paired_unpaired_ratio:.3f}, P={paired_p:.2e}" if not np.isnan(paired_p) else f"    Paired/Unpaired ratio: {paired_unpaired_ratio:.3f}")
    
    # === Part B: Clinical severity mapping ===
    
    # -- B1: LIHC Edmondson grade --
    lihc_grade_omega = {}
    if cancer == "TCGA-LIHC" and lihc_grade_map:
        print(f"    LIHC grade stratification...")
        for i in range(n_t):
            participant = tumor_participants[i]
            if participant in lihc_grade_map:
                grade = lihc_grade_map[participant]
                # Use mean of all TT omegas for this tumor as its "perturbation score"
                tt_row = omega_tt[i, :]
                tt_vals_clean = tt_row[~np.isnan(tt_row)]
                if len(tt_vals_clean) > 0:
                    lihc_grade_omega.setdefault(grade, []).append(np.nanmean(tt_vals_clean))
        for g in ("G1", "G2", "G3", "G4"):
            if g in lihc_grade_omega:
                vals = lihc_grade_omega[g]
                print(f"      {g}: n={len(vals)}, mean={np.mean(vals):.2f}, std={np.std(vals):.2f}")
    
    # -- B2: BRCA PAM50 --
    brca_pam50_omega = {}
    if cancer == "TCGA-BRCA" and pam50_map:
        print(f"    BRCA PAM50 stratification...")
        for i in range(n_t):
            sid = tumor_sids[i]
            if sid in pam50_map:
                subtype = pam50_map[sid]
                tt_row = omega_tt[i, :]
                tt_vals_clean = tt_row[~np.isnan(tt_row)]
                if len(tt_vals_clean) > 0:
                    brca_pam50_omega.setdefault(subtype, []).append(np.nanmean(tt_vals_clean))
        for st, vals in sorted(brca_pam50_omega.items()):
            print(f"      {st}: n={len(vals)}, mean={np.mean(vals):.2f}, std={np.std(vals):.2f}")
    
    # -- B3: LUAD EGFR/KRAS --
    luad_mut_omega = {}
    if cancer == "TCGA-LUAD" and luad_mutation_map:
        print(f"    LUAD mutation stratification...")
        for i in range(n_t):
            sid = tumor_sids[i]
            tt_row = omega_tt[i, :]
            tt_vals_clean = tt_row[~np.isnan(tt_row)]
            if len(tt_vals_clean) == 0:
                continue
            omega_val = np.nanmean(tt_vals_clean)
            if sid in luad_mutation_map:
                mut = luad_mutation_map[sid]
                if mut != "EGFR+KRAS":  # exclude double mutants (n=2)
                    luad_mut_omega.setdefault(mut, []).append(omega_val)
            else:
                luad_mut_omega.setdefault("WT", []).append(omega_val)
        for mut, vals in sorted(luad_mut_omega.items()):
            print(f"      {mut}: n={len(vals)}, mean={np.mean(vals):.2f}, std={np.std(vals):.2f}")
    
    # TT stats
    tt_vals = omega_tt[np.triu_indices(n_t, k=1)]
    tt_vals = tt_vals[~np.isnan(tt_vals)]
    nn_vals = omega_nn[np.triu_indices(n_n, k=1)]
    nn_vals = nn_vals[~np.isnan(nn_vals)]
    tn_vals = omega_tn.flatten()
    tn_vals = tn_vals[~np.isnan(tn_vals)]
    
    print(f"    omega_TT: mean={np.nanmean(tt_vals):.1f}, median={np.nanmedian(tt_vals):.1f}")
    print(f"    omega_NN: mean={np.nanmean(nn_vals):.1f}, median={np.nanmedian(nn_vals):.1f}")
    print(f"    omega_TN: mean={np.nanmean(tn_vals):.1f}, median={np.nanmedian(tn_vals):.1f}")
    
    all_results[cancer] = {
        "n_tumor": n_t,
        "n_normal": n_n,
        "tumor_sids": tumor_sids,
        "normal_sids": normal_sids,
        "tumor_participants": tumor_participants,
        "normal_participants": normal_participants,
        "omega_tt": omega_tt,
        "omega_nn": omega_nn,
        "omega_tn": omega_tn,
        "tt_vals": tt_vals,
        "nn_vals": nn_vals,
        "tn_vals": tn_vals,
        "paired_omega": paired_omega,
        "unpaired_omega": unpaired_omega,
        "paired_unpaired_ratio": paired_unpaired_ratio,
        "paired_p_value": paired_p,
        "lihc_grade_omega": lihc_grade_omega,
        "brca_pam50_omega": brca_pam50_omega,
        "luad_mut_omega": luad_mut_omega,
    }

# ====================================================================
# 4. Statistical tests for clinical severity
# ====================================================================
print("\n" + "=" * 60)
print("4. Clinical severity statistical tests...")
print("=" * 60)

clinical_results = []

# LIHC Edmondson trend test
if "TCGA-LIHC" in all_results:
    res = all_results["TCGA-LIHC"]
    grade_omega = res["lihc_grade_omega"]
    if grade_omega:
        # Jonckheere-Terpstra trend test
        try:
            from scipy.stats import jttest_on_ranks
        except ImportError:
            # Fallback: manual Jonckheere-Terpstra
            def jttest_on_ranks_wrapper(groups):
                """Manual Jonckheere-Terpstra test for ordered groups."""
                n_total = sum(len(g) for g in groups)
                if n_total < 2:
                    return 0, 1.0
                # Compute JT statistic: for each earlier group, count later-group members with higher rank
                jt = 0
                for k1 in range(len(groups)):
                    for k2 in range(k1 + 1, len(groups)):
                        for i in range(len(groups[k1])):
                            for j in range(len(groups[k2])):
                                if groups[k1][i] < groups[k2][j]:
                                    jt += 1
                                elif groups[k1][i] == groups[k2][j]:
                                    jt += 0.5
                # Normal approximation
                n = sum(len(g) for g in groups)
                ni_sq_sum = sum(len(g)**2 for g in groups)
                ni_sum_cu = sum(len(g)**3 for g in groups)
                
                E = n * (n - 1) / 4.0
                V = (2*(n**3) + 3*(n**2) - n - ni_sq_sum*(2*n + 3) + ni_sum_cu) / 72.0
                
                if V <= 0:
                    return 0, 1.0
                
                z = (jt - E) / np.sqrt(V)
                from scipy.stats import norm
                p = 2 * (1 - norm.cdf(abs(z)))
                return jt, p
            
            groups = [np.array(grade_omega.get(g, [])) for g in ("G1", "G2", "G3", "G4")]
            groups = [g for g in groups if len(g) > 0]
            if len(groups) >= 3:
                jt_stat, jt_p = jttest_on_ranks_wrapper(groups)
                print(f"  LIHC Edmondson JT trend test: stat={jt_stat:.1f}, P={jt_p:.4f}")
                # Summary
                grade_summary = []
                for g in ("G1", "G2", "G3", "G4"):
                    if g in grade_omega:
                        vals = np.array(grade_omega[g])
                        grade_summary.append({
                            "cancer": "LIHC",
                            "stratification": "Edmondson_grade",
                            "group": g,
                            "n": len(vals),
                            "omega_mean": f"{np.mean(vals):.2f}",
                            "omega_std": f"{np.std(vals):.2f}",
                        })
                clinical_results.extend(grade_summary)
    
# BRCA PAM50 Kruskal-Wallis
if "TCGA-BRCA" in all_results:
    res = all_results["TCGA-BRCA"]
    pam50_omega = res["brca_pam50_omega"]
    if pam50_omega and len(pam50_omega) >= 2:
        groups = [np.array(v) for v in pam50_omega.values() if len(v) > 0]
        if len(groups) >= 2:
            h_stat, h_p = kruskal(*groups)
            print(f"  BRCA PAM50 Kruskal-Wallis: H={h_stat:.2f}, P={h_p:.4f}")
            for st, vals in sorted(pam50_omega.items()):
                clinical_results.append({
                    "cancer": "BRCA",
                    "stratification": "PAM50",
                    "group": st,
                    "n": len(vals),
                    "omega_mean": f"{np.mean(vals):.2f}",
                    "omega_std": f"{np.std(vals):.2f}",
                })

# LUAD mutation Kruskal-Wallis
if "TCGA-LUAD" in all_results:
    res = all_results["TCGA-LUAD"]
    mut_omega = res["luad_mut_omega"]
    # Include EGFR, KRAS, WT (exclude double mutants)
    valid_groups = {k: v for k, v in mut_omega.items() if k in ("EGFR", "KRAS", "WT")}
    if valid_groups and len(valid_groups) >= 2:
        groups = [np.array(v) for v in valid_groups.values() if len(v) > 0]
        if len(groups) >= 2:
            h_stat, h_p = kruskal(*groups)
            print(f"  LUAD mutation Kruskal-Wallis: H={h_stat:.2f}, P={h_p:.4f}")
            for mut, vals in sorted(valid_groups.items()):
                clinical_results.append({
                    "cancer": "LUAD",
                    "stratification": "mutation",
                    "group": mut,
                    "n": len(vals),
                    "omega_mean": f"{np.mean(vals):.2f}",
                    "omega_std": f"{np.std(vals):.2f}",
                })

# ====================================================================
# 5. Save results
# ====================================================================
print("\n" + "=" * 60)
print("5. Saving results...")
print("=" * 60)

# Paired/unpaired results
paired_rows = []
for cancer in usable:
    res = all_results[cancer]
    paired_rows.append({
        "Cancer": cancer,
        "n_Tumor": res["n_tumor"],
        "n_Normal": res["n_normal"],
        "n_Paired_TN": len(res["paired_omega"]),
        "n_Unpaired_TN": len(res["unpaired_omega"]),
        "Paired_mean": f"{np.nanmean(res['paired_omega']):.2f}" if len(res["paired_omega"]) > 0 else "NA",
        "Unpaired_mean": f"{np.nanmean(res['unpaired_omega']):.2f}" if len(res["unpaired_omega"]) > 0 else "NA",
        "Paired_Unpaired_ratio": f"{res['paired_unpaired_ratio']:.3f}" if not np.isnan(res['paired_unpaired_ratio']) else "NA",
        "P_value": f"{res['paired_p_value']:.2e}" if not np.isnan(res['paired_p_value']) else "NA",
        "NN_TT_ratio": f"{np.nanmedian(res['nn_vals'])/np.nanmedian(res['tt_vals']):.2f}" if np.nanmedian(res['tt_vals']) > 0 else "NA",
    })

df_paired = pd.DataFrame(paired_rows)
df_paired.to_csv(RESULTS_DIR / "phase34_clinical_paired_unpaired.csv", index=False)
print(df_paired.to_string(index=False))

# Clinical severity results
if clinical_results:
    df_clinical = pd.DataFrame(clinical_results)
    df_clinical.to_csv(RESULTS_DIR / "phase34_clinical_severity.csv", index=False)
    print("\n" + df_clinical.to_string(index=False))

# ====================================================================
# 6. Visualization
# ====================================================================
print("\n" + "=" * 60)
print("6. Visualization...")
print("=" * 60)

n_plots = (3 if "TCGA-LIHC" in all_results and all_results["TCGA-LIHC"]["lihc_grade_omega"] else 0) + \
          (1 if "TCGA-BRCA" in all_results and all_results["TCGA-BRCA"]["brca_pam50_omega"] else 0) + \
          (1 if "TCGA-LUAD" in all_results and all_results["TCGA-LUAD"]["luad_mut_omega"] else 0) + \
          len(usable)

if n_plots == 0:
    n_plots = 1

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
ax_idx = 0

# 6a. Paired vs Unpaired comparison per cancer
ax = axes[ax_idx]
ax_idx += 1
cancers = usable
x = np.arange(len(cancers))
width = 0.35

paired_means = []
unpaired_means = []
for c in cancers:
    res = all_results[c]
    paired_means.append(np.nanmean(res["paired_omega"]) if len(res["paired_omega"]) > 0 else 0)
    unpaired_means.append(np.nanmean(res["unpaired_omega"]) if len(res["unpaired_omega"]) > 0 else 0)

bars1 = ax.bar(x - width/2, paired_means, width, label="Paired TN", color="#3498DB", alpha=0.8)
bars2 = ax.bar(x + width/2, unpaired_means, width, label="Unpaired TN", color="#E74C3C", alpha=0.8)
for b1, b2, c in zip(bars1, bars2, cancers):
    r = all_results[c]
    if not np.isnan(r["paired_p_value"]):
        sig = "***" if r["paired_p_value"] < 0.001 else "**" if r["paired_p_value"] < 0.01 else "*" if r["paired_p_value"] < 0.05 else "ns"
        ax.text((b1.get_x()+b1.get_width()/2 + b2.get_x()+b2.get_width()/2)/2, 
                max(b1.get_height(), b2.get_height())+1, sig, ha="center", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(cancers, fontsize=8)
ax.set_ylabel("Mean Omega", fontsize=10)
ax.set_title("Paired vs Unpaired Tumor-Normal Omega", fontsize=11, fontweight="bold")
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.3)

# 6b. LIHC Edmondson grade
if "TCGA-LIHC" in all_results and all_results["TCGA-LIHC"]["lihc_grade_omega"]:
    ax = axes[ax_idx]
    ax_idx += 1
    grade_omega = all_results["TCGA-LIHC"]["lihc_grade_omega"]
    grades = ["G1", "G2", "G3", "G4"]
    data = []
    labels = []
    for g in grades:
        if g in grade_omega:
            data.append(grade_omega[g])
            labels.append(f"{g}\nn={len(grade_omega[g])}")
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.5)
    colors = ["#F39C12", "#E67E22", "#E74C3C", "#C0392B"]
    for patch, color in zip(bp["boxes"], colors[:len(data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_title("LIHC: Omega by Edmondson Grade", fontsize=11, fontweight="bold")
    ax.set_ylabel("Omega (TT mean)")
    ax.grid(axis="y", alpha=0.3)

# 6c. BRCA PAM50
if "TCGA-BRCA" in all_results and all_results["TCGA-BRCA"]["brca_pam50_omega"]:
    ax = axes[ax_idx]
    ax_idx += 1
    pam50_omega = all_results["TCGA-BRCA"]["brca_pam50_omega"]
    data = []
    labels = []
    for st in sorted(pam50_omega.keys()):
        data.append(pam50_omega[st])
        labels.append(f"{st}\nn={len(pam50_omega[st])}")
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.5)
    pam50_colors = ["#3498DB", "#9B59B6", "#2ECC71", "#F39C12", "#95A5A6"]
    for patch, color in zip(bp["boxes"], pam50_colors[:len(data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_title("BRCA: Omega by PAM50 Subtype", fontsize=11, fontweight="bold")
    ax.set_ylabel("Omega (TT mean)")
    ax.grid(axis="y", alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=15, ha="right", fontsize=7)

    # 6d. LUAD mutation
if "TCGA-LUAD" in all_results and all_results["TCGA-LUAD"]["luad_mut_omega"]:
    ax = axes[ax_idx]
    ax_idx += 1
    mut_omega = all_results["TCGA-LUAD"]["luad_mut_omega"]
    # Show EGFR, KRAS, WT (ordered)
    order = ["EGFR", "KRAS", "WT"]
    data = []
    labels = []
    for mut in order:
        if mut in mut_omega and len(mut_omega[mut]) > 0:
            data.append(mut_omega[mut])
            labels.append(f"{mut}\nn={len(mut_omega[mut])}")
    
    if data:
        bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.4)
        mut_colors = ["#3498DB", "#E74C3C", "#95A5A6"]
        for patch, color in zip(bp["boxes"], mut_colors[:len(data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title("LUAD: Omega by Mutation Status", fontsize=11, fontweight="bold")
        ax.set_ylabel("Omega (TT mean)")
        ax.grid(axis="y", alpha=0.3)

# 6e. NN/TT ratio bar
ax = axes[ax_idx]
ax_idx += 1
nn_tt_ratios = []
for c in cancers:
    res = all_results[c]
    nn_med = np.nanmedian(res["nn_vals"])
    tt_med = np.nanmedian(res["tt_vals"])
    nn_tt_ratios.append(nn_med / tt_med if tt_med > 0 else 0)

colors_nntt = ["#2ECC71" if r > 1 else "#E74C3C" for r in nn_tt_ratios]
bars = ax.bar(cancers, nn_tt_ratios, color=colors_nntt, alpha=0.7)
for bar, r in zip(bars, nn_tt_ratios):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{r:.2f}", 
            ha="center", fontsize=9, fontweight="bold")
ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="NN = TT")
ax.set_ylabel("NN/TT Omega Ratio", fontsize=10)
ax.set_title("Normal Heterogeneity / Tumor Homogeneity", fontsize=11, fontweight="bold")
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.3)

# Hide unused axes
for i in range(ax_idx, len(axes)):
    axes[i].set_visible(False)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_clinical_plots.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase34_clinical_plots.png")

# ====================================================================
# 7. Report
# ====================================================================
print("\n" + "=" * 60)
print("7. Generating report...")
print("=" * 60)

elapsed = time.time() - t0_total

report = f"""# CKI Phase 3.4 Supplement: Paired/Unpaired & Clinical Severity

## Overview
- Data: TCGA pan-cancer bulk RNA-seq (5 cancer types)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f, n={N_TOP_KF})
- Analysis time: {elapsed:.0f}s

## Part A: Paired vs Unpaired Tumor-Normal Comparison
{df_paired.to_string(index=False)}

## Part B: Clinical Severity Stratification
"""
if clinical_results:
    df_clinical = pd.DataFrame(clinical_results)
    report += df_clinical.to_string(index=False) + "\n"
else:
    report += "(No clinical data available)\n"

report += """
## Statistical Tests
- LIHC Edmondson grade: Jonckheere-Terpstra trend test (ordered G1 < G2 < G3 < G4)
- BRCA PAM50: Kruskal-Wallis test (independent subtypes)
- LUAD EGFR/KRAS: Kruskal-Wallis test (independent groups)

## Data Sources
- TCGA TPM: UCSC Xena (tcga_RSEM_gene_tpm.gz)
- LIHC grade: cBioPortal API (lihc_tcga study, GRADE attribute)
- BRCA PAM50: cBioPortal API (brca_tcga_pub study, PAM50_SUBTYPE attribute)
- LUAD mutations: cBioPortal API (luad_tcga study, EGFR/KRAS mutation status)

## Output Files
- phase34_clinical_paired_unpaired.csv
- phase34_clinical_severity.csv
- phase34_clinical_plots.png
"""

with open(RESULTS_DIR / "phase34_clinical_report.md", "w", encoding="utf-8") as f:
    f.write(report.strip())

print("  Saved: phase34_clinical_report.md")
print(f"\nPhase 3.4 Clinical Supplement complete in {elapsed:.0f}s")
print("Done!")
