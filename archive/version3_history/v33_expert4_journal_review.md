# CKI v33 独立审稿 — E4: 学术出版与同行评议

**审稿日期**: 2026-08-03
**审稿人**: E4 (Academic Publishing & Peer Review)
**审稿对象**: version3/CKI_NAR_Submission_v33/ (5 文件 fulltext + MANIFEST)
**对比基准**: v32 审稿评分 8.3/10 (v32_expert4_journal_review.md)
**评分**: 8.4/10 (v32: 8.3/10, Δ: +0.1)

---

## 1. 核心发现概要

v33 相对于 v32 在 Minor 层面取得了可验证的改进：m1（MANIFEST FDR 术语统一）、m2（CV 60%→52%）、m3（Cover Letter "30 signatures"措辞修正）、m4–m8（多项细节修正）、m16（补充图编号统一）均已正确实施。Abstract 195 词合规，47 篇参考文献完整，Cover Letter 必备要素齐全。

然而，**E4 在 v32 提出的 2 个 Major 问题（M3: S3–S9 未在正文引用；M4: 8 篇 orphan references）均未实际修复**，尽管 MANIFEST 声称已修复。经逐行验证：(1) S3–S9 仍仅在图例部分定义（lines 124–130），正文 Methods/Results/Discussion 中无任何引用；(2) References 31–35, 40–41 仍未在正文中引用（7 篇 orphan）。Ref 44 (Bakken et al. 2021) 已通过 m12 修复在 line 98 以 "(44; Supplementary Fig. S2)" 形式引用，故 orphan references 从 8 篇减至 7 篇。m17（"orthogonal"→"complementary"）仅部分修复（line 98 已改，line 77 仍为 "orthogonal"）。

**Critical: 0 | Major: 2（v32 遗留，未修复）| Minor: 3**

---

## 2. v32→v33 修复验证（逐项）

### 2.1 Major 修复验证

#### M3: S3–S9 补充图在正文中引用 — ❌ **未修复**

- **MANIFEST 声称**: "M3: S3-S9 supplementary figures cited in manuscript body"
- **验证方法**: `head -120 CKI_NAR_Manuscript_fulltext.txt | grep -oP 'Supplementary Fig\.? S\d+'`，提取正文（lines 1–120，即 Abstract 至 Discussion 结束）所有补充图引用
- **结果**: 正文仅引用 S1（line 49）、S2（line 98）、S10（lines 24, 99）、S11（line 56）、S10–12（line 54）。**S3, S4, S5, S6, S7, S8, S9 在正文中无任何引用**
- **图例定义**: S3–S9 定义于 lines 124–130（Supplementary Figure legends 段），与 v32 完全一致
- **结论**: ❌ M3 未修复。S3–S9 仍为 orphan supplementary figures，状态与 v32 相同

#### M4: 8 篇 orphan references（31–35, 40–41, 44）引用或删除 — ⚠️ **部分修复（1/8 已引用）**

- **MANIFEST 声称**: "M4: 8 orphan references (31-35, 40-41, 44) cited or removed"
- **验证方法**: `head -134 CKI_NAR_Manuscript_fulltext.txt | grep -oP '\(\d{1,2}(?:[,;]\s*\d{1,2})*\)'`，提取正文+图例所有引用编号，与参考文献列表交叉比对。额外搜索 semicolon 格式引用 `(44;`
- **结果**: 正文引用的参考文献编号为 1–30, 36–39, 42, 43, 44, 45–47。**Ref 44 已在 line 98 以 "(44; Supplementary Fig. S2)" 形式引用**（通过 m12 cross-species 讨论修复）。但 **Refs 31, 32, 33, 34, 35, 40, 41 仍未被引用**（7 篇 orphan）
- **参考文献列表**: 47 篇全部保留（lines 136–182）
- **作者名搜索**: 在正文（lines 1–120）中搜索 "Shemer"、"Menassa"、"Barry-Carroll"、"Schaffenrath"、"Yang 2007"、"PAML"、"Tan 2020" — 均无匹配
- **结论**: ⚠️ 部分修复。Ref 44 已引用（v32 的 8 篇 orphan 减至 7 篇），但 Refs 31–35, 40–41 仍为 orphan

