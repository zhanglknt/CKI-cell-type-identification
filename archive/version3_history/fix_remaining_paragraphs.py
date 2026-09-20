#!/usr/bin/env python3
"""
Fix remaining text issues that span multiple <w:t> elements.
Uses lxml for proper paragraph-level text extraction and replacement.
"""
import os
import subprocess
from lxml import etree

XML_PATH = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript\word\document.xml"
OUTPUT = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\v12_docx\CKI_NAR_Manuscript.docx"
UNPACKED = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript"
PACK_SCRIPT = r"C:\Users\KnightZ\.workbuddy\plugins\marketplaces\codebuddy-plugins-official\plugins\docx\scripts\office\pack.py"
PYTHON = r"C:\Users\KnightZ\AppData\Local\Programs\Python\Python312\python.exe"

NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_paragraph_text(para):
    """Get the full text of a <w:p> by joining all <w:t> elements."""
    texts = []
    for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            texts.append(t.text)
    return ''.join(texts)

def set_paragraph_text(para, new_text):
    """Replace all <w:t> text in a paragraph with new_text, preserving structure."""
    t_elements = list(para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
    if not t_elements:
        return
    # Clear all
    for t in t_elements:
        t.text = ''
    # Put all text in the first t element
    t_elements[0].text = new_text

def main():
    tree = etree.parse(XML_PATH)
    root = tree.getroot()
    
    replacements = [
        # P37: Statistics section — remove FDR paragraph
        ('Tabula Sapiens 5,151 pairs; brain 31,764 pairs), Benjamini-Hochberg FDR correction was applied; adjusted q-values are reported in Supplementary Tables alongside raw P-values. Primary conclusions are based on patterns that are robust to both raw and FDR-corrected thresholds.',
         'For mouse calibration, bootstrap permutation testing (B = 500) was used to assess significance. For human, TCGA, and brain primary analyses, standard statistical tests were applied without multiple-testing correction; all reported P-values are raw, uncorrected values.'),
        
        # P43: Methods Step 3 — fix bootstrap description (only the part that's wrong)
        ('Bootstrap inference uses B = 1,000 for primary analyses (B = 500 for calibration and exploratory analyses).',
         'Bootstrap inference uses B = 500 for mouse calibration. For primary analyses (human, TCGA, brain), standard statistical tests are applied without multiple testing.'),
        
        # P96: Limitations — tone down bootstrap discussion (only change B=1000 reference)
        # Match in limitations: "B = 1,000 for primary analyses" 
        ('(B = 500 for calibration; B = 1,000 for primary analyses)',
         '(B = 500 for calibration; no bootstrap for primary analyses)'),
        
        # P96: "with B = 1,000 is ~0.001; after Benjamini-Hochberg" — remove FDR reference
        ('minimum achievable P-value with B = 1,000 is ~0.001; after Benjamini-Hochberg correction, the',
         'For primary analyses without bootstrap, P-values are computed using standard statistical tests;'),
        
        # P96: "full bootstrap testing (B = 1,000) requires approximately 32 minutes"
        ('full bootstrap testing (B = 1,000) requires approximately 32 minutes',
         'standard statistical testing requires approximately 1 minute'),
        
        # P37 also: "5,151 pairs" (not caught by M3 because it's "pairs" not "cell-type pairs" or because split)
        # Already corrected by M3 in pair-count contexts, but check if this specific instance remains
    ]
    
    changes = 0
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        text = get_paragraph_text(para)
        for old, new in replacements:
            if old in text:
                new_text = text.replace(old, new)
                set_paragraph_text(para, new_text)
                changes += 1
                print(f'FIXED: {old[:60]}...')
                print(f'  -> {new[:60]}...')
                break  # Only apply first matching replacement per paragraph
    
    # Also handle M3 (5,151 → 4,851) in paragraphs that weren't caught
    m3_old = '5,151 pairs'
    m3_new = '4,851 pairs'
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        text = get_paragraph_text(para)
        if m3_old in text and 'n = ' in text:
            # Only in pair-count context
            if 'n = 5,151 pairs' in text:
                new_text = text.replace('n = 5,151 pairs', 'n = 4,851 pairs')
                set_paragraph_text(para, new_text)
                changes += 1
                print(f'FIXED M3: n = 4,851 pairs')
            elif 'all 5,151 ' in text:
                new_text = text.replace('all 5,151 ', 'all 4,851 ')
                set_paragraph_text(para, new_text)
                changes += 1
                print(f'FIXED M3: all 4,851')
    
    print(f'\nTotal paragraph-level changes: {changes}')
    
    if changes > 0:
        # Write XML
        tree.write(XML_PATH, xml_declaration=True, encoding='UTF-8')
        print(f'Saved XML to {XML_PATH}')
        
        # Repack
        cmd = [PYTHON, PACK_SCRIPT, UNPACKED, OUTPUT]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'Repacked: {OUTPUT}')
        else:
            print(f'PACK ERROR: {result.stderr}')
    else:
        print('No changes made')

if __name__ == '__main__':
    main()
