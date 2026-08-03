# E4 稿件质量与期刊策略审稿报告 — v26

**审稿日期**: 2026-08-02
**审稿专家**: E4 (稿件质量与期刊策略)
**审稿对象**: CKI_NAR_Submission_v26 (27 文件, 3.4 MB)
**目标期刊**: Nucleic Acids Research (IF ~16.6)
**v25 评分**: 8.30/10 (E4维度)

---

## 1. 执行摘要

**v26 评分: 7.80/10** (v25 E4: 8.30 → 7.80, −0.50)

v26 成功修复了 v25 专家团提出的 P0 项 (N1-N4) 和 P1 项 (N6-N9) 中的绝大多数。跨文档一致性显著改善：标题统一为 "Baseline-Normalized"，术语 "Cohen's d" 全部替换为 "SES"，"neutral" 不再用于描述 CKI 的 HK 基因，Table 1 数值对齐至 102/5,151。

但审稿发现 **3 个新问题**（v25 未识别）和 **2 个 deferred 项的残留**，其中最严重的是 **Supplementary Figures S8-S12 缺失**——稿件正文引用了 S1-S12 共 12 张补充图，但投稿包仅包含 S1-S7。这是 desk reject 级别的风险。

| 类别 | 数量 | 状态 |
|------|:----:|:----:|
| v25 P0 修复 (N1-N4, N8) | 5 | 4 验证通过, 1 部分修复 (N8 编号仍重复) |
| v25 P1 修复 (N6-N9) | 3 | 3 验证通过 |
| v25 Deferred (N5, N10) | 2 | 确认残留，严重程度评估如下 |
| **新发现** | 3 | 1 Critical (S8-S12缺失) + 2 Minor |

---

## 2. v25 P0/P1 修复验证

### 2.1 P0 修复逐项验证

| ID | 描述 | 状态 | 验证详情 |
|----|------|:----:|----------|
| **N1** | Supplementary/Cover Letter 标题 "Selective" → "Baseline-Normalized" | ✅ 通过 | 三文档标题完全一致："CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling"。全文搜索 "Selective"（大写首字母）在 Supplementary 和 Cover Letter 中零命中。稿件正文中 "selectively" 作为副词使用 (line 85, 87) 属正常学术用语，非标题术语残留。 |
| **N2** | "Cohen's d" → "SES" 全局清理 (7处残留) | ✅ 通过 | 全文搜索 "Cohen" 在所有4个 fulltext 文件中零命中。"SES" 在 Manuscript (5处)、Supplementary (3处)、Repro Guide (2处) 中一致使用。定义公式 "SES = (ω_obs − μ_null) / σ_null" 在多文档中一致。 |
| **N3** | Table 1 数值对齐 99→102, 4,851→5,151 | ✅ 通过 | Table1-2_fulltext.txt: "102 cell types, 5,151 pairs"。Manuscript line 59: "102 cell types, 5,151 pairs"。全文无 "99 cell types" 或 "4,851 pairs" 残留。 |
| **N4** | "neutral" 术语清理 (Fig 1-3 legends, 5处) | ✅ 通过 | 稿件中 "neutral" 仅在3处合法上下文中出现：(1) "neutral drift" (line 15, Introduction, 生物学概念); (2) "pure neutral drift" (line 99, Discussion limitations, 描述 Ka/Ks 对比); (3) "neutral baseline" (line 119, Fig 1 legend, 描述 Ka/Ks 的 Ks 而非 CKI 的 k_n)。Supplementary line 24 中 "the neutral reference in Ka/Ks" 是对比 Ka/Ks 与 CKI 的正确用法。**无一处将 CKI 的 HK 基因描述为 "neutral"。** |
| **N8** | Limitations 编号修复 "Seventh" → "Eleventh" | ⚠️ 部分修复 | 见 §3.1 新问题 N-E4-1 |

### 2.2 P1 修复逐项验证

