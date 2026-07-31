# v18 Review: Statistical Methods Expert

## Overall Score: 3/10
## Readiness: 25%

## Summary

The CKI manuscript presents a heuristic transcriptomic divergence index (ω = k_f/k_n) validated across four datasets with bootstrap permutation testing (B=1000), Benjamini-Hochberg FDR correction, and non-parametric supplementary tests. While the conceptual framework is creative and the biological interpretations are engaging, the statistical implementation contains fundamental flaws that undermine the validity of the inferential claims.

The most critical problem is that the "bootstrap permutation test" described in the manuscript is not actually a permutation test for two of the four datasets. The human (08b) and brain (08c) analysis scripts resample pre-computed ω values with replacement (bootstrap resampling of the mean) rather than permuting cell labels. This is a fundamentally different statistical procedure. The P-value formula P = (count(|boot_mean − 1| ≥ |obs_mean − 1|) + 1)/(B + 1) is meaningless in this context because the bootstrap means are centered around the observed mean, not around ω = 1. Consequently, all human and brain bootstrap P-values cluster near 0.5, yielding zero statistical power. The TCGA bootstrap, which does use cell-level permutation, produces ω = 0.0000 for all five cancer types (kn = 0, kf = 0), indicating a computational failure that renders the P-values meaningless. Only the mouse pilot (15 pairs) uses the permutation test correctly and produces sensible results.

Beyond the bootstrap issues, the manuscript contains a critical internal contradiction regarding the calibration mean (6.67 in the Abstract/Results vs. 1.54 in the Statistical Reporting/Discussion/Limitations sections), a three-way contradiction on whether BH FDR correction was applied (manuscript says yes, Reproducibility Guide says no, code says yes), and a fabricated data point (Microglia DTg vs. SN claimed as "the single strongest signal, residual = 0.132" when the actual data shows this pair has residual = 0.6459 and is classified as Weak, not Strong). These issues must be resolved before submission.

## Critical Issues (must fix before submission)

### [C1] The "bootstrap permutation test" for human and brain is NOT a permutation test — it has zero statistical power

**The problem:** The manuscript (Materials and Methods, Statistical Reporting) describes: "We randomly permute cell labels between the two populations (B = 1,000), recompute pseudobulk vectors, and calculate ω_null for each permutation." This is a standard permutation test. However, the actual analysis scripts for human (`08b_human_bootstrap_csv.py`) and brain (`08c_brain_bootstrap_csv.py`) do NOT permute cell labels. Instead, they:

1. Load pre-computed ω values from a CSV file (one ω per cell-type pair or region pair)
2. Resample these ω values **with replacement** (bootstrap resampling of the mean)
3. Compute P = (count(|boot_mean − 1| ≥ |obs_mean − 1|) + 1)/(B + 1)

This is a **bootstrap resampling of the mean**, not a permutation test. The fundamental difference:
- **Permutation test**: Shuffles cell labels to generate a null distribution under H₀ (populations are identical). The null ω values reflect what happens when the biological signal is destroyed.
- **Bootstrap resampling**: Resamples observed ω values to estimate the sampling distribution of the mean. The bootstrap means are centered around the observed mean, NOT around the null.

**Consequence:** The P-value formula tests whether |bootstrap_mean − 1| ≥ |observed_mean − 1|. Since bootstrap means are drawn from the observed ω distribution, they are centered around obs_mean. When obs_mean >> 1 (e.g., brain astrocyte mean ω = 14.36), both |boot_mean − 1| and |obs_mean − 1| are large and similar, so ~50% of bootstrap means exceed the observed deviation. This is why **all brain P-values are 0.477–0.520 and all human P-values are 0.500–0.504** — the test has literally zero power.

**Evidence from CSV files:**
- `brain_bootstrap_results.csv`: All 10 p_values range from 0.477 to 0.520 (all non-significant)
- `human_bootstrap_results.csv`: All 4 p_values range from 0.500 to 0.504 (all non-significant)

**Fix:** Either (a) implement a true cell-level permutation test (as the `bootstrap_test()` function in `cki/bootstrap.py` already does) for all datasets, or (b) explicitly acknowledge that the human and brain analyses use bootstrap CIs for the mean rather than significance testing, and remove all P-value claims for these datasets.

