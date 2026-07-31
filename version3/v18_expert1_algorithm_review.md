# Expert Review 1: Algorithm & Methodology

**Reviewer**: Expert in computational biology algorithms and methodology
**Date**: 2026-07-27
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research (NAR)
**Files reviewed**: `generate_manuscript_nar.py` (manuscript text), `notebooks/68_gen_supplementary_en.py` (supplementary materials), `version3/v17_review_synthesis.md` (previous review context)

---

## 1. Overall Assessment

**Score: 6.5 / 10**

CKI proposes a conceptually interesting framework: decomposing transcriptomic divergence between two cell populations into a baseline component (k_n, from housekeeping genes) and a functional component (k_f, from identity genes), then taking the ratio ω = k_f/k_n. The Ka/Ks analogy, while heuristic, provides a productive conceptual lens. The validation across four datasets (mouse atlas, human atlas, TCGA, brain atlas) demonstrates breadth of application.

However, the algorithm description contains several gaps between the general pseudocode (Algorithm 1) and the actual implementation used for the human and brain analyses (the "hybrid scheme"). The pseudocode does not fully capture the computational pipeline as described in the Methods and Results sections. Key normalization choices (softmax on log1p-transformed data) are insufficiently justified. The multiplicative residual model for brain analysis, while creative, lacks a formal null distribution. The v17 fixes (C1, C2, C5, C7) have been applied and improve cross-document consistency, but several algorithmic concerns remain unaddressed.

The manuscript is publishable in NAR after addressing the issues below, particularly the Critical items regarding pseudocode completeness and the hybrid scheme description.

---

## 2. Strengths

1. **Conceptual novelty with honest caveats.** The idea of using housekeeping genes as an internal baseline reference — analogous to synonymous sites in Ka/Ks — is genuinely novel in the single-cell comparison field. The manuscript is commendably honest that CKI "does not share Ka/Ks's formal mathematical properties (notably the shared mutation rate that cancels in the ratio)" (manuscript line 354). This intellectual honesty is appropriate.

2. **Data-driven HK detection without external reference.** The decision to use `use_reference=False` (purely data-driven HK detection via combined detection-rate/CV criterion) across all datasets is methodologically sound. It avoids circularity and makes the method species-agnostic. The sensitivity analysis (r > 0.95 with alternative HK definitions) supports robustness.

3. **Calibration with control comparisons.** The six random-split controls on Tabula Muris (mean ω = 1.54, all P > 0.05) provide a basic sanity check. The monotonic increase of ω across biological distance categories (C < S < D < X) is convincing.

4. **Negative correlation with standard metrics.** The finding that CKI ω is negatively correlated with all four standard distance metrics (Spearman r = −0.42 to −0.73) while the standard metrics form a tight positive cluster (r = 0.85–0.97) is the strongest evidence that CKI captures an orthogonal information dimension. This is a compelling result.

5. **Parameter sweep justification.** The sweep testing identity-only (w_identity = 1.0) vs. pathway-enriched configurations, with the identity-only achieving optimal AUC (0.847), provides empirical justification for the default configuration. This pre-registration of the design choice before seeing downstream results is good practice.

6. **Open-source availability.** Code on GitHub (v0.3.1, MIT License) with Zenodo DOI deposition, fixed random seed (42), and analysis script index in supplementary materials supports reproducibility.

---

## 3. Weaknesses / Concerns

### Critical

**C1. Pseudocode (Algorithm 1) does not capture the hybrid scheme used for human and brain analyses.**

Algorithm 1 (supplementary lines 207–224) describes a single gene set I (fixed HVG set) used for both k_n and k_f. However, the actual human Tabula Sapiens and brain atlas analyses use a **hybrid scheme**: k_n is computed globally (shared HK gene set), while k_f uses **pairwise top-200 differentially expressed genes** selected per comparison (manuscript line 427, supplementary Algorithm 2 lines 236–243). Algorithm 1's bootstrap loop (line 13: `omega_null[b] <- CKI_core(A_perm, B_perm, H, I)`) passes a fixed I parameter, which does not reflect the pairwise gene re-selection that should occur in each permutation for the hybrid scheme.

