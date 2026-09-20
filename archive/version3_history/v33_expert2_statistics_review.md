# CKI v33 独立审稿 — E2: 定量生物学与统计

**审稿日期**: 2026-08-03
**评分**: 8.7/10 (v32: 8.4/10, Δ: +0.3)

## 1. 核心发现概要

v33 在统计维度上实现了稳健的增量改进。v32 的 6 项 Minor 问题中，4 项彻底修复、1 项部分修复、1 项 MANIFEST 声称修复但实际未实施。统计方法学核心框架保持正确：Permutation P 值公式 P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) 在全部 6 处文档位置完全一致；BH-FDR 分层策略（cell-type 级 bootstrap vs. pair 级残差模型）正确实施；SES 非参数定位明确；校准因子 CI [4.12, 9.33] 在 5 处一致报告。

关键修复包括：CV 事实性错误 60% → 52% 已更正（m2）；MANIFEST "FDR-significant" 术语矛盾已消除（m1）；摘要 "statistically significant" 改为 "permutation support"（m8）；单侧检验方向性限制作为 Limitation #18 明确声明（m10）；P 值下限饱和率的替代解释作为 Limitation #19 补充（m11）；P 值精度 9.99×10⁻⁴ 统一标注（m5）。

**新发现问题**：m9（k_n floor TT/NN 触发比例量化）在 MANIFEST 中声称已修复为 Limitation #20，但手稿中不存在 "Twentieth" 条目，Limitations 编号从 #19 直接跳至 #21——MANIFEST 声称与文本内容不一致。此外，Introduction 第 18 行仍使用 "both statistically significant"，与 Abstract 的 m8 修复不一致；"orthogonal" 一词仍出现 2 处（m17 声称已修复），从统计角度构成误导（CKI ω 与标准指标的 Spearman r = −0.38 至 −0.57 是负相关而非正交）。

**Critical: 0, Major: 0, Minor: 6**

## 2. v32→v33 修复验证

### 2.1 m2: CV 60% → 52% — 修复 ✅

v32 问题：手稿第 52 行报告 "CV ≈ 60%"，实际 CV = 52.1%（样本 SD）或 47.5%（总体 SD），v28 综合报告已正确标注 52%。

v33 状态：
- 手稿第 52 行：**"CV ≈ 52%"** ✅
- 独立验证：6 个 control 值 [12.16, 6.57, 6.34, 5.22, 8.15, 1.59]，Mean = 6.672, Sample SD = 3.474, **CV = 52.1%** ✅
- 与 Limitations #17 中 "coefficient of variation of ~52%" 一致 ✅

**评估**：事实性错误已更正，CV 值在全文一致。✅

### 2.2 m1: MANIFEST FDR 术语统一 — 修复 ✅

v32 问题：MANIFEST 第 72 行 "16/30 FDR-significant descriptive" 内部矛盾——"FDR-significant" 与正文 "formal FDR correction is not applicable" 冲突。

v33 状态：
- MANIFEST 第 53 行：**"FDR: No formal FDR applies (P-value floor saturation); signals interpreted as descriptive evidence"** ✅
- MANIFEST 第 54 行：**"Residual Model: 30 Strong, 16/30 P-value floor (descriptive), 14/30 non-significant"** ✅
- 全文搜索 "FDR-significant"：无匹配 ✅

**评估**：术语矛盾彻底消除。✅

### 2.3 m8: Abstract "statistically significant" → "permutation support" — 部分修复 (Minor 残留)

v32 问题：Abstract 第 11 行 "two statistically significant" 与正文 "descriptive evidence" / "FDR not applicable" 不一致。

v33 状态：
- Abstract（第 11 行）：**"two with permutation support"** ✅ 已修复
- **但 Introduction（第 18 行）仍使用 "both statistically significant"** ❌ 未修复

  > "including developmental origin heterogeneity and compartmentalized developmental specification **(both statistically significant)**, as well as colonization route boundaries and a postnatal migration event (exploratory, not statistically significant)"

- Introduction 的 "statistically significant" 与 Abstract 的 "permutation support" 以及正文 Limitations #16 的 "descriptive evidence rather than FDR-controlled discoveries" 三者不一致。

**评估**：Abstract 已修复，Introduction 遗留相同问题。Minor。

### 2.4 m9: k_n floor TT/NN 触发比例量化 (Limitations #20) — ❌ 未实施 (MANIFEST 虚假声明)

v32 问题：仅报告 TN（tumor-versus-normal）k_n floor 触发率（5/5 cancer types = 100%），TT 和 NN 比较的 floor 触发比例未报告。

