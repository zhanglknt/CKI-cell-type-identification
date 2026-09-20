# v49.8: cover letter + supplementary note — change-detection framing, drop classification AUC.
import io, sys

# ---------- CL ----------
P = r'C:\Users\KnightZ\Desktop\细胞受选择\generate_cover_letter_nc.py'
src = io.open(P, encoding='utf-8').read()

# C1. module docstring evidence list (lines ~26-27)
old = "  manuscript Table 1 (classification AUC 0.680) and simulation\n  results (FPR 0.00 vs 0.55-0.58; AUC 0.80)."
new = "  simulation change-detection results (FPR 0.00 vs 0.55-0.58; AUC 0.80\n  rank 1/6, skin replication 0.91)."
assert src.count(old) == 1, 'C1 anchor'
src = src.replace(old, new)
print('OK  C1 docstring evidence list')

# C2. body paragraph (lines 118-125, 1-based) -> change-detection framing
lines = src.split('\n')
assert 'Two properties' in lines[117], f'C2 anchor1: {lines[117]!r}'
assert 'biology (Fig. 3). And the pan-cancer divergence map, with the ' in lines[124], f'C2 anchor2: {lines[124]!r}'
new_block = [
    '        "Two properties of this work are worth stating explicitly. CKI is "',
    '        "a specificity-first index, designed to detect dynamic cell-state "',
    '        "changes rather than to discriminate static cell types: on the "',
    '        "benchmark matched to its question domain\\u2014false divergence "',
    '        "calls on real technical and donor drift\\u2014it misreports least "',
    '        "among the continuous divergence metrics while retaining "',
    '        "sensitivity to biology (Fig. 3); in the ground-truth simulation "',
    '        "it ranks first of six metrics at separating injected functional "',
    '        "change from neutral drift (AUC = 0.80; Fig. 2e). And the "',
    '        "pan-cancer divergence map, with the "',
]
lines = lines[:117] + new_block + lines[125:]
src = '\n'.join(lines)
print('OK  C2 body paragraph reframed')
io.open(P, 'w', encoding='utf-8', newline='').write(src)

rb = io.open(P, encoding='utf-8').read()
assert '0.680' not in rb, 'CL still cites 0.680'
assert 'cell-type classification' not in rb, 'CL still mentions classification'
assert 'dynamic cell-state' in rb, 'CL missing new framing'
print('OK  CL readback (no 0.680 / no classification / new framing present)')

# ---------- SI ----------
P2 = r'C:\Users\KnightZ\Desktop\细胞受选择\notebooks\68_gen_supplementary_nc.py'
s2 = io.open(P2, encoding='utf-8').read()
old2 = "    'for CKI \\u03c9 significance inference; ROC-AUC for cell type classification '\n    'performance assessment.'"
new2 = "    'for CKI \\u03c9 significance inference; ROC-AUC for benchmark performance '\n    'assessment (parameter sweep and functional-change detection).'"
assert s2.count(old2) == 1, 'S1 anchor'
s2 = s2.replace(old2, new2)
io.open(P2, 'w', encoding='utf-8', newline='').write(s2)
rb2 = io.open(P2, encoding='utf-8').read()
assert 'ROC-AUC for cell type classification' not in rb2
assert 'parameter sweep and functional-change detection' in rb2
print('OK  S1 SI statistical-tests list reworded')
print('ALL CL/SI EDITS PASS')
