"""
01b_hk_stability.py — HK gene set size stability analysis
===========================================================
Produces: results/hk_stability_sweep.csv

Evaluates k_n convergence as the number of housekeeping genes increases.
Uses Tabula Muris mouse data to systematically vary n_HK and compute k_n
for all tissue pairs. The resulting CSV is used by ED Fig 1A.

Method:
- Load Tabula Muris FACS SmartSeq2 data for 6 organs
- Normalize and select HVGs
- Starting from the full HRT Atlas HK gene set, rank by detection rate
- Subsample HK genes at increasing sizes [250, 500, 750, 1000, 1250, 1500]
- For each size, compute k_n for all 15 tissue pairs
- Report mean and SD of k_n across pairs
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path

from cki.core import compute_omega

# ── Config ──────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE  = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
N_HVG = 2000
RANDOM_SEED = 42
HK_SIZES = [250, 500, 750, 1000, 1250, 1500]

np.random.seed(RANDOM_SEED)
sc.settings.verbosity = 1

# ── 1. Load Data ────────────────────────────────────────────
print("1. Loading data...")
hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_ref_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  Reference HK genes: {len(hk_ref_genes)}")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# ── 2. Unified AnnData ──────────────────────────────────────
print("2. Building unified AnnData...")
common_genes = sorted(all_genes)
for df in adatas.values():
    common_genes = [g for g in common_genes if g in df.index]
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue in TARGET_TISSUES:
    df = adatas[tissue]
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    obs_tissue = pd.DataFrame({"cell": df_aligned.index.tolist(), "tissue": tissue})
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
adata.obs["tissue"] = adata.obs["tissue"].astype("category")
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

# ── 3. Preprocessing ────────────────────────────────────────
print("3. Preprocessing...")
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=N_HVG, flavor="seurat")
print(f"  After QC: {adata.n_obs} x {adata.n_vars}")
print(f"  HVGs: {adata.var['highly_variable'].sum()}")

# ── 4. Map HK genes, rank by detection rate ─────────────────
gene_names = adata.var_names.tolist()
hk_in_data = [g for g in gene_names if g in hk_ref_genes]
print(f"  HK genes matched in data: {len(hk_in_data)}")

# Compute detection rate for each HK gene (fraction of cells expressing > 0)
hk_detection = {}
for g in hk_in_data:
    idx = gene_names.index(g)
    expr = adata.X[:, idx]
    if hasattr(expr, "toarray"):
        expr = expr.toarray()
    hk_detection[g] = np.mean(expr.flatten() > 0)

# Sort HK genes by detection rate (highest first)
hk_ranked = sorted(hk_detection.items(), key=lambda x: -x[1])
hk_ranked_indices = [gene_names.index(g) for g, _ in hk_ranked]

# Identity genes: HVGs excluding HK
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()
identity_indices = [i for i in identity_indices if i not in set(hk_ranked_indices)]
print(f"  Identity genes: {len(identity_indices)}")

# ── 5. Tissue pseudobulks ───────────────────────────────────
print("5. Building tissue pseudobulks...")
tissue_pb = {}
for t in TARGET_TISSUES:
    mask = adata.obs["tissue"] == t
    X_t = adata[mask].X
    if hasattr(X_t, "toarray"):
        X_t = X_t.toarray()
    tissue_pb[t] = np.mean(X_t, axis=0)
    print(f"  {t}: {mask.sum()} cells")

# ── 6. Sweep n_HK and compute k_n for all tissue pairs ──────
print("6. Sweeping n_HK...")
results = []
for n_hk in HK_SIZES:
    if n_hk > len(hk_ranked_indices):
        print(f"  n_HK={n_hk}: exceeds available genes ({len(hk_ranked_indices)}), skipping")
        continue
    hk_subset = hk_ranked_indices[:n_hk]
    
    kn_values = []
    for i, ti in enumerate(TARGET_TISSUES):
        for j, tj in enumerate(TARGET_TISSUES):
            if i >= j:
                continue
            result = compute_omega(
                tissue_pb[ti], tissue_pb[tj],
                hk_subset, identity_indices,
            )
            kn_values.append(result["kn"])
    
    kn_mean = np.mean(kn_values)
    kn_std = np.std(kn_values)
    results.append({"n_hk": n_hk, "kn_mean": kn_mean, "kn_std": kn_std})
    print(f"  n_HK={n_hk}: k_n = {kn_mean:.4f} ± {kn_std:.4f}")

# ── 7. Save ─────────────────────────────────────────────────
print("7. Saving...")
hk_stab_df = pd.DataFrame(results)
hk_stab_df.to_csv(RESULTS_DIR / "hk_stability_sweep.csv", index=False)
print(f"  Saved: hk_stability_sweep.csv")
print(hk_stab_df.to_string(index=False))

print("DONE.")
