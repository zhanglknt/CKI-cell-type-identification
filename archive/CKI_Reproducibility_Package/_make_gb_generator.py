# -*- coding: utf-8 -*-
"""One-shot converter: generate_manuscript_nar.py -> generate_manuscript_gb.py
NAR layout  : Intro -> M&M -> Results -> Discussion -> end sections
GB layout   : Background -> Results -> Discussion -> Conclusions -> Methods
              -> List of abbreviations -> Declarations -> Additional files
Also: structured abstract, [n] citations, Additional file 1 supp citations,
      Vancouver references. Idempotent (always reads the NAR source).
"""
import ast, re, sys

SRC = 'generate_manuscript_nar.py'
DST = 'generate_manuscript_gb.py'
src = open(SRC, encoding='utf-8').read()

# ---------- 1. slice blocks by marker comments ----------
def mark(name):
    a = '# ============================================================\n# ' + name
    i = src.index(a)
    return i

A_TITLE  = mark('TITLE PAGE')
A_ABS    = mark('TEXT ABSTRACT')
A_KW     = mark('KEYWORDS')
A_INTRO  = mark('INTRODUCTION')
A_MM     = mark('MATERIALS AND METHODS')
A_RES    = mark('RESULTS (NAR')
A_DISC   = mark('DISCUSSION (NAR')
A_DA     = mark('DATA AVAILABILITY')
A_FIGL   = mark('FIGURE LEGENDS')
A_REFS   = mark('REFERENCES (NAR')

head       = src[:A_TITLE]
title      = src[A_TITLE:A_ABS]
kw         = src[A_KW:A_INTRO]
intro      = src[A_INTRO:A_MM]
methods    = src[A_MM:A_RES]
results    = src[A_RES:A_DISC]
discussion = src[A_DISC:A_DA]
endmatter  = src[A_DA:A_FIGL]
figlegends = src[A_FIGL:A_REFS]
tail       = src[A_REFS:]

# ---------- 2. extract reusable endmatter paragraphs ----------
def grab(pattern, where, name):
    m = re.search(pattern, where, re.S)
    if not m:
        sys.exit(f'FATAL: cannot extract {name}')
    return m.group(1)

da_txt  = grab(r"p\('(Tabula Muris data: [^']*)'\)", endmatter, 'data availability')
ack_txt = grab(r"p\('(We thank the Tabula Muris Consortium[^']*)'\)", endmatter, 'acknowledgements')
con_txt = grab(r"p\('(X\.W\. performed[^']*)'\)", endmatter, 'contributions')
fun_txt = grab(r"p\('(This work was supported[^']*)'\)", endmatter, 'funding')
ai_txt  = grab(r"p\('(During the preparation of this work[^']*)'\)", endmatter, 'AI statement')

# ---------- 3. citation transform  (n) / (n,m) / (n\u2013m)  ->  [n] / [n,m] / [n-m] ----------
CIT = re.compile(r"(?<![A-Za-z0-9_(\\])\((\d{1,2}(?:(?:,|, |\\u2013|\u2013)\d{1,2})*)\)")

audit = []
def cit_sub(m):
    inner = m.group(1)
    nums = [int(x) for x in re.findall(r'\d{1,2}', inner)]
    if not all(1 <= n <= 49 for n in nums):
        return m.group(0)
    audit.append(m.group(0))
    return '[' + inner.replace('\\u2013', '-').replace('\u2013', '-') + ']'

def cit(text):
    # FAKE-CITATION GUARDS -------------------------------------------------
    # 1) 'caps (12\u201325)' in Methods is the omega-cap grid (numeric value
    #    range), not a citation.  The digit guard alone cannot reject it
    #    because the literal '\u2013' escape yields digits '20','13' which
    #    both fall inside 1..49.
    # 2) Results count sentence: 'oligodendrocytes 10 (10), fibroblasts 6 (4),
    #    ...' -- parenthesised counts of Strong candidates with raw P < 0.05,
    #    not references.  Values 1..12 collide with real ref numbers.
    # 3) Fig S7 caption: 'oligodendrocytes (10) and fibroblasts (6)' -- same.
    GUARDS = [
        ('caps (12\\u201325)', 'caps @@OMEGACAPS@@'),
        ('oligodendrocytes 10 (10), fibroblasts 6 (4), astrocytes 3 (3), '
         'ependymal cells 2 (0), committed OPCs 1 (0), and OPCs 1 (1)',
         '@@CTCOUNTS@@'),
        ('oligodendrocytes (10) and fibroblasts (6)', '@@CTCAPTION@@'),
    ]
    protected = text
    for plain, token in GUARDS:
        protected = protected.replace(plain, token)
    converted = CIT.sub(cit_sub, protected)
    for plain, token in GUARDS:
        converted = converted.replace(token, plain)
    return converted

