#!/usr/bin/env python3
"""nc83 figure 1 typographic repair (in-place, geometry untouched).

Problem: figure1 is the only main figure with residual sub-7 pt text, all of it
carried over from the author's v6 vector artwork:
  (a) 3 schematic annotations at 6.0 pt  ('non-synonymous (AA change)', 'synonymous')
  (a) 4 workflow-box second lines at 6.0 pt ('Normalized', 'Average expression',
      'k_f and k_n', 'omega = k_f / k_n')
  (b) 2 in-plot annotations at 6.0 pt   ('Median = 7.69', 'Baseline = 7.70')
  (c) panel title variables at 4.0 pt   ('K_n', 'K_f'; the words are outlined paths)

Fix: redact the affected text only (line art preserved) and re-stamp at 7.0 pt,
keeping each element's colour, centre and baseline so the layout is unchanged.
The panel (c) title is re-typeset because its word fragments are vector outlines.

Output: results/figures_nc83/figure1.pdf
"""
import os

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'CKI_Submission_NC', 'figure1.pdf')
OUTDIR = os.path.join(BASE, 'results', 'figures_nc83')
PREV = os.path.join(BASE, 'results', 'audit', '_nc83_previews')
OUT = os.path.join(OUTDIR, 'figure1.pdf')

ARIAL = 'C:/Windows/Fonts/arial.ttf'
ARIALBD = 'C:/Windows/Fonts/arialbd.ttf'
ARIALI = 'C:/Windows/Fonts/ariali.ttf'
# unique resource names: 'Arial' already exists in the source PDF and PyMuPDF
# would silently reuse that bold resource instead of embedding our file
RES = {ARIAL: 'ArR', ARIALBD: 'ArB', ARIALI: 'ArI'}

BASE_PT = 7.0
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

_FONTS = {}


def font(path):
    if path not in _FONTS:
        _FONTS[path] = fitz.Font(fontfile=path)
    return _FONTS[path]


def tw(text, path, size):
    return font(path).text_length(text, fontsize=size)


def rgb(srgb):
    return (((srgb >> 16) & 255) / 255.0, ((srgb >> 8) & 255) / 255.0,
            (srgb & 255) / 255.0)


def norm(t):
    """PyMuPDF maps ' '/'-' to U+00A0/U+00AD in the ToUnicode CMap; normalise."""
    return t.replace('\u00a0', ' ').replace('\u00ad', '-').strip()


