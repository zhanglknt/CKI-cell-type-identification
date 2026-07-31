"""
Accept all Track Changes and unify text color to black.
Uses lxml to preserve namespace prefixes (ElementTree mangles them).
"""
import zipfile
import os
from lxml import etree as ET

WORK_DIR = "C:/Users/KnightZ/Desktop/细胞受选择/version2/NAR_Submission"
SRC = f"{WORK_DIR}/CKI_NAR_Manuscript_with_tc.docx"
DONE = f"{WORK_DIR}/CKI_NAR_Manuscript.docx"
UNPACKED = f"{WORK_DIR}/_cleanup_tmp"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def accept_track_changes(elem):
    """Recursively accept all track changes in an lxml element."""
    parent_map = {c: p for p in elem.iter() for c in p}
    
    # 1. Remove deletions
    for del_elem in list(elem.iter(f'{{{W}}}del')):
        parent = parent_map.get(del_elem)
        if parent is not None:
            parent.remove(del_elem)
    
    # Rebuild parent map
    parent_map = {c: p for p in elem.iter() for c in p}
    
    # 2. Move insertion children to parent
    for ins in list(elem.iter(f'{{{W}}}ins')):
        parent = parent_map.get(ins)
        if parent is None:
            continue
        idx = list(parent).index(ins)
        children = list(ins)
        for i, child in enumerate(children):
            parent.insert(idx + i, child)
        parent.remove(ins)
    
    # Rebuild parent map
    parent_map = {c: p for p in elem.iter() for c in p}
    
    # 3. Remove rPrChange (accept run property changes)
    for rpr in list(elem.iter(f'{{{W}}}rPrChange')):
        parent = parent_map.get(rpr)
        if parent is not None:
            parent.remove(rpr)
    
    # 4. Remove pPrChange (accept paragraph property changes)
    for ppr in list(elem.iter(f'{{{W}}}pPrChange')):
        parent = parent_map.get(ppr)
        if parent is not None:
            parent.remove(ppr)
    
    # 5. Remove other change elements
    for tag in ['sectPrChange', 'tblPrChange', 'tcPrChange', 'trPrChange', 'tblGridChange']:
        for change in list(elem.iter(f'{{{W}}}{tag}')):
            parent = parent_map.get(change)
            if parent is not None:
                parent.remove(change)

def remove_paragraph_borders(elem):
    for pBdr in list(elem.iter(f'{{{W}}}pBdr')):
        pBdr.getparent().remove(pBdr)

def change_all_color_to_black(elem):
    for color in list(elem.iter(f'{{{W}}}color')):
        val = color.get(f'{{{W}}}val')
        if val and val != '000000':
            color.set(f'{{{W}}}val', '000000')

def cleanup_doc_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    body = root.find(f'{{{W}}}body')
    
    accept_track_changes(body)
    remove_paragraph_borders(body)
    change_all_color_to_black(body)
    
    # Remove rsidRDefault (only needed for revision tracking)
    for p in body.iter(f'{{{W}}}p'):
        attr_key = f'{{{W}}}rsidRDefault'
        if attr_key in p.attrib:
            del p.attrib[attr_key]
    
    # Write preserving original encoding and namespace prefixes
    tree.write(filepath, xml_declaration=True, encoding='UTF-8', standalone=True)

def cleanup_styles_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    remove_paragraph_borders(root)
    change_all_color_to_black(root)
    tree.write(filepath, xml_declaration=True, encoding='UTF-8', standalone=True)

def main():
    # Start fresh from unpack
    if os.path.exists(UNPACKED):
        import shutil
        shutil.rmtree(UNPACKED)
    os.makedirs(UNPACKED)
    
    # Unpack the TC backup
    with zipfile.ZipFile(SRC, 'r') as z:
        z.extractall(UNPACKED)
    
    doc_path = f"{UNPACKED}/word/document.xml"
    styles_path = f"{UNPACKED}/word/styles.xml"
    
    print("Cleaning document.xml with lxml...")
    cleanup_doc_xml(doc_path)
    
    print("Cleaning styles.xml with lxml...")
    cleanup_styles_xml(styles_path)
    
    # Repack
    print("Repacking to manuscript...")
    if os.path.exists(DONE):
        os.remove(DONE)
    
    with zipfile.ZipFile(DONE, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(UNPACKED):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, UNPACKED)
                zout.write(filepath, arcname)
    
    # Cleanup
    import shutil
    shutil.rmtree(UNPACKED)
    
    print(f"Done: {DONE}")

if __name__ == '__main__':
    main()
