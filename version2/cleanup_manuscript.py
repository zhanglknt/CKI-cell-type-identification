"""
Accept all Track Changes and unify text color to black.
"""
import shutil
import zipfile
import os
import re
import xml.etree.ElementTree as ET

WORK_DIR = "C:/Users/KnightZ/Desktop/细胞受选择/version2/NAR_Submission"
SRC = f"{WORK_DIR}/CKI_NAR_Manuscript.docx"
DONE = f"{WORK_DIR}/CKI_NAR_Manuscript_clean.docx"
UNPACKED = f"{WORK_DIR}/unpacked"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def accept_track_changes_in_element(elem):
    """Recursively accept all track changes in an XML element."""
    parent_map = {c: p for p in elem.iter() for c in p}
    
    # Process deletions first (remove them)
    dels = list(elem.iter(f'{{{W}}}del'))
    for del_elem in dels:
        parent = parent_map.get(del_elem)
        if parent is not None:
            parent.remove(del_elem)
    
    # Rebuild parent map after deletions
    parent_map = {c: p for p in elem.iter() for c in p}
    
    # Process insertions (move children to parent)
    ins_elements = list(elem.iter(f'{{{W}}}ins'))
    for ins in ins_elements:
        parent = parent_map.get(ins)
        if parent is None:
            continue
        idx = list(parent).index(ins)
        # Move all children of ins into parent at this position
        children = list(ins)
        for i, child in enumerate(children):
            parent.insert(idx + i, child)
        parent.remove(ins)
    
    # Remove rPrChange elements (revision properties)
    for rpr_change in list(elem.iter(f'{{{W}}}rPrChange')):
        parent = parent_map.get(rpr_change)
        if parent is not None:
            # Accept the change - remove the rPrChange wrapper
            parent.remove(rpr_change)
    
    # Remove pPrChange elements
    for ppr_change in list(elem.iter(f'{{{W}}}pPrChange')):
        parent = parent_map.get(ppr_change)
        if parent is not None:
            parent.remove(ppr_change)
    
    # Remove sectPrChange elements
    for spr_change in list(elem.iter(f'{{{W}}}sectPrChange')):
        parent = parent_map.get(spr_change)
        if parent is not None:
            parent.remove(spr_change)
    
    # Remove tblPrChange, tcPrChange etc
    for tag in ['tblPrChange', 'tcPrChange', 'trPrChange', 'tblGridChange']:
        for change in list(elem.iter(f'{{{W}}}{tag}')):
            parent = parent_map.get(change)
            if parent is not None:
                parent.remove(change)

def remove_paragraph_borders(elem):
    """Remove paragraph border elements."""
    for pPr in elem.iter(f'{{{W}}}pPr'):
        pBdr = pPr.find(f'{{{W}}}pBdr')
        if pBdr is not None:
            pPr.remove(pBdr)

def change_all_text_to_black(elem):
    """Change all w:color to 000000 (black)."""
    for color in elem.iter(f'{{{W}}}color'):
        val = color.get(f'{{{W}}}val')
        if val and val != '000000':
            color.set(f'{{{W}}}val', '000000')

def cleanup_document_xml(filepath):
    """Clean up document.xml: accept TC, remove borders, black text."""
    ET.register_namespace('', W)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    body = root.find(f'{{{W}}}body')
    
    accept_track_changes_in_element(body)
    remove_paragraph_borders(body)
    change_all_text_to_black(body)
    
    # Also clean up rsidRDefault to remove revision-only default runs
    for p in body.iter(f'{{{W}}}p'):
        # Remove rsidRDefault that points to revision-only text
        if f'{{{W}}}rsidRDefault' in p.attrib:
            del p.attrib[f'{{{W}}}rsidRDefault']
    
    tree.write(filepath, xml_declaration=True, encoding='UTF-8')

def cleanup_styles_xml(filepath):
    """Clean up styles.xml: remove borders from styles, black text."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Remove paragraph borders from styles
    for pPr in root.iter(f'{{{W}}}pPr'):
        pBdr = pPr.find(f'{{{W}}}pBdr')
        if pBdr is not None:
            pPr.remove(pBdr)
    
    change_all_text_to_black(root)
    
    tree.write(filepath, xml_declaration=True, encoding='UTF-8')

def main():
    # Clean up unpacked XML
    doc_path = f"{UNPACKED}/word/document.xml"
    styles_path = f"{UNPACKED}/word/styles.xml"
    
    print("Cleaning document.xml...")
    cleanup_document_xml(doc_path)
    
    print("Cleaning styles.xml...")
    cleanup_styles_xml(styles_path)
    
    # Repack to DOCX
    print("Repacking...")
    if os.path.exists(DONE):
        os.remove(DONE)
    
    # Create new zip
    with zipfile.ZipFile(DONE, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(UNPACKED):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, UNPACKED)
                zout.write(filepath, arcname)
    
    print(f"Done: {DONE}")

if __name__ == '__main__':
    main()
