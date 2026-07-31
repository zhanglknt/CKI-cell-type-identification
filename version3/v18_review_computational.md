# v18 Review: Computational/Algorithm Expert

## Overall Score: 5/10
## Readiness: 55%

## Summary

CKI proposes a heuristic decomposition of transcriptomic divergence into a housekeeping-gene baseline (k_n) and a functional-gene divergence (k_f), with the ratio ω = k_f/k_n inspired by the Ka/Ks analogy. The conceptual motivation is sound and the negative correlation with all standard distance metrics (Spearman r = −0.38 to −0.57) is a genuinely interesting finding. The codebase is well-structured, modular, and documented, and the JS divergence implementation (base-2, softmax normalization) is mathematically correct.

However, the submission has several critical issues that must be resolved before it can be recommended for acceptance. The most severe is a direct internal contradiction in the calibration ω value (6.67 in Results vs. 1.54 in Discussion/Statistical Reporting), which undermines the paper's central argument that CKI recognizes equivalent populations as having ω ≈ 1. Second, the manuscript repeatedly claims Benjamini-Hochberg FDR correction is applied, but the Reproducibility Guide explicitly states it is NOT applied—a contradiction that makes the reported significance claims unverifiable. Third, Algorithm 1's pseudocode says ω is "capped at 1,000," but the actual code implements an undocumented k_n floor of 1e-4 instead, with no cap. Fourth, the pairwise DE gene selection in the code uses Wilcoxon rank-sum testing, while the pseudocode (Algorithm 2) says genes are ranked by absolute mean difference |μ_A − μ_B|—a different selection criterion. These are not minor cosmetic issues; they affect numerical reproducibility and the validity of the statistical claims.

The bootstrap test design also has conceptual problems: the absolute-deviation-from-ω=1 test statistic conflates the theoretical null (ω=1) with the empirical permutation null, and the manuscript's own calibration data (whether 6.67 or 1.54) shows that ω is substantially >1 for equivalent populations, contradicting the claim that ω ≈ 1 is the operational baseline. The kn_min=1e-4 floor can dominate results when k_n is small (especially for TCGA bulk data), effectively making ω ≈ k_f × 10^4 rather than a true ratio. I detail these issues below with specific line references.

## Critical Issues (must fix before submission)

- **[C1] Calibration ω contradiction: 6.67 vs. 1.54.** The Results section (manuscript line 47) states "The mean ω was 6.67 (median 6.46, range 1.59–12.16)" for the six calibration controls. The Abstract (line 10) repeats "mean ω = 6.67." However, the Statistical Reporting section (line 37) and Discussion (line 91) both state "mean observational ω = 1.54 for equivalent populations." These cannot both be correct. The 1.54 value is used to justify anchoring the P-value at ω=1 and to argue the calibration is "close to 1"—but if the true calibration mean is 6.67, that argument fails entirely, since 6.67 is far from 1. If 1.54 is correct, then the Results section, Abstract, range (1.59–12.16), and median (6.46) are all wrong. This is the single most damaging inconsistency in the paper and must be resolved before any further review.

- **[C2] FDR correction: manuscript says applied, reproducibility guide says NOT applied.** The manuscript states "Benjamini-Hochberg FDR correction is applied within each dataset" in at least four places (lines 22, 37, 43; Supplementary Note 3.2, 3.3). The Reproducibility Guide (Section 5.2, line 151) explicitly contradicts this: "Multiple testing correction (Benjamini-Hochberg FDR) is NOT systematically applied in the current analyses: all reported P-values and significance thresholds use raw (uncorrected) bootstrap P-values." The reproducibility checklist (line 197) repeats: "FDR correction is not applied in the current analyses." The code provides `benjamini_hochberg()` and `apply_fdr()` functions, but whether they are actually called in the analysis notebooks is unclear. This must be reconciled: either apply FDR and update the guide, or remove all FDR claims from the manuscript and clearly state that raw P-values are reported.

