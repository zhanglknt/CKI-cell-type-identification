"""
Generate a professional NAR-style Graphical Abstract for CKI (portrait orientation).

NAR requirements:
- Single image summarizing the article
- Recommended 1200 x 1600 pixels (min 531 x 1328)
- 300 DPI
- Format: PNG, PDF, TIFF, JPEG (file <= 10 MB)

Outputs:
    results/figures_final/CKI_graphical_abstract.png
    results/figures_final/CKI_graphical_abstract.pdf
    results/figures_final/CKI_graphical_abstract.svg
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.patches import FancyBboxPatch, Circle, Polygon
import numpy as np
import os

# Use a font available on the system to avoid warnings; NAR prefers Arial/Helvetica
font_candidates = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
available_font = 'sans-serif'
for f in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
    try:
        prop = matplotlib.font_manager.FontProperties(fname=f)
        name = prop.get_name()
        if name in ('Arial', 'Helvetica', 'DejaVu Sans') and name not in available_font:
            available_font = name
            break
    except Exception:
        pass

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = [available_font]
plt.rcParams['font.size'] = 10
plt.rcParams['svg.fonttype'] = 'none'  # keep text as text in SVG
plt.rcParams['pdf.fonttype'] = 42      # embed TrueType (editable text)
plt.rcParams['ps.fonttype'] = 42

OUT_DIR = 'results/figures_final'
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Color palette (NAR-friendly, colorblind-safe; aligned with the shared
# _fig_style.py palette used across all main and supplementary figures)
# ---------------------------------------------------------------------------
C_BG = '#FFFFFF'
C_TEXT = '#1A1A1A'
C_SUBTEXT = '#5D6D7E'
C_BLUE = '#1B4F8A'
C_BLUE_L = '#D9E7F5'
C_BLUE_M = '#8FB4DC'
C_BLUE_D = '#0E3A66'
C_ORANGE = '#C0581A'
C_ORANGE_L = '#F8E3D3'
C_ORANGE_M = '#E39A6B'
C_ORANGE_D = '#8A3E12'
C_PURPLE = '#6C3483'
C_PURPLE_L = '#EFEBF7'
C_GREEN = '#1E8449'
C_GREEN_L = '#E8F4EC'
C_GOLD = '#B7770D'
C_GOLD_L = '#FAEEDA'
C_RED = '#922B21'
C_RED_L = '#FBEAE8'
C_GRAY = '#BDC3C7'
C_PANEL = '#F7F8F9'


def draw_arrow(ax, x1, y1, x2, y2, color=C_SUBTEXT, lw=1.2, arrowstyle='->'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=arrowstyle, color=color, lw=lw,
                                connectionstyle='arc3,rad=0'))


def draw_cell_cluster(ax, cx, cy, base_color, dark_color, n_cells=10, radius=0.7):
    np.random.seed(42)
    for i in range(n_cells):
        angle = 2 * np.pi * i / n_cells + np.random.uniform(-0.15, 0.15)
        dist = np.random.uniform(0.0, 0.45)  # more compact
        x = cx + dist * np.cos(angle) * 1.1
        y = cy + dist * np.sin(angle) * 1.1
        r = np.random.uniform(0.10, 0.20)
        col = dark_color if i % 3 == 0 else base_color
        circle = Circle((x, y), r, facecolor=col, edgecolor=dark_color, linewidth=0.5, zorder=3)
        ax.add_patch(circle)
    circle = Circle((cx, cy), 0.12, facecolor='white', edgecolor=dark_color, linewidth=0.5, zorder=4)
    ax.add_patch(circle)


def draw_distribution(ax, cx, cy, width, height, color, second_color=None, divergent=False):
    x = np.linspace(-1, 1, 100)
    if divergent:
        y1 = height * np.exp(-2.5 * (x + 0.35) ** 2)
        y2 = height * np.exp(-2.5 * (x - 0.35) ** 2)
        ax.fill_between(cx + x * width / 2, cy, cy + y1, color=color, alpha=0.22, zorder=2)
        ax.fill_between(cx + x * width / 2, cy, cy + y2, color=second_color, alpha=0.22, zorder=2)
        ax.plot(cx + x * width / 2, cy + y1, color=color, lw=2, zorder=3)
        ax.plot(cx + x * width / 2, cy + y2, color=second_color, lw=2, zorder=3)
    else:
        y = height * np.exp(-3.5 * x ** 2)
        ax.fill_between(cx + x * width / 2, cy, cy + y, color=color, alpha=0.22, zorder=2)
        ax.plot(cx + x * width / 2, cy + y, color=color, lw=2, zorder=3)


def draw_dna_icon(ax, x, y, color, scale=1.0):
    t = np.linspace(-1, 1, 50)
    x1 = x + t * 0.35 * scale
    y1 = y + 0.25 * scale * np.sin(np.pi * t)
    x2 = x + t * 0.35 * scale
    y2 = y + 0.25 * scale * np.sin(np.pi * t + np.pi)
    ax.plot(x1, y1, color=color, lw=1.5 * scale)
    ax.plot(x2, y2, color=color, lw=1.5 * scale)
    for i in range(5):
        tx = -0.7 + i * 0.35
        ax.plot([x + tx * scale, x + tx * scale],
                [y + 0.25 * scale * np.sin(np.pi * tx) - 0.02 * scale,
                 y + 0.25 * scale * np.sin(np.pi * tx + np.pi) + 0.02 * scale],
                color=color, lw=1.2 * scale)


def draw_selection_icon(ax, x, y, color, scale=1.0):
    draw_dna_icon(ax, x, y - 0.15 * scale, color, scale=scale)
    ax.annotate('', xy=(x, y + 0.45 * scale), xytext=(x, y + 0.05 * scale),
                arrowprops=dict(arrowstyle='->', color=color, lw=2 * scale))


def main():
    # -----------------------------------------------------------------------
    # Portrait figure: 6.5 x 9 inches at 300 DPI = 1950 x 2700 pixels
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 9), dpi=300)
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    # -----------------------------------------------------------------------
    # Title
    # -----------------------------------------------------------------------
    ax.text(3.25, 8.90, 'CKI: A Cell-type Identity Index',
            fontsize=17, fontweight='bold', color=C_TEXT, ha='center', va='top')
    ax.text(3.25, 8.68, 'Quantifying baseline-normalized transcriptomic divergence from expression distributions',
            fontsize=8.5, color=C_SUBTEXT, ha='center', va='top')

    # -----------------------------------------------------------------------
    # STEP 1: Two cell states (side by side)
    # -----------------------------------------------------------------------
    y_cells = 7.65
    draw_cell_cluster(ax, 1.8, y_cells, C_BLUE_L, C_BLUE, n_cells=10, radius=0.7)
    ax.text(1.8, y_cells - 0.50, 'Cell state A', fontsize=9, color=C_TEXT, ha='center', va='top', fontweight='bold')

    draw_cell_cluster(ax, 4.7, y_cells, C_ORANGE_L, C_ORANGE, n_cells=10, radius=0.7)
    ax.text(4.7, y_cells - 0.50, 'Cell state B', fontsize=9, color=C_TEXT, ha='center', va='top', fontweight='bold')

    # Comparison arrow above cell clusters (arc)
    ax.annotate('', xy=(4.3, y_cells + 0.15), xytext=(2.2, y_cells + 0.15),
                arrowprops=dict(arrowstyle='->', color=C_SUBTEXT, lw=1.2,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(3.25, y_cells + 0.65, 'compare expression profiles', fontsize=7, color=C_SUBTEXT, ha='center', va='center')

    # -----------------------------------------------------------------------
    # STEP 2: Pseudobulk aggregation
    # -----------------------------------------------------------------------
    y_pb = 6.50
    draw_arrow(ax, 1.8, y_cells - 0.45, 2.3, y_pb + 0.25, color=C_SUBTEXT, lw=1.1)
    draw_arrow(ax, 4.7, y_cells - 0.45, 4.2, y_pb + 0.25, color=C_SUBTEXT, lw=1.1)

    box_pb = FancyBboxPatch((1.85, y_pb - 0.25), 2.8, 0.50, boxstyle='round,pad=0.05,rounding_size=0.1',
                            facecolor=C_PANEL, edgecolor=C_GRAY, linewidth=1.2)
    ax.add_patch(box_pb)
    # mini bar chart
    bars = [(0.15, 0.18, C_BLUE), (0.35, 0.10, C_BLUE_M), (0.55, 0.22, C_BLUE),
            (0.75, 0.09, C_ORANGE_M), (0.95, 0.20, C_ORANGE), (1.15, 0.12, C_ORANGE_M),
            (1.35, 0.14, C_BLUE_M), (1.55, 0.16, C_ORANGE_M)]
    for bx, bh, bc in bars:
        ax.bar(2.15 + bx, bh, width=0.12, bottom=y_pb - 0.15, color=bc, edgecolor='none')
    ax.text(3.25, y_pb + 0.15, 'Pseudobulk expression profiles', fontsize=9, color=C_TEXT, ha='center', va='center', fontweight='bold')

    # -----------------------------------------------------------------------
    # STEP 3: Gene set split
    # -----------------------------------------------------------------------
    y_split = 5.15
    draw_arrow(ax, 3.25, y_pb - 0.25, 2.15, y_split + 0.40, color=C_BLUE, lw=1.2)
    draw_arrow(ax, 3.25, y_pb - 0.25, 4.35, y_split + 0.40, color=C_ORANGE, lw=1.2)

    # Housekeeping box (left)
    box_hk = FancyBboxPatch((0.55, y_split - 0.55), 2.4, 1.05, boxstyle='round,pad=0.05,rounding_size=0.12',
                            facecolor=C_BLUE_L, edgecolor=C_BLUE_M, linewidth=1.2)
    ax.add_patch(box_hk)
    draw_dna_icon(ax, 1.75, y_split + 0.22, C_BLUE, scale=1.0)
    ax.text(1.75, y_split + 0.74, 'Housekeeping genes', fontsize=9, color=C_BLUE_D, ha='center', va='bottom', fontweight='bold',
            path_effects=[path_effects.withStroke(linewidth=2.5, foreground='white')])
    ax.text(1.75, y_split + 0.64, 'Neutral expression baseline', fontsize=7, color=C_SUBTEXT, ha='center', va='bottom',
            path_effects=[path_effects.withStroke(linewidth=2, foreground='white')])
    draw_distribution(ax, 1.75, y_split - 0.15, 1.6, 0.55, C_BLUE)
    ax.text(1.75, y_split - 0.35, r'$k_n$  (JS divergence)', fontsize=8, color=C_TEXT, ha='center', va='top')

    # Functional box (right)
    box_fn = FancyBboxPatch((3.55, y_split - 0.55), 2.4, 1.05, boxstyle='round,pad=0.05,rounding_size=0.12',
                            facecolor=C_ORANGE_L, edgecolor=C_ORANGE_M, linewidth=1.2)
    ax.add_patch(box_fn)
    draw_selection_icon(ax, 4.75, y_split + 0.22, C_ORANGE, scale=1.0)
    ax.text(4.75, y_split + 0.74, 'Functional genes', fontsize=9, color=C_ORANGE_D, ha='center', va='bottom', fontweight='bold',
            path_effects=[path_effects.withStroke(linewidth=2.5, foreground='white')])
    ax.text(4.75, y_split + 0.64, 'Under selective pressure', fontsize=7, color=C_SUBTEXT, ha='center', va='bottom',
            path_effects=[path_effects.withStroke(linewidth=2, foreground='white')])
    draw_distribution(ax, 4.75, y_split - 0.15, 1.6, 0.55, C_ORANGE_M, C_ORANGE, divergent=True)
    ax.text(4.75, y_split - 0.35, r'$k_f$  (JS divergence)', fontsize=8, color=C_TEXT, ha='center', va='top')

    # -----------------------------------------------------------------------
    # STEP 4: Omega ratio
    # -----------------------------------------------------------------------
    y_omega = 4.00
    draw_arrow(ax, 1.75, y_split - 0.55, 2.55, y_omega + 0.35, color=C_BLUE, lw=1.2)
    draw_arrow(ax, 4.75, y_split - 0.55, 3.95, y_omega + 0.35, color=C_ORANGE, lw=1.2)

    box_omega = FancyBboxPatch((1.75, y_omega - 0.35), 3.0, 0.75, boxstyle='round,pad=0.05,rounding_size=0.15',
                               facecolor=C_PURPLE_L, edgecolor=C_PURPLE, linewidth=1.5)
    ax.add_patch(box_omega)
    ax.text(3.25, y_omega + 0.08, r'$\omega = k_f / k_n$', fontsize=20, color=C_PURPLE, ha='center', va='center',
            fontweight='bold')
    ax.text(3.25, y_omega - 0.15, r'$\omega > 1 \rightarrow$ selection exceeds drift', fontsize=8, color=C_PURPLE,
            ha='center', va='center')

    # -----------------------------------------------------------------------
    # STEP 5: Bootstrap test + classification
    # -----------------------------------------------------------------------
    y_boot = 2.95
    draw_arrow(ax, 3.25, y_omega - 0.35, 3.25, y_boot + 0.30, color=C_PURPLE, lw=1.2)

    # Bootstrap icon
    circ = Circle((2.65, y_boot), 0.22, facecolor=C_GOLD_L, edgecolor=C_GOLD, linewidth=1.2)
    ax.add_patch(circ)
    theta = np.linspace(0.2, 1.7 * np.pi, 50)
    ax.plot(2.65 + 0.12 * np.cos(theta), y_boot + 0.12 * np.sin(theta), color=C_GOLD, lw=1.5)
    ax.text(2.65, y_boot - 0.30, 'Bootstrap test', fontsize=7, color=C_TEXT, ha='center', va='top')

    draw_arrow(ax, 2.88, y_boot, 3.55, y_boot, color=C_SUBTEXT, lw=1.1)

    # Classification boxes (vertical stack)
    cat_x = 4.05
    categories = [
        (cat_x, y_boot + 0.28, 'Strong', C_GREEN, C_GREEN_L, 'p < 0.01'),
        (cat_x, y_boot, 'Moderate', C_GOLD, C_GOLD_L, 'p < 0.05'),
        (cat_x, y_boot - 0.28, 'Weak', C_RED, C_RED_L, 'p >= 0.05'),
    ]
    for x, y, label, text_c, fill_c, ptext in categories:
        box = FancyBboxPatch((x - 0.48, y - 0.10), 0.96, 0.20,
                             boxstyle='round,pad=0.02,rounding_size=0.05',
                             facecolor=fill_c, edgecolor=text_c, linewidth=1.2)
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=8, color=text_c, ha='center', va='center', fontweight='bold')

    # -----------------------------------------------------------------------
    # Applications panel (bottom row)
    # -----------------------------------------------------------------------
    y_app = 1.40
    ax.text(3.25, y_app + 0.95, 'Applications', fontsize=11, color=C_TEXT, ha='center', va='top', fontweight='bold')

    # TCGA cancer panel
    box_t = FancyBboxPatch((0.55, y_app - 0.45), 1.7, 0.95, boxstyle='round,pad=0.05,rounding_size=0.1',
                           facecolor=C_ORANGE_L, edgecolor=C_ORANGE, linewidth=1.2)
    ax.add_patch(box_t)
    ax.text(1.40, y_app + 0.38, 'TCGA cancer', fontsize=9, color=C_ORANGE, ha='center', va='top', fontweight='bold')
    ax.text(1.40, y_app + 0.28, 'Tumor vs. normal', fontsize=7, color=C_SUBTEXT, ha='center', va='top')
    ax.bar([1.15], [0.35], width=0.28, bottom=y_app - 0.05, color=C_ORANGE, edgecolor='none')
    ax.bar([1.65], [0.18], width=0.28, bottom=y_app - 0.05, color=C_BLUE_M, edgecolor='none')
    ax.text(1.15, y_app - 0.12, 'Tumor', fontsize=7, color=C_TEXT, ha='center', va='top')
    ax.text(1.65, y_app - 0.12, 'Normal', fontsize=7, color=C_TEXT, ha='center', va='top')

    # Brain atlas panel
    box_b = FancyBboxPatch((2.40, y_app - 0.45), 1.7, 0.95, boxstyle='round,pad=0.05,rounding_size=0.1',
                           facecolor=C_BLUE_L, edgecolor=C_BLUE, linewidth=1.2)
    ax.add_patch(box_b)
    ax.text(3.25, y_app + 0.38, 'Human brain atlas', fontsize=9, color=C_BLUE, ha='center', va='top', fontweight='bold')
    ax.text(3.25, y_app + 0.28, 'Cell-type diversity', fontsize=7, color=C_SUBTEXT, ha='center', va='top')
    # mini brain outline + dots
    brain_x = np.array([0.0, 0.15, 0.45, 0.75, 0.85, 0.65, 0.35, 0.0]) * 1.0
    brain_y = np.array([0.0, 0.35, 0.5, 0.35, 0.0, -0.15, -0.15, 0.0]) * 0.9
    ax.plot(3.25 + brain_x - 0.425, y_app + 0.05 + brain_y, color=C_BLUE, lw=1.5)
    for dx, dy, c in [(0.15, 0.15, C_BLUE), (0.45, 0.25, C_ORANGE), (0.6, 0.05, C_GREEN),
                      (0.3, -0.05, C_PURPLE)]:
        ax.scatter(3.25 + dx - 0.425, y_app + 0.05 + dy, s=10, color=c, zorder=5)

    # Tabula atlases panel
    box_m = FancyBboxPatch((4.25, y_app - 0.45), 1.7, 0.95, boxstyle='round,pad=0.05,rounding_size=0.1',
                           facecolor=C_GREEN_L, edgecolor=C_GREEN, linewidth=1.2)
    ax.add_patch(box_m)
    ax.text(5.10, y_app + 0.38, 'Tabula atlases', fontsize=9, color=C_GREEN, ha='center', va='top', fontweight='bold')
    ax.text(5.10, y_app + 0.28, 'Validation across tissues', fontsize=7, color=C_SUBTEXT, ha='center', va='top')
    for i, c in enumerate([C_BLUE, C_ORANGE, C_PURPLE, C_GREEN]):
        ax.add_patch(Circle((4.65 + i * 0.26, y_app + 0.08), 0.08, facecolor=c, edgecolor='white', linewidth=0.5))

    # -----------------------------------------------------------------------
    # Bottom key insight
    # -----------------------------------------------------------------------
    box_key = FancyBboxPatch((0.40, 0.20), 5.7, 0.55, boxstyle='round,pad=0.05,rounding_size=0.1',
                             facecolor=C_PANEL, edgecolor=C_GRAY, linewidth=0.8)
    ax.add_patch(box_key)
    ax.text(0.60, 0.58, 'Key insight:', fontsize=9, color=C_TEXT, ha='left', va='center', fontweight='bold')
    ax.text(0.60, 0.35, r'$\omega$ distinguishes functional remodeling from neutral transcriptomic drift',
            fontsize=8, color=C_SUBTEXT, ha='left', va='center')

    # -----------------------------------------------------------------------
    # Step indicator circles (left margin, drawn last for z-order)
    # -----------------------------------------------------------------------
    for y_val, label, col in [
        (y_cells, '1', C_BLUE),
        (y_pb, '2', C_BLUE),
        (y_split, '3', C_PURPLE),
        (y_omega, '4', C_PURPLE),
        (y_boot, '5', C_GOLD),
    ]:
        circ = Circle((0.28, y_val), 0.15, facecolor=col, edgecolor='white', linewidth=1.5, zorder=10)
        ax.add_patch(circ)
        ax.text(0.28, y_val, label, fontsize=8, color='white', ha='center', va='center',
                fontweight='bold', zorder=11)

    # -----------------------------------------------------------------------
    # Save outputs
    # -----------------------------------------------------------------------
    png_path = os.path.join(OUT_DIR, 'CKI_graphical_abstract.png')
    pdf_path = os.path.join(OUT_DIR, 'CKI_graphical_abstract.pdf')
    svg_path = os.path.join(OUT_DIR, 'CKI_graphical_abstract.svg')

    fig.savefig(png_path, dpi=300, bbox_inches='tight', pad_inches=0.08, facecolor=C_BG)
    fig.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0.08, facecolor=C_BG)
    fig.savefig(svg_path, dpi=300, bbox_inches='tight', pad_inches=0.08, facecolor=C_BG)

    print(f'Saved: {png_path}')
    print(f'Saved: {pdf_path}')
    print(f'Saved: {svg_path}')

    for p in [png_path, pdf_path, svg_path]:
        size_kb = os.path.getsize(p) / 1024
        print(f'  {os.path.basename(p)}: {size_kb:.1f} KB')


if __name__ == '__main__':
    main()
