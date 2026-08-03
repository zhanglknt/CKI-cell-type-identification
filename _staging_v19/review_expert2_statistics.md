# Expert Review #2: Statistics & Data Analysis

## Overall Assessment
CKI is a conceptually elegant metric that addresses a genuine gap in transcriptomic comparison methodology. The decomposition of JS divergence into baseline (k_n) and functional (k_f) components is principled and well-motivated. However, the statistical framework has several important weaknesses that undermine confidence in the reported claims — most critically, insufficient bootstrap resolution for the scale of multiple comparisons, absence of confidence intervals for the primary effect-size metric ω, and arbitrary thresholding in the migration detection model without formal statistical inference. With targeted revisions, the manuscript can achieve the rigor expected of NAR. **Score: 5.5/10**.

## Strengths
- The baseline-normalized divergence framework (k_n/k_f decomposition) is genuinely innovative and addresses a well-articulated gap — that standard distance metrics conflate baseline variation with functional divergence
- The negative correlation of CKI ω with all four standard metrics (Spearman r = −0.38 to −0.57, all P < 0.001; Manuscript, "CKI captures information that standard metrics miss," paragraph 3) provides strong evidence that ω captures an orthogonal information dimension, which is perhaps the strongest empirical result in the paper
- The calibration experiment (6 split-half controls on equivalent populations) is a commendable attempt to establish baseline behavior empirically, and the acknowledgment that ω=6.67 is the empirical baseline rather than ω=1 (Discussion, paragraph 1) shows awareness of the method's limitations
- OPCs as a negative control for the multiplicative residual model (0 Strong candidates among 5,671 OPC comparisons despite being the most motile cells) is a clever and persuasive orthogonal validation that the model does not simply detect general cell motility (Manuscript, "OPCs: key negative control," paragraph 1)
- Robustness to HK gene set definition (r > 0.95 when using lowest-variance genes as alternative; Manuscript, Discussion paragraph 2; Supplementary Note 1.2) is reassuring
- Transparent disclosure of AI writing tool usage (Cover Letter, paragraph 3) is appreciated
- Well-organized reproducibility guide with clear parameter specifications and output file descriptions

## Critical Issues (must fix before submission)

### C1. Bootstrap resolution (B=1,000) severely limits BH-FDR power for large-scale comparisons
- **Location**: Manuscript, "Bootstrap permutation test" (Methods, paragraph 2); Reproducibility Guide §5.1; Supplementary Note 3.2–3.3
- **Problem**: With B=1,000 permutations, the minimum achievable one-sided P-value is 1/(1001) ≈ 0.001. For the brain atlas analysis with m=31,764 comparisons, the Benjamini-Hochberg threshold at rank i=1 is α/m = 0.05/31764 ≈ 1.57×10⁻⁶, which is approximately 635-fold below the minimum resolvable P-value. While BH-FDR at larger ranks (i ≥ 635) can reach the 0.001 threshold (at i=635, threshold = 635×0.05/31764 = 0.001), this creates two problems: (a) all comparisons with genuinely extreme ω are right-censored at P≈0.001, losing statistical resolution; (b) the granularity — only 1,001 distinct P-values exist for 31,764 comparisons — means many comparisons share identical P-values, requiring a tie-breaking strategy that is not described. For Tabula Sapiens (5,151 pairs), at least 103 comparisons must achieve minimum P for any BH rejection at α=0.05, which is plausible but not guaranteed. The issue is acknowledged nowhere in the manuscript.
- **Fix**: (a) Increase B to at least 10,000 and preferably 50,000–100,000 for the brain and human datasets (computationally feasible with the described hardware). This would provide minimum P ≈ 10⁻⁵, substantially improving resolution. (b) Alternatively, adopt an adaptive permutation strategy (e.g., Besag & Clifford, 1991) that continues permuting for borderline comparisons until a predetermined number of exceedances is observed. (c) Document the tie-breaking procedure used in BH-FDR when P-values are tied. (d) Report the number of comparisons achieving FDR < 0.05 at each B value as a sensitivity analysis.

