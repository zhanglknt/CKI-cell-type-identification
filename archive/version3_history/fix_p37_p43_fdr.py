#!/usr/bin/env python3
"""Fix remaining P37 and P43 FDR paragraphs using lxml."""
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
    
    # P37: Statistics section
    old37 = (
        'For analyses involving multiple comparisons (Tabula Sapiens 5,151 pairs; '
        'brain 31,764 pairs), Benjamini-Hochberg FDR correction was applied; '
        'adjusted q-values are reported in Supplementary Tables alongside raw P-values. '
        'Primary conclusions are based on effect sizes and patterns that are robust '
        'to both raw and FDR-corrected thresholds.'
    )
    new37 = (
        'For mouse calibration, bootstrap permutation testing (B = 500) was used to '
        'assess significance. For human, TCGA, and brain primary analyses, standard '
        'statistical tests were applied without multiple-testing correction; all reported '
        'P-values are raw, uncorrected values.'
    )
    
    if old37 in full:
        new_full = full.replace(old37, new37)
        for t in t_elems:
            t.text = ''
        t_elems[0].text = new_full
        changes += 1
        print('FIXED P37: FDR paragraph replaced')
    
    # P43: Methods Step 3 — remove remaining FDR sentence
    if 'Step 3' in full and 'Benjamini-Hochberg' in full:
        old43 = (
            'For analyses involving multiple comparisons, Benjamini-Hochberg FDR '
            'correction was applied; FDR-adjusted q-values are reported in '
            'Supplementary Tables alongside raw P-values.'
        )
        if old43 in full:
            new_full = full.replace(old43, '')
            for t in t_elems:
                t.text = ''
            t_elems[0].text = new_full
            changes += 1
            print('FIXED P43: remaining FDR sentence removed')
        else:
            idx = full.find('FDR')
            if idx >= 0:
                print(f'P43 FDR context (unmatched): ...{full[max(0,idx-60):idx+100]}...')

# Write back
xml_str = etree.tostring(tree, xml_declaration=True, encoding='UTF-8').decode('utf-8')
with open(XML_PATH, 'w', encoding='utf-8') as f:
    f.write(xml_str)

# Count remaining
for pat in ['B = 1,000', 'Benjamini-Hochberg', 'FDR', '5,151 pairs']:
    print(f'Remaining {pat}: {xml_str.count(pat)}')

print(f'Paragraph changes: {changes}')

if changes > 0:
    cmd = [PYTHON, PACK_SCRIPT, UNPACKED, OUTPUT]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'Repacked: {OUTPUT}')
    else:
        print(f'PACK ERROR: {result.stderr}')
