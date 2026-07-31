# CKI v16 统计学审稿报告

**审稿人**: 统计学专家
**审稿日期**: 2026-07-27
**版本**: v16

## 评分
- 统计学评分: 7.3/10 (v14: 6.8)
- 投稿准备度（统计维度）: 72%
- Critical: 5 | Major: 7 | Minor: 7

## v14→v16 改进确认

### 已修复的v14 Critical Issues

| v14编号 | 问题 | v16状态 | 评价 |
|---------|------|---------|------|
| C1 (多重检验校正缺失) | 31,764次比较无FDR | **部分修复** | Bootstrap范围已缩减至mouse pilot（15对）+校准对照（6个），共21次检验。但"descriptive statistics only"的声明与实际使用的推断检验（Kruskal-Wallis等）矛盾，见C3。TCGA的3个omnibus检验仍未校正。 |
| C2 (P值公式三方不一致) | 正文/补充/算法公式不同 | **部分修复** | 稿件和补充材料Note 1.5/3.2已统一为双侧+1伪计数公式。但可复现性指南仍使用完全不同的公式，见C1。 |
| C3 (校准实验n=6 + TOST移除) | n=6不足，TOST被删 | **部分修复** | TOST注释已恢复（line 47）。但正文仍声称P>0.05"confirms no functional divergence"，且ω=1.54被描述为"ω≈1"，见C5。 |

### 已修复的v14 Major Issues

| v14问题 | v16状态 | 评价 |
|---------|---------|------|
| Bootstrap范围 | **已修复** | 稿件明确限定B=500仅用于mouse pilot和校准对照；human/TCGA/brain不使用置换检验。 |
| CI概念纠正 (P0-10) | **已修复** | 补充材料Note 1.5和可复现性指南均明确区分"test critical values"与"confidence intervals for ω"。 |
| k_f选择偏差讨论 (P0-9) | **部分修复** | Discussion新增校准对照论证。但ω=1.54与"ω≈1"的表述自相矛盾，见C5。 |
| 术语统一 ("raw empirical P-values") | **部分修复** | 稿件和补充材料已更新，但可复现性指南仍使用"raw bootstrap P-values"（lines 165, 206）。 |

---

## Critical Issues

### C1. 可复现性指南中P值公式与稿件/补充材料完全不同

**位置**: `reproducibility_text.txt` line 161

稿件（lines 22, 37, 43）和补充材料（Note 1.5 line 26, Algorithm 1 line 47, Note 3.2 line 63）统一使用：

```
P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)), capped at 1.0
```

可复现性指南（line 161）使用：

```
p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)
```

**关键差异**:
1. **单侧 vs 双侧**: 指南公式无 `2 ×` 因子，为单侧检验
2. **检验统计量不同**: 指南公式以 |ω - 1| 为统计量（距离1的偏差），稿件以 ω_obs 在零分布中的位置为统计量
3. **无上限封顶**: 指南公式无 `capped at 1.0`

这两个公式检验的假设不同、检验方向不同、P值量级不同。在B=500时，对于同一组数据，两个公式可能给出完全不同的P值。这是v14 C2问题的残留——虽然稿件层面已统一，但可复现性指南作为代码验证文档仍未同步，严重影响可复现性。

**建议**: 将可复现性指南的P值公式统一为稿件版本，并明确标注双侧+1伪计数+封顶1.0。

### C2. 可复现性指南中Bootstrap B值和适用范围与稿件矛盾

**位置**: `reproducibility_text.txt` lines 155, 199, 206

| 位置 | B值/范围 | 与稿件一致性 |
|------|----------|-------------|
| 稿件 line 22, 37 | B=500，仅mouse pilot（15对）+ 校准对照（6个） | 基准 |
| 补充 Algorithm 1 line 42 | "default 1,000" | ❌ 应为500 |
| 补充 Note 3.2 line 63 | B=500，mouse pilot only | ✅ |
| 可复现性指南 line 155 | "B = 500 or 1000" | ❌ 暗示两种B值均在使用 |
| 可复现性指南 line 199 | "500 (mouse) or 1000 (human/TCGA/brain)" | ❌ 直接矛盾——稿件明确说human/TCGA/brain不使用bootstrap |
| 可复现性指南 line 206 | "all reported P-values are raw bootstrap P-values" | ❌ 如果human/TCGA/brain不使用bootstrap，此声明具有误导性 |

