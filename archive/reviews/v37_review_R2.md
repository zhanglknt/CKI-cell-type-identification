# 模拟审稿报告（Reviewer R2 — 单细胞基因组学方向）

**期刊**: Nucleic Acids Research（Original Research）
**稿件**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling（v37 投稿包）
**审稿人专长**: snRNA-seq/scRNA-seq 数据分析、细胞类型注释、跨数据集比较
**日期**: 2026-08-28

**声明**: 我抽查了 `results/` 下与稿件关键数字对应的结果文件（`phase35_all_metrics_pairs.csv`、`brain_bs_null_ct_test.csv`、`brain_bs_null_summary.txt`、`reviewer_within_donor_gradient.csv`、`reviewer_lineage_enrichment.txt`、`reviewer_brain_splithalf_summary.txt`、`reviewer_ts_splithalf_summary.txt`、`mouse_pilot_v2_results.csv`、`reviewer_kn_estimator_consistency.csv` 等），独立复算了 4,851 对 Tabula Sapiens 五度量的 Spearman 相关矩阵（复现了 r = −0.36～−0.46 与标准度量间 0.57–0.93 的正簇）、小鼠 pilot 六个 control 的均值 6.67、脑内 split-half 基线 12.29 等核心数字。**所有抽验数字均可复现**。本报告的批评集中在科学性与论证结构，而非数字造假。

---

## 一、贡献与主张总结

本稿提出 CKI（cell-state kinetic index, ω = k_f/k_n）：将两个细胞群体 pseudobulk 之间的 Jensen–Shannon divergence 分解为基于 housekeeping（HK）基因的"基线分歧率" k_n 与基于 identity 基因的"功能分歧率" k_f，以其比值 ω 量化"相对于内部基线的功能分化"。作者明确将其定位为 Ka/Ks 的启发式类比而非形式化选择度量，并在四个尺度上验证：(1) Tabula Muris 小鼠 atlas 的校准（同群体随机二分的 ω 基线为 6.67，95% CI [4.24, 9.24]）；(2) Tabula Sapiens 人 atlas 4,851 对细胞类型比较及与四种标准距离度量的对比；(3) TCGA 泛癌 bulk RNA-seq 的探索性分析（NN/TT > 1 的"转录趋同"信号）；(4) Siletti 人脑 snRNA-seq atlas（888,263 个非神经元核，31,764 个同细胞类型跨脑区比较）揭示的 10 个细胞类间 6.88 倍区域分化梯度，及基于乘法残差模型的"异常相似"候选筛选（55 个 Strong 候选，其中 37 个 raw P < 0.05，但无一通过 BH-FDR 校正，最小 q = 0.949）。

值得肯定的是，本稿在统计诚实性上明显高于同类投稿：作者主动披露了 (i) 负相关是 k_n 分母导致的比值伪相关（partial r 转正）；(ii) 小鼠校准因子不能迁移到脑数据（脑内 split-half 基线 12.29）；(iii) 脑梯度主要是 k_n 效应（k_n 差 5.7 倍，k_f 仅差 1.2 倍）；(iv) per-pair DE 选基因的循环性；(v) 脑候选筛选在当前 B 与多重性下 q < 0.05 数学上不可达；(vi) Bergmann glia 的低 ω 部分源于其仅限于小脑的解剖分布；(vii) 供体混杂的 within-donor 复验。这些自我批评真实且必要。

然而，把这些诚实披露拼起来看，暴露出的是同一个核心问题：**本稿目前没有证明 ω 测量的是"功能分化"而不是"基因选择程序的构造性产物"**。校准基线 6.67 ≠ 1 且不能跨数据集迁移；与标准度量的负相关是分母伪迹；唯一客观的判别性能指标（分类 AUC = 0.680）在五个方法中垫底；旗舰分析（脑候选筛选）全部为 null 结果；脑梯度主要由 k_n 驱动。每一处作者都作了正确的 caveats，但整篇文章的"正面贡献"由此所剩无几——它目前更像一篇高质量的"指标解剖学/警示性"论文，而非一个被验证可用的新方法。

