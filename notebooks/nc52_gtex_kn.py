# -*- coding: utf-8 -*-
"""
nc52: GTEx healthy-tissue reference for the TCGA k_n mechanism claim (R3 Major B2)
=================================================================================

Question: is the elevated k_n (housekeeping-divergence denominator) in tumors
a tumor-specific housekeeping dysregulation, or a field effect already present
in adjacent-normal tissue? The missing reference is HEALTHY tissue from GTEx.

Data:
  TCGA  : data/tcga/tcga_RSEM_gene_tpm.gz   (UCSC Xena Toil RSEM TPM, GENCODE v23)
  GTEx  : data/gtex/gtex_RSEM_gene_tpm.gz   (UCSC Xena Toil RSEM TPM, GENCODE v23
          -> identical quantification pipeline and identical 60,498-gene row set
          as the TCGA matrix; verified row-for-row identical on 2026-09-24)
  GTEx phenotype: data/gtex/GTEX_phenotype.gz (body_site_detail SMTSD)

Method (LINE-FOR-LINE reuse of notebooks/85_tcga_linear_norm_v44.py, which is
itself a mirror of 06_phase34_v2.py):
  - per-cancer gene filtering: expression > 0 in any loaded sample, then
    mean TPM >= 0.5 across the loaded samples (v44 two-pass equivalent);
    the loaded set per cancer is TCGA tumors + TCGA adjacent normals +
    the organ-matched GTEx tissue samples (<=300, seeded subsample)
  - HK panel: HRT Atlas human symbols (data/housekeeping/Human_Mouse_Common.csv)
    mapped through data/tcga/probemap.tsv (Ensembl, version stripped)
  - probability mapping: p_i = (TPM+1) / sum(TPM+1)   (linear, v44)
  - k_n = Jensen-Shannon divergence (base 2) on HK-restricted linear probs
  - k_f = JSD on per-pair top-200 non-HK identity genes ranked on log2(TPM+1)
  - omega_floor with kn_floor = 1e-4
  - RANDOM_SEED = 42, MAX_PAIRS = 2000 (same subsampling protocol as v44)

FOUR pair types are computed per cancer on the SAME gene set:
  TT = tumor-tumor          (identical 2000-pair seeded subsample as v44,
                             because the TCGA sample ordering and seeding are
                             reproduced verbatim)
  NN = adjacent-adjacent    (complete, as v44)
  GG = GTEx-GTEx            (complete or 2000-pair seeded subsample)
  GA = GTEx-adjacent        (complete or 2000-pair seeded subsample)
TT/NN k_n values are cross-checked against
results/tcga_linear_norm_v44_all_pairs.csv (published v44 numbers; only the
gene filter differs, by the added GTEx samples).

Organ mapping: Lung=LUAD+LUSC, Liver=LIHC, Kidney=KIRC (GTEx Kidney-Cortex),
Breast=BRCA (GTEx Breast-Mammary Tissue).

Outputs:
  results/nc52_gtex_pairs.csv             all computed pairs (sample-labelled)
  results/nc52_gtex_kn_by_grouptype.csv   organ x pair_type summary stats
                                          (+ per-cancer detail rows)
  results/nc52_gtex_summary.json          metadata + tests + ordering verdict
  results/audit/_nc52_gtex_run.log        run log
"""
import sys, os, json, time, gzip, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, norm

warnings.filterwarnings("ignore")

# === Config (verbatim from 85_tcga_linear_norm_v44.py) ===
RANDOM_SEED = 42
N_TOP_KF = 200
MAX_PAIRS = 2000          # v44 MAX_PAIRS_TT / MAX_PAIRS_TN
KN_FLOOR = 1e-4
MAX_GTEX_PER_TISSUE = 300

CANCER_ORGAN_SITE = {
    "TCGA-LUAD": ("Lung", "Lung"),
    "TCGA-LUSC": ("Lung", "Lung"),
    "TCGA-LIHC": ("Liver", "Liver"),
    "TCGA-KIRC": ("Kidney", "Kidney - Cortex"),
    "TCGA-BRCA": ("Breast", "Breast - Mammary Tissue"),
}

GTEX_FILE = DATA_DIR / "gtex" / "gtex_RSEM_gene_tpm.gz"
GTEX_PHENO = DATA_DIR / "gtex" / "GTEX_phenotype.gz"
V44_PAIRS = RESULTS_DIR / "tcga_linear_norm_v44_all_pairs.csv"

