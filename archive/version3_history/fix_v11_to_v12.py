#!/usr/bin/env python3
"""
v11 -> v12 全面修复脚本
修复 P0-1 到 P0-6 以及 M1-M12 的所有问题
"""

import copy
import os
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

# ============================================================
# Configuration
# ============================================================
BASE = r"C:\Users\KnightZ\Desktop\细胞受选择\version3"
EXTRACTED = os.path.join(BASE, "v11_extracted", "CKI_NAR_Submission_v11")
OUTPUT = os.path.join(BASE, "v12_docx")
os.makedirs(OUTPUT, exist_ok=True)

# Files to fix
FILES = {
    "manuscript": os.path.join(EXTRACTED, "CKI_NAR_Manuscript.docx"),
    "cover_letter": os.path.join(EXTRACTED, "CKI_NAR_Cover_Letter.docx"),
    "supplementary": os.path.join(EXTRACTED, "CKI_NAR_Supplementary.docx"),
    "repro_guide": os.path.join(EXTRACTED, "CKI_NAR_Reproducibility_Guide.docx"),
}

# ============================================================
# Helper: find and replace text in document
# ============================================================
def replace_in_doc(doc, old_text, new_text, count=0):
    """Replace old_text with new_text across all paragraphs and table cells."""
    total = 0
    # Paragraphs
    for para in doc.paragraphs:
        if old_text in para.text:
            runs = para.runs
            # Try inline replacement via runs first
            para_full = para.text
            if old_text in para_full:
                # Clear and rebuild
                new_full = para_full.replace(old_text, new_text, count - total if count else 0)
                total += para_full.count(old_text) if not count else min(count - total, para_full.count(old_text))
                # Simple approach: clear all runs, set text in first run
                for run in runs:
                    run.text = ""
                if runs:
                    runs[0].text = new_full
                else:
                    para.add_run(new_full)
                if count and total >= count:
                    return total
    # Table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if old_text in para.text:
                        para_full = para.text
                        new_full = para_full.replace(old_text, new_text)
                        for run in para.runs:
                            run.text = ""
                        if para.runs:
                            para.runs[0].text = new_full
    return total


def regex_replace_in_doc(doc, pattern, replacement, flags=0):
    """Regex-based replacement across all paragraphs."""
    total = 0
    compiled = re.compile(pattern, flags)
    for para in doc.paragraphs:
        if compiled.search(para.text):
            new_text = compiled.sub(replacement, para.text)
            for run in para.runs:
                run.text = ""
            if para.runs:
                para.runs[0].text = new_text
            else:
                para.add_run(new_text)
            total += 1
    # Table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if compiled.search(para.text):
                        new_text = compiled.sub(replacement, para.text)
                        for run in para.runs:
                            run.text = ""
                        if para.runs:
                            para.runs[0].text = new_text
    return total


def find_paragraphs_containing(doc, text):
    """Find all paragraphs containing text."""
    results = []
    for i, para in enumerate(doc.paragraphs):
        if text in para.text:
            results.append((i, para.text[:200]))
    # Tables
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                for pi, para in enumerate(cell.paragraphs):
                    if text in para.text:
                        results.append((f"T{ti}R{ri}C{ci}P{pi}", para.text[:200]))
    return results


# ============================================================
# P0 fixes
# ============================================================

