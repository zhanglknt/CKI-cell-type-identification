"""
Notebook 83: k_f-only ordering control (review P1-3)
=====================================================

Question
--------
The manuscript claims (i) a cross-organ conservation RANKING of cell types
(Table 2 / Fig 5, Tabula Sapiens) and (ii) clinical-severity GRADIENTS of
intratumoral omega within TCGA cancer types (Edmondson grade, PAM50,
LUAD mutation strata).  Both claims rest on omega = k_f / k_n.  This note
asks: do the same orderings / gradients appear when k_f ALONE is used,
and how much of each signal is carried by the k_n denominator?

Design
------
Part A (cross-organ, Tabula Sapiens):
  - Rebuild the exact phase35 pseudobulk pipeline (largest-donor pseudobulk
    per organ|cell-type entry, common genes, log1p, HK from
    Human_Mouse_Common.csv; k_f = JS on the per-pair top-200 non-HK |delta|
    genes; k_n = JS on HK genes; omega = k_f / k_n).
  - Restrict to the 59 same-cell-type cross-organ pairs (17 cell types).
  - Per-cell-type mean omega vs mean k_f (and mean k_n): rank comparison,
    Spearman; extremes under k_f-only.
  - Sanity: per-CT mean omega must reproduce
    results/phase35_cross_organ_summary.csv.

Part B (TCGA severity):
  - Rebuild the exact 07_phase34_clinical TT computation for LIHC / BRCA /
    LUAD (per-cancer gene filtering mean >= 0.5 TPM, log2(TPM+1), TT pairs
    subsampled to 2000 with seed 42, per-pair top-200 non-HK gene k_f),
    recording omega, k_f, k_n per pair.
  - Per-tumor row means for all three metrics; stratify by Edmondson /
    PAM50 / LUAD mutation; Jonckheere (ordered) and Kruskal-Wallis tests
    for each metric.
  - Sanity: omega stratum means must reproduce
    results/phase34_clinical_severity.csv.

Outputs
-------
  results/kf_only_ordering.csv        per-CT cross-organ table (Part A)
  results/kf_only_severity.csv        per-stratum TCGA table (Part B)
  results/kf_only_ordering.json      machine-readable summary (both parts)
  results/kf_only_ordering.txt       human-readable report
"""
import sys, os, json, time, gzip, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr, kruskal, norm
from collections import Counter

warnings.filterwarnings("ignore")

OUT_CSV = RESULTS_DIR / "kf_only_ordering.csv"
OUT_SEV = RESULTS_DIR / "kf_only_severity.csv"
OUT_JSON = RESULTS_DIR / "kf_only_ordering.json"
OUT_TXT = RESULTS_DIR / "kf_only_ordering.txt"

SUMMARY = {}

# ====================================================================
# PART A: Cross-organ k_f-only ranking (Tabula Sapiens)
# ====================================================================
print("=" * 60)
print("PART A: Cross-organ k_f-only ranking (Tabula Sapiens)")
print("=" * 60)

from cki.core import js_divergence

RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200

# --- Loading (verbatim from 13_phase35_method_comparison.py E0) ---
adatas_raw = {}
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        adata = sc.read_h5ad(fname)
        adata.obs["organ"] = organ
        adatas_raw[organ] = adata
        print(f"  TS_{organ}: {adata.n_obs} cells")

all_gene_sets = [set(a.var_names) for a in adatas_raw.values()]
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))

adata_list = []
for organ, adata in adatas_raw.items():
    adata_sub = adata[:, common_genes].copy()
    adata_sub.obs["organ"] = organ
    adata_list.append(adata_sub)

adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
gene_names = adata.var_names.tolist()
hk_global_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human_genes])
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes; HK: {len(hk_global_idx)}")

