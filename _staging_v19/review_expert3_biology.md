# Expert Review #3: Biological Interpretation

## Overall Assessment

CKI introduces a conceptually elegant framework for decomposing transcriptomic divergence into baseline (k_n) and functional (k_f) components, heuristically inspired by Ka/Ks. The authors are unusually honest about the mathematical limitations of this analogy, and the brain regional analysis—while overambitious in its initial framing as "migration detection"—contains compelling evidence for persistent developmental signatures in adult transcriptomes. However, several biological claims require stronger justification, particularly the neutrality assumption for housekeeping genes and the interpretation of TCGA cancer convergence. Overall, this is a novel and well-executed computational method with room for more nuanced biological interpretation.

**Score: 7.0 / 10**

---

## Strengths

- **S1. Genuine conceptual novelty.** The decomposition of transcriptomic divergence into baseline and functional components via an internal baseline (HK genes) has not been proposed before. The negative correlation with all four standard metrics (Manuscript, Results paragraph 52) convincingly demonstrates that ω captures an independent information dimension.

- **S2. Honest discussion of the Ka/Ks analogy.** The Discussion (Manuscript, paragraphs 91–93) explicitly acknowledges the mathematical non-equivalence with Ka/Ks—no shared mutation rate cancellation, no codon substitution model, a systematic k_f inflation (ω ≈ 6.67 for equivalent populations). This intellectual honesty is commendable and rare in computational methods papers.

- **S3. Clever use of OPCs as negative control.** The finding that OPCs—the most actively migrating cells in the adult CNS—yield 0 Strong signals among 5,671 comparisons (Manuscript, paragraphs 76–77) provides a powerful orthogonal validation that the multiplicative residual model detects fixed developmental signatures rather than ongoing cell motility.

- **S4. Biological plausibility of the brain ω gradient.** The 6.06-fold gradient from Bergmann glia (mean ω = 2.37) to astrocytes (mean ω = 14.36) (Manuscript, paragraph 69) aligns well with known cell biology: Bergmann glia are developmentally fixed with a constrained transcriptional program (Reeber et al., 2015), while astrocytes show extensive regional specialization in ion channels, neurotransmitter transporters, and secreted factors.

- **S5. Systematic literature cross-validation.** The authors cross-validated all 30 Strong signals against the developmental neuroscience literature (Manuscript, paragraphs 79–89), mapping each to a specific biological mechanism: developmental origin heterogeneity (oligodendrocytes), colonization route boundaries (microglia), compartmentalized developmental specification (astrocytes, vascular cells), and postnatal migration (perivascular fibroblasts). This is thorough and well-reasoned.

---

## Critical Issues (must fix before submission)

### C1. Housekeeping gene neutrality assumption requires stronger biological justification

- **Location:** Manuscript, Introduction paragraph 15; Materials and Methods paragraph 19; Discussion paragraph 91; Supplementary Note 1.2
- **Problem:** The entire CKI framework rests on the assumption that HK gene expression divergence represents "neutral" transcriptional variation. This analogy to synonymous sites in Ka/Ks is structurally elegant but biologically problematic. Unlike synonymous codons, which have a mechanistic basis for neutrality in the genetic code, HRT Atlas housekeeping genes are defined empirically by stable expression across tissues (Hounkpe et al., 2021). Several HK genes (GAPDH, ACTB, TUBB) are known to be under stabilizing selection at the protein level and may also be subject to selection on expression levels. The authors acknowledge this caveat in one sentence ("HK genes... may be subject to stabilizing selection on expression levels," Discussion paragraph 93), but this is insufficient. If HK gene expression is under stabilizing selection, then k_n captures not "neutral drift" but the combined effects of stabilizing selection on expression + technical noise + stochastic bursting. This fundamentally changes the interpretation of ω: ω ≫ 1 could mean either (a) functional genes diverge more than neutral expectation, or (b) functional genes diverge more than a heavily constrained baseline. The distinction matters enormously for the "selective transcriptomic remodeling" framing. The sensitivity analysis (r > 0.95 with lowest-10%-variance genes) addresses robustness to gene set choice but does not address the deeper biological question of whether any gene set can serve as a truly neutral expression baseline.

