# -*- coding: utf-8 -*-
"""v47 参考文献修复：事实错误（8 条）+ GB/NLM 格式（期刊缩写去内点 + 页码缩写）。
只改 generate_manuscript_gb.py 的 _refs_nar 列表（root + 镜像同步）。"""
import io, re, ast, shutil

P = r'C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_gb.py'
t = io.open(P, encoding='utf-8').read()

# ---- 定位 _refs_nar 列表字面量 ----
i = t.find('_refs_nar = [')
depth = 0; end = None
for k in range(i, len(t)):
    if t[k] == '[': depth += 1
    elif t[k] == ']':
        depth -= 1
        if depth == 0:
            end = k + 1; break
seg = t[i:end]
refs = ast.literal_eval(seg.split('=', 1)[1].strip())
assert len(refs) == 56, len(refs)

# ---- A. 事实性修复（精确替换，计数断言） ----
fixes = {
 12: ('Science. 2023;382:eadl7046.', 'Science. 2023;382:eadd7046.'),
 19: ('Schaffenrath J, Huang SF, Wyss T, Delorenzi M, Keller A. Characteristics of blood-brain barrier heterogeneity between brain regions. Nat. Neurosci. 2024;27:1851-1865.',
      'Pfau SJ, Langen UH, Fisher TM, Prakash I, Nagpurwala F, Lozoya RA, et al. Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells. Nat. Neurosci. 2024;27:1892-1903.'),
 20: ('Meningeal origins and dynamics of perivascular fibroblast development. Development. 2023;150:dev201805.',
      'Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature. Development. 2023;150:dev201805.'),
 22: ('Shemer A, Jung S. The molecular determinants of microglial developmental colonization. Nat. Rev. Neurosci. 2024;25:414-427.',
      'Barry-Carroll L, Gomez-Nicola D. The molecular determinants of microglial developmental dynamics. Nat. Rev. Neurosci. 2024;25:414-427.'),
 24: ('Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors. Cell Rep. 2023;42:112425.',
      'Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling. Cell Rep. 2023;42:112425.'),
 26: ('Akay LA, Effenberger AH, Tsai LH. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration. Neuron. 2022;111:190-201.e8.',
      'Su Y, Wang X, Yang Y, Chen L, Xia W, Hoi KK, et al. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development. Neuron. 2023;111:190-201.e8.'),
 27: ('Nat. Neurosci. 2024;27:1155-1165.', 'Nat. Neurosci. 2024;27:1545-1554.'),
 28: ('Reeber SL, Arancillo M, Sillitoe RV. Bergmann glia are patterned into topographic molecular zones in the cerebellum. Cerebellum. 2015;14:392-403.',
      'Reeber SL, Arancillo M, Sillitoe RV. Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum. Cerebellum. 2018;17:392-403.'),
 29: ('Cell Discov. 2024;10:25.', 'Cell Discov. 2024;10:22.'),
 30: ('Endo F, Kasai A, Cui W, Tanaka KF, Hashimoto H. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. EMBO J. 2024;43:4423-4447.',
      'Zhang Y, Li D, Cai Y, Zou R, Zhang Y, Deng X, et al. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. EMBO J. 2024;43:5114-5140.'),
 34: ('Single-cell proteomic and transcriptomic analyses reveal lower intrinsic noise in human cells. Nature. 2006;441:810-816.',
      'Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise. Nature. 2006;441:840-846.'),
}
for n, (old_frag, new_frag) in fixes.items():
    assert old_frag in refs[n-1], 'ref %d anchor missing: %s' % (n, old_frag[:60])
    refs[n-1] = refs[n-1].replace(old_frag, new_frag)
    print('factual fix #%d ok' % n)

