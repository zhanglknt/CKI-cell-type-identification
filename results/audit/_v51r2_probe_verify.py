#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51r2: probe current ms/sfull for the 39 failing ms_verify + 1 si_verify checks."""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
full = (BASE / "results" / "CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
sfull = (BASE / "results" / "CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8")

P = [
    # 1 Results Section 3.12 ref
    ("1a", "relative-calibration advantage"),
    ("1b", "(Section 3.12)"),
    # 2 Methods Section 3.12 ref
    ("2", "full audit of design, diagnostics"),
    # 3 count
    ("3", "Section 3.12"),
    # 4 MWU/label-permutation
    ("4a", "label-permutation confirmed; Section 3.13"),
    ("4b", "per-tumor Mann-Whitney"),
    # 5 T1 qualified
    ("5", "misreported least among the continuous divergence metrics"),
    # 6 Jaccard 19.9
    ("6a", "19.9%"),
    ("6b", "T1 FPR 19.9%"),
    # 7 Jaccard weakest
    ("7", "weakest to real regional divergence"),
    # 8 3,596
    ("8a", "3,596"),
    ("8b", "of the 3,596 expression-matrix samples"),
    # 9 per-cancer counts
    ("9a", "LUAD 493 tumor + 76"),
    ("9b", "LUAD: 493 tumor + 76 normal"),
    ("9c", "LUSC: 534 tumor + 58 normal"),
    ("9d", "BRCA: 1010 tumor + 109 normal"),
    # 10 attrition
    ("10a", "3 do not appear in the assembled pair table"),
    ("10b", "spans 3,593 unique barcodes"),
    # 11 k_n mechanism
    ("11", "TT k_n exceeded NN k_n by 1.3\u20133.3-fold in every cancer type"),
    # 12 Dunn/label-perm
    ("12a", "Dunn\u2013Holm P \u2264 0.008 for both KRAS contrasts"),
    # 13 LIHC mapping
    ("13", "LIHC mapping-sensitive: 1.10 versus 1.31 softmax"),
    # 14 softmax demoted
    ("14a", "recomputed under the authoritative linear probability mapping"),
    ("14b", "softmax-caliber values are archived here as a sensitivity analysis"),
    # 15 smoking
    ("15a", "alone or jointly with admixture, age, and sex"),
    ("15b", "+13.3"),
    ("15c", "+13.6"),
    ("15d", "+13.9"),
    # 16 purity proxy
    ("16", "monotonically equivalent to published ESTIMATE purity"),
    ("16b", "ESTIMATE"),
    # 17 pack-years
    ("17", "pack-years"),
    # 18 batch/center
    ("18", "differ in source site and batch"),
    # 19 GTEx
    ("19a", "Adjacent non-tumor is not healthy tissue"),
    ("19b", "external healthy reference"),
    # 20 epidemiology
    ("20", "left the contrast essentially unchanged"),
    # 21 k_n admix correlation
    ("21", "\u22120.23 to \u22120.42"),
    # 22 high-purity LUAD
    ("22", "LUAD 2.46 \u2192 2.86"),
    # 23 high-purity half
    ("23a", "high-purity-half comparisons increased the TT k_n elevation in all five"),
    ("23b", "high-purity-half 1.17 versus 1.19 excluding CC"),
    # 24 reversal admixture
    ("24", "admixture can only weaken, not create"),
    # 25 ESTIMATE block
    ("25a", "141 stromal and 141 immune genes"),
    ("25b", "45,504 expressed genes"),
    # 26 cBioPortal smoking block
    ("26a", "luad_tcga"),
    ("26b", "smoking status available for 508"),
    ("26c", "427 of 492 tumors"),
    # 27 scripts
    ("27a", "nc49_tcga_purity.py"),
    ("27b", "nc49_tcga_luad_smoking.py"),
    ("27c", "nc49_tcga_admix_scores.csv"),
    # 28 Intro EGFR
    ("28", "the apparent EGFR association dissolves"),
    # 29 B=30
    ("29", "resolves to 1/31"),
    # 30 tier class-composition
    ("30", "mix class composition with drift tier"),
    # 31 seeded subsampling
    ("31", "Monte-Carlo error of roughly 0.01\u20130.02 ratio units"),
    # 32 Hallmark
    ("32a", "no MSigDB Hallmark enrichment"),
    ("32b", "all q \u2265 0.24"),
    # 33/34 k_f ordering
    ("33", "retained the TT \u2265 NN k_f ordering in all five"),
    # 35 Kang k_f
    ("35", "k_f likewise 0 of 30"),
    # 36 Jaccard 1.41
    ("36", "T3 calibration 1.41 versus 1.80"),
    # 37 Cox
    ("37", "LIHC Cox HR per SD 1.07, 95% CI 0.88\u20131.31"),
    # 38 background2
    ("38", "AUC(k_f) = 0.859; Fig. 2e"),
    # 39 Table 1
    ("39a", "(Fig. 5; Table 1; Supplementary Fig. 5)"),
    ("39b", "n \u2265 5 pairs; Table 1"),
]

print(f"{'id':5s} {'ms':>3s} {'sn':>3s}  phrase")
for cid, ph in P:
    print(f"{cid:5s} {full.count(ph):3d} {sfull.count(ph):3d}  {ph[:65]}")
