# -*- coding: utf-8 -*-
"""Apply first-author (X.W.) revisions to generate_manuscript_gb.py for v47.

Every replacement asserts exactly-one occurrence. All strings are RAW so that
literal \\uXXXX escapes in the generator source are matched literally.
"""
import io, sys

PATH = r'C:/Users/KnightZ/Desktop/细胞受选择/generate_manuscript_gb.py'
src = io.open(PATH, encoding='utf-8', newline='').read()

E = []  # (id, old, new)

# ---------- main text: Fig.2 panel ref ----------
E.append(('T01  Fig2B,D -> 2B,C',
 r"biological distance (Fig. 2B, D).",
 r"biological distance (Fig. 2B, C)."))

# ---------- main text: delete old S3 (method comparison) ref ----------
E.append(('T02  del Fig. S3 ref',
 r"ranked 5th of 5 methods; Table 1; Additional file 1: Fig. S3)",
 r"ranked 5th of 5 methods; Table 1)"))

# ---------- main text: S renumbering ----------
E.append(('T03  S13->S12 (Kang, Results)',
 r"(Additional file 1: Fig. S13; Additional file 1: Note 3.15)",
 r"(Additional file 1: Fig. S12; Additional file 1: Note 3.15)"))
E.append(('T04  S4->S3 (TCGA)',
 r"(Fig. 4; Additional file 1: Fig. S4)",
 r"(Fig. 4; Additional file 1: Fig. S3)"))
E.append(('T05  S5->S4 (cross-organ)',
 r"(Fig. 5; Table 2; Additional file 1: Fig. S5)",
 r"(Fig. 5; Table 2; Additional file 1: Fig. S4)"))
E.append(('T06  S6->S5 (brain)',
 r"(Fig. 6; Additional file 1: Fig. S6; Additional file 1: Table S3)",
 r"(Fig. 6; Additional file 1: Fig. S5; Additional file 1: Table S3)"))
E.append(('T07  S7->S6 (pair-specific kn)',
 r"per-pair k_n estimator (Additional file 1: Fig. S7)",
 r"per-pair k_n estimator (Additional file 1: Fig. S6)"))
E.append(('T08  S8->S7 (residual model)',
 r"Weak (residual < 0.75, \u03c9 < 35; Additional file 1: Fig. S8)",
 r"Weak (residual < 0.75, \u03c9 < 35; Additional file 1: Fig. S7)"))
E.append(('T09  S9->S8 (block-shuffle null)',
 r"Under the block-shuffle null (B = 1,000; Additional file 1: Fig. S9)",
 r"Under the block-shuffle null (B = 1,000; Additional file 1: Fig. S8)"))
E.append(('T10  S14->S13 (QQ, Results)',
 r"Additional file 1: Note 4.6; Additional file 1: Fig. S14)",
 r"Additional file 1: Note 4.6; Additional file 1: Fig. S13)"))
E.append(('T11  S10->S9 (cross-species, Discussion)',
 r"P = 0.55; Additional file 1: Fig. S10)",
 r"P = 0.55; Additional file 1: Fig. S9)"))
E.append(('T13  S11->S10 (omega dist, Limitations)',
 r"P = 0.071; Additional file 1: Fig. S11)",
 r"P = 0.071; Additional file 1: Fig. S10)"))
E.append(('T14  S14->S13 (QQ, Limitations)',
 r"(Results; Additional file 1: Note 4.6, Fig. S14)",
 r"(Results; Additional file 1: Note 4.6, Fig. S13)"))
E.append(('T15  S12->S11 (JS dim, Methods)',
 r"between d = 1,130 and d = 2,000; Additional file 1: Fig. S12)",
 r"between d = 1,130 and d = 2,000; Additional file 1: Fig. S11)"))
E.append(('T16  Fig2D->2B,C (stat conventions)',
 r"calibration contrast (Fig. 2D) uses a one-sided",
 r"calibration contrast (Fig. 2C) uses a one-sided"))
E.append(('T17  Additional files S1-S14 -> S1-S13',
 r"including Supplementary Figures S1\u2013S14 and Supplementary Tables S1\u2013S4",
 r"including Supplementary Figures S1\u2013S13 and Supplementary Tables S1\u2013S4"))

# ---------- D4: Kang sentence in Discussion ("When to use CKI") ----------
E.append(('D4a  name Kang',
 r"A real perturbation demonstration (Results) supports this boundary",
 r"A real perturbation demonstration (Kang et al. [14]; Results) supports this boundary"))