可复现性指南的checklist（line 199）要求验证者确认"1000 (human/TCGA/brain)"的bootstrap迭代数，但稿件明确声明这些分析不进行置换检验。这意味着按可复现性指南操作的验证者将尝试运行不存在的bootstrap分析，或认为稿件声明有误。

**建议**: 
1. 补充Algorithm 1的default B从1,000改为500
2. 可复现性指南删除所有关于human/TCGA/brain使用B=1000的表述
3. 可复现性指南line 206改为"All reported empirical P-values from bootstrap testing are raw (uncorrected)"
4. 术语"bootstrap P-values"统一为"empirical P-values"

### C3. "Descriptive statistics only"声明与实际使用的推断检验矛盾

**位置**: 稿件 lines 22, 37, 43; 补充材料 line 65

稿件多次声明human/TCGA/brain分析"used descriptive statistics (median, IQR, effect sizes) without permutation testing"。但稿件实际报告了以下推断检验：

| 分析 | 检验方法 | P值 | 位置 |
|------|----------|-----|------|
| Tabula Sapiens相关性 | Spearman correlation | all P < 0.001 | line 52 |
| 同器官 vs 跨器官 | Mann-Whitney U | P < 0.001 | line 55 |
| LIHC Edmondson grade | Jonckheere-Terpstra trend | P < 0.001 | line 60 |
| BRCA PAM50 subtypes | Kruskal-Wallis | P = 0.0002 | line 60 |
| LUAD mutations | Kruskal-Wallis | P = 0.017 | line 60 |
| Paired vs. unpaired | Mann-Whitney U | P = 0.024 (LIHC) | line 59 |

Kruskal-Wallis、Jonckheere-Terpstra、Mann-Whitney U、Spearman相关均为**推断检验**（inferential tests），不是描述性统计。稿件在line 37甚至自相矛盾：先说"descriptive statistics only"，同一段又说"Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05"。

这一概念混淆严重影响方法学透明度。读者无法判断哪些分析是纯描述性的、哪些使用了推断检验。

**建议**: 
1. 将"descriptive statistics only"改为"standard non-parametric tests without permutation testing"
2. 明确区分：bootstrap置换检验（仅mouse pilot）→ 标准非参数检验（TCGA分层分析）→ 纯描述性统计（brain atlas的ω梯度描述）
3. 补充材料Note 3.3应相应更新

### C4. 临床分层分析样本量在稿件与可复现性指南之间存在重大差异

**位置**: 稿件 lines 26, 60 vs 可复现性指南 line 126-128

| 分析 | 稿件样本量 | 可复现性指南样本量 | 差异 |
|------|-----------|-------------------|------|
| LIHC Edmondson | G1(39), G2(133), G3(105), G4(11); total=288 | G1(12), G2(118), G3(127), G4(32); total=289 | 各分层人数完全不同 |
| BRCA PAM50 | LumA(224), LumB(123), HER2(55), Basal(97), Normal(7); total=506 | Basal(181), HER2(78), LumA(562), LumB(207), Normal(36); total=1064 | total 506 vs 1064（差距2倍+） |
| LUAD mutations | EGFR(61), KRAS(120), WT(311); total=492 | EGFR(97), KRAS(152), WT(283); total=532 | 各组人数显著不同 |

BRCA PAM50的差异最为严重：可复现性指南的total (1064)甚至超过了稿件报告的BRCA肿瘤样本总数(1032)。这意味着两份文档描述的是不同的数据处理流程或不同的过滤标准。

由于Kruskal-Wallis和Jonckheere-Terpstra检验的P值直接依赖于样本量，不同样本量可能产生不同结论。验证者无法确定应使用哪组数据复现结果。

**建议**: 核实实际分析数据，统一稿件与可复现性指南的样本量，并解释差异来源（如不同的QC过滤标准、不同的PAM50基因匹配率等）。

### C5. 校准实验统计学解释仍不正确——P > 0.05 ≠ "confirms no functional divergence"

**位置**: 稿件 lines 47, 97

