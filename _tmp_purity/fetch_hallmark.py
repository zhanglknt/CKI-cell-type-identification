# -*- coding: utf-8 -*-
"""Download MSigDB Hallmark gene sets (via Enrichr mirror)."""
import urllib.request, sys

OUT = r"c:/Users/KnightZ/Desktop/细胞受选择/data/tcga/hallmark_2020.gmt"
LOG = r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/hallmark_fetch_log.txt"
URLS = [
    "https://maayanlab.cloud/Enrichr/geneSetLibrary?mode=text&libraryName=MSigDB_Hallmark_2020",
    "https://maayanlab.cloud/Enrichr/geneSetLibrary?mode=text&libraryName=MSigDB_Hallmark_2020&format=gmt",
]
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
log = []
ok = False
for u in URLS:
    try:
        req = urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read().decode("utf-8", errors="replace")
        lines = [l for l in data.splitlines() if l.strip()]
        n_sets = sum(1 for l in lines if len(l.split("\t")) > 20)
        if n_sets >= 45:
            with open(OUT, "w", encoding="utf-8") as f:
                f.write(data)
            log.append(f"OK {u}: {len(lines)} sets, {n_sets} with genes, {len(data)} bytes")
            ok = True
            break
        else:
            log.append(f"BADCONTENT {u}: {len(lines)} lines, {n_sets} sets; head={data[:200]!r}")
    except Exception as e:
        log.append(f"FAIL {u}: {e}")
open(LOG, "w").write("\n".join(log))
sys.exit(0 if ok else 1)
