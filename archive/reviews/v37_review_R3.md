# Nucleic Acids Research — 模拟审稿报告（Reviewer R3, 统计推断方向）

**稿件**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling (v37 投稿包)
**审稿人身份**: 统计推断审稿人（假设检验、零模型、bootstrap、多重检验校正、统计功效）
**审稿日期**: 2026-08-28
**审稿依据**: 主稿、补充材料、复现指南、cover letter、Table 1–2、MANIFEST；并对 results/ 下的 brain_bs_null_*、reviewer_*、phaseB_*、mouse_pilot_v2 等输出文件做了抽查核验。

---

## 一、贡献与主张总结

作者提出 CKI（cell-state kinetic index），一个受 Ka/Ks 启发的转录组分歧度量：以 housekeeping（HK）基因上的 Jensen–Shannon 散度 k_n 作为"基线分歧率"、以 identity 基因（per-pair top-200 DE 或全局 top-2,000 HVG）上的 JS 散度 k_f 作为"功能分歧率"，比值 ω = k_f/k_n 量化"经基线归一化的功能分歧"。统计推断采用 one-sided permutation test（B=1,000，标签置换并在置换样本上重做基因选择），辅以 BH-FDR、SES、bootstrap CI、split-half 经验校准（ω_cal = ω/6.67）以及若干非参数检验。软件以开源 Python 包（v0.3.1，GitHub + Zenodo）发布，附复现指南。

四个数据集上的主张：(i) Tabula Muris 校准：等同群体的经验基线 ω = 6.67（95% CI [4.24, 9.24]），由 identity 基因选择偏差导致；(ii) Tabula Sapiens：ω 与四个标准度量负相关（r = −0.36 至 −0.46），但作者自己分解后承认该负相关部分来自 k_n 分母的比值效应；(iii) TCGA：肿瘤较瘤旁组织更"同质"（NN/TT > 1，明确定位为 exploratory）；(iv) Siletti 脑图谱（886,808 nuclei、31,764 对）：10 个非神经元类之间 6.88 倍的区域分化梯度（donor 内 4.07 倍），8/10 类在 block-shuffle null 下 P = 9.99×10⁻⁴；多基因座候选筛查（multiplicative residual model）55 个 Strong 候选、37 个 raw P < 0.05，但无一个通过 BH 校正（min q = 0.949），候选列表被定位为 hypothesis-generating。

本版（v37）相对前版的主要改进值得肯定：scheme-matched 的脑内（12.29）与 TS 内（7.67）split-half 校准暴露了小鼠校准因子在脑数据不成立；k_n 估计量敏感性分析揭示梯度主要由分母驱动；within-donor 分析控制了 donor 混杂；block-shuffle null 取代了明显 anti-conservative 的旧 per-pair shuffle（旧法 36.3% 的 P 值触底）。作者对自身方法局限的披露程度远高于同类投稿，这一点在方法学论文中是加分项。但如下所述，核心统计推断链仍有实质性缺陷。

---

## 二、具体问题

### Critical

**C1. Block-shuffle null 的交换性错配：library→region 置换跨越 donor 边界，零模型与所声明的 null hypothesis 不对应。**
- 证据：Methods（multiplicative residual model 一节）："10x Chromium libraries (sample_id) were treated as blocks, and the sample-to-region assignment was randomly permuted across libraries (preserving the observed per-region library-count structure)"。每个 10x library 来自单一 donor、单一区域；该置换同时打乱了 donor→region 的对应关系，因此 ω_null 中混入了 donor 间异质性。这直接导致两个"无区域效应"参照严重不一致：我核验 results/brain_bs_null_ct_test.csv，astrocyte 的 null_mean = 46.74，而作者自己的脑内 split-half 基线（Results："an internal baseline of 12.29"）是 12.29——同一个"等同群体"概念给出相差 3.8 倍的数值，说明 block-shuffle null 是一个被 donor 混合过度散化的零分布。
- 后果（我复核的结果文件）：results/brain_bs_null_results.csv 中 p_perm_high（上尾）列显示 6,153/31,764（19.4%）的 pair 满足上尾 P < 0.05（全局零假设下期望 5%，偏离约 117 个标准差）。作者在稿件中只报告了下尾的 938/31,764（3.0%）"少于期望的 ~1,588，indicating no aggregate excess of small P-values"（Results, Anomalously similar cell-type/region pairs 一节），却从未报告自己已经算出的 6,153 这个上尾数。这属于对自身结果文件的选择性呈现：下尾缺失正是全局 ω 上移/零分布过散的镜像，不能读作"筛查无整体信号"。
- 要求：(a) 改用 donor 分层置换（在 donor 内部置换 library→region 或区域标签），使零模型与"无区域效应但保留 donor 结构"的 null hypothesis 对应；(b) 报告 p_perm_high 的分布并与下尾并列解读；(c) 用 split-half 基线（12.29）校准 block-shuffle null 的水平并解释 46.7 vs 12.3 的差距；(d) 相应重写"minimum q = 0.949 纯属 permutation resolution"的叙事——目前稿件把 FDR 失败归因于 B 与 m 的组合（"q < 0.05 could not be reached at any effect size without B ≈ 6 × 10⁵ permutations"），但若零模型本身过散，即使 B = 6×10⁵ 也仍无功效；分辨率与功效是两个不同的问题，稿件未区分。

