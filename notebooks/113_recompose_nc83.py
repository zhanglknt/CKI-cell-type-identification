#!/usr/bin/env python3
"""nc83 figure re-composition: figure 2 (6 -> 4 panels) + new Supplementary Fig. 11.

Route chosen by the author (2026-11-18): main figures must reach 7 pt, SI panels
are split off rather than squeezed.  figure 2 keeps the four mechanistic panels
(a-d); the two robustness panels move to Supplementary Fig. 11.

  figure2 = old fig2 a (k_n calibration) | old fig2 b (k_f/k_n decomposition)
            old fig2 d|c (TS metric heatmap + omega by category)
            old fig2 e (functional change vs neutral drift, ROC)
  SF11a   = old fig3 a (Kang batch1 replication)
  SF11b   = old fig3 c (brain drift misreporting)
  SF11c   = old fig3 b (brain calibration by tier)

All bands are placed at scale 1.0 (figure 2) / 1.15 (SF11) from the pristine
v58 artwork in results/audit/nc70_backup/; nothing is re-rendered and no data
is touched.  Page widths are chosen so 1.0x of the artwork fits 178 mm.

Outputs: results/figures_nc83/figure2.pdf, Supplementary_Fig_11.pdf
"""
import os

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAK = os.path.join(BASE, 'results', 'audit', 'nc70_backup')
OUTDIR = os.path.join(BASE, 'results', 'figures_nc83')
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'
MM = 25.4 / 72.0


def B(name):
    return os.path.join(BAK, name + '.pdf')


def white(page, rect, pad=1.2):
    page.draw_rect(fitz.Rect(rect.x0 - pad, rect.y0 - pad,
                             rect.x1 + pad, rect.y1 + pad),
                   color=None, fill=(1, 1, 1), overlay=True)


def stamp(page, x, y, text, size):
    page.insert_text((x, y), text, fontname='ArB', fontfile=ARIALBD,
                     fontsize=size, color=(0, 0, 0))


def compose(out_name, rows, page_w, scale, gap_x=6.0, gap_y=6.0, marg=4.0,
            label_pt=9.0, label_dx=3.0, label_dy=12.0, post_whites=()):
    """rows: list of list of (src_path, crop Rect, [white rects], stamp tuple)."""
    docs = {}
    heights = [max(c[1].height for c in row) * scale for row in rows]
    H = 2 * marg + sum(heights) + gap_y * (len(rows) - 1)
    out = fitz.open()
    page = out.new_page(width=page_w, height=H)
    y = marg
    for row, h in zip(rows, heights):
        tw = sum(c[1].width * scale for c in row) + gap_x * (len(row) - 1)
        x = (page_w - tw) / 2.0
        for src, crop, whites, lab in row:
            if src not in docs:
                docs[src] = fitz.open(src)
            tgt = fitz.Rect(x, y, x + crop.width * scale, y + crop.height * scale)
            page.show_pdf_page(tgt, docs[src], 0, clip=crop)
            for wr in whites:
                white(page, fitz.Rect(tgt.x0 + (wr.x0 - crop.x0) * scale,
                                      tgt.y0 + (wr.y0 - crop.y0) * scale,
                                      tgt.x0 + (wr.x1 - crop.x0) * scale,
                                      tgt.y0 + (wr.y1 - crop.y0) * scale))
            if lab:
                text, dx, dy = lab
                stamp(page, tgt.x0 + dx, tgt.y0 + dy, text, label_pt)
            x += crop.width * scale + gap_x
        y += h + gap_y
    for wr in post_whites:                 # target-coordinate clean-ups
        white(page, fitz.Rect(*wr), pad=0.4)
    path = os.path.join(OUTDIR, out_name + '.pdf')
    out.save(path, deflate=True, garbage=4)
    out.close()
    for d in docs.values():
        d.close()
    doc = fitz.open(path)
    pg = doc[0]
    sizes = sorted({round(s['size'], 1)
                    for b in pg.get_text('dict')['blocks']
                    for l in b.get('lines', []) for s in l['spans']
                    if s['text'].strip()})
    print(f'{out_name}: {pg.rect.width * MM:.1f} x {pg.rect.height * MM:.1f} mm, '
          f'scale {scale}, sizes {sizes[:6]}{"..." if len(sizes) > 6 else ""}')
    doc.close()
    return path


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    R = fitz.Rect

    # ------------------------------------------------------------- figure 2
    f2, f3 = B('figure2'), B('figure3')
    C2a = (f2, R(6, 6, 252, 203), [R(16.1, 12.3, 27.1, 22.4)], ('(a)', 3, 12))
    C2b = (f2, R(252, 6, 502, 203), [R(261.4, 12.3, 272.9, 22.4)], ('(b)', 3, 12))
    C2c = (f2, R(6, 202, 229, 374), [R(16.1, 208.4, 27.1, 218.5)], None)
    C2d = (f2, R(229, 203, 502, 374), [R(250.8, 208.4, 262.3, 218.5)], ('(c)', 3, 12))
    C2e = (f2, R(6, 374, 502, 575.4), [R(16.1, 382.4, 27.1, 392.5)], ('(d)', 3, 12))

    # page width = widest row at 1.0x  (246+6+250 = 502 pt = 177.2 mm <= 178)
    compose('figure2',
            [[C2a, C2b], [C2d, C2c], [C2e]],
            page_w=502.0, scale=1.0, gap_x=6.0, gap_y=6.0, marg=4.0)

    # ------------------------------------------------- Supplementary Fig. 11
    C3a = (f3, R(8, 12, 260, 190), [R(6, 12, 34, 34)], ('(a)', 3, 12))
    C3c = (f3, R(618, 12, 945, 190), [R(655.8, 17.6, 666.8, 30.1)], ('(b)', 3, 12))
    C3b = (f3, R(276, 12, 618, 190), [R(306.1, 18.3, 317.3, 28.7)], ('(c)', 3, 12))
    # the artwork carries a stray full-width '(a）' (AdobeSongStd) inside the
    # first panel's title; cover it so the stamped (a) is the only letter
    compose('Supplementary_Fig_11',
            [[C3a], [C3c], [C3b]],
            page_w=492.567, scale=1.15, gap_x=6.0, gap_y=6.0, marg=4.0,
            post_whites=[(139.4, 10.8, 158.6, 23.6)])


if __name__ == '__main__':
    main()
