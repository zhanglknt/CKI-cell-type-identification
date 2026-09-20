# -*- coding: utf-8 -*-
"""v47.1 附图按首引顺序重编号。
映射 old->new: S12->S3, S3->S4, S4->S5, S5->S6, S6->S7, S7->S8, S8->S9,
              S13->S10, S9->S11, S10->S12, S11->S13 (S1/S2 不变)
依据 MS 正文首引序列: S1(8279) S2(15093) S12(24273) S3(28161) S4(32942)
S5(35464) S6(40357) S7(45283) S8(45535) S13(47315) S9(63856) S10(73440) S11(92872)"""
import io, re, shutil, py_compile

ROOT = r'C:\Users\KnightZ\Desktop\细胞受选择'
MAP = {3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 11, 10: 12, 11: 13, 12: 3, 13: 10}

def renumber_refs(text):
    """置换 (Fig|Figure) SN 引用，占位符防循环。"""
    def sub(m):
        n = int(m.group(2))
        return m.group(1) + 'S\u00a7%d\u00a7' % MAP.get(n, n)
    t = re.sub(r'(Fig\.?\s+|Figure\s+)S(\d{1,2})', sub, text)
    return re.sub(r'S\u00a7(\d+)\u00a7', lambda m: 'S' + m.group(1), t)

# ============ 1. generate_manuscript_gb.py ============
P = ROOT + r'\generate_manuscript_gb.py'
t = io.open(P, encoding='utf-8').read()
assert t.count('S\u00a7') == 0
t = renumber_refs(t)
# 图例段重排：按新编号排序 p('Additional file 1: Figure SN. ...') 行
i = t.find("ry figure legends', level=1)")
j = t.find('# == Save ==', i)
seg = t[i:j]
lines = seg.split('\n')
head = []
legs = []
for l in lines:
    if l.startswith("p('Additional file 1: Figure S"):
        m = re.match(r"p\('Additional file 1: Figure S(\d+)\.", l)
        legs.append((int(m.group(1)), l))
    else:
        head.append(l)
assert len(legs) == 13, len(legs)
nums = [n for n, _ in legs]
assert sorted(nums) == list(range(1, 14)), 'legend nums after renumber: %s' % nums
legs_sorted = sorted(legs, key=lambda x: x[0])
# 重组：head 前缀（含 heading 行），图例间空行保持单空行
prefix_lines = head[:]
# 去掉 head 尾部多余空行
while prefix_lines and prefix_lines[-1].strip() == '':
    prefix_lines.pop()
new_seg = '\n'.join(prefix_lines) + '\n\n' + '\n\n'.join(l for _, l in legs_sorted) + '\n\n'
t = t[:i] + new_seg + t[j:]
io.open(P, 'w', encoding='utf-8', newline='').write(t)
py_compile.compile(P, doraise=True)
print('MS generator: refs renumbered + legends reordered')
shutil.copyfile(P, ROOT + r'\CKI_Reproducibility_Package\generate_manuscript_gb.py')

# ============ 2. 68_gen_supplementary_en.py ============
P2 = ROOT + r'\notebooks\68_gen_supplementary_en.py'
t2 = io.open(P2, encoding='utf-8').read()
before = re.findall(r'(?:Fig\.?|Figure)\s+S\d{1,2}', t2)
t2 = renumber_refs(t2)
after = re.findall(r'(?:Fig\.?|Figure)\s+S\d{1,2}', t2)
print('68 script:', before, '->', after)
assert 'Figure S12' in t2 and '(Fig. S3)' in t2 and 'Fig. S10.' in t2
io.open(P2, 'w', encoding='utf-8', newline='').write(t2)
py_compile.compile(P2, doraise=True)
shutil.copyfile(P2, ROOT + r'\CKI_Reproducibility_Package\notebooks\68_gen_supplementary_en.py')

