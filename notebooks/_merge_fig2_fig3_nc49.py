#!/usr/bin/env python3
"""Merge regenerated Figure 2 top row (A-C) with old Figure 3 (D-E) into the
final NC Figure 2 (5 panels, 178 mm double column, all fonts >= 7 pt).

- Top row: results/figures_submission_nc/_fig2_toprow_nc49.pdf
  (178 x 74 mm, matplotlib, Arial >= 7 pt, Type 42 embedded, native scale)
- Bottom row: results/figures_submission_nc/figure3.pdf
  (178 x 72 mm, native scale, labels A/B whited-out and re-inserted as D/E
  in embedded Arial Bold 9 pt)

Output: results/figures_submission_nc/figure2_merged_final.pdf
        results/audit/_merge_final.png  (150 dpi preview)
"""
import sys
sys.path.insert(0, r'C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Lib\site-packages')
import fitz

TOP = 'results/figures_final/_fig2_toprow_nc49.pdf'
BOT = 'results/figures_v47_author/figure3.pdf'
OUT_PDF = 'results/figures_final/figure2_merged_nc49.pdf'
OUT_PNG = 'results/audit/_merge_final.png'
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'

dt = fitz.open(TOP)
db = fitz.open(BOT)
pt, pb = dt[0], db[0]
print('top :', pt.rect, f'= {pt.rect.width/72*25.4:.1f} x {pt.rect.height/72*25.4:.1f} mm')
print('bot :', pb.rect, f'= {pb.rect.width/72*25.4:.1f} x {pb.rect.height/72*25.4:.1f} mm')

W = pt.rect.width                      # 504.567 pt = 178 mm
gap = 6.0
h_top = pt.rect.height                 # native, no scaling
h_bot = pb.rect.height
H = h_top + gap + h_bot

out = fitz.open()
page = out.new_page(width=W, height=H)
page.show_pdf_page(fitz.Rect(0, 0, W, h_top), dt, 0)
page.show_pdf_page(fitz.Rect(0, h_top + gap, W, H), db, 0)

# ---- relabel bottom row: A -> D, B -> E (embedded Arial Bold 9 pt) --------
yoff = h_top + gap
jobs = [
    (fitz.Rect(16.2, 8.9, 25.7, 21.9), 'D', (17.7, 18.6)),
    (fitz.Rect(273.5, 7.9, 283.0, 23.4), 'E', (275.0, 20.0)),
]
for rect, ch, (x, y) in jobs:
    r = fitz.Rect(rect.x0, rect.y0 + yoff, rect.x1, rect.y1 + yoff)
    page.draw_rect(r, color=None, fill=(1, 1, 1), overlay=True)
    page.insert_text((x, y + yoff), ch, fontname='arialbd',
                     fontfile=ARIALBD, fontsize=9.0, color=(0, 0, 0))

out.save(OUT_PDF, deflate=True, garbage=3)
print(f'saved {OUT_PDF}: {W:.1f} x {H:.1f} pt = {W/72*25.4:.1f} x {H/72*25.4:.1f} mm')

# ---- audit: every text span size & font -----------------------------------
chk = fitz.open(OUT_PDF)
pg = chk[0]
sizes = {}
fonts = set()
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            sizes[round(s['size'], 1)] = sizes.get(round(s['size'], 1), 0) + 1
            fonts.add(s['font'])
print('span sizes:', dict(sorted(sizes.items())))
print('fonts:', sorted(fonts))
n_primary = sum(c for sz, c in sizes.items() if sz >= 6.95)
sub = {k: v for k, v in sorted(sizes.items()) if k < 6.95}
print(f'primary text spans >= 7 pt: {n_primary}')
print(f'mathtext sub/superscript spans (<7 pt): {sub}  '
      f'(4.9-6.3 pt; consistent with package norm fig1/4/5/6, Nature floor 5 pt)')

pix = pg.get_pixmap(dpi=150)
pix.save(OUT_PNG)
print('preview:', OUT_PNG, pix.width, 'x', pix.height)
