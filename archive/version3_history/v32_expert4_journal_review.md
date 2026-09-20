# CKI v32 独立审稿 — E4: 学术出版与同行评议

**审稿日期**: 2026-08-02
**审稿人**: E4 (Academic Publishing & Peer Review)
**审稿对象**: version3/CKI_NAR_Submission_v32/ (32 文件，3.2 MB ZIP 已解压)
**对比基准**: v28 审稿评分 7.85/10 (v28_expert_panel_synthesis.md)
**评分**: 8.3/10 (v28: 7.85/10, Δ: +0.45)

---

## 1. 核心发现概要

v32 相对于 v28 在学术出版维度取得了实质性改进：P0-1 Strong candidate 计数矛盾（58→30）已修复，P0-3 校准因子 CI [4.12, 9.33] 已在正文 5 处添加，E4-1~E4-7 全部 7 项 Minor 问题已解决，Cover Letter 过度声明（"orthogonal"、"confirmed baseline behavior"）已移除。投稿包文件完整，无缺失。

然而，独立审稿发现 **2 个新 Major 问题**：(1) 7 张补充图（S3–S9）仅在图例部分定义，从未在正文 Methods/Results/Discussion 中引用，违反 NAR 补充材料引用规范；(2) 8 篇参考文献（Ref 31–35, 40–41, 44）从未在正文中引用，属于 orphan references。这两个问题均为 NAR 编辑办公室常规检查项目，需在投稿前修复。

**Critical: 0 | Major: 2 | Minor: 4**

---

## 2. v28→v32 修复验证（逐项 E4-1~E4-7）

### E4-1: Abstract ≤200 词 ✅ 已修复

- **验证方法**: `wc -w` 统计 Manuscript fulltext line 11（Abstract 段落）
- **结果**: 194 词（wc -w 计数）；MANIFEST 声称 195 词（差异来自特殊字符 ω/≥/≤ 的分词方式）
- **NAR 限制**: ≤200 词
- **结论**: ✅ 合规，余量 5–6 词

### E4-2: AUC Rank 4/5 设计原理解释 ✅ 已修复

- **位置**: Manuscript line 61
- **原文**: "This moderate ranking is expected by design: CKI down-weights shared HK gene patterns to isolate functional divergence, trading some ability to detect global transcriptional identity for enhanced sensitivity to functional specialization. The AUC rank therefore validates that CKI captures a distinct signal rather than being a better general-purpose classifier."
- **结论**: ✅ 设计原理解释充分，将排名劣势转化为方法论优势论证

### E4-3: Acknowledgements 扩展 ✅ 已修复

- **位置**: Manuscript line 107
- **内容**: 已扩展至三类致谢：
  1. 数据提供者：Tabula Muris Consortium, Tabula Sapiens Consortium, TCGA Research Network, Siletti et al. brain atlas team
  2. 工具/库开发者：scanpy, scipy, scikit-learn, broader open-source scientific Python ecosystem
  3. 参考资源团队：HRT Atlas team
- **结论**: ✅ 从 v28 的简略致谢显著扩展

### E4-4: 参考文献 47 篇 ✅ 已修复

- **验证方法**: 逐行计数 Manuscript lines 136–182
- **结果**: 47 篇参考文献
- **格式**: Author1,A., Author2,B. and Author3,C. (Year) Title. *Journal*, **Volume**, Pages.
- **et al. 规则**: 10 作者后 et al.（如 Ref 1 Regev et al.、Ref 11 Siletti et al.），符合 NAR 规范
- **结论**: ✅ 数量和格式合规

### E4-5: Bergmann glia 归属确认 ✅ 已修复

- **位置**: Manuscript line 89
- **原文**: "Bergmann glia had the lowest global ω (2.37) and no Strong signals, consistent with their developmentally fixed, transcriptionally constrained state in the adult cerebellum (30). Bergmann glia are patterned into topographic molecular zones that align with cerebellar functional compartments (28), and their low global ω reflects their specialized role in maintaining Purkinje cell layer architecture with minimal regional transcriptional variation. The astrocyte CBL (cerebellar lobule) vs. CBV (cerebellar vermis) Strong signal reflects the established molecular topography difference across cerebellar compartments, rather than any migratory event."
- **结论**: ✅ Bergmann glia 明确无 Strong signals；cerebellar CBL vs. CBV signal 归属 astrocytes 而非 Bergmann glia

