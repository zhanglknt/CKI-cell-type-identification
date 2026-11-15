#!/usr/bin/env python3
"""Patch the S7 figure legend inside the existing submission manuscript docx.

Inserts the OL-lineage enrichment sentence into panel (C) of the
Supplementary Figure S7 legend, in place, without regenerating the
manuscript (which would overwrite co-editors' revisions).

Also applies the same edit to the fulltext extraction .txt.
"""
from docx import Document
from pathlib import Path

SUB_DIR = Path(r'c:\Users\KnightZ\Desktop\细胞受选择\CKI_NAR_Submission_v38')
DOCX = SUB_DIR / 'CKI_NAR_Manuscript.docx'
TXT = SUB_DIR / 'CKI_NAR_Manuscript_fulltext.txt'

OLD_C = ('(C) Top 10 Strong candidates (lowest multiplicative residuals), '
         'showing observed \u03c9 for each cell-type/region pair. (D)')
NEW_C = ('(C) Top 10 Strong candidates (lowest multiplicative residuals), '
         'showing observed \u03c9 for each cell-type/region pair; bars are colored by '
         'oligodendrocyte-lineage (purple) vs. non-OL (red) membership. '
         '50/55 Strong-tier candidates are oligodendrocyte-lineage; '
         'hypergeometric P = 4.5e-15. (D)')

# ---- 1. Patch the docx paragraph in place ----
doc = Document(DOCX)
patched = 0
for para in doc.paragraphs:
    if para.text.startswith('Supplementary Figure S7.'):
        if OLD_C in para.text:
            # Rebuild the paragraph text across runs while preserving the
            # first run's formatting.
            full = para.text.replace(OLD_C, NEW_C)
            # Keep the first run, clear the rest, put all text in run 0.
            runs = para.runs
            if runs:
                runs[0].text = full
                for r in runs[1:]:
                    r.text = ''
            patched += 1
        else:
            print('  S7 legend found but expected (C) text not present:')
            print('  ' + para.text[:300])
        break
if patched:
    doc.save(DOCX)
    print(f'  docx patched: {DOCX}')

# ---- 2. Patch the fulltext txt ----
text = TXT.read_text(encoding='utf-8')
if OLD_C in text:
    text = text.replace(OLD_C, NEW_C)
    TXT.write_text(text, encoding='utf-8')
    print(f'  txt patched: {TXT}')
else:
    print('  WARNING: expected S7 (C) text not found in fulltext txt')

print('DONE' if patched else 'NO DOCX CHANGE MADE')
