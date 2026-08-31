# v38 candidate-composition analyses (Round-4 fixes)

## A. Omnibus test of Strong-candidate class composition

Observed Strong composition (n = 39) vs the classes' share of all 31,764 comparisons. Pearson chi-square = 26.68; asymptotic p = 0.001579; Monte-Carlo p (20,000 multinomial draws, expected counts from comparison shares) = 0.0471.

| cell_type                           |   observed_strong |   expected_from_share |
|:------------------------------------|------------------:|----------------------:|
| Astrocyte                           |                 3 |                  7.09 |
| Bergmann glia                       |                 0 |                  0.03 |
| Choroid plexus                      |                 0 |                  0.02 |
| Committed oligodendrocyte precursor |                 1 |                  1.63 |
| Ependymal                           |                 2 |                  0.96 |
| Fibroblast                          |                 6 |                  4.18 |
| Microglia                           |                16 |                  6.96 |
| Oligodendrocyte                     |                10 |                  7.09 |
| Oligodendrocyte precursor           |                 1 |                  6.96 |
| Vascular                            |                 0 |                  4.08 |

## B. Strong-candidate class composition under the block-shuffle null

The Strong rule (residual < 0.3, omega < 15, lowest-in-pair) was re-evaluated on each of the B = 1000 permutations exactly as in addendum S1b; per-class candidate counts were tallied per permutation.

| cell_type                           |   observed_strong |   null_mean |   null_max |
|:------------------------------------|------------------:|------------:|-----------:|
| Microglia                           |                16 |        52   |        169 |
| Oligodendrocyte                     |                10 |        43.7 |        110 |
| Fibroblast                          |                 6 |         7   |         76 |
| Astrocyte                           |                 3 |         3.2 |        100 |
| Ependymal                           |                 2 |         4.1 |         36 |
| Oligodendrocyte precursor           |                 1 |        34.2 |        141 |
| Committed oligodendrocyte precursor |                 1 |         2.8 |         39 |
| Bergmann glia                       |                 0 |         0.1 |          5 |
| Choroid plexus                      |                 0 |         0.4 |          5 |
| Vascular                            |                 0 |         1   |         58 |

Microglia: observed 16 vs null-rule expectation 52.0 (fold 0.31); permutation P(null microglia count >= 16) = 0.990.

## C. Tier-sensitivity grid for the microglia enrichment

The Strong rule was re-applied at alternative (residual, omega-cap) thresholds on the observed landscape; microglia enrichment is recomputed per combination (hypergeometric over the class share of comparisons, Bonferroni across the ten classes).

|   res_threshold |   omega_cap |   n_strong |   microglia |   microglia_fold |   hypergeom_P |   bonferroni_P |
|----------------:|------------:|-----------:|------------:|-----------------:|--------------:|---------------:|
|            0.2  |          12 |          1 |           1 |             5.6  |        0.1785 |         1      |
|            0.2  |          15 |          1 |           1 |             5.6  |        0.1785 |         1      |
|            0.2  |          20 |          1 |           1 |             5.6  |        0.1785 |         1      |
|            0.2  |          25 |          1 |           1 |             5.6  |        0.1785 |         1      |
|            0.25 |          12 |         12 |           5 |             2.33 |        0.0474 |         0.474  |
|            0.25 |          15 |         13 |           5 |             2.15 |        0.066  |         0.6601 |
|            0.25 |          20 |         13 |           5 |             2.15 |        0.066  |         0.6601 |
|            0.25 |          25 |         13 |           5 |             2.15 |        0.066  |         0.6601 |
|            0.3  |          12 |         33 |          13 |             2.21 |        0.003  |         0.0297 |
|            0.3  |          15 |         39 |          16 |             2.3  |        0.0006 |         0.006  |
|            0.3  |          20 |         41 |          16 |             2.19 |        0.0012 |         0.0115 |
|            0.3  |          25 |         42 |          16 |             2.13 |        0.0016 |         0.0156 |
|            0.35 |          12 |         77 |          22 |             1.6  |        0.0138 |         0.1381 |
|            0.35 |          15 |         96 |          35 |             2.04 |        0      |         0.0001 |
|            0.35 |          20 |        108 |          39 |             2.02 |        0      |         0      |
|            0.35 |          25 |        109 |          39 |             2    |        0      |         0.0001 |
|            0.4  |          12 |        164 |          47 |             1.61 |        0.0004 |         0.0044 |
|            0.4  |          15 |        206 |          75 |             2.04 |        0      |         0      |
|            0.4  |          20 |        251 |          97 |             2.16 |        0      |         0      |
|            0.4  |          25 |        259 |          99 |             2.14 |        0      |         0      |

## D. Permutation calibration of the lower-tail count

V = number of pairs with lower-tail p < 0.05 in one null experiment (recomputed per permutation as in addendum S1a). Observed V = 1960; null mean = 1588.2; null 95th percentile = 1868; null 99th percentile = 1956; null max = 2138.0; P(V_null >= 1960) = 0.011.

## E. Strong-candidate composition under alternative gene-selection schemes

Applying the same Strong rule (residual < 0.3, omega < 15, lowest-in-pair) on the leave-pair-out (S2) omega scale fires on 457 pairs; microglia contribute 85 (fold 1.04, hypergeometric P = 0.3561, Bonferroni P = 1.000).

Class composition (S2 leave-pair-out Strong): Fibroblast: 120, Committed oligodendrocyte precursor: 115, Vascular: 93, Microglia: 85, Astrocyte: 21, Oligodendrocyte: 15, Oligodendrocyte precursor: 5, Ependymal: 3

On the unselected (S3; all 5,000 non-HK genes) omega scale the same rule fires on 10 pairs; microglia contribute 1 (fold 0.56, hypergeometric P = 0.8601, Bonferroni P = 1.000).

Class composition (S3 unselected Strong): Committed oligodendrocyte precursor: 6, Astrocyte: 3, Microglia: 1

