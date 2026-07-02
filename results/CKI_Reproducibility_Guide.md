Supplementary Methods: CKI Computational Reproducibility Guide
==============================================================

Li Zhang1,2,*

1 Institute of Blood Transfusion, Chinese Academy of Medical Sciences &
  Peking Union Medical College, Chengdu, China
2 Chinese Institute for Brain Research, Beijing, China
* Correspondence: knightz@pumc.edu.cn


1. SOFTWARE ENVIRONMENT
-----------------------

This reproducibility package was developed and tested with the exact
versions listed below. Using different versions may produce different
numerical results.

1.1 Python and Core Packages
    (verified environment)

    Python:              3.13.12  (MSC v.1944 64 bit, AMD64)
    numpy:               2.4.6
    scipy:               1.17.1
    pandas:              2.3.3
    matplotlib:          3.10.9
    scikit-learn:        1.8.0
    python-docx:         1.2.0

1.2 CKI Package

    Version:             0.3.1  (editable install from project root)
    Repository:          https://github.com/zhanglknt/CKI-cell-type-identification

    Install:
      cd <project_root>
      pip install -e .

1.3 System Requirements

    Operating system:    Windows 10/11 x64 (also tested on Linux x86_64)
    Memory:              >= 32 GB RAM recommended (TCGA matrix ~10 GB peak)
    Disk space:          >= 5 GB (for TCGA TPM.gz and intermediate files)
    Network:             Internet access for data downloads and cBioPortal API

1.4 Data Dependencies

    The cloned repository includes the pre-specified housekeeping gene
    file at data/housekeeping/Human_Mouse_Common.csv (see Section 3.1).
    All analysis scripts reference HK genes from this file by relative
    path; no additional download or configuration is needed.

    External data downloads required (detailed in each analysis section):
    - TCGA TPM:     https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz (~3.2 GB)
    - TCGA probeMap: https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/probeMap%2Fhugo_gencode_good_hg38_v22comp12%2Fgencode.v22.annotation.genes.probeMap (~1.5 MB)
    - LIHC clinical: cBioPortal API (lihc_tcga study) — bundled in data/tcga/
    - LUAD mutations: cBioPortal API (luad_tcga study) — bundled in data/tcga/
    - BRCA PAM50:    cBioPortal API (brca_tcga_pub study) — fetched live by script

    All analyses use random seed 42 throughout.


2. CKI ALGORITHM DEFINITION
----------------------------

CKI decomposes transcriptomic divergence into two components:

    omega = k_f / k_n    (kn=0 → ω=∞)

where:

    k_n  = JS(p_HK_A || p_HK_B)       ... neutral offset rate
    k_f  = JS(p_ID_A || p_ID_B)       ... functional conversion rate

and JS(P || Q) is the Jensen-Shannon divergence (natural log):

    M     = 0.5 * (P + Q)
    JS(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)

    where KL(P || M) = sum_i [ P_i * ln(P_i / M_i) ] for P_i > 0

Both k_n and k_f use the same computational pipeline:
(1) Subset the pseudobulk expression vector to the relevant gene indices.
(2) Convert expression values into a probability distribution via the
    CKI `ensure_probability_distribution()` function. In "auto" mode
    (the default), the method is selected based on the data range:
    - Non-negative values: sum-normalization (p_i = x_i / sum_j x_j).
      This is used for all CP10k+log1p-normalized data (mouse, human,
      brain), which are non-negative after transformation.
    - Any negative values: softmax (p_i = exp(x_i - max) / sum_j
      exp(x_j - max), with epsilon=1e-9 in the denominator to prevent
      division-by-zero). This is automatically selected for log2-
      transformed data (TCGA), where the +0.001 offset still allows
      small negative values.
(3) Compute JS divergence between the two resulting distributions.

Both methods produce valid probability distributions for JS divergence;
the auto-switching behavior is an implementation detail that has no
substantive effect on the results (see Supplementary Figure 1 for
normalization sensitivity analysis).


3. GENE SET SELECTION
---------------------

3.1 Housekeeping Genes (for k_n)

