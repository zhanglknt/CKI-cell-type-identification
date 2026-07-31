# CKI 算法方法学审稿报告

**审稿人角色**：计算生物学方法学审稿专家（单细胞转录组分析、基因选择算法、信息论散度度量、进化选择压力检测）

**审稿版本**：v15 投稿包（manuscript.txt, supplementary.txt, reproducibility.txt）

**审稿日期**：2026-07-27

---

## 1. 总体评分：5.5 / 10

CKI 提出了一个概念上新颖且有启发性的框架——将转录组差异分解为"基线差异"（k_n）与"功能差异"（k_f）两个分量并用比值 ω = k_f/k_n 量化功能分化程度。这一思路在单细胞转录组比较分析领域具有一定原创性，且在四个大规模数据集上展示了应用广度。

然而，从方法学严谨性角度评估，当前稿件存在多处严重的内部文档不一致、统计推断缺陷、以及数学基础论证不足等问题，这些在投稿前必须解决。核心问题包括：（1）正文、补充材料与复现指南之间存在关于对数底和归一化方式的直接矛盾；（2）k_f 使用配对差异基因（pairwise DE）引入的选择偏倚未被充分讨论或校正；（3）大规模多重比较（31,764 对）缺乏 FDR 校正；（4）ω = 1 中性阈值缺乏数学推导，经验校准仅基于 n = 6。

在解决上述问题后，该方法具有中等偏上的方法学价值和实际应用潜力。

---

## 2. Critical 问题（投稿阻断）

### C1. 三份文档之间存在直接矛盾：对数底（base-2 vs natural log）

**正文**（manuscript.txt:20）和**补充材料**（supplementary.txt:16）明确声明：
> "JS divergence uses the base-2 logarithm (range [0, 1])"

但**复现指南**（reproducibility.txt:50, 53）声明：
> "JS(P || Q) is the Jensen-Shannon divergence (natural log)"
> "KL(P || M) = sum_i [ P_i * ln(P_i / M_i) ]"

这是**直接矛盾**。对数底的选择虽然不影响 ω = k_f/k_n 的比值（因为分子分母使用相同的底，比值中性），但直接影响 JS 散度的绝对范围（base-2 → [0, 1]；natural log → [0, ln 2 ≈ 0.693]），进而影响 k_n 和 k_f 的绝对数值以及读者对 ω 量级的理解。

**要求**：必须统一对数底的定义，并确保实际代码实现与文档一致。如果实际代码使用 `scipy.spatial.distance.jensenshannon`，需注明该函数默认使用 base-2（`scipy >= 1.0`）还是 natural log（取决于版本和参数）。建议统一使用 base-2 并在复现指南中修正。

### C2. 三份文档之间存在直接矛盾：归一化方式（softmax vs auto sum-normalization）

**正文**（manuscript.txt:20）明确声明：
> "each vector is normalized to a probability distribution before JS divergence computation via softmax normalization (p_i = exp(x_i) / Σ exp(x_j))"

**补充材料**（supplementary.txt:16）同样声明使用 softmax。

但**复现指南**（reproducibility.txt:57-71）揭示了实际实现完全不同：
> "In 'auto' mode (the default), the method is selected based on the data range:
> - Non-negative values: sum-normalization (p_i = x_i / sum_j x_j). This is used for all CP10k+log1p-normalized data (mouse, human, brain)
> - Any negative values: softmax ... This is automatically selected for log2-transformed data (TCGA)"

这意味着：
- 小鼠、人类、脑数据集实际使用的是 **sum-normalization**（而非 softmax）
- 仅 TCGA 数据使用 softmax（因为 log2 变换后存在负值）
- 复现指南还声称 "the auto-switching behavior is an implementation detail that has no substantive effect on the results"

这是严重问题。sum-normalization 和 softmax 在数学上有本质区别：
- sum-normalization：p_i = x_i / Σx_j（线性，保持比例关系）
- softmax：p_i = exp(x_i) / Σexp(x_j)（非线性，放大高表达基因的权重）

这两种方法对 JS 散度数值和 ω 的影响不同，不能简单地视为"实现细节"。正文需要如实描述实际使用的归一化方法，并分析其对结果的影响。

