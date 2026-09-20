# Nucleic Acids Research — 模拟审稿报告（Reviewer 4，编辑视角）

**稿件标题**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**稿件类型**: Original Research（计算方法类）
**投稿包版本**: v37（2026-08-28）
**审稿人身份**: NAR 编辑视角审稿人（scope 匹配度 / novelty / 读者价值 / 发表就绪度）
**审稿日期**: 2026-08-28

---

## 一、稿件贡献与主张总结

CKI（Cell-state Kinetic Index）提出一个受 Ka/Ks 启发的启发式指数：将两组细胞群体的 pseudobulk 表达谱分解为以 housekeeping（HK）基因计算的基线分歧率 k_n 与以 identity 基因（top-200 per-pair DE 基因，或 top-2,000 HVG）计算的功能分歧率 k_f，以 ω = k_f/k_n 量化"基线归一化的转录组重塑"。作者在四个数据集上验证：Tabula Muris 小鼠 atlas 的 split-half 校准（等效群体基线 ω = 6.67，95% CI [4.24, 9.24]）；Tabula Sapiens 人 atlas 上 4,851 对 cell-type 的方法比较与 cross-organ 保守性排序；TCGA 五种癌症的 bulk 探索性分析（NN/TT > 1 的"转录趋同"信号）；以及 Siletti 人脑 snRNA-seq atlas（888,263 非 neuron 核，31,764 对 cross-region 比较）中 10 个非 neuron 细胞类的 6.88 倍区域分化梯度与少突胶质细胞系富集的 55 个"异常相似"Strong 候选。

v37 版本的一个显著特征是统计诚实性上的大幅自我修正：作者明确报告了对自己不利的结果——脑数据集内部 split-half 基线（12.29）约为小鼠因子 1.8 倍、校准不可跨数据集迁移；CKI 与标准度量的负相关部分是 k_n 分母导致的比值伪相关（偏相关转正）；脑梯度主要由 k_n 效应驱动（k_f 仅 1.2 倍差异，k_n 达 5.7 倍）；block-shuffle null 下 31,764 对中没有任何候选通过 BH FDR 校正（minimum q = 0.949），并披露早先 per-pair shuffle 实现的反保守错误（36.3% pairs 落在 P 值下限）。软件包（v0.3.1，MIT）经 GitHub + Zenodo（DOI: 10.5281/zenodo.15670808）公开，附完整复现指南、随机种子、逐脚本输出索引与 Dockerfile。

然而，从编辑视角看，这篇稿件的核心困境在于：**论文自己的稳健性分析系统性地削弱了其核心主张**。方法比较中 CKI 的分类 AUC 排名 5/5（0.680，最低）；"负相关揭示独立信息维度"的主张被自己的分解分析否定；脑梯度的"功能分化"解读被自己的 k_f/k_n 分解否定（梯度实为 HK 基因稳定性差异）；校准因子被证明数据集依赖；TCGA 结论因 bulk 分辨率与 k_n floor 饱和而仅具探索性；唯一的"发现"层结果（55 个 Strong 候选）为纯阴性 FDR 结果。剩余的实质性贡献是一个概念简单（两个 JS 散度之比）的启发式指数、一个可复现的软件包、以及大量 caveats——这对 NAR 读者群的净价值需要认真权衡。

---

## 二、逐条问题清单

### Critical

**C1. 缺少任何 ground-truth / 模拟验证——方法论文的根本性缺失。**
作者自己承认（Limitations 第十四条，由 Reproducibility Guide 5.5.i 证实："Added as Limitation #14 (no synthetic data validation with known ground-truth signals)"）。一篇提出新度量并主张其能"quantify functional divergence"的方法论文，必须证明：在已知真实功能分歧大小的合成数据中，ω 比 k_f、k_n 或标准度量更接近真值。现有全部"验证"都是观测性、事后解释性的（与已知细胞生物学一致性论证，作者自己也承认是 "post hoc biological plausibility"）。尤其关键的是：由于 k_f 的 per-pair DE 选择是循环的（作者承认 "the circular dependency inherent in the per-pair k_f scheme"），ω 的分子本质上是被测差异本身的上界，没有 ground truth 就无法界定该指数的测量效度。
**要求**：构建带已知功能分歧信号（可控幅度、可控 HK 基因漂移、含 batch/donor 结构）的模拟框架，系统评估 ω、k_f、k_n、raw JS 的真值恢复能力（含 type-I error 与 power），并与至少 1-2 个现有方法定量比较。这是重投的必要条件。

