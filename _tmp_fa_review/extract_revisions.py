# -*- coding: utf-8 -*-
"""Extract tracked changes (w:ins / w:del) and comments from a docx, with paragraph context."""
import zipfile, re, sys, os
from lxml import etree

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}
W = NS['w']

def para_text(p, skip_deleted=True):
    """Text of a paragraph. Optionally skip w:del content; mark w:ins."""
    parts = []
    for node in p.iter():
        tag = etree.QName(node).localname if isinstance(node.tag, str) else ''
        if tag == 't':
            # check ancestry for ins/del
            anc = node.getparent()
            in_ins = in_del = False
            while anc is not None:
                at = etree.QName(anc).localname if isinstance(anc.tag, str) else ''
                if at == 'ins': in_ins = True
                if at == 'del': in_del = True
                anc = anc.getparent()
            if in_del:
                continue  # skip deleted text in "accepted" view
            txt = node.text or ''
            if in_ins:
                parts.append('⟦INS:' + txt + '⟧')
            else:
                parts.append(txt)
        elif tag == 'delText':
            pass
    return ''.join(parts)

def main(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(f'{{{W}}}body')

    # Map comment id -> comment text
    comments = {}
    if 'word/comments.xml' in z.namelist():
        croot = etree.fromstring(z.read('word/comments.xml'))
        for c in croot.findall(f'{{{W}}}comment'):
            cid = c.get(f'{{{W}}}id')
            author = c.get(f'{{{W}}}author')
            texts = [t.text or '' for t in c.iter(f'{{{W}}}t')]
            comments[cid] = (author, ''.join(texts))

    print('=' * 80)
    print('COMMENTS (批注)')
    print('=' * 80)
    # find comment ranges with anchor text
    for p_i, p in enumerate(body.iter(f'{{{W}}}p')):
        starts = [e.get(f'{{{W}}}id') for e in p.findall(f'.//{{{W}}}commentRangeStart')]
        if starts:
            anchor = para_text(p)
            for cid in starts:
                author, ctext = comments.get(cid, ('?', '?'))
                print(f'\n--- Comment {cid} by {author} ---')
                print(f'  ANCHOR: {anchor[:300]}')
                print(f'  COMMENT: {ctext}')

    print()
    print('=' * 80)
    print('TRACKED CHANGES (修订)')
    print('=' * 80)
    change_no = 0
    for p_i, p in enumerate(body.iter(f'{{{W}}}p')):
        ins_nodes = p.findall(f'.//{{{W}}}ins')
        del_nodes = p.findall(f'.//{{{W}}}del')
        if not ins_nodes and not del_nodes:
            continue
        ctx = para_text(p)
        ctx_clean = re.sub(r'⟦INS:|⟧', '', ctx)
        for n in ins_nodes:
            change_no += 1
            author = n.get(f'{{{W}}}author'); date = n.get(f'{{{W}}}date')
            txt = ''.join(t.text or '' for t in n.iter(f'{{{W}}}t'))
            print(f'\n[{change_no}] INS by {author} {date}')
            print(f'  + {txt!r}')
            print(f'  CTX: {ctx_clean[:400]}')
        for n in del_nodes:
            change_no += 1
            author = n.get(f'{{{W}}}author'); date = n.get(f'{{{W}}}date')
            txt = ''.join(t.text or '' for t in n.iter(f'{{{W}}}delText'))
            print(f'\n[{change_no}] DEL by {author} {date}')
            print(f'  - {txt!r}')
            print(f'  CTX: {ctx_clean[:400]}')
    print(f'\nTOTAL changes: {change_no}')

if __name__ == '__main__':
    main(sys.argv[1])