v33 MANIFEST 声称：**"m9: k_n floor TT/NN quantified (in Limitations #20)"**

v33 手稿实际状态：
- 全文搜索 "Twentieth"：**无匹配** ❌
- Limitations 编号：#18（Eighteenth, m10）→ #19（Nineteenth, m11）→ #21（Twenty-first, m15），**#20 不存在**
- 手稿第 97 行仍仅报告 TN floor 触发：**"in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴"**
- 搜索 "tumor-tumor.*floor"、"NN.*floor"、"floor.*trigger"、"floor.*percent"、"floor.*proportion"：均无匹配
- Repro Guide 第 314 行仅有参数记录 "k_n floor (minimum) | 1e-4 | all analyses"，无 TT/NN 触发比例

**评估**：MANIFEST 声称修复但手稿中完全不存在。这是 MANIFEST 变更日志的准确性问题，影响审稿人对修复清单的信任。v32 Minor 5.4 未解决。Minor（但需警告 MANIFEST 准确性）。

### 2.5 m10: 单侧检验方向性限制 (Limitations #18) — 修复 ✅

v32 问题：主 permutation test 固定为上尾检验，无法检测功能约束（ω 显著低于 null），未在 Limitations 中声明。

v33 状态：
- 手稿第 101 行：**"Eighteenth, the one-sided permutation test (H1: ω_obs > ω_null) does not detect functional constraint (ω_obs < ω_null); users investigating bidirectional hypotheses should employ two-sided permutation tests, available via the direction parameter in the CKI package."** ✅
- SN 3.10（第 83 行）保留方向性假设论证 ✅
- Repro Guide 参数表第 327 行：**"One-sided test direction | omega_null >= omega_obs | Phase D (M-S1)"** ✅

**评估**：限制声明清晰，提供双向检验选项。✅

### 2.6 m11: P 值下限饱和率替代解释 (Limitations #19) — 修复 ✅

v32 问题：36.3% 信号达到 P 值下限，仅解释为 "strong evidence"，未讨论 null 分布可能过于狭窄的替代解释。

v33 状态：
- 手稿第 101 行：**"Nineteenth, the residual model permutation test (B = 10,000) reached the P-value floor (9.99 × 10⁻⁵) for 36.3% of signals. An alternative interpretation is that the null distribution, constructed by shuffling cell-type labels within region pairs, is narrower than the true null because cell types differ in global plasticity; a null that accounts for cell-type-specific baseline plasticity could reduce the saturation rate, though constructing such a null would require modeling the covariance structure of ω across cell types and region pairs."** ✅

**评估**：替代解释具体、技术性强，不仅提出可能性还指出解决方向。✅

### 2.7 m5: P 值精度 0.001 → 9.99×10⁻⁴ — 修复 ✅

v33 状态：
- 手稿第 41 行：**"minimum resolvable P-value is 9.99 × 10⁻⁴"** ✅
- SN 3.11（第 85 行）：**"minimum P = 9.99 × 10⁻⁴ (= 1/(B+1) = 1/1001)"** ✅
- 独立验证：1/(1000+1) = 0.000999 = 9.99×10⁻⁴ ✅

**评估**：精度标注统一且计算正确。✅

### 2.8 其他修复验证

| 编号 | 内容 | 状态 | 验证位置 |
|------|------|:----:|----------|
| m14 | "Strong candidate" → "threshold-passing candidates" (P≥0.76) | ✅ | 第 81、90、91、98 行 |
| m6 | 脑细胞类型 9 → 10（committed OPC 独立分类） | ✅ | 第 74 行：10 major non-neuronal classes |
| m16 | 补充图编号 Figure 8 → S8, Figure 9 → S9 | ✅ | 第 129、130 行 |
| m4 | requirements.txt 在 Repro Guide section 1 引用 | ✅ | Repro Guide 第 24 行 |
| m17 | "orthogonal" → "complementary" (2 处) | ⚠️ | **仍有 2 处残留**，见 §3.3 |

## 3. 新发现统计问题

### 3.1 (Minor) m9 MANIFEST 虚假声明 — Limitation #20 不存在

**位置**：MANIFEST 第 24 行声称 "m9: k_n floor TT/NN quantified (in Limitations #20)"；手稿 Limitations 编号 #19 → #21
**问题**：MANIFEST 声称 m9 已修复为 Limitation #20，但手稿中不存在 "Twentieth" 条目。Limitations 编号从 #19（Nineteenth）直接跳至 #21（Twenty-first），形成编号缺口。TT/NN 的 k_n floor 触发比例仍未量化。
**影响**：MANIFEST 是审稿人验证修复完成度的关键文件，虚假声明降低信任度。同时，TCGA ω 值异常偏高（BRCA Luminal A ω ≈ 344.5）主要由 k_n floor 驱动，完整量化 TT/NN/TN 三类比较的 floor 触发比例对解释 TCGA 结果至关重要。
**建议**：在手稿中补充 Limitation #20，量化 TT 和 NN 比较中 k_n floor 触发的比例（如 "X% of TT pairs and Y% of NN pairs also triggered the k_n floor"），或在 MANIFEST 中标注 m9 为 "deferred"。

