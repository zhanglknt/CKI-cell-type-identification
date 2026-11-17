# -*- coding: utf-8 -*-
"""
nc80_paired_tn.py — paired within-patient TCGA T-vs-N analysis (nc80 panel M-I).

Panel question (methods reviewer M-I): the published TN rows rest on a
2,000-pair random subsample in which same-patient (within-individual)
tumour-vs-normal pairs are nearly absent (2-5 per cancer). The strongest
available control for the denominator (k_n) reading of the TT/NN reversal
is the FULL set of within-patient TN pairs: tumour and normal from the same
individual share germline background, sequencing facility and (often)
batch, so if k_n truly measures non-specific background divergence,
within-patient TN k_n should sit at or below the normal-cluster (NN) level
and far below the tumour-cloud (TT) level.

Design:
- Line-for-line mirror of the authoritative TCGA v44 pipeline
  (notebooks/85_tcga_linear_norm_v44.py): per-cancer streaming load,
  expression>0 gene presence pass, mean TPM >= 0.5 filter, per-cancer HK
  mapping, N_TOP_KF=200 per-pair |delta| identity genes ranked on
  log2(TPM+1), linear probability mapping p=(TPM+1)/sum(TPM+1),
  kn_floor=1e-4. RANDOM_SEED=42.
- Cohort per cancer: patients (TCGA participant barcode) with >=1 tumour
  (01) and >=1 normal (11) sample in the usable matrix.
- Pair types, all within the paired cohort:
    TN_same  : (tumour, normal) within the same patient — FULL enumeration
               (no subsampling; this is the fix for the MAX_PAIRS_TN=2000
               sampling artefact).
    TN_cross : (tumour_i, normal_j), i != j — random subsample capped at
               2,000 per cancer (seed 42), disclosed as sampled.
    TT       : cross-patient tumour-tumour pairs — FULL enumeration.
    NN       : cross-patient normal-normal pairs — FULL enumeration.
- Statistics: median k_n per pair type; ratios TN_same/TT, TN_same/NN,
  TN_same/TN_cross; Mann-Whitney U (two-sided) TN_same vs each type on k_n;
  patient-level cluster bootstrap (B=1000, seed 42, patients resampled with
  replacement, percentile CI) for the median-ratio statistics; the same
  for omega_raw descriptively. Pooled = all five cancers combined
  (bootstrap resamples patients within each cancer, then pools).

Outputs (all NEW files; nothing under results/ is overwritten):
  results/nc80_paired_tn.csv            all computed pairs, labelled
  results/nc80_paired_tn.json           per-cancer + pooled summary, CIs, tests
  results/nc80_paired_tn_summary.txt    human-readable summary
"""
import sys, os, json, time, gzip, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, norm

warnings.filterwarnings("ignore")

# === Config (verbatim from v44) ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_TUMOR = 30
MIN_NORMAL = 10
MAX_PAIRS_CROSS_TN = 2000   # subsample cap for TN_cross only (disclosed)
KN_FLOOR = 1e-4
N_BOOT = 1000

TARGET = [
    "TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"
]

t0_total = time.time()

# ====================================================================
# Linear-normalization replacements for cki.core (verbatim from v44)
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


# ====================================================================
# 0. HK gene mapping (verbatim from v44)
# ====================================================================
print("=" * 60)
print("0. Loading HK gene mapping...")
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

# ====================================================================
# 1. Parse sample metadata (verbatim from v44)
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
    header_line = fh.readline().strip().split("\t")

proj_tumor = {}
proj_normal = {}
for sid in header_line[1:]:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj is None or proj not in TARGET:
        continue
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
# 2. Per-cancer loading (verbatim from v44)
# ====================================================================

def load_cancer_data(cancer, tumor_ids, normal_ids):
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

    return expr_log, expr_lin, hk_arr, genes, sample_list


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    """Select top-N non-HK genes by absolute expression difference (verbatim v2/v44)."""
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


# ====================================================================
# 3. Bootstrap helpers (patient-level cluster bootstrap)
# ====================================================================