In the analyses reported here, housekeeping (HK) genes were
auto-detected per dataset using the CKI `detect_housekeeping_genes()`
function with the "combined" method:

  - Detection rate > 0.9 (> 90% of cells express the gene)
  - CV (coefficient of variation) < 30th percentile (lowest
    expression variability)
  - use_reference=True: union with HRT Atlas reference set

Note: CKI `detect_housekeeping_genes()` defaults are
`method="combined", use_reference=False`. All analysis scripts in this
study override the default by explicitly passing `use_reference=True`
(and `method="combined"`) to ensure the HRT Atlas reference is merged.

The reference file is:

  data/housekeeping/Human_Mouse_Common.csv
  (1,130 orthologous gene pairs; Mouse column = mouse genes,
  Human column = human genes; this file is identical in content
  to the bundled cki/data/hrt_atlas.csv shipped with the CKI
  package)

For each dataset, HK genes were loaded as follows:

    Tabula Muris (mouse):  auto-detected (combined criterion);
                              HRT Atlas mouse genes (column 0)
                              merged via union; intersected with
                              data gene names

    Tabula Sapiens (human):  auto-detected (combined criterion);
                              HRT Atlas human genes (column 1)
                              merged via union; intersected with
                              common gene set

    TCGA (human):           auto-detected (combined criterion);
                              HRT Atlas human genes (column 1)
                              merged via union; mapped via probeMap
                              to Ensembl IDs, then intersected with
                              data genes

    Siletti Brain (human):  auto-detected (combined criterion);
                              HRT Atlas human genes (column 1)
                              merged via union; matched to
                              var["Gene"] in the h5ad file

Note: The `use_reference=True` flag merges the HRT Atlas reference
set with the auto-detected HK genes via set union, ensuring both
empirically stable genes and literature-curated housekeeping genes
are included. This approach balances data-driven selection with
biological prior knowledge.

3.2 Identity Genes (for k_f)

Identity (functional) genes are defined as:

    Default (CKI):    top-2,000 highly variable genes (HVGs; Scanpy
                      ``flavor='seurat'``), with HK genes explicitly
                      excluded (adapted to min(2000, 0.8 * n_total_genes)).
                      Used only in the mouse full pairwise analysis
                      (03_full_matrix.py, heatmap in Fig. 2). All other
                      analyses (mouse pilot, human, TCGA, brain) use the
                      per-pair top-200 DE approach (hybrid mode, below).

    Hybrid mode:      ``func_method='pairwise_de'``. global k_n computed
                      once with shared HK gene set; per-pair k_f uses the
                      top-200 differentially expressed genes (ranked by
                      |mean_diff| between the two groups), excluding HK
                      genes, via ``n_top_genes=200``

The hybrid mode is used in all four analyses to give
each cell-type pair the most informative identity genes while keeping
all pairs on a common k_n scale. The parameter sweep (Supplementary
Figure 1) confirmed that the identity-only configuration (w1 = 1.0,
w2 = 0.0) achieves the best cell-type discrimination without external
pathway databases.

  

