# -*- coding: utf-8 -*-
"""
TCGA linear-normalization recompute (v44 sensitivity analysis)
==============================================================

Blind-review concern: the authoritative TCGA pipeline (06_phase34_v2.py)
feeds log2(TPM+1) values into cki.core.compute_omega, whose internal
js_divergence maps values to a probability distribution via softmax
(cki.utils.ensure_probability_distribution, mode="softmax"). Since
softmax(log2(x)) is proportional to x**(1/ln 2) = x**1.4427, the published
probability mapping is an undisclosed power transform of (TPM+1).

This script is a LINE-FOR-LINE MIRROR of 06_phase34_v2.py (per-cancer
streaming load, expression>0 gene presence pass, mean TPM >= 0.5 filter,
per-cancer HK mapping, N_TOP_KF=200 per-pair |delta| identity genes,
kn_floor=1e-4, RANDOM_SEED=42, MAX_PAIRS_TT=MAX_PAIRS_TN=2000, same
TT-subsample seeding order) with ONE change only:

    probability mapping  p_i = softmax(log2(TPM+1))
        ->  p_i = (TPM+1) / sum_j (TPM_j + 1)      (linear normalization)

Design decision (isolation of the mapping effect): the per-pair top-200
identity-gene ranking (select_top_diff) is still performed on the
log2(TPM+1) representation, exactly as in v2, so the identity gene SETS
are identical to the authoritative run; only the probability vectors
entering the Jensen-Shannon divergence change.

In the same per-cancer loop (to avoid re-reading the 11 GB matrix) we
also rebuild the 07_phase34_clinical / 83_kf_only_ordering Part B
severity analysis (LIHC Edmondson grade, BRCA PAM50, LUAD EGFR/KRAS)
under the linear mapping, with the published severity convention
kn_floor=0 (raw omega = k_f/k_n), reporting omega / k_f / k_n per
stratum and Jonckheere-Terpstra / Kruskal-Wallis tests for all three
metrics (mirrors notebook 83 Part B).

Outputs (all NEW files, _v44 suffix; nothing under results/ is overwritten):
  results/tcga_linear_norm_v44_summary.csv        per-cancer TT/NN/TN summary
  results/tcga_linear_norm_v44_all_pairs.csv      all pairs, sample-labelled
  results/tcga_linear_norm_v44_<cancer>_pairs.csv per-cancer pair tables
  results/tcga_clinical_severity_v44.csv          strata x metric table
  results/tcga_clinical_severity_v44.json         strata + tests + metadata
"""
import sys, os, json, time, gzip, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, kruskal, norm

warnings.filterwarnings("ignore")

# === Config (verbatim from 06_phase34_v2.py) ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_TUMOR = 30
MIN_NORMAL = 10
MAX_PAIRS_TT = 2000
MAX_PAIRS_TN = 2000
KN_FLOOR = 1e-4

TARGET = [
    "TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"
]

LIHC_CLINICAL_FILE = DATA_DIR / "tcga" / "lihc_patient_clinical.json"
LUAD_MUTATION_FILE = DATA_DIR / "tcga" / "luad_egfr_kras_mutations.json"
PAM50_CACHE = RESULTS_DIR / "phase34_pam50_cache.json"

t0_total = time.time()

# ====================================================================
# Linear-normalization replacements for cki.core (the ONLY change)
# ====================================================================

