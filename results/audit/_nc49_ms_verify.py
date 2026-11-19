"""Verify regenerated MS docx (v49 fix round): blind-review text fixes,
Section 3.12/3.13 references, 3,563 caliber, TODO-nc49-fix markers (3),
Abstract word count, and prior-phase content intact."""
import re
from docx import Document

doc = Document('results/CKI_Manuscript_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)
sfull = open('results/CKI_Supplementary_NC_fulltext.txt', encoding='utf-8').read()

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
chk('Results Section 3.12 ref (v51 short form)',
    'relative-calibration advantage' in full and 'Section 3.12' in full)
chk('Methods Section 3.12 ref (v51)',
    'per-class values in Section 3.12' in full)
chk('Section 3.12 referenced 4x (nc82: wild-cluster bootstrap + PSD pointers added)',
    full.count('Section 3.12') == 4,
    f'found {full.count("Section 3.12")}')
chk('MWU deleted from main claims; permutation -> Section 3.13 (v51)',
    'label-permutation confirmed)' in full
    and 'per-tumor Mann-Whitney' not in full)
chk('no stale Section 3.20/3.21 refs',
    'Section 3.20' not in full and 'Section 3.21' not in full)

# 3. P0-1 qualification of misreporting claims
chk('T1 qualified (continuous metrics, v51)',
    'had the lowest exceedance among continuous metrics' in full)
chk('marker Jaccard T1 19.9% admitted (v51: MS legend + SI; nc79 caption slim)',
    'marker Jaccard is lower still on the false-positive statistic' in sfull and 'T1 FPR 19.9%' in sfull)
chk('Jaccard weakest on genuine divergence admitted (v51)',
    'weakest to real regional divergence' in sfull)
chk('same-statistic frontier admitted (v50: SI)',
    'T3\u2212T1 FPR gap 0.60 versus 0.56' in sfull and 'T3/T1 ratio 4.0 versus 3.0' in sfull)
chk('final claim qualified (v50)',
    'shows the lowest exceedance among the continuous divergence metrics' in sfull)
chk('Discussion decision-rules qualified (v50)',
    'offers no k_n/k_f decomposition' in sfull)
chk('no unqualified "misreported least of seven"',
    'least of seven metrics' not in full and 'of the seven metrics except' not in full)

# 4. Abstract (drift sentence, word count <= 150; nc79: NC article limit)
abs_paras = [t for t in paras if 'Standard metrics confound cell-state shifts' in t]
chk('Abstract drift sentence present', len(abs_paras) == 1)
if abs_paras:
    wc = len(abs_paras[0].split())
    chk('Abstract word count <= 150 (nc79)', wc <= 150, f'{wc} words')
chk('Abstract real-data calibration sentence (nc80 M-C: scoped log-MAD)',
    bool(abs_paras) and 'with the tightest technical-replicate dispersion among seven metrics' in abs_paras[0]
    and 'log-scale MAD 0.113' in abs_paras[0]
    and 'most reproducible' not in abs_paras[0])
chk('Abstract null-free calibration claim only (nc79 panel P0-2: no error-rate claim)',
    bool(abs_paras) and 'zero false reports' not in abs_paras[0]
    and 'shallowest' not in abs_paras[0])
chk('Abstract Ka/Ks heuristic wording (nc82 P2-24: heuristic in first sentence)',
    bool(abs_paras) and 'Adapting the Ka/Ks heuristic' in abs_paras[0])
chk('Abstract background-specific trade-off (nc82 P1-6: sensitivity vs specificity)',
    bool(abs_paras) and 'background-specific precision advantage bought with sensitivity' in abs_paras[0]
    and '35\u201366% vs 97\u2013100% of injected 10x modules' in abs_paras[0])
chk('Abstract 3,535 (ex-CC, v52)', bool(abs_paras) and '3,535' in abs_paras[0])
chk('Abstract pan-cancer pattern (nc79)',
    bool(abs_paras) and 'tumor\u2013tumor pairs show higher housekeeping divergence than normal\u2013normal pairs in all five (1.3\u20133.3-fold)' in abs_paras[0])
chk('Abstract k_n-driven attribution (nc80 plan b)',
    bool(abs_paras) and 'copy-number instability is associated with at most 56% (95% CI 46\u201366%) of that k_n gap' in abs_paras[0])

# 5. Sample caliber 3,535 ex-CC everywhere (v52: ex-CC default)
chk('3,535 present (ex-CC, v52)', '3,535' in full)
chk('no 3,563 residue', '3,563' not in full)
chk('no 3,596 stray residue (v53: MS clean; SI x3)',
    '3,596' not in full and sfull.count('3,596') == 3)
chk('Methods per-cancer counts (v51)',
    'LUAD 493 tumor + 76 normal; LUSC 534 + 58; LIHC 398 + 57; KIRC 750 + 82; BRCA 1,010 + 109' in full)
# 5b. v53 panel-fix round assertions
chk('Methods ex-CC arithmetic parenthetical (v53)',
    '3,567 samples, of which 3,535 enter the pair-level analysis' in full)
chk('Methods pair table ex-CC 34,828 (v53)',
    '34,828 pairs after dropping the 478 pairs' in full)
chk('Discussion permute-k_n full-inventory qualifier (v53)',
    '5,151 full-inventory human pairs' in full)
chk('Table 1 legend present (v53 R5-M1)',
    'Table 1. Cross-organ conservation ranking by cell type' in full)
chk('Supplementary Fig. 4 legend present (nc72: 3->4 first-citation order; legends in SI)',
    'Supplementary Fig. 4. Human-brain sanity check on the microglia supercluster' in sfull)
chk('quality-adjustment attribution (class, region) only (v53 R1-5)',
    '(class, region)-level adjustment for detection depth' in full
    and '(class, library)- and (class, region)-level adjustment' not in full)
chk('deconv fallback cited in Results (v53 R3-C3; v54 rho referent R2-m2)',
    'reference-free composition check: non-parenchymal fraction versus k_n' in full
    and 'Supplementary Note 8' in full)
chk('Fig 4a k_f orientation explicit (v54 R3-m2)',
    'while the NN/TT ratio of k_f does not' in full
    and 'while k_f does not' not in full)
chk('GTEx tumor fold range 2.0-2.8 (v54 R2-C2)',
    '2.0\u20132.8-fold higher' in full and '2.0\u20132.7-fold higher' not in full)
chk('38% misreports tagged simulation (v54 R2-C4)',
    '(simulation) k_f misreports 38% of neutral pairs' in full)
chk('attrition three-way arithmetic (v51: SI)',
    '3 do not appear in the assembled pair table' in sfull
    and 'spans 3,593 unique barcodes' in sfull
    and '29 expression-matrix samples were excluded' not in full)
chk('CC ratio list new values (v52: MS ratios, CIs in SI)',
    'mean NN/TT \u03c9: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11' in full)
chk('CC old ratio list gone',
    'KIRC 1.90' not in full and 'LUSC 1.82' not in full
    and 'LIHC 1.13 (0.97' not in full and '1.35\u20131.83' not in full)
chk('k_n mechanism sentence new range (v51: MS range; per-cancer CIs in SI Table 11)',
    'TT k_n exceeded NN k_n by 1.3\u20133.3-fold in every cancer type' in full)
chk('k_n mechanism old examples gone',
    '2.1\u20133.6-fold at the median' not in full
    and 'KIRC 3.21 [2.51, 4.28]' not in full and 'LIHC 1.41 [1.08, 1.98]' not in full)
chk('Discussion range updated (v52)',
    'mean NN/TT 1.11\u20132.46' in full and 'mean NN/TT 1.10\u20132.46' not in full)

# 6. R1-P1-3 / R3-P1-1: MWU deleted from main text, CI presentation
chk('pair-level MWU P deleted from main claims (v51)',
    'Dunn\u2013Holm P \u2264 0.008 for both KRAS contrasts' in full
    and 'label-permutation confirmed)' in full)
chk('LIHC mapping-sensitivity honest (v52)',
    'linear 1.11 versus softmax 1.29; Supplementary Table 8a' in full)
chk('softmax demoted to SI sensitivity (v51; nc79 wording)',
    'Under the authoritative linear probability mapping' in full
    and 'Section 1.7' in full and 'softmax-caliber values are archived here as a sensitivity analysis' in sfull)

# 7. R2-P0/P1: purity + smoking adjustment integrated
chk('purity adj KRAS omega +16.8 (v50: SI 3.13)',
    '\u0394\u03c9 +16.8, P = 4.0 \u00d7 10\u207b\u2076' in sfull)
chk('purity adj k_f/k_n significant (v50: SI 3.13)',
    '\u0394k_f +0.012, P = 0.009' in sfull and '\u0394k_n \u22120.0004, P = 0.003' in sfull)
chk('EGFR null after purity adj (nc82: carried by SI 3.13)',
    'disappear entirely under purity adjustment (all P > 0.4)' in sfull)
chk('EGFR admixture highest (v50: SI 3.13)',
    'EGFR-mutant tumors carry the highest admixture scores (Kruskal-Wallis P = 0.003)' in sfull)
chk('smoking enrichment 94/63/86 (v50: SI 3.13)',
    '94% versus 63% EGFR-mutant and 86% wild-type' in sfull)
chk('smoking chi2 (v50: SI 3.13)', '\u03c7\u00b2 = 30.3, P = 2.7 \u00d7 10\u207b\u2077' in sfull)
chk('smoking three-model adjustment (v52: MS headline; SI models)',
    'smoking, TP53 and proliferation' in full and '+13.3' in sfull
    and '+13.6' in sfull and '+13.9' in sfull)
chk('smoking alone +13.9 (v50: SI 3.13)', '+13.9' in sfull)
chk('purity proxy limitation (v51: SI)',
    'monotonically equivalent to published ESTIMATE purity' in sfull)
chk('pack-years sparsity documented (v51: MS note; SI detail)',
    'pack-years reported descriptively' in full and 'pack-years for 356' in sfull)
chk('TCGA design limitation (v52)', 'the TCGA analysis is limited to bulk resolution' in full)
chk('GTEx healthy-reference analysis (v52 wording)',
    'adjacent non-tumor resembles healthy tissue' in full and 'kidney is an exception' in full)
chk('Discussion epidemiology sentence (nc82: adjustment retained, new wording)',
    'survives adjustment for purity (adjusted log-\u03c9 ratio 1.19' in full)

# 7b. Pan-cancer purity sensitivity (Results para 3)
chk('k_n admix correlation range (v51r2: SI Note 8)', 'r = \u22120.23 to \u22120.42' in sfull)
chk('high-purity half LUAD (v51: SI Note 8)', 'LUAD 2.46 \u2192 2.86' in sfull)
chk('high-purity half LIHC caliber kept (v52: MS + SI 3.13)',
    'high-purity-half comparisons increased the NN/TT ratio in all five' in full
    and 'high-purity-half 1.17 full-cohort (95% CI [0.97, 1.41]) versus 1.19 excluding CC' in sfull)
chk('reversal not admixture artefact (nc80 scoped)',
    'admixture neither uniformly weakens nor uniformly creates the elevation' in full)

# 7c. Methods covariate blocks
chk('Methods ESTIMATE block (v51: MS count; SI gene sets)',
    'official ESTIMATE gene sets (141 stromal and 141 immune genes)' in sfull
    and '45,504 expressed genes' in full)
chk('Methods cBioPortal smoking block (v51: SI)',
    'study luad_tcga, patient-level clinical data' in sfull
    and 'smoking status available for 508' in sfull
    and '427 of 492 tumors with known smoking status, 87%' in sfull)
chk('Methods scripts extended (v51: SI)',
    'notebooks/nc49_tcga_purity.py' in sfull
    and 'notebooks/nc49_tcga_luad_smoking.py' in sfull
    and 'results/nc49_tcga_admix_scores.csv' in sfull)

# 7d. Abstract / Intro / Fig.5 sync
chk('KRAS dual-component k_f contrast (nc82: detail moved to SI 3.13)',
    'KRAS versus EGFR under k_f alone, P = 0.015' in full)
chk('KRAS group-level scoping (nc82 P1-12)',
    'group-level association rather than a confirmed driver effect' in full
    and 'fixed gene panel (\u0394\u03c9 +2.6, P = 0.089)' in full)
chk('KRAS purity adjustment retained in MS (nc82)',
    'survives adjustment for purity (adjusted log-\u03c9 ratio 1.19, 95% CI [1.12, 1.26])' in full)
chk('EGFR admixture resolution carried by SI 3.13 (nc82)',
    'the EGFR-wild-type differences disappear entirely under purity adjustment' in sfull)
chk('Fig 3 single panel: no stale driver-panel pointer in MS',
    'Fig. 3b' not in full and 'Fig. 3c' not in full and 'Fig. 3d' not in full)
chk('Fig 3 legend points to SI 3.13 for the stratification (nc82)',
    'The accompanying LUAD driver-mutation stratification is reported in Supplementary Information 3.13' in full)
chk('Fig 4 legend old EGFR-baseline gone',
    'the EGFR association appears only in the k_n baseline' not in full)

# 7e. xv-text round: P2 clarifications in MS
chk('B=30 MC noise note (v51: SI)', 'resolves to 1/31' in sfull)
chk('tier class-composition note (v51: SI)', 'mix class composition with drift tier' in sfull)
chk('per-tumor cross-group pairing note (v50: SI 3.13)',
    'averages overlapping (non-disjoint) pair sets' in sfull)
chk('wild-type label qualified (v50: SI 3.13)',
    'wild-type (negative for both drivers)' in sfull)
chk('seeded subsampling MC note (v51: SI)',
    'Monte-Carlo error of roughly 0.01\u20130.02 ratio units' in sfull)
chk('TCGA fixed-panel caveat (v50)',
    'depend on the per-pair circular selection of k_f genes' in full)
chk('Fig 4a dual-axis note', 'The two axes use independent scales' in full)
chk('affiliation postcodes (nc65: 4 affiliations, XJTU first)',
    "School of Mathematics and Statistics, Xi'an Jiaotong University, Xi'an 710049, China" in full
    and 'Beijing 102206, China' in full and 'Chengdu 610052, China' in full
    and "Weifang Second People's Hospital, Weifang 261041, China" in full)
chk('author list (nc65: Liu / Zu / Zhang, Wu removed)',
    'Wenting Liu' in full and 'Jian Zu' in full and 'Li Zhang' in full
    and 'Xianming Wu' not in full)
chk('author contributions (nc65)',
    'W.L. performed the analyses and wrote the first draft' in full
    and 'J.Z. participated in the revision of the manuscript' in full
    and 'All authors read and approved the final manuscript' in full
    and 'X.W.' not in full and 'Both authors' not in full)

# 7f. R4-P2-4 subtitle <= 60 chars
chk('short Result 5 heading',
    'A pan-cancer map of tissue-level divergence in tumors' in full
    and 'A pan-cancer map of tissue-level functional divergence in tumors' not in full)

# 7g. Three-in-one round: KRAS magnitude + Hallmark
chk('KRAS magnitude sentence restored (v50: MS headline; Dunn P in SI)',
    'carried predominantly by a lower housekeeping baseline (~73% of the log-\u03c9 gap)' in full
    and '0.097' in sfull)
chk('KRAS magnitude coexists with adjusted (nc82: SI 3.13)',
    'k_f +0.012, '
    'P = 0.009' in sfull)
chk('Hallmark enrichment sentence (v51)',
    'no MSigDB Hallmark enrichment' in full and 'all q \u2265 0.24' in full)
chk('Hallmark distributed-signal framing (v51: k_f ordering retained)',
    'retained TT \u2265 NN k_f ordering in all five' in full)  # v54: "the" dropped for MAIN word budget
chk('k_f composition regression sentence (v51)',
    'retained TT \u2265 NN k_f ordering in all five' in full)  # v54: "the" dropped for MAIN word budget
chk('Data availability Enrichr mirror',
    'accessed via the Enrichr gene-set library (MSigDB_Hallmark_2020' in full)

# 8. R1 P2-4: Kang k_f increment honest
chk('Kang k_f 0/30 parenthetical (v52)',
    '0 of 30 above its null 95th percentile; k_f likewise' in full)

# 9. R4-P1-4: no Additional file 2
chk('no Additional file 2', 'Additional file 2' not in full)
chk('SI availability rewritten',
    'Supplementary Information is available for this paper' in full)

# 10. Prior-phase content intact
chk('severity -> Note 5 + Supp Fig 3d (nc72: 2d->3d)',
    'denominator-dominated vignettes, Supplementary Note 5' in full
    and 'Supplementary Fig. 3d' in sfull)
chk('marker Jaccard 1.41 (nc79: caption slim -> SI)', 'T3 calibration 1.41 versus 1.80' in sfull)
chk('no leftover 1.40 versus 1.80', '1.40 versus 1.80' not in full)
chk('Result 5 TCGA title',
    'A pan-cancer map of tissue-level divergence in tumors' in full)
chk('Figure 3 legend (TCGA; nc70: 4->3)', 'Figure 3. Pan-cancer tissue-level divergence in tumors' in full)
chk('Cox limitation sentence (v52)',
    'ex-CC LIHC Cox, stage categorical' in full and '1.08 [0.88, 1.33]' in full)
chk('drift Results heading', 'Real-data neutral-drift calibration on technical replicates' in full)
chk('Kang Wilson CI (v50: SI)', 'Wilson 95% CI [0.000, 0.114]' in sfull)
chk('Kang-brain size reconciliation (v58: Results + SI Note 10)',
    'the absolute \u03c9 exceedance rate grows with group size' in full
    and 'A library-aware null (class \u00d7 run-stratum, leave-self-out)' in full
    and '4.8% (95% CI 3.8\u20136.1%)' in full
    and 'essentially fully explained by class size' in sfull)

# 11. Figure legends order (nc79: cross-organ Fig 4 demoted; brain 5->4)
figs = [t[:12] for t in paras if re.match(r'^Figure \d\.', t)]
fignums = [int(re.match(r'^Figure (\d)\.', t).group(1)) for t in paras if re.match(r'^Figure \d\.', t)]
chk('main figure legends 1-4 in order (nc79: cross-organ demoted)', fignums == list(range(1, 5)), str(figs))

# 11b. v49.7: Fig 2e = change-detection ROC
chk('Fig 2 legend new scope',
    'functional-change detection in the ground-truth simulation' in full)
chk('Fig 2e legend change-detection ROC (v52)',
    'ROC curves for discriminating injected functional signal' in full
    and 'highest AUC of six metrics (0.80; paired comparisons in Supplementary Table 2c)' in full
    and 'AUC = 0.91' in full)
chk('Fig 2e legend old classification ROC gone',
    'ROC curves for cell-type classification across five metrics on Tabula Sapiens data' not in full)
chk('Result 3 anchor narrowed to Fig. 2c (nc70: 2d->2c)',
    'human column) (Fig. 2c).' in full and 'human column) (Fig. 2c, d).' not in full)
chk('Result 3b AUC sentence cites Fig. 2d (nc70: 2e->2d)',
    'from neutral perturbations in this SmartSeq2 background (Fig. 2d; AUC = 0.80' in full)
chk('Result 3b background2 cites Fig. 2d (v51; nc70: 2e->2d)',
    'AUC(k_f) = 0.859; Fig. 2d' in full)

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
chk('cross-organ demoted to Table 1 + SF5d (nc79)',
    '(Table 1; Supplementary Fig. 5d)' in full
    and 'n \u2265 5 pairs; Table 1' in full
    and '(Fig. 4; Table 1; Supplementary Fig. 5)' not in full)

# 12. Fig 3 legend honest framing
chk('Fig 2e legend Jaccard admission (nc79 caption slim; nc80 m7 interval)',
    'marker Jaccard is lower still on the false-positive statistic' in sfull
    and '\u22120.088 [\u22120.116, \u22120.059]' in sfull)

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
chk('superscript citation group count == 70 (nc79: practical-rules [14] aside cut)', len(_sup_groups) == 70,
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
raise SystemExit(1 if nfail else 0)

# ---- nc84: nc83 expert-panel P0/P1 fixes (MS) ----
chk('nc84 abstract AUC attributed to KRAS-vs-EGFR',
    bool(abs_paras) and 'KRAS-versus-EGFR discrimination is weak (AUC 0.648)' in abs_paras[0]
    and '(P = 0.089; AUC 0.648)' not in abs_paras[0])
chk('nc84 intro AUC attribution corrected',
    '\u03c9 discriminates KRAS- from EGFR-mutant tumours weakly (AUC 0.648 versus 0.841' in full)
chk('nc84 Supplementary Table 2c pointer present (MS)',
    'Supplementary Table 2c)' in full and 'Supplementary Table 2a)' not in full)
chk('nc84 dangling residence/migration citation removed',
    'residence/migration' not in full)
chk('nc84 theory language scoped',
    'with a scoped estimand' in full and 'explicit estimand' not in full
    and 'The scoped correspondence' in full and 'The full correspondence' not in full)
chk('nc84 calibration residual conditional',
    'absorbs only under design-matched permutation' in full)
chk('nc84 ambient/doublet concession in Limitations',
    'nor were ambient RNA or doublets modelled' in full)
chk('nc84 CNA attribution downgraded everywhere',
    'accounts for 56%' not in full and 'associated with \u226456%' in full
    and 'unmeasured-reference upper bound' in full)
chk('nc84 brain legend downgraded',
    'Brain regional housekeeping-anchored class-level differences' in full)
chk('nc84 Zenodo claim honest',
    'An earlier release is archived at Zenodo' in full
    and 'the v0.6.4 archive accompanies this submission' not in full)
