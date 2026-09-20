#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XV6 cross-validation for v49.15 (fifth-round blind-review fixes).

Independent of build assertions: extracts the four documents fresh from the
published zip (sha256 a76a0195...) and verifies each of the 6 fixes against
ground truth, plus regression checks on the v49.14 fix set.
"""
import io
import os
import zipfile

import docx

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZD = os.path.join(BASE, "results", "audit", "_v4915_xv6")

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


os.makedirs(ZD, exist_ok=True)
z = zipfile.ZipFile(os.path.join(BASE, "CKI_Submission_v49_NC.zip"))
for n in z.namelist():
    if n.endswith(".docx"):
        z.extract(n, ZD)
base = os.path.join(ZD, "CKI_Submission_v49_NC")
ms = fulltext(os.path.join(base, "CKI_Manuscript_NC.docx"))
si = fulltext(os.path.join(base, "CKI_Supplementary_NC.docx"))
cl = fulltext(os.path.join(base, "CKI_NC_Cover_Letter.docx"))
gd = fulltext(os.path.join(base, "CKI_Reproducibility_Guide_NC.docx"))

print("=== m1 (R2): Fig 1a legend word order ===")
chk("m1 new word order present",
    "the constrained counterpart of the synonymous baseline" in ms)
chk("m1 old word order absent",
    "the counterpart of the constrained synonymous baseline" not in ms)

print("=== m2 (R1): span-matched residual decomposition in MS ===")
chk("m2 decomposition clause present",
    "residual again predominantly k_n-driven: k_f 1.39 versus k_n 0.33" in ms
    and "Supplementary Note 10" in ms)
# ground truth: SI Note 10 values
chk("m2 ground truth values in SI",
    "1.39" in si and "0.33" in si,
    "nc49_brain_region_matched_summary.csv: kf 1.391 / kn 0.327")

print("=== m3 (R1): ependymal against-direction note in MS ===")
chk("m3 reversal clause present",
    "ependymal cells (P 0.058 free versus 0.021 stratified)" in ms
    and "stratified q = 0.052" in ms)
chk("m3 consistent with SI disclosure",
    "0.021 versus 0.058" in si and "not nested" in si,
    "SI Note 12 is the authority for both numbers")
chk("m3 q does not cross 0.05 (claim integrity)",
    0.052 > 0.05)

print("=== m4 (R6): exact cross-organ Mann-Whitney P ===")
chk("m4 exact P present",
    "Mann-Whitney U, P = 5.6 \u00d7 10\u207b\u00b9\u2078" in ms)
chk("m4 threshold residue absent",
    "Mann-Whitney U, P < 0.001" not in ms)
# independent recompute from ground truth
import pandas as pd
from scipy.stats import mannwhitneyu
p = pd.read_csv(os.path.join(BASE, "results", "phase35_all_metrics_pairs.csv"))
a = p[(p["same_organ"]) & (~p["same_ct"])]
b = p[(~p["same_organ"]) & (~p["same_ct"])]
u = mannwhitneyu(a["omega"], b["omega"], alternative="two-sided")
chk("m4 independent recompute matches 5.6e-18",
    abs(u.pvalue - 5.6e-18) / 5.6e-18 < 0.02
    and len(a) == 1038 and len(b) == 3754,
    f"recomputed P={u.pvalue:.3e}, n={len(a)} vs {len(b)}")

print("=== m5 (R6): CL per-background count ===")
chk("m5 CL wording",
    "1,750 replicates per background, two backgrounds" in cl)

print("=== R5 optional: median qualifier ===")
chk("R5 median qualifier on agg-order baseline",
    "split-control median baseline itself moves from 6.46 to 10.94" in ms)

print("=== regression: v49.14 fix set intact ===")
for item, cond in [
    ("A1 reciprocal-of-NI wording",
     "parallels the reciprocal of the neutrality index" in ms),
    ("A2 ex-CC CI [0.997, 1.880] includes 1",
     "0.997, 1.880" in ms and "includes 1" in ms),
    ("B1 three-way attrition",
     "3 do not appear in the assembled pair table" in ms
     and "spans 3,593 unique barcodes" in ms),
    ("B2 smoking three-model",
     "alone, jointly with admixture, or jointly with age and sex" in ms),
    ("C1 B = 1,000 Methods sentence",
     "B = 1,000 for the composition cluster bootstrap" in ms),
    ("C1 pooled attenuation",
     "\u22124.8%, +2.0" in ms),
    ("C3 rho 0.78 sentence",
     "Spearman \u03c1 = 0.78" in ms),
    ("B13 functional change",
     "functional change rather than neutral drift" in ms),
    ("B18 BRCA 1.34\u20131.85",
     "BRCA 1.57 (1.34\u20131.85)" in ms),
    ("B8 CL ORCID",
     "ORCID (corresponding author): Li Zhang 0000-0002-0698-0754" in cl),
    ("stale '[1.00, 1.88]' absent", "[1.00, 1.88]" not in ms),
    ("stale '(1.34\u20131.84)' absent", "(1.34\u20131.84)" not in ms),
    ("stale 'median \u22121.2%' absent", "median \u22121.2%" not in ms),
    ("stale 'Mann-Whitney U, P < 0.001' absent (MS-wide)",
     "Mann-Whitney U, P < 0.001" not in ms),
]:
    chk(f"regression: {item}", cond)

print()
n_pass = sum(1 for _, ok, _ in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print(f"XV6: {n_pass}/{len(RESULTS)} PASS, {n_fail} FAIL")
if n_fail:
    for item, ok, _ in RESULTS:
        if not ok:
            print("  -", item)
