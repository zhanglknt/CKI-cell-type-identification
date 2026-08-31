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
      code("Python:              3.14.4  (64-bit, AMD64)"),
      code("numpy:               2.4.6"),
      code("scipy:               1.17.1"),
      code("scanpy:              1.12.1"),
      code("pandas:              2.3.3"),
      code("matplotlib:          3.10.9"),
      code("scikit-learn:        1.8.0"),
      code("python-docx:         1.2.0"),

      heading("1.2 CKI Package", 3),
      p("Version: 0.4.3 (editable install from project root)"),
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

      p("Both k_n and k_f use the same computational pipeline: (1) subset the pseudobulk expression vector to the relevant gene indices; (2) add a +1 pseudo-count followed by L1 normalization to convert expression values into a probability distribution:  p_i = (x_i + 1) / sum_j (x_j + 1); (3) compute JS divergence between the two resulting distributions. This internal consistency (same metric, same normalization, same underlying expression space) ensures omega is self-calibrated."),

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
          tableRow(["HRT Atlas file", "cki/data/hrt_atlas.csv (shipped with the package; byte-identical to the downloaded data/housekeeping/Human_Mouse_Common.csv, see data/README_data.md)", "all"], [3200, 1600, 4200]),
          tableRow(["Number of HVGs", "2,000 (global, for k_f; Fig. 2 heatmap only)", "mouse full matrix"], [3200, 1600, 4200]),
          tableRow(["Pilot k_f genes", "200 (per-pair DE, |mean_diff|)", "mouse pilot calibration"], [3200, 1600, 4200]),
          tableRow(["Per-pair DE genes (k_f)", "200", "human, TCGA, brain"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "mouse pilot (main analysis)"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "human (script 08b)"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "TCGA (script 08a)"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "brain (script 08c)"], [3200, 1600, 4200]),
          tableRow(["k_n scaling (alpha)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["k_n floor (minimum)", "0 (positivity guard only; min observed per-pair k_n: 1.1e-4 mouse, 6.3e-4 human, 9.2e-5 brain; only 1 of 31,764 brain pairs below 1e-4, uncapped)", "single-cell: mouse, human, brain"], [3200, 1600, 4200]),
          tableRow(["k_n floor (minimum)", "1e-4 (bulk RNA-seq only)", "TCGA"], [3200, 1600, 4200]),
          tableRow(["k_f weight (w1)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Pathway weight (w2)", "0.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Normalization target", "1e4 (CP10k)", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "10", "mouse, human"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "20", "brain"], [3200, 1600, 4200]),
          tableRow(["Epsilon (omega ratio)", "1e-9", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Bootstrap CI iterations", "10000 (pair-level resampling)", "Phase B (C-S2)"], [3200, 1600, 4200]),
          tableRow(["Permutation null iterations", "10000 (per-signal P-values)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Permutation null P-values", "Unadjusted (descriptive, FDR not applicable)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Calibrated omega baseline", "6.67, 95% bootstrap CI [4.24, 9.24] (mouse split-half, n=6)", "Phase C (C-M1)"], [3200, 1600, 4200]),
          tableRow(["Dimensionality simulation trials", "2000 per dimension", "Phase C (C-M2)"], [3200, 1600, 4200]),
          tableRow(["k_n computation mode", "per-pair on the shared HK gene set (all datasets)", "Phase C (C-M3)"], [3200, 1600, 4200]),
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
      p("the HRT Atlas v1.0 reference (Hounkpe et al., NAR 2021) via the shipped"),
      p("file cki/data/hrt_atlas.csv (1,130 human-mouse conserved HK genes;"),
      p("the analysis scripts read a byte-identical local copy at"),
      p("data/housekeeping/Human_Mouse_Common.csv, downloaded per data/README_data.md)."),
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
      p("Hybrid mode: per-pair k_n computed on the shared HK gene set (a single HK reference applied to all pairs, keeping k_n on a consistent scale across the atlas); per-pair k_f uses the top-200 differentially expressed genes (ranked by |mean_diff| between the two groups), excluding HK genes."),
      p("The default mode (global HVG 2,000) is used only for the Tabula Muris full pairwise matrix (03_full_matrix.py, 703 pairs, Fig. 2 heatmap). The hybrid mode (per-pair k_n with per-pair top-200 DE k_f) is used for all other reported analyses: Tabula Muris pilot analyses (calibration controls + validation, 02b_pilot_v2.py), Tabula Sapiens (human), TCGA, and the Siletti brain atlas. In every dataset, k_n is computed per pair on the shared HK gene set: a sensitivity analysis contrasting this per-pair estimator with a global-k_n variant (k_n computed once from the full gene-by-cell-type pseudobulk matrix) showed that brain k_n exhibits substantial cross-pair variability (CV = 97.52%) that is poorly captured by a global mean, and that the two estimators yield substantially different omega rankings (Spearman rho = 0.142; Supplementary Fig. S11). The parameter sweep (Supplementary Figure 1) confirmed that the identity-only configuration (w1 = 1.0, w2 = 0.0) achieves the best cell-type discrimination without external pathway databases."),

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
      p("  5. Filter: cell-type entries retained if they have >= 20 cells in total and at least one mouse contributing >= 10 cells (38 entries, 703 pairs)."),
      p("  6. Compute per-pair k_n on the shared HK gene set for each cell-type pair."),
      p("  7. Compute per-pair k_f with top-200 DE genes (ranked by |mean_diff|, HK excluded)."),
      p("  8. Permutation test: n = 1,000 permutations, one-sided test (P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1))."),
      p("Controls: Six random-split comparisons (same cell population divided into two halves) tested baseline behavior (empirical baseline omega = 6.67, 95% bootstrap CI [4.24, 9.24], B = 10,000 resamples of the 6 control omega values; see Section 5.4 a for reproduction)."),
      p("Total pairs: 703 cell-type pairs across 6 organs."),
      p("Cross-species matching note (Supplementary Fig. S2): the mouse-human cell-type matching used for the cross-species comparison is case-insensitive with prefix matching (notebooks/_ed_fig2_clean.py), because cell-type names in results/full_matrix_pairs.csv are truncated to 20 characters. This rule matches 15 shared cell types between the Tabula Muris and Tabula Sapiens annotations; exact-string matching would match none. Re-running the comparison with a different matching rule will change the plotted cell-type set."),

      heading("4.2 Tabula Sapiens (Human) \u2014 Result 3 (Fig. 3)", 3),
      p("Dataset:    Tabula Sapiens (Jones et al., Science 2022)"),
      p("Source:     https://github.com/czbiohub-sf/tabula-sapiens (raw data; CZ CELLxGENE Discover provides the processed version used in this study)"),
      p("Technology: 10x Genomics (3\u2032 and 5\u2032 assays)"),
      p("Data used:  108,136 cells (6 h5ad files total), 102 cell-type entries (99 of which passed the pairwise-analysis filters: at least 20 cells per entry and at least one donor with at least 10 cells; \"unknown\" annotations excluded), 6 organs (Liver, Kidney, Heart, Bone Marrow, Spleen, Lung)"),
      p("Processing:", { bold: true }),
      p("  1. Load per-organ h5ad files (TS_{Organ}.h5ad; e.g., TS_Liver.h5ad, TS_Kidney.h5ad, etc.)."),
      p("  2. Intersect to common gene set across all 6 organs."),
      p("  3. Within each organ: filter cells with < 500 genes, then normalize: sc.pp.normalize_total(target_sum=1e4), log1p."),
      p("  4. Pseudobulk: one pseudobulk per cell-type entry from its largest donor (the donor with the most cells passing QC), to avoid donor-pair proliferation."),
      p("  5. Per-pair k_n: JS divergence on the shared HK gene set for each pair (single HK reference applied to all pairs)."),
      p("  6. Per-pair k_f: top-200 DE genes (ranked by absolute mean difference), HK genes excluded."),
      p("  7. Full pairwise omega computed for all 4,851 analyzed cell-type pairs (C(99, 2))."),
      p("Method comparison: Spearman rank correlation computed between CKI omega and four standard metrics on all 4,851 cell-type pairs: raw JS divergence (all genes), Spearman distance (1 - Spearman r), cosine distance (1 - cosine similarity), marker Jaccard distance (1 - intersection/union of top-200 marker genes per cell type). Classification AUC from cell-type pair classification task (same-type vs. different-type) computed with sklearn.metrics.roc_auc_score. Output: results/phase35_all_metrics_pairs.csv."),

      heading("4.3 TCGA (Human Cancer) \u2014 Result 4 (Fig. 4)", 3),
      p("Dataset:    TCGA Pan-Cancer (Hutter & Zenklusen, Cell 2018; Liu et al., Cell 2018)"),
      p("Source:     UCSC Xena (https://xenabrowser.net/), file: tcga_RSEM_gene_tpm.gz"),
      p("Data used:  3,596 samples (from 10,535 raw TCGA samples after filtering) across 5 cancer types: LUAD, LUSC, LIHC, KIRC, BRCA"),
      p("Processing:", { bold: true }),
      p("  1. Filter: gene-level mean expression > 1 TPM within each cancer type (per-cancer independent filtering)."),
      p("  2. log2(TPM + 1) transformation."),
      p("  3. Pseudobulk: mean expression per sample."),
      p("  4. Sample pairs drawn from: tumor-tumor (TT), normal-normal (NN), tumor-normal (TN). Maximum 2,000 random TT and TN pairs each."),
      p("  5. Per-pair k_n computed on the shared HK gene set for each sample pair."),
      p("  6. Per-pair k_f with top-200 DE genes (ranked by |mean_diff|)."),
      p("  7. NN/TT ratio computed as mean(omega_NN) / mean(omega_TT) per cancer type."),
      p("Clinical stratification:", { bold: true }),
      p("  LIHC Edmondson grade: G1 (n=39), G2 (n=133), G3 (n=105), G4 (n=11). Jonckheere-Terpstra trend test."),
      p("  BRCA PAM50 subtype: Basal-like (n=97), HER2 (n=55), LumA (n=224), LumB (n=123), Normal-like (n=7). Kruskal-Wallis test."),
      p("  LUAD mutation: EGFR (n=61), KRAS (n=120), WT (n=311). Kruskal-Wallis test."),

      p("Cross-organ conservation (Result 5, Fig. 5): Subset of 59 same-cell-type cross-organ pairs from Tabula Sapiens data. Ranked by mean omega per cell type."),

      heading("4.4 Siletti Brain Atlas (Human) \u2014 Result 6 (Fig. 6)", 3),
      p("Dataset:    Siletti et al. (Science 2023)"),
      p("Source:     https://github.com/linnarsson-lab/snRNA_brain_atlas (raw data; CZ CELLxGENE Discover provides the processed version used in this study, collection ID as referenced in Siletti et al., Science 2023)"),
      p("Technology: snRNA-seq (10x Genomics)"),
      p("Data used:  888,263 non-neuronal nuclei (886,808 after filtering), 108 brain regions, 10 cell classes"),
      p("Processing:", { bold: true }),
      p("  1. Load Nonneurons.h5ad in backed mode (backed='r') for memory efficiency."),
      p("  2. Map gene symbols from var[\"Gene\"]; match HK genes from HRT Atlas (1,115 of 1,130 human genes matched to the Siletti gene annotation)."),
      p("  3. Group by (cell_type, brain_region). Filter groups with < 20 nuclei; require >= 50 nuclei per region."),
      p("  4. Build pseudobulk vectors: cell-count-weighted means of per-library (10x sample) mean expression vectors per (ct, region) group, then normalize_total (target_sum=1e4) and log1p at the pseudobulk level."),
      p("  5. Compute omega for all same-cell-type cross-region pairs (31,764 pairs total)."),
      p("  6. Organize omega values per cell type and per region pair."),

      p("Region-association detection model (multiplicative):", { bold: true }),
      p("For each (cell_type, region_pair) combination:"),
      code("expected_omega = mu_ct * mu_pair / mu_grand"),
      p("where mu_ct = cell type\u2019s global mean omega, mu_pair = region pair\u2019s mean omega, mu_grand = global mean over all 31,764 pairs (38.55)."),
      code("residual = observed_omega / expected_omega"),
      p("Confidence tiers:"),
      p("  Strong:   residual < 0.3, omega < 15, lowest omega in region pair."),
      p("  Moderate: residual < 0.5, omega < 25."),
      p("  Weak:     residual < 0.75, omega < 35."),

      // ========================================================
      // 5. STATISTICAL TESTING
      // ========================================================
      heading("5. Statistical Testing", 2),

      heading("5.1 Permutation Test", 3),
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
      p("  6. Null-distribution reference values: the one-sided critical value at alpha=0.05 is percentile(null, 95); omega_obs above this value rejects H0. The interval [percentile(null, 2.5), percentile(null, 97.5)] is the central 95% range of the null distribution (descriptive only) and is NOT a confidence interval for omega itself. Confidence intervals for omega point estimates are computed separately by pair-level resampling (Section 5.3b)."),

      heading("5.2 Notes on Execution", 3),
      p("Benjamini-Hochberg FDR correction is applied to the permutation P-values within each dataset (group-level tests: m = 10 for brain, 17 for human, 15 for mouse, 5 for TCGA). The q_value column in the bootstrap output CSV files (tcga_bootstrap_results.csv, human_bootstrap_results.csv, brain_bootstrap_results.csv) provides the BH-adjusted P-value. The BH procedure is implemented in cki/bootstrap.py:benjamini_hochberg(). For the brain per-pair region-association screen, FDR correction is applied across all m = 31,764 region pairs under the block-shuffle null (Section 5.3c); the corresponding per-pair BH-adjusted P-values are in brain_bs_null_results.csv (column q_fdr), summarized in brain_bs_null_fdr_manifest.json."),

      heading("5.3 Phase B Statistical Upgrades", 3),
      p("Three additional statistical analyses were performed to address reviewer concerns (Phase B):"),
      p(""),
      p("  a. Adaptive permutation analysis (C-S1):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     Verified that B=1,000 is sufficient because permutation tests are at the cell-type level (10 brain, 17 human, 15 mouse), not the pair level. The minimum resolvable P-value (1/1001 = 9.99e-4) is well below the BH threshold for the top-ranked test in each dataset."),
      p(""),
      p("  b. Bootstrap confidence intervals (C-S2):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     95% CIs computed by pair-level resampling (B=10,000) for all key omega estimates. Output: results/phaseB_bootstrap_cis.csv."),
      p(""),
      p("  c. Block-shuffle permutation null for the residual model (C-S3):"),
      p("     Scripts: notebooks/08d_brain_blockshuffle_null.py, notebooks/08e_brain_blockshuffle_results.py"),
      p("     10x Chromium libraries (sample_id) were treated as blocks, and the sample-to-region assignment was randomly permuted across libraries (preserving the observed per-region library-count structure); region pseudobulks, all 31,764 pair omega values, and multiplicative residuals were then recomputed. B = 1,000 permutations (minimum resolvable P = 1/1,001 = 9.99e-4). Per-pair empirical P-values use the one-sided lower-tail formula P = (count(omega_null <= omega_obs) + 1)/(B + 1), the appropriate direction because region-associated candidates are defined by anomalously low omega. Benjamini-Hochberg FDR was applied across all m = 31,764 pairs: no pair reached q < 0.05 (minimum q = 0.520). At this multiplicity q < 0.05 would require either B ~ 6e5 permutations or at least ~635 of the 31,764 P-values at the permutation floor of 9.99e-4 (the BH threshold for the smallest ordered P-value, 0.05/31,764 = 1.6e-6, is roughly 600-fold below the P-value floor), so the FDR outcome primarily reflects permutation resolution rather than evidence against the candidates. Among the 39 Strong-tier candidates, 31 had raw P < 0.05 and are reported as hypothesis-generating signals; interpretation is restricted to the predefined Strong tier because per-signal tests are not independent. An earlier per-pair cell-label shuffle implementation of this test was anti-conservative (36.3% of pairs at the P-value floor) because it ignored the block structure of the experiment; the block-shuffle null rectifies this. A companion cell-type-level test (whether regional structure significantly raises a cell type's mean omega; one-sided upper-tail P across the same B = 1,000 permutations) is output in brain_bs_null_ct_test.csv. Output: results/brain_bs_null_observed_pairs.csv, results/brain_bs_null_results.csv, results/brain_bs_null_ct_test.csv, results/brain_bs_null_summary.txt, results/brain_bs_null_fdr_manifest.json."),
      p(""),
      p("  d. Omega distribution characterization (C-S5):"),
      p("     Script: notebooks/09_phaseB_statistical_upgrades.py"),
      p("     Computed skewness, kurtosis, and normality tests (Shapiro-Wilk, D'Agostino-Pearson) for all datasets. All omega distributions are right-skewed and non-normal. SES reported as descriptive measure. Output: results/phaseB_omega_distribution.json."),

      heading("5.4 Phase C Methodological Reinforcement", 3),
      p("Three methodological analyses were performed to address reviewer concerns (Phase C):"),
      p(""),
      p("  a. Calibrated omega normalization (C-M1):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Calibrated omega: omega_cal = omega / 6.67 (empirical baseline from mouse split-half, n=6; 95% bootstrap CI [4.24, 9.24] computed by resampling the 6 control omega values with replacement, B = 10,000, reporting the 2.5th and 97.5th percentiles — see results/mouse_pilot_v2_results.csv, category C_control). Rescales all values so equivalent populations yield omega_cal ~ 1.0; given the width of the baseline CI, calibrated values are reported with one significant figure: brain global mean 38.55 -> omega_cal ~ 6 (range 4.2-9.1); astrocytes 82.75 -> ~ 12 (range 9.0-19.5); Bergmann glia 13.56 -> ~ 2. Scheme-matched split-half calibration inside the brain atlas gave an internal baseline of 9.73 (95% CI [9.03, 10.53]), ~1.5-fold higher than the mouse factor, under which Bergmann glia corresponds to omega_cal ~ 1.4 (close to the internal baseline); the Tabula Sapiens internal baseline was 7.67 (95% CI [7.39, 8.00]), inside the mouse CI, so the mouse factor transfers to Tabula Sapiens but not to the brain dataset (omega_cal is dataset-relative). Function: cki.calibrate_omega(). Output: results/brain_bs_null_observed_pairs.csv (the authoritative observed-pair values; the earlier results/phaseC_calibration.json and results/phaseC_calibrated_omega_brain.csv predate the block-shuffle pipeline and are superseded)."),
      p(""),
      p("  b. JS divergence dimensionality invariance (C-M2):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Simulation of 2,000 random Dirichlet distribution pairs across dimensions 50-5,000. Mean JS divergence is effectively constant (0.155-0.159; ratio=1.001 between d=1,130 and d=2,000), confirming that k_f inflation arises from HVG selection bias, not dimensional mismatch. Output: results/phaseC_dimensionality.json, results/phaseC_dimensionality_simulation.csv."),
      p(""),
      p("  c. Pair-specific k_n variability (C-M3):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Per-pair k_n across 31,764 brain comparisons: CV=97.52% (mean=0.0035, median=0.0022). Spearman rho between per-pair omega and global-kn omega = +0.142 (P=7.07e-143), confirming pair-specific k_n yields substantially different rankings. Justifies the per-pair k_n estimator used in all reported analyses. Output: results/phaseC_kn_variability.json, results/phaseC_kn_stats.csv, results/phaseC_omega_pair_vs_global.csv."),

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
      p("  i. Simulation ground truth: addressed in the current revision by notebooks/45_groundtruth_simulation.py (semi-synthetic module-shift injection on a real single-cell background; type-I error 0.00 under neutral HK drift vs 0.58 for cosine; AUC 0.80 for functional-vs-neutral discrimination). Limitation #14 was rewritten from a missing-validation statement into an explicit sensitivity bound."),
      p(""),
      p("  j. Parameter justification (M-M5): Added as Limitation #15 and Supplementary Note 3.11 (normalization pseudo-count, epsilon, top-200 DE, HVG count, log-base 2, B=1000)."),
      p(""),
      p("  k. omega 38.55 vs 82.75 (M-S6): Clarified in Results that grand mean is lower because it is dominated by cell types with many pairs and low omega."),
      p(""),
      p("  l. Cross-species analysis (M-B1): Added mention in Discussion that preliminary cross-species validation was performed (Supplementary Fig. S2)."),
      p(""),
      p("  m. Cover Letter fixes (M-W1, M-W2, M-W3): Removed 'orthogonal' overclaim, changed 'confirmed baseline behavior' to 'empirical baseline', changed 'developmental origin signatures' to 'developmental signatures'."),
      p(""),
      p("  n. Figure legends (M-W7): Added unified 'Statistical conventions' paragraph after supplementary figure legends."),

      heading("5.6 Reviewer Robustness Analyses (v36 peer review)", 3),
      p("Five analyses were run to address the simulated peer-review round on the v36 package (4.6/10, Major Revision). All use the same gene sets and pseudobulk pipeline as the corresponding main analyses:"),
      p(""),
      p("  a. Within-donor cross-region gradient (C-J):"),
      p("     Script: notebooks/41_reviewer_fix_within_donor.py"),
      p("     Recomputed the brain class-level omega gradient using only same-donor (donor, region) pseudobulk pairs. Astrocytes remained the most divergent class (mean omega = 75.18 across 11,139 within-donor pairs) and Bergmann glia the least (16.73), a 4.50-fold gradient whose class ordering closely tracked the pooled ordering; within-donor values are systematically lower for the largest classes, indicating part of the pooled signal reflects donor-level variation. Output: results/reviewer_within_donor_gradient.csv."),
      p(""),
      p("  b. k_n estimator sensitivity and brain split-half calibration (C-C, C-B brain):"),
      p("     Script: notebooks/42_reviewer_fix_kn_estimators.py"),
      p("     Re-derived per-pair k_f and k_n for all 31,764 brain pairs and compared four aggregation schemes. Class ordering is stable under an aggregate-first k_n estimator (Spearman rho = 0.988 vs. the reported per-pair estimator; gradient 6.51-fold vs. 6.10-fold) but not under a single global k_n (rho = 0.09; this variant is effectively a rescaling of k_f-only). The astrocyte-vs-Bergmann-glia contrast is predominantly a k_n effect (k_f differs 2.0-fold, k_n 3.2-fold). The same script performed scheme-matched split-half calibration inside the brain atlas: internal baseline 9.73 (95% bootstrap CI [9.03, 10.53]; 29 populations, B = 50 splits each, >= 200 nuclei), ~1.5-fold higher than the mouse-derived 6.67, so the mouse calibration overstates omega_cal in the brain dataset. Outputs: results/reviewer_kn_estimator_consistency.csv, results/reviewer_brain_splithalf_summary.txt, results/reviewer_brain_splithalf_raw.csv."),
      p(""),
      p("  c. Tabula Sapiens split-half calibration (C-B human):"),
      p("     Script: notebooks/43_reviewer_fix_ts_splithalf.py"),
      p("     Scheme-matched split-half calibration inside Tabula Sapiens (largest donor per (organ, cell type) group, >= 100 cells; 71 populations; B = 50 splits each): internal baseline 7.67 (95% bootstrap CI [7.39, 8.00]), which lies inside the mouse-derived CI [4.24, 9.24]; the mouse calibration factor is therefore transferable to Tabula Sapiens. Outputs: results/reviewer_ts_splithalf_summary.txt, results/reviewer_ts_splithalf_populations.csv."),
      p(""),
      p("  d. Lineage enrichment (C-G):"),
      p("     Script: notebooks/38_reviewer_fix_lineage_enrichment.py"),
      p("     Tested enrichment of each cell class among Strong candidates with a hypergeometric test over the 31,764 pairs. The oligodendrocyte lineage (pre-specified, 12,775 pairs, 40.2% of comparisons) shows no enrichment: 12 of 39 Strong candidates (expected 15.7; fold 0.77; hypergeometric P = 0.916; permutation P = 0.917 with B = 100,000; OPCs alone P = 0.9995). The only class with significant enrichment is microglia (16 of 39, fold 2.30, hypergeometric P = 6.0e-4, Bonferroni-corrected P = 0.006 across the ten classes). Output: results/reviewer_lineage_enrichment.txt."),
      p(""),
      p("  e. Tier-threshold sensitivity (C-D):"),
      p("     Script: notebooks/39_reviewer_fix_tier_sensitivity.py"),
      p("     Recomputed the Strong set and lineage enrichment over a 20-combination grid of residual caps (0.2-0.4) and omega caps (12-25). No combination shows oligodendrocyte-lineage enrichment (fold enrichment 0.36-1.15 across the grid; the full range including residual-cap 0.2 rows is 0-1.15, where fold 0 arises because the Strong set shrinks to a single non-lineage candidate; all hypergeometric P >= 0.43); the Strong set size ranges from 1 (residual cap 0.2) to 259 (residual cap 0.4, omega cap 25). Output: results/reviewer_tier_sensitivity.csv."),
      p("     Script: notebooks/44_fix_phaseB_cis.py"),
      p("     Recomputed results/phaseB_bootstrap_cis.csv from the authoritative omega sources: brain rows from results/brain_bs_null_observed_pairs.csv (astrocyte mean 82.75, matching the main text) and human rows from results/phase35_all_metrics_pairs.csv (n = 4,851); removed 16 legacy Human (per-CT) rows computed with a null-sd approximation; mouse rows preserved verbatim (downstream loaders depend on them). The data sources of notebooks/09_phaseB_statistical_upgrades.py were updated accordingly, and results/phaseC_calibrated_cis.csv was regenerated (deterministic division by 6.67)."),

      p("     Script: notebooks/45_groundtruth_simulation.py"),
      p("     Ground-truth simulation injecting module shifts of known magnitude (delta = 0.125-2) into a real single-cell background (Tabula Muris FACS marrow B cells, 1,848 cells; 200 cells per group; gene set mirrors the brain pipeline). Neutral perturbations injected separately: HK-gene drift (eta = 0.25-1) and global overdispersion (epsilon = 0.3-1). Six metrics per replicate with the identical brain-analysis code path (omega, k_f, k_n, raw JS, cosine, k_f/k_total); thresholds calibrated at the 95th percentile of 200 baseline replicates; three independent module seeds; 1,750 replicates total. Key results: type-I error under neutral HK drift omega 0.000 vs raw JS 0.553 and cosine 0.580; power at delta = 1: omega 0.000 vs raw JS 0.993; AUC functional-vs-neutral: omega 0.804 (rank 1 of 6). Outputs: results/groundtruth_simulation_raw.csv, results/groundtruth_simulation_summary.csv, results/groundtruth_simulation_metrics.json."),

      p("     Script: notebooks/46_fixed_panel_ablation.py"),
      p("     Fixed gene-panel ablation of the brain landscape: recomputed all 31,764 same-cell-type cross-region pairs under four k_f gene-selection schemes (S0 reported per-pair top-200 DE; S1 fixed top-2,000 by global mean; S2 leave-pair-out top-200; S3 all 5,000 non-HK genes), with identical keep set, pseudobulks and k_n. The reference implementation reproduced the reported landscape exactly (max per-pair omega difference 6.4e-13). Pair-level Spearman rho vs S0: 0.918 (S1), 0.937 (S2), 0.931 (S3); class-mean ordering rho 0.90/0.99/0.93; astrocyte/Bergmann-glia ratio 6.10 (S0) versus 7.67/6.53/6.57. Circularity inflation: median k_f(S0)/k_f(S2) = 1.61 (IQR 1.27-2.07). Scheme-matched block-shuffle null under S2 (B = 200): astrocytes, OPCs and committed OPCs at the P = 0.005 permutation floor, fibroblasts P = 0.020, vascular cells P = 0.035, ependymal P = 0.164, microglia P = 0.796, oligodendrocytes P = 0.876, choroid plexus P = 0.562, Bergmann glia P = 0.980. Outputs: results/fixed_panel_ablation_pairs.csv, results/fixed_panel_ablation_ct.csv, results/fixed_panel_ablation_null_<CT>.npy, results/fixed_panel_ablation_summary.json."),


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
      p("    Human method comparison (phase35):"),
      code("      results/phase35_all_metrics_pairs.csv      # five metrics per analyzed pair (4,851 rows)"),
      p(""),
      p("    TCGA (06_phase34_v2.py):"),
      code("      results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega"),
      code("      results/phase34_v2_summary.csv           # per-cancer summary statistics"),
      code("      results/phase34_v2_TCGA-{cancer}_pairs.csv  # per-cancer pair files (TCGA-BRCA/KIRC/LIHC/LUAD/LUSC)"),
      p(""),
      p("    Brain (07c_brain_siletti_v3.py):"),
      p("      NOTE: the four brain_siletti_*_v3.csv files below are PRE-FIX"),
      p("      outputs generated before the v38.1 extract_csr_from_backed()"),
      p("      row-allocation fix and are SUPERSEDED - their values (e.g."),
      p("      astrocyte omega 103.08, Bergmann glia 16.42, min k_n 7.7 × 10⁻⁵)"),
      p("      contradict the manuscript. All authoritative post-fix brain"),
      p("      numbers are in brain_bs_null_observed_pairs.csv /"),
      p("      brain_bs_null_results.csv and the reviewer_brain_* files"),
      p("      (astrocyte 82.75, Bergmann glia 13.56, min k_n 9.2e-5)."),
      code("      results/brain_siletti_omega_pairs_v3.csv        # all region-pair omega values [SUPERSEDED - pre-v38.1]"),
      code("      results/brain_siletti_ct_summary_v3.csv          # per-cell-type mean omega [SUPERSEDED - pre-v38.1]"),
      code("      results/brain_siletti_key_values_v3.csv          # per-cell-type global summary [SUPERSEDED - pre-v38.1]"),
      code("      results/brain_siletti_migration_candidates_v3.csv # region-associated candidate list [SUPERSEDED - pre-v38.1]"),
      p(""),
      p("    Permutation tests (08a/08b/08c; file names retain the historical *_bootstrap_* naming):"),
      code("      results/tcga_bootstrap_results.csv           # TCGA permutation P-values (B=1000)"),
      code("      results/human_bootstrap_results.csv          # Human permutation P-values (B=1000)"),
      code("      results/brain_bootstrap_results.csv          # Brain permutation P-values (B=1000)"),
      p(""),
      p("    Brain block-shuffle null (08d/08e):"),
      code("      results/brain_bs_null_observed_pairs.csv   # observed omega/residual/tier per pair (31,764 rows)"),
      code("      results/brain_bs_null_results.csv          # per-pair block-shuffle P-values and BH q_fdr"),
      code("      results/brain_bs_null_ct_test.csv          # cell-type-level block-shuffle test"),
      code("      results/brain_bs_null_summary.txt          # FDR summary (Strong n=39, 31 raw P<0.05, min q=0.520)"),
      code("      results/brain_bs_null_fdr_manifest.json    # machine-readable manifest"),
      p(""),
      p("    Phase B Statistical Upgrades (09_phaseB_statistical_upgrades.py; 09b_phaseB_residual_pervisign.py, residual-model outputs superseded by the block-shuffle null):"),
      code("      results/phaseB_adaptive_analysis.json         # Adaptive permutation analysis (C-S1)"),
      code("      results/phaseB_bootstrap_cis.csv             # Bootstrap 95% CIs for omega (C-S2)"),
      code("      results/phaseB_omega_distribution.json       # Distribution characterization (C-S5)"),
      code("      results/phaseB_residual_null.json            # Permutation null summary (C-S3; superseded by block-shuffle null)"),
      code("      results/phaseB_residual_pervisign.csv        # Per-signal P-values (C-S3; superseded by block-shuffle null)"),
      code("      results/figures_final/ed_fig8_omega_distribution.pdf  # Distribution figure"),
      code("      results/figures_final/ed_fig9_residual_null.pdf      # Residual null figure"),
      p(""),
      p("    Phase C Methodological Reinforcement (09c_phaseC_methodological.py):"),
      code("      results/phaseC_calibration.json             # Calibrated omega summary (C-M1; superseded by block-shuffle observed pairs)"),
      code("      results/phaseC_calibrated_omega_brain.csv   # Calibrated omega per brain pair (C-M1; superseded by block-shuffle observed pairs)"),
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
      p("Figure scripts: notebooks/30_genome_biology_figures.py"),
      heading("7. Reproducibility Checklist", 2),
      p("[\u2713] Install CKI v0.4.3: pip install -e ."),
      p("[\u2713] Verify Python 3.14.4 environment (Section 1.1)."),
      p("[\u2713] Verify random seed = 42 in all scripts."),
      p("[\u2713] Verify HK gene source: HRT Atlas v1.0 reference (cki/data/hrt_atlas.csv, shipped; analysis scripts read the byte-identical downloaded copy data/housekeeping/Human_Mouse_Common.csv), loaded directly for all datasets."),
      p("[\u2713] Verify identity gene parameters: HVG seurat flavor, n=2000, HK excluded."),
      p("[\u2713] Verify permutation iterations: 1000 (mouse, main), 1000 (human, 08b), 1000 (TCGA, 08a), 1000 (brain, 08c)."),
      p("[\u2713] Verify normalization: CP10k + log1p."),
      p("[\u2713] Verify +1 pseudo-count and L1 normalization before JS divergence."),
      p("[\u2713] Verify epsilon = 1e-9 in omega computation."),
      p("[\u2713] Verify one-sided permutation test with pseudocount +1 (P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1))."),
      p("[\u2713] For mouse pilot/human/TCGA/brain: verify k_n is computed per pair on the shared HK gene set and per-pair k_f uses top-200 DE genes."),
      p("[\u2713] For brain: verify min_cells_per_group = 20."),
      p("[\u2713] Note: Benjamini-Hochberg FDR correction is applied within each dataset. BH-adjusted P-values are available in the bootstrap output CSV files. (Section 5.2)"),
      p("[\u2713] Phase B: Verify bootstrap CIs (B=10,000) in results/phaseB_bootstrap_cis.csv. (Section 5.3)"),
      p("[\u2713] Block-shuffle null: Verify B=1,000 in results/brain_bs_null_fdr_manifest.json (39 Strong candidates, 31 with raw P<0.05, minimum q=0.520). (Section 5.3)"),
      p("[\u2713] Phase B: Verify omega distribution characterization in results/phaseB_omega_distribution.json. (Section 5.3)"),
      p("[\u2713] Phase C: Verify calibrated omega (omega/6.67, 95% bootstrap CI [4.24, 9.24]): brain mean 38.55 -> omega_cal ~ 6, astrocytes 82.75 -> ~ 12, Bergmann glia 13.56 -> ~ 2 (results/brain_bs_null_observed_pairs.csv); verify internal split-half baselines 9.73 [9.03, 10.53] (brain) and 7.67 [7.39, 8.00] (Tabula Sapiens) in results/reviewer_brain_splithalf_summary.txt and results/reviewer_ts_splithalf_summary.txt. (Section 5.4/5.6)"),
      p("[\u2713] Phase C: Verify dimensionality invariance in results/phaseC_dimensionality.json (ratio ~1.001). (Section 5.3)"),
      p("[\u2713] Phase C: Verify k_n variability (CV=97.52%) in results/phaseC_kn_variability.json. (Section 5.4)"),
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
