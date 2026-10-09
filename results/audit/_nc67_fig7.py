#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc67: render main Figure 7 (neuronal superclass regional divergence) and the
re-rendered Supplementary Fig. 17 (pair-level distributions + subcluster tier).

Promotes the strongest offensive result of the manuscript into a main figure:
  Fig. 7  (a) block-shuffle null vs observed per superclass (violins)
          (b) median pair-omega ladder: 3 neuronal superclasses + 10 non-neuronal classes
  Supp Fig 17 (a) pair-level ECDF (log x): neurons / non-neurons ex-astro / astrocytes
               (b) subcluster-tier boxplots per superclass vs superclass medians

Palette matches the first-author v6 re-render (nc63 B2 / nc66): purple / red /
grey, Arial >= 7pt.
Data: results/brain_neuron_blockshuffle.csv (+ _null_means.npy),
      results/brain_neuron_superclass_omega.csv,
      results/brain_neuron_subcluster_omega.csv,
      results/brain_bs_null_observed_pairs.csv
Output: results/figures_v67/figure7.pdf, Supplementary_Fig_17.pdf
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
OUT = BASE / "results" / "figures_v67"
OUT.mkdir(parents=True, exist_ok=True)

bs = pd.read_csv(BASE / "results" / "brain_neuron_blockshuffle.csv")
null_means = np.load(BASE / "results" / "brain_neuron_blockshuffle_null_means.npy")
neu = pd.read_csv(BASE / "results" / "brain_neuron_superclass_omega.csv")
sub = pd.read_csv(BASE / "results" / "brain_neuron_subcluster_omega.csv")
non = pd.read_csv(BASE / "results" / "brain_bs_null_observed_pairs.csv")

PURPLE = "#7d3c98"
RED = "#c0392b"
ORANGE = "#e67e22"
GREY = "#95a5a6"
DGREY = "#5d6d7e"
STEEL = "#2e4053"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 7,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "pdf.fonttype": 42,
})

MM = 1 / 25.4


def panel_label(ax, s):
    ax.text(-0.16, 1.04, s, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="top")


SHORT = {
    "MGE interneuron": "MGE int.",
    "Thalamic excitatory": "Thalamic exc.",
    "Upper-layer intratelencephalic": "Upper-layer IT",
    "Astrocyte": "Astrocyte",
    "Oligodendrocyte precursor": "OPC",
    "Choroid plexus": "Choroid plex.",
    "Oligodendrocyte": "Oligodendr.",
    "Committed oligodendrocyte precursor": "COP",
    "Microglia": "Microglia",
    "Ependymal": "Ependymal",
    "Fibroblast": "Fibroblast",
    "Vascular": "Vascular",
    "Bergmann glia": "Bergmann glia",
}

# ================= Figure 7 (main) =================
fig, axes = plt.subplots(1, 2, figsize=(178 * MM, 70 * MM),
                         gridspec_kw={"width_ratios": [1, 1.25]})

# (a) block-shuffle null vs observed per superclass
ax = axes[0]
order = list(bs["supercluster"])
top = max(float(null_means.max()), float(bs["omega_mean"].max()))
for i, name in enumerate(order):
    nm = null_means[i]
    vp = ax.violinplot([nm], positions=[i], widths=0.7, showextrema=False)
    for b in vp["bodies"]:
        b.set_facecolor(GREY)
        b.set_alpha(0.65)
        b.set_edgecolor("none")
    ax.scatter([i], [nm.mean()], marker="_", s=90, color=STEEL, lw=1.2, zorder=3)
    row = bs[bs["supercluster"] == name].iloc[0]
    ax.scatter([i], [row["omega_mean"]], marker="o", s=18, color=RED, zorder=4)
    p = row["p_value"]
    plab = f"P = {p:.3f}" if p >= 0.001 else "P < 0.001"
    ax.text(i, top * 1.06, plab, ha="center", fontsize=6.2, color=STEEL)
ax.set_xticks(range(len(order)))
ax.set_xticklabels([SHORT[n] for n in order], fontsize=6.4)
ax.set_ylabel("Mean regional \u03c9")
ax.set_ylim(0, top * 1.16)
ax.set_title("Block-shuffle null (B = 1,000)\nred = observed; grey = null",
             fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "a")

