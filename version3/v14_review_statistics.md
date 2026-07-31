# 统计学审稿报告 — CKI v14 NAR Submission

## 评分：6.8 / 10（v12: 5.8/10）

---

## v12→v14 修复评估

### 已充分修复的问题

**1. JS 对数底统一（v12 C3 → v14 已修复）** ✅

v12 中主文称"natural logarithm"而补充材料称"base-2 logarithm"，存在直接矛盾。v14 已彻底统一：
- 主文 P020 明确声明："JS divergence uses the base-2 logarithm (range [0, 1])."
- 补充材料 Note 1.1（P018）一致使用 "D(p||q) = Σ p_i log2(p_i/q_i)"，并正确声明 [0, 1] 界值。
- 界值声明现在数学上正确：base-2 JS divergence ∈ [0, 1]。

**评估**：此问题已充分修复。对数底统一后，k_n 和 k_f 的绝对值具有明确的统计含义（占最大分歧的比例），ω = k_f/k_n 的比值解释也更具一致性。

**2. Bootstrap B 值提升（v12 C4 → v14 部分修复）** ⚠️

v12 所有 bootstrap 分析均使用 B = 500；v14 将 primary analyses 提升至 B = 1,000，calibration 保持 B = 500。
- P022："B = 1,000 for primary analyses, B = 500 for calibration"
- P037（Statistical reporting）一致声明
- B = 1,000 时，最小可达 P 值为 1/1001 ≈ 0.000999，理论上可支持 P < 0.001 的声明

**评估**：部分修复。Primary analyses 的 B 值已达到现代探索性分析的最低推荐值。但 calibration 实验仍使用 B = 500，考虑到校准实验是整个方法体系的基石，B = 500 仍然偏低。此外，v12 提到的 P023 重复表述（"B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"）在 v14 中已通过重写消除。

**3. Bootstrap 检验统计量修改（v12 C2 → v14 部分修复）** ⚠️

v12 使用 |ω - 1| 作为检验统计量，与经验零假设中心 ~1.54 矛盾。v14 改为百分位法：
- P022（Methods）："P = 2 × min(proportion of ω_null ≥ ω_obs, proportion of ω_null ≤ ω_obs)"
- 伪代码 P047："P <- 2 * min(pct_above, pct_below) // percentile-based two-sided"

百分位法不假设特定中心值，直接将 ω_obs 与整个 ω_null 分布比较，理论上不受 ω_null 中心偏移影响。

**评估**：方向正确，但存在严重的不一致问题（详见下方 Critical Issue C2）。此外，v14 Discussion（P091）明确承认"ω = 1 does not carry population-genetic meaning of neutrality; rather, it is an empirically calibrated operational baseline (mean observational ω = 1.54)"，这是重要的概念澄清。

**4. FDR 声明透明度（v12 C1 → v14 部分改善但未解决）** ⚠️

v14 在多处明确声明不进行多重检验校正：
- P037："All reported P-values are raw bootstrap P-values without multiple testing correction."
- P043："All reported P-values are raw bootstrap P-values without multiple testing correction."
- 补充材料 Note 3.3："Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses"

**评估**：透明度显著提升，从 v12 的"声明但未执行"到 v14 的"明确声明不执行"。但问题本身未解决——31,764 次脑图谱比较和 4,851 次人类比较仍无任何多重检验校正。"NOT systematically applied"的声明是否可被审稿人接受，取决于个体审稿人的标准，但从统计学严谨性角度，这仍然是一个需要解决的问题（详见 C1）。

**5. 归一化参数统一** ✅

v14 统一使用 softmax 归一化（P020, P041, 补充材料 Note 1.2），消除了 v12 中可能存在的归一化不一致。

**6. ω = 1.54 的概念澄清** ✅（新改进）

v14 Discussion（P091）新增重要澄清："CKI lacks an analogous cancellation mechanism. Its ω = 1 does not carry population-genetic meaning of neutrality; rather, it is an empirically calibrated operational baseline (mean observational ω = 1.54 for equivalent populations)." 这比 v12 更诚实地承认了 ω = 1 的非中性含义。

---

## 总体评价