ct_entries = []
for organ in TS_ORGANS:
    tdata = adata[adata.obs["organ"] == organ]
    ct_labels = tdata.obs["cell_ontology_class"].value_counts()
    for ct, count in ct_labels.items():
        if ct.lower() == "unknown":
            continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2:
            continue
        if "donor" in ct_data.obs.columns:
            donor_counts = ct_data.obs["donor"].value_counts()
            donors_ok = [(d, n) for d, n in donor_counts.items() if n >= MIN_CELLS_PER_CT]
        else:
            donors_ok = [("pooled", ct_data.n_obs)]
        if len(donors_ok) < 1:
            continue
        donors_ok.sort(key=lambda x: -x[1])
        largest_donor = donors_ok[0][0]
        if "donor" in ct_data.obs.columns:
            mask_largest = ct_data.obs["donor"] == largest_donor
        else:
            mask_largest = slice(None)
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, "toarray"):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({"key": f"{organ}|{ct}", "organ": organ, "ct": ct, "pb": pb})

n_ct = len(ct_entries)
print(f"  Viable CT entries: {n_ct}")

# --- Same-cell-type cross-organ pairs (verbatim metric logic from phase35) ---
rows = []
for i in range(n_ct):
    for j in range(i + 1, n_ct):
        if ct_entries[i]["ct"] != ct_entries[j]["ct"]:
            continue
        if ct_entries[i]["organ"] == ct_entries[j]["organ"]:
            continue
        pb_i = ct_entries[i]["pb"]
        pb_j = ct_entries[j]["pb"]

        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = float(js_divergence(hk_i, hk_j))

        abs_diff = np.abs(pb_i - pb_j)
        non_hk_mask = np.ones(len(gene_names), dtype=bool)
        non_hk_mask[hk_global_idx] = False
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1
        top_n = min(N_TOP_KF, non_hk_mask.sum())
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        top_idx = top_idx[np.argsort(abs_diff_non_hk[top_idx])[::-1]]
        kf_val = float(js_divergence(pb_i[top_idx], pb_j[top_idx]))
        omega_val = kf_val / kn_val if kn_val > 0 else float("inf")

        rows.append({
            "ct": ct_entries[i]["ct"],
            "organ_i": ct_entries[i]["organ"],
            "organ_j": ct_entries[j]["organ"],
            "omega": omega_val,
            "kf": kf_val,
            "kn": kn_val,
        })

pairs_df = pd.DataFrame(rows)
print(f"\n  Same-CT cross-organ pairs: {len(pairs_df)} ({pairs_df['ct'].nunique()} cell types)")

# --- Per-CT aggregation ---
grp = pairs_df.groupby("ct").agg(
    n_pairs=("omega", "count"),
    mean_omega=("omega", "mean"),
    mean_kf=("kf", "mean"),
    mean_kn=("kn", "mean"),
).reset_index().sort_values("mean_omega").reset_index(drop=True)

# Sanity: reproduce phase35_cross_organ_summary.csv
ref = pd.read_csv(RESULTS_DIR / "phase35_cross_organ_summary.csv")
merged = grp.merge(ref, on="ct", suffixes=("_new", "_ref"))
max_delta = float(np.max(np.abs(merged["mean_omega_new"] - merged["mean_omega_ref"])))
print(f"  Sanity vs phase35_cross_organ_summary.csv: max |delta mean omega| = {max_delta:.2e} "
      f"over {len(merged)}/{len(ref)} CTs")
assert max_delta < 1e-9, "Part A does NOT reproduce phase35 summary!"

# --- Rank agreement ---
r_pair, p_pair = spearmanr(pairs_df["omega"], pairs_df["kf"])
r_ct_kf, p_ct_kf = spearmanr(grp["mean_omega"], grp["mean_kf"])
r_ct_kn, p_ct_kn = spearmanr(grp["mean_omega"], grp["mean_kn"])

grp["omega_rank"] = grp["mean_omega"].rank().astype(int)
grp["kf_rank"] = grp["mean_kf"].rank().astype(int)
grp["kn_rank"] = grp["mean_kn"].rank().astype(int)
grp["well_sampled"] = grp["n_pairs"] >= 5

