#!/usr/bin/env python3
"""nc84 supplementary-figure recomposition (vector re-layout, multi-page).

Why this exists
---------------
nc70 squeezed several author panels into a single 178 mm page.  The horizontal
scale factor fell to 0.55-0.77 and every lettering span shrank with it, so
Supplementary Figs 1/3/5 measured a *primary* size of 3.7 / 3.4 / 4.2 pt, below
the NC 5 pt floor.  Supplementary Fig 6 was forced through a documented
exception because most of its lettering is vector outlines.

What this script does
---------------------
Re-lays SF1, SF3 and SF5 from the pristine originals in nc70_backup/ as
multi-page PDFs.  ``show_pdf_page`` embeds each source page as a Form XObject,
so scaling is pure vector geometry: every span's effective size scales exactly
with the placement rectangle (verified: a 4.9 pt span renders at 2.9 / 7.4 /
9.8 pt for s = 0.6 / 1.5 / 2.0).  Each page therefore carries at most two blocks
(one or two original panel crops per row) at s = 1.0 -- i.e. the author's native
6.5-9 pt lettering -- which already clears 5 pt.  Three over-wide crops
(SF3 c = 891 pt, SF3 d = 800 pt, SF5 d = 549 pt) cannot fit inside one 180 mm
page at s = 1.0; they are split *at the author's own sub-panel seams* and each
half is placed on its own page.

SF6 is different: its source is the already-outlined (MyriadPro -> curves) build
shipped in CKI_Submission_NC/, where only a handful of mathtext ``_n``
subscripts survive as live text (3.3 / 4.1 / 5.0 pt).  We keep that single page
byte-for-byte except for lifting the two sub-5 pt subscripts to 5.0 pt in place
(redact text only, keep line art), which removes the last need for an exception.

Mapping (verified by token overlap against the shipped files, Jaccard = 1.000)
---------------------------------------------------------------------------
  SF1  <- nc70 compose 'figure_S1' = S1(a,b,c)  + S13(d,e)      + S14(f)
  SF3  <- nc70 compose 'figure_S2' = S2(a,b)    + S5(c,d)
  SF5  <- nc70 compose 'figure_S6' = S11(a,b)   + S12(c)        + S6(d)
(The nc70 script's own figure_S<N> filenames are offset from the submission
Supplementary_Fig_<M> numbering; SF3 is *not* nc70's figure_S3.)

Outputs: results/figures_nc84/Supplementary_Fig_{1,3,5,6}.pdf
Previews: results/audit/_nc84_previews/nc84_SF{N}_p{K}.png
"""
import os
import sys

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAK = os.path.join(BASE, 'results', 'audit', 'nc70_backup')
SUB = os.path.join(BASE, 'CKI_Submission_NC')
OUT = os.path.join(BASE, 'results', 'figures_nc84')
PREV = os.path.join(BASE, 'results', 'audit', '_nc84_previews')
ARIAL = 'C:/Windows/Fonts/arial.ttf'
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'

R = fitz.Rect
W = 504.567                 # 178 mm content measure used by nc70
ML, GX, GY = 6.0, 8.0, 6.0
MAXW_MM = 180.0
MAXH_MM = 280.0             # hard ceiling (task allows 280 mm when forced)
S_CAP = 1.0                 # default: never enlarge beyond native 1x
FLOOR = 5.0
SUB_RATIO = 0.80
SUB_FLOOR = 0.60


def B(name):
    return os.path.join(BAK, name + '.pdf')


# --------------------------------------------------------------------------- #
# checker-faithful span extraction / two-tier classification (identical maths
# to scripts/check_figure_spec.py, so the script's own assertions agree with it)
# --------------------------------------------------------------------------- #
def spans(page):
    out = []
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            for sp in line['spans']:
                if sp['text'].strip():
                    r = fitz.Rect(sp['bbox'])
                    out.append(dict(size=sp['size'], rect=r, text=sp['text'],
                                    color=sp['color'], origin=tuple(sp['origin'])))
    return out