CKI v14 相比 v12 在统计严谨性方面有实质性进步，评分从 5.8 提升至 6.8。最显著的改善包括：(1) JS 对数底矛盾的彻底解决，使 k_n 和 k_f 的绝对值具有一致的数学含义；(2) Bootstrap B 值从 500 提升至 1,000（primary analyses），提高了零分布估计精度；(3) 检验统计量从有偏的 |ω - 1| 改为百分位法，消除了与经验零假设中心的逻辑矛盾；(4) 对 ω = 1.54 作为经验基线的概念澄清，使方法的理论定位更加诚实。这些修复表明作者认真对待了 v12 审稿意见，并在关键统计问题上做出了有意义的改进。

然而，v14 仍存在若干需要在发表前解决的统计学问题。最突出的是：(1) 多重检验校正的持续缺失——虽然声明更加透明，但 31,764 次比较中筛选 30 个 Strong candidate 并逐一赋予生物学解释，已超出探索性分析范畴，需要正式的多重检验控制；(2) Bootstrap P 值公式在主文、Results、补充材料和伪代码之间存在三方不一致（two-sided vs. one-sided），这是一个直接影响统计推断有效性的基础性错误；(3) 校准实验仍仅基于 n = 6，且 v14 移除了 v12 中的 TOST 等价检验但未替代以任何等效验证；(4) 效应量报告仍未提供 95% CI（Cohen's d、Spearman r 均缺失），且 AUC 的 95% CI 相比 v12 反而被移除，构成退步。

此外，v14 引入了一些新的编辑性错误（如 P020 中 softmax 归一化句子的重复）和新的不一致（Figure 1c 标注 B = 500 与主文 B = 1,000 的矛盾）。这些问题虽不影响核心科学内容，但影响稿件的专业性印象。建议作者进行一轮聚焦的修订，重点解决下方列出的 Critical 和 Major Issues。

---

## 关键问题（Critical Issues）

### C1. 多重检验校正持续缺失，"NOT systematically applied"声明不充分

v14 在 31,764 次脑图谱比较和 4,851 次人类比较中仍不进行 FDR 校正。虽然补充材料 Note 3.3 明确声明"Benjamini-Hochberg FDR correction is NOT systematically applied"，但这一声明并不能替代实际的统计校正。

**核心问题**：

1. **脑图谱分析的 31,764 次比较**：作者通过乘法残差模型筛选出 30 个 Strong candidate（0.09%），并对其逐一进行文献交叉验证和生物学机制赋值（DO、CR、DS、PM）。这种对个别信号的深度解读已构成确认性分析（confirmatory analysis），而非纯探索性分析。在确认性框架下，必须控制 family-wise error rate 或 FDR。

2. **期望假阳性数未计算**：在 31,764 次比较中，即使 Strong 的联合条件（residual < 0.3 AND ω < 15 AND lowest ω in pair AND pair median ω > 20）在零假设下的单次假阳性率仅为 0.01%，期望假阳性数仍为 31,764 × 0.0001 ≈ 3.2。即，在完全无信号的情况下，仍期望约 3 个假阳性。观察到的 30 个 Strong candidate 虽远超期望，但作者未提供这一定量对比。

3. **TCGA 多临床变量检验**：同一数据集内检验了 PAM50 亚型（KW, P = 0.0002）、Edmondson 分级（JT, P < 0.001）和 LUAD 突变状态（KW, P = 0.017）三个临床变量。仅 3 个检验时，Bonferroni 校正阈值 α = 0.05/3 = 0.0167，LUAD 突变（P = 0.017）在 Bonferroni 校正后不再显著。但稿件未进行此校正。

4. **Tabula Sapiens 4,851 对比较**：五个度量的两两 Spearman 相关（10 对比较）均报告 P < 0.001。虽然 n = 4,851 使得即使微弱相关也统计显著，但正是这种情况（大样本下统计显著 vs. 实际意义有限）更需要区分统计显著性与效应量大小。

5. **"NOT systematically applied"的可接受性**：这一声明本质上是"我们意识到了问题但选择不解决"。对于 NAR 级别的期刊，这种处理方式在以下条件下可能被接受：(a) 分析明确标注为探索性；(b) 不对个别比较的显著性做强声明；(c) 提供效应量使读者自行判断。但 v14 对 30 个 Strong candidate 的深度生物学解读已超出这些条件。

