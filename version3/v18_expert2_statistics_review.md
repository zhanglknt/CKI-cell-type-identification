# CKI Manuscript Statistical Methodology Review (v18 Expert 2)

**Reviewer**: Statistics & Data Analysis Expert  
**Date**: 2026-07-27  
**Scope**: P-value methodology, bootstrap adequacy, multiple testing, effect sizes, statistical power  
**Files reviewed**: `generate_manuscript_nar.py` (manuscript text), `notebooks/68_gen_supplementary_en.py` (supplementary), `version3/v17_review_synthesis.md` (prior review), `notebooks/02c_pilot_v2b.py` (mouse bootstrap), `notebooks/08a_tcga_bootstrap.py` (TCGA bootstrap), `notebooks/08b_human_bootstrap_csv.py` (human bootstrap), `notebooks/08c_brain_bootstrap.py` and `08c_brain_bootstrap_csv.py` (brain bootstrap), `cki/bootstrap.py` (core bootstrap module), `results/*.csv` (bootstrap outputs)

---

## 1. Overall Assessment

**Score: 3.5 / 10**

The manuscript presents a novel heuristic metric (CKI ω) with an appealing biological analogy to Ka/Ks. However, the statistical inference framework has critical implementation flaws that undermine the validity of the reported P-values for three of four datasets. Specifically, the brain and human "bootstrap" scripts do not implement the permutation test described in the manuscript—they perform bootstrap resampling of pre-computed ω values, producing P-values clustered at ~0.5 that are mathematically uninformative. Only the mouse pilot and TCGA bootstrap scripts implement the correct label-permutation procedure. Additionally, the P-value formula using |ω−1| as test statistic against a permutation null that is centered far from 1 creates a conceptually muddled and potentially very conservative test. The FDR limitation disclosure, while transparent, is insufficient for the 31,764-comparison brain analysis where 30 "Strong" candidates receive extensive biological interpretation without multiple testing correction. Several other statistical issues (sample size, effect size interpretation, confidence interval reporting) compound these problems.

---

## 2. Strengths

1. **Transparent reporting of limitations**: The manuscript explicitly states that no FDR correction was applied and provides an expected false positive calculation (≈1,588 at α=0.05 for 31,764 tests). The P-value formula is fully specified in both the manuscript and supplementary materials.

2. **Correct permutation test for mouse and TCGA**: The `02c_pilot_v2b.py` and `08a_tcga_bootstrap.py` scripts correctly pool cells from both groups, permute labels, recompute pseudobulks, and recalculate ω_null. The P-value formula `P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1)/(B + 1)` is correctly implemented in these scripts and in `cki/bootstrap.py`.

3. **Pseudocount approach is principled**: The +1 pseudocount in the P-value formula follows Phipson & Smyth (2010) and ensures P > 0, preventing infinite odds ratios. This is standard practice for permutation tests.

4. **Calibration experiment design**: The split-half calibration using biologically equivalent populations (random split of same cell type) is a sensible approach for validating baseline behavior. The inclusion of a negative control (OPCs with 0 Strong signals despite high motility) demonstrates methodological awareness.

5. **Supplementary materials are detailed**: The algorithm pseudocode, mathematical derivation, and statistical testing details are thoroughly documented, enabling reproducibility assessment.

---

## 3. Concerns

### Critical Concerns

#### C1. Brain and human bootstrap P-values are mathematically meaningless (IMPLEMENTATION ERROR)

**This is the most serious statistical issue in the manuscript.**

The manuscript (Methods, line 371) states:
> "We randomly permute cell labels between the two populations (B = 500 for the mouse pilot...B = 100 for brain atlas), recompute pseudobulk vectors, and calculate ω_null for each permutation."

The actual brain bootstrap code (`08c_brain_bootstrap_csv.py`) does NOT permute cell labels. It:

1. Loads **pre-computed** ω values from `brain_siletti_omega_pairs_v3.csv`
2. For each cell type, **resamples the ω values with replacement** (bootstrap, not permutation)
3. Computes P-value as: `(np.sum(boot_means >= obs_mean) + 1) / (N_BOOTSTRAP + 1)`

This tests whether the bootstrap mean exceeds the observed mean. By construction of the bootstrap, approximately 50% of resampled means will exceed the observed mean, producing P ≈ 0.5 regardless of the data.

