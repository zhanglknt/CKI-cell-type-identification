# v50 Phase C: flip 29 build assertions to match migrated/compressed text
P = r"C:\Users\KnightZ\Desktop\细胞受选择\99_build_nc_v49.py"
src = open(P, encoding="utf-8").read()

E = []

E.append((
'''        ("LIHC 1.10 (0.93", "N11 LIHC NN/TT ratio (post-CC)"),''',
'''        ("LIHC 1.10;", "N11 LIHC NN/TT ratio (post-CC, v50 wording)"),'''))

E.append((
'''        ("1.3\\u20133.3-fold (mean ratios", "N12 k_n fold elevation (mean, post-CC)"),''',
'''        ("1.3\\u20133.3-fold in every cancer type", "N12 k_n fold elevation (v50 wording)"),'''))

E.append((
'''    for pat, name in [("16.8", "N23 purity-adjusted KRAS omega"),
                      ("13.6", "N24 joint-adjusted KRAS omega"),
                      ("2.86", "N25 high-purity LUAD ratio"),
                      ("stromal or immune admixture", "N27 admixture caveat phrase")]:
        check(pat in ms, f"V49-{name}")''',
'''    check("2.86" in ms, "V49-N25 high-purity LUAD ratio")
    check("fully explained by admixture" in ms, "V49-N27 admixture caveat phrase (v50)")
    # v50: adjusted-delta details migrated to SI 3.13
    check("\\u0394\\u03c9 +16.8" in sn, "V49-N23 purity-adjusted KRAS omega (v50: SI 3.13)")
    check("+13.6" in sn, "V49-N24 joint-adjusted KRAS omega (v50: SI 3.13)")'''))

E.append((
'''    check('one committed OPC, one OPC) accounting for the remainder (39 in total)' in ms,
          "V49-N40 A5 brain enumeration sums to 39 (OPC lineage included)")''',
'''    check('concentrate in microglia (16 Strong) and oligodendrocytes (10)' in ms,
          "V49-N40 A5 brain candidate concentration (v50 wording)")'''))

E.append((
'''    check('median ratios 2.18\\u20133.70 in the Supplementary Information' in ms,
          "V49-N41 A6 mean/median caliber cross-pointer (TCGA k_n ratios)")''',
'''    check('2.18\\u20133.70' in sn,
          "V49-N41 A6 mean/median caliber cross-pointer (v50: SI carries medians)")'''))

E.append((
'''    check('McDonald\\u2013Kreitman-style contrast' in ms
          and '34. McDonald' in ms and 'Adh locus in Drosophila' in ms,
          "V49-N46 B2 Ka/Ks structural inversion + MK ref [34]")''',
'''    check('McDonald\\u2013Kreitman-style fourth term' in ms
          and '34. McDonald' in ms and 'Adh locus in Drosophila' in ms,
          "V49-N46 B2 MK fourth-term pointer + MK ref [34] (v50)")'''))

E.append((
'''    check('attenuates by \\u22121.3% pooled (cluster-bootstrap median \\u22121.3%, '
          '95% CI [\\u22124.8%, +2.0%])' in ms
          and 'attenuates by \\u22120.5% pooled' not in ms
          and 'Spearman \\u03c1 = 0.364 pooled, P < 10\\u207b\\u00b3\\u2070\\u2070; 0.20\\u20130.51 per cancer type' in ms
          and '0.387 pooled' not in ms,
          "V49-N58 N2 Discussion composition numbers = post-CC linear caliber")''',
'''    check('attenuates by only \\u22121.3% pooled (95% CI [\\u22124.8%, +2.0%]; per-cancer \\u221216% to +33%)' in ms
          and 'attenuates by \\u22120.5% pooled' not in ms
          and 'Spearman \\u03c1 = 0.364 pooled; 0.20\\u20130.51 per cancer type' in ms
          and '0.387 pooled' not in ms,
          "V49-N58 N2 Discussion composition numbers (v50 wording)")'''))

E.append((
'''    check('\\u22121.3% pooled; cluster-bootstrap median \\u22121.3%' in ms
          and 'median |Delta z| 1.31-fold higher for the three-panel composite' in ms,
          "V49-N58b N2 Results composition caliber (point + bootstrap median, post-CC linear)")''',
'''    check('\\u22121.3% pooled, 95% CI \\u22124.8% to +2.0%' in ms
          and 'median |Delta z| 1.31-fold higher' in ms,
          "V49-N58b N2 composition caliber (v50 wording)")'''))

E.append((
'''    check('with endpoint gradients of 6.60, 6.10, and 4.12 at thresholds 10, 20, and 50 '
          '(at 100 nuclei the eight retained classes exclude Bergmann glia' in ms,
          "V49-N59 N3 threshold-sweep gradient values completed")''',
'''    _si_blob = "\\n".join(str(_c.value) for _ws in _si_xlsx for _row in _ws.iter_rows()
                         for _c in _row if _c.value is not None)
    check('6.60' in _si_blob and '4.12' in _si_blob,
          "V49-N59 N3 threshold-sweep gradient values (v50: Supp Table 19)")'''))

