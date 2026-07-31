# CKI 算法方法学审稿报告

**审稿人**: methods-reviewer
**审稿版本**: v10 (NAR Manuscript)
**审稿日期**: 2026-07-26

---

## 1. 总体评价

**综合评分: 6/10**

CKI 提出了一个有启发性的概念框架——将转录组差异分解为"中性基线"和"功能转换"两个分量，借鉴 Ka/Ks 的比值思路。作者在 Discussion 中坦诚地承认了 CKI 与 Ka/Ks 的本质差异（缺乏突变率的抵消机制、HK 基因并非真正中性），这种科学诚实性值得肯定。代码实现质量较高，API 设计清晰，文档完善。

然而，方法学上存在几个关键问题：(1) Hybrid 方案中 k_n（全局、固定基因集）与 k_f（逐对、不同 DE 基因集）的比值在数学上不一致，导致 ω 跨配对不可直接比较；(2) Softmax 归一化后计算 JS 散度的生物学含义不清晰；(3) k_n 下限阈值在稿件（0.001）与代码（1e-4）之间存在不一致；(4) Ka/Ks 类比虽在 Discussion 中被"去神话化"，但在 Abstract/Introduction/Figure 1 中仍作为核心卖点，存在过度包装风险。

---

## 2. 方法创新性评估

**创新性评分: 7.5/10**

### 2.1 概念创新
- **将 Ka/Ks 思路引入转录组比较**：这是一个有价值的 conceptual contribution。尽管类比不完美（作者已承认），"用低变异基因集作为内参基线"的思路本身是合理且有启发性的。
- **转录组差异的可分解性**：CKI 是目前唯一能将成对相似度显式分解为 neutral（k_n）和 functional（k_f）分量的度量，这一点在 Figure 3D 中清晰展示，是真正的差异化卖点。
- **乘法残差模型**（brain 分析）：用于检测异常低 ω 的细胞类型/区域对组合，设计巧妙，OPC 阴性对照（0 个 Strong 信号）提供了正交验证。

### 2.2 技术创新
- **HK 基因自动检测**（detection rate + CV）：数据驱动、跨物种可用，减少了对外部参考数据库的依赖，是一个工程亮点。
- **Bootstrap 置换检验**：标准的细胞标签置换 + +1 伪计数 P 值，实现规范。
- **多模式功能基因选择**（HVG / markers / pairwise_de）：灵活性好，但默认 HVG 模式的生物学合理性存疑（见下）。

### 2.3 与现有方法的关系
- 与 transcriptional drift analysis [37] 的关系：作者明确指出两者互补（drift 是群体内时间维度，CKI 是群体间截面维度），定位清晰。
- 与 SAMap/SATURN/CACIMAR/CellTypist/scArches 的关系：作者在 Discussion 中承认未做定量 benchmarking，这是诚实但也是弱点。

---

## 3. Critical 问题（必须修改）

### C1. Hybrid 方案的比值不一致性

**问题**：在 Tabula Sapiens 和 brain 分析中，作者采用 "hybrid scheme"：k_n 全局计算一次（所有细胞类型共享同一 HK 基因集），k_f 逐对计算（每对细胞类型用其 top-200 DE 基因）。稿件 P49 称：

> "since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies."

**这个论断是错误的**。JS 散度的取值范围和数值尺度高度依赖基因集大小和组成：
- k_n 在固定 HK 基因集（~1000+ 基因）上计算，JS 值被大量低变异基因稀释，数值偏小。
- k_f 在 top-200 DE 基因上计算，这些基因本身就是差异最大的基因，JS 值系统性偏大。

因此 ω = k_f/k_n 的分子分母处于不同的数值尺度，导致 ω 系统性膨胀。这也部分解释了为什么人脑 ω 中位数 13.68，远高于小鼠的 7.07——除了生物学差异，hybrid 方案本身会放大 ω。

更严重的是：**不同配对的 k_f 使用不同基因集，导致 ω 值跨配对不可直接比较**。A-B 配对的 ω=20 和 C-D 配对的 ω=20 不代表同等程度的功能分化，因为它们用的是不同的 200 个基因。

**建议**：
1. 如果要保留 hybrid 方案，必须明确声明 ω 只在相对排序意义上有效，不能跨配对比较绝对数值。
2. 提供全局 HVG 方案的对照结果（所有配对用同一组 HVG），验证主要结论是否稳健。
3. 在 Methods 中明确说明 k_n 和 k_f 的基因集大小差异，以及这对 ω 数值尺度的影响。

### C2. Softmax 归一化后 JS 散度的语义问题