### 3.2 (Minor) Introduction "both statistically significant" 与 Abstract 不一致

**位置**：手稿第 18 行（Introduction）vs. 第 11 行（Abstract）
**问题**：Abstract 已将 "two statistically significant" 改为 "two with permutation support"（m8），但 Introduction 第 18 行仍使用 **"both statistically significant"**：

> "developmental origin heterogeneity and compartmentalized developmental specification (both statistically significant)"

正文 Limitations #16 明确声明 "descriptive evidence rather than FDR-controlled discoveries"，Introduction 的 "statistically significant" 与此矛盾。
**影响**：Introduction 是审稿人评估论文框架的第一站，措辞不一致引起对统计严谨性的质疑。
**建议**：将第 18 行 "both statistically significant" 改为 "both with permutation support"，与 Abstract 一致。

### 3.3 (Minor) "orthogonal" 统计术语误用残留

**位置**：手稿第 77 行、第 116 行
**问题**：m17 声称将 "orthogonal" 改为 "complementary"（2 处），但手稿中仍有 2 处 "orthogonal"：

- 第 77 行："providing an **orthogonal** transcriptomic readout of migration history"
- 第 116 行（Figure 2 legend）："confirming ω captures **orthogonal** information"

从统计角度，"orthogonal" 意味着零相关（r = 0）。但手稿第 58 行明确报告 CKI ω 与标准指标的 Spearman r = **−0.38 至 −0.57**（负相关，非正交）。使用 "orthogonal" 与数据矛盾，构成统计术语误用。

**影响**：审稿人可能质疑作者对 "orthogonal" 概念的理解，特别是在统计学审稿中。
**建议**：将两处 "orthogonal" 改为 "complementary" 或 "distinct"，与 m17 修复声明一致。

### 3.4 (Minor) Limitations 编号缺口 (#20 缺失)

**位置**：手稿第 101 行
**问题**：Limitations 编号从 #19（Nineteenth）直接跳至 #21（Twenty-first），#20 不存在。
**影响**：编号不连续引起审稿人注意，可能怀疑内容遗漏。
**建议**：补充 #20（见 §3.1）或重新编号使序列连续。

### 3.5 (Minor) "Future directions" 段落被 Limitations 文本中断

**位置**：手稿第 101 行
**问题**：第 101 行文本结构异常——"Future directions" 句子被 Limitations #18–#21 中断：

> "Future directions include developmental biology (...), drug response profiling (...), aging research (tracking age-related baseline vs. **[Eighteenth...Nineteenth...Twenty-first...]** functional transcriptional drift), and evolutionary cell biology (...)"

"aging research (tracking age-related baseline vs." 与 "functional transcriptional drift)" 之间被 4 条 Limitations 隔开，形成语法断裂。
**影响**：影响可读性，审稿人可能认为排版错误。
**建议**：将 Limitations #18–#21 移至 "Future directions" 段落之前，或使用独立段落分隔。

### 3.6 (Minor) MANIFEST Bootstrap Status 表述需统一

**位置**：MANIFEST 第 46–49 行
**问题**：MANIFEST Bootstrap Status 使用混合表述：
- "8/15 significant" (mouse)
- "15/16 significant, P=9.99e-04" (human)
- "descriptive + SES" (TCGA)
- "10/10 significant, P<0.01, FDR<0.05" (brain)

"significant" 在 TCGA 行缺失但其他三行使用，且 brain 行同时标注 "FDR<0.05" 而 m1 已统一为 "P-value floor (descriptive)" 术语。虽然 MANIFEST 不是正文，但作为构建清单应与正文术语一致。
**建议**：统一为 "X/Y reached significance (BH-FDR < 0.05, B=1000)" 或 "descriptive only (B=1000)" 格式。

## 4. 统计方法逐一评估

### 4.1 Bootstrap P 值公式一致性 — 通过 ✅

公式 P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) 在以下 6 处完全一致：