def classify(items, dy=5.0, dx=150.0, ratio=SUB_RATIO):
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
        (sub if s['size'] <= ratio * base + 1e-6 else primary).append(s)
    return primary, sub


def rgb(srgb):
    return (((srgb >> 16) & 255) / 255.0, ((srgb >> 8) & 255) / 255.0,
            (srgb & 255) / 255.0)


# --------------------------------------------------------------------------- #
# block = (src_stem, crop, whites, stamp, force_s)
#   stamp = (text, dx, dy, size) or None ; dx/dy/size are in *crop* points and
#   are multiplied by s so the letter keeps its position/size relative to panel.
#   force_s = None -> derive s from the page width; else use exactly this s.
# --------------------------------------------------------------------------- #
def _b(*t):
    if len(t) == 4:
        t = t + (None,)
    return t


def row_scale(row):
    forced = [b[4] for b in row if len(b) > 4 and b[4] is not None]
    if forced:
        return min(forced)
    tw = sum(b[1].width for b in row)
    return min(S_CAP, (W - 2 * ML - GX * (len(row) - 1)) / tw)


def compose(pages):
    srcdocs = {}
    doc = fitz.open()
    for rows in pages:
        metas = []
        for row in rows:
            s = row_scale(row)
            h = max(b[1].height for b in row) * s
            w = sum(b[1].width for b in row) * s + GX * (len(row) - 1) + 2 * ML
            metas.append((row, s, h, w))
        page_w = max(m[3] for m in metas)
        page_h = ML + sum(m[2] for m in metas) + GY * (len(metas) - 1) + ML
        page = doc.new_page(width=page_w, height=page_h)
        y = ML
        for row, s, h, w in metas:
            tw = sum(b[1].width for b in row) * s + GX * (len(row) - 1)
            x = (page_w - tw) / 2.0
            for src, crop, whites, stamp, _fs in row:
                if src not in srcdocs:
                    srcdocs[src] = fitz.open(B(src))
                tgt = R(x, y, x + crop.width * s, y + crop.height * s)
                page.show_pdf_page(tgt, srcdocs[src], 0, clip=crop)
                for wr in whites:
                    mr = R(tgt.x0 + (wr.x0 - crop.x0) * s,
                           tgt.y0 + (wr.y0 - crop.y0) * s,
                           tgt.x0 + (wr.x1 - crop.x0) * s,
                           tgt.y0 + (wr.y1 - crop.y0) * s)
                    page.draw_rect(R(mr.x0 - 1.2, mr.y0 - 1.2,
                                     mr.x1 + 1.2, mr.y1 + 1.2),
                                   color=None, fill=(1, 1, 1), overlay=True)
                if stamp:
                    text, dx, dy, size = stamp
                    page.insert_text((tgt.x0 + dx * s, tgt.y0 + dy * s), text,
                                     fontname='ArB', fontfile=ARIALBD,
                                     fontsize=size * s, color=(0, 0, 0))
                x += crop.width * s + GX
            y += h + GY
    for d in srcdocs.values():
        d.close()
    return doc


# --------------------------------------------------------------------------- #
# figure definitions (crop/white/stamp copied verbatim from _nc70_suppfigs.py,
# only regrouped into <=2 blocks per page and split at sub-panel seams)
# --------------------------------------------------------------------------- #
def build_sf1():
    """6 panels, every crop < 492 pt -> s = 1.0 on 2-block pages."""
    return [
        [[_b('figure_S1', R(2, 0, 325, 251), [R(32.5, 0.1, 44.7, 13.9)], ('(a)', 3, 12, 9))],
         [_b('figure_S1', R(325, 0, 628, 251), [R(363.7, 0.1, 376.5, 13.9)], ('(b)', 3, 12, 9))]],
        [[_b('figure_S1', R(628, 0, 1002, 251), [R(714.5, 0.1, 726.7, 13.9)], ('(c)', 3, 12, 9))],
         [_b('figure_S13', R(7, 0, 248, 197), [R(32.1, 2.9, 48.0, 15.4)], ('(d)', 18.1, 13.2, 9))]],
        [[_b('figure_S13', R(266, 0, 499, 197), [R(282.8, 2.9, 297.0, 15.4)], ('(e)', 9.8, 13.2, 9))],
         [_b('figure_S14', R(7, 7, 499, 497), [], ('(f)', 3, 12, 9))]],
    ]


