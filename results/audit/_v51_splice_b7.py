"""v51 splice batch 7: brain regional gradient paragraphs [55]-[61]."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p('We applied CKI to the Siletti",
 r'''p('We applied CKI to the Siletti et al. human brain single-nucleus atlas [12] (~3.3 million nuclei, 108 regions), asking how much functional divergence separates the same cell type across regions. We focused on 888,263 non-neuronal nuclei in 10 major classes (neurons excluded: supercluster_term does not resolve neuronal subtypes). CKI \u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs) (Fig. 6; Supplementary Fig. 6; Supplementary Table 3); vascular cells and fibroblasts are heterogeneous superclusters, so their class-level \u03c9 values are supercluster averages.')'''))
R.append((r"p('Class-mean \u03c9 spanned",
 r'''p('Class-mean \u03c9 spanned a regional gradient across cell classes, from Bergmann glia and vascular cells (both 13.56) to astrocytes (82.75 \u00b1 44.98, n = 5,778 pairs across 108 regions)\u2014a full-data endpoint gradient of 6.10-fold. Because class-mean k_n is confounded by class size (below), this headline is an uncorrected upper bound: an equal-n downsample control attenuates it to 1.74 (95% CI [1.64, 1.84]), and a span-matched control restricted to the 21 intra-cerebellar region pairs yields 3.68 (residual again k_n-driven; Supplementary Note 10). We therefore co-report 6.10-fold (full-data) and 1.74-fold (size-balanced) throughout (5.99 under class-specific split-half baselines; Supplementary Note 2).')'''))
R.append((r"p('To test whether this gradient exceeds chance",
 r'''p('To test whether this gradient exceeds chance, we used a cell-type-level block-shuffle null that permutes 10x-library-to-region assignments (B = 1,000; Methods). For 4 of 10 cell classes regional structure significantly raised mean \u03c9 (astrocytes at the permutation floor; OPCs, committed OPCs, fibroblasts P \u2264 0.030), 3 of 10 surviving Benjamini-Hochberg correction; a donor-stratified null (Methods) leaves the same 3 of 10, and the single class moving against the conservative direction\u2014ependymal cells\u2014still does not survive correction (stratified q = 0.052). Microglia, oligodendrocytes, and Bergmann glia sit at or below the null expectation.')'''))
R.append((r"p('Four analyses probe the robustness",
 r'''p('Four analyses probe the robustness of the gradient. First, restricting comparisons to same-donor region pairs preserved the extremes and a 4.50-fold gradient, so donor identity cannot explain the gradient away (per-class values in Supplementary Note 12). Second, the astrocyte-versus-Bergmann-glia contrast is predominantly a k_n effect (k_f differs 2.0-fold; mean k_n 3.2-fold): across the ten classes, class-mean \u03c9 tracks k_n (Spearman \u03c1 = \u22120.73) but not k_f (\u03c1 = 0.09), and under a k_f-only ordering astrocytes rank third of ten. The gradient thus chiefly reflects housekeeping stability across regions, not functional-gene divergence (k_n estimator sensitivity: Supplementary Fig. 7).')'''))
R.append((r"p('Third, class-mean k_n correlates",
 r'''p('Third, class-mean k_n correlates negatively with class size (Spearman \u03c1 = \u22120.648, P = 0.043) while class-mean \u03c9 is uncorrelated with all tested confounders (P \u2265 0.091; Supplementary Note 10). The equal-n residual is carried predominantly by the functional term: the astrocyte/Bergmann-glia k_f ratio is 2.09 under equal-n (full-data 2.03), whereas the k_n ratio reverses direction (equal-n 1.29, astrocyte higher; full-data 0.31)\u2014the Bergmann-glia k_n elevation in the full data is largely a class-size artefact. Fourth, the gradient is robust to the group-size threshold in direction but not magnitude.')'''))
R.append((r"p('The gradient aligns with known cell biology",
 r'''p('The gradient aligns with known cell biology: vascular cells and fibroblasts are tissue-resident and replenished locally, consistent with their low \u03c9 (though low class-level \u03c9 is not spatial uniformity [17,18]); microglia share core surveillance machinery [19]; astrocytes express region-specific ion channels, transporters, and secreted factors\u2014regional specialization compatible with, but not established by, the k_n-dominated ordering.')'''))
R.append((r"p('The gradient suggests a residence/migration framework",
 r'''p('The gradient suggests a residence/migration framework (recently migrated types should show low inter-regional \u03c9; resident types accumulate regional signatures), but the data provide no evidence for it: OPCs\u2014the most actively migrating non-neuronal population\u2014show the second-highest mean \u03c9 (40.62), and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92); the framework remains hypothesis generation, not inference.')'''))

nfail = 0
for prefix, newline in R:
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        print('FAIL prefix not unique:', prefix[:60], len(idx)); nfail += 1; continue
    old = lines[idx[0]]
    lines[idx[0]] = newline
    print(f'OK L{idx[0]+1}: {len(old.split())} -> {len(newline.split())}')
if nfail:
    raise SystemExit(1)
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('batch 7 written')
