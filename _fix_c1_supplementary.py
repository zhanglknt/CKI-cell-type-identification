#!/usr/bin/env python3
"""Fix C1 BH-FDR issue in 68_gen_supplementary_en.py"""
import re

with open('notebooks/68_gen_supplementary_en.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Fix 1: Replace the BH-FDR two-level paragraph
start1 = content.find('magnitude. For the brain atlas analysis, 31,764')
end1_marker = "theory (GPD tail extrapolation, see SN 3.3).'"
end1 = content.find(end1_marker, start1)
if start1 >= 0 and end1 >= 0:
    end1 += len(end1_marker)
    old1 = content[start1:end1]
    new1 = (
        'magnitude. For the brain atlas analysis, 31,764 cross-region comparisons yielded '
        '30 Strong candidates (residual < 0.3). Per-signal empirical P-values were computed '
        'via permutation testing (B = 10,000); however, 36.3% of signals (11,541/31,764) '
        'reached the empirical P-value floor (P = 9.99 \\u00d7 10\\u207b\\u2075), precluding '
        'meaningful Benjamini-Hochberg FDR correction. We therefore report unadjusted '
        'permutation P-values and interpret significance descriptively: 16 of 30 Strong-tier '
        'candidates reached the P-value floor (no null permutation exceeded the observed '
        'residual in 10,000 shuffles), while 14 signals showed no evidence of departure '
        '(all P \\u2265 0.76).')
    content = content[:start1] + new1 + content[end1:]
    changes += 1
    print(f'Fix 1 (BH-FDR two-level): OK ({len(old1)} -> {len(new1)} chars)')
else:
    print(f'Fix 1 FAILED: start={start1}, end={end1}')

# Fix 2: Replace the EVT/GPD add_para block
start2 = content.find(
    "add_para(\n    'Permutation-based validation of the multiplicative residual model was"
)
end2_marker = "characterization; Supplementary Figure 9: residual null distribution.)'\n)"
end2 = content.find(end2_marker, start2)
if start2 >= 0 and end2 >= 0:
    end2 += len(end2_marker)
    old2 = content[start2:end2]
    new2 = (
        "add_para(\n"
        "    'Permutation-based validation of the multiplicative residual model was '\n"
        "    'performed using B = 10,000 permutations. For each of the 31,764 brain '\n"
        "    'region pairs, cell type labels were randomly shuffled within region pairs '\n"
        "    'to construct a null distribution of residuals. Per-signal empirical '\n"
        "    'P-values were computed as P = (count(null_residual \\u2264 observed_residual) + 1) '\n"
        "    '/ (B + 1). Of the 31,764 signals, 11,541 (36.3%) reached the empirical '\n"
        "    'P-value floor (P = 9.99 \\u00d7 10\\u207b\\u2075) of the B = 10,000 permutation test, '\n"
        "    'precluding meaningful Benjamini-Hochberg FDR correction. We therefore '\n"
        "    'interpret the permutation results descriptively: among the 30 Strong-tier '\n"
        "    'candidates, 16 signals (6 astrocytes, 10 oligodendrocytes) reached the '\n"
        "    'P-value floor, indicating strong evidence of deviation from the '\n"
        "    'multiplicative null model, while 14 signals (10 microglia, 1 fibroblast, '\n"
        "    '3 vascular) showed no evidence of departure (P \\u2265 0.76). Per-signal '\n"
        "    'tests are not independent (the same cell type or region pair appears in '\n"
        "    'multiple comparisons); we restrict biological interpretation to the 30 '\n"
        "    'predefined Strong candidates. (Supplementary Figure 8: \\u03c9 distribution '\n"
        "    'characterization; Supplementary Figure 9: residual null distribution.)'\n)"
    )
    content = content[:start2] + new2 + content[end2:]
    changes += 1
    print(f'Fix 2 (EVT/GPD add_para): OK ({len(old2)} -> {len(new2)} chars)')
else:
    print(f'Fix 2 FAILED: start={start2}, end={end2}')

# Verify
for kw in ['EVT', 'GPD', 'q = 1.0', 'FDR < 0.05']:
    count = content.count(kw)
    if count > 0:
        print(f'WARNING: {count}x "{kw}"')
    else:
        print(f'CLEAN: "{kw}"')

print(f'\nTotal changes: {changes}/2')

with open('notebooks/68_gen_supplementary_en.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
