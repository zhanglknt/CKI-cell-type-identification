# -*- coding: utf-8 -*-
"""Verify the regenerated v49 cover letter: word count, format, content keys."""
from docx import Document

doc = Document(r'C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_NC_Cover_Letter.docx')
paras = [p.text for p in doc.paragraphs]

lines = []
def log(s=''):
    lines.append(s)
    print(s)

# 1. Word count (all paragraphs incl. salutation/signature)
total_words = sum(len(t.split()) for t in paras if t.strip())
log('Total word count (incl. salutation/closing): %d' % total_words)
body_words = sum(len(t.split()) for t in paras[1:-3] if t.strip())
log('Body word count (excl. salutation/signature block): %d' % body_words)

# 2. Format checks
sec = doc.sections[0]
from docx.shared import Inches
log('Margins (in): top=%.2f bottom=%.2f left=%.2f right=%.2f' % (
    sec.top_margin.inches, sec.bottom_margin.inches,
    sec.left_margin.inches, sec.right_margin.inches))
st = doc.styles['Normal'].font
log('Font: %s %spt' % (st.name, st.size.pt))
log('Paragraph count: %d' % len([t for t in paras if t.strip()]))

# 3. Content keys
keys = ['principled separation', 'Ka/Ks ratio', '0.00 versus 0.55', '0 of 30',
        '36.7%', '23.3%', '2,161', '28.6%', '44\u201345%', '1.04 \u2192 1.76 \u2192 1.80',
        '1.07 \u2192 3.32 \u2192 2.98', '3,596 TCGA', '1.13\u20132.46',
        '2.1\u20133.6-fold', 'P = 7.8 \u00d7 10\u207b\u2077',
        'Previously raised concerns', 'AUC = 0.680', '5th of 5',
        'misreporting control', 'pan-cancer tissue-level divergence map',
        'driver-class decomposition', 'q = 0.520', 'tissue-level functional divergence',
        'Zenodo DOI 10.5281/zenodo.22735744', 'grant 32370682',
        'Fabian Theis', 'Joshua Welch', 'Sten Linnarsson', 'Patrik St\u00e5hl',
        'Sch\u00e4ffer', 'Zemin Zhang']
log('\nContent key presence:')
missing = []
for k in keys:
    n = sum(t.count(k) for t in paras)
    log('  %r: %d' % (k, n))
    if n == 0:
        missing.append(k)
log('\nMISSING KEYS: %s' % (missing if missing else 'none'))

# 4. Old framing gone
gone = ['better metric', 'novel computational method', 'headline result is a specificity-first']
log('\nOld framing (expect 0):')
for g in gone:
    log('  %r: %d' % (g, sum(t.count(g) for t in paras)))

# 5. Print the concern-response paragraph verbatim
idx = [i for i, t in enumerate(paras) if 'Previously raised concerns' in t][0]
log('\n=== Concern-response paragraph (verbatim) ===')
log(paras[idx])

open(r'C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_cl_verify.txt', 'w',
     encoding='utf-8').write('\n'.join(lines))
print('DONE')