E.append(('D4b  anchor stationarity sentence',
 r"retains 0.98. Use standard metrics when any of the following hold",
 r"retains 0.98. This makes explicit that the index presupposes anchor stationarity: when the anchor itself moves, cross-metric contrasts\u2014not absolute \u03c9 values\u2014are the reliable signal (Additional file 1: Fig. S12). Use standard metrics when any of the following hold"))

# ---------- Fig 2 legend: delete old C, D->C ----------
E.append(('F2  legend panel C/D',
 r"(C) Spearman correlation between CKI \u03c9 and four standard metrics (Cosine, Raw JS, Marker Jaccard, Spearman) on Tabula Muris data (703 pairs across 38 cell types). On the mouse calibration data \u03c9 is only weakly correlated with the standard metrics (|r| \u2264 0.28, with Raw JS near zero at +0.05), whereas on the human data all four correlations are negative (Results, \u201cCorrelation structure between CKI and standard metrics\u201d; Fig. 3); in neither case should the correlation pattern be read as evidence that \u03c9 captures an independent information dimension, because it partly reflects the \u03c9 denominator. (D) \u03c9 distribution by comparison category",
 r"(C) \u03c9 distribution by comparison category"))

# ---------- Fig 3 legend: delete B/D/E, C->B ----------
E.append(('F3a  del B, C->B',
 r"""(B) Scatter plot of CKI \u03c9 vs. k_n (baseline rate) on Tabula Sapiens data (n = {_h["n_pairs_total"]:,} pairs), colored by same-organ vs. cross-organ pairs, with Spearman r. (C) ROC curves""",
 r"(B) ROC curves"))
E.append(('F3b  del D/E',
 r" (D) \u03c9 by comparison category: S (same cell type, different organ), D (different cell type, same organ), X (different cell type, different organ); the C category (random split of the same population) has no pairs in this dataset and is not shown. Box plots show log10(\u03c9) distribution. (E) AUC (cell-type classification) vs. interpretability (decomposability) comparison across five metrics. CKI \u03c9 had the lowest AUC of all five metrics (0.680, versus 0.690 for Spearman, 0.801 for marker Jaccard, 0.849 for raw JS, and 0.887 for cosine) but is the only fully decomposable metric into baseline (k_n) and functional (k_f) components.",
 r""))

# ---------- Fig 4 legend: delete C/D/E ----------
E.append(('F4  del C/D/E',
 r" (C) Mean \u03c9 by PAM50 intrinsic subtype in BRCA (per-sample PAM50 labels; mean tumor-tumor \u03c9 within each subtype). (D) Permutation standardized effect size (SES) for NN vs. TT comparisons per cancer type. (E) Tissue-level pairwise \u03c9 matrix heatmap across five cancer types.",
 r""))

# ---------- Fig 5 legend: Table of top -> Top 5 ----------
E.append(('F5  Top 5',
 r"(D) Table of top conservative cell-type pairs",
 r"(D) Top 5 conservative cell-type pairs"))

# ---------- Fig 6 legend: delete old C, D->C, E->D ----------
E.append(('F6a  del C, D->C',
 r" (C) Astrocyte \u03c9 across representative brain regions (region \u00d7 region matrix; warmer colors, higher \u03c9). (D) Region-associated candidate detection",
 r" (C) Region-associated candidate detection"))
E.append(('F6b  E->D',
 r"(E) Observed vs. expected \u03c9 for the five strongest Strong candidates",
 r"(D) Observed vs. expected \u03c9 for the five strongest Strong candidates"))

# ---------- S1 legend: A panel decreasing wording (keep AUC 0.786) ----------
E.append(('S1  A panel wording',
 r"housekeeping gene set size, showing convergence at ~200-300 HK genes.",
 r"housekeeping gene set size; k_n decreases monotonically with increasing HK gene number (250\u20131,000), indicating that the baseline rate is gene-set-size-dependent; absolute \u03c9 values are therefore scheme-specific, consistent with the fixed-panel ablation (Results)."))

# ---------- S2 legend: two baselines ----------
E.append(('S2  two baselines',
 r"p('Additional file 1: Figure S2. Calibrated omega. (A) Raw vs. calibrated \u03c9 (\u03c9_cal = \u03c9 / 7.70) by brain cell type. (B) Calibrated \u03c9 distribution across all 31,764 brain pairs, with calibration baseline (\u03c9_cal = 1.0) and mean indicated.')",
 r"p('Additional file 1: Figure S2. Calibrated \u03c9 under two baselines. (A) Raw \u03c9 and calibrated \u03c9 (\u03c9_cal = \u03c9 / 7.70, mouse FACS baseline; \u03c9 / 9.73, brain-internal baseline) by brain cell type (log scale). Dashed line indicates the split-half expectation (\u03c9_cal = 1.0). (B) Calibrated \u03c9 distributions across all 31,764 brain region pairs under both baselines; calibrating with the mouse baseline overstates brain \u03c9_cal by 1.26-fold (9.73 / 7.70).')"))

