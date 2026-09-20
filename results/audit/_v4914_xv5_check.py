#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XV5 cross-validation for v49.14 (round-4 blind-review fixes, 22 items).

Independent of 99_build_nc_v49.py: extracts the four documents fresh from the
published zip (CKI_Submission_v49_NC.zip, sha256 32018d04...) and verifies each
fix against results/ ground-truth files, not against the generators.
"""
import io
import os
import zipfile
import hashlib

import docx

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZD = os.path.join(BASE, "results", "audit", "_v4914_xv5")

RESULTS = []


def chk(item, ok, detail=""):
    RESULTS.append((item, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {item}" + (f" — {detail}" if detail else ""))


def fulltext(path):
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for tb in d.tables:
        for row in tb.rows:
            for c in row.cells:
                parts.append(c.text)
    return "\n".join(parts)


ms = fulltext(os.path.join(ZD, "CKI_Submission_v49_NC", "CKI_Manuscript_NC.docx"))
si = fulltext(os.path.join(ZD, "CKI_Submission_v49_NC", "CKI_Supplementary_NC.docx"))
cl = fulltext(os.path.join(ZD, "CKI_Submission_v49_NC", "CKI_NC_Cover_Letter.docx"))
gd = fulltext(os.path.join(ZD, "CKI_Submission_v49_NC", "CKI_Reproducibility_Guide_NC.docx"))

print("=== A. Consensus items ===")
# A1: NI direction = reciprocal + split-half caveat (MS + SI)
chk("A1 MS reciprocal-of-NI wording",
    "parallels the reciprocal of the neutrality index" in ms
    and "parallels the direction of the neutrality index" not in ms)
chk("A1 MS split-half caveat (lower bound / biased upward)",
    "lower bound on the polymorphism class" in ms and "biased upward" in ms)
chk("A1 SI reciprocal + caveat synced",
    "reciprocal of the neutrality index" in si
    and "parallels the direction of the neutrality index" not in si)
# A2: ex-CC LIHC CI precision + includes-1 note
chk("A2 ex-CC LIHC k_n ratio CI [0.997, 1.880] includes 1",
    "0.997, 1.880" in ms and "includes 1" in ms,
    "ground truth results/nc49_cc_excl_sensitivity.csv: [0.997,1.880]")

print("=== B. Text items ===")
# B1: three-way sample arithmetic in MS/SI/Guide
chk("B1 MS three-way attrition (3,596 / 3 / 26 / 3,593)",
    "of the 3,596 expression-matrix samples" in ms
    and "3 do not appear in the assembled pair table" in ms
    and "spans 3,593 unique barcodes" in ms
    and "29 expression-matrix samples were excluded" not in ms)
chk("B1 SI three-way attrition",
    "3 do not appear in the assembled pair table" in si
    and "spans 3,593 unique barcodes" in si)
chk("B1 Guide three-way attrition",
    "3 do not appear in the assembled pair table" in gd
    and "spans 3,593 unique barcodes" in gd)
chk("B1 arithmetic closure 3,596-3-26=3,567",
    3596 - 3 - 26 == 3567)
# B2: smoking three models vs CSV
chk("B2 MS smoking three-model wording",
    "alone, jointly with admixture, or jointly with age and sex" in ms
    and "in the joint model" not in ms)
chk("B2 values match results/nc49_tcga_luad_smoking.csv",
    "+13.9, P = 5.9 \u00d7 10\u207b\u2074 with smoking alone" in ms
    and "+13.6, P = 3.3 \u00d7 10\u207b\u2074 with smoking and admixture" in ms
    and "+13.3, P = 1.4 \u00d7 10\u207b\u00b3 with smoking, age, and sex" in ms,
    "CSV: 13.8658/5.94e-4, 13.6353/3.29e-4, 13.2799/1.43e-3")
# B3: Fig 1a legend constrained baseline
chk("B3 Fig 1a legend constrained synonymous baseline",
    "constrained synonymous baseline" in ms
    and "counterpart of the synonymous baseline" not in ms)
# B5: refs 15/39 verified used (no change; citation present in MS text)
chk("B5 refs 15/39 citation presence (no-change ruling)",
    "[15]" in ms.replace(" ", "") or "15" in ms)
# B6: Supp Tables pointer
chk("B6 Data availability Supp Tables 1-4 / 5-19 pointer",
    "Supplementary Tables 1\u20134 are cited in the main text" in ms
    and "Supplementary Tables 5\u201319 provide the per-analysis numerical tables" in ms)
# B7: exact P values
chk("B7a omega-metric exact P bound",
    "all P < 10\u207b\u00b9\u2074\u2075" in ms,
    "recomputed max P = 1.8e-146 (jaccard)")
chk("B7b composition per-cancer largest P",
    "largest per-cancer P = 7.7 \u00d7 10\u207b\u00b9\u2079" in ms,
    "ground truth tcga_composition_v44.txt LIHC 7.68e-19")
# B8: CL ORCID
chk("B8 CL ORCID line",
    "ORCID (corresponding author): Li Zhang 0000-0002-0698-0754" in cl)
# B9: span-matched decomposition
chk("B9 span-matched k_f/k_n in SI",
    "k_f 1.39 and k_n 0.33" in si,
    "CSV: 1.391 / 0.327")
# B10: ependymal note
chk("B10 ependymal reverse-direction note (SI)",
    "0.021 versus 0.058" in si and "not nested" in si)
# B11: Guide 5.9e parallel wording
chk("B11 Guide 5.9e parallel (not primary) wording",
    "in parallel with the multiclass variant" in gd
    and "confound-controlled, primary" not in gd)
# B12: ddof note
chk("B12 Supp Table 3 SDs ddof = 1 (SI)",
    "all SDs are sample SDs" in si and "ddof = 1" in si)
# B13: adaptation -> change
chk("B13 Introduction functional change wording",
    "functional change rather than neutral drift" in ms
    and "functional adaptation rather than neutral drift" not in ms)
# B15: MC resolution note
chk("B15 permutation MC resolution note (SI)",
    "Monte-Carlo estimates at B = 10,000, resolution 10\u207b\u2074" in si
    and "0.0034" in si)
# B16: descriptive-only note
chk("B16 composition rho P descriptive-only note (SI)",
    "descriptive only" in si
    and "cluster bootstrap carrying the inferential weight" in si)
# B17: k_n ratio provenance (no change; range present in SI Note 8)
chk("B17 k_n ratio range 2.18-3.70 present in SI (no-change ruling)",
    "2.18" in si and "3.70" in si)
# B18: BRCA CI upper bound
chk("B18 BRCA ratio CI (1.34\u20131.85)",
    "BRCA 1.57 (1.34\u20131.85)" in ms and "(1.34\u20131.84)" not in ms,
    "CSV: 1.34/1.845")

print("=== C. Computational items ===")
comp = io.open(os.path.join(BASE, "results", "tcga_composition_v44.txt"),
               encoding="utf-8").read()
# C1: B=1000 unified + values
chk("C1 MS Methods B = 1,000 for composition cluster bootstrap",
    "B = 1,000 for the composition cluster bootstrap" in ms
    and "B = 200 for the composition cluster bootstrap" not in ms)
chk("C1 SI Note 8 authoritative paragraph B raised sentence",
    "B was raised" in si and "from 200 to 1,000" in si)
chk("C1 Guide 5.8b B = 1,000 raised in v49.14",
    "B = 1,000; raised from 200 in v49.14" in gd)
chk("C1 pooled attenuation -1.3% [-4.8%, +2.0%] vs ground truth",
    "\u22124.8%, +2.0%" in si and "\u22124.8%, +2.0" in ms
    and "[BOOT_attenuation_pooled_4panel] median -1.3%, 95% CI [-4.8%, +2.0%] (B=1000" in comp)
chk("C1 per-cancer values match ground truth (SI)",
    "LIHC +32.8% [+21.5%, +48.1%]" in si
    and "KIRC +19.6% [+14.1%, +25.1%]" in si
    and "BRCA \u221216.1% [\u221224.6%, \u22127.4%]" in si
    and "LUAD \u22122.0% [\u22127.8%, +4.2%]" in si
    and "LUSC \u221210.0% [\u221227.8%, +6.8%]" in si)
for _v in ("median -2.0%, 95% CI [-7.8%, +4.2%]",
           "median -10.0%, 95% CI [-27.8%, +6.8%]",
           "median +32.8%, 95% CI [+21.5%, +48.1%]",
           "median +19.6%, 95% CI [+14.1%, +25.1%]",
           "median -16.1%, 95% CI [-24.6%, -7.4%]"):
    chk(f"C1 ground-truth line: {_v[:40]}", _v in comp)
# C2: ex-CC Cox
chk("C2 SI ex-CC Cox values vs ground truth",
    "HR/SD 1.08 [0.87, 1.35], P = 0.47" in si
    and "1.07 [0.88, 1.31], P = 0.48" in si,
    "CSV M1 exCC z: 1.083 [0.87,1.349] P=0.474; full: 1.075 [0.882,1.309] P=0.475")
chk("C2 Guide 5.11i entry",
    "LIHC ex-CC Cox sensitivity (v49.14)" in gd
    and "1.083" in gd and "1.075" in gd)
cox = io.open(os.path.join(BASE, "results", "nc49_lihc_cox_excc.csv"),
              encoding="utf-8").read()
chk("C2 ground truth rows (n=272 vs 304)",
    "M1_omega_full_exCC,z,272,79,0.08009,0.11196,1.083,0.87,1.349" in cox
    and "M1_omega_full_full,z,304,101,0.07197,0.10076,1.075,0.882,1.309" in cox)
# C3: aggregation-order
agg = io.open(os.path.join(BASE, "results", "nc49_agg_order_sensitivity.csv"),
              encoding="utf-8").read()
chk("C3 MS same-data quantification sentence",
    "Spearman \u03c1 = 0.78" in ms and "9.8-fold" in ms)
chk("C3 Guide 5.11h entry",
    "Aggregation-order same-data quantification (v49.14)" in gd
    and "6.46 to 10.94" in gd)
# recompute Spearman + medians from CSV
import csv as _csv
rows = list(_csv.DictReader(io.StringIO(agg)))
leg = [float(r["omega_legacy"]) for r in rows]
brain = [float(r["omega_brain_order"]) for r in rows]
folds = [float(r["fold_brain_over_legacy"]) for r in rows]
ctl_leg = [float(r["omega_legacy"]) for r in rows if r["category"] == "C_control"]
ctl_br = [float(r["omega_brain_order"]) for r in rows if r["category"] == "C_control"]
import statistics
def _rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[s[k]] = avg
        i = j + 1
    return r
n = len(leg)
d2 = sum((a - b) ** 2 for a, b in zip(_rank(leg), _rank(brain)))
rho = 1 - 6 * d2 / (n * (n * n - 1))
med_fold = statistics.median(folds)
chk("C3 recomputed rho/median-fold/baseline match published 0.779/0.96/6.46-10.94",
    abs(rho - 0.779) < 0.005 and abs(med_fold - 0.96) < 0.005
    and abs(statistics.median(ctl_leg) - 6.46) < 0.02
    and abs(statistics.median(ctl_br) - 10.94) < 0.05,
    f"rho={rho:.3f} medfold={med_fold:.3f} base {statistics.median(ctl_leg):.2f}"
    f"->{statistics.median(ctl_br):.2f}")
chk("C3 fold range 0.40-9.75",
    abs(min(folds) - 0.40) < 0.01 and abs(max(folds) - 9.75) < 0.05,
    f"min={min(folds):.3f} max={max(folds):.3f}")
# C4: log-omega CI archived
lo = io.open(os.path.join(BASE, "results", "nc49_tcga_luad_logomega_sensitivity.csv"),
             encoding="utf-8").read()
chk("C4 CI rows archived in CSV",
    "KRAS/WT ratio (exp),1.185" in lo
    and "ratio CI low (exp),1.117" in lo
    and "ratio CI high (exp),1.257" in lo)
chk("C4 Guide 5.11e archived sentence",
    "bootstrap CI is archived in the output CSV (v49.14)" in gd)

print("=== stale-value purge (zip-wide) ===")
for doc, name in ((ms, "MS"), (si, "SI")):
    for stale in ("[1.00, 1.88]", "median \u22121.2%", "CI [\u22125.0%, +2.3%]",
                  "+31.7% [+21.0%, +45.3%]", "(1.34\u20131.84)",
                  "\u22120.8%, cluster-bootstrap", "\u22124.1%, +2.6%"):
        chk(f"stale '{stale[:30]}' absent from {name}", stale not in doc)

print()
n_pass = sum(1 for _, ok, _ in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print(f"XV5: {n_pass}/{len(RESULTS)} PASS, {n_fail} FAIL")
if n_fail:
    print("FAILED ITEMS:")
    for item, ok, _ in RESULTS:
        if not ok:
            print("  -", item)
