"""Verify all 36 references against PubMed E-utilities"""
import urllib.request
import urllib.parse
import json
import time
import xml.etree.ElementTree as ET
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

refs = [
    (1, "Regev A", "2017", "The Human Cell Atlas", "eLife", "6", "e27041", "10.7554/eLife.27041"),
    (2, "Luecken MD", "2019", "Current best practices in single-cell RNA-seq analysis", "Mol Syst Biol", "15", "e8746", "10.15252/msb.20188746"),
    (3, "Nei M", "1986", "Simple methods for estimating synonymous and nonsynonymous substitutions", "Mol Biol Evol", "3", "418", ""),
    (4, "Hounkpe BW", "2021", "HRT Atlas v1.0 database", "Nucleic Acids Res", "49", "D947", "10.1093/nar/gkaa1118"),
    (5, "Tabula Muris", "2018", "Single-cell transcriptomics of 20 mouse organs", "Nature", "562", "367", "10.1038/s41586-018-0590-4"),
    (6, "Tabula Sapiens", "2022", "The Tabula Sapiens", "Science", "376", "eabl4896", "10.1126/science.abl4896"),
    (7, "Cancer Genome Atlas", "2014", "Comprehensive molecular profiling of lung adenocarcinoma", "Nature", "511", "543", "10.1038/nature13385"),
    (8, "Weinstein JN", "2013", "The Cancer Genome Atlas Pan-Cancer analysis project", "Nat Genet", "45", "1113", "10.1038/ng.2764"),
    (9, "Cancer Genome Atlas", "2012", "Comprehensive molecular portraits of human breast tumours", "Nature", "490", "61", "10.1038/nature11412"),
    (10, "Siletti K", "2023", "Transcriptomic diversity of cell types across the adult human brain", "Nature", "622", "348", ""),
    (11, "Tran HTN", "2020", "A benchmark of batch-effect correction methods", "Genome Biol", "21", "12", ""),
    (12, "Korsunsky I", "2019", "Fast sensitive and accurate integration of single-cell data", "Nat Methods", "16", "1289", ""),
    (13, "Lopez R", "2018", "Deep generative modeling for single-cell transcriptomics", "Nat Methods", "15", "1053", ""),
    (14, "Rosen Y", "2024", "Universal cell-type embeddings from single-cell atlases", "Nat Methods", "21", "881", ""),
    (15, "Storey JD", "2003", "Statistical significance for genomewide studies", "Proc Natl Acad Sci", "100", "9440", ""),
    (16, "Wolf FA", "2018", "SCANPY large-scale single-cell gene expression data analysis", "Genome Biol", "19", "15", ""),
    (17, "Edmondson HA", "1954", "Primary carcinoma of the liver", "Cancer", "7", "462", ""),
    (18, "Perou CM", "2000", "Molecular portraits of human breast tumours", "Nature", "406", "747", ""),
    (19, "Parker JS", "2009", "Supervised risk predictor of breast cancer based on intrinsic subtypes", "J Clin Oncol", "27", "1160", ""),
    (20, "Yang Z", "2007", "PAML 4 phylogenetic analysis by maximum likelihood", "Mol Biol Evol", "24", "1586", ""),
    (21, "Tarashansky AJ", "2021", "Mapping single-cell atlases throughout Metazoa", "eLife", "10", "e66747", ""),
    (22, "Jiang J", "2024", "CACIMAR cross-species analysis", "Brief Bioinform", "25", "bbae283", ""),
    (23, "Hao Y", "2021", "Integrated analysis of multimodal single-cell data", "Cell", "184", "3573", ""),
    (24, "CZI Cell Science", "2025", "CZ CELLxGENE Discover", "Nucleic Acids Res", "53", "D886", ""),
    (25, "Colaprico A", "2016", "TCGAbiolinks", "Nucleic Acids Res", "44", "e71", ""),
    (26, "Cerami E", "2012", "The cBio Cancer Genomics Portal", "Cancer Discov", "2", "401", ""),
    (27, "Liberzon A", "2015", "The Molecular Signatures Database Hallmark", "Cell Syst", "1", "417", ""),
    (28, "Tsai HH", "2016", "Oligodendrocyte precursors migrate along vasculature", "Science", "351", "379", ""),
    (29, "Akay LA", "2022", "Astrocyte endfoot formation", "Neuron", "110", "3699", ""),
    (30, "Foerster S", "2024", "Developmental origin of oligodendrocytes", "Nat Neurosci", "27", "499", ""),
    (31, "Endo F", "2024", "Astrocyte allocation during brain development", "EMBO J", "43", "4423", ""),
    (32, "Yang L", "2024", "Single-cell multi-omics analysis of lineage development", "Cell Discov", "10", "25", ""),
    (33, "Tan YL", "2020", "Microglial regional heterogeneity", "Mol Psychiatry", "25", "351", ""),
    (34, "Menassa DA", "2022", "The spatiotemporal dynamics of microglia", "Nature", "609", "370", ""),
    (35, "Walchli T", "2024", "Single-cell atlas of the human brain vasculature", "Nature", "627", "546", ""),
    (36, "Hao Y", "2024", "Dictionary learning for integrative multimodal", "Cell", "187", "4379", ""),
]

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search_pubmed(first_author, year, title_keywords):
    """Search PubMed by author + year + title keywords"""
    query = f'"{first_author}"[Author] AND {year}[Date - Publication] AND {title_keywords}[Title]'
    url = f"{BASE}esearch.fcgi?db=pubmed&retmax=3&retmode=json&term={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids
    except Exception as e:
        return [f"ERROR: {e}"]

