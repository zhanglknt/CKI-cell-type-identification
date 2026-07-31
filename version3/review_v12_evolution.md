# 分子进化概念审稿报告 — CKI v12

**审稿人专业方向**: 分子进化生物学、选择压度量、进化速率比较

**审稿日期**: 2026-07-26

---

## 评分: 6.5/10

**评分依据**: 作者对该类比的局限性有较好的自我认知和诚实披露（值得肯定），但概念框架的核心缺陷——缺乏消除共享速率因子的机制——使得这一类比在理论上是不完整的。该指标作为"基线归一化功能分歧指数"是有价值的，但作为"选择压"度量的理论依据不足。已发表前提下适用 4-5/10；若允许明确降级为启发式指标而非进化选择模型，可达 7/10。

---

## 1. Critical Issues（阻断发表的问题）

### 1.1 CKI ω 的比率消除机制缺失——与 Ka/Ks 的本质差异

这是 CKI 框架中最根本的概念缺陷。在分子进化中，Ka/Ks 比率之所以具有理论优雅性，是因为存在一个**共享突变率 μ** 在分子和分母中精确消除：

```
Ka/Ks = (μ × f_K(N_e, s)) / (μ × f_S(N_e, s)) = f(N_e, s)
```

同义位点和非同义位点经历完全相同的突变过程，共享相同的 μ，因此比率仅保留选择信号。这是 Ka/Ks 作为"选择压纯洁信号"的理论基础（Kimura 1983; Yang & Nielsen 2000）。

CKI 中的比率 ω = k_f/k_n **不享有类似的消除机制**。k_f 和 k_n 在不同的基因集合上计算，具有不同的基线分歧特性：
- k_n 基于管家基因（~1000 个基因，低方差）
- k_f 基于身份基因（~200 个差异表达基因，高方差）

不存在一个在分子和分母中可消除的共享"漂变率"。因此，CKI ω = 1 不具备任何群体遗传学意义上的中性解释。作者在 Discussion 中承认了这一点，但这一定性确认意味着"选择压"的核心类比在理论上是**断裂的**。

**建议**: 
- 明确将 CKI 降级为一个"基线归一化功能分歧指数"（baseline-normalized functional divergence index），而不是"选择压"指标
- 在标题、摘要和所有核心论点中反映这一降级
- 删除或大幅弱化所有直接的 Ka/Ks 类比，改为"在逻辑上受启发于"更弱的表述

### 1.2 "选择"概念的范畴错误（category error）

分子进化中的"选择"作用于可遗传的序列变异，通过差异繁殖成功率在世代间传递。这是严格定义的达尔文选择。CKI 将其扩展到：

- **体细胞时间尺度**（细胞分化和状态转换）
- **不经过孟德尔遗传**的转录组差异
- **不依赖差异繁殖**的表达模式变化

这不是一个延伸，而是一个范畴错误。不同细胞类型之间的转录组差异反映的是**发育程序执行**和**环境响应**，而不是达尔文意义上的自然选择作用。即使用"隐喻"包装，这一概念的跨域移植在生物学上是站不住脚的。

作者在 Introduction 中陈述："Throughout this paper, we use evolutionary terminology ('selection', 'constraint', 'neutral') as heuristic metaphors for transcriptomic divergence patterns, not as claims about Darwinian selection on gene expression." 这一免责声明虽然诚实，但并未解决范畴错误——称一个指标为"选择索引"（selective index），同时又说它不衡量选择，这在逻辑上自相矛盾。

**建议**: 
- 完全重构术语体系，放弃"选择"语言
- 使用"功能分歧率"（functional divergence rate）替代"选择压"
- 使用"基线约束"（baseline constraint）替代"纯化选择"
- 使用"增强分歧"（enhanced divergence）替代"正选择"

---

## 2. Major Issues（需要重大修改）

### 2.1 管家基因作为"中性位点"的类比基础不充分

方程:
```
k_n = JS(norm(ε_A[H]), norm(ε_B[H]))
```
中，H 基因集被类比为同义位点，但二者之间存在根本差异：