**问题**：`ensure_probability_distribution` 默认用 softmax 将表达向量转为概率分布（`utils.py:41-45`）。Softmax 会指数化放大高表达基因的权重，使概率分布被少数高表达基因主导。

对于 HK 基因，softmax 后的概率分布可能被 GAPDH、ACTB 等极高表达基因主导，导致 k_n 主要反映这几个基因的差异，而非整个 HK 基因集的"中性漂移"。

稿件 P19 提到 "Softmax normalization converts expression vectors to probability distributions"，但未讨论 softmax 对 JS 散度数值特性的影响，也未与简单的 sum-normalization（`mode="normalize"`）做对比。

**建议**：
1. 提供 softmax vs. sum-normalization 的敏感性分析（已有 `mode` 参数，只需运行对照）。
2. 讨论 softmax 对 JS 数值范围的影响——softmax 后的分布更"尖锐"（peakier），JS 值会系统性偏小，但这不改变相对排序。
3. 在 Methods 中明确说明为什么选择 softmax（log1p 数据有零值和正值，sum-normalization 会丢失零值信息，softmax 更合适——但这需要显式论证）。

### C3. k_n 下限阈值：稿件与代码不一致

**问题**：
- 稿件 P19："we recommend reporting ω with a lower-bound k_n threshold (e.g., k_n ≥ 0.001)"
- 代码 `core.py:255`：`kn_min = 1e-4`

10 倍差异。这直接影响 ω 的数值。用户批注 Comment 3 也提到："这个是怎么计算得到的？我手算没发现有 k_n < 0.001 的 pair"，说明阈值选择对结果有实际影响。

**建议**：
1. 统一稿件和代码的阈值。
2. 报告不同阈值（1e-3, 1e-4, 1e-5）下 ω 分布的敏感性分析。
3. 考虑用 `np.where(kn < kn_min, np.nan, kf/kn)` 而非 `kf/kn_min`——当前实现会人为压低高 k_f 配对的 ω，引入截断偏倚。

### C4. Ka/Ks 类比的过度使用

**问题**：尽管 Discussion（P91）坦诚承认 "CKI is a heuristic, baseline-normalized functional divergence index, not a formal evolutionary selection model"，且明确指出：
- Ka/Ks 有突变率 μ 的抵消机制，CKI 没有
- CKI 的 ω=1 无群体遗传学中性含义
- HK 基因可能受稳定化选择

但在 Abstract、Introduction（P13）、Figure 1A 中，Ka/Ks 类比仍作为核心 framing device，且措辞暗示更强的对应关系（如 "Inspired by this logic"、"neutral offset rate"、"functional conversion rate"）。

**建议**：
1. 在 Introduction 首次引入类比时（P13-P14），就加入一段限定性说明，而非推迟到 Discussion。
2. Figure 1A 的概念图应同时展示类比和关键差异（μ 的抵消 vs. CKI 的无抵消）。
3. 考虑将 "neutral offset rate" 改为更中性的术语，如 "baseline divergence rate"，"functional conversion rate" 改为 "identity gene divergence rate"——减少进化论色彩，更准确描述方法本质。

---

## 4. Major 问题（建议修改）

### M1. HK 基因"中性"假设的验证不充分

**问题**：稿件 P40 承认 "HK genes, defined operationally by high detection rate and low expression variance, show empirically lower between-population divergence"，但"低变异"不等于"中性"。作者自己指出 HK 基因可能受稳定化选择（低方差恰恰因为强功能约束）。

敏感性分析（250-1000 基因，CV<13%）只验证了 ω 对基因集大小的稳健性，未验证"中性"假设本身。如果 HK 基因受稳定化选择，那么 k_n 度量的是"约束下的低漂移"而非"中性漂移"，ω 的解释需要调整。

**建议**：
1. 增加对照：用随机等大小基因集（非 HK）计算 k_n，比较 ω 分布。如果 HK 基因集的 k_n 显著低于随机基因集，支持其作为"低漂移基线"的操作性合理性（不必声称"中性"）。
2. 增加表达年龄依赖性分析：HK 基因的表达是否随年龄/状态漂移？如果漂移，则 k_n 包含真实生物学信号而非纯噪声。
3. 在癌症分析中明确讨论 Warburg 效应对 HK 基因（GAPDH 等糖酵解基因）表达的影响——P95 已提及但较简略，建议量化。

### M2. 校准结果 ω=1.54 与理论值 ω=1 的偏差处理

**问题**：P46 报告校准实验 mean ω=1.54（median 1.42），偏离理论预期 1.0 达 54%。作者解释为"operational HK gene set retains residual biological variation that biases k_n estimates conservatively downward"。

