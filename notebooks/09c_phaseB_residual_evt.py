"""
09c_phaseB_residual_evt.py - Extreme Value Theory P-values for residual model
===============================================================================
Resolves P-value saturation in 09b_phaseB_residual_pervisign.py where 36.3%
of signals hit the minimum empirical P-value floor (1/(B+1) = 9.999e-5).

Method: Generalized Pareto Distribution (GPD) tail extrapolation via
Peaks-Over-Threshold (POT). For each signal with null_le_count = 0:

  1. Collect K=500 smallest null residuals from B=10,000 permutations
  2. Set threshold u = K-th smallest null
  3. Compute exceedances: y_i = u - null_i (positive, for the K smallest)
  4. Fit GPD(c, scale) to exceedances via MLE (scipy.stats.genpareto)
  5. EVT P = (K/B) * GPD_survival(u - observed_residual)

For non-saturated signals: use empirical P = (null_le_count + 1) / (B + 1).

Output:
  results/phaseB_residual_evt.csv
  results/phaseB_residual_evt.json
"""

import sys, os, time, json, warnings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats as sp_stats

# ============================================================
# Configuration
# ============================================================
B_PERM = 10000
K_TAIL = 500          # Number of smallest nulls retained for GPD fitting
RANDOM_SEED = 42      # Must match 09b for reproducibility

