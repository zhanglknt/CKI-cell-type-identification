"""v51 splice batch 5: TCGA paragraphs [48]/[49]/[50]."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p(f'We applied CKI to TCGA",
 r"p(f'We applied CKI to TCGA bulk RNA-seq data across five cancer types (LUAD, LUSC, LIHC, KIRC, BRCA) [10,11], totalling {_tc[\"n_total\"]:,} samples. Because bulk RNA-seq averages over tumor, stromal, and immune compartments, \u03c9 here quantifies divergence between tissue states rather than between cell types; we therefore compare tumor\u2013tumor (TT), normal\u2013normal (NN), and tumor\u2013normal (TN) pairs within each cancer type (Fig. 4; Supplementary Fig. 4). A consistent pan-cancer reversal emerged: NN pairs were more divergent than TT pairs in all five cancer types (mean NN/TT \u03c9: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.10; cluster-bootstrap CI excluding 1 in four of five, LIHC excepted). Component decomposition identified the mechanism: TT k_n exceeded NN k_n by 1.3\u20133.3-fold in every cancer type (95% CIs excluding 1 in all five), whereas TT k_f was equal to or higher than NN k_f\u2014the reversal reflects a more stable housekeeping baseline among adjacent non-tumor specimens, not smaller functional-gene divergence of tumor cells (Fig. 4a).')"))
R.append((r"p('To ask whether the ratio resolves",
 r"p('To ask whether the ratio resolves biologically distinct tumor states, we stratified LUAD tumors by driver mutation (61 EGFR-mutant, 120 KRAS-mutant, 311 wild-type) using per-tumor \u03c9 (Fig. 4b). KRAS-mutant tumors showed the highest tissue-level divergence (mean \u03c9 = 136.9 versus 115.4 wild-type and 122.2 EGFR-mutant; Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; Dunn\u2013Holm P \u2264 0.008 for both KRAS contrasts, P = 0.39 for EGFR\u2013wild-type); whole-tumor label-permutation tests confirmed all three contrasts (Section 3.13 of the Supplementary Information). The KRAS elevation was carried predominantly by a lower housekeeping baseline (~84% of the log-\u03c9 gap) with an accompanying functional component (KRAS versus EGFR under k_f alone, P = 0.015). Adjustment for ESTIMATE stromal/immune admixture left the KRAS\u2013wild-type difference significant for both components (adjusted log-\u03c9 ratio 1.19, 95% CI [1.12, 1.26]), whereas the apparent EGFR elevation was fully explained by admixture (all adjusted P > 0.4); adjusting for smoking, alone or jointly with admixture, age, and sex, left the contrast essentially unchanged (\u0394\u03c9 +13.3, P = 1.4 \u00d7 10\u207b\u00b3; per-model values in Section 3.13). TP53 co-mutation and histological subtype were not adjusted for, so the KRAS contrast carries residual confounding; stratifications beyond LUAD are denominator-dominated vignettes (Supplementary Note 9).')"))
R.append((r"p('Four controls bound the interpretation",
 r"p('Four controls bound the interpretation (Supplementary Note 8). First, composition adjustment left the pooled tumor-pair k_n coefficient essentially unchanged (\u22121.3% pooled, 95% CI \u22124.8% to +2.0%), and ESTIMATE stromal/immune scoring showed admixture can only weaken, not create, the TT k_n elevation (high-purity-half comparisons increased the ratio in all five, e.g. LUAD 2.46 \u2192 2.86). Second, all TCGA statistics were recomputed under a linear probability mapping (the authoritative caliber), with all key results preserved (LIHC effect size mapping-sensitive: 1.10 versus 1.31 under softmax; Section 1.7). Third, LUAD KRAS identity panels showed no enrichment for any MSigDB Hallmark program [15] after correction (all q \u2265 0.24), and composition-adjusted regressions retained the TT \u2265 NN k_f ordering in all five cancer types. Fourth, excluding the 32 cell-line-derived LIHC samples leaves the LIHC null result unchanged (NN/TT 1.11, 95% CI [0.93, 1.30]). TCGA \u201cnormal\u201d samples are adjacent non-tumor tissues rather than healthy donor tissue, and per-tumor \u03c9 was not associated with overall survival (LIHC Cox hazard ratio per SD 1.07, 95% CI 0.88\u20131.31): we report all TCGA findings as tissue-level divergence at bulk resolution, pending single-cell or deconvolution-based validation.')"))

nfail = 0
for prefix, newline in R:
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        print('FAIL prefix not unique:', prefix[:60], len(idx)); nfail += 1; continue
    old = lines[idx[0]]
    lines[idx[0]] = newline
    print(f'OK L{idx[0]+1}: {len(old.split())} -> {len(newline.split())}')
if nfail:
    raise SystemExit(1)
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('batch 5 written')
