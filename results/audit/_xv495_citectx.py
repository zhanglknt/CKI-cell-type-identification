# xv495: context around citation order violations + post-References superscripts
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

ref_idx = next(i for i, runs in enumerate(paras) if "".join(x for x, _ in runs).strip().lower() == "references")

def para_text(runs):
    return "".join(x for x, _ in runs)

# find paragraphs containing first occurrence of specific superscript numbers
targets = ["56", "16,17", "15", "55", "18"]
seen_groups = set()
for i, runs in enumerate(paras[:ref_idx]):
    buf = ""
    for txt, sup in runs:
        if sup:
            buf += txt
        else:
            if buf.strip():
                seen_groups.add((i, buf))
            buf = ""
    if buf.strip():
        seen_groups.add((i, buf))

want = {"56": None, "16,17": None, "15": None}
for i, g in sorted(seen_groups):
    gs = g.strip()
    if gs in want and want[gs] is None:
        want[gs] = i
for gs, i in want.items():
    if i is not None:
        t = para_text(paras[i])
        pos = t.find(" ")  # just print first 300 chars + around the citation
        print(f"=== first superscript '{gs}' in paragraph {i} ===")
        print(t[:400])
        print()

# superscripts AFTER References (figure legends etc.)
print("=== superscripts after References ===")
post = []
for i, runs in enumerate(paras[ref_idx + 1:], start=ref_idx + 1):
    buf = ""
    for txt, sup in runs:
        if sup:
            buf += txt
        else:
            if buf.strip():
                post.append((i, buf))
            buf = ""
    if buf.strip():
        post.append((i, buf))
print("count:", len(post))
for i, g in post:
    print(i, repr(g))
