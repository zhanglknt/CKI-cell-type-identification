# -*- coding: utf-8 -*-
"""
build_nc_ms.py — 由 generate_manuscript_gb.py 生成 generate_manuscript_nc.py。

GB → NC 改造（team-lead 11 项规格），全部带锚点断言。
只读 generate_manuscript_gb.py，写出 generate_manuscript_nc.py + 计数 JSON。
"""
import json
import py_compile
import re
from pathlib import Path

ROOT = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
SRC_P = ROOT / "generate_manuscript_gb.py"
OUT_P = ROOT / "generate_manuscript_nc.py"
COUNTS_P = ROOT / "_tmp_fa_review" / "nc_ms_build_counts.json"

src = SRC_P.read_text(encoding="utf-8")
counts = {}

def rep(name, old, new, expect=1):
    global src
    n = src.count(old)
    assert n == expect, f"[{name}] anchor count {n} != {expect}"
    src = src.replace(old, new)
    counts[name] = n
    print(f"OK  {name}: {n}")

def rep_re(name, pattern, repl, expect):
    global src
    src, n = re.subn(pattern, repl, src)
    assert n == expect, f"[{name}] regex count {n} != {expect}"
    counts[name] = n
    print(f"OK  {name}: {n}")

def rep_span(name, start_anchor, end_anchor, new, keep_end=True):
    global src
    i = src.index(start_anchor)
    j = src.index(end_anchor, i + len(start_anchor))
    if keep_end:
        src = src[:i] + new + src[j:]
    else:
        src = src[:i] + new + src[j + len(end_anchor):]
    counts[name] = 1
    print(f"OK  {name}: span replaced")

# ---------------------------------------------------------------- 1. docstring
OLD_DOC = '''"""
Generate CKI_Manuscript.docx — Nucleic Acids Research article.

NAR formatting compliance:
- Single-column, single-spaced
- No line numbers (page numbers only)
- Unstructured abstract (≤200 words, single paragraph)
- Section order: Introduction → Materials and Methods → Results → Discussion
- Numbered references in parentheses: (2), (3,4), (4-7)
- NAR reference style: Author,A.B., Author,C.D. (Year) Title. *Journal.*, **Vol**, Pages.
- Authors listed up to 20, then et al.
- All text black; Arial/Helvetica (TrueType embedded)
- AI use statement (OUP mandatory disclosure)
"""'''
NEW_DOC = '''"""
Generate CKI_Manuscript_NC.docx — Nature Communications Article.

NC formatting compliance:
- Section order: Title -> Abstract -> Introduction -> Results -> Discussion ->
  Methods -> Data availability -> Code availability -> References ->
  Acknowledgements -> Author contributions -> Competing interests -> Figure legends
- Unstructured abstract <=150 words, single paragraph; no Keywords line;
  no Conclusions section (merged into Discussion); no List of abbreviations
- No subheadings inside Discussion; no level-3 subheadings inside Results
- Nature reference style: Author, A. B. et al. Title. *Journal* **Vol**, pages (year).
  >=6 authors -> first author + et al.; <=5 authors all listed (" & " before last)
- In-text citations: superscript numerals (ranges with en dash)
- Supplementary naming: Supplementary Fig./Table/Note; panel labels lowercase
- Methods contains a "Statistics and reproducibility" section
- AI use statement kept inside Methods
"""'''
rep("docstring", OLD_DOC, NEW_DOC)

# ---------------------------------------------------------------- 2. import re
rep("import re", "from pathlib import Path\n", "from pathlib import Path\nimport re\n")

# ---------------------------------------------------------------- 3. p() -> citation-superscript version
OLD_P = '''def p(text, bold=False, italic=False, size=11):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(size)
    set_black(run)
    run.bold = bold
    run.italic = italic
    para.paragraph_format.line_spacing = 1.15
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.first_line_indent = Cm(0)
    return para'''
