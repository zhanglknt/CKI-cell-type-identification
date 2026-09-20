# -*- coding: utf-8 -*-
"""Download estimate R package tarball (contains SI_geneset.gmt)."""
import urllib.request, os, sys

OUT = r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/estimate_1.0.11.tar.gz"
URLS = [
    "https://downloads.sourceforge.net/project/estimateproject/estimate_1.0.11.tar.gz",
    "https://sourceforge.net/projects/estimateproject/files/estimate_1.0.11.tar.gz/download",
    "https://master.dl.sourceforge.net/project/estimateproject/estimate_1.0.11.tar.gz",
    "https://phoenixnap.dl.sourceforge.net/project/estimateproject/estimate_1.0.11.tar.gz",
]
LOG = []
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ok = False
for u in URLS:
    try:
        req = urllib.request.Request(u, headers=hdr)
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if data[:2] == b"\x1f\x8b":  # gzip magic
            with open(OUT, "wb") as f:
                f.write(data)
            LOG.append(f"OK {u} -> {len(data)} bytes (gzip)")
            ok = True
            break
        else:
            LOG.append(f"NOTGZ {u} -> {len(data)} bytes first={data[:16]!r}")
    except Exception as e:
        LOG.append(f"FAIL {u}: {e}")

with open(r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/download_log2.txt", "w") as f:
    f.write("\n".join(LOG))
sys.exit(0 if ok else 1)