# ============ 3. Guide.js ============
P3 = ROOT + r'\notebooks\100_gen_reproducibility_docx.js'
t3 = io.open(P3, encoding='utf-8').read()
b3 = re.findall(r'Fig\.?\s+S\d{1,2}', t3)
t3 = renumber_refs(t3)
a3 = re.findall(r'Fig\.?\s+S\d{1,2}', t3)
print('Guide.js:', b3, '->', a3)
io.open(P3, 'w', encoding='utf-8', newline='').write(t3)
shutil.copyfile(P3, ROOT + r'\CKI_Reproducibility_Package\notebooks\100_gen_reproducibility_docx.js')

# ============ 4. 99_build_gb_v47.py（断言/映射/注释） ============
P4 = ROOT + r'\99_build_gb_v47.py'
t4 = io.open(P4, encoding='utf-8').read()
orig = t4

def rep(old, new, cnt=1):
    global t4
    n = t4.count(old)
    assert n == cnt, 'anchor %r count %d (expect %d)' % (old[:70], n, cnt)
    t4 = t4.replace(old, new)

# 4a. FIGURE_MAP：目标键按新编号（源文件名不变）
rep('"Supplementary_Figure_S3": "figure_S3",', '"Supplementary_Figure_S4": "figure_S3",')
rep('"Supplementary_Figure_S4": "figure_S4",', '"Supplementary_Figure_S5": "figure_S4",')
rep('"Supplementary_Figure_S5": "figure_S5",', '"Supplementary_Figure_S6": "figure_S5",')
rep('"Supplementary_Figure_S6": "figure_S6",', '"Supplementary_Figure_S7": "figure_S6",')
rep('"Supplementary_Figure_S7": "figure_S7",', '"Supplementary_Figure_S8": "figure_S7",')
rep('"Supplementary_Figure_S8": "figure_S8",', '"Supplementary_Figure_S9": "figure_S8",')
rep('"Supplementary_Figure_S9": "figure_S9",', '"Supplementary_Figure_S11": "figure_S9",')
rep('"Supplementary_Figure_S10": "figure_S10",', '"Supplementary_Figure_S12": "figure_S10",')
rep('"Supplementary_Figure_S11": "figure_S11",', '"Supplementary_Figure_S13": "figure_S11",')
rep('"Supplementary_Figure_S12": "figure_S12",', '"Supplementary_Figure_S3": "figure_S12",')
rep('"Supplementary_Figure_S13": "figure_S13",', '"Supplementary_Figure_S10": "figure_S13",')

# 4b. MAP 上方注释更新
rep('''# Supplementary figures S1-S13 (v47 renumbered, staged in''',
    '''# Supplementary figures S1-S13 (v47.1 renumbered BY FIRST-CITATION
# ORDER; source PDF names unchanged, staged in''')

# 4c. E4-M1 断言 S9->S11
rep('''    v.check(bool(re.search(r'(Additional file 1: )?(Supplementary )?Fig(ure)?\\.? S9', t)),
            "Fig S9 cited in text")''',
    '''    v.check(bool(re.search(r'(Additional file 1: )?(Supplementary )?Fig(ure)?\\.? S11', t)),
            "Fig S11 cited in text (v47.1 renumber)")''')

# 4d. V41-21/22/25 Kang S12->S3
rep("v.check(bool(re.search(r'Additional file 1: Fig\\. S12', t)),\n"
    '            "V41-21 MS cites Additional file 1 Fig. S12 (v47: Kang)")',
    "v.check(bool(re.search(r'Additional file 1: Fig\\. S3', t)),\n"
    '            "V41-21 MS cites Additional file 1 Fig. S3 (v47.1: Kang)")')
rep("v.check(bool(re.search(r'Figure S12\\. Real perturbation demonstration', t)),\n"
    '            "V41-22 S12 caption in MS (v47: Kang renumbered)")',
    "v.check(bool(re.search(r'Figure S3\\. Real perturbation demonstration', t)),\n"
    '            "V41-22 S3 caption in MS (v47.1: Kang renumbered)")')
