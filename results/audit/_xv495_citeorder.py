# xv495: extract superscript citation runs from docx XML, verify order
from pathlib import Path
import re, zipfile
from xml.etree import ElementTree as ET

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
DOCX = ROOT / "results" / "CKI_Manuscript_NC.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

with zipfile.ZipFile(DOCX) as z:
    xml = z.read("word/document.xml")
root = ET.fromstring(xml)
body = root.find(f"{W}body")

paras = []
for p in body.iter(f"{W}p"):
    runs = []
    for r in p.iter(f"{W}r"):
        sup = False
        rpr = r.find(f"{W}rPr")
        if rpr is not None:
            va = rpr.find(f"{W}vertAlign")
            if va is not None and va.get(f"{W}val") == "superscript":
                sup = True
        txt = "".join(t.text or "" for t in r.iter(f"{W}t"))
        runs.append((txt, sup))
    paras.append(runs)

# locate References heading paragraph
ref_idx = None
for i, runs in enumerate(paras):
    t = "".join(x for x, _ in runs).strip().lower()
    if t == "references":
        ref_idx = i
        break
print("References paragraph index:", ref_idx, "of", len(paras))

# collect superscript groups before References; merge adjacent superscript runs
groups = []
for runs in paras[:ref_idx]:
    buf = ""
    for txt, sup in runs:
        if sup:
            buf += txt
        else:
            if buf.strip():
                groups.append(buf)
            buf = ""
    if buf.strip():
        groups.append(buf)

print("superscript groups found:", len(groups))
for g in groups:
    print(repr(g))

# parse groups into numbers
seq = []
for g in groups:
    s = g.strip()
    if not re.fullmatch(r"[\d,\s\u2013\-]+", s):
        print("NON-CITATION superscript:", repr(g))
        continue
    for piece in s.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "\u2013" in piece or "-" in piece:
            a, b = re.split(r"[\u2013\-]", piece)
            seq.extend(range(int(a), int(b) + 1))
        else:
            seq.append(int(piece))
print("total citation numbers:", len(seq))
first_seen, seen = [], set()
for c in seq:
    if c not in seen:
        seen.add(c)
        first_seen.append(c)
print("unique cited:", len(seen))
print("first-seen:", first_seen)
mono = all(first_seen[i] < first_seen[i + 1] for i in range(len(first_seen) - 1))
print("monotone:", mono)
if not mono:
    for i in range(len(first_seen) - 1):
        if first_seen[i] >= first_seen[i + 1]:
            print("  break at pos", i + 1, ":", first_seen[i], "->", first_seen[i + 1])
print("orphans:", sorted(set(range(1, 57)) - seen))
print(">56 cited:", sorted(c for c in seen if c > 56))