稿件line 47表述：
> "This confirms that CKI recognizes biologically equivalent cell populations as having no functional divergence."

稿件line 97表述：
> "the calibration controls (random split of the same population, mean ω = 1.54) demonstrate that HVG selection alone does not inflate ω—when two populations are biologically equivalent, k_f and k_n are comparably small, **yielding ω ≈ 1**."

**问题**:
1. **P > 0.05不确认零假设**: 6个对照比较均P > 0.05仅表示未能在α=0.05水平拒绝零假设，不等于"确认无功能分歧"。这是统计学基本原理（absence of evidence ≠ evidence of absence）。虽然TOST注释已添加，但正文主句仍使用"confirms"一词，TOST注释仅作为脚注式的局限性说明，未修正主结论的措辞。

2. **ω = 1.54 ≠ "ω ≈ 1"**: 均值1.54比期望值1.0高54%，范围为1.09–2.10。将1.54描述为"ω ≈ 1"在定量上不准确。如果HVG选择不导致膨胀，期望ω应非常接近1.0。1.54的偏差可能反映：(a) HVG选择确实存在轻度膨胀效应；(b) softmax归一化引入系统性偏差；(c) 小样本(n=6)随机波动。稿件未讨论这些替代解释。

3. **k_f选择偏差论证逻辑自相矛盾**: 稿件用ω=1.54来论证"HVG选择不膨胀ω"，但同时声称"yielding ω ≈ 1"。如果ω确实≈1，那1.54的偏差需要解释；如果1.54是可接受的基线，那"≈1"的表述就是错误的。

4. **缺乏不确定性量化**: n=6的均值1.54没有报告95% CI。粗略估计（均值1.54，SD≈0.38，n=6），95% CI约为[1.16, 1.92]，不包含1.0。这意味着虽然置换检验未达统计显著（可能因B=500功效不足），但均值1.54的置信区间实际上与1.0有统计意义上的偏离。

**建议**:
1. 将"confirms"改为"is consistent with"
2. 将"yielding ω ≈ 1"改为"yielding ω = 1.54 (empirical baseline)"
3. 报告校准ω的95% CI
4. 讨论1.54偏离1.0的可能原因
5. 明确区分"统计显著性"和"等价性"——TOST注释应提升为正文讨论，而非脚注

---

## Major Issues

### M1. "Cohen's d"标注不准确——实际为置换z-score

**位置**: 稿件 lines 22, 37, 43; 补充材料 line 63, Algorithm 1 line 48; 可复现性指南 line 162

稿件定义效应量公式为：

```
Standardized effect size = (ω_obs - mean(ω_null)) / sd(ω_null)
```

并将其称为"Cohen's d"（line 37: "Effect sizes are reported as Cohen's d"）。

**问题**: Cohen's d的经典定义是两组均值差除以合并标准差：d = (μ₁ - μ₂) / σ_pooled。而稿件公式计算的是观测统计量相对于零分布的标准化偏差（permutation z-score）。两者在概念上不同：
- Cohen's d衡量两组之间的效应大小
- 置换z-score衡量观测值在零假设下的极端程度

虽然在某些情况下两者数值接近，但将置换z-score标注为"Cohen's d"会引起方法论混淆，特别是在d > 0.8的"大效应"阈值引用上——该阈值是针对Cohen's d制定的，不直接适用于置换z-score。

**建议**: 将术语改为"standardized effect size (permutation z-score)"或" standardized test statistic"，保留Cohen's d用于真正的两组比较（如TCGA的NN vs. TT）。

### M2. 效应量、AUC和相关系数均缺少置信区间

**位置**: 全文

以下关键统计量均未报告95% CI：

| 统计量 | 位置 | 当前报告 | 缺失 |
|--------|------|----------|------|
| CKI vs. 标准度量Spearman相关 | line 52 | r = -0.38 to -0.57, P < 0.001 | 95% CI for r |
| 分类AUC | Table 1, line 55 | AUC = 0.716, 0.690, 0.887等 | 95% CI for AUC |
| 校准ω均值 | line 47 | mean = 1.54 | 95% CI |
| TCGA NN/TT比值 | line 58 | median ratios per cancer | 95% CI |
| Cohen's d / 置换z-score | lines 22, 63 | d values reported | 95% CI (bootstrap) |