---

### [C2] TCGA bootstrap results show ω = 0.0000 for all five cancer types — the computation has failed

**The problem:** The `tcga_bootstrap_results.csv` file shows:

| Cancer | ω | k_n | k_f | P-value |
|--------|---|-----|-----|---------|
| LUAD | 0.0000 | 0.000000 | 0.000000 | 0.032 |
| LUSC | 0.0000 | 0.000000 | 0.000000 | 0.123 |
| LIHC | 0.0000 | 0.000000 | 0.000000 | 0.306 |
| KIRC | 0.0000 | 0.000000 | 0.000000 | 0.785 |
| BRCA | 0.0000 | 0.000000 | 0.000000 | 0.699 |

All ω = 0, all k_n = 0, all k_f = 0. The JS divergences are exactly zero, meaning the tumor and normal pseudobulk vectors are identical after normalization. This happens because the TCGA bootstrap (`08a_tcga_bootstrap.py`) pools **all** tumor samples vs **all** normal samples (e.g., 495 tumors vs 76 normals for LUAD) and computes a single pseudobulk for each group. With hundreds of samples averaged together, the pseudobulk profiles converge, and both k_n and k_f approach zero.

**Why this matters:** The P-values in this table (0.032–0.785) are meaningless because they test deviations of ω = 0 from the null, not deviations of meaningful ω values. The manuscript's TCGA results discuss pairwise comparisons (TT, NN, TN) with meaningful ω values (e.g., "median NN/TT ω ratio exceeded 1.0"), but the bootstrap tests a completely different hypothesis (pooled tumor vs. normal). The bootstrap P-values are therefore disconnected from the biological claims.

**Additional inconsistency:** The TCGA script uses `log2(maximum(expr, 0) + 1)` (line 192) and filters genes with `mean TPM >= 0.5` (line 186), while the Reproducibility Guide states `log2(TPM + 0.001)` and `mean expression > 1 TPM`. These preprocessing differences may contribute to the ω = 0 result.

**Fix:** Redesign the TCGA bootstrap to test the actual hypotheses of interest (e.g., bootstrap the NN/TT ω ratio, or permute sample labels within paired tumor-normal groups). Do not report P-values from the current broken implementation.

---

### [C3] Calibration mean ω contradiction: 6.67 vs. 1.54

**The problem:** The manuscript reports two different calibration means for the same experiment:

| Location | Reported value |
|----------|---------------|
| Abstract | mean ω = 6.67 |
| Results (Calibration) | "The mean ω was 6.67 (median 6.46, range 1.59–12.16)" |
| Statistical Reporting | "The empirical calibration mean of ω = 1.54 for split-half equivalent populations" |
| Discussion | "mean observational ω = 1.54 for equivalent populations" |
| Limitations | "the calibration controls (random split of the same population, mean ω = 1.54)" |

**Data verification from `mouse_pilot_v2_results.csv`:** The 6 C_control ω values are: 12.161, 6.573, 6.338, 5.224, 8.148, 1.594. Mean = 6.672 ≈ **6.67** ✓. Median = 6.455 ≈ **6.46** ✓. Range = 1.594–12.161 ≈ **1.59–12.16** ✓.

The value **1.54 does not appear anywhere in the data**. The closest value is 1.594 (the neutrophil control), which rounds to 1.59, not 1.54. The value 1.54 appears to be fabricated or carried over from an earlier analysis version.

**Why this matters:** The 1.54 value is used in the Statistical Reporting section to justify using ω = 1 as the P-value anchor: "The empirical calibration mean of ω = 1.54... reflects residual measurement noise... using 1.54 as the anchor would conflate technical noise with the biological null." If the true calibration mean is 6.67 (54% higher than 1.54), this argument is substantially weakened — the gap between the theoretical null (1.0) and the empirical null (6.67) is much larger than implied.

**Fix:** Correct all instances of 1.54 to 6.67 throughout the manuscript. Re-evaluate whether the P-value anchor justification still holds with the correct value.

---

### [C4] Three-way contradiction on whether BH FDR correction was applied

**The problem:** The manuscript, Supplementary Materials, and Reproducibility Guide give contradictory statements:

