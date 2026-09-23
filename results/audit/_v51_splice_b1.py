"""v51 splice batch 1: Intro [12]/[13] compression (219->~145, 292->~185)."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append(("p('CKI defines two rates:",
 r"p('CKI defines two rates: a baseline divergence rate k_n, estimated from housekeeping (HK) gene expression, and a functional divergence rate k_f, estimated from cell-type identity genes; the ratio \u03c9 = k_f/k_n quantifies baseline-normalized functional divergence (Fig. 1). The scope of \u03c9 is bounded by one central assumption, stated here once and quantified empirically throughout: the HK anchor is valid only where housekeeping expression remains constrained. Functional signal on HK genes is invisible to \u03c9 by construction, and in disease or strong-perturbation contexts the anchor itself shifts (TCGA and IFN-\u03b2 below; Supplementary Note 1), inflating the denominator and deflating the ratio; in such regimes \u03c9 must be read alongside its components, and k_f with a design-matched null is the honest default for ordering claims (Results; Discussion). CKI \u03c9 is a heuristic index, not a formal measure of Darwinian selection; interpretation is anchored in the empirical distribution of \u03c9 within each analysis rather than in fixed cut-offs (Discussion).')"))
R.append(("p('Here, we show that CKI provides",
 r"p('Here, we show that CKI provides a baseline-normalized index of cell-state divergence across five scales. First, random splits of the same mouse cell population (Tabula Muris [8]) yield \u03c9 above 1 (empirical calibration baseline 7.70, 95% CI [7.37, 8.02]). Second, in Tabula Sapiens human data [9], \u03c9 is negatively correlated with all four standard distance metrics\u2014partly a denominator effect of k_n (Results). Third, on real technical replicates (30 cross-lane PBMC pairs; 2,161 brain library pairs), \u03c9 shows the lowest drift misreporting among continuous metrics while retaining sensitivity to genuine biology. Fourth, on TCGA data [10,11] (five cancer types, 3,567 samples), CKI uncovers a consistent pan-cancer reversal\u2014tumors less divergent than adjacent non-tumor tissue, attributable to an elevated housekeeping baseline\u2014and resolves lung-adenocarcinoma driver classes, KRAS-mutant tumors retaining both functional (k_f) and baseline (k_n) divergence after purity and smoking adjustment while the apparent EGFR association dissolves. Fifth, in a human brain atlas [12], we quantify a regional differentiation gradient (1.74-fold size-balanced) and screen for anomalously similar cell-type/region pairs; because no candidate survives FDR correction, the screen is presented as a bounded, hypothesis-generating catalogue. Ground-truth simulations complement all five analyses throughout.')"))

nfail = 0
for prefix, newline in R:
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        print('FAIL prefix not unique:', prefix[:60], len(idx)); nfail += 1; continue
    old = lines[idx[0]]
    lines[idx[0]] = newline
    print(f'OK L{idx[0]+1}: {len(old.split())} -> {len(newline.split())} (line words)')
if nfail:
    raise SystemExit(1)
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('batch 1 written')