This is a correctness concern: the pseudocode as written would not reproduce the human or brain results. A reader following Algorithm 1 literally would implement a global-HVG scheme, not the hybrid scheme. Algorithm 2 partially addresses the pairwise gene selection but does not integrate with Algorithm 1's bootstrap loop.

**Recommendation**: Either (a) add a third algorithm (Algorithm 3) that shows the complete hybrid pipeline including pairwise gene selection within the bootstrap loop, or (b) modify Algorithm 1's line 13 to indicate that I is re-selected per permutation when using the pairwise scheme, e.g., `I_perm <- select_identity_genes(A_perm, B_perm, H, N)` then `omega_null[b] <- CKI_core(A_perm, B_perm, H, I_perm)`.

---

**C2. Pseudocode line 4: "auto-detected normalization" is ambiguous and inconsistent with the manuscript text.**

Supplementary line 211: `k_n <- JS_divergence(norm(mu_A_H), norm(mu_B_H))  // auto-detected normalization`

The comment "auto-detected normalization" is unclear. The manuscript text (line 368) explicitly states "softmax normalization (p_i = exp(x_i) / Σ exp(x_j))". The pseudocode should state `softmax(mu_A_H)` or at minimum `softmax_normalize(mu_A_H)`, not the vague `norm()` with an "auto-detected" comment. Algorithm 2 (line 240) correctly uses `softmax()`, creating an internal inconsistency within the same supplementary document.

**Recommendation**: Replace `norm()` with `softmax()` in Algorithm 1 lines 4 and 6, and remove the "auto-detected normalization" comment.

---

**C3. The brain atlas uses a different normalization order than all other datasets, but this is not reflected in the pseudocode or adequately discussed.**

Manuscript line 380 (brain atlas Methods): "Pseudobulk vectors were computed as the mean of raw counts per group, then normalized using Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation **at the pseudobulk level**."

Manuscript line 366 (general Methods): "We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation. Pseudobulk vectors are computed by averaging expression across cells..."

Algorithm 1 line 1: "X_A, X_B <- library-normalize and log1p-transform A and B" (i.e., normalize → log1p → pseudobulk)

The brain atlas pipeline is: **raw counts → pseudobulk → normalize → log1p**, while the standard pipeline (and pseudocode) is: **raw counts → normalize → log1p → pseudobulk**. These are mathematically non-equivalent: averaging log-transformed values (standard pipeline) is not the same as log-transforming averaged values (brain pipeline). The mean of log1p(x) ≠ log1p(mean(x)).

This difference affects the input to softmax normalization and thus the JS divergence values. The pseudocode only describes the standard pipeline. The brain analysis, which constitutes the most complex application of CKI (31,764 comparisons, multiplicative residual model), uses a non-standard normalization order that is not captured algorithmically.

**Recommendation**: Add a note in the pseudocode or supplementary methods explicitly stating that the brain atlas uses pseudobulk-level normalization (normalize after aggregation) while other datasets use cell-level normalization (normalize before aggregation). Discuss why this difference exists and whether it affects ω comparability across datasets.

---

**C4. The pseudocode does not handle the k_n = 0 edge case (division by zero).**

Algorithm 1 line 7: `omega <- k_f / k_n  // capped at 1,000`

If k_n = 0 (i.e., the two populations have identical HK gene probability distributions after softmax), the division is undefined. The "capped at 1,000" comment suggests a cap is applied, but the logic is not shown. In practice, with continuous softmax-normalized vectors, exact zero JS divergence is unlikely but possible (e.g., when two pseudobulk vectors are identical after normalization). The manuscript does not discuss this edge case.

**Recommendation**: Add a line in the pseudocode: `if k_n == 0: omega <- 1000 (or NaN with special handling)`. Discuss in the Methods how many comparisons (if any) hit this cap or the k_n = 0 case.

---

### Major

**M1. Softmax normalization on log1p-transformed data is not formally justified.**

The manuscript applies softmax normalization (p_i = exp(x_i) / Σ exp(x_j)) to pseudobulk vectors that have been log1p-transformed. This means the effective computation is: p_i = exp(log1p(x_i)) / Σ exp(log1p(x_j)) = (x_i + 1) / Σ (x_j + 1), which simplifies to a shifted L1 normalization, not a true softmax. This is because exp(log1p(x)) = x + 1 for x ≥ 0.

