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
_tc49 = _pd.read_csv(Path(__file__).resolve().parent / "results" / "nc52_tcga_pancancer_excc.csv").set_index('cancer')
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
'Batiuk, M. Y. et al. Identification of region-specific astrocyte subtypes at single cell resolution. «i»Nat. Commun.«/i» «b»11,«/b» 1224 (2020).',
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
tr = t.add_run('CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases')
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

p('Inspired by Ka/Ks, CKI (Cell-type Ka/Ks-inspired Index) decomposes transcriptomic divergence into a baseline rate k_n (housekeeping genes) and a functional rate k_f (identity genes); \u03c9 = k_f/k_n quantifies baseline-normalized functional divergence. In ground-truth simulation, \u03c9 rejected neutral housekeeping drift (housekeeping-anchored false-positive rate 0.00 versus 0.55\u20130.58 for raw JS and cosine) and gave the best bounded-power discrimination (AUC = 0.80 [0.770, 0.838]). On real technical replicates (30 cross-lane Kang IFN-\u03b2 pairs), \u03c9 raised no false reports; under stronger brain library-level drift it retained the lowest false-report rate among continuous metrics, though specificity decays with group size. In 3,535 TCGA samples across five cancer types, \u03c9 revealed a consistent pan-cancer reversal\u2014tumors less divergent than adjacent normal tissue (ratio 1.11\u20132.46, four of five CIs excluding 1)\u2014driven by a 1.3\u20133.3-fold elevated housekeeping baseline; GTEx references in lung, liver, and breast are consistent with tumor-specific elevation. In lung adenocarcinoma, KRAS-mutant tumors showed elevated tissue-level divergence whose functional (k_f) and baseline (k_n) components survived purity and smoking adjustment, whereas the apparent EGFR-mutant association reflected stromal/immune admixture. Brain analysis revealed a 3.7-fold regional gradient (k_n-dominated) under span- and size-matched control (donor-level 95% CI [1.9, 3.8]). CKI is available as an open-source Python package.')


# ============================================================
# INTRODUCTION (NC: manuscript must begin with the heading "Introduction")
# ============================================================
heading('Introduction', level=1)

p('Comparing two cell populations is among the most common tasks in single-cell analysis. Researchers typically choose a standard metric: Euclidean distance, cosine similarity, Pearson or Spearman correlation, or Jensen-Shannon divergence. These metrics are convenient, but they treat all gene expression differences equally.')

p('Not all expression changes have the same biological meaning: a twofold change in GAPDH may reflect technical noise, whereas a twofold change in a transcription factor may reflect a functional state shift, and standard metrics cannot tell these apart. The problem is acute in large single-cell atlases [1], where donor- and batch-level variation often dominates over cell-type identity. Methods such as Harmony [2], scVI [3], and SATURN [4] remove such nuisance variation [5], but a key question remains: how much of the difference between two populations reflects functional change rather than neutral drift?')

p('This question mirrors one addressed in molecular evolution. The Ka/Ks ratio (dN/dS) distinguishes nonsynonymous changes (Ka, which alter the protein) from synonymous changes (Ks, largely silent) [6,7], using synonymous sites as an internal baseline so that the ratio reveals selection. While CKI does not share Ka/Ks\u2019s formal mathematical properties (notably the shared mutation rate that cancels in the ratio; see Discussion), it adopts an analogous heuristic logic for transcriptomic comparisons.')

p('CKI defines two rates: a baseline divergence rate k_n, estimated from housekeeping (HK) gene expression, and a functional divergence rate k_f, estimated from cell-type identity genes; the ratio \u03c9 = k_f/k_n quantifies baseline-normalized functional divergence (Fig. 1). The scope of \u03c9 is bounded by one central assumption, quantified empirically throughout: the HK anchor is valid only where housekeeping expression remains constrained. Functional signal on HK genes is invisible to \u03c9 by construction, and in disease or strong-perturbation contexts the anchor itself shifts (TCGA and IFN-\u03b2 below; Supplementary Note 1), so \u03c9 must be read alongside its components (Results; Discussion).')

p('Here, we show that CKI provides a baseline-normalized index of cell-state divergence across five scales. First, random splits of the same mouse cell population (Tabula Muris [8]) yield \u03c9 above 1 (empirical baseline 7.70, two-stage-bootstrap 95% CI [6.38, 9.82]). Second, in Tabula Sapiens human data [9], \u03c9 is negatively correlated with all four standard distance metrics\u2014partly a denominator effect (Results). Third, on real technical replicates (30 cross-lane PBMC pairs; 2,161 brain library pairs), \u03c9 shows the lowest drift misreporting among continuous metrics while retaining sensitivity to genuine biology. Fourth, on TCGA data [10,11] (five cancer types, 3,535 samples after excluding cell-line-derived aliquots), CKI uncovers a consistent pan-cancer reversal\u2014tumors less divergent than adjacent non-tumor tissue, attributable to an elevated housekeeping baseline that GTEx references support as largely tumor-specific\u2014and stratifies lung-adenocarcinoma driver classes with residual confounding (KRAS robust to purity and smoking adjustment under whole-tumor permutation; the apparent EGFR association dissolves). Fifth, in a human brain atlas [12], we quantify a regional differentiation gradient (3.7-fold span- and size-matched, donor-level 95% CI [1.9, 3.8]) and screen for anomalously similar cell-type/region pairs; no candidate survives FDR correction, so the screen is a bounded, hypothesis-generating catalogue.')

# ============================================================
# RESULTS
# ============================================================
heading('Results', level=1)

# --- Result 1 ---
heading('Decomposing transcriptomic variation', level=2)

p('CKI takes two cell populations, each a pseudobulk expression vector (mean expression across cells), and applies the same metric (Jensen\u2013Shannon divergence) in three steps on the same matrix, so the ratio is internally calibrated (Fig. 1).')

p('Step 1: baseline divergence rate k_n: pseudobulk vectors restricted to housekeeping (HK) gene indices, +1 pseudo-count, L1 normalization; k_n is the JS divergence between the two HK-gene probability distributions. Because HK genes should not differ systematically between biologically equivalent populations [13], k_n captures baseline technical and physiological noise.')

p('Step 2: functional divergence rate k_f on cell-type identity genes: top-2,000 highly variable genes (HVGs; Seurat, HK excluded) for the Tabula Muris full pairwise matrix (Supplementary Fig. 1), and the pair\u2019s top-200 differentially expressed genes (absolute mean difference, HK excluded) for all other analyses, with k_n computed per pair on the shared HK set (fixed-panel ablation, Results).')

p(f'Step 3: \u03c9 = k_f/k_n. Statistical inference uses permutation testing (B = 1,000 for all datasets): group labels are permuted (cell labels for mouse and human, sample labels for TCGA) or, for the brain, library-to-region assignments block-shuffled; empirical P-values, standardized effect sizes, and Benjamini-Hochberg FDR are computed within each dataset (Methods).')

p(f'Adding pathway enrichment scores to k_f does not improve discrimination (Tabula Muris; identity-only AUC = {_sb["identity_auc"]:.3f}; Supplementary Table 1).')

# --- Result 2 ---
heading('Calibration confirms baseline behavior', level=2)

p(f'We calibrated CKI on the Tabula Muris FACS dataset [8] (SmartSeq2, {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs), with housekeeping genes from HRT Atlas v1.0 [13] (mouse column): top-{_ds["n_hvg"]:,} HVGs for the full pairwise matrix (703 pairs, Supplementary Fig. 1), and the hybrid per-pair scheme for the pilot (Fig. 2).')

p(f'Control comparisons randomly split the same population into halves across six FACS control populations (Fig. 2a): 50 split-half replicates per population (300 \u03c9 values) stabilized the baseline at mean \u03c9 = 7.70 (two-stage bootstrap over the six populations, 95% CI [6.38, 9.82]; the 300-replicate interval [7.37, 8.02] is pseudo-replicated and superseded; leave-one-population-out range 6.75\u20138.08; Section 3.10 of the Supplementary Information). No control comparison reached significance (all P > 0.05): biologically equivalent populations are recognized as undiverged.')

p(f'Beyond controls, \u03c9 increased monotonically with biological distance (Fig. 2b, c): same cell type across organs (mean \u03c9 = {_mc["S_mean"]:.2f}, n = {_mc["S_n"]}) sat below different cell types within an organ (mean \u03c9 = {_mc["D_mean"]:.2f}, n = {_mc["D_n"]}), with cross-organ cross-type comparisons highest (2\u20134 pairs per category). k_f drives this: from controls to inter-cell-type comparisons, k_f rose ~400-fold ({_mc["kf_mean_ctrl"]:.4f} \u2192 {_mc["kf_mean_D"]:.2f}\u2013{_mc["kf_mean_X"]:.2f}) while k_n rose only {_mc["kn_fold_D"]:.0f}\u2013{_mc["kn_fold_X"]:.0f}-fold\u2014CKI measures functional divergence, not total difference.')

p(f'Because the empirical baseline deviates from the theoretical ideal (\u03c9 = 1), we introduce \u03c9_cal = \u03c9_obs / 7.70 (one-significant-digit resolution). The factor is dataset-relative (brain atlas 9.73; Tabula Sapiens 7.67, indicative only); class-specific baselines leave the astrocyte-to-Bergmann-glia gradient essentially unchanged, and a ratio-estimator audit confirms the calibration absorbs ratio bias (Supplementary Notes 2\u20134).')

# --- Result 3 ---
heading('Correlation structure between CKI and standard metrics', level=2)