# ---------- 4. supplementary citation mapping -> Additional file 1 ----------
SUPP_MAP = [
    ('Supplementary Figures S', 'Additional file 1: Figures S'),
    ('Supplementary Figure S',  'Additional file 1: Figure S'),
    ('Supplementary Fig. S',    'Additional file 1: Fig. S'),
    ('Supplementary Tables S',  'Additional file 1: Tables S'),
    ('Supplementary Table S',   'Additional file 1: Table S'),
    ('Supplementary Note',      'Additional file 1: Note'),
]
def supp(text):
    for a, b in SUPP_MAP:
        text = text.replace(a, b)
    return text

def body(text):
    return supp(cit(text))

# ---------- 5. title block: drop NAR running title ----------
i1 = title.index('# Running title')
i2 = title.index('sub = doc.add_paragraph()')
title = title[:i1] + title[i2:]

# ---------- 6. heading renames ----------
intro   = intro.replace("heading('Introduction', level=1)", "heading('Background', level=1)")
methods = methods.replace("heading('Materials and Methods', level=1)", "heading('Methods', level=1)")

# ---------- 7. structured abstract (GB: Background / Results / Conclusions, <=250 words) ----------
abstract = (
"# ============================================================\n"
"# ABSTRACT (structured: Background / Results / Conclusions, <=250 words - GB)\n"
"# ============================================================\n"
"heading('Abstract', level=1)\n"
"\n"
"def ab(label, text):\n"
"    para = doc.add_paragraph()\n"
"    r1 = para.add_run(label + '. ')\n"
"    r1.font.name = 'Arial'; r1.font.size = Pt(11); r1.bold = True; set_black(r1)\n"
"    r2 = para.add_run(text)\n"
"    r2.font.name = 'Arial'; r2.font.size = Pt(11); set_black(r2)\n"
"    para.paragraph_format.line_spacing = 1.15\n"
"    para.paragraph_format.space_after = Pt(4)\n"
"    return para\n"
"\n"
"ab('Background', 'Standard distance metrics conflate baseline variation with functional adaptation in single-cell genomics. Inspired by the Ka/Ks ratio, CKI (Cell-type Identity Index) decomposes divergence into a baseline rate k_n (housekeeping genes) and a functional rate k_f (identity genes); \\u03c9 = k_f/k_n quantifies baseline-normalized functional divergence.')\n"
"ab('Results', 'In a ground-truth simulation, \\u03c9 alone rejected neutral housekeeping-gene drift (false-positive rate 0.00, versus 0.58 for cosine and 0.55 for raw JS) and ranked first for functional-versus-neutral discrimination (AUC = 0.80), at the cost of bounded power. We evaluated CKI on mouse (Tabula Muris), human (Tabula Sapiens), pan-cancer (The Cancer Genome Atlas, TCGA; exploratory), and brain single-nucleus datasets. Calibration established an equivalent-population baseline (\\u03c9 = 6.67, 95% CI [4.24, 9.24]). CKI \\u03c9 correlated negatively with all standard distance metrics (Spearman r = \\u22120.36 to \\u22120.46), partly a k_n-denominator artifact. Brain analysis indicated a 6.10-fold regional differentiation gradient across 10 non-neuronal classes, predominantly k_n-driven (3.21-fold k_n versus 2.03-fold k_f); under a strict block-shuffle null, four of ten classes showed significant regional structure (three after false-discovery-rate correction), but no pair survived correction. A gene-panel ablation showed per-pair gene selection inflates k_f (median 1.6-fold) but preserves rankings (Spearman \\u03c1 \\u2248 0.92 across 31,764 brain comparisons).')\n"
"ab('Conclusions', 'CKI provides an interpretable, baseline-normalized index of cell-state divergence whose rankings are robust to gene-panel choice, and is freely available as an open-source package.')\n"
"\n")