Wait — actually, this depends on whether the pseudobulk values are on the log1p scale or the raw normalized count scale when softmax is applied. The manuscript text (line 366–368) suggests: normalize → log1p → pseudobulk → softmax. So the input to softmax is log1p(normalized_count_averages), and the softmax is applied to these log-scale values: p_i = exp(log1p(μ_i)) / Σ exp(log1p(μ_j)) = (μ_i + 1) / Σ (μ_j + 1).

This is mathematically equivalent to shifted L1 normalization (adding 1 pseudocount to each gene then normalizing to sum 1). This is a reasonable choice (it prevents zero-probability issues), but it is NOT what most readers would understand "softmax normalization" to mean in a machine learning context (where softmax is applied to raw logits, not log-transformed counts).

The manuscript should either (a) clarify that "softmax on log1p values" is equivalent to "shifted L1 normalization with pseudocount 1" and discuss why this specific normalization is preferred, or (b) provide a sensitivity analysis comparing softmax on log1p vs. softmax on raw normalized counts vs. simple L1 normalization.

**M2. The HVG selection bias argument has a logical gap.**

Discussion line 506: "the calibration controls (random split of the same population, mean ω = 1.54) demonstrate that HVG selection alone does not inflate ω — when two populations are biologically equivalent, k_f and k_n are comparably small, yielding ω ≈ 1."

This argument tests whether HVG selection inflates ω **for equivalent populations**, but it does not test whether HVG selection inflates k_f **relative to a random gene set of the same size** for non-equivalent populations. HVGs are, by definition, genes that vary across cell types. Selecting them for k_f ensures that k_f measures divergence on genes that are known to vary. This is a tautological bias: k_f is computed on genes pre-selected to be variable, so it will tend to be larger than k_n (computed on HK genes pre-selected to be stable).

The calibration shows ω ≈ 1.54 for equivalent populations, which is already > 1 — suggesting that even for equivalent populations, k_f is slightly larger than k_n. This is consistent with HVG selection bias: even when two random splits are biologically equivalent, the HVGs (selected based on variation across all cell types in the dataset) may show slightly more divergence than HK genes between the two splits.

The manuscript should acknowledge this more explicitly and ideally provide a control: compare k_f(HVG) vs. k_f(random 2000 genes) for the same population pairs.

**M3. The multiplicative residual model thresholds lack formal statistical grounding.**

Manuscript line 386: "Strong (residual < 0.3, ω < 15, lowest ω in the region pair), Moderate (residual < 0.5, ω < 25), Weak (residual < 0.75, ω < 35)."

These thresholds are purely empirical. The manuscript provides no permutation-based null distribution for the residuals, no FDR control, and no sensitivity analysis for threshold choice. The v17 review noted this (M6), and the manuscript now acknowledges (line 514): "the 31,764 brain cross-region comparisons yielded 30 Strong candidates without formal multiple testing correction; at a nominal alpha = 0.05, approximately 1,588 false positives would be expected."

However, the manuscript then proceeds to interpret all 30 signals biologically (lines 470–495), assigning each to one of four mechanisms (DO, CR, DS, PM). This level of interpretation exceeds what "hypothesis-generating" signals warrant. The OPC negative control (0 Strong signals despite being the most motile cell type) is a compelling specificity argument, but it does not substitute for formal statistical control.

**Recommendation**: Either (a) perform a permutation test for the residual model (shuffle region labels within cell types, recompute residuals, estimate FDR), or (b) present the 30 signals as exploratory findings without mechanism assignment, deferring biological interpretation to a follow-up study.

**M4. The P-value formula's two-sided absolute deviation test may be suboptimal for directional hypotheses.**

Manuscript line 371: `P = (count(|ω_null − 1| ≥ |ω_obs − 1|) + 1)/(B + 1)`