t0_total = time.time()
lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

# ====================================================================
# Verbatim functions from 85_tcga_linear_norm_v44.py
# ====================================================================

def js_divergence_linear(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    sa = a.sum()
    sb = b.sum()
    if sa <= 0 and sb <= 0:
        return 0.0
    if sa <= 0 or sb <= 0:
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
    kn = js_divergence_linear(pb_a[hk_idx], pb_b[hk_idx]) if len(hk_idx) else 0.0
    kf = js_divergence_linear(pb_a[id_idx], pb_b[id_idx]) if len(id_idx) else 0.0
    return kn, kf


def omega_from_kn_kf(kn, kf, kn_floor):
    if kn_floor > 0 and kn < kn_floor:
        omega_floor = kf / kn_floor
    elif kn <= 0.0:
        omega_floor = float("inf")
    else:
        omega_floor = kf / kn
    omega_raw = kf / kn if kn > 0 else float("inf")
    return omega_floor, omega_raw


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


def pair_metrics(i_row, j_row, expr_log, expr_lin, hk_arr):
    p1_log = expr_log[i_row, :]
    p2_log = expr_log[j_row, :]
    id_idx = select_top_diff(p1_log, p2_log, hk_arr, N_TOP_KF)
    kn, kf = kn_kf_linear(expr_lin[i_row, :], expr_lin[j_row, :], hk_arr, id_idx)
    omega_floor, omega_raw = omega_from_kn_kf(kn, kf, KN_FLOOR)
    return kn, kf, omega_floor, omega_raw


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


# ====================================================================
# 0. HK gene mapping (verbatim from v44)
# ====================================================================
log("=" * 60)
log("0. Loading HK gene mapping...")
log("=" * 60)

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
log(f"  HK gene symbols: {len(hk_human)}, probeMap: {len(ens_to_symbol)}")

# ====================================================================
# 1. Sample metadata (TCGA: verbatim TSS mapping; GTEx: phenotype)
# ====================================================================
log("\n" + "=" * 60)
log("1. Sample metadata...")
log("=" * 60)

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
    "94":"TCGA-LUSC","96":"TCGA-LUSC","98":"TCGA-LUSC","CC":"TCGA-LIHC",
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
    "MW":"TCGA-KIRC","P4":"TCGA-KIRC","Q2":"TCGA-KIRC",
    "UZ":"TCGA-KIRC","V5":"TCGA-KIRC","XM":"TCGA-KIRC","YE":"TCGA-KIRC",
}

with gzip.open(TCGA_FILE, "rt") as fh:
    tcga_header = fh.readline().strip().split("\t")

proj_tumor, proj_normal = {}, {}
for sid in tcga_header[1:]:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    proj = TSS_TO_PROJECT.get(parts[1])
    if proj is None or proj not in CANCER_ORGAN_SITE:
        continue
    sc = parts[3][:2]
    if sc == "01":
        proj_tumor.setdefault(proj, []).append(sid)
    elif sc == "11":
        proj_normal.setdefault(proj, []).append(sid)

for c in sorted(CANCER_ORGAN_SITE):
    log(f"  {c}: T={len(proj_tumor.get(c, []))}, N={len(proj_normal.get(c, []))}")

# GTEx phenotype -> tissue samples, seeded subsample <= MAX_GTEX_PER_TISSUE
ph = pd.read_csv(GTEX_PHENO, sep="\t", compression="gzip")
with gzip.open(GTEX_FILE, "rt") as fh:
    gtex_header = fh.readline().strip().split("\t")
gtex_avail = set(gtex_header[1:])

rng_sel = np.random.RandomState(RANDOM_SEED)
tissue_samples = {}
for site in ["Lung", "Liver", "Kidney - Cortex", "Breast - Mammary Tissue"]:
    ids = sorted(ph.loc[ph["body_site_detail (SMTSD)"] == site, "Sample"])
    ids = [s for s in ids if s in gtex_avail]
    if len(ids) > MAX_GTEX_PER_TISSUE:
        ids = sorted(rng_sel.choice(ids, MAX_GTEX_PER_TISSUE, replace=False))
    tissue_samples[site] = ids
    log(f"  GTEx {site}: {len(ids)} samples (cap {MAX_GTEX_PER_TISSUE}, seed {RANDOM_SEED})")

# ====================================================================
# 2. Load expression matrices (pandas fast path; values identical to
#    the v44 two-pass streaming load)
# ====================================================================
log("\n" + "=" * 60)
log("2. Loading expression matrices...")
log("=" * 60)

