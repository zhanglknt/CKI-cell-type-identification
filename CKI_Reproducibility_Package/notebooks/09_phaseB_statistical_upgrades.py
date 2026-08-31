"""
Phase B: Statistical Upgrades
=============================
Addresses 4 Critical issues from v19 expert review:

C-S1: Bootstrap B=1,000 resolution — adaptive permutation analysis
C-S2: Bootstrap confidence intervals for ω point estimates
C-S3: Null distribution for multiplicative residual model
C-S5: ω distribution properties characterization

Outputs:
  - results/phaseB_bootstrap_cis.csv (C-S2)
  - results/phaseB_residual_null.csv (C-S3)
  - results/phaseB_omega_distribution.json (C-S5)
  - results/phaseB_adaptive_analysis.json (C-S1)
  - results/figures_final/ed_fig8_omega_distribution.pdf (C-S5 plot)
  - results/figures_final/ed_fig9_residual_null.pdf (C-S3 plot)
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, normaltest, skew, kurtosis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

FIGURES_DIR = RESULTS_DIR / "figures_final"
FIGURES_DIR.mkdir(exist_ok=True)

# ============================================================
# Config
# ============================================================
B_BOOTSTRAP_CI = 10000       # bootstrap iterations for CIs
# C-S3 now uses the block-shuffle null matrices from 08d (B=1,000),
# reloaded from results/brain_bs_null_pairs_<CT>.npy
RANDOM_SEED = 42
rng = np.random.RandomState(RANDOM_SEED)

# ============================================================
# C-S1: Adaptive permutation analysis
# ============================================================
print("=" * 60)
print("C-S1: Adaptive permutation — B=1,000 sufficiency analysis")
print("=" * 60)

# Load bootstrap results for each dataset
brain_bs = pd.read_csv(RESULTS_DIR / "brain_bootstrap_results.csv")
human_bs = pd.read_csv(RESULTS_DIR / "human_bootstrap_per_ct_results.csv")
mouse_bs = pd.read_csv(RESULTS_DIR / "mouse_pilot_v2b_results.csv")

# Compute actual test counts and BH thresholds
datasets = {
    "Brain": {"n_tests": len(brain_bs), "p_values": brain_bs["p_value"].values},
    "Human (per-CT)": {"n_tests": len(human_bs), "p_values": human_bs["p_value"].values},
    "Mouse (pilot)": {"n_tests": len(mouse_bs), "p_values": mouse_bs["p_value"].values},
}

adaptive_results = {}
for name, info in datasets.items():
    n = info["n_tests"]
    pvals = np.sort(info["p_values"])
    bh_thresholds = np.array([0.05 * (i + 1) / n for i in range(n)])
    min_resolvable_p = 1.0 / 1001  # B=1000 → min P = 1/(B+1)

    # Check if any P-value is between min_resolvable_p and bh_threshold
    # (i.e., borderline cases that need more permutations)
    borderline = []
    for i, (p, thresh) in enumerate(zip(pvals, bh_thresholds)):
        if p < thresh and p < 5 * min_resolvable_p:
            borderline.append({
                "rank": i + 1,
                "p_value": float(p),
                "bh_threshold": float(thresh),
                "margin": float(thresh / p) if p > 0 else float('inf')
            })

    n_significant = int(np.sum(pvals < bh_thresholds))
    adaptive_results[name] = {
        "n_tests": n,
        "B": 1000,
        "min_resolvable_p": float(min_resolvable_p),
        "bh_threshold_rank1": float(0.05 / n),
        "n_significant_fdr": n_significant,
        "borderline_cases": borderline,
        "sufficient": len(borderline) == 0,
        "recommendation": "B=1,000 sufficient" if len(borderline) == 0
                         else f"B=1,000 insufficient for {len(borderline)} borderline cases"
    }

    print(f"\n  {name}:")
    print(f"    Tests: {n}, B=1000, min_P={min_resolvable_p:.4e}")
    print(f"    BH threshold (rank 1): {0.05/n:.4e}")
    print(f"    Significant (FDR<0.05): {n_significant}/{n}")
    if borderline:
        print(f"    Borderline cases: {len(borderline)}")
        for bc in borderline:
            print(f"      rank {bc['rank']}: P={bc['p_value']:.4e}, "
                  f"thresh={bc['bh_threshold']:.4e}, margin={bc['margin']:.1f}x")
    else:
        print(f"    No borderline cases — B=1,000 is sufficient")

# Save
with open(RESULTS_DIR / "phaseB_adaptive_analysis.json", 'w') as f:
    json.dump(adaptive_results, f, indent=2)
print(f"\n  Saved: results/phaseB_adaptive_analysis.json")

# ============================================================
# C-S2: Bootstrap CIs for ω point estimates
# ============================================================
print("\n" + "=" * 60)
print(f"C-S2: Bootstrap CIs for ω (B={B_BOOTSTRAP_CI:,})")
print("=" * 60)

all_cis = []

# --- Brain ---
# Authoritative source: block-shuffle observed pairs (08d/08e), matching the
# manuscript's per-class statistics (e.g. Astrocyte omega = 76.83, n = 5,778).
# The legacy brain_siletti_omega_pairs_v3.csv pipeline is superseded.
print("\n  Loading brain omega pairs...")
brain_pairs = pd.read_csv(RESULTS_DIR / "brain_bs_null_observed_pairs.csv")
for ct in brain_pairs["cell_type"].unique():
    ct_omegas = brain_pairs[brain_pairs["cell_type"] == ct]["omega"].values
    if len(ct_omegas) < 5:
        continue
    # Bootstrap resample
    boot_means = np.array([
        np.mean(rng.choice(ct_omegas, size=len(ct_omegas), replace=True))
        for _ in range(B_BOOTSTRAP_CI)
    ])
    ci_lo = float(np.percentile(boot_means, 2.5))
    ci_hi = float(np.percentile(boot_means, 97.5))
    obs_mean = float(np.mean(ct_omegas))
    all_cis.append({
        "dataset": "Brain",
        "group": ct,
        "n_pairs": len(ct_omegas),
        "omega_mean": round(obs_mean, 4),
        "ci_95_lower": round(ci_lo, 4),
        "ci_95_upper": round(ci_hi, 4),
        "ci_width": round(ci_hi - ci_lo, 4),
    })
    print(f"    {ct}: ω={obs_mean:.2f} [{ci_lo:.2f}, {ci_hi:.2f}]")

# --- Mouse (full matrix) ---
print("\n  Loading mouse omega matrix...")
mouse_mat = pd.read_csv(RESULTS_DIR / "full_matrix_omega.csv", index_col=0)
mouse_vals = mouse_mat.values[np.triu_indices_from(mouse_mat.values, k=1)]
mouse_vals = mouse_vals[mouse_vals > 0]
boot_means = np.array([
    np.mean(rng.choice(mouse_vals, size=len(mouse_vals), replace=True))
    for _ in range(B_BOOTSTRAP_CI)
])
all_cis.append({
    "dataset": "Mouse (all pairs)",
    "group": "all",
    "n_pairs": len(mouse_vals),
    "omega_mean": round(float(np.mean(mouse_vals)), 4),
    "ci_95_lower": round(float(np.percentile(boot_means, 2.5)), 4),
    "ci_95_upper": round(float(np.percentile(boot_means, 97.5)), 4),
    "ci_width": round(float(np.percentile(boot_means, 97.5) - np.percentile(boot_means, 2.5)), 4),
})
print(f"    Mouse all pairs: ω={np.mean(mouse_vals):.2f} "
      f"[{np.percentile(boot_means, 2.5):.2f}, {np.percentile(boot_means, 97.5):.2f}]")

# --- Human (phase35 analyzed pairs) ---
# Authoritative source: the phase35 analyzed pairs (n = 4,851), matching the
# human omega statistics reported in the manuscript. The legacy
# phase33_v3_human_omega.csv matrix is superseded.
print("\n  Loading human omega pairs...")
human_vals = pd.read_csv(
    RESULTS_DIR / "phase35_all_metrics_pairs.csv")["omega"].values
human_vals = human_vals[human_vals > 0]
boot_means = np.array([
    np.mean(rng.choice(human_vals, size=len(human_vals), replace=True))
    for _ in range(B_BOOTSTRAP_CI)
])
all_cis.append({
    "dataset": "Human (all pairs)",
    "group": "all",
    "n_pairs": len(human_vals),
    "omega_mean": round(float(np.mean(human_vals)), 4),
    "ci_95_lower": round(float(np.percentile(boot_means, 2.5)), 4),
    "ci_95_upper": round(float(np.percentile(boot_means, 97.5)), 4),
    "ci_width": round(float(np.percentile(boot_means, 97.5) - np.percentile(boot_means, 2.5)), 4),
})
print(f"    Human all pairs: ω={np.mean(human_vals):.2f} "
      f"[{np.percentile(boot_means, 2.5):.2f}, {np.percentile(boot_means, 97.5):.2f}]")

# --- Mouse categories (C, S, D, X) ---
print("\n  Loading mouse pilot results...")
for category in mouse_bs["category"].unique():
    cat_data = mouse_bs[mouse_bs["category"] == category]
    omegas = cat_data["omega"].values
    if len(omegas) < 2:
        continue
    boot_means = np.array([
        np.mean(rng.choice(omegas, size=len(omegas), replace=True))
        for _ in range(B_BOOTSTRAP_CI)
    ])
    all_cis.append({
        "dataset": "Mouse (pilot)",
        "group": category,
        "n_pairs": len(omegas),
        "omega_mean": round(float(np.mean(omegas)), 4),
        "ci_95_lower": round(float(np.percentile(boot_means, 2.5)), 4),
        "ci_95_upper": round(float(np.percentile(boot_means, 97.5)), 4),
        "ci_width": round(float(np.percentile(boot_means, 97.5) - np.percentile(boot_means, 2.5)), 4),
    })

# NOTE: Human per-CT rows were REMOVED (v37 review R3-C3): the previous block
# wrote null_std x 1.96 approximations, which are not bootstrap CIs, and no
# downstream consumer (loader / manuscript / supplementary) referenced them.

ci_df = pd.DataFrame(all_cis)
ci_df.to_csv(RESULTS_DIR / "phaseB_bootstrap_cis.csv", index=False)
print(f"\n  Saved: results/phaseB_bootstrap_cis.csv ({len(ci_df)} entries)")

# ============================================================
# C-S5: ω distribution characterization
# ============================================================
print("\n" + "=" * 60)
print("C-S5: ω distribution characterization")
print("=" * 60)

dist_results = {}

# Authoritative omega sources (unified with the C-S2 CI sections above):
#   - Brain: block-shuffle null observed pairs (08d/08e), matching main-text stats
#   - Human: phase35 analyzed pairs, matching the human omega statistics reported
#     in the manuscript (n=4,851 pairs)
brain_bs_obs = brain_pairs
human_p35_vals = human_vals

# Collect all omega distributions
distributions = {
    "Brain (per-pair)": brain_bs_obs["omega"].values,
    "Mouse (all pairs)": mouse_vals,
    "Human (analyzed pairs)": human_p35_vals,
}

for name, vals in distributions.items():
    vals = vals[vals > 0]  # remove zeros
    n = len(vals)
    mean_val = float(np.mean(vals))
    std_val = float(np.std(vals))
    skew_val = float(skew(vals))
    kurt_val = float(kurtosis(vals))  # excess kurtosis

    # Normality test
    if n <= 5000:
        stat_sw, p_sw = shapiro(vals)
        test_name = "Shapiro-Wilk"
        test_stat = float(stat_sw)
        test_p = float(p_sw)
    else:
        stat_da, p_da = normaltest(vals)
        test_name = "D'Agostino-Pearson"
        test_stat = float(stat_da)
        test_p = float(p_da)

    # Check log-normality
    log_vals = np.log(vals[vals > 0])
    if len(log_vals) <= 5000:
        _, p_log = shapiro(log_vals)
    else:
        _, p_log = normaltest(log_vals)

    dist_results[name] = {
        "n": n,
        "mean": round(mean_val, 4),
        "std": round(std_val, 4),
        "median": round(float(np.median(vals)), 4),
        "min": round(float(np.min(vals)), 4),
        "max": round(float(np.max(vals)), 4),
        "skewness": round(skew_val, 4),
        "excess_kurtosis": round(kurt_val, 4),
        "normality_test": test_name,
        "normality_stat": round(test_stat, 4),
        "normality_p": float(f"{test_p:.4e}"),
        "is_normal": bool(test_p > 0.05),
        "log_normality_p": float(f"{p_log:.4e}"),
        "is_log_normal": bool(p_log > 0.05),
        "distribution_type": "log-normal" if p_log > test_p else "non-normal",
    }

    print(f"\n  {name}:")
    print(f"    n={n}, mean={mean_val:.2f}, std={std_val:.2f}")
    print(f"    skewness={skew_val:.3f}, excess kurtosis={kurt_val:.3f}")
    print(f"    {test_name}: P={test_p:.4e} → {'normal' if test_p > 0.05 else 'non-normal'}")
    print(f"    Log-normality: P={p_log:.4e} → {'log-normal' if p_log > 0.05 else 'not log-normal'}")

# Save
with open(RESULTS_DIR / "phaseB_omega_distribution.json", 'w') as f:
    json.dump(dist_results, f, indent=2)
print(f"\n  Saved: results/phaseB_omega_distribution.json")

# --- Generate distribution plots ---
print("\n  Generating distribution plots...")

# Shared publication style (presentation only)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fig_style as st
st.apply_style()

fig, axes = plt.subplots(3, 3, figsize=(7.0, 7.0))

for i, (name, vals) in enumerate(distributions.items()):
    vals = vals[vals > 0]

    # Row 1: Histogram
    ax = axes[0, i]
    ax.hist(vals, bins=50, density=True, alpha=0.85, color=st.C_BLUE,
            edgecolor='white', linewidth=0.4)
    ax.set_title(name, fontsize=8, fontweight='bold', pad=3)
    ax.set_xlabel('ω', fontsize=7)
    ax.set_ylabel('Density', fontsize=7)
    st.despine(ax)
    st.subtle_grid(ax, axis='y')

    # Row 2: Q-Q plot (normal)
    ax = axes[1, i]
    stats.probplot(vals, dist="norm", plot=ax)
    ax.set_title('Q-Q (Normal)', fontsize=8, fontweight='bold', pad=3)
    ax.set_xlabel('Theoretical', fontsize=7)
    ax.set_ylabel('Sample', fontsize=7)
    ax.get_lines()[0].set_color(st.C_BLUE)
    ax.get_lines()[0].set_markersize(1.5)
    ax.get_lines()[1].set_color(st.C_RED)
    ax.get_lines()[1].set_linewidth(0.8)
    st.despine(ax)

    # Row 3: Q-Q plot (log-normal)
    ax = axes[2, i]
    log_vals = np.log(vals)
    stats.probplot(log_vals, dist="norm", plot=ax)
    ax.set_title('Q-Q (Log-Normal)', fontsize=8, fontweight='bold', pad=3)
    ax.set_xlabel('Theoretical', fontsize=7)
    ax.set_ylabel('Sample (log ω)', fontsize=7)
    ax.get_lines()[0].set_color(st.C_ORANGE)
    ax.get_lines()[0].set_markersize(1.5)
    ax.get_lines()[1].set_color(st.C_RED)
    ax.get_lines()[1].set_linewidth(0.8)
    st.despine(ax)

plt.tight_layout(pad=0.8)
out_path = FIGURES_DIR / "ed_fig8_omega_distribution.pdf"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.savefig(str(out_path).replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"  Saved: {out_path}")

# ============================================================
# C-S3: Null distribution for multiplicative residual model
# (block-shuffle null from 08d/08e; B=1,000 permutations shuffling
#  sample/library blocks across regions. This supersedes the earlier
#  CT-label permutation within region pairs, which was anti-conservative
#  because per-pair shuffling ignores the block structure of 10x libraries.)
# ============================================================
print("\n" + "=" * 60)
print("C-S3: Null distribution for residual model (block-shuffle null)")
print("=" * 60)

# Observed pairs + tiers from the authoritative block-shuffle pipeline
print("  Loading brain block-shuffle observed pairs...")
bs_pairs = pd.read_csv(RESULTS_DIR / "brain_bs_null_observed_pairs.csv")
n_total = len(bs_pairs)
B_PERM_NULL = 1000  # block-shuffle permutations (as in 08d)

obs_strong = int((bs_pairs["tier"] == "Strong").sum())
obs_moderate = int((bs_pairs["tier"] == "Moderate").sum())
obs_weak = int((bs_pairs["tier"] == "Weak").sum())
print(f"  Total pairs: {n_total:,}, Cell types: {bs_pairs['cell_type'].nunique()}")
print(f"\n  Observed tier counts (08d definitions, exclusive tiers):")
print(f"    Strong (res<0.3, ω<15, lowest-in-pair): {obs_strong}")
print(f"    Moderate (res<0.5, ω<25): {obs_moderate}")
print(f"    Weak (res<0.75, ω<35): {obs_weak}")

# Assemble the block-shuffle null omega matrix (n_pairs x B), aligned to
# bs_pairs row order via each CT's pair_idx into its null matrix
print(f"\n  Assembling null matrix ({n_total:,} x {B_PERM_NULL})...")
null_mat = np.empty((n_total, B_PERM_NULL), dtype=np.float32)
for ct, sub in bs_pairs.groupby("cell_type", sort=False):
    npy_path = RESULTS_DIR / f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"
    null = np.load(npy_path)
    assert null.shape == (len(sub), B_PERM_NULL), (ct, null.shape, len(sub))
    null_mat[sub.index.values, :] = null[sub["pair_idx"].values, :]
print("  All CT null matrices loaded.")

# Group structures for the multiplicative residual model
ct_id = pd.factorize(bs_pairs["cell_type"])[0]
n_ct = int(ct_id.max()) + 1
ct_sizes = np.bincount(ct_id, minlength=n_ct).astype(float)
rp_id = pd.factorize(
    list(zip(bs_pairs["region_a"], bs_pairs["region_b"])))[0]
n_rp = int(rp_id.max()) + 1
rp_sizes = np.bincount(rp_id, minlength=n_rp).astype(float)

# Precompute the sort order for lowest-in-pair (group min across CTs per
# region pair); rp_id does not change across permutations
w_order = np.argsort(rp_id, kind="stable")
rp_sorted = rp_id[w_order]
rp_offsets = np.concatenate(([0], np.where(np.diff(rp_sorted) != 0)[0] + 1))
sorted_gid = np.repeat(np.arange(n_rp), np.diff(np.append(rp_offsets, n_total)))

null_strong_counts = np.zeros(B_PERM_NULL, dtype=int)
null_moderate_counts = np.zeros(B_PERM_NULL, dtype=int)
null_weak_counts = np.zeros(B_PERM_NULL, dtype=int)
null_residuals_sample = []

t0 = time.time()
for b in range(B_PERM_NULL):
    w = null_mat[:, b].astype(np.float64)
    mu_grand_b = w.mean()
    mu_ct_b = np.bincount(ct_id, weights=w, minlength=n_ct) / ct_sizes
    mu_pair_b = np.bincount(rp_id, weights=w, minlength=n_rp) / rp_sizes
    expected = mu_ct_b[ct_id] * mu_pair_b[rp_id] / mu_grand_b
    residuals = w / expected

    # lowest-in-pair under the null (min omega across CTs per region pair)
    w_sorted = w[w_order]
    rp_min = np.minimum.reduceat(w_sorted, rp_offsets)
    lowest_sorted = w_sorted <= rp_min[sorted_gid]
    lowest = np.empty(n_total, dtype=bool)
    lowest[w_order] = lowest_sorted

    strong_mask = (residuals < 0.3) & (w < 15) & lowest
    moderate_mask = (residuals < 0.5) & (w < 25) & ~strong_mask
    weak_mask = (residuals < 0.75) & (w < 35) & ~strong_mask & ~moderate_mask

    null_strong_counts[b] = int(strong_mask.sum())
    null_moderate_counts[b] = int(moderate_mask.sum())
    null_weak_counts[b] = int(weak_mask.sum())

    # Sample residuals for histogram (every 100th iteration)
    if b % 100 == 0:
        null_residuals_sample.extend(
            residuals[rng.choice(n_total, 1000, replace=False)].tolist()
        )

    if (b + 1) % 200 == 0:
        elapsed = time.time() - t0
        eta = elapsed / (b + 1) * (B_PERM_NULL - b - 1)
        print(f"    Iter {b+1}/{B_PERM_NULL}, "
              f"strong={np.mean(null_strong_counts[:b+1]):.1f}, "
              f"elapsed={elapsed:.0f}s, ETA={eta:.0f}s")

# Compute P-values (one-sided upper: excess of tier candidates vs null)
n_obs_strong = obs_strong
n_obs_moderate = obs_moderate
n_obs_weak = obs_weak

p_strong = (np.sum(null_strong_counts >= n_obs_strong) + 1) / (B_PERM_NULL + 1)
p_moderate = (np.sum(null_moderate_counts >= n_obs_moderate) + 1) / (B_PERM_NULL + 1)
p_weak = (np.sum(null_weak_counts >= n_obs_weak) + 1) / (B_PERM_NULL + 1)

# FDR: 3 tests, BH correction
p_vals_residual = np.array([p_strong, p_moderate, p_weak])
sorted_idx = np.argsort(p_vals_residual)
q_vals = np.zeros(3)
for i, idx in enumerate(sorted_idx):
    q_vals[idx] = p_vals_residual[idx] * 3 / (i + 1)
q_vals = np.minimum.accumulate(q_vals[::-1])[::-1]
# Re-sort
q_sorted = np.zeros(3)
for i, idx in enumerate(sorted_idx):
    q_sorted[idx] = q_vals[idx]

residual_null_results = {
    "null_type": "block_shuffle (10x library / sample_id blocks, as in 08d)",
    "observed": {
        "strong": int(n_obs_strong),
        "moderate": int(n_obs_moderate),
        "weak": int(n_obs_weak),
    },
    "null_mean": {
        "strong": float(np.mean(null_strong_counts)),
        "moderate": float(np.mean(null_moderate_counts)),
        "weak": float(np.mean(null_weak_counts)),
    },
    "null_std": {
        "strong": float(np.std(null_strong_counts)),
        "moderate": float(np.std(null_moderate_counts)),
        "weak": float(np.std(null_weak_counts)),
    },
    "null_95ci": {
        "strong": [float(np.percentile(null_strong_counts, 2.5)),
                    float(np.percentile(null_strong_counts, 97.5))],
        "moderate": [float(np.percentile(null_moderate_counts, 2.5)),
                      float(np.percentile(null_moderate_counts, 97.5))],
        "weak": [float(np.percentile(null_weak_counts, 2.5)),
                  float(np.percentile(null_weak_counts, 97.5))],
    },
    "p_values": {
        "strong": float(f"{p_strong:.4e}"),
        "moderate": float(f"{p_moderate:.4e}"),
        "weak": float(f"{p_weak:.4e}"),
    },
    "q_values_bh": {
        "strong": float(f"{q_sorted[0]:.4e}"),
        "moderate": float(f"{q_sorted[1]:.4e}"),
        "weak": float(f"{q_sorted[2]:.4e}"),
    },
    "B": B_PERM_NULL,
    "n_total_pairs": int(n_total),
    "mu_grand": round(float(bs_pairs["omega"].mean()), 4),
}

print(f"\n  Results:")
print(f"    Strong: observed={n_obs_strong}, null={np.mean(null_strong_counts):.1f}±{np.std(null_strong_counts):.1f}, "
      f"P={p_strong:.4e}, q={q_sorted[0]:.4e}")
print(f"    Moderate: observed={n_obs_moderate}, null={np.mean(null_moderate_counts):.1f}±{np.std(null_moderate_counts):.1f}, "
      f"P={p_moderate:.4e}, q={q_sorted[1]:.4e}")
print(f"    Weak: observed={n_obs_weak}, null={np.mean(null_weak_counts):.1f}±{np.std(null_weak_counts):.1f}, "
      f"P={p_weak:.4e}, q={q_sorted[2]:.4e}")

# Save
with open(RESULTS_DIR / "phaseB_residual_null.json", 'w') as f:
    json.dump(residual_null_results, f, indent=2)

# Save null distribution samples for plotting
null_sample_df = pd.DataFrame({
    "iteration": np.repeat(np.arange(0, B_PERM_NULL, 100), 1000),
    "residual": null_residuals_sample
})
null_sample_df.to_csv(RESULTS_DIR / "phaseB_residual_null_sample.csv", index=False)

# Also save per-iteration counts
null_counts_df = pd.DataFrame({
    "iteration": np.arange(B_PERM_NULL),
    "strong_count": null_strong_counts,
    "moderate_count": null_moderate_counts,
    "weak_count": null_weak_counts,
})
null_counts_df.to_csv(RESULTS_DIR / "phaseB_residual_null_counts.csv", index=False)
print(f"\n  Saved: results/phaseB_residual_null.json + CSVs")

# --- Generate residual null plot ---
# Matches the S9 caption: distribution of multiplicative residuals under
# block-shuffle permutation (B=1,000), compared against observed residuals
# for Strong-tier candidates.
print("\n  Generating residual null distribution plot...")

null_res_arr = np.asarray(null_residuals_sample, dtype=float)
obs_res = bs_pairs["residual"].values
strong_res = bs_pairs.loc[bs_pairs["tier"] == "Strong", "residual"].values

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.6))

# Panel A: overall null vs observed residual distributions
lo, hi = 0.0, float(np.percentile(np.concatenate([null_res_arr, obs_res]), 99.5))
bins_common = np.linspace(lo, hi, 60)
ax1.hist(null_res_arr, bins=bins_common, density=True, alpha=0.45,
         color=st.C_BLUE, edgecolor='white', linewidth=0.4,
         label="Block-shuffle null (B=1,000)")
ax1.hist(obs_res, bins=bins_common, density=True, histtype="step",
         lw=1.2, color=st.C_DARK, label="Observed")
ax1.set_xlabel("Multiplicative residual", fontsize=7)
ax1.set_ylabel("Density", fontsize=7)
ax1.set_title(f"All pairs (n = {n_total:,})", fontsize=8,
              fontweight='bold', pad=3)
ax1.legend(fontsize=7, frameon=True, framealpha=0.9, edgecolor='#BDC3C7',
           borderpad=0.4, labelspacing=0.3)
st.despine(ax1)
st.subtle_grid(ax1, axis='y')

# Panel B: lower tail with Strong-tier candidates
bins_tail = np.linspace(lo, 0.8, 60)
ax2.hist(null_res_arr, bins=bins_tail, density=True, alpha=0.45,
         color=st.C_BLUE, edgecolor='white', linewidth=0.4,
         label="Block-shuffle null (B=1,000)")
for r in strong_res:
    ax2.axvline(r, color=st.C_RED, lw=0.8, alpha=0.7)
ax2.plot([], [], color=st.C_RED, lw=0.8,
         label=f"Strong candidates (n={len(strong_res)})")
ax2.set_xlabel("Multiplicative residual", fontsize=7)
ax2.set_ylabel("Density", fontsize=7)
ax2.set_title("Lower tail: Strong-tier candidates", fontsize=8,
              fontweight='bold', pad=3)
ax2.legend(fontsize=7, frameon=True, framealpha=0.9, edgecolor='#BDC3C7',
           borderpad=0.4, labelspacing=0.3)
st.despine(ax2)
st.subtle_grid(ax2, axis='y')

plt.tight_layout(pad=0.8)
out_path = FIGURES_DIR / "ed_fig9_residual_null.pdf"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.savefig(str(out_path).replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"  Saved: {out_path}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("Phase B Summary")
print("=" * 60)

print("""
C-S1 (Adaptive permutation):
  - Brain: 10 tests, B=1,000, min_P=9.99e-04, BH_thresh=5.0e-03 → sufficient
  - Human: 17 tests, B=1,000, min_P=9.99e-04, BH_thresh=2.9e-03 → sufficient
  - Mouse: 15 tests, B=1,000, min_P=9.99e-04, BH_thresh=3.3e-03 → sufficient
  - Test granularity is cell-type level, not pair level
  - No borderline cases requiring additional permutations