# (b) median ladder: 3 neuronal + 10 non-neuronal classes
ax = axes[1]
med_neu = neu.groupby("supercluster")["omega"].median()
med_non = non.groupby("cell_type")["omega"].median()
rows = ([(SHORT[n], v, PURPLE) for n, v in med_neu.items()]
        + [(SHORT[n], v, RED if n == "Astrocyte" else GREY)
           for n, v in med_non.items()])
rows.sort(key=lambda r: r[1])
yp = np.arange(len(rows))
ax.barh(yp, [r[1] for r in rows],
        color=[r[2] for r in rows], height=0.66, edgecolor="none")
for y, (_, v, c) in zip(yp, rows):
    ax.text(v + 1.2, y, f"{v:.1f}", va="center", fontsize=5.9, color=STEEL)
ax.set_yticks(yp)
ax.set_yticklabels([r[0] for r in rows], fontsize=6.0)
ax.set_xlabel("Median pair \u03c9")
ax.set_xlim(0, max(r[1] for r in rows) * 1.22)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Neuronal superclasses vs non-neuronal classes\n"
             "Mann\u2013Whitney $P < 10^{-300}$ ($z$ = 52.6); "
             "astrocytes sole exception", fontsize=7)
panel_label(ax, "b")

fig.tight_layout(w_pad=2.0)
fig.savefig(OUT / "figure7.pdf")
plt.close(fig)

# ================= Supplementary Fig 17 (re-rendered) =================
fig, axes = plt.subplots(1, 2, figsize=(178 * MM, 64 * MM))

# (a) pair-level ECDF (log x)
ax = axes[0]
vals = {
    "Neuronal superclasses (n = 2,995)": (neu["omega"].values, PURPLE),
    "Non-neuronal, ex-astrocyte (n = 25,986)":
        (non[non["cell_type"] != "Astrocyte"]["omega"].values, GREY),
    "Astrocytes (n = 5,778)": (non[non["cell_type"] == "Astrocyte"]["omega"].values, RED),
}
for lab, (v, c) in vals.items():
    xs = np.sort(v)
    ys = np.arange(1, len(xs) + 1) / len(xs)
    ax.plot(xs, ys, color=c, lw=1.1, label=lab)
ax.set_xscale("log")
ax.set_xlabel("Pair \u03c9 (log scale)")
ax.set_ylabel("ECDF")
ax.set_ylim(0, 1)
ax.legend(loc="lower right", frameon=False, fontsize=5.9)
ax.set_title("Pair-level distributions\nmedians 62.2 / 24.5 / 73.4", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "a")

# (b) subcluster tier boxplots per superclass + superclass medians
ax = axes[1]
order = list(bs["supercluster"])
data = [sub[sub["supercluster"] == s]["omega"].values for s in order]
bp = ax.boxplot(data, positions=range(3), widths=0.55, showfliers=False,
                patch_artist=True, medianprops=dict(color=STEEL, lw=1.0),
                whiskerprops=dict(color=DGREY, lw=0.7),
                capprops=dict(color=DGREY, lw=0.7),
                boxprops=dict(facecolor=GREY, alpha=0.55, edgecolor=DGREY,
                              lw=0.6))
for i, s in enumerate(order):
    sc_med = float(neu[neu["supercluster"] == s]["omega"].median())
    ax.hlines(sc_med, i - 0.32, i + 0.32, color=PURPLE, lw=1.6, zorder=4)
    n = len(data[i])
    ax.text(i, ax.get_ylim()[1] if False else np.max(data[i]) * 1.45,
            f"n = {n:,}\nmedians {np.median(data[i]):.1f} / {sc_med:.1f}",
            ha="center", fontsize=5.9, color=STEEL, va="bottom")
ax.set_yscale("log")
ax.set_xticks(range(3))
ax.set_xticklabels([SHORT[n] for n in order], fontsize=6.4)
ax.set_ylabel("Pair \u03c9 (log scale)")
ax.set_ylim(0.5, 3000)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Subcluster tier (grey boxes) vs superclass median\n"
             "(purple bars); subcluster pairs dominated by "
             "region-restricted clusters", fontsize=7)
panel_label(ax, "b")

fig.tight_layout(w_pad=2.2)
fig.savefig(OUT / "Supplementary_Fig_17.pdf")
plt.close(fig)

print("done:", list(p.name for p in OUT.glob("*.pdf")))