- **[C3] Undocumented k_n floor (kn_min=1e-4) replaces the stated ω cap at 1,000.** Algorithm 1 pseudocode (Supplementary Note 2, step 7) says "omega <- k_f / k_n  // capped at 1,000." Supplementary Note 1.1 says "in practice omega is capped at 1,000." The actual code in `core.py:242-246` implements something entirely different:
  ```python
  kn_min = 1e-4  # lower bound on k_n
  if kn < kn_min:
      omega = kf / kn_min
  else:
      omega = kf / kn
  ```
  There is NO cap at 1,000. Instead, k_n is floored at 1e-4, which means ω can reach up to kf/1e-4 = 10,000 (since JS divergence ≤ 1). The Reproducibility Guide (line 193) mentions "Verify epsilon = 1e-9 in omega computation"—this refers to the softmax epsilon, not the kn_min=1e-4 floor, which is never mentioned anywhere in the manuscript or guide. This floor has major numerical consequences: for TCGA bulk RNA-seq where HK gene expression is very similar between samples (k_n often ≈ 0), ω is effectively kf × 10^4, not a true ratio. The reported TCGA ω values (e.g., 344.5 for Luminal A) are consistent with this floor being active. The pseudocode, manuscript text, and code must all be aligned.

- **[C4] Pairwise DE gene selection: Wilcoxon (code) vs. absolute mean difference (pseudocode).** Algorithm 2 (Supplementary Note 2) specifies:
  ```
  1. Delta <- |mu_A - mu_B|  // per-gene absolute expression difference
  2. I <- indices of top-N genes ranked by descending Delta, excluding H
  ```
  The Reproducibility Guide (line 96) also says "top-200 DE genes (ranked by |mean_diff|)." However, the actual code in `gene_sets.py:534-603` (`_detect_by_pairwise_de`) uses `sc.tl.rank_genes_groups` with `method="wilcoxon"`, which ranks genes by Wilcoxon rank-sum statistical significance, NOT by absolute mean difference. These are different criteria: Wilcoxon considers both effect size and variance/p-value, while |mean_diff| is a pure effect-size ranking. This discrepancy means the pseudocode cannot reproduce the actual results. Either rewrite Algorithm 2 to match the Wilcoxon implementation, or change the code to use |mean_diff| ranking.

- **[C5] The absolute-deviation-from-ω=1 test conflates theoretical and empirical nulls.** The P-value formula P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1)/(B + 1) anchors at ω=1 (the theoretical null of "no functional divergence"). But the permutation null distribution of ω_null is NOT centered at 1: under cell-label permutation, the same HVG gene set is used for k_f, so k_f remains inflated relative to k_n even for random splits, producing ω_null values substantially >1. The manuscript itself acknowledges this (line 37): "The empirical calibration mean of ω = 1.54 for split-half equivalent populations reflects residual measurement noise." If ω_null is centered at ~1.54 (or ~6.67 per the Results section), then the test is really asking "is |ω_obs − 1| larger than |ω_null − 1|," which is a valid permutation test of exchangeability—but it is NOT a test of H0: ω = 1. The manuscript's claim that "The P-value is anchored at the theoretical null of ω = 1 (k_f = k_n, i.e., zero functional divergence), which represents the formal null hypothesis that the two populations are functionally identical" (line 37) is misleading. The test actually evaluates whether the observed pair is more divergent than random label permutations, which is a different (though still useful) question. The null hypothesis should be restated as H0: the two populations are exchangeable (their labels are arbitrary).

## Major Issues (should fix)

- **[M1] Version mismatch: code is v0.3.2, manuscript reports v0.3.1.** `__init__.py:37` declares `__version__ = "0.3.2"`, but the manuscript (line 98), Data Availability (line 100), and Reproducibility Guide (line 17) all reference v0.3.1. This means the code reviewed here may differ from the code that produced the reported results. The Zenodo DOI (line 100) should also be verified to point to the correct version. Pin the exact version tag used for all analyses.

- **[M2] Inconsistent `use_reference_hk` defaults between `compute()` and `bootstrap_test()`.** In `core.py:266`, `compute()` has `use_reference_hk: bool = False` (data-driven only). In `bootstrap.py:126`, `bootstrap_test()` has `use_reference_hk: bool = True` (reference-enhanced). With `merge_mode="union"` (default in `detect_housekeeping_genes`), the latter produces the UNION of data-detected and HRT Atlas genes, not "the pre-specified HRT Atlas reference" alone. The manuscript states "all reported analyses use the pre-specified HRT Atlas reference" (line 19), which implies only the reference genes are used—not a union. If the analysis notebooks pass `hk_genes` manually (bypassing auto-detection), this is moot for the reported results, but the API inconsistency will confuse users trying to reproduce results using the public API.