NEW_P = r'''_CITE_GROUP_RE = re.compile(r'\[(\d+(?:\s*[,\-]\s*\d+)*)\]')
_cite_sup_count = 0

def _is_citation_group(content):
    # Guard: only convert groups whose parts are all integers in 1-56.
    # This excludes 95% CI brackets such as [7.37, 8.02] (decimals),
    # [0, 1] (JS range) and [12, 74] (bootstrap CI).
    try:
        nums = [int(x) for x in re.split(r'[,\-]', content)]
    except ValueError:
        return False
    return all(1 <= n <= 56 for n in nums)

def _fmt_citation(content):
    # [22-24] -> 22–24 (en dash); [6,7] -> 6,7
    parts = []
    for part in content.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            parts.append(a.strip() + '\u2013' + b.strip())
        else:
            parts.append(part)
    return ','.join(parts)

def p(text, bold=False, italic=False, size=11):
    """Body paragraph. Numeric citation groups [n] / [n,m] / [n-m] are split
    into superscript runs (NC style); all other brackets pass through."""
    global _cite_sup_count
    para = doc.add_paragraph()

    def _add(t, sup=False):
        if not t:
            return
        run = para.add_run(t)
        run.font.name = 'Arial'
        run.font.size = Pt(size)
        set_black(run)
        run.bold = bold
        run.italic = italic
        if sup:
            set_superscript(run)

    pos = 0
    for m in _CITE_GROUP_RE.finditer(text):
        if not _is_citation_group(m.group(1)):
            continue
        _add(text[pos:m.start()])
        _add(_fmt_citation(m.group(1)), sup=True)
        _cite_sup_count += 1
        pos = m.end()
    _add(text[pos:])
    para.paragraph_format.line_spacing = 1.15
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.first_line_indent = Cm(0)
    return para'''
rep("p() citation superscript", OLD_P, NEW_P)

# ---------------------------------------------------------------- 4. references
OLD_REFS_COMMENT = '''# ============================================================
# NAR REFERENCE LIST
# Format: Author,A.B., Author,C.D. and Author,E.F. (Year) Title. *Journal.*, **Vol**, Pages.
# Authors up to 20, then et al.
# Journal italic, volume bold.
# ============================================================'''
NEW_REFS_COMMENT = '''# ============================================================
# NC REFERENCE LIST (Nature style)
# Author, A. B., Author, C. D. & Author, E. F. Title. *Journal* **Vol**, pages (year).
# >=6 authors -> first author + et al.; <=5 authors all listed.
# Markup: «i»..«/i» = italic journal, «b»..«/b» = bold volume + comma.
# ============================================================'''
rep("refs comment", OLD_REFS_COMMENT, NEW_REFS_COMMENT)

# extract old entries (for the report mapping) before replacing the list
_m = re.search(r"_refs_nar = \[\n(.*?)\n\]\n", src, re.S)
assert _m, "refs list anchor not found"
OLD_REFS = re.findall(r"^'(.*)',$", _m.group(1), re.M)
assert len(OLD_REFS) == 56, f"old refs parsed {len(OLD_REFS)} != 56"

IB, IE, BB, BE = "\u00abi\u00bb", "\u00ab/i\u00bb", "\u00abb\u00bb", "\u00ab/b\u00bb"
def J(x):  # italic journal
    return IB + x + IE
def V(x):  # bold volume + comma
    return BB + x + BE

