# R3 recalc part 4: full independent recomputation of v49 TCGA tables
# from the linear-normalization 35,306-pair table + archived cBioPortal mutation labels
import pandas as pd
import numpy as np
import json
from scipy import stats

base = 'C:/Users/KnightZ/Desktop/细胞受选择/'
df = pd.read_csv(base + 'results/tcga_linear_norm_v44_all_pairs.csv')
print('pairs:', len(df), '(paper 35,306)')

# ---- 1. Pan-cancer table recompute (omega = omega_floor, kn_floor=1e-4 reported version) ----
tab = pd.read_csv(base + 'results/nc49_tcga_pancancer.csv')
print()
print(f'{"cancer":10s} {"TTmean_re":>9s} {"csv":>8s} {"NNmean_re":>9s} {"csv":>8s} {"ratio_re":>8s} {"csv":>7s} {"MWUp_re":>10s} {"csv":>10s}')
for _, r in tab.iterrows():
    c = r['cancer']
    tt = df[(df.cancer == c) & (df.pair_type == 'TT')]['omega_floor']
    nn = df[(df.cancer == c) & (df.pair_type == 'NN')]['omega_floor']
    ratio = nn.mean() / tt.mean()
    u = stats.mannwhitneyu(nn, tt, alternative='greater')
    print(f'{c:10s} {tt.mean():9.2f} {r["omega_TT_mean"]:8.2f} {nn.mean():9.2f} {r["omega_NN_mean"]:8.2f} {ratio:8.3f} {r["NN_TT_ratio"]:7.3f} {u.pvalue:10.3g} {r["p_MWU_NN_gt_TT"]:10.3g}')
print()
print('kn ratios / kf means from linear table:')
for _, r in tab.iterrows():
    c = r['cancer']
    ttk = df[(df.cancer == c) & (df.pair_type == 'TT')]
    nnk = df[(df.cancer == c) & (df.pair_type == 'NN')]
    print(f'{c:10s} kn med ratio {ttk.kn.median()/nnk.kn.median():.3f} (csv {r["kn_TT_NN_median_ratio"]:.3f}) | kn mean ratio {ttk.kn.mean()/nnk.kn.mean():.3f} (csv {r["kn_TT_NN_mean_ratio"]:.3f}) | kf TT {ttk.kf.mean():.4f} (csv {r["kf_TT_mean"]:.4f}) kf NN {nnk.kf.mean():.4f} (csv {r["kf_NN_mean"]:.4f})')
# floor trigger
n_floor = (df['kn'] < 1e-4).sum()
print('pairs with raw kn < 1e-4:', n_floor, '(paper: 1, KIRC NN, kn=8.41e-5)')
print(df.loc[df['kn'].idxmin()][['cancer', 'pair_type', 'kn']].to_dict())
print('omega_floor == omega_raw except floor pair:', (df['omega_floor'] != df['omega_raw']).sum())
# composite structure on linear table
lo = np.log(df['omega_floor']); lf = np.log(df['kf']); ln = np.log(df['kn'])
print('rho(log w, log kf) =', round(stats.spearmanr(lo, lf).statistic, 3), '(paper +0.04)')
print('rho(log w, log kn) =', round(stats.spearmanr(lo, ln).statistic, 3), '(paper -0.82)')
print('log-var kn share =', round(ln.var() / (lf.var() + ln.var()), 3), '(paper ~0.72)')

# ---- 2. LUAD per-sample mutation analysis: full recompute ----
print()
print('=== LUAD per-sample recompute ===')
tt = df[(df.cancer == 'TCGA-LUAD') & (df.pair_type == 'TT')]
print('LUAD TT pairs:', len(tt))
# per-tumor mean over pairs the sample participates in
samples = pd.unique(pd.concat([tt['sample_a'], tt['sample_b']]))
print('unique tumors in TT pairs:', len(samples))
per = {}
for col in ['omega_floor', 'kf', 'kn']:
    a = tt.groupby('sample_a')[col].agg(['sum', 'count'])
    b = tt.groupby('sample_b')[col].agg(['sum', 'count'])
    tot = a.add(b, fill_value=0)
    per[col] = tot['sum'] / tot['count']
pers = pd.DataFrame(per)
pers.index.name = 'sample'
npair = tt.groupby('sample_a').size().add(tt.groupby('sample_b').size(), fill_value=0)
pers['n_pairs'] = npair
print('pairs per tumor: median', pers['n_pairs'].median(), 'range', pers['n_pairs'].min(), '-', pers['n_pairs'].max(), '(paper: median 4-11 across cancer types)')