| ID | 描述 | 状态 | 验证详情 |
|----|------|:----:|----------|
| **N6** | Repro Guide brain k_n 描述修正 | ✅ 通过 | Repro Guide §3.2 (line 68): "The brain atlas analysis also uses per-pair top-200 DE genes for k_f, but unlike the other datasets, uses per-pair k_n (computed separately for each cell-type/region pair from the same HK gene set) rather than a global k_n; this is because brain k_n exhibits substantial cross-pair variability (CV = 97.35%)." 描述准确清晰。 |
| **N7** | Supplementary SN 3.3 EVT GPD 拟合诊断 | ✅ moot | 稿件已放弃 EVT 方法，改用描述性 P 值解读 ("formal FDR correction is not applicable")。搜索 "EVT" / "GPD" / "extreme value" / "generalized Pareto" 在所有 fulltext 中零命中。N7 修复已无意义，但 MANIFEST 仍引用 EVT，需更新。 |
| **N9** | Brain PMI 讨论扩展 | ✅ 通过 | Limitations 第五条 (line 103) 包含完整 PMI 讨论：PMI 变异 → RNA 完整性 → 区域/细胞类型差异 → 神经元特异性降解 → 胶质细胞较少受影响 → 建议发育时间课程验证。从 v25 的1句话扩展为4+句，修复充分。 |

### 2.3 Cover Letter M-W1/W2/W3 修复验证

| 修复项 | 状态 | 验证 |
|--------|:----:|------|
| M-W1: 移除 "orthogonal" | ✅ | Cover Letter 全文无 "orthogonal" |
| M-W2: "confirmed baseline behavior" → "empirical baseline" | ✅ | Cover Letter line 18: "calibration establishing an empirical baseline for equivalent populations" |
| M-W3: "developmental origin signatures" → "developmental signatures" | ✅ | Cover Letter line 18: "30 cell-type-specific developmental signatures" |

---

## 3. 新发现问题

### 3.1 Critical — Supplementary Figures S8-S12 缺失

**ID**: N-E4-1
**严重程度**: 🔴 Critical (desk reject 风险)
**涉及文件**: 投稿包目录

**详情**:

稿件正文引用了 Supplementary Figures S1-S12 共 12 张补充图，且在 Supplementary Figure legends 部分有完整的 S1-S12 图注。但投稿包仅包含以下补充图文件：

```
Supplementary_Figure_S1.pdf  ✓
Supplementary_Figure_S2.pdf  ✓
Supplementary_Figure_S3.pdf  ✓
Supplementary_Figure_S4.pdf  ✓
Supplementary_Figure_S5.pdf  ✓
Supplementary_Figure_S6.pdf  ✓
Supplementary_Figure_S7.pdf  ✓
Supplementary_Figure_S8.pdf  ✗ 缺失
Supplementary_Figure_S9.pdf  ✗ 缺失
Supplementary_Figure_S10.pdf ✗ 缺失
Supplementary_Figure_S11.pdf ✗ 缺失
Supplementary_Figure_S12.pdf ✗ 缺失
```

缺失的 5 张图对应 Phase B/C 统计升级生成的关键诊断图：
- **S8**: ω 分布特征 (skewness, Q-Q plots, normality tests)
- **S9**: 残差模型置换零分布 (permutation null for residual model)
- **S10**: JS divergence 维度不变性 (dimensionality invariance)
- **S11**: 逐对 k_n 变异性 (per-pair k_n variability, CV=97.35%)
- **S12**: 校准 omega (calibrated omega, ω_cal = ω/6.67)

这些图在正文中被多处引用：
- Line 24: "Supplementary Fig. S10"
- Line 54: "Supplementary Figures 10–12"
- Line 56: "Supplementary Fig. S11"
- Line 73 (Supplementary): "(Supplementary Figure S12.)"
- Line 75 (Supplementary): "(Supplementary Figure S10.)"
- Line 77 (Supplementary): "(Supplementary Figure S11.)"
- Line 134-137: 完整的 S8-S12 图注

Repro Guide (line 253-267) 确认这些图以 `ed_fig8` 至 `ed_fig12` 的文件名存在于 `results/figures_final/` 目录，但未被打包进投稿包。

**MANIFEST 不一致**: MANIFEST 声明 "Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf"，未提及 S8-S12。同时 MANIFEST 声称 "BH-FDR across 31,764 EVT-extrapolated P-values" 和 "16/30 significant (FDR<0.05)"，但稿件正文明确声明 "formal Benjamini-Hochberg FDR correction is not applicable"——MANIFEST 与稿件正文矛盾。

