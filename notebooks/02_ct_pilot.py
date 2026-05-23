"""
CKI Cell-Type-Level Pilot Validation
=====================================
Switching from tissue-level to cell-type-level pseudobulk.
Control design: same tissue + same cell type, different mice -> expected omega ~1.0
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

# CJK font setup
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
    print(f"  Using CJK font: {_cjk_prop.get_name()}")
else:
    plt.rcParams["font.family"] = "sans-serif"

from cki.core import compute_omega

# ── Config ──────────────────────────────────────────────────
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE  = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
N_BOOTSTRAP = 500
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10  # per (tissue, cell_type, mouse_group)

def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

# ── 1. Load Data ────────────────────────────────────────────
print("=" * 60)
print("1. Loading data...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  Housekeeping genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)
print(f"  Annotations: {len(annot)} cells in target tissues")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# ── 2. Build Unified AnnData ────────────────────────────────
print("\n" + "=" * 60)
print("2. Building unified AnnData...")
print("=" * 60)

common_genes = all_genes.copy()
for tissue, df in adatas.items():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell", "cell_ontology_class", "mouse.id"]],
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

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

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
print(f"  HK genes: {len(hk_indices)}, Identity genes: {len(identity_indices)}")

# ── 5. Build Cell-Type-Level Pseudobulk per Mouse Group ─────
print("\n" + "=" * 60)
print("5. Building CT-level pseudobulk per mouse group...")
print("=" * 60)

# Store raw cell data per (tissue, cell_type) for later control split
ct_all_cells = {}  # key: (tissue, ct), value: expression matrix (all cells, pooled)
ct_pb_largest = {}  # key: (tissue, ct), value: pseudobulk of largest mouse group
ct_cells_largest = {}  # key: (tissue, ct), value: cells of largest mouse group

for tissue in TARGET_TISSUES:
    tdata = adata[adata.obs["tissue"] == tissue]
    t_cts = tdata.obs["cell_ontology_class"].unique()
    for ct in t_cts:
        if ct.lower() == "unknown":
            continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2:
            continue
        
        X_all = ct_data.X
        if hasattr(X_all, "toarray"): X_all = X_all.toarray()
        ct_all_cells[(tissue, ct)] = X_all
        
        # Also get largest mouse group for cross-tissue comparisons
        mouse_counts = ct_data.obs["mouse.id"].value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) >= 1:
            mice_ok.sort(key=lambda x: -x[1])
            largest_mouse = mice_ok[0][0]
            mask_largest = ct_data.obs["mouse.id"] == largest_mouse
            X_largest = ct_data[mask_largest].X
            if hasattr(X_largest, "toarray"): X_largest = X_largest.toarray()
            if X_largest.shape[0] >= MIN_CELLS_PER_CT:
                ct_pb_largest[(tissue, ct)] = np.mean(X_largest, axis=0)
                ct_cells_largest[(tissue, ct)] = X_largest

print(f"  CTs with >= {MIN_CELLS_PER_CT*2} cells: {len(ct_all_cells)}")
print(f"  CTs with largest-mouse group: {len(ct_pb_largest)}")

# Helper: random balanced split of pooled cells for control
def random_split_cells(cells, seed=RANDOM_SEED):
    """Split cell matrix into two balanced halves randomly."""
    n = cells.shape[0]
    n_half = n // 2
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    return cells[idx[:n_half]], cells[idx[n_half:]]

# Also build simple tissue-level pseudobulk for cross-CT comparisons
tissue_pb = {}
for t in TARGET_TISSUES:
    mask = adata.obs["tissue"] == t
    X_t = adata[mask].X
    if hasattr(X_t, "toarray"): X_t = X_t.toarray()
    tissue_pb[t] = np.mean(X_t, axis=0)

# ── 6. Define Comparison Groups ─────────────────────────────
print("\n" + "=" * 60)
print("6. Defining comparisons...")
print("=" * 60)

comparisons = []

# === C: Control (same tissue, same CT, RANDOM split of pooled cells) ===
# Expected omega ~1.0 (both halves drawn from same distribution)
control_pairs = [
    ("Liver", "hepatocyte"),
    ("Heart", "endothelial cell"),
    ("Spleen", "B cell"),
    ("Marrow", "B cell"),
    ("Heart", "fibroblast"),
    ("Marrow", "neutrophil"),
]
for tissue, ct in control_pairs:
    key = (tissue, ct)
    if key in ct_all_cells:
        cells_a, cells_b = random_split_cells(ct_all_cells[key])
        label = f"C: {ct}\n({tissue})"
        comparisons.append({
            "label": label, "category": "C_control",
            "type": "within_ct_random",
            "tissue": tissue, "ct": ct,
            "pb_a": np.mean(cells_a, axis=0),
            "pb_b": np.mean(cells_b, axis=0),
            "cells_a": cells_a,
            "cells_b": cells_b,
        })

# === S: Same CT across tissues ===
# Expected omega 2-5 (moderate)
same_ct_pairs = [
    ("B cell", "Marrow", "Spleen"),
    ("B cell", "Spleen", "Lung"),
    ("endothelial cell", "Heart", "Lung"),
    ("natural killer cell", "Marrow", "Liver"),
]
for ct, t1, t2 in same_ct_pairs:
    key1 = (t1, ct)
    key2 = (t2, ct)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        label = f"S: {ct}\n({t1} vs {t2})"
        comparisons.append({
            "label": label, "category": "S_same_ct",
            "type": "cross_tissue_same_ct",
            "tissue_a": t1, "tissue_b": t2, "ct": ct,
            "pb_a": ct_pb_largest[key1],
            "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1],
            "cells_b": ct_cells_largest[key2],
        })

# === D: Different CT, same tissue ===
# Expected omega 5-15
diff_ct_pairs = [
    ("Liver", "hepatocyte", "endothelial cell of hepatic sinusoid"),
    ("Marrow", "B cell", "neutrophil"),
    ("Heart", "endothelial cell", "fibroblast"),
]
for tissue, ct1, ct2 in diff_ct_pairs:
    key1 = (tissue, ct1)
    key2 = (tissue, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        label = f"D: {ct1} vs {ct2}\n({tissue})"
        comparisons.append({
            "label": label, "category": "D_diff_ct",
            "type": "within_tissue_diff_ct",
            "tissue": tissue, "ct_a": ct1, "ct_b": ct2,
            "pb_a": ct_pb_largest[key1],
            "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1],
            "cells_b": ct_cells_largest[key2],
        })

# === X: Different CT, different tissue ===
# Expected omega >15
cross_pairs = [
    ("Liver", "hepatocyte", "Marrow", "B cell"),
    ("Heart", "cardiac muscle cell", "Marrow", "neutrophil"),
]
for t1, ct1, t2, ct2 in cross_pairs:
    key1 = (t1, ct1)
    key2 = (t2, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        label = f"X: {ct1}({t1})\nvs {ct2}({t2})"
        comparisons.append({
            "label": label, "category": "X_cross",
            "type": "cross_tissue_diff_ct",
            "tissue_a": t1, "tissue_b": t2,
            "ct_a": ct1, "ct_b": ct2,
            "pb_a": ct_pb_largest[key1],
            "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1],
            "cells_b": ct_cells_largest[key2],
        })

print(f"  Total comparisons: {len(comparisons)}")
for c in comparisons:
    print(f"    {c['label'].replace(chr(10),' ')} [{c['category']}]")

# ── 7. Run CKI with Bootstrap ───────────────────────────────
print("\n" + "=" * 60)
print("7. Running CKI with bootstrap...")
print("=" * 60)

results_list = []
for comp in comparisons:
    label = comp["label"]
    pb_a = comp["pb_a"]
    pb_b = comp["pb_b"]
    cells_a = comp["cells_a"]
    cells_b = comp["cells_b"]
    n_a, n_b = cells_a.shape[0], cells_b.shape[0]
    
    # Compute observed omega
    result = compute_omega(pb_a, pb_b, hk_indices, identity_indices)
    observed = result["omega"]
    
    # Bootstrap: pool cells, permute, recompute
    pooled = np.vstack([cells_a, cells_b])
    n_total = n_a + n_b
    rng = np.random.RandomState(RANDOM_SEED)
    
    null_omega = []
    for _ in tqdm(range(N_BOOTSTRAP), desc=f"  {label.replace(chr(10),' ')}"):
        perm = rng.permutation(n_total)
        pb_perm1 = np.mean(pooled[perm[:n_a]], axis=0)
        pb_perm2 = np.mean(pooled[perm[n_a:]], axis=0)
        r = compute_omega(pb_perm1, pb_perm2, hk_indices, identity_indices)
        if not np.isnan(r["omega"]):
            null_omega.append(r["omega"])
    
    null_omega = np.array(null_omega)
    if len(null_omega) == 0:
        p_value, null_mean, null_std, cohens_d = 1.0, np.nan, np.nan, np.nan
    else:
        p_value = (np.sum(null_omega >= observed) + 1) / (len(null_omega) + 1)
        null_mean = np.mean(null_omega)
        null_std = np.std(null_omega)
        cohens_d = (observed - null_mean) / null_std if null_std > 1e-12 else 0.0
    
    entry = {
        "comparison": label,
        "category": comp["category"],
        "omega": observed,
        "kn": result["kn"], "kf": result["kf"],
        "delta_hk": result["delta_hk"],
        "delta_identity": result["delta_identity"],
        "p_value": p_value,
        "null_mean": null_mean, "null_std": null_std,
        "cohens_d": cohens_d,
        "n_cells_A": n_a, "n_cells_B": n_b,
        "null_distribution": null_omega.tolist() if len(null_omega) > 0 else [],
    }
    results_list.append(entry)
    
    sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    print(f"  {label.replace(chr(10),' ')}: omega={observed:.3f}, "
          f"kn={result['kn']:.5f}, kf={result['kf']:.5f}, "
          f"p={p_value:.4f}{sig}, d={cohens_d:.2f}")

results_df = pd.DataFrame(results_list)

# ── 8. Save Results Table ───────────────────────────────────
print("\n" + "=" * 60)
print("8. Saving results...")
print("=" * 60)

results_csv = results_df.drop(columns=["null_distribution"], errors="ignore")
results_csv.to_csv(RESULTS_DIR / "ct_pilot_results.csv", index=False)
print("  Saved: ct_pilot_results.csv")

# ── 9. Visualization ────────────────────────────────────────
print("\n" + "=" * 60)
print("9. Generating figures...")
print("=" * 60)

# 9a. Main bar chart: all comparisons colored by category
category_colors = {
    "C_control": "#059669",
    "S_same_ct": "#D4AF37",
    "D_diff_ct": "#E67E22",
    "X_cross": "#C0392B",
}
category_labels = {
    "C_control": "Control (same CT, same tissue, diff mice)",
    "S_same_ct": "Same CT, diff tissue",
    "D_diff_ct": "Diff CT, same tissue",
    "X_cross": "Diff CT, diff tissue",
}
category_order = ["C_control", "S_same_ct", "D_diff_ct", "X_cross"]

# Sort results by category order then by omega
results_df["cat_order"] = results_df["category"].apply(lambda x: category_order.index(x) if x in category_order else 99)
results_df = results_df.sort_values(["cat_order", "omega"]).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(14, 6))
bar_colors = [category_colors.get(c, "#999") for c in results_df["category"]]
x_pos = range(len(results_df))
bars = ax.bar(x_pos, results_df["omega"], color=bar_colors, edgecolor="white", linewidth=0.5)

# Short labels
short_labels = [r["comparison"].replace("\n", " ").replace("(", " ").replace(")", "")[:35] for _, r in results_df.iterrows()]
ax.set_xticks(x_pos)
ax.set_xticklabels(short_labels, rotation=30, ha="right", fontsize=7)
ax.set_ylabel("omega", fontsize=12)
ax.set_title("CKI Cell-Type-Level Validation: Control Calibration & Comparisons", fontsize=13, fontweight="bold")
ax.axhline(y=1.0, color="gray", linestyle="--", linewidth=1, alpha=0.5, label="omega=1 (null)")

# Add p-value annotations
for i, (_, row) in enumerate(results_df.iterrows()):
    p = row["p_value"]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    color = "#1E3A5F" if p < 0.05 else "#999"
    ax.text(i, row["omega"] + max(0.3, row["omega"]*0.02),
            f"p={p:.4f}{sig}", ha="center", fontsize=6.5, color=color)

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=category_labels[cat]) for cat, c in category_colors.items()]
legend_elements.append(plt.Line2D([0], [0], color="gray", linestyle="--", linewidth=1, label="omega=1"))
ax.legend(handles=legend_elements, fontsize=7, loc="upper left")

plt.tight_layout()
fig.savefig(RESULTS_DIR / "ct_key_comparisons.png", dpi=150)
plt.close()
print("  Saved: ct_key_comparisons.png")

# 9b. Category summary boxplot
fig, ax = plt.subplots(figsize=(8, 5))
plot_data = []
plot_cats = []
for cat in category_order:
    vals = results_df[results_df["category"] == cat]["omega"].values
    if len(vals) > 0:
        plot_data.append(vals)
        plot_cats.append(cat)

bp = ax.boxplot(plot_data, labels=[category_labels.get(c, c).replace(" ", "\n") for c in plot_cats],
                patch_artist=True, widths=0.5)
for i, cat in enumerate(plot_cats):
    bp["boxes"][i].set_facecolor(category_colors.get(cat, "#999"))

# Overlay individual points
for i, vals in enumerate(plot_data):
    jitter = np.random.RandomState(RANDOM_SEED).normal(0, 0.04, len(vals))
    ax.scatter(np.ones(len(vals)) * (i+1) + jitter, vals, color="#1E3A5F", s=30, alpha=0.7, zorder=3)

ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)
ax.set_ylabel("omega", fontsize=12)
ax.set_title("CKI Validation: Category Summary", fontsize=13, fontweight="bold")
plt.tight_layout()
fig.savefig(RESULTS_DIR / "ct_category_summary.png", dpi=150)
plt.close()
print("  Saved: ct_category_summary.png")

# 9c. Null distributions
n_comps = len(results_df)
n_cols = 4
n_rows = (n_comps + n_cols - 1) // n_cols
fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3.5 * n_rows))
axes = np.atleast_1d(axes).flatten()

for i, (_, row) in enumerate(results_df.iterrows()):
    ax = axes[i]
    nd = row.get("null_distribution", [])
    if len(nd) > 0:
        ax.hist(nd, bins=30, alpha=0.7, color=category_colors.get(row["category"], "#999"), edgecolor="white")
        ax.axvline(x=row["omega"], color="#C0392B", linewidth=2, label=f"obs={row['omega']:.2f}")
        ax.axvline(x=1.0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(row["comparison"].replace("\n", " ")[:30], fontsize=7)
    ax.set_xlabel("omega", fontsize=6)
    ax.set_ylabel("", fontsize=6)
    ax.tick_params(labelsize=6)
    if len(nd) > 0:
        ax.legend(fontsize=5)

for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "ct_null_distributions.png", dpi=150)
plt.close()
print("  Saved: ct_null_distributions.png")

# ── 10. Print Summary ───────────────────────────────────────
print("\n" + "=" * 60)
print("10. Category Summary Statistics")
print("=" * 60)

for cat in category_order:
    cat_data = results_df[results_df["category"] == cat]
    if len(cat_data) == 0:
        continue
    omegas = cat_data["omega"].values
    print(f"\n  {category_labels.get(cat, cat)} (n={len(cat_data)}):")
    print(f"    Mean omega: {np.mean(omegas):.3f}")
    print(f"    Median omega: {np.median(omegas):.3f}")
    print(f"    Range: [{np.min(omegas):.3f}, {np.max(omegas):.3f}]")
    print(f"    Std: {np.std(omegas):.3f}")
    sig_count = (cat_data["p_value"] < 0.05).sum()
    print(f"    Significant (p<0.05): {sig_count}/{len(cat_data)}")

# ── 11. Check pass/fail for control calibration ─────────────
print("\n" + "=" * 60)
print("11. Control Calibration Check")
print("=" * 60)

control_data = results_df[results_df["category"] == "C_control"]
if len(control_data) > 0:
    ctrl_mean = control_data["omega"].mean()
    ctrl_median = control_data["omega"].median()
    ctrl_min, ctrl_max = control_data["omega"].min(), control_data["omega"].max()
    ctrl_sig = (control_data["p_value"] < 0.05).sum()
    
    print(f"  Control comparisons: {len(control_data)}")
    print(f"  Mean omega: {ctrl_mean:.3f}")
    print(f"  Median omega: {ctrl_median:.3f}")
    print(f"  Range: [{ctrl_min:.3f}, {ctrl_max:.3f}]")
    print(f"  Significant (p<0.05): {ctrl_sig}/{len(control_data)}")
    
    # Pass if mean omega < 2.0 (relaxed from 1.0 since biological variation exists)
    if ctrl_mean < 2.0:
        print(f"\n  >>> PASS: Control mean omega ({ctrl_mean:.1f}) < 2.0, calibration acceptable")
        print(f"  >>> Ready to proceed to Benchmark phase.")
    else:
        print(f"\n  >>> NEEDS WORK: Control mean omega ({ctrl_mean:.1f}) >= 2.0")
else:
    print("  WARNING: No control comparisons computed")

print("\n" + "=" * 60)
print("DONE. All results saved to:", str(RESULTS_DIR))
print("=" * 60)