3.3 Script-to-Manuscript Results Mapping
--------------------------------------

  This section clarifies which notebook scripts produce the results
  reported in the manuscript, and which scripts are exploratory
  (older designs that do not match the manuscript numbers).

  All scripts listed below are in the `notebooks/` directory.
  Scripts marked "Exploratory" are retained for reference but
  their output does NOT correspond to manuscript values.

  +----------+-------------+------------------+---------------------+
  | Dataset  | Manuscript | Primary script  | Output CSV(s)       |
  |          | Figure       |                  |                     |
  +----------+-------------+------------------+---------------------+
  | Mouse    | Results 1-2, | `02b_pilot_v2.py`  | `mouse_pilot_v2_results.csv` |
  | (pilot)  | Fig. 2      | `02c_pilot_v2b.py` | `mouse_pilot_v2b_results.csv` |
  +----------+-------------+------------------+---------------------+
  | Mouse    | Fig. 2      | `03_full_matrix.py` | `full_matrix_omega.csv` |
  | (full    | heatmap     |                  | `full_matrix_pairs.csv` |
  |  pairwise)|             |                  |                     |
  +----------+-------------+------------------+---------------------+
  | Human    | Fig. 3      | `05_phase33_v3_fixed.py` | `phase33_v3_human_omega.csv` |
  +----------+-------------+------------------+---------------------+
  | TCGA     | Fig. 4      | `06_phase34_v2.py` | `phase34_v2_summary.csv` |
  | (tumor   | (tumor      |                  | `phase34_v2_all_pairs.csv` |
  |  vs      |  vs normal) |                  |                     |
  |  normal) |             |                  |                     |
  +----------+-------------+------------------+---------------------+
  | TCGA     | Fig. 4      | `07_phase34_clinical.py` | `phase34_clinical_severity.csv` |
  | (clinical)| (clinical   |                  |                     |
  |  severity)|  severity)  |                  |                     |
  +----------+-------------+------------------+---------------------+
  | Brain    | Fig. 5      | `07c_brain_siletti_v3.py` | `brain_siletti_omega_pairs_v3.csv` |
  +----------+-------------+------------------+---------------------+
  | Method   | Fig. 4      | `13_phase35_method_comparison.py` | `phase35_all_metrics_pairs.csv` |
  | comparison| (AUC)       |                  | `phase35_cross_organ_conservation.csv` |
  +----------+-------------+------------------+---------------------+
  | Bootstrap| Fig. 2-3    | `08a_tcga_bootstrap.py` | `tcga_bootstrap_results.csv` |
  |          | (significance)| `08b_mouse_bootstrap.py` | `mouse_pilot_v2b_bootstrap.csv` |
  +----------+-------------+------------------+---------------------+

  Exploratory scripts (do NOT match manuscript numbers):

  - `01_pilot_mouse.py`
      Tissue-level CKI only (not cell-type-level).
      Uses a different control design (split by mouse ID at tissue level).
      Replaced by `02b`/`02c` in the manuscript.

  - `02_ct_pilot.py`
      Early cell-type-level pilot with random-split control.
      The manuscript uses mouse-ID-split control (`02c_pilot_v2b.py`)
      which is more biologically meaningful.
      [Bug fixed in v0.3.2: `fname`→`fname` typo on line 72.]

  - `04_phase32_sweep.py`
      Parameter sweep over w1/w2 weights for multi-component k_f.
      The sweep result is NOT exactly reproducible because
      `gsp.utils.download_library('H', 'Mouse')` downloads the
      latest MSigDB Hallmark definitions at runtime, and pathway
      gene sets can change between MSigDB releases.
      The manuscript reports sweep results with MSigDB Hallmark v7.5.
      To reproduce exactly, use the bundled `results/phase32_sweep_results.csv`
      instead of re-running the sweep.
      [Bug fixed in v0.3.2: `fname`→`fname` typo on line 69.]

  Recommended reproduction workflow:
  1. Run `02b_pilot_v2.py` → `02c_pilot_v2b.py` → `03_full_matrix.py`
     to reproduce all mouse results (Fig. 2, Results 1-2).
  2. For the parameter sweep, use the bundled `phase32_sweep_results.csv`
     rather than re-running `04_phase32_sweep.py`.
  3. All other scripts (`05` through `08`) reproduce manuscript results
     exactly when run with the provided data and CKI v0.3.1.

  

4. DATA SOURCES & PREPROCESSING
--------------------------------

