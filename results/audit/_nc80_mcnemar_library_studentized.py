#!/usr/bin/env python3
"""nc80 stat m7: re-report the T1 paired FPR contrasts on library clusters.

Panel complaint (stat m7). Exact McNemar P values on 2,161 T1 pairs treat
library-level technical replicates as independent observations, although the
pairs come from 597 10x libraries and 4 donors (mean pair-degree 7.2). Exact
McNemar P values are therefore anti-conservative by orders of magnitude, and
the donor-cluster percentile bootstrap (4 clusters) is itself over-precise --
the paper's own Note 2 shows percentile cluster coverage of 0.876 at 6-7
clusters.

Fix adopted here. Report intervals, not exact P values, and take the
*library* (597 clusters) rather than the donor (4 clusters) as the
resampling unit -- the same studentized correction already used for region
clusters. Two estimators are produced:

  (i) library-level estimand
      For each library L, exceedance rate of each metric over all T1 pairs
      that involve L: r_m(L), r_omega(L), Delta_L = r_m(L) - r_omega(L).
      Delta_lib = mean_L Delta_L, SE = sd(Delta_L)/sqrt(G), G = 597.
      Studentized bootstrap-t: resample libraries with replacement, recompute
      Delta*_b and its own SE*_b, form t*_b = (Delta*_b - Delta_lib)/SE*_b,
      interval = Delta_lib - t*_{97.5} * SE_obs (and symmetrically).

  (ii) pair-level estimand (the quantity the manuscript quotes)
      Delta_pair = mean_i(o_i - ow_i); included to show the estimand choice
      moves the point estimate only in the third decimal.

Outputs:
  results/nc80_mcnemar_t1_studentized.csv
  results/nc80_mcnemar_t1_studentized.json
  results/nc80_mcnemar_t1_studentized.txt
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results"
RNG = np.random.default_rng(42)
B = 10000
METS = ["raw_js", "cosine", "spearman", "marker_jaccard", "k_n", "k_f"]

lad = pd.read_csv(OUT / "nc49_brain_drift_ladder.csv")
t1 = lad[lad["tier"] == "T1_techrep"].reset_index(drop=True)
assert len(t1) == 2161, len(t1)

libs = np.sort(pd.unique(pd.concat([t1["sample_a"], t1["sample_b"]])))
assert len(libs) == 597, len(libs)
lib_ix = {l: i for i, l in enumerate(libs)}
ia = t1["sample_a"].map(lib_ix).to_numpy()
ib = t1["sample_b"].map(lib_ix).to_numpy()
G = len(libs)

ow = t1["exceed_omega"].to_numpy(int)
n = len(t1)
p_omega = ow.mean()
deg = np.bincount(ia, minlength=G) + np.bincount(ib, minlength=G)
print(f"T1: {n} pairs, {G} libraries, mean pair-degree {deg.mean():.2f}, "
      f"donors {t1['donor_a'].nunique()}")
print(f"omega exceedance rate {p_omega:.4f} ({ow.sum()}/{n})")

rows = []
boot_store = {}
for met in METS:
    o = t1[f"exceed_{met}"].to_numpy(int)
    d = o - ow                                     # paired difference, +1 unit
    p_m = o.mean()
    delta_pair = p_m - p_omega

    # ---- library-level rates
    s_m = np.bincount(ia, weights=o, minlength=G) + np.bincount(ib, weights=o, minlength=G)
    s_w = np.bincount(ia, weights=ow, minlength=G) + np.bincount(ib, weights=ow, minlength=G)
    r_m, r_w = s_m / deg, s_w / deg
    dl = r_m - r_w
    delta_lib = float(dl.mean())
    se_lib = float(dl.std(ddof=1) / np.sqrt(G))

    # library-weighted pair-level estimate (should reproduce delta_pair)
    delta_wt = float((s_m.sum() - s_w.sum()) / (2 * n))

    # ---- studentized bootstrap-t over libraries
    tstar = np.empty(B)
    dstar = np.empty(B)
    for b in range(B):
        pick = RNG.integers(0, G, size=G)
        v = dl[pick]
        dstar[b] = v.mean()
        se_b = v.std(ddof=1) / np.sqrt(G)
        tstar[b] = (dstar[b] - delta_lib) / se_b if se_b > 1e-12 else 0.0
    t_lo, t_hi = np.percentile(tstar, [2.5, 97.5])
    bt_lo, bt_hi = delta_lib - t_hi * se_lib, delta_lib - t_lo * se_lib
    pc_lo, pc_hi = np.percentile(dstar, [2.5, 97.5])

    # ---- analytic library-cluster t interval (df = G - 1)
    tq = stats.t.ppf(0.975, G - 1)
    an_lo, an_hi = delta_lib - tq * se_lib, delta_lib + tq * se_lib

    # ---- naive pair-level binomial interval, for the anti-conservativeness demo
    naive_se = np.sqrt(d.var(ddof=1) / n)
    naive_lo, naive_hi = delta_pair - 1.959964 * naive_se, delta_pair + 1.959964 * naive_se

    # ---- pair-level estimand with two-way (Cameron-Gelbach-Miller)
    # cluster-robust variance on the two library endpoints of every pair.
    # Each pair is one dyad (library_a, library_b); clustering on a, on b, and
    # on the intersection, then V = V_a + V_b - V_ab.  This keeps the
    # manuscript's pair-average estimand while removing the fiction that
    # 2,161 library-level pairs are independent observations.
    def _cluster_var(clusters):
        """Cluster-robust variance of the mean, one-way clustering."""
        s = pd.Series(d).groupby(clusters).sum().to_numpy()
        sz = pd.Series(d).groupby(clusters).size().to_numpy()
        Gm = len(s)
        return float(Gm / (Gm - 1) * (((s - sz * d.mean()) ** 2).sum()) / n ** 2)

    V_a = _cluster_var(ia)
    V_b = _cluster_var(ib)
    V_ab = float((n / (n - 1)) * ((d - d.mean()) ** 2).sum() / n ** 2)
    V_2way = max(V_a + V_b - V_ab, 1e-12)
    se_2way = float(np.sqrt(V_2way))
    df_2way = G - 1
    tq2 = stats.t.ppf(0.975, df_2way)
    dy_lo, dy_hi = delta_pair - tq2 * se_2way, delta_pair + tq2 * se_2way
    deff_2way = (se_2way / naive_se) ** 2 if naive_se > 0 else np.nan

    # ---- ICC-style design effect: how much the naive SE understates
    deff = (se_lib / naive_se) ** 2 if naive_se > 0 else np.nan

    b_ct = int(((ow == 1) & (o == 0)).sum())
    c_ct = int(((ow == 0) & (o == 1)).sum())
    rows.append(dict(
        contrast=f"{met} - omega",
        fpr_metric=p_m, fpr_omega=p_omega,
        delta_pair=delta_pair, delta_lib=delta_lib, delta_lib_weighted=delta_wt,
        se_lib=se_lib, se_naive_pair=naive_se, design_effect=deff,
        lib_t_lo=an_lo, lib_t_hi=an_hi,
        lib_boott_lo=bt_lo, lib_boott_hi=bt_hi,
        lib_percentile_lo=pc_lo, lib_percentile_hi=pc_hi,
        naive_pair_lo=naive_lo, naive_pair_hi=naive_hi,
        se_2way=se_2way, deff_2way=deff_2way,
        dyadic_t_lo=dy_lo, dyadic_t_hi=dy_hi,
        dyadic_excludes_zero=bool(min(dy_lo, dy_hi) > 0 or max(dy_lo, dy_hi) < 0),
        discordant_omega_only=b_ct, discordant_metric_only=c_ct,
        n_pairs=n, n_libraries=G, n_donors=int(t1["donor_a"].nunique()),
        excludes_zero=bool(min(an_lo, an_hi) > 0 or max(an_lo, an_hi) < 0),
    ))
    boot_store[met] = dict(delta_pair=delta_pair, delta_lib=delta_lib,
                           se_2way=se_2way, deff_2way=deff_2way,
                           dyadic_t=[float(dy_lo), float(dy_hi)],
                           se_lib=se_lib,
                           boott=[float(bt_lo), float(bt_hi)],
                           t_quantiles=[float(t_lo), float(t_hi)])
    print(f"{met:>15s}: FPR {p_m:.4f} vs {p_omega:.4f} | "
          f"Delta_pair={delta_pair:+.4f} (2way SE {se_2way:.4f}, deff {deff_2way:.1f}) "
          f"t95 [{dy_lo:+.3f},{dy_hi:+.3f}] | Delta_lib={delta_lib:+.4f} "
          f"SE_lib={se_lib:.4f} boott [{bt_lo:+.3f},{bt_hi:+.3f}]")

df = pd.DataFrame(rows)
df.to_csv(OUT / "nc80_mcnemar_t1_studentized.csv", index=False)

summary = {
    "design": "T1 technical-replicate pairs; library (597) instead of donor (4) "
              "or pair (2161) as the resampling unit; studentized bootstrap-t, "
              "B=10000, seed 42",
    "n_pairs": n, "n_libraries": G, "mean_pair_degree": float(deg.mean()),
    "fpr_omega": float(p_omega),
    "max_design_effect": float(np.nanmax(df["design_effect"])),
    "all_exclude_zero": bool(df["excludes_zero"].all()),
    "contrasts": boot_store,
}
(OUT / "nc80_mcnemar_t1_studentized.json").write_text(json.dumps(summary, indent=2))

lines = [
    "nc80 stat m7 -- T1 paired FPR contrasts on library clusters",
    "=" * 62,
    f"pairs={n} libraries={G} donors={t1['donor_a'].nunique()} "
    f"mean pair-degree={deg.mean():.2f}",
    f"omega exceedance rate = {p_omega:.4f}",
    "",
    f"{'contrast':>22s} {'d_pair':>8s} {'d_lib':>8s} {'SE_lib':>7s} "
    f"{'deff':>6s} {'lib-t 95%':>18s} {'boot-t 95%':>18s}",
]
for r in rows:
    lines.append(
        f"{r['contrast']:>22s} {r['delta_pair']:+8.4f} {r['delta_lib']:+8.4f} "
        f"{r['se_lib']:7.4f} {r['design_effect']:6.1f} "
        f"[{r['lib_t_lo']:+.3f},{r['lib_t_hi']:+.3f}]".ljust(78)
        + f" [{r['lib_boott_lo']:+.3f},{r['lib_boott_hi']:+.3f}]")
lines += ["", "Note: exact McNemar P values are no longer reported for these "
              "contrasts (stat m7); the interval is the inferential statement."]
(OUT / "nc80_mcnemar_t1_studentized.txt").write_text("\n".join(lines) + "\n")
print("\n" + "\n".join(lines))
print("\nwrote results/nc80_mcnemar_t1_studentized.{csv,json,txt}")