| Ref # | 行号 | 参考文献 | 应引用位置 | v32 状态 | v33 状态 |
|:-----:|:----:|---------|-----------|:--------:|:--------:|
| 31 | 166 | Shemer & Jung 2024, microglial colonization | Discussion microglia (line 76) | orphan | **仍 orphan** |
| 32 | 167 | Menassa et al. 2022, microglia lifespan | Discussion microglia (line 76) | orphan | **仍 orphan** |
| 33 | 168 | Barry-Carroll et al. 2023, microglia clonal expansion | Discussion microglia (line 76) | orphan | **仍 orphan** |
| 34 | 169 | Schaffenrath et al. 2024, BBB heterogeneity | Discussion vascular cells (line 76) | orphan | **仍 orphan** |
| 35 | 170 | Jones et al. 2023, meningeal fibroblast | Discussion fibroblasts (line 76) | orphan | **仍 orphan** |
| 40 | 175 | Yang 2007, PAML 4 | Discussion Ka/Ks limitations (line 95) | orphan | **仍 orphan** |
| 41 | 176 | Tan et al. 2020, microglial heterogeneity | Discussion microglia (line 76) | orphan | **仍 orphan** |
| 44 | 179 | Bakken et al. 2021, motor cortex comparison | Discussion cross-species (line 98) | orphan | ✅ **已引用** (m12) |

### 2.2 Minor 修复验证

| 修复项 | MANIFEST 描述 | 验证方法 | 结果 | 状态 |
|--------|-------------|---------|------|:----:|
| m1 | MANIFEST FDR → "P-value floor (descriptive)" | `grep "FDR" MANIFEST_v33.txt` | MANIFEST line 54: "16/30 P-value floor (descriptive)" | ✅ |
| m2 | CV 60% → 52% | Manuscript line 52 | "CV ≈ 52%" + "coefficient of variation of ~52%" | ✅ |
| m3 | Cover Letter "30 signatures" → "30 threshold-passing candidates" | Cover Letter line 18 | "30 threshold-passing candidates (16 statistically significant)" | ✅ |
| m4 | requirements.txt 在 Repro Guide section 1 | `grep "requirements.txt" Repro Guide` | Line 24: `pip install -r requirements.txt` | ✅ |
| m5 | Supp P-value precision 0.001 → 9.99e-04 | Supplementary line 68 | "P = 9.99 × 10⁻⁵" 统一使用 | ✅ |
| m6 | Brain cell types 9→10 (committed OPCs) | `grep "committed oligodendrocyte" Manuscript` | 2 处提及 committed OPCs | ✅ |
| m7 | MANIFEST "section 2" → "section 1" | `grep "section" MANIFEST` | 无 "section 2" 残留 | ✅ |
| m8 | Abstract "two statistically significant" → "two with permutation support" | Manuscript line 11 | "(two with permutation support)" | ✅ |
| m16 | Supp numbering "Figure 8" → "S8" | `grep "Supplementary Figure" Supp` | 统一为 "Supplementary Figure S8/S9" | ✅ |
| m17 | "orthogonal" → "complementary" (2 occurrences) | `grep "orthogonal" Manuscript` | Line 98: "complementary" ✅; **Line 77: 仍为 "orthogonal" ❌** | ⚠️ 部分 |

### 2.3 m17 详细验证

- **MANIFEST 声称**: "m17: 'orthogonal' → 'complementary' (2 occurrences)"
- **v32 状态**: 正文 lines 77, 98 各 1 处 "orthogonal"
- **v33 验证**:
  - Line 77: "providing an **orthogonal** transcriptomic readout of migration history" — ❌ **未修改**
  - Line 98: "providing a notable **complementary** validation" — ✅ 已修改
  - Line 116 (Figure 2 legend): "confirming ω captures **orthogonal** information" — 未修改（v32 未标记此项，但属同类措辞）
