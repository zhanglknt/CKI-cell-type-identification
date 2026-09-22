# v50 Phase B batch 1: compress Decomposing + Calibration sections
# Replaces single lines by line number with prefix assertion (line count unchanged).
import io, sys

P = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
src = open(P, encoding="utf-8").read().split("\n")

REPL = {}

REPL[472] = (r"p('Step 2: Compute the functional divergence rate k_f.",
r"""p('Step 2: Compute the functional divergence rate k_f. We restrict the pseudobulk vectors to identity gene indices\u2014genes that define cell-type-specific functions. In the default configuration (Tabula Muris full pairwise matrix, Supplementary Fig. 1), identity genes are the top-2,000 highly variable genes (HVGs; Seurat flavor), excluding HK genes; for all other analyses (mouse pilot, human Tabula Sapiens, TCGA, brain atlas), k_f uses the top-200 differentially expressed genes (ranked by absolute mean difference) for that specific pair and k_n is computed per pair on the shared HK gene set, HK genes excluded throughout. k_f is the JS divergence between the two identity-gene probability distributions. Because the k_f genes are selected per pair from the observed difference itself, absolute k_f\u2014and therefore absolute \u03c9\u2014are upper-bound, scheme-specific estimates (fixed gene-panel ablation, Results).')""")

REPL[476] = (r"p(f'A parameter sweep on Tabula Muris mouse data",
r"""p(f'A parameter sweep on Tabula Muris ({_sb["n_pairs"]} pairs, {_ds["tabula_muris_organs"]} organs) showed that adding pathway enrichment scores to k_f does not improve discrimination (identity-only AUC = {_sb["identity_auc"]:.3f}; Supplementary Fig. 1, Supplementary Table 1). Partitioning expression into constrained baseline and identity gene sets suffices, without external pathway databases.')""")

REPL[481] = (r"p(f'We calibrated CKI on the Tabula Muris FACS dataset",
r"""p(f'We calibrated CKI on the Tabula Muris FACS dataset [8] (SmartSeq2, {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs), with housekeeping genes from the HRT Atlas v1.0 reference [13] (mouse ortholog column). For the full pairwise matrix (703 pairs, Supplementary Fig. 1), identity genes were the top-{_ds["n_hvg"]:,} highly variable genes (HVGs; Seurat), excluding HK genes; for the pilot calibration we used the hybrid per-pair scheme (per-pair k_n on the shared HK set; per-pair k_f on the top-200 differentially expressed genes, HK excluded) (Fig. 2).')""")

REPL[483] = (r"p(f'We performed control comparisons",
r"""p(f'We performed control comparisons in which we randomly split the same cell population into two halves, across six FACS control populations (Fig. 2a). Repeating split-half 50 times per population (300 \u03c9 values) stabilized the baseline at mean \u03c9 = 7.70 (SD of replicate means 1.15, 95% CI [7.37, 8.02]); the legacy six-split estimate (6.67) is consistent with it. No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence. A leave-one-population-out sensitivity gives a baseline range of 6.75\u20138.08 (Section 3.10 of the Supplementary Information).')""")

REPL[485] = (r"p(f'Beyond controls,",
r"""p(f'Beyond controls, \u03c9 values increased monotonically with biological distance (Fig. 2b, c): same cell type across organs (S category: mean \u03c9 = {_mc["S_mean"]:.2f}, n = {_mc["S_n"]}) sat below different cell types within an organ (D category: mean \u03c9 = {_mc["D_mean"]:.2f}, n = {_mc["D_n"]}), with cross-organ cross-type comparisons highest (2\u20134 pairs per category, so category means are calibration-scale estimates). Component analysis confirmed k_f as the driver: from controls to inter-cell-type comparisons, k_f rose roughly 400-fold ({_mc["kf_mean_ctrl"]:.4f} \u2192 {_mc["kf_mean_D"]:.2f}\u2013{_mc["kf_mean_X"]:.2f}), while k_n rose only {_mc["kn_fold_D"]:.0f}\u2013{_mc["kn_fold_X"]:.0f}-fold. CKI thus measures functional divergence, not total difference.')""")

REPL[487] = (r"p(f'Because the empirical baseline",
r"""p(f'Because the empirical baseline deviates substantially from the theoretical ideal (\u03c9 = 1), we introduce a calibrated omega, \u03c9_cal = \u03c9_obs / 7.70, reported to at most two significant figures. Scheme-matched split-half calibration inside each dataset shows the factor to be dataset-relative, not universal: the brain atlas baseline is 9.73 (95% CI [9.03, 10.53]; 29 populations), ~1.3-fold above the mouse-derived factor, whereas Tabula Sapiens gives 7.67 (95% CI [7.39, 8.00]), inside the mouse CI. Class-specific split-half baselines (range 7.58\u201312.52, a 1.65-fold spread) leave the astrocyte-to-Bergmann-glia gradient essentially unchanged (5.99, 95% CI [4.43, 7.69]) while compressing calibrated levels, and a ratio-estimator audit confirms the calibration absorbs ratio bias (median +0.2% per class \u00d7 region group; Supplementary Notes 2\u20134). calibrate_omega() is available in the CKI package.')""")

for ln, (prefix, new) in REPL.items():
    cur = src[ln - 1]
    assert cur.startswith(prefix), f"line {ln} prefix mismatch: {cur[:80]!r}"
    src[ln - 1] = new
    print(f"line {ln}: {len(cur)} -> {len(new)} ch")

open(P, "w", encoding="utf-8", newline="\n").write("\n".join(src))
print("OK batch1")
