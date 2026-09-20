# Expert 3 审稿意见：生物学 / 单细胞基因组学

**稿件**：CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling（NAR 投稿版 v35，2026-08-28）
**审稿人角色**：生物学 / 单细胞基因组学审稿专家
**审阅材料**：主稿件全文、补充材料全文、复现指南全文、REVIEWER_GUIDE.md（v5→v35 修订清单）

---

## 总体评价

**倾向：大修（Major Revision）。**

从生物学角度看，CKI 的核心构思（以 HK 基因散度作为内源性基线、把转录组比较从"绝对距离"转向"基线归一化功能散度"）是新颖且有价值的；脑区分析的自证式降级（block-shuffle null、0 个 FDR 显著、候选列表定位为 hypothesis-generating）、TCGA 结果的 exploratory 措辞、以及 OPC/成熟 oligodendrocyte 解读中"consistent with but not proof of"的克制，均体现了良好的审慎态度。方法论讨论（HK 中性假设缺陷、HVG 选择膨胀、per-pair DE 循环性、ω_cal 跨方案迁移）在生物学的可辩护性上是合格的。

**但存在三类硬伤，必须在接受前解决**：
1. **补充材料与复现指南未随 v35 更新**，与主稿件直接矛盾（脑区置换 null 方法、Strong 候选数、κ_n 统计量、脑区全局均值）——对一篇以方法/统计严谨性为核心的期刊投稿，这是严重的一致性/诚信问题；
2. **图注与正文直接矛盾**（Supplementary Figure S7B 的 "OPCs 0 Strong" 对正文 "OPCs 27 Strong"）；
3. **若干生物学归因过度或混淆**（Bergmann glia 解剖限制、vascular/fibroblast 循环交换归因、n=1 细胞类型领衔保守性排序、摘要 "millions of cells"）。

以下逐条列出，按 Critical → Major → Minor → 已妥善解决项 组织。

---

## Critical 问题（必须修改，否则不能接受）

### C1. Supplementary Figure S7 (B) 图注与正文 Results 直接矛盾：OPCs "0 Strong" vs "27 Strong"

- **位置**：补充材料 line 125（S7 图注）；对照主稿件 line 80-82（Results "OPCs contributed 27 Strong candidates (16 with raw P < 0.05)"）。
- **问题**：S7B 图注写 "OPCs (0 Strong despite highest motility among the 10 non-neuronal classes) provide a key internal consistency check, supporting that the model detects developmental-origin signatures rather than general motility"。这与 v35 正文的核心结果（OPC 是 Strong 候选最大贡献者，27/55，16 个 raw P<0.05；正文因此给出"consistent with OPC 迁移/巡查"的叙事）**完全相反**。这是 v5 旧叙事的遗留（旧分析中 OPC 确实 0 Strong），v35 重算后图注未更新。审稿人若按图注核对正文会直接判定稿件内部矛盾。
- **建议**：S7B 图注改为 "OPCs contributed the largest share of Strong candidates (27 of 55), consistent with their known motility/surveillance; interpretation is hypothesis-generating because no candidate survives FDR correction"。并全局检索所有 "0 Strong" 残留表述。

### C2. 补充 Note 3.3 与复现指南 §5.3 描述的是已被弃用的 per-pair 置换 null，与正文 block-shuffle null 矛盾

- **位置**：补充材料 line 62-63（SN3.3）；复现指南 line 166（§5.3c）；对照主稿件 line 35（Methods block-shuffle）、line 80-87（Results）。
- **问题**：SN3.3 全文仍描述"per-signal empirical P-values via permutation (B = 10,000)，每对区域内随机打乱 cell type labels"，并报告 **30 个 Strong 候选**（16 个达到 P 值下限：6 astrocyte + 10 oligodendrocyte；14 个 P≥0.76）。复现指南 §5.3c 完全一致。但 v35 正文已改用 **block-shuffle null（以 10x library 为 block，B = 1,000）**，报告 **55 个 Strong 候选**（37 个 raw P<0.05，BH 后 min q = 0.949），并明确说明旧 per-pair 置换"anti-conservative（36.3% 达 P 值下限）"、已被替换。即：补充材料与复现指南的"统计检验方法"章节还在教读者复现一种被正文否定掉的方法，且计数（30 vs 55）和显著性结构（astro/oligo vs OPC/COPC）完全不一致。
- **建议**：将 SN3.3 与复现指南 §5.3 重写为 block-shuffle null 描述（B=1,000，m=31,764，min q=0.949，55 Strong / 37 raw P<0.05），并将旧 per-pair 实现按正文口径改写为"早期反保守版本、已被弃用"的历史说明。