### C2. ω point estimates lack confidence intervals throughout
- **Location**: All Results sections (Tabula Muris §2, Tabula Sapiens §3, TCGA §4, Brain §5–6); Reproducibility Guide §5.1 explicitly states: "NOT confidence intervals for omega itself"
- **Problem**: ω is the primary reported metric, yet only point estimates (means, medians, ranges) are provided. The reproducibility guide explicitly disclaims that bootstrap critical values are "NOT confidence intervals for omega itself." For an effect-size-based metric that is a ratio of two JS divergences (both bounded [0,1] but the ratio unbounded), readers have no way to assess the precision of any reported ω value. This is particularly problematic for: (a) the cross-organ conservation ranking (Table 2), where several cell types have n=1 or n=3 — the point estimates imply precision that doesn't exist; (b) the brain migration candidates, where individual ω values (e.g., ω=2.51 for Astrocyte VLN vs. VPL) are used for ranking without any uncertainty bounds.
- **Fix**: The existing B=1,000 bootstrap resamples for each pair already contain the information needed to construct percentile or BCa confidence intervals for ω. Report 95% bootstrap CIs alongside all point estimates. For comparisons with extreme ω values where the ratio distribution is heavy-tailed, consider reporting the interval on the log scale. The computational cost is negligible since the resamples already exist.

### C3. Multiplicative residual model lacks formal statistical inference
- **Location**: Manuscript, "Multiplicative residual model for brain regional analysis" (Methods, last paragraph); "CKI detects putative inter-regional migration events" (Results, middle paragraph); Supplementary Note 3.3
- **Problem**: The Strong/Moderate/Weak tier thresholds (residual < 0.3, < 0.5, < 0.75) are arbitrary and uncalibrated. They represent fixed cutoffs on the ratio of observed to expected ω, but no null distribution exists for the residuals. The authors compute expected_ω from a two-way multiplicative model (cell_type × region_pair) and define candidates as those with low residuals — but low relative to what baseline? The 30 Strong candidates are subsequently cross-validated against literature, which provides biological plausibility but not statistical evidence for the residual thresholds themselves. Key unknowns: (a) what is the false positive rate of the Strong tier? (b) could the same number of candidates arise by chance given the residual distribution? The inclusion of OPCs (0 Strong among 5,671 pairs) as a "negative control" is clever but doesn't constitute a formal null.
- **Fix**: (a) Generate an empirical null distribution for the residuals by permuting cell-type labels across region pairs (shuffling the cell_type × region_pair mapping) and recomputing the model. This would yield a null distribution of residual values against which to calibrate thresholds. (b) Compute permutation P-values for each candidate's residual and apply FDR correction. (c) Alternatively, fit a formal log-linear model [log(ω) ~ cell_type + region_pair] and identify outliers via studentized residuals with a known distribution (e.g., approximate normality after log transformation). The OPC negative control can then be quantified as an enrichment analysis rather than a qualitative observation.

### C4. Per-cell-type sample sizes insufficient for cross-organ conservation ranking
- **Location**: Manuscript, "CKI ranks cell types by cross-organ conservation" paragraph, Table 2
- **Problem**: Of the 17 cell types ranked in Table 2, several have critically small sample sizes: Memory B cells (n=1), Smooth muscle cells (n=1), Endothelial cells (n=3). The manuscript acknowledges that "several cell types (particularly those with n = 1 or 3) have small sample sizes, and their rankings should be interpreted with appropriate caution," yet presents them in a ranked table with precise mean ω values — a format that inherently implies statistical ordering. The point estimate for Memory B cells (mean ω = 2.70) is based on a single comparison, making its rank potentially driven by noise.
- **Fix**: (a) Either remove cell types with n < 5 from the ranking table (reporting them in a separate "insufficient data" category), or (b) provide bootstrap CIs for each cell-type mean ω that transparently show the uncertainty. Given the manuscript structure, option (b) is preferred as it preserves the full data while communicating uncertainty. Also: clarify whether the n=1 for B cells and Smooth muscle cells is a genuine data limitation or a filtering artifact from the ≥10 cells per group requirement.