**建议**: 将 S8-S12 的 PDF 文件重命名并加入投稿包；更新 MANIFEST 以匹配稿件正文描述。

### 3.2 Medium — Limitations 编号重复

**ID**: N-E4-2
**严重程度**: 🟡 Medium
**涉及文件**: CKI_NAR_Manuscript_fulltext.txt (line 103-104)

**详情**:

N8 修复将 v25 中的重复 "Seventh" 改为 "Eleventh"，但未检查是否已存在 "Eleventh" 条目。当前 Limitations 段落的编号为：

| 编号 | 内容 | 位置 |
|------|------|------|
| First | pseudobulk level | line 103 |
| Second | HK gene set | line 103 |
| Third | HVG inflation | line 103 |
| Fourth | TCGA bulk RNA-seq | line 103 |
| Fifth | PMI | line 103 |
| Sixth | FDR within dataset | line 103 |
| Seventh | ω distribution non-normal | line 103 |
| Eighth | permutation testing | line 103 |
| Ninth | bootstrap CIs | line 103 |
| Tenth | calibration baseline n=6 | line 103 |
| **Eleventh** | k_n/k_f gene set sizes | line 103 |
| **Twelfth** | hybrid scheme | line 103 |
| Thirteenth | BH-FDR separate | line 103 |
| Fourteenth | no synthetic validation | line 103 |
| Fifteenth | parameter justification | line 103 |
| **Eleventh** ← 重复 | multiplicative residual model permutation | line 104 |
| **Twelfth** ← 重复 | calibration factor cross-scheme | line 104 |

实际共 17 条 limitations，但编号只到 15，且 11 和 12 各重复一次。line 104 的两条应编号为 Sixteenth 和 Seventeenth。

### 3.3 Minor — Graphical Abstract 占位符文本未更新

**ID**: N-E4-3
**严重程度**: ⚪ Minor
**涉及文件**: CKI_NAR_Manuscript_fulltext.txt (line 9)

**详情**:

Manuscript line 9: "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]"

但 CKI_graphical_abstract.pdf/png/svg 三个文件已在投稿包中 (82KB/335KB/225KB)。占位符文本应更新为正式引用，或在 NAR 在线投稿系统中作为单独上传的文件注明。

---

## 4. Deferred 项残留评估

### 4.1 N5 — 参考文献未按首次引用顺序编号

**状态**: 确认残留
**严重程度**: 🟡 Medium
**评估**:

稿件正文首次引用序列为: (16), (1), (2), (3), (32), (31), (5), (6), (7,8), (9), (30), (4), (25), (26,27), (28), (29), (14), (11,12), (10)...

Reference 1 (Harmony, Korsunsky et al.) 首次出现在第 2 个引用位置；Reference 4 (HRT Atlas) 首次出现在第 12 个引用位置。编号严重不按引用顺序。

**NAR 要求**: 参考文献按首次引用顺序编号。当前编号不符合此要求。

**严重程度评估**: 中等。NAR 编辑可能在初审时标记此问题，但不太可能导致 desk reject。建议在 revision 阶段修复，或在投稿前修复以避免编辑质疑。

**修复工作量**: 需系统性重编号——遍历全文所有引用，按首次出现顺序重新分配编号，同时更新 References 列表。估计 1-2 小时。

### 4.2 N10 — Python 版本声明不一致

**状态**: 确认残留
**严重程度**: ⚪ Minor
**评估**:

| 文件 | 位置 | 声明 |
|------|------|------|
| Manuscript | line 39 (Methods) | "Python 3.13.12" (具体运行版本) |
| Manuscript | line 107 (Data Availability) | "Python 3.8+" (最低要求) |
| Cover Letter | line 19 | "Python (≥3.9)" (最低要求) |
| Repro Guide | line 9 | "Python: 3.13.12" (验证环境) |

**不一致**: Manuscript 说 3.8+，Cover Letter 说 ≥3.9。两者相差一个版本号。具体版本 3.13.12 在 Manuscript 和 Repro Guide 间一致。

**建议**: 统一为 "Python ≥3.9" (因为 Cover Letter 声明 ≥3.9 更保守，且 Manuscript Methods 已注明实际运行版本为 3.13.12)。

---

## 5. NAR 格式合规审查

### 5.1 结构与排版

