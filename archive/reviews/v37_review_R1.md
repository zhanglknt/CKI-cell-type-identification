# NAR 模拟审稿报告（R1，计算方法学/算法审稿人）

**稿件**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling (v37)
**审稿人身份**: 计算方法学审稿人（度量论、算法评估、计算生物学方法）
**审稿日期**: 2026-08-28
**总体建议**: Major Revision（总分 4/10）

---

## 一、贡献与主张总结

作者提出 CKI（cell-state kinetic index），一个受 Ka/Ks 启发的启发式比值度量：以 housekeeping（HK）基因上的 Jensen-Shannon 散度 k_n 作为"基线速率"，以 identity 基因（per-pair top-200 DE 基因或全局 top-2,000 HVG）上的 JS 散度 k_f 作为"功能速率"，ω = k_f/k_n 量化"baseline-normalized functional divergence"。方法在四个数据集上验证：Tabula Muris 校准（split-half 等价群体基线 ω = 6.67）、Tabula Sapiens 4,851 对方法比较、TCGA 泛癌探索性分析（NN/TT 比值、PAM50/Edmondson/突变分层）、Siletti 人脑 888k 非神经元核的 31,764 个跨区域比较（6.88 倍细胞类别分化梯度 + 乘法残差迁移候选筛选，block-shuffle null 下无一通过 FDR）。

本版（v37）是对上一轮模拟审稿的实质性修订，修订质量值得肯定：新增了 within-donor 梯度（4.07 倍，类别排序保持）、k_n 估计量敏感性（aggregate-first ρ = 0.988；global-k_n ρ = −0.21）、scheme-matched split-half 内部校准（brain 12.29、TS 7.67，发现 mouse 校准因子不可迁移到 brain）、lineage enrichment 正式检验（50/55，hypergeometric P = 4.5e-15）、tier 阈值敏感性（16/19 组合显著）。作者主动承认 ratio artifact、TCGA 混杂、候选筛选为 hypothesis-generating、q < 0.05 在 B = 1,000 下数学上不可达等，诚实程度在同类稿件中罕见。代码、notebook、结果文件、复现指南齐备，我对抽查的数据文件（reviewer_* 系列、brain_bs_null_*）核验，稿件报告的数字与底层输出一致。

然而，作为方法学审稿人，我认为核心问题依然存在且部分被稿件低估：**CKI 的中心命题——ω 度量"以基线归一化的功能分歧"——被作者自己的分解分析实质性削弱，而我基于其公开数据文件的核验表明，在 pair 级别 ω 几乎完全由分母 k_n 驱动**（详见 Critical #1）。校准因子不可跨数据集迁移（Critical #2），per-pair DE 基因选择的循环依赖使 k_f 跨对不可比（Critical #3），而方法学论文最需要的 ground-truth 模拟验证完全缺失（Critical #4）。稿件目前的价值更多在于 k_f/k_n 分解诊断本身，而非 ω 比值。

---

## 二、逐条问题

### Critical

**C1. ω 在数据中实际是分母主导的复合量，与标题/摘要的 "functional divergence" 命题不符；稿件在 pair 级别低估了这一点。**

证据（稿件原文）：
- Results（brain 梯度一节）: "the astrocyte-versus-Bergmann-glia contrast is predominantly a k_n effect: k_f differs only 1.2-fold between the two classes (0.033 vs. 0.027), whereas mean k_n differs 5.7-fold"。作者自己得出 "The ω gradient therefore chiefly reflects differences in how stably housekeeping programs are maintained across regions... not proportionally larger functional-gene divergence"。
- Abstract 仍以 "Brain analysis revealed a 6.88-fold regional differentiation gradient" 作为主要发现，标题仍为 "Quantifying Baseline-Normalized Transcriptomic Remodeling"。
- 审稿人核验（results/reviewer_brain_pair_kf_kn.csv，31,764 对）：pair 级别 Spearman ρ(ω, k_n) = **−0.535**，ρ(ω, k_f) = **−0.032**，ρ(k_f, k_n) = +0.832。即脑数据中 ω 的排序信息几乎全部来自 k_n 的逆序，与 k_f（"functional" 分量）在 pair 级别**零相关**。类别级聚合掩盖了这一点。
- 另一处自我矛盾：Fig. 2C 图例仍写 "All show negative correlation, confirming ω captures complementary information"，而 Results 已将该负相关归因于 "the classical spurious correlation of ratios" 的分母效应。