**建议**：
- 对脑图谱 31,764 次比较，至少应用 Benjamini-Hochberg FDR 校正，报告 30 个 Strong candidate 在 FDR < 0.05 下的存活数量。如果部分候选在 FDR 校正后不再显著，应如实报告。
- 补充排列检验：对 region label 进行置换（B ≥ 1,000），计算每个 (cell_type, region_pair) 组合的排列 P 值，报告 FDR 校正后的 Strong candidate 数量。
- 计算 Strong 联合条件在零假设下的期望假阳性数，与观察到的 30 进行定量对比。
- 对 TCGA 三个临床变量检验，应用 Bonferroni 校正（α = 0.0167），报告校正后哪些结果仍然显著。
- 对 Tabula Sapiens 的 10 对 Spearman 相关，应用 BH FDR 校正并报告 q 值。

### C2. Bootstrap P 值公式的三方不一致

v14 的 bootstrap P 值计算在不同位置存在严重不一致，直接影响统计推断的有效性：

| 位置 | 公式 | 类型 | +1 伪计数 |
|------|------|------|-----------|
| P022 (Methods) | P = 2 × min(prop ≥, prop ≤) | 双侧 | 未提及 |
| P043 (Results) | fraction of permuted ω values that exceed observed ω | 单侧 | 有 |
| Note 1.5 (补充) | (count(≥) + 1)/(B + 1) | 单侧 | 有 |
| 伪代码 P047 | 2 × min(pct_above, pct_below) | 双侧 | 未提及 |

**问题分析**：

1. **单侧 vs. 双侧**：Methods 和伪代码使用双侧检验，而 Results 和补充材料使用单侧检验。对于 CKI 的应用场景，双侧检验更合适——因为 ω 既可能显著高于 null（功能分歧增强），也可能显著低于 null（功能约束，如 Strong candidate 的低 ω 信号）。如果使用单侧检验（仅检测 ω > null），则无法检测功能约束信号，而脑图谱分析的核心发现（30 个 Strong candidate）正是基于低 ω 值。

2. **+1 伪计数**：Results 和补充材料包含 +1 伪计数以避免 P = 0，但 Methods 和伪代码未提及。+1 伪计数是 bootstrap P 值的标准做法（Phipson & Smyth, 2010），应当统一包含。

3. **对校准实验的影响**：P047 声称校准实验"none of the six comparisons reached statistical significance (all P > 0.05, two-sided bootstrap test)"，但如果实际代码使用的是单侧公式，则正文中"two-sided"的声明是错误的。

4. **对 Strong candidate 筛选的影响**：Strong candidate 的核心标准是"低 ω"（residual < 0.3, ω < 15）。如果 bootstrap P 值使用单侧（ω > null 方向），则低 ω 值的 P 值将接近 1，无法达到显著性。这意味着 Strong candidate 的筛选完全依赖残差阈值而非统计显著性——这本身可以接受，但需要明确说明。

**建议**：
- 统一全稿为双侧检验：P = 2 × min[(count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)]，并统一包含 +1 伪计数。
- 如果确实使用单侧检验，需修改 Methods 和伪代码为单侧，并在正文中将"two-sided"改为"one-sided"。
- 明确说明 Strong candidate 筛选是基于残差阈值而非 P 值显著性，避免读者误解。

### C3. 校准实验 n = 6 仍不足且 TOST 被移除

v14 校准实验仍仅基于 6 次同种群随机分裂比较（P047）。n = 6 的核心问题在 v12 审稿中已详细指出，v14 未做任何改善：

1. **精度极低**：mean ω = 1.54（range 1.09–2.10），range 几乎翻倍（2.10/1.09 = 1.93×），表明 ω 在等效种群下的变异极大。在 n = 6 下，95% CI 宽度约为点估计的 60%+，无法精确定位基线 ω 值。

2. **TOST 等价检验被移除**：v12 至少尝试了 TOST 等价检验（虽然功效不足），v14 完全移除了 TOST，仅报告"all P > 0.05"。但"P > 0.05"只能说明"未拒绝零假设"，不能证明"零假设为真"。缺乏等价检验意味着无法正式宣称"CKI recognizes biologically equivalent cell populations as having no functional divergence"（P047）——这一声明在统计学上是不成立的。

3. **Tabula Muris 有 32 个细胞类型条目**，每个可做多次随机分裂，完全可以将 n 提升至 100+，但作者未做此努力。

4. **校准是整个方法的基础**：ω = 1.54 被用作"经验基线"（P091），所有后续分析的阈值（如 ω < 15 for Strong candidate）间接依赖这一基线。如果基线估计不精确，所有下游分析的不确定性都会被低估。

