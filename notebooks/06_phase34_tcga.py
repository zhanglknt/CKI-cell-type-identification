"""
CKI Phase 3.4: TCGA Tumor Perturbation Analysis
=================================================
Tests CKI omega's ability to detect transcriptomic perturbation in tumor vs normal tissue.
- Data: UCSC Xena TCGA RSEM gene TPM (bulk RNA-seq, pan-cancer)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f)
- Cancer types: ≥5 projects with ≥20 normal samples each
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import gzip, time, warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list, fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics import roc_auc_score
from cki.core import compute_omega, js_divergence

warnings.filterwarnings("ignore")

# === Config ===
TCGA_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\tcga_RSEM_gene_tpm.gz")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

RANDOM_SEED = 42
N_TOP_KF = 200  # per-pair top DE genes for k_f
MIN_NORMAL_SAMPLES = 15  # min normal samples per cancer type
MIN_TUMOR_SAMPLES = 30
MAX_PAIRS_TT = 3000  # cap on TT pairs (random sample) to limit runtime
MAX_PAIRS_TN = 3000  # cap on TN pairs (random sample)

# Target cancer types (will be filtered by actual data availability)
TARGET_PROJECTS = [
    "TCGA-LUAD",   # Lung Adenocarcinoma
    "TCGA-LUSC",   # Lung Squamous Cell Carcinoma
    "TCGA-LIHC",   # Liver Hepatocellular Carcinoma
    "TCGA-KIRC",   # Kidney Renal Clear Cell Carcinoma
    "TCGA-BRCA",   # Breast Invasive Carcinoma
]

# === Font setup ===
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "Microsoft YaHei"
    plt.rcParams["axes.unicode_minus"] = False

# ====================================================================
# 1. Load TCGA TPM matrix
# ====================================================================
print("=" * 60)
print("1. Loading TCGA TPM matrix...")
print("=" * 60)
t0 = time.time()

if not TCGA_FILE.exists():
    raise FileNotFoundError(f"TCGA file not found: {TCGA_FILE}")

# Read header line to get sample IDs
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")

print(f"  Columns (samples): {len(header) - 1}")
print(f"  First 5 sample IDs: {header[1:6]}")

# Parse TCGA barcodes to extract project and sample type
# TCGA barcode: TCGA-[TSS]-[Participant]-[SampleType]...
# TSS (Tissue Source Site) codes map to specific cancer types
# Mapping from TCGA Wiki/codebooks for major projects

TSS_TO_PROJECT = {
    # BRCA
    "A1": "TCGA-BRCA", "A2": "TCGA-BRCA", "A7": "TCGA-BRCA", "A8": "TCGA-BRCA",
    "AN": "TCGA-BRCA", "AO": "TCGA-BRCA", "AQ": "TCGA-BRCA", "AR": "TCGA-BRCA",
    "B6": "TCGA-BRCA", "BH": "TCGA-BRCA", "C8": "TCGA-BRCA", "D8": "TCGA-BRCA",
    "E2": "TCGA-BRCA", "EW": "TCGA-BRCA", "GI": "TCGA-BRCA", "WT": "TCGA-BRCA",
    "XX": "TCGA-BRCA", "E9": "TCGA-BRCA", "GM": "TCGA-BRCA", "HN": "TCGA-BRCA",
    "JL": "TCGA-BRCA", "LD": "TCGA-BRCA", "LL": "TCGA-BRCA", "MS": "TCGA-BRCA",
    "OL": "TCGA-BRCA", "PE": "TCGA-BRCA", "PL": "TCGA-BRCA", "S3": "TCGA-BRCA",
    "UL": "TCGA-BRCA", "V7": "TCGA-BRCA", "W8": "TCGA-BRCA", "WV": "TCGA-BRCA",
    # LUAD
    "05": "TCGA-LUAD", "35": "TCGA-LUAD", "38": "TCGA-LUAD", "44": "TCGA-LUAD",
    "49": "TCGA-LUAD", "50": "TCGA-LUAD", "55": "TCGA-LUAD", "64": "TCGA-LUAD",
    "67": "TCGA-LUAD", "73": "TCGA-LUAD", "75": "TCGA-LUAD", "78": "TCGA-LUAD",
    "86": "TCGA-LUAD", "91": "TCGA-LUAD", "93": "TCGA-LUAD", "97": "TCGA-LUAD",
    "J2": "TCGA-LUAD", "L3": "TCGA-LUAD", "L4": "TCGA-LUAD", "M1": "TCGA-LUAD",
    "MP": "TCGA-LUAD", "MT": "TCGA-LUAD", "N1": "TCGA-LUAD", "N6": "TCGA-LUAD",
    "O1": "TCGA-LUAD", "S2": "TCGA-LUAD", "TR": "TCGA-LUAD", "TV": "TCGA-LUAD",
    "TQ": "TCGA-LUAD", "NJ": "TCGA-LUAD", "KN": "TCGA-LUAD", "LF": "TCGA-LUAD",
    # LUSC
    "18": "TCGA-LUSC", "21": "TCGA-LUSC", "22": "TCGA-LUSC", "33": "TCGA-LUSC",
    "34": "TCGA-LUSC", "37": "TCGA-LUSC", "39": "TCGA-LUSC", "43": "TCGA-LUSC",
    "51": "TCGA-LUSC", "52": "TCGA-LUSC", "56": "TCGA-LUSC", "60": "TCGA-LUSC",
    "63": "TCGA-LUSC", "66": "TCGA-LUSC", "68": "TCGA-LUSC", "70": "TCGA-LUSC",
    "77": "TCGA-LUSC", "85": "TCGA-LUSC", "90": "TCGA-LUSC", "92": "TCGA-LUSC",
    "94": "TCGA-LUSC", "96": "TCGA-LUSC", "98": "TCGA-LUSC", "CC": "TCGA-LUSC",
    "L5": "TCGA-LUSC", "N2": "TCGA-LUSC", "NK": "TCGA-LUSC", "Q1": "TCGA-LUSC",
    "IE": "TCGA-LUSC", "IF": "TCGA-LUSC", "IG": "TCGA-LUSC",
    # LIHC
    "BC": "TCGA-LIHC", "DD": "TCGA-LIHC", "ED": "TCGA-LIHC", "EP": "TCGA-LIHC",
    "ES": "TCGA-LIHC", "FV": "TCGA-LIHC", "FY": "TCGA-LIHC", "G3": "TCGA-LIHC",
    "GJ": "TCGA-LIHC", "HP": "TCGA-LIHC", "HU": "TCGA-LIHC", "K7": "TCGA-LIHC",
    "KR": "TCGA-LIHC", "LG": "TCGA-LIHC", "NI": "TCGA-LIHC", "O8": "TCGA-LIHC",
    "PD": "TCGA-LIHC", "QN": "TCGA-LIHC", "RC": "TCGA-LIHC", "RG": "TCGA-LIHC",
    "T6": "TCGA-LIHC", "UB": "TCGA-LIHC", "WQ": "TCGA-LIHC", "XR": "TCGA-LIHC",
    "YA": "TCGA-LIHC", "ZP": "TCGA-LIHC", "ZS": "TCGA-LIHC", "CC": "TCGA-LIHC",
    "MI": "TCGA-LIHC", "F5": "TCGA-LIHC",
    # KIRC
    "A3": "TCGA-KIRC", "AK": "TCGA-KIRC", "AL": "TCGA-KIRC", "AY": "TCGA-KIRC",
    "B0": "TCGA-KIRC", "B1": "TCGA-KIRC", "B2": "TCGA-KIRC", "B3": "TCGA-KIRC",
    "B4": "TCGA-KIRC", "B8": "TCGA-KIRC", "BP": "TCGA-KIRC", "BW": "TCGA-KIRC",
    "CJ": "TCGA-KIRC", "CW": "TCGA-KIRC", "CZ": "TCGA-KIRC", "DV": "TCGA-KIRC",
    "DX": "TCGA-KIRC", "EU": "TCGA-KIRC", "GK": "TCGA-KIRC", "HE": "TCGA-KIRC",
    "I6": "TCGA-KIRC", "K6": "TCGA-KIRC", "KL": "TCGA-KIRC", "MM": "TCGA-KIRC",
    "MW": "TCGA-KIRC", "P4": "TCGA-KIRC", "Q2": "TCGA-KIRC", "RG": "TCGA-KIRC",
    "UZ": "TCGA-KIRC", "V5": "TCGA-KIRC", "XM": "TCGA-KIRC", "YE": "TCGA-KIRC",
}

def parse_tcga_barcode(barcode):
    """Parse TCGA barcode: TCGA-[TSS]-[Participant]-[SampleType]...
    Use hardcoded TSS->project mapping.
    """
    parts = barcode.split("-")
    if len(parts) >= 4:
        tss = parts[1]
        project = TSS_TO_PROJECT.get(tss, None)
        sample_code = parts[3][:2]  # e.g., "01" or "11"
        participant = "-".join(parts[:3])  # TCGA-TSS-Participant
        return project, sample_code, participant, tss
    return None, None, None, None

# Analyze sample composition
sample_info = []
for sid in header[1:]:
    proj, code, part, tss = parse_tcga_barcode(sid)
    sample_info.append({"sample_id": sid, "project": proj, "sample_code": code, "participant": part, "tss": tss})

df_samples = pd.DataFrame(sample_info)
print(f"\n  Total samples: {len(df_samples)}")

# Count by project
proj_counts = df_samples.groupby("project").size().sort_values(ascending=False)
print(f"  Projects: {len(proj_counts)}")
for proj in TARGET_PROJECTS:
    if proj in proj_counts.index:
        total = proj_counts[proj]
        tumor = ((df_samples["project"] == proj) & (df_samples["sample_code"] == "01")).sum()
        normal = ((df_samples["project"] == proj) & (df_samples["sample_code"] == "11")).sum()
        print(f"    {proj}: total={total}, tumor={tumor}, normal={normal}")
    else:
        print(f"    {proj}: NOT FOUND")

# Filter to usable projects
usable_projects = []
for proj in TARGET_PROJECTS:
    if proj in proj_counts.index:
        tumor = ((df_samples["project"] == proj) & (df_samples["sample_code"] == "01")).sum()
        normal = ((df_samples["project"] == proj) & (df_samples["sample_code"] == "11")).sum()
        if normal >= MIN_NORMAL_SAMPLES and tumor >= MIN_TUMOR_SAMPLES:
            usable_projects.append(proj)
            print(f"  \u2713 {proj}: tumor={tumor}, normal={normal}")

print(f"\n  Usable projects: {len(usable_projects)}")
if not usable_projects:
    print("  ERROR: No projects met criteria. Falling back to all TARGET_PROJECTS with data.")
    usable_projects = [p for p in TARGET_PROJECTS if p in proj_counts.index]

# ====================================================================
# 2. Load expression data (streaming, build gene x sample matrix)
# ====================================================================
print("\n" + "=" * 60)
print("2. Loading expression matrix...")
print("=" * 60)

# Build column indices for samples we want
wanted_cols = set()
for proj in usable_projects:
    proj_samples = df_samples[(df_samples["project"] == proj) &
                               (df_samples["sample_code"].isin(["01", "11"]))]["sample_id"].tolist()
    wanted_cols.update(proj_samples)

# Map sample_id to column index
col_index = {}
for i, sid in enumerate(header[1:], 1):
    if sid in wanted_cols:
        col_index[sid] = i

print(f"  Samples to load: {len(col_index)}")

# Sort sample IDs and precompute column indices (avoid dict lookups in inner loop)
sample_ids = sorted(wanted_cols)
n_samples = len(sample_ids)
# Precompute: for each sample position, the column index in the gzip file
sample_col_indices = np.array([col_index[sid] for sid in sample_ids], dtype=np.int32)
# Also precompute max col index for fast bounds check
max_col_idx = np.max(sample_col_indices)

print(f"  Samples to load: {n_samples}, max file column index: {max_col_idx}")

# === Two-pass parse: pass 1 counts qualifying genes, pass 2 fills numpy matrix ===

# Pass 1: scan file, count genes with any expression > 0 in relevant samples
print("  Pass 1: scanning and counting qualifying genes...")
gene_names_qualifying = []
n_total_pass1 = 0
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()  # skip header
    for line in fh:
        n_total_pass1 += 1
        parts = line.strip().split("\t")
        # Fast check: does any wanted column have expression?
        has_expr = False
        for ci in sample_col_indices:
            if ci < len(parts):
                try:
                    if float(parts[ci]) > 0:
                        has_expr = True
                        break
                except (ValueError, IndexError):
                    pass
        if has_expr:
            gene_names_qualifying.append(parts[0])
        if n_total_pass1 % 10000 == 0:
            print(f"    Scanned {n_total_pass1} genes, kept {len(gene_names_qualifying)}", end="\r")

n_qualifying = len(gene_names_qualifying)
print(f"\n  Pass 1 done: {n_total_pass1} genes scanned, {n_qualifying} qualifying")

# Pre-allocate numpy float32 matrix (samples x genes) - no Python list overhead
print(f"  Pre-allocating {n_samples} x {n_qualifying} float32 matrix ({n_samples * n_qualifying * 4 / 1024**2:.0f} MB)...")
expr_matrix = np.zeros((n_samples, n_qualifying), dtype=np.float32)

# Pass 2: fill numpy matrix directly, gene by gene (column by column)
print("  Pass 2: filling numpy matrix...")
gene_idx = 0
n_total_pass2 = 0
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()  # skip header
    for line in fh:
        n_total_pass2 += 1
        parts = line.strip().split("\t")
        if gene_idx < n_qualifying and parts[0] == gene_names_qualifying[gene_idx]:
            # This is a qualifying gene - fill one column of the matrix
            for sample_i, ci in enumerate(sample_col_indices):
                if ci < len(parts):
                    try:
                        expr_matrix[sample_i, gene_idx] = float(parts[ci])
                    except (ValueError, IndexError):
                        pass  # keep as 0.0
            gene_idx += 1
            if gene_idx % 5000 == 0:
                print(f"    Filled {gene_idx}/{n_qualifying} genes", end="\r")
            if gene_idx >= n_qualifying:
                break  # early exit: all qualifying genes found

print(f"\n  Pass 2 done: filled {gene_idx} genes")
print(f"  Matrix shape: {expr_matrix.shape} (samples x genes)")

# Clean up to free memory
genes = gene_names_qualifying
del gene_names_qualifying, sample_col_indices

print(f"  Matrix shape: {expr_matrix.shape} (samples x genes)")

# Gene filtering: remove genes with mean TPM < 0.5 across samples
gene_means = np.mean(expr_matrix, axis=0)
keep_genes = gene_means >= 0.5
expr_matrix = expr_matrix[:, keep_genes]
genes_filtered = [g for g, keep in zip(genes, keep_genes) if keep]
print(f"  After mean >= 0.5 filter: {len(genes_filtered)} genes")

# Log2 transform (clip negative RSEM values to 0 first)
expr_log = np.log2(np.maximum(expr_matrix, 0) + 0.001)
print(f"  Applied log2(max(TPM, 0) + 0.001)")

# ====================================================================
# 3. Build sample metadata
# ====================================================================
print("\n" + "=" * 60)
print("3. Build sample metadata...")
print("=" * 60)

df_meta = df_samples[df_samples["sample_id"].isin(wanted_cols)].copy()
df_meta = df_meta.set_index("sample_id").loc[sample_ids].reset_index()
df_meta["sample_type"] = df_meta["sample_code"].map({"01": "Tumor", "11": "Normal"})
df_meta["sample_idx"] = range(len(df_meta))

print(f"  Total: {len(df_meta)} samples")
for proj in usable_projects:
    mask = df_meta["project"] == proj
    n_t = ((mask) & (df_meta["sample_type"] == "Tumor")).sum()
    n_n = ((mask) & (df_meta["sample_type"] == "Normal")).sum()
    n_paired = df_meta[mask].groupby("participant").filter(lambda g: set(g["sample_type"]) == {"Tumor", "Normal"})["participant"].nunique()
    print(f"  {proj}: {n_t}T + {n_n}N, {n_paired} paired")

# ====================================================================
# 4. Map Ensembl IDs to gene symbols + Load HK genes
# ====================================================================
print("\n" + "=" * 60)
print("4. Loading probeMap + HK genes...")
print("=" * 60)

PROBEMAP_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\probemap.tsv")
pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
print(f"  probeMap: {len(pm)} entries")

# Build Ensembl ID (no version) -> gene symbol mapping
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol

symbol_to_ens = {}
for ens_id, symbol in ens_to_symbol.items():
    symbol_to_ens.setdefault(symbol, []).append(ens_id)

print(f"  Unique Ensembl IDs: {len(ens_to_symbol)}, gene symbols: {len(symbol_to_ens)}")

# Load HK genes (gene symbols)
hk_df = pd.read_csv(HK_FILE)
hk_raw = hk_df.iloc[:, 0].dropna().astype(str)
hk_human = set()
for row in hk_raw:
    parts = row.split(";")
    if len(parts) >= 2:
        hk_human.add(parts[1].strip())

# Map HK symbols -> Ensembl indices in expression matrix
gene_ens_ids = [g.split(".")[0] for g in genes_filtered]
ens_to_idx = {ens: i for i, ens in enumerate(gene_ens_ids)}

hk_ens_ids = []
for symbol in hk_human:
    if symbol in symbol_to_ens:
        for ens_id in symbol_to_ens[symbol]:
            if ens_id in ens_to_idx:
                hk_ens_ids.append(ens_to_idx[ens_id])

hk_ens_ids = sorted(set(hk_ens_ids))
hk_idx = np.array(hk_ens_ids, dtype=int)

print(f"  Human HK gene symbols: {len(hk_human)}")
print(f"  HK mapped to expression matrix: {len(hk_idx)}")

# ====================================================================
# 5. Helper: per-pair top-N non-HK difference gene selection
# ====================================================================
def select_top_diff_genes(pb1, pb2, hk_idx, n_top=200):
    """Select top-N genes by absolute expression difference, excluding HK genes.
    Returns identity_indices for compute_omega.
    """
    diff = np.abs(pb1 - pb2)
    # Mask out HK genes
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1  # ensure HK genes are never selected
    top_idx = np.argsort(diff)[-n_top:]
    # Only keep those with positive diff (exclude HK genes that had diff=-1)
    top_idx = top_idx[diff[top_idx] >= 0]
    return np.sort(top_idx).astype(int)


# ====================================================================
# 5. Per-cancer-type omega analysis
# ====================================================================
print("\n" + "=" * 60)
print("5. Per-cancer-type omega analysis (v3 hybrid)...")
print("=" * 60)

all_results = {}

for proj in usable_projects:
    print(f"\n--- {proj} ---")

    # Get sample indices for this project
    mask = df_meta["project"] == proj
    proj_meta = df_meta[mask].copy()
    tumor_mask = proj_meta["sample_type"] == "Tumor"
    normal_mask = proj_meta["sample_type"] == "Normal"

    n_tumor = tumor_mask.sum()
    n_normal = normal_mask.sum()

    if n_tumor < 5 or n_normal < 5:
        print(f"  SKIP: insufficient samples (T={n_tumor}, N={n_normal})")
        continue

    # Subset expression matrix
    t_indices = proj_meta[tumor_mask]["sample_idx"].values
    n_indices = proj_meta[normal_mask]["sample_idx"].values

    expr_t = expr_log[t_indices, :]  # tumor samples x genes
    expr_n = expr_log[n_indices, :]  # normal samples x genes

    # Build pseudobulks (one per sample; each sample is already bulk)
    pbs_t = [(f"T{i}", expr_t[i, :]) for i in range(n_tumor)]
    pbs_n = [(f"N{i}", expr_n[i, :]) for i in range(n_normal)]

    # === 5a. Tumor-Tumor omega (random sample to limit runtime) ===
    all_tt_pairs = [(i, j) for i in range(n_tumor) for j in range(i + 1, n_tumor)]
    n_tt_total = len(all_tt_pairs)
    np.random.seed(RANDOM_SEED)
    if n_tt_total > MAX_PAIRS_TT:
        tt_pairs = [all_tt_pairs[k] for k in np.random.choice(n_tt_total, MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt_pairs
    print(f"  Tumor-Tumor: {len(tt_pairs)}/{n_tt_total} pairs sampled...")

    omega_tt = np.zeros((n_tumor, n_tumor))
    omega_tt[:] = np.nan
    for idx, (i, j) in enumerate(tt_pairs):
        pb1, pb2 = pbs_t[i][1], pbs_t[j][1]
        id_idx = select_top_diff_genes(pb1, pb2, hk_idx, n_top=N_TOP_KF)
        r = compute_omega(pb1, pb2, hk_idx, id_idx, w1=1.0, w2=0.0)
        omega_tt[i, j] = r["omega"]
        omega_tt[j, i] = r["omega"]
        if (idx + 1) % 1000 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)}", end="\r")
    print(f"    TT: {len(tt_pairs)}/{len(tt_pairs)} done")

    # === 5b. Normal-Normal omega (keep all, typically small) ===
    n_nn_total = n_normal * (n_normal - 1) // 2
    print(f"  Normal-Normal: {n_nn_total} pairs...")
    omega_nn = np.zeros((n_normal, n_normal))
    omega_nn[:] = np.nan
    for i in range(n_normal):
        for j in range(i + 1, n_normal):
            pb1, pb2 = pbs_n[i][1], pbs_n[j][1]
            id_idx = select_top_diff_genes(pb1, pb2, hk_idx, n_top=N_TOP_KF)
            r = compute_omega(pb1, pb2, hk_idx, id_idx, w1=1.0, w2=0.0)
            omega_nn[i, j] = r["omega"]
            omega_nn[j, i] = r["omega"]

    # === 5c. Tumor-Normal omega (random sample) ===
    all_tn_pairs = [(i, j) for i in range(n_tumor) for j in range(n_normal)]
    n_tn_total = len(all_tn_pairs)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn_pairs[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn_pairs
    print(f"  Tumor-Normal: {len(tn_pairs)}/{n_tn_total} pairs sampled...")

    omega_tn = np.zeros((n_tumor, n_normal))
    omega_tn[:] = np.nan
    for idx, (i, j) in enumerate(tn_pairs):
        pb1, pb2 = pbs_t[i][1], pbs_n[j][1]
        id_idx = select_top_diff_genes(pb1, pb2, hk_idx, n_top=N_TOP_KF)
        r = compute_omega(pb1, pb2, hk_idx, id_idx, w1=1.0, w2=0.0)
        omega_tn[i, j] = r["omega"]
        if (idx + 1) % 1000 == 0:
            print(f"    TN: {idx+1}/{len(tn_pairs)}", end="\r")
    print(f"    TN: {len(tn_pairs)}/{len(tn_pairs)} done")

    # Store results
    all_results[proj] = {
        "omega_tt": omega_tt,
        "omega_nn": omega_nn,
        "omega_tn": omega_tn,
        "n_tumor": n_tumor,
        "n_normal": n_normal,
        "tumor_ids": [pbs_t[i][0] for i in range(n_tumor)],
        "normal_ids": [pbs_n[i][0] for i in range(n_normal)],
    }

    # Summary stats (filter NaN from uncomputed pairs)
    tt_vals_full = omega_tt[np.triu_indices(n_tumor, k=1)]
    nn_vals_full = omega_nn[np.triu_indices(n_normal, k=1)]
    tn_vals_full = omega_tn.flatten()
    tt_vals = tt_vals_full[~np.isnan(tt_vals_full)]
    nn_vals = nn_vals_full[~np.isnan(nn_vals_full)]
    tn_vals = tn_vals_full[~np.isnan(tn_vals_full)]

    print(f"    omega(TT): mean={np.mean(tt_vals):.2f} median={np.median(tt_vals):.2f} std={np.std(tt_vals):.2f}")
    print(f"    omega(NN): mean={np.mean(nn_vals):.2f} median={np.median(nn_vals):.2f} std={np.std(nn_vals):.2f}")
    print(f"    omega(TN): mean={np.mean(tn_vals):.2f} median={np.median(tn_vals):.2f} std={np.std(tn_vals):.2f}")

    # Effect size: log2(TN / mean(TT+NN)/2)
    baseline = (np.mean(tt_vals) + np.mean(nn_vals)) / 2
    effect = np.mean(tn_vals) / baseline
    print(f"    TN/baseline: {effect:.2f}x")

    # Mann-Whitney test
    from scipy.stats import mannwhitneyu
    combined_self = np.concatenate([tt_vals, nn_vals])
    _, p_val = mannwhitneyu(tn_vals, combined_self, alternative="greater")
    print(f"    Mann-Whitney TN > (TT+NN): p={p_val:.2e}")

elapsed = time.time() - t0
print(f"\n  Analysis completed in {elapsed:.1f}s")

# ====================================================================
# 6. Cross-project summary
# ====================================================================
print("\n" + "=" * 60)
print("6. Cross-project summary...")
print("=" * 60)

summary_rows = []
for proj, res in all_results.items():
    tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
    nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
    tn_raw = res["omega_tn"].flatten()
    tt_vals = tt_raw[~np.isnan(tt_raw)]
    nn_vals = nn_raw[~np.isnan(nn_raw)]
    tn_vals = tn_raw[~np.isnan(tn_raw)]

    baseline = (np.mean(tt_vals) + np.mean(nn_vals)) / 2
    effect_ratio = np.mean(tn_vals) / baseline

    from scipy.stats import mannwhitneyu
    combined_self = np.concatenate([tt_vals, nn_vals])
    _, p_val = mannwhitneyu(tn_vals, combined_self, alternative="greater")

    summary_rows.append({
        "Project": proj,
        "n_Tumor": res["n_tumor"],
        "n_Normal": res["n_normal"],
        "omega_TT_mean": f"{np.mean(tt_vals):.2f}",
        "omega_NN_mean": f"{np.mean(nn_vals):.2f}",
        "omega_TN_mean": f"{np.mean(tn_vals):.2f}",
        "TN_Baseline": f"{effect_ratio:.2f}x",
        "p_value": f"{p_val:.2e}",
    })

df_summary = pd.DataFrame(summary_rows)
print(df_summary.to_string(index=False))
df_summary.to_csv(RESULTS_DIR / "phase34_summary.csv", index=False)

# ====================================================================
# 7. Visualization
# ====================================================================
print("\n" + "=" * 60)
print("7. Visualization...")
print("=" * 60)

# 7a. Combined boxplot (Tumor-Tumor, Normal-Normal, Tumor-Normal per project)
fig, axes = plt.subplots(1, len(all_results), figsize=(5 * len(all_results), 5))
if len(all_results) == 1:
    axes = [axes]

all_tt, all_nn, all_tn = [], [], []
all_labels_tt, all_labels_nn, all_labels_tn = [], [], []

for ax, (proj, res) in zip(axes, all_results.items()):
    tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
    nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
    tn_raw = res["omega_tn"].flatten()
    tt = tt_raw[~np.isnan(tt_raw)]
    nn = nn_raw[~np.isnan(nn_raw)]
    tn = tn_raw[~np.isnan(tn_raw)]

    data = [tt, nn, tn]
    labels = ["Tumor-Tumor", "Normal-Normal", "Tumor-Normal"]
    colors = ["#E74C3C", "#2ECC71", "#8E44AD"]

    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    for median in bp["medians"]:
        median.set_color("black")
        median.set_linewidth(1.5)

    ax.set_title(f"{proj}\n(nT={res['n_tumor']}, nN={res['n_normal']})", fontsize=11, fontweight="bold")
    ax.set_ylabel("Omega")
    ax.grid(axis="y", alpha=0.3)

    all_tt.extend(tt)
    all_nn.extend(nn)
    all_tn.extend(tn)
    all_labels_tt.extend([f"{proj}_TT"] * len(tt))
    all_labels_nn.extend([f"{proj}_NN"] * len(nn))
    all_labels_tn.extend([f"{proj}_TN"] * len(tn))

plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_boxplot_per_project.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase34_boxplot_per_project.png")

# 7b. Combined cross-project comparison
fig, ax = plt.subplots(figsize=(12, 6))
projects = list(all_results.keys())
x = np.arange(len(projects))
width = 0.25

data_tt = []
data_nn = []
data_tn = []
for p in projects:
    res = all_results[p]
    tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
    nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
    tn_raw = res["omega_tn"].flatten()
    data_tt.append(np.nanmean(tt_raw))
    data_nn.append(np.nanmean(nn_raw))
    data_tn.append(np.nanmean(tn_raw))

bars1 = ax.bar(x - width, data_tt, width, label="Tumor-Tumor", color="#E74C3C", alpha=0.7)
bars2 = ax.bar(x, data_nn, width, label="Normal-Normal", color="#2ECC71", alpha=0.7)
bars3 = ax.bar(x + width, data_tn, width, label="Tumor-Normal", color="#8E44AD", alpha=0.7)

# Add value labels
for bars, fs in [(bars1, 8), (bars2, 8), (bars3, 8)]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.2, f"{height:.1f}",
                ha="center", va="bottom", fontsize=fs)

ax.set_xticks(x)
ax.set_xticklabels(projects, fontsize=10)
ax.set_ylabel("Mean Omega", fontsize=12)
ax.set_title("CKI Omega: Tumor vs Normal Perturbation (TCGA Pan-Cancer)", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_cross_project_bar.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase34_cross_project_bar.png")

# 7c. Effect size bar chart
fig, ax = plt.subplots(figsize=(10, 5))
effects = []
for proj in projects:
    res = all_results[proj]
    tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
    nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
    tn_raw = res["omega_tn"].flatten()
    tt = np.nanmean(tt_raw)
    nn = np.nanmean(nn_raw)
    tn = np.nanmean(tn_raw)
    baseline = (tt + nn) / 2
    effects.append(tn / baseline)

bars = ax.bar(projects, effects, color=["#E74C3C" if e > 1.5 else "#F39C12" for e in effects], alpha=0.7)
for bar, e in zip(bars, effects):
    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.02, f"{e:.2f}x",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.axhline(y=1.0, color="gray", linestyle="--", linewidth=1, label="Baseline (no perturbation)")
ax.set_ylabel("TN / Baseline Ratio", fontsize=12)
ax.set_title("Tumor Perturbation Effect Size (omega_TN / omega_self)", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_effect_size.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase34_effect_size.png")

# 7d. Combined histogram
if len(projects) >= 2:
    fig, axes = plt.subplots(1, len(projects), figsize=(5 * len(projects), 4))
    if len(projects) == 1:
        axes = [axes]

    for ax, proj in zip(axes, projects):
        res = all_results[proj]
        tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
        nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
        tn_raw = res["omega_tn"].flatten()
        tt = tt_raw[~np.isnan(tt_raw)]
        nn = nn_raw[~np.isnan(nn_raw)]
        tn = tn_raw[~np.isnan(tn_raw)]

        bins = np.linspace(0, max(np.max(tt), np.max(nn), np.max(tn)) * 1.1, 30)
        ax.hist(tt, bins=bins, alpha=0.5, label="Tumor-Tumor", color="#E74C3C", density=True)
        ax.hist(nn, bins=bins, alpha=0.5, label="Normal-Normal", color="#2ECC71", density=True)
        ax.hist(tn, bins=bins, alpha=0.5, label="Tumor-Normal", color="#8E44AD", density=True)
        ax.set_title(proj, fontsize=11, fontweight="bold")
        ax.set_xlabel("Omega")
        ax.set_ylabel("Density")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "phase34_histogram.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: phase34_histogram.png")

# ====================================================================
# 8. Generate report [Phase 3.4 TCGA Tumor Perturbation]
# ====================================================================
print("\n" + "=" * 60)
print("8. Generating report...")
print("=" * 60)

# Build report content
report = f"""# CKI Phase 3.4 Report: TCGA Tumor Perturbation