要求：作者必须正面处理 ω 的解释问题，而不是在 Limitations 中承认后继续以功能分歧语言包装结果。具体要求：(i) 在 Results 正文报告 pair 级别 ω 与 k_f、k_n 的秩相关（我的核验可直接复现）；(ii) 重写摘要与标题，明确 ω 在实际数据中的分母主导性质，或将论文主贡献重新定位为 k_f/k_n **分解诊断框架**（稿件自己已建议 "comparing k_f and k_n components directly when mechanistic attribution matters"——既然如此，主结果就应当这样做）；(iii) 删除/改写 Fig. 2C 图例及一切 "complementary information"、"independent dimension" 残留表述。若作者坚持 ω 作为主度量，需提供 ω 优于 k_f 单独使用或 (k_f, k_n) 二元组的定量证据。

**C2. 校准体系不可迁移，ω_cal 的科学价值未确立。**

证据：
- Results: "a scheme-matched split-half calibration performed inside the brain atlas itself... gave an internal baseline of 12.29..., approximately 1.8-fold higher than the mouse-derived factor"; "the mouse-derived calibration factor is therefore transferable to the Tabula Sapiens dataset but not to the brain atlas, and ω_cal should be treated as a dataset-relative"（句子被截断但语义明确）。
- 校准源头仅 n = 6 个 mouse split，CV ≈ 52%，CI [4.24, 9.24]——作者自己写 "formal equivalence testing (e.g., TOST)... the current sample size (n = 6)... limits the power of such tests and the precision of the calibration factor"。
- 内部校准还揭示：Bergmann glia 的 ω_cal ≈ 0.9，处于（而非高于）等价群体期望——作者承认 "the conclusion that essentially all non-neuronal classes exceed the split-half baseline does not hold under internal calibration"。

要求：一个仅在单一数据集内有效、且数值随数据集改变 ~1.8 倍的"校准"不是校准，而是 dataset-specific offset。要求作者：(i) 以内部（scheme-matched, split-half）校准为默认，ω_cal 只在数据集内部使用；(ii) 研究偏移量随可操纵数据特征（测序深度、每群细胞数、sparsity、归一化方式）的系统变化并给出机制解释（softmax(log1p) 下 p_i ∝ geomean(1+x)，伪计数 1 相对 log1p 尺度的权重效应值得分析）；(iii) 或者放弃 ω_cal 跨数据集的任何表述，全文仅保留 rank-based 结论。

**C3. per-pair top-200 DE 基因选择的循环依赖使 k_f（从而 ω）在跨对比较中不可比，而 brain 梯度与残差模型恰恰是跨对绝对比较。**

证据：
- Methods/Algorithm 2: "Delta <- |mu_A - mu_B|; I <- indices of top-N genes ranked by descending Delta"——k_f 的分子基因由被比较两组自身的差异最大基因定义。
- Limitations 承认: "the circularity means that k_f magnitudes lack independent external validation and should be interpreted as an upper bound on functional divergence" 与 "ω is computed on different gene sets per comparison, limiting absolute cross-comparison interpretability"。
- 但 brain 分析的核心操作正是跨对绝对比较：类均值梯度（μ_ct）、乘法残差模型（expected_ω = μ_ct × μ_pair/μ_grand）、tier 阈值（ω < 15/25/35）都是绝对量。稿件未解释为什么循环选择下这些跨对绝对比较仍然有效。

要求：permutation 检验保持选择程序，只能使 exchangeability 检验有效，不能解决跨对可比性。要求作者：(i) 用固定基因集（如全局 HVG-2000 或整个非 HK 高表达池）重算 brain 梯度与残差模型作为敏感性分析，报告类别排序与候选列表的稳定性；(ii) 或论证 top-200 选择在不同 pair 间的"选择强度"（如 200th 基因的 |Δ| 分布）近似恒定；(iii) 明确声明残差模型 tier 中的绝对 ω 阈值在该循环方案下无跨对含义。

**C4. 方法学论文缺乏 ground-truth 模拟验证。**

证据：Limitation #14（Reproducibility Guide Phase D i 项）: "Added as Limitation #14 (no synthetic data validation with known ground-truth signals)"；Discussion 承认未与 SAMap/SATURN/CACIMAR 定量比较（"we did not quantitatively benchmark CKI against these specialized methods"）。Table 1 中 CKI 的 AUC = 0.680，五个方法中排名末位。

