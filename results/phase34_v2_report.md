# CKI Phase 3.4 v2 Report: TCGA Tumor Perturbation (Per-Cancer Loading)

## Key Fix
- v1 (failed): Global gene filtering across all 5 cancers diluted per-cancer signal, omega ≈ 0
- v2: Each cancer type loaded and filtered independently, preserving cancer-specific expression patterns

## Overview
- Data: UCSC Xena TCGA RSEM gene TPM (pan-cancer bulk RNA-seq)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f, n=200)
- Normalization: log2(TPM + 0.001)
- Analysis time: 797s

## Summary
  Project  n_Tumor  n_Normal  n_Genes  n_HK omega_TT_mean omega_TT_median omega_NN_mean omega_NN_median omega_TN_mean omega_TN_median TN_Baseline  p_value time_s
TCGA-LUAD      495        76    14178  1125         256.8            97.6         633.4           155.8         269.4           116.4       0.61x 5.69e-17    144
TCGA-LUSC      567        58    13989  1125         225.9            96.2         443.9           137.9         197.8           100.2       0.59x 3.98e-16    137
TCGA-LIHC      365        57    12047  1124         117.4            60.3         206.4           170.7          84.2            55.4       0.52x 3.56e-42    126
TCGA-KIRC      755        82    13876  1125         235.2            95.9         532.6           190.2         210.2           106.8       0.55x 1.97e-47    153
TCGA-BRCA     1032       109    14272  1125         293.5           116.8         610.7           163.4         267.5           118.8       0.59x 7.20e-47    233

## Interpretation
- TN/Baseline > 1: tumor transcriptomes are more divergent from normals than self-pairs
- CKI omega detects tumor perturbation via elevated k_f relative to stable k_n
- A ratio >>1 supports CKI's ability to detect transcriptional perturbation in bulk tumor RNA-seq

## Files
- phase34_v2_summary.csv: per-cancer summary
- phase34_v2_all_pairs.csv: all pair-level omega/kn/kf
- phase34_v2_<Cancer>_pairs.csv: per-cancer pair details
- phase34_v2_boxplot_per_project.png
- phase34_v2_cross_project_bar.png
- phase34_v2_effect_size.png
- phase34_v2_combined_histogram.png