但这个 +54% 的 offset 未被校正，所有后续分析（人脑 ω 中位数 13.68、癌症 NN/TT 比值等）都包含这个系统性偏移。作者声称"this systematic offset does not affect the validity of relative comparisons"——这对排序比较成立，但对绝对数值判断（如 "ω ≈ 1 表示中性漂移"）不成立。

**建议**：
1. 报告校准后的"normalized ω" = ω_observed / 1.54，使同群体分裂的 ω 中心在 1.0 附近。
2. 或明确将所有"阈值"（如 Strong candidate 的 ω<15）以校准值为基准表述。
3. n=6 的校准样本量过小，建议增加校准实验的配对数（如 Tabula Sapiens 内的同细胞类型随机分裂），给出更精确的 offset 估计和置信区间。

### M3. pairwise_de 模式的循环性

**问题**：`gene_sets.py:534-603` 的 `pairwise_de` 模式先对 A vs B 做 DE 检验，选出 top-N 差异基因，然后在这些基因上计算 k_f = JS divergence。这存在循环性：**你先选了差异最大的基因，然后测量它们有多不同**——k_f 必然偏大，ω 必然显著。

这不同于 Ka/Ks 的逻辑，Ka/Ks 是在所有位点上计算 Ka 和 Ks，而非先选非同义位点。

**建议**：
1. 明确讨论这个循环性，并解释为何不构成问题（例如：DE 筛选基于统计显著性，而 k_f 基于效应量大小，两者不同——但这需要显式论证）。
2. 提供全局 HVG 方案的对照（所有配对用同一组 HVG），验证 pairwise_de 的结论是否稳健。
3. 或采用"留一法"验证：对每对配对，用其他配对的 DE 基因计算 k_f，检查是否一致。

### M4. Bootstrap 检验未考虑基因集选择的不确定性

**问题**：`bootstrap.py:223-234` 的置换检验在每次置换中保持 hk_indices 和 identity_indices 固定，仅置换细胞标签。这检验的是"给定基因集，细胞标签是否可交换"，但未检验"基因集选择本身是否稳定"。

对于 pairwise_de 模式，每次置换的 null ω 是在固定 DE 基因上计算的，但这些 DE 基因是在原始（未置换）数据上选出的——置换后这些基因可能不再是 top DE。这会低估 null 分布的方差，使 p 值偏小。

**建议**：
1. 在 Methods 中明确说明 bootstrap 保持基因集固定。
2. 对于 pairwise_de 模式，考虑在每次置换中重新选择 DE 基因（计算成本高但更严谨），或至少讨论这对 p 值的影响。
3. 提供基因集稳定性分析：bootstrap 过程中记录 k_n 和 k_f 的方差，评估基因集固定假设的影响。

### M5. ω 的可解释性与阈值

**问题**：稿件中使用了多个 ω 阈值（ω<15, ω<25, ω<35 for Strong/Moderate/Weak；ω≈1 for neutral），但这些阈值的生物学含义不清晰。P19 提到 "93.6% of all ω values were < 15"，但未解释为什么 15 是一个有意义的分界。

Strong candidate 的 ω<15 阈值与 residual<0.3 是 AND 关系，但两者的交互逻辑未充分说明。

**建议**：
1. 提供 ω 阈值的生物学校准：例如，已知同细胞类型跨器官的 ω 分布（mean 8.70），不同细胞类型同器官的 ω 分布（mean 16.18），用这些经验分位数来界定阈值。
2. 明确 ω<15 在 hybrid 方案下的含义（考虑到 C1 的尺度问题）。
3. 用户批注 Comment 4 指出 "ω<15 的比例应该是 56.3%"——请核实数据，当前稿件与批注不一致。

---

## 5. Minor 问题（可选修改）

### m1. 用户批注的数值不一致

- **Comment 0/13**："手算结果：k_n median = 0.034, range 0.0018-0.221" vs 稿件 P45："median k_n = 0.0086, range 0.0004–0.106"。差异可能来自不同数据集（mouse vs human）或不同归一化方式，但稿件未明确区分。
- **Comment 18**："手算 median = 3.63, mean=5.27" vs 稿件 P50："mouse mean ω = 7.07"。3 倍差异需核实。
- **Comment 22**："上一版是59？"——指 Tabula Sapiens cell-type entries 数量，需核实是 99 还是 59。
- **Comment 4**："ω<15 的比例应该是 56.3%" vs 稿件 P19："93.6%"。巨大差异，必须核实。

**建议**：逐条核对批注，修正稿件数值。

### m2. AUC 比较的公平性

