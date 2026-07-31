# v18 Review: Single-Cell Genomics Expert

## Overall Score: 4.5/10
## Readiness: 35%

## Summary

The manuscript presents CKI (Cell-state Kinetic Index), a metric that decomposes transcriptomic divergence into a baseline rate (k_n, from housekeeping genes) and a functional rate (k_f, from identity genes), yielding ω = k_f/k_n. The approach is applied to four datasets: Tabula Muris (mouse, 15,057 cells), Tabula Sapiens (human, 108,136 cells), TCGA bulk RNA-seq (3,596 samples, 5 cancer types), and the Siletti et al. human brain atlas (888,263 non-neuronal nuclei, 108 regions). The biological interpretations—particularly the brain regional analysis claiming detection of developmental origin signatures, colonization route boundaries, and a postnatal migration event—are intellectually creative but overreach the data.

The single-cell genomics foundation has several substantive problems. The pseudobulk computation (mean of log1p-transformed values) is non-standard and compresses dynamic range, particularly for 10x droplet data. Cell-type annotations across datasets are not harmonized, undermining cross-organ "same cell type" comparisons. The shift from global HVG (mouse, 2,000 genes) to pairwise top-200 DE genes (human/brain/TCGA) represents a fundamental methodological change that makes cross-dataset comparisons invalid. A critical internal inconsistency exists in the calibration values: the Results section reports mean ω = 6.67 for split-half controls, while the Discussion and Statistical Reporting sections reference ω = 1.54 for the same experiment. The manuscript also claims Benjamini-Hochberg FDR correction is applied, but the Reproducibility Guide explicitly states it is NOT applied—a direct contradiction. The brain developmental claims are post hoc literature correlations, not independent validations, and the "first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocytes" claim is unsupported.

## Critical Issues (must fix before submission)

- [C1] **Calibration ω value contradiction (6.67 vs. 1.54).** The Results section (line 47) reports calibration controls yielding "mean ω was 6.67 (median 6.46, range 1.59–12.16)." The Discussion (line 91) states "mean observational ω = 1.54 for equivalent populations." The Statistical Reporting section (line 37) repeats "The empirical calibration mean of ω = 1.54 for split-half equivalent populations." The Abstract states "mean ω = 6.67." These are irreconcilable contradictions for the same six control comparisons. If 6.67 is correct, the calibration fails badly—random splits of the same population produce ω far from 1.0, indicating systematic inflation of k_f relative to k_n. If 1.54 is correct, the Results section, Abstract, and all downstream references to 6.67 must be corrected. This must be resolved before any calibration claim can be evaluated.

- [C2] **FDR correction: manuscript claims vs. code reality.** The manuscript Methods (line 22) and Statistical Reporting (line 37) state "Benjamini-Hochberg FDR correction is applied within each dataset." Supplementary Note 3.3 states "Benjamini-Hochberg FDR correction is applied to the bootstrap P-values, and candidates passing FDR < 0.05 are reported as significant discoveries." However, the Reproducibility Guide Section 5.2 explicitly states: "Multiple testing correction (Benjamini-Hochberg FDR) is NOT systematically applied in the current analyses: all reported P-values and significance thresholds use raw (uncorrected) bootstrap P-values." The Discussion (line 97) also acknowledges "without formal multiple testing correction." This is a direct contradiction between the Methods description and the actual analysis. With 31,764 brain comparisons, failure to apply FDR correction means the 30 "Strong" candidates (0.09%) could easily be false positives—at nominal α = 0.05, ~1,588 false positives are expected. The manuscript must either (a) apply FDR correction and re-report results, or (b) transparently state throughout that no FDR correction was applied and reframe all claims as hypothesis-generating.

- [C3] **Calibration ω far from 1.0 undermines the core premise.** Regardless of whether the true value is 6.67 or 1.54, both are substantially above ω = 1.0. The manuscript's central claim is that ω ≈ 1 for biologically equivalent populations. A mean of 6.67 (range 1.59–12.16) means even random splits of the SAME population produce ω values indicative of "functional divergence." The manuscript attributes this to "residual measurement noise and minor stochastic variation in the pseudobulk procedure" but does not adequately investigate the root cause. The likely explanation is that k_f (computed on HVGs or pairwise DE genes) is systematically larger than k_n (computed on HK genes) even for equivalent populations, because HVG/DE selection enriches for genes with variance by construction. The calibration control does not validate the null model—it reveals a systematic bias. The argument that "none reached statistical significance (all P > 0.05)" with n = 6 is statistically unsound: with 6 samples and high variance, the power to detect any effect is negligible.