NEW_REFS = [
'Regev, A. et al. The Human Cell Atlas. ' + J('eLife') + ' ' + V('6,') + ' e27041 (2017).',
'Korsunsky, I. et al. Fast, sensitive and accurate integration of single-cell data with Harmony. ' + J('Nat. Methods') + ' ' + V('16,') + ' 1289\u20131296 (2019).',
'Lopez, R., Regier, J., Cole, M. B., Jordan, M. I. & Yosef, N. Deep generative modeling for single-cell transcriptomics. ' + J('Nat. Methods') + ' ' + V('15,') + ' 1053\u20131058 (2018).',
'Rosen, Y. et al. Toward universal cell embeddings: integrating single-cell RNA-seq datasets across species with SATURN. ' + J('Nat. Methods') + ' ' + V('21,') + ' 1492\u20131500 (2024).',
'Tran, H. T. N. et al. A benchmark of batch-effect correction methods for single-cell RNA sequencing data. ' + J('Genome Biol.') + ' ' + V('21,') + ' 12 (2020).',
'Nei, M. & Gojobori, T. Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions. ' + J('Mol. Biol. Evol.') + ' ' + V('3,') + ' 418\u2013426 (1986).',
'Yang, Z. PAML 4: phylogenetic analysis by maximum likelihood. ' + J('Mol. Biol. Evol.') + ' ' + V('24,') + ' 1586\u20131591 (2007).',
'Tabula Muris Consortium. Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris. ' + J('Nature') + ' ' + V('562,') + ' 367\u2013372 (2018).',
'Tabula Sapiens Consortium. The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. ' + J('Science') + ' ' + V('376,') + ' eabl4896 (2022).',
'Cancer Genome Atlas Research Network. Comprehensive molecular profiling of lung adenocarcinoma. ' + J('Nature') + ' ' + V('511,') + ' 543\u2013550 (2014).',
'Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. ' + J('Nature') + ' ' + V('490,') + ' 61\u201370 (2012).',
'Siletti, K. et al. Transcriptomic diversity of cell types across the adult human brain. ' + J('Science') + ' ' + V('382,') + ' eadd7046 (2023).',
'Hounkpe, B. W., Chenou, F., de Lima, F. & De Paula, E. V. HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate reference transcripts by mining massive RNA-seq datasets. ' + J('Nucleic Acids Res.') + ' ' + V('49,') + ' D947\u2013D955 (2021).',
'Kang, H. M. et al. Multiplexed droplet single-cell RNA-sequencing using natural genetic variation. ' + J('Nat. Biotechnol.') + ' ' + V('36,') + ' 89\u201394 (2018).',
'Edmondson, H. A. & Steiner, P. E. Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies. ' + J('Cancer') + ' ' + V('7,') + ' 462\u2013503 (1954).',
'Perou, C. M. et al. Molecular portraits of human breast tumours. ' + J('Nature') + ' ' + V('406,') + ' 747\u2013752 (2000).',
'Parker, J. S. et al. Supervised risk predictor of breast cancer based on intrinsic subtypes. ' + J('J. Clin. Oncol.') + ' ' + V('27,') + ' 1160\u20131167 (2009).',
'W\u00e4lchli, T. et al. Single-cell atlas of the human brain vasculature across development, adulthood and disease. ' + J('Nature') + ' ' + V('632,') + ' 603\u2013613 (2024).',
'Pfau, S. J. et al. Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells. ' + J('Nat. Neurosci.') + ' ' + V('27,') + ' 1892\u20131903 (2024).',
'Jones, H. E. et al. Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature. ' + J('Development') + ' ' + V('150,') + ' dev201805 (2023).',
'Tan, Y. L., Yuan, Y. & Tian, L. Microglial regional heterogeneity and its role in the brain. ' + J('Mol. Psychiatry') + ' ' + V('25,') + ' 351\u2013367 (2020).',
'Barry-Carroll, L. & Gomez-Nicola, D. The molecular determinants of microglial developmental dynamics. ' + J('Nat. Rev. Neurosci.') + ' ' + V('25,') + ' 414\u2013427 (2024).',
'Menassa, D. A. et al. The spatiotemporal dynamics of microglia across the human lifespan. ' + J('Dev. Cell') + ' ' + V('57,') + ' 2127\u20132139.e6 (2022).',
'Barry-Carroll, L. et al. Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling. ' + J('Cell Rep.') + ' ' + V('42,') + ' 112425 (2023).',
'Tsai, H. H. et al. Oligodendrocyte precursors migrate along vasculature in the developing nervous system. ' + J('Science') + ' ' + V('351,') + ' 379\u2013384 (2016).',
'Su, Y. et al. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development. ' + J('Neuron') + ' ' + V('111,') + ' 190\u2013201.e8 (2023).',
'Foerster, S. et al. Developmental origin of oligodendrocytes determines their function in the adult brain. ' + J('Nat. Neurosci.') + ' ' + V('27,') + ' 1545\u20131554 (2024).',
'Reeber, S. L., Arancillo, M. & Sillitoe, R. V. Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum. ' + J('Cerebellum') + ' ' + V('17,') + ' 392\u2013403 (2018).',
'Yang, L. et al. Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum. ' + J('Cell Discov.') + ' ' + V('10,') + ' 22 (2024).',
'Zhang, Y. et al. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. ' + J('EMBO J.') + ' ' + V('43,') + ' 5114\u20135140 (2024).',
'Vandesompele, J. et al. Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. ' + J('Genome Biol.') + ' ' + V('3,') + ' RESEARCH0034 (2002).',
'Eisenberg, E. & Levanon, E. Y. Human housekeeping genes, revisited. ' + J('Trends Genet.') + ' ' + V('29,') + ' 569\u2013574 (2013).',
'Elowitz, M. B., Levine, A. J., Siggia, E. D. & Swain, P. S. Stochastic gene expression in a single cell. ' + J('Science') + ' ' + V('297,') + ' 1183\u20131186 (2002).',
'Newman, J. R. S. et al. Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise. ' + J('Nature') + ' ' + V('441,') + ' 840\u2013846 (2006).',
'Raj, A. & van Oudenaarden, A. Nature, nurture, or chance: stochastic gene expression variation and its consequences on individual cellular fitness. ' + J('Cell') + ' ' + V('135,') + ' 216\u2013226 (2008).',
'Tarashansky, A. J. et al. Mapping single-cell atlases throughout Metazoa unravels cell type evolution. ' + J('eLife') + ' ' + V('10,') + ' e66747 (2021).',
'Jiang, J. et al. CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions. ' + J('Brief. Bioinform.') + ' ' + V('25,') + ' bbae283 (2024).',
'Skinnider, M. A. et al. Cell type prioritization in single-cell data. ' + J('Nat. Biotechnol.') + ' ' + V('39,') + ' 30\u201334 (2021).',
'Waxman, S. & Wurmbach, E. De-regulation of common housekeeping genes in hepatocellular carcinoma. ' + J('BMC Genomics') + ' ' + V('8,') + ' 243 (2007).',
'Bakken, T. E. et al. Comparative cellular analysis of motor cortex in human, marmoset and mouse. ' + J('Nature') + ' ' + V('598,') + ' 111\u2013119 (2021).',
'Marques, S. et al. Oligodendrocyte heterogeneity in the mouse juvenile and adult central nervous system. ' + J('Science') + ' ' + V('352,') + ' 1326\u20131329 (2016).',
'Spitzer, S. O. et al. Oligodendrocyte progenitor cells become regionally diverse and heterogeneous with age. ' + J('Neuron') + ' ' + V('101,') + ' 459\u2013471.e5 (2019).',
'Luecken, M. D. & Theis, F. J. Current best practices in single-cell RNA-seq analysis: a tutorial. ' + J('Mol. Syst. Biol.') + ' ' + V('15,') + ' e8746 (2019).',
'Lin, J. Divergence measures based on the Shannon entropy. ' + J('IEEE Trans. Inf. Theory') + ' ' + V('37,') + ' 145\u2013151 (1991).',
'Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. ' + J('J. R. Stat. Soc. Series B Stat. Methodol.') + ' ' + V('57,') + ' 289\u2013300 (1995).',
'Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. ' + J('Genome Biol.') + ' ' + V('19,') + ' 15 (2018).',
'Hao, Y. et al. Integrated analysis of multimodal single-cell data. ' + J('Cell') + ' ' + V('184,') + ' 3573\u20133587 (2021).',
'Hao, Y. et al. Dictionary learning for integrative, multimodal and scalable single-cell analysis. ' + J('Nat. Biotechnol.') + ' ' + V('42,') + ' 293\u2013304 (2024).',
'Weinstein, J. N. et al. The Cancer Genome Atlas Pan-Cancer analysis project. ' + J('Nat. Genet.') + ' ' + V('45,') + ' 1113\u20131120 (2013).',
'Colaprico, A. et al. TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. ' + J('Nucleic Acids Res.') + ' ' + V('44,') + ' e71 (2016).',
'Cerami, E. et al. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. ' + J('Cancer Discov.') + ' ' + V('2,') + ' 401\u2013404 (2012).',
'Waskom, M. L. seaborn: statistical data visualization. ' + J('J. Open Source Softw.') + ' ' + V('6,') + ' 3021 (2021).',
'Pedregosa, F. et al. Scikit-learn: machine learning in Python. ' + J('J. Mach. Learn. Res.') + ' ' + V('12,') + ' 2825\u20132830 (2011).',
'Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman and Hall/CRC, 1994).',
'CZI Cell Science Program. CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data. ' + J('Nucleic Acids Res.') + ' ' + V('53,') + ' D886\u2013D900 (2025).',
'Liberzon, A. et al. The Molecular Signatures Database Hallmark Gene Set Collection. ' + J('Cell Syst.') + ' ' + V('1,') + ' 417\u2013425 (2015).',
]
assert len(NEW_REFS) == 56