### C5. ω distribution properties not adequately characterized
- **Location**: Manuscript, Methods ("CKI computation"), Results sections; Supplementary Note 1.4
- **Problem**: ω = k_f/k_n is a ratio of two JS divergences, each bounded in [0,1] but with potentially very small denominators. A floor of 1e-4 is applied to k_n (Supplementary Note 1.1, "to prevent inflated omega from near-zero denominators"), but the distributional consequences are not discussed. Key concerns: (a) ω is inherently right-skewed and potentially heavy-tailed — this matters for using Cohen's d (which assumes approximate normality) as a standardized effect size; (b) the permutation null distribution of ω may not be normal either, especially when k_n is small; (c) the floor at 1e-4 creates an upper bound of ω ≈ k_f/1e⁻⁴ ≈ 10⁴, but the actual behavior near this bound isn't characterized. For the TCGA analysis where normal-normal ω can exceed 300 (and tumor-tumor ω even higher), the distributional properties should be examined.
- **Fix**: (a) Report the empirical null distributions (histograms or Q-Q plots) for representative comparisons in each dataset, demonstrating whether the permutation null is approximately normal or requires non-parametric inference. (b) If the null is non-normal, replace Cohen's d with a non-parametric standardized effect size (e.g., rank-based). (c) For readers' benefit, add a supplementary figure showing the ω distribution shape across all comparisons in the largest dataset (brain atlas, 31,764 pairs), including tail behavior and the effect of the k_n floor.

### C6. TCGA paired tumor-normal analysis critically underpowered yet Mann-Whitney tests are performed
- **Location**: Manuscript, "Cancer analysis reveals unexpected transcriptional convergence" paragraphs 2–3; Reproducibility Guide §4.3
- **Problem**: The paired tumor-normal comparison involves n = 2–5 patients per cancer type (Manuscript: "the small number of patients with paired tumor and normal samples (n = 2–5 per cancer type)"). Despite acknowledging this limitation, Mann-Whitney U tests are reported (paired vs. unpaired comparison), with LIHC reaching P = 0.024. The Mann-Whitney test with n₁=2–5 and n₂=larger (unpaired samples) has negligible power to detect anything but enormous effect sizes. More critically, at n=2, the minimum possible two-sided Mann-Whitney P-value is 0.33 — the test literally cannot reject at α=0.05. The reported P=0.024 for LIHC is therefore either from a cancer type with n > 2 or represents a different comparison than stated.
- **Fix**: (a) Remove formal hypothesis tests for the paired vs. unpaired comparison entirely — report only descriptive statistics with the caveat that n=2–5 precludes meaningful inference. (b) If reporting P-values, explicitly state the achievable P-value floor for each cancer type given its paired sample size. (c) Consider whether the Paired/Uunpaired ratio analysis adds scientific value beyond the much more robust NN/TT convergence finding.

## Major Issues (should fix)

### M1. One-sided bootstrap test: justification incomplete
- **Location**: Manuscript, "Bootstrap permutation test" (Methods, paragraph 2); Supplementary Note 1.5, 3.2
- **Problem**: The one-sided test H₀: ω ≤ ω_null is designed to detect ω significantly above null expectation. However, the CKI framework conceptually allows ω << calibration (functional constraint). The Discussion acknowledges ω << 1 is "rare in practice" (Supplementary Note 1.4), and the calibration experiment shows ω never falls below 1.59 for equivalent populations. Yet the choice of one-sided testing should be explicitly justified against the possibility of detecting significantly constrained comparisons (ω substantially below null). Using only a one-sided test precludes discovery of convergent/constrained transcriptional programs.
- **Fix**: Add a paragraph justifying the one-sided choice with reference to the calibration data. Alternatively, provide two-sided P-values as supplementary for completeness, while noting that the empirical null (μ≈6.67) makes two-sided lower-tail P-values uninformative in practice. This would demonstrate awareness of the issue without changing the conclusions.

