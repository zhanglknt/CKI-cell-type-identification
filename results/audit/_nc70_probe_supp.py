#!/usr/bin/env python3
"""Probe supplementary-figure panel geometry for nc70 merges.

For each source figure: text panel labels, then a row/column ink profile
(from the 110-dpi raster) to locate whitespace bands = panel boundaries.
"""
import os
import fitz

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(BASE, 'results', 'figures_v58_author')
FIGS = ['figure_S1', 'figure_S2', 'figure_S3', 'figure_S4', 'figure_S5',
        'figure_S6', 'figure_S7', 'figure_S8', 'figure_S9', 'figure_S10',
        'figure_S11', 'figure_S12', 'figure_S13', 'figure_S14',
        'figure_S15', 'figure_S16', 'figure_S17', 'figure_S18']


def bands(profile, gap_min=6):
    """Return content bands: index ranges separated by >=gap_min empty slots."""
    empty = [v == 0 for v in profile]
    out, start = [], None
    run = 0
    for i, e in enumerate(empty):
        if not e:
            if start is None:
                start = i
            run = 0
        else:
            run += 1
            if start is not None and run >= gap_min:
                out.append((start, i - run + 1))
                start = None
    if start is not None:
        out.append((start, len(profile)))
    return out


for name in FIGS:
    doc = fitz.open(os.path.join(STAGE, name + '.pdf'))
    pg = doc[0]
    W, H = pg.rect.width, pg.rect.height
    print(f'=== {name}: {W:.0f}x{H:.0f} pt ({W/72*25.4:.0f}x{H/72*25.4:.0f} mm)')
    # labels
    for b in pg.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = s['text'].strip()
                if t in ('(a)', '(b)', '(c)', '(d)', '(e)', '(f)', 'a', 'b', 'c', 'd') \
                   and s['size'] >= 8.0:
                    r = s['bbox']
                    print(f'  label {t!r} at ({r[0]:.1f},{r[1]:.1f})-({r[2]:.1f},{r[3]:.1f}) size {s["size"]:.1f}')
    # ink profile at 110 dpi
    pix = pg.get_pixmap(dpi=110)
    sc = 110 / 72
    wpx, hpx, n = pix.width, pix.height, pix.n
    colink = [0] * wpx
    rowink = [0] * hpx
    smp = pix.samples
    for yy in range(hpx):
        base = yy * wpx * n
        for xx in range(wpx):
            if smp[base + xx * n] < 245:
                colink[xx] += 1
                rowink[yy] += 1
    colthr = [1 if v >= 2 else 0 for v in colink]
    rowthr = [1 if v >= 2 else 0 for v in rowink]
    vbands = bands(colthr, gap_min=int(0.06 * 72 * sc))   # 6pt gaps
    hbands = bands(rowthr, gap_min=int(0.06 * 72 * sc))
    to_pt = lambda v: v / sc
    print('  col bands (pt):', [(round(to_pt(a), 1), round(to_pt(b), 1)) for a, b in vbands])
    print('  row bands (pt):', [(round(to_pt(a), 1), round(to_pt(b), 1)) for a, b in hbands])
    doc.close()
