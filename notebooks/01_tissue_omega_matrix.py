"""
01_tissue_omega_matrix.py — Tissue-level CKI omega matrix (Tabula Muris mouse)
================================================================================
Produces: results/omega_matrix_tissue.csv

This script computes pairwise CKI ω between 6 mouse organs (Heart, Kidney, Liver,
Lung, Marrow, Spleen) from Tabula Muris FACS SmartSeq2 data. Each organ's
pseudobulk is the mean expression across all cells in that organ.

Gene sets:
- HK genes: HRT Atlas human-mouse conserved reference (1,130 genes)
- Identity genes: top-2,000 HVGs (Seurat v3), excluding HK genes

Required data files:
- data/FACS/FACS/{tissue}-counts.csv  (6 files)
- data/housekeeping/Human_Mouse_Common.csv
- data/annotations_FACS.csv

Output:
- results/omega_matrix_tissue.csv  (6x6 symmetric matrix)
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
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
MIN_GENES_PER_CELL = 500
MIN_CELLS_PER_GENE = 3
N_HVG = 2000
RANDOM_SEED = 42
TARGET_SUM = 1e4

np.random.seed(RANDOM_SEED)

# ── 1. Load Data ────────────────────────────────────────────
print("=" * 60)
print("1. Loading data...")
print("=" * 60)

# Load HK genes from HRT Atlas reference
hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  Reference HK genes loaded: {len(hk_mouse_genes)}")

# Load annotations
annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
print(f"  Annotations: {len(annot)} cells in target tissues")

# Load count matrices per tissue
adatas = {}
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        print(f"  WARNING: {fname} not found, skipping")
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    print(f"  {tissue}: {df.shape[1]} cells x {df.shape[0]} genes")

# ── 2. Build Unified AnnData ────────────────────────────────
print("\n" + "=" * 60)
print("2. Building unified AnnData...")
print("=" * 60)

# Align genes: intersection of all loaded tissues
all_genes = set()
for df in adatas.values():
    all_genes.update(df.index.tolist())
common_genes = all_genes.copy()
for df in adatas.values():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)
print(f"  Common genes across all tissues: {len(common_genes)}")

# Build expression matrix
expr_parts = []
obs_parts = []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0)
    df_aligned = df_aligned.T  # cells x genes
    expr_parts.append(df_aligned.values)
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")

adata = sc.AnnData(X=X, obs=obs, var=var)
adata.obs["tissue"] = adata.obs["tissue"].astype("category")
print(f"  Unified AnnData: {adata.n_obs} cells x {adata.n_vars} genes")

# ── 3. Preprocessing ────────────────────────────────────────
print("\n" + "=" * 60)
print("3. Preprocessing...")
print("=" * 60)

sc.pp.filter_cells(adata, min_genes=MIN_GENES_PER_CELL)
sc.pp.filter_genes(adata, min_cells=MIN_CELLS_PER_GENE)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")

sc.pp.normalize_total(adata, target_sum=TARGET_SUM)
sc.pp.log1p(adata)
print("  Normalized: log1p(CP10k)")

# Select HVGs as identity genes
sc.pp.highly_variable_genes(adata, n_top_genes=N_HVG, flavor="seurat")
n_hvg = adata.var["highly_variable"].sum()
print(f"  HVGs selected: {n_hvg}")

# ── 4. Gene Index Mapping ──────────────────────────────────
print("\n" + "=" * 60)
print("4. Gene index mapping...")
print("=" * 60)

gene_names = adata.var_names.tolist()
hk_indices = [i for i, g in enumerate(gene_names) if g in hk_mouse_genes]
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()

# Exclude HK genes from identity set (maintain independence)
identity_indices = [i for i in identity_indices if i not in set(hk_indices)]

print(f"  HK genes matched: {len(hk_indices)} / {len(hk_mouse_genes)} reference")
print(f"  Identity genes (HVG excl. HK): {len(identity_indices)}")

# ── 5. Tissue Pseudobulk ────────────────────────────────────
print("\n" + "=" * 60)
print("5. Tissue-level pseudobulk...")
print("=" * 60)

tissues = adata.obs["tissue"].cat.categories.tolist()
n_tissues = len(tissues)

tissue_pb = {}
for t in tissues:
    mask = adata.obs["tissue"] == t
    X_t = adata[mask].X
    if hasattr(X_t, "toarray"):
        X_t = X_t.toarray()
    tissue_pb[t] = np.mean(X_t, axis=0)
    print(f"  {t}: {mask.sum()} cells → pseudobulk")

# ── 6. Compute Pairwise Omega Matrix ────────────────────────
print("\n" + "=" * 60)
print("6. Computing pairwise omega matrix...")
print("=" * 60)

omega_matrix = np.full((n_tissues, n_tissues), np.inf)
for i, ti in enumerate(tissues):
    for j, tj in enumerate(tissues):
        if i == j:
            omega_matrix[i, j] = np.inf  # self-comparison
            continue
        result = compute_omega(
            tissue_pb[ti], tissue_pb[tj],
            hk_indices, identity_indices,
        )
        omega_matrix[i, j] = result["omega"]
        print(f"  {ti} vs {tj}: ω={result['omega']:.4f}, "
              f"k_n={result['kn']:.6f}, k_f={result['kf']:.6f}")

# ── 7. Save ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("7. Saving...")
print("=" * 60)

omega_df = pd.DataFrame(omega_matrix, index=tissues, columns=tissues)
omega_df.to_csv(RESULTS_DIR / "omega_matrix_tissue.csv")
print(f"  Saved: omega_matrix_tissue.csv ({omega_df.shape[0]}x{omega_df.shape[1]})")
print(f"  ω range: [{omega_df.values[omega_df.values < np.inf].min():.2f}, "
      f"{omega_df.values[omega_df.values < np.inf].max():.2f}]")
print(f"  ω mean: {omega_df.values[omega_df.values < np.inf].mean():.2f}")

print("\n" + "=" * 60)
print("DONE.")
print("=" * 60)