**C2. ω 的测量学效度（measurement validity）未在任何 ground-truth 场景下建立，而标题与摘要按"功能分歧"量度进行主张。**
- 证据：作者自己的 Limitation Fourteenth："CKI has not been validated on synthetic data with known ground-truth selection signals"；Limitation Third + Results："k_f magnitudes lack independent external validation and should be interpreted as an upper bound"；Results（brain gradient）："the astrocyte-versus-Bergmann-glia contrast is predominantly a k_n effect: k_f differs only 1.2-fold ... whereas mean k_n differs 5.7-fold"。也就是说：分子循环选择（top-200 按 |μ_A−μ_B| 选出）、分母高度可变（brain per-pair k_n CV = 92.89%）、经验基线随数据集漂移 6.67→12.29、类别排序对 k_n 估计量选择敏感（global-k_n 下 ρ = −0.21）。一个 NAR 方法学论文的核心量度，其 type-I error 校准、偏差与功效完全依赖"内部一致性"论证，没有任何注入已知分歧幅度的模拟给出 sensitivity/specificity/power 曲线。
- 要求：增加模拟基准（已知注入的功能分歧幅度、已知噪声水平、不同 HK 稳定性情形），报告 permutation test 的经验 type-I error（应 ≈ α）、ω 的偏差与方差、以及检测功效随分歧幅度和样本量的变化。这是本刊对方法学论文的底线要求，"校准控制提供内部一致性检查"（Limitation Fourteenth）不能替代。

**C3. 关键统计输出与稿件数字不可互溯，且三份文档对同一参数给出互相矛盾的取值。**
- 证据一（CI 不可溯源）：复现指南 Section 7 检查清单明确让读者到 results/phaseB_bootstrap_cis.csv 核对 bootstrap CI（"[✓] Phase B: Verify bootstrap CIs (B=10,000) in results/phaseB_bootstrap_cis.csv"）。我核验该文件：Brain Astrocyte omega_mean = 103.08，CI [101.61, 104.50]；Bergmann glia 16.42 [13.47, 19.59]；OPC 50.62；choroid plexus 48.21；且 "Human (all pairs) n_pairs = 5,151"（非稿件的 4,851）。这些值与稿件主结果（astro 76.83、Bergmann 11.17、OPC 22.56、choroid 33.97）来自不同的、被 supersede 的管线；稿件引用的 CI（Supplementary Note 3.2：astrocytes "[69.41, 71.93], median 70.59"、Bergmann glia "[9.42, 10.89]"）在该文件中不存在。读者按复现指南操作将得到与稿件矛盾的数字。
- 证据二（kn_floor 三处矛盾）：主稿 Methods："the package default (kn_floor = 0) ... is the behavior used by all single-cell analyses ... The TCGA bulk RNA-seq analysis is the sole exception and applies kn_floor = 1 × 10⁻⁴"；但 Supplementary Note 1 的 Algorithm 1 第 7 行："if k_n < 1e-4: k_n <- 1e-4 // floor to prevent inflated omega"（无条件施加）；复现指南参数表："k_n floor (minimum) | 1e-4 | all analyses"。包源码（cki/core.py:174）默认 kn_floor=0 与主稿一致，则补充材料与复现指南为错。由于 k_n 中位数仅 0.0017、最小值 7.7×10⁻⁵（brain），floor 是否施加直接改变大量 pair 的 ω 值。
- 要求：(a) 在 brain_bs_null_observed_pairs.csv（31,764 行权威数据）上重算 pair-level bootstrap CI 并替换 phaseB_bootstrap_cis.csv，或明确该文件已被取代并从复现清单中移除；(b) 逐处统一 kn_floor 的表述；(c) 全面排查复现指南与稿件间的版本漂移（另见 Minor m1、m10）。