**Confirmation in data**: All 10 brain bootstrap P-values are between 0.477 and 0.521 (`brain_bootstrap_results.csv`):

| Cell type | P-value |
|-----------|---------|
| Astrocyte | 0.4825 |
| Oligodendrocyte | 0.5205 |
| Microglia | 0.5135 |
| OPC | 0.4885 |
| Choroid plexus | 0.4915 |
| Ependymal | 0.4845 |
| Fibroblast | 0.4765 |
| Vascular | 0.5015 |
| Committed OPC | 0.5035 |
| Bergmann glia | 0.4855 |

All cluster at 0.5, confirming the test is uninformative.

The same issue exists in the human bootstrap (`08b_human_bootstrap_csv.py`): all P-values are 0.500–0.504 (`human_bootstrap_results.csv`).

**The original brain bootstrap script** (`08c_brain_bootstrap.py`, B=100) has an even more fundamental error: it attempts to "permute" pseudobulk labels, but the code itself acknowledges (line 164): *"This doesn't change anything..."* — permuting the order of pseudobulks and then computing all C(n,2) pairwise ω values produces the identical set of values, so the null mean always equals the observed mean, giving P = 0.5 exactly.

**Impact**: The manuscript claims "Bootstrap permutation testing was performed for all four datasets" (line 395), but for 2 of 4 datasets (human, brain), the P-values are mathematically meaningless. The brain analysis P-values are never individually reported in the manuscript text, but the supplementary materials present them as if they are valid statistical results.

**Required fix**: Implement a proper permutation test for the brain and human analyses. For each cell type, pool all cells across regions, permute region labels at the cell level (not pseudobulk level), recompute pseudobulks, and recalculate ω for each permutation. Use the correct P-value formula. This is computationally expensive but necessary for valid inference.

---

#### C2. P-value formula conflates theoretical null (ω=1) with permutation null (ω≫1)

The P-value formula `P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1)/(B + 1)` uses the absolute deviation from ω=1 as the test statistic in a permutation framework. This creates a conceptual problem:

- **The theoretical null** is ω = 1 (k_f = k_n, no functional divergence).
- **The permutation null** produces ω values far from 1. For TCGA, `null_mean ≈ 48.75` (LUAD) to `57.69` (BRCA) — see `tcga_bootstrap_results.csv`. For the mouse pilot, the null mean varies by comparison type but is generally >1.

The formula asks: "Is the observed deviation from 1 more extreme than the permuted deviation from 1?" But since both observed and permuted ω are far from 1, the test has very low power. This is illustrated by the TCGA results:

| Cancer | ω_obs | null_mean | |ω_obs−1| | |ω_null−1| ≈ | P-value |
|--------|-------|-----------|-----------|------------|---------|
| LUAD | 47.30 | 48.75 | 46.30 | 47.75 | 0.515 |
| LUSC | 21.57 | 57.27 | 20.57 | 56.27 | 1.000 |
| LIHC | 30.04 | 51.45 | 29.04 | 50.45 | 0.881 |
| KIRC | 54.15 | 46.84 | 53.15 | 45.84 | 0.356 |
| BRCA | 85.21 | 57.69 | 84.21 | 56.69 | 0.168 |

For LUSC, the observed ω (21.57) is *lower* than the null mean (57.27), meaning the tumor-normal divergence is *less* than random label shuffling. The formula interprets this as "observed deviation from 1 is smaller than null deviation from 1," giving P = 1.000 — but this doesn't mean the result is non-significant; it means the test is inappropriate for this data structure.

**Recommendation**: Either (a) use a one-sided test `P = count(ω_null ≥ ω_obs)/(B+1)` to test whether observed ω is in the upper tail of the permutation null, or (b) use `P = count(|ω_null − null_mean| ≥ |ω_obs − null_mean|)/(B+1)` to test deviation from the permutation null center.

---

#### C3. B=100 is insufficient for the brain and TCGA analyses

For B=100:
- Minimum achievable P-value: 1/101 ≈ 0.0099
- P-value resolution: 0.01

For the brain analysis with 31,764 comparisons:
- At α = 0.05, even a perfect test would yield P-values of 0.01, 0.02, 0.03... — only 100 distinct values
- BH-FDR correction at this resolution would be extremely coarse
- The 30 "Strong" candidates were selected by residual thresholds, not P-values, so this doesn't directly affect the Strong count — but it means no valid P-value-based inference is possible for the brain analysis