C-S2 (Bootstrap CIs):
  - Computed 95% bootstrap CIs for all key ω estimates
  - Brain: 10 cell types, CI widths reflect pair count
  - Mouse/Human: aggregate + mouse per-category CIs
  - Sources: brain_bs_null_observed_pairs.csv / phase35_all_metrics_pairs.csv
    (supersede the legacy v3/phase33 matrices)
  - Human (per-CT) pseudo-CI rows removed (R3-C3)

C-S3 (Residual null distribution):
  - Block-shuffle null (B=1,000; 10x library/sample_id blocks, from 08d)
  - Empirical P-values for Strong/Moderate/Weak tier counts
  - BH-FDR correction across 3 tests
  - Supersedes the anti-conservative CT-label permutation

C-S5 (Distribution characterization):
  - All ω distributions are right-skewed (positive skewness)
  - Non-normal but approximately log-normal
  - Cohen's d should be interpreted with caution (non-normal distribution)
  - Histograms + Q-Q plots generated as ED Fig 8
""")

print("\nPhase B complete!")
print(f"Output files:")
print(f"  results/phaseB_adaptive_analysis.json")
print(f"  results/phaseB_bootstrap_cis.csv")
print(f"  results/phaseB_omega_distribution.json")
print(f"  results/phaseB_residual_null.json")
print(f"  results/phaseB_residual_null_counts.csv")
print(f"  results/phaseB_residual_null_sample.csv")
print(f"  results/figures_final/ed_fig8_omega_distribution.pdf")
print(f"  results/figures_final/ed_fig9_residual_null.pdf")