---

## 二、具体问题

### Critical

**C1. 缺少任何 ground-truth 验证，无法确立"ω 测量功能分化"的核心主张。**
- 证据：文中唯一的定量性能指标是 Table 1 的分类 AUC，CKI 为 0.680，"ranked 5th of 5 methods"（Results, "Correlation structure between CKI and standard metrics" 节）。作者自己写道 "we did not quantitatively benchmark CKI against these specialized methods"（Discussion），并在 Limitation 中承认无合成数据 ground-truth 验证（Reproducibility Guide 5.5i："Added as Limitation #14 (no synthetic data validation with known ground-truth signals)"）。
- 论证链条的每一环都被作者自己的敏感性分析削弱：校准基线偏离理论值 6.67 倍且脑内为 12.29（≈1.8×小鼠因子，"the mouse-derived calibration overstates ω_cal in the brain dataset"）；负相关是比值伪迹（"the negative raw correlation is thus partly a ratio artifact of the k_n denominator"）；脑梯度 "predominantly a k_n effect: k_f differs only 1.2-fold ... whereas mean k_n differs 5.7-fold"。如果 ω 的排序主要由分母（HK 基因的跨区稳定性）驱动，而分母又被承认可能"reflect regulatory constraints rather than pure neutral drift"（Discussion），那么把 ω 称为"功能分化指数"缺乏证据。
- **要求**：增加一个受控模拟框架：在真实单细胞数据背景上注入已知强度的"功能"扰动（特定 gene module 的协同移位）与"中性"漂移（全局噪声/技术批次），系统比较 ω、k_f-only、raw JS、cosine 等在恢复注入信号上的 precision-recall 与排序保真度。若 ω 在该 ground truth 下不优于简单基线，文章的核心主张不成立，应当重新定位（例如作为"比值型度量的统计陷阱"方法学论文）。这一条是决定性的。

**C2. per-pair k_f 的循环基因选择未被充分中和，跨 pair 的 ω 比较因此不可解释。**
- 证据：k_f 使用 "the top-200 differentially expressed genes (ranked by absolute mean difference) for that specific pair"（Methods, CKI computation；Supplementary Note 2 Algorithm 2: "Delta <- |mu_A - mu_B|; I <- indices of top-N genes ranked by descending Delta"）。作者承认 "the circular dependency inherent in the per-pair k_f scheme ... the genes defining 'functional divergence' are precisely those with the largest expression differences between the two groups under comparison"（Limitations）。
- 问题在于：permutation null 只能校正**同一对内部**的循环性，而全文的实质性主张——脑 10 类间 6.88 倍梯度、跨器官保守性排序、候选残差排序——全部依赖**跨 pair** 比较 ω。循环选基因带来的膨胀幅度随 pair 而异（依赖两组的 DE 结构、基因数、表达量量级），这种 pair 特异性偏倚恰恰在跨 pair 排序中不被 permutation null 消除。作者展示的 k_n 估计器敏感性（aggregate-first ρ = 0.988；global-k_n ρ = −0.21）没有触及 k_f 的选基因方案。
- **要求**：(a) 用**固定的** identity 基因面板（如每类 curated marker 基因集，或全数据集全局 HVG）重算脑梯度与排序，报告与 per-pair DE 方案的秩相关；(b) 检验梯度对 top-200 这一截断值（100/500/1000）的敏感性；(c) 若固定基因集下梯度消失，必须如实报告并重写结论。