For TCGA (5 comparisons):
- B=100 gives adequate resolution for 5 tests
- But the permutation null produces P ≈ 0.35–1.0 for all cancers, so resolution is not the limiting factor

**Note**: The manuscript states B=100 for brain, but the actual brain results CSV (`brain_bootstrap_results.csv`) was generated by `08c_brain_bootstrap_csv.py` with `N_BOOTSTRAP = 1000` (line 18). The p-value precision (5 significant digits, e.g., 4.8252e-01) is consistent with B=1000, not B=100. This is another documentation discrepancy.

---

#### C4. No FDR correction for 31,764 brain comparisons; 30 "Strong" candidates receive extensive interpretation

The manuscript adds a limitation statement (line 514):
> "the 31,764 brain cross-region comparisons yielded 30 Strong candidates without formal multiple testing correction; at a nominal alpha = 0.05, approximately 1,588 false positives would be expected..."

This transparency is commendable, but the 30 Strong candidates are then subjected to extensive biological interpretation across 6 subsections of the Results (OPCs, oligodendrocytes, astrocytes, Bergmann glia, microglia, vascular cells, fibroblasts), with each signal assigned to a specific biological mechanism (developmental origin, colonization route, etc.). This depth of interpretation is inconsistent with a "hypothesis-generating" framing.

**Additional concern**: The "Strong" threshold (residual < 0.3, ω < 15, lowest ω in pair) is a composite criterion with no formal statistical basis. The residual thresholds (0.3, 0.5, 0.75) are arbitrary. No permutation-based null distribution for the residuals is provided, and no sensitivity analysis of threshold choice is reported.

**Required fix**: Either (a) apply BH-FDR to the 31,764 residuals (or their associated P-values, once properly computed), or (b) explicitly label all 30 signals as "exploratory, unvalidated" and remove the detailed biological mechanism assignments from the Results, deferring them to a hypothesis-generating Discussion paragraph.

---

### Major Concerns

#### M1. Mouse calibration sample size is extremely small (n=6)

The calibration experiment uses only 6 control comparisons (random splits of the same cell population). The reported mean ω = 1.54 with range [1.09, 2.10]. With n=6:
- The 95% CI for the mean is very wide: approximately 1.54 ± 0.39 (assuming SD ≈ 0.37 from the range)
- The manuscript itself acknowledges: "formal equivalence testing (e.g., TOST) with a larger calibration sample would provide stronger statistical evidence for equivalence"
- However, the calibration result is used to justify the P-value anchoring at ω=1, which is a key statistical decision

**Recommendation**: Increase calibration to at least n=20–30 controls. Report the 95% CI for the calibration mean and perform formal equivalence testing (TOST with equivalence bound ±0.5 ω units).

#### M2. Confidence intervals are null distribution quantiles, not parameter CIs

The `ci_95` reported in `tcga_bootstrap_results.csv` and `brain_bootstrap_results.csv` are the 2.5th and 97.5th percentiles of the null/permutation distribution, NOT confidence intervals for the observed ω. The supplementary materials acknowledge this (line 175–176):
> "Note: these are permutation-based test critical values for rejecting H0, NOT confidence intervals for omega itself."

However, the manuscript Results text does not clearly distinguish between:
- **Null distribution quantiles** (what is reported): describes the range of ω under the null
- **Confidence intervals for ω_obs** (what readers may expect): describes uncertainty in the observed estimate

For the brain bootstrap (CSV-based), the CI is a bootstrap CI for the *mean* ω across pairs, not for the observed ω itself.

**Recommendation**: Report bootstrap CIs for ω_obs (e.g., bootstrap the entire CKI pipeline including gene selection) and clearly label null distribution quantiles as "null 95% range" rather than "CI."

#### M3. Spurious correlation of ratios (Pearson 1897)

ω = k_f/k_n is a ratio. The negative correlation between ω and standard metrics (Spearman r = −0.19 to −0.41) could be partly driven by the mathematical coupling inherent in ratio variables: if k_n appears in both ω and (indirectly) in the standard metrics, a spurious negative correlation can emerge.

The v17 review flagged this (M2), but no partial correlation analysis has been added. The manuscript mentions (line 506) that "CKI currently lacks a formal phylogenetic framework" but does not address the ratio coupling issue.

