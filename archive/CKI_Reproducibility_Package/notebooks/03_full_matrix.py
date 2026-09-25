"""
CKI Phase 3.1: Full Matrix Pairwise CT Comparisons
====================================================
Build 32x32 omega matrix for all viable (tissue, cell_type) pairs.
No bootstrap — direct omega computation for scalability.
Hierarchical clustering to validate omega recovers CT lineages.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from scipy.spatial.distance import squareform

# CJK font setup
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
else:
    plt.rcParams["font.family"] = "sans-serif"

from cki.core import compute_omega

# -- Config --
# DATA_DIR, FACS_DIR, HK_FILE, RESULTS_DIR from _paths
ANNOT_FILE = FACS_ANNOTATIONS  # from _paths
TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10

def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

# -- 1. Load Data --
print("="*60)
print("1. Loading data...")
print("="*60)

hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  HK genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)
print(f"  Annotations: {len(annot)} cells")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists(): continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# -- 2. Unified AnnData --
print("\n" + "="*60)
print("2. Building unified AnnData...")
print("="*60)

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
    obs_tissue = obs_tissue.merge(tissue_annot[["cell","cell_ontology_class","mouse.id"]], on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

# -- 3. Preprocessing --
print("\n" + "="*60)
print("3. Preprocessing...")
print("="*60)

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} x {adata.n_vars}")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
print(f"  HVGs: {adata.var['highly_variable'].sum()}")

# -- 4. Gene Indices --
gene_names = adata.var_names.tolist()
hk_indices = [i for i,g in enumerate(gene_names) if g in hk_mouse_genes]
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()
print(f"  HK: {len(hk_indices)}, Identity: {len(identity_indices)}")

# -- 5. Build CT pseudobulk dict --
print("\n" + "="*60)
print("5. Building CT pseudobulk (largest mouse group)...")
print("="*60)

ct_entries = []  # list of {key, tissue, ct, pb, n_cells}
for tissue in TARGET_TISSUES:
    tdata = adata[adata.obs["tissue"] == tissue]
    for ct in tdata.obs["cell_ontology_class"].unique():
        if ct.lower() == "unknown": continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2: continue
        mouse_counts = ct_data.obs["mouse.id"].value_counts()
        mice_ok = [(m,n) for m,n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) < 1: continue
        mice_ok.sort(key=lambda x: -x[1])
        largest_mouse = mice_ok[0][0]
        mask_largest = ct_data.obs["mouse.id"] == largest_mouse
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, "toarray"): X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT: continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({
            "key": f"{tissue}|{ct}",
            "tissue": tissue,
            "ct": ct,
            "pb": pb,
            "n_cells": X_large.shape[0],
        })

print(f"  Viable CT entries: {len(ct_entries)}")
for e in ct_entries:
    print(f"    {e['key']} (n={e['n_cells']})")

# -- 6. Compute all pairwise omega --
print("\n" + "="*60)
print("6. Computing all pairwise omega...")
print("="*60)

n_ct = len(ct_entries)
omega_matrix = np.zeros((n_ct, n_ct))
kn_matrix = np.zeros((n_ct, n_ct))
kf_matrix = np.zeros((n_ct, n_ct))
dhk_matrix = np.zeros((n_ct, n_ct))
did_matrix = np.zeros((n_ct, n_ct))

from tqdm import tqdm
total_pairs = n_ct * (n_ct - 1) // 2
print(f"  Total pairs: {total_pairs}")

pair_count = 0
for i in tqdm(range(n_ct), desc="Rows"):
    for j in range(i+1, n_ct):
        result = compute_omega(ct_entries[i]["pb"], ct_entries[j]["pb"],
                               hk_indices, identity_indices)
        omega_matrix[i,j] = result["omega"]
        omega_matrix[j,i] = result["omega"]
        kn_matrix[i,j] = result["kn"]
        kn_matrix[j,i] = result["kn"]
        kf_matrix[i,j] = result["kf"]
        kf_matrix[j,i] = result["kf"]
        dhk_matrix[i,j] = result["delta_hk"]
        dhk_matrix[j,i] = result["delta_hk"]
        did_matrix[i,j] = result["delta_identity"]
        did_matrix[j,i] = result["delta_identity"]
        pair_count += 1

# Diagonal: zero (self-comparison)
np.fill_diagonal(omega_matrix, 0)
np.fill_diagonal(kn_matrix, 0)
np.fill_diagonal(kf_matrix, 0)

print(f"\n  Computed {pair_count} pairs")

# -- 7. Build labels --
labels = []
for e in ct_entries:
    ct_short = e["ct"].replace("endothelial cell of hepatic sinusoid", "liver sinusoid EC")
    ct_short = ct_short.replace("cardiac muscle cell", "cardiac muscle")
    ct_short = ct_short.replace("natural killer cell", "NK cell")
    if len(ct_short) > 18:
        ct_short = ct_short[:16] + ".."
    labels.append(f"{e['tissue'][:4]}|{ct_short}")

# -- 8. Save matrices --
print("\n" + "="*60)
print("8. Saving matrices...")
print("="*60)

omega_df = pd.DataFrame(omega_matrix, index=labels, columns=labels)
omega_df.to_csv(RESULTS_DIR / "full_matrix_omega.csv")
print("  Saved: full_matrix_omega.csv")

kn_df = pd.DataFrame(kn_matrix, index=labels, columns=labels)
kn_df.to_csv(RESULTS_DIR / "full_matrix_kn.csv")
print("  Saved: full_matrix_kn.csv")

kf_df = pd.DataFrame(kf_matrix, index=labels, columns=labels)
kf_df.to_csv(RESULTS_DIR / "full_matrix_kf.csv")
print("  Saved: full_matrix_kf.csv")

# -- 9. Summary statistics --
print("\n" + "="*60)
print("9. Summary Statistics")
print("="*60)

upper_tri = omega_matrix[np.triu_indices(n_ct, k=1)]
print(f"  Omega range: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]")
print(f"  Omega mean: {np.mean(upper_tri):.2f}")
print(f"  Omega median: {np.median(upper_tri):.2f}")
print(f"  Omega std: {np.std(upper_tri):.2f}")

# By category: same tissue, same CT (broad class)
same_tissue_mask = np.zeros((n_ct,n_ct), dtype=bool)
same_ct_class = np.zeros((n_ct,n_ct), dtype=bool)
for i in range(n_ct):
    for j in range(n_ct):
        if i >= j: continue
        same_tissue_mask[i,j] = ct_entries[i]["tissue"] == ct_entries[j]["tissue"]
        same_ct_class[i,j] = ct_entries[i]["ct"] == ct_entries[j]["ct"]

same_tissue = upper_tri[same_tissue_mask[np.triu_indices(n_ct,k=1)]]
diff_tissue = upper_tri[~same_tissue_mask[np.triu_indices(n_ct,k=1)]]
same_ct = upper_tri[same_ct_class[np.triu_indices(n_ct,k=1)]]
diff_ct = upper_tri[~same_ct_class[np.triu_indices(n_ct,k=1)]]

print(f"\n  Same tissue (n={len(same_tissue)}): mean={np.mean(same_tissue):.2f}, median={np.median(same_tissue):.2f}")
print(f"  Diff tissue (n={len(diff_tissue)}): mean={np.mean(diff_tissue):.2f}, median={np.median(diff_tissue):.2f}")
print(f"  Same CT class (n={len(same_ct)}): mean={np.mean(same_ct):.2f}, median={np.median(same_ct):.2f}")
print(f"  Diff CT class (n={len(diff_ct)}): mean={np.mean(diff_ct):.2f}, median={np.median(diff_ct):.2f}")

# -- 10. Heatmap with clustering --
print("\n" + "="*60)
print("10. Generating heatmap...")
print("="*60)

# Hierarchical clustering
condensed_dist = squareform(upper_tri, checks=False)
# Use 1/omega or omega for distance? Higher omega = more different, so use omega as distance
linkage_matrix = linkage(condensed_dist, method="ward")
leaf_order = leaves_list(linkage_matrix)

# Reorder matrix
omega_clustered = omega_matrix[leaf_order][:, leaf_order]
labels_clustered = [labels[i] for i in leaf_order]

fig, ax = plt.subplots(figsize=(18, 15))
im = ax.imshow(omega_clustered, cmap="RdYlBu_r", aspect="equal", vmin=0, vmax=max(30, np.max(upper_tri)*1.1))

ax.set_xticks(range(n_ct))
ax.set_yticks(range(n_ct))
ax.set_xticklabels(labels_clustered, rotation=90, ha="center", fontsize=6)
ax.set_yticklabels(labels_clustered, fontsize=6)
ax.set_title("CKI Phase 3.1: Full Matrix Pairwise Omega (32 CT Pairs)", fontsize=14, fontweight="bold", pad=20)

cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("omega", fontsize=11)

# Annotate with omega values (small font)
for i in range(n_ct):
    for j in range(n_ct):
        val = omega_clustered[i,j]
        if val > 0:
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=4,
                    color="white" if val > np.percentile(upper_tri, 70) else "black")

plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: full_matrix_heatmap.png")

# -- 11. Dendrogram only --
fig, ax = plt.subplots(figsize=(20, 5))
dn = dendrogram(linkage_matrix, labels=labels, ax=ax, leaf_font_size=7,
                color_threshold=np.percentile(linkage_matrix[:,2], 60))
ax.set_title("CKI omega-based Hierarchical Clustering of Cell Types", fontsize=13, fontweight="bold")
ax.set_ylabel("Omega distance (Ward linkage)", fontsize=10)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_dendrogram.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: full_matrix_dendrogram.png")

# -- 12. Top/bottom pairs --
print("\n" + "="*60)
print("12. Top 15 Most Differentiated Pairs")
print("="*60)

pairs_list = []
for i in range(n_ct):
    for j in range(i+1, n_ct):
        pairs_list.append({
            "pair": f"{labels[i]} vs {labels[j]}",
            "omega": omega_matrix[i,j],
            "kn": kn_matrix[i,j],
            "kf": kf_matrix[i,j],
            "same_tissue": ct_entries[i]["tissue"] == ct_entries[j]["tissue"],
            "same_ct": ct_entries[i]["ct"] == ct_entries[j]["ct"],
        })

pairs_df = pd.DataFrame(pairs_list)
pairs_df = pairs_df.sort_values("omega", ascending=False)

print("\n  Top 15 (highest omega = most differentiated):")
for _, row in pairs_df.head(15).iterrows():
    st = " (same tissue)" if row["same_tissue"] else ""
    sct = " (same CT)" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}, kn={row['kn']:.5f}, kf={row['kf']:.5f}{st}{sct}")

print("\n  Bottom 15 (lowest omega = most similar):")
for _, row in pairs_df.tail(15).iterrows():
    st = " (same tissue)" if row["same_tissue"] else ""
    sct = " (same CT)" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}, kn={row['kn']:.5f}, kf={row['kf']:.5f}{st}{sct}")

pairs_df.to_csv(RESULTS_DIR / "full_matrix_pairs.csv", index=False)
print("  Saved: full_matrix_pairs.csv")

# -- 13. Category boxplot --
print("\n" + "="*60)
print("13. Generating category boxplot...")
print("="*60)

# Define four categories based on same/different tissue and CT
cat_data = {"same_tissue+same_ct": [], "same_tissue+diff_ct": [],
            "diff_tissue+same_ct": [], "diff_tissue+diff_ct": []}

for _, row in pairs_df.iterrows():
    if row["same_tissue"] and row["same_ct"]:
        cat_data["same_tissue+same_ct"].append(row["omega"])
    elif row["same_tissue"] and not row["same_ct"]:
        cat_data["same_tissue+diff_ct"].append(row["omega"])
    elif not row["same_tissue"] and row["same_ct"]:
        cat_data["diff_tissue+same_ct"].append(row["omega"])
    else:
        cat_data["diff_tissue+diff_ct"].append(row["omega"])

cat_names = ["SameTissue\nSameCT", "SameTissue\nDiffCT", "DiffTissue\nSameCT", "DiffTissue\nDiffCT"]
cat_colors = ["#059669", "#E67E22", "#D4AF37", "#C0392B"]
cat_data_values = [np.array(cat_data["same_tissue+same_ct"]),
                   np.array(cat_data["same_tissue+diff_ct"]),
                   np.array(cat_data["diff_tissue+same_ct"]),
                   np.array(cat_data["diff_tissue+diff_ct"])]

fig, ax = plt.subplots(figsize=(8, 5))
bp = ax.boxplot(cat_data_values, labels=cat_names, patch_artist=True, widths=0.5)
for i in range(4):
    bp["boxes"][i].set_facecolor(cat_colors[i])
    jitter = np.random.RandomState(RANDOM_SEED).normal(0, 0.03, len(cat_data_values[i]))
    ax.scatter(np.ones(len(cat_data_values[i]))*(i+1) + jitter, cat_data_values[i],
               color="#1E3A5F", s=15, alpha=0.4, zorder=3)

ax.set_ylabel("omega", fontsize=12)
ax.set_title(f"Full Matrix: omega by Tissue/CT Category\n(n_total={len(pairs_df)})", fontsize=13, fontweight="bold")
for i, vals in enumerate(cat_data_values):
    if len(vals) > 0:
        ax.annotate(f"n={len(vals)}\nmean={np.mean(vals):.1f}", (i+1, np.max(vals)*1.02),
                    ha="center", fontsize=7, color="#333")

plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_category_boxplot.png", dpi=150)
plt.close()
print("  Saved: full_matrix_category_boxplot.png")

print("\n" + "="*60)
print("DONE. Phase 3.1 complete.")
print("="*60)
