# nc50: Supplementary Fig. 14 - independent human-brain microglia validation
# Panel A: omega distributions (functional vs neutral half-splits per cell type)
# Panel B: per-metric AUC (functional > neutral), exact rank AUC
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                     "axes.linewidth": 0.6, "pdf.fonttype": 42})

df = pd.read_csv(r"results/nc50_brain_atlas_microglia.csv")
func = df[df.pair_class == "functional"]
nm = df[df.pair_class == "neutral_microglial cell"]
nc = df[df.pair_class == "neutral_central nervous system macrophage"]

METRICS = ["omega", "k_n", "k_f", "raw_js", "cosine", "spearman", "jaccard"]
LABELS = ["CKI \u03c9", "k_n", "k_f", "Raw JS", "Cosine", "Spearman", "Jaccard"]
neut = df[df.pair_class != "functional"]

aucs = {}
for mc in METRICS:
    f, n = func[mc].values, neut[mc].values
    ranks = pd.Series(np.concatenate([f, n])).rank().values[: len(f)]
    aucs[mc] = (ranks.sum() - len(f) * (len(f) + 1) / 2) / (len(f) * len(n))

fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5),
                         gridspec_kw={"width_ratios": [1.15, 1.0]})
INK, BLUE, TEAL, AMBER = "#1a1a1a", "#2f6fb2", "#1f9e8e", "#d9a021"

ax = axes[0]
groups = [func["omega"].values, nm["omega"].values, nc["omega"].values]
labels = [f"Functional\nmicroglia vs CNS-M\u03c6\n(n = {len(func)})",
          f"Neutral self-split\nmicroglia (n = {len(nm)})",
          f"Neutral self-split\nCNS-M\u03c6 (n = {len(nc)})"]
cols = [BLUE, TEAL, AMBER]
bp = ax.boxplot(groups, widths=0.5, showfliers=False, patch_artist=True,
                medianprops=dict(color=INK, lw=1.0),
                whiskerprops=dict(color=INK, lw=0.6),
                capprops=dict(color=INK, lw=0.6),
                boxprops=dict(lw=0.6))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.35)
rng = np.random.default_rng(42)
for i, (g, c) in enumerate(zip(groups, cols)):
    ax.scatter(np.full(len(g), i + 1) + rng.uniform(-0.12, 0.12, len(g)), g,
               s=4, color=c, alpha=0.85, lw=0, zorder=3)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(labels, fontsize=6)
ax.set_ylabel("CKI \u03c9 (HVG scheme)")
ax.set_title("A", loc="left", fontweight="bold", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

ax = axes[1]
x = np.arange(len(METRICS))
vals = [aucs[m] for m in METRICS]
barcols = [BLUE if m in ("omega", "k_n", "k_f") else "#8a8a8a" for m in METRICS]
ax.bar(x, vals, width=0.62, color=barcols, lw=0)
for xi, v in zip(x, vals):
    ax.text(xi, v + 0.02, f"{v:.2f}" if v < 1 else "1.00", ha="center", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels(LABELS, rotation=32, ha="right", fontsize=6)
ax.set_ylim(0, 1.18); ax.set_ylabel("AUC (functional > neutral)")
ax.axhline(0.5, color=INK, lw=0.6, ls="--")
ax.set_title("B", loc="left", fontweight="bold", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(r"results/Supplementary_Fig_14.pdf", dpi=300)
print("saved results/Supplementary_Fig_14.pdf")
