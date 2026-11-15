"""
C-S3 v2: Per-signal empirical P-values for residual model
=========================================================
Instead of counting total Strong/Moderate/Weak signals per permutation,
compute per-signal P-values: for each (ct, region_pair), what is the
probability of getting a residual that low under the null?

Null: shuffle CT labels within each region pair, recompute residuals.
For each observed signal, P = (count(null_residual <= observed) + 1) / (B + 1)

Output: results/phaseB_residual_pervisign.csv
        results/phaseB_residual_null.json (updated)
"""

import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from pathlib import Path

B_PERM = 10000
RANDOM_SEED = 42
rng = np.random.RandomState(RANDOM_SEED)

# ============================================================
# Load brain omega pairs
# ============================================================
print("Loading brain omega pairs...")
df = pd.read_csv(RESULTS_DIR / "brain_siletti_omega_pairs_v3.csv")
print(f"  Total pairs: {len(df):,}, Cell types: {df['cell_type'].nunique()}")

# Compute observed residuals
mu_grand = df["omega"].mean()
mu_ct = df.groupby("cell_type")["omega"].mean().to_dict()
mu_pair = df.groupby(["region_a", "region_b"])["omega"].mean().to_dict()

df["mu_ct"] = df["cell_type"].map(mu_ct)
df["mu_pair"] = df.apply(
    lambda r: mu_pair.get((r["region_a"], r["region_b"]), mu_grand), axis=1
)
df["expected_omega"] = df["mu_ct"] * df["mu_pair"] / mu_grand
df["observed_residual"] = df["omega"] / df["expected_omega"]

# Observed tiers (before 'lowest ω in pair' filter)
obs_strong_mask = (df["observed_residual"] < 0.3) & (df["omega"] < 15)
obs_moderate_mask = (df["observed_residual"] < 0.5) & (df["omega"] < 25)
obs_weak_mask = (df["observed_residual"] < 0.75) & (df["omega"] < 35)

n_strong = int(obs_strong_mask.sum())
n_moderate = int(obs_moderate_mask.sum())
n_weak = int(obs_weak_mask.sum())
print(f"  Observed: Strong={n_strong}, Moderate={n_moderate}, Weak={n_weak}")

# ============================================================
# Permutation null: per-signal P-values
# ============================================================
print(f"\nRunning {B_PERM:,} permutations (per-signal tracking)...")

# Pre-index: for each region pair, get the row indices
pair_groups = df.groupby(["region_a", "region_b"]).indices
pair_keys = list(pair_groups.keys())
pair_indices = [pair_groups[k] for k in pair_keys]

# Extract arrays
omegas = df["omega"].values
ct_labels = df["cell_type"].values
mu_pair_arr = df["mu_pair"].values
obs_residuals = df["observed_residual"].values
n_total = len(df)

# Per-signal null counts: how many times null_residual <= observed_residual
# Lower counts → more significant (the observed is more extreme than most nulls)
null_le_count = np.zeros(n_total, dtype=np.int32)

t0 = time.time()
for b in range(B_PERM):
    # Shuffle CT labels within each region pair
    perm_ct = ct_labels.copy()
    for idx_array in pair_indices:
        if len(idx_array) > 1:
            perm_ct[idx_array] = rng.permutation(perm_ct[idx_array])

    # Compute permuted mu_ct
    perm_df = pd.DataFrame({"ct": perm_ct, "omega": omegas})
    perm_mu_ct = perm_df.groupby("ct")["omega"].mean().to_dict()
    perm_mu_ct_arr = np.array([perm_mu_ct[c] for c in perm_ct])

    # Compute permuted residuals
    expected = perm_mu_ct_arr * mu_pair_arr / mu_grand
    # Avoid division by zero
    expected_safe = np.where(expected > 0, expected, 1e-10)
    perm_residuals = omegas / expected_safe

    # Per-signal: count how many times null residual <= observed
    # (one-sided test: is the observed residual unusually LOW?)
    null_le_count += (perm_residuals <= obs_residuals).astype(np.int32)

    if (b + 1) % 1000 == 0:
        elapsed = time.time() - t0
        eta = elapsed / (b + 1) * (B_PERM - b - 1)
        print(f"  Iter {b+1}/{B_PERM}, elapsed={elapsed:.0f}s, ETA={eta:.0f}s")

# Compute per-signal P-values
# P = (count(null <= observed) + 1) / (B + 1)
# This is a one-sided test: H0 = residual is not unusually low
# Low P = observed residual is more extreme (lower) than most null residuals
p_values = (null_le_count + 1) / (B_PERM + 1)

# Add to dataframe
df["null_le_count"] = null_le_count
df["p_value"] = p_values

# Apply BH-FDR across ALL 31,764 pairs
from cki.bootstrap import benjamini_hochberg
q_values = benjamini_hochberg(p_values)
df["q_value"] = q_values

