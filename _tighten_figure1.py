#!/usr/bin/env python3
"""Tighten the vertical spacing between panels of main Figure 1.

Input  : results/figures_v58_author/figure1.pdf  (first-author v6 vector PDF)
Output : same path (in place), with the three content bands re-stacked
         closer together.  A pristine copy of the original is saved to
         results/audit/figure1_author_v6_original.pdf on first run.

Method: band-level vector re-composition with PyMuPDF.  Nothing is
re-rendered: each content band is clipped from the source page and placed
1:1 on a new, shorter page, so type sizes / vector quality are untouched.

Band boundaries (pt, y-down) were measured by row-ink profiling at 150 dpi:
  band A  (Ka/Ks concept + formula box)      content 31.2 - 190.6
  band B  (four-step pipeline)               content 222.7 - 286.1
  band C  (panels c/d/e)                     content 301.4 - 457.0
Original inter-band gaps: 32.6 pt (A-B) and 15.8 pt (B-C); top margin 31.2 pt.
"""
import os
import shutil
import fitz

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'results', 'figures_v58_author', 'figure1.pdf')
BAK = os.path.join(BASE, 'results', 'audit', 'figure1_author_v6_original.pdf')

W = 481.8897705078125          # page width in pt (=170 mm), unchanged
MARGIN = 3.0                   # safety margin around each clipped band (pt)
TOP_PAD = 7.0                  # new top margin (pt)
INTER_GAP = 9.0                # new gap between bands (pt)
BOT_PAD = 6.0                  # new bottom margin (pt)

BANDS = [(31.2, 190.6),        # A: Ka/Ks concept + formula box
         (222.7, 286.1),       # B: pipeline
         (301.4, 457.0)]       # C: panels c/d/e


def main():
    if not os.path.exists(BAK):
        shutil.copy2(SRC, BAK)
        print('backup written:', BAK)

    src = fitz.open(SRC)
    sp = src[0]
    print(f'source page: {sp.rect.width:.1f} x {sp.rect.height:.1f} pt '
          f'({sp.rect.width/72*25.4:.1f} x {sp.rect.height/72*25.4:.1f} mm)')

    clips = []
    for y0, y1 in BANDS:
        clips.append((max(0.0, y0 - MARGIN), min(sp.rect.height, y1 + MARGIN)))

    y = TOP_PAD
    placements = []
    for cy0, cy1 in clips:
        placements.append((cy0, cy1, y))
        y += (cy1 - cy0) + INTER_GAP
    new_h = y - INTER_GAP + BOT_PAD

    out = fitz.open()
    page = out.new_page(width=W, height=new_h)
    for cy0, cy1, dy in placements:
        h = cy1 - cy0
        page.show_pdf_page(fitz.Rect(0, dy, W, dy + h), src, 0,
                           clip=fitz.Rect(0, cy0, W, cy1))
        print(f'  band clip y[{cy0:6.1f},{cy1:6.1f}] -> new y {dy:6.1f}..{dy+h:6.1f}')

    old_h = sp.rect.height
    tmp = SRC + '.tmp'
    out.save(tmp, deflate=True, garbage=4)
    out.close()
    src.close()
    os.replace(tmp, SRC)          # atomic overwrite once handles are closed
    print(f'output page: {W:.1f} x {new_h:.1f} pt '
          f'({W/72*25.4:.1f} x {new_h/72*25.4:.1f} mm)')
    print(f'height reduced by {old_h - new_h:.1f} pt '
          f'({(old_h - new_h)/old_h*100:.1f}%)')


if __name__ == '__main__':
    main()