- **[M3] Softmax on log1p-transformed data amplifies high-expression genes dramatically.** The softmax normalization p_i = exp(x_i) / Σexp(x_j) is applied to log1p-transformed expression values. For typical log1p data: a gene at expression 0 (log1p=0) gets weight exp(0)=1, while a gene at expression 100 (log1p≈4.6) gets weight exp(4.6)≈100. This means JS divergence is dominated by the handful of highest-expression genes in each set. For k_n, this means the metric is effectively driven by the top 1–2 most highly expressed HK genes (e.g., GAPDH, ACTB) rather than the full HK gene profile. This is not necessarily wrong, but it is an unusual choice that should be explicitly justified. An alternative (simple L1 normalization: p_i = x_i / Σx_j) would give all expressed genes proportional weight. The manuscript should discuss why softmax is preferred over L1 normalization for log1p data.

- **[M4] The multiplicative residual model thresholds are arbitrary and lack statistical calibration.** The Strong/Moderate/Weak tiers (residual < 0.3/0.5/0.75 with ω < 15/25/35) are heuristic cutoffs with no statistical justification. There is no permutation-based or analytical derivation of these thresholds. The Limitations section (line 97) acknowledges that "at a nominal alpha = 0.05, approximately 1,588 false positives would be expected among 31,764 tests," but the 30 Strong candidates are selected by residual thresholds, not by P-values, so this FDR discussion is somewhat orthogonal. A more principled approach would be to fit log(ω) ~ cell_type + region_pair (additive model on log scale, equivalent to the multiplicative model) and use the residual distribution to define outliers (e.g., residuals in the bottom 1% or 0.1% of a fitted normal/Gamma distribution).

- **[M5] The brain atlas preprocessing pipeline differs from the standard CKI pipeline.** The manuscript (line 27) describes a unique brain atlas preprocessing: "Pseudobulk vectors were computed as the mean of raw counts per group, then normalized using Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation at the pseudobulk level." This is the reverse of the standard pipeline (normalize → log1p → pseudobulk) used for Tabula Muris and Tabula Sapiens. Normalizing at the pseudobulk level (rather than cell level) means the library size correction is applied to aggregated counts, which can give different results when cell counts per group vary widely. The `preprocess.py` code implements the standard pipeline (cell-level normalization), not the brain-specific pipeline. This means the brain analysis cannot be reproduced using the documented CKI API alone—the analysis notebook implements a custom preprocessing path that is not part of the package.

- **[M6] The "Genome Biology manuscript" reference in code comments.** `gene_sets.py:546` and `core.py:343` contain comments referencing "the Genome Biology manuscript." The current submission is to NAR, not Genome Biology. These leftover comments suggest the manuscript was previously submitted elsewhere and should be cleaned up, as they may confuse reviewers checking code-manuscript correspondence.

- **[M7] Brain pair count verification: partial inconsistency.** The manuscript reports pair counts per cell type that can be verified against the formula n×(n−1)/2 for n regions:
  - Astrocytes: 108 regions → 5,778 pairs ✓
  - Microglia: 107 regions → 5,671 pairs ✓
  - Bergmann glia: 7 regions → 21 pairs ✓
  - Committed OPCs: 52 regions → 1,326 pairs ✓
  - Fibroblasts: 83 regions → 3,403 pairs ✓
  - Vascular cells: 82 regions → 3,321 pairs ✓
  - Ependymal cells: 40 regions → 780 pairs ✓

  These 7 cell types sum to 20,300 pairs. The remaining 3 cell types (oligodendrocytes, OPCs, choroid plexus) must account for 11,464 pairs. Line 77 states "5,671 OPC cross-region comparisons"—the same count as microglia (107 regions). If OPCs also span 107 regions, that leaves oligodendrocytes + choroid plexus = 5,793 pairs. The manuscript does not provide complete pair counts for all 10 cell types. A complete summary table should be provided (Supplementary Table 3 is referenced but not shown) so the total of 31,764 can be verified.

