# -*- coding: utf-8 -*-
"""解包 GSE96583_RAW.tar 中 batch1 三个 lane 到 data/kang_ifnb/_raw/"""
import tarfile, os, sys

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
TAR = os.path.join(ROOT, "data/kang_ifnb/GSE96583_RAW.tar")
OUT = os.path.join(ROOT, "data/kang_ifnb/_raw")
LOG = os.path.join(ROOT, "results", "audit", "_nc49_unpack.log")

os.makedirs(OUT, exist_ok=True)
lines = []
with tarfile.open(TAR) as t:
    for m in t.getmembers():
        if m.name.startswith(("GSM2560245", "GSM2560246", "GSM2560247")):
            t.extract(m, OUT)
            lines.append(f"extracted {m.name} ({m.size} bytes)")
lines.append("listing: " + repr(sorted(os.listdir(OUT))))
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