v14审稿已指出AUC 95% CI在v12存在但在v14被移除。v16仍未恢复。对于NAR投稿，效应量的不确定性量化是基本要求。

**建议**: 
1. 所有AUC报告95% CI（可用DeLong方法或bootstrap）
2. Spearman相关报告95% CI（Fisher z变换或bootstrap）
3. 校准ω均值报告95% CI
4. 置换z-score报告bootstrap 95% CI

### M3. TCGA LUAD突变分析P=0.017在多重检验校正后不显著

**位置**: 稿件 line 60

TCGA分层分析进行了3组omnibus检验：
- LIHC Edmondson grade: Jonckheere-Terpstra, P < 0.001 ✓
- BRCA PAM50 subtypes: Kruskal-Wallis, P = 0.0002 ✓
- LUAD mutations: Kruskal-Wallis, P = 0.017

Bonferroni校正：α = 0.05/3 = 0.0167。LUAD突变P = 0.017 > 0.0167，在校正后不显著。

此外，paired vs. unpaired比较进行了5次Mann-Whitney检验（5种癌症类型），仅LIHC显著（P = 0.024）。Bonferroni校正：α = 0.05/5 = 0.01，P = 0.024不显著。

稿件声明"Omnibus tests use P < 0.05 without additional correction"（line 37）。对于探索性研究，这一声明在概念上可以接受，但稿件在Results中对P = 0.017的LUAD结果进行了实质性生物学解读（line 60: "EGFR-mutant and KRAS-mutant tumors exhibiting higher ω than wild-type tumors"），已超出纯探索性范畴。

**建议**: 
1. 对3个omnibus检验报告Bonferroni校正后的阈值
2. 对LUAD P = 0.017标注"marginally significant, not surviving Bonferroni correction (α = 0.0167)"
3. 对5个paired vs. unpaired检验同样处理
4. 或声明这些为探索性分析，结论需验证

### M4. 乘法残差模型阈值缺乏敏感性分析和正式零分布

**位置**: 稿件 lines 31, 74; 可复现性指南 lines 143-150

Strong候选信号的筛选标准为：residual < 0.3, ω < 15, lowest ω in pair, pair median ω > 20。这些阈值的选择缺乏统计学依据：
1. 为什么residual阈值是0.3而非0.25或0.35？
2. 为什么ω < 15而非10或20？
3. 为什么pair median ω > 20？

在31,764次比较中，30个Strong候选（0.09%）被广泛生物学解读。但缺少：
- 阈值变化对候选数量的敏感性分析（如residual < 0.2/0.25/0.3/0.35各有多少候选）
- 残差的经验零分布（如果乘法模型成立，残差应近似以1为中心分布——实际分布如何？）
- 在零假设下的期望假阳性数估计

OPC阴性对照（0/5,671 Strong signals）是有力的特异性证据，但单一阴性对照不足以替代正式的统计功效分析。

**建议**: 
1. 补充残差分布图（已有Supplementary Fig. S7a，但需更详细的分位数分析）
2. 进行阈值敏感性分析（表格展示不同阈值下的候选数量）
3. 通过置换或模拟估计零假设下的期望候选数
4. 在Methods中讨论阈值选择的依据

### M5. HK基因选择方法在稿件与可复现性指南之间存在矛盾

**位置**: 稿件 lines 19, 46 vs 可复现性指南 lines 48-76

| 文档 | HK基因选择方法 |
|------|---------------|
| 稿件 line 19 | "auto-detected from data using a combined criterion: detection rate > 0.9 and CV below the 30th percentile" + "HRT Atlas v1.0 consensus set is optionally used as supplementary enhancement" |
| 稿件 line 46 | "Housekeeping genes were auto-detected from data... supplemented with 1,130 human-mouse conserved reference HK genes" |
| 可复现性指南 lines 48-50 | "housekeeping (HK) genes were **NOT** auto-detected. Instead, pre-specified HK gene lists were loaded from the HRT Atlas reference file" |
| 可复现性指南 lines 71-76 | "This auto-detection was **NOT** used in the current analyses (the pre-specified list approach was preferred for reproducibility)" |

