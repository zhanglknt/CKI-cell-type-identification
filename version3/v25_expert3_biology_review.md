# 专家3：生物学与单细胞基因组学审稿报告 — CKI v25

**Reviewer**: E3 — 生物学与单细胞基因组学专家
**Date**: 2026-08-01
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v25 (20 files)
**Review baseline**: v22 expert score: 6.0/10

---

## 1. 总体评估

**v25 Score: 7.5/10** (v22: 6.0/10, **+1.5**)

v25 是自 v20 以来生物学维度改进最大的版本。两个生物学 Critical Issues（C4 HK 基因假设、C5 OPC 角色）均在概念层面得到修复，多个生物学 Major Issues（M8/M9/M10 TCGA confounders、M11 Brain migration、M20 aging 叙事）的修复质量超出预期。特别是 TCGA confounder 讨论和脑迁移叙事重构，已达到可接受发表的标准。

主要减分项：(1) C4 修复存在术语一致性问题——Discussion 已改为 "constrained baseline"，但 Results、Figure legends 和 Supplementary 仍残留 5+ 处 "neutral" 语言；(2) M16（脑 PMI 混杂）仅一句话带过，是所有生物学修复中最薄弱的；(3) 新发现 Table 1 数字不一致等小问题。

---

## 2. C4 修复验证：HK "constrained baseline"

### 修复评估：部分完成（7/10）

**核心修复（Discussion, line 98）— 充分且正确**：

> "housekeeping (HK) genes are under stabilizing selection that constrains their expression variance across conditions, making them a practical **constrained baseline** against which functional divergence can be measured."

这一表述在三个层面解决了 v22 提出的问题：
1. **明确了 HK 基因的生物学性质**：处于稳定化选择（stabilizing selection）下，而非"中性"
2. **承认了与 Ka/Ks 的根本区别**："Unlike Ka/Ks—where a shared mutation rate cancels mathematically, leaving a pure selection signal—CKI uses empirically defined HK genes as the baseline, **lacking a comparable mechanistic cancellation**"
3. **定位为启发式工具**："CKI is a heuristic index rather than a formal measure of selection"

**Discussion 中的进一步强化（line 100）**：
> "HK genes are defined empirically (high detection rate, low CV) rather than mechanistically (synonymous sites in Ka/Ks), and their expression variance could reflect regulatory constraints rather than pure neutral drift"

这一表述准确区分了"经验定义"与"机制定义"，并承认 HK 基因表达方差可能反映调控约束而非中性漂变。

**Introduction 中的声明（line 17）**：
> "Importantly, CKI ω is a heuristic index, not a formal measure of Darwinian selection; we use ω < 1, ω ≈ 1, and ω > 1 as convenient operational thresholds rather than claims about selection regimes"

**Supplementary Note 1.4 中的明确声明**：
> "The Ka/Ks analogy is structurally similar but mathematically non-equivalent. Key differences: (1) Ka/Ks operates on sequence alignments with explicit codon models, while CKI operates on continuous expression vectors; (2) the neutral reference in Ka/Ks has a mechanistic basis in the genetic code (synonymous changes are assumed neutral), whereas HK genes in CKI are empirically defined"

### 存在的问题：术语一致性不足

尽管 Discussion 中的核心修复正确且充分，但稿件其他部分仍多处残留 "neutral" 语言指代 k_n 或 HK 基因，与 Discussion 的 "constrained baseline" 定位产生矛盾：

| 位置 | 原文 | 问题 |
|------|------|------|
| Line 50 (Results) | "partitioning the expression data into **neutral** and identity gene sets" | 应改为 "constrained" 或 "baseline" |
| Line 73 (Results) | "if their **neutral baseline** k_n is low" | 应改为 "constrained baseline" |
| Line 121 (Fig 2 legend) | "confirming **neutral baseline** behavior" | 应改为 "constrained baseline behavior" |
| Line 122 (Fig 3 legend) | "k_n (**neutral rate**)" 及 "neutral (k_n) and functional (k_f) components" | 应改为 "constrained baseline rate" |
| Suppl. Note 1.2 | "k_n thus provides an internal baseline, heuristically analogous to Ks" | 未使用 "constrained" 语言 |

**评估**：Discussion 是审稿人最关注的位置，核心概念修复在此已完成。但术语不一致会给仔细阅读的审稿人留下"修改不彻底"的印象。这些残留修改的技术难度极低（搜索替换即可，约 30 分钟），但对稿件内部一致性的提升显著。

### 文献支撑评估

