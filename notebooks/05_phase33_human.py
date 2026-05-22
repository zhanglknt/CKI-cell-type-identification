"""
CKI Phase 3.3: Tabula Sapiens Human Cross-Validation
=====================================================
Load 6 TS human h5ad files, build unified AnnData, compute pairwise omega.
Compare with Phase 3.2 mouse results for cross-species validation.
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
from scipy.stats import mannwhitneyu

# CJK font setup
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
else:
    plt.rcParams["font.family"] = "sans-serif"

from cki.core import compute_omega

# -- Config --
TS_HUMAN_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TS_ORGANS = ["Liver", "Kidney", "Heart", "Bone_Marrow", "Spleen", "Lung"]
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10

# ================================================================
# 1. Load all 6 TS h5ad -> unified AnnData
# ================================================================
print("="*60)
print("1. Loading TS human h5ad files...")
print("="*60)

adatas_raw = {}
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        adata = sc.read_h5ad(fname)
        adata.obs["organ"] = organ
        adatas_raw[organ] = adata
        n_ct = adata.obs["cell_ontology_class"].nunique()
        print(f"  TS_{organ}: {adata.n_obs} cells, {n_ct} cell types")

# Find common genes across all organs
all_gene_sets = [set(adata.var_names) for adata in adatas_raw.values()]
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))
print(f"\n  Common genes across all 6 organs: {len(common_genes)}")

# Build unified AnnData
adata_list = []
obs_list = []
for organ, adata in adatas_raw.items():
    # Subset to common genes
    adata_sub = adata[:, common_genes].copy()
    adata_sub.obs["organ"] = organ
    adata_list.append(adata_sub)
    obs_list.append(adata_sub.obs)

adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

# ================================================================
# 2. Preprocessing
# ================================================================
print("\n" + "="*60)
print("2. Preprocessing...")
print("="*60)

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
print(f"  HVGs: {adata.var['highly_variable'].sum()}")

# ================================================================
# 3. Load Human HK genes
# ================================================================
print("\n" + "="*60)
print("3. Loading human housekeeping genes...")
print("="*60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
print(f"  Human HK genes (raw): {len(hk_human_genes)}")

# Intersect with gene space
gene_names = adata.var_names.tolist()
hk_indices = [i for i, g in enumerate(gene_names) if g in hk_human_genes]
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()
print(f"  HK genes in data: {len(hk_indices)}")
print(f"  Identity (HVG) genes: {len(identity_indices)}")

# ================================================================
# 4. Build CT pseudobulks (largest donor group)
# ================================================================
print("\n" + "="*60)
print("4. Building CT pseudobulks (largest donor)...")
print("="*60)

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
        # Select largest donor
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
        ct_entries.append({
            "key": f"{organ}|{ct}",
            "organ": organ,
            "ct": ct,
            "pb": pb,
            "n_cells": X_large.shape[0],
            "donor": largest_donor,
        })

print(f"  Viable CT entries: {len(ct_entries)}")
for e in ct_entries:
    print(f"    {e['key']} (donor={e['donor']}, n={e['n_cells']})")

# ================================================================
# 5. Compute all pairwise omega
# ================================================================
print("\n" + "="*60)
print("5. Computing all pairwise omega...")
print("="*60)

n_ct = len(ct_entries)
omega_matrix = np.zeros((n_ct, n_ct))
kn_matrix = np.zeros((n_ct, n_ct))
kf_matrix = np.zeros((n_ct, n_ct))

from tqdm import tqdm
total_pairs = n_ct * (n_ct - 1) // 2
print(f"  Total pairs: {total_pairs}")

for i in tqdm(range(n_ct), desc="Rows"):
    for j in range(i+1, n_ct):
        result = compute_omega(
            ct_entries[i]["pb"], ct_entries[j]["pb"],
            hk_indices, identity_indices,
            w1=1.0, w2=0.0  # identity_only (best from Phase 3.2)
        )
        omega_matrix[i,j] = result["omega"]
        omega_matrix[j,i] = result["omega"]
        kn_matrix[i,j] = result["kn"]
        kn_matrix[j,i] = result["kn"]
        kf_matrix[i,j] = result["kf"]
        kf_matrix[j,i] = result["kf"]

np.fill_diagonal(omega_matrix, 0)
np.fill_diagonal(kn_matrix, 0)
np.fill_diagonal(kf_matrix, 0)

# ================================================================
# 6. Build labels
# ================================================================
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

# ================================================================
# 7. Category analysis
# ================================================================
print("\n" + "="*60)
print("7. Category Analysis")
print("="*60)

same_organ_mask = np.zeros((n_ct, n_ct), dtype=bool)
same_ct_mask = np.zeros((n_ct, n_ct), dtype=bool)
for i in range(n_ct):
    for j in range(n_ct):
        if i >= j: continue
        same_organ_mask[i,j] = ct_entries[i]["organ"] == ct_entries[j]["organ"]
        same_ct_mask[i,j] = ct_entries[i]["ct"] == ct_entries[j]["ct"]

upper_tri = omega_matrix[np.triu_indices(n_ct, k=1)]

same_organ_vals = upper_tri[same_organ_mask[np.triu_indices(n_ct, k=1)]]
diff_organ_vals = upper_tri[~same_organ_mask[np.triu_indices(n_ct, k=1)]]
same_ct_vals = upper_tri[same_ct_mask[np.triu_indices(n_ct, k=1)]]
diff_ct_vals = upper_tri[~same_ct_mask[np.triu_indices(n_ct, k=1)]]

print(f"  Same organ (n={len(same_organ_vals)}): mean={np.mean(same_organ_vals):.2f}, median={np.median(same_organ_vals):.2f}")
print(f"  Diff organ (n={len(diff_organ_vals)}): mean={np.mean(diff_organ_vals):.2f}, median={np.median(diff_organ_vals):.2f}")
print(f"  Same CT (n={len(same_ct_vals)}): mean={np.mean(same_ct_vals):.2f}, median={np.median(same_ct_vals):.2f}")
print(f"  Diff CT (n={len(diff_ct_vals)}): mean={np.mean(diff_ct_vals):.2f}, median={np.median(diff_ct_vals):.2f}")

# AUC for CT discrimination
y_true_ct = []
y_score_ct = []
for i in range(n_ct):
    for j in range(i+1, n_ct):
        y_true_ct.append(1 if ct_entries[i]["ct"] == ct_entries[j]["ct"] else 0)
        y_score_ct.append(omega_matrix[i,j])
auc_ct = roc_auc_score(y_true_ct, [-s for s in y_score_ct])
effect_sep = np.mean(diff_ct_vals) / (np.mean(same_ct_vals) + 1e-9) if len(same_ct_vals) > 0 else 0
print(f"  AUC (same CT vs diff CT): {auc_ct:.3f}")
print(f"  Effect separation: {effect_sep:.2f}")

# ================================================================
# 8. Save matrices
# ================================================================
print("\n" + "="*60)
print("8. Saving matrices...")
print("="*60)

omega_df = pd.DataFrame(omega_matrix, index=labels, columns=labels)
omega_df.to_csv(RESULTS_DIR / "phase33_human_omega.csv")
print("  Saved: phase33_human_omega.csv")

kn_df = pd.DataFrame(kn_matrix, index=labels, columns=labels)
kn_df.to_csv(RESULTS_DIR / "phase33_human_kn.csv")
print("  Saved: phase33_human_kn.csv")

kf_df = pd.DataFrame(kf_matrix, index=labels, columns=labels)
kf_df.to_csv(RESULTS_DIR / "phase33_human_kf.csv")
print("  Saved: phase33_human_kf.csv")

# -- Pairs list --
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
pairs_df.to_csv(RESULTS_DIR / "phase33_human_pairs.csv", index=False)
print("  Saved: phase33_human_pairs.csv")

# ================================================================
# 9. Heatmap with clustering
# ================================================================
print("\n" + "="*60)
print("9. Generating heatmap...")
print("="*60)

condensed_dist = squareform(upper_tri, checks=False)
linkage_matrix = linkage(condensed_dist, method="ward")
leaf_order = leaves_list(linkage_matrix)

omega_clustered = omega_matrix[leaf_order][:, leaf_order]
labels_clustered = [labels[i] for i in leaf_order]

fig, ax = plt.subplots(figsize=(max(16, n_ct*0.55), max(14, n_ct*0.48)))
vmax_val = max(30, np.max(upper_tri) * 1.1)
im = ax.imshow(omega_clustered, cmap="RdYlBu_r", aspect="equal",
               vmin=0, vmax=vmax_val)
ax.set_xticks(range(n_ct))
ax.set_yticks(range(n_ct))
ax.set_xticklabels(labels_clustered, rotation=90, ha="center", fontsize=6)
ax.set_yticklabels(labels_clustered, fontsize=6)
ax.set_title(f"CKI Phase 3.3: TS Human Omega Heatmap ({n_ct} CTs, {total_pairs} pairs)",
             fontsize=14, fontweight="bold", pad=20)
cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("omega", fontsize=11)

for i in range(n_ct):
    for j in range(n_ct):
        val = omega_clustered[i,j]
        if val > 0:
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=4,
                    color="white" if val > np.percentile(upper_tri, 70) else "black")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_human_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase33_human_heatmap.png")

# -- Dendrogram --
fig, ax = plt.subplots(figsize=(max(20, n_ct*0.6), 5))
dn = dendrogram(linkage_matrix, labels=labels, ax=ax, leaf_font_size=7,
                color_threshold=np.percentile(linkage_matrix[:,2], 60))
ax.set_title("CKI Phase 3.3: TS Human Omega Dendrogram", fontsize=13, fontweight="bold")
ax.set_ylabel("Omega distance (Ward linkage)", fontsize=10)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_human_dendrogram.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase33_human_dendrogram.png")

# ================================================================
# 10. Category boxplot
# ================================================================
print("\n" + "="*60)
print("10. Generating category boxplot...")
print("="*60)

cat_names = ["SameOrgan\nSameCT", "SameOrgan\nDiffCT",
             "DiffOrgan\nSameCT", "DiffOrgan\nDiffCT"]
cat_colors = ["#059669", "#E67E22", "#D4AF37", "#C0392B"]

cat_data_viz = {}
for _, row in pairs_df.iterrows():
    if row["same_organ"] and row["same_ct"]:
        key = "sos"
    elif row["same_organ"] and not row["same_ct"]:
        key = "sod"
    elif not row["same_organ"] and row["same_ct"]:
        key = "dos"
    else:
        key = "dod"
    cat_data_viz.setdefault(key, []).append(row["omega"])

cat_vals = [np.array(cat_data_viz.get(k, [])) for k in ["sos", "sod", "dos", "dod"]]

fig, ax = plt.subplots(figsize=(8, 5))
bp = ax.boxplot(cat_vals, labels=cat_names, patch_artist=True, widths=0.5)
for i in range(4):
    bp["boxes"][i].set_facecolor(cat_colors[i])
    if len(cat_vals[i]) > 0:
        jitter = np.random.RandomState(RANDOM_SEED).normal(0, 0.03, len(cat_vals[i]))
        ax.scatter(np.ones(len(cat_vals[i]))*(i+1) + jitter, cat_vals[i],
                   color="#1E3A5F", s=15, alpha=0.4, zorder=3)
        ax.annotate(f"n={len(cat_vals[i])}\nmean={np.mean(cat_vals[i]):.1f}",
                    (i+1, np.max(cat_vals[i])*1.02),
                    ha="center", fontsize=7, color="#333")
ax.set_ylabel("omega", fontsize=12)
ax.set_title(f"CKI Phase 3.3: TS Human Omega by Organ/CT Category (n={len(pairs_df)} pairs)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_human_category_boxplot.png", dpi=150)
plt.close()
print("  Saved: phase33_human_category_boxplot.png")

# ================================================================
# 11. Top/bottom pairs
# ================================================================
print("\n" + "="*60)
print("11. Top/Bottom Pairs")
print("="*60)

print("\n  Top 15 (highest omega = most differentiated):")
for _, row in pairs_df.head(15).iterrows():
    so = " [SO]" if row["same_organ"] else ""
    sc = " [SC]" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}{so}{sc}")

print("\n  Bottom 15 (lowest omega = most similar):")
for _, row in pairs_df.tail(15).iterrows():
    so = " [SO]" if row["same_organ"] else ""
    sc = " [SC]" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}{so}{sc}")

# ================================================================
# 12. Summary statistics
# ================================================================
print("\n" + "="*60)
print("12. Summary Statistics")
print("="*60)

print(f"  CT entries: {n_ct}")
print(f"  Total pairs: {total_pairs}")
print(f"  Omega range: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]")
print(f"  Omega mean: {np.mean(upper_tri):.2f}")
print(f"  Omega median: {np.median(upper_tri):.2f}")
print(f"  Omega std: {np.std(upper_tri):.2f}")
print(f"  AUC (CT discrimination): {auc_ct:.3f}")
print(f"  Effect separation: {effect_sep:.2f}")

# ================================================================
# 13. Cross-species comparison (load mouse Phase 3.2 results)
# ================================================================
print("\n" + "="*60)
print("13. Cross-species comparison (Human vs Mouse Phase 3.2)")
print("="*60)

try:
    mouse_omega = pd.read_csv(RESULTS_DIR / "full_matrix_omega.csv", index_col=0)
    mouse_ut = mouse_omega.values[np.triu_indices(len(mouse_omega), k=1)]
    print(f"\n  Mouse (Phase 3.2): n={len(mouse_ut)} pairs, "
          f"mean={np.mean(mouse_ut):.2f}, median={np.median(mouse_ut):.2f}")
    print(f"  Human (Phase 3.3): n={len(upper_tri)} pairs, "
          f"mean={np.mean(upper_tri):.2f}, median={np.median(upper_tri):.2f}")

    # Histogram comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.hist(mouse_ut, bins=30, color="#1E3A5F", alpha=0.7, edgecolor="white")
    ax1.axvline(np.mean(mouse_ut), color="#D4AF37", linestyle="--", linewidth=2)
    ax1.set_xlabel("omega", fontsize=11)
    ax1.set_ylabel("Count", fontsize=11)
    ax1.set_title(f"Mouse (FACS, Phase 3.2)\nn={len(mouse_ut)}, mean={np.mean(mouse_ut):.2f}",
                  fontsize=12, fontweight="bold")

    ax2.hist(upper_tri, bins=30, color="#059669", alpha=0.7, edgecolor="white")
    ax2.axvline(np.mean(upper_tri), color="#D4AF37", linestyle="--", linewidth=2)
    ax2.set_xlabel("omega", fontsize=11)
    ax2.set_ylabel("Count", fontsize=11)
    ax2.set_title(f"Human (TS, Phase 3.3)\nn={len(upper_tri)}, mean={np.mean(upper_tri):.2f}",
                  fontsize=12, fontweight="bold")

    fig.suptitle("CKI Phase 3.3: Cross-Species Omega Distribution Comparison",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "phase33_cross_species_histogram.png", dpi=150)
    plt.close()
    print("  Saved: phase33_cross_species_histogram.png")

    # Overlay comparison
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(mouse_ut, bins=40, color="#1E3A5F", alpha=0.5, label=f"Mouse (mean={np.mean(mouse_ut):.2f})")
    ax.hist(upper_tri, bins=40, color="#059669", alpha=0.5, label=f"Human (mean={np.mean(upper_tri):.2f})")
    ax.set_xlabel("omega", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("CKI Phase 3.3: Mouse vs Human Omega Distribution Overlay",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=11)
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "phase33_cross_species_overlay.png", dpi=150)
    plt.close()
    print("  Saved: phase33_cross_species_overlay.png")

except Exception as e:
    print(f"  [Cross-species comparison skipped: {e}]")

# ================================================================
# 14. Generate report
# ================================================================
print("\n" + "="*60)
print("14. Writing report...")
print("="*60)

# Per-organ summary
organ_summary = {}
for e in ct_entries:
    org = e["organ"]
    organ_summary.setdefault(org, {"n_ct": 0, "total_cells": 0})
    organ_summary[org]["n_ct"] += 1
    organ_summary[org]["total_cells"] += e["n_cells"]

organ_lines = []
for org in TS_ORGANS:
    if org in organ_summary:
        s = organ_summary[org]
        organ_lines.append(f"| {org} | {s['n_ct']} | {s['total_cells']} |")

report = f"""# CKI Phase 3.3 Report: Tabula Sapiens Human Cross-Validation