p(f'We extended CKI to the Tabula Sapiens human atlas [9] ({_ds["tabula_sapiens_cells"]:,} cells; {_h["n_ct_analyzed"]} filtered cell-type entries, {_h["n_pairs_total"]:,} pairs across six organs (largest-donor pseudobulks; Methods), using the same hybrid scheme with HRT Atlas v1.0 HK genes [13] (human column) (Fig. 2d). Human \u03c9 ranged from {_h["omega_min"]:.2f} to {_h["omega_max"]:.2f}; cross-dataset comparisons are rank-based only (Discussion). The biological hierarchy was preserved: same cell type across organs (mean \u03c9 = {_h["diff_organ_same_ct_mean"]:.2f}, n = {_h["diff_organ_same_ct_n"]}) sat below different cell types within an organ (mean \u03c9 = {_h["same_organ_diff_ct_mean"]:.2f}, n = {_h["same_organ_diff_ct_n"]:,}).')



_decomp_kf_lo = _decomp['corr_kf_M'].min(); _decomp_kf_hi = _decomp['corr_kf_M'].max()
_decomp_kn_lo = _decomp['corr_kn_M'].min(); _decomp_kn_hi = _decomp['corr_kn_M'].max()
_decomp_pc_lo = _decomp['partial_corr_omega_M_given_kn'].min()
_decomp_pc_hi = _decomp['partial_corr_omega_M_given_kn'].max()
p(f'On all {_h["n_pairs_total"]:,} human pairs, \u03c9 correlated negatively with all four standard metrics (raw JS, Spearman, cosine, marker Jaccard; Spearman r = {f'{_sc["max"]:.2f}'.replace('-', '\u2212')} to {f'{_sc["min"]:.2f}'.replace('-', '\u2212')}; entry-clustered bootstrap 95% CIs excluding 0; Supplementary Methods 5.5), the four forming a tight positive cluster (pairwise r = {_sc["std_pairwise_min"]:.2f}\u2013{_sc["std_pairwise_max"]:.2f}). The negative sign is partly a ratio artifact: k_f correlated positively with the standard metrics (r = +{_decomp_kf_lo:.2f} to +{_decomp_kf_hi:.2f}) and k_n more strongly (r = +{_decomp_kn_lo:.2f} to +{_decomp_kn_hi:.2f}), and conditional on k_n all four turned positive (partial r = +{_decomp_pc_lo:.2f} to +{_decomp_pc_hi:.2f}, entry-clustered CIs excluding 0).')

p('CKI was the only metric scoring same-organ different-cell-type pairs above different-organ different-cell-type pairs (Mann-Whitney P = 5.6 \u00d7 10\u207b\u00b9\u2078, descriptive\u2014pairs share cell-type pseudobulks); all four standard metrics showed the opposite pattern. Decomposition tempers the functional reading: same-organ pairs have indistinguishable k_f (P = 0.60) but lower k_n (P = 3.0 \u00d7 10\u207b\u00b9\u2076)\u2014a more stable within-organ housekeeping baseline, not greater functional specialization (also descriptive; Supplementary Note 9).')

# --- Result 3b: ground-truth simulation ---
heading('Ground-truth simulation: specificity versus sensitivity', level=2)

p('No real dataset provides pairs with known functional divergence, so we injected perturbations into a real background (Tabula Muris FACS marrow B cells; pre-injection divergence zero; Methods). Under pure neutral housekeeping drift, raw JS and cosine exceeded their null thresholds in 55% and 58% of replicates, \u03c9 in none (Clopper-Pearson intervals in Supplementary Note 1); an injected functional module was detected only when strong (0 of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2). \u03c9 is structurally blind to modules on HK genes (k_n fired at 0.61\u20131.00), yet under expression-matched low-variance non-HK drift \u03c9 stayed calibrated (0.000\u20130.067) while raw JS and cosine inflated to 0.81\u20131.00 (Supplementary Notes 1, 5).')

p('\u03c9 best discriminated functional (\u03b4 \u2265 0.25) from neutral perturbations (Fig. 2e; AUC = 0.80 versus 0.72 k_f, 0.64 raw JS, 0.58 cosine, 0.21 k_n; DeLong 95% CI [0.770, 0.838]): the standard metrics\u2019 apparent power is purchased with false positives on neutral drift. Rank discrimination and thresholded power diverge (marrow: AUC 0.85 at \u03b4 = 1 despite 0/150 detections at the null-95 threshold; Supplementary Note 1). The ratio also conferred robustness to technical asymmetry (Discussion)\u2014a specificity-first screen rejecting neutral drift at the cost of bounded power for weak-to-moderate signals (Supplementary Note 1).')

p('The design reproduced in a second background (skin keratinocyte stem cells; AUC(\u03c9) = 0.908 versus AUC(k_f) = 0.859; Fig. 2e; Supplementary Note 1).')

# --- Result 3b-nc49: real-data neutral-drift calibration on technical replicates ---
heading('Real-data neutral-drift calibration on technical replicates', level=2)
p('On real technical replicates (per-pair size-matched cell-shuffle nulls, B = 200; Methods), the 30 same-donor, same-condition cross-lane pairs of the IFN-\u03b2 PBMC dataset [14] are clean: \u03c9 was fully calibrated (0 of 30 above its null 95th percentile; k_f likewise), whereas raw JS misreported 36.7% and cosine 23.3% (Fig. 3d).')
p('The design scales to the brain atlas (606 10x libraries) as a four-tier drift ladder of library-level pairs [12]: T1, same donor, region, and cell type (2,161 pairs); T2, different donors within a region (1,089); T3, different regions within a donor (1,656). On T1, \u03c9 misreported least among the continuous divergence metrics (FPR 28.6% versus 37.6\u201345.2% for the others; Fig. 3b, c), and its calibration gradient is the shallowest across the ladder (T3 ratio 1.80 versus 2.98 raw JS).')
p('Two qualifications temper this: the absolute \u03c9 FPR grows with group size (14.1% below 30 nuclei to 48.0% above 500; small-stratum raw JS 28.6% to 72.5%)\u2014a library-level component the anchor absorbs only partially\u2014and a minority of classes show gene-specific library effects (Section 3.12 of the Supplementary Information). Neutral-drift immunity thus transfers as a relative-calibration advantage.')

p('A sanity check on unused data is consistent with this: on the CELLxGENE Microglia supercluster [12] (91,838 nuclei), sample-matched microglia-versus-CNS-macrophage pairs (n = 35) separate cleanly from neutral half-splits (n = 40; \u03c9 21.83 \u00b1 7.20 versus 1.30 \u00b1 0.36; Mann-Whitney P = 5.5 \u00d7 10\u207b\u00b9\u2074, descriptive\u2014pairs overlap across four donors; AUC = 1.00), the margin carried by k_f (Supplementary Note 16; Supplementary Fig. 14).')

# --- Result 3b: real perturbation demonstration (IFN-beta PBMC) ---
heading('Real perturbation demonstration: IFN-\u03b2-stimulated PBMCs', level=2)
p('On a real perturbation\u2014PBMCs from eight donors, control versus 6-hour IFN-\u03b2 stimulation [14] (24,413 cells, six cell types; Methods), condition fully confounded with lane\u2014we read this as a relative architecture demonstration. The perturbation was visible at the \u03c9 level in all six cell types, but k_f alone separated perturbation from donor drift as well or better (rank AUC: \u03c9 0.55\u20130.92, k_f 0.74\u20131.00); in CD14+ monocytes \u03c9 fell to 0.55 while k_f retained 0.98, because stimulation raises housekeeping expression itself (median k_n 1.2\u20135.7-fold) and the inflating denominator partially cancels the functional signal (Supplementary Fig. 3; Supplementary Note 6).')

# --- Result 3d: benchmarking against perturbation-response metrics ---
heading('Benchmarking against perturbation-response metrics', level=2)
p('We benchmarked CKI against MELD (v1.0.2) and scDist (Python approximation) on the Kang IFN-\u03b2 dataset [14]. CKI and MELD agreed on effect direction in 6 of 6 cell types, but MELD\u2019s within-type separation was near-saturated (AUC 0.997\u20130.9998). In an additive mean-shift simulation, MELD and the scDist approximation detected every configuration (sensitivity 1.00), whereas CKI \u03c9 rose from AUC 0.52 to 0.79 as the shift grew on 100 genes but collapsed to 0.05\u20130.13 on 500 genes, where the anchor responds (k_n AUC = 1.000) and annihilates the ratio; for maximal detection power on broad perturbations use MELD, scDist, or CKI\u2019s own k_f.')

# --- Result 3c: fixed gene-panel ablation ---
heading('Fixed-panel ablation: robust rankings, scheme-specific \u03c9', level=2)
p('Non-circular panels left rankings essentially untouched (pair-level \u03c1 = 0.937 leave-pair-out, 0.918\u20130.931 other panels; class means \u03c1 = 0.90\u20130.99), and the astrocyte-to-Bergmann-glia gradient was preserved and amplified (6.10-fold reported; 6.53-fold leave-pair-out), with class-level significance largely robust under scheme-matched block-shuffle nulls (Supplementary Note 7). Circular selection inflated k_f by a median 1.61-fold versus leave-pair-out (grand mean \u03c9 38.55 reported; 26.5 leave-pair-out; 6.5 fixed), so absolute \u03c9 values are upper-bound, scheme-specific estimates: rank-based conclusions are robust, but the tier cutoffs (\u03c9 < 15/25/35) do not transfer.')



# --- Result 4 ---
heading('A pan-cancer map of tissue-level divergence in tumors', level=2)