要求：对一个提出新度量的 NAR 方法论文，这是核心验证的缺失，不能用 Limitation 免除。要求：(i) 构造已知功能分歧强度的合成数据（控制 HK 基因漂移幅度与 identity 基因差异幅度，含 dropout、深度、细胞数不平衡等真实单细胞特征），验证 ω 对功能分歧的单调性、估计偏差、方差与 power，并与 k_f、raw JS、cosine 在同一 ground truth 下比较；(ii) 至少与一个现有可比较方法（如 SATURN 的跨数据集一致性得分或简单基线 k_f/k_total）在共享任务上定量比较。若 ground-truth 下 ω 不优于现有量，应如实报告并据此重新定位贡献。

### Major

**M1. kn_floor 的文档矛盾，以及稿件对 brain 最小 k_n 的陈述与数据不符；小分母对比值尾部的实际影响未报告。**

证据：
- 主稿 Methods: "the package default (kn_floor = 0) applies only a positivity guard... so no reported single-cell ω was capped (minimum observed per-pair k_n: ...; 7.7 × 10⁻⁵, brain). The TCGA bulk RNA-seq analysis is the sole exception and applies kn_floor = 1 × 10⁻⁴"。
- Supplementary Note 1.1 与 Algorithm 1（第 7 步 "if k_n < 1e-4: k_n <- 1e-4"）及 Reproducibility Guide 参数表（"k_n floor (minimum) | 1e-4 | all analyses"）均写 floor = 1e-4 适用于所有分析——与主稿直接矛盾。
- 审稿人核验 results/reviewer_brain_pair_kf_kn.csv：31,764 对中最小 k_n = **7.8 × 10⁻⁶**（不是 7.7e-5），且 **1,825 对（5.7%）k_n < 1e-4**；该子集平均 ω = 39.0（高于全局均值 32.56），整体最大 ω = 266.9。若 floor 真被应用，这些 ω 全部被截断——显然 brain pipeline 未应用 floor，故 Guide/Supplementary 的描述错误，主稿的 7.7e-5 也与数据不符。

要求：(i) 澄清并统一三处文档；(ii) 修正 brain 最小 k_n 数值；(iii) 报告 k_n 分布下尾（如 < 1e-4、< 5e-5 的对数）及其对梯度、残差模型、类别均值的影响分析（例如 winsonize/截断 k_n 后重算梯度）；(iv) 复现指南中给出验证 floor 行为的可执行检查步骤。注意 kn_cv 高达 92.89% 本身已是小分母不稳定性的信号，稿件把它当作"per-pair k_n 必要性"的证据（见 M7），方向值得商榷。

**M2. TCGA 分析的 ω 估计量处于饱和状态，临床分层结论建立在截断比值上。**

证据：主稿 Limitation 20: "the TCGA analysis applies kn_floor = 1 × 10⁻⁴ (the aggregate tumor-versus-normal k_n ranged from 3.0 × 10⁻⁵ to 1.9 × 10⁻⁴ across the five cancer types, so ω saturates at k_f/10⁻⁴ in 3 of 5 cancer types)"。既然 3/5 癌型中 ω 退化为 k_f × 10⁴，则 PAM50 梯度、Edmondson 趋势、突变分层以及 NN/TT 比值在这些癌型中不是"baseline-normalized"信号而只是 k_f 的单调变换，Ka/Ks 式解释失去基础。

要求：在饱和癌型中以 k_f 直接报告并检验临床分层；NN/TT 比值分析需说明饱和对比值的影响方向；或对 TCGA 使用不同 floor/不同基线估计策略的重算。鉴于作者已将 TCGA 定位为 exploratory，此要求为修订而非新增大规模计算。

**M3. 方法比较（AUC）的任务定义不清，且关键统计检验忽略配对非独立性。**

