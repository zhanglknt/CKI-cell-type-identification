#!/usr/bin/env python3
"""Final pass: fix all remaining 5,151, B=1,000, Benjamini-Hochberg, 60 cross-organ."""
import subprocess
from lxml import etree

XML_PATH = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript\word\document.xml"
OUTPUT = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\v12_docx\CKI_NAR_Manuscript.docx"
UNPACKED = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript"
PACK_SCRIPT = r"C:\Users\KnightZ\.workbuddy\plugins\marketplaces\codebuddy-plugins-official\plugins\docx\scripts\office\pack.py"
PYTHON = r"C:\Users\KnightZ\AppData\Local\Programs\Python\Python312\python.exe"

with open(XML_PATH, 'r', encoding='utf-8') as f:
    xml_content = f.read()

tree = etree.fromstring(xml_content.encode())
ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
changes = 0

for para in tree.iter(f'{{{ns}}}p'):
    t_elems = list(para.iter(f'{{{ns}}}t'))
    if not t_elems:
        continue
    texts = [t.text for t in t_elems if t.text]
    full = ''.join(texts)
    modified = False
    
    # ---- Fix M3: remaining 5,151 in pair-count contexts ----
    # "for all 5,151 Tabula Sapiens cell-type pairs" 
    if '5,151 Tabula Sapiens' in full:
        full = full.replace('5,151 Tabula Sapiens cell-type pairs', '4,851 Tabula Sapiens cell-type pairs')
        full = full.replace('5,151 Tabula Sapiens pairs', '4,851 Tabula Sapiens pairs')
        modified = True
    
    # "n = 5,151 Tabula Sapiens pairs"
    if 'n = 5,151' in full:
        full = full.replace('n = 5,151', 'n = 4,851')
        modified = True
    
    # ---- Fix M4: 60 → 59 cross-organ ----
    if '60 same-cell-type cross-organ' in full:
        full = full.replace('60 same-cell-type cross-organ', '59 same-cell-type cross-organ')
        modified = True
    if '60 cross-organ pairs' in full:
        full = full.replace('60 cross-organ pairs', '59 cross-organ pairs')
        modified = True
    
    # ---- Fix remaining B=1,000/BH in Discussion ----
    if 'B = 1,000' in full and 'Benjamini-Hochberg' in full:
        old_bh = (
            'minimum achievable P-value with B = 1,000 is ~0.001; after '
            'Benjamini-Hochberg correction across 5,151 or 31,764 comparisons, '
            'resolution may be insufficient for marginal signals.'
        )
        if old_bh in full:
            full = full.replace(old_bh,
                'minimum achievable P-value from mouse calibration bootstrap (B = 500) '
                'is ~0.002. For primary analyses without bootstrap, P-values are computed '
                'using standard statistical tests; individual pairwise P-values at the extremes '
                'of the distribution should be interpreted with appropriate caution.')
            modified = True
        else:
            # Try with 4,851
            old_bh2 = (
                'minimum achievable P-value with B = 1,000 is ~0.001; after '
                'Benjamini-Hochberg correction across 4,851 or 31,764 comparisons, '
                'resolution may be insufficient for marginal signals.'
            )
            if old_bh2 in full:
                full = full.replace(old_bh2,
                    'minimum achievable P-value from mouse calibration bootstrap (B = 500) '
                    'is ~0.002. For primary analyses without bootstrap, P-values are computed '
                    'using standard statistical tests; individual pairwise P-values at the extremes '
                    'of the distribution should be interpreted with appropriate caution.')
                modified = True
    
    # ---- Fix remaining "B = 1,000" generically ----
    if 'B = 1,000' in full:
        full = full.replace('B = 1,000', 'B = 500')
        modified = True
    
    if modified:
        for t in t_elems:
            t.text = ''
        t_elems[0].text = full
        changes += 1

# Write back
xml_str = etree.tostring(tree, xml_declaration=True, encoding='UTF-8').decode('utf-8')
with open(XML_PATH, 'w', encoding='utf-8') as f:
    f.write(xml_str)

for pat in ['B = 1,000', 'Benjamini-Hochberg', 'FDR', '5,151']:
    remaining = xml_str.count(pat)
    status = 'OK' if remaining == 0 else f'{remaining} remaining'
    print(f'{pat}: {status}')

print(f'Paragraph changes: {changes}')

if changes > 0:
    cmd = [PYTHON, PACK_SCRIPT, UNPACKED, OUTPUT]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'Repacked: {OUTPUT}')
    else:
        print(f'PACK ERROR: {result.stderr}')
