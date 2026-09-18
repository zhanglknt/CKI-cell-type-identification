"""Verify the regenerated SI docx (v49 fix round): section renumbering
(3.5-3.13 contiguous), version-tag removal, 3.12 wording sync, 3.13a MWU
descriptive note, 3,563 caliber, 1.7 LIHC sentence, prior content intact."""
import re
from docx import Document

doc = Document('results/CKI_Supplementary_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)

cells = []
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            cells.append(c.text)
cellfull = ' | '.join(cells)

checks = []

def chk(name, cond, detail=''):
    checks.append((name, 'PASS' if cond else 'FAIL', detail))

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

# 4. Table captions renumbered
for tag in ('3.11a', '3.11b', '3.11c', '3.12a', '3.12b',
            '3.13a', '3.13b', '3.13c', '3.13d'):
    chk(f'Table (Section {tag})', f'Table (Section {tag}).' in full)
chk('Sections 3.13b,c in-text ref', 'Tables (Sections 3.13b,c))' in full)
chk('Section 3.10 in-text ref (Note 2)', 'Section 3.10)' in full)

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

# 6. 3.13a MWU descriptive note
chk('MWU descriptive note',
    'pair-level Mann-Whitney P-values are descriptive only' in full
    and 'dyadic dependence between pairs sharing a sample' in full)

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
for tag in ('3.13e', '3.13f', '3.13g'):
    chk(f'Table (Section {tag})', f'Table (Section {tag}).' in full)
chk('3.13e table cells (LUAD row)',
    '-0.42 (1.8\u00d710\u207b\u00b2\u00b2)' in cellfull
    and '2.86 [2.410,3.451]' in cellfull)
chk('3.13e post-CC half ratios',
    '1.17 [0.968,1.412]' in cellfull and '1.82 [1.442,2.245]' in cellfull
    and '2.27 [1.944,2.668]' in cellfull and '1.74 [1.488,2.082]' in cellfull)
chk('3.13e caption post-CC P values',
    'KIRC P = 8.3 \u00d7 10\u207b\u00b9\u2077' in full
    and 'LIHC P = 3.9 \u00d7 10\u207b\u2076' in full
    and '8.9 \u00d7 10\u207b\u00b3\u2070' not in full)
chk('3.13f ANCOVA cells',
    '+16.83' in cellfull and '+0.0124' in cellfull)
chk('3.13g smoking model cells',
    '+13.64' in cellfull and '+13.87' in cellfull)
chk('3.13g caption chi2',
    '\u03c7\u00b2 = 30.3' in full and '2.7\u00d710\u207b\u2077' in full)
chk('3.13g ever-smoker pcts', '94.1%' in full and '62.7%' in full and '85.6%' in full)
chk('admix group means caption', '23,870' in full and '27,064' in full)

# 8. 4.3 sample counts (CC fix 09-19)
chk('4.3 counts 3,567',
    'LUAD (493 tumor + 76 normal)' in full and 'LUSC (534 + 58)' in full
    and 'LIHC (398 + 57)' in full and 'KIRC (750 + 82)' in full
    and 'BRCA (1,010 + 109)' in full and 'n = 3,567 samples' in full)
chk('4.3 attrition note', '29 expression-matrix samples were excluded' in full)
chk('no 3,563 residue', '3,563' not in full and '3,563' not in cellfull)
chk('no 3,596 residue', '3,596' not in full and '3,596' not in cellfull)

# 9. 1.7 LIHC mapping-sensitivity sentence
chk('1.7 LIHC mapping caveat',
    'mean NN/TT \u03c9 ratio is 1.10 under the linear mapping versus 1.31 under the softmax mapping' in full)

# 10. Prior-phase numbers intact
chk('Kang omega cal 0.963', '0.963' in full)
chk('Kang 0/30 wording', 'no pair exceeded its own null 95th percentile (0 of 30' in full)
chk('Wilson CI [0.000, 0.114]', '[0.000, 0.114]' in full)
chk('T1 FPR 28.6%', '28.6%' in full)
chk('T2 omega 90.9%', '90.9%' in full)
chk('marker Jaccard T3 1.41', '1.41 versus 1.80 for \u03c9' in full)
chk('choroid 137-fold', '137-fold' in full)
chk('LUAD NN/TT 2.46 CI (table)', '2.46 [2.13, 2.86]' in cellfull)
chk('CC post-fix ratios (table)',
    '1.88 [1.63, 2.16]' in cellfull and '1.71 [1.38, 2.09]' in cellfull
    and '1.10 [0.93, 1.29]' in cellfull and '1.57 [1.34, 1.84]' in cellfull)
chk('CC post-fix k_n mean ratios (table)',
    '3.29 [2.54, 4.35]' in cellfull and '1.35 [1.02, 1.88]' in cellfull)
chk('CC old table values gone',
    '1.13 [0.97, 1.34]' not in cellfull and '1.82 [1.46, 2.25]' not in cellfull
    and '1.90 [1.65, 2.17]' not in cellfull)
chk('LUAD means (table)',
    '115.4' in cellfull and '122.2' in cellfull and '136.9' in cellfull)
chk('Cox M1 (table)', '1.07 [0.88, 1.31]' in cellfull)
chk('Cox caption post-CC',
    'all P \u2265 0.07; k_f closest at P = 0.072' in full
    and 'all P \u2265 0.30' not in full)
chk('Kang table omega row', '0.963 [0.918, 0.998]' in cellfull)
chk('Ladder table T1 omega cell', '1.04 [0.97, 1.21] / 28.6%' in cellfull)

# 11. Note 9 sync + figure refs
chk('Note 9 sync sentence',
    'reported here as denominator-dominated vignettes (Supplementary Fig. 4b)' in full)
chk('Note 9 cross-organ Fig. 6', '(Table 2 / Fig. 6)' in full)
chk('Note 9 LIHC severity post-CC',
    '78.2 / 76.8 / 77.9 / 72.6' in full
    and 'JT 6.9 \u00d7 10\u207b\u00b9\u2075' in full
    and 'about 5-20' in full
    and 'G1 > G2 \u2248 G3 > G4' in full)
chk('Note 9 no stale severity',
    '82.4 / 74.7' not in full
    and 'JT 1.05' not in full
    and 'about 10-19' not in full
    and 'G1 > G2 \u2248 G3 \u2248 G4' not in full)
chk('Supp Table 3 Figure 7', '_fig6_clean.py (Figure 7)' in full)

# 12. Notes 1-15 unchanged
notes = re.findall(r'Supplementary Note (\d+):', full)
chk('Notes 1-15 count = 15', len(set(notes)) == 15,
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
    'Wilson intervals treat the 30 pairs as independent' in full)
chk('McNemar paired note', 'McNemar-style' in full)
chk('3.12b B=100/30/30 + noise note', 'resolves to 1/31' in full)
chk('3.12b class-composition note',
    'mix class composition with drift tier' in full)
chk('pooled-null note', 'pooled null' in full)
chk('3.13b wild-type definition',
    'Wild-type means wild-type for EGFR and KRAS' in full)
chk('3.13b pair-sharing note', 'pair-sharing dependence' in full)
chk('SI title matches MS',
    'CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics' in full
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