def boot_ratio_ci(pairs_by_type, patient_lists, n_boot=N_BOOT, seed=RANDOM_SEED):
    """Percentile CI for median-kn ratios, resampling PATIENTS with replacement.

    pairs_by_type: {ptype: list of (kn, kf, omega_raw, pa, pb)} where pa/pb
                   are patient ids (equal for TN_same).
    Fully vectorized: patient ids are mapped to integer roster positions
    once, and each bootstrap iteration keeps pairs whose two endpoint
    patients were both drawn.
    """
    rng = np.random.default_rng(seed)
    ratios = {"TN_same_over_TT": [], "TN_same_over_NN": [], "TN_same_over_TN_cross": []}
    omegas = {"TN_same_over_TT": [], "TN_same_over_NN": [], "TN_same_over_TN_cross": []}

    all_patients = sorted(set().union(*[set(v) for v in patient_lists.values()])) if patient_lists else []
    n_p = len(all_patients)
    p_pos = {p: k for k, p in enumerate(all_patients)}

    kn_arr, om_arr, pa_i, pb_i = {}, {}, {}, {}
    for pt, pl in pairs_by_type.items():
        if pl:
            kn_arr[pt] = np.array([x[0] for x in pl], dtype=float)
            om_arr[pt] = np.array([x[2] for x in pl], dtype=float)
            pa_i[pt] = np.array([p_pos[x[3]] for x in pl], dtype=int)
            pb_i[pt] = np.array([p_pos[x[4]] for x in pl], dtype=int)
        else:
            kn_arr[pt] = np.array([])
            om_arr[pt] = np.array([])
            pa_i[pt] = np.array([], dtype=int)
            pb_i[pt] = np.array([], dtype=int)

    for _ in range(n_boot):
        draw = rng.integers(0, n_p, size=n_p)
        counts = np.bincount(draw, minlength=n_p)
        med_kn, med_om = {}, {}
        for pt in ["TN_same", "TT", "NN", "TN_cross"]:
            if len(kn_arr[pt]) == 0:
                med_kn[pt] = np.nan
                med_om[pt] = np.nan
                continue
            keep = (counts[pa_i[pt]] > 0) & (counts[pb_i[pt]] > 0)
            if keep.sum() < 3:
                med_kn[pt] = np.nan
                med_om[pt] = np.nan
                continue
            med_kn[pt] = np.median(kn_arr[pt][keep])
            med_om[pt] = np.median(om_arr[pt][keep])
        for num, den in [("TN_same", "TT"), ("TN_same", "NN"), ("TN_same", "TN_cross")]:
            key = f"{num}_over_{den}"
            if np.isfinite(med_kn[num]) and np.isfinite(med_kn[den]) and med_kn[den] > 0:
                ratios[key].append(med_kn[num] / med_kn[den])
            else:
                ratios[key].append(np.nan)
            if np.isfinite(med_om[num]) and np.isfinite(med_om[den]) and med_om[den] > 0:
                omegas[key].append(med_om[num] / med_om[den])
            else:
                omegas[key].append(np.nan)

    def pct_ci(arr):
        a = np.array([x for x in arr if np.isfinite(x)])
        if len(a) == 0:
            return [None, None, 0]
        return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), int(len(a))]

    return {k: pct_ci(v) for k, v in ratios.items()}, {k: pct_ci(v) for k, v in omegas.items()}


# ====================================================================
# 4. Per-cancer computation
# ====================================================================
print("\n" + "=" * 60)
print("2. Per-cancer paired-TN analysis (linear normalization, v44 mirror)...")
print("=" * 60)

all_rows = []
summary = {"per_cancer": {}, "config": {
    "seed": RANDOM_SEED, "n_top_kf": N_TOP_KF, "kn_floor": KN_FLOOR,
    "probability_mapping": "linear (TPM+1)/sum(TPM+1)",
    "identity_gene_ranking_scale": "log2(TPM+1) (v44 convention)",
    "max_pairs_TN_cross": MAX_PAIRS_CROSS_TN, "n_boot": N_BOOT,
    "tn_same": "full enumeration (no subsampling)"}}

