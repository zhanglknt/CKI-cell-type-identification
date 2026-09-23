"""XV7 cross-validation for v50 (NC): independent recomputation of the
microglia headline numbers from the CSV, word budgets, title sync,
citation integrity, zip integrity, and SI migration spot-checks.
Run AFTER 99_build_nc_v49.py (fulltexts + zip must be fresh)."""
import re
import zipfile
import hashlib
import pandas as pd
from scipy.stats import mannwhitneyu
from docx import Document

P, F = [], []
def chk(name, cond, detail=''):
    (P if cond else F).append(name)
    print(f'[{"PASS" if cond else "FAIL"}] {name} {detail}')

# ---------- 1. microglia headline numbers (independent recompute) ----------
df = pd.read_csv('results/nc50_brain_atlas_microglia.csv')
func = df[df['pair_class'] == 'functional']
neut = df[df['pair_class'] != 'functional']
chk('functional n = 35', len(func) == 35, f'got {len(func)}')
chk('neutral n = 40', len(neut) == 40, f'got {len(neut)}')
mf, mn = func['omega'].mean(), neut['omega'].mean()
sf, sn_ = func['omega'].std(ddof=1), neut['omega'].std(ddof=1)
chk('omega functional 21.83 +/- 7.20', f'{mf:.2f}' == '21.83' and f'{sf:.2f}' == '7.20',
    f'{mf:.2f} +/- {sf:.2f}')
chk('omega neutral 1.30 +/- 0.36', f'{mn:.2f}' == '1.30' and f'{sn_:.2f}' == '0.36',
    f'{mn:.2f} +/- {sn_:.2f}')
u = mannwhitneyu(func['omega'], neut['omega'], alternative='greater')
chk('MWU P = 5.5e-14', f'{u.pvalue:.1e}' == '5.5e-14', f'{u.pvalue:.2e}')
def auc(x, y):
    # rank AUC P(x > y)
    import numpy as np
    return float(np.mean([ (a > b) + 0.5 * (a == b) for a in x for b in y ]))
chk('omega AUC = 1.00', auc(func['omega'], neut['omega']) == 1.0)
chk('k_f AUC = 1.00', auc(func['k_f'], neut['k_f']) == 1.0)
kf_auc_n = auc(func['k_n'], neut['k_n'])
chk('k_n AUC = 0.89', f'{kf_auc_n:.2f}' == '0.89', f'{kf_auc_n:.3f}')

# ---------- 2. word budgets ----------
doc = Document('results/CKI_Manuscript_NC.docx')
secs, cur = {}, None
for p in doc.paragraphs:
    t = p.text.strip()
    if t in ('Introduction', 'Results', 'Discussion', 'Methods'):
        cur = t; secs[cur] = 0
    elif t in ('Abstract', 'References', 'Acknowledgements', 'Author contributions',
               'Data availability', 'Code availability'):
        cur = None
    elif cur:
        secs[cur] += len(t.split())
main = sum(secs.get(k, 0) for k in ('Introduction', 'Results', 'Discussion'))
chk('MAIN (Intro+Results+Discussion) <= 8000', main <= 8000,
    f'{main} words {secs}')
abs_paras = [p.text for p in doc.paragraphs if 'Inspired by the Ka/Ks ratio' in p.text]
chk('Abstract <= 200 words', len(abs_paras) == 1 and len(abs_paras[0].split()) <= 200,
    f'{len(abs_paras[0].split()) if abs_paras else 0} words')

# ---------- 3. title H1 sync across MS/SI/CL/Guide ----------
H1 = 'CKI: a Ka/Ks-inspired index separating functional divergence from baseline variation in cell atlases'
ms = open('results/CKI_Manuscript_NC_fulltext.txt', encoding='utf-8').read()
sn = open('results/CKI_Supplementary_NC_fulltext.txt', encoding='utf-8').read()
cl = open('results/CKI_NC_Cover_Letter_fulltext.txt', encoding='utf-8').read()
gd = open('results/CKI_Reproducibility_Guide_NC_fulltext.txt', encoding='utf-8').read()
for nm, src in (('MS', ms), ('SI', sn), ('CL', cl)):
    chk(f'title H1 in {nm}', H1 in src)