- **结论**: ⚠️ 2 处中仅修复 1 处（line 98），line 77 仍为 "orthogonal"

---

## 3. NAR 格式合规检查

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| Abstract ≤200 词 | ✅ | 195 词（`wc -w` 计数），余量 5 词 |
| 章节结构 | ✅ | Abstract → Keywords → Introduction → M&M → Results → Discussion → Data availability → Acknowledgements → Author contributions → Funding → Conflict of interest → Figure legends → References |
| 引用格式 | ✅ | 括号编号 (1), (2,3), (9,10)，NAR 格式 |
| 参考文献 et al. 规则 | ✅ | 10 作者后 et al.（如 Ref 1 Regev et al.） |
| 图表面板标签 | ✅ | 大写 (A), (B), (C), (D), (E) |
| Graphical Abstract | ✅ | PDF + PNG + SVG 三格式（MANIFEST 声明） |
| 关键词 | ✅ | 5 个关键词 |
| Running title | ✅ | "CKI: Baseline-Normalized Divergence Index" |
| ORCID | ✅ | 0000-0002-0698-0754 (Manuscript line 7, Cover Letter line 8) |
| 数据可用性声明 | ✅ | Manuscript line 103，含 GitHub URL + Zenodo DOI |
| AI 使用声明 | ✅ | Cover Letter line 19 |
| 推荐审稿人 | ✅ | 6 位（Theis, Teichmann, Welch, Yanai, Zhang, Wang） |
| 利益冲突声明 | ✅ | "The authors declare no competing interests" |
| 资金声明 | ✅ | NSFC 32370682 + 国家科技重大专项 2026ZD01910500 |
| 作者贡献 | ✅ | X.W. and L.Z. conceived/designed; L.Z. developed/analyzed/figured; X.W. contributed to data curation/validation/writing |
| 补充图正文引用 | ❌ | S3–S9 未在正文引用（NAR 要求所有补充材料在正文中引用） |
| 参考文献完整性 | ❌ | 7 篇参考文献未在正文中引用（Refs 31–35, 40–41；Ref 44 已引用） |

**NAR 格式合规评分: 7.5/10** — 与 v32 相同，扣分项仍为补充图引用和参考文献引用问题

---

## 4. 文档一致性检查

### 4.1 关键词全局搜索

| 关键词 | 搜索结果 | 一致性 |
|--------|----------|:------:|
| `Cohen` | 仅在 Manuscript line 26 出现，上下文为 "not as a parametric test statistic such as Cohen's d" | ✅ |
| `EVT` / `GPD` / `extreme value` | 全文档无匹配 | ✅ |
| `FDR` | 正文/补充/MANIFEST 一致：BH FDR within dataset；residual model "FDR not applicable"；MANIFEST 使用 "P-value floor (descriptive)" | ✅ |
| `neutral` | 仅在 Ka/Ks synonymous sites 上下文出现 | ✅ |
| `selective` | 仅在 "selectively diverged" / "selectively constrained" 上下文出现 | ✅ |
| `orthogonal` | Cover Letter: 无匹配 ✅；Manuscript body: **2 处**（lines 77, 116）；Supplementary: 无匹配 | ⚠️ |
| `confirmed baseline` | 全文档无匹配 | ✅ |
| `developmental origin signatures` | Cover Letter: 无匹配 ✅；Manuscript body: 4 处（lines 78, 85, 98 等）— 作为生物学机制名称使用，科学正确 | ✅ |

### 4.2 关键数值跨文档一致性

