# Expert Review #1: Methods & Algorithms

## Overall Assessment
CKI presents a conceptually elegant framework for decomposing transcriptomic divergence into baseline (k_n) and functional (k_f) components, inspired by the Ka/Ks ratio in molecular evolution. The core idea—using housekeeping genes as an internal normalization baseline—is creative and addresses a genuine gap in single-cell comparative analysis. However, the manuscript suffers from several foundational mathematical and interpretational issues that prevent the current formulation from achieving its stated goals. The calibration results (mean ω = 6.67 for identical populations) fundamentally undermine the ω ≈ 1 interpretation, and the hybrid scheme (global k_n, per-pair k_f) creates internal logical inconsistencies. I assign an overall score of **6.0/10**—the method has merit and the biological applications are well-motivated, but critical mathematical and validation issues must be resolved before the framework can be considered sound.

---

## Strengths
- **Conceptual innovation**: The Ka/Ks-inspired decomposition approach is genuinely novel in the single-cell field. Using HK genes as an internal reference to normalize functional divergence is a clever and biologically grounded idea that addresses a real limitation of existing distance metrics.
- **Thorough biological validation**: The four-dataset strategy (mouse atlas, human atlas, TCGA pan-cancer, brain atlas) provides multi-scale biological evidence. The cross-organ conservation ranking and brain regional analysis demonstrate CKI's ability to extract biologically meaningful signals. The OPC negative control (0 Strong signals among active migrators) provides compelling orthogonal validation of the multiplicative residual model's specificity.
- **Honest engagement with limitations**: The authors explicitly acknowledge the heuristic (not formal) nature of the Ka/Ks analogy, the empirical (not mechanistic) basis of HK gene definition, and the calibration inflation problem. This intellectual honesty is commendable and rare in methods papers.
- **Good documentation**: The supplementary materials, reproducibility guide, and pseudocode are thorough. The MIT-licensed open-source package with Zenodo archival DOI follows best practices for computational reproducibility.

---

## Critical Issues (must fix before submission)

### C1. Calibration results contradict the core interpretive framework
- **Location**: Manuscript, "Calibration confirms baseline behavior at baseline" (Results §2); Supplementary Note 1.4
- **Problem**: The calibration experiment (n = 6 random-split comparisons of the same cell population) yields a mean ω = 6.67, not ω ≈ 1. The authors correctly identify HVG pre-selection as the source of this inflation and acknowledge the discrepancy, but this acknowledgment does not resolve the problem. Specifically:
  - The entire interpretive framework (ω ≈ 1 = baseline, ω ≫ 1 = functional divergence, ω ≪ 1 = constraint) is built around ω = 1 as the theoretical null. If the empirical null is 6.67, then statements about ω values are misleading. A mean ω of 6.67 for identical populations means that in practice, ω ≈ 1 is *never observed*, which collapses the interpretive scale.
  - The permutation test addresses *statistical significance* (whether an observed ω exceeds a null ω distribution) but does not address *interpretability* (what a given ω value means). A significant ω of 8.0 may be indistinguishable from the calibration baseline of 6.67 in practical terms.
  - The authors state ω < 1 indicates "strong functional constraint," but if the calibration baseline is 6.67, the operational threshold for constraint should be ω ≪ 6.67, not ω < 1. The manuscript inconsistently uses ω = 1 as the interpretive anchor (e.g., Discussion §1: "ω near 1 means the observed differences are consistent with baseline expectation") while simultaneously reporting that baseline is 6.67.
- **Fix**: 
  1. Implement a calibration-normalized ω: ω_cal = ω_obs / ω_baseline, where ω_baseline is the expected ω for equivalent populations (mean from calibration). This would re-center the interpretation around 1.
  2. Alternatively, perform formal equivalence testing (TOST) with a larger calibration sample (n ≫ 6, ideally ≥ 30) to establish the empirical null distribution with adequate statistical power.
  3. At minimum, add ω_calibrated values alongside raw ω in all tables and figures, and revise all interpretive text to reference the calibration baseline (6.67) rather than the theoretical ideal (1.0).
  4. Report confidence intervals for the calibration baseline mean to quantify uncertainty.