稿件引用了 Hounkpel et al. (2021) HRT Atlas v1.0（ref 4）作为 HK 基因来源，并在 Limitations 中提到 "sensitivity analysis showed that CKI results are robust to alternative HK definitions (using the lowest 10% variable genes as a constrained set yielded ω correlations r > 0.95)"。这一敏感性分析支持了 HK 基因集选择对结果的影响有限。

然而，稿件未引用关于 HK 基因稳定化选择的直接文献。建议引用以下类型的工作以加强 "constrained baseline" 的文献支撑：
- HK 基因表达稳定性受启动子结构、组蛋白修饰等调控约束的分子生物学证据
- HK 基因在进化中处于强纯化选择（purifying selection）下的群体遗传学证据

---

## 3. C5 修复验证：OPC "internal consistency check"

### 修复评估：充分且正确（8.5/10）

**Section header（line 83）**：从 "negative control validation" 改为 "OPCs: internal consistency check" ✅

**核心论述（line 84）**：
> "CKI detected 0 Strong signals among 5,671 OPC cross-region comparisons—a finding that provides a useful **orthogonal validation** of the multiplicative residual model. The model is not simply detecting high ω values or absolute transcriptional differences; it identifies cell-type/region-pair combinations where the observed functional divergence is substantially below what the cell type's global plasticity and the region pair's background divergence would jointly predict."

这一重写准确地将 OPC 的角色从"方法灵敏度的阴性对照验证"重新定位为"模型结构的内部一致性检验"。关键改进：

1. **明确解释了为什么 OPC 0 Strong 信号是有意义的**：模型不是简单检测高 ω 值，而是检测偏离预期的异常低值
2. **给出了 OPC 全局 ω（7.65）的生物学解释**："OPCs have a high global mean ω (7.65) because their transcriptional program includes both progenitor and differentiation states"
3. **解释了 52 个 Moderate 信号的意义**："likely reflect the balance between shared developmental origins and ongoing regional maturation"
4. **总结了 OPC 案例的方法学价值**："demonstrates that the residual model differentiates between broad baseline motility and specific transcriptional signatures of developmental history"

**Discussion 中的呼应（line 103）**：
> "OPCs—the most actively migrating cells in the adult CNS (13,17)—yielded 0 Strong signals among 5,671 comparisons, providing a notable orthogonal validation that the residual model specifically detects fixed developmental signatures rather than ongoing cell motility"

**Supplementary Fig S7 legend（line 133）**：
> "OPCs (0 Strong despite highest motility among the 10 non-neuronal classes) provide a key internal consistency check, supporting that the model detects developmental-origin signatures rather than general motility"

### 小缺口

v22 审稿中指出了一个数学结构问题：OPC 全局 ω（7.65）接近总均值（8.01），在乘法残差模型中 expected_ω = μ_ct × μ_pair / μ_grand，当 μ_ct ≈ μ_grand 时，expected_ω ≈ μ_pair，使得残差不容易极低。v25 的修复从生物学角度解释了 OPC 的高 ω，但没有从数学结构角度讨论 ω 接近均值时残差的预期行为。

这一缺口不是必须修复的——生物学解释已经充分支持论点——但补充一句数学说明会令论证更完整，例如："Additionally, because OPC global ω (7.65) is close to the grand mean (8.01), the multiplicative model's expected values are dominated by the region-pair term, making Strong-tier residuals structurally challenging to achieve—a mathematical property that reinforces rather than undermines the biological interpretation."

### 术语一致性注意

Section header 使用 "internal consistency check"，但正文使用 "orthogonal validation"。这两个概念有微妙差异：内部一致性检验验证的是模型结构，而正交验证暗示独立证据。建议统一使用 "internal consistency check"（与 header 和 Supplementary 一致），或在首次使用时明确定义两者关系。

---

## 4. 生物学 Major Issues 修复评估

### M8/M9/M10: TCGA confounders — 优秀（9/10）

这是 v25 生物学修复中质量最高的部分。

**Results（line 65）**——明确列出三种非排他性替代解释：
> "(i) shifts in tumor cell composition relative to normal tissue (tumor purity, stromal infiltration, immune cell infiltration); (ii) peritumoral inflammation and desmoplastic reactions that are shared across tumors; (iii) systematic RNA quality differences between tumor and normal specimens"

**Results（line 67）**——PAM50 增殖分数混杂讨论：
> "the PAM50 gradient may partly reflect proliferative fraction differences across subtypes (Basal-like tumors have the highest proliferation rates and the lowest ω), meaning that the observed convergence could be driven by proliferation programs overriding tissue-specific expression rather than by a shared transcriptional attractor per se"