This tests absolute deviation from ω = 1, treating ω > 1 (enhanced divergence) and ω < 1 (functional constraint) as equally interesting deviations. However, the manuscript's biological interpretation is inherently directional: ω > 1 indicates "selective transcriptomic remodeling" (the paper's title), while ω < 1 indicates "functional constraint" (rare in practice). A one-sided test (count(ω_null − 1 ≥ ω_obs − 1) for ω_obs > 1, or count(1 − ω_null ≥ 1 − ω_obs) for ω_obs < 1) would provide more power for the directional hypotheses the manuscript actually tests.

**Recommendation**: Justify the two-sided test or switch to one-sided tests for directional hypotheses.

**M5. The ω cap at 1,000 is mentioned but never analyzed.**

Supplementary line 99: "in practice omega is capped at 1,000." Algorithm 1 line 7: `omega <- k_f / k_n  // capped at 1,000`.

The manuscript does not report what fraction of comparisons hit this cap, what the maximum uncapped ω values are, or how results change with/without the cap. For the TCGA analysis, where ω values reach 344.5 (BRCA Luminal A, line 445), the cap is not binding. But for brain analysis with 31,764 comparisons, some pairs may have very small k_n values that produce extreme ω. The cap could mask important outliers or distort the multiplicative residual model.

**Recommendation**: Report the fraction of comparisons hitting the cap in each dataset. Perform a sensitivity analysis with cap = 10,000 or no cap.

---

### Minor

**m1. Symbol inconsistency between manuscript and pseudocode.**
Manuscript line 368 uses ε (epsilon) for pseudobulk vectors: "pseudobulk vectors ε_A and ε_B." Supplementary Note 1.2 (line 108) uses μ (mu): "pseudobulk vectors μ_A and μ_B." Algorithm 1 (line 209) also uses μ. The manuscript should use one symbol consistently.

**m2. Pseudocode line 9 notation is unclear.**
`labels <- concatenate([A]*n_A, [B]*n_B)` — This notation mixes label values (A, B) with cell counts (n_A, n_B). A clearer formulation: `labels <- [A]*n_A + [B]*n_B` (list replication and concatenation), or `labels <- rep('A', n_A) + rep('B', n_B)` (R-style notation).

**m3. Pseudocode line 16 references ω instead of ω_obs.**
`d <- (omega - mean(omega_null)) / sd(omega_null)` — should be `d <- (omega_obs - mean(omega_null)) / sd(omega_null)` for clarity, since the variable was named `omega` in line 7 but the observed value should be distinguished from null values.

**m4. The "combined criterion" for HK detection needs a clearer definition of "well-expressed genes."**
Manuscript line 366: "coefficient of variation below the 30th percentile among well-expressed genes (mean expression > 0.5)." The threshold "mean expression > 0.5" is on what scale? Log1p-normalized? Raw normalized counts? This affects reproducibility.

**m5. The B=100 for TCGA and brain is very low for stable P-value estimation.**
With B=100, the minimum achievable P-value is 1/101 ≈ 0.0099. For the brain atlas with 31,764 comparisons, this is insufficient resolution. The manuscript acknowledges this (line 371: "bootstrap iterations were computationally limited") and supplements with non-parametric tests, which is appropriate. However, the supplementary (line 174–176) mentions "test critical values at alpha=0.05 are derived from the permutation null distribution (2.5th and 97.5th percentiles)" — with B=100, the 2.5th and 97.5th percentiles are estimated from only 2–3 data points, which is unreliable.

**m6. The "same metric (JS divergence)" claim needs qualification.**
Manuscript line 405: "all of which use the same metric (Jensen-Shannon divergence) on the same underlying expression matrix, ensuring the ratio is internally calibrated." This is true for the mouse analysis (global HVG for k_f), but NOT true for the human/brain analyses where k_f uses pairwise DE genes (different gene sets per comparison). The "same underlying expression matrix" claim is weakened when the gene subsets differ.

**m7. Algorithm 2 is incomplete — it shows gene selection but not the full computation.**
Algorithm 2 (supplementary lines 236–243) shows how to select identity genes (pairwise top-N by |Δ|), but it does not show the complete k_f computation including normalization. It also does not specify how k_n is computed in the hybrid scheme (the note says "k_n uses the global HK set" but does not show the computation).

