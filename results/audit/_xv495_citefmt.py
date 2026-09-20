# xv495: inspect citation format in MS body
from pathlib import Path
import re

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
text = (ROOT / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
lines = text.split("\n")
body = "\n".join(lines[:133])

for pat in [r"silent\).{0,40}", r"of 30 Kang.{0,30}", r"Housekeeping genes.{0,60}",
            r"molecular evolution.{0,60}", r"previously.{0,50}"]:
    for m in re.finditer(pat, body):
        print(repr(m.group(0)))
        print("  codepoints:", [hex(ord(ch)) for ch in m.group(0)][:60])
        print("---")
# superscript chars present?
sup = set(ch for ch in body if "⁰" <= ch <= "⁹" or ch in "¹²³")
print("superscript chars found:", sup)
# sample: find a spot known to have citations e.g. 'Ka/Ks'
m = re.search(r"distinguishes nonsynonymous changes.{0,140}", body)
print(repr(m.group(0)) if m else "nf")
