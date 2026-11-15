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


# span = (text, rect, size_pt, angle_deg, signed_dir, centre)
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
            ctr = ((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2)
            spans.append((txt, rect, round(s['size'], 1), ang, d, ctr))
print(f'text spans: {len(spans)}')


def rotated_benign(sz1, sz2, ang, d1, d2, c1, c2):
    """Two parallel slanted glyph bands only touch when their perpendicular
    separation is below the glyph height.  Perpendicular distance between the
    two band centrelines = |(c2 - c1) x dir| with the SIGNED text direction.
    This covers both neighbours along one axis (offset runs along the axis,
    perpendicular part = spacing * sin(theta)) and the two lines of one wrapped
    label (offset = one line spacing, perpendicular part ~ 1.2 * size).
    An axis-aligned box intersection is therefore NOT a visual overlap."""
    if ang < 15:
        return False
    dx, dy = d1 if abs(d1[0]) >= abs(d2[0]) else d2
    sep = abs((c2[0] - c1[0]) * dy - (c2[1] - c1[1]) * dx)
    return sep > max(sz1, sz2) * 0.9   # pt vs pt


# ---- 1. text vs text --------------------------------------------------------
bad, benign = [], []
for i in range(len(spans)):
    for j in range(i + 1, len(spans)):
        t1, r1, s1, a1, d1, c1 = spans[i]
        t2, r2, s2, a2, d2, c2 = spans[j]
        inter = r1 & r2
        if inter.is_empty:
            continue
        frac = inter.get_area() / min(r1.get_area(), r2.get_area())
        if frac < 0.15:
            continue
        item = (round(frac, 2), t1[:34], t2[:34], round(a1))
        if rotated_benign(s1, s2, max(a1, a2), d1, d2, c1, c2):
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
out = [(t, r) for t, r, s, a, d, c in spans
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
