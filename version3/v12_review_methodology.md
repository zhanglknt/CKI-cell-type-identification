# 方法学专家审稿报告 — CKI v12 NAR Submission

## 评分：5.5 / 10

## 总体评价

CKI 提出了一个概念上引人注目的框架：将转录组差异分解为中性偏移率 k_n（来自管家基因）和功能转化率 k_f（来自身份基因），以比值 ω = k_f/k_n 量化选择性转录组重塑。这一思路借鉴分子进化中 Ka/Ks 比值的逻辑，在概念层面具有原创性，填补了转录组比较方法学中"基线归一化功能差异"这一空白。稿件在四个数据集（Tabula Muris、Tabula Sapiens、TCGA、Siletti 脑图谱）上进行了大规模验证，涵盖校准、跨方法比较、癌症分析和脑区分析，工作量和数据覆盖范围令人印象深刻。

然而，从方法学严谨性角度审视，本稿件存在若干需要根本性修正的问题。最突出的问题是稿件内部存在多处自相矛盾的表述——归一化方法（softmax vs. sum-normalization）、Bootstrap 迭代次数（B=500 vs. B=1000）、身份基因选择策略（top-200 vs. top-2000 HVG）、TCGA 数据预处理（TPM vs. FPKM）在不同章节给出了不一致的描述，这直接影响方法的可重复性和可信度。此外，Ka/Ks 类比虽然在概念上具有启发性，但缺少理论支撑使其在定量层面成立：k_n 和 k_f 在不同基因集上计算，缺少 Ka/Ks 中突变率 μ 的自然抵消机制，校准实验中 ω = 1.54（而非理论期望的 1.0）且 TOST 等效性检验未通过，进一步暴露了这一类比的定量缺陷。

混合方案（hybrid scheme）中 k_n 使用全局共享 HK 基因集而 k_f 使用每对细胞类型的 top-200 DE 基因，虽然作者声称比值是"尺度无关的"，但 JS divergence 的值依赖于基因集的维度和分布特征，不同基因集上的 JS 值直接取比值在数学上缺乏严格依据。建议作者在修订中系统性地解决这些问题，并考虑提供更严格的理论推导。

## 关键问题（Critical Issues）

**C1. 归一化方法的内部矛盾**

稿件在不同位置对归一化方法的描述存在直接矛盾：
- Methods（P021）："norm is sum-normalization for non-negative single-cell data (softmax only for TCGA bulk RNA-seq)"
- Results（P042）："apply softmax normalization, which converts expression values to probabilities"
- Supplementary Note 1.1："softmax normalization is applied to convert raw expression vectors into probability distributions"
- Supplementary Note 2（伪代码）："k_n <- JS_divergence(softmax(mu_A_H), softmax(mu_B_H))"

这是无法接受的矛盾。归一化方法直接影响 JS divergence 的值，进而影响 k_n、k_f 和 ω 的所有计算结果。作者必须明确：单细胞数据到底用的是 softmax 还是 sum-normalization？如果是 sum-normalization，为什么伪代码写的是 softmax？如果不同数据集用不同归一化，那么跨数据集的 ω 值是否可比？

**C2. 身份基因选择策略的不一致与混淆**

稿件在不同位置描述了两种截然不同的身份基因选择策略：
- P021："I is the set of the top-200 most differentially expressed genes per cell-type pair (Seurat v3 flavor) excluding HK genes"
- P043："identity genes are the top-2,000 highly variable genes (HVGs; Seurat v3 flavor)"
- P021 同时又说："The choice of 2,000 HVGs follows the Scanpy default parameter"

补充材料澄清了：Tabula Muris 用全局 2000 HVG，Tabula Sapiens 用成对 top-200 DE 基因。但正文从未明确说明这一区别的理由，且在不同章节交替使用"top-200"和"top-2000"，极易造成混淆。更关键的是，200 vs. 2000 的基因集维度差异约 10 倍，JS divergence 在不同维度上的行为不同，这直接影响 k_f 的可比性。