**C3. 脑候选筛选的统计设计保证了 null 结果，而 OPC 谱系叙事却仍以 Results 标题级别呈现。**
- 证据：作者明确论证 "at this multiplicity q < 0.05 could not be reached at any effect size without B ≈ 6 × 10⁵ permutations"（Results/Methods），且 "938 of 31,764 pairs (3.0%) showed raw P < 0.05, fewer than the ~1,588 (5%) expected under a global null, indicating no aggregate excess of small P-values"。也就是说，**整个 screen 在全局层面无任何超出 null 的信号**。然而 Results 仍保留 "OPCs dominate the candidate list" 这样的独立小节标题，摘要仍写 "a screen of anomalously similar cell-type/region-pair candidates"。
- 谱系富集检验（hypergeometric P = 4.5e-15；permutation P = 1.0e-5）回答的是"给定这 55 个阈值通过者，是否集中于少突胶质谱系"，它**条件于一个自身无统计学证据的候选集**——在全局 P 值无过量溢出的前提下，"阈值通过者的谱系富集"完全可能是阈值结构（残差模型中 μ_ct、ω-cap=15 与各类的 k_n 尺度差异）驱动的。ω < 15 的 cap 本身就让低 k_n 尺度的类（OL 谱系各类均值 22–42，Bergmann glia 11）更容易落选/入选的结构性偏差需要正面讨论：为何富集不可能是"少突谱系各类的 ω 分布形状更靠近 cap"所致？
- **要求**：(a) 将 B 提升至能分辨目标信号的量级（作者自估 B ≈ 6 × 10⁵；脑分析 B = 1,000 用 72 core-hours，B = 10⁵ 约数千 core-hours，在集群上可行），或采用分层/置换式 FDR（作者自己在 Limitation 19 提到 "a hierarchical or permutation-based FDR estimate could further refine the multiplicity model"，但未做）；(b) 在 block-shuffle null 下直接计算 Strong 候选的谱系富集期望（目前富集的 expected 是按 pair 份额，不是按 null 下 Strong 候选的分布）；(c) 在获得任何统计支持之前，将 OPC/谱系叙事从 Results 降级为 Discussion 中的假设性讨论。

**C4. 供体混杂只对"梯度"做了 within-donor 复验，候选 screen 未做。**
- 证据：脑数据仅 4 名供体，"94.5% of region pairs share at least one donor（median top-donor share within a region: 0.61）"（Methods）。区域 pseudobulk 在中位数意义上 61% 的核来自单一供体——**许多"区域"实际上近似单供体测量**。作者对类级梯度做了 within-donor 复验（4.07 倍梯度保留，Results），但 55 个 Strong 候选没有任何供体层面的复现性检验：某个候选区域对可能完全由一名供体贡献。
- **要求**：对每个 Strong 候选，报告其区域对在多少名供体中各有 ≥20 核，以及按供体分层后该区域对的 ω 是否在 ≥2 名供体中一致偏低。候选不复现供体间一致性者应从列表中剔除。

### Major

**M1. 方法比较的对照集不公平、不完整，且"CKI 是唯一同器官异类型 > 跨器官异类型"的旗舰主张缺乏机制解释。**
- 证据：对比对象只有四个朴素距离度量（raw JS、Spearman、cosine、marker Jaccard；Methods "Method comparison"）。未纳入任何现代基线：scVI/Harmony 校正后的潜空间距离、基于 DE 的经典统计量、或 Augur/Milo 类状态优先级方法。作者承认未与 SAMap/SATURN/CACIMAR 定量比较（Discussion）。
- "CKI was the only metric where same-organ different-cell-type pairs had higher values than different-organ different-cell-type pairs ... This reversal reflects CKI's sensitivity to functional specialization within shared microenvironments"（Results）——该解释是纯粹的 post-hoc 叙事。另一种同样（或更）合理的机制是组织特异性基因进入 per-pair top-200 DE 集合后同时抬高 k_f 与组织信号，或跨器官对之间 k_n 系统性偏高。作者未做分解来区分。
- 更关键的是，该比较"one pseudobulk was computed per cell-type entry from its largest donor"，即**整个 4,851 对比较建立在单供体 pseudobulk 上**，供体变异完全未被刻画（作者已承认）。
- **要求**：(a) 至少加入 scVI 潜空间距离与 k_f-only 作为对照；(b) 对"同器官 > 跨器官"的反转现象给出 k_f/k_n 分解层面的解释或撤回该解释性语句；(c) 用多供体混合 pseudobulk（或 donor-average）重复关键比较。

