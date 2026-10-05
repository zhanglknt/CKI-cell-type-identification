#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc63 B2: render Supplementary Fig. 15 & 16 (lineage-distance validation across atlases).

Palette imitates the first-author v6 re-render: purple / red / orange / grey, Arial >= 7pt.
Data sources: results/nc61_lineage_stats.json, results/nc62_brain_lineage_stats.json,
results/nc61_lineage_distance.csv (dist-0 anchors), results/nc62_brain_lineage_pairs.csv.
Output: version3-stage PDFs -> results/figures_v63_b2/Supplementary_Fig_15.pdf, _16.pdf
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
OUT = BASE / "results" / "figures_v63_b2"
OUT.mkdir(parents=True, exist_ok=True)

S61 = json.load(open(BASE / "results" / "nc61_lineage_stats.json"))
S62 = json.load(open(BASE / "results" / "nc62_brain_lineage_stats.json"))

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
    ax.text(-0.16, 1.04, s, transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")


# ---------------- Fig 15 ----------------
fig, axes = plt.subplots(1, 3, figsize=(178 * MM, 62 * MM))

# (a) TS six-rung ladder
ax = axes[0]
bins = ["0", "1-2", "3-4", "5-6", "7-8", "9+"]
b61 = S61["same_organ_diff_ct"]["dist_bins"]
vals = [None] + [b["kf_median"] for b in b61]
ns = [None] + [b["n"] for b in b61]
# dist-0 anchor: same CL term across organs, non-ambiguous (n=69, median 0.1062)
d61 = pd.read_csv(BASE / "results" / "nc61_lineage_distance.csv")
d0 = d61[(d61["cl_dist"] == 0) & (~d61["same_organ"]) & (~d61["ambiguous"])]
vals[0] = float(d0["kf"].median())
ns[0] = int(len(d0))
colors = [GREY] + [PURPLE] * 5
bars = ax.bar(range(6), vals, color=colors, width=0.68, edgecolor="none")
for i, (v, n) in enumerate(zip(vals, ns)):
    ax.text(i, v + 0.006, f"{v:.3f}", ha="center", fontsize=6.4, color=STEEL)
    ax.text(i, 0.008, f"n={n}", ha="center", fontsize=5.8, color="white", rotation=90)
ax.set_xticks(range(6))
ax.set_xticklabels(bins)
ax.set_xlabel("CL lineage distance bin")
ax.set_ylabel("Median $k_f$")
ax.set_ylim(0, 0.31)
ax.set_title("Cross-organ (Tabula Sapiens)\n" + r"$\rho$ = 0.227, $P$ = 9.5$\times$10$^{-14}$; permutation $P$ = 1$\times$10$^{-4}$", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "a")

# (b) Brain binned trend (honest: not monotone)
ax = axes[1]
b62 = S62["same_region_diff_ct"]["dist_bins"]
bins2 = [b["bin"].replace("9-40", "9+") for b in b62]
vals2 = [b["kf_fixed_median"] for b in b62]
ns2 = [b["n"] for b in b62]
ax.bar(range(5), vals2, color=RED, width=0.68, edgecolor="none")
for i, (v, n) in enumerate(zip(vals2, ns2)):
    ax.text(i, v + 0.0035, f"{v:.3f}", ha="center", fontsize=6.4, color=STEEL)
    ax.text(i, 0.004, f"n={n}", ha="center", fontsize=5.8, color="white", rotation=90)
ax.set_xticks(range(5))
ax.set_xticklabels(bins2)
ax.set_xlabel("CL lineage distance bin")
ax.set_ylabel("Median $k_f$ (fixed 5,000-gene panel)")
ax.set_ylim(0, 0.158)
ax.set_title("Cross-region (Siletti brain)\n" + r"$\rho$ = 0.181, $P$ = 9.9$\times$10$^{-13}$; permutation $P$ = 1$\times$10$^{-4}$", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "b")

# (c) Oligo chain per-region paired lines
ax = axes[2]
pairs = pd.read_csv(BASE / "results" / "nc62_brain_lineage_pairs.csv")
oc = S62["oligo_chain"]
k1 = "Oligodendrocyte precursor <> Committed oligodendrocyte precursor"
k2 = "Committed oligodendrocyte precursor <> Oligodendrocyte"
k3 = "Oligodendrocyte precursor <> Oligodendrocyte"


def chain_series(df, a, b):
    sub = df[((df["ct_a"] == a) & (df["ct_b"] == b)) | ((df["ct_a"] == b) & (df["ct_b"] == a))]
    return sub.set_index("region")["kf_fixed"]


have = False
if {"ct_a", "ct_b", "region", "kf_fixed"} <= set(pairs.columns):
    s1 = chain_series(pairs, "Oligodendrocyte precursor", "Committed oligodendrocyte precursor")
    s2 = chain_series(pairs, "Committed oligodendrocyte precursor", "Oligodendrocyte")
    s3 = chain_series(pairs, "Oligodendrocyte precursor", "Oligodendrocyte")
    common = s1.index.intersection(s2.index).intersection(s3.index)
    if len(common) >= 2:
        have = True
        for r in common:
            ax.plot([0, 1, 2], [s1[r], s2[r], s3[r]], color=GREY, lw=0.4, alpha=0.45, zorder=1)
        meds = [float(s1[common].median()), float(s2[common].median()), float(s3[common].median())]
        ax.plot([0, 1, 2], meds, color=PURPLE, lw=2.0, marker="o", ms=4, zorder=3)
        for i, m in enumerate(meds):
            ax.text(i, m + 0.004, f"{m:.3f}", ha="center", fontsize=6.6, color=PURPLE, fontweight="bold")
if not have:
    # fallback: medians only (chain json values)
    meds = [oc[k1]["kf_fixed_median"], oc[k2]["kf_fixed_median"],
            oc["paired_tests"]["kf_opc_oligo_median"]]
    ax.plot([0, 1, 2], meds, color=PURPLE, lw=2.0, marker="o", ms=4)
    for i, m in enumerate(meds):
        ax.text(i, m + 0.004, f"{m:.3f}", ha="center", fontsize=6.6, color=PURPLE, fontweight="bold")
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["OPC<->COP\n(dist 2)", "COP<->Oligo\n(dist 5)", "OPC<->Oligo\n(dist 5)"], fontsize=6.4)
ax.set_ylabel("Per-region $k_f$")
ax.set_title("Oligodendrocyte-lineage chain\n52/52 regions monotone; Wilcoxon $P$ = 1.8$\\times$10$^{-10}$", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(bottom=0)
panel_label(ax, "c")

fig.tight_layout(w_pad=2.2)
fig.savefig(OUT / "Supplementary_Fig_15.pdf")
plt.close(fig)

# ---------------- Fig 16 ----------------
fig, axes = plt.subplots(1, 3, figsize=(178 * MM, 60 * MM), gridspec_kw={"width_ratios": [1.25, 1, 1.1]})

# (a) rho comparison across atlases
ax = axes[0]
metrics = ["$k_f$", "$k_n$", "$\\omega$"]
ts = [S61["same_organ_diff_ct"]["rho_kf"], S61["same_organ_diff_ct"]["rho_kn"], S61["same_organ_diff_ct"]["rho_omega"]]
br = [S62["same_region_diff_ct"]["rho_kf_fixed"], S62["same_region_diff_ct"]["rho_kn"], S62["same_region_diff_ct"]["rho_omega_fixed"]]
ts_p = [S61["same_organ_diff_ct"]["p_kf"], S61["same_organ_diff_ct"]["p_kn"], S61["same_organ_diff_ct"]["p_omega"]]
br_p = [S62["same_region_diff_ct"]["p_kf_fixed"], S62["same_region_diff_ct"]["p_kn"], S62["same_region_diff_ct"]["p_omega_fixed"]]
x = np.arange(3)
w = 0.36
ax.bar(x - w / 2, ts, width=w, color=ORANGE, label="Cross-organ (Tabula Sapiens)")
ax.bar(x + w / 2, br, width=w, color=PURPLE, label="Cross-region (Siletti brain)")
for xi, (v, p) in enumerate(zip(ts, ts_p)):
    star = "***" if p < 1e-3 else ("NS" if p > 0.05 else "*")
    ax.text(xi - w / 2, v + 0.012 if v >= 0 else v - 0.03, star, ha="center", fontsize=6.6, color=STEEL)
for xi, (v, p) in enumerate(zip(br, br_p)):
    star = "***" if p < 1e-3 else ("NS" if p > 0.05 else "*")
    ax.text(xi + w / 2, v + 0.012 if v >= 0 else v - 0.03, star, ha="center", fontsize=6.6, color=STEEL)
ax.axhline(0, color="black", lw=0.6)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylabel(r"Spearman $\rho$ with CL lineage distance")
ax.set_ylim(-0.22, 0.4)
ax.legend(frameon=False, loc="upper left", fontsize=6.2)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("$k_f$ replicates; $k_n$ reverses across designs", fontsize=7)
panel_label(ax, "a")

# (b) germ-layer test
ax = axes[1]
mm = S62["microglia_vs_macroglia"]
ax.bar([0, 1], [mm["microglia_kf_fixed_median"], mm["macroglia_kf_fixed_median"]],
       color=[RED, PURPLE], width=0.55)
ax.text(0, mm["microglia_kf_fixed_median"] + 0.004, f"{mm['microglia_kf_fixed_median']:.3f}", ha="center", fontsize=6.6, color=STEEL)
ax.text(1, mm["macroglia_kf_fixed_median"] + 0.004, f"{mm['macroglia_kf_fixed_median']:.3f}", ha="center", fontsize=6.6, color=STEEL)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Microglia\n(mesoderm)\nn = 420", "Macroglia\n(ectoderm)\nn = 652"], fontsize=6.4)
ax.set_ylabel("Median $k_f$ to other classes")
ax.set_ylim(0, 0.19)
ax.set_title("Germ-layer prediction\nMann–Whitney $P$ = 4.5$\\times$10$^{-146}$", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
panel_label(ax, "b")

# (c) dist-0 anchors vs closest cross-class pair
ax = axes[2]
anch = S62["dist0_anchor_same_ct_cross_region"]
names = sorted(anch, key=lambda k: anch[k]["kf_fixed_median"])
v0 = [anch[k]["kf_fixed_median"] for k in names]
yp = np.arange(len(names))
ax.barh(yp, v0, color=GREY, height=0.62)
ax.axvline(oc[k1]["kf_fixed_median"], color=RED, lw=1.2, ls="--")
ax.text(oc[k1]["kf_fixed_median"] + 0.0012, len(names) - 0.4, "closest cross-class pair\nOPC<->COP (0.063)", fontsize=6.0, color=RED, va="top")
ax.set_yticks(yp)
ax.set_yticklabels([n.replace("Committed oligodendrocyte precursor", "COP").replace("Oligodendrocyte precursor", "OPC") for n in names], fontsize=6.0)
ax.set_xlabel("Median distance-0 $k_f$\n(same class, cross-region; 31,764 pairs)")
ax.set_xlim(0, 0.075)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Distance-0 anchors sit far below\nany cross-class pair", fontsize=7)
panel_label(ax, "c")

fig.tight_layout(w_pad=2.0)
fig.savefig(OUT / "Supplementary_Fig_16.pdf")
plt.close(fig)

print("done:", list(p.name for p in OUT.glob("*.pdf")))
