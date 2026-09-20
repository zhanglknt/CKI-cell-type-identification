#!/usr/bin/env python3
"""Fix remaining B=1000/Benjamini-Hochberg in Discussion/Limitations paragraph."""
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
    
    if 'Benjamini-Hochberg' not in full and 'B = 1,000' not in full:
        continue
    
    # Fix 1: Remove B=1000/BH claim in limitations
    old1 = (
        "the bootstrap resolution limit (B = 500 for calibration; B = 1,000 for primary "
        "analyses) may be insufficient for detecting subtle effects after multiple-testing "
        "correction. The minimum achievable P-value with B = 1,000 is ~0.001; after "
        "Benjamini-Hochberg correction across 5,151 or 31,764 comparisons, resolution "
        "may be insufficient for marginal signals."
    )
    new1 = (
        "the bootstrap resolution limit for mouse calibration (B = 500) provides "
        "a minimum achievable P-value of ~0.002. For human, TCGA, and brain primary "
        "analyses, standard statistical tests without multiple-testing correction are "
        "applied; while this avoids resolution limits, it means individual pairwise "
        "P-values at the extremes of the distribution should be interpreted with caution."
    )
    if old1 in full:
        new_full = full.replace(old1, new1)
        for t in t_elems:
            t.text = ''
        t_elems[0].text = new_full
        changes += 1
        print('FIXED: bootstrap resolution limit paragraph')
    else:
        # Try simpler sub-patterns
        old1a = (
            'minimum achievable P-value with B = 1,000 is ~0.001; after '
            'Benjamini-Hochberg correction across 5,151 or 31,764 comparisons, '
            'resolution may be insufficient for marginal signals.'
        )
        new1a = (
            'minimum achievable P-value from mouse calibration bootstrap (B = 500) is '
            '~0.002. For primary analyses without bootstrap, P-values are computed using '
            'standard statistical tests; individual pairwise P-values at the extremes '
            'should be interpreted with appropriate caution.'
        )
        if old1a in full:
            new_full = full.replace(old1a, new1a)
            for t in t_elems:
                t.text = ''
            t_elems[0].text = new_full
            changes += 1
            print('FIXED: P-value resolution sub-pattern')
        else:
            # Just try fixing the B=1,000 reference generically
            if 'B = 1,000' in full:
                new_full = full.replace('B = 1,000', 'B = 500')
                for t in t_elems:
                    t.text = ''
                t_elems[0].text = new_full
                changes += 1
                print('FIXED: Generic B=1,000 -> B=500')
    
    # Fix 2: "full bootstrap testing (B = 1,000) requires approximately 32 million"
    if 'B = 1,000' in full and 'million' in full:
        old2 = 'full bootstrap testing (B = 1,000) requires approximately 32 million'
        new2 = 'full pairwise bootstrap testing (B = 500) requires approximately 16 million'
        if old2 in full:
            full = full.replace(old2, new2)
            for t in t_elems:
                t.text = ''
            t_elems[0].text = full
            changes += 1
            print('FIXED: bootstrap timing estimate')
        else:
            # Generic: replace any remaining B=1,000
            if 'B = 1,000' in full:
                full = full.replace('B = 1,000', 'B = 500')
                for t in t_elems:
                    t.text = ''
                t_elems[0].text = full
                changes += 1
                print('FIXED: remaining B=1,000')

# Write back
xml_str = etree.tostring(tree, xml_declaration=True, encoding='UTF-8').decode('utf-8')
with open(XML_PATH, 'w', encoding='utf-8') as f:
    f.write(xml_str)

for pat in ['B = 1,000', 'Benjamini-Hochberg', 'FDR', '5,151']:
    print(f'Remaining {pat}: {xml_str.count(pat)}')

print(f'Changes: {changes}')

if changes > 0:
    cmd = [PYTHON, PACK_SCRIPT, UNPACKED, OUTPUT]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'Repacked: {OUTPUT}')
    else:
        print(f'PACK ERROR: {result.stderr}')
