"""
CKI Brain Bootstrap (CSV-based, fast)
============================================
Works on brain_siletti_omega_pairs_v3.csv.
For each cell type, bootstrap the mean omega.
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import percentileofscore

# RESULTS_DIR from _paths
N_BOOTSTRAP = 1000
RANDOM_STATE = 42

print("=" * 60)
print("Brain CKI Bootstrap (B=1000, CSV-based)")
print("=" * 60)

# === Load data ===
print("\nLoading brain_siletti_omega_pairs_v3.csv...")
df = pd.read_csv(RESULTS_DIR / "brain_siletti_omega_pairs_v3.csv")
print(f"  Loaded: {df.shape[0]} pairs, {df['cell_type'].nunique()} cell types")

# === Bootstrap per cell type ===
print(f"\nBootstrapping per cell type (B={N_BOOTSTRAP})...")
rng = np.random.RandomState(RANDOM_STATE)

all_results = []

for ct in sorted(df["cell_type"].unique()):
    sub = df[df["cell_type"] == ct]
    omegas = sub["omega"].values
    n_pairs = len(omegas)
    
    if n_pairs < 10:
        continue
    
    obs_mean = np.mean(omegas)
    obs_median = np.median(omegas)
    obs_std = np.std(omegas)
    
    # Bootstrap: resample pairs with replacement
    boot_means = []
    for b in range(N_BOOTSTRAP):
        sample = rng.choice(omegas, size=n_pairs, replace=True)
        boot_means.append(np.mean(sample))
    
    boot_means = np.array(boot_means)
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    
    # P-value: fraction of bootstrap means >= obs_mean (one-sided)
    p_value = (np.sum(boot_means >= obs_mean) + 1) / (N_BOOTSTRAP + 1)
    
    all_results.append({
        "cell_type": ct,
        "n_pairs": n_pairs,
        "omega_mean": round(obs_mean, 4),
        "omega_median": round(obs_median, 4),
        "omega_std": round(obs_std, 4),
        "ci_95_lower": round(ci_lower, 4),
        "ci_95_upper": round(ci_upper, 4),
        "p_value": f"{p_value:.4e}",
    })

# === Save ===
print("\n" + "=" * 60)
print("Results:")
print("=" * 60)

df_out = pd.DataFrame(all_results)
# Sort by omega_mean descending
df_out = df_out.sort_values("omega_mean", ascending=False)
print(df_out.to_string(index=False))
df_out.to_csv(RESULTS_DIR / "brain_bootstrap_results.csv", index=False)

print(f"\nDone! Saved to brain_bootstrap_results.csv")
print(f"  Gradient (max/min): {df_out['omega_mean'].max() / df_out['omega_mean'].min():.2f}-fold")