**C2. 论文未能证明 ω（比值）相对其自身分量 k_f、k_n 的增量价值——核心 value proposition 未成立。**
证据链：(i) AUC 0.680，5 个方法中最低（Table 1；正文："CKI showed moderate cell-type classification performance (AUC = 0.680, ranked 5th of 5 methods)"）；(ii) 负相关部分是分母伪相关（"consistent with a partial denominator effect, the Spearman correlation between ω and each standard metric conditional on k_n became positive in all four cases (partial r = +0.11 to +0.54)"）；(iii) 脑 6.88 倍梯度主要是 k_n 效应（"k_f differs only 1.2-fold between the two classes (0.033 vs. 0.027), whereas mean k_n differs 5.7-fold"）——即标题性发现"astrocytes 区域分化最强"实际反映的是 astrocytes 的 HK 基因跨区域更稳定，这与 Ka/Ks 叙事（功能基因分化超出中性基线）方向相反；(iv) 作者自己建议 "comparing k_f and k_n components directly when mechanistic attribution matters"。既然如此，读者为什么要用 ω 而不是直接看分量？
**要求**：给出至少一个具体分析场景，其中 ω（或 ω 排序）纠正了 k_f-only 或 raw JS 的错误结论，并定量展示。若做不到，应重写主张，把论文重定位为"k_f/k_n 分解框架"而非"ω 指数"，并把 k_n 驱动梯度作为主要结果明确呈现于摘要。

**C3. 主稿 Methods、Reproducibility Guide 与补充材料在 k_n floor 上存在直接矛盾——复现层面的 blocker。**
主稿 Methods（CKI computation）明确写道："the package default (kn_floor = 0) applies only a positivity guard, which is the behavior used by all single-cell analyses reported in this paper... The TCGA bulk RNA-seq analysis is the sole exception and applies kn_floor = 1 × 10⁻⁴"。但：(a) Reproducibility Guide 参数表写 "k_n floor (minimum) | 1e-4 | all analyses"；(b) Supplementary Note 2 Algorithm 1 伪代码第 7 行无条件执行 "if k_n < 1e-4: k_n <- 1e-4 // floor to prevent inflated omega"；(c) Supplementary Note 1.1 同样说 "a small floor value (1e-4) is applied to k_n"。三份文件给出两套互斥的默认行为，而 kn_floor 取值直接影响 ω 的绝对数值（尤其脑数据集最小 per-pair k_n 仅 7.7 × 10⁻⁵，低于 1e-4 floor——若 floor 真被应用，脑数据集的全部低 ω 值都会被截断改写）。
**要求**：核查实际代码行为，统一三处描述；若 1e-4 floor 确实被应用于全部脑数据（代码与主稿矛盾），则脑数据集所有 ω 值、梯度、residual 模型结果均需重算重报。另需提供包的自动化测试（pytest）覆盖该默认值。

### Major

**M1. Cover letter 与 v37 主稿的自我修正脱节，保留了已被主稿撤回的过度主张。**
Cover letter 第 2 段第一点仍宣称："demonstrating that ω measures something fundamentally different from raw JS divergence, cosine similarity, and other existing approaches"，并称 CKI 为 "a robust, interpretable measure"。但主稿 v37 已将 Figure 3 重新定名为 "Correlation structure"、明确写入 "should not be interpreted as evidence that ω measures a fully independent information dimension"，且 MANIFEST 自述 "C-A residual overclaim cleanup... reframed to composite-signal language"。Cover letter 的 "fundamentally different" 与 "robust" 直接违反主稿自己的结论。
**要求**：重写 cover letter 使其与 v37 的 composite-signal 框架一致；删除 "independent information dimension" 表述。

