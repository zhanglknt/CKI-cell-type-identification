#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc68: render Supplementary Fig. 19 (theory diagnostics, SI Note 20).

Panels (2x2, 178 mm wide):
  a. Quadratic-regime check: |JS - Q| / JS by dataset x panel
     (HK = k_n scale; top-200 = k_f scale), log scale.
  b. Background-energy exchangeability: per-gene mean-energy ratio
     (top-200 / HK) on split-half null pairs.
  c. Ground-truth estimand: mean omega - 1 versus injected functional
     shift delta, one line per background-drift level eta
     (groundtruth_simulation_background2 grid).
  d. Null ancillarity: cross-class dispersion (CV) of the split-half
     null for k_f, k_n and omega (brain + mouse).

Data: results/theory_diagnostics.csv (notebooks/85_theory_diagnostics.py)
Output: results/figures_v66/Supplementary_Fig_19.pdf (+ STAGE copy)
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

df = pd.read_csv(BASE / "results" / "theory_diagnostics.csv")

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
    ax.text(-0.16, 1.06, s, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="top")


fig, axes = plt.subplots(2, 2, figsize=(178 * MM, 110 * MM))

# ---------- a. quadratic regime ----------
ax = axes[0, 0]
a = df[df["part"] == "A_quadratic"]
order = [("brain_observed", "Brain obs."), ("brain_splithalf", "Brain null"),
         ("ts_observed", "TS obs."), ("ts_splithalf", "TS null")]
pos, data, colors, ticklabels = [], [], [], []
i = 0
for ds, lab in order:
    for panel, col in [("hk", STEEL), ("top200", PURPLE)]:
        v = a[(a["dataset"] == ds) & (a["panel"] == panel)]["rel_err"].dropna()
        if len(v):
            data.append(v.values * 100)
            pos.append(i)
            colors.append(col)
            i += 1
    ticklabels.append(lab)
bp = ax.boxplot(data, positions=pos, widths=0.62, showfliers=False,
                patch_artist=True, medianprops=dict(color="black", lw=0.8),
                whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
for patch, col in zip(bp["boxes"], colors):
    patch.set_facecolor(col)
    patch.set_alpha(0.75)
    patch.set_edgecolor("none")
ax.set_yscale("log")
centers = [np.mean(pos[k * 2:k * 2 + 2]) for k in range(len(order))]
ax.set_xticks(centers)
ax.set_xticklabels(ticklabels)
ax.set_ylabel("|JS \u2212 Q| / JS (%)")
ax.set_title("Second-order expansion error", loc="left")
handles = [plt.Rectangle((0, 0), 1, 1, fc=STEEL, alpha=0.75),
           plt.Rectangle((0, 0), 1, 1, fc=PURPLE, alpha=0.75)]
ax.legend(handles, ["HK panel (k$_n$)", "top-200 panel (k$_f$)"],
          frameon=False, loc="upper left")
panel_label(ax, "a")

# ---------- b. exchangeability ----------
ax = axes[0, 1]
b = df[df["part"] == "B_exchangeability"]
for (ds, col, lab) in [("brain_splithalf", PURPLE, "Brain null"),
                       ("ts_splithalf", GREY, "TS null")]:
    v = b[b["dataset"] == ds]["exch_mean_energy_ratio"].dropna()
    ax.hist(np.log10(v), bins=30, alpha=0.65, color=col,
            label=f"{lab} (n={len(v)})", density=True)
    med = np.median(v)
    ax.axvline(np.log10(med), color=col, ls="--", lw=0.8)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("log$_{10}$ per-gene energy ratio (top-200 / HK)")
ax.set_ylabel("Density")
ax.set_title("Background-energy exchangeability", loc="left")
ax.legend(frameon=False, loc="upper right")
panel_label(ax, "b")

# ---------- c. ground-truth estimand ----------
ax = axes[1, 0]
d = df[(df["part"] == "D_groundtruth")
       & df["dataset"].str.startswith("estimand_")].copy()
d["delta"] = d["pair_id"].str.replace("delta_", "").astype(float)
d["eta"] = d["exch_mean_energy_ratio"].astype(float)
cmap = {0.0: STEEL, 0.25: GREY, 0.5: ORANGE, 1.0: RED}
for eta in sorted(d["eta"].unique()):
    sub = d[d["eta"] == eta].sort_values("delta")
    ax.plot(sub["delta"], sub["js"] - 1, marker="o", ms=3, lw=1.0,
            color=cmap.get(eta, DGREY), label=f"\u03b7 = {eta:g}")
ax.set_yscale("log")
ax.set_xlabel("functional shift \u03b4 (log$_2$ fold)")
ax.set_ylabel("\u03c9 \u2212 1")
ax.set_title("Ground-truth estimand (\u03b5 = 0)", loc="left")
ax.legend(frameon=False, title="background drift", loc="upper left")
panel_label(ax, "c")

# ---------- d. null ancillarity ----------
ax = axes[1, 1]
c = df[df["part"] == "C_ancillarity"]
met_order = ["kf", "kn", "omega"]
met_lab = {"kf": "k$_f$", "kn": "k$_n$", "omega": "\u03c9"}
ds_order = [d for d in c["dataset"].unique()]
width = 0.25
x = np.arange(len(ds_order))
for k, met in enumerate(met_order):
    vals = []
    for ds in ds_order:
        row = c[(c["dataset"] == ds) & (c["ct"] == met)]
        vals.append(float(row["js"].iloc[0]) if len(row) else np.nan)
    ax.bar(x + (k - 1) * width, vals, width=width,
           color=[PURPLE, STEEL, ORANGE][k], alpha=0.8, label=met_lab[met])
ax.set_xticks(x)
ax.set_xticklabels([d.replace("_", "\n") for d in ds_order], fontsize=6)
ax.set_ylabel("cross-class CV of null median")
ax.set_title("Null dispersion across classes", loc="left")
ax.legend(frameon=False, loc="upper right")
panel_label(ax, "d")

fig.tight_layout()
fig.savefig(OUT / "Supplementary_Fig_19.pdf")
print("saved", OUT / "Supplementary_Fig_19.pdf")

# stage copy (build ships from STAGE)
import shutil
stage = BASE / "results" / "figures_v58_author"
shutil.copy2(OUT / "Supplementary_Fig_19.pdf", stage / "figure_S19.pdf")
print("staged", stage / "figure_S19.pdf")

# ---- geometry audit (no overlapping tick labels / legend inside axes) ----
import warnings
fig.canvas.draw()
rend = fig.canvas.get_renderer()
for ax in axes.flat:
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
        bb = tl.get_window_extent(rend)
        if bb.width > ax.get_window_extent(rend).width * 1.05:
            warnings.warn(f"tick overflow on axes {ax.get_title()}")
print("geometry audit done")
