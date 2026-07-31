# 统计学专家审稿报告 — CKI v12 NAR Submission

## 评分：5.8 / 10

## 总体评价

CKI 算法在概念设计上具有创新性，将 Ka/Ks 类比思想引入转录组比较领域，通过分解中性偏移率（k_n）和功能转化率（k_f）构建基线标准化的功能分歧指数，这一思路具有启发价值。稿件在方法敏感性分析（HK 基因集大小扫描、HVG 数量扫描）和负对照设计（OPC 零 Strong 信号）方面体现了较好的方法学意识。v12 相比 v11 在统计修正方面有明显进步，包括移除 bootstrap/FDR 的虚假声明、修正 JS 对数底等。

然而，从统计学严谨性角度审视，本稿件存在多个需要实质性问题。最突出的问题是：(1) 多重检验校正的全面缺失——在脑图谱分析中进行了 31,764 次比较却未应用任何 FDR 或 Bonferroni 校正，仅以"注意多重性"一笔带过；(2) bootstrap 检验设计存在逻辑矛盾——校准实验显示 ω 的经验零假设均值应为 ~1.54 而非理论值 1，但检验统计量仍以 |ω - 1| 为中心；(3) 主文与补充材料在 JS 对数底这一基础参数上存在直接矛盾（主文称自然对数，补充材料称 base-2）；(4) 多项关键分析的样本量严重不足（校准实验 n=6，配对肿瘤-正常 n=2-5，多个跨器官细胞类型 n=1-3）。这些问题中部分需要在发表前解决。

以下按严重程度分类详述。

---

## 关键问题（Critical Issues）

### C1. 多重检验校正的全面缺失

稿件在 Statistical reporting 部分明确声明："For human, TCGA, and brain analyses, standard statistical tests were applied without multiple-testing correction; all reported P-values are raw, uncorrected values." 这一做法在多个分析层面存在严重问题：

- **脑图谱分析**：31,764 次跨区域比较中，仅凭经验百分位阈值（残差 < 0.3）筛选出 30 个 Strong candidate。即使残差阈值本身是数据驱动的，但后续对 30 个候选信号逐一进行文献交叉验证并赋予生物学机制解释，实质上构成了对多重比较结果的选择性解读。更关键的是，在没有正式零分布的情况下，无法评估 30/31,764（0.09%）这一比例是否超出了随机预期。稿件提到排列阈值"qualitatively consistent but not identical"，但未提供具体数值，使读者无法评估稳健性。
  
- **TCGA 临床分析**：在同一个数据集内同时检验了 PAM50 亚型（Kruskal-Wallis, P = 0.0002）、Edmondson 分级（Jonckheere-Terpstra, P < 0.001）和突变状态（Kruskal-Wallis, P = 0.017）三个临床变量。虽然稿件声明"we note the number of tests performed"，但仅凭声明而不做校正无法控制 family-wise error rate 或 FDR。

- **Tabula Sapiens 分析**：4,851 对细胞类型比较中，五个度量的两两 Spearman 相关（10 对比较）均报告 P < 0.001。虽然 n = 4,851 使得即使微弱相关也统计显著，但问题在于：研究者未区分"统计显著"与"实际显著"，且未报告相关性系数的置信区间。

**建议**：至少对脑图谱分析中的 31,764 次比较应用 Benjamini-Hochberg FDR 校正，并报告校正后的 q 值。对 TCGA 多临床变量检验，应明确声明检验总数并应用 Bonferroni 或 FDR 校正。对"30 个 Strong candidate"的发现，应通过排列检验计算期望候选数，并评估观察值是否显著超出期望值。

### C2. Bootstrap 检验统计量与经验零假设的逻辑矛盾

稿件使用的 bootstrap 检验公式为：Empirical P = (count(|ω_null - 1| >= |ω_obs - 1|) + 1) / (B + 1)。该公式以 |ω - 1| 为检验统计量，隐含假设 ω = 1 为零假设下的期望值。然而：

- 校准实验（P048）明确显示，同种群随机分裂的 mean ω = 1.54（median 1.42, 95% CI [1.12, 2.08]），且 TOST 等价检验未确认 ω = 1 的严格等价性。
- 如果排列零分布的 ω_null 也以 ~1.54 为中心（这是合理的，因为排列本质上也是随机重分组），那么 |ω_null - 1| 将系统性偏大（平均 ~0.54），导致检验统计量在零假设下不以 0 为中心，从而使检验偏保守或偏 liberal，取决于 ω_obs 的方向。