**要求**：正文和补充材料必须修正为实际使用的归一化方法（auto 模式）。如果不同数据集使用不同归一化方法，必须明确说明并讨论跨数据集 ω 值的可比性。

### C3. k_f 使用配对差异基因（pairwise DE）引入严重选择偏倚

**问题**：在人类、TCGA 和脑数据集中，k_f 使用"每对细胞类型间差异最大的 top-200 基因"计算 JS 散度（supplementary.txt:49-52, reproducibility.txt:122-127）：

> "Delta <- |mu_A - mu_B| // per-gene absolute expression difference
> I <- indices of top-N genes ranked by descending Delta, excluding H"

这构成了**循环论证/选择偏倚**：先按基因差异排序选出差异最大的基因，再在这些基因上计算差异度量。k_f 本质上是在被保证有最大差异的基因子集上计算的，因此 k_f 几乎必然为高值。这导致：

1. ω = k_f/k_n 几乎必然显著大于 1（因为 k_f 被人为放大）
2. 不同配对之间的 ω 绝对值不可比（因为每对使用的基因集不同，且选择偏倚程度可能不同）
3. 标准度量的负相关可能部分源于此偏倚

文中虽然提到"users should compare ω ranks rather than absolute values across datasets"（manuscript.txt:91），但这只是回避而非解决问题。对于 NAR 方法学论文，这种选择偏倚必须有正式的理论分析或模拟验证。

**要求**：
- 提供零模拟（null simulation）：在已知无差异的合成数据上计算 pairwise DE 模式的 ω，量化选择偏倚的大小
- 比较 global HVG 模式与 pairwise DE 模式的 ω 分布差异
- 明确在何条件下 pairwise DE 模式的 ω 可用于跨配对比较

### C4. 大规模多重比较完全缺乏 FDR 校正

**问题**：Tabula Sapiens 分析涉及 4,851 对比较，脑图谱分析涉及 31,764 对比较。补充材料明确承认：

> "Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses; all reported P-values are raw bootstrap P-values." (supplementary.txt:24)

> "FDR correction (Benjamini-Hochberg, q < 0.05) was intended for multi-pair comparisons but was not systematically implemented in the analysis pipeline." (reproducibility.txt:420-421)

在 31,764 对比较中，即使所有零假设为真，在 α = 0.05 下预期约 1,588 个假阳性。不进行多重比较校正意味着报道的 P 值具有严重膨胀的假阳性率。

更严重的是，脑图谱分析的迁移检测模型使用了经验阈值（residual < 0.3, ω < 15 等）而非统计推断，这些阈值没有任何统计学校准或 FDR 控制。

**要求**：
- 所有涉及多重比较的 P 值必须进行 BH-FDR 校正
- 迁移检测模型应建立正式的统计检验框架（如基于置换检验的 FDR），而非仅凭经验阈值

### C5. 正文与复现指南之间关于 Bootstrap 使用的严重矛盾

**正文**（manuscript.txt:22, 43）声明：
> "We randomly permute cell labels between the two populations (B = 1,000 for primary analyses, B = 500 for calibration)"

暗示所有主要分析都使用了 bootstrap。

**复现指南**（reproducibility.txt:399-401, 442-443）揭示：
> "B is not applicable to human/TCGA/brain analyses which do NOT use bootstrap"
> "Bootstrap (human): N/A — human (no bootstrap)"
> "Bootstrap (TCGA): N/A — TCGA (no bootstrap)"
> "Bootstrap (brain): N/A — brain (no bootstrap)"

这意味着仅小鼠试点分析（15 对比较，B = 500）使用了 bootstrap，而人类（4,851 对）、TCGA（~20,000 对）和脑图谱（31,764 对）分析均**没有统计推断**。

正文报道的 P 值和效应量仅来自 n = 6 的对照比较和 n = 15 的小鼠试点。正文中大量声称的统计显著性（如脑图谱分析的 P 值、TCGA 分析的 P 值）要么不存在，要么来源不明。

**要求**：正文必须如实说明哪些分析使用了 bootstrap 推断、哪些没有。对于未使用 bootstrap 的大规模分析，应明确说明结果仅为描述性统计，不涉及统计推断。

---