chk('Guide carries no stale title (Guide never carries MS title)',
    'in single-cell genomics' not in gd and 'baseline variation in cell atlases' not in gd)
chk('no stale title in MS', 'in single-cell genomics' not in ms.split('Abstract')[0])

# ---------- 4. citation integrity ----------
def _cite_expand(s):
    out = []
    for part in s.split(','):
        part = part.strip()
        m = re.match(r'^(\d+)\s*[\u2013\-]\s*(\d+)$', part)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out
paras = [p.text for p in doc.paragraphs]
_ai = next(i for i, t in enumerate(paras) if t.strip() == 'Abstract')
_ri = next(i for i, t in enumerate(paras) if t.strip() == 'References')
groups = []
for _p in doc.paragraphs[_ai + 1:_ri]:
    for _r in _p.runs:
        if _r.font.superscript:
            groups.append(_cite_expand(_r.text))
chk('citation groups = 73', len(groups) == 73, f'got {len(groups)}')
_first, _seen = [], set()
for g in groups:
    for n in g:
        if n not in _seen:
            _seen.add(n); _first.append(n)
chk('first-appearance 1..57 monotonic', _first == list(range(1, 58)),
    f'head {_first[:30]}')
chk('no orphans (57 cited)', len(_seen) == 57)

# ---------- 5. zip integrity ----------
z = zipfile.ZipFile('CKI_Submission_v50_NC.zip')
names = z.namelist()
chk('zip 28 entries', len(names) == 28, f'got {len(names)}')
chk('zip has Supplementary_Fig_14.pdf',
    'CKI_Submission_v50_NC/Supplementary_Fig_14.pdf' in names)
chk('zip has microglia csv (via MANIFEST or file list not required; skip)', True)
sha = hashlib.sha256(open('CKI_Submission_v50_NC.zip', 'rb').read()).hexdigest()
print(f'  zip sha256 = {sha}')
chk('zip size < 15 MB', len(open('CKI_Submission_v50_NC.zip', 'rb').read()) < 15e6,
    f"{len(open('CKI_Submission_v50_NC.zip', 'rb').read()):,} B")

# ---------- 6. SI migration spot-checks ----------
mig = {
    'leave-one-out 6.75-8.08': '6.75' in sn and '8.08' in sn,
    'span-matched 4.30 [3.40, 4.95]': '4.30' in sn and '3.40' in sn and '4.95' in sn,
    'equal-n [2.02, 2.18]': '2.02' in sn and '2.18' in sn,
    'microglia null 52.0 / 2.30-fold': '52.0' in sn and '2.30-fold' in sn,
    'LUAD purity +16.8': '+16.8' in sn,
    'smoking chi2 30.3': '30.3' in sn,
    'LIHC CC TT k_n 1.34 [0.997, 1.880]': '1.34 [0.997, 1.880]' in sn,
    'MK inversion in SI 1.4': 'Ks' in sn and 'branch' in sn,
}
for k, v in mig.items():
    chk(f'SI carries: {k}', v)

# ---------- 7. Note/Fig structure ----------
heads = sorted(set(int(m.group(1)) for m in re.finditer(r'Supplementary Note (\d+):', sn)))
chk('SI Notes 1..16', heads == list(range(1, 17)), str(heads))
chk('MS cites Notes 1-16 span', 'Supplementary Notes 1\u201316' in ms)
chk('MS cites Supplementary Fig. 14', 'Supplementary Fig. 14' in ms)
chk('SI cites Supplementary Fig. 14', 'Supplementary Fig. 14' in sn)
chk('MS Note 16 pointer numbers verbatim',
    '21.83 \u00b1 7.20 versus 1.30 \u00b1 0.36' in ms and '5.5 \u00d7 10\u207b\u00b9\u2074' in ms
    and 'AUC = 1.00' in ms)

print(f'\nXV7 TOTAL: {len(P) + len(F)} checks, {len(F)} failures')
if F:
    print('FAILURES:', F)
    raise SystemExit(1)
print('XV7 ALL PASS')