正确的做法应该是：(a) 使用排列分布的中心（如 median(ω_null)）代替 1 作为参考点，即 P = (count(|ω_null - median(ω_null)| >= |ω_obs - median(ω_null)|) + 1) / (B + 1)；或者 (b) 直接使用排列分布的尾部概率，即 P = (count(ω_null >= ω_obs) + 1) / (B + 1)（单侧）。

**建议**：重新审视 bootstrap 检验的检验统计量设计，使其与经验零假设一致。如果保留 |ω - 1| 作为统计量，需要明确论证为何 ω = 1 是零假设下的正确参考点，且需要解释校准实验中 ω = 1.54 的偏移如何影响检验的有效性。

### C3. 主文与补充材料在 JS 对数底上的直接矛盾

主文 Methods（P021）明确声明："JS divergence uses the natural logarithm." 而补充材料 Note 1.1（第 1 段）写道："D(p||q) = Σ p_i log2(p_i/q_i). When using base-2 logarithms, the JS divergence is bounded in [0, 1]."

这是一个基础性矛盾，直接影响：
- JS divergence 的取值范围：base-2 时 ∈ [0, 1]，自然对数时 ∈ [0, ln 2] ≈ [0, 0.693]
- k_n 和 k_f 的绝对值解释：median k_n = 0.034（human）在不同对数底下的含义完全不同
- ω = k_f/k_n 的比值理论上不受对数底影响（因为两者使用同一底数），但如果实际实现中 k_n 和 k_f 使用了不同的对数底，则 ω 会被系统性偏移

v12 的背景信息表明 JS 对数底修正是 v11→v12 的重要修正之一，但当前版本中主文与补充材料的不一致说明修正可能不彻底或存在遗留错误。

**建议**：统一主文与补充材料的对数底描述。如果使用自然对数，需修正补充材料中 [0, 1] 的界值声明（应为 [0, ln 2]）；如果使用 base-2，需修正主文。同时，需在代码层面验证实际实现中 k_n 和 k_f 使用的是同一对数底。

### C4. B = 500 的 bootstrap 重采样次数不足

稿件在所有 bootstrap 分析中使用 B = 500。这一选择在多个方面存在问题：

- **精度不足**：B = 500 时，P 值的最小可能值为 1/501 ≈ 0.002。如果研究者希望声明 P < 0.001（如某些相关分析），则 B = 500 在数学上无法达到。虽然相关分析使用标准检验而非 bootstrap，但这一限制仍影响了 bootstrap 检验的分辨力。
- **零分布估计精度**：B = 500 仅生成 500 个零分布样本，对于分布尾部的估计极为粗糙。现代推荐值通常为 B ≥ 1,000（用于探索性分析）至 B ≥ 10,000（用于正式推断）。
- **重复表述**：P023 中 "B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration" 存在重复，提示可能为编辑遗留错误。
- **可重现性**：P036 提到"Stability across random seeds was verified for key results; full multi-seed validation was not performed." 但未报告 seed 稳定性验证的具体结果。

**建议**：将关键分析的 B 值提升至至少 1,000-2,000，并报告多 seed 稳定性验证的定量结果（如不同 seed 下 P 值的变异系数）。修正 P023 中的重复表述。

---

## 主要问题（Major Issues）

### M1. 校准实验样本量严重不足（n = 6）

核心校准实验仅基于 6 次同种群随机分裂比较。在 n = 6 的情况下：

- 95% CI [1.12, 2.08] 宽达 0.96，约为点估计（1.54）的 62%，表明精度极低
- TOST 等价检验在 n = 6 下的统计功效极低，"未确认严格等价"可能完全是功效不足的结果，而非真实的不等价
- 稿件以这 6 次比较的结论（"ω close to 1"）作为整个方法体系的基础假设，但 n = 6 不足以支持这一假设
- 范围 1.09–2.10 显示 ω 几乎翻倍的变异，这一变异幅度与"中性行为"的声明不完全一致

**建议**：大幅增加校准比较的数量。Tabula Muris 有 32 个细胞类型条目，可以每个细胞类型做多次随机分裂，轻松将 n 提升至 100+。在更大的样本下重新评估 ω 的分布、TOST 等价检验结果和 95% CI。

### M2. 多项分析的样本量不足且未讨论统计功效

除校准实验外，多处分析的样本量严重不足：

