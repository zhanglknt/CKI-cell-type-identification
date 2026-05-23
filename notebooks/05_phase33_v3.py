"""
CKI Phase 3.3 v3: Hybrid Omega (fixed k_n + per-pair k_f)
=======================================================
- k_n: GLOBAL HK genes (stable, comparable to v1 and mouse)
- k_f: per-pair top-N DE genes (exclude HK, select by |diff|)
- This fixes v2's problem: per-pair top-genes accidentally inflated k_n
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

# === 1. Load & preprocess (reuse v1 preprocessing) ===
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
        print(f"  TS_{organ}: {adata.n_obs} cells, {n_ct} CTs")

all_gene_sets = [set(a.var_names) for a in adatas_raw.values()]
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))
print(f"\n  Common genes: {len(common_genes)}")

adata_list = []
for organ, adata in adatas_raw.items():
    adata_sub = adata[:, common_genes].copy()
    adata_sub.obs["organ"] = organ
    adata_list.append(adata_sub)

adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

# Preprocess
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
print(f"  log1p-normalized")

# === 2. Global HK genes ===
print("\n" + "="*60)
print("2. Loading human housekeeping genes (GLOBAL)...")
print("="*60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
gene_names = adata.var_names.tolist()
hk_global_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human_genes])
print(f"  Global HK genes in data: {len(hk_global_idx)}")

# === 3. Build CT pseudobulks ===
print("\n" + "="*60)
print("3. Building CT pseudobulks...")
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

n_ct = len(ct_entries)
print(f"  Viable CT entries: {n_ct}")
for e in ct_entries:
    print(f"    {e['key']} (donor={e['donor']}, n={e['n_cells']})")

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
        # Compute |diff| over ALL genes
        abs_diff = np.abs(pb_i - pb_j)
        # Exclude HK genes from k_f gene selection
        non_hk_mask = np.ones(len(gene_names), dtype=bool)
        non_hk_mask[hk_global_idx] = False
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1  # ensure HK never selected

        top_n = min(N_TOP_KF, non_hk_mask.sum())
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        top_idx = top_idx[np.argsort(abs_diff_non_hk[top_idx])[::-1]]

        # k_f = JS divergence of these top genes
        kf_val = js_divergence(pb_i[top_idx], pb_j[top_idx])

        # omega
        omega_val = kf_val / (kn_val + 1e-9)

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

# === 5. Labels ===
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

# Category masks
same_organ_mask = np.zeros((n_ct, n_ct), dtype=bool)
same_ct_mask = np.zeros((n_ct, n_ct), dtype=bool)
for i in range(n_ct):
    for j in range(n_ct):
        if i >= j: continue
        same_organ_mask[i,j] = ct_entries[i]["organ"] == ct_entries[j]["organ"]
        same_ct_mask[i,j] = ct_entries[i]["ct"] == ct_entries[j]["ct"]

upper_tri = omega_matrix[np.triu_indices(n_ct, k=1)]
upper_kf = kf_matrix[np.triu_indices(n_ct, k=1)]
upper_kn = kn_matrix[np.triu_indices(n_ct, k=1)]

same_organ_vals = upper_tri[same_organ_mask[np.triu_indices(n_ct, k=1)]]
diff_organ_vals = upper_tri[~same_organ_mask[np.triu_indices(n_ct, k=1)]]
same_ct_vals = upper_tri[same_ct_mask[np.triu_indices(n_ct, k=1)]]
diff_ct_vals = upper_tri[~same_ct_mask[np.triu_indices(n_ct, k=1)]]

print(f"  Same organ (n={len(same_organ_vals)}): mean={np.mean(same_organ_vals):.2f} median={np.median(same_organ_vals):.2f}")
print(f"  Diff organ (n={len(diff_organ_vals)}): mean={np.mean(diff_organ_vals):.2f} median={np.median(diff_organ_vals):.2f}")
print(f"  Same CT (n={len(same_ct_vals)}): mean={np.mean(same_ct_vals):.2f} median={np.median(same_ct_vals):.2f}")
print(f"  Diff CT (n={len(diff_ct_vals)}): mean={np.mean(diff_ct_vals):.2f} median={np.median(diff_ct_vals):.2f}")

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
for i in range(n_ct):
    for j in range(n_ct):
        val = omega_clustered[i,j]
        if val > 0:
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=4,
                    color="white" if val > np.percentile(upper_tri, 70) else "black")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_v3_human_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase33_v3_human_heatmap.png")

# Dendrogram
fig, ax = plt.subplots(figsize=(max(22, n_ct*0.6), 5))
dn = dendrogram(linkage_matrix, labels=labels, ax=ax, leaf_font_size=7,
                color_threshold=np.percentile(linkage_matrix[:,2], 60))
ax.set_title("CKI Phase 3.3 v3: TS Human Omega Dendrogram", fontsize=13, fontweight="bold")
ax.set_ylabel("Omega distance (Ward)", fontsize=10)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_v3_human_dendrogram.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: phase33_v3_human_dendrogram.png")

# === 8. Category boxplot ===
print("\n" + "="*60)
print("8. Category boxplot...")
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
bp = ax.boxplot(cat_vals, tick_labels=cat_names, patch_artist=True, widths=0.5)
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
ax.set_title(f"CKI Phase 3.3 v3: Omega by Category (n={len(pairs_df)} pairs)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase33_v3_human_category_boxplot.png", dpi=150)
plt.close()
print("  Saved: phase33_v3_human_category_boxplot.png")

# === 9. Top/Bottom pairs ===
print("\n" + "="*60)
print("9. Top/Bottom Pairs")
print("="*60)

print("\n  Top 15:")
for _, row in pairs_df.head(15).iterrows():
    so = " [SO]" if row["same_organ"] else ""
    sc = " [SC]" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}{so}{sc}")

print("\n  Bottom 15:")
for _, row in pairs_df.tail(15).iterrows():
    so = " [SO]" if row["same_organ"] else ""
    sc = " [SC]" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}{so}{sc}")

# === 10. Summary ===
print("\n" + "="*60)
print("10. Summary Statistics")
print("="*60)

print(f"  CT entries: {n_ct}")
print(f"  Total pairs: {total_pairs}")
print(f"  Omega range: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]")
print(f"  Omega mean: {np.mean(upper_tri):.2f}")
print(f"  Omega median: {np.median(upper_tri):.2f}")
print(f"  Omega std: {np.std(upper_tri):.2f}")
print(f"  k_f mean: {np.mean(upper_kf):.4f}")
print(f"  k_n mean: {np.mean(upper_kn):.4f}")
print(f"  AUC: {auc_ct:.3f}")
print(f"  Effect sep: {effect_sep:.2f}")

# === 11. Cross-species comparison ===
print("\n" + "="*60)
print("11. Cross-species comparison (v3 Human vs Phase 3.2 Mouse)")
print("="*60)

try:
    mouse_omega = pd.read_csv(RESULTS_DIR / "full_matrix_omega.csv", index_col=0)
    mouse_kf = pd.read_csv(RESULTS_DIR / "full_matrix_kf.csv", index_col=0)
    mouse_kn = pd.read_csv(RESULTS_DIR / "full_matrix_kn.csv", index_col=0)
    m_ut = mouse_omega.values[np.triu_indices(len(mouse_omega), k=1)]
    m_kf = mouse_kf.values[np.triu_indices(len(mouse_kf), k=1)]
    m_kn = mouse_kn.values[np.triu_indices(len(mouse_kn), k=1)]

    print(f"\n  Mouse (Phase 3.2): n={len(m_ut)}, omega_mean={np.mean(m_ut):.2f}")
    print(f"                         k_f_mean={np.mean(m_kf):.4f}, k_n_mean={np.mean(m_kn):.4f}")
    print(f"  Human v3:          n={len(upper_tri)}, omega_mean={np.mean(upper_tri):.2f}")
    print(f"                         k_f_mean={np.mean(upper_kf):.4f}, k_n_mean={np.mean(upper_kn):.4f}")

    # Histogram overlay
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(m_ut, bins=40, color="#1E3A5F", alpha=0.5,
            label=f"Mouse P3.2 (mean={np.mean(m_ut):.2f})")
    ax.hist(upper_tri, bins=40, color="#059669", alpha=0.5,
            label=f"Human v3 (mean={np.mean(upper_tri):.2f})")
    ax.set_xlabel("omega", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("CKI Phase 3.3 v3: Mouse vs Human Omega (hybrid method)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=11)
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "phase33_v3_cross_species_overlay.png", dpi=150)
    plt.close()
    print("  Saved: phase33_v3_cross_species_overlay.png")

    # Print comparison table
    print(f"\n  {'Metric':<20} {'Mouse P3.2':>12} {'Human v3':>12} {'Ratio (H/M)':>12}")
    print(f"  {'omega mean':<20} {np.mean(m_ut):>12.2f} {np.mean(upper_tri):>12.2f} {np.mean(upper_tri)/(np.mean(m_ut)+1e-9):>12.2f}")
    print(f"  {'k_f mean':<20} {np.mean(m_kf):>12.4f} {np.mean(upper_kf):>12.4f} {np.mean(upper_kf)/(np.mean(m_kf)+1e-9):>12.2f}")
    print(f"  {'k_n mean':<20} {np.mean(m_kn):>12.4f} {np.mean(upper_kn):>12.4f} {np.mean(upper_kn)/(np.mean(m_kn)+1e-9):>12.2f}")

except Exception as e:
    print(f"  [Cross-species skipped: {e}]")

# === 12. Report ===
print("\n" + "="*60)
print("12. Writing report...")
print("="*60)

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

# Precompute cross-species summary for report
m_ut_n = len(m_ut) if 'm_ut' in dir() else 'N/A'
m_ut_mean = f"{np.mean(m_ut):.2f}" if 'm_ut' in dir() else 'N/A'

report = f"""# CKI Phase 3.3 v3 Report: Hybrid Omega (Global k_n + Per-Pair k_f)

