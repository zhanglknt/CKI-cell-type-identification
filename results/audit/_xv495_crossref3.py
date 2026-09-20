# xv495 pass 3: DOI-direct CrossRef lookups for unresolved refs
import json, time, urllib.request

PY_UA = {"User-Agent": "xv495-refcheck/1.0 (mailto:audit@example.org)"}

CHECKS = {
    1:  "10.7554/eLife.27041",           # Regev et al., The Human Cell Atlas, eLife 6:e27041 (2017)
    9:  "10.1126/science.abl4896",       # Tabula Sapiens, Science 376:eabl4896 (2022)
    16: "10.1038/35021093",              # Perou et al., Nature 406:747-752 (2000)
    20: "10.1242/dev.201805",            # Jones et al., Development 150:dev201805 (2023)
    30: "10.1038/s44318-024-00218-x",    # Zhang et al., EMBO J 43 (2024) - check page
    35: "10.1016/j.cell.2008.09.050",    # Raj & van Oudenaarden, Cell 135:216-226 (2008) - check exact title
    37: "10.1093/bib/bbae283",           # Jiang et al., Brief Bioinform 25:bbae283 (2024)
    40: "10.1038/s41586-021-03465-8",    # Bakken et al., Nature 598:111-119 (2021)
}

out = {}
for refno, doi in CHECKS.items():
    url = "https://api.crossref.org/works/" + urllib.request.quote(doi)
    try:
        req = urllib.request.Request(url, headers=PY_UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.loads(r.read().decode("utf-8"))["message"]
        auth = m.get("author", [])
        fam = auth[0].get("family", "") if auth else ""
        rec = {
            "doi": m.get("DOI"),
            "title": (m.get("title") or [""])[0],
            "container": (m.get("container-title") or [""])[0],
            "short_container": (m.get("short-container-title") or [""])[0],
            "year": (m.get("issued", {}).get("date-parts", [[None]])[0][0]),
            "volume": m.get("volume", ""),
            "issue": m.get("issue", ""),
            "page": m.get("page", ""),
            "article_number": m.get("article-number", ""),
            "first_family": fam,
            "n_authors": len(auth),
            "publisher": m.get("publisher", ""),
        }
        out[refno] = rec
        print(f"[{refno}] OK {fam}/{rec['year']}/{rec['container']}/vol={rec['volume']}/issue={rec['issue']}/page={rec['page']}/art={rec['article_number']}/n={len(auth)}")
        print(f"     title: {rec['title'][:110]}")
    except Exception as e:
        out[refno] = {"error": str(e)}
        print(f"[{refno}] ERROR {e}")
    time.sleep(0.8)

with open(r"C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_xv495_crossref3.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved")