4.1 Tabula Muris (Mouse) — Result 2 (Fig. 2)

    Dataset:     Tabula Muris FACS (Schaum et al., Nature 2018)
    Source:      https://github.com/czbiohub-sf/tabula-muris
    Technology:  SmartSeq2
    Data used:   17,957 cells, 23,433 genes (raw data
                 dimensions before QC); 15,057 cells,
                 22,308 genes (after QC and intersection
                 across 6 organs)

    Processing:
      1. Load per-tissue count matrices (e.g., FACS/FACS/Liver-counts.csv,
         FACS/FACS/Kidney-counts.csv, etc.; note double FACS/ directory layer).
      2. Intersect to common gene set across all tissues.
      3. Quality control: sc.pp.filter_cells(min_genes=500),
         sc.pp.filter_genes(min_cells=3).
      4. Normalize: sc.pp.normalize_total(target_sum=1e4), then log1p.
      5. Pseudobulk: mean expression per cell-type annotation.
      6. Filter: cell types with < 20 cells excluded
         (MIN_CELLS_PER_CT = 10; main filtering uses MIN_CELLS_PER_CT * 2 = 20).

    Pilot analysis (targeted comparisons with bootstrap):
      7. Compute global k_n on all cell-type pseudobulks (shared HK set).
      8. Compute per-pair k_f with top-200 DE genes for 15 targeted
         comparisons: 6 control (within-cell-type random-split), 4
         same-cell-type cross-organ, 3 different-cell-type, and 2
         cross-organ. See notebooks/02c_pilot_v2b.py.
      9. Bootstrap: n = 500 permutations, two-sided test per pair.

    Full pairwise analysis (no bootstrap):
      All 703 cell-type pairs (38 choose 2) produced by the separate
      script notebooks/03_full_matrix.py, which computes omega for
      every pair without bootstrap, used for the heatmap and
      hierarchical clustering in Fig. 2. Output:
      results/full_matrix_*.csv.

    Controls:  Six random-split comparisons (within same cell
    population) tested neutral behavior (omega ~ 1).

    Total pairs:  703 cell-type pairs (38 choose 2) across 6 organs
    (from the full pairwise analysis; pilot uses 15 targeted pairs).

    How to re-run:
      # Download data (Tabula Muris FACS counts)
      git clone https://github.com/czbiohub-sf/tabula-muris.git data/tabula-muris
      # Run pilot analysis (15 targeted comparisons with bootstrap)
      python notebooks/02c_pilot_v2b.py
      # Run full pairwise analysis (703 pairs, no bootstrap;
      #   independent script, does not require pilot output)
      python notebooks/03_full_matrix.py

    Expected output: results/mouse_pilot_v2b_*.csv (pilot);
      results/full_matrix_*.csv (full pairwise)

4.2 Tabula Sapiens (Human) — Result 3 (Fig. 3)

    Dataset:     Tabula Sapiens (Jones et al., Science 2022)
    Source:      https://github.com/czbiohub-sf/tabula-sapiens
    Technology:  10x Genomics (3' and 5' assays)
    Data used:   108,136 cells (sum across 6 h5ad files; verified
                 by script loading; see 05_phase33_v3_fixed.py comments
                 for per-organ cell counts), 102 cell-type entries,
                 6 organs (Liver, Kidney, Heart, Bone Marrow,
                 Spleen, Lung)

    Processing:

      1. Load per-organ h5ad files (TS_{Organ}.h5ad; e.g.,
         TS_Liver.h5ad, TS_Kidney.h5ad, etc.).
      2. Intersect to common gene set across all 6 organs.
      3. Within each organ: sc.pp.filter_cells(min_genes=500), then
         normalize: sc.pp.normalize_total(target_sum=1e4), log1p.
      4. Filter: cell-type/donor groups with < 10 cells excluded
         (MIN_CELLS_PER_CT = 10).
      5. Pseudobulk: mean expression per cell_ontology_class.
      6. Global k_n: JS divergence on full pseudobulk matrix with shared HK set.
      7. Per-pair k_f: top-200 DE genes (ranked by absolute mean
         difference), HK genes excluded.
      8. Full pairwise omega computed for all 5,151 cell-type pairs.

    Method comparison: Spearman rank correlation computed between CKI
    omega and four standard metrics on all 5,151 pairs:
      - Raw JS divergence (all genes)
      - Spearman distance (1 - Spearman r)
      - Cosine distance (1 - cosine similarity)
      - Marker Jaccard distance (1 - intersection/union of top-200
        marker genes per cell type)

    Classification: AUC from cell-type pair classification task
    (same-type vs. different-type) computed with sklearn.metrics.
    roc_auc_score.

    How to re-run:
      # Download Tabula Sapiens h5ad files from Figshare:
      #   https://figshare.com/projects/Tabula_Sapiens/100973
      #   Place h5ad files in data/ts_human/
      #   (e.g., TS_Liver.h5ad, TS_Kidney.h5ad, TS_Heart.h5ad,
      #    TS_Bone_Marrow.h5ad, TS_Spleen.h5ad, TS_Lung.h5ad)
      python notebooks/05_phase33_v3_fixed.py

    Expected output: results/phase33_v3_human_*.csv

    Cross-organ conservation (Fig. 5):

    This analysis uses the same Tabula Sapiens pseudobulks to identify
    60 same-cell-type cross-organ pairs and rank cell types by their
    transcriptional conservation across organs.

    Processing:
      1. Starting from the human pseudobulks (Section 4.2 above),
         identify all pairs where the same cell type appears in two
         different organs (e.g., macrophage in Liver vs Bone Marrow).
      2. Compute CKI omega, raw JS divergence, Spearman distance,
         cosine distance, and marker Jaccard distance for each of
         these 60 cross-organ pairs.
      3. Rank cell types by their mean cross-organ omega. Lower omega
         indicates higher cross-organ conservation (the cell type's
         transcriptional program is less organ-dependent).
      4. Compute Spearman rank correlations between the CKI ranking
         and rankings from the four standard metrics.

    Script:           notebooks/13_phase35_method_comparison.py
    Input requirement: Tabula Sapiens h5ad files (same as Section 4.2;
                       must complete 05_phase33_v3_fixed.py first)
    Output:           results/phase35_cross_organ_conservation.csv
    (60 rows  x  7 columns: ct, organ_i, organ_j, omega, js_raw,
     spearman, cosine, marker_jaccard)

    Expected results:
      - 60 same-CT cross-organ pairs across 6 organs
      - Most conserved: immune cells (macrophage omega_mean ~9.8,
        T cells ~8–12)
      - Most variable: structural cells (erythrocyte, endothelial)
      - CKI ranking vs standard metrics: Spearman r = -0.13 to +0.02
        (little agreement, because CKI normalizes for neutral drift)

    How to re-run:
      # Same data as Section 4.2 (Tabula Sapiens h5ad files)
      python notebooks/13_phase35_method_comparison.py

    Expected output:
      - results/phase35_cross_organ_conservation.csv
      - results/phase35_all_metrics_pairs.csv
      - results/phase35_metric_correlation.csv