ws = grp[grp["well_sampled"]]
r_ws_kf, p_ws_kf = spearmanr(ws["mean_omega"], ws["mean_kf"])
r_ws_kn, p_ws_kn = spearmanr(ws["mean_omega"], ws["mean_kn"])

print(f"\n  Per-pair Spearman(omega, k_f), n={len(pairs_df)}: r = {r_pair:.3f} (P = {p_pair:.2e})")
print(f"  Per-CT  Spearman(mean omega, mean k_f), n={len(grp)}: r = {r_ct_kf:.3f} (P = {p_ct_kf:.3f})")
print(f"  Per-CT  Spearman(mean omega, mean k_n), n={len(grp)}: r = {r_ct_kn:.3f} (P = {p_ct_kn:.3f})")
print(f"  Well-sampled (n>=5, n={len(ws)}): Spearman(omega, k_f) r = {r_ws_kf:.3f} (P = {p_ws_kf:.3f}); "
      f"Spearman(omega, k_n) r = {r_ws_kn:.3f} (P = {p_ws_kn:.3f})")

print("\n  Per-CT table (sorted by mean omega):")
for _, r in grp.iterrows():
    flag = " *" if r["well_sampled"] else ""
    print(f"    {r['ct']:<42} n={int(r['n_pairs'])}  omega={r['mean_omega']:7.2f}  "
          f"k_f={r['mean_kf']:7.4f}  k_n={r['mean_kn']:7.5f}{flag}")

# Extremes under each metric (all 17 CTs, and well-sampled subset)
def extremes(df, col):
    d = df.sort_values(col)
    return (d.iloc[0]["ct"], d.iloc[-1]["ct"])

ext_omega = extremes(grp, "mean_omega")
ext_kf = extremes(grp, "mean_kf")
ext_kf_ws = extremes(ws, "mean_kf")
print(f"\n  Extremes by mean omega: most conserved = {ext_omega[0]}, most divergent = {ext_omega[1]}")
print(f"  Extremes by mean k_f  : most conserved = {ext_kf[0]}, most divergent = {ext_kf[1]}")
print(f"  Extremes by mean k_f (well-sampled): most conserved = {ext_kf_ws[0]}, most divergent = {ext_kf_ws[1]}")

SUMMARY["part_a"] = {
    "n_pairs": int(len(pairs_df)),
    "n_ct": int(len(grp)),
    "n_ct_well_sampled": int(len(ws)),
    "spearman_pair_omega_kf": {"r": float(r_pair), "p": float(p_pair)},
    "spearman_ct_omega_kf": {"r": float(r_ct_kf), "p": float(p_ct_kf)},
    "spearman_ct_omega_kn": {"r": float(r_ct_kn), "p": float(p_ct_kn)},
    "spearman_wellsampled_omega_kf": {"r": float(r_ws_kf), "p": float(p_ws_kf)},
    "spearman_wellsampled_omega_kn": {"r": float(r_ws_kn), "p": float(p_ws_kn)},
    "extremes_by_omega": {"most_conserved": ext_omega[0], "most_divergent": ext_omega[1]},
    "extremes_by_kf": {"most_conserved": ext_kf[0], "most_divergent": ext_kf[1]},
    "extremes_by_kf_wellsampled": {"most_conserved": ext_kf_ws[0], "most_divergent": ext_kf_ws[1]},
    "sanity_max_delta_vs_phase35": max_delta,
    "per_ct": [
        {"ct": r["ct"], "n_pairs": int(r["n_pairs"]),
         "mean_omega": float(r["mean_omega"]), "mean_kf": float(r["mean_kf"]),
         "mean_kn": float(r["mean_kn"]), "well_sampled": bool(r["well_sampled"])}
        for _, r in grp.iterrows()
    ],
}
grp_out = grp[["ct", "n_pairs", "mean_omega", "mean_kf", "mean_kn",
               "omega_rank", "kf_rank", "kn_rank", "well_sampled"]]