**C3. 校准偏差与等效性检验失败**

核心校准实验显示，同一细胞群体的随机分裂产生的 mean ω = 1.54（而非理论期望 1.0），偏差 +54%。TOST 等效性检验（等效区间 [0.67, 1.50]）在 n=6 时未通过。作者承认这是"operational baseline"的偏差，但辩称不影响相对比较的有效性。

这一论证存在根本缺陷：
- 如果 ω = 1 并不对应"中性"，那么 ω 的绝对值失去了解释力，所有基于 ω 阈值的生物学结论（如脑区分析中的 Strong/Moderate/Weak 分级）都需要重新校准
- n=6 的校准样本量极小，无法支撑"系统性偏移不影响相对比较"的结论——需要更大规模的校准实验
- 偏差方向（ω > 1）暗示 k_n 被系统性地低估，即 HK 基因的分歧度低于"真正中性"的期望，这与作者声称 HK 基因受"稳定选择"的说法一致，但恰恰说明 HK 基因并非中性的良好代理

**C4. 混合方案中 k_n/k_f 可比性的数学基础缺失**

在 Tabula Sapiens 的混合方案中，k_n 使用 ~1000 个全局共享 HK 基因计算，k_f 使用每对的 top-200 DE 基因计算。作者声称"the ratio ω = k_f/k_n is scale-invariant within each JS divergence computation, so the gene set size difference does not bias the result"。

这一声称在数学上不成立。JS divergence = JS(p, q) 的值取决于概率分布 p 和 q 的维度（基因数量）以及各分量的分布形态。一个 200 维分布上的 JS 值与一个 1000 维分布上的 JS 值没有直接的数学可比性。虽然 JS divergence 在 [0,1] 区间有界，但在高维空间中，两个分布的 JS 值会随维度增加而趋向于 1（curse of dimensionality），因此 1000 基因上的 k_n 可能系统性地偏高或偏低，导致 ω 的偏倚。

作者需要：(1) 提供理论推导或模拟实验证明不同维度下 JS 值的比值是无偏的；(2) 或者使用相同维度的基因集计算 k_n 和 k_f。

**C5. TCGA 数据预处理描述的矛盾**

TCGA 数据的预处理在不同位置给出了不一致的信息：
- P027："TPM values, log2(x+1) transformed"
- Supplementary Note 4.3："FPKM values from GDC, followed by log2(x+1) transformation"
- Supplementary Note 1.6："For TCGA bulk RNA-seq data, FPKM normalization is used instead"

TPM 和 FPKM 是不同的归一化方法（TPM 对转录长度归一化后再对总读数归一化，FPKM 的顺序相反），这会导致不同的表达值分布，进而影响 softmax/sum-normalization 后的概率分布和 JS divergence 值。此外，样本数量在不同位置也不一致：P027 列出的总数约 3627，而 Supplementary Note 4.3 列出的数字完全不同（如 LUAD: 495+76 vs 515+59），且声称总计 10,535 样本（实际应为约 3583）。

## 主要问题（Major Issues）

**M1. Ka/Ks 类比的理论基础不足**

虽然作者在 Discussion 中明确承认 CKI 是"heuristic"而非"formal evolutionary selection model"，并指出缺少 Ka/Ks 中突变率 μ 的抵消机制，但正文仍然大量使用"selection"、"constraint"、"neutral"、"selective remodeling"等进化术语。这些术语在 Ka/Ks 框架中有严格的群体遗传学含义，在 CKI 中的使用可能误导读者。

具体问题：
- "ω >> 1 indicates selective transcriptomic remodeling" — 但 ω >> 1 可能仅仅是因为身份基因集的固有变异高于管家基因集，而非"选择"的信号
- "ω << 1 indicates strong transcriptomic constraint" — 稿件自己承认这种情况"in practice"很罕见，但未解释为什么
- 时间尺度问题：Ka/Ks 衡量跨代进化分歧，CKI 衡量共存群体间的横向差异，两者在时间维度上完全不同

