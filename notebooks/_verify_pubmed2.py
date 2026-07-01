"""Verify all 36 references - use requests with SSL verify=False"""
import requests
import urllib.parse
import time
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

refs = [
    (1,  "Regev", "2017", "Human Cell Atlas", "eLife", "10.7554/eLife.27041"),
    (2,  "Luecken", "2019", "Current best practices single-cell RNA-seq analysis", "Mol Syst Biol", "10.15252/msb.20188746"),
    (3,  "Nei", "1986", "Simple methods estimating synonymous nonsynonymous nucleotide substitutions", "Mol Biol Evol", ""),
    (4,  "Hounkpe", "2021", "HRT Atlas v1.0 database housekeeping genes", "Nucleic Acids Res", "10.1093/nar/gkaa1118"),
    (5,  "Tabula Muris", "2018", "Single-cell transcriptomics 20 mouse organs", "Nature", "10.1038/s41586-018-0590-4"),
    (6,  "Tabula Sapiens", "2022", "Tabula Sapiens multiple-organ single-cell transcriptomic atlas humans", "Science", "10.1126/science.abl4896"),
    (7,  "Cancer Genome Atlas", "2014", "Comprehensive molecular profiling lung adenocarcinoma", "Nature", "10.1038/nature13385"),
    (8,  "Weinstein", "2013", "Cancer Genome Atlas Pan-Cancer analysis project", "Nat Genet", "10.1038/ng.2764"),
    (9,  "Cancer Genome Atlas Network", "2012", "Comprehensive molecular portraits human breast tumours", "Nature", "10.1038/nature11412"),
    (10, "Siletti", "2023", "Transcriptomic diversity of cell types across the adult human brain", "Nature", "10.1038/s41586-023-06812-9"),
    (11, "Tran", "2020", "benchmark of batch-effect correction methods single-cell RNA sequencing data", "Genome Biol", "10.1186/s13059-020-02054-8"),
    (12, "Korsunsky", "2019", "Fast sensitive and accurate integration of single-cell data with Harmony", "Nat Methods", "10.1038/s41592-019-0616-0"),
    (13, "Lopez", "2018", "Deep generative modeling for single-cell transcriptomics", "Nat Methods", "10.1038/s41592-018-0229-2"),
    (14, "Rosen", "2024", "Universal cell-type embeddings from single-cell atlases using protein language models", "Nat Methods", "10.1038/s41592-024-02233-5"),
    (15, "Storey", "2003", "Statistical significance for genomewide studies", "Proc Natl Acad Sci USA", "10.1073/pnas.1530509100"),
    (16, "Wolf", "2018", "SCANPY large-scale single-cell gene expression data analysis", "Genome Biol", "10.1186/s13059-017-1382-0"),
    (17, "Edmondson", "1954", "Primary carcinoma of the liver", "Cancer", ""),
    (18, "Perou", "2000", "Molecular portraits of human breast tumours", "Nature", "10.1038/35019593"),
    (19, "Parker", "2009", "Supervised risk predictor of breast cancer based on intrinsic subtypes", "J Clin Oncol", "10.1200/JCO.2008.18.1370"),
    (20, "Yang", "2007", "PAML 4 phylogenetic analysis by maximum likelihood", "Mol Biol Evol", "10.1093/molbev/msm088"),
    (21, "Tarashansky", "2021", "Mapping single-cell atlases throughout Metazoa unravels cell type evolution", "eLife", "10.7554/eLife.66747"),
    (22, "Jiang", "2024", "CACIMAR cross-species analysis of cell identities markers regulations and interactions", "Brief Bioinform", "10.1093/bib/bbae283"),
    (23, "Hao", "2021", "Integrated analysis of multimodal single-cell data", "Cell", "10.1016/j.cell.2021.04.048"),
    (24, "CZI Cell Science", "2025", "CZ CELLxGENE Discover single-cell data platform", "Nucleic Acids Res", "10.1093/nar/gkae1026"),
    (25, "Colaprico", "2016", "TCGAbiolinks an R/Bioconductor package for integrative analysis of TCGA data", "Nucleic Acids Res", "10.1093/nar/gkv1507"),
    (26, "Cerami", "2012", "cBio Cancer Genomics Portal an open platform for exploring multidimensional cancer data", "Cancer Discov", "10.1158/2159-8290.CD-12-0095"),
    (27, "Liberzon", "2015", "Molecular Signatures Database Hallmark Gene Set Collection", "Cell Syst", "10.1016/j.cels.2015.12.004"),
    (28, "Tsai", "2016", "Oligodendrocyte precursors migrate along vasculature in the developing nervous system", "Science", "10.1126/science.aah5232"),
    (29, "Akay", "2022", "Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration", "Neuron", "10.1016/j.neuron.2022.09.025"),
    (30, "Foerster", "2024", "Developmental origin of oligodendrocytes determines their function in the adult brain", "Nat Neurosci", "10.1038/s41593-024-01581-2"),
    (31, "Endo", "2024", "Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction", "EMBO J", "10.1038/s44318-024-00149-0"),
    (32, "Yang", "2024", "Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum", "Cell Discov", "10.1038/s41421-024-00663-6"),
    (33, "Tan", "2020", "Microglial regional heterogeneity and its role in the brain", "Mol Psychiatry", "10.1038/s41380-019-0610-3"),
    (34, "Menassa", "2022", "The spatiotemporal dynamics of microglia recruitment after myocardial infarction", "Nature", "10.1038/s41586-022-04636-5"),
    (35, "Walchli", "2024", "Single-cell atlas of the human brain vasculature across development adulthood and disease", "Nature", "10.1038/s41586-023-06699-8"),
    (36, "Hao", "2024", "Dictionary learning for integrative multimodal and scalable single cell", "Cell", "10.1016/j.cell.2024.08.025"),
]

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed_author_year(author, year, title_kw):
    query = f'"{author}"[Author] AND {year}[Date - Publication] AND ({title_kw})[Title]'
    url = f"{BASE}esearch.fcgi?db=pubmed&retmax=5&retmode=json&term={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, timeout=20, verify=False)
        data = r.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        return [f"ERR:{e}"]