- [C4] **Inconsistent gene selection strategy between mouse and human datasets invalidates cross-dataset comparisons.** Mouse (Tabula Muris) uses global HVG (2,000 genes, Seurat flavor) for k_f. Human (Tabula Sapiens, TCGA, brain) uses pairwise top-200 DE genes ranked by |mean_diff|. These are fundamentally different approaches: global HVG captures genes variable across ALL cell types, while pairwise DE genes capture genes differing between TWO specific populations. The resulting k_f values are not on the same scale, and ω values are not comparable across datasets. The manuscript does not acknowledge this as a limitation. The mouse mean ω (27.31) vs. human mean ω (14.23) comparison (line 51) is meaningless given the different k_f definitions. Figure 5's cross-organ conservation ranking "between human and mouse" is similarly compromised.

- [C5] **TCGA log transformation discrepancy.** The manuscript (line 26) states "log2(TPM + 1) transformed." The Reproducibility Guide (line 105) states "log2(TPM + 0.001) transformation." These are vastly different: log2(TPM + 1) zeroes out sub-1 TPM values, while log2(TPM + 0.001) preserves them at large negative log values. This affects all downstream k_f and k_n computations on TCGA data. The correct transformation must be identified and used consistently.

## Major Issues (should fix)

- [M1] **Pseudobulk computed as mean of log-transformed values is non-standard.** The pipeline normalizes per cell (CP10k → log1p), then averages across cells to form pseudobulk. Standard practice for pseudobulk differential expression aggregates raw counts (or simple sums) and applies normalization after aggregation. Mean-of-log values compresses the dynamic range and is sensitive to dropout, especially for 10x data (Tabula Sapiens, brain atlas). For SmartSeq2 (Tabula Muris), this is less problematic. The manuscript should justify this choice or switch to standard pseudobulk aggregation and recompute results.

- [M2] **Cell-type label harmonization across datasets is not described.** Cross-organ "same cell type" comparisons (59 pairs, 17 cell types) require that a "macrophage" in liver and a "macrophage" in lung refer to the same cell type. Tabula Sapiens uses cell_type_ontology_term_id, but the manuscript does not describe how labels were harmonized across organs or whether ontology IDs were validated. Similarly, the mouse-human comparison in Figure 5 requires cross-species cell-type mapping, which is not described. The reliability of the entire cross-organ conservation analysis depends on this unaddressed step.

- [M3] **Softmax normalization before JS divergence is poorly justified and potentially problematic.** Softmax (p_i = exp(x_i) / Σexp(x_j)) is extremely sensitive to high-expression outliers. A few highly expressed genes will dominate the probability distribution, making JS divergence effectively a comparison of only the top few genes. This is particularly acute for HK genes, where a small number of highly abundant HK genes (e.g., ribosomal genes, GAPDH) could dominate k_n. The manuscript should test sensitivity to normalization choice (e.g., simple L1 normalization, rank-based normalization) or justify why softmax is appropriate for expression data.

- [M4] **HVG selection bias for k_f is not adequately addressed.** The manuscript acknowledges (line 93) that "pre-selecting genes that vary across cell types, k_f may be inflated relative to a random gene set." The counter-argument is that calibration controls (random split, ω ≈ 1) show HVG selection alone doesn't inflate ω. But this argument is circular: the calibration controls use the SAME HVG selection on the SAME population, so any inflation affects k_f and k_n equally if the split is random. The real question is whether HVG selection inflates k_f for genuinely different populations, which the calibration cannot test. A proper control would compare k_f on HVGs vs. k_f on random gene sets of equal size for known different cell types.

- [M5] **The OPC "negative control" argument is logically flawed.** The manuscript presents 0 Strong signals for OPCs (the most migratory CNS cells) as validation that the model "detects developmental-origin signatures rather than general motility" (line 77). But if the model's purpose includes detecting migration (as claimed for fibroblasts), then failing to detect migration in the MOST migratory cell type could equally indicate poor sensitivity. The argument is post hoc: when the model finds signals, they are "developmental signatures"; when it doesn't find signals in migratory cells, this "validates specificity." This circular reasoning needs to be replaced with a rigorous positive and negative control framework.

- [M6] **"First transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations" is an overreach.** The CKI analysis identifies region pairs with low ω for oligodendrocytes. The dorsal/ventral interpretation is imposed post hoc by mapping these region pairs onto known developmental origins from Foerster et al. (35). The analysis does not independently classify oligodendrocytes as dorsal- or ventral-derived—it identifies transcriptomic similarity between certain brain regions. The claim of "first transcriptome-wide metric" should be removed or substantially softened to accurately reflect what was demonstrated (low ω between cortex and thalamus/brainstem, consistent with known developmental origin differences).