# ---------- delete old S3 legend + S4->S3 ----------
E.append(('S3  del old S3, S4->S3',
 r"p('Additional file 1: Figure S3. Method comparison performance. ROC-AUC bar plot for cell-type classification across five metrics.')" + "\n\n" + r"p('Additional file 1: Figure S4. TCGA per-cancer matrices.",
 r"p('Additional file 1: Figure S3. TCGA per-cancer matrices."))

# ---------- S5->S4 legend rewrite ----------
E.append(('S4  cross-organ raw data',
 r"p('Additional file 1: Figure S5. Cross-organ conservation raw data. Complete table of 59 same-cell-type cross-organ pairs (Additional file 1: Table S2).')",
 r"p('Additional file 1: Figure S4. Cross-organ conservation raw data. Blue = well-sampled (n \u2265 5 pairs); gray = sparsely sampled (n < 5 pairs). Panel A shows mean \u00b1 SD; Panel B shows raw pair-level distribution.')"))

# ---------- S6->S5 legend rewrite (new A-C) ----------
E.append(('S5  brain regional details',
 r"p('Additional file 1: Figure S6. Brain regional analysis details. (A) Cell type nuclei counts per brain region, showing the distribution of non-neuronal nuclei across sampled regions. (B) \u03c9 distribution per cell class (log scale; boxes: median and IQR, whiskers 1.5\u00d7 IQR), from the block-shuffle observed landscape. (C) \u03c9 vs. number of regions (n_regions) per cell type, with Spearman \u03c1 reported; broader spatial distribution is associated with greater transcriptomic divergence. (D) Region-region \u03c9 matrix for astrocytes across representative brain regions. (E) Top region-associated candidates (Strong tier) by 1 \u2212 residual.')",
 r"p('Additional file 1: Figure S5. Brain regional analysis details. (A) Mean regional divergence (\u03c9, with SD) per cell type, ranked ascending; red bars denote significant deviation from the block-shuffle null (p < 0.05 and |standardised effect size (SES)| \u2265 2; SES = [observed \u03c9 \u2212 null mean] / null SD), grey otherwise. (B) \u03c9 versus number of sampled regions (n_regions) per cell type; Spearman \u03c1 is reported (broader spatial coverage is not significantly associated with divergence at n = 10). (C) Distribution of multiplicative residuals (observed/expected \u03c9) across all 31,764 cross-region pairs; colours indicate confidence tier (Strong: < 0.3; Moderate: < 0.5; Weak).')"))

# ---------- S7->S6 legend rewrite ----------
E.append(('S6  pair-specific k_n',
 r"p('Additional file 1: Figure S7. Per-pair k_n variability. (A) Per-pair k_n (mean \u00b1 SD) by cell type in the brain atlas, showing substantial cross-pair variability (CV = 97.52%). (B) Scatter plot of \u03c9 computed with per-pair k_n vs. global k_n (Spearman \u03c1 = 0.142), indicating that pair-specific k_n yields substantially different rankings.')",
 r"p('Additional file 1: Figure S6. Pair-specific k_n variability (brain). (A) Distribution of per-pair k_n values by cell type (bars: mean \u00b1 SD); bar colour reflects the cross-pair coefficient of variation (CV) of k_n, from light (low CV, stable k_n) to dark (high CV, variable k_n). (B) Per-pair \u03c9 (pair-specific k_n) versus \u03c9 estimated with the global mean k_n; red line is y = x. Spearman \u03c1 = 0.142 (P = 7.07\u00d710\u207b\u00b9\u2074\u00b3, n = 31,764).')"))