### Major

**M1. Pair-level i.i.d. bootstrap CI 在强依赖数据上无效，精度被系统性高估。**
- 证据：Supplementary Note 3.2："For each cell type, observed pair-level ω values were resampled with replacement and the median was computed"。但 astrocytes 的 5,778 个 pair 来自仅 108 个区域 × 4 个 donor（within-donor 分析显示 261 个 donor-region block）；同一区域出现在上百个 pair 中，pair 远非独立单元。i.i.d. 重采样 pair 等于假装有效样本量是 5,778，得到的 [69.41, 71.93]（宽度 ≈ 2）严重反保守。
- 要求：改用层级/聚类 bootstrap（先重采样 donor，再在 donor 内重采样 region 或 block），或混合效应模型；报告 astro vs Bergmann 梯度（6.88 倍）在聚类感知推断下的不确定性——目前稿件对"梯度"本身从未做过任何正式检验，只检验了各类均值是否高于各自零分布。

**M2. 校准因子"可迁移性"的推断逻辑不成立：CI 包含 ≠ 等价。**
- 证据：Supplementary Note 3.5 / Results："the Tabula Sapiens internal baseline was 7.67 ..., which lies inside the mouse-derived CI [4.24, 9.24]; the mouse-derived calibration factor is therefore transferable to the Tabula Sapiens dataset"。小鼠基线来自 n = 6、CV ≈ 52% 的控制组（均值 6.67、范围 1.59–12.16），其 CI 横跨 2.2 倍；如此宽的区间几乎可以"包含"任何合理的数据集基线，"transfers to Tabula Sapiens"是不充分证据下的接受性结论——作者在其他场合自己也承认需要 TOST（Results："formal equivalence testing (e.g., two one-sided tests, TOST) with a larger calibration sample would provide stronger statistical evidence"）。此外脑内基线 CI [12.12, 12.47]（宽度 3%）与小鼠 CI（宽度 >100%）精度相差一个数量级以上，直接比较两个区间得出"approximately 1.8-fold higher"在精度上是不对称比较；且脑内 split-half 只取"每类 ≥200 nuclei 的三个区域"（Methods），属于选择最大群体的方便样本。
- 要求：要么扩充小鼠 split-half 控制组并做 TOST（预设等价界），要么删除"transferable"的表述、将 ω_cal 一律降格为"仅在数据集内部使用"；明确说明脑内校准的抽样规则及其对 12.29 的影响。

**M3. 摘要、标题与 cover letter 的主张强度超出正文分解分析所能支持的范围。**
- 证据：Abstract："Brain analysis revealed a 6.88-fold regional differentiation gradient"（pooled、含跨 donor 成分，且主要由 k_n 驱动）；正文自己的结论是"the ω gradient therefore chiefly reflects differences in how stably housekeeping programs are maintained across regions ... not proportionally larger functional-gene divergence"（Results），within-donor 梯度为 4.07 倍。标题的核心词 "Baseline-Normalized Transcriptomic Remodeling" 与 "functional divergence rate" 的命名在分母主导 + 基线不可跨数据集迁移的现实下名不副实——按作者自己的分解，astrocytes 的"最高分化"实际上是"HK 基因最稳定"（k_n 最低）。Cover letter 仍写"demonstrating that ω measures something fundamentally different from raw JS divergence"，与主稿"composite of numerator and denominator information"（Discussion）的直接矛盾；cover letter 还声称"which we verified is not driven by gene-set dimensionality"，而 Supplementary Note 3.6 自己承认该 Dirichlet 模拟"does not simulate the variance-based gene selection mechanism that generates the ω inflation"——模拟验证的是一个 strawman。
- 要求：摘要改为以 within-donor 4.07 倍与"分母主导"为主表述；"functional divergence/kinetic index"的措辞全文降格（如 "baseline-normalized divergence ratio"）；cover letter 与主稿措辞对齐。