**M2. Figure 2 图注仍保留旧版过度主张，与 Figure 3 图注的修订不一致。**
Figure 2 legend（Fig. 2C）："All show negative correlation, confirming ω captures complementary information." 其中 "confirming... complementary information" 正是 v37 在 Figure 3 与 Discussion 中撤回的说法（负相关部分是比值伪相关）。同一份稿件内两个图注对同一现象给出矛盾的因果解读。
**要求**：修改 Figure 2C 图注为描述性表述（"negative correlation; see Fig. 3 decomposition for interpretation"）。

**M3. 摘要遗漏了最重要的校准结论：基线不可跨数据集迁移。**
摘要仅写 "Calibration established an empirical baseline for equivalent populations (mean ω = 6.67, 95% CI [4.24, 9.24]), inflated by identity-gene selection"，未提及 brain-internal baseline 12.29（约 1.8 倍）导致 ω_cal 在脑数据集被系统性高估、Bergmann glia 的 ω_cal ≈ 0.9 位于（而非高于）内部基线。这是 v37 新增的核心 honesty 修正（MANIFEST 第一条），但摘要读者无法获知。摘要同时称 CKI "provides a framework" 却未提示 ω 绝对值不可跨数据集比较（正文："Users should compare ω ranks rather than absolute values across datasets"）。
**要求**：在摘要中加入一句数据集相对性限制；考虑删除或限定 ω_cal 在正文中的展示（当前以小鼠因子标定的 ω_cal 在脑数据集已被证明失真）。

**M4. TCGA headline 结果建立在 k_n floor 饱和的 ω 值上，且未分层报告。**
正文承认 "the TCGA analysis applies kn_floor = 1 × 10⁻⁴... so ω saturates at k_f/10⁻⁴ in 3 of 5 cancer types"。这意味着五种癌症中有三种的全部 ω 值实际上是 k_f 的单调重标度（k_n 信息完全丢失），而 headline 结论 "In all five cancer types, the median NN/TT ω ratio exceeded 1.0" 把饱和与未饱和癌症混在一起报告。NN/TT > 1 在三种饱和癌症里等价于 k_f 的 NN/TT > 1——即标准的全基因 JS 类比较，CKI 的"基线归一化"卖点在这些癌症中不存在。
**要求**：分癌症明确标注哪些结果受 floor 饱和影响；仅用未饱和癌症（或提高 floor 分辨率的 k_n 估计）重新支持 NN/TT 结论；否则将该结论降格为 "in 2 of 5 unsaturated cancer types"。

**M5. 相关工作覆盖不足：中性表达演化文献缺失，novelty 定位不完整。**
"以中性/约束基因集为内部参照衡量表达分歧"并非本文首创：比较转录组学中关于基因表达的中性演化框架（如 Khaitovich 等的 expression divergence neutrality 工作，以及建议审稿人 Itai Yanai 本人在表达分歧方面的系列研究）与 qPCR/RT-PCR 中以 HK 基因为参照归一化的惯例，均与 CKI 的核心思想同构。稿件引用了 Ka/Ks（Nei & Gojobori; PAML）但完全未引用表达演化领域的先行工作，使 novelty 主张（Introduction: "CKI introduces a conceptual shift"）显得比实际更强。
**要求**：补充并讨论表达分歧中性模型相关文献；明确说明 CKI 相对它们的增量（JS 分解 + 单细胞 pseudobulk 应用 + permutation null）。

**M6. 未与任何专门方法做定量基准比较（作者自认）。**
Discussion："we did not quantitatively benchmark CKI against these specialized methods"（SAMap、SATURN、CACIMAR）。对 NAR 的方法论文而言，至少应在 CKI 声称占优的任务上（如 cross-organ conservation 排序）与一个替代方法（如直接用 k_f 或 marker Jaccard 的排序）做正面对比，包括与 C1 要求的模拟验证结合。仅靠 "they address different questions" 的辩解不足以支撑 "general tool" 的定位。

**M7. 稿件长度与结构严重超标，Discussion/Limitations 沦为修订日志。**
Limitations 编号至 "Twenty-first"，其中大量条目（如第十、十二、十六、十七、十九条）实际上是 v36 审稿回复内容的逐条内嵌，讨论部分出现 "An earlier implementation of this test... produced anti-conservative P-values (36.3% of pairs at the P-value floor)" 这类属于回复信/复现指南的内容。以 NAR 计算方法论文的惯例衡量，主稿应大幅压缩：将 robustness 细节移入补充材料，Limitations 归并为一节结构化讨论（~8 条以内），主稿聚焦方法定义、基准验证与核心结果。当前形态会显著降低可读性。