def fetch_summary(pmid):
    """Fetch article summary"""
    url = f"{BASE}esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
        result = data.get("result", {}).get(pmid, {})
        return {
            "title": result.get("title", "N/A"),
            "source": result.get("source", "N/A"),
            "doi": result.get("elocationid", "N/A"),
            "pmid": pmid,
        }
    except Exception as e:
        return {"error": str(e)}

results = []
for num, author, year, keywords, journal, vol, pages, doi in refs:
    # Use shorter keyword phrase for better matching
    kw_short = " ".join(keywords.split()[:4])
    print(f"[{num}] Searching: {kw_short}...", end=" ", flush=True)
    pmids = search_pubmed(author, year, kw_short)
    
    if pmids and isinstance(pmids, list) and len(pmids) > 0:
        # Verify by fetching details
        found = False
        for pid in pmids[:3]:
            summary = fetch_summary(pid)
            st = summary.get("title", "").lower()
            # Check if title matches keywords
            match = all(w.lower() in st for w in kw_short.split()[:3])
            if match:
                found = True
                print(f"OK (PMID:{pid})")
                results.append((num, "FOUND", pid, summary.get("source", ""), summary.get("doi", "")))
                break
        
        if not found:
            # Try broader search with DOI
            if doi:
                print(f"trying DOI...", end=" ", flush=True)
                doi_query = f'{doi}[DOI]'
                doi_url = f"{BASE}esearch.fcgi?db=pubmed&retmax=3&retmode=json&term={urllib.parse.quote(doi_query)}"
                try:
                    with urllib.request.urlopen(doi_url, timeout=15) as resp:
                        doi_data = json.loads(resp.read())
                    doi_ids = doi_data.get("esearchresult", {}).get("idlist", [])
                    if doi_ids:
                        print(f"OK via DOI (PMID:{doi_ids[0]})")
                        results.append((num, "FOUND_via_DOI", doi_ids[0], "", doi))
                    else:
                        print(f"NOT FOUND on PubMed")
                        results.append((num, "NOT_FOUND", "", "", doi))
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append((num, "ERROR", str(e), "", doi))
            else:
                print(f"NOT FOUND on PubMed (no DOI)")
                results.append((num, "NOT_FOUND", "", "", ""))
        
        if num % 5 == 0:
            time.sleep(0.5)  # Rate limiting
    elif isinstance(pmids, list):
        print(f"NOT FOUND on PubMed")
        results.append((num, "NOT_FOUND", "", "", ""))
    else:
        print(f"ERROR: {pmids}")
        results.append((num, "ERROR", str(pmids), "", ""))

print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)

for num, status, pmid, source, doi in results:
    icon = "OK" if "FOUND" in status else "XX"
    print(f"[{num:2d}] {icon} {'PMID:'+pmid if pmid else 'NOT FOUND':20s} | {source[:40] if source else doi[:50]}")

found_count = sum(1 for _, s, _, _, _ in results if "FOUND" in s)
not_found = [r for r in results if r[1] == "NOT_FOUND"]
errors = [r for r in results if r[1] == "ERROR"]

print(f"\nFound: {found_count}/36")
print(f"Not found: {len(not_found)}")
print(f"Errors: {len(errors)}")

if not_found:
    print("\n--- NOT FOUND (to be deleted) ---")
    for num, _, _, _, doi in not_found:
        print(f"  [#{num}] DOI: {doi}")
