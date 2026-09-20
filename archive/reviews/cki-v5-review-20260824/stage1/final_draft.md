# CKI version5 投稿版专家团综合审稿报告

**审稿对象**：version5/submitting_version.zip（2026-08-23 打包，含主稿件 CKI_NAR_Manuscript.docx、Cover Letter、5 张主图、图文摘要、Table 1-2、Supplementary Figures S1-S6）

**审稿方式**：四位专家独立审稿后汇总（方法学/计算生物学、统计学、生物学/单细胞基因组学、写作/NAR 期刊策略）

**审稿日期**：2026 年 8 月 24 日

**审稿模式**：纯审稿，未对任何原文件做实际改动

## 一、总体结论

四位专家一致倾向 **大修（Major Revision）**。

CKI（Cell-state Kinetic Index）概念具有原创性——以管家基因表达散度作为内源基线、将功能散度归一化的思路方向合理；跨数据集负相关发现（CKI ω 与四种标准距离度量的 Spearman r = −0.57 至 −0.38，均 P < 0.001）表明其确实捕捉到与现有度量互补的信息维度；Python 包开源（GitHub + Zenodo DOI）完备。

但统计推断链与投稿合规各存在多处实质缺陷：脑区分析的多重比较失效、per-pair 基因选择的循环依赖、校准基线的统计基础不足三项统计结构问题被三位专家独立指出；投稿包卫生与声明不符问题则可能直接导致编辑部退回。**当前状态不建议直接投出。**

## 二、Critical 问题（7 项，足以导致拒稿或编辑部退回）

### C1. 脑区分析多重比较失效（统计/方法学/生物三方共识）

31,764 次比较、36.3%（11,541 个）触及置换检验 P 值地板 9.99×10⁻⁵，无法进行 Bonferroni/BH 校正；16 个 "Strong signals" 全部触底，且候选先经阈值筛选（residual < 0.3、ω < 15）再行置换验证，属双重筛选，实际发现率不可评估。摘要将 "two with permutation support" 作为核心成果宣传，与正文自认的 "descriptive evidence" 相矛盾。建议采用更严格的 null 模型（如 block-shuffle 保持 cell-type × region 联合分布）重做，或将脑分析明确降级为假设生成（hypothesis-generating）。

### C2. per-pair k_f 基因选择的循环依赖（data snooping）

k_f 的 top-200 基因按两组均值差绝对值 |μ_A − μ_B| 选出——"功能基因"恰恰是两组间差异最大的基因，任意两群比较都会内生地放大 k_f 与 ω。作者虽在 Limitations 承认其为 "upper bound"，但主结果中绝对 ω 数值的解读全部受此动摇，且不可跨数据集比较。

### C3. 校准基线 ω = 6.67 统计基础不足且被跨方案滥用

校准仅基于 n = 6 个对照，CV ≈ 52%，bootstrap 95% CI [4.12, 9.33]（上下界相差逾 2 倍）；基线来自小鼠 global HVG-2000 方案，却被外推到人类/TCGA/脑分析的 per-pair DE-200 方案；TCGA 中 5/5 癌症类型的 k_n 全部触及地板值 10⁻⁴，ω 退化为 k_f 的缩放，却仍与单细胞数据 ω 同尺度比较。建议改用 rank-based 解释贯穿全文，并补充各数据集独立的 split-half 校准。

### C4. 管家基因"中性基线"生物学假设未论证

管家基因受肿瘤代谢重编程（Warburg 效应）、增殖/细胞周期状态、缺氧与炎症微环境等系统调控，在肿瘤中可能失调；HRT Atlas 的"低变异"是跨组织平均结果，不代表特定肿瘤或细胞状态下稳定。TCGA 分析未做任何 HK 稳定性诊断或癌症特异性敏感性检验（Figure S3 的替代集为"低变异基因"，概念上并非管家基因）。

### C5. 投稿包卫生问题（已核实）