## Overview
- Data: UCSC Xena TCGA RSEM gene TPM (pan-cancer bulk RNA-seq)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f, n={N_TOP_KF})
- Normalization: log2(TPM + 0.001)
- HK genes: {len(hk_idx)} human HK genes mapped to expression matrix
- Genes after filtering: {len(genes_filtered)} (mean TPM >= 0.5)
- Samples loaded: {len(wanted_cols)}
- Analysis time: {elapsed:.0f}s

## Cancer Types Analyzed
{df_summary.to_string(index=False)}

## Detailed Results
"""

for proj in projects:
    res = all_results[proj]
    tt_raw = res["omega_tt"][np.triu_indices(res["n_tumor"], k=1)]
    nn_raw = res["omega_nn"][np.triu_indices(res["n_normal"], k=1)]
    tn_raw = res["omega_tn"].flatten()
    tt_vals = tt_raw[~np.isnan(tt_raw)]
    nn_vals = nn_raw[~np.isnan(nn_raw)]
    tn_vals = tn_raw[~np.isnan(tn_raw)]

    report += f"""
### {proj}
| Metric | Tumor-Tumor | Normal-Normal | Tumor-Normal |
|--------|-------------|---------------|--------------|
| Mean | {np.mean(tt_vals):.2f} | {np.mean(nn_vals):.2f} | {np.mean(tn_vals):.2f} |
| Median | {np.median(tt_vals):.2f} | {np.median(nn_vals):.2f} | {np.median(tn_vals):.2f} |
| Std | {np.std(tt_vals):.2f} | {np.std(nn_vals):.2f} | {np.std(tn_vals):.2f} |
| N pairs | {len(tt_vals)} | {len(nn_vals)} | {len(tn_vals)} |

- TN / Baseline (mean(TT,NN)): {np.mean(tn_vals) / ((np.mean(tt_vals) + np.mean(nn_vals)) / 2):.2f}x
"""

report += """
## Interpretation
- The TN / Baseline ratio quantifies the perturbation magnitude: >1 means tumor transcriptomes are more divergent from normals than normals are from each other.
- CKI omega should detect this perturbation as elevated k_f (identity gene divergence) relative to stable k_n (HK gene stability).
- A ratio >>1 supports CKI's tumor perturbation application.

## Next Steps
- Phase 3.5: Method comparison (SAMap, SATURN, etc.)
- Phase 4: CKI application papers
"""

with open(RESULTS_DIR / "phase34_report.md", "w", encoding="utf-8") as f:
    f.write(report.strip())

print("  Saved: phase34_report.md")
print(f"\nPhase 3.4 complete. Results in {RESULTS_DIR}/")
print("Done!")