refs_code = "_refs_nc = [\n" + "\n".join(repr(e) + "," for e in NEW_REFS) + "\n]\n"
rep_span("refs list _refs_nar->_refs_nc", "_refs_nar = [", "\n]\n", refs_code, keep_end=False)

OLD_REF_P = '''def ref_p_nar(text):
    """Add a NAR-formatted reference paragraph."""
    para = doc.add_paragraph(text)
    para.paragraph_format.line_spacing = 1.15
    para.paragraph_format.space_after = Pt(3)
    for run in para.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(10)
        set_black(run)
    return para'''
NEW_REF_P = '''def _ref_run(para, text, bold=False, italic=False):
    run = para.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(10)
    set_black(run)
    run.bold = bold
    run.italic = italic
    return run

_REF_MARK_RE = re.compile(r'\u00ab([ib])\u00bb(.*?)\u00ab/\\1\u00bb')

def ref_p_nc(text):
    """Add a Nature-formatted reference paragraph.
    Entry markup: «i»..«/i» = italic journal, «b»..«/b» = bold volume."""
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = 1.15
    para.paragraph_format.space_after = Pt(3)
    pos = 0
    for m in _REF_MARK_RE.finditer(text):
        if m.start() > pos:
            _ref_run(para, text[pos:m.start()])
        _ref_run(para, m.group(2), bold=(m.group(1) == 'b'), italic=(m.group(1) == 'i'))
        pos = m.end()
    if pos < len(text):
        _ref_run(para, text[pos:])
    return para'''
rep("ref_p_nar -> ref_p_nc", OLD_REF_P, NEW_REF_P)

# ---------------------------------------------------------------- 5. title page
rep("title (no colon, <=15 words)",
    "'CKI: a Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics'",
    "'CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics'")