### M2. BH-FDR per-dataset boundaries may mask cross-dataset comparisons
- **Location**: Manuscript, "Bootstrap permutation test" (Methods); Supplementary Note 3.3; Reproducibility Guide §5.2
- **Problem**: BH-FDR correction is applied "within each dataset." This is reasonable for independent analyses but creates an ambiguity: the four datasets have vastly different numbers of tests — mouse pilot (15 pairs + 6 controls), Tabula Sapiens (5,151), TCGA (varies by cancer type), and brain atlas (31,764). The BH correction stringency differs by ~2,000-fold between the smallest and largest datasets, meaning a ω result with the same nominal P-value could be declared significant in one dataset but not in another. This is inherent in the FDR framework but should be explicitly discussed.
- **Fix**: Add a note in the Methods clarifying that FDR-corrected significance is dataset-specific and that cross-dataset comparison of "significance" is not appropriate. Consider reporting both dataset-specific FDR and a pooled FDR as a sensitivity analysis.

### M3. Spearman correlations between metrics: bootstrapping of correlation CIs absent
- **Location**: Manuscript, "CKI captures information that standard metrics miss" paragraphs 2–3; Figure 3A
- **Problem**: The negative correlation between CKI ω and standard metrics (r = −0.38 to −0.57) is the paper's strongest statistical claim and is reported with "all P < 0.001" on n=5,151 pairs. At this sample size, even negligible correlations achieve P < 0.001, making the P-value uninformative. What matters is the magnitude and stability of the correlation, yet no bootstrap CIs or cross-validation of the correlation coefficients are provided.
- **Fix**: Report 95% bootstrap CIs for each Spearman correlation coefficient (by resampling the 5,151 pairs with replacement). This would demonstrate whether the negative correlation is robust to resampling. Given n=5,151, CIs should be tight, but reporting them would strengthen one of the paper's central claims.

### M4. Empirical calibration baseline (ω=6.67) estimated from only n=6 comparisons
- **Location**: Manuscript, "Calibration confirms baseline behavior at baseline" paragraph 2; Discussion paragraph 1
- **Problem**: The empirical calibration baseline ω=6.67 is a critical interpretive anchor — it replaces the theoretical ω=1 as the operational "no divergence" reference. Yet it's estimated from only n=6 split-half comparisons on a single dataset (Tabula Muris), whose ω values range from 1.59 to 12.16 (a 7.6-fold range). This wide range for "equivalent" populations suggests ω has substantial intrinsic variability that is not adequately captured. The standard error of this baseline mean is approximately 1.52 (SD/√6 = 3.72/√6), making the 95% CI roughly [3.6, 9.7] — wide enough to overlap with many "real" ω values.
- **Fix**: (a) Report the standard error and 95% CI of the calibration mean. (b) Ideally, expand the calibration by including split-half controls from the Tabula Sapiens dataset as well, to demonstrate that the empirical baseline generalizes across datasets. If Tabula Sapiens calibration yields a different baseline (likely, given species and platform differences), discuss the implications.

### M5. Clinical stratification: PAM50 Normal-like subgroup (n=7) and Edmondson G4 (n=11) too small for inference
- **Location**: Manuscript, "Cancer analysis" final paragraph; Reproducibility Guide §4.3
- **Problem**: The BRCA PAM50 analysis reports Kruskal-Wallis P = 0.0002 across 5 subtypes, but the Normal-like group has n=7. In the LIHC Edmondson analysis, the Jonckheere-Terpstra trend test (P < 0.001) is driven partly by G4 (n=11). Omitting these small groups would change the test results. Additionally, the Kruskal-Wallis test only reports omnibus significance — post-hoc pairwise comparisons between subtypes are not provided, leaving unclear which specific subtype differences drive the signal.
- **Fix**: (a) For PAM50, report the Kruskal-Wallis result with and without the Normal-like (n=7) group as a sensitivity analysis. (b) Provide post-hoc Dunn's test with Holm correction for pairwise subtype comparisons. (c) For LIHC, report the Jonckheere-Terpstra result with and without G4.

