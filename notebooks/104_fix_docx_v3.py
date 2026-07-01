#!/usr/bin/env python3
"""
Robustly patch DOCX table cells where text may be split across
multiple <w:t> elements.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import os

DOCX = "C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Reproducibility_Guide.docx"
EXTRACT = "C:/Users/KnightZ/Desktop/细胞受选择/results/docx_patch_v3_tmp/"

def get_cell_text(cell, ns):
    """Concatenate all <w:t> text in a cell."""
    texts = [t.text or '' for t in cell.findall('.//w:t', ns)]
    return ' '.join(texts)

def set_cell_text(cell, ns, new_text):
    """Set cell text by modifying the first <w:t> and clearing others."""
    t_elements = cell.findall('.//w:t', ns)
    if not t_elements:
        return False
    # Set first t element to new text
    t_elements[0].text = new_text
    # Clear remaining t elements
    for t in t_elements[1:]:
        t.text = None
    return True

def patch_docx():
    # 1. Extract DOCX
    if os.path.exists(EXTRACT):
        import shutil
        shutil.rmtree(EXTRACT)
    os.makedirs(EXTRACT, exist_ok=True)
    
    with zipfile.ZipFile(DOCX, 'r') as z:
        z.extractall(EXTRACT)
    
    doc_path = Path(EXTRACT) / "word" / "document.xml"
    tree = ET.parse(doc_path)
    root = tree.getroot()
    
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    # 2. Find all tables
    tables = root.findall('.//w:tbl', ns)
    print(f"Found {len(tables)} table(s)")
    
    patched = [False, False]
    
    for table_idx, table in enumerate(tables):
        rows = table.findall('.//w:tr', ns)
        
        for row_idx, row in enumerate(rows):
            cells = row.findall('.//w:tc', ns)
            row_text = ' '.join(get_cell_text(c, ns) for c in cells)
            
            # Fix 1: HK detection method for Tabula Sapiens
            if 'HK detection' in row_text and 'Tabula Sapiens' in row_text:
                for cell in cells:
                    cell_text = get_cell_text(cell, ns)
                    if 'detect' in cell_text.lower() or 'combined' in cell_text:
                        old = cell_text
                        new = cell_text.replace('detect (combined)', 'direct load')
                        if new != old:
                            set_cell_text(cell, ns, new)
                            print(f"  Patched HK method: '{old}' -> '{new}'")
                            patched[0] = True
            
            # Fix 2: HRT Atlas reference for Tabula Sapiens
            if 'HRT Atlas' in row_text and 'Tabula Sapiens' in row_text:
                for cell in cells:
                    cell_text = get_cell_text(cell, ns)
                    if cell_text.strip() == 'no':
                        old = cell_text
                        set_cell_text(cell, ns, 'yes')
                        print(f"  Patched HRT Atlas: '{old}' -> 'yes'")
                        patched[1] = True
    
    # 3. Write back
    tree.write(doc_path, xml_declaration=True, encoding='UTF-8', method='xml')
    print(f"\nPatched: HK method={patched[0]}, HRT Atlas={patched[1]}")
    
    # 4. Re-zip
    with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
        for root_dir, _, files in os.walk(EXTRACT):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, EXTRACT)
                z.write(file_path, arcname)
    
    print(f"Saved: {DOCX}")

if __name__ == "__main__":
    patch_docx()