**建议**：
- 将校准比较数从 n = 6 增加到 n ≥ 100（利用 Tabula Muris 的 32 个细胞类型，每个做 3-5 次随机分裂）。
- 在更大样本下重新评估：ω 的分布形态、均值/中位数及 95% CI、变异性。
- 恢复或替代 TOST 等价检验，在 n ≥ 100 下使用合理的等价边界（如 Δ = 0.5，即 [1.04, 2.04]）进行正式等价检验。
- 报告校准实验的功效分析：在给定 n 和变异度下，TOST 能检测到的最小偏移量。

---

## 主要问题（Major Issues）

### M1. 效应量报告仍不完整，95% CI 全面缺失

v14 在 Statistical reporting（P037）中声称"Effect sizes are reported as Cohen's d; d > 0.8 indicates a large effect"，但实际执行存在多处缺失：

1. **Cohen's d 无 95% CI**：P115（Figure 4d）提到"Bootstrap Cohen's d effect sizes for NN vs. TT comparisons"，但正文和图注均未报告 d 值的 95% CI。Cohen's d 从 bootstrap 分布计算，获取 95% CI（percentile 方法）几乎无额外成本。

2. **Spearman r 无 95% CI**：P052 报告"Spearman r = -0.38 to -0.57, all P < 0.001"（n = 4,851），未报告 r 的 95% CI。对于 n = 4,851 的大样本，可通过 Fisher z 变换轻松计算：z = arctanh(r)，SE = 1/√(n-3)，CI_r = tanh(z ± 1.96×SE)。例如 r = -0.38 时，95% CI ≈ [-0.40, -0.36]。

3. **AUC 95% CI 被移除（退步）**：v12 报告了 AUC = 0.716 [0.698, 0.734]，v14 P055 仅报告"AUC = 0.716"而无 CI。P044 的"AUC = 0.847"同样无 CI。这是 v12→v14 的明确退步，需要恢复。

4. **非参数检验无效应量**：P060 的 Kruskal-Wallis（PAM50, P = 0.0002）和 Jonckheere-Terpstra（Edmondson, P < 0.001）均未报告效应量（ε² 或 Kendall's W）。Mann-Whitney U（LIHC paired, P = 0.024）未报告 rank-biserial correlation。

5. **效应量方向未解释**：v12 审稿（m3）指出 LUSC 和 LIHC 的 Cohen's d 为负值，与"tumors are more homogeneous"（NN/TT > 1）的结论表面矛盾。v14 未回应此问题。

**建议**：
- 为所有 Cohen's d 值补充 95% CI（bootstrap percentile 方法）。
- 为所有 Spearman r 值补充 Fisher z 变换的 95% CI。
- 恢复 AUC 的 95% CI 并说明计算方法（DeLong 或 bootstrap）。
- 为 Kruskal-Wallis 补充 ε² = H/(n-1) × (k-1)/k；为 Jonckheere-Terpstra 补充 Kendall's W；为 Mann-Whitney U 补充 rank-biserial correlation r = U/(n₁×n₂)。
- 解释 Cohen's d 负值与 NN/TT > 1 之间的一致性。

### M2. ω = 1 与 ω = 1.54 的概念张力未完全解决

v14 Discussion（P091）明确声明"ω = 1 does not carry population-genetic meaning of neutrality; rather, it is an empirically calibrated operational baseline (mean observational ω = 1.54)"。这一澄清是重要进步，但与正文中的操作性阈值描述存在张力：

1. **Introduction 仍以 ω = 1 为参考**：P015 描述"ω near 1 means the observed differences are consistent with baseline expectation; ω much greater than 1 means functional divergence exceeds baseline variation; ω much less than 1 means strong functional constraint." 如果经验基线是 1.54 而非 1，则这些阈值应以 1.54 为参考。

2. **Discussion 仍使用 ω = 1 阈值**：P091 同一段落中"We use ω < 1, ω ≈ 1, and ω > 1 as convenient operational thresholds"——但这些阈值与刚刚声明的 1.54 基线不一致。ω = 1.0 在 1.54 基线下已属于"低于基线"，但作者仍将其标记为"baseline"。

3. **校准实验的范围**：ω range 1.09–2.10 意味着等效种群可产生 ω > 2，这在 ω = 1 阈值框架下会被误判为"functional divergence exceeds baseline variation"。只有以 1.54 为参考，ω = 2.10 才被正确理解为"基线范围内的波动"。

4. **对 Strong candidate 的影响**：Strong candidate 要求 ω < 15。如果等效种群的 ω 可达 2.10，则 ω < 15 的阈值是否过于宽松？15/1.54 ≈ 9.7 倍基线——这意味着即使 ω 是基线的近 10 倍，仍被视为"低 ω"。这一阈值的合理性需要论证。

