"""Patch manuscript script to replace remaining hardcoded values with dynamic CSV reads."""
from _load_manuscript_data import get_manuscript_data
DATA = get_manuscript_data()
_ds = DATA['datasets']
_mc = DATA['mouse_calibration']
_h = DATA['human']
_sc = DATA['spearman_corr']
_tc = DATA['tcga']
_br = DATA['brain']
_br_ct = _br['cell_types']
_au = DATA['table1_auc']
_sb = DATA['sweep']
_co = DATA['cross_organ_spearman']

with open('generate_manuscript_genome_biology.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper: find brain cell type by name keyword
def find_ct(name):
    for ct in _br_ct:
        if name.lower() in ct['name'].lower():
            return ct
    return None

# === Build TCGA NN/TT dynamic paragraph ===
cancers = sorted(_tc['cancers'], key=lambda c: c['nn_tt_ratio'])
min_c = cancers[0]
max_c = cancers[-1]
mid_c = [c for c in cancers if c != min_c and c != max_c]
mid_vals = ', '.join([f"{c['name'].replace('TCGA-','')} {c['nn_tt_ratio']:.2f}" for c in mid_c])

nn_tt_var_name = 'cancers = sorted(_tc["cancers"], key=lambda c: c["nn_tt_ratio"])\n'
nn_tt_var_name += 'min_c = cancers[0]; max_c = cancers[-1]\n'
nn_tt_var_name += 'mid_c = [c for c in cancers if c != min_c and c != max_c]\n'

nn_tt_fstring = (
    'p(f\'The most striking finding was that tumors are more transcriptionally homogeneous than '
    'normal tissues. In all five cancer types, the median NN/TT \u03c9 ratio exceeded 1.0, '
    'meaning that normal individuals differ more from each other than tumors differ from each other. '
    '{min_c["name"].replace("TCGA-","")} ({min_c["name"]}) showed the smallest contrast '
    '(median NN/TT = {min_c["nn_tt_ratio"]:.2f}), while {max_c["name"].replace("TCGA-","")} '
    '({max_c["name"]}) showed the largest (median NN/TT = {max_c["nn_tt_ratio"]:.2f}), '
    'with intermediate values for '
    + ''.join([f'{{mid_c[{i}]["name"].replace("TCGA-","")}} {{mid_c[{i}]["nn_tt_ratio"]:.2f}}' + 
              (', ' if i < len(mid_c)-1 else '') for i in range(len(mid_c))]) +
    '. This convergence toward shared transcriptional states may represent common vulnerabilities '
    'across genetically diverse tumors.\')'
)

# === Clinical severity paragraph ===
clin = _tc['clinical']
lihc = sorted([r for r in clin if r['cancer'] == 'LIHC' and r['stratification'] == 'Edmondson_grade'],
              key=lambda x: int(x['group'][1:]))
brca = sorted([r for r in clin if r['cancer'] == 'BRCA' and r['stratification'] == 'PAM50'],
              key=lambda x: -x['omega_mean'])
luad = sorted([r for r in clin if r['cancer'] == 'LUAD' and r['stratification'] == 'mutation'],
              key=lambda x: -x['omega_mean'])

lihc_str = ' > '.join([f"G{int(r['group'][1:])} ({r['omega_mean']:.1f} \u00b1 {r['omega_std']:.1f}, n = {r['n']})" for r in lihc])

brca_first = brca[0]
brca_rest = brca[1:-1]
brca_last = brca[-1]
brca_mid_str = ', '.join([f"followed by {r['group']} ({r['omega_mean']:.1f} \u00b1 {r['omega_std']:.1f}, n = {r['n']})" for r in brca_rest])

luad_wt = [r for r in luad if r['group'] == 'WT'][0]
luad_mut = [r for r in luad if r['group'] != 'WT']
luad_mut_str = ' and '.join([f"{r['group']}-mutant ({r['omega_mean']:.1f} \u00b1 {r['omega_std']:.1f}, n = {r['n']})" for r in luad_mut])

# Now build as f-string variable for inline use
clinical_prep = (
    f"lihc = sorted([r for r in _tc['clinical'] if r['cancer'] == 'LIHC' "
    f"and r['stratification'] == 'Edmondson_grade'], key=lambda x: int(x['group'][1:]))\n"
    f"brca = sorted([r for r in _tc['clinical'] if r['cancer'] == 'BRCA' "
    f"and r['stratification'] == 'PAM50'], key=lambda x: -x['omega_mean'])\n"
    f"luad = sorted([r for r in _tc['clinical'] if r['cancer'] == 'LUAD' "
    f"and r['stratification'] == 'mutation'], key=lambda x: -x['omega_mean'])\n"
    f"luad_wt = [r for r in luad if r['group'] == 'WT'][0]\n"
    f"luad_mut = [r for r in luad if r['group'] != 'WT']\n"
)

clinical_fstring = (
    "p(f'We then asked whether \\u03c9 tracks with clinical severity within cancer types. "
    "In liver cancer, \\u03c9 decreased with increasing Edmondson grade [10]: "
    + ' + '.join([f"{{lihc[{i}]['group']}} ({{lihc[{i}]['omega_mean']:.1f}} \\u00b1 {{lihc[{i}]['omega_std']:.1f}}, n = {{lihc[{i}]['n']}})" + 
                  (' > ' if i < len(lihc)-1 else '') for i in range(len(lihc))]) +
    " (Jonckheere-Terpstra trend test, P < 0.001). "
    f"In breast cancer, PAM50 subtype analysis [11,12] revealed a gradient of transcriptional heterogeneity: "
    f"{{brca[0]['group']}} tumors had the highest intratumoral \\u03c9 ({{brca[0]['omega_mean']:.1f}} \\u00b1 {{brca[0]['omega_std']:.1f}}, n = {{brca[0]['n']}}), "
    + ', '.join([f"followed by {{brca[{i}]['group']}} ({{brca[{i}]['omega_mean']:.1f}} \\u00b1 {{brca[{i}]['omega_std']:.1f}}, n = {{brca[{i}]['n']}})" for i in range(1, len(brca)-1)]) +
    f", with {{brca[{len(brca)-1}]['group']}} tumors having the lowest \\u03c9 ({{brca[{len(brca)-1}]['omega_mean']:.1f}} \\u00b1 {{brca[{len(brca)-1}]['omega_std']:.1f}}, n = {{brca[{len(brca)-1}]['n']}}; Kruskal-Wallis, P = 0.0002). "
    "Lung adenocarcinoma mutation stratification showed significant differences (Kruskal-Wallis, P = 0.017), "
    f"with {{luad_mut[0]['group']}}-mutant ({{luad_mut[0]['omega_mean']:.1f}} \\u00b1 {{luad_mut[0]['omega_std']:.1f}}, n = {{luad_mut[0]['n']}}) "
    f"and {{luad_mut[1]['group']}}-mutant tumors ({{luad_mut[1]['omega_mean']:.1f}} \\u00b1 {{luad_mut[1]['omega_std']:.1f}}, n = {{luad_mut[1]['n']}}) "
    f"exhibiting higher \\u03c9 than wild-type tumors ({{luad_wt['omega_mean']:.1f}} \\u00b1 {{luad_wt['omega_std']:.1f}}, n = {{luad_wt['n']}}).')"
)

# === Build replacements ===
old_nn_tt = "p('The most striking finding was that tumors are more transcriptionally homogeneous than normal tissues. In all five cancer types, the median NN/TT \u03c9 ratio exceeded 1.0, meaning that normal individuals differ more from each other than tumors differ from each other. Breast cancer (BRCA) showed the smallest contrast (median NN/TT = 1.40), while liver cancer (LIHC) showed the largest (median NN/TT = 2.83), with intermediate values for lung adenocarcinoma (LUAD 1.60), lung squamous (LUSC 1.43), and kidney clear cell (KIRC 1.98). This convergence toward shared transcriptional states may represent common vulnerabilities across genetically diverse tumors.')"

content = content.replace(old_nn_tt, nn_tt_fstring)
print('OK: NN/TT paragraph')

old_clinical = "p('We then asked whether \u03c9 tracks with clinical severity within cancer types. In liver cancer, \u03c9 decreased with increasing Edmondson grade [10]: G1 (101.8 \u00b1 46.8, n = 39) > G2 (100.2 \u00b1 63.9, n = 133) > G3 (96.8 \u00b1 58.2, n = 105) > G4 (90.0 \u00b1 57.8, n = 11; Jonckheere-Terpstra trend test, P < 0.001). In breast cancer, PAM50 subtype analysis [11,12] revealed a gradient of transcriptional heterogeneity: Luminal A tumors had the highest intratumoral \u03c9 (344.5 \u00b1 323.4, n = 224), followed by Luminal B (313.6 \u00b1 282.7, n = 123), HER2-enriched (263.0 \u00b1 255.6, n = 55), and Basal-like tumors (223.4 \u00b1 183.7, n = 97), with Normal-like tumors having the lowest \u03c9 (108.0 \u00b1 65.5, n = 7; Kruskal-Wallis, P = 0.0002). Lung adenocarcinoma mutation stratification showed significant differences (Kruskal-Wallis, P = 0.017), with EGFR-mutant (285.3 \u00b1 180.1, n = 61) and KRAS-mutant tumors (284.6 \u00b1 227.9, n = 120) exhibiting higher \u03c9 than wild-type tumors (237.6 \u00b1 195.4, n = 311).')"

# Note: clinical_fstring has \u03c9 and \u00b1 which need careful handling
content = content.replace(old_clinical, clinical_fstring)
print('OK: Clinical severity paragraph')

with open('generate_manuscript_genome_biology.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nPatches applied successfully.')