# ---------------------------------------------------------------- 6. abstract 151 -> 149 words
rep("abstract trim", r"with power bounded to ~50\u2013200 cells per donor per condition.",
    r"with power bounded to ~50\u2013200 cells per donor.")
rep("abstract comment", "# ABSTRACT (GB Methodology: unstructured, single paragraph, ~145 words)",
    "# ABSTRACT (NC: unstructured, single paragraph, <=150 words)")

# ---------------------------------------------------------------- 7. delete Keywords block
OLD_KW = '''# ============================================================
# KEYWORDS (GB: 3-10 keywords, independent line after the abstract)
# ============================================================
kw = doc.add_paragraph()
run = kw.add_run('Keywords: cell-state divergence, housekeeping genes, Jensen-Shannon decomposition, baseline-normalized divergence, single-cell genomics')
run.font.name = 'Arial'
set_black(run)
run.font.size = Pt(11)
'''
rep("delete Keywords block", OLD_KW, "")

# ---------------------------------------------------------------- 8. Background -> Introduction
rep("heading Background->Introduction", "heading('Background', level=1)", "heading('Introduction', level=1)")
rep("intro comment", '# INTRODUCTION (NAR: "Introduction" instead of "Background")',
    '# INTRODUCTION (NC: manuscript must begin with the heading "Introduction")')
rep("body (Background)->(Introduction)", "stated with the concept definition (Background)",
    "stated with the concept definition (Introduction)")

# ---------------------------------------------------------------- 9. supplementary naming
rep_re("AF1: Fig. Sx -> Supplementary Fig.", r"Additional file 1: Fig\. S(\d+)", r"Supplementary Fig. \1", 17)
rep_re("bare Fig. Sx -> Supplementary Fig.", r"Fig\. S(\d+)", r"Supplementary Fig. \1", 1)
rep_re("AF1: Figure Sx. -> Supplementary Fig.", r"Additional file 1: Figure S(\d+)\.", r"Supplementary Fig. \1.", 13)
rep_re("AF1: Table Sx -> Supplementary Table", r"Additional file 1: Table S(\d+)", r"Supplementary Table \1", 4)
NOTE_MAP = [("3.12", "1"), ("3.21", "2"), ("3.5", "3"), ("3.20", "4"), ("3.22", "5"),
            ("3.15", "6"), ("3.13", "7"), ("5.2", "8"), ("3.16", "9"), ("3.17", "10"),
            ("3.14", "11"), ("4.6", "12"), ("5.1", "13"), ("3.23", "14"), ("3.6", "15")]
NOTE_PREF_COUNTS = {"3.12": 5, "3.21": 3, "3.5": 2, "3.20": 1, "3.22": 2, "3.15": 1,
                    "3.13": 2, "5.2": 2, "3.16": 6, "3.17": 2, "3.14": 2, "4.6": 3,
                    "5.1": 3, "3.23": 1, "3.6": 1}
NOTE_BARE_COUNTS = {"3.21": 1, "3.15": 1}
for old_id, new_id in NOTE_MAP:
    esc = old_id.replace(".", r"\.")
    rep_re(f"AF1: Note {old_id} -> Supplementary Note {new_id}",
           r"Additional file 1: Note " + esc + r"(?!\d)",
           f"Supplementary Note {new_id}", NOTE_PREF_COUNTS[old_id])
for old_id, new_id in NOTE_MAP:
    esc = old_id.replace(".", r"\.")
    expect = NOTE_BARE_COUNTS.get(old_id, 0)
    if expect:
        rep_re(f"bare Note {old_id} -> Supplementary Note {new_id}",
               r"Note " + esc + r"(?!\d)", f"Supplementary Note {new_id}", expect)
rep_re("bare 'in Additional file 1.' -> Supplementary Information",
       r" in Additional file 1\.", " in the Supplementary Information.", 3)
rep("AF2 reference renamed", "Additional file 2)", "Additional file 2: Reproducibility Guide)")

# ---------------------------------------------------------------- 10. panel labels lowercase
rep("Fig. 2B, C -> Fig. 2b, c", "Fig. 2B, C", "Fig. 2b, c")
rep("Fig. 2A -> Fig. 2a", "Fig. 2A", "Fig. 2a")
rep("Fig. 2C -> Fig. 2c", "Fig. 2C", "Fig. 2c")
rep("(A)->(a)", "(A)", "(a)", 15)
rep("(B)->(b)", "(B)", "(b)", 14)
rep("(C)->(c)", "(C)", "(c)", 8)
rep("(D)->(d)", "(D)", "(d)", 3)
rep("(E)->(e)", "(E)", "(e)", 1)
rep("Panel A -> panel a", "Panel A", "panel a")
rep("Panel B -> panel b", "Panel B", "panel b")

