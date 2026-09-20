# -*- coding: utf-8 -*-
"""Recon: count exact pattern occurrences in generate_manuscript_gb.py source."""
import re
from pathlib import Path

SRC = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_gb.py").read_text(encoding="utf-8")

def c(pat, label):
    n = len(re.findall(pat, SRC))
    print(f"{n:4d}  {label}  [{pat}]")

print("== Supplementary naming ==")
c(r"Additional file 1: Fig\. S\d+", "AF1: Fig. Sx (body, prefixed)")
c(r"Fig\. S\d+", "Fig. Sx (any)")
c(r"Additional file 1: Figure S\d+\.", "AF1: Figure Sx. (legend titles)")
c(r"Figure S\d+", "Figure Sx (any)")
c(r"Additional file 1: Table S\d+", "AF1: Table Sx (prefixed)")
c(r"Table S\d+", "Table Sx (any)")
note_ids = ["3.12","3.21","3.5","3.20","3.22","3.15","3.13","5.2","3.16","3.17","3.14","4.6","5.1","3.23","3.6"]
tot_pref, tot_bare = 0, 0
for nid in note_ids:
    esc = nid.replace(".", r"\.")
    n_any = len(re.findall(r"Note " + esc + r"(?!\d)", SRC))
    n_pref = len(re.findall(r"Additional file 1: Note " + esc + r"(?!\d)", SRC))
    tot_pref += n_pref; tot_bare += n_any - n_pref
    print(f"    Note {nid}: any={n_any} prefixed={n_pref} bare={n_any-n_pref}")
print(f"    TOTAL note refs: any={tot_pref+tot_bare} prefixed={tot_pref} bare={tot_bare}")
c(r"Additional file 1", "Additional file 1 (any)")
c(r"Additional file 2", "Additional file 2 (any)")
c(r"Additional file", "Additional file (any)")

print("== Panel labels ==")
for L in "ABCDEX":
    c(r"\(" + L + r"\)", f"({L})")
c(r"Fig\. 2A", "Fig. 2A")
c(r"Fig\. 2B", "Fig. 2B")
c(r"Fig\. 2C", "Fig. 2C")
c(r"Fig\. \d[A-E]", "Fig. <d><A-E> any")
c(r"Panel A", "Panel A")
c(r"Panel B", "Panel B")

print("== Structure anchors ==")
for s in ["heading('Background', level=1)", "heading('Conclusions', level=1)",
          "heading('List of abbreviations', level=1)", "heading('Declarations', level=1)",
          "heading('Statistical reporting', level=2)",
          "heading('Microglia: composition of the largest candidate share', level=3)",
          "heading('Oligodendrocytes: thalamo-temporal convergence', level=3)",
          "heading('Astrocytes, fibroblasts, and ependymal cells: sparse candidates', level=3)",
          "heading('When to use CKI versus standard metrics', level=2)",
          "heading('Practical usage guide', level=2)",
          "heading('Limitations', level=2)",
          "heading('Additional files', level=1)",
          "heading('Additional file 1: Supplementary figure legends', level=1)",
          "heading('Figure legends', level=1)",
          "heading('References', level=1)",
          "heading(\"Authors' contributions\", level=2)",
          "heading('Acknowledgements', level=2)",
          "heading('Competing interests', level=2)",
          "heading('Funding', level=2)",
          "heading('Availability of data and materials', level=2)",
          "heading('Ethics approval and consent to participate', level=2)",
          "heading('Consent for publication', level=2)",
          "for i, ref in enumerate(_refs_nar, 1):",
          'results" / "CKI_Manuscript_GB.docx',
          ]:
    n = SRC.count(s)
    print(f"{n:4d}  {s}")

print("== Citation groups in MS.txt before References ==")
ms = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\version3\CKI_Submission_v47\CKI_Manuscript_fulltext.txt")
if ms.exists():
    txt = ms.read_text(encoding="utf-8")
    body = txt.split("\nReferences\n")[0] if "\nReferences\n" in txt else txt
    grp = re.findall(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body)
    ok = [g for g in grp if all(1 <= int(x) <= 56 for x in re.split(r"[-,]", g))]
    print(f"    bracket int-groups total={len(grp)} citation-like(1-56)={len(ok)}")
else:
    print("    MS.txt not found")

print("== Abstract word count ==")
m = re.search(r"p\('Standard distance metrics conflate.*?'\)\n", SRC, re.S)
if m:
    s = m.group(0)
    # strip python escapes for counting (approximate: count words in literal)
    lit = s[3:-3]
    words = lit.split()
    print("    abstract literal words (with \\uXXXX tokens as words):", len(words))