| 检查项 | 状态 | 详情 |
|--------|:----:|------|
| Abstract ≤200 词 | ✅ | 194 词 (NAR 限制: ≤200) |
| Running title ≤50 字符 | ✅ | "CKI: Baseline-Normalized Divergence Index" = 39 字符 |
| Keywords 位置 | ✅ | 位于 Abstract 之后、Introduction 之前 |
| 章节完整性 | ✅ | Abstract → Keywords → Introduction → Materials and Methods → Results → Discussion → Data availability → Supplementary Data → Acknowledgements → Author contributions → Funding → Conflict of interest → Figure legends → References |
| 图表标签 A/B/C 大写 | ✅ | 所有 Figure legends 使用 (A), (B), (C) 格式 |
| ORCID | ✅ | 0000-0002-0698-0754 (Manuscript + Cover Letter) |
| 作者 affiliation | ✅ | 2 个机构标注清晰 |
| 通讯作者 | ✅ | Email + ORCID |

### 5.2 引用格式

**当前格式**: 正文引用为括号编号 (16), (1), (2) 等。

**NAR 标准**: NAR 使用上标编号或方括号编号 [16], [1]。括号编号 (16) 不是 NAR 标准格式。

**注意**: 由于 fulltext 是 DOCX 的纯文本提取，上标格式可能存在于 DOCX 中但不可见。需在 DOCX 中验证。

**References 列表格式**: ✓ 符合 NAR 标准
- 作者格式: Surname,A.B., Surname2,C.D. and Surname3,E.F. ✓
- 期刊名斜体 ✓
- 卷号粗体 ✓
- 年份在括号内 ✓

### 5.3 Cover Letter 质量评估

| 检查项 | 状态 | 详情 |
|--------|:----:|------|
| 6 位审稿人建议 | ✅ | Theis, Teichmann, Welch, Yanai, Zhang, Wang — 涵盖单细胞基因组学、计算生物学、癌症基因组学 |
| 审稿人邮箱 | ✅ | 全部提供 |
| AI 使用声明 | ✅ | "AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors, who take full responsibility." |
| 未投稿声明 | ✅ | "This work has not been published elsewhere, is not under consideration by any other journal, and has not been previously submitted to Nucleic Acids Research." |
| ORCID | ✅ | 0000-0002-0698-0754 |
| 数据可用性 | ✅ | GitHub URL + Zenodo DOI (10.5281/zenodo.15670808) |
| 利益冲突声明 | ✅ | "declare no competing interests" |
| 资助信息 | ✅ | NSFC 32370682 + 国家科技重大专项 2026ZD01910500 |
| 日期 | ✅ | August 02, 2026 |
| 签名 | ✅ | Li Zhang (Corresponding) + Xianming Wu (First Author) |
| 无 "orthogonal" 过度声明 | ✅ | M-W1 修复验证 |
| "empirical baseline" (非 "confirmed") | ✅ | M-W2 修复验证 |
| "developmental signatures" (非 "origin signatures") | ✅ | M-W3 修复验证 |

**Cover Letter 质量评价**: 专业、完整、无过度声明。审稿人建议涵盖领域专家且无明显利益冲突。AI 声明符合 NAR 政策。

### 5.4 跨文档一致性

| 检查项 | Manuscript | Supplementary | Cover Letter | Repro Guide | 状态 |
|--------|:----:|:----:|:----:|:----:|:----:|
| 标题 | Baseline-Normalized | Baseline-Normalized | Baseline-Normalized | N/A | ✅ 一致 |
| 术语 "SES" | ✓ | ✓ | N/A | ✓ | ✅ 一致 |
| 术语 "constrained baseline" | ✓ | ✓ | N/A | ✓ | ✅ 一致 |
| Table 1 数值 | 102/5,151 | N/A | N/A | N/A | ✅ 一致 |
| GitHub URL | ✓ | ✓ | ✓ | ✓ | ✅ 一致 |
| Zenodo DOI | ✓ | N/A | ✓ | N/A | ✅ 一致 |
| Python 版本 | 3.13.12 / 3.8+ | N/A | ≥3.9 | 3.13.12 | ⚠️ N10 残留 |
| Bootstrap B | 1,000 | 1,000 | N/A | 1,000 | ✅ 一致 |
| ω 校准常数 | 6.67 | 6.67 | N/A | 6.67 | ✅ 一致 |
| 脑区比较数 | 31,764 | 31,764 | 31,764 | 31,764 | ✅ 一致 |
| Strong 候选数 | 30 | 30 | 30 | 30 | ✅ 一致 |