for cancer in usable:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")
    print("  Loading data...")
    expr_log, expr_lin, hk_arr, genes, sample_list = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal[cancer])
    sid_to_idx = {s: i for i, s in enumerate(sample_list)}
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, samples: {len(sample_list)}")

    # --- build patient map: participant -> tumour samples / normal samples
    pat_tumor = {}
    pat_normal = {}
    for sid in sample_list:
        parts = sid.split("-")
        participant = "-".join(parts[:3])
        sc = parts[3][:2]
        if sc == "01":
            pat_tumor.setdefault(participant, []).append(sid)
        elif sc == "11":
            pat_normal.setdefault(participant, []).append(sid)
    paired_pats = sorted(set(pat_tumor) & set(pat_normal))
    n_pat = len(paired_pats)
    pat_pos = {p: k for k, p in enumerate(paired_pats)}
    n_cohort_tumors = sum(len(pat_tumor[p]) for p in paired_pats)
    n_cohort_normals = sum(len(pat_normal[p]) for p in paired_pats)
    print(f"  Paired patients: {n_pat} (cohort tumors: {n_cohort_tumors}, "
          f"cohort normals: {n_cohort_normals})")

    pairs_by_type = {"TN_same": [], "TT": [], "NN": [], "TN_cross": []}

    def emit(ptype, i, j, pa, pb):
        kn, kf, ofl, oraw = pair_metrics(i, j, expr_log, expr_lin, hk_arr)
        pairs_by_type[ptype].append((kn, kf, oraw, pa, pb))
        all_rows.append({"pair_type": ptype, "cancer": cancer,
                         "sample_a": sample_list[i], "sample_b": sample_list[j],
                         "patient_a": pa, "patient_b": pb,
                         "kn": kn, "kf": kf,
                         "omega_floor": ofl, "omega_raw": oraw})
        return kn, kf, oraw

    # --- TN_same: within-patient, FULL enumeration
    for p in paired_pats:
        for t in pat_tumor[p]:
            for n in pat_normal[p]:
                emit("TN_same", sid_to_idx[t], sid_to_idx[n], p, p)

    # --- TT: cross-patient tumour pairs, FULL enumeration
    for a in range(n_pat):
        for b in range(a + 1, n_pat):
            pa, pb = paired_pats[a], paired_pats[b]
            for t1 in pat_tumor[pa]:
                for t2 in pat_tumor[pb]:
                    emit("TT", sid_to_idx[t1], sid_to_idx[t2], pa, pb)

    # --- NN: cross-patient normal pairs, FULL enumeration
    for a in range(n_pat):
        for b in range(a + 1, n_pat):
            pa, pb = paired_pats[a], paired_pats[b]
            for n1 in pat_normal[pa]:
                for n2 in pat_normal[pb]:
                    emit("NN", sid_to_idx[n1], sid_to_idx[n2], pa, pb)

    # --- TN_cross: cross-patient tumour-vs-normal, subsample cap
    cross_list = []
    for a in range(n_pat):
        for b in range(n_pat):
            if a == b:
                continue
            pa, pb = paired_pats[a], paired_pats[b]
            for t in pat_tumor[pa]:
                for n in pat_normal[pb]:
                    cross_list.append((sid_to_idx[t], sid_to_idx[n], pa, pb))
    rng = np.random.default_rng(RANDOM_SEED)
    if len(cross_list) > MAX_PAIRS_CROSS_TN:
        sel = rng.choice(len(cross_list), MAX_PAIRS_CROSS_TN, replace=False)
        cross_list = [cross_list[k] for k in sel]
    for i, j, pa, pb in cross_list:
        emit("TN_cross", i, j, pa, pb)

    # --- stats
    kn_arr = {pt: np.array([x[0] for x in pl]) for pt, pl in pairs_by_type.items()}
    om_arr = {pt: np.array([x[2] for x in pl]) for pt, pl in pairs_by_type.items()}
    kf_arr = {pt: np.array([x[1] for x in pl]) for pt, pl in pairs_by_type.items()}

    med_kn = {pt: float(np.median(kn_arr[pt])) if len(kn_arr[pt]) else None
              for pt in kn_arr}
    med_kf = {pt: float(np.median(kf_arr[pt])) if len(kf_arr[pt]) else None
              for pt in kf_arr}
    med_om = {pt: float(np.median(om_arr[pt])) if len(om_arr[pt]) else None
              for pt in om_arr}

    def mwu(a, b):
        if len(a) < 3 or len(b) < 3:
            return None
        u, p = mannwhitneyu(a, b, alternative="two-sided")
        return {"U": float(u), "p": float(p)}

    tests = {
        "TN_same_vs_TT_kn": mwu(kn_arr["TN_same"], kn_arr["TT"]),
        "TN_same_vs_NN_kn": mwu(kn_arr["TN_same"], kn_arr["NN"]),
        "TN_same_vs_TN_cross_kn": mwu(kn_arr["TN_same"], kn_arr["TN_cross"]),
    }

    patient_lists = {pt: sorted({x[3] for x in pl} | {x[4] for x in pl})
                     for pt, pl in pairs_by_type.items()}
    kn_cis, om_cis = boot_ratio_ci(pairs_by_type, patient_lists)

    ratios_point = {}
    for num, den in [("TN_same", "TT"), ("TN_same", "NN"), ("TN_same", "TN_cross")]:
        if med_kn[num] is not None and med_kn[den] not in (None, 0):
            ratios_point[f"{num}_over_{den}"] = med_kn[num] / med_kn[den]

    summary["per_cancer"][cancer] = {
        "n_paired_patients": n_pat,
        "n_cohort_tumors": n_cohort_tumors,
        "n_cohort_normals": n_cohort_normals,
        "n_pairs": {pt: len(pl) for pt, pl in pairs_by_type.items()},
        "median_kn": med_kn, "median_kf": med_kf, "median_omega_raw": med_om,
        "iqr_kn": {pt: [float(np.percentile(kn_arr[pt], 25)),
                        float(np.percentile(kn_arr[pt], 75))]
                   if len(kn_arr[pt]) else None for pt in kn_arr},
        "ratio_medians_kn": ratios_point,
        "bootstrap_ci_ratio_kn": kn_cis,
        "bootstrap_ci_ratio_omega": om_cis,
        "mwu_tests_kn": tests,
        "n_genes": len(genes), "n_hk": int(len(hk_arr)),
    }
    print(f"  med k_n  TN_same={med_kn['TN_same']:.3e}  TT={med_kn['TT']:.3e}  "
          f"NN={med_kn['NN']:.3e}  TN_cross={med_kn['TN_cross']:.3e}")
    print(f"  ratio TN/TT={ratios_point.get('TN_same_over_TT'):.3f}  "
          f"TN/NN={ratios_point.get('TN_same_over_NN'):.3f}  "
          f"TN/TN_cross={ratios_point.get('TN_same_over_TN_cross'):.3f}")
    print(f"  ({time.time() - t0_cancer:.0f}s)")