| Source | Statement |
|--------|-----------|
| Manuscript (Methods, Statistical Reporting) | "Benjamini-Hochberg FDR correction is applied within each dataset" |
| Supplementary Note 3.3 | "Benjamini-Hochberg FDR correction is applied to the bootstrap P-values, and candidates passing FDR < 0.05 are reported as significant discoveries" |
| Reproducibility Guide §5.2 | "Multiple testing correction (Benjamini-Hochberg FDR) is NOT systematically applied in the current analyses: all reported P-values and significance thresholds use raw (uncorrected) bootstrap P-values" |
| Reproducibility Guide Checklist | "Note: FDR correction is not applied in the current analyses; all reported P-values are raw bootstrap P-values." |

**Code verification:** I examined all three bootstrap scripts:
- `08a_tcga_bootstrap.py` (line 265): `q_vals = benjamini_hochberg(p_numeric)` ✓
- `08b_human_bootstrap_csv.py` (line 130): `q_vals = benjamini_hochberg(p_numeric)` ✓
- `08c_brain_bootstrap_csv.py` (line 83): `df_out["q_value"] = benjamini_hochberg(df_out["p_value"].values)` ✓

All three scripts DO apply BH FDR correction, and all four CSV files contain a `q_value` column. The Reproducibility Guide is factually wrong.

**I verified the BH implementation** in `cki/bootstrap.py` (lines 18–64) against all four CSV files:
- Mouse pilot (15 P-values): All 15 q_values match the BH formula exactly ✓
- TCGA (5 P-values): All 5 q_values match ✓
- Brain (10 P-values): All 10 q_values match (all = 0.5205 after monotonicity enforcement) ✓
- Human (4 P-values): All 4 q_values match ✓

The BH implementation itself is correct. The problem is the documentation contradiction.

**Additional issue:** The Manuscript Limitations section says "the 31,764 brain cross-region comparisons yielded 30 Strong candidates **without formal multiple testing correction**" — but the Supplementary Note says BH FDR IS applied, and the code confirms it. These cannot both be true. In reality, BH FDR was applied to the 10 cell-type-level bootstrap P-values (all q > 0.52), but the 30 Strong candidates were identified by the multiplicative residual model (a completely separate analysis that has no P-values and no FDR correction). The manuscript conflates two different analyses.

**Fix:** (a) Correct the Reproducibility Guide to state that BH FDR is applied. (b) Clarify that the 30 Strong brain candidates come from the multiplicative residual model, not from bootstrap testing, and that no multiple testing correction was applied to the residual model. (c) Remove the contradictory Supplementary Note 3.3 claim that "candidates passing FDR < 0.05 are reported as significant discoveries" — no candidate passes FDR < 0.05 (all q > 0.52).

---

### [C5] Fabricated data point: Microglia DTg vs. SN claimed as "single strongest signal (residual = 0.132)"

**The problem:** The manuscript states (Results, Microglia section): "DTg (dorsal tegmental nucleus) vs. SN (substantia nigra), the single strongest signal (residual = 0.132), lies entirely within the mesencephalon."

**Data verification from `brain_siletti_migration_candidates_v3.csv`:**
- Microglia, DTg, SN: omega = 4.125, expected_omega = 6.39, residual = **0.6459**, tier = **Weak**
- No entry in the entire 31,764-row dataset has a residual of 0.132 (searched range 0.125–0.135: zero matches)
- The actual strongest Microglia signal is: Microglia, DTg, **TF** (not SN), residual = **0.2465**
- The actual strongest overall signal is: Astrocyte, VLN, VPL, residual = **0.2021**