4.3 TCGA (Human Cancer) — Result 4 (Fig. 4)

    Dataset:     TCGA Pan-Cancer (Hutter & Zenklusen, Cell 2018;
                 Liu et al., Cell 2018)
    Source:      UCSC Xena (https://xenabrowser.net/)
                 File: tcga_RSEM_gene_tpm.gz
                 Direct download mirror:
                 https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz
    Data used:   10,535 samples available; 3,596 after filtering, across 5 cancer types:
                 LUAD (lung adenocarcinoma), LUSC (lung squamous),
                 LIHC (liver hepatocellular), KIRC (kidney clear cell),
                 BRCA (breast invasive)

    Processing:
      1. Filter: gene-level mean expression >= 0.5 TPM within each
         cancer type (per-cancer independent filtering).
      2. log2(TPM + 0.001) transformation.
      3. Pseudobulk: mean expression per sample.
      4. Sample pairs drawn from: tumor-tumor (TT), normal-normal (NN),
         tumor-normal (TN). Maximum 2,000 random TT and 2,000 TN pairs
         per cancer type (10,000 each total across 5 cancers).
      5. Global k_n computed once per cancer type using shared HK genes.
      6. Per-pair k_f with top-200 DE genes (ranked by |mean_diff|).
      7. TN_Baseline computed as mean(omega_TN) / baseline,
         where baseline = (mean(omega_TT) + mean(omega_NN)) / 2,
         per cancer type.

    Paired/Unpaired & Clinical stratification:
      Script: notebooks/07_phase34_clinical.py
      This script performs two additional analyses:

      (A) Paired vs Unpaired Tumor-Normal comparison:
          - Identifies patients with both tumor and normal samples
          - Computes paired TN omega (same patient) vs unpaired TN omega
          - Reports paired/unpaired ratio and Mann-Whitney P-values
          per cancer type

      (B) Clinical severity stratification:
          - LIHC Edmondson grade: G1-G4 from cBioPortal (lihc_tcga,
            GRADE attribute). Jonckheere-Terpstra trend test.
          - BRCA PAM50 subtype: fetched live from cBioPortal API
            (brca_tcga_pub study, PAM50_SUBTYPE attribute).
            Subtypes: Basal-like, HER2-enriched, Luminal A,
            Luminal B, Normal-like. Kruskal-Wallis test.
          - LUAD EGFR/KRAS mutation: from bundled data/tcga/
            luad_egfr_kras_mutations.json.
            Kruskal-Wallis test.

    How to re-run:
      # 1. Download TCGA TPM data from UCSC Xena:
      #    https://xenabrowser.net/datapages/?dataset=tcga_RSEM_gene_tpm
      #    or direct download:
      #    https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz
      #    Save as data/tcga/tcga_RSEM_gene_tpm.gz

      # 2. Run main TCGA omega analysis (TT, NN, TN):
      python notebooks/06_phase34_v2.py

      # 3. Run paired/unpaired + clinical stratification:
      python notebooks/07_phase34_clinical.py

    Expected output:
      - results/phase34_v2_*.csv              (main omega results)
      - results/phase34_clinical_paired_unpaired.csv
      - results/phase34_clinical_severity.csv
      - results/phase34_clinical_plots.png
      - results/phase34_clinical_report.md

4.4 Siletti Brain Atlas (Human) — Results 5 & 6 (Fig. 5 & 6)

    Dataset:     Siletti et al. (Science 2023)
    Source:      https://github.com/linnarsson-lab/adult-human-brain
    Data:        https://zenodo.org/records/7865491 (Nonneurons.h5ad, ~4.4 GB)
    Technology:  snRNA-seq (10x Genomics)
    Data used:   888,263 non-neuronal nuclei, ~100 brain regions,
                 10 cell classes (Astrocyte, Oligodendrocyte,
                 Oligodendrocyte precursor, Microglia, Vascular,
                 Fibroblast, Ependymal, Choroid plexus, Committed
                 oligodendrocyte precursor, Bergmann glia)

    Processing:
      1. Load Nonneurons.h5ad (full load into memory; ~4.4 GB file,
         >= 16 GB RAM recommended). For memory-limited
         environments, backed mode can be enabled by adding
         `backed='r'` to `sc.read_h5ad()`.
      2. Map gene symbols from var["Gene"]; match HK genes from HRT
         Atlas (1,129 unique human genes after set() deduplication;
         the 1,130-row file contains 1 duplicate mapping where mouse
         genes Hdhd2 and Ier3ip1 both map to human IER3IP1) to gene
         symbol column. After intersection with brain gene symbols,
         1,115 HK genes were matched.
      3. Group by (cell_type, brain_region). Filter groups with < 20
         nuclei; additionally, retain only brain regions with >= 50
         total nuclei across all cell types.
      4. Build pseudobulk vectors: raw count means per (ct, region)
         group. Normalize each pseudobulk (2 preprocessing steps):
          1. CP10k: pb_norm = pb / sum(pb) * 1e4
          2. log1p: pb_log = log1p(pb_norm)
         (Probability distribution conversion is applied internally
         by js_divergence() — see Section 2 step 2.)
      5. Global k_n: JS divergence on full pseudobulk matrix with
         shared HK set.
      6. Per-pair k_f: top-200 DE genes (ranked by absolute mean
         difference between the two region groups within the same
         cell type), HK genes excluded (hybrid mode; same approach
         as mouse, human, and TCGA analyses).
      7. Compute omega for all same-cell-type cross-region pairs
         (31,764 pairs total).
      8. Organize omega values per cell type and per region pair.

    Migration detection model (multiplicative):
      For each (cell_type, region_pair) combination:

          expected_omega = mu_ct * mu_pair / mu_grand

      where mu_ct = cell type's global mean omega,
            mu_pair = region pair's mean omega,
            mu_grand = global mean (8.01).

          omega_ratio = observed_omega / expected_omega

      Confidence tiers:
        Strong:   residual < 0.3, omega < 15, lowest omega in the
                  region pair, and pair median omega > 20
        Moderate: residual < 0.5, omega < 25
        Weak:     residual < 0.75, omega < 35

    How to re-run:
      # Download Nonneurons.h5ad from Zenodo:
      #   https://zenodo.org/records/7865491
      #   Save as data/brain/Nonneurons.h5ad
      python notebooks/07c_brain_siletti_v3.py

    Expected output: results/brain_siletti_*_v3.csv


5. STATISTICAL TESTING
----------------------

5.1 Bootstrap Permutation Test

For each cell-type pair comparison, the null hypothesis H0: omega = 1
(no selective remodeling) is tested via permutation:

    1. Pool all cells from groups A and B.
    2. For each of B iterations (B = 500 for mouse pilot;
       B is not applicable to human/TCGA/brain analyses
       which do NOT use bootstrap):

       For mouse pilot only:
       a. Randomly permute cell labels.
       b. Split into two groups of original sizes.
       c. Recompute pseudobulks and omega.
    3. Null distribution = {omega_perm[1], ..., omega_perm[B]}.
    4. Two-sided P-value:
         p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1)
             / (B + 1)
    5. Effect size: Cohen's d = (omega_obs - mean_null) / std_null.
    6. 95% CI: [percentile(null, 2.5), percentile(null, 97.5)].

    Implementation note: In the mouse pilot bootstrap (02c_pilot_v2b.py,
    line 311), the null omega uses omega_null = kf_null / (kn_null + 1e-9),
    adding a tiny epsilon to prevent division-by-zero in the null
    distribution context. This differs from the CKI core function
    (compute_omega in cki/core.py), which uses omega = kf / kn with
    kn=0 → ω=∞. The epsilon in the bootstrap null is negligible for
    all practical purposes (kn_null ≫ 1e-9 in real data), but this
    implementation detail is noted for full transparency.