**M2. "ω 随生物学距离单调上升"的校准主张与其自身数据矛盾。**
- 证据：正文称 "Beyond controls, ω values increased monotonically with biological distance"（Results, Calibration 节），Fig. 2 图例称 "ω increases monotonically from control splits (C) to cross-organ comparisons (X)"。但同一段给出的数字是 S = 21.31 (n=4) < D = 43.19 (n=3)，而 X = 27.31 (n=2)——**D > X，单调性在 X 处断裂**。我核验了 `mouse_pilot_v2_results.csv`：X 类仅两对（31.65、22.96），且 S 类中 "B cell (Marrow vs Spleen)" 的 ω = 42.77 高于两个 X 值。n = 2–4 的类别均值不支撑任何单调性叙述。
- **要求**：删除"monotonically"的表述，改为如实描述 C < {S, D, X} 且后三者在小样本下不可排序；修正 Fig. 2 图例。

**M3. 校准体系自我拆台：ω_cal 既不能跨数据集迁移，又仍以小鼠因子出现在摘要与正文中。**
- 证据：作者自己得出 "the mouse-derived calibration factor is therefore transferable to the Tabula Sapiens dataset but not to the brain atlas, and ω_cal should be treated as a dataset-relative quantity"（Results）。脑内基线 12.29 vs 小鼠 6.67，差异近 2 倍，且在小鼠因子下 Bergmann glia 的 ω_cal ≈ 2 变为脑内基线下的 ≈ 0.9，结论方向都变了（"the conclusion that essentially all non-neuronal classes exceed the split-half baseline does not hold under internal calibration"）。既然 ω_cal 是数据集相对量且校准因子不可迁移，小鼠来源的 6.67 体系在摘要中继续报告（"mean ω = 6.67, 95% CI [4.24, 9.24]"）只会误导读者。
- **要求**：要么统一使用各数据集 scheme-matched 内部基线（并解释为何脑与 TS 的内部基线相差 12.29/7.67 ≈ 1.6 倍——这一点本身就需要解释，作者未讨论），要么整体放弃 ω_cal 叙事，只保留 rank-based 陈述。

**M4. 6.88 倍梯度的两个端点都有已知的解释性问题，头条数字被系统性美化。**
- 证据：梯度低段 Bergmann glia "all 21 of their comparisons are intra-cerebellar, and their low ω partly reflects this anatomical restriction rather than solely a low intrinsic capacity for regional divergence"（作者自己承认，Results）；梯度低段第二位 vascular cells 是 "heterogeneous superclusters that likely aggregate multiple transcriptionally distinct subtypes"（作者承认，Results）。headline 的 6.88 = 76.83/11.17 恰好以问题最大的类为分母。
- **要求**：报告排除 Bergmann glia 的梯度（astro/vascular = 6.1 倍）作为主数字或至少并列；在 Siletti 提供的更细注释层级（subclass/cluster）上重复梯度分析，检验"astrocyte 最具区域可塑性"的结论是否被注释粒度混杂（一个内部异质性更高的注释类，其跨区 pseudobulk 差异天然更大）。

**M5. 脑分析中 k_f 的基因池被限制为 top-5,000 平均表达非 HK 基因，其他数据集无此限制，且脑 pseudobulk 的归一化顺序与其他数据集不同。**
- 证据：脑分析 "the per-pair identity-gene selection was restricted to a pre-filtered pool of the 5,000 non-HK genes with the highest mean expression"（Methods, Datasets）；且脑的 pseudobulk 是 "cell-count-weighted means of per-library (10x sample) mean expression vectors ... then normalized using Scanpy normalize_total ... followed by log1p transformation **at the pseudobulk level**"——即先聚合后归一化，而小鼠/TS 是先 per-cell 归一化再聚合。两处不一致都未被讨论其影响。
- **要求**：报告 (a) top-5,000 池筛选对梯度与候选的影响（如改为全基因）；(b) 归一化顺序（先归一后聚合 vs 先聚合后归一）对 k_n/k_f 的敏感性；(c) 在 Methods 中明确说明这些 pipeline 差异。

