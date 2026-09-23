#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51r2 batch-17: re-sync _nc49_ms_verify.py (39 checks) + _nc49_si_verify.py
(1 check) to v51r2 wording, and add hard exit gates to all three verify
scripts (they previously always exited 0, masking failures).
All-or-nothing per file."""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
MSV = BASE / "results" / "audit" / "_nc49_ms_verify.py"
SIV = BASE / "results" / "audit" / "_nc49_si_verify.py"
CLV = BASE / "results" / "audit" / "_nc49_cl_guide_verify.py"

MS_EDITS = [
    ("""chk('Results Section 3.12 ref (v50)',
    'relative-calibration advantage (Section 3.12 of the Supplementary Information)' in full)""",
     """chk('Results Section 3.12 ref (v51 short form)',
    'relative-calibration advantage' in full and 'Section 3.12' in full)"""),
    ("""chk('Methods Section 3.12 ref',
    'Section 3.12 of the Supplementary Information reports the full audit of design, diagnostics, and per-class results' in full)""",
     """chk('Methods Section 3.12 ref (v51)',
    'per-class values in Section 3.12' in full)"""),
    ("""chk('Section 3.12 referenced 3x (Results, Methods, class-composition note)',
    full.count('Section 3.12 of the Supplementary Information') == 3,
    f'found {full.count("Section 3.12 of the Supplementary Information")}')""",
     """chk('Section 3.12 referenced 3x (v51 short form)',
    full.count('Section 3.12') == 3,
    f'found {full.count("Section 3.12")}')"""),
    ("""chk('MWU deleted from main claims; permutation -> Section 3.13 (v50)',
    'whole-tumor label-permutation tests confirmed all three contrasts (Section 3.13 of the Supplementary Information)' in full
    and 'per-tumor Mann-Whitney' not in full)""",
     """chk('MWU deleted from main claims; permutation -> Section 3.13 (v51)',
    'label-permutation confirmed; Section 3.13' in full
    and 'per-tumor Mann-Whitney' not in full)"""),
    ("""chk('T1 qualified (continuous metrics)',
    'lowest misreporting rate among the continuous divergence metrics' in full)""",
     """chk('T1 qualified (continuous metrics, v51)',
    'misreported least among the continuous divergence metrics' in full)"""),
    ("""chk('marker Jaccard T1 19.9% admitted (v50: MS + SI)',
    'marker Jaccard distance was lower still (19.9%)' in full and 'T1 FPR 19.9%' in sfull)""",
     """chk('marker Jaccard T1 19.9% admitted (v51: MS legend + SI)',
    'marker Jaccard is lower still on the false-positive statistic (T1 19.9%' in full and 'T1 FPR 19.9%' in sfull)"""),
    ("""chk('Jaccard weakest on genuine divergence admitted (v50)',
    'responded weakest to genuine regional divergence' in full)""",
     """chk('Jaccard weakest on genuine divergence admitted (v51)',
    'weakest to real regional divergence' in full)"""),
    ("""chk('no 3,596 stray residue (v49.14: single attrition mention)',
    full.count('3,596') == 1 and 'of the 3,596 expression-matrix samples' in full)""",
     """chk('no 3,596 stray residue (v51: MS clean; SI x2)',
    '3,596' not in full and sfull.count('3,596') == 2)"""),
    ("""chk('Methods per-cancer counts',
    'LUAD: 493 tumor + 76 normal' in full and 'LUSC: 534 tumor + 58 normal' in full
    and 'LIHC: 398 tumor + 57 normal' in full and 'KIRC: 750 tumor + 82 normal' in full
    and 'BRCA: 1010 tumor + 109 normal' in full)""",
     """chk('Methods per-cancer counts (v51)',
    'LUAD 493 tumor + 76 normal; LUSC 534 + 58; LIHC 398 + 57; KIRC 750 + 82; BRCA 1,010 + 109' in full)"""),
    ("""chk('attrition three-way arithmetic (v49.14)',
    '3 do not appear in the assembled pair table' in full
    and 'spans 3,593 unique barcodes' in full
    and '29 expression-matrix samples were excluded' not in full)""",
     """chk('attrition three-way arithmetic (v51: SI)',
    '3 do not appear in the assembled pair table' in sfull
    and 'spans 3,593 unique barcodes' in sfull
    and '29 expression-matrix samples were excluded' not in full)"""),
    ("""chk('k_n mechanism sentence new range (v50: MS range; per-cancer CIs in SI Table 11)',
    'TT k_n exceeded NN k_n by 1.3\\u20133.3-fold in every cancer type (95% CIs excluding 1 in all five)' in full)""",
     """chk('k_n mechanism sentence new range (v51: MS range; per-cancer CIs in SI Table 11)',
    'TT k_n exceeded NN k_n by 1.3\\u20133.3-fold in every cancer type' in full)"""),
    ("""chk('pair-level MWU P deleted from main claims (v50)',
    'Dunn\\u2013Holm P \\u2264 0.008 for both KRAS contrasts' in full
    and 'whole-tumor label-permutation tests confirmed all three contrasts' in full)""",
     """chk('pair-level MWU P deleted from main claims (v51)',
    'Dunn\\u2013Holm P \\u2264 0.008 for both KRAS contrasts' in full
    and 'label-permutation confirmed; Section 3.13' in full)"""),
    ("""chk('LIHC mapping-sensitivity honest (v50)',
    'LIHC effect size mapping-sensitive: 1.10 versus 1.31 under softmax' in full)""",
     """chk('LIHC mapping-sensitivity honest (v51)',
    'LIHC mapping-sensitive: 1.10 versus 1.31 softmax' in full)"""),
    ("""chk('softmax demoted to SI sensitivity (v50)',
    'recomputed under a linear probability mapping (the authoritative caliber)' in full
    and 'Section 1.7' in full and 'softmax-caliber values are archived here as a sensitivity analysis' in sfull)""",
     """chk('softmax demoted to SI sensitivity (v51)',
    'recomputed under the authoritative linear probability mapping' in full
    and 'Section 1.7' in full and 'softmax-caliber values are archived here as a sensitivity analysis' in sfull)"""),
    ("""chk('smoking three-model adjustment (v50: MS headline; SI models)',
    'alone or jointly with admixture, age, and sex' in full and '+13.3' in full
    and '+13.6' in sfull and '+13.9' in sfull)""",
     """chk('smoking three-model adjustment (v51: MS headline; SI models)',
    'alone or jointly with admixture, age, and sex' in full and '+13.3' in sfull
    and '+13.6' in sfull and '+13.9' in sfull)"""),
    ("""chk('purity proxy limitation (Results)',
    'monotonically equivalent to published ESTIMATE purity' in full)""",
     """chk('purity proxy limitation (v51: SI)',
    'monotonically equivalent to published ESTIMATE purity' in sfull)"""),
    ("""chk('pack-years sparsity documented (v50: Methods)',
    'pack-years for 356' in full)""",
     """chk('pack-years sparsity documented (v51: MS note; SI detail)',
    'pack-years reported descriptively' in full and 'pack-years for 356' in sfull)"""),
    ("""chk('batch/center limitation (v50)', 'tissue-source site and batch' in full)""",
     """chk('batch/center limitation (v51)', 'differ in source site and batch' in full)"""),
    ("""chk('GTEx healthy-reference limitation (v50 wording)',
    'adjacent non-tumor tissue is not healthy tissue' in full and 'external healthy reference' in full)""",
     """chk('GTEx healthy-reference limitation (v51 wording)',
    'Adjacent non-tumor is not healthy tissue' in full and 'external healthy reference' in full)"""),
    ("""chk('Discussion epidemiology sentence (v50: adjustment retained)',
    'Adjusting for smoking' in full and 'essentially unchanged' in full)""",
     """chk('Discussion epidemiology sentence (v51: adjustment retained)',
    'left the contrast essentially unchanged' in full)"""),
    ("""chk('k_n admix correlation range', 'r = \\u22120.23 to \\u22120.42' in full)""",
     """chk('k_n admix correlation range (v51r2: SI Note 8)', 'r = \\u22120.23 to \\u22120.42' in sfull)"""),
    ("""chk('high-purity half LUAD (v50)', 'LUAD 2.46 \\u2192 2.86' in full)""",
     """chk('high-purity half LUAD (v51: SI Note 8)', 'LUAD 2.46 \\u2192 2.86' in sfull)"""),
    ("""chk('high-purity half LIHC caliber kept (v50: MS + SI 3.13)',
    'high-purity-half comparisons increased the ratio in all five' in full
    and 'high-purity-half 1.17 versus 1.19 excluding CC' in sfull)""",
     """chk('high-purity half LIHC caliber kept (v51: MS + SI 3.13)',
    'high-purity-half comparisons increased the TT k_n elevation in all five' in full
    and 'high-purity-half 1.17 versus 1.19 excluding CC' in sfull)"""),
    ("""chk('reversal not admixture artefact (v50)',
    'admixture can only weaken, not create, the TT k_n elevation' in full)""",
     """chk('reversal not admixture artefact (v51)',
    'admixture can only weaken, not create' in full)"""),
    ("""chk('Methods ESTIMATE block',
    'official ESTIMATE gene sets (141 stromal and 141 immune genes)' in full
    and '45,504 expressed genes' in full)""",
     """chk('Methods ESTIMATE block (v51: MS count; SI gene sets)',
    'official ESTIMATE gene sets (141 stromal and 141 immune genes)' in sfull
    and '45,504 expressed genes' in full)"""),
    ("""chk('Methods cBioPortal smoking block',
    'study luad_tcga, patient-level clinical data' in full
    and 'smoking status available for 508' in full
    and '427 of 492 tumors with known smoking status, 87%' in full)""",
     """chk('Methods cBioPortal smoking block (v51: SI)',
    'study luad_tcga, patient-level clinical data' in sfull
    and 'smoking status available for 508' in sfull
    and '427 of 492 tumors with known smoking status, 87%' in sfull)"""),
    ("""chk('Methods scripts extended',
    'notebooks/nc49_tcga_purity.py' in full
    and 'notebooks/nc49_tcga_luad_smoking.py' in full
    and 'results/nc49_tcga_admix_scores.csv' in full)""",
     """chk('Methods scripts extended (v51: SI)',
    'notebooks/nc49_tcga_purity.py' in sfull
    and 'notebooks/nc49_tcga_luad_smoking.py' in sfull
    and 'results/nc49_tcga_admix_scores.csv' in sfull)"""),
    ("""chk('Intro EGFR dissolved',
    'apparent EGFR association dissolved under purity adjustment' in full)""",
     """chk('Intro EGFR dissolved (v51)',
    'the apparent EGFR association dissolves' in full)"""),
    ("""chk('B=30 MC noise note', 'resolves to 1/31' in full)""",
     """chk('B=30 MC noise note (v51: SI)', 'resolves to 1/31' in sfull)"""),
    ("""chk('tier class-composition note', 'mix class composition with drift tier' in full)""",
     """chk('tier class-composition note (v51: SI)', 'mix class composition with drift tier' in sfull)"""),
    ("""chk('seeded subsampling MC note',
    'Monte-Carlo error of roughly 0.01\\u20130.02 ratio units' in full)""",
     """chk('seeded subsampling MC note (v51: SI)',
    'Monte-Carlo error of roughly 0.01\\u20130.02 ratio units' in sfull)"""),
    ("""chk('Hallmark enrichment sentence (v50)',
    'no enrichment for any MSigDB Hallmark program' in full and 'all q \\u2265 0.24' in full)""",
     """chk('Hallmark enrichment sentence (v51)',
    'no MSigDB Hallmark enrichment' in full and 'all q \\u2265 0.24' in full)"""),
    ("""chk('Hallmark distributed-signal framing (v50: k_f ordering retained)',
    'retained the TT \\u2265 NN k_f ordering in all five cancer types' in full)""",
     """chk('Hallmark distributed-signal framing (v51: k_f ordering retained)',
    'retained the TT \\u2265 NN k_f ordering in all five' in full)"""),
    ("""chk('k_f composition regression sentence',
    'retained the TT \\u2265 NN k_f ordering in all five cancer types' in full)""",
     """chk('k_f composition regression sentence (v51)',
    'retained the TT \\u2265 NN k_f ordering in all five' in full)"""),
    ("""chk('Kang k_f 0/30 parenthetical (v50)',
    'k_f alone likewise 0 of 30' in full)""",
     """chk('Kang k_f 0/30 parenthetical (v51)',
    'k_f likewise 0 of 30' in full)"""),
    ("""chk('marker Jaccard 1.41 (Results)', 'T3 calibration ratio 1.41 versus 1.80' in full)""",
     """chk('marker Jaccard 1.41 (v51: Fig 3 legend)', 'T3 calibration 1.41 versus 1.80' in full)"""),
    ("""chk('Cox limitation sentence (v50)',
    'LIHC Cox hazard ratio per SD 1.07, 95% CI 0.88\\u20131.31' in full)""",
     """chk('Cox limitation sentence (v51)',
    'LIHC Cox HR per SD 1.07, 95% CI 0.88\\u20131.31' in full)"""),
    ("""chk('Result 3b background2 cites Fig. 2e (v50)',
    'AUC(k_f) = 0.859 (Fig. 2e)' in full)""",
     """chk('Result 3b background2 cites Fig. 2e (v51)',
    'AUC(k_f) = 0.859; Fig. 2e' in full)"""),
    ("""chk('cross-organ Table 1 citations (v50)',
    '(Fig. 5; Table 1; Supplementary Fig. 5)' in full
    and 'upper block of Table 1' in full)""",
     """chk('cross-organ Table 1 citations (v51)',
    '(Fig. 5; Table 1; Supplementary Fig. 5)' in full
    and 'n \\u2265 5 pairs; Table 1' in full)"""),
]

SI_EDITS = [
    ("""chk('no 3,596 stray residue (v49.14: single attrition mention)',
    full.count('3,596') == 1 and 'of the 3,596 expression-matrix samples' in full
    and '3,596' not in cellfull)""",
     """chk('no 3,596 stray residue (v51: Note + SuppMethods 5.12)',
    full.count('3,596') == 2 and 'of the 3,596 expression-matrix samples' in full
    and '3,596' not in cellfull)"""),
]

EXIT_OLD = "print(f'TOTAL: {len(checks)} checks, {nfail} failures')"
EXIT_NEW = ("print(f'TOTAL: {len(checks)} checks, {nfail} failures')\n"
            "raise SystemExit(1 if nfail else 0)")

def apply(path, edits, add_exit):
    src = path.read_text(encoding="utf-8")
    ok = True
    for i, (old, new) in enumerate(edits, 1):
        n = src.count(old)
        if n != 1:
            ok = False
            print(f"[BAD] {path.name} edit {i}: matches={n}  {old[:60]!r}")
    if add_exit and src.count(EXIT_OLD) != 1:
        ok = False
        print(f"[BAD] {path.name}: exit-gate anchor matches={src.count(EXIT_OLD)}")
    if not ok:
        raise SystemExit(f"ABORT on {path.name}; nothing written.")
    for old, new in edits:
        src = src.replace(old, new)
    if add_exit:
        src = src.replace(EXIT_OLD, EXIT_NEW)
    path.write_text(src, encoding="utf-8")
    print(f"{path.name}: {len(edits)} edits applied" + (" + exit gate" if add_exit else ""))

apply(MSV, MS_EDITS, True)
apply(SIV, SI_EDITS, True)
apply(CLV, [], True)
print("done")