**M4. 谱系富集检验是条件于未经 FDR 支持的候选集合的事后推断（post-selection inference），且 multiplicative residual 的均值构造在高方差类别上机械地产生低残差。**
- 证据：Results："the three oligodendrocyte-lineage classes account for 40.2% of all pairs but 50 of the 55 Strong candidates (fold enrichment 2.26; hypergeometric P = 4.5 × 10⁻¹⁵...)"。问题有三层：(i) 富集检验以 55 个 Strong 候选为条件，而这 55 个候选本身没有任何多重检验支持（min q = 0.949），"显著富集"不能为候选集体背书；(ii) expected_ω = μ_ct × μ_pair / μ_grand 用类别均值构造期望，而 ω 右偏且类别方差悬殊（OPC 22.56 ± 14.55、choroid 33.97 ± 35.89，per-cell-type k_n CV 36.5%–69.8%），均值型期望使高方差类别在低分歧区域对上系统性出现低残差——"oligodendrocyte lineage 集中"可能是异方差的人为产物而非生物学；(iii) hypergeometric 检验把 31,764 个强依赖的 pair 当作独立抽样单元（作者在别处自己承认"Per-signal tests are not independent"）。
- 要求：以中位数或类别内标准化（如按各类别残差的经验分布标准化）重定义残差；在 block-shuffle null 下按类别重算富集（即用置换的类别标签在零模型内构造富集零分布，而非解析 hypergeometric）；明确该检验只能回答"候选集中于哪些类别"，不能回答"候选是否为真"。

**M5. 类别级检验的推断单元与 P 值报告不规范。**
- 证据：Results："For 8 of 10 cell classes, regional structure significantly raised the mean ω relative to the null at the permutation resolution floor (one-sided P = 9.99 × 10⁻⁴, standardized effect sizes 4.8–15.8)"。SES = 15.8 的计算把 5,778 个相依 pair 的均值与基于同样相依结构的 null_sd（astro 1.90）相比，依赖性使 SES 数值膨胀（有效自由度远小于 pair 数）；Bergmann glia 的 P = 0.031 在 m = 10 的 BH 下 q ≈ 0.31，稿件称"marginal significance"不成立。另外 Results 声称"within-donor values are systematically lower"与 results/reviewer_within_donor_gradient.csv 不符：fibroblast（16.67 vs 13.99 pooled）、ependymal（16.22 vs 14.52）within-donor 反而更高，vascular 持平——"systematically"应为"for the well-sampled high-ω classes"。
- 要求：类别级检验采用聚类感知的零分布（region 或 donor-region block 级置换统计量）；Bergmann glia 改为"not significant after BH"；修正"systematically lower"的表述并逐类报告 within-donor 与 pooled 的差值。

**M6. TCGA 分析中 3/5 癌种的 ω 已被 kn_floor 饱和，此时 ω 退化为 k_f 的单调变换，"基线归一化"名存实亡。**
- 证据：Limitations Twentieth："the TCGA analysis applies kn_floor = 1 × 10⁻⁴ (the aggregate tumor-versus-normal k_n ranged from 3.0 × 10⁻⁵ to 1.9 × 10⁻⁴ across the five cancer types, so ω saturates at k_f/10⁻⁴ in 3 of 5 cancer types)"。在这 3 个癌种中，NN/TT 比值、PAM50 梯度（Luminal A 123.4 vs Basal 97.8）实质上是 k_f 的比较，与 CKI 的核心卖点无关。同时 NN/TT 比值没有任何不确定性量化（Fig. 4A 只给中位数；TT/TN pair 为"Maximum 2,000 random pairs"的子抽样，其随机性未传播到报告值）。
- 要求：逐癌种报告 k_n 分布与 floor 的位置；对饱和癌种直接以 k_f 呈现结果；对 NN/TT 与 TN 比值补 pair-resampling bootstrap CI（并考虑子抽样的随机性）。

**M7. 多个 omnibus 检验与相关检验在强依赖 pair 集上未做依赖修正，且跨分析的多重检验无全局记账。**
- 证据：Statistical reporting："Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05 without additional correction"；"Spearman correlation between ω and each standard metric conditional on k_n became positive in all four cases (partial r = +0.11 to +0.54, all P < 1 × 10⁻¹⁴; 95% bootstrap CIs excluding zero)"——这些 P 值把 4,851 个共享细胞类型的 pair 当独立观测。稿件正文报告的正式检验（类别级 10、人类 17、小鼠 15、TCGA 5、per-pair 31,764、富集 2、tier 敏感性 19、各种 Spearman/MW/KW/JT）总数数十个，"BH within each dataset"只覆盖其中一部分。
- 要求：至少 (i) 对依赖结构敏感的 Spearman/MW 检验改用 block/类别级置换或聚类稳健方法；(ii) 给出一个全稿检验清单与校正范围声明，说明哪些是确认性、哪些是探索性。

### Minor