**M8. 环境与数值的文档不一致（复现可信度问题）。**
(a) 主稿 Methods 写 "scanpy 1.12.1"，Reproducibility Guide 1.1 写 "scanpy: 1.10.4"；(b) 主稿 Results（line 54）写 brain-internal 校准下 "global mean corresponds to ω_cal ≈ 2.7, astrocytes to ω_cal ≈ 6.3"，Supplementary Note 3.5 写 "≈ 2.6... ≈ 6.2"；(c) Reproducibility Guide 复现清单写 "mouse pilot (main analysis)" 使用 hybrid 模式，而 Supplementary Note 2 又将 hybrid 模式归于 "Tabula Sapiens Extension" 并称 Fig. 2 使用 global HVG——但主稿的 Figure 2 实际是 pilot calibration（hybrid），global HVG 矩阵在 Supplementary Fig. S1，两处指称混乱。这些不一致虽小，但叠加 C3 会让审稿人对"numerically identical results"的承诺失去信心。
**要求**：全文数值与环境做一次交叉审计；明确每张图对应的确切 scheme 并在图注中标注。

### Minor

**m1.** Table 2 与正文排序逻辑不一致：正文将 Endothelial cells 与 Erythrocytes（均 n = 3）描述为 "At the divergent end... had the highest cross-organ ω"（即当作排序顶端解读），而表格将二者置于 "n < 5 pairs: interpret with caution" 分隔线之下、排在所有 n = 1 类型之后。虽然正文加了 "suggestive only" 限定，但"最高分歧端"由 n = 3 的类型占据这一事实应更醒目地反映在图 5 的呈现中。

**m2.** "migration inference" 措辞残留：Figure 6 标题 "Brain regional cell-type differentiation and migration inference" 与图注 "Migration candidate detection"，而正文反复声明候选不构成 inference（"we present the brain candidates as hypothesis-generating signals... rather than confirmed discoveries"）。建议将 "migration inference" 改为 "candidate screen"。

**m3.** Supplementary Note 3.2 写 "In all CKI results, standardized effect sizes are typically > 1.0 for biologically meaningful comparisons"——这是一个未定义 "biologically meaningful" 的经验性断言，且与 SES 仅作描述性统计的定位（主稿多处强调）不一致。

**m4.** HK 基因集敏感性分析 "yields omega correlations of r > 0.95"（Limitation 第二条、Supplementary Note 1.2）未说明该相关性是在哪个数据集、哪种 scheme（global HVG 还是 per-pair DE）下计算——两种 scheme 下 HK 集合的影响机制不同（后者只影响 k_n）。

**m5.** Abstract 写 "888,263 non-neuronal nuclei profiled; 886,808 analyzed after filtering"——精确到个位数的数字放在摘要里信息价值低，建议简化为 ~0.89M。

**m6.** 参考文献 (44) Bakken et al. 用于支撑 "Preliminary cross-species validation"，但该验证只有 Supplementary Fig. S2 一句带过（"limited by the small number of directly comparable cell-type pairs"）。要么扩充为可评估的定量结果（给出 n 与具体 ρ 值），要么从 Discussion 中删除。

**m7.** Data availability 写 "accessed July 2025"，MANIFEST 写 built 2026-08-28——时间线自洽但建议统一为具体版本号/快照日期，尤其 CELLxGENE 集合会更新。

**m8.** 建议的审稿人列表（cover letter）质量合理且无利益冲突声明，予以肯定。

---

## 三、编辑视角专项评估

**Scope 匹配度**：可接受但不无勉强。NAR 发表计算方法与资源类论文（含单细胞分析方法），CKI 是面向基因组数据的开源 Python 方法包，主题在 scope 内。但 NAR 方法论文通常期待显著的方法学 advance 或对读者群有明确工具价值；CKI 的概念核心（两个基因子集上 JS 散度之比）技术门槛低，且如 C2 所述工具价值尚未确立。若修订后仍无法证明 ω 的增量价值，本文更适合 Bioinformatics（应用笔记/方法）、Genome Biology 或 PLOS Computational Biology。