- **[M8] Migration candidate count arithmetic error.** The manuscript (line 75) states "30 (0.09%) were classified as Strong... Another 1,247 pairs (3.93%) were Moderate candidates, and 6,567 (20.67%) were Weak candidates." Supplementary Table 4 states "7,842 pairs (24.7%) were classified as migration candidates." However, 30 + 1,247 + 6,567 = 7,844, not 7,842. The total is off by 2. This is a minor arithmetic error but should be corrected.

## Minor Issues (nice to fix)

- **[m1] `min_cells` parameter inconsistency across code and manuscript.** `preprocess.py:19` defaults to `min_cells=3`. The manuscript (line 19) says "requiring at least 10 cells per group." The brain atlas (line 27) uses ">= 20 nuclei per group." `_detect_by_pairwise_de` in `gene_sets.py:555` hardcodes a check for `< 10` cells. These thresholds should be consistent or the differences should be clearly documented.

- **[m2] `ci_95` variable name is misleading.** In `bootstrap.py:340-343`, the variable `ci_95` stores the 2.5th and 97.5th percentiles of the null distribution. Supplementary Note 3 (line 149) correctly notes these are "permutation-based test critical values for rejecting H0, NOT confidence intervals for omega itself." The variable should be renamed to `null_critical_values` or `null_percentiles` to avoid confusion.

- **[m3] Cohen's d uses population SD (ddof=0) instead of sample SD (ddof=1).** `bootstrap.py:334` uses `np.std(null_omega)` which defaults to `ddof=0`. Standard Cohen's d typically uses sample SD. With B=1000, the difference is negligible (√(1000/999) ≈ 1.0005), but for consistency with the statistical literature, `ddof=1` should be used.

- **[m4] `delta_hk` and `delta_identity` in `compute_omega` are redundant with `kn` and `kf`.** `core.py:229-239` computes `delta_hk` and `delta_identity` by calling `js_divergence` on the same gene subsets used for `kn` and `kf`. When `alpha=1.0` and `w2=0.0` (the defaults), `delta_hk == kn` and `delta_identity == kf`. This redundancy could confuse users reading the source code. Consider removing the redundant fields or documenting that they are identical to kn/kf under default parameters.

- **[m5] The n_top_genes adaptive cap is undocumented.** `gene_sets.py:429` caps HVG selection at `min(n_top_genes, int(n_total_genes * 0.8))`. This 80% cap is not mentioned in the manuscript or Supplementary Methods. For datasets with few genes, this could silently reduce the HVG count below the user-specified value.

- **[m6] The `detect_by_detection_rate` function changes behavior when `cell_type_col` is provided.** When `cell_type_col` is set (which it always is in `compute()`, since `cell_type_col or groupby` is passed), the detection rate is computed per-cell-type (requiring detection in >90% of cells within EACH cell type), which is much stricter than the global detection rate described in the manuscript. This behavioral difference should be documented, or the per-cell-type logic should be made opt-in rather than default.

- **[m7] B=1000 may be insufficient for the brain atlas (31,764 tests).** With B=1000, the minimum achievable P-value is 1/1001 ≈ 9.99e-4. For 31,764 tests at Bonferroni-corrected α = 0.05/31764 ≈ 1.57e-6, no test can reach significance. Even with BH-FDR at α=0.05, the smallest adjusted P-value would be ~9.99e-4 × 31764/1 ≈ 0.032, so only the single most extreme test could potentially pass FDR. If bootstrap testing is intended to support the brain analysis claims, B should be increased substantially (e.g., B=10,000 or 100,000) or the inference should rely entirely on the non-parametric tests and residual model.

- **[m8] The `pseudobulk_a`/`pseudobulk_b` path in `bootstrap_test` has an unclear n_a.** `bootstrap.py:274` sets `n_a = X.shape[0] // 2` when pre-computed pseudobulks are provided, assuming the input matrix contains exactly the two groups concatenated. This is fragile—if the user passes the full dataset matrix, the split will be incorrect. The function should require explicit `n_a` when pre-computed pseudobulks are used.

## Strengths

- **Conceptual innovation.** The Ka/Ks analogy for transcriptomic comparison is creative and well-motivated. The decomposition into baseline (k_n) and functional (k_f) components addresses a real limitation of standard distance metrics, and the negative correlation with all four standard metrics (r = −0.38 to −0.57) is strong evidence that CKI captures an independent information dimension.