| 特性 | 同义位点 (Ka/Ks) | 管家基因 (CKI) |
|------|-------------------|----------------|
| 中性来源 | 遗传密码的简并性 | 操作定义（低方差） |
| 中性证据 | 数学确定（第三位点摇摆） | 经验观察（高检测率+低CV） |
| 是否可能受选择 | 部分位点可能与剪接调控偶联 | 极可能受稳定化选择 |
| 理论纯净性 | 高（遗传密码是硬约束） | 低（低方差可能 = 强功能约束） |

作者注意到底这一点（"HK genes may still be subject to stabilizing selection on expression levels"），但低估了其后果。最需要担心的情形是：如果某些细胞谱系中的管家基因确实处于稳定化选择之下，k_n 将低估真实的"中性"基线，导致 ω 系统性膨胀。这与校准实验中观察到的均值 ω = 1.54（而非 1.0）的情形一致，提示该偏移可能不是随机分布。

作者进行了 HK 基因集大小的敏感性分析（250-1000 个基因，CV < 13% 对于 99.2% 的配对），但这一分析仅测试了**稳健性**而非**准确性**——它证明 ω 在 HK 基因集大小变化时保持稳定，但并未证明 k_n 捕捉的是真正的中性变异，而非保守性地高估的纯化约束水平。

**建议**:
- 增加一项分析：将 k_n 与仅使用**最低表达方差**基因（例如底部 5%、10%、20%）计算的基线分歧进行比较，以直接测试低方差基因是否确实产生沿所有比较轴一致的"中性"基线
- 讨论管家基因普遍受到强烈稳定化选择的大量文献（Duret & Mouchiroud 2000; Zhang & Li 2004），并解释为什么这不使 CKI 的类比失效
- 提供 HK 与非 HK 基因之间表达分歧与功能约束强度关系的定量评估

### 2.2 身份基因作为"非同义位点"类比的合理性存疑

在分子进化中，非同义位点是结构上定义的：它们是改变氨基酸的任何核苷酸位点。这是一个精准的二进制划分（同义/非同义），由遗传密码决定。

CKI 的"身份基因"是操作上定义的：通过 Seurat v3 风味选择的 top-200 差异表达基因。这带来几个问题：

**(a) 基因集合的上下文依赖性**: 在 Ka/Ks 中，同义/非同义分类仅依赖参考序列，而非所比较的两个序列。CKI 的身份基因集合依赖于所比较的**特定细胞类型配对**——不同配对的"身份基因集"不同。这意味着"受选择位点"的内容在每次比较中都会改变，这将违反选择压推断的核心假设：所有比较应使用同一组"位点"。

**(b) 表达差异 ≠ 功能重要性**: DE 分析识别的是**统计上差异最大**的基因，而非**功能上最重要**的基因。一个转录因子可能表达量很低、在 DE 分析中排名靠后，但对细胞身份的建立至关重要。一个高表达的结构蛋白可能被选入 top-200，但该蛋白对两个细胞类型的功能差异贡献甚微。

**建议**:
- 区分"统计学上差异显著"与"功能上重要"的概念
- 考虑基于先验生物学知识的功能基因集替代方案（GO 注释、转录因子数据库等）
- 讨论为何 k_f 排除了 HK 基因但包括许多其他类别的广泛表达基因，这种做法是否会在某些比较中产生偏差

### 2.3 ω 值的三区解释缺乏严格的理论支撑

经典 Ka/Ks 分析提供三个定义明确的状态：
- ω < 1: 纯化选择（s < 0, 即有害突变被移除）
- ω ≈ 1: 中性进化（s = 0）
- ω > 1: 正选择（s > 0, 即有益突变被固定）

CKI 采用了相同的三分法，但作者在 Discussion 中坦言："ω = 1 in CKI carries no population-genetic interpretation of neutrality." 如果 ω = 1 不意味着任何群体遗传学意义上的状态，那么 ω < 1 和 ω > 1 也不能按照 Ka/Ks 的传统方式进行解释。但整个稿件（Fig. 1-6）都隐含地采用了这种三分法。

校准数据进一步证实了这一担忧：等效群体的平均 ω = 1.54（而非 1.0），且 TOST 等效性检验未确认严格等效。这意味着该方法的"中性"基线被系统性高估，所有下游解释都基于一个偏移的参考点。

