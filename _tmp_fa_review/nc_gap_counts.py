# -*- coding: utf-8 -*-
"""NC gap audit: counting script (read-only analysis)."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MS = r'C:\Users\KnightZ\Desktop\细胞受选择\version3\CKI_Submission_v47\CKI_Manuscript_fulltext.txt'
text = open(MS, encoding='utf-8').read()
lines = text.splitlines()

# ---- 1. All level-1 (standalone short line) headings with line numbers ----
known = ['Abstract','Background','Results','Discussion','Conclusions','Methods','Declarations',
         'List of abbreviations','Additional files','Figure legends','References','Keywords']
print('== 疑似一级标题（独立短行）==')
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s and len(s) < 60 and not s.startswith('Figure') and not s.startswith('Additional file 1: Figure') \
       and not re.match(r'^\d+\. ', s) and not s.startswith('Table'):
        if s in known or (len(s.split()) <= 8 and not s.endswith('.') and not s[0].islower()
                          and not re.search(r'[\d,;=]', s) and not s.startswith('ORCID')):
            print(f'  L{i}: {s}')

# ---- Results subsection headings (lines inside Results..Discussion) ----
print('\n== Results 小节标题（Results 与 Discussion 之间、独立短行）==')
try:
    ri = next(i for i,l in enumerate(lines) if l.strip()=='Results')
    di = next(i for i,l in enumerate(lines) if l.strip()=='Discussion')
    for i in range(ri+1, di):
        s = lines[i].strip()
        if s and len(s) < 70 and not s[0].islower() and not re.match(r'^(Fig|Table|Step|A |\(|[0-9])', s) and not s.startswith('Note'):
            print(f'  L{i+1}: {s}')
except StopIteration:
    print('  (未找到)')

# ---- 2. Abstract word count ----
ai = next(i for i,l in enumerate(lines) if l.strip()=='Abstract')
kw_i = next(i for i,l in enumerate(lines) if l.strip().startswith('Keywords'))
abstract = ' '.join(lines[ai+1:kw_i]).strip()
print(f'\n== Abstract ==\n词数: {len(abstract.split())}; 段落数: {len([l for l in lines[ai+1:kw_i] if l.strip()])}; 结构化: 否（单段）')

# ---- 3. Citation groups [n] in body (before References) ----
ref_i = next(i for i,l in enumerate(lines) if l.strip()=='References')
body = '\n'.join(lines[:ref_i])
groups = re.findall(r'\[(\d[\d,\s\-–]*(?:,\s*\d+)*)\]', body)
print(f'\n== 正文方括号引用组 ==\n组数: {len(groups)}')
nums = set()
for g in groups:
    for part in re.split(r',', g):
        part = part.strip()
        m = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', part)
        if m: nums.update(range(int(m.group(1)), int(m.group(2))+1))
        elif part.isdigit(): nums.add(int(part))
print(f'被引用的唯一文献号: {len(nums)} -> {sorted(nums)[:10]}...max={max(nums)}')
missing = set(range(1,57)) - nums
print(f'未被引用的编号(1-56): {sorted(missing) if missing else "无"}')

# ---- References list count in txt ----
ref_lines = [l for l in lines[ref_i+1:] if re.match(r'^\d+\. ', l.strip())]
print(f'References 清单条数: {len(ref_lines)} (首条 L{ref_i+2}, 末条编号 {ref_lines[-1].split(".")[0] if ref_lines else "-"})')

# ---- 5. Supplementary naming counts ----
fig_s = re.findall(r'(?:Additional file 1: )?Fig\.? S\d+', body)
tab_s = re.findall(r'(?:Additional file 1: )?Table S\d+', body)
note  = re.findall(r'Note \d+\.\d+', body)
af    = re.findall(r'Additional file \d', body)
print(f'\n== 附属材料引用（正文，References 之前）==')
print(f'Fig. S* 提及: {len(fig_s)}')
print(f'Table S* 提及: {len(tab_s)}')
print(f'Note X.X 提及: {len(note)}')
print(f'Additional file 提及: {len(af)}')
from collections import Counter
print('Note 明细:', dict(Counter(note)))

# full text (incl. legends)
fig_s_all = re.findall(r'Figure S\d+', text)
print(f'全文 "Figure S\\d+" (图例区): {len(fig_s_all)}')

# ---- 6. Panel labels ----
panels = re.findall(r'\(([A-Z])\)', text)
pc = Counter(panels)
print(f'\n== 面板标签 "(X)" 大写字母出现 ==\n总计: {len(panels)}; 分布: {dict(sorted(pc.items()))}')

# ---- 7. Data / Code availability ----
print('\n== Data/Code availability 关键词位置 ==')
for i, ln in enumerate(lines, 1):
    if re.search(r'data avail|code avail|Data avail|Code avail', ln, re.I):
        print(f'  L{i}: {ln[:120]}')
print('（若无输出: 正文中无独立 "Data availability"/"Code availability" 标题，仅有 Declarations > Availability of data and materials）')

# ---- Declarations subsections ----
di2 = next(i for i,l in enumerate(lines) if l.strip()=='Declarations')
afi = next(i for i,l in enumerate(lines) if l.strip()=='Additional files')
print('\n== Declarations 子节（顺序）==')
for i in range(di2+1, afi):
    s = lines[i].strip()
    if s and len(s) < 60 and not s[0].islower():
        print(f'  L{i+1}: {s[:70]}')

# ---- Cover letter mentions ----
CL = open(r'C:\Users\KnightZ\Desktop\细胞受选择\version3\CKI_Submission_v47\CKI_Cover_Letter_fulltext.txt', encoding='utf-8').read()
print('\n== Cover Letter 提及 ==')
for kw in ['Genome Biology', 'Methodology article', 'Nature Communications']:
    c = len(re.findall(kw, CL))
    print(f'  "{kw}": {c} 次')
cl_lines = CL.splitlines()
for i, ln in enumerate(cl_lines, 1):
    if 'Genome Biology' in ln or 'Methodology' in ln:
        print(f'  L{i}: ...{ln[max(0,ln.find("Genome")-60):ln.find("Genome")+80] if "Genome" in ln else ln[:150]}')
        break

# word count of cover letter body
print(f'Cover Letter 正文词数(约): {len(CL.split())}')