### C3. 补充 Note 3.5 / 3.7 与复现指南 §5.4 保留 v5 旧数值，与正文多处关键数字矛盾

- **位置**：补充材料 line 67（SN3.5）、line 71（SN3.7）；复现指南 line 174（§5.4a）、line 180（§5.4c）；对照主稿件 line 54、line 56、line 75、line 35。
- **问题**（逐项列明矛盾对）：
  - **脑区全局均值**：正文 `ω_grand = 32.56`（ω_cal 4.88，line 54/75/35）；SN3.5 与复现指南为 `8.01`（ω_cal 1.20）。
  - **astrocyte**：正文 `76.83`（ω_cal 11.52）；SN3.5 为 `14.36`（ω_cal 2.15）。
  - **Bergmann glia**：正文 `11.17`（ω_cal 1.67）；SN3.5 为 ω_cal `0.36`（意味着正文"所有 10 类均高于经验基线"的结论在 SN3.5 中被写成"Bergmann 低于基线"）。
  - **k_n 跨 pair 变异**：正文 `CV = 92.89%`、`per-pair vs global-k_n Spearman ρ = +0.181`（P=9.38e-232，line 56）；SN3.7 与复现指南为 `CV = 97.35%`、`ρ = −0.027`（P=9.96e-7）。**符号都反转了**（−0.027 → +0.181），这直接改变了对"per-pair k_n 必要性"论据的表述。
- **影响**：上述数字均为主稿件关键结果；补充材料与复现指南作为"Statistical Testing Details"与"Reproducibility Guide"，读者按之核对将得到与正文不可调和的数值。v35 修订只更新了主稿件与部分图注（S11 图注已是新值），未同步 SN 正文与复现指南。
- **建议**：全面同步 SN3.5、SN3.7、复现指南 §5.4 至 v35 数值；建议建一个"跨文档关键数字一致性核查表"（正文↔SN↔复现指南↔图注）作为投稿前清单。

---

## Major 问题（建议修改）

### M1. TCGA "exploratory" 定位未贯穿到摘要与 Results 标题

- **位置**：摘要 line 11（"Cancer analysis **revealed** transcriptional convergence across genetically diverse tumors"）；Results 标题 line 61（"Cancer analysis **reveals unexpected** transcriptional convergence"）；对照正文 Results line 63-65 与 Discussion line 93 的 exploratory 表述。
- **问题**：正文（Results + Discussion）已充分列举 bulk 伪影（细胞组成/纯度、基质与免疫浸润、瘤周炎症、RNA 质量）并反复声明"exploratory in nature / descriptive only"，但摘要与 Results 标题仍使用 "revealed / reveals unexpected" 的确定性语言。审稿人要求 exploratory 定位"一致贯穿"，目前摘要与标题是缺口。
- **建议**：摘要改为 "Cancer analysis **suggested** potential transcriptional convergence ... (exploratory, confounded by bulk cell-composition shifts)"；Results 标题改为 "Cancer analysis **suggests potential** transcriptional convergence（exploratory）"。图 4 图注（line 115）的 "indicating that normal individuals differ more from each other than tumors differ from each other" 也建议加 "at bulk resolution, pending single-cell validation"。

### M2. 摘要 "a human brain single-nucleus atlas from millions of cells" 与实际分析规模不符

- **位置**：摘要 line 11；对照主稿件 line 72（atlas ~3.3M nuclei，实际分析 888,263 非神经元核 / 过滤后 886,808）。
- **问题**：atlas 全量约 330 万核，但本研究只分析了其中 88.8 万非神经元核（且神经元被明确排除）。"validated across four datasets: ... a human brain single-nucleus atlas from millions of cells" 易被读成"用数百万细胞做验证"。
- **建议**：改为 "a human brain single-nucleus atlas（888,263 non-neuronal nuclei analyzed）"，或在摘要中明确 "focusing on non-neuronal classes"。

### M3. 跨物种直接比较不当：mouse 27.31（X 类别，n=2）vs human 21.61（n=4,851 全均值）