## 3. Major 问题（强烈建议修改）

### M1. ω = 1 作为中性阈值缺乏数学推导，经验校准样本量过小

CKI 的核心理论主张是 ω ≈ 1 代表中性差异（功能差异与基线差异相当）。但校准实验显示，等价群体的 mean ω = 1.54（median 1.42, range 1.09–2.10），显著偏离 1.0。

问题在于：
1. **没有数学推导**说明为什么 ω = 1 应为中性阈值。在 Ka/Ks 中，ω = 1 有明确的群体遗传学含义（中性进化），因为突变率 μ 在比值中数学上消去。CKI 中没有类似的消去机制——k_n 和 k_f 在不同基因集上计算，没有共享因子可消去。
2. **校准样本量极小**：仅 n = 6 个随机分裂对照。mean ω = 1.54 的置信区间极宽，无法可靠地建立中性基线。
3. **1.54 vs 1.0 的偏差未被解释**：如果理论中性值是 1.0，为什么经验值是 1.54？这 54% 的偏差是否系统性地源于 softmax/sum-normalization 的选择、HK 基因的固有低变异性、或 pairwise DE 的选择偏倚？

**建议**：
- 提供更充分的校准：至少 100-500 次随机分裂实验，建立 ω 的经验零分布
- 从数学上分析：在零假设下（两组来自同一分布），E[ω] 的期望值是多少？由于 k_f 在 HK 基因集上计算时其方差结构与 k_n 不同，E[ω] 不一定为 1
- 考虑使用经验零分布的中位数/均值作为校正因子（如 ω_corrected = ω / ω_null_median），而非直接使用 ω = 1 作为阈值

### M2. Ka/Ks 类比的有效性存在根本性缺陷

作者诚实地承认了 Ka/Ks 类比的局限性（manuscript.txt:89-91），这是值得肯定的。但问题在于，尽管承认了局限性，正文仍在多处使用 Ka/Ks 类比作为核心概念框架（Figure 1a, Introduction, Discussion），这可能误导读者。

关键差异：
1. **Ka/Ks 的数学基础**：Ka = μ × (nonsynonymous sites / total sites) × fixation probability，Ks = μ × (synonymous sites / total sites) × fixation probability。比值 Ka/Ks 中 μ 消去，留下纯粹的适应度信号。这是**比率的核心数学性质**。
2. **CKI 的 ω**：k_n = JS(HK_A, HK_B)，k_f = JS(ID_A, ID_B)。这两个量没有共享的数学因子可在比值中消去。HK 基因和功能基因的方差结构、表达分布、基因数量都不同，因此 k_f/k_n 的比值没有类似 Ka/Ks 的数学简洁性。
3. **Ka/Ks 有明确的统计模型**（如 PAML 的密码子替换模型），CKI 没有对应的概率模型。

**建议**：
- 大幅缩减 Ka/Ks 类比的使用，将其明确限定为"概念启发"而非"数学类比"
- 将 Figure 1a 从"Ka/Ks ↔ CKI 的直接类比"改为"概念灵感来源"的更谦虚表述
- 增加一个专门的"理论局限性"段落，讨论为什么 ω 不具有 Ka/Ks 的数学性质

### M3. k_n 与 k_f 使用不同基因集和不同选择策略使比值解释性受损

在"hybrid scheme"中：
- k_n 使用全局 HK 基因集（同一数据集所有配对共享）
- k_f 使用每配对 top-200 DE 基因（每对不同）

文中声称"since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies"（manuscript.txt:50）。

这一论证有缺陷。JS 散度的值取决于：
1. 概率分布的形状（由基因集决定）
2. 基因集的大小（|H| vs |I|，通常差异巨大）
3. 归一化后的分布特征

在 HK 基因集（~1,100 基因）上计算 JS 散度，和在 top-200 DE 基因上计算 JS 散度，得到的数值不在同一量纲上。虽然两者都是 [0, 1] 范围内的 JS 散度，但其统计分布特性（均值、方差）取决于基因集大小和组成。用比值 k_f/k_n 比较两个不同基因集上的散度，类似于用苹果除以橘子。

