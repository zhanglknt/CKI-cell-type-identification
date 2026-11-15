#!/usr/bin/env python3
"""nc70 main-figure consolidation (7 -> 5, panels 4/6/4/4/6).

Vector band re-composition with PyMuPDF (no re-render; precedent:
archive/scripts/_tighten_figure1.py, notebooks/_merge_fig2_fig3_nc49.py).

Outputs (in results/figures_v58_author/, originals backed up in
results/audit/nc70_backup/):
  figure1.pdf  5 -> 4 panels : old 1a+1b merged (re-letter only)
  figure2.pdf  5+3 -> 6      : old fig2 cells + old fig3 cells
                               (2b+2c merged -> b; 3a+3c merged -> e)
  figure3.pdf  <- old figure4.pdf (TCGA, a-d unchanged)
  figure4.pdf  <- old figure5.pdf (cross-organ, a-d unchanged)
  figure5.pdf  old fig6 (a-d) + old fig7 as (e),(f)

Scale note: new fig2 bands at 0.80 uniform so height ~= old fig6 (273 mm),
the package's existing max-height precedent; panel labels are re-stamped
at full 9 pt (not scaled), body text >= ~5.5 pt (package mathtext norm
already 4.9-6.3 pt).
"""
import os
import shutil
import fitz

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(BASE, 'results', 'figures_v58_author')
BAK = os.path.join(BASE, 'results', 'audit', 'nc70_backup')
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'

S = 0.80            # uniform band scale for new figure 2
GAP_X = 8.0
GAP_Y = 6.0
MARG = 6.0
W2 = 504.567        # 178 mm


def white(page, rect):
    r = fitz.Rect(rect.x0 - 1.5, rect.y0 - 1.5, rect.x1 + 1.5, rect.y1 + 1.5)
    page.draw_rect(r, color=None, fill=(1, 1, 1), overlay=True)


def stamp(page, x, y_baseline, text, size):
    page.insert_text((x, y_baseline), text, fontname='arialbd',
                     fontfile=ARIALBD, fontsize=size, color=(0, 0, 0))


def ink_bbox(page, clip):
    ink = None
    d = page.get_text('dict', clip=clip)
    for b in d['blocks']:
        r = fitz.Rect(b['bbox'])
        ink = r if ink is None else ink | r
    for dr in page.get_drawings():
        r = dr['rect']
        if r.is_empty or r.is_infinite:
            continue
        if r.intersects(clip):
            r = r & clip
            ink = r if ink is None else ink | r
    return ink


# ---------------------------------------------------------------- figure 1
def build_fig1():
    src = fitz.open(os.path.join(BAK, 'figure1.pdf'))
    sp = src[0]
    out = fitz.open()
    page = out.new_page(width=sp.rect.width, height=sp.rect.height)
    page.show_pdf_page(page.rect, src, 0)
    # erase old (b); re-letter c->b, d->c, e->d  (Arial-BoldMT 10 pt)
    jobs = [
        ((33.6, 182.6, 46.3, 196.4), None),          # old (b) removed
        ((33.6, 260.9, 45.8, 274.7), '(b)'),
        ((204.5, 260.9, 217.3, 274.7), '(c)'),
        ((372.6, 260.9, 384.8, 274.7), '(d)'),
    ]
    for rect, new in jobs:
        white(page, fitz.Rect(*rect))
        if new:
            stamp(page, rect[0], rect[1] + 10.6, new, 10.0)
    out.save(os.path.join(STAGE, 'figure1.pdf'), deflate=True, garbage=4)
    print(f'figure1: relabelled, {sp.rect.width:.1f} x {sp.rect.height:.1f} pt')
    out.close()
    src.close()