- **位置**：主稿件 line 57（"Human ω values ranged from 1.35 to 87.69 (mean 21.61, median 19.65, n = 4,851 pairs), substantively lower than mouse (mean 27.31)"）。
- **问题**：(1) mouse 27.31 对应 mouse pilot 的 X 类别（cross-organ，n=2），是一个两对的子集均值，而 human 21.61 是全部 4,851 对的整体均值——类别与样本量均不可比；(2) 同一段落随后用"不同 k_f 基因选择策略（per-pair DE vs global HVG）"解释该差异，但 27.31 若出自 pilot（per-pair DE 混合方案），与 human 同方案，则该解释在逻辑上不成立；(3) 稿件自己在 Discussion line 91、line 93 反复声明"绝对 ω 跨数据集不可比、应按秩比较"，此处直接比较绝对值与之矛盾。
- **建议**：删除"substantively lower than mouse (mean 27.31)"的直接比较，或改为可比的同类别比较并加显式警示：如 mouse S 类别（same cell type across organs，21.31，n=4）vs human same-CT cross-organ（15.83，n=59），并注明 n 差异大、仅作方向性观察。

### M4. S/D/X 比较类别定义在正文与图注间冲突

- **位置**：主稿件 line 53（Results："Same cell type across different organs (S category: mean ω = 21.31, n = 4 pairs)"）；Figure 2B 图注 line 113 与 Figure 3D 图注 line 114（"S (same sub-organ)"）。
- **问题**：正文把 S 定义为"same cell type across different organs"，图注却写 "S (same sub-organ)"；而图注中的 "X (cross-organ)" 又似乎与正文的 S 定义重叠。四条类别（C/S/D/X）的完整定义在图注与正文之间不统一，直接影响 Fig 2 的核心验证叙事（"ω 随生物学距离单调递增：S < D"）。
- **建议**：统一定义并逐字对齐：C（same cell type, same organ 对照/校准）、S（same cell type, different organs）、D（different cell type, same organ）、X（different cell type, different organs）。图注若指 "same sub-organ" 则需另设类别或改名，避免与正文冲突。

### M5. 数值不一致：Tabula Sapiens pairs 4,851 vs 5,151；参数扫描 AUC 0.786 vs 0.847

- **位置**：
  - pairs：主稿件 line 33/56/58/59（4,851）；补充材料 line 62（"Tabula Sapiens: 5,151 pairs"）；复现指南 line 101（"all 5,151 cell-type pairs"）。
  - AUC：主稿件 line 49（"identity-only ... AUC = 0.786"）与 Supp Fig S1 图注 line 119（0.786）；补充 SN1.3 line 20（0.847）与 Supp Table 1 line 90（0.847）。
- **问题**：C(102,2)=5,151，但正文统一使用 4,851（可能剔除了 300 个未达标 pair），补充与复现指南未同步；AUC 在"正文+图注"与"SN+Supp Table 1"之间为 0.786 vs 0.847 的直接矛盾（同一次 sweep 的同一配置）。
- **建议**：统一为 4,851 并注明剔除规则（如 min cells per group 或未命中基因）；核实 AUC 真值并全稿统一。

### M6. FDR 检验数表述混乱：cell-type 级 vs per-pair 级（m=31,764）

- **位置**：主稿件 line 41（Statistical reporting："The number of tests is determined by the number of cell types (10 for brain, 17 for human per-cell-type, 15 for mouse), **not** the number of region pairs"）；对照 Methods line 35（brain residual screen "Benjamini-Hochberg FDR correction was applied across all m = 31,764 pairs"）与 line 26（bootstrap per-pair）。
- **问题**：同一 Methods 内部存在两套 FDR：脑区 bootstrap 每 pair 有 P 值（08c，31,764），而 line 41 声称检验数按 10 个细胞类型计；同时 block-shuffle residual screen 又在 m=31,764 上做 BH（min q=0.949）。读者无法判断：脑区 31,764 个 per-pair bootstrap P 值到底是否经过 BH、若按 10 类汇总又是如何汇总的。此外 "17 for human per-cell-type" 与 4,851 对 per-pair 检验的关系也未交代。
- **建议**：在 Statistical reporting 中明确两套检验各自的检验单位与 BH 范围：(a) 细胞类层面的 block-shuffle 检验（10 类，BH 按 10）；(b) residual screen 的 per-pair 检验（31,764，BH 按 m=31,764，min q=0.949）。删除或改写 "not the number of region pairs" 以避免与 (b) 冲突。

