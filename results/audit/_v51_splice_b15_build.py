#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51 batch-15: sync 38 failing v50-wording assertions in 99_build_nc_v49.py.

Three action classes (per assertion):
  - reword: expected string updated to v51 wording (still checked in ms)
  - flip:   ms -> sn (content migrated to SI in v51)
  - count:  numeric expectation updated (S6: 9 -> 10)

All-or-nothing: every OLD must match exactly once before anything is written.
"""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
TARGET = BASE / "99_build_nc_v49.py"

EDITS = [
    # --- S6: SI Supplementary Fig. refs 9 -> 10 (Supplementary Methods 5.1 adds one) ---
    ('check(n_sfig_sn == 9, f"V49-S6 SN Supplementary Fig. refs = 9 (v50: +Fig. 14) ({n_sfig_sn})")',
     'check(n_sfig_sn == 10, f"V49-S6 SN Supplementary Fig. refs = 10 (v51: +Supplementary Methods 5.1) ({n_sfig_sn})")'),

    # --- A13: ratio bias anchor reworded ---
    ('        ("1.3-fold", "A13 ratio bias"),',
     '        ("absorbs ratio bias", "A13 ratio bias (v51 wording)"),'),

    # --- N1: 0.963 ms -> sn (drop from ms anchor list) ---
    ('        ("0.963", "N1 Kang omega calibration median"),\n', ''),

    # --- N6: 90.9 ms -> sn (drop from ms anchor list) ---
    ('        ("90.9", "N6 brain T2 omega FPR"),\n', ''),

    # --- N9: pointer now short form "(Section 3.12)" ---
    ('("Section 3.12 of the Supplementary Information", "N9 Section 3.12 pointer x2"),',
     '("Section 3.12", "N9 Section 3.12 pointers present (v51 short form)"),'),

    # --- N15: bulk positioning phrase reworded ---
    ('("tissue-level functional divergence", "N15 bulk positioning phrase"),',
     '("tissue-level divergence at bulk resolution", "N15 bulk positioning phrase (v51 wording)"),'),

    # --- N17: count short-form pointers; N1/N6 sn checks inserted here ---
    ('''    check(ms.count("Section 3.12 of the Supplementary Information") == 3,
          "V49-N17 exactly 3 Section 3.12 pointers in MS (post-CC)")''',
     '''    check("0.963" in sn, "V49-N1 Kang omega calibration median (v51: SI)")
    check("90.9" in sn, "V49-N6 brain T2 omega FPR (v51: SI)")
    check(ms.count("Section 3.12") == 3,
          "V49-N17 exactly 3 Section 3.12 pointers in MS (v51 short form)")'''),

    # --- N25: 2.86 ms -> sn ---
    ('check("2.86" in ms, "V49-N25 high-purity LUAD ratio")',
     'check("2.86" in sn, "V49-N25 high-purity LUAD ratio (v51: SI Note 8)")'),

    # --- N27: admixture caveat phrase reworded ---
    ('check("fully explained by admixture" in ms, "V49-N27 admixture caveat phrase (v50)")',
     'check("abolished the apparent EGFR elevation" in ms, "V49-N27 admixture caveat phrase (v51 wording)")'),

    # --- N31: Cox P ms -> sn ---
    ('''    for pat, name in [("3,567", "N29 sample total post-CC"),
                      ("1.10\\u20132.46", "N30 Abstract ratio range post-CC"),
                      ("P = 0.48", "N31 Cox P post-CC")]:
        check(pat in ms, f"V49-{name}")''',
     '''    for pat, name in [("3,567", "N29 sample total post-CC"),
                      ("1.10\\u20132.46", "N30 Abstract ratio range post-CC")]:
        check(pat in ms, f"V49-{name}")
    check("P = 0.48" in sn, "V49-N31 Cox P post-CC (v51: SI)")'''),

    # --- N37: 'upper block of Table 1' -> v51 well-sampled clause ---
    ("""check('(Fig. 5; Table 1; Supplementary Fig. 5)' in ms and 'upper block of Table 1' in ms""",
     """check('(Fig. 5; Table 1; Supplementary Fig. 5)' in ms and '(n \\u2265 5 pairs; Table 1)' in ms"""),

    # --- N38: scope design argument reworded ---
    ("""    check('not to discriminate cell-type identity' in ms
          and 'housekeeping gene sets may differ across cell types' in ms
          and 'expected by design and delineates, rather than limits' in ms,
          "V49-N38 Scope design argument present (HK anchor cell-type-specific)")""",
     """    check('not cell-type identity' in ms
          and 'the housekeeping anchor is cell-type-specific' in ms
          and 'delineates, rather than limits, its scope' in ms,
          "V49-N38 Scope design argument present (HK anchor cell-type-specific, v51 wording)")"""),

    # --- N40: brain candidate concentration reworded ---
    ("""    check('concentrate in microglia (16 Strong) and oligodendrocytes (10)' in ms,
          "V49-N40 A5 brain candidate concentration (v50 wording)")""",
     """    check('Microglial candidates (16 of 39)' in ms,
          "V49-N40 A5 brain candidate concentration (v51 wording)")"""),

    # --- N47: Table 1 cross-type caveat reworded ---
    ("""    check('descriptive rather than calibrated differences' in ms,
          "V49-N47 B3 Table 1 cross-type caveat")""",
     """    check('cross-type gaps should be read descriptively' in ms,
          "V49-N47 B3 Table 1 cross-type caveat (v51 wording)")"""),

    # --- N49: donor-confounding disclosure reworded ---
    ("""    check('leaving pair-level nominations subject to donor confounding' in ms,
          "V49-N49 B5 brain screen donor-confounding disclosure")""",
     """    check('inheriting the atlas\\u2019s four-donor structure' in ms,
          "V49-N49 B5 brain screen donor-confounding disclosure (v51 wording)")"""),

    # --- N50: CC provenance ms -> sn ---
    ("""    check('sample-source code (positions 14\\u201315)' in ms
          and 'assigned to LIHC following a barcode audit' in ms,
          "V49-N50 B7 CC provenance disclosure (32 LUSC->LIHC)")""",
     """    check('sample-source code (positions 14\\u201315)' in sn
          and 'assigned to LIHC following a barcode audit' in sn,
          "V49-N50 B7 CC provenance disclosure (32 LUSC->LIHC; v51: SI)")"""),

    # --- N51: percentile interval type ms -> sn ---
    ("""    check('2.5th and 97.5th percentiles of the resampled ratios' in ms,
          "V49-N51 B8 TCGA cluster-bootstrap interval type stated (percentile)")""",
     """    check('2.5th and 97.5th percentiles of the resampled ratios' in sn,
          "V49-N51 B8 TCGA cluster-bootstrap interval type stated (percentile; v51: SI)")"""),

    # --- N56: seed 20260905 ms -> sn ---
    ("""    check('which used seed 20260903, and the small-cluster studentized bootstrap-t analysis '
          '(notebooks/89_cluster_boot_v45.py), which used seed 20260905' in ms,
          "V49-N56 N1 seed 20260905 declared in MS Methods")""",
     """    check('seed 20260905' in sn and '89_cluster_boot_v45.py' in sn,
          "V49-N56 N1 seed 20260905 declared (v51: SI)")"""),

    # --- N57: bootstrap-t pivot/SE v51 wording; MC coverage ms -> sn ---
    ("""    check('supersedes the earlier i.i.d. interval' in ms
          and 'influence-function (multiplier) sandwich standard error' in ms
          and 'Monte Carlo coverage 0.953/0.951 at 6\\u20137 clusters' in ms,
          "V49-N57 C6 studentized bootstrap-t pivot/SE described")""",
     """    check('superseding the earlier anti-conservative i.i.d. interval' in ms
          and 'influence-function sandwich standard error' in ms
          and 'Monte Carlo coverage 0.953/0.951 at 6\\u20137 clusters' in sn,
          "V49-N57 C6 studentized bootstrap-t pivot/SE described (v51 wording)")"""),

    # --- N58: Discussion composition numbers v51 wording (MS pooled; SI correlation) ---
    ("""    check('attenuates by only \\u22121.3% pooled (95% CI [\\u22124.8%, +2.0%]; per-cancer \\u221216% to +33%)' in ms
          and 'attenuates by \\u22120.5% pooled' not in ms
          and 'Spearman \\u03c1 = 0.364 pooled; 0.20\\u20130.51 per cancer type' in ms
          and '0.387 pooled' not in ms,
          "V49-N58 N2 Discussion composition numbers (v50 wording)")""",
     """    check('attenuates the pooled k_n coefficient by only \\u22121.3%' in ms
          and '\\u22121.3% pooled, 95% CI \\u22124.8% to +2.0%' in ms
          and 'attenuates by \\u22120.5% pooled' not in ms
          and 'Spearman \\u03c1 = 0.364 pooled' in sn
          and '0.387 pooled' not in ms,
          "V49-N58 N2 Discussion composition numbers (v51: MS pooled; SI correlation)")"""),

    # --- N58b: composition caliber (MS pooled; SI per-panel median |dz|) ---
    ("""    check('\\u22121.3% pooled, 95% CI \\u22124.8% to +2.0%' in ms
          and 'median |Delta z| 1.31-fold higher' in ms,
          "V49-N58b N2 composition caliber (v50 wording)")""",
     """    check('\\u22121.3% pooled, 95% CI \\u22124.8% to +2.0%' in ms
          and 'median |\\u0394z| 1.305-fold' in sn,
          "V49-N58b N2 composition caliber (v51: MS pooled; SI per-panel)")"""),

    # --- N60: Results size-balanced gradient v51 wording ---
    ("""    check('attenuates it to 1.74 (95% CI [1.64, 1.84])' in ms
          and 'co-report 6.10-fold (full-data) and 1.74-fold (size-balanced)' in ms,
          "V49-N60 C5 Results leads with size-balanced gradient (v50 wording)")""",
     """    check('attenuates it to 1.74 (95% CI [1.64, 1.84])' in ms
          and 'uncorrected upper bound inflated by class-size imbalance (equal-n estimate 1.74-fold, 95% CI [1.64, 1.84])' in ms,
          "V49-N60 C5 Results leads with size-balanced gradient (v51 wording)")"""),

    # --- N62: CC sensitivity v51 wording (MS clause; SI numbers) ---
    ("""    check('Fourth, excluding the 32 cell-line-derived LIHC samples' in ms
          and 'NN/TT 1.11, 95% CI [0.93, 1.30]' in ms
          and 'Four controls bound the interpretation' in ms,
          "V49-N62 C4 CC sensitivity analysis (fourth control, v50 wording)")""",
     """    check('excluding the 32 cell-line-derived LIHC samples leaves the LIHC null unchanged' in ms
          and 'NN/TT 1.11 [0.93, 1.30]' in sn
          and 'Four controls bound the interpretation' in ms,
          "V49-N62 C4 CC sensitivity analysis (v51 wording)")"""),

    # --- N67: span-matched control v51 wording ---
    ("""    check('span-matched control restricted to the 21 intra-cerebellar region pairs '
          'defining Bergmann glia yields 3.68' in ms
          and 'paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]' in sn,
          "V49-N67 B1 span-matched control (MS headline; SI Note 10 details, v50)")""",
     """    check('span-matched control (21 intra-cerebellar pairs) yields 3.68' in ms
          and 'paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]' in sn,
          "V49-N67 B1 span-matched control (MS headline; SI Note 10 details, v51)")"""),

    # --- N68: equal-n decomposition v51 wording ---
    ("""    check('k_f ratio is 2.09 under equal-n (full-data 2.03)' in ms
          and 'equal-n 1.29, astrocyte higher; full-data 0.31, Bergmann glia higher' in ms
          and '95% CI [2.02, 2.18]' in sn
          and '96_brain_downsample_decomp_v49.py' in sn,
          "V49-N68 B2 equal-n decomposition (MS headline; SI Note 10 details, v50)")""",
     """    check('k_f ratio 2.09 equal-n, 2.03 full-data' in ms
          and 'equal-n 1.29, astrocyte higher; full-data 0.31' in ms
          and '95% CI [2.02, 2.18]' in sn
          and '96_brain_downsample_decomp_v49.py' in sn,
          "V49-N68 B2 equal-n decomposition (MS headline; SI Note 10 details, v51)")"""),

    # --- N69: leave-one-out range v51 wording ---
    ("""    check('leave-one-population-out baseline range 6.75\\u20138.08' in ms
          and 'removing hepatocyte lowers it to 6.75' in sn,
          "V49-N69 B3 calibration leave-one-out (MS pointer; SI 3.10 details, v50)")""",
     """    check('leave-one-population-out range 6.75\\u20138.08' in ms
          and 'removing hepatocyte lowers it to 6.75' in sn,
          "V49-N69 B3 calibration leave-one-out (MS pointer; SI 3.10 details, v51)")"""),

    # --- N70: LUAD label permutation v51 wording ---
    ("""    check('whole-tumor label-permutation tests confirmed all three contrasts' in ms
          and '93_luad_group_permutation_v49.py' in sn,
          "V49-N70 B4 LUAD whole-tumor label permutation (MS pointer; SI 3.13, v50)")""",
     """    check('label-permutation confirmed; Section 3.13' in ms
          and '93_luad_group_permutation_v49.py' in sn,
          "V49-N70 B4 LUAD whole-tumor label permutation (MS pointer; SI 3.13, v51)")"""),

    # --- N78: MK/NI pointer v51 wording ---
    ("""    check('Section 1.4 of the Supplementary Information' in ms
          and 'never as evidence of positive selection' in ms,
          "V49-N78 A1 MK/NI pointer to SI 1.4 (v50)")""",
     """    check('caveats are in Section 1.4' in ms
          and 'never as evidence of positive selection' in ms,
          "V49-N78 A1 MK/NI pointer to SI 1.4 (v51 wording)")"""),

    # --- N81: sample-count reconciliation ms -> sn ---
    ("""    check('3 do not appear in the assembled pair table' in ms
          and '26 further samples appear only in tumor\\u2013normal pairs' in ms
          and 'spans 3,593 unique barcodes' in ms,
          "V49-N81 B1 sample-count reconciliation (3,596/3,593/3,567)")""",
     """    check('3 do not appear in the assembled pair table' in sn
          and '26 further samples appear only in tumor\\u2013normal pairs' in sn
          and 'spans 3,593 unique barcodes' in sn,
          "V49-N81 B1 sample-count reconciliation (3,596/3,593/3,567; v51: SI)")"""),

    # --- N82: smoking covariate (MS phrase; SI numbers) ---
    ("""    check('alone or jointly with admixture, age, and sex' in ms
          and '\\u0394\\u03c9 +13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3' in ms,
          "V49-N82 B2 smoking covariate wording (v50)")""",
     """    check('alone or jointly with admixture, age, and sex' in ms
          and '+13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3 with smoking, age, and sex' in sn,
          "V49-N82 B2 smoking covariate wording (v51: MS phrase; SI numbers)")"""),

    # --- N86: composition bootstrap B=1000 v51 wording ---
    ("""    check('cluster-bootstrap intervals (B = 1,000), the tumor-pair coefficient' in ms
          and 'B = 1,000 for the composition cluster bootstrap' in ms""",
     """    check('B = 1,000 composition cluster bootstrap' in ms
          and 'B = 1,000 for the composition cluster bootstrap' in sn"""),
    ('"V49-N86 C1 composition bootstrap B unified to 1,000 (MS/SI/Guide)")',
     '"V49-N86 C1 composition bootstrap B unified to 1,000 (MS/SI/Guide, v51)")'),

    # --- N87: per-cancer attenuation v51: SI only (drop ms clause) ---
    ("""          '\\u221210.0% [\\u221227.8%, +6.8%]' in sn
          and '\\u221216% to +33%' in ms,
          "V49-N87 C1 per-cancer attenuation updated (B=1000)")""",
     """          '\\u221210.0% [\\u221227.8%, +6.8%]' in sn,
          "V49-N87 C1 per-cancer attenuation updated (B=1000; v51: SI only)")"""),

    # --- N88: aggregation-order ms -> sn ---
    ("""    check('rank ordering is largely preserved (Spearman \\u03c1 = 0.78)' in ms
          and 'mouse Tabula Muris pilot and the human Tabula Sapiens pipelines' in gd
          and 'Aggregation-order same-data quantification (v49.14)' in gd
          and 'control-category median baseline itself moves from 6.46 to 10.94' in gd,
          "V49-N88 C3 aggregation-order quantified + attribution unified")""",
     """    check('rank ordering is largely preserved (Spearman \\u03c1 = 0.78)' in sn
          and 'mouse Tabula Muris pilot and the human Tabula Sapiens pipelines' in gd
          and 'Aggregation-order same-data quantification (v49.14)' in gd
          and 'control-category median baseline itself moves from 6.46 to 10.94' in gd,
          "V49-N88 C3 aggregation-order quantified + attribution unified (v51: SI)")"""),

    # --- N100: span-matched residual decomposition ms -> sn ---
    ("""    check('residual again k_n-driven: k_f 1.39 versus k_n 0.33'
          in ms and 'Supplementary Note 10' in ms,
          "V49-N100 m2 span-matched residual decomposition in MS (v50 wording)")""",
     """    check('decomposes the residual 3.68-fold gradient into k_f 1.39 and k_n 0.33'
          in sn and 'Supplementary Note 10' in ms,
          "V49-N100 m2 span-matched residual decomposition (v51: SI Note 10)")"""),

    # --- N101: ependymal reversal v51 wording ---
    ("""    check('ependymal cells (P 0.058 free versus 0.021 stratified)' in ms
          and 'stratified q = 0.052' in ms,
          "V49-N101 m3 ependymal stratified-reversal note in MS")""",
     """    check('ependymal cells\\u2014the one class moving against the conservative direction\\u2014still do not survive (stratified q = 0.052)' in ms,
          "V49-N101 m3 ependymal stratified-reversal note in MS (v51 wording)")"""),

    # --- N102: exact Mann-Whitney P v51 wording ---
    ("""    check('Mann-Whitney U, P = 5.6 \\u00d7 10\\u207b\\u00b9\\u2078' in ms
          and 'Mann-Whitney U, P < 0.001' not in ms,
          "V49-N102 m4 exact cross-organ Mann-Whitney P (5.6e-18)")""",
     """    check('Mann-Whitney P = 5.6 \\u00d7 10\\u207b\\u00b9\\u2078' in ms
          and 'Mann-Whitney U, P < 0.001' not in ms,
          "V49-N102 m4 exact cross-organ Mann-Whitney P (5.6e-18, v51 wording)")"""),

    # --- N104: agg-order median baseline ms -> sn ---
    ("""    check('split-control median baseline itself moves from 6.46 to 10.94' in ms,
          "V49-N104 R5 median qualifier on agg-order baseline (MS)")""",
     """    check('split-control median baseline itself moves from 6.46 to 10.94' in sn,
          "V49-N104 R5 median qualifier on agg-order baseline (v51: SI)")"""),

    # --- N53: MK fourfold correspondence pointer v51 wording ---
    ("""    check('Section 1.4 of the Supplementary Information' in ms
          and 'synonymous-site divergence (Ks)' in sn""",
     """    check('caveats are in Section 1.4' in ms
          and 'synonymous-site divergence (Ks)' in sn"""),
]

src = TARGET.read_text(encoding="utf-8")

# verify all OLDs match exactly once before writing
ok = True
for i, (old, new) in enumerate(EDITS, 1):
    n = src.count(old)
    tag = "OK " if n == 1 else "BAD"
    if n != 1:
        ok = False
    print(f"[{tag}] edit {i:2d}: matches={n}  {old[:70]!r}")
if not ok:
    raise SystemExit("ABORT: some OLD strings did not match exactly once; nothing written.")

for old, new in EDITS:
    src = src.replace(old, new)

TARGET.write_text(src, encoding="utf-8")
print(f"\nAll {len(EDITS)} edits applied -> {TARGET.name}")
