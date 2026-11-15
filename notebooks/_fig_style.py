#!/usr/bin/env python3
"""Shared publication style for CKI NAR submission figures.

All figure scripts import this module so that every main figure, supplementary
figure and the graphical abstract share one coherent visual identity:

  * NAR sizing: 178 mm (double column) / 89 mm (single column), 300 dpi
  * Arial (Type 42 embedded, editable text in PDF)
  * Minimum font size 7 pt (NAR floor), panel labels 9 pt bold
  * Unified colour palette (colour-blind-safe family used across the paper)
  * Despined axes, subtle dotted grid, no top/right spines
  * save_fig() helper writing both PDF (vector) and PNG (preview)

IMPORTANT: this module touches ONLY presentation.  Figure scripts must keep
their data loading and numeric computations untouched.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

# --------------------------------------------------------------------------
# Sizing constants (NAR guidelines)
# --------------------------------------------------------------------------
MM = 1 / 25.4
SINGLE = 89 * MM          # single column
DOUBLE = 178 * MM         # double column
DPI = 300

# --------------------------------------------------------------------------
# Colour palette — identical hue family across every figure
# --------------------------------------------------------------------------
C_BLUE        = "#1B4F8A"   # primary (k_n, neutral)
C_GREEN       = "#1E8449"   # primary (k_f, functional)
C_AMBER       = "#B7770D"
C_RED         = "#922B21"
C_ORANGE      = "#C0581A"
C_ORANGE2     = "#DC7633"
C_PURPLE      = "#6C3483"
C_TEAL        = "#0E7D78"
C_STEEL       = "#5D6D7E"
C_GRAY        = "#4D5656"
C_DARK        = "#1A1A1A"
C_LIGHT_GRAY  = "#D5D8DC"
C_LIGHT_BLUE  = "#AEC9E2"   # fill for box plots / ribbons
C_LIGHT_GREEN = "#A9DFBF"

# Sequential ramps (heatmaps)
RAMP_BLUE   = ["#F4F8FC", "#C9DCF0", "#8FB4DC", "#5A8EC4", "#2E66A8", "#1B4F8A"]
RAMP_PURPLE = ["#F7F3FA", "#D7C4E4", "#B191CE", "#8C63AC", "#6C3483", "#4A1F5C"]
RAMP_TEAL   = ["#F2FAF9", "#C4E4E2", "#8CC9C6", "#4FA8A5", "#1B8783", "#0E7D78"]

# --------------------------------------------------------------------------
# Type scale (pt) — NAR minimum is 7 pt
# --------------------------------------------------------------------------
LABEL_SIZE = 9    # panel letters A/B/C/D (bold)
TITLE_SIZE = 9    # panel titles (bold)
BODY_SIZE  = 8    # axis labels / body text
SMALL_SIZE = 7    # ticks, legends (NAR floor)

# --------------------------------------------------------------------------
# Global rcParams
# --------------------------------------------------------------------------
DEFAULT_RC = {
    "font.family": "Arial",
    "font.size": BODY_SIZE,
    "axes.titlesize": TITLE_SIZE,
    "axes.titleweight": "bold",
    "axes.labelsize": BODY_SIZE,
    "axes.labelcolor": C_DARK,
    "axes.edgecolor": "#3A3A3A",
    "axes.linewidth": 0.6,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": "#BDC3C7",
    "grid.linewidth": 0.4,
    "grid.linestyle": ":",
    "xtick.labelsize": SMALL_SIZE,
    "ytick.labelsize": SMALL_SIZE,
    "xtick.color": C_DARK,
    "ytick.color": C_DARK,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.fontsize": SMALL_SIZE,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "#BDC3C7",
    "legend.fancybox": False,
    "lines.linewidth": 1.1,
    "patch.linewidth": 0.5,
    "figure.titlesize": 10,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.format": "pdf",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
}


def apply_style() -> None:
    """Apply the shared rcParams (call once at the top of every script)."""
    matplotlib.rcParams.update(DEFAULT_RC)


# --------------------------------------------------------------------------
# Helper: despine
# --------------------------------------------------------------------------
def despine(ax, left=True, bottom=True) -> None:
    """Remove top/right spines (default rcParams already do); keep optional."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if not left:
        ax.spines["left"].set_visible(False)
    if not bottom:
        ax.spines["bottom"].set_visible(False)