### M7. Bergmann glia 的"最保守"生物学解读被解剖限制混淆

- **位置**：主稿件 line 73（"Bergmann glia showed the lowest mean ω (11.17 ± 3.50, n = 21 pairs across 7 regions)"）、line 75、line 86（"developmentally fixed, transcriptionally constrained state in the adult cerebellum"）。
- **问题**：Bergmann glia 是**小脑特异性**放射状胶质细胞，其 21 个 pair 全部落在 7 个小脑亚区之间（即全部是"小脑内比较"）。低 ω 更简单的解释是：同一个小脑结构的微环境相似、比较范围受限，而不必归因于"发育上固定、转录受约束"。同时，6.88 倍梯度两个端点（astrocyte：108 区域全域分布 vs Bergmann：7 个小脑亚区）的区域覆盖差异巨大，梯度数值在一定程度上是分布广度差异的产物。正文虽在 Supp Fig S6C 报告了"ω vs n_regions 正相关（ρ 显著）"，但主叙事未将该混淆前置。
- **建议**：在 Results 明确加一句："Bergmann glia are restricted to the cerebellum; their cross-region comparisons are all intra-cerebellar, so their low ω may partly reflect anatomical restriction rather than developmental constraint alone"。并讨论 n_regions 与 ω 的相关性对"梯度"解释的贡献。

### M8. vascular/fibroblast 低 ω 的"循环/脑膜交换"归因在生物学上不准确

- **位置**：主稿件 line 76（"the low ω values for vascular cells and fibroblasts are consistent with continuous turnover and exchange through the circulatory and meningeal systems"）；line 75（"Vascular cells and fibroblasts encounter relatively uniform extracellular environments ... the blood-brain barrier (34) and meningeal structures (35) impose similar constraints"）。
- **问题**：(1) 血管细胞（内皮 + 周细胞/平滑肌）是**驻留细胞**，并不随血液循环"周转与交换"；随循环交换的是血细胞（免疫细胞）。把低 ω 归因于"持续循环交换"在细胞生物学上不成立。(2) 引文 (34) 为 Schaffenrath et al. 2024《Characteristics of blood-brain barrier heterogeneity between brain regions》——该文核心结论恰恰是 BBB 属性存在**区域异质性**，用它来支持"BBB 在不同解剖位置施加相似约束"属于引用-内容不符。(3) 更可能的解释未被讨论：snRNA-seq 对血管细胞取样稀少（9,586 核覆盖 82 区域），且血管异质性主要由血管段（动脉/静脉/毛细血管）而非脑区决定；fibroblast 则多为脑膜来源，天然均匀。
- **建议**：改写为"vascular/fibroblast 的低 ω 与其以血管段/脑膜来源为主的共享核心程序一致，且不排除取样限制；不应归因于循环周转"。修正 (34) 的引用方式或改引支持"血管程序区域保守"的文献。

### M9. 跨器官保守性排序以 n=1 细胞类型领衔，与自身 n≥5 建议冲突

- **位置**：主稿件 line 69 与 Table 2（line 188-207）；补充 SN3.9（line 74-75）。
- **问题**：正文开场即给出 "Hepatocytes (mean ω = 8.57, **n = 1**) and B cells (mean ω = 9.36, **n = 1**) were among the most conserved"，把样本量为 1 的估计排在最前面并作生物学陈述（"most conserved"）。虽然随后有 n<5 警示，但叙事的强调顺序已在传递生物学结论。特别地，hepatocyte 在 Tabula Sapiens 中几乎只存在于肝脏，一个 n=1 的"跨器官 pair"其定义本身就需要交代（hepatocyte 出现在哪两个器官）；erythrocyte 的 SD=23.07（≈均值 29.36）同样表明 n=3 估计极不稳定。
- **建议**：叙事顺序改为先呈现 n≥5 的可靠排序（CD8+ T、Plasma、Macrophage、NK、Endothelial、Neutrophil 等），把 n<5 条目（尤其 hepatocyte/B cell/erythrocyte）降级为"名录性参考"，或直接在正文表格中用加粗/斜体标注 n<5。

### M10. "supercluster_term 提供 transcriptionally coherent cell classes" 对 vascular/fibroblast 过强

