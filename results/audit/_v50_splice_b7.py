# v50 Phase B batch 7: clause-level second-pass trims (unique-substring replaces)
P = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
src = open(P, encoding="utf-8").read()

EDITS = [
# --- Decomposing ---
("k_n captures baseline noise: technical variation, stochastic bursting, and individual-level physiological differences.",
 "k_n captures baseline technical and physiological noise."),
(" k_f is the JS divergence between the two identity-gene probability distributions. Because the k_f genes",
 " Because the k_f genes"),
(" and Benjamini-Hochberg FDR correction is applied within each dataset; larger-scale analyses are supplemented with non-parametric tests and descriptive statistics.",
 " and Benjamini-Hochberg FDR correction is applied within each dataset."),
(" Partitioning expression into constrained baseline and identity gene sets suffices, without external pathway databases.')",
 "')"),
# --- Calibration ---
(" No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence. A leave-one-population-out sensitivity gives a baseline range of 6.75\\u20138.08 (Section 3.10 of the Supplementary Information).",
 " No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence (leave-one-population-out baseline range 6.75\\u20138.08; Section 3.10 of the Supplementary Information)."),
("\\u03c9_cal = \\u03c9_obs / 7.70, reported to at most two significant figures. Scheme-matched split-half calibration inside each dataset shows the factor to be dataset-relative, not universal:",
 "\\u03c9_cal = \\u03c9_obs / 7.70. Split-half calibration inside each dataset shows the factor to be dataset-relative, not universal:"),
("while compressing calibrated levels, and a ratio-estimator audit confirms the calibration absorbs ratio bias (median +0.2% per class \\u00d7 region group; Supplementary Notes 2\\u20134). calibrate_omega() is available in the CKI package.",
 "while compressing calibrated levels; a ratio-estimator audit confirms the calibration absorbs ratio bias (Supplementary Notes 2\\u20134)."),
# --- Correlation ---
(" The negative raw correlation is thus partly a ratio artifact of the k_n denominator: \\u03c9 is a composite whose value lies in normalizing functional divergence against a population-specific baseline rather than in statistical independence from existing metrics.",
 " The negative raw correlation is thus partly a ratio artifact of the k_n denominator."),
# --- Simulation ---
("Two adversarial scenarios quantify the boundary (Supplementary Notes 1, 5): with the module placed on HK genes, \\u03c9 detected none at any \\u03b4 (rate 0.000; k_n itself fired at 0.61\\u20131.00)\\u2014\\u03c9 is structurally blind to functional change on its anchor genes\\u2014whereas under expression-matched low-variance non-HK drift (N1 control) \\u03c9 stayed at its calibrated false-positive rate (0.000\\u20130.067) while raw JS and cosine inflated to 0.81\\u20131.00: the ratio cancels global compositional drift wherever it acts, so \\u03c9\\u2019s specificity is not an HK-anchoring artifact.",
 "Two adversarial scenarios quantify the boundary (Supplementary Notes 1, 5): \\u03c9 is structurally blind to modules placed on HK genes (detection 0.000 at every \\u03b4; k_n itself fired at 0.61\\u20131.00), yet under expression-matched low-variance non-HK drift (N1 control) \\u03c9 stayed at its calibrated false-positive rate (0.000\\u20130.067) while raw JS and cosine inflated to 0.81\\u20131.00\\u2014the ratio cancels global compositional drift wherever it acts, so its specificity is not an HK-anchoring artifact."),
("Integrating specificity and sensitivity, \\u03c9 best discriminated",
 "\\u03c9 best discriminated"),
(", the advantage over k_f holding in 100% of resamples):", "):"),
(" These results delimit the intended use of \\u03c9: a specificity-first screen whose construction rejects neutral drift, at the cost of bounded power for weak-to-moderate functional signals (Supplementary Note 1).",
 " \\u03c9 is thus a specificity-first screen: its construction rejects neutral drift, at the cost of bounded power for weak-to-moderate functional signals (Supplementary Note 1)."),
("and fully reproduced: AUC(\\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e), with the same metric ranking in both backgrounds.",
 "and fully reproduced: AUC(\\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e)."),
(" Limitations replicated too: under strong confounding both \\u03c9 and k_f fell below threshold, and under the fourfold imbalance k_f retained higher power (0.98\\u20131.00 versus 0.04\\u20130.20)\\u2014the flip side of the ratio\\u2019s neutral-drift immunity.",
 " Under the fourfold imbalance k_f retained higher power (0.98\\u20131.00 versus 0.04\\u20130.20)\\u2014the flip side of the ratio\\u2019s neutral-drift immunity."),
# --- Neutral-drift ---
("(0 of 30 pairs above its own null 95th percentile, 95% CI [0.000, 0.114]; median calibration ratio 0.963; k_f alone likewise 0 of 30)",
 "(0 of 30 pairs above its own null 95th percentile; median calibration ratio 0.963; k_f alone likewise 0 of 30)"),
("(FPR 28.6%, CI [26.8, 30.6], versus 45.2% for raw JS, 44.1% for cosine, 40.6% for Spearman, and 37.6% for k_f alone; Fig. 3b, c)",
 "(FPR 28.6% versus 45.2% raw JS, 44.1% cosine, 40.6% Spearman, 37.6% k_f; Fig. 3b, c)"),
("but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \\u03c9 and 2.98 for raw JS) and, as a single set-overlap statistic, offers no k_n/k_f decomposition.",
 "but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \\u03c9 and 2.98 for raw JS) and offers no k_n/k_f decomposition."),
("At T2 all metrics fire on most pairs (donor differences contain real biology) and \\u03c9 again misreported least among the continuous metrics (90.9% versus 98.4\\u201398.7%); at T3 every metric rose, confirming retained sensitivity: across the ladder",
 "At T2 \\u03c9 again misreported least among the continuous metrics (90.9% versus 98.4\\u201398.7%); across the ladder"),
("\\u2014lowest misreporting among the continuous divergence metrics at every tier, with sensitivity to genuine regional divergence preserved (Fig. 3; Section 3.12 of the Supplementary Information).",
 "\\u2014lowest misreporting among the continuous divergence metrics at every tier (Section 3.12 of the Supplementary Information)."),
# --- Fixed-panel ---
("and the ten class means at \\u03c1 = 0.90\\u20130.99. The astrocyte-to-Bergmann-glia gradient was preserved and, under leave-pair-out, amplified (6.10-fold reported; 6.53-fold leave-pair-out), because non-circular panels deflate \\u03c9 more strongly in transcriptionally constrained classes.",
 "and the ten class means at \\u03c1 = 0.90\\u20130.99. The astrocyte-to-Bergmann-glia gradient was preserved and, under leave-pair-out, amplified (6.10-fold reported; 6.53-fold leave-pair-out)."),
# --- Pan-cancer ---
("whereas TT k_f was equal to or higher than NN k_f (e.g. LUAD 0.282 versus 0.226)\\u2014the reversal reflects",
 "whereas TT k_f was equal to or higher than NN k_f\\u2014the reversal reflects"),
("with the sample-level cluster-bootstrap CI excluding 1 in four of five cancers (LIHC excepted, direction consistent in all five)",
 "the cluster-bootstrap CI excluding 1 in four of five (LIHC excepted, direction consistent in all five)"),
(" using per-tumor \\u03c9 (the mean over all TT pairs in which a tumor participates; Fig. 4b). KRAS-mutant tumors showed the highest tissue-level divergence (mean \\u03c9 = 136.9), exceeding wild-type (115.4; Kruskal-Wallis P = 7.8 \\u00d7 10\\u207b\\u2077; Dunn\\u2013Holm P = 3.6 \\u00d7 10\\u207b\\u2077) and EGFR-mutant tumors (122.2; Dunn\\u2013Holm P = 0.008), while EGFR and wild-type did not differ significantly (P = 0.39); whole-tumor label-permutation tests, insensitive to the dyadic dependence of per-tumor means, confirmed all three contrasts",
 " using per-tumor \\u03c9 (Fig. 4b). KRAS-mutant tumors showed the highest tissue-level divergence (mean \\u03c9 = 136.9 versus 115.4 wild-type and 122.2 EGFR-mutant; Kruskal-Wallis P = 7.8 \\u00d7 10\\u207b\\u2077; Dunn\\u2013Holm P \\u2264 0.008 for both KRAS contrasts, P = 0.39 for EGFR\\u2013wild-type); whole-tumor label-permutation tests confirmed all three contrasts"),
("(k_n contributed ~84% of the log-\\u03c9 gap; WT > KRAS, Dunn\\u2013Holm P = 4.2 \\u00d7 10\\u207b\\u2074)",
 "(k_n contributed ~84% of the log-\\u03c9 gap)"),
("KRAS-mutant tumors were enriched for ever-smokers (94% versus 63% EGFR-mutant and 86% wild-type), yet adjusting for smoking\\u2014alone, jointly with admixture, or jointly with age and sex\\u2014left the contrast essentially unchanged (\\u0394\\u03c9 +13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3 with smoking, age, and sex).",
 "Adjusting for smoking (94% ever-smokers among KRAS-mutant tumors versus 63% EGFR-mutant and 86% wild-type), alone or jointly with admixture, age, and sex, left the contrast essentially unchanged (\\u0394\\u03c9 +13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3)."),
("showed admixture can only weaken, not create, the TT k_n elevation: per-tumor k_n correlated negatively with admixture in every cancer type (r = \\u22120.23 to \\u22120.42), and restricting tumor\\u2013tumor comparisons to the high-purity half increased the NN/TT ratio in all five (e.g. LUAD 2.46 \\u2192 2.86; LIHC 1.10 \\u2192 1.17, CI still including 1).",
 "showed admixture can only weaken, not create, the TT k_n elevation (per-tumor k_n correlated negatively with admixture, r = \\u22120.23 to \\u22120.42; high-purity-half comparisons increased the ratio in all five, e.g. LUAD 2.46 \\u2192 2.86)."),
("and the reversal, its ranking, the k_n elevation, and the LUAD mutation gradient were preserved, although the LIHC effect size is mapping-sensitive (NN/TT 1.10 versus 1.31 under the softmax mapping; Section 1.7).",
 "with the reversal, its ranking, the k_n elevation, and the LUAD gradient preserved (LIHC effect size mapping-sensitive: 1.10 versus 1.31 under softmax; Section 1.7)."),
("found no program surviving multiple-testing correction (all q \\u2265 0.24), consistent with a distributed identity-gene signal, and composition-adjusted regressions retained",
 "found no program surviving correction (all q \\u2265 0.24), and composition-adjusted regressions retained"),
("leaves the LIHC null result unchanged (NN/TT 1.11, 95% CI [0.93, 1.30]), so the LIHC interval is not an artefact of their reassignment.",
 "leaves the LIHC null result unchanged (NN/TT 1.11, 95% CI [0.93, 1.30])."),
("Remaining limitations are inherent to bulk resolution: TCGA \\u201cnormal\\u201d samples are adjacent non-tumor tissues from cancer patients, not healthy donor tissue, and per-tumor \\u03c9 was not associated with overall survival in LIHC (Cox hazard ratio per SD 1.07, 95% CI 0.88\\u20131.31, P = 0.48), so we report all TCGA findings as tissue-level functional divergence at bulk resolution, pending single-cell or deconvolution-based validation.",
 "TCGA \\u201cnormal\\u201d samples are adjacent non-tumor tissues rather than healthy donor tissue, and per-tumor \\u03c9 was not associated with overall survival (LIHC Cox hazard ratio per SD 1.07, 95% CI 0.88\\u20131.31): we report all TCGA findings as tissue-level divergence at bulk resolution, pending single-cell or deconvolution-based validation."),
# --- Brain ---
("We focused on 888,263 non-neuronal nuclei in 10 major classes (886,808 passing the \\u2265 20-nuclei filter); neurons were excluded because supercluster_term does not resolve neuronal subtypes, violating the same-cell-type assumption. CKI \\u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs total) (Fig. 6; Supplementary Fig. 6; Supplementary Table 3). Vascular cells and fibroblasts are heterogeneous superclusters aggregating multiple subtypes, so their class-level \\u03c9 values are supercluster averages, not properties of one coherent cell type.",
 "We focused on 888,263 non-neuronal nuclei in 10 major classes (886,808 passing the \\u2265 20-nuclei filter); neurons were excluded because supercluster_term does not resolve neuronal subtypes. CKI \\u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs) (Fig. 6; Supplementary Fig. 6; Supplementary Table 3); vascular cells and fibroblasts are heterogeneous superclusters, so their class-level \\u03c9 values are supercluster averages."),
("from Bergmann glia and vascular cells (both 13.56, a near-tie whose order flips with the filter threshold; Supplementary Note 10) through microglia (24.31 \\u00b1 12.35) and the oligodendrocyte lineage to astrocytes, the most regionally divergent class (82.75 \\u00b1 44.98, n = 5,778 pairs across 108 regions; all SDs with ddof = 1)\\u2014a full-data endpoint gradient of 6.10-fold. Because class-mean k_n is confounded by class size (below), this headline is an uncorrected upper bound:",
 "from Bergmann glia and vascular cells (both 13.56) to astrocytes (82.75 \\u00b1 44.98, n = 5,778 pairs across 108 regions)\\u2014a full-data endpoint gradient of 6.10-fold. Because class-mean k_n is confounded by class size (below), this headline is an uncorrected upper bound:"),
("We therefore co-report 6.10-fold (full-data) and 1.74-fold (size-balanced) throughout; under class-specific split-half baselines the gradient is 5.99 (95% CI [4.43, 7.69]; Supplementary Note 2), and excluding Bergmann glia it is unchanged (astrocytes versus vascular cells, 95% CI [6.00, 6.21]).",
 "We therefore co-report 6.10-fold (full-data) and 1.74-fold (size-balanced) throughout (5.99, 95% CI [4.43, 7.69], under class-specific split-half baselines; Supplementary Note 2)."),
("(astrocytes P \\u2264 9.99 \\u00d7 10\\u207b\\u2074, the permutation floor; OPCs P = 0.002; committed OPCs P = 0.005; fibroblasts P = 0.030)",
 "(astrocytes at the permutation floor, P \\u2264 9.99 \\u00d7 10\\u207b\\u2074; OPCs, committed OPCs, and fibroblasts P \\u2264 0.030)"),
(" Microglia, oligodendrocytes, and Bergmann glia sit at or below the null expectation (P = 0.883\\u20130.998). The gradient is thus supported at the cell-class level for a subset of classes\\u2014most strongly astrocytes and the OPC-to-oligodendrocyte lineage.",
 " Microglia, oligodendrocytes, and Bergmann glia sit at or below the null expectation (P = 0.883\\u20130.998)."),
("First, with only four donors and 94.5% of region pairs sharing at least one, the pooled gradient could reflect donor identity rather than regional biology; restricting comparisons to same-donor region pairs preserved the extremes (astrocytes 75.18 across 11,139 within-donor pairs; Bergmann glia 16.73), a 4.50-fold gradient, so donor sharing cannot explain the gradient away.",
 "First, restricting comparisons to same-donor region pairs (the atlas has four donors; 94.5% of region pairs share at least one) preserved the extremes (astrocytes 75.18; Bergmann glia 16.73), a 4.50-fold gradient, so donor identity cannot explain the gradient away."),
(" The ordering is stable under an aggregate-first k_n estimator (\\u03c1 = 0.988) but not under a single global k_n shared by all classes (\\u03c1 = 0.09), so fine-grained \\u03c9 orderings depend materially on the per-pair k_n estimator (Supplementary Fig. 7)\\u2014the gradient chiefly reflects housekeeping stability across regions, not functional-gene divergence.",
 " The gradient thus chiefly reflects housekeeping stability across regions, not functional-gene divergence (k_n estimator sensitivity: Supplementary Fig. 7)."),
("(P \\u2265 0.091; Supplementary Note 10)\\u2014the ratio cancels shared sampling noise. Decomposing",
 "(P \\u2265 0.091; Supplementary Note 10). Decomposing"),
(" Fourth, the gradient is robust to the 20-nuclei group-size threshold in direction but not magnitude (endpoint gradients 6.60, 6.10, and 4.12 at thresholds 10, 20, and 50; thresholds must stay at or below 50 nuclei to retain all ten classes; Supplementary Note 10).",
 " Fourth, the gradient is robust to the group-size threshold in direction but not magnitude (Supplementary Note 10)."),
("p('The gradient suggests a residence/migration framework in which recently migrated or continuously exchanging types show low inter-regional \\u03c9 while stably resident types accumulate regional signatures. The data, however, provide no evidence for it: OPCs\\u2014the most actively migrating non-neuronal population\\u2014show the second-highest global mean \\u03c9 (40.62), and the corrected candidate screen shows no oligodendrocyte-lineage concentration (fold enrichment 0.77, P = 0.92). With no candidate surviving multiple-testing correction (below), this framework remains hypothesis generation complementing lineage tracing, not inference.')",
 "p('The gradient suggests a residence/migration framework (recently migrated types should show low inter-regional \\u03c9; resident types accumulate regional signatures), but the data provide no evidence for it: OPCs\\u2014the most actively migrating non-neuronal population\\u2014show the second-highest mean \\u03c9 (40.62), and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92); the framework remains hypothesis generation, not inference.')"),
# --- Screen ---
("p('Low CKI \\u03c9 for a cell type across two regions indicates transcriptomic similarity beyond baseline expectation, arising from non-exclusive mechanisms (developmental origin heterogeneity, embryonic colonization route boundaries [20-22], postnatal migration [23,24]). We report",
 "p('Low CKI \\u03c9 for a cell type across two regions indicates transcriptomic similarity beyond baseline expectation, with non-exclusive candidate mechanisms (developmental origin heterogeneity, colonization-route boundaries [20-22], postnatal migration [23,24]). We report"),
(" The catalogue below is therefore a prioritized hypothesis list, not discoveries; it also inherits the atlas\\u2019s donor structure (four donors; 94.5% of region pairs share at least one), leaving pair-level nominations subject to donor confounding. Region abbreviations follow the Siletti et al. dissection nomenclature (glossary in Supplementary Note 11).",
 " The catalogue below is therefore a prioritized hypothesis list, not discoveries, and inherits the atlas\\u2019s donor structure (four donors), leaving pair-level nominations subject to donor confounding (region glossary in Supplementary Note 11)."),
("p('The screen uses a multiplicative model: for each (cell_type, region_pair), expected_\\u03c9 = \\u03bc_ct \\u00d7 \\u03bc_pair / \\u03bc_grand (\\u03bc_ct the cell type\\u2019s global mean \\u03c9, \\u03bc_pair the pair\\u2019s mean \\u03c9, \\u03bc_grand = 38.55). A residual (observed / expected) well below 1 marks a cell type far less differentiated between two regions than expected from its own plasticity and the pair\\u2019s divergence\\u2014a signature of shared transcriptional state, potentially reflecting shared developmental history or recent migration. Three confidence tiers",
 "p('The screen uses a multiplicative model, expected_\\u03c9 = \\u03bc_ct \\u00d7 \\u03bc_pair / \\u03bc_grand (Methods): a residual (observed / expected) well below 1 marks a cell type far less differentiated between two regions than expected from its own plasticity and the pair\\u2019s divergence. Three confidence tiers"),
("Candidates concentrate in microglia (16 Strong) and oligodendrocytes (10), but the microglial share-level enrichment (2.30-fold) does not survive the design-matched null: the Strong rule fires preferentially on low-\\u03c9 classes (52.0 of the 148.3 null candidates are microglial; observed 16, fold 0.31, P = 0.990). We make no class-composition claim, consistent with the class-level test (microglial mean below null, P = 0.904).",
 "Candidates concentrate in microglia (16 Strong) and oligodendrocytes (10), but the microglial enrichment does not survive the design-matched null (52.0 of the 148.3 null candidates are microglial; observed 16, fold 0.31, P = 0.990): we make no class-composition claim."),
("whereas same-region halves showed a 37.6% lower-tail rate, confirming retained power; the small excess of real over pseudo rates is the marginal signature of true regional biology.",
 "whereas same-region halves showed a 37.6% lower-tail rate, confirming retained power."),
("converging on visual-relay and orbitofrontal dissections (five pairs involve the lateral geniculate nucleus, four the pulvinar, four the occipitotemporal area TF, with orbitofrontal areas A13 and A14 recurring; Supplementary Note 11).",
 "converging on visual-relay and orbitofrontal dissections (five pairs involve the lateral geniculate nucleus, four the pulvinar; Supplementary Note 11)."),
("Astrocytes, fibroblasts, and ependymal cells contributed sparse candidates compatible with published developmental mechanisms [26,28]; Bergmann glia, vascular cells, and choroid plexus contributed none\u2014the absence of Bergmann glia candidates is consistent with their transcriptionally constrained state in the adult cerebellum [26,27] and their purely intra-cerebellar comparison set. None of these signals survives multiple-testing correction; they are catalogued as hypothesis-generating targets for spatial-transcriptomic and lineage follow-up [19], not discoveries.",
 "Astrocytes, fibroblasts, and ependymal cells contributed sparse candidates compatible with published developmental mechanisms [26,28]; Bergmann glia, vascular cells, and choroid plexus contributed none [26,27]. All are catalogued as hypothesis-generating targets for spatial-transcriptomic and lineage follow-up [19], not discoveries."),
(" We therefore position the entire candidate list as hypothesis-generating, prioritized for lineage-tracing and spatial-transcriptomic validation rather than presented as discoveries.",
 " We therefore position the entire candidate list as hypothesis-generating rather than discoveries."),
]

nfail = 0
for old, new in EDITS:
    c = src.count(old)
    if c != 1:
        print("FAIL", c, old[:90]); nfail += 1; continue
    src = src.replace(old, new)
print("applied", len(EDITS) - nfail, "of", len(EDITS))
if nfail == 0:
    open(P, "w", encoding="utf-8", newline="\n").write(src)
    print("written")
else:
    print("NOT written (fix failures first)")
