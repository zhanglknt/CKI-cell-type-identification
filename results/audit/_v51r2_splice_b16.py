#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51r2 batch-16: strict NC compliance — MAIN 5,304 -> ~4,950 (<=5,000).

Rules: numbers/CI/P verbatim or SI-carried (all probed); no [N] citation
group removed (73-group invariant); build-asserted phrases preserved.
All-or-nothing: every OLD must match exactly once before writing.
"""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
TARGET = BASE / "generate_manuscript_nc.py"

EDITS = [
    # ---------------- INTRODUCTION ----------------
    # I1 L456: scope sentence tail compressed
    (r'''(TCGA and IFN-\u03b2 below; Supplementary Note 1), inflating the denominator and deflating the ratio; in such regimes \u03c9 must be read alongside its components, and k_f with a design-matched null is the honest default for ordering claims (Results; Discussion).''',
     r'''(TCGA and IFN-\u03b2 below; Supplementary Note 1), so \u03c9 must be read alongside its components (Results; Discussion).'''),
    # I2 L458: roadmap fourth item compressed
    (r'''and resolves lung-adenocarcinoma driver classes: KRAS-mutant tumors retain both functional (k_f) and baseline (k_n) divergence after purity and smoking adjustment, while the apparent EGFR association dissolves.''',
     r'''and resolves lung-adenocarcinoma driver classes (KRAS robust to purity and smoking adjustment; the apparent EGFR association dissolves).'''),

    # ---------------- RESULTS ----------------
    # R3 L483
    (r'''No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence.''',
     r'''No control comparison reached significance (all P > 0.05): biologically equivalent populations are recognized as undiverged.'''),
    # R4 L485
    (r'''with cross-organ cross-type comparisons highest (2\u20134 pairs per category, calibration-scale estimates). Component analysis confirmed k_f as the driver: from controls''',
     r'''with cross-organ cross-type comparisons highest (2\u20134 pairs per category). k_f drives this: from controls'''),
    # R5 L487 (CIs 9.03/10.53, 7.39/8.00 carried in SI Notes 2-4)
    (r'''(brain atlas 9.73 [9.03, 10.53]; Tabula Sapiens 7.67 [7.39, 8.00], inside the mouse CI)''',
     r'''(brain atlas 9.73; Tabula Sapiens 7.67, inside the mouse CI)'''),
    # R6 L500
    (r'''We computed CKI \u03c9 and four standard metrics (raw JS divergence, Spearman distance, cosine distance, marker Jaccard distance) on all {_h["n_pairs_total"]:,} human cell-type pairs. \u03c9 correlated negatively with all four (Spearman r = ''',
     r'''On all {_h["n_pairs_total"]:,} human pairs, \u03c9 correlated negatively with all four standard metrics (raw JS, Spearman, cosine, marker Jaccard; Spearman r = '''),
    # R7 L507a
    (r'''so we built a semi-synthetic ground truth by injecting perturbations into a real background (Tabula Muris FACS marrow B cells; true pre-injection divergence zero; Methods).''',
     r'''so we injected perturbations into a real background (Tabula Muris FACS marrow B cells; pre-injection divergence zero; Methods).'''),
    # R39 L507b (0.025 + 2% overdispersion carried in SI Note 1)
    (r'''\u03c9 in none (2% under global overdispersion); an injected functional module was detected only when strong (0 of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2), per-pair top-200 selection saturating with noise under the null (median baseline k_f = 0.025).''',
     r'''\u03c9 in none; an injected functional module was detected only when strong (0 of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2).'''),
    # R45 L507c
    (r'''(Supplementary Notes 1, 5)\u2014the ratio cancels global compositional drift wherever it acts.''',
     r'''(Supplementary Notes 1, 5).'''),
    # R31 L509
    (r'''(fourfold cell-count imbalance: \u03c9 \u221232%, k_f +67%, cosine +108%), and is thus a specificity-first screen, rejecting neutral drift at the cost of bounded power''',
     r'''(fourfold cell-count imbalance: \u03c9 \u221232%, k_f +67%, cosine +108%)\u2014a specificity-first screen rejecting neutral drift at the cost of bounded power'''),
    # R8 L515
    (r'''We tested the same specificity on real technical replicates, calibrated against per-pair size-matched cell-shuffle nulls (B = 200; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14], the 30 same-donor, same-condition cross-lane pairs serve as clean technical replicates:''',
     r'''We tested the same specificity on real technical replicates (per-pair size-matched cell-shuffle nulls, B = 200; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14], the 30 same-donor, same-condition cross-lane pairs are clean technical replicates:'''),
    # R9 L516
    (r'''and across the ladder its calibration gradient is the shallowest (T3 ratio 1.80 versus 2.98 raw JS; full per-tier values in Section 3.12).''',
     r'''and its calibration gradient is the shallowest across the ladder (T3 ratio 1.80 versus 2.98 raw JS; Section 3.12).'''),
    # R10 L517
    (r'''(14.1% below 30 nuclei per library to 48.0% above 500; raw JS 28.6% to 72.5%), a library-level technical component the anchor absorbs only partially\u2014the 0-of-30 Kang outcome sits at the favorable end of this size dependence.''',
     r'''(14.1% below 30 nuclei per library to 48.0% above 500; raw JS 28.6% to 72.5%)\u2014a library-level technical component the anchor absorbs only partially, so the 0-of-30 Kang outcome sits at the favorable end of this size dependence.'''),
    # R51 L519
    (r'''An independent validation on unused data reinforces this calibration:''',
     r'''An independent validation on unused data reinforces this:'''),
    # R12 L523
    (r'''stimulation [14] (24,413 cells, six cell types; Methods)\u2014condition is fully confounded with lane, so we read this as a relative architecture demonstration.''',
     r'''stimulation [14] (24,413 cells, six cell types; Methods), condition fully confounded with lane\u2014we read this as a relative architecture demonstration.'''),
    # R13 L527a
    (r'''and scDist (Python approximation of the R-only package) on the Kang IFN-\u03b2 dataset [14].''',
     r'''and scDist (Python approximation) on the Kang IFN-\u03b2 dataset [14].'''),
    # R13b L527b
    (r'''where the anchor responds (k_n AUC = 1.000) and the ratio is annihilated by its denominator; users seeking''',
     r'''where the anchor responds (k_n AUC = 1.000) and annihilates the ratio; users seeking'''),
    # R14 L531a (6.4e-13 verbatim in SI Note 7)
    (r'''The reference implementation first reproduced the reported landscape exactly (maximum per-pair |\u0394\u03c9| = 6.4 \u00d7 10\u207b\u00b9\u00b3 over 31,764 pairs). Non-circular panels''',
     r'''Non-circular panels'''),
    # R14b L531b
    (r'''but the tier cutoffs (\u03c9 < 15/25/35) are calibrated to the reported scheme\u2019s inflated scale and do not transfer (Supplementary Note 7).''',
     r'''but the tier cutoffs (\u03c9 < 15/25/35) do not transfer (Supplementary Note 7).'''),
    # R15 L538
    (r'''At bulk resolution, averaging over tumor, stromal, and immune compartments, \u03c9 quantifies divergence between tissue states;''',
     r'''At bulk resolution, \u03c9 quantifies divergence between tissue states;'''),
    # R36 L540
    (r'''(61 EGFR-mutant, 120 KRAS-mutant, 311 wild-type) on per-tumor \u03c9 (Fig. 4b), KRAS-mutant''',
     r'''(61 EGFR-mutant, 120 KRAS-mutant, 311 wild-type; Fig. 4b), KRAS-mutant'''),
    # R17 L542
    (r'''All TCGA statistics were recomputed under a linear probability mapping (the authoritative caliber), with key results preserved (LIHC effect size mapping-sensitive: 1.10 versus 1.31 softmax; Section 1.7).''',
     r'''All TCGA statistics were recomputed under the authoritative linear probability mapping, with key results preserved (LIHC mapping-sensitive: 1.10 versus 1.31 softmax; Section 1.7).'''),
    # R42 L547
    (r'''are same-cell-type cross-organ comparisons, asking which types maintain identity regardless of residence (Fig. 5; Table 1; Supplementary Fig. 5).''',
     r'''are same-cell-type cross-organ comparisons (Fig. 5; Table 1; Supplementary Fig. 5).'''),
    # R18 L547b
    (r'''though both rest on n = 3 pairs\u2014sparsely sampled types (n = 1\u20133) carry no reliable signal.''',
     r'''though both rest on n = 3 pairs; sparsely sampled types carry no reliable signal.'''),
    # R22a L560
    (r'''First, restricting to same-donor region pairs preserved the extremes and a 4.50-fold gradient, so donor identity cannot explain it away (Supplementary Note 12).''',
     r'''First, restricting to same-donor region pairs preserved the extremes and a 4.50-fold gradient (Supplementary Note 12).'''),
    # R22b L560b
    (r'''and under a k_f-only ordering astrocytes rank third of ten\u2014the gradient chiefly reflects housekeeping stability across regions, not functional-gene divergence.''',
     r'''and under a k_f-only ordering astrocytes rank third of ten.'''),
    # R23a L560c (enumeration Four -> Three)
    (r'''Four analyses probe the gradient\u2019s robustness.''',
     r'''Three analyses probe the gradient\u2019s robustness.'''),
    # R23b L562 (group-size threshold sweep carried in SI Note 10)
    (r''' Fourth, the gradient is robust to the group-size threshold in direction but not magnitude.''',
     r''''''), 
    # R25a L566
    (r'''The gradient suggests a residence/migration framework (recent migrants should show low inter-regional \u03c9; residents accumulate regional signatures), but the data provide no support: OPCs''',
     r'''A residence/migration framework (recent migrants should show low inter-regional \u03c9; residents accumulate regional signatures) finds no support: OPCs'''),
    # R25b L566b
    (r'''and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92); the framework remains hypothesis generation.''',
     r'''and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92).'''),
    # R26 L570
    (r'''Globally, under a design-matched null that recomputes the full selection rule on every block-shuffle permutation, the expected number of Strong candidates is 148.3 across the 31,764-pair pool''',
     r'''Under a design-matched null recomputing the full selection rule on every block-shuffle permutation, the expected Strong-candidate count is 148.3 across the 31,764-pair pool'''),
    # R27 L572
    (r'''a residual (observed/expected) well below 1 marks a cell type far less differentiated between two regions''',
     r'''a residual (observed/expected) below 1 marks a cell type less differentiated between two regions'''),
    # R28 L576
    (r'''libraries of every region were split into pseudo-regions and the identical test re-run on 127,756 pseudo-pairs (Supplementary Note 12; Supplementary Fig. 10)\u2014cross-region pseudo-pairs gave near-nominal tail rates, same-region halves a 37.6% lower-tail rate.''',
     r'''splitting libraries of every region into pseudo-regions and re-running the identical test on 127,756 pseudo-pairs (Supplementary Note 12; Supplementary Fig. 10) gave near-nominal cross-region tail rates but a 37.6% lower-tail rate for same-region halves.'''),
    # R34 L578
    (r'''(five pairs involve the lateral geniculate nucleus; Supplementary Note 11)''',
     r'''(five involve the lateral geniculate nucleus; Supplementary Note 11)'''),
    # R29 L584
    (r'''The block-shuffle re-analysis thus tempers the brain catalogue: an earlier per-pair label-shuffle implementation was anti-conservative (36.3% of P-values at the floor) by ignoring the 10x-library block structure, and we position the entire candidate list as hypothesis-generating.''',
     r'''An earlier per-pair label-shuffle implementation was anti-conservative (36.3% of P-values at the floor) by ignoring the 10x-library block structure; the entire candidate list is therefore hypothesis-generating.'''),
    # R35 L502
    (r'''lower k_n (P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable housekeeping baseline within organs, not greater functional specialization''',
     r'''lower k_n (P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable within-organ housekeeping baseline, not greater functional specialization'''),
    # R67 L481
    (r'''with housekeeping genes from HRT Atlas v1.0 [13] (mouse ortholog column): top-{_ds["n_hvg"]:,} HVGs for the full pairwise matrix (703 pairs, Supplementary Fig. 1), and the hybrid per-pair scheme for the pilot calibration (Fig. 2).''',
     r'''with housekeeping genes from HRT Atlas v1.0 [13] (mouse column): top-{_ds["n_hvg"]:,} HVGs for the full pairwise matrix (703 pairs, Supplementary Fig. 1), and the hybrid per-pair scheme for the pilot (Fig. 2).'''),
    # R52 L554
    (r'''(neurons excluded: supercluster_term does not resolve neuronal subtypes)''',
     r'''(supercluster_term does not resolve neuronal subtypes)'''),

    # ---------------- DISCUSSION ----------------
    # D13 L592a
    (r'''unlike Ka/Ks\u2014where a shared mutation rate cancels mathematically\u2014CKI uses empirically defined HK genes as baseline, lacking comparable mechanistic cancellation, so CKI is a heuristic index rather than a formal measure of selection.''',
     r'''unlike Ka/Ks, where a shared mutation rate cancels mathematically, CKI lacks comparable mechanistic cancellation and is a heuristic index rather than a formal measure of selection.'''),
    # D1 L592b
    (r'''so \u03c9_cal = \u03c9 / 7.70 is the operational scale, interpreted against the empirical equivalent-population distribution rather than fixed cut-offs.''',
     r'''so \u03c9_cal = \u03c9 / 7.70 is the operational scale (Results).'''),
    # D2 L594
    (r'''Classifying cell types from transcriptomic data is largely solved;''',
     r'''Classifying cell types is largely solved;'''),
    # D11 L596
    (r'''HK genes are empirically defined rather than mechanistically neutral, and the HK anchor is itself the most strongly constrained expression class, so \u03c9 should be read as functional divergence''',
     r'''HK genes are empirically defined, not mechanistically neutral, and are themselves the most constrained expression class, so \u03c9 reads as functional divergence'''),
    # D12 L600 (0.442/0.564 preserved)
    (r'''CKI is also not redundant with Augur [37], which prioritizes cell types by condition predictability: rankings are moderately concordant (Augur separability versus class-mean \u03c9 \u03c1 = 0.442; versus k_f \u03c1 = 0.564) with overlapping extremes, at n = 10 classes descriptive only (Supplementary Note 14).''',
     r'''CKI is also not redundant with Augur [37] (condition-predictability prioritization): rankings are moderately concordant (\u03c1 = 0.442 versus class-mean \u03c9; 0.564 versus k_f) with overlapping extremes, descriptive only at n = 10 classes (Supplementary Note 14).'''),
    # D4a L602a
    (r'''at bulk resolution the apparent convergence could reflect cell-composition shifts, peritumoral inflammation, or RNA-quality differences rather than genuine transcriptional convergence, and the reversal''',
     r'''at bulk resolution the apparent convergence could reflect cell-composition shifts, peritumoral inflammation, or RNA-quality differences, and the reversal'''),
    # D4b L602b
    (r'''Tumor and adjacent non-tumor aliquots differ systematically in source site and batch, and adjacent non-tumor is not healthy tissue; separating''',
     r'''Adjacent non-tumor is not healthy tissue and aliquots differ in source site and batch; separating'''),
    # D5a L604a
    (r'''show CKI measuring functional differentiation at multiple spatial scales, with one qualification: the brain regional gradient is a composite signal dominated by the k_n denominator''',
     r'''show CKI measuring functional differentiation at multiple spatial scales, though the brain regional gradient is dominated by the k_n denominator'''),
    # D5b L604b
    (r'''\u2014statistical claims at atlas scale require nulls respecting the experimental design, and the absence of FDR-significant signals is itself informative, delimiting what adult transcriptomes alone can support.''',
     r'''\u2014statistical claims at atlas scale require nulls respecting the experimental design; the absence of FDR-significant signals is itself informative.'''),
    # D6a L606a
    (r'''Although no individual candidate survives FDR correction, several signals are consistent with prior reports\u2014literature anchoring rather than independent validation.''',
     r'''Several signals are consistent with prior reports\u2014literature anchoring, not independent validation.'''),
    # D6b L606b
    (r'''concentrates on an axis rather than scattering across the 108 regions (two null references in Supplementary Note 13); correspondence with the developmental organization of forebrain oligodendrocytes [25] remains at the level of axis anatomy,''',
     r'''concentrates on an axis rather than scattering across the 108 regions (Supplementary Note 13); correspondence with the developmental organization of forebrain oligodendrocytes [25] remains at axis anatomy,'''),
    # D7 L608
    (r'''report k_f with the design-matched null directly\u2014in the real data analyzed here, \u03c9 orderings were predominantly denominator-driven (Supplementary Note 9), so k_f plus a design-matched null is the honest default for ordering claims.''',
     r'''report k_f with the design-matched null directly (\u03c9 orderings here were predominantly denominator-driven; Supplementary Note 9).'''),
    # D9a L613a
    (r'''(v) Multiple testing and cluster-aware inference: the class-level upper-tail tests and the pair-level lower-tail screen are separate families reported without joint cross-family correction; the block-shuffle null assumes libraries are otherwise exchangeable, so systematic library-level confounding would distort the null in ways the permutation cannot capture (bounded by the pseudo-region negative control; Supplementary Note 12); and B = 1,000 bounds the resolvable P-value at 9.99 \u00d7 10\u207b\u2074, so the per-pair FDR outcome (minimum q = 0.520) is a statement about permutation resolution rather than evidence against any candidate.''',
     r'''(v) Multiple testing and cluster-aware inference: the class-level upper-tail tests and the pair-level lower-tail screen are reported without joint cross-family correction; the block-shuffle null assumes libraries are otherwise exchangeable (bounded by the pseudo-region negative control; Supplementary Note 12); and B = 1,000 bounds the resolvable P-value at 9.99 \u00d7 10\u207b\u2074, so the per-pair FDR outcome (minimum q = 0.520) reflects permutation resolution, not evidence against any candidate.'''),
    # D9b L613b
    (r'''the scDist results were obtained with a Python approximation of the R package and should be re-verified against the original implementation.''',
     r'''the scDist results used a Python approximation of the R package and should be re-verified against the original.'''),
    # D10 L628
    (r'''with applications to developmental biology, drug-response profiling, aging research, and evolutionary cell biology.''',
     r'''with applications across developmental biology, drug response, aging, and evolutionary cell biology.'''),
]

src = TARGET.read_text(encoding="utf-8")

ok = True
for i, (old, new) in enumerate(EDITS, 1):
    n = src.count(old)
    tag = "OK " if n == 1 else "BAD"
    if n != 1:
        ok = False
        print(f"[{tag}] edit {i:2d}: matches={n}  {old[:70]!r}")
if not ok:
    raise SystemExit("ABORT: unmatched OLD strings; nothing written.")
print(f"all {len(EDITS)} OLDs match exactly once")

def _wc(s):
    import re
    return len(re.sub(r'\\u[0-9a-fA-F]{4}', 'X', s).split())

total = 0
for old, new in EDITS:
    d = _wc(old) - _wc(new)
    total += d
    src = src.replace(old, new)
print(f"estimated words removed: ~{total}")

TARGET.write_text(src, encoding="utf-8")
print(f"applied -> {TARGET.name}")