- **JS divergence implementation is correct.** The base-2 logarithm JS divergence in `core.py:19-55` is mathematically correct, properly handles zero-probability terms via masking (`mask_p = p > 0`), and returns values in [0, 1] as claimed. The `ensure_probability_distribution` utility correctly implements numerically stable softmax.

- **Comprehensive multi-dataset validation.** Testing across four independent datasets (Tabula Muris, Tabula Sapiens, TCGA, Siletti brain atlas) at different scales (mouse → human, single-cell → bulk, atlas → disease) demonstrates the method's breadth. The inclusion of calibration controls is a strength, even if the specific numbers have issues.

- **The multiplicative residual model is elegant.** The two-way multiplicative model (expected_ω = μ_ct × μ_pair / μ_grand) for detecting anomalous cell-type/region pairs is a clean and interpretable approach. The OPC negative control (0 Strong signals despite highest motility) is a powerful validation of specificity.

- **Code quality.** The CKI package is well-organized (core, bootstrap, gene_sets, preprocess, utils, species modules), thoroughly documented with docstrings, and includes type hints. The BH FDR implementation (`bootstrap.py:18-64`) is correct. The HRT Atlas reference file is properly bundled (1,130 genes verified).

- **Reproducibility infrastructure.** The Reproducibility Guide is detailed, specifying exact software versions, data sources, parameters, and output file paths. The random seed (42) is fixed throughout. The open-source release with MIT license and Zenodo DOI deposition follow best practices.

- **The 6.06-fold brain gradient is arithmetically verified.** 14.36 / 2.37 = 6.06. ✓ All brain region-pair counts that can be verified match the n×(n−1)/2 formula. The percentage calculations for migration tiers (0.09%, 3.93%, 20.67%) are individually correct (though their sum has the minor arithmetic error noted in M8).

## Specific Recommendations

1. **Resolve the 6.67 vs. 1.54 calibration contradiction immediately** (C1). Re-run the calibration controls, report the correct value, and ensure the Discussion and Statistical Reporting sections are consistent with the Results. If 6.67 is correct, the argument that ω ≈ 1 for equivalent populations needs to be fundamentally revised, and the P-value anchoring at ω=1 needs new justification. If 1.54 is correct, update the Results section with the accurate mean, median, and range.

2. **Reconcile the FDR correction claim** (C2). Either apply BH-FDR in the analysis scripts (and verify the notebooks actually call `apply_fdr`) or remove all FDR claims from the manuscript. If raw P-values are reported, state this explicitly and discuss the implications for the 31,764 brain comparisons.

3. **Align the pseudocode with the actual implementation** (C3, C4). Either: (a) update Algorithm 1 to describe the kn_min=1e-4 floor instead of the ω cap at 1,000, and update Algorithm 2 to describe Wilcoxon DE instead of |mean_diff| ranking; or (b) change the code to match the pseudocode (add a ω cap at 1,000, implement |mean_diff| ranking for pairwise DE). Option (a) is easier but requires justifying the kn_min floor; option (b) is cleaner but requires re-running all analyses.

4. **Increase B for large-scale analyses** (m7). For the brain atlas (31,764 tests), B=1,000 is insufficient for any meaningful multiple-testing-corrected inference. Consider B=10,000 for the brain analysis, or rely on the non-parametric tests (which are already reported) and the residual model for significance assessment.

5. **Justify or replace the softmax normalization** (M3). Provide a sensitivity analysis comparing softmax vs. L1 normalization on log1p data, showing that the key results (negative correlation with standard metrics, brain gradient, TCGA convergence) are robust to the normalization choice. If softmax is retained, explain why amplifying high-expression genes is desirable for this application.

6. **Document the kn_min=1e-4 floor explicitly** in the manuscript (not just the code). Report what fraction of comparisons in each dataset have k_n < 1e-4 (i.e., are affected by the floor). If a substantial fraction of TCGA comparisons hit the floor, the ω values for those comparisons are effectively k_f × 10^4, not a true ratio, and this should be discussed as a limitation.

7. **Provide a complete cell-type summary table** for the brain analysis (M7) showing all 10 cell types, their region counts, pair counts, mean ω, and k_n/k_f decomposition, with the pair counts summing to exactly 31,764.

8. **Pin the code version** (M1). Tag the exact commit used for all reported analyses as v0.3.1 on GitHub, and ensure the `__init__.py` version matches. Update the Zenodo DOI if necessary.