### E4-6: L102/S12 全部补图 present ✅ 已修复

- **文件验证**: Supplementary_Figure_S1.pdf 至 Supplementary_Figure_S12.pdf 全部 12 个 PDF 文件存在
- **图例验证**: Manuscript lines 122–133 定义 S1–S12 全部 12 个补充图图例
- **结论**: ✅ 文件和图例完整

### E4-7: 内嵌表格分离 ✅ 已修复

- **验证**: Table1-2.docx (37,475 bytes) 和 Table1-2_fulltext.txt (976 bytes) 作为独立文件存在
- **内容**: Table 1 (5 metrics ROC-AUC) 和 Table 2 (17 cell types cross-organ ranking)
- **正文引用**: Manuscript line 59 引用 Table 1，line 68 引用 Table 2
- **结论**: ✅ 表格已分离为独立文件

---

## 3. NAR 规范合规检查

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| Abstract ≤200 词 | ✅ | 194–195 词 |
| 章节结构 | ✅ | Abstract → Keywords → Introduction → M&M → Results → Discussion → Data availability → Acknowledgements → Author contributions → Funding → Conflict of interest → Figure legends → References |
| 引用格式 | ✅ | 括号编号 (1), (2,3), (9,10)，NAR 格式 |
| 参考文献 et al. 规则 | ✅ | 10 作者后 et al. |
| 图表面板标签 | ✅ | 大写 (A), (B), (C), (D), (E) — 在图例中使用 |
| Graphical Abstract | ✅ | PDF + PNG + SVG 三格式 |
| 关键词 | ✅ | 5 个关键词 |
| Running title | ✅ | "CKI: Baseline-Normalized Divergence Index" |
| ORCID | ✅ | 0000-0002-0698-0754 (Manuscript line 7, Cover Letter line 8) |
| 数据可用性声明 | ✅ | Manuscript line 103, 含 GitHub URL + Zenodo DOI |
| AI 使用声明 | ✅ | Cover Letter line 19 |
| 推荐审稿人 | ✅ | 6 位（Theis, Teichmann, Welch, Yanai, Zhang, Wang） |
| 利益冲突声明 | ✅ | "The authors declare no competing interests" |
| 资金声明 | ✅ | NSFC 32370682 + 国家科技重大专项 2026ZD01910500 |
| 作者贡献 | ✅ | X.W. and L.Z. conceived/designed; L.Z. developed/analyzed/figured; X.W. contributed to data curation/validation/writing |

**评分: 7.5/10** — 扣分项为补充图引用和参考文献引用问题（见第 7 节）

---

## 4. 跨文档一致性验证

### 4.1 关键词全局搜索

| 关键词 | 搜索结果 | 一致性 |
|--------|----------|:------:|
| `Cohen` | 仅在 Manuscript lines 26, 42 出现，上下文为 "not as a parametric test statistic such as Cohen's d" — 正确用于与 SES 对比 | ✅ |
| `EVT` / `GPD` / `extreme value` / `generalized Pareto` | 全文档无匹配 — v28 P0-2 修复已彻底清除 | ✅ |
| `FDR` | 正文/补充/Repro Guide 一致声明：BH FDR applied within dataset；residual model "FDR not applicable" | ✅* |
| `neutral` | 仅在描述 Ka/Ks 的 synonymous sites 上下文出现（lines 15, 95, 115, Sup 24）— 科学正确 | ✅ |
| `selective` | 仅在 "selectively diverged"（line 85）和 "selectively constrained"（line 87）上下文出现 — 描述生物模式，非选择声明 | ✅ |
| `orthogonal` | Cover Letter: 无匹配 ✅；Manuscript body: 2 处（lines 77, 98）| ⚠️ |
| `confirmed baseline` | 全文档无匹配 | ✅ |

### 4.2 关键数值跨文档一致性

