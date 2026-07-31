#!/usr/bin/env python3
"""Fetch full author lists for the 3 corrected PMIDs + format all 16 refs in NAR style."""
import json, time, urllib.request, urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esummary(pmid):
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "retmode": "json"})
    url = f"{EUTILS}/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read()).get("result", {}).get(pmid, {})

def format_nar_name(pubmed_name):
    """Convert 'Lastname FM' to 'Lastname,F.M.' for NAR format."""
    # Handle suffixes like "3rd", "Jr"
    parts = pubmed_name.rsplit(" ", 1)
    if len(parts) == 2:
        lastname, initials = parts
        # Add periods between initials
        formatted_initials = ".".join(list(initials)) + "."
        # Handle suffixes
        if formatted_initials.endswith(".."):
            formatted_initials = formatted_initials[:-1]
        return f"{lastname},{formatted_initials}"
    else:
        # Single name (consortium)
        return pubmed_name + ","

def format_nar_authors(authors, skip_consortium=False):
    """Format author list per NAR rules: <=10 all, >10 first 10 + et al."""
    names = []
    for a in authors:
        name = a.get("name", "")
        if not name:
            continue
        if skip_consortium and ("Network" in name or "Consortium" in name or "Program" in name):
            continue
        names.append(format_nar_name(name))

    n = len(names)
    if n <= 10:
        if n == 1:
            return names[0]
        elif n == 2:
            return f"{names[0]} and {names[1]}"
        else:
            return ", ".join(names[:-1]) + " and " + names[-1]
    else:
        return ", ".join(names[:10]) + " et al."

# Correct PMIDs for the 3 fixed refs
FIXED_PMIDS = {
    9: "37824663",   # Siletti et al. 2023 Science
    16: "29206104",  # Regev et al. 2017 eLife - Human Cell Atlas
}

# Also re-fetch ref 32 with correct PMID
EXTRA_PMIDS = {
    32: "31948481",  # Tran et al. 2020 Genome Biol
}

# Load previous results
with open("_ref_authors_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Fetch fixed refs
for ref_num, pmid in {**FIXED_PMIDS, **EXTRA_PMIDS}.items():
    print(f"\n--- Ref {ref_num} (PMID {pmid}) ---")
    time.sleep(0.5)
    s = esummary(pmid)
    title = s.get("title", "N/A")
    source = s.get("source", "N/A")
    pubdate = s.get("pubdate", "N/A")
    volume = s.get("volume", "N/A")
    pages = s.get("pages", "N/A")
    authors = s.get("authors", [])

    print(f"  Title: {title}")
    print(f"  {source}, Vol:{volume}, Pages:{pages}, Date:{pubdate}")
    for i, a in enumerate(authors):
        print(f"    {i+1}. {a.get('name', 'N/A')}")

    # Special handling: ref 28 (Weinstein) - skip consortium name
    skip_cons = (ref_num == 28)

    formatted = format_nar_authors(authors, skip_consortium=skip_cons)
    print(f"  NAR formatted: {formatted}")

    results[ref_num] = {
        "pmid": pmid,
        "title": title,
        "source": source,
        "pubdate": pubdate,
        "volume": volume,
        "pages": pages,
        "n_authors": len(authors),
        "all_authors": [a.get("name", "") for a in authors],
        "nar_formatted": formatted,
    }

# Now format ALL 16 refs and print final NAR strings
print("\n\n=== FINAL NAR FORMATTED REFERENCES ===\n")

# Existing reference metadata (from the manuscript script)
# (journal_italic, volume_bold, year, pages)
# We use the existing manuscript metadata, only replacing the author portion
REF_META = {
    1:  ("Nat. Methods", "16", "2019", "1289\u20131296"),
    9:  ("Science", "382", "2023", "eadl7046"),
    11: ("Nature", "406", "2000", "747\u2013752"),
    12: ("J. Clin. Oncol.", "27", "2009", "1160\u20131167"),
    13: ("Science", "351", "2016", "379\u2013384"),
    14: ("Cancer Discov.", "2", "2012", "401\u2013404"),
    15: ("eLife", "10", "2021", "e66747"),
    16: ("eLife", "6", "2017", "e27041"),
    20: ("Dev. Cell", "57", "2022", "1910\u20131927.e10"),
    26: ("Cell", "184", "2021", "3573\u20133587"),
    27: ("Nat. Biotechnol.", "42", "2024", "293\u2013304"),
    28: ("Nat. Genet.", "45", "2013", "1113\u20131120"),
    29: ("Nucleic Acids Res.", "44", "2016", "e71"),
    32: ("Genome Biol.", "21", "2020", "12"),
    36: ("Nature", "632", "2024", "603\u2013613"),
    40: ("Cell Rep.", "42", "2023", "113453"),
}

# Also get the titles from existing data or use known titles
REF_TITLES = {
    1:  "Fast, sensitive and accurate integration of single-cell data with Harmony",
    9:  "Transcriptomic diversity of cell types across the adult human brain",
    11: "Molecular portraits of human breast tumours",
    12: "Supervised risk predictor of breast cancer based on intrinsic subtypes",
    13: "Oligodendrocyte precursors migrate along vasculature in the developing nervous system",
    14: "The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data",
    15: "Mapping single-cell atlases throughout Metazoa unravels cell type evolution",
    16: "The Human Cell Atlas",
    20: "The spatiotemporal dynamics of microglia across the human lifespan",
    26: "Integrated analysis of multimodal single-cell data",
    27: "Dictionary learning for integrative, multimodal and scalable single-cell analysis",
    28: "The Cancer Genome Atlas Pan-Cancer analysis project",
    29: "TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data",
    32: "A benchmark of batch-effect correction methods for single-cell RNA sequencing data",
    36: "Single-cell atlas of the human brain vasculature across development, adulthood and disease",
    40: "Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors",
}

for ref_num in sorted(results.keys()):
    data = results[ref_num]
    if data is None:
        print(f"Ref {ref_num}: NOT FOUND")
        continue

    authors_str = data["nar_formatted"]
    journal, vol, year, pages = REF_META[ref_num]
    title = REF_TITLES[ref_num]

    # NAR format: Author,A.B., Author,C.D. and Author,E.F. (Year) Title. *Journal.*, **Vol**, Pages.
    nar_ref = f"{authors_str} ({year}) {title}. *{journal}*, **{vol}**, {pages}."

    print(f"Ref {ref_num}: {nar_ref}")

# Save updated results
with open("_ref_authors_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Also check page number discrepancies
print("\n\n=== PAGE NUMBER CHECK ===")
PAGE_CHECKS = {
    20: ("Dev. Cell", "57", "1910\u20131927.e10", results[20].get("pages", "")),
    40: ("Cell Rep.", "42", "113453", results[40].get("pages", "")),
    9:  ("Science", "382", "eadl7046", results[9].get("pages", "")),
}
for ref_num, (journal, vol, ms_pages, pm_pages) in PAGE_CHECKS.items():
    match = "OK" if ms_pages == pm_pages else f"MISMATCH (PubMed: {pm_pages})"
    print(f"  Ref {ref_num}: MS={ms_pages} | PubMed={pm_pages} -> {match}")