这一讨论展示了良好的生物学洞察力——Basal-like 肿瘤的高增殖率可能导致组织特异性表达被增殖程序覆盖，而非真正的转录趋同。

**Discussion（line 102）**——重复并强化警告：
> "Single-cell or deconvolution-based validation would be needed to disentangle these alternatives."

**Supplementary Note 3.8**——专门的 "TCGA Exploratory Analysis Caveats" 章节，列出六条具体警告 ✅

**评估**：confounder 讨论在 Results、Discussion 和 Supplementary 三个层面保持一致，覆盖了细胞组成、瘤周炎症、RNA 质量和增殖分数四个维度。这是发表级别的修复。

### M11: Brain migration — 优秀（9/10）

v25 对脑迁移信号的重新框架是该版本最重要的生物学改进之一。

**关键改进**：

1. **Section titles 加入统计学限定**：
   - "Microglia: exploratory colonization wave hypotheses **(not statistically significant)**"
   - "Fibroblast: exploratory postnatal migration signal"

2. **统计 caveat 前置（line 92）**：
   > "Microglia contributed 10 Strong signals by the threshold criteria; **however, permutation testing revealed that none reached statistical significance (all P ≥ 0.76, q = 1.0)**. We therefore present the following biological interpretation as **an exploratory hypothesis rather than a statistically supported finding**."

3. **Narrative 后置警告**：
   > "given the lack of statistical significance, these patterns may reflect stochastic variation in the high-dimensional ω landscape rather than reproducible biological signals"

4. **Oligodendrocyte 重新解释为 "developmental origin rather than migration"**（line 85-86）：
   - 所有 10 个 Strong 信号均涉及 cortex/thalamus 或 brainstem-internal 配对
   - 与 Foerster et al. (2024) 的背侧/腹侧起源实验数据一致
   - 声明 "first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations without requiring lineage tracing"

5. **Astrocyte 解释为 "regional specialization with developmental origins"**（line 87-88）：
   - 6 个 Strong 信号集中在丘脑亚核和海马亚区
   - 与 compartmentalized astrogenesis 文献一致（Endo et al. 2024, Tcf4）

**评估**：迁移信号的生物学解释从"迁移证据"重构为"发育起源签名"，这是一个更准确、更保守的框架。统计非显著的信号（microglia、fibroblast、vascular）被明确标记为 exploratory，避免了过度解读。

### M16: Brain PMI — 薄弱（4/10）

**仅一句话（Limitation Fifth, line 104）**：
> "Fifth, the brain analysis uses post-mortem tissue; developmental time courses would provide stronger evidence for migration inference."

**不足**：
- 未具体讨论 PMI（死后间隔）作为混杂因素如何影响跨区域 ω 测量
- 未讨论不同脑区 PMI 差异可能导致 RNA 降解不均匀，从而产生虚假的区域间差异
- 未讨论细胞数量不对称（如 Bergmann glia n=21 vs astrocytes n=5,778）对 ω 估计精度的影响
- Siletti et al. 数据集的供体信息（年龄、PMI、死因）未被讨论为潜在混杂

**建议**：将这一句话扩展为 3-4 句，具体讨论：(1) PMI 对 RNA 质量的影响及其区域异质性；(2) 供体间变异对 ω 的潜在贡献；(3) 细胞数量不对称导致的统计功效差异。

### M20: Aging 叙事 — 良好（8.5/10）

v22 指出微胶质细胞定殖波叙事在统计 caveat 之前。v25 已修复：

1. **统计 caveat 在 narrative 之前**（line 92）✅
2. **"exploratory hypothesis" 明确标记** ✅
3. **Section title 包含 "(not statistically significant)"** ✅
4. **Post-narrative 警告**："these patterns may reflect stochastic variation" ✅

**评估**：叙事顺序问题已解决。读者现在首先了解到信号不显著，然后才看到生物学解释，最后再次被提醒谨慎解读。

---

## 5. 四数据集生物学结论自洽性

### 数据集间 ω 尺度差异

| 数据集 | ω 均值 | k_f 方案 | 生物学一致性 |
|--------|--------|----------|-------------|
| Mouse (Tabula Muris) | 6.67 (cal), 27.31 (full) | Global HVG 2,000 / per-pair 200 | 基线校准 ✅ |
| Human (Tabula Sapiens) | 14.23 | per-pair top-200 DE | same CT < different CT ✅ |
| TCGA (bulk) | ~100-344 | per-pair top-200 DE | 趋同信号 ✅ (但尺度异常高) |
| Brain (Siletti) | 8.01 | per-pair k_n + per-pair k_f | 梯度一致 ✅ |

