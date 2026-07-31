#!/usr/bin/env python3
"""Fix 3 wrong PubMed queries and check page numbers."""
import json, time, urllib.request, urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esearch(query, retmax=5):
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"})
    url = f"{EUTILS}/esearch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read()).get("esearchresult", {}).get("idlist", [])

def esummary(pmid):
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "retmode": "json"})
    url = f"{EUTILS}/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read()).get("result", {}).get(pmid, {})

# Fix queries with more specific terms
FIXES = [
    (9,  "Siletti K Hodge R transcriptomic diversity cell types adult human brain Science 2023"),
    (16, "Regev Teichmann Lender Human Cell Atlas eLife 2017"),
    (32, "Tran Ang Chevrier benchmark batch-effect correction single-cell RNA sequencing Genome Biology 2020"),
]

for ref_num, query in FIXES:
    print(f"\n--- Ref {ref_num}: {query[:70]}... ---")
    time.sleep(0.5)
    pmids = esearch(query)
    print(f"  PMIDs: {pmids}")
    for pmid in pmids[:3]:
        time.sleep(0.5)
        s = esummary(pmid)
        title = s.get("title", "N/A")
        source = s.get("source", "N/A")
        pubdate = s.get("pubdate", "N/A")
        volume = s.get("volume", "N/A")
        pages = s.get("pages", "N/A")
        authors = s.get("authors", [])
        author_names = [a.get("name", "") for a in authors]
        print(f"  PMID {pmid}: {title[:80]}")
        print(f"    {source}, Vol:{volume}, Pages:{pages}, Date:{pubdate}")
        print(f"    Authors ({len(authors)}): {author_names[:5]}...")