**建议**：
- 将 Introduction 和 Discussion 中的操作性阈值统一以经验基线（1.54）为参考：ω ≈ 1.54 为基线水平，ω >> 1.54 为功能分歧增强，ω << 1.54 为功能约束。
- 或者明确说明 ω = 1 阈值是"理论参考"而 1.54 是"经验观测"，并讨论二者差异的实际影响。
- 评估 ω < 15 阈值相对于基线 1.54 的合理性。

### M3. 乘法残差模型的阈值基础仍不明确

v14 的三个置信分层（P031, P074）仍为：Strong (residual < 0.3, ω < 15, lowest ω in pair, pair median ω > 20)、Moderate (residual < 0.5, ω < 25)、Weak (residual < 0.75, ω < 35)。以下问题在 v12 审稿中已指出但 v14 未回应：

1. **0.3 vs. 0.40 的差异**：v12 审稿指出"Strong 阈值（residual < 0.3）来自 1st percentile ≈ 0.40 的经验校准，但实际阈值为 0.3 而非 0.40，二者之间的差距未解释"。v14 仍未解释。

2. **联合条件的期望假阳性数**：Strong 需同时满足 4 个条件（residual < 0.3 AND ω < 15 AND lowest ω in pair AND pair median ω > 20）。4 个条件的联合概率在零假设下未计算。

3. **ω < 15 阈值对不同细胞类型的不均等影响**：Bergmann glia mean ω = 2.37，所有比较均远低于 15，该约束几乎不发挥筛选作用；而 astrocytes mean ω = 14.36，ω < 15 约束排除了约半数比较。这种不均等影响未讨论。

4. **排列验证仍不充分**：v12 审稿要求"提供排列验证的完整结果（数值对比表或 Bland-Altman 类型图）"，v14 仍未提供。P075 仅报告观察到的候选数（30 Strong, 1,247 Moderate, 6,567 Weak），无排列基线对比。

5. **Strong 标准的变更历史**：v12 有 3 条标准，v14 有 4 条（增加了"lowest ω in the region pair"和"pair median ω > 20"）。标准变更对候选数的影响未报告。

**建议**：
- 解释 residual < 0.3 vs. 1st percentile ≈ 0.40 的差异来源。
- 计算 4 条联合条件在零假设下的期望假阳性数（通过 region label 置换估计）。
- 按细胞类型分层评估 ω < 15 约束的筛选比例，讨论公平性。
- 提供排列验证的完整结果表：观察阈值 vs. 排列阈值，以及二者的 95% CI。
- 说明 v12→v14 Strong 标准变更的理由及对候选数的影响。

### M4. 样本量充分性讨论不足，无功效分析

v14 在 P065 新增了"We note that several cell types (particularly those with n = 1 or 3) have small sample sizes, and their rankings should be interpreted with appropriate caution"，这是对 v12 M2 的部分回应。但以下问题仍未解决：

1. **无正式功效分析**：全文未讨论任何 power analysis。在以下分析中，功效不足可能导致假阴性：
   - 校准实验 n = 6：TOST 等价检验在 n = 6 下的功效极低
   - 配对肿瘤-正常比较 n = 2-5 per cancer type（P059）：Mann-Whitney U 在 n = 2-5 下的最小可达 P 值约为 0.048（n = 5 vs. 5 时），几乎无法达到显著性
   - 跨器官细胞类型保守性：B cells n = 1, Memory B cells n = 1, Smooth muscle cells n = 1——n = 1 时无法计算 SD，仅报告 mean 无统计意义

2. **确认性 vs. 探索性分析未区分**：稿件未明确声明哪些分析为 confirmatory、哪些为 exploratory。4,851 对比较和 31,764 对比较的规模暗示探索性，但 30 个 Strong candidate 的深度解读暗示确认性。

3. **P059 的配对比较**：声明"the small number of patients with paired tumor and normal samples (n = 2–5 per cancer type) limits statistical power and precludes definitive conclusions"，但仍报告了 Mann-Whitney P = 0.024 for LIHC。在 n = 2-5 的样本量下，Mann-Whitney 检验的有效性存疑，且 P = 0.024 的稳定性未评估。

