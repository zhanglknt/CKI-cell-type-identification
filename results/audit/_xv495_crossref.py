# xv495: verify 56 references against CrossRef via urllib
from pathlib import Path
import json, re, time, urllib.parse, urllib.request

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
OUT = ROOT / "results" / "audit" / "_xv495_crossref.json"
UA = {"User-Agent": "CKI-ref-check/1.0 (mailto:knightz@pumc.edu.cn)"}

REFS = [
    (1, "Regev", True, "The Human Cell Atlas", "eLife", "6", "e27041", "2017"),
    (2, "Korsunsky", True, "Fast, sensitive and accurate integration of single-cell data with Harmony", "Nat. Methods", "16", "1289-1296", "2019"),
    (3, "Lopez", False, "Deep generative modeling for single-cell transcriptomics", "Nat. Methods", "15", "1053-1058", "2018"),
    (4, "Rosen", True, "Toward universal cell embeddings: integrating single-cell RNA-seq datasets across species with SATURN", "Nat. Methods", "21", "1492-1500", "2024"),
    (5, "Tran", True, "A benchmark of batch-effect correction methods for single-cell RNA sequencing data", "Genome Biol.", "21", "12", "2020"),
    (6, "Nei", False, "Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions", "Mol. Biol. Evol.", "3", "418-426", "1986"),
    (7, "Yang", False, "PAML 4: phylogenetic analysis by maximum likelihood", "Mol. Biol. Evol.", "24", "1586-1591", "2007"),
    (8, "Tabula Muris Consortium", False, "Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris", "Nature", "562", "367-372", "2018"),
    (9, "Tabula Sapiens Consortium", False, "The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans", "Science", "376", "eabl4896", "2022"),
    (10, "Cancer Genome Atlas Research Network", False, "Comprehensive molecular profiling of lung adenocarcinoma", "Nature", "511", "543-550", "2014"),
    (11, "Cancer Genome Atlas Network", False, "Comprehensive molecular portraits of human breast tumours", "Nature", "490", "61-70", "2012"),
    (12, "Siletti", True, "Transcriptomic diversity of cell types across the adult human brain", "Science", "382", "eadd7046", "2023"),
    (13, "Hounkpe", False, "HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate reference transcripts by mining massive RNA-seq datasets", "Nucleic Acids Res.", "49", "D947-D955", "2021"),
    (14, "Kang", True, "Multiplexed droplet single-cell RNA-sequencing using natural genetic variation", "Nat. Biotechnol.", "36", "89-94", "2018"),
    (15, "Edmondson", False, "Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies", "Cancer", "7", "462-503", "1954"),
    (16, "Perou", True, "Molecular portraits of human breast tumours", "Nature", "406", "747-752", "2000"),
    (17, "Parker", True, "Supervised risk predictor of breast cancer based on intrinsic subtypes", "J. Clin. Oncol.", "27", "1160-1167", "2009"),
    (18, "W\u00e4lchli", True, "Single-cell atlas of the human brain vasculature across development, adulthood and disease", "Nature", "632", "603-613", "2024"),
    (19, "Pfau", True, "Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells", "Nat. Neurosci.", "27", "1892-1903", "2024"),
    (20, "Jones", True, "Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature", "Development", "150", "dev201805", "2023"),
    (21, "Tan", False, "Microglial regional heterogeneity and its role in the brain", "Mol. Psychiatry", "25", "351-367", "2020"),
    (22, "Barry-Carroll", False, "The molecular determinants of microglial developmental dynamics", "Nat. Rev. Neurosci.", "25", "414-427", "2024"),
    (23, "Menassa", True, "The spatiotemporal dynamics of microglia across the human lifespan", "Dev. Cell", "57", "2127-2139.e6", "2022"),
    (24, "Barry-Carroll", True, "Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling", "Cell Rep.", "42", "112425", "2023"),
    (25, "Tsai", True, "Oligodendrocyte precursors migrate along vasculature in the developing nervous system", "Science", "351", "379-384", "2016"),
    (26, "Su", True, "Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development", "Neuron", "111", "190-201.e8", "2023"),
    (27, "Foerster", True, "Developmental origin of oligodendrocytes determines their function in the adult brain", "Nat. Neurosci.", "27", "1545-1554", "2024"),
    (28, "Reeber", False, "Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum", "Cerebellum", "17", "392-403", "2018"),
    (29, "Yang", True, "Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum", "Cell Discov.", "10", "22", "2024"),
    (30, "Zhang", True, "Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction", "EMBO J.", "43", "5114-5140", "2024"),
    (31, "Vandesompele", True, "Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes", "Genome Biol.", "3", "RESEARCH0034", "2002"),
    (32, "Eisenberg", False, "Human housekeeping genes, revisited", "Trends Genet.", "29", "569-574", "2013"),
    (33, "Elowitz", False, "Stochastic gene expression in a single cell", "Science", "297", "1183-1186", "2002"),
    (34, "Newman", True, "Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise", "Nature", "441", "840-846", "2006"),
    (35, "Raj", False, "Nature, nurture, or chance: stochastic gene expression variation and its consequences on individual cellular fitness", "Cell", "135", "216-226", "2008"),
    (36, "Tarashansky", True, "Mapping single-cell atlases throughout Metazoa unravels cell type evolution", "eLife", "10", "e66747", "2021"),
    (37, "Jiang", True, "CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions", "Brief. Bioinform.", "25", "bbae283", "2024"),
    (38, "Skinnider", True, "Cell type prioritization in single-cell data", "Nat. Biotechnol.", "39", "30-34", "2021"),
    (39, "Waxman", False, "De-regulation of common housekeeping genes in hepatocellular carcinoma", "BMC Genomics", "8", "243", "2007"),
    (40, "Bakken", True, "Comparative cellular analysis of motor cortex in human, marmoset and mouse", "Nature", "598", "111-119", "2021"),
    (41, "Marques", True, "Oligodendrocyte heterogeneity in the mouse juvenile and adult central nervous system", "Science", "352", "1326-1329", "2016"),
    (42, "Spitzer", True, "Oligodendrocyte progenitor cells become regionally diverse and heterogeneous with age", "Neuron", "101", "459-471.e5", "2019"),
    (43, "Luecken", False, "Current best practices in single-cell RNA-seq analysis: a tutorial", "Mol. Syst. Biol.", "15", "e8746", "2019"),
    (44, "Lin", False, "Divergence measures based on the Shannon entropy", "IEEE Trans. Inf. Theory", "37", "145-151", "1991"),
    (45, "Benjamini", False, "Controlling the false discovery rate: a practical and powerful approach to multiple testing", "J. R. Stat. Soc. Series B Stat. Methodol.", "57", "289-300", "1995"),
    (46, "Wolf", False, "SCANPY: large-scale single-cell gene expression data analysis", "Genome Biol.", "19", "15", "2018"),
    (47, "Hao", True, "Integrated analysis of multimodal single-cell data", "Cell", "184", "3573-3587", "2021"),
    (48, "Hao", True, "Dictionary learning for integrative, multimodal and scalable single-cell analysis", "Nat. Biotechnol.", "42", "293-304", "2024"),
    (49, "Weinstein", True, "The Cancer Genome Atlas Pan-Cancer analysis project", "Nat. Genet.", "45", "1113-1120", "2013"),
    (50, "Colaprico", True, "TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data", "Nucleic Acids Res.", "44", "e71", "2016"),
    (51, "Cerami", True, "The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data", "Cancer Discov.", "2", "401-404", "2012"),
    (52, "Waskom", False, "seaborn: statistical data visualization", "J. Open Source Softw.", "6", "3021", "2021"),
    (53, "Pedregosa", True, "Scikit-learn: machine learning in Python", "J. Mach. Learn. Res.", "12", "2825-2830", "2011"),
    (54, "Efron", False, "An Introduction to the Bootstrap", "Chapman and Hall/CRC", "", "", "1994"),
    (55, "CZI Cell Science Program", False, "CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data", "Nucleic Acids Res.", "53", "D886-D900", "2025"),
    (56, "Liberzon", True, "The Molecular Signatures Database Hallmark Gene Set Collection", "Cell Syst.", "1", "417-425", "2015"),
]

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def sim(a, b):
    ta, tb = norm(a), norm(b)
    if not ta or not tb:
        return 0.0
    if ta == tb:
        return 1.0
    sa, sb = set(ta.split()), set(tb.split())
    return len(sa & sb) / max(len(sa), len(sb))

