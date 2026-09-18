"""Verify the regenerated SI docx (v49): Section 3.20/3.21 content, Note 9 sync,
figure-reference fixes, and key numbers (paragraphs + table cells)."""
from docx import Document

doc = Document('results/CKI_Supplementary_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)

# also collect table cell text
cells = []
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            cells.append(c.text)
cellfull = ' | '.join(cells)

checks = []

def chk(name, cond, detail=''):
    checks.append((name, 'PASS' if cond else 'FAIL', detail))

# 1. New subsections exist
chk('3.20 heading present', '3.20 Real-Data Neutral-Drift Calibration on Technical Replicates (v49)' in full)
chk('3.21 heading present', '3.21 Per-Sample Divergence and Group Statistics for TCGA (v49)' in full)

# 2. Key numbers in 3.20 paragraphs
chk('Kang omega cal 0.963', '0.963' in full)
chk('Kang 0/30 wording', 'no pair exceeded its own null 95th percentile (0 of 30' in full)
chk('Wilson CI [0.000, 0.114]', '[0.000, 0.114]' in full)
chk('T1 FPR 28.6%', '28.6%' in full)
chk('T2 omega 90.9%', '90.9%' in full)
chk('marker Jaccard T3 1.41', '1.41 versus 1.80 for \u03c9' in full)
chk('n-bin 14.1%', '14.1%' in full)
chk('choroid 137-fold', '137-fold' in full)
chk('Bergmann 21.9 / 9.7', '21.9' in full and '9.7' in full)

# 3. Key numbers in 3.21 (tables)
chk('LUAD NN/TT 2.46 CI (table)', '2.46 [2.13, 2.86]' in cellfull)
chk('LIHC NN/TT 1.13 CI (table)', '1.13 [0.97, 1.34]' in cellfull)
chk('k_n KIRC 3.21 CI (table)', '3.21 [2.51, 4.28]' in cellfull)
chk('LUAD means 115.4/122.2/136.9 (table)', '115.4' in cellfull and '122.2' in cellfull and '136.9' in cellfull)
chk('Cox M1 1.06 [0.85, 1.32] (table)', '1.06 [0.85, 1.32]' in cellfull)
chk('Cox M1 P 0.59 (table)', '0.59' in cellfull)
chk('Dunn KRAS-WT omega (table)', 'KRAS' in cellfull and '21.57' in cellfull)
chk('Kang table cells (omega row)', '\u03c9' in cellfull and '0.963 [0.918, 0.998]' in cellfull)
chk('Ladder table T1 omega cell', '1.04 [0.97, 1.21] / 28.6%' in cellfull)

# 4. Note 9 sync
chk('Note 9 stale sentence gone',
    'The main text reports these gradients only as a one-paragraph exploratory vignette' not in full)
chk('Note 9 new sync sentence', 'reported here as denominator-dominated vignettes (Supplementary Fig. 4b)' in full)

# 5. Figure reference fixes
chk('Note 9 cross-organ now Fig. 6', '(Table 2 / Fig. 6)' in full)
chk('Supp Table 3 now Figure 7', '_fig6_clean.py (Figure 7)' in full)
chk('no stale Fig. 5 cross-organ ref', '(Table 2 / Fig. 5)' not in full)
chk('no stale Figure 6 brain ref', '_fig6_clean.py (Figure 6)' not in full)

# 6. Notes 1-15 unchanged
import re
notes = re.findall(r'Supplementary Note (\d+):', full)
chk('Notes 1-15 count = 15', len(set(notes)) == 15, f'found {sorted(set(map(int, notes)))}')

# 7. No TODO residue
chk('no TODO in SI', 'TODO' not in full and 'TODO' not in cellfull)

# 8. Table captions convention
for tag in ('3.20a', '3.20b', '3.21a', '3.21b', '3.21c', '3.21d'):
    chk(f'Table (Section {tag})', f'Table (Section {tag}).' in full)

print('===== Checks =====')
nfail = 0
for name, status, detail in checks:
    print(f'[{status}] {name} {detail}')
    if status == 'FAIL':
        nfail += 1
print(f'TOTAL: {len(checks)} checks, {nfail} failures')
