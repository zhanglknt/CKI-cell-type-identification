"""Verify the regenerated SI docx + SI tables xlsx (v49.5): section renumbering
(3.5-3.13 contiguous), version-tag removal, 3.12 wording sync, 3.13a MWU
descriptive note, 3,567 caliber, 1.7 LIHC sentence, prior content intact.
v49.5: 15 embedded tables migrated to CKI_Supplementary_Tables_NC.xlsx as
Supplementary Table 5-19 (docx keeps zero tables); table-cell assertions read
the xlsx, caption assertions read the xlsx A1 cells."""
import re
from docx import Document
from openpyxl import load_workbook

doc = Document('results/CKI_Supplementary_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)

wb = load_workbook('results/CKI_Supplementary_Tables_NC.xlsx')
cells = []
caps = []
for sn in wb.sheetnames:
    ws = wb[sn]
    caps.append(str(ws['A1'].value))
    for row in ws.iter_rows(min_row=3, values_only=True):
        for v in row:
            cells.append('' if v is None else str(v))
cellfull = ' | '.join(cells)
capfull = '\n'.join(caps)

checks = []

def chk(name, cond, detail=''):
    checks.append((name, 'PASS' if cond else 'FAIL', detail))

# 0. v53 structural: docx has zero tables; xlsx has 19 sheets Table 1..19
chk('SI docx zero tables', len(doc.tables) == 0,
    f'found {len(doc.tables)}')
_expected_sheets = [f'Table {n}' for n in range(1, 20)]
chk('xlsx 19 sheets named Table 1..19', wb.sheetnames == _expected_sheets,
    f'found {wb.sheetnames}')
for _i, _n in enumerate(range(1, 20)):
    chk(f'xlsx A1 caption SuppTable {_n}',
        caps[_i].startswith(f'Supplementary Table {_n}: '))
chk('no old-style Table (Section refs in docx', 'Table (Section' not in full)

# 0b. v53 panel-fix round assertions
chk('k_n ratio parenthetical fixed (v53 R3-C2)',
    'which includes 1; high-purity-half' not in full
    and 'excludes 1 ex-CC, so the k_n elevation is nominally significant' in full)
chk('4.3 cohort hierarchy ex-CC (v53 R1-2)',
    'totaling n = 3,567 samples in the pair-level analysis before the barcode audit' in full
    and 'leaving 3,535 samples' in full)
chk('Note 1 DeLong methods (v53 R1-1)',
    'AUC interval methods (v52)' in full and 'DeLong' in full)
chk('Note 9 k_n-permutation floor (v53 R2-A1)',
    'k_n-permutation floor (v52' in full and '0.524 (95% CI [0.506, 0.541])' in full)
chk('Note 8 deconv fallback (v53 R3-C3)',
    'Reference-free composition fallback (v52)' in full and '0.934 LIHC, 0.964 KIRC' in full)
chk('GTEx liver direction + P caliber (v54 R1-N1/R3-m1)',
    'in liver the two medians coincide (ratio 1.03)' in full
    and 'heavier adjacent upper tail' in full
    and 'liver healthy is marginally above adjacent' not in full
    and 'P \u2248 0)' not in full)
chk('GTEx fold range + independence caveat (v54 R2-C2/R1-N2)',
    '2.0\u20132.8-fold higher' in full
    and 'Pair-level P values in this GTEx comparison treat pairs as independent' in full)
chk('Table 5 caption composition caliber ex-CC (v54 R2-m1)',
    'attenuation \u22120.9%' in capfull
    and 'cluster-bootstrap median \u22120.8% [95% CI \u22124.3%, +2.5%]' in capfull
    and 'median \u22121.3% [95% CI \u22124.8%, +2.0%]' not in capfull)

# 1. Renumbered headings present (no version tags)
chk('3.12 heading present',
    '3.12 Real-Data Neutral-Drift Calibration on Technical Replicates' in full)
chk('3.13 heading present',
    '3.13 Per-Sample Divergence and Group Statistics for TCGA' in full)
chk('3.10 mouse split-half heading',
    '3.10 Mouse Split-Half Re-calibration' in full)
chk('3.11 competitor heading', '3.11 Competitor Benchmark' in full)

# 2. Section-3 numbering contiguous 3.1-3.13
sec3 = [int(m.group(1)) for t in paras
        for m in [re.match(r'^3\.(\d+) \S', t)] if m]
chk('Section 3 contiguous 1-13', sorted(set(sec3)) == list(range(1, 14)),
    f'found {sorted(set(sec3))}')

# 3. Old numbers and version tags gone
chk('no 3.18-3.21 headings/refs',
    not re.search(r'3\.(18|19|20|21)\b', full))
chk('no (v44)/(v45)/(v49) tags',
    '(v44)' not in full and '(v45)' not in full and '(v49)' not in full)
chk('no inline v4x labels',
    'v44 update' not in full and 'v44 re-computation' not in full
    and 'v44 linear' not in full and '(v45;' not in full)

# 4. Prose pointers to renumbered tables (every table has >=1 pointer)
chk('SuppTable 5 prose pointer', 'choice drives no conclusion (Supplementary Table 5).' in full)
chk('SuppTable 6 prose pointer', '(Supplementary Table 6).' in full)
chk('SuppTable 7 prose pointer', 'Supplementary Table 7).' in full)
chk('SuppTable 8 prose pointer', '(Supplementary Table 8).' in full)
chk('SuppTable 9 prose pointer', 'given in Supplementary Table 9;' in full)
chk('SuppTable 10 prose pointer', 'given in Supplementary Table 10;' in full)
chk('SuppTables 11-17 group pointer', 'Supplementary Tables 11\u201317' in full)
chk('SuppTables 12 and 13 in-text ref', '; Supplementary Tables 12 and 13)' in full)
chk('SuppTables 15-17 in-text ref', 'Supplementary Tables 15\u201317)' in full)
chk('SuppTable 18 prose pointer', 'given in Supplementary Table 18.' in full)
chk('SuppTable 19 prose pointer', 'given in Supplementary Table 19.' in full)
chk('Section 3.10 in-text ref (Note 2)', 'Section 3.10)' in full)
chk('TOC SuppTable 5 entry', 'Supplementary Table 5: TCGA Linear-Normalization Robustness' in full)
chk('TOC SuppTable 19 entry', 'Supplementary Table 19: Brain min-cells Threshold Sensitivity' in full)

# 5. 3.12 wording sync (P0-1)
chk('T1 continuous-metrics framing',
    'lowest misreporting rate among the continuous divergence metrics' in full)
chk('Jaccard same-statistic admission',
    'T3\u2212T1 FPR gap 0.60 versus 0.56' in full
    and 'T3/T1 ratio 4.0 versus 3.0' in full)
chk('Jaccard claim restricted',
    'misreporting claim for \u03c9 is restricted to the continuous divergence metrics' in full)
chk('Jaccard per-class 10/10 admission',
    'below \u03c9 in 10 of 10 cell classes' in full)
chk('T2 Jaccard 74.7%', 'marker Jaccard was again lower at 74.7%' in full)
chk('T2 continuous-metrics framing',
    'misreported least among the continuous divergence metrics' in full)
chk('no "seven metrics except Jaccard" residue',
    'of the seven metrics except' not in full)
chk('Jaccard no-decomposition sentence',
    'as a single set-overlap statistic it offers no k_n/k_f decomposition' in full)
chk('transfer sentence qualified',
    'lowest misreporting among the continuous divergence metrics at every tier' in full)

# 6. 3.13a MWU descriptive note (now in SuppTable 11 caption)
chk('MWU descriptive note',
    'pair-level Mann-Whitney P-values are descriptive only' in capfull
    and 'dyadic dependence between pairs sharing a sample' in capfull)

# 7. EGFR terminology + B-group integration
chk('no baseline-driven/baseline-associated in SI',
    'baseline-driven' not in full and 'baseline-associated' not in full)
chk('no "available locally" in SI', 'available locally' not in full)
chk('3.13 EGFR admixture artefact',
    'the apparent EGFR elevation is an admixture artefact' in full)
chk('3.13 adjusted KRAS components',
    'k_f +0.012, P = 0.009; k_n -0.0004, P = 0.003' in full)
chk('3.13 joint smoking adjustment',
    'omega +13.6, P = 3.3 \u00d7 10\u207b\u2074' in full)
chk('purity/smoking block intro',
    'Purity and smoking covariate sensitivity' in full)
chk('3.13e table cells (LUAD row)',
    '-0.42 (1.8\u00d710\u207b\u00b2\u00b2)' in cellfull
    and '2.86 [2.410,3.451]' in cellfull)
chk('3.13e post-CC half ratios',
    '1.17 [0.968,1.412]' in cellfull and '1.82 [1.442,2.245]' in cellfull
    and '2.27 [1.944,2.668]' in cellfull and '1.74 [1.488,2.082]' in cellfull)
chk('3.13e caption post-CC P values',
    'KIRC P = 8.3 \u00d7 10\u207b\u00b9\u2077' in capfull
    and 'LIHC P = 3.9 \u00d7 10\u207b\u2076' in capfull
    and '8.9 \u00d7 10\u207b\u00b3\u2070' not in capfull)
chk('3.13f ANCOVA cells',
    '+16.83' in cellfull and '+0.0124' in cellfull)
chk('3.13g smoking model cells',
    '+13.64' in cellfull and '+13.87' in cellfull)
chk('3.13g caption chi2',
    '\u03c7\u00b2 = 30.3' in capfull and '2.7\u00d710\u207b\u2077' in capfull)
chk('3.13g ever-smoker pcts', '94.1%' in capfull and '62.7%' in capfull and '85.6%' in capfull)
chk('admix group means caption', '23,870' in capfull and '27,064' in capfull)

# 8. 4.3 sample counts (CC fix 09-19)
chk('4.3 counts 3,567',
    'LUAD (493 tumor + 76 normal)' in full and 'LUSC (534 + 58)' in full
    and 'LIHC (398 + 57)' in full and 'KIRC (750 + 82)' in full
    and 'BRCA (1,010 + 109)' in full and 'n = 3,567 samples' in full)
chk('4.3 attrition three-way note (v49.14)',
    '3 do not appear in the assembled pair table' in full
    and 'spans 3,593 unique barcodes' in full
    and '29 expression-matrix samples were excluded' not in full)
chk('no 3,563 residue', '3,563' not in full and '3,563' not in cellfull)
chk('no 3,596 stray residue (v53: Note x2 + 4.3 hierarchy + 5.12)',
    full.count('3,596') == 3 and 'of the 3,596 expression-matrix samples' in full
    and '3,596' not in cellfull)

# 9. 1.7 LIHC mapping-sensitivity sentence (in SuppTable 5 caption since v49.5)
chk('1.7 LIHC mapping caveat (v52)',
    'mapping-sensitive only through LIHC (four of five linear, five of five softmax)' in capfull)

# 10. Prior-phase numbers intact
chk('Kang omega cal 0.963', '0.963' in full)
chk('Kang 0/30 wording', 'no pair exceeded its own null 95th percentile (0 of 30' in full)
chk('Wilson CI [0.000, 0.114]', '[0.000, 0.114]' in cellfull)
chk('T1 FPR 28.6%', '28.6%' in full)
chk('T2 omega 90.9%', '90.9%' in full)
chk('marker Jaccard T3 1.41', '1.41 versus 1.80 for \u03c9' in full)
chk('choroid 137-fold', '137-fold' in full)
chk('LUAD NN/TT 2.46 CI (table)', '2.46 [2.13, 2.86]' in cellfull)
chk('CC post-fix ratios (table, ex-CC v52)',
    '1.88 [1.64, 2.15]' in cellfull and '1.71 [1.38, 2.09]' in cellfull
    and '1.11 [0.94, 1.30]' in cellfull and '1.57 [1.34, 1.81]' in cellfull)
chk('CC post-fix k_n mean ratios (table, ex-CC v52)',
    '2.55 [2.09, 3.31]' in cellfull and '1.34 [1.02, 1.89]' in cellfull)
chk('CC old table values gone',
    '1.13 [0.97, 1.34]' not in cellfull and '1.82 [1.46, 2.25]' not in cellfull
    and '1.90 [1.65, 2.17]' not in cellfull)
chk('LUAD means (table)',
    '115.4' in cellfull and '122.2' in cellfull and '136.9' in cellfull)
chk('Cox M1 (table, ex-CC v52)', '1.08 [0.88, 1.33]' in cellfull)
chk('Cox caption ex-CC (v52)',
    'ex-CC' in capfull and 'cox.zph' in capfull
    and 'all P \u2265 0.30' not in capfull)
chk('Kang table omega row', '0.963 [0.918, 0.998]' in cellfull)
chk('Ladder table T1 omega cell', '1.04 [0.97, 1.21] / 28.6%' in cellfull)

# 11. Note 9 sync + figure refs
chk('Note 9 sync sentence',
    'reported here as denominator-dominated vignettes (Supplementary Fig. 4b)' in full)
chk('Note 9 cross-organ Fig. 5', '(Table 1 / Fig. 5)' in full)
chk('Note 9 LIHC severity ex-CC (v52)',
    '78.8 / 75.8 / 77.6 / 72.3' in cellfull
    and 'JT 8.4 \u00d7 10\u207b\u00b9\u00b2' in cellfull
    and 'about 5-20' in full
    and 'G1 > G2 \u2248 G3 > G4' in cellfull)
chk('Note 9 no stale severity',
    '82.4 / 74.7' not in cellfull
    and 'JT 1.05' not in cellfull
    and 'about 10-19' not in full
    and 'G1 > G2 \u2248 G3 \u2248 G4' not in cellfull)
chk('Supp Table 3 Figure 6', '_fig6_clean.py (Figure 6)' in full)

# 12. Notes 1-16 (v50: +Note 16 microglia validation)
notes = re.findall(r'Supplementary Note (\d+):', full)
chk('Notes 1-16 count = 16 (v50)', len(set(notes)) == 16,
    f'found {sorted(set(map(int, notes)))}')

# 12b. xv-text round: NEW-1 + P2 clarifications in SI
chk('NEW-1 linear authoritative',
    'which is the authoritative caliber throughout' in full
    and 'The authoritative TCGA pipeline' not in full
    and 'softmax-caliber values are archived here as a sensitivity analysis' in full)
chk('3.13 EGFR k_n NS framing',
    'no significant k_n difference (WT > EGFR' in full
    and 'is visible only in the k_n baseline' not in full)
chk('pair-table filename + rebuild pointer',
    'results/tcga_linear_norm_v44_all_pairs.csv' in full
    and 'not archived as a separate file' in full)
chk('Wilson CI clustering note',
    'Wilson intervals treat the 30 pairs as independent' in capfull)
chk('McNemar paired note', 'McNemar-style' in capfull)
chk('3.12b B=100/30/30 + noise note', 'resolves to 1/31' in capfull)
chk('3.12b class-composition note',
    'mix class composition with drift tier' in capfull)
chk('pooled-null note', 'pooled null' in full)
chk('3.13b wild-type definition',
    'Wild-type means wild-type for EGFR and KRAS' in capfull)
chk('3.13b pair-sharing note', 'pair-sharing dependence' in capfull)
chk('SI title matches MS (v52)',
    'CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases' in full
    and 'functional cell-type divergence in single-cell transcriptomics' not in full)
chk('Data 1 naming unified',
    'Complete Analysis Script Index' not in full
    and full.count('Supplementary Data 1: Analysis Script Index') >= 1)
chk('SI affiliation postcodes',
    'Beijing 102206, China' in full and 'Chengdu 610052, China' in full)
chk('3.13 short heading ref',
    'A pan-cancer map of tissue-level divergence in tumors' in full
    and 'tissue-level functional divergence in tumors' not in full)

# 12c. Three-in-one round: KRAS magnitude + Hallmark in SI
chk('3.13 KRAS magnitude restored',
    'contributed ~84% of the log-\u03c9 gap' in full
    and 'Dunn P = 0.097' in full)
chk('3.13 Hallmark paragraph',
    'Panel semantics and composition correction for k_f' in full
    and 'Estrogen Response Late, q = 0.24' in full)
chk('3.13 kf_composition output listed',
    full.count('results/nc49_tcga_kf_composition.csv') >= 2
    and 'notebooks/nc49_tcga_kf_composition.py' in full)

# 13. No TODO residue
chk('no TODO in SI', 'TODO' not in full and 'TODO' not in cellfull)

print('===== SI checks =====')
nfail = 0
for name, status, detail in checks:
    print(f'[{status}] {name} {detail}')
    if status == 'FAIL':
        nfail += 1
print(f'TOTAL: {len(checks)} checks, {nfail} failures')
raise SystemExit(1 if nfail else 0)
