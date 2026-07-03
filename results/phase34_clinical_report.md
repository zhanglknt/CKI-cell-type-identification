# CKI Phase 3.4 Supplement: Paired/Unpaired & Clinical Severity

## Overview
- Data: TCGA pan-cancer bulk RNA-seq (5 cancer types)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f, n=200)
- Analysis time: 507s

## Part A: Paired vs Unpaired Tumor-Normal Comparison
   Cancer  n_Tumor  n_Normal  n_Paired_TN  n_Unpaired_TN Paired_mean Unpaired_mean Paired_Unpaired_ratio  P_value NN_TT_ratio
TCGA-LUAD      495        76            5           1995      267.64        269.45                 0.993 7.77e-01        1.60
TCGA-LUSC      567        58            2           1998      342.30        197.67                 1.732       NA        1.43
TCGA-LIHC      365        57            5           1995      183.84         83.95                 2.190 2.42e-02        2.83
TCGA-KIRC      755        82            4           1996      679.19        209.25                 3.246       NA        1.98
TCGA-BRCA     1032       109            4           1996      452.92        267.09                 1.696       NA        1.40

## Part B: Clinical Severity Stratification
cancer  stratification         group   n omega_mean omega_std
  LIHC Edmondson_grade            G1  39     101.82     46.84
  LIHC Edmondson_grade            G2 133     100.23     63.86
  LIHC Edmondson_grade            G3 105      96.77     58.19
  LIHC Edmondson_grade            G4  11      89.95     57.78
  BRCA           PAM50    Basal-like  97     223.44    183.72
  BRCA           PAM50 HER2-enriched  55     263.01    255.60
  BRCA           PAM50     Luminal A 224     344.52    323.35
  BRCA           PAM50     Luminal B 123     313.59    282.65
  BRCA           PAM50   Normal-like   7     108.00     65.47
  LUAD        mutation          EGFR  61     285.34    180.10
  LUAD        mutation          KRAS 120     284.58    227.93
  LUAD        mutation            WT 311     237.60    195.39

## Statistical Tests
- LIHC Edmondson grade: Jonckheere-Terpstra trend test (ordered G1 < G2 < G3 < G4)
- BRCA PAM50: Kruskal-Wallis test (independent subtypes)
- LUAD EGFR/KRAS: Kruskal-Wallis test (independent groups)

## Data Sources
- TCGA TPM: UCSC Xena (tcga_RSEM_gene_tpm.gz)
- LIHC grade: cBioPortal API (lihc_tcga study, GRADE attribute)
- BRCA PAM50: cBioPortal API (brca_tcga_pub study, PAM50_SUBTYPE attribute)
- LUAD mutations: cBioPortal API (luad_tcga study, EGFR/KRAS mutation status)

## Output Files
- phase34_clinical_paired_unpaired.csv
- phase34_clinical_severity.csv
- phase34_clinical_plots.png