- **Fix:** (1) Add a dedicated paragraph in the Discussion (or a Supplementary Note) comparing the biological properties of HRT Atlas HK genes with alternative "neutral" gene sets: lowest-variance genes, genes with minimal cell-type-specific expression, and genes with low regulatory complexity (few enhancers, low TF binding site density). Provide evidence that these different neutral sets yield similar ω rankings, not just correlated ω values. (2) Explicitly reframe the interpretation: rather than claiming HK genes represent "neutral" expression variation, argue that they represent a **maximally constrained baseline** — the smallest transcriptomic divergence achievable between two populations given unavoidable technical and biological noise. Under this interpretation, ω quantifies how much functional divergence exceeds this minimal-possible baseline. (3) Cite relevant literature on stabilizing selection on expression levels (e.g., Bedford & Hartl, 2009; Gilad et al., 2006; Romero et al., 2012).

### C2. The term "migration" is misleading; most Strong signals reflect developmental history, not cell motility

- **Location:** Manuscript, Results paragraphs 72–75; Abstract line 16; Cover Letter line 18
- **Problem:** The manuscript frames the multiplicative residual model as "migration inference" or "migration detection" (Abstract: "a single postnatal migration event"; Cover Letter: "identifying 30 cell-type-specific developmental origin signatures"). But in the detailed Results, the authors themselves reclassify all but 1 of the 30 Strong signals as reflecting developmental history rather than migration: 10 oligodendrocyte signals → developmental origin heterogeneity (not migration); 10 microglia signals → colonization wave boundaries (not migration); 6 astrocyte signals → developmental astrogenesis (not migration); 3 vascular signals → BBB regional specification (not migration). Only the fibroblast A40–SN signal (1/30) is attributed to postnatal migration. The Abstract says "detecting... a single postnatal migration event" — this acknowledges the reclassification but still uses "migration" as the framing term. A casual reader of the abstract will take away the wrong message.

- **Fix:** (1) Rename the model from "migration inference" / "migration detection" to **"developmental signature detection"** throughout the manuscript, including the Abstract and Cover Letter. This is more accurate and avoids claiming something the data do not support. (2) Keep the migration terminology only for the fibroblast result, explicitly labeled as the sole instance where postnatal migration is the most parsimonious explanation. (3) Update Figure 6D-E labels and the Supplementary Table 4 title to reflect the "developmental signature" framing.

### C3. TCGA "convergence" interpretation overreaches the data

- **Location:** Manuscript, Results paragraph 57–58; Discussion paragraph 95
- **Problem:** The central TCGA claim—"tumors are more transcriptionally homogeneous than normal tissues"—is stated as a finding (Results paragraph 58: "A notable finding was that tumors are more transcriptionally homogeneous than normal tissues"), but the interpretation is speculative and lacks mechanistic grounding. The NN/TT ω ratio > 1.0 could arise from multiple mechanisms, most of which are not directly about transcriptional convergence: (a) normal samples come from diverse anatomical substructures, while bulk tumors represent large, relatively homogeneous cell populations dominated by one clone; (b) TCGA normal samples are often peritumoral tissue, which may have inflammation-driven transcriptional heterogeneity; (c) the tumor samples are enriched for a single cell type (malignant epithelial cells), while normal tissue samples contain diverse cell-type mixtures (epithelial, stromal, immune, endothelial); (d) technical factors: tumor samples typically have higher RNA integrity and read depth. The Discussion (paragraph 95) acknowledges none of these alternative explanations, jumping directly to therapeutic implications ("common vulnerabilities that transcend individual mutations").

- **Fix:** (1) Add a paragraph in the Discussion explicitly listing alternative explanations for NN/TT > 1.0, including cell-type composition differences, peritumoral inflammation, sampling depth, and RNA quality differences. (2) Qualify the convergence claim: "These results are consistent with transcriptional convergence but could also reflect differences in sample cellular composition and must be validated with single-cell resolution TCGA data." (3) Remove or heavily qualify the therapeutic speculation in Discussion paragraph 95. (4) Consider a cell-type deconvolution analysis (e.g., CIBERSORTx, EPIC) to estimate whether NN/TT differences persist after accounting for cell-type proportions.

