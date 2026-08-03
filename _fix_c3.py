"""Fix C3: Mouse k_n/k_f computation description contradiction."""
import re

# ===== FIX 1: generate_manuscript_nar.py =====
with open('generate_manuscript_nar.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Fix 1a: Line 462 - Methods: add hybrid scheme note
old1 = ('In the default configuration, identity genes are the top-2,000 '
        'highly variable genes (HVGs; Seurat flavor), excluding HK genes '
        'to maintain k_n/k_f independence.')
new1 = ('In the default configuration (used for the Tabula Muris full '
        'pairwise matrix, Fig. 2), identity genes are the top-2,000 '
        'highly variable genes (HVGs; Seurat flavor), excluding HK genes '
        'to maintain k_n/k_f independence. For the mouse pilot calibration '
        'and all cross-species analyses (human, TCGA, brain), we used a '
        'hybrid scheme: k_n is computed globally with a shared HK gene set, '
        'while k_f uses the top-200 differentially expressed genes (ranked '
        'by absolute mean difference) for each specific pair, with HK genes '
        'excluded.')
if old1 in content:
    content = content.replace(old1, new1)
    changes += 1
    print('Fix 1a (Methods k_f description): OK')
else:
    print('Fix 1a: NOT FOUND')

# Fix 1b: Line 471 - Calibration section: distinguish full matrix vs pilot
old1b = ('Identity genes were the top-{_ds["n_hvg"]:,} highly variable genes '
         '(HVGs; Seurat), excluding HK genes (Fig. 2).')
new1b = ('For the full pairwise matrix (703 pairs, Fig. 2), identity genes '
         'were the top-{_ds["n_hvg"]:,} highly variable genes (HVGs; Seurat), '
         'excluding HK genes. For the pilot calibration (controls, S/D/X '
         'categories), we used a hybrid scheme: global k_n (shared HK gene set) '
         'with per-pair k_f (top-200 differentially expressed genes, ranked '
         'by absolute mean difference, HK excluded).')
if old1b in content:
    content = content.replace(old1b, new1b)
    changes += 1
    print('Fix 1b (Calibration k_f description): OK')
else:
    print('Fix 1b: NOT FOUND')
    # Debug: find the actual text
    idx = content.find('Identity genes were the top-')
    if idx >= 0:
        snippet = content[idx:idx+120]
        print(f'  Found: {repr(snippet)}')

with open('generate_manuscript_nar.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Manuscript: {changes}/2 changes applied')

# ===== FIX 2: 100_gen_reproducibility_docx.js =====
with open('notebooks/100_gen_reproducibility_docx.js', 'r', encoding='utf-8') as f:
    content2 = f.read()

changes2 = 0

# Fix 2a: Line 265 - step 7
old2a = 'Compute per-pair k_f with global HVG set (2,000 genes, HK excluded).'
new2a = 'Compute per-pair k_f with top-200 DE genes (ranked by |mean_diff|, HK excluded).'
if old2a in content2:
    content2 = content2.replace(old2a, new2a)
    changes2 += 1
    print('Fix 2a (Repro Guide step 7): OK')
else:
    print('Fix 2a: NOT FOUND')

# Fix 2b: Line 429 - Parameter table: split mouse HVG vs pilot k_f
old2b = ('tableRow(["Number of HVGs", "2,000 (global, for k_f)", '
         '"mouse (Tabula Muris)"], [3200, 1600, 4200]),')
new2b = (
    'tableRow(["Number of HVGs", "2,000 (global, for k_f; Fig. 2 heatmap only)", '
    '"mouse full matrix"], [3200, 1600, 4200]),\n'
    '          tableRow(["Pilot k_f genes", "200 (per-pair DE, |mean_diff|)", '
    '"mouse pilot calibration"], [3200, 1600, 4200]),'
)
if old2b in content2:
    content2 = content2.replace(old2b, new2b)
    changes2 += 1
    print('Fix 2b (Parameter table HVG): OK')
else:
    print('Fix 2b: NOT FOUND')

# Fix 2c: k_n computation mode row
old2c = ('tableRow(["k_n computation mode", "per-pair (brain), global (human/TCGA)", '
         '"Phase C (C-M3)"], [3200, 1600, 4200]),')
new2c = ('tableRow(["k_n computation mode", "per-pair (brain), '
         'global (mouse pilot/human/TCGA)", "Phase C (C-M3)"], '
         '[3200, 1600, 4200]),')
if old2c in content2:
    content2 = content2.replace(old2c, new2c)
    changes2 += 1
    print('Fix 2c (k_n mode row): OK')
else:
    print('Fix 2c: NOT FOUND')

with open('notebooks/100_gen_reproducibility_docx.js', 'w', encoding='utf-8') as f:
    f.write(content2)

print(f'Repro Guide: {changes2}/3 changes applied')
print('\nAll C3 fixes complete.')