**建议**：
- 分析基因集大小对 JS 散度的影响（理论上，更大的基因集在零假设下有更高的 JS 散度期望值，因为维度增加）
- 考虑使用基因集大小校正（如将 JS 散度除以基因集大小的对数，或使用标准化 JS 散度）
- 或改为在同一基因集上计算 k_n 和 k_f（如使用全部 HK 基因计算 k_n，使用排除了 HK 的固定 HVG 集计算 k_f），使两者至少在基因集选择策略上一致

### M4. "CKI 捕获正交信息维度"的论证不充分

正文声称 CKI ω 与四种标准度量负相关（Spearman r = -0.38 到 -0.57）"proving it captures an orthogonal information dimension"（manuscript.txt:52）。

问题：
1. **负相关 ≠ 正交**。正交（independent）意味着相关系数接近 0。r = -0.38 到 -0.57 表示中等程度的负相关，说明 CKI 与标准度量**共享信息但方向相反**。
2. **负相关可能是比值的数学假象**。ω = k_f/k_n。当总体差异增大时，k_f 和 k_n 都倾向于增大（更多基因差异 → 更大的 JS 散度）。但由于 k_n 在分母，当总体差异增大到一定程度，k_n 的增大可能使 ω 反而下降。这种负相关可能纯粹来自比值结构，而非"捕获了独立信息"。
3. 需要控制变量分析：固定 k_n 时 ω 与标准度量的偏相关是多少？固定总体 JS 散度时 ω 与标准度量的关系如何？

**建议**：
- 使用偏相关分析（partial correlation）控制总体差异后，检验 ω 是否与标准度量独立
- 明确修正措辞：将"orthogonal"改为"complementary"或"partially non-redundant"
- 提供理论解释为什么负相关意味着 CKI 捕获了不同的信息，而非数学假象

### M5. 与现有方法的比较不充分

正文将 CKI 与 JS 散度、Spearman 距离、余弦距离、Jaccard 距离四种标准距离度量进行了比较。这在 CKI 作为"距离度量"的定位下是合理的。

但审稿要点要求评估与 scDD、MAST、DESeq2 等方法的比较。这些方法虽然目的不同（差异表达检测 vs 群体距离度量），但方法学论文应讨论 CKI 与这些方法的关系：

1. **与 DE 方法的定位差异**：CKI 是群体级（population-level）距离度量，scDD/MAST/DESeq2 是基因级（gene-level）差异检测方法。文中应明确讨论这一定位差异，解释为什么 CKI 不需要也不应该直接与 DE 方法比较。
2. **可能的整合**：k_f 的 identity 基因选择可以使用 DE 方法的输出（如 DESeq2 的 DE 基因列表），这可以作为 CKI 的扩展。
3. **缺失的比较**：CKI 应与以下同类方法比较：
   - MNN/batch correction 后的距离度量（如 Harmony correction + cosine distance）
   - 其他使用内部归一化的方法（如比率-based 方法）
   - lineage tracing 中的差异度量（如 Waddington-OT 的 transport distance）

**建议**：
- 增加"CKI 与现有单细胞分析方法的关系"段落
- 讨论为什么不与 scDD/MAST/DESeq2 直接比较（定位不同）
- 至少与一种基于校正后的距离度量进行比较（如 Harmony + cosine）

### M6. 持家基因检测策略的合理性评估

当前策略：detection rate > 0.9 + CV < 30th percentile（在 well-expressed genes 中，mean expression > 0.5）。

评估：
1. **detection rate > 0.9 是合理的**，但阈值（0.9）的选择缺乏敏感性分析。建议测试 0.8 和 0.95 的效果。
2. **CV < 30th percentile 的阈值较激进**——取最低 30% 可能包含一些低变异性但生物学上非"持家"的基因（如某些受强烈负调控的细胞类型特异性基因）。更保守的做法是使用 10th 或 5th percentile。
3. **HRT Atlas 参考集的 union 合并**可能引入非持家基因。union 策略意味着 data-driven + reference 的并集，但 data-driven 检测和 reference 集可能有不同的假阳性模式。考虑使用 intersection 而非 union 作为替代方案。
4. **敏感性分析不充分**：文中提到"using the lowest 10% variable genes as a neutral set yielded ω correlations r > 0.95"（manuscript.txt:95），但未提供不同 HK 检测策略（不同 detection rate 阈值、不同 CV 阈值、union vs intersection）对 ω 数值分布影响的系统分析。