# ====================================================================
# 5. Pooled analysis (all cancers; bootstrap resamples within cancer)
# ====================================================================
print("\n" + "=" * 60)
print("3. Pooled analysis...")
print("=" * 60)

df = pd.DataFrame(all_rows)
pooled = {}
for pt in ["TN_same", "TT", "NN", "TN_cross"]:
    sub = df[df["pair_type"] == pt]
    pooled[pt] = {
        "n": int(len(sub)),
        "median_kn": float(sub["kn"].median()),
        "median_kf": float(sub["kf"].median()),
        "median_omega_raw": float(sub["omega_raw"].median()),
    }
pooled_ratios = {
    f"TN_same_over_{den}": pooled["TN_same"]["median_kn"] / pooled[den]["median_kn"]
    for den in ["TT", "NN", "TN_cross"]
}

# pooled patient-level bootstrap: resample patients within each cancer
# (patient ids are strings and roster differs per cancer, so a dedicated
#  implementation is used instead of the per-cancer helper)
cancers_list = sorted(summary["per_cancer"].keys())
kn_tables = {}
om_tables = {}
pa_tables = {}
pb_tables = {}
for pt in ["TN_same", "TT", "NN", "TN_cross"]:
    sub = df[df["pair_type"] == pt]
    kn_tables[pt] = sub["kn"].to_numpy(dtype=float)
    om_tables[pt] = sub["omega_raw"].to_numpy(dtype=float)
    pa_tables[pt] = sub["patient_a"].to_numpy()
    pb_tables[pt] = sub["patient_b"].to_numpy()