**建议**：
- 在 Methods 部分明确声明哪些分析为确认性、哪些为探索性。
- 对 n < 5 的分析结果，降级为补充表格，正文仅做定性描述。
- 补充 post-hoc 功效分析：在给定样本量和变异度下，能检测到的最小效应量。
- 对 P059 的配对比较，说明 n = 2-5 下 Mann-Whitney P = 0.024 的稳定性（如通过 bootstrap 评估 P 值的变异）。

### M5. k_n = 0.034 的统计解释仍不充分

v12 审稿 M5 指出 k_n = 0.034（human median）缺乏正式统计解释。v14 统一了对数底（base-2），使 k_n 的绝对值具有明确含义——0.034 表示 HK 基因表达分布之间的 JS divergence 为最大值的 3.4%。但以下问题仍未解决：

1. **k_n 的正式统计解释缺失**：0.034（3.4%）在实际含义上意味着什么？两个等效种群的 HK 基因表达分布有 3.4% 的分歧——这是大还是小？需要参照系（如与不同细胞类型间的 k_n 对比）才能判断。

2. **k_n 的变异范围**：v12 报告 k_n 范围 0.0018–0.221（约 100 倍变异）。当 k_n = 0.0018 时，ω = k_f/k_n 的分母极小，比值极不稳定。v14 未讨论这一比值稳定性问题。

3. **k_n 下限阈值**：v12 提到 k_n ≥ 0.001 的下限阈值，v14 未提及。是否仍使用此阈值？如果是，0.001 在 base-2 JS divergence 语境下意味着 0.1% 的分歧，几乎为测量噪声水平。

4. **k_n 与 k_f 的基因集大小不对等**：k_n 使用 ~1,130 个 HK 基因，k_f 使用 top-200 DE 基因（human pairwise scheme）。虽然 JS divergence 输出已归一化为概率分布间的距离，理论上不受基因数影响，但不同基因集大小的统计特性（方差、对噪声敏感度）不同，可能间接影响比值稳定性。

**建议**：
- 提供与生物学距离对比的 k_n 参照系（如同细胞类型 k_n vs. 不同细胞类型 k_n 的分布对比）。
- 讨论 k_n 接近下界时 ω 的比值稳定性问题，建议基于 k_n 分布 5th percentile 的下限阈值。
- 报告 k_n 和 k_f 的变异系数对比。

### M6. v14 新引入的编辑性错误和内部不一致

v14 虽修复了 v12 的多个问题，但引入了若干新的编辑性错误：

1. **P020 softmax 句子重复**："softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j)). softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j))." 同一句子连续出现两次，明显为编辑遗留错误。

2. **Figure 1c 的 B 值不一致**：P112（Figure 1 legend）标注"Bootstrap ω distribution (B = 500 permutations)"，但主文 P022 声明 primary analyses 使用 B = 1,000。如果 Figure 1c 展示的是 calibration 数据，则 B = 500 合理，但需在图注中明确说明。

3. **补充材料 HK 基因数不一致**：P019（主文）称"1,130 human-mouse shared HK genes"，P025 称"1,130 HRT Atlas v1.0 genes"；但补充材料 Note 4.2（P073）称"1,129 genes from HRT Atlas v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog was excluded)"。1,130 vs. 1,129 的差异需统一。

4. **ω 上限 cap = 1,000**：补充材料 Note 1.1（P018）提到"in practice omega is capped at 1,000"，伪代码 P039 也确认"omega <- k_f / k_n // capped at 1,000"。但主文未提及此截断。需说明：(a) 有多少比例的 ω 值被截断；(b) 截断对相关分析和下游分析的影响。

**建议**：
- 删除 P020 的重复句子。
- 统一 Figure 1c 的 B 值标注与主文一致，或在图注中说明"B = 500 for calibration example"。
- 统一 HK 基因数为 1,130（或 1,129，取决于是否计入无人类同源物的基因）。
- 在主文 Methods 中提及 ω cap = 1,000，并报告受影响的数据比例。

---

## 次要问题（Minor Issues）

### m1. P 值报告格式仍不统一

v14 P 值报告格式不一致：P < 0.001（P052）、P = 0.0002（P060 PAM50）、P = 0.017（P060 LUAD）、P = 0.024（P059 LIHC）、P > 0.05（P047）。NAR 通常要求统一格式。建议：P < 0.001 时报告 P < 0.001，否则报告精确值至三位小数。

### m2. 随机种子稳健性验证仍不充分

