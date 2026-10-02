# nc58: Supplementary Fig. 3 - independent human-brain microglia validation
# (renumbered from SF14; UMAP panel added per first-author v5 feedback [12])
# Panel a: UMAP embedding (precomputed X_UMAP), coloured by cell type
# Panel b: omega distributions (functional vs neutral half-splits per cell type)
# Panel c: per-metric AUC (functional > neutral), exact rank AUC
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                     "axes.linewidth": 0.6, "pdf.fonttype": 42})

INK, BLUE, TEAL, AMBER = "#1a1a1a", "#2f6fb2", "#1f9e8e", "#d9a021"

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

# --- UMAP coordinates (precomputed in the CELLxGENE h5ad) ---
import anndata as ad
a = ad.read_h5ad(r"data/human_brain_atlas_microglia.h5ad", backed="r")
umap = a.obsm["X_UMAP"][:]
ctype = a.obs["cell_type"].astype(str).values
is_mg = ctype == "microglial cell"
n_mg, n_cm = int(is_mg.sum()), int((~is_mg).sum())
a.file.close()

fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5),
                         gridspec_kw={"width_ratios": [1.0, 1.15, 1.0]})

# --- panel a: UMAP ---
ax = axes[0]
rng = np.random.default_rng(42)
idx_mg = np.where(is_mg)[0]
idx_cm = np.where(~is_mg)[0]
ax.scatter(umap[idx_mg, 0], umap[idx_mg, 1], s=0.15, color=BLUE, alpha=0.25,
           lw=0, rasterized=True)
ax.scatter(umap[idx_cm, 0], umap[idx_cm, 1], s=0.8, color=AMBER, alpha=0.9,
           lw=0, rasterized=True)
ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
ax.set_xlabel("UMAP 1"); ax.set_ylabel("UMAP 2")
handles = [Line2D([], [], marker="o", ls="", color=BLUE, markersize=3.5,
                  label=f"microglial cell (n = {n_mg:,})"),
           Line2D([], [], marker="o", ls="", color=AMBER, markersize=3.5,
                  label=f"CNS-M\u03c6 (n = {n_cm:,})")]
ax.legend(handles=handles, loc="upper right", fontsize=5.2, frameon=False,
          handletextpad=0.1, borderaxespad=0.1)
ax.set_title("A", loc="left", fontweight="bold", fontsize=9)
for sp in ax.spines.values():
    sp.set_visible(True)

# --- panel b: omega distributions ---
ax = axes[1]
groups = [func["omega"].values, nm["omega"].values, nc["omega"].values]
labels = [f"Functional\nmicroglia vs\nCNS-M\u03c6 (n = {len(func)})",
          f"Neutral\nmicroglia\nself-split (n = {len(nm)})",
          f"Neutral\nCNS-M\u03c6\nself-split (n = {len(nc)})"]
cols = [BLUE, TEAL, AMBER]
bp = ax.boxplot(groups, widths=0.5, showfliers=False, patch_artist=True,
                medianprops=dict(color=INK, lw=1.0),
                whiskerprops=dict(color=INK, lw=0.6),
                capprops=dict(color=INK, lw=0.6),
                boxprops=dict(lw=0.6))
for patch, c in zip(bp["boxes"], cols):
    patch.set_facecolor(c); patch.set_alpha(0.35)
for i, (g, c) in enumerate(zip(groups, cols)):
    ax.scatter(np.full(len(g), i + 1) + rng.uniform(-0.12, 0.12, len(g)), g,
               s=4, color=c, alpha=0.85, lw=0, zorder=3)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(labels, fontsize=6)
ax.set_ylabel("CKI \u03c9 (HVG scheme)")
ax.set_title("B", loc="left", fontweight="bold", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

# --- panel c: per-metric AUC ---
ax = axes[2]
x = np.arange(len(METRICS))
vals = [aucs[m] for m in METRICS]
barcols = [BLUE if m in ("omega", "k_n", "k_f") else "#8a8a8a" for m in METRICS]
ax.bar(x, vals, width=0.62, color=barcols, lw=0)
for xi, v in zip(x, vals):
    ax.text(xi, v + 0.02, f"{v:.2f}" if v < 1 else "1.00", ha="center", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels(LABELS, rotation=32, ha="right", fontsize=6)
ax.set_ylim(0, 1.18); ax.set_ylabel("AUC (functional > neutral)")
ax.axhline(0.5, color=INK, lw=0.6, ls="--")
ax.set_title("C", loc="left", fontweight="bold", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(r"results/Supplementary_Fig_3.pdf", dpi=300)
print("saved results/Supplementary_Fig_3.pdf")
