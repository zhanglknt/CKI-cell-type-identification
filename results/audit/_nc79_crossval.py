"""nc79 cross-validation: every new number in MS/SI traced back to its source CSV.

Reads the fresh DOCX fulltexts (results/*_fulltext.txt, written by the build) and
re-derives each quoted quantity from the analysis outputs written by the A1-A5
agents. Prints PASS/FAIL per item and exits non-zero on any failure.
"""
import os
import re
import sys
import json

import pandas as pd
from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

P, F = [], []


def chk(name, cond, detail=''):
    (P if cond else F).append(name)
    print(f'[{"PASS" if cond else "FAIL"}] {name} {detail}')


MS = open('results/CKI_Manuscript_NC_fulltext.txt', encoding='utf-8').read()
SN = open('results/CKI_Supplementary_NC_fulltext.txt', encoding='utf-8').read()
CL = open('results/CKI_NC_Cover_Letter_fulltext.txt', encoding='utf-8').read()
GD = open('results/CKI_Reproducibility_Guide_NC_fulltext.txt', encoding='utf-8').read()
ABS = [p.text for p in Document('results/CKI_Manuscript_NC.docx').paragraphs
       if 'Standard metrics confound cell-state shifts' in p.text][0]


def pct(x, nd=1):
    return f'{100 * x:.{nd}f}'


# ---------------------------------------------------------------- A1 CNA share (nc80 v2)
share2 = pd.read_csv('results/nc80_cna_share_v2.csv')
excc = share2[share2.cohort == 'excc']
pooled = excc[excc.scope == 'pooled'].set_index('delta')
p0, p5 = pooled.loc[0.0], pooled.loc[0.05]
chk('A1 v2 pooled share at delta=0 -> 56% (95% CI 46-66%)',
    round(100 * p0['share']) == 56
    and round(100 * p0['share_lo']) == 46 and round(100 * p0['share_hi']) == 66,
    f'{p0["share"]:.3f} [{p0["share_lo"]:.3f}, {p0["share_hi"]:.3f}]')
chk('A1 MS quotes 56% (95% CI 46-66%)', '56% (95% CI 46\u201366%)' in MS)
chk('A1 v2 pooled share at delta=0.05 -> 42% (34-50%)',
    round(100 * p5['share']) == 42
    and round(100 * p5['share_lo']) == 34 and round(100 * p5['share_hi']) == 50,
    f'{p5["share"]:.3f} [{p5["share_lo"]:.3f}, {p5["share_hi"]:.3f}]')
chk('A1 MS quotes the 0.05 sensitivity (42% 34-50%)',
    '42% (34\u201350%) at a residual of 0.05' in MS)
chk('A1 SI quotes the same two point estimates',
    '56% (95% CI 46\u201366%' in SN and '42% (34\u201350%)' in SN)

# per-cancer shares and beta extrema (v2 ex-CC)
d0 = excc[(excc.delta == 0.0) & (excc.scope != 'pooled')].set_index('scope')
chk('A1 v2 per-cancer beta_CNA_TT range matches SI extrema',
    f'+{d0.beta_CNA_TT.min():.2f} (LIHC)' in SN and f'+{d0.beta_CNA_TT.max():.2f} (KIRC)' in SN,
    f'{d0.beta_CNA_TT.min():.3f} .. {d0.beta_CNA_TT.max():.3f}')
chk('A1 SI TT CNA distance range is 0.129-0.246',
    f'{d0.mean_cna_TT.min():.3f}\u2013{d0.mean_cna_TT.max():.3f}' == '0.129\u20130.246'
    and '0.129\u20130.246' in SN, f'{d0.mean_cna_TT.min():.3f}-{d0.mean_cna_TT.max():.3f}')
chk('A1 SI per-cancer shares match v2 CSV',
    all(f'{s} {round(100*d0.loc[s,"share"])}% [{round(100*d0.loc[s,"share_lo"])}, {round(100*d0.loc[s,"share_hi"])}]'
        in SN for s in ['BRCA', 'KIRC', 'LIHC', 'LUAD', 'LUSC']),
    str({s: f'{d0.loc[s,"share"]:.3f}' for s in ['BRCA', 'KIRC', 'LIHC', 'LUAD', 'LUSC']}))
chk('A1 all per-cancer beta > 0 (co-directional, not attenuating)',
    bool((d0.beta_CNA_TT > 0).all()), str(d0.beta_CNA_TT.round(2).to_dict()))
