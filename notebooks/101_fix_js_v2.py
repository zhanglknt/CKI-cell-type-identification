"""
用行号精确替换 JS 文件中 Section 3.1 和 Section 7 的内容。
读取 JS 文件 → 找到行号 → 整段替换 → 写回。
"""
JS = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\100_gen_reproducibility_docx.js"

with open(JS, "r", encoding="utf-8") as f:
    lines = f.readlines()

# ── 1. 找到 Section 3.1 的起始和结束行号 ──────────────────────
# Section 3.1 起始：包含 '3.1 Housekeeping Genes' 的行
# Section 3.1 结束：下一个 heading 行（包含 '3.2' 或 heading( 的行）
s31_start = None
s31_end = None
for i, ln in enumerate(lines):
    if '3.1 Housekeeping Genes' in ln:
        s31_start = i
    if s31_start is not None and i > s31_start:
        if '3.2 Identity Genes' in ln:
            s31_end = i
            break

print(f"Section 3.1 行号范围: [{s31_start}, {s31_end})")
print(f"当前内容预览：")
for i in range(s31_start, min(s31_end, s31_start + 15)):
    print(f"  {i+1}: {lines[i].rstrip()}")

# ── 2. 构造新的 Section 3.1 内容 ─────────────────────────────
new_s31 = [
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

# 替换
assert s31_start is not None, "找不到 Section 3.1 起始行！"
assert s31_end is not None, "找不到 Section 3.1 结束行！"
lines[s31_start:s31_end] = new_s31
print(f"✅ Section 3.1 已替换（{s31_end - s31_start} 行 → {len(new_s31)} 行）")

# ── 3. 找到 Section 7 的输出文件名行并替换 ─────────────────────────
# Section 7 包含 'All results are written to results/:" 的行
# 后面跟着 code("...") 行
s7_start = None
for i, ln in enumerate(lines):
    if 'All results are written to results/' in ln:
        s7_start = i
        break

assert s7_start is not None, "找不到 Section 7 起始行！"
print(f"\nSection 7 起始行: {s7_start + 1}")

# 找到 Section 7 中所有 code(...) 行并替换
replacements_7 = {
    'results/mouse_pilot_v2b_omega_hybrid.csv':
        'results/mouse_pilot_v2b_results.csv",
      code("      results/mouse_pilot_v2b_key_values.csv   # k_n, k_f, omega per comparison"),',
    'results/ts_human_omega_hybrid_v3.csv':
        'results/phase33_v3_human_omega.csv        # omega matrix (cell-types x cell-types)",
      code("      results/phase33_v3_human_kn.csv           # k_n matrix"),
      code("      results/phase33_v3_human_kf.csv          # k_f matrix"),
      code("      results/phase33_v3_human_pairs.csv       # long-form pair list with omega"),',
    'results/tcga_omega_v2.csv':
        'results/phase34_v2_all_pairs.csv          # all TT/NN/TN pairs with omega)",
      code("      results/phase34_v2_summary.csv           # per-cancer summary statistics)"),
      code("      results/phase34_v2_{cancer}_pairs.csv  # per-cancer pair files"),',
    'results/brain_siletti_ct_summary_v3.csv':
        'results/brain_siletti_v4_ct_summary.csv          # per-cell-type mean omega)",
      code("      results/brain_siletti_v4_omega_pairs.csv        # all region-pair omega values)"),
      code("      results/brain_siletti_v4_migration_candidates.csv # migration candidate list"),',
}

count_7 = 0
for i, ln in enumerate(lines):
    for old_substr, new_substr in replacements_7.items():
        if old_substr in ln:
            lines[i] = '      code("' + new_substr + '\n'
            count_7 += 1
            print(f"  ✅ 行 {i+1}: {old_substr[:50]}...")

print(f"\nSection 7: 替换了 {count_7} 处")

# ── 4. 检查是否还有残留的 1,064 ─────────────────────────────────
count_1064 = sum(1 for ln in lines if '1,064' in ln or '1064' in ln)
if count_1064 > 0:
    print(f"\n⚠  警告：还有 {count_1064} 处残留 '1,064'！")
else:
    print(f"\n✅ 无残留 '1,064'")

# ── 5. 保存 ─────────────────────────────────────────────────────
with open(JS, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"\n✅ 已保存: {JS}")
print(f"   行数变化: {len(lines)} 行")
