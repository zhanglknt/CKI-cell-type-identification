# -*- coding: utf-8 -*-
"""nc80 M-K remaining (bio M2): minimum-detectable-effect statement for the
GTEx field-effect design + normal-tissue heterogeneity correlation.

Two quantitative pieces the panel requested:

(1) MDE. The GTEx arm compares TCGA adjacent-normal within-class k_n (NN)
    against GTEx healthy within-class k_n (GG) across cohorts. The same-
    organ cross-cohort offset GA/GG (GTEx-vs-adjacent mean-profile shift)
    sets the design's resolution: any field effect smaller than that
    offset cannot be resolved. Report per-cancer tested difference
    (GG vs NN) against the cross-cohort offset (GA/GG).

(2) Normal-heterogeneity tracking. bio's alternative explanation for the
    per-cancer reversal gradient: the TT/NN ratio ranking tracks the
    adjacent-normal heterogeneity (the denominator), not tumour magnitude
    (the numerator). Test: Spearman(NN median, TT/NN ratio) across the
    five cancers with exact permutation P (n = 5, 120 permutations),
    against Spearman(TT median, ratio).

Inputs: results/nc52_gtex_summary.json (per-cancer k_n medians by pair
        type, nn/gg/ga/tt). No re-analysis of raw data.

Outputs: results/nc80_mk_mde_heterogeneity.csv / .txt
"""
import json
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "nc52_gtex_summary.json"
OUT_CSV = ROOT / "results" / "nc80_mk_mde_heterogeneity.csv"
OUT_TXT = ROOT / "results" / "nc80_mk_mde_heterogeneity.txt"

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

d = json.load(open(SRC))
rows = []
for can, v in d["per_cancer"].items():
    km = v["kn_median"]
    nn, gg, ga, tt = km["NN"], km["GG"], km["GA"], km["TT"]
    rows.append({
        "cancer": can, "organ": v["organ"],
        "n_adjacent": v["n_adjacent"], "n_gtex": v["n_gtex"],
        "kn_NN": nn, "kn_GG": gg, "kn_GA": ga, "kn_TT": tt,
        # tested difference: healthy(GTEx) vs adjacent, as % of adjacent
        "tested_diff_GG_vs_NN_pct": 100.0 * (gg - nn) / nn,
        # cross-cohort offset: GTEx-vs-adjacent mean-shift, as % of GG
        "cross_cohort_shift_GA_vs_GG_pct": 100.0 * (ga - gg) / gg,
        "ratio_TT_NN": v["ratio_TT_NN"],
        "ratio_GG_TT": gg / tt,
        "ratio_GG_NN": v["ratio_GG_NN"],
    })
df = pd.DataFrame(rows)

# ---- Spearman with exact permutation P (n=5) ----
nn_med = df["kn_NN"].to_numpy()
tt_med = df["kn_TT"].to_numpy()
ratio = df["ratio_TT_NN"].to_numpy()

def spearman_exact(x, y):
    rho = stats.spearmanr(x, y).statistic
    n = len(x)
    count_ge = 0
    count_le = 0
    perms = list(permutations(range(n)))
    for p in perms:
        r = stats.spearmanr(x, [y[i] for i in p]).statistic
        if r >= rho:
            count_ge += 1
        if r <= rho:
            count_le += 1
    # exact two-sided P: min tail doubled (permutation distribution)
    p_ge = count_ge / len(perms)
    p_le = count_le / len(perms)
    p_two = min(1.0, 2 * min(p_ge, p_le))
    return rho, p_two

rho_nn, p_nn = spearman_exact(nn_med, ratio)
rho_tt, p_tt = spearman_exact(tt_med, ratio)
log("per-cancer table:")
log(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
log(f"Spearman(k_n NN median, TT/NN ratio): rho={rho_nn:.3f}, "
    f"exact two-sided P={p_nn:.4f} (n=5, 120 permutations)")
log(f"Spearman(k_n TT median, TT/NN ratio): rho={rho_tt:.3f}, "
    f"exact two-sided P={p_tt:.4f}")

# ---- MDE summary line ----
sub4 = df[df["cancer"] != "TCGA-KIRC"]
log(f"tested adjacent-vs-healthy differences (GG vs NN, % of NN): "
    f"{sub4['tested_diff_GG_vs_NN_pct'].min():.0f} to "
    f"{sub4['tested_diff_GG_vs_NN_pct'].max():.0f}% in the four non-KIRC "
    f"cancers; KIRC {df.loc[df.cancer=='TCGA-KIRC','tested_diff_GG_vs_NN_pct'].iloc[0]:.0f}%")
log(f"cross-cohort same-organ offset (GA vs GG, % of GG): "
    f"{df['cross_cohort_shift_GA_vs_GG_pct'].min():.0f} to "
    f"{df['cross_cohort_shift_GA_vs_GG_pct'].max():.0f}%")
kirc = df[df["cancer"] == "TCGA-KIRC"].iloc[0]
log(f"KIRC: healthy GTEx within-class k_n = "
    f"{kirc['ratio_GG_TT']:.2f} x tumour k_n (GG/TT); n_gtex="
    f"{int(kirc['n_gtex'])} (Kidney-Cortex); adjacent normals the "
    f"tightest cluster of the five (NN {kirc['kn_NN']:.5f})")

df.to_csv(OUT_CSV, index=False)
extra = pd.DataFrame([
    {"stat": "spearman_NN_vs_ratio", "rho": rho_nn, "p_exact_two_sided": p_nn},
    {"stat": "spearman_TT_vs_ratio", "rho": rho_tt, "p_exact_two_sided": p_tt},
])
extra.to_csv(OUT_CSV.with_name("nc80_mk_mde_spearman.csv"), index=False)
log(f"saved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
