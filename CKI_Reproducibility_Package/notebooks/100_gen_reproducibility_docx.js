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
                   new TextRun({ text: " Chinese Institute for Brain Research, Beijing, China", font: FONT, size: SIZE, color: BLACK })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "2", font: FONT, size: 18, color: BLACK, superScript: true }),
                   new TextRun({ text: " Institute of Blood Transfusion, Chinese Academy of Medical Sciences & Peking Union Medical College, Chengdu, China", font: FONT, size: SIZE, color: BLACK })],
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
      p("Document-build dependencies (python-docx 1.2.0, python-pptx, lxml, reportlab, and related packages) are NOT required for any analysis; they are listed separately under 'Document generation' in requirements.txt and are needed only to rebuild the manuscript, supplementary notes, and this guide."),

      heading("1.2 CKI Package", 3),
      p("Version: 0.4.7 (editable install from project root)"),
      p("Repository: https://github.com/zhanglknt/CKI-cell-type-identification"),
      p("Install (editable, recommended):"),
      code("cd <project_root>"),
      code("pip install -e ."),
      p("Install (fixed dependencies):"),
      code("pip install -r requirements.txt"),
      p("A Dockerfile pinning the same environment (Linux x86_64 base) is provided in the repository root for containerized reproduction."),

      heading("1.3 System Requirements", 3),
      code("Operating system:    Windows 10/11 x64 (also tested Linux x86_64)"),
      code("Memory:              >= 32 GB RAM (TCGA matrix ~10 GB peak)"),
      code("Disk space:          >= 5 GB (for TPM data and intermediates)"),
      code("Network:             Internet for data downloads and cBioPortal API"),

      heading("1.4 Data Dependencies", 3),
      p("The cloned repository includes the HRT Atlas reference file at cki/data/hrt_atlas.csv (1,130 HK genes; available as optional enhancement via use_reference=True). External data downloads required (detailed in each analysis section):"),
      code("TCGA TPM:     https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz (~0.74 GB compressed; ~4.96 GB decompressed)"),
      code("TCGA probeMap: bundled at data/tcga/probemap.tsv (~1.5 MB; the original UCSC Xena S3 URL is no longer served, so the identical file ships with the repository)"),
      code("LIHC clinical: cBioPortal API (lihc_tcga) - bundled in data/tcga/"),
      code("LUAD mutations: cBioPortal API (luad_tcga) - bundled in data/tcga/"),
      code("BRCA PAM50:    cBioPortal API (brca_tcga_pub) - fetched live by script"),
      code("Kang IFN-beta PBMC: GEO GSE96583 - download GSE96583_RAW.tar (~76 MB), GSE96583_genes.txt.gz, and the batch2 tsne.df/metadata files into data/kang_ifnb/ (see the header of notebooks/79_kang_ifnb_demo.py for the exact expected files)"),
      p("All analyses use random seed 42 throughout, with three fixed exceptions: notebooks/77_pseudoregion_control.py, notebooks/78_axis_permutation_test.py, and notebooks/79_kang_ifnb_demo.py use the fixed seed 20260903 (77 additionally uses a permutation-base seed of 777000). These seeds are hard-coded in the scripts."),

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

      p("Both k_n and k_f use the same computational pipeline: (1) subset the pseudobulk expression vector to the relevant gene indices; (2) convert the vector to a probability distribution by softmax normalization, p_i = exp(x_i - max(x)) / sum_j exp(x_j - max(x)) (cki/utils.py, ensure_probability_distribution; when the pseudobulk is the log1p of linear-scale aggregates, as in the brain pipeline, this is exactly equivalent to adding a +1 pseudo-count followed by L1 normalization on the linear scale, p_i = (y_i + 1) / sum_j (y_j + 1)); (3) compute JS divergence between the two resulting distributions. This internal consistency (same metric, same normalization, same underlying expression space) ensures omega is self-calibrated."),

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
          tableRow(["Permutation iterations", "1000 (one-sided)", "human (script 08b_human_bootstrap_v2.py)"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "TCGA (script 08a)"], [3200, 1600, 4200]),
          tableRow(["Permutation iterations", "1000 (one-sided)", "brain (script 08c_brain_bootstrap_v3.py; authoritative stats: 08d/08e block-shuffle)"], [3200, 1600, 4200]),
          tableRow(["k_n scaling (alpha)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["k_n floor (minimum)", "0 (positivity guard only; min observed per-pair k_n: 1.1e-4 mouse, 6.3e-4 human, 9.2e-5 brain; only 1 of 31,764 brain pairs below 1e-4, uncapped)", "single-cell: mouse, human, brain"], [3200, 1600, 4200]),
          tableRow(["k_n floor (minimum)", "1e-4 (bulk RNA-seq only)", "TCGA"], [3200, 1600, 4200]),
          tableRow(["k_f weight (w1)", "1.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Pathway weight (w2)", "0.0", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Normalization target", "1e4 (CP10k)", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "10", "mouse, human"], [3200, 1600, 4200]),
          tableRow(["Min cells per group", "20", "brain"], [3200, 1600, 4200]),
          tableRow(["Omega positivity guard", "kn <= 0 -> inf; TCGA kn_floor = 1e-4; 1e-9 only on the bootstrap-null denominator (02b/02c)", "all analyses"], [3200, 1600, 4200]),
          tableRow(["Bootstrap CI iterations", "10000 (pair-level resampling)", "Phase B (C-S2)"], [3200, 1600, 4200]),
          tableRow(["Permutation null iterations", "10000 (per-signal P-values)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Permutation null P-values", "Unadjusted (descriptive, FDR not applicable)", "Phase B (C-S3)"], [3200, 1600, 4200]),
          tableRow(["Calibrated omega baseline", "7.70, 95% CI [7.37, 8.02] (mouse split-half, 50 replicates across six control populations, 300 omega values; data: results/mouse_splithalf_v44.csv)", "Phase C (C-M1)"], [3200, 1600, 4200]),
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
      p("The default mode (global HVG 2,000) is used only for the Tabula Muris full pairwise matrix (03_full_matrix.py, 703 pairs, Fig. 2 heatmap). The hybrid mode (per-pair k_n with per-pair top-200 DE k_f) is used for all other reported analyses: Tabula Muris pilot analyses (calibration controls + validation, 02b_pilot_v2.py), Tabula Sapiens (human), TCGA, and the Siletti brain atlas. In every dataset, k_n is computed per pair on the shared HK gene set: a sensitivity analysis contrasting this per-pair estimator with a global-k_n variant (k_n computed once from the full gene-by-cell-type pseudobulk matrix) showed that brain k_n exhibits substantial cross-pair variability (CV = 97.52%) that is poorly captured by a global mean, and that the two estimators yield substantially different omega rankings (Spearman rho = 0.142; Supplementary Fig. S7). The parameter sweep (Supplementary Figure 1) confirmed that the identity-only configuration (w1 = 1.0, w2 = 0.0) achieves the best cell-type discrimination without external pathway databases."),

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
      p("Controls: Six random-split comparisons (same cell population divided into two halves) tested baseline behavior (empirical baseline omega = 7.70, 95% CI [7.37, 8.02], from 50 split-half replicates across the six control populations, 300 omega values; data: results/mouse_splithalf_v44.csv; the legacy six-split estimate 6.67 [4.24, 9.24] is superseded; see Section 5.4 a for reproduction)."),
      p("Total pairs: 703 cell-type pairs across 6 organs."),
      p("Cross-species matching note (Supplementary Fig. S10): the mouse-human cell-type matching used for the cross-species comparison is case-insensitive exact matching over a small explicit alias table (notebooks/_ed_fig2_clean.py), because cell-type names in results/full_matrix_pairs.csv are truncated to 18 characters. This rule matches 15 shared cell types between the Tabula Muris and Tabula Sapiens annotations; case-sensitive exact-string matching alone would match 11. Re-running the comparison with a different matching rule will change the plotted cell-type set."),

      heading("4.2 Tabula Sapiens (Human) \u2014 Result 3 (Fig. 3)", 3),
      p("Dataset:    Tabula Sapiens (Jones et al., Science 2022)"),
      p("Source:     https://github.com/czbiohub-sf/tabula-sapiens (raw data; CZ CELLxGENE Discover provides the processed version used in this study)"),
      p("Technology: 10x Genomics (3\u2032 and 5\u2032 assays)"),
      p("Data used:  108,136 cells (6 h5ad files total), 102 cell-type entries (99 of which passed the pairwise-analysis filters: at least 20 cells per entry — applied downstream in notebooks/13_phase35_human_pairs.py — and at least one donor with at least 10 cells, checked in notebooks/05_phase33_v3_fixed.py; \"unknown\" annotations excluded), 6 organs (Liver, Kidney, Heart, Bone Marrow, Spleen, Lung)"),
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
      p("  1. Filter: gene-level mean expression >= 0.5 TPM within each cancer type (per-cancer independent filtering; np.mean(expr, axis=0) >= 0.5 in 06_phase34_v2.py)."),
      p("  2. log2(TPM + 1) transformation."),
      p("  3. Pseudobulk: mean expression per sample."),
      p("  4. Sample pairs drawn from: tumor-tumor (TT), normal-normal (NN), tumor-normal (TN). Maximum 2,000 random TT and TN pairs each."),
      p("  5. Per-pair k_n computed on the shared HK gene set for each sample pair."),
      p("  6. Per-pair k_f with top-200 DE genes (ranked by |mean_diff|)."),
      p("  7. NN/TT ratio computed as median(omega_NN) / median(omega_TT) per cancer type (the manuscript and Fig. 4A report the median NN/TT omega ratio)."),
      p("Clinical stratification:", { bold: true }),
      p("  LIHC Edmondson grade: G1 (n=39), G2 (n=133), G3 (n=105), G4 (n=11). Jonckheere-Terpstra trend test."),
      p("  BRCA PAM50 subtype: Basal-like (n=97), HER2 (n=55), LumA (n=224), LumB (n=123), Normal-like (n=7). Kruskal-Wallis test."),
      p("  LUAD mutation: EGFR (n=61), KRAS (n=120), WT (n=311). Kruskal-Wallis test."),

      p("Cross-organ conservation (Result 5, Fig. 5): Subset of 59 same-cell-type cross-organ pairs from Tabula Sapiens data. Ranked by mean omega per cell type."),

      heading("4.4 Siletti Brain Atlas (Human) \u2014 Result 6 (Fig. 6)", 3),
      p("Dataset:    Siletti et al. (Science 2023)"),
      p("Source:     https://github.com/linnarsson-lab/adult-human-brain (raw data; CZ CELLxGENE Discover provides the processed version used in this study, collection ID 283d65eb-dd53-496d-adb7-7570c7caa443, Nonneurons.h5ad)"),
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
      p("Note: the tier assignment above is that of the authoritative block-shuffle null pipeline (notebooks/08d_brain_blockshuffle_null.py). notebooks/07d_brain_siletti_v4.py, which computes the per-pair omega and residual values from the pseudobulks, applies a related strong-screen variant (residual < 0.3, omega < 15, and region-pair mean omega > 20); the reported Strong tier follows 08d."),

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
      p("Benjamini-Hochberg FDR correction is applied to the permutation P-values within each dataset (group-level tests: m = 10 for brain, 17 for human, 15 for mouse, 5 for TCGA). The q_value column in tcga_bootstrap_results.csv provides the BH-adjusted P-value. Caveat for the other two shipped files (see Section 6): results/superseded/human_bootstrap_results.csv is a superseded output of the broken legacy script - after regenerating it with 08b_human_bootstrap_v2.py its q_value column holds the m = 17 BH-adjusted P-values; results/superseded/brain_bootstrap_results.csv holds pre-fix values and must NOT be used - the authoritative brain cell-type statistics (with the m = 10 group-level test) are in brain_bs_null_ct_test.csv (e.g. astrocyte omega 82.75), and the per-pair screen uses brain_bs_null_results.csv (column q_fdr) under the block-shuffle null. The BH procedure is implemented in cki/bootstrap.py:benjamini_hochberg(). For the brain per-pair region-association screen, FDR correction is applied across all m = 31,764 region pairs under the block-shuffle null (Section 5.3c); the corresponding per-pair BH-adjusted P-values are in brain_bs_null_results.csv (column q_fdr), summarized in brain_bs_null_fdr_manifest.json."),

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
      p(""),
      p("  e. Post-hoc coherence checks (v40):"),
      p("     Scripts: notebooks/72_brain_setlevel_tests.py, notebooks/73_tcga_composition_check.py"),
      p("     Brain set-level checks: raw-P enrichment by effect tier (Strong 31/39 at raw P < 0.05 = 79.5% versus 6.2% overall; Cochran-Armitage dose-response z = 61.0) and thalamo-temporal axis enrichment among the 10 mature-oligodendrocyte Strong candidates, tested by a permutation procedure that resamples candidate sets of size 10 from the same 5,778-pair pool while preserving the pool's endpoint co-occurrence structure (thalamic-relay endpoint 6/10 versus a null mean of 1.95, P = 1.005e-5; temporal-fusiform 4/10 versus 0.19, P <= 1e-5; combined axis 9/10 versus 2.27, P <= 1e-5; B = 100,000; qualified by a selection-rule-matched null whose per-candidate rate test gives P = 0.005/0.001; Section 5.7e). These are post-hoc coherence checks, not FDR-controlled discovery. TCGA composition check v2: 25,306 sample-labelled NN/TT pairs regenerated with the per-cancer pipeline (TT capped at 2,000 per cancer type, all NN pairs, seed 42); the TT/NN median k_n ratio (2.18-3.70x) replicates exactly, composition deltas are larger in TT pairs and correlate with k_n (Spearman rho = 0.387 pooled; 0.23-0.52 per cancer type); adjusting for the four lineage-marker composition deltas (immune, myeloid, stromal, epithelial) with sample-level cluster bootstrap (B = 200) attenuates the tumor-pair coefficient by only -0.5% pooled (95% CI [-3.2%, +2.6%]; per-cancer BRCA -14.0%, LUSC -9.7%, LUAD -2.3%, KIRC +19.6%, LIHC +33.5%; Section 5.7a). Output: results/brain_setlevel_tests.csv, results/brain_setlevel_tests.txt, results/tcga_composition_v2.txt, results/tcga_composition_v2.csv, results/tcga_composition_pairs.csv."),

      heading("5.4 Phase C Methodological Reinforcement", 3),
      p("Three methodological analyses were performed to address reviewer concerns (Phase C):"),
      p(""),
      p("  a. Calibrated omega normalization (C-M1):"),
      p("     Script: notebooks/09c_phaseC_methodological.py"),
      p("     Calibrated omega: omega_cal = omega / 7.70 (empirical baseline from 50 split-half replicates across the six mouse control populations, 300 omega values; 95% CI [7.37, 8.02]; data: results/mouse_splithalf_v44.csv). Rescales all values so equivalent populations yield omega_cal ~ 1.0; given the width of the baseline CI, calibrated values are reported with one significant figure: brain global mean 38.55 -> omega_cal ~ 5 (range 4.8-5.2); astrocytes 82.75 -> ~ 11 (range 10.3-11.2); Bergmann glia 13.56 -> ~ 1.8. Scheme-matched split-half calibration inside the brain atlas gave an internal baseline of 9.73 (95% CI [9.03, 10.53]), ~1.3-fold higher than the mouse factor, under which Bergmann glia corresponds to omega_cal ~ 1.3 (close to the internal baseline); the Tabula Sapiens internal baseline was 7.67 (95% CI [7.39, 8.00]), inside the updated mouse CI [7.37, 8.02], so the mouse factor transfers to Tabula Sapiens but not to the brain dataset (omega_cal is dataset-relative). The legacy six-split estimate 6.67 (95% bootstrap CI [4.24, 9.24], from results/mouse_pilot_v2_results.csv, category C_control) is consistent with the updated 50-replicate estimate (CIs overlap) and is superseded. Function: cki.calibrate_omega(). Output: results/brain_bs_null_observed_pairs.csv (the authoritative observed-pair values; the earlier results/superseded/phaseC_calibration.json and results/superseded/phaseC_calibrated_omega_brain.csv predate the block-shuffle pipeline and are superseded)."),
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
      p("  l. Cross-species analysis (M-B1): Added mention in Discussion that preliminary cross-species validation was performed (Supplementary Fig. S10)."),
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
      p("     Re-derived per-pair k_f and k_n for all 31,764 brain pairs and compared four aggregation schemes. Class ordering is stable under an aggregate-first k_n estimator (Spearman rho = 0.988 vs. the reported per-pair estimator; gradient 6.51-fold vs. 6.10-fold) but not under a single global k_n (rho = 0.09; this variant is effectively a rescaling of k_f-only). The astrocyte-vs-Bergmann-glia contrast is predominantly a k_n effect (k_f differs 2.0-fold, k_n 3.2-fold). The same script performed scheme-matched split-half calibration inside the brain atlas: internal baseline 9.73 (95% bootstrap CI [9.03, 10.53]; 29 populations, B = 50 splits each, >= 200 nuclei), ~1.3-fold higher than the mouse-derived 7.70, so the mouse calibration overstates omega_cal in the brain dataset. Outputs: results/reviewer_kn_estimator_consistency.csv, results/reviewer_brain_splithalf_summary.txt, results/reviewer_brain_splithalf_raw.csv."),
      p(""),
      p("  c. Tabula Sapiens split-half calibration (C-B human):"),
      p("     Script: notebooks/43_reviewer_fix_ts_splithalf.py"),
      p("     Scheme-matched split-half calibration inside Tabula Sapiens (largest donor per (organ, cell type) group, >= 100 cells; 71 populations; B = 50 splits each): internal baseline 7.67 (95% bootstrap CI [7.39, 8.00]), which lies inside the updated mouse-derived CI [7.37, 8.02]; the mouse calibration factor is therefore transferable to Tabula Sapiens. Outputs: results/reviewer_ts_splithalf_summary.txt, results/reviewer_ts_splithalf_populations.csv."),
      p(""),
      p("  d. Lineage enrichment (C-G):"),
      p("     Script: notebooks/38_reviewer_fix_lineage_enrichment.py"),
      p("     Tested enrichment of each cell class among Strong candidates with a hypergeometric test over the 31,764 pairs. The oligodendrocyte lineage (pre-specified, 12,775 pairs, 40.2% of comparisons) shows no enrichment: 12 of 39 Strong candidates (expected 15.7; fold 0.77; hypergeometric P = 0.916; permutation P = 0.917 with B = 100,000; OPCs alone P = 0.9995). The only class with significant enrichment is microglia (16 of 39, fold 2.30, hypergeometric P = 6.0e-4, Bonferroni-corrected P = 0.006 across the ten classes). Output: results/reviewer_lineage_enrichment.txt."),
      p(""),
      p("  e. Tier-threshold sensitivity (C-D):"),
      p("     Script: notebooks/39_reviewer_fix_tier_sensitivity.py"),
      p("     Recomputed the Strong set and lineage enrichment over a 20-combination grid of residual caps (0.2-0.4) and omega caps (12-25). No combination shows oligodendrocyte-lineage enrichment (fold enrichment 0.36-1.15 across the grid; the full range including residual-cap 0.2 rows is 0-1.15, where fold 0 arises because the Strong set shrinks to a single non-lineage candidate; all hypergeometric P >= 0.43); the Strong set size ranges from 1 (residual cap 0.2) to 259 (residual cap 0.4, omega cap 25). Output: results/reviewer_tier_sensitivity.csv."),
      p(""),
      p("  f. Phase B CI regeneration:"),
      p("     Script: notebooks/44_fix_phaseB_cis.py"),
      p("     Recomputed results/phaseB_bootstrap_cis.csv from the authoritative omega sources: brain rows from results/brain_bs_null_observed_pairs.csv (astrocyte mean 82.75, matching the main text) and human rows from results/phase35_all_metrics_pairs.csv (n = 4,851); removed 16 legacy Human (per-CT) rows computed with a null-sd approximation; mouse rows preserved verbatim (downstream loaders depend on them). The data sources of notebooks/09_phaseB_statistical_upgrades.py were updated accordingly, and results/phaseC_calibrated_cis.csv was regenerated (deterministic division by 6.67, a legacy constant superseded by 7.70 in v44)."),

      p("  g. Ground-truth simulation (marrow background):"),
      p("     Script: notebooks/45_groundtruth_simulation.py"),
      p("     Ground-truth simulation injecting module shifts of known magnitude (delta = 0.125-2) into a real single-cell background (Tabula Muris FACS marrow B cells, 1,848 cells; 200 cells per group; gene set mirrors the brain pipeline). Neutral perturbations injected separately: HK-gene drift (eta = 0.25-1) and global overdispersion (epsilon = 0.3-1). Six metrics per replicate with the identical brain-analysis code path (omega, k_f, k_n, raw JS, cosine, k_f/k_total); thresholds calibrated at the 95th percentile of 200 baseline replicates; three independent module seeds; 1,750 replicates total. Key results: type-I error under neutral HK drift omega 0.000 vs raw JS 0.553 and cosine 0.580; power at delta = 1: omega 0.000 vs raw JS 0.993; AUC functional-vs-neutral: omega 0.804 (rank 1 of 6). Outputs: results/groundtruth_simulation_raw.csv, results/groundtruth_simulation_summary.csv, results/groundtruth_simulation_metrics.json."),

      p("  h. Fixed gene-panel ablation:"),
      p("     Script: notebooks/46_fixed_panel_ablation.py"),
      p("     Fixed gene-panel ablation of the brain landscape: recomputed all 31,764 same-cell-type cross-region pairs under four k_f gene-selection schemes (S0 reported per-pair top-200 DE; S1 fixed top-2,000 by global mean; S2 leave-pair-out top-200; S3 all 5,000 non-HK genes), with identical keep set, pseudobulks and k_n. The reference implementation reproduced the reported landscape exactly (max per-pair omega difference 6.4e-13). Pair-level Spearman rho vs S0: 0.918 (S1), 0.937 (S2), 0.931 (S3); class-mean ordering rho 0.90/0.99/0.93; astrocyte/Bergmann-glia ratio 6.10 (S0) versus 7.67/6.53/6.57. Circularity inflation: median k_f(S0)/k_f(S2) = 1.61 (IQR 1.27-2.07). Scheme-matched block-shuffle null under S2 (B = 200): astrocytes, OPCs and committed OPCs at the P = 0.005 permutation floor, fibroblasts P = 0.020, vascular cells P = 0.035, ependymal P = 0.164, microglia P = 0.796, oligodendrocytes P = 0.876, choroid plexus P = 0.562, Bergmann glia P = 0.980. Outputs: results/fixed_panel_ablation_pairs.csv, results/fixed_panel_ablation_ct.csv, results/fixed_panel_ablation_null_<CT>.npy, results/fixed_panel_ablation_summary.json."),


      // ========================================================
      // 5.7 V41 BLIND-REVIEW ANALYSES
      // ========================================================
      heading("5.7 v41 Blind-Review Analyses", 3),
      p("The following analyses were added for the v41 package (blind-review round on v40). All reuse the authoritative gene sets, pseudobulks, and nulls of the corresponding main analyses; no result above is altered."),
      p(""),
      p("  a. TCGA composition check v2 (four panels, cluster bootstrap):"),
      p("     Script: notebooks/74_tcga_composition_v2.py"),
      p("     Regenerated the 25,306 sample-labelled NN/TT pairs with the per-cancer pipeline (TT capped at 2,000 per cancer type, all NN pairs, seed 42) and added a myeloid panel (CD68, CD163, LST1, FCGR3A, C1QA) to the immune/stromal/epithelial panels. Within TT pairs k_n correlates with the four-panel composition difference (Spearman rho = 0.387 pooled; 0.23-0.52 per cancer type); in regressions of log k_n on pair type with the four composition deltas as covariates and sample-level cluster bootstrap (B = 200), the tumor-pair coefficient attenuates by only -0.5% pooled (95% CI [-3.2%, +2.6%]; per-cancer BRCA -14.0%, LUSC -9.7%, LUAD -2.3%, KIRC +19.6%, LIHC +33.5%). Outputs: results/tcga_composition_v2.txt, results/tcga_composition_v2.csv, results/tcga_composition_pairs.csv (the v1 three-panel check of 73_tcga_composition_check.py is superseded)."),
      p(""),
      p("  b. Simulation circularity boundaries (S1/S2):"),
      p("     Script: notebooks/75_sim_circularity_scenarios.py"),
      p("     Adversarial scenarios quantifying the anchoring assumption's boundary: with the functional module placed on HK genes, omega detects 0 of 600 replicates at every delta >= 0.25 (S1, structural blind spot), while with neutral drift placed on non-HK genes omega's false-positive rate stays <= 0.02 versus 1.00 for raw JS at eta = 1 (S2). Outputs: results/sim_circularity_summary.csv, results/sim_circularity_summary.json, results/sim_circularity_raw.csv, results/sim_circularity_report.txt."),
      p(""),
      p("  c. Per-class split-half calibration:"),
      p("     Script: notebooks/76_perclass_calibration.py"),
      p("     Class-specific split-half baselines from the 29 brain split-half populations (7.58 microglia to 12.52 committed OPCs, 1.65-fold spread); under per-class baselines the astrocyte-to-Bergmann-glia gradient is 5.99 (95% CI [4.12, 9.18] under the joint region-clustered bootstrap of notebooks/81_perclass_uncertainty.py, B = 5,000, numerator region-clustered + denominator two-stage split-half resampling; the earlier i.i.d.-numerator CI [4.86, 7.42] is anti-conservative and superseded; 9 of 10 classes have joint calibrated CIs excluding 1). Outputs: results/perclass_calibration.csv, results/perclass_calibration.json, results/perclass_calibration_report.txt, results/perclass_uncertainty.csv, results/perclass_uncertainty.json, results/perclass_uncertainty_report.txt."),
      p(""),
      p("  d. Pseudo-region negative control:"),
      p("     Script: notebooks/77_pseudoregion_control.py"),
      p("     Libraries were reassigned to synthetic pseudo-regions (half the library count per group, twice the region count); under the same block-shuffle machinery the pseudo-region tail rates (5.79% lower / 6.87% upper) closely match the real ones (6.17% / 7.90%) and same-origin pseudo-pairs are only modestly enriched (37.6%), delimiting how much of the per-pair screen could reflect library grouping alone. Outputs: results/pseudoregion_control_summary.txt, results/pseudoregion_control_summary.json, results/pseudoregion_control_pairs.csv, results/pseudoregion_control_genemodel.npz (per-CT checkpoints under results/pseudoregion_ct_ckpt/)."),
      p(""),
      p("  e. Thalamo-temporal axis permutation test:"),
      p("     Script: notebooks/78_axis_permutation_test.py"),
      p("     Endpoint-co-occurrence-preserving permutation test: candidate sets of size 10 are resampled from the same 5,778-pair oligodendrocyte pool (B = 100,000; null mean hit counts 1.95 thalamic-relay, 0.19 temporal-fusiform, 2.27 combined). Observed 6/10, 4/10, and 9/10 give P = 1.005e-5, P <= 1e-5, and P <= 1e-5. This replaces the base-rate hypergeometric P-values in the manuscript text (the set-level raw-P tier enrichment with hypergeometric P = 9.6e-31 and Cochran-Armitage z = 61.0 remains in Supplementary Note 5.1). A selection-rule-matched null (notebooks/82_axis_rule_matched_null.py, B = 1,000, the Strong rule re-evaluated on each block-shuffle permutation at the same specification as the microglia composition check) qualifies these values: the rule-matched null generates more survivors than observed (mean 43.7 vs 10), so absolute hit counts are not extreme (6 vs 6.58 P = 0.48; 9 vs 8.49 P = 0.38), while the per-candidate hit rate remains concentrated (0.60/0.90 vs 0.15/0.19; P = 0.005/0.001) - the supported claim is axis concentration of surviving candidates, not an axis excess. Outputs: results/axis_permutation_test.txt, results/axis_permutation_test.json, results/axis_rule_matched_null.txt, results/axis_rule_matched_null.json."),
      p(""),
      p("  f. Real perturbation demonstration (IFN-beta PBMC):"),
      p("     Script: notebooks/79_kang_ifnb_demo.py (analysis), notebooks/80_kang_demo_figure.py (Fig. S13)"),
      p("     Kang et al. 2018 (GSE96583) droplet-arm PBMCs: same-donor stimulated-vs-control (perturbation) and same-condition cross-donor (drift) comparisons per cell type (24,413 cells, 6 classes; HK 1,099 genes; 709 pairs). IFN-beta stimulation raises k_n itself 1.2-5.7-fold above the donor-drift level, and where it does so most strongly (CD14+ monocytes) the omega AUC falls to 0.55 while k_f retains 0.98 - an empirical demonstration of the anchor-visibility boundary. Condition is fully confounded with 10x lane in this dataset (all control cells in one lane), so only cross-metric AUC contrasts are interpreted. Outputs: results/kang_ifnb_demo_pairs.csv, results/kang_ifnb_demo_summary.json, results/kang_ifnb_demo_summary.txt, results/figures_submission/Supplementary_Figure_S13.pdf."),
      p(""),
      p("  g. Second simulation background:"),
      p("     Script: notebooks/49_groundtruth_sim_background2.py"),
      p("     The full ground-truth simulation repeated in skin keratinocyte stem cells (1,371 cells; 1,750 replicates): AUC(omega) = 0.908 versus AUC(k_f) = 0.859, reproducing the metric ranking of the marrow background. Outputs: results/groundtruth_simulation_background2_raw.csv, results/groundtruth_simulation_background2_summary.csv, results/groundtruth_simulation_background2_metrics.json, results/groundtruth_simulation_background2.csv, results/groundtruth_simulation_background2.md."),
      p(""),
      p("  h. Data-driven verification entry points:"),
      p("     Script: scripts/spot_check.py (40 assertions recomputing headline numbers directly from the authoritative result files: TCGA NN/TT median ratios and k_n inversion, mouse four-class values, brain class-level astrocyte statistics, Strong 39/31/q = 0.520, set-level S1-S3, internal baselines 9.73/7.67, 4,851 analyzed human pairs (phase35; the 5,151-row phase33_v3 export is the pre-analysis 102-class inventory), Kang CD14 omega AUC 0.55 vs k_f 0.98)."),
      p("     Script: tests/test_reference_values.py (7 pytest regression tests asserting the authoritative result files; auto-skip when results/ is absent)."),
      p(""),
      p("  i. k_f-only ordering controls (cross-organ ranking and TCGA severity):"),
      p("     Script: notebooks/83_kf_only_ordering.py"),
      p("     Recomputes the two ratio-based ordering claims with k_f alone (and k_n alone) on the identical pipelines. Cross-organ (Tabula Sapiens, 59 same-cell-type pairs, 17 cell types; reproduces phase35 summary to 3.6e-15): per-cell-type Spearman(mean omega, mean k_f) r = 0.23 (P = 0.37; r = 0.10 among the five well-sampled types), mean omega vs mean k_n r = -0.31; CD8+ T cells most conserved well-sampled type under both metrics, but the middle of the ordering does not reproduce (NK cells most divergent under omega, second-most conserved under k_f). TCGA severity (per-tumor mean of TT pairs; all 12 published stratum omega means reproduced exactly): LIHC Edmondson gradient reverses under k_f-only (k_f rises with grade, Jonckheere P = 1.1e-12, k_n rises in parallel) - denominator-driven; BRCA PAM50 ordering largely reverses under k_f-only (Luminal A lowest 0.479, Basal-like highest 0.536, KW P = 1.3e-11) - predominantly baseline-driven; only the LUAD mutation contrast persists under k_f (KW P = 0.015, KRAS highest in both omega and k_f; the EGFR elevation above wild-type is denominator-driven). Jonckheere-Terpstra note: notebook 83 uses the manual JT implementation that 07_phase34_clinical.py keeps as its scipy ImportError fallback (07 prefers scipy.stats.jttest_on_ranks, scipy >= 1.17); the two implementations share the same JT statistic with 0.5 tie credit and the same normal approximation, and the 12/12 strata sanity check was run against the published omega values produced by the scipy path. These k_f-only controls are post-hoc; their P-values are nominal and carry no multiplicity correction. Outputs: results/kf_only_ordering.csv, results/kf_only_ordering.json, results/kf_only_severity.csv, results/kf_only_ordering.txt."),

      // ========================================================
      // 5.8 V44 BLIND-REVIEW ANALYSES
      // ========================================================
      heading("5.8 v44 Blind-Review Analyses", 3),
      p("The following analyses were added for the v44 revision (blind-review round on v43). All reuse the authoritative gene sets, pseudobulks, and nulls of the corresponding main analyses; no result above is altered."),
      p(""),
      p("  a. TCGA linear-normalization robustness:"),
      p("     Script: notebooks/85_tcga_linear_norm_v44.py"),
      p("     Recomputes the TCGA pipeline (baseline omega, NN/TT inversion, k_n inversion, severity vignettes) with the linear normalization p_i = (TPM+1)/sum_j(TPM_j+1) in place of softmax over log2(TPM+1), verifying that all qualitative conclusions are normalization-independent. Outputs: results/tcga_linear_norm_v44_* (summary in results/tcga_linear_norm_v44_report.md)."),
      p(""),
      p("  b. TCGA composition check under linear normalization:"),
      p("     Script: notebooks/86_tcga_composition_linear_norm_v44.py"),
      p("     Repeats the four-panel composition analysis (immune, myeloid, stromal, epithelial) under the linear-normalization mapping with sample-level cluster bootstrap. Outputs: results/tcga_composition_v44.txt, results/tcga_composition_v44.csv."),
      p(""),
      p("  c. Cross-organ rank-correlation confidence interval:"),
      p("     Script: notebooks/87_cross_organ_rho_ci_v44.py"),
      p("     Organ-clustered bootstrap (B = 1,000, seed 42) 95% CI for the Spearman correlation between per-cell-type mean omega and mean k_f across the 59 same-cell-type cross-organ pairs. Outputs: results/cross_organ_rho_ci_v44.csv, results/cross_organ_rho_ci_v44.json."),
      p(""),
      p("  d. Brain confounder controls, downsample, and threshold sensitivity:"),
      p("     Script: notebooks/86_brain_downsample_threshold_v44.py"),
      p("     Tests k_n and omega against class-size and detection-depth confounders, re-runs the class gradient under equal-n downsampling (all classes to 4,118 nuclei, 20 replicates), and sweeps the min-nuclei threshold (t = 10/20/50/100). Outputs: results/brain_v44_* (summary in results/brain_downsample_threshold_v44_report.md)."),
      p(""),
      p("  e. Mouse split-half calibration (50 replicates):"),
      p("     Script: notebooks/87_mouse_splithalf_v44.py"),
      p("     Repeats the split-half calibration 50 times across the six FACS control populations (300 omega values), yielding the updated calibration constant 7.70 (95% CI [7.37, 8.02]) that supersedes the legacy six-split estimate 6.67. Outputs: results/mouse_splithalf_v44.csv, results/mouse_splithalf_v44_summary.json."),
      p(""),
      p("  f. Competitor benchmark (MELD, scDist approximation):"),
      p("     Script: notebooks/101_competitors_v44.py"),
      p("     Benchmarks CKI against MELD 1.0.2 and a Python approximation of scDist on the Kang IFN-beta PBMC data and additive mean-shift simulations, including donor-paired power curves that delimit the per-donor working range. Outputs: results/competitors_v44_* (summary in results/competitors_v44_report.md)."),

      // ========================================================
      // 6. OUTPUT FILES
      // ========================================================
      heading("6. Output Files", 2),
      p("All results are written to results/. Ten pre-fix output files whose values contradict the manuscript are consolidated under results/superseded/ (v42 P0-6, three-reviewer consensus); they are retained for provenance and ship with the release tag, but must not be used as numerical sources - each entry below marks the authoritative replacement."),
      p(""),
      p("    Mouse (02b_pilot_v2.py, authoritative pilot and calibration output; the v2b re-validation 02c_pilot_v2b.py writes the parallel *v2b_* files):"),
      code("      results/mouse_pilot_v2_results.csv        # omega per pair (authoritative; feeds the legacy 6.67 baseline, superseded by results/mouse_splithalf_v44.csv, 7.70)"),
      code("      results/mouse_pilot_v2_key_values.csv   # k_n, k_f, omega per comparison"),
      code("      results/mouse_pilot_v2b_results.csv       # v2b re-validation (memory-fixed re-run)"),
      code("      results/mouse_pilot_v2b_key_values.csv  # v2b per-comparison key values"),
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
      p("      row-allocation fix and are SUPERSEDED - moved to results/superseded/"),
      p("      in v42. Their values (e.g. astrocyte omega 103.08, Bergmann glia"),
      p("      16.42, min k_n 7.7 × 10⁻⁵) contradict the manuscript. All authoritative"),
      p("      post-fix brain numbers are in brain_bs_null_observed_pairs.csv /"),
      p("      brain_bs_null_results.csv and the reviewer_brain_* files"),
      p("      (astrocyte 82.75, Bergmann glia 13.56, min k_n 9.2e-5)."),
      code("      results/superseded/brain_siletti_omega_pairs_v3.csv # all region-pair omega values [SUPERSEDED - pre-v38.1]"),
      code("      results/superseded/brain_siletti_ct_summary_v3.csv  # per-cell-type mean omega [SUPERSEDED - pre-v38.1]"),
      code("      results/superseded/brain_siletti_key_values_v3.csv  # per-cell-type global summary [SUPERSEDED - pre-v38.1]"),
      code("      results/superseded/brain_siletti_migration_candidates_v3.csv # region-associated candidate list [SUPERSEDED - pre-v38.1]"),
      p(""),
      p("    Permutation tests (08a_tcga_bootstrap.py, 08b_human_bootstrap_v2.py, 08c_brain_bootstrap_v3.py; output file names retain the historical *_bootstrap_* naming):"),
      p("      NOTE: two of the three CSV files below are shipped under"),
      p("      results/superseded/ as PRE-FIX outputs and are SUPERSEDED. (1) human_bootstrap_results.csv"),
      p("      was produced by the broken legacy 08b_human_bootstrap_csv.py, which bootstrapped"),
      p("      pre-computed omega values and yielded uninformative P-values near 0.5 for every"),
      p("      group; regenerate it by re-running 08b_human_bootstrap_v2.py (cell-level label"),
      p("      permutation, which recreates the corrected file at results/human_bootstrap_results.csv)."),
      p("      (2) brain_bootstrap_results.csv holds pre-fix cell-type values (e.g. astrocyte"),
      p("      omega 83.64, OPC 40.83) that contradict the manuscript; all authoritative brain"),
      p("      statistics are in brain_bs_null_ct_test.csv (astrocyte 82.75, OPC 40.62) and the"),
      p("      other brain_bs_null_* files from the 08d/08e block-shuffle null (Section 5.3c)."),
      code("      results/tcga_bootstrap_results.csv           # TCGA permutation P-values (B=1000)"),
      code("      results/superseded/human_bootstrap_results.csv # Human permutation P-values (B=1000) [SUPERSEDED - pre-fix output; regenerate with 08b_human_bootstrap_v2.py]"),
      code("      results/superseded/brain_bootstrap_results.csv # Brain permutation P-values (B=1000) [SUPERSEDED - pre-fix values; authoritative brain stats in brain_bs_null_ct_test.csv]"),
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
      code("      results/superseded/phaseB_residual_null.json  # Permutation null summary (C-S3; superseded by block-shuffle null)"),
      code("      results/superseded/phaseB_residual_pervisign.csv # Per-signal P-values (C-S3; superseded by block-shuffle null)"),
      code("      results/figures_final/ed_fig8_omega_distribution.pdf  # Distribution figure"),
      code("      results/figures_final/ed_fig9_residual_null.pdf      # Residual null figure"),
      p(""),
      p("    Phase C Methodological Reinforcement (09c_phaseC_methodological.py):"),
      code("      results/superseded/phaseC_calibration.json   # Calibrated omega summary (C-M1; superseded by block-shuffle observed pairs)"),
      code("      results/superseded/phaseC_calibrated_omega_brain.csv # Calibrated omega per brain pair (C-M1; superseded by block-shuffle observed pairs)"),
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
      p(""),
      p("    v41 blind-review analyses (Section 5.7):"),
      code("      results/tcga_composition_v2.txt / .csv          # TCGA composition check v2 (four panels, cluster bootstrap B = 200)"),
      code("      results/sim_circularity_*                       # S1/S2 adversarial circularity scenarios"),
      code("      results/perclass_calibration.csv / .json / _report.txt  # per-class split-half baselines and gradient"),
      code("      results/perclass_uncertainty.csv / .json / _report.txt  # joint region-clustered bootstrap CIs (Section 5.7c)"),
      code("      results/axis_rule_matched_null.txt / .json      # selection-rule-matched axis null (Section 5.7e)"),
      code("      results/pseudoregion_control_*                   # pseudo-region negative control (+ pseudoregion_ct_ckpt/)"),
      code("      results/axis_permutation_test.txt / .json        # endpoint-co-occurrence axis permutation test"),
      code("      results/kang_ifnb_demo_*                         # IFN-beta PBMC real-perturbation demonstration"),
      code("      results/groundtruth_simulation_background2_*     # second-background simulation replication"),
      code("      results/kf_only_ordering.* / kf_only_severity.csv  # k_f-only ordering controls (Section 5.7i)"),
      p(""),
      p("    v44 blind-review analyses (Section 5.8):"),
      code("      results/tcga_linear_norm_v44_*                  # TCGA linear-normalization robustness (Section 5.8a)"),
      code("      results/tcga_composition_v44.txt / .csv         # composition check under linear normalization (Section 5.8b)"),
      code("      results/cross_organ_rho_ci_v44.csv / .json      # organ-clustered bootstrap CI for rho(omega, k_f) (Section 5.8c)"),
      code("      results/brain_v44_*                              # brain confounder/downsample/threshold analyses (Section 5.8d)"),
      code("      results/mouse_splithalf_v44.csv / _summary.json  # 50-replicate split-half calibration, omega = 7.70 [7.37, 8.02] (Section 5.8e)"),
      code("      results/competitors_v44_*                        # MELD / scDist-approximation benchmark (Section 5.8f)"),
      p(""),
      p("Figure scripts: notebooks/30_genome_biology_figures.py"),
      heading("7. Reproducibility Checklist", 2),
      p("[\u2713] Install CKI v0.4.7: pip install -e ."),
      p("[\u2713] Verify Python 3.14.4 environment (Section 1.1)."),
      p("[\u2713] Verify random seed = 42 in all analysis scripts (fixed exceptions: notebooks 77/78/79 use seed 20260903)."),
      p("[\u2713] Verify HK gene source: HRT Atlas v1.0 reference (cki/data/hrt_atlas.csv, shipped; analysis scripts read the byte-identical downloaded copy data/housekeeping/Human_Mouse_Common.csv), loaded directly for all datasets."),
      p("[\u2713] Verify identity gene parameters: HVG seurat flavor, n=2000, HK excluded."),
      p("[\u2713] Verify permutation iterations: 1000 (mouse, main), 1000 (human, 08b_human_bootstrap_v2.py), 1000 (TCGA, 08a), 1000 (brain, 08c_brain_bootstrap_v3.py; authoritative brain statistics come from the 08d/08e block-shuffle null)."),
      p("[\u2713] Verify normalization: CP10k + log1p."),
      p("[\u2713] Verify softmax normalization before JS divergence (equivalent to a +1 pseudo-count followed by L1 normalization on the linear scale; cki/utils.py)."),
      p("[\u2713] Verify the omega positivity guard (kn <= 0 -> inf; kn_floor = 1e-4 in the TCGA pipeline)."),
      p("[\u2713] Verify one-sided permutation test with pseudocount +1 (P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1))."),
      p("[\u2713] For mouse pilot/human/TCGA/brain: verify k_n is computed per pair on the shared HK gene set and per-pair k_f uses top-200 DE genes."),
      p("[\u2713] For brain: verify min_cells_per_group = 20."),
      p("[\u2713] Note: Benjamini-Hochberg FDR correction is applied within each dataset. BH-adjusted P-values are available in tcga_bootstrap_results.csv (and in human_bootstrap_results.csv once it is regenerated with 08b_human_bootstrap_v2.py); for the brain use brain_bs_null_ct_test.csv (cell-type level) and brain_bs_null_results.csv (q_fdr, per pair) instead of the superseded results/superseded/brain_bootstrap_results.csv. (Section 5.2)"),
      p("[\u2713] Phase B: Verify bootstrap CIs (B=10,000) in results/phaseB_bootstrap_cis.csv. (Section 5.3)"),
      p("[\u2713] Block-shuffle null: Verify B=1,000 in results/brain_bs_null_fdr_manifest.json (39 Strong candidates, 31 with raw P<0.05, minimum q=0.520). (Section 5.3)"),
      p("[\u2713] Phase B: Verify omega distribution characterization in results/phaseB_omega_distribution.json. (Section 5.3)"),
      p("[\u2713] Phase C: Verify calibrated omega (omega/7.70, 95% CI [7.37, 8.02]; data: results/mouse_splithalf_v44.csv): brain mean 38.55 -> omega_cal ~ 5, astrocytes 82.75 -> ~ 11, Bergmann glia 13.56 -> ~ 1.8 (results/brain_bs_null_observed_pairs.csv); verify internal split-half baselines 9.73 [9.03, 10.53] (brain) and 7.67 [7.39, 8.00] (Tabula Sapiens) in results/reviewer_brain_splithalf_summary.txt and results/reviewer_ts_splithalf_summary.txt. (Section 5.4/5.6)"),
      p("[\u2713] Phase C: Verify dimensionality invariance in results/phaseC_dimensionality.json (ratio ~1.001). (Section 5.3)"),
      p("[\u2713] Phase C: Verify k_n variability (CV=97.52%) in results/phaseC_kn_variability.json. (Section 5.4)"),
      p("[\u2713] Phase C: Verify calibrate_omega() function in cki/core.py is importable."),
      p("[\u2713] Phase D: Verify TCGA paired analysis has no formal P-value (descriptive only). (Section 5.5)"),
      p("[\u2713] Phase D: Verify cross-organ ranking flags n<5 cell types. (Section 5.5)"),
      p("[\u2713] Phase D: Verify one-sided test justification in Methods. (Section 5.5)"),
      p("[\u2713] Phase D: Verify Cover Letter does not use 'orthogonal' or 'confirmed baseline behavior'. (Section 5.5)"),
      p("[\u2713] Phase D: Verify figure legends include 'Statistical conventions' paragraph. (Section 5.5)"),
      p("[\u2713] Data-driven spot-check: python scripts/spot_check.py (40 assertions recomputing headline numbers directly from the authoritative result files; Section 5.7h)."),
      p("[\u2713] Regression tests: python -m pytest tests/ -q (7 tests asserting the authoritative result files; auto-skip when results/ is absent; Section 5.7h)."),

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
