import pandas as pd, numpy as np

co = pd.read_csv('results/phase35_cross_organ_conservation.csv')
out = []
g = co.groupby('ct')['omega']
stats = pd.DataFrame({'mean': g.mean(), 'sd': g.std(ddof=1), 'n': g.size()})
stats['cv'] = stats['sd'] / stats['mean']
stats = stats.sort_values('mean')
out.append(stats.to_string())
out.append('')
out.append('total pairs: %d, n CTs: %d' % (len(co), co['ct'].nunique()))
out.append('same-CT cross-organ mean omega (all 59): %.2f' % co['omega'].mean())
with open('results/figures_final/_tmp_probe1.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done')
