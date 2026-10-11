#!/usr/bin/env python3
"""nc70 supplementary-figure consolidation (19 -> 9, panels 4 or 6).

Vector band re-composition (PyMuPDF show_pdf_page clips; no re-render).
Sources: pristine originals in results/audit/nc70_backup/.
Outputs: results/figures_v58_author/figure_S1.pdf .. figure_S9.pdf.

Mapping (letters kept stable where possible):
  SF1 = S1(a,b,c) + S13(a,b -> d,e) + S14(-> f)
  SF2 = S2(a,b)     + S5(a,b -> c,d)
  SF3 = S3(a,b,c)   + S4(a,b merged -> d)
  SF4 = S7(a,b,c)   + S8(a,b merged -> d)
  SF5 = S9(a,b,c)   + S10(a,b merged -> d)
  SF6 = S11(new a,b)+ S12(-> c)       + S6(merged -> d)
  SF7 = S15(a,b,c)  + S16(a,b,c -> d,e,f)
  SF8 = S17(a,b)    + S18(a,b -> c,d)
  SF9 = S19 (unchanged)
"""
import os
import shutil
import fitz

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(BASE, 'results', 'figures_v58_author')
BAK = os.path.join(BASE, 'results', 'audit', 'nc70_backup')
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'

W = 504.567
ML, GX, GY = 6.0, 8.0, 6.0


def B(name):
    return os.path.join(BAK, name + '.pdf')


# cell: (src, crop, [(white_rect), ...], (stamp_text, dx, dy_baseline, size) or None)
def compose(out_name, rows, scale_caps):
    docs = {}
    caps_iter = iter(scale_caps)
    meta = []
    for row in rows:
        cap = next(caps_iter)
        tw = sum(c[1].width for c in row)
        s = min(cap, (W - 2 * ML - GX * (len(row) - 1)) / tw)
        h = max(c[1].height for c in row) * s
        meta.append((s, h))
    H = ML + sum(h for _, h in meta) + GY * (len(rows) - 1) + ML
    out = fitz.open()
    page = out.new_page(width=W, height=H)
    y = ML
    for row, (s, h) in zip(rows, meta):
        tw = sum(c[1].width for c in row) * s + GX * (len(row) - 1)
        x = (W - tw) / 2
        for src, crop, whites, stamp in row:
            if src not in docs:
                docs[src] = fitz.open(src)
            tgt = fitz.Rect(x, y, x + crop.width * s, y + crop.height * s)
            page.show_pdf_page(tgt, docs[src], 0, clip=crop)
            for wr in whites:
                mr = fitz.Rect(tgt.x0 + (wr.x0 - crop.x0) * s,
                               tgt.y0 + (wr.y0 - crop.y0) * s,
                               tgt.x0 + (wr.x1 - crop.x0) * s,
                               tgt.y0 + (wr.y1 - crop.y0) * s)
                page.draw_rect(fitz.Rect(mr.x0 - 1.2, mr.y0 - 1.2,
                                         mr.x1 + 1.2, mr.y1 + 1.2),
                               color=None, fill=(1, 1, 1), overlay=True)
            if stamp:
                text, dx, dy, size = stamp
                page.insert_text((tgt.x0 + dx, tgt.y0 + dy), text,
                                 fontname='arialbd', fontfile=ARIALBD,
                                 fontsize=size, color=(0, 0, 0))
            x += crop.width * s + GX
        y += h + GY
    out.save(os.path.join(STAGE, out_name + '.pdf'), deflate=True, garbage=4)
    for d in docs.values():
        d.close()
    out.close()
    print(f'{out_name}: {W/72*25.4:.0f} x {H/72*25.4:.0f} mm, {len(rows)} rows')


