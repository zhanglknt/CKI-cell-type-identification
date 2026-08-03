#!/usr/bin/env python3
"""Fix C1 BH-FDR issue in 100_gen_reproducibility_docx.js"""
import re

with open('notebooks/100_gen_reproducibility_docx.js', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Fix 1: Replace EVT/GPD paragraph (line 361)
start1 = content.find('      p("     For each of 31,764 brain region pairs')
end1_marker = 'Output: results/phaseB_residual_evt.csv.")'
end1 = content.find(end1_marker, start1)
if start1 >= 0 and end1 >= 0:
    end1 += len(end1_marker)
    old1 = content[start1:end1]
    new1 = (
        '      p("     For each of 31,764 brain region pairs, cell type labels were shuffled '
        'B=10,000 times. Per-signal empirical P-values: P = (count(null_residual <= observed) '
        '+ 1)/(B+1). 11,541 signals (36.3%) reached the empirical P-value floor (P=9.99e-5), '
        'precluding meaningful BH-FDR correction. We therefore interpret permutation results '
        'descriptively: among the 30 Strong-tier candidates, 16 signals (6 astrocytes, 10 '
        'oligodendrocytes) reached the P-value floor indicating strong evidence of deviation '
        'from the multiplicative null model, while 14 signals (P>=0.76) showed no evidence of '
        'departure. Per-signal tests are not independent; interpretation is restricted to the '
        '30 predefined Strong candidates. Output: results/phaseB_residual_pervisign.csv, '
        'results/phaseB_residual_null.json.")'
    )
    content = content[:start1] + new1 + content[end1:]
    changes += 1
    print(f'Fix 1 (EVT paragraph): OK ({len(old1)} -> {len(new1)} chars)')
else:
    print(f'Fix 1 FAILED: start={start1}, end={end1}')

# Fix 2: Update script references (line 360)
content = content.replace(
    '      p("     Script: notebooks/09b_phaseB_residual_pervisign.py (empirical) + 09c_phaseB_residual_evt.py (EVT)"),',
    '      p("     Script: notebooks/09b_phaseB_residual_pervisign.py"),'
)
changes += 1
print('Fix 2 (script ref): OK')

# Fix 3: Update parameter table row (line 445)
content = content.replace(
    'tableRow(["Permutation null FDR", "BH across 31,764 (global EVT-extrapolated)", "Phase B (C-S3)"]',
    'tableRow(["Permutation null P-values", "Unadjusted (descriptive, FDR not applicable)", "Phase B (C-S3)"]'
)
changes += 1
print('Fix 3 (param table): OK')

# Fix 4: Update Phase B script listing (line 487)
content = content.replace(
    'p("    Phase B Statistical Upgrades (09_phaseB_statistical_upgrades.py, 09b_phaseB_residual_pervisign.py, 09c_phaseB_residual_evt.py):"),',
    'p("    Phase B Statistical Upgrades (09_phaseB_statistical_upgrades.py, 09b_phaseB_residual_pervisign.py):"),'
)
changes += 1
print('Fix 4 (script listing): OK')

# Fix 5: Remove EVT file references (lines 493-494)
content = content.replace(
    '      code("      results/phaseB_residual_evt.csv              # EVT-resolved P-values (31,764 rows) (C-S3)"),\n',
    ''
)
content = content.replace(
    '      code("      results/phaseB_residual_evt.json             # EVT analysis summary (C-S3)"),\n',
    ''
)
changes += 1
print('Fix 5 (EVT file refs): OK')

# Fix 6: Update verification checklist (line 526)
content = content.replace(
    'p("[\\u2713] Phase B: Verify permutation null (B=10,000) in results/phaseB_residual_evt.csv (EVT-resolved P-values). (Section 5.3)"),',
    'p("[\\u2713] Phase B: Verify permutation null (B=10,000) in results/phaseB_residual_pervisign.csv (descriptive P-values, FDR not applicable). (Section 5.3)"),'
)
changes += 1
print('Fix 6 (checklist): OK')

# Verify
for kw in ['EVT', 'GPD', 'q=1.0', 'FDR<0.05']:
    count = content.count(kw)
    if count > 0:
        print(f'WARNING: {count}x "{kw}"')
    else:
        print(f'CLEAN: "{kw}"')

print(f'\nTotal changes: {changes}/6')

with open('notebooks/100_gen_reproducibility_docx.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
