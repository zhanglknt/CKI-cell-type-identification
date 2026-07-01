"""
CKI Phase 3.3 v3: Hybrid Omega (fixed k_n + per-pair k_f) — Memory-optimized
=============================================================================
- k_n: GLOBAL HK genes (stable, comparable to v1 and mouse)
- k_f: per-pair top-N DE genes (exclude HK, select by |diff|)
- Memory fix: process organs one at a time, only keep pseudobulks in memory
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
from pathlib import Path
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from scipy.spatial.distance import squareform
from sklearn.metrics import roc_auc_score
from cki.core import compute_omega, js_divergence

# === Config ===
TS_HUMAN_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TS_ORGANS = ["Liver", "Kidney", "Heart", "Bone_Marrow", "Spleen", "Lung"]
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200  # per-pair top DE genes for k_f

# === 1. Compute common genes across all organs (load gene lists only) ===
print("="*60)
print("1. Computing common genes across all organs...")
print("="*60)

all_var_names = []
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        # Read var names only using h5py (no AnnData load)
        import h5py
        with h5py.File(fname, 'r') as f:
            var_names = [x.decode('utf-8') if isinstance(x, bytes) else x 
                        for x in f['var']['_index'][:]]
        all_var_names.append(set(var_names))
        print(f"  {organ}: {len(all_var_names[-1])} genes")

common_genes = sorted(all_var_names[0].intersection(*all_var_names[1:]))
common_genes_set = set(common_genes)
print(f"\n  Common genes: {len(common_genes)}")

# === 2. Load HK genes ===
print("\n" + "="*60)
print("2. Loading human housekeeping genes (GLOBAL)...")
print("="*60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
# HK genes that are in common gene set
hk_global_genes = sorted(hk_human_genes & common_genes_set)
hk_global_idx_map = {g: i for i, g in enumerate(common_genes)}
hk_global_idx = np.array([hk_global_idx_map[g] for g in hk_global_genes])
print(f"  Global HK genes in common set: {len(hk_global_idx)}")

# === 3. Build CT pseudobulks — one organ at a time ===
print("\n" + "="*60)
print("3. Building CT pseudobulks (per organ, memory-optimized)...")
print("="*60)

ct_entries = []
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if not fname.exists():
        print(f"  SKIP {organ}: file not found")
        continue

    print(f"  Loading {organ}...")
    adata = sc.read_h5ad(fname)

    # Subset to common genes
    gene_mask = np.array([g in common_genes_set for g in adata.var_names])
    adata = adata[:, gene_mask].copy()

    # Ensure genes are in the same order as common_genes
    var_to_idx = {g: i for i, g in enumerate(common_genes)}

    # Preprocess (on common genes only)
    sc.pp.filter_cells(adata, min_genes=500)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Find positions of common genes in this organ's var_names
    var_to_common_idx = {}
    for idx, g in enumerate(adata.var_names):
        if g in common_genes_set:
            var_to_common_idx[idx] = common_genes.index(g)

    ct_labels = adata.obs["cell_ontology_class"].value_counts()
    for ct, count in ct_labels.items():
        if ct.lower() == "unknown":
            continue
        ct_mask = adata.obs["cell_ontology_class"] == ct
        ct_data = adata[ct_mask]

        # Determine donor
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

        # Map expression to common gene order
        pb_common = np.zeros(len(common_genes))
        for local_idx, common_idx in var_to_common_idx.items():
            pb_common[common_idx] = np.mean(X_large[:, local_idx])

        ct_entries.append({
            "key": f"{organ}|{ct}",
            "organ": organ,
            "ct": ct,
            "pb": pb_common,
            "n_cells": X_large.shape[0],
            "donor": largest_donor,
        })
        print(f"    {organ}|{ct}: {X_large.shape[0]} cells")

    # Free memory
    del adata
    import gc
    gc.collect()

n_ct = len(ct_entries)
print(f"\n  Total viable CT entries: {n_ct}")

# === 4. Compute omega: global k_n + per-pair k_f ===
print("\n" + "="*60)
print(f"4. Computing omega (global k_n, per-pair k_f top-{N_TOP_KF})...")
print("="*60)

omega_matrix = np.zeros((n_ct, n_ct))
kn_matrix = np.zeros((n_ct, n_ct))
kf_matrix = np.zeros((n_ct, n_ct))
total_pairs = n_ct * (n_ct - 1) // 2
print(f"  Total pairs: {total_pairs}")

for i in range(n_ct):
    for j in range(i+1, n_ct):
        pb_i = ct_entries[i]["pb"]
        pb_j = ct_entries[j]["pb"]

        # --- k_n: GLOBAL HK (stable) ---
        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = js_divergence(hk_i, hk_j)

        # --- k_f: per-pair top-N DE genes (exclude HK) ---
        abs_diff = np.abs(pb_i - pb_j)
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1  # exclude HK

        top_n = min(N_TOP_KF, len(abs_diff_non_hk) - len(hk_global_idx))
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        top_idx = top_idx[np.argsort(abs_diff_non_hk[top_idx])[::-1]]

        kf_val = js_divergence(pb_i[top_idx], pb_j[top_idx])

        # omega
        omega_val = kf_val / kn_val if kn_val > 0 else float('inf')

        omega_matrix[i,j] = omega_val
        omega_matrix[j,i] = omega_val
        kn_matrix[i,j] = kn_val
        kn_matrix[j,i] = kn_val
        kf_matrix[i,j] = kf_val
        kf_matrix[j,i] = kf_val

    if (i+1) % 10 == 0:
        print(f"  Progress: row {i+1}/{n_ct}")

np.fill_diagonal(omega_matrix, 0)
np.fill_diagonal(kn_matrix, 0)
np.fill_diagonal(kf_matrix, 0)
print(f"  Complete: {total_pairs} pairs")

# === 5. Labels and category analysis ===
print("\n" + "="*60)
print("5. Building labels and category analysis...")
print("="*60)

labels = []
for e in ct_entries:
    ct_short = e["ct"]
    replacements = {
        "endothelial cell of hepatic sinusoid": "livEC",
        "cardiac muscle cell": "cardio",
        "natural killer cell": "NK",
        "type II pneumocyte": "pneumoII",
        "type I pneumocyte": "pneumoI",
        "endothelial cell": "EC",
        "epithelial cell": "epi",
    }
    for old, new in replacements.items():
        ct_short = ct_short.replace(old, new)
    if len(ct_short) > 16:
        ct_short = ct_short[:14] + ".."
    labels.append(f"{e['organ'][:4]}|{ct_short}")

same_organ_mask = np.zeros((n_ct, n_ct), dtype=bool)
same_ct_mask = np.zeros((n_ct, n_ct), dtype=bool)
for i in range(n_ct):
    for j in range(n_ct):
        if i >= j: continue
        same_organ_mask[i,j] = ct_entries[i]["organ"] == ct_entries[j]["organ"]
        same_ct_mask[i,j] = ct_entries[i]["ct"] == ct_entries[j]["ct"]

si, sj = np.triu_indices(n_ct, k=1)
upper_tri = omega_matrix[si, sj]
upper_kf = kf_matrix[si, sj]
upper_kn = kn_matrix[si, sj]

same_organ_vals = upper_tri[same_organ_mask[si, sj]]
diff_organ_vals = upper_tri[~same_organ_mask[si, sj]]
same_ct_vals = upper_tri[same_ct_mask[si, sj]]
diff_ct_vals = upper_tri[~same_ct_mask[si, sj]]

print(f"  Same organ (n={len(same_organ_vals)}): mean={np.mean(same_organ_vals):.2f} median={np.median(same_organ_vals):.2f}")
print(f"  Diff organ (n={len(diff_organ_vals)}): mean={np.mean(diff_organ_vals):.2f} median={np.median(diff_organ_vals):.2f}")
print(f"  Same CT (n={len(same_ct_vals)}): mean={np.mean(same_ct_vals):.2f} median={np.median(same_ct_vals):.2f}")
print(f"  Diff CT (n={len(diff_ct_vals)}): mean={np.mean(diff_ct_vals):.2f} median={np.median(diff_ct_vals):.2f}")

# Compute cross-organ same-CT pairs (S category)
same_ct_diff_organ_vals = upper_tri[same_ct_mask[si, sj] & ~same_organ_mask[si, sj]]
same_ct_same_organ_vals = upper_tri[same_ct_mask[si, sj] & same_organ_mask[si, sj]]
print(f"  Same-CT Cross-organ (n={len(same_ct_diff_organ_vals)}): mean={np.mean(same_ct_diff_organ_vals):.2f}")
print(f"  Same-CT Same-organ (n={len(same_ct_same_organ_vals)}): mean={np.mean(same_ct_same_organ_vals):.2f}")

# Diff-CT Same-organ pairs (D category)
diff_ct_same_organ_vals = upper_tri[~same_ct_mask[si, sj] & same_organ_mask[si, sj]]
print(f"  Diff-CT Same-organ (n={len(diff_ct_same_organ_vals)}): mean={np.mean(diff_ct_same_organ_vals):.2f}")

# AUC for same-CT classification
y_true_ct = []
y_score_ct = []
for i in range(n_ct):
    for j in range(i+1, n_ct):
        y_true_ct.append(1 if ct_entries[i]["ct"] == ct_entries[j]["ct"] else 0)
        y_score_ct.append(omega_matrix[i,j])
auc_ct = roc_auc_score(y_true_ct, [-s for s in y_score_ct])
print(f"  AUC (same CT vs diff CT): {auc_ct:.3f}")

# Overall omega stats
print(f"\n  Overall omega: min={upper_tri.min():.2f}, max={upper_tri.max():.2f}, "
      f"mean={np.mean(upper_tri):.2f}, median={np.median(upper_tri):.2f}")

# === 6. Save matrices ===
print("\n" + "="*60)
print("6. Saving matrices...")
print("="*60)

omega_df = pd.DataFrame(omega_matrix, index=labels, columns=labels)
omega_df.to_csv(RESULTS_DIR / "phase33_v3_human_omega.csv")
print("  Saved: phase33_v3_human_omega.csv")

kn_df = pd.DataFrame(kn_matrix, index=labels, columns=labels)
kn_df.to_csv(RESULTS_DIR / "phase33_v3_human_kn.csv")
print("  Saved: phase33_v3_human_kn.csv")

kf_df = pd.DataFrame(kf_matrix, index=labels, columns=labels)
kf_df.to_csv(RESULTS_DIR / "phase33_v3_human_kf.csv")
print("  Saved: phase33_v3_human_kf.csv")

pairs_list = []
for i in range(n_ct):
    for j in range(i+1, n_ct):
        pairs_list.append({
            "pair": f"{labels[i]} vs {labels[j]}",
            "omega": omega_matrix[i,j],
            "kn": kn_matrix[i,j],
            "kf": kf_matrix[i,j],
            "same_organ": ct_entries[i]["organ"] == ct_entries[j]["organ"],
            "same_ct": ct_entries[i]["ct"] == ct_entries[j]["ct"],
        })
pairs_df = pd.DataFrame(pairs_list).sort_values("omega", ascending=False)
pairs_df.to_csv(RESULTS_DIR / "phase33_v3_human_pairs.csv", index=False)
print("  Saved: phase33_v3_human_pairs.csv")

# === 7. Heatmap ===
print("\n" + "="*60)
print("7. Generating heatmap...")
print("="*60)

condensed_dist = squareform(upper_tri, checks=False)
linkage_matrix = linkage(condensed_dist, method="ward")
leaf_order = leaves_list(linkage_matrix)

omega_clustered = omega_matrix[leaf_order][:, leaf_order]
labels_clustered = [labels[i] for i in leaf_order]

fig, ax = plt.subplots(figsize=(max(18, n_ct*0.55), max(16, n_ct*0.48)))
vmax_val = max(30, np.percentile(upper_tri, 95) * 1.2)
im = ax.imshow(omega_clustered, cmap="RdYlBu_r", aspect="equal",
               vmin=0, vmax=vmax_val)
ax.set_xticks(range(n_ct))
ax.set_yticks(range(n_ct))
ax.set_xticklabels(labels_clustered, rotation=90, ha="center", fontsize=6)
ax.set_yticklabels(labels_clustered, fontsize=6)
ax.set_title(f"CKI Phase 3.3 v3: TS Human Omega (hybrid, {n_ct} CTs)",
             fontsize=14, fontweight="bold", pad=20)
cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("omega", fontsize=11)

fig.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_v3_human_heatmap.png", dpi=150, bbox_inches="tight")
print("  Saved: phase33_v3_human_heatmap.png")
plt.close()

# === 8. Report ===
print("\n" + "="*60)
print("8. Generating report...")
print("="*60)

report = []
report.append("# CKI Phase 3.3 v3: Hybrid Omega — Results Report\n")
report.append(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
report.append(f"Total cell-type entries: {n_ct}\n")
report.append(f"Total pairs: {total_pairs}\n\n")

report.append("## Omega Distribution\n")
report.append(f"- Min: {upper_tri.min():.2f}\n")
report.append(f"- Max: {upper_tri.max():.2f}\n")
report.append(f"- Mean: {np.mean(upper_tri):.2f}\n")
report.append(f"- Median: {np.median(upper_tri):.2f}\n")
report.append(f"- Std: {np.std(upper_tri):.2f}\n\n")

report.append("## Category Analysis\n")
report.append(f"- Same-CT Cross-organ (n={len(same_ct_diff_organ_vals)}): mean={np.mean(same_ct_diff_organ_vals):.2f}, median={np.median(same_ct_diff_organ_vals):.2f}\n")
report.append(f"- Diff-CT Same-organ (n={len(diff_ct_same_organ_vals)}): mean={np.mean(diff_ct_same_organ_vals):.2f}, median={np.median(diff_ct_same_organ_vals):.2f}\n")
report.append(f"- Same-CT Same-organ (n={len(same_ct_same_organ_vals)}): mean={np.mean(same_ct_same_organ_vals):.2f}, median={np.median(same_ct_same_organ_vals):.2f}\n")
report.append(f"- Same-organ (n={len(same_organ_vals)}): mean={np.mean(same_organ_vals):.2f}\n")
report.append(f"- Diff-organ (n={len(diff_organ_vals)}): mean={np.mean(diff_organ_vals):.2f}\n")
report.append(f"- AUC (same-CT): {auc_ct:.3f}\n")

with open(RESULTS_DIR / "phase33_v3_report.md", "w") as f:
    f.writelines(report)
print("  Saved: phase33_v3_report.md")

print("\n" + "="*60)
print("Phase 3.3 v3 complete!")
print("="*60)