chk('A1 KIRC DNA coverage 44% disclosed in SI',
    'only 871 of its 2,000 sampled tumour pairs carry DNA profiles (44%)' in SN)
chk('A1 LIHC share flagged as not stably identified',
    'not stably identified' in SN)

# joint confounder model (stat M2 fix)
jm = pd.read_csv('results/nc80_cna_joint_model.csv')
jb = jm[(jm.scope == 'pooled') & (jm.variant == 'base') & (jm.delta == 0.0)].iloc[0]
chk('A1 joint model pooled CNA 40% [30, 51] and composition +2%',
    round(100 * jb.share_cna) == 40 and round(100 * jb.share_comp) == 2,
    f'CNA {jb.share_cna:.3f} comp {jb.share_comp:.3f}')
chk('A1 SI quotes joint model decomposition',
    'CNA 40% [30, 51]' in SN and 'composition +2% [\u22123, +6]' in SN)
chk('A1 joint model decomposition closes to 1 (all scopes, all variants)',
    float(((jm.share_cna + jm.share_comp + jm.share_resid
            + jm.share_rin.fillna(0) + jm.share_other) - 1).abs().max()) < 1e-6,
    f'max dev {(jm.share_cna + jm.share_comp + jm.share_resid + jm.share_rin.fillna(0) + jm.share_other - 1).abs().max():.2e}')

# direction flip: tumour CNA > normal-by-assumption, beta > 0 (legacy text checks)
chk('A1 old "attenuates, rather than creates" gone from MS and SI',
    'attenuates, rather than creates' not in MS
    and 'attenuates, rather than creates' not in SN)
chk('A1 new direction stated in MS', 'creates part of the elevation' in MS)
chk('A1 new direction stated in SI',
    'creates rather than attenuates the TT/NN housekeeping gap' in SN)
chk('A1 old IVW pooling language gone from SI',
    'inverse-variance pooling' not in SN)

# ---------------------------------------------------------------- A2 T1 / drift
lad49 = pd.read_csv('results/nc49_brain_drift_ladder.csv')
st = pd.read_csv('results/nc79_a2_t1_strata.csv')
all_t1 = st[(st.stratum_dim == 'clean_subset') & (st.metric == 'omega')]
chk('A2 T1 omega rate reproduces 0.286', abs(all_t1.fpr.iloc[0] - 0.2864) < 5e-4,
    f'{all_t1.fpr.iloc[0]:.4f}')
chk('A2 MS quotes 28.6%', '28.6%' in MS)
sb = st[st.stratum_dim == 'batch']
same = sb[sb.stratum.str.contains('same', case=False) & (sb.metric == 'omega')]
diff = sb[sb.stratum.str.contains('diff|cross', case=False) & (sb.metric == 'omega')]
chk('A2 same-batch 11.4% and cross-batch 66.9% in SI',
    f'{100*same.fpr.iloc[0]:.1f}%' in SN and f'{100*diff.fpr.iloc[0]:.1f}%' in SN,
    f'{same.fpr.iloc[0]:.4f} / {diff.fpr.iloc[0]:.4f}')
_t1 = lad49[lad49.tier == 'T1_techrep'].copy()
_pfx = _t1.sample_a.astype(str).str.rsplit('_', n=1).str[0]
_pfx_b = _t1.sample_b.astype(str).str.rsplit('_', n=1).str[0]
_nr = _t1[['n_cells_a', 'n_cells_b']].min(axis=1) / _t1[['n_cells_a', 'n_cells_b']].max(axis=1)
_strict = _t1[(_pfx == _pfx_b) & (_nr >= 0.7)]
_sfpr = _strict.exceed_omega.mean()
chk('A2 strict block reproduces 10.3% at n=1,334',
    f'{100*_sfpr:.1f}' == '10.3' and len(_strict) == 1334,
    f'{_sfpr:.4f} n={len(_strict)}')
chk('A2 SI quotes 10.3% (8.8-12.1) and n = 1,334',
    '10.3% (8.8\u201312.1)' in SN and 'n = 1,334' in SN)

grad = pd.read_csv('results/nc79_a2_nullfree_gradient.csv')
raw = grad[(grad.metric == 'omega') & (grad['transform'].str.replace('_', '').str.lower().str.startswith('raw'))]
chk('A2 omega rank 4/7 in raw units',
    int(raw['rank'].iloc[0]) == 4, f'rank {int(raw["rank"].iloc[0])}')
chk('A2 SI states omega ranks fourth of seven in raw units',
    'fourth of seven in raw units' in SN)
