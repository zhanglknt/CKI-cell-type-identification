/**
 * Generate Supplementary Methods: CKI Computational Reproducibility Guide
 * NAR-compliant DOCX with Arial font, same formatting as manuscript.
 */
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageBreak, PageNumber, TabStopType, TabStopPosition
} = require("docx");

const OUT = "C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Reproducibility_Guide.docx";
const FONT = "Arial";
const BLACK = "000000";
const SIZE = 20; // 10pt in half-points
const SIZE_SM = 18; // 9pt

function p(text, opts = {}) {
  const runs = [];
  if (opts.bold) {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || SIZE, bold: true, color: BLACK }));
  } else if (opts.italic) {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || SIZE, italics: true, color: BLACK }));
  } else {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || SIZE, color: BLACK }));
  }
  return new Paragraph({
    children: runs,
    spacing: { after: 60, line: 240 },
  });
}

function heading(text, level) {
  const sizes = { 1: 32, 2: 28, 3: 24 };
  const before = { 1: 240, 2: 180, 3: 120 };
  return new Paragraph({
    heading: level === 1 ? HeadingLevel.HEADING_1 : (level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3),
    children: [new TextRun({ text, font: FONT, size: sizes[level], bold: true, color: BLACK })],
    spacing: { before: before[level], after: 120 },
  });
}

function code(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Consolas", size: 18, color: BLACK })],
    spacing: { after: 40, line: 220 },
    indent: { left: 360 },
  });
}