def js_divergence_linear(a, b):
    """JS divergence (base-2) on linearly normalized distributions.

    p_i = x_i / sum(x), x = TPM+1 (non-negative). Mirrors the structure
    of cki.core.js_divergence with ensure_probability_distribution
    replaced by sum normalization.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    sa = a.sum()
    sb = b.sum()
    if sa <= 0 and sb <= 0:
        return 0.0
    if sa <= 0 or sb <= 0:
        # one side degenerate -> maximal divergence
        return 1.0
    p = a / sa
    q = b / sb
    m = 0.5 * (p + q)
    kl_pm = 0.0
    mask_p = p > 0
    if mask_p.any():
        kl_pm = np.sum(p[mask_p] * np.log2(p[mask_p] / m[mask_p]))
    kl_qm = 0.0
    mask_q = q > 0
    if mask_q.any():
        kl_qm = np.sum(q[mask_q] * np.log2(q[mask_q] / m[mask_q]))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def kn_kf_linear(pb_a, pb_b, hk_idx, id_idx):
    """k_n and k_f under the linear probability mapping."""
    kn = js_divergence_linear(pb_a[hk_idx], pb_b[hk_idx]) if len(hk_idx) else 0.0
    kf = js_divergence_linear(pb_a[id_idx], pb_b[id_idx]) if len(id_idx) else 0.0
    return kn, kf


def omega_from_kn_kf(kn, kf, kn_floor):
    """v2 denominator handling (kn_floor=1e-4) and raw (kn_floor=0)."""
    if kn_floor > 0 and kn < kn_floor:
        omega_floor = kf / kn_floor
    elif kn <= 0.0:
        omega_floor = float("inf")
    else:
        omega_floor = kf / kn
    omega_raw = kf / kn if kn > 0 else float("inf")
    return omega_floor, omega_raw


# ====================================================================
# 0. Preload HK gene mapping + clinical maps (verbatim from v2 / 83)
# ====================================================================
print("=" * 60)
print("0. Loading HK gene mapping and clinical annotations...")
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

# --- clinical maps (verbatim from 83 Part B / 07) ---
lihc_grade_map = {}
if LIHC_CLINICAL_FILE.exists():
    with open(LIHC_CLINICAL_FILE) as f:
        lihc_clinical = json.load(f)
    for entry in lihc_clinical:
        if entry["clinicalAttributeId"] == "GRADE":
            grade = entry["value"]
            if grade in ("G1", "G2", "G3", "G4"):
                lihc_grade_map[entry["patientId"]] = grade

luad_mutation_map = {}
if LUAD_MUTATION_FILE.exists():
    with open(LUAD_MUTATION_FILE) as f:
        luad_mut = json.load(f)
    for sid_full in luad_mut.get("egfr_samples", []):
        luad_mutation_map[sid_full[:15]] = "EGFR"
    for sid_full in luad_mut.get("kras_samples", []):
        sid_short = sid_full[:15]
        if sid_short in luad_mutation_map:
            luad_mutation_map[sid_short] = "EGFR+KRAS"
        else:
            luad_mutation_map[sid_short] = "KRAS"

pam50_map = {}
if PAM50_CACHE.exists():
    with open(PAM50_CACHE) as f:
        pam50_map = json.load(f)
print(f"  LIHC grades: {len(lihc_grade_map)}; LUAD mut: {len(luad_mutation_map)}; "
      f"BRCA PAM50: {len(pam50_map)}")

# ====================================================================
# 1. Parse sample metadata (verbatim from v2, plus participant map from 07)
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

with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

proj_tumor = {}
proj_normal = {}
sample_to_participant = {}
for sid in header_line[1:]:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj is None or proj not in TARGET:
        continue
    sample_to_participant[sid] = "-".join(parts[:3])
    sc = parts[3][:2]
    if sc == "01":
        proj_tumor.setdefault(proj, []).append(sid)
    elif sc == "11":
        proj_normal.setdefault(proj, []).append(sid)

usable = []
for proj in TARGET:
    nt = len(proj_tumor.get(proj, []))
    nn = len(proj_normal.get(proj, []))
    if nt >= MIN_TUMOR and nn >= MIN_NORMAL:
        usable.append(proj)
        print(f"  {proj}: T={nt}, N={nn}")
    else:
        print(f"  {proj}: T={nt}, N={nn} -> SKIP")

print(f"\n  Usable: {len(usable)} cancers")

# ====================================================================
# 2. Per-cancer-type loading (verbatim from v2, returning BOTH the
#    log2 representation for identity-gene ranking and the linear
#    TPM+1 representation for the probability mapping)
# ====================================================================

def load_cancer_data(cancer, tumor_ids, normal_ids):
    """Load expression matrix for ONE cancer type with its own gene filtering."""
    wanted = set(tumor_ids + normal_ids)

    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k

    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)

    # Pass 1: count qualifying genes (expression > 0 in any wanted sample)
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

    # Per-cancer gene filtering: mean TPM >= 0.5
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]

    # Representations: log2(TPM+1) for identity-gene ranking (identical
    # to v2), TPM+1 for the linear probability mapping (the v44 change).
    expr_log = np.log2(np.maximum(expr, 0) + 1)
    expr_lin = np.maximum(expr, 0).astype(np.float64) + 1.0

    # Map HK genes
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

    return expr_log, expr_lin, hk_arr, tumor_mask, normal_mask, genes, sample_list


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    """Select top-N non-HK genes by absolute expression difference (verbatim v2)."""
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


def pair_metrics(i_row, j_row, expr_log, expr_lin, hk_arr):
    """k_n / k_f under the linear mapping; identity genes ranked on log2."""
    p1_log = expr_log[i_row, :]
    p2_log = expr_log[j_row, :]
    id_idx = select_top_diff(p1_log, p2_log, hk_arr, N_TOP_KF)
    kn, kf = kn_kf_linear(expr_lin[i_row, :], expr_lin[j_row, :], hk_arr, id_idx)
    omega_floor, omega_raw = omega_from_kn_kf(kn, kf, KN_FLOOR)
    return kn, kf, omega_floor, omega_raw


# --- manual Jonckheere-Terpstra (verbatim from 83; scipy path unavailable
#     on this machine, so the published runs used this same fallback) ---
def jttest_on_ranks_manual(groups):
    n_total = sum(len(g) for g in groups)
    if n_total < 2:
        return 0, 1.0
    jt = 0
    for k1 in range(len(groups)):
        for k2 in range(k1 + 1, len(groups)):
            for i in range(len(groups[k1])):
                for j in range(len(groups[k2])):
                    if groups[k1][i] < groups[k2][j]:
                        jt += 1
                    elif groups[k1][i] == groups[k2][j]:
                        jt += 0.5
    n = sum(len(g) for g in groups)
    ni_sq_sum = sum(len(g) ** 2 for g in groups)
    ni_sum_cu = sum(len(g) ** 3 for g in groups)
    E = n * (n - 1) / 4.0
    V = (2 * (n ** 3) + 3 * (n ** 2) - n - ni_sq_sum * (2 * n + 3) + ni_sum_cu) / 72.0
    if V <= 0:
        return 0, 1.0
    z = (jt - E) / np.sqrt(V)
    p = 2 * (1 - norm.cdf(abs(z)))
    return jt, p


STRATA = {
    "TCGA-LIHC": ("Edmondson_grade", lambda sid, part: lihc_grade_map.get(part),
                  ["G1", "G2", "G3", "G4"], "jt"),
    "TCGA-BRCA": ("PAM50", lambda sid, part: pam50_map.get(sid),
                  sorted(set(pam50_map.values())), "kw"),
    "TCGA-LUAD": ("mutation", lambda sid, part: luad_mutation_map.get(sid, "WT"),
                  ["WT", "EGFR", "KRAS"], "kw"),
}

# ====================================================================
# 3. Per-cancer computation (TT/NN/TN + clinical severity, one loop)
# ====================================================================
print("\n" + "=" * 60)
print("3. Per-cancer analysis (linear normalization)...")
print("=" * 60)

all_summary = []
all_pair_details = []
severity_rows = []
severity_tests = {}
run_meta = {"seed": RANDOM_SEED, "n_top_kf": N_TOP_KF,
            "kn_floor_main": KN_FLOOR, "kn_floor_severity": 0.0,
            "probability_mapping": "linear (TPM+1)/sum(TPM+1)",
            "identity_gene_ranking_scale": "log2(TPM+1) (unchanged from v2)",
            "per_cancer": {}}

for cancer in usable:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")

    print(f"  Loading data...")
    expr_log, expr_lin, hk_arr, tumor_mask, normal_mask, genes, sample_list = \
        load_cancer_data(cancer, proj_tumor[cancer], proj_normal[cancer])
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(normal_mask)[0]
    n_t = len(t_idx)
    n_n = len(n_idx)
    tumor_sids = [sample_list[i] for i in t_idx]
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}, N={n_n}")

    # === TT pairs (verbatim v2 seeding) ===
    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    n_tt_total = len(all_tt)
    np.random.seed(RANDOM_SEED)
    if n_tt_total > MAX_PAIRS_TT:
        tt_pairs = [all_tt[k] for k in np.random.choice(n_tt_total, MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt

    omega_tt = np.full((n_t, n_t), np.nan)   # raw omega (severity convention)
    kf_tt = np.full((n_t, n_t), np.nan)
    kn_tt = np.full((n_t, n_t), np.nan)
    tt_details = []
    for idx, (i, j) in enumerate(tt_pairs):
        kn, kf, omega_floor, omega_raw = pair_metrics(
            t_idx[i], t_idx[j], expr_log, expr_lin, hk_arr)
        omega_tt[i, j] = omega_tt[j, i] = omega_raw
        kf_tt[i, j] = kf_tt[j, i] = kf
        kn_tt[i, j] = kn_tt[j, i] = kn
        tt_details.append({"pair_type": "TT", "cancer": cancer,
                           "sample_a": tumor_sids[i], "sample_b": tumor_sids[j],
                           "kn": kn, "kf": kf,
                           "omega_floor": omega_floor, "omega_raw": omega_raw})
        if (idx + 1) % 500 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)}", end="\r")
    print(f"    TT: {len(tt_pairs)}/{n_tt_total} done")

    # === NN pairs ===
    n_nn_total = n_n * (n_n - 1) // 2
    nn_details = []
    omega_nn_f = []
    for i in range(n_n):
        for j in range(i + 1, n_n):
            kn, kf, omega_floor, omega_raw = pair_metrics(
                n_idx[i], n_idx[j], expr_log, expr_lin, hk_arr)
            omega_nn_f.append(omega_floor)
            nn_details.append({"pair_type": "NN", "cancer": cancer,
                               "sample_a": sample_list[n_idx[i]],
                               "sample_b": sample_list[n_idx[j]],
                               "kn": kn, "kf": kf,
                               "omega_floor": omega_floor, "omega_raw": omega_raw})
    print(f"    NN: {n_nn_total} done")

    # === TN pairs (continues v2's rng stream, verbatim) ===
    all_tn = [(i, j) for i in range(n_t) for j in range(n_n)]
    n_tn_total = len(all_tn)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn

    tn_details = []
    omega_tn_f = []
    for idx, (i, j) in enumerate(tn_pairs):
        kn, kf, omega_floor, omega_raw = pair_metrics(
            t_idx[i], n_idx[j], expr_log, expr_lin, hk_arr)
        omega_tn_f.append(omega_floor)
        tn_details.append({"pair_type": "TN", "cancer": cancer,
                           "sample_a": tumor_sids[i],
                           "sample_b": sample_list[n_idx[j]],
                           "kn": kn, "kf": kf,
                           "omega_floor": omega_floor, "omega_raw": omega_raw})
        if (idx + 1) % 500 == 0:
            print(f"    TN: {idx+1}/{len(tn_pairs)}", end="\r")
    print(f"    TN: {len(tn_pairs)}/{n_tn_total} done")

    # === v2-style summary (omega with kn_floor=1e-4) ===
    df_c = pd.DataFrame(tt_details + nn_details + tn_details)
    tt_f = df_c[df_c.pair_type == "TT"]["omega_floor"].values
    nn_f = df_c[df_c.pair_type == "NN"]["omega_floor"].values
    tn_f = df_c[df_c.pair_type == "TN"]["omega_floor"].values
    kn_tt_v = df_c[df_c.pair_type == "TT"]["kn"].values
    kn_nn_v = df_c[df_c.pair_type == "NN"]["kn"].values
    kn_tn_v = df_c[df_c.pair_type == "TN"]["kn"].values

    baseline = (np.nanmean(tt_f) + np.nanmean(nn_f)) / 2
    combined = np.concatenate([tt_f, nn_f])
    _, p_val = mannwhitneyu(tn_f, combined, alternative="less") if len(combined) > 0 else (0, 1.0)

    floor_frac = {
        "TT": float(np.mean(np.array(kn_tt_v) < KN_FLOOR)),
        "NN": float(np.mean(np.array(kn_nn_v) < KN_FLOOR)),
        "TN": float(np.mean(np.array(kn_tn_v) < KN_FLOOR)),
    }
    print(f"    omega_TT(floor): mean={np.nanmean(tt_f):.1f}, median={np.nanmedian(tt_f):.1f}")
    print(f"    omega_NN(floor): mean={np.nanmean(nn_f):.1f}, median={np.nanmedian(nn_f):.1f}")
    print(f"    omega_TN(floor): mean={np.nanmean(tn_f):.1f}, median={np.nanmedian(tn_f):.1f}")
    print(f"    kn medians: TT={np.median(kn_tt_v):.3e} NN={np.median(kn_nn_v):.3e} TN={np.median(kn_tn_v):.3e}")
    print(f"    kn<1e-4 fraction: TT={floor_frac['TT']:.3f} NN={floor_frac['NN']:.3f} TN={floor_frac['TN']:.3f}")
    print(f"    TN/baseline: {np.nanmean(tn_f)/baseline:.2f}x, p={p_val:.2e}")

    df_c.to_csv(RESULTS_DIR / f"tcga_linear_norm_v44_{cancer}_pairs.csv", index=False)
    all_pair_details.append(df_c)

    all_summary.append({
        "Project": cancer,
        "n_Tumor": n_t,
        "n_Normal": n_n,
        "n_Genes": len(genes),
        "n_HK": len(hk_arr),
        "omega_TT_mean": f"{np.nanmean(tt_f):.4f}",
        "omega_TT_median": f"{np.nanmedian(tt_f):.4f}",
        "omega_NN_mean": f"{np.nanmean(nn_f):.4f}",
        "omega_NN_median": f"{np.nanmedian(nn_f):.4f}",
        "omega_TN_mean": f"{np.nanmean(tn_f):.4f}",
        "omega_TN_median": f"{np.nanmedian(tn_f):.4f}",
        "kn_TT_median": f"{np.median(kn_tt_v):.6e}",
        "kn_NN_median": f"{np.median(kn_nn_v):.6e}",
        "kn_TN_median": f"{np.median(kn_tn_v):.6e}",
        "floor_frac_TT": f"{floor_frac['TT']:.4f}",
        "floor_frac_NN": f"{floor_frac['NN']:.4f}",
        "floor_frac_TN": f"{floor_frac['TN']:.4f}",
        "TN_Baseline": f"{np.nanmean(tn_f)/baseline:.4f}",
        "p_value": f"{p_val:.3e}",
        "time_s": f"{time.time()-t0_cancer:.0f}",
    })
    run_meta["per_cancer"][cancer] = {"time_s": time.time() - t0_cancer,
                                      "floor_frac": floor_frac}

    # === Clinical severity (mirrors 83 Part B; raw omega, kn_floor=0) ===
    if cancer in STRATA:
        with np.errstate(invalid="ignore"):
            tumor_omega = np.nanmean(omega_tt, axis=1)
            tumor_kf = np.nanmean(kf_tt, axis=1)
            tumor_kn = np.nanmean(kn_tt, axis=1)

        strat_name, strat_fn, order, test_kind = STRATA[cancer]
        group_vals = {"omega": {}, "kf": {}, "kn": {}}
        for i_pos, sid in enumerate(tumor_sids):
            part = sample_to_participant[sid]
            g = strat_fn(sid, part)
            if g is None or g == "EGFR+KRAS":
                continue
            if np.isnan(tumor_omega[i_pos]) or np.isnan(tumor_kf[i_pos]) or np.isnan(tumor_kn[i_pos]):
                continue
            for m, arr in (("omega", tumor_omega), ("kf", tumor_kf), ("kn", tumor_kn)):
                group_vals[m].setdefault(g, []).append(float(arr[i_pos]))

        order = [g for g in order if g in group_vals["omega"]]
        print(f"  {strat_name} strata (per-tumor mean of TT pairs, linear mapping):")
        print(f"    {'group':<16} {'n':>4} {'omega':>10} {'k_f':>10} {'k_n':>12}")
        severity_tests[cancer] = {"stratification": strat_name, "groups": {}}
        for g in order:
            n_g = len(group_vals["omega"][g])
            mo = np.mean(group_vals["omega"][g]); so = np.std(group_vals["omega"][g])
            mk = np.mean(group_vals["kf"][g]);    sk = np.std(group_vals["kf"][g])
            mn = np.mean(group_vals["kn"][g]);    sn = np.std(group_vals["kn"][g])
            print(f"    {g:<16} {n_g:>4} {mo:>10.2f} {mk:>10.4f} {mn:>12.6e}")
            severity_rows.append({
                "cancer": cancer.replace("TCGA-", ""), "stratification": strat_name,
                "group": g, "n": n_g,
                "omega_mean": round(mo, 4), "omega_std": round(so, 4),
                "kf_mean": round(mk, 6), "kf_std": round(sk, 6),
                "kn_mean": round(mn, 8), "kn_std": round(sn, 8),
            })
            severity_tests[cancer]["groups"][g] = {
                "n": n_g, "omega_mean": float(mo), "kf_mean": float(mk),
                "kn_mean": float(mn)}
        tests = {}
        for m in ("omega", "kf", "kn"):
            groups = [np.array(group_vals[m][g]) for g in order]
            if test_kind == "jt":
                stat, p = jttest_on_ranks_manual(groups)
                tests[m] = {"test": "Jonckheere-Terpstra", "stat": float(stat), "p": float(p)}
            else:
                stat, p = kruskal(*groups)
                tests[m] = {"test": "Kruskal-Wallis", "stat": float(stat), "p": float(p)}
            print(f"    {m:>5}: {tests[m]['test']} stat={tests[m]['stat']:.2f}, P={tests[m]['p']:.3e}")
        severity_tests[cancer]["tests"] = tests

# ====================================================================
# 4. Save combined outputs
# ====================================================================
print("\n" + "=" * 60)
print("4. Saving outputs...")
print("=" * 60)

df_all = pd.concat(all_pair_details, ignore_index=True)
print(f"  Total pairs: {len(df_all)}")
df_all.to_csv(RESULTS_DIR / "tcga_linear_norm_v44_all_pairs.csv", index=False)

df_summary = pd.DataFrame(all_summary)
print("\n" + df_summary.to_string(index=False))
df_summary.to_csv(RESULTS_DIR / "tcga_linear_norm_v44_summary.csv", index=False)

sev_df = pd.DataFrame(severity_rows)
sev_df.to_csv(RESULTS_DIR / "tcga_clinical_severity_v44.csv", index=False)

run_meta["total_time_s"] = time.time() - t0_total
with open(RESULTS_DIR / "tcga_clinical_severity_v44.json", "w") as f:
    json.dump({"severity": severity_tests, "meta": run_meta}, f, indent=2)

print(f"\nSaved: tcga_linear_norm_v44_summary.csv")
print(f"Saved: tcga_linear_norm_v44_all_pairs.csv ({len(df_all)} pairs)")
print(f"Saved: tcga_clinical_severity_v44.csv / .json")
print(f"\nTotal time: {run_meta['total_time_s']:.0f}s")
print("DONE")
