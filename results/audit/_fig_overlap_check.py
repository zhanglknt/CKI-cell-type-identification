#!/usr/bin/env python3
"""Programmatic layout check for a figure PDF.

Checks:
  1. text-vs-text overlap  (intersection >= 15% of the smaller span box).
     Rotated tick labels are resolved geometrically: two parallel slanted bars
     are separated along their normal by dx*sin(theta), so an axis-aligned box
     intersection is NOT a visual overlap when that separation exceeds the
     glyph height.  Wrapped lines of one label share the same anchor (dx ~ 0).
  2. text overflowing the page rectangle
  3. font inventory and span-size histogram (NC floor: body text >= 7 pt)

Usage: python results/audit/_fig_overlap_check.py <pdf>
"""
import sys
import math
import fitz

PDF = sys.argv[1]

doc = fitz.open(PDF)
pg = doc[0]
PR = pg.rect
print(PDF)
print(f'page: {PR.width/72*25.4:.1f} x {PR.height/72*25.4:.1f} mm')


def anchor_x(span, bbox):
    org = span.get('origin')
    if org:
        return org[0]
    return bbox[0]


# span = (text, rect, size_pt, angle_deg, anchor_x)
spans = []
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        d = l.get('dir', (1, 0))
        ang = abs(math.degrees(math.atan2(d[1], d[0])))
        for s in l['spans']:
            txt = s['text'].strip()
            if not txt:
                continue
            rect = fitz.Rect(s['bbox'])
            spans.append((txt, rect, round(s['size'], 1), ang, anchor_x(s, rect)))
print(f'text spans: {len(spans)}')


def rotated_benign(sz1, sz2, ox1, ox2, ang):
    if ang < 15:
        return False
    dx = abs(ox1 - ox2)
    if dx < 1.0:                       # second line of one wrapped label
        return True
    sep = dx * math.sin(math.radians(ang))
    return sep > max(sz1, sz2) * 0.9   # pt vs pt


# ---- 1. text vs text --------------------------------------------------------
bad, benign = [], []
for i in range(len(spans)):
    for j in range(i + 1, len(spans)):
        t1, r1, s1, a1, o1 = spans[i]
        t2, r2, s2, a2, o2 = spans[j]
        inter = r1 & r2
        if inter.is_empty:
            continue
        frac = inter.get_area() / min(r1.get_area(), r2.get_area())
        if frac < 0.15:
            continue
        item = (round(frac, 2), t1[:34], t2[:34], round(a1))
        if rotated_benign(s1, s2, o1, o2, max(a1, a2)):
            benign.append(item)
        else:
            bad.append(item)
print(f'\n[1] text-vs-text overlaps: {len(bad)} real / {len(benign)} benign'
      f' (rotated labels, normal separation > glyph height)')
for frac, a, b_, ang in sorted(bad, reverse=True)[:20]:
    print(f'    REAL   {frac:>5} ({ang}deg)  {a!r} vs {b_!r}')
for frac, a, b_, ang in sorted(benign, reverse=True)[:12]:
    print(f'    benign {frac:>5} ({ang}deg)  {a!r} vs {b_!r}')

# ---- 2. page overflow -------------------------------------------------------
out = [(t, r) for t, r, s, a, o in spans
       if r.x0 < PR.x0 - 0.5 or r.y0 < PR.y0 - 0.5
       or r.x1 > PR.x1 + 0.5 or r.y1 > PR.y1 + 0.5]
print(f'\n[2] spans outside page: {len(out)}')
for t, r in out[:10]:
    print(f'    {t!r} box=({r.x0:.0f},{r.y0:.0f},{r.x1:.0f},{r.y1:.0f})')

# ---- 3. sizes / fonts -------------------------------------------------------
sizes, fonts = {}, set()
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            sizes[round(s['size'], 1)] = sizes.get(round(s['size'], 1), 0) + 1
            fonts.add(s['font'])
print('\n[3] span sizes:', dict(sorted(sizes.items())))
print('    fonts:', sorted(fonts))
print('    sub-7pt:', {k: v for k, v in sorted(sizes.items()) if k < 6.95})