def search_pubmed_doi(doi):
    url = f"{BASE}esearch.fcgi?db=pubmed&retmax=3&retmode=json&term={urllib.parse.quote(doi)}[DOI]"
    try:
        r = requests.get(url, timeout=20, verify=False)
        data = r.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        return [f"ERR:{e}"]

results = []
for num, author, year, keywords, journal, doi in refs:
    print(f"[{num:2d}] {author} {year} - {keywords[:50]}...", end=" ", flush=True)
    
    # Try author+year+title search
    kw_safe = keywords[:60]
    pmids = search_pubmed_author_year(author, year, kw_safe)
    time.sleep(0.3)
    
    found = False
    if pmids and isinstance(pmids, list) and len(pmids) > 0 and not str(pmids[0]).startswith("ERR"):
        print(f"OK (PMID:{pmids[0]})")
        results.append((num, "FOUND", pmids[0], ""))
        found = True
    elif doi:
        # Try DOI search
        doi_pmids = search_pubmed_doi(doi)
        time.sleep(0.3)
        if doi_pmids and isinstance(doi_pmids, list) and len(doi_pmids) > 0:
            print(f"OK via DOI (PMID:{doi_pmids[0]})")
            results.append((num, "FOUND_DOI", doi_pmids[0], ""))
            found = True
    
    if not found:
        reason = "Not in PubMed" if not doi else f"Not in PubMed (DOI:{doi})"
        print(f"NOT FOUND")
        results.append((num, "NOT_FOUND", "", doi))

print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)

for num, status, pmid, doi in results:
    icon = "OK " if "FOUND" in status else "XX"
    extra = f" (PMID:{pmid})" if pmid else ""
    print(f"  [{num:2d}] {icon}{extra}")

found_count = sum(1 for _, s, *_ in results if "FOUND" in s)
not_found = [r for r in results if r[1] == "NOT_FOUND"]

print(f"\nFound: {found_count}/36")
if not_found:
    print(f"\nReferences NOT in PubMed (to remove):")
    for num, _, _, doi in not_found:
        print(f"  [{num:2d}] {doi if doi else '(no DOI)'}")
