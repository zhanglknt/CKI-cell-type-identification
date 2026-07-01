"""
Split a single-page oversized PDF into multiple A4 pages.
usage_guide_en.pdf: 317.5x687.9mm -> ~3 A4 pages
"""
import fitz
import os

SRC = "results/figures_final/usage_guide_en.pdf"
DST = "results/figures_final/usage_guide_en_A4.pdf"

A4_W_PT = 595.28   # 210mm
A4_H_PT = 841.89   # 297mm

doc = fitz.open(SRC)
src_page = doc[0]

src_w = src_page.rect.width
src_h = src_page.rect.height
print(f"Source: {src_w*25.4/72:.1f} x {src_h*25.4/72:.1f} mm")

# How many A4 pages needed
n_pages = int(src_h / A4_H_PT) + (1 if src_h % A4_H_PT > 0 else 0)
print(f"Splitting into {n_pages} A4 pages...")

new_doc = fitz.open()
for i in range(n_pages):
    y0 = i * A4_H_PT
    y1 = min((i+1) * A4_H_PT, src_h)
    h_pt = y1 - y0

    # Create A4 page
    new_page = new_doc.new_page(width=A4_W_PT, height=A4_H_PT)

    # Draw the source region onto the new page
    # Source rect (in source page coordinates)
    src_rect = fitz.Rect(0, y0, src_w, y1)
    # Destination rect (full A4 page)
    dst_rect = fitz.Rect(0, 0, A4_W_PT, A4_H_PT)

    new_page.show_pdf_page(dst_rect, doc, 0, clip=src_rect)

new_doc.save(DST)
new_doc.close()
doc.close()
print(f"Saved: {DST}")
print(f"Size: {os.path.getsize(DST)/1024:.0f} KB")