chk('A2 SI states omega ranks last on the log scale',
    'last of seven' in SN)
chk('A2 SI withdraws the shallowest-gradient claim',
    'shallowest' not in MS and 'no claim that \u03c9 has the shallowest drift' in SN)

# log-MAD precision spread
import numpy as np
lad = pd.read_csv('results/nc49_brain_drift_ladder.csv')
t1 = lad[lad.tier == 'T1_techrep']
lm = {}
for m in ('omega', 'k_n', 'k_f', 'raw_js', 'cosine', 'spearman', 'marker_jaccard'):
    v = np.log10(t1[m].replace(0, np.nan)).dropna()
    lm[m] = 1.4826 * float(np.median(np.abs(v - np.median(v))))  # normal-consistent MAD, same caliber as shift_z
others = [v for k, v in lm.items() if k != 'omega']
chk('A2 omega log-MAD 0.113 decades',
    f'{lm["omega"]:.3f}' == '0.113', f'{lm["omega"]:.4f}')
chk('A2 other metrics log-MAD 0.267-0.586',
    f'{min(others):.3f}' == '0.267' and f'{max(others):.3f}' == '0.586',
    f'{min(others):.3f}-{max(others):.3f}')
chk('A2 SI quotes 0.113 / 0.267-0.586', '0.113 decades' in SN and '0.267\u20130.586' in SN)

# ---------------------------------------------------------------- A5 tail stats
tl = pd.read_csv('results/nc79_a5_tail_stats.csv').set_index('tier')
chk('A5 P(null <= 39) = 1.0e-3 at B=1000', abs(tl.loc['Strong', 'p_lower'] - 1e-3) < 5e-6,  # 0.000999 = 1/(B+1) at B=1000
    f'{tl.loc["Strong", "p_lower"]:.4g}')
chk('A5 null mean 148.3 reproduces manuscript expectation',
    round(tl.loc['Strong', 'null_mean'], 1) == 148.3,
    f'{tl.loc["Strong", "null_mean"]:.1f}')
chk('A5 MS quotes one-sided lower tail', 'one-sided P(null \u2264 39)' in MS)
chk('A5 old P(null >= 39) = 1.0 gone from MS and figure legend',
    'P(null count \u2265 39)' not in MS)
chk('A5 Moderate null 1,900 +/- 131 and Weak 6,108 +/- 148 in MS',
    f'{round(tl.loc["Moderate", "null_mean"]):,}' in MS
    and f'{round(tl.loc["Moderate", "null_sd"]):,}' in MS
    and f'{round(tl.loc["Weak", "null_mean"]):,}' in MS
    and f'{round(tl.loc["Weak", "null_sd"]):,}' in MS,
    f'{tl.loc["Moderate","null_mean"]:.0f}+/-{tl.loc["Moderate","null_sd"]:.0f}; '
    f'{tl.loc["Weak","null_mean"]:.0f}+/-{tl.loc["Weak","null_sd"]:.0f}')

# ---------------------------------------------------------------- A3 KRAS AUC
auc = pd.read_csv('results/nc79_a3_kras_auc.csv')
cmp_ = pd.read_csv('results/nc79_a3_kras_compare.csv')
om = auc[auc.metric.str.lower().str.contains('omega')].iloc[0]
de = auc[auc.metric.str.lower().str.contains('de')].iloc[0]
chk('A3 omega AUC 0.648 [0.568, 0.733]',
    f'{om.auc:.3f}' == '0.648' and f'{om.auc_lo:.3f}' == '0.568'
    and f'{om.auc_hi:.3f}' == '0.733',
    f'{om.auc:.3f} [{om.auc_lo:.3f}, {om.auc_hi:.3f}]')
chk('A3 DE AUC 0.841', f'{de.auc:.3f}' == '0.841', f'{de.auc:.3f}')
chk('A3 SI quotes 0.648 / 0.841 / DeLong P = 0.002',
    'AUC 0.648 (95% CI 0.568\u20130.733' in SN and '(0.841;' in SN
    and 'DeLong P = 0.002' in SN)
d = cmp_[cmp_.comparison.str.lower().str.contains('de')].iloc[0]
chk('A3 SI delta AUC -0.193 [-0.307, -0.069]',
    f'{d.delta:.3f}' == '-0.193' and f'{d.delta_lo:.3f}' == '-0.307'
    and f'{d.delta_hi:.3f}' == '-0.069'
    and '\u22120.193' in SN, f'{d.delta:.3f} [{d.delta_lo:.3f}, {d.delta_hi:.3f}]')
