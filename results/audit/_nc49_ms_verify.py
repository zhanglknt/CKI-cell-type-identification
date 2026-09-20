"""Verify regenerated MS docx (v49 fix round): blind-review text fixes,
Section 3.12/3.13 references, 3,563 caliber, TODO-nc49-fix markers (3),
Abstract word count, and prior-phase content intact."""
import re
from docx import Document

doc = Document('results/CKI_Manuscript_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)

checks = []

def chk(name, cond, detail=''):
    checks.append((name, 'PASS' if cond else 'FAIL', detail))

# 1. TODO state: zero TODO of any kind
chk('TODO-nc49-fix count == 0', full.count('TODO-nc49-fix') == 0,
    f'found {full.count("TODO-nc49-fix")}')
chk('no TODO-nc49-drift residue', 'TODO-nc49-drift' not in full)
chk('no TODO at all', 'TODO' not in full)

# 1b. baseline-* phrasing fully removed
chk('no baseline-driven/baseline-associated',
    'baseline-driven' not in full and 'baseline-associated' not in full)
chk('no "available locally"', 'available locally' not in full)
chk('no stale 85% decomposition (0.097 restored in new sentence)',
    '85% of the log-scale' not in full)

# 2. Section references (SI renumbered 3.20->3.12, 3.21->3.13)
chk('Results Section 3.12 ref',
    'audit trails in the companion repository; Section 3.12 of the Supplementary Information' in full)
chk('Methods Section 3.12 ref',
    'Section 3.12 of the Supplementary Information reports the full audit of design, diagnostics, and per-class results' in full)
chk('Section 3.12 referenced 3x (Results, Methods, class-composition note)',
    full.count('Section 3.12 of the Supplementary Information') == 3,
    f'found {full.count("Section 3.12 of the Supplementary Information")}')
chk('MWU descriptive -> Section 3.13',
    'reported as descriptive only in Section 3.13 of the Supplementary Information' in full)
chk('no stale Section 3.20/3.21 refs',
    'Section 3.20' not in full and 'Section 3.21' not in full)

# 3. P0-1 qualification of misreporting claims
chk('T1 qualified (continuous metrics)',
    'lowest misreporting rate among the four continuous divergence metrics' in full)
chk('marker Jaccard T1 19.9% admitted', 'T1 FPR 19.9%' in full)
chk('Jaccard below omega 10/10 admitted', 'below \u03c9 in all ten cell classes' in full)
chk('same-statistic frontier admitted',
    'T3\u2212T1 FPR gap 0.60 versus 0.56' in full and 'T3/T1 ratio 4.0 versus 3.0' in full)
chk('final claim qualified',
    'lowest misreporting among the continuous divergence metrics' in full)
chk('Discussion decision-rules qualified',
    'marker Jaccard was more conservative still but offers no k_n/k_f decomposition' in full)
chk('no unqualified "misreported least of seven"',
    'least of seven metrics' not in full and 'of the seven metrics except' not in full)

# 4. Abstract (drift sentence, word count <= 200)
abs_paras = [t for t in paras if 'Inspired by the Ka/Ks ratio' in t]
chk('Abstract drift sentence present', len(abs_paras) == 1)
if abs_paras:
    wc = len(abs_paras[0].split())
    chk('Abstract word count <= 200', wc <= 200, f'{wc} words')
chk('Abstract real-data calibration numbers',
    bool(abs_paras) and '28.6% versus 45.2% for raw JS' in abs_paras[0]
    and 'specificity decays with group size' in abs_paras[0])
chk('Abstract 3,567', bool(abs_paras) and '3,567' in abs_paras[0])
chk('Abstract new ratio range', bool(abs_paras) and 'ratio 1.10\u20132.46' in abs_paras[0])
chk('Abstract new k_n range', bool(abs_paras) and '1.3\u20133.3-fold elevated housekeeping baseline' in abs_paras[0])

# 5. Sample caliber 3,567 everywhere (CC fix 09-19)
chk('3,567 present', '3,567' in full)
chk('no 3,563 residue', '3,563' not in full)
chk('no 3,596 residue', '3,596' not in full)
chk('Methods per-cancer counts',
    'LUAD: 493 tumor + 76 normal' in full and 'LUSC: 534 tumor + 58 normal' in full
    and 'LIHC: 398 tumor + 57 normal' in full and 'KIRC: 750 tumor + 82 normal' in full
    and 'BRCA: 1010 tumor + 109 normal' in full)
chk('attrition sentence', '29 expression-matrix samples were excluded' in full)
chk('CC ratio list new values',
    'KIRC 1.88 (1.63\u20132.16)' in full and 'LUSC 1.71 (1.38\u20132.09)' in full
    and 'BRCA 1.57 (1.34\u20131.84)' in full and 'LIHC 1.10 (0.93\u20131.29)' in full)
chk('CC old ratio list gone',
    'KIRC 1.90' not in full and 'LUSC 1.82' not in full
    and 'LIHC 1.13 (0.97' not in full and '1.35\u20131.83' not in full)
chk('k_n mechanism sentence new range',
    'TT k_n exceeded NN k_n by 1.3\u20133.3-fold (mean ratios' in full
    and 'KIRC 3.29 [2.54, 4.35]' in full and 'LIHC 1.35 [1.02, 1.88]' in full)
chk('k_n mechanism old examples gone',
    '2.1\u20133.6-fold at the median' not in full
    and 'KIRC 3.21 [2.51, 4.28]' not in full and 'LIHC 1.41 [1.08, 1.98]' not in full)
chk('Discussion range updated',
    'mean NN/TT 1.10\u20132.46' in full and 'mean NN/TT 1.13\u20132.46' not in full)

# 6. R1-P1-3 / R3-P1-1: MWU deleted from main text, CI presentation
chk('pair-level MWU P deleted from main claims',
    'pair-level Mann-Whitney P-values, which ignore dyadic dependence between pairs' in full)
chk('LIHC mapping-sensitivity honest',
    'quantitatively weaker under the linear mapping (NN/TT mean ratio 1.10 versus 1.31' in full)
chk('softmax demoted to SI sensitivity',
    'softmax-caliber values are archived as a sensitivity analysis in Section 1.7' in full)

# 7. R2-P0/P1: purity + smoking adjustment integrated
chk('purity adj KRAS omega +16.8',
    '\u0394\u03c9 +16.8, P = 4.0 \u00d7 10\u207b\u2076' in full)
chk('purity adj k_f/k_n significant',
    '\u0394k_f +0.012, P = 0.009' in full and '\u0394k_n \u22120.0004, P = 0.003' in full)
chk('EGFR null after purity adj', 'all P > 0.4' in full)
chk('EGFR admixture highest', 'highest in EGFR-mutant tumors (Kruskal-Wallis P = 0.003)' in full)
chk('smoking enrichment 94/63/86',
    '94% versus 63% in EGFR-mutant and 86% in wild-type tumors' in full)
chk('smoking chi2', '\u03c7\u00b2 = 30.3, P = 2.7 \u00d7 10\u207b\u2077' in full)
chk('smoking joint model +13.6',
    '+13.6, P = 3.3 \u00d7 10\u207b\u2074 in the joint model' in full)
chk('smoking alone +13.9', '\u0394\u03c9 +13.9, P = 5.9 \u00d7 10\u207b\u2074 with smoking alone' in full)
chk('purity proxy limitation (Results)',
    'monotonically equivalent to published ESTIMATE purity' in full)
chk('pack-years limitation', 'pack-years data were too sparse to model (smoking status covered 427 of 492 tumors, 87%)' in full)
chk('batch/center limitation', 'tissue-source site and processing batch' in full)
chk('GTEx healthy-reference limitation', 'GTEx' in full)
chk('Discussion epidemiology sentence',
    'unlikely to be a smoking-field effect' in full)

# 7b. Pan-cancer purity sensitivity (Results para 3)
chk('k_n admix correlation range', 'r = \u22120.23 to \u22120.42' in full)
chk('high-purity half LUAD', 'LUAD 2.46 \u2192 2.86, 95% CI 2.41\u20133.45' in full)
chk('high-purity half LIHC caliber kept',
    'LIHC 1.10 \u2192 1.17, its CI still including 1' in full)
chk('reversal not admixture artefact',
    'not an artefact of stromal or immune admixture' in full)

# 7c. Methods covariate blocks
chk('Methods ESTIMATE block',
    'official ESTIMATE gene sets (141 stromal and 141 immune genes)' in full
    and '45,504 expressed genes' in full)
chk('Methods cBioPortal smoking block',
    'study luad_tcga, patient-level clinical data' in full
    and 'smoking status available for 508' in full
    and '427 of 492 tumors with known smoking status, 87%' in full)
chk('Methods scripts extended',
    'notebooks/nc49_tcga_purity.py' in full
    and 'notebooks/nc49_tcga_luad_smoking.py' in full
    and 'results/nc49_tcga_admix_scores.csv' in full)

# 7d. Abstract / Intro / Fig.5 sync
chk('Abstract KRAS dual-component adjusted',
    'both survived purity and smoking adjustment' in full)
chk('Abstract EGFR admixture',
    'apparent EGFR-mutant association was explained by stromal/immune admixture' in full)
chk('Intro EGFR dissolved',
    'apparent EGFR association dissolved under purity adjustment' in full)
chk('Fig 5 legend NEW-3 fix',
    'apparent EGFR elevation dissolved under purity adjustment (all adjusted P > 0.4)' in full)
chk('Fig 5 legend old EGFR-baseline gone',
    'the EGFR association appears only in the k_n baseline' not in full)

# 7e. xv-text round: P2 clarifications in MS
chk('B=30 MC noise note', 'resolves to 1/31' in full)
chk('tier class-composition note', 'mix class composition with drift tier' in full)
chk('per-tumor cross-group pairing note',
    'not formed from disjoint pair sets' in full)
chk('wild-type label qualified', 'wild-type for EGFR and KRAS' in full)
chk('seeded subsampling MC note',
    'Monte-Carlo error of roughly 0.01\u20130.02 ratio units' in full)
chk('TCGA fixed-panel caveat',
    'fixed-panel ablation of the per-pair top-200 selection was run for the brain pipeline' in full)
chk('Fig 4a dual-axis note', 'The two axes use independent scales' in full)
chk('affiliation postcodes',
    'Beijing 102206, China' in full and 'Chengdu 610052, China' in full)

# 7f. R4-P2-4 subtitle <= 60 chars
chk('short Result 5 heading',
    'A pan-cancer map of tissue-level divergence in tumors' in full
    and 'A pan-cancer map of tissue-level functional divergence in tumors' not in full)

# 7g. Three-in-one round: KRAS magnitude + Hallmark
chk('KRAS magnitude sentence restored',
    'The elevation was carried predominantly by the lower baseline (k_n contributed ~84% of the log-\u03c9 gap; the unadjusted k_f contrast was non-significant, Dunn P = 0.097)' in full)
chk('KRAS magnitude coexists with adjusted',
    '\u0394k_f +0.012, P = 0.009' in full)
chk('Hallmark enrichment sentence',
    'no program surviving multiple-testing correction (all q \u2265 0.24)' in full)
chk('Hallmark distributed-signal framing',
    'distributed identity-gene signal rather than a single-pathway artefact' in full)
chk('k_f composition regression sentence',
    'retained the TT \u2265 NN k_f ordering in all five cancer types' in full)
chk('Data availability Enrichr mirror',
    'accessed via the Enrichr gene-set library (MSigDB_Hallmark_2020' in full)

# 8. R1 P2-4: Kang k_f increment honest
chk('Kang k_f 0/30 parenthetical',
    'k_f alone was likewise 0 of 30' in full)

# 9. R4-P1-4: no Additional file 2
chk('no Additional file 2', 'Additional file 2' not in full)
chk('SI availability rewritten',
    'Supplementary Information is available for this paper' in full)

# 10. Prior-phase content intact
chk('severity -> Note 9 + Supp Fig 4b',
    'reported as denominator-dominated vignettes in the Supplementary Information (Supplementary Note 9; Supplementary Fig. 4b)' in full)
chk('marker Jaccard 1.41 (Results)', 'T3 calibration ratio 1.41 versus 1.80' in full)
chk('no leftover 1.40 versus 1.80', '1.40 versus 1.80' not in full)
chk('Result 5 TCGA title',
    'A pan-cancer map of tissue-level divergence in tumors' in full)
chk('Figure 4 legend (TCGA)', 'Figure 4. Pan-cancer tissue-level divergence in tumors' in full)
chk('Cox limitation sentence', 'Cox hazard ratio per SD 1.07, 95% CI 0.88\u20131.31, P = 0.48' in full)
chk('drift Results heading', 'Real-data neutral-drift calibration on technical replicates' in full)
chk('Kang Wilson CI', 'Wilson 95% CI [0.000, 0.114]' in full)
chk('Kang-brain size reconciliation',
    'consistent under the size-dependence of the technical component' in full)

# 11. Figure legends order 1-6 (v49.6: Fig2+Fig3 merged, 3-7 renumbered)
figs = [t[:12] for t in paras if re.match(r'^Figure \d\.', t)]
fignums = [int(re.match(r'^Figure (\d)\.', t).group(1)) for t in paras if re.match(r'^Figure \d\.', t)]
chk('main figure legends 1-6 in order', fignums == list(range(1, 7)), str(figs))

# 11b. v49.7: Fig 2e = change-detection ROC
chk('Fig 2 legend new scope',
    'functional-change detection in the ground-truth simulation' in full)
chk('Fig 2e legend change-detection ROC',
    'ROC curves for discriminating injected functional signal' in full
    and 'AUC = 0.80' in full and 'AUC = 0.91 (rank 1/6)' in full)
chk('Fig 2e legend old classification ROC gone',
    'ROC curves for cell-type classification across five metrics on Tabula Sapiens data' not in full)
chk('Result 3 anchor narrowed to Fig. 2d',
    'human column) (Fig. 2d).' in full and 'human column) (Fig. 2d, e).' not in full)
chk('Result 3b AUC sentence cites Fig. 2e',
    'from neutral perturbations (Fig. 2e; AUC = 0.80' in full)
chk('Result 3b background2 cites Fig. 2e',
    '= 0.859 (Fig. 2e), with the same metric ranking' in full)

# 11c. v49.8: classification benchmark fully cut; main Table 2 renumbered to Table 1
chk('classification benchmark paragraph removed',
    'cell-type classification performance' not in full
    and 'ranked 5th of 5 methods' not in full and '0.680' not in full)
chk('Fig 2 legend Table 1 pointer removed',
    'Cell-type classification performance on Tabula Sapiens is reported in Table 1' not in full)
chk('Methods classification ROC-AUC removed',
    'cell-type classification ROC-AUC' not in full)
chk('main-text Table 2 retired',
    not re.search(r'(?<!Supplementary )Table 2', full))
chk('cross-organ Table 1 citations',
    '(Fig. 5; Table 1; Supplementary Fig. 5)' in full
    and 'upper block of Table 1' in full and 'lower block of Table 1' in full)

# 12. Fig 3 legend honest framing
chk('Fig 3 legend Jaccard admission',
    'marker Jaccard is lower still on the false-positive statistic (T1 19.9%, T2 74.7%)' in full)

# 13. Citation order (v49.5 refs renumber): superscript citation groups between
# the Abstract heading and the References heading must first-appear in strict
# 1..56 order; every reference must be cited (no orphans); References list must
# be numbered 1..56 with the v49.5 reordered entries at their new positions.
def _cite_expand(s):
    out = []
    for part in s.split(','):
        part = part.strip()
        m = re.match(r'^(\d+)\s*[–\-]\s*(\d+)$', part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.extend(range(a, b + 1))
        elif part.isdigit():
            out.append(int(part))
    return out

_abs_i = next(i for i, t in enumerate(paras) if t.strip() == 'Abstract')
_ref_i = next(i for i, t in enumerate(paras) if t.strip() == 'References')
_sup_groups = []
for _p in doc.paragraphs[_abs_i + 1:_ref_i]:
    for _r in _p.runs:
        if _r.font.superscript:
            _sup_groups.append(_cite_expand(_r.text))
chk('superscript citation group count == 76', len(_sup_groups) == 76,
    f'found {len(_sup_groups)}')
_first, _seen = [], set()
for _g in _sup_groups:
    for _n in _g:
        if _n not in _seen:
            _seen.add(_n)
            _first.append(_n)
chk('citation first-appearance order is 1..57 monotonic',
    _first == list(range(1, 58)),
    'seq head: ' + str(_first[:18]))
chk('no orphan references (all 57 cited in text)', len(_seen) == 57,
    f'cited: {len(_seen)}')

_refs = [t for t in paras[_ref_i + 1:] if re.match(r'^\d+\.\s', t)]
chk('57 reference entries', len(_refs) == 57, f'found {len(_refs)}')
chk('references numbered 1..57 sequentially',
    [int(re.match(r'^(\d+)\.', t).group(1)) for t in _refs] == list(range(1, 58)))
if len(_refs) == 57:
    chk('ref 15 = Liberzon MSigDB (moved from old 56)', _refs[14].startswith('15. Liberzon'))
    chk('ref 33 = Raj fixed title', _refs[32].startswith('33. Raj') and
        'stochastic gene expression and its consequences.' in _refs[32] and
        'variation and its consequences on individual' not in _refs[32])
    chk('ref 34 = McDonald-Kreitman (new in v49.10)',
        _refs[33].startswith('34. McDonald') and 'Adh locus in Drosophila' in _refs[33])
    chk('ref 36 = Jiang CACIMAR completed title', _refs[35].startswith('36. Jiang') and
        'using single-cell RNA sequencing data' in _refs[35])
    chk('ref 46 = Hao 2021 pages .e29', _refs[45].startswith('46. Hao') and
        '3573–3587.e29' in _refs[45])
    chk('ref 48 = CZI CELLxGENE (moved from old 55)',
        _refs[47].startswith('48. CZI Cell Science Program') and 'CZ CELLxGENE Discover' in _refs[47])
    chk('ref 52/53 = Perou/Parker (moved from old 16/17)',
        _refs[51].startswith('52. Perou') and _refs[52].startswith('53. Parker'))
    chk('ref 54 = Edmondson (moved from old 15)', _refs[53].startswith('54. Edmondson'))
    chk('ref 57 = Efron bootstrap (moved from old 54)', _refs[56].startswith('57. Efron'))
    chk('refs 49-51 = Weinstein/Colaprico/Cerami (moved from old 49-51)',
        _refs[48].startswith('49. Weinstein') and _refs[49].startswith('50. Colaprico')
        and _refs[50].startswith('51. Cerami'))

print('===== MS checks =====')
nfail = 0
for name, status, detail in checks:
    print(f'[{status}] {name} {detail}')
    if status == 'FAIL':
        nfail += 1
print(f'TOTAL: {len(checks)} checks, {nfail} failures')
