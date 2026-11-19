"""nc85: extract the *post-fix* v0.6.4 submission DOCX/XLSX into a flat
blind-review material pack.

Six independent reviewers get the same pack.  They must NOT read each other's
reports, the nc81/nc83 panel summaries, or the nc84 fix report (blind, no
anchoring).  This pack is generated from the freshly rebuilt root package
CKI_Submission_NC/ (nc84 closure / 240-240 build), so it reflects the final
text as it would be submitted.
"""
from pathlib import Path

from docx import Document

BASE = Path(__file__).resolve().parents[2]
PKG = BASE / "CKI_Submission_NC"
OUT = BASE / "results" / "audit" / "_nc85_review_materials"
OUT.mkdir(parents=True, exist_ok=True)

DOCS = [
    ("CKI_Manuscript_NC.docx", "ms.txt"),
    ("CKI_Supplementary_NC.docx", "si.txt"),
    ("CKI_NC_Cover_Letter.docx", "cl.txt"),
    ("CKI_Reproducibility_Guide_NC.docx", "guide.txt"),
]

for src, dst in DOCS:
    doc = Document(PKG / src)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            lines.append(t)
    for ti, tbl in enumerate(doc.tables, 1):
        lines.append(f"[DOCX TABLE {ti}]")
        for row in tbl.rows:
            lines.append(" | ".join(c.text.strip() for c in row.cells))
    (OUT / dst).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{dst}: {len(lines)} lines, {sum(len(x) for x in lines)} chars")

# XLSX overview: sheet names + first rows, so reviewers can locate every table
try:
    import openpyxl

    xlines = []
    for f in ("CKI_Tables_NC.xlsx", "CKI_Supplementary_Tables_NC.xlsx"):
        wb = openpyxl.load_workbook(PKG / f, read_only=True, data_only=True)
        for ws in wb.worksheets:
            xlines.append(f"\n=== {f} :: sheet '{ws.title}'  dims={ws.max_row}x{ws.max_column} ===")
            for row in ws.iter_rows(min_row=1, max_row=min(10, ws.max_row), values_only=True):
                xlines.append(" | ".join("" if v is None else str(v) for v in row))
        wb.close()
    (OUT / "tables_overview.txt").write_text("\n".join(xlines) + "\n", encoding="utf-8")
    print(f"tables_overview.txt: {len(xlines)} lines")
except Exception as e:  # pragma: no cover
    print("xlsx overview skipped:", e)

# MANIFEST as-is
man = (PKG / "MANIFEST.txt").read_text(encoding="utf-8", errors="replace")
(OUT / "manifest.txt").write_text(man, encoding="utf-8")
print(f"manifest.txt: {len(man)} chars")

# Round label, deliberately minimal (no prior-round scores or verdicts)
(OUT / "round.txt").write_text(
    "Round: nc85 (post-fix blind re-review of the v0.6.4 submission package).\n"
    "Read the materials in this directory only. Do not consult any earlier\n"
    "review round, panel summary, editor factcheck, or fix report.\n",
    encoding="utf-8",
)