P035 称"All random seeds were fixed at 42"，但未报告多 seed 验证结果。v12 审稿（m2）要求"至少对核心结论报告 5-10 个 seed 的结果稳定性"，v14 未回应。建议至少对校准实验、Spearman 相关和 Strong candidate 筛选报告多 seed 稳定性。

### m3. ω 分布右偏的描述统计不一致

P069 等处使用"mean ω = 8.02 ± 4.93"描述右偏分布，而 P051 使用"mean 14.23, median 13.81"同时报告两者。建议统一：对右偏分布同时报告 mean ± SD 和 median [IQR]，或统一使用 median [IQR]。

### m4. 补充材料 Note 1.5 的置信区间描述

Note 1.5（P026）提到"Confidence intervals for omega are obtained via percentile bootstrap: the 2.5th and 97.5th percentiles of the null distribution"。但这一 CI 描述的是 ω_null 分布的区间，而非 ω_obs 估计的不确定性区间。这两个概念不同：(a) ω_null 分布的 95% 区间是零假设下的期望范围；(b) ω_obs 的 95% CI 应通过 bootstrap 重采样原始数据（而非排列标签）获得。需澄清 CI 的含义和计算方法。

### m5. 代码版本更新但可重现性细节仍不完整

v14 提到 CKI Python package v0.3.2（v12 为 v0.3.1），GitHub 和 Zenodo DOI 均已提供。但未提供完整的随机数生成协议（如 numpy/scipy 全局随机状态设置代码）。建议补充 `np.random.seed(42)` 之外的全局随机状态设置，以及分析环境的 `requirements.txt` 或 `environment.yml`。

### m6. TCGA 分析中 Cohen's d 方向解释缺失

v12 审稿 m3 指出 LUSC 和 LIHC 的 Cohen's d 为负值（-1.98, -1.22），与 NN/TT > 1 的结论表面矛盾。v14 未回应此问题。P115（Figure 4d）仅提及"Bootstrap Cohen's d effect sizes for NN vs. TT comparisons"，未在正文中报告具体 d 值。建议在正文中报告各癌症类型的 Cohen's d 值及其方向解释。

### m7. Discussion 中 OU 模型展望缺乏具体性

P093 新增了对 Ornstein-Uhlenbeck 模型的展望："Integrating CKI's baseline-normalized decomposition with OU-based selection strength estimation is a promising direction for future theoretical development." 这是好的方向性展望，但缺乏具体性——如何将 CKI 的比率框架与 OU 的漂移参数映射？建议补充一两句具体设想。

### m8. 参考文献编号与正文引用的不一致

P150 引用 Storey & Tibshirani (2003) 关于 FDR 的经典文献，但正文未在任何 FDR 讨论中引用此文。考虑到 C1 涉及 FDR 问题，建议在补充材料 Note 3.3 中引用此文作为方法学背景。

---

## 优点（Strengths）

1. **v12→v14 的实质性改进**：作者在关键统计问题上做出了有意义的修复，特别是 JS 对数底统一、B 值提升和检验统计量修改。这些修复表明作者认真对待了审稿意见。

2. **概念诚实性显著提升**：v14 Discussion（P091-093）对 CKI 与 Ka/Ks 的类比起到了更加审慎的界定，明确声明"CKI is a heuristic index, not a formal measure of Darwinian selection"和"ω = 1 does not carry population-genetic meaning of neutrality"。这种科学诚实值得肯定。

3. **负对照设计依然出色**：OPC 作为最强迁移细胞却产生 0 个 Strong candidate（P077），为方法特异性提供了有力支持。这一设计在 v14 中被更清晰地定位为"key negative control validates method specificity"。

4. **统计透明度提升**：P037（Statistical reporting）比 v12 更加详细和明确，特别是"All reported P-values are raw bootstrap P-values without multiple testing correction"的声明，以及"Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05 without additional correction"的澄清。

5. **多数据集验证框架**：在四个独立数据集（Tabula Muris, Tabula Sapiens, TCGA, Siletti 脑图谱）上验证方法，涵盖不同物种、技术平台和生物学尺度，体现了良好的外部验证意识。

6. **非参数检验的合理使用**：面对右偏的 ω 分布，稿件一致使用中位数描述统计和非参数检验（Kruskal-Wallis, Mann-Whitney U, Jonckheere-Terpstra），这是正确的统计决策。

7. **敏感性分析**：HK 基因集选择敏感性分析（r > 0.95，P097）和参数扫描（AUC = 0.847，P044）体现了方法稳健性意识。