5.2 Multiple Testing Correction

    FDR correction (Benjamini-Hochberg, q < 0.05) was intended for
    multi-pair comparisons but was not systematically implemented in
    the analysis pipeline. All reported results use raw two-sided
    bootstrap P-values without FDR adjustment. The full set of
    P-values and effect sizes is available in the supplementary
    output files for independent correction by readers.

6. PARAMETER SUMMARY
--------------------

All parameters used in the reported analyses:

    Parameter               Value            Used in
    --------               -----            -------
    Random seed             42               all analyses*
    HK detection method     auto-detected    all analyses
                             (combined criterion:
                              detection rate > 0.9,
                              CV < 30th pctile;
                              use_reference=True)
    HRT Atlas file         data/housekeeping/
                             Human_Mouse_Common.csv
    HRT Atlas reference      yes             all analyses
    Number of HVGs           2,000 (default, unused)  all
    Per-pair DE genes (k_f)  200             human, TCGA, mouse, brain
    Bootstrap iterations     500 (two-sided)* mouse pilot
    Bootstrap (human)        N/A             human (no bootstrap)
    Bootstrap (TCGA)         N/A             TCGA (no bootstrap)
    Bootstrap (brain)        N/A             brain (no bootstrap)
    k_n scaling (alpha)      1.0 (CKI internal)   all analyses
    k_f weight (w1)          1.0             all analyses
    Pathway weight (w2)      0.0             all analyses
    Normalization target     1e4 (CP10k)     mouse, human, brain
    Normalization (TCGA)   log2(TPM+0.001)  TCGA
    Min cells per group      20*             mouse
    Min cells per group      10              human
    Min cells per group      20              brain
    epsilon (omega ratio)   not used; kn=0 → ω=∞    all analyses
                             (bootstrap null: 1e-9
                              for div-by-zero prevention)  mouse pilot

    Approximate runtimes (on a workstation with >= 16 GB RAM,
    8+ CPU cores; wall-clock times vary with hardware):

        Analysis                            Pairs      Bootstrap   ~Runtime
        --------                            -----      ---------   --------
        Mouse pilot (02c_pilot_v2b.py)       15        Yes (500)   5–10 min
        Mouse full (03_full_matrix.py)      703        No         10–20 min
        Human (05_phase33_v3_fixed.py)    5,151        No          1–2 h
        Cross-organ (13_phase35_method*)    60/4,851    No         0.5–1 h
        TCGA (06_phase34_v2.py)         ~20,000        No          1–2 h
        Brain (07c_brain_siletti_v3.py)  31,764        No          4–8 h