rng = np.random.RandomState(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ============================================================
# Load brain omega pairs
# ============================================================
print("=" * 60)
print("09c: EVT residual P-values (GPD tail extrapolation)")
print("=" * 60)

print("\n[1/5] Loading brain omega pairs...")
df = pd.read_csv(RESULTS_DIR / "brain_siletti_omega_pairs_v3.csv")
n_total = len(df)
print(f"  Total pairs: {n_total:,}")
print(f"  Cell types: {df['cell_type'].nunique()}")
print(f"  Unique region pairs: {df.groupby(['region_a','region_b']).ngroups}")

# Compute observed residuals (identical to 09b)
mu_grand = float(df["omega"].mean())
mu_ct = df.groupby("cell_type")["omega"].mean().to_dict()
mu_pair = df.groupby(["region_a", "region_b"])["omega"].mean().to_dict()

df["mu_ct"] = df["cell_type"].map(mu_ct)
df["mu_pair"] = df.apply(
    lambda r: mu_pair.get((r["region_a"], r["region_b"]), mu_grand), axis=1
)
df["expected_omega"] = df["mu_ct"] * df["mu_pair"] / mu_grand
df["observed_residual"] = df["omega"] / df["expected_omega"]

# Observed tiers
obs_strong_mask = (df["observed_residual"] < 0.3) & (df["omega"] < 15)
obs_moderate_mask = (df["observed_residual"] < 0.5) & (df["omega"] < 25)
obs_weak_mask = (df["observed_residual"] < 0.75) & (df["omega"] < 35)

print(f"  Observed: Strong={obs_strong_mask.sum()}, Moderate={obs_moderate_mask.sum()}, "
      f"Weak={obs_weak_mask.sum()}")

# ============================================================
# Pre-encode for fast numpy operations
# ============================================================
print("\n[2/5] Pre-encoding data for numpy operations...")

ct_labels = df["cell_type"].values
ct_categories = pd.Categorical(ct_labels)
ct_codes = ct_categories.codes.astype(np.int32)
n_cts = ct_codes.max() + 1

omegas = df["omega"].values.astype(np.float64)
mu_pair_arr = df["mu_pair"].values.astype(np.float64)
obs_residuals = df["observed_residual"].values.astype(np.float64)

# Region pair indices (must use same order as 09b)
pair_groups = df.groupby(["region_a", "region_b"]).indices
pair_keys = list(pair_groups.keys())
pair_indices = [pair_groups[k].astype(np.int32) for k in pair_keys]

print(f"  CT codes: {n_cts} unique")
print(f"  Region pairs: {len(pair_keys)}")
print(f"  Memory for nulls: {B_PERM * n_total * 4 / (1024**3):.2f} GB (float32)")

# ============================================================
# Permutation loop (numpy-optimized)
# ============================================================
print(f"\n[3/5] Running {B_PERM:,} permutations...")

# Pre-allocate storage for all null residuals (float32 to save memory)
all_nulls = np.empty((B_PERM, n_total), dtype=np.float32)
null_le_count = np.zeros(n_total, dtype=np.int32)

t0 = time.time()
for b in range(B_PERM):
    # 1. Shuffle CT labels within each region pair
    perm_ct = ct_codes.copy()  # fast C-level copy
    for idx_array in pair_indices:
        if len(idx_array) > 1:
            perm_ct[idx_array] = rng.permutation(perm_ct[idx_array])

    # 2. Compute mu_ct via bincount (much faster than pandas groupby)
    ct_sums = np.bincount(perm_ct, weights=omegas, minlength=n_cts)
    ct_counts = np.bincount(perm_ct, minlength=n_cts)
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_ct_arr = np.divide(ct_sums, ct_counts, where=ct_counts > 0)
        mu_ct_arr[ct_counts == 0] = mu_grand
    perm_mu_ct_per_signal = mu_ct_arr[perm_ct]

    # 3. Compute permuted residuals
    expected = perm_mu_ct_per_signal * mu_pair_arr / mu_grand
    expected_safe = np.where(expected > 0, expected, 1e-10)
    perm_residuals = omegas / expected_safe

    # 4. Store and count
    all_nulls[b] = perm_residuals.astype(np.float32)
    null_le_count += (perm_residuals <= obs_residuals).astype(np.int32)

    if (b + 1) % 2000 == 0:
        elapsed = time.time() - t0
        eta = elapsed / (b + 1) * (B_PERM - b - 1)
        print(f"  Perm {b+1}/{B_PERM}, elapsed={elapsed:.0f}s, ETA={eta:.0f}s, "
              f"saturated_so_far={int((null_le_count == 0).sum()):,}")

perm_time = time.time() - t0
print(f"  Permutations done in {perm_time:.0f}s ({perm_time/60:.1f} min)")

# ============================================================
# Empirical P-values (for comparison & validation)
# ============================================================
p_empirical = (null_le_count + 1) / (B_PERM + 1)
n_saturated = int((null_le_count == 0).sum())
print(f"  Empirical P-values: {n_saturated:,} saturated (P={p_empirical[null_le_count==0].min():.4e})")

# ============================================================
# EVT analysis: GPD tail extrapolation
# ============================================================
print(f"\n[4/5] Fitting GPD to {K_TAIL}-smallest nulls per signal...")

p_values_evt = np.empty(n_total, dtype=np.float64)
n_evt_success = 0
n_evt_nodata = 0
n_evt_badfit = 0
n_evt_bound = 0

for i in range(n_total):
    # Extract sorted null residuals for this signal
    nulls_i = np.sort(all_nulls[:, i])
    obs_i = obs_residuals[i]
    le_count = int(null_le_count[i])

    if le_count > 0:
        # Non-saturated: use empirical P-value
        p_values_evt[i] = p_empirical[i]
        continue

    # --- Saturated signal: EVT extrapolation ---

    # K_TAIL smallest null residuals
    k_smallest = nulls_i[:K_TAIL]
    u = float(k_smallest[-1])  # threshold = K-th smallest

    # Exceedances over threshold (how far below u the null falls)
    exceedances = u - k_smallest
    exceedances = exceedances[exceedances > 0]  # remove values at threshold

    n_exc = len(exceedances)
    if n_exc < 50:
        p_values_evt[i] = p_empirical[i]
        n_evt_nodata += 1
        continue

    y_obs = float(u - obs_i)
    if y_obs <= 0:
        # observed >= threshold (should not happen for saturated)
        p_values_evt[i] = p_empirical[i]
        n_evt_nodata += 1
        continue

    try:
        # Fit GPD via MLE (fix location at 0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            c, loc, scale = sp_stats.genpareto.fit(exceedances, floc=0)

        if scale <= 0 or not np.isfinite(c) or not np.isfinite(scale):
            p_values_evt[i] = p_empirical[i]
            n_evt_badfit += 1
            continue

        # GPD survival log-probability: log S(y) = log P(Y > y)
        # Compute in log-space to avoid float64 underflow for extreme signals
        log_base = np.log(float(n_exc) / B_PERM)
        if abs(c) < 1e-8:
            # Exponential tail (c ~ 0): S(y) = exp(-y/scale)
            log_s = -y_obs / scale
        elif c < 0:
            # Bounded tail: support is [0, -scale/c]
            bound = -scale / c
            if y_obs >= bound:
                log_s = -np.inf  # beyond support => P=0
            else:
                log_s = (-1.0 / c) * np.log(1.0 + c * y_obs / scale)
        else:
            # Heavy tail (c > 0): S(y) = (1 + c*y/scale)^(-1/c)
            log_s = (-1.0 / c) * np.log(1.0 + c * y_obs / scale)

        # EVT P-value in log-space
        log_p = log_base + log_s

        # Convert to probability, cap at minimum to avoid exact zero
        MIN_P_EVT = 1e-300  # floor: well below any practical significance threshold
        if not np.isfinite(log_p) or log_p < np.log(MIN_P_EVT):
            p_evt = MIN_P_EVT
        else:
            p_evt = float(np.exp(log_p))

        # Sanity: EVT P should not exceed empirical floor
        p_evt = min(p_evt, p_empirical[i])

        p_values_evt[i] = p_evt
        n_evt_success += 1

    except (RuntimeError, ValueError, np.linalg.LinAlgError):
        p_values_evt[i] = p_empirical[i]
        n_evt_badfit += 1
        continue

# Free large array
all_nulls_nbytes = all_nulls.nbytes
del all_nulls
print(f"  Freed null array ({all_nulls_nbytes / 1024**3:.2f} GB)")

print(f"\n  EVT fitting complete:")
print(f"    Saturated signals: {n_saturated:,}")
print(f"    EVT success: {n_evt_success:,}")
print(f"    EVT fallback (insufficient tail data): {n_evt_nodata}")
print(f"    EVT fallback (bad fit): {n_evt_badfit}")
print(f"    EVT fallback (bounded tail): {n_evt_bound}")

# ============================================================
# Summary statistics
# ============================================================
print(f"\n  EVT P-value distribution (saturated signals):")
evt_p_saturated = p_values_evt[null_le_count == 0]
if n_evt_success > 0:
    log10_p = -np.log10(np.maximum(evt_p_saturated, 1e-100))
    for threshold in [2, 3, 4, 5, 6, 8, 10]:
        count = int(np.sum(evt_p_saturated < 10**(-threshold)))
        if count > 0:
            print(f"    P < 1e-{threshold}: {count:,}")

# ============================================================
# Apply BH-FDR
# ============================================================
print(f"\n[5/5] Applying BH-FDR...")
from cki.bootstrap import benjamini_hochberg

q_values_evt = benjamini_hochberg(p_values_evt)
q_values_emp = benjamini_hochberg(p_empirical)

# ============================================================
# Save results
# ============================================================
df["p_value_emp"] = p_empirical
df["q_value_emp"] = q_values_emp
df["p_value_evt"] = p_values_evt
df["q_value_evt"] = q_values_evt

# Tier-specific results
strong_df = df[obs_strong_mask]
moderate_df = df[obs_moderate_mask]
weak_df = df[obs_weak_mask]

# Save CSV
out_cols = ["cell_type", "region_a", "region_b", "omega", "kn", "kf",
            "expected_omega", "observed_residual",
            "p_value_evt", "q_value_evt"]
df[out_cols].to_csv(RESULTS_DIR / "phaseB_residual_evt.csv", index=False)
print(f"  Saved: results/phaseB_residual_evt.csv")

# Save JSON summary
summary = {
    "method": "GPD tail extrapolation (Peaks-Over-Threshold)",
    "description": (
        "For signals with null_le_count=0 (saturated P-value), fits a "
        "Generalized Pareto Distribution to the K=500 smallest null residuals "
        "and extrapolates the P-value below the B=10,000 empirical floor."
    ),
    "parameters": {
        "B_permutations": B_PERM,
        "K_tail": K_TAIL,
        "random_seed": RANDOM_SEED,
    },
    "data": {
        "n_total_pairs": int(n_total),
        "mu_grand": round(mu_grand, 4),
        "n_cell_types": int(df["cell_type"].nunique()),
        "n_region_pairs": int(len(pair_keys)),
    },
    "evt_fitting": {
        "n_saturated": int(n_saturated),
        "n_evt_success": int(n_evt_success),
        "n_evt_fallback_nodata": int(n_evt_nodata),
        "n_evt_fallback_badfit": int(n_evt_badfit),
    },
    "overall_significance": {
        "evt": {
            "p_lt_1e2": int(np.sum(p_values_evt < 0.01)),
            "p_lt_1e3": int(np.sum(p_values_evt < 0.001)),
            "p_lt_1e4": int(np.sum(p_values_evt < 1e-4)),
            "p_lt_1e5": int(np.sum(p_values_evt < 1e-5)),
            "fdr_lt_005": int(np.sum(q_values_evt < 0.05)),
            "fdr_lt_001": int(np.sum(q_values_evt < 0.01)),
        },
        "empirical": {
            "fdr_lt_005": int(np.sum(q_values_emp < 0.05)),
        },
    },
    "strong_tier": {
        "n": int(obs_strong_mask.sum()),
        "evt_fdr_lt_005": int((strong_df["q_value_evt"] < 0.05).sum()),
        "evt_p_min": float(f"{strong_df['p_value_evt'].min():.4e}"),
        "evt_p_max": float(f"{strong_df['p_value_evt'].max():.4e}"),
        "evt_q_min": float(f"{strong_df['q_value_evt'].min():.4e}"),
        "evt_q_max": float(f"{strong_df['q_value_evt'].max():.4e}"),
        "emp_fdr_lt_005": int((strong_df["q_value_emp"] < 0.05).sum()),
    },
    "strong_tier_by_ct": {},
}
for ct in sorted(strong_df["cell_type"].unique()):
    ct_data = strong_df[strong_df["cell_type"] == ct]
    summary["strong_tier_by_ct"][ct] = {
        "n": int(len(ct_data)),
        "evt_fdr_lt_005": int((ct_data["q_value_evt"] < 0.05).sum()),
    }

with open(RESULTS_DIR / "phaseB_residual_evt.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"  Saved: results/phaseB_residual_evt.json")

# ============================================================
# Final comparison report
# ============================================================
print("\n" + "=" * 60)
print("COMPARISON: EVT vs Empirical")
print("=" * 60)

print(f"\n  All {n_total:,} pairs:")
print(f"    EVT: P < 0.05:   {int(np.sum(p_values_evt < 0.05)):>6,}")
print(f"    EVT: P < 1e-3:   {int(np.sum(p_values_evt < 1e-3)):>6,}")
print(f"    EVT: P < 1e-4:   {int(np.sum(p_values_evt < 1e-4)):>6,}")
print(f"    EVT: P < 1e-5:   {int(np.sum(p_values_evt < 1e-5)):>6,}")
print(f"    EVT: FDR < 0.05: {int(np.sum(q_values_evt < 0.05)):>6,}")
print(f"    Emp: FDR < 0.05: {int(np.sum(q_values_emp < 0.05)):>6,}")
print(f"    EVT: FDR < 0.01: {int(np.sum(q_values_evt < 0.01)):>6,}")
print(f"    Emp: FDR < 0.01: {int(np.sum(q_values_emp < 0.01)):>6,}")

print(f"\n  Strong tier ({obs_strong_mask.sum()} signals):")
print(f"    EVT P range: [{strong_df['p_value_evt'].min():.4e}, {strong_df['p_value_evt'].max():.4e}]")
print(f"    EVT Q range: [{strong_df['q_value_evt'].min():.4e}, {strong_df['q_value_evt'].max():.4e}]")
print(f"    EVT FDR < 0.05: {(strong_df['q_value_evt'] < 0.05).sum()}/{len(strong_df)}")
print(f"    Emp FDR < 0.05: {(strong_df['q_value_emp'] < 0.05).sum()}/{len(strong_df)}")

print(f"\n  Moderate tier ({obs_moderate_mask.sum()} signals):")
print(f"    EVT FDR < 0.05: {(moderate_df['q_value_evt'] < 0.05).sum()}/{len(moderate_df)}")

print(f"\n  Weak tier ({obs_weak_mask.sum()} signals):")
print(f"    EVT FDR < 0.05: {(weak_df['q_value_evt'] < 0.05).sum()}/{len(weak_df)}")

print("\nDone! 09c EVT analysis complete.")