def main():
    R = fitz.Rect

    # ---------------- SF1 = S1(a,b,c) + S13(d,e) + S14(f) ----------------
    compose('figure_S1', [
        [(B('figure_S1'), R(2, 0, 325, 251), [R(32.5, 0.1, 44.7, 13.9)], ('(a)', 3, 12, 9)),
         (B('figure_S1'), R(325, 0, 628, 251), [R(363.7, 0.1, 376.5, 13.9)], ('(b)', 3, 12, 9))],
        [(B('figure_S1'), R(628, 0, 1002, 251), [R(714.5, 0.1, 726.7, 13.9)], ('(c)', 3, 12, 9)),
         (B('figure_S13'), R(7, 0, 248, 197), [R(32.1, 2.9, 48.0, 15.4)], ('(d)', 25.1 - 7, 13.2, 9)),
         (B('figure_S13'), R(266, 0, 499, 197), [R(282.8, 2.9, 297.0, 15.4)], ('(e)', 275.8 - 266, 13.2, 9))],
        [(B('figure_S14'), R(7, 7, 499, 497), [], ('(f)', 3, 12, 9))],
    ], [1.0, 1.0, 0.85])

    # ---------------- SF2 = S2(a,b) + S5(c,d) ----------------
    compose('figure_S2', [
        [(B('figure_S2'), R(20, 2, 295, 200), [], None),
         (B('figure_S2'), R(295, 2, 540, 200), [], None)],
        [(B('figure_S5'), R(0, 0, 891, 169), [R(2.8, 2.8, 14.5, 16.7)], ('(c)', 3, 12, 9))],
        [(B('figure_S5'), R(0, 169, 800, 362), [R(2.4, 170.4, 14.8, 184.3)], ('(d)', 3, 12, 9))],
    ], [1.0, 1.0, 1.0])

    # ---------------- SF3 = S3(a,b,c) + S4(d) ----------------
    compose('figure_S3', [
        [(B('figure_S3'), R(7, 2, 154, 180), [], None),
         (B('figure_S3'), R(158, 2, 332, 180), [], None),
         (B('figure_S3'), R(340, 2, 497, 180), [], None)],
        [(B('figure_S4'), R(5, 0, 260, 200), [R(57.5, 1.2, 67.3, 12.3)], ('(d)', 3, 12, 9)),
         (B('figure_S4'), R(282, 0, 498, 200), [R(308.2, 1.2, 318.4, 12.3)], None)],
    ], [1.0, 1.0])

    # ---------------- SF4 = S7(a,b,c) + S8(d) ----------------
    compose('figure_S4', [
        [(B('figure_S7'), R(1, 0, 210, 249), [], None),
         (B('figure_S7'), R(286, 0, 472, 249), [], None),
         (B('figure_S7'), R(506, 0, 690, 249), [], None)],
        [(B('figure_S8'), R(7, 2, 359, 215), [R(148.5, 4.0, 156.9, 13.6)], ('(d)', 3, 12, 9)),
         (B('figure_S8'), R(388, 2, 623, 215), [R(414.9, 5.0, 424.0, 14.6)], None)],
    ], [1.0, 1.0])

    # ---------------- SF5 = S9(a,b,c) + S10(d) ----------------
    compose('figure_S5', [
        [(B('figure_S9'), R(30, 7, 380, 240), [], None),
         (B('figure_S9'), R(380, 7, 699, 240), [], None)],
        [(B('figure_S9'), R(30, 250, 699, 487), [], None)],
        [(B('figure_S10'), R(7, 2, 233, 235), [R(14.6, 4.7, 25.6, 17.1)], ('(d)', 3, 12, 9)),
         (B('figure_S10'), R(268, 2, 498, 235), [R(275.8, 4.7, 287.3, 17.1)], None)],
    ], [1.0, 1.0, 1.0])

    # ---------------- SF6 = S11(a,b) + S12(c) + S6(d) ----------------
    compose('figure_S6', [
        [(B('figure_S11'), R(17, 5, 240, 225), [], ('(a)', 3, 12, 9)),
         (B('figure_S11'), R(264, 5, 487, 225), [], ('(b)', 3, 12, 9))],
        [(B('figure_S12'), R(29, 29, 382, 554), [], ('(c)', 3, 12, 9))],
        [(B('figure_S6'), R(0, 0, 549, 313),
          [R(29.5, 0.0, 41.3, 13.2), R(29.5, 138.1, 41.7, 153.2)], ('(d)', 3, 12, 9))],
    ], [1.0, 0.55, 0.70])

    # ---------------- SF7 = S15(a,b,c) + S16(d,e,f) ----------------
    compose('figure_S7', [
        [(B('figure_S15'), R(9, 9, 184, 169), [], None),
         (B('figure_S15'), R(184, 9, 349, 169), [], None),
         (B('figure_S15'), R(349, 9, 505, 169), [], None)],
        [(B('figure_S16'), R(9, 9, 178, 161), [R(25.1, 24.6, 30.1, 34.7)], ('d', 19, 26, 9)),
         (B('figure_S16'), R(178, 9, 308, 161), [R(197.5, 24.6, 203.0, 34.7)], ('e', 22.5, 26, 9)),
         (B('figure_S16'), R(308, 9, 499, 161), [R(344.4, 24.6, 349.4, 34.7)], ('f', 39.4, 26, 9))],
    ], [1.0, 1.0])

    # ---------------- SF8 = S17(a,b) + S18(c,d) ----------------
    compose('figure_S8', [
        [(B('figure_S17'), R(2, 5, 244, 175), [], None),
         (B('figure_S17'), R(250, 5, 500, 175), [], None)],
        [(B('figure_S18'), R(7, 5, 263, 179), [R(47.0, 19.3, 52.0, 29.4)], ('c', 43, 24.5, 9)),
         (B('figure_S18'), R(272, 5, 497, 179), [R(276.6, 19.3, 282.1, 29.4)], ('d', 7.6, 24.5, 9))],
    ], [1.0, 1.0])

    # ---------------- SF9 = S19 ----------------
    shutil.copy2(B('figure_S19'), os.path.join(STAGE, 'figure_S9.pdf'))
    print('figure_S9 <- old figure_S19 (theory diagnostics, a-d unchanged)')


def audit():
    import collections
    for i in range(1, 10):
        f = f'figure_S{i}'
        doc = fitz.open(os.path.join(STAGE, f + '.pdf'))
        pg = doc[0]
        sizes = collections.Counter()
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    sizes[round(s['size'], 1)] += 1
        pix = pg.get_pixmap(dpi=100)
        pix.save(os.path.join(BASE, 'results', 'audit', f'_nc70_{f}_preview.png'))
        print(f'{f}: {pg.rect.width:.0f}x{pg.rect.height:.0f} pt, '
              f'sizes {dict(sorted(sizes.items()))}')
        doc.close()


if __name__ == '__main__':
    main()
    audit()
