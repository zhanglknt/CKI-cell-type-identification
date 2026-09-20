# R3 recalc part 2: T2/T3 tiers, LUAD internal consistency, Cox table
import pandas as pd
import numpy as np
from scipy import stats

base = 'C:/Users/KnightZ/Desktop/细胞受选择/results/'
d = pd.read_csv(base + 'nc49_brain_drift_ladder.csv')
mets = ['omega', 'k_f', 'k_n', 'raw_js', 'cosine', 'spearman', 'marker_jaccard']
for tier in ['T2_cross_donor', 'T3_cross_roi']:
    sub = d[d['tier'] == tier]
    print(f'-- {tier} n={len(sub)}')
    for m in mets:
        print(f'   {m:15s} FPR {sub[f"exceed_{m}"].mean()*100:5.1f}%   cal median {sub[f"cal_{m}"].median():.3f}')
print('paper T2: omega FPR 90.9% cal 1.76; raw_js 98.4% cal 3.32; k_f 98.7% cal 3.22')
print('paper T3: omega cal 1.80; raw_js 2.98; marker_jaccard 1.41; k_f ? ')
# T1/T2/T3 omega cal gradient
for tier in ['T1_techrep', 'T2_cross_donor', 'T3_cross_roi']:
    sub = d[d['tier'] == tier]
    print(tier, 'omega cal med', round(sub['cal_omega'].median(), 3), 'rawjs cal med', round(sub['cal_raw_js'].median(), 3))
print('paper gradient: omega 1.04->1.76->1.80; raw_js 1.07->3.32->2.98')

# B per tier check
print()
print('B values per tier:', d.groupby('tier')['B'].agg(['min', 'max']).to_string())
print('paper: B=100/30/30 for T1/T2/T3')

print()
print('=== LUAD internal consistency ===')
m = pd.read_csv(base + 'nc49_tcga_luad_mutation.csv')
m['p'] = pd.to_numeric(m['p'], errors='coerce')
m['stat'] = pd.to_numeric(m['stat'], errors='coerce')
m['n_total'] = pd.to_numeric(m['n_total'], errors='coerce')
# KW p from H
for met in ['LUAD_omega', 'LUAD_kf', 'LUAD_kn']:
    row = m[(m.metric == met) & (m.test == 'Kruskal-Wallis')].iloc[0]
    p_re = stats.chi2.sf(row['stat'], 2)
    print(f'{met}: H={row["stat"]} p_csv={row["p"]:.4g} p_recalc_chi2(df=2)={p_re:.4g} match={np.isclose(p_re, row["p"], rtol=1e-3)}')
# Dunn z -> raw two-sided p, then Holm across 3 contrasts
for met in ['LUAD_omega', 'LUAD_kf', 'LUAD_kn']:
    sub = m[(m.metric == met) & (m.test == 'Dunn (Holm)')].copy()
    sub['p_raw'] = 2 * stats.norm.sf(sub['stat'].abs())
    sub = sub.sort_values('p_raw')
    holm = []
    for i, (_, r) in enumerate(sub.iterrows()):
        holm.append(min(1.0, r['p_raw'] * (3 - i)))
    sub['p_holm_recalc'] = holm
    print(f'-- {met} Dunn:')
    for _, r in sub.iterrows():
        print(f'   {r["comparison"]:14s} z={r["stat"]:7.3f} p_raw={r["p_raw"]:.4g} p_holm_csv={r["p"]:.4g} p_holm_recalc={r["p_holm_recalc"]:.4g} match={np.isclose(r["p"], r["p_holm_recalc"], rtol=1e-2)}')
# group n
ns = m[(m.test == 'descriptive')]
print('group ns:', dict(zip(ns['comparison'], ns['n_total'])), 'sum =', ns['n_total'].sum(), '(paper: 492; 61+120+311)')

print()
print('=== LIHC Cox (nc49_pilot_lihc_cox.csv) ===')
c = pd.read_csv(base + 'nc49_pilot_lihc_cox.csv')
print(c['model'].unique())
z = c[c['covariate'] == 'z']
print(z[['model', 'n', 'events', 'HR', 'HR_lower', 'HR_upper', 'p']].to_string(index=False))
print('paper: M1 omega HR 1.06 [0.85,1.32] P=0.59; all six exposures P>=0.30')
# verify HR = exp(coef), CI = exp(coef +- 1.96 se), p from z
c['HR_re'] = np.exp(c['coef'])
c['lo_re'] = np.exp(c['coef'] - 1.959964 * c['se'])
c['hi_re'] = np.exp(c['coef'] + 1.959964 * c['se'])
c['p_re'] = 2 * stats.norm.sf(np.abs(c['coef'] / c['se']))
bad = c[~np.isclose(c['HR'], c['HR_re'], atol=2e-3) | ~np.isclose(c['p'], c['p_re'], rtol=1e-2)]
print('rows failing internal HR/p consistency:', len(bad))
print(c[['model', 'covariate', 'HR', 'HR_re', 'p', 'p_re']].head(30).to_string(index=False))