稿件描述的方法（自动检测+可选HRT Atlas增强）与实际执行的方法（仅使用HRT Atlas预定义列表）不同。这是一个方法描述不准确的问题，也影响可复现性——按稿件方法操作的读者将使用自动检测，而非实际使用的预定义列表。

**建议**: 
1. 稿件应如实描述实际使用的方法："HK genes were loaded from the HRT Atlas v1.0 reference file (1,130 human-mouse conserved genes)"
2. 将自动检测描述为"available as an option for species without curated HK lists"
3. 可复现性指南已正确描述，无需修改

### M6. 脑图谱分析归一化流程在稿件与可复现性指南之间存在矛盾

**位置**: 稿件 line 27 vs 可复现性指南 line 138

| 文档 | 归一化流程 |
|------|-----------|
| 稿件 line 27 | "Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation. Pseudobulk vectors were computed as the mean log-normalized expression per group." |
| 可复现性指南 line 138 | "Build pseudobulk vectors: raw count means per (ct, region) group. Normalize each pseudobulk: softmax(log1p(pb / sum(pb) * 1e4 + 1e-9))." |

关键差异：
- **稿件**: 细胞级归一化（normalize_total → log1p）→ 计算pseudobulk（均值）→ softmax → JS divergence
- **可复现性指南**: 原始计数pseudobulk（均值）→ log1p + 归一化 → softmax → JS divergence

由于 log(mean) ≠ mean(log)，两种流程产生不同的pseudobulk向量，进而产生不同的ω值。其他数据集（Tabula Muris, Tabula Sapiens）在两份文档中描述一致（均为细胞级归一化），仅脑图谱分析存在差异。

**建议**: 核实实际代码使用的归一化流程，统一两份文档的描述。如果脑图谱确实使用了不同的归一化策略，需在Methods中解释原因。

### M7. 可复现性指南术语未更新——"bootstrap P-values"应为"empirical P-values"

**位置**: 可复现性指南 lines 165, 206

v15→v16的修改要求将"raw Bootstrap P-values"统一为"raw empirical P-values"。稿件和补充材料已完成此更新，但可复现性指南仍使用旧术语：
- Line 165: "all reported P-values and significance thresholds use raw (uncorrected) **bootstrap** P-values"
- Line 206: "all reported P-values are raw **bootstrap** P-values"

**建议**: 将可复现性指南中所有"bootstrap P-values"替换为"empirical P-values"。

---

## Minor Issues

### m1. Algorithm 1默认B值错误

**位置**: 补充材料 Algorithm 1, line 42

Algorithm 1伪代码写"for b = 1 to B (default 1,000)"，但实际mouse pilot使用B=500。应改为"default 500 (mouse pilot)"或移除默认值标注。

### m2. P值封顶（capped at 1.0）在Algorithm 1和可复现性指南中缺失

**位置**: 补充材料 Algorithm 1 line 47; 可复现性指南 line 161

稿件和Note 1.5/3.2均注明P值"capped at 1.0"（双侧检验中min函数可能产生P > 1.0的情况需要封顶），但Algorithm 1伪代码和可复现性指南的公式均未提及封顶。应统一添加。

### m3. 校准实验缺少ω均值的95% CI

**位置**: 稿件 line 47

mean ω = 1.54 (median 1.42, range 1.09–2.10, n=6) 未报告95% CI。基于n=6的t分布，粗略95% CI约为[1.16, 1.92]。报告CI有助于读者判断1.54与1.0的偏离是否具有统计意义。

### m4. 可复现性指南零假设表述不精确

**位置**: 可复现性指南 line 153

指南写"H0: omega = 1 (no selective remodeling)"，但置换检验的零假设是**标签可交换性**（exchangeability），即两组细胞来自同一分布。ω = 1不是零假设本身，而是零假设下的期望值。这一区分对统计推断的解读有影响。

### m5. AUC 95% CI自v12移除后仍未恢复

v12版本报告了AUC的95% CI，v14移除，v16未恢复。Table 1的5个度量AUC值均缺少CI。对于NAR投稿，分类性能的不确定性量化应作为标准报告内容。

### m6. 脑图谱细胞类型数量在Methods和Results之间不一致

