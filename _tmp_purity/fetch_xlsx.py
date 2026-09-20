# -*- coding: utf-8 -*-
"""Download ESTIMATE official supplementary gene lists (ncomms3612-s2.xlsx)."""
import urllib.request, os, sys

OUT = r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/ncomms3612-s2.xlsx"
URLS = [
    "https://pmc.ncbi.nlm.nih.gov/articles/instance/3826632/bin/ncomms3612-s2.xlsx",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/instance/3826632/bin/ncomms3612-s2.xlsx",
]
LOG = []
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ok = False
for u in URLS:
    try:
        req = urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(OUT, "wb") as f:
            f.write(data)
        LOG.append(f"OK {u} -> {len(data)} bytes")
        ok = True
        break
    except Exception as e:
        LOG.append(f"FAIL {u}: {e}")

with open(r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/download_log.txt", "w") as f:
    f.write("\n".join(LOG))
sys.exit(0 if ok else 1)
