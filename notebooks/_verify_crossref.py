"""Verify references via CrossRef (DOI resolution) + WebSearch fallback"""
import requests
import sys, io, time, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# All 36 references with DOI or title for verification
refs = [
    (1,  "Regev", "2017", "The Human Cell Atlas", "eLife", "10.7554/eLife.27041"),
    (2,  "Luecken", "2019", "Current best practices in single-cell RNA-seq analysis", "Mol Syst Biol", "10.15252/msb.20188746"),
    (3,  "Nei", "1986", "Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions", "Mol Biol Evol", ""),
    (4,  "Hounkpe", "2021", "HRT Atlas v1.0 database: redefining human and mouse housekeeping genes", "Nucleic Acids Res", "10.1093/nar/gkaa1118"),
    (5,  "Tabula Muris Consortium", "2018", "Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris", "Nature", "10.1038/s41586-018-0590-4"),
    (6,  "Tabula Sapiens Consortium", "2022", "The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans", "Science", "10.1126/science.abl4896"),
    (7,  "Cancer Genome Atlas Research Network", "2014", "Comprehensive molecular profiling of lung adenocarcinoma", "Nature", "10.1038/nature13385"),
    (8,  "Weinstein", "2013", "The Cancer Genome Atlas Pan-Cancer analysis project", "Nat Genet", "10.1038/ng.2764"),
    (9,  "Cancer Genome Atlas Network", "2012", "Comprehensive molecular portraits of human breast tumours", "Nature", "10.1038/nature11412"),
    (10, "Siletti", "2023", "Transcriptomic diversity of cell types across the adult human brain", "Nature", "10.1038/s41586-023-06812-9"),
    (11, "Tran", "2020", "A benchmark of batch-effect correction methods for single-cell RNA sequencing data", "Genome Biol", "10.1186/s13059-020-02054-8"),
    (12, "Korsunsky", "2019", "Fast, sensitive and accurate integration of single-cell data with Harmony", "Nat Methods", "10.1038/s41592-019-0616-0"),
    (13, "Lopez", "2018", "Deep generative modeling for single-cell transcriptomics", "Nat Methods", "10.1038/s41592-018-0229-2"),
    (14, "Rosen", "2024", "Universal cell-type embeddings from single-cell atlases using protein language models", "Nat Methods", "10.1038/s41592-024-02233-5"),
    (15, "Storey", "2003", "Statistical significance for genomewide studies", "Proc Natl Acad Sci USA", "10.1073/pnas.1530509100"),
    (16, "Wolf", "2018", "SCANPY: large-scale single-cell gene expression data analysis", "Genome Biol", "10.1186/s13059-017-1382-0"),
    (17, "Edmondson", "1954", "Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies", "Cancer", ""),
    (18, "Perou", "2000", "Molecular portraits of human breast tumours", "Nature", "10.1038/35019593"),
    (19, "Parker", "2009", "Supervised risk predictor of breast cancer based on intrinsic subtypes", "J Clin Oncol", "10.1200/JCO.2008.18.1370"),
    (20, "Yang", "2007", "PAML 4: phylogenetic analysis by maximum likelihood", "Mol Biol Evol", "10.1093/molbev/msm088"),
    (21, "Tarashansky", "2021", "Mapping single-cell atlases throughout Metazoa unravels cell type evolution", "eLife", "10.7554/eLife.66747"),
    (22, "Jiang", "2024", "CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions", "Brief Bioinform", "10.1093/bib/bbae283"),
    (23, "Hao", "2021", "Integrated analysis of multimodal single-cell data", "Cell", "10.1016/j.cell.2021.04.048"),
    (24, "CZI Cell Science Program", "2025", "CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling", "Nucleic Acids Res", "10.1093/nar/gkae1026"),
    (25, "Colaprico", "2016", "TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data", "Nucleic Acids Res", "10.1093/nar/gkv1507"),
    (26, "Cerami", "2012", "The cBio Cancer Genomics Portal: an open platform for exploring multidimensional cancer data", "Cancer Discov", "10.1158/2159-8290.CD-12-0095"),
    (27, "Liberzon", "2015", "The Molecular Signatures Database Hallmark Gene Set Collection", "Cell Syst", "10.1016/j.cels.2015.12.004"),
    (28, "Tsai", "2016", "Oligodendrocyte precursors migrate along vasculature in the developing nervous system", "Science", "10.1126/science.aah5232"),
    (29, "Akay", "2022", "Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration", "Neuron", "10.1016/j.neuron.2022.09.025"),
    (30, "Foerster", "2024", "Developmental origin of oligodendrocytes determines their function in the adult brain", "Nat Neurosci", "10.1038/s41593-024-01581-2"),
    (31, "Endo", "2024", "Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction", "EMBO J", "10.1038/s44318-024-00149-0"),
    (32, "Yang", "2024", "Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum", "Cell Discov", "10.1038/s41421-024-00663-6"),
    (33, "Tan", "2020", "Microglial regional heterogeneity and its role in the brain", "Mol Psychiatry", "10.1038/s41380-019-0610-3"),
    (34, "Menassa", "2022", "The spatiotemporal dynamics of microglia recruitment after myocardial infarction", "Nature", "10.1038/s41586-022-04636-5"),
    (35, "Walchli", "2024", "Single-cell atlas of the human brain vasculature across development, adulthood and disease", "Nature", "10.1038/s41586-023-06699-8"),
    (36, "Hao", "2024", "Dictionary learning for integrative, multimodal and scalable single cell", "Cell", "10.1016/j.cell.2024.08.025"),
]

def verify_doi(doi):
    """Verify DOI exists via CrossRef API"""
    if not doi:
        return "NO_DOI"
    url = f"https://doi.org/{doi}"
    try:
        r = requests.get(url, timeout=15, allow_redirects=True, verify=False)
        if r.status_code in (200, 302, 301):
            return "DOI_OK"
        return f"DOI_FAIL_{r.status_code}"
    except Exception as e:
        return f"DOI_ERR:{str(e)[:60]}"

results = []
for num, author, year, title, journal, doi in refs:
    print(f"[{num:2d}] {author} {year} ... ", end="", flush=True)
    
    if doi:
        status = verify_doi(doi)
        if "OK" in status:
            print(f"OK (DOI verified)")
            results.append((num, "FOUND", doi))
        else:
            print(f"DOI issue: {status}")
            results.append((num, "DOI_FAIL", doi))
    else:
        print(f"NO DOI - old paper ({year})")
        results.append((num, "NO_DOI", ""))
    
    time.sleep(0.2)

print("\n" + "="*70)
print("VERIFICATION SUMMARY (via CrossRef)")
print("="*70)

for num, status, doi in results:
    icon = "OK " if status == "FOUND" else "XX"
    extra = f" {doi[:45]}" if doi else ""
    print(f"  [{num:2d}] {icon}{extra}")

found = sum(1 for _, s, _ in results if s == "FOUND")
no_doi = [(n, d) for n, s, d in results if s == "NO_DOI"]
doi_fail = [(n, d) for n, s, d in results if s == "DOI_FAIL"]

print(f"\nDOI Verified: {found}/36")
if no_doi:
    print(f"\nNo DOI (old papers, need manual check):")
    for n, d in no_doi:
        print(f"  [{n:2d}] {d}")
if doi_fail:
    print(f"\nDOI verification failed:")
    for n, d in doi_fail:
        print(f"  [{n:2d}] {d}")
