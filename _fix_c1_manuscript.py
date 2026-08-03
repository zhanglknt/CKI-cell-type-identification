#!/usr/bin/env python3
"""Fix C1 BH-FDR issue in generate_manuscript_nar.py"""
import re

with open('generate_manuscript_nar.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Helper: search using ASCII-only patterns with flexible unicode
def find_between(start_marker, end_marker):
    """Find text between two ASCII markers, returning (start_pos, end_pos)"""
    s = content.find(start_marker)
    if s < 0:
        return (-1, -1)
    e = content.find(end_marker, s + len(start_marker))
    if e < 0:
        return (s, -1)
    return (s, e + len(end_marker))

# ============================================================
# Edit 1: Methods - Replace EVT/BH-FDR paragraph
# (from "Benjamini-Hochberg FDR..." to end of that p() call)
# ============================================================
start1, end1 = find_between(
    'Benjamini-Hochberg FDR correction was applied at two levels',
    "search space.'"
)
if start1 >= 0 and end1 >= 0:
    old1 = content[start1:end1]
    new1 = (
        'Given the large number of tests (m = 31,764) and the finite '
        'permutation resolution (B = 10,000), 36.3% of signals '
        '(11,541/31,764) reached the empirical P-value floor '
        '(P = 9.99 \\u00d7 10\\u207b\\u2075), precluding meaningful '
        'Benjamini-Hochberg FDR correction. We therefore report unadjusted '
        'permutation P-values and interpret significance descriptively: '
        'signals reaching the P-value floor (no null permutation exceeded '
        'the observed residual in 10,000 shuffles) are considered strong '
        'evidence of deviation from the multiplicative null model, while '
        'signals with P \\u2265 0.50 show little to no evidence of departure. '
        'Per-signal tests are not independent (the same cell type or region '
        'pair appears in multiple comparisons); we restrict biological '
        'interpretation to the 30 predefined Strong candidates rather than '
        'the full 31,764 search space, and treat the permutation results as '
        'descriptive validation rather than formal FDR-controlled inference.'
    )
    content = content[:start1] + new1 + content[end1:]
    changes += 1
    print(f"Edit 1 (Methods BH-FDR): OK ({len(old1)} -> {len(new1)} chars)")
else:
    print(f"Edit 1: markers not found (start={start1}, end={end1})")

# ============================================================
# Edit 3: Results - "Permutation testing (B = 10,000) with EVT..."
# ============================================================
start3, end3 = find_between(
    'Permutation testing (B = 10,000) with EVT extrapolation',
    ", q = 1.0)."
)
if start3 >= 0 and end3 >= 0:
    old3 = content[start3:end3]
    new3 = (
        'Permutation testing (B = 10,000) revealed that 16 of 30 Strong '
        'signals reached the permutation P-value floor (P = 9.99 \\u00d7 '
        '10\\u207b\\u2075, i.e., no permutation out of 10,000 produced a residual '
        'as extreme as observed): all 6 astrocyte and all 10 oligodendrocyte '
        'signals. The remaining 14 signals (10 microglia, 1 fibroblast, '
        '3 vascular) showed no evidence of deviation from the multiplicative '
        'null model (all P \\u2265 0.76). Given the large number of tests '
        '(m = 31,764) and P-value floor saturation (36.3% of signals at '
        'P = 9.99 \\u00d7 10\\u207b\\u2075), formal FDR correction is not applicable; '
        'the 16 floor-reaching signals are interpreted as descriptive evidence '
        'of residual deviation from the multiplicative null, not as '
        'FDR-controlled discoveries.'
    )
    content = content[:start3] + new3 + content[end3:]
    changes += 1
    print(f"Edit 3 (Results Strong): OK ({len(old3)} -> {len(new3)} chars)")
else:
    print(f"Edit 3: markers not found (start={start3}, end={end3})")

# ============================================================
# Edit 4: Oligodendrocytes - "reached statistical significance in permutation testing"
# ============================================================
start4, end4 = find_between(
    ', all of which reached statistical significance in permutation testing (EVT-extrapolated P',
    ', FDR < 0.05)'
)
if start4 >= 0 and end4 >= 0:
    old4 = content[start4:end4]
    new4 = (
        ', all of which reached the permutation P-value floor '
        '(P = 9.99 \\u00d7 10\\u207b\\u2075, B = 10,000)'
    )
    content = content[:start4] + new4 + content[end4:]
    changes += 1
    print(f"Edit 4 (Oligodendrocytes): OK ({len(old4)} -> {len(new4)} chars)")
else:
    print(f"Edit 4: markers not found (start={start4}, end={end4})")

# ============================================================
# Edit 5: Astrocytes - "all of which reached statistical significance (EVT-"
# ============================================================
start5, end5 = find_between(
    ', all of which reached statistical significance (EVT-extrapolated P',
    ', FDR < 0.05)'
)
if start5 >= 0 and end5 >= 0:
    old5 = content[start5:end5]
    new5 = (
        ', all of which reached the permutation P-value floor '
        '(P = 9.99 \\u00d7 10\\u207b\\u2075, B = 10,000)'
    )
    content = content[:start5] + new5 + content[end5:]
    changes += 1
    print(f"Edit 5 (Astrocytes): OK ({len(old5)} -> {len(new5)} chars)")
else:
    print(f"Edit 5: markers not found (start={start5}, end={end5})")

print(f"\nTotal changes (including Edits 2,6,7 from previous run): {changes + 3}/7")

with open('generate_manuscript_nar.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("File saved.")