# ---------------------------------------------------------------- 11. structural deletions / renames
rep("delete Results L3 heading 1", "heading('Microglia: composition of the largest candidate share', level=3)\n", "")
rep("delete Results L3 heading 2", "heading('Oligodendrocytes: thalamo-temporal convergence', level=3)\n", "")
rep("delete Results L3 heading 3", "heading('Astrocytes, fibroblasts, and ependymal cells: sparse candidates', level=3)\n", "")
rep("delete Discussion L2 heading 1", "heading('When to use CKI versus standard metrics', level=2)\n", "")
rep("delete Discussion L2 heading 2", "heading('Practical usage guide', level=2)\n", "")
rep("delete Discussion L2 heading 3", "heading('Limitations', level=2)\n", "")
rep("conclusions comment", "# CONCLUSIONS (GB: required, before Methods)",
    "# Conclusions paragraph retained, merged into the end of Discussion (NC: no separate Conclusions section)")
rep("delete Conclusions heading", "heading('Conclusions', level=1)\n", "")
rep("Statistical reporting -> Statistics and reproducibility",
    "heading('Statistical reporting', level=2)", "heading('Statistics and reproducibility', level=2)")
rep("body xref Statistical reporting", "(see Statistical reporting)",
    "(see Statistics and reproducibility)")

# ---------------------------------------------------------------- 11b. round-2 fixes
# (1) Introduction final paragraph: "Here, we show ..." opening (NC convention)
rep("intro final paragraph 'Here, we show'",
    "p('We evaluated CKI across four scales. First, we calibrated",
    "p('Here, we show that CKI provides a baseline-normalized index of cell-state divergence across four scales. First, we calibrated")

# (2) Results L2 headings shortened to <=60 chars
rep("shorten L2 heading: ground-truth simulation",
    "heading('Ground-truth simulation dissociates specificity from sensitivity', level=2)",
    "heading('Ground-truth simulation: specificity versus sensitivity', level=2)")
rep("shorten L2 heading: fixed gene-panel ablation",
    r"heading('Fixed gene-panel ablation: rankings robust, absolute \u03c9 scheme-specific', level=2)",
    r"heading('Fixed-panel ablation: robust rankings, scheme-specific \u03c9', level=2)")
rep("shorten L2 heading: cancer analysis",
    "heading('Cancer analysis suggests apparent tumor homogeneity (exploratory)', level=2)",
    "heading('Cancer analysis: apparent tumor homogeneity (exploratory)', level=2)")
rep("shorten L2 heading: brain regional analysis",
    "heading('Brain regional analysis reveals cell-type divergence gradients', level=2)",
    "heading('Brain regional analysis reveals divergence gradients', level=2)")
rep("shorten L2 heading: anomalously similar pairs",
    "heading('Anomalously similar cell-type/region pairs: a hypothesis-generating screen', level=2)",
    "heading('Anomalously similar pairs: a hypothesis-generating screen', level=2)")

# (3) dangling cross-references to deleted Discussion subsections
rep("dangling xref: (Results; Limitations)",
    "(Results; Limitations)",
    "(Results; limitations are addressed in the Discussion)")
rep("dangling xref: operating window; Limitations",
    r"(operating window ~50\u2013200 cells; Limitations)",
    r"(operating window ~50\u2013200 cells; limitations are addressed in the Discussion)")
rep("dangling xref: RNA quality; Limitations",
    "RNA quality; Limitations)",
    "RNA quality; limitations discussed below)")
rep("results comment", "# RESULTS (NAR: placed AFTER Methods)", "# RESULTS")
rep("discussion comment", "# DISCUSSION (NAR: can merge Results and Discussion, but we keep separate)", "# DISCUSSION")
rep("methods comment", "# MATERIALS AND METHODS (NAR: placed BEFORE Results)", "# METHODS")
rep("format comment", "# == NAR formatting: single-spaced, Arial 11pt ==", "# == NC submission formatting: single-spaced, Arial 11pt ==")

# ---------------------------------------------------------------- 12. delete List of abbreviations
OLD_ABBR = '''# ============================================================
# LIST OF ABBREVIATIONS (GB: required when abbreviations are used)
# ============================================================
heading('List of abbreviations', level=1)
p('AUC, area under the ROC curve; BH, Benjamini-Hochberg; CKI, Cell-type Ka/Ks-inspired Index; CV, coefficient of variation; DE, differentially expressed; FDR, false discovery rate; GSVA, gene set variation analysis; HK, housekeeping; HVG, highly variable gene; IQR, interquartile range; JS, Jensen-Shannon; OPC, oligodendrocyte precursor cell; PAM50, prediction analysis of microarray 50; QC, quality control; ROC, receiver operating characteristic; SD, standard deviation; SES, standardized effect size; TCGA, The Cancer Genome Atlas.')
'''
rep("delete List of abbreviations", OLD_ABBR, "")