此外，ω 分布的极右偏态（中位数 13.68 vs. 均值 14.12；56.3% 的值 < 15）意味着许多比较产生极端比率。对于一个在 ~15 处"中性"的比率（例如 k_f = 0.03, k_n = 0.002）与一个在 ~15 处真正偏离 "基线" 的比率（例如 k_f = 0.3, k_n = 0.02），其生物学解释完全不同——但 ω 值对这些差异视而不见。这一点在稿件中未做足够探讨。

**建议**:
- 为 ω 值的统计显著性和生物学意义开发独立的阈值（如基于置换的显著性截断值）
- 用实证校准替换三分法阈值：ω_obs/ω_null > X 为"增强分歧"，ω_obs/ω_null < 1 为"约束"
- 报告 ω 时应始终同时报告 k_f 和 k_n，以防止高 ω 值由接近零的 k_n 驱动

### 2.4 与基因表达进化理论的衔接严重缺失

本稿件最突出的文献空白是缺乏与**基因表达进化**理论的衔接。半个多世纪以来，分子进化生物学已经发展了成熟的框架用于分析基因表达水平上的选择和约束，但该稿件对这些工作基本没有引用。

**(a) 表达水平的稳定化选择**: 已有丰富文献证明基因表达水平受到强烈的稳定化选择（Lemos et al. 2005; Bedford & Hartl 2009; Gilad et al. 2006; Romero et al. 2012）。这一发现对 CKI 有直接影响：如果所有基因（包括管家基因和身份基因）的表达水平都受到某种程度的稳定化选择，那么 k_n 和 k_f 均已包含"纯化"信号，ω 不能简单解释为选择性重塑。

**(b) Ornstein-Uhlenbeck (OU) 模型**: 在比较生物学中，OU 模型是量化跨物种性状（包括基因表达）选择强度的标准工具（Butler & King 2004; Rohlfs & Nielsen 2015; Chen et al. 2019）。OU 模型包含一个选择强度参数 α，直接衡量表型被拉向最优值的力度——这与 CKI ω 声称要捕获的概念几乎完全相同，但方法更严谨。

**(c) 表达进化速率**: 已有多种方法量化基因表达分歧速率（Khaitovich et al. 2005; Brawand et al. 2011），包括区分顺式和反式调控贡献（Wittkopp et al. 2004）。CKI 与这些方法的关系完全没有被讨论。

**建议**:
- 增加专门讨论 CKI 与:
  - OU 过程框架（为什么 CKI 比拟合 OU 模型更简单或更优？）
  - 表达水平的稳定化选择（CKI ω 与选择强度如何关联？）
  - 跨物种表达分歧度量（CKI 在系统发育框架中的适用性如何？）
- 至少在 Discussion 中增加 1-2 段内容，承认这些成熟的进化框架并为 CKI 在与它们比较时的定位提供比较

### 2.5 CKI ω 与标准指标的负相关解释不充分

CKI 的核心卖点是与所有四种标准距离指标的负相关（Spearman r = -0.57 至 -0.38）。作者将这一负相关解释为"CKI 捕获了正交信息维度"。然而，存在更简洁的解释：

当 k_f > k_n 时，ω = k_f/k_n 较大；如果 k_n 的变异主要由高表达基因驱动（这些基因也贡献了 JS 散度等原始距离指标的大部分信号），那么：
- 原始 JS 散度 ≈ k_all（所有基因），大致正比于 k_n + k_f
- CKI ω = k_f/k_n
- 因此 ω 与原始 JS 散度成**反函数关系**——这不是一个独立的信息维度，而是对相同底层数据在一个方向上做了不同的重新加权

需要直接检验这一反函数的解释，例如通过计算 ω 与 1/(原始 JS) 的偏相关，或基于 k_f 和k_n 随机置换生成零相关分布。

**建议**:
- 通过 bootstrap 置换验证负相关是否由一个数学恒等式（而非独立生物学信号）驱动
- 进行偏相关分析：控制 k_n 后，ω 是否真的捕获了 k_f 中不被 k_n 解释的独立成分？
- 讨论 CKI 在多大程度上是对相同基础信息的一个加权视角（weighted perspective），而非一个真正独立的信息维度

