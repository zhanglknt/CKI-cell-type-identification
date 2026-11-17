# -*- coding: utf-8 -*-
"""
nc80_t1_library_null.py — T1 library-aware null (nc80 panel M-D / stat Q6).

Question (stat reviewer Q6, verbatim intent): what is the T1 exceedance rate
under a null that preserves library identity (permuting libraries within
donor x region x cell type)? If ~5%, the 28.6% is a library-effect measure
and the metric is calibrated; if it remains >10%, the per-pair cell-shuffle
null is still anti-conservative.

Design constraints discovered on the data:
- T1 blocks (donor, roi, cell type) are sparse: 1,144 blocks over 2,161
  pairs, median block = 1 pair -> leave-self-out *re-pairing within a block*
  is infeasible for most pairs.
- The per-pair cell-shuffle null (deposited in the ladder) re-splits the two
  libraries' pooled nuclei, so it contains cell-sampling noise plus the
  between-library mean shift diluted into the pool — it is TIGHTER than the
  observed between-library variation whenever real library effects exist.

Library-aware null used here (class-level, run-matched): for a T1 pair p of
cell class c and 10x-run-match flag f, the null reference set is the omega
values of all OTHER T1 pairs of the same class with the same run-match flag
(f = same-run for the primary analysis). Those pairs are same-donor,
same-region, same-class library comparisons from other blocks: they carry
the class's real between-library (and size-imbalance) noise but no
regional biological signal (each is within one region). Exceedance is
omega_p > empirical q95 of that set (leave-self-out). Under the null of
exchangeable library noise within class x run-stratum, E[exceedance] = 5%.

Decision rule (panel):
  rate ~ 5%  -> the 28.6%/10.3% under the per-pair sampling null measures
                real library effects; omega is calibrated against
                library-aware noise.
  rate > 10% -> pairs are atypical even against their own class's library
                noise; the per-pair null remains anti-conservative.

Also computed:
- noise-scale ratio: median(class-null q95) / median(cell-shuffle q95) per
  class — how much wider the library-aware null is (library-effect size).
- mechanism attribution of the residual 2x on the strictly matched block
  (same-run prefix and n-ratio >= 0.7, n = 1,334): exceeders' calibration
  ratios, size ratios, and run composition.

Inputs (read-only): results/nc49_brain_drift_ladder.csv
Outputs:
  results/nc80_t1_library_null.csv        per-pair library-null flags
  results/nc80_t1_library_null_summary.txt
  results/nc80_t1_library_null.json
Seed: deterministic (no sampling).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LADDER = ROOT / "results" / "nc49_brain_drift_ladder.csv"
OUT_CSV = ROOT / "results" / "nc80_t1_library_null.csv"
OUT_TXT = ROOT / "results" / "nc80_t1_library_null_summary.txt"
OUT_JSON = ROOT / "results" / "nc80_t1_library_null.json"


def wilson(p_hat, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    denom = 1 + z * z / n
    center = (p_hat + z * z / (2 * n)) / denom
    half = z * np.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


def main():
    df = pd.read_csv(LADDER)
    t1 = df[df["tier"] == "T1_techrep"].copy().reset_index(drop=True)
    assert len(t1) == 2161, f"expected 2161 T1 pairs, got {len(t1)}"

    t1["prefix_a"] = t1["sample_a"].str.split("_").str[0]
    t1["prefix_b"] = t1["sample_b"].str.split("_").str[0]
    t1["same_run"] = (t1["prefix_a"] == t1["prefix_b"]).astype(int)
    t1["n_ratio"] = np.minimum(t1["n_cells_a"], t1["n_cells_b"]) / np.maximum(
        t1["n_cells_a"], t1["n_cells_b"]
    )
    t1["strict"] = ((t1["same_run"] == 1) & (t1["n_ratio"] >= 0.7)).astype(int)

    # --- library-aware class-level nulls ---------------------------------
    # Primary: run-matched class null (same-run stratum)
    sr = t1[t1["same_run"] == 1]
    dr = t1[t1["same_run"] == 0]
    # Variant: all-T1 class null (any run)
    class_all_null_q95 = t1.groupby("cell_type")["omega"].quantile(0.95)
    class_sr_null_q95 = sr.groupby("cell_type")["omega"].quantile(0.95)

    # leave-self-out: recompute per-pair q95 excluding the pair itself.
    # With class-stratum sizes 67-503, self-exclusion shifts q95 negligibly;
    # we still implement it exactly.
    t1_sorted = t1.sort_values("omega").reset_index()
    q95_lso_sr = {}
    q95_lso_all = {}
    for ct, g in t1.groupby("cell_type"):
        om = np.sort(g["omega"].values)
        g_sr = np.sort(g.loc[g["same_run"] == 1, "omega"].values)
        n_all, n_sr = len(om), len(g_sr)
        for idx, row in g.iterrows():
            # all-run class null, leave-self-out
            om_lso = np.delete(om, np.searchsorted(om, row["omega"]))
            q95_lso_all[idx] = np.quantile(om_lso, 0.95)
            # same-run class null, leave-self-out
            if row["same_run"] == 1 and n_sr > 1:
                om_sr_lso = np.delete(g_sr, np.searchsorted(g_sr, row["omega"]))
                q95_lso_sr[idx] = np.quantile(om_sr_lso, 0.95)
            else:
                q95_lso_sr[idx] = np.nan

    t1["lib_null_q95_sr"] = pd.Series(q95_lso_sr)
    t1["lib_null_q95_all"] = pd.Series(q95_lso_all)
    t1["lib_exceed_sr"] = (
        t1["omega"] > t1["lib_null_q95_sr"]
    ).astype(float).where(t1["lib_null_q95_sr"].notna(), np.nan)
    t1["lib_exceed_all"] = (t1["omega"] > t1["lib_null_q95_all"]).astype(int)

    # noise-scale comparison per class: library-aware q95 vs cell-shuffle q95
    scale_rows = []
    for ct, g in t1.groupby("cell_type"):
        scale_rows.append(
            {
                "cell_type": ct,
                "n_pairs": len(g),
                "n_same_run": int(g["same_run"].sum()),
                "med_omega": g["omega"].median(),
                "med_libq95_sr": g.loc[g.same_run == 1, "lib_null_q95_sr"].median(),
                "med_libq95_all": g["lib_null_q95_all"].median(),
                "med_shuffle_q95": g["null_p95_omega"].median(),
                "shuffle_exceed": g["exceed_omega"].mean(),
                "lib_exceed_all": g["lib_exceed_all"].mean(),
                "lib_exceed_sr": g.loc[g.same_run == 1, "lib_exceed_sr"].mean(),
            }
        )
    scale = pd.DataFrame(scale_rows)
    scale["libq95_over_shuffleq95"] = scale["med_libq95_sr"] / scale["med_shuffle_q95"]

    # --- stratum rates ----------------------------------------------------
    def rate(sub, col):
        m = sub[col].notna() if sub[col].dtype == float else slice(None)
        s = sub.loc[m] if isinstance(m, pd.Series) else sub
        r = s[col].mean()
        lo, hi = wilson(r, len(s))
        return len(s), r, lo, hi

    strata = {
        "all_T1": t1,
        "same_run": t1[t1.same_run == 1],
        "cross_run": t1[t1.same_run == 0],
        "strict_block": t1[t1.strict == 1],
    }
    table = []
    for name, sub in strata.items():
        n_shuffle, r_shuffle, lo_s, hi_s = rate(sub, "exceed_omega")
        n_liba, r_liba, lo_a, hi_a = rate(sub, "lib_exceed_all")
        n_libs, r_libs, lo_s2, hi_s2 = rate(sub, "lib_exceed_sr")
        table.append(
            {
                "stratum": name,
                "n_pairs": len(sub),
                "shuffle_null_exceed": r_shuffle,
                "shuffle_ci": (lo_s, hi_s),
                "libnull_all_exceed": r_liba,
                "libnull_all_ci": (lo_a, hi_a),
                "libnull_sr_exceed": r_libs,
                "libnull_sr_ci": (lo_s2, hi_s2),
                "libnull_sr_n": n_libs,
            }
        )

    # --- mechanism attribution on the strict block -----------------------
    sb = t1[t1.strict == 1]
    exc = sb[sb.exceed_omega == 1]
    nonexc = sb[sb.exceed_omega == 0]
    mech = {
        "strict_n": len(sb),
        "strict_shuffle_exceed": sb.exceed_omega.mean(),
        "strict_exceeders_cal_median": exc.cal_omega.median() if len(exc) else np.nan,
        "strict_nonexceeders_cal_median": nonexc.cal_omega.median(),
        "strict_exceeders_n_ratio_median": exc.n_ratio.median() if len(exc) else np.nan,
        "strict_nonexceeders_n_ratio_median": nonexc.n_ratio.median(),
        "strict_libexceed_sr": sb.lib_exceed_sr.mean(),
        "n_ratio_bins_shuffle_exceed": {
            f"{lo}-{hi}": (
                lambda s: (
                    len(s),
                    s.exceed_omega.mean() if len(s) else np.nan,
                    s.lib_exceed_sr.mean() if len(s) else np.nan,
                )
            )(sb[(sb.n_ratio >= lo) & (sb.n_ratio < hi)])
            for lo, hi in [(0, 0.7), (0.7, 0.9), (0.9, 1.01)]
        },
    }

    # n_ratio bins over ALL T1 (library-aware vs shuffle)
    bins_all = {}
    for lo, hi in [(0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.01)]:
        s = t1[(t1.n_ratio >= lo) & (t1.n_ratio < hi)]
        srs = s[s.same_run == 1]
        bins_all[f"{lo}-{hi}"] = {
            "n": len(s),
            "shuffle_exceed": s.exceed_omega.mean(),
            "libnull_all_exceed": s.lib_exceed_all.mean(),
            "n_same_run": len(srs),
            "libnull_sr_exceed": srs.lib_exceed_sr.mean() if len(srs) else np.nan,
        }

    # --- outputs ----------------------------------------------------------
    keep_cols = [
        "cell_type", "sample_a", "sample_b", "roi_a", "donor_a",
        "n_cells_a", "n_cells_b", "n_ratio", "same_run", "strict",
        "omega", "null_med_omega", "null_p95_omega", "cal_omega",
        "exceed_omega", "lib_null_q95_sr", "lib_null_q95_all",
        "lib_exceed_sr", "lib_exceed_all",
    ]
    t1[keep_cols].to_csv(OUT_CSV, index=False)

    summary = {
        "design": (
            "class-level run-matched library-aware null; T1 pairs of the same "
            "cell class and run-match stratum, leave-self-out q95"
        ),
        "decision_rule": (
            "~5% => exceedance under the per-pair sampling null measures real "
            "library effects and omega is calibrated against library-aware "
            "noise; >10% => per-pair null still anti-conservative"
        ),
        "strata": table,
        "mechanism_strict_block": mech,
        "n_ratio_bins_all_T1": bins_all,
        "per_class_scale": scale.to_dict(orient="records"),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, default=float))

    lines = []
    lines.append("nc80 T1 library-aware null (panel M-D / stat Q6)")
    lines.append("=" * 60)
    lines.append(
        "Null: class x run-stratum leave-self-out q95 of observed omega "
        "between libraries (same-donor, same-region, same-class, other blocks)."
    )
    lines.append("")
    lines.append(f"{'stratum':<14} {'n':>5} {'shuffle':>8} {'lib(all)':>9} {'lib(sr)':>8} {'n_sr':>5}")
    for row in table:
        lines.append(
            f"{row['stratum']:<14} {row['n_pairs']:>5} "
            f"{row['shuffle_null_exceed']:>8.3f} "
            f"{row['libnull_all_exceed']:>9.3f} "
            f"{row['libnull_sr_exceed']:>8.3f} "
            f"{row['libnull_sr_n']:>5}"
        )
    lines.append("")
    lines.append("Per-class noise scale (median library-null q95 / median cell-shuffle q95):")
    for r in scale.to_dict(orient="records"):
        lines.append(
            f"  {r['cell_type']:<42} ratio={r['libq95_over_shuffleq95']:.2f} "
            f"shuffle_exceed={r['shuffle_exceed']:.3f} lib_exceed(all)={r['lib_exceed_all']:.3f}"
        )
    lines.append("")
    lines.append("Mechanism (strictly matched block, n=1,334):")
    for k, v in mech.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                lines.append(f"  n_ratio {kk}: n={vv[0]} shuffle={vv[1]:.3f} lib_sr={vv[2]:.3f}")
        else:
            lines.append(f"  {k}: {v}")
    OUT_TXT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {OUT_CSV.name}, {OUT_JSON.name}, {OUT_TXT.name}")


if __name__ == "__main__":
    main()
