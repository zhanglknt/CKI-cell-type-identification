#!/usr/bin/env python3
"""v49.7: merge Figure 2 top row (A-C) with the natively regenerated
bottom row (D heatmap + E change-detection ROC) into the final NC Figure 2.

- Top:    results/figures_final/_fig2_toprow_nc49.pdf      (178 x 74 mm)
- Bottom: results/figures_final/_fig2_bottomrow_nc49.pdf   (178 x 72 mm,
          native panel labels D/E, Arial >= 7 pt)

Output: results/figures_final/figure2_merged_nc49.pdf
        results/audit/_merge_final.png (150 dpi preview)
"""
import sys
sys.path.insert(0, r'C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Lib\site-packages')
import fitz

TOP = 'results/figures_final/_fig2_toprow_nc49.pdf'
BOT = 'results/figures_final/_fig2_bottomrow_nc49.pdf'
OUT_PDF = 'results/figures_final/figure2_merged_nc49.pdf'
OUT_PNG = 'results/audit/_merge_final.png'

dt = fitz.open(TOP)
db = fitz.open(BOT)
pt, pb = dt[0], db[0]
print('top :', pt.rect, f'= {pt.rect.width/72*25.4:.1f} x {pt.rect.height/72*25.4:.1f} mm')
print('bot :', pb.rect, f'= {pb.rect.width/72*25.4:.1f} x {pb.rect.height/72*25.4:.1f} mm')
assert abs(pt.rect.width - pb.rect.width) < 0.5

W = pt.rect.width
gap = 6.0
h_top = pt.rect.height
h_bot = pb.rect.height
H = h_top + gap + h_bot

out = fitz.open()
page = out.new_page(width=W, height=H)
page.show_pdf_page(fitz.Rect(0, 0, W, h_top), dt, 0)
page.show_pdf_page(fitz.Rect(0, h_top + gap, W, H), db, 0)
out.save(OUT_PDF, deflate=True, garbage=3)
print(f'saved {OUT_PDF}: {W:.1f} x {H:.1f} pt = {W/72*25.4:.1f} x {H/72*25.4:.1f} mm')

# ---- audit -----------------------------------------------------------------
chk = fitz.open(OUT_PDF)
pg = chk[0]
sizes, fonts = {}, set()
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
print(f'mathtext sub/superscript spans (<7 pt): {sub}')

pix = pg.get_pixmap(dpi=150)
pix.save(OUT_PNG)
print('preview:', OUT_PNG, pix.width, 'x', pix.height)
