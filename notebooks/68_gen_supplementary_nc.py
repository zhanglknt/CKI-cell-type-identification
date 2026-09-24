"""
Generate NC-format Supplementary Information DOCX (from 68_gen_supplementary_en.py).
NC naming: Supplementary Note 1-15, Supplementary Fig., Supplementary Table.
Output: results/CKI_Supplementary_NC.docx
"""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _load_manuscript_data import get_manuscript_data
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from lxml import etree

# Load all manuscript data dynamically
DATA = get_manuscript_data()
_br = DATA['brain']
_h = DATA['human']
_mc = DATA['mouse_calibration']

import json
import numpy as np
import pandas as pd
from scipy import stats

# Brain block-shuffle observed pairs (current pipeline: 08d/08e)
_obs = pd.read_csv(Path(__file__).resolve().parent.parent / "results" / "brain_bs_null_observed_pairs.csv")

# Region-associated candidates for S4 top-5 (Strong tier from the block-shuffle re-analysis)
_mig = _obs
_strong = _mig[_mig['tier'] == 'Strong'].sort_values('residual').head(5)
_candidates = _mig[_mig['tier'].isin(['Strong', 'Moderate', 'Weak'])]

# Per-pair k_n variability (phaseC)
_knv = json.loads((Path(__file__).resolve().parent.parent / "results" / "phaseC_kn_variability.json").read_text())
_kn_overall = _knv['brain_overall']
_kn_per_ct = _knv['per_cell_type']
_kn_rho = _knv['omega_correlation']['spearman_rho']
_kn_rho_p = _knv['omega_correlation']['p_value']
_kn_cv_lo = min(_kn_per_ct.items(), key=lambda kv: kv[1]['kn_cv'])
_kn_cv_hi = max(_kn_per_ct.items(), key=lambda kv: kv[1]['kn_cv'])

# Scheme-matched split-half internal baselines (reviewer C-B; notebooks 42/43)
_bs_txt = (Path(__file__).resolve().parent.parent / "results" / "reviewer_brain_splithalf_summary.txt").read_text()
_bs = dict(kv.split(None, 1) for kv in (ln.strip() for ln in _bs_txt.splitlines()) if '\t' in kv or ' ' in kv)
_brain_sh_mean = float(_bs['brain_split_half_mean_omega'])
_brain_sh_ci = [float(x) for x in _bs['brain_split_half_ci95'].strip('[]').split(',')]

_ts_txt = (Path(__file__).resolve().parent.parent / "results" / "reviewer_ts_splithalf_summary.txt").read_text()
_ts = dict(kv.split(None, 1) for kv in (ln.strip() for ln in _ts_txt.splitlines()) if '\t' in kv or ' ' in kv)
_ts_sh_mean = float(_ts['ts_split_half_mean_omega'])
_ts_sh_ci = [float(x) for x in _ts['ts_split_half_ci95'].strip('[]').split(',')]

# Per-class split-half calibration (reviewer E1-M4/E2-M5; notebook 76)
_pc = json.loads((Path(__file__).resolve().parent.parent / "results" / "perclass_calibration.json").read_text())
_pc_base = pd.DataFrame(_pc['baselines']).set_index('cell_type')
_pc_cal = pd.DataFrame(_pc['calibration']).set_index('cell_type')
_pc_bmin, _pc_bmax = _pc_base['baseline_popmean'].min(), _pc_base['baseline_popmean'].max()
_pc_bmin_ct = _pc_base['baseline_popmean'].idxmin()
_pc_bmax_ct = _pc_base['baseline_popmean'].idxmax()
_pc_grad = _pc['gradient']['per_class']
# P1-2 (blind-review round 1, E1-M2): joint region-clustered bootstrap values from
# notebooks/81_perclass_uncertainty.py (numerator region-clustered, denominator
# two-stage split-half resampling); the i.i.d.-numerator CIs in
# perclass_calibration.json are anti-conservative and superseded.
_pc_unc = json.loads((Path(__file__).resolve().parent.parent / "results" / "perclass_uncertainty.json").read_text())
_pc_unc_df = pd.read_csv(Path(__file__).resolve().parent.parent / "results" / "perclass_uncertainty.csv").set_index('cell_type')
_kfo = json.loads((Path(__file__).resolve().parent.parent / "results" / "kf_only_ordering.json").read_text())
_kfo_sev = pd.read_csv(Path(__file__).resolve().parent.parent / "results" / "kf_only_severity.csv")
_pc_grad_ci = _pc_unc['gradient']['joint_region_clustered_ci']
_pc_grad_ci_old = _pc['gradient']['per_class_ci95']
_pc_astro = float(_pc_cal.loc['Astrocyte', 'omega_cal_class'])
_pc_astro_ci = [float(_pc_unc_df.loc['Astrocyte', 'omega_cal_class_lo']),
                float(_pc_unc_df.loc['Astrocyte', 'omega_cal_class_hi'])]
_pc_bg = float(_pc_cal.loc['Bergmann glia', 'omega_cal_class'])
_pc_bg_ci = [float(_pc_unc_df.loc['Bergmann glia', 'omega_cal_class_lo']),
             float(_pc_unc_df.loc['Bergmann glia', 'omega_cal_class_hi'])]
_pc_bg_nreg = int(_pc_unc_df.loc['Bergmann glia', 'n_baseline_regions'])
_pc_bg_base_ci = [float(_pc_unc_df.loc['Bergmann glia', 'baseline_two_stage_lo']),
                  float(_pc_unc_df.loc['Bergmann glia', 'baseline_two_stage_hi'])]
_pc_astro_base_ci = [float(_pc_unc_df.loc['Astrocyte', 'baseline_two_stage_lo']),
                     float(_pc_unc_df.loc['Astrocyte', 'baseline_two_stage_hi'])]
_pc_n_div_joint = _pc_unc['n_divergent_joint']
_pc_bg_rc = [8.49, 19.52]  # canonical published BG region-clustered CI
# (class-level CI list, _v38_statistical_addenda.py, B = 2,000); the per-class
# calibration script's independent re-run ([9.09, 19.35]) is a bootstrap
# resampling wobble of the same estimator -- use one value package-wide.
_pc_bg_base = float(_pc_cal.loc['Bergmann glia', 'baseline_class'])
_pc_n_div = dict(_pc['classification']['n_divergent'])
# under the canonical [8.49, 19.52] interval the BG class-mean CI includes its
# own baseline 9.08, so per-class divergence is 9/10 (BG borderline), not 10/10
_pc_n_div['per_class'] = 9

# Normality tests on the current-pipeline omega distributions
_norm_brain_p = float(stats.normaltest(_obs['omega'])[1])
_norm_human_p = float(stats.shapiro(pd.read_csv(
    Path(__file__).resolve().parent.parent / "results" / "phase35_all_metrics_pairs.csv")['omega'])[1])
_norm_mouse_p = float(stats.shapiro(pd.read_csv(
    Path(__file__).resolve().parent.parent / "results" / "mouse_pilot_v2_results.csv")['omega'])[1])
_norm_mouse_skew = float(stats.skew(pd.read_csv(
    Path(__file__).resolve().parent.parent / "results" / "mouse_pilot_v2_results.csv")['omega']))

# Bootstrap 95% CIs for the class-mean omega (pair-level resampling, B = 10,000)
# Round-8 fix (E3-M2): report the mean CIs shipped in phaseB_bootstrap_cis.csv
# (the file accompanying the submission) rather than median CIs recomputed
# inline, so SN 3.2 matches the shipped artifact and the mean-based reporting
# used throughout the manuscript.
_pb_cis = pd.read_csv(Path(__file__).resolve().parent.parent / "results" / "phaseB_bootstrap_cis.csv")

# nc49 v49: real-data neutral-drift calibration and TCGA per-sample statistics
_root49 = Path(__file__).resolve().parent.parent
_kang_drift = pd.read_csv(_root49 / "results" / "nc49_pilot_kang_techrep.csv")
_ladder = pd.read_csv(_root49 / "results" / "nc49_brain_drift_ladder.csv")
_tcga_pc = pd.read_csv(_root49 / "results" / "nc52_tcga_pancancer_excc.csv")
_tcga_luad = pd.read_csv(_root49 / "results" / "nc49_tcga_luad_mutation.csv")
_tcga_cox = pd.read_csv(_root49 / "results" / "nc52_lihc_cox_excc.csv")

_METRICS49 = ['k_n', 'k_f', 'omega', 'raw_js', 'cosine', 'spearman', 'marker_jaccard']
_LABEL49 = {'k_n': 'k_n', 'k_f': 'k_f', 'omega': '\u03c9', 'raw_js': 'raw JS',
            'cosine': 'cosine', 'spearman': 'Spearman', 'marker_jaccard': 'marker Jaccard'}


def _wilson49(k, n):
    ci = stats.binomtest(int(k), int(n)).proportion_ci(0.95, method='wilson')
    return ci.low, ci.high


def _agg49(df, metric):
    """Calibration median [IQR] and false-positive count for one metric."""
    cal = df['cal_' + metric]
    ex = df['exceed_' + metric]
    return dict(cal_med=float(cal.median()), cal_lo=float(cal.quantile(0.25)),
                cal_hi=float(cal.quantile(0.75)), k=int(ex.sum()), n=int(len(df)))


_SUP49 = str.maketrans('0123456789-', '\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207b')


def _pf49(v):
    """Format a P-value in the SI house style (unicode scientific below 1e-3)."""
    v = float(v)
    if v < 1e-3:
        m, e = f'{v:.1e}'.split('e')
        return f'{m}\u00d710{str(int(e)).translate(_SUP49)}'
    if v < 0.1:
        return f'{v:.3f}'
    return f'{v:.2f}'


# Kang batch-1 aggregates
_km49 = {m: _agg49(_kang_drift, m) for m in ['k_n', 'k_f', 'omega', 'raw_js', 'cosine']}

# Brain ladder aggregates per tier
_lad49 = {}
for _t, _tier in (('T1', 'T1_techrep'), ('T2', 'T2_cross_donor'), ('T3', 'T3_cross_roi')):
    _sub = _ladder[_ladder['tier'] == _tier]
    _lad49[_t] = {m: _agg49(_sub, m) for m in _METRICS49}

# T1 per-cell-class FPR comparison (omega vs raw JS / cosine / Spearman)
_t1_49 = _ladder[_ladder['tier'] == 'T1_techrep']
_t1ct_49 = _t1_49.groupby('cell_type').agg(
    fpr_omega=('exceed_omega', 'mean'), fpr_js=('exceed_raw_js', 'mean'),
    fpr_cos=('exceed_cosine', 'mean'), fpr_spr=('exceed_spearman', 'mean'),
    fpr_mj=('exceed_marker_jaccard', 'mean'),
    cal_omega=('cal_omega', 'median'), n=('exceed_omega', 'size'))
_nct_49 = len(_t1ct_49)
_below49 = dict(js=int((_t1ct_49.fpr_omega < _t1ct_49.fpr_js).sum()),
                cos=int((_t1ct_49.fpr_omega < _t1ct_49.fpr_cos).sum()),
                spr=int((_t1ct_49.fpr_omega < _t1ct_49.fpr_spr).sum()),
                mj=int((_t1ct_49.fpr_mj < _t1ct_49.fpr_omega).sum()))
_ratio49 = _t1ct_49.fpr_js / _t1ct_49.fpr_omega
_ratio_lo49, _ratio_hi49 = float(_ratio49.min()), float(_ratio49.max())

# T1 FPR growth with group size (min of the two library sizes per pair)
_nmin49 = _t1_49[['n_cells_a', 'n_cells_b']].min(axis=1)
_bins49 = {}
for _lab, _mask in (('small', _nmin49 <= 30), ('mid', (_nmin49 > 30) & (_nmin49 <= 500)),
                    ('large', _nmin49 > 500)):
    _bins49[_lab] = dict(n=int(_mask.sum()),
                         fpr_omega=float(_t1_49.loc[_mask, 'exceed_omega'].mean()),
                         fpr_js=float(_t1_49.loc[_mask, 'exceed_raw_js'].mean()))


def _mean_ci_from_file(group):
    row = _pb_cis[(_pb_cis['dataset'] == 'Brain') & (_pb_cis['group'] == group)].iloc[0]
    return float(row['omega_mean']), float(row['ci_95_lower']), float(row['ci_95_upper'])


_ci_astro = _mean_ci_from_file('Astrocyte')
_ci_berg = _mean_ci_from_file('Bergmann glia')

doc = Document()

# Set default font
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

# Page margins (NAR: 2.5cm)
for sec in doc.sections:
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)

# Heading styles
for lvl, size in [(1, 16), (2, 14), (3, 12)]:
    hs = doc.styles[f'Heading {lvl}']
    hs.font.name = 'Arial'
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)


def add_heading(text, level=1):
    return doc.add_heading(text, level=level)