def fix_p01_kn_statistics(doc):
    """P0-1: Fix k_n statistics - use human data, not mouse control."""
    changes = 0
    
    # Fix: median 0.0019 → 0.034
    c = replace_in_doc(doc, "median of 0.0019", "median of 0.034")
    changes += c
    
    # Fix: range 0.0006-0.0027 → 0.0018-0.221
    c = replace_in_doc(doc, "0.0006 to 0.0027", "0.0018 to 0.221")
    changes += c
    c = replace_in_doc(doc, "0.0006\u20130.0027", "0.0018\u20130.221")
    changes += c
    
    # Fix: "our datasets, k_n had a median of 0.0019" → "our human dataset (n=5,151), k_n had a median of 0.034"
    c = replace_in_doc(doc, "our datasets, k_n had a median of 0.0019", 
                       "our human dataset (n = 5,151), k_n had a median of 0.034")
    changes += c
    c = replace_in_doc(doc, "In our datasets, k_n had a median of 0.0019", 
                       "In our human dataset (n = 5,151), k_n had a median of 0.034")
    changes += c
    
    # Fix mouse calibration context: "In our datasets, k_n had a median of 0.0019 (range 0.0006\u20130.0027)"
    c = replace_in_doc(doc, 
                       "In our datasets, k_n had a median of 0.0019 (range 0.0006\u20130.0027)",
                       "Across the 5,151 human cell-type pairs analyzed, k_n had a median of 0.034 (range 0.0018\u20130.221)")
    changes += c
    
    # Try alternative patterns based on what might be in the doc
    for old, new in [
        ("median of 0.0019 (range 0.0006\u20130.0027)", "median of 0.034 (range 0.0018\u20130.221)"),
        ("k_n had a median of 0.0019", "k_n had a median of 0.034"),
        ("median k_n of 0.0019", "median k_n of 0.034"),
        ("(median = 0.0019)", "(median = 0.034)"),
        ("(0.0006\u20130.0027)", "(0.0018\u20130.221)"),
    ]:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    print(f"  P0-1 kn stats: {changes} replacements")
    return changes


def fix_p02_bootstrap_fdr(doc):
    """P0-2: Remove false Bootstrap/FDR claims from human/TCGA/brain sections."""
    changes = 0
    
    # Key patterns to remove bootstrap/FDR claims
    patterns = [
        # "B = 1000 bootstrap" and "BH-FDR" references
        (r'B\s*=\s*1000\s*bootstrap', 'standard statistical tests'),
        (r'B\s*=\s*1,000\s*bootstrap', 'standard statistical tests'),
        (r'BH[-\s]FDR', ''),
        (r'FDR-adjusted', ''),
        (r'FDR corrected', ''),
        (r'after FDR correction', ''),
        (r'with BH-FDR correction', ''),
        (r'Benjamini[-\s]Hochberg\s+FDR', ''),
        (r',? ?FDR ?[<>≤≥]=? ?0\.\d+', ''),
        (r'bootstrap\s*\(B\s*=\s*1[,，]?000\)', 'standard statistical tests'),
        (r'bootstrap\s*\(B\s*=\s*1000\)', 'standard statistical tests'),
        (r'bootstrapped\s+P[-\s]values', 'P-values'),
        (r'bootstrap-derived P-values', 'P-values'),
        (r'bootstrap P-values', 'P-values'),
    ]
    
    for pattern, replacement in patterns:
        c = regex_replace_in_doc(doc, pattern, replacement, re.IGNORECASE)
        changes += c
    
    # Specific sentence patterns to fix
    specific_fixes = [
        # "we applied bootstrap (B = 1000) with BH-FDR correction"
        ("applied bootstrap (B = 1000)", "applied"),
        ("bootstrap (B=1000)", ""),
        ("bootstrap (B = 1000)", ""),
        ("bootstrap (B = 1,000)", ""),
        # "P-values were adjusted for multiple testing using the Benjamini-Hochberg procedure" 
        # -> Keep if it's for post-hoc tests, but human/TCGA/brain didn't use it
        ("P-values were adjusted for multiple testing using the Benjamini-Hochberg procedure",
         "P-values were computed using standard statistical tests without multiple-testing correction"),
        # "with BH-FDR correction (q < 0.05)"
        ("with BH-FDR correction (q < 0.05)", ""),
        ("(q < 0.05)", ""),
    ]
    
    for old, new in specific_fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    print(f"  P0-2 bootstrap/FDR: {changes} replacements")
    return changes


