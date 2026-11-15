"""
nc49_fig_tcga: main figure for the TCGA tissue-level divergence application.

Panel A: pancancer NN/TT omega ratio (forest-style, ranked) with
         sample-level cluster bootstrap 95% CIs + k_n TT/NN mechanism.
Panel B: LUAD per-tumor omega by mutation group (WT/EGFR/KRAS) with
         Kruskal-Wallis / Dunn-Holm annotations; k_f and k_n side panels
         showing the mechanism contrast.

Data: results/nc49_tcga_pancancer.csv, results/nc49_tcga_luad_mutation.csv
      (re-derived per-tumor LUAD stats from tcga_linear_norm_v44_all_pairs.csv)
Style: notebooks/_fig_style.py (NAR/NC double column, 300 dpi).

Output: results/figures_final/nc49_fig_tcga.{pdf,png}
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from scipy.stats import kruskal

from _fig_style import (apply_style, new_figure, save_fig, despine,
                        subtle_grid, add_panel_label, C_BLUE, C_GREEN,
                        C_RED, C_PURPLE, C_GRAY, C_STEEL, C_LIGHT_GRAY,
                        C_AMBER, DOUBLE, SMALL_SIZE, BODY_SIZE)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAN = pd.read_csv(os.path.join(ROOT, "results", "nc49_tcga_pancancer.csv"))
PAIRS = os.path.join(ROOT, "results", "tcga_linear_norm_v44_all_pairs.csv")

# ------------------------------------------------------------------
# Re-derive LUAD per-tumor stats (same logic as nc49_tcga_main.py)
# ------------------------------------------------------------------
import json
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    luad_tt[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby("sample").agg(omega=("omega", "mean"),
                                       kf=("kf", "mean"), kn=("kn", "mean"))
mut = json.load(open(os.path.join(ROOT, "data", "tcga",
                                  "luad_egfr_kras_mutations.json")))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])
def group_of(s):
    e, k = s in egfr, s in kras
    if e and k: return "DOUBLE"
    if e: return "EGFR"
    if k: return "KRAS"
    return "WT"
pt = per_tumor.reset_index()
pt["group"] = pt["sample"].map(group_of)
pt = pt[pt.group != "DOUBLE"]

apply_style()
fig = new_figure(DOUBLE, 96 / 25.4)  # double column, ~96 mm high
gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 1, 1, 1], wspace=0.52,
                      left=0.085, right=0.985, bottom=0.14, top=0.80)

# ================= Panel A: pancancer ranking =================
axA = fig.add_subplot(gs[0, 0])
pan = PAN.sort_values("NN_TT_ratio", ascending=True).reset_index(drop=True)
y = np.arange(len(pan))
labels = [c.replace("TCGA-", "") for c in pan.cancer]

# NN/TT omega ratio with CI
axA.errorbar(pan.NN_TT_ratio, y,
             xerr=[pan.NN_TT_ratio - pan.NN_TT_ratio_CI95_lower,
                   pan.NN_TT_ratio_CI95_upper - pan.NN_TT_ratio],
             fmt="o", color=C_BLUE, ecolor=C_BLUE, elinewidth=1.1,
             capsize=2.5, markersize=4.2, label="ω NN/TT", zorder=3)
# k_n TT/NN mean ratio (mechanism) on secondary x
axA2 = axA.twiny()
axA2.errorbar(pan.kn_TT_NN_mean_ratio, y,
              xerr=[pan.kn_TT_NN_mean_ratio - pan.kn_TT_NN_mean_ratio_CI95_lower,
                    pan.kn_TT_NN_mean_ratio_CI95_upper - pan.kn_TT_NN_mean_ratio],
              fmt="s", color=C_AMBER, ecolor=C_AMBER, elinewidth=1.1,
              capsize=2.5, markersize=3.6, label="$k_n$ TT/NN", zorder=3)
axA2.spines["top"].set_visible(True)
axA2.spines["top"].set_color(C_AMBER)
axA2.spines["right"].set_visible(False)
axA2.set_xlim(0.5, 4.5)
axA.axvline(1.0, color=C_GRAY, linestyle=":", linewidth=0.8, zorder=1)
axA.set_yticks(y)
axA.set_yticklabels(labels)
axA.set_xlim(0.85, 3.15)
axA.set_xlabel("ω ratio NN/TT (means)")
axA.set_ylabel("")
axA.set_title("Pan-cancer reversal", fontsize=9, fontweight="bold", pad=26)
subtle_grid(axA, axis="x")
despine(axA)
axA2.set_xlabel("$k_n$ ratio TT/NN (means)", fontsize=8, color=C_AMBER,
                labelpad=3)
axA2.tick_params(axis="x", colors=C_AMBER, labelsize=SMALL_SIZE)
h1, l1 = axA.get_legend_handles_labels()
h2, l2 = axA2.get_legend_handles_labels()
axA.legend(h1 + h2, l1 + l2, loc="lower right", frameon=False,
           fontsize=SMALL_SIZE)
add_panel_label(fig, axA, "A", x=-0.30, y=1.30)

# ================= Panel B: LUAD omega by mutation group ==========
GROUPS = ["WT", "EGFR", "KRAS"]
GCOL = {"WT": C_STEEL, "EGFR": C_PURPLE, "KRAS": C_RED}
pos = {g: i for i, g in enumerate(GROUPS)}

def group_boxes(ax, metric, ylabel, title, sci=False):
    data = [pt.loc[pt.group == g, metric].values for g in GROUPS]
    bp = ax.boxplot(data, positions=range(3), widths=0.55,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color="white", linewidth=1.0),
                    whiskerprops=dict(color=C_GRAY, linewidth=0.7),
                    capprops=dict(color=C_GRAY, linewidth=0.7))
    for patch, g in zip(bp["boxes"], GROUPS):
        patch.set_facecolor(GCOL[g])
        patch.set_alpha(0.75)
        patch.set_edgecolor(C_GRAY)
    # jittered points
    rng = np.random.default_rng(7)
    for i, g in enumerate(GROUPS):
        vals = pt.loc[pt.group == g, metric].values
        xj = rng.uniform(i - 0.22, i + 0.22, len(vals))
        ax.scatter(xj, vals, s=2.0, color=GCOL[g], alpha=0.35, linewidths=0,
                   zorder=3)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{g}\n(n={sum(pt.group == g)})" for g in GROUPS])
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=9, fontweight="bold")
    subtle_grid(ax, axis="y")
    despine(ax)

axB = fig.add_subplot(gs[0, 1])
group_boxes(axB, "omega", "Per-tumor ω",
            "LUAD ω by driver")
# significance brackets (Dunn-Holm from nc49_tcga_luad_mutation.csv)
ymax = pt.omega.max()
span = ymax - pt.omega.min()
def bracket(ax, x1, x2, y, text):
    ax.plot([x1, x1, x2, x2], [y, y + 0.02 * span, y + 0.02 * span, y],
            color=C_GRAY, linewidth=0.7)
    ax.text((x1 + x2) / 2, y + 0.03 * span, text, ha="center", va="bottom",
            fontsize=SMALL_SIZE)
bracket(axB, 0, 2, ymax * 1.02, "P$_{Holm}$ = 3.6×10$^{-7}$")
bracket(axB, 1, 2, ymax * 1.15, "P$_{Holm}$ = 0.008")
axB.set_ylim(top=ymax * 1.30)
axB.text(0.02, 0.66, "KW P = 7.8×10$^{-7}$", transform=axB.transAxes,
         fontsize=SMALL_SIZE, va="top")
add_panel_label(fig, axB, "B", x=-0.40, y=1.30)

# Panel C: k_f (functional component)
axC = fig.add_subplot(gs[0, 2])
group_boxes(axC, "kf", "Per-tumor $k_f$", "$k_f$ component")
axC.text(0.02, 0.98, "KW P = 0.015\nKRAS>EGFR\nP$_{Holm}$ = 0.015",
         transform=axC.transAxes, fontsize=SMALL_SIZE, va="top")
add_panel_label(fig, axC, "C", x=-0.40, y=1.30)

# Panel D: k_n (baseline component)
axD = fig.add_subplot(gs[0, 3])
group_boxes(axD, "kn", "Per-tumor $k_n$", "$k_n$ baseline")
axD.text(0.02, 0.98, "KW P = 3.4×10$^{-4}$\nWT>KRAS\nP$_{Holm}$ = 4.2×10$^{-4}$",
         transform=axD.transAxes, fontsize=SMALL_SIZE, va="top")
add_panel_label(fig, axD, "D", x=-0.40, y=1.30)

save_fig(fig, "nc49_fig_tcga")
print("DONE nc49_fig_tcga")