| 数值 | Manuscript | Supplementary | Repro Guide | Cover Letter | MANIFEST | 一致性 |
|------|:----------:|:------------:|:-----------:|:------------:|:--------:|:------:|
| 校准因子 ω=6.67 | ✅ (5处) | ✅ | ✅ | ✅ ("empirical baseline") | ✅ | ✅ |
| 95% CI [4.12, 9.33] | ✅ (5处) | ❌ | ❌ | ❌ | ✅ (2处) | ✅† |
| GitHub URL | ✅ (2处) | — | ✅ | ✅ | — | ✅ |
| Zenodo DOI | ✅ | — | — | ✅ | — | ✅ |
| Python ≥3.10 | ✅ | — | — | ✅ | — | ✅ |
| Strong candidates = 30 | ✅ (6+10+10+1+3=30) | ✅ | ✅ | ✅ ("30") | ✅ | ✅ |
| 16/30 P-value floor | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Brain nuclei = 888,263 | ✅ | ✅ | ✅ | — | — | ✅ |
| B=1,000 (bootstrap) | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| B=10,000 (residual) | ✅ | ✅ | ✅ | — | ✅ | ✅ |

*MANIFEST line 72 仍使用 "FDR-significant descriptive" 措辞，与正文 "formal FDR correction is not applicable" 存在矛盾（Minor）
†CI 仅出现在 Manuscript 和 MANIFEST 中，未在补充材料和 Repro Guide 中出现，但 MANIFEST 声称 "5 locations"，与 Manuscript 一致

### 4.3 Cover Letter 过度声明检查

| 检查项 | v28 状态 | v32 状态 |
|--------|----------|----------|
| "orthogonal" | 存在 | ✅ 已移除 |
| "confirmed baseline behavior" | 存在 | ✅ 已移除（改为 "empirical baseline"）|
| "developmental origin signatures" | 存在 | ✅ 已改为 "developmental signatures" |

**跨文档一致性评分: 8.5/10**

---

## 5. 图表完整性验证

### 5.1 主图（6 张）

| 图号 | 文件 | 正文引用 | 面板标签 | 状态 |
|------|------|:--------:|:--------:|:----:|
| Figure 1 | figure1.pdf (77KB) | ✅ line 45 | A–E | ✅ |
| Figure 2 | figure2.pdf (52KB) | ✅ lines 47, 51 | A–D | ✅ |
| Figure 3 | figure3.pdf (85KB) | ✅ line 56 | A–E | ✅ |
| Figure 4 | figure4.pdf (64KB) | ✅ line 63 | A–E | ✅ |
| Figure 5 | figure5.pdf (50KB) | ✅ line 70 | A–D | ✅ |
| Figure 6 | figure6.pdf (64KB) | ✅ line 74 | A–E | ✅ |

### 5.2 补充图（12 张）

| 图号 | 文件 | 图例定义 | **正文引用** | 状态 |
|------|------|:--------:|:------------:|:----:|
| S1 | Supplementary_Figure_S1.pdf (443KB) | ✅ line 122 | ✅ line 49 | ✅ |
| S2 | Supplementary_Figure_S2.pdf (181KB) | ✅ line 123 | ✅ line 98 | ✅ |
| S3 | Supplementary_Figure_S3.pdf (274KB) | ✅ line 124 | ❌ **未引用** | ⚠️ Major |
| S4 | Supplementary_Figure_S4.pdf (570KB) | ✅ line 125 | ❌ **未引用** | ⚠️ Major |
| S5 | Supplementary_Figure_S5.pdf (579KB) | ✅ line 126 | ❌ **未引用** | ⚠️ Major |
| S6 | Supplementary_Figure_S6.pdf (68KB) | ✅ line 127 | ❌ **未引用** | ⚠️ Major |
| S7 | Supplementary_Figure_S7.pdf (63KB) | ✅ line 128 | ❌ **未引用** | ⚠️ Major |
| S8 | Supplementary_Figure_S8.pdf (749KB) | ✅ line 129 | ❌ **未引用** | ⚠️ Major |
| S9 | Supplementary_Figure_S9.pdf (19KB) | ✅ line 130 | ❌ **未引用** | ⚠️ Major |
| S10 | Supplementary_Figure_S10.pdf (21KB) | ✅ line 131 | ✅ lines 24, 99 | ✅ |
| S11 | Supplementary_Figure_S11.pdf (97KB) | ✅ line 132 | ✅ lines 56, 99 | ✅ |
| S12 | Supplementary_Figure_S12.pdf (23KB) | ✅ line 133 | ✅ line 54 ("Supplementary Figures 10–12") | ✅ |

**关键发现**: S3–S9（7 张补充图）仅在 Supplementary Figure legends 部分定义（lines 122–130），从未在正文 Methods/Results/Discussion 中引用。NAR 要求所有补充图表在正文中引用。这是投稿前需修复的 Major 问题。

