# -*- coding: utf-8 -*-
"""v47 图表编号顺序审计（GB 惯例：按正文首次引用顺序编码）。
检查：主图 1-6 / 主表 / 附图 S1-S13 / 附表 / Additional file 1-N。"""
import io, re

WD = r'C:\Users\KnightZ\Desktop\细胞受选择\version3\CKI_Submission_v47'
ms = io.open(WD + r'\CKI_Manuscript_fulltext.txt', encoding='utf-8').read()
sn = io.open(WD + r'\CKI_Supplementary_fulltext.txt', encoding='utf-8').read()
tb = io.open(WD + r'\Table1-2_fulltext.txt', encoding='utf-8').read()

# 切掉 References 之后的正文范围（图表引用只在正文与图例中）
ms_body_end = ms.find('References\n')
ms_body = ms[:ms_body_end] if ms_body_end > 0 else ms
ms_legends = ms[ms_body_end:] if ms_body_end > 0 else ''

def first_occurrences(text, pattern, name_group=1):
    """返回按位置排序的 (pos, 编号) 列表"""
    out = []
    for m in re.finditer(pattern, text):
        out.append((m.start(), m.group(name_group)))
    return out

issues = []

# ---- 1. 主图 Figure N / Fig. N 引用顺序 ----
pat_main = r'(?:Figure|Fig\.?)\s+(\d{1,2})(?![\d.S])'
main_refs = first_occurrences(ms_body, pat_main)
nums = [int(n) for _, n in main_refs]
# 首次出现顺序
seen = []
for _, n in main_refs:
    v = int(n)
    if v not in seen:
        seen.append(v)
print('主图首次引用顺序:', seen)
if seen != sorted(seen):
    issues.append('主图首次引用顺序非递增: %s' % seen)
if sorted(set(nums)) != list(range(1, 7)):
    issues.append('主图编号集合异常: %s (期望 1-6)' % sorted(set(nums)))

# ---- 2. 补充图 Figure SN ----
pat_supp = r'(?:Figure|Fig\.?)\s+S(\d{1,2})(?![\d])'
supp_refs = first_occurrences(ms_body, pat_supp)
seen_s = []
for _, n in supp_refs:
    v = int(n)
    if v not in seen_s:
        seen_s.append(v)
print('附图首次引用顺序:', seen_s)
if seen_s != sorted(seen_s):
    issues.append('附图首次引用顺序非递增: %s' % seen_s)
if sorted(set(seen_s)) != list(range(1, 14)) or len(seen_s) != 13:
    issues.append('附图编号集合异常: %s (期望 S1-S13)' % seen_s)

# ---- 3. 主表 Table N（正文引用） ----
pat_tbl = r'Table\s+(\d{1,2})(?![\d.S])'
tbl_refs = first_occurrences(ms_body, pat_tbl)
seen_t = []
for _, n in tbl_refs:
    v = int(n)
    if v not in seen_t:
        seen_t.append(v)
print('主表首次引用顺序:', seen_t)

# ---- 4. 补充表 Table SN ----
pat_stbl = r'Table\s+S(\d{1,2})(?![\d])'
stbl_refs = first_occurrences(ms_body + '\n' + sn, pat_stbl)
seen_st = []
for _, n in stbl_refs:
    v = int(n)
    if v not in seen_st:
        seen_st.append(v)
print('附表首次引用顺序(MS+SN合并):', seen_st)

# ---- 5. Additional file N ----
pat_af = r'Additional\s+file\s+(\d{1,2})(?![\d])'
af_refs = first_occurrences(ms_body, pat_af)
seen_af = []
for _, n in af_refs:
    v = int(n)
    if v not in seen_af:
        seen_af.append(v)
print('Additional file 首次引用顺序(MS):', seen_af)
if seen_af != sorted(seen_af):
    issues.append('Additional file 首次引用顺序非递增: %s' % seen_af)

# ---- 6. SN 文档内部图注编号完整性 ----
sn_figs = sorted(set(int(n) for _, n in first_occurrences(sn, r'(?:Figure|Fig\.?)\s+S(\d{1,2})(?![\d])')))
print('SN 内出现的附图编号:', sn_figs)
sn_tbls = sorted(set(int(n) for _, n in first_occurrences(sn, r'Table\s+S(\d{1,2})(?![\d])')))
print('SN 内出现的附表编号:', sn_tbls)

# ---- 7. Table1-2 文件内编号 ----
tb_nums = sorted(set(int(n) for _, n in first_occurrences(tb, r'Table\s+(\d{1,2})(?![\d.S])')))
print('Table1-2 文件内编号:', tb_nums)

# ---- 8. 主图图例存在性 ----
for i in range(1, 7):
    if not re.search(r'Figure %d[.:]' % i, ms_legends + ms_body):
        issues.append('主图 %d 图例缺失' % i)

# ---- 9. 附图引用与 SN 图注一一对应 ----
for v in range(1, 14):
    if v not in seen_s:
        issues.append('附图 S%d 未在 MS 正文引用' % v)
    if v not in sn_figs:
        issues.append('附图 S%d 在 SN 中无图注' % v)

print()
print('=' * 50)
if issues:
    print('ISSUES (%d):' % len(issues))
    for x in issues:
        print(' -', x)
else:
    print('NO ISSUES — 图表编号顺序全部符合 GB 惯例')

# 附：附图首次引用位置上下文（前 3 个供抽查）
print()
print('=== 附图首引上下文抽查 ===')
shown = set()
for pos, n in supp_refs:
    v = int(n)
    if v in shown: continue
    shown.add(v)
    if v <= 3 or v >= 12:
        print('S%d: ...%s...' % (v, ms_body[max(0,pos-100):pos+30].replace(chr(10),' ')[-130:]))