E.append((
'''    check('Class-mean \\u03c9 spanned a 1.74-fold size-balanced regional gradient' in ms
          and 'The brain analysis showed a regional \\u03c9 gradient across 10 cell classes '
          '(size-balanced 1.74-fold; uncorrected full-data 6.10-fold' in ms,
          "V49-N60 C5 Results/Discussion lead with size-balanced gradient")''',
'''    check('attenuates it to 1.74 (95% CI [1.64, 1.84])' in ms
          and 'co-report 6.10-fold (full-data) and 1.74-fold (size-balanced)' in ms,
          "V49-N60 C5 Results leads with size-balanced gradient (v50 wording)")'''))

E.append((
'''    check('Pearson r = \\u22120.850, P = 0.0018' in ms,
          "V49-N61 C7 class-size Pearson correlation added")''',
'''    check('0.850' in sn,
          "V49-N61 C7 class-size Pearson correlation (v50: SI Note 10)")'''))

E.append((
'''    check('Fourth, excluding the 32 cell-line-derived (CC) LIHC samples' in ms
          and 'NN/TT 1.11, 95% CI [0.93, 1.30]' in ms
          and 'Four controls bound the interpretation' in ms,
          "V49-N62 C4 CC sensitivity analysis (fourth control)")''',
'''    check('Fourth, excluding the 32 cell-line-derived LIHC samples' in ms
          and 'NN/TT 1.11, 95% CI [0.93, 1.30]' in ms
          and 'Four controls bound the interpretation' in ms,
          "V49-N62 C4 CC sensitivity analysis (fourth control, v50 wording)")'''))

E.append((
'''    check('3.68-fold span-matched intra-cerebellar' in ms
          and 'span-matched gradient of 3.68 (ratio of class means; paired '
          'per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]' in ms
          and 'size-balanced but not span-balanced' in ms,
          "V49-N67 B1 span-matched intra-cerebellar control (3.68) in MS")''',
'''    check('span-matched control restricted to the 21 intra-cerebellar region pairs '
          'defining Bergmann glia yields 3.68' in ms
          and 'paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]' in sn,
          "V49-N67 B1 span-matched control (MS headline; SI Note 10 details, v50)")'''))

E.append((
'''    check('k_f ratio is 2.09 (95% CI [2.02, 2.18]) under equal-n' in ms
          and 'equal-n 1.29, 95% CI [1.21, 1.41], astrocyte higher; '
          'full-data 0.31, Bergmann glia higher' in ms
          and '96_brain_downsample_decomp_v49.py' in ms,
          "V49-N68 B2 equal-n k_f/k_n decomposition (2.09/1.29/0.31) in MS")''',
'''    check('k_f ratio is 2.09 under equal-n (full-data 2.03)' in ms
          and 'equal-n 1.29, astrocyte higher; full-data 0.31, Bergmann glia higher' in ms
          and '95% CI [2.02, 2.18]' in sn
          and '96_brain_downsample_decomp_v49.py' in sn,
          "V49-N68 B2 equal-n decomposition (MS headline; SI Note 10 details, v50)")'''))

E.append((
'''    check('removing hepatocyte lowers the baseline to 6.75 (\\u221212.3%; '
          'leave-one-out range 6.75\\u20138.08; median-of-population-means 7.12)' in ms,
          "V49-N69 B3 calibration leave-one-out in MS")''',
'''    check('leave-one-population-out baseline range 6.75\\u20138.08' in ms
          and 'removing hepatocyte lowers it to 6.75' in sn,
          "V49-N69 B3 calibration leave-one-out (MS pointer; SI 3.10 details, v50)")'''))

E.append((
'''    check('KW P = 0.0001 (B = 10,000), KRAS\\u2013WT P = 0.0001, '
          'KRAS\\u2013EGFR P = 0.003, EGFR\\u2013WT P = 0.21' in ms
          and '93_luad_group_permutation_v49.py' in ms,
          "V49-N70 B4 LUAD whole-tumor label permutation in MS")''',
'''    check('whole-tumor label-permutation tests confirmed all three contrasts' in ms
          and '93_luad_group_permutation_v49.py' in sn,
          "V49-N70 B4 LUAD whole-tumor label permutation (MS pointer; SI 3.13, v50)")'''))

E.append((
'''    check('on the log-\\u03c9 scale the adjusted KRAS/WT ratio is 1.19, '
          'bootstrap 95% CI [1.12, 1.26], so the adjustment conclusion is '
          'scale-robust' in ms,
          "V49-N71 C4b log-omega scale sensitivity in MS")''',
'''    check('adjusted log-\\u03c9 ratio 1.19, 95% CI [1.12, 1.26]' in ms,
          "V49-N71 C4b log-omega scale sensitivity (v50 wording)")'''))