def build_sf3():
    """(a)(b) native S2; (c)/(d) from S5 split at the matrix/bar seam x=492."""
    cut = 492.0
    return [
        [[_b('figure_S2', R(20, 2, 295, 200), [], None)],
         [_b('figure_S2', R(295, 2, 540, 200), [], None)]],
        [[_b('figure_S5', R(0, 0, cut, 169), [R(2.8, 2.8, 14.5, 16.7)], ('(c)', 3, 12, 9))],
         [_b('figure_S5', R(cut, 0, 891, 169), [], None)]],
        [[_b('figure_S5', R(0, 169, cut, 362), [R(2.4, 170.4, 14.8, 184.3)], ('(d)', 3, 12, 9))],
         [_b('figure_S5', R(cut, 169, 800, 362), [], None)]],
    ]


def build_sf5():
    """(a)(b) S11, (c) S12 (outlines), (d) S6 split at the author's own dashed
    blue/grey seam x=200 (between hepatocyte and B cell).  The (d) halves are
    enlarged to s=1.3 so the rotated y-axis-title fragments the PDF reports at
    4.0 pt clear 5 pt (4.0 -> 5.2)."""
    cut = 200.0
    return [
        [[_b('figure_S11', R(17, 5, 240, 225), [], ('(a)', 3, 12, 9))],
         [_b('figure_S11', R(264, 5, 487, 225), [], ('(b)', 3, 12, 9))]],
        [[_b('figure_S12', R(29, 29, 382, 554), [], ('(c)', 3, 12, 9))]],
        [[_b('figure_S6', R(0, 0, cut, 313),
             [R(29.5, 0.0, 41.3, 13.2), R(29.5, 138.1, 41.7, 153.2)],
             ('(d)', 3, 12, 9), 1.3)]],
        [[_b('figure_S6', R(cut, 0, 549, 313), [], None, 1.3)]],
    ]


# --------------------------------------------------------------------------- #
# SF6: keep the shipped outlined single page, lift only the two live sub-5 pt
# subscripts to 5.0 pt in place.
# --------------------------------------------------------------------------- #
def lift_small_text(page, lift_size=5.5, threshold=None):
    """Re-stamp every live text span below ``threshold`` at ``lift_size``.

    The shipped SF6 has six MyriadPro ``_n`` subscripts the PDF reports at
    3.3 / 4.1 / 4.95 pt (the "5.0" ones measure 4.953 because of the font's em
    scaling).  Lifting them all to 5.5 pt removes the 4.95 rounding knife-edge
    and leaves a comfortable margin.  Only the text layer is redacted -- line
    art (the outlined MyriadPro lettering) is preserved via
    PDF_REDACT_LINE_ART_NONE.
    """
    if threshold is None:
        threshold = lift_size
    items = spans(page)
    targets = [s for s in items if s['size'] < threshold - 1e-6]
    if not targets:
        return []
    for s in targets:
        r = s['rect']
        page.add_redact_annot(R(r.x0 - 0.8, r.y0 - 1.0, r.x1 + 0.8, r.y1 + 1.0))
    kw = {}
    for key, val in (('images', 'PDF_REDACT_IMAGE_NONE'),
                     ('graphics', 'PDF_REDACT_LINE_ART_NONE'),
                     ('text', 'PDF_REDACT_TEXT_REMOVE')):
        if hasattr(fitz, val):
            kw[key] = getattr(fitz, val)
    page.apply_redactions(**kw)
    for s in targets:
        txt = s['text'].lstrip('_') or s['text']
        page.insert_text(s['origin'], txt, fontname='ArR', fontfile=ARIAL,
                         fontsize=lift_size, color=rgb(s['color']))
    return targets


