import sys, collections
sys.path.insert(0, r'C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Lib\site-packages')
import fitz

SCALE = 0.7585  # top-row scale in merged layout

d = fitz.open('results/figures_submission_nc/figure2.pdf')
p = d[0]
print('page rect:', p.rect)

hs = collections.Counter()
for dr in p.get_drawings():
    if dr['type'] not in ('f', 'fs'):
        continue
    r = dr['rect']
    h, w = r.height, r.width
    if 1.0 <= h <= 12.0 and 0.3 <= w <= 10.0:  # glyph-sized outlines
        hs[round(h, 1)] += 1

print('glyph-height histogram (top 25):')
for h, c in hs.most_common(25):
    fs = h / 0.7  # cap-height ~ 0.7 * font size
    print(f'  h={h:5.1f}pt n={c:4d}  ~fontsize={fs:4.1f}pt  effective={fs*SCALE:4.1f}pt')

# robust summary: weighted median-ish buckets
small = sum(c for h, c in hs.items() if h / 0.7 * SCALE < 7.0)
big = sum(c for h, c in hs.items() if h / 0.7 * SCALE >= 7.0)
print(f'\nglyph outlines effective <7pt: {small}   >=7pt: {big}')