# ---------------------------------------------------------------- figure 2
def build_fig2():
    f2 = fitz.open(os.path.join(BAK, 'figure2.pdf'))
    f3 = fitz.open(os.path.join(BAK, 'figure3.pdf'))
    p2, p3 = f2[0], f3[0]

    # crops: (doc, page, rect, old-label rect or None, path-label probe or None)
    C2a = (f2, fitz.Rect(6, 6, 252, 203), fitz.Rect(16.1, 12.3, 27.1, 22.4), None)
    C2b = (f2, fitz.Rect(252, 6, 502, 203), fitz.Rect(261.4, 12.3, 272.9, 22.4), None)
    C2c = (f2, fitz.Rect(6, 202, 229, 374), fitz.Rect(16.1, 208.4, 27.1, 218.5), None)
    C2d = (f2, fitz.Rect(229, 203, 502, 374), fitz.Rect(250.8, 208.4, 262.3, 218.5), None)
    C2e = (f2, fitz.Rect(6, 374, 502, 575.4), fitz.Rect(16.1, 382.4, 27.1, 392.5), None)
    C3a = (f3, fitz.Rect(8, 12, 260, 190), None, fitz.Rect(6, 12, 34, 34))
    C3b = (f3, fitz.Rect(276, 12, 618, 190), fitz.Rect(306.1, 18.3, 317.3, 28.7), None)
    C3c = (f3, fitz.Rect(618, 12, 945, 190), fitz.Rect(655.8, 17.6, 666.8, 30.1), None)

    # rows: list of (crop, new label or None)
    rows = [
        [(C2a, '(a)'), (C2b, '(b)')],
        [(C2d, '(c)'), (C2c, None)],      # 2c = lower half of merged panel b
        [(C2e, '(d)')],
        [(C3a, '(e)'), (C3c, None)],      # 3c = right half of merged panel e
        [(C3b, '(f)')],
    ]

    # verify crops contain their ink
    for ri, row in enumerate(rows):
        for (doc, crop, _lab, _probe), _nl in row:
            ink = ink_bbox(doc[0], crop)
            if ink and not crop.contains(ink):
                print(f'  WARN row {ri}: ink {ink} exceeds crop {crop}')

    # row scales & heights
    meta = []
    for row in rows:
        tw = sum(c[0][1].width for c in row) + GAP_X * (len(row) - 1)
        s = min(S, (W2 - 2 * MARG - GAP_X * (len(row) - 1)) /
                sum(c[0][1].width for c in row))
        h = max(c[0][1].height for c in row) * s
        meta.append((s, h))
    H = MARG + sum(h for _, h in meta) + GAP_Y * (len(rows) - 1) + MARG

    out = fitz.open()
    page = out.new_page(width=W2, height=H)
    y = MARG
    for row, (s, h) in zip(rows, meta):
        tw = sum(c[0][1].width for c in row) * s + GAP_X * (len(row) - 1)
        x = (W2 - tw) / 2
        for (doc, crop, lab, probe), newlab in row:
            tgt = fitz.Rect(x, y, x + crop.width * s, y + crop.height * s)
            page.show_pdf_page(tgt, doc, 0, clip=crop)
            if lab is not None:  # white out old text label (mapped coords)
                mr = fitz.Rect(tgt.x0 + (lab.x0 - crop.x0) * s,
                               tgt.y0 + (lab.y0 - crop.y0) * s,
                               tgt.x0 + (lab.x1 - crop.x0) * s,
                               tgt.y0 + (lab.y1 - crop.y0) * s)
                white(page, mr)
            if probe is not None:  # path-drawn label: white its probe zone
                mr = fitz.Rect(tgt.x0 + (probe.x0 - crop.x0) * s,
                               tgt.y0 + (probe.y0 - crop.y0) * s,
                               tgt.x0 + (probe.x1 - crop.x0) * s,
                               tgt.y0 + (probe.y1 - crop.y0) * s)
                white(page, mr)
            if newlab:
                stamp(page, tgt.x0 + 3, tgt.y0 + 12, newlab, 9.0)
            x += crop.width * s + GAP_X
        y += h + GAP_Y

    out.save(os.path.join(STAGE, 'figure2.pdf'), deflate=True, garbage=4)
    print(f'figure2: 6 panels, {W2:.1f} x {H:.1f} pt = '
          f'{W2/72*25.4:.0f} x {H/72*25.4:.0f} mm')
    out.close()
    f2.close()
    f3.close()


# ---------------------------------------------------------------- figure 3/4
def copy_figs():
    shutil.copy2(os.path.join(BAK, 'figure4.pdf'),
                 os.path.join(STAGE, 'figure3.pdf'))
    shutil.copy2(os.path.join(BAK, 'figure5.pdf'),
                 os.path.join(STAGE, 'figure4.pdf'))
    print('figure3 <- old figure4 (TCGA); figure4 <- old figure5 (cross-organ)')