# ---------------------------------------------------------------- 13. Declarations restructure
OLD_DECL_A = '''# ============================================================
# DECLARATIONS (GB: all subheadings required)
# ============================================================
heading('Declarations', level=1)

heading('Ethics approval and consent to participate', level=2)
p('Not applicable. This study analysed only publicly available, de-identified datasets and did not involve human participants, human tissue, or animals.')

heading('Consent for publication', level=2)
p('Not applicable.')

'''
rep("delete Declarations/Ethics/Consent", OLD_DECL_A, "")

NEW_BLOCK_B = r'''# ============================================================
# DATA AVAILABILITY / CODE AVAILABILITY (NC: after Methods, before References;
# no literature citations inside either section)
# ============================================================
heading('Data availability', level=1)
p('Tabula Muris data: GEO accession GSE109774. Tabula Sapiens data: CZ CELLxGENE Discover (https://cellxgene.cziscience.com/, accessed July 2025). TCGA data: NCI Genomic Data Commons (https://portal.gdc.cancer.gov/). HRT Atlas (optional human/mouse housekeeping-gene reference): https://www.housekeeping.unicamp.br. Human brain atlas: CZ CELLxGENE Discover, collection ID 283d65eb-dd53-496d-adb7-7570c7caa443 (https://cellxgene.cziscience.com/collections/283d65eb-dd53-496d-adb7-7570c7caa443, accessed July 2025). Kang et al. IFN-\u03b2-stimulated PBMC data: GEO accession GSE96583. BRCA PAM50 subtype assignments: cBioPortal (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute). MSigDB Hallmark gene sets: Broad Institute Molecular Signatures Database.')

heading('Code availability', level=1)
p('The CKI source code (v0.5.0) is publicly available at https://github.com/zhanglknt/CKI-cell-type-identification (tag v0.5.0) under the MIT License. A permanent archival copy has been deposited at Zenodo (concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.0: 10.5281/zenodo.22735744). The package requires Python \u22653.10 and runs on Linux, macOS, and Windows. A Dockerfile is provided in the repository for containerized reproducibility. All analysis notebooks and processed data matrices are available in the same GitHub repository (tag v0.5.0) and are included in the Zenodo archive (concept DOI: 10.5281/zenodo.20405458).')

# ============================================================
# REFERENCES (NC: Nature style; superscript citations in text)
# ============================================================
heading('References', level=1)

for i, ref in enumerate(_refs_nc, 1):
    ref_p_nc(f'{i}. {ref}')
'''
rep_span("Availability -> Data/Code availability + References block",
         "heading('Availability of data and materials', level=2)",
         "\n\nheading('Competing interests', level=2)",
         NEW_BLOCK_B)

NEW_BLOCK_C = '''# ============================================================
# ACKNOWLEDGEMENTS / AUTHOR CONTRIBUTIONS / COMPETING INTERESTS
# (NC fixed order, after References; Funding merged into Acknowledgements)
# ============================================================
heading('Acknowledgements', level=1)
p('This work was supported by the National Natural Science Foundation of China (NSFC) under grant number 32370682. We thank the Tabula Muris Consortium, Tabula Sapiens Consortium, TCGA Research Network, and the Siletti et al. brain atlas team for making their data publicly available. We also thank the developers of scanpy, scipy, scikit-learn, and the broader open-source scientific Python ecosystem for the computational infrastructure that made this work possible. We are grateful to the HRT Atlas team for maintaining the housekeeping gene reference resource.')

heading('Author contributions', level=1)
p('X.W. performed the analyses and wrote the first draft of the manuscript. L.Z. conceived and supervised the study, developed the CKI algorithm, acquired funding, and finalized the manuscript. Both authors read and approved the final manuscript.')

heading('Competing interests', level=1)
p('The authors declare no competing interests.')

p('Supplementary Information is available for this paper: Supplementary Notes 1\u201315, Supplementary Figs. 1\u201313, and Supplementary Tables 1\u20134 (accompanying CKI_Supplementary document). Additional file 2: Reproducibility Guide provides step-by-step instructions, the verified computational environment, and spot-check values for reproducing all analyses, figures, and tables reported in this work.')

p('Correspondence and requests for materials should be addressed to L.Z.')'''
rep_span("Competing/Funding/Authors/Ack -> Ack/AC/CI/SI (NC order)",
         "heading('Competing interests', level=2)",
         "maintaining the housekeeping gene reference resource.')",
         NEW_BLOCK_C, keep_end=False)

rep_span("delete Additional files block",
         "# ============================================================\n# ADDITIONAL FILES (GB: list file name / format / title / description)",
         "reported in this work.')",
         "", keep_end=False)

