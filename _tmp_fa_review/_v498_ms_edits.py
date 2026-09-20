# v49.8: generate_manuscript_nc.py — cut cell-type classification benchmark,
# renumber main Table 2 -> Table 1. Atomic replaces with count asserts + readback.
import io, sys

P = r'C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py'
src = io.open(P, encoding='utf-8').read()
orig = src

def rep(old, new, n=1, tag=''):
    global src
    c = src.count(old)
    assert c == n, f'{tag}: count {c} != {n}'
    src = src.replace(old, new)
    print(f'OK  {tag} ({c})')

# E1. line ~521: drop 3 classification sentences, keep reversal half (drop "Critically, ")
rep(
    "p(f'CKI showed moderate cell-type classification performance (AUC = {_au[\"cki_omega\"]:.3f}, ranked 5th of 5 methods; Table 1). "
    "The pair-level bootstrap 95% CI ([0.609, 0.745], B = 2,000) widens to [0.540, 0.804] under cell-type-entry clustering: "
    "the classification advantage is weak and resampling-unit dependent. "
    "The lower ranking is expected by design: CKI down-weights shared HK patterns to isolate functional divergence, "
    "trading global-identity sensitivity for identity-gene divergence. Critically, CKI was the only metric",
    "p(f'CKI was the only metric",
    1, 'E1 classification paragraph cut (reversal kept)')

# E2. Fig 2 legend tail: drop Table 1 pointer
rep("gave AUC = 0.91 (rank 1/6). Cell-type classification performance on Tabula Sapiens is reported in Table 1.')",
    "gave AUC = 0.91 (rank 1/6).')",
    1, 'E2 Fig2 legend Table 1 pointer removed')

# E3. Methods: scikit-learn sentence
rep("Inter-metric Spearman correlations and cell-type classification ROC-AUC were computed using scikit-learn.",
    "Inter-metric Spearman correlations were computed using scikit-learn.",
    1, 'E3 Methods classification ROC-AUC removed')

# E4. line ~564: four main-text Table 2 -> Table 1 (Supplementary Table 2 untouched)
rep('(Fig. 5; Table 2; Supplementary Fig. 5)', '(Fig. 5; Table 1; Supplementary Fig. 5)', 1, 'E4a Fig5 Table ref')
rep('(Supplementary Note 9) (Table 2).', '(Supplementary Note 9) (Table 1).', 1, 'E4b Note 9 Table ref')
rep('upper block of Table 2', 'upper block of Table 1', 1, 'E4c upper block')
rep('lower block of Table 2', 'lower block of Table 1', 1, 'E4d lower block')

# E5. xlsx block: drop classification sheet (lines 223-247, 1-based), make cross-organ the only sheet 'Table 1'
lines = src.split('\n')
assert lines[222].strip() == 'ws1 = wb.active', f'E5 anchor1: {lines[222]!r}'
assert lines[246].strip() == "ws2 = wb.create_sheet('Table 2')", f'E5 anchor2: {lines[246]!r}'
new_block = [
    "    t2d = DATA['table2_data']",
    "    has_sep = any(int(r[3]) < 5 for r in t2d) and any(int(r[3]) >= 5 for r in t2d)",
    '    ws2 = wb.active',
    "    ws2.title = 'Table 1'",
]
lines = lines[:222] + new_block + lines[247:]
src = '\n'.join(lines)
print('OK  E5 xlsx classification sheet removed (rows 223-247 -> 4 rows)')

# E6. cap2: Table 2 -> Table 1 caption
rep('cap2 = (f"Table 2. Cross-organ conservation ranking by cell type (Tabula Sapiens, "',
    'cap2 = (f"Table 1. Cross-organ conservation ranking by cell type (Tabula Sapiens, "',
    1, 'E6 cap2 renumbered')

assert src != orig
io.open(P, 'w', encoding='utf-8', newline='').write(src)

# ---- readback ----
rb = io.open(P, encoding='utf-8').read()
checks = [
    ('cell-type classification performance' not in rb, 'RB1 no classification-performance phrase'),
    ('ranked 5th of 5 methods' not in rb, 'RB2 no 5th-of-5'),
    ('is reported in Table 1' not in rb, 'RB3 legend pointer gone'),
    ('cell-type classification ROC-AUC' not in rb, 'RB4 Methods clean'),
    ('(Fig. 5; Table 1; Supplementary Fig. 5)' in rb, 'RB5 Fig5->Table 1'),
    ('upper block of Table 1' in rb and 'lower block of Table 1' in rb, 'RB6 blocks renamed'),
    ("ws2.title = 'Table 1'" in rb and "create_sheet('Table 2')" not in rb, 'RB7 xlsx single sheet'),
    ('cap2 = (f"Table 1. Cross-organ conservation' in rb, 'RB8 cap2'),
    ('Table 2' not in rb.replace('Supplementary Table 2', ''), 'RB9 no stray main Table 2'),
]
bad = [m for ok, m in checks if not ok]
for ok, m in checks:
    print(('PASS ' if ok else 'FAIL ') + m)
if bad:
    sys.exit(1)
print('ALL EDITS + READBACK PASS')
