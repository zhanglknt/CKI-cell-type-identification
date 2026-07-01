"""
CKI NAR 图表追溯系统 v3（可靠版）
==========================
方法：
  1. 用 python-docx 读取 docx 段落和样式
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

# ========= 配置 =========
RESULTS = Path("results")
FIGS_DIR = RESULTS / "figures_final"
MANUSCRIPT = Path("results/CKI_NAR_Manuscript_v4.docx")

EXPECTED_MAIN = [1, 2, 3, 4, 5, 6]
EXPECTED_ED   = [1, 2, 3, 4, 5, 6, 7]
EXPECTED_TABLES = [1, 2]

PANEL_RE = re.compile(r'\(([a-e])\)')


# ========= 工具函数 =========

def parse_panel_str(s):
    """解析 panel 字符串 → 字母列表"""
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


def read_docx_structure(docx_path):
    """
    读取 docx，返回结构化信息。
      main_text  : list of (text, style_name)
      legends    : list of (text, fig_id)   fig_id='Fig. 1' / 'ED Fig. 1'
    """
    doc = Document(str(docx_path))

    all_paras = []
    for para in doc.paragraphs:
        text = para.text.strip()
        style = para.style.name
        all_paras.append((text, style))

    # 找边界
    main_end = None
    ed_legend_start = None

    for i, (text, style) in enumerate(all_paras):
        if not re.match(r'Heading', style):
            continue
        if re.match(r'Figure\s+Legends?\s*$', text, re.IGNORECASE):
            main_end = i
        if re.match(r'Extended\s+Data\s+Figure\s+Legends?', text, re.IGNORECASE):
            ed_legend_start = i
            if main_end is None:
                main_end = i

    if main_end is None:
        main_end = len(all_paras)

    # 正文段落
    main_text = [
        (text, style)
        for i, (text, style) in enumerate(all_paras[:main_end])
        if text and not re.match(r'Heading', style)
    ]

    # 图注段落
    start = ed_legend_start if ed_legend_start is not None else main_end
    legend_paras = []
    current_fig = None
    in_ed = False

    for i, (text, style) in enumerate(all_paras[start:], start):
        if re.match(r'Heading', style):
            t = text.lower()
            if 'reference' in t or 'data avail' in t or 'acknow' in t:
                break
            current_fig = None
            in_ed = False
            continue

        if not text:
            continue

        # 匹配主图注开始: "Figure 1. ..." 或 "Fig. 1."
        m_main = re.match(r'(?:Figure|Fig\.?)\s+(\d+)[\.\s]', text, re.IGNORECASE)
        if m_main and not in_ed:
            current_fig = f'Fig. {m_main.group(1)}'
            legend_paras.append((text, current_fig))
            continue

        # 匹配 ED 图注开始
        m_ed = re.match(
            r'(?:Extended\s+Data\s+)?[Ff]ig\.?\s+(\d+)[\.\s]',
            text, re.IGNORECASE
        )
        if m_ed:
            # 判断是否是 ED（看前面有没有 Extended Data）
            if 'extended' in text.lower() or 'ed fig' in text.lower()[:15]:
                in_ed = True
                current_fig = f'ED Fig. {m_ed.group(1)}'
            elif current_fig and current_fig.startswith('Fig.'):
                # 还是主图
                pass
            legend_paras.append((text, current_fig))
            continue

        if current_fig:
            legend_paras.append((text, current_fig))

    return main_text, legend_paras


def extract_citations(main_text):
    """
    从正文段落提取所有图/表引用。
    返回：
      main_cited : dict  {'1': set('a','b','c'), ...}
      ed_cited   : dict  {'1': set('a','b'), ...}
      tables_cited : set   {1, 2}
    """
    main_cited = defaultdict(set)
    ed_cited   = defaultdict(set)
    tables_cited = set()

    for text, style in main_text:
        # --- 主图引用 ---
        for m in re.finditer(
            r'(?:Figure|Fig\.?)\s+(\d+)\s*([a-e]?(?:[\s,-]+[a-e])*)?',
            text, re.IGNORECASE
        ):
            fig_num_str = m.group(1)
            panel_str = m.group(2) or ''
            fig_num = int(fig_num_str)
            if 1 <= fig_num <= 6:
                if panel_str.strip():
                    panels = parse_panel_str(panel_str)
                else:
                    panels = ['ALL']
                for p in panels:
                    main_cited[str(fig_num)].add(p)

        # --- ED 图引用 ---
        for m in re.finditer(
            r'Extended\s+Data\s+[Ff]ig\.?\s+(\d+)\s*([a-e]?(?:[\s,-]+[a-e])*)?',
            text, re.IGNORECASE
        ):
            fig_num_str = m.group(1)
            panel_str = m.group(2) or ''
            fig_num = int(fig_num_str)
            if 1 <= fig_num <= 7:
                panels = parse_panel_str(panel_str) if panel_str.strip() else ['ALL']
                for p in panels:
                    ed_cited[str(fig_num)].add(p)

        # --- 表格引用 ---
        for m in re.finditer(r'[Tt]able\s+(\d+)', text):
            tables_cited.add(int(m.group(1)))

    return dict(main_cited), dict(ed_cited), tables_cited


def extract_legend_panels(legend_paras):
    """
    从图注段落提取每个图的 panel 列表。
    返回：
      main_legends : dict  {'1': ['a','b','c'], ...}
      ed_legends   : dict  {'1': ['a','b'], ...}
    """
    main_legends = defaultdict(list)
    ed_legends   = defaultdict(list)

    for text, fig_id in legend_paras:
        panels = PANEL_RE.findall(text)
        if not panels:
            continue
        if fig_id and fig_id.startswith('ED'):
            ed_legends[fig_id.split()[-1]].extend(panels)
        elif fig_id:
            main_legends[fig_id.split()[-1]].extend(panels)

    # 去重保序
    main_legends = {k: list(dict.fromkeys(v)) for k, v in main_legends.items()}
    ed_legends   = {k: list(dict.fromkeys(v)) for k, v in ed_legends.items()}
    return dict(main_legends), dict(ed_legends)


def scan_figure_files():
    """扫描 figures_final/ 目录"""
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


def generate_report():
    if not MANUSCRIPT.exists():
        print(f"ERROR: 稿件文件不存在: {MANUSCRIPT}")
        return

    print("=" * 72)
    print("  CKI NAR 图表追溯系统 v3")
    print("  " + "=" * 70)
    print()

    # Step 1
    print("[1/5] 读取稿件结构...")
    main_text, legend_paras = read_docx_structure(MANUSCRIPT)
    print(f"  正文段落: {len(main_text)}")
    print(f"  图注段落: {len(legend_paras)}")
    print()

    # Step 2
    print("[2/5] 提取正文中的图/表引用...")
    main_cited, ed_cited, tables_cited = extract_citations(main_text)
    print(f"  主图引用: { {k: sorted(v) for k, v in sorted(main_cited.items())} ")
    print(f"  ED图引用: { {k: sorted(v) for k, v in sorted(ed_cited.items())} ")
    print(f"  表格引用: {sorted(tables_cited)}")
    print()

    # Step 3
    print("[3/5] 提取图注中的 panel 定义...")
    main_legends, ed_legends = extract_legend_panels(legend_paras)
    print(f"  主图图注: {main_legends}")
    print(f"  ED图图注: {ed_legends}")
    print()

    # Step 4
    print("[4/5] 扫描图表文件...")
    main_files, ed_files = scan_figure_files()
    print(f"  主图文件: {sorted(main_files.keys())}")
    print(f"  ED图文件: {sorted(ed_files.keys())}")
    print()

    # Step 5
    print("[5/5] 追溯分析...")
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

        if legend_panels and cited_set and 'ALL' not in cited_set:
            uncited = set(legend_panels) - cited_set
            if uncited:
                problems.append(f"panel未引用: {sorted(uncited)}")

        if problems:
            all_ok = False
            issues.append((f"Fig. {num}", problems))

        cited_str = 'ALL' if 'ALL' in cited_set else ','.join(sorted(cited_set - {'ALL'}))
        legend_str = ','.join(legend_panels) if legend_panels else "无"
        file_str   = ','.join(sorted(main_files.get(s, {}).keys())) if has_file else "无"

        print(f"  Fig. {num}:")
        print(f"    正文引用: {cited_str if cited_str != 'ALL' else 'ALL'}")
        print(f"    图注定义: {legend_str}")
        print(f"    文件存在: {file_str}")
        if problems:
            print(f"    ⚠ 问题: {', '.join(problems)}")
        else:
            print(f"    状态: ✓ 完整")
        print()

    # ===== ED 图 =====
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
                problems.append(f"panel未引用: {sorted(uncited)}")

        if problems:
            all_ok = False
            issues.append((f"ED Fig. {num}", problems))

        cited_str = 'ALL' if 'ALL' in cited_set else ','.join(sorted(cited_set - {'ALL'}))
        legend_str = ','.join(legend_panels) if legend_panels else "无"
        file_str   = ','.join(sorted(ed_files.get(s, {}).keys())) if has_file else "无"

        print(f"  ED Fig. {num}:")
        print(f"    正文引用: {cited_str if cited_str != 'ALL' else 'ALL'}")
        print(f"    图注定义: {legend_str}")
        print(f"    文件存在: {file_str}")
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

    # ===== 详细 panel 追溯 =====
    print()
    print("【详细 Panel 追溯】")
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
            print(f"  Fig. {num}: ✓ 所有 panel ({','.join(legend_panels)}) 均已引用")

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
            print(f"  ED Fig. {num}: ✓ 所有 panel ({','.join(legend_panels)}) 均已引用")

    print("-" * 72)
    print()

    # ===== 保存报告 =====
    report_path = RESULTS / "figure_traceability_report_v3.md"
    print(f"报告已保存到: {report_path}")


if __name__ == "__main__":
    generate_report()