- **配对肿瘤-正常比较**（P058）：n = 2–5 per cancer type，稿件承认"limits statistical power and precluding definitive cross-organ cell-type conservation estimates"，但仍报告了 Mann-Whitney P = 0.024 for LIHC。在 n = 2-5 的样本量下，Mann-Whitney 检验的有效性存疑。
- **跨器官细胞类型保守性**（P061-064）：多个细胞类型仅有 n = 1-3 对比较（如 B cells n=1, Endothelial cells n=3, Memory B cells n=1）。稿件声明这些为"exploratory"且"without standard deviation estimates"，但仍报告了均值和排名，可能误导读者。
- **Spearman r = 0.74, p = 0.015**（Supplementary Fig. S4C）：基于 10 个细胞类别的相关分析，n = 10 下的相关性检验功效很低，p = 0.015 的结果可能不稳定。
- 全文未讨论任何功效分析（power analysis），未声明哪些分析为确认性（confirmatory）、哪些为探索性（exploratory）。

**建议**：明确区分确认性和探索性分析。对 n < 5 的分析结果，考虑降级为附录表格而非正文图表。补充 post-hoc 功效分析，说明在给定样本量下能检测到的最小效应量。

### M3. ω 阈值和置信分层的统计学基础不明确

乘法残差模型的三个置信分层（Strong: residual < 0.3, ω < 15; Moderate: residual < 0.5, ω < 25; Weak: residual < 0.75, ω < 35）存在以下统计学问题：

- **阈值来源**：稿件称 Strong 阈值（residual < 0.3）来自"1st percentile ≈ 0.40"的经验校准，但实际阈值为 0.3 而非 0.40，二者之间的差距未解释。如果 1st percentile = 0.40，为何阈值设为 0.3？
- **联合条件问题**：Strong candidate 需同时满足 residual < 0.3 AND ω < 15（v12 从 4 条降为 3 条）。多个条件的联合概率未计算，无法评估期望假阳性数。在 31,764 次比较中，即使单条件假阳性率为 1%，联合条件的假阳性期望也需要正式计算。
- **ω < 15 阈值的任意性**：ω < 15 这一约束在脑图谱分析中的合理性未论证。不同细胞类型的 ω 分布差异巨大（Bergmann glia mean ω = 2.37 vs. astrocytes mean ω = 14.36），统一的 ω < 15 阈值可能对不同细胞类型的灵敏度产生不均等影响。
- **排列验证不充分**：稿件提到"permutation-based thresholds (shuffling region labels within each cell type) yielded qualitatively consistent but not identical cutoffs"，但未提供具体数值、图表或定量对比。

**建议**：(1) 解释 0.3 vs. 0.40 的差异来源；(2) 计算联合条件的期望假阳性数；(3) 提供排列验证的完整结果（数值对比表或 Bland-Altman 类型图），而非仅以"qualitatively consistent"概括；(4) 论证 ω < 15 阈值对不同细胞类型公平性。

### M4. 效应量报告不完整且不一致

虽然稿件在 Statistical reporting 部分声称报告效应量，但实际执行存在不一致：

- **Bootstrap 检验**：报告了 Cohen's d（如 BRCA +1.04, LUSC −1.98, LIHC −1.22），但未提供 Cohen's d 的 95% CI。Cohen's d 本身是从 bootstrap 分布计算的，应当可以轻松获取 CI。
- **Spearman 相关**：报告了 r 值和 P 值，但未报告 95% CI。对于 n = 4,851 的相关分析，CI 可以通过 Fisher z 变换计算，应当报告。
- **Kruskal-Wallis / Mann-Whitney**：声称报告 ε² 或 rank-biserial correlation，但在正文中（P059）仅报告了 P 值和均值±SD，未见效应量。例如 PAM50 Kruskal-Wallis P = 0.0002，但 ε² 未在正文出现。
- **Jonckheere-Terpstra 趋势检验**：P < 0.001 但无效应量。Jonckheere-Terpstra 的效应量可用 Kendall's W 或 rank correlation 表示。
- **AUC 值**：报告了 95% CI（如 AUC = 0.716 [0.698, 0.734]），这是正确的做法，但 CI 的计算方法（bootstrap 还是 DeLong）未说明。

**建议**：统一在正文表格中报告所有统计检验的效应量及其 95% CI。对于 Spearman 相关，补充 Fisher z 变换的 95% CI。对于非参数检验，补充 ε² 或 rank-biserial correlation 的正文报告。

### M5. k_n 统计量的合理性与稳定性

k_n 的中位数为 0.034（human），范围为 0.0018–0.221，约 100 倍变异。以下问题需要关注：