ratios_boot = {f"TN_same_over_{d}": [] for d in ["TT", "NN", "TN_cross"]}
om_boot = {f"TN_same_over_{d}": [] for d in ["TT", "NN", "TN_cross"]}

# Rebuild patient rosters per cancer from the pair table
# (patient ids are unique per cancer)
pats_by_cancer = {c: {} for c in cancers_list}
for pt in ["TN_same", "TT", "NN", "TN_cross"]:
    sub = df[df["pair_type"] == pt]
    for _, r in sub.iterrows():
        pats_by_cancer[r["cancer"]][r["patient_a"]] = True
        pats_by_cancer[r["cancer"]][r["patient_b"]] = True

roster = {c: sorted(pats_by_cancer[c].keys()) for c in cancers_list}
roster_pos = {c: {p: k for k, p in enumerate(roster[c])} for c in cancers_list}
cancer_of_pair = {pt: df[df["pair_type"] == pt]["cancer"].to_numpy()
                  for pt in ["TN_same", "TT", "NN", "TN_cross"]}
# Pre-map patient ids to per-cancer integer roster indices (vectorized keep)
pa_int = {}
pb_int = {}
for pt in ["TN_same", "TT", "NN", "TN_cross"]:
    pa_int[pt] = {}
    pb_int[pt] = {}
    for c in cancers_list:
        mask = cancer_of_pair[pt] == c
        if mask.sum() == 0:
            continue
        pa_int[pt][c] = np.array([roster_pos[c][p] for p in pa_tables[pt][mask]], dtype=int)
        pb_int[pt][c] = np.array([roster_pos[c][p] for p in pb_tables[pt][mask]], dtype=int)

rng = np.random.default_rng(RANDOM_SEED)
for it in range(N_BOOT):
    counts_c = {}
    for c in cancers_list:
        n_pc = len(roster[c])
        draw = rng.integers(0, n_pc, size=n_pc)
        counts_c[c] = np.bincount(draw, minlength=n_pc)
    med_kn_b, med_om_b = {}, {}
    for pt in ["TN_same", "TT", "NN", "TN_cross"]:
        kn_parts, om_parts = [], []
        for c in cancers_list:
            mask = cancer_of_pair[pt] == c
            if mask.sum() == 0:
                continue
            kn_c = kn_tables[pt][mask]
            om_c = om_tables[pt][mask]
            cnt = counts_c[c]
            keep = (cnt[pa_int[pt][c]] > 0) & (cnt[pb_int[pt][c]] > 0)
            if keep.sum() >= 3:
                kn_parts.append(kn_c[keep])
                om_parts.append(om_c[keep])
        if kn_parts:
            allk = np.concatenate(kn_parts)
            allo = np.concatenate(om_parts)
            med_kn_b[pt] = float(np.median(allk))
            med_om_b[pt] = float(np.median(allo))
        else:
            med_kn_b[pt] = np.nan
            med_om_b[pt] = np.nan
    for d in ["TT", "NN", "TN_cross"]:
        key = f"TN_same_over_{d}"
        if np.isfinite(med_kn_b["TN_same"]) and np.isfinite(med_kn_b[d]) and med_kn_b[d] > 0:
            ratios_boot[key].append(med_kn_b["TN_same"] / med_kn_b[d])
        else:
            ratios_boot[key].append(np.nan)
        if np.isfinite(med_om_b["TN_same"]) and np.isfinite(med_om_b[d]) and med_om_b[d] > 0:
            om_boot[key].append(med_om_b["TN_same"] / med_om_b[d])
        else:
            om_boot[key].append(np.nan)


def pct_ci(arr):
    a = np.array([x for x in arr if np.isfinite(x)])
    if len(a) == 0:
        return [None, None, 0]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), int(len(a))]