- [M7] **TCGA application: the pseudobulk concept breaks down.** For single-cell data, pseudobulk aggregates many cells into a representative profile. For TCGA bulk RNA-seq, the "pseudobulk" IS the bulk measurement—there is no aggregation step. The k_f/k_n decomposition on bulk tissue measures tissue-level transcriptomic divergence, not cell-state divergence. Tumor-tumor ω comparisons are confounded by tumor purity, stromal content, and immune infiltration, none of which are controlled for. The claim that "tumors are more transcriptionally homogeneous than normal tissues" (median NN/TT > 1.0) could reflect tumor purity artifacts rather than biological convergence. The manuscript should acknowledge these confounders and, ideally, control for tumor purity (e.g., using ESTIMATE or similar).

- [M8] **Paired tumor-normal sample sizes are critically small.** The manuscript reports n = 2–5 paired samples per cancer type (line 59). With such small samples, the paired vs. unpaired comparison (Mann-Whitney P = 0.024 for LIHC only) is underpowered and the "paired/unpaired ratio = 0.99–3.25" range is uninformative. The manuscript acknowledges this limitation but still presents the analysis as a result. This section should be moved to supplementary or removed.

- [M9] **Brain developmental mechanism assignments are post hoc and unvalidated.** The four biological mechanisms (developmental origin heterogeneity, colonization route boundaries, compartmentalized developmental specification, postnatal migration) are assigned to 30 Strong candidates by "systematic cross-validation against the developmental neuroscience literature." This is literature correlation, not independent validation. The assignments are unfalsifiable—any low ω signal can be attributed to some developmental mechanism after the fact. The manuscript should explicitly state that these are hypothesis-generating interpretations, not validated discoveries, and remove language implying confirmation (e.g., "CKI detects," "demonstrates," "confirms").

- [M10] **Cross-organ conservation rankings include cell types with n = 1.** B cells (n = 1), Smooth muscle cells (n = 1), and Memory B cells (n = 1) appear in the ranking table (Table 2). A ranking based on a single pair is uninformative and misleading. These should be removed from the ranking or clearly flagged as unrankable. The Spearman r = -0.40 to +0.02 concordance with standard metrics is based on only 59 pairs, many of which have n ≤ 3, making the correlation unreliable.

## Minor Issues (nice to fix)

- [m1] **Minimum 10 cells per type is low for pseudobulk.** While common in atlas-scale analyses, 10 cells provides limited power for stable pseudobulk estimates, especially for 10x data with high dropout rates. The brain atlas uses ≥20 nuclei, which is better, but the Tabula Sapiens threshold of 10 should be justified or raised.

- [m2] **TCGA sample count discrepancy.** The manuscript states 3,596 samples from 5 cancer types. The Reproducibility Guide mentions "from 10,535 raw TCGA samples after filtering" (line 102) without explaining what filtering was applied. The filtering criteria should be specified.

- [m3] **Figure 5 legend ambiguity.** The legend states "17 cell types with cross-organ comparisons (n = 59 pairs) between human and mouse," but the Results text describes only Tabula Sapiens (human) data. The "between human and mouse" phrase is misleading if no mouse data is included in this specific analysis.

- [m4] **Cross-organ pair count: 59 vs. 60.** The manuscript consistently states 59 pairs, but the Reproducibility Guide (line 127) states "Subset of 60 same-cell-type cross-organ pairs." This discrepancy should be resolved.

- [m5] **HK gene count varies across datasets.** HRT Atlas v1.0 contains 1,130 genes, but 1,129 matched Tabula Sapiens (Supplementary Note 4.2) and 1,115 matched the Siletti brain atlas (line 27). The manuscript should report the exact number of HK genes used per dataset in a single table for transparency.

- [m6] **Enormous standard deviations in TCGA clinical analysis.** PAM50 Luminal A: 344.5 ± 323.4 (SD > 90% of mean). Edmondson G1: 101.8 ± 46.8. These extreme variances suggest ω is not normally distributed and may have outliers driving the means. Median-based reporting would be more appropriate, and the distributions should be inspected for bimodality or outlier effects.

- [m7] **Random seed = 42 is stated but bootstrap reproducibility is not verified.** With B = 1,000 permutations, results should be stable across seeds. A sensitivity analysis with 2-3 additional seeds would strengthen reproducibility claims.

- [m8] **Donor-level variation not addressed in pseudobulk.** Tabula Sapiens contains multiple donors. Averaging across all cells of a type ignores donor identity, potentially conflating inter-donor variation with cell-type variation. A donor-aware pseudobulk (average per donor, then compare) would be more rigorous.