建议：要么提供更严格的理论推导将 CKI 与表达进化模型联系起来（如引用并正式引入 Raser & O'Shea 的随机表达模型或类似的群体遗传框架），要么在正文首次使用进化术语时加入更明确的警示，并将"selection"等术语替换为更中性的描述（如"functional divergence exceeding baseline"）。

**M2. 未进行多重检验校正**

稿件在多个分析中进行了大量统计检验但未进行多重检验校正：
- 脑区分析进行了 31,764 次比较
- Tabula Sapiens 进行了 4,851 次比较
- TCGA 分析中多个临床变量在同一数据集内测试

作者在 P038 中承认"all reported P-values are raw, uncorrected values"，但仅以"effect sizes are consistently large"作为辩护理由。对于 31,764 次比较，即使不存在真实信号，在 P < 0.05 阈值下也预期产生约 1588 个假阳性。Strong candidate 的 30 个信号（0.09%）是否可能由随机产生？作者需要：(1) 对主要分析应用 Benjamini-Hochberg FDR 校正；(2) 或提供置换检验（permutation-based FDR）估计假阳性率。

**M3. 负相关作为"独立信息维度"的证据不充分**

CKI ω 与四种标准距离度量的负相关（Spearman ρ = -0.57 到 -0.38）被作为"CKI captures an independent information dimension"的核心证据。但负相关并不等于独立——负相关仍然是一种线性关联。

更关键的是，负相关的机制解释不够充分。作者在 P066 中解释为"populations may share highly expressed genes (high raw similarity), but if their neutral baselines differ, even modest functional divergence produces a high ω"。但这也可以解释为：当两个群体总体上很相似（标准距离低）时，k_n 接近零，导致 ω = k_f/k_n 被放大（除以接近零的数）。换言之，负相关可能是 k_n → 0 时的数值不稳定所致，而非真正的信息正交性。

建议：(1) 分析 ω 与标准度量负相关是否主要由 k_n 接近零的 case 驱动；(2) 在排除 k_n < 0.01 的比较后重新计算相关性；(3) 使用偏相关分析控制 k_n 的影响。

**M4. "同器官 > 跨器官"反转的替代解释未排除**

P054 报告 CKI 是唯一一个"同器官细胞对间 ω 高于跨器官细胞对"的度量（mean ω 16.18 vs. 13.77），并将其解读为 CKI 对"共享微环境中的功能特化"的敏感性。但这一反转有更简单的替代解释：

- 在混合方案中，k_f 使用每对的 top-200 DE 基因。同器官内的不同细胞类型可能在器官特异性基因上高度分歧（因为它们在同一器官中竞争不同生态位），导致 top-200 DE 基因的分歧度更高
- k_n 使用全局 HK 基因集，同器官细胞对间的 HK 基因分歧可能更低（共享微环境），导致分母更小，ω 更大
- 这不是"功能特化"的信号，而是基因选择策略和基线差异的人为产物

建议：使用固定基因集（非成对选择）重新分析，检验"同器官 > 跨器官"反转是否仍然存在。

**M5. 乘法残差模型的阈值缺乏正式零分布**

脑区分析中的乘法残差模型使用经验导出的阈值（Strong: residual < 0.3，对应第 1 百分位；Moderate: < 0.5，第 5 百分位；Weak: < 0.75，第 25 百分位）。作者承认"these thresholds are calibrated on the observed data rather than a formal null distribution"。

虽然补充材料提到置换检验（shuffle region labels）产生了"qualitatively consistent but not identical cutoffs"（Supplementary Fig. S5），但正文未报告置换检验的具体阈值。对于一篇方法学论文，阈值的选择必须有更严格的基础：
- 应报告置换检验的完整结果（每个 tier 的置换 p 值和 FDR）
- 应比较经验阈值与置换阈值的定量差异
- 30 个 Strong 信号中有多少在置换零分布下仍然显著？

