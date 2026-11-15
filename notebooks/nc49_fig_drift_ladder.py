# -*- coding: utf-8 -*-
"""
nc49_fig_drift_ladder.py — Figure for the brain neutral-drift ladder (NC v49).

Reads:
  results/nc49_brain_drift_ladder.csv   (long table; one row per library pair)
  results/nc49_pilot_kang_techrep.csv   (Kang batch1 pilot replication)

Panels:
  a  Schematic of the four-tier ladder (text/diagram).
  b  Calibration distributions per tier x metric (box plots of
     cal = observed / own n-matched null median), brain.
  c  FPR bar chart (fraction of pairs exceeding own null p95) for
     T1 (technical drift) and T2 (donor drift), brain.
  d  Kang batch1 replication: per-metric FPR + calibration (T1 only).

Style: _fig_style.py (NAR sizing; NC target reuses the same identity).

Run:
  C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe
      -u notebooks/nc49_fig_drift_ladder.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "notebooks"))
from _fig_style import (  # noqa: E402
    apply_style, despine, subtle_grid, add_panel_label, save_fig,
    new_figure, DOUBLE, MM, C_BLUE, C_GREEN, C_RED, C_AMBER, C_STEEL,
    C_PURPLE, C_TEAL, C_ORANGE, C_GRAY, SMALL_SIZE, BODY_SIZE,
)
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = PROJECT_ROOT / "results"
OUT_NAME = "nc49_fig_drift_ladder"

METRICS = ["omega", "k_f", "k_n", "raw_js", "cosine", "spearman", "marker_jaccard"]
METRIC_LABELS = {
    "omega": "CKI $\\omega$",
    "k_f": "$k_f$",
    "k_n": "$k_n$",
    "raw_js": "raw JS",
    "cosine": "cosine dist",
    "spearman": "Spearman dist",
    "marker_jaccard": "marker Jaccard",
}
METRIC_COLORS = {
    "omega": C_BLUE, "k_f": C_GREEN, "k_n": C_TEAL,
    "raw_js": C_RED, "cosine": C_ORANGE, "spearman": C_PURPLE,
    "marker_jaccard": C_STEEL,
}
TIERS = ["T1_techrep", "T2_cross_donor", "T3_cross_roi"]
TIER_LABELS = {
    "T1_techrep": "T1 technical\n(same donor+region,\ncross-library)",
    "T2_cross_donor": "T2 donor drift\n(same region,\ncross-donor)",
    "T3_cross_roi": "T3 regional\n(same donor,\ncross-region)",
}


def main():
    df = pd.read_csv(RESULTS / "nc49_brain_drift_ladder.csv")
    kang = pd.read_csv(RESULTS / "nc49_pilot_kang_techrep.csv")

    fig = new_figure(DOUBLE, 120 * MM)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1.0],
                          height_ratios=[1.0, 1.0], hspace=0.42, wspace=0.28,
                          left=0.075, right=0.985, top=0.90, bottom=0.10)

    # ---------------- (a) schematic ----------------
    axa = fig.add_subplot(gs[0, 0])
    axa.set_xlim(0, 10)
    axa.set_ylim(0, 10)
    axa.axis("off")
    add_panel_label(fig, axa, "a")
    axa.text(5, 9.6, "Neutral-drift ladder (brain, library-level pairs)",
             ha="center", fontsize=9, fontweight="bold")
    tiers_txt = [
        ("T1  technical drift", "same donor, same region, two 10x libraries\n"
         "ground truth: no functional difference", C_RED),
        ("T2  donor drift", "same region, two donors\n"
         "technical + inter-individual drift", C_AMBER),
        ("T3  regional biology", "same donor, two regions\n"
         "positive control: divergence expected", C_GREEN),
    ]
    y = 7.8
    for title, desc, color in tiers_txt:
        axa.add_patch(plt.Rectangle((0.4, y - 1.5), 9.2, 1.9,
                                    facecolor="white", edgecolor=color,
                                    linewidth=1.0))
        axa.text(0.9, y + 0.05, title, fontsize=8, fontweight="bold",
                 va="center", color=color)
        axa.text(0.9, y - 0.95, desc, fontsize=7, va="center", color="#333")
        y -= 2.5
    axa.text(5, 0.35, "per pair: observed vs. n-matched cell-shuffle null\n"
             "(pooled nuclei, split at observed group sizes, "
             f"B = 100/30/30)", ha="center", fontsize=7, style="italic",
             color="#555")

    # ---------------- (b) calibration distributions ----------------
    axb = fig.add_subplot(gs[0, 1])
    add_panel_label(fig, axb, "b")
    positions, data, colors, alphas = [], [], [], []
    ticklabels = []
    pos = 0.0
    TIER_ALPHAS = {"T1_techrep": 0.90, "T2_cross_donor": 0.55, "T3_cross_roi": 0.25}
    for m in METRICS:
        for tier in TIERS:
            sub = df[(df.tier == tier)][f"cal_{m}"].dropna()
            sub = sub[np.isfinite(sub)]
            # clip extreme tails for display (keep whiskers informative)
            lo, hi = sub.quantile([0.02, 0.98])
            sub_c = sub[(sub >= lo) & (sub <= hi)]
            positions.append(pos)
            data.append(sub_c.values)
            colors.append(METRIC_COLORS[m])
            alphas.append(TIER_ALPHAS[tier])
            pos += 1
        ticklabels.append((pos - 3 / 2, METRIC_LABELS[m]))
        pos += 0.7
    bp = axb.boxplot(data, positions=positions, widths=0.72, showfliers=False,
                     patch_artist=True, medianprops=dict(color="black",
                                                         linewidth=0.9),
                     whiskerprops=dict(linewidth=0.6),
                     capprops=dict(linewidth=0.6))
    for patch, c, a in zip(bp["boxes"], colors, alphas):
        patch.set_facecolor(c)
        patch.set_alpha(a)
        patch.set_edgecolor(c)
    axb.axhline(1.0, color="#1A1A1A", linewidth=0.8, linestyle="--", zorder=0)
    axb.set_yscale("log")
    axb.set_yticks([0.5, 1, 2, 5, 10])
    axb.set_yticklabels(["0.5", "1", "2", "5", "10"])
    axb.set_ylabel("calibration  (observed / null median)")
    axb.set_xticks([p for p, _ in ticklabels])
    axb.set_xticklabels([t for _, t in ticklabels], rotation=30, ha="right")
    # tier legend: fill lightness encodes tier (T1 dark -> T3 light)
    handles = []
    for tier, a in TIER_ALPHAS.items():
        h = plt.Rectangle((0, 0), 1, 1, facecolor=C_GRAY, alpha=a,
                          edgecolor=C_GRAY, linewidth=0.5)
        handles.append(h)
    leg = axb.legend(handles, [TIER_LABELS[t].split("\n")[0] for t in TIERS],
                     loc="upper left", fontsize=SMALL_SIZE, ncol=1,
                     handletextpad=0.4, borderpad=0.4,
                     title="tiers (left to right within each metric)")
    leg.get_title().set_fontsize(SMALL_SIZE)
    axb.set_title("Brain: calibration by tier", fontsize=9, loc="left")
    subtle_grid(axb, axis="y")

    # ---------------- (c) FPR bars (brain) ----------------
    axc = fig.add_subplot(gs[1, 0])
    add_panel_label(fig, axc, "c")
    width = 0.38
    xs = np.arange(len(METRICS))
    for k, tier in enumerate(["T1_techrep", "T2_cross_donor"]):
        fprs = [df[df.tier == tier][f"exceed_{m}"].mean() for m in METRICS]
        # Wilson 95% CI
        n = (df.tier == tier).sum()
        z = 1.96
        cis = []
        for p in fprs:
            den = 1 + z**2 / n
            ctr = (p + z**2 / (2 * n)) / den
            half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
            cis.append(half)
        axc.bar(xs + (k - 0.5) * width, fprs, width=width,
                color=[C_RED, C_ORANGE] if k == 0 else "#B9BEC4",
                edgecolor="black", linewidth=0.4,
                label=TIER_LABELS[tier].split("\n")[0])
        axc.errorbar(xs + (k - 0.5) * width, fprs, yerr=[cis, cis],
                     fmt="none", ecolor="black", elinewidth=0.7, capsize=1.5)
    axc.axhline(0.05, color="#1A1A1A", linewidth=0.8, linestyle=":")
    axc.text(len(METRICS) - 0.45, 0.055, "nominal 5%", fontsize=6.5,
             ha="right", color="#333")
    axc.set_xticks(xs)
    axc.set_xticklabels([METRIC_LABELS[m] for m in METRICS], rotation=30,
                        ha="right")
    axc.set_ylabel("false-positive rate\n(exceed own null p95)")
    axc.set_title("Brain: drift misreporting", fontsize=9, loc="left")
    axc.legend(fontsize=SMALL_SIZE)
    subtle_grid(axc, axis="y")

    # ---------------- (d) Kang replication ----------------
    axd = fig.add_subplot(gs[1, 1])
    add_panel_label(fig, axd, "d")
    km = ["omega", "k_f", "k_n", "raw_js", "cosine"]
    fprs = [kang[f"exceed_{m}"].mean() for m in km]
    cals = [kang[f"cal_{m}"].median() for m in km]
    n = len(kang)
    z = 1.96
    cis = []
    for p in fprs:
        den = 1 + z**2 / n
        ctr = (p + z**2 / (2 * n)) / den
        half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
        cis.append(half)
    xs = np.arange(len(km))
    axd.bar(xs, fprs, width=0.6, color=[METRIC_COLORS[m] for m in km],
            edgecolor="black", linewidth=0.4)
    axd.errorbar(xs, fprs, yerr=[cis, cis], fmt="none", ecolor="black",
                 elinewidth=0.7, capsize=1.5)
    axd.axhline(0.05, color="#1A1A1A", linewidth=0.8, linestyle=":")
    for x, c in zip(xs, cals):
        axd.text(x, 0.012, f"cal\n{c:.2f}", ha="center", fontsize=6,
                 color="#333")
    axd.set_xticks(xs)
    axd.set_xticklabels([METRIC_LABELS[m] for m in km], rotation=30,
                        ha="right")
    axd.set_ylabel("false-positive rate")
    axd.set_title(f"Replication: Kang batch1 technical replicates (n={n})",
                  fontsize=9, loc="left")
    subtle_grid(axd, axis="y")

    paths = save_fig(fig, OUT_NAME)
    for p in paths:
        print(f"saved {p}")
    plt.close(fig)


if __name__ == "__main__":
    main()