**图表完整性评分: 7.5/10** — 扣分因 7 张补充图未在正文引用

---

## 6. Cover Letter 质量

### 6.1 必备要素检查

| 要素 | 状态 | 位置 |
|------|:----:|------|
| 通讯作者信息 | ✅ | Li Zhang, Institute of Blood Transfusion, CAMS & PUMC, Chengdu; Chinese Institute for Brain Research, Beijing |
| ORCID 0000-0002-0698-0754 | ✅ | line 8 |
| 投稿日期 | ✅ | August 02, 2026 |
| 期刊编辑称呼 | ✅ | "The Editors, Nucleic Acids Research, Oxford University Press" |
| 文章类型声明 | ✅ | "Original Research Article" |
| AI 使用声明 | ✅ | line 19: "AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors, who take full responsibility." |
| 数据可用性 | ✅ | line 19: GitHub URL + Zenodo DOI |
| 推荐审稿人 ≥6 | ✅ | 6 位：Theis, Teichmann, Welch, Yanai, Zhang, Wang — 含邮箱和非利益冲突声明 |
| 利益冲突声明 | ✅ | line 19: "declare no competing interests" |
| 独创性声明 | ✅ | line 19: "not been published elsewhere, is not under consideration by any other journal" |
| 合著者批准 | ✅ | line 19: "Both authors have approved the manuscript" |

### 6.2 Cover Letter 措辞检查

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| 无 "orthogonal" | ✅ | v28 修复确认 |
| 无 "confirmed baseline behavior" | ✅ | v28 修复确认，已改为 "empirical baseline" |
| 无 "developmental origin signatures" | ✅ | 已改为 "developmental signatures" |
| "30 cell-type-specific developmental signatures" | ⚠️ | line 18 称 "30 cell-type-specific developmental signatures"，但正文明确 14/30 无统计学证据（P≥0.76，line 81），不应称为 "signatures"。建议改为 "30 threshold-passing candidates (16 statistically significant)" |

**Cover Letter 评分: 9.0/10** — 仅 "30 signatures" 措辞需调整

---

## 7. 新发现问题

### Major-1: 7 张补充图（S3–S9）未在正文中引用

**位置**: Manuscript body text (lines 1–121)

**详情**:
- S3 (TCGA per-cancer matrices): 图例定义于 line 124，但正文 TCGA Results 段（lines 63–66）无引用
- S4 (Method comparison performance): 图例定义于 line 125，但正文 Method comparison 段（lines 56–61）无引用
- S5 (Cross-organ conservation raw data): 图例定义于 line 126，但正文 Cross-organ 段（lines 68–72）无引用
- S6 (Brain regional analysis details): 图例定义于 line 127，但正文 Brain regional 段（lines 74–77）无引用
- S7 (Developmental signature detection): 图例定义于 line 128，但正文 Developmental signature 段（lines 79–91）无引用
- S8 (ω distribution characterization): 图例定义于 line 129，但正文无引用（Limitations line 99 讨论了 ω 分布非正态性但未引用 S8）
- S9 (Permutation null distribution): 图例定义于 line 130，但正文 Multiplicative model 段（line 35）和 Limitations（line 100）未引用

**NAR 规范**: NAR 要求所有补充材料在正文中引用（"Supplementary material should be referenced in the text"）

**修复建议**: 在对应 Results 段落添加 "(Supplementary Fig. S3)" 等引用。预计工作量 ~15 min。

### Major-2: 8 篇参考文献未在正文中引用（Orphan references）

**位置**: Manuscript References section (lines 136–182)

**详情**:
| Ref # | Line | Reference | 应引用位置 |
|:-----:|:----:|-----------|-----------|
| 31 | 166 | Shemer & Jung 2024, microglial colonization | Discussion microglia biology (line 76) |
| 32 | 167 | Menassa et al. 2022, microglia lifespan | Discussion microglia biology (line 76) |
| 33 | 168 | Barry-Carroll et al. 2023, microglia clonal expansion | Discussion microglia biology (line 76) |
| 34 | 169 | Schaffenrath et al. 2024, BBB heterogeneity | Discussion vascular cells (line 76) |
| 35 | 170 | Jones et al. 2023, meningeal fibroblast | Discussion fibroblasts (line 76) |
| 40 | 175 | Yang 2007, PAML 4 | Discussion Ka/Ks limitations (line 95) |
| 41 | 176 | Tan et al. 2020, microglial heterogeneity | Discussion microglia (line 76) |
| 44 | 179 | Bakken et al. 2021, motor cortex comparison | Discussion cross-species (line 98) |

