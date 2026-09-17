# v48 Nature Communications 格式改造 — 审计与交叉验证报告

**日期**: 2026-09-17
**范围**: v47.3（Genome Biology）→ v48（Nature Communications）格式转换
**指令**: 召唤专家团，修改格式投稿 Nature Communications
**基线**: v47.3 包（670/670，commit 1adad93）不动，新建 v48 NC 包

---

## 1. 专家团工作流

| 角色 | 任务 | 产出 |
|---|---|---|
| nc-spec | NC 官方格式规范调研 | `_tmp_fa_review/nc_format_spec_2026-09-17.md`（含官方 style guide 原文 PDF） |
| nc-gap | GB→NC 差距审计 | `_tmp_fa_review/nc_gap_audit_2026-09-17.md`（v2 含词数超限发现） |
| nc-ms | 文稿生成器改造 | `generate_manuscript_nc.py` + 转换报告（85/85 自检） |
| nc-sn | 附注生成器改造 | `notebooks/68_gen_supplementary_nc.py` + 报告 |
| nc-guide | 复现指南改造 | `notebooks/100_gen_reproducibility_nc.js` + 报告 |
| nc-cl | 封面信改写 | `generate_cover_letter_nc.py` + 报告（510 词） |
| team-lead | Note 首引映射 + 构建脚本 + finalize + 发布 | `99_build_nc_v48.py` + `_tmp_fa_review/finalize_v48_nc.py` |

## 2. 关键规范决策（以官网为准）

- **Introduction 带标题**（NC 官方格式指南明确；纠正任务书假设）
- **参考文献**：≥6 作者 → 第一作者 + et al.（NC 规则，比 GB 更简）；56 条全转 Nature 风格（期刊斜体带点、卷号加粗、en dash 全页码、年份末尾括号）；6 条六作者条目（#4/#20/#27/#29/#37/#56）截断
- **正文引用**：[n] 方括号 → 上标数字（69 组；CI 方括号守卫生效零误伤；3 组随 Data/Code availability 去引用删除）
- **Supplementary 命名**：Figure S1→Supplementary Fig. 1、Table S1→Supplementary Table 1、Note X.Y→Supplementary Note 1-15（按正文首引顺序；未引用小节保留十进制改称 Section X.Y）
- **面板标签**：正文/图注 42 处 (A)-(E)→(a)-(e)；图 PDF 内标签本轮不改（用户决策：先文本层）
- **Declarations**：NC 固定顺序 Methods→Data availability→Code availability→References→Acknowledgements（含 Funding）→Author contributions→Competing interests；删 Declarations 总块/Ethics/Consent 三节；Data/Code 声明不带引用
- **结构**：删 Conclusions（并入 Discussion）、Keywords、List of abbreviations；Results 3 个 L3 + Discussion 3 个 L2 小节去标题；5 个超 60 字符 L2 标题缩短；Introduction 末段改 'Here, we show' 句式；Abstract 149 词；标题去冒号 11 词

## 3. 交叉验证

- **构建 61/61 PASS**（`99_build_nc_v48.py`）：三名工人自检脚本全过 + SN/Guide/CL 内联检查 + 17 项科学数值回归锚点（Strong=39、CI [7.37, 8.02]、1.74 [1.64, 1.84]、Augur 0.442/0.564、4,851/31,764/24,413、AUC 0.80、6.10-fold、1.3-fold、7.70、Zenodo 22735744、GSE96583/GSE109774、bootstrap-t 0.953/0.951-SN）+ 包完整性
- **nc-ms DOCX 自检 85/85**：一级标题顺序 = NC 固定顺序；无 Keywords/Conclusions/abbreviations；[n] 引用组=0；上标 run=77；Data/Code availability 无引用；56 条参考文献 Nature 格式（斜体/粗体 run 验证）；无 Heading 3；L2 全部 ≤60 字符
- 首轮构建 4 个失败均为断言口径错误（图计数 23→22、TOC 重复计数、'5,151' 记忆锚点错误实为 '4,851'、0.953 在 SN 非 MS），修正后全绿——内容零返工
- **finalize**：v48 zip **65,521,245 B / 32 条目**，复现包 302 文件（52,765,417 B，sha b0d8602b…），内嵌校验一致；NC 生成器链 5 文件已镜像入复现包

## 4. 遗留事项（已决策）

- 正文词数 12,151 / Methods 4,437 超 NC 指南（5,000/3,000）→ **按现状投**，NC 首次投稿格式宽松，压缩留返修阶段（内容手术宜由一作主刀）
- 图 PDF 内面板标签大写 → 本轮不改（首次投稿宽松，返修时与图件重渲染一并处理）
- Nature Portfolio Reporting Summary 表单 → 投稿时在线填写（Nature 系统内表单，非本地文件）
- 指南内引用 `results/figures_submission/Supplementary_Figure_S13.pdf` 为仓内产物路径（描述复现流程，非投稿命名），保留

## 5. 结论

**CLOSED** — v48 NC 投稿包构建完成并通过全部验证，构建断言与工人独立自检双通道一致。

审计文件：`results/audit/v48_nc_format_audit_2026-09-17.md`（本文件）；各转换报告见 `_tmp_fa_review/nc_*_report_2026-09-17.md`
