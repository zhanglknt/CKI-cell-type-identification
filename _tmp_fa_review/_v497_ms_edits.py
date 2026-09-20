#!/usr/bin/env python3
"""v49.7 MS edits: Fig 2E -> change-detection ROC (atomic, counted, read-back)."""
import io, sys

F = 'generate_manuscript_nc.py'
src = io.open(F, encoding='utf-8').read()

edits = []

# --- 1. Fig 2 legend: title + panel (e) ------------------------------------
old_t = 'Figure 2. CKI calibration on Tabula Muris mouse data and benchmarking against standard metrics on Tabula Sapiens.'
new_t = ('Figure 2. CKI calibration on Tabula Muris mouse data, metric correlation structure on '
         'Tabula Sapiens, and functional-change detection in the ground-truth simulation.')
edits.append(('fig2-title', old_t, new_t, 1))

old_e = ("(e) ROC curves for cell-type classification across five metrics on Tabula Sapiens data.'")
new_e = ("(e) ROC curves for discriminating injected functional signal (\\u03b4 \\u2265 0.25) from neutral "
         "drift in the semi-synthetic ground-truth simulation (marrow B-cell background; 600 functional "
         "versus 250 neutral replicates). CKI \\u03c9 ranked first of six metrics (AUC = 0.80); independent "
         "replication on a skin keratinocyte background gave AUC = 0.91 (rank 1/6). Cell-type classification "
         "performance on Tabula Sapiens is reported in Table 1.'")
edits.append(('fig2-panelE', old_e, new_e, 1))

# --- 2. line 511 anchor: (Fig. 2d, e) -> (Fig. 2d) --------------------------
old_a = 'human column) (Fig. 2d, e).'
new_a = 'human column) (Fig. 2d).'
edits.append(('r3-anchor', old_a, new_a, 1))

# --- 3. Result 3b: attach (Fig. 2e) to the AUC sentence ---------------------
old_b = ('from neutral perturbations (AUC = 0.80, versus 0.72 for k_f alone, 0.64 for raw JS, '
         '0.58 for cosine, and 0.21 for k_n alone; bootstrap 95% CI')
new_b = ('from neutral perturbations (Fig. 2e; AUC = 0.80, versus 0.72 for k_f alone, 0.64 for raw JS, '
         '0.58 for cosine, and 0.21 for k_n alone; bootstrap 95% CI')
edits.append(('r3b-auc', old_b, new_b, 1))

# --- 4. background-2 sentence: reference Fig. 2e ----------------------------
old_c = 'AUC(\\u03c9) = 0.908 versus AUC(k_f) = 0.859, with the same metric ranking'
new_c = 'AUC(\\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e), with the same metric ranking'
edits.append(('r3b-bg2', old_c, new_c, 1))

for tag, old, new, want in edits:
    n = src.count(old)
    if n != want:
        print(f'FAIL {tag}: found {n}, want {want}')
        sys.exit(1)
    src = src.replace(old, new)
    print(f'OK   {tag}: replaced {n}')

io.open(F, 'w', encoding='utf-8', newline='\n').write(src)

# read-back verification
chk = io.open(F, encoding='utf-8').read()
for tag, old, new, _ in edits:
    assert new.replace('\\\\', '\\') in chk or new in chk, tag
print('READ-BACK OK: all 4 edits persisted')
