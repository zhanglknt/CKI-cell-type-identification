"""
61_fix_slide16_rebuild.py — 修复PPTX Slide 16缺失的nvGrpSpPr/grpSpPr

根因: Slide 16的spTree缺少OOXML必需的nvGrpSpPr和grpSpPr元素，
导致PowerPoint报"无法读取部分内容"。

修复: 直接操作ZIP内slide16.xml，插入缺失的两个必需元素。

验证结果: PowerPoint COM打开v4文件，22页全部正常，无任何错误。
"""

import os, shutil
from lxml import etree
import zipfile

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
ET = '{%s}' % P_NS
EA = '{%s}' % A_NS


def fix_slide16(pptx_path, out_path):
    """Copy v3 to v4, then add missing nvGrpSpPr/grpSpPr to slide 16's spTree."""
    shutil.copy2(pptx_path, out_path)

    with zipfile.ZipFile(out_path, 'r') as zin:
        all_files = {name: zin.read(name) for name in zin.namelist()}

    tree = etree.fromstring(all_files['ppt/slides/slide16.xml'])
    spTree = tree.find(f'{ET}cSld/{ET}spTree')

    if spTree.find(f'{ET}nvGrpSpPr') is not None and spTree.find(f'{ET}grpSpPr') is not None:
        print('  Already fixed')
        return

    # Build nvGrpSpPr
    nvGrp = etree.Element(f'{ET}nvGrpSpPr')
    etree.SubElement(nvGrp, f'{ET}cNvPr', id='1', name='')
    etree.SubElement(nvGrp, f'{ET}cNvGrpSpPr')
    etree.SubElement(nvGrp, f'{ET}nvPr')

    # Build grpSpPr
    grpSp = etree.Element(f'{ET}grpSpPr')
    xfrm = etree.SubElement(grpSp, f'{EA}xfrm')
    etree.SubElement(xfrm, f'{EA}off', x='0', y='0')
    etree.SubElement(xfrm, f'{EA}ext', cx='0', cy='0')
    etree.SubElement(xfrm, f'{EA}chOff', x='0', y='0')
    etree.SubElement(xfrm, f'{EA}chExt', cx='0', cy='0')

    spTree.insert(0, nvGrp)
    spTree.insert(1, grpSp)

    all_files['ppt/slides/slide16.xml'] = etree.tostring(
        tree, xml_declaration=True, encoding='UTF-8', standalone=True
    )

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in all_files.items():
            zout.writestr(name, data)

    print('  Fixed: added nvGrpSpPr and grpSpPr')


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    BASE = r'results/figures_final'
    for fname in ['CKI_Lecture_2026_v3.pptx', 'CKI_Lecture_2026_v3_ZH.pptx']:
        src = os.path.join(BASE, fname)
        dst = os.path.join(BASE, fname.replace('v3', 'v4'))
        print(f'\n{fname} -> {os.path.basename(dst)}')
        fix_slide16(src, dst)
    print('\nDone.')
