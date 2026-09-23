#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51: probe ms/sn for each failing assertion phrase (presence + context)."""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
ms = (BASE / "results" / "CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
sn = (BASE / "results" / "CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8")

PHRASES = [
    # (check-id, phrase)
    ("S6-count", "Supplementary Fig. "),           # count via regex separately
    ("A13", "1.3-fold"),
    ("N1", "0.963"),
    ("N6", "90.9"),
    ("N9/N17", "Section 3.12 of the Supplementary Information"),
    ("N15", "tissue-level functional divergence"),
    ("N31", "P = 0.48"),
    ("N25", "2.86"),
    ("N27-old", "fully explained by admixture"),
    ("N27-new", "abolished the apparent EGFR elevation"),
    ("N37a", "(Fig. 5; Table 1; Supplementary Fig. 5)"),
    ("N37b", "upper block of Table 1"),
    ("N38a", "not to discriminate cell-type identity"),
    ("N38b", "housekeeping gene sets may differ across cell types"),
    ("N38c", "expected by design and delineates, rather than limits"),
    ("N38n1", "not cell-type identity"),
    ("N38n2", "the housekeeping anchor is cell-type-specific"),
    ("N38n3", "delineates, rather than limits, its scope"),
    ("N40-old", "concentrate in microglia (16 Strong) and oligodendrocytes (10)"),
    ("N40-new", "Microglial candidates (16 of 39)"),
    ("N47", "descriptive rather than calibrated differences"),
    ("N49-old", "leaving pair-level nominations subject to donor confounding"),
    ("N49-new", "inheriting the atlas\u2019s four-donor structure"),
    ("N50a", "sample-source code (positions 14\u201315)"),
    ("N50b", "assigned to LIHC following a barcode audit"),
    ("N51", "2.5th and 97.5th percentiles of the resampled ratios"),
    ("N56", "seed 20260905"),
    ("N57a", "supersedes the earlier i.i.d. interval"),
    ("N57b", "influence-function (multiplier) sandwich standard error"),
    ("N57c", "Monte Carlo coverage 0.953/0.951 at 6\u20137 clusters"),
    ("N57n1", "superseding the earlier anti-conservative i.i.d. interval"),
    ("N57n2", "influence-function sandwich standard error"),
    ("N58a", "attenuates by only \u22121.3% pooled (95% CI [\u22124.8%, +2.0%]; per-cancer \u221216% to +33%)"),
    ("N58c", "Spearman \u03c1 = 0.364 pooled; 0.20\u20130.51 per cancer type"),
    ("N58b-a", "\u22121.3% pooled, 95% CI \u22124.8% to +2.0%"),
    ("N58b-b", "median |Delta z| 1.31-fold higher"),
    ("N58b-b2", "median |\u0394z| 1.31-fold higher"),
    ("N60a", "attenuates it to 1.74 (95% CI [1.64, 1.84])"),
    ("N60b", "co-report 6.10-fold (full-data) and 1.74-fold (size-balanced)"),
    ("N62a", "Fourth, excluding the 32 cell-line-derived LIHC samples"),
    ("N62b", "NN/TT 1.11, 95% CI [0.93, 1.30]"),
    ("N62c", "Four controls bound the interpretation"),
    ("N62n", "excluding the 32 cell-line-derived LIHC samples leaves the LIHC null unchanged"),
    ("N67a", "span-matched control restricted to the 21 intra-cerebellar region pairs defining Bergmann glia yields 3.68"),
    ("N67b", "paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]"),
    ("N68a", "k_f ratio is 2.09 under equal-n (full-data 2.03)"),
    ("N68b", "equal-n 1.29, astrocyte higher; full-data 0.31, Bergmann glia higher"),
    ("N68c", "95% CI [2.02, 2.18]"),
    ("N68d", "96_brain_downsample_decomp_v49.py"),
    ("N68n1", "k_f ratio 2.09 equal-n, 2.03 full-data"),
    ("N68n2", "equal-n 1.29, astrocyte higher; full-data 0.31"),
    ("N69a", "leave-one-population-out baseline range 6.75\u20138.08"),
    ("N69b", "removing hepatocyte lowers it to 6.75"),
    ("N69n", "leave-one-population-out range 6.75\u20138.08"),
    ("N70a", "whole-tumor label-permutation tests confirmed all three contrasts"),
    ("N70b", "93_luad_group_permutation_v49.py"),
    ("N78a", "Section 1.4 of the Supplementary Information"),
    ("N78b", "never as evidence of positive selection"),
    ("N81a", "3 do not appear in the assembled pair table"),
    ("N81b", "26 further samples appear only in tumor\u2013normal pairs"),
    ("N81c", "spans 3,593 unique barcodes"),
    ("N82a", "alone or jointly with admixture, age, and sex"),
    ("N82b", "\u0394\u03c9 +13.3, P = 1.4 \u00d7 10\u207b\u00b3"),
    ("N86a", "cluster-bootstrap intervals (B = 1,000), the tumor-pair coefficient"),
    ("N86b", "B = 1,000 for the composition cluster bootstrap"),
    ("N86c", "B was raised from 200 to 1,000"),
    ("N87a", "LIHC +32.8% [+21.5%, +48.1%], KIRC +19.6% [+14.1%, +25.1%], BRCA \u221216.1% [\u221224.6%, \u22127.4%], LUAD \u22122.0% [\u22127.8%, +4.2%], LUSC \u221210.0% [\u221227.8%, +6.8%]"),
    ("N87b", "\u221216% to +33%"),
    ("N88a", "rank ordering is largely preserved (Spearman \u03c1 = 0.78)"),
    ("N88b", "control-category median baseline itself moves from 6.46 to 10.94"),
    ("N100a", "residual again k_n-driven: k_f 1.39 versus k_n 0.33"),
    ("N100b", "Supplementary Note 10"),
    ("N101a", "ependymal cells (P 0.058 free versus 0.021 stratified)"),
    ("N101b", "stratified q = 0.052"),
    ("N101n", "ependymal cells\u2014the one class moving against the conservative direction\u2014still do not survive (stratified q = 0.052)"),
    ("N102a", "Mann-Whitney U, P = 5.6 \u00d7 10\u207b\u00b9\u2078"),
    ("N102n", "Mann-Whitney P = 5.6 \u00d7 10\u207b\u00b9\u2078"),
    ("N104", "split-control median baseline itself moves from 6.46 to 10.94"),
    ("N53a", "Section 1.4 of the Supplementary Information"),
    ("N53b", "synonymous-site divergence (Ks)"),
    ("N53c", "polymorphism class"),
    ("N53d", "reciprocal of the neutrality index"),
    # extra probes for context
    ("X-bias", "ratio bias"),
    ("X-131", "1.31-fold"),
    ("X-atten", "attenuat"),
]

import re
print(f"{'id':10s} {'ms':>3s} {'sn':>3s}  phrase")
for cid, ph in PHRASES:
    m = ms.count(ph)
    s = sn.count(ph)
    print(f"{cid:10s} {m:3d} {s:3d}  {ph[:70]}")

print()
n_sfig = len(re.findall(r"Supplementary Fig\. \d+", sn))
print(f"S6 sn Supplementary Fig. refs = {n_sfig}")
print(f"N9/N17 ms count = {ms.count('Section 3.12 of the Supplementary Information')}")

# context snippets for missing-in-ms items
def ctx(text, key, w=130):
    i = text.find(key)
    if i < 0:
        return None
    return text[max(0, i - w): i + len(key) + w].replace("\n", " ")

print("\n--- contexts (ms) ---")
for key in ["1.3-fold", "ratio bias", "0.963", "90.9", "tissue-level functional",
            "P = 0.48", "2.86", "abolished the apparent EGFR",
            "Microglial candidates", "inheriting the atlas",
            "superseding the earlier", "excluding the 32 cell-line",
            "k_f ratio 2.09", "leave-one-population-out", "label-permutation",
            "Section 1.4", "admixture, age, and sex", "B = 1,000",
            "Spearman \u03c1 = 0.78", "6.46 to 10.94", "ependymal",
            "Mann-Whitney", "residual again", "never as evidence"]:
    c = ctx(ms, key)
    print(f"[ms] {key!r}: {c if c else 'ABSENT'}")

print("\n--- contexts (sn) for flip candidates ---")
for key in ["0.963", "90.9", "2.86", "sample-source code", "percentiles of the resampled",
            "20260905", "\u22121.3% pooled", "1.31-fold", "0.364", "3,593 unique barcodes",
            "+13.3", "Spearman \u03c1 = 0.78", "6.46 to 10.94", "\u221216% to +33%",
            "NN/TT 1.11", "4.30, bootstrap", "B was raised"]:
    c = ctx(sn, key)
    print(f"[sn] {key!r}: {c if c else 'ABSENT'}")