E.append((
'''    check('LIHC 1.17 with all tumors versus 1.19 excluding CC, '
          '95% CI [1.01, 1.44]' in ms
          and 'barcode source-code audit' in ms
          and '94_cc_audit_sensitivity_v49.py' in ms,
          "V49-N72 B5/B6 CC exclusion sensitivity + barcode audit in MS")''',
'''    check('high-purity-half 1.17 versus 1.19 excluding CC, 95% CI [1.01, 1.44]' in sn
          and '94_cc_audit_sensitivity_v49.py' in sn,
          "V49-N72 B5/B6 CC exclusion sensitivity + barcode audit (v50: SI 3.13)")'''))

E.append((
'''    check('parallels the reciprocal of the neutrality index' in ms
          and 'biased upward' in ms
          and 'lower bound on the polymorphism class' in ms,
          "V49-N78 A1 NI reciprocal direction + split-half caveat (MS)")''',
'''    check('Section 1.4 of the Supplementary Information' in ms
          and 'never as evidence of positive selection' in ms,
          "V49-N78 A1 MK/NI pointer to SI 1.4 (v50)")'''))

E.append((
'''    check('95% CI [0.997, 1.880], which includes 1' in ms
          and 'BRCA 1.57 (1.34\\u20131.85)' in ms,
          "V49-N80 A2/B18 CI precision fixes")''',
'''    check('0.997, 1.880' in sn and 'BRCA 1.57' in ms,
          "V49-N80 A2/B18 CI precision (v50: MS ratio; SI CIs)")'''))

E.append((
'''    check('alone, jointly with admixture, or jointly with age and sex' in ms
          and '+13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3 with smoking, age, and sex' in ms,
          "V49-N82 B2 smoking covariate wording matches fitted models")''',
'''    check('alone or jointly with admixture, age, and sex' in ms
          and '\\u0394\\u03c9 +13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3' in ms,
          "V49-N82 B2 smoking covariate wording (v50)")'''))

E.append((
'''    check('all P < 10\\u207b\\u00b9\\u2074\\u2075' in ms
          and 'largest per-cancer P = 7.7 \\u00d7 10\\u207b\\u00b9\\u2079' in ms,
          "V49-N83 B7 exact P values replace thresholds")''',
'''    check('all P < 10\\u207b\\u00b9\\u2074\\u2075' in ms
          and '7.7 \\u00d7 10\\u207b\\u00b9\\u2079' in sn,
          "V49-N83 B7 exact P values (v50: SI Note 8 per-cancer P)")'''))

E.append((
'''    check('cluster bootstrap confidence intervals (B = 1,000), the tumor-pair coefficient' in ms
          and 'B = 1,000 for the composition cluster bootstrap' in ms''',
'''    check('cluster-bootstrap intervals (B = 1,000), the tumor-pair coefficient' in ms
          and 'B = 1,000 for the composition cluster bootstrap' in ms'''))

E.append((
'''    check('residual again predominantly k_n-driven: k_f 1.39 versus k_n 0.33'
          in ms and 'Supplementary Note 10' in ms,
          "V49-N100 m2 span-matched residual decomposition in MS")''',
'''    check('residual again k_n-driven: k_f 1.39 versus k_n 0.33'
          in ms and 'Supplementary Note 10' in ms,
          "V49-N100 m2 span-matched residual decomposition in MS (v50 wording)")'''))

E.append((
'''    check('synonymous-site divergence (Ks) to HK-gene divergence (k_n)' in ms
          and 'nonsynonymous divergence (Ka) to functional-gene divergence (k_f)' in ms
          and 'a species pair to the two cell populations being compared' in ms
          and 'the split-half calibration baseline (within-population \\u03c9 \\u2248 7.70) to the '
          'polymorphism class' in ms
          and 'parallels the reciprocal of the neutrality index' in ms
          and 'substantive rather than nominal' not in ms,
          "V49-N53 MK fourfold correspondence in MS Discussion (self-grading removed)")''',
'''    # v50: MK fourfold correspondence migrated to SI 1.4; MS carries pointer
    check('Section 1.4 of the Supplementary Information' in ms
          and 'synonymous-site divergence (Ks)' in sn
          and 'polymorphism class' in sn
          and 'reciprocal of the neutrality index' in sn
          and 'substantive rather than nominal' not in ms,
          "V49-N53 MK fourfold correspondence migrated to SI 1.4 (v50)")'''))

E.append((
'''    check("Supplementary Note 1" in ms and "Supplementary Note 15" in ms, "V49-SC5 notes 1/15 cited")''',
'''    check("Supplementary Note 1" in ms and "Supplementary Notes 1\\u201316" in ms,
          "V49-SC5 notes cited (v50: 1-16 span)")'''))

nfail = 0
for old, new in E:
    c = src.count(old)
    if c != 1:
        print("FAIL", c, old[:90].replace("\n", " ")); nfail += 1; continue
    src = src.replace(old, new)
print("applied", len(E) - nfail, "of", len(E))
if nfail == 0:
    open(P, "w", encoding="utf-8", newline="\n").write(src)
    print("written")
else:
    print("NOT written")
