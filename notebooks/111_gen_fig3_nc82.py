#!/usr/bin/env python3
"""nc82 (P1-12): rebuild figure 3 as a single-panel NN/TT ratio plot and move
the LUAD driver-mutation stratification to Supplementary Fig. 10.

Content change per the 2026-11-17 figure policy: panel composition changes
(old figure 3 carried panels a-d; the new main figure keeps only the NN/TT
panel, and the KRAS stratification becomes a supplementary figure).

Data sources (all live, with assertions against the authoritative tables):
  * results/nc52_tcga_pancancer_excc.csv        -> figure 3 (NN/TT + k_n ratios)
  * results/tcga_linear_norm_v44_TCGA-LUAD_pairs.csv
    + data/tcga/luad_egfr_kras_mutations.json   -> Supplementary Fig. 10
  * results/nc49_tcga_luad_mutation.csv         -> test statistics (assertions)

Outputs: results/figures_nc82/figure3.pdf/.png,
         results/figures_nc82/Supplementary_Fig_10.pdf/.png
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fig_style import (new_figure, save_fig, despine, subtle_grid,
                        add_panel_label, C_BLUE, C_AMBER, C_GREEN,
                        C_GRAY, C_DARK, C_LIGHT_GRAY,
                        BODY_SIZE, SMALL_SIZE, TITLE_SIZE, MM)

# any text containing mathtext superscripts must be >= 10 pt so that the
# exponent (0.7x base) still clears the 7 pt floor
MTEXT_SIZE = 10

BASE = Path(__file__).resolve().parent.parent
RES = BASE / "results"
OUT = RES / "figures_nc82"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 1. figure 3: pan-cancer NN/TT omega ratio + k_n TT/NN ratio
# --------------------------------------------------------------------------
pc = pd.read_csv(RES / "nc52_tcga_pancancer_excc.csv")
pc["cancer"] = pc["cancer"].str.replace("TCGA-", "", regex=False)
pc = pc.sort_values("NN_TT_ratio", ascending=False).reset_index(drop=True)

# --- assertions against Supplementary Table 5 (authoritative) --------------
exp_ratio = {"LUAD": 2.464, "KIRC": 1.88, "LUSC": 1.71, "BRCA": 1.57, "LIHC": 1.112}
exp_kn = {"LUAD": 2.55, "KIRC": 3.29, "LUSC": 1.89, "BRCA": 2.27, "LIHC": 1.34}
assert list(pc["cancer"]) == ["LUAD", "KIRC", "LUSC", "BRCA", "LIHC"], pc["cancer"].tolist()
for _, r in pc.iterrows():
    c = r["cancer"]
    assert abs(r["NN_TT_ratio"] - exp_ratio[c]) < 0.01, (c, r["NN_TT_ratio"])
    assert abs(r["kn_TT_NN_mean_ratio"] - exp_kn[c]) < 0.01, (c, r["kn_TT_NN_mean_ratio"])

x = np.arange(len(pc))
fig = new_figure(114 * MM, 80 * MM)
ax = fig.add_axes([0.14, 0.15, 0.60, 0.78])
ax2 = ax.twinx()

bars = ax.bar(x - 0.11, pc["NN_TT_ratio"], width=0.34, color=C_BLUE, alpha=0.88,
              zorder=3, label="NN/TT \u03c9 (left)")
ax.errorbar(x - 0.11, pc["NN_TT_ratio"],
            yerr=[pc["NN_TT_ratio"] - pc["NN_TT_ratio_CI95_lower"],
                  pc["NN_TT_ratio_CI95_upper"] - pc["NN_TT_ratio"]],
            fmt="none", ecolor=C_DARK, elinewidth=0.8, capsize=2.2, zorder=4)
ax.axhline(1.0, color=C_GRAY, lw=0.8, ls=":", zorder=2)
ax.text(-0.45, 1.06, "ratio = 1", fontsize=SMALL_SIZE, color=C_GRAY,
        va="bottom", ha="left",
        bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none"))

ax2.errorbar(x + 0.17, pc["kn_TT_NN_mean_ratio"],
             yerr=[pc["kn_TT_NN_mean_ratio"] - pc["kn_TT_NN_mean_ratio_CI95_lower"],
                   pc["kn_TT_NN_mean_ratio_CI95_upper"] - pc["kn_TT_NN_mean_ratio"]],
             fmt="D", color=C_AMBER, markersize=3.4, elinewidth=0.8,
             ecolor=C_AMBER, capsize=2.2, lw=0, zorder=4,
             label="k_n TT/NN (right)")

ax.set_xticks(x)
ax.set_xticklabels(pc["cancer"])
ax.set_ylabel("NN/TT ratio of \u03c9", fontsize=BODY_SIZE)
ax.set_ylim(0, 3.4)
ax2.set_ylabel("k_n TT/NN ratio", fontsize=BODY_SIZE, color=C_AMBER)
ax2.set_ylim(0, 4.6)
ax2.tick_params(axis="y", colors=C_AMBER)
ax2.spines["right"].set_visible(True)
ax2.spines["right"].set_color(C_AMBER)
ax.set_xlabel("Cancer type (ranked by NN/TT \u03c9)", fontsize=BODY_SIZE)
despine(ax)
ax2.spines["top"].set_visible(False)
subtle_grid(ax, axis="y")

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=SMALL_SIZE,
          handlelength=1.4, borderpad=0.3, labelspacing=0.25)

paths = save_fig(fig, "figure3", out_dir=OUT)
for p in paths:
    print("wrote", p)

# --------------------------------------------------------------------------
# 2. Supplementary Fig. 10: LUAD driver stratification (omega, k_f, k_n)
# --------------------------------------------------------------------------
pairs = pd.read_csv(RES / "tcga_linear_norm_v44_TCGA-LUAD_pairs.csv")
tt = pairs[pairs.pair_type == "TT"]
mut = json.load(open(BASE / "data" / "tcga" / "luad_egfr_kras_mutations.json"))
egfr = {s[:12] for s in mut["egfr_samples"]}
kras = {s[:12] for s in mut["kras_samples"]}
dbl = {s[:12] for s in mut["double_mutants"]}

_a = tt[["sample_a", "omega_raw", "kf", "kn"]].rename(columns={"sample_a": "s"})
_b = tt[["sample_b", "omega_raw", "kf", "kn"]].rename(columns={"sample_b": "s"})
pt = pd.concat([_a, _b]).groupby("s").mean()

def _grp(s):
    p = s[:12]
    if p in dbl:
        return "DOUBLE"
    if p in kras:
        return "KRAS"
    if p in egfr:
        return "EGFR"
    return "WT"

pt["group"] = [_grp(s) for s in pt.index]
pt = pt[pt.group != "DOUBLE"]

# --- assertions against Supplementary Table 6a (authoritative) -------------
exp_n = {"WT": 311, "EGFR": 61, "KRAS": 120}
exp_m = {"WT": (115.3734, 0.2814, 0.0032),
         "EGFR": (122.2156, 0.2732, 0.0028),
         "KRAS": (136.9436, 0.2919, 0.0027)}
for g in ("WT", "EGFR", "KRAS"):
    sub = pt[pt.group == g]
    assert len(sub) == exp_n[g], (g, len(sub))
    eo, ef, en = exp_m[g]
    assert abs(sub["omega_raw"].mean() - eo) < 5e-3, (g, sub["omega_raw"].mean())
    assert abs(sub["kf"].mean() - ef) < 5e-5, (g, sub["kf"].mean())
    assert abs(sub["kn"].mean() - en) < 5e-5, (g, sub["kn"].mean())

# test statistics from the authoritative file
tm = pd.read_csv(RES / "nc49_tcga_luad_mutation.csv")
def _p(metric, comparison):
    row = tm[(tm.metric == metric) & (tm.test == "Dunn (Holm)") &
             (tm.comparison == comparison)]
    assert len(row) == 1, (metric, comparison)
    return float(row.iloc[0]["p"])

def _kw(metric):
    row = tm[(tm.metric == metric) & (tm.test == "Kruskal-Wallis")]
    assert len(row) == 1
    return float(row.iloc[0]["p"])

kw_omega = _kw("LUAD_omega")
assert abs(kw_omega - 7.8325e-07) < 1e-10, kw_omega
# cross-check with a live Kruskal-Wallis on the aggregated data
from scipy.stats import kruskal
_kw_live = kruskal(*[pt.loc[pt.group == g, "omega_raw"] for g in ("WT", "EGFR", "KRAS")]).pvalue
assert abs(_kw_live - kw_omega) / kw_omega < 0.01, (_kw_live, kw_omega)

GROUPS = ["WT", "EGFR", "KRAS"]
GCOLOR = {"WT": C_GRAY, "EGFR": C_GREEN, "KRAS": C_AMBER}

def _fmt_p(p):
    """Mathtext so that the superscript minus is rendered (Arial lacks U+207B)."""
    if p < 1e-3:
        m, e = f"{p:.1e}".split("e")
        e = int(e)
        return rf"${m}\times10^{{{e}}}$"
    if p < 0.1:
        return f"{p:.3f}"
    return f"{p:.2f}"

panels = [
    ("a", "omega_raw", "Per-tumor \u03c9", "LUAD_omega", False),
    ("b", "kf", "Per-tumor k_f", "LUAD_kf", False),
    ("c", "kn", "Per-tumor k_n", "LUAD_kn", True),
]

fig = new_figure(178 * MM, 62 * MM)
axes = [fig.add_axes([0.075 + i * 0.32, 0.17, 0.25, 0.66]) for i in range(3)]
rng = np.random.default_rng(42)

for ax, (letter, col, ylabel, metric, sci) in zip(axes, panels):
    data = [pt.loc[pt.group == g, col].values for g in GROUPS]
    bp = ax.boxplot(data, positions=[0, 1, 2], widths=0.52, showfliers=False,
                    medianprops=dict(color=C_DARK, lw=1.1),
                    boxprops=dict(lw=0.7), whiskerprops=dict(lw=0.7),
                    capprops=dict(lw=0.7), patch_artist=True)
    for patch, g in zip(bp["boxes"], GROUPS):
        patch.set_facecolor(GCOLOR[g])
        patch.set_alpha(0.35)
    for i, (vals, g) in enumerate(zip(data, GROUPS)):
        ax.scatter(i + rng.uniform(-0.13, 0.13, len(vals)), vals,
                   s=2.0, color=GCOLOR[g], alpha=0.55, zorder=3,
                   edgecolors="none")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([f"{g}\n(n = {len(v)})" for g, v in zip(GROUPS, data)],
                       fontsize=SMALL_SIZE)
    ax.set_ylabel(ylabel, fontsize=BODY_SIZE)
    despine(ax)
    subtle_grid(ax, axis="y")
    add_panel_label(fig, ax, f"({letter})", x=-0.30, y=1.10)
    kw = _kw(metric)
    # mathtext exponents render at 0.7x the base size; for the exponent to
    # clear the 7 pt floor the base must be >= 10 pt (see figure4 lessons).
    ax.set_title(f"KW $P$ = {_fmt_p(kw)}", fontsize=MTEXT_SIZE,
                 fontweight="normal", pad=5)

# Dunn-Holm brackets on panel a
ax = axes[0]
y_top = pt["omega_raw"].max() * 1.02
brackets = [(0, 2, _p("LUAD_omega", "WT vs KRAS")),
            (1, 2, _p("LUAD_omega", "EGFR vs KRAS")),
            (0, 1, _p("LUAD_omega", "WT vs EGFR"))]
ys = [y_top * 1.08, y_top * 1.22, y_top * 1.36]
for (i, j, p), yy in zip(brackets, ys):
    ax.plot([i, i, j, j], [yy - y_top * 0.02, yy, yy, yy - y_top * 0.02],
            color=C_DARK, lw=0.6, clip_on=False)
    ax.text((i + j) / 2, yy + y_top * 0.012, _fmt_p(p),
            ha="center", va="bottom", fontsize=MTEXT_SIZE)
ax.set_ylim(None, y_top * 1.52)

paths = save_fig(fig, "Supplementary_Fig_10", out_dir=OUT)
for p in paths:
    print("wrote", p)

print("nc82 fig3 rebuild: all assertions passed.")