## Date: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}

## Method
- **k_n**: GLOBAL HK genes (stable, comparable across all pairs and to mouse)
- **k_f**: Per-pair top-{N_TOP_KF} DE genes (exclude HK, select by |pb_i - pb_j|)
- **omega** = k_f / k_n

## Fix History
| Version | k_n | k_f | omega_mean | Problem |
|---------|-----|-----|------------|---------|
| v1 | Global HK | Global HVG(2000) | 1.41 | k_f compressed by non-specific HVG |
| v2 | Per-pair HVG (incl HK) | Per-pair HVG (incl HK) | 39.00 | k_n inflated by per-pair selection |
| v3 | **Global HK (fixed)** | **Per-pair top-{N_TOP_KF} non-HK** | TBD | -- |

## Dataset
- 6 organs: {', '.join(TS_ORGANS)}
- {adata.n_obs} cells x {adata.n_vars} genes (post-QC, log1p)
- {n_ct} CT entries

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
- **k_f mean**: {np.mean(upper_kf):.4f}
- **k_n mean**: {np.mean(upper_kn):.4f}
- **AUC** (CT discrimination): {auc_ct:.3f}
- **Effect separation** (diff_CT / same_CT): {effect_sep:.2f}

### Category breakdown
| Category | n | mean omega | median omega |
|----------|---|------------|--------------|
| SameOrgan SameCT | {len(cat_vals[0])} | {np.mean(cat_vals[0]):.2f} | {np.median(cat_vals[0]):.2f} |
| SameOrgan DiffCT | {len(cat_vals[1])} | {np.mean(cat_vals[1]):.2f} | {np.median(cat_vals[1]):.2f} |
| DiffOrgan SameCT | {len(cat_vals[2])} | {np.mean(cat_vals[2]):.2f} | {np.median(cat_vals[2]):.2f} |
| DiffOrgan DiffCT | {len(cat_vals[3])} | {np.mean(cat_vals[3]):.2f} | {np.median(cat_vals[3]):.2f} |

## Cross-Species Comparison
- Mouse (FACS, Phase 3.2): n={m_ut_n}, mean={m_ut_mean}
- Human v3 (TS, Phase 3.3): n={total_pairs}, mean={np.mean(upper_tri):.2f}

## Files Generated
- `phase33_v3_human_omega.csv`
- `phase33_v3_human_kn.csv`
- `phase33_v3_human_kf.csv`
- `phase33_v3_human_pairs.csv`
- `phase33_v3_human_heatmap.png`
- `phase33_v3_human_dendrogram.png`
- `phase33_v3_human_category_boxplot.png`
- `phase33_v3_cross_species_overlay.png`

## Next Steps
- Phase 3.4: TCGA tumor perturbation
- Phase 3.5: Method comparison (SAMap / SATURN / CACIMAR)
"""

report_path = RESULTS_DIR / "phase33_v3_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)
print(f"  Saved: phase33_v3_report.md")

print("\n" + "="*60)
print("DONE. Phase 3.3 v3 complete.")
print("="*60)
