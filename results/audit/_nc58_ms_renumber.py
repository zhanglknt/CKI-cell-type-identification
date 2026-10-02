#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc58: Figure 3 legend rewrite + supplementary legends reorder + global SF renumber.

Final monotonic mapping (old -> new) by first-citation order:
  1->1, 2->2, 14->3, 3->4, 4->5, 5->6, 6->7, 7->8, 8->9, 9->10, 10->11,
  11->12, 13->13, 12->14
Applies to: generate_manuscript_nc.py (body + legends block),
            notebooks/68_gen_supplementary_nc.py (whole),
            notebooks/100_gen_reproducibility_nc.js (whole, renumber only).
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
MS = BASE + r"\generate_manuscript_nc.py"
SI = BASE + r"\notebooks\68_gen_supplementary_nc.py"
JS = BASE + r"\notebooks\100_gen_reproducibility_nc.js"

OLD2NEW = {1: 1, 2: 2, 14: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10,
           10: 11, 11: 12, 13: 13, 12: 14}

FIG3_LEGEND = (
    "p('Figure 3. Real-data neutral-drift calibration on technical replicates. "
    "(a) Replication in the Kang IFN-\\u03b2 PBMC batch-1 technical replicates "
    "(30 same-donor, same-condition cross-lane pairs, n-matched null with B = 200 "
    "per pair): \\u03c9 FPR = 0 of 30 with calibration median 0.96, versus 36.7% "
    "for raw JS and 23.3% for cosine. \\u03c9 lowers drift misreporting to the "
    "minimum among compared metrics while retaining sensitivity to genuine "
    "biological divergence\\u2014a relative-calibration advantage, not absolute "
    "immunity (see Results). (b) Brain calibration distributions (observed / own "
    "n-matched null median; log scale) for seven metrics across the three-tier "
    "drift ladder (T1: two 10x libraries of the same donor, region, and cell "
    "type, 2,161 pairs, pure technical drift; T2: crosses donors within a "
    "region, 1,089 pairs; T3: crosses regions within a donor, 1,656 pairs, "
    "regional biology as positive control; each pair read against its own "
    "n-matched null). Boxes show median and IQR (whiskers not shown; extreme "
    "tails clipped at the 2nd\\u201398th percentiles for display). \\u03c9 "
    "(leftmost metric) stays near 1 at T1 and shows the shallowest gradient to "
    "T3, whereas raw JS, cosine, Spearman, and k_f rise several-fold. (c) "
    "False-positive rates on T1 (technical drift, dark) and T2 (donor drift, "
    "light): fraction of pairs whose observed value exceeds its own null 95th "
    "percentile, with Wilson 95% CIs; the dotted line marks the nominal 5% "
    "level. \\u03c9 misreports least among the continuous divergence metrics at "
    "both tiers (T1: 28.6% versus 35.7\\u201345.2% for the others); marker "
    "Jaccard is lower still on the false-positive statistic (T1 19.9%, T2 "
    "74.7%) but responds weakest to real regional divergence (T3 calibration "
    "1.41 versus 1.80 for \\u03c9 and 2.98 for raw JS; panel b) and offers no "
    "k_n/k_f decomposition.')"
)

# New SF3 (microglia) legend: 2-panel with UMAP (a) + omega separation (b);
# [12] legend clarification: both values are omega.
MICRO_LEGEND = (
    "p('Supplementary Fig. 3. Human-brain sanity check on the microglia "
    "supercluster (Supplementary Note 16). (a) UMAP embedding of the CELLxGENE "
    "Microglia supercluster (Human Brain Cell Atlas v1.0; 91,838 nuclei), "
    "coloured by cell type: microglial cell (88,494 nuclei) versus CNS "
    "macrophage (3,344). (b) CKI \\u03c9 for the functional contrast (35 "
    "sample-matched microglia-versus-CNS-M\\u03c6 pairs) versus neutral "
    "half-splits (40 pairs): \\u03c9 = 21.83 \\u00b1 7.20 (functional) versus "
    "\\u03c9 = 1.30 \\u00b1 0.36 (neutral); Mann-Whitney P = 5.5 \\u00d7 "
    "10\\u207b\\u00b9\\u2074; exact rank AUC = 1.00. The margin is carried by "
    "k_f (AUC = 1.00), whereas k_n is only partially elevated (AUC = 0.89); "
    "standard metrics also separate the classes (raw JS, cosine, marker "
    "Jaccard AUC = 1.00; Spearman 0.90). This analysis uses the global-HVG "
    "scheme, not the per-pair top-200 hybrid scheme, so absolute \\u03c9 "
    "values sit on a different scale from the 7.70-calibrated hybrid baseline "
    "and are compared internally only.')"
)