**建议**：
- 补充 HK 基因集大小对 k_n 稳定性的敏感性分析（Supplementary Fig. S1a 提到"convergence at ~200-300 HK genes"，但未展示数据）
- 比较 union vs intersection 策略对结果的影响
- 提供 HK 基因集的 GO enrichment 分析，验证检测到的基因确实是持家功能

### M7. 功能基因集选择策略在数据集间不一致

文中存在两种功能基因集选择策略：
1. **Global HVG = 2,000**（小鼠全配对分析, 03_full_matrix.py）
2. **Pairwise top-200 DE genes**（小鼠试点、人类、TCGA、脑）

正文中 mouse calibration 使用 pilot（pairwise DE），但 Figure 2 的 heatmap 使用 full matrix（global HVG）。这两种策略产生不同量级的 ω 值，但在正文中混合呈现时未充分区分。

**建议**：
- 统一策略或在所有结果中明确标注使用的是哪种策略
- 提供 global HVG 与 pairwise DE 两种模式在同一数据集上的 ω 分布比较
- 解释为什么小鼠使用 global HVG 而其他数据集使用 pairwise DE（是计算量考虑还是性能考虑？）

---

## 4. Minor 问题（建议改进）

### m1. 软件版本不一致
- 正文（manuscript.txt:35）："Python 3.12"
- 复现指南（reproducibility.txt:14）："Python: 3.13.12"
- 正文（manuscript.txt:96）："CKI Python package (v0.3.2)"
- 复现指南（reproducibility.txt:22）："Version: 0.3.1"

这些版本号需要统一。

### m2. 数据集细胞数不一致
- 正文（manuscript.txt:24, 26）：Tabula Muris "15,057 cells"；Tabula Sapiens "108,136 cells"
- 复现指南（reproducibility.txt:161, 206）：Tabula Muris "17,957 cells ... before QC"；Tabula Sapiens "108,136 cells (sum across 6 h5ad files)"
- 正文中 Tabula Muris 写的是 post-QC 数量，但复现指南同时给出 pre-QC 和 post-QC，需要确认正文中数字确实是 post-QC 的。

### m3. Tabula Sapiens cell-type 数量不一致
- 正文（manuscript.txt:26）："99 cell-type entries"
- 复现指南（reproducibility.txt:210）："102 cell-type entries"
- 可能是 102 个原始条目经过 QC 后剩 99 个，但需明确说明。

### m4. 正文中提到但未详细描述的"hybrid scheme"
正文多次提到"hybrid scheme"（manuscript.txt:50），但这一术语在 Methods 中首次出现时未给出明确定义。建议在 Methods 中给出正式定义，而非在 Results 中逐步展开。

### m5. 多重模型残差的阈值缺乏统计依据
脑图谱分析中的迁移检测模型使用了经验阈值（Strong: residual < 0.3, ω < 15；Moderate: residual < 0.5, ω < 25；Weak: residual < 0.75, ω < 35）。这些阈值的选择没有统计学依据，建议：
- 使用置换检验建立残差的零分布，以 FDR 控制替代经验阈值
- 或至少提供敏感性分析：不同阈值下 Strong/Moderate/Weak 的数量变化

### m6. softmax 数值稳定性
正文给出的 softmax 公式为 p_i = exp(x_i) / Σexp(x_j)，但未提及数值稳定性处理。对于高表达基因，exp(x_i) 可能溢出。建议在公式中加入 max-subtraction trick：p_i = exp(x_i - max(x)) / Σexp(x_j - max(x))。复现指南提到了这一技巧（reproducibility.txt:63-64），但正文应与之一致。

### m7. ω 上限截断
补充材料提到"omega is capped at 1,000"（supplementary.txt:16）。但正文中人类数据 ω 最大值为 58.69，TCGA 数据中 ω 达到 344.5（BRCA Luminal A），均远低于 1,000。建议说明：
- 在何情况下 ω 会接近 1,000？（k_n 接近 0 时）
- 截断对结果分布的影响