**m8. The random seed is fixed at 42, but the manuscript does not specify the random number generator.**
Manuscript line 392: "All random seeds were fixed at 42." Different RNG implementations (numpy's MT19937 vs. Python's built-in random) produce different permutation sequences. Specifying `numpy.random.seed(42)` or `random.seed(42)` would improve reproducibility.

---

## 4. Algorithm-Specific Comments (Line-Level)

### Algorithm 1 (Supplementary Note 2, lines 207–224)

| Line | Pseudocode | Comment |
|------|-----------|---------|
| 1 | `X_A, X_B <- library-normalize and log1p-transform A and B` | Does not reflect brain pipeline (pseudobulk-level normalization). See C3. |
| 2 | `mu_A <- mean(X_A, axis=0); mu_B <- mean(X_B, axis=0)` | Correct for standard pipeline. Should note minimum cell count (≥10). |
| 3 | `mu_A_H <- mu_A[H]; mu_B_H <- mu_B[H]` | Correct gene subsetting. |
| 4 | `k_n <- JS_divergence(norm(mu_A_H), norm(mu_B_H))` | `norm()` should be `softmax()`. See C2. |
| 5 | `mu_A_I <- mu_A[I]; mu_B_I <- mu_B[I]` | Correct, but I is undefined for the hybrid scheme. See C1. |
| 6 | `k_f <- JS_divergence(norm(mu_A_I), norm(mu_B_I))` | Same `norm()` issue. |
| 7 | `omega <- k_f / k_n  // capped at 1,000` | No k_n = 0 handling. See C4. Cap rationale missing. See M5. |
| 9 | `labels <- concatenate([A]*n_A, [B]*n_B)` | Unclear notation. See m2. |
| 10 | `for b = 1 to B (B = 500 for main mouse; 1,000 for human; 100 for TCGA and brain)` | B values are now consistent with manuscript text. v17 C1/C5 fix verified. |
| 13 | `omega_null[b] <- CKI_core(A_perm, B_perm, H, I)` | Does not re-select I for hybrid scheme. See C1. |
| 15 | `P <- (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)` | Two-sided test; directional alternative not considered. See M4. v17 C7 fix (ω=1 anchoring) is explained in manuscript line 395. |
| 16 | `d <- (omega - mean(omega_null)) / sd(omega_null)` | Should use `omega_obs`. See m3. |

### Algorithm 2 (Supplementary Note 2, lines 236–243)