// Table helper
const TBL_BASE = 9000; // total table width in DXA
const border = { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" };
const borders = { top: border, bottom: border, left: border, right: border };
const margins = { top: 60, bottom: 60, left: 100, right: 100 };

function tableHeader(cells, widths) {
  return new TableRow({
    children: cells.map((t, i) => new TableCell({
      borders,
      width: { size: widths[i], type: WidthType.DXA },
      margins,
      shading: { fill: "E8E8E8", type: ShadingType.CLEAR },
      children: [new Paragraph({
        children: [new TextRun({ text: t, font: FONT, size: SIZE_SM, bold: true, color: BLACK })],
      })],
    })),
  });
}

function tableRow(cells, widths) {
  return new TableRow({
    children: cells.map((t, i) => new TableCell({
      borders,
      width: { size: widths[i], type: WidthType.DXA },
      margins,
      children: [new Paragraph({
        children: [new TextRun({ text: t, font: FONT, size: SIZE_SM, color: BLACK })],
      })],
    })),
  });
}

// ============================================================
// Build document
// ============================================================
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT, size: SIZE, color: BLACK } },
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 120, after: 60 }, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [new TextRun({ text: "CKI Computational Reproducibility Guide", font: FONT, size: SIZE_SM, italics: true, color: "888888" })],
          alignment: AlignmentType.RIGHT,
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "Page ", font: FONT, size: SIZE_SM, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE_SM, color: "888888" }),
          ],
          alignment: AlignmentType.CENTER,
        })],
      }),
    },
    children: [
      // ===== Title =====
      new Paragraph({
        heading: HeadingLevel.TITLE,
        children: [new TextRun({ text: "Supplementary Methods:\nCKI Computational Reproducibility Guide", font: FONT, size: 36, bold: true, color: BLACK })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
      }),

      // Authors
      new Paragraph({
        children: [new TextRun({ text: "Xianming Wu", font: FONT, size: SIZE, italics: true, color: BLACK }),
                   new TextRun({ text: "1", font: FONT, size: 18, color: BLACK, superScript: true }),
                   new TextRun({ text: ", ", font: FONT, size: SIZE, color: BLACK }),
                   new TextRun({ text: "Li Zhang", font: FONT, size: SIZE, italics: true, color: BLACK }),
                   new TextRun({ text: "1,2,*", font: FONT, size: 18, color: BLACK, superScript: true })],
        alignment: AlignmentType.CENTER,
      }),
      new Paragraph({
        children: [new TextRun({ text: "1", font: FONT, size: 18, color: BLACK, superScript: true }),
                   new TextRun({ text: " Institute of Blood Transfusion, Chinese Academy of Medical Sciences & Peking Union Medical College, Chengdu, China", font: FONT, size: SIZE, color: BLACK })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "2", font: FONT, size: 18, color: BLACK, superScript: true }),
                   new TextRun({ text: " Chinese Institute for Brain Research, Beijing, China", font: FONT, size: SIZE, color: BLACK })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "* Correspondence: knightz@pumc.edu.cn", font: FONT, size: SIZE, italics: true, color: BLACK })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 300 },
      }),

      // ========================================================
      // 1. SOFTWARE ENVIRONMENT
      // ========================================================
      heading("1. Software Environment", 2),

      heading("1.1 Python and Core Packages (verified environment)", 3),
      code("Python:              3.13.12  (MSC v.1944 64 bit, AMD64)"),
      code("numpy:               2.4.6"),
      code("scipy:               1.17.1"),
      code("scanpy:              1.10.4"),
      code("pandas:              2.3.3"),
      code("matplotlib:          3.10.9"),
      code("scikit-learn:        1.8.0"),
      code("python-docx:         1.2.0"),

      heading("1.2 CKI Package", 3),
      p("Version: 0.3.1 (editable install from project root)"),
      p("Repository: https://github.com/zhanglknt/CKI-cell-type-identification"),
      p("Install (editable, recommended):"),
      code("cd <project_root>"),
      code("pip install -e ."),
      p("Install (fixed dependencies):"),
      code("pip install -r requirements.txt"),

      heading("1.3 System Requirements", 3),
      code("Operating system:    Windows 10/11 x64 (also tested Linux x86_64)"),
      code("Memory:              >= 32 GB RAM (TCGA matrix ~10 GB peak)"),
      code("Disk space:          >= 5 GB (for TPM data and intermediates)"),
      code("Network:             Internet for data downloads and cBioPortal API"),

      heading("1.4 Data Dependencies", 3),
      p("The cloned repository includes the HRT Atlas reference file at cki/data/hrt_atlas.csv (1,130 HK genes; available as optional enhancement via use_reference=True). External data downloads required (detailed in each analysis section):"),
      code("TCGA TPM:     https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz (~3.2 GB)"),
      code("TCGA probeMap: https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/probeMap%2Fhugo_gencode_good_hg38_v22comp12%2Fgencode.v22.annotation.genes.probeMap (~1.5 MB)"),
      code("LIHC clinical: cBioPortal API (lihc_tcga) - bundled in data/tcga/"),
      code("LUAD mutations: cBioPortal API (luad_tcga) - bundled in data/tcga/"),
      code("BRCA PAM50:    cBioPortal API (brca_tcga_pub) - fetched live by script"),
      p("All analyses use random seed 42 throughout."),

      // ========================================================
      // 2. CKI ALGORITHM DEFINITION
      // ========================================================
      heading("2. CKI Algorithm Definition", 2),
      p("CKI decomposes transcriptomic divergence into two components:"),
      code("omega = k_f / k_n"),
      p("where:"),
      code("k_n  = JS(p_HK_A || p_HK_B)       ... baseline divergence rate"),
      code("k_f  = JS(p_ID_A || p_ID_B)       ... functional divergence rate"),

      p("and JS(P || Q) is the Jensen-Shannon divergence (base-2 logarithm, range [0, 1]):"),
      code("M        = 0.5 * (P + Q)"),
      code("JS(P||Q) = 0.5 * KL(P||M) + 0.5 * KL(Q||M)"),
      code("where KL(P||M) = sum_i [ P_i * log2(P_i / M_i) ]  for P_i > 0"),

      p("Both k_n and k_f use the same computational pipeline: (1) subset the pseudobulk expression vector to the relevant gene indices; (2) apply softmax normalization to convert expression values into a probability distribution:  p_i = exp(x_i) / sum_j exp(x_j); (3) compute JS divergence between the two resulting distributions. This internal consistency (same metric, same normalization, same underlying expression space) ensures omega is self-calibrated."),

      // --- 2.1 Parameter Summary ---
      heading("2.1 Parameter Summary", 3),
      p("All parameters used in the reported analyses:"),

      new Table({
        width: { size: TBL_BASE, type: WidthType.DXA },
        columnWidths: [3200, 1600, 4200],
        rows: [
          tableHeader(["Parameter", "Value", "Used in"], [3200, 1600, 4200]),
          tableRow(["Random seed", "42", "all analyses"], [3200, 1600, 4200]),
          tableRow(["HK source", "HRT Atlas v1.0 (loaded directly)", "all datasets"], [3200, 1600, 4200]),
          tableRow(["HK use_reference", "N/A (loaded directly, not via API)", "all datasets"], [3200, 1600, 4200]),
          tableRow(["HRT Atlas file", "data/housekeeping/Human_Mouse_Common.csv (used)", "all"], [3200, 1600, 4200]),
          tableRow(["Number of HVGs", "2,000 (global, for k_f; Fig. 2 heatmap only)", "mouse full matrix"], [3200, 1600, 4200]),
          tableRow(["Pilot k_f genes", "200 (per-pair DE, |mean_diff|)", "mouse pilot calibration"], [3200, 1600, 4200]),
          tableRow(["Per-pair DE genes (k_f)", "200", "human, TCGA, brain"], [3200, 1600, 4200]),
          tableRow(["Bootstrap iterations", "1000 (one-sided)", "mouse pilot (main analysis)"], [3200, 1600, 4200]),
          tableRow(["Bootstrap iterations", "1000 (one-sided)", "human (script 08b)"], [3200, 1600, 4200]),
          tableRow(["Bootstrap iterations", "1000 (one-sided)", "TCGA (script 08a)"], [3200, 1600, 4200]),
          tableRow(["Bootstrap iterations", "1000 (one-sided)", "brain (script 08c)"], [3200, 1600, 4200]),
          tableRow(["k_n scaling (alpha)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["k_n floor (minimum)", "1e-4", "all analyses"], [3200, 1600, 4200]),
          tableRow(["k_f weight (w1)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Pathway weight (w2)", "0.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Normalization target", "1e4 (CP10k)", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "10", "mouse, human"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "20", "brain"], [3200, 1600, 4200]),
          tableRow(["Epsilon (omega ratio)", "1e-9", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Bootstrap CI iterations", "10000 (pair-level resampling)", "Phase B (C-S2)"], [3200, 1600, 4200]),
          tableRow(["Permutation null iterations", "10000 (per-signal P-values)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Permutation null P-values", "Unadjusted (descriptive, FDR not applicable)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Calibrated omega baseline", "6.67 (mouse split-half, n=6)", "Phase C (C-M1)"], [3200, 1600, 4200]),
          tableRow(["Dimensionality simulation trials", "2000 per dimension", "Phase C (C-M2)"], [3200, 1600, 4200]),
          tableRow(["k_n computation mode", "per-pair (brain), global (mouse pilot/human/TCGA)", "Phase C (C-M3)"], [3200, 1600, 4200]),
          tableRow(["One-sided test direction", "omega_null >= omega_obs", "Phase D (M-S1)"], [3200, 1600, 4200]),
          tableRow(["TCGA paired analysis", "Descriptive only (no formal test)", "Phase D (C-S6)"], [3200, 1600, 4200]),
          tableRow(["Cross-organ min n for ranking", "n >= 5 recommended", "Phase D (C-S4)"], [3200, 1600, 4200]),
        ],
      }),

      p("The above parameters, when used with the exact random seed and gene selection procedures described in subsequent sections, should reproduce all values reported in the manuscript. See Section 6 for output file locations and Section 7 for a step-by-step verification checklist."),

      // ========================================================
      // 3. GENE SET SELECTION
      // ========================================================
      heading("3. Gene Set Selection", 2),

      heading("3.1 Housekeeping Genes (for k_n)", 3),
      p("In all reported analyses, housekeeping (HK) genes were loaded from"),
      p("the HRT Atlas v1.0 reference (Hounkpe et al., NAR 2021) via the file"),
      p("data/housekeeping/Human_Mouse_Common.csv (1,130 human-mouse conserved"),
      p("HK genes; identical to cki/data/hrt_atlas.csv)."),
      p(""),
      p("For each dataset, HK genes were loaded as follows:"),
      p("  Tabula Muris (mouse):   HRT Atlas mouse genes (column 0),"),
      p("  Tabula Sapiens (human): HRT Atlas human genes (column 1),"),
      p("  TCGA (human):           HRT Atlas human genes (column 1),"),
      p("  Siletti Brain (human):  HRT Atlas human genes (column 1)."),
      p(""),
      p("The CKI package also supports data-driven auto-detection via"),
      p("detect_housekeeping_genes() (detection rate > 0.9, CV < 30th"),
      p("percentile, \"combined\" method; use_reference=False by default),"),
      p("but this was NOT used in the reported analyses."),
      heading("3.2 Identity Genes (for k_f)", 3),
      p("Identity (functional) genes are defined as:"),
      p("Default (CKI): top-2,000 highly variable genes (HVGs; Scanpy seurat flavor), with HK genes explicitly excluded to maintain k_n/k_f independence (adapted to min(2000, 0.8 * n_total_genes))."),
      p("Hybrid mode: global k_n computed once with shared HK gene set; per-pair k_f uses the top-200 differentially expressed genes (ranked by |mean_diff| between the two groups), excluding HK genes."),
      p("The default mode (global HVG 2,000) is used for the Tabula Muris full pairwise matrix (03_full_matrix.py, 703 pairs, Fig. 2 heatmap). The hybrid mode (per-pair top-200 DE) is used for Tabula Muris pilot analyses (calibration controls + validation, 02b_pilot_v2.py), Tabula Sapiens (human), and TCGA analyses, using a common global k_n scale (shared HK gene set) with per-pair k_f. The brain atlas analysis also uses per-pair top-200 DE genes for k_f, but unlike the other datasets, uses per-pair k_n (computed separately for each cell-type/region pair from the same HK gene set) rather than a global k_n; this is because brain k_n exhibits substantial cross-pair variability (CV = 97.35%) that is poorly captured by a global mean. The parameter sweep (Supplementary Figure 1) confirmed that the identity-only configuration (w1 = 1.0, w2 = 0.0) achieves the best cell-type discrimination without external pathway databases."),

      // ========================================================
      // 4. DATA SOURCES & PREPROCESSING
      // ========================================================
      heading("4. Data Sources & Preprocessing", 2),

      heading("4.1 Tabula Muris (Mouse) \u2014 Result 2 (Fig. 2)", 3),
      p("Dataset:    Tabula Muris FACS (Schaum et al., Nature 2018)"),
      p("Source:     https://github.com/czbiohub-sf/tabula-muris (raw data; GEO accession GSE109774 provides the processed version used in this study)"),
      p("Technology: SmartSeq2"),
      p("Data used:  15,057 cells, 22,308 genes, 6 organs (Liver, Kidney, Spleen, Lung, Heart, Marrow)"),
      p("Processing:", { bold: true }),
      p("  1. Load per-tissue count matrices (FACS/tissue-counts.csv)."),
      p("  2. Intersect to common gene set across all tissues."),
      p("  3. Normalize: sc.pp.normalize_total(target_sum=1e4), then log1p."),
      p("  4. Pseudobulk: mean expression per cell-type annotation."),
      p("  5. Filter: cell types with < 10 cells excluded."),
      p("  6. Compute global k_n on all cell-type pseudobulks (shared HK set)."),
      p("  7. Compute per-pair k_f with top-200 DE genes (ranked by |mean_diff|, HK excluded)."),
      p("  8. Bootstrap: n = 1,000 permutations, one-sided test (P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1))."),
      p("Controls: Six random-split comparisons (same cell population divided into two halves) tested baseline behavior (empirical baseline omega ~ 6.67)."),
      p("Total pairs: 703 cell-type pairs across 6 organs."),

      heading("4.2 Tabula Sapiens (Human) \u2014 Result 3 (Fig. 3)", 3),
      p("Dataset:    Tabula Sapiens (Jones et al., Science 2022)"),
      p("Source:     https://github.com/czbiohub-sf/tabula-sapiens (raw data; CZ CELLxGENE Discover provides the processed version used in this study)"),
      p("Technology: 10x Genomics (3\u2032 and 5\u2032 assays)"),
      p("Data used:  108,136 cells (6 h5ad files total), 102 cell-type entries, 6 organs (Liver, Kidney, Heart, Bone Marrow, Spleen, Lung)"),
      p("Processing:", { bold: true }),
      p("  1. Load per-organ h5ad files (TS_{Organ}.h5ad; e.g., TS_Liver.h5ad, TS_Kidney.h5ad, etc.)."),
      p("  2. Intersect to common gene set across all 6 organs."),
      p("  3. Within each organ: filter cells with < 500 genes, then normalize: sc.pp.normalize_total(target_sum=1e4), log1p."),
      p("  4. Pseudobulk: mean expression per cell_type_ontology_term_id."),
      p("  5. Global k_n: JS divergence on full pseudobulk matrix with shared HK set."),
      p("  6. Per-pair k_f: top-200 DE genes (ranked by absolute mean difference), HK genes excluded."),
      p("  7. Full pairwise omega computed for all 5,151 cell-type pairs."),
      p("Method comparison: Spearman rank correlation computed between CKI omega and four standard metrics on all 5,151 cell-type pairs:raw JS divergence (all genes), Spearman distance (1 - Spearman r), cosine distance (1 - cosine similarity), marker Jaccard distance (1 - intersection/union of top-200 marker genes per cell type). Classification AUC from cell-type pair classification task (same-type vs. different-type) computed with sklearn.metrics.roc_auc_score."),

      heading("4.3 TCGA (Human Cancer) \u2014 Result 4 (Fig. 4)", 3),
      p("Dataset:    TCGA Pan-Cancer (Hutter & Zenklusen, Cell 2018; Liu et al., Cell 2018)"),
      p("Source:     UCSC Xena (https://xenabrowser.net/), file: tcga_RSEM_gene_tpm.gz"),
      p("Data used:  3,596 samples (from 10,535 raw TCGA samples after filtering) across 5 cancer types: LUAD, LUSC, LIHC, KIRC, BRCA"),
      p("Processing:", { bold: true }),
      p("  1. Filter: gene-level mean expression > 1 TPM within each cancer type (per-cancer independent filtering)."),
      p("  2. log2(TPM + 1) transformation."),
      p("  3. Pseudobulk: mean expression per sample."),
      p("  4. Sample pairs drawn from: tumor-tumor (TT), normal-normal (NN), tumor-normal (TN). Maximum 2,000 random TT and TN pairs each."),
      p("  5. Global k_n computed once per cancer type using shared HK genes."),
      p("  6. Per-pair k_f with top-200 DE genes (ranked by |mean_diff|)."),
      p("  7. NN/TT ratio computed as mean(omega_NN) / mean(omega_TT) per cancer type."),
      p("Clinical stratification:", { bold: true }),
      p("  LIHC Edmondson grade: G1 (n=39), G2 (n=133), G3 (n=105), G4 (n=11). Jonckheere-Terpstra trend test."),
      p("  BRCA PAM50 subtype: Basal-like (n=97), HER2 (n=55), LumA (n=224), LumB (n=123), Normal-like (n=7). Kruskal-Wallis test."),
      p("  LUAD mutation: EGFR (n=61), KRAS (n=120), WT (n=311). Kruskal-Wallis test."),

      heading("4.4 Siletti Brain Atlas (Human) \u2014 Results 5 & 6 (Fig. 5 & 6)", 3),
      p("Dataset:    Siletti et al. (Science 2023)"),
      p("Source:     https://github.com/linnarsson-lab/snRNA_brain_atlas (raw data; CZ CELLxGENE Discover provides the processed version used in this study, collection ID as referenced in Siletti et al., Science 2023)"),
      p("Technology: snRNA-seq (10x Genomics)"),
      p("Data used:  888,263 non-neuronal nuclei, 108 brain regions, 10 cell classes"),
      p("Processing:", { bold: true }),
      p("  1. Load Nonneurons.h5ad in backed mode (backed='r') for memory efficiency."),
      p("  2. Map gene symbols from var[\"Gene\"]; match HK genes from HRT Atlas (1,130 human genes) to gene symbol column."),
      p("  3. Group by (cell_type, brain_region). Filter groups with < 20 nuclei."),
      p("  4. Build pseudobulk vectors: raw count means per (ct, region) group, then normalize_total (target_sum=1e4) and log1p at the pseudobulk level."),
      p("  5. Compute omega for all same-cell-type cross-region pairs (31,764 pairs total)."),
      p("  6. Organize omega values per cell type and per region pair."),

      p("Cross-organ conservation (Fig. 5): Subset of 59 same-cell-type cross-organ pairs from Tabula Sapiens data. Ranked by mean omega per cell type."),

      p("Migration detection model (multiplicative):", { bold: true }),
      p("For each (cell_type, region_pair) combination:"),
      code("expected_omega = mu_ct * mu_pair / mu_grand"),
      p("where mu_ct = cell type\u2019s global mean omega, mu_pair = region pair\u2019s mean omega, mu_grand = global mean (8.01)."),
      code("residual = observed_omega / expected_omega"),
      p("Confidence tiers:"),
      p("  Strong:   residual < 0.3, omega < 15, lowest omega in region pair."),
      p("  Moderate: residual < 0.5, omega < 25."),
      p("  Weak:     residual < 0.75, omega < 35."),

      // ========================================================
      // 5. STATISTICAL TESTING
      // ========================================================
      heading("5. Statistical Testing", 2),

      heading("5.1 Bootstrap Permutation Test", 3),
      p("For each cell-type pair comparison, the null hypothesis H0: no functional divergence beyond baseline is tested via permutation:"),
      p("  1. Pool all cells from groups A and B."),
      p("  2. For each of B iterations (B = 1,000 for all datasets):"),
      p("     a. Randomly permute cell labels."),
      p("     b. Split into two groups of original sizes."),
      p("     c. Recompute pseudobulks and omega."),
      p("  3. Null distribution = {omega_perm[1], ..., omega_perm[B]}."),
      p("  4. P-value (one-sided permutation test):"),
      code("p = (count(omega_null >= omega_obs) + 1) / (B + 1)"),
      p("  5. Effect size: SES = (omega_obs - mean_null) / std_null."),
      p("  6. Test critical values at alpha=0.05: [percentile(null, 2.5), percentile(null, 97.5)]. Note: these are permutation-based test critical values for rejecting H0, NOT confidence intervals for omega itself."),

      heading("5.2 Notes on Execution", 3),
      p("Benjamini-Hochberg FDR correction is applied to the bootstrap P-values within each dataset. The q-value column in the bootstrap output CSV files (tcga_bootstrap_results.csv, human_bootstrap_results.csv, brain_bootstrap_results.csv) provides the FDR-adjusted significance. The BH procedure is implemented in cki/bootstrap.py:benjamini_hochberg()."),

      heading("5.3 Phase B Statistical Upgrades", 3),
      p("Three additional statistical analyses were performed to address reviewer concerns (Phase B):"),
      p(""),
      p("  a. Adaptive permutation analysis (C-S1):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     Verified that B=1,000 is sufficient because bootstrap tests are at the cell-type level (10 brain, 17 human, 15 mouse), not the pair level. The minimum resolvable P-value (1/1001 = 9.99e-4) is well below the BH threshold for the top-ranked test in each dataset."),
      p(""),
      p("  b. Bootstrap confidence intervals (C-S2):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     95% CIs computed by pair-level resampling (B=10,000) for all key omega estimates. Output: results/phaseB_bootstrap_cis.csv."),
      p(""),
      p("  c. Permutation null for residual model (C-S3):"),
      p("     Script: notebooks/09b_phaseB_residual_pervisign.py"),
      p("     For each of 31,764 brain region pairs, cell type labels were shuffled B=10,000 times. Per-signal empirical P-values: P = (count(null_residual <= observed) + 1)/(B+1). 11,541 signals (36.3%) reached the empirical P-value floor (P=9.99e-5), precluding meaningful BH-FDR correction. We therefore interpret permutation results descriptively: among the 30 Strong-tier candidates, 16 signals (6 astrocytes, 10 oligodendrocytes) reached the P-value floor indicating strong evidence of deviation from the multiplicative null model, while 14 signals (P>=0.76) showed no evidence of departure. Per-signal tests are not independent; interpretation is restricted to the 30 predefined Strong candidates. Output: results/phaseB_residual_pervisign.csv, results/phaseB_residual_null.json."),
      p(""),
      p("  d. Omega distribution characterization (C-S5):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     Computed skewness, kurtosis, and normality tests (Shapiro-Wilk, D'Agostino-Pearson) for all datasets. All omega distributions are right-skewed and non-normal. SES reported as descriptive measure. Output: results/phaseB_omega_distribution.json."),

      heading("5.4 Phase C Methodological Reinforcement", 3),
      p("Three methodological analyses were performed to address reviewer concerns (Phase C):"),
      p(""),
      p("  a. Calibrated omega normalization (C-M1):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Calibrated omega: omega_cal = omega / 6.67 (empirical baseline from mouse split-half, n=6). Rescales all values so equivalent populations yield omega_cal ~ 1.0. Brain global mean: 8.01 -> 1.20; astrocytes: 14.36 -> 2.15; Bergmann glia: 2.37 -> 0.36. Function: cki.calibrate_omega(). Output: results/phaseC_calibration.json, results/phaseC_calibrated_omega_brain.csv."),
      p(""),
      p("  b. JS divergence dimensionality invariance (C-M2):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Simulation of 2,000 random Dirichlet distribution pairs across dimensions 50-5,000. Mean JS divergence is effectively constant (0.155-0.159; ratio=1.001 between d=1,130 and d=2,000), confirming that k_f inflation arises from HVG selection bias, not dimensional mismatch. Output: results/phaseC_dimensionality.json, results/phaseC_dimensionality_simulation.csv."),
      p(""),
      p("  c. Pair-specific k_n variability (C-M3):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Per-pair k_n across 31,764 brain comparisons: CV=97.35% (mean=0.0141, median=0.0086). Spearman rho between per-pair omega and global-kn omega = -0.027 (P=9.96e-7), confirming pair-specific k_n yields substantially different rankings. Justifies per-pair k_n approach for brain analysis. Output: results/phaseC_kn_variability.json, results/phaseC_kn_stats.csv, results/phaseC_omega_pair_vs_global.csv."),

      heading("5.5 Phase D Interpretation Corrections", 3),
      p("Text revisions were made to address 4 Critical and 19 Major reviewer concerns about biological interpretation and statistical caution (Phase D). No new scripts or data files were generated; all changes are in the manuscript, supplementary, and cover letter generators:"),
      p(""),
      p("  a. HK gene neutrality (C-B1): Expanded Discussion to acknowledge that HK genes lack mechanistic neutrality argument (unlike synonymous sites in Ka/Ks), and that sensitivity analysis (r > 0.95) is a practical but not mechanistic proxy."),
      p(""),
      p("  b. TCGA convergence reframing (C-B3, M-M4): TCGA Results reframed as exploratory; added explicit confounders (cell composition, peritumoral inflammation, RNA quality). Discussion paragraph rewritten to present alternative explanations."),
      p(""),
      p("  c. TCGA paired analysis (C-S6): Removed formal Mann-Whitney P-value from paired comparisons (n=2-5 per cancer type); now reported as descriptive statistics only."),
      p(""),
      p("  d. Cross-organ sample size (C-S4, M-B5): Expanded Results to flag cell types with n<5 (Memory B n=1, Smooth muscle n=1); recommend n>=5 for biological conclusions; bootstrap CIs referenced."),
      p(""),
      p("  e. PAM50/Edmondson subgroups (M-S5, M-B4): Added caveats about small subgroups (Normal-like n=7, Edmondson G4 n=11) and proliferation confound in Results and Discussion."),
      p(""),
      p("  f. One-sided test justification (M-S1): Added rationale to Methods (directional hypothesis: omega exceeding null expectation)."),
      p(""),
      p("  g. Method comparison limitation (M-M2, M-B2): Acknowledged in Discussion that CKI was not quantitatively benchmarked against SAMap/SATURN/CACIMAR."),
      p(""),
      p("  h. BH-FDR per-dataset (M-S2): Added as Limitation #13 (significance thresholds not comparable across datasets)."),
      p(""),
      p("  i. Simulation ground truth (M-M1): Added as Limitation #14 (no synthetic data validation with known ground-truth signals)."),
      p(""),
      p("  j. Parameter justification (M-M5): Added as Limitation #15 and Supplementary Note 3.11 (softmax, epsilon, top-200 DE, HVG count, log-base 2, B=1000)."),
      p(""),
      p("  k. omega 8.01 vs 14.36 (M-S6): Clarified in Results that grand mean is lower because it is dominated by cell types with many pairs and low omega."),
      p(""),
      p("  l. Cross-species analysis (M-B1): Added mention in Discussion that preliminary cross-species validation was performed (Supplementary Fig. S2)."),
      p(""),
      p("  m. Cover Letter fixes (M-W1, M-W2, M-W3): Removed 'orthogonal' overclaim, changed 'confirmed baseline behavior' to 'empirical baseline', changed 'developmental origin signatures' to 'developmental signatures'."),
      p(""),
      p("  n. Figure legends (M-W7): Added unified 'Statistical conventions' paragraph after supplementary figure legends."),

      // ========================================================
      // 6. OUTPUT FILES
      // ========================================================
      heading("6. Output Files", 2),
      p("All results are written to results/:"),
      p(""),
      p("    Mouse (02c_pilot_v2b.py):"),
      code("      results/mouse_pilot_v2b_results.csv        # omega per pair"),
      code("      results/mouse_pilot_v2b_key_values.csv   # k_n, k_f, omega per comparison"),
      p(""),
      p("    Human (05_phase33_v3_fixed.py):"),
      code("      results/phase33_v3_human_omega.csv        # omega matrix (cell-types x cell-types)"),
      code("      results/phase33_v3_human_kn.csv           # k_n matrix"),
      code("      results/phase33_v3_human_kf.csv          # k_f matrix"),
      code("      results/phase33_v3_human_pairs.csv       # long-form pair list with omega"),
      p(""),
      p("    TCGA (06_phase34_v2.py):"),
      code("      results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega"),
      code("      results/phase34_v2_summary.csv           # per-cancer summary statistics"),
      code("      results/phase34_v2_{cancer}_pair.csv  # per-cancer pair files"),
      p(""),
      p("    Brain (07c_brain_siletti_v3.py):"),
      code("      results/brain_siletti_omega_pairs_v3.csv        # all region-pair omega values"),
      code("      results/brain_siletti_ct_summary_v3.csv          # per-cell-type mean omega"),
      code("      results/brain_siletti_key_values_v3.csv          # per-cell-type global summary"),
      code("      results/brain_siletti_migration_candidates_v3.csv # migration candidate list"),
      p(""),
      p("    Bootstrap (08a/08b/08c):"),
      code("      results/tcga_bootstrap_results.csv           # TCGA bootstrap P-values (B=1000)"),
      code("      results/human_bootstrap_results.csv          # Human bootstrap P-values (B=1000)"),
      code("      results/brain_bootstrap_results.csv          # Brain bootstrap P-values (B=1000)"),
      p(""),
      p("    Phase B Statistical Upgrades (09_phaseB_statistical_upgrades.py, 09b_phaseB_residual_pervisign.py):"),
      code("      results/phaseB_adaptive_analysis.json         # Adaptive permutation analysis (C-S1)"),
      code("      results/phaseB_bootstrap_cis.csv             # Bootstrap 95% CIs for omega (C-S2)"),
      code("      results/phaseB_omega_distribution.json       # Distribution characterization (C-S5)"),
      code("      results/phaseB_residual_null.json            # Permutation null summary (C-S3)"),
      code("      results/phaseB_residual_pervisign.csv        # Empirical per-signal P-values (31,764 rows) (C-S3)"),
      code("      results/figures_final/ed_fig8_omega_distribution.pdf  # Distribution figure"),
      code("      results/figures_final/ed_fig9_residual_null.pdf      # Residual null figure"),
      p(""),
      p("    Phase C Methodological Reinforcement (09c_phaseC_methodological.py):"),
      code("      results/phaseC_calibration.json             # Calibrated omega summary (C-M1)"),
      code("      results/phaseC_calibrated_omega_brain.csv   # Calibrated omega per brain pair (C-M1)"),
      code("      results/phaseC_calibrated_cis.csv           # Calibrated bootstrap CIs (C-M1)"),
      code("      results/phaseC_dimensionality.json          # Dimensionality invariance (C-M2)"),
      code("      results/phaseC_dimensionality_simulation.csv # JS vs dimension (C-M2)"),
      code("      results/phaseC_kn_variability.json         # k_n variability analysis (C-M3)"),
      code("      results/phaseC_kn_stats.csv                # Per-cell-type k_n stats (C-M3)"),
      code("      results/phaseC_omega_pair_vs_global.csv    # Per-pair vs global k_n omega (C-M3)"),
      code("      results/figures_final/ed_fig10_dimensionality.pdf   # Dimensionality figure"),
      code("      results/figures_final/ed_fig11_kn_variability.pdf   # k_n variability figure"),
      code("      results/figures_final/ed_fig12_calibrated_omega.pdf # Calibrated omega figure"),
      p(""),
      p("Figure scripts: notebooks/30_nar_figures_fixed_v2.py"),
      heading("7. Reproducibility Checklist", 2),
      p("[\u2713] Install CKI v0.3.1: pip install -e ."),
      p("[\u2713] Verify random seed = 42 in all scripts."),
      p("[\u2713] Verify HK gene source: HRT Atlas v1.0 reference (data/housekeeping/Human_Mouse_Common.csv), loaded directly for all datasets."),
      p("[\u2713] Verify identity gene parameters: HVG seurat flavor, n=2000, HK excluded."),
      p("[\u2713] Verify bootstrap iterations: 1000 (mouse, main), 1000 (human, 08b), 1000 (TCGA, 08a), 1000 (brain, 08c)."),
      p("[\u2713] Verify normalization: CP10k + log1p."),
      p("[\u2713] Verify softmax normalization before JS divergence."),
      p("[\u2713] Verify epsilon = 1e-9 in omega computation."),
      p("[\u2713] Verify one-sided bootstrap permutation test with pseudocount +1 (P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1))."),
      p("[\u2713] For human/TCGA/brain: verify per-pair k_f uses top-200 DE genes."),
      p("[\u2713] For brain: verify min_cells_per_group = 20."),
      p("[\u2713] Note: Benjamini-Hochberg FDR correction is applied within each dataset. FDR-adjusted q-values are available in the bootstrap output CSV files. (Section 5.2)"),
      p("[\u2713] Phase B: Verify bootstrap CIs (B=10,000) in results/phaseB_bootstrap_cis.csv. (Section 5.3)"),
      p("[\u2713] Phase B: Verify permutation null (B=10,000) in results/phaseB_residual_pervisign.csv (descriptive P-values, FDR not applicable). (Section 5.3)"),
      p("[\u2713] Phase B: Verify omega distribution characterization in results/phaseB_omega_distribution.json. (Section 5.3)"),
      p("[\u2713] Phase C: Verify calibrated omega (omega/6.67) in results/phaseC_calibration.json. (Section 5.3)"),
      p("[\u2713] Phase C: Verify dimensionality invariance in results/phaseC_dimensionality.json (ratio ~1.001). (Section 5.3)"),
      p("[\u2713] Phase C: Verify k_n variability (CV=97.35%) in results/phaseC_kn_variability.json. (Section 5.3)"),
      p("[\u2713] Phase C: Verify calibrate_omega() function in cki/core.py is importable."),
      p("[\u2713] Phase D: Verify TCGA paired analysis has no formal P-value (descriptive only). (Section 5.5)"),
      p("[\u2713] Phase D: Verify cross-organ ranking flags n<5 cell types. (Section 5.5)"),
      p("[\u2713] Phase D: Verify one-sided test justification in Methods. (Section 5.5)"),
      p("[\u2713] Phase D: Verify Cover Letter does not use 'orthogonal' or 'confirmed baseline behavior'. (Section 5.5)"),
      p("[\u2713] Phase D: Verify figure legends include 'Statistical conventions' paragraph. (Section 5.5)"),

      p(""),
      p("By following this guide with the exact parameter configurations above, readers should obtain numerically identical results to those reported in the manuscript. Minor floating-point differences (\u00b11e-6) may occur due to hardware differences in transcendental function evaluation (exp, log) but will not affect any biological conclusions."),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT, buffer);
  console.log("Generated: " + OUT);
  console.log("Size: " + (buffer.length / 1024).toFixed(1) + " KB");
});