- **位置**：主稿件 line 72（"where the supercluster_term annotation provides well-defined, transcriptionally coherent cell classes"）。
- **问题**：神经元因亚型异质性被排除的理由充分，但同样的逻辑部分适用于"vascular cells"（在 Siletti 数据中合并了不同血管段内皮、周细胞、血管平滑肌等转录组上可区分的群体）与 "fibroblasts"（脑膜 vs 血管周来源）。把这两类称为"well-defined, transcriptionally coherent"并用于跨区域比较，存在同类别假设的部分违背；若两类中血管段构成随区域变化，ω 会被污染。
- **建议**：在 Methods/Results 承认 vascular cells 与 fibroblasts 是超类（heterogeneous superclusters），并将这一点列入解释低 ω 的候选机制（与 M8 合并处理）。

### M11. BH-FDR 引用错配（ref 23 = Storey & Tibshirani 2003）

- **位置**：主稿件 line 41（"Benjamini-Hochberg FDR correction ... (23)"）；References line 155（ref 23 = Storey & Tibshirani 2003, q-value 方法）。
- **问题**：正文明确写 "Benjamini-Hochberg"，却引用 q-value（Storey）论文；复现指南 §5.2 明确实现的是 `benjamini_hochberg()`。引用与方法名不匹配。
- **建议**：改引 Benjamini & Hochberg (1995, JRSS B) 与/或 Benjamini & Yekutieli（如适用）；若实际使用 q-value 则统一方法名。

### M12. Data availability 声明与投稿包实际不符

- **位置**：主稿件 line 100（"All analysis notebooks and processed data matrices are included in the Supplementary Data"）。
- **问题**：v35 投稿包（MANIFEST）只含 DOCX/PDF/图表，不含代码或数据矩阵；复现指南将代码指向 GitHub、数据指向 Zenodo。按 NAR 对数据/代码可获得性的要求，该句为不实声明。
- **建议**：改为 "All analysis notebooks and processed data matrices are available at GitHub (tag v0.3.1) and Zenodo (DOI ...)"，或确实把代码/结果矩阵打包进 Supplementary Data。

### M13. OPC 整体 ω（22.56，中等偏高）与"迁移/交换细胞应低 ω"框架存在张力，未讨论

- **位置**：主稿件 line 73（OPC mean ω = 22.56）、line 76（"Cell types that recently migrated... should show low inter-regional ω"）、line 82（OPC 迁移叙事）。
- **问题**：框架预测"持续迁移/交换的细胞 → 区域间低 ω"，但 OPC 整体 ω=22.56 处于 10 类中的中高段（高于 microglia 13.50、fibroblast 13.99）。正文只聚焦 27 个低 ω Strong pair，未解释为何 OPC 的**全局** ω 并不低（如果 OPC 全脑巡查/交换充分，其整体区域分化应被抹平）。两处表述存在概念张力。
- **建议**：在 Results 加一句讨论："OPC 的全局 ω 为中等偏高，说明其区域转录分化并非整体缺失；27 个 Strong 候选代表少数区域对之间的异常相似性，其与整体迁移假说的关系需要 lineage-tracing 验证"，或调整框架的预期。

---

## Minor 问题（建议修改）