**位置**: 稿件 line 27 (Methods) vs line 68 (Results)

Methods列出9个细胞类别（choroid plexus列为第9个），Results描述10个类别但未提及choroid plexus的ω值。应统一为10个类别并在Results中报告所有10个类别的ω值，或解释choroid plexus为何未纳入梯度分析。

### m7. Paired/unpaired比值范围0.99–3.25与"higher in four of five"表述容易引起误解

**位置**: 稿件 line 59

"paired tumor-normal comparisons yielded higher ω than unpaired comparisons in four of five cancer types (paired/unpaired ratio = 0.99–3.25)"——0.99 < 1意味着该癌症类型paired < unpaired。虽然"four of five"的表述逻辑正确（4个ratio > 1，1个ratio = 0.99），但将0.99与"higher"放在同一句中容易引起误解。建议分别列出5个癌症类型各自的ratio值。

---

## 优点

1. **Bootstrap范围缩减策略正确**: 将B=500置换检验限定于mouse pilot（15对）和校准对照（6个），避免在大规模比较中滥用计算昂贵的置换检验，是合理的策略选择。对human/TCGA/brain使用标准非参数检验或描述性统计，在探索性研究框架下可以接受。

2. **CI概念纠正到位**: 补充材料Note 1.5明确区分"permutation-based test critical values"与"confidence intervals for ω itself"，消除了v14中将零分布分位数误称为CI的概念错误。

3. **TOST注释恢复**: 在校准实验中恢复TOST等价检验的讨论（line 47），承认n=6不足以进行正式等价检验，体现了统计诚实性。

4. **k_f选择偏差讨论**: Discussion（line 97）新增用校准对照论证HVG选择不膨胀ω的讨论，虽然论证逻辑存在C5中指出的问题，但方向正确。

5. **效应量报告意识**: 稿件在所有显著性声明旁报告效应量（Cohen's d、Spearman r），虽然术语标注有误（M1），但"统计显著性≠生物学意义"的意识值得肯定。

6. **OPC阴性对照设计**: 使用OPC（成人CNS中最活跃迁移的细胞）作为阴性对照来验证乘法残差模型的特异性，实验设计思路优秀。0/5,671 Strong signals的结果为模型的假阳性控制提供了有力证据。

7. **术语统一部分完成**: "raw empirical P-values"在稿件和补充材料中已统一（虽然可复现性指南滞后，见M7）。

---

## 总体评价

v16在统计学维度相较v14取得了**渐进式但实质性的进步**（6.8 → 7.3分）。核心改善在于概念纠正：Bootstrap范围从"全文使用"缩减至"仅mouse pilot"，CI概念从"零分布分位数=CI"纠正为"test critical values ≠ confidence intervals"，P值公式在稿件和补充材料层面实现了统一。这些修正使稿件的方法学描述更接近统计学的规范表述。

然而，v16存在一个系统性的修复传播问题：**多项v15→v16修复仅在稿件和补充材料中完成，未同步至可复现性指南**。最突出的表现是C1（P值公式完全不同）和C2（B值和bootstrap范围矛盾）。可复现性指南作为代码验证文档，其统计公式不一致直接影响验证者能否复现结果。此外，C3（"descriptive statistics only"声明与实际推断检验矛盾）和C4（临床分层样本量差异）是新发现的问题，反映出稿件各部分之间的协调仍不充分。

最令人担忧的统计学问题仍是C5：校准实验ω = 1.54被描述为"ω ≈ 1"且声称"confirms no functional divergence"。P > 0.05不确认零假设是统计学的基本原则——虽然TOST注释已添加，但正文主结论的措辞未相应修正。考虑到1.54比期望值1.0高54%，且粗略95% CI [1.16, 1.92]不包含1.0，这一偏差需要正面讨论而非回避。校准实验是CKI方法有效性的基石，其统计学解释必须严谨。

**投稿建议**: 修复C1-C5（预计4-6小时）后，统计学维度可达NAR投稿门槛（7.5+/10）。C1-C2仅需同步可复现性指南，C3需修订措辞，C4需核实数据，C5需调整校准实验的结论表述。M1-M7可在Revision中根据审稿人反馈选择性处理。