**验证方法**: 使用 `grep -oP "\(\d{1,2}(?:,\s*\d{1,2})*\)"` 提取正文所有引用编号，与参考文献列表交叉比对

**NAR 规范**: NAR 要求所有列出的参考文献必须在正文中引用

**修复建议**: 在对应段落添加引用，或删除未引用的参考文献。预计工作量 ~10 min。

### Minor-1: MANIFEST "FDR-significant descriptive" 措辞矛盾

**位置**: MANIFEST_v32.txt line 72

**详情**: MANIFEST 写道 "Residual Model: 30 Strong, 16/30 FDR-significant descriptive, 14/30 non-significant"，但正文（lines 81, 100）明确声明 "formal Benjamini-Hochberg FDR correction is not applicable"。使用 "FDR-significant" 即使附加 "descriptive" 限定词仍与正文矛盾。

**修复建议**: 改为 "16/30 reached P-value floor (descriptive evidence), 14/30 non-significant"

### Minor-2: 补充材料图编号不一致

**位置**: Supplementary_fulltext.txt

**详情**: 补充材料中图编号混用两种格式：
- "Supplementary Figure 8"（line 69，无 S 前缀）
- "Supplementary Figure 9"（line 69，无 S 前缀）
- "Supplementary Figure S10"（line 73，有 S 前缀）
- "Supplementary Figure S11"（line 75，有 S 前缀）
- "Supplementary Figure S12"（line 73，有 S 前缀）

**修复建议**: 统一为 "Supplementary Figure S8" / "Supplementary Figure S9" 格式

### Minor-3: Cover Letter "30 developmental signatures" 过度声明

**位置**: Cover Letter line 18

**详情**: Cover Letter 称 "brain regional analysis identifying 30 cell-type-specific developmental signatures among 31,764 cross-region comparisons"，但正文（line 81）明确指出 14/30 "showed no evidence of deviation from the multiplicative null model (all P ≥ 0.76)"，且 line 91 声明 "These 14 signals are likely dominated by stochastic variation... should not be interpreted as evidence of biological structure." 将 30 个 threshold-passing candidates 全部称为 "developmental signatures" 与正文的谨慎表述不一致。

Abstract 也有类似表述（line 11: "30 cell-type developmental signatures"），但 Abstract 至少添加了 "(two statistically significant)" 限定。Cover Letter 无此限定。

**修复建议**: Cover Letter 改为 "30 threshold-passing candidates (16 statistically significant)" 或 "16 cell-type-specific developmental signatures (plus 14 threshold-passing candidates)"

### Minor-4: "orthogonal" 在正文中的使用

**位置**: Manuscript lines 77, 98

**详情**: 虽然 v28 修复了 Cover Letter 中的 "orthogonal" 过度声明，但正文中仍有 2 处使用：
- Line 77: "providing an orthogonal transcriptomic readout of migration history"
- Line 98: "providing a notable orthogonal validation that the residual model specifically detects fixed developmental signatures"

这两处 "orthogonal" 的使用意为 "互补的/独立的"，在科学写作中属常见用法，不构成过度声明。但考虑到 v28 审稿已将 "orthogonal" 标记为需移除的措辞，建议在正文中也替换为 "complementary" 或 "independent" 以保持一致性。

**严重性**: Minor（不影响科学准确性，仅措辞一致性）

---

## 8. 综合评分与建议

### 8.1 评分明细

| 维度 | 评分 | 权重 | 加权分 |
|------|:----:|:----:|:------:|
| NAR 规范合规 | 7.5 | 25% | 1.875 |
| 跨文档一致性 | 8.5 | 25% | 2.125 |
| Cover Letter 质量 | 9.0 | 20% | 1.800 |
| 图表完整性 | 7.5 | 15% | 1.125 |
| 投稿包完整性 | 9.5 | 15% | 1.425 |
| **综合** | | **100%** | **8.35** |

**综合评分: 8.3/10** (v28: 7.85/10, Δ: +0.45)

### 8.2 评分趋势