- **m1**：摘要 "6.9-fold"（line 11）vs 正文 "6.88-fold"（line 73/94）——建议统一为 6.88。
- **m2**："9 of 10 cell classes ... P = 9.99 × 10⁻⁴"（line 74、line 87）计数内部矛盾：若 Bergmann glia 为 P=0.031（line 74 明示）、choroid plexus 为 P=0.76，则不可能有 9 类都取到 floor P；应表述为"8 类 P=9.99×10⁻⁴（SES 4.8–15.8），Bergmann P=0.031（SES 2.0），合计 9/10 类在 α=0.05 显著；choroid 不显著（P=0.76）"。line 87 的 "9 of 10 classes, P = 9.99 × 10⁻⁴" 同样需改。
- **m3**：SN3.11(4)（补充 line 79）"HVG count of 2,000 (human/brain)" 与 human/brain 实际使用 per-pair top-200 DE（hybrid scheme）矛盾；2,000 HVG 仅用于 mouse full matrix。需修正措辞。
- **m4**：SN3.11(3)（补充 line 79）参数扫描网格 {500, 1000, 2000, 3000, 5000} 与 SN4.4（补充 line 88）{50, 100, 200, 500, 1,000, 2,000} 不一致。
- **m5**：Fig 2D 图注（line 113）"Pathway enrichment in the k_f component" 与默认 identity-only 配置（w_pathway=0）并列展示，易误导；建议注明为 parameter sweep 的补充分析。
- **m6**：Methods 脑区 10 类核数（line 31，合计 886,808）与总核数 888,263 并列，建议明确括号内为过滤后计数，避免读成两类总数不一致。
- **m7**：Table 2 中 erythrocyte（29.36 ± 23.07, n=3）与 hepatocyte/B cell（n=1）作为"最特异/最保守"端点，建议在表注中再加粗 n<5 警示（正文已提示但表内无标注）。
- **m8**：OPC 迁移引文 Tsai 2016（发育期沿血管迁移）用于支撑"adult 持续 surveil"略弱，建议补成人 OPC 巡查/增殖文献。
- **m9**：癌症 HK 失调的引证 ref 47（Butte 2001）较泛，建议直接讨论 Warburg/糖酵解基因上调对 k_n 的潜在影响，并将敏感性分析（r>0.95）在该语境下复述。
- **m10**：摘要（M1 相关）与 Figure 4 图注（line 115）的确定性表述需与正文 exploratory 口径统一（见 M1）。

---

## 已妥善解决的上一轮项（确认项）

以下为 v5 审稿中提出、v35 中**正文层面**已妥善落实、本审稿予以确认（但注意其中两项的补充材料未同步，见 C1/C2/C3）：

1. **脑区 block-shuffle null 重算并整体降级**（v5 C1）：正文 Methods line 35、Results line 80-87、Discussion line 94 均一致采用 block-shuffle null（B=1,000，m=31,764，min q=0.949，0 个 FDR 显著），脑区候选明确"hypothesis-generating / prioritized for lineage-tracing"——定位恰当，正文自洽。⚠️ 但补充材料/复现指南未同步（见 C2）。
2. **TCGA 收敛结论降级为 exploratory**：Results line 63-65 与 Discussion line 93 的 caveat 清单（细胞组成/纯度、基质与免疫浸润、瘤周炎症、RNA 质量、n=2-5 描述性）完备且切中要害；"单细胞/去卷积验证不可少"的结论性语句合理。⚠️ 摘要与 Results 标题未对冲（见 M1）。
3. **HK 基因中性假设的坦诚讨论**：Discussion line 91 承认 HK 是经验定义、无机制性中性依据，并以敏感性分析（r>0.95）作为实用代理；SN1.2 一致。
4. **PAM50 / Edmondson 小亚组警示**：Results line 65 明确 Normal-like n=7、Edmondson G4 n=11 的统计功效不足及增殖分数混淆。
5. **paired TCGA 去除正式检验**：line 64 明确"descriptive statistics only, without P-values"，与复现指南 §5.5 Phase D 一致。
6. **单侧置换检验理由**：Methods line 26 与 SN3.10 给出方向性假设论证。
7. **Discussion 限制清单**（#13 跨数据集阈值不可比、#14 无 ground-truth 模拟验证、#15 参数依据、#17 ω_cal 跨方案迁移、#19 block-shuffle 假设、#20 k_n floor）覆盖全面、语言克制。
8. **OPC 解读措辞**："consistent with but by no means proof of"（line 82）、"one candidate interpretation among several"（line 84）——生物学叙事克制得当；Foerster 2024 用于成熟 oligodendrocyte 发育起源的引用恰当。⚠️ 但图注 S7B 未同步（见 C1）。
9. **脑区 per-cell-type pair/region 计数自洽**：各细胞类型 pair 数 = C(n_regions,2)，总和 = 31,764（已逐类验算：21+3,321+5,671+3,403+780+5,671+1,326+5,778+5,778+15 = 31,764）；TCGA 样本总数 3,596（571+625+422+837+1,141）一致。

---

## 对生物学家审稿人的一句话总结

方法学创新与正文叙事的基本审慎值得肯定，但 v35 的修订未能同步到补充材料与复现指南，造成脑区核心统计方法与关键数值的多处矛盾（C1–C3），加之摘要/标题的过度表述（M1–M3）与若干生物学归因过度（M7–M9），建议**大修**：先修复跨文档一致性（这是接受前提），再逐条打磨生物学解释与措辞。
