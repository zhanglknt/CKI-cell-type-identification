# -*- coding: utf-8 -*-
"""Self-check for CKI_NC_Cover_Letter.docx against NC conversion requirements."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
DOCX = ROOT / "results" / "CKI_NC_Cover_Letter.docx"

from docx import Document

doc = Document(str(DOCX))
full = "\n".join(p.text for p in doc.paragraphs)

nc_count = full.count("Nature Communications")
gb_count = full.count("Genome Biology")
new_title = "CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics"
title_present = new_title in full
colon_title = "CKI: a Ka/Ks-inspired" in full
dear = full.startswith("Dear Editors,")
word_count = len(full.split())
doi_ok = "10.5281/zenodo.22735744" in full
v_ok = "v0.5.0" in full
github_ok = "github.com/zhanglknt/CKI-cell-type-identification" in full
article_ok = "as an Article in Nature Communications" in full
methodology_phrase = "novel computational method for quantifying functional divergence in single-cell genomics" in full
reviewers = all(n in full for n in ["Theis", "Welch", "Linnarsson", "Patrik", "Alejandro", "Zemin Zhang"])

checks = [
    ("'Nature Communications' >=2", nc_count >= 2, nc_count),
    ("'Genome Biology' ==0", gb_count == 0, gb_count),
    ("new title present", title_present, title_present),
    ("no colon title", not colon_title, colon_title),
    ("starts with 'Dear Editors,'", dear, dear),
    ("word count <=550", word_count <= 550, word_count),
    ("DOI 10.5281/zenodo.22735744", doi_ok, doi_ok),
    ("release tag v0.5.0", v_ok, v_ok),
    ("GitHub URL", github_ok, github_ok),
    ("'as an Article in Nature Communications'", article_ok, article_ok),
    ("methodology phrase", methodology_phrase, methodology_phrase),
    ("6 suggested reviewers", reviewers, reviewers),
]

all_pass = True
for name, ok, val in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {val}")
    all_pass = all_pass and ok

print(f"\nWord count: {word_count}")
print(f"NC mentions: {nc_count}, GB mentions: {gb_count}")
print("OVERALL:", "PASS" if all_pass else "FAIL")