```
v25: 7.50 (第一批专家)
v26: 7.80 (第一批专家)
v28: 7.85 (第二批专家, Strong candidate 计数矛盾)
v32: 8.30 (第三批独立审稿, E4-1~E4-7 全部修复 + 2 新 Major)
```

### 8.3 v28→v32 改进项

| 改进项 | v28 问题 | v32 状态 | 分值贡献 |
|--------|----------|----------|:--------:|
| P0-1 Strong candidate 计数 | 58≠30 | ✅ 6+10+10+1+3=30 | +0.15 |
| P0-3 校准因子 CI | 无 CI | ✅ [4.12, 9.33] 5 处 | +0.10 |
| E4-1 Abstract 词数 | 198 词 | ✅ 194–195 词 | +0.05 |
| E4-2 AUC Rank 解释 | 缺失 | ✅ 设计原理解释 | +0.05 |
| E4-3 Acknowledgements | 简略 | ✅ 扩展三类 | +0.03 |
| E4-4 参考文献数 | 偏少 | ✅ 47 篇 | +0.03 |
| E4-5 Bergmann glia 归属 | 不清 | ✅ 明确无 Strong | +0.02 |
| E4-6 S12 补图 | truncation | ✅ 全部 present | +0.02 |
| E4-7 内嵌表格 | 未分离 | ✅ Table1-2.docx | +0.02 |
| Cover Letter 过度声明 | orthogonal/confirmed | ✅ 已移除 | +0.05 |
| 新 Major: S3-S9 未引用 | — | ❌ -0.15 | -0.15 |
| 新 Major: 8 篇 orphan refs | — | ❌ -0.10 | -0.10 |
| Minor: MANIFEST FDR 措辞 | — | ❌ -0.03 | -0.03 |
| Minor: 补充图编号不一致 | — | ❌ -0.02 | -0.02 |

### 8.4 修复优先级

**投稿前必须修复（~25 min）**:

1. **Major-1**: 在正文对应段落添加 S3–S9 的引用（~15 min）
   - S3 → TCGA Results (line 63 附近)
   - S4 → Method comparison (line 56 附近)
   - S5 → Cross-organ conservation (line 68 附近)
   - S6 → Brain regional analysis (line 74 附近)
   - S7 → Developmental signature detection (line 79 附近)
   - S8 → Limitations 第七条 ω 分布 (line 99 附近)
   - S9 → Multiplicative model Methods (line 35 附近)

2. **Major-2**: 在正文添加 8 篇 orphan references 的引用，或删除这些参考文献（~10 min）

**投稿前建议修复（~10 min）**:

3. **Minor-1**: MANIFEST line 72 "FDR-significant descriptive" → "reached P-value floor (descriptive)"
4. **Minor-3**: Cover Letter "30 developmental signatures" → "30 threshold-passing candidates (16 statistically significant)"

**Revision 阶段修复**:

5. **Minor-2**: 补充材料统一图编号为 "Supplementary Figure S8/S9" 格式
6. **Minor-4**: 正文 "orthogonal" → "complementary"（2 处）

### 8.5 Desk Reject 风险评估

**风险: 低**

- Cover Letter 完整，含 ORCID、AI 声明、6 位推荐审稿人、Zenodo DOI
- 稿件结构符合 NAR 方法学位定位
- 6 张主图 + 12 张补充图 + Graphical Abstract 全部 present
- 数据可用性声明完整
- 无 Critical 问题

**主要风险**: NAR 编辑办公室可能在格式审查时发现未引用的补充图和参考文献，要求 minor correction。建议投稿前修复 Major-1 和 Major-2 以避免不必要的往返。

### 8.6 总结

v32 是迄今最完善的版本。E4-1~E4-7 全部 7 项 Minor 问题已解决，P0-1 计数矛盾和 P0-3 校准 CI 两个关键问题已修复。Cover Letter 质量显著提升，过度声明已清除。投稿包文件完整，跨文档数值一致性良好。

2 个新 Major 问题（补充图 S3–S9 未引用、8 篇 orphan references）均为编辑性问题而非科学问题，修复简单（~25 min），但需在投稿前完成以确保通过 NAR 格式审查。

**Critical: 0 | Major: 2 | Minor: 4**

**推荐行动**: 修复 2 个 Major 后投稿 NAR。预计修复后评分 8.7/10。