P52 已部分讨论：CKI 用 200 DE 基因 vs. cosine distance 用 ~20000 基因。作者提供了 cosine 限制在 200 DE 基因时的 AUC=0.752，但仍低于 cosine 全基因的 0.887。建议更明确地说明"CKI 的设计目标是可分解性而非分类精度"，并将 AUC 比比改为次要结论。

### m3. 代码实现细节

- `core.py:255` 的 `kn_min = 1e-4` 硬编码，建议改为参数 `kn_min: float = 1e-4` 暴露给用户。
- `gene_sets.py:216-221` 的 mean_cv 计算有潜在问题：`mean_expr[hk_indices]` 用全局均值，但 `std_expr` 用 HK 子集的 std——两者尺度应匹配，但代码用 `X[:, hk_indices].std(axis=0)` 而 `mean_expr` 是 `X.mean(axis=0)[hk_indices]`，一致性需验证。
- `bootstrap.py:183-184`：当 pseudobulk 直接提供时，`n_a = X.shape[0] // 2`——这假设两组等大，但未在 docstring 中说明此假设。

### m4. 文稿表述问题

- P14："ω ≈ 1 indicates functional divergence consistent with baseline variation (empirically calibrated; see Results)"——这里 "empirically calibrated" 指校准实验 ω=1.54，但表述暗示 ω≈1 是校准后的基准，实际校准基准是 1.54，存在误导。
- P52 最后一段有截断（"the only metric whose mathematical formulation permits full decomposition..."），需补全。
- P77 有截断（"the first transcriptome-wide metric to distinguish dorsal..."），需补全。
- Figure 5 legend（P114-P115）出现两次，且内容混乱（有 track changes 残留），Comment 31 提到"这一代改的有问题，建议全部删除"——需重写。
- P90 有段落断裂："CKI is explicitly designed as a perturbation index, not a classifierCKI answers a complementary question..."——句子粘连。

### m5. 参考文献与引用

- P18 引用 [4] HRT Atlas，但未在参考文献列表中看到（需核实）。
- transcriptional drift [37] 的关系讨论较好，但 [38,39,40] 在 P91 中引用的 population-genetic models of expression evolution 未在参考文献中明确列出（需核实）。

---

## 6. 具体改进建议（按优先级）

### 高优先级
1. **统一 k_n 下限阈值**（稿件 0.001 vs 代码 1e-4），并做敏感性分析。
2. **核实所有用户批注的数值**（Comment 0, 4, 18, 22），修正稿件中的错误数据。
3. **在 Methods 中明确讨论 hybrid 方案的尺度不一致性**，或提供全局 HVG 对照结果。
4. **重写 Figure 5 legend**（Comment 31 指出有问题）。
5. **在 Introduction 首次引入 Ka/Ks 类比时就加入限定性说明**，不要等到 Discussion。

### 中优先级
6. 增加 HK 基因"中性"假设的正交验证（随机基因集对照）。
7. 报告校准后的 normalized ω = ω/1.54，使阈值有统一的参照基准。
8. 讨论 pairwise_de 模式的循环性，或提供全局 HVG 对照。
9. 补全截断段落（P52, P77, P95 等）。
10. 提供 softmax vs. sum-normalization 的敏感性分析。

### 低优先级
11. 将 `kn_min` 暴露为参数。
12. 修正 `gene_sets.py` 中 mean_cv 的计算一致性。
13. 在 `bootstrap.py` docstring 中说明 pseudobulk 直接输入时的等大假设。
14. 精简 Figure 1A 的 Ka/Ks 类比，加入"关键差异"子图。

---

## 7. 总结

CKI 是一个**概念上有启发性、工程上实现良好、但方法学论证存在明显缺口**的工作。核心问题在于：

1. **Hybrid 方案的比值不一致性**（C1）是最严重的方法学问题——k_n 和 k_f 处于不同尺度，ω 跨配对不可直接比较，这削弱了所有基于绝对 ω 数值的结论（如 ω<15 阈值、ω 梯度的倍数关系）。
2. **Ka/Ks 类比的张力**：作者在 Discussion 中做了诚实的 disclaimer，但在 Introduction 和 Abstract 中仍过度依赖类比的说服力。建议将 disclaimer 前移。
3. **"中性"假设**：操作性定义合理，但理论论证薄弱。建议用"baseline divergence"替代"neutral drift"的表述，减少进化论色彩。

这些问题大多是**可通过修改和补充分析解决的**，不构成拒稿理由。建议作者在修订中：
- 降级 Ka/Ks 类比的定位（从"inspired by"改为"loosely analogous to"）
- 统一数值和阈值
- 明确 hybrid 方案的局限性
- 将"neutral"术语改为"baseline"

代码质量良好，建议在修订后接受。
