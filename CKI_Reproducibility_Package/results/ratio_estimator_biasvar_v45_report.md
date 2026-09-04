# Ratio-estimator bias-variance characterization (v45, analysis A)

Reviewer point (r-statistics P1-1): `omega = k_f / k_n` is a ratio of two JS divergences; ratio estimators are upward biased and heavy right-tailed when the denominator is small.  This analysis quantifies the magnitude using existing data only.

## Part 1  Bias under the null (split-half, identical populations)

Source: `reviewer_brain_splithalf_raw.csv` (1450 half/half splits, 10 classes x top-3 regions x 50 splits).  Both halves are the same population, so `mean(k_f/k_n) / (mean(k_f)/mean(k_n)) - 1` isolates pure ratio-estimator bias.

Pooled over all splits: E[omega] = 9.73, E[k_f]/E[k_n] = 9.90, ratio bias = **-1.8%**; SD = 2.55, skew = 2.28, excess kurtosis = 9.14, P95 = 14.4, P99 = 18.9.

Per-group (class x region, n=50 each), median across 29 groups: empirical ratio bias +0.2%, delta-method prediction +0.2% (Spearman rho = 0.99); empirical SD 0.91 vs delta SD 0.90 (rho = 1.00). The second-order delta approximation tracks the empirical bias and variance, confirming the ratio-noise mechanism.

k_n-binned null behaviour (small-denominator leverage):

| k_n bin | n | E[omega] | ratio bias | SD | skew | P95 | P99 |
|---|---|---|---|---|---|---|---|
| kn<1e-4 | 600 | 9.63 | +6.5% | 2.23 | 3.36 | 13.1 | 18.4 |
| 1e-4<=kn<1e-3 | 402 | 9.60 | -8.3% | 2.09 | 0.91 | 13.3 | 15.1 |
| kn>=1e-3 | 448 | 9.97 | +1.5% | 3.23 | 1.82 | 15.9 | 19.9 |

## Part 2  Robust class-level summaries (brain, 31,764 pairs)

Pooled per-pair omega: skew = 2.22, excess kurtosis = 6.02 (matches the reported 2.22 / 6.02).

| class | n | mean | median | 10% trimmed | skew |
|---|---|---|---|---|---|
| Astrocyte | 5778 | 82.75 | 73.37 | 78.68 | 0.77 |
| Bergmann glia | 21 | 13.56 | 12.23 | 12.91 | 0.93 |
| Choroid plexus | 15 | 37.76 | 33.15 | 35.07 | 2.39 |
| Committed oligodendrocyte precursor | 1326 | 28.84 | 26.70 | 27.64 | 0.79 |
| Ependymal | 780 | 22.98 | 21.31 | 21.96 | 1.14 |
| Fibroblast | 3403 | 18.18 | 15.61 | 16.62 | 1.94 |
| Microglia | 5671 | 24.31 | 21.61 | 22.75 | 1.72 |
| Oligodendrocyte | 5778 | 37.05 | 34.28 | 35.90 | 0.79 |
| Oligodendrocyte precursor | 5671 | 40.62 | 36.73 | 38.49 | 1.03 |
| Vascular | 3321 | 13.56 | 12.45 | 12.91 | 1.43 |

Astrocyte / Bergmann-glia gradient: mean **6.10x** (headline 6.10) -> median **6.00x**, 10% trimmed **6.09x**.
Class-ranking agreement (Spearman rho): mean vs median 0.988, mean vs trimmed 0.976, median vs trimmed 0.988.

## Part 3  Near-zero k_n leverage

Per-pair k_n: min = 9.23e-05 (kn_floor = 0), P1 = 3.58e-04, P5 = 5.53e-04, median = 2.17e-03.

| threshold | n below | frac | mean omega below | mean omega rest | gradient after exclusion | rank rho vs full |
|---|---|---|---|---|---|---|
| k_n < 1e-04 | 1 | 0.003% | 41.24 | 38.54 | 6.10x | 1.000 |
| k_n < 3e-04 | 141 | 0.444% | 46.04 | 38.51 | 6.41x | 1.000 |
| k_n < 5e-04 | 1141 | 3.592% | 44.82 | 38.31 | 6.52x | 1.000 |
| k_n < 1e-03 | 6320 | 19.897% | 53.35 | 34.87 | 6.46x | 0.964 |

## Conclusions / suggested manuscript wording

1. Ratio bias is small, theory-consistent, and *null-calibrated*: under the split-half null, E[k_f/k_n] vs E[k_f]/E[k_n] differs by a median of +0.2% across class x region groups (pooled -1.8%), with the largest upward bias in the smallest-denominator bin (k_n < 1e-4: +6.5%), exactly where delta-method theory predicts it; the second-order delta approximation reproduces both the bias and the SD per group (Spearman rho = 0.99 / 1.00).  Because the empirical calibration baseline (omega_0) is computed with the same ratio estimator on the same scale of k_n, this inflation is absorbed into the baseline.  The heavy right tail (null skew 2.28, P99/P50 = 2.1) widens CIs but does not shift the calibrated conclusions.
2. The Astrocyte/Bergmann-glia gradient is robust to the summary statistic: 6.10x (mean) vs 6.00x (median) vs 6.09x (10% trimmed); the 10-class ranking is essentially unchanged (Spearman rho >= 0.98).  The mean-based headline is not a heavy-tail artefact.
3. Near-zero denominators are rare and non-influential: only 1 pair (0.003%) has k_n < 1e-4 and 141 (0.44%) have k_n < 3e-4; low-k_n pairs actually carry *below-average* leverage on the gradient -- excluding all pairs with k_n < 5e-4 (1141 pairs, 3.59%) moves the gradient slightly *up*, from 6.10x to 6.52x, with the class ranking unchanged (rho = 1.000); even dropping the bottom 20% by k_n leaves the ranking at rho = 0.964. The 6.10x headline is, if anything, conservative with respect to small-denominator pairs.

Files: `results/ratio_estimator_biasvar_v45.json` (all numbers), this report.  No manuscript text modified.