def subtle_grid(ax, axis="y") -> None:
    """Dotted grid behind the data (NAR-friendly, very light)."""
    ax.grid(True, axis=axis, linewidth=0.4, linestyle=":",
            color="#C9CED3", alpha=0.8, zorder=0)
    ax.set_axisbelow(True)


# --------------------------------------------------------------------------
# Helper: panel labels
# --------------------------------------------------------------------------
def add_panel_label(fig, ax, letter: str, x=None, y=1.02,
                    axes_relative: bool = True, size=LABEL_SIZE) -> None:
    """Bold panel letter.

    axes_relative=True  -> place at axes fraction (x default -0.02, i.e. just
                           left of the axes, aligned across rows when the
                           columns share margins).
    axes_relative=False -> x/y are figure fractions (for left-column alignment
                           via fig.text, matching existing _fig*_clean.py).
    """
    if x is None:
        x = -0.02 if axes_relative else 0.035
    if axes_relative:
        ax.text(x, y, letter, transform=ax.transAxes, fontsize=size,
                fontweight="bold", va="bottom", ha="left", clip_on=False)
    else:
        fig.text(x, y, letter, fontsize=size, fontweight="bold",
                 va="bottom", ha="left")


# --------------------------------------------------------------------------
# Helper: axis formatting
# --------------------------------------------------------------------------
def sci_formatter(decimals: int = 1) -> FuncFormatter:
    """Scientific-notation tick formatter (e.g. 2.5×10⁻³)."""
    def _fmt(val, _pos):
        if val == 0:
            return "0"
        m = abs(val)
        if 0.01 <= m < 10000:
            return f"{val:g}"
        exp = 0
        v = val
        while abs(v) >= 10:
            v /= 10.0
            exp += 1
        while abs(v) < 1:
            v *= 10.0
            exp -= 1
        return f"{v:.{decimals}f}\u00d710$^{{{exp}}}$"
    return FuncFormatter(_fmt)


# --------------------------------------------------------------------------
# Helper: output
# --------------------------------------------------------------------------
FIGURE_DIRS = [
    Path("results/figures_final"),
]


def save_fig(fig, name: str, out_dir: str | os.PathLike | None = None,
             pdf: bool = True, png: bool = True, pad: float = 0.04) -> list:
    """Save figure as results/figures_final/<name>.pdf and .png.

    Kept signature-compatible with existing scripts:
        out_pdf = OUT_DIR / f'{name}.pdf'
    Returns list of written paths.
    """
    out = Path(out_dir) if out_dir else FIGURE_DIRS[0]
    out.mkdir(parents=True, exist_ok=True)
    written = []
    if pdf:
        p = out / f"{name}.pdf"
        fig.savefig(p, dpi=DPI, facecolor="white",
                    bbox_inches=None, pad_inches=pad,
                    metadata={"Creator": "CKI NAR Figures"})
        written.append(p)
    if png:
        p = out / f"{name}.png"
        fig.savefig(p, dpi=DPI, facecolor="white",
                    bbox_inches=None, pad_inches=pad)
        written.append(p)
    return written


# --------------------------------------------------------------------------
# Convenience: figure factory
# --------------------------------------------------------------------------
def new_figure(width_in, height_in, **kwargs):
    """Apply style and return a new figure (rcParams set once here)."""
    apply_style()
    return plt.figure(figsize=(width_in, height_in), dpi=DPI, **kwargs)


apply_style()

if __name__ == "__main__":
    # Smoke test: render a tiny demo panel and report sizes.
    fig = new_figure(DOUBLE, 40 * MM)
    ax = fig.add_subplot(111)
    ax.bar([0, 1, 2], [1.2, 0.8, 2.1], color=[C_BLUE, C_GREEN, C_AMBER])
    subtle_grid(ax)
    despine(ax)
    add_panel_label(fig, ax, "A")
    ax.set_xlabel("x", fontsize=BODY_SIZE)
    ax.set_ylabel("y", fontsize=BODY_SIZE)
    paths = save_fig(fig, "_style_smoke_test")
    plt.close(fig)
    for p in paths:
        print(f"OK {p}")
