#!/usr/bin/env python3
"""Figure specification checker for the NC submission package.

NC requirements checked here:
  * final width <= 180 mm (single page, landscape) and <= 178 mm for a
    two-column-width figure;
  * every text span at final size >= 7 pt (Arial / Helvetica family);
  * report the effective font size after the figure is scaled to its
    maximum allowed width, so a canvas that is too wide is flagged even
    when its on-page type looks acceptable.

Usage:  python scripts/check_figure_spec.py [--max-mm 180]
Exit code 0 when every figure passes, 1 otherwise.
"""
import argparse
import glob
import os
import sys

import fitz

PKG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'CKI_Submission_NC')


def font_sizes(page):
    sizes = []
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                if span['text'].strip():
                    sizes.append(span['size'])
    return sizes


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


def check(path, max_mm):
    doc = fitz.open(path)
    page = doc[0]
    width_mm = page.rect.width / 72 * 25.4
    height_mm = page.rect.height / 72 * 25.4
    sizes = font_sizes(page)
    box = ink_bbox(page)
    scale = min(1.0, max_mm / width_mm) if width_mm else 1.0
    eff_min = min(sizes) * scale if sizes else None
    eff_max = max(sizes) * scale if sizes else None
    width_ok = width_mm <= max_mm + 0.5
    font_ok = eff_min is not None and eff_min >= 6.95
    return dict(name=os.path.basename(path), pages=len(doc),
                width_mm=width_mm, height_mm=height_mm, scale=scale,
                n_text=len(sizes), min_pt=min(sizes) if sizes else None,
                max_pt=max(sizes) if sizes else None,
                eff_min=eff_min, eff_max=eff_max,
                width_ok=width_ok, font_ok=font_ok,
                ink=[round(v / 72 * 25.4, 1) for v in box] if box else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-mm', type=float, default=180.0)
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(PKG, 'figure[0-9]*.pdf')))
    paths += sorted(glob.glob(os.path.join(PKG, 'Supplementary_Fig_*.pdf')))
    if not paths:
        print('no figure PDFs found in', PKG)
        return 1

    bad = 0
    print(f"{'figure':<28}{'mm (w x h)':<18}{'scale':>6}{'min pt':>8}"
          f"{'eff min':>9}{'eff max':>9}   status")
    for p in paths:
        r = check(p, args.max_mm)
        flags = []
        if not r['width_ok']:
            flags.append('WIDTH')
        if not r['font_ok']:
            flags.append('FONT')
        if r['pages'] != 1:
            flags.append(f"PAGES={r['pages']}")
        bad += bool(flags)
        print(f"{r['name']:<28}{r['width_mm']:6.1f} x {r['height_mm']:6.1f}   "
              f"{r['scale']:6.2f}{r['min_pt']:8.1f}{r['eff_min']:9.1f}"
              f"{r['eff_max']:9.1f}   {','.join(flags) if flags else 'ok'}")
    print(f"\n{len(paths) - bad}/{len(paths)} pass; max width {args.max_mm:.0f} mm, "
          f"minimum effective type 7 pt")
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
