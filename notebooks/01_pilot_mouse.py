"""
CKI Pilot Validation — Tabula Muris FACS Mouse Data
=====================================================
Step 3-4: Data loading, preprocessing, CKI computation, bootstrap testing.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path
from tqdm import tqdm

# CJK font setup for Windows
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower() or "simsun" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
    print(f"  Using CJK font: {_cjk_prop.get_name()}")
else:
    plt.rcParams["font.family"] = "sans-serif"
    print("  WARNING: No CJK font found, Chinese labels may not render")

from cki.core import js_divergence, compute_kn, compute_kf, compute_omega
from cki.bootstrap import bootstrap_test
from cki.utils import ensure_probability_distribution

# ── Config ──────────────────────────────────────────────────
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE  = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
N_BOOTSTRAP = 500  # reduced for pilot speed
RANDOM_SEED = 42
MIN_CELLS_PER_TYPE = 20
MIN_GENES_PER_CELL = 500
MIN_CELLS_PER_GENE = 3

# ── 1. Load Data ────────────────────────────────────────────
print("=" * 60)
print("1. Loading data...")
print("=" * 60)

# Load housekeeping genes
hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
print(f"  Housekeeping genes: {len(hk_df)} rows")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())

# Load annotations
annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
print(f"  Annotations: {len(annot)} cells in target tissues")
print(f"  Tissues: {annot['tissue'].value_counts().to_dict()}")

# Load count matrices
adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        print(f"  WARNING: {fname} not found, skipping")
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())
    print(f"  {tissue}: {df.shape[1]} cells x {df.shape[0]} genes")

# ── 2. Build Unified AnnData ────────────────────────────────
print("\n" + "=" * 60)
print("2. Building unified AnnData...")
print("=" * 60)

# Align genes: use intersection of all loaded tissues
common_genes = all_genes.copy()
for tissue, df in adatas.items():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)
print(f"  Common genes: {len(common_genes)}")

# Build expression matrix and cell metadata
expr_parts = []
obs_parts = []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0)
    df_aligned = df_aligned.T  # cells x genes
    expr_parts.append(df_aligned.values)
    
    # Build obs for this tissue
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell", "cell_ontology_class"]],
                                   on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
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

# Basic QC
sc.pp.filter_cells(adata, min_genes=MIN_GENES_PER_CELL)
sc.pp.filter_genes(adata, min_cells=MIN_CELLS_PER_GENE)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
print("  Normalized: log1p(CP10k)")

# HVG selection
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
n_hvg = adata.var["highly_variable"].sum()
print(f"  HVGs: {n_hvg}")

# ── 4. Gene Index Mapping ──────────────────────────────────
print("\n" + "=" * 60)
print("4. Gene index mapping...")
print("=" * 60)

gene_names = adata.var_names.tolist()
hk_indices = [i for i, g in enumerate(gene_names) if g in hk_mouse_genes]
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()
print(f"  HK genes mapped: {len(hk_indices)} / {len(hk_mouse_genes)}")
print(f"  Identity genes (HVG): {len(identity_indices)}")

# ── 5. Tissue-level CKI ─────────────────────────────────────
print("\n" + "=" * 60)
print("5. Tissue-level CKI (pseudobulk per tissue)...")
print("=" * 60)

tissues = adata.obs["tissue"].cat.categories.tolist()
n_tissues = len(tissues)

# Pseudobulk per tissue
tissue_pb = {}
tissue_ncells = {}
for t in tissues:
    mask = adata.obs["tissue"] == t
    if mask.sum() == 0:
        continue
    X_t = adata[mask].X
    if hasattr(X_t, "toarray"):
        X_t = X_t.toarray()
    tissue_pb[t] = np.mean(X_t, axis=0)
    tissue_ncells[t] = mask.sum()

print("  Tissue pseudobulk cells:")
for t, n in tissue_ncells.items():
    print(f"    {t}: {n}")

# Compute omega for all tissue pairs
omega_matrix = np.zeros((n_tissues, n_tissues))
omega_matrix[:] = np.nan
kn_matrix = np.zeros((n_tissues, n_tissues))
kf_matrix = np.zeros((n_tissues, n_tissues))

for i, t1 in enumerate(tissues):
    for j, t2 in enumerate(tissues):
        if tissue_pb.get(t1) is None or tissue_pb.get(t2) is None:
            continue
        result = compute_omega(
            tissue_pb[t1], tissue_pb[t2],
            hk_indices, identity_indices,
            pathway_a=None, pathway_b=None,
            alpha=1.0, w1=1.0, w2=0.0
        )
        omega_matrix[i, j] = result["omega"]
        kn_matrix[i, j] = result["kn"]
        kf_matrix[i, j] = result["kf"]

# ── 6. Cell-type-level CKI ──────────────────────────────────
print("\n" + "=" * 60)
print("6. Cell-type-level CKI...")
print("=" * 60)

# Get major cell types (>= MIN_CELLS_PER_TYPE across all tissues)
ct_counts = adata.obs["cell_ontology_class"].value_counts()
major_types = ct_counts[ct_counts >= MIN_CELLS_PER_TYPE].index.tolist()
# Remove 'unknown'
major_types = [ct for ct in major_types if ct.lower() != "unknown"]
print(f"  Major cell types (>= {MIN_CELLS_PER_TYPE} cells): {len(major_types)}")
for ct in major_types:
    print(f"    {ct}: {ct_counts[ct]} cells")

# Compute pseudobulk per (tissue, cell_type) for types with enough cells
ct_pb = {}  # key: (tissue, cell_type)
for t in tissues:
    for ct in major_types:
        mask = (adata.obs["tissue"] == t) & (adata.obs["cell_ontology_class"] == ct)
        n = mask.sum()
        if n < MIN_CELLS_PER_TYPE:
            continue
        X_ct = adata[mask].X
        if hasattr(X_ct, "toarray"):
            X_ct = X_ct.toarray()
        ct_pb[(t, ct)] = np.mean(X_ct, axis=0)

print(f"  Total (tissue, cell_type) pairs with >= {MIN_CELLS_PER_TYPE} cells: {len(ct_pb)}")

# ── 6b. Split Liver by mouse for proper control ──────────
print("\n" + "=" * 60)
print("6b. Splitting Liver by mouse ID for control...")
print("=" * 60)

# Extract mouse ID from cell barcodes: "F18.MAA000377.3_9_M.1.1" -> "3_9_M"
def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

liver_cells = adata[adata.obs["tissue"] == "Liver"]
liver_mice = [extract_mouse_id(c) for c in liver_cells.obs_names]
mouse_counts = pd.Series(liver_mice).value_counts()
print(f"  Liver mice: {mouse_counts.to_dict()}")

# Group A: 3_9_M + 3_11_M (male), Group B: 3_56_F + 3_57_F (female)
# Or if unbalanced, split largest vs rest
if len(mouse_counts) >= 2:
    sorted_mice = mouse_counts.index.tolist()
    group_a_mice = [sorted_mice[0]]
    group_b_mice = sorted_mice[1:]
    
    mask_a = np.isin(liver_mice, group_a_mice)
    mask_b = np.isin(liver_mice, group_b_mice)
    
    X_liver_a = liver_cells[mask_a].X
    X_liver_b = liver_cells[mask_b].X
    if hasattr(X_liver_a, "toarray"):
        X_liver_a = X_liver_a.toarray()
    if hasattr(X_liver_b, "toarray"):
        X_liver_b = X_liver_b.toarray()
    
    pb_liver_a = np.mean(X_liver_a, axis=0)
    pb_liver_b = np.mean(X_liver_b, axis=0)
    n_liver_a, n_liver_b = X_liver_a.shape[0], X_liver_b.shape[0]
    print(f"  Control groups: A({group_a_mice})={n_liver_a} cells, B({group_b_mice})={n_liver_b} cells")
else:
    print("  WARNING: Cannot split by mouse, using random split")
    n_half = liver_cells.n_obs // 2
    idx = np.random.RandomState(RANDOM_SEED).permutation(liver_cells.n_obs)
    X_liver_a = liver_cells[idx[:n_half]].X
    X_liver_b = liver_cells[idx[n_half:]].X
    if hasattr(X_liver_a, "toarray"):
        X_liver_a = X_liver_a.toarray()
    if hasattr(X_liver_b, "toarray"):
        X_liver_b = X_liver_b.toarray()
    pb_liver_a = np.mean(X_liver_a, axis=0)
    pb_liver_b = np.mean(X_liver_b, axis=0)
    n_liver_a, n_liver_b = n_half, liver_cells.n_obs - n_half

# ── 7. Key Comparisons with Bootstrap ───────────────────────
print("\n" + "=" * 60)
print("7. Key comparisons with bootstrap...")
print("=" * 60)

comparisons = [
    # (label, (tissue_or_group, ct), expected_category, use_split_data)
    ("同组织肝-肝(对照)", ("Liver_split", None), "conserved", True),
    ("肝vs肾(实质器官)", ("Liver", "Kidney"), "moderate", False),
    ("肝vs脾(实质vs免疫)", ("Liver", "Spleen"), "divergent", False),
    ("肝vs骨髓(实质vs造血)", ("Liver", "Marrow"), "divergent", False),
]

results_list = []
for label, (t1_key, t2_key), expected, is_split in comparisons:
    # Get pseudobulk
    if is_split:
        pb1 = pb_liver_a
        pb2 = pb_liver_b
        n1, n2 = n_liver_a, n_liver_b
    else:
        pb1 = tissue_pb.get(t1_key)
        pb2 = tissue_pb.get(t2_key)
        cells1 = adata[adata.obs["tissue"] == t1_key]
        cells2 = adata[adata.obs["tissue"] == t2_key]
        X1 = cells1.X
        X2 = cells2.X
        if hasattr(X1, "toarray"):
            X1 = X1.toarray()
        if hasattr(X2, "toarray"):
            X2 = X2.toarray()
        n1, n2 = X1.shape[0], X2.shape[0]
    
    if pb1 is None or pb2 is None:
        print(f"  SKIP {label}: insufficient data")
        continue
    
    # Compute omega
    result = compute_omega(pb1, pb2, hk_indices, identity_indices)
    
    # Bootstrap
    if is_split:
        # For split control, pool the two liver groups and permute
        pooled = np.vstack([X_liver_a, X_liver_b])
        n_total = n_liver_a + n_liver_b
    else:
        cells1 = adata[adata.obs["tissue"] == t1_key]
        cells2 = adata[adata.obs["tissue"] == t2_key]
        X1 = cells1.X
        X2 = cells2.X
        if hasattr(X1, "toarray"):
            X1 = X1.toarray()
        if hasattr(X2, "toarray"):
            X2 = X2.toarray()
        n1, n2 = X1.shape[0], X2.shape[0]
        pooled = np.vstack([X1, X2])
        n_total = n1 + n2
        n_liver_a_for_perm = n1  # for perm indexing
    
    rng = np.random.RandomState(RANDOM_SEED)
    n_a_perm = n_liver_a if is_split else n1
    
    null_omega = []
    for _ in tqdm(range(N_BOOTSTRAP), desc=f"  {label}"):
        perm = rng.permutation(n_total)
        pb_perm1 = np.mean(pooled[perm[:n_a_perm]], axis=0)
        pb_perm2 = np.mean(pooled[perm[n_a_perm:]], axis=0)
        r = compute_omega(pb_perm1, pb_perm2, hk_indices, identity_indices)
        if not np.isnan(r["omega"]):
            null_omega.append(r["omega"])
    
    null_omega = np.array(null_omega)
    p_value = (np.sum(null_omega >= result["omega"]) + 1) / (len(null_omega) + 1)
    null_mean = np.mean(null_omega)
    null_std = np.std(null_omega)
    cohens_d = (result["omega"] - null_mean) / null_std if null_std > 1e-12 else 0.0
    
    entry = {
        "comparison": label,
        "tissue_A": "Liver_A" if is_split else t1_key,
        "tissue_B": "Liver_B" if is_split else t2_key,
        "omega": result["omega"],
        "kn": result["kn"], "kf": result["kf"],
        "delta_hk": result["delta_hk"],
        "delta_identity": result["delta_identity"],
        "p_value": p_value,
        "null_mean": null_mean, "null_std": null_std,
        "cohens_d": cohens_d,
        "n_cells_A": n_liver_a if is_split else n1,
        "n_cells_B": n_liver_b if is_split else n2,
        "expected": expected,
        "null_distribution": null_omega.tolist() if len(null_omega) > 0 else [],
    }
    results_list.append(entry)
    
    print(f"  {label}: omega={result['omega']:.4f}, kn={result['kn']:.6f}, "
          f"kf={result['kf']:.6f}, p={p_value:.4f}, d={cohens_d:.2f}")

results_df = pd.DataFrame(results_list)

# ── 8. Sensitivity Analysis ────────────────────────────────
print("\n" + "=" * 60)
print("8. Sensitivity analysis (HK gene subset robustness)...")
print("=" * 60)

# Randomly sample 80% of HK genes 10 times, recompute omega for key pairs
n_subsets = 10
hk_subset_frac = 0.8
omega_variations = {}

for label, t1_info, expected, is_split in comparisons:
    if is_split:
        continue  # skip sensitivity for split control
    t1_key, t2_key = t1_info
    pb1 = tissue_pb.get(t1_key)
    pb2 = tissue_pb.get(t2_key)
    if pb1 is None or pb2 is None:
        continue
    
    omegas = []
    rng = np.random.RandomState(RANDOM_SEED)
    for _ in range(n_subsets):
        subset_idx = rng.choice(len(hk_indices),
                                size=int(len(hk_indices) * hk_subset_frac),
                                replace=False)
        hk_sub = [hk_indices[i] for i in subset_idx]
        r = compute_omega(pb1, pb2, hk_sub, identity_indices)
        omegas.append(r["omega"])
    
    omegas = np.array(omegas)
    omega_variations[label] = {
        "mean": np.mean(omegas), "std": np.std(omegas),
        "cv": np.std(omegas) / np.mean(omegas) if np.mean(omegas) > 1e-12 else 0
    }
    print(f"  {label}: omega={np.mean(omegas):.4f} +/- {np.std(omegas):.4f} "
          f"(CV={omega_variations[label]['cv']:.3f})")

# ── 9. Generate Outputs ─────────────────────────────────────
print("\n" + "=" * 60)
print("9. Generating outputs...")
print("=" * 60)

# 9a. Tissue omega heatmap
fig, ax = plt.subplots(figsize=(8, 6))
mask = np.isnan(omega_matrix)
sns.heatmap(omega_matrix, annot=True, fmt=".3f", cmap="RdYlBu_r",
            xticklabels=tissues, yticklabels=tissues,
            center=1.0, mask=mask,
            cbar_kws={"label": "omega"},
            ax=ax)
ax.set_title("CKI omega: Tissue-level comparisons\n(Tabula Muris FACS)", fontsize=12)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "omega_heatmap_tissue.png", dpi=150)
plt.close()
print("  Saved: omega_heatmap_tissue.png")

# 9b. k_n and k_f side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
sns.heatmap(kn_matrix, annot=True, fmt=".4f", cmap="Blues",
            xticklabels=tissues, yticklabels=tissues,
            ax=ax1)
ax1.set_title("k_n (Neutral Offset Rate)")
sns.heatmap(kf_matrix, annot=True, fmt=".4f", cmap="Oranges",
            xticklabels=tissues, yticklabels=tissues,
            ax=ax2)
ax2.set_title("k_f (Functional Conversion Rate)")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "kn_kf_heatmaps.png", dpi=150)
plt.close()
print("  Saved: kn_kf_heatmaps.png")

# 9c. Results bar chart
fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#059669" if r["expected"] == "conserved" else
          "#D4AF37" if r["expected"] == "moderate" else
          "#1E3A5F" for _, r in results_df.iterrows()]
bars = ax.bar(range(len(results_df)), results_df["omega"], color=colors, edgecolor="white")
ax.set_xticks(range(len(results_df)))
ax.set_xticklabels(results_df["comparison"], rotation=15, ha="right", fontsize=9)
ax.set_ylabel("omega = k_f / k_n")
ax.set_title("CKI Pilot Validation: Key Comparisons", fontsize=12)
ax.axhline(y=1.0, color="gray", linestyle="--", linewidth=1, alpha=0.7)

# Add p-value annotations
for i, (_, row) in enumerate(results_df.iterrows()):
    sig = "***" if row["p_value"] < 0.001 else "**" if row["p_value"] < 0.01 else "*" if row["p_value"] < 0.05 else "ns"
    ax.text(i, row["omega"] + 0.05, f"p={row['p_value']:.3f} {sig}",
            ha="center", fontsize=8)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "key_comparisons.png", dpi=150)
plt.close()
print("  Saved: key_comparisons.png")

# 9d. Null distributions for key comparisons
n_comps = len(results_df)
n_cols = min(3, n_comps)
n_rows = (n_comps + n_cols - 1) // n_cols
fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
if n_comps == 1:
    axes = [axes]
axes = np.atleast_1d(axes).flatten()

for i, (_, row) in enumerate(results_df.iterrows()):
    ax = axes[i]
    ax.hist(row.get("null_distribution", []), bins=30, alpha=0.7, color="#1E3A5F")
    ax.axvline(x=row["omega"], color="#D4AF37", linewidth=2,
               label=f"obs omega={row['omega']:.3f}")
    ax.axvline(x=1.0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(f"{row['comparison']}\np={row['p_value']:.4f}, d={row['cohens_d']:.2f}")
    ax.set_xlabel("omega")
    ax.legend(fontsize=7)

for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "null_distributions.png", dpi=150)
plt.close()
print("  Saved: null_distributions.png")

# ── 10. Save Results Table ──────────────────────────────────
results_csv = results_df.drop(columns=["null_distribution"], errors="ignore")
results_csv.to_csv(RESULTS_DIR / "pilot_results.csv", index=False)
print("  Saved: pilot_results.csv")

# Tissue omega matrix
omega_df = pd.DataFrame(omega_matrix, index=tissues, columns=tissues)
omega_df.to_csv(RESULTS_DIR / "omega_matrix_tissue.csv")
print("  Saved: omega_matrix_tissue.csv")

print("\n" + "=" * 60)
print("DONE. All results saved to:", str(RESULTS_DIR))
print("=" * 60)