**自洽性评估**：

1. **Mouse → Human**：稿件解释了不同 k_f 方案导致绝对 ω 不可比，但排名一致。此解释合理。✅
2. **Human → Brain**：Brain 使用 per-pair k_n（CV=97.35%），而 Human 使用 global k_n。稿件在 Methods 和 Supplementary Fig S11 中充分讨论了这一差异。✅
3. **Single-cell → TCGA**：TCGA 的 ω 值（BRCA Luminal A = 344.5）比单细胞数据高 20-50 倍。稿件仅提到 bulk RNA-seq 的 confounders，但**未讨论为什么 TCGA ω 值如此之高**。一个可能的解释是 k_n floor (1e-4)：如果 bulk RNA-seq 的 HK 基因 JS divergence 接近 floor，那么 ω = k_f / 1e-4 可能被人为放大。这一问题在 v22 审稿中已被提出，但在 v25 中仍未被讨论。⚠️

### 生物学梯度一致性

四个数据集内部的生物学梯度是一致的：
- Mouse: same CT (6.67) < same organ diff CT (43.19) < cross-organ
- Human: same CT cross-organ (15.83) < different CT same organ (24.87)
- TCGA: NN > TT (正常组织间差异大于肿瘤间差异)
- Brain: Bergmann glia (2.37) < astrocytes (14.36)

这些梯度与已知的细胞生物学知识一致。✅

---

## 6. 跨物种比较评估

**当前状态**：有限但足够

稿件在 Discussion 中提到：
> "Preliminary cross-species validation (Supplementary Fig. S2) showed that ω rankings are moderately conserved between mouse and human for shared cell types, though absolute ω values differ due to different computation schemes (per-pair for mouse, hybrid for human)."

Supplementary Fig S2 legend 描述了跨物种 ω 保守性散点图，但正文中未给出具体的 Spearman r 值。

**评估**：
- 跨物种比较是"初步的"（preliminary），这一诚实定位是恰当的
- 不同计算方案（mouse per-pair vs human hybrid）限制了绝对 ω 的可比性，稿件已承认
- 建议：在正文中报告跨物种 Spearman r 值和 P 值，使读者能评估保守程度
- 未与 SAMap/CACIMAR 等专门的跨物种方法进行定量比较——稿件解释了原因（"they address different questions"），这一解释合理

---

## 7. 新发现问题

### N1（Minor）: Table 1 细胞类型/配对数不一致

- **Manuscript（line 60）**："102 cell types, 5,151 pairs"
- **Table1-2.docx（line 3）**："99 cell types, 4,851 pairs"
- **Supplementary**：102 cell types, 5,151 pairs

独立的 Table1-2.docx 与 Manuscript 和 Supplementary 不一致。可能是旧版本表格未更新。需统一。

### N2（Minor）: "Neutral" 术语残留

如第 2 节详述，Discussion 已改为 "constrained baseline"，但 Results（line 50, 73）、Figure 2 legend（line 121）、Figure 3 legend（line 122）和 Supplementary Note 1.2 仍使用 "neutral" 语言指代 k_n/HK 基因。需全局替换。

### N3（Moderate）: TCGA ω 尺度异常未讨论

TCGA BRCA Luminal A 的 ω = 344.5 比脑数据平均 ω（8.01）高 43 倍。稿件讨论了 bulk RNA-seq 的 confounders，但未讨论：
- 为什么 TCGA ω 值如此之高
- k_n floor (1e-4) 是否在驱动这些高值
- 如果 k_n 接近 floor，ω 的生物学含义是否需要重新解读

建议在 TCGA Results 或 Discussion 中增加 1-2 句讨论 k_n 分布和 floor 触发频率。

### N4（Minor）: Limitation 编号错误

Limitations 段落中出现两个 "Seventh"：一个在长段落末尾（line 104），一个在独立段落（line 105）。需要修正编号。

### N5（Minor）: Cover Letter 仍使用 "selective" 语言

标题已从 "Selective Transcriptomic Remodeling" 改为 "Baseline-Normalized Transcriptomic Remodeling"，但 Cover Letter（line 17）仍说 "selective transcriptomic remodeling"。建议统一为 "baseline-normalized transcriptomic remodeling"。

