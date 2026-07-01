"""
Fix 100_gen_reproducibility_docx.js
- Section 3.1: replace old HK description with new one
- Section 7: replace output file names
Uses line-number-based replacement (read lines, replace slice, write back).
"""
JS = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\100_gen_reproducibility_docx.js"

with open(JS, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# ── 1. Fix Section 3.1 (lines ~207-219) ──────────────────────────
# Find start: line containing 'heading("3.1 Housekeeping'
# Find end: line containing 'heading("3.2'
start_31 = None
end_31 = None
for i, ln in enumerate(lines):
    if 'heading("3.1 Housekeeping' in ln:
        start_31 = i
    if start_31 is not None and i > start_31:
        if 'heading("3.2' in ln:
            end_31 = i
            break

assert start_31 is not None, "Cannot find Section 3.1 start!"
assert end_31 is not None, "Cannot find Section 3.1 end!"
print(f"Section 3.1: lines [{start_31}, {end_31})")

new_31 = [
    '      heading("3.1 Housekeeping Genes (for k_n)", 3),\n',
    '      p("In the analyses reported here, housekeeping (HK) genes were NOT"),\n',
    '      p("auto-detected. Instead, pre-specified HK gene lists were loaded"),\n',
    '      p("from the HRT Atlas reference file:"),\n',
    '      p(""),\n',
    '      p("  data/housekeeping/Human_Mouse_Common.csv"),\n',
    '      p("  (1,130 orthologous gene pairs; Mouse column = mouse genes,"),\n',
    '      p("  Human column = human genes; format identical to cki/data/hrt_atlas.csv)"),\n',
    '      p(""),\n',
    '      p("For each dataset, HK genes were loaded as follows:"),\n',
    '      p(""),\n',
    '      p("    Tabula Muris (mouse):  HRT Atlas mouse genes (column 0),"),\n',
    '      p("                              intersected with data gene names"),\n',
    '      p(""),\n',
    '      p("    Tabula Sapiens (human):  HRT Atlas human genes (column 1),"),\n',
    '      p("                              intersected with common gene set"),\n',
    '      p(""),\n',
    '      p("    TCGA (human):           HRT Atlas human genes (column 1),"),\n',
    '      p("                              mapped via probeMap to Ensembl IDs,"),\n',
    '      p("                              then intersected with data genes"),\n',
    '      p(""),\n',
    '      p("    Siletti Brain (human):  HRT Atlas human genes (column 1)"),\n',
    '      p("                              matched to var[\\"Gene\\"] in the h5ad file"),\n',
    '      p(""),\n',
    '      p("Note: CKI supports data-driven HK auto-detection via"),\n',
    '      p("`detect_housekeeping_genes()` (detection rate > 0.9, CV < 30th"),\n',
    '      p("percentile, \\"combined\\" method; use_reference=True merges HRT Atlas)."),\n',
    '      p("This auto-detection was NOT used in the current analyses"),\n',
    '      p("(the pre-specified list approach was preferred for reproducibility),"),\n',
    '      p("but is available for new datasets without a curated HK list."),\n',
]

# Replace lines[start_31+1 : end_31] (keep the heading line)
lines[start_31+1 : end_31] = new_31[1:]  # skip heading, already in new_31[0]
# Actually, replace from start_31 to end_31-1 (keep heading at start_31, next heading at end_31)
lines[start_31 : end_31] = new_31
print(f"  → replaced with {len(new_31)} lines")

# ── 2. Fix Section 7 output file names ────────────────────────────────
# Find Section 7: line containing 'heading("7. Output Files'
start_7 = None
for i, ln in enumerate(lines):
    if 'heading("7. Output Files' in ln:
        start_7 = i
        break
assert start_7 is not None, "Cannot find Section 7 start!"

# Find end of Section 7: next heading (8.)
end_7 = None
for i in range(start_7 + 1, len(lines)):
    if 'heading("8.' in lines[i]:
        end_7 = i
        break
assert end_7 is not None, "Cannot find Section 7 end!"
print(f"Section 7: lines [{start_7}, {end_7})")

new_7 = [
    '      heading("7. Output Files", 2),\n',
    '      p("All results are written to results/:"),\n',
    '      p(""),\n',
    '      p("    Mouse (02c_pilot_v2b.py):"),\n',
    '      code("      results/mouse_pilot_v2b_results.csv        # omega per pair"),\n',
    '      code("      results/mouse_pilot_v2b_key_values.csv   # k_n, k_f, omega per comparison"),\n',
    '      p(""),\n',
    '      p("    Human (05_phase33_v3_fixed.py):"),\n',
    '      code("      results/phase33_v3_human_omega.csv        # omega matrix (cell-types x cell-types)"),\n',
    '      code("      results/phase33_v3_human_kn.csv           # k_n matrix"),\n',
    '      code("      results/phase33_v3_human_kf.csv          # k_f matrix"),\n',
    '      code("      results/phase33_v3_human_pairs.csv       # long-form pair list with omega"),\n',
    '      p(""),\n',
    '      p("    TCGA (06_phase34_v2.py):"),\n',
    '      code("      results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega"),\n',
    '      code("      results/phase34_v2_summary.csv           # per-cancer summary statistics"),\n',
    '      code("      results/phase34_v2_{cancer}_pair.csv  # per-cancer pair files"),\n',
    '      p(""),\n',
    '      p("    Brain (07d_brain_siletti_v4.py):"),\n',
    '      code("      results/brain_siletti_v4_omega_pairs.csv        # all region-pair omega values"),\n',
    '      code("      results/brain_siletti_v4_ct_summary.csv          # per-cell-type mean omega"),\n',
    '      code("      results/brain_siletti_v4_migration_candidates.csv # migration candidate list"),\n',
    '      p(""),\n',
    '      p("Figure scripts: notebooks/30_nar_figures_fixed_v2.py"),\n',
]

lines[start_7 : end_7] = new_7
print(f"  → replaced with {len(new_7)} lines")

# ── 3. Fix any remaining "1,064" or "1064" ──────────────────────────
count_1064 = 0
for i, ln in enumerate(lines):
    if '1,064' in ln or '1064' in ln:
        lines[i] = ln.replace('1,064', '1,130').replace('1064', '1130')
        count_1064 += 1
        print(f"  Fixed 1,064 → 1,130 at line {i+1}")
print(f"Total 1,064 fixes: {count_1064}")

# ── Save ────────────────────────────────────────────────────────────────────
with open(JS, "w", encoding="utf-8") as f:
    f.writelines(lines)
print(f"\n✅ Saved: {JS}")
print(f"   New total lines: {len(lines)}")