- **比值稳定性**：当 k_n 接近下界（0.0018）时，ω = k_f/k_n 的分母极小，导致比值极不稳定。稿件建议 k_n ≥ 0.001 的下限阈值，但 0.001 似乎过低——在 k_n = 0.001 时，即使 k_f 的微小波动（如测量误差）也会导致 ω 的剧烈变化。
- **k_n = 0.034 的统计解释**：稿件未提供 k_n 的正式统计解释。0.034 在 base-2 JS divergence 语境下意味着 HK 基因表达分布之间的分歧约为最大值的 3.4%，但在自然对数语境下（如主文所述），解释完全不同。需明确对数底后才能讨论 k_n 的绝对值含义。
- **k_n 与 k_f 的基因集大小不对等**：k_n 使用 ~1,000 个 HK 基因，k_f 使用 top-200 DE 基因。虽然稿件论证"the ratio ω = k_f/k_n is scale-invariant within each JS divergence computation"（因为 JS divergence 输出已归一化为概率分布间的距离，不受基因数直接影响），但不同基因集大小的统计特性（如方差、对噪声的敏感度）不同，可能间接影响比值。

**建议**：(1) 重新评估 k_n 下限阈值，建议基于 k_n 分布的 5th percentile 而非任意值；(2) 提供对数底统一后的 k_n 正式统计解释；(3) 补充 k_n 和 k_f 的变异系数对比，评估比值稳定性。

### M6. v11→v12 统计修正的残留问题

v12 修复了多个 v11 的统计问题，但以下方面仍需关注：

- **bootstrap/FDR 虚假声明的移除**：v12 移除了虚假声明，但取而代之的是完全不进行多重检验校正（见 C1）。从一个极端（虚假声明 FDR）到另一个极端（完全不校正）并非正确的修正方式。
- **"Strong candidate"标准从 4 条降为 3 条**：稿件未说明被移除的第 4 条标准是什么，也未论证为何移除该标准不影响特异性。如果移除标准增加了候选数，则需要重新验证特异性。
- **JS 对数底修正**：如 C3 所述，主文与补充材料仍存在矛盾，说明修正未完全落实。
- **k_n 统计数据校正（human 0.034）**：0.034 这一数值在 v12 中被明确标注为 median，但如 M5 所述，其统计解释仍不充分。

**建议**：提供 v11→v12 修改的完整 changelog，包括被移除的第 4 条 Strong 标准的具体内容和移除理由。补充修改前后的候选数对比，评估修改对灵敏度/特异性的影响。

---

## 次要问题（Minor Issues）

### m1. P 值报告格式不统一

稿件中 P 值报告格式不一致：部分为"P < 0.001"（P053, P059），部分为"P = 0.0002"（P059 PAM50），部分为"P = 0.017"（P059 LUAD mutations），部分为"P = 0.024"（P058 LIHC paired）。NAR 期刊通常要求统一报告精确 P 值或使用一致的截断标准。建议统一为：P < 0.001 时报告 P < 0.001，否则报告精确值至三位小数。

### m2. 随机种子固定但未充分验证稳健性

P036 提到"All random seeds were fixed at 42 for reproducibility"且"Stability across random seeds was verified for key results; full multi-seed validation was not performed." 但未报告：(1) 哪些结果进行了多 seed 验证；(2) 验证结果的定量指标；(3) 为何未进行全面多 seed 验证。建议至少对核心结论（校准实验、Spearman 相关、Strong candidate 筛选）报告 5-10 个 seed 的结果稳定性。

### m3. TCGA 分析中的 Cohen's d 解释问题

P057 报告了"Bootstrapped Cohen's d analysis"的效应量（BRCA +1.04, LUSC −1.98, LIHC −1.22）。但 LUSC 和 LIHC 的负值 d 意味着 NN < TT（即肿瘤间差异大于正常组织间差异），这与稿件的核心结论"tumors are more transcriptionally homogeneous"（NN/TT > 1）矛盾。虽然这可能反映了不同比较维度（NN vs. TT 的中位数比值 vs. Cohen's d 的均值差异），但稿件未解释这一表面矛盾。建议明确各效应量的方向解释。

### m4. ω 分布的右偏处理

P044 提到"the empirical ω distribution is right-skewed (median 13.68 vs. mean 14.12)"。在右偏分布下，使用中位数和非参数检验是正确的。但在 P052 等处仍使用"mean ω = 8.70"和"mean ω = 16.18"进行组间比较。建议统一使用中位数 [IQR] 进行描述性统计，或在报告均值时同时报告中位数以便读者判断偏态程度。

