# v45 analysis B: small-cluster corrections for region-clustered bootstrap CIs

Seed 20260905; Part 1 B = 5000; Part 2 2000 simulations x B = 999.

## Part 1  Alternative 95% intervals on the real data

### Bergmann glia class-mean omega (7 regions)
- point estimate: 13.555
- percentile cluster bootstrap: [9.13, 19.45] (width 10.32)  (reference [8.49, 19.52] published)
- wild cluster bootstrap (Rademacher): [8.69, 18.42] (width 9.73)
- studentized bootstrap-t: [5.76, 28.59] (width 22.84)

### Choroid plexus class-mean omega (6 regions)
- point estimate: 37.756
- percentile cluster bootstrap: [27.30, 55.76] (width 28.46)  (reference [27.30, 56.19] published)
- wild cluster bootstrap (Rademacher): [24.48, 51.03] (width 26.54)
- studentized bootstrap-t: [25.93, 76.30] (width 50.37)

### Astrocyte / Bergmann-glia calibrated gradient
- point estimate: 5.985
- percentile cluster bootstrap: [4.10, 9.28] (width 5.18)  (reference [4.12, 9.18] published (joint percentile))
- wild cluster bootstrap (Rademacher): [4.13, 8.61] (width 4.48)
- studentized bootstrap-t: [4.43, 7.69] (width 3.26)

## Part 2  Monte Carlo coverage (nominal 95%)

| scenario | percentile | wild | bootstrap-t |
|---|---|---|---|
| 7 clusters (Bergmann-like) | 0.876 | 0.816 | 0.953 |
| 6 clusters (choroid-like) | 0.873 | 0.806 | 0.951 |

MC standard error of a coverage estimate near 0.90: ~0.0067.

## Conclusions / recommendation

1. **Percentile cluster bootstrap under-covers by ~7-8 points at G = 6-7.** Monte Carlo coverage of the nominal 95% interval: 0.876 (7 clusters) and 0.873 (6 clusters). The published percentile intervals for Bergmann glia and choroid plexus are therefore too narrow, confirming reviewer P1-2.

2. **Wild cluster bootstrap (Rademacher) is worse** (0.816 / 0.806): with 2^6-2^7 sign combinations the tails are coarse, and the symmetric perturbation cannot reproduce the skewness of the few-cluster sampling distribution. Not recommended as the replacement.

3. **Studentized bootstrap-t attains nominal coverage** (0.953 / 0.951) and is the recommended replacement for every statistic resting on <= 7 region clusters. The price is honestly wider intervals (simulation mean width 16.0 vs 9.2 for the percentile at G = 7).

4. **Recommended replacement intervals (studentized bootstrap-t, 95%):**
   - Bergmann glia class-mean omega 13.56: [5.76, 28.59] (width 22.84) (was percentile [8.49, 19.52]). The lower bound 5.76 now falls BELOW the class baseline 9.08, so the claim that Bergmann glia diverges above its own class baseline does not survive the small-cluster correction and should be DOWNGRADED to a qualitative statement (cross-region omega elevated in absolute terms, but not separable from baseline at 7 regions). This is consistent with the notebook-81 joint calibrated-omega CI [0.99, 2.12], which already includes 1.
   - Choroid plexus class-mean omega 37.76: [25.93, 76.30] (width 50.37) (was percentile [27.30, 56.19]). Lower bound remains far above its baseline 10.66; the choroid divergence claim STANDS quantitatively.
   - Astrocyte/Bergmann calibrated gradient 5.99x: [4.43, 7.69] (width 3.26) (was joint percentile [4.12, 9.18]). All three methods agree the lower bound is > 4 (percentile 4.10, wild 4.13, bootstrap-t 4.43), so the gradient claim is ROBUST and can remain quantitative; update the reported interval to the bootstrap-t one.

5. Wild bootstrap and percentile intervals are retained above for the record; the studentization uses the sandwich variance of the multiplicity-weighted pair mean evaluated on the resampled graph (degree G - m_i per redrawn region), which is the consistent resampled-world analogue of the point-estimate influence-function se.