def load_matrix(path, wanted, label):
    t0 = time.time()
    df = pd.read_csv(path, sep="\t", compression="gzip",
                     usecols=["sample"] + list(wanted))
    df = df.set_index("sample").T
    df = df.loc[[s for s in wanted if s in df.index]]
    log(f"  {label}: {df.shape[0]} samples x {df.shape[1]} genes "
        f"({time.time()-t0:.0f}s)")
    return df.values.astype(np.float32), list(df.columns), list(df.index)

all_wanted_tcga = sorted(set(
    s for c in CANCER_ORGAN_SITE
    for s in proj_tumor.get(c, []) + proj_normal.get(c, [])))
tcga_expr, tcga_genes, tcga_samples = load_matrix(TCGA_FILE, all_wanted_tcga, "TCGA")

all_wanted_gtex = sorted(set(s for ids in tissue_samples.values() for s in ids))
gtex_expr, gtex_genes, gtex_samples = load_matrix(GTEX_FILE, all_wanted_gtex, "GTEx")

assert tcga_genes == gtex_genes, "gene lists differ between matrices"
genes = tcga_genes
log(f"  gene lists identical: {len(genes)} genes")

tcga_pos = {s: i for i, s in enumerate(tcga_samples)}
gtex_pos = {s: i for i, s in enumerate(gtex_samples)}

# ====================================================================
# 3. Per-cancer computation (TT / NN / GG / GA on one combined gene set)
# ====================================================================
log("\n" + "=" * 60)
log("3. Per-cancer analysis...")
log("=" * 60)

pair_rows = []
meta = {"seed": RANDOM_SEED, "n_top_kf": N_TOP_KF, "kn_floor": KN_FLOOR,
        "max_pairs": MAX_PAIRS, "max_gtex_per_tissue": MAX_GTEX_PER_TISSUE,
        "probability_mapping": "linear (TPM+1)/sum(TPM+1)",
        "identity_gene_ranking_scale": "log2(TPM+1) (unchanged from v2/v44)",
        "per_cancer": {}}
kn_by_cancer = {}