rep("v.check(bool(re.search(r'\\(Fig\\. S12\\)', s)), \"V41-25 SN 3.15 references Fig. S12 (v47)\")",
    "v.check(bool(re.search(r'\\(Fig\\. S3\\)', s)), \"V41-25 SN 3.15 references Fig. S3 (v47.1)\")")

# 4e. V41-29/30 QQ S13->S10
rep("v.check(bool(re.search(r'Additional file 1: Fig\\. S13', t)),\n"
    '            "V41-29 MS cites Additional file 1 Fig. S13 (v47: QQ)")',
    "v.check(bool(re.search(r'Additional file 1: Fig\\. S10', t)),\n"
    '            "V41-29 MS cites Additional file 1 Fig. S10 (v47.1: QQ)")')
rep("v.check(bool(re.search(r'Figure S13\\. Pseudo-region negative control', t)),\n"
    '            "V41-30 S13 caption in MS (v47: QQ renumbered)")',
    "v.check(bool(re.search(r'Figure S10\\. Pseudo-region negative control', t)),\n"
    '            "V41-30 S10 caption in MS (v47.1: QQ renumbered)")')

# 4f. R2-4 消息
rep('"R2-4 Fig S12 (Kang) caption uses \'consistent with\' (v47)")',
    '"R2-4 Fig S3 (Kang) caption uses \'consistent with\' (v47.1)")')

# 4g. V47-3d/e/f caption 断言
rep('v.check("Figure S3. TCGA per-cancer matrices" in ms,',
    'v.check("Figure S4. TCGA per-cancer matrices" in ms,')
rep('v.check("Figure S12. Real perturbation demonstration" in ms,\n'
    '            "V47-3e Kang caption = Figure S12")',
    'v.check("Figure S3. Real perturbation demonstration" in ms,\n'
    '            "V47-3e Kang caption = Figure S3 (v47.1)")')
rep('v.check("Figure S13. Pseudo-region negative control" in ms,\n'
    '            "V47-3f QQ caption = Figure S13")',
    'v.check("Figure S10. Pseudo-region negative control" in ms,\n'
    '            "V47-3f QQ caption = Figure S10 (v47.1)")')

# 4h. E4-6 / E4-9 / M3 消息文字
rep('"E4-6 Supplementary figures S1-S12 complete")',
    '"E4-6 Supplementary figures S1-S13 complete (v47.1)")')
rep('f"{sn_words} words, figures S8-S12 cited in notes")',
    'f"{sn_words} words, figures S2, S3, S7, S9, S10, S12, S13 cited in notes (v47.1)")')
rep('f"M3 S1-S12 cited in body ({total_supp} supp fig refs)")',
    'f"M3 S1-S13 cited in body ({total_supp} supp fig refs)")')

# 4i. 尾部 docstring 描述行
rep('table headings (Table S1-S4) present; notes cite Figures S8-S12;',
    'table headings (Table S1-S4) present; notes cite Figures S2, S3, S7,\nS9, S10, S12, S13 (v47.1 renumber);')
rep('Table S4 (candidate tiers), and Supplementary Fig. S9',
    'Table S4 (candidate tiers), and Supplementary Fig. S11')

# 4j. 头部 docstring 追加 v47.1 说明（在 v47 描述段后）
rep("Kang IFN-beta S13->S12; QQ S14->S13); Figure S1 regenerated",
    "Kang IFN-beta S13->S12; QQ S14->S13); Figure S1 regenerated\n"
    "v47.1 (2026-09-14): supplementary figures renumbered BY\n"
    "FIRST-CITATION ORDER per GB convention (Kang S12->S3, QQ\n"
    "S13->S10, S3-S8->S4-S9, S9-S11->S11-S13); source PDF names\n"
    "unchanged, FIGURE_MAP target keys remapped")

assert t4 != orig
io.open(P4, 'w', encoding='utf-8', newline='').write(t4)
py_compile.compile(P4, doraise=True)
shutil.copyfile(P4, ROOT + r'\CKI_Reproducibility_Package\99_build_gb_v47.py')
print('build script: MAP + assertions + docstrings updated')
print('ALL RENUMBER EDITS DONE')
