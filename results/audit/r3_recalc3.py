# R3 recalc part 3: recompute pan-cancer table from the 35,306-pair table
import pandas as pd
import numpy as np
from scipy import stats

base = 'C:/Users/KnightZ/Desktop/细胞受选择/results/'
df = pd.read_csv(base + 'phase34_v2_all_pairs.csv')
print('pairs:', len(df), '(paper 35,306)')
print(df.groupby(['cancer', 'pair_type']).size().unstack())
tab = pd.read_csv(base + 'nc49_tcga_pancancer.csv')

print()
print(f'{"cancer":10s} {"TTmean_re":>10s} {"TTmean_csv":>10s} {"NNmean_re":>10s} {"NNmean_csv":>10s} {"ratio_re":>8s} {"ratio_csv":>8s} {"MWUp_re":>10s} {"MWUp_csv":>10s}')
for _, r in tab.iterrows():
    c = r['cancer']
    tt = df[(df.cancer == c) & (df.pair_type == 'TT')]['omega']
    nn = df[(df.cancer == c) & (df.pair_type == 'NN')]['omega']
    ratio = nn.mean() / tt.mean()
    u = stats.mannwhitneyu(nn, tt, alternative='greater')
    print(f'{c:10s} {tt.mean():10.2f} {r["omega_TT_mean"]:10.2f} {nn.mean():10.2f} {r["omega_NN_mean"]:10.2f} {ratio:8.3f} {r["NN_TT_ratio"]:8.3f} {u.pvalue:10.3g} {r["p_MWU_NN_gt_TT"]:10.3g}')

print()
print('kn medians TT/NN ratio:')
for _, r in tab.iterrows():
    c = r['cancer']
    tt = df[(df.cancer == c) & (df.pair_type == 'TT')]['kn']
    nn = df[(df.cancer == c) & (df.pair_type == 'NN')]['kn']
    print(f'{c:10s} recalc {tt.median()/nn.median():.3f} csv {r["kn_TT_NN_median_ratio"]:.3f} | mean ratio recalc {tt.mean()/nn.mean():.3f} csv {r["kn_TT_NN_mean_ratio"]:.3f} | kf means TT {tt.mean():.4f}/{r["kf_TT_mean"]:.4f}? ')
# kf means
for _, r in tab.iterrows():
    c = r['cancer']
    kf_tt = df[(df.cancer == c) & (df.pair_type == 'TT')]['kf'].mean()
    kf_nn = df[(df.cancer == c) & (df.pair_type == 'NN')]['kf'].mean()
    print(f'{c:10s} kf_TT recalc {kf_tt:.4f} csv {r["kf_TT_mean"]:.4f} | kf_NN recalc {kf_nn:.4f} csv {r["kf_NN_mean"]:.4f}')

print()
# composite structure check: rho(log omega, log kf/kn) on all pairs
lo = np.log(df['omega']); lf = np.log(df['kf']); ln = np.log(df['kn'])
print('rho(log w, log kf) =', round(stats.spearmanr(lo, lf).statistic, 3), '(paper +0.04)')
print('rho(log w, log kn) =', round(stats.spearmanr(lo, ln).statistic, 3), '(paper -0.82)')
vf, vn = lf.var(), ln.var()
print('log-var kn share =', round(vn / (vf + vn), 3), '(paper ~72% kn)')
# kn floor trigger: pairs with kn < 1e-4
print('pairs with kn < 1e-4:', (df['kn'] < 1e-4).sum(), '(paper: 1 of 35,306, KIRC NN pair, kn=8.41e-5)')
mn = df.loc[df['kn'].idxmin()]
print('min kn row:', mn['cancer'], mn['pair_type'], mn['kn'])

# TT pair counts per cancer (paper: 2000 TT subsampled per cancer; complete NN; 2000 TN)
print()
print(df['pair_type'].value_counts())
