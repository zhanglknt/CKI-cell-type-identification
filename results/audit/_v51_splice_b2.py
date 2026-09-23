"""v51 splice batch 2: decomposition/calibration/correlation (f-string preserving)."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append(("p('Step 2: Compute the functional divergence rate",
 r"p('Step 2: Compute the functional divergence rate k_f on cell-type identity genes. In the default configuration (Tabula Muris full pairwise matrix, Supplementary Fig. 1) these are the top-2,000 highly variable genes (HVGs; Seurat), excluding HK genes; for all other analyses, k_f uses the top-200 differentially expressed genes of that specific pair (ranked by absolute mean difference, HK excluded) and k_n is computed per pair on the shared HK gene set. Because the k_f genes are selected per pair from the observed difference itself, absolute k_f\u2014and therefore absolute \u03c9\u2014are upper-bound, scheme-specific estimates (fixed-panel ablation, Results).')"))
R.append(("p(f'Beyond controls, ",
 r"p(f'Beyond controls, \u03c9 values increased monotonically with biological distance (Fig. 2b, c): same cell type across organs (S category: mean \u03c9 = {_mc[\"S_mean\"]:.2f}, n = {_mc[\"S_n\"]}) sat below different cell types within an organ (D category: mean \u03c9 = {_mc[\"D_mean\"]:.2f}, n = {_mc[\"D_n\"]}), with cross-organ cross-type comparisons highest (2\u20134 pairs per category, calibration-scale estimates). Component analysis confirmed k_f as the driver: from controls to inter-cell-type comparisons, k_f rose roughly 400-fold ({_mc[\"kf_mean_ctrl\"]:.4f} \u2192 {_mc[\"kf_mean_D\"]:.2f}\u2013{_mc[\"kf_mean_X\"]:.2f}) while k_n rose only {_mc[\"kn_fold_D\"]:.0f}\u2013{_mc[\"kn_fold_X\"]:.0f}-fold\u2014CKI measures functional divergence, not total difference.')"))
R.append(("p(f'Because the empirical baseline deviates",
 r"p(f'Because the empirical baseline deviates substantially from the theoretical ideal (\u03c9 = 1), we introduce a calibrated omega, \u03c9_cal = \u03c9_obs / 7.70. Split-half calibration inside each dataset shows the factor to be dataset-relative, not universal (brain atlas 9.73 [9.03, 10.53]; Tabula Sapiens 7.67 [7.39, 8.00], inside the mouse CI); class-specific baselines leave the astrocyte-to-Bergmann-glia gradient essentially unchanged, and a ratio-estimator audit confirms the calibration absorbs ratio bias (Supplementary Notes 2\u20134).')"))
R.append(("p(f'We computed CKI ",
 r"p(f'We computed CKI \u03c9 and four standard metrics (raw JS divergence, Spearman distance, cosine distance, marker Jaccard distance) on all {_h[\"n_pairs_total\"]:,} human cell-type pairs. CKI \u03c9 was negatively correlated with all four (Spearman r = {f\'{_sc[\"max\"]:.2f}\'.replace(\'-\', \'\u2212\')} to {f\'{_sc[\"min\"]:.2f}\'.replace(\'-\', \'\u2212\')}, all P < 10\u207b\u00b9\u2074\u2075), whereas the four formed a tight positive cluster (pairwise r = {_sc[\"std_pairwise_min\"]:.2f}\u2013{_sc[\"std_pairwise_max\"]:.2f}). Decomposition shows this is partly a ratio artifact: k_f correlated positively with the standard metrics (r = +{_decomp_kf_lo:.2f} to +{_decomp_kf_hi:.2f}) and k_n more strongly (r = +{_decomp_kn_lo:.2f} to +{_decomp_kn_hi:.2f}), and conditional on k_n the \u03c9\u2013metric correlations turned positive in all four cases (partial r = +{_decomp_pc_lo:.2f} to +{_decomp_pc_hi:.2f}, all P < 1 \u00d7 10\u207b\u00b9\u2074).')"))
R.append(("p(f'CKI was the only metric where",
 r"p(f'CKI was the only metric where same-organ different-cell-type pairs had higher values than different-organ different-cell-type pairs (mean \u03c9 {_h[\"same_organ_diff_ct_mean\"]:.2f}, n = {_h[\"same_organ_diff_ct_n\"]:,} vs. {_h[\"diff_organ_diff_ct_mean\"]:.2f}, n = {_h[\"diff_organ_diff_ct_n\"]:,}; Mann-Whitney U, P = 5.6 \u00d7 10\u207b\u00b9\u2078); all four standard metrics showed the opposite pattern. Decomposition tempers the reversal\u2019s functional reading: same-organ pairs have indistinguishable k_f (P = 0.60) but lower k_n (P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable housekeeping baseline within organs, not greater functional specialization (per-component values in Supplementary Note 9).')"))

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
print('batch 2 written')
