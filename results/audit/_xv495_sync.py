# xv495: docx vs txt sync check (mtimes, methods para, refs list)
from pathlib import Path
import datetime, re, zipfile
from xml.etree import ElementTree as ET

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

for f in ["results/CKI_Manuscript_NC.docx", "results/CKI_Manuscript_NC_fulltext.txt",
          "results/CKI_Supplementary_NC.docx", "results/CKI_Supplementary_NC_fulltext.txt"]:
    p = ROOT / f
    if p.exists():
        print(f, datetime.datetime.fromtimestamp(p.stat().st_mtime), p.stat().st_size)

with zipfile.ZipFile(ROOT / "results/CKI_Manuscript_NC.docx") as z:
    xml = z.read("word/document.xml")
root = ET.fromstring(xml)
body = root.find(f"{W}body")
paras = []
for p in body.iter(f"{W}p"):
    txt = "".join(t.text or "" for t in p.iter(f"{W}t"))
    paras.append(txt)

# full Methods TCGA paragraph
for i, t in enumerate(paras):
    if "TCGA bulk RNA-seq" in t:
        print(f"--- docx para {i} ---")
        print(t)
        break

# docx references list
ref_idx = next(i for i, t in enumerate(paras) if t.strip().lower() == "references")
print("\n--- docx references ---")
n = 0
docx_refs = []
for t in paras[ref_idx + 1:]:
    s = t.strip()
    if not s:
        continue
    m = re.match(r"^(\d+)\.\s", s)
    if m:
        n += 1
        docx_refs.append((int(m.group(1)), " ".join(s.split())))
    elif n > 0:
        break
print("docx n refs:", len(docx_refs))

# txt references
txt = (ROOT / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
tl = txt.split("\n")
rs = next(i for i, ln in enumerate(tl) if re.match(r"^#{0,3}\s*references\s*$", ln.strip(), re.I))
parts = re.split(r"(?m)^(\d+)\.\s+", "\n".join(tl[rs + 1:]))
txt_refs = {}
for i in range(1, len(parts) - 1, 2):
    txt_refs[int(parts[i])] = " ".join(parts[i + 1].split())

# compare (txt ref body may have trailing acknowledgements on last; strip at 'Acknowledgements')
diffs = 0
for num, dref in docx_refs:
    tref = txt_refs.get(num, "<missing>")
    tref_clean = tref.split("Acknowledgements")[0].strip()
    dref_clean = dref.split("Acknowledgements")[0].strip()
    if tref_clean != dref_clean:
        diffs += 1
        print(f"REF {num} DIFF:\n  docx: {dref_clean[:200]}\n  txt : {tref_clean[:200]}")
print("ref list diffs:", diffs)