for cancer in ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]:
    t0 = time.time()
    organ, site = CANCER_ORGAN_SITE[cancer]
    log(f"\n--- {cancer} ({organ}; GTEx {site}) ---")

    # combined sample set: TCGA (sorted, as v44 sample_list) + GTEx appended
    tc_wanted = sorted(set(proj_tumor[cancer] + proj_normal[cancer]))
    gt_ids = tissue_samples[site]
    n_tc, n_gt = len(tc_wanted), len(gt_ids)

    comb = np.vstack([tcga_expr[[tcga_pos[s] for s in tc_wanted]],
                      gtex_expr[[gtex_pos[s] for s in gt_ids]]])
    sample_list = tc_wanted + gt_ids
    tumor_set = set(proj_tumor[cancer])
    normal_set = set(proj_normal[cancer])

    # v44 two-pass equivalent: presence > 0 in any, then mean TPM >= 0.5
    present = (comb > 0).any(axis=0)
    comb = comb[:, present]
    genes_c = [g for g, k in zip(genes, present) if k]
    keep = comb.mean(axis=0) >= 0.5
    comb = comb[:, keep]
    genes_c = [g for g, k in zip(genes_c, keep) if k]

    expr_log = np.log2(np.maximum(comb, 0) + 1)
    expr_lin = np.maximum(comb, 0).astype(np.float64) + 1.0

    gene_ens = [g.split(".")[0] for g in genes_c]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)

    t_idx = np.array([i for i, s in enumerate(sample_list) if s in tumor_set])
    n_idx = np.array([i for i, s in enumerate(sample_list) if s in normal_set])
    g_idx = np.arange(n_tc, n_tc + n_gt)
    n_t, n_n, n_g = len(t_idx), len(n_idx), len(g_idx)
    log(f"  samples: T={n_t}, N={n_n}, GTEx={n_g}; genes={len(genes_c)}, HK={len(hk_arr)}")

    def run_pairs(pair_list, pair_type):
        rows, kns = [], []
        for idx, (i, j) in enumerate(pair_list):
            kn, kf, omega_floor, omega_raw = pair_metrics(
                i, j, expr_log, expr_lin, hk_arr)
            rows.append({"pair_type": pair_type, "cancer": cancer, "organ": organ,
                         "sample_a": sample_list[i], "sample_b": sample_list[j],
                         "kn": kn, "kf": kf,
                         "omega_floor": omega_floor, "omega_raw": omega_raw})
            kns.append(kn)
            if (idx + 1) % 2000 == 0:
                log(f"    {pair_type}: {idx+1}/{len(pair_list)}")
        log(f"    {pair_type}: {len(pair_list)} done, kn median={np.median(kns):.4e}")
        return rows, np.array(kns)

    # --- TT (verbatim v44 seeding -> identical pair set to the v44 run) ---
    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    np.random.seed(RANDOM_SEED)
    if len(all_tt) > MAX_PAIRS:
        tt_pairs = [(t_idx[i], t_idx[j]) for i, j in
                    (all_tt[k] for k in np.random.choice(len(all_tt), MAX_PAIRS, replace=False))]
    else:
        tt_pairs = [(t_idx[i], t_idx[j]) for i, j in all_tt]
    rows, kn_tt = run_pairs(tt_pairs, "TT")
    pair_rows += rows

    # --- NN (complete, as v44) ---
    all_nn = [(n_idx[i], n_idx[j]) for i in range(n_n) for j in range(i + 1, n_n)]
    rows, kn_nn = run_pairs(all_nn, "NN")
    pair_rows += rows

    # --- GG (new; same protocol: seed then complete-or-2000 subsample) ---
    all_gg = [(i, j) for i in range(n_g) for j in range(i + 1, n_g)]
    np.random.seed(RANDOM_SEED)
    if len(all_gg) > MAX_PAIRS:
        gg_pairs = [(g_idx[i], g_idx[j]) for i, j in
                    (all_gg[k] for k in np.random.choice(len(all_gg), MAX_PAIRS, replace=False))]
    else:
        gg_pairs = [(g_idx[i], g_idx[j]) for i, j in all_gg]
    rows, kn_gg = run_pairs(gg_pairs, "GG")
    pair_rows += rows

    # --- GA (new; continues the rng stream, as TN did in v44) ---
    all_ga = [(i, j) for i in g_idx for j in n_idx]
    if len(all_ga) > MAX_PAIRS:
        ga_pairs = [all_ga[k] for k in np.random.choice(len(all_ga), MAX_PAIRS, replace=False)]
    else:
        ga_pairs = all_ga
    rows, kn_ga = run_pairs(ga_pairs, "GA")
    pair_rows += rows

    # --- tests ---
    p_gg_nn = mannwhitneyu(kn_gg, kn_nn, alternative="less").pvalue
    p_nn_tt = mannwhitneyu(kn_tt, kn_nn, alternative="greater").pvalue
    p_gg_tt = mannwhitneyu(kn_tt, kn_gg, alternative="greater").pvalue
    p_ga_gg = mannwhitneyu(kn_ga, kn_gg, alternative="greater").pvalue
    jt_stat, jt_p = jttest_on_ranks_manual(
        [kn_gg.tolist(), kn_nn.tolist(), kn_tt.tolist()])

    meds = {"GG": float(np.median(kn_gg)), "GA": float(np.median(kn_ga)),
            "NN": float(np.median(kn_nn)), "TT": float(np.median(kn_tt))}
    r_gg_nn = meds["GG"] / meds["NN"]
    r_tt_nn = meds["TT"] / meds["NN"]
    r_tt_gg = meds["TT"] / meds["GG"]
    # three-way data-driven verdict
    if 0.8 <= r_gg_nn <= 1.25 and r_tt_nn >= 1.5:
        verdict = ("GTEx~adjacent<tumor: healthy and adjacent baselines coincide, "
                   "tumor elevated -> supports tumor-specific HK dysregulation "
                   "(NOT a field effect)")
    elif r_gg_nn < 0.8 and r_tt_nn > 1.25:
        verdict = ("GTEx<adjacent<tumor: graded elevation from healthy through "
                   "adjacent to tumor -> field-effect gradient")
    elif r_tt_gg <= 1.25:
        verdict = ("GTEx~tumor: healthy GTEx k_n already at tumor level -> "
                   "does NOT support tumor specificity (check tissue-specific "
                   "technical confounds)")
    else:
        verdict = "mixed/intermediate pattern"
    log(f"  k_n medians: GG={meds['GG']:.4e} GA={meds['GA']:.4e} "
        f"NN={meds['NN']:.4e} TT={meds['TT']:.4e}")
    log(f"  ratios: GG/NN={r_gg_nn:.2f}, TT/NN={r_tt_nn:.2f}, TT/GG={r_tt_gg:.2f}")
    log(f"  MWU: GG<NN P={p_gg_nn:.2e}; TT>NN P={p_nn_tt:.2e}; "
        f"TT>GG P={p_gg_tt:.2e}; GA>GG P={p_ga_gg:.2e}")
    log(f"  JT trend GG<NN<TT: stat={jt_stat:.0f}, P={jt_p:.2e}")
    log(f"  verdict: {verdict}")

    kn_by_cancer[cancer] = {"TT": kn_tt, "NN": kn_nn, "GG": kn_gg, "GA": kn_ga}
    meta["per_cancer"][cancer] = {
        "organ": organ, "gtex_site": site,
        "n_tumor": int(n_t), "n_adjacent": int(n_n), "n_gtex": int(n_g),
        "n_genes": len(genes_c), "n_hk": len(hk_arr),
        "kn_median": meds,
        "ratio_GG_NN": float(r_gg_nn),
        "ratio_TT_NN": float(r_tt_nn),
        "ratio_TT_GG": float(r_tt_gg),
        "p_MWU_GG_lt_NN": float(p_gg_nn),
        "p_MWU_TT_gt_NN": float(p_nn_tt),
        "p_MWU_TT_gt_GG": float(p_gg_tt),
        "p_MWU_GA_gt_GG": float(p_ga_gg),
        "JT_trend_GG_NN_TT": {"stat": float(jt_stat), "p": float(jt_p)},
        "ordering_verdict": verdict,
        "time_s": time.time() - t0,
    }