def query_crossref(title, rows=3):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": rows})
    url = f"https://api.crossref.org/works?{q}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

results = []
for num, auth1, etal, title, jrnl, vol, page, year in REFS:
    rec = {"num": num, "entry_first_author": auth1, "entry_etal": etal,
           "entry_title": title, "entry_journal": jrnl, "entry_vol": vol,
           "entry_page": page, "entry_year": year}
    try:
        data = query_crossref(title)
        items = data.get("message", {}).get("items", [])
    except Exception as e:
        rec["error"] = str(e)
        results.append(rec)
        print(f"[{num}] ERROR {e}", flush=True)
        time.sleep(1.0)
        continue
    best = None
    best_sim = -1
    for it in items:
        t = " ".join(it.get("title", [])[:1])
        s = sim(t, title)
        if s > best_sim:
            best_sim = s
            best = it
    rec["title_sim"] = round(best_sim, 3)
    if best is not None:
        rec["cr_title"] = " ".join(best.get("title", [])[:1])
        rec["cr_container"] = " ".join(best.get("container-title", [])[:1])
        rec["cr_vol"] = best.get("volume", "")
        rec["cr_issue"] = best.get("issue", "")
        rec["cr_page"] = best.get("page", "") or best.get("article-number", "")
        rec["cr_doi"] = best.get("DOI", "")
        rec["cr_type"] = best.get("type", "")
        dp = best.get("published-print") or best.get("published") or best.get("issued") or {}
        parts = dp.get("date-parts", [[None]])
        rec["cr_year"] = str(parts[0][0]) if parts and parts[0] else ""
        auths = best.get("author", [])
        rec["cr_n_authors"] = len(auths)
        rec["cr_first_family"] = auths[0].get("family", "") if auths else ""
        rec["cr_first_given"] = auths[0].get("given", "") if auths else ""
        if auths and not auths[0].get("family"):
            rec["cr_first_family"] = auths[0].get("name", "")
    print(f"[{num}] sim={rec['title_sim']} {rec.get('cr_first_family','')}/{rec.get('cr_year','')}/"
          f"{rec.get('cr_container','')[:40]}/{rec.get('cr_vol','')}/{rec.get('cr_page','')}", flush=True)
    results.append(rec)
    time.sleep(0.8)

OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", OUT)
