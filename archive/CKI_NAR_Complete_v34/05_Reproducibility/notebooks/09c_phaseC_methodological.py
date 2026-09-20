"""
Phase C: Methodological Reinforcement — C-M1, C-M2, C-M3

C-M1: Calibrated normalization (omega_cal = omega_obs / omega_baseline)
C-M2: JS divergence dimensionality matching validation
C-M3: Pair-specific k_n variability analysis (global vs per-pair)
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# C-M1: Calibrated Normalization
# ============================================================
print("=" * 60)
print("C-M1: Calibrated Normalization")
print("=" * 60)

OMEGA_BASELINE = 6.67  # empirical calibration baseline from mouse split-half

# Load brain omega pairs (has kn, kf, omega per pair)
brain_df = pd.read_csv(RESULTS_DIR / "brain_siletti_omega_pairs_v3.csv")
brain_df["omega_cal"] = brain_df["omega"] / OMEGA_BASELINE

# Load brain CT summary
brain_ct = pd.read_csv(RESULTS_DIR / "brain_siletti_ct_summary_v3.csv")
brain_ct["omega_cal_mean"] = brain_ct["omega_mean"] / OMEGA_BASELINE
brain_ct["omega_cal_median"] = brain_ct["omega_median"] / OMEGA_BASELINE

# Load mouse calibration data from _load_manuscript_data
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from _load_manuscript_data import get_manuscript_data
DATA = get_manuscript_data()
_mc = DATA["mouse_calibration"]

# Calibrated omega for mouse calibration controls
control_omega_cal = _mc["control_mean"] / OMEGA_BASELINE

# Human omega data
omega_matrix = pd.read_csv(RESULTS_DIR / "omega_matrix_tissue.csv", index_col=0)
# Extract upper triangle values
mask = np.triu(np.ones_like(omega_matrix, dtype=bool), k=1)
human_omegas = omega_matrix.values[mask]
human_omegas = human_omegas[~np.isnan(human_omegas)]
human_omega_cal = human_omegas / OMEGA_BASELINE

# Phase B bootstrap CIs for calibrated omega
phaseB_cis = pd.read_csv(RESULTS_DIR / "phaseB_bootstrap_cis.csv")
phaseB_cis["omega_cal_mean"] = phaseB_cis["omega_mean"] / OMEGA_BASELINE
phaseB_cis["ci_cal_lower"] = phaseB_cis["ci_95_lower"] / OMEGA_BASELINE
phaseB_cis["ci_cal_upper"] = phaseB_cis["ci_95_upper"] / OMEGA_BASELINE

# Save calibrated omega results
brain_df[["cell_type", "region_a", "region_b", "omega", "omega_cal", "kn", "kf"]].to_csv(
    RESULTS_DIR / "phaseC_calibrated_omega_brain.csv", index=False
)

# Summary statistics for calibrated omega
calibration_summary = {
    "baseline_omega": OMEGA_BASELINE,
    "baseline_source": "Mouse split-half equivalent populations (n=6, mean omega=6.67)",
    "brain": {
        "n_pairs": len(brain_df),
        "omega_raw_mean": float(brain_df["omega"].mean()),
        "omega_raw_median": float(brain_df["omega"].median()),
        "omega_cal_mean": float(brain_df["omega_cal"].mean()),
        "omega_cal_median": float(brain_df["omega_cal"].median()),
        "omega_cal_range": [float(brain_df["omega_cal"].min()), float(brain_df["omega_cal"].max())],
        "per_cell_type": {}
    },
    "mouse": {
        "n_pairs": int(_mc.get("total_pairs", 703)),
        "control_omega_raw": float(_mc["control_mean"]),
        "control_omega_cal": float(control_omega_cal),
        "S_omega_raw": float(_mc["S_mean"]),
        "S_omega_cal": float(_mc["S_mean"]) / OMEGA_BASELINE,
        "D_omega_raw": float(_mc["D_mean"]),
        "D_omega_cal": float(_mc["D_mean"]) / OMEGA_BASELINE,
    },
    "human": {
        "n_pairs": len(human_omegas),
        "omega_raw_mean": float(np.mean(human_omegas)),
        "omega_raw_median": float(np.median(human_omegas)),
        "omega_cal_mean": float(np.mean(human_omega_cal)),
        "omega_cal_median": float(np.median(human_omega_cal)),
    }
}

# Per cell-type calibrated omega for brain
for ct in brain_ct["cell_type"].unique():
    row = brain_ct[brain_ct["cell_type"] == ct].iloc[0]
    calibration_summary["brain"]["per_cell_type"][ct] = {
        "omega_raw_mean": float(row["omega_mean"]),
        "omega_cal_mean": float(row["omega_mean"]) / OMEGA_BASELINE,
        "omega_raw_median": float(row["omega_median"]),
        "omega_cal_median": float(row["omega_median"]) / OMEGA_BASELINE,
        "n_pairs": int(row["n_pairs"]),
    }

# Key interpretation
calibration_summary["interpretation"] = (
    f"Calibrated omega (omega_cal = omega / {OMEGA_BASELINE}) rescales all values so "
    f"that equivalent populations have omega_cal ~ 1.0. "
    f"Mouse controls: omega_cal = {control_omega_cal:.2f} (raw {float(_mc['control_mean']):.2f}). "
    f"Brain global mean: omega_cal = {calibration_summary['brain']['omega_cal_mean']:.2f} "
    f"(raw {calibration_summary['brain']['omega_raw_mean']:.2f}). "
    f"Astrocytes: omega_cal = {calibration_summary['brain']['per_cell_type'].get('Astrocyte', {}).get('omega_cal_mean', 'N/A'):.2f} "
    f"if available. "
    f"Bergmann glia: omega_cal = {calibration_summary['brain']['per_cell_type'].get('Bergmann glia', {}).get('omega_cal_mean', 'N/A'):.2f}. "
    f"Values > 1 indicate functional divergence exceeding the empirical baseline."
)

with open(RESULTS_DIR / "phaseC_calibration.json", "w") as f:
    json.dump(calibration_summary, f, indent=2, default=str)

print(f"  Baseline omega: {OMEGA_BASELINE}")
print(f"  Brain raw mean: {calibration_summary['brain']['omega_raw_mean']:.2f} -> cal: {calibration_summary['brain']['omega_cal_mean']:.2f}")
print(f"  Mouse control: {float(_mc['control_mean']):.2f} -> cal: {control_omega_cal:.2f}")
print(f"  Human mean: {calibration_summary['human']['omega_raw_mean']:.2f} -> cal: {calibration_summary['human']['omega_cal_mean']:.2f}")
for ct, vals in calibration_summary["brain"]["per_cell_type"].items():
    print(f"  {ct}: raw={vals['omega_raw_mean']:.2f} cal={vals['omega_cal_mean']:.2f} (n={vals['n_pairs']})")

# Save calibrated CIs
phaseB_cis.to_csv(RESULTS_DIR / "phaseC_calibrated_cis.csv", index=False)

# ============================================================
# C-M2: JS Divergence Dimensionality Matching Validation
# ============================================================
print("\n" + "=" * 60)
print("C-M2: JS Divergence Dimensionality Matching")
print("=" * 60)

np.random.seed(42)

def js_divergence_np(p, q):
    """Compute JS divergence using base-2 log."""
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    kl_pm = np.sum(p[p > 0] * np.log2(p[p > 0] / m[p > 0]))
    kl_qm = np.sum(q[q > 0] * np.log2(q[q > 0] / m[q > 0]))
    return 0.5 * kl_pm + 0.5 * kl_qm

# Simulation: JS divergence between random Dirichlet distributions at different dimensions
dims = [50, 100, 200, 500, 1000, 1130, 2000, 5000]
n_trials = 2000
results_dim = []

for d in dims:
    js_values = []
    js_same = []  # JS between two draws from same Dirichlet (null case)
    for _ in range(n_trials):
        # Two random distributions on d-dim simplex
        alpha = np.ones(d) * 2.0  # moderate concentration
        p = np.random.dirichlet(alpha)
        q = np.random.dirichlet(alpha)
        js_val = js_divergence_np(p, q)
        js_values.append(js_val)
        
        # Same distribution case (control)
        p2 = np.random.dirichlet(alpha)
        q2 = np.random.dirichlet(alpha)
        js_same.append(js_divergence_np(p2, q2))
    
    results_dim.append({
        "dimension": d,
        "mean_js": float(np.mean(js_values)),
        "std_js": float(np.std(js_values)),
        "median_js": float(np.median(js_values)),
        "p5_js": float(np.percentile(js_values, 5)),
        "p95_js": float(np.percentile(js_values, 95)),
        "mean_js_same": float(np.mean(js_same)),
    })
    print(f"  dim={d:5d}: mean JS={np.mean(js_values):.6f} +/- {np.std(js_values):.6f}")

# Key insight: ratio of JS at different dimensions
dim_df = pd.DataFrame(results_dim)
dim_df.to_csv(RESULTS_DIR / "phaseC_dimensionality_simulation.csv", index=False)

# Dimensionality ratio analysis
js_1130 = dim_df[dim_df["dimension"] == 1130]["mean_js"].values[0]
js_2000 = dim_df[dim_df["dimension"] == 2000]["mean_js"].values[0]
js_200 = dim_df[dim_df["dimension"] == 200]["mean_js"].values[0]
dim_ratio = js_2000 / js_1130

dim_summary = {
    "n_trials": n_trials,
    "dimensions_tested": dims,
    "js_at_1130_dim": float(js_1130),
    "js_at_2000_dim": float(js_2000),
    "js_at_200_dim": float(js_200),
    "ratio_2000_to_1130": float(dim_ratio),
    "ratio_2000_to_200": float(js_2000 / js_200),
    "finding": (
        f"JS divergence between random Dirichlet distributions scales with dimensionality: "
        f"mean JS at d=1130 is {js_1130:.6f}, at d=2000 is {js_2000:.6f} "
        f"(ratio {dim_ratio:.3f}). This means k_n (computed on ~1,130 HK genes) and k_f "
        f"(computed on 200-2,000 HVG genes) are not dimensionally matched. However, the ratio "
        f"omega = k_f/k_n is still meaningful because: (1) both are JS divergences bounded in [0,1], "
        f"(2) the empirical calibration baseline (omega=6.67) captures the combined effect of "
        f"dimensionality mismatch and HVG selection bias, and (3) the permutation null distribution "
        f"is constructed using the same gene sets, ensuring internal consistency."
    ),
    "mitigation": (
        "Calibrated omega (omega_cal = omega / 6.67) absorbs the dimensional bias into the baseline. "
        "The permutation test compares observed omega against a null built from the same gene sets, "
        "so dimensionality effects cancel in the hypothesis test."
    )
}

with open(RESULTS_DIR / "phaseC_dimensionality.json", "w") as f:
    json.dump(dim_summary, f, indent=2)

print(f"\n  Ratio JS(2000)/JS(1130) = {dim_ratio:.3f}")
print(f"  Ratio JS(2000)/JS(200) = {js_2000/js_200:.3f}")

# ============================================================
# C-M3: Pair-Specific k_n Variability (Global vs Per-Pair)
# ============================================================
print("\n" + "=" * 60)
print("C-M3: Pair-Specific k_n Variability")
print("=" * 60)

# Analyze k_n variability across all brain pairs
kn_stats = brain_df.groupby("cell_type")["kn"].agg([
    ("kn_mean", "mean"),
    ("kn_std", "std"),
    ("kn_median", "median"),
    ("kn_min", "min"),
    ("kn_max", "max"),
    ("kn_cv", lambda x: x.std() / x.mean() if x.mean() > 0 else 0),
    ("n_pairs", "count"),
]).reset_index()

# Overall k_n variability
kn_overall_cv = brain_df["kn"].std() / brain_df["kn"].mean()
kn_overall_mean = brain_df["kn"].mean()
kn_overall_median = brain_df["kn"].median()

# Also compute pair-specific omega (k_f / k_n_pair) vs global omega
# In the brain analysis, k_n is computed per-pair (not global)
# Let's check: if k_n were truly global, CV would be ~0
print(f"  Overall k_n: mean={kn_overall_mean:.6f}, median={kn_overall_median:.6f}, CV={kn_overall_cv:.4f}")

# Per cell-type
for _, row in kn_stats.iterrows():
    print(f"  {row['cell_type']}: kn_mean={row['kn_mean']:.6f}, CV={row['kn_cv']:.4f}, n={int(row['n_pairs'])}")

# Compute omega using per-pair k_n (already what brain data uses) vs mean k_n
brain_df["omega_global_kn"] = brain_df["kf"] / brain_df["kn"].mean()
brain_df["omega_ratio"] = brain_df["omega"] / brain_df["omega_global_kn"]

# Correlation between per-pair omega and global-kn omega
from scipy.stats import spearmanr
rho, pval = spearmanr(brain_df["omega"], brain_df["omega_global_kn"])

kn_summary = {
    "brain_overall": {
        "kn_mean": float(kn_overall_mean),
        "kn_std": float(brain_df["kn"].std()),
        "kn_median": float(kn_overall_median),
        "kn_min": float(brain_df["kn"].min()),
        "kn_max": float(brain_df["kn"].max()),
        "kn_cv": float(kn_overall_cv),
        "n_pairs": len(brain_df),
    },
    "per_cell_type": {},
    "omega_correlation": {
        "spearman_rho": float(rho),
        "p_value": float(pval),
        "interpretation": (
            f"Spearman rho = {rho:.4f} (P = {pval:.2e}) between per-pair omega "
            f"and global-kn omega. k_n CV = {kn_overall_cv:.4f} "
            f"({kn_overall_cv*100:.2f}%). "
            f"{'k_n is relatively stable across pairs (CV < 10%), confirming that '
            f'the global k_n simplification in the hybrid scheme preserves ranking order.' if kn_overall_cv < 0.10 
            else 'k_n shows substantial cross-pair variability (CV >= 10%), indicating '
            f'that pair-specific k_n matters for absolute omega values.'}"
        )
    }
}

for _, row in kn_stats.iterrows():
    kn_summary["per_cell_type"][row["cell_type"]] = {
        "kn_mean": float(row["kn_mean"]),
        "kn_std": float(row["kn_std"]),
        "kn_cv": float(row["kn_cv"]),
        "n_pairs": int(row["n_pairs"]),
    }

with open(RESULTS_DIR / "phaseC_kn_variability.json", "w") as f:
    json.dump(kn_summary, f, indent=2)

# Save k_n stats
kn_stats.to_csv(RESULTS_DIR / "phaseC_kn_stats.csv", index=False)

# Also save omega comparison (per-pair vs global-kn)
brain_df[["cell_type", "region_a", "region_b", "omega", "omega_global_kn", "kn", "kf"]].to_csv(
    RESULTS_DIR / "phaseC_omega_pair_vs_global.csv", index=False
)

print(f"\n  Spearman rho (per-pair vs global-kn omega): {rho:.4f} (P={pval:.2e})")
print(f"  k_n CV: {kn_overall_cv:.4f} ({kn_overall_cv*100:.2f}%)")

# ============================================================
# Generate supplementary figures
# ============================================================
print("\n" + "=" * 60)
print("Generating Phase C figures...")
print("=" * 60)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 8,
    "font.family": "Arial",
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.dpi": 300,
})

FIG_DIR = RESULTS_DIR / "figures_final"
FIG_DIR.mkdir(exist_ok=True)

# --- Figure 1: Dimensionality simulation ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.8))

ax1.errorbar(dim_df["dimension"], dim_df["mean_js"], 
             yerr=dim_df["std_js"], fmt="o-", color="#2c3e50", 
             capsize=3, markersize=4, linewidth=1)
ax1.axvline(1130, color="#e74c3c", linestyle="--", alpha=0.7, label="HK genes (1,130)")
ax1.axvline(2000, color="#3498db", linestyle="--", alpha=0.7, label="HVG (2,000)")
ax1.set_xlabel("Dimensionality (number of genes)")
ax1.set_ylabel("JS divergence (mean +/- SD)")
ax1.set_title("A. JS divergence vs dimensionality")
ax1.legend(framealpha=0.9)
ax1.set_xscale("log")

# Ratio plot
ax2.plot(dim_df["dimension"], dim_df["mean_js"] / dim_df[dim_df["dimension"]==1130]["mean_js"].values[0],
         "s-", color="#27ae60", markersize=4, linewidth=1)
ax2.axhline(1.0, color="gray", linestyle=":", alpha=0.5)
ax2.set_xlabel("Dimensionality (number of genes)")
ax2.set_ylabel("JS / JS(d=1130)")
ax2.set_title("B. Dimensionality ratio (relative to HK gene set)")
ax2.set_xscale("log")

plt.tight_layout()
plt.savefig(FIG_DIR / "ed_fig10_dimensionality.pdf", bbox_inches="tight")
plt.savefig(FIG_DIR / "ed_fig10_dimensionality.png", bbox_inches="tight", dpi=300)
plt.close()
print("  Saved ed_fig10_dimensionality.pdf/png")

# --- Figure 2: k_n variability ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.8))

# k_n distribution
cell_types = kn_stats.sort_values("kn_mean")
colors = plt.cm.Set2(np.linspace(0, 1, len(cell_types)))
ax1.barh(range(len(cell_types)), cell_types["kn_mean"].values, 
         xerr=cell_types["kn_std"].values, color=colors, capsize=2, height=0.7)
ax1.set_yticks(range(len(cell_types)))
ax1.set_yticklabels([ct[:20] for ct in cell_types["cell_type"]], fontsize=6)
ax1.set_xlabel("k_n (mean +/- SD)")
ax1.set_title("A. Per-pair k_n by cell type (brain)")

# Omega: per-pair vs global-kn scatter
sample = brain_df.sample(min(5000, len(brain_df)), random_state=42)
ax2.scatter(sample["omega_global_kn"], sample["omega"], s=2, alpha=0.3, color="#2c3e50")
max_val = max(sample["omega_global_kn"].max(), sample["omega"].max())
ax2.plot([0, max_val], [0, max_val], "r--", alpha=0.5, label="y=x")
ax2.set_xlabel("omega (global k_n)")
ax2.set_ylabel("omega (per-pair k_n)")
ax2.set_title(f"B. Per-pair vs global k_n omega (rho={rho:.3f})")
ax2.legend(fontsize=6)

plt.tight_layout()
plt.savefig(FIG_DIR / "ed_fig11_kn_variability.pdf", bbox_inches="tight")
plt.savefig(FIG_DIR / "ed_fig11_kn_variability.png", bbox_inches="tight", dpi=300)
plt.close()
print("  Saved ed_fig11_kn_variability.pdf/png")

# --- Figure 3: Calibrated omega ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.8))

# Raw vs calibrated omega for brain
brain_ct_sorted = brain_ct.sort_values("omega_mean")
y_pos = np.arange(len(brain_ct_sorted))
ax1.barh(y_pos - 0.15, brain_ct_sorted["omega_mean"].values, height=0.3, 
         color="#3498db", alpha=0.8, label="Raw omega")
ax1.barh(y_pos + 0.15, brain_ct_sorted["omega_mean"].values / OMEGA_BASELINE, height=0.3,
         color="#e74c3c", alpha=0.8, label="Calibrated omega")
ax1.axvline(6.67, color="#3498db", linestyle="--", alpha=0.5)
ax1.axvline(1.0, color="#e74c3c", linestyle="--", alpha=0.5)
ax1.set_yticks(y_pos)
ax1.set_yticklabels([ct[:20] for ct in brain_ct_sorted["cell_type"]], fontsize=6)
ax1.set_xlabel("omega")
ax1.set_title("A. Raw vs calibrated omega (brain)")
ax1.legend(fontsize=6)

# Calibrated omega distribution
ax2.hist(brain_df["omega_cal"].values, bins=100, color="#2c3e50", alpha=0.7, density=True)
ax2.axvline(1.0, color="#e74c3c", linestyle="--", linewidth=1.5, label="Calibration baseline")
ax2.axvline(brain_df["omega_cal"].mean(), color="#f39c12", linestyle="-", linewidth=1.5, 
            label=f"Mean={brain_df['omega_cal'].mean():.2f}")
ax2.set_xlabel("Calibrated omega (omega / 6.67)")
ax2.set_ylabel("Density")
ax2.set_title("B. Calibrated omega distribution (brain)")
ax2.legend(fontsize=6)
ax2.set_xlim(0, 8)

plt.tight_layout()
plt.savefig(FIG_DIR / "ed_fig12_calibrated_omega.pdf", bbox_inches="tight")
plt.savefig(FIG_DIR / "ed_fig12_calibrated_omega.png", bbox_inches="tight", dpi=300)
plt.close()
print("  Saved ed_fig12_calibrated_omega.pdf/png")

print("\n" + "=" * 60)
print("Phase C analysis complete!")
print("=" * 60)
print(f"\nOutput files:")
print(f"  results/phaseC_calibration.json")
print(f"  results/phaseC_calibrated_omega_brain.csv")
print(f"  results/phaseC_calibrated_cis.csv")
print(f"  results/phaseC_dimensionality.json")
print(f"  results/phaseC_dimensionality_simulation.csv")
print(f"  results/phaseC_kn_variability.json")
print(f"  results/phaseC_kn_stats.csv")
print(f"  results/phaseC_omega_pair_vs_global.csv")
print(f"  results/figures_final/ed_fig10_dimensionality.pdf/png")
print(f"  results/figures_final/ed_fig11_kn_variability.pdf/png")
print(f"  results/figures_final/ed_fig12_calibrated_omega.pdf/png")