# ============================================================
# Results
# ============================================================
print("\n" + "=" * 60)
print("Per-signal results")
print("=" * 60)

# Overall signal statistics
print(f"\n  All {n_total:,} pairs:")
print(f"    P < 0.05: {int(np.sum(p_values < 0.05)):,}")
print(f"    P < 0.01: {int(np.sum(p_values < 0.01)):,}")
print(f"    P < 0.001: {int(np.sum(p_values < 0.001)):,}")
print(f"    FDR < 0.05: {int(np.sum(q_values < 0.05)):,}")
print(f"    FDR < 0.01: {int(np.sum(q_values < 0.01)):,}")

# Strong tier analysis
strong_df = df[obs_strong_mask].copy()
print(f"\n  Strong tier (residual<0.3, ω<15): {n_strong} signals")
print(f"    P < 0.05: {int((strong_df['p_value'] < 0.05).sum())}/{n_strong}")
print(f"    P < 0.01: {int((strong_df['p_value'] < 0.01).sum())}/{n_strong}")
print(f"    FDR < 0.05: {int((strong_df['q_value'] < 0.05).sum())}/{n_strong}")
print(f"    P-value range: [{strong_df['p_value'].min():.4e}, {strong_df['p_value'].max():.4e}]")
print(f"    Q-value range: [{strong_df['q_value'].min():.4e}, {strong_df['q_value'].max():.4e}]")

# Moderate tier
moderate_df = df[obs_moderate_mask].copy()
print(f"\n  Moderate tier (residual<0.5, ω<25): {n_moderate} signals")
print(f"    P < 0.05: {int((moderate_df['p_value'] < 0.05).sum())}/{n_moderate}")
print(f"    FDR < 0.05: {int((moderate_df['q_value'] < 0.05).sum())}/{n_moderate}")

# Weak tier
weak_df = df[obs_weak_mask].copy()
print(f"\n  Weak tier (residual<0.75, ω<35): {n_weak} signals")
print(f"    P < 0.05: {int((weak_df['p_value'] < 0.05).sum())}/{n_weak}")
print(f"    FDR < 0.05: {int((weak_df['q_value'] < 0.05).sum())}/{n_weak}")

# Save per-signal results
out_cols = ["cell_type", "region_a", "region_b", "omega", "kn", "kf",
            "expected_omega", "observed_residual", "null_le_count", "p_value", "q_value"]
df[out_cols].to_csv(RESULTS_DIR / "phaseB_residual_pervisign.csv", index=False)
print(f"\n  Saved: results/phaseB_residual_pervisign.csv ({len(df):,} rows)")

# Update JSON summary
summary = {
    "method": "per-signal permutation test",
    "null_hypothesis": "CT labels are randomly assigned within each region pair",
    "test": "one-sided: P(null_residual <= observed_residual)",
    "B": B_PERM,
    "n_total_pairs": int(n_total),
    "mu_grand": round(float(mu_grand), 4),
    "observed_counts": {
        "strong": n_strong,
        "moderate": n_moderate,
        "weak": n_weak,
    },
    "overall_significance": {
        "p_lt_005": int(np.sum(p_values < 0.05)),
        "p_lt_001": int(np.sum(p_values < 0.01)),
        "p_lt_0001": int(np.sum(p_values < 0.001)),
        "fdr_lt_005": int(np.sum(q_values < 0.05)),
        "fdr_lt_001": int(np.sum(q_values < 0.01)),
    },
    "strong_tier": {
        "n": n_strong,
        "p_lt_005": int((strong_df['p_value'] < 0.05).sum()),
        "p_lt_001": int((strong_df['p_value'] < 0.01).sum()),
        "fdr_lt_005": int((strong_df['q_value'] < 0.05).sum()),
        "p_range": [float(f"{strong_df['p_value'].min():.4e}"),
                     float(f"{strong_df['p_value'].max():.4e}")],
        "q_range": [float(f"{strong_df['q_value'].min():.4e}"),
                     float(f"{strong_df['q_value'].max():.4e}")],
    },
    "moderate_tier": {
        "n": n_moderate,
        "p_lt_005": int((moderate_df['p_value'] < 0.05).sum()),
        "fdr_lt_005": int((moderate_df['q_value'] < 0.05).sum()),
    },
    "weak_tier": {
        "n": n_weak,
        "p_lt_005": int((weak_df['p_value'] < 0.05).sum()),
        "fdr_lt_005": int((weak_df['q_value'] < 0.05).sum()),
    },
}

with open(RESULTS_DIR / "phaseB_residual_null.json", 'w') as f:
    json.dump(summary, f, indent=2)
print(f"  Saved: results/phaseB_residual_null.json")

print("\nDone! C-S3 per-signal analysis complete.")