def add_para(text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


# v49.5: all 15 SI tables are migrated to results/CKI_Supplementary_Tables_NC.xlsx
# (Supplementary Tables 5-19, one sheet per table, in document order). The docx
# itself carries no tables; add_table only collects the rows, and the former
# in-document caption paragraph of each table is registered via si_caption so
# the pair (rows, caption) can be exported with the caption as the sheet's A1.
_SI_TABLE_ROWS = []
_SI_TABLE_CAPS = []

def add_table(rows, header=True):
    _SI_TABLE_ROWS.append([[str(v) for v in row] for row in rows])
    return None

def si_caption(text):
    body = re.sub(r'^Supplementary Table \d+\.\s*', '', text)
    _SI_TABLE_CAPS.append(body)
    return None


# ===== TITLE PAGE =====
add_heading('Supplementary Information', 1)
add_para('CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases')
add_para('Xianming Wu (1), Li Zhang (1,2,*)')
add_para('(1) Chinese Institute for Brain Research, Beijing 102206, China')
add_para('(2) Institute of Blood Transfusion, Chinese Academy of Medical Sciences & '
         'Peking Union Medical College, Chengdu 610052, China')
add_para('(*) Corresponding author')
add_para('')

add_heading('Table of Contents', 2)
toc = [
    'CKI Mathematical Derivation',
    'CKI Algorithm Pseudocode',
    'Statistical Testing Details',
    'Dataset Quality Control and Filtering Criteria',
    'Supplementary Note 1: Ground-Truth Simulation',
    'Supplementary Note 2: Small-Cluster Bootstrap Corrections for Region-Clustered CIs',
    'Supplementary Note 3: Calibrated Omega Normalization',
    'Supplementary Note 4: Ratio-Estimator Bias\u2013Variance Characterization',
    'Supplementary Note 5: Non-HK-Anchored Neutral Drift Controls',
    'Supplementary Note 6: Real Perturbation Demonstration (Kang et al. IFN-beta PBMC)',
    'Supplementary Note 7: Fixed Gene-Panel Ablation',
    'Supplementary Note 8: TCGA composition-contribution check for the NN/TT k_n reversal',
    'Supplementary Note 9: k_f-only Ordering Controls (Cross-Organ Ranking and TCGA Severity)',
    'Supplementary Note 10: Brain Class-Size Confounding Controls and min-cells Threshold Sensitivity',
    'Supplementary Note 11: Region Glossary (Siletti et al. Dissection Nomenclature)',
    'Supplementary Note 12: Pseudo-Region Negative Control (Block-Shuffle Null Calibration)',
    'Supplementary Note 13: Brain set-level enrichment of the block-shuffle signal (post-hoc)',
    'Supplementary Note 14: Comparison with Augur Cell-Type Prioritization',
    'Supplementary Note 15: JS Divergence Dimensionality Invariance',
    'Supplementary Note 16: Human-Brain Sanity Check on the Microglia Supercluster',
    'Supplementary Methods',
    'Supplementary Table 1: Parameter Sweep Results',
    'Supplementary Table 2: Cross-Organ Conservation Data',
    'Supplementary Table 3: Human Brain Non-neuronal Cell Regional CKI Data',
    'Supplementary Table 4: Inter-regional Region-Associated Candidate Data',
    'Supplementary Table 5: TCGA Linear-Normalization Robustness',
    'Supplementary Table 6: Kang IFN-beta Per-Cell-Type Effects',
    'Supplementary Table 7: Target-Detection AUC in Mean-Shift Simulation',
    'Supplementary Table 8: Donor-Paired Detection Power',
    'Supplementary Table 9: Kang Batch-1 Technical-Replicate Calibration',
    'Supplementary Table 10: Brain Drift Ladder by Tier and Metric',
    'Supplementary Table 11: Pan-Cancer NN/TT Ratios',
    'Supplementary Table 12: LUAD Driver-Group Means',
    'Supplementary Table 13: LUAD Pairwise Contrasts',
    'Supplementary Table 14: LIHC Overall-Survival Cox Models',
    'Supplementary Table 15: Purity Sensitivity of the Pan-Cancer Reversal',
    'Supplementary Table 16: LUAD Admixture-Adjusted Contrasts',
    'Supplementary Table 17: LUAD Smoking-Covariate Adjustment',
    'Supplementary Table 18: TCGA Clinical-Severity Gradients',
    'Supplementary Table 19: Brain min-cells Threshold Sensitivity',
    'Supplementary Data 1: Analysis Script Index',
]
for item in toc:
    add_para(item)

doc.add_page_break()

# ===== SN1: Mathematical Derivation =====

add_heading('CKI Mathematical Derivation', 2)

add_para('1.1 Jensen-Shannon Divergence', bold=True)
add_para(
    'The Jensen-Shannon (JS) divergence is a symmetrized and smoothed version of the '
    'Kullback-Leibler divergence. For two probability vectors p and q: '
    'JS(p, q) = 1/2 D(p||m) + 1/2 D(q||m), where m = 1/2(p+q), '
    'and D(p||q) = \u03a3 p_i log2(p_i/q_i). When using the base-2 logarithm, '
    'the JS divergence is bounded in [0, 1]. This bound is important for interpreting '
    '\u03c9: when both k_n and k_f approach 1, \u03c9 = k_f/k_n may still vary. '
    'A small floor value (1e-4) on k_n is applied only in the TCGA bulk RNA-seq analysis '
    '(where pseudobulk averaging across millions of cells compresses HK gene variance and '
    'drives aggregate k_n toward zero) to prevent inflated \u03c9 from near-zero denominators; '
    'all single-cell analyses (mouse, Tabula Sapiens, brain atlas) apply no floor '
    '(kn_floor = 0, positivity guard only; minimum observed per-pair k_n: '
    '1.1e-4, mouse; 6.3e-4, human; 9.2e-5, brain; under the reported brain pipeline, '
    'only 1 of 31,764 pairs had k_n below 1e-4, and these values entered \u03c9 uncapped). '
    'Before computing JS divergence, both pseudobulk vectors are mapped to probability '
    'distributions by a softmax over the log-transformed values '
    '(cki.utils.ensure_probability_distribution, mode = "softmax"). For single-cell data '
    '(natural-log log1p of library-size-normalized counts) this mapping is exactly linear '
    'in the normalized counts: softmax(log1p(x)) yields p_i = (x_i + 1)/\u03a3(x_j + 1), '
    'equivalent to a +1 pseudo-count followed by L1 normalization. For TCGA bulk RNA-seq '
    '(log2(TPM + 1) values) the same softmax is mathematically equivalent to a power '
    'transformation, p_i \u221d (TPM + 1)^(1/ln 2) = (TPM + 1)^1.4427, which earlier '
    'versions of this document did not disclose. A full re-analysis of the TCGA pipeline '
    'under a strictly linear mapping, p_i = (TPM + 1)/\u03a3(TPM + 1), leaves every '
    'qualitative conclusion unchanged (robustness table in Section 1.7).'
)

add_para('1.2 Baseline Divergence Rate k_n', bold=True)
add_para(
    'Housekeeping (HK) genes are defined as genes that maintain stable expression '
    'across cell types and conditions. Let H = {g1, ..., gM} be the set of HK gene '
    'indices. Given pseudobulk vectors \u03bc_A and \u03bc_B (length G, total number of genes), '
    'the baseline divergence rate is: k_n = JS(norm(\u03bc_A[H]), norm(\u03bc_B[H])), '
    'where norm() denotes +1 pseudo-count addition followed by L1 normalization. '
    'Rationale: HK genes should not exhibit systematic differences between biologically '
    'identical cell populations. The JS divergence observed on HK genes therefore reflects '
    'baseline noise: technical variation, stochastic transcriptional bursting, and '
    'individual-level physiological differences. k_n thus provides an internal baseline, '
    'heuristically analogous to Ks (synonymous substitution rate) in molecular evolution. '
    'HK gene set selection: HK genes were loaded from the HRT Atlas v1.0 reference '
    '(1,130 human-mouse conserved HK genes) [13]. For mouse datasets, the mouse ortholog '
    'column is used; for human datasets (Tabula Sapiens, TCGA, brain atlas), the human '
    'gene column is used. The CKI package also supports data-driven auto-detection via '
    'detect_housekeeping_genes() (combined criterion: detection rate > 0.9 and CV < 30th '
    'percentile, use_reference = False), but all reported analyses use the pre-specified '
    'HRT Atlas reference. Sensitivity analysis indicates that CKI results are robust to HK set '
    'selection: using the top 10% lowest-variance genes as an alternative constrained set '
    'yields \u03c9 correlations of r > 0.95.'
)

add_para('1.3 Functional Divergence Rate k_f', bold=True)
add_para(
    'Identity genes I are defined as genes that capture cell-type-specific functional '
    'programs. In the default configuration (w1 = 1.0, w2 = 0.0), I consists of the '
    'top-N highly variable genes (HVG), excluding HK genes. The functional divergence '
    'rate is: k_f = JS(norm(\u03bc_A[I]), norm(\u03bc_B[I])). Extended configurations '
    'can incorporate additional gene sets: (1) regulon activity genes \u2014 genes enriched '
    'for cell-type-specific transcription factor motifs; (2) pathway enrichment genes '
    '\u2014 genes from MSigDB pathways differentially active between the two groups; '
    '(3) macro-gene embeddings \u2014 gene-level embeddings from protein language models '
    '(e.g., ESM-2). These extensions use a weighted formulation: '
    'k_f = w1*JS(HVG) + w2*JS(pathway) + w3*JS(macro). Parameter sweep (Phase 3.2) '
    f'showed that the pure identity gene configuration (w1=1.0, w2=w3=0.0) achieved '
    f'optimal cell type discrimination (AUC = {DATA["sweep"]["identity_auc"]:.3f}, n = {DATA["sweep"]["n_pairs"]:,} '
    f'mouse cell-type pairs); this was therefore adopted as '
    'the default scheme (a gene-set configuration criterion only; CKI itself '
    'is not designed for cell-type discrimination\u2014see the main-text '
    'Discussion).'
)

add_para('1.4 Omega Ratio and Its Interpretation', bold=True)
add_para(
    '\u03c9 = k_f/k_n. Interpretation is anchored in the empirical \u03c9 distribution '
    'within each dataset rather than in fixed ratio cut-offs: values close to the '
    'equivalent-population calibration baseline are consistent with baseline '
    'expectation, with no evidence of functional reprogramming; values far above the '
    'baseline indicate functional divergence exceeding baseline drift, i.e. evidence of '
    'functional transcriptional reprogramming beyond baseline; values far below the '
    'baseline indicate functional constraint, the two groups being more similar in '
    'functional genes than expected from baseline drift (rare in practice). '
    'The Ka/Ks analogy is structurally similar but mathematically non-equivalent, '
    'and the correspondence is threefold: synonymous-site divergence (Ks) '
    'corresponds to HK-gene divergence (k_n), nonsynonymous divergence (Ka) to '
    'functional-gene divergence (k_f), and a species pair to the two cell '
    'populations compared (main-text Discussion), with a constrained rather than '
    'neutral reference class; completing the McDonald\u2013Kreitman-style contrast, '
    'the split-half calibration baseline (within-population \u03c9 \u2248 7.70) '
    'stands in for the polymorphism class, so \u03c9_cal = \u03c9/7.70 parallels '
    'the reciprocal of the neutrality index (the \u03b1-direction of the McDonald\u2013Kreitman '
    'contrast) and inherits its caveats; the split-half denominator measures '
    'within-population sampling and technical variability rather than standing '
    'between-individual variation, so it is a lower bound on the polymorphism '
    'class and \u03c9_cal is biased upward accordingly. '
    'The inversion is structural rather than incidental: in Ka/Ks the denominator '
    '(Ks) is a putatively neutral standard, whereas the HK anchor is itself the most '
    'strongly constrained expression class\u2014as if synonymous sites were selected '
    'along one lineage, where dN/dS loses its interpretation. The TCGA pan-cancer '
    'reversal, in which the denominator shifts 1.3\u20133.3-fold with disease state, '
    'is the empirical demonstration of that failure mode; the per-class split-half '
    'baselines (a 1.65-fold spread) are the analogue of dS varying across lineages, '
    'handled in molecular evolution by branch models and here by per-class '
    'calibration. Sensitivity analysis with alternative low-variance gene sets '
    '(r > 0.95) partially mitigates the empirical-definition concern; CKI also '
    'lacks a formal phylogenetic framework (e.g., Ornstein-Uhlenbeck models). '
    'Key differences: (1) Ka/Ks operates on sequence alignments with explicit codon '
    'models, while CKI operates on continuous expression vectors; (2) the neutral '
    'reference in Ka/Ks has a mechanistic basis in the genetic code (synonymous changes '
    'are assumed neutral), whereas HK genes in CKI are empirically defined; (3) Ka/Ks '
    'uses explicit evolutionary models (e.g., PAML), while CKI uses empirical permutation '
    'inference; (4) Ka/Ks counts all nonsynonymous sites, whereas the k_f numerator is '
    'computed on a per-pair top-200 selection of the most diverged genes\u2014an '
    'ascertainment asymmetry on the Ka side (in MK terms, counting only the amino-acid '
    'sites already known to differ), quantified by the circularity analyses '
    '(median inflation 1.61\u00d7; leave-pair-out \u03c1 = 0.92\u20130.94; \u03c9 as '
    'upper bound; Supplementary Note 7) and handled statistically by the '
    'gene-reselecting permutation nulls.'
)

add_para('1.5 Permutation Test', bold=True)
add_para(
    'Statistical inference is performed by generating a null distribution of \u03c9 '
    'under the null hypothesis that the group labels are exchangeable between the two '
    'cell populations. Procedure: (1) Annotate all cells in the pooled dataset with their '
    'original group labels (A or B); (2) Randomly permute group labels B times '
    '(B=1,000): cell labels for mouse and human, sample (tumor/normal) labels for TCGA; '
    'for the brain atlas the authoritative null is the library-to-region block-shuffle '
    'permutation rather than label permutation; pseudobulk vectors and omega_null are '
    'recomputed each time, with the top-N identity genes re-selected on the permuted '
    'pseudobulks in the mouse, human, and brain pipelines, while the TCGA per-cancer '
    'permutation test holds a fixed HVG panel across permutations (anti-conservative relative '
    'to re-selection); '
    '(3) Empirical P-value (one-sided): '
    'P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1), with the '
    '+1 term avoiding P = 0; (4) Effect size: SES = (omega_obs - '
    'mean(omega_null))/sd(omega_null). Benjamini-Hochberg FDR correction is '
    'applied within each dataset to control the false discovery rate. '
    'Because the test is one-sided, rejection at a given alpha is decided '
    'directly by the empirical P-value (P < alpha); no separate two-sided '
    'critical values are derived from the null distribution, and the null '
    'quantiles are not confidence intervals for \u03c9 itself. '
    'Permutation testing was performed for all four datasets: label permutation for the '
    'mouse pilot (15 cell-type pairs), human Tabula Sapiens, and TCGA (B=1,000 each), and '
    'the block-shuffle null for the brain atlas (B=1,000). For the larger-scale analyses, results are supplemented with non-parametric '
    'statistical tests (Spearman correlation, Mann-Whitney U, Kruskal-Wallis, '
    'Jonckheere-Terpstra) and descriptive statistics.'
)

add_para('1.6 Pseudobulk Construction', bold=True)
add_para(
    'Raw count matrices X (cells x genes) are preprocessed as follows: '
    '(1) Library size normalization: X_norm = 10,000 * (X/colSums(X)); '
    '(2) log1p transformation: X_log = log1p(X_norm), stabilizing variance and reducing '
    'the influence of high-expression outliers; (3) Pseudobulk: mu = column-wise mean '
    'of X_log for all cells with the same cell type annotation, with a minimum of 20 '
    'cells per group. For TCGA bulk RNA-seq data, TPM normalization is used instead: '
    'TPM values from UCSC Xena, followed by log2(TPM + 1) transformation. No pseudobulk step '
    'is needed as each sample is already a bulk expression profile.'
)

add_para('1.7 Probability-Mapping Robustness: Linear-Normalization Re-analysis of the TCGA Pipeline', bold=True)
add_para(
    'Disclosure. All TCGA statistics reported in the manuscript are computed under the '
    'strictly linear probability mapping p_i = (TPM + 1)/\u03a3(TPM + 1), which is the '
    'authoritative caliber throughout (notebooks/85_tcga_linear_norm_v44.py; per-cancer '
    'streaming gene loading, mean TPM \u2265 0.5 filtering, per-cancer HK mapping, '
    'per-pair top-200 |\u0394| identity genes ranked on the log2(TPM + 1) '
    'representation so that the identity gene sets are unchanged, kn_floor = 1 \u00d7 '
    '10\u207b\u2074, seed 42, TT/TN caps of 2,000 pairs). The legacy pipeline '
    '(notebooks/06_phase34_v2.py) applied the softmax probability mapping to '
    'log2(TPM + 1) values, which is mathematically equivalent to the power '
    'transformation p_i \u221d (TPM + 1)^(1/ln 2) (Section 1.1); the softmax-caliber '
    'values are archived here as a sensitivity analysis to verify that the mapping '
    'choice drives no conclusion (Supplementary Table 5). Scripts: '
    'notebooks/85_tcga_linear_norm_v44.py '
    '(linear-normalization pair table) with the v52 ex-CC default chain '
    'notebooks/nc52_tcga_excc_main.py (main pipeline and clinical '
    'severity; outputs results/nc52_tcga_pancancer_excc.csv, '
    'results/nc52_tcga_excc_severity.csv) and '
    'notebooks/nc52_tcga_composition_excc.py '
    '(composition sensitivity; results/nc52_tcga_composition_excc.{csv,txt}); '
    'the softmax-caliber sensitivity used notebooks/nc52_tcga_softmax_pairs.py '
    'and notebooks/nc52_tcga_mapping_schemes.py '
    '(results/nc52_tcga_softmax_all_pairs.csv, '
    'results/nc52_tcga_mapping_schemes_table.csv); '
    'report: results/tcga_linear_norm_v44_report.md.'
)
add_table([
    ['Cancer type', 'NN/TT \u03c9 (linear) [95% CI]', 'CI excl. 1',
     'NN/TT \u03c9 (softmax) [95% CI]', 'CI excl. 1'],
    ['LUAD', '2.464 [2.128, 2.863]', 'yes', '2.620 [2.265, 3.042]', 'yes'],
    ['LUSC', '1.708 [1.378, 2.087]', 'yes', '1.885 [1.508, 2.294]', 'yes'],
    ['LIHC', '1.112 [0.943, 1.302]', 'no', '1.286 [1.091, 1.533]', 'yes'],
    ['KIRC', '1.880 [1.638, 2.148]', 'yes', '2.046 [1.760, 2.335]', 'yes'],
    ['BRCA', '1.567 [1.342, 1.815]', 'yes', '1.748 [1.511, 2.009]', 'yes'],
])
si_caption(
    'Supplementary Table 5. Two-caliber NN/TT \u03c9 reversal table (ex-CC '
    'cohort, v52). Mean NN/TT \u03c9 ratio with sample-level cluster-bootstrap '
    '95% CI (B = 1,000, seed 42) under the authoritative linear probability '
    'mapping and the legacy softmax mapping. The reversal direction is '
    'preserved in 5 of 5 cancer types under both calibers; the count of CIs '
    'excluding 1 is mapping-sensitive only through LIHC (four of five linear, '
    'five of five softmax), so the main-text "four of five" statement is '
    'conservative. Floor sensitivity: k_n floor settings 0, 1 \u00d7 '
    '10\u207b\u2075, and 1 \u00d7 10\u207b\u2074 leave every ratio identical '
    '(no pair-level k_n falls in (0, 10\u207b\u2074); '
    'results/nc52_tcga_knfloor_sensitivity.csv), while 1 \u00d7 10\u207b\u00b3 '
    'truncates ~50% of NN pairs and attenuates the reversal (LUAD 2.464 '
    '\u2192 1.494; BRCA below 1), quantifying the floor dependence; all '
    'three clinical-severity orderings are preserved (full values in '
    'Supplementary Note 9), and the composition-sensitivity conclusion is '
    'unchanged (pooled tumor-pair coefficient attenuation \u22120.9%, '
    'cluster-bootstrap median \u22120.8% [95% CI \u22124.3%, +2.5%] at '
    'B = 1,000; Supplementary Note 8).'
)

doc.add_page_break()

# ===== SN2: Algorithm Pseudocode =====

add_heading('CKI Algorithm Pseudocode', 2)
add_para('Algorithm 1: CKI Core Computation', bold=True)
add_para(
    'Input: Two cell populations A and B (expression matrices), HK gene set H, '
    'identity gene set I (default top-N HVG excluding H). '
    'Output: \u03c9, P-value, SES, null distribution.'
)
pseudo = [
    ' 1. X_A, X_B <- library-normalize and log1p-transform A and B',
    ' 2. mu_A <- mean(X_A, axis=0); mu_B <- mean(X_B, axis=0)  // pseudobulk',
    ' 3. mu_A_H <- mu_A[H]; mu_B_H <- mu_B[H]',
    ' 4. k_n <- JS_divergence(norm(mu_A_H), norm(mu_B_H))  // norm: softmax over log1p counts, i.e., p_i = exp(log1p(c_i)) / sum_j exp(log1p(c_j)) = (c_i+1) / sum_j (c_j+1)',
    ' 5. mu_A_I <- mu_A[I]; mu_B_I <- mu_B[I]',
    ' 6. k_f <- JS_divergence(norm(mu_A_I), norm(mu_B_I))',
    ' 7. if (bulk RNA-seq analysis) and k_n < 1e-4: k_n <- 1e-4  // TCGA-only floor; single-cell analyses apply no floor',
    ' 8. omega <- k_f / k_n',
    ' 9. // Permutation test',
    '10. labels <- concatenate([A]*n_A, [B]*n_B)  // for bulk RNA-seq, one label per sample',
    '11. for b = 1 to B (B = 1,000 for all datasets):',
    '12.     labels_perm <- random_permutation(labels)',
    '13.     mu_perm1 <- mean(pooled[labels_perm[:n_A]], axis=0); mu_perm2 <- mean(pooled[labels_perm[n_A:]], axis=0)',
    '14.     I_b <- top-N identity genes selected on (mu_perm1, mu_perm2)  // re-selected at every permutation',
    '15.     omega_null[b] <- CKI_core(mu_perm1, mu_perm2, H, I_b)',
    '16. // Inference (one-sided permutation test)',
    '17. P <- (count(omega_null >= omega_obs) + 1) / (B + 1)',
    '18. d <- (omega - mean(omega_null)) / sd(omega_null)',
]
for line in pseudo:
    p = add_para(line)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(0)

add_para(
    'Note: in the released cki package (v0.5.2), bootstrap_test() reproduces lines 9-15 '
    'by default (reselect_identity = True): the HK set H is resolved once before the '
    'permutation loop and held fixed, while the k_f gene set is re-selected at every '
    'permutation (and for the observed value) as the top 200 non-HK genes by absolute '
    'pseudobulk difference, so the null incorporates the gene-selection step; this is '
    'the label-permutation procedure reported for the mouse pilot and Tabula Sapiens '
    'analyses. Passing explicit identity gene sets, or reselect_identity = False, pins '
    'a fixed panel across permutations (legacy mode; anti-conservative relative to '
    're-selection whenever the observed \u03c9 uses per-pair selection). The TCGA '
    'per-cancer permutation test deliberately held a fixed identity panel across '
    'permutations (anti-conservative relative to re-selection; see 1.5 Permutation '
    'Test), and the brain analysis uses a library-level block-shuffle null '
    '(cki.blocknull.block_shuffle_test) instead of label permutation.'
)
add_para('')
add_para('Algorithm 2: Pairwise Identity Gene Selection (Tabula Sapiens Extension)', bold=True)
add_para(
    'Unlike the Tabula Muris full pairwise matrix (global HVG set for Fig. 2), Tabula Sapiens and all pilot analyses (mouse calibration, human, TCGA, brain) employ pairwise identity '
    'gene selection to avoid dilution of HVG across 102 cell types.'
)
pseudo2 = [
    'Input: Pseudobulk vectors mu_A, mu_B; HK set H; top-N parameter N (default 200)',
    '1. Delta <- |mu_A - mu_B|  // per-gene absolute expression difference',
    '2. I <- indices of top-N genes ranked by descending Delta, excluding H',
    '3. k_f <- JS(norm(mu_A[I]), norm(mu_B[I]))',
    '',
    'Note: k_n uses the global HK set (same for all pairs); k_f uses pairwise top-N genes.',
]
for line in pseudo2:
    p = add_para(line)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(0)

doc.add_page_break()

# ===== SN3: Statistical Testing =====

add_heading('Statistical Testing Details', 2)

add_para('3.1 Tests Performed and Correction Strategy', bold=True)
add_para(
    'The following statistical tests were used in this study: Mann-Whitney U test '
    '(two-sided) for independent comparisons between two groups; Kruskal-Wallis test '
    'for multi-group comparisons (e.g., BRCA PAM50 subtypes); Jonckheere-Terpstra trend '
    'test for ordered categorical variables (e.g., LIHC Edmondson grade); Spearman rank '
    'correlation for correlations between metrics; Permutation test (B=1,000) '
    'for CKI \u03c9 significance inference; ROC-AUC for benchmark performance '
    'assessment (parameter sweep and functional-change detection).'
)

add_para('3.2 Permutation Test and Bootstrap CI Details', bold=True)
add_para(
    'Permutation iterations: B=1,000 for all datasets (mouse pilot study with '
    '15 cell-type pairs, human Tabula Sapiens via script 08b, TCGA via script 08a, '
    'and brain atlas via scripts 08d-08e, which implement the block-shuffle null). '
    'Permutation testing was performed '
    'for all four datasets. Benjamini-Hochberg FDR correction is '
    'applied within each dataset to control the false discovery rate. '
    'For the calibration '
    'experiment, empirical P-values '
    'are computed as: P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1). '
    'Standardized effect size = (\u03c9_obs - mean(\u03c9_null)) / sd(\u03c9_null).'
)
add_para(
    'Bootstrap confidence intervals (95% CI) for all key \u03c9 estimates were '
    'computed by pair-level resampling with B=10,000 iterations. For each cell '
    'type, observed pair-level \u03c9 values were resampled with replacement and the '
    'mean was computed; the 2.5th and 97.5th percentiles of the resulting '
    'distribution define the 95% CI. A region-clustered block bootstrap (B = 2,000; the 108 '
    'regions resampled with replacement, all statistics recomputed per resample) yields wider, '
    'cluster-aware intervals for landscape-level quantities: gradient 6.10 [5.55, 9.63], '
    'grand mean \u03c9 38.55 [36.35, 40.73], Strong-candidate count 39 [12, 74]. '
    'Confidence interval widths scale inversely '
    'with the number of contributing pairs: well-sampled cell types (e.g., '
    f'astrocytes, 5,778 pairs) yield narrow intervals ([{_ci_astro[1]:.2f}, {_ci_astro[2]:.2f}], '
    f'mean {_ci_astro[0]:.2f}), whereas cell types with fewer comparisons '
    f'(e.g., Bergmann glia, 21 pairs) produce wider intervals '
    f'([{_ci_berg[1]:.2f}, {_ci_berg[2]:.2f}], mean {_ci_berg[0]:.2f}).'
)

add_para('3.3 Multiple Testing Correction', bold=True)
_bs = _br['bs_null']
add_para(
    'Permutation testing was performed for all four datasets with B=1,000: '
    'mouse pilot (15 cell-type pairs), human Tabula Sapiens, TCGA, and '
    'brain atlas. Benjamini-Hochberg FDR correction is applied within each '
    'dataset to control the false discovery rate, with the number of tests '
    'defined at the level at which each analysis is performed. For the human '
    f'atlas, {_h["n_ct_analyzed"]} of 102 cell-type entries passed the pairwise-analysis filters '
    f'(at least 20 cells per entry and a donor with at least 10 cells), yielding '
    f'C({_h["n_ct_analyzed"]}, 2) = {_h["n_pairs_total"]:,} pairs; for the brain atlas, 31,764 '
    'same-cell-type cross-region pairs were tested. For the larger-scale analyses, permutation results '
    'are supplemented with non-parametric '
    'statistical tests and descriptive statistics (median, IQR, effect sizes). For TCGA stratified '
    'analyses (BRCA PAM50, LIHC Edmondson) involving 4-5 groups, omnibus tests '
    '(Kruskal-Wallis, Jonckheere-Terpstra) are used. Effect sizes are reported alongside '
    'all significance statements to distinguish statistical significance from biological '
    'magnitude.'
)
add_para(
    f'For the brain region-association screen, per-pair empirical P-values were computed with a '
    f'block-shuffle permutation null (B = {_bs["B"]:,}), in which 10x Chromium libraries '
    '(sample_id) were treated as blocks and the library-to-region assignment was randomly permuted '
    '(preserving the observed per-region library-count structure), after which region pseudobulks, all '
    f'31,764 pair \u03c9 values, and multiplicative residuals were recomputed. The one-sided lower-tail '
    f'P-value is P = (count(\u03c9_null \u2264 \u03c9_obs) + 1)/(B + 1); the complementary upper-tail P-value '
    f'P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1) was also computed for every pair, and both tails are '
    f'reported here. Of the {_br["n_strong"]} Strong-tier candidates '
    f'(residual < 0.3), {_br.get("n_significant", 31)} showed raw P < 0.05, but after Benjamini-Hochberg '
    f'correction across all m = 31,764 pairs, none reached q < 0.05 (minimum q = {_br["min_q_fdr"]:.3f}). '
    f'Globally, {_bs["n_p_lt_05"]:,} of 31,764 pairs (6.2%) showed raw lower-tail P < 0.05, above the '
    f'permutation null mean of 1,588 and beyond its 99th percentile (1,956): calibrated against the '
    f'design-matched null distribution of the count itself, this excess is significant (P = 0.011; 0.022 '
    f'after Bonferroni correction across the two tails tested), and it is contributed chiefly by classes '
    f'whose mean \u03c9 sits below the null expectation\u2014microglia (8.06% of class pairs at lower-tail '
    f'P < 0.05, +173 pairs above the 5% null rate), oligodendrocytes (6.01%, +58), and Bergmann glia '
    f'(8 of 21 pairs, 38.1%, the family nominally significant under stratified BH)\u2014but also by '
    f'astrocytes (7.60%, +150 pairs), whose wide, right-skewed \u03c9 distributions generate pairs far '
    f'below the null even though the class mean lies far above it. The complementary upper tail '
    f'was also tested and shows a clear excess in the opposite direction: '
    f'{_bs.get("n_p_high_lt_05", 2510):,} pairs ({_bs.get("pct_p_high_lt_05", 7.9):.1f}%) had upper-tail '
    f'P < 0.05 (observed \u03c9 above the block-shuffle null), concentrated in the most regionally structured '
    f'classes (astrocytes 16.2%, committed OPCs 9.7%, OPCs 9.6% of class pairs; Bergmann glia 0%). The '
    f'two-sided excesses are the pair-level signature of the same regional structure detected at the '
    f'cell-class level\u2014classes with upward-shifted \u03c9 distributions contribute the upper-tail excess, '
    f'while the lower-tail excess, though concentrated in the below-null classes, also draws a nearly equal '
    f'contribution from the wide astrocyte distribution\u2014and the lower-tail excess in aggregate is not '
    f'evidence for anomalously low-\u03c9 pairs beyond what the class-level shifts predict '
 f'(rule-matched null caveat on reading these tail excesses: Supplementary Note 13). '
    'The null FDR outcome for the candidate screen is structural rather than purely empirical: with m = 31,764 tests, '
    'the BH threshold for the smallest ordered P-value (0.05/31,764 \u2248 1.6 \u00d7 10\u207b\u2076) lies roughly '
    '600-fold below the smallest resolvable permutation P (9.99 \u00d7 10\u207b\u2074 at B = 1,000), so '
    'q < 0.05 would require either B \u2248 6 \u00d7 10\u2075 permutations or at least ~635 of the 31,764 '
    'P-values at the permutation floor\u2014neither condition is approached in these data, as the '
    'selection-rule analysis quantifies (the null alone would pass the complete '
    'Strong rule 148.3 times in expectation, 3.8-fold above the 39 observed candidates; for the rule '
    'restricted to raw P < 0.05 the null expectation of 131.2 exceeds the observed 31 4.2-fold). '
    'We therefore report the Strong candidates as a prioritized hypothesis-generating list rather than '
    'FDR-controlled discoveries. An earlier implementation of this test, which shuffled cell-type '
    'labels within each region pair (B = 10,000), produced anti-conservative P-values (36.3% of pairs at '
    'the P-value floor) because per-pair shuffling ignores the block structure of 10x libraries; that '
    'implementation was superseded by the block-shuffle null reported here. Per-signal tests are not '
    'independent (the same cell type or region pair appears in multiple comparisons); interpretation is '
    'therefore restricted to the predefined Strong tier. (Supplementary Fig. 12: \u03c9 distribution '
    'characterization; Supplementary Fig. 9: block-shuffle null distribution for the residual model.)'
)

add_para('3.4 Reporting Conventions', bold=True)
add_para(
    'Summary statistics are reported as mean +/- standard deviation (range) or median '
    '[interquartile range]. Boxplots display: median (center line), IQR (box), '
    '1.5x IQR (whiskers), with data points beyond the whiskers shown as outliers. '
    'All P-values from non-permutation tests are two-sided; permutation '
    'P-values are one-sided (see Section 1.5). Correlation '
    'coefficients (Spearman rho) are reported with P-values. Effect sizes (standardized effect size, SES = (\u03c9_obs \u2212 \u03bc_null) / \u03c3_null) '
    'are reported as descriptive measures of magnitude; because the \u03c9 distribution '
    'is right-skewed and non-normal for the large datasets (brain: D\u2019Agostino-Pearson '
    f'P < 2.2 \u00d7 10\u207b\u00b9\u2076; human: Shapiro-Wilk P = {_norm_human_p:.1e}; the mouse pilot at n = 15 '
    f'pairs does not reject normality, Shapiro-Wilk P = {_norm_mouse_p:.3f}), SES should be '
    'interpreted as a '
    'non-parametric descriptive statistic rather than a parametric test result.'
)

add_para('3.5 Pair-Specific k_n Variability', bold=True)
add_para(
    'In all reported analyses (mouse pilot, human, TCGA, and brain), k_n is computed '
    'per pair on the shared HK gene set: for each comparison, the HK-gene JS divergence '
    'between the two pseudobulk vectors is evaluated on that pair alone (a single HK '
    'reference is shared across all pairs, keeping k_n on a consistent scale, but the '
    'divergence itself is pair-specific). '
    f'Analysis of per-pair k_n across {_kn_overall["n_pairs"]:,} brain comparisons revealed substantial cross-pair '
    f'variability: overall k_n CV = {_kn_overall["kn_cv"]:.2%} (mean = {_kn_overall["kn_mean"]:.4f}, median = {_kn_overall["kn_median"]:.4f}), with per-cell-type '
    f'CVs ranging from {_kn_cv_lo[1]["kn_cv"]:.1%} ({_kn_cv_lo[0].lower()}s) to {_kn_cv_hi[1]["kn_cv"]:.1%} ({_kn_cv_hi[0].lower()}s). '
    'As a sensitivity analysis, we contrasted this per-pair k_n estimator with a global-k_n '
    'variant (k_n computed once from the full gene-by-cell-type pseudobulk matrix): the Spearman '
    f'correlation between the resulting \u03c9 rankings was only \u03c1 = {_kn_rho:.3f} (P = {_kn_rho_p:.2e}), so the '
    'global-k_n simplification would preserve only ~2% of the variance in \u03c9 orderings '
    '(\u03c1\u00b2 \u2248 0.02). This justifies the per-pair k_n approach used throughout and '
    'highlights that fine-grained \u03c9 orderings should be interpreted with the estimator '
    'choice in mind. (Supplementary Fig. 7.)'
)

add_para('3.6 TCGA Exploratory Analysis Caveats', bold=True)
add_para(
    'The TCGA pan-cancer analysis (Results Section: Cancer analysis) is exploratory in nature '
    'due to several inherent limitations of bulk RNA-seq data. First, bulk RNA-seq confounds '
    'cell-composition shifts (tumor purity, stromal infiltration, immune cell infiltration) '
    'with genuine transcriptional divergence; the observed NN/TT > 1.0 pattern may partly '
    'reflect shared cell-composition changes across tumors rather than true transcriptional '
    'convergence. Second, peritumoral inflammation and desmoplastic reactions are shared '
    'across tumors and could contribute to apparent convergence. Third, systematic RNA quality '
    'differences between tumor and normal specimens may introduce technical bias. Fourth, '
    'the paired tumor-normal analysis (n = 2-5 per cancer type) lacks statistical power for '
    'formal hypothesis testing (minimum two-sided P approx 0.33 for n = 2); we therefore '
    'report paired comparisons as descriptive statistics only. Fifth, PAM50 and Edmondson '
    'stratification includes small subgroups (Normal-like n = 7; Edmondson G4 n = 11) whose '
    'rankings are unreliable. Sixth, the PAM50 gradient (aggressive subtypes have lower \u03c9) '
    'may be driven by proliferative fraction differences rather than shared transcriptional '
    'states. These caveats do not invalidate the descriptive findings but preclude causal '
    'inference from bulk-level data alone.'
)

add_para('3.7 Cross-Organ Sample Size Considerations', bold=True)
add_para(
    'The cross-organ conservation ranking (Results Section: CKI ranks cell types by cross-organ '
    'conservation) includes cell types with varying numbers of cross-organ pairs. Several cell '
    'types have very few pairs (n = 1-3; e.g., Memory B cells n = 1, Smooth muscle n = 1), '
    'making their mean \u03c9 estimates unreliable. We recommend interpreting rankings of cell '
    'types with n < 5 as suggestive only. Bootstrap 95% confidence intervals for cell types '
    'with n \u2265 5 are provided in Supplementary Table 2. The Spearman correlations between '
    'CKI \u03c9 and standard metrics are reported with bootstrap 95% CIs (B = 10,000 resamples).'
)

add_para('3.8 One-Sided Permutation Test Justification', bold=True)
add_para(
    'All permutation P-values use a one-sided test: P = (count(omega_null \u2265 omega_obs) + 1)/(B + 1). '
    'The one-sided formulation is appropriate because our hypothesis is directional: we test '
    'whether observed \u03c9 exceeds the null expectation (equivalent populations), not whether '
    'it differs in either direction. A two-sided test would be appropriate if we were testing '
    'for any departure from the null (either elevated or suppressed \u03c9). However, the '
    'biological questions addressed here (functional divergence exceeding baseline, Strong '
    'region-associated candidates showing anomalously low \u03c9) are inherently directional. '
    'One exception: the brain per-pair candidate screen uses the one-sided lower-tail '
    'formula P = (count(omega_null \u2264 omega_obs) + 1)/(B + 1), because region-associated '
    'candidates are defined by anomalously low \u03c9; the complementary upper-tail '
    'P-value is computed for every pair and both tails are reported. In the released '
    'cki package (v0.5.2), the tested tail is selected by the tail parameter of '
    'bootstrap_test() and block_shuffle_test() (tail = "upper", "lower", or '
    '"two-sided"); earlier releases used the parameter name "direction".'
)

add_para('3.9 Parameter Justification', bold=True)
add_para(
    'Key CKI parameters and their rationale: (1) +1 pseudo-count followed by L1 '
    'normalization: converts expression vectors to probability distributions for JS '
    'divergence computation; adding one pseudo-count before L1 normalization preserves '
    'relative magnitude information while ensuring non-negativity and sum-to-one. '
    '(2) Zero entries are excluded from the JS divergence by explicit masking '
    '(p > 0, q > 0); the constant _EPS = 1e-9 is used only as a softmax denominator '
    'guard and never enters k_n, k_f, or \u03c9. (3) Identity-gene sets for k_f: two schemes are used '
    '\u2014 a global panel of the top-2,000 highly variable genes (HVGs; Seurat flavor, HK '
    'excluded) for the Tabula Muris full pairwise matrix, and per-pair top-200 DE genes '
    '(ranked by absolute mean difference, HK excluded) for the mouse pilot, Tabula '
    'Sapiens, TCGA, and brain analyses; the Phase 3.2 sweep varied the identity/pathway '
    'weighting at the fixed 2,000-HVG panel and found the identity-only configuration '
    'optimal for AUC (Supplementary Table 1). (4) Gene-set sizes by dataset: 2,000 HVGs '
    '(Scanpy default) for the mouse matrix; the brain pipeline retains the top-5,000 '
    'non-HK genes by global mean expression; a diagnostic HVG-size sweep on Tabula '
    'Sapiens (N_HVG in {2,000, 5,000, 10,000, 20,000}; notebooks/05b_phase33_diagnose.py) '
    'informed these choices. (5) Log-base 2 for JS divergence: standard choice giving JS '
    'range [0, 1]; the base does not affect \u03c9 = k_f/k_n since it cancels in the ratio. '
    '(6) B = 1,000 for permutation: justified by adaptive permutation analysis showing minimum '
    'P = 9.99 \u00d7 10\u207b\u2074 (= 1/(B+1) = 1/1001) is well below BH thresholds for cell-type-level tests (Phase B).'
)

add_para('3.10 Mouse Split-Half Re-calibration (6 \u2192 50 splits)', bold=True)
add_para(
    'The equivalent-population calibration of Supplementary Note 3 was re-run with 50 '
    'independent random split-halves per control population (the same six FACS '
    'control populations as the original calibration: liver hepatocyte, heart '
    'endothelial, spleen B cell, marrow B cell, heart fibroblast, marrow '
    'neutrophil; 300 split-half \u03c9 values; identical QC, normalization, and '
    'k_n/k_f definitions; script notebooks/87_mouse_splithalf_v44.py; outputs '
    'results/mouse_splithalf_v44.csv and results/mouse_splithalf_v44_summary.json; '
    'seed 42). The replicate baseline stabilizes at mean \u03c9 = 7.70 '
    '(SD of replicate means 1.15, pooled SD 3.63). Because the 300 split-half '
    'values are nested within only six populations, intervals treating them as '
    'independent ([7.37, 8.02] by t-interval, [7.38, 8.02] by bootstrap '
    'with B = 10,000) are pseudo-replicated and anti-conservative; the '
    'preferred interval is a two-stage bootstrap (B = 5,000, seed 42) that '
    'resamples the six populations first and the 50 split-half values within '
    'each drawn population second: 95% CI [6.38, 9.82] (six-population-mean '
    't-interval [5.18, 10.21]; leave-one-population-out range 6.75\u20138.08), '
    'superseding both the pseudo-replicated intervals and the legacy '
    'single-split estimate 6.67 [4.24, 9.24]. Per-population '
    'means (50 splits each): hepatocyte 12.44 \u00b1 5.98, marrow B cell '
    '7.36 \u00b1 1.39, heart endothelial 7.23 \u00b1 1.59, heart fibroblast '
    '7.00 \u00b1 1.73, spleen B cell 6.38 \u00b1 0.93, marrow neutrophil '
    '5.77 \u00b1 2.67. The calibration constant used throughout this revision '
    'is therefore 7.70 [6.38, 9.82]; qualitative calibrated-\u03c9 conclusions '
    'are unchanged (e.g., brain grand mean 38.5 \u2192 \u03c9_cal \u2248 '
    '5.0\u20135.8 under either baseline), but the widened interval '
    '(\u00b121% relative half-width) limits \u03c9_cal to roughly one decimal '
    'of resolution: \u03c9_cal = 1 is induced by any baseline in [6.38, 9.82] '
    'dividing 7.70, so \u03c9_cal differences below ~0.1\u20130.2 are not '
    'meaningful.'
)


add_para(
    'Leave-one-population-out sensitivity. Removing each control population in '
    'turn moves the 50-split baseline within 6.75\u20138.08 '
    '(median-of-population-means 7.12); removing hepatocyte lowers it to 6.75 '
    '(\u221212.3%). All ratio statements are baseline-invariant, but absolute '
    '\u03c9_cal magnitudes shift by up to 14% under the outlier-free baseline '
    '(Bergmann glia \u03c9_cal 1.76 \u2192 2.01; astrocytes 10.75 \u2192 12.26).'
)
add_para('3.11 Competitor Benchmark: MELD and a Python Approximation of scDist', bold=True)
add_para(
    'Purpose and methods. CKI was benchmarked against MELD (PyPI meld 1.0.2, '
    'minimal --no-deps install; per-cell-type score = within-type AUC of the '
    'stim-versus-control likelihood) and against a Python approximation of '
    'scDist (the R package was unavailable in our environment; per cell type, '
    'per-PC OLS of PC score on condition plus donor fixed effects, cell-type '
    'distance = \u221a(\u03a3_j \u03b2\u00b2_cond,j \u03bb_j) over 20 PCs of '
    'log-normalized 3,000 HVGs). The scDist implementation reproduces the '
    'fixed-effects condition-coefficient distance of Mitsakos et al. 2023 but '
    'is not the R package\u2019s exact implementation and is labelled "Python '
    'approximation of scDist" throughout. Script: '
    'notebooks/101_competitors_v44.py; report: results/competitors_v44_report.md; '
    'seed 42; at least 20 replicates for every simulation and power number.'
)
add_para(
    'Kang IFN-\u03b2 real data (GSE96583; same design as Supplementary Note 6). All three '
    'methods agree on direction in 6 of 6 cell types (every type shows '
    '\u03c9_cal > 1 and MELD within-type AUC > 0.5). The IFN-\u03b2 effect is '
    'near-ceiling, so MELD AUCs saturate (0.997\u20130.9998) with almost no '
    'dynamic range, while the scDist-approximation distances span '
    '71.9\u2013182.6 (CD14+ monocytes highest). Per-type quantitative rankings '
    'are not comparable across methods (Spearman: CKI\u2013MELD \u03c1 = '
    '\u22120.09, P = 0.87; CKI\u2013scDist \u03c1 = 0.14, P = 0.79; '
    'MELD\u2013scDist \u03c1 = 0.77, P = 0.07); CKI\u2019s \u03c9_cal spread '
    '(1.76\u20133.44) reflects anchor visibility rather than effect size '
    '(Supplementary Table 6).'
)
add_table([
    ['Cell type', 'n cells', 'CKI \u03c9_cal', 'MELD within-type AUC',
     'scDist-approx distance'],
    ['B cells', '2,573', '3.44', '0.9994', '94.7'],
    ['CD14+ monocytes', '5,385', '2.28', '0.9998', '182.6'],
    ['CD4 T cells', '10,389', '1.76', '0.9989', '71.9'],
    ['CD8 T cells', '2,042', '3.23', '0.9976', '72.4'],
    ['FCGR3A+ monocytes', '1,599', '3.09', '0.9995', '145.3'],
    ['NK cells', '1,993', '2.88', '0.9972', '88.2'],
])
si_caption(
    'Supplementary Table 6. Per-cell-type effects on Kang IFN-\u03b2 '
    '(stimulated versus control). \u03c9_cal is calibrated against the '
    'split-half baseline of Supplementary Note 6.'
)
add_para(
    'Simulation with known ground truth (Kang control background; additive '
    'Poisson mean-shift on G \u2208 {100, 500} non-HK genes in CD14+ '
    'monocytes, fold \u2208 {2, 4, 8}; 20 effect plus 20 pure-null replicates '
    'per configuration; thresholds at the null q95, FPR on held-out nulls). '
    'MELD and the scDist approximation achieve perfect detection at every '
    'configuration (sensitivity 1.00, AUC 1.000; per-type FPR 0.033 and '
    '0.050), while CKI \u03c9 is insensitive at G = 100 (AUC 0.52 \u2192 0.79 '
    'for fold 2 \u2192 8) and anti-monotonic at G = 500 (AUC 0.05\u20130.13). '
    'The mechanism is documented by the diagnostic components: at G = 500 '
    'and fold \u2265 4 the broad shift moves the HK anchor itself (k_n '
    'AUC = 1.000), so \u03c9 = k_f/k_n is annihilated by its own denominator. '
    '\u03c9 quantifies divergence in excess of anchor movement and is by '
    'construction insensitive to perturbations whose dominant effect is a '
    'broad mean shift \u2014 a design property, disclosed here as a boundary '
    'of the method (the anchor-visibility boundary; see also Supplementary Notes 1 and '
    '6; Supplementary Table 7).'
)
add_table([
    ['Method', 'FPR/type', 'G100 F2', 'G100 F4', 'G100 F8',
     'G500 F2', 'G500 F4', 'G500 F8'],
    ['MELD', '0.033', '1.000', '1.000', '1.000', '1.000', '1.000', '1.000'],
    ['scDist (Python approximation)', '0.050', '1.000', '1.000', '1.000',
     '1.000', '1.000', '1.000'],
    ['CKI \u03c9', '0.083', '0.517', '0.688', '0.787', '0.127', '0.059', '0.054'],
])
si_caption(
    'Supplementary Table 7. Target-detection AUC (target CD14+ monocytes versus '
    'the five null cell types) in the additive mean-shift simulation. MELD '
    'and the scDist approximation also achieve sensitivity 1.00 and top-1 hit '
    'rate 1.00 at every configuration.'
)
add_para(
    'Power formalization (donor-paired design of Supplementary Note 6; per-pair '
    'permutation test on \u03c9, B = 100, one-sided P < 0.05; 20 replicates '
    'per cell type and sample size). Power at n = 50 cells per condition per '
    'donor is 0.67\u20130.93 across the six cell types; it declines as n '
    'grows (n = 100: 0.47\u20130.76; n = 200: 0.17\u20130.55; n = 500: 0.09 '
    'in the only testable type; pooled-donor designs at n \u2265 500: '
    '\u2248 0), because the permutation null of \u03c9 explodes with '
    'pseudobulk size (k_n \u2192 0 in the null while top-200 selection keeps '
    'k_f elevated), so observed and null stop separating. CKI\u2019s '
    'operating regime is therefore approximately 50\u2013200 cells per donor '
    'per condition; large pooled pseudobulks defeat the \u03c9 permutation '
    'test. MELD- and scDist-style scores have no such boundary but do not '
    'decompose donor drift, which is CKI\u2019s design target '
    '(Supplementary Table 8).'
)
add_table([
    ['Cell type', 'n = 50', 'n = 100', 'n = 200', 'n = 500'],
    ['B cells', '0.84', '0.68', '0.17', '\u2014'],
    ['CD14+ monocytes', '0.78', '0.76', '0.55', '\u2014'],
    ['CD4 T cells', '0.67', '0.61', '0.47', '0.09'],
    ['CD8 T cells', '0.70', '0.68', '\u2014', '\u2014'],
    ['FCGR3A+ monocytes', '0.74', '0.47', '\u2014', '\u2014'],
    ['NK cells', '0.93', '0.76', '\u2014', '\u2014'],
])
si_caption(
    'Supplementary Table 8. Donor-paired detection power (fraction of 20 '
    'replicates significant at one-sided P < 0.05); cells marked \u2014 had '
    'too few eligible donors.'
)
add_para(
    'Summary. CKI is weaker than the competitors at detecting broad '
    'mean-shift perturbations (the anchor moves and \u03c9 is annihilated), '
    'at large-pseudobulk inference (power collapses for per-condition '
    'n \u2273 500), and at quantitative per-type ranking on near-ceiling '
    'real perturbations. CKI holds up on direction and type-level detection '
    'on real data (6/6 sign agreement with MELD), on donor-paired designs at '
    'its intended scale (70\u201393% power at n = 50), and on '
    'interpretability: the k_n/k_f decomposition pinpoints why a '
    'perturbation is or is not visible (anchor movement versus excess '
    'divergence), which neither MELD likelihoods nor scDist distances '
    'expose.'
)

# ===== Section 3.12: real-data neutral-drift calibration =====
add_para('3.12 Real-Data Neutral-Drift Calibration on Technical Replicates', bold=True)
add_para(
    'Purpose and design. Supplementary Note 1 quantifies neutral-drift '
    'specificity in simulation; this section repeats the test on real '
    'technical replicates, where the ground truth of no functional '
    'difference comes from the study design rather than from injected '
    'noise. Every metric is calibrated against a per-pair size-matched '
    '(n-matched) cell-shuffle null: the nuclei of the two libraries being '
    'compared are pooled, permuted, and re-split into disjoint subsets of '
    'exactly the observed group sizes (n_a, n_b), so the null matches '
    'donor, cell type, and group sizes while containing no group structure '
    '(B = 200 per pair for Kang; 100/30/30 for brain tiers T1/T2/T3). '
    'Calibration is the ratio observed / null median; the false-positive '
    'element is observed > own null 95th percentile. Two designs are used. '
    '(i) Kang et al. batch 1 (GSE96583): eight unstimulated PBMC donors '
    'captured across three 10x lanes such that every donor appears in '
    'exactly two lanes, yielding 30 same-donor, same-condition cross-lane '
    'pairs (pure technical drift) across six cell types, evaluated with the '
    'per-pair top-200 scheme for k_n, k_f, \u03c9, raw JS, and cosine '
    'distance. (ii) The Siletti et al. brain atlas drift ladder: 2,732 '
    '(cell class, library) groups with at least 20 nuclei, nested in 606 '
    'libraries, define three tiers of library-level pairs within each cell '
    'class - T1, same (donor, region) different libraries, all 2,161 pairs '
    '(pure technical drift); T2, same region different donors, 1,089 pairs '
    '(technical plus inter-individual drift); T3, same donor different '
    'regions, 1,656 pairs (regional biology, positive control) - evaluated '
    'with the brain pipeline (HK genes plus top-5,000 non-HK genes by mean '
    'expression; per-pair top-200 selection) for seven metrics: k_n, k_f, '
    '\u03c9, raw JS, cosine distance, Spearman distance (1 - \u03c1), and '
    'marker Jaccard distance (1 minus the Jaccard index of each '
    'group\u2019s top-200 markers, genes ranked by pseudobulk difference '
    'minus the cell-weighted background of the other cell classes). '
    'Scripts: notebooks/nc49_pilot_kang_techrep.py (seed 20260918), '
    'notebooks/nc49_brain_drift_ladder.py (seed 42); outputs: '
    'results/nc49_pilot_kang_techrep.csv, '
    'results/nc49_brain_drift_ladder.csv.'
)
_om49 = _km49['omega']
_js49 = _km49['raw_js']
_cos49 = _km49['cosine']
_wom49 = _wilson49(_om49['k'], _om49['n'])
_wjs49 = _wilson49(_js49['k'], _js49['n'])
_wcos49 = _wilson49(_cos49['k'], _cos49['n'])
add_para(
    'Kang batch 1 (technical replicates). \u03c9 was fully calibrated: no '
    f'pair exceeded its own null 95th percentile ({_om49["k"]} of {_om49["n"]}, '
    f'Wilson 95% CI [{_wom49[0]:.3f}, {_wom49[1]:.3f}]), with a median '
    f'calibration ratio of {_om49["cal_med"]:.3f} (IQR '
    f'[{_om49["cal_lo"]:.3f}, {_om49["cal_hi"]:.3f}]); k_f alone was equally '
    f'calibrated ({_km49["k_f"]["k"]} of {_km49["k_f"]["n"]}). Raw JS '
    f'misreported {_js49["k"]} of {_js49["n"]} pairs '
    f'({_js49["k"] / _js49["n"]:.1%}, CI '
    f'[{_wjs49[0]:.3f}, {_wjs49[1]:.3f}]) and cosine distance '
    f'{_cos49["k"]} of {_cos49["n"]} ({_cos49["k"] / _cos49["n"]:.1%}, CI '
    f'[{_wcos49[0]:.3f}, {_wcos49[1]:.3f}]) as divergence; k_n alone fired '
    f'once ({_km49["k_n"]["k"]} of {_km49["k_n"]["n"]}). The per-metric '
    'values are given in Supplementary Table 9; the replication is shown '
    'in main-text Fig. 3d.'
)
_rows_kang49 = [['Metric', 'Calibration median [IQR]', 'FPR (k/n)', 'Wilson 95% CI']]
for _m in ['k_n', 'k_f', 'omega', 'raw_js', 'cosine']:
    _a = _km49[_m]
    _w = _wilson49(_a['k'], _a['n'])
    _rows_kang49.append([
        _LABEL49[_m],
        f'{_a["cal_med"]:.3f} [{_a["cal_lo"]:.3f}, {_a["cal_hi"]:.3f}]',
        f'{_a["k"]}/{_a["n"]}',
        f'[{_w[0]:.3f}, {_w[1]:.3f}]'])
add_table(_rows_kang49)
si_caption(
    'Supplementary Table 9. Kang batch 1, 30 same-donor, same-condition '
    'cross-lane pairs. Calibration = observed / own n-matched null median '
    '(B = 200 per pair); FPR = fraction of pairs whose observed value '
    'exceeds its own null 95th percentile. The Wilson intervals treat the '
    '30 pairs as independent (donor-level clustering is not modeled), so '
    'they are optimistic for the cohort-level rate. Cross-metric '
    'comparisons on these 30 pairs are paired by design - every metric is '
    'evaluated on the identical pairs against the identical per-pair '
    'nulls - so FPR differences are within-pair contrasts (a McNemar-style '
    'paired framing applies to any cross-metric test).'
)
_l1o, _l1w = _lad49['T1']['omega'], _lad49['T1']['raw_js']
_l2o, _l2w = _lad49['T2']['omega'], _lad49['T2']['raw_js']
_l3o, _l3w = _lad49['T3']['omega'], _lad49['T3']['raw_js']
_mj1, _mj3 = _lad49['T1']['marker_jaccard'], _lad49['T3']['marker_jaccard']
_mj2 = _lad49['T2']['marker_jaccard']
_kf1, _kf2 = _lad49['T1']['k_f'], _lad49['T2']['k_f']
_mjf1, _mjf3 = _mj1['k'] / _mj1['n'], _mj3['k'] / _mj3['n']
_omf1, _omf3 = _l1o['k'] / _l1o['n'], _l3o['k'] / _l3o['n']
_gap_mj49, _gap_om49 = _mjf3 - _mjf1, _omf3 - _omf1
_rat_mj49, _rat_om49 = _mjf3 / _mjf1, _omf3 / _omf1
add_para(
    'Brain drift ladder. On T1 (pure technical drift), \u03c9 had the '
    'lowest misreporting rate among the continuous divergence metrics '
    f'(FPR {_omf1:.1%}, versus '
    f'{_lad49["T1"]["raw_js"]["k"] / _lad49["T1"]["raw_js"]["n"]:.1%} for raw JS, '
    f'{_lad49["T1"]["cosine"]["k"] / _lad49["T1"]["cosine"]["n"]:.1%} for cosine, '
    f'{_lad49["T1"]["spearman"]["k"] / _lad49["T1"]["spearman"]["n"]:.1%} for Spearman, '
    f'{_kf1["k"] / _kf1["n"]:.1%} for k_f, and '
    f'{_lad49["T1"]["k_n"]["k"] / _lad49["T1"]["k_n"]["n"]:.1%} for k_n), and \u03c9 '
    f'was below raw JS in {_below49["js"]} of {_nct_49} cell classes (below cosine in '
    f'{_below49["cos"]} of {_nct_49}, below Spearman in {_below49["spr"]} of '
    f'{_nct_49}; per-class raw-JS-to-\u03c9 FPR ratios '
    f'{_ratio_lo49:.1f}-{_ratio_hi49:.1f}). Marker Jaccard distance was '
    f'lower still (T1 FPR {_mjf1:.1%}, below \u03c9 in {_below49["mj"]} of '
    f'{_nct_49} cell classes): judged on the false-positive statistic '
    'alone, it separates the tiers at least as well as \u03c9 '
    f'(T3\u2212T1 FPR gap {_gap_mj49:.2f} versus {_gap_om49:.2f}; '
    f'T3/T1 ratio {_rat_mj49:.1f} versus {_rat_om49:.1f}), so the '
    'misreporting claim for \u03c9 is restricted to the continuous '
    'divergence metrics. At T2 (donor drift), all metrics '
    'fired on most pairs - donor differences contain real biology - and '
    '\u03c9 again misreported least among the continuous divergence metrics '
    f'({_l2o["k"] / _l2o["n"]:.1%} versus '
    f'{_l2w["k"] / _l2w["n"]:.1%} for raw JS and {_kf2["k"] / _kf2["n"]:.1%} for '
    f'k_f; marker Jaccard was again lower at {_mj2["k"] / _mj2["n"]:.1%}; '
    f'calibration {_l2o["cal_med"]:.2f} versus {_l2w["cal_med"]:.2f} and '
    f'{_kf2["cal_med"]:.2f}). At T3 (regional biology, positive control), '
    f'every metric rose (\u03c9 calibration {_l3o["cal_med"]:.2f}; raw JS '
    f'{_l3w["cal_med"]:.2f}), so sensitivity to genuine divergence is '
    'preserved; across the ladder the \u03c9 calibration gradient is the '
    f'shallowest of all metrics ({_l1o["cal_med"]:.2f} \u2192 {_l2o["cal_med"]:.2f} '
    f'\u2192 {_l3o["cal_med"]:.2f}, versus {_l1w["cal_med"]:.2f} \u2192 '
    f'{_l2w["cal_med"]:.2f} \u2192 {_l3w["cal_med"]:.2f} for raw JS). The '
    'advantage of \u03c9 over marker Jaccard lies elsewhere: Jaccard '
    'responds weakest to genuine regional divergence (T3 calibration '
    f'{_mj3["cal_med"]:.2f} versus {_l3o["cal_med"]:.2f} for \u03c9 and '
    f'{_l3w["cal_med"]:.2f} for raw JS), so its apparent specificity is '
    'purchased with the weakest sensitivity to real signal, and as a '
    'single set-overlap statistic it offers no k_n/k_f decomposition. '
    'Per-tier values '
    'for all seven metrics are given in Supplementary Table 10; main-text '
    'Fig. 3b,c.'
)
_rows_lad49 = [['Metric', 'T1 cal [IQR] / FPR', 'T2 cal [IQR] / FPR', 'T3 cal [IQR] / FPR']]
for _m in _METRICS49:
    _row = [_LABEL49[_m]]
    for _t in ('T1', 'T2', 'T3'):
        _a = _lad49[_t][_m]
        _row.append(f'{_a["cal_med"]:.2f} [{_a["cal_lo"]:.2f}, {_a["cal_hi"]:.2f}] '
                    f'/ {_a["k"] / _a["n"]:.1%}')
    _rows_lad49.append(_row)
add_table(_rows_lad49)
si_caption(
    'Supplementary Table 10. Brain drift ladder, per tier and metric: '
    'calibration median [IQR] (observed / own n-matched null median) and '
    'FPR (observed > own null 95th percentile). T1: same (donor, region) '
    'cross-library pairs, n = 2,161; T2: same region cross-donor pairs, '
    'n = 1,089; T3: same donor cross-region pairs, n = 1,656. Per-pair '
    'nulls used B = 100 permutations for T1 and B = 30 for T2/T3; at '
    'B = 30 the per-pair exceedance indicator resolves to 1/31, so the '
    'T2/T3 tier rates carry Monte-Carlo noise of a few percentage points '
    'and are tier-level, not per-pair, calibrations. The 200-per-class '
    'subsampling cap makes the cell-class composition of T2/T3 '
    'availability-dependent, so cross-tier comparisons mix class '
    'composition with drift tier; per-class T1 values are discussed in '
    'the text.'
)
_cp49 = _t1ct_49.loc['Choroid plexus']
_bg49 = _t1ct_49.loc['Bergmann glia']
add_para(
    'Diagnostics and honest qualifications. First, the absolute \u03c9 FPR '
    'on T1 is not zero, and it grows with group size: '
    f'{_bins49["small"]["fpr_omega"]:.1%} for pairs with at most 30 nuclei per '
    f'library (n = {_bins49["small"]["n"]}), '
    f'{_bins49["mid"]["fpr_omega"]:.1%} for 31-500, and '
    f'{_bins49["large"]["fpr_omega"]:.1%} above 500 (n = {_bins49["large"]["n"]}; raw JS '
    f'{_bins49["small"]["fpr_js"]:.1%} \u2192 {_bins49["large"]["fpr_js"]:.1%}) - a real '
    'library-level technical component (capture efficiency, depth) that '
    'grows detectable with power and that the k_n denominator absorbs only '
    f'partially (the T1 k_n calibration itself is {_lad49["T1"]["k_n"]["cal_med"]:.2f}). '
    'Second, a minority of cell classes show gene-specific library effects '
    'that the anchor cannot absorb: choroid plexus '
    f'(n = {int(_cp49["n"])} pairs, median calibration {_cp49["cal_omega"]:.2f}) and '
    f'Bergmann glia (n = {int(_bg49["n"])}, {_bg49["cal_omega"]:.2f}) exceed the null '
    'most strongly; in choroid plexus, two libraries of the same donor, '
    'region, and type differ in k_f by up to 137-fold. The ladder thereby '
    'quantifies the library-level structure that the block-shuffle null '
    'retains by design (Supplementary Note 12): the Bergmann-glia '
    'block-shuffle null mean (21.9) lying far above its split-half '
    'baseline (9.7) reflects precisely this within-donor, within-region '
    'technical divergence. Third, per-pair nulls were used throughout '
    '(one null per pair, not one pooled null per class-size bin); the '
    'size-binned FPR gradient above is reported precisely to expose the '
    'group-size dependence that a pooled null would mask, and small-group '
    'p95 estimates are correspondingly noisy at the smallest group sizes. '
    'The simulation-level claim of absolute '
    'neutral-drift immunity (Supplementary Note 1) thus transfers to real '
    'data only as a relative-calibration advantage: lowest misreporting '
    'among the continuous divergence metrics at every tier, with '
    'sensitivity to genuine '
    'regional divergence preserved.'
)

# ===== Section 3.13: TCGA per-sample statistics =====
add_para('3.13 Per-Sample Divergence and Group Statistics for TCGA', bold=True)
add_para(
    'Purpose and design. The main-text TCGA analysis (Results: A pan-cancer '
    'map of tissue-level divergence in tumors; Methods: '
    'Per-sample divergence and group statistics) ranks cancer types by the '
    'NN/TT ratio of mean \u03c9, stratifies LUAD tumors by driver mutation, '
    'and tests survival association in LIHC. This section reports the full '
    'group statistics behind those claims (Supplementary Tables 11\u201317). '
    'Per-tumor statistics are the '
    'mean of \u03c9, k_f, and k_n over all pairs in the linear-normalization '
    'pair table after the barcode-audit exclusion (34,828 pairs: the 478 '
    'pairs touching the 32 cell-line-derived aliquots dropped from the '
    '35,306-pair table; authoritative file: '
    'results/tcga_linear_norm_v44_all_pairs.csv) in which a sample '
    'participates; per-sample values are not archived as a separate file '
    'and are rebuilt from that pair table plus the cBioPortal mutation '
    'labels by notebooks/nc52_tcga_excc_main.py (Reproducibility Guide, '
    'Section 5.10c). Group-level ratios carry sample-level cluster bootstrap '
    '95% CIs (B = 1,000; seed 42; tumor and normal samples resampled with '
    'replacement independently, each pair reweighted by the product of its '
    'endpoint resampling weights). LUAD driver groups (61 EGFR, 120 KRAS, '
    '311 wild-type (negative for both drivers); 2 double mutants excluded) were tested with '
    'Kruskal-Wallis followed by Dunn post-hoc tests with Holm correction '
    '(manual implementation, tie-corrected rank variances); group mean '
    'differences carry within-group bootstrap 95% CIs (B = 1,000). Because '
    'per-tumor \u03c9 averages overlapping (non-disjoint) pair sets, the '
    'group tests were additionally re-run as whole-tumor label-permutation '
    'tests (B = 10,000, seed 42): KW P = 0.0001; KRAS\u2013WT P = 0.0001, '
    'KRAS\u2013EGFR P = 0.003, EGFR\u2013WT P = 0.21 \u2014 the published '
    'ordering and significance pattern is preserved (all permutation P-values '
    'are Monte-Carlo estimates at B = 10,000, resolution 10\u207b\u2074; the '
    'KRAS\u2013EGFR P is 0.0034, whose final digit is not stable across random '
    'streams) (notebooks/'
    '93_luad_group_permutation_v49.py; output: results/'
    'nc49_tcga_luad_mutation_perm.csv). The KRAS contrast was also '
    're-evaluated on the log-\u03c9 scale: adjusted KRAS/WT ratio 1.19, '
    'bootstrap 95% CI [1.12, 1.26], so the adjustment conclusion is '
    'scale-robust (notebooks/98_luad_logomega_sensitivity_v49.py; output: '
    'results/nc49_tcga_luad_logomega_sensitivity.csv). '
    'The '
    'LIHC survival analysis used Cox proportional-hazards regression '
    '(R survival::coxph) on the ex-CC default cohort (all 32 ILSBio '
    'cell-line tumours excluded; n = 272 tumors with complete covariates, '
    '79 events) with per-tumor \u03c9 standardized to unit SD '
    '(hazard ratios per SD), AJCC stage entered as a categorical factor, '
    'plus Edmondson grade (G1-G4, ordinal), age, and sex (listwise '
    'deletion of missing covariates), '
    'with k_f-only, k_n-only, and tumor-normal-\u03c9 exposures as '
    'sensitivity models (Supplementary Table 14). Proportional hazards '
    'were checked with cox.zph (M2 GLOBAL P = 0.023, reported alongside '
    'the estimates); the \u03c9 null is unchanged across models (HR/SD '
    '1.08 [0.88, 1.33], P = 0.467 in the full model; '
    'notebooks/nc52_lihc_cox_excc.py; outputs: '
    'results/nc52_lihc_cox_excc.csv, results/nc52_lihc_cox_excc_zph.csv). '
    'The adjusted LUAD driver contrasts were additionally re-run as '
    'whole-tumor label-permutation tests (B = 10,000, seed 42) that re-fit '
    'the full OLS adjustment model at every permutation: the KRAS '
    'contrasts remain significant (KRAS-WT P \u2264 0.001) while the '
    'EGFR-WT contrast does not (P \u2265 0.28), matching the parametric '
    'conclusion (notebooks/nc52_tcga_luad_adjmodel_permutation.py; '
    'output: results/nc52_tcga_luad_adjmodel_permutation.csv). '
    'Covariate sensitivity used '
    'the official ESTIMATE '
    'stromal (141) and immune (141) gene sets (rank-based single-sample '
    'enrichment; combined stromal-plus-immune score, monotonically '
    'equivalent to published ESTIMATE purity) and cBioPortal patient-level '
    'LUAD clinical data (study luad_tcga; smoking status 508, pack-years '
    '356, sex 522 patients; 427 of 492 tumors with known smoking status, '
    '87%). Scripts: notebooks/nc52_tcga_excc_main.py (seed 42; ex-CC '
    'default main chain: pan-cancer ratios, clinical severity, summary), '
    'notebooks/nc49_tcga_purity.py, '
    'notebooks/nc49_tcga_luad_smoking.py, '
    'notebooks/nc49_tcga_kf_composition.py; outputs: '
    'results/nc52_tcga_pancancer_excc.csv, '
    'results/nc52_tcga_excc_severity.csv, '
    'results/nc52_tcga_excc_summary.json, '
    'results/nc49_tcga_luad_mutation.csv, results/nc49_tcga_purity.csv, '
    'results/nc49_tcga_admix_scores.csv, results/nc49_tcga_luad_smoking.csv, '
    'results/nc49_tcga_kf_composition.csv.'
)
_rows_pc49 = [['Cancer', 'NN/TT \u03c9 ratio [95% CI]', 'MWU P',
               'k_n TT/NN median', 'k_n mean ratio [95% CI]']]
for _, _r in _tcga_pc.sort_values('rank_by_NN_TT_ratio').iterrows():
    _p = _r['p_MWU_NN_gt_TT']
    _ps = '< 10\u207b\u00b3\u2070\u2070' if _p == 0 else _pf49(_p)
    _rows_pc49.append([
        _r['cancer'].replace('TCGA-', ''),
        f'{_r["NN_TT_ratio"]:.2f} [{_r["NN_TT_ratio_CI95_lower"]:.2f}, '
        f'{_r["NN_TT_ratio_CI95_upper"]:.2f}]',
        _ps,
        f'{_r["kn_TT_NN_median_ratio"]:.1f}\u00d7',
        f'{_r["kn_TT_NN_mean_ratio"]:.2f} [{_r["kn_TT_NN_mean_ratio_CI95_lower"]:.2f}, '
        f'{_r["kn_TT_NN_mean_ratio_CI95_upper"]:.2f}]'])
add_table(_rows_pc49)
si_caption(
    'Supplementary Table 11. Pan-cancer NN/TT ratios (mean NN to mean TT '
    '\u03c9) with sample-level cluster-bootstrap 95% CIs, one-sided '
    'Mann-Whitney P (NN > TT), and the housekeeping-baseline mechanism: '
    'median and mean TT/NN k_n ratios with bootstrap 95% CIs. The '
    'pair-level Mann-Whitney P-values are descriptive only: they ignore '
    'the dyadic dependence between pairs sharing a sample, so the '
    'cluster-bootstrap CI is the inferential caliber. The point '
    'estimate exceeds 1 in 5 of 5 cancer types; the CI excludes 1 in 4 of '
    '5 (LIHC includes 1), whereas the k_n mean-ratio CI excludes 1 in all '
    'five. Ranked by NN/TT effect size (main-text Fig. 4a).'
)
add_para(
    'LUAD driver-mutation stratification. Mean per-tumor \u03c9 was highest '
    'in KRAS-mutant tumors (136.9), exceeding wild-type (115.4) and '
    'EGFR-mutant tumors (122.2; Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; '
    'Supplementary Tables 12 and 13). The k_f/k_n decomposition separates the '
    'two drivers\u2019 associations: the KRAS contrast carries a functional '
    'component - k_f is elevated in KRAS-mutant tumors (KRAS versus EGFR, '
    'Dunn-Holm P = 0.015; KRAS-wild-type k_f difference 0.011, 95% CI '
    '0.002-0.019) accompanied by a lower k_n (wild-type > KRAS, '
    'Dunn-Holm P = 4.2 \u00d7 10\u207b\u2074), both of which raise the '
    'ratio; the unadjusted elevation is denominator-dominated (k_n '
    'contributed ~84% of the log-\u03c9 gap; the unadjusted k_f contrast '
    'KRAS versus WT was non-significant, Dunn P = 0.097), so both the '
    'unadjusted decomposition and the covariate-adjusted estimates below '
    'are reported; the EGFR association shows no significant k_f difference (all '
    'Holm-adjusted P > 0.09) and no significant k_n difference (WT > EGFR, '
    'P = 0.09). '
    'Covariate adjustment resolves the two drivers differently (Supplementary Tables 15\u201317): after adjustment for stromal/immune admixture the '
    'KRAS-wild-type contrast retains both components (k_f +0.012, '
    'P = 0.009; k_n -0.0004, P = 0.003) and likewise survives joint '
    'smoking-plus-admixture adjustment (omega +13.6, P = 3.3 \u00d7 '
    '10\u207b\u2074), whereas the EGFR-wild-type differences disappear '
    'entirely under purity adjustment (all P > 0.4) - EGFR-mutant tumors '
    'carry the highest admixture scores (Kruskal-Wallis P = 0.003), so the '
    'apparent EGFR elevation is an admixture artefact.'
)
_rows_lu49 = [['Metric', 'WT', 'EGFR', 'KRAS', 'Kruskal-Wallis P']]
for _met, _lab in (('omega', '\u03c9'), ('kf', 'k_f'), ('kn', 'k_n')):
    _d = _tcga_luad[(_tcga_luad['metric'] == f'LUAD_{_met}') &
                    (_tcga_luad['test'] == 'descriptive')].set_index('comparison')['stat']
    _p = _tcga_luad[(_tcga_luad['metric'] == f'LUAD_{_met}') &
                    (_tcga_luad['test'] == 'Kruskal-Wallis')]['p'].iloc[0]
    _fmt = (lambda v: f'{v:.1f}') if _met == 'omega' else (lambda v: f'{v:.4f}')
    _rows_lu49.append([_lab, _fmt(_d['WT']), _fmt(_d['EGFR']), _fmt(_d['KRAS']),
                       _pf49(_p)])
add_table(_rows_lu49)
si_caption(
    'Supplementary Table 12. LUAD per-tumor group means (n = 311 wild-type, '
    '61 EGFR-mutant, 120 KRAS-mutant) and the omnibus Kruskal-Wallis test '
    'for \u03c9, k_f, and k_n. Wild-type means wild-type for EGFR and KRAS '
    '(tumors carrying other drivers were not separately excluded). '
    'Per-tumor means share TT pairs across groups, so the KW/Dunn tests '
    'and within-group bootstrap CIs do not model this pair-sharing '
    'dependence and are read descriptively; the covariate-adjusted OLS '
    'contrasts of Supplementary Tables 16 and 17 are the inferential caliber.'
)
_rows_luc49 = [['Contrast', '\u03c9: Dunn-Holm P / bootstrap diff [95% CI]',
                'k_f: P / diff [95% CI]', 'k_n: P / diff [95% CI]']]
_dhcmp49 = {'KRAS - WT': 'WT vs KRAS', 'KRAS - EGFR': 'EGFR vs KRAS',
            'EGFR - WT': 'WT vs EGFR'}
for _cmp in ('KRAS - WT', 'KRAS - EGFR', 'EGFR - WT'):
    _row = [_cmp.replace(' -', ' \u2212')]
    for _met in ('omega', 'kf', 'kn'):
        _dh = _tcga_luad[(_tcga_luad['metric'] == f'LUAD_{_met}') &
                         (_tcga_luad['test'] == 'Dunn (Holm)') &
                         (_tcga_luad['comparison'] == _dhcmp49[_cmp])]['p'].iloc[0]
        _bt = _tcga_luad[(_tcga_luad['metric'] == f'LUAD_{_met}') &
                         (_tcga_luad['test'] == 'bootstrap mean diff') &
                         (_tcga_luad['comparison'] == _cmp)].iloc[0]
        _lo, _hi = (float(x) for x in
                    _bt['p'].replace('CI95 [', '').replace(']', '').split(','))
        _row.append(f'{_pf49(_dh)} / {_bt["stat"]:+.4g} [{_lo:.4g}, {_hi:.4g}]')
    _rows_luc49.append(_row)
add_table(_rows_luc49)
si_caption(
    'Supplementary Table 13. LUAD pairwise contrasts: Dunn post-hoc P-values '
    'with Holm correction, and within-group bootstrap mean differences with '
    '95% CIs (B = 1,000). Main-text Fig. 5b-d.'
)
_coxz49 = _tcga_cox[_tcga_cox['covariate'].str.startswith('z_')].set_index('model')
_coxlab49 = {'M1_omega_full_exCC': 'M1: \u03c9, full adjustment',
             'M2_omega_stage_grade_exCC': 'M2: \u03c9 + stage + grade',
             'M3_omega_unadjusted_exCC': 'M3: \u03c9, unadjusted',
             'M4_kf_full_exCC': 'M4: k_f, full adjustment',
             'M5_kn_full_exCC': 'M5: k_n, full adjustment',
             'M6_tnomega_full_exCC': 'M6: TN-\u03c9, full adjustment'}
_rows_cox49 = [['Model', 'n', 'Events', 'HR per SD [95% CI]', 'P']]
for _mod in ['M1_omega_full_exCC', 'M2_omega_stage_grade_exCC', 'M3_omega_unadjusted_exCC',
             'M4_kf_full_exCC', 'M5_kn_full_exCC', 'M6_tnomega_full_exCC']:
    _r = _coxz49.loc[_mod]
    _rows_cox49.append([
        _coxlab49[_mod], f'{int(_r["n"])}', f'{int(_r["events"])}',
        f'{_r["HR"]:.2f} [{_r["HR_lower"]:.2f}, {_r["HR_upper"]:.2f}]',
        _pf49(_r["p"])])
add_table(_rows_cox49)
si_caption(
    'Supplementary Table 14. LIHC overall-survival Cox models (hazard ratios '
    'per +1 SD of the exposure; ex-CC cohort, n = 272 with 79 events; R '
    'survival::coxph with AJCC stage as a categorical covariate; '
    'proportional-hazards checked by cox.zph\u2014M2 shows a GLOBAL '
    'departure signal at P = 0.023, all other models P \u2265 0.07). No '
    'exposure reaches significance (all P \u2265 0.39), so the pan-cancer '
    'reversal is a descriptive property '
    'of tissue-state divergence, not a prognostic marker; the full '
    'coefficient table is results/nc52_lihc_cox_excc.csv of the companion '
    'repository.'
)

# ===== Section 3.13 continued: purity and smoking covariate sensitivity =====
_pur49 = pd.read_csv(_root49 / "results" / "nc49_tcga_purity.csv")
_smk49 = pd.read_csv(_root49 / "results" / "nc49_tcga_luad_smoking.csv")
add_para(
    'Purity and smoking covariate sensitivity. Stromal/immune admixture was '
    'scored per sample with the official ESTIMATE gene sets (141 stromal + '
    '141 immune genes) using the rank-based single-sample enrichment '
    'algorithm over all 45,504 expressed genes of the five-cancer merged '
    'matrix; the combined stromal-plus-immune score is monotonically '
    'equivalent to published ESTIMATE purity, so regression-based '
    'adjustment is invariant to the transformation. Per-tumor k_n '
    'correlated negatively with admixture in every cancer type, and '
    'restricting tumor-tumor pairs to the low-admixture half of tumors '
    'increased the NN/TT ratio in all five cancer types (Supplementary Table 15), so the pan-cancer reversal is not an admixture artefact. In '
    'LUAD, admixture differed across driver groups (highest in EGFR-mutant '
    'tumors), and OLS adjustment for admixture abolished the EGFR-wild-type '
    'differences while preserving both KRAS-wild-type components (Supplementary Table 16); smoking status (ever/never, available for 427 of '
    '492 LUAD tumors, 87%) was strongly confounded with driver group but '
    'did not carry the divergence association (Supplementary Table 17).'
)
_rows_pur49 = [['Cancer', 'k_n ~ admix r (P)', '\u03c9 ~ admix r (P)',
                'NN/TT all tumors', 'NN/TT low-admix half [95% CI]']]
for _c in ('TCGA-LUAD', 'TCGA-LUSC', 'TCGA-LIHC', 'TCGA-KIRC', 'TCGA-BRCA'):
    _kn = _pur49[(_pur49.section == 'A_regression') &
                 (_pur49.cancer == _c) & (_pur49.metric == 'kn')].iloc[0]
    _om = _pur49[(_pur49.section == 'A_regression') &
                 (_pur49.cancer == _c) & (_pur49.metric == 'omega')].iloc[0]
    _all = _pur49[(_pur49.section == 'D_nntt_highpurity') &
                  (_pur49.cancer == _c) &
                  (_pur49.test == 'NN/TT all tumours')].iloc[0]
    _half = _pur49[(_pur49.section == 'D_nntt_highpurity') &
                   (_pur49.cancer == _c) &
                   (_pur49.test == 'NN/TT low-admix half')].iloc[0]
    _rows_pur49.append([
        _c.replace('TCGA-', ''),
        f'{_kn.pearson_r:.2f} ({_pf49(_kn.p)})',
        f'{_om.pearson_r:+.2f} ({_pf49(_om.p)})',
        f'{_all.stat:.2f}',
        f'{_half.stat:.2f} {str(_half["p"]).replace("CI95 ", "")}'])
add_table(_rows_pur49)
si_caption(
    'Supplementary Table 15. Purity sensitivity of the pan-cancer reversal. '
    'Left: Pearson correlations of per-tumor k_n and \u03c9 with the '
    'ESTIMATE combined admixture score; the k_n correlation is negative in '
    'all five cancer types (KIRC P = 8.3 \u00d7 10\u207b\u00b9\u2077, '
    'LIHC P = 3.9 \u00d7 10\u207b\u2076), so admixture can only weaken, '
    'not create, the TT k_n elevation. Right: NN/TT \u03c9 mean ratio over '
    'all tumors versus tumor-tumor pairs restricted to the low-admixture '
    '(high-purity) half of tumors (sample-level cluster bootstrap 95% CI, '
    'B = 1,000, seed 42); the ratio increases in all five cancer types and '
    'the CI excludes 1 in four of five (LIHC still including 1).'
)
_anco49 = _pur49[(_pur49.section == 'C_luad_ancova') &
                 (_pur49.test == 'OLS adj diff (group + admix)')]
_rows_anc49 = [['Contrast', '\u0394\u03c9 (P)', '\u0394k_f (P)',
                '\u0394k_n (P)']]
for _cmp in ('KRAS - WT', 'KRAS - EGFR', 'EGFR - WT'):
    _row = [_cmp.replace(' -', ' \u2212')]
    for _met in ('omega', 'kf', 'kn'):
        _r = _anco49[(_anco49.metric == _met) &
                     (_anco49.comparison == _cmp)].iloc[0]
        _row.append(f'{_r.stat:+.4g} ({_pf49(_r.p)})')
    _rows_anc49.append(_row)
add_table(_rows_anc49)
_kwad49 = _pur49[(_pur49.section == 'B_group_admix') &
                 (_pur49.test == 'Kruskal-Wallis')].iloc[0]
_gmad49 = _pur49[(_pur49.section == 'B_group_admix') &
                 (_pur49.test == 'group mean')].set_index('n')['stat']
si_caption(
    'Supplementary Table 16. LUAD driver-group contrasts after adjustment '
    'for stromal/immune admixture (OLS metric ~ group + z-scored '
    'admixture, n = 492 tumors). Admixture differed across driver groups '
    f'(means WT {_gmad49[311]:,.0f} < KRAS {_gmad49[120]:,.0f} < EGFR '
    f'{_gmad49[61]:,.0f}; Kruskal-Wallis P = {_pf49(_kwad49.p)}), '
    'consistent with the low-purity lepidic growth pattern of EGFR-mutant '
    'tumors. After adjustment the KRAS \u2212 WT contrast retains both '
    'components, whereas EGFR \u2212 WT is null on every metric (all '
    'P > 0.4) - the apparent EGFR elevation is an admixture artefact.'
)
_smkmods49 = [('B_group_only', 'group only'),
              ('B_smoke_adj', '+ ever-smoker'),
              ('B_smoke_agesex_adj', '+ ever-smoker + age + sex'),
              ('B_smoke_admix_adj', '+ ever-smoker + admixture')]
_rows_smk49 = [['Model (KRAS \u2212 WT)', 'n', '\u0394\u03c9 (P)',
                '\u0394k_f (P)', '\u0394k_n (P)']]
for _sec, _lab in _smkmods49:
    _sub = _smk49[_smk49.section == _sec]
    _row = [f'OLS {_lab}', f'{int(_sub.n.iloc[0])}']
    for _met in ('omega', 'kf', 'kn'):
        _r = _sub[(_sub.metric == _met) &
                  (_sub.comparison == 'KRAS - WT')].iloc[0]
        _row.append(f'{_r.stat:+.4g} ({_pf49(_r.p)})')
    _rows_smk49.append(_row)
add_table(_rows_smk49)
_chi49 = _smk49[_smk49.test == 'chi2 ever/never x group'].iloc[0]
_pct49 = _smk49[_smk49.test.str.startswith('ever-smoker pct')].set_index('test')['stat']
si_caption(
    'Supplementary Table 17. LUAD smoking-covariate adjustment (ever/never; '
    '427 of 492 tumors with known smoking status). KRAS-mutant tumors were '
    'strongly enriched for ever-smokers '
    f'({_pct49["ever-smoker pct KRAS"]:.1f}% versus '
    f'{_pct49["ever-smoker pct WT"]:.1f}% wild-type and '
    f'{_pct49["ever-smoker pct EGFR"]:.1f}% EGFR-mutant; \u03c7\u00b2 = '
    f'{_chi49.stat:.1f}, P = {_pf49(_chi49.p)}), yet the KRAS \u2212 WT '
    'differences are essentially unchanged across adjustments; EGFR \u2212 '
    'WT was non-significant in every model (all P > 0.10; full values in '
    'results/nc49_tcga_luad_smoking.csv). Pack-years (available for 356 '
    'patients) were not modeled owing to high missingness and are '
    'descriptive only.'
)
add_para(
    'Panel semantics and composition correction for k_f. Enrichment of '
    'the LUAD KRAS tumor-tumor identity panels (all 7,260 KRAS-KRAS '
    'pairs, top-200 genes per pair; core panel by the documented '
    'frequency fallback) against the 50 MSigDB Hallmark programs found '
    'no program surviving multiple-testing correction (top: Estrogen '
    'Response Late, q = 0.24; recurrent panel members are dominated by '
    'individually variable, sex-linked and secreted markers), indicating '
    'that bulk k_f measures broad tissue-state divergence rather than a '
    'single tumor-intrinsic program; pair-level regressions of log k_f '
    'on pair type with ESTIMATE admixture covariates retained the '
    'TT \u2265 NN k_f ordering in all five cancer types (adjusted log '
    'gaps +0.21 to +0.82, all P \u2264 8.2 \u00d7 '
    '10\u207b\u2078\u2070), so the k_f group differences are not '
    'explained by stromal/immune admixture. Script: '
    'notebooks/nc49_tcga_kf_composition.py; output: '
    'results/nc49_tcga_kf_composition.csv.'
)


add_para(
    'Additional driver-stratification controls (migrated from the main text in '
    'v50). The admixture-adjusted KRAS\u2013wild-type differences were significant '
    'for both components (\u0394\u03c9 +16.8, P = 4.0 \u00d7 10\u207b\u2076; '
    '\u0394k_f +0.012, P = 0.009; \u0394k_n \u22120.0004, P = 0.003; adjusted '
    'log-\u03c9 ratio 1.19, bootstrap 95% CI [1.12, 1.26]). KRAS-mutant tumors '
    'were strongly enriched for ever-smokers (94% versus 63% EGFR-mutant and 86% '
    'wild-type, \u03c7\u00b2 = 30.3, P = 2.7 \u00d7 10\u207b\u2077); '
    'smoking-adjusted contrasts remained significant (\u0394\u03c9 +13.9, '
    'P = 5.9 \u00d7 10\u207b\u2074 smoking alone; +13.6, P = 3.3 \u00d7 '
    '10\u207b\u2074 with admixture; +13.3, P = 1.4 \u00d7 10\u207b\u00b3 '
    'with smoking, age, and sex; smoking status covered 427 of 492 tumors, 87%). '
    'KRAS-mutant LUAD also differs from wild-type in TP53 co-mutation rate and '
    'histological subtype (invasive mucinous adenocarcinoma is KRAS-enriched); '
    'neither was adjusted for. The ex-CC default cohort (the 32 '
    'cell-line-derived (CC) LIHC samples excluded from all v52 analyses) '
    'keeps the LIHC null result and the high-purity-half analysis '
    'unchanged (NN/TT 1.11 [0.94, 1.30], which includes 1; the TT k_n/NN k_n ratio '
    '1.34 [1.02, 1.89] excludes 1 ex-CC, so the k_n elevation is nominally significant; high-purity-half 1.17 versus 1.19 excluding CC, 95% CI [1.01, 1.44]); the full barcode source-code audit is '
    'documented in the Reproducibility Guide '
    '(notebooks/94_cc_audit_sensitivity_v49.py).'
)
doc.add_page_break()

add_heading('Dataset Quality Control and Filtering Criteria', 2)

add_para('4.1 Tabula Muris FACS (Mouse)', bold=True)
add_para(
    'Downloaded from GEO (GSE109774). FACS-sorted cells (not droplet-based) were used '
    'to ensure high per-cell gene detection. QC filtering: cells with < 500 detected '
    'genes were removed; cells with > 10% mitochondrial gene expression were removed; '
    'genes detected in < 3 cells were removed. Result: 15,057 cells x 22,308 genes '
    '(post-QC). Cell type annotation: 38 cell type entries (each with at least 20 '
    'cells in total and at least one mouse contributing at least 10 cells) '
    'were retained for pseudobulk construction, spanning 6 organs (Liver, Kidney, '
    'Spleen, Lung, Heart, Bone Marrow), yielding C(38, 2) = 703 analyzed pairs.'
)

add_para('4.2 Tabula Sapiens (Human)', bold=True)
add_para(
    'Downloaded from CZ CELLxGENE Discover. QC filtering: cells with < 500 detected '
    'genes were removed; cells with > 20% mitochondrial gene expression were removed. '
    'Result: 108,136 cells retained (6 h5ad files total), with 51,852 genes (filtered from the '
    'original 58,870). Cell type entries: 102 entries across 6 organs (Liver, Kidney, '
    'Heart, Bone Marrow, Spleen, Lung). Cell types included in pairwise \u03c9 analysis '
    f'were required to have \u2265 10 cells in at least one donor and at least 20 cells per '
    f'entry ("unknown" annotations excluded); 99 of the 102 entries passed these filters, '
    f'yielding C(99, 2) = 4,851 analyzed pairs. Pairwise identity gene '
    'selection (top-200 genes by |Delta expression| ranking) ensures that each comparison '
    'uses the most informative genes for that specific pair. Human HK genes: HRT Atlas '
    'v1.0 reference (1,130 genes; human column, 1,129 matched to data).'
)

add_para('4.3 TCGA Bulk RNA-seq', bold=True)
add_para(
    'Data were obtained from the NCI Genomic Data Commons. Five cancer types were selected: '
    'LUAD (493 tumor + 76 normal), LUSC (534 + 58), LIHC (398 + 57), KIRC (750 + 82), '
    'BRCA (1,010 + 109), totaling n = 3,567 samples in the pair-level analysis '
    'before the barcode audit (of the 3,596 expression-matrix samples, 3 do not appear in the '
    'assembled pair table, and 26 further samples appear only in tumor\u2013normal '
    'pairs; the pair table spans 3,593 unique barcodes). The ex-CC default cohort '
    'excludes the 32 cell-line-derived (CC) LIHC aliquots, leaving 3,535 samples '
    '(LIHC 366 tumor + 57 normal) for all reported analyses; the GTEx comparison '
    'and the reference-free composition fallback (Supplementary Note 8) instead use the '
    'full expression-matrix cohort (3,596 samples, e.g. KIRC 754 tumors). '
    'Normalization: TPM values from UCSC Xena, '
    'followed by log2(TPM + 1) transformation. For paired analysis, tumor-normal pairs were '
    'matched by patient barcode (TCGA-XX-XXXX format). Clinical metadata for stratified '
    'analyses were obtained from GDC (via the TCGAbiolinks R package) and the cBioPortal API.'
)

add_para('4.4 Highly Variable Gene (HVG) Selection', bold=True)
add_para(
    'Tabula Muris: Global HVG selection was performed using '
    'scanpy.pp.highly_variable_genes, with parameters flavor="seurat" and '
    'n_top_genes=2,000. The global HVG set was used for all pairwise comparisons '
    'in Phases 3.1-3.2. Tabula Sapiens: Pairwise HVG selection. For each cell type '
    'pair (CT_i, CT_j), the top-200 genes ranked by |mu_i - mu_j| (absolute log1p '
    'expression difference) were selected as identity genes, excluding HK genes. This '
    'avoids the dilution effect of HVG across comparisons involving 102 cell types. '
    'HVG count sensitivity: the Phase 3.2 sweep varied the identity/pathway weighting '
    'at a fixed global panel of 2,000 HVGs (Supplementary Table 1); no N_HVG grid was '
    'run on the mouse matrix. A diagnostic HVG-size sweep on Tabula Sapiens tested '
    'N_HVG in {2,000, 5,000, 10,000, 20,000} (notebooks/05b_phase33_diagnose.py). '
    'The pairwise scheme (human) uses N = 200 per-pair genes to maintain discriminative '
    'power with computational efficiency.'
)

add_para('4.5 Kang et al. IFN-beta PBMC (Perturbation Demonstration)', bold=True)
add_para(
    'Downloaded from GEO (GSE96583; Kang et al. 2018, Nature Biotechnology). '
    'The droplet arm was used: two 10x Genomics lanes from eight donors, '
    'lane 2.1 control (14,619 cells) and lane 2.2 IFN-beta-stimulated '
    '(14,446 cells, 6-hour stimulation), with donor assignment by genetic '
    'demultiplexing (demuxlet) provided by the original authors. QC '
    'filtering: only droplets annotated as singlets with a cell-type label '
    'were retained; Megakaryocytes were excluded; cell types with fewer '
    'than 50 cells in any (donor, condition) group were dropped '
    '(Dendritic cells). Result: 24,413 cells across six cell types '
    '(B cells, CD4 T, CD8 T, NK, CD14+ monocytes, FCGR3A+ monocytes). '
    'Ensembl gene identifiers were mapped to HGNC symbols via the HGNC '
    'custom download (23,503 unique symbols), and 1,099 HRT Atlas '
    'housekeeping genes were matched. Because all control cells reside in '
    'one lane and all stimulated cells in the other, condition and lane '
    'are confounded; this is disclosed in Supplementary Note 6 and does not affect '
    'the within-metric class comparison.'
)

doc.add_page_break()

# ===== Supplementary Notes (NC: citation order 1-15) =====

add_heading('Supplementary Note 1: Ground-Truth Simulation', 2)
add_para(
    'Semi-synthetic benchmark. To provide a known ground truth, perturbations of known '
    'magnitude were injected into a real single-cell background (Tabula Muris FACS marrow '
    'B cells, 1,848 cells). Each replicate resampled two independent groups of 200 cells '
    'from the same cell type, so the true functional divergence before injection is zero. '
    'The kept gene set mirrored the brain pipeline (1,064 matched HK genes plus the 5,000 '
    'non-HK genes with highest global means). Functional signal: multiplicative shift of '
    '2^delta (delta = 0.125-2) on a fixed module of 200 non-HK genes in group B. Neutral '
    'perturbations, injected separately: (i) 2^eta shift on HK genes in group A '
    '(eta = 0.25-1, neutral drift), (ii) extra Poisson noise across all genes in group A '
    '(epsilon = 0.3-1, technical batch noise). Six metrics were computed with the identical '
    'code path as the brain analysis: \u03c9, k_f, k_n, raw JS over the full kept gene set, '
    'cosine distance, and k_f/k_total. Signal scenarios used three independent module draws '
    '(seeds 42, 137, 2024). Detection thresholds were the 95th percentile of 200 baseline '
    'replicates (pure cell resampling) per metric, so type-I error and power refer to a '
    'common nominal 5% level. 1,750 replicates per background; scripts: '
    'notebooks/45_groundtruth_simulation.py (marrow B cells) and notebooks/49_groundtruth_sim_background2.py (skin keratinocyte stem cells; runtime about 1 minute each).'
)
add_para(
    'Type-I error under neutral perturbation. Under pure HK drift (eta = 0.25-1, pooled), '
    'exceedance rates were: \u03c9 0.000, k_f 0.007, k_n 0.813, raw JS 0.553, cosine 0.580, '
    'k_f/k_total 0.000. Exact Clopper-Pearson intervals: \u03c9 0/150 under pure HK drift '
    '(one-sided 95% upper bound 0.0198; 2/250 pooled neutral replicates, 95% CI '
    '[0.001, 0.029]); raw JS 0.553 (95% CI [0.470, 0.635]); cosine 0.580 (95% CI '
    '[0.497, 0.660]). '
    'Under global overdispersion noise (epsilon = 0.3-1, pooled): '
    '\u03c9 0.020 (95% CI [0.002, 0.070]), k_f 0.020, k_n 0.060, raw JS 0.040, cosine 0.040. Standard unnormalized '
    'metrics cannot distinguish neutral drift from functional divergence; \u03c9 and the '
    'ratio variants reject neutral drift almost perfectly.'
)
add_para(
    'Power for injected functional signal (detection rate, pooled over three module seeds; '
    'thresholds calibrated at the 95th percentile of the baseline distribution). '
    'delta = 0.125: \u03c9 0.013, k_f 0.013, raw JS 0.040, cosine 0.060. delta = 0.25: '
    '\u03c9 0.000, k_f 0.013, raw JS 0.053, cosine 0.060. delta = 0.5: \u03c9 0.000, k_f '
    '0.000, raw JS 0.140, cosine 0.100. delta = 1: \u03c9 0.000 (all three module seeds), '
    'k_f 0.013, raw JS 0.993, cosine 0.667. delta = 2: \u03c9 0.133 (per-seed 0.12-0.16), '
    'k_f 0.153, raw JS 1.000, cosine 1.000. The \u03c9 detection floor is structural: the '
    'per-pair top-200 selection saturates with noise under the null (median baseline k_f = '
    '0.025), so weak module shifts do not lift k_f above the selection floor, and \u03c9 '
    'inherits this as an upper-bound estimator. The baseline \u03c9 distribution on this '
    'background (mean 11.6, 95th percentile 20.8) reproduces the scale of the brain-internal '
    'split-half calibration baseline (9.73), supporting external validity.'
)
add_para(
    'Confounded scenarios (delta = 0.5 plus neutral HK drift). Detection rates: '
    'eta = 0.25: \u03c9 0.000, raw JS 0.260, cosine 0.140; eta = 0.5: \u03c9 0.000, raw JS '
    '0.960, cosine 0.940; eta = 1: \u03c9 0.000, raw JS 1.000, cosine 1.000. Neutral '
    'drift suppresses \u03c9 further through the inflated denominator while inflating the '
    'unnormalized metrics (which count drift as divergence).'
)
add_para(
    'Discrimination and robustness. ROC AUC for separating functional (delta \u2265 0.25) from '
    'neutral (HK drift or global overdispersion) replicates: \u03c9 0.804 > k_f 0.716 > '
    'raw JS 0.640 > cosine 0.584 > k_f/k_total 0.437 > k_n 0.213. Under a fourfold '
    'cell-count imbalance (n_B = 50, delta = 1), \u03c9 changed by \u221232% (8.47 versus 12.46) '
    'while k_f inflated by +67% and cosine by +108%; 30% dropout and a twofold depth '
    'difference produced no systematic shift in \u03c9. Module-size sensitivity at '
    'delta = 1: m = 50 (\u03c9 mean 11.99), m = 200 (12.46), m = 500 (7.31; large modules '
    'shift total library composition, which leaks into k_n and suppresses \u03c9). '
    'Interpretation: \u03c9 is a specificity-first screen; its construction rejects neutral '
    'drift, at the cost of bounded power for weak-to-moderate functional signals.'
)
add_para(
    'AUC interval methods (v52). The main-text AUC 95% CI [0.770, 0.838] is the DeLong '
    'interval on the 850-replicate ROC (600 signal, 250 neutral replicates). A module-seed '
    'cluster bootstrap (resampling the three module-seed clusters on the signal side plus '
    'iid neutral replicates, B = 5,000, seed 42) gives a near-identical interval '
    '[0.771, 0.836], so the DeLong caliber is robust to the clustered simulation design; '
    'fixed-specificity sensitivity values are tabulated in '
    'results/nc52_stats_auc_ci_methods.csv (script scripts/nc52_stats_resampling.py).'
)

add_para(
    'Second-background replication. The entire design was repeated in Tabula Muris FACS skin '
    'keratinocyte stem cells (1,371 cells; script notebooks/49_groundtruth_sim_background2.py; '
    'results/groundtruth_simulation_background2*.csv) with identical grids, module seeds, group '
    'sizes, and code path. Type-I error under pure HK drift: \u03c9 0.000, versus 0.780 for raw '
    'JS and 0.787 for cosine (both more inflated than in the marrow background); under global '
    'overdispersion noise: \u03c9 0.080, k_f 0.080. AUCs: \u03c9 0.908 > k_f 0.859 > raw JS 0.649 '
    '> cosine 0.608 > k_f/k_total 0.539 > k_n 0.207 (identical ordering to the marrow '
    'background). Detection power at delta = 1: \u03c9 0.913, k_f 0.927, raw JS 1.000; at '
    'delta = 2: \u03c9 0.993. Under the fourfold cell-count imbalance (n_B = 50, delta = 1), '
    'k_f retained higher power than \u03c9 (0.98-1.00 versus 0.04-0.20 at delta = 0.25 and '
    'delta = 1). Both backgrounds are Tabula Muris FACS samples of the same platform, so the '
    'replication establishes robustness across tissues and library depths within that platform, '
    'not across platforms.'
)

add_para(
    'Adversarial circularity scenarios. The neutral-drift null above places the null '
    'perturbation on HK genes, which is the same anchoring assumption that CKI itself '
    'makes; the type-I and AUC advantages above are therefore conditional on that '
    'assumption rather than evidence for it. Two adversarial scenarios quantify the '
    'consequences (script notebooks/75_sim_circularity_scenarios.py; results: '
    'results/sim_circularity_*.csv; same background, gene set, six-metric code path, '
    'and baseline null thresholds as above; three module seeds per scenario, 50 '
    'replicates each). S1, functional-on-HK: a functional module of 200 genes was '
    'drawn from the HK genes themselves and shifted by 2^delta (delta = 0.25, 0.5, 1, '
    '2; 600 replicates). \u03c9 detected none of these signals (rate 0.000 at every '
    'delta, all seeds), because an HK-located shift inflates k_n while k_f stays at '
    'the selection floor, driving \u03c9 down, away from its upper tail; k_n itself '
    'fires at 0.61 for delta = 0.25 and 1.00 thereafter, and the unnormalized metrics '
    'detect the signal at moderate-to-strong magnitude (k_total 0.06/0.11/0.95/1.00 '
    'and cosine 0.06/0.10/0.85/1.00 across the delta grid). CKI is thus structurally '
    'blind to functional signal located on the anchor genes - an unavoidable property '
    'of any HK-anchored normalization, and the mirror image of its claimed advantage. '
    'S2, neutral-on-nonHK: neutral drift (2^eta, eta = 0.25, 0.5, 1) was instead '
    'placed on a module of non-HK genes (450 replicates), i.e., drift on the wrong side '
    'of the anchor. \u03c9 remained at or below the nominal level (type-I error 0.020, '
    '0.007, 0.007 across the eta grid), whereas k_total false-positived at 0.060, '
    '0.147, and 1.000 and cosine at 0.060, 0.100, and 0.673. \u03c9 therefore trades a '
    'structural blind spot for HK-located signal for strong specificity against '
    'non-HK drift: it is conservative by construction, and its discrimination '
    'advantage holds exactly when functional signal lies off the anchor and drift on '
    'the anchor is neutral. Users whose perturbations of interest include '
    'housekeeping genes (e.g., metabolic reprogramming) should use unnormalized '
    'metrics alongside \u03c9.'
)

add_para('Second-background detail (migrated from the main text in v51): the skin k_f selection floor is lower than marrow (median 0.011 versus 0.025); at \u03b4 = 1, \u03c9 detection was 0.91 versus 0.00 in marrow, and under the fourfold cell-count imbalance k_f retained higher power (0.98\u20131.00 versus 0.04\u20130.20).')

add_heading('Supplementary Note 2: Small-Cluster Bootstrap Corrections for Region-Clustered CIs', 2)
add_para(
    'Several brain intervals rest on only 6\u20137 region clusters (Bergmann '
    'glia 7; choroid plexus 6), where the percentile cluster bootstrap '
    'under-covers. A Monte Carlo coverage study (2,000 simulations \u00d7 '
    'B = 999; nominal 95%) gives coverage 0.876 (7 clusters) and 0.873 (6 '
    'clusters) for the percentile interval, 0.816/0.806 for the wild '
    '(Rademacher) cluster bootstrap\u2014worse, because 2\u2076\u20132\u2077 '
    'sign combinations give coarse tails and the symmetric perturbation '
    'cannot reproduce the few-cluster skewness\u2014and 0.953/0.951 for the '
    'studentized bootstrap-t, which is therefore the recommended replacement '
    'for every statistic resting on \u2264 7 region clusters (seed 20260905; '
    'B = 5,000 on the real data).'
)
add_para(
    'Replacement 95% intervals (studentized bootstrap-t): Bergmann-glia '
    'class-mean \u03c9 13.56: [5.76, 28.59] (was percentile [8.49, 19.52])'
    '\u2014the lower bound now falls below the class baseline 9.08, so the '
    'above-baseline claim for Bergmann glia is downgraded to a qualitative '
    'statement (cross-region \u03c9 elevated in absolute terms but not '
    'separable from baseline at 7 regions; consistent with the joint '
    'calibrated-\u03c9 CI [0.99, 2.12], which already includes 1). Choroid '
    'plexus 37.76: [25.93, 76.30] (was [27.30, 56.19])\u2014the lower bound '
    'remains far above its baseline 10.66, so the choroid divergence claim '
    'stands. Astrocyte/Bergmann-glia calibrated gradient 5.99: [4.43, 7.69] '
    '(was joint percentile [4.12, 9.18])\u2014all three methods agree the '
    'lower bound exceeds 4, so the gradient claim remains quantitative. '
    'Script notebooks/89_cluster_boot_v45.py; report '
    'results/cluster_boot_v45_report.md.'
)

add_heading('Supplementary Note 3: Calibrated Omega Normalization', 2)
add_para(
    'The theoretical baseline \u03c9 = 1 (k_f = k_n) is never observed in practice because '
    'identity-gene selection (per-pair top-200 DE genes or HVGs) systematically inflates k_f '
    'relative to k_n. '
    f'Empirical calibration on split-half equivalent populations (mouse, 6 FACS control '
    f'populations with 50 independent random split-halves each; 300 split-half \u03c9 '
    f'values; Section 3.10) yielded a replicate-baseline mean \u03c9 = 7.70 (two-stage '
    f'population-resampled bootstrap 95% CI [6.38, 9.82], B = 5,000; the 300-value '
    f'intervals [7.37, 8.02]/[7.38, 8.02] are pseudo-replicated and superseded), and the legacy single-split '
    f'estimate 6.67 [4.24, 9.24] lies inside the widened CI and is '
    f'superseded. We introduce calibrated \u03c9: omega_cal = omega_obs / 7.70, which '
    'rescales all values so that equivalent populations yield omega_cal ~ 1.0. Given the width '
    'of the baseline CI (\u00b121% relative half-width), calibrated values carry roughly one '
    'significant figure of resolution and should '
    'be read as order-of-magnitude estimates rather than precise quantities. Under this '
    f'mouse-derived calibration: mouse controls yield omega_cal = 1.0, the brain global mean becomes omega_cal '
    f'\u2248 {_br["global_mean"] / 7.70:.0f} (raw {_br["global_mean"]:.2f}; range 4.8\u20135.2 across the baseline CI), and the most divergent brain cell type '
    f'({_br["gradient_highest_ct"].lower()}s) yields omega_cal '
    f'\u2248 {_br["gradient_highest_omega"] / 7.70:.0f} (raw {_br["gradient_highest_omega"]:.2f}). '
    f'A scheme-matched split-half calibration performed inside the brain atlas itself (29 populations '
    f'with at least 200 nuclei; B = 50 random splits per population) gave an internal baseline of '
    f'{_brain_sh_mean:.2f} (95% bootstrap CI [{_brain_sh_ci[0]:.2f}, {_brain_sh_ci[1]:.2f}]), approximately 1.3-fold '
    'higher than the mouse-derived factor, indicating that the mouse-derived calibration '
    'overstates omega_cal in the brain dataset. Under the brain-internal baseline, the brain '
    f'global mean corresponds to omega_cal \u2248 {_br["global_mean"] / _brain_sh_mean:.1f}, the most divergent class to '
    f'omega_cal \u2248 {_br["gradient_highest_omega"] / _brain_sh_mean:.1f}, and the most constrained class '
    f'({_br["gradient_lowest_ct"]}) to omega_cal \u2248 {_br["gradient_lowest_omega"] / _brain_sh_mean:.1f} (raw '
    f'{_br["gradient_lowest_omega"]:.2f}): the most regionally constrained class sits at, not above, the '
    'split-half expectation for equivalent brain populations, so the statement that all ten '
    'non-neuronal classes diverge beyond the split-half baseline holds only under the '
    'mouse-derived calibration and is not supported under brain-internal calibration. '
    'In Tabula Sapiens, the analogous scheme-matched internal baseline was '
    f'{_ts_sh_mean:.2f} (95% bootstrap CI [{_ts_sh_ci[0]:.2f}, {_ts_sh_ci[1]:.2f}]; 71 populations from the largest donor per group), which lies inside the '
    'updated mouse-derived CI [6.38, 9.82], so the mouse-derived calibration factor is transferable to '
    'the Tabula Sapiens dataset but not to the brain atlas, and omega_cal should be treated as a '
    'dataset-relative quantity rather than a universal constant. '
    'A single brain-wide baseline also averages over marked between-class heterogeneity: '
    f'class-specific split-half baselines derived from the same 29 split-half populations range from '
    f'{_pc_bmin:.2f} ({_pc_bmin_ct.lower()}) to {_pc_bmax:.2f} ({_pc_bmax_ct.lower()}), a '
    f'{_pc_bmax/_pc_bmin:.2f}-fold spread, and the split-half k_f floor itself varies roughly '
    '40-fold across classes (from 0.0001 in oligodendrocytes to 0.020 in committed '
    'oligodendrocyte precursors), so the equivalent-population expectation is a class-specific '
    'quantity in both components rather than a single atlas-wide constant; each class '
    'baseline rests on only 2-3 split-half populations (50 splits per population), so the '
    'calibrated levels carry non-trivial denominator uncertainty (two-stage 95% CIs span, '
    f'for example, [{_pc_astro_base_ci[0]:.2f}, {_pc_astro_base_ci[1]:.2f}] for astrocytes and '
    f'[{_pc_bg_base_ci[0]:.2f}, {_pc_bg_base_ci[1]:.2f}] for Bergmann glia, the latter from only '
    f'{_pc_bg_nreg} populations). Under per-class '
    f'baselines the astrocyte-to-Bergmann-glia gradient is {_pc_grad:.2f} (95% CI '
    f'[{_pc_grad_ci[0]:.2f}, {_pc_grad_ci[1]:.2f}] under a joint region-clustered bootstrap '
    'that resamples region pairs and split-half populations together, propagating both '
    'sources of calibration uncertainty; the narrower i.i.d.-numerator CI '
    f'[{_pc_grad_ci_old[0]:.2f}, {_pc_grad_ci_old[1]:.2f}] ignores within-region correlation '
    'and is anti-conservative), essentially unchanged from the raw 6.10 '
    'because the two classes\u2019 own baselines nearly coincide (9.26 vs 9.08), while the calibrated '
    f'levels compress: astrocytes yield omega_cal = {_pc_astro:.1f} (95% CI '
    f'[{_pc_astro_ci[0]:.1f}, {_pc_astro_ci[1]:.1f}]) and Bergmann glia omega_cal = {_pc_bg:.2f} '
    f'(joint 95% CI [{_pc_bg_ci[0]:.2f}, {_pc_bg_ci[1]:.2f}], which no longer excludes 1). Bergmann glia is therefore borderline '
    f'against its own class baseline (region-clustered CI [{_pc_bg_rc[0]:.2f}, {_pc_bg_rc[1]:.2f}] '
    f'versus baseline {_pc_bg_base:.2f}; the class contributes only 7 regions, so the interval\u2019s '
    'lower edge is itself sensitive to bootstrap resampling): under per-class baselines '
    f'{_pc_n_div["per_class"]} of 10 classes have region-clustered class-mean CIs excluding their '
    'own baselines (versus '
    f'{_pc_n_div["brain_global"]} of 10 under the single brain-wide baseline and '
    f'{_pc_n_div["mouse"]} of 10 under the mouse-derived factor), and under the joint '
    'region-clustered bootstrap of the calibrated ratio (notebooks/81_perclass_uncertainty.py, '
    f'B = 5,000) {_pc_n_div_joint} of 10 classes have joint 95% CIs excluding 1, with Bergmann glia the '
    'borderline exception under both internal calibrations; its excess is small (+49%) and '
    'rests on only 21 pairs across 7 intra-cerebellar regions, so we read it as '
    '"at, or marginally above, its own expectation" rather than clear divergence. Because a shared '
    'calibration constant cancels in any ratio of class means, external calibration changes the '
    'levels (astrocytes 10.75 under mouse-derived versus 8.51 under brain-internal) but not the '
    'gradient ratio; only class-specific baselines move the ratio, and then only slightly. We '
    'therefore recommend per-class split-half calibration whenever within-dataset class '
    'contrasts are the target, and treat omega_cal as dataset- and class-relative throughout. '
    'The calibrate_omega() function is available in the CKI package (cki.calibrate_omega). '
    'Both raw and calibrated \u03c9 values are reported in all key results. (Supplementary Fig. 2.)'
)
add_para(
    'Small-cluster correction (Supplementary Note 2). A Monte Carlo coverage study '
    'shows that the percentile region-clustered bootstrap under-covers by '
    '7\u20138 points at 6\u20137 clusters (coverage 0.876/0.873 at nominal '
    '0.95), so the Bergmann-glia and choroid-plexus class-mean CIs quoted '
    'above are too narrow. Under the recommended studentized bootstrap-t '
    '(coverage 0.953/0.951): Bergmann glia 13.56 [5.76, 28.59] (was '
    '[8.49, 19.52])\u2014the lower bound now falls below the class baseline '
    '9.08, so the above-baseline claim is downgraded to a qualitative '
    'statement (cross-region \u03c9 elevated in absolute terms, not '
    'separable from baseline at 7 regions); choroid plexus 37.76 [25.93, '
    '76.30] (was [27.30, 56.19])\u2014the lower bound remains far above '
    'its baseline 10.66, so the choroid claim stands; the '
    'astrocyte/Bergmann-glia gradient 5.99 [4.43, 7.69] (was [4.12, 9.18])'
    '\u2014the gradient claim remains quantitative.'
)

add_heading('Supplementary Note 4: Ratio-Estimator Bias\u2013Variance Characterization', 2)
add_para(
    '\u03c9 = k_f/k_n is a ratio of two JS divergences, and ratio estimators '
    'are upward biased and heavy right-tailed when the denominator is small. '
    'On the 1,450 split-half replicates of the brain-internal calibration '
    '(both halves of each split are the same population, so E[k_f/k_n] '
    'versus E[k_f]/E[k_n] isolates pure ratio bias), the bias is small and '
    'null-calibrated: median +0.2% across the 29 class \u00d7 region groups '
    '(pooled \u22121.8%), tracked almost exactly by the second-order '
    'delta-method prediction (Spearman \u03c1 = 0.99 for bias, 1.00 for SD). '
    'The largest upward bias sits in the smallest-denominator bin (k_n < '
    '10\u207b\u2074: +6.5%; 10\u207b\u2074 \u2264 k_n < 10\u207b\u00b3: '
    '\u22128.3%; k_n \u2265 10\u207b\u00b3: +1.5%), where delta-method '
    'theory predicts it; because the calibration baseline is computed with '
    'the same estimator on the same scale of k_n, this bias is absorbed '
    'into the baseline. The null distribution is heavy-tailed (skew 2.28, '
    'excess kurtosis 9.14, P99/P50 = 2.1), which widens intervals but does '
    'not shift calibrated conclusions.'
)
add_para(
    'On the 31,764 brain pairs, the astrocyte/Bergmann-glia gradient is '
    'robust to the summary statistic (6.10 mean, 6.00 median, 6.09 10% '
    'trimmed; 10-class ranking agreement Spearman \u03c1 \u2265 0.976), so '
    'the mean-based headline is not a heavy-tail artifact. Near-zero '
    'denominators are rare and non-influential: 1 pair (0.003%) has k_n < '
    '10\u207b\u2074 and 141 (0.44%) have k_n < 3 \u00d7 10\u207b\u2074; '
    'excluding all pairs with k_n < 5 \u00d7 10\u207b\u2074 (1,141 pairs, '
    '3.59%) moves the gradient slightly up, to 6.52, with the class ranking '
    'unchanged (\u03c1 = 1.000), and even dropping the bottom 20% by k_n '
    'leaves \u03c1 = 0.964\u2014the 6.10-fold headline is, if anything, '
    'conservative with respect to small-denominator pairs. Script '
    'notebooks/88_ratio_estimator_v45.py; report '
    'results/ratio_estimator_biasvar_v45_report.md.'
)

add_heading('Supplementary Note 5: Non-HK-Anchored Neutral Drift Controls', 2)
add_para(
    'The ground-truth simulation (Supplementary Note 1) defines neutral drift as a '
    'multiplicative shift on housekeeping genes\u2014the same set \u03c9 uses '
    'as its denominator\u2014so the headline specificity (FPR 0.00 versus '
    '0.55\u20130.58 for raw JS and cosine) could be a construction artifact. '
    'Two non-HK-anchored neutral models on the identical background and '
    'scheme (30 replicates per condition; thresholds at the 95th percentile '
    'of 200 pure-resampling baselines; Clopper-Pearson CIs) answer this. N0 '
    '(internal control, original HK drift) reproduces the original run '
    '(\u03c9 0.000; raw JS 0.556; cosine 0.600, pooled over \u03b7).'
)
add_para(
    'N1 (multiplicative drift moved off HK genes: random low-variance non-HK '
    'sets, bottom-half CV, greedy log-mean matched to the HK set, n = 1,064 '
    'genes, 3 random sets): \u03c9 stays calibrated\u2014FPR 0.067, 0.011, and '
    '0.000 at \u03b7 = 0.25, 0.5, and 1.0, versus raw JS 0.067/0.811/1.000 '
    'and cosine 0.089/0.878/1.000 at the same amplitudes. The /1e4 '
    'renormalization propagates the library inflation into a uniform '
    'compositional scaling that k_n absorbs, so \u03c9\u2019s specificity comes '
    'from its ratio structure, not from the drift being HK-anchored. Supplementary Note 1\u2019s earlier non-HK drift scenario (type-I error 0.020) used a '
    'different, non-expression-matched non-HK module; N1 is the stricter '
    'expression-matched control. N2 (composition-preserving gene-identity '
    'swap of non-HK expression profiles within one group; 0.25\u20131 \u00d7 '
    'n_hk swapped genes, 3 random pairings): every metric fires at FPR = '
    '1.00. The swap preserves library size and the expression-value multiset '
    'exactly, so k_n sees no compositional signal while the swapped genes '
    'dominate the per-pair top-200 set and k_f fires. Whether N2 counts as '
    'neutral is debatable\u2014reassigning which gene carries which '
    'expression level is precisely a gene-identity-specific change, which '
    '\u03c9 is designed to detect\u2014but under it \u03c9 behaves no worse '
    'than anchor-free global metrics. The FPR = 0.00 figure thus pertains '
    'to compositional/multiplicative neutral drift, whether HK- or '
    'non-HK-anchored. Script notebooks/90_nonhk_drift_v45.py; report '
    'results/nonhk_drift_v45_report.md.'
)

add_heading('Supplementary Note 6: Real Perturbation Demonstration (Kang et al. IFN-beta PBMC)', 2)
add_para(
    'Purpose and dataset. To test \u03c9 on a real perturbation with known '
    'ground truth, we re-analyzed the droplet arm of Kang et al. 2018 '
    '(GEO: GSE96583): peripheral blood mononuclear cells from eight donors, '
    'split into control and 6-hour IFN-beta-stimulated conditions and '
    'captured in two 10x lanes (lane 2.1 control, 14,619 cells; lane 2.2 '
    'stimulated, 14,446 cells), with donor assignment by genetic '
    'demultiplexing provided by the original authors. Singlets with '
    'annotated cell types were retained (24,413 cells across six cell '
    'types; Megakaryocytes excluded; Dendritic cells dropped for '
    'insufficient per-group cells). Ensembl gene identifiers were mapped '
    'to HGNC symbols via the HGNC custom download; 23,503 unique symbols '
    'and 1,099 HRT Atlas housekeeping genes were matched.'
)
add_para(
    'Design. Pseudobulks were computed per (donor, condition) from raw '
    'counts, normalized to 10,000 counts per pseudobulk, and log1p-'
    'transformed. Two comparison classes were defined: the perturbation '
    'class (stimulated versus control within donor, 4-8 pairs per cell '
    'type) and the donor-drift class (donor versus donor within '
    'condition, 10-56 pairs per cell type); a split-half baseline (six '
    'random half-splits per group) anchored the calibrated scale. All '
    'metrics used the per-pair top-200 DE hybrid scheme (k_n on the HK '
    'set, k_f on the top-200 non-HK genes by absolute mean difference, '
    're-selected per pair). Significance of the within-donor perturbation '
    'effect used condition-label permutation within donor (B = 1,000; '
    'genes re-selected at every permutation; one-sided upper tail). Class '
    'separability was summarized as the exact rank AUC of each metric '
    'within each cell type. Because all control cells sit in one lane and '
    'all stimulated cells in the other, the condition effect is '
    'confounded with lane; donor-drift pairs are within-lane, so the '
    'comparison across metrics is internally consistent but the design '
    'does not separate condition from capture effects.'
)
add_para(
    'Results. Median \u03c9: stimulated-control 19.3-33.4, donor-donor '
    '9.9-25.7, split-half 6.7-18.9 (omega_cal for the perturbation class '
    '1.8-3.4 versus donor-drift 0.9-2.7). AUC (perturbation versus '
    'donor-drift): \u03c9 0.551-0.922, k_f 0.743-1.000, raw JS 0.792-1.000. '
    'The permutation test reached raw P < 0.05 in 15 of 37 donor-level '
    'tests (no multiplicity correction; under the global null roughly '
    'two of 37 tests would cross raw P < 0.05, so the aggregate excess '
    'is informative while individual tests are not). The components are '
    'consistent with the metric ordering: IFN-beta '
    'stimulation raises median k_n 1.2-5.7-fold above the donor-drift '
    'level (ACTB and GAPDH fall roughly 40% in stimulated cells, a '
    'magnitude consistent with the anchor mechanism but not separable '
    'from the lane effect) while '
    'raising median k_f 1.6-6.8-fold, so the ratio partially cancels the '
    'signal; in CD14+ monocytes, where the k_n rise is largest (5.7-fold), '
    'the \u03c9 AUC falls to 0.551 while k_f retains 0.984. Within the '
    'lane-confounded design this supports the '
    'anchor-visibility boundary: perturbations '
    'that touch the housekeeping anchor deflate \u03c9, and k_f-only with '
    'a design-matched null is the more honest statistic in that regime '
    '(Supplementary Fig. 3). '
    'Script: notebooks/79_kang_ifnb_demo.py; outputs: '
    'results/kang_ifnb_demo_pairs.csv (709 pairs), '
    'results/kang_ifnb_demo_summary.json.'
)

add_para('Effect-scale detail (migrated from the main text in v51): median within-donor stimulated-versus-control \u03c9 exceeded median donor-versus-donor \u03c9 by 1.1\u20132.0-fold.')

add_heading('Supplementary Note 7: Fixed Gene-Panel Ablation', 2)
add_para(
    'Design. To test whether the brain conclusions depend on the per-pair circular '
    'selection of k_f genes (top-200 genes ranked by the absolute difference of the '
    'same two pseudobulks on which k_f is computed), the entire observed brain '
    'landscape was recomputed under four gene-selection schemes with identical keep '
    'gene set, pseudobulks, and k_n: S0, the reported per-pair top-200 scheme '
    '(circular selection; reference); S1, a fixed panel of the 2,000 non-HK genes '
    'with the highest global mean expression; S2, a leave-pair-out panel in which the '
    'top-200 genes for a pair are selected by the mean absolute difference over all '
    'other region pairs of the same cell type (adaptive but not circular for the '
    'tested pair; note that S2 is not fully independent either, because the panel '
    'still aggregates regional-effect genes from the other region pairs of the '
    'same cell type); S3, all 5,000 non-HK genes of the keep set (no selection). The '
    'reference implementation reproduced the reported landscape exactly (maximum '
    'per-pair \u03c9 difference 6.4e-13 over 31,764 pairs). A scheme-matched '
    'block-shuffle null (B = 200) was rerun under S2. Script: '
    'notebooks/46_fixed_panel_ablation.py (runtime about 28 minutes).'
)
add_para(
    'Rank robustness. Pair-level Spearman correlation with S0: rho = 0.918 (S1), '
    '0.937 (S2), 0.931 (S3). Ordering of the ten class means: rho = 0.90 (S1), 0.99 '
    '(S2), 0.93 (S3); under S2 the only change was a swap of the adjacent '
    'Bergmann-glia and vascular means. Astrocyte-to-Bergmann-glia ratio: 6.10 (S0) versus 7.67 '
    '(S1), 6.53 (S2), 6.57 (S3) - the gradient is preserved under the '
    'non-circular adaptive panel, because non-circular panels deflate \u03c9 more '
    'strongly in transcriptionally constrained classes. Under the S2-matched '
    'block-shuffle null, astrocytes, OPCs and committed OPCs reached the permutation floor '
    '(P \u2264 1/(B + 1) = 0.005); fibroblasts remained significant (P = 0.020, versus 0.030 '
    'reported); vascular cells reached significance (P = 0.035, versus 0.115 '
    'reported, non-significant under the primary null); ependymal cells were not significant (P = 0.164); and the remaining '
    'classes stayed clearly non-significant (microglia P = 0.796, oligodendrocytes '
    'P = 0.876, choroid plexus P = 0.562, Bergmann glia P = 0.980). The four primary '
    'classes are stable across all three null variants; ependymal and vascular '
    'appear only under one variant each and are not claimed.'
)
add_para(
    'Circularity inflation and scale. On the same pairs, the circular panel '
    'inflated k_f by a median of 1.61-fold relative to the leave-pair-out panel '
    '(IQR 1.27-2.07) and by 6.1- to 7.3-fold relative to the fixed and unselected '
    'panels (which also differ in panel composition). The absolute \u03c9 scale is '
    'therefore scheme-specific (grand mean 38.55 for S0 versus 6.5, 26.5, and 5.3 '
    'for S1-S3). Rank-based conclusions are robust: the multiplicative-residual '
    'ranking correlated at rho = 0.86-0.88 across schemes, and S2 retained 32 of '
    '50 (64%) of the S0 residual < 0.3 candidate pairs. Absolute tier cutoffs '
    '(\u03c9 < 15/25/35) are calibrated to the S0 scale and do not transfer across '
    'schemes: candidate lists defined by absolute \u03c9 thresholds are not '
    'comparable across gene-selection schemes. Outputs: '
    'results/fixed_panel_ablation_pairs.csv, results/fixed_panel_ablation_ct.csv, '
    'results/fixed_panel_ablation_null_<CT>.npy, results/fixed_panel_ablation_summary.json.'
)

add_para('Panel grand means and ranking robustness (migrated from the main text in v51): 38.55 reported, 26.5 leave-pair-out, 6.5 fixed, 5.3 unselected; the circular panel inflated k_f by a median 1.61-fold relative to leave-pair-out and by 6.1- and 7.3-fold relative to the fixed and unselected panels, and the multiplicative-residual ranking correlated at \u03c1 = 0.86\u20130.88 across schemes.')

add_heading('Supplementary Note 8: TCGA composition-contribution check for the NN/TT k_n reversal', 2)
add_para(
    'The TCGA analysis reports that normal-normal (NN) pairs have systematically lower '
    'k_n than tumor-tumor (TT) pairs (median TT/NN ratio 2.2-3.7x across the five '
    'cancer types). Because bulk tumor samples differ in cellular composition, this '
    'reversal could in principle be a purity artifact. We therefore regenerated '
    'sample-labelled NN/TT pairs with the per-cancer pipeline of the main analysis '
    '(per-cancer gene loading and mean TPM \u2265 0.5 filtering, log2(TPM+1), HRT Atlas HK '
    'genes, top-200 abs-diff identity genes, kn_floor = 1 x 10^-4, seed 42; TT capped at '
    '2,000 pairs per cancer type, all NN pairs; 25,306 pairs in total) and scored each '
    'sample for four lineage marker panels: immune (CD3D, CD3E, CD8A, GZMB, NKG7, '
    'MS4A1, CD79A), myeloid (CD68, CD163, LST1, FCGR3A, C1QA), stromal (COL1A1, '
    'COL1A2, DCN, LUM, FAP, VIM), and epithelial (EPCAM, KRT8, KRT18, KRT19), as the '
    'mean log2(TPM+1) over mapped panel genes, z-scored within each cancer type; the '
    'myeloid panel was added in a second revision because the initial three-panel '
    'check omitted myeloid markers despite myeloid infiltration being a known feature '
    'of tumors. The reversal replicates exactly (median TT/NN k_n ratio 2.18, '
    '2.53, 2.18, 3.70, and 2.79 for LUAD, LUSC, LIHC, KIRC, and BRCA on this '
    'composition-check pair set of 25,306 NN+TT pairs; on the main '
    '35,306-pair linear table the corresponding medians are 2.60, 2.53, '
    '2.08, 3.61, and 2.78\u2014the difference is the pair set, not the '
    'estimator; all '
    'Mann-Whitney P < 10^-90). Composition differences are real and directional: the '
    'median |Delta z| between pair members is 1.33-1.46-fold larger for TT than NN '
    'pairs across the original three panels (all P < 10^-300), and with the myeloid '
    'panel included the overall four-panel |Delta z| is still 1.24-fold larger for TT '
    'pairs (median 0.834 vs 0.673; P = 9 x 10^-77); notably, the myeloid |Delta z| '
    'itself does not differ between TT and NN pairs (median 0.749 vs 0.747, ratio '
    '1.003, P = 0.99), so myeloid composition shifts are not preferentially a '
    'tumor-pair phenomenon in these data. Within TT pairs, k_n correlates with the '
    'overall four-panel composition difference (Spearman rho = 0.23-0.52 per cancer '
    'type; pooled rho = 0.387, P < 10^-300; three-panel pooled rho = 0.377). '
    'In OLS regressions of log k_n on pair type plus the composition deltas (softmax '
    'caliber; superseded by the linear-normalization update at the end of this note, '
    'the authoritative caliber for the regression and correlation estimates cited in '
    'the manuscript), the '
    'tumor-pair coefficient attenuation depends materially on the panel: the original '
    'three-panel model attenuated the coefficient by +5.7% pooled (95% CI [+2.7%, '
    '+8.7%]; per cancer type +2%, +4%, +39%, +23%, and \u221212%), whereas the four-panel '
    'model including the myeloid markers attenuates it by \u22120.5% pooled (95% CI '
    '[\u22123.2%, +2.6%]; median \u22120.4%), i.e., the pooled tumor-pair coefficient is '
    'essentially unchanged after composition adjustment. All regression uncertainty '
    'intervals are sample-level cluster bootstraps (B = 200): within each cancer type, '
    'tumor and normal samples are resampled with replacement, a pair is retained when '
    'both members are drawn, weighted by the product of the two members resampling '
    'multiplicities, and the weighted OLS is recomputed; this respects the dependence '
    'structure that each sample contributes to many pairs (the naive pair-level '
    'standard errors, which treat 25,306 pairs as independent, overstate precision '
    'and are not used for inference); at B = 200 resamples the Monte-Carlo error '
    'of an endpoint of the resampling distribution is roughly 1-2 percentage '
    'points, small relative to the reported interval widths, and the pooled '
    '[\u22123.2%, +2.6%] interval is interpreted only as excluding large pooled '
    'attenuation, not as a precise point estimate. Per-cancer four-panel attenuation is strongly '
    'heterogeneous: LUAD \u22122.3% (95% CI [\u22127.6%, +4.8%]), LUSC \u22129.7% ([\u221228.4%, +6.7%]), '
    'LIHC +33.5% ([+23.0%, +46.9%]), KIRC +19.6% ([+14.6%, +25.7%]), and BRCA \u221214.0% '
    '([\u221223.2%, \u22125.7%]), so composition covariates absorb a substantial share of the '
    'tumor-pair coefficient in LIHC and KIRC but not in the other cancer types, and '
    'the pooled near-zero estimate masks this heterogeneity. Two caveats bound the '
    'interpretation. First, marker panels are noisy proxies for true cellular '
    'composition (classical measurement error attenuates the covariate coefficients), '
    'so these attenuation estimates are lower bounds on the true composition '
    'contribution; the pooled excess of tumor-pair k_n is not fully explained by a '
    'noisy marker-panel proxy, but neither can a marker-panel regression exclude '
    'composition as the driver. Second, the per-cancer heterogeneity itself (from '
    '\u221214% to +34%) argues against a single universal explanation. Plausible '
    'contributors to the residual include tumor-specific housekeeping-gene '
    'dysregulation and RNA-quality differences, and single-cell or '
    'deconvolution-based validation remains necessary. Scripts: '
    'notebooks/73_tcga_composition_check.py (three-panel) and '
    'notebooks/74_tcga_composition_v2.py (four-panel + cluster bootstrap); results: '
    'results/tcga_composition_check.{csv,txt}, results/tcga_composition_pairs.csv, and '
    'results/tcga_composition_v2.{csv,txt}.'
)
add_para(
    'Linear-normalization update (authoritative caliber, ex-CC default '
    'cohort, v52). The composition check '
    'was re-run on the ex-CC '
    'linear-normalization pair table of Section 1.7 (script '
    'notebooks/nc52_tcga_composition_excc.py, mirroring script 74 with '
    'the four marker panels and the sample-level cluster bootstrap; '
    'B = 1,000, seed 42; 25,015 ex-CC pairs with the 291 CC-touching pairs '
    'dropped and the CC samples also excluded from the z-score '
    'standardization population; '
    'outputs results/nc52_tcga_composition_excc.{csv,txt}); '
    'the pre-exclusion run is '
    'archived as results/superseded/tcga_composition_v44.{csv,txt}. '
    'All conclusions are '
    'unchanged: tumor\u2013tumor pairs show larger composition differences than '
    'normal\u2013normal pairs (median |\u0394z| 1.305-fold for the three-panel '
    'composite, P = 2.63 \u00d7 10\u207b\u00b9\u00b3\u2075, and 1.216-fold with '
    'the myeloid panel included, P = 4.67 \u00d7 10\u207b\u2076\u2078; the '
    'myeloid panel alone shows no tumour excess, ratio 1.001, P = 0.982); '
    'pooled four-panel attenuation \u22120.9% (cluster-bootstrap '
    'median \u22120.8%, 95% CI [\u22124.3%, +2.5%]); per-cancer attenuation '
    'LIHC +44.1% [+29.9%, +60.0%], KIRC +19.7% [+14.5%, +25.3%], BRCA '
    '\u221215.9% [\u221224.5%, \u22127.3%], LUAD \u22122.0% [\u22128.0%, +5.1%], LUSC '
    '\u22129.0% [\u221226.6%, +6.1%]; the within-TT correlation of k_n with the composition '
    'difference is Spearman \u03c1 = 0.380 pooled (n = 9,709 pairs, '
    'P < 10\u207b\u00b3\u2070\u2070; per-cancer 0.223\u20130.513, '
    'n = 2,000 per cancer except LIHC n = 1,709, all P \u2264 6.3 \u00d7 '
    '10\u207b\u00b2\u00b3; these correlation '
    'P-values treat pairs as independent and are reported as descriptive only, '
    'with the cluster bootstrap carrying the inferential weight). Composition '
    'covariates still absorb a substantial '
    'share of the tumor-pair coefficient in LIHC and KIRC but not in the '
    'other cancer types, and the pooled near-zero estimate still masks this '
    'heterogeneity. These linear-normalization estimates are the ones cited in '
    'the manuscript.'
)

add_para('Purity sensitivity detail (migrated from the main text in v51): high-purity-half comparisons increased the NN/TT \u03c9 ratio in all five cancer types (e.g. LUAD 2.46 \u2192 2.86, NN/TT \u03c9 ratios, not k_n fold-changes); per-tumor k_n correlated negatively with admixture, r = \u22120.23 to \u22120.42 across the five cancer types (range restored to the SI in v51r2).')
add_para(
    'GTEx healthy reference (v52). To separate tumor-specific housekeeping '
    'elevation from a field effect, GTEx V8 gene-level TPM (gtexportal.org; '
    'lung n = 288, liver n = 110, kidney cortex n = 28, breast n = 179 after '
    'QC and seed-42 subsampling to \u2264 300 per tissue) was processed with '
    'the identical k_n pipeline (HRT Atlas HK panel, linear (TPM+1)/\u03a3 '
    'mapping, kn_floor = 1 \u00d7 10\u207b\u2074, seed 42; script '
    'notebooks/nc52_gtex_kn.py; results/nc52_gtex_kn_by_grouptype.csv). '
    'Median k_n by pair type: lung GTEx\u2013GTEx 1.14 \u00d7 10\u207b\u00b3 '
    'versus adjacent\u2013adjacent 9.7 \u00d7 10\u207b\u2074 versus '
    'tumor\u2013tumor 2.50 \u00d7 10\u207b\u00b3; liver 1.98 \u00d7 '
    '10\u207b\u00b3 / 1.92 \u00d7 10\u207b\u00b3 / 3.98 \u00d7 '
    '10\u207b\u00b3; breast 9.1 \u00d7 10\u207b\u2074 / 8.7 \u00d7 '
    '10\u207b\u2074 / 2.41 \u00d7 10\u207b\u00b3\u2014in all three organs '
    'the adjacent-normal baseline is at the healthy level (healthy/adjacent '
    '\u2248 1.0\u20131.2; in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU '
    'P = 3.8 \u00d7 10\u207b\u2075, with a heavier adjacent upper tail) while tumor is 2.0\u20132.8-fold higher (TT \u226b '
    'NN, P \u2264 3.2 \u00d7 10\u207b\u2078\u2074), so the elevation is tumor-specific rather than a '
    'field effect. Kidney is the exception: GTEx cortex k_n (2.38 \u00d7 '
    '10\u207b\u00b3) \u2248 tumor (2.60 \u00d7 10\u207b\u00b3) \u226b '
    'adjacent (7.2 \u00d7 10\u207b\u2074), with only n = 28 and very high '
    'variance (GTEx kidney autolysis is documented), so no conclusion is '
    'drawn for KIRC. Cross-cohort GTEx\u2013adjacent pairs show k_n elevated '
    'to tumor levels in every organ (P \u2264 1.4 \u00d7 10\u207b\u00b2'
    '\u2076), a cohort-level technical effect; mechanistic claims therefore '
    'rest on within-cohort orderings only. Pair-level P values in this GTEx comparison treat pairs as independent and are descriptive only.'
)

add_para(
    'Reference-free composition fallback (v52). Full deconvolution tools were not executable '
    'in the offline revision environment (CIBERSORTx requires an online API token; BayesPrism '
    'is not installed), so a reference-free non-negative least-squares fallback was run on the '
    'full expression-matrix cohort (LIHC 366 and KIRC 754 tumors; seed 42, 60 markers per '
    'compartment): each tumor is decomposed into endothelial, epithelial, immune, and residual '
    'fractions, and the non-parenchymal fraction is correlated with per-tumor k_n. The '
    'estimator itself is reproducible (split-half Spearman \u03c1 = 0.934 LIHC, 0.964 KIRC), but the '
    'non-parenchymal fraction tracks k_n only weakly (Spearman \u03c1 = 0.20 LIHC, 0.26 KIRC), so '
    'measurable composition shifts explain at most a small share of the per-tumor k_n '
    'elevation\u2014consistent with the marker-panel check above. Script: '
    'notebooks/nc52_tcga_deconv_feasibility.py; outputs: '
    'results/nc52_tcga_deconv_feasibility.{csv,json} and '
    'results/nc52_tcga_deconv_{lihc,kirc}_pertumor.csv.'
)

add_heading('Supplementary Note 9: k_f-only Ordering Controls (Cross-Organ Ranking and TCGA Severity)', 2)
add_para(
    'Purpose. Two ordering claims in the manuscript rest on the ratio '
    '\u03c9 = k_f / k_n: the cross-organ conservation ranking of cell types '
    '(Table 1 / Fig. 5) and the TCGA clinical-severity gradients (Edmondson '
    'grade, PAM50, LUAD mutation strata). This note reports the control in '
    'which each ordering is recomputed using k_f alone (and k_n alone), with '
    'the identical pipeline otherwise, to separate functional-divergence '
    'signal from denominator effects.'
)
add_para(
    'k_n-permutation floor (v52; cited in the main-text Discussion). To test whether the '
    'observed \u03c9\u2013k_f correlation is mathematically forced by the shared k_f numerator, k_n was '
    'permuted across pairs (B = 1,000, seed 42) and the floor correlation '
    'corr(k_f/k_n_perm, k_f) computed. On the full-inventory human pair set (5,151 pairs, the '
    '102-entry inventory before the 99-entry filter that yields the 4,851 analyzed pairs), the '
    'floor is 0.524 (95% CI [0.506, 0.541]) while the observed Spearman correlation is '
    '0.089\u2014far below the floor, so the structured baseline decorrelates \u03c9 from k_f. On the '
    'mouse full matrix (703 pairs) the floor is 0.857 [0.843, 0.870] and the observed 0.821 '
    'sits essentially at it: the high mouse \u03c9\u2013k_f correlation is mathematically forced and '
    'dataset-dependent, not biological coupling. Script: scripts/nc52_stats_resampling.py; '
    'output: results/nc52_stats_omega_kf_math_floor.csv.'
)
_a = _kfo['part_a']
add_para(
    f"Cross-organ ranking (Tabula Sapiens). The exact phase-3.5 pipeline "
    f"(largest-donor pseudobulks, per-pair top-200 non-HK gene selection) was "
    f"re-run on the {_a['n_pairs']} same-cell-type cross-organ pairs across "
    f"{_a['n_ct']} cell types; it reproduces the published per-cell-type mean "
    f"\u03c9 values to within {_a['sanity_max_delta_vs_phase35']:.1e}. "
    f"Agreement between the \u03c9 and k_f orderings is weak at the cell-type "
    f"level: Spearman r = {_a['spearman_ct_omega_kf']['r']:.2f} "
    f"(P = {_a['spearman_ct_omega_kf']['p']:.2f}, n = {_a['n_ct']}), and "
    f"r = {_a['spearman_wellsampled_omega_kf']['r']:.2f} "
    f"(P = {_a['spearman_wellsampled_omega_kf']['p']:.2f}) among the "
    f"{_a['n_ct_well_sampled']} well-sampled types (n \u2265 5 pairs); "
    f"per-pair agreement is moderate (r = {_a['spearman_pair_omega_kf']['r']:.2f}, "
    f"P = 5.7 \u00d7 10\u207b\u2074, n = {_a['n_pairs']}). "
    f"Mean \u03c9 correlates negatively with mean k_n "
    f"(r = {_a['spearman_ct_omega_kn']['r']:.2f}, "
    f"P = {_a['spearman_ct_omega_kn']['p']:.2f}). "
    f"Organ-clustered bootstrap 95% CIs (B = 1,000, seed 42; organs resampled with "
    f"replacement, all statistics recomputed per resample; "
    f"notebooks/87_cross_organ_rho_ci_v44.py): the cell-type-level \u03c1(\u03c9, k_f) "
    f"= 0.23 has 95% CI [\u22120.08, +0.38], spanning zero, whereas \u03c1(\u03c9, "
    f"k_n) = \u22120.31 has 95% CI [\u22120.61, \u22120.17], excluding zero "
    f"\u2014 the interval estimates support a denominator-driven ordering. "
    f"CD8+ T cells are the most conserved well-sampled type under both "
    f"\u03c9 and k_f, and the divergent end is directionally consistent "
    f"(endothelial cells and erythrocytes carry the highest mean k_f among "
    f"multi-pair types), but the middle of the ordering does not reproduce: "
    f"NK cells rank most divergent under \u03c9 yet second-most conserved "
    f"under k_f among well-sampled types. The cross-organ ranking is "
    f"therefore a composite of functional divergence and baseline "
    f"differences, not a pure k_f ordering. Full per-cell-type table: "
    f"results/kf_only_ordering.csv."
)
add_para(
    'TCGA clinical-severity gradients (per-tumor mean of intratumoral TT pairs; '
    'values below are from the ex-CC linear-normalization re-analysis at '
    'kn_floor = 0, '
    'notebooks/nc52_tcga_excc_main.py, results/nc52_tcga_excc_severity.csv '
    '(the pre-exclusion run is archived as '
    'results/superseded/tcga_clinical_severity_v44.csv), '
    'which mirrors the published pipeline of notebooks/83_kf_only_ordering.py; '
    'ordering, direction, and significance are identical to the earlier softmax '
    'run, with \u03c9 levels shifted upward by about 5-20). LIHC Edmondson grade: '
    'mean \u03c9 is highest in G1, roughly flat across G2\u2013G3, and lowest in '
    'G4 (78.8, 75.8, 77.6, 72.3 for G1\u2013G4; Jonckheere-Terpstra P < 10\u207b\u00b9\u2075), '
    'but k_f increases with grade (JT P = 8.4 \u00d7 10\u207b\u00b9\u00b2) and '
    'k_n increases in parallel '
    '(JT P < 10\u207b\u00b9\u2075), so the \u03c9 gradient is a denominator effect. BRCA PAM50: '
    'mean \u03c9 decreases across Luminal A (142.0), Luminal B (136.5), '
    'HER2-enriched (121.8), Basal-like (116.7), and Normal-like (101.9) '
    '(Kruskal-Wallis P = 7.0 \u00d7 10\u207b\u2077); the ordering largely reverses '
    'under k_f-only, consistent with the lowest mean k_n in Luminal A, so the '
    '\u03c9 heterogeneity gradient is predominantly a baseline effect. LUAD '
    'mutation strata: the contrast persists under k_f-only (mean \u03c9 KRAS 136.9 '
    '> EGFR 122.2 > wild-type 115.4; Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077 '
    'for \u03c9; k_f P = 0.015; k_n P = 3.4 \u00d7 10\u207b\u2074), with k_n '
    'lowest in EGFR-mutant tumors, so part of the \u03c9 contrast is '
    'denominator-driven. The main text reports only the LUAD driver-mutation '
    'contrast as a primary result; the LIHC Edmondson and BRCA PAM50 '
    'gradients are reported here as denominator-dominated vignettes '
    '(Supplementary Fig. 4b), and the full values '
    'and test details are given in Supplementary Table 18. The k_f-only controls are post-hoc; the P-values '
    'reported here (three severity analyses crossed with three metrics) are '
    'nominal and carry no multiplicity correction. Scripts: '
    'notebooks/83_kf_only_ordering.py (published softmax run) and '
    'notebooks/nc52_tcga_excc_main.py (ex-CC linear re-analysis); outputs: '
    'results/kf_only_ordering.csv, results/kf_only_ordering.json, '
    'results/kf_only_severity.csv, results/kf_only_ordering.txt, '
    'results/nc52_tcga_excc_severity.csv.'
)
add_table([
    ['Stratum', 'Ordering by mean \u03c9', 'Mean \u03c9 per group',
     '\u03c9 omnibus P', 'k_f P', 'k_n P'],
    ['LIHC Edmondson grade', 'G1 > G2 \u2248 G3 > G4',
     '78.8 / 75.8 / 77.6 / 72.3', 'JT < 1e-15',
     'JT 8.4 \u00d7 10\u207b\u00b9\u00b2', 'JT \u2248 0'],
    ['BRCA PAM50', 'LumA > LumB > HER2 > Basal > Normal',
     '142.0 / 136.5 / 121.8 / 116.7 / 101.9', 'KW 7.0 \u00d7 10\u207b\u2077',
     'KW 8.3 \u00d7 10\u207b\u00b9\u00b2', 'KW 3.6 \u00d7 10\u207b\u00b9\u2070'],
    ['LUAD mutation', 'KRAS > EGFR > wild-type', '136.9 / 122.2 / 115.4',
     'KW 7.8 \u00d7 10\u207b\u2077', 'KW 0.015', 'KW 3.4 \u00d7 10\u207b\u2074'],
])
si_caption(
    'Supplementary Table 18. TCGA clinical-severity gradients under the '
    'ex-CC linear-normalization re-analysis (kn_floor = 0; per-tumor mean of '
    'intratumoral TT pairs; results/nc52_tcga_excc_severity.csv). '
    'JT = Jonckheere-Terpstra trend test; '
    'KW = Kruskal-Wallis. All P-values are nominal (no multiplicity '
    'correction); every gradient is denominator-dominated, as shown by the '
    'parallel k_n trends.'
)

add_para('Same-organ decomposition values (migrated from the main text in v51): same-organ pairs have indistinguishable k_f (0.247 vs. 0.250, P = 0.60) but lower k_n (0.0130 vs. 0.0148, P = 3.0 \u00d7 10\u207b\u00b9\u2076), contributing +0.176 on the log scale (factor 1.19).')

add_heading('Supplementary Note 10: Brain Class-Size Confounding Controls and min-cells Threshold Sensitivity', 2)
add_para(
    'Purpose. Three post-hoc controls quantify how class size and the 20-nucleus '
    'minimum affect the brain landscape (script '
    'notebooks/86_brain_downsample_threshold_v44.py; report '
    'results/brain_downsample_threshold_v44_report.md; seed 42). Pipeline '
    'validation: at the reference threshold (min 20 nuclei) the rerun reproduces '
    'the authoritative observed pairs exactly (31,764 pairs; class \u03c9 means '
    'within 4.1 \u00d7 10\u207b\u00b9\u2075; grand mean 38.545; 39 Strong '
    'candidates).'
)
add_para(
    'Confound correlations (class level, 10 classes). k_n correlates '
    'significantly with class size \u2014 Spearman \u03c1 = \u22120.648 '
    '(P = 0.043), Pearson r = \u22120.850 (P = 0.0018) against log10(nuclei per '
    'class); smaller classes have noisier HK pseudobulks and hence larger k_n. '
    'k_n shows no significant correlation with detection depth (mean detected '
    'genes or mean total counts; all P > 0.22). \u03c9 itself is uncorrelated '
    'with every confound tested (all P \u2265 0.091): the sampling-noise factor '
    'is shared by k_f and k_n and cancels in the ratio.'
)
add_para(
    'Equal-n downsampling. Downsampling every class to 4,118 nuclei (the '
    'smallest class; 20 replicates, proportional across regions, without '
    'replacement) abolishes the class-level k_n ordering (full versus equal-n '
    'Spearman \u03c1 = \u22120.055, P = 0.88), confirming that the k_n ordering '
    'is essentially fully explained by class size, and attenuates the \u03c9 '
    'ordering (\u03c1 = 0.370, P = 0.29). The astrocyte-to-Bergmann-glia '
    'gradient survives in direction: 6.10 (full data) \u2192 1.74 \u00b1 0.07 '
    '(mean \u00b1 SD over 20 replicates; 95% percentile interval [1.64, 1.84], '
    'which excludes 1.0). However, that interval propagates only '
    'cell-resampling noise at fixed donors; a donor-level cluster bootstrap '
    '(B = 1,000, seed 42; the four donors resampled with replacement, the full '
    'pipeline recomputed per resample) yields median 1.56 with 95% CI '
    '[0.80, 2.34] (12.6% of replicates below 1; leave-one-donor-out range '
    '[0.93, 1.76]; donor\u00d7region block bootstrap [0.76, 2.13]): with only '
    'four donors\u2014and Bergmann glia present in three\u2014the size-only '
    'equal-n gradient is not separable from donor composition, and it is '
    'therefore reported as a sensitivity analysis rather than a headline '
    '(main text). Roughly 70% of the full-data 6.10-fold magnitude '
    'therefore reflects class-size imbalance and is disclosed as such in the '
    'main text; the direction of the gradient is robust. The span-matched '
    'intra-cerebellar control (main text; 21 matched region pairs) decomposes '
    'the residual 3.68-fold gradient into k_f 1.39 and k_n 0.33 (ratios of '
    'class means; median paired k_f ratio 1.58), so a substantial share of the '
    'residual gradient is carried by the k_n denominator rather than the k_f '
    'numerator (results/nc49_brain_region_matched_summary.csv). The min-cells '
    'threshold sweep is given in Supplementary Table 19.'
)
add_table([
    ['min cells', 'classes', 'pairs', 'Strong', 'lowest-\u03c9 class',
     'Astrocyte/Bergmann gradient'],
    ['10', '10', '37,361', '29', 'Vascular', '6.60'],
    ['20 (reference)', '10', '31,764', '39', 'Bergmann glia', '6.10'],
    ['50', '10', '25,876', '31', 'Vascular', '4.12'],
    ['100', '8', '22,968', '22', 'Vascular', 'n/a (Bergmann glia, choroid plexus dropped)'],
])
si_caption(
    'Supplementary Table 19. Threshold sensitivity of the brain landscape. The '
    '20-nucleus threshold is not arbitrary-sensitive: the high-\u03c9 classes '
    '(astrocytes, oligodendrocytes, OPCs, microglia) change by \u2264 1% across '
    'thresholds, and Strong-tier counts vary modestly (22\u201339). Two caveats: '
    '(i) the lowest-\u03c9 position is a near-tie at t = 20 (Bergmann glia '
    '13.555 versus vascular 13.559) and flips with threshold choice; (ii) '
    't = 100 drops the two smallest classes (Bergmann glia, choroid plexus), so '
    'the threshold must stay \u2264 50 to retain all ten classes; t = 20 '
    'maximizes pair coverage while keeping per-group pseudobulk noise '
    'acceptable.'
)


add_para(
    'Span-matched and equal-n decomposition controls (migrated from the main text '
    'in v50). Restricting astrocytes to the 21 intra-cerebellar region pairs that '
    'define Bergmann glia yields a span-matched gradient of 3.68 (ratio of class '
    'means; paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]; '
    'notebooks/95_brain_region_matched_v49.py), so the gradient persists, at '
    'reduced magnitude, after size and span controls. Unlike the size-only '
    'control, the span-matched gradient is robust at the donor level: the same '
    'donor cluster bootstrap (B = 1,000, seed 42) gives a ratio-of-means '
    'gradient of 3.28 [1.67, 3.97] and a paired-median of 3.99 [2.56, 4.30], '
    'with every leave-one-donor-out replicate above 1 '
    '(notebooks/nc52_brain_donor_bootstrap.py). A combined span- and '
    'size-matched control (equal-n downsampling inside the 21 matched pairs, '
    'target 7,965 nuclei per class, 20 replicates) yields an observed gradient '
    'of 3.66 [3.60, 3.71] across cell-resampling replicates and a donor-level '
    'median of 3.28 [1.92, 3.78] (leave-one-donor-out 2.31\u20133.68, all '
    'above 1): this combined estimate is the main-text headline because it '
    'controls span and size simultaneously and remains significant under donor '
    'resampling (results/nc52_brain_combined_equaln_spanmatch.csv). '
    'Decomposing the equal-n '
    'residual: the astrocyte/Bergmann-glia k_f ratio is 2.09 (95% CI [2.02, 2.18]) '
    'under equal-n\u2014essentially the full-data value (2.03)\u2014whereas the k_n '
    'ratio reverses direction (equal-n 1.29, 95% CI [1.21, 1.41], astrocyte '
    'higher; full-data 0.31, Bergmann glia higher), so the Bergmann-glia k_n '
    'elevation in the full data is largely a class-size artefact '
    '(notebooks/96_brain_downsample_decomp_v49.py). Ordering controls: the '
    'k_f-only gradient is 4.1-fold and the k_n-only gradient 6.7-fold; the '
    'class-mean ordering is stable under an aggregate-first k_n estimator '
    '(Spearman \u03c1 = 0.988, gradient 6.51-fold) but not under a single global '
    'k_n (\u03c1 = 0.09).'
)
add_para(
    'RNA-quality proxies (v52). The atlas metadata carries no PMI or RIN, so '
    'technical variation was proxied by mean detected genes, mean total UMI, '
    'and mitochondrial fraction per group. At the (class, library) level '
    '(4,906 pairs), per-pair regression of log10(k_n/k_f/\u03c9) on the three '
    'proxies shows that mitochondrial fraction explains parts of k_n and k_f '
    '(R\u00b2 0.225\u21920.271 and 0.442\u21920.504 when added) but not of '
    '\u03c9 (0.300\u21920.308), and the T3 (cross-region) \u03c9 coefficient '
    'attenuates from 0.257 to 0.202 (\u221221%) but remains; at the (class, '
    'region) level, adjusting class means for the proxies leaves the endpoint '
    'gradient at 6.33 (depth/UMI) to 6.45 (adding mitochondrial fraction) '
    'versus 6.10 unadjusted. Technical variation capturable by depth, capture, '
    'and composition proxies therefore does not drive the gradient\u2014the '
    'shared technical component cancels in the ratio, as designed; '
    'PMI-related RNA-degradation deformation cannot be excluded (scripts '
    'notebooks/nc52_brain_quality_regression.py, '
    'notebooks/nc52_brain_quality_mito.py).'
)
add_heading('Supplementary Note 11: Region Glossary (Siletti et al. Dissection Nomenclature)', 2)
add_para(
    'All brain-region abbreviations used in the manuscript follow the dissection '
    'nomenclature of the Siletti et al. atlas [12], which is derived from the adult '
    'human brain structural ontology of Ding et al. We extract the ROI-to-dissection '
    'mapping verbatim from the dataset metadata (data/brain/Nonneurons.h5ad, obs '
    'roi and dissection fields; script notebooks/_v38_region_glossary.py, output '
    'results/v38_region_glossary.csv). Candidate-screen endpoints discussed in the '
    'text: A13, caudal intermediate orbital gyrus (orbitofrontal cortex); A14, gyrus '
    'rectus (medial orbitofrontal cortex); A38, temporopolar area; A40, supramarginal '
    'gyrus; A43, parietal operculum (gustatory cortex); A46, middle frontal gyrus; '
    'A5-A7, posterosuperior parietal cortex; AON, anterior olfactory nucleus; TF, temporal area TF of the '
    'occipitotemporal (fusiform) gyrus; Pro, area prostriata; Cla, claustrum; '
    'LG, lateral geniculate nucleus; MG, medial geniculate nuclei; LP, lateral '
    'posterior nucleus; Pul, pulvinar; VA, ventral anterior nucleus; MD, '
    'mediodorsal nucleus; MD-Re, mediodorsal plus reuniens nuclei; CM-Pf, '
    'centromedian and parafascicular nuclei; VPL, ventral posterolateral nucleus '
    '(all thalamic except where noted); STH, subthalamic nucleus (grouped under '
    'thalamus in the dissection ontology but not a thalamic relay nucleus); GPe, '
    'external segment of the globus pallidus; NAC, nucleus accumbens; SI, '
    'substantia innominata; BL, basolateral amygdaloid nucleus; BM, basomedial '
    'amygdaloid nucleus; CMN, corticomedial amygdaloid nuclear group; CA1C-CA3C, '
    'caudal hippocampus (cornu ammonis fields CA1-CA3); CBL, lateral hemisphere of '
    'the cerebellum; CBV, cerebellar vermis; IC, inferior colliculus; DTg, dorsal '
    'tegmental nucleus; PAG-DR, periaqueductal gray and dorsal raphe nucleus; PN, '
    'pontine nucleus; PnAN, afferent nuclei of cranial nerves in pons; PnRF, '
    'pontine reticular formation; MoRF-MoEN, medullary reticular formation and '
    'efferent nuclei of cranial nerves in the medulla oblongata; HTHso-HTHtub, '
    'supraoptic and tuberal hypothalamus. A13 and A14 are cortical '
    '(Brodmann-designated orbitofrontal) areas, not thalamic nuclei; the numbered '
    'A-series labels in the 108-region set are cortical areas, whereas thalamic '
    'nuclei carry their conventional abbreviations (LG, MG, Pul, LP, VPL, VA, MD, '
    'CM-Pf, and related labels). The full 108-region glossary '
    '(abbreviation to full dissection path) ships as '
    'results/v38_region_glossary.csv in the reproducibility package.'
)

add_heading('Supplementary Note 12: Pseudo-Region Negative Control (Block-Shuffle Null Calibration)', 2)
add_para(
    'Purpose. To isolate the calibration of the brain block-shuffle null '
    'from the regional structure it is designed to test, every region\u2019s '
    'libraries were split uniformly at random into two halves (seed = '
    '20260903), producing two "pseudo-regions" per region per cell type; '
    'the identical block-shuffle test (same gene model of HRT Atlas HK '
    'genes + top-5000 non-HK HVG; same filters: minimum 20 nuclei per '
    '(region, cell type), minimum 50 nuclei per region, and at least two '
    'libraries in the group; B = 1,000 permutations; identical one-sided '
    '(B+1) P-value formulae) was re-run on the 127,756 pseudo-pairs '
    'across the ten non-neuronal cell types. Pairs formed between the two '
    'halves of the same real region are "same-origin" (n = 700); all '
    'others are "cross-origin" (n = 127,056), the direct analogue of the '
    'real cross-region pairs.'
)
add_para(
    'Results. Cross-origin pseudo-pairs gave near-nominal marginal tail '
    'rates (5.79% lower tail and 6.87% upper tail at P < 0.05, versus the '
    '5% nominal level), closely matching the real analysis (6.17% lower, '
    '7.90% upper). Same-origin pairs showed a 37.6% lower-tail rate '
    '(263/700), demonstrating within-region library similarity, and a '
    'suppressed upper-tail rate (2.0%). Kolmogorov-Smirnov tests against '
    'U(0,1) reject exact uniformity (cross-origin D = 0.065/0.064 for the '
    'lower/upper tail; P approximately 0 at n = 127,056, which detects '
    'minute deviations), and binomial tail tests quantify the practical '
    'magnitude: an excess of ~0.8-1.9 percentage points over nominal '
    '(binom P = 9.2e-37 and 6.8e-185). The QQ plots are shown in '
    'Supplementary Fig. 10.'
)
add_para(
    'Interpretation. Because the random split destroys regional structure '
    'but preserves within-region library grouping (donor, dissection, and '
    'batch effects tied to each region), the closeness of the pseudo-pair '
    'and real-pair marginal rates demonstrates that the mild '
    'over-dispersion of the per-pair P-values arises from library-level '
    'grouping shared by both designs, not from a null-width mismatch '
    'driven by real regional structure. The 37.6% same-origin rate '
    'confirms that the test retains full power where within-region '
    'similarity exists. The small excess of the real over the pseudo '
    'marginal rates (0.4 and 1.0 percentage points in the lower and upper '
    'tails) is the marginal signature of the true regional biology. '
    'Script: notebooks/77_pseudoregion_control.py; outputs: '
    'results/pseudoregion_control_summary.json, '
    'results/pseudoregion_control_pairs.csv.'
)
add_para(
    'Donor-stratified null transparency. The per-class detail behind the '
    'manuscript statement that 3 of 10 classes survive the '
    'donor-stratified null is tabulated in '
    'results/nc49_donor_stratified_table.csv: for each class it lists the '
    'permutation P-value and BH q-value both with and without donor '
    'stratification, the number of shufflable libraries (libraries '
    'belonging to donors with more than one library; single-library '
    'donors are fixed by design), the per-donor library counts, and the '
    'exact probability that a random donor-stratified shuffle returns '
    'the identity assignment \u2014 the analytic floor on the attainable '
    'one-sided P-value, since the permutation engine retains identity '
    'draws as valid. That floor is negligible for every class '
    '(identity-permutation share at most 4.8 \u00d7 10\u207b\u00b2\u00b3\u00b9), so the nulls are '
    'not degenerate; the three surviving classes are astrocytes '
    '(stratified q = 0.005), oligodendrocyte precursors (0.005), and '
    'committed oligodendrocyte precursors (0.043). One class moves against the '
    'conservative direction: ependymal cells obtain a smaller P under the '
    'donor-stratified null than under the free null (0.021 versus 0.058), '
    'because the within-donor shuffle space differs in composition from the '
    'unrestricted one (the two nulls are not nested); its stratified BH q '
    '(0.052) nonetheless exceeds 0.05, so it is not counted among the '
    'survivors. Script: '
    'notebooks/97_donor_stratified_table_v49.py.'
)

add_para('Within-donor gradient values (migrated from the main text in v51): astrocytes remained the most divergent class (mean \u03c9 = 75.18 across 11,139 within-donor pairs, versus 82.75 pooled) and Bergmann glia the least (16.73), a 4.50-fold gradient.')

add_heading('Supplementary Note 13: Brain set-level enrichment of the block-shuffle signal (post-hoc)', 2)
add_para(
    'Under the block-shuffle null (B = 1,000; m = 31,764 region pairs) no individual '
    'candidate survives Benjamini-Hochberg correction (minimum q = 0.520), and the '
    'manuscript accordingly presents the 39 Strong candidates as hypothesis-generating. '
    'A structural caveat applies to everything below: the tier variable '
    '(residual < 0.3, \u03c9 < 15, lowest-in-pair) and the per-pair permutation '
    'P-values are both monotone functions of the same observed and null \u03c9 '
    'values, so the tier-graded raw-P enrichment is partly guaranteed by '
    'construction; the set-level statistics below quantify the pattern rather than '
    'provide independent evidence for it. Two post-hoc set-level checks ask whether '
    'the raw-P signal is nonetheless structured rather than diffuse. First, raw-P '
    'enrichment is strongly tier-dependent: '
    'raw P < 0.05 occurs in 31 of 39 Strong-tier pairs (79.5%), 417 of 1,171 Moderate '
    '(35.6%), 909 of 5,381 Weak (16.9%), and 603 of 25,173 unclassified pairs (2.4%), '
    'versus 6.2% overall; the Strong-tier excess is significant under a hypergeometric '
    'test (P = 9.6 x 10^-31), the dose-response across tiers is monotone '
    '(Cochran-Armitage trend z = 61.0), and the Strong-tier raw P-values are '
    'stochastically smaller than all other pairs (Mann-Whitney P = 5.3 x 10^-24; '
    'Kolmogorov-Smirnov D = 0.846, P = 4.9 x 10^-32). Second, the 10 mature-oligodendrocyte '
    'Strong candidates concentrate on a thalamo-temporal axis: a thalamic-relay endpoint '
    '(conservative set: MG, LG, LP, LP-VPL, Pul, VPL, VA, MD, MD-Re, CM-Pf, CM) occurs in '
    '6 of 10 candidates versus a 19.4% base rate among all 5,778 mature-oligodendrocyte '
    'pairs, a temporal-fusiform (TF) endpoint in 4 of 10 versus 1.9%, and the combined '
    'axis (thalamic relay, subthalamic nucleus, or TF endpoint) in 9 of 10 versus 22.7%. '
    'Because the candidates share endpoints (MG appears in three pairs, TF in four), the '
    'hypergeometric tests (P = 0.005, 2.1 x 10^-5, and 1.3 x 10^-5 respectively) assume '
    'independent draws and are reported for reference only; a permutation test that '
    'instead resamples candidate sets of size 10 from the same 5,778-pair pool, thereby '
    'preserving the pool\u2019s endpoint co-occurrence structure, gives P = 1.005 x 10^-5 '
    'for the thalamic-relay endpoint and P \u2264 1 x 10^-5 for the TF and combined-axis '
    'endpoints (B = 100,000; null mean hit counts 1.95, 0.19, and 2.27 respectively; '
    'the observed 4 and 9 hits equal or exceed the null maximum). A selection-rule-'
    'matched null, at the same specification as the microglia composition check '
    '(the Strong rule re-evaluated on each block-shuffle permutation, B = 1,000; '
    'notebooks/82_axis_rule_matched_null.py), qualifies these values: the rule-matched '
    'null generates more survivors than observed (mean 43.7 per permutation, 95% '
    '[20, 79], versus 10 observed; this expectation applies to the '
    'mature-oligodendrocyte pool of 5,778 pairs, whereas the 148.3 figure quoted '
    'above refers to the full 31,764-pair screen\u2014the two survivor expectations '
    'are computed on different pools and are not directly comparable), so absolute hit counts are not extreme '
    '(thalamic-relay 6 versus a null mean of 6.58, P = 0.48; TF 4 versus 1.51, '
    'P = 0.13; combined axis 9 versus 8.49, P = 0.38); the concentration is '
    'significant at the level of the per-candidate hit rate (observed 0.60/0.40/0.90 '
    'versus null mean rates 0.149/0.034/0.193; P = 0.005, 0.002, and 0.001; these '
    'per-candidate hit-rate P values are conditional on the selected survivor '
    'set and are not valid post-selection P values). The '
    'uniform-draw permutation treats the candidates as a size-10 uniform subset of '
    'the pool and does not model the selection rule; the rule-matched rate test is '
    'the design-matched comparison, and the claim it supports is axis concentration '
    'of the surviving candidates, not an axis excess of candidates. These are post-hoc '
    'checks in a single dataset, with the tier variable and the axis definition chosen '
    'after inspecting the data, and all P-values are nominal with no multiplicity '
    'adjustment; they support the interpretation that the signal is not random '
    'noise, but they do not substitute for pair-level FDR control. Scripts: '
    'notebooks/72_brain_setlevel_tests.py, notebooks/78_axis_permutation_test.py, '
    'and notebooks/82_axis_rule_matched_null.py; '
    'results: results/brain_setlevel_tests.csv, results/brain_setlevel_tests.txt, '
    'results/axis_permutation_test.txt, and results/axis_rule_matched_null.txt.'
)


add_para(
    'Microglia composition null (migrated from the main text in v50). The '
    'microglial share-level enrichment among Strong candidates (16 of 39; raw '
    'share-level 2.30-fold, hypergeometric P = 6.0 \u00d7 10\u207b\u2074) does '
    'not survive the design-matched null: the Strong rule fires preferentially on '
    'low-\u03c9 classes, so 52.0 of the 148.3 null-rule candidates are microglial '
    '(observed 16, fold 0.31, P = 0.990), and the concentration does not survive '
    'the leave-pair-out panel.'
)
add_heading('Supplementary Note 14: Comparison with Augur Cell-Type Prioritization', 2)
add_para(
    'Augur (Skinnider et al., Nat. Biotechnol. 2021; main-text ref. 37) '
    'prioritizes cell types by the predictability of a condition label from '
    'single-cell expression. We asked whether its class-level prioritization '
    'of the brain atlas (condition = brain region) agrees with CKI\u2019s '
    'regional divergence ordering. Because the reference Python port '
    'augurpy is not distributed for Python 3.13, we used pyaugur 0.1.0, a '
    'pure-Python port of R Augur v1.0.3; the port\u2019s own validation '
    'benchmark (shipped with the pyaugur package) reports Spearman '
    '\u03c1 = 1.0 against the R reference implementation\u2014we note '
    'that this is the port\u2019s self-reported benchmark rather than an '
    'independent validation by us. A stratified '
    'sample of 33,036 nuclei '
    '(\u2264 50 per class \u00d7 region group; groups with \u2265 20 '
    'nuclei, regions with \u2265 50 total nuclei\u2014identical filters to '
    'the CKI pipeline) was scored per class over its eligible regions with '
    'a random forest (100 trees; CP10k + log1p input). Two variants were '
    'run: (i) multiclass macro-OvR AUC (5 subsample seeds \u00d7 3-fold '
    'stratified CV; 15 AUC estimates per class); and (ii) a '
    'confound-controlled binary one-vs-rest variant\u2014for each eligible '
    'region r, r versus the class\u2019s other eligible regions (20 versus '
    '20 cells, 3 repeats \u00d7 3 folds), class score = mean AUC over '
    'regions\u2014because eligible-region counts differ by class '
    '(6\u2013107) and multiclass AUC is not comparable across different '
    'region sets. The two variants were specified before comparing against '
    'CKI, and both are reported below.'
)
add_para(
    'Under the confound-controlled binary one-vs-rest variant (n = 10 '
    'classes): Augur score '
    'versus class-mean \u03c9 Spearman \u03c1 = +0.442 (P = 0.200); versus '
    'k_f \u03c1 = +0.564 (P = 0.090); versus k_n \u03c1 = \u22120.236 '
    '(P = 0.511)\u2014moderate concordance, limited by the n = 10 power. '
    'Astrocytes, the top class by \u03c9 (82.75), rank third of ten by '
    'Augur OvR (AUC 0.703), and choroid plexus is high on both (OvR AUC '
    '0.765, \u03c9 37.76). The shared signal localizes to the HK-anchored '
    'numerator k_f rather than k_n, whose regional divergence is largely '
    'invisible to per-cell whole-transcriptome separability: this pattern is '
    'consistent with, but does not establish, a shared basis in '
    'HK-anchored divergence\u2014the two methods are complementary rather '
    'than redundant. The multiclass variant is reported as a sensitivity '
    'analysis alongside the above because its AUC '
    'correlates with the number of eligible regions per class '
    '(\u03c1 = \u22120.744, P = 0.014); it gives a weaker association '
    '(versus \u03c9 \u03c1 = +0.127, P = 0.726). Scripts '
    'notebooks/91_augur_v45.py and notebooks/91b_augur_ovr_v45.py; '
    'report results/augur_comparison_v45_report.md.'
)

add_heading('Supplementary Note 15: JS Divergence Dimensionality Invariance', 2)
add_para(
    'Because k_n is computed on ~1,130 housekeeping (HK) genes and k_f on 200-2,000 highly '
    'variable genes (HVGs), we verified that JS divergence is not systematically biased by '
    'gene set dimensionality. A simulation of 2,000 random Dirichlet distribution pairs '
    'across dimensions ranging from 50 to 5,000 showed that mean JS divergence is effectively '
    'constant across all dimensions tested (range: 0.155-0.159; ratio = 1.001 between d = 1,130 '
    'and d = 2,000). This confirms that the systematic inflation of k_f relative to k_n '
    '(\u03c9 = 7.70 for equivalent populations) arises from HVG selection bias (selecting genes '
    'with high cross-cell variance) rather than from dimensional mismatch between the HK and '
    'HVG gene sets. We note that this simulation addresses dimensionality per se (random '
    'probability vectors of different lengths) but does not simulate the variance-based '
    'gene selection mechanism that generates the \u03c9 inflation. A more complete validation '
    'would test whether the inflation magnitude scales with the stringency of variance '
    'filtering rather than gene count. The calibrated \u03c9 (omega_cal = \u03c9 / 7.70) '
    'absorbs this bias into the empirical baseline, and the permutation null distribution '
    '- constructed using the same gene sets as the observed data - ensures internal '
    'consistency. (Supplementary Fig. 13.)'
)

doc.add_page_break()

add_heading('Supplementary Note 16: Human-Brain Sanity Check on the Microglia Supercluster', 2)
add_para(
    'This note reports a sanity check on data not used in any main-text '
    'analysis: the Microglia supercluster of the Human Brain Cell Atlas v1.0 '
    '(Siletti et al.; CZ CELLxGENE Discover, collection '
    '283d65eb-dd53-496d-adb7-7570c7caa443; 91,838 nuclei, 58,232 genes), which '
    'carries two cell_type labels\u2014microglial cell (88,494 nuclei) and central '
    'nervous system macrophage (CNS-M\u03c6; 3,344 nuclei)\u2014across 4 donors, '
    '598 samples, and 10 brain regions. Pseudobulks were computed per '
    '(cell_type \u00d7 sample) group (\u2265 20 cells; 563 eligible groups, '
    '89,533 nuclei) with the Tabula Sapiens pipeline order (per-cell '
    'normalize_total(1e4) + log1p, then group means); k_n used the HRT Atlas v1.0 '
    'human HK genes (1,107 matched) and k_f the global seurat HVG 2,000 panel '
    'excluding HK (1,973 genes), with kn_floor = 1 \u00d7 10\u207b\u2074 and '
    'seed 42. The functional contrast comprised 35 sample-matched '
    'microglia-versus-CNS-M\u03c6 pairs (within-sample, controlling donor, '
    'region, and batch); neutral contrasts comprised 20 random half-splits per '
    'cell type of the same (cell_type, sample) group (microglia halves \u2265 '
    '100 cells from 95 groups \u2265 200 cells; CNS-M\u03c6 halves \u2265 50 '
    'cells from 4 groups \u2265 100 cells, within the recommended 50\u2013200 '
    'cell operating window).'
)
add_para(
    'CKI \u03c9 separated the functional contrast from the neutral baseline '
    'completely: \u03c9 = 21.83 \u00b1 7.20 (functional) versus 1.30 \u00b1 '
    '0.36 (neutral), Mann-Whitney P = 5.5 \u00d7 10\u207b\u00b9\u2074, exact '
    'rank AUC = 1.00. The margin is carried by the functional component: k_f '
    '(0.064 \u00b1 0.012 versus 0.0020 \u00b1 0.0016, AUC = 1.00) separates '
    'perfectly, whereas k_n (0.0033 \u00b1 0.0011 versus 0.0014 \u00b1 0.0009) '
    'is only partially elevated (AUC = 0.89)\u2014the decomposition-first '
    'reading argued throughout the manuscript. Standard metrics also separated '
    'the classes (raw JS, cosine, and marker Jaccard AUC = 1.00; Spearman '
    '0.90), as expected for two genuinely distinct cell types; the validation '
    'value lies in \u03c9 tracking the functional contrast far above its own '
    'neutral baseline on an independent dataset. Note that this analysis uses '
    'the global-HVG scheme, not the per-pair top-200 hybrid scheme, so absolute '
    '\u03c9 values sit on a different scale from the 7.70-calibrated hybrid '
    'baseline and are compared internally only. Scripts: '
    'notebooks/nc50_brain_atlas_microglia.py and '
    'notebooks/nc50_fig_microglia.py; outputs: '
    'results/nc50_brain_atlas_microglia.csv and .txt. (Supplementary Fig. 14.)'
)

doc.add_page_break()

# ===== Supplementary Methods (v51: procedural detail migrated verbatim from main-text Methods) =====
add_heading('Supplementary Methods', 2)
add_para('Sections 5.1\u20135.14 collect, verbatim, the full procedural detail compressed out of the main-text Methods in v51. All parameter values, scripts, and output files are preserved; subsection numbering follows the main-text Methods order.')
add_para('5.1 CKI computation', bold=True)
add_para('We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation [42]. Pseudobulk vectors average expression across cells sharing the same cell-type annotation (at least 20 cells per entry (pseudobulk group); at least one donor/mouse contributing at least 10 cells). Housekeeping (HK) genes are loaded from the HRT Atlas v1.0 reference [13] (1,130 human-mouse conserved HK genes; mouse ortholog column for mouse datasets, human column for Tabula Sapiens, TCGA, and the brain atlas). The package also supports data-driven auto-detection (detect_housekeeping_genes(); combined detection-rate and CV criterion, use_reference = False), but all reported analyses use the pre-specified reference.')
add_para('For populations A and B with pseudobulk vectors ε_A and ε_B, each vector is normalized to a probability distribution before Jensen-Shannon (JS) divergence computation by a softmax over log-transformed values, which in count space is exactly the operation of adding a +1 pseudo-count followed by L1 normalization: p_i = (c_i + 1)/Σ_j(c_j + 1), where c denotes the pseudobulk count. The aggregation order differs across datasets and must be distinguished: the brain pipeline applies log1p after averaging counts, softmax(log1p(mean counts)), matching the count-space formula exactly, whereas the mouse (Tabula Muris pilot) and human (Tabula Sapiens) pipelines average per-cell log1p values and normalize afterwards, softmax(mean(log1p)). This difference plausibly contributes, alongside dataset scale and gene-selection effects, to the non-transferability of the dataset-specific calibration constants (Results). The package default from v0.5.x is the brain order, softmax(log1p(mean counts)), which matches the count-space formula exactly; the reverse order is retained only as a legacy option for reproducing the mouse and human pilots. Calibration constants are pipeline-internal and must not be transferred across pipelines: an ω calibrated under one aggregation order is not comparable to an ω computed under the other. A same-data quantification on the mouse pilot’s 15 comparisons (recomputing ω under both orders on identical cells) confirms the warning: the rank ordering is largely preserved (Spearman ρ = 0.78), but absolute values shift (median fold 0.96, up to 9.8-fold per comparison), and the split-control median baseline itself moves from 6.46 to 10.94 (results/nc49_agg_order_sensitivity.csv). Then k_n = JS(norm(ε_A[H]), norm(ε_B[H])), where H is the set of HK gene indices; k_f = JS(norm(ε_A[I]), norm(ε_B[I])), where I is the set of top-2,000 highly variable genes (HVGs; Seurat flavor) excluding HK genes; ω = k_f/k_n, with JS divergence [43] using the base-2 logarithm (range [0, 1]). To guard against division by near-zero k_n, the package exposes an optional denominator floor (kn_floor); the package default (kn_floor = 0) applies only a positivity guard, used by all reported single-cell analyses, so no reported single-cell ω was capped (minimum observed per-pair k_n: 1.1 × 10⁻⁴, mouse; 6.3 × 10⁻⁴, human; 9.2 × 10⁻⁵, brain; only 1 of 31,764 pairs had k_n below 1 × 10⁻⁴, and these values entered ω uncapped). The TCGA bulk analysis is the sole exception and applies kn_floor = 1 × 10⁻⁴, because pseudobulk averaging across millions of cells compresses HK gene variance and drives aggregate k_n toward zero (see Results). One property of this mapping must be made explicit for TCGA: applied to log2(TPM + 1) values, the softmax is mathematically equivalent to p_i ∝ (TPM + 1)^{1/ln 2}—an implicit power transformation of the counts that was not disclosed in earlier versions of this pipeline. We therefore recomputed every TCGA analysis with the linear normalization p_i = (TPM + 1)/Σ_j(TPM_j + 1): all qualitative conclusions were unchanged (the NN > TT ω reversal preserved in 5 of 5 cancer types; kn_floor saturation 0; all severity-gradient directions preserved), with full side-by-side results in the Supplementary Information.')
add_para('A note on package parity: all hybrid-scheme analyses reported in this paper (mouse pilot, Tabula Sapiens, TCGA, brain atlas) select the k_f genes of each pair as the top-200 genes ranked by the absolute pseudobulk difference. The released package’s func_method = "pairwise_de" option instead runs a two-directional Wilcoxon test and yields a different gene set; the reported abs-diff scheme is provided exactly as func_method = "pairwise_absdiff" in package version 0.5.2. All ω values reported here were computed with the abs-diff scheme. The package’s permutation test (bootstrap_test()) reproduces the reported null by default: reselect_identity = True holds the HK set fixed while re-selecting the k_f set at every permutation under the same per-pair rule as the observed value; the legacy fixed-gene-set null remains available as reselect_identity = False and is anti-conservative relative to re-selection (cf. the TCGA fixed-panel caveat).')
add_para('Because k_n is computed on ~1,130 HK genes and k_f on 200–2,000 HVG genes, we verified that JS divergence is not systematically biased by gene set dimensionality. A simulation of 2,000 random Dirichlet distribution pairs across dimensions 50–5,000 showed mean JS divergence effectively constant (0.155–0.159, ratio = 1.001 between d = 1,130 and d = 2,000; Supplementary Fig. 13). The systematic inflation of k_f relative to k_n (ω = 7.70 for equivalent populations) therefore arises from HVG selection bias rather than dimensional mismatch; the calibrated omega (ω_cal = ω / 7.70) absorbs this bias into the empirical baseline, and the permutation null—constructed using the same gene sets—ensures internal consistency.')
add_para('5.2 Permutation testing', bold=True)
add_para('Statistical significance was assessed with permutation tests whose exchangeability unit and gene-selection handling follow the structure of each dataset. For the mouse pilot, Tabula Sapiens, and TCGA per-cancer analyses, labels were permuted between groups (cell labels, or tumor/normal labels across bulk samples; B = 1,000); pseudobulks were recomputed after each permutation and ω recalculated under the same per-pair gene-selection procedure as the observed value, so the null incorporates the gene-selection step. The TCGA per-cancer permutation test additionally holds the identity gene set fixed across permutations (a global HVG panel selected once on the observed grouping); because this fixed-panel null can only deflate the null k_f relative to re-selection, it is anti-conservative, and the corresponding TCGA P-values (all P > 0.9) should be read with this caveat. These P > 0.9 values coexist with cluster-bootstrap CIs that exclude 1 in four of five cancer types, and the two are not contradictory: the permutation null tests exchangeability of tumor and normal labels at the aggregate level under a fixed identity panel—a test with essentially no power here, because aggregate k_n sits at the denominator floor in 3 of 5 cancer types—whereas the bootstrap CIs quantify the sampling uncertainty of the within-cancer NN/TT pairing structure. The aggregate-level permutation test is accordingly uninformative for the reversal claim, which rests on the pair-level cluster bootstrap. For the brain atlas, the authoritative null is the block-shuffle permutation described under “Multiplicative residual model” (10x libraries permuted across regions, per-pair genes re-selected at every permutation; B = 1,000). Empirical P-values use the one-sided upper-tail formula P = (count(ω_null ≥ ω_obs) + 1)/(B + 1), where the +1 pseudocount avoids P = 0; the brain per-pair screen instead uses the one-sided lower-tail formula (anomalously low ω), with the upper tail reported as a complementary summary. The one-sided default is appropriate because our hypothesis is directional: we test whether observed ω exceeds the null expectation, not whether it differs in either direction. Standardized effect size (SES = (ω_obs − mean(ω_null)) / sd(ω_null)) is reported as a non-parametric descriptive statistic complementing the permutation P-value, not a parametric test statistic such as Cohen’s d. Benjamini-Hochberg (BH) FDR correction [44] is applied within each dataset; larger-scale analyses are supplemented with non-parametric tests and descriptive statistics.')
add_para('5.3 Datasets: Tabula Muris, Tabula Sapiens, TCGA', bold=True)
add_para('Tabula Muris FACS SmartSeq2 [8]: 15,057 cells, 22,308 genes, 6 organs (liver, kidney, spleen, lung, heart, bone marrow). Post-quality-control (QC): 38 cell-type entries (each with at least 20 cells and at least one mouse contributing at least 10 cells), yielding C(38, 2) = 703 analyzed pairs. Highly variable genes selected using scanpy [45] with flavor="seurat" [46,47] and n_top_genes=2,000.')
add_para('Tabula Sapiens v1.0 [9]: accessed via CZ CELLxGENE Discover [48]. Post-QC: 108,136 cells (6 h5ad files total), 51,852 genes, 102 cell-type entries across 6 organs. Of these, 99 entries passed the pairwise-analysis filters (at least 20 cells per entry and at least one donor with at least 10 cells; "unknown" annotations excluded), yielding C(99, 2) = 4,851 analyzed pairs. HK genes: HRT Atlas v1.0 reference (1,130 genes; human column).')
add_para('TCGA bulk RNA-seq [49]: five cancer types from NCI Genomic Data Commons, accessed via TCGAbiolinks [50] and cBioPortal [51] APIs. LUAD: 493 tumor + 76 normal; LUSC: 534 tumor + 58 normal; LIHC: 398 tumor + 57 normal; KIRC: 750 tumor + 82 normal; BRCA: 1010 tumor + 109 normal (3,535 samples entering the pair-level analysis under the ex-CC default: of the 3,596 expression-matrix samples, 3 do not appear in the assembled pair table, 26 further samples appear only in tumor–normal pairs and never enter the tumor–tumor or normal–normal comparisons, and the 32 cell-line-derived aliquots identified by the barcode audit below are excluded from all v52 analyses; the pair table itself spans 3,593 unique barcodes, the denominator of the barcode audit in Methods). TPM values from UCSC Xena; within each cancer type, genes with mean expression below 0.5 TPM were removed, and the retained values were log2(TPM + 1) transformed. BRCA PAM50 subtype assignments [52,53] were retrieved from cBioPortal (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute; 522 samples with subtype calls). LIHC Edmondson grade [54]: from cBioPortal, 372 patients with grade calls in the cached pull (289 ex-CC tumors with pair coverage entered the analysis). LUAD mutations: from cBioPortal, 492 samples (61 EGFR, 120 KRAS, 311 WT). Sample provenance followed the TCGA barcode sample-source code (positions 14–15): the 32 cell-line-derived LIHC samples (source code CC, ILSBio liver cancer lines) shipped in the LUSC matrix were assigned to LIHC following a barcode audit and are excluded from all reported analyses (the ex-CC default); the pre-exclusion outputs are archived under results/superseded/.')
add_para('5.4 Dataset: human brain atlas', bold=True)
add_para('Human brain atlas [12]: Siletti et al. (2023) single-nucleus RNA-seq (v3.11) from CZ CELLxGENE Discover 48 (collection ID: 283d65eb-dd53-496d-adb7-7570c7caa443). We used the Nonneurons.h5ad dataset (888,263 nuclei, 59,480 genes, 108 brain regions), classified by supercluster_term annotation into 10 major non-neuronal classes; after filtering (≥ 20 nuclei per (region, cell_type) group, ≥ 50 per region), 886,808 nuclei contributed to the analysis (astrocytes 155,025; oligodendrocytes 490,246; oligodendrocyte precursors 105,723; committed oligodendrocyte precursors 4,118; microglia 91,826; vascular cells 9,586; fibroblasts 8,897; ependymal cells 5,779; choroid plexus 7,643; Bergmann glia 7,965). Pseudobulks were computed as cell-count-weighted means of per-library (10x sample) mean expression vectors per group, then normalized (Scanpy normalize_total, target_sum = 10,000) followed by log1p at the pseudobulk level. CKI ω was computed for all same-cell-type cross-region comparisons (31,764 pairs) with the hybrid scheme; HK genes came from the HRT Atlas v1.0 reference (1,115 genes matched to the Siletti annotation). For computational efficiency, per-pair identity-gene selection was restricted to a pre-filtered pool of the 5,000 non-HK genes with the highest mean expression, within which the top-200 genes with the largest absolute pseudobulk difference were selected per comparison (HK genes excluded).')
add_para('5.5 Method comparison', bold=True)
add_para('We computed five metrics on all 4,851 Tabula Sapiens cell-type pairs: CKI ω (hybrid scheme), raw JS divergence (all genes), Spearman distance (1 - ρ), cosine distance (1 - cos θ), and marker Jaccard distance (1 - Jaccard index of top-200 expressed genes). To avoid donor-pair proliferation, one pseudobulk was computed per cell-type entry from its largest donor (the donor with the most QC-passing cells); the method comparison therefore does not capture inter-donor variability. Inter-metric Spearman correlations were computed using scikit-learn. The four correlations of \u03c9 with the standard metrics carry entry-clustered bootstrap 95% CIs (the 99 pseudobulk entries resampled with replacement, each pair weighted by the product of its endpoint multiplicities; B = 5,000, seed 42; scripts/nc52_stats_resampling.py; results/nc52_stats_tabula_entrycluster.csv): \u03c9 versus raw JS \u22120.40 [\u22120.54, \u22120.23], versus Spearman distance \u22120.46 [\u22120.58, \u22120.34], versus cosine distance \u22120.39 [\u22120.52, \u22120.23], and versus marker Jaccard distance \u22120.36 [\u22120.51, \u22120.19] \u2014 all excluding 0; these cluster-aware intervals replace the independence-assuming P-values of earlier versions (the P < 10\u207b\u00b9\u2074\u2075 caliber is retired). The component decomposition (results/reviewer_decomposition_correlations.csv): k_f correlated positively with the standard metrics (r = +0.43 to +0.72), k_n more strongly (r = +0.69 to +0.81), and conditional on k_n all four \u03c9 correlations turned positive (partial r = +0.11 to +0.54, entry-clustered CIs excluding 0).')
add_para('5.6 Multiplicative residual model (brain)', bold=True)
add_para('For the brain regional analysis, we designed a multiplicative model to detect (cell_type, region_pair) combinations with anomalously low ω: expected_ω = μ_ct × μ_pair / μ_grand, where μ_ct is the cell type’s global mean ω, μ_pair the region pair’s mean ω, and μ_grand the global mean over all 31,764 pairs (38.55); the multiplicative residual = observed / expected, and a residual well below 1 indicates the cell type is far less differentiated between those regions than expected from its global plasticity and the pair’s overall divergence. Three confidence tiers were defined: Strong (residual < 0.3, ω < 15, lowest ω in the region pair), Moderate (residual < 0.5, ω < 25), and Weak (residual < 0.75, ω < 35). Statistical significance was assessed with a block-shuffle permutation null that preserves the joint cell-type × region design: 10x Chromium libraries (sample_id) were treated as blocks and the sample-to-region assignment randomly permuted across libraries (preserving per-region library counts), after which region pseudobulks, all 31,764 pair ω values, and residuals were recomputed; because each library’s cells move together, this null retains library-level structure while breaking the cell–region association and is markedly more conservative than per-cell label shuffling. B = 1,000 permutations were run (minimum resolvable P = 1/1,001 ≈ 9.99 × 10⁻⁴). Per-pair empirical P-values used the one-sided lower-tail formula P = (count(ω_null ≤ ω_obs) + 1)/(B + 1), appropriate because candidates are defined by anomalously low ω; the complementary upper-tail P-value was computed for every pair and both tails are reported. Benjamini-Hochberg FDR correction was applied across all m = 31,764 pairs. No pair reached q < 0.05 (minimum q = 0.520); at this multiplicity q < 0.05 would require B ≈ 6 × 10⁵ permutations or ~635 P-values at the permutation floor (see Statistics and reproducibility), so this outcome reflects permutation resolution rather than evidence against the candidates. The 31 Strong-tier pairs with raw P < 0.05 are reported as hypothesis-generating signals, prioritized for future lineage-tracing validation, with interpretation restricted to the predefined Strong tier rather than the full 31,764 search space. A cell-type-level test additionally asked whether regional structure significantly raises a cell type’s mean ω relative to the same null (one-sided upper-tail P across B = 1,000 permutations). As a negative control for null calibration, the same test was re-run on pseudo-regions obtained by splitting each region’s libraries uniformly at random into two halves (seed fixed; 127,756 pseudo-pairs across the ten classes; Supplementary Note 12).')
add_para('5.7 Brain robustness analyses and donor-stratified null', bold=True)
add_para('Donor confounding and within-donor gradient (brain). The brain atlas contains nuclei from four donors, and 94.5% of region pairs share at least one donor (median top-donor share within a region: 0.61). To test whether the pooled class-level gradient reflects donor identity rather than regional biology, we recomputed cross-region ω using only same-donor (donor, region) pseudobulk pairs: every pair of regions with at least 20 nuclei from the same donor contributed one comparison, and class means were aggregated over all such pairs (astrocytes: 11,139 pairs from 261 donor-region blocks; Bergmann glia: 10 pairs). k_n estimator sensitivity (brain). For all 31,764 pairs we compared four aggregation schemes: per-pair k_n (the reported estimator), an aggregate-first estimator (k_n computed once per cell type from class-level region pseudobulks), a global-k_n variant (a single grand-mean k_n shared by all classes), and k_f-only and k_n-only orderings; agreement was summarized as Spearman rank correlation of the ten class means. Scheme-matched split-half calibration. To test whether the mouse-derived calibration factor transfers, we repeated the random-split-of-the-same-population calibration inside each large single-cell dataset using exactly the gene-selection and pseudobulk pipeline of the corresponding analysis. Brain: for each cell class, the three regions with at least 200 nuclei were split into random halves (B = 50 splits per population; 29 populations), and 95% bootstrap CIs were obtained by resampling the 29 population means (the between-population bootstrap carries the variance relevant to the baseline, so the smaller per-population split count does not inflate the reported CIs relative to the B = 1,000 used in the main inference). Tabula Sapiens: for each (organ, cell type) group from the largest donor with at least 100 cells passing QC (71 populations across six organs), cells were randomly split into halves (B = 50) and ω computed with the same per-pair hybrid pipeline as the main Tabula Sapiens analysis. Lineage enrichment and tier sensitivity (brain). Enrichment of oligodendrocyte-lineage classes among Strong candidates was tested with a hypergeometric test over the 31,764 pairs (12,775 belonging to the lineage), corroborated by permutation (B = 100,000); tier-threshold sensitivity was assessed by recomputing the Strong set and lineage enrichment over a grid of residual caps (0.2–0.4) and ω caps (12–25). Class-size confounding and threshold sensitivity (brain). Class-mean k_n and ω were tested against log10(class nuclei count) and mean detection depth (Spearman and Pearson correlations); an equal-n control downsampled every class to 4,118 nuclei (the smallest class; 20 replicates) and recomputed class rankings and the endpoint gradient; and the full landscape was recomputed at group-size thresholds of 10, 50, and 100 nuclei in addition to the reported 20 (script notebooks/86_brain_downsample_threshold_v44.py). Donor-level uncertainty (v52): for the equal-n, span-matched, and combined span- and size-matched gradients, a donor cluster bootstrap (B = 1,000, seed 42; the four donors resampled with replacement, the full pipeline including cell-level downsampling recomputed per resample; percentile 95% CI) and leave-one-donor-out replicates were computed (script notebooks/nc52_brain_donor_bootstrap.py). RNA-quality proxies (v52): per-pair (class, library)-level and (class, region)-level OLS of log10(k_n/k_f/\u03c9) on mean detected genes, mean total UMI, and mitochondrial fraction (scripts notebooks/nc52_brain_quality_regression.py, notebooks/nc52_brain_quality_mito.py).')
add_para("Donor-stratified null (brain). To ask whether the class-level significance of the pooled block-shuffle null survives when library-to-region assignments cannot cross donor boundaries, we re-ran the permutation test with a donor-stratified shuffle: within each cell class, the sample_id-to-region assignment was permuted only among libraries belonging to the same donor (B = 1,000; identical gene set, pseudobulks, and ω pipeline as the free shuffle). This scheme preserves each donor's library counts and the per-region block-size structure within donors while breaking the library-to-region association; libraries from donors contributing a single library to the class (non-shufflable blocks; e.g., 8 of 606 astrocyte libraries) were held fixed, and permutations returning the identity assignment were retained as valid draws. Class-level significance used the same one-sided upper-tail statistic, P = (count(mean ω_null ≥ mean ω_obs) + 1)/(B + 1). The accompanying free-null P-values come from an independent Monte-Carlo re-run within the same script (same B and pipeline), so small differences from the primary analysis (ependymal cells P = 0.058 here versus 0.075; committed oligodendrocyte precursor cells (OPCs) P = 0.004 versus 0.005) reflect Monte-Carlo variability; the donor-stratified null is strictly the more conservative test.")
add_para('5.8 Ground-truth simulation', bold=True)
add_para('To measure specificity and sensitivity against a known ground truth, we injected perturbations of known magnitude into a real single-cell background: Tabula Muris FACS marrow B cells (1,848 cells). Each replicate resampled two independent groups of 200 cells (gene set: 1,064 matched HK genes plus the 5,000 non-HK genes with the highest global means, mirroring the brain pipeline). A functional signal was injected as a multiplicative shift of 2^δ (δ = 0.125–2) on a fixed module of 200 non-HK genes in group B; neutral perturbations were injected separately as a 2^η shift (η = 0.25–1) on HK genes in group A (neutral drift that should not count as functional divergence) or Poisson noise across all genes in group A (ε = 0.3–1, technical batch noise). Six metrics were computed per replicate with the identical code path as the brain analysis (ω, k_f, k_n, raw JS divergence over the full kept gene set, cosine distance, k_f/k_total). Signal scenarios were repeated with three independent random module draws (seeds 42, 137, 2024); detection thresholds were calibrated per metric as the 95th percentile of 200 baseline replicates, so type-I error and power refer to a common nominal level (the 95th-percentile threshold estimate itself carries Monte Carlo noise of roughly ±1.5 percentage points at 200 baseline replicates, small relative to the between-metric gaps reported). Robustness scenarios (30% dropout, twofold depth difference, fourfold cell-count imbalance) and module-size sensitivity (m = 50, 200, 500) were run at δ = 0.25 and δ = 1. The entire design was repeated in a second background within the same Tabula Muris FACS platform—skin keratinocyte stem cells (1,371 cells)—with identical grids, module seeds, group sizes, and code path (1,750 replicates per background across the full grid). Full results: Supplementary Note 1 and the results/groundtruth_simulation_*.csv files of the companion repository.')
add_para('5.9 Real perturbation demonstration (IFN-β PBMC)', bold=True)
add_para('To test ω on a real perturbation with known ground truth, we re-analyzed the droplet arm of Kang et al. [14] (GEO: GSE96583): peripheral blood mononuclear cells from eight donors, split into control and 6-hour IFN-β-stimulated conditions and captured in two 10x lanes, with donor assignment by genetic demultiplexing as provided by the original authors. All control cells sit in one lane and all stimulated cells in the other, so condition is fully confounded with capture lane (disclosed in Supplementary Note 6): every metric inherits the same confound, and cross-metric contrasts, not absolute detection, are the informative quantity. Singlets with annotated cell types were retained (24,413 cells across six cell types; Ensembl gene identifiers mapped to HGNC symbols). Pseudobulks were computed per (donor, condition) from raw counts, normalized to 10,000 counts, and log1p-transformed; ω, k_f, k_n, and raw JS were evaluated with the per-pair top-200 scheme for two comparison classes: stimulated-versus-control within donor (perturbation class) and donor-versus-donor within condition (donor-drift class). A split-half baseline (six random half-splits per group) anchored the calibrated scale. The significance of the perturbation effect was assessed by permuting condition labels within donor (B = 1,000; genes re-selected at every permutation, one-sided upper tail), and class separability was summarized as the exact rank AUC of each metric within each cell type. Script: notebooks/79_kang_ifnb_demo.py; outputs: results/kang_ifnb_demo_pairs.csv, results/kang_ifnb_demo_summary.json.')
add_para('5.10 Neutral-drift calibration on technical replicates', bold=True)
add_para('To test the neutral-drift specificity property on real data with a ground truth of no functional difference, we constructed technical-replicate pairs and calibrated every metric against a per-pair size-matched (n-matched) cell-shuffle null: the nuclei of the two groups being compared are pooled, randomly permuted, and re-split into disjoint subsets of exactly the observed group sizes (n_a, n_b), so each observed pair is compared against a null distribution that matches its donor, cell type, and group sizes while containing no group structure; B = 200 permutations per pair (Kang) or 100/30/30 for brain tiers T1/T2/T3; at B = 30 the per-pair exceedance indicator resolves to 1/31, so the T2/T3 tier rates carry Monte-Carlo noise of a few percentage points and are read as tier-level, not per-pair, calibrations. Calibration is reported as the ratio observed / null median, and the false-positive element as observed > own null 95th percentile. Kang batch 1 [14]: unstimulated PBMCs from eight donors captured across three 10x lanes (lanes A and B hold four donors each, lane C holds all eight, so every donor appears in exactly two lanes); singlets with annotated cell types and at least 50 cells in both lanes of a donor yielded 30 same-donor, same-condition cross-lane pairs across six cell types, evaluated with the per-pair top-200 scheme on k_n (HRT Atlas HK genes [13]), k_f, ω, raw JS, and cosine distance. Brain drift ladder [12]: from the 888,263 non-neuronal nuclei and 606 10x libraries, 2,732 (cell class, library) groups with at least 20 nuclei defined library-level pairs in three tiers—T1, same (donor, region) different libraries, all 2,161 pairs; T2, same region different donors, 1,089 pairs (random subsample capped at 200 per cell class); T3, same donor different regions, 1,656 pairs (same cap; the cap makes the cell-class composition of T2/T3 availability-dependent, so cross-tier comparisons mix class composition with drift tier—per-class values are reported in Section 3.12 of the Supplementary Information)—evaluated with the brain pipeline (HK genes plus top-5,000 non-HK genes by mean expression; per-pair top-200 selection) for seven metrics: k_n, k_f, ω, raw JS, cosine distance, Spearman distance (1 − ρ), and a pairwise marker Jaccard distance defined as 1 minus the Jaccard index of each group’s top-200 markers (genes ranked by pseudobulk expression minus the cell-weighted background of all other cell classes in the same reduced gene set). Random seeds: 20260918 (Kang), 42 (brain). Scripts: notebooks/nc49_pilot_kang_techrep.py, notebooks/nc49_brain_drift_ladder.py; outputs: results/nc49_pilot_kang_techrep.csv, results/nc49_brain_drift_ladder.csv, and figure notebook nc49_fig_drift_ladder.py (companion repository). Section 3.12 of the Supplementary Information reports the full audit of design, diagnostics, and per-class results.')
add_para('5.11 Fixed gene-panel ablation', bold=True)
add_para('To test whether the brain conclusions depend on the per-pair circular selection of k_f genes (top-200 genes ranked by the absolute difference of the same two pseudobulks on which k_f is computed), we recomputed the entire observed brain landscape—all 31,764 pairs, with identical keep gene set, pseudobulks, and k_n—under three alternative gene-selection schemes: (i) a fixed panel of the 2,000 non-HK genes with the highest global mean expression (selected once, pair-independent); (ii) a leave-pair-out panel, in which the top-200 genes for a pair are selected by the mean absolute pseudobulk difference over all other region pairs of the same cell type (adaptive but not circular for the tested pair); and (iii) all 5,000 non-HK genes of the keep set. The reference implementation reproduced the reported landscape exactly (maximum per-pair |Δω| = 6.4 × 10⁻¹³). We summarized pair-level and class-level rank agreement (Spearman), the circularity inflation as the per-pair ratio of k_f under the reported scheme to k_f under each alternative, and the agreement of the multiplicative-residual ranking. A scheme-matched block-shuffle null (B = 200; minimum resolvable P ≈ 0.005) was rerun under the leave-pair-out scheme to verify that class-level significance does not depend on circular selection. Full results: Supplementary Note 7 and the results/fixed_panel_ablation_* files of the companion repository.')
add_para('5.12 TCGA per-sample statistics and clinical severity analyses', bold=True)
add_para('Per-tumor statistics were derived from the linear-normalization pair table under the ex-CC default (34,828 pairs: the 478 pairs touching the 32 cell-line-derived aliquots dropped from the 35,306-pair table of 2,000 TT pairs per cancer type drawn by seeded subsampling (1,709 for LIHC after the exclusion), complete NN pairs, and 2,000 TN pairs per cancer type; sample-labelled; the seeded subsampling carries a Monte-Carlo error of roughly 0.01–0.02 ratio units on the NN/TT mean ratio, below the between-cancer differences reported), as the mean of ω, k_f, and k_n over all pairs in which a given sample participates (median 4–11 pairs per tumor across cancer types). Group-level NN/TT and k_n ratios are reported as ratios of means with 95% confidence intervals from a sample-level cluster bootstrap (B = 1,000; seed 42): tumor and normal samples were resampled with replacement independently, each pair reweighted by the product of its endpoint resampling weights, and the ratio recomputed per resample; 95% CIs are the 2.5th and 97.5th percentiles of the resampled ratios. LUAD driver groups were assigned by matching cBioPortal mutation labels to the expression matrix by 15-character TCGA barcode (75 EGFR-labelled and 161 KRAS-labelled aliquots, of which 62 EGFR and 122 KRAS matched the matrix; 2 double mutants excluded), yielding 61 EGFR, 120 KRAS, and 311 wild-type tumors with pair coverage. Between-group differences were tested with Kruskal-Wallis followed by Dunn post-hoc tests with Holm correction (manual implementation, tie-corrected rank variances); group mean differences are reported with within-group bootstrap 95% CIs (B = 1,000). For covariate adjustment, stromal and immune admixture was scored per sample with the official ESTIMATE gene sets (141 stromal and 141 immune genes) using the rank-based single-sample enrichment algorithm over all 45,504 expressed genes of the five-cancer merged matrix; the combined stromal-plus-immune score served as the admixture covariate (it is monotonically equivalent to published ESTIMATE purity, leaving regression-based adjustment invariant). Smoking status (ever/never, TCGA tobacco-smoking-history indicator), age, sex, and pack-years for LUAD were obtained from cBioPortal (study luad_tcga, patient-level clinical data; smoking status available for 508, pack-years for 356, and sex for 522 patients) and merged by patient barcode (427 of 492 tumors with known smoking status, 87%). LUAD group contrasts were re-estimated by OLS with the admixture score as a covariate (metric ~ group + z-scored admixture), with ever-smoker status as a covariate, and in a combined model including both (with an age- and sex-adjusted variant); pack-years were not modeled owing to high missingness and are reported descriptively. The adjusted LUAD contrasts were verified by whole-tumor label-permutation tests that re-fit the full OLS adjustment model at every permutation (B = 10,000, seed 42): the KRAS contrasts remain significant (P ≤ 0.001) and the EGFR–WT contrast does not (P ≥ 0.28), matching the parametric conclusions (notebooks/nc52_tcga_luad_adjmodel_permutation.py, results/nc52_tcga_luad_adjmodel_permutation.csv). The LIHC survival analysis used Cox proportional-hazards regression (R survival::coxph) on the ex-CC default cohort (n = 272 tumors with complete covariates, 79 events) with per-tumor ω standardized to unit SD (hazard ratios per SD), AJCC stage entered as a categorical factor, plus Edmondson grade (G1–G4, ordinal), age, and sex, with listwise deletion of missing covariates; k_f-only, k_n-only, and tumor–normal-ω exposures were run as sensitivity models, and proportional hazards were checked with cox.zph (M2 GLOBAL P = 0.023, reported alongside the estimates). Scripts: notebooks/nc52_tcga_excc_main.py (seed 42), notebooks/nc52_lihc_cox_excc.py, notebooks/nc49_tcga_purity.py, notebooks/nc49_tcga_luad_smoking.py; outputs: results/nc52_tcga_pancancer_excc.csv, results/nc52_tcga_excc_severity.csv, results/nc49_tcga_luad_mutation.csv, results/nc52_lihc_cox_excc.csv, results/nc49_tcga_purity.csv, results/nc49_tcga_admix_scores.csv, results/nc49_tcga_luad_smoking.csv.')
add_para('In supplementary within-cancer-type stratification analyses, we computed intratumoral ω for samples within each clinical stratum using the hybrid scheme. BRCA PAM50 subtype calls [52,53] were retrieved directly from the cBioPortal API (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute; 522 samples with subtype calls, cached locally for reproducibility, of which 506 had matched expression data and entered the analysis); no de novo centroid-based classification was performed in this work. LIHC Edmondson grades [54] came from cBioPortal (372 patients with calls in the cached pull; 289 ex-CC tumors with pair coverage entered the analysis), and LUAD mutation status (EGFR, KRAS, WT) from cBioPortal (n = 492 samples). Between-stratum differences were tested with Kruskal-Wallis (PAM50 subtypes, LUAD mutations) and trend with Jonckheere-Terpstra (Edmondson grades). Paired versus unpaired tumor-normal comparisons are reported as descriptive statistics (medians and interquartile ranges, IQRs) without formal P-values, as the paired design does not meet the independence assumption of standard between-group tests. k_f-only and k_n component controls for the ordering claims were computed with the identical pipeline (per-cancer loading, gene filtering, and TT-pair subsampling), stratifying per-tumor mean k_f and k_n exactly as for ω; per-cell-type mean k_f for the cross-organ ranking was computed from the same pseudobulks and per-pair gene selection (notebooks/83_kf_only_ordering.py; results/kf_only_ordering.csv; results/kf_only_severity.csv; Supplementary Note 9).')
add_para('5.13 Computational environment', bold=True)
add_para('Typical runtime for a single cell-type pair is under 5 minutes on a standard laptop; the full brain analysis (31,764 pairs) required approximately 72 core-hours on a Windows x64 workstation with at least 32 GB RAM (the verified environment of the Reproducibility Guide, Section 1.1 of the Supplementary Information). All analyses were performed in Python 3.14.4 with scanpy 1.12.1 [45], scipy ≥ 1.10.0, numpy ≥ 1.23.0, pandas ≥ 1.5.0, matplotlib ≥ 3.6.0, seaborn [55] ≥ 0.12.0, and scikit-learn [56] ≥ 1.2.0; random seeds were fixed at 42 throughout, except scripts 77/78/79, which used seed 20260903, and the small-cluster studentized bootstrap-t analysis (notebooks/89_cluster_boot_v45.py), which used seed 20260905. Permutation results are stable with respect to seed choice: with B = 1,000 permutations the Monte Carlo standard error of the empirical P-value is approximately 0.016 at P = 0.5, so seed variation has negligible impact on statistical conclusions.')
add_para('5.14 Statistical inference details', bold=True)
add_para('We report summary statistics as mean ± s.d. (range) or median [IQR] as noted. Resampling-based inference [57] (permutation tests for P-values; bootstrap for confidence intervals) was performed for all four datasets with B = 1,000: label permutation for the mouse pilot (15 cell-type pairs, 6 calibration control populations with 50 split-half replicates each), human Tabula Sapiens, and TCGA, and the block-shuffle null for the brain atlas (Methods). Empirical P-values are one-sided, P = (count(ω_null ≥ ω_obs) + 1)/(B + 1), with the exchangeability unit following the dataset structure; in each iteration pseudobulks are recomputed from the permuted groups and ω recalculated with identity genes re-selected on the permuted pseudobulks (the TCGA per-cancer permutation test is the sole exception, holding a fixed HVG panel; Methods). Benjamini-Hochberg FDR correction [44] is applied within each dataset, with two levels distinguished. First, group-level tests (one test per cell class, cell type, or cancer type): brain cell-class (m = 10), human per-cell-type (m = 17), mouse pilot (m = 15), TCGA per-cancer (m = 5); the BH thresholds for the most significant test (0.05/m) are 5.0 × 10⁻³, 2.9 × 10⁻³, 3.3 × 10⁻³, and 1.0 × 10⁻²—all above the minimum resolvable permutation P-value of 9.99 × 10⁻⁴ at B = 1,000, so resolution is sufficient for every group-level test. Second, the brain per-pair screen, with BH correction across all m = 31,764 region pairs: the BH threshold for the smallest ordered P-value (0.05/31,764 ≈ 1.6 × 10⁻⁶) lies roughly 600-fold below the smallest resolvable P, so q < 0.05 is unattainable unless ~635 of the 31,764 P-values sit at the permutation floor (a regime the empirical FDR analysis shows is not approached) or B ≈ 6 × 10⁵ permutations are run. The per-pair FDR outcome (minimum q = 0.520) is consequently a statement about permutation resolution rather than evidence against any candidate, and we report it together with the raw permutation P-value distribution (1,960 of 31,764 pairs at raw P < 0.05, slightly more than the ~1,588 expected under a global null).')
add_para('Bootstrap 95% confidence intervals for ω point estimates were computed by resampling observed pair-level ω values with replacement (B = 10,000) and reporting the 2.5th and 97.5th percentiles. Because pairs are nested within regions, we additionally computed region-clustered block bootstrap 95% CIs (B = 2,000; the 108 regions resampled with replacement, all landscape statistics recomputed per resample): gradient 6.10 [5.55, 9.63], grand mean ω 38.55 [36.35, 40.73], Strong-candidate count 39 [12, 74]; these cluster-aware intervals are wider and are the preferred uncertainty summary for landscape-level quantities. Per-class calibrated quantities additionally propagate the uncertainty of the calibration denominator: a joint region-clustered bootstrap (B = 5,000) resamples regions with replacement for the numerator (region-clustered weighted resampling, pair weights equal to the product of the two regions’ library counts) while independently resampling the split-half control populations for the denominator (two-stage: control populations first, random half-splits within each drawn population second), and reports the 2.5th and 97.5th percentiles of the ratio; this joint interval supersedes the earlier i.i.d. interval, which propagated neither source and was anti-conservative (Supplementary Note 3; notebooks/81_perclass_uncertainty.py). The studentized (bootstrap-t) region-clustered intervals pivot the statistic by an influence-function (multiplier) sandwich standard error of the multiplicity-weighted pair mean re-evaluated within each resample, with ratios studentized on the log scale via the delta method (B = 5,000, seed 20260905; Monte Carlo coverage 0.953/0.951 at 6–7 clusters; notebooks/89_cluster_boot_v45.py). The ω distribution was characterized using skewness, excess kurtosis, and normality tests (Shapiro-Wilk for n ≤ 5,000; D’Agostino-Pearson for n > 5,000): all distributions were right-skewed (brain 2.22; mouse pilot 0.99; human 1.17), and normality was rejected for the large datasets (brain P < 2.2 × 10⁻¹⁶; human P = 7.6 × 10⁻⁴²) but not for the mouse pilot (P = 0.071, minimal power at n = 15). The split-half calibration experiment (50 random-split replicates across six control populations of the same tissue, 300 ω values) yielded a mean ω = 7.70 (two-stage bootstrap over the six populations, B = 5,000, seed 42: 95% CI [6.38, 9.82]; the 300-value intervals [7.37, 8.02]/[7.38, 8.02] treat nested splits as independent and are anti-conservative; SD of replicate means = 1.15, pooled SD = 3.63; the legacy n = 6 estimate 6.67 is consistent with it), reflecting systematic inflation of k_f relative to k_n from identity-gene selection; the permutation test accounts for this by constructing the null under the same gene-selection procedure.')
add_para('Statistical conventions. All P-values are from one-sided permutation tests (B = 1,000 for mouse/human/TCGA/brain and for the multiplicative residual model block-shuffle null) unless otherwise specified. Benjamini-Hochberg FDR correction was applied within each dataset. Non-parametric tests (Spearman correlation, Mann-Whitney U, Kruskal-Wallis, Jonckheere-Terpstra) are two-sided and reported with exact P-values, with one exception: the mouse-pilot X-versus-C calibration contrast (Fig. 2c) uses a one-sided Mann-Whitney U test (H1: ω_X > ω_C) matching the directional calibration hypothesis; as an exploratory pilot (n = 15) this contrast is reported for transparency rather than as a pre-registered test. Descriptive statistics are reported as mean ± SD or median [IQR] as indicated. Effect sizes include standardized effect size (SES = (ω_obs − mean(ω_null)) / sd(ω_null)), computed from the permutation null distribution. Bootstrap 95% confidence intervals use stratified resample counts reported per analysis (B = 1,000 for the composition cluster bootstrap, 1,000 for TCGA ratio CIs, 2,000 for region-clustered brain intervals, 5,000 for the joint and studentized small-cluster analyses, and 10,000 for simple resampling of pair-level point estimates), with the Monte Carlo error of each interval reported alongside it in the Supplementary Information. All analyses use JS divergence with base-2 logarithm. Sample sizes (n) are reported for each comparison.')

# ===== Supplementary Tables =====

add_heading('Supplementary Table 1: Parameter Sweep Results', 2)
add_para(
    f'Phase 3.2 parameter sweep on Tabula Muris mouse data (n = 703 cell type pairs, '
    f'6 organs). The pure identity gene configuration (w1 = 1.0, w2 = 0.0) achieved '
    f'optimal cell type discrimination (AUC = {DATA["sweep"]["identity_auc"]:.3f}). Data file: '
    'results/phase32_sweep_results.csv. Visualization: results/phase32_sweep_barplot.png. '
    'Table content: CKI_Supplementary_Tables_NC.xlsx (sheet Table 1).'
)

add_para('')

add_heading('Supplementary Table 2: Cross-Organ Conservation Data', 2)
add_para(
    'Complete dataset of 59 same-cell-type cross-organ pairs in Tabula Sapiens, '
    'including \u03c9, Jensen-Shannon divergence, Spearman distance, Cosine distance, '
    'and Marker Jaccard distance values. Data file: '
    'results/phase35_cross_organ_conservation.csv. '
    'Table content: CKI_Supplementary_Tables_NC.xlsx (sheet Table 2).'
)

add_para('')

add_heading('Supplementary Table 3: Human Brain Non-neuronal Cell Regional CKI Data', 2)
add_para(
    f'Complete results of CKI brain region analysis for non-neuronal cells from the '
    f'Siletti et al. (2023) human brain atlas, comprising {_br["total_pairs"]:,} pairwise cross-region '
    f'comparisons across 10 cell types (n = {_br["n_nuclei"]:,} nuclei, {_br["n_regions"]} regions, '
    f'{_br["n_genes"]:,} genes). Summary statistics for each cell type (\u03c9 mean, '
    f'median, SD, range, k_n and k_f components; all SDs are sample SDs with '
    f'ddof = 1) are provided in Supplementary Table 3. '
    f'Raw data file: results/brain_bs_null_observed_pairs.csv ({_br["total_pairs"]:,} rows, '
    f'block-shuffle re-analysis pipeline). '
    f'Summary file: results/brain_bs_null_ct_test.csv (10-row summary). '
    f'Analysis scripts: notebooks/08d_brain_blockshuffle_null.py and notebooks/08e_brain_blockshuffle_results.py. '
    f'Figure generation: notebooks/_fig6_clean.py (Figure 6). '
    f'Table content (per-cell-type summary): CKI_Supplementary_Tables_NC.xlsx (sheet Table 3).'
)

add_para('')

add_heading('Supplementary Table 4: Inter-regional Region-Associated Candidate Data', 2)

# Build dynamic S4 text
n_candidates = len(_candidates)
pct_candidates = n_candidates / len(_mig) * 100
n_strong = int(_br['n_strong'])
n_moderate = int(_br['n_moderate'])
n_weak = int(_br['n_weak'])
pct_strong = float(_br['pct_strong'])
pct_moderate = float(_br['pct_moderate'])
pct_weak = float(_br['pct_weak'])

# Build top-5 list (Strong tier, lowest multiplicative residuals; strip 'Human ' prefix)
top5_lines = []
for i, (_, r) in enumerate(_strong.iterrows()):
    ra = str(r['region_a']).replace('Human ', '')
    rb = str(r['region_b']).replace('Human ', '')
    top5_lines.append(
        f'{r["cell_type"]} {ra} vs. {rb} '
        f'(\u03c9 = {r["omega"]:.2f}, residual = {r["residual"]:.3f})'
    )

s4_text = (
    f'Results of multiplicative model-based detection of candidate inter-regional cell '
    f'region-association signals (block-shuffle re-analysis pipeline). Of the {_br["total_pairs"]:,} total pairwise cross-region comparisons, '
    f'{n_candidates:,} pairs ({pct_candidates:.1f}%) were classified as threshold-passing candidates '
    f'(residual < 0.75), with full tier definitions: '
    f'{n_strong} Strong signals (residual < {DATA["brain"]["residual_thresholds"]["strong"]}, \u03c9 < 15, and the lowest \u03c9 in the region pair; '
    f'{pct_strong:.2f}%), '
    f'{n_moderate:,} Moderate signals (residual < {DATA["brain"]["residual_thresholds"]["moderate"]}, \u03c9 < 25; '
    f'{pct_moderate:.2f}%), '
    f'and {n_weak:,} Weak signals (residual < {DATA["brain"]["residual_thresholds"]["weak"]}, \u03c9 < 35; '
    f'{pct_weak:.2f}%). '
    f'Under the block-shuffle permutation null (B = {_bs["B"]:,}), {_br.get("n_significant", 31)} of the {n_strong} '
    f'Strong candidates showed raw one-sided P < 0.05, but none survived Benjamini-Hochberg '
    f'correction across all 31,764 pairs (minimum q = {_br["min_q_fdr"]:.3f}); the candidate list is '
    f'therefore hypothesis-generating only. '
    f'Top-5 strongest signals by cell type (ranked by residual): '
    f'1) {top5_lines[0]}, '
    f'2) {top5_lines[1]}, '
    f'3) {top5_lines[2]}, '
    f'4) {top5_lines[3]}, '
    f'5) {top5_lines[4]}. '
    f'Complete candidate dataset: results/brain_bs_null_observed_pairs.csv '
    f'({n_candidates:,} threshold-passing rows of 31,764 total). '
    f'Tables S3 and S4 share the same underlying data file ' 
    f'(results/brain_bs_null_observed_pairs.csv): Supplementary Table 3 reports all 31,764 pairs ' 
    f'with per-cell-type summary statistics, whereas Supplementary Table 4 retains the ' 
    f'{n_candidates:,} threshold-passing rows with their tier, residual, and ' 
    f'\u03c9 annotations. '
    f'Table content: CKI_Supplementary_Tables_NC.xlsx (sheet Table 4). '
    f'Analysis scripts: notebooks/08d_brain_blockshuffle_null.py and notebooks/08e_brain_blockshuffle_results.py.'
)
add_para(s4_text)

add_para('')

add_heading('Supplementary Data 1: Analysis Script Index', 2)
add_para(
    'Complete analysis scripts used in this study are organized in the notebooks/ '
    'directory of the GitHub repository (github.com/zhanglknt/CKI-cell-type-identification). '
    'The package can be installed via: pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git. '
    'Key scripts include: notebooks/04_phase32_sweep.py (parameter sweep and calibration), '
    'notebooks/06_phase34_v2.py (TCGA pan-cancer analysis), '
    'notebooks/05_phase33_v3_fixed.py (Tabula Sapiens cross-organ analysis), '
    'notebooks/08d_brain_blockshuffle_null.py with notebooks/08e_brain_blockshuffle_results.py (brain regional CKI analysis and region-associated candidate detection under the block-shuffle null; supersedes the pre-fix 07c_brain_siletti_v3.py outputs archived in results/superseded/), '
    'notebooks/13_phase35_method_comparison.py (cross-organ method comparison), '
    'and notebooks/30_genome_biology_figures.py with notebooks/_fig1_clean.py to _fig6_clean.py (figure generation).'
)

# ===== Add line numbers (continuous, every line) =====
for sec in doc.sections:
    sect_pr = sec._sectPr
    ln_num = etree.SubElement(sect_pr, qn('w:lnNumType'))
    ln_num.set(qn('w:countBy'), '1')
    ln_num.set(qn('w:start'), '1')
    ln_num.set(qn('w:restart'), 'continuous')

out_path = 'results/CKI_Supplementary_NC.docx'
doc.save(out_path)
print(f'Saved: {out_path}')
print(f'Paragraphs: {len(doc.paragraphs)}')

# ===== v49.5: export the 15 migrated tables as Supplementary Tables 5-19 =====
def write_si_tables_xlsx():
    from openpyxl import Workbook
    from openpyxl.styles import Font
    assert len(_SI_TABLE_ROWS) == 15, f'expected 15 tables, got {len(_SI_TABLE_ROWS)}'
    assert len(_SI_TABLE_CAPS) == 15, f'expected 15 captions, got {len(_SI_TABLE_CAPS)}'
    # Tables 1-4: content previously only referenced as repository CSVs (v52 panel fix)
    _t1 = pd.read_csv('results/phase32_sweep_results.csv')
    _t2 = pd.read_csv('results/phase35_cross_organ_conservation.csv')
    _t3 = pd.read_csv('results/brain_bs_null_ct_test.csv')
    _t4 = _candidates
    _early = [
        (_t1, 'Parameter sweep on Tabula Muris mouse data (n = 703 cell type pairs, 6 organs): AUC per weighting configuration; the pure identity configuration (w1 = 1.0, w2 = 0.0) achieves optimal discrimination. Raw data: results/phase32_sweep_results.csv.'),
        (_t2, 'Complete dataset of 59 same-cell-type cross-organ pairs in Tabula Sapiens: omega, JS divergence, Spearman, cosine, and marker-Jaccard distances. Raw data: results/phase35_cross_organ_conservation.csv.'),
        (_t3, 'Per-cell-type summary of the Siletti et al. (2023) human-brain regional CKI analysis (10 non-neuronal cell types; omega mean, median, SD, range, k_n and k_f components; SDs are sample SDs, ddof = 1). Raw pair-level data: results/brain_bs_null_observed_pairs.csv (31,764 rows).'),
        (_t4, f'Threshold-passing inter-regional region-association candidates (residual < 0.75; {len(_t4):,} of 31,764 pairs) from the multiplicative-model block-shuffle re-analysis, with tier, residual, and omega annotations; {int((_t4["tier"] == "Strong").sum())} Strong signals, none FDR-surviving. Raw data: results/brain_bs_null_observed_pairs.csv.'),
    ]
    wb = Workbook()
    wb.remove(wb.active)
    for _i, (_df, _cap) in enumerate(_early):
        _n = _i + 1
        ws = wb.create_sheet(f'Table {_n}')
        ws['A1'] = f'Supplementary Table {_n}: {_cap}'
        ws['A1'].font = Font(bold=True)
        ws.append([])
        ws.append(list(_df.columns))
        for _c in ws[3]:
            _c.font = Font(bold=True)
        for _row in _df.itertuples(index=False):
            ws.append([None if pd.isna(_v) else _v for _v in _row])
        ws.column_dimensions['A'].width = 28
    for _i, (_rows, _cap) in enumerate(zip(_SI_TABLE_ROWS, _SI_TABLE_CAPS)):
        _n = _i + 5
        ws = wb.create_sheet(f'Table {_n}')
        ws['A1'] = f'Supplementary Table {_n}: {_cap}'
        ws['A1'].font = Font(bold=True)
        ws.append([])
        for _ri, _row in enumerate(_rows):
            ws.append(list(_row))
            if _ri == 0:
                for _c in ws[3]:
                    _c.font = Font(bold=True)
        ws.column_dimensions['A'].width = 28
    out_x = 'results/CKI_Supplementary_Tables_NC.xlsx'
    wb.save(out_x)
    print(f'Saved: {out_x} (sheets: {len(wb.sheetnames)})')

write_si_tables_xlsx()