**Recommendation**: Compute partial correlations between k_f (not ω) and standard metrics, controlling for k_n. If the partial correlation remains negative, the claim of an "independent information dimension" is strengthened.

#### M4. Cohen's d is computed against the permutation null, not a meaningful baseline

The effect size `Cohen's d = (ω_obs − mean(ω_null)) / sd(ω_null)` measures how far the observed ω is from the permutation null mean in null SD units. This is not a standard Cohen's d (which measures mean difference between two groups in pooled SD units). Calling it "Cohen's d" may mislead readers into thinking it represents a standardized mean difference between biological groups.

Additionally, when the null distribution is very wide (as in TCGA, where null_std ≈ 20), Cohen's d values are small even for large ω differences. For LUSC, d = −1.98 — a "large" effect by Cohen's conventions, but it indicates the observed ω is *below* the null mean, which is biologically uninterpretable.

**Recommendation**: Rename to "permutation z-score" or "standardized deviation from null." Report effect sizes in ω units (e.g., ω_obs / null_mean ratio) for biological interpretability.

#### M5. Multiplicative residual model lacks formal null distribution

The Strong/Moderate/Weak tiers (residual < 0.3/0.5/0.75) are based on `observed / expected` where `expected = μ_ct × μ_pair / μ_grand`. No permutation-based null distribution for the residuals is provided. It is unclear what residual values would be expected under a null model of no cell-type-specific regional effects.

**Recommendation**: Permute region labels within each cell type, recompute residuals, and derive empirical P-values for each (cell_type, region_pair) combination. This would provide a principled statistical threshold for "Strong" signals.

---

### Minor Concerns

#### m1. Terminology: "one-sided" vs "two-sided"

The code comment in `cki/bootstrap.py` (line 238) says "two-sided test" while the team lead's description says "one-sided." Using |ω−1| as the test statistic tests for deviation in either direction, which is a two-sided test. The manuscript should use consistent terminology.

#### m2. "Cohen's d" nomenclature

As noted in M4, the effect size is not a standard Cohen's d. Using the correct name would prevent confusion.

#### m3. Brain bootstrap script discrepancy

Two brain bootstrap scripts exist (`08c_brain_bootstrap.py` with B=100 and `08c_brain_bootstrap_csv.py` with B=1000). The results CSV was generated by the B=1000 script, but the manuscript reports B=100. The actual number of bootstrap iterations used for the brain analysis should be clarified.

#### m4. HRT Atlas usage in code vs manuscript

The manuscript now states `use_reference = False`, consistent with the code. However, `02c_pilot_v2b.py` (mouse pilot, line 50–51) loads HK genes from the HRT Atlas file directly: `hk_df = pd.read_csv(HK_FILE, sep=";")` — meaning the mouse pilot DID use HRT Atlas genes. This contradicts the manuscript's claim that HK detection was "purely data-driven" for all datasets.

---

## 4. P-value Methodology Deep Dive

### 4.1 Formula Analysis

The P-value formula:
```
P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1) / (B + 1)
```

**Mathematical validity**: This is a valid permutation P-value with the +1 pseudocount (Phipson & Smyth, 2010). The test statistic T = |ω−1| measures deviation from the theoretical null of ω=1.

**However, there are two distinct null hypotheses being conflated**:

1. **Theoretical null**: H₀: ω = 1 (k_f = k_n, no functional divergence). Under this null, the two populations are functionally identical.

2. **Permutation null**: H₀: the group labels are exchangeable. Under this null, ω follows the distribution obtained by permuting labels.

These are NOT the same hypothesis. The permutation null does not produce ω = 1; it produces ω values that depend on the heterogeneity of the pooled cells. For TCGA, the permutation null mean is ~50, meaning that random label assignments produce substantial "functional divergence" simply because the pooled tumor+normal cells are heterogeneous.

**The formula tests**: "Is the observed deviation from ω=1 more extreme than what the permutation null produces?" This is a valid question, but it has very low power when the permutation null is centered far from 1, because both observed and null values are far from 1, and the test reduces to comparing their relative distances.

### 4.2 The Anchoring Issue (ω=1 vs ω=1.54)

The manuscript now explains (line 395):
> "The P-value is anchored at the theoretical null of ω = 1 (k_f = k_n, i.e., zero functional divergence)... The empirical calibration mean of ω = 1.54 for split-half equivalent populations reflects residual measurement noise..."