证据：
- Methods "Method comparison" 与 Table 1 只给 AUC 数值，未定义分类任务的具体设定（正负样本、打分如何映射为类别判别、ROC 曲线如何构造），读者无法复现 0.680–0.887。
- Results: "CKI was the only metric where same-organ different-cell-type pairs had higher values than different-organ different-cell-type pairs (mean ω 24.87, n = 1,038 vs. 20.80, n = 3,754; ... Mann-Whitney U test, P < 0.001)"——4,851 个对共享细胞类型与器官，并非独立样本，P < 0.001 被夸大。同类问题也出现在 TCGA（intratumoral ω 由共享样本的对构成）与 brain（类别检验共享 region 对）。
- Methods 已承认 "one pseudobulk was computed per cell-type entry from its largest donor... the method comparison does not capture inter-donor variability"（好），但这与上述独立性问题是两回事。

要求：(i) 完整给出 AUC 任务定义；(ii) 对依赖数据的检验改用 block/cluster bootstrap（按细胞类型或按样本 block 重采样）或 permutation（保持依赖结构），重新报告显著性；(iii) TCGA 分层分析补充说明样本对依赖性对 Kruskal-Wallis/Jonckheere-Terpstra 的影响及稳健推断结果。

**M4. Cover letter 与修订后主稿的科学主张相矛盾。**

证据：Cover letter: "demonstrating that ω measures something fundamentally different from raw JS divergence, cosine similarity, and other existing approaches"；"a robust, interpretable measure of baseline-normalized transcriptomic remodeling"；"which we verified is not driven by gene-set dimensionality"。而主稿 Results 明确写 "the negative raw correlation is thus partly a ratio artifact of the k_n denominator and should not be interpreted as evidence that ω measures a fully independent information dimension"；Supplementary Note 3.6 承认 dimensionality 模拟 "does not simulate the variance-based gene selection mechanism"。"robust" 与 ρ(ω_global-kn-variant) = 0.181 的估计量敏感性（作者自己报告）也不相容。

要求：重写 cover letter 使其与主稿的诚实表述一致；删除 "fundamentally different"、"robust"、"verified is not driven by dimensionality" 等超出证据的措辞。

**M5. Lineage enrichment 检验的 "pre-specified" 定性不成立（post hoc 检验被包装为先验）。**

证据：results/reviewer_lineage_enrichment.txt 输出明确标注 "Oligodendrocyte lineage (pre-specified): pairs=12775..."；但 MANIFEST_v37 显示该检验是 v37 针对 v36 审稿意见 C-G 新增的（"C-G lineage enrichment formal test"），即是在观察到 50/55 集中现象之后才设计与实施的。主稿 Results 相应表述为 "Formal enrichment testing of the lineage concentration at the default thresholds confirmed it"，用词 "confirmed" 具有验证性语气。

要求：如实标注该检验为 post hoc（exploratory），删除 "pre-specified" 标签；或在独立数据（如另一个脑区图谱或小鼠 OPC 数据）上做 out-of-sample 验证。hypergeometric 检验本身也依赖类别间 pair 数差异的独立性格局（例如 oligodendrocyte 类 5,778 对全部来自 108 个区域的跨区组合结构），应说明其独立性假设在此的适用性。

**M6. 维数不变性模拟（Dirichlet）不能代表 softmax(log1p) 表达分布的结构，k_f/k_n 不对等性的结论外推过强。**

证据：Supplementary Note 3.6 / Fig. S10 使用 "random Dirichlet distribution pairs"；作者自己承认 "this simulation addresses dimensionality per se... but does not simulate the variance-based gene selection mechanism"。更深一层：softmax(log1p(μ)) 产生的概率向量高度集中于少数高表达基因（p_i ∝ geomean(1+x_i)，长尾基因权重 ~1），随机 Dirichlet 向量的支撑结构与它完全不同；JS 散度在这种集中分布下对维数的依赖可能与 Dirichlet 情形不同。

要求：用从真实数据（如 Tabula Muris/TS 的 pseudobulk）bootstrap 或扰动生成的、保持表达集中结构的模拟对重做该分析，或将 Fig. S10 的结论降格为"维数本身不是问题，选择机制是问题"的辅助证据（后者其实已是作者结论，但摘要/cover letter 的表述强度需要相应下调）。

**M7. 估计量敏感性分析揭示 ω 排序高度脆弱，但被叙述为对所选估计量的支持。**