p(f'We applied CKI to TCGA bulk RNA-seq across five cancer types (LUAD, LUSC, LIHC, KIRC, BRCA) [10,11], totalling {_tc["n_total"]:,} samples, comparing tumor\u2013tumor (TT), normal\u2013normal (NN), and tumor\u2013normal pairs within each type (Fig. 4; Supplementary Fig. 4). A pan-cancer reversal emerged: NN pairs were more divergent than TT pairs in all five (mean NN/TT \u03c9: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11; cluster-bootstrap CI excluding 1 in four of five, LIHC excepted). All TCGA results exclude 32 cell-line-derived aliquots found by barcode audit (Section 1.7 of the Supplementary Information). Decomposition identified the mechanism: TT k_n exceeded NN k_n by 1.3\u20133.3-fold in every cancer type while TT k_f was equal to or higher\u2014the reversal reflects a more stable housekeeping baseline among adjacent non-tumor specimens, not smaller functional-gene divergence of tumor cells (Fig. 4a).')

p('Stratifying LUAD tumors by driver mutation (61 EGFR-mutant, 120 KRAS-mutant, 311 wild-type; Fig. 4b), KRAS-mutant tumors showed the highest tissue-level divergence (mean \u03c9 = 136.9 versus 115.4 wild-type and 122.2 EGFR-mutant; Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; Dunn\u2013Holm P \u2264 0.008 for both KRAS contrasts, P = 0.39 for EGFR\u2013wild-type; label-permutation confirmed; Section 3.13). The KRAS elevation was carried predominantly by a lower housekeeping baseline (~84% of the log-\u03c9 gap) with an accompanying functional component (KRAS versus EGFR under k_f alone, P = 0.015). Adjusting for ESTIMATE stromal/immune admixture left the KRAS\u2013wild-type difference significant (adjusted log-\u03c9 ratio 1.19, 95% CI [1.12, 1.26]) but abolished the apparent EGFR elevation (all adjusted P > 0.4); adjusting for smoking, alone or jointly with admixture, or with age and sex, left the contrast essentially unchanged (whole-tumor permutation of the adjusted models, B = 10,000: KRAS P \u2264 0.001, all EGFR contrasts P \u2265 0.28; Section 3.13 of the Supplementary Information). TP53 co-mutation and histological subtype were not adjusted for, so residual confounding remains; stratifications beyond LUAD are denominator-dominated vignettes (Supplementary Note 9).')

p('Four controls bound the interpretation (Supplementary Note 8). Composition adjustment left the pooled tumor-pair k_n coefficient unchanged (\u22120.9% pooled, 95% CI \u22124.3% to +2.5%), and high-purity-half comparisons increased the NN/TT ratio in all five, so admixture can only weaken, not create, the elevation. All TCGA statistics were recomputed under the authoritative linear probability mapping; only LIHC is mapping-sensitive (linear 1.11 [0.94, 1.30] versus softmax 1.29 [1.09, 1.53], the latter excluding 1 in all five; Supplementary Table 5), and the housekeeping floor (k_n \u2265 10\u207b\u2074) is essentially never reached, leaving ratios identical across floors 0\u201310\u207b\u2074 (Supplementary Note 8). LUAD KRAS identity panels showed no MSigDB Hallmark enrichment [15] after correction (all q \u2265 0.24), and composition-adjusted regressions retained TT \u2265 NN k_f ordering in all five. TCGA \u201cnormal\u201d samples are adjacent non-tumor, and per-tumor \u03c9 was not associated with survival (ex-CC LIHC Cox, stage categorical: \u03c9 HR per SD 1.08 [0.88, 1.33], P = 0.467; k_f likewise null; Supplementary Table 14): we report all TCGA findings as tissue-level divergence at bulk resolution, pending single-cell validation (reference-free composition check: non-parenchymal fraction versus k_n, ρ = 0.20–0.26; Supplementary Note 8).')
p('A GTEx healthy reference supplies the missing external comparison (Supplementary Note 8): in lung, liver, and breast, adjacent-normal k_n is as low as healthy k_n (healthy/adjacent \u2248 1.0\u20131.2) while tumor k_n is 2.0\u20132.8-fold higher\u2014adjacent non-tumor resembles healthy tissue, consistent with tumor-specific elevation rather than a field effect within cohorts. Kidney is the exception (GTEx cortex k_n \u2248 tumor; n = 28, high variance).')

# --- Result 5 ---
heading('CKI ranks cell types by cross-organ conservation', level=2)

p(f'Of the {_h["n_pairs_total"]:,} Tabula Sapiens pairs, {DATA["cross_organ_n_total"]} are same-cell-type cross-organ comparisons (Fig. 5; Table 1; Supplementary Fig. 5). Among well-sampled types (n \u2265 5 pairs; Table 1), {t2[0][0]}s (mean \u03c9 = {t2[0][1]} \u00b1 {t2[0][2]}, n = {t2[0][3]}) and {t2[1][0]}s (mean \u03c9 = {t2[1][1]} \u00b1 {t2[1][2]}, n = {t2[1][3]}) were the most conserved, followed by {t2[2][0]}s and {t2_next[0]}s, with {mac[0]}s (n = {mac[3]}) intermediate; {last2[0][0]}s and {last2[1][0]}s were the most divergent, consistent with organ-specific endothelial programs [16] (both n = 3); sparsely sampled types carry no reliable signal.')