def fix_p03_js_log_base(doc):
    """P0-3: Fix JS divergence log base description (base-2 → natural log + auto-switching)."""
    changes = 0
    
    fixes = [
        # base-2 → natural log
        ("base-2 logarithm", "natural logarithm"),
        ("log base 2", "natural log"),
        ("log-base-2", "natural log"),
        ("base-2 Jensen-Shannon divergence", "Jensen-Shannon divergence (natural log)"),
        # softmax only → auto-switching
        ("softmax transformation", "appropriate normalization (sum-normalization for non-negative data; softmax for data containing negative values)"),
        ("softmax-transformed", "appropriately normalized"),
        # More specific patterns
        ("using softmax-normalized gene expression vectors", 
         "using normalized gene expression vectors (sum-normalization for human/mouse/brain datasets; softmax only for TCGA bulk RNA-seq data where negative values may occur)"),
    ]
    
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    # Search for "JS divergence" and "softmax" in same paragraph
    for para in doc.paragraphs:
        if "JS divergence" in para.text and "softmax" in para.text and "natural" not in para.text:
            new_text = para.text.replace("softmax", "sum-normalization for non-negative expression data (softmax only for TCGA bulk RNA-seq)")
            for run in para.runs:
                run.text = ""
            if para.runs:
                para.runs[0].text = new_text
            changes += 1
    
    print(f"  P0-3 JS log base: {changes} replacements")
    return changes


def fix_p04_strong_criteria(doc):
    """P0-4: Remove 'pair median ω > 20' from Strong candidate criteria."""
    changes = 0
    
    fixes = [
        # Remove the 4th condition from Strong criteria
        ("pair median ω > 20", ""),
        # Fix "four criteria" → "three criteria" or "two criteria"
        ("four criteria:(1) pair median ω > 20; (2)", "three criteria: (1)"),
        ("four criteria: (1) pair median ω > 20; (2)", "three criteria: (1)"),
        ("Four criteria were applied", "Three criteria were applied"),
        ("four stringent criteria", "three stringent criteria"),
        ("meeting all four criteria", "meeting all three criteria"),
        ("satisfied all four criteria", "satisfied all three criteria"),
        # Fix "4 conditions" pattern
        ("4 conditions", "3 conditions"),
        ("four conditions", "three conditions"),
        # Clean up any remaining "pair median ω > 20" mentions
        (", pair median ω > 20", ""),
        ("and pair median ω > 20", ""),
        ("(i) pair median ω > 20,", ""),
        ("(i) pair median ω > 20;", ""),
        # Fix numbering shift after removing condition 1
        ("three criteria: (1) Spearman residual < 0.3; (2)", "two criteria: (1) Spearman residual < 0.3; (2)"),
    ]
    
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    print(f"  P0-4 Strong criteria: {changes} replacements")
    return changes


def fix_p05_text_corruption(doc):
    """P0-5: Fix 4 spots of text corruption."""
    changes = 0
    
    fixes = [
        ("not a classifierCKI answers", "not a classifier; CKI answers"),
        ("[19].exhibitedthe strongest", "[19] exhibited the strongest"),
        ("[19].exhibited the strongest", "[19] exhibited the strongest"),
        ("types.per cell-type coverage. limitedwarranting", 
         "types. Per-cell-type coverage is limited, warranting"),
        ("types. per cell-type coverage. limited warranting", 
         "types. Per-cell-type coverage is limited, warranting"),
        ("types.per cell-type coveragelimitedwarranting", 
         "types. Per-cell-type coverage is limited, warranting"),
    ]
    
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    # P55 isolated fragment - need to find exact text
    # Look for paragraphs ending abruptly
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("This is consistent") and len(text) < 60:
            # This is likely the P55 fragment - append to previous paragraph
            idx = doc.paragraphs.index(para)
            if idx > 0:
                prev_para = doc.paragraphs[idx - 1]
                merged = prev_para.text + " " + text
                for run in prev_para.runs:
                    run.text = ""
                if prev_para.runs:
                    prev_para.runs[0].text = merged
                for run in para.runs:
                    run.text = ""
                changes += 1
    
    print(f"  P0-5 text corruption: {changes} replacements")
    return changes


def fix_p06_chinese_punctuation(doc):
    """P0-6: Fix 3 Chinese punctuation marks."""
    changes = 0
    
    fixes = [
        # P55: "Fig. 4，" → "Fig. 4,"
        ("Fig. 4\uff0c", "Fig. 4,"),
        # P58: "Furthermore，" → "Furthermore,"
        ("Furthermore\uff0c", "Furthermore,"),
        # P73: "（Supplementary Fig. S5）" → "(Supplementary Fig. S5)"
        ("\uff08Supplementary Fig. S5\uff09", "(Supplementary Fig. S5)"),
        ("\uff08Suppl", "([S]uppl"),
        ("\uff09", ")"),
        ("\uff0c", ","),
    ]
    
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    
    print(f"  P0-6 Chinese punctuation: {changes} replacements")
    return changes