| 位置 | 文件 | 行号 | B 值 |
|------|------|------|------|
| Methods | Manuscript | 26 | 1,000 |
| Statistical reporting | Manuscript | 41 | 1,000 |
| Results | Manuscript | 48 | 1,000 |
| SN 1.5 | Supplementary | 26 | 1,000 |
| SN 3.1 | Supplementary | 63–65 | 1,000 |
| Repro Guide 5.1 | Reproducibility | 148–150 | 1,000 |

残差模型使用反向公式 P = (count(null_residual ≤ observed) + 1)/(B + 1)（手稿第 35 行），B = 10,000，方向正确（检测异常低残差）。+1 pseudocount 在所有位置一致。✅

### 4.2 BH-FDR 校正策略 — 正确实施 ✅

**Bootstrap permutation（B = 1,000）**：
- BH-FDR 在每个数据集内单独应用 ✅
- 最小可解析 P 值 9.99×10⁻⁴ 低于每个数据集最显著检验的 BH 阈值：
  - brain: 5.0×10⁻³ (10 tests) → 9.99×10⁻⁴ < 5.0×10⁻³ ✅
  - human: 2.9×10⁻³ (17 tests) → 9.99×10⁻⁴ < 2.9×10⁻³ ✅
  - mouse: 3.3×10⁻³ (15 tests) → 9.99×10⁻⁴ < 3.3×10⁻³ ✅
- 检验数由 cell-type 数决定，而非 pair 数 ✅

**残差模型 permutation（B = 10,000）**：
- 36.3% 信号达到 P 值下限（9.99×10⁻⁵），BH-FDR 不可用 ✅
- 描述性 P 值方案：P-floor-reaching = "strong evidence"；P ≥ 0.50 = "little to no evidence" ✅
- 限制生物学解释于 30 个预定义 Strong 候选信号 ✅
- Limitations #16 明确声明 "formal Benjamini-Hochberg FDR correction is not applicable" ✅

### 4.3 单侧检验理由 — 充分，限制已声明 ✅

**理由充分性**：
- Methods 第 26 行：方向性假设理由清晰 ✅
- SN 3.10（第 83 行）：进一步论证两种方向对应不同生物学假设 ✅
- Limitations #18（m10 新增）：明确声明无法检测功能约束方向，提供 `direction` 参数选项 ✅

### 4.4 效应量报告 — 改进维持 ✅

- SES = (ω_obs − μ_null) / σ_null，明确为 "non-parametric descriptive statistic" ✅
- Cohen's d 仅作为反面对比 ✅
- 非正态性证据：Shapiro-Wilk / D'Agostino-Pearson all P < 10⁻¹⁵ ✅
- Bootstrap 95% CI（B = 10,000, pair-level resampling）覆盖所有关键 ω 估计 ✅
- CI 宽度与 pair 数反比：astrocytes [14.14, 14.58] (5,778 pairs) vs. Bergmann glia [1.95, 2.90] (21 pairs) ✅

### 4.5 校准因子深度分析 ✅

| 参数 | 手稿报告值 | 独立计算值 | 一致性 |
|------|-----------|-----------|:------:|
| Mean ω | 6.67 | 6.6717 | ✅ |
| Median ω | 6.46 | 6.455 | ✅ |
| Range | 1.59–12.16 | 1.59–12.16 | ✅ |
| CV | ≈ 52% | 52.1% (sample SD) | ✅ (m2 已修复) |
| 95% Bootstrap CI | [4.12, 9.33] | 正态近似 [3.89, 9.45] | ✅ (Bootstrap CI 合理) |
| 影响因子 (下限) | 1.62× | 6.672/4.12 = 1.619× | ✅ |
| 影响因子 (上限) | 0.71× | 6.672/9.33 = 0.715× | ✅ |
| MCSE (P=0.5, B=1000) | ≈ 0.016 | √(0.25/1000) = 0.0158 | ✅ |
| MCSE (P=0.001, B=1000) | ≈ 0.001 | √(0.001×0.999/1000) = 0.0010 | ✅ |

### 4.6 ω 分布特征化 — 全面 ✅

- Skewness: brain 2.22, mouse 0.98, human 0.73 ✅
- 正态性检验：Shapiro-Wilk (n ≤ 5,000) + D'Agostino-Pearson (n > 5,000), all P < 10⁻¹⁵ ✅
- Supplementary Figure S8 提供直方图和 Q-Q 图 ✅
- Limitations #19 新增 null 分布宽度替代解释 ✅

### 4.7 TCGA 统计处理 — 谨慎 ✅

