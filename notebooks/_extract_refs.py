"""Extract all references from manuscript DOCX"""
from docx import Document
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = Document(r'C:\Users\KnightZ\Desktop\细胞受选择\results\CKI_NAR_Manuscript_v4.docx')

in_refs = False
refs = []
for p in doc.paragraphs:
    t = p.text.strip()
    if t == 'References':
        in_refs = True
        continue
    if in_refs and t:
        refs.append(t)

for i, r in enumerate(refs, 1):
    print(f"[{i}] {r[:200]}")
    print()

print(f"\nTotal references: {len(refs)}")
