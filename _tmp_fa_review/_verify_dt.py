# -*- coding: utf-8 -*-
"""Verify the regenerated NC manuscript docx after d-tcga integration."""
from docx import Document

doc = Document(r'C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Manuscript_NC.docx')
paras = [p.text for p in doc.paragraphs]

lines = []
def log(s=''):
    lines.append(s)
    print(s)

# 1. TCGA section presence
tc_idx = [i for i, t in enumerate(paras) if 'pan-cancer map of tissue-level' in t]
log('TCGA results heading at paragraphs: %s' % tc_idx)

# 2. Figure legends order 1-7
fig_leg = [i for i, t in enumerate(paras) if t.startswith('Figure ') and '.' in t[:10]]
log('Figure legends in order:')
for i in fig_leg:
    log('  [%d] %s' % (i, paras[i][:80]))

# 3. Main figure references
import re
log('\nMain Fig references by number (excluding Supplementary):')
for n in range(1, 8):
    hits = [i for i, t in enumerate(paras)
            if re.search(r'Fig\. %d\b' % n, t) and not t.startswith('Figure %d' % n)]
    log('  Fig. %d: paragraphs %s' % (n, hits))

# 4. Key TCGA numbers presence
keys = ['2.46', '1.13', '3.21', '2.1\u20133.6', '136.9', '115.4', '7.8 \u00d7 10\u207b\u2077',
        'Dunn\u2013Holm', '3.6 \u00d7 10\u207b\u2077', '0.015', '4.2 \u00d7 10\u207b\u2074',
        '\u22124.1% to +2.6%', 'hazard ratio per SD 1.06', '0.85\u20131.32',
        'tissue-level functional divergence', 'nc49_tcga_pancancer.csv',
        'nc49_pilot_lihc_cox.csv', 'cluster bootstrap, B = 1,000']
log('\nKey-number presence:')
for k in keys:
    log('  %r: %d occurrence(s)' % (k, sum(t.count(k) for t in paras)))

# 5. Old exploratory phrasing must be gone
gone = ['apparent tumor homogeneity', 'TCGA; exploratory', 'median NN/TT = 1.23',
        'median NN/TT = 2.32', 'paired/unpaired ratio = 0.89']
log('\nRemoved phrasing (expect 0):')
for g in gone:
    log('  %r: %d' % (g, sum(t.count(g) for t in paras)))

# 6. Abstract word count
abs_idx = [i for i, t in enumerate(paras) if t.startswith('Inspired by the Ka/Ks ratio')][0]
log('\nAbstract word count: %d' % len(paras[abs_idx].split()))

# 7. Supp Fig 4 legend
s4 = [i for i, t in enumerate(paras) if t.startswith('Supplementary Fig. 4')]
log('\nSupplementary Fig. 4 legend: %s' % paras[s4[0]][:120])

open(r'C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_docx_verify_dt.txt', 'w',
     encoding='utf-8').write('\n'.join(lines))
print('DONE')