- 配对分析 n = 2–5：明确声明 "descriptive statistics only, without P-values" ✅
- 最小 two-sided P ≈ 0.33 for n = 2（Mann-Whitney U, C(4,2) = 6 排列, 2/6 ≈ 0.333）✅
- 小样本亚组标注（Normal-like n = 7; Edmondson G4 n = 11）✅
- TCGA 探索性质声明：3 个替代解释（cell composition, peritumoral inflammation, RNA quality）✅
- k_n floor 机制说明：TN floor 触发 5/5 cancer types ✅（但 TT/NN 未量化，见 §3.1）

## 5. 问题汇总

| 编号 | 级别 | 位置 | 问题 | 状态 |
|------|------|------|------|:----:|
| 3.1 | Minor | MANIFEST 第 24 行 / 手稿 Limitations | m9 MANIFEST 声称修复但 Limitation #20 不存在；TT/NN floor 触发比例未量化 | 新发现 |
| 3.2 | Minor | 手稿第 18 行 | Introduction "both statistically significant" 与 Abstract "permutation support" 不一致 | v32 残留 |
| 3.3 | Minor | 手稿第 77、116 行 | "orthogonal" 术语误用（实际为负相关 r = −0.38 至 −0.57，非正交） | m17 声称修复但残留 |
| 3.4 | Minor | 手稿第 101 行 | Limitations 编号 #19 → #21，#20 缺失 | 新发现 |
| 3.5 | Minor | 手稿第 101 行 | "Future directions" 段落被 Limitations #18–#21 中断，语法断裂 | 新发现 |
| 3.6 | Minor | MANIFEST 第 46–49 行 | Bootstrap Status 表述格式不统一 | 新发现 |

## 6. 评分理由

### 6.1 评分分解

| 维度 | v32 评分 | v33 评分 | Δ | 评估依据 |
|------|---------|---------|---|---------|
| 统计方法严谨性 | 8.5 | 8.8 | +0.3 | P 值公式 6 处一致；BH-FDR 分层正确；单侧检验限制声明 (m10)；P-floor 替代解释 (m11)；CV 更正 (m2) |
| 效应量报告 | 8.5 | 8.7 | +0.2 | SES 非参数定位维持；Bootstrap CI 覆盖全面；m5 精度统一 |
| 校准因子可靠性 | 8.2 | 8.6 | +0.4 | CV 事实错误更正 (m2)；CI 5 处一致；影响因子验证正确；m9 未实施扣 0.1 |
| 数据集间比较 | 8.4 | 8.6 | +0.2 | TCGA 探索性定位维持；跨方案转移性承认；Introduction 措辞不一致扣 0.1；"orthogonal" 术语扣 0.05 |
| **加权综合** | **8.4** | **8.7** | **+0.3** | — |

### 6.2 评分变化理由

+0.3 的提升来自：
1. CV 事实性错误更正 60% → 52%（m2, +0.1）——消除 v32 遗留的数据准确性问题
2. MANIFEST FDR 术语统一（m1, +0.05）——消除 "FDR-significant descriptive" 矛盾
3. 单侧检验方向性限制声明（m10, Limitation #18, +0.05）——补全 v32 未覆盖的统计限制
4. P 值下限饱和率替代解释（m11, Limitation #19, +0.05）——提升 null 分布讨论深度
5. Abstract 措辞修复（m8, +0.05）——消除摘要与正文矛盾
6. P 值精度统一（m5, +0.05）——消除精度表述不一致

扣分项（阻止 9.0+ 的因素）：
1. m9 MANIFEST 虚假声明（−0.1）——声称修复但实际未实施，影响信任度
2. Introduction "statistically significant" 残留（−0.05）——m8 部分修复
3. "orthogonal" 统计术语误用残留（−0.05）——与数据矛盾

### 6.3 投稿准备度评估

**统计维度准备度**：~92%。无 Critical 或 Major 问题。6 项 Minor 问题预计 20 分钟内可全部修复。

**修复优先级**：
1. 补充 Limitation #20（k_n floor TT/NN 触发比例）或修正 MANIFEST m9 声明 — 5 分钟
2. 修正 Introduction 第 18 行 "statistically significant" → "with permutation support" — 1 分钟
3. 替换 "orthogonal" → "complementary"（第 77、116 行）— 1 分钟
4. 修复 Limitations 编号缺口（#19 → #21）— 与 #1 合并
5. 修复 "Future directions" 段落断裂 — 2 分钟
6. 统一 MANIFEST Bootstrap Status 表述 — 3 分钟

**推荐行动**：统计维度已达到 NAR 投稿标准。建议修复上述 6 项 Minor 问题后投稿。即使不修复也不构成 desk reject 或 major revision 的理由，但 m9 的 MANIFEST 虚假声明应在投稿前更正以避免审稿人质疑变更日志的可信度。

**Critical: 0, Major: 0, Minor: 6**