7. OUTPUT FILES
---------------

All results are written to results/:

    Mouse (02c_pilot_v2b.py):
      results/mouse_pilot_v2b_results.csv        # omega per pair (15 comparisons)
      results/mouse_pilot_v2b_key_values.csv   # k_n, k_f, omega per comparison

    Mouse full pairwise (03_full_matrix.py):
      results/full_matrix_omega.csv           # omega matrix (38 x 38 cell types)
      results/full_matrix_kn.csv              # k_n matrix
      results/full_matrix_kf.csv              # k_f matrix
      results/full_matrix_pairs.csv           # long-form 703-pair list

    Human (05_phase33_v3_fixed.py):
      results/phase33_v3_human_omega.csv        # omega matrix (cell-types x cell-types)
      results/phase33_v3_human_kn.csv           # k_n matrix
      results/phase33_v3_human_kf.csv          # k_f matrix
      results/phase33_v3_human_pairs.csv       # long-form pair list with omega

    Cross-organ conservation & method comparison (13_phase35_method_comparison.py):
      results/phase35_cross_organ_conservation.csv  # 60 same-CT cross-organ pairs
      results/phase35_all_metrics_pairs.csv        # 5,151 pairs x 5 metrics
      results/phase35_metric_correlation.csv       # 5x5 inter-metric correlation

    TCGA (06_phase34_v2.py):
      results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega
      results/phase34_v2_summary.csv           # per-cancer summary statistics
      results/phase34_v2_{cancer}_pairs.csv  # per-cancer pair files

    TCGA Clinical (07_phase34_clinical.py):
      results/phase34_clinical_paired_unpaired.csv  # paired vs unpaired TN
      results/phase34_clinical_severity.csv         # clinical severity by grade/subtype/mutation
      results/phase34_clinical_plots.png            # multi-panel clinical figure
      results/phase34_clinical_report.md            # analysis report

    Brain (07c_brain_siletti_v3.py):
      results/brain_siletti_omega_pairs_v3.csv        # all region-pair omega values
      results/brain_siletti_ct_summary_v3.csv          # per-cell-type mean omega
      results/brain_siletti_migration_candidates_v3.csv # migration candidate list
      results/brain_siletti_key_values_v3.csv          # global key-value summary