- **m1. 软件环境版本不一致**：主稿称 scanpy 1.12.1、Python 3.14.4；复现指南 Section 1.1 称 scanpy 1.10.4。请统一（并说明 3.14.4 是否真实存在——这是极前沿的版本号，复核指南可信度）。
- **m2. 数据卫生**：results/mouse_pilot_v2_results.csv 中 "C: hepatocyte (Liver)" 与 "C: endothelial cell (Heart)" 各出现两次（完全重复行）。虽不影响均值（6.67、median 6.46 我已核验一致），但应去重并说明来源。
- **m3. 上尾/下尾报告不对称**：brain_bs_null_results.csv 同时计算了 p_perm 与 p_perm_high，稿件只报告下尾（见 C1）。即便不重做零模型，也应在补充材料完整给出两侧分布。
- **m4. SES 循环表述**：Supplementary Note 3.2："standardized effect sizes are typically > 1.0 for biologically meaningful comparisons"——用"biologically meaningful"定义"SES > 1"，再用 SES 支持生物学意义，属循环论证；删除或改为外部基准。
- **m5. Figure 2C 图说未随 v37 修订**："All show negative correlation, confirming ω captures complementary information"——与正文"partly a ratio artifact of the k_n denominator"（Results）矛盾，属旧版残留。
- **m6. 小鼠 S/D 类别 n = 3–4**（"S category: mean ω = 21.31, n = 4 pairs"）：虽已加 CI 提示，建议在正文明确标注"illustrative, no inferential weight"，或移入补充材料。
- **m7. 复现指南残留旧参数**：参数表"Permutation null iterations | 10000 (per-signal P-values) | Phase B (C-S3)"对应已被取代的管线；"k_n floor 1e-4 all analyses"见 C3。建议整表按 v37 权威管线重写。
- **m8. Brain split-half 的抽样规则表述含糊**：Methods "for each cell class, the three regions with at least 200 nuclei were split into random halves (B = 50 splits per population; 29 populations)"——"三个区域"是每类选 3 个最大区域还是全部合格区域？29 个 population 如何对应 10 类 × 3？请给出 population 清单（reviewer_brain_splithalf_raw.csv 已存在，应在补充材料引用）。
- **m9. One-sided 检验的双向不完整**：主检验为上尾（ω 偏大），migration 筛查为下尾，作者在 Limitation Eighteenth 承认不检测 functional constraint；建议在同一张表/图中对称呈现两尾结论（与 m3 合并处理）。

---

## 三、对作者修稿的总体统计要求

1. 重建 brain 零模型：donor 分层置换 + 与 split-half 基线的水平校准；同时报告两尾 P 值分布（C1、m3）。
2. 增加 ground-truth 模拟：type-I error 校准、偏差、功效曲线（C2）。
3. 全部 CI 改为聚类/层级 bootstrap；梯度本身给出正式检验（M1）。
4. ω_cal 的跨数据集陈述降格或以 TOST 重做（M2）。
5. 残差模型改为中位数/方差标准化版本并重做富集（M4）。
6. 摘要、标题、cover letter 与正文分解结论对齐（M3）。
7. 修复文档间数字与参数矛盾，重出权威 CI 文件（C3、m1、m5、m7）。

---

## 四、评分与推荐决定

**总分：4.5 / 10**（NAR 标准：1–3 拒稿，4–5 Major Revision，6–7 Minor Revision，8+ 接收边缘）

**推荐决定：Major Revision**

理由：本稿的可取之处真实存在——方法框架有新意，作者的自我批判和零模型迭代（放弃 anti-conservative 的 per-pair shuffle、引入 block-shuffle、暴露校准不可迁移）显示出少见的统计诚实，可核验数字（6.67/12.29/7.67、min q = 0.949、938、8/10 类、hypergeometric 4.5×10⁻¹⁵ 等）与 results/ 文件一致。但按本审稿人核验，(i) block-shuffle null 的交换性单元与 null hypothesis 错配，per-pair 筛查实际功效存疑且作者只报告了对自己叙事有利的一侧尾部；(ii) 核心量度 ω 无任何 ground-truth 效度验证，且已被作者自己的分解证明是分母主导的复合信号，而标题/摘要/cover letter 仍按"功能分歧"主张；(iii) 复现指南指向的 CI 文件与稿件数字矛盾、kn_floor 三处表述冲突。这些问题均为可修复的统计设计与报告问题，而非概念破产，因此不建议拒稿；但修复需要重新设计零模型、重算不确定性并系统降格主张，工作量超出 Minor Revision 范畴。

若作者能在修稿中完成 C1–C3 与 M1–M4，本审稿人愿意在下一轮重新评估；届时若模拟显示 permutation test 的 type-I error 校准且 ω 的偏差可量化，评分有望进入 6–7 区间。