**M6. Bootstrap 迭代次数不一致且偏低**

- 正文 Methods（P023）："B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"
- 正文 P038："Bootstrap inference uses B = 500 permutations"
- Supplementary Note 3.2："B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"

B=500 对于构建稳定的 null 分布偏低，尤其是在尾部推断（如 P < 0.001 的声明）时。更关键的是，正文和补充材料的数值不一致，无法确定实际使用了哪个值。建议统一为 B ≥ 1000，并在所有分析中使用一致的迭代次数。

**M7. 与现有方法的比较不够充分**

方法比较仅限于四种标准距离度量（raw JS、Spearman、cosine、Jaccard）。缺少以下比较：
- **Wasserstein distance**（earth mover's distance）：在单细胞领域有广泛应用，且作为分布度量与 JS divergence 有理论联系
- **PCA-based distance**：在高维数据降维后计算距离是常见做法
- **MAST/DESeq2 差异表达统计**：CKI 的 k_f 基于 DE 基因，应与标准 DE 分析方法的输出比较
- **转录组漂移分析（Transcriptional drift）**：作者在 Discussion 中提到了这一框架但未进行定量比较

此外，AUC 比较存在不公平性：CKI 的 k_f 使用 200 个成对 DE 基因，而标准度量使用全部 ~20,000 基因。虽然作者在 P054 中承认了这一点并做了限制基因集后的比较（cosine AUC 从 0.887 降到 0.752），但未对其他度量做同样的限制。

## 次要问题（Minor Issues）

**m1. TCGA 样本数量不一致**
P027 与 Supplementary Note 4.3 中各癌种的 tumor/normal 样本数不同（如 LUAD: 495+76 vs 515+59），且 Supplementary 声称总计 10,535 样本（实际约 3583）。需要核实并统一。

**m2. ω 上限截断（capping at 1000）未在正文中说明**
Supplementary Note 1.1 提到"omega is capped at 1,000"，但正文从未提及这一截断。截断会影响高 ω 值的统计分布和解读。需在 Methods 中明确说明，并报告有多少比较被截断。

**m3. 跨物种 k_n 不可比**
Mouse 校准中 k_n 中位数 = 0.0019，而 Human 数据中 k_n 范围 0.0147–0.0166，相差约 10 倍。这暗示跨物种的 ω 值不直接可比，但稿件在 Discussion 中未讨论这一问题。

**m4. 随机种子验证不充分**
P036 声称"Stability across random seeds was verified for key results; full multi-seed validation was not performed"。仅固定 seed=42 并进行部分验证不足以支撑大规模分析的可重复性声明。建议至少对关键结果进行 5 个随机种子的验证。

**m5. 术语使用不够统一**
稿件中"k_n"在不同位置被称作"neutral offset rate"、"neutral drift rate"和"neutral baseline"；"k_f"被称作"functional conversion rate"和"functional divergence"。建议统一术语。

**m6. 脑区分析中 OPC 阴性对照的逻辑循环风险**
P077 声称 OPCs（最活跃的迁移细胞）产生 0 个 Strong 信号是方法特异性的验证。但作者也承认 OPCs 的高全局 ω（7.65）提高了检测阈值。这意味着对于高 ω 细胞类型，模型天然不敏感——这不是"特异性"而是"敏感性不足"。需要更仔细地区分特异性和敏感性。

**m7. TCGA 分析中 bulk RNA-seq 的局限未充分讨论**
TCGA bulk RNA-seq 反映组织级平均，包含多种细胞类型。NN/TT > 1 的发现可能完全由肿瘤微环境（免疫浸润、基质组成）的趋同变化驱动，而非恶性细胞本身。虽然作者在 P056-057 中提及了这一点，但未进行去卷积分析来排除这一混淆。