OLD_REFS_LOOP = '''# ============================================================
# REFERENCES (GB: Vancouver, square-bracket citations)
# ============================================================
heading('References', level=1)

for i, ref in enumerate(_refs_nar, 1):
    ref_p_nar(f'{i}. {ref}')
'''
rep("delete old References loop (moved)", OLD_REFS_LOOP, "")

# supplementary figure legends heading removed (NC: legends follow main figure legends)
rep("supp legends comment", "# Supplementary Figure legends (NAR convention)",
    "# Supplementary figure legends (NC: follows the main figure legends)")
rep("delete supp legends heading", "heading('Additional file 1: Supplementary figure legends', level=1)\n", "")

# ---------------------------------------------------------------- 14. save path + citation count assertion
rep("save path", 'CKI_Manuscript_GB.docx', 'CKI_Manuscript_NC.docx')
rep("citation count assertion", "# == Save ==",
    "# == Save ==\nassert _cite_sup_count == 69, f'Expected 69 superscripted citation groups, got {_cite_sup_count}'\nprint(f'Superscripted citation groups: {_cite_sup_count}')")

# ---------------------------------------------------------------- final source-level assertions
def absent(label, s):
    assert s not in src, f"residual found: {label}"
    print(f"OK  absent: {label}")

def present_count(label, s, expect):
    n = src.count(s)
    assert n == expect, f"{label}: {n} != {expect}"
    print(f"OK  count {label} = {n}")

absent("Additional file 1", "Additional file 1")
absent("Fig. S", "Fig. S")
absent("Table S", "Table S")
assert not re.search(r"Note \d\.\d", src), "residual Note x.y"
print("OK  absent: Note x.y")
absent("_refs_nar", "_refs_nar")
absent("ref_p_nar", "ref_p_nar")
absent("CKI_Manuscript_GB", "CKI_Manuscript_GB")
absent("heading('Background'", "heading('Background'")
absent("heading('Conclusions'", "heading('Conclusions'")
absent("List of abbreviations heading", "heading('List of abbreviations'")
absent("heading('Declarations'", "heading('Declarations'")
absent("Keywords:", "Keywords:")
absent("Statistical reporting", "Statistical reporting")
absent("(A)", "(A)"); absent("(B)", "(B)"); absent("(C)", "(C)")
absent("(D)", "(D)"); absent("(E)", "(E)")
present_count("(X) retained", "(X)", 1)
absent("dangling '(Results; Limitations)'", "(Results; Limitations)")
absent("dangling '; Limitations)'", "; Limitations)")
present_count("Here, we show opening", "Here, we show that CKI provides", 1)
for h in ["Ground-truth simulation: specificity versus sensitivity",
          "Cancer analysis: apparent tumor homogeneity (exploratory)",
          "Brain regional analysis reveals divergence gradients",
          "Anomalously similar pairs: a hypothesis-generating screen"]:
    present_count(f"short heading: {h[:40]}", f"heading('{h}', level=2)", 1)
present_count("short heading: Fixed-panel ablation",
              "heading('Fixed-panel ablation: robust rankings, scheme-specific \\u03c9', level=2)", 1)
present_count("AF2 renamed", "Additional file 2: Reproducibility Guide", 2)
present_count("Supplementary Fig. refs", "Supplementary Fig. ", 31)
present_count("Supplementary Table refs", "Supplementary Table ", 4)
n_note = len(re.findall(r"Supplementary Note \d+", src))
assert n_note == 38, f"Supplementary Note refs {n_note} != 38"
print(f"OK  Supplementary Note refs = {n_note}")
for lid, nid in NOTE_MAP:
    n = len(re.findall(r"Supplementary Note " + nid + r"(?!\d)", src))
    print(f"    Supplementary Note {nid} (old {lid}): {n}")

# abstract word count in new source
m_abs = re.search(r"p\('Standard distance metrics conflate.*?'\)\n", src, re.S)
assert m_abs, "abstract anchor"
n_words = len(m_abs.group(0)[3:-3].split())
assert n_words <= 150, f"abstract {n_words} words"
counts["abstract_words"] = n_words
print(f"OK  abstract words = {n_words}")

# title word count
n_tw = len("CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics".split())
assert n_tw <= 15
counts["title_words"] = n_tw
print(f"OK  title words = {n_tw}")

# ---------------------------------------------------------------- write + compile
OUT_P.write_text(src, encoding="utf-8")
print(f"\nWritten: {OUT_P}")
py_compile.compile(str(OUT_P), doraise=True)
print("py_compile OK")

COUNTS_P.write_text(json.dumps({
    "counts": counts,
    "old_refs": OLD_REFS,
    "new_refs": NEW_REFS,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Counts JSON: {COUNTS_P}")