---

## Major Issues (should fix)

### M1. Limited cross-species analysis undermines the evolutionary biology framing

- **Location:** Manuscript, Abstract; Discussion paragraph 97; Cover Letter paragraph 18
- **Problem:** The manuscript invokes evolutionary biology extensively (Ka/Ks analogy throughout, "evolutionary cell biology" as a future direction in Discussion paragraph 98), yet cross-species analysis is nearly absent from the main text. Table 2 (cross-organ conservation) and Figure 5 are based entirely on Tabula Sapiens human data. The mouse data (Tabula Muris) is used only for calibration and parameter sweeping. There is no systematic comparison of ω values between mouse and human for shared cell types. The Cover Letter promises "cross-dataset consistency," but the manuscript proper contains no direct cross-species ω comparison. Given the evolutionary framing, readers will expect at minimum a human-mouse ω comparison showing which cell types show conserved vs. divergent functional divergence patterns across species—this is a missed opportunity.

- **Fix:** (1) Add a cross-species analysis as a major result or a prominent Supplementary Figure. Tabula Muris and Tabula Sapiens share several organs and cell types (macrophages, B cells, T cells, endothelial cells, fibroblasts). Compute ω for the same cell-type pairs in both species and test whether cross-species ω rankings are correlated. (2) If cross-species consistency is demonstrated, add this as a main-text result. If not, reduce the emphasis on evolutionary biology in the Abstract and Introduction.

### M2. Method comparison is limited to generic distance metrics; no comparison with biologically aware methods

- **Location:** Manuscript, Materials and Methods paragraph 29 (Method comparison); Introduction paragraph 13
- **Problem:** The method comparison (Manuscript, paragraph 52; Table 1) benchmarks CKI against four standard distance metrics: raw JS divergence, Spearman distance, cosine distance, and marker Jaccard distance. These are all generic metrics. However, the Introduction explicitly positions CKI in relation to single-cell integration and batch correction methods: Harmony (ref 1), scVI (ref 2), and SATURN (ref 3) are introduced as methods that "remove such nuisance variation" (paragraph 13). The logical reader expectation is that CKI will be compared to these biologically motivated methods. But they are never compared—not in performance, not conceptually, not even in a supplementary analysis. Similarly, CACIMAR (ref 22) is mentioned in Discussion as a complementary method, but its cross-species conservation scoring is never compared to CKI ω rankings. Without this comparison, readers cannot assess whether CKI adds value beyond existing single-cell analysis frameworks.

- **Fix:** (1) Add a Supplementary Figure comparing CKI ω rankings with (a) scVI latent-space distances, (b) SATURN cross-species embedding distances (if computationally feasible, perhaps for a subset of cell types), and (c) CACIMAR conservation scores. (2) At minimum, add a Discussion paragraph conceptually comparing what CKI measures versus what integration/batch-correction methods remove: CKI explicitly separates baseline and functional variation, while integration methods aim to remove baseline variation entirely. Clarify whether these are complementary or competing approaches.

### M3. The 30 Strong signals lack false discovery rate control appropriate for 31,764 tests

- **Location:** Manuscript, Materials and Methods paragraph 31; Results paragraph 75; Supplementary Note 3.3
- **Problem:** The multiplicative residual model identifies 30 Strong candidates from 31,764 cross-region comparisons using hard thresholds (residual < 0.3, ω < 15, lowest ω in pair). While Benjamini-Hochberg FDR correction is applied to the bootstrap P-values (Supplementary Note 3.3), the multiplicative residual thresholds are not statistically calibrated. The 0.09% hit rate (30/31,764) is plausibly below chance expectation given three simultaneous threshold criteria, but no empirical null distribution is presented. Without a proper FDR assessment (e.g., permuting cell-type labels and recomputing residuals), the 30 Strong signals remain hypothesis-generating—which the authors acknowledge in paragraph 97—but the Acknowledgments section calls them "significant discoveries" (Supplementary Note 3.3: "candidates passing FDR < 0.05 are reported as significant discoveries").

