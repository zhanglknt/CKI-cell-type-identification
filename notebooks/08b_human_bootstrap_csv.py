"""
CKI Human (Tabula Sapiens) Bootstrap (CSV-based)
=====================================================
Works on phase33_v3_human_pairs.csv.
Bootstrap mean omega for: same_organ, cross-organ, same_ct, cross-ct.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
N_BOOTSTRAP = 1000
RANDOM_STATE = 42

print("=" * 60)
print("Human (Tabula Sapiens) CKI Bootstrap (B=1000, CSV-based)")
print("=" * 60)

# === Load data ===
print("\nLoading phase33_v3_human_pairs.csv...")
df = pd.read_csv(RESULTS_DIR / "phase33_v3_human_pairs.csv")
print(f"  Loaded: {df.shape[0]} pairs")
print(f"  Columns: {df.columns.tolist()}")

# === Define groups ===
groups = {
    "same_organ_same_ct":    df[df["same_organ"] & df["same_ct"]],
    "same_organ_diff_ct":    df[df["same_organ"] & ~df["same_ct"]],
    "diff_organ_same_ct":   df[~df["same_organ"] & df["same_ct"]],
    "diff_organ_diff_ct":   df[~df["same_organ"] & ~df["same_ct"]],
}

# === Bootstrap mean omega for each group ===
print(f"\nBootstrapping (B={N_BOOTSTRAP})...")
rng = np.random.RandomState(RANDOM_STATE)

all_results = []

for gname, gdf in groups.items():
    omegas = gdf["omega"].values
    n = len(omegas)
    if n < 10:
        print(f"  {gname}: SKIP (n={n})")
        continue

    obs_mean = float(np.mean(omegas))
    obs_median = float(np.median(omegas))
    obs_std = float(np.std(omegas))

    # Bootstrap: resample with replacement
    boot_means = []
    for b in range(N_BOOTSTRAP):
        sample = rng.choice(omegas, size=n, replace=True)
        boot_means.append(float(np.mean(sample)))

    boot_means = np.array(boot_means)
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))

    # One-sided P-value: fraction of bootstrap means >= obs_mean
    p_ge = (np.sum(boot_means >= obs_mean) + 1) / (N_BOOTSTRAP + 1)

    all_results.append({
        "group": gname,
        "n_pairs": n,
        "omega_mean": round(obs_mean, 4),
        "omega_median": round(obs_median, 4),
        "omega_std": round(obs_std, 4),
        "ci_95_lower": round(ci_lower, 4),
        "ci_95_upper": round(ci_upper, 4),
        "p_ge_obs": f"{p_ge:.4e}",
    })

    print(f"  {gname}: n={n}, mean={obs_mean:.2f}, 95% CI [{ci_lower:.2f}, {ci_upper:.2f}]")

# === Also bootstrap: correlation-like contrast (cross-organ / same-organ ratio) ===
print(f"\nBootstrap: cross-organ vs same-organ contrast...")

same_org = df[df["same_organ"]]["omega"].values
cross_org = df[~df["same_organ"]]["omega"].values

# Observed: ratio of means
obs_ratio = float(np.mean(cross_org) / np.mean(same_org)) if np.mean(same_org) > 0 else 0.0

# Bootstrap the ratio
boot_ratios = []
n_s = len(same_org)
n_c = len(cross_org)
for b in range(N_BOOTSTRAP):
    s_sample = rng.choice(same_org, size=n_s, replace=True)
    c_sample = rng.choice(cross_org, size=n_c, replace=True)
    r = float(np.mean(c_sample) / np.mean(s_sample)) if np.mean(s_sample) > 0 else 0.0
    boot_ratios.append(r)

boot_ratios = np.array(boot_ratios)
ci_lower_r = float(np.percentile(boot_ratios, 2.5))
ci_upper_r = float(np.percentile(boot_ratios, 97.5))
p_ratio = (np.sum(boot_ratios >= obs_ratio) + 1) / (N_BOOTSTRAP + 1)

print(f"  Cross/same organ omega ratio: {obs_ratio:.2f}, 95% CI [{ci_lower_r:.2f}, {ci_upper_r:.2f}]")

all_results.append({
    "group": "cross_vs_same_organ_ratio",
    "n_pairs": n_c + n_s,
    "omega_mean": round(obs_ratio, 4),
    "omega_median": "",
    "omega_std": "",
    "ci_95_lower": round(ci_lower_r, 4),
    "ci_95_upper": round(ci_upper_r, 4),
    "p_ge_obs": f"{p_ratio:.4e}",
})

# === Save results ===
print("\n" + "=" * 60)
print("Results:")
print("=" * 60)

df_out = pd.DataFrame(all_results)
print("\n" + df_out.to_string(index=False))
df_out.to_csv(RESULTS_DIR / "human_bootstrap_results.csv", index=False)

print(f"\nDone! Saved to human_bootstrap_results.csv")