grp_out.to_csv(OUT_CSV, index=False)
print(f"\n  Wrote {OUT_CSV}")

# ====================================================================
# PART B: TCGA severity k_f-only / k_n control
# ====================================================================
print("\n" + "=" * 60)
print("PART B: TCGA severity k_f-only / k_n control")
print("=" * 60)

from cki.core import compute_omega

LIHC_CLINICAL_FILE = DATA_DIR / "tcga" / "lihc_patient_clinical.json"
LUAD_MUTATION_FILE = DATA_DIR / "tcga" / "luad_egfr_kras_mutations.json"
PAM50_CACHE = RESULTS_DIR / "phase34_pam50_cache.json"
MAX_PAIRS_TT = 2000

# --- Probe map / HK (verbatim from 07) ---
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

hk_df2 = pd.read_csv(HK_FILE)
hk_raw = hk_df2.iloc[:, 0].dropna().astype(str)
hk_human = set()
for row in hk_raw:
    parts = row.split(";")
    if len(parts) >= 2:
        hk_human.add(parts[1].strip())

# --- Clinical maps (verbatim from 07) ---
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

# --- TSS -> project map (verbatim from 07) ---
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
    all_sample_ids = fh.readline().strip().split("\t")[1:]

proj_tumor = {}
proj_normal = {}
sample_to_participant = {}
for sid in all_sample_ids:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    proj = TSS_TO_PROJECT.get(parts[1])
    if proj is None or proj not in ("TCGA-LIHC", "TCGA-BRCA", "TCGA-LUAD"):
        continue
    sample_to_participant[sid] = "-".join(parts[:3])
    if parts[3][:2] == "01":
        proj_tumor.setdefault(proj, []).append(sid)
    elif parts[3][:2] == "11":
        proj_normal.setdefault(proj, []).append(sid)

print(f"  Samples: " + ", ".join(
    f"{k}: T={len(proj_tumor[k])}, N={len(proj_normal.get(k, []))}" for k in proj_tumor))


def load_cancer_data(cancer, tumor_ids, normal_ids):
    """Load expression for ONE cancer type (verbatim per-cancer filtering from 07,
    including normal columns so gene filtering is identical to the published run)."""
    wanted = set(tumor_ids + normal_ids)
    col_idx_map = {}
    for k, sid in enumerate(all_sample_ids, 1):
        if sid in wanted:
            col_idx_map[sid] = k
    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)

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
    expr_log = np.log2(np.maximum(expr, 0) + 1)

    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)
    tumor_mask = np.array([s in set(tumor_ids) for s in sample_list])
    return expr_log, hk_arr, genes, sample_list, tumor_mask


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


def jttest_on_ranks(groups):
    """Manual Jonckheere-Terpstra test (verbatim from 07).

    Implementation note: 07_phase34_clinical.py prefers
    scipy.stats.jttest_on_ranks (scipy >= 1.17) and uses this manual
    implementation only as its ImportError fallback.  Both use the same
    JT statistic with 0.5 tie credit and the same normal approximation,
    and the Part B sanity check (12/12 strata at zero deviation) was run
    against the published omega values, which came from the scipy path.
    The k_f/k_n JT P-values reported here therefore use the identical
    statistic and variance formula as the published omega tests.
    """
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


# Per-cancer TT computation with omega / kf / kn
part_b = {}
severity_rows = []

STRATA = {
    "TCGA-LIHC": ("Edmondson_grade", lambda i, sid, part: lihc_grade_map.get(part),
                  ["G1", "G2", "G3", "G4"], "jt"),
    "TCGA-BRCA": ("PAM50", lambda i, sid, part: pam50_map.get(sid),
                  sorted(set(pam50_map.values())), "kw"),
    "TCGA-LUAD": ("mutation", lambda i, sid, part: luad_mutation_map.get(sid, "WT"),
                  ["WT", "EGFR", "KRAS"], "kw"),
}