| 数值 | Manuscript | Supplementary | Repro Guide | Cover Letter | MANIFEST | 一致性 |
|------|:----------:|:------------:|:-----------:|:------------:|:--------:|:------:|
| 校准因子 ω=6.67 | ✅ (5处) | ✅ | ✅ | ✅ ("empirical baseline") | ✅ | ✅ |
| 95% CI [4.12, 9.33] | ✅ (5处) | ❌ | ❌ | ❌ | ✅ | ✅† |
| GitHub URL | ✅ (2处) | — | ✅ | ✅ | — | ✅ |
| Zenodo DOI | ✅ | — | — | ✅ | — | ✅ |
| Python ≥3.10 | ✅ | — | — | ✅ | — | ✅ |
| Strong candidates = 30 | ✅ (6+10+10+1+3) | ✅ | ✅ | ✅ ("30") | ✅ | ✅ |
| 16/30 P-value floor | ✅ | ✅ | ✅ | ✅ ("16 statistically significant") | ✅ | ✅ |
| 14/30 non-significant | ✅ (P≥0.76) | ✅ | ✅ | — | ✅ | ✅ |
| Brain nuclei = 888,263 | ✅ | ✅ | ✅ | — | — | ✅ |
| B=1,000 (bootstrap) | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| B=10,000 (residual) | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| CV ≈ 52% | ✅ (line 52) | — | — | — | — | ✅ (v33 新) |

†CI 仅出现在 Manuscript 和 MANIFEST 中，未在补充材料和 Repro Guide 中出现

### 4.3 Cover Letter 措辞检查

| 检查项 | v32 状态 | v33 状态 |
|--------|----------|----------|
| 无 "orthogonal" | ✅ | ✅ |
| 无 "confirmed baseline behavior" | ✅ | ✅ |
| 无 "developmental origin signatures" | ✅ | ✅ |
| "30 threshold-passing candidates (16 statistically significant)" | ❌ ("30 developmental signatures") | ✅ 已修正 (m3) |

**跨文档一致性评分: 9.0/10** — 较 v32（8.5）提升，m1 FDR 术语统一和 m2 CV 修正消除了跨文档矛盾

---

## 5. 图表完整性验证

### 5.1 主图（6 张）

| 图号 | 正文引用 | 面板标签 | 状态 |
|------|:--------:|:--------:|:----:|
| Figure 1 | ✅ line 45 | A–E | ✅ |
| Figure 2 | ✅ lines 47, 51 | A–D | ✅ |
| Figure 3 | ✅ line 56 | A–E | ✅ |
| Figure 4 | ✅ line 63 | A–E | ✅ |
| Figure 5 | ✅ line 70 | A–D | ✅ |
| Figure 6 | ✅ line 74 | A–E | ✅ |

### 5.2 补充图（12 张）

| 图号 | 图例定义 | **正文引用** | 状态 |
|------|:--------:|:------------:|:----:|
| S1 | ✅ line 122 | ✅ line 49 | ✅ |
| S2 | ✅ line 123 | ✅ line 98 | ✅ |
| S3 | ✅ line 124 | ❌ **未引用** | ⚠️ Major |
| S4 | ✅ line 125 | ❌ **未引用** | ⚠️ Major |
| S5 | ✅ line 126 | ❌ **未引用** | ⚠️ Major |
| S6 | ✅ line 127 | ❌ **未引用** | ⚠️ Major |
| S7 | ✅ line 128 | ❌ **未引用** | ⚠️ Major |
| S8 | ✅ line 129 | ❌ **未引用** | ⚠️ Major |
| S9 | ✅ line 130 | ❌ **未引用** | ⚠️ Major |
| S10 | ✅ line 131 | ✅ lines 24, 99 | ✅ |
| S11 | ✅ line 132 | ✅ line 56 | ✅ |
| S12 | ✅ line 133 | ✅ line 54 ("Supplementary Figures 10–12") | ✅ |

**关键发现**: S3–S9（7 张补充图）仍仅在 Supplementary Figure legends 部分定义（lines 124–130），从未在正文 Methods/Results/Discussion 中引用。**与 v32 状态完全一致，M3 未修复。**

**图表完整性评分: 7.5/10** — 与 v32 相同

---

## 6. Cover Letter 质量

### 6.1 必备要素检查