summary["pooled"] = {
    "by_pair_type": pooled,
    "ratio_medians_kn": pooled_ratios,
    "bootstrap_ci_ratio_kn": {k: pct_ci(v) for k, v in ratios_boot.items()},
    "bootstrap_ci_ratio_omega": {k: pct_ci(v) for k, v in om_boot.items()},
}

# ====================================================================
# 6. Write outputs
# ====================================================================
df.to_csv(RESULTS_DIR / "nc80_paired_tn.csv", index=False)
with open(RESULTS_DIR / "nc80_paired_tn.json", "w") as f:
    json.dump(summary, f, indent=2, default=float)

lines = []
lines.append("nc80 paired within-patient TN analysis (v44 linear-mapping mirror)")
lines.append("=" * 70)
lines.append(f"Cohort: patients with >=1 tumour (01) and >=1 normal (11) sample")
lines.append(f"TN_same: FULL enumeration; TN_cross: subsample cap {MAX_PAIRS_CROSS_TN}; "
             f"TT/NN: cross-patient, full enumeration within cohort")
lines.append(f"Bootstrap: patient-level cluster, B={N_BOOT}, seed={RANDOM_SEED}")
lines.append("")
for c in cancers_list:
    s = summary["per_cancer"][c]
    lines.append(f"[{c}] patients={s['n_paired_patients']}  "
                 f"pairs={s['n_pairs']}")
    lines.append(f"  median k_n:  TN_same={s['median_kn']['TN_same']:.3e}  "
                 f"TT={s['median_kn']['TT']:.3e}  NN={s['median_kn']['NN']:.3e}  "
                 f"TN_cross={s['median_kn']['TN_cross']:.3e}")
    lines.append(f"  median k_f:  TN_same={s['median_kf']['TN_same']:.3e}  "
                 f"TT={s['median_kf']['TT']:.3e}  NN={s['median_kf']['NN']:.3e}  "
                 f"TN_cross={s['median_kf']['TN_cross']:.3e}")
    lines.append(f"  median omega_raw:  TN_same={s['median_omega_raw']['TN_same']:.2f}  "
                 f"TT={s['median_omega_raw']['TT']:.2f}  NN={s['median_omega_raw']['NN']:.2f}  "
                 f"TN_cross={s['median_omega_raw']['TN_cross']:.2f}")
    for key in ["TN_same_over_TT", "TN_same_over_NN", "TN_same_over_TN_cross"]:
        ci = s["bootstrap_ci_ratio_kn"][key]
        lines.append(f"  k_n ratio {key.replace('_over_', '/')} = "
                     f"{s['ratio_medians_kn'].get(key, float('nan')):.3f}  "
                     f"boot 95% CI [{ci[0]:.3f}, {ci[1]:.3f}] (n={ci[2]})")
    for tname, t in s["mwu_tests_kn"].items():
        if t:
            lines.append(f"  MWU {tname}: U={t['U']:.0f}  p={t['p']:.2e}")
    lines.append("")
p = summary["pooled"]
lines.append("[POOLED all five cancers]")
lines.append(f"  median k_n:  TN_same={p['by_pair_type']['TN_same']['median_kn']:.3e}  "
             f"TT={p['by_pair_type']['TT']['median_kn']:.3e}  "
             f"NN={p['by_pair_type']['NN']['median_kn']:.3e}  "
             f"TN_cross={p['by_pair_type']['TN_cross']['median_kn']:.3e}")
for key in ["TN_same_over_TT", "TN_same_over_NN", "TN_same_over_TN_cross"]:
    ci = p["bootstrap_ci_ratio_kn"][key]
    lines.append(f"  k_n ratio {key.replace('_over_', '/')} = "
                 f"{p['ratio_medians_kn'][key]:.3f}  "
                 f"boot 95% CI [{ci[0]:.3f}, {ci[1]:.3f}] (n={ci[2]})")
lines.append("")
lines.append(f"Total time: {time.time() - t0_total:.0f}s")

with open(RESULTS_DIR / "nc80_paired_tn_summary.txt", "w") as f:
    f.write("\n".join(lines))

print("\n".join(lines))
print(f"\nDone. Outputs written to results/nc80_paired_tn.*")