---

## 6. 投稿包完整性

### 6.1 文件清单 (27 文件)

| 类别 | 文件数 | 文件 |
|------|:------:|------|
| 主文档 | 4 DOCX | Manuscript, Supplementary, Cover Letter, Repro Guide |
| 表格 | 1 DOCX | Table1-2.docx |
| 主图 | 6 PDF | figure1-6.pdf |
| 补充图 | **7 PDF** | S1-S7 (**缺 S8-S12**) |
| Graphical Abstract | 3 | PDF + PNG + SVG |
| MANIFEST | 1 | MANIFEST_v26.txt |
| Fulltext (审稿用) | 6 TXT | 4 DOCX + Table1-2 的文本提取 |
| **合计** | 27 | — |

### 6.2 大文件检查

无 >10MB 文件。最大文件: Supplementary_Figure_S5.pdf (579 KB)。总包大小 3.4 MB。NAR 投稿系统通常允许单文件 ≤50MB，总投稿 ≤350MB。✅ 无问题。

### 6.3 格式检查

- 主图: PDF ✓ (NAR 接受 PDF/TIFF/EPS)
- 补充图: PDF ✓
- Graphical Abstract: PNG + PDF + SVG ✓ (NAR 要求 PNG/JPEG, ≤300KB 单文件 — PNG 335KB 略超 NAR 建议但可接受)
- 文档: DOCX ✓ (NAR 接受 DOCX/LaTeX)
- Table: DOCX ✓ (NAR 接受 Excel/Word)

---

## 7. Desk Reject 风险评估

### 7.1 风险矩阵

| 风险项 | 概率 | 严重程度 | 说明 |
|--------|:----:|:--------:|------|
| **S8-S12 缺失** | 高 | 🔴 高 | 编辑/审稿人发现正文引用不存在的图 → 退回修改 |
| 引用格式 (括号 vs 上标) | 中 | 🟡 中 | 需在 DOCX 中验证；如为括号格式需改为上标 |
| 参考文献编号顺序 (N5) | 低 | 🟡 中 | 编辑可能标记但不退稿 |
| Limitations 编号重复 | 低 | ⚪ 低 | 编辑可能标记但不退稿 |
| Python 版本不一致 | 低 | ⚪ 低 | 不影响审稿 |

### 7.2 综合风险评估

**Desk reject 概率: 10-15%**

主要风险来自 S8-S12 缺失。如果编辑在初审时发现正文引用的补充图不存在，可能直接退回要求补齐。其他问题（编号、格式）通常在 revision 阶段修复，不会导致 desk reject。

**建议**: 投稿前必须补齐 S8-S12 文件并更新 MANIFEST。

---

## 8. 评分维度分解

| 维度 | v25 E4 | v26 E4 | Δ | 说明 |
|------|:------:|:------:|:--:|------|
| 标题与术语一致性 | 7.0 | 9.0 | +2.0 | N1/N2/N4 全部修复，三文档标题完全一致 |
| Cover Letter 质量 | 8.5 | 9.0 | +0.5 | M-W1/W2/W3 修复验证通过，无过度声明 |
| NAR 格式合规 | 8.0 | 7.5 | −0.5 | Abstract/Running title 合规；引用格式待 DOCX 验证 |
| 投稿包完整性 | 8.5 | 6.0 | −2.5 | S8-S12 缺失是关键扣分项 |
| 结构与排版 | 8.5 | 8.0 | −0.5 | Limitations 编号重复 |
| 跨文档数据一致性 | 8.0 | 9.0 | +1.0 | N3 修复 + 核心数值全部一致 |
| 参考文献质量 | 7.5 | 7.5 | 0 | N5 未修复 (deferred) |
| **加权综合** | **8.30** | **7.80** | **−0.50** | — |

---

## 9. 优先级行动方案

### P0 — 投稿前必须修复 (阻塞项)

