#!/usr/bin/env python3
"""Figure specification checker for the NC submission package (v2, nc83).

Two-tier typography rule
------------------------
NC asks for sans-serif lettering in the 5-7 pt range at final size.  Judging
*every* span against 7 pt is stricter than the journal and impossible to meet
for any figure that carries mathtext: a 7 pt label renders its sub/superscripts
at about 4.9 pt by typographic convention.  So the checker separates

  * primary text   - the largest span of each visual line  -> must be >= 7 pt
                     for main figures and >= 5 pt for supplementary figures;
  * sub/superscript - spans <= 0.80x the primary of their own visual line ->
                     reported, and required only to stay >= 0.6x the primary.

Widths are still the hard constraint (<= 180 mm, i.e. the two-column measure).

Usage:  python scripts/check_figure_spec.py [--max-mm 180] [--main-min 7.0]
                                            [--supp-min 5.0] [--pkg DIR]
Exit code 0 when every figure passes, 1 otherwise.
"""
import argparse
import glob
import json
import os
import sys

import fitz

PKG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'CKI_Submission_NC')

SUB_RATIO = 0.80          # <= this x primary  ->  sub/superscript
SUB_FLOOR_RATIO = 0.60    # sub/superscript must stay above this x primary


def spans(page):
    out = []
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                if span['text'].strip():
                    r = fitz.Rect(span['bbox'])
                    out.append(dict(size=span['size'], rect=r,
                                    cy=(r.y0 + r.y1) / 2.0))
    return out


def classify(items, dy=5.0, dx=150.0, ratio=SUB_RATIO):
    """Split spans into primary text and mathtext sub/superscripts.

    A span is a sub/superscript when a span at least 1/ratio times its size sits
    within a small window around it (same visual line, allow for the raised or
    lowered baseline).  This is deliberately window-based rather than
    block-based: matplotlib emits every mathtext fragment as its own span, and
    often as its own block, so block identity carries no information here.
    """
    primary, sub = [], []
    for s in items:
        r = s['rect']
        base = s['size']
        for o in items:
            if o is s:
                continue
            q = o['rect']
            if abs((q.y0 + q.y1) / 2.0 - (r.y0 + r.y1) / 2.0) > dy:
                continue
            gap = max(r.x0 - q.x1, q.x0 - r.x1)
            if gap > dx:
                continue
            if o['size'] > base:
                base = o['size']
        (sub if s['size'] <= ratio * base + 1e-6 else primary).append(s['size'])
    return primary, sub


def ink_bbox(page):
    box = None
    for block in page.get_text('dict')['blocks']:
        r = fitz.Rect(block['bbox'])
        if r.is_empty or r.is_infinite:
            continue
        box = r if box is None else box | r
    for d in page.get_drawings():
        r = d['rect']
        if r.is_empty or r.is_infinite:
            continue
        box = r if box is None else box | r
    return box


def check(path, max_mm, floor):
    """Per-page check (nc84): a multi-page supplementary figure is judged over
    all its pages at once.

    Every page is classified independently (so spans from different pages never
    influence each other's primary/sub decision), then the primary and sub size
    lists are pooled.  The reported primary / sub minima are the minima of the
    pooled lists, and the width is the widest page.  This keeps the two-tier
    typography rule while allowing a figure to be split across several pages.
    """
    doc = fitz.open(path)
    all_primary, all_sub = [], []
    width_mm = 0.0
    height_mm = 0.0
    box = None
    for page in doc:
        width_mm = max(width_mm, page.rect.width / 72 * 25.4)
        height_mm = max(height_mm, page.rect.height / 72 * 25.4)
        primary, sub = classify(spans(page))
        all_primary += primary
        all_sub += sub
        b = ink_bbox(page)
        if b is not None:
            box = b if box is None else (box | b)
    scale = min(1.0, max_mm / width_mm) if width_mm else 1.0
    p_min = min(all_primary) * scale if all_primary else None
    s_min = min(all_sub) * scale if all_sub else None
    width_ok = width_mm <= max_mm + 0.5
    font_ok = p_min is not None and p_min >= floor - 0.05
    sub_ok = s_min is None or p_min is None or s_min >= SUB_FLOOR_RATIO * p_min
    return dict(name=os.path.basename(path), pages=len(doc),
                width_mm=width_mm, height_mm=height_mm, scale=scale,
                n_text=len(all_primary) + len(all_sub),
                n_primary=len(all_primary), n_sub=len(all_sub),
                p_min=p_min, s_min=s_min, floor=floor,
                p_max=max(all_primary) * scale if all_primary else None,
                width_ok=width_ok, font_ok=font_ok, sub_ok=sub_ok,
                ink=[round(v / 72 * 25.4, 1) for v in box] if box else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-mm', type=float, default=180.0)
    ap.add_argument('--main-min', type=float, default=7.0)
    ap.add_argument('--supp-min', type=float, default=5.0)
    ap.add_argument('--pkg', default=PKG)
    ap.add_argument('--exceptions', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'results', 'audit', '_nc83_figure_exceptions.json'),
        help='JSON of documented per-figure exceptions (name -> {why, reviewed})')
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.pkg, 'figure[0-9]*.pdf')))
    paths += sorted(glob.glob(os.path.join(args.pkg, 'Supplementary_Fig_*.pdf')))
    if not paths:
        print('no figure PDFs found in', args.pkg)
        return 1

    exc = {}
    if os.path.exists(args.exceptions):
        exc = json.load(open(args.exceptions, encoding='utf-8'))
    bad = 0
    print(f"{'figure':<28}{'mm (w x h)':<18}{'pg':>4}{'floor':>6}{'primary':>9}"
          f"{'sub':>7}{'n pri':>7}{'n sub':>7}   status")
    for p in paths:
        name = os.path.basename(p)
        floor = args.main_min if name.startswith('figure') else args.supp_min
        r = check(p, args.max_mm, floor)
        flags = []
        if not r['width_ok']:
            flags.append('WIDTH')
        if not r['font_ok']:
            flags.append('TYPE')
        if not r['sub_ok']:
            flags.append('SUB')
        status = ','.join(flags) if flags else 'ok'
        # nc84: documented exceptions are deliberately NOT consulted.  A
        # TYPE/SUB failure can never be upgraded to 'ok' by an entry in the
        # exceptions file -- the file is a leftover audit artefact (now `{}`).
        bad += bool(flags)
        print(f"{name:<28}{r['width_mm']:6.1f} x {r['height_mm']:6.1f}   "
              f"{r['pages']:>3d}{r['floor']:6.1f}{r['p_min']:9.1f}"
              f"{(r['s_min'] if r['s_min'] is not None else float('nan')):7.1f}"
              f"{r['n_primary']:7d}{r['n_sub']:7d}   "
              f"{status}")
    print(f"\n{len(paths) - bad}/{len(paths)} pass; width <= {args.max_mm:.0f} mm, "
          f"primary >= {args.main_min:.0f} pt (main) / {args.supp_min:.0f} pt "
          f"(supplementary), sub/superscripts >= {SUB_FLOOR_RATIO:.0%} of their line")
    print('note: "sub" counts mathtext sub/superscripts only; they are compared '
          'against their own line, not against the 7 pt floor.')
    if exc:
        print(f'documented exceptions ({len(exc)}):')
        for k, v in exc.items():
            print(f'  {k}: {v["why"][:110]}...')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
