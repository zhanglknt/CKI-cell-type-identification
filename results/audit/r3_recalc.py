# R3 blind-review recomputation script (read-only w.r.t. manuscript data)
# Verifies v49 numbers against authoritative CSVs.
import pandas as pd
import numpy as np
from scipy import stats

base = 'C:/Users/KnightZ/Desktop/细胞受选择/results/'
out = []

def rec(s):
    out.append(s)
    print(s)

def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    m = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (c - m) / d, (c + m) / d

# ---------- A. Kang technical replicates ----------
rec('=' * 70)
rec('A. Kang batch1 techrep (nc49_pilot_kang_techrep.csv)')
k = pd.read_csv(base + 'nc49_pilot_kang_techrep.csv')
n = len(k)
rec(f'n pairs = {n} (paper: 30)')
for m in ['omega', 'k_f', 'k_n', 'raw_js', 'cosine']:
    e = int(k[f'exceed_{m}'].sum())
    lo, hi = wilson(e, n)
    med = k[f'cal_{m}'].median()
    q1, q3 = k[f'cal_{m}'].quantile([0.25, 0.75])
    rec(f'  {m:8s} FPR {e}/{n} = {e/n:.3f}  Wilson [{lo:.3f},{hi:.3f}]  cal median {med:.3f} IQR [{q1:.3f},{q3:.3f}]')
rec('paper: omega 0/30 [0.000,0.114] med 0.963 IQR[0.918,0.998]; k_f 0/30; raw_js 11/30 [0.219,0.545]; cosine 7/30 [0.118,0.409]; k_n 1/30')

# ---------- B. Brain drift ladder ----------
rec('=' * 70)
rec('B. Brain drift ladder (nc49_brain_drift_ladder.csv)')
d = pd.read_csv(base + 'nc49_brain_drift_ladder.csv')
rec(f'total rows = {len(d)} (paper: 2161+1089+1656 = 4906)')
rec(str(d['tier'].value_counts().to_dict()))
mets = ['omega', 'k_f', 'k_n', 'raw_js', 'cosine', 'spearman', 'marker_jaccard']
for tier, tname in [('T1_techrep', 'T1'), ('T2_donor', 'T2'), ('T3_region', 'T3')]:
    sub = d[d['tier'] == tier]
    if len(sub) == 0:
        rec(f'  tier {tier} NOT FOUND; tiers present: {sorted(d.tier.unique())}')
        continue
    rec(f'-- {tier} n={len(sub)}')
    for m in mets:
        fpr = sub[f'exceed_{m}'].mean()
        calmed = sub[f'cal_{m}'].median()
        rec(f'   {m:15s} FPR {fpr*100:5.1f}%   cal median {calmed:.3f}')

# per-class T1 comparison omega vs raw_js/cosine/spearman
t1 = d[d['tier'] == d['tier'].unique()[0]] if 'T1_techrep' not in set(d['tier']) else d[d['tier'] == 'T1_techrep']
rec('-- T1 per-class FPR: omega vs raw_js / cosine / spearman')
cnt = {'raw_js': 0, 'cosine': 0, 'spearman': 0}
tot = 0
for ct, g in t1.groupby('cell_type'):
    tot += 1
    fo = g['exceed_omega'].mean()
    for m in cnt:
        if fo < g[f'exceed_{m}'].mean():
            cnt[m] += 1
    rec(f'   {ct:35s} n={len(g):4d}  omega {fo*100:5.1f}%  raw_js {g["exceed_raw_js"].mean()*100:5.1f}%  cosine {g["exceed_cosine"].mean()*100:5.1f}%  spearman {g["exceed_spearman"].mean()*100:5.1f}%  ratio rjs/om {(g["exceed_raw_js"].mean()/fo if fo>0 else np.nan):.2f}')
rec(f'omega below raw_js in {cnt["raw_js"]}/{tot} classes; cosine {cnt["cosine"]}/{tot}; spearman {cnt["spearman"]}/{tot} (paper 10/10, 9/10, 8/10; ratios 1.2-2.3)')

# size-stratified T1 FPR (group size = min(n_cells_a, n_cells_b)? try both)
nmin = t1[['n_cells_a', 'n_cells_b']].min(axis=1)
nmax = t1[['n_cells_a', 'n_cells_b']].max(axis=1)
for lab, ns in [('min', nmin), ('max', nmax)]:
    b1 = t1[ns <= 30]; b2 = t1[(ns > 30) & (ns <= 500)]; b3 = t1[ns > 500]
    rec(f'-- T1 size strata by {lab}(n_a,n_b): <=30 n={len(b1)} omega {b1["exceed_omega"].mean()*100:.1f}% rawjs {b1["exceed_raw_js"].mean()*100:.1f}% | 31-500 n={len(b2)} omega {b2["exceed_omega"].mean()*100:.1f}% rawjs {b2["exceed_raw_js"].mean()*100:.1f}% | >500 n={len(b3)} omega {b3["exceed_omega"].mean()*100:.1f}% rawjs {b3["exceed_raw_js"].mean()*100:.1f}%')
rec('paper: <=30 n=199 omega 14.1% rawjs 28.6%; >500 n=269 omega 48.0% rawjs 72.5%')

# choroid plexus / Bergmann glia calibration
for ct in ['Choroid plexus', 'Bergmann glia']:
    g = t1[t1['cell_type'] == ct]
    rec(f'-- T1 {ct}: n={len(g)} median cal_omega {g["cal_omega"].median():.3f} (paper CP n=9 2.31; BG n=27 1.16)')

# T1 k_n calibration
rec(f'-- T1 k_n cal median {t1["cal_k_n"].median():.3f} (paper 1.05)')
# Wilson CI for omega T1 FPR
e = int(t1['exceed_omega'].sum()); lo, hi = wilson(e, len(t1))
rec(f'-- T1 omega FPR {e}/{len(t1)} = {e/len(t1)*100:.1f}% Wilson [{lo*100:.1f},{hi*100:.1f}] (paper 28.6% [26.8,30.6])')

# ---------- C. TCGA pancancer ----------
rec('=' * 70)
rec('C. TCGA pancancer (nc49_tcga_pancancer.csv)')
p = pd.read_csv(base + 'nc49_tcga_pancancer.csv')
p['ratio_recalc'] = p['omega_NN_mean'] / p['omega_TT_mean']
p['kn_ratio_recalc'] = p['kn_TT_median'] / p['kn_NN_median']
rec(p[['cancer', 'NN_TT_ratio', 'ratio_recalc', 'NN_TT_ratio_CI95_lower', 'NN_TT_ratio_CI95_upper', 'kn_TT_NN_median_ratio', 'kn_ratio_recalc', 'kn_TT_NN_mean_ratio', 'p_MWU_NN_gt_TT']].to_string(index=False))
rec('paper: LUAD 2.46 [2.13,2.86], KIRC 1.90 [1.65,2.17], LUSC 1.82 [1.46,2.25], BRCA 1.57 [1.35,1.83], LIHC 1.13 [0.97,1.34]; kn mean ratio e.g. KIRC 3.21 [2.51,4.28], LIHC 1.41 [1.08,1.98]; kn median ratio 2.1-3.6')

# ---------- D. LUAD mutation ----------
rec('=' * 70)
rec('D. LUAD mutation (nc49_tcga_luad_mutation.csv)')
m = pd.read_csv(base + 'nc49_tcga_luad_mutation.csv')
rec(m.to_string(index=False))