This explanation is reasonable in principle: ω=1 is the formal theoretical null, and ω=1.54 is an empirical observation that includes technical noise. Using ω=1 as the anchor tests whether the observed ω deviates from the formal null, which is the correct statistical approach.

**However**: the P-value formula uses ω=1 as the anchor for BOTH the observed and permuted ω values. If the permutation null mean is 50 (as in TCGA), the formula effectively asks: "Is |ω_obs − 1| / |ω_null − 1| significantly different from 1?" — which is not a meaningful biological question.

**A more principled approach** would be to use a two-stage test:
1. First, establish the calibration null (ω ≈ 1.54 for equivalent populations)
2. Then, test whether the observed ω exceeds the calibration null by more than expected from measurement noise

### 4.3 The +1 Pseudocount

The +1 pseudocount ensures P > 0 and follows standard permutation test practice. With B=500, the minimum P = 1/501 ≈ 0.002. With B=100, the minimum P = 1/101 ≈ 0.01. These are adequate for individual tests but insufficient for multiple testing correction at the scale of 31,764 comparisons (where BH-FDR would require P-values on the order of 10⁻⁶ for genome-wide significance).

---

## 5. Bootstrap Adequacy Analysis

### 5.1 Mouse Pilot (B=500)

**Implementation**: Correct (`02c_pilot_v2b.py`, lines 286–320). Pools cells, permutes labels, recomputes pseudobulks and ω_null using the same gene selection procedure.

**Adequacy**: B=500 gives P-value resolution of 0.002. For 15 comparisons + 6 controls (21 total), this is adequate without FDR correction (Bonferroni α = 0.05/21 ≈ 0.0024, just above the resolution limit). Marginal but acceptable.

**Stability concern**: With only n=6 calibration controls, the calibration mean (ω = 1.54) has a wide CI. B=500 is sufficient for the P-value computation, but the small sample size is the real bottleneck.

### 5.2 Human Tabula Sapiens (B=1000)

**Implementation**: **INCORRECT** (`08b_human_bootstrap_csv.py`). Does not permute cell labels. Resamples pre-computed ω values with replacement. All P-values ≈ 0.50.

**Adequacy**: B=1000 would be adequate if the correct permutation test were implemented. With 5,151 pairs, the P-value resolution of 0.001 would be marginal for FDR correction but sufficient for exploratory analysis.

**Required fix**: Reimplement using cell-level permutation (as in `cki/bootstrap.py`).

### 5.3 TCGA (B=100)

**Implementation**: Correct (`08a_tcga_bootstrap.py` uses `cki.bootstrap.bootstrap_test`).

**Adequacy**: B=100 gives P-value resolution of 0.01. For 5 cancer types (5 tests), this is adequate. The P-values themselves (0.168–1.0) are non-significant, but this is due to the formula issue (C2), not the B value.

**Stability concern**: With B=100, the P-values have ±0.01 uncertainty. For the reported P-values (0.168, 0.356, 0.515, 0.881, 1.000), this uncertainty doesn't affect conclusions (all P > 0.05).

### 5.4 Brain Atlas (B=100 or B=1000?)

**Implementation**: **INCORRECT** (both `08c_brain_bootstrap.py` and `08c_brain_bootstrap_csv.py`).

- `08c_brain_bootstrap.py` (B=100): Attempts to permute pseudobulk labels, but the code itself acknowledges this doesn't change anything (line 164: *"This doesn't change anything..."*). All P-values would be exactly 0.5.
- `08c_brain_bootstrap_csv.py` (B=1000): Bootstraps pre-computed ω values. All P-values ≈ 0.5.

**Discrepancy**: Manuscript reports B=100 for brain, but the results CSV was generated with B=1000 (based on p-value precision).

**Required fix**: Implement a proper cell-level permutation test. For 888,263 nuclei across 108 regions, this is computationally challenging but feasible with subsampling or approximate permutation methods. At minimum, permute region labels at the pseudobulk level for each cell type — but note that this requires creating new pseudobulk combinations, not just relabeling existing ones.

---

## 6. Multiple Testing / FDR Assessment

### 6.1 Current State