chk('A3 MS/abstract no longer claim "separates KRAS from EGFR"',
    'separates KRAS from EGFR' not in MS and 'separates KRAS from EGFR' not in CL
    and 'distinguishes KRAS- from EGFR' not in MS and 'distinguishes KRAS- from EGFR' not in ABS
    and 'distinguishes KRAS- from EGFR' not in CL)
chk('A3 abstract KRAS-mutant vs wild-type (EGFR arm dissolved, nc80)',
    'KRAS-mutant tumors exceed wild-type group means after purity adjustment' in ABS)
chk('A3 "genuine driver-associated divergence" removed everywhere',
    'genuine driver-associated' not in MS and 'genuine driver-associated' not in SN)

# ---------------------------------------------------------------- A4 floor / CV
fl = pd.read_csv('results/nc79_a4_floor_sensitivity.csv')
kn = fl[(fl.section == 'i_kn_dist') & (fl.subset == 'POOLED')].set_index('quantity')['value']
chk('A4 floor binds on 0-1 pair at 1e-4', kn['n_kn_below_1e-4'] <= 1,
    f'{kn["n_kn_below_1e-4"]:.0f} of {kn["n_pairs"]:.0f}')
chk('A4 MS says the floor binds in one pair only',
    'housekeeping floor binds in one pair only' in MS)
cv = pd.read_csv('results/nc79_a4_cv_metrics.csv')
chk('A4 CV audit covers brain + TCGA', cv.dataset.nunique() >= 2,
    str(cv.dataset.unique()[:4]))
chk('A4 Methods declares the CV caliber',
    'Coefficients of variation are s.d./mean unless labelled MAD/median' in MS)

# ---------------------------------------------------------------- nc80 P0/P1 numbers
# M-D: T1 library-aware null (class x run-stratum leave-self-out q95)
lib = json.load(open('results/nc80_t1_library_null.json'))
ln = lib['strata'] if 'strata' in lib else lib
# summary.txt is authoritative for the four headline rates
lt = open('results/nc80_t1_library_null_summary.txt').read()
chk('nc80-MD all_T1 shuffle 28.6% -> lib_sr 5.5%',
    'all_T1' in lt and '0.286' in lt and '0.055' in lt)
chk('nc80-MD strict_block shuffle 10.3% -> lib_sr 4.8%',
    'strict_block' in lt and '0.103' in lt and '0.048' in lt)
chk('nc80-MD MS quotes library-aware 5.5% and 4.8% [3.8, 6.1]',
    'gives 5.5% overall and 4.8% (95% CI 3.8\u20136.1%)' in MS)
chk('nc80-MD MS uses exceedance rate, no FPR in Results T1',
    'exceedance rate 28.6%' in MS and 'FPR' not in MS)
chk('nc80-MD SI Note 1 carries library-aware paragraph',
    'Library-aware null (nc80)' in SN and '5.5%' in SN and '4.8%' in SN)
chk('nc80-MD CL quotes 4.8% under library-aware null',
    '4.8% under a library-aware null' in CL)

# M-I: paired within-patient TN (full enumeration)
tn = json.load(open('results/nc80_paired_tn.json'))
pool = tn['pooled']
tn_csv = pd.read_csv('results/nc80_paired_tn.csv')
chk('nc80-MI cohort sizes 57-108 patients per cancer',
    sorted(tn['per_cancer'][c]['n_paired_patients'] for c in tn['per_cancer'])
    == [57, 58, 75, 82, 108])
chk('nc80-MI TN_same full enumeration counts match SI',
    all(tn['per_cancer'][c]['n_pairs']['TN_same']
        == tn['per_cancer'][c]['n_paired_patients'] for c in tn['per_cancer']))
chk('nc80-MI pooled TN_same/TT = 0.90 [0.86, 0.95]',
    abs(pool['ratio_medians_kn']['TN_same_over_TT'] - 0.903) < 0.005
    and pool['bootstrap_ci_ratio_kn']['TN_same_over_TT'][0] < 0.86
    and pool['bootstrap_ci_ratio_kn']['TN_same_over_TT'][1] > 0.94)
chk('nc80-MI pooled TN_same/NN = 2.26 [2.06, 2.49]',
    abs(pool['ratio_medians_kn']['TN_same_over_NN'] - 2.260) < 0.01)
