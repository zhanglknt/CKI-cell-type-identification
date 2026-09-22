"""
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
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from pathlib import Path
import re

# Load all manuscript data dynamically from CSV files
from _load_manuscript_data import get_manuscript_data
DATA = get_manuscript_data()

# Shorthand accessors
_ds = DATA['datasets']
_mc = DATA['mouse_calibration']
_h = DATA['human']
_sc = DATA['spearman_corr']
_tc = DATA['tcga']
# v49 analysis caliber: sample counts that actually entered the linear-
# normalization pair table (nc49_tcga_pancancer.csv); 33 expression-matrix
# samples were excluded for missing barcode matching or pair coverage.
import pandas as _pd
_tc49 = _pd.read_csv(Path(__file__).resolve().parent / "results" / "nc49_tcga_pancancer.csv").set_index('cancer')
_tc = dict(_tc)
_tc['n_total'] = int(_tc49['n_tumor'].sum() + _tc49['n_normal'].sum())
for _c in _tc['cancers']:
    _c['n_tumor'] = int(_tc49.loc[_c['name'], 'n_tumor'])
    _c['n_normal'] = int(_tc49.loc[_c['name'], 'n_normal'])
_br = DATA['brain']
_br_ct = _br['cell_types']
_au = DATA['table1_auc']
_sb = DATA['sweep']
_co = DATA['cross_organ_spearman']
_bb = DATA['bootstrap']['brain']

# Phase B: Statistical upgrade data
import json as _json
import pandas as pd
RESULTS_DIR = Path(__file__).parent / "results"
_phaseB_ci = pd.read_csv(RESULTS_DIR / "phaseB_bootstrap_cis.csv") if (RESULTS_DIR / "phaseB_bootstrap_cis.csv").exists() else None
with open(RESULTS_DIR / "phaseB_omega_distribution.json") as _f:
    _phaseB_dist = _json.load(_f)
with open(RESULTS_DIR / "phaseB_adaptive_analysis.json") as _f:
    _phaseB_adaptive = _json.load(_f)
_phaseB_residual = None
if (RESULTS_DIR / "superseded" / "phaseB_residual_pervisign.csv").exists():
    _phaseB_residual = pd.read_csv(RESULTS_DIR / "superseded" / "phaseB_residual_pervisign.csv")

# Phase C: Methodological reinforcement data
_phaseC_cal = None
_phaseC_dim = None
_phaseC_kn = None
if (RESULTS_DIR / "superseded" / "phaseC_calibration.json").exists():
    with open(RESULTS_DIR / "superseded" / "phaseC_calibration.json") as _f:
        _phaseC_cal = _json.load(_f)
if (RESULTS_DIR / "phaseC_dimensionality.json").exists():
    with open(RESULTS_DIR / "phaseC_dimensionality.json") as _f:
        _phaseC_dim = _json.load(_f)
if (RESULTS_DIR / "phaseC_kn_variability.json").exists():
    with open(RESULTS_DIR / "phaseC_kn_variability.json") as _f:
        _phaseC_kn = _json.load(_f)

# C-A fix: k_f/k_n correlation decomposition (reviewer_decomposition_correlations.csv)
_decomp = None
if (RESULTS_DIR / "reviewer_decomposition_correlations.csv").exists():
    _decomp = pd.read_csv(RESULTS_DIR / "reviewer_decomposition_correlations.csv")
    _decomp = _decomp[_decomp['metric'] != 'corr(k_f, k_n)']

t2 = DATA['table2_data']
tcga_cancers = _tc['cancers']
min_c = min(tcga_cancers, key=lambda x: x['nn_tt_ratio'])
max_c = max(tcga_cancers, key=lambda x: x['nn_tt_ratio'])
th = _br['residual_thresholds']

mac = [r for r in t2 if 'Macrophage' in r[0]][0]
# next well-sampled cell type after t2[0..2] that is not the duplicated macrophage row
t2_next = next((r for r in t2 if int(r[3]) >= 5 and r[0] != mac[0]
                and r not in t2[:3]), t2[3])
last2 = t2[-2:]
t2_sparse = [r for r in t2 if int(r[3]) < 5]

def find_ct(name):
    for ct in _br_ct:
        if name.lower() in ct['name'].lower():
            return ct
    return None

sbg = sorted(_br_ct, key=lambda x: x['omega_mean'])
opc = find_ct('oligodendrocyte precursor')
astro = find_ct('astrocyte')
oligo_ct = find_ct('oligodendrocyte')
bergmann_ct = find_ct('bergmann')

tcga_detail = '; '.join([
    f"{c['name'].replace('TCGA-','')}: {c['n_tumor']} tumor + {c['n_normal']} normal"
    for c in _tc['cancers']
])

doc = Document()

# == NC submission formatting: single-spaced, Arial 11pt ==
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(11)
style.font.color.rgb = RGBColor(0,0,0)
style.paragraph_format.line_spacing = 1.15  # single spacing
style.paragraph_format.space_after = Pt(0)

# Page margins
section = doc.sections[0]
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)

# == Helpers ==
def set_black(run):
    run.font.color.rgb = RGBColor(0,0,0)

def set_superscript(run):
    rPr = run._element.get_or_add_rPr()
    for old in rPr.findall(qn('w:vertAlign')):
        rPr.remove(old)
    va = rPr.makeelement(qn('w:vertAlign'), {qn('w:val'): 'superscript'})
    rPr.append(va)

def heading(text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = 'Arial'
        set_black(run)
        run.font.size = Pt([14, 12, 11][level-1])
        rPr = run._element.get_or_add_rPr()
        for old in rPr.findall(qn('w:b')):
            rPr.remove(old)
        b = rPr.makeelement(qn('w:b'), {})
        rPr.append(b)
    p.paragraph_format.space_before = Pt(21)
    p.paragraph_format.space_after = Pt(8)
    return p

_CITE_GROUP_RE = re.compile(r'\[(\d+(?:\s*[,\-]\s*\d+)*)\]')
_cite_sup_count = 0

def _is_citation_group(content):
    # Guard: only convert groups whose parts are all integers in 1-57.
    # This excludes 95% CI brackets such as [7.37, 8.02] (decimals),
    # [0, 1] (JS range) and [12, 74] (bootstrap CI).
    try:
        nums = [int(x) for x in re.split(r'[,\-]', content)]
    except ValueError:
        return False
    return all(1 <= n <= 57 for n in nums)

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
    return para

# == Tables -> standalone Excel (tables as separate file, not in the DOCX) ==
def write_tables_xlsx():
    from openpyxl import Workbook
    from openpyxl.styles import Font
    auc = DATA['table1_auc']
    ds = DATA['datasets']
    wb = Workbook()
    t2d = DATA['table2_data']
    has_sep = any(int(r[3]) < 5 for r in t2d) and any(int(r[3]) >= 5 for r in t2d)
    ws2 = wb.active
    ws2.title = 'Table 1'
    cap2 = (f"Table 1. Cross-organ conservation ranking by cell type (Tabula Sapiens, "
            f"n={DATA['cross_organ_n_total']} same-cell-type cross-organ pairs). Well-sampled "
            f"cell types (n \u2265 5 cross-organ pairs) are ranked first by mean \u03c9; "
            f"sparsely sampled cell types (n < 5 pairs; SD shown only where n > 1) are listed "
            f"below the divider, and their rankings should be interpreted as suggestive only. "
            f"Because the k_n anchor is not calibrated across cell types (Discussion), cross-type gaps in mean \u03c9 are descriptive rather than calibrated. "
            f"k_f-only controls for this ranking are reported in Supplementary Note 9.")
    ws2['A1'] = cap2
    ws2['A1'].font = Font(bold=True)
    ws2.append([])
    ws2.append(['Cell type', 'Mean \u03c9', 'SD', 'n pairs'])
    for c in ws2[3]:
        c.font = Font(bold=True)
    sep_done = False
    for (name, mean_w, sd, n) in t2d:
        if has_sep and not sep_done and int(n) < 5:
            ws2.append(['\u2014 Sparsely sampled (n < 5 pairs): interpret with caution \u2014', '', '', ''])
            sep_done = True
        ws2.append([name, mean_w, sd, n])
    ws2.column_dimensions['A'].width = 34
    for col in 'BCD':
        ws2.column_dimensions[col].width = 10
    out_x = str(PROJECT_ROOT / "results" / "CKI_Tables_NC.xlsx")
    wb.save(out_x)
    print(f"Saved: {out_x}")

# ============================================================
# NC REFERENCE LIST (Nature style)
# Author, A. B., Author, C. D. & Author, E. F. Title. *Journal* **Vol**, pages (year).
# >=6 authors -> first author + et al.; <=5 authors all listed.
# Markup: «i»..«/i» = italic journal, «b»..«/b» = bold volume + comma.
# ============================================================

_refs_nc = [
'Regev, A. et al. The Human Cell Atlas. «i»eLife«/i» «b»6,«/b» e27041 (2017).',
'Korsunsky, I. et al. Fast, sensitive and accurate integration of single-cell data with Harmony. «i»Nat. Methods«/i» «b»16,«/b» 1289–1296 (2019).',
'Lopez, R., Regier, J., Cole, M. B., Jordan, M. I. & Yosef, N. Deep generative modeling for single-cell transcriptomics. «i»Nat. Methods«/i» «b»15,«/b» 1053–1058 (2018).',
'Rosen, Y. et al. Toward universal cell embeddings: integrating single-cell RNA-seq datasets across species with SATURN. «i»Nat. Methods«/i» «b»21,«/b» 1492–1500 (2024).',
'Tran, H. T. N. et al. A benchmark of batch-effect correction methods for single-cell RNA sequencing data. «i»Genome Biol.«/i» «b»21,«/b» 12 (2020).',
'Nei, M. & Gojobori, T. Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions. «i»Mol. Biol. Evol.«/i» «b»3,«/b» 418–426 (1986).',
'Yang, Z. PAML 4: phylogenetic analysis by maximum likelihood. «i»Mol. Biol. Evol.«/i» «b»24,«/b» 1586–1591 (2007).',
'Tabula Muris Consortium. Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris. «i»Nature«/i» «b»562,«/b» 367–372 (2018).',
'Tabula Sapiens Consortium. The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. «i»Science«/i» «b»376,«/b» eabl4896 (2022).',
'Cancer Genome Atlas Research Network. Comprehensive molecular profiling of lung adenocarcinoma. «i»Nature«/i» «b»511,«/b» 543–550 (2014).',
'Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. «i»Nature«/i» «b»490,«/b» 61–70 (2012).',
'Siletti, K. et al. Transcriptomic diversity of cell types across the adult human brain. «i»Science«/i» «b»382,«/b» eadd7046 (2023).',
'Hounkpe, B. W., Chenou, F., de Lima, F. & De Paula, E. V. HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate reference transcripts by mining massive RNA-seq datasets. «i»Nucleic Acids Res.«/i» «b»49,«/b» D947–D955 (2021).',
'Kang, H. M. et al. Multiplexed droplet single-cell RNA-sequencing using natural genetic variation. «i»Nat. Biotechnol.«/i» «b»36,«/b» 89–94 (2018).',
'Liberzon, A. et al. The Molecular Signatures Database Hallmark Gene Set Collection. «i»Cell Syst.«/i» «b»1,«/b» 417–425 (2015).',
'Wälchli, T. et al. Single-cell atlas of the human brain vasculature across development, adulthood and disease. «i»Nature«/i» «b»632,«/b» 603–613 (2024).',
'Pfau, S. J. et al. Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells. «i»Nat. Neurosci.«/i» «b»27,«/b» 1892–1903 (2024).',
'Jones, H. E. et al. Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature. «i»Development«/i» «b»150,«/b» dev201805 (2023).',
'Tan, Y. L., Yuan, Y. & Tian, L. Microglial regional heterogeneity and its role in the brain. «i»Mol. Psychiatry«/i» «b»25,«/b» 351–367 (2020).',
'Barry-Carroll, L. & Gomez-Nicola, D. The molecular determinants of microglial developmental dynamics. «i»Nat. Rev. Neurosci.«/i» «b»25,«/b» 414–427 (2024).',
'Menassa, D. A. et al. The spatiotemporal dynamics of microglia across the human lifespan. «i»Dev. Cell«/i» «b»57,«/b» 2127–2139.e6 (2022).',
'Barry-Carroll, L. et al. Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling. «i»Cell Rep.«/i» «b»42,«/b» 112425 (2023).',
'Tsai, H. H. et al. Oligodendrocyte precursors migrate along vasculature in the developing nervous system. «i»Science«/i» «b»351,«/b» 379–384 (2016).',
'Su, Y. et al. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development. «i»Neuron«/i» «b»111,«/b» 190–201.e8 (2023).',
'Foerster, S. et al. Developmental origin of oligodendrocytes determines their function in the adult brain. «i»Nat. Neurosci.«/i» «b»27,«/b» 1545–1554 (2024).',
'Reeber, S. L., Arancillo, M. & Sillitoe, R. V. Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum. «i»Cerebellum«/i» «b»17,«/b» 392–403 (2018).',
'Yang, L. et al. Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum. «i»Cell Discov.«/i» «b»10,«/b» 22 (2024).',
'Zhang, Y. et al. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. «i»EMBO J.«/i» «b»43,«/b» 5114–5140 (2024).',
'Vandesompele, J. et al. Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. «i»Genome Biol.«/i» «b»3,«/b» RESEARCH0034 (2002).',
'Eisenberg, E. & Levanon, E. Y. Human housekeeping genes, revisited. «i»Trends Genet.«/i» «b»29,«/b» 569–574 (2013).',
'Elowitz, M. B., Levine, A. J., Siggia, E. D. & Swain, P. S. Stochastic gene expression in a single cell. «i»Science«/i» «b»297,«/b» 1183–1186 (2002).',
'Newman, J. R. S. et al. Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise. «i»Nature«/i» «b»441,«/b» 840–846 (2006).',
'Raj, A. & van Oudenaarden, A. Nature, nurture, or chance: stochastic gene expression and its consequences. «i»Cell«/i» «b»135,«/b» 216–226 (2008).',
'McDonald, J. H. & Kreitman, M. Adaptive protein evolution at the Adh locus in Drosophila. «i»Nature«/i» «b»351,«/b» 652–654 (1991).',
'Tarashansky, A. J. et al. Mapping single-cell atlases throughout Metazoa unravels cell type evolution. «i»eLife«/i» «b»10,«/b» e66747 (2021).',
'Jiang, J. et al. CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions using single-cell RNA sequencing data. «i»Brief. Bioinform.«/i» «b»25,«/b» bbae283 (2024).',
'Skinnider, M. A. et al. Cell type prioritization in single-cell data. «i»Nat. Biotechnol.«/i» «b»39,«/b» 30–34 (2021).',
'Waxman, S. & Wurmbach, E. De-regulation of common housekeeping genes in hepatocellular carcinoma. «i»BMC Genomics«/i» «b»8,«/b» 243 (2007).',
'Bakken, T. E. et al. Comparative cellular analysis of motor cortex in human, marmoset and mouse. «i»Nature«/i» «b»598,«/b» 111–119 (2021).',
'Marques, S. et al. Oligodendrocyte heterogeneity in the mouse juvenile and adult central nervous system. «i»Science«/i» «b»352,«/b» 1326–1329 (2016).',
'Spitzer, S. O. et al. Oligodendrocyte progenitor cells become regionally diverse and heterogeneous with age. «i»Neuron«/i» «b»101,«/b» 459–471.e5 (2019).',
'Luecken, M. D. & Theis, F. J. Current best practices in single-cell RNA-seq analysis: a tutorial. «i»Mol. Syst. Biol.«/i» «b»15,«/b» e8746 (2019).',
'Lin, J. Divergence measures based on the Shannon entropy. «i»IEEE Trans. Inf. Theory«/i» «b»37,«/b» 145–151 (1991).',
'Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. «i»J. R. Stat. Soc. Series B Stat. Methodol.«/i» «b»57,«/b» 289–300 (1995).',
'Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. «i»Genome Biol.«/i» «b»19,«/b» 15 (2018).',
'Hao, Y. et al. Integrated analysis of multimodal single-cell data. «i»Cell«/i» «b»184,«/b» 3573–3587.e29 (2021).',
'Hao, Y. et al. Dictionary learning for integrative, multimodal and scalable single-cell analysis. «i»Nat. Biotechnol.«/i» «b»42,«/b» 293–304 (2024).',
'CZI Cell Science Program. CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data. «i»Nucleic Acids Res.«/i» «b»53,«/b» D886–D900 (2025).',
'Weinstein, J. N. et al. The Cancer Genome Atlas Pan-Cancer analysis project. «i»Nat. Genet.«/i» «b»45,«/b» 1113–1120 (2013).',
'Colaprico, A. et al. TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. «i»Nucleic Acids Res.«/i» «b»44,«/b» e71 (2016).',
'Cerami, E. et al. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. «i»Cancer Discov.«/i» «b»2,«/b» 401–404 (2012).',
'Perou, C. M. et al. Molecular portraits of human breast tumours. «i»Nature«/i» «b»406,«/b» 747–752 (2000).',
'Parker, J. S. et al. Supervised risk predictor of breast cancer based on intrinsic subtypes. «i»J. Clin. Oncol.«/i» «b»27,«/b» 1160–1167 (2009).',
'Edmondson, H. A. & Steiner, P. E. Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies. «i»Cancer«/i» «b»7,«/b» 462–503 (1954).',
'Waskom, M. L. seaborn: statistical data visualization. «i»J. Open Source Softw.«/i» «b»6,«/b» 3021 (2021).',
'Pedregosa, F. et al. Scikit-learn: machine learning in Python. «i»J. Mach. Learn. Res.«/i» «b»12,«/b» 2825–2830 (2011).',
'Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman and Hall/CRC, 1994).',
]

def _ref_run(para, text, bold=False, italic=False):
    run = para.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(10)
    set_black(run)
    run.bold = bold
    run.italic = italic
    return run

_REF_MARK_RE = re.compile(r'«([ib])»(.*?)«/\1»')

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
    return para

# ============================================================
# TITLE PAGE
# ============================================================
# Title as plain paragraph: add_heading(level=0) uses Word's built-in Title
# style, which carries a blue bottom border (visible as a blue rule under the
# title). A plain paragraph avoids the style entirely.
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = t.add_run('CKI: a Ka/Ks-inspired index separating functional divergence from baseline variation in cell atlases')
tr.font.name = 'Arial'
tr.font.color.rgb = RGBColor(0,0,0)
tr.font.size = Pt(16)
tr.bold = True
t.paragraph_format.space_after = Pt(14)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Xianming Wu (first author)
run = sub.add_run('Xianming Wu')
run.font.name = 'Arial'
run.font.size = Pt(14)
set_black(run)
for ch in ['1']:
    r = sub.add_run(ch)
    r.font.name = 'Arial'
    r.font.size = Pt(11)
    set_black(r)
    set_superscript(r)

sub.add_run(', ')

# Li Zhang (corresponding author)
run = sub.add_run('Li Zhang')
run.font.name = 'Arial'
run.font.size = Pt(14)
set_black(run)
for ch in ['1', ',', '2', ' ']:
    r = sub.add_run(ch)
    r.font.name = 'Arial'
    r.font.size = Pt(11)
    set_black(r)
    set_superscript(r)
r = sub.add_run('*')
r.font.name = 'Arial'
r.font.size = Pt(11)
set_black(r)
set_superscript(r)

# Affiliations
auth = doc.add_paragraph()
auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
run1 = auth.add_run('1')
run1.font.name = 'Arial'
run1.font.size = Pt(10)
set_black(run1)
set_superscript(run1)
run2 = auth.add_run('Chinese Institute for Brain Research, Beijing 102206, China')
run2.font.name = 'Arial'
run2.font.size = Pt(10)
set_black(run2)

auth2 = doc.add_paragraph()
auth2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run3 = auth2.add_run('2')
run3.font.name = 'Arial'
run3.font.size = Pt(10)
set_black(run3)
set_superscript(run3)
run4 = auth2.add_run('Institute of Blood Transfusion, Chinese Academy of Medical Sciences & Peking Union Medical College, Chengdu 610052, China')
run4.font.name = 'Arial'
run4.font.size = Pt(10)
set_black(run4)

# Correspondence
cor = doc.add_paragraph()
cor.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = cor.add_run('* To whom correspondence should be addressed. Email: knightz@pumc.edu.cn')
run.font.name = 'Arial'
set_black(run)
run.font.size = Pt(10)

# ORCID
orcid = doc.add_paragraph()
orcid.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = orcid.add_run('ORCID: Li Zhang 0000-0002-0698-0754')
run.font.name = 'Arial'
set_black(run)
run.font.size = Pt(11)

# ============================================================
# ABSTRACT (NC: unstructured, single paragraph, <=150 words)
# ============================================================
heading('Abstract', level=1)

p('Inspired by the Ka/Ks ratio, CKI (Cell-type Ka/Ks-inspired Index) decomposes transcriptomic divergence into a baseline rate k_n (housekeeping genes) and a functional rate k_f (identity genes); \u03c9 = k_f/k_n quantifies baseline-normalized functional divergence. In ground-truth simulation, \u03c9 rejected neutral housekeeping drift (false-positive rate 0.00 versus 0.55\u20130.58 for raw JS and cosine) and ranked first for functional-versus-neutral discrimination (AUC = 0.80). On real technical replicates\u201430 cross-lane pairs from Kang IFN-\u03b2\u2014\u03c9 raised no false reports; under stronger brain library-level drift (2,161 pairs), it had the lowest false-report rate among continuous metrics (28.6% versus 45.2% for raw JS), though specificity decays with group size. In 3,567 TCGA samples across five cancer types, \u03c9 revealed a consistent pan-cancer reversal\u2014tumors less divergent than adjacent normal tissue (ratio 1.10\u20132.46, CI excluding 1 in four of five cancers)\u2014driven by a 1.3\u20133.3-fold elevated housekeeping baseline, not reduced functional divergence; in lung adenocarcinoma, KRAS-mutant tumors showed elevated tissue-level divergence whose functional (k_f) and baseline (k_n) components both survived purity and smoking adjustment, whereas the apparent EGFR-mutant association was explained by stromal/immune admixture. Brain analysis revealed a 1.74-fold size-balanced regional gradient ([1.64, 1.84]; 6.10-fold uncorrected; 3.68-fold span-matched intra-cerebellar). CKI is freely available as an open-source Python package.')


# ============================================================
# INTRODUCTION (NC: manuscript must begin with the heading "Introduction")
# ============================================================
heading('Introduction', level=1)

p('Comparing two cell populations is among the most common tasks in single-cell analysis. Researchers typically choose a standard metric: Euclidean distance, cosine similarity, Pearson or Spearman correlation, or Jensen-Shannon divergence. These metrics are convenient, but they treat all gene expression differences equally.')

p('Not all expression changes have the same biological meaning: a twofold change in GAPDH may reflect technical noise, whereas a twofold change in a transcription factor may reflect a functional state shift, and standard metrics cannot tell these apart. The problem is acute in large single-cell atlases [1], where donor- and batch-level variation often dominates over cell-type identity. Methods such as Harmony [2], scVI [3], and SATURN [4] remove such nuisance variation [5], but a key question remains: how much of the difference between two populations reflects functional change rather than neutral drift?')

p('This question mirrors one addressed in molecular evolution. The Ka/Ks ratio (dN/dS) distinguishes nonsynonymous changes (Ka, which alter the protein) from synonymous changes (Ks, largely silent) [6,7], using synonymous sites as an internal baseline so that the ratio reveals selection. While CKI does not share Ka/Ks\u2019s formal mathematical properties (notably the shared mutation rate that cancels in the ratio; see Discussion), it adopts an analogous heuristic logic for transcriptomic comparisons.')

p('CKI defines two rates: a baseline divergence rate k_n, estimated from housekeeping (HK) gene expression, and a functional divergence rate k_f, estimated from cell-type identity genes. The ratio \u03c9 = k_f/k_n quantifies baseline-normalized functional divergence: values close to the equivalent-population calibration baseline (established empirically within each dataset; see Results) indicate baseline-consistent differences, values far above indicate functional divergence exceeding baseline variation, and values far below indicate strong functional constraint. The scope of \u03c9 is bounded by a single central assumption, stated here once and quantified empirically throughout: the HK anchor is valid only where housekeeping expression remains constrained. Functional signal located on HK genes is invisible to \u03c9 by construction, and in disease or strong-perturbation contexts the anchor itself shifts\u2014housekeeping dysregulation and composition change in cancer (TCGA, below), IFN-\u03b2 stimulation of housekeeping genes in the perturbation demonstration (below; simulated adversarial scenarios in Supplementary Note 1)\u2014inflating the denominator and deflating the ratio. In such regimes \u03c9 must be read alongside its components, and k_f with a design-matched null is the honest default for ordering claims (Results; limitations are addressed in the Discussion). CKI \u03c9 is a heuristic index, not a formal measure of Darwinian selection; interpretation is anchored in the empirical distribution of \u03c9 within each analysis rather than in fixed ratio cut-offs or claims about selection regimes (see Discussion).')

p('Here, we show that CKI provides a baseline-normalized index of cell-state divergence across five scales. First, we calibrated CKI on Tabula Muris mouse data [8]: random splits of the same cell population yield \u03c9 above 1 (empirical calibration baseline 7.70, 95% CI [7.37, 8.02]). Second, in Tabula Sapiens human data [9], CKI \u03c9 is negatively correlated with all four standard distance metrics; a decomposition analysis showed this association is partly driven by the k_n denominator (k_n is itself strongly positively correlated with the standard metrics), so \u03c9 is a composite of numerator and denominator information rather than a fully independent dimension (see Results). Third, on real technical replicates\u201430 same-donor cross-lane pairs in an IFN-\u03b2 PBMC cohort and 2,161 same-donor, same-region library pairs in the brain atlas\u2014\u03c9 showed the lowest drift misreporting among continuous divergence metrics while retaining sensitivity to genuine biology (Results). Fourth, applied to TCGA cancer data [10,11], CKI mapped tissue-level functional divergence across five cancer types and 3,567 samples, uncovering a consistent pan-cancer reversal\u2014tumor specimens less divergent than adjacent non-tumor tissue, attributable to an elevated housekeeping baseline\u2014and resolving driver-class differences in lung adenocarcinoma, where KRAS-mutant tumors retained both functional (k_f) and baseline (k_n) divergence after purity and smoking adjustment, whereas the apparent EGFR association dissolved under purity adjustment (Results). Fifth, in a human brain single-nucleus atlas [12], we measured how non-neuronal cell classes differ across brain regions, quantifying a regional differentiation gradient (1.74-fold size-balanced; 6.10-fold uncorrected full-data estimate) and screening for anomalously similar cell-type/region-pair candidates; because no candidate survived false-discovery-rate correction under a strict block-shuffle null preserving the cell-type-by-region design, we present the brain candidates as hypothesis-generating signals for future lineage-tracing validation. The human, pan-cancer, and brain analyses are complemented by mouse Tabula Muris calibration and ground-truth simulation analyses throughout.')

# ============================================================
# RESULTS
# ============================================================
heading('Results', level=1)

# --- Result 1 ---
heading('Decomposing transcriptomic variation', level=2)

p('CKI takes two cell populations as input, each represented as a pseudobulk expression vector (mean expression across its cells). The computation has three steps, all using the same metric (Jensen-Shannon divergence) on the same expression matrix, so the ratio is internally calibrated (Fig. 1).')

p('Step 1: Compute the baseline divergence rate k_n. We restrict the pseudobulk vectors to housekeeping (HK) gene indices and add a +1 pseudo-count followed by L1 normalization; k_n is the JS divergence between the two HK-gene probability distributions. Because HK genes should not differ systematically between biologically equivalent populations [13], k_n captures baseline technical and physiological noise.')

p('Step 2: Compute the functional divergence rate k_f. We restrict the pseudobulk vectors to identity gene indices\u2014genes that define cell-type-specific functions. In the default configuration (Tabula Muris full pairwise matrix, Supplementary Fig. 1), identity genes are the top-2,000 highly variable genes (HVGs; Seurat flavor), excluding HK genes; for all other analyses (mouse pilot, human Tabula Sapiens, TCGA, brain atlas), k_f uses the top-200 differentially expressed genes (ranked by absolute mean difference) for that specific pair and k_n is computed per pair on the shared HK gene set, HK genes excluded throughout. Because the k_f genes are selected per pair from the observed difference itself, absolute k_f\u2014and therefore absolute \u03c9\u2014are upper-bound, scheme-specific estimates (fixed gene-panel ablation, Results).')

p(f'Step 3: \u03c9 = k_f/k_n. For statistical inference, we perform permutation testing (B = 1,000 for all datasets): group labels are permuted (cell labels for mouse and human, sample labels for TCGA) or, for the brain, library-to-region assignments are block-shuffled, and \u03c9 is recalculated to generate a null distribution. The empirical P-value is P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1), effect size is reported as standardized effect size (SES = (\u03c9_obs \u2212 \u03bc_null) / \u03c3_null), and Benjamini-Hochberg FDR correction is applied within each dataset.')

p(f'A parameter sweep on Tabula Muris ({_sb["n_pairs"]} pairs, {_ds["tabula_muris_organs"]} organs) showed that adding pathway enrichment scores to k_f does not improve discrimination (identity-only AUC = {_sb["identity_auc"]:.3f}; Supplementary Fig. 1, Supplementary Table 1).')

# --- Result 2 ---
heading('Calibration confirms baseline behavior', level=2)

p(f'We calibrated CKI on the Tabula Muris FACS dataset [8] (SmartSeq2, {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs), with housekeeping genes from the HRT Atlas v1.0 reference [13] (mouse ortholog column). For the full pairwise matrix (703 pairs, Supplementary Fig. 1), identity genes were the top-{_ds["n_hvg"]:,} highly variable genes (HVGs; Seurat), excluding HK genes; for the pilot calibration we used the hybrid per-pair scheme (per-pair k_n on the shared HK set; per-pair k_f on the top-200 differentially expressed genes, HK excluded) (Fig. 2).')

p(f'We performed control comparisons in which we randomly split the same cell population into two halves, across six FACS control populations (Fig. 2a). 50 split-half replicates per population (300 \u03c9 values) stabilized the baseline at mean \u03c9 = 7.70 (95% CI [7.37, 8.02]); the legacy six-split estimate (6.67) is consistent. No control comparison reached significance (all P > 0.05, one-sided permutation test): CKI recognizes biologically equivalent populations as having no functional divergence (leave-one-population-out baseline range 6.75\u20138.08; Section 3.10 of the Supplementary Information).')

p(f'Beyond controls, \u03c9 values increased monotonically with biological distance (Fig. 2b, c): same cell type across organs (S category: mean \u03c9 = {_mc["S_mean"]:.2f}, n = {_mc["S_n"]}) sat below different cell types within an organ (D category: mean \u03c9 = {_mc["D_mean"]:.2f}, n = {_mc["D_n"]}), with cross-organ cross-type comparisons highest (2\u20134 pairs per category, so category means are calibration-scale estimates). Component analysis confirmed k_f as the driver: from controls to inter-cell-type comparisons, k_f rose roughly 400-fold ({_mc["kf_mean_ctrl"]:.4f} \u2192 {_mc["kf_mean_D"]:.2f}\u2013{_mc["kf_mean_X"]:.2f}), while k_n rose only {_mc["kn_fold_D"]:.0f}\u2013{_mc["kn_fold_X"]:.0f}-fold. CKI thus measures functional divergence, not total difference.')

p(f'Because the empirical baseline deviates substantially from the theoretical ideal (\u03c9 = 1), we introduce a calibrated omega, \u03c9_cal = \u03c9_obs / 7.70. Split-half calibration inside each dataset shows the factor to be dataset-relative, not universal: the brain atlas baseline is 9.73 (95% CI [9.03, 10.53]; 29 populations), ~1.3-fold above the mouse-derived factor, whereas Tabula Sapiens gives 7.67 (95% CI [7.39, 8.00]), inside the mouse CI. Class-specific baselines (range 7.58\u201312.52, 1.65-fold spread) leave the astrocyte-to-Bergmann-glia gradient essentially unchanged (5.99, 95% CI [4.43, 7.69]), and a ratio-estimator audit confirms the calibration absorbs ratio bias (Supplementary Notes 2\u20134).')

# --- Result 3 ---
heading('Correlation structure between CKI and standard metrics', level=2)

p(f'We extended CKI to the Tabula Sapiens human atlas [9] ({_ds["tabula_sapiens_cells"]:,} cells; {_h["n_ct_analyzed"]} filtered cell-type entries contributing {_h["n_pairs_total"]:,} pairs across six organs), using the same hybrid scheme with HRT Atlas v1.0 HK genes [13] (human column) (Fig. 2d).')

p(f'Human \u03c9 values ranged from {_h["omega_min"]:.2f} to {_h["omega_max"]:.2f} (mean {_h["omega_mean"]:.2f}, median {_h["omega_median"]:.2f}, n = {_h["n_pairs_total"]:,} pairs); cross-dataset \u03c9 comparisons are rank-based only throughout (Discussion). Within the human atlas, the biological hierarchy was preserved: same cell type across organs (mean \u03c9 = {_h["diff_organ_same_ct_mean"]:.2f}, n = {_h["diff_organ_same_ct_n"]} pairs) was lower than different cell types within the same organ (mean \u03c9 = {_h["same_organ_diff_ct_mean"]:.2f}, n = {_h["same_organ_diff_ct_n"]:,} pairs).')

_decomp_kf_lo = _decomp['corr_kf_M'].min(); _decomp_kf_hi = _decomp['corr_kf_M'].max()
_decomp_kn_lo = _decomp['corr_kn_M'].min(); _decomp_kn_hi = _decomp['corr_kn_M'].max()
_decomp_pc_lo = _decomp['partial_corr_omega_M_given_kn'].min()
_decomp_pc_hi = _decomp['partial_corr_omega_M_given_kn'].max()
p(f'We computed CKI \u03c9 and four standard metrics (raw JS divergence, Spearman distance, cosine distance, marker Jaccard distance) on all {_h["n_pairs_total"]:,} human cell-type pairs. CKI \u03c9 was negatively correlated with all four (Spearman r = {f'{_sc["max"]:.2f}'.replace('-', '\u2212')} to {f'{_sc["min"]:.2f}'.replace('-', '\u2212')}, all P < 10\u207b\u00b9\u2074\u2075), whereas the four standard metrics formed a tight positive cluster (pairwise r = {_sc["std_pairwise_min"]:.2f}\u2013{_sc["std_pairwise_max"]:.2f}). Decomposing the association: k_f was positively correlated with the standard metrics (r = +{_decomp_kf_lo:.2f} to +{_decomp_kf_hi:.2f}) and k_n more strongly so (r = +{_decomp_kn_lo:.2f} to +{_decomp_kn_hi:.2f}), and conditional on k_n the correlation between \u03c9 and each standard metric became positive in all four cases (partial r = +{_decomp_pc_lo:.2f} to +{_decomp_pc_hi:.2f}, all P < 1 \u00d7 10\u207b\u00b9\u2074). The negative raw correlation is thus partly a ratio artifact of the k_n denominator.')

p(f'CKI was the only metric where same-organ different-cell-type pairs had higher values than different-organ different-cell-type pairs (mean \u03c9 {_h["same_organ_diff_ct_mean"]:.2f}, n = {_h["same_organ_diff_ct_n"]:,} vs. {_h["diff_organ_diff_ct_mean"]:.2f}, n = {_h["diff_organ_diff_ct_n"]:,}; Mann-Whitney U, P = 5.6 \u00d7 10\u207b\u00b9\u2078); all four standard metrics showed the opposite pattern. Decomposition tempers the reversal\u2019s functional reading: same-organ pairs have indistinguishable k_f (0.247 vs. 0.250, P = 0.60) but lower k_n (0.0130 vs. 0.0148, P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable housekeeping baseline within organs, not greater functional specialization of same-organ cell types.')

# --- Result 3b: ground-truth simulation ---
heading('Ground-truth simulation: specificity versus sensitivity', level=2)

p('No real dataset provides pairs with known functional divergence, so we built a semi-synthetic ground truth by injecting known perturbations into a real background (Tabula Muris FACS marrow B cells; true pre-injection divergence zero; Methods). Under pure neutral housekeeping drift, raw JS and cosine exceeded their null thresholds in 55% and 58% of replicates, whereas \u03c9 produced none (2% under global overdispersion). Conversely, detecting an injected functional module required strong signals (\u03c9 detected none of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2): per-pair top-200 selection saturates with noise even under the null (median baseline k_f = 0.025), so weak shifts do not lift k_f above the selection floor. Two adversarial scenarios quantify the boundary (Supplementary Notes 1, 5): \u03c9 is structurally blind to modules placed on HK genes (detection 0.000 at every \u03b4; k_n itself fired at 0.61\u20131.00), yet under expression-matched low-variance non-HK drift (N1 control) \u03c9 stayed at its calibrated false-positive rate (0.000\u20130.067) while raw JS and cosine inflated to 0.81\u20131.00\u2014the ratio cancels global compositional drift wherever it acts, so its specificity is not an HK-anchoring artifact.')

p('\u03c9 best discriminated functional (\u03b4 \u2265 0.25) from neutral perturbations (Fig. 2e; AUC = 0.80 versus 0.72 k_f, 0.64 raw JS, 0.58 cosine, 0.21 k_n; 95% CI [0.777, 0.831]): the apparent power of the standard metrics is purchased with false positives on neutral drift. The ratio also conferred robustness to technical asymmetry (fourfold cell-count imbalance: \u03c9 \u221232%, k_f +67%, cosine +108%; no systematic shift from 30% dropout or a twofold depth difference). \u03c9 is thus a specificity-first screen: its construction rejects neutral drift at the cost of bounded power for weak-to-moderate signals (Supplementary Note 1).')

p('The design was repeated in a second Tabula Muris FACS background\u2014skin keratinocyte stem cells (1,371 cells; 1,750 replicates per background; Methods)\u2014and fully reproduced: AUC(\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e). The power bound is background-dependent (skin has a lower k_f selection floor, median 0.011 versus 0.025; at \u03b4 = 1, \u03c9 detection 0.91 versus 0.00 in marrow). Under the fourfold imbalance k_f retained higher power (0.98\u20131.00 versus 0.04\u20130.20)\u2014the flip side of the ratio\u2019s neutral-drift immunity.')

# --- Result 3b-nc49: real-data neutral-drift calibration on technical replicates ---
heading('Real-data neutral-drift calibration on technical replicates', level=2)
p('The simulation\u2019s neutral-drift benchmark concerns synthetic drift; we therefore tested the same specificity on real technical replicates, calibrating each pair against a per-pair size-matched cell-shuffle null (B = 200 per pair; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14] (eight unstimulated donors, each captured in two 10x lanes)\u2014the 30 same-donor, same-condition cross-lane pairs provide clean technical replicates: \u03c9 was fully calibrated (0 of 30 pairs above its own null 95th percentile; median calibration ratio 0.963; k_f alone likewise 0 of 30), whereas raw JS misreported 36.7% of pairs and cosine 23.3% as divergence (Fig. 3d).')
p('The same design scales to the brain atlas (606 10x libraries): a three-tier drift ladder of library-level pairs\u2014T1, same donor, region, and cell type (pure technical drift; 2,161 pairs); T2, different donors within a region (1,089 pairs); T3, different regions within a donor (regional biology, positive control; 1,656 pairs) [12]. On T1, \u03c9 had the lowest misreporting rate among the continuous divergence metrics (FPR 28.6% versus 45.2% raw JS, 44.1% cosine, 40.6% Spearman, 37.6% k_f; Fig. 3b, c); marker Jaccard distance was lower still (19.9%) but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \u03c9 and 2.98 for raw JS) and offers no k_n/k_f decomposition. At T2 \u03c9 again misreported least among the continuous metrics (90.9% versus 98.4\u201398.7%); across the ladder the \u03c9 calibration gradient is the shallowest of all metrics (1.04 \u2192 1.76 \u2192 1.80, versus 1.07 \u2192 3.32 \u2192 2.98 for raw JS), so \u03c9 best separates technical drift from biology in relative terms.')
p('Two qualifications temper the brain result. First, the absolute \u03c9 FPR is not zero and grows with group size (14.1% below 30 nuclei per library to 48.0% above 500; raw JS 28.6% to 72.5%), a library-level technical component the k_n anchor absorbs only partially\u2014the 0-of-30 Kang outcome sits at the favorable end of this size dependence. Second, a minority of classes show gene-specific library effects the anchor cannot absorb (choroid plexus median calibration 2.31; Bergmann glia 1.16). Absolute neutral-drift immunity thus transfers to real data only as a relative-calibration advantage (Section 3.12 of the Supplementary Information).')

p('An independent validation on data not used above reinforces this calibration: on the CELLxGENE Microglia supercluster [12] (91,838 nuclei), sample-matched microglia-versus-CNS-macrophage pairs (n = 35) separated cleanly from neutral half-splits (n = 40; \u03c9 21.83 \u00b1 7.20 versus 1.30 \u00b1 0.36; Mann-Whitney P = 5.5 \u00d7 10\u207b\u00b9\u2074; AUC = 1.00), the margin carried by k_f (AUC 1.00) rather than k_n (0.89) (Supplementary Note 16; Supplementary Fig. 14).')

# --- Result 3b: real perturbation demonstration (IFN-beta PBMC) ---
heading('Real perturbation demonstration: IFN-\u03b2-stimulated PBMCs', level=2)
p('How \u03c9 behaves on a real perturbation whose effect on the housekeeping anchor is unknown was tested on peripheral blood mononuclear cells from eight donors, control versus 6-hour IFN-\u03b2 stimulation [14] (24,413 cells, six cell types; Methods). Because the two conditions were captured in separate 10x lanes, condition is fully confounded with lane for every metric; we read the analysis as a relative architecture demonstration, not an absolute detection claim. The perturbation was visible at the \u03c9 level in all six cell types (median within-donor stimulated-versus-control \u03c9 exceeded median donor-versus-donor \u03c9 by 1.1\u20132.0-fold), but k_f alone separated perturbation from donor drift as well or better (rank AUC: \u03c9 0.55\u20130.92, k_f 0.74\u20131.00); in CD14+ monocytes \u03c9 AUC fell to 0.55 while k_f retained 0.98, consistent with the anchor-visibility mechanism\u2014stimulation raises housekeeping expression itself (median k_n rises 1.2\u20135.7-fold), so the denominator inflates and partially cancels the functional signal. The demonstration thus supports, within a lane-confounded design, the anchor-visibility boundary in the decision rules, while \u03c9 tracks real perturbation above donor drift when the anchor is unaffected (Supplementary Fig. 3; Supplementary Note 6).')

# --- Result 3d: benchmarking against perturbation-response metrics ---
heading('Benchmarking against perturbation-response metrics', level=2)
p('We benchmarked CKI against MELD (v1.0.2) and scDist on the Kang IFN-\u03b2 dataset [14] (using a Python approximation of the R-only scDist, labelled as such throughout). CKI and MELD agreed on effect direction in 6 of 6 cell types, but MELD\u2019s within-type separation was near-saturated (AUC 0.997\u20130.9998), leaving no gradient to compare. In an additive mean-shift simulation, MELD and the scDist approximation detected every configuration (sensitivity 1.00), whereas CKI \u03c9 rose from AUC 0.52 to 0.79 as the shift grew on 100 genes but collapsed to 0.05\u20130.13 on 500 genes\u2014at 500 shifted genes the anchor k_n itself responds (k_n AUC = 1.000) and the ratio is annihilated by its denominator. \u03c9 therefore measures divergence in excess of the anchor and is, by design, insensitive to perturbations that move the anchor itself; users seeking maximal detection power for broad perturbations should use MELD, scDist, or CKI\u2019s own k_f component. Donor-paired power falls from 0.67\u20130.93 at 50 cells per donor per condition to \u2248 0 at 500 and above (operating window ~50\u2013200 cells; Discussion).')

# --- Result 3c: fixed gene-panel ablation ---
heading('Fixed-panel ablation: robust rankings, scheme-specific \u03c9', level=2)
p('The reference implementation first reproduced the reported landscape exactly (maximum per-pair |\u0394\u03c9| = 6.4 \u00d7 10\u207b\u00b9\u00b3 over all 31,764 pairs). Non-circular panels left rankings essentially untouched: pair-level \u03c9 under leave-pair-out correlated with the reported scheme at \u03c1 = 0.937 (0.918\u20130.931 across the other two panels), and the ten class means at \u03c1 = 0.90\u20130.99. The astrocyte-to-Bergmann-glia gradient was preserved and, under leave-pair-out, amplified (6.10-fold reported; 6.53-fold leave-pair-out). Class-level significance was largely robust under a scheme-matched block-shuffle null (B = 200) with leave-pair-out panels: astrocytes, OPCs, and committed OPCs remained at the permutation floor, fibroblasts and vascular cells remained or reached significance (P = 0.020 and 0.035), and the remaining classes stayed non-significant.')

p('The ablation also quantifies what circular selection costs: the circular panel inflated k_f by a median of 1.61-fold relative to the leave-pair-out panel and by 6.1- and 7.3-fold relative to the fixed and unselected panels, so reported absolute \u03c9 values are upper-bound, scheme-specific estimates (grand mean 38.55 reported; 26.5 leave-pair-out; 6.5 fixed; 5.3 unselected). Rank-based conclusions are robust (the multiplicative-residual ranking underlying the region-association screen correlated at \u03c1 = 0.86\u20130.88 across schemes), but absolute thresholds do not transfer: the tier cutoffs (\u03c9 < 15/25/35) are calibrated to the reported scheme\u2019s inflated scale (Supplementary Note 7).')

# --- Result 4 ---
heading('A pan-cancer map of tissue-level divergence in tumors', level=2)

p(f'We applied CKI to TCGA bulk RNA-seq data across five cancer types (LUAD, LUSC, LIHC, KIRC, BRCA) [10,11], totalling {_tc["n_total"]:,} samples. Because bulk RNA-seq averages over tumor, stromal, and immune compartments, \u03c9 here quantifies divergence between tissue states rather than between cell types; we therefore compare tumor\u2013tumor (TT), normal\u2013normal (NN), and tumor\u2013normal (TN) pairs within each cancer type (Fig. 4; Supplementary Fig. 4). A consistent pan-cancer reversal emerged: NN pairs were more divergent than TT pairs in all five cancer types (mean NN/TT \u03c9: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.10; cluster-bootstrap CI excluding 1 in four of five, LIHC excepted). Component decomposition identified the mechanism: TT k_n exceeded NN k_n by 1.3\u20133.3-fold in every cancer type (95% CIs excluding 1 in all five), whereas TT k_f was equal to or higher than NN k_f\u2014the reversal reflects a more stable housekeeping baseline among adjacent non-tumor specimens, not smaller functional-gene divergence of tumor cells (Fig. 4a).')

p('To ask whether the ratio resolves biologically distinct tumor states, we stratified LUAD tumors by driver mutation (61 EGFR-mutant, 120 KRAS-mutant, 311 wild-type) using per-tumor \u03c9 (Fig. 4b). KRAS-mutant tumors showed the highest tissue-level divergence (mean \u03c9 = 136.9 versus 115.4 wild-type and 122.2 EGFR-mutant; Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; Dunn\u2013Holm P \u2264 0.008 for both KRAS contrasts, P = 0.39 for EGFR\u2013wild-type); whole-tumor label-permutation tests confirmed all three contrasts (Section 3.13 of the Supplementary Information). The decomposition separated the drivers mechanistically (Fig. 4c,d): the KRAS elevation was carried predominantly by a lower housekeeping baseline (~84% of the log-\u03c9 gap) with an accompanying functional component (KRAS versus EGFR under k_f alone, P = 0.015). Adjustment for ESTIMATE stromal/immune admixture left the KRAS\u2013wild-type difference significant for both components (adjusted log-\u03c9 ratio 1.19, 95% CI [1.12, 1.26]), whereas the apparent EGFR elevation was fully explained by admixture (all adjusted P > 0.4). Adjusting for smoking (94% ever-smokers among KRAS-mutant tumors versus 63% EGFR-mutant and 86% wild-type), alone or jointly with admixture, age, and sex, left the contrast essentially unchanged (\u0394\u03c9 +13.3, P = 1.4 \u00d7 10\u207b\u00b3). TP53 co-mutation and histological subtype were not adjusted for, so the KRAS contrast carries residual confounding. Stratifications beyond LUAD (LIHC Edmondson grade, BRCA PAM50) are denominator-dominated vignettes (Supplementary Note 9).')

p('Four controls bound the interpretation (Supplementary Note 8). First, composition adjustment left the pooled tumor-pair k_n coefficient essentially unchanged (\u22121.3% pooled, 95% CI \u22124.8% to +2.0%; \u221216% to +33% per cancer type), and ESTIMATE stromal/immune scoring showed admixture can only weaken, not create, the TT k_n elevation (per-tumor k_n correlated negatively with admixture, r = \u22120.23 to \u22120.42; high-purity-half comparisons increased the ratio in all five, e.g. LUAD 2.46 \u2192 2.86). Second, all TCGA statistics were recomputed under a linear probability mapping (the authoritative caliber), with all key results preserved (LIHC effect size mapping-sensitive: 1.10 versus 1.31 under softmax; Section 1.7). Third, LUAD KRAS identity panels showed no enrichment for any MSigDB Hallmark program [15] after correction (all q \u2265 0.24), and composition-adjusted regressions retained the TT \u2265 NN k_f ordering in all five cancer types. Fourth, excluding the 32 cell-line-derived LIHC samples leaves the LIHC null result unchanged (NN/TT 1.11, 95% CI [0.93, 1.30]). TCGA \u201cnormal\u201d samples are adjacent non-tumor tissues rather than healthy donor tissue, and per-tumor \u03c9 was not associated with overall survival (LIHC Cox hazard ratio per SD 1.07, 95% CI 0.88\u20131.31): we report all TCGA findings as tissue-level divergence at bulk resolution, pending single-cell or deconvolution-based validation.')

# --- Result 5 ---
heading('CKI ranks cell types by cross-organ conservation', level=2)

p(f'Of the {_h["n_pairs_total"]:,} Tabula Sapiens cell-type pairs, {DATA["cross_organ_n_total"]} are same-cell-type cross-organ comparisons, which ask which cell types maintain their identity regardless of residence and which are shaped by their organ environment (Fig. 5; Table 1; Supplementary Fig. 5). We anchor interpretation on well-sampled cell types (n \u2265 5 pairs; upper block of Table 1): {t2[0][0]}s (mean \u03c9 = {t2[0][1]} \u00b1 {t2[0][2]}, n = {t2[0][3]}) and {t2[1][0]}s (mean \u03c9 = {t2[1][1]} \u00b1 {t2[1][2]}, n = {t2[1][3]}) were the most conserved, followed by {t2[2][0]}s and {t2_next[0]}s; {mac[0]}s, the most abundant type (n = {mac[3]}), showed intermediate conservation. At the divergent end, {last2[0][0]}s and {last2[1][0]}s had the highest cross-organ \u03c9, consistent with organ-specific endothelial gene programs [16], although both rest on only n = 3 pairs; sparsely sampled types (n = 1\u20133 pairs) carry no reliable signal.')

p(f'The cross-organ ranking showed little agreement with rankings from standard metrics (Spearman r = {f'{min(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')} to {f'{max(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')}, n = {DATA["cross_organ_n_total"]} pairs; Supplementary Table 2), because CKI explicitly normalizes: two populations may share highly expressed genes, yet a low baseline k_n turns modest functional differences into high \u03c9. A k_f-only control qualifies the interpretation (Supplementary Note 9): per-cell-type mean \u03c9 and mean k_f are only weakly concordant (r = 0.23, 95% CI [\u22120.08, 0.38], n = 17 cell types), and while the extremes reproduce (CD8+ T cells most conserved under both \u03c9 and k_f), the middle does not (NK cells rank most divergent under \u03c9, second-most conserved under k_f). The cross-organ ranking is thus a composite of functional divergence and baseline differences; because the k_n anchor is not calibrated across cell types (Discussion), cross-type gaps in mean \u03c9 should be read as descriptive rather than calibrated differences.')

# --- Result 6 ---
heading('Brain regional analysis reveals divergence gradients', level=2)

p('We applied CKI to the Siletti et al. human brain single-nucleus atlas [12] (~3.3 million nuclei, 108 regions), asking how much functional divergence separates the same cell type across regions. We focused on 888,263 non-neuronal nuclei in 10 major classes (886,808 passing the \u2265 20-nuclei filter); neurons were excluded because supercluster_term does not resolve neuronal subtypes. CKI \u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs) (Fig. 6; Supplementary Fig. 6; Supplementary Table 3); vascular cells and fibroblasts are heterogeneous superclusters, so their class-level \u03c9 values are supercluster averages.')

p('Class-mean \u03c9 spanned a regional gradient across cell classes, from Bergmann glia and vascular cells (both 13.56) to astrocytes (82.75 \u00b1 44.98, n = 5,778 pairs across 108 regions)\u2014a full-data endpoint gradient of 6.10-fold. Because class-mean k_n is confounded by class size (below), this headline is an uncorrected upper bound: an equal-n downsample control (4,118 nuclei per class, 20 replicates) attenuates it to 1.74 (95% CI [1.64, 1.84]), and a span-matched control restricted to the 21 intra-cerebellar region pairs defining Bergmann glia yields 3.68 (residual again k_n-driven: k_f 1.39 versus k_n 0.33; Supplementary Note 10). We therefore co-report 6.10-fold (full-data) and 1.74-fold (size-balanced) throughout (5.99, 95% CI [4.43, 7.69], under class-specific split-half baselines; Supplementary Note 2).')

p('To test whether this gradient exceeds chance, we used a cell-type-level block-shuffle null that permutes 10x-library-to-region assignments (B = 1,000; Methods). For 4 of 10 cell classes regional structure significantly raised mean \u03c9 (astrocytes at the permutation floor; OPCs, committed OPCs, fibroblasts P \u2264 0.030), 3 of 10 surviving Benjamini-Hochberg correction; a donor-stratified null (Methods) leaves the same 3 of 10, and the single class moving against the conservative direction\u2014ependymal cells (P 0.058 free versus 0.021 stratified)\u2014still does not survive correction (stratified q = 0.052). Microglia, oligodendrocytes, and Bergmann glia sit at or below the null expectation (P = 0.883\u20130.998).')

p('Four analyses probe the robustness of the gradient. First, restricting comparisons to same-donor region pairs (the atlas has four donors; 94.5% of region pairs share at least one) preserved the extremes (astrocytes 75.18; Bergmann glia 16.73), a 4.50-fold gradient, so donor identity cannot explain the gradient away. Second, the astrocyte-versus-Bergmann-glia contrast is predominantly a k_n effect (k_f differs 2.0-fold; mean k_n 3.2-fold): across the ten classes, class-mean \u03c9 tracks k_n (Spearman \u03c1 = \u22120.73) but not k_f (\u03c1 = 0.09), and under a k_f-only ordering astrocytes rank third of ten (k_f-only gradient 4.1-fold). The gradient thus chiefly reflects housekeeping stability across regions, not functional-gene divergence (k_n estimator sensitivity: Supplementary Fig. 7).')

p('Third, class-mean k_n correlates negatively with class size (Spearman \u03c1 = \u22120.648, P = 0.043) while class-mean \u03c9 is uncorrelated with all tested confounders (P \u2265 0.091; Supplementary Note 10). The equal-n residual is carried predominantly by the functional term: the astrocyte/Bergmann-glia k_f ratio is 2.09 under equal-n (full-data 2.03), whereas the k_n ratio reverses direction (equal-n 1.29, astrocyte higher; full-data 0.31, Bergmann glia higher)\u2014the Bergmann-glia k_n elevation in the full data is largely a class-size artefact. Fourth, the gradient is robust to the group-size threshold in direction but not magnitude.')

p('The gradient aligns with known cell biology: vascular cells and fibroblasts are tissue-resident and replenished locally, consistent with their low \u03c9 (though low class-level \u03c9 is not spatial uniformity [17,18]); microglia share core surveillance machinery [19]; astrocytes express region-specific ion channels, transporters, and secreted factors\u2014regional specialization compatible with, but not established by, the k_n-dominated ordering.')

p('The gradient suggests a residence/migration framework (recently migrated types should show low inter-regional \u03c9; resident types accumulate regional signatures), but the data provide no evidence for it: OPCs\u2014the most actively migrating non-neuronal population\u2014show the second-highest mean \u03c9 (40.62), and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92); the framework remains hypothesis generation, not inference.')

heading('Anomalously similar pairs: a hypothesis-generating screen', level=2)

p('Low CKI \u03c9 for a cell type across two regions indicates transcriptomic similarity beyond baseline expectation, with non-exclusive candidate mechanisms (developmental origin heterogeneity, colonization-route boundaries [20-22], postnatal migration [23,24]). We report the screen\u2019s global verdict first: under a design-matched null that recomputes the full selection rule on every block-shuffle permutation, the expected number of Strong candidates is 148.3 across the full 31,764-pair pool\u2014the 39 observed lie 3.8-fold below the null expectation (P(null count \u2265 39) = 1.0), and no candidate survives FDR correction (minimum q = 0.520). The catalogue below is therefore a prioritized hypothesis list, not discoveries, and inherits the atlas\u2019s donor structure (four donors), leaving pair-level nominations subject to donor confounding (region glossary in Supplementary Note 11).')

p('The screen uses a multiplicative model, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand (Methods): a residual (observed / expected) well below 1 marks a cell type far less differentiated between two regions than expected from its own plasticity and the pair\u2019s divergence. Three confidence tiers were defined: Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the region pair), Moderate (residual < 0.5, \u03c9 < 25), and Weak (residual < 0.75, \u03c9 < 35; Supplementary Fig. 8).')

p(f'Among {_br["total_pairs"]:,} comparisons, criteria identified {_br["n_strong"]} ({_br["pct_strong"]:.2f}%) Strong, {_br["n_moderate"]:,} ({_br["pct_moderate"]:.2f}%) Moderate, and {_br["n_weak"]:,} ({_br["pct_weak"]:.2f}%) Weak candidates (Supplementary Table 4). Under the block-shuffle null (B = 1,000; Supplementary Fig. 9), 31 Strong candidates showed raw P < 0.05 but none survived Benjamini-Hochberg correction (minimum q = 0.520); the only sub-nominal stratified family is intra-cerebellar Bergmann-glia (m = 21; minimum q = 0.042). Candidates concentrate in microglia (16 Strong) and oligodendrocytes (10), but the microglial enrichment does not survive the design-matched null (52.0 of the 148.3 null candidates are microglial; observed 16, fold 0.31, P = 0.990): we make no class-composition claim.')

p('A negative control confirms the null is calibrated by library-level, not regional, structure: libraries of every region were split at random into pseudo-regions and the identical test re-run on 127,756 pseudo-pairs (Supplementary Note 12; Supplementary Fig. 10). Pseudo-pairs between halves of different regions gave near-nominal tail rates (5.79% and 6.87% versus 6.17% and 7.90% real), whereas same-region halves showed a 37.6% lower-tail rate, confirming retained power.')

p('The catalogue converges on anatomically coherent themes. Microglial candidates (16 of 39) converge on visual-relay and orbitofrontal dissections (five pairs involve the lateral geniculate nucleus, four the pulvinar; Supplementary Note 11). Mature-oligodendrocyte candidates (10, all raw P < 0.05) show a thalamo-temporal orientation (six with a thalamic relay-nucleus endpoint; tested post hoc under two null references: Discussion, Supplementary Note 13) that crosses rather than follows the dorsoventral origin boundary [25], so their mechanistic basis is left unassigned. Astrocytes, fibroblasts, and ependymal cells contributed sparse candidates [26,27]; Bergmann glia, vascular cells, and choroid plexus contributed none [26,28]. All are hypothesis-generating targets for spatial-transcriptomic and lineage follow-up [19], not discoveries.')





p('In summary, the block-shuffle re-analysis substantially tempers the brain candidate catalogue: the cell-class-level gradient is supported for 4 of 10 classes (3 of 10 after Benjamini-Hochberg correction), no individual candidate survives FDR correction (minimum q = 0.520), and the Strong rule itself is anti-enriched relative to its null (148.3 expected versus 39 observed). An earlier per-pair label-shuffle implementation was anti-conservative (36.3% of P-values at the floor) by ignoring the 10x-library block structure. We therefore position the entire candidate list as hypothesis-generating rather than discoveries.')


# ============================================================
# DISCUSSION
# ============================================================
heading('Discussion', level=1)

p('CKI reframes transcriptomic comparison\u2014from measuring absolute distance to quantifying functional divergence relative to an internal baseline\u2014but this is better described as a recombination of established ideas than a conceptual shift. Reference genes have long anchored normalization and quality control in expression measurement: qPCR normalization by geometric averaging of validated internal control genes [29], and the constrained-variance property of housekeeping genes has been characterized at the genomic level [13,30]. The idea that an intrinsic, gene-property-dependent noise floor can serve as a baseline has likewise been central to the transcriptional-noise literature [31-33], which showed that expression variance is reproducibly gene-specific. CKI\u2019s specific contribution is to combine these ingredients\u2014a constrained reference set, a functional panel, and their divergence ratio\u2014into a per-comparison, design-testable index with an explicit split-half calibration and a design-matched permutation null, rather than to introduce a new concept. The key assumption is that housekeeping (HK) genes are under stabilizing selection that constrains their expression variance across conditions, making them a practical constrained baseline against which functional divergence can be measured. This decomposition is heuristically inspired by Ka/Ks analysis, but CKI is a heuristic index rather than a formal measure of selection: unlike Ka/Ks\u2014where a shared mutation rate cancels mathematically, leaving a pure selection signal\u2014CKI uses empirically defined HK genes as the baseline, lacking a comparable mechanistic cancellation. The empirical calibration (split-half equivalent populations; 50 replicates across six control populations) yielded a mean \u03c9 = 7.70 (95% CI [7.37, 8.02]; the legacy six-split estimate 6.67 is consistent with it), indicating that k_f systematically exceeds k_n even for identical populations due to identity-gene selection. We therefore use \u03c9_cal = \u03c9 / 7.70 as the operational scale, interpreting \u03c9_cal relative to the empirical equivalent-population distribution rather than against fixed cut-offs: values well below the calibrated baseline suggest functional constraint and values well above it enhanced divergence\u2014not as claims about Darwinian selection regimes, and with the caveat that the baseline is dataset-dependent (Results).')

p('CKI is a divergence index, not a classifier\u2014and this is by design. Classifying cell types from transcriptomic data is largely a solved problem; CKI answers a complementary question: regardless of cell-type labels, how much functional divergence separates two populations, relative to their shared baseline? The negative correlation with all standard metrics initially suggested complementary information content, but the decomposition analysis showed this association to be partly a denominator effect (k_n is itself strongly positively correlated with the standard metrics), so \u03c9 should be understood as a composite of numerator and denominator information rather than a fully independent signal dimension. The ratio earns its increment over k_f under controlled ground truth (AUC 0.80 versus 0.72 for k_f in the marrow background; 0.91 versus 0.86 in the skin replication) and in drift rejection, where the anchor cancels shared sampling noise; on real-data orderings the increment is not established, and k_f with a design-matched null remains the default for ordering claims.')

p('The Ka/Ks analogy is heuristically productive but technically bounded: HK genes are empirically defined rather than mechanistically neutral, and the HK anchor is itself the most strongly constrained expression class, so \u03c9 should be read as functional divergence in excess of a constrained baseline, never as evidence of positive selection. The full correspondence\u2014including its McDonald\u2013Kreitman-style fourth term [34]\u2014and its caveats are developed in Section 1.4 of the Supplementary Information.')

p('CKI complements rather than replaces existing methods. SAMap [35] and SATURN [4] excel at cross-species alignment; CACIMAR [36] provides conservation scoring that could be reinterpreted through the CKI lens. However, we did not quantitatively benchmark CKI against these specialized methods, as they address different questions (cross-species alignment vs. within-species functional divergence). A systematic comparison on shared datasets would clarify the complementary strengths of each approach. More broadly, CKI provides a principled null model for any transcriptomic comparison: before concluding that two populations are meaningfully different, ask whether the difference exceeds baseline expectation.')

p('We also compared CKI with Augur [37], which prioritizes cell types by how predictable a condition is from single-cell expression, on the brain atlas (pure-Python port of Augur v1.0.3; 33,036 stratified nuclei; 10 non-neuronal classes; condition label = brain region; Supplementary Note 14). Two variants were run: binary one-vs-rest tasks (comparable across classes despite region-set sizes of 6\u2013107) and a multiclass macro-OvR run; the binary variant was designated the confound-controlled comparison after observing that the multiclass AUC correlates with the eligible-region count, and both are reported in parallel rather than as primary versus secondary. Under the binary variant, the two rankings are moderately concordant: Augur separability versus class-mean \u03c9 Spearman \u03c1 = 0.442 (P = 0.200), versus k_f \u03c1 = 0.564 (P = 0.090), and versus k_n \u03c1 = \u22120.236 (P = 0.511). Astrocytes\u2014the top class by \u03c9 (82.75)\u2014rank third of ten by Augur, and choroid plexus is high on both, so the extremes of the two rankings overlap; at n = 10 the pattern is consistent with, but does not establish, localization of the shared signal to the k_f numerator rather than k_n. CKI is therefore not redundant with perturbation-prioritization tools, with complementarity supported by the decomposition rather than by the ranking correlation alone. The multiclass macro-OvR variant gave a weaker, confounded association (versus \u03c9 \u03c1 = 0.127, P = 0.726; AUC correlated with eligible-region count at \u03c1 = \u22120.744, P = 0.014). The pure-Python port (pyaugur 0.1.0) reports rank identity with the R reference implementation, but that equivalence is the port author\u2019s validation and was not independently re-verified on a public benchmark here. With n = 10 classes these correlations are descriptive only.')

p('The pan-cancer reversal\u2014tumor specimens less divergent than adjacent non-tumor tissue (mean NN/TT 1.10\u20132.46, cluster-bootstrap CIs excluding 1 in four of five cancers)\u2014is a robust tissue-level observation whose mechanistic reading remains cautious: at bulk RNA-seq resolution the apparent convergence could be driven by cell-composition shifts, peritumoral inflammation, or systematic RNA quality differences rather than genuine transcriptional convergence of tumor cells. Component decomposition reinforces this caution: the reversal is predominantly a k_n effect\u2014normal-normal pairs show systematically lower housekeeping-gene divergence than tumor-tumor pairs in all five cancer types, while tumor pairs show the higher functional-gene divergence (k_f)\u2014so the data do not indicate smaller functional divergence of tumor cells. A marker-panel composition check quantifies the confound directly (Supplementary Note 8): tumor-tumor pairs show larger composition differences than normal-normal pairs (median |Delta z| 1.31-fold higher; P = 4 \u00d7 10\u207b\u00b9\u00b3\u2077), and within tumor-tumor pairs k_n correlates with the composition difference (Spearman \u03c1 = 0.364 pooled; 0.20\u20130.51 per cancer type); however, in covariate-adjusted regressions with cluster-bootstrap intervals (B = 1,000), the tumor-pair coefficient attenuates by only \u22121.3% pooled (95% CI [\u22124.8%, +2.0%]; per-cancer \u221216% to +33%). Because marker panels are noisy proxies for true composition, these attenuation estimates are lower bounds: the pooled k_n excess is not fully explained by marker-measurable composition, but neither can a marker-panel regression exclude composition as the driver\u2014plausibly reflecting tumor-specific housekeeping dysregulation [38] or RNA-quality differences\u2014and single-cell or deconvolution-based validation remains necessary. Tumor and adjacent non-tumor aliquots also differ systematically in tissue-source site and batch, and adjacent non-tumor tissue is not healthy tissue, so separating tumor-specific housekeeping elevation from field effects will require an external healthy reference. The PAM50 gradient likewise cannot be read as a functional-divergence ordering (it largely reverses under k_f alone; Supplementary Note 9), and raw \u03c9 scales vary across datasets and schemes, so cross-dataset \u03c9 comparisons are rank-based only.')

p('The cross-organ and cross-brain-region analyses indicate that CKI can serve as a general tool for measuring functional differentiation at multiple spatial scales, with an important qualification: the brain regional gradient is a composite signal dominated by the k_n denominator (k_n contributes 3.21-fold versus 2.03-fold from k_f), so it should not be read as a pure functional-divergence ranking. The candidate screen illustrates a second principle: under a design-matched block-shuffle null, 31 of the 39 Strong candidates showed raw P < 0.05 but none survived Benjamini-Hochberg correction across all 31,764 pairs (minimum q = 0.520), and the raw-P enrichment is strongly tier-dependent\u2014a post-hoc coherence check whose statistical caveats, including the mathematical coupling between the tier rule and the per-pair P values, are quantified in Supplementary Note 13\u2014rather than FDR-controlled evidence. The oligodendrocyte lineage as a whole shows no enrichment (fold 0.77, P = 0.92), and the microglial concentration mirrors the screening rule\u2019s intrinsic bias toward low-\u03c9 classes (fold 0.31; Results). These results illustrate a general principle for high-throughput screens in single-cell atlases: statistical claims require nulls that respect the experimental design, and the absence of FDR-significant signals is itself informative, delimiting what can be concluded from adult transcriptomes alone. Preliminary cross-species validation across the 15 shared mouse\u2013human cell types [39] found no significant cross-species correlation of per-cell-type mean \u03c9 rankings (Spearman r = \u22120.17, P = 0.55; Supplementary Fig. 11), so cell-type-level cross-species transferability of \u03c9 remains unestablished.')

p('Although no individual candidate survives FDR correction, several signals are consistent with prior reports\u2014literature anchoring rather than independent validation. Maturation comparisons must be made on the k_f-only ordering rather than the composite \u03c9 ordering, because the composite is k_n-dominated (Results): under k_f alone the lineage ranks committed OPCs (k_f class mean 0.197, the highest of all ten classes; estimated from only 4,118 nuclei and 1,326 pairs, so this rank carries the widest sampling uncertainty) above oligodendrocytes (0.054), with OPCs lowest (0.048)\u2014partially consistent with reports that early oligodendrocyte stages are regionally uniform whereas mature subsets become region-enriched [40,41]\u2014whereas the composite \u03c9 ordering gives the opposite picture (40.62 above 37.05 above 28.84); neither supports a monotone-maturation reading. The thalamo-temporal orientation of the mature-oligodendrocyte candidates (six of ten with a thalamic relay-nucleus endpoint) concentrates on an axis rather than scattering across the 108 regions. As a descriptive, exploratory characterization\u2014not an inferential claim\u2014we compared this concentration against two null references (Supplementary Note 13). A uniform-draw permutation test (B = 100,000) gives thalamic-relay endpoints in 6 of 10 candidates versus a null mean of 1.95 (P = 1.005 \u00d7 10\u207b\u2075); a selection-rule-matched null (B = 1,000) qualifies this: it generates more survivors than observed (mean 43.7 versus 10), so absolute hit counts are not extreme (6 versus 6.58, P = 0.48), whereas the per-candidate hit rate remains concentrated (0.60 versus 0.15, P = 0.005; conditional on the selected set, not a valid post-selection P value). We therefore describe an axis concentration of the surviving candidates\u2014a pattern difficult to reconcile with migration\u2014whose correspondence with the developmental organization of forebrain oligodendrocytes [25] remains at the level of axis anatomy, because the candidate pairs cross rather than follow the dorsoventral origin boundary; lineage-tracing or spatial-transcriptomic follow-up remains necessary.')

p('CKI and standard metrics answer different questions, and choosing between them can be reduced to a few practical rules. Use CKI when the question is relative: is the functional divergence between two populations larger than what their own housekeeping baseline varies by, within the same dataset and gene-selection scheme? CKI then offers a normalized, interpretable scale (\u03c9 relative to the split-half calibration), higher discrimination than raw distances for strong perturbations (simulation AUC 0.80 versus 0.72 for k_f; Results), and a specificity-first screen: with a design-matched permutation null, a significant \u03c9 rejects label exchangeability under that null\u2014drift on the anchor is the null hypothesis by construction, and functional signal on the anchor is invisible to \u03c9. Before trusting fine-grained \u03c9 orderings, diagnose the denominator: if per-pair k_n itself lies in the extreme tail of its own null distribution, or k_n correlates with technical covariates, report k_f (or SES(k_f)) with the design-matched null directly rather than the ratio. In the real data analyzed here, \u03c9 orderings were predominantly denominator-driven (Supplementary Note 9), so the honest default for ordering claims is k_f plus a design-matched null, with \u03c9 reserved for its specificity-first property. The IFN-\u03b2 demonstration (Kang et al. [14]; Results) makes the boundary explicit: when the anchor itself moves (k_n raised 1.2\u20135.7-fold; monocyte \u03c9 AUC 0.55 versus k_f 0.98), cross-metric contrasts, not absolute \u03c9 values, are the reliable signal. Use standard metrics when absolute cross-dataset distances are required, when the task is classification, when weak-to-moderate effects must be detected at atlas scale, or when an orthogonal signal dimension is needed; when the baseline itself is suspect (bulk data with composition shifts), interpret k_n and k_f separately rather than trusting \u03c9 alone.')

p('For prospective applications of CKI we recommend the following. (i) Cell numbers: use at least 100\u2013200 cells per group; the calibration controls and simulation replicates used 100\u2013200 cells, and below this range pseudobulk noise inflates both k_n and k_f unpredictably. (ii) Reference gene set: use the HRT Atlas v1.0 housekeeping panel (shipped with the package as cki/data/hrt_atlas.csv) rather than data-driven auto-detection, so that k_n is anchored to a pre-specified constrained gene set. (iii) Estimation: compare populations only within the same dataset and the same gene-selection scheme; absolute \u03c9 does not transfer across datasets or schemes (Results). (iv) Baseline: calibrate within the dataset of interest by randomly splitting the same population into halves and computing split-half \u03c9 with the analysis pipeline being used, and interpret \u03c9 relative to that internal baseline rather than the mouse-derived 7.70. (v) Inference: use a permutation null that matches the experimental design (block-shuffle where libraries or donors define blocks)\u2014the reference implementation used here is provided in the package as cki.blocknull.block_shuffle_test\u2014and expect bounded sensitivity: \u03c9 is a specificity-first screen whose value is rejecting neutral drift, not detecting weak-to-moderate functional shifts.')


p('Limitations. Several boundaries delimit where \u03c9 can fire and how it should be read. (i) Scope: CKI is designed to detect state changes within a given cell type, not to discriminate cell-type identity; because the housekeeping anchor is cell-type-specific (housekeeping gene sets may differ across cell types), the k_n baseline is directly comparable only within the same cell type, so limited cross-type discrimination of ω is expected by design and delineates, rather than limits, the index’s scope; the intended domain is biologically matched populations\u2014the same cell type across organs, brain regions, or perturbation states. CKI currently operates at the pseudobulk level. (ii) Gene-set definition and calibration: the per-pair k_f scheme selects genes by the observed difference itself, so k_f magnitudes are inflated upper bounds (median 1.61-fold versus a leave-pair-out panel) and absolute tier thresholds are scheme-specific; housekeeping gene expression may be dysregulated in cancer [38], potentially shifting the k_n baseline in a disease-specific manner; and the empirical calibration factor (7.70, 95% CI [7.37, 8.02]) derives from mouse split-half controls under the per-pair DE scheme, so absolute \u03c9 does not transfer across datasets or gene-selection schemes. Key parameters (top-200 DE genes for k_f, 2,000 HVGs, the +1 pseudo-count) are practical defaults rather than optimized values; the per-pair top-200 count was not itself swept on real data. (iii) Data and design: the TCGA analysis is limited to bulk RNA-seq resolution, its per-cancer permutation test holds the identity panel fixed (anti-conservative relative to per-permutation re-selection), and with five cancer types the TCGA results are exploratory; the brain atlas uses post-mortem tissue, and donor-level PMI and RNA-integrity covariates were unavailable, so regionally differential RNA degradation could masquerade as regional structure in k_n. (iv) Anchor visibility: \u03c9 is structurally insensitive to perturbations that move the housekeeping anchor itself\u2014in simulation, once 500 genes shifted fourfold or more, k_n detected the shift perfectly while the ratio collapsed (AUC 0.05\u20130.13)\u2014and donor-paired permutation power vanishes beyond roughly 500 cells per group, bounding the practical operating window at approximately 50\u2013200 cells; the scDist results were obtained with a Python approximation of the R package and should be re-verified against the original implementation. (v) Multiple testing and cluster-aware inference: the class-level upper-tail tests and the pair-level lower-tail screen are separate families reported without cross-family joint correction; the block-shuffle null assumes libraries are otherwise exchangeable, so systematic library-level confounding (for example batch correlated with dissection order) would distort the null in ways the permutation cannot capture\u2014bounded empirically by the pseudo-region negative control (Supplementary Note 12)\u2014and B = 1,000 permutations bounds the resolvable P-value at 9.99 \u00d7 10\u207b\u2074, so the per-pair FDR outcome (minimum q = 0.520) is a statement about permutation resolution rather than evidence against any candidate. Full treatments of each limitation, with the supporting sensitivity analyses, are given in the Supplementary Information (Supplementary Notes 1\u201316).')









p('Future directions include developmental biology (quantifying functional differentiation between developmental stages), drug response profiling (measuring selectivity of drug-induced transcriptional changes), aging research (tracking age-related baseline vs. functional transcriptional drift), and evolutionary cell biology (quantifying conservation and divergence of cell-type programs across the tree of life). The CKI Python package (v0.5.0) and all analysis notebooks are available at https://github.com/zhanglknt/CKI-cell-type-identification under the MIT License.')

# ============================================================
# Conclusions paragraph retained, merged into the end of Discussion (NC: no separate Conclusions section)
# ============================================================
p('CKI adapts the baseline-normalization logic of Ka/Ks to single-cell transcriptomics, decomposing population divergence into a housekeeping baseline rate (k_n) and an identity-gene functional rate (k_f). Across simulation, calibration, cross-organ, pan-cancer, and brain-regional analyses, we showed that \u03c9 rankings carry reproducible biological signal while absolute \u03c9 values remain scheme- and dataset-specific, that statistical claims at atlas scale require nulls respecting the experimental design, and that the absence of FDR-significant candidates is itself an informative bound on what adult transcriptomes alone can support. CKI is released as an open-source Python package with a fully reproducible analysis pipeline, and we anticipate its use as an interpretable complement to standard distance metrics in comparative single-cell analyses.')

# ============================================================
# METHODS
# ============================================================
heading('Methods', level=1)

heading('CKI computation', level=2)
p(f'We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation [42]. Pseudobulk vectors average expression across cells sharing the same cell-type annotation (at least 20 cells per entry (pseudobulk group); at least one donor/mouse contributing at least 10 cells). Housekeeping (HK) genes are loaded from the HRT Atlas v1.0 reference [13] ({_ds["hrt_atlas_n_hk"]:,} human-mouse conserved HK genes; mouse ortholog column for mouse datasets, human column for Tabula Sapiens, TCGA, and the brain atlas). The package also supports data-driven auto-detection (detect_housekeeping_genes(); combined detection-rate and CV criterion, use_reference = False), but all reported analyses use the pre-specified reference.')

p('For populations A and B with pseudobulk vectors \u03b5_A and \u03b5_B, each vector is normalized to a probability distribution before Jensen-Shannon (JS) divergence computation by a softmax over log-transformed values, which in count space is exactly the operation of adding a +1 pseudo-count followed by L1 normalization: p_i = (c_i + 1)/\u03a3_j(c_j + 1), where c denotes the pseudobulk count. The aggregation order differs across datasets and must be distinguished: the brain pipeline applies log1p after averaging counts, softmax(log1p(mean counts)), matching the count-space formula exactly, whereas the mouse (Tabula Muris pilot) and human (Tabula Sapiens) pipelines average per-cell log1p values and normalize afterwards, softmax(mean(log1p)). This difference plausibly contributes, alongside dataset scale and gene-selection effects, to the non-transferability of the dataset-specific calibration constants (Results). The package default from v0.5.x is the brain order, softmax(log1p(mean counts)), which matches the count-space formula exactly; the reverse order is retained only as a legacy option for reproducing the mouse and human pilots. Calibration constants are pipeline-internal and must not be transferred across pipelines: an \u03c9 calibrated under one aggregation order is not comparable to an \u03c9 computed under the other. A same-data quantification on the mouse pilot\u2019s 15 comparisons (recomputing \u03c9 under both orders on identical cells) confirms the warning: the rank ordering is largely preserved (Spearman \u03c1 = 0.78), but absolute values shift (median fold 0.96, up to 9.8-fold per comparison), and the split-control median baseline itself moves from 6.46 to 10.94 (results/nc49_agg_order_sensitivity.csv). Then k_n = JS(norm(\u03b5_A[H]), norm(\u03b5_B[H])), where H is the set of HK gene indices; k_f = JS(norm(\u03b5_A[I]), norm(\u03b5_B[I])), where I is the set of top-2,000 highly variable genes (HVGs; Seurat flavor) excluding HK genes; \u03c9 = k_f/k_n, with JS divergence [43] using the base-2 logarithm (range [0, 1]). To guard against division by near-zero k_n, the package exposes an optional denominator floor (kn_floor); the package default (kn_floor = 0) applies only a positivity guard, used by all reported single-cell analyses, so no reported single-cell \u03c9 was capped (minimum observed per-pair k_n: 1.1 \u00d7 10\u207b\u2074, mouse; 6.3 \u00d7 10\u207b\u2074, human; 9.2 \u00d7 10\u207b\u2075, brain; only 1 of 31,764 pairs had k_n below 1 \u00d7 10\u207b\u2074, and these values entered \u03c9 uncapped). The TCGA bulk analysis is the sole exception and applies kn_floor = 1 \u00d7 10\u207b\u2074, because pseudobulk averaging across millions of cells compresses HK gene variance and drives aggregate k_n toward zero (see Results). One property of this mapping must be made explicit for TCGA: applied to log2(TPM + 1) values, the softmax is mathematically equivalent to p_i \u221d (TPM + 1)^{1/ln 2}\u2014an implicit power transformation of the counts that was not disclosed in earlier versions of this pipeline. We therefore recomputed every TCGA analysis with the linear normalization p_i = (TPM + 1)/\u03a3_j(TPM_j + 1): all qualitative conclusions were unchanged (the NN > TT \u03c9 reversal preserved in 5 of 5 cancer types; kn_floor saturation 0; all severity-gradient directions preserved), with full side-by-side results in the Supplementary Information.')

p('A note on package parity: all hybrid-scheme analyses reported in this paper (mouse pilot, Tabula Sapiens, TCGA, brain atlas) select the k_f genes of each pair as the top-200 genes ranked by the absolute pseudobulk difference. The released package\u2019s func_method = "pairwise_de" option instead runs a two-directional Wilcoxon test and yields a different gene set; the reported abs-diff scheme is provided exactly as func_method = "pairwise_absdiff" in package version 0.5.0. All \u03c9 values reported here were computed with the abs-diff scheme. The package\u2019s permutation test (bootstrap_test()) reproduces the reported null by default: reselect_identity = True holds the HK set fixed while re-selecting the k_f set at every permutation under the same per-pair rule as the observed value; the legacy fixed-gene-set null remains available as reselect_identity = False and is anti-conservative relative to re-selection (cf. the TCGA fixed-panel caveat).')

heading('Dimensionality invariance of JS divergence', level=2)
p(f'Because k_n is computed on ~1,130 HK genes and k_f on 200\u20132,000 HVG genes, we verified that JS divergence is not systematically biased by gene set dimensionality. A simulation of {int(_phaseC_dim.get("n_trials", 2000)):,} random Dirichlet distribution pairs across dimensions 50\u20135,000 showed mean JS divergence effectively constant (0.155\u20130.159, ratio = {_phaseC_dim.get("ratio_2000_to_1130", 1.001):.3f} between d = 1,130 and d = 2,000; Supplementary Fig. 13). The systematic inflation of k_f relative to k_n (\u03c9 = 7.70 for equivalent populations) therefore arises from HVG selection bias rather than dimensional mismatch; the calibrated omega (\u03c9_cal = \u03c9 / 7.70) absorbs this bias into the empirical baseline, and the permutation null\u2014constructed using the same gene sets\u2014ensures internal consistency.')

heading('Permutation test', level=2)
p('Statistical significance was assessed with permutation tests whose exchangeability unit and gene-selection handling follow the structure of each dataset. For the mouse pilot, Tabula Sapiens, and TCGA per-cancer analyses, labels were permuted between groups (cell labels, or tumor/normal labels across bulk samples; B = 1,000); pseudobulks were recomputed after each permutation and \u03c9 recalculated under the same per-pair gene-selection procedure as the observed value, so the null incorporates the gene-selection step. The TCGA per-cancer permutation test additionally holds the identity gene set fixed across permutations (a global HVG panel selected once on the observed grouping); because this fixed-panel null can only deflate the null k_f relative to re-selection, it is anti-conservative, and the corresponding TCGA P-values (all P > 0.9) should be read with this caveat. These P > 0.9 values coexist with cluster-bootstrap CIs that exclude 1 in four of five cancer types, and the two are not contradictory: the permutation null tests exchangeability of tumor and normal labels at the aggregate level under a fixed identity panel\u2014a test with essentially no power here, because aggregate k_n sits at the denominator floor in 3 of 5 cancer types\u2014whereas the bootstrap CIs quantify the sampling uncertainty of the within-cancer NN/TT pairing structure. The aggregate-level permutation test is accordingly uninformative for the reversal claim, which rests on the pair-level cluster bootstrap. For the brain atlas, the authoritative null is the block-shuffle permutation described under \u201cMultiplicative residual model\u201d (10x libraries permuted across regions, per-pair genes re-selected at every permutation; B = 1,000). Empirical P-values use the one-sided upper-tail formula P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1), where the +1 pseudocount avoids P = 0; the brain per-pair screen instead uses the one-sided lower-tail formula (anomalously low \u03c9), with the upper tail reported as a complementary summary. The one-sided default is appropriate because our hypothesis is directional: we test whether observed \u03c9 exceeds the null expectation, not whether it differs in either direction. Standardized effect size (SES = (\u03c9_obs \u2212 mean(\u03c9_null)) / sd(\u03c9_null)) is reported as a non-parametric descriptive statistic complementing the permutation P-value, not a parametric test statistic such as Cohen\u2019s d. Benjamini-Hochberg (BH) FDR correction [44] is applied within each dataset; larger-scale analyses are supplemented with non-parametric tests and descriptive statistics.')

heading('Datasets', level=2)
p(f'Tabula Muris FACS SmartSeq2 [8]: {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs (liver, kidney, spleen, lung, heart, bone marrow). Post-quality-control (QC): {_ds["tabula_muris_ct_entries"]} cell-type entries (each with at least 20 cells and at least one mouse contributing at least 10 cells), yielding C(38, 2) = 703 analyzed pairs. Highly variable genes selected using scanpy [45] with flavor="seurat" [46,47] and n_top_genes={_ds["n_hvg"]:,}.')

p(f'Tabula Sapiens v1.0 [9]: accessed via CZ CELLxGENE Discover [48]. Post-QC: {_ds["tabula_sapiens_cells"]:,} cells ({_ds["tabula_sapiens_organs"]} h5ad files total), {_ds["tabula_sapiens_genes"]:,} genes, {_ds["tabula_sapiens_ct_entries"]} cell-type entries across 6 organs. Of these, {_h["n_ct_analyzed"]} entries passed the pairwise-analysis filters (at least 20 cells per entry and at least one donor with at least 10 cells; "unknown" annotations excluded), yielding C({_h["n_ct_analyzed"]}, 2) = {_h["n_pairs_total"]:,} analyzed pairs. HK genes: HRT Atlas v1.0 reference ({_ds["hrt_atlas_n_hk"]:,} genes; human column).')

p(f'TCGA bulk RNA-seq [49]: five cancer types from NCI Genomic Data Commons, accessed via TCGAbiolinks [50] and cBioPortal [51] APIs. LUAD: 493 tumor + 76 normal; LUSC: 534 tumor + 58 normal; LIHC: 398 tumor + 57 normal; KIRC: 750 tumor + 82 normal; BRCA: 1010 tumor + 109 normal (3,567 samples entering the pair-level analysis: of the 3,596 expression-matrix samples, 3 do not appear in the assembled pair table, and 26 further samples appear only in tumor\u2013normal pairs and never enter the tumor\u2013tumor or normal\u2013normal comparisons; the pair table itself spans 3,593 unique barcodes, the denominator of the barcode audit in Methods). TPM values from UCSC Xena; within each cancer type, genes with mean expression below 0.5 TPM were removed, and the retained values were log2(TPM + 1) transformed. BRCA PAM50 subtype assignments [52,53] were retrieved from cBioPortal (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute; 522 samples with subtype calls). LIHC Edmondson grade [54]: from cBioPortal, 288 tumors. LUAD mutations: from cBioPortal, 492 samples (61 EGFR, 120 KRAS, 311 WT). Sample provenance followed the TCGA barcode sample-source code (positions 14\u201315): the 32 cell-line-derived LIHC samples (source code CC, ILSBio liver cancer lines) shipped in the LUSC matrix were assigned to LIHC following a barcode audit, and all counts above reflect this corrected assignment.')

p('Human brain atlas [12]: Siletti et al. (2023) single-nucleus RNA-seq (v3.11) from CZ CELLxGENE Discover [48] (collection ID: 283d65eb-dd53-496d-adb7-7570c7caa443). We used the Nonneurons.h5ad dataset (888,263 nuclei, 59,480 genes, 108 brain regions), classified by supercluster_term annotation into 10 major non-neuronal classes; after filtering (\u2265 20 nuclei per (region, cell_type) group, \u2265 50 per region), 886,808 nuclei contributed to the analysis (astrocytes 155,025; oligodendrocytes 490,246; oligodendrocyte precursors 105,723; committed oligodendrocyte precursors 4,118; microglia 91,826; vascular cells 9,586; fibroblasts 8,897; ependymal cells 5,779; choroid plexus 7,643; Bergmann glia 7,965). Pseudobulks were computed as cell-count-weighted means of per-library (10x sample) mean expression vectors per group, then normalized (Scanpy normalize_total, target_sum = 10,000) followed by log1p at the pseudobulk level. CKI \u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs) with the hybrid scheme; HK genes came from the HRT Atlas v1.0 reference (1,115 genes matched to the Siletti annotation). For computational efficiency, per-pair identity-gene selection was restricted to a pre-filtered pool of the 5,000 non-HK genes with the highest mean expression, within which the top-200 genes with the largest absolute pseudobulk difference were selected per comparison (HK genes excluded).')

heading('Method comparison', level=2)
p(f'We computed five metrics on all {_h["n_pairs_total"]:,} Tabula Sapiens cell-type pairs: CKI \u03c9 (hybrid scheme), raw JS divergence (all genes), Spearman distance (1 - \u03c1), cosine distance (1 - cos \u03b8), and marker Jaccard distance (1 - Jaccard index of top-200 expressed genes). To avoid donor-pair proliferation, one pseudobulk was computed per cell-type entry from its largest donor (the donor with the most QC-passing cells); the method comparison therefore does not capture inter-donor variability. Inter-metric Spearman correlations were computed using scikit-learn.')

heading('Multiplicative residual model for brain regional analysis', level=2)
p('For the brain regional analysis, we designed a multiplicative model to detect (cell_type, region_pair) combinations with anomalously low \u03c9: expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, where \u03bc_ct is the cell type\u2019s global mean \u03c9, \u03bc_pair the region pair\u2019s mean \u03c9, and \u03bc_grand the global mean over all 31,764 pairs (38.55); the multiplicative residual = observed / expected, and a residual well below 1 indicates the cell type is far less differentiated between those regions than expected from its global plasticity and the pair\u2019s overall divergence. Three confidence tiers were defined: Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the region pair), Moderate (residual < 0.5, \u03c9 < 25), and Weak (residual < 0.75, \u03c9 < 35). Statistical significance was assessed with a block-shuffle permutation null that preserves the joint cell-type \u00d7 region design: 10x Chromium libraries (sample_id) were treated as blocks and the sample-to-region assignment randomly permuted across libraries (preserving per-region library counts), after which region pseudobulks, all 31,764 pair \u03c9 values, and residuals were recomputed; because each library\u2019s cells move together, this null retains library-level structure while breaking the cell\u2013region association and is markedly more conservative than per-cell label shuffling. B = 1,000 permutations were run (minimum resolvable P = 1/1,001 \u2248 9.99 \u00d7 10\u207b\u2074). Per-pair empirical P-values used the one-sided lower-tail formula P = (count(\u03c9_null \u2264 \u03c9_obs) + 1)/(B + 1), appropriate because candidates are defined by anomalously low \u03c9; the complementary upper-tail P-value was computed for every pair and both tails are reported. Benjamini-Hochberg FDR correction was applied across all m = 31,764 pairs. No pair reached q < 0.05 (minimum q = 0.520); at this multiplicity q < 0.05 would require B \u2248 6 \u00d7 10\u2075 permutations or ~635 P-values at the permutation floor (see Statistics and reproducibility), so this outcome reflects permutation resolution rather than evidence against the candidates. The 31 Strong-tier pairs with raw P < 0.05 are reported as hypothesis-generating signals, prioritized for future lineage-tracing validation, with interpretation restricted to the predefined Strong tier rather than the full 31,764 search space. A cell-type-level test additionally asked whether regional structure significantly raises a cell type\u2019s mean \u03c9 relative to the same null (one-sided upper-tail P across B = 1,000 permutations). As a negative control for null calibration, the same test was re-run on pseudo-regions obtained by splitting each region\u2019s libraries uniformly at random into two halves (seed fixed; 127,756 pseudo-pairs across the ten classes; Supplementary Note 12).')


heading('Robustness and calibration analyses', level=2)
p('Donor confounding and within-donor gradient (brain). The brain atlas contains nuclei from four donors, and 94.5% of region pairs share at least one donor (median top-donor share within a region: 0.61). To test whether the pooled class-level gradient reflects donor identity rather than regional biology, we recomputed cross-region \u03c9 using only same-donor (donor, region) pseudobulk pairs: every pair of regions with at least 20 nuclei from the same donor contributed one comparison, and class means were aggregated over all such pairs (astrocytes: 11,139 pairs from 261 donor-region blocks; Bergmann glia: 10 pairs). k_n estimator sensitivity (brain). For all 31,764 pairs we compared four aggregation schemes: per-pair k_n (the reported estimator), an aggregate-first estimator (k_n computed once per cell type from class-level region pseudobulks), a global-k_n variant (a single grand-mean k_n shared by all classes), and k_f-only and k_n-only orderings; agreement was summarized as Spearman rank correlation of the ten class means. Scheme-matched split-half calibration. To test whether the mouse-derived calibration factor transfers, we repeated the random-split-of-the-same-population calibration inside each large single-cell dataset using exactly the gene-selection and pseudobulk pipeline of the corresponding analysis. Brain: for each cell class, the three regions with at least 200 nuclei were split into random halves (B = 50 splits per population; 29 populations), and 95% bootstrap CIs were obtained by resampling the 29 population means (the between-population bootstrap carries the variance relevant to the baseline, so the smaller per-population split count does not inflate the reported CIs relative to the B = 1,000 used in the main inference). Tabula Sapiens: for each (organ, cell type) group from the largest donor with at least 100 cells passing QC (71 populations across six organs), cells were randomly split into halves (B = 50) and \u03c9 computed with the same per-pair hybrid pipeline as the main Tabula Sapiens analysis. Lineage enrichment and tier sensitivity (brain). Enrichment of oligodendrocyte-lineage classes among Strong candidates was tested with a hypergeometric test over the 31,764 pairs (12,775 belonging to the lineage), corroborated by permutation (B = 100,000); tier-threshold sensitivity was assessed by recomputing the Strong set and lineage enrichment over a grid of residual caps (0.2\u20130.4) and \u03c9 caps (12\u201325). Class-size confounding and threshold sensitivity (brain). Class-mean k_n and \u03c9 were tested against log10(class nuclei count) and mean detection depth (Spearman and Pearson correlations); an equal-n control downsampled every class to 4,118 nuclei (the smallest class; 20 replicates) and recomputed class rankings and the endpoint gradient; and the full landscape was recomputed at group-size thresholds of 10, 50, and 100 nuclei in addition to the reported 20 (script notebooks/86_brain_downsample_threshold_v44.py).')

p('Donor-stratified null (brain). To ask whether the class-level significance of the pooled block-shuffle null survives when library-to-region assignments cannot cross donor boundaries, we re-ran the permutation test with a donor-stratified shuffle: within each cell class, the sample_id-to-region assignment was permuted only among libraries belonging to the same donor (B = 1,000; identical gene set, pseudobulks, and \u03c9 pipeline as the free shuffle). This scheme preserves each donor\'s library counts and the per-region block-size structure within donors while breaking the library-to-region association; libraries from donors contributing a single library to the class (non-shufflable blocks; e.g., 8 of 606 astrocyte libraries) were held fixed, and permutations returning the identity assignment were retained as valid draws. Class-level significance used the same one-sided upper-tail statistic, P = (count(mean \u03c9_null \u2265 mean \u03c9_obs) + 1)/(B + 1). The accompanying free-null P-values come from an independent Monte-Carlo re-run within the same script (same B and pipeline), so small differences from the primary analysis (ependymal cells P = 0.058 here versus 0.075; committed oligodendrocyte precursor cells (OPCs) P = 0.004 versus 0.005) reflect Monte-Carlo variability; the donor-stratified null is strictly the more conservative test.')

heading('Ground-truth simulation', level=2)
p('To measure specificity and sensitivity against a known ground truth, we injected perturbations of known magnitude into a real single-cell background: Tabula Muris FACS marrow B cells (1,848 cells). Each replicate resampled two independent groups of 200 cells (gene set: 1,064 matched HK genes plus the 5,000 non-HK genes with the highest global means, mirroring the brain pipeline). A functional signal was injected as a multiplicative shift of 2^\u03b4 (\u03b4 = 0.125\u20132) on a fixed module of 200 non-HK genes in group B; neutral perturbations were injected separately as a 2^\u03b7 shift (\u03b7 = 0.25\u20131) on HK genes in group A (neutral drift that should not count as functional divergence) or Poisson noise across all genes in group A (\u03b5 = 0.3\u20131, technical batch noise). Six metrics were computed per replicate with the identical code path as the brain analysis (\u03c9, k_f, k_n, raw JS divergence over the full kept gene set, cosine distance, k_f/k_total). Signal scenarios were repeated with three independent random module draws (seeds 42, 137, 2024); detection thresholds were calibrated per metric as the 95th percentile of 200 baseline replicates, so type-I error and power refer to a common nominal level (the 95th-percentile threshold estimate itself carries Monte Carlo noise of roughly \u00b11.5 percentage points at 200 baseline replicates, small relative to the between-metric gaps reported). Robustness scenarios (30% dropout, twofold depth difference, fourfold cell-count imbalance) and module-size sensitivity (m = 50, 200, 500) were run at \u03b4 = 0.25 and \u03b4 = 1. The entire design was repeated in a second background within the same Tabula Muris FACS platform\u2014skin keratinocyte stem cells (1,371 cells)\u2014with identical grids, module seeds, group sizes, and code path (1,750 replicates per background across the full grid). Full results: Supplementary Note 1 and the results/groundtruth_simulation_*.csv files of the companion repository.')

heading('Perturbation demonstration (IFN-\u03b2 PBMC)', level=2)
p('To test \u03c9 on a real perturbation with known ground truth, we re-analyzed the droplet arm of Kang et al. [14] (GEO: GSE96583): peripheral blood mononuclear cells from eight donors, split into control and 6-hour IFN-\u03b2-stimulated conditions and captured in two 10x lanes, with donor assignment by genetic demultiplexing as provided by the original authors. All control cells sit in one lane and all stimulated cells in the other, so condition is fully confounded with capture lane (disclosed in Supplementary Note 6): every metric inherits the same confound, and cross-metric contrasts, not absolute detection, are the informative quantity. Singlets with annotated cell types were retained (24,413 cells across six cell types; Ensembl gene identifiers mapped to HGNC symbols). Pseudobulks were computed per (donor, condition) from raw counts, normalized to 10,000 counts, and log1p-transformed; \u03c9, k_f, k_n, and raw JS were evaluated with the per-pair top-200 scheme for two comparison classes: stimulated-versus-control within donor (perturbation class) and donor-versus-donor within condition (donor-drift class). A split-half baseline (six random half-splits per group) anchored the calibrated scale. The significance of the perturbation effect was assessed by permuting condition labels within donor (B = 1,000; genes re-selected at every permutation, one-sided upper tail), and class separability was summarized as the exact rank AUC of each metric within each cell type. Script: notebooks/79_kang_ifnb_demo.py; outputs: results/kang_ifnb_demo_pairs.csv, results/kang_ifnb_demo_summary.json.')

heading('Neutral-drift calibration on technical replicates', level=2)
p('To test the neutral-drift specificity property on real data with a ground truth of no functional difference, we constructed technical-replicate pairs and calibrated every metric against a per-pair size-matched (n-matched) cell-shuffle null: the nuclei of the two groups being compared are pooled, randomly permuted, and re-split into disjoint subsets of exactly the observed group sizes (n_a, n_b), so each observed pair is compared against a null distribution that matches its donor, cell type, and group sizes while containing no group structure; B = 200 permutations per pair (Kang) or 100/30/30 for brain tiers T1/T2/T3; at B = 30 the per-pair exceedance indicator resolves to 1/31, so the T2/T3 tier rates carry Monte-Carlo noise of a few percentage points and are read as tier-level, not per-pair, calibrations. Calibration is reported as the ratio observed / null median, and the false-positive element as observed > own null 95th percentile. Kang batch 1 [14]: unstimulated PBMCs from eight donors captured across three 10x lanes (lanes A and B hold four donors each, lane C holds all eight, so every donor appears in exactly two lanes); singlets with annotated cell types and at least 50 cells in both lanes of a donor yielded 30 same-donor, same-condition cross-lane pairs across six cell types, evaluated with the per-pair top-200 scheme on k_n (HRT Atlas HK genes [13]), k_f, \u03c9, raw JS, and cosine distance. Brain drift ladder [12]: from the 888,263 non-neuronal nuclei and 606 10x libraries, 2,732 (cell class, library) groups with at least 20 nuclei defined library-level pairs in three tiers\u2014T1, same (donor, region) different libraries, all 2,161 pairs; T2, same region different donors, 1,089 pairs (random subsample capped at 200 per cell class); T3, same donor different regions, 1,656 pairs (same cap; the cap makes the cell-class composition of T2/T3 availability-dependent, so cross-tier comparisons mix class composition with drift tier\u2014per-class values are reported in Section 3.12 of the Supplementary Information)\u2014evaluated with the brain pipeline (HK genes plus top-5,000 non-HK genes by mean expression; per-pair top-200 selection) for seven metrics: k_n, k_f, \u03c9, raw JS, cosine distance, Spearman distance (1 \u2212 \u03c1), and a pairwise marker Jaccard distance defined as 1 minus the Jaccard index of each group\u2019s top-200 markers (genes ranked by pseudobulk expression minus the cell-weighted background of all other cell classes in the same reduced gene set). Random seeds: 20260918 (Kang), 42 (brain). Scripts: notebooks/nc49_pilot_kang_techrep.py, notebooks/nc49_brain_drift_ladder.py; outputs: results/nc49_pilot_kang_techrep.csv, results/nc49_brain_drift_ladder.csv, and figure notebook nc49_fig_drift_ladder.py (companion repository). Section 3.12 of the Supplementary Information reports the full audit of design, diagnostics, and per-class results.')

heading('Fixed gene-panel ablation', level=2)
p('To test whether the brain conclusions depend on the per-pair circular selection of k_f genes (top-200 genes ranked by the absolute difference of the same two pseudobulks on which k_f is computed), we recomputed the entire observed brain landscape\u2014all 31,764 pairs, with identical keep gene set, pseudobulks, and k_n\u2014under three alternative gene-selection schemes: (i) a fixed panel of the 2,000 non-HK genes with the highest global mean expression (selected once, pair-independent); (ii) a leave-pair-out panel, in which the top-200 genes for a pair are selected by the mean absolute pseudobulk difference over all other region pairs of the same cell type (adaptive but not circular for the tested pair); and (iii) all 5,000 non-HK genes of the keep set. The reference implementation reproduced the reported landscape exactly (maximum per-pair |\u0394\u03c9| = 6.4 \u00d7 10\u207b\u00b9\u00b3). We summarized pair-level and class-level rank agreement (Spearman), the circularity inflation as the per-pair ratio of k_f under the reported scheme to k_f under each alternative, and the agreement of the multiplicative-residual ranking. A scheme-matched block-shuffle null (B = 200; minimum resolvable P \u2248 0.005) was rerun under the leave-pair-out scheme to verify that class-level significance does not depend on circular selection. Full results: Supplementary Note 7 and the results/fixed_panel_ablation_* files of the companion repository.')

heading('Per-sample divergence and group statistics (TCGA)', level=2)
p('Per-tumor statistics were derived from the linear-normalization pair table (35,306 pairs: 2,000 TT pairs per cancer type drawn by seeded subsampling, complete NN pairs, and 2,000 TN pairs per cancer type; sample-labelled; the seeded subsampling carries a Monte-Carlo error of roughly 0.01\u20130.02 ratio units on the NN/TT mean ratio, below the between-cancer differences reported), as the mean of \u03c9, k_f, and k_n over all pairs in which a given sample participates (median 4\u201311 pairs per tumor across cancer types). Group-level NN/TT and k_n ratios are reported as ratios of means with 95% confidence intervals from a sample-level cluster bootstrap (B = 1,000; seed 42): tumor and normal samples were resampled with replacement independently, each pair reweighted by the product of its endpoint resampling weights, and the ratio recomputed per resample; 95% CIs are the 2.5th and 97.5th percentiles of the resampled ratios. LUAD driver groups were assigned by matching cBioPortal mutation labels to the expression matrix by 15-character TCGA barcode (75 EGFR-labelled and 161 KRAS-labelled aliquots, of which 62 EGFR and 122 KRAS matched the matrix; 2 double mutants excluded), yielding 61 EGFR, 120 KRAS, and 311 wild-type tumors with pair coverage. Between-group differences were tested with Kruskal-Wallis followed by Dunn post-hoc tests with Holm correction (manual implementation, tie-corrected rank variances); group mean differences are reported with within-group bootstrap 95% CIs (B = 1,000). For covariate adjustment, stromal and immune admixture was scored per sample with the official ESTIMATE gene sets (141 stromal and 141 immune genes) using the rank-based single-sample enrichment algorithm over all 45,504 expressed genes of the five-cancer merged matrix; the combined stromal-plus-immune score served as the admixture covariate (it is monotonically equivalent to published ESTIMATE purity, leaving regression-based adjustment invariant). Smoking status (ever/never, TCGA tobacco-smoking-history indicator), age, sex, and pack-years for LUAD were obtained from cBioPortal (study luad_tcga, patient-level clinical data; smoking status available for 508, pack-years for 356, and sex for 522 patients) and merged by patient barcode (427 of 492 tumors with known smoking status, 87%). LUAD group contrasts were re-estimated by OLS with the admixture score as a covariate (metric ~ group + z-scored admixture), with ever-smoker status as a covariate, and in a combined model including both (with an age- and sex-adjusted variant); pack-years were not modeled owing to high missingness and are reported descriptively. The LIHC survival analysis used Cox proportional-hazards regression (statsmodels PHReg) with per-tumor \u03c9 standardized to unit SD (hazard ratios per SD), adjusted for AJCC stage (I\u2013IV), Edmondson grade (G1\u2013G4), age, and sex, with listwise deletion of missing covariates; k_f-only, k_n-only, and tumor\u2013normal-\u03c9 exposures were run as sensitivity models. Scripts: notebooks/nc49_tcga_main.py, notebooks/nc49_pilot_lihc_cox.py, notebooks/nc49_tcga_purity.py, notebooks/nc49_tcga_luad_smoking.py; outputs: results/nc49_tcga_pancancer.csv, results/nc49_tcga_luad_mutation.csv, results/nc49_pilot_lihc_cox.csv, results/nc49_tcga_purity.csv, results/nc49_tcga_admix_scores.csv, results/nc49_tcga_luad_smoking.csv.')

heading('Clinical severity analysis', level=2)
p('In supplementary within-cancer-type stratification analyses, we computed intratumoral \u03c9 for samples within each clinical stratum using the hybrid scheme. BRCA PAM50 subtype calls [52,53] were retrieved directly from the cBioPortal API (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute; 522 samples with subtype calls, cached locally for reproducibility, of which 506 had matched expression data and entered the analysis); no de novo centroid-based classification was performed in this work. LIHC Edmondson grades [54] came from cBioPortal (n = 288 tumors), and LUAD mutation status (EGFR, KRAS, WT) from cBioPortal (n = 492 samples). Between-stratum differences were tested with Kruskal-Wallis (PAM50 subtypes, LUAD mutations) and trend with Jonckheere-Terpstra (Edmondson grades). Paired versus unpaired tumor-normal comparisons are reported as descriptive statistics (medians and interquartile ranges, IQRs) without formal P-values, as the paired design does not meet the independence assumption of standard between-group tests. k_f-only and k_n component controls for the ordering claims were computed with the identical pipeline (per-cancer loading, gene filtering, and TT-pair subsampling), stratifying per-tumor mean k_f and k_n exactly as for \u03c9; per-cell-type mean k_f for the cross-organ ranking was computed from the same pseudobulks and per-pair gene selection (notebooks/83_kf_only_ordering.py; results/kf_only_ordering.csv; results/kf_only_severity.csv; Supplementary Note 9).')

heading('Computational environment', level=2)
p('Typical runtime for a single cell-type pair is under 5 minutes on a standard laptop; the full brain analysis (31,764 pairs) required approximately 72 core-hours on a Windows x64 workstation with at least 32 GB RAM (the verified environment of the Reproducibility Guide, Section 1.1 of the Supplementary Information). All analyses were performed in Python 3.14.4 with scanpy 1.12.1 [45], scipy \u2265 1.10.0, numpy \u2265 1.23.0, pandas \u2265 1.5.0, matplotlib \u2265 3.6.0, seaborn [55] \u2265 0.12.0, and scikit-learn [56] \u2265 1.2.0; random seeds were fixed at 42 throughout, except scripts 77/78/79, which used seed 20260903, and the small-cluster studentized bootstrap-t analysis (notebooks/89_cluster_boot_v45.py), which used seed 20260905. Permutation results are stable with respect to seed choice: with B = 1,000 permutations the Monte Carlo standard error of the empirical P-value is approximately 0.016 at P = 0.5, so seed variation has negligible impact on statistical conclusions.')

heading('Statistics and reproducibility', level=2)
p('We report summary statistics as mean \u00b1 s.d. (range) or median [IQR] as noted. Resampling-based inference [57] (permutation tests for P-values; bootstrap for confidence intervals) was performed for all four datasets with B = 1,000: label permutation for the mouse pilot (15 cell-type pairs, 6 calibration control populations with 50 split-half replicates each), human Tabula Sapiens, and TCGA, and the block-shuffle null for the brain atlas (Methods). Empirical P-values are one-sided, P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1), with the exchangeability unit following the dataset structure; in each iteration pseudobulks are recomputed from the permuted groups and \u03c9 recalculated with identity genes re-selected on the permuted pseudobulks (the TCGA per-cancer permutation test is the sole exception, holding a fixed HVG panel; Methods). Benjamini-Hochberg FDR correction [44] is applied within each dataset, with two levels distinguished. First, group-level tests (one test per cell class, cell type, or cancer type): brain cell-class (m = 10), human per-cell-type (m = 17), mouse pilot (m = 15), TCGA per-cancer (m = 5); the BH thresholds for the most significant test (0.05/m) are 5.0 \u00d7 10\u207b\u00b3, 2.9 \u00d7 10\u207b\u00b3, 3.3 \u00d7 10\u207b\u00b3, and 1.0 \u00d7 10\u207b\u00b2\u2014all above the minimum resolvable permutation P-value of 9.99 \u00d7 10\u207b\u2074 at B = 1,000, so resolution is sufficient for every group-level test. Second, the brain per-pair screen, with BH correction across all m = 31,764 region pairs: the BH threshold for the smallest ordered P-value (0.05/31,764 \u2248 1.6 \u00d7 10\u207b\u2076) lies roughly 600-fold below the smallest resolvable P, so q < 0.05 is unattainable unless ~635 of the 31,764 P-values sit at the permutation floor (a regime the empirical FDR analysis shows is not approached) or B \u2248 6 \u00d7 10\u2075 permutations are run. The per-pair FDR outcome (minimum q = 0.520) is consequently a statement about permutation resolution rather than evidence against any candidate, and we report it together with the raw permutation P-value distribution (1,960 of 31,764 pairs at raw P < 0.05, slightly more than the ~1,588 expected under a global null).')

p('Bootstrap 95% confidence intervals for \u03c9 point estimates were computed by resampling observed pair-level \u03c9 values with replacement (B = 10,000) and reporting the 2.5th and 97.5th percentiles. Because pairs are nested within regions, we additionally computed region-clustered block bootstrap 95% CIs (B = 2,000; the 108 regions resampled with replacement, all landscape statistics recomputed per resample): gradient 6.10 [5.55, 9.63], grand mean \u03c9 38.55 [36.35, 40.73], Strong-candidate count 39 [12, 74]; these cluster-aware intervals are wider and are the preferred uncertainty summary for landscape-level quantities. Per-class calibrated quantities additionally propagate the uncertainty of the calibration denominator: a joint region-clustered bootstrap (B = 5,000) resamples regions with replacement for the numerator (region-clustered weighted resampling, pair weights equal to the product of the two regions\u2019 library counts) while independently resampling the split-half control populations for the denominator (two-stage: control populations first, random half-splits within each drawn population second), and reports the 2.5th and 97.5th percentiles of the ratio; this joint interval supersedes the earlier i.i.d. interval, which propagated neither source and was anti-conservative (Supplementary Note 3; notebooks/81_perclass_uncertainty.py). The studentized (bootstrap-t) region-clustered intervals pivot the statistic by an influence-function (multiplier) sandwich standard error of the multiplicity-weighted pair mean re-evaluated within each resample, with ratios studentized on the log scale via the delta method (B = 5,000, seed 20260905; Monte Carlo coverage 0.953/0.951 at 6\u20137 clusters; notebooks/89_cluster_boot_v45.py). The \u03c9 distribution was characterized using skewness, excess kurtosis, and normality tests (Shapiro-Wilk for n \u2264 5,000; D\u2019Agostino-Pearson for n > 5,000): all distributions were right-skewed (brain 2.22; mouse pilot 0.99; human 1.17), and normality was rejected for the large datasets (brain P < 2.2 \u00d7 10\u207b\u00b9\u2076; human P = 7.6 \u00d7 10\u207b\u2074\u00b2) but not for the mouse pilot (P = 0.071, minimal power at n = 15). The split-half calibration experiment (50 random-split replicates across six control populations of the same tissue, 300 \u03c9 values) yielded a mean \u03c9 = 7.70 (95% CI [7.37, 8.02]; SD of replicate means = 1.15, pooled SD = 3.63; the legacy n = 6 estimate 6.67 is consistent with it), reflecting systematic inflation of k_f relative to k_n from identity-gene selection; the permutation test accounts for this by constructing the null under the same gene-selection procedure.')

p('Statistical conventions. All P-values are from one-sided permutation tests (B = 1,000 for mouse/human/TCGA/brain and for the multiplicative residual model block-shuffle null) unless otherwise specified. Benjamini-Hochberg FDR correction was applied within each dataset. Non-parametric tests (Spearman correlation, Mann-Whitney U, Kruskal-Wallis, Jonckheere-Terpstra) are two-sided and reported with exact P-values, with one exception: the mouse-pilot X-versus-C calibration contrast (Fig. 2c) uses a one-sided Mann-Whitney U test (H1: \u03c9_X > \u03c9_C) matching the directional calibration hypothesis; as an exploratory pilot (n = 15) this contrast is reported for transparency rather than as a pre-registered test. Descriptive statistics are reported as mean \u00b1 SD or median [IQR] as indicated. Effect sizes include standardized effect size (SES = (\u03c9_obs \u2212 mean(\u03c9_null)) / sd(\u03c9_null)), computed from the permutation null distribution. Bootstrap 95% confidence intervals use stratified resample counts reported per analysis (B = 1,000 for the composition cluster bootstrap, 1,000 for TCGA ratio CIs, 2,000 for region-clustered brain intervals, 5,000 for the joint and studentized small-cluster analyses, and 10,000 for simple resampling of pair-level point estimates), with the Monte Carlo error of each interval reported alongside it in the Supplementary Information. All analyses use JS divergence with base-2 logarithm. Sample sizes (n) are reported for each comparison.')

heading('Use of large language models', level=2)
p('During the preparation of this work the authors used AI-assisted tools (large language model-based assistants) for computational debugging, statistical code review, and language editing. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.')


# ============================================================
# DATA AVAILABILITY / CODE AVAILABILITY (NC: after Methods, before References;
# no literature citations inside either section)
# ============================================================
heading('Data availability', level=1)
p('Tabula Muris data: GEO accession GSE109774. Tabula Sapiens data: CZ CELLxGENE Discover (https://cellxgene.cziscience.com/, accessed July 2025). TCGA data: NCI Genomic Data Commons (https://portal.gdc.cancer.gov/). HRT Atlas (optional human/mouse housekeeping-gene reference): https://www.housekeeping.unicamp.br. Human brain atlas: CZ CELLxGENE Discover, collection ID 283d65eb-dd53-496d-adb7-7570c7caa443 (https://cellxgene.cziscience.com/collections/283d65eb-dd53-496d-adb7-7570c7caa443, accessed July 2025). Kang et al. IFN-\u03b2-stimulated PBMC data: GEO accession GSE96583. BRCA PAM50 subtype assignments: cBioPortal (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute). MSigDB Hallmark gene sets (Liberzon et al. 2015; see References): accessed via the Enrichr gene-set library (MSigDB_Hallmark_2020; local mirror data/tcga/hallmark_2020.gmt in the companion repository). Supplementary Tables 1\u20134 are cited in the main text; Supplementary Tables 5\u201319 provide the per-analysis numerical tables cited within the Supplementary Information.')

heading('Code availability', level=1)
p('The CKI source code (v0.5.0) is publicly available at https://github.com/zhanglknt/CKI-cell-type-identification (tag v0.5.0) under the MIT License. A permanent archival copy has been deposited at Zenodo (concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.0: 10.5281/zenodo.22735744). The package requires Python \u22653.10 and runs on Linux, macOS, and Windows. A Dockerfile is provided in the repository for containerized reproducibility. All analysis notebooks and processed data matrices are available in the same GitHub repository (tag v0.5.0) and are included in the Zenodo archive (concept DOI: 10.5281/zenodo.20405458).')

# ============================================================
# REFERENCES (NC: Nature style; superscript citations in text)
# ============================================================
heading('References', level=1)

for i, ref in enumerate(_refs_nc, 1):
    ref_p_nc(f'{i}. {ref}')


# ============================================================
# ACKNOWLEDGEMENTS / AUTHOR CONTRIBUTIONS / COMPETING INTERESTS
# (NC fixed order, after References; Funding merged into Acknowledgements)
# ============================================================
heading('Acknowledgements', level=1)
p('This work was supported by the National Natural Science Foundation of China (NSFC) under grant number 32370682. We thank the Tabula Muris Consortium, Tabula Sapiens Consortium, TCGA Research Network, and the Siletti et al. brain atlas team for making their data publicly available. We also thank the developers of scanpy, scipy, scikit-learn, and the broader open-source scientific Python ecosystem for the computational infrastructure that made this work possible. We are grateful to the HRT Atlas team for maintaining the housekeeping gene reference resource.')

heading('Author contributions', level=1)
p('X.W. performed the analyses and wrote the first draft of the manuscript. L.Z. conceived and supervised the study, developed the CKI algorithm, acquired funding, and finalized the manuscript. Both authors read and approved the final manuscript.')

heading('Competing interests', level=1)
p('The authors declare no competing interests.')

p('Supplementary Information is available for this paper: Supplementary Notes 1–15, Supplementary Figs. 1–13, Supplementary Tables 1–19, and the Reproducibility Guide (providing step-by-step instructions, the verified computational environment, and spot-check values for reproducing all analyses, figures, and tables reported in this work).')

p('Correspondence and requests for materials should be addressed to L.Z.')



# ============================================================
# FIGURE LEGENDS
# ============================================================
heading('Figure legends', level=1)

p('Figure 1. The CKI framework. (a) Conceptual analogy between Ka/Ks in molecular evolution and CKI in transcriptomics. Ka/Ks uses synonymous substitution rate (Ks) as a neutral baseline; \u03c9 = Ka/Ks > 1 indicates positive selection (a heuristic analogy only, not a formal population-genetic claim). CKI uses housekeeping gene divergence for k_n\u2014the constrained counterpart of the synonymous baseline\u2014and identity gene divergence for k_f\u2014the counterpart of nonsynonymous divergence; \u03c9 = k_f/k_n quantifies transcriptomic divergence relative to the baseline, read against the empirical calibration baseline rather than against 1. (b) Computational pipeline: raw count matrix \u2192 pseudobulk \u2192 JS divergence on HK genes (k_n) and identity genes (k_f) \u2192 \u03c9 = k_f/k_n. (c) Bootstrap distribution of the mean split-half control \u03c9 (B = 10,000 resamples of the 300 mouse-pilot split-half control \u03c9 values from 50 replicates across six control populations), with the median indicated by the dashed line and the control mean (the empirical calibration baseline 7.70, 95% CI [7.37, 8.02]) by the dotted line. (d) Scatter plot of k_n vs. k_f, showing that functional variation dominates constrained baseline. (e) \u03c9 distribution with \u03c9 = 1 (the theoretical baseline for equivalent populations, marked by dashed line) and the empirical calibration baseline \u03c9 = 7.70 indicated; \u03c9 = 1 is never observed in practice because identity-gene selection inflates k_f relative to k_n (see Results).')

p(f'Figure 2. CKI calibration on Tabula Muris mouse data, metric correlation structure on Tabula Sapiens, and functional-change detection in the ground-truth simulation. (a) k_n calibration across six Tabula Muris cell types from control comparisons (C category: random split of same population). k_n values are stable across cell types, consistent with constrained baseline behavior. (b) Component decomposition of k_n and k_f across four comparison categories: C (random split of the same population), S (same cell type, different organ), D (different cell type, same organ), and X (different cell type, different organ). k_f increases monotonically with biological distance, while k_n remains relatively constrained. (c) \u03c9 distribution by comparison category (log scale) from the mouse pilot calibration dataset. Boxes: median and IQR; whiskers, 1.5\u00d7 IQR. \u03c9 increases monotonically from control splits (C) to cross-organ comparisons (X); X vs. C, one-sided Mann-Whitney test. (d) Spearman correlation heatmap of five metrics on n = {_h["n_pairs_total"]:,} Tabula Sapiens pairs. CKI \u03c9 is negatively correlated with all four standard metrics; because k_n is itself positively correlated with the standard metrics, this negativity partly reflects the \u03c9 denominator (see Results). Standard metrics form a positive cluster. (e) ROC curves for discriminating injected functional signal (\u03b4 \u2265 0.25) from neutral drift in the semi-synthetic ground-truth simulation (marrow B-cell background; 600 functional versus 250 neutral replicates). CKI \u03c9 ranked first of six metrics (AUC = 0.80); independent replication on a skin keratinocyte background gave AUC = 0.91 (rank 1/6).')

p('Figure 3. Real-data neutral-drift calibration on technical replicates. (a) Schematic of the four-tier drift ladder. Library-level pairs within each brain cell class are arranged by drift source: the per-pair n-matched null (pooled nuclei of the two libraries, permuted and re-split at the observed group sizes) embeds same-library sampling noise; T1 pairs two 10x libraries of the same donor, region, and cell type (pure technical drift; ground truth: no functional difference); T2 crosses donors within a region (technical plus inter-individual drift); T3 crosses regions within a donor (regional biology; positive control). (b) Brain calibration distributions (observed / own n-matched null median; log scale) for seven metrics across tiers T1\u2013T3; boxes show median and IQR (whiskers not shown; extreme tails clipped at the 2nd\u201398th percentiles for display). \u03c9 (leftmost metric) stays near 1 at T1 and shows the shallowest gradient to T3, whereas raw JS, cosine, Spearman, and k_f rise several-fold. (c) False-positive rates on T1 (technical drift, dark) and T2 (donor drift, light): fraction of pairs whose observed value exceeds its own null 95th percentile, with Wilson 95% CIs; the dotted line marks the nominal 5% level. \u03c9 misreports least among the continuous divergence metrics at both tiers; marker Jaccard is lower still on the false-positive statistic (T1 19.9%, T2 74.7%) but responds weakest to real regional divergence (T3 calibration 1.41 versus 1.80 for \u03c9 and 2.98 for raw JS; panel b) and offers no k_n/k_f decomposition. (d) Replication in the Kang IFN-\u03b2 PBMC batch-1 technical replicates (30 same-donor, same-condition cross-lane pairs, n-matched null with B = 200 per pair): \u03c9 FPR = 0 of 30 with calibration median 0.96, versus 36.7% for raw JS and 23.3% for cosine. \u03c9 lowers drift misreporting to the minimum among compared metrics while retaining sensitivity to genuine biological divergence\u2014a relative-calibration advantage, not absolute immunity (see Results).')

p('Figure 4. Pan-cancer tissue-level divergence in tumors. (a) Ratio of mean normal\u2013normal (NN) to tumor\u2013tumor (TT) \u03c9 per cancer type (blue; ranked by effect size), with sample-level cluster-bootstrap 95% CIs (B = 1,000); the amber axis shows the corresponding tumor/normal ratio of the housekeeping baseline k_n (TT/NN, means with 95% CIs), which exceeds 1 in all five cancer types while k_f does not\u2014the reversal is denominator-driven. The two axes use independent scales so that both series remain legible. Dotted line, ratio = 1. (b) Per-tumor \u03c9 in LUAD by driver mutation (wild-type n = 311, EGFR-mutant n = 61, KRAS-mutant n = 120; boxes, median and IQR; points, individual tumors). Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; brackets, Dunn post-hoc P-values with Holm correction. (c, d) The same stratification for the components k_f (c) and k_n (d): the KRAS contrast carries a functional component (KRAS > EGFR under k_f alone, P_Holm = 0.015; KRAS versus WT retained after purity and smoking adjustment, adjusted P = 0.009 and 0.029) together with a lower k_n baseline (WT > KRAS, P_Holm = 4.2 \u00d7 10\u207b\u2074), whereas the apparent EGFR elevation dissolved under purity adjustment (all adjusted P > 0.4), consistent with an admixture artefact rather than a baseline shift. All values from the linear-normalization re-computation (Methods).')

p(f'Figure 5. Cross-organ cell-type conservation. (a) CKI \u03c9 ranking of 17 cell types with cross-organ comparisons (n = 59 pairs) within the Tabula Sapiens human atlas, with well-sampled cell types (n \u2265 5 pairs) ranked first and sparsely sampled types (n < 5) listed separately. Among well-sampled types, CD8+ T cells, plasma cells, and neutrophils rank lowest; endothelial cells and erythrocytes rank highest (n = 3 pairs each, suggestive only). (b) \u03c9 distribution across all cell-type pairs, showing conserved vs. variable cell types. (c) Cross-organ \u03c9 gradient (mean \u00b1 SD) showing systematic variation across organ pairs. (d) Top 5 conservative cell-type pairs with the lowest cross-organ \u03c9 values.')

p('Figure 6. Brain regional cell-type differentiation and region-association inference. (a) Brain region map schematic showing anatomical regions analyzed in the Siletti et al. atlas. (b) \u03c9 gradient across 10 non-neuronal cell classes (mean \u03c9 per class, block-shuffle observed landscape). Bergmann glia and vascular cells (mean \u03c9 = 13.56) show the lowest regional divergence; astrocytes (mean \u03c9 = 82.75) show the highest, a 6.10-fold gradient that is an uncorrected upper bound inflated by class-size imbalance (equal-n estimate 1.74-fold, 95% CI [1.64, 1.84]). The gradient is a composite signal dominated by the k_n denominator (3.21-fold k_n versus 2.03-fold k_f contribution at the endpoint contrast; see Results). (c) Region-associated candidate detection: multiplicative residual model identifies 39 Strong candidates (residual < 0.3, \u03c9 < 15, lowest \u03c9 in pair) among 31,764 cross-region comparisons, shown as tier counts as a percentage of all pairs; under a design-matched null the Strong rule expects 148.3 candidates, so the observed 39 are anti-enriched (P(null count \u2265 39) = 1.0) and none survives FDR correction. (d) Observed vs. expected \u03c9 for the five strongest Strong candidates across all cell classes (lowest residuals), showing the gap between observed regional similarity and the cell-type-specific expectation.')

# ============================================================
# Supplementary figure legends (NC: follows the main figure legends)
# ============================================================

p('Supplementary Fig. 1. Parameter sweep and pathway analysis. (a) k_n stability as a function of housekeeping gene set size; k_n decreases monotonically with increasing HK gene number (250\u20131,000), indicating that the baseline rate is gene-set-size-dependent; absolute \u03c9 values are therefore scheme-specific, consistent with the fixed-panel ablation (Results). (b) Variance of module-level GSVA enrichment scores across 38 mouse cell-type entries for the 20 HVG-partition modules (sorted by variance). Cell-type divergence is broadly distributed across modules rather than concentrated in a single module, consistent with the identity-only configuration of k_f. (c) Weight sweep for multi-component k_f. Identity-only (w_identity = 1.0, w_pathway = 0.0) achieves optimal cell-type discrimination (AUC = 0.786, n = 703 mouse cell-type pairs, 6 organs).')

p('Supplementary Fig. 2. Calibrated \u03c9 under two baselines. (a) Raw \u03c9 and calibrated \u03c9 (\u03c9_cal = \u03c9 / 7.70, mouse FACS baseline; \u03c9 / 9.73, brain-internal baseline) by brain cell type (log scale). Dashed line indicates the split-half expectation (\u03c9_cal = 1.0). (b) Calibrated \u03c9 distributions across all 31,764 brain region pairs under both baselines; calibrating with the mouse baseline overstates brain \u03c9_cal by 1.26-fold (9.73 / 7.70).')

p('Supplementary Fig. 3. Real perturbation demonstration (Kang et al. IFN-\u03b2-stimulated PBMCs). (a) Area under the ROC curve (AUC) for separating within-donor stim-versus-control pairs (perturbation) from cross-donor same-condition pairs (donor drift) per cell type, for \u03c9 (blue), k_f alone (green), and raw JS divergence (grey); bars start at the chance level of 0.5. Where IFN-\u03b2 moves the housekeeping anchor hardest (CD14+ monocytes), the \u03c9 AUC falls to 0.55 while k_f retains 0.98 \u2014 the anchor-visibility boundary. (b) Median per-pair k_n (JS divergence on housekeeping genes) by comparison class, donor-drift pairs (steel) versus stim-versus-control pairs (red), on a logarithmic scale; red annotations give the stim-versus-control-to-donor-drift median ratio (1.2\u20135.7-fold), consistent with the perturbation raising the housekeeping anchor itself. Condition is fully confounded with capture lane in this dataset; cross-metric contrasts, not absolute detection, are the informative quantity.')

p('Supplementary Fig. 4. TCGA per-cancer matrices and supplementary stratification vignettes. (a) Pairwise \u03c9 matrices for five cancer types (BRCA, KIRC, LIHC, LUAD, LUSC) showing tissue-level transcriptomic divergence structure within each cancer cohort. (b) Within-cancer-type stratification (exploratory): per-tumor \u03c9 by LIHC Edmondson grade and BRCA PAM50 subtype; both orderings are denominator-dominated and reverse or largely reverse under k_f alone, unlike the LUAD driver-mutation contrast (Results).')

p('Supplementary Fig. 5. Cross-organ conservation raw data. Blue = well-sampled (n \u2265 5 pairs); gray = sparsely sampled (n < 5 pairs). panel a shows mean \u00b1 SD; panel b shows raw pair-level distribution.')

p('Supplementary Fig. 6. Brain regional analysis details. (a) Mean regional divergence (\u03c9, with SD) per cell type, ranked ascending; red bars denote significant deviation from the block-shuffle null (p < 0.05 and |standardised effect size (SES)| \u2265 2; SES = [observed \u03c9 \u2212 null mean] / null SD), grey otherwise. (b) \u03c9 versus number of sampled regions (n_regions) per cell type; Spearman \u03c1 is reported (broader spatial coverage is not significantly associated with divergence at n = 10). (c) Distribution of multiplicative residuals (observed/expected \u03c9) across all 31,764 cross-region pairs; colours indicate confidence tier (Strong: < 0.3; Moderate: < 0.5; Weak).')

p('Supplementary Fig. 7. Pair-specific k_n variability (brain). (a) Distribution of per-pair k_n values by cell type (bars: mean \u00b1 SD); bar colour reflects the cross-pair coefficient of variation (CV) of k_n, from light (low CV, stable k_n) to dark (high CV, variable k_n). (b) Per-pair \u03c9 (pair-specific k_n) versus \u03c9 estimated with the global mean k_n; red line is y = x. Spearman \u03c1 = 0.142 (P = 7.07\u00d710\u207b\u00b9\u2074\u00b3, n = 31,764).')

p('Supplementary Fig. 8. Developmental signature detection. (a) Multiplicative residual distribution for all 31,764 cross-region pairs, with Strong (residual < 0.3), Moderate (residual < 0.5), and Weak (residual < 0.75) tiers shaded. (b) The ten Strong candidates with the smallest residual, shown as horizontal bars (residual and \u03c9 value annotated on each bar); bars are coloured by oligodendrocyte (OL) lineage membership (purple, OL-lineage; red, non-OL). Inset: OL-lineage representation among Strong candidates \u2014 12 of 39 Strong, fold = 0.77, hypergeometric P = 0.92 (no enrichment). Cell types and region pairs are given in full. (c) Confidence-tier composition (Strong/Moderate/Weak) of all cross-region pairs, stacked by cell type and sorted by the number of Strong pairs (ascending). The number and percentage (to two decimal places) of Strong pairs are annotated on each bar \u2014 e.g., Microglia: Strong 16 (0.96%); Oligodendrocyte: Strong 10 (0.95%); Astrocyte: Strong 3 (0.47%).')

p('Supplementary Fig. 9. Block-shuffle permutation null for the residual model. Distribution of multiplicative residuals under block-shuffle permutation of library-to-region assignments (B = 1,000), compared against observed residuals for Strong candidates.')

p('Supplementary Fig. 10. Pseudo-region negative control for the brain block-shuffle null (QQ plots of per-pair permutation P-values against the uniform distribution). (a) Lower-tail P-values; (b) upper-tail P-values. Every region\u2019s libraries were split uniformly at random into two pseudo-regions per cell type and the identical block-shuffle test (B = 1,000) was re-run on the 127,756 pseudo-pairs. Pseudo-pairs between halves of different real regions (cross-origin, n = 127,056) track the diagonal closely (marginal tail rates 5.79% lower / 6.87% upper versus the 5% nominal level), closely matching the real analysis (6.17% / 7.90%), while pairs between the two halves of the same region (same-origin, n = 700) deviate strongly in the lower tail (37.6%), demonstrating both the null\u2019s calibration under the design-matched null and its power to detect within-region library similarity.')

p('Supplementary Fig. 11. Cross-species comparison details. (a) Cross-species \u03c9 comparison: scatter plot of human vs. mouse per-cell-type mean \u03c9 for the 15 shared cell types (Spearman r = \u22120.17, P = 0.55; no significant correlation).')

p('Supplementary Fig. 12. \u03c9 distribution characterization. Histograms and Q-Q plots of \u03c9 distributions for brain, mouse, and human datasets, showing right-skewness; normality is rejected for brain (D\u2019Agostino-Pearson, P < 2.2 \u00d7 10\u207b\u00b9\u2076) and human (Shapiro-Wilk, P = 7.6 \u00d7 10\u207b\u2074\u00b2), while the mouse pilot (n = 15 pairs) does not reject normality (P = 0.071), although the small sample size limits the power of this test.')

p('Supplementary Fig. 13. JS divergence dimensionality invariance. (a) Mean JS divergence between random Dirichlet distribution pairs as a function of dimensionality (50\u20135,000 genes, n = 2,000 trials per dimension), showing that JS divergence is effectively constant across dimensions (ratio = 1.001 between d = 1,130 and d = 2,000). (b) Dimensionality ratio relative to the HK gene set (d = 1,130), confirming that k_n and k_f are dimensionally comparable.')















# == Save ==
# 75 = 73 groups of v49.4 + 2 new in-text citations of ref 47 (CZ CELLxGENE
# Discover; Methods Tabula Sapiens and brain atlas dataset paragraphs, v49.5).
assert _cite_sup_count == 73, f'Expected 73 superscripted citation groups, got {_cite_sup_count}'
print(f'Superscripted citation groups: {_cite_sup_count}')
PROJECT_ROOT = Path(__file__).resolve().parent
write_tables_xlsx()
out = str(PROJECT_ROOT / "results" / "CKI_Manuscript_NC.docx")
doc.save(out)
print(f'Saved: {out}')