# ---------------------------------------------------------------- figure 5
def build_fig5():
    f6 = fitz.open(os.path.join(BAK, 'figure6.pdf'))
    f7 = fitz.open(os.path.join(BAK, 'figure7.pdf'))
    p6, p7 = f6[0], f7[0]
    W = p6.rect.width
    gap = 24.0
    y7 = p6.rect.height + gap
    x7 = (W - p7.rect.width) / 2
    H = y7 + p7.rect.height + MARG

    out = fitz.open()
    page = out.new_page(width=W, height=H)
    page.show_pdf_page(fitz.Rect(0, 0, W, p6.rect.height), f6, 0)
    page.show_pdf_page(fitz.Rect(x7, y7, x7 + p7.rect.width, y7 + p7.rect.height), f7, 0)
    # white out fig7's bare labels a/b, stamp (e)/(f) at 14 pt to match fig6
    for lab, new in ((fitz.Rect(4.1, 23.1, 9.1, 33.1), '(e)'),
                     (fitz.Rect(236.4, 23.1, 241.9, 33.1), '(f)')):
        white(page, fitz.Rect(x7 + lab.x0, y7 + lab.y0, x7 + lab.x1, y7 + lab.y1))
        stamp(page, x7 + lab.x0 - 3, y7 + lab.y1 + 1, new, 14.0)
    out.save(os.path.join(STAGE, 'figure5.pdf'), deflate=True, garbage=4)
    print(f'figure5: 6 panels, {W:.1f} x {H:.1f} pt = '
          f'{W/72*25.4:.0f} x {H/72*25.4:.0f} mm')
    out.close()
    f6.close()
    f7.close()


def audit():
    import collections
    for f in ['figure1', 'figure2', 'figure3', 'figure4', 'figure5']:
        doc = fitz.open(os.path.join(STAGE, f + '.pdf'))
        pg = doc[0]
        sizes = collections.Counter()
        labels = []
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    sizes[round(s['size'], 1)] += 1
                    t = s['text'].strip()
                    if t in ('(a)', '(b)', '(c)', '(d)', '(e)', '(f)') and s['size'] >= 8.5:
                        labels.append((t, round(s['bbox'][0], 1), round(s['bbox'][1], 1)))
        print(f'{f}: {pg.rect.width:.0f}x{pg.rect.height:.0f} pt, '
              f'labels {sorted(labels)}, sizes {dict(sorted(sizes.items()))}')
        pix = pg.get_pixmap(dpi=110)
        pix.save(os.path.join(BASE, 'results', 'audit', f'_nc70_{f}_preview.png'))
        doc.close()
    # whiteness probe: fig1 old (b) zone must be fully white after erase
    doc = fitz.open(os.path.join(STAGE, 'figure1.pdf'))
    pg = doc[0]
    clip = fitz.Rect(33.6, 182.6, 46.3, 196.4)
    pix = pg.get_pixmap(dpi=150, clip=clip)
    nonwhite = sum(1 for i in range(0, len(pix.samples), pix.n)
                   if pix.samples[i] < 250)
    print(f'fig1 old-(b) zone: {nonwhite} non-white px of '
          f'{pix.width*pix.height} ({"CLEAN" if nonwhite == 0 else "RESIDUE!"})')
    # fig2 old scaled labels must be covered: probe the 7.2 pt label spots
    doc2 = fitz.open(os.path.join(STAGE, 'figure2.pdf'))
    pg2 = doc2[0]
    bad = []
    for b in pg2.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = s['text'].strip()
                if t in ('(a)', '(b)', '(c)', '(d)', '(e)') and s['size'] < 8.5:
                    r = fitz.Rect(s['bbox'])
                    px = pg2.get_pixmap(dpi=150, clip=r)
                    nw = sum(1 for i in range(0, len(px.samples), px.n)
                             if px.samples[i] < 250)
                    if nw:
                        bad.append((t, round(r.x0, 1), round(r.y0, 1), nw))
    print('fig2 covered old labels with residue:', bad if bad else 'NONE (all white)')
    doc.close()
    doc2.close()


if __name__ == '__main__':
    build_fig1()
    build_fig2()
    copy_figs()
    build_fig5()
    audit()