投稿包内存在：Word 临时锁文件 `~$ble1-2.docx`（表明打包时 Table1-2.docx 仍处于打开状态）、`.DS_Store` 文件 2 个、`__MACOSX/` 元数据目录。编辑部对此类"脏包"通常直接要求清理重传，且影响职业化印象。

### C6. Supplementary Data 声明与实际文件不符

正文声明 "All analysis notebooks and processed data matrices are included in the Supplementary Data"，但投稿包内除 S1-S6 六个 PDF 外无任何代码或数据文件。须补齐 Supp Data 文件，或将该声明改为 "available at GitHub/Zenodo"，否则审稿人核对即发现不符。

### C7. Figure 2 图例与正文类别定义直接矛盾

图例定义 C/S/D/X 四类，其中 S 为 "same sub-organ"；正文却定义 S 为 "same cell type across different organs"，且 C 类别在正文从未出现。数据内部一致性问题，审稿人必抓。

## 三、Major 问题（12 项，需大修）

| 编号 | 问题 | 提出专家 |
|------|------|---------|
| M1 | Ka/Ks 类比无数学对等性（无共享速率过程，比率失去"消去中性过程"语义），ω 符号与群体遗传学 dN/dS 专有符号冲突；摘要/标题仍以其为中心叙事，存在过度宣称 | 方法学 |
| M2 | softmax(log1p) 在 1130-2000 维向量上饱和，k_n 极易触底（TCGA 即此机制）；未论证 softmax 与 L1-normalize 的方案差异及温度选择依据 | 方法学 |
| M3 | k_n 方案跨数据集不一致：Tabula Sapiens/TCGA 用 global 共享 HK 集合，脑分析用 per-pair；同类任务（cross-organ，n=59）双重标准，使 ω 不可直接比较 | 方法学 |
| M4 | 缺 ground-truth 正对照：无 spike-in 模拟、无 TOST 等价检验，全部结论依赖事后生物学回溯解释 | 方法学 |
| M5 | ω 右偏分布（skewness 0.73-2.22）却用算术均值建模乘法残差模型，未采用 log-ω 或中位数等稳健量 | 统计 |
| M6 | 效应量与置信区间缺失：主发现负相关无 CI；Table 2 中 10/17 细胞类型仅 n = 1 仍参与排序并获生物学解释 | 统计 |
| M7 | 分类器 AUC 评估不透明：未说明交叉验证、102 类转二分类方式；5,151 个 pair 非独立（同细胞类型重复出现）导致 AUC 高估；CKI 0.716 vs Spearman 0.690 差异无 DeLong/bootstrap 检验 | 统计 |
| M8 | 因果语言过度："migration candidates" 实为发育起源信号（OPC 零 Strong signals 恰说明低 ω 应解释为共享发育程序）；"transcriptional convergence" 与自认 exploratory 矛盾；应全文统一为关联性表述 | 统计/生物 |
| M9 | TCGA 肿瘤"转录收敛"结论受 bulk RNA-seq 细胞组成伪影严重混淆（纯度、基质/免疫浸润未校正），应降级为待 scRNA-seq 验证的探索性假说 | 生物 |
| M10 | 缺与领域现有方法比较（inferCNV/CopyKAT、CytoTRACE、Palantir、Shannon/Simpson 异质性指数等），无法证明增量价值 | 生物 |
| M11 | Limitations 共 21 条且编号错乱（First/Second/Third 后直接跳 Sixteenth），防御过度、拖累可读性；Methods 中置换检验程序与 P 值公式在约三处近乎逐字重复 | 写作 |
| M12 | 引用与声明问题：BH 校正误引 Storey & Tibshirani 2003（正确出处为 Benjamini & Hochberg 1995）；稿件正文缺 AI 使用声明（Cover letter 已有，OUP/NAR 要求稿件内披露）；Figure 1C 标注 "Bootstrap…mouse pilot" 与 "simulated" 自相矛盾；脑细胞类别数 9/10 前后不一 | 写作 |

## 四、Minor 问题