| 优先级 | ID | 描述 | 估计时间 |
|:------:|:---|------|:--------:|
| 🥇 | N-E4-1 | 补齐 Supplementary Figures S8-S12 (5个PDF) 并更新 MANIFEST | 30min |
| 🥈 | N-E4-2 | 修复 Limitations 编号: line 104 的 "Eleventh"→"Sixteenth", "Twelfth"→"Seventeenth" | 5min |
| 🥉 | N10 | 统一 Python 版本声明: Manuscript "3.8+" → "≥3.9" | 5min |

### P1 — 强烈建议

| ID | 描述 | 估计时间 |
|----|------|:--------:|
| N5 | 参考文献按首次引用顺序重新编号 | 1-2h |
| MANIFEST | 更新 MANIFEST 以匹配稿件正文 (移除 EVT 引用, 添加 S8-S12) | 10min |
| N-E4-3 | Graphical Abstract 占位符文本更新 | 5min |

### P2 — DOCX 验证 (需打开 DOCX 文件确认)

| 检查项 | 说明 |
|--------|------|
| 引用格式 | 确认 DOCX 中引用为上标或方括号，非括号 |
| 行距 | 确认双倍行距 (NAR 要求) |
| 页码 | 确认页码编号 |
| 字体 | 确认正文使用标准字体 (Arial/Times New Roman, 12pt) |

---

## 10. 底线

1. **v26 的 P0/P1 修复基本成功**。N1-N4 全部验证通过，N6/N9 验证通过，N7 因方法变更而 moot。Cover Letter 的 M-W1/W2/W3 修复全部验证通过。跨文档一致性显著提升。

2. **S8-S12 缺失是唯一的新 Critical 问题**。稿件正文有完整图注但投稿包无对应文件。这是 desk reject 级别风险，必须在投稿前解决。修复成本极低（文件已在 Repro Guide 记录的路径中，仅需重命名并打包）。

3. **N8 修复引入了新的编号重复**。"Seventh" → "Eleventh" 的替换未检查已有编号，导致两个 "Eleventh" 和两个 "Twelfth"。修复仅需改两个词。

4. **Deferred 项 (N5, N10) 确认残留但严重程度可控**。N5 (参考文献编号) 是中等严重程度的格式问题，NAR 编辑可能标记但不会导致退稿。N10 (Python 版本) 是次要不一致。两者均可在 revision 阶段修复。

5. **投稿建议**: 修复 P0 三项 (补齐 S8-S12, 修复编号, 统一 Python 版本) 后可直接投稿 NAR。P1 项建议在投稿前修复但不阻塞。预计修复后评分 ≥8.5/10。

---

## 附录: 搜索验证记录

| 搜索项 | 搜索范围 | 命中数 | 结论 |
|--------|----------|:------:|------|
| "Cohen" | 4 fulltext | 0 | N2 修复验证 ✓ |
| "Selective" (大写) | 4 fulltext | 0 | N1 修复验证 ✓ |
| "selectively" (小写) | Manuscript | 2 | 副词用法，非标题术语 ✓ |
| "neutral" | 4 fulltext | 5 | 均为合法上下文 (Ka/Ks 对比/neutral drift) ✓ |
| "orthogonal" | Cover Letter | 0 | M-W1 修复验证 ✓ |
| "orthogonal" | Manuscript | 4 | 学术用法 (orthogonal information/validation)，非 Cover Letter 过度声明 ✓ |
| "confirmed baseline" | Cover Letter | 0 | M-W2 修复验证 ✓ |
| "empirical baseline" | Cover Letter | 1 | M-W2 修复验证 ✓ |
| "EVT" / "GPD" | 4 fulltext | 0 | 方法已变更，N7 moot ✓ |
| "Cohen's d" | 4 fulltext | 0 | N2 修复验证 ✓ |
| "99 cell types" | 4 fulltext | 0 | N3 修复验证 ✓ |
| "4,851 pairs" | 4 fulltext | 0 | N3 修复验证 ✓ |
| "102 cell types" | Manuscript + Table1-2 | 2 | N3 修复验证 ✓ |
| "5,151 pairs" | Manuscript + Table1-2 | 2 | N3 修复验证 ✓ |
| Supplementary Figure S8-S12 | 文件系统 | 0 文件 | **N-E4-1 缺失** 🔴 |
| Supplementary Figure S8-S12 | Manuscript 正文引用 | 12 引用 | 引用存在但文件缺失 🔴 |
