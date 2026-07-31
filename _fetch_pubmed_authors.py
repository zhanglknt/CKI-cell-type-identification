#!/usr/bin/env python3
"""Query NCBI E-utilities to get full author lists for 16 references.

NAR rule: <=10 authors -> list all; >10 authors -> first 10 + et al.
"""

import json
import time
import urllib.request
import urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# (ref_number, search_query)
# Using title + first author for precise matching
QUERIES = [
    (1,  "Korsunsky Harmony single-cell data 2019"),
    (9,  "Siletti Transcriptomic diversity cell types adult human brain 2023"),
    (11, "Perou Molecular portraits human breast tumours 2000"),
    (12, "Parker Supervised risk predictor breast cancer intrinsic subtypes 2009"),
    (13, "Tsai Oligodendrocyte precursors migrate vasculature developing nervous system 2016"),
    (14, "Cerami cBio cancer genomics portal open platform 2012"),
    (15, "Tarashansky Mapping single-cell atlases Metazoa cell type evolution 2021"),
    (16, "Regev Human Cell Atlas 2017"),
    (20, "Menassa spatiotemporal dynamics microglia human lifespan 2022"),
    (26, "Hao Integrated analysis multimodal single-cell data 2021"),
    (27, "Hao Dictionary learning integrative multimodal scalable single-cell 2024"),
    (28, "Weinstein Cancer Genome Atlas Pan-Cancer analysis project 2013"),
    (29, "Colaprico TCGAbiolinks R Bioconductor package integrative analysis TCGA 2016"),
    (32, "Tran benchmark batch-effect correction methods single-cell RNA sequencing 2020"),
    (36, "Walchli Single-cell atlas human brain vasculature development adulthood disease 2024"),
    (40, "Barry-Carroll Microglia colonize developing brain clonal expansion proliferative progenitors 2023"),
]


def esearch(query, retmax=5):
    """Search PubMed, return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
    })
    url = f"{EUTILS}/esearch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmid):
    """Get article summary including full author list."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": pmid,
        "retmode": "json",
    })
    url = f"{EUTILS}/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("result", {}).get(pmid, {})


def format_nar_authors(authors):
    """Format author list per NAR rules: <=10 all, >10 first 10 + et al."""
    # Extract names from author dicts
    names = []
    for a in authors:
        name = a.get("name", "")
        if name:
            names.append(name)

    n = len(names)
    if n <= 10:
        if n == 1:
            return names[0]
        elif n == 2:
            return f"{names[0]} and {names[1]}"
        else:
            return ", ".join(names[:-1]) + " and " + names[-1]
    else:
        # First 10 + et al.
        return ", ".join(names[:10]) + " et al."


def main():
    results = {}

    for ref_num, query in QUERIES:
        print(f"\n--- Ref {ref_num}: {query[:60]}... ---")
        time.sleep(0.5)  # Rate limit: 3 req/sec without API key
        pmids = esearch(query)
        print(f"  Found {len(pmids)} PMIDs: {pmids}")

        if not pmids:
            print(f"  WARNING: No PMID found for ref {ref_num}")
            results[ref_num] = None
            continue

        # Use first PMID (most relevant)
        pmid = pmids[0]
        time.sleep(0.5)
        summary = esummary(pmid)

        title = summary.get("title", "N/A")
        source = summary.get("source", "N/A")
        pubdate = summary.get("pubdate", "N/A")
        volume = summary.get("volume", "N/A")
        pages = summary.get("pages", "N/A")
        authors = summary.get("authors", [])

        print(f"  Title: {title[:80]}")
        print(f"  Source: {source}, Vol: {volume}, Pages: {pages}, Date: {pubdate}")
        print(f"  Authors ({len(authors)}):")
        for i, a in enumerate(authors):
            print(f"    {i+1}. {a.get('name', 'N/A')}")

        formatted = format_nar_authors(authors)
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

    # Save results
    with open("_ref_authors_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n\n=== SUMMARY ===")
    for ref_num, data in results.items():
        if data:
            print(f"Ref {ref_num}: {data['n_authors']} authors -> {data['nar_formatted'][:80]}...")
        else:
            print(f"Ref {ref_num}: NOT FOUND")

    print("\nResults saved to _ref_authors_results.json")


if __name__ == "__main__":
    main()
