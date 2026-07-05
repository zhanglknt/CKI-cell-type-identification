"""
Generate English Supplementary Materials DOCX with continuous line numbers.
Replaces the Chinese supplementary with English translation in Chinese-researcher style.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from lxml import etree

doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.5

# Page margins (NAR: 2.5cm)
for sec in doc.sections:
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)

# Heading styles
for lvl, size in [(1, 16), (2, 14), (3, 12)]:
    hs = doc.styles[f'Heading {lvl}']
    hs.font.name = 'Arial'
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)


def add_heading(text, level=1):
    return doc.add_heading(text, level=level)


def add_para(text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


# ===== TITLE PAGE =====
add_heading('Supplementary Materials', 1)
add_para('CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptional Reprogramming')
add_para('Li Zhang')
add_para('')

add_heading('Table of Contents', 2)
toc = [
    'Supplementary Note 1: CKI Mathematical Derivation',
    'Supplementary Note 2: CKI Algorithm Pseudocode',
    'Supplementary Note 3: Statistical Testing Details',
    'Supplementary Note 4: Dataset Quality Control and Filtering Criteria',
    'Supplementary Table 1: Parameter Sweep Results (Phase 3.2)',
    'Supplementary Table 2: Cross-Organ Conservation Data (Phase 3.5)',
    'Supplementary Table 3: Human Brain Non-neuronal Cell Regional CKI Data',
    'Supplementary Table 4: Inter-regional Cell Migration Candidate Data',
    'Supplementary Data 1: Complete Analysis Script Index',
]
for item in toc:
    add_para(item)

doc.add_page_break()

# ===== SN1: Mathematical Derivation =====
add_heading('Supplementary Note 1: CKI Mathematical Derivation', 2)

add_para('1.1 Jensen-Shannon Divergence', bold=True)
add_para(
    'The Jensen-Shannon (JS) divergence is a symmetrized and smoothed version of the '
    'Kullback-Leibler divergence. For two probability vectors p and q: '
    'JS(p, q) = 1/2 D(p||m) + 1/2 D(q||m), where m = 1/2(p+q), '
    'and D(p||q) = \u03a3 p_i log2(p_i/q_i). When using base-2 logarithms, '
    'the JS divergence is bounded in [0, 1]. This bound is important for interpreting '
    'omega: when both k_n and k_f approach 1, omega = k_f/k_n may still vary, '
    'and in practice omega is capped at 1,000. Before CKI computation, softmax '
    'normalization is applied to convert raw expression vectors into probability '
    'distributions: softmax(x)_i = exp(x_i)/\u03a3exp(x_j).'
)

add_para('1.2 Neutral Drift Rate k_n', bold=True)
add_para(
    'Housekeeping (HK) genes are defined as genes that maintain stable expression '
    'across cell types and conditions. Let H = {g1, ..., gM} be the set of HK gene '
    'indices. Given pseudobulk vectors \u03bc_A and \u03bc_B (length G, total number of genes), '
    'the neutral drift rate is: k_n = JS(softmax(\u03bc_A[H]), softmax(\u03bc_B[H])). '
    'Rationale: HK genes should not exhibit systematic differences between biologically '
    'identical cell populations. The JS divergence observed on HK genes therefore reflects '
    'neutral noise: technical variation, stochastic transcriptional bursting, and '
    'individual-level physiological differences. k_n thus provides an internal neutral '
    'baseline, analogous to Ks (synonymous substitution rate) in molecular evolution. '
    'HK gene set selection: CKI employs data-driven automatic detection of HK genes '
    '(joint criteria: detection rate > 0.9 and CV < 30th percentile), supplemented by '
    'the HRT Atlas v1.0 consensus set (1,130 human-mouse conserved HK genes) as an optional '
    'enhancement. Sensitivity analysis indicates that CKI results are robust to HK set '
    'selection: using the top 10% lowest-variance genes as an alternative neutral set '
    'yields omega correlations of r > 0.95.'
)

add_para('1.3 Functional Conversion Rate k_f', bold=True)
add_para(
    'Identity genes I are defined as genes that capture cell-type-specific functional '
    'programs. In the default configuration (w1 = 1.0, w2 = 0.0), I consists of the '
    'top-N highly variable genes (HVG), excluding HK genes. The functional conversion '
    'rate is: k_f = JS(softmax(\u03bc_A[I]), softmax(\u03bc_B[I])). Extended configurations '
    'can incorporate additional gene sets: (1) regulon activity genes \u2014 genes enriched '
    'for cell-type-specific transcription factor motifs; (2) pathway enrichment genes '
    '\u2014 genes from MSigDB pathways differentially active between the two groups; '
    '(3) macro-gene embeddings \u2014 gene-level embeddings from protein language models '
    '(e.g., ESM-2). These extensions use a weighted formulation: '
    'k_f = w1*JS(HVG) + w2*JS(pathway) + w3*JS(macro). Parameter sweep (Phase 3.2) '
    'showed that the pure identity gene configuration (w1=1.0, w2=w3=0.0) achieved '
    'optimal cell type discrimination (AUC = 0.786); this was therefore adopted as '
    'the default scheme.'
)

add_para('1.4 Omega Ratio and Its Interpretation', bold=True)
add_para(
    'omega = k_f/k_n. Interpretation follows a Ka/Ks analogy: '
    'omega ~ 1: the observed transcriptomic difference is consistent with neutral '
    'expectation, with no evidence of selective reprogramming; '
    'omega >> 1: functional divergence exceeds neutral drift, indicating evidence of '
    'selective transcriptional reprogramming; '
    'omega << 1: functional constraint, the two groups are more similar in functional '
    'genes than expected from neutral drift (rare in practice). '
    'The Ka/Ks analogy is structurally similar but mathematically non-equivalent. '
    'Key differences: (1) Ka/Ks operates on sequence alignments with explicit codon '
    'models, while CKI operates on continuous expression vectors; (2) the neutral '
    'reference in Ka/Ks has a mechanistic basis in the genetic code (synonymous changes '
    'are assumed neutral), whereas HK genes in CKI are empirically defined; (3) Ka/Ks '
    'uses explicit evolutionary models (e.g., PAML), while CKI uses empirical bootstrap '
    'inference.'
)

add_para('1.5 Bootstrap Permutation Test', bold=True)
add_para(
    'Statistical inference is performed by generating a null distribution of omega '
    'under the null hypothesis that the two cell populations are drawn from the same '
    'distribution. Procedure: (1) Annotate all cells in the pooled dataset with their '
    'original group labels (A or B); (2) Randomly permute labels B times (default '
    'B=1,000), recomputing pseudobulk vectors and omega_null each time; '
    '(3) Empirical P-value = (count(omega_null >= omega_obs) + 1)/(B + 1), with the '
    '+1 term avoiding P = 0; (4) Effect size: Cohen\'s d = (omega_obs - '
    'mean(omega_null))/sd(omega_null). Note: Benjamini-Hochberg FDR correction is NOT '
    'systematically applied in the current analyses; all reported P-values are raw '
    'bootstrap P-values. '
    'Confidence intervals for omega are obtained via percentile bootstrap: the 2.5th '
    'and 97.5th percentiles of the null distribution.'
)

add_para('1.6 Pseudobulk Construction', bold=True)
add_para(
    'Raw count matrices X (cells x genes) are preprocessed as follows: '
    '(1) Library size normalization: X_norm = 10,000 * (X/colSums(X)); '
    '(2) log1p transformation: X_log = log1p(X_norm), stabilizing variance and reducing '
    'the influence of high-expression outliers; (3) Pseudobulk: mu = column-wise mean '
    'of X_log for all cells with the same cell type annotation, with a minimum of 10 '
    'cells per group. For TCGA bulk RNA-seq data, FPKM normalization is used instead: '
    'FPKM values from GDC, followed by log2(x+1) transformation. No pseudobulk step '
    'is needed as each sample is already a bulk expression profile.'
)

doc.add_page_break()

# ===== SN2: Algorithm Pseudocode =====
add_heading('Supplementary Note 2: CKI Algorithm Pseudocode', 2)
add_para('Algorithm 1: CKI Core Computation', bold=True)
add_para(
    'Input: Two cell populations A and B (expression matrices), HK gene set H, '
    'identity gene set I (default top-N HVG excluding H). '
    'Output: omega, P-value, Cohen\'s d, null distribution.'
)
pseudo = [
    ' 1. X_A, X_B <- library-normalize and log1p-transform A and B',
    ' 2. mu_A <- mean(X_A, axis=0); mu_B <- mean(X_B, axis=0)  // pseudobulk',
    ' 3. mu_A_H <- mu_A[H]; mu_B_H <- mu_B[H]',
    ' 4. k_n <- JS_divergence(softmax(mu_A_H), softmax(mu_B_H))',
    ' 5. mu_A_I <- mu_A[I]; mu_B_I <- mu_B[I]',
    ' 6. k_f <- JS_divergence(softmax(mu_A_I), softmax(mu_B_I))',
    ' 7. omega <- k_f / k_n  // capped at 1,000',
    ' 8. // Bootstrap',
    ' 9. labels <- concatenate([A]*n_A, [B]*n_B)',
    '10. for b = 1 to B (default 1,000):',
    '11.     labels_perm <- random_permutation(labels)',
    '12.     A_perm, B_perm <- split by labels_perm',
    '13.     omega_null[b] <- CKI_core(A_perm, B_perm, H, I)',
    '14. // Inference',
    '15. P <- (count(omega_null >= omega) + 1) / (B + 1)',
    '16. d <- (omega - mean(omega_null)) / sd(omega_null)',
]
for line in pseudo:
    p = add_para(line)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(0)

add_para('')
add_para('Algorithm 2: Pairwise Identity Gene Selection (Tabula Sapiens Extension)', bold=True)
add_para(
    'Unlike Tabula Muris (global HVG set), Tabula Sapiens employs pairwise identity '
    'gene selection to avoid dilution of HVG across 99 cell types.'
)
pseudo2 = [
    'Input: Pseudobulk vectors mu_A, mu_B; HK set H; top-N parameter N (default 200)',
    '1. Delta <- |mu_A - mu_B|  // per-gene absolute expression difference',
    '2. I <- indices of top-N genes ranked by descending Delta, excluding H',
    '3. k_f <- JS(softmax(mu_A[I]), softmax(mu_B[I]))',
    '',
    'Note: k_n uses the global HK set (same for all pairs); k_f uses pairwise top-N genes.',
]
for line in pseudo2:
    p = add_para(line)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(0)

doc.add_page_break()

# ===== SN3: Statistical Testing =====
add_heading('Supplementary Note 3: Statistical Testing Details', 2)
add_para('3.1 Tests Performed and Correction Strategy', bold=True)
add_para(
    'The following statistical tests were used in this study: Mann-Whitney U test '
    '(two-sided) for independent comparisons between two groups; Kruskal-Wallis test '
    'for multi-group comparisons (e.g., BRCA PAM50 subtypes); Jonckheere-Terpstra trend '
    'test for ordered categorical variables (e.g., LIHC Edmondson grade); Spearman rank '
    'correlation for correlations between metrics; Bootstrap permutation test (B=1,000) '
    'for CKI omega significance inference; ROC-AUC for cell type classification '
    'performance assessment.'
)

add_para('3.2 Bootstrap Details', bold=True)
add_para(
    'Bootstrap iterations: B=1,000 for all primary results (B=500 used for the Phase 3.2 '
    'parameter sweep). The empirical P-value formula uses a +1 pseudocount in both '
    'numerator and denominator to avoid zero P-values. '
    'Cohen\'s d interpretation: d < 0.2 = negligible; 0.2-0.5 = small; '
    '0.5-0.8 = medium; > 0.8 = large. In CKI results, d values are typically > 1.0 for '
    'significant comparisons, indicating large effect sizes.'
)

add_para('3.3 Note on Multiple Testing Correction', bold=True)
add_para(
    'Note: Benjamini-Hochberg FDR correction is NOT systematically applied in the '
    'current analyses. All reported significance judgments are based on raw bootstrap '
    'P-values (P < 0.05). Effect sizes (Cohen\'s d) are consistently large '
    '(typically d > 1.0), providing complementary evidence strength. '
    'TCGA stratified analyses '
    '(BRCA PAM50, LIHC Edmondson) involve a small number of comparisons (4-5 groups), '
    'and omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) are used without additional '
    'correction beyond the omnibus P-value.'
)

add_para('3.4 Reporting Conventions', bold=True)
add_para(
    'Summary statistics are reported as mean +/- standard deviation (range) or median '
    '[interquartile range]. Boxplots display: median (center line), IQR (box), '
    '1.5x IQR (whiskers), with data points beyond the whiskers shown as outliers. '
    'All P-values are two-sided unless otherwise noted. Correlation coefficients '
    '(Spearman rho) are reported with P-values. Effect sizes (Cohen\'s d) are reported '
    'for all significant omega comparisons.'
)

doc.add_page_break()

# ===== SN4: QC and Filtering =====
add_heading('Supplementary Note 4: Dataset Quality Control and Filtering Criteria', 2)

add_para('4.1 Tabula Muris FACS (Mouse)', bold=True)
add_para(
    'Downloaded from GEO (GSE109774). FACS-sorted cells (not droplet-based) were used '
    'to ensure high per-cell gene detection. QC filtering: cells with < 500 detected '
    'genes were removed; cells with > 10% mitochondrial gene expression were removed; '
    'genes detected in < 3 cells were removed. Result: 15,057 cells x 22,308 genes '
    '(post-QC). Cell type annotation: 32 cell type entries with >= 10 cells per group '
    'were retained for pseudobulk construction, spanning 6 organs (Liver, Kidney, '
    'Spleen, Lung, Heart, Bone Marrow).'
)

add_para('4.2 Tabula Sapiens (Human)', bold=True)
add_para(
    'Downloaded from CZ CELLxGENE Discover. QC filtering: cells with < 200 detected '
    'genes were removed; cells with > 20% mitochondrial gene expression were removed. '
    'Result: 108,136 cells retained (6 h5ad files total), with 51,852 genes (filtered from the '
    'original 58,870). Cell type entries: 99 entries across 6 organs (Liver, Kidney, '
    'Heart, Bone Marrow, Spleen, Lung). Cell types included in pairwise omega analysis '
    'were required to have >= 10 cells in at least one donor. Pairwise identity gene '
    'selection (top-200 genes by |Delta expression| ranking) ensures that each comparison '
    'uses the most informative genes for that specific pair. Human HK genes: data-driven '
    'automatic detection (joint criteria), supplemented with 1,129 genes from HRT Atlas '
    'v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog '
    'was excluded).'
)

add_para('4.3 TCGA Bulk RNA-seq', bold=True)
add_para(
    'Data were obtained from the NCI Genomic Data Commons. Five cancer types were selected: '
    'LUAD (515 tumor + 59 normal), LUSC (501 + 51), LIHC (371 + 50), KIRC (533 + 72), '
    'BRCA (1,093 + 113), totaling n = 10,535 samples. Normalization: FPKM values from GDC, '
    'followed by log2(x+1) transformation. For paired analysis, tumor-normal pairs were '
    'matched by patient barcode (TCGA-XX-XXXX format). Clinical metadata for stratified '
    'analyses were obtained from GDC (via the TCGAbiolinks R package) and the cBioPortal API.'
)

add_para('4.4 Highly Variable Gene (HVG) Selection', bold=True)
add_para(
    'Tabula Muris: Global HVG selection was performed using '
    'scanpy.pp.highly_variable_genes, with parameters flavor="seurat" and '
    'n_top_genes=2,000. The global HVG set was used for all pairwise comparisons '
    'in Phases 3.1-3.2. Tabula Sapiens: Pairwise HVG selection. For each cell type '
    'pair (CT_i, CT_j), the top-200 genes ranked by |mu_i - mu_j| (absolute log1p '
    'expression difference) were selected as identity genes, excluding HK genes. This '
    'avoids the dilution effect of HVG across comparisons involving 99 cell types. '
    'HVG count sensitivity: the parameter sweep (Phase 3.2) tested N_HVG in '
    '{50, 100, 200, 500, 1,000, 2,000}. The global scheme (mouse) achieved peak AUC '
    'at N=2,000, while the pairwise scheme (human) used N=200 to maintain discriminative '
    'power with computational efficiency.'
)

doc.add_page_break()

# ===== Supplementary Tables =====
add_heading('Supplementary Table 1: Parameter Sweep Results', 2)
add_para(
    'Phase 3.2 parameter sweep on Tabula Muris mouse data (n = 703 cell type pairs, '
    '6 organs). The pure identity gene configuration (w1 = 1.0, w2 = 0.0) achieved '
    'optimal cell type discrimination (AUC = 0.786). Data file: '
    'results/phase32_sweep_results.csv. Visualization: results/phase32_sweep_barplot.png.'
)

add_para('')
add_heading('Supplementary Table 2: Cross-Organ Conservation Data', 2)
add_para(
    'Complete dataset of 59 same-cell-type cross-organ pairs in Tabula Sapiens, '
    'including omega, Jensen-Shannon divergence, Spearman distance, Cosine distance, '
    'and Marker Jaccard distance values. Data file: '
    'results/phase35_cross_organ_conservation.csv.'
)

add_para('')
add_heading('Supplementary Table 3: Human Brain Non-neuronal Cell Regional CKI Data', 2)
add_para(
    'Complete results of CKI brain region analysis for non-neuronal cells from the '
    'Siletti et al. (2023) human brain atlas, comprising 31,764 pairwise cross-region '
    'comparisons across 10 cell types. Summary statistics for each cell type (omega mean, '
    'median, SD, range, k_n and k_f components) are provided in Supplementary Table 3. '
    'Raw data file: results/brain_region_omega.csv (31,764 rows). '
    'Summary file: results/brain_region_summary.csv (10-row summary). '
    'Analysis script: notebooks/27_brain_region_cki.py. '
    'Figure generation: notebooks/28_gen_fig6.py. '
    'Visualization output: results/figures_final/figure6_brain_regional_cki.png.'
)

add_para('')
add_heading('Supplementary Table 4: Inter-regional Cell Migration Candidate Data', 2)
add_para(
    'Results of multiplicative model-based detection of potential inter-regional cell '
    'migration candidates. Of the full 31,764 pairwise cross-region comparisons, 5,346 '
    'pairs (16.83%) were classified as migration candidates: 213 strong signals '
    '(residual < 0.3, omega < 15, within-pair rank = 1, pair median omega > 20), '
    '1,294 medium signals (residual < 0.5, omega < 25), and 3,839 weak signals '
    '(residual < 0.75, omega < 35). Top-5 strongest migration signals by cell type '
    '(ranked by residual): OPC MoRF-MoEN vs. MoSR (omega = 1.19, residual = 0.033), '
    'Astrocyte A23 vs. ITG (omega = 2.60, residual = 0.041), '
    'Oligodendrocyte A23 vs. SN (omega = 4.53, residual = 0.063), '
    'OPC GPi vs. PN (omega = 4.14, residual = 0.076), '
    'Vascular A44-A45 vs. VA (omega = 1.75, residual = 0.083). '
    'Complete candidate dataset: results/brain_migration/migration_candidates.csv '
    '(5,346 rows). Analysis script: notebooks/29_brain_migration_detection.py. '
    'Literature validation report: results/brain_migration/literature_validation_report.md.'
)

add_para('')
add_heading('Supplementary Data 1: Analysis Script Index', 2)
add_para(
    'Complete analysis scripts used in this study are organized in the notebooks/ '
    'directory of the GitHub repository (github.com/zhanglknt/CKI-cell-type-identification). '
    'The package can be installed via: pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git. '
    'Key scripts include: notebooks/20_main_analysis.py (core CKI pipeline), '
    'notebooks/21_tcga_analysis.py (TCGA pan-cancer analysis), '
    'notebooks/22_tabula_sapiens_analysis.py (Tabula Sapiens cross-organ analysis), '
    'notebooks/27_brain_region_cki.py (brain regional CKI analysis), '
    'notebooks/29_brain_migration_detection.py (migration candidate detection), '
    'and notebooks/30_nar_figures_final.py (NAR figure generation).'
)

# ===== Add line numbers (continuous, every line) =====
for sec in doc.sections:
    sect_pr = sec._sectPr
    ln_num = etree.SubElement(sect_pr, qn('w:lnNumType'))
    ln_num.set(qn('w:countBy'), '1')
    ln_num.set(qn('w:start'), '1')
    ln_num.set(qn('w:restart'), 'continuous')

out_path = 'results/NAR_Submission_Final/supplementary/CKI_NAR_Supplementary.docx'
doc.save(out_path)
print(f'Saved: {out_path}')
print(f'Paragraphs: {len(doc.paragraphs)}')