- **Mouse pilot**: 21 tests, no FDR. Acceptable for exploratory analysis with small scale.
- **Human Tabula Sapiens**: 5,151 pairs, P-values are meaningless (C1). FDR cannot be applied to the current results.
- **TCGA**: 5 tests, no FDR. Bonferroni would require P < 0.01; all P > 0.05. No multiple testing issue.
- **Brain**: 31,764 comparisons, 30 Strong candidates selected by residual threshold (not P-value). No FDR applied. Limitation statement added.

### 6.2 Limitation Statement Assessment

The limitation statement (line 514) is:
> "the 31,764 brain cross-region comparisons yielded 30 Strong candidates without formal multiple testing correction; at a nominal alpha = 0.05, approximately 1,588 false positives would be expected among 31,764 tests, meaning the 30 Strong candidates should be interpreted as hypothesis-generating signals requiring independent validation rather than definitive discoveries."

**Assessment**: This is transparent but insufficient because:

1. The 1,588 expected false positives is calculated at α=0.05, but the Strong candidates were selected by residual < 0.3 (not P < 0.05). The expected false positive rate for residual < 0.3 is unknown without a null distribution for residuals.

2. The statement says "hypothesis-generating," but the Results section provides detailed biological mechanism assignments for all 30 candidates, with 6 subsections of interpretation. This creates a tension between the stated exploratory framing and the depth of biological claims.

3. No post-hoc FDR or permutation-based FDR is provided, even as a sensitivity analysis.

### 6.3 Recommendations

1. **If P-values can be properly computed** (after fixing C1): Apply BH-FDR to the 31,764 P-values. Report q-values alongside residuals. Identify which of the 30 Strong candidates survive FDR < 0.05 or < 0.10.

2. **If P-values cannot be computed** (computational limitations): Compute a permutation null for the residuals. Permute region labels within each cell type, recompute residuals, and derive empirical FDR.

3. **At minimum**: Add a sensitivity analysis showing how the Strong candidate count changes with residual threshold (e.g., 0.2, 0.25, 0.3, 0.35, 0.4). If the count is stable, the threshold choice is robust; if it changes dramatically, the threshold is arbitrary.

---

## 7. Effect Size & Confidence Intervals

### 7.1 ω as an Effect Size

ω = k_f/k_n is a ratio, not a standardized effect size. Its interpretation depends on:
- The absolute values of k_f and k_n (which vary by dataset)
- The gene selection method (global HVG vs pairwise DE)
- The number of genes used (2,000 for mouse, 200 for human/brain)

The manuscript acknowledges this: "users should compare ω ranks rather than absolute values across datasets" (line 506). This is an important caveat that limits cross-dataset comparability.

**Within-dataset**: ω is meaningful as a relative measure. The 6.06-fold gradient in the brain (2.37 to 14.36) is a valid within-dataset comparison.

**Cross-dataset**: The mouse mean ω ≈ 7.07 vs human mean ω ≈ 13.77 cannot be directly compared because the gene selection strategies differ (global HVG vs pairwise DE).

### 7.2 Cohen's d

As noted in M4, the reported "Cohen's d" is actually a permutation z-score: `d = (ω_obs − mean(ω_null)) / sd(ω_null)`. This is not a standardized mean difference between groups and should not be called Cohen's d.

For the mouse pilot, d values are reported as "typically > 1.0 for biologically meaningful comparisons" (supplementary, line 278). However, when the null distribution is narrow (small sd), even small ω differences produce large d values, and vice versa.

### 7.3 Confidence Intervals

The reported CIs are null distribution quantiles, not parameter CIs:
- `ci_95_lower` and `ci_95_upper` in the brain results are the 2.5th and 97.5th percentiles of bootstrap means
- `ci_95` in the TCGA results is the 2.5th and 97.5th percentiles of the permutation null ω

Neither provides a CI for the observed ω itself. To compute a proper CI for ω_obs, one would need to bootstrap the entire CKI pipeline (including gene selection) at the cell level.

---

## 8. Statistical Power Considerations

### 8.1 Mouse Pilot

- **n=6 controls**: Very low power for equivalence testing. The manuscript acknowledges this.
- **n=3–4 per comparison category (S, D, X)**: Insufficient for robust group-level inference.
- **B=500**: Adequate for P-value computation but limited by small biological replicates.

### 8.2 Human Tabula Sapiens

- **5,151 pairs**: Large sample, but P-values are invalid (C1).
- **59 cross-organ pairs across 17 cell types**: Many cell types have n=1–3 pairs (acknowledged in manuscript, line 453). Power for individual cell type rankings is very low.

