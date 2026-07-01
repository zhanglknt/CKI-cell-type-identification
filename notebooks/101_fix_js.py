"""
用正则表达式修复 notebooks/100_gen_reproducibility_docx.js
- Section 3.1: HK gene 描述（与修复后的 markdown 对齐）
- Section 7: 输出文件名
"""
import re

JS = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\100_gen_reproducibility_docx.js"

with open(JS, "r", encoding="utf-8") as f:
    content = f.read()

count = 0

# ── 1. 替换 Section 3.1（HK genes） ─────────────────────────────
# 匹配从 heading("3.1 Housekeeping...) 到下一个 heading(...) 之间的所有 p(...) 行
pattern_31 = r"""(heading\(\"3\.1 Housekeeping[^\"]*?\",\s*\d+\),\s*\n)(\s*)"""
# 更实用的方案：直接查找并替换关键旧字符串

old_texts_31 = [
    'p("Housekeeping (HK) genes are defined by two intrinsic, data-driven criteria:"),',
    'p("Ubiquity: expressed in > 90% of cells (detection rate > 0.9)."),',
    'p("Stability: coefficient of variation (CV) below the 30th percentile among well-expressed genes (mean > 0.5)."),',
    'p("The \\"combined\\" method requires BOTH criteria. This is the default."),',
    'p("For human and mouse datasets, the HRT Atlas reference set (Hounkpe et al., Nucleic Acids Research, 2021) is bundled with CKI at cki/data/hrt_atlas.csv. It contains 1,064 human-mouse orthologous housekeeping gene pairs."),',
    'p("In the analyses reported here:", { bold: true }),',
    'p("    Tabula Muris (mouse):   HRT Atlas + combined detection, union merge."),',
    'p("    Tabula Sapiens (human): combined detection only (use_reference=False)."),',
    'p("    TCGA (human):           HRT Atlas + combined detection, union merge."),',
    'p("    Siletti Brain (human):  HRT Atlas gene symbols matched to var[\\"Gene\\"]."),',
]

new_texts_31 = [
    'p("In the analyses reported here, housekeeping (HK) genes were NOT"),',
    'p("auto-detected. Instead, pre-specified HK gene lists were loaded"),',
    'p("from the HRT Atlas reference file:"),',
    'p(""),',
    'p("  data/housekeeping/Human_Mouse_Common.csv"),',
    'p("  (1,130 orthologous gene pairs; Mouse column = mouse genes,"),',
    'p("  Human column = human genes; format identical to cki/data/hrt_atlas.csv)"),',
    'p(""),',
    'p("For each dataset, HK genes were loaded as follows:"),',
    'p(""),',
    'p("    Tabula Muris (mouse):  HRT Atlas mouse genes (column 0),"),',
    'p("                              intersected with data gene names"),',
    'p(""),',
    'p("    Tabula Sapiens (human):  HRT Atlas human genes (column 1),"),',
    'p("                              intersected with common gene set"),',
    'p(""),',
    'p("    TCGA (human):           HRT Atlas human genes (column 1),"),',
    'p("                              mapped via probeMap to Ensembl IDs,"),',
    'p("                              then intersected with data genes"),',
    'p(""),',
    'p("    Siletti Brain (human):  HRT Atlas human genes (column 1)"),',
    'p("                              matched to var[\\"Gene\\"] in the h5ad file"),',
    'p(""),',
    'p("Note: CKI supports data-driven HK auto-detection via"),',
    'p("`detect_housekeeping_genes()` (detection rate > 0.9, CV < 30th"),',
    'p("percentile, \\"combined\\" method; use_reference=True merges HRT Atlas)."),',
    'p("This auto-detection was NOT used in the current analyses"),',
    'p("(the pre-specified list approach was preferred for reproducibility),"),',
    'p("but is available for new datasets without a curated HK list."),',
]

print("=== 修复 Section 3.1 ===")
for old, new in zip(old_texts_31, new_texts_31):
    if old in content:
        content = content.replace(old, new, 1)
        count += 1
        print(f"  ✅ [{count}] {old[:60]!r}")
    else:
        print(f"  ⚠ 未找到: {old[:60]!r}")

print(f"\nSection 3.1: 替换了 {count} 处\n")

# ── 2. 替换 Section 7 输出文件名 ───────────────────────────────
old_files = [
    'code("Mouse:    results/mouse_pilot_v2b_omega_hybrid.csv"),',
    'code("Human:    results/ts_human_omega_hybrid_v3.csv"),',
    'code("TCGA:     results/tcga_omega_v2.csv"),',
    'code("Brain:    results/brain_siletti_ct_summary_v3.csv"),',
    'code("             results/brain_siletti_omega_pairs_v3.csv"),',
    'code("             results/brain_siletti_migration_candidates_v3.csv"),',
]

new_files = [
    'p("    Mouse (02c_pilot_v2b.py):"),',
    'code("      results/mouse_pilot_v2b_results.csv        # omega per pair"),',
    'code("      results/mouse_pilot_v2b_key_values.csv   # k_n, k_f, omega per comparison"),',
    'p(""),',
    'p("    Human (05_phase33_v3_fixed.py):"),',
    'code("      results/phase33_v3_human_omega.csv        # omega matrix (cell-types x cell-types)"),',
    'code("      results/phase33_v3_human_kn.csv           # k_n matrix"),',
    'code("      results/phase33_v3_human_kf.csv          # k_f matrix"),',
    'code("      results/phase33_v3_human_pairs.csv       # long-form pair list with omega"),',
    'p(""),',
    'p("    TCGA (06_phase34_v2.py):"),',
    'code("      results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega"),',
    'code("      results/phase34_v2_summary.csv           # per-cancer summary statistics"),',
    'code("      results/phase34_v2_{cancer}_pairs.csv  # per-cancer pair files"),',
    'p(""),',
    'p("    Brain (07d_brain_siletti_v4.py):"),',
    'code("      results/brain_siletti_v4_omega_pairs.csv        # all region-pair omega values"),',
    'code("      results/brain_siletti_v4_ct_summary.csv          # per-cell-type mean omega"),',
    'code("      results/brain_siletti_v4_migration_candidates.csv # migration candidate list"),',
    'p(""),',
    'p("Figure scripts: notebooks/30_nar_figures_fixed_v2.py"),',
]

print("=== 修复 Section 7 ===")
count2 = 0
for old, new in zip(old_files, new_files):
    if old in content:
        content = content.replace(old, new, 1)
        count2 += 1
        print(f"  ✅ [{count2}] {old[:60]!r}")
    else:
        print(f"  ⚠ 未找到: {old[:60]!r}")

print(f"\nSection 7: 替换了 {count2} 处\n")

# ── 3. 替换所有残留的 "1,064" ─────────────────────────────
count3 = content.count("1,064")
if count3 > 0:
    content = content.replace("1,064", "1,130")
    print(f"✅ 替换了 {count3} 处 '1,064' → '1,130'")
else:
    print("✅ 无残留 '1,064'")

# ── 保存 ─────────────────────────────────────────────────────────
with open(JS, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ 已保存: {JS}")
print(f"   共替换: Section3.1={count}, Section7={count2}, 1,064={count3}")