# ---------- S8->S7 legend rewrite (B/C swapped to match figure panels) ----------
E.append(('S7  developmental signature',
 r"p('Additional file 1: Figure S8. Developmental signature detection. (A) Multiplicative residual distribution for all 31,764 cross-region pairs, with Strong (residual < 0.3), Moderate (residual < 0.5), and Weak (residual < 0.75) tiers shaded. (B) Strong candidate counts by cell type: microglia contribute the largest share (16 of 39), followed by oligodendrocytes (10) and fibroblasts (6); the candidate list is dominated by microglia, while the oligodendrocyte lineage as a whole shows no enrichment (12 of 39 versus a 40.2% share of comparisons; fold 0.77, P = 0.92). Because no candidate survives FDR correction (minimum q = 0.520), these counts describe a hypothesis-generating screen rather than validated region-association events. (C) Top 10 Strong candidates (lowest multiplicative residuals), showing observed \u03c9 for each cell-type/region pair; bars are colored by oligodendrocyte-lineage (purple) vs. non-OL (red) membership. 12/39 Strong-tier candidates are oligodendrocyte-lineage (fold enrichment 0.77, P = 0.92); microglia account for 16/39 (fold 2.30 versus their share of comparisons, P = 6.0e-4, but fold 0.31 versus the null-rule composition\u2014see Results; no class-composition claim is made). (D) Region-associated candidates by cell type and confidence tier, showing tier distribution across all 10 non-neuronal cell classes.')",
 r"p('Additional file 1: Figure S7. Developmental signature detection. (A) Multiplicative residual distribution for all 31,764 cross-region pairs, with Strong (residual < 0.3), Moderate (residual < 0.5), and Weak (residual < 0.75) tiers shaded. (B) The ten Strong candidates with the smallest residual, shown as horizontal bars (residual and \u03c9 value annotated on each bar); bars are coloured by oligodendrocyte (OL) lineage membership (purple, OL-lineage; red, non-OL). Inset: OL-lineage representation among Strong candidates \u2014 12 of 39 Strong, fold = 0.77, hypergeometric P = 0.92 (no enrichment). Cell types and region pairs are given in full. (C) Confidence-tier composition (Strong/Moderate/Weak) of all cross-region pairs, stacked by cell type and sorted by the number of Strong pairs (ascending). The number and percentage (to two decimal places) of Strong pairs are annotated on each bar \u2014 e.g., Microglia: Strong 16 (0.96%); Oligodendrocyte: Strong 10 (0.95%); Astrocyte: Strong 3 (0.47%).')"))

# ---------- S9->S8 renumber ----------
E.append(('S8  block-shuffle null',
 r"p('Additional file 1: Figure S9. Block-shuffle permutation null",
 r"p('Additional file 1: Figure S8. Block-shuffle permutation null"))

# ---------- S10->S9 cross-species: renumber + delete B/C ----------
E.append(('S9  cross-species',
 r"""p(f'Additional file 1: Figure S10. Cross-species comparison details. (A) Cross-species \u03c9 comparison: scatter plot of human vs. mouse per-cell-type mean \u03c9 for the 15 shared cell types (Spearman r = \u22120.17, P = 0.55; no significant correlation). (B) HK gene set detection stability: overlap between human and mouse HK gene sets detected by the combined criterion. (C) \u03c9 distribution comparison between mouse (n = 15 shared cell types) and human (n = {_h["n_pairs_total"]:,} pairs).')""",
 r"p('Additional file 1: Figure S9. Cross-species comparison details. (A) Cross-species \u03c9 comparison: scatter plot of human vs. mouse per-cell-type mean \u03c9 for the 15 shared cell types (Spearman r = \u22120.17, P = 0.55; no significant correlation).')"))

# ---------- S11->S10 omega distribution: renumber + append clause ----------
E.append(('S10a renumber',
 r"p('Additional file 1: Figure S11. \u03c9 distribution characterization.",
 r"p('Additional file 1: Figure S10. \u03c9 distribution characterization."))
E.append(('S10b append power clause',
 r"does not reject normality (P = 0.071).')",
 r"does not reject normality (P = 0.071), although the small sample size limits the power of this test.')"))

# ---------- S12->S11 renumber ----------
E.append(('S11  JS dimensionality',
 r"p('Additional file 1: Figure S12. JS divergence dimensionality invariance.",
 r"p('Additional file 1: Figure S11. JS divergence dimensionality invariance."))

# ---------- S13->S12 renumber ----------
E.append(('S12  Kang',
 r"p('Additional file 1: Figure S13. Real perturbation demonstration",
 r"p('Additional file 1: Figure S12. Real perturbation demonstration"))

# ---------- S14->S13 renumber ----------
E.append(('S13  QQ',
 r"p('Additional file 1: Figure S14. Pseudo-region negative control",
 r"p('Additional file 1: Figure S13. Pseudo-region negative control"))

# ================= run =================
fails = []
for tag, old, new in E:
    n = src.count(old)
    if n != 1:
        fails.append((tag, n))
        continue
    src = src.replace(old, new)

if fails:
    print('FAILED (tag, occurrences):')
    for t, n in fails:
        print(f'  {t}  -> {n}')
    sys.exit(1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(src)
print(f'OK: {len(E)} replacements applied to generate_manuscript_gb.py')