### M6. Multiplicative residual model: global mean ω=8.01 appears to differ from the astrocyte mean of 14.36
- **Location**: Manuscript, "CKI detects putative inter-regional migration events" paragraph 1; Multiplicative residual model paragraph 1
- **Problem**: The global mean ω of 8.01 reported in the multiplicative model context appears inconsistent: if the 10-cell-type weighted average means range from 2.37 (Bergmann glia) to 14.36 (astrocytes), the global mean should reflect the weighted contribution of each cell type. Astrocytes (5,778 pairs) and oligodendrocytes (likely largest given 490,246 nuclei) would dominate. The text does not explain how 8.01 is computed — is it the arithmetic mean across all 31,764 pair-level ω values, or the mean of the 10 cell-type means? The difference matters because cell types with many regions (and thus many pairs) would dominate a pair-level mean.
- **Fix**: Clarify the computation of μ_grand. If it's the arithmetic mean of all 31,764 pair-level ω values, state this explicitly and provide the weighted breakdown by cell type. If it's the mean of cell-type means, justify the choice and note that this gives equal weight to cell types with vastly different numbers of regions and pairs.

## Minor Issues (suggestions)

### m1. +1 pseudocount in P-value formula: cite precedent
- **Location**: Manuscript, "Bootstrap permutation test" (Methods); Supplementary Note 1.5
- **Problem**: The formula P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) is a standard correction (Davison & Hinkley, 1997; Phipson & Smyth, 2010), but the manuscript does not cite this precedent. Given the interpretive importance of the +1 correction (preventing P=0), appropriate citation would strengthen methodological credibility.
- **Fix**: Cite Davison & Hinkley (1997) "Bootstrap Methods and Their Application" and/or Phipson & Smyth (2010) "Permutation P-values Should Never Be Zero" (Stat. Appl. Genet. Mol. Biol.).

### m2. Cohen's d from permutation null: assumption of normality
- **Location**: Manuscript, "Bootstrap permutation test," "Statistical reporting" (Methods); Supplementary Note 3.2
- **Problem**: Cohen's d = (ω_obs − mean(ω_null))/sd(ω_null) is computed from the permutation null distribution. This is standard practice but implicitly assumes that the null is approximately normal (or at least symmetric). For a ratio distribution (ω = k_f/k_n), normality of the null is not guaranteed. The Supplementary Note states "standardized effect sizes are typically > 1.0 for biologically meaningful comparisons, indicating large effects relative to the null distribution," which conflates Cohen's d thresholds (d > 0.8 = large) with permutation-based standardized differences.
- **Fix**: Add a brief note in Supplementary Note 3.2 acknowledging that Cohen's d thresholds (0.2, 0.5, 0.8) were developed for approximately normal data and should be interpreted cautiously with permutation-based effect sizes. Consider renaming to "standardized mean difference" rather than "Cohen's d" to avoid implying normality.

### m3. TCGA TT vs. NN: maximum 2,000 random comparisons
- **Location**: Reproducibility Guide §4.3 ("Maximum 2,000 random TT and TN pairs each")
- **Problem**: For BRCA with 1,032 tumor samples, the number of possible TT pairs is ~532,000, but only 2,000 are sampled. The manuscript does not discuss whether 2,000 random pairs adequately represent the full pairwise structure or whether the sampling introduces variance. This is a minor concern given the large underlying sample sizes.
- **Fix**: Add a brief note on the sampling strategy justification (e.g., "2,000 pairs captures the distribution with SE < 1% of the mean") or report the variability across repeated random draws as a sensitivity check.

### m4. TCGA ω values scale differently from single-cell ω values
- **Location**: Manuscript, TCGA Results section; Discussion
- **Problem**: TCGA ω values (tens to hundreds, e.g., Luminal A intratumoral ω = 344.5) are an order of magnitude larger than single-cell ω values (e.g., Tabula Sapiens cross-organ ω range 1.10–58.69). This is because TCGA uses bulk RNA-seq (TPM → log2(TPM+1)) with a fundamentally different noise structure than single-cell pseudobulk (CP10k + log1p). The manuscript does not explicitly discuss how normalization differences affect the ω scale and whether cross-dataset comparison of absolute ω values is meaningful.
- **Fix**: Add a sentence in the Discussion acknowledging that TCGA ω values are not directly comparable in magnitude to single-cell ω values due to different data modalities and preprocessing. Emphasize that within-dataset ω rankings and ratios (e.g., NN/TT) are the valid comparisons.