## Date: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}

## Method
Same as Phase 3.2 best config: identity_only (w1=1.0, w2=0.0)
- k_f = Delta_identity (JS divergence of HVG expression)
- k_n = Delta_HK (JS divergence of housekeeping gene expression)
- omega = k_f / k_n

## Dataset (Human - Tabula Sapiens)
- 6 organs: Liver, Kidney, Heart, Bone_Marrow, Spleen, Lung
- {adata.n_obs} cells x {adata.n_vars} genes (post-QC)
- {n_ct} CT entries (min {MIN_CELLS_PER_CT} cells per CT)

### Per-organ CT entries
| Organ | CT entries | Cells |
|-------|-----------|-------|
{chr(10).join(organ_lines)}

## Results
- **CT entries**: {n_ct}
- **Total pairs**: {total_pairs}
- **Omega range**: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]
- **Omega mean**: {np.mean(upper_tri):.2f}
- **Omega median**: {np.median(upper_tri):.2f}
- **Omega std**: {np.std(upper_tri):.2f}
- **AUC (CT discrimination)**: {auc_ct:.3f}
- **Effect separation (diff_CT / same_CT)**: {effect_sep:.2f}

### Category breakdown
| Category | n | mean omega | median omega |
|----------|---|------------|--------------|
| SameOrgan SameCT | {len(cat_vals[0])} | {np.mean(cat_vals[0]):.2f} | {np.median(cat_vals[0]):.2f} |
| SameOrgan DiffCT | {len(cat_vals[1])} | {np.mean(cat_vals[1]):.2f} | {np.median(cat_vals[1]):.2f} |
| DiffOrgan SameCT | {len(cat_vals[2])} | {np.mean(cat_vals[2]):.2f} | {np.median(cat_vals[2]):.2f} |
| DiffOrgan DiffCT | {len(cat_vals[3])} | {np.mean(cat_vals[3]):.2f} | {np.median(cat_vals[3]):.2f} |

## Cross-species comparison (Human vs Mouse)
- Mouse (FACS, Phase 3.2): n=703 pairs
- Human (TS, Phase 3.3): n={total_pairs} pairs

## Files Generated
- `phase33_human_omega.csv`
- `phase33_human_kn.csv`
- `phase33_human_kf.csv`
- `phase33_human_pairs.csv`
- `phase33_human_heatmap.png`
- `phase33_human_dendrogram.png`
- `phase33_human_category_boxplot.png`
- `phase33_cross_species_histogram.png`
- `phase33_cross_species_overlay.png`

## Next Steps
- Phase 3.4: TCGA tumor perturbation
- Phase 3.5: Method comparison (SAMap / SATURN / CACIMAR)
"""

report_path = RESULTS_DIR / "phase33_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)
print(f"  Saved: phase33_report.md")

print("\n" + "="*60)
print("DONE. Phase 3.3 complete.")
print("="*60)
