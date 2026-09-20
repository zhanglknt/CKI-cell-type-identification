# gen_response_v47.py — v47 投稿包对一作（吴宪明）问题清单的逐条回复
# 输出：主目录 v47_问题逐条回复.docx（Times New Roman + 宋体，全黑正文）
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from pathlib import Path

BASE = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
OUT = BASE / "v47_问题逐条回复.docx"

doc = Document()
# 页边距
for sec in doc.sections:
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def _fmt(run, size=10.5, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = None  # 黑色
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    return run


def h1(text):
    p = doc.add_paragraph()
    _fmt(p.add_run(text), size=14, bold=True)
    p.space_before = Pt(10)
    return p


def h2(text):
    p = doc.add_paragraph()
    _fmt(p.add_run(text), size=12, bold=True)
    return p


def para(text, bold=False, italic=False, indent=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.left_indent = Cm(0.6)
    _fmt(p.add_run(text), bold=bold, italic=italic)
    return p


def quote(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.8)
    _fmt(p.add_run(text), size=10, italic=True)
    return p


def kv(label, text):
    p = doc.add_paragraph()
    _fmt(p.add_run(label), bold=True)
    _fmt(p.add_run(text))
    return p


# ============ 标题 ============
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
_fmt(t.add_run("v47 投稿包问题逐条回复"), size=16, bold=True)
s = doc.add_paragraph()
s.alignment = WD_ALIGN_PARAGRAPH.CENTER
_fmt(s.add_run("—— 宪明：你回传的 v46 修订与问题清单已全部核查落包，以下逐条回复"), size=11)
doc.add_paragraph()

para("总体情况：你回传的 95 处文字修订与 6 条批注已全部核查并采纳（无暗中改动，句子级 diff 确认全部差异均可归因于修订记录）；主图 figure1–6 全部采用你的重画版。v47 投稿包已构建完成，构建自检 664 项断言全部通过；完整复现包（294 个文件，含本轮新补的结果 CSV 与 ensg2sym.tsv）已一并放入投稿包 zip 内（CKI_Reproducibility_Package.zip）。以下按你问题文档的顺序逐条回复。")

# ============ Q1 ============
h1("问题 1｜Figure S1（A/B/C 三张图数据不对，结果文件中没有对应结果）")
kv("我们的判断：", "部分采纳——曲线方向你是对的，AUC 数值我们保持原值。逐项独立复算的依据如下。")
h2("判断依据")
para("（1）Panel A（k_n 随 HK 基因集大小）：你说得对。我们用复现包 notebooks/01b_hk_stability.py 原脚本独立重跑（Tabula Muris，n_HK = 250/500/750/1000），k_n 单调递减：0.0147 → 0.0101 → 0.0080 → 0.0068，与你的重跑曲线一致。v46 包里旧版 hk_stability_sweep.csv 的递增结果是错的，已作废替换。", indent=True)
para("（2）Panel C（identity-only AUC）：我们用 notebooks/04_phase32_sweep.py 原脚本逐位复现出 AUC = 0.7855（Mann–Whitney u = 2930，P = 6.6e-6），与你 CSV 中的 0.6482（u = 4806，P = 0.0119）不一致。两边 omega_mean 几乎相同（5.71 vs 5.73），说明差异不在 ω 本身，而在 pair 集合/标签构成（由 u 反推，我们版本 same-CT pairs ≈ 5，你的 ≈ 11）。你的 0.648 无法从我们的脚本+数据复现，因此正文与附图保持 0.786。", indent=True)
para("（3）“结果文件中没有对应的结果”——属实，指复现包此前只带了脚本、没带这几个结果 CSV。本轮已补齐（见下）。", indent=True)
h2("v47 修改细节")
para("S1 整图由我们的脚本（_ed_fig1_clean.py）用修正后数据重画：A = 递减曲线（新 CSV），C = AUC 0.786 保持；S1 图例采用你的新文案（k_n 单调递减、baseline rate 依赖基因集大小、ω 值 scheme-specific），你文案里的笔误 \"absolute w values\" 已改为 ω。正文 2 处与 SN 2 处 AUC 均保持 0.786（SN 中另有一处 Spearman ρ = −0.648 为类别大小混杂指标，与本问题无关）。复现包新增 results/hk_stability_sweep.csv、phase32_sweep_results.csv、figure_data_module_variance.csv（panel B 数据）三个文件。", indent=True)

# ============ Q2 ============
h1("问题 2｜Table S1–S4 没有准确对应的表；Table S3 与 S4 指向同一文件？")
kv("我们的判断：", "属实，采纳你提供的 4 CSV 映射。")
h2("判断依据")
para("核对确认：SN 中 Table S3 与 S4 的底层数据文件确实同为 brain_bs_null_observed_pairs.csv——S3 报告全部 31,764 个 pair 的 per-cell-type 汇总统计，S4 是其中 6,591 行通过阈值筛选的子集（带 tier、residual、ω 注释）。二者是同一数据的两个视图，不是错误，但确实需要说清楚。", indent=True)
h2("v47 修改细节")
para("（1）采纳你的映射：S1 = phase32_sweep_results.csv，S2 = phase35_cross_organ_conservation.csv，S3 = brain_bs_null_observed_pairs.csv（含 ct_test 汇总），S4 = 同文件筛选视图。（2）SN 中新增同源澄清句：\"Tables S3 and S4 share the same underlying data file (results/brain_bs_null_observed_pairs.csv): Table S3 reports all 31,764 pairs with per-cell-type summary statistics, whereas Table S4 retains the 6,591 threshold-passing rows with their tier, residual, and ω annotations.\"（3）4 个 CSV 中此前缺的 phase35_cross_organ_conservation.csv、phase32_sweep_results.csv 已补进复现包（brain_bs_null 两个原本就在）。", indent=True)

# ============ Q3 ============
h1("问题 3｜Fig. S13（Kang IFN-β）无法验证——缺 ensg2sym.tsv；建议 Discussion 加句")
kv("我们的判断：", "三个子项全部落实：图保留你的格式版；Discussion 加句（润色后）；缺的文件补进复现包。")
h2("判断依据")
para("（1）图中数字全部属实：CD14+ monocytes ω AUC 0.551、k_f 0.984，perturbation 使 k_n 抬升 1.2–5.7×——与 reference_results/kang_ifnb_demo_summary.json 一一核对无误。（2）GEO 原始数据下载后运行缺 ensg2sym.tsv 属实：该文件在主仓 data/kang_ifnb/（1,050,018 B），此前未随复现包分发。（3）你建议的 Discussion 句子方向正确，与稿件 \"When to use CKI\" 段落的论证结构吻合，润色后采纳。", indent=True)
h2("v47 修改细节")
para("（1）ensg2sym.tsv 已补进复现包 data/kang_ifnb/，你现在可以在本地完整复跑 79_kang_ifnb_demo.py → 80_kang_demo_figure.py。（2）图采用你的格式优化版（panel 标签不再撞标题），按新编号为 Figure S12。（3）Discussion 已加句（润色版）：\"…IFN-β perturbation raises k_n itself 1.2–5.7-fold above the donor-drift level, and where it does so most strongly (CD14+ monocytes) the ω AUC for separating perturbation from donor drift falls to 0.55 while k_f retains 0.98. This makes explicit that the index presupposes anchor stationarity: when the anchor itself moves, cross-metric contrasts—not absolute ω values—are the reliable signal (Additional file 1: Fig. S12).\"", indent=True)

# ============ Q4 ============
h1("问题 4｜Fig. S14（置换检验 QQ 图）重跑结果基本一致，保留原图")
kv("我们的判断：", "确认一致，保留原图。")
h2("判断依据")
para("你重跑的 lower 5.967% / upper 6.842% 与原结果 6.0% / 6.8% 在置换检验的随机波动范围内完全一致（差异 <0.05 个百分点），QQ 图本体无需任何改动。你这份重跑记录本身就是该图的独立验证记录。", indent=True)
h2("v47 修改细节")
para("保留原 QQ 图，按新编号为 Figure S13，无改动。", indent=True)

# ============ Q5 ============
h1("问题 5｜目前没有 Figure S12 编号的图，等 S13 确认后重新排序")
kv("我们的判断：", "不等投稿前——本轮直接完成连续化重排。")
h2("判断依据")
para("S13（Kang）本轮已确认采用，没有理由保留空号到投稿前再改一次；编号与引用的对应关系一次改齐、一次校验，比两次改动更安全。", indent=True)
h2("v47 修改细节")
para("附图全部连续化：删除旧 S3（方法对比 ROC，与 Fig 3 重复，按你的批注 56）；旧 S4→S3、S5→S4、……、S12→S11；Kang（你的 S13）→S12；QQ（你的 S14）→S13，最终 S1–S13 无空号。正文 ~14 处附图引用、图例头、SN 内 7 处交叉引用全部同步改写，并由构建断言逐项校验（S14 引用清零、新 S3 = TCGA、S12 = Kang、S13 = QQ、S1–S13 序列完整）。", indent=True)

# ============ Q6 ============
h1("问题 6｜参考文献最后统一调整")
kv("我们的判断：", "同意，投稿前统一处理。")
h2("v47 修改细节")
para("v47 维持 refs 56 不变；投稿前按 Genome Biology 格式（括号编号、≤20 作者后 et al.）统一终校，不阻塞本轮。", indent=True)

# ============ 附：其他落包说明 ============
h1("附｜其他落包事项（非你问题清单，一并说明）")
para("1. 图形摘要（GA）：采用你的版式，但标题 \"CKI: A Cell-state Kinetic Index\" 与稿件定名不一致，已改回 \"CKI: a Ka/Ks-inspired index\"（与稿件标题前缀一致）。")
para("2. 你的版本遗留小问题已顺手修正：cross-species 图例头仍写 Figure S10→改为 S9；新 S7 图例 B/C 字母与 panel 顺序对调（B = top-10、C = tier 构成）；S4 图例句末双句点；S1 图例 \"absolute w\"→ω。")
para("3. Table1-2.docx 标题 \"Supplementary Tables\"→\"Tables\"（Table 1/2 为主表）。")
para("4. 6 条批注全部处理：批注 56（删旧 S3）、63（表引用移出图例）、69/71（S5 重画 A–C）、99（S9 删 B/C panel 描述）已落包；批注 72 为空批注，忽略。")
para("5. 版本与发布：cki 包升级至 v0.5.0；MS Availability 阶段一沿用 v0.4.9 的 Zenodo 记录 DOI（10.5281/zenodo.22333850），v0.5.0 发布后写入新记录 DOI。")
para("6. 投稿包位置：主目录 CKI_Submission_v47.zip（65,316,691 B，内含完整复现包 CKI_Reproducibility_Package.zip，294 个文件）；变更全记录见包内 MANIFEST_v47.txt。")

doc.save(str(OUT))
print("saved:", OUT, f"({OUT.stat().st_size:,} B)")
