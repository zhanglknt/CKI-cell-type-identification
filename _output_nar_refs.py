#!/usr/bin/env python3
"""Output final NAR formatted reference strings for all 16 refs."""
import json

# Load results
with open("_ref_authors_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Reference metadata from manuscript (journal, vol, year, pages, title)
REF_META = {
    "1":  ("Nat. Methods", "16", "2019", "1289\u20131296", "Fast, sensitive and accurate integration of single-cell data with Harmony"),
    "9":  ("Science", "382", "2023", "eadl7046", "Transcriptomic diversity of cell types across the adult human brain"),
    "11": ("Nature", "406", "2000", "747\u2013752", "Molecular portraits of human breast tumours"),
    "12": ("J. Clin. Oncol.", "27", "2009", "1160\u20131167", "Supervised risk predictor of breast cancer based on intrinsic subtypes"),
    "13": ("Science", "351", "2016", "379\u2013384", "Oligodendrocyte precursors migrate along vasculature in the developing nervous system"),
    "14": ("Cancer Discov.", "2", "2012", "401\u2013404", "The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data"),
    "15": ("eLife", "10", "2021", "e66747", "Mapping single-cell atlases throughout Metazoa unravels cell type evolution"),
    "16": ("eLife", "6", "2017", "e27041", "The Human Cell Atlas"),
    "20": ("Dev. Cell", "57", "2022", "1910\u20131927.e10", "The spatiotemporal dynamics of microglia across the human lifespan"),
    "26": ("Cell", "184", "2021", "3573\u20133587", "Integrated analysis of multimodal single-cell data"),
    "27": ("Nat. Biotechnol.", "42", "2024", "293\u2013304", "Dictionary learning for integrative, multimodal and scalable single-cell analysis"),
    "28": ("Nat. Genet.", "45", "2013", "1113\u20131120", "The Cancer Genome Atlas Pan-Cancer analysis project"),
    "29": ("Nucleic Acids Res.", "44", "2016", "e71", "TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data"),
    "32": ("Genome Biol.", "21", "2020", "12", "A benchmark of batch-effect correction methods for single-cell RNA sequencing data"),
    "36": ("Nature", "632", "2024", "603\u2013613", "Single-cell atlas of the human brain vasculature across development, adulthood and disease"),
    "40": ("Cell Rep.", "42", "2023", "113453", "Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors"),
}

print("=== FINAL NAR FORMATTED REFERENCES ===\n")
for ref_num in sorted(results.keys(), key=lambda x: int(x)):
    data = results[ref_num]
    if data is None:
        print(f"Ref {ref_num}: NOT FOUND")
        continue

    authors_str = data["nar_formatted"]
    journal, vol, year, pages, title = REF_META[ref_num]
    nar_ref = f"    '{authors_str} ({year}) {title}. *{journal}*, **{vol}**, {pages}.'"
    print(f"Ref {ref_num}:")
    print(nar_ref)
    print()

# Page number checks
print("=== PAGE NUMBER CHECK ===")
PAGE_CHECKS = {
    "20": ("1910\u20131927.e10", results["20"].get("pages", "")),
    "40": ("113453", results["40"].get("pages", "")),
    "9":  ("eadl7046", results["9"].get("pages", "")),
}
for ref_num, (ms_pages, pm_pages) in PAGE_CHECKS.items():
    match = "OK" if ms_pages == pm_pages else f"MISMATCH (PubMed: {pm_pages})"
    print(f"  Ref {ref_num}: MS={ms_pages} | PubMed={pm_pages} -> {match}")