for cancer in ("TCGA-LIHC", "TCGA-BRCA", "TCGA-LUAD"):
    t0 = time.time()
    print(f"\n--- {cancer} ---")
    expr_log, hk_arr, genes, sample_list, tumor_mask = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal.get(cancer, []))
    t_idx = np.where(tumor_mask)[0]
    tumor_sids = [sample_list[i] for i in t_idx]
    n_t = len(tumor_sids)
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}")

    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    np.random.seed(RANDOM_SEED)
    if len(all_tt) > MAX_PAIRS_TT:
        tt_pairs = [all_tt[k] for k in np.random.choice(len(all_tt), MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt

    omega_tt = np.full((n_t, n_t), np.nan)
    kf_tt = np.full((n_t, n_t), np.nan)
    kn_tt = np.full((n_t, n_t), np.nan)
    for idx, (a, b) in enumerate(tt_pairs):
        i, j = t_idx[a], t_idx[b]
        p1, p2 = expr_log[i, :], expr_log[j, :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        omega_tt[a, b] = omega_tt[b, a] = r["omega"]
        kf_tt[a, b] = kf_tt[b, a] = r["kf"]
        kn_tt[a, b] = kn_tt[b, a] = r["kn"]
        if (idx + 1) % 500 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)} ({time.time()-t0:.0f}s)", end="\r")
    print(f"    TT: {len(tt_pairs)}/{len(all_tt)} done ({time.time()-t0:.0f}s)")

    # Per-tumor row means (tumor-position axis)
    with np.errstate(invalid="ignore"):
        tumor_omega = np.nanmean(omega_tt, axis=1)
        tumor_kf = np.nanmean(kf_tt, axis=1)
        tumor_kn = np.nanmean(kn_tt, axis=1)

    strat_name, strat_fn, order, test_kind = STRATA[cancer]
    group_vals = {"omega": {}, "kf": {}, "kn": {}}
    for i_pos, sid in enumerate(tumor_sids):
        part = sample_to_participant[sid]
        g = strat_fn(i_pos, sid, part)
        if g is None or g == "EGFR+KRAS":
            continue
        if np.isnan(tumor_omega[i_pos]) or np.isnan(tumor_kf[i_pos]) or np.isnan(tumor_kn[i_pos]):
            continue  # tumor not covered by any sampled TT pair (mirrors 07)
        for m, arr in (("omega", tumor_omega), ("kf", tumor_kf), ("kn", tumor_kn)):
            group_vals[m].setdefault(g, []).append(float(arr[i_pos]))

    order = [g for g in order if g in group_vals["omega"]]
    part_b[cancer] = {}
    print(f"\n  {strat_name} strata (per-tumor mean of TT pairs):")
    print(f"    {'group':<16} {'n':>4} {'omega':>8} {'k_f':>9} {'k_n':>10}")
    for g in order:
        n_g = len(group_vals["omega"][g])
        mo = np.mean(group_vals["omega"][g])
        mk = np.mean(group_vals["kf"][g])
        mn = np.mean(group_vals["kn"][g])
        so = np.std(group_vals["omega"][g])
        sk = np.std(group_vals["kf"][g])
        sn = np.std(group_vals["kn"][g])
        print(f"    {g:<16} {n_g:>4} {mo:>8.2f} {mk:>9.4f} {mn:>10.6f}")
        severity_rows.append({
            "cancer": cancer.replace("TCGA-", ""), "stratification": strat_name,
            "group": g, "n": n_g,
            "omega_mean": round(mo, 2), "omega_std": round(so, 2),
            "kf_mean": round(mk, 4), "kf_std": round(sk, 4),
            "kn_mean": round(mn, 6), "kn_std": round(sn, 6),
        })
        part_b[cancer][g] = {"n": n_g, "omega_mean": float(mo), "kf_mean": float(mk),
                             "kn_mean": float(mn)}

    tests = {}
    for m in ("omega", "kf", "kn"):
        groups = [np.array(group_vals[m][g]) for g in order]
        if test_kind == "jt":
            stat, p = jttest_on_ranks(groups)
            tests[m] = {"test": "Jonckheere-Terpstra", "stat": float(stat), "p": float(p)}
        else:
            stat, p = kruskal(*groups)
            tests[m] = {"test": "Kruskal-Wallis", "stat": float(stat), "p": float(p)}
        print(f"    {m:>5}: {tests[m]['test']} stat={tests[m]['stat']:.2f}, P={tests[m]['p']:.3e}")
    part_b[cancer]["tests"] = tests

# Sanity: omega stratum means vs published severity CSV
ref_sev = pd.read_csv(RESULTS_DIR / "phase34_clinical_severity.csv")
sev_df = pd.DataFrame(severity_rows)
merged_sev = sev_df.merge(ref_sev, on=["cancer", "stratification", "group", "n"],
                          suffixes=("_new", "_ref"))
max_delta_sev = float(np.max(np.abs(merged_sev["omega_mean_new"] - merged_sev["omega_mean_ref"])))
print(f"\n  Sanity vs phase34_clinical_severity.csv: max |delta omega mean| = {max_delta_sev:.2f} "
      f"over {len(merged_sev)}/{len(ref_sev)} strata")
assert max_delta_sev < 0.5, "Part B omega does NOT reproduce published severity!"

SUMMARY["part_b"] = {
    "strata": part_b,
    "sanity_max_delta_vs_published_severity": max_delta_sev,
}

# --- Write outputs ---
with open(OUT_JSON, "w") as f:
    json.dump(SUMMARY, f, indent=2)
sev_df.to_csv(OUT_SEV, index=False)

with open(OUT_TXT, "w") as f:
    f.write("k_f-only ordering control (P1-3)\n")
    f.write("=" * 60 + "\n\nPART A: Cross-organ (Tabula Sapiens)\n")
    a = SUMMARY["part_a"]
    f.write(f"n pairs = {a['n_pairs']}, n CTs = {a['n_ct']} (well-sampled {a['n_ct_well_sampled']})\n")
    f.write(f"Per-pair Spearman(omega, k_f): r = {a['spearman_pair_omega_kf']['r']:.3f} "
            f"(P = {a['spearman_pair_omega_kf']['p']:.2e})\n")
    f.write(f"Per-CT Spearman(mean omega, mean k_f): r = {a['spearman_ct_omega_kf']['r']:.3f} "
            f"(P = {a['spearman_ct_omega_kf']['p']:.3f})\n")
    f.write(f"Per-CT Spearman(mean omega, mean k_n): r = {a['spearman_ct_omega_kn']['r']:.3f} "
            f"(P = {a['spearman_ct_omega_kn']['p']:.3f})\n")
    f.write(f"Well-sampled Spearman(omega, k_f): r = {a['spearman_wellsampled_omega_kf']['r']:.3f}\n")
    f.write(f"Well-sampled Spearman(omega, k_n): r = {a['spearman_wellsampled_omega_kn']['r']:.3f}\n")
    f.write(f"Extremes by omega: {a['extremes_by_omega']}\n")
    f.write(f"Extremes by k_f:   {a['extremes_by_kf']}\n")
    f.write(f"Extremes by k_f (well-sampled): {a['extremes_by_kf_wellsampled']}\n\n")
    f.write("PART B: TCGA severity strata\n")
    for cancer, info in SUMMARY["part_b"]["strata"].items():
        f.write(f"\n{cancer}\n")
        for g, vals in info.items():
            if g == "tests":
                continue
            f.write(f"  {g:<16} n={vals['n']:>4}  omega={vals['omega_mean']:8.2f}  "
                    f"k_f={vals['kf_mean']:8.4f}  k_n={vals['kn_mean']:.6f}\n")
        for m, t in info["tests"].items():
            f.write(f"  {m}: {t['test']} P={t['p']:.3e}\n")

print(f"\nWrote {OUT_JSON}, {OUT_SEV}, {OUT_TXT}")
print("DONE")