---

## 3. Minor Issues（建议修改）

### 3.1 术语学的一致性

- 稿件交替使用"selection"、"functional divergence"、"selective remodeling"，暗示三种不同程度的概念承诺。"functional divergence"（功能分歧）在生物学上没有争议，但在和 Ka/Ks 做类比的部分又不够强。
- **Line 31**: "CKI as a heuristic transcriptomic analogue" —— "heuristic" 和 "analogue" 之间的张力贯穿全文。建议在 Introduction 末尾统一并明确声明 CKI 在何种意义上是（或不是）Ka/Ks 的类比。

### 3.2 "转录组重塑"与发育可塑性的混淆

稿件使用"transcriptomic remodeling"（转录组重塑）一词，主要是在比较不同细胞类型的稳态转录组。但这些差异大部分反映了发育分支点上的分化决策，而非"重塑"（remodeling，暗示对已有状态的积极重编程）。建议在非扰动上下文中使用"transcriptomic divergence"或"differentiation"，保留"remodeling"用于扰动/疾病分析等场景（如 TCGA 分析）。

### 3.3 缺少对替代框架的引用

稿件自称："CKI provides a principled null model for any transcriptomic comparison." 但在讨论中未引用与 CKI 最接近的现有方法：
- 表达数量性状位点（eQTL）分析：使用局部遗传变异作为"中性"基线来测试表达水平的遗传控制
- 转录漂变（Transcriptional drift）框架（Zou et al. 2022, 已引用但整合有限）：量化衰老和疾病中表达噪声的年龄相关积累，可作为 k_n 概念的自然延伸
- 管家基因作为参考基因的广义使用：qPCR 和其他表达定量方法中早已将管家基因作为内部参考；CKI 将这一思想扩展到了组学规模

### 3.4 跨物种适用性讨论不足

既然类比分子进化中的跨物种比较，CKI 是否适用于跨物种细胞类型比较？这似乎是一个自然的延伸。如果 CKI 能用于比较人类和鼠类 B 细胞，它将更直接地映射到 Ka/Ks 的比较框架。但稿件中未讨论这一可能性。至少在 Discussion 中提及并说明为什么当前版本不支持跨物种分析将是合乎逻辑的。

### 3.5 "细胞状态动力学索引"的命名

"CKI: Cell-state Kinetic Index" 中的 "Kinetic" 一词提示时间动态过程。但 CKI 分析的是稳态细胞类型/状态，而非动态过程。该名称可能对预期进行动力学分析的读者产生误导。建议改为 "Cell-state Comparative Index" 或 "Cell-state Divergence Index"。

### 3.6 多次出现的小的技术错误

- **Line 45**: "B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration" — 重复语句
- **Line 59**: "top-200 expressed genes" — 第 40 行描述为 "top-200 most differentially expressed genes"，表述不一致
- **Line 121, 123**: 内皮细胞的矛盾描述——第 121 行称内皮细胞"最低保守性"（ω = 15.09），但紧接着说"表现出最强的功能约束……无论解剖位置如何维持高度保守的转录程序"。这两个句子相互矛盾，需修正。

---

## 4. 概念创新亮点

尽管存在上述严重问题，该稿件也具有几个值得认可的概念贡献:

1. **基线归一化的思想是优雅的**: 使用内部参考基因集来归一化分歧度量的想法在直觉上是合理的，与 qPCR 归一化中管家基因的传统用法相呼应，但被提升到了全转录组规模。这与 Ka/Ks 的数学精确性无关，而是一种不同的、操作性的优雅。

2. **k_n/k_f 分解回答了真实的生物学问题**: 无论"选择"的类比是否成立，将转录组分歧分解为"基线"（所有细胞共享的变异）和"功能"（身份基因特异的变异）两个组分，是对现有"总分歧"指标的有意义改进。

3. **负相关发现虽然可能存在数学解释，但很有趣**: CKI ω 与所有标准指标的负相关如果得到充分验证（而非仅仅作为数学产物），将代表一个真正的概念性贡献——即某些比较轴上的度量行为发生了颠倒。