p(f'The cross-organ ranking agreed little with standard-metric rankings (Spearman r = {f'{min(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')} to {f'{max(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')}, n = {DATA["cross_organ_n_total"]} pairs; Supplementary Table 2), because CKI explicitly normalizes. A k_f-only control qualifies this (Supplementary Note 9): per-cell-type mean \u03c9 and mean k_f are only weakly concordant (r = 0.23, 95% CI [\u22120.08, 0.38], n = 17), the extremes reproduce but the middle does not. The ranking is thus a composite of functional divergence and baseline differences, and because the k_n anchor is not calibrated across cell types, cross-type gaps should be read descriptively (Discussion).')

# --- Result 6 ---
heading('Brain regional analysis reveals divergence gradients', level=2)

p('We applied CKI to the Siletti et al. human brain atlas [12] (~3.3 million nuclei, 108 regions), focusing on 888,263 non-neuronal nuclei in 10 major classes (supercluster_term does not resolve neuronal subtypes). \u03c9 was computed for all same-cell-type cross-region pairs (31,764; Fig. 6; Supplementary Fig. 6; Supplementary Table 3); vascular cells and fibroblasts are heterogeneous superclusters, so their class-level \u03c9 values are supercluster averages.')

p('Class-mean \u03c9 spanned a regional gradient from Bergmann glia and vascular cells (both 13.56) to astrocytes (82.75 \u00b1 44.98, n = 5,778 pairs)\u2014a full-data endpoint gradient of 6.10-fold, an uncorrected upper bound. Two controls converge on a robust intermediate value: a span-matched control (21 intra-cerebellar pairs) yields 3.68 (donor-level bootstrap [1.67, 3.97]) and a combined span- and size-matched control yields 3.66 (donor-level bootstrap [1.92, 3.78]; leave-one-donor-out always > 1). The size-only equal-n control (1.74) is not donor-robust (95% CI [0.80, 2.34]; four donors) and is relegated to a sensitivity analysis (Supplementary Note 10). RNA-quality proxies do not drive the gradient: (class, region)-level adjustment for detection depth, UMI counts, and mitochondrial fraction leaves it at 6.33\u20136.45.')

p('A cell-type-level block-shuffle null permuting library-to-region assignments (B = 1,000; Methods) tested whether the gradient exceeds chance: regional structure significantly raised mean \u03c9 for 4 of 10 classes (astrocytes at the permutation floor; OPCs, committed OPCs, fibroblasts P \u2264 0.030), 3 of 10 surviving Benjamini-Hochberg correction; a donor-stratified null leaves the same 3 of 10 (ependymal cells, moving against the conservative direction, still do not survive: stratified q = 0.052). Microglia, oligodendrocytes, and Bergmann glia sit at or below the null expectation.')

p('Three analyses probe robustness. First, same-donor region pairs preserve the extremes and a 4.50-fold gradient (Supplementary Note 12). Second, the astrocyte-versus-Bergmann-glia contrast is predominantly a k_n effect (k_f differs 2.0-fold; mean k_n 3.2-fold): class-mean \u03c9 tracks k_n (\u03c1 = \u22120.73) but not k_f (\u03c1 = 0.09), and under a k_f-only ordering astrocytes rank third of ten.')

p('Third, class-mean k_n correlates negatively with class size (Spearman \u03c1 = \u22120.648, P = 0.043) while class-mean \u03c9 does not (P \u2265 0.091), and the equal-n decomposition shows the full-data Bergmann-glia k_n elevation is largely a class-size artefact (Supplementary Note 10).')

p('The ordering is compatible with known cell biology\u2014tissue-resident vascular cells and fibroblasts lowest [17,18], regionally specialized astrocytes highest [19]\u2014but it is k_n-dominated and does not by itself establish functional specialization.')

p('A residence/migration framework finds no support: OPCs\u2014the most actively migrating non-neuronal population\u2014show the second-highest mean \u03c9 (40.62), and the screen shows no oligodendrocyte-lineage concentration (fold 0.77, P = 0.92).')

heading('Anomalously similar pairs: a hypothesis-generating screen', level=2)

p('Low \u03c9 for a cell type across two regions indicates similarity beyond baseline expectation, with non-exclusive candidate mechanisms (developmental origin heterogeneity, colonization-route boundaries [20-22], postnatal migration [23,24]). Under a design-matched null recomputing the full selection rule on every block-shuffle permutation, the expected Strong-candidate count is 148.3 across the 31,764-pair pool\u2014the 39 observed lie 3.8-fold below expectation (P(null count \u2265 39) = 1.0), and no candidate survives global FDR correction (minimum q = 0.520). The catalogue is thus a prioritized hypothesis list, inheriting the four-donor structure (Supplementary Note 11).')

p('The screen uses a multiplicative model, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, with three residual tiers: Strong (< 0.3, \u03c9 < 15, lowest \u03c9 in the pair), Moderate (< 0.5, \u03c9 < 25), Weak (< 0.75, \u03c9 < 35; Methods; Supplementary Fig. 8).')

p(f'Criteria identified {_br["n_strong"]} ({_br["pct_strong"]:.2f}%) Strong, {_br["n_moderate"]:,} ({_br["pct_moderate"]:.2f}%) Moderate, and {_br["n_weak"]:,} ({_br["pct_weak"]:.2f}%) Weak candidates among {_br["total_pairs"]:,} comparisons (Supplementary Table 4). Under the block-shuffle null (B = 1,000; Supplementary Fig. 9), 31 Strong candidates showed raw P < 0.05; the only sub-nominal stratified family is intra-cerebellar Bergmann-glia (m = 21; within-family minimum q = 0.042). The microglial concentration (16 Strong) does not survive the design-matched null (fold 0.31, P = 0.990): we make no class-composition claim.')

p('A pseudo-region negative control (127,756 pseudo-pairs) confirms the null is calibrated by library-level, not regional, structure (near-nominal cross-region tail rates; Supplementary Note 12; Supplementary Fig. 10).')

p('The catalogue shows spatial patterning without establishing anatomical themes. Microglial candidates (16 of 39) concentrate on visual-relay and orbitofrontal dissections (Supplementary Note 11), and mature-oligodendrocyte candidates (10, all raw P < 0.05) show a thalamo-temporal orientation crossing rather than following the dorsoventral origin boundary [25] (Supplementary Note 13); sparse candidates came from astrocytes, fibroblasts, and ependymal cells [26,27], none from Bergmann glia, vascular cells, or choroid plexus [26,28]. But the set is estimator-sensitive\u2014only 3 of 39 Strong candidates survive a switch to a global-k_n estimator\u2014so all entries are strictly hypothesis-generating.')







# ============================================================
# DISCUSSION
# ============================================================
heading('Discussion', level=1)

p('CKI reframes transcriptomic comparison\u2014from measuring absolute distance to quantifying functional divergence relative to an internal baseline\u2014but is better described as a recombination of established ideas than a conceptual shift: reference genes have long anchored normalization and quality control [29], the constrained-variance property of housekeeping genes is characterized genomically [13,30], and gene-specific noise floors are central to the transcriptional-noise literature [31-33]. CKI combines these ingredients into a per-comparison, design-testable index with explicit split-half calibration and a design-matched permutation null. The key assumption\u2014HK genes under stabilizing selection\u2014lacks the mathematical cancellation Ka/Ks enjoys, so CKI is a heuristic index, not a formal measure of selection. The empirical calibration indicates k_f systematically exceeds k_n even for identical populations (Results), so \u03c9_cal = \u03c9 / 7.70 is an indicative, dataset-relative scale (Results; Supplementary Note 3).')
p('What \u03c9 adds beyond k_f is calibration, not detection power: under fourfold cell-count imbalance (simulation) k_f misreports 38% of neutral pairs, \u03c9 none; on Kang CD14+ monocytes k_f follows neutral housekeeping drift (AUC 0.98) while \u03c9 stays conservative (0.55). Nor is the relationship mathematically forced: permuting k_n across the 5,151 full-inventory human pairs predicts Spearman 0.524 between \u03c9 and k_f, yet the observed value is 0.089\u2014the structured baseline decorrelates them (Supplementary Note 9).')

p('CKI is a divergence index, not a classifier\u2014by design. Classifying cell types is largely solved; CKI answers a complementary question: regardless of labels, how much functional divergence separates two populations relative to their shared baseline? The negative correlation with standard metrics is partly a denominator effect (decomposition, Results), so \u03c9 is a composite of numerator and denominator information rather than an independent dimension. The ratio earns its increment over k_f under controlled ground truth and in drift rejection; on real-data orderings the increment is not established, and k_f with a design-matched null remains the default for ordering claims.')

p('The Ka/Ks analogy is heuristically productive but technically bounded: HK genes are empirically defined, not mechanistically neutral, and are themselves the most constrained expression class, so \u03c9 reads as functional divergence in excess of a constrained baseline, never as evidence of positive selection. The full correspondence\u2014including its McDonald\u2013Kreitman-style fourth term [34]\u2014and caveats are in Section 1.4 of the Supplementary Information.')

p('CKI complements rather than replaces existing methods: SAMap [35] and SATURN [4] address cross-species alignment and CACIMAR [36] conservation scoring\u2014different questions from within-species functional divergence, so we did not benchmark quantitatively. More broadly, CKI provides a principled null model for any transcriptomic comparison: before concluding two populations differ meaningfully, ask whether the difference exceeds baseline expectation.')

p('CKI is also not redundant with Augur [37] (condition-predictability prioritization): rankings are moderately concordant (\u03c1 = 0.442 versus class-mean \u03c9; 0.564 versus k_f) with overlapping extremes, descriptive only at n = 10 classes (Supplementary Note 14).')

p('The pan-cancer reversal\u2014tumor specimens less divergent than adjacent non-tumor tissue (mean NN/TT 1.11\u20132.46, cluster-bootstrap CIs excluding 1 in four of five cancers)\u2014is a robust tissue-level observation: at bulk resolution the apparent convergence could reflect cell-composition shifts, peritumoral inflammation, or RNA-quality differences, and the reversal is predominantly a k_n effect, so the data do not indicate smaller functional divergence of tumor cells. A marker-panel composition check (Supplementary Note 8) shifts the pooled k_n coefficient by only \u22120.9%, but this masks heterogeneity: the shift is largest in LIHC (+44%, the weakest reversal) and KIRC (+20%), so marker-measurable composition likely contributes in those types. A GTEx healthy reference (Results) shows adjacent-normal k_n at healthy-tissue levels in lung, liver, and breast, consistent with tumor-specific housekeeping elevation over a field effect within cohorts; kidney is an exception (noisy healthy reference). The hepatocellular literature motivating this reading [38] concerns the weakest-reversal cancer type, where the mechanism is least certain.')

p('The cross-organ and cross-brain-region analyses show CKI measuring functional differentiation at multiple spatial scales, though the brain regional gradient is dominated by the k_n denominator, not a pure functional-divergence ranking. The candidate screen illustrates a second principle: 31 of 39 Strong candidates showed raw P < 0.05 but none survived correction (minimum q = 0.520), and only 3 of 39 are retained under a global-k_n estimator (Supplementary Note 13)\u2014statistical claims at atlas scale require nulls respecting the experimental design; the absence of FDR-significant signals is itself informative. Cross-species transfer remains unestablished (per-cell-type mean \u03c9 rankings uncorrelated, r = \u22120.17, P = 0.55; Supplementary Fig. 11) [39].')

p('Several signals are consistent with prior reports\u2014literature anchoring, not independent validation. Maturation comparisons must use the k_f-only ordering, because the composite is k_n-dominated: under k_f alone committed OPCs rank highest (0.197) and OPCs lowest (0.048), partially consistent with reports that early oligodendrocyte stages are regionally uniform whereas mature subsets become region-enriched [40,41]; neither ordering supports a monotone-maturation reading. The thalamo-temporal orientation of the mature-oligodendrocyte candidates corresponds to the developmental organization of forebrain oligodendrocytes [25] only at axis anatomy, pending lineage-tracing or spatial-transcriptomic follow-up.')

p('CKI and standard metrics answer different questions, and choosing between them reduces to a few practical rules. Use CKI when the question is relative\u2014is the functional divergence between two populations larger than what their own housekeeping baseline varies by, within the same dataset and gene-selection scheme?\u2014offering a normalized scale and a specificity-first screen: a significant \u03c9 rejects label exchangeability under a design-matched null, and functional signal on the anchor is invisible to \u03c9, as the IFN-\u03b2 demonstration makes explicit (ref. [14]; Results). Before trusting fine-grained \u03c9 orderings, diagnose the denominator: if k_n lies in the extreme tail of its own null or correlates with technical covariates, report k_f with the design-matched null directly (\u03c9 orderings here were predominantly denominator-driven; Supplementary Note 9). Use standard metrics when absolute cross-dataset distances are required, for classification, for weak-to-moderate effects at atlas scale, or when the baseline itself is suspect\u2014then interpret k_n and k_f separately rather than trusting \u03c9 alone.')

p('For prospective applications we recommend: (i) at least ~100 cells per group (operating window ~50\u2013200; power already erodes inside this window; Section 3.11 of the Supplementary Information), below which pseudobulk noise inflates k_n and k_f unpredictably; (ii) the pre-specified HRT Atlas v1.0 housekeeping panel (cki/data/hrt_atlas.csv) rather than data-driven auto-detection; (iii) comparisons only within the same dataset and gene-selection scheme, interpreting \u03c9 against a split-half internal baseline rather than the mouse-derived 7.70\u2014absolute \u03c9 does not transfer; (iv) a permutation null matching the experimental design (block-shuffle where libraries or donors define blocks; cki.blocknull.block_shuffle_test).')


p('Limitations. Several boundaries delimit where \u03c9 can fire and how it should be read. (i) Scope: CKI detects state changes within a given cell type, not cell-type identity, and operates at the pseudobulk level; because the housekeeping anchor is cell-type-specific, k_n is directly comparable only within the same cell type, so limited cross-type discrimination is expected by design. (ii) Gene-set definition and calibration: the per-pair k_f scheme selects genes by the observed difference itself, so k_f magnitudes are inflated upper bounds (median 1.61-fold) and absolute tier thresholds are scheme-specific; housekeeping expression may be dysregulated in cancer [38]; and the empirical calibration factor (7.70, two-stage 95% CI [6.38, 9.82]) derives from mouse split-half controls, so absolute \u03c9 does not transfer across datasets or gene-selection schemes. (iii) Data and design: the TCGA analysis is limited to bulk resolution, its per-cancer permutation test holds the identity panel fixed (anti-conservative, retained only for completeness), and five cancer types make the results exploratory; the brain atlas uses post-mortem tissue\u2014detection-depth, UMI, and mitochondrial-fraction proxies do not drive the regional gradient (Results), but these proxies cannot capture PMI-related RNA-degradation deformation, which remains unexcluded. (iv) Anchor visibility: \u03c9 is structurally insensitive to perturbations that move the housekeeping anchor itself\u2014in simulation, once 500 genes shifted, the ratio collapsed (AUC 0.05\u20130.13)\u2014and permutation power vanishes beyond ~500 cells per group, bounding the operating window at ~50\u2013200 cells; the scDist results used a Python approximation of the R package and should be re-verified against the original. (v) Multiple testing and cluster-aware inference: the class-level upper-tail tests and the pair-level lower-tail screen are reported without joint cross-family correction; the block-shuffle null assumes libraries are otherwise exchangeable (bounded by the pseudo-region negative control; Supplementary Note 12); the candidate catalogue is estimator-sensitive (3 of 39 Strong retained under a global-k_n switch); and B = 1,000 bounds the resolvable P-value at 9.99 \u00d7 10\u207b\u2074, so the per-pair FDR outcome (minimum q = 0.520) reflects permutation resolution, not evidence against any candidate. Full treatments and supporting sensitivity analyses are given in Supplementary Notes 1\u201316.')











# ============================================================
# Conclusions paragraph retained, merged into the end of Discussion (NC: no separate Conclusions section)
# ============================================================
p('CKI adapts the baseline-normalization logic of Ka/Ks to single-cell transcriptomics, decomposing population divergence into a housekeeping baseline rate (k_n) and an identity-gene functional rate (k_f). Across simulation, calibration, cross-organ, pan-cancer, and brain-regional analyses, \u03c9 rankings carried reproducible biological signal while absolute \u03c9 values remain scheme- and dataset-specific; statistical claims at atlas scale require nulls respecting the experimental design; and the absence of FDR-significant candidates is itself an informative bound on what adult transcriptomes alone can support. Released as an open-source Python package with a fully reproducible pipeline, CKI offers an interpretable complement to standard distance metrics, with applications across developmental biology, drug response, aging, and evolutionary cell biology.')

# ============================================================
# METHODS
# ============================================================
heading('Methods', level=1)

heading('CKI computation', level=2)
p(f'We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation [42]. Pseudobulk vectors average expression across cells sharing the same cell-type annotation (\u2265 20 cells per entry, \u2265 1 donor/mouse contributing \u2265 10 cells). Housekeeping (HK) genes are loaded from HRT Atlas v1.0 [13] ({_ds["hrt_atlas_n_hk"]:,} human-mouse conserved genes; species-appropriate column per dataset); all reported analyses use this pre-specified reference rather than data-driven auto-detection (Supplementary Methods 5.1).')

p('For populations A and B with pseudobulk vectors \u03b5_A and \u03b5_B, each vector is normalized to a probability distribution before Jensen\u2013Shannon (JS) divergence computation by a softmax over log-transformed values, which in count space is exactly a +1 pseudo-count followed by L1 normalization: p_i = (c_i + 1)/\u03a3_j(c_j + 1). Aggregation order differs across pipelines (brain: softmax(log1p(mean counts)); mouse and human pilots: softmax(mean(log1p))), and calibration constants are pipeline-internal and must not be transferred across pipelines (same-data sensitivity analysis in Supplementary Methods 5.1). Then k_n = JS(norm(\u03b5_A[H]), norm(\u03b5_B[H])) over HK gene indices H; k_f = JS(norm(\u03b5_A[I]), norm(\u03b5_B[I])) over the identity-gene set I (top-2,000 HVGs, Seurat flavor, HK excluded, for the full matrix; per-pair top-200 otherwise); \u03c9 = k_f/k_n, with JS divergence [43] using base-2 logarithm (range [0, 1]). An optional denominator floor guards against near-zero k_n; all single-cell analyses apply only the positivity guard (kn_floor = 0; no reported single-cell \u03c9 was capped), while the TCGA bulk analysis applies kn_floor = 1 \u00d7 10\u207b\u2074. Because the softmax mapping applied to log2(TPM + 1) implies an undisclosed power transformation, every TCGA analysis was recomputed with the linear normalization p_i = (TPM + 1)/\u03a3_j(TPM_j + 1), with all qualitative conclusions unchanged (Supplementary Methods 5.1).')

p('Package parity: all hybrid-scheme analyses reported here select each pair\u2019s k_f genes as the top-200 by absolute pseudobulk difference (func_method = "pairwise_absdiff" in package v0.5.2); the package\u2019s default permutation test re-selects the k_f set at every permutation under the same per-pair rule (reselect_identity = True), the legacy fixed-set null being anti-conservative (Supplementary Methods 5.1).')

heading('Dimensionality invariance of JS divergence', level=2)
p(f'Because k_n is computed on ~1,130 HK genes and k_f on 200\u20132,000 genes, we verified that JS divergence is not systematically biased by gene-set dimensionality ({int(_phaseC_dim.get("n_trials", 2000)):,} random Dirichlet pairs across dimensions 50\u20135,000: mean JS 0.155\u20130.159, ratio {_phaseC_dim.get("ratio_2000_to_1130", 1.001):.3f} between d = 1,130 and d = 2,000; Supplementary Fig. 13); the systematic inflation of k_f over k_n thus arises from HVG selection bias, which the empirical calibration absorbs (Supplementary Methods 5.1).')

heading('Permutation test', level=2)
p('Statistical significance was assessed with permutation tests whose exchangeability unit and gene-selection handling follow each dataset\u2019s structure. For the mouse pilot, Tabula Sapiens, and TCGA, labels were permuted between groups (B = 1,000), pseudobulks recomputed, and \u03c9 recalculated under the same per-pair gene-selection procedure as the observed value, so the null incorporates gene selection. The TCGA per-cancer test additionally holds the identity panel fixed (anti-conservative; the corresponding P > 0.9 values are uninformative at the aggregate level because aggregate k_n sits at the denominator floor in 3 of 5 cancer types, and the reversal claim rests on the pair-level cluster bootstrap; Supplementary Methods 5.2). For the brain, the authoritative null is the block-shuffle permutation below. Empirical P-values are one-sided, P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1) (lower tail for the brain per-pair screen), standardized effect size SES = (\u03c9_obs \u2212 mean(\u03c9_null))/sd(\u03c9_null) is reported as a descriptive complement, and Benjamini-Hochberg FDR [44] is applied within each dataset.')

heading('Datasets', level=2)
p(f'Tabula Muris FACS SmartSeq2 [8]: {_ds["tabula_muris_cells"]:,} cells, {_ds["tabula_muris_genes"]:,} genes, {_ds["tabula_muris_organs"]} organs; post-QC {_ds["tabula_muris_ct_entries"]} cell-type entries, yielding C(38, 2) = 703 analyzed pairs. HVGs: scanpy [45] flavor="seurat" [46,47], n_top_genes={_ds["n_hvg"]:,}.')

p(f'Tabula Sapiens v1.0 [9] via CZ CELLxGENE Discover [48]: post-QC {_ds["tabula_sapiens_cells"]:,} cells, {_ds["tabula_sapiens_genes"]:,} genes, {_ds["tabula_sapiens_ct_entries"]} cell-type entries across 6 organs; {_h["n_ct_analyzed"]} entries passed the pairwise-analysis filters, yielding {_h["n_pairs_total"]:,} analyzed pairs. HK genes: HRT Atlas v1.0 ({_ds["hrt_atlas_n_hk"]:,} genes; human column).')

p('TCGA bulk RNA-seq [49]: five cancer types from NCI Genomic Data Commons via TCGAbiolinks [50] and cBioPortal [51]: LUAD 493 tumor + 76 normal; LUSC 534 + 58; LIHC 398 + 57; KIRC 750 + 82; BRCA 1,010 + 109 (3,567 samples, of which 3,535 enter the pair-level analysis after the barcode-audit exclusion below; all 32 excluded cell-line aliquots are LIHC tumors, leaving 366). TPM values from UCSC Xena were filtered (mean \u2265 0.5 TPM within cancer type) and log2(TPM + 1) transformed. BRCA PAM50 subtypes [52,53] (522 samples), LIHC Edmondson grade [54] (372 patients with calls), and LUAD mutation calls (492 samples: 61 EGFR, 120 KRAS, 311 WT) were retrieved from cBioPortal; the 32 cell-line-derived LIHC samples shipped in the LUSC matrix were excluded after a barcode audit (Supplementary Methods 5.3).')

p('Human brain atlas [12]: Siletti et al. (2023) single-nucleus RNA-seq (v3.11) from CZ CELLxGENE Discover [48], Nonneurons.h5ad (888,263 nuclei, 59,480 genes, 108 regions) in 10 supercluster_term classes; after filtering (\u2265 20 nuclei per (region, cell_type) group, \u2265 50 per region), 886,808 nuclei contributed (per-class counts in Supplementary Methods 5.4). Pseudobulks are cell-count-weighted means of per-library mean expression per group, normalized (target_sum = 10,000) and log1p-transformed at the pseudobulk level; \u03c9 was computed for all same-cell-type cross-region pairs (31,764) with the hybrid scheme (HK: 1,115 HRT Atlas genes matched to the Siletti annotation; per-pair top-200 selection within a pre-filtered pool of 5,000 non-HK genes with highest mean expression).')

heading('Method comparison', level=2)
p(f'We computed five metrics on all {_h["n_pairs_total"]:,} Tabula Sapiens pairs: CKI \u03c9 (hybrid scheme), raw JS divergence (all genes), Spearman distance (1 \u2212 \u03c1), cosine distance (1 \u2212 cos \u03b8), and marker Jaccard distance (1 \u2212 Jaccard index of top-200 expressed genes); one pseudobulk per cell-type entry from its largest donor, and inter-metric Spearman correlations via scikit-learn.')

heading('Multiplicative residual model for brain regional analysis', level=2)
p('For the brain regional analysis, a multiplicative model detects (cell_type, region_pair) combinations with anomalously low \u03c9: expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, with \u03bc_ct the cell type\u2019s global mean \u03c9, \u03bc_pair the region pair\u2019s mean \u03c9, and \u03bc_grand the global mean over all 31,764 pairs (38.55); the residual = observed/expected, with tiers Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the pair), Moderate (< 0.5, \u03c9 < 25), Weak (< 0.75, \u03c9 < 35). Significance uses a block-shuffle null preserving the joint cell-type \u00d7 region design: 10x libraries (sample_id) are blocks whose sample-to-region assignment is permuted (preserving per-region library counts), after which region pseudobulks, all pair \u03c9 values, and residuals are recomputed\u2014retaining library-level structure while breaking the cell\u2013region association (B = 1,000; minimum resolvable P \u2248 9.99 \u00d7 10\u207b\u2074). Per-pair P-values use the one-sided lower tail (upper tail reported complementarily), with Benjamini-Hochberg FDR across m = 31,764 pairs; q < 0.05 would require B \u2248 6 \u00d7 10\u2075 permutations, so the per-pair FDR outcome reflects permutation resolution rather than evidence against candidates (Statistics and reproducibility). A cell-type-level test asks whether regional structure raises a class\u2019s mean \u03c9 (one-sided upper tail), and a pseudo-region negative control re-ran the identical test on 127,756 pseudo-pairs (Supplementary Note 12; full design in Supplementary Methods 5.6).')


heading('Robustness and calibration analyses', level=2)
p('Robustness analyses (brain; full designs in Supplementary Methods 5.7). Donor confounding: cross-region \u03c9 was recomputed using only same-donor (donor, region) pseudobulk pairs (94.5% of region pairs share at least one donor). k_n estimator sensitivity: four aggregation schemes (per-pair, aggregate-first, global-k_n, k_f-only/k_n-only orderings) were compared by Spearman correlation of the ten class means. Scheme-matched split-half calibration: the random-split calibration was repeated inside the brain atlas (29 populations, B = 50 splits) and Tabula Sapiens (71 populations, B = 50) with each dataset\u2019s own pipeline. Lineage enrichment and tier sensitivity: hypergeometric test over 31,764 pairs (12,775 oligodendrocyte-lineage), corroborated by permutation (B = 100,000), over a grid of tier thresholds. Class-size confounding: class-mean k_n and \u03c9 were tested against class size and detection depth, an equal-n control downsampled every class to 4,118 nuclei (20 replicates), and the landscape recomputed at group-size thresholds 10/50/100. A combined span- and size-matched control downsamples classes within the 21 intra-cerebellar pairs (target 7,965 nuclei, 20 replicates). RNA-quality proxies: per-pair OLS of log10(k_n/k_f/\u03c9) on detected genes, total UMI, and mitochondrial fraction at (class, library) and (class, region) levels.')

p('Donor-stratified null (brain). The class-level permutation test was re-run with shuffles restricted within donors (B = 1,000; identical pipeline), preserving each donor\u2019s library counts and per-region block structure; single-library donor blocks were held fixed and identity assignments retained as valid draws. The donor-stratified null is strictly the more conservative test; accompanying free-null P-values come from an independent Monte-Carlo re-run, so small differences from the primary analysis reflect Monte-Carlo variability (values in Supplementary Methods 5.7).')

heading('Ground-truth simulation', level=2)
p('To measure specificity and sensitivity against a known ground truth, perturbations of known magnitude were injected into a real background (Tabula Muris FACS marrow B cells, 1,848 cells; gene set: 1,064 matched HK genes plus the 5,000 highest-mean non-HK genes). Each replicate resampled two groups of 200 cells; functional signal was a multiplicative 2^\u03b4 shift (\u03b4 = 0.125\u20132) on a fixed 200-gene non-HK module in group B; neutral perturbations were 2^\u03b7 shifts (\u03b7 = 0.25\u20131) on HK genes or Poisson noise (\u03b5 = 0.3\u20131) in group A. Six metrics were computed per replicate with the brain code path; detection thresholds were calibrated per metric as the 95th percentile of 200 baseline replicates; signal scenarios used three module seeds (42, 137, 2024); robustness scenarios (30% dropout, twofold depth, fourfold imbalance) and module sizes (m = 50, 200, 500) were run at \u03b4 = 0.25 and 1. The design was repeated in a second background (skin keratinocyte stem cells, 1,371 cells; 1,750 replicates per background). Full design and results: Supplementary Note 1 and Supplementary Methods 5.8.')

heading('Perturbation demonstration (IFN-\u03b2 PBMC)', level=2)
p('For a real perturbation with known ground truth, we re-analyzed the droplet arm of Kang et al. [14] (GEO: GSE96583): PBMCs from eight donors, control versus 6-hour IFN-\u03b2 stimulation captured in two 10x lanes (condition fully confounded with lane, disclosed in Supplementary Note 6; cross-metric contrasts, not absolute detection, are the informative quantity). Singlets with annotated cell types were retained (24,413 cells, six cell types); pseudobulks per (donor, condition) were computed from raw counts, normalized to 10,000, log1p-transformed; \u03c9, k_f, k_n, and raw JS were evaluated under the per-pair top-200 scheme for stimulated-versus-control (perturbation class) and donor-versus-donor (donor-drift class) comparisons. Significance: condition labels permuted within donor (B = 1,000, genes re-selected per permutation, one-sided upper tail); separability: exact rank AUC per metric per cell type (scripts and outputs in Supplementary Methods 5.9).')

heading('Neutral-drift calibration on technical replicates', level=2)
p('Neutral-drift specificity was tested on real technical replicates against a per-pair size-matched cell-shuffle null: nuclei of the two groups are pooled, permuted, and re-split into disjoint subsets of the observed sizes, so each pair is compared against a null matching its donor, cell type, and group sizes (B = 200 per pair for Kang; 100/30/30 for brain tiers T1/T2/T3, the B = 30 tiers read as tier-level calibrations). Calibration is reported as observed/null median; the false-positive element as observed > own null 95th percentile. Kang batch 1 [14]: unstimulated PBMCs from eight donors across three 10x lanes (every donor in exactly two lanes) yielded 30 same-donor, same-condition cross-lane pairs across six cell types, evaluated on k_n (HRT Atlas HK genes [13]), k_f, \u03c9, raw JS, and cosine. Brain drift ladder [12]: 2,732 (cell class, library) groups with \u2265 20 nuclei defined library-level pairs in three tiers (the per-pair null constituting the fourth ladder tier)\u2014T1, same (donor, region), 2,161 pairs; T2, same region different donors, 1,089; T3, same donor different regions, 1,656 (T2/T3 subsampled at 200 per cell class)\u2014evaluated for seven metrics including Spearman distance and a pairwise marker Jaccard distance (definitions, seeds, scripts in Supplementary Methods 5.10; per-class values in Section 3.12 of the Supplementary Information).')

heading('Fixed gene-panel ablation', level=2)
p('To test whether the brain conclusions depend on the per-pair circular selection of k_f genes, the entire brain landscape (31,764 pairs, identical keep set, pseudobulks, k_n) was recomputed under three alternative schemes: (i) a fixed panel of 2,000 non-HK genes with highest global mean; (ii) a leave-pair-out panel (top-200 by mean absolute difference over all other region pairs of the same cell type); (iii) all 5,000 non-HK genes. Pair-level and class-level rank agreement (Spearman), circularity inflation ratios, and residual-ranking agreement were summarized, and a scheme-matched block-shuffle null (B = 200) verified class-level significance under leave-pair-out (full results: Supplementary Note 7 and Supplementary Methods 5.11).')

heading('Per-sample divergence and group statistics (TCGA)', level=2)
p('Per-tumor statistics were derived from the linear-normalization pair table (34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table: 2,000 TT and 2,000 TN seeded-subsampled pairs per cancer type plus complete NN pairs; Monte-Carlo error ~0.01\u20130.02 ratio units) as the mean of \u03c9, k_f, k_n over all pairs in which a sample participates (median 4\u201311 per tumor). Group-level NN/TT and k_n ratios are ratios of means with 95% CIs from a sample-level cluster bootstrap (B = 1,000; tumor and normal samples resampled independently, pairs reweighted by endpoint weights). LUAD driver groups (61 EGFR, 120 KRAS, 311 WT with pair coverage; 2 double mutants excluded) were tested by Kruskal-Wallis with Dunn\u2013Holm post-hoc tests and within-group bootstrap CIs (B = 1,000). Covariate adjustment used ESTIMATE stromal/immune scores (official 141 + 141 gene sets, rank-based single-sample enrichment over 45,504 expressed genes; combined score as covariate) and LUAD smoking status, age, and sex from cBioPortal (87% coverage), fitted by OLS (metric ~ group + covariates; pack-years reported descriptively). The LIHC survival analysis used Cox proportional-hazards regression with per-tumor \u03c9 standardized per SD, adjusted for AJCC stage, Edmondson grade, age, and sex, with k_f-only, k_n-only, and tumor\u2013normal-\u03c9 sensitivity models (scripts and outputs in Supplementary Methods 5.12).')

heading('Clinical severity analysis', level=2)
p('Supplementary within-cancer-type stratifications (BRCA PAM50 [52,53], LIHC Edmondson grade [54], LUAD mutations; all cBioPortal-derived as above) used intratumoral \u03c9 per clinical stratum, tested by Kruskal-Wallis or Jonckheere-Terpstra trend tests; paired tumor\u2013normal comparisons are reported descriptively, and k_f-only/k_n-only component controls used the identical pipeline (Supplementary Note 9; Supplementary Methods 5.12).')

heading('Computational environment', level=2)
p('Typical runtime for a single cell-type pair is under 5 minutes; the full brain analysis required ~72 core-hours on a Windows x64 workstation (32 GB RAM; verified environment in the Reproducibility Guide). Analyses used Python 3.14.4 with scanpy 1.12.1 [45], scipy \u2265 1.10.0, numpy \u2265 1.23.0, pandas \u2265 1.5.0, matplotlib \u2265 3.6.0, seaborn \u2265 0.12.0 [55], and scikit-learn \u2265 1.2.0 [56]; seeds fixed at 42 unless noted (Supplementary Methods 5.13). With B = 1,000 permutations the Monte Carlo standard error of the empirical P-value is ~0.016 at P = 0.5, so seed variation has negligible impact.')

heading('Statistics and reproducibility', level=2)
p('We report summary statistics as mean \u00b1 s.d. or median [IQR] as noted. Resampling-based inference [57] (permutation for P-values; bootstrap for CIs) used B = 1,000 across all four datasets, with one-sided empirical P-values P = (count(\u03c9_null \u2265 \u03c9_obs) + 1)/(B + 1) and identity genes re-selected per iteration (TCGA fixed-panel excepted). Benjamini-Hochberg FDR [44] is applied within each dataset at two levels: group-level tests (m = 10 brain classes, 17 human cell types, 15 mouse pairs, 5 cancer types; BH thresholds for the most significant test all exceed the resolvable P-value 9.99 \u00d7 10\u207b\u2074) and the brain per-pair screen (m = 31,764; the BH threshold at 0.05/31,764 \u2248 1.6 \u00d7 10\u207b\u2076 lies ~600-fold below the smallest resolvable P, so q < 0.05 is unattainable without ~635 floor P-values or B \u2248 6 \u00d7 10\u2075 permutations). The per-pair FDR outcome (minimum q = 0.520) is thus a statement about permutation resolution; raw-P distribution: 1,960 of 31,764 pairs at raw P < 0.05 versus ~1,588 expected under a global null.')

p('Bootstrap 95% CIs for \u03c9 point estimates resample pair-level values (B = 10,000, percentile method); because pairs nest within regions, region-clustered block bootstrap CIs (B = 2,000) are the preferred uncertainty summary for landscape quantities (gradient 6.10 [5.55, 9.63]; grand mean 38.55 [36.35, 40.73]; Strong count 39 [12, 74]). Per-class calibrated quantities propagate calibration-denominator uncertainty via a joint two-stage region-clustered bootstrap (B = 5,000; Supplementary Note 3), superseding the earlier anti-conservative i.i.d. interval; studentized (bootstrap-t) intervals use an influence-function sandwich standard error with log-scale delta method (B = 5,000; coverage 0.953/0.951; Supplementary Methods 5.14). The \u03c9 distribution was characterized by skewness, kurtosis, and normality tests: all right-skewed (brain 2.22; mouse 0.99; human 1.17), normality rejected for the large datasets. The split-half calibration experiment (300 \u03c9 values) yielded mean \u03c9 = 7.70 (two-stage bootstrap over the six populations, B = 5,000: 95% CI [6.38, 9.82]; the 300-value interval [7.37, 8.02] treats nested splits as independent and is anti-conservative; SD of replicate means 1.15; legacy estimate 6.67 consistent), reflecting systematic k_f inflation from identity-gene selection, which the permutation null accounts for by construction. Gradient-level controls additionally use a donor cluster bootstrap (B = 1,000, seed 42; four donors resampled with replacement, full pipeline recomputed per resample).')

p('Statistical conventions. All P-values are one-sided permutation tests (B = 1,000) unless otherwise specified; Benjamini-Hochberg FDR within each dataset. Non-parametric tests (Spearman, Mann-Whitney U, Kruskal-Wallis, Jonckheere-Terpstra) are two-sided with exact P-values, except the mouse-pilot X-versus-C calibration contrast (Fig. 2c; one-sided U, exploratory pilot n = 15). Effect sizes include SES from the permutation null. Bootstrap CI resample counts are reported per analysis (B = 1,000 composition cluster bootstrap and TCGA ratios; 2,000 region-clustered; 5,000 joint and studentized; 10,000 pair-level point estimates), with Monte Carlo errors in the Supplementary Information. All analyses use JS divergence with base-2 logarithm; sample sizes are reported per comparison.')

heading('Use of large language models', level=2)
p('During the preparation of this work the authors used AI-assisted tools (large language model-based assistants) for computational debugging, statistical code review, and language editing. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.')


# ============================================================
# DATA AVAILABILITY / CODE AVAILABILITY (NC: after Methods, before References;
# no literature citations inside either section)
# ============================================================
heading('Data availability', level=1)
p('Tabula Muris data: GEO accession GSE109774. Tabula Sapiens data: CZ CELLxGENE Discover (https://cellxgene.cziscience.com/, accessed July 2025). TCGA data: NCI Genomic Data Commons (https://portal.gdc.cancer.gov/). HRT Atlas (optional human/mouse housekeeping-gene reference): https://www.housekeeping.unicamp.br. Human brain atlas: CZ CELLxGENE Discover, collection ID 283d65eb-dd53-496d-adb7-7570c7caa443 (https://cellxgene.cziscience.com/collections/283d65eb-dd53-496d-adb7-7570c7caa443, accessed July 2025). Kang et al. IFN-\u03b2-stimulated PBMC data: GEO accession GSE96583. GTEx V8 gene-level TPM and sample metadata: GTEx Portal (https://gtexportal.org/, lung, liver, kidney cortex, and breast; accessed September 2026). Microglia supercluster data: CZ CELLxGENE Discover, same collection as the brain atlas (regenerable via notebooks/nc50_brain_atlas_microglia.py in the companion repository). BRCA PAM50 subtype assignments: cBioPortal (brca_tcga_pub study, PAM50_SUBTYPE clinical attribute). MSigDB Hallmark gene sets (Liberzon et al. 2015; see References): accessed via the Enrichr gene-set library (MSigDB_Hallmark_2020; local mirror data/tcga/hallmark_2020.gmt in the companion repository). All Supplementary Tables (1\u201319) are provided in CKI_Supplementary_Tables_NC.xlsx.')

heading('Code availability', level=1)
p('The CKI source code (v0.5.2) is publicly available at https://github.com/zhanglknt/CKI-cell-type-identification (tag v0.5.2) under the MIT License. A permanent archival copy has been deposited at Zenodo (concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.2: 10.5281/zenodo.22949350). The package requires Python \u22653.10 and runs on Linux, macOS, and Windows (continuous integration covers Linux; macOS and Windows are verified on local workstations). A Dockerfile is provided in the repository for containerized reproducibility. All analysis notebooks and processed data matrices are available in the same GitHub repository (tag v0.5.2) and are included in the Zenodo archive (concept DOI: 10.5281/zenodo.20405458).')

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

p('Supplementary Information is available for this paper: Supplementary Notes 1\u201316, Supplementary Figs. 1\u201314, Supplementary Tables 1\u201319, Supplementary Methods (Sections 5.1\u20135.14), and the Reproducibility Guide (providing step-by-step instructions, the verified computational environment, and spot-check values for reproducing all analyses, figures, and tables reported in this work).')

p('Correspondence and requests for materials should be addressed to L.Z.')



# ============================================================
# FIGURE LEGENDS
# ============================================================
heading('Figure legends', level=1)

p('Figure 1. The CKI framework. (a) Conceptual analogy between Ka/Ks in molecular evolution and CKI in transcriptomics. Ka/Ks uses synonymous substitution rate (Ks) as a neutral baseline; \u03c9 = Ka/Ks > 1 indicates positive selection (a heuristic analogy only, not a formal population-genetic claim). CKI uses housekeeping gene divergence for k_n\u2014the constrained counterpart of the synonymous baseline\u2014and identity gene divergence for k_f\u2014the counterpart of nonsynonymous divergence; \u03c9 = k_f/k_n quantifies transcriptomic divergence relative to the baseline, read against the empirical calibration baseline rather than against 1. (b) Computational pipeline: raw count matrix \u2192 pseudobulk \u2192 JS divergence on HK genes (k_n) and identity genes (k_f) \u2192 \u03c9 = k_f/k_n. (c) Bootstrap distribution of the mean split-half control \u03c9 (B = 10,000 resamples of the 300 mouse-pilot split-half control \u03c9 values from 50 replicates across six control populations), with the median indicated by the dashed line and the control mean (the empirical calibration baseline 7.70, two-stage population-bootstrap 95% CI [6.38, 9.82]) by the dotted line. (d) Scatter plot of k_n vs. k_f, showing that functional variation dominates constrained baseline. (e) \u03c9 distribution with \u03c9 = 1 (the theoretical baseline for equivalent populations, marked by dashed line) and the empirical calibration baseline \u03c9 = 7.70 indicated; \u03c9 = 1 is never observed in practice because identity-gene selection inflates k_f relative to k_n (see Results).')

p(f'Figure 2. CKI calibration on Tabula Muris mouse data, metric correlation structure on Tabula Sapiens, and functional-change detection in the ground-truth simulation. (a) k_n calibration across six Tabula Muris cell types from control comparisons (C category: random split of same population). k_n values are stable across cell types, consistent with constrained baseline behavior. (b) Component decomposition of k_n and k_f across four comparison categories: C (random split of the same population), S (same cell type, different organ), D (different cell type, same organ), and X (different cell type, different organ). k_f increases monotonically with biological distance, while k_n shows far smaller variation across categories. (c) \u03c9 distribution by comparison category (log scale) from the mouse pilot calibration dataset. Boxes: median and IQR; whiskers, 1.5\u00d7 IQR. \u03c9 increases monotonically from control splits (C) to cross-organ comparisons (X); X vs. C, one-sided Mann-Whitney test. (d) Spearman correlation heatmap of five metrics on n = {_h["n_pairs_total"]:,} Tabula Sapiens pairs. CKI \u03c9 is negatively correlated with all four standard metrics; because k_n is itself positively correlated with the standard metrics, this negativity partly reflects the \u03c9 denominator (see Results). Standard metrics form a positive cluster. (e) ROC curves for discriminating injected functional signal (\u03b4 \u2265 0.25) from neutral drift in the semi-synthetic ground-truth simulation (marrow B-cell background; 600 functional versus 250 neutral replicates). CKI \u03c9 gave the highest AUC of six metrics (0.80, DeLong 95% CI [0.770, 0.838]); independent replication on a skin keratinocyte background gave AUC = 0.91 (thresholded power differs by background: 0/150 detections at \u03b4 = 1 on marrow versus 0.91 on keratinocyte; see Results).')

p('Figure 3. Real-data neutral-drift calibration on technical replicates. (a) Schematic of the four-tier drift ladder. Library-level pairs within each brain cell class are arranged by drift source: the per-pair n-matched null (pooled nuclei of the two libraries, permuted and re-split at the observed group sizes) embeds same-library sampling noise; T1 pairs two 10x libraries of the same donor, region, and cell type (2,161 pairs; pure technical drift; ground truth: no functional difference); T2 crosses donors within a region (1,089 pairs; technical plus inter-individual drift); T3 crosses regions within a donor (1,656 pairs; regional biology; positive control). (b) Brain calibration distributions (observed / own n-matched null median; log scale) for seven metrics across tiers T1\u2013T3; boxes show median and IQR (whiskers not shown; extreme tails clipped at the 2nd\u201398th percentiles for display). \u03c9 (leftmost metric) stays near 1 at T1 and shows the shallowest gradient to T3, whereas raw JS, cosine, Spearman, and k_f rise several-fold. (c) False-positive rates on T1 (technical drift, dark) and T2 (donor drift, light): fraction of pairs whose observed value exceeds its own null 95th percentile, with Wilson 95% CIs; the dotted line marks the nominal 5% level. \u03c9 misreports least among the continuous divergence metrics at both tiers (T1: 28.6% versus 37.6\u201345.2% for the others); marker Jaccard is lower still on the false-positive statistic (T1 19.9%, T2 74.7%) but responds weakest to real regional divergence (T3 calibration 1.41 versus 1.80 for \u03c9 and 2.98 for raw JS; panel b) and offers no k_n/k_f decomposition. (d) Replication in the Kang IFN-\u03b2 PBMC batch-1 technical replicates (30 same-donor, same-condition cross-lane pairs, n-matched null with B = 200 per pair): \u03c9 FPR = 0 of 30 with calibration median 0.96, versus 36.7% for raw JS and 23.3% for cosine. \u03c9 lowers drift misreporting to the minimum among compared metrics while retaining sensitivity to genuine biological divergence\u2014a relative-calibration advantage, not absolute immunity (see Results).')

p('Figure 4. Pan-cancer tissue-level divergence in tumors. (a) Ratio of mean normal\u2013normal (NN) to tumor\u2013tumor (TT) \u03c9 per cancer type (blue; ranked by effect size), with sample-level cluster-bootstrap 95% CIs (B = 1,000); the amber axis shows the corresponding tumor/normal ratio of the housekeeping baseline k_n (TT/NN, means with 95% CIs), which exceeds 1 in all five cancer types while the NN/TT ratio of k_f does not\u2014the reversal is denominator-driven. The two axes use independent scales so that both series remain legible. Dotted line, ratio = 1. (b) Per-tumor \u03c9 in LUAD by driver mutation (wild-type n = 311, EGFR-mutant n = 61, KRAS-mutant n = 120; boxes, median and IQR; points, individual tumors). Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; brackets, Dunn post-hoc P-values with Holm correction. (c, d) The same stratification for the components k_f (c) and k_n (d): the KRAS contrast carries a functional component (KRAS > EGFR under k_f alone, P_Holm = 0.015; KRAS versus WT retained after purity and smoking adjustment, adjusted P = 0.009 and 0.029) together with a lower k_n baseline (WT > KRAS, P_Holm = 4.2 \u00d7 10\u207b\u2074), whereas the apparent EGFR elevation dissolved under purity adjustment (all adjusted P > 0.4), consistent with an admixture artefact rather than a baseline shift. All values from the linear-normalization re-computation (Methods).')

p(f'Figure 5. Cross-organ cell-type conservation. (a) CKI \u03c9 ranking of 17 cell types with cross-organ comparisons (n = 59 pairs) within the Tabula Sapiens human atlas, with well-sampled cell types (n \u2265 5 pairs) ranked first and sparsely sampled types (n < 5) listed separately. Among well-sampled types, CD8+ T cells, plasma cells, and neutrophils rank lowest; endothelial cells and erythrocytes rank highest (n = 3 pairs each, suggestive only). (b) \u03c9 distribution across all cell-type pairs, showing conserved vs. variable cell types. (c) Cross-organ \u03c9 gradient (mean \u00b1 SD) showing systematic variation across organ pairs. (d) Top 5 conserved cell-type pairs with the lowest cross-organ \u03c9 values.')

p('Figure 6. Brain regional cell-type differentiation and region-association inference. (a) Brain region map schematic showing anatomical regions analyzed in the Siletti et al. atlas. (b) \u03c9 gradient across 10 non-neuronal cell classes (mean \u03c9 per class, block-shuffle observed landscape). Bergmann glia and vascular cells (mean \u03c9 = 13.56) show the lowest regional divergence; astrocytes (mean \u03c9 = 82.75) show the highest, a 6.10-fold gradient that is an uncorrected upper bound inflated by class-size imbalance; the combined span- and size-matched control gives 3.66-fold (donor-level cluster bootstrap 95% CI [1.92, 3.78]), while the size-only equal-n estimate (1.74-fold) is not donor-robust (Supplementary Note 10). The gradient is a composite signal dominated by the k_n denominator (3.21-fold k_n versus 2.03-fold k_f contribution at the endpoint contrast; see Results). (c) Region-associated candidate detection: multiplicative residual model identifies 39 Strong candidates (residual < 0.3, \u03c9 < 15, lowest \u03c9 in pair) among 31,764 cross-region comparisons, shown as tier counts as a percentage of all pairs; under a design-matched null the Strong rule expects 148.3 candidates, so the observed 39 are anti-enriched (P(null count \u2265 39) = 1.0) and none survives FDR correction; only 3 of 39 are retained under a global-k_n estimator, so the catalogue is hypothesis-generating. (d) Observed vs. expected \u03c9 for the five strongest Strong candidates across all cell classes (lowest residuals), showing the gap between observed regional similarity and the cell-type-specific expectation.')

p('Table 1. Cross-organ conservation ranking by cell type (Tabula Sapiens, n = 59 same-cell-type cross-organ pairs). Well-sampled cell types (n \u2265 5 cross-organ pairs) are ranked first by mean \u03c9; sparsely sampled cell types (n < 5 pairs; SD shown only where n > 1) are listed below the divider, and their rankings should be interpreted as suggestive only. Because the k_n anchor is not calibrated across cell types (Discussion), cross-type gaps in mean \u03c9 are descriptive rather than calibrated. k_f-only controls for this ranking are reported in Supplementary Note 9. The table is provided as a separate file (CKI_Tables_NC.xlsx).')

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

p('Supplementary Fig. 14. Human-brain sanity check on the microglia supercluster (Supplementary Note 16). The microglia supercluster of the Human Brain Cell Atlas v1.0 (91,838 nuclei; microglial cell 88,494 versus CNS macrophage 3,344) provides a functional contrast not used in any main-text analysis. CKI \u03c9 separates the functional contrast from the neutral baseline completely (\u03c9 = 21.83 \u00b1 7.20 functional versus 1.30 \u00b1 0.36 neutral; Mann-Whitney P = 5.5 \u00d7 10\u207b\u00b9\u2074; exact rank AUC = 1.00); the margin is carried by k_f (AUC = 1.00), whereas k_n is only partially elevated (AUC = 0.89), the decomposition-first reading argued throughout. Standard metrics also separate the classes (raw JS, cosine, marker Jaccard AUC = 1.00; Spearman 0.90); the sanity-check value lies in \u03c9 tracking the functional contrast far above its own neutral baseline on an independent dataset.')















# == Save ==
# 72 = 73 groups (v49.5: 73 = 71 of v49.4 + 2 new in-text citations of ref 47,
# CZ CELLxGENE Discover) - 1 dangling [19] removed (nc55 F1: self-evaluation
# qualifier "strictly hypothesis-generating" needs no citation).
assert _cite_sup_count == 72, f'Expected 72 superscripted citation groups, got {_cite_sup_count}'
print(f'Superscripted citation groups: {_cite_sup_count}')
PROJECT_ROOT = Path(__file__).resolve().parent
write_tables_xlsx()
out = str(PROJECT_ROOT / "results" / "CKI_Manuscript_NC.docx")
doc.save(out)
print(f'Saved: {out}')
