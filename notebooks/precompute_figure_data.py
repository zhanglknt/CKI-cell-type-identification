"""
Pre-compute derived figure data for NAR figure script.

Outputs needed by 30_genome_biology_figures.py:
  P2-1: Fig 2C / 3A — correlation matrix from phase35_metric_correlation.csv
  P2-2: Fig 3C / 3E / ED Fig 4 — AUC scores from phase35_all_metrics_pairs.csv
  P2-4: ED Fig 1B — per-module GSVA score variance across cell types
         (real data from phase32_pathway_scores.csv, produced by 04_phase32_sweep.py)

Outputs:
  results/figure_data_correlations.npy
  results/figure_data_auc.npy
  results/figure_data_module_variance.csv

Note: ED Fig 2B (HK overlap) is now handled by 01c_hk_overlap.py → hk_overlap_subsamples.csv
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR  = PROJECT_ROOT / "results"
DATA_DIR     = PROJECT_ROOT / "data"

print("=" * 60)
print("Pre-computing figure data for Genome Biology figures")
print("=" * 60)

# ============================================================
# P2-1: Correlation matrix from phase35_metric_correlation.csv
# ============================================================
print("\n[P2-1] Loading phase35_metric_correlation.csv ...")
corr_df = pd.read_csv(RESULTS_DIR / "phase35_metric_correlation.csv", index_col=0)
print(corr_df)

# Fig 2C: CKI omega vs each metric
metrics_order_2c = ['Cosine dist', 'Raw JS', 'Marker Jaccard dist', 'Spearman dist']
corrs_2c = [float(corr_df.loc['CKI omega', m]) for m in metrics_order_2c]
print(f"  Fig 2C corrs = {corrs_2c}")

# Fig 3A: Full 5x5 correlation matrix
metrics_order_3a = ['CKI omega', 'Cosine dist', 'Raw JS', 'Marker Jaccard dist', 'Spearman dist']
n = len(metrics_order_3a)
corr_matrix = np.zeros((n, n))
for i, mi in enumerate(metrics_order_3a):
    for j, mj in enumerate(metrics_order_3a):
        corr_matrix[i, j] = corr_df.loc[mi, mj]
print(f"  Fig 3A corr_matrix shape = {corr_matrix.shape}")

np.save(RESULTS_DIR / "figure_data_correlations.npy",
         {"corrs_2c": corrs_2c, "corr_matrix": corr_matrix,
          "metrics_2c": ['Cosine', 'Raw JS', 'Marker Jaccard', 'Spearman'],
          "metrics_3a": ['CKI ω', 'Cosine', 'Raw JS', 'Marker Jaccard', 'Spearman']})
print("  Saved: results/figure_data_correlations.npy")

# ============================================================
# P2-2: AUC from phase35_all_metrics_pairs.csv
# ============================================================
print("\n[P2-2] Computing AUC from phase35_all_metrics_pairs.csv ...")
pairs = pd.read_csv(RESULTS_DIR / "phase35_all_metrics_pairs.csv")
print(f"  Loaded {len(pairs)} pairs, same_ct rate = {pairs['same_ct'].mean():.3f}")

auc_scores = {}
for method, score_col in [
    ('CKI ω',          'omega'),
    ('Cosine',          'cosine_dist'),
    ('Raw JS',          'js_raw'),
    ('Marker Jaccard',  'marker_jaccard_dist'),
    ('Spearman',        'spearman_dist'),
]:
    # All metrics: lower = more similar; negate so higher = more similar
    scores = -pairs[score_col].values
    auc_val = roc_auc_score(pairs['same_ct'].astype(int), scores)
    auc_scores[method] = float(auc_val)
    print(f"  AUC({method}) = {auc_val:.4f}")

np.save(RESULTS_DIR / "figure_data_auc.npy", auc_scores)
print("  Saved: results/figure_data_auc.npy")

# ============================================================
# P2-4: Per-module GSVA score variance across cell types
# (real data; replaces former fabricated pathway-enrichment panel)
# ============================================================
print("\n[P2-4] Computing per-module variance from phase32_pathway_scores.csv ...")

_pw_score_file = RESULTS_DIR / "phase32_pathway_scores.csv"
if _pw_score_file.exists():
    pw_scores = pd.read_csv(_pw_score_file, index_col=0)
    # Rows: cell-type entries; columns: 20 HVG-partition modules (GSVA scores)
    module_var = pw_scores.var(axis=0).sort_values(ascending=False)
    module_sd = pw_scores.std(axis=0)
    module_df = pd.DataFrame({
        "module": module_var.index.astype(str),
        "variance": module_var.values,
        "sd": module_sd.loc[module_var.index].values,
        "mean": pw_scores.mean(axis=0).loc[module_var.index].values,
    })
    module_df.to_csv(RESULTS_DIR / "figure_data_module_variance.csv", index=False)
    print(f"  Saved: results/figure_data_module_variance.csv ({len(module_df)} modules)")
    print(module_df.head(8).to_string())
else:
    raise FileNotFoundError(
        "phase32_pathway_scores.csv not found — run notebooks/04_phase32_sweep.py first. "
        "No fallback data is provided (fabricated values are not acceptable)."
    )

print("\n" + "=" * 60)
print("All pre-computation complete.")
print(f"  correlation:     results/figure_data_correlations.npy")
print(f"  auc:             results/figure_data_auc.npy")
print(f"  module variance: results/figure_data_module_variance.csv")
print("=" * 60)