8. **数据和代码开放**：GitHub 代码库（v0.3.2, MIT License）、Zenodo DOI、分析脚本索引（补充材料 Data 1）均提供，可重现性基础良好。

---

## 具体修改建议

### 对应 Critical Issues

**对 C1（多重检验校正）**：
1. 对脑图谱 31,764 次比较应用 BH FDR 校正，报告 30 个 Strong candidate 在 q < 0.05 下的存活数。
2. 补充排列检验：region label 置换（B ≥ 1,000），计算每个组合的排列 P 值和 FDR。
3. 计算 Strong 联合条件在零假设下的期望假阳性数。
4. 对 TCGA 三个临床变量检验应用 Bonferroni 校正（α = 0.0167）。
5. 对 Tabula Sapiens 10 对 Spearman 相关应用 BH FDR 并报告 q 值。

**对 C2（Bootstrap P 值不一致）**：
1. 统一全稿为双侧检验公式：P = 2 × min[(count(≥)+1)/(B+1), (count(≤)+1)/(B+1)]。
2. 或统一为单侧并修改所有"two-sided"声明。
3. 统一包含 +1 伪计数。
4. 明确 Strong candidate 筛选基于残差阈值而非 P 值。

**对 C3（校准 n = 6）**：
1. 将校准比较数增加至 n ≥ 100。
2. 恢复 TOST 等价检验，使用合理等价边界。
3. 报告功效分析。

### 对应 Major Issues

**对 M1（效应量 95% CI）**：
1. 为所有 Cohen's d 补充 bootstrap percentile 95% CI。
2. 为所有 Spearman r 补充 Fisher z 变换 95% CI。
3. 恢复 AUC 的 95% CI 并说明计算方法。
4. 为非参数检验补充 ε²、Kendall's W 或 rank-biserial correlation。

**对 M2（ω = 1 vs 1.54）**：
1. 统一操作性阈值以 1.54 为参考，或明确说明 1 和 1.54 的关系。
2. 评估 ω < 15 阈值相对于基线 1.54 的合理性。

**对 M3（阈值基础）**：
1. 解释 0.3 vs. 0.40 的差异。
2. 计算联合条件期望假阳性数。
3. 提供排列验证完整结果。
4. 评估 ω < 15 对不同细胞类型的公平性。

**对 M4（样本量与功效）**：
1. 明确区分确认性和探索性分析。
2. 对 n < 5 的结果降级为补充表格。
3. 补充 post-hoc 功效分析。

**对 M5（k_n 解释）**：
1. 提供 k_n 的参照系对比。
2. 讨论 k_n 接近下界时的比值稳定性。
3. 报告 k_n 和 k_f 的变异系数。

**对 M6（编辑性错误）**：
1. 删除 P020 重复句子。
2. 统一 Figure 1c 的 B 值标注。
3. 统一 HK 基因数。
4. 在主文提及 ω cap = 1,000 并报告影响比例。

### 对应 Minor Issues

1. 统一 P 值报告格式。
2. 报告多 seed 验证定量结果。
3. 统一使用 median [IQR] 描述右偏分布。
4. 澄清补充材料 Note 1.5 中 CI 的含义。
5. 补充随机状态设置代码和 environment.yml。
6. 报告并解释 TCGA Cohen's d 方向。
7. 补充 OU 模型展望的具体设想。
8. 在 FDR 讨论中引用 Storey & Tibshirani (2003)。

---

## 总结

CKI v14 相比 v12 在统计严谨性方面有实质性进步（5.8 → 6.8），核心修复包括 JS 对数底统一、Bootstrap B 值提升和检验统计量改进。作者对 ω = 1.54 经验基线的概念澄清尤其值得肯定，表明对方法局限性的深入理解。

然而，三个 Critical Issues 仍需在发表前解决：(1) 多重检验校正的持续缺失——"NOT systematically applied"的声明不能替代实际的统计校正，特别是当 30 个 Strong candidate 被深度解读时；(2) Bootstrap P 值公式在主文、Results、补充材料和伪代码之间存在三方不一致（单侧 vs. 双侧），直接影响统计推断有效性；(3) 校准实验 n = 6 仍不足且 TOST 被移除，方法基线假设的统计基础薄弱。

建议作者进行聚焦修订（focused revision），优先解决 C1-C3 和 M1-M2。在修正这些问题后，本稿件有望达到 NAR 的发表标准。考虑到 v12→v14 的改进轨迹，作者有能力在下一轮修订中解决剩余问题。