**m8. 部分句子在全文中不完整**
正文中存在多处被截断的句子（如 P054 末尾"... [truncated]"、P077"... [truncated]"、P079"... [truncated]"、P085"... [truncated]"、P093"... [truncated]"、P097"... [truncated]"）。虽然可能是排版问题，但需要确保正式投稿版本中无遗漏。

## 优点（Strengths）

1. **概念创新性突出**：将 Ka/Ks 的"中性基线归一化"逻辑引入转录组比较领域是一个新颖且有启发性的思路，填补了现有距离度量无法区分"功能性差异"与"背景噪音"的空白。

2. **验证规模宏大**：跨四个大规模数据集（Tabula Muris 15K 细胞、Tabula Sapiens 108K 细胞、TCGA 3596 样本、Siletti 888K 核）进行验证，数据覆盖范围和方法的应用广度令人印象深刻。

3. **敏感性分析较为全面**：对 HK 基因集大小（250-1000）、HVG 数量（1000-4000）、基因选择策略（identity-only vs. pathway-enhanced）进行了参数扫描，并报告了 ω 的稳定性。

4. **OPC 阴性控制设计巧妙**：利用 OPCs 作为"最活跃迁移细胞"的阴性对照，验证乘法残差模型不单纯检测迁移能力，这一设计在方法学上值得肯定。

5. **局限性的自我认知较好**：作者在 Discussion 中坦诚讨论了多个局限性（pseudobulk 限制、HK 基因的"中性"假设、TCGA bulk 限制、Warburg 效应干扰等），这种自我批判态度在方法学论文中是可贵的。

6. **代码和数据公开**：Python 包和所有分析脚本在 GitHub 上公开（MIT License），Zenodo 存档，有利于可重复性。

7. **生物学解读有深度**：脑区分析中区分了发育起源异质性、定植路线边界和出生后迁移三种机制，并将 Strong 信号系统性地与发育神经科学文献交叉验证，这种"计算-实验"交叉验证的思路值得提倡。

## 具体修改建议

### 针对 Critical Issues

**C1 修改建议**：
- 在 Methods 中用一段统一描述归一化策略，明确说明单细胞数据使用 sum-normalization（理由：非负计数数据天然适合归一化为概率分布），TCGA bulk 数据使用 softmax（理由：log 变换后可能出现负值）
- 修正 Supplementary 中的伪代码，确保与正文一致
- 补充说明：为什么 softmax 用于 log-transformed 数据是合理的（softmax 对 log 值的指数化等价于对原始值的归一化，但这需要在文中明确论证）

**C2 修改建议**：
- 在 Methods 中明确列出两个数据集使用不同身份基因选择策略的原因（如："Tabula Muris 仅 32 个细胞类型，全局 HVG 足以区分；Tabula Sapiens 有 99 个细胞类型，全局 HVG 会稀释成对信号，因此使用成对 top-200 DE 基因"）
- 补充交叉验证：在 Tabula Sapiens 上也用全局 2000 HVG 计算一次 ω，与成对 200 DE 基因的结果比较，报告相关性
- 在全文中统一使用"global HVG scheme"和"pairwise DE scheme"来区分两种策略

**C3 修改建议**：
- 扩大校准样本量：至少在 Tabula Muris 的全部 32 个细胞类型上各进行 10 次随机分裂（共 320 次），报告 ω 的分布
- 报告 TOST 在更大样本量下的结果
- 考虑引入"校准因子"（calibration factor）：将 ω 除以校准实验的 mean ω（如 1.54），使校准后的 ω' ≈ 1 对应中性
- 在脑区分析等基于 ω 阈值的分析中，使用校准后的 ω' 重新确定阈值

**C4 修改建议**：
- 提供理论推导：在两个不同维度（m 维和 n 维）的概率分布上，JS divergence 的期望值如何随维度变化？
- 进行模拟实验：生成已知差异度的合成数据，在不同基因集维度下计算 JS 值的比值，验证比值是否有偏
- 最稳妥的修改：使用相同维度和相同选择策略的基因集计算 k_n 和 k_f（例如都使用全局 HK 基因和全局身份基因，或都使用成对 top-N 基因但分别从 HK 池和 non-HK 池中选取）

