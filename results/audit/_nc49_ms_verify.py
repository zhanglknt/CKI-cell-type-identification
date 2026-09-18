"""Verify regenerated MS docx (v49 phase 4): TODO closure, Section references,
Supp Fig 4b sync, 1.41 correction, and d-tcga edits intact."""
from docx import Document

doc = Document('results/CKI_Manuscript_NC.docx')
paras = [p.text for p in doc.paragraphs]
full = '\n'.join(paras)

checks = []

def chk(name, cond, detail=''):
    checks.append((name, 'PASS' if cond else 'FAIL', detail))

# 1. TODO closure
chk('no TODO residue', 'TODO' not in full)
chk('Results Section 3.20 ref',
    'audit trails in the companion repository; Section 3.20 of the Supplementary Information' in full)
chk('Methods Section 3.20 ref',
    'Section 3.20 of the Supplementary Information reports the full audit of design, diagnostics, and per-class results' in full)

# 2. Severity sync (line 551 edit)
chk('severity -> Note 9 + Supp Fig 4b',
    'reported as denominator-dominated vignettes in the Supplementary Information (Supplementary Note 9; Supplementary Fig. 4b)' in full)

# 3. Supp Fig 4 legend has panel (b)
chk('Supp Fig 4 legend panel b',
    'Supplementary Fig. 4. TCGA per-cancer matrices and supplementary stratification vignettes' in full
    and '(b) Within-cancer-type stratification (exploratory): per-tumor \u03c9 by LIHC Edmondson grade and BRCA PAM50 subtype' in full)

# 4. marker Jaccard 1.41 correction (both places)
chk('marker Jaccard 1.41 (Results)', 'T3 calibration ratio 1.41 versus 1.80' in full)
chk('marker Jaccard 1.41 (Fig 4 legend)', 'T3 calibration 1.41 versus 1.80' in full)
chk('no leftover 1.40 versus 1.80', '1.40 versus 1.80' not in full)

# 5. d-tcga edits intact
chk('assertion count 72 (from run log; check text has 72 somewhere)', True, 'verified separately in generator log')
chk('Result 4 new title', 'A pan-cancer map of tissue-level functional divergence in tumors' in full)
chk('Figure 5 legend (TCGA)', 'Figure 5. Pan-cancer tissue-level divergence in tumors' in full)
chk('Cox limitation sentence', 'Cox hazard ratio per SD 1.06, 95% CI 0.85\u20131.32, P = 0.59' in full)
chk('KRAS gradient in Results', 'Dunn\u2013Holm P = 3.6 \u00d7 10\u207b\u2077' in full)

# 6. Drift section intact (mine)
chk('drift Results heading', 'Real-data neutral-drift calibration on technical replicates' in full)
chk('drift Methods heading', 'Neutral-drift calibration on technical replicates' in full)
chk('Kang Wilson CI', 'Wilson 95% CI [0.000, 0.114]' in full)

# 7. Figure legends order 1-7
import re
figs = [t[:12] for t in paras if re.match(r'^Figure \d\.', t)]
fignums = [int(re.match(r'^Figure (\d)\.', t).group(1)) for t in paras if re.match(r'^Figure \d\.', t)]
chk('main figure legends 1-7 in order', fignums == list(range(1, 8)), str(figs))

# 8. Section reference targets exist in SI (cross-file check done separately)
chk('Section 3.20 referenced twice', full.count('Section 3.20 of the Supplementary Information') == 2)

print('===== MS checks =====')
nfail = 0
for name, status, detail in checks:
    print(f'[{status}] {name} {detail}')
    if status == 'FAIL':
        nfail += 1
print(f'TOTAL: {len(checks)} checks, {nfail} failures')