- **Fix:** (1) Generate an empirical null distribution for multiplicative residuals by permuting cell-type labels across regions and recomputing the residual model. Report the expected number of Strong candidates under permutation. (2) If the observed 30 significantly exceeds the null expectation, present this as formal FDR. (3) If not feasible for 31,764 comparisons, present a bootstrap-based FDR for at least the 7,842 pairs with residual < 0.75. (4) Harmonize the language: either call them "significant discoveries" (after proper FDR) or "hypothesis-generating candidates" consistently throughout.

### M4. Biological interpretation of PAM50 and Edmondson grade results is mechanistically shallow

- **Location:** Manuscript, Results paragraph 60; Discussion paragraph 95
- **Problem:** The clinical severity analysis shows that ω decreases with tumor aggressiveness: Luminal A > Luminal B > HER2 > Basal-like (breast cancer), and G1 > G2 > G3 > G4 (liver cancer). The Discussion (paragraph 95) interprets this as "aggressive subtypes show the strongest convergence, consistent with proliferation programs overriding tissue-specific expression." This interpretation is plausible but ignores well-known alternative explanations: Basal-like and high-grade tumors have higher proliferation rates, which means a larger fraction of the transcriptome is devoted to cell-cycle genes. Cell-cycle genes are a shared expression program across all cancers — high ω reflects functional divergence from normal, and if both Basal-like tumors converge on the same cell-cycle-dominant expression state, their intratumoral ω would indeed decrease. But this is a trivial consequence of proliferation, not a novel finding about selective transcriptomic remodeling.