mut = json.load(open(base + 'data/tcga/luad_egfr_kras_mutations.json', encoding='utf-8'))
egfr = {s[:15] for s in mut['egfr_samples']}
kras = {s[:15] for s in mut['kras_samples']}
dbl = {s[:15] for s in mut['double_mutants']}
print('egfr aliquots:', len(mut['egfr_samples']), 'unique 15-char:', len(egfr),
      '| kras:', len(mut['kras_samples']), len(kras), '| doubles:', len(mut['double_mutants']), dbl)

def grp(s):
    if s in dbl: return 'double'
    if s in egfr: return 'EGFR'
    if s in kras: return 'KRAS'
    return 'WT'
pers['group'] = [grp(s) for s in pers.index]
print(pers['group'].value_counts().to_dict(), '(paper: EGFR 61, KRAS 120, WT 311; 2 double excluded)')
an = pers[pers['group'] != 'double']
print('analysis n =', len(an))

# group means
gm = an.groupby('group')[['omega_floor', 'kf', 'kn']].mean()
print(gm)
print('paper: omega WT 115.4 EGFR 122.2 KRAS 136.9; kf WT 0.2814 EGFR 0.2732 KRAS 0.2919; kn WT 0.0032 EGFR 0.0028 KRAS 0.0027')

# KW
groups = [g['omega_floor'].values for _, g in an.groupby('group')]
H, pkw = stats.kruskal(*groups)
print(f'KW omega: H={H:.2f} p={pkw:.3g} (csv H=28.12 p=7.83e-7)')
for met in ['kf', 'kn']:
    H, pkw = stats.kruskal(*[g[met].values for _, g in an.groupby('group')])
    print(f'KW {met}: H={H:.3f} p={pkw:.3g} (csv kf H=8.386 p=0.0151; kn H=16.002 p=3.35e-4)')

# Dunn with tie correction + Holm
def dunn_test(an, col):
    data = an[[col, 'group']].dropna()
    ranks = stats.rankdata(data[col])
    data = data.assign(rank=ranks)
    N = len(data)
    # tie correction
    _, counts = np.unique(ranks, return_counts=True)
    tie_sum = (counts**3 - counts).sum()
    sigma2 = (N * (N + 1) / 12 - tie_sum / (12 * (N - 1)))
    gs = {g: data[data.group == g] for g in ['WT', 'EGFR', 'KRAS']}
    res = []
    for a, b in [('WT', 'EGFR'), ('WT', 'KRAS'), ('EGFR', 'KRAS')]:
        Ra = gs[a]['rank'].mean(); Rb = gs[b]['rank'].mean()
        na = len(gs[a]); nb = len(gs[b])
        z = (Ra - Rb) / np.sqrt(sigma2 * (1 / na + 1 / nb))
        p = 2 * stats.norm.sf(abs(z))
        res.append((f'{a} vs {b}', z, p))
    # Holm
    order = np.argsort([r[2] for r in res])
    holm = [None] * 3
    running = 0
    for rank_i, idx in enumerate(order):
        adj = min(1.0, res[idx][2] * (3 - rank_i))
        running = max(running, adj)
        holm[idx] = running
    return [(res[i][0], res[i][1], res[i][2], holm[i]) for i in range(3)]

for col, lab in [('omega_floor', 'omega'), ('kf', 'kf'), ('kn', 'kn')]:
    print(f'-- Dunn {lab} (comparison, z, p_raw, p_holm):')
    for cmp, z, pr, ph in dunn_test(an, col):
        print(f'   {cmp:14s} z={z:7.3f} p_raw={pr:.4g} p_holm={ph:.4g}')
print('csv omega: WT-KRAS z=-5.295 pH=3.57e-7; EGFR-KRAS z=-2.860 pH=0.00847; WT-EGFR z=-0.852 pH=0.394')
print('csv kf: EGFR-KRAS z=-2.817 pH=0.01455; WT-KRAS z=-1.973 pH=0.0969; WT-EGFR z=1.649 pH=0.0992')
print('csv kn: WT-KRAS z=3.809 pH=4.18e-4; WT-EGFR z=2.007 pH=0.0895; EGFR-KRAS z=0.816 pH=0.415')
