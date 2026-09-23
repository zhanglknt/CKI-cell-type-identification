import sys

PATH = 'generate_manuscript_nc.py'
src = open(PATH, encoding='utf-8').read().splitlines()

REPL = [
    (r"""p('CKI takes two cell populations""",
     r"""p('CKI takes two cell populations, each represented as a pseudobulk expression vector (mean expression across cells), and applies the same metric (Jensen\u2013Shannon divergence) in three steps on the same expression matrix, so the ratio is internally calibrated (Fig. 1).')"""),
    (r"""p('Step 1: Compute the baseline""",
     r"""p('Step 1: baseline divergence rate k_n: pseudobulk vectors restricted to housekeeping (HK) gene indices, +1 pseudo-count, L1 normalization; k_n is the JS divergence between the two HK-gene probability distributions. Because HK genes should not differ systematically between biologically equivalent populations [13], k_n captures baseline technical and physiological noise.')"""),
    (r"""p('Step 2: Compute the functional""",
     r"""p('Step 2: functional divergence rate k_f on cell-type identity genes: top-2,000 highly variable genes (HVGs; Seurat, HK excluded) for the Tabula Muris full pairwise matrix (Supplementary Fig. 1), and the pair\u2019s top-200 differentially expressed genes (absolute mean difference, HK excluded) for all other analyses, with k_n computed per pair on the shared HK set (fixed-panel ablation, Results).')"""),
    (r"""p(f'Step 3: \u03c9 = k_f/k_n.""",
     r"""p(f'Step 3: \u03c9 = k_f/k_n. Statistical inference uses permutation testing (B = 1,000 for all datasets): group labels are permuted (cell labels for mouse and human, sample labels for TCGA) or, for the brain, library-to-region assignments block-shuffled; empirical P-values, standardized effect sizes, and Benjamini-Hochberg FDR are computed within each dataset (Methods).')"""),
    (r"""p(f'We calibrated CKI on the Tabula Muris FACS""",
     r"""p(f'We calibrated CKI on the Tabula Muris FACS dataset [8] (SmartSeq2, {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs), with housekeeping genes from HRT Atlas v1.0 [13] (mouse ortholog column): top-{_ds["n_hvg"]:,} HVGs for the full pairwise matrix (703 pairs, Supplementary Fig. 1), and the hybrid per-pair scheme for the pilot calibration (Fig. 2).')"""),
    (r"""p(f'We performed control comparisons""",
     r"""p(f'Control comparisons randomly split the same population into halves across six FACS control populations (Fig. 2a): 50 split-half replicates per population (300 \u03c9 values) stabilized the baseline at mean \u03c9 = 7.70 (95% CI [7.37, 8.02]; legacy six-split estimate 6.67 consistent; leave-one-population-out range 6.75\u20138.08; Section 3.10). No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence.')"""),
    (r"""p(f'Beyond controls,""",
     r"""p(f'Beyond controls, \u03c9 increased monotonically with biological distance (Fig. 2b, c): same cell type across organs (mean \u03c9 = {_mc["S_mean"]:.2f}, n = {_mc["S_n"]}) sat below different cell types within an organ (mean \u03c9 = {_mc["D_mean"]:.2f}, n = {_mc["D_n"]}), with cross-organ cross-type comparisons highest (2\u20134 pairs per category, calibration-scale estimates). Component analysis confirmed k_f as the driver: from controls to inter-cell-type comparisons, k_f rose ~400-fold ({_mc["kf_mean_ctrl"]:.4f} \u2192 {_mc["kf_mean_D"]:.2f}\u2013{_mc["kf_mean_X"]:.2f}) while k_n rose only {_mc["kn_fold_D"]:.0f}\u2013{_mc["kn_fold_X"]:.0f}-fold\u2014CKI measures functional divergence, not total difference.')"""),
    (r"""p(f'Because the empirical baseline""",
     r"""p(f'Because the empirical baseline deviates from the theoretical ideal (\u03c9 = 1), we introduce \u03c9_cal = \u03c9_obs / 7.70. Split-half calibration inside each dataset shows the factor to be dataset-relative (brain atlas 9.73 [9.03, 10.53]; Tabula Sapiens 7.67 [7.39, 8.00], inside the mouse CI); class-specific baselines leave the astrocyte-to-Bergmann-glia gradient essentially unchanged, and a ratio-estimator audit confirms the calibration absorbs ratio bias (Supplementary Notes 2\u20134).')"""),
    (r"""p(f'Human \u03c9 values ranged""",
     r"""p(f'Human \u03c9 ranged from {_h["omega_min"]:.2f} to {_h["omega_max"]:.2f} (mean {_h["omega_mean"]:.2f}, median {_h["omega_median"]:.2f}, n = {_h["n_pairs_total"]:,} pairs); cross-dataset \u03c9 comparisons are rank-based only (Discussion). The biological hierarchy was preserved: same cell type across organs (mean \u03c9 = {_h["diff_organ_same_ct_mean"]:.2f}, n = {_h["diff_organ_same_ct_n"]}) sat below different cell types within an organ (mean \u03c9 = {_h["same_organ_diff_ct_mean"]:.2f}, n = {_h["same_organ_diff_ct_n"]:,}).')"""),
    (r"""p(f'We computed CKI \u03c9 and four standard metrics""",
     r"""p(f'We computed CKI \u03c9 and four standard metrics (raw JS divergence, Spearman distance, cosine distance, marker Jaccard distance) on all {_h["n_pairs_total"]:,} human cell-type pairs. \u03c9 correlated negatively with all four (Spearman r = {f'{_sc["max"]:.2f}'.replace('-', '\u2212')} to {f'{_sc["min"]:.2f}'.replace('-', '\u2212')}, all P < 10\u207b\u00b9\u2074\u2075), the four forming a tight positive cluster (pairwise r = {_sc["std_pairwise_min"]:.2f}\u2013{_sc["std_pairwise_max"]:.2f}). The negative sign is partly a ratio artifact: k_f correlated positively with the standard metrics (r = +{_decomp_kf_lo:.2f} to +{_decomp_kf_hi:.2f}) and k_n more strongly (r = +{_decomp_kn_lo:.2f} to +{_decomp_kn_hi:.2f}), and conditional on k_n all four \u03c9\u2013metric correlations turned positive (partial r = +{_decomp_pc_lo:.2f} to +{_decomp_pc_hi:.2f}, all P < 1 \u00d7 10\u207b\u00b9\u2074).')"""),
    (r"""p(f'CKI was the only metric""",
     r"""p(f'CKI was the only metric scoring same-organ different-cell-type pairs above different-organ different-cell-type pairs (mean \u03c9 {_h["same_organ_diff_ct_mean"]:.2f}, n = {_h["same_organ_diff_ct_n"]:,} vs. {_h["diff_organ_diff_ct_mean"]:.2f}, n = {_h["diff_organ_diff_ct_n"]:,}; Mann-Whitney P = 5.6 \u00d7 10\u207b\u00b9\u2078); all four standard metrics showed the opposite pattern. Decomposition tempers the functional reading: same-organ pairs have indistinguishable k_f (P = 0.60) but lower k_n (P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable housekeeping baseline within organs, not greater functional specialization (Supplementary Note 9).')"""),
]

used = set()
for idx, (pre, new) in enumerate(REPL):
    hits = [i for i, l in enumerate(src) if l.strip().startswith(pre) and i not in used]
    if len(hits) != 1:
        print(f'FAIL[{idx}] matched {len(hits)}: {pre[:70]}')
        sys.exit(1)
    i = hits[0]
    used.add(i)
    ow = len(src[i].split()); nw = len(new.split())
    src[i] = new
    print(f'L{i+1}: {ow} -> {nw}')

open(PATH, 'w', encoding='utf-8').write('\n'.join(src) + '\n')
print('WROTE OK')