# ---- B1. 期刊缩写去内点（NLM） ----
JMAP = {
 'eLife.': 'Elife.',
 'Nat. Methods.': 'Nat Methods.',
 'Mol. Biol. Evol.': 'Mol Biol Evol.',
 'Nat. Biotechnol.': 'Nat Biotechnol.',
 'J. Clin. Oncol.': 'J Clin Oncol.',
 'Nat. Neurosci.': 'Nat Neurosci.',
 'Mol. Psychiatry.': 'Mol Psychiatry.',
 'Nat. Rev. Neurosci.': 'Nat Rev Neurosci.',
 'Dev. Cell.': 'Dev Cell.',
 'Brief. Bioinform.': 'Brief Bioinform.',
 'Mol. Syst. Biol.': 'Mol Syst Biol.',
 'IEEE Trans. Inf. Theory.': 'IEEE Trans Inf Theory.',
 'J. R. Stat. Soc. Series B Stat. Methodol.': 'J R Stat Soc Series B Stat Methodol.',
 'Nat. Genet.': 'Nat Genet.',
 'J. Open Source Softw.': 'J Open Source Softw.',
 'J. Mach. Learn. Res.': 'J Mach Learn Res.',
}
n_j = 0
for k, r in enumerate(refs):
    for old, new in JMAP.items():
        if old in r:
            refs[k] = r.replace(old, new); n_j += 1
            break
print('journal abbrev fixes:', n_j)

# ---- B2. 页码缩写（NLM 规则，保守） ----
def abbrev_pages(m):
    p1, p2 = m.group(1), m.group(2)
    if not p1.isdigit() or not p2.isdigit(): return m.group(0)
    if len(p1) != len(p2): return m.group(0)
    # 共享前导数字
    s = 0
    while s < len(p1) - 1 and p1[s] == p2[s]:
        s += 1
    if s == 0: return m.group(0)
    rest = p2[s:]
    if not rest or rest[0] == '0': return m.group(0)  # 余数以 0 开头 → 保留全写
    return p1 + '-' + rest + m.group(3)

n_p = 0
for k, r in enumerate(refs):
    # 仅匹配 ;VOL:P1-P2<尾巴> 且非 e-locator / D 页 / 文章号
    m = re.search(r'(\d{4};[\w]+:)(\d+)-(\d+)(\.\w+\d*\.?)$', r)
    if m and 'D' not in m.group(1).split(':')[1]:
        new_r = re.sub(r'(\d{4};[\w]+:)(\d+)-(\d+)(\.\w+\d*\.?)$',
                       lambda mm: mm.group(1) + abbrev_pages(mm), r)
        if new_r != r:
            refs[k] = new_r; n_p += 1
print('page abbrev fixes:', n_p)

# ---- 渲染回源码 ----
lines = ['_refs_nar = [']
for r in refs:
    q = "'" + r.replace("'", "\\'") + "'"
    lines.append(q + ',')
lines.append(']')
new_seg = '\n'.join(lines)
t2 = t[:i] + new_seg + t[end:]
io.open(P, 'w', encoding='utf-8', newline='').write(t2)
print('generator written')

# ---- 镜像同步 ----
shutil.copyfile(P, r'C:\Users\KnightZ\Desktop\细胞受选择\CKI_Reproducibility_Package\generate_manuscript_gb.py')
print('mirror synced')

# ---- 自检：语法 + 条数 ----
import py_compile
py_compile.compile(P, doraise=True)
t3 = io.open(P, encoding='utf-8').read()
j = t3.find('_refs_nar = [')
d = 0; e2 = None
for k in range(j, len(t3)):
    if t3[k] == '[': d += 1
    elif t3[k] == ']':
        d -= 1
        if d == 0: e2 = k + 1; break
refs2 = ast.literal_eval(t3[j:e2].split('=', 1)[1].strip())
assert len(refs2) == 56
bad = [r for r in refs2 if re.search(r'[A-Z]\. [A-Z]', r.split('. ')[1] if '. ' in r else '') and 'et al' not in r]
print('final check: 56 refs; remaining dotted journal abbrevs in title field:', len(bad))
for n, r in enumerate(refs2, 1):
    if n in (12, 19, 20, 22, 24, 26, 27, 28, 29, 30, 34):
        print(' ', n, r[:150])
