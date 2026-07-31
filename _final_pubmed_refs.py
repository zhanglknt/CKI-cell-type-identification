#!/usr/bin/env python3
"""Final script: fetch all 16 references with correct PMIDs, format in NAR style."""
import json, re, time, urllib.request, urllib.parse

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# All 16 refs with verified PMIDs
REFS = {
    1:  {"pmid": "31740819", "journal": "Nat. Methods", "vol": "16", "year": "2019",
         "pages": "1289\u20131296",
         "title": "Fast, sensitive and accurate integration of single-cell data with Harmony"},
    9:  {"pmid": "37824663", "journal": "Science", "vol": "382", "year": "2023",
         "pages": "eadl7046",
         "title": "Transcriptomic diversity of cell types across the adult human brain"},
    11: {"pmid": "10963602", "journal": "Nature", "vol": "406", "year": "2000",
         "pages": "747\u2013752",
         "title": "Molecular portraits of human breast tumours"},
    12: {"pmid": "19204204", "journal": "J. Clin. Oncol.", "vol": "27", "year": "2009",
         "pages": "1160\u20131167",
         "title": "Supervised risk predictor of breast cancer based on intrinsic subtypes"},
    13: {"pmid": "26798014", "journal": "Science", "vol": "351", "year": "2016",
         "pages": "379\u2013384",
         "title": "Oligodendrocyte precursors migrate along vasculature in the developing nervous system"},
    14: {"pmid": "22588877", "journal": "Cancer Discov.", "vol": "2", "year": "2012",
         "pages": "401\u2013404",
         "title": "The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data"},
    15: {"pmid": "33944782", "journal": "eLife", "vol": "10", "year": "2021",
         "pages": "e66747",
         "title": "Mapping single-cell atlases throughout Metazoa unravels cell type evolution"},
    16: {"pmid": "29206104", "journal": "eLife", "vol": "6", "year": "2017",
         "pages": "e27041",
         "title": "The Human Cell Atlas"},
    20: {"pmid": "35977545", "journal": "Dev. Cell", "vol": "57", "year": "2022",
         "pages": "1910\u20131927.e10",
         "title": "The spatiotemporal dynamics of microglia across the human lifespan"},
    26: {"pmid": "34062119", "journal": "Cell", "vol": "184", "year": "2021",
         "pages": "3573\u20133587",
         "title": "Integrated analysis of multimodal single-cell data"},
    27: {"pmid": "37231261", "journal": "Nat. Biotechnol.", "vol": "42", "year": "2024",
         "pages": "293\u2013304",
         "title": "Dictionary learning for integrative, multimodal and scalable single-cell analysis"},
    28: {"pmid": "24071849", "journal": "Nat. Genet.", "vol": "45", "year": "2013",
         "pages": "1113\u20131120",
         "title": "The Cancer Genome Atlas Pan-Cancer analysis project",
         "skip_consortium": True},
    29: {"pmid": "26704973", "journal": "Nucleic Acids Res.", "vol": "44", "year": "2016",
         "pages": "e71",
         "title": "TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data"},
    32: {"pmid": "31948481", "journal": "Genome Biol.", "vol": "21", "year": "2020",
         "pages": "12",
         "title": "A benchmark of batch-effect correction methods for single-cell RNA sequencing data"},
    36: {"pmid": "38987604", "journal": "Nature", "vol": "632", "year": "2024",
         "pages": "603\u2013613",
         "title": "Single-cell atlas of the human brain vasculature across development, adulthood and disease"},
    40: {"pmid": "37099424", "journal": "Cell Rep.", "vol": "42", "year": "2023",
         "pages": "113453",
         "title": "Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors"},
}


def esummary(pmid):
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "retmode": "json"})
    url = f"{EUTILS}/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read()).get("result", {}).get(pmid, {})


def parse_nar_name(pubmed_name):
    """Convert PubMed 'Lastname FM' to NAR 'Lastname,F.M.'

    Handles:
    - Multi-word last names: 'Mossi Albiach A' -> 'Mossi Albiach,A.'
    - Suffixes: 'Mauck WM 3rd' -> 'Mauck,W.M. 3rd'
    - Lowercase particles: 'van de Rijn M' -> 'van de Rijn,M.'
    - Consortium names: 'Cancer Genome Atlas Research Network' -> as-is
    """
    # Check for consortium/organization names (no initials at end)
    # These typically don't have uppercase initials at the very end
    m = re.match(r'^(.+?) ([A-Z]+)(?: (3rd|Jr|Sr|II|III|IV))?$', pubmed_name)
    if m:
        lastname = m.group(1)
        initials = m.group(2)
        suffix = m.group(3)
        # Format initials with periods
        formatted_init = ".".join(list(initials)) + "."
        result = f"{lastname},{formatted_init}"
        if suffix:
            result += f" {suffix}"
        return result
    else:
        # Consortium or single name - return as-is with trailing comma
        return pubmed_name + ","


def format_nar_authors(authors, skip_consortium=False):
    """Format author list per NAR rules: <=10 all, >10 first 10 + et al."""
    names = []
    for a in authors:
        name = a.get("name", "")
        if not name:
            continue
        if skip_consortium and any(x in name for x in ["Network", "Consortium", "Program", "Participants"]):
            continue
        names.append(parse_nar_name(name))

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


def main():
    final_refs = {}

    for ref_num in sorted(REFS.keys()):
        info = REFS[ref_num]
        pmid = info["pmid"]
        skip_cons = info.get("skip_consortium", False)

        print(f"\n--- Ref {ref_num} (PMID {pmid}) ---")
        time.sleep(0.4)
        s = esummary(pmid)
        authors = s.get("authors", [])

        # Verify title match
        pm_title = s.get("title", "").rstrip(".")
        ms_title = info["title"].rstrip(".")
        if pm_title.lower() != ms_title.lower():
            print(f"  WARNING: Title mismatch!")
            print(f"    PubMed: {pm_title[:80]}")
            print(f"    MS:     {ms_title[:80]}")
        else:
            print(f"  Title OK: {ms_title[:70]}")

        # Check page numbers
        pm_pages = s.get("pages", "")
        ms_pages = info["pages"]
        if pm_pages and ms_pages and pm_pages != ms_pages:
            print(f"  PAGE MISMATCH: MS={ms_pages} | PubMed={pm_pages}")

        # Format authors
        nar_authors = format_nar_authors(authors, skip_consortium=skip_cons)
        print(f"  Authors ({len(authors)}): {nar_authors[:80]}...")

        # Build full NAR reference string
        nar_ref = f"'{nar_authors} ({info['year']}) {info['title']}. *{info['journal']}*, **{info['vol']}**, {info['pages']}.'"
        print(f"  NAR: {nar_ref[:100]}...")

        final_refs[ref_num] = nar_ref

    # Print all final reference strings
    print("\n\n=== FINAL REFERENCE STRINGS (for generate_manuscript_nar.py) ===\n")
    for ref_num in sorted(final_refs.keys()):
        print(f"  # Ref {ref_num}:")
        print(f"  {final_refs[ref_num]}")
        print()

    # Save for use in update script
    with open("_final_refs.json", "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in final_refs.items()}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
