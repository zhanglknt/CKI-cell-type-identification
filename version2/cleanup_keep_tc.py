"""
Remove paragraph borders and unify text color to black.
PRESERVES all Track Changes markup (w:ins, w:del, w:delText, rPrChange, pPrChange, etc.).
Uses lxml to preserve namespace prefixes.
"""
import zipfile
import os
import shutil
from lxml import etree as ET

WORK_DIR = "C:/Users/KnightZ/Desktop/细胞受选择/version2/NAR_Submission"
SRC = f"{WORK_DIR}/CKI_NAR_Manuscript_with_tc.docx"
DONE = f"{WORK_DIR}/CKI_NAR_Manuscript.docx"
UNPACKED = f"{WORK_DIR}/_cleanup_tmp"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def remove_paragraph_borders(elem):
    """Remove all paragraph border elements."""
    for pBdr in list(elem.iter(f'{{{W}}}pBdr')):
        pBdr.getparent().remove(pBdr)
    print(f"  Removed paragraph borders")

def change_all_color_to_black(elem):
    """Change all explicit w:color values to 000000 (black)."""
    count = 0
    for color in list(elem.iter(f'{{{W}}}color')):
        val = color.get(f'{{{W}}}val')
        if val and val != '000000' and val != 'auto':
            color.set(f'{{{W}}}val', '000000')
            count += 1
    print(f"  Changed {count} color values to black")

def cleanup_doc_xml(filepath):
    """Clean document.xml: remove borders, unify colors. Keep all TC markup."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    body = root.find(f'{{{W}}}body')
    
    remove_paragraph_borders(body)
    change_all_color_to_black(body)
    
    tree.write(filepath, xml_declaration=True, encoding='UTF-8', standalone=True)

def cleanup_styles_xml(filepath):
    """Clean styles.xml: remove borders, unify colors."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    remove_paragraph_borders(root)
    change_all_color_to_black(root)
    tree.write(filepath, xml_declaration=True, encoding='UTF-8', standalone=True)

def verify_result(filepath):
    """Verify: TC markup present, no borders, no non-black colors."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ins_count = len(root.findall(f'.//{{{W}}}ins'))
    del_count = len(root.findall(f'.//{{{W}}}del'))
    pBdr_count = len(root.findall(f'.//{{{W}}}pBdr'))
    
    non_black = []
    for color in root.findall(f'.//{{{W}}}color'):
        val = color.get(f'{{{W}}}val')
        if val and val not in ('000000', 'auto'):
            non_black.append(val)
    
    print(f"  w:ins: {ins_count}")
    print(f"  w:del: {del_count}")
    print(f"  pBdr: {pBdr_count}")
    print(f"  Non-black colors: {non_black}")
    
    ok = (ins_count > 0 or del_count > 0) and pBdr_count == 0 and len(non_black) == 0
    print(f"  VERIFY: {'PASS' if ok else 'FAIL'}")
    return ok

def main():
    if os.path.exists(UNPACKED):
        shutil.rmtree(UNPACKED)
    os.makedirs(UNPACKED)
    
    # Unpack the TC backup
    with zipfile.ZipFile(SRC, 'r') as z:
        z.extractall(UNPACKED)
    
    doc_path = f"{UNPACKED}/word/document.xml"
    styles_path = f"{UNPACKED}/word/styles.xml"
    
    print("=== Cleaning document.xml (keeping TC) ===")
    cleanup_doc_xml(doc_path)
    print("  Verifying...")
    verify_result(doc_path)
    
    print("\n=== Cleaning styles.xml ===")
    cleanup_styles_xml(styles_path)
    
    # Repack
    print("\n=== Repacking ===")
    if os.path.exists(DONE):
        os.remove(DONE)
    
    with zipfile.ZipFile(DONE, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(UNPACKED):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, UNPACKED)
                zout.write(filepath, arcname)
    
    shutil.rmtree(UNPACKED)
    size_kb = os.path.getsize(DONE) / 1024
    print(f"Done: {DONE} ({size_kb:.0f} KB)")

if __name__ == '__main__':
    main()