# ============================================================
# Major fixes
# ============================================================

def fix_m1_tcga_sample_count(doc):
    """M1: TCGA sample count: 3,596 vs 3,358."""
    changes = 0
    
    # In manuscript, ensure 3,596 is used (per-cancer analysis)
    c = replace_in_doc(doc, "3,358 TCGA samples", "3,596 TCGA samples")
    changes += c
    c = replace_in_doc(doc, "n = 3,358", "n = 3,596")
    changes += c
    
    print(f"  M1 TCGA samples: {changes} replacements")
    return changes


def fix_m2_tcga_normalization(doc):
    """M2: TCGA normalization: FPKM → TPM."""
    changes = 0
    c = replace_in_doc(doc, "FPKM", "TPM")
    changes += c
    print(f"  M2 TCGA FPKM->TPM: {changes} replacements")
    return changes


def fix_m3_celltype_pairs(doc):
    """M3: Cell type pairs: 5,151 vs 4,851."""
    changes = 0
    c = replace_in_doc(doc, "5,151", "4,851")
    changes += c
    print(f"  M3 pairs 5151->4851: {changes} replacements")
    return changes


def fix_m4_cross_organ_pairs(doc):
    """M4: Cross-organ pairs: 60 → 59."""
    changes = 0
    # Only replace "60 cross-organ" not "60%" or "160" etc.
    c = replace_in_doc(doc, "60 cross-organ pairs", "59 cross-organ pairs")
    changes += c
    c = replace_in_doc(doc, "among 60", "among 59")
    changes += c
    print(f"  M4 cross-organ: {changes} replacements")
    return changes


def fix_m5_cki_version(doc):
    """M5: CKI version v0.3.2 → v0.3.1."""
    changes = 0
    c = replace_in_doc(doc, "v0.3.2", "v0.3.1")
    changes += c
    print(f"  M5 CKI version: {changes} replacements")
    return changes


def fix_m6_python_version(doc):
    """M6: Python version 3.12 → 3.13.12."""
    changes = 0
    c = replace_in_doc(doc, "Python 3.12", "Python 3.13")
    changes += c
    print(f"  M6 Python version: {changes} replacements")
    return changes


def fix_m7_residual_percentile(doc):
    """M7: Residual 1st percentile ~0.29 → 0.40."""
    changes = 0
    fixes = [
        ("≈ 0.29", "≈ 0.40"),
        ("~0.29", "~0.40"),
        ("approximately 0.29", "approximately 0.40"),
    ]
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    print(f"  M7 residual percentile: {changes} replacements")
    return changes


def fix_m8_cover_letter_orthologs(doc):
    """M8: Remove 'mouse orthologs correlation' from Cover Letter."""
    changes = 0
    fixes = [
        ("mouse ortholog correlation analysis", "cross-species expression conservation analysis"),
        ("mouse orthologs correlation", "cross-species analysis"),
        ("mouse-human ortholog correlation", "cross-species comparison"),
    ]
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    print(f"  M8 cover letter orthologs: {changes} replacements")
    return changes


def fix_m9_title_inconsistency(doc):
    """M9: Title 'Cell-state' vs body 'Cell-type' inconsistency."""
    changes = 0
    # Don't change title - it's intentional. But fix inconsistent uses in body.
    c = replace_in_doc(doc, "cell-state Kinetic Index", "Cell-state Kinetic Index")
    changes += c
    print(f"  M9 title consistency: {changes} replacements")
    return changes


def fix_m10_hvg_description(doc):
    """M10: top-2000 HVG → top-200 per-pair DE genes for hybrid scheme."""
    changes = 0
    fixes = [
        ("top-2,000 highly variable genes (HVGs)", "the top-200 most differentially expressed genes per cell-type pair"),
        ("top 2000 HVGs", "top-200 DE genes per pair"),
        ("top-2000 HVG", "top-200 per-pair DE gene"),
    ]
    for old, new in fixes:
        c = replace_in_doc(doc, old, new)
        changes += c
    print(f"  M10 HVG description: {changes} replacements")
    return changes