**M6. 单侧 permutation 检验贯穿所有 bootstrap 分析。**
- 证据：所有数据集 "Empirical P-values are computed as one-sided permutation tests"（Methods）。作者在 Limitation 18 承认不能检出 ω < null 的功能约束方向，但正文的主要卖点之一恰是"约束"叙事（Bergmann glia"最受限"）。对任何一个 �_obs > null 中位数的对，单侧检验都会系统性放大显著性。
- **要求**：主分析改双侧（或至少报告双侧版本作为敏感性），尤其在 TS 与 TCGA 的 bootstrap 结论上。

**M7. Cover letter 与正文自相矛盾，且残留过度主张。**
- 证据：Cover letter 称负相关 "demonstrating that ω measures something fundamentally different from raw JS divergence"——而正文已将该负相关定性为"partly a ratio artifact of the k_n denominator"，且明确 ω "should be understood as a composite of numerator and denominator information"。Cover letter 又称 "a standardized, assumption-free metric to quantify transcriptomic divergence ... has been lacking"（assumption-free 明显不实：HK 基因选择、top-200 截断、softmax 归一化都是假设/选择）。摘要中也仍把负相关放在最前面的结果位置。
- **要求**：改写 cover letter 与摘要，使其与正文的修正后解释一致；删除 "assumption-free"。

**M8. TCGA 部分对主线贡献微弱，且其 ω 在 3/5 癌种中被 kn_floor 饱和。**
- 证据：作者自述 "ω saturates at k_f/10⁻⁴ in 3 of 5 cancer types"（Limitation 20），且全部结论均被作者自己标注为 exploratory、不能排除成分/炎症/质量混杂（Results 与 Discussion 大段 caveats）。NN/TT 比值在分母饱和状态下意义存疑。
- **要求**：建议整体移入补充材料或删除；若保留，需报告去掉 kn_floor 后（或用更高 floor 敏感性）的 NN/TT 结果，并讨论饱和对五个癌种排序的影响。

### Minor

1. **命名误导**："Cell-state **Kinetic** Index" 与 k_n/k_f 的"rate"用语暗示时间/动力学过程，实际测量的是静态分歧比。建议改名（如 baseline-normalized divergence index）或在 Discussion 开头正面辩护。
2. **环境版本不一致**：正文写 "scanpy 1.12.1"（Methods, Computational environment），Reproducibility Guide 写 "scanpy: 1.10.4"；正文 Python 3.14.4 与 Guide 一致但与 GitHub 要求（≥3.10）的兼容性说明应统一。请核对何为真实分析环境。
3. **Fig. 2C 图例**："All show negative correlation, confirming ω captures complementary information" —— 与正文对负相关的伪迹定性冲突（正文只在 human 部分做了该修正，mouse 部分图例仍是旧口径）。
4. **S 类别内部方差**：S 类 4 对中 B cell (Marrow vs Spleen) ω = 42.77、其余 8.8–19.2（我核验的 pilot 数据），S 均值 21.31 几乎由单对驱动；正文仅给出类别 CI，未指出这一点。
5. **HK 基因数表述**：不同数据集实际匹配数不同（1,130 / 1,129 / 1,115），Methods 已有但建议在 Table 或附录统一列出。
6. **softmax 命名**：作者已注明 softmax(log1p) 等价于 L1+1 伪计数，仍建议正文直接用后者表述以减少读者困惑；同时应讨论 JS 在 L1(log1p) 分布上由少数高表达基因主导的问题。
7. **文中 mouse pilot "15 cell-type pairs"** 实为 6 C + 4 S + 3 D + 2 X 的混合，称 "pairs" 易误读为 15 个生物学比较对；建议表格化。
8. **审稿人建议名单**：cover letter 建议的 6 位审稿人均为单细胞/计算生物学知名学者，但本文脑分析部分建议增加一位神经 snRNA-seq 领域专家（编辑事务，仅供参考）。
9. **Fig. 6E** 只展示"五个最强 OPC 候选"的 observed vs expected，在全部候选未过 FDR 的情况下，该图有 cherry-picking 观感；建议改为全谱 residual 分布图（S7 已有，可合并）。
10. **重复表述**：Methods 的 "Statistical reporting" 与 Results/Supplementary Note 3 有大段重复（BH 结构性不可达的论述出现至少四次），可精简。