证据：Results: "the Spearman correlation between per-pair ω and global-k_n ω was only 0.181..., confirming that pair-specific k_n is essential for accurate ω ranking"。"accurate" 相对什么？没有 ground truth，两个合理估计量给出秩相关仅 0.181 的排序，说明的是 ω 对分母估计方式极度敏感（Supplementary Note 3.7 亦称 "would preserve only ~3% of the variance in omega orderings"），而不是 per-pair 版本"essential"。aggregate-first 与 per-pair 的 ρ = 0.988 则说明结论在类均值层面可救，但 pair 级排序（残差模型、tier 筛选所依赖的量）的稳定性未被评估。

要求：(i) 删除 "essential for accurate ω ranking" 的循环论证措辞，改为诚实报告敏感性；(ii) 在 aggregate-first / global-k_n 两个变体下重算残差模型与 55 个 Strong 候选的重合率（Jaccard），报告筛选结果的估计量稳定性——这是候选列表可信度的直接证据。

**M8. 头条 brain 结果的两个端点均存在结构性混杂，"6.88-fold gradient" 作为摘要级主张强度过高。**

证据：(i) Bergmann glia 端点——"all 21 of their comparisons are intra-cerebellar, and their low ω partly reflects this anatomical restriction"（作者承认）；(ii) astrocyte 端点——梯度主要由 k_n 差异驱动（C1）、within-donor 值系统偏低（"part of the pooled between-region signal reflects between-donor variation"）、四个 donor、94.5% region pair 共享至少一个 donor。摘要以 "6.88-fold regional differentiation gradient" 领衔，而作者自己的分析把它分解为 ~1.2 倍 k_f + ~5.7 倍 k_n。

要求：摘要改为报告 k_f/k_n 分解后的表述（如 "gradient driven predominantly by housekeeping-program stability"），或以 within-donor 4.07 倍为主要数字并注明成分结构。

### Minor

**m1. 软件环境不一致。** 主稿写 "scanpy 1.12.1"，Reproducibility Guide 1.1 写 "scanpy: 1.10.4"；主稿 Python "3.14.4" 与 package "requires Python ≥3.10" 并存无矛盾但建议核对实际运行版本。要求统一。

**m2. ω_cal 数值不一致。** 主稿 brain 内部校准下 "ω_cal ≈ 2.7, astrocytes to ω_cal ≈ 6.3"；Supplementary Note 3.5 写 "2.6...6.2"。32.56/12.29 = 2.65、76.83/12.29 = 6.25，两处取整方向不同。要求统一（按投稿版本核对）。

**m3. HVG 参数 sweep 网格两处不一致。** Supplementary Note 3.11: "tested N_HVG in {500, 1000, 2000, 3000, 5000}"；Note 4.4: "tested N_HVG in {50, 100, 200, 500, 1,000, 2,000}"。要求核对 phase32_sweep_results.csv 后统一。

**m4. Supplementary Note 1.3 提及从未评估的扩展。** "regulon activity genes... pathway enrichment genes... macro-gene embeddings (e.g., ESM-2)" 加权扩展从未在任何 sweep 中测试（sweep 只覆盖 w_identity/w_pathway）。要求删除或明确标注为未实现的设想。

**m5. "Kinetic" 命名误导。** k_f、k_n 是散度（无量纲），不含时间或速率语义，"cell-state kinetic index" 与 "divergence rate" 的提法会误导读者预期动力学内容。要求改名（如 "baseline-normalized divergence index"）或在 Methods 明确 "rate" 为类比修辞。

**m6. TCGA 采样随机性。** "Maximum 2,000 random TT and TN pairs each"——NN 对是否同样封顶未说明；随机子采样使结果依赖 seed 42 的单次实现，建议报告跨 seed 的稳定性（作者已论证 B 的 Monte Carlo 误差，但子采样方差未讨论）。

**m7. Table 2 端点统计。** Endothelial/Erythrocyte n = 3 已被恰当下调为 suggestive（好）；建议对 n ≥ 5 的类别补 bootstrap CI（正文说在 Supplementary Table S2，请确认实际包含）。

**m8. 参考文献 20（TCGA）在 Reproducibility Guide 4.3 中引用 "Hutter & Zenklusen, Cell 2018; Liu et al., Cell 2018"，与主稿参考文献列表 (10,11) 的 TCGA Network 论文不一致。** 要求统一引用。

---

## 三、方法学重点评述（比值度量性质总结）