| 要素 | 状态 | 位置 |
|------|:----:|------|
| 通讯作者信息 | ✅ | Li Zhang, IBT CAMS & PUMC, CIBR Beijing |
| ORCID 0000-0002-0698-0754 | ✅ | line 8 |
| 投稿日期 | ✅ | August 03, 2026 |
| 期刊编辑称呼 | ✅ | "The Editors, Nucleic Acids Research, Oxford University Press" |
| 文章类型声明 | ✅ | "Original Research Article" |
| AI 使用声明 | ✅ | line 19 |
| 数据可用性 | ✅ | line 19: GitHub URL + Zenodo DOI |
| 推荐审稿人 ≥6 | ✅ | 6 位：Theis, Teichmann, Welch, Yanai, Zhang, Wang |
| 利益冲突声明 | ✅ | "declare no competing interests" |
| 独创性声明 | ✅ | "not been published elsewhere, is not under consideration" |
| 合著者批准 | ✅ | "Both authors have approved the manuscript" |

### 6.2 Cover Letter 措辞检查

| 检查项 | 状态 | 说明 |
|--------|:----:|------|
| 无 "orthogonal" | ✅ | v28 修复维持 |
| 无 "confirmed baseline behavior" | ✅ | v28 修复维持 |
| "30 threshold-passing candidates (16 statistically significant)" | ✅ | v33 m3 修复 |
| 无过度声明 | ✅ | 措辞审慎 |

**Cover Letter 评分: 9.5/10** — 较 v32（9.0）提升，"30 signatures" 措辞已修正

---

## 7. 新发现问题

### New-1 (Minor): MANIFEST 声称 M3/M4 已修复但实际未修复

**位置**: MANIFEST_v33.txt lines 10–11

**详情**: MANIFEST 声称：
- "M3: S3-S9 supplementary figures cited in manuscript body"
- "M4: 8 orphan references (31-35, 40-41, 44) cited or removed"

但经逐行验证，S3–S9 仍仅在图例定义（lines 124–130），正文无引用；8 篇 orphan references 全部保留在参考文献列表中，正文无引用。两项 Major 修复均未实际执行。

**影响**: 投稿包元数据与实际内容不一致。NAR 编辑办公室在格式审查时依赖投稿包元数据了解修复状态，此类不一致可能影响编辑对作者沟通效率的评价。

**严重性**: Minor（不影响科学内容，但影响投稿包元数据可信度）

### New-2 (Minor): m17 部分修复 — line 77 仍为 "orthogonal"

**位置**: Manuscript line 77

**原文**: "This approach complements lineage tracing and developmental studies by providing an **orthogonal** transcriptomic readout of migration history."

**详情**: MANIFEST 声称 m17 修复了 2 处 "orthogonal"→"complementary"，但实际仅修复了 line 98（Discussion），line 77（Results）仍为 "orthogonal"。

**修复建议**: line 77 改为 "providing a complementary transcriptomic readout of migration history"

### New-3 (Minor): Figure 2 legend 仍有 "orthogonal"

**位置**: Manuscript line 116

**原文**: "All show negative correlation, confirming ω captures **orthogonal** information."

**详情**: v32 审稿仅检查了正文 body text 的 "orthogonal"（lines 77, 98），未检查图例。Figure 2 legend 中的 "orthogonal" 描述 CKI 与标准度量的关系，建议统一替换为 "complementary" 或 "independent"。

**严重性**: Minor（措辞一致性问题）

---

## 8. 问题汇总

### 8.1 问题清单

| 编号 | 严重性 | 描述 | v32 状态 | v33 状态 |
|------|:------:|------|:--------:|:--------:|
| M3 | Major | S3–S9 未在正文引用 | 发现 | **未修复**（MANIFEST 声称已修复） |
| M4 | Major | 7 篇 orphan references (31–35, 40–41) | 发现 (8篇) | **部分修复**（Ref 44 已引用，7/8 仍 orphan） |
| m17 | Minor | "orthogonal" 在 line 77 | 发现 | **部分修复**（line 98 已改，line 77 未改） |
| New-1 | Minor | MANIFEST 元数据与实际内容不一致 | — | **新发现** |
| New-2 | Minor | Figure 2 legend "orthogonal" | 未检查 | **新发现** |