def spans_of(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if s['text'].strip():
                    out.append(dict(size=round(s['size'], 1),
                                    rect=fitz.Rect(s['bbox']),
                                    origin=tuple(s['origin']), text=s['text'],
                                    font=s['font'], color=s['color']))
    return out


def pick(spans, text, size=None, y0=None, y1=None):
    hits = [s for s in spans if s['text'].strip() == text
            and (size is None or abs(s['size'] - size) < 0.05)
            and (y0 is None or s['rect'].y0 >= y0)
            and (y1 is None or s['rect'].y1 <= y1)]
    assert len(hits) == 1, (text, size, [(h['size'], h['rect']) for h in hits])
    return hits[0]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    if os.path.exists(OUT):
        os.remove(OUT)
    doc = fitz.open(SRC)
    page = doc[0]
    spans = spans_of(page)

    # each entry: (redact rect, baseline, [(x, text, size, fontfile, colour)])
    edits = []

    # The four workflow boxes carry two stacked lines whose text bboxes touch
    # (line 1 bottom 227.8 vs line 2 top 227.6), so a per-span redaction clips
    # the neighbouring line.  Redact the whole band and re-stamp both lines.
    boxes = [fitz.Rect(42.0, 201.2, 122.1, 247.5),
             fitz.Rect(147.9, 201.4, 228.0, 247.5),
             fitz.Rect(253.9, 201.4, 333.9, 247.5),
             fitz.Rect(359.8, 201.4, 439.9, 247.5)]
    band = fitz.Rect(43.0, 212.5, 439.0, 238.5)
    box_rows = []
    for box in boxes:
        line1 = [s for s in spans if box.x0 < s['rect'].x0 and
                 s['rect'].x1 < box.x1 and 210 < s['rect'].y0 < 222]
        line2 = [s for s in spans if box.x0 < s['rect'].x0 and
                 s['rect'].x1 < box.x1 and 225 < s['rect'].y0 < 240]
        assert len(line1) == 1 and len(line2) == 1, (box, line1, line2)
        a, b = line1[0], line2[0]
        assert abs(a['size'] - 8.0) < 0.05 and abs(b['size'] - 6.0) < 0.05
        box_rows.append((box, [(a['text'].strip(), 8.0, a['origin'][1]),
                               (b['text'].strip(), BASE_PT, b['origin'][1])]))
    redact_rects = [band]
    stamps = []                        # (x, baseline, text, size, fontfile, colour)
    for box, rows in box_rows:
        for text, size, baseline in rows:
            w = tw(text, ARIALBD, size)
            assert w + 4 < box.width, (text, w, box.width)
            stamps.append((box.x0 + (box.width - w) / 2.0, baseline, text,
                           size, ARIALBD, WHITE))

    # (a) red / italic annotation, one line made of two spans
    s1 = pick(spans, 'non-synonymous', size=6.0)
    s2 = pick(spans, '(AA change)', size=6.0)          # span text keeps its space
    raw2 = s2['text']                                  # ' (AA change)'
    line_c = (s1['rect'].x0 + s2['rect'].x1) / 2.0
    w1 = tw('non-synonymous', ARIAL, BASE_PT)
    w2 = tw(raw2, ARIALI, BASE_PT)
    x1 = line_c - (w1 + w2) / 2.0
    edits.append((s1['rect'], s1['origin'][1],
                  [(x1, 'non-synonymous', BASE_PT, ARIAL, rgb(s1['color']))]))
    edits.append((s2['rect'], s2['origin'][1],
                  [(x1 + w1, raw2, BASE_PT, ARIALI, rgb(s2['color']))]))

    # (a) blue 'synonymous'
    s = pick(spans, 'synonymous', size=6.0)
    w = tw('synonymous', ARIAL, BASE_PT)
    edits.append((s['rect'], s['origin'][1],
                  [(s['rect'].x0 + s['rect'].width / 2.0 - w / 2.0, 'synonymous',
                    BASE_PT, ARIAL, rgb(s['color']))]))

    # a white-on-white 'T' shares the bbox band of 'synonymous' and would be
    # removed along with it; restore it verbatim so the text layer stays whole
    # the Ka-row 'T' at x=317 shares its bbox band with 'synonymous' and would
    # be removed with it; restore it verbatim so no visible letter is lost
    wt = [s for s in spans if s['text'].strip() == 'T'
          and abs(s['size'] - 8.0) < 0.05 and 36 < s['rect'].y0 < 44
          and 310 < s['rect'].x0 < 325]
    assert len(wt) == 1, wt
    edits.append((wt[0]['rect'], wt[0]['origin'][1],
                  [(wt[0]['rect'].x0, 'T', 8.0, ARIAL, rgb(wt[0]['color']))]))

    # (b) two stacked in-plot annotations, leading opened up by 1.2 pt
    for label, dy in (('Median = 7.69', -0.6), ('Baseline = 7.70', 0.6)):
        s = pick(spans, label, size=6.0)
        edits.append((s['rect'], s['origin'][1] + dy,
                      [(s['rect'].x0, label, BASE_PT, ARIAL, rgb(s['color']))]))

    # (c) panel title: 4.0 pt variables are live text, the words are outlines
    kn = pick(spans, 'K_n', size=4.0)
    kf = pick(spans, 'K_f', size=4.0)
    assert 270 < kn['rect'].y0 < 290 and 270 < kf['rect'].y0 < 290
    title_rect = fitz.Rect(kn['rect'].x0 - 1.2, kn['rect'].y0 - 2.2,
                           336.0, kn['rect'].y1 + 1.8)
    title = 'K_n vs K_f (mouse pilot)'
    w = tw(title, ARIALBD, BASE_PT)
    title_x = (kn['rect'].x0 + 336.0) / 2.0 - w / 2.0
    title_baseline = kn['origin'][1]

    # ------------------------------------------- pass 1: text-only redaction
    for rect in [e[0] for e in edits]:
        page.add_redact_annot(fitz.Rect(rect.x0 - 0.8, rect.y0 - 1.0,
                                        rect.x1 + 0.8, rect.y1 + 1.0))
    for rect in redact_rects:
        page.add_redact_annot(rect)
    kw = {}
    for key, val in (('images', 'PDF_REDACT_IMAGE_NONE'),
                     ('graphics', 'PDF_REDACT_LINE_ART_NONE'),
                     ('text', 'PDF_REDACT_TEXT_REMOVE')):
        if hasattr(fitz, val):
            kw[key] = getattr(fitz, val)
    page.apply_redactions(**kw)

    # --------------------------------- pass 2: title band, outlines included
    page.add_redact_annot(title_rect)
    kw2 = dict(kw)
    for name in ('PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED',
                 'PDF_REDACT_LINE_ART_REMOVE'):
        if hasattr(fitz, name):
            kw2['graphics'] = getattr(fitz, name)
            break
    page.apply_redactions(**kw2)

    # ------------------------------------------------------- stamp new text
    want = []
    for _, baseline, runs in edits:
        for x, text, size, path, colour in runs:
            page.insert_text((x, baseline), text, fontname=RES[path],
                             fontfile=path, fontsize=size, color=colour)
            want.append((text.strip(), x, x + tw(text, path, size), size))
    for x, baseline, text, size, path, colour in stamps:
        page.insert_text((x, baseline), text, fontname=RES[path],
                         fontfile=path, fontsize=size, color=colour)
        want.append((text.strip(), x, x + tw(text, path, size), size))
    page.insert_text((title_x, title_baseline), title, fontname=RES[ARIALBD],
                     fontfile=ARIALBD, fontsize=BASE_PT, color=BLACK)
    want.append((title, title_x, title_x + w, BASE_PT))

    doc.save(OUT, deflate=True, garbage=4, incremental=False)
    doc.close()

    # ------------------------------------------------------------- verify
    doc = fitz.open(OUT)
    pg = doc[0]
    got = spans_of(pg)
    low = [(s['size'], s['text']) for s in got if s['size'] < 7.0]
    print(f'figure1: {pg.rect.width / 72 * 25.4:.1f} x '
          f'{pg.rect.height / 72 * 25.4:.1f} mm')
    print('size profile:', sorted({s['size'] for s in got}))
    print('spans < 7 pt:', low if low else 'NONE')
    for text, xa, xb, sz in want:
        hits = [s for s in got if norm(s['text']) == norm(text)
                and abs(s['size'] - sz) < 0.05]
        assert hits, ('missing', text)
        s = min(hits, key=lambda h: abs(h['rect'].x0 - xa))
        dx = abs(s['rect'].x0 - xa)
        print(f'  {"OK" if dx < 2.0 else "SHIFTED":8s} {text[:30]:32s} '
              f'target x={xa:6.1f} got x={s["rect"].x0:6.1f} '
              f'w={s["rect"].width:5.1f} (exp {xb - xa:5.1f}) {s["font"]} '
              f'#{s["color"]:06X}')
    for ytest in (24.5, 47.4, 289.2, 297.6):
        row = sorted([s for s in got if abs(s['rect'].y0 - ytest) < 1.5],
                     key=lambda s: s['rect'].x0)
        for a, b in zip(row, row[1:]):
            gap = b['rect'].x0 - a['rect'].x1
            if gap < -0.2:
                print(f'  OVERLAP y={ytest}: {norm(a["text"])!r}/'
                      f'{norm(b["text"])!r} gap={gap:.1f}')
    doc.close()

    doc = fitz.open(OUT)
    for name, rect in (('title', title_rect),
                       ('a_top', fitz.Rect(120, 14, 420, 62)),
                       ('boxes', fitz.Rect(35, 195, 445, 270)),
                       ('b_annot', fitz.Rect(60, 250, 300, 330))):
        doc[0].get_pixmap(dpi=400, clip=rect).save(
            os.path.join(PREV, f'fig1_fixed_{name}.png'))
    doc.close()


if __name__ == '__main__':
    main()