4. **脑区分析展示了生物学效用**: 大脑分析中区分发育起源特征与活跃细胞迁移的能力展示了该方法的实用价值，与数学框架的有效性相互独立。

5. **诚实的自我披露**: 作者在 Discussion 中对类比的局限性和 CKI 的非正式性质进行了坦率的讨论，这在计算生物学领域中并不常见，应该被认可。第 185-186 行的讨论尤为全面。

---

## 5. 总体建议

### 5.1 发表建议: **重大修改后考虑发表（Major Revision）**

我建议给予"重大修改"而非"拒绝"的机会，原因如下：
- 该方法作为**基线归一化功能分歧指数**具有实用价值，四个数据集的验证表明了其效用
- 作者对类比的局限性有良好的自我认知（Discussion 第 185-186 行）
- 大脑分析中的应用展示了超越概念类比的实际生物学洞察

但发表必须以**实质性重新构思**概念框架为条件。

### 5.2 核心修改要求

1. **降级类比声明**: 从"Ka/Ks 的转录组类比"正式降级为"Ka/Ks 的逻辑启发式基线归一化方法"。术语应从"选择"体系转向"分歧"体系。

2. **解决表达进化理论衔接**: 必须增加有质量的内容，讨论 CKI 与基因表达进化领域已建立的框架之间的关系（OU 模型、表达水平稳定化选择、跨物种分歧度量）。

3. **校正 ω 值解释**: 放弃从 Ka/Ks 移植过来的三分法（ω<1/≈1/>1），建立基于实证的显著性检验框架（如 ω_obs 相对于 ω_null 分布的效应大小）。

4. **明确标志使用警告**: 在每处出现 CKI ω 值的图注中添加一句话："CKI ω 不是'选择压'的形式度量。值反映的是基线归一化功能分歧——较高值指示功能基因分歧超出基线，而非正达尔文选择。"

### 5.3 如果以上修改不可行

如果作者不愿意降级类比或重写术语体系，则该稿件应按其当前表述被评判——即"选择性转录组重塑的指标"——并以理论依据不充分为由**建议拒稿**。在当前范式下，核心的范畴错误无法通过增加验证数据或校准来解决。

---

## 参考文献（审稿人建议补充）

- Bedford T, Hartl DL (2009) Optimization of gene expression by natural selection. *PNAS* 106:1133-1138.
- Brawand D et al. (2011) The evolution of gene expression levels in mammalian organs. *Nature* 478:343-348.
- Butler MA, King AA (2004) Phylogenetic comparative analysis: a modeling approach for adaptive evolution. *Am Nat* 164:683-695.
- Chen J et al. (2019) A quantitative framework for characterizing the evolutionary history of gene expression. *Genome Res* 29:53-63.
- Duret L, Mouchiroud D (2000) Determinants of substitution rates in mammalian genes: expression pattern affects selection intensity but not mutation rate. *Mol Biol Evol* 17:68-74.
- Gilad Y et al. (2006) Expression profiling in primates reveals a rapid evolution of human transcription factors. *Nature* 440:242-245.
- Khaitovich P et al. (2005) Parallel patterns of evolution in the genomes and transcriptomes of humans and chimpanzees. *Science* 309:1850-1854.
- Lemos B et al. (2005) Rates of divergence in gene expression profiles of primates, mice, and flies: stabilizing selection and variability among functional categories. *Evolution* 59:126-137.
- Rohlfs RV, Nielsen R (2015) Phylogenetic ANOVA: the expression variance and evolution model for quantitative trait evolution. *Syst Biol* 64:695-708.
- Romero IG et al. (2012) Comparative studies of gene expression and the evolution of gene regulation. *Nat Rev Genet* 13:505-516.
- Wittkopp PJ et al. (2004) Evolutionary changes in cis and trans gene regulation. *Nature* 430:85-88.
- Zhang L, Li WH (2004) Mammalian housekeeping genes evolve more slowly than tissue-specific genes. *Mol Biol Evol* 21:236-239.

---

*审稿人声明: 无利益冲突。*