The manuscript's claim is wrong on three counts:
1. DTg vs. SN is NOT a Strong candidate (it's Weak)
2. The residual is 0.6459, not 0.132
3. It is not the strongest signal — the strongest is Astrocyte VLN vs. VPL (residual = 0.2021)

**Fix:** Correct this passage. The strongest Microglia signal is DTg vs. TF (residual = 0.2465). If the intent was to highlight a DTg pairing, use the correct partner (TF) and residual (0.2465). Remove the residual = 0.132 claim entirely.

---

### [C6] The P-value anchor at ω = 1 is invalid given the empirical null at ω ≈ 6.67

**The problem:** The bootstrap test uses |ω − 1| as the test statistic, where ω = 1 is described as the "theoretical null" (k_f = k_n, zero functional divergence). However, the calibration data shows that biologically equivalent populations (random splits of the same cell type) yield mean ω = 6.67 (range 1.59–12.16). The permutation null distributions in the mouse pilot confirm this: null means range from 6.02 to 11.99 across the 6 control comparisons.

The manuscript argues: "using 1.54 [sic, should be 6.67] as the anchor would conflate technical noise with the biological null." This argument is circular — it acknowledges that the empirical null is shifted away from 1, but insists on using 1 as the anchor anyway.

**Consequences:**
1. **For the mouse pilot** (cell-level permutation): The test accidentally works because the permutation null distribution captures the empirical shift. When ω_obs is much larger than the null mean (e.g., ω_obs = 42.77 vs. null_mean = 7.27), |ω_obs − 1| > |ω_null − 1|, and the test correctly rejects. When ω_obs is close to the null mean (controls), |ω_obs − 1| ≈ |ω_null − 1|, and the test correctly fails to reject. The anchor at 1 doesn't matter because the permutation null is internally calibrated.

2. **For the brain and human** (CSV-based resampling): The test completely fails because the bootstrap means are centered around the observed mean, not around 1. The anchor at 1 is irrelevant — the test would give P ≈ 0.5 regardless of the anchor value.

3. **The test statistic |ω − 1| treats ω = 0 and ω = 2 identically**, which is inappropriate. A population with ω < 1 (functional constraint) and one with ω > 1 (functional divergence) are biologically different but would produce the same |ω − 1|.

**Fix:** For the permutation test (mouse pilot), use a standard test statistic: either ω_obs itself (one-sided) or (ω_obs − null_mean) / null_std (standardized). Do not use |ω − 1| as the test statistic. For the brain and human analyses, abandon the bootstrap P-value approach entirely and rely on effect sizes and CIs.

---

### [C7] The "1,588 expected false positives" calculation is misleading and conflates two different analyses

**The problem:** The manuscript states (Limitations): "the 31,764 brain cross-region comparisons yielded 30 Strong candidates without formal multiple testing correction; at a nominal alpha = 0.05, approximately 1,588 false positives would be expected among 31,764 tests."

**Arithmetic check:** 31,764 × 0.05 = 1,588.2 ✓ (calculation is correct)

**Why it's misleading:**
1. The 30 Strong candidates were NOT identified by significance testing at α = 0.05. They were identified by the multiplicative residual model (residual < 0.3, ω < 15, lowest ω in region pair). No P-values are involved in this selection. The "1,588 false positives" calculation is about a hypothetical significance testing scenario that was never performed.

2. The brain bootstrap test only has **10 P-values** (one per cell type), not 31,764. All 10 are non-significant (P = 0.48–0.52). The 31,764 comparisons were never individually tested.

3. The 31,764 cross-region comparisons are **not independent**. Many pairs share regions (e.g., A1C-A5 and A1C-A13 share A1C) and cell types, creating strong correlations. The effective number of independent tests is much smaller than 31,764. Methods like the Benjamini-Hochberg procedure or permutation-based FDR estimation would need to account for this dependence structure.

4. The manuscript says the 30 candidates "should be interpreted as hypothesis-generating signals requiring independent validation" — this is appropriate, but the "1,588 false positives" framing is still misleading because it implies a significance testing framework that doesn't apply.

**Fix:** Remove the "1,588 false positives" calculation or reframe it accurately: "The 30 Strong candidates were identified by the multiplicative residual model (residual < 0.3), not by significance testing. The 31,764 comparisons are not independent (they share regions and cell types), so simple FDR estimates are not applicable. These candidates should be interpreted as hypothesis-generating signals."

---

## Major Issues (should fix)

### [M1] B = 1,000 is insufficient for the claimed scope of testing

For the mouse pilot (15 tests) and the cell-type-level brain (10 tests) and human (4 tests) analyses, B = 1,000 gives a minimum P-value of 1/(B+1) = 1/1001 ≈ 0.001, which is adequate for these small-scale tests.

However, the manuscript repeatedly implies that 31,764 brain comparisons and 5,151 human comparisons were individually bootstrap-tested: "Bootstrap permutation testing was performed for all four datasets with B = 1,000: mouse pilot (15 cell-type pairs), human Tabula Sapiens, TCGA, and brain atlas." If 31,764 individual tests were performed with B = 1,000:
- Minimum achievable P-value: 1/1001 ≈ 0.001
- After BH correction for 31,764 tests: minimum q-value = 0.001 × 31764/1 = 31.764, capped at 1.0
- **No test could ever reach significance after BH correction**

In reality, only 10 brain-level and 4 human-level bootstrap tests were performed (not 31,764 and 5,151). The manuscript should clarify this. If pairwise testing is intended, B must be increased dramatically (B ≥ 100,000 for stable P-values at the 10⁻⁶ level needed after BH correction for 31,764 tests).

### [M2] Confidence intervals are inconsistently defined and mislabeled across datasets

The `bootstrap_test()` function in `cki/bootstrap.py` (lines 340–343) returns `ci_95` as the 2.5th and 97.5th percentiles of the **null distribution**. The Supplementary Note correctly states: "these are permutation-based test critical values for rejecting H₀, NOT confidence intervals for omega itself."

However:
1. **Naming**: The variable is called `ci_95` in code and `ci_95_lower`/`ci_95_upper` in CSV files, implying they are confidence intervals. They should be named `null_percentile_2.5` and `null_percentile_97.5` or `test_critical_lower`/`test_critical_upper`.

2. **Mouse pilot CSV**: Does not report ci_95 columns at all — reports `null_mean` and `null_std` instead. Inconsistent with other datasets.

3. **TCGA CSV**: Reports `ci_95_lower` and `ci_95_upper` as 0.0000 for all cancers (because the null distribution is all zeros, given ω = 0).

4. **Brain CSV**: Reports `ci_95_lower` and `ci_95_upper` that are actually **bootstrap CIs for the mean ω** (from resampling pairs), NOT null distribution percentiles. For Astrocyte: CI = [14.13, 14.57] around mean 14.36 — this is a tight CI for the mean, not a null distribution range.

5. **Human CSV**: Similarly reports bootstrap CIs for the mean, not null distribution percentiles.

The four datasets use three different CI definitions (null distribution percentiles for mouse/TCGA, bootstrap CIs for the mean for brain/human, and no CIs for the mouse CSV). This must be standardized.

### [M3] The multiplicative residual model for brain analysis has no statistical inference framework

The 30 "Strong" brain migration candidates are identified by the multiplicative residual model: residual = observed_ω / expected_ω, where expected_ω = μ_ct × μ_pair / μ_grand. The thresholds (Strong: < 0.3; Moderate: < 0.5; Weak: < 0.75) are arbitrary and have no statistical basis.

Key issues:
1. **No P-values**: The residual model produces no P-values, so the 30 "Strong" candidates have no statistical significance attached.
2. **No null model**: There is no formal null distribution for the residual. What would the residual look like under a null hypothesis of no developmental signature?
3. **Arbitrary thresholds**: The choice of 0.3, 0.5, 0.75 is not justified. How many candidates would be expected by chance at each threshold?
4. **No multiple testing correction**: 31,764 comparisons are filtered by residual thresholds without any FDR control.
5. **The "lowest ω in the region pair" criterion** for Strong is a post-hoc filtering step that further inflates the false positive rate without correction.

### [M4] Cohen's d uses population SD (ddof=0) instead of sample SD (ddof=1)

In `cki/bootstrap.py` line 334: `null_std = float(np.std(null_omega))`. NumPy's `np.std()` uses ddof=0 by default (population standard deviation), not ddof=1 (sample standard deviation). Cohen's d typically uses the sample standard deviation. With B = 1000, the difference is negligible (factor of sqrt(1000/999) ≈ 1.0005), but it should be documented and corrected for consistency with standard practice.

### [M5] The `bootstrap_test()` function in bootstrap.py is never called for human and brain datasets

The `bootstrap_test()` function (lines 108–368 of `cki/bootstrap.py`) implements a proper cell-level permutation test. It is only called in `08a_tcga_bootstrap.py` (where it produces ω = 0 due to the pooling issue). The human and brain scripts (`08b`, `08c`) bypass this function entirely and implement their own CSV-based resampling. This means:
1. The well-tested library function is not used for 2 of 4 datasets
2. The CSV-based approach has no cell-level permutation
3. The P-value formula from the library function is applied in a context where it's invalid

### [M6] Single random seed (42) limits generalizability assessment

All analyses use seed = 42. While this ensures reproducibility, it provides no assessment of result stability across different random seeds. For the bootstrap P-values, a sensitivity analysis with 3–5 different seeds should be performed to verify that:
1. P-values are stable (especially near significance thresholds)
2. The 30 Strong brain candidates are robust to seed choice
3. The mouse pilot calibration P-values remain > 0.05 across seeds

The manuscript does not mention this limitation.

---

## Minor Issues (nice to fix)

### [m1] The +1 pseudocount formula uses `len(null_omega)` instead of `n_bootstrap`

In `cki/bootstrap.py` line 332: `p_value = (np.sum(null_dists >= obs_dist) + 1) / (len(null_omega) + 1)`. If any null ω values are NaN (filtered out by the `if not np.isnan(r["omega"])` check on line 324), `len(null_omega)` will be less than `n_bootstrap`. The manuscript formula says (count + 1)/(B + 1), implying B is the denominator, not the actual number of valid null values. This is a minor discrepancy — using `len(null_omega)` is actually more correct, but the documentation should match the code.

### [m2] The BH docstring example is incorrect

The docstring for `benjamini_hochberg()` (line 39) states:
```
>>> q = benjamini_hochberg(p)
>>> print(q)  # [0.025, 0.0667, 0.05, 0.25, 0.005]
```
For input `[0.01, 0.04, 0.03, 0.20, 0.001]`:
- Sorted: [0.001, 0.01, 0.03, 0.04, 0.20]
- BH: [0.005, 0.0167, 0.05, 0.05, 0.20]
- After monotonicity: [0.005, 0.0167, 0.05, 0.05, 0.20]
- Unsorted: [0.0167, 0.05, 0.05, 0.20, 0.005]

The docstring output `[0.025, 0.0667, 0.05, 0.25, 0.005]` is wrong.

### [m3] omega capping at 1,000 is mentioned but never tested

Supplementary Note 1.1 states "omega is capped at 1,000." This is not discussed in the context of any results, and no ω values in the data approach this cap. The capping could mask extreme outliers and should be documented in the Methods if it has any effect.

### [m4] TCGA paired analysis sample sizes are too small for meaningful P-values

The manuscript acknowledges "the small number of patients with paired tumor and normal samples (n = 2–5 per cancer type) limits statistical power." With n = 2 paired samples, the two-sided Mann-Whitney U test has a minimum P-value of ~0.667 (cannot reach significance at α = 0.05). The reported P = 0.024 for LIHC likely comes from comparing paired ω values against a larger set of unpaired ω values, but this should be clarified. The manuscript should explicitly state which groups are being compared in the Mann-Whitney test.

### [m5] Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05 without correction

The manuscript states: "Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05 without additional correction." For the TCGA stratified analyses (BRCA PAM50: 5 groups; LIHC Edmondson: 4 grades; LUAD mutations: 3 groups), this is acceptable as each omnibus test is a single test. However, the manuscript should note that these are exploratory and that post-hoc pairwise comparisons (if performed) would require correction.

### [m6] The "all P < 0.001" claim for Spearman correlations is not verifiable from the provided CSV files

The manuscript states "CKI ω was negatively correlated with all four standard metrics (Spearman r = −0.38 to −0.57, all P < 0.001)." With n = 5,151 pairs, even r = −0.38 gives P < 10⁻²⁰⁰, so the claim is plausible. However, the actual correlation P-values are not reported in any CSV file, and the human bootstrap CSV only has 4 group-level P-values (all ≈ 0.5). The correlation analysis should be documented with its own output file.

### [m7] The `np.std` in the brain CSV script also uses ddof=0

In `08c_brain_bootstrap_csv.py` line 46: `obs_std = np.std(omegas)` uses ddof=0. The reported `omega_std` in the brain CSV is therefore the population SD, not the sample SD. This is inconsistent with standard statistical reporting conventions.

---

## Strengths

1. **BH FDR implementation is mathematically correct**: I verified the `benjamini_hochberg()` function against all four CSV files. Every q_value matches the BH formula exactly, including monotonicity enforcement and capping at 1.0. The implementation handles edge cases (n=0, n=1) correctly.

2. **Mouse pilot calibration is well-designed**: The 6 control comparisons (random splits of the same population) provide a legitimate negative control. The P-values (0.31–0.99) correctly fail to reject the null, and the ω values (1.59–12.16) honestly characterize the empirical null distribution. The increasing ω across biological distance categories (C → S → D → X) is biologically sensible.

3. **The +1 pseudocount formula is correctly implemented**: P = (count + 1)/(B + 1) ensures P > 0 and is a standard approach in permutation testing (Phipson & Smyth, 2010). The implementation in `bootstrap.py` is correct.

4. **The multiplicative residual model is conceptually sound**: Using μ_ct × μ_pair / μ_grand as an expected value is a reasonable two-way ANOVA-like decomposition. The idea of detecting cell-type/region-pair combinations with anomalously low ω is biologically motivated.

5. **All numerical claims about brain candidate counts are accurate**: 30 Strong (0.09%), 1,247 Moderate (3.93%), 6,567 Weak (20.67%) all match the data exactly. The top-5 strongest signals listed in Supplementary Table 4 match the CSV data precisely.

6. **Comprehensive data deposition**: The migration candidates CSV with all 31,764 rows and tier classifications enables full reproducibility of the brain analysis.

7. **Random seed is reported**: Seed = 42 is documented in both the manuscript and the Reproducibility Guide.

---

## Specific Recommendations

1. **Replace the CSV-based bootstrap with true cell-level permutation** for the human and brain datasets. The `bootstrap_test()` function in `cki/bootstrap.py` already implements this correctly. If computational cost is a concern, run it on a representative subset of pairs (e.g., 100 random pairs per cell type) rather than all 31,764.

2. **Fix the TCGA bootstrap**: The current implementation produces ω = 0 for all cancers. Redesign it to test the actual hypotheses (e.g., bootstrap the NN/TT ω ratio, or permute sample labels within paired groups). If the goal is to test whether tumors are more homogeneous than normals, bootstrap the NN/TT ratio directly.

3. **Correct the calibration mean from 1.54 to 6.67** in all manuscript sections (Statistical Reporting, Discussion, Limitations). Re-evaluate the P-value anchor justification — with the empirical null at 6.67, the gap from 1.0 is much larger than implied.

4. **Remove or correct the fabricated DTg vs. SN claim** (residual = 0.132). The correct strongest Microglia signal is DTg vs. TF (residual = 0.2465). The correct strongest overall signal is Astrocyte VLN vs. VPL (residual = 0.2021).

5. **Standardize CI reporting**: Use consistent CI definitions across all four datasets. If reporting bootstrap CIs for the mean, label them as such. If reporting null distribution percentiles, label them as test critical values. Do not mix the two.

6. **Add a formal statistical framework for the multiplicative residual model**: Define a null distribution for the residual (e.g., by permuting region labels within cell types), compute P-values, and apply FDR correction. Alternatively, explicitly state that the residual model is exploratory and that the 30 candidates are hypothesis-generating.

7. **Clarify the scope of bootstrap testing**: State explicitly that bootstrap testing was performed at the cell-type level (10 tests for brain, 4 tests for human, 5 for TCGA, 15 for mouse), NOT at the pair level (31,764 for brain, 5,151 for human). The current text implies pair-level testing.

8. **Correct the Reproducibility Guide**: Section 5.2 and the checklist incorrectly state that FDR is not applied. Update to reflect that BH FDR is applied in all bootstrap scripts.

9. **Run sensitivity analysis with multiple random seeds** (e.g., 42, 123, 456, 789, 2024) to assess robustness of the 30 Strong brain candidates and the mouse calibration P-values.

10. **Report effect sizes alongside all P-values**: The manuscript reports Cohen's d for some comparisons but not others. Standardize effect size reporting across all significance claims.

11. **Address the non-independence of brain comparisons**: The 31,764 cross-region pairs share regions and cell types, violating independence. Consider methods like the Benjamini-Hochberg procedure with dependence adjustment, or permutation-based FDR estimation that accounts for the correlation structure.

12. **Document the omega capping at 1,000**: If any ω values were capped, report how many and at what threshold. If no values were capped, state this explicitly.