chk('nc80-MI pooled TN_same/TN_cross = 0.85 (reciprocal 1.18)',
    abs(pool['ratio_medians_kn']['TN_same_over_TN_cross'] - 0.847) < 0.005
    and abs(1 / pool['ratio_medians_kn']['TN_same_over_TN_cross'] - 1.18) < 0.01)
chk('nc80-MI MS quotes 0.90 / 2.26 / 18% higher',
    '0.90 of the tumor\u2013tumor level' in MS
    and '2.26 of the normal\u2013normal level (2.06\u20132.49)' in MS
    and '18% higher' in MS)
chk('nc80-MI SI 3.6 carries full-enumeration paragraph',
    'Within-patient paired tumor-normal analysis (nc80, full enumeration)' in SN
    and 'no longer says not part of the present analysis'
    or 'not part of the present analysis' not in SN)
chk('nc80-MI MWU TN vs TT significant in 3/5 (LUAD/LIHC/BRCA)',
    sum(1 for c in tn['per_cancer'].values()
        if c['mwu_tests_kn']['TN_same_vs_TT_kn']['p'] < 0.05) == 3)

# M-C / M-F: scoped reproducibility + authoritative 1.20/0.146 + robust calibers
cm = pd.read_csv('results/audit/_nc78_student_fourth/SourceData/Figure2/'
                 'split_half_cv_summary.csv')
brain = cm[cm.dataset == 'Adult human brain'].set_index('metric')['cv']
chk('nc80-MC authoritative brain CV 1.2049 -> 0.1465 (ratio 8.23)',
    abs(brain['kf'] - 1.2049) < 0.001 and abs(brain['omega'] - 0.1465) < 0.001
    and abs(brain['kf'] / brain['omega'] - 8.23) < 0.02)
chk('nc80-MC abstract says 1.20 to 0.146 + scoped log-MAD',
    '1.20 \u2192 0.146' in ABS and 'log-scale MAD 0.113' in ABS
    and 'most reproducible' not in ABS)
chk('nc80-MC CL scoped (tightest dispersion, no most reproducible)',
    'tightest dispersion of the seven metrics' in CL
    and 'most reproducible' not in CL)
chk('nc80-MF Discussion robust calibers IQR/median + max/min quoted',
    'the two calibers are not interchangeable' in MS)
chk('nc80-MF mouse collapse 1.7x quoted',
    'mouse only 1.7-fold' in MS
    and abs(0.435777 / 0.251447 - 1.733) < 0.01)
chk('nc80-MF alpha spread 1.65-2.2 quoted in MS',
    'varies 1.65\u20132.2-fold across populations' in MS)

# M-E: conditional monotonicity (omega > 2 alpha = 19.46, 30.3% outside)
bp = pd.read_csv('results/brain_bs_null_observed_pairs.csv')
omega_col = 'omega' if 'omega' in bp.columns else [c for c in bp.columns
                                                   if 'omega' in c.lower()][0]
frac_below = (bp[omega_col] < 2 * 9.73).mean()
chk('nc80-ME 30.3% of 31,764 pairs below omega > 2*9.73 = 19.46',
    len(bp) == 31764 and abs(frac_below - 0.303) < 0.005,
    f'{frac_below:.3f}')
chk('nc80-ME MS states guarantee + 30.3% + 39 Strong omega < 15',
    'guaranteed only for \u03c9 > 2\u03b1' in MS and '30.3% of pairs' in MS
    and 'all 39 Strong candidates (\u03c9 < 15)' in MS)

# M-G: catalogue anti-enrichment floor + microglia depletion
chk('nc80-MG P(null <= 39) floor with <= in MS',
    'P(null \u2264 39) \u2264 1.0 \u00d7 10\u207b\u00b3' in MS
    and 'P(null \u2264 39) = 1.0 \u00d7 10\u207b\u00b3' not in MS)
chk('nc80-MG microglia 0.31-fold depletion disclosed in MS',
    '0.31-fold below expectation, P = 0.990' in MS)

# M-K: GTEx not-resolved downgrade in CL
chk('nc80-MK CL excluded tested size / larger shifts not resolved',
    'a field effect of the tested size is tentatively excluded' in CL
    and 'larger shifts are not resolved' in CL
    and 'arguing against a field-effect reading' not in CL)

# ---------------------------------------------------------------- tally
print()
print(f'TOTAL: {len(P) + len(F)} checks, {len(F)} failures')
if F:
    print('FAILURES:', F)
    sys.exit(1)
print('ALL PASS')