- [m9] **The 10 cell classes in the brain analysis are uneven.** Bergmann glia (not stated, likely small) and choroid plexus (7,689) have far fewer nuclei than oligodendrocytes (490,246). The ω estimates for rare cell types are less stable. The manuscript should report confidence intervals or bootstrap uncertainty for the per-cell-type mean ω values.

- [m10] **The multiplicative residual model thresholds are arbitrary.** Strong (residual < 0.3), Moderate (< 0.5), Weak (< 0.75) are not justified by any statistical or biological reasoning. The manuscript should either derive these from the data (e.g., percentile-based) or justify the specific cutoffs.

## Strengths

- The conceptual framing—decomposing transcriptomic divergence into baseline and functional components—is intellectually interesting and addresses a real gap in how standard metrics treat all expression changes equally.

- The transparency about the Ka/Ks analogy being heuristic rather than formal is commendable. The Discussion explicitly states "CKI is a heuristic index, not a formal measure of Darwinian selection" and lists four technical limitations of the analogy.

- The inclusion of four diverse datasets spanning mouse, human, cancer, and brain demonstrates ambition and breadth. The Siletti brain atlas analysis with 888,263 nuclei is computationally impressive.

- The negative correlation between CKI ω and all four standard metrics (Spearman r = -0.38 to -0.57, P < 0.001) on 5,151 pairs is the most convincing result, suggesting CKI captures genuinely different information.

- The observation that CKI is the only metric where same-organ pairs have higher values than different-organ pairs (mean ω 16.18 vs. 13.77) is an interesting finding that merits further investigation.

- The open-source Python package (MIT License) with documented reproducibility guide and fixed random seeds facilitates transparency and reproducibility.

- The sensitivity analysis showing robustness to alternative HK definitions (r > 0.95) partially addresses concerns about HK gene choice, though this analysis is only briefly mentioned and should be expanded.

## Specific Recommendations

1. **Resolve the 6.67 vs. 1.54 calibration contradiction immediately.** Re-run the six calibration controls, verify the exact values, and ensure all sections of the manuscript (Abstract, Results, Discussion, Statistical Reporting) report the same number. If the true calibration mean is 6.67, acknowledge that the method has a systematic positive bias and investigate its source (likely HVG selection inflating k_f).

2. **Reconcile the FDR correction discrepancy.** If FDR correction was not applied (as stated in the Reproducibility Guide), update all manuscript text to reflect this. Apply BH FDR correction to the 31,764 brain comparisons and report how many Strong candidates survive. If most do not survive, reframe the brain analysis as exploratory.

3. **Standardize the gene selection strategy.** Use either global HVG or pairwise DE genes consistently across all datasets. If different strategies are justified for different dataset sizes, explicitly state that ω values are not comparable across datasets and remove any cross-dataset comparisons (including the mouse-human comparison in Figure 5).

4. **Replace the OPC negative control argument with a proper validation framework.** Define a priori what the model should detect (migration vs. developmental origin) and test against known positive controls (e.g., cell types with well-characterized migration) and negative controls. The current post hoc reasoning is unfalsifiable.

5. **Soften all biological interpretation claims.** Replace "CKI detects," "demonstrates," "confirms," and "identifies" with "CKI is consistent with," "suggests," or "is associated with" throughout the brain analysis section. Remove the "first transcriptome-wide metric" claim.

6. **Address pseudobulk computation methodology.** Either justify mean-of-log1p as a deliberate choice (with sensitivity analysis against sum-then-normalize) or switch to standard pseudobulk aggregation. For the brain atlas, normalization at the pseudobulk level (rather than cell level) should be justified.

7. **Test sensitivity to softmax normalization.** Compare results using softmax vs. L1 normalization vs. rank-based normalization on at least one dataset. If results are robust, report this; if not, discuss the implications.

8. **Control for tumor purity in TCGA analysis.** Use established purity estimation methods (ESTIMATE, ABSOLUTE, or CPE) and verify that the NN/TT > 1.0 finding persists after purity adjustment. If purity drives the result, reframe the interpretation.

9. **Expand the cross-organ conservation analysis.** Remove cell types with n ≤ 3 from the ranking, or collapse them into broader categories. Report confidence intervals for each cell type's mean ω. Test whether the ranking is stable to bootstrap resampling.

10. **Add a donor-level analysis for Tabula Sapiens.** Compute pseudobulks per donor per cell type and assess how much of k_n is driven by inter-donor variation. If donor effects are substantial, this should be acknowledged as a limitation and ideally corrected.
