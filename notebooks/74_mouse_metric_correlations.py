"""
CKI Phase 3.5-Mouse: Method comparison on Tabula Muris (fix Fig 2C)
====================================================================
Fig 2C claims Spearman correlations between CKI omega and four standard
metrics "on Tabula Muris data", but the figure previously displayed the
Tabula Sapiens (human) values from figure_data_correlations.npy
(corrs_2c = -0.386/-0.396/-0.358/-0.461). This script recomputes the
metrics on the mouse calibration dataset:

  Data:   phase32 pipeline — 6 FACS tissues, QC (min_genes=500, min_cells=3),
          normalize_total(1e4) + log1p, largest-mouse-group pseudobulks
          (>=10 cells per mouse, >=20 cells per CT) -> 38 CT entries -> 703 pairs
  Metrics (identical to 13_phase35_method_comparison.py):
    1. CKI omega (hybrid: global HK k_n + per-pair top-200 non-HK DE k_f,
       softmax inside cki.core.js_divergence)
    2. Raw JS divergence (all genes)
    3. Spearman distance (1 - rho)
    4. Cosine distance (1 - cosine similarity)
    5. Marker Jaccard distance (1 - Jaccard of top-200 expressed genes)

Outputs:
  results/phase35_mouse_metric_correlation.csv   (5x5 Spearman matrix)
  results/phase35_mouse_all_metrics_pairs.csv    (703 pairs x 5 metrics)
  results/figure_data_correlations_mouse.npy     (metrics_2c + corrs_2c
                                                  consumed by _fig2_clean.py)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
np.random.seed(42)
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr
from cki.core import js_divergence

# -- Config (mirrors phase32 / phase35) --
TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200
N_MARKER = 200

# ============================================================
# 1. Load data (phase32 pipeline)
# ============================================================
print("=" * 60)
print("1. Loading Tabula Muris FACS data (phase32 pipeline)...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse_genes = set(hk_df["Mouse"].dropna().tolist())
print(f"  HK genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(FACS_ANNOTATIONS)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]

def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)
print(f"  Annotations: {len(annot)} cells")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# ============================================================
# 2. Unified AnnData + preprocessing (phase32 pipeline)
# ============================================================
print("\n" + "=" * 60)
print("2. Building unified AnnData + QC + normalization...")
print("=" * 60)

common_genes = sorted(all_genes.copy())
for tissue, df in adatas.items():
    common_genes = [g for g in common_genes if g in df.index]
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(
        tissue_annot[["cell", "cell_ontology_class", "mouse.id"]],
        on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} x {adata.n_vars}")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

gene_names = adata.var_names.tolist()
hk_global_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_mouse_genes])
print(f"  Global HK genes in data: {len(hk_global_idx)}")

# ============================================================
# 3. CT pseudobulks — largest mouse group (phase32 pipeline)
# ============================================================
print("\n" + "=" * 60)
print("3. Building CT pseudobulks (largest mouse group)...")
print("=" * 60)

ct_entries = []
for tissue in TARGET_TISSUES:
    tdata = adata[adata.obs["tissue"] == tissue]
    for ct in tdata.obs["cell_ontology_class"].unique():
        if ct.lower() == "unknown":
            continue
        ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2:
            continue
        mouse_counts = ct_data.obs["mouse.id"].value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) < 1:
            continue
        mice_ok.sort(key=lambda x: -x[1])
        largest_mouse = mice_ok[0][0]
        mask_largest = ct_data.obs["mouse.id"] == largest_mouse
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, "toarray"):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({
            "key": f"{tissue}|{ct}",
            "tissue": tissue,
            "ct": ct,
            "pb": pb,
            "n_cells": X_large.shape[0],
        })

n_ct = len(ct_entries)
total_pairs = n_ct * (n_ct - 1) // 2
print(f"  Viable CT entries: {n_ct}  ->  {total_pairs} pairs")
assert n_ct == 38 and total_pairs == 703, \
    f"Expected 38 CT entries / 703 pairs (phase32 ground truth), got {n_ct}/{total_pairs}"

# ============================================================
# 4. Compute 5 metrics for all pairs (phase35 hybrid scheme)
# ============================================================
print("\n" + "=" * 60)
print("4. Computing 5 metrics for all pairs (phase35 hybrid scheme)...")
print("=" * 60)

# Per-CT top marker genes (Jaccard)
ct_marker_sets = []
for i in range(n_ct):
    pb_i = ct_entries[i]["pb"]
    top_n = min(N_MARKER, len(pb_i))
    top_idx = np.argpartition(pb_i, -top_n)[-top_n:]
    ct_marker_sets.append(set(top_idx.tolist()))

pairs_list = []
for i in range(n_ct):
    for j in range(i + 1, n_ct):
        pb_i = ct_entries[i]["pb"]
        pb_j = ct_entries[j]["pb"]

        # M1: CKI omega (hybrid — global HK k_n + per-pair top-200 non-HK DE k_f)
        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = float(js_divergence(hk_i, hk_j))

        abs_diff = np.abs(pb_i - pb_j)
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1
        top_n = min(N_TOP_KF, len(gene_names) - len(hk_global_idx))
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        kf_val = float(js_divergence(pb_i[top_idx], pb_j[top_idx]))
        omega_val = kf_val / kn_val if kn_val > 0 else float("inf")

        # M2: Raw JS (all genes)
        js_raw_val = float(js_divergence(pb_i, pb_j))

        # M3: Spearman distance
        rho_val, _ = spearmanr(pb_i, pb_j)
        spearman_val = 1.0 - rho_val

        # M4: Cosine distance
        dot_ij = np.dot(pb_i, pb_j)
        norm_i = np.linalg.norm(pb_i)
        norm_j = np.linalg.norm(pb_j)
        if norm_i > 1e-12 and norm_j > 1e-12:
            cos_sim = np.clip(dot_ij / (norm_i * norm_j), -1.0, 1.0)
        else:
            cos_sim = 0.0
        cosine_val = 1.0 - cos_sim

        # M5: Marker Jaccard distance
        set_i, set_j = ct_marker_sets[i], ct_marker_sets[j]
        union = len(set_i | set_j)
        jaccard_sim = len(set_i & set_j) / union if union > 0 else 0.0
        marker_jaccard_val = 1.0 - jaccard_sim

        pairs_list.append({
            "pair": f"{ct_entries[i]['key']} vs {ct_entries[j]['key']}",
            "ct_i": ct_entries[i]["ct"],
            "ct_j": ct_entries[j]["ct"],
            "tissue_i": ct_entries[i]["tissue"],
            "tissue_j": ct_entries[j]["tissue"],
            "same_tissue": ct_entries[i]["tissue"] == ct_entries[j]["tissue"],
            "same_ct": ct_entries[i]["ct"] == ct_entries[j]["ct"],
            "omega": omega_val,
            "js_raw": js_raw_val,
            "spearman_dist": spearman_val,
            "cosine_dist": cosine_val,
            "marker_jaccard_dist": marker_jaccard_val,
        })
    print(f"  Progress: row {i + 1}/{n_ct}")

pairs_df = pd.DataFrame(pairs_list)
pairs_df.to_csv(RESULTS_DIR / "phase35_mouse_all_metrics_pairs.csv", index=False)
print(f"  Saved: phase35_mouse_all_metrics_pairs.csv ({len(pairs_df)} pairs)")

# ============================================================
# 5. Inter-metric Spearman correlation matrix
# ============================================================
print("\n" + "=" * 60)
print("5. Inter-metric Spearman correlation matrix...")
print("=" * 60)

metric_names = ["CKI omega", "Raw JS", "Spearman dist", "Cosine dist", "Marker Jaccard dist"]
metric_arrays = [pairs_df["omega"].to_numpy(), pairs_df["js_raw"].to_numpy(),
                 pairs_df["spearman_dist"].to_numpy(), pairs_df["cosine_dist"].to_numpy(),
                 pairs_df["marker_jaccard_dist"].to_numpy()]

n_metrics = len(metric_names)
corr_matrix = np.zeros((n_metrics, n_metrics))
pval_matrix = np.zeros((n_metrics, n_metrics))
for i in range(n_metrics):
    for j in range(n_metrics):
        if i == j:
            corr_matrix[i, j], pval_matrix[i, j] = 1.0, 0.0
        else:
            r, p = spearmanr(metric_arrays[i], metric_arrays[j])
            corr_matrix[i, j], pval_matrix[i, j] = r, p

corr_df = pd.DataFrame(corr_matrix, index=metric_names, columns=metric_names)
corr_df.to_csv(RESULTS_DIR / "phase35_mouse_metric_correlation.csv")
print("  Saved: phase35_mouse_metric_correlation.csv")
print(corr_df.round(3).to_string())

# ============================================================
# 6. Fig 2C payload (same key order as precompute_figure_data.py)
# ============================================================
metrics_order_2c = ["Cosine dist", "Raw JS", "Marker Jaccard dist", "Spearman dist"]
corrs_2c = [float(corr_df.loc["CKI omega", m]) for m in metrics_order_2c]
print(f"\n  Fig 2C mouse corrs = {[f'{c:.3f}' for c in corrs_2c]}")

payload = {
    "corrs_2c": corrs_2c,
    "metrics_2c": ["Cosine", "Raw JS", "Marker Jaccard", "Spearman"],
    "n_pairs": int(len(pairs_df)),
    "n_ct": int(n_ct),
    "dataset": "Tabula Muris (mouse)",
}
np.save(RESULTS_DIR / "figure_data_correlations_mouse.npy", payload,
        allow_pickle=True)
print("  Saved: figure_data_correlations_mouse.npy")

print("\n" + "=" * 60)
print("Phase 3.5-Mouse COMPLETE.")
print("=" * 60)
