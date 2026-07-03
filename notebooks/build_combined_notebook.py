"""
Build a combined JupyterLab .ipynb from the core analysis .py scripts.

Strategy:
- Docstring of each script → H2 markdown cell
- # === SECTION === lines → H3/H4 markdown cells
- Code blocks between markers → code cells
"""
import nbformat as nbf
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "CKI_Reproducibility.ipynb"

# ── core analysis scripts in execution order ──────────────────────────
CORE_SCRIPTS = [
    # Part 0: Tissue omega matrix + HK gene set analysis
    ("01_tissue_omega_matrix.py", "Part 0: Tissue-Level Omega Matrix — Tabula Muris 6 Organs"),
    ("01b_hk_stability.py", "Part 0 (cont.): HK Gene Set Stability Analysis"),
    ("01c_hk_overlap.py", "Part 0 (cont.): HK Gene Set Detection Overlap with HRT Atlas"),
    ("precompute_figure_data.py", "Part 0 (cont.): Pre-compute Derived Figure Data"),
    # Part A: Mouse pilot
    ("02b_pilot_v2.py", "Part A: Mouse Pilot v2 — Tabula Muris FACS"),
    ("02c_pilot_v2b.py", "Part A (cont.): Cell-Type Pilot v2b"),
    # Part B: Human full matrix
    ("03_full_matrix.py", "Part B: Full Matrix — All Human Cell-Type Pairs (32x32)"),
    ("04_phase32_sweep.py", "Part B (cont.): Mouse-Human Cross-Species Sweep"),
    # Part C: Tabula Sapiens — omega profiles
    ("05_phase33_v3_fixed.py", "Part C: Tabula Sapiens — Omega Profiles per Organ"),
    # Part D: TCGA tumor perturbation
    ("06_phase34_v2.py", "Part D: TCGA Tumor Perturbation"),
    ("07_phase34_clinical.py", "Part D (cont.): Clinical Severity Analysis"),
    # Part E: Brain regional analysis
    ("07c_brain_siletti_v3.py", "Part E: Brain Regional Analysis — Human MTG"),
    # Part F: Bootstrap / statistical testing
    ("08a_tcga_bootstrap.py", "Part F: TCGA Bootstrap Significance Testing"),
    # Part G: Method comparison
    ("13_phase35_method_comparison.py", "Part G: Method Comparison — ω vs Standard Metrics"),
    # Part H: Final figures
    ("30_genome_biology_figures.py", "Part H: Final Figures for Genome Biology"),
]

# ── helpers ───────────────────────────────────────────────────────────

def extract_docstring(text: str) -> str | None:
    """Extract the module docstring (first triple-quoted block)."""
    m = re.match(r'^\s*"""\s*\n?(.*?)\n\s*"""', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None

def strip_docstring(text: str) -> str:
    """Remove the module docstring from text, return remainder."""
    return re.sub(r'^\s*""".*?"""\s*\n?', '', text, flags=re.DOTALL, count=1)

def is_section_header(line: str) -> str | None:
    """If line is a # === section marker, return the section title."""
    m = re.match(r'^#\s*=+\s*(.+?)\s*=+\s*$', line)
    if m and len(m.group(1)) > 0:
        title = m.group(1).strip().strip("=").strip()
        if title and title not in ("=", "=="):
            return title
    return None

def is_double_separator(line: str) -> bool:
    """Lines like # ============ (no title)."""
    return bool(re.match(r'^#\s*=+\s*$', line))

def smart_split_cells(code_body: str) -> list[nbf.NotebookNode]:
    """Split code body into alternating markdown (section headers) and code cells."""
    cells = []
    lines = code_body.split("\n")
    
    current_code: list[str] = []
    prev_blank = False
    
    for i, line in enumerate(lines):
        section_title = is_section_header(line)
        
        if section_title:
            # Flush current code block
            if current_code:
                code_str = "\n".join(current_code).strip()
                if code_str:
                    cells.append(nbf.v4.new_code_cell(code_str))
                current_code = []
            # Add markdown header
            cells.append(nbf.v4.new_markdown_cell(f"### {section_title}"))
            prev_blank = False
            continue
        
        if is_double_separator(line):
            # Treat bare separators as cell boundaries
            if current_code:
                code_str = "\n".join(current_code).strip()
                if code_str:
                    cells.append(nbf.v4.new_code_cell(code_str))
                current_code = []
            prev_blank = False
            continue
        
        # Double blank line → cell boundary
        if line.strip() == "":
            if prev_blank and current_code:
                code_str = "\n".join(current_code).strip()
                if code_str:
                    cells.append(nbf.v4.new_code_cell(code_str))
                current_code = []
                prev_blank = False
                continue
            prev_blank = True
            current_code.append(line)
            continue
        
        prev_blank = False
        current_code.append(line)
    
    # Flush trailing code
    if current_code:
        code_str = "\n".join(current_code).strip()
        if code_str:
            cells.append(nbf.v4.new_code_cell(code_str))
    
    return cells

# ── build notebook ────────────────────────────────────────────────────

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12.0",
    },
}

# Title cell
nb.cells.append(nbf.v4.new_markdown_cell(
    "# CKI Reproducibility Notebook\n\n"
    "Combined analysis pipeline for *CKI: A Ka/Ks-inspired metric for quantifying "
    "transcriptomic selection pressure in single-cell data*.\n\n"
    "---\n"
    "**Run sequentially.** Each part writes intermediate results to `results/` "
    "that subsequent parts depend on."
))

# Table of contents
toc_lines = ["## Table of Contents\n"]
for fname, label in CORE_SCRIPTS:
    toc_lines.append(f"- **{label}**  ")
nb.cells.append(nbf.v4.new_markdown_cell("\n".join(toc_lines)))

# Process each script
for fname, label in CORE_SCRIPTS:
    script_path = ROOT / "notebooks" / fname
    if not script_path.exists():
        print(f"  SKIP (missing): {fname}")
        continue
    
    text = script_path.read_text(encoding="utf-8")
    doc = extract_docstring(text)
    body = strip_docstring(text)
    
    # H2 section header
    nb.cells.append(nbf.v4.new_markdown_cell(
        f"## {label}\n\n{doc or ''}"
    ))
    
    # Split body into cells
    sub_cells = smart_split_cells(body)
    nb.cells.extend(sub_cells)
    
    print(f"  OK: {fname} → {1 + len(sub_cells)} cells")

# Write
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, str(OUTPUT))
total = len(nb.cells)
print(f"\nDone: {OUTPUT}  ({total} total cells)")