| Line | Pseudocode | Comment |
|------|-----------|---------|
| 1 | `Delta <- |mu_A - mu_B|` | Correct absolute difference. |
| 2 | `I <- indices of top-N genes ranked by descending Delta, excluding H` | Correct pairwise selection. N=200 for human/brain. |
| 3 | `k_f <- JS(softmax(mu_A[I]), softmax(mu_B[I]))` | Uses `softmax()` correctly (contrast with Algorithm 1's `norm()`). |
| — | `Note: k_n uses the global HK set (same for all pairs); k_f uses pairwise top-N genes.` | This note is critical but insufficient — it does not describe how k_n is computed or how the bootstrap integrates with pairwise selection. See C1, m7. |

### Manuscript Methods (lines 365–396)

| Lines | Section | Comment |
|-------|---------|---------|
| 366 | HK detection criterion | "well-expressed genes (mean expression > 0.5)" — scale unclear. See m4. |
| 368 | Softmax normalization | Clear description, but does not justify why softmax on log1p data. See M1. |
| 371 | Bootstrap P-value formula | Consistent with supplementary. v17 C7 fix applied: ω=1 as theoretical null, ω=1.54 as empirical calibration, explanation provided. |
| 380 | Brain atlas normalization | Pseudobulk-level normalization differs from standard. See C3. |
| 386 | Multiplicative residual thresholds | Empirical, no null distribution. See M3. |
| 395 | P-value anchoring explanation | v17 C7 fix: "The P-value is anchored at the theoretical null of ω = 1... using 1.54 as the anchor would conflate technical noise with the biological null." This is a reasonable defense, though the tension remains. |

---

## 5. Novelty Evaluation

### What is genuinely novel

1. **The core concept of baseline-normalized functional divergence for transcriptomics.** Using housekeeping genes as an internal baseline reference (analogous to synonymous sites in Ka/Ks) is a new conceptual contribution to single-cell comparison. While the individual components (JS divergence, HK gene detection, pseudobulk aggregation) are all standard, their combination into a ratio ω = k_f/k_n is novel.

2. **The multiplicative residual model for brain regional analysis.** The model `expected_ω = μ_ct × μ_pair / μ_grand` with residual = observed/expected is a creative approach to detecting cell-type/region-pair combinations with anomalously low divergence. The four-mechanism classification framework (DO, CR, DS, PM) and the OPC negative control are thoughtful design elements.

3. **The negative correlation with standard metrics.** The finding that CKI ω is negatively correlated with all standard distance metrics (while they form a tight positive cluster) is a striking empirical result that suggests CKI captures genuinely different information.

### What is not novel

1. **Individual computational components.** Pseudobulk aggregation, JS divergence, softmax normalization, HVG selection (Seurat flavor), and bootstrap permutation testing are all standard techniques. CKI's novelty lies in their specific combination, not in any individual technique.

2. **The Ka/Ks analogy itself.** The analogy is acknowledged as heuristic, and the manuscript is careful to state that CKI "does not share Ka/Ks's formal mathematical properties." The analogy is productive conceptually but does not constitute a formal theoretical contribution.

### Comparison to existing methods

| Method | Relationship to CKI |
|--------|---------------------|
| Standard distance metrics (Euclidean, cosine, JS, Spearman) | CKI normalizes by baseline; standard metrics do not. Negative correlation demonstrates orthogonality. |
| Harmony, scVI, SATURN | These are batch-correction/integration tools, not divergence metrics. CKI operates after correction, asking "how different are these populations?" |
| SAMap, CACIMAR | Cross-species alignment/conservation tools. CKI is complementary — it could be applied within or across species. |
| Differential expression (DESeq2, etc.) | DE methods identify per-gene differences; CKI aggregates over gene sets to produce a single divergence index. |
| Cell-type identity tools (CellTypist, etc.) | Classification tools; CKI is explicitly "not a classifier" (Discussion line 504). |

**Novelty assessment**: The core idea is genuinely novel and the validation is broad. The main concern is whether the novelty is sufficient for NAR's Methods section, which typically expects formal theoretical contributions. CKI is a pragmatic heuristic rather than a theoretically grounded method. The manuscript acknowledges this honestly, but reviewers may question whether the analogy to Ka/Ks is deep enough to warrant a Methods paper in a high-impact journal.

---

## 6. Reproducibility Assessment

### Strengths

1. **Code availability**: GitHub repository (v0.3.1, MIT License) with Zenodo DOI (10.5281/zenodo.15670808).
2. **Data availability**: All datasets are public (GEO, CZ CELLxGENE, GDC, cBioPortal).
3. **Analysis scripts indexed**: Supplementary Data 1 lists key scripts with paths.
4. **Random seed fixed**: Seed = 42 (manuscript line 392).
5. **Parameter sweep data**: results/phase32_sweep_results.csv is referenced.
6. **v17 consistency fixes applied**: B values, HRT Atlas status, and P-value anchoring are now consistent across manuscript and supplementary.

### Weaknesses

1. **Pseudocode does not fully reproduce the pipeline.** As noted in C1 and C3, Algorithm 1 does not capture the hybrid scheme or the brain-specific normalization order. A reimplementer following the pseudocode would produce different results for human and brain analyses.

2. **The "combined criterion" for HK detection has ambiguous thresholds.** "Mean expression > 0.5" (line 366) does not specify the scale. "CV below the 30th percentile" is relative to "well-expressed genes" — the definition of which is circular (depends on the mean expression threshold, which depends on the scale).

3. **The hybrid scheme's pairwise gene selection is underspecified.** Algorithm 2 shows `Delta <- |mu_A - mu_B|` but does not specify whether this is computed on log1p-normalized pseudobulk values or raw values. It also does not specify whether the top-200 selection uses the absolute difference, the squared difference, or another ranking criterion.

4. **No containerized environment.** The manuscript specifies Python 3.13.12 and package version minimums, but does not provide a Docker/Singularity container or conda environment file. Python version sensitivity is not discussed.

5. **The multiplicative residual model implementation is not shown in pseudocode.** The formula (expected_ω = μ_ct × μ_pair / μ_grand) is described in prose (line 386) but not in pseudocode. The thresholding logic (Strong/Moderate/Weak tiers) is also only in prose.

6. **Processed data files referenced but not deposited.** Supplementary Table 3 references `results/brain_siletti_omega_pairs_v3.csv` and Supplementary Table 4 references `results/brain_siletti_migration_candidates_v3.csv`, but these processed files are not confirmed to be in the supplementary materials or Zenodo deposit.

**Reproducibility score**: 6/10. The raw materials (code, data, seeds) are available, but the algorithmic description has gaps that would make independent reimplementation difficult without reading the source code directly.

---

## 7. Recommendations for Improvement

### Must-fix before submission (Critical)

1. **Unify the pseudocode with the actual implementation.** Create a single, complete algorithm description that covers both the global-HVG scheme (mouse) and the hybrid scheme (human/brain). Show how pairwise gene selection integrates with the bootstrap loop. (Addresses C1)

2. **Replace `norm()` with `softmax()` in Algorithm 1.** Remove the "auto-detected normalization" comment. Ensure both algorithms use consistent terminology. (Addresses C2)

3. **Explicitly document the brain atlas normalization order.** Add a note that the brain pipeline normalizes after pseudobulk aggregation (unlike the standard pipeline), and discuss whether this affects ω comparability. (Addresses C3)

4. **Add k_n = 0 edge case handling to the pseudocode.** Report how many comparisons hit the ω = 1,000 cap in each dataset. (Addresses C4, M5)

### Strongly recommended (Major)

5. **Justify or clarify the softmax-on-log1p normalization.** Explain that softmax on log1p values is equivalent to shifted L1 normalization, or provide a sensitivity analysis comparing normalizations. (Addresses M1)

6. **Address the HVG selection bias more rigorously.** Provide a control comparing k_f(HVG) vs. k_f(random gene set) for the same population pairs. (Addresses M2)

7. **Add formal statistical control to the multiplicative residual model.** Perform a permutation test (shuffle region labels within cell types) to estimate the null distribution of residuals and compute FDR. At minimum, present the 30 Strong signals as explicitly exploratory. (Addresses M3)

8. **Justify the two-sided P-value test or switch to one-sided.** (Addresses M4)

### Recommended improvements (Minor)

9. **Fix symbol inconsistency** (ε vs μ for pseudobulk vectors). (Addresses m1)
10. **Clarify pseudocode notation** in lines 9 and 16. (Addresses m2, m3)
11. **Specify the scale for the HK detection threshold** ("mean expression > 0.5"). (Addresses m4)
12. **Note the limitations of B=100** for stable percentile estimation. (Addresses m5)
13. **Qualify the "same metric" claim** for the hybrid scheme. (Addresses m6)
14. **Complete Algorithm 2** to show the full k_f computation and k_n reference. (Addresses m7)
15. **Specify the RNG implementation** (e.g., `numpy.random.seed(42)`). (Addresses m8)

### Long-term improvements

16. **Develop a formal theoretical framework.** The manuscript acknowledges CKI lacks Ka/Ks's formal mutation-rate cancellation. Future work could explore whether an Ornstein-Uhlenbeck process or other stochastic model could provide a theoretical grounding for ω.

17. **Single-cell extension.** The pseudobulk limitation (Discussion line 514) is significant. A single-cell version of CKI that handles sparsity and dropout would substantially increase the method's impact.

18. **Cross-species validation.** The manuscript mentions SAMap and SATURN but does not test CKI on cross-species comparisons. Given the Ka/Ks inspiration, this is a natural next step.

---

## Summary

CKI is a creative and well-validated heuristic method with a clear conceptual contribution. The v17 fixes (B values, HRT Atlas, P-value anchoring) have improved cross-document consistency. The remaining algorithmic concerns center on: (1) the gap between the pseudocode and the actual hybrid scheme implementation, (2) insufficient justification of normalization choices, and (3) the lack of formal statistical control for the brain residual model. These are addressable issues that do not undermine the core contribution but must be resolved before the manuscript is suitable for NAR publication.
