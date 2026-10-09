#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc66: render Supplementary Fig. 17 & 18 (neuron superclass divergence;
program diffuseness + SEA-AD disease anchor).

Palette imitates the first-author v6 re-render (nc63 B2): purple / red /
orange / grey, Arial >= 7pt.
Data sources:
  results/brain_neuron_blockshuffle.csv (+ _null_means.npy)
  results/brain_neuron_superclass_omega.csv
  results/brain_bs_null_observed_pairs.csv
  results/sea_ad_dam_positive_control.csv
  results/brain_hallmark_program_omega.csv
Output: results/figures_v66/Supplementary_Fig_17.pdf, _18.pdf
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
OUT = BASE / "results" / "figures_v66"
OUT.mkdir(parents=True, exist_ok=True)

bs = pd.read_csv(BASE / "results" / "brain_neuron_blockshuffle.csv")
null_means = np.load(BASE / "results" / "brain_neuron_blockshuffle_null_means.npy")
neu = pd.read_csv(BASE / "results" / "brain_neuron_superclass_omega.csv")
non = pd.read_csv(BASE / "results" / "brain_bs_null_observed_pairs.csv")
sea = pd.read_csv(BASE / "results" / "sea_ad_dam_positive_control.csv")
hm = pd.read_csv(BASE / "results" / "brain_hallmark_program_omega.csv")

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

# ================= Fig 17 =================
fig, axes = plt.subplots(1, 3, figsize=(178 * MM, 64 * MM))

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
ax.set_title("Block-shuffle null (B = 1,000)\nred = observed; grey = null", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "a")

# (b) class-median ladder: 3 neuronal superclasses + 10 non-neuronal classes
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
             "Mann\u2013Whitney $P < 10^{-300}$ ($z$ = 52.6)", fontsize=7)
panel_label(ax, "b")

# (c) pair-level ECDF (log x): neurons / non-neurons / astrocytes
ax = axes[2]
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
panel_label(ax, "c")

fig.tight_layout(w_pad=2.0)
fig.savefig(OUT / "Supplementary_Fig_17.pdf")
plt.close(fig)

# ================= Fig 18 =================
fig, axes = plt.subplots(1, 2, figsize=(178 * MM, 66 * MM))

# (a) SEA-AD disease anchor: omega_ad_vs_ctrl vs null per (class, gene set)
ax = axes[0]
sea_sorted = sea.sort_values("omega_ad_vs_ctrl", ascending=True)
yp = np.arange(len(sea_sorted))
POS = {("Astrocyte", "Pan_reactive_astro"), ("Astrocyte", "DAM_core")}
NEG = {("Astrocyte", "Homeostatic_microglia"), ("Microglia-PVM", "A2_astro")}
for y, (_, r) in zip(yp, sea_sorted.iterrows()):
    key = (r["cell_class"], r["gene_set"])
    c = RED if key in POS else (ORANGE if key in NEG else GREY)
    ax.barh(y, r["omega_ad_vs_ctrl"], color=c, height=0.62, edgecolor="none")
    ax.errorbar(r["null_mean"], y,
                xerr=1.96 * r["null_sd"], fmt="none", ecolor=STEEL,
                elinewidth=0.8, capsize=2, zorder=4)
    ax.scatter([r["null_mean"]], [y], marker="|", s=60, color=STEEL, zorder=5)
    ax.text(r["omega_ad_vs_ctrl"] + 0.18, y, f"P = {r['p_emp']:.3f}",
            va="center", fontsize=5.7, color=STEEL)
ax.set_yticks(yp)
ax.set_yticklabels([f"{r['cell_class'].replace('-PVM','')} \u00b7 "
                    f"{r['gene_set'].replace('_astro','').replace('_microglia','')
                     .replace('_core','').replace('_',' ')}"
                    for _, r in sea_sorted.iterrows()], fontsize=5.9)
ax.set_xlabel("\u03c9 (AD-high vs reference donors)")
ax.set_xlim(0, sea["omega_ad_vs_ctrl"].max() * 1.24)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("SEA-AD disease anchor (10 pre-registered tests)\n"
             "bar = observed; | = null mean, 95% range", fontsize=7)
panel_label(ax, "a")

# (b) Hallmark diffuseness: histogram of 400 empirical P + lipid highlight
ax = axes[1]
is_lipid = hm["program"].isin(["Pperoxisome", "Peroxisome",
                               "Bile Acid Metabolism"])
bins = np.linspace(0, 1, 21)
ax.hist(hm.loc[~is_lipid, "p_emp"], bins=bins, color=GREY, alpha=0.8,
        label=f"other programs (n = {int((~is_lipid).sum())})")
ax.hist(hm.loc[is_lipid, "p_emp"], bins=bins, color=PURPLE, alpha=0.9,
        label=f"Peroxisome / Bile Acid (n = {int(is_lipid.sum())})")
exp = len(hm) / 20
ax.axhline(exp, color=STEEL, lw=0.9, ls="--")
ax.text(0.99, exp * 1.25, "uniform expectation (20 per bin)",
        ha="right", fontsize=5.9, color=STEEL)
n_le = int((hm["p_emp"] <= 0.01).sum())
ax.axvline(0.01, color=RED, lw=0.8, ls=":")
ax.text(0.035, ax.get_ylim()[1] * 0.82,
        f"P \u2264 0.01: {n_le} observed\nvs 4.0 expected;\n0/400 survive BH "
        f"(min q = 0.233)", fontsize=6.0, color=RED)
ax.set_xlabel("Empirical $P$ (size-bucketed null, $B$ = 2,000)")
ax.set_ylabel("Tests (of 400)")
ax.set_xlim(0, 1)
ax.legend(loc="upper right", frameon=False, fontsize=5.9)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Hallmark-program diffuseness\n10 classes \u00d7 40 programs", fontsize=7)
panel_label(ax, "b")

fig.tight_layout(w_pad=2.2)
fig.savefig(OUT / "Supplementary_Fig_18.pdf")
plt.close(fig)

print("done:", list(p.name for p in OUT.glob("*.pdf")))