### m8. Bootstrap P-value 公式的双侧检验逻辑
P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)) 这一公式是双侧检验，但需说明：
- 该公式检验的零假设是 H0: ω = ω_null 的中位数（即两组来自同一分布），而非 H0: ω = 1
- 复现指南中另一处（reproducibility.txt:407）给出了不同的 P 值公式：p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)，这一公式检验 H0: ω = 1。两处公式不一致，需统一。

### m9. 引用格式问题
参考文献编号存在跳跃（如正文引用 (13,17) 在 manuscript.txt:74，但参考文献列表中 13 为 Tsai et al. 2016，17 为 Akay et al. 2022）。需检查所有引用编号是否与参考文献列表对应。

### m10. "Brain atlas" 中神经元数据排除的理由
脑图谱分析仅使用非神经元细胞（888,263 核），排除了大量神经元。文中未说明排除神经元的理由。建议补充：是因为神经元区域异质性过高导致 ω 不可解释，还是因为计算资源限制？

### m11. TCGA 分析中 ω 值远高于单细胞数据
TCGA 中 BRCA Luminal A 的 ω 达到 344.5，而 Tabula Sapiens 中最大 ω 仅 58.69。这一数量级差异需要解释：是否因为 bulk RNA-seq 的不同归一化方式（log2(TPM+0.001) vs CP10k+log1p）导致 softmax 输入范围不同，从而系统性影响 ω 值？

---

## 5. 方法创新性评价

### 5.1 核心创新点

**持家基因作为内部基线参考** — 这是 CKI 最核心的创新。将 HK 基因的散度作为"中性基线"，用功能基因散度与之相比，这一思路在单细胞转录组比较分析中是新颖的。现有方法（如 Harmony、scVI 等）主要关注批次校正，而 CKI 提供了一个在已校正数据上量化功能分化程度的框架。**创新性评分：7/10**

**比值结构 ω = k_f/k_n** — 类比 Ka/Ks 的比值结构虽然在数学上不严格等价，但作为概念框架具有启发性。将绝对距离转化为相对于基线的比值，这一"相对化"思路在转录组比较中是新的。**创新性评分：6/10**

**乘法残差模型检测迁移信号** — 在脑图谱分析中，使用 expected_ω = μ_ct × μ_pair / μ_grand 的乘法模型来检测异常低的 ω，这一设计巧妙地同时控制了细胞类型全局可塑性和区域对背景差异。**创新性评分：7/10**

### 5.2 与现有方法的差异化

CKI 的定位是"功能分化度量"（functional divergence metric），而非"细胞类型分类器"（classifier）或"差异表达检测器"（DE detector）。在这一定位下，CKI 确实填补了一个空白：
- 现有距离度量（JS, cosine, Spearman, Jaccard）不区分基线差异和功能差异
- 现有 DE 方法（scDD, MAST, DESeq2）关注基因级差异，不提供群体级距离
- 现有批次校正方法（Harmony, scVI）关注去除批次效应，不量化功能分化程度

CKI 的差异化定位是合理的，但需更清晰地阐述这一定位。

### 5.3 理论深度不足

CKI 目前的理论框架停留在"启发式"层面，缺乏：
1. ω 在不同零假设下的期望值和方差的推导
2. ω 的统计性质（如大样本一致性、渐近分布）
3. 与信息论中其他归一化散度（如 normalized mutual information）的理论联系
4. HK 基因和功能基因的方差结构对 ω 分布的影响

这些理论分析对于方法学论文（尤其是 NAR 级别的方法学论文）是必要的。

### 5.4 总体创新性评分：6.5/10

创新性在概念层面较高（将进化生物学的比值思路引入转录组比较），但在数学理论层面不足（缺乏形式化推导，Ka/Ks 类比不严格）。

---

## 6. 期刊适配度评估

### NAR (Nucleic Acids Research) — 适配度：中等偏低

**优势**：
- NAR 发表过 HRT Atlas（ref 4），与 CKI 使用 HK 基因相关
- NAR 对计算方法的生物学应用广度有要求，CKI 覆盖四个数据集符合