### m5. 补充材料中 ω 上限设定

补充材料提到"in practice omega is capped at 1,000"。这一任意截断可能影响统计分布和极端值分析。建议说明：(1) 有多少比例的 ω 值被截断；(2) 截断对相关分析和回归分析的影响；(3) 是否进行了未截断数据的敏感性分析。

### m6. 代码版本与可重现性

稿件提到 CKI Python package v0.3.1 和固定 seed 42，但未提供完整的随机数生成协议（如 numpy/scipy 的随机状态设置方式）。建议补充 `np.random.seed(42)` 之外的全局随机状态设置代码，以及分析环境的完整 `requirements.txt`（已在 GitHub 提供，建议在补充材料中明确引用）。

### m7. AUC 置信区间计算方法未说明

P054 报告了 AUC 的 95% CI（如 AUC = 0.716 [0.698, 0.734]），但未说明 CI 的计算方法（bootstrap percentile、DeLong 方法等）。不同的 CI 计算方法有不同的统计性质，建议明确说明。

### m8. 校准实验中等价边界的选择

P048 使用 TOST 等价检验，等价边界设为 [0.67, 1.50]。这一边界的选择理由未说明。等价边界的选择应基于领域知识或最小有意义差异（minimal clinically important difference）。建议补充边界选择的依据。

---

## 优点（Strengths）

1. **方法敏感性分析充分**：对 HK 基因集大小（250-1000）和 HVG 数量（1000-4000）进行了系统扫描，报告了 ω 变异系数 < 13% 的定量结果，表明方法对参数选择具有较好的稳健性。

2. **负对照设计出色**：以 OPC（成年 CNS 中最活跃迁移的细胞）作为负对照，预期应有迁移信号但实际检测到 0 个 Strong candidate，为方法特异性提供了有力支持。这一设计思路体现了优秀的实验设计意识。

3. **透明度与诚实性**：稿件在多处坦率承认了方法局限，包括"CKI is a heuristic, not a formal evolutionary selection model"、HK 基因的中性假设是操作性的而非机制性的、TCGA bulk RNA-seq 的混杂因素等。这种科学诚实值得肯定。

4. **非参数检验的合理使用**：面对右偏的 ω 分布，稿件选择中位数描述统计和非参数检验（Kruskal-Wallis, Mann-Whitney U, Jonckheere-Terpstra），这是正确的统计决策。

5. **校准实验设计**：通过同种群随机分裂验证中性行为，以及跨生物学距离的单调性验证（C → S → D → X 类别），体现了方法验证的系统思路。

6. **效应量意识**：虽然执行不一致（见 M4），但稿件在 Statistical reporting 部分明确承诺报告效应量（Cohen's d, ε², rank-biserial correlation），表明作者具备效应量报告的意识。

7. **跨数据集验证**：在四个独立数据集（Tabula Muris, Tabula Sapiens, TCGA, Siletti 脑图谱）上验证方法，涵盖不同物种、不同技术平台和不同生物学问题，体现了较好的外部验证意识。

---

## 具体修改建议

### 对应关键问题（Critical Issues）

**对 C1（多重检验校正）**：
1. 在脑图谱分析中，对 31,764 次比较应用 Benjamini-Hochberg FDR 校正。报告 Strong candidate 在 FDR < 0.05 下的存活数量。如果 30 个候选中部分在 FDR 校正后不再显著，应如实报告。
2. 补充排列检验：在 31,764 次比较中，对每个 (cell_type, region_pair) 组合进行 region label 置换（建议 B ≥ 1000），计算每个组合的排列 P 值，并报告 FDR 校正后的 Strong candidate 数量。
3. 对 TCGA 多临床变量检验，应用 Bonferroni 校正（3 个检验，α = 0.05/3 = 0.0167）。报告校正后哪些结果仍然显著。
4. 对 Tabula Sapiens 的 10 对 Spearman 相关，应用 BH FDR 校正并报告 q 值。

**对 C2（bootstrap 检验统计量）**：
1. 修改检验统计量，使用排列分布的中位数作为参考点替代 1，或直接使用排列分布的尾部概率。
2. 报告 ω_null 分布的描述统计（中位数、IQR、范围），使读者能够判断零分布的中心位置。
3. 论证或实证验证：在 ω_null 中心 ≈ 1.54 的情况下，使用 |ω - 1| 作为检验统计量对第一类错误率的影响。