def renumber_text(text):
    """Two-pass placeholder renumber of 'Supplementary Fig. N' (singular)."""
    def p1(m):
        old = int(m.group(1))
        return f"Supplementary Fig. @@{OLD2NEW[old]}@@"
    out = re.sub(r"Supplementary Fig\. (\d+)(?=[^\d])", p1, text)
    return out.replace("@@", "")


def main():
    # ---------- MS generator ----------
    src = open(MS, encoding="utf-8").read()
    lines = src.split("\n")

    # 1) Figure 3 legend line
    n_fig3 = 0
    for i, ln in enumerate(lines):
        if ln.startswith("p('Figure 3. Real-data neutral-drift calibration"):
            lines[i] = FIG3_LEGEND
            n_fig3 += 1
    assert n_fig3 == 1, f"Figure 3 legend line not found uniquely: {n_fig3}"

    # 2) locate supplementary legends block (marker comment .. last SF legend)
    marker = next(i for i, ln in enumerate(lines)
                  if ln.startswith("# Supplementary figure legends"))
    leg_idx = {}
    for i in range(marker, len(lines)):
        m = re.match(r"p\('Supplementary Fig\. (\d+)\. ", lines[i])
        if m:
            leg_idx[int(m.group(1))] = i
    assert len(leg_idx) == 14, f"expected 14 supp legends, got {len(leg_idx)}"
    first_leg = min(leg_idx.values())
    last_leg = max(leg_idx.values())

    # 3) renumber everything OUTSIDE the legends block
    for i, ln in enumerate(lines):
        if first_leg <= i <= last_leg and re.match(
                r"p\('Supplementary Fig\. \d+\. ", ln):
            continue
        lines[i] = renumber_text(ln)

    # 4) rebuild legends block in final order with new labels
    new_block = []
    for old in sorted(OLD2NEW, key=lambda o: OLD2NEW[o]):
        new = OLD2NEW[old]
        ln = lines[leg_idx[old]]
        if old == 14:
            new_block.append(MICRO_LEGEND)
            continue
        ln = re.sub(r"^p\('Supplementary Fig\. \d+\. ",
                    f"p('Supplementary Fig. {new}. ", ln)
        new_block.append(ln)
    lines[first_leg:last_leg + 1] = new_block

    open(MS, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print(f"MS: Figure3 legend rewritten; legends reordered; body renumbered.")

    # ---------- SI generator ----------
    si = open(SI, encoding="utf-8").read()
    si = renumber_text(si)
    open(SI, "w", encoding="utf-8", newline="\n").write(si)
    print("SI: renumbered.")

    # ---------- Repro guide (renumber only; microglia text fixed separately) --
    js = open(JS, encoding="utf-8").read()
    js = renumber_text(js)
    open(JS, "w", encoding="utf-8", newline="\n").write(js)
    print("Guide: renumbered.")

    # ---------- verify ----------
    ms2 = open(MS, encoding="utf-8").read()
    body = ms2.split("# Supplementary figure legends")[0]
    order = [int(m.group(1)) for m in
             re.finditer(r"Supplementary Fig\. (\d+)(?=[^\d])", body)]
    seen = []
    for n in order:
        if n not in seen:
            seen.append(n)
    print("MS body first-citation order:", seen)
    assert seen == list(range(1, 15)), f"NOT monotonic: {seen}"
    print("MS body first-citation order MONOTONIC 1..14 OK")

    leg_sec = ms2.split("# Supplementary figure legends")[1]
    labels = [int(m.group(1)) for m in
              re.finditer(r"p\('Supplementary Fig\. (\d+)\. ", leg_sec)]
    print("Legends block order:", labels)
    assert labels == list(range(1, 15)), f"legends not sequential: {labels}"
    print("Legends block 1..14 sequential OK")


if __name__ == "__main__":
    main()