- 小样本分层结果进入正文（Edmondson G4 n = 11、PAM50 Normal-like n = 7、配对肿瘤-正常 n = 2-5 无 P 值），建议移入补充材料。
- TCGA 三个临床检验未做多重比较校正；LUAD mutation P = 0.017 经 BH 校正后可能不显著（约 0.051）。
- 维度不变性模拟（Dirichlet，2,000 trials）仅模拟均匀随机向量，未模拟"基因选择偏置"，而该偏置恰是 ω = 6.67 膨胀的来源，论证不完整。
- Figure 5D 横轴区域缩写标签严重重叠，难以阅读。
- Strong/Moderate/Weak 分层阈值（residual 0.3/0.5/0.75 与 ω 上限 15/25/35）缺乏推导或验证，显得武断。
- 神经元因亚型未解析被整体排除，限制脑区分析对谷氨酸/GABA 神经元区域特化的外推。
- 文件命名三套规则混用（figure1-5.pdf / Supplementary_Figure_S1-S6.pdf / Table1-2.docx），建议统一前缀。
- GitHub 仓库名 "CKI-cell-type-identification" 与论文定位 "CKI is a divergence index, not a classifier" 相悖。
- Cover letter：摘要框架 "three dimensions" 与正文 "four scales" 不一；建议审稿人 Theis（scanpy 作者）、Teichmann（ref[1] 资深作者）或被视为利益关联；"None have recent collaborations" 属无法担保的绝对化陈述。
- 术语与缩写："DE" 首用未定义；Table 1 表头 "CKI omega" 与正文 ω 拼写不一；摘要 "millions of cells" 实际分析仅 888,263 个非神经元核；摘要 "30 signatures (two with permutation support)" 应区分阈值候选与统计支持。

## 五、修订优先级建议（按投入产出排序）

### 第一优先级：零成本、必须（预计 1-2 天）

清理投稿包重新打包（删除 `~$ble1-2.docx`、`.DS_Store`、`__MACOSX/`）；修复 Supp Data 声明（C6）；修复 Figure 2 类别矛盾（C7）；更正 BH 引用；正文补 AI 使用声明；修复 Limitations 编号错乱。

### 第二优先级：低成本、高回报

全文因果语言降级为关联性表述；脑分析降级为 hypothesis-generating；摘要 "30 signatures (two with permutation support)" 改为区分阈值候选与统计支持；"migration candidates" 改为 "developmental origin / regional specialization candidates"。

### 第三优先级：需实质重新分析

rank-based 替代绝对 ω_cal 解读；各数据集独立 split-half 校准；更严格 null 模型（block-shuffle）；log-ω 建模；AUC 补交叉验证与 DeLong CI；TCGA 纯度/解卷积敏感性分析；HK 集合癌症特异性敏感性检验。

### 第四优先级：可选加强

spike-in 合成数据 ground-truth benchmark；与 CytoTRACE/inferCNV 等领域工具比较。

## 六、各专家总体评价摘录

**方法学专家**：Major Revision；若结构性缺陷（循环依赖、校准不稳定、方案不一致、P 值地板）无法在修订中解决，应考虑 Reject & Resubmit。

**统计学专家**：Major Revision；核心统计推断链存在三处实质缺陷（脑分析多重比较失效、基因选择循环性、校准外推与低分母退化），若不愿实质改动统计设计，当前证据强度不足以支撑摘要中的因果式宣传，存在拒稿风险。

**生物学专家**：大修后可能接收；在解决 HK 中性基线论证（C1）与校准可转移性（C2）及 TCGA 伪影混淆、领域方法比较之前，不适合以当前形式接收。

**写作/期刊策略专家**：科学内容扎实、写作总体流畅、图表引用完整、Data/Code availability 完善；主要问题集中于投稿包卫生、声明与实际不符、Methods/Discussion 冗长与内部编号矛盾。修复第一优先级问题后，预计 1-2 周内可达到投稿成熟度。

---

**附注**：本报告基于四位专家对 version5/submitting_version.zip 的独立审稿意见汇总，审稿过程为纯评审模式，未对任何原文件做实际改动。原稿件、图表与投稿包均保持原样。