**对 C3（JS 对数底矛盾）**：
1. 逐一核查主文 P021、补充材料 Note 1.1、以及实际代码实现中的对数底使用。
2. 统一为同一对数底（建议 base-2，因为补充材料的 [0, 1] 界值声明仅在 base-2 下成立）。
3. 如果使用 base-2，修正主文 P021 中的"natural logarithm"为"base-2 logarithm"。
4. 如果使用自然对数，修正补充材料中的 [0, 1] 界值为 [0, ln 2]。
5. 确认 k_n 和 k_f 在代码实现中使用同一对数底。

**对 C4（bootstrap B 值）**：
1. 将关键分析的 B 值提升至 B = 2,000。
2. 报告 5 个不同随机种子下的 P 值变异系数。
3. 修正 P023 中的重复表述。

### 对应主要问题（Major Issues）

**对 M1（校准样本量）**：
1. 将校准比较数从 n = 6 增加到 n ≥ 100（利用 Tabula Muris 的 32 个细胞类型，每个做 3-5 次随机分裂）。
2. 在更大样本下重新评估：ω 的分布形态、均值/中位数及 95% CI、TOST 等价检验结果。
3. 报告校准实验的功效分析：在 n = 100 和给定变异度下，TOST 能检测到的最小偏移量。

**对 M2（样本量不足）**：
1. 在方法部分明确声明哪些分析为确认性、哪些为探索性。
2. 对 n < 5 的结果，移至补充表格，正文仅做定性描述。
3. 对 Supplementary Fig. S4C 的 Spearman 相关（n = 10），补充功效说明：在 n = 10、α = 0.05 下，检测 r ≥ 0.7 的功效约为 0.45，属于探索性分析。

**对 M3（阈值基础）**：
1. 明确解释 0.3 vs. 0.40 的差异（是否为向下取整或其他考虑）。
2. 提供排列验证的完整结果表：观察阈值 vs. 排列阈值，以及二者的 95% CI。
3. 计算联合条件（residual < 0.3 AND ω < 15）在零假设下的期望假阳性数。
4. 按细胞类型分层评估 ω < 15 阈值的公平性。

**对 M4（效应量报告）**：
1. 在正文表格中统一报告所有统计检验的效应量及 95% CI。
2. 对 Spearman 相关，使用 Fisher z 变换计算 95% CI：z = arctanh(r)，SE = 1/√(n-3)，CI_z = z ± 1.96×SE，CI_r = tanh(CI_z)。
3. 对 Cohen's d，从 bootstrap 分布的 2.5th 和 97.5th percentile 获取 95% CI。
4. 在 P059 正文中补充 PAM50 的 ε²、Edmondson 的 Kendall's W、LUAD 突变的 rank-biserial correlation。

**对 M5（k_n 统计量）**：
1. 统一对数底后，重新评估 k_n = 0.034 的统计含义。
2. 计算 k_n 分布的 5th percentile，以此作为下限阈值的建议。
3. 报告 k_n 和 k_f 的变异系数对比表。

**对 M6（v11→v12 修正）**：
1. 提供完整的 v11→v12 修改 changelog 作为补充材料。
2. 明确被移除的第 4 条 Strong 标准的内容和移除理由。
3. 报告修改前后 Strong candidate 数量、假阳性率的对比。

### 对应次要问题（Minor Issues）

**对 m1-m8**：
1. 统一 P 值报告格式。
2. 报告多 seed 验证的定量结果。
3. 解释 LUSC/LIHC Cohen's d 负值与 NN/TT > 1 的表面矛盾。
4. 统一使用中位数 [IQR] 描述 ω 分布。
5. 报告 ω 截断（cap = 1000）影响的数据比例。
6. 补充随机状态设置的完整代码。
7. 说明 AUC CI 的计算方法。
8. 论证 TOST 等价边界 [0.67, 1.50] 的选择依据。

---

## 总结

CKI 算法在概念层面具有创新性，v12 相比 v11 在统计严谨性方面有明显改善。然而，当前版本仍存在多个统计学问题需要在发表前解决。其中最关键的是多重检验校正的全面缺失（C1）、bootstrap 检验统计量与经验零假设的矛盾（C2）、以及主文与补充材料在 JS 对数底上的直接矛盾（C3）。这些问题不仅影响特定结果的解释，更关乎整个方法体系的统计学有效性。

建议作者进行大修（major revision），重点解决四个 Critical Issues 和六个 Major Issues。在修正这些问题后，本稿件有望达到 NAR 的发表标准。
