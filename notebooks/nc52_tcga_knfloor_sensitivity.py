# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B7): kn_floor sensitivity of the five-cancer
NN/TT omega reversal.

The TCGA omega uses a denominator floor: when k_n < kn_floor, omega is
computed as k_f / kn_floor (the published value is 1e-4). Reviewers (R1/R3)
asked how the NN/TT reversal depends on that choice. This table recomputes
omega = k_f / max(k_n, floor) pair-by-pair from the stored k_n / k_f columns
(no expression-matrix recompute needed) for

    kn_floor in {0, 1e-5, 1e-4, 1e-3}

(floor = 0 is the raw guard: k_n <= 0 -> omega = inf; inf pairs are excluded
from means and their count reported), on the ex-CC default cohort, under both
probability mappings:

  linear  : results/tcga_linear_norm_v44_all_pairs.csv (ex-CC filtered)
  softmax : results/nc52_tcga_softmax_all_pairs.csv    (ex-CC filtered)

Per cancer x floor: omega_TT_mean, omega_NN_mean, NN/TT ratio, fraction of
pairs at/below the floor (truncated), and the reversal-magnitude change vs
the published 1e-4 reference (delta ratio).

Outputs:
  results/nc52_tcga_knfloor_sensitivity.csv
Seed: not applicable (deterministic aggregation of stored pair values).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LIN = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
SOFT = ROOT / "results" / "nc52_tcga_softmax_all_pairs.csv"
OUT = ROOT / "results" / "nc52_tcga_knfloor_sensitivity.csv"

FLOORS = [0.0, 1e-5, 1e-4, 1e-3]
REF_FLOOR = 1e-4
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    s = str(s)
    return len(s) >= 7 and s[5:7] == "CC"

tables = {"linear": pd.read_csv(LIN), "softmax": pd.read_csv(SOFT)}

rows = []
for mapping, df in tables.items():
    df = df[df.pair_type.isin(["TT", "NN"])].copy()
    cc_mask = df.sample_a.map(is_cc) | df.sample_b.map(is_cc)
    df = df[~cc_mask]
    log(f"{mapping}: ex-CC pairs TT+NN = {len(df)}")
    # reference ratios at 1e-4
    ref_ratio = {}
    for c in CANCERS:
        sub = df[df.cancer == c]
        for floor in FLOORS:
            rec = {"mapping": mapping, "cancer": c, "kn_floor": floor}
            for ptype in ["TT", "NN"]:
                s = sub[sub.pair_type == ptype]
                kn = s.kn.values
                kf = s.kf.values
                if floor > 0:
                    at_floor = kn < floor
                    omega = kf / np.maximum(kn, floor)
                    n_inf = 0
                else:
                    at_floor = kn <= 0
                    with np.errstate(divide="ignore", invalid="ignore"):
                        omega = np.where(kn > 0, kf / np.where(kn > 0, kn, 1.0),
                                         np.inf)
                    n_inf = int(np.isinf(omega).sum())
                    omega = omega[np.isfinite(omega)]
                rec[f"omega_{ptype}_mean"] = round(float(np.mean(omega)), 3)
                rec[f"frac_{ptype}_at_floor"] = round(float(at_floor.mean()), 5)
                if floor == 0:
                    rec[f"n_{ptype}_inf_dropped"] = n_inf
            ratio = rec["omega_NN_mean"] / rec["omega_TT_mean"]
            rec["NN_TT_ratio"] = round(ratio, 4)
            if floor == REF_FLOOR:
                ref_ratio[c] = ratio
            rows.append(rec)
    for rec in rows:
        if rec["mapping"] == mapping:
            rec["delta_ratio_vs_1e-4"] = round(
                rec["NN_TT_ratio"] - ref_ratio[rec["cancer"]], 4)

out = pd.DataFrame(rows)
# column order
cols = ["mapping", "cancer", "kn_floor", "omega_TT_mean", "omega_NN_mean",
        "NN_TT_ratio", "delta_ratio_vs_1e-4", "frac_TT_at_floor",
        "frac_NN_at_floor", "n_TT_inf_dropped", "n_NN_inf_dropped"]
out = out.reindex(columns=cols)
OUT.write_text(out.to_csv(index=False), encoding="utf-8")

log("")
for mapping in tables:
    log(f"--- {mapping} ---")
    for c in CANCERS:
        sub = out[(out.mapping == mapping) & (out.cancer == c)]
        r = {f: sub.loc[sub.kn_floor == f, "NN_TT_ratio"].iloc[0] for f in FLOORS}
        span = max(r.values()) - min(r.values())
        log(f"{c}: NN/TT by floor 0={r[0.0]:.3f} 1e-5={r[1e-5]:.3f} "
            f"1e-4={r[1e-4]:.3f} 1e-3={r[1e-3]:.3f} (span={span:.3f})")
log("")
log("saved: " + str(OUT))
print("DONE")