**劣势**：
- NAR 方法学论文要求方法的数学基础扎实，CKI 的理论推导不足
- NAR 对统计严谨性要求高，当前的多重比较缺失和文档矛盾将难以通过审稿
- NAR 更偏向"方法 + 软件工具"的定位，CKI 的软件工程（版本管理、测试覆盖）需加强

**建议**：在解决 Critical 和 Major 问题后，可以考虑投稿 NAR 的 Methods 类别。当前状态不适合直接投稿。

### Genome Biology — 适配度：中等

**优势**：
- Genome Biology 发表过大量单细胞方法学论文（如 scVI、Scanpy）
- 对方法创新性有较高要求，CKI 的概念创新符合
- 对大规模数据应用有偏好，CKI 的四数据集验证符合

**劣势**：
- Genome Biology 审稿严格，对统计严谨性要求极高
- 对方法的实际生物学发现质量有要求，CKI 的脑图谱分析有一定深度
- 对 Ka/Ks 类比的严密性会有更高标准

**建议**：Genome Biology 是 CKI 的合理目标期刊之一，但需在解决统计问题后投稿。

### Briefings in Bioinformatics — 适配度：中等偏高

**优势**：
- 发表过 CACIMAR（ref 22），与 CKI 有领域相关性
- 对方法学论文的理论深度要求相对宽松，更看重实用性和软件可用性
- 对 Ka/Ks 类比的启发性定位更容易被接受

**劣势**：
- 影响因子低于 NAR 和 Genome Biology
- 对生物学发现的深度要求相对较低

**建议**：如果作者希望快速发表，BiB 是较务实的选择。建议作为备选期刊。

### Cell Systems — 适配度：中等

**优势**：
- Cell Systems 重视概念创新和跨领域思路（Ka/Ks → 转录组）
- 对"新概念框架"有偏好，CKI 的相对化距离度量符合

**劣势**：
- Cell Systems 对方法的理论严密性要求极高
- 对数学模型的形式化有要求，CKI 的启发式定位可能不够
- 对生物学发现的深度和实验验证有更高期望

**建议**：除非补充理论推导和实验验证，否则不适合 Cell Systems。

### Bioinformatics — 适配度：中等偏高

**优势**：
- Bioinformatics 是计算方法学的主流期刊
- 对软件工具的可用性和可复现性有明确要求，CKI 已提供开源代码和 Zenodo 存档
- 对方法的数学基础有一定要求但不像 Cell Systems 那样严格

**劣势**：
- 影响因子低于 Genome Biology 和 NAR
- 对生物学应用的深度要求相对较低

**建议**：Bioinformatics 是 CKI 的最务实目标期刊。建议在解决 Critical 问题后优先考虑。

### 综合期刊推荐排序

1. **Bioinformatics**（最务实，适配度最高）
2. **Briefings in Bioinformatics**（备选，对理论要求更宽松）
3. **NAR Methods**（在解决统计和文档问题后可考虑）
4. **Genome Biology**（需大幅加强统计严谨性）
5. **Cell Systems**（需补充理论推导和实验验证，当前不适合）

---

## 7. 总结

CKI 提出了一个概念新颖的转录组比较框架，核心创新在于使用持家基因作为内部基线来归一化功能差异。该方法在四个大规模数据集上展示了应用广度，脑图谱分析中的生物学发现有较好的文献支持。

然而，当前稿件存在以下必须解决的问题：

1. **文档一致性**（Critical C1, C2, C5）：正文、补充材料与复现指南之间存在直接矛盾，严重影响可复现性和方法学可信度。
2. **选择偏倚**（Critical C3）：k_f 使用 pairwise DE 基因引入循环论证，需理论分析和模拟验证。
3. **统计推断**（Critical C4, Major M1）：大规模多重比较缺乏 FDR 校正；ω = 1 中性阈值缺乏数学推导和充分校准。
4. **理论深度**（Major M2, M3, M4）：Ka/Ks 类比的有效性、k_n/k_f 比值的数学性质、"正交信息"的论证均需加强。

在解决上述问题后，CKI 有潜力成为一个有价值的单细胞转录组比较工具。建议作者优先解决 Critical 问题（尤其是文档矛盾和选择偏倚），然后补充理论分析和统计校正，重新投稿。

**最终建议**：Major revision。解决 Critical 问题后重新评估。