# ====================================================================
# 4. Summary table (organ-level pooled + per-cancer detail)
# ====================================================================
log("\n" + "=" * 60)
log("4. Summary table...")
log("=" * 60)

def sum_row(scope, name, pt, arr):
    q25, q75 = np.percentile(arr, [25, 75])
    return {"level": scope, "group": name, "pair_type": pt,
            "n_pairs": len(arr),
            "kn_median": f"{np.median(arr):.6e}",
            "kn_mean": f"{arr.mean():.6e}",
            "kn_q25": f"{q25:.6e}", "kn_q75": f"{q75:.6e}",
            "kn_iqr": f"{q75 - q25:.6e}",
            "floor_frac_kn_lt_1e-4": f"{np.mean(arr < KN_FLOOR):.4f}"}

summary_rows = []
ORGAN_CANCERS = {"Lung": ["TCGA-LUAD", "TCGA-LUSC"], "Liver": ["TCGA-LIHC"],
                 "Kidney": ["TCGA-KIRC"], "Breast": ["TCGA-BRCA"]}
organ_kn = {}
for organ in ["Lung", "Liver", "Kidney", "Breast"]:
    organ_kn[organ] = {}
    for pt in ("GG", "GA", "NN", "TT"):
        arr = np.concatenate([kn_by_cancer[c][pt] for c in ORGAN_CANCERS[organ]])
        organ_kn[organ][pt] = arr
        summary_rows.append(sum_row("organ", organ, pt, arr))
for cancer in CANCER_ORGAN_SITE:
    for pt in ("GG", "GA", "NN", "TT"):
        summary_rows.append(sum_row("cancer", cancer, pt, kn_by_cancer[cancer][pt]))

