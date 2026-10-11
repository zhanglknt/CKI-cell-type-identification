#!/usr/bin/env python3
"""Probe panel-label positions and ink bounding boxes for nc70 figure merges."""
import os
import fitz

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(BASE, 'results', 'figures_v58_author')

FIGS = ['figure1', 'figure2', 'figure3', 'figure6', 'figure7']


def probe(name):
    doc = fitz.open(os.path.join(STAGE, name + '.pdf'))
    for pno, page in enumerate(doc):
        print(f'=== {name} page {pno}: {page.rect.width:.1f} x {page.rect.height:.1f} pt '
              f'({page.rect.width/72*25.4:.0f} x {page.rect.height/72*25.4:.0f} mm)')
        d = page.get_text('dict')
        spans = []
        for b in d['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    t = s['text'].strip()
                    if t in ('(a)', '(b)', '(c)', '(d)', '(e)', '(f)', 'a', 'b', 'c', 'd', 'e', 'f') \
                       and s['size'] >= 7.5:
                        spans.append((t, round(s['bbox'][0], 1), round(s['bbox'][1], 1),
                                      round(s['bbox'][2], 1), round(s['bbox'][3], 1),
                                      round(s['size'], 1), s['font']))
        for t in spans:
            print('  label', t)
        # ink bbox of all drawings+text
        ink = None
        for b in d['blocks']:
            r = fitz.Rect(b['bbox'])
            ink = r if ink is None else ink | r
        try:
            for dr in page.get_drawings():
                r = dr['rect']
                if r.is_empty or r.is_infinite:
                    continue
                ink = r if ink is None else ink | r
        except Exception:
            pass
        if ink:
            print(f'  ink bbox: x[{ink.x0:.1f},{ink.x1:.1f}] y[{ink.y0:.1f},{ink.y1:.1f}]')
    doc.close()


for f in FIGS:
    probe(f)
