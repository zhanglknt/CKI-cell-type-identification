"""XV8 cross-validation for v52 (NC ex-CC default + panel-recompute round):
word budgets (NC limits), figure-legend budgets, title length, Discussion
subheading ban, declaration blocks, citation integrity, zip integrity,
MS<->SI pointer consistency, and v51/v52 SI-migration spot-checks.
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

doc = Document('results/CKI_Manuscript_NC.docx')
ms = open('results/CKI_Manuscript_NC_fulltext.txt', encoding='utf-8').read()
sn = open('results/CKI_Supplementary_NC_fulltext.txt', encoding='utf-8').read()
cl = open('results/CKI_NC_Cover_Letter_fulltext.txt', encoding='utf-8').read()
gd = open('results/CKI_Reproducibility_Guide_NC_fulltext.txt', encoding='utf-8').read()

# ---------- 1. word budgets (NC) ----------
secs, cur = {}, None
for p in doc.paragraphs:
    t = p.text.strip()
    if t in ('Introduction', 'Results', 'Discussion', 'Methods'):
        cur = t; secs[cur] = [0, 0]
    elif t in ('Abstract', 'References', 'Acknowledgements', 'Author contributions',
               'Data availability', 'Code availability', 'Competing interests'):
        cur = None
    elif cur:
        w = len(t.split())
        secs[cur][0] += w
        if p.style.name.startswith('Heading'):
            secs[cur][1] += w
main = sum(secs[k][0] for k in ('Introduction', 'Results', 'Discussion'))
main_xh = main - sum(secs[k][1] for k in ('Introduction', 'Results', 'Discussion'))
chk('MAIN (Intro+Results+Discussion) <= 5000 (NC, v52)', 0 < main <= 5000,
    f'{main} incl subheadings, {main_xh} excl {secs}')
chk('Methods < 3000 (NC)', 0 < secs['Methods'][0] < 3000, f"{secs['Methods'][0]} words")
abs_p = [p.text for p in doc.paragraphs if 'Inspired by Ka/Ks' in p.text]
chk('Abstract <= 200 words (NC)', len(abs_p) == 1 and len(abs_p[0].split()) <= 200,
    f'{len(abs_p[0].split()) if abs_p else 0} words')
chk('Abstract carries no citation superscripts',
    all(not r.font.superscript for p in doc.paragraphs if 'Inspired by Ka/Ks' in p.text
        for r in p.runs))

H1 = 'CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases'
chk('Title <= 15 words (NC)', len(H1.split()) <= 15, f'{len(H1.split())} words')
for nm, src in (('MS', ms), ('SI', sn), ('CL', cl)):
    chk(f'title H1 in {nm}', H1 in src)

# ---------- 2. figure legend budgets (NC: <=350 words each) ----------
leg = {}
for p in doc.paragraphs:
    t = p.text.strip()
    m = re.match(r'^Figure (\d+)\.', t)
    if m:
        leg[int(m.group(1))] = len(t.split())
chk('main figure legends 1..6 present', sorted(leg) == [1, 2, 3, 4, 5, 6], str(leg))
chk('every main figure legend <= 350 words (NC)', all(v <= 350 for v in leg.values()),
    f'max = Figure {max(leg, key=leg.get)} at {max(leg.values())}')

# ---------- 3. structure: order + Discussion without subheadings ----------
paras = doc.paragraphs
idx = {}
for i, p in enumerate(paras):
    if p.text.strip() in ('Abstract', 'Introduction', 'Results', 'Discussion',
                          'Methods', 'References'):
        idx.setdefault(p.text.strip(), i)
chk('section order Abstract<Intro<Results<Discussion<Methods<References',
    idx['Abstract'] < idx['Introduction'] < idx['Results'] < idx['Discussion']
    < idx['Methods'] < idx['References'], str(idx))
disc_heads = [p.text.strip()[:50] for p in paras[idx['Discussion'] + 1:idx['Methods']]
              if p.style.name.startswith('Heading') and p.text.strip()]
chk('Discussion has no subheadings (NC)', disc_heads == [], str(disc_heads))

# ---------- 4. declaration blocks (NC pre-submission) ----------
for h in ('Acknowledgements', 'Author contributions', 'Competing interests',
          'Data availability', 'Code availability'):
    chk(f'declaration present: {h}', any(p.text.strip() == h for p in paras))

# ---------- 5. citation integrity ----------
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
_ai, _ri = idx['Abstract'], idx['References']
groups = []
for _p in paras[_ai + 1:_ri]:
    for _r in _p.runs:
        if _r.font.superscript:
            groups.append(_cite_expand(_r.text))
chk('citation groups = 72', len(groups) == 72, f'got {len(groups)}')
_first, _seen = [], set()
for g in groups:
    for n in g:
        if n not in _seen:
            _seen.add(n); _first.append(n)
chk('first-appearance 1..57 monotonic', _first == list(range(1, 58)),
    f'head {_first[:30]}')
chk('no orphans (57 cited)', len(_seen) == 57)

# ---------- 6. zip integrity ----------
z = zipfile.ZipFile('CKI_Submission_v50_NC.zip')
names = z.namelist()
chk('zip 28 entries', len(names) == 28, f'got {len(names)}')
chk('zip has Supplementary_Fig_14.pdf',
    'CKI_Submission_v50_NC/Supplementary_Fig_14.pdf' in names)
sha = hashlib.sha256(open('CKI_Submission_v50_NC.zip', 'rb').read()).hexdigest()
print(f'  zip sha256 = {sha}')
chk('zip size < 15 MB', len(open('CKI_Submission_v50_NC.zip', 'rb').read()) < 15e6,
    f"{len(open('CKI_Submission_v50_NC.zip', 'rb').read()):,} B")

# ---------- 7. MS<->SI pointer consistency (v51) ----------
chk('MS Supplementary Methods 5.x pointers = 20 (v52: +5.5 entry-cluster)', ms.count('Supplementary Methods 5.') == 20,
    f"got {ms.count('Supplementary Methods 5.')}")
chk('MS cites Notes 1-16 span', 'Supplementary Notes 1\u201316' in ms)
chk('MS cites Figs 1-14 span', 'Supplementary Figs. 1\u201314' in ms)
chk('MS Section 3.12 pointers = 2 (proof: L37 dedup)', ms.count('Section 3.12') == 2)
chk('SI carries Supplementary Methods section', 'Supplementary Methods' in sn)
_sm_heads = [f'5.{i} ' for i in range(1, 15)]
_missing = [h for h in _sm_heads if not re.search(rf'^{re.escape(h)}', sn, re.M)]
chk('SI Supplementary Methods 5.1-5.14 headings present', _missing == [], str(_missing))
chk('SI v51 migration markers = 6', sn.count('migrated from the main text in v51') == 6,
    f"got {sn.count('migrated from the main text in v51')}")

# ---------- 8. v51 SI-migration spot-checks ----------
mig = {
    'Kang calibration median 0.963': '0.963' in sn,
    'brain T2 omega FPR 90.9': '90.9' in sn,
    'high-purity LUAD 2.86': '2.86' in sn,
    'CC provenance (positions 14-15)': 'sample-source code (positions 14\u201315)' in sn,
    'percentile bootstrap interval': '2.5th and 97.5th percentiles of the resampled ratios' in sn,
    'seed 20260905': 'seed 20260905' in sn,
    'sample counts 3,593': 'spans 3,593 unique barcodes' in sn,
    'smoking +13.3 P=1.4e-3': '+13.3, P = 1.4 \u00d7 10\u207b\u00b3' in sn,
    'agg-order Spearman 0.78': 'rank ordering is largely preserved (Spearman \u03c1 = 0.78)' in sn,
    'agg-order baseline 6.46 to 10.94': 'moves from 6.46 to 10.94' in sn,
    'span-matched residual k_f 1.39 / k_n 0.33': 'k_f 1.39 and k_n 0.33' in sn,
    'ex-CC default NN/TT 1.11 [0.94, 1.30] (v52)': 'NN/TT 1.11 [0.94, 1.30]' in sn,
    'composition Spearman 0.380 (ex-CC, v52)': 'Spearman \u03c1 = 0.380 pooled' in sn,
    'composition median |dz| 1.305': 'median |\u0394z| 1.305-fold' in sn,
    'k_f 0.247/0.250': '0.247' in sn and '0.250' in sn,
    'k_n 0.0130/0.0148': '0.0130' in sn and '0.0148' in sn,
    'ablation rho 0.86-0.88': '0.86\u20130.88' in sn,
    'grand means 75.18/16.73': '75.18' in sn and '16.73' in sn,
    'IFN 1.1-2.0-fold': '1.1\u20132.0-fold' in sn,
    'skin power 0.98-1.00 / 0.04-0.20': '0.98\u20131.00' in sn and '0.04\u20130.20' in sn,
    'Cox P = 0.467 (ex-CC, v52)': 'P = 0.467' in sn,
    'two-stage calibration CI (v52)': 'two-stage population-resampled bootstrap 95% CI [6.38, 9.82]' in sn,
    'combined control gradient 3.66 (v52)': 'observed gradient of 3.66 [3.60, 3.71]' in sn,
    'R coxph in SI methods (v52)': 'R survival::coxph' in sn,
    'GTEx healthy/adjacent ratio (v52)': 'healthy/adjacent' in sn,
    'ex-CC LIHC severity (v52)': '78.8, 75.8, 77.6, 72.3' in sn,
    'entry-cluster CIs in SI 5.5 (v52)': 'entry-clustered bootstrap 95% CIs' in sn,
    'ex-CC pair table 34,828 (v52)': '34,828 pairs' in sn,
    'Guide 5.13 nc52 section (v52)': '5.13 nc52 Analyses' in gd,
    'sample count 3,535 ex-CC (v52)': '3,535' in ms and '3,535 samples' in gd,
}
for k, v in mig.items():
    chk(f'SI carries: {k}', v)

# ---------- 9. microglia headline (independent recompute, kept from XV7) ----------
df = pd.read_csv('results/nc50_brain_atlas_microglia.csv')
func = df[df['pair_class'] == 'functional']
neut = df[df['pair_class'] != 'functional']
mf, mn = func['omega'].mean(), neut['omega'].mean()
sf, ss = func['omega'].std(ddof=1), neut['omega'].std(ddof=1)
chk('microglia omega 21.83+/-7.20 vs 1.30+/-0.36',
    f'{mf:.2f}' == '21.83' and f'{sf:.2f}' == '7.20'
    and f'{mn:.2f}' == '1.30' and f'{ss:.2f}' == '0.36',
    f'{mf:.2f}/{sf:.2f} vs {mn:.2f}/{ss:.2f}')
u = mannwhitneyu(func['omega'], neut['omega'], alternative='greater')
chk('microglia MWU P = 5.5e-14', f'{u.pvalue:.1e}' == '5.5e-14', f'{u.pvalue:.2e}')

# ---------- 10. SI Notes structure ----------
heads = sorted(set(int(m.group(1)) for m in re.finditer(r'Supplementary Note (\d+):', sn)))
chk('SI Notes 1..16', heads == list(range(1, 17)), str(heads))

print(f'\nXV8 TOTAL: {len(P) + len(F)} checks, {len(F)} failures')
if F:
    print('FAILURES:', F)
    raise SystemExit(1)
print('XV8 ALL PASS')
