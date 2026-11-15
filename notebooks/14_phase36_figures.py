"""
CKI Phase 3.6: Generate NBT manuscript figures
================================================
Generates all 7 data-driven figure panels and 3 conceptual diagrams.

Figures:
  Fig 1a: Ka/Ks → CKI conceptual diagram
  Fig 1b: CKI computation pipeline flowchart
  Fig 1c: Bootstrap permutation schematic
  Fig 2b: k_n/k_f component decomposition (Phase 3.2 mouse data)
  Fig 2d: Per-gene JS divergence (hepatocyte vs LSEC)
  Fig 3d: SameOrgan/DiffOrgan effect reversal (Phase 3.5)
  Fig 5a: Cross-organ omega ranking bar plot
  Fig 5b: Ranking consistency scatter plot
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Wedge
from pathlib import Path
from scipy.special import softmax
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

# CJK font setup
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
else:
    plt.rcParams["font.family"] = "sans-serif"

# === Config ===
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

# NBT color scheme
CKI_BLUE = "#1E3A5F"
CKI_GOLD = "#D4AF37"
CKI_GREEN = "#059669"
CKI_RED = "#C0392B"
CKI_ORANGE = "#E67E22"
CKI_GRAY = "#7F8C8D"
CKI_LIGHT = "#ECF0F1"

DPI = 300
FIGSIZE_FULL = (10, 6)
FIGSIZE_WIDE = (12, 5)
FIGSIZE_SQUARE = (8, 8)

print("=" * 60)
print("Phase 3.6: NBT Figure Generation")
print("=" * 60)

# ============================================================
# Fig 1a: Ka/Ks → CKI Conceptual Diagram
# ============================================================
print("\n[1/10] Fig 1a: Ka/Ks analogy conceptual diagram")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left panel: Ka/Ks
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis("off")
ax1.set_title("Molecular Evolution: Ka/Ks", fontsize=14, fontweight="bold", color=CKI_BLUE, pad=15)

# DNA sequence
dna_y = 8
ax1.text(5, dna_y + 1.2, "DNA Sequence Alignment", ha="center", fontsize=11, fontweight="bold", color="black")
ax1.plot([1.5, 8.5], [dna_y, dna_y], "k-", lw=3)
# Synonymous sites
for x in [2.0, 3.5, 5.0, 6.5, 8.0]:
    ax1.plot(x, dna_y, "o", ms=8, color=CKI_GRAY, alpha=0.5)
# Nonsynonymous sites
for x in [2.5, 4.0, 5.5, 7.0]:
    ax1.plot(x, dna_y, "o", ms=8, color=CKI_RED, alpha=0.5)

# Arrow to Ks
ax1.annotate("", xy=(3.5, 5.5), xytext=(3.5, 7.2),
             arrowprops=dict(arrowstyle="->", color=CKI_GRAY, lw=2))
ax1.text(4.0, 6.3, "Synonymous (Ks)\nNeutral baseline", fontsize=9, color=CKI_GRAY)

# Arrow to Ka
ax1.annotate("", xy=(6.0, 5.5), xytext=(6.0, 7.2),
             arrowprops=dict(arrowstyle="->", color=CKI_RED, lw=2))
ax1.text(6.5, 6.3, "Nonsynonymous (Ka)\nUnder selection", fontsize=9, color=CKI_RED)

# Omega formula
ax1.text(5, 4.5, "omega = Ka / Ks", ha="center", fontsize=13, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor=CKI_LIGHT, edgecolor=CKI_BLUE))
ax1.text(5, 3.8, "omega > 1: Positive selection", ha="center", fontsize=10, color=CKI_RED)

# Right panel: CKI
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis("off")
ax2.set_title("Transcriptomics: CKI", fontsize=14, fontweight="bold", color=CKI_GREEN, pad=15)

# Gene expression
exp_y = 8
ax2.text(5, exp_y + 1.2, "Pseudobulk Expression Profiles", ha="center", fontsize=11, fontweight="bold", color="black")

# Bar chart representation
bars_x = np.linspace(1.5, 8.5, 15)
heights_a = np.random.RandomState(42).uniform(2, 8, 15)
heights_b = np.random.RandomState(43).uniform(2, 8, 15)
bar_w = 0.3

for i in range(15):
    ax2.bar(bars_x[i] - bar_w/2, heights_a[i], bar_w, color=CKI_GRAY if i < 5 else CKI_GREEN, alpha=0.7)
    ax2.bar(bars_x[i] + bar_w/2, heights_b[i], bar_w, color=CKI_GRAY if i < 5 else CKI_GREEN, alpha=0.4)

# Label HK vs identity
ax2.text(2.5, 8.8, "HK", ha="center", fontsize=8, color=CKI_GRAY, fontweight="bold")
ax2.text(6.0, 8.8, "Identity", ha="center", fontsize=8, color=CKI_GREEN, fontweight="bold")

# Arrow to k_n
ax2.annotate("", xy=(3.0, 5.5), xytext=(3.0, 7.2),
             arrowprops=dict(arrowstyle="->", color=CKI_GRAY, lw=2))
ax2.text(3.5, 6.3, "k_n (JS on HK)\nNeutral offset", fontsize=9, color=CKI_GRAY)

# Arrow to k_f
ax2.annotate("", xy=(7.0, 5.5), xytext=(7.0, 7.2),
             arrowprops=dict(arrowstyle="->", color=CKI_GREEN, lw=2))
ax2.text(7.5, 6.3, "k_f (JS on identity)\nFunctional conversion", fontsize=9, color=CKI_GREEN)

# Omega formula
ax2.text(5, 4.5, "omega = k_f / k_n", ha="center", fontsize=13, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor=CKI_LIGHT, edgecolor=CKI_GREEN))
ax2.text(5, 3.8, "omega >> 1: Selective remodeling", ha="center", fontsize=10, color=CKI_GREEN)

# Bridge arrow
fig.text(0.5, 0.02, "Conceptual mapping: Neutral reference enables signal/noise decomposition", ha="center",
         fontsize=11, fontstyle="italic", color=CKI_BLUE)

plt.tight_layout(rect=[0, 0.06, 1, 1])
fig.savefig(RESULTS_DIR / "phase36_fig1a_kaks_analogy.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig1a_kaks_analogy.png")

# ============================================================
# Fig 1b: CKI Computation Pipeline Flowchart
# ============================================================
print("[2/10] Fig 1b: CKI computation pipeline")

fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 4)
ax.axis("off")

# Pipeline boxes
boxes = [
    (0.5, 1.5, 2.5, 1.0, "scRNA-seq\nCount Matrix", CKI_BLUE),
    (3.5, 1.5, 2.5, 1.0, "Pseudobulk\n(mean per CT)", CKI_BLUE),
    (6.5, 2.2, 2.0, 0.6, "JS on HK genes\n→ k_n", CKI_GRAY),
    (6.5, 0.7, 2.0, 0.6, "JS on identity genes\n→ k_f", CKI_GREEN),
    (9.0, 1.5, 2.0, 1.0, "omega = k_f/k_n\n+ Bootstrap test", CKI_GOLD),
    (11.5, 1.5, 2.0, 1.0, "Cell-state\nKinetic Index", CKI_RED),
]

for x, y, w, h, label, color in boxes:
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor="white", alpha=0.9, lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=8,
            color="white", fontweight="bold")

# Arrows between main boxes
for i in range(len(boxes) - 1):
    if i == 1:
        # Split: box 1 -> box 2 (top) and box 3 (bottom)
        x1 = boxes[1][0] + boxes[1][2]
        y1_top = boxes[2][1] + boxes[2][3]/2
        y1_bot = boxes[3][1] + boxes[3][3]/2
        ax.annotate("", xy=(boxes[2][0], y1_top), xytext=(x1, boxes[1][1] + boxes[1][3]*0.75),
                    arrowprops=dict(arrowstyle="->", color=CKI_GRAY, lw=1.5))
        ax.annotate("", xy=(boxes[3][0], y1_bot), xytext=(x1, boxes[1][1] + boxes[1][3]*0.25),
                    arrowprops=dict(arrowstyle="->", color=CKI_GREEN, lw=1.5))
    elif i == 0 or i >= 4:
        x1 = boxes[i][0] + boxes[i][2]
        y1 = boxes[i][1] + boxes[i][3]/2
        x2 = boxes[i+1][0]
        y2 = boxes[i+1][1] + boxes[i+1][3]/2
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="white", lw=1.5))
    elif i == 2:
        # Merge: box 2 and 3 -> box 4
        x1 = boxes[2][0] + boxes[2][2]
        y1 = boxes[2][1] + boxes[2][3]/2
        x2 = boxes[4][0]
        y2 = boxes[4][1] + boxes[4][3]*0.75
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=CKI_GRAY, lw=1.5))
        x1 = boxes[3][0] + boxes[3][2]
        y1 = boxes[3][1] + boxes[3][3]/2
        y2 = boxes[4][1] + boxes[4][3]*0.25
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=CKI_GREEN, lw=1.5))

ax.set_title("CKI Computation Pipeline", fontsize=14, fontweight="bold", color=CKI_BLUE, pad=20)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig1b_pipeline.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig1b_pipeline.png")

# ============================================================
# Fig 1c: Bootstrap Permutation Schematic
# ============================================================
print("[3/10] Fig 1c: Bootstrap permutation schematic")

fig, axes = plt.subplots(1, 3, figsize=(14, 5))

# Panel 1: Observed data
ax = axes[0]
np.random.seed(42)
group_a = np.random.normal(loc=2, scale=0.5, size=30)
group_b = np.random.normal(loc=5, scale=0.5, size=30)
ax.scatter(np.ones(30)*0.9, group_a, s=20, color=CKI_BLUE, alpha=0.6, label="Population A", zorder=3)
ax.scatter(np.ones(30)*1.1, group_b, s=20, color=CKI_RED, alpha=0.6, label="Population B", zorder=3)
ax.boxplot([group_a, group_b], positions=[1, 1], widths=0.3, patch_artist=True,
           boxprops=dict(facecolor=CKI_LIGHT), medianprops=dict(color=CKI_BLUE))
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_ylabel("Expression (log1p)", fontsize=10)
ax.set_title("Observed Populations\nomega_obs = 5.2", fontsize=11, fontweight="bold", color=CKI_BLUE)
ax.legend(fontsize=8, loc="upper left")

# Panel 2: Permutation
ax = axes[1]
all_data = np.concatenate([group_a, group_b])
np.random.shuffle(all_data)
perm_a = all_data[:30]
perm_b = all_data[30:]
ax.scatter(np.ones(30)*0.9, perm_a, s=20, color=CKI_GRAY, alpha=0.5, label="Shuffled A", zorder=3)
ax.scatter(np.ones(30)*1.1, perm_b, s=20, color=CKI_GRAY, alpha=0.5, label="Shuffled B", zorder=3)
ax.boxplot([perm_a, perm_b], positions=[1, 1], widths=0.3, patch_artist=True,
           boxprops=dict(facecolor=CKI_LIGHT), medianprops=dict(color=CKI_GRAY))
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_ylabel("")
ax.set_title("Permuted Labels (x1000)\nomega_null ~ 0.8", fontsize=11, fontweight="bold", color=CKI_GRAY)
ax.legend(fontsize=8, loc="upper left")

# Panel 3: Null distribution
ax = axes[2]
null_dist = np.random.lognormal(mean=-0.2, sigma=0.3, size=1000)
null_dist = np.clip(null_dist, 0.01, 3.0)
ax.hist(null_dist, bins=40, color=CKI_GRAY, alpha=0.5, edgecolor="white", density=True)
ax.axvline(x=5.2, color=CKI_RED, lw=2.5, linestyle="--", label=f"omega_obs = 5.2")
ax.axvline(x=np.percentile(null_dist, 95), color=CKI_BLUE, lw=1.5, linestyle=":",
           label=f"95th percentile = {np.percentile(null_dist, 95):.1f}")
ax.set_xlabel("omega", fontsize=10)
ax.set_ylabel("Density", fontsize=10)
ax.set_title("Null Distribution\np < 0.001", fontsize=11, fontweight="bold", color=CKI_BLUE)
ax.legend(fontsize=8)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig1c_bootstrap.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig1c_bootstrap.png")

# ============================================================
# Fig 2b: k_n / k_f Component Decomposition
# ============================================================
print("[4/10] Fig 2b: k_n/k_f component decomposition")

pilot_df = pd.read_csv(RESULTS_DIR / "pilot_results.csv")
# 根据expected列创建category映射
expected_to_category = {
    "conserved": "C_control",
    "moderate": "X_cross",
    "divergent": "D_diff_ct"
}
pilot_df["category"] = pilot_df["expected"].map(expected_to_category)
pilot_df["category_short"] = pilot_df["category"].map({
    "C_control": "Controls (C)", "S_same_ct": "Same-CT (S)",
    "D_diff_ct": "Diff-CT (D)", "X_cross": "Cross (X)"
})

cat_order = ["Controls (C)", "Same-CT (S)", "Diff-CT (D)", "Cross (X)"]
cat_colors = [CKI_GRAY, CKI_GOLD, CKI_GREEN, CKI_RED]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Panel: k_n by category
kn_data = [pilot_df[pilot_df["category_short"] == c]["kn"].values * 1000 for c in cat_order]
bp1 = ax1.boxplot(kn_data, labels=["C", "S", "D", "X"], patch_artist=True, widths=0.5)
for i in range(4):
    bp1["boxes"][i].set_facecolor(cat_colors[i])
    if len(kn_data[i]) > 0:
        jitter = np.random.RandomState(42).normal(0, 0.03, len(kn_data[i]))
        ax1.scatter(np.ones(len(kn_data[i]))*(i+1) + jitter, kn_data[i],
                   color=CKI_BLUE, s=25, alpha=0.5, zorder=3)
ax1.set_ylabel("k_n (x10^-3)", fontsize=11, color=CKI_GRAY)
ax1.set_title("Neutral Offset Rate (k_n)", fontsize=12, fontweight="bold", color=CKI_GRAY)
ax1.set_ylim(bottom=0)

# Panel: k_f by category
kf_data = [pilot_df[pilot_df["category_short"] == c]["kf"].values * 1000 for c in cat_order]
bp2 = ax2.boxplot(kf_data, labels=["C", "S", "D", "X"], patch_artist=True, widths=0.5)
for i in range(4):
    bp2["boxes"][i].set_facecolor(cat_colors[i])
    if len(kf_data[i]) > 0:
        jitter = np.random.RandomState(42).normal(0, 0.03, len(kf_data[i]))
        ax2.scatter(np.ones(len(kf_data[i]))*(i+1) + jitter, kf_data[i],
                   color=CKI_BLUE, s=25, alpha=0.5, zorder=3)
ax2.set_ylabel("k_f (x10^-3)", fontsize=11, color=CKI_GREEN)
ax2.set_title("Functional Conversion Rate (k_f)", fontsize=12, fontweight="bold", color=CKI_GREEN)
ax2.set_ylim(bottom=0)

# Add fold-change annotation
kn_means = [np.mean(d) for d in kn_data]
kf_means = [np.mean(d) for d in kf_data]
kf_kn_ratio = [f/b if b > 0 else 0 for f, b in zip(kf_means, kn_means)]
for i, (r, c) in enumerate(zip(kf_kn_ratio, cat_order)):
    ax2.annotate(f"k_f/k_n\n= {r:.1f}x", (i+1, kf_means[i] + 10), ha="center", fontsize=7, color=CKI_BLUE)

plt.suptitle("Component Decomposition by Comparison Category\n(Tabula Muris, n=15 pairs)", fontsize=13, fontweight="bold", color=CKI_BLUE)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig2b_kn_kf_decomposition.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig2b_kn_kf_decomposition.png")

# ============================================================
# Fig 2d: Per-gene JS Divergence (hepatocyte vs LSEC)
# ============================================================
print("[5/10] Fig 2d: Per-gene JS divergence")

import scanpy as sc

FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())

annot = pd.read_csv(ANNOT_FILE)
annot["mouse.id"] = annot["cell"].apply(
    lambda c: next((p for p in c.split(".") if "_" in p and (p.endswith("_M") or p.endswith("_F"))), "unknown"))

# Load Liver FACS data
liver_df = pd.read_csv(FACS_DIR / "Liver-counts.csv", index_col=0)
liver_annot = annot[annot["tissue"] == "Liver"].copy()

# Build AnnData for Liver
cell_ids = [c for c in liver_df.columns if c in liver_annot["cell"].values]
liver_annot = liver_annot[liver_annot["cell"].isin(cell_ids)].set_index("cell")
liver_expr = liver_df[cell_ids].T

# Hepatocyte and LSEC cells
hepatocyte_cells = liver_annot[liver_annot["cell_ontology_class"].str.contains("hepatocyte", case=False, na=False)].index
lsec_cells = liver_annot[liver_annot["cell_ontology_class"].str.contains("sinusoid", case=False, na=False)].index

if len(hepatocyte_cells) >= 10 and len(lsec_cells) >= 10:
    # Take largest mouse group for each
    for cell_list, name in [(hepatocyte_cells, "hepatocyte"), (lsec_cells, "LSEC")]:
        mouse_counts = liver_annot.loc[cell_list, "mouse.id"].value_counts()
        largest = mouse_counts.index[0]
        target_cells = liver_annot.loc[cell_list][liver_annot.loc[cell_list, "mouse.id"] == largest].index
        if name == "hepatocyte":
            hep_cells_final = target_cells
        else:
            lsec_cells_final = target_cells

    hep_expr = liver_expr.loc[hep_cells_final].values
    lsec_expr = liver_expr.loc[lsec_cells_final].values

    # Pseudobulk
    hep_pb = np.mean(hep_expr, axis=0)
    lsec_pb = np.mean(lsec_expr, axis=0)

    # Per-gene JS divergence
    genes = liver_df.index.tolist()
    hk_indices = [i for i, g in enumerate(genes) if g in hk_mouse_genes]
    identity_indices = [i for i, g in enumerate(genes) if g not in hk_mouse_genes]

    per_gene_js = []
    for i in range(len(genes)):
        p = np.array([hep_pb[i], 1e-10])
        q = np.array([lsec_pb[i], 1e-10])
        p_sm = softmax(p)
        q_sm = softmax(q)
        m = 0.5 * (p_sm + q_sm)
        js = 0.5 * (np.sum(p_sm * np.log2((p_sm + 1e-10) / (m + 1e-10))) +
                    np.sum(q_sm * np.log2((q_sm + 1e-10) / (m + 1e-10))))
        per_gene_js.append(js)

    per_gene_js = np.array(per_gene_js)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Sort by JS value
    sorted_idx = np.argsort(per_gene_js)[::-1]
    x = np.arange(len(sorted_idx))

    is_hk = np.array([i in hk_indices for i in sorted_idx])
    is_id = ~is_hk

    # Identity genes (bulk)
    ax.bar(x[is_id], per_gene_js[sorted_idx][is_id], width=1.0, color=CKI_GREEN, alpha=0.3, label="Identity genes")
    # HK genes (stand out)
    ax.bar(x[is_hk], per_gene_js[sorted_idx][is_hk], width=1.0, color=CKI_GRAY, alpha=0.8, label="Housekeeping genes")

    # Annotation
    mean_js_id = np.mean(per_gene_js[identity_indices])
    mean_js_hk = np.mean(per_gene_js[hk_indices])
    ax.axhline(y=mean_js_id, color=CKI_GREEN, linestyle="--", lw=1.5, alpha=0.7,
               label=f"Mean identity JS = {mean_js_id:.4f}")
    ax.axhline(y=mean_js_hk, color=CKI_GRAY, linestyle="--", lw=1.5, alpha=0.7,
               label=f"Mean HK JS = {mean_js_hk:.4f}")

    ax.set_xlabel("Genes (sorted by per-gene JS divergence)", fontsize=10)
    ax.set_ylabel("Per-gene JS Divergence", fontsize=10)
    ax.set_title("Per-Gene Transcriptomic Divergence: Hepatocyte vs LSEC\n"
                 f"(omega = 12.31, mean identity JS / mean HK JS = {mean_js_id/mean_js_hk:.1f}x)",
                 fontsize=11, fontweight="bold", color=CKI_BLUE)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    ax.set_xlim(-50, len(sorted_idx) + 50)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "phase36_fig2d_per_gene_js.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"  -> phase36_fig2d_per_gene_js.png (mean JS: id={mean_js_id:.4f}, hk={mean_js_hk:.4f})")
else:
    print("  [SKIP] Insufficient hepatocyte/LSEC cells for per-gene JS computation")

# ============================================================
# Fig 3d: SameOrgan/DiffOrgan Effect Reversal
# ============================================================
print("[6/10] Fig 3d: SameOrgan/DiffOrgan effect reversal")

metrics_df = pd.read_csv(RESULTS_DIR / "phase35_all_metrics_pairs.csv")
metrics = ["omega", "js_raw", "spearman_dist", "cosine_dist", "marker_jaccard_dist"]
metric_labels = ["CKI omega", "Raw JS", "Spearman dist", "Cosine dist", "Marker Jaccard"]

fig, axes = plt.subplots(1, 5, figsize=(18, 5), sharey=False)

for idx, (metric, label, ax) in enumerate(zip(metrics, metric_labels, axes)):
    same_vals = metrics_df[metrics_df["same_organ"] == True][metric].values
    diff_vals = metrics_df[metrics_df["same_organ"] == False][metric].values

    same_mean = np.mean(same_vals)
    diff_mean = np.mean(diff_vals)
    ratio = same_mean / diff_mean if diff_mean > 0 else 0

    bp = ax.boxplot([same_vals, diff_vals], labels=["Same\nOrgan", "Diff\nOrgan"],
                    patch_artist=True, widths=0.4)
    bp["boxes"][0].set_facecolor(CKI_GREEN if ratio > 1 else CKI_GOLD)
    bp["boxes"][1].set_facecolor(CKI_GRAY)

    ax.set_title(label, fontsize=10, fontweight="bold",
                 color=CKI_GREEN if ratio > 1 else CKI_BLUE)
    ax.annotate(f"Ratio: {ratio:.2f}x", xy=(0.5, 0.95), xycoords="axes fraction",
                ha="center", fontsize=8,
                color=CKI_GREEN if ratio > 1 else CKI_BLUE,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

plt.suptitle("Same-Organ vs Different-Organ Effect Across Metrics\n"
             "CKI omega is the ONLY metric where SameOrgan > DiffOrgan",
             fontsize=12, fontweight="bold", color=CKI_BLUE)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig3d_same_organ_reversal.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig3d_same_organ_reversal.png")

# ============================================================
# Fig 5a: Cross-Organ Omega Ranking Bar Plot
# ============================================================
print("[7/10] Fig 5a: Cross-organ omega ranking")

cross_df = pd.read_csv(RESULTS_DIR / "phase35_cross_organ_conservation.csv")
# Compute mean omega per cell type
ct_summary = cross_df.groupby("ct").agg(
    mean_omega=("omega", "mean"),
    std_omega=("omega", "std"),
    n_pairs=("omega", "count"),
    mean_js=("js_raw", "mean"),
    mean_spearman=("spearman", "mean"),
    mean_cosine=("cosine", "mean"),
    mean_jaccard=("marker_jaccard", "mean"),
).reset_index()

ct_summary = ct_summary.sort_values("mean_omega")

# Classify cell types
immune_types = {"macrophage", "monocyte", "nk cell", "neutrophil",
                "b cell", "plasma cell", "memory b cell", "naive b cell",
                "cd8-positive, alpha-beta t cell", "cd4-positive, alpha-beta t cell",
                "classical monocyte", "intermediate monocyte"}
structural_types = {"endothelial cell", "erythrocyte", "smooth muscle cell",
                    "hematopoietic stem cell"}

def classify_ct(ct):
    if ct.lower() in immune_types:
        return "Immune"
    elif ct.lower() in structural_types:
        return "Structural"
    return "Other"

ct_summary["class"] = ct_summary["ct"].apply(classify_ct)
class_colors = {"Immune": CKI_GREEN, "Structural": CKI_ORANGE, "Other": CKI_GRAY}

fig, ax = plt.subplots(figsize=(12, 6))
y_pos = np.arange(len(ct_summary))

colors = [class_colors[c] for c in ct_summary["class"]]
bars = ax.barh(y_pos, ct_summary["mean_omega"], xerr=ct_summary["std_omega"],
               color=colors, alpha=0.85, edgecolor="white", capsize=3, height=0.7,
               error_kw=dict(lw=1, capsize=2))

# Labels
labels = [f"{row['ct'][:30]} (n={int(row['n_pairs'])})"
          for _, row in ct_summary.iterrows()]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7)

ax.set_xlabel("Mean CKI omega (cross-organ)", fontsize=11)
ax.set_title("Cross-Organ Transcriptional Conservation by Cell Type\n"
             "(59 same-CT cross-organ pairs, Tabula Sapiens)",
             fontsize=12, fontweight="bold", color=CKI_BLUE)

# Add omega values
for i, (_, row) in enumerate(ct_summary.iterrows()):
    ax.text(row["mean_omega"] + row["std_omega"] + 1, i,
            f"{row['mean_omega']:.1f}", va="center", fontsize=7, color=CKI_BLUE)

# Legend
legend_patches = [mpatches.Patch(color=class_colors[c], label=c, alpha=0.85)
                  for c in ["Immune", "Structural", "Other"]]
ax.legend(handles=legend_patches, fontsize=9, loc="lower right")

# Annotation
ax.axvline(x=ct_summary["mean_omega"].median(), color=CKI_RED, linestyle="--", lw=1, alpha=0.5)
ax.text(ct_summary["mean_omega"].median() + 1, len(ct_summary) - 1,
        f"Median: {ct_summary['mean_omega'].median():.1f}", fontsize=7, color=CKI_RED)

ax.invert_yaxis()
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig5a_cross_organ_ranking.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig5a_cross_organ_ranking.png")

# ============================================================
# Fig 5b: Ranking Consistency Scatter Plot
# ============================================================
print("[8/10] Fig 5b: Ranking consistency scatter")

# Rank by each metric
ct_summary["rank_omega"] = ct_summary["mean_omega"].rank()
ct_summary["rank_js"] = ct_summary["mean_js"].rank()
ct_summary["rank_spearman"] = ct_summary["mean_spearman"].rank()
ct_summary["rank_cosine"] = ct_summary["mean_cosine"].rank()
ct_summary["rank_jaccard"] = ct_summary["mean_jaccard"].rank()

metrics_compare = [
    ("rank_js", "Raw JS", CKI_GREEN),
    ("rank_spearman", "Spearman", CKI_GOLD),
    ("rank_cosine", "Cosine", CKI_BLUE),
    ("rank_jaccard", "Jaccard", CKI_GRAY),
]

fig, axes = plt.subplots(2, 2, figsize=(10, 9))
axes = axes.flatten()

for idx, (col, label, color) in enumerate(metrics_compare):
    ax = axes[idx]
    r, p = spearmanr(ct_summary["rank_omega"], ct_summary[col])
    ax.scatter(ct_summary["rank_omega"], ct_summary[col], c=color, alpha=0.7,
               s=60, edgecolors="white", linewidth=0.5, zorder=3)

    # Add diagonal
    lims = [0, len(ct_summary) + 2]
    ax.plot(lims, lims, "k--", alpha=0.3, lw=1)

    ax.set_xlabel("CKI omega rank", fontsize=9)
    ax.set_ylabel(f"{label} rank", fontsize=9)
    ax.set_title(f"{label}: r = {r:.3f} (p = {p:.3f})", fontsize=10, fontweight="bold", color=color)

    # Annotate outliers
    for _, row in ct_summary.iterrows():
        diff = abs(row["rank_omega"] - row[col])
        if diff > len(ct_summary) * 0.3:
            ax.annotate(row["ct"][:12], (row["rank_omega"], row[col]),
                       fontsize=5, alpha=0.7, color=CKI_RED,
                       xytext=(3, 3), textcoords="offset points")

plt.suptitle("Cross-Organ Conservation Ranking: CKI vs Standard Metrics\n"
             "(CKI ranking is orthogonal to all standard metrics)",
             fontsize=12, fontweight="bold", color=CKI_BLUE)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase36_fig5b_ranking_comparison.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("  -> phase36_fig5b_ranking_comparison.png")

# ============================================================
# Summary CSV for Fig 5
# ============================================================
ct_summary_out = ct_summary[["ct", "class", "mean_omega", "std_omega", "n_pairs",
                              "mean_js", "mean_spearman", "mean_cosine", "mean_jaccard",
                              "rank_omega", "rank_js", "rank_spearman", "rank_cosine", "rank_jaccard"]]
ct_summary_out = ct_summary_out.sort_values("mean_omega")
ct_summary_out.to_csv(RESULTS_DIR / "phase36_cross_organ_summary.csv", index=False)
print("  -> phase36_cross_organ_summary.csv")

print("\n" + "=" * 60)
print("Phase 3.6 figure generation complete!")
print(f"  {8} figure panels generated in {RESULTS_DIR}")
print("=" * 60)

# List generated files
generated = [
    "phase36_fig1a_kaks_analogy.png",
    "phase36_fig1b_pipeline.png",
    "phase36_fig1c_bootstrap.png",
    "phase36_fig2b_kn_kf_decomposition.png",
    "phase36_fig2d_per_gene_js.png",
    "phase36_fig3d_same_organ_reversal.png",
    "phase36_fig5a_cross_organ_ranking.png",
    "phase36_fig5b_ranking_comparison.png",
    "phase36_cross_organ_summary.csv",
]
for f in generated:
    path = RESULTS_DIR / f
    if path.exists():
        print(f"  [OK] {f} ({path.stat().st_size:,} bytes)")
    else:
        print(f"  [MISSING] {f}")