# ---------- 8. new sections ----------
conclusions = (
"# ============================================================\n"
"# CONCLUSIONS (GB: required, before Methods)\n"
"# ============================================================\n"
"heading('Conclusions', level=1)\n"
"p('CKI adapts the baseline-normalization logic of Ka/Ks to single-cell transcriptomics, decomposing population divergence into a housekeeping baseline rate (k_n) and an identity-gene functional rate (k_f). Across simulation, calibration, cross-organ, pan-cancer, and brain-regional analyses, we showed that \\u03c9 rankings carry reproducible biological signal while absolute \\u03c9 values remain scheme- and dataset-specific, that statistical claims at atlas scale require nulls respecting the experimental design, and that the absence of FDR-significant candidates is itself an informative bound on what adult transcriptomes alone can support. CKI is released as an open-source Python package with a fully reproducible analysis pipeline, and we anticipate its use as an interpretable complement to standard distance metrics in comparative single-cell analyses.')\n"
"\n")

llm_methods = (
"heading('Use of large language models', level=2)\n"
f"p('{ai_txt}')\n"
"\n")
methods = methods.rstrip() + '\n\n' + llm_methods

abbrev = (
"# ============================================================\n"
"# LIST OF ABBREVIATIONS (GB: required when abbreviations are used)\n"
"# ============================================================\n"
"heading('List of abbreviations', level=1)\n"
"p('AUC, area under the ROC curve; BH, Benjamini-Hochberg; CKI, Cell-type Identity Index; CV, coefficient of variation; DE, differentially expressed; FDR, false discovery rate; GSVA, gene set variation analysis; HK, housekeeping; HVG, highly variable gene; IQR, interquartile range; JS, Jensen-Shannon; OPC, oligodendrocyte precursor cell; PAM50, prediction analysis of microarray 50; QC, quality control; ROC, receiver operating characteristic; SD, standard deviation; SES, standardized effect size; TCGA, The Cancer Genome Atlas.')\n"
"\n")

declarations = (
"# ============================================================\n"
"# DECLARATIONS (GB: all subheadings required)\n"
"# ============================================================\n"
"heading('Declarations', level=1)\n"
"\n"
"heading('Ethics approval and consent to participate', level=2)\n"
"p('Not applicable. This study analysed only publicly available, de-identified datasets and did not involve human participants, human tissue, or animals.')\n"
"\n"
"heading('Consent for publication', level=2)\n"
"p('Not applicable.')\n"
"\n"
"heading('Availability of data and materials', level=2)\n"
f"p('{da_txt}')\n"
"\n"
"heading('Competing interests', level=2)\n"
"p('The authors declare that they have no competing interests.')\n"
"\n"
"heading('Funding', level=2)\n"
f"p('{fun_txt}')\n"
"\n"
"heading(\"Authors' contributions\", level=2)\n"
f"p('{con_txt}')\n"
"\n"
"heading('Acknowledgements', level=2)\n"
f"p('{ack_txt}')\n"
"\n")

additional = (
"# ============================================================\n"
"# ADDITIONAL FILES (GB: list file name / format / title / description)\n"
"# ============================================================\n"
"heading('Additional files', level=1)\n"
"p('Additional file 1: CKI supplementary notes. Format: DOCX (a PDF rendering is also provided). Title: CKI: Supplementary Notes. Description: extended methods and supplementary analyses, including Supplementary Figures S1\\u2013S12 and Supplementary Tables S1\\u2013S4.')\n"
"\n")