**C5 修改建议**：
- 核实 TCGA 数据实际使用的是 TPM 还是 FPKM，统一全文描述
- 核实各癌种的真实样本数，修正 Supplementary 中的总数计算错误
- 在 Methods 中补充说明从 GDC 下载的数据处理流程（包括是否使用 GDC 的 HTSeq-TPM 还是 HTSeq-FPKM）

### 针对 Major Issues

**M1 修改建议**：
- 在 Introduction 首次引入 Ka/Ks 类比时（P016），加入一段明确的边界声明："The analogy is conceptual, not mathematical: Ka/Ks derives its power from a shared mutation rate μ that cancels in the ratio, while CKI's k_n and k_f are computed on different gene sets without an analogous cancellation mechanism."
- 在 Results 的所有结论性陈述中，将"selective remodeling"替换为"functional divergence exceeding baseline"或类似中性表述
- 在 Discussion 中增加一段正式讨论 CKI 与 expression evolution models（如 Raser & O'Shea 2005 的随机表达模型、Berg & Lässig 2003 的适应度景观模型）的理论联系

**M2 修改建议**：
- 对 Tabula Sapiens 的 4,851 比较和脑区分析的 31,764 比较分别应用 BH-FDR
- 报告 FDR 校正后仍然显著的比较数量
- 对脑区 Strong 信号（30 个）报告置换检验 FDR 估计的假阳性数

**M3 修改建议**：
- 分层分析：将 4,851 对按 k_n 分为低（k_n < 0.01）、中（0.01-0.05）、高（>0.05）三组，分别计算 ω 与标准度量的相关性
- 报告排除 k_n < 0.01 后的 ω-标准度量相关性
- 使用偏相关分析控制 k_n 的影响后，检验 ω 是否仍与标准度量负相关

**M4 修改建议**：
- 使用全局固定基因集（如全局 top-2000 HVG 中 non-HK 部分）重新计算 Tabula Sapiens 的 ω
- 检验"同器官 > 跨器官"反转是否仍然存在
- 如果反转消失，说明该信号由成对基因选择策略驱动，需在文中明确讨论

**M5 修改建议**：
- 在正文报告置换检验的完整结果：每个 tier 的置换 p 值和 FDR
- 报告经验阈值与置换阈值的定量比较
- 对 30 个 Strong 信号逐一报告置换显著性

**M6 修改建议**：
- 统一 B 值：所有分析使用 B = 1000（或更高）
- 修正正文与补充材料的不一致
- 对关键 P 值（如 P < 0.001 的声明）报告 B = 1000 下的置信区间

**M7 修改建议**：
- 增加与 Wasserstein distance 的比较
- 对所有标准度量在限制到相同 200 DE 基因后重新计算 AUC，进行公平比较
- 增加 CKI 与转录组漂移分析的定量比较
- 讨论 CKI 与差异表达分析（如 Wilcoxon rank-sum test on DE genes）的关系：CKI 的 k_f 本质上是在 DE 基因上度量分布差异，与标准 DE 分析有何本质区别？

---

**总结**：CKI 的核心概念具有创新性和生物学意义，验证工作覆盖面广，但方法学层面存在多处需要修正的关键问题——尤其是归一化方法的自相矛盾、基因选择策略的不一致、混合方案中 k_n/k_f 可比性的数学基础缺失，以及校准偏差未充分解决。建议作者进行 Major Revision，重点解决上述 Critical 和 Major Issues。修订后的稿件如果能够：(1) 统一并明确所有方法描述，(2) 提供 k_n/k_f 跨基因集可比性的理论或模拟证据，(3) 扩大校准实验规模并引入校准因子，(4) 对主要分析进行多重检验校正，则有潜力成为该领域的有价值贡献。