Figure scripts: notebooks/30_genome_biology_figures.py


8. REPRODUCIBILITY CHECKLIST
-----------------------------

[ ] Install CKI v0.3.1: pip install -e .
[ ] Verify random seed = 42 in all scripts.
[ ] Verify HK genes are auto-detected (combined criterion:
      detection rate > 0.9, CV < 30th percentile)
      with HRT Atlas reference merged via set union
      (data/housekeeping/Human_Mouse_Common.csv).
[ ] Verify identity gene parameters: per-pair top-200 DE genes
      (hybrid mode), with HK genes excluded, used in mouse pilot,
      human, TCGA, and brain analyses. The mouse full pairwise analysis
      (03_full_matrix.py, Fig. 2 heatmap) uses global HVG=2000 instead.
[ ] Verify bootstrap iterations: 500 (mouse pilot only;
      CKI default = 1000; human/TCGA/brain do NOT use bootstrap)
[ ] Verify normalization: CP10k + log1p (mouse, human, brain);
      log2(TPM + 0.001) (TCGA).
[ ] Verify probability distribution conversion: sum-normalization
    for non-negative log1p data; softmax for log2 data (Section 2 step 2).
[ ] Verify no epsilon in omega ratio; kn=0 returns omega=∞.
    (NB: mouse bootstrap null uses epsilon=1e-9 in denominator;
    see Section 5.1 implementation note.)
[ ] Verify two-sided bootstrap test with pseudocount +1.
[ ] For human/TCGA: verify per-pair k_f uses top-200 DE genes.
[ ] For brain: verify min_cells_per_group = 20.

Notes:
* CKI package default bootstrap iterations = 1000;
  mouse pilot used 500.
* Alpha (k_n scaling) is a CKI internal parameter;
  not explicitly set in analysis scripts.
* For the full mouse pairwise analysis (703 pairs, 03_full_matrix.py),
  no bootstrap is performed — statistical significance is assessed
  only in the pilot (02c_pilot_v2b.py, 15 targeted pairs, 500
  iterations).

By following this guide with the exact parameter configurations above,
readers should obtain numerically identical results to those reported
in the manuscript. Minor floating-point differences (±1e-6) may occur
due to hardware differences in transcendental function evaluation
(exp, log). Bootstrap P-values may differ by small amounts (~±0.01)
due to the random permutation draws (seed=42 controls reproducibility
within the same platform, but cross-platform RNG implementations may
vary). Neither class of variation affects any biological conclusions.