# ---------- 9. Vancouver references ----------
def parse_authors(raw):
    if ',' not in raw:
        return raw, False  # corporate author
    persons, etal = [], False
    for tok in raw.split(', '):
        tok = tok.strip()
        if tok.rstrip('.') == 'et al':
            etal = True
            continue
        if tok.endswith(' et al.'):
            etal = True
            tok = tok[:-7].strip()
        for part in tok.split(' and '):
            if part.strip():
                persons.append(part.strip())
    names = []
    for p in persons:
        if ',' not in p:
            names.append(p)
            continue
        s, i = p.split(',', 1)
        third = '3rd' in i
        ini = i.replace('3rd', '').replace('.', '').replace(' ', '')
        names.append(f'{s.strip()} {ini}' + (' 3rd' if third else ''))
    if len(names) > 6 or etal:
        names = names[:6] + ['et al.']
    return ', '.join(names), etal

def van_ref(s):
    if 'Chapman and Hall/CRC' in s:
        return 'Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman and Hall/CRC; 1994.'
    m = re.match(r'(.+?) \((\d{4})\) (.+)$', s)
    if not m:
        sys.exit(f'FATAL ref parse: {s[:80]}')
    authors_raw, year, rest = m.groups()
    jm = re.match(r'(.+?)\*([^*]+)\*, \*\*([^*]+)\*\*, (.+?)\.?\s*$', rest)
    if not jm:
        sys.exit(f'FATAL journal parse: {s[:80]}')
    title, journal, vol, pages = jm.groups()
    title = title.strip()
    if not title.endswith('.'):
        title += '.'
    journal = journal.rstrip('.')
    pages = pages.rstrip('.').replace('\u2013', '-')
    astr, _ = parse_authors(authors_raw)
    return f'{astr.rstrip(chr(46))}. {title} {journal}. {year};{vol}:{pages}.'

tree = ast.parse(src)
refs = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_refs_nar' for t in node.targets):
        refs = [ast.literal_eval(e) for e in node.value.elts]
assert refs and len(refs) == 49
van = [van_ref(r) for r in refs]
print('--- VANCOUVER CONVERSION (before -> after) ---')
for i, (a, b) in enumerate(zip(refs, van), 1):
    print(f'[{i}] {b}')

i = head.index('_refs_nar = [')
j = head.index('\n]', i)
refblock = '_refs_nar = [\n' + ''.join(f'    {r!r},\n' for r in van)
head = head[:i] + refblock + head[j:]

# ---------- 10. apply body transforms ----------
# GB section is named 'Methods'; remap inline cross-references that point to
# the old 'Materials and Methods' section title (Results L549/L553 style).
results = results.replace('; Materials and Methods)', '; Methods)')

kw          = body(kw)
intro       = body(intro)
methods     = body(methods)
results     = body(results)
discussion  = body(discussion)
figlegends  = body(figlegends)
declarations = cit(declarations)   # da_txt carries citations
conclusions  = conclusions

# supplegends heading retitle
figlegends = figlegends.replace(
    "heading('Supplementary Figure legends', level=1)",
    "heading('Additional file 1: Supplementary figure legends', level=1)")

# ---------- 11. output name ----------
tail = tail.replace('"results" / "CKI_Manuscript.docx"', '"results" / "CKI_Manuscript_GB.docx"')
tail = tail.replace('# REFERENCES (NAR: numbered, parentheses format)', '# REFERENCES (GB: Vancouver, square-bracket citations)')
# GB/Vancouver requires a NUMBERED reference list matching the [n] citations
tail = tail.replace(
    "for ref in _refs_nar:\n    ref_p_nar(ref)",
    "for i, ref in enumerate(_refs_nar, 1):\n    ref_p_nar(f'{i}. {ref}')")

# ---------- 12. compose ----------
out = (head + title + abstract + kw + intro + results + discussion
       + conclusions + methods + abbrev + declarations + additional
       + figlegends + tail)
open(DST, 'w', encoding='utf-8').write(out)
ast.parse(out)
print('\nSYNTAX OK ->', DST)
print('citation transforms applied:', len(audit))
seq = [int(n) for a in audit for n in re.findall(r'\d{1,2}', a)]
first = []
for n in seq:
    if n not in first:
        first.append(n)
print('first-appearance order:', first)
print('monotonic:', first == sorted(first), '| complete 1..49:', first == list(range(1, 50)))
bad = [a for a in audit if not re.fullmatch(r'\(\d{1,2}(?:[,\\u2013\u2013-]+\d{1,2})*\)', a)]
print('audit anomalies:', bad if bad else 'NONE')