### 8.3 TCGA

- **5 cancer types, n=57–1,094 samples per cancer**: Adequate sample sizes.
- **Paired tumor-normal: n=2–5 per cancer type**: Very low power (acknowledged in manuscript, line 443).
- **B=100**: Adequate for 5 tests but marginal.
- **All P-values > 0.05**: The test has very low power due to the formula issue (C2). The permutation null is so wide (null_std ≈ 20) that detecting significance would require ω_obs > 100 or < 5, which is an extreme threshold.

### 8.4 Brain Atlas

- **888,263 nuclei, 31,764 pairs**: Large dataset.
- **But P-values are invalid** (C1), so power analysis is moot.
- **30 Strong candidates from residual model**: No power analysis for the residual model is provided. The residual model's sensitivity (ability to detect true migration signals) is unknown.
- **OPC negative control (0 Strong signals)**: Provides some evidence of specificity, but without a formal power analysis, it's unclear whether the model would detect a true migration signal if one existed.

---

## 9. Recommendations

### Immediate (Required Before Submission)

1. **Fix the brain and human bootstrap**: Implement proper cell-level permutation tests for both datasets. This is the single most critical statistical issue. The current P-values are mathematically meaningless.

2. **Reconcile B value for brain**: Clarify whether B=100 or B=1000 was used. The results CSV appears to use B=1000, but the manuscript reports B=100.

3. **Revise the P-value formula or justify it more carefully**: Either switch to a one-sided test `P = count(ω_null ≥ ω_obs)/(B+1)` or provide a detailed statistical justification for why |ω−1| is the appropriate test statistic when the permutation null is centered far from 1.

4. **Apply FDR correction** to the brain analysis (once valid P-values are computed) or provide a permutation-based null for the residual model.

5. **Rename "Cohen's d"** to "permutation z-score" or "standardized deviation from null."

6. **Clarify CI reporting**: Distinguish between null distribution quantiles and parameter confidence intervals. Report proper bootstrap CIs for ω_obs where possible.

### Recommended (Strengthen the Analysis)

7. **Increase mouse calibration to n≥20**: The current n=6 is insufficient for robust calibration. Perform formal TOST equivalence testing.

8. **Compute partial correlations** between k_f and standard metrics, controlling for k_n, to address the spurious ratio correlation concern (v17 M2).

9. **Add residual threshold sensitivity analysis**: Show how the Strong candidate count changes with threshold (0.2, 0.25, 0.3, 0.35, 0.4).

10. **Implement permutation null for the residual model**: Permute region labels within each cell type and derive empirical P-values for each (cell_type, region_pair) combination.

11. **Address the HRT Atlas usage in mouse pilot**: The manuscript says `use_reference = False` for all datasets, but `02c_pilot_v2b.py` loads HK genes directly from the HRT Atlas file. Clarify whether the mouse pilot used HRT Atlas genes or data-driven detection.

### Documentation Fixes

12. **Fix the bootstrap B value discrepancy** for brain (manuscript says B=100, code uses B=1000).

13. **Use consistent terminology** for the test directionality (one-sided vs two-sided).

14. **Remove or clearly label** the invalid P-values in the supplementary brain and human bootstrap result tables.

---

## Appendix: Verification of Key Claims

### A1. "Bootstrap permutation testing was performed for all four datasets"

**Partially verified**: True for mouse (B=500) and TCGA (B=100). False for human and brain — these scripts perform bootstrap resampling of pre-computed ω values, not label permutation.

### A2. "P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1)/(B + 1)"

**Verified for mouse and TCGA only**. The brain and human scripts use `P = (sum(boot_means >= obs_mean) + 1)/(N + 1)`, which is a different formula.

### A3. "All reported P-values are raw empirical P-values without multiple testing correction"

**Verified**: No FDR correction is applied anywhere in the codebase. The limitation is acknowledged in the manuscript.

### A4. "The +1 pseudocount avoids P = 0"

**Verified**: The +1 is correctly implemented in `cki/bootstrap.py` (line 241) and `02c_pilot_v2b.py` (line 317).

### A5. "Cohen's d = (ω_obs − mean(ω_null)) / sd(ω_null)"

**Verified**: This is the formula used in `cki/bootstrap.py` (line 244) and `02c_pilot_v2b.py` (line 320). However, this is a permutation z-score, not a standard Cohen's d.