---

## 三、单细胞领域视角的集中评述

1. **数据来源与实验设计**：Siletti/Tabula Sapiens/Tabula Muris/TCGA 的选取合理且为领域标准资源，数字核验一致，可复现性在同类投稿中属上乘（开源包、Zenodo、种子、逐文件输出索引）。这是本稿最扎实的部分。
2. **批次/供体/区域混杂**：4 名供体、区域中位单供体占比 0.61，这是 Siletti 数据用于"区域比较"的固有限制。作者做了 within-donor 梯度复验（值得肯定），但候选 screen 与 block-shuffle null 的组合仍不能排除"library/供体水平的技术结构"驱动残差（作者在 Limitation 19 也承认 library 交换性假设）。候选层面必须补供体复现（见 C4）。
3. **基因选择循环性**：这是本方法在单细胞语境下最要害的问题——单细胞领域已有大量关于 DE 基因驱动的 pseudobulk 距离会夸大组间差异的方法学共识，本文的 per-pair top-200 DE 方案是该问题的极端形式。permutation null 能救单对检验，救不了跨对排序；而全文结论几乎全部依赖跨对排序。C2 是必须完成的修改。
4. **OPC 谱系叙事**：文献功底是有的（Hughes/Young、Foerster 背腹侧起源、TF 端点收敛等引用得当），但叙事建立在 55 个未过 FDR 的候选 + 一个条件于无信号候选集的富集检验上。OPC 的全局 ω（22.56，中间偏高）与"迁移→低 ω"的框架预测相反，作者用"migration history shapes ω only for specific region pairs"自圆其说——这使框架不可证伪。在 C3 完成前，该叙事应整体降级。
5. **方法比较公允性**：与四个朴素度量比较并垫底（AUC 0.680），再以"by design 不是分类器"辩护，这在 NAR 方法论文标准下不够。缺少与 k_f-only、与批次校正后潜空间距离、与既有 HK 归一化先例（qPCR 的 housekeeping 归一化正是"以 HK 为基线"的经典思想，Discussion 未讨论此先例，novelty 表述应据此收敛）的对比。

---

## 四、评分与推荐

**总分：5 / 10**

**推荐决定：Major Revision**

**理由**：稿件在统计诚实性、可复现性与稳健性披露上表现出色（这部分工作真实、数字可复验，且 v37 对此前审稿意见的响应是认真而非敷衍的），但当前版本的核心科学主张——ω 是一个可用的"功能分化"度量——建立在四重未解决的弱点上：(1) 无 ground-truth 验证且唯一客观指标垫底；(2) per-pair DE 循环选择使跨对 ω 排序不可解释；(3) 旗舰脑候选筛选在现有 B 与多重性设计下结构性不可达显著，OPC 叙事缺乏统计学支撑；(4) 校准因子不可跨数据集迁移、梯度主要由 k_n 驱动。C1–C4 为必须完成的实质新增分析，而非文字修改，故给 Major Revision 而非 Minor Revision。若作者完成 C1–C4 且模拟 ground truth 下 ω 优于基线，本稿有成为一篇有用的方法学/警示性论文的潜力；若模拟显示 ω 无增量价值，建议重新定位或转投专注于统计方法评论的平台。

**给编辑的置信度说明**：本审稿人愿在作者修改后复审；对 C1（ground-truth 模拟）的判断有较高信心，这是单细胞方法学领域的通行验证底线。

（完）