- **Fix:** (1) Add cell-cycle signature scoring (e.g., using Seurat's CellCycleScoring or MSigDB Hallmark G2M checkpoint genes) to each TCGA sample. Test whether intratumoral ω correlates with proliferation signature strength after controlling for subtype/grade. (2) If ω differences are fully explained by proliferation, state this clearly. If ω captures information beyond proliferation, highlight this as a genuine finding. (3) Add a mechanistic discussion of *why* more aggressive tumors show stronger convergence — is it proliferation-driven, or is there a genuine reduction in transcriptional plasticity?

### M5. Cross-organ ω values rely on extremely small sample sizes for many cell types

- **Location:** Manuscript, Table 2; Results paragraph 64–66
- **Problem:** Several cell types in the cross-organ conservation analysis have n = 1 or n = 3 comparisons (B cells: n = 1; Smooth muscle cells: n = 1; Memory B cells: n = 1; Endothelial cells: n = 3). The authors acknowledge this limitation (paragraph 65: "small sample sizes... should be interpreted with appropriate caution"), but the Table 2 presentation (ranking from most to least conserved) visually implies biological meaning for all entries, including those based on single comparisons. A reader skimming Table 2 might conclude that "B cells are the most conserved cell type" when this is based on a single inter-organ pair that may not generalize.

- **Fix:** (1) Either remove cell types with n < 3 from Table 2 and Figure 5, or visually distinguish them (e.g., gray text, different symbol) with a clear note that rankings based on n < 3 are unreliable. (2) Consider a meta-analysis approach: for cell types with only 1–3 pairs, report the individual ω values rather than a mean, so readers can assess the range. (3) Add confidence intervals (bootstrap) for means to visually represent uncertainty in the ranking.

---

## Minor Issues (suggestions)

### m1. The calibration ω = 6.67 needs a biological explanation, not just a methodological one

- **Location:** Manuscript, Results paragraph 47; Discussion paragraph 91
- **Problem:** The calibration experiment shows that split-half equivalent populations yield mean ω = 6.67 (range 1.59–12.16). The authors correctly identify HVG selection as the cause (Discussion paragraph 91, 97). But ω = 6.67 is a large departure from the theoretical ideal of ω = 1, and the biological significance is glossed over. If HVG selection introduces a ~6.7-fold bias, then ω values of 50–100 in the cancer analysis should be interpreted relative to this inflated baseline (effective "neutral" ω ≈ 6.67), not relative to 1. The authors partially address this by stating ω = 1 is never reached in practice, but they should explicitly calibrate all ω values against the empirical baseline throughout the Results.

- **Fix:** (1) Add a horizontal dashed line at ω = 6.67 (empirical calibration baseline) on all ω distribution figures (Figures 2E, 3B, 4B). (2) In the Results text, report ω values relative to the calibration baseline where relevant: e.g., "astrocytes showed ω = 14.36, approximately 2.2-fold above the calibration baseline." (3) Discuss whether ω-calibrated = ω_observed / ω_calibration would improve cross-dataset comparability.

### m2. The TCGA paired analysis is underpowered to the point of being misleading

- **Location:** Manuscript, Results paragraph 59; Reproducibility Guide Section 4.3
- **Problem:** The paired tumor-normal analysis uses n = 2–5 patients per cancer type. The authors report "paired/unpaired ratio = 0.99–3.25, Mann-Whitney P = 0.024 for LIHC, not significant for others" and correctly note that "the small number of patients... limits statistical power." However, presenting these ratios at all—especially the 3.25-fold ratio for LIHC—invites readers to overinterpret numerical differences that have no statistical support. The Mann-Whitney U test with n = 2 is effectively meaningless.

- **Fix:** (1) Move the paired analysis entirely to Supplementary Materials, or (2) Remove it from the main text and state that "paired analysis was attempted but sample sizes (n = 2–5 per cancer type) preclude meaningful statistical inference." Do not present numerical results from analyses with n < 5.

### m3. The "cell-type classifier" framing in Table 1 is confusing

- **Location:** Manuscript, Table 1; Results paragraph 55; Supplementary Figure S4
- **Problem:** CKI is evaluated as a cell-type classifier (AUC = 0.716) and compared to standard metrics. But the authors explicitly state that CKI "is a divergence index, not a classifier—and this is by design" (Discussion paragraph 92). Presenting classification AUC as a performance metric (Table 1) and then dismissing it as irrelevant to CKI's purpose creates unnecessary confusion. Readers unfamiliar with CKI may interpret the lower AUC as a weakness rather than a design feature.

- **Fix:** (1) Move Table 1 to Supplementary and de-emphasize the classification framing in the main text. (2) Replace it with a metric that better reflects CKI's intended use: e.g., ability to identify functionally divergent populations that share cell-type labels (cross-organ pairs), or ability to detect known functional specializations. (3) In the main text, state clearly: "CKI's lower classification AUC is expected because it down-weights the transcriptomic features that define cell-type identity in favor of capturing functional specialization."

### m4. Missing reference: Gilad et al. on expression evolution

- **Location:** Manuscript, Discussion paragraph 93, 97, 98
- **Problem:** The Discussion mentions "Ornstein-Uhlenbeck models that dominate expression evolution analysis" (paragraph 93) but cites no references for this literature. Integrating CKI with evolutionary models of gene expression (OU models, phylogenetic ANOVA, expression variance decomposition) is raised as a future direction, but readers need at minimum 2–3 references to this extensive literature.

- **Fix:** Add citations: (1) Bedford & Hartl, "Optimization of gene expression by natural selection," *PNAS* 2009. (2) Rohlfs et al., "Modeling gene expression evolution with an extended Ornstein-Uhlenbeck process," *Syst. Biol.* 2014. (3) Brawand et al., "The evolution of gene expression levels in mammalian organs," *Nature* 2011.

### m5. Astrocyte-paragraph regional specialization claims need citations

- **Location:** Manuscript, Results paragraph 70: "astrocytes express region-specific sets of ion channels, neurotransmitter transporters, and secreted factors"
- **Problem:** This sentence summarizes extensive astrocyte biology without citations. Readers may challenge this claim; it needs support from the literature.

- **Fix:** Add 2–3 primary citations, e.g.: (1) Chai et al., "Neural circuit-specialized astrocytes," *Neuron* 2017. (2) John Lin et al., "Identification of diverse astrocyte populations and their malignant analogs," *Nat. Neurosci.* 2017. (3) Batiuk et al., "An immunoaffinity-based method for isolating ultrapure adult astrocytes," *Neuron* 2017.

### m6. The HRT Atlas reference definition of HK genes could be more clearly stated

- **Location:** Manuscript, Materials and Methods paragraph 19; Supplementary Note 1.2; Reproducibility Guide Section 3.1
- **Problem:** The manuscript uses HRT Atlas v1.0 as the HK gene reference but provides inconsistent descriptions. Paragraph 19 says "1,130 human-mouse conserved HK genes." Supplementary Note 1.2 says "1,130 human-mouse conserved HK genes (HRT Atlas v1.0 reference)." The Reproducibility Guide Section 3.1 says "1,130 human-mouse conserved HK genes (identical to cki/data/hrt_atlas.csv)." But the mouse analysis (paragraph 24) may use a different subset depending on ortholog mapping. It's unclear whether all analyses use exactly the same 1,130 genes or different subsets after ortholog mapping and gene symbol matching.

- **Fix:** In Materials and Methods paragraph 19, add a sentence like: "After intersecting with each dataset's gene annotation, the effective HK gene set sizes were: 1,115 (brain atlas), 1,129 (Tabula Sapiens), 1,130 (TCGA), and [N] (Tabula Muris mouse orthologs)." This transparency helps readers assess gene set overlap across analyses.

### m7. The "selective transcriptomic remodeling" terminology should be softened

- **Location:** Manuscript, title; Abstract; throughout
- **Problem:** The title and abstract use "selective transcriptomic remodeling," which carries evolutionary connotations of Darwinian selection. The authors correctly disclaim this in the Discussion (paragraphs 91–93: "CKI is a heuristic index, not a formal measure of Darwinian selection"), but the disconnect between the framing and the disclaimers creates ambiguity. A title emphasizing "baseline-normalized functional divergence" would be more accurate and equally compelling.

- **Fix:** Consider revising the title to: "CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Functional Transcriptomic Divergence." This retains the core concept while removing the unsubstantiated "selective" framing. Alternatively, use "selective" only in the sense of "selective [gene set] transcriptomic remodeling" rather than "selective [evolutionary] transcriptomic remodeling."

---

## Score Breakdown

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Biological Insight | 7/10 | Elegant conceptual framework; Ka/Ks analogy is well-motivated but mathematically imprecise; HK gene neutrality assumption needs stronger defense |
| Cell-Type Biology | 8/10 | 6.06-fold brain ω gradient and cross-organ rankings are biologically plausible; reclassification of migration signals into developmental mechanisms is thoughtful; small-n cell types weaken cross-organ analysis |
| Migration Inference | 6/10 | Multiplicative residual model is statistically creative; "migration" framing is misleading (29/30 reflect development, not migration); lacks empirical null for FDR; OPC negative control is the strongest validation |
| Cancer Biology | 5/10 | NN/TT finding is intriguing but alternative explanations (cellular composition, peritumoral inflammation, RNA quality) are unexplored; clinical severity results may be trivial consequences of proliferation; interpretation overreaches |
| Literature & Context | 7/10 | Covers core references for each biological domain; missing expression evolution literature (OU models, stabilizing selection on expression); method comparison with Harmony/scVI/SATURN is absent despite being introduced |
| **OVERALL** | **7.0/10** | A novel, well-executed method with honest discussion of limitations; biological interpretation is generally sound but several claims (TCGA convergence, migration detection, HK neutrality) require stronger justification or rephrasing |

---

## Summary for Authors

CKI represents a genuinely novel conceptual contribution to single-cell transcriptomics. The decomposition of transcriptomic divergence into baseline and functional components fills a gap that existing distance metrics do not address. The brain regional analysis—particularly the OPC negative control and the systematic literature cross-validation of all 30 Strong signals—is the strongest section of the paper and will resonate with developmental biologists. I encourage the authors to (1) strengthen the biological defense of the HK gene neutrality assumption; (2) reframe "migration detection" as "developmental signature detection" to match what the data actually show; (3) acknowledge alternative explanations for the TCGA convergence and PAM50 results; and (4) add cross-species comparisons to substantiate the evolutionary framing. With these revisions, CKI will make a substantial contribution to the field.