### m5. ABBA-BABA or f4-statistic analogy potential
- **Location**: Discussion (general)
- **Problem**: The Ka/Ks analogy is the primary conceptual framework, but CKI's structure — decomposing a distance into components and computing ratios — has interesting parallels to ABBA-BABA/f4-statistics in population genetics, which also use ratio-based inference to detect deviations from neutral admixture. Mentioning this parallel could enrich the Discussion and connect CKI to a broader statistical tradition.
- **Fix**: Optional. Add a 1–2 sentence mention of the conceptual parallel, if space permits.

### m6. Missing explicit statement on normality assumptions for parametric tests
- **Location**: Supplementary Note 3.1
- **Problem**: The manuscript uses non-parametric tests (Mann-Whitney, Kruskal-Wallis, Spearman) for most comparisons, which is appropriate. However, Cohen's d and the bootstrap standardization implicitly involve parametric assumptions (normal approximation to the null). A single sentence clarifying why non-parametric tests were chosen for group comparisons but parametric-style effect sizes are reported would improve transparency.
- **Fix**: Add to Supplementary Note 3.1: "Non-parametric tests were chosen because ω distributions are typically right-skewed and do not satisfy normality assumptions. For effect sizes, standardized mean differences from the permutation null are reported as descriptive measures rather than parametric Cohen's d."

### m7. ROC-AUC without confidence intervals or cross-validation
- **Location**: Manuscript, Table 1; Figure 3C
- **Problem**: Cell-type classification AUC values (e.g., CKI ω AUC = 0.716) are reported as point estimates without CIs. With 5,151 pairs, the AUC should have a reportable standard error (e.g., via DeLong's method), especially since the AUC differences between metrics (0.716 vs. 0.690 vs. 0.718) are small and may not be statistically distinguishable.
- **Fix**: Report 95% CIs for all AUC values and, if comparing metrics, provide DeLong test P-values for pairwise AUC differences.

### m8. Calibration "all P > 0.05" assertion needs explicit P-values
- **Location**: Manuscript, "Calibration confirms baseline behavior" paragraph 2
- **Problem**: The statement "none of the six comparisons reached statistical significance (all P > 0.05, one-sided bootstrap test)" reports only a range for P-values. For transparency, report the actual P-values for all 6 calibration comparisons in the supplementary material, allowing readers to assess whether the non-significance is marginal (P ≈ 0.06) or unequivocal (P ≈ 0.50+).
- **Fix**: Add a supplementary table listing all 6 calibration control comparisons with observed ω, null mean ω, null SD, and exact bootstrap P-value.

---

## Score Breakdown

| Criterion | Score | Justification |
|-----------|-------|---------------|
| Bootstrap Design | 4/10 | B=1,000 is insufficient for BH-FDR with 31,764 tests; no adaptive or sequential strategy; tie-breaking undocumented |
| P-value & FDR | 5/10 | One-sided choice reasonable but under-justified; +1 correction correct but uncited; BH resolution gap not acknowledged |
| Multiple Comparisons | 4/10 | BH-FDR restricted by bootstrap resolution; per-dataset boundaries not discussed; brain analysis detection model uses uncalibrated thresholds |
| Effect Size Interpretation | 5/10 | ω as effect size is principled but CIs absent; empirical baseline (ω=6.67) from only n=6; distributional properties of ω not examined |
| Clinical Analysis Rigor | 5/10 | Small subgroups (PAM50 Normal-like n=7, Edmondson G4 n=11, paired n=2–5); post-hoc tests missing; TCGA paired analysis underpowered |
| **OVERALL** | **5.5/10** | Innovative framework with principled design; statistical rigor needs substantial improvement in bootstrap resolution, confidence intervals, and formal inference for the multiplicative residual model |