# organ-level tests
for organ in ["Lung", "Liver", "Kidney", "Breast"]:
    k = organ_kn[organ]
    p_gg_nn = mannwhitneyu(k["GG"], k["NN"], alternative="less").pvalue
    p_nn_tt = mannwhitneyu(k["TT"], k["NN"], alternative="greater").pvalue
    p_gg_tt = mannwhitneyu(k["TT"], k["GG"], alternative="greater").pvalue
    p_ga_gg = mannwhitneyu(k["GA"], k["GG"], alternative="greater").pvalue
    jt_stat, jt_p = jttest_on_ranks_manual(
        [k["GG"].tolist(), k["NN"].tolist(), k["TT"].tolist()])
    meds = {pt: float(np.median(k[pt])) for pt in ("GG", "GA", "NN", "TT")}
    r_gg_nn = meds["GG"] / meds["NN"]
    r_tt_nn = meds["TT"] / meds["NN"]
    r_tt_gg = meds["TT"] / meds["GG"]
    if 0.8 <= r_gg_nn <= 1.25 and r_tt_nn >= 1.5:
        verdict = ("GTEx~adjacent<tumor: supports tumor-specific HK dysregulation "
                   "(NOT a field effect)")
    elif r_gg_nn < 0.8 and r_tt_nn > 1.25:
        verdict = "GTEx<adjacent<tumor: field-effect gradient"
    elif r_tt_gg <= 1.25:
        verdict = ("GTEx~tumor: does NOT support tumor specificity "
                   "(check tissue-specific technical confounds)")
    else:
        verdict = "mixed/intermediate pattern"
    log(f"  {organ}: GG={meds['GG']:.4e} GA={meds['GA']:.4e} NN={meds['NN']:.4e} "
        f"TT={meds['TT']:.4e} | GG/NN={r_gg_nn:.2f} TT/NN={r_tt_nn:.2f} "
        f"TT/GG={r_tt_gg:.2f} | GG<NN P={p_gg_nn:.2e}, TT>NN P={p_nn_tt:.2e}, "
        f"GA>GG P={p_ga_gg:.2e}, JT P={jt_p:.2e}")
    log(f"    verdict: {verdict}")
    meta["per_organ"] = meta.get("per_organ", {})
    meta["per_organ"][organ] = {
        "kn_median": meds,
        "kn_iqr": {pt: [float(x) for x in np.percentile(k[pt], [25, 75])]
                   for pt in ("GG", "GA", "NN", "TT")},
        "n_pairs": {pt: int(len(k[pt])) for pt in ("GG", "GA", "NN", "TT")},
        "ratio_GG_NN": float(r_gg_nn),
        "ratio_TT_NN": float(r_tt_nn),
        "ratio_TT_GG": float(r_tt_gg),
        "p_MWU_GG_lt_NN": float(p_gg_nn),
        "p_MWU_TT_gt_NN": float(p_nn_tt),
        "p_MWU_TT_gt_GG": float(p_gg_tt),
        "p_MWU_GA_gt_GG": float(p_ga_gg),
        "JT_trend_GG_NN_TT": {"stat": float(jt_stat), "p": float(jt_p)},
        "ordering_verdict": verdict,
    }

# ====================================================================
# 5. Cross-check TT/NN against published v44 pair table
# ====================================================================
log("\n" + "=" * 60)
log("5. Cross-check vs published v44 (TCGA-only gene filter)...")
log("=" * 60)
v44 = pd.read_csv(V44_PAIRS)
new_pairs = pd.DataFrame(pair_rows)
xcheck = {}
for cancer in CANCER_ORGAN_SITE:
    xcheck[cancer] = {}
    for pt in ("TT", "NN"):
        old = v44[(v44.cancer == cancer) & (v44.pair_type == pt)].kn
        new = new_pairs[(new_pairs.cancer == cancer) & (new_pairs.pair_type == pt)].kn
        same_pairs = len(old) == len(new)
        xcheck[cancer][pt] = {
            "n_v44": int(len(old)), "n_nc52": int(len(new)),
            "same_n_pairs": bool(same_pairs),
            "v44_median": float(old.median()), "nc52_median": float(new.median()),
            "median_ratio": float(new.median() / old.median())}
        log(f"  {cancer} {pt}: n={len(old)}/{len(new)} "
            f"v44 median={old.median():.4e}, nc52 median={new.median():.4e} "
            f"(ratio {new.median()/old.median():.3f})")
meta["crosscheck_vs_v44"] = xcheck

# ====================================================================
# 6. Save outputs
# ====================================================================
log("\n" + "=" * 60)
log("6. Saving outputs...")
log("=" * 60)

new_pairs.to_csv(RESULTS_DIR / "nc52_gtex_pairs.csv", index=False)
log(f"  nc52_gtex_pairs.csv: {len(new_pairs)} pairs")

df_sum = pd.DataFrame(summary_rows)
df_sum.to_csv(RESULTS_DIR / "nc52_gtex_kn_by_grouptype.csv", index=False)
log(f"  nc52_gtex_kn_by_grouptype.csv: {len(df_sum)} rows")
log("\n" + df_sum[df_sum.level == "organ"].to_string(index=False))

meta["total_time_s"] = time.time() - t0_total
with open(RESULTS_DIR / "nc52_gtex_summary.json", "w") as f:
    json.dump(meta, f, indent=2)

(RESULTS_DIR / "audit").mkdir(exist_ok=True)
with open(RESULTS_DIR / "audit" / "_nc52_gtex_run.log", "w") as f:
    f.write("\n".join(lines))

log(f"\nTotal time: {meta['total_time_s']:.0f}s")
log("DONE")