def build_sf6():
    doc = fitz.open(os.path.join(SUB, 'Supplementary_Fig_6.pdf'))
    targets = lift_small_text(doc[0], lift_size=5.5, threshold=5.5)
    print(f'  SF6: lifted {len(targets)} sub-5.5pt subscripts to 5.5 pt')
    return doc


# --------------------------------------------------------------------------- #
# verification
# --------------------------------------------------------------------------- #
def verify(name, doc, expect_pages=None):
    maxw = 0.0
    all_p, all_s = [], []
    rows = []
    for i, page in enumerate(doc):
        w = page.rect.width / 72 * 25.4
        h = page.rect.height / 72 * 25.4
        maxw = max(maxw, w)
        assert w <= MAXW_MM + 0.05, f'{name} page {i}: width {w:.1f} mm > {MAXW_MM}'
        assert h <= MAXH_MM + 0.05, f'{name} page {i}: height {h:.1f} mm > {MAXH_MM}'
        primary, sub = classify(spans(page))
        all_p += [s['size'] for s in primary]
        all_s += [s['size'] for s in sub]
        rows.append(dict(page=i, w_mm=round(w, 1), h_mm=round(h, 1),
                         p_min=round(min(s['size'] for s in primary), 2) if primary else None,
                         s_min=round(min(s['size'] for s in sub), 2) if sub else None,
                         n_primary=len(primary), n_sub=len(sub)))
    p_min = min(all_p) if all_p else None
    s_min = min(all_s) if all_s else None
    assert p_min is not None and p_min >= FLOOR - 0.05, f'{name}: primary min {p_min} < {FLOOR}'
    if s_min is not None:
        assert s_min >= SUB_FLOOR * p_min - 1e-6, f'{name}: sub min {s_min} < 60% of {p_min}'
    assert len(doc) >= 1
    if expect_pages is not None:
        assert len(doc) == expect_pages, f'{name}: pages {len(doc)} != {expect_pages}'
    return dict(name=name, pages=len(doc), maxw_mm=round(maxw, 1),
                p_min=round(p_min, 2), s_min=None if s_min is None else round(s_min, 2),
                rows=rows)


def save_and_preview(name, doc):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    path = os.path.join(OUT, name)
    doc.save(path, deflate=True, garbage=4)
    size_kb = os.path.getsize(path) / 1024.0
    if size_kb > 10 * 1024:
        print(f'  WARNING {name}: {size_kb/1024:.1f} MB > 10 MB')
    return path, size_kb


def main():
    specs = [
        ('Supplementary_Fig_1.pdf', build_sf1, 'SF1'),
        ('Supplementary_Fig_3.pdf', build_sf3, 'SF3'),
        ('Supplementary_Fig_5.pdf', build_sf5, 'SF5'),
        ('Supplementary_Fig_6.pdf', build_sf6, 'SF6'),
    ]
    summary = []
    for fname, builder, tag in specs:
        built = builder()
        doc = compose(built) if isinstance(built, list) else built
        info = verify(tag, doc)
        path, size_kb = save_and_preview(fname, doc)
        # previews
        for i, page in enumerate(doc):
            page.get_pixmap(dpi=110).save(
                os.path.join(PREV, f'nc84_{tag}_p{i + 1}.png'))
        doc.close()
        info['file'] = path
        info['size_kb'] = round(size_kb, 1)
        summary.append(info)
        print(f'{tag}: {info["pages"]} page(s), max width {info["maxw_mm"]} mm, '
              f'primary min {info["p_min"]} pt, sub min {info["s_min"]} pt, '
              f'{size_kb:.0f} KB')
        for r in info['rows']:
            print(f'    p{r["page"] + 1}: {r["w_mm"]} x {r["h_mm"]} mm  '
                  f'primary>={r["p_min"]} sub>={r["s_min"]}  '
                  f'({r["n_primary"]} pri / {r["n_sub"]} sub)')
    print('\nAll assertions passed.')
    return summary


if __name__ == '__main__':
    main()
