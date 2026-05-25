"""
63b_fix_slide23_spTree.py - Fix slide23 missing nvGrpSpPr/grpSpPr
Then update 63_split_s2.py to preserve these elements.
"""
import zipfile, shutil, os, io
from lxml import etree
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results\figures_final")

NSMAP = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

GRP_SHAPES = (
    '<p:nvGrpSpPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    '<p:cNvPr id="0" name=""/>'
    '<p:cNvGrpSpPr/>'
    '<p:nvPr/>'
    '</p:nvGrpSpPr>'
    '<p:grpSpPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    '<a:xfrm>'
    '<a:off x="0" y="0"/>'
    '<a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/>'
    '<a:chExt cx="0" cy="0"/>'
    '</a:xfrm>'
    '</p:grpSpPr>'
)


def fix_slide_spTree(pptx_path, slide_filename):
    """Add nvGrpSpPr and grpSpPr to the slide's spTree if missing."""
    tmp = pptx_path.with_suffix(".tmp.pptx")
    
    with zipfile.ZipFile(str(pptx_path), 'r') as zin:
        with zipfile.ZipFile(str(tmp), 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                
                if item.filename == slide_filename:
                    root = etree.fromstring(data)
                    spTree = root.find(".//p:spTree", NSMAP)
                    if spTree is not None:
                        has_nv = spTree.find("p:nvGrpSpPr", NSMAP) is not None
                        has_grp = spTree.find("p:grpSpPr", NSMAP) is not None
                        
                        if not has_nv and not has_grp:
                            # Insert nvGrpSpPr + grpSpPr at the beginning
                            grp_elements = etree.fromstring(f"<root>{GRP_SHAPES}</root>")
                            children = list(grp_elements)
                            # Insert at position 0
                            spTree.insert(0, children[0])  # nvGrpSpPr
                            spTree.insert(1, children[1])  # grpSpPr
                            data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                            print(f"  FIXED: {slide_filename}")
                        else:
                            print(f"  OK: {slide_filename} (already has group props)")
                
                zout.writestr(item, data)
    
    # Replace original
    os.replace(str(tmp), str(pptx_path))


# Fix both EN and ZH
for tag, pptx_path in [("EN", BASE / "CKI_Lecture_2026_v4.pptx"),
                        ("ZH", BASE / "CKI_Lecture_2026_v4_ZH.pptx")]:
    print(f"\n{tag}:")
    fix_slide_spTree(pptx_path, "ppt/slides/slide23.xml")
    print(f"  Saved ({pptx_path.stat().st_size//1024} KB)")

print("\nDone. Now update 63_split_s2.py to preserve group props.")
