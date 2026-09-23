#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51 probe round 2: exact v51 wording for remaining assertion rewrites."""
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
ms = (BASE / "results" / "CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
sn = (BASE / "results" / "CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8")
gd = (BASE / "results" / "CKI_Reproducibility_Guide_NC_fulltext.txt").read_text(encoding="utf-8")

def ctx_all(text, key, w=150, label=""):
    start = 0
    n = 0
    while True:
        i = text.find(key, start)
        if i < 0:
            break
        n += 1
        print(f"  [{label}#{n}] ...{text[max(0,i-w):i+len(key)+w]}...".replace("\n", " "))
        start = i + 1
    if n == 0:
        print(f"  [{label}] ABSENT: {key!r}")

print("== ms '3.12' ==");            ctx_all(ms, "3.12", 100, "ms")
print("== ms 'bulk' ==");             ctx_all(ms, "bulk", 120, "ms")
print("== ms 'Table 1' ==");          ctx_all(ms, "Table 1", 90, "ms")
print("== ms 'calibrated' ==");       ctx_all(ms, "calibrated", 120, "ms")
print("== ms '\u22121.3% pooled' =="); ctx_all(ms, "\u22121.3% pooled", 200, "ms")
print("== ms '6.10' ==");             ctx_all(ms, "6.10", 150, "ms")
print("== ms '3.68' ==");             ctx_all(ms, "3.68", 180, "ms")
print("== ms 'attenuat' ==");         ctx_all(ms, "attenuat", 200, "ms")
print("== ms 'span-matched' ==");     ctx_all(ms, "span-matched", 180, "ms")
print("== ms 'composition' ==");      ctx_all(ms, "composition", 130, "ms")
print("== ms 'substantive rather than nominal' =="); ctx_all(ms, "substantive rather than nominal", 60, "ms")
print("== ms 'P = 0.47' / Cox ==");   ctx_all(ms, "Cox", 150, "ms")
print("== ms '0.48' ==");             ctx_all(ms, "0.48", 120, "ms")
print("== gd 'B = 1,000; raised' =="); ctx_all(gd, "B = 1,000; raised", 60, "gd")
print("== gd 'mouse Tabula Muris pilot' =="); ctx_all(gd, "mouse Tabula Muris pilot", 60, "gd")
print("== gd 'Aggregation-order same-data' =="); ctx_all(gd, "Aggregation-order same-data", 60, "gd")
print("== gd 'control-category median baseline' =="); ctx_all(gd, "control-category median baseline", 60, "gd")
print("== sn 'attenuates by' ==");    ctx_all(sn, "attenuates by", 200, "sn")
print("== sn 'median |\u0394z|' ==");  ctx_all(sn, "median |\u0394z|", 160, "sn")
print("== ms '1.74' ==");             ctx_all(ms, "1.74", 170, "ms")
print("== ms 'Section 3.13' ==");     ctx_all(ms, "Section 3.13", 110, "ms")
