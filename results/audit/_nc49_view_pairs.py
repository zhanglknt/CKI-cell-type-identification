# -*- coding: utf-8 -*-
import pandas as pd
df = pd.read_csv('C:/Users/KnightZ/Desktop/细胞受选择/results/nc49_pilot_kang_techrep.csv')
cols = ['cell_type','donor','lane_a','lane_b','n_cells_a','n_cells_b',
        'omega','cal_omega','cal_raw_js','cal_cosine']
out = []
out.append(df[cols].to_string(index=False))
out.append('')
out.append('exceed raw_js: %d/%d' % (df['exceed_raw_js'].sum(), len(df)))
out.append('exceed cosine: %d/%d' % (df['exceed_cosine'].sum(), len(df)))
out.append('exceed omega:  %d/%d' % (df['exceed_omega'].sum(), len(df)))
open('C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_pilot_pairs_view.txt',
     'w', encoding='utf-8').write('\n'.join(out))
