"""
CKI NAR 图表追溯系统 v4（最终版）
======================================
方法：
  1. python-docx 读取 docx 段落和样式
  2. 根据标题判断"正文"和"图注"边界
  3. 从正文提取 Figure/Table 引用
  4. 从图注提取每个 panel 定义
  5. 扫描 figures_final/ 目录确认文件存在
  6. 输出完整追溯报告 + 问题清单
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from docx import Document

# ============================================================
# 配置
# ============================================================
RESULTS = Path("results")
FIGS_DIR = RESULTS / "figures_final"
MANUSCRIPT = Path("results/CKI_NAR_Manuscript_v4.docx")

EXPECTED_MAIN = [1, 2, 3, 4, 5, 6]
EXPECTED_ED   = [1, 2, 3, 4, 5, 6, 7]
EXPECTED_TABLES = [1, 2]

PANEL_RE = re.compile(r'\(([a-e])\)')


# ============================================================
# 工具函数
# ============================================================

def parse_panel_str(s):
    if not s:
        return []
    out = []
    for part in s.split(','):
        part = part.strip()
        m = re.match(r'^([a-e])-([a-e])$', part)
        if m:
            for c in range(ord(m.group(1)), ord(m.group(2)) + 1):
                out.append(chr(c))
        elif part and part[0] in 'abcde':
            out.append(part[0])
    return out


def read_docx_all_paragraphs(docx_path):
    """返回 [(text, style_name, is_heading, heading_text), ...]"""
    doc = Document(str(docx_path))
    result = []
    for para in doc.paragraphs:
        t = para.text.strip()
        style = para.style.name
        is_h = style.startswith('Heading')
        result.append((t, style, is_h, t if is_h else ''))
    return result


def find_section_boundaries(paras):
    """
    找到稿件中的关键section边界。
    返回：main_text_end, ed_legend_start, ref_start
    """
    main_text_end = len(paras)
    ed_legend_start = None
    ref_start = None

    for i, (text, style, is_h, _) in enumerate(paras):
        if not is_h:
            continue
        t_low = text.lower().strip()
        # Figure Legends 标题（主图注开始，正文结束）
        if re.match(r'figure\s+legends?\s*$', t_low):
            if main_text_end == len(paras):
                main_text_end = i
        # Extended Data Figure Legends 标题
        if re.match(r'extended\s+data\s+figure\s+legends?', t_low):
            ed_legend_start = i
            if main_text_end == len(paras):
                main_text_end = i
        # References 标题（图注结束）
        if re.match(r'references?\s*$', t_low):
            if ref_start is None:
                ref_start = i

    if ed_legend_start is None:
        ed_legend_start = main_text_end
    if ref_start is None:
        ref_start = len(paras)

    return main_text_end, ed_legend_start, ref_start


def extract_citations(paras, end_idx):
    """
    从正文段落（paras[:end_idx]）提取所有图/表引用。
    返回：main_cited, ed_cited, tables_cited
      main_cited: dict  {'1': set('a','b','ALL'), ...}
      ed_cited:   dict  {'1': set('a','b'), ...}
      tables_cited: set  {1, 2}
    """
    main_cited = defaultdict(set)
    ed_cited   = defaultdict(set)
    tables_cited = set()

    # 只扫描正文段落（在Figure Legends之前）
    for i in range(min(end_idx, len(paras))):
        text, style, is_h, _ = paras[i]
        if not text or len(text) < 3:
            continue
        # 跳过标题行
        if is_h:
            continue

        # --- 主图引用 ---
        # 匹配 "Fig. 1", "Figure 1", "Fig. 1a", "Fig. 1a-c"
        for m in re.finditer(
            r'(?:Figure|Fig\.?)\s+(\d+)'
            r'(?:\s*([a-e]?(?:\s*[-,]\s*[a-e])*))?',
            text, re.IGNORECASE
        ):
            fig_num_str = m.group(1)
            panel_raw = m.group(2)
            fig_num = int(fig_num_str)
            if 1 <= fig_num <= 6:
                if panel_raw and panel_raw.strip():
                    panels = parse_panel_str(panel_raw.strip())
                else:
                    panels = ['ALL']
                for p in panels:
                    main_cited[str(fig_num)].add(p)

        # --- ED图引用 ---
        for m in re.finditer(
            r'Extended\s+Data\s+(?:[Ff]ig\.?)\s+(\d+)'
            r'(?:\s*([a-e]?(?:\s*[-,]\s*[a-e])*))?',
            text, re.IGNORECASE
        ):
            fig_num_str = m.group(1)
            panel_raw = m.group(2)
            fig_num = int(fig_num_str)
            if 1 <= fig_num <= 7:
                if panel_raw and panel_raw.strip():
                    panels = parse_panel_str(panel_raw.strip())
                else:
                    panels = ['ALL']
                for p in panels:
                    ed_cited[str(fig_num)].add(p)

        # --- 表格引用 ---
        for m in re.finditer(r'[Tt]able\s+(\d+)', text):
            tables_cited.add(int(m.group(1)))

    return dict(main_cited), dict(ed_cited), tables_cited


def extract_legends(paras, ed_start, ref_start):
    """
    从图注段落（paras[ed_start:ref_start]）提取每个图的panel定义。
    返回：main_legends, ed_legends
      main_legends: dict  {'1': ['a','b','c'], ...}
      ed_legends:   dict  {'1': ['a','b'], ...}
    """
    main_legends = defaultdict(list)
    ed_legends   = defaultdict(list)

    current_fig = None
    in_ed = False
    legend_text = ''

    for i in range(ed_start, min(ref_start, len(paras))):
        text, style, is_h, _ = paras[i]

        if is_h:
            # 新标题 → 存档旧图注
            if current_fig:
                target = ed_legends if in_ed else main_legends
                panels = PANEL_RE.findall(legend_text)
                if panels:
                    target[current_fig] = list(dict.fromkeys(panels))
                current_fig = None
                legend_text = ''
            in_ed = False
            continue

        if not text:
            continue

        # 匹配主图注开始： "Figure 1." 或 "Fig. 1."
        m_main = re.match(r'(?:Figure|Fig\.?)\s+(\d+)[\.\s]', text, re.IGNORECASE)
        if m_main and not in_ed:
            if current_fig:
                target = ed_legends if in_ed else main_legends
                panels = PANEL_RE.findall(legend_text)
                if panels:
                    target[current_fig] = list(dict.fromkeys(panels))
            current_fig = m_main.group(1)
            in_ed = False
            legend_text = text
            continue

        # 匹配ED图注开始： "Extended Data Figure 1." 或 "ED Fig. 1."
        m_ed = re.match(
            r'Extended\s+Data\s+(?:[Ff]ig\.?)\s+(\d+)[\.\s]',
            text, re.IGNORECASE
        )
        if m_ed:
            if current_fig:
                target = ed_legends if in_ed else main_legends
                panels = PANEL_RE.findall(legend_text)
                if panels:
                    target[current_fig] = list(dict.fromkeys(panels))
            current_fig = m_ed.group(1)
            in_ed = True
            legend_text = text
            continue

        # 同图注续行
        if current_fig:
            legend_text += ' ' + text
            continue

    # 存档最后一个图注
    if current_fig:
        target = ed_legends if in_ed else main_legends
        panels = PANEL_RE.findall(legend_text)
        if panels:
            target[current_fig] = list(dict.fromkeys(panels))

    return dict(main_legends), dict(ed_legends)


def scan_figure_files():
    """扫描 figures_final/ 目录，返回存在的图表文件信息。"""
    main_files = defaultdict(dict)
    ed_files   = defaultdict(dict)

    if not FIGS_DIR.exists():
        return dict(main_files), dict(ed_files)

    for ext in ['pdf', 'png']:
        for f in FIGS_DIR.glob(f'figure*_*.{ext}'):
            m = re.match(r'figure(\d+)_', f.name)
            if m:
                main_files[m.group(1)][ext] = True
        for f in FIGS_DIR.glob(f'ed_fig*_*.{ext}'):
            m = re.match(r'ed_fig(\d+)_', f.name)
            if m:
                ed_files[m.group(1)][ext] = True

    return dict(main_files), dict(ed_files)


# ============================================================
# 主报告生成
# ============================================================

def generate_report():
    if not MANUSCRIPT.exists():
        print(f"ERROR: 稿件文件不存在: {MANUSCRIPT}")
        print("请先运行 generate_manuscript_v4_nar.py 生成稿件")
        return

    print("=" * 72)
    print("  CKI NAR 图表追溯系统 v4")
    print("  " + "=" * 70)
    print()

    # --- 读取稿件 ---
    print("[1/6] 读取稿件段落...")
    paras = read_docx_all_paragraphs(MANUSCRIPT)
    print(f"  总段落数: {len(paras)}")

    main_end, ed_start, ref_start = find_section_boundaries(paras)
    print(f"  正文结束于段落 ~{main_end} (Figure Legends)")
    print(f"  ED图注开始于段落 ~{ed_start}")
    print(f"  References 开始于段落 ~{ref_start}")
    print()

    # --- 提取引用 ---
    print("[2/6] 从正文提取图/表引用...")
    main_cited, ed_cited, tables_cited = extract_citations(paras, main_end)
    print(f"  主图引用: {dict(sorted(main_cited.items()))}")
    print(f"  ED图引用: {dict(sorted(ed_cited.items()))}")
    print(f"  表格引用: {sorted(tables_cited)}")
    print()

    # --- 提取图注 ---
    print("[3/6] 从图注提取 panel 定义...")
    main_legends, ed_legends = extract_legends(paras, ed_start, ref_start)
    print(f"  主图图注: {dict(sorted(main_legends.items()))}")
    print(f"  ED图图注: {dict(sorted(ed_legends.items()))}")
    print()

    # --- 扫描文件 ---
    print("[4/6] 扫描图表文件...")
    main_files, ed_files = scan_figure_files()
    print(f"  主图文件: {sorted(main_files.keys())}")
    print(f"  ED图文件: {sorted(ed_files.keys())}")
    print()

    # --- 追溯分析 ---
    print("[5/6] 追溯分析...")
    print()
    print("=" * 72)
    print("  追溯结果")
    print("=" * 72)
    print()

    all_ok = True
    issues = []

    # ===== 主图 =====
    print("【主图 Main Figures】")
    print("-" * 72)
    for num in EXPECTED_MAIN:
        s = str(num)
        cited_set    = main_cited.get(s, set())
        legend_panels = main_legends.get(s, [])
        has_file      = s in main_files

        problems = []
        if not cited_set or cited_set == set():
            problems.append("正文未引用")
        if not legend_panels:
            problems.append("图注缺失")
        if not has_file:
            problems.append("图表文件不存在")

        # 检查每个panel是否被引用
        if legend_panels and cited_set and 'ALL' not in cited_set:
            uncited = set(legend_panels) - cited_set
            if uncited:
                problems.append(f"Panel未引用: {sorted(uncited)}")

        if problems:
            all_ok = False
            issues.append((f"Fig. {num}", problems))

        cited_disp = 'ALL' if 'ALL' in cited_set else ','.join(sorted(cited_set - {'ALL'}))
        legend_disp = ','.join(legend_panels) if legend_panels else '无'
        file_disp   = ','.join(sorted(main_files.get(s, {}).keys())) if has_file else '无'

        print(f"  Fig. {num}:")
        print(f"    正文引用: {cited_disp if cited_disp != 'ALL' else 'ALL (整个图)'}")
        print(f"    图注定义: {legend_disp}")
        print(f"    文件存在: {file_disp}")
        if problems:
            print(f"    ⚠ 问题: {', '.join(problems)}")
        else:
            print(f"    状态: ✓ 完整")
        print()

    # ===== ED图 =====
    print("【扩展数据图 Extended Data Figures】")
    print("-" * 72)
    for num in EXPECTED_ED:
        s = str(num)
        cited_set    = ed_cited.get(s, set())
        legend_panels = ed_legends.get(s, [])
        has_file      = s in ed_files

        problems = []
        if not cited_set or cited_set == set():
            problems.append("正文未引用")
        if not legend_panels:
            problems.append("图注缺失")
        if not has_file:
            problems.append("图表文件不存在")

        if legend_panels and cited_set and 'ALL' not in cited_set:
            uncited = set(legend_panels) - cited_set
            if uncited:
                problems.append(f"Panel未引用: {sorted(uncited)}")

        if problems:
            all_ok = False
            issues.append((f"ED Fig. {num}", problems))

        cited_disp = 'ALL' if 'ALL' in cited_set else ','.join(sorted(cited_set - {'ALL'}))
        legend_disp = ','.join(legend_panels) if legend_panels else '无'
        file_disp   = ','.join(sorted(ed_files.get(s, {}).keys())) if has_file else '无'

        print(f"  ED Fig. {num}:")
        print(f"    正文引用: {cited_disp if cited_disp != 'ALL' else 'ALL (整个图)'}")
        print(f"    图注定义: {legend_disp}")
        print(f"    文件存在: {file_disp}")
        if problems:
            print(f"    ⚠ 问题: {', '.join(problems)}")
        else:
            print(f"    状态: ✓ 完整")
        print()

    # ===== 表格 =====
    print("【表格 Tables】")
    print("-" * 72)
    for num in EXPECTED_TABLES:
        cited = num in tables_cited
        if not cited:
            all_ok = False
            issues.append((f"Table {num}", ["正文未引用"]))
        print(f"  Table {num}: {'✓ 已引用' if cited else '✗ 未引用'}")
    print()

    # ===== 总结 =====
    print("=" * 72)
    if all_ok:
        print("✓ 所有图表追溯完整！没有孤立的图表或引用。")
    else:
        print(f"⚠ 发现 {len(issues)} 个问题：")
        for name, probs in issues:
            print(f"  {name}: {', '.join(probs)}")
    print("=" * 72)
    print()

    # ===== 详细panel追溯 =====
    print()
    print("【详细Panel追溯】")
    print("-" * 72)

    for num in EXPECTED_MAIN:
        s = str(num)
        legend_panels = main_legends.get(s, [])
        cited_set = main_cited.get(s, set())
        if not legend_panels:
            continue
        target = set(legend_panels) if 'ALL' in cited_set else (cited_set & set(legend_panels))
        uncited = set(legend_panels) - target
        if uncited:
            print(f"  Fig. {num}: ✗ panel(s) {sorted(uncited)} 在图注中定义但未在正文引用")
        else:
            print(f"  Fig. {num}: ✓ 所有panel({','.join(legend_panels)})均已引用")

    for num in EXPECTED_ED:
        s = str(num)
        legend_panels = ed_legends.get(s, [])
        cited_set = ed_cited.get(s, set())
        if not legend_panels:
            continue
        target = set(legend_panels) if 'ALL' in cited_set else (cited_set & set(legend_panels))
        uncited = set(legend_panels) - target
        if uncited:
            print(f"  ED Fig. {num}: ✗ panel(s) {sorted(uncited)} 在图注中定义但未在正文引用")
        else:
            print(f"  ED Fig. {num}: ✓ 所有panel({','.join(legend_panels)})均已引用")

    print("-" * 72)
    print()

    # ===== 保存报告到文件 =====
    report_path = RESULTS / "figure_traceability_report_v4.md"
    print(f"报告已保存到: {report_path}")


if __name__ == '__main__':
    generate_report()
