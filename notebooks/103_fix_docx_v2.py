#!/usr/bin/env python3
"""
Properly patch the 2 missing fixes in the DOCX parameter table:
1. HK detection method for Tabula Sapiens: "detect (combined)" -> "direct load"
2. HRT Atlas reference for Tabula Sapiens: "no" -> "yes"
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import os

DOCX = "C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Reproducibility_Guide.docx"
EXTRACT = "C:/Users/KnightZ/Desktop/细胞受选择/results/docx_patch_v2_tmp/"

def patch_docx():
    # 1. Extract DOCX
    if os.path.exists(EXTRACT):
        import shutil
        shutil.rmtree(EXTRACT)
    os.makedirs(EXTRACT, exist_ok=True)
    
    with zipfile.ZipFile(DOCX, 'r') as z:
        z.extractall(EXTRACT)
    
    # 2. Parse document.xml
    doc_path = os.path.join(EXTRACT, "word", "document.xml")
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    # DOCX XML namespace
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # 3. Find all tables
    tables = root.findall('.//w:tbl', ns)
    print(f"Found {len(tables)} tables")
    
    patched = [False, False]
    
    for table_idx, table in enumerate(tables):
        rows = table.findall('.//w:tr', ns)
        for row_idx, row in enumerate(rows):
            cells = row.findall('.//w:tc', ns)
            cell_texts = []
            for cell in cells:
                texts = [t.text or '' for t in cell.findall('.//w:t', ns)]
                cell_texts.append(''.join(texts))
            
            # Check if this is the parameter table (has "Parameter" header)
            if len(cell_texts) >= 2:
                row_text = ' '.join(cell_texts)
                
                # Fix 1: HK detection method for Tabula Sapiens
                if 'HK detection' in row_text and 'Tabula Sapiens' in row_text:
                    for cell in cells:
                        texts = cell.findall('.//w:t', ns)
                        for t in texts:
                            if t.text and 'detect' in t.text:
                                old = t.text
                                t.text = t.text.replace('detect (combined)', 'direct load')
                                if old != t.text:
                                    print(f"  Patched HK method: '{old}' -> '{t.text}'")
                                    patched[0] = True
                
                # Fix 2: HRT Atlas reference for Tabula Sapiens
                if 'HRT Atlas' in row_text and 'Tabula Sapiens' in row_text:
                    for cell in cells:
                        texts = cell.findall('.//w:t', ns)
                        for t in texts:
                            if t.text and t.text.strip() == 'no':
                                old = t.text
                                t.text = 'yes'
                                print(f"  Patched HRT Atlas: '{old}' -> '{t.text}'")
                                patched[1] = True
    
    # 4. Write back
    tree.write(doc_path, xml_declaration=True, encoding='UTF-8', method='xml')
    print(f"Patched: HK method={patched[0]}, HRT Atlas={patched[1]}")
    
    # 5. Re-zip
    with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
        for root_dir, _, files in os.walk(EXTRACT):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, EXTRACT)
                z.write(file_path, arcname)
    
    print(f"Saved: {DOCX}")

if __name__ == "__main__":
    patch_docx()