**Novelty 与增量贡献**：中等偏弱。Ka/Ks 类比本身作者已承认是启发式且数学上不等价（"lacking a comparable mechanistic cancellation"）；表达分歧相对中性参照的思想在表达演化文献中有先例（M5）；单细胞 pseudobulk 层面的实现与 block-shuffle null 设计是本文最扎实的增量，但不足以单独支撑 NAR 方法论文。v37 新增的 within-donor 梯度、split-half 内部校准、estimator 敏感性分析质量较高，说明团队有执行深度。

**摘要/图表/叙事清晰度**：摘要总体诚实（罕见地主动报告了负相关的伪相关来源与 FDR 阴性结果），但遗漏校准不可迁移这一关键点（M3）。图 1-6 的图注质量参差：Figure 3 的 v37 修订到位，Figure 2 图注滞后（M2）。叙事的最大问题是把"我们没有发现什么"（FDR 阴性）与"我们发现了一个梯度"（但梯度由 k_n 驱动）编织成正向故事线，而论文自己的分解分析已经拆掉了这个故事的地基——叙事需要围绕"k_f/k_n 分解"而非"ω 指数"重构。

**阴性结果的呈现诚实性**：**出色**，这是本稿最突出的优点。minimum q = 0.949、36.3% 反保守错误、AUC 垫底、校准不迁移、TCGA 探索性定位、循环选择问题全部主动披露，且 v37 的修订（MANIFEST 各条）真实落实到主稿。编辑应明确肯定这一点——本审稿的扣分不在诚实性，而在证据强度。

**软件包与数据可得性（NAR 强制要求）**：基本合规。GitHub（MIT）+ Zenodo 永久存档 + Dockerfile + 固定种子 + 复现指南 + 逐输出文件索引，超过多数投稿的标准。但 C3（kn_floor 矛盾）说明文档与代码的一致性未经审计；要求补充 CI 自动测试与一键端到端复现脚本（至少覆盖 Fig. 2 与 Table 1 的关键数值）后，此项可评为合规且优秀。

**稿件长度与格式**：不合规风险高。主稿正文（含 21 条 Limitations、海量 Methods 细节）明显超出 NAR 计算方法论文的常规体量，需按 M7 大幅精简并将稳健性细节移入补充材料。graphical abstract 已备，AI 使用声明已备，其余格式项（ORCID、 Funding、COI、author contributions）齐全。

---

## 四、总分与推荐决定

| 维度 | 评价 |
|---|---|
| 方法学新颖性 | 中偏弱（概念简单，先例文献未覆盖） |
| 证据强度 | 弱（无 ground-truth 验证；headline 结果为阴性或被自身分解削弱） |
| 统计诚实性 | 优秀 |
| 复现与开源 | 良好（但存在 kn_floor 文档矛盾 blocker） |
| 写作与叙事 | 中（长度失控，叙事与自身证据脱节） |
| 对 NAR 读者价值 | 待定（取决于 C2 能否补足） |

**总分：4 / 10**

**推荐决定：Major Revision（大修）**

理由：稿件在诚实性与复现工程上有真实优点，且 v37 对 v36 评审的响应质量高，说明团队有能力完成大修；但 C1（ground-truth 验证）、C2（ω 的增量价值）、C3（复现 blocker）均为必须解决的根本问题，任一不能解决即应拒稿。大修后重新送审时，建议至少一名具有统计模拟/度量理论背景的审稿人评估 C1-C2 的回应质量。

**转投建议（供作者参考）**：若大修后发现 ω 指数的增量价值确实无法确立，建议将稿件重构为 "k_f/k_n decomposition framework + 软件工具" 投稿 Bioinformatics（Applications Note 或 Original Paper）或 Genome Biology；不建议投数据库类或纯生物学期刊。

---

*本报告基于 v37 投稿包全部六份文件的完整阅读（主稿、补充材料、复现指南、cover letter、表格、MANIFEST），所有引用均可在对应文件中定位。*