### C2. JS divergence on probability-normalized vectors of different dimensionalities is not mathematically well-justified
- **Location**: Manuscript, Materials and Methods §1 ("CKI computation"); Supplementary Note 1.1–1.3; Reproducibility Guide §2
- **Problem**: k_n is computed on M-dimensional HK gene probability vectors (after softmax), while k_f is computed on N-dimensional identity gene vectors, where M (≈1,130 HK genes) and N (200 or 2,000 HVGs) are different. JS divergence is sensitive to the dimensionality of the probability space:
  1. **Dimensionality effect**: JS divergence values on a 1,130-dimensional simplex are not directly comparable to those on a 200-dimensional simplex. Higher-dimensional spaces tend to spread probability mass across more bins, which can systematically lower JS values even when the underlying distributions are equally separated.
  2. **Softmax normalization properties**: Softmax normalization is sensitive to outliers—a single highly expressed gene can absorb most of the probability mass, compressing JS divergence toward zero for both k_n and k_f. The authors should demonstrate that this effect is symmetric (i.e., doesn't differentially affect k_n vs. k_f).
  3. **Sample size normalization**: The authors do not discuss whether JS divergence is computed with explicit sample-size correction, which can matter for small pseudobulk groups.
- **Fix**:
  1. Provide a mathematical proof or simulation study showing that JS divergence on softmax-normalized vectors is approximately scale-invariant with respect to gene set size, under realistic scRNA-seq expression distributions.
  2. Alternatively, use a dimensionality-matched approach: randomly subsample HK genes to the same size as the identity gene set (e.g., 200 or 2,000) for k_n computation, and average over multiple bootstrap subsamples to stabilize the estimate.
  3. As a sensitivity analysis, report ω values computed with different HK gene set sizes (e.g., 100, 200, 500, full 1,130) to demonstrate that ω is invariant to k_n dimensionality.
  4. Discuss the effect of extreme expression values on softmax normalization and whether winsorization or alternative normalization (e.g., L1, rank-based) might be more robust.

### C3. The hybrid scheme (global k_n, per-pair k_f) creates an internal logical inconsistency
- **Location**: Manuscript, Results §3 ("CKI captures information that standard metrics miss"); Reproducibility Guide §3.2
- **Problem**: In the hybrid scheme (used for Tabula Sapiens, TCGA, and brain atlas), k_n is computed once globally (using the full pseudobulk matrix over all cell types, with the shared 1,130 HK genes), while k_f is computed per pair using the top-200 DE genes for that specific pair. This creates a fundamental asymmetry:
  1. ω becomes effectively a scaled version of k_f, since k_n is constant (or nearly constant) across all comparisons within a dataset. The ratio ω = k_f/k_n loses its intended interpretation as "baseline-normalized functional divergence" because the baseline is not pair-specific.
  2. For the Tabula Sapiens analysis (5,151 pairs), if k_n is constant, then the negative correlation between ω and standard metrics (Spearman r = -0.38 to -0.57) is actually driven entirely by k_f's correlation with standard metrics—the ratio provides no additional information beyond what k_f alone provides.
  3. The calibration experiment uses a pair-specific k_n (random split of same population), but the main analyses use a global k_n. These are different k_n definitions, making the calibration not directly applicable to the hybrid-scheme results.
  4. The statement that ω ranges from 1.10 to 58.69 (Results §3) is misleading if k_n is constant—the lowest ω merely reflects the pair with the lowest k_f.
- **Fix**:
  1. Report results with pair-specific k_n alongside global k_n for all major analyses. If the biological conclusions are consistent between the two approaches, this strengthens the method; if they differ, the global k_n approach should be abandoned.
  2. Explicitly report whether k_n varies across pairs in the hybrid scheme. If k_n is effectively constant, the authors should acknowledge that ω in the hybrid scheme is simply a rescaled k_f and adjust interpretations accordingly.
  3. In the hybrid scheme, report k_n's mean, variance, and coefficient of variation across all pairs. If CV(k_n) < 0.1, the ratio provides negligible additional information.
  4. Consider using a semi-global approach: compute k_n per organ, per tissue, or per major cell lineage rather than globally, to preserve some pair-specific baseline variability.

---

## Major Issues (should fix)

### M1. No simulation-based validation with known ground truth
- **Location**: Results (all sections)
- **Problem**: All four validation datasets are real biological data where the "true" functional divergence is unknown. The method would be substantially strengthened by simulation studies where the ground truth is controlled:
  1. Simulate data with known k_n/k_f ratios by perturbing specific gene modules at controlled magnitudes
  2. Test whether CKI recovers the known perturbation magnitude
  3. Test at various noise levels (zero-inflation, dropout rates, batch effects)
  4. Test with varying numbers of cells per group to determine minimum group sizes
- **Fix**: Add a simulation study section (can be in Supplementary) with at minimum: (a) recovery of known divergence magnitudes, (b) false positive rate under different noise regimes, and (c) power analysis as a function of sample size and effect size.

### M2. Method comparison is insufficiently systematic
- **Location**: Manuscript, Materials and Methods §4 ("Method comparison"); Discussion §4
- **Problem**: The comparison with existing methods is limited to:
  1. Computing correlations between CKI ω and four standard distance metrics on Tabula Sapiens data—but this merely establishes that ω is different, not that it is better.
  2. Computing AUC for cell-type classification (ω AUC = 0.716)—but this is a task for which CKI is explicitly not designed (the authors state "CKI is a divergence index, not a classifier").
  3. Qualitative mention of SAMap, SATURN, and CACIMAR in the Discussion—without any quantitative comparison.
  The authors claim CKI "captures information that standard metrics miss" but have not demonstrated a task where CKI outperforms all existing methods. The negative correlation (r = -0.38 to -0.57) shows CKI is different, not necessarily better.
- **Fix**:
  1. Define a task where CKI's decomposition provides actionable advantage: e.g., identifying cross-organ conserved cell types, detecting functionally specialized subpopulations within a cluster, or ranking perturbation effects. Benchmark CKI against standard metrics and specialized methods on this task.
  2. For cross-species comparison (CKI's stated application in Discussion §4): implement a quantitative comparison with SAMap and SATURN on a shared benchmark dataset with known cross-species homolog relationships.
  3. Include comparison with scHOT (single-cell Higher Order Testing; Ghazanfar et al., 2020), which also addresses differential variability in single-cell data, and with Milo (Dann et al., 2021), which tests for differential abundance.
  4. Clearly distinguish correlation analysis (what the metrics measure) from task-based benchmarking (whether what they measure is useful).

### M3. The multiplicative residual model lacks statistical rigor
- **Location**: Manuscript, Materials and Methods §5 ("Multiplicative residual model"); Results §6–10
- **Problem**: The multiplicative residual model for detecting developmental origin signatures in the brain analysis has several statistical weaknesses:
  1. The thresholds for Strong/Moderate/Weak (residual < 0.3, < 0.5, < 0.75) and ω thresholds (< 15, < 25, < 35) are arbitrary. No justification is provided for these specific cutoffs, and there is no sensitivity analysis showing how the number of detected candidates varies with threshold choice.
  2. The model structure (expected_ω = μ_ct × μ_pair / μ_grand) assumes independence of cell-type and region-pair effects, but does not test this assumption. If cell types differ in how uniformly they are distributed across regions, this assumption may be violated.
  3. The "lowest ω in the region pair" criterion for Strong candidates introduces a post-hoc selection bias: among 31,764 comparisons, the minimum ω for each region pair will always exist, regardless of biological meaning.
  4. No formal statistical test is associated with the residual classification. The authors should compute a p-value for each residual under a null model (e.g., permutation of ω values across pairs).
  5. The cross-validation against developmental neuroscience literature is post-hoc and could be subject to confirmation bias—the authors may have selectively interpreted signals that align with known biology while dismissing signals that don't.
- **Fix**:
  1. Compute empirical null distributions for the multiplicative residual by permuting ω values across cell-type/region-pair combinations, and report FDR-adjusted p-values for each Strong candidate.
  2. Perform sensitivity analysis varying the residual thresholds (e.g., 0.2, 0.3, 0.4) and ω thresholds (e.g., 10, 15, 20) to demonstrate robustness of the top signals.
  3. Provide a negative control: apply the same model to a dataset where no developmental signatures are expected (e.g., random splits within the same region) and show that the Strong candidate rate is at or below the expected false positive rate.
  4. Replace the "lowest ω in the region pair" criterion with a statistical criterion (e.g., ω significantly below the region-pair mean by more than 2 SD).

### M4. TCGA bulk RNA-seq analysis conflates cell-type composition with transcriptional divergence
- **Location**: Manuscript, Results §4 ("Cancer analysis reveals unexpected transcriptional convergence")
- **Problem**: The TCGA analysis uses bulk RNA-seq data, where each sample represents a mixture of cell types (tumor cells, stromal cells, immune infiltrate). The finding that "tumors are more homogeneous than normal tissues" (NN/TT > 1) may be driven by cell-type composition differences rather than transcriptional convergence:
  1. Normal tissues from different donors include diverse cell types in varying proportions (epithelial, stromal, immune), inflating between-sample divergence.
  2. Tumors from different patients may converge on a shared composition (predominantly tumor cells with reduced stromal/immune diversity in high-purity samples), reducing between-sample divergence.
  3. CKI at the bulk level cannot separate compositional effects from bona fide transcriptional divergence.
  4. The paired analysis (n = 2–5 patients per cancer type, only LIHC significant) is severely underpowered and does not rescue this limitation.
- **Fix**:
  1. Add a cell-type deconvolution step (e.g., CIBERSORTx, EPIC, or MuSiC) to estimate tumor purity and immune/stromal fractions for each TCGA sample. Re-compute CKI ω on deconvolved cell-type-specific expression profiles, or at minimum, regress out purity as a covariate.
  2. If deconvolution is not feasible, reframe the TCGA analysis as exploratory and acknowledge that observed NN/TT ratios may reflect compositional rather than transcriptional convergence. Remove or heavily caveat the clinical severity analyses until validated with single-cell or deconvolved data.
  3. For the clinical severity trend (LIHC Edmondson grade, BRCA PAM50), report whether the observed ω trends remain after controlling for tumor purity.

### M5. Parameter justification is incomplete
- **Location**: Manuscript, Materials and Methods; Supplementary Table 1; Reproducibility Guide §6
- **Problem**: Several key parameters are insufficiently justified:
  1. **ε = 1e-9 pseudocount**: The JS divergence pseudocount is mentioned only in the reproducibility guide (checklist item). No mathematical justification is provided for this specific value. Why not ε = 0 or machine epsilon? Does ω change with different ε values?
  2. **B = 1,000 permutations**: The authors state B = 1,000 for all datasets. For the brain atlas with 31,764 comparisons, 1,000 permutations yielding p-values on the order of 0.001 (the minimum possible p-value with pseudocount: 1/1001 ≈ 0.001) may not provide sufficient resolution for multiple testing correction at q < 0.05. A power analysis for the required B is needed.
  3. **Top-200 DE genes for k_f**: The choice of 200 is pragmatic (from the parameter sweep testing 50–2,000), but the justification that 200 "maintains discriminative power with computational efficiency" is vague. Report AUC or effect sizes at each N and demonstrate that 200 sits at the plateau (or near it).
  4. **Log base**: JS divergence uses base-2 logarithm. The authors should justify this choice vs. natural log, particularly since the [0,1] bound depends on the log base.
  5. **Softmax temperature**: Softmax normalization is applied with temperature = 1.0. The sensitivity to this implicit parameter is not discussed.
- **Fix**:
  1. Provide a sensitivity analysis for ε across {0, 1e-16, 1e-9, 1e-6, 1e-3} and demonstrate ω stability.
  2. Perform power analysis: what is the minimum B needed to achieve FDR < 0.05 at a given effect size for the brain dataset?
  3. Report parameter sweep results for N_DE in the main text or supplementary figure.
  4. Justify the base-2 log choice (presumably for the [0,1] bound) and note whether natural log produces numerically different results.

---

## Minor Issues (suggestions)

### m1. Missing equivalence testing for calibration
- **Location**: Manuscript, Results §2 ("Calibration confirms baseline behavior")
- **Problem**: Calibration uses n = 6 random-split comparisons and reports "all P > 0.05"—but failure to reject the null does not confirm equivalence. Formal TOST (Two One-Sided Tests) with an equivalence margin (e.g., ω within 20% of the calibration mean) would provide stronger evidence.
- **Fix**: Report TOST results or explicitly acknowledge the limitation that n = 6 provides insufficient power for formal equivalence testing.

### m2. HVG selection creates a circular dependency
- **Location**: Manuscript, Materials and Methods §1
- **Problem**: For Tabula Muris, HVGs are computed globally on all cells (including both populations A and B). This means the identity gene set is not independent of the data being compared—HVG selection uses variance across all cells, which includes between-population variance. This could inflate k_f for comparisons with large between-group differences.
- **Fix**: Compute HVGs independently within each population and take the union, or use a held-out reference dataset for HVG selection. Alternatively, demonstrate that the circularity does not meaningfully affect ω through a hold-one-out analysis.

### m3. Cell number imbalance is not addressed
- **Location**: Manuscript, Materials and Methods §1
- **Problem**: Pseudobulk quality depends on group size. Groups with 10 cells (the minimum) produce noisier pseudobulk estimates than groups with 1,000 cells. The authors do not discuss whether ω is sensitive to group size imbalance, and whether differentially sized groups yield biased ω estimates.
- **Fix**: Perform a downsampling analysis: for a fixed pair of cell types, compute ω with varying numbers of cells per group (10, 20, 50, 100, 200, 500) and report the stability. Check whether ω correlates with the smaller group's cell count across comparisons.

### m4. Brain atlas threshold inconsistency
- **Location**: Manuscript, Materials and Methods §3 ("Datasets"); Reproducibility Guide §4.4
- **Problem**: The brain atlas uses ≥20 nuclei per group and ≥50 nuclei per region, while other datasets use ≥10 cells per group. The rationale for this different threshold is not explained.
- **Fix**: Either standardize all thresholds or provide a biological/technical justification for the brain-specific threshold (e.g., snRNA-seq has higher noise than SmartSeq2, requiring larger group sizes).

### m5. Suppressed pathway analysis
- **Location**: Supplementary Note 1.3; Supplementary Figure S1
- **Problem**: The parameter sweep found that the identity-only configuration (w_identity = 1.0, w_pathway = 0.0) achieved the best cell-type discrimination (AUC = 0.847). However, the supplementary reports only the AUC comparison without exploring why pathway information did not improve performance. This is an informative negative result.
- **Fix**: Discuss possible reasons: pathway gene sets may overlap substantially with HVGs, pathway scores may be too coarse-grained, or MSigDB pathways may be biased toward certain biological processes. This discussion would help guide future extensions.

### m6. No discussion of batch effects on k_n
- **Location**: Manuscript, Discussion
- **Problem**: The authors note that methods like Harmony and scVI are designed to remove batch effects, but do not discuss whether k_n adequately captures batch-level variation as part of the baseline. If two samples differ primarily due to batch (not biology), CKI should ideally assign this difference to k_n (baseline) rather than k_f (functional). The authors do not test this.
- **Fix**: Perform a batch-effect analysis: compare ω before and after batch correction (e.g., Harmony), or compute ω on pairs where the primary difference is batch (same cell type, same organ, different sequencing runs). A well-functioning k_n should absorb batch variation, leaving ω unchanged.

### m7. Missing discussion of JS divergence floor effect
- **Location**: Manuscript, Materials and Methods §1; Supplementary Note 1.1
- **Problem**: When k_n approaches 0 (nearly identical gene expression distributions), the ratio ω = k_f/k_n becomes unstable (a small absolute change in k_n produces a large change in ω). The authors apply a floor of 1e-4 to k_n, but this arbitrary threshold may mask biologically meaningful near-zero k_n values.
- **Fix**: Report the distribution of raw k_n values across all analyses, identify how many comparisons fall below the floor, and discuss the impact on ω stability.

### m8. PAM50 classification accuracy not reported
- **Location**: Manuscript, Results §4
- **Problem**: The BRCA PAM50 subtype analysis uses nearest-centroid classification with Pearson correlation on 44 of 47 PAM50 genes. The classification accuracy of this PAM50 assignment is not reported.
- **Fix**: Report PAM50 classification accuracy (e.g., agreement with clinical subtype, or silhouette score). Misclassified samples could bias the ω-by-subtype comparison.

### m9. Software environment version mismatch
- **Location**: Reproducibility Guide §1.1; Manuscript, Materials and Methods §6
- **Problem**: The reproducibility guide reports Python 3.13.12 with numpy 2.4.6, scipy 1.17.1, scikit-learn 1.8.0. The manuscript reports Python 3.13.12 with scanpy >= 1.9.0, scipy >= 1.10.0, numpy >= 1.23.0, pandas >= 1.5.0, scikit-learn >= 1.2.0. The version specifications differ between the two documents—the manuscript specifies minimum versions while the reproducibility guide lists exact versions. The extremely high version numbers (numpy 2.4.6, scipy 1.17.1—these are future versions relative to the current ecosystem) suggest the reproducibility guide may contain errors.
- **Fix**: Reconcile the version specifications. Update to currently available versions or confirm that these version numbers are correct. If these are internal/compatibility versions, specify the minimum compatible versions clearly.

---

## Score Breakdown

| Category | Score | Justification |
|---|---|---|
| **Algorithm Design** | 5/10 | The Ka/Ks-inspired decomposition is creative, but the calibration failure (ω = 6.67 for identical populations), dimensionality incomparability of JS divergence on different-sized gene sets, and the hybrid scheme inconsistency represent fundamental mathematical issues that prevent the current formulation from being sound. |
| **Gene Set Selection** | 7/10 | HRT Atlas v1.0 is a well-established reference. Sensitivity analysis (r > 0.95 with alternative neutral gene sets) partially addresses robustness concerns. Deduction for: HVG circularity issue (m2), lack of formal comparison with data-driven HK detection, and insufficient justification for DE top-N choice. |
| **Validation Strategy** | 7/10 | Four-dataset strategy is comprehensive and biologically diverse. The OPC negative control is an elegant internal validation. Deduction for: absence of simulation data with known ground truth (M1), insufficient paired TCGA analysis (n = 2–5), and the brain atlas threshold inconsistency. |
| **Comparison Methods** | 4/10 | No direct benchmarking against comparable methods. Correlation with standard metrics establishes that CKI is different, not that it is better. No quantitative comparison with SAMap, SATURN, CACIMAR, scHOT, or Milo. The AUC benchmark uses an ill-suited task for CKI. |
| **Reproducibility** | 7/10 | Good documentation (pseudocode, parameter summary, output file listing, seeding at 42). Open-source package with DOI. Deduction for: version number discrepancies, lack of runtime/memory benchmarks, and absence of containerization (Docker/Singularity). |
| **OVERALL** | **6.0/10** | The method has genuine conceptual merit and the biological applications are well-chosen. However, critical mathematical issues (C1–C3) must be addressed before the framework can be considered valid, and the method comparison (M2) is inadequate for a NAR methods paper. |

---

## Recommendation

**Major Revision Required.** The core concept is valuable and the biological applications demonstrate the method's potential utility. However, the three critical issues (calibration inflation, JS dimensionality incomparability, and hybrid scheme inconsistency) represent foundational mathematical concerns that undermine the validity of the current formulation. I believe these issues are addressable with modifications to the normalization strategy and computational pipeline. If the authors can resolve these concerns and strengthen the method comparison, CKI would represent a significant contribution to the single-cell genomics methods literature.
