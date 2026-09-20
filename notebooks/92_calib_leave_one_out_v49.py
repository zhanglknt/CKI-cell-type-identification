"""
v49.13 B3: leave-one-population-out sensitivity of the empirical calibration
constant omega_cal baseline (7.70, from mouse split-half control populations).
============================================================================
Reviewer: R1-N1. SI Section 3.10 reports six control populations (50 split-half
replicates each); the global mean 7.70 is inflated ~13% by the hepatocyte
outlier (12.44 +/- 5.98 vs 5.77-7.36 for the other five).

This script reports:
  1. per-population mean/SD (reproduces SI 3.10 numbers);
  2. leave-one-population-out baselines (6 values, range);
  3. robust (median-of-population-means) baseline;
  4. rescaling of the manuscript's omega_cal anchor values under each LOO
     baseline (brain grand mean, astrocyte class mean, Bergmann glia class
     mean) with the direction of change made explicit.

Input : results/mouse_splithalf_v44.csv  (script 87, seed 42, 50 splits x 6 pops)
Output: results/nc49_calib_leave_one_out.csv
        results/nc49_calib_leave_one_out.txt
Seed  : 42 (no stochastic component beyond the input file; deterministic).
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
IN = ROOT / "results" / "mouse_splithalf_v44.csv"
OUT = ROOT / "results" / "nc49_calib_leave_one_out.csv"
OUT_TXT = ROOT / "results" / "nc49_calib_leave_one_out.txt"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

df = pd.read_csv(IN)
pop = df.groupby(["tissue", "cell_type"]).omega.agg(["mean", "std", "count"])
log("Per-population split-half omega (50 reps each):")
log(pop.round(3).to_string())

base_full = float(pop["mean"].mean())
log("")
log(f"Global baseline (mean of 6 population means): {base_full:.3f}  "
    f"(manuscript value 7.70)")

# --- leave-one-population-out ---
loo_rows = []
for (t, c) in pop.index:
    kept = pop.drop(index=(t, c))
    b = float(kept["mean"].mean())
    loo_rows.append({"removed_population": f"{t} {c}",
                     "removed_mean": round(float(pop.loc[(t, c), 'mean']), 3),
                     "loo_baseline": round(b, 3),
                     "pct_change_vs_full": round(100 * (b - base_full) / base_full, 1)})
loo = pd.DataFrame(loo_rows)
log("")
log("Leave-one-population-out baselines:")
log(loo.to_string(index=False))

loo_min = loo.loo_baseline.min()
loo_max = loo.loo_baseline.max()
base_no_hep = float(loo.loc[loo.removed_population.str.contains("hepatocyte"),
                            "loo_baseline"].iloc[0])
base_median = float(np.median(pop["mean"].values))
log("")
log(f"LOO range: [{loo_min:.2f}, {loo_max:.2f}]; "
    f"excluding hepatocyte: {base_no_hep:.2f} "
    f"({100*(base_no_hep-base_full)/base_full:+.1f}%); "
    f"median-of-population-means baseline: {base_median:.2f} "
    f"({100*(base_median-base_full)/base_full:+.1f}%)")

# --- rescale manuscript omega_cal anchors ---
# anchors: brain grand mean omega (t=20 observed pairs), astrocyte and
# Bergmann glia class means (same source, results/brain_v44_class_confound.csv)
cc = pd.read_csv(ROOT / "results" / "brain_v44_class_confound.csv")
obs = pd.read_csv(ROOT / "results" / "brain_bs_null_observed_pairs.csv")
grand = float(obs["omega"].mean())
astro = float(cc.loc[cc.cell_type == "Astrocyte", "omega_mean"].iloc[0])
berg = float(cc.loc[cc.cell_type == "Bergmann glia", "omega_mean"].iloc[0])
log("")
log(f"Anchors (raw omega): brain grand mean = {grand:.2f}, astrocyte = {astro:.2f}, "
    f"Bergmann glia = {berg:.2f}")

anchor_rows = []
for name, b in [("full 7.70 (manuscript)", base_full),
                ("LOO excl. hepatocyte", base_no_hep),
                ("LOO min (most conservative upward)", loo_min),
                ("LOO max", loo_max),
                ("median-of-means", base_median)]:
    anchor_rows.append({
        "baseline": name, "baseline_value": round(b, 2),
        "omega_cal_brain_grand": round(grand / b, 2),
        "omega_cal_astrocyte": round(astro / b, 2),
        "omega_cal_bergmann_glia": round(berg / b, 2),
    })
anchor = pd.DataFrame(anchor_rows)
log("")
log("omega_cal anchors under alternative baselines:")
log(anchor.to_string(index=False))

log("")
log("Direction: a smaller baseline (e.g. excluding hepatocyte, "
    f"{base_no_hep:.2f}) raises every omega_cal by "
    f"{100*(base_full/base_no_hep-1):.0f}%; Bergmann glia omega_cal moves from "
    f"{berg/base_full:.2f} to {berg/base_no_hep:.2f} (further above 1); "
    "astrocyte from {:.2f} to {:.2f}. The astrocyte-over-Bergmann-glia "
    "ordering and all ratio statements are baseline-invariant; only absolute "
    "omega_cal magnitudes shift.".format(astro/base_full, astro/base_no_hep))

pd.concat([loo.assign(table="loo_baseline"), anchor.assign(table="anchors")],
          ignore_index=True).to_csv(OUT, index=False)
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
log("")
log("saved: " + str(OUT) + ", " + str(OUT_TXT))