### 8.2 v32→v33 修复对照

| v32 问题 | v33 状态 | 分值变化 |
|---------|----------|:--------:|
| Major-1: S3–S9 未引用 | ❌ 未修复 | 0 |
| Major-2: 8 篇 orphan refs | ⚠️ 部分修复 (Ref 44 已引用, 7 篇仍 orphan) | +0.03 |
| Minor-1: MANIFEST FDR 措辞 | ✅ 已修复 (m1) | +0.03 |
| Minor-2: 补充图编号不一致 | ✅ 已修复 (m16) | +0.02 |
| Minor-3: Cover Letter "30 signatures" | ✅ 已修复 (m3) | +0.03 |
| Minor-4: "orthogonal" 在正文 | ⚠️ 部分修复 (m17, 1/2) | +0.01 |
| 新: MANIFEST 元数据不一致 | ❌ 新问题 | -0.02 |
| 新: Figure legend "orthogonal" | ❌ 新发现 | -0.01 |
| m2: CV 60%→52% | ✅ 已修复 | +0.02 |
| m4–m8: 其他 Minor | ✅ 已修复 | +0.02 |

---

## 9. 评分理由与投稿建议

### 9.1 评分明细

| 维度 | v32 评分 | v33 评分 | 权重 | v33 加权分 | 变化说明 |
|------|:--------:|:--------:|:----:|:----------:|---------|
| NAR 规范合规 | 7.5 | 7.5 | 25% | 1.875 | S3–S9/orphan refs 未修复 |
| 跨文档一致性 | 8.5 | 9.0 | 25% | 2.250 | m1 FDR 术语、m2 CV 统一 |
| Cover Letter 质量 | 9.0 | 9.5 | 20% | 1.900 | m3 "30 signatures" 修正 |
| 图表完整性 | 7.5 | 7.5 | 15% | 1.125 | S3–S9 仍未引用 |
| 投稿包完整性 | 9.5 | 9.0 | 15% | 1.350 | MANIFEST 元数据不准确 |
| **综合** | **8.30** | | **100%** | **8.50** | |

**综合评分: 8.4/10** (v32: 8.3/10, Δ: +0.1)

> 注：加权计算为 8.50，但考虑到 M3/M4 声称修复却未修复这一信任影响因素，下调至 8.4。

### 9.2 评分趋势

```
v25: 7.50 (第一批专家)
v26: 7.80 (第一批专家)
v28: 7.85 (第二批专家)
v32: 8.30 (第三批独立审稿, E4-1~E4-7 修复 + 2 新 Major)
v33: 8.40 (第四批独立审稿, Minor 广泛修复但 2 Major 未实际修复)
```

### 9.3 评分理由

v33 评分仅微幅上升（+0.1），原因如下：

**加分因素（+0.15）**：
- m1 MANIFEST FDR 术语统一 → 跨文档一致性提升
- m2 CV 60%→52% 数值修正 → 消除跨文档矛盾
- m3 Cover Letter "30 signatures" 措辞修正 → Cover Letter 质量提升
- m16 补充图编号统一 → 消除 S8/S9 编号不一致
- m4–m8 多项细节修正 → 整体质量提升

**扣分因素（-0.05）**：
- M3/M4 声称修复但实际未修复 → MANIFEST 元数据可信度受损
- m17 仅部分修复 → 措辞一致性未完全达成
- Figure 2 legend "orthogonal" 未处理

**未变化因素**：
- M3（S3–S9 未引用）和 M4（orphan refs）与 v32 完全一致，既未恶化也未改善

### 9.4 修复优先级

**投稿前必须修复（~25 min）**:

1. **M3**: 在正文对应段落添加 S3–S9 的引用（~15 min）
   - S3 → TCGA Results (line 63 附近): "(Supplementary Fig. S3)"
   - S4 → Method comparison (line 56 附近): "(Supplementary Fig. S4)"
   - S5 → Cross-organ conservation (line 68 附近): "(Supplementary Fig. S5)"
   - S6 → Brain regional analysis (line 74 附近): "(Supplementary Fig. S6)"
   - S7 → Developmental signature detection (line 79 附近): "(Supplementary Fig. S7)"
   - S8 → Limitations 第七条 ω 分布 (line 99 附近): "(Supplementary Fig. S8)"
   - S9 → Multiplicative model Methods (line 35 附近): "(Supplementary Fig. S9)"

2. **M4**: 在正文添加 7 篇 orphan references 的引用，或删除（~10 min）
   - Refs 31–33, 41 → Discussion microglia biology (line 76 附近)
   - Ref 34 → Discussion vascular cells (line 76 附近)
   - Ref 35 → Discussion fibroblasts (line 76 附近)
   - Ref 40 → Discussion Ka/Ks limitations (line 95 附近): "formal phylogenetic framework (e.g., PAML (40))"
   - Ref 44 → ✅ 已在 line 98 引用（无需修复）

3. **m17 完成**: line 77 "orthogonal" → "complementary"（~1 min）

**投稿前建议修复（~5 min）**:

4. **New-2**: Figure 2 legend line 116 "orthogonal" → "complementary" 或 "independent"
5. **New-1**: 更新 MANIFEST，如实标注 M3/M4 状态

### 9.5 Ref 44 引用验证

在验证过程中发现，line 98 包含 "(44; Supplementary Fig. S2)"，表明 Ref 44 (Bakken et al. 2021) **已在 v33 中引用**。此引用通过 m12（"Cross-species Spearman r referenced in Discussion"）添加，并非 M4 的直接修复。因此：
- v32 的 8 篇 orphan references 中，**Ref 44 已解决**（通过 m12 间接修复）
- v33 实际 orphan references 为 **7 篇**（Refs 31–35, 40–41）
- MANIFEST 声称 "8 orphan references cited or removed" 不准确——仅 1 篇被引用，7 篇仍为 orphan

### 9.6 Desk Reject 风险评估

**风险: 低**

- Cover Letter 完整，含 ORCID、AI 声明、6 位推荐审稿人、Zenodo DOI
- 稿件结构符合 NAR 方法学位定位
- 6 张主图 + 12 张补充图 + Graphical Abstract 全部 present
- 数据可用性声明完整
- 无 Critical 问题

**主要风险**: NAR 编辑办公室在格式审查时可能发现未引用的补充图和参考文献，要求 minor correction。由于 MANIFEST 声称已修复但实际未修复，若编辑基于 MANIFEST 进行核查，可能导致信任损失。建议投稿前实际完成 M3/M4 修复。

### 9.7 总结

v33 在 Minor 层面取得了广泛且可验证的改进：m1–m8、m16 共 9 项 Minor 修复均正确实施，Cover Letter 质量从 9.0 提升至 9.5，跨文档一致性从 8.5 提升至 9.0。

然而，**E4 在 v32 提出的 2 个 Major 问题均未完全修复**，尽管 MANIFEST 声称已修复。M3（S3–S9 未引用）完全未修复；M4（orphan references）仅部分修复——Ref 44 通过 m12 间接引用，但 Refs 31–35, 40–41（7 篇）仍为 orphan。这是本版本最关键的发现：投稿包元数据与实际内容存在不一致。m17（"orthogonal"→"complementary"）仅部分修复（2 处中仅修复 1 处）。

2 个 Major 问题均为编辑性问题而非科学问题，修复简单（~25 min），但必须在投稿前实际完成。建议作者：
1. 在正文添加 S3–S9 引用和 7 篇 orphan references 引用
2. 完成 m17 剩余部分（line 77）
3. 更新 MANIFEST 如实反映修复状态

**Critical: 0 | Major: 2（v32 遗留，M3 未修复/M4 部分修复）| Minor: 3**

**推荐行动**: 实际完成 M3/M4 修复后投稿 NAR。预计修复后评分 8.8/10。