### N6（Minor）: "Internal consistency check" vs "orthogonal validation" 术语混用

OPC section header 使用 "internal consistency check"，但正文使用 "orthogonal validation"。两者概念有微妙差异。建议统一术语，或在首次使用时明确定义关系。

### N7（Observation）: 脑分析四机制分类缺乏定量验证

稿件提出四种低 ω 机制（发育起源异质性、定殖路线边界、分区化发育特化、出生后迁移），但机制分配依赖于文献交叉验证而非定量标准。这一方法在当前框架下是合理的（因为残差模型只标识异常低的 ω，不直接推断机制），但建议明确声明机制分配是专家判断而非算法输出。

---

## 8. 生物学创新性评估

CKI 的核心生物学贡献——将转录组分歧分解为基线（HK 基因）和功能（identity 基因）两个分量——在概念水平上是有价值的。v25 的改进使这一贡献更加可信：

1. **"constrained baseline" 框架**比 "neutral baseline" 更准确地反映了 HK 基因的生物学性质
2. **OPC 内部一致性检验**正确展示了模型区分"广泛运动性"和"发育历史签名"的能力
3. **TCGA confounder 讨论**展示了对 bulk 数据局限性的诚实认知
4. **脑发育起源签名检测**——特别是首次无谱系示踪区分背侧/腹侧少突胶质细胞——是一个有意义的发现

---

## 9. 评分明细

| 项目 | v22 评分 | v25 评分 | Δ | 说明 |
|------|----------|----------|---|------|
| C4 (HK baseline) | 3/10 | 7/10 | +4 | 核心修复正确，但术语一致性不足 |
| C5 (OPC role) | 4/10 | 8.5/10 | +4.5 | 充分修复，小缺口可忽略 |
| M8/M9/M10 (TCGA) | 3/10 | 9/10 | +6 | 优秀的三层 confounder 讨论 |
| M11 (Brain migration) | 4/10 | 9/10 | +5 | 统计 caveat 前置 + 发育起源重构 |
| M16 (Brain PMI) | 3/10 | 4/10 | +1 | 仅一句话，实质性不足 |
| M20 (Aging narrative) | 4/10 | 8.5/10 | +4.5 | 叙事顺序已修复 |
| 四数据集自洽性 | 6/10 | 7/10 | +1 | TCGA ω 尺度异常未讨论 |
| 跨物种比较 | 6/10 | 6/10 | 0 | 无实质变化 |
| 新发现问题 | — | -1.5 | — | Table 1 不一致等 6 项 |

**综合评分：7.5/10**

---

## 10. 建议

### 发表前必须修复（P0）

1. **Table 1 数字统一**（N1）：确定 102/5,151 还是 99/4,851 正确，全局统一
2. **"Neutral" 术语清理**（N2）：全局搜索替换 "neutral" → "constrained"（指代 k_n/HK 时）
3. **Limitation 编号修正**（N4）：修复两个 "Seventh" 的问题

### 强烈建议修复（P1）

4. **TCGA ω 尺度讨论**（N3）：增加 1-2 句讨论 TCGA 中 k_n 分布和 floor 触发频率对高 ω 值的影响
5. **M16 PMI 扩展**：将单句扩展为 3-4 句，讨论 PMI 区域异质性和细胞数量不对称
6. **Cover Letter 统一**（N5）："selective" → "baseline-normalized"

### 建议改进（P2）

7. **跨物种 Spearman r 值**：在正文中报告具体数值
8. **OPC 术语统一**（N6）：统一 "internal consistency check" 和 "orthogonal validation"
9. **HK 基因稳定化选择文献**：引用直接支持 HK 基因受纯化选择的文献

---

## 11. 总结

v25 在生物学维度取得了实质性进步。C4 和 C5 的概念修复方向正确、论述充分，虽然术语一致性仍有不足。M8/M9/M10 和 M11 的修复质量超出预期，达到了发表标准。M16 是唯一仍存在实质性不足的生物学问题。

与 v22（6.0/10）相比，v25（7.5/10）的提升主要来自：
- C4/C5 从未修复到概念修复（+0.8）
- M8/M9/M10 从未讨论到三层 confounder 讨论（+0.4）
- M11 从未修复到统计 caveat 前置 + 发育起源重构（+0.3）

修复 P0 项后预计评分可达 8.0/10。所有 P0+P1 修复后预计 8.5/10。

**v25 评分：7.5/10** | v22: 6.0/10 | Δ: +1.5