1. **比值数学性质**：ω = k_f/k_n 中分子分母强正相关（ρ(k_f,k_n) = 0.83，我核验；主稿亦报告 k_n 与标准度量 r = 0.69–0.81），比值在消除共同信号的同时把方差放大留给分母噪声；pair 级 ρ(ω,k_f) ≈ 0 说明比值在实际数据中已不再是"功能分歧"的读数。Pearson (1897) 经典的 spurious correlation of ratios 在此完全适用，作者部分承认，但未承认到 pair 级别。
2. **伪相关风险**：稿件处理了与外部度量的伪相关（分解分析、Fig 3 重命名、partial correlation——这部分做得好），但未处理内部结构：ω 与自身分母的负相关（ρ = −0.54）意味着任何与 k_n 相关的协变量（donor、region 覆盖度、每群细胞数、测序深度）都会以反向进入 ω。nuclei 数与 ω 的正相关（Supp Fig. S6C）可能正是这一机制的表现，稿件以 "broader spatial distribution... greater divergence" 解释，存在替代解释（更深/更多细胞的 pseudobulk 平均压缩 k_n → 抬高 ω）。要求补充每群 nuclei 数对 k_n 的回归/分层分析。
3. **估计量稳健性**：per-pair / global / aggregate-first 三种 k_n 估计给出 ρ = 0.181 / 0.988 的两两不一致格局，类均值层面稳定、pair 级别脆弱（M7）；小分母尾部（1,825 对 < 1e-4）未纳入稳健性叙述（M1）。
4. **校准体系**：mouse 6.67 [4.24, 9.24]（n=6, CV 52%）→ brain 12.29 → TS 7.67，跨数据集不可迁移（C2）；"ω = 1 的理论理想"从未达到，且偏移无机制模型。
5. **基准比较公平性**：AUC 任务定义缺失；CKI 在其唯一可比的定量基准上排名末位，其独特性主张依赖的 "same-organ > different-organ 反转" 使用了忽略依赖结构的检验（M3）。
6. **可复现性**：代码/数据/seed/输出文件索引完备且抽查一致（值得表扬），但 kn_floor 的三文档矛盾、scanpy 版本不一致、最小 k_n 数值错误说明文档层质量控制在修订中失守（M1/m1）。复现指南声称 "readers should obtain numerically identical results"，在上述矛盾澄清前无法完全成立。

---

## 四、评分与推荐

| 维度 | 评价 |
|---|---|
| 新颖性 | 中。分解思想有价值，但 ω 本身的 Ka/Ks 类比是启发式的，且作者已承认其形式性质不成立 |
| 方法学严谨性 | 中偏低。诚实但被动：问题多在 Limitations 承认而非在设计中解决；核心度量被自己的分析削弱 |
| 验证充分性 | 低。无 ground-truth 模拟、无与现有方法定量比较、唯一可比基准中排名末位 |
| 生物学发现 | 弱。brain 筛选无 FDR 幸存者（诚实报告），TCGA 为探索性，headline 梯度主要是 k_n 效应 |
| 可复现性 | 高（文档矛盾待修） |

**总分：4/10**

**推荐决定：Major Revision**

理由：稿件在诚实性、稳健性分析覆盖面与可复现性工程上优于一般投稿，且修订响应质量高；但中心度量 ω 的科学命题被作者自己的分解与审稿人的数据核验实质性否定（分母主导、校准不可迁移、循环基因选择下的跨对不可比），而方法学验证（ground truth、外部基准）缺失。这些问题可通过重新定位论文（以 k_f/k_n 分解诊断为主、ω 为派生读数）、补做合成数据验证、修正文档矛盾与依赖结构推断来解决，故给予 Major Revision 而非 Reject。若作者在修订中坚持以 ω 为核心并维持 "functional divergence" 的主张强度，我将在下轮倾向于 Reject。

---

*审稿人声明：本评审基于 v37 投稿包全部文本及 results/ 目录下抽查数据文件（brain_bs_null_summary.txt、reviewer_brain_pair_kf_kn.csv、reviewer_kn_estimator_consistency.csv、reviewer_within_donor_gradient.csv、reviewer_lineage_enrichment.txt、reviewer_tier_sensitivity.csv、reviewer_brain_splithalf_summary.txt、reviewer_ts_splithalf_summary.txt、reviewer_decomposition_correlations.csv、mouse_pilot_v2_results.csv、phase35_all_metrics_pairs.csv），数字核验细节见各条目内注明。*
