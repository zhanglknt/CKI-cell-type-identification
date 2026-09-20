#!/usr/bin/env python3
"""Assemble v47 figure staging (results/figures_v47_author/).

Sources:
- first-author v46_manuscript/Figures: figure1-6, figure_S2..S11, figure_S13__ (Kang)
- our re-drawn S1: results/figures_final/ed_fig1_parameter_sweep_pathway.pdf
- v46 QQ:          results/figures_final/pseudoregion_control_qq.pdf
- GA: author's CKI_graphical_abstract.pdf with title fixed to
  "CKI: a Ka/Ks-inspired index" (was "CKI: A Cell-state Kinetic Index"),
  + fresh png/svg review-aid renders.

Mapping (author file -> v47 submission slot):
  figure_S1   (his redrawn sweep)      DISCARDED (replaced by our ed_fig1)
  figure_S2..S11 (already new-numbered) -> S2..S11 as-is
  figure_S13__ (Kang IFN-beta)          -> S12
  figure_S14 (QQ)                       DISCARDED (v46 pseudoregion_control_qq kept)
"""
import os, shutil, sys, hashlib
import fitz

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
AUTHOR = os.path.join(BASE, "_tmp_fa_review", "v46_manuscript", "Figures")
FINAL = os.path.join(BASE, "results", "figures_final")
STAGE = os.path.join(BASE, "results", "figures_v47_author")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]

def cp(src, dst):
    shutil.copy2(src, dst)
    print(f"  {os.path.basename(dst):42s} <- {os.path.basename(src)} "
          f"({os.path.getsize(dst):,}B sha:{sha(dst)})")

def main():
    os.makedirs(STAGE, exist_ok=True)
    # clean stage
    for f in os.listdir(STAGE):
        os.remove(os.path.join(STAGE, f))

    print("[1] main figures 1-6 (author)")
    for i in range(1, 7):
        cp(os.path.join(AUTHOR, f"figure{i}.pdf"),
           os.path.join(STAGE, f"figure{i}.pdf"))

    print("[2] supplementary S1 (ours, re-drawn) + S2-S11 (author)")
    cp(os.path.join(FINAL, "ed_fig1_parameter_sweep_pathway.pdf"),
       os.path.join(STAGE, "figure_S1.pdf"))
    for i in range(2, 12):
        cp(os.path.join(AUTHOR, f"figure_S{i}.pdf"),
           os.path.join(STAGE, f"figure_S{i}.pdf"))

    print("[3] S12 = author Kang (figure_S13__.pdf); S13 = v46 QQ")
    cp(os.path.join(AUTHOR, "figure_S13__.pdf"),
       os.path.join(STAGE, "figure_S12.pdf"))
    cp(os.path.join(FINAL, "pseudoregion_control_qq.pdf"),
       os.path.join(STAGE, "figure_S13.pdf"))

    print("[4] GA: fix title on author's version")
    ga_src = fitz.open(os.path.join(AUTHOR, "CKI_graphical_abstract.pdf"))
    pg = ga_src[0]
    W = pg.rect.width
    # cover old outlined title (curves bbox y 6.1-18.7, subtitle starts 25.9)
    pg.draw_rect(fitz.Rect(0, 0, W, 23.5), color=None, fill=(1, 1, 1), overlay=True)
    # draw corrected title, matched style: bold ~16pt, #2C2C2A, centered.
    # NOTE: insert_textbox silently fails to fit here; use single-line insert_text.
    title = "CKI: a Ka/Ks-inspired index"
    ink = (44 / 255, 44 / 255, 42 / 255)
    tw = fitz.get_text_length(title, fontname="hebo", fontsize=16)
    pg.insert_text(((W - tw) / 2, 17.5), title, fontsize=16,
                   fontname="hebo", color=ink)
    ga_pdf = os.path.join(STAGE, "CKI_graphical_abstract.pdf")
    ga_src.save(ga_pdf, garbage=4, deflate=True)
    ga_src.close()
    print(f"  CKI_graphical_abstract.pdf fixed ({os.path.getsize(ga_pdf):,}B)")

    # review-aid renders from the FIXED pdf
    gd = fitz.open(ga_pdf)
    g0 = gd[0]
    pix = g0.get_pixmap(dpi=300)
    png_out = os.path.join(STAGE, "CKI_graphical_abstract.png")
    pix.save(png_out)
    svg_out = os.path.join(STAGE, "CKI_graphical_abstract.svg")
    with open(svg_out, "w", encoding="utf-8") as f:
        f.write(g0.get_svg_image())
    gd.close()
    print(f"  GA png ({os.path.getsize(png_out):,}B) + svg ({os.path.getsize(svg_out):,}B)")

    print("[5] verify staged set")
    expect = ([f"figure{i}.pdf" for i in range(1, 7)] +
              [f"figure_S{i}.pdf" for i in range(1, 14)] +
              ["CKI_graphical_abstract.pdf"])
    have = sorted(os.listdir(STAGE))
    ok = True
    for e in expect:
        p = os.path.join(STAGE, e)
        if not os.path.exists(p):
            print(f"  MISSING: {e}")
            ok = False
            continue
        try:
            d = fitz.open(p)
            _ = d[0].get_pixmap(dpi=40)  # render smoke test
            d.close()
        except Exception as ex:
            print(f"  RENDER FAIL: {e}: {ex}")
            ok = False
    extra = [h for h in have if h not in expect and not h.startswith("CKI_graphical_abstract")]
    if extra:
        print(f"  EXTRA files: {extra}")
        ok = False
    print(f"  staged {len(have)} files; expect {len(expect)} figure PDFs + GA png/svg")
    if not ok:
        sys.exit(1)
    print("OK: v47 figure staging complete")

if __name__ == "__main__":
    main()