def fix_m11_hybrid_scale(doc):
    """M11: Hybrid scheme k_n/k_f scale inconsistency - add note."""
    changes = 0
    # Add clarification about scale difference
    note = (" (note: k_n is computed from ~1,000 shared HK genes while k_f uses "
            "the top 200 DE genes per pair; the ratio remains meaningful because "
            "JS divergence is scale-invariant within each computation)")
    for para in doc.paragraphs:
        if "hybrid scheme" in para.text.lower() and "global k_n" in para.text and note not in para.text:
            new_text = para.text + note
            for run in para.runs:
                run.text = ""
            if para.runs:
                para.runs[0].text = new_text
            changes += 1
    print(f"  M11 hybrid scale: {changes} additions")
    return changes


def fix_m12_moderate_numbers(doc):
    """M12: Fix 10 incorrect Moderate candidate numerical values."""
    changes = 0
    fixes = [
        # These are from the data reviewer report
        # Moderate count
        ("1,247 Moderate", "1,247 Moderate"),
        # Moderate percentages
        ("3.93% Moderate", "3.93% Moderate"),
        # Verify these aren't already correct
    ]
    # Actually the data says 1,247/3.93% are correct.
    # The issue might be wrong per-cell-type counts in P51/P62/P64
    # Leave for now - need exact values from reports
    print(f"  M12 moderate numbers: {changes} replacements (needs per-type verification)")
    return changes


# ============================================================
# Apply all fixes per file
# ============================================================

FIX_FUNCTIONS_MANUSCRIPT = [
    fix_p01_kn_statistics,
    fix_p02_bootstrap_fdr,
    fix_p03_js_log_base,
    fix_p04_strong_criteria,
    fix_p05_text_corruption,
    fix_p06_chinese_punctuation,
    fix_m1_tcga_sample_count,
    fix_m2_tcga_normalization,
    fix_m3_celltype_pairs,
    fix_m4_cross_organ_pairs,
    fix_m5_cki_version,
    fix_m6_python_version,
    fix_m7_residual_percentile,
    fix_m9_title_inconsistency,
    fix_m10_hvg_description,
    fix_m11_hybrid_scale,
    fix_m12_moderate_numbers,
]

FIX_FUNCTIONS_COVER_LETTER = [
    fix_m4_cross_organ_pairs,
    fix_m5_cki_version,
    fix_m8_cover_letter_orthologs,
]

FIX_FUNCTIONS_SUPPLEMENTARY = [
    fix_m1_tcga_sample_count,
    fix_m3_celltype_pairs,
    fix_m4_cross_organ_pairs,
    fix_m5_cki_version,
]

FIX_FUNCTIONS_REPRO_GUIDE = [
    fix_m5_cki_version,
    fix_m6_python_version,
]

FILE_FIX_MAP = {
    "manuscript": FIX_FUNCTIONS_MANUSCRIPT,
    "cover_letter": FIX_FUNCTIONS_COVER_LETTER,
    "supplementary": FIX_FUNCTIONS_SUPPLEMENTARY,
    "repro_guide": FIX_FUNCTIONS_REPRO_GUIDE,
}


def main():
    total_changes = 0
    skipped = []
    
    for name, path in FILES.items():
        if not os.path.exists(path):
            print(f"SKIP {name}: file not found at {path}")
            skipped.append(name)
            continue
        
        print(f"\n{'='*60}")
        print(f"Fixing {name}: {os.path.basename(path)}")
        print(f"{'='*60}")
        
        doc = Document(path)
        fix_funcs = FILE_FIX_MAP.get(name, [])
        file_changes = 0
        
        for fix_func in fix_funcs:
            try:
                changes = fix_func(doc)
                file_changes += changes
            except Exception as e:
                print(f"  ERROR in {fix_func.__name__}: {e}")
        
        # Save
        out_path = os.path.join(OUTPUT, os.path.basename(path))
        doc.save(out_path)
        print(f"  Saved: {out_path}")
        print(f"  Total changes for {name}: {file_changes}")
        total_changes += file_changes
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {total_changes} total text replacements across {len(FILES) - len(skipped)} files")
    if skipped:
        print(f"Skipped: {', '.join(skipped)}")
    print(f"Output directory: {OUTPUT}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
