# 单细胞方法学评审意见 — CKI (Cell-type Ka/Ks-inspired Index) nc73 版投稿

**审稿人视角**：单细胞转录组方法学（Nature Communications 级别盲审）
**稿件**：CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases

---

## 一句话总结

CKI 用管家基因（HK）散度 k_n 作内参分母、身份基因散度 k_f 作分子，构造 ω = k_f/k_n 这一"Ka/Ks 启发式"的基线归一化细胞状态散度指数；方法思路有启发性、统计自省程度罕见地高，但核心增量（相对 k_f 的优势）主要在受控模拟与技术重复的假阳性率上成立，真实数据上多项主要结论被作者自己证明是 k_n 分母驱动或不可重复，且与 MELD/Augur/da-seq 类差异丰度方法的比较深度不足、per-pair top-200 循环基因选择带来方案特异的绝对值不可迁移问题——是一篇"诚实但被自身证据链束缚"的方法学论文。

---

## Overall score: 6.0 / 10

**NC 中稿率估计：约 20–30%**（大修后转投命中率更高；若按当前版本直接送审，大概率 Major Revision 后仍难在 NC 存活，因为审稿人共识很可能是"方法正确性充分但必要性未确立"）。

评分依据：统计学自省、可复现性工程、消融与阴性对照的完备程度属同领域前 5%；但方法学新颖性属"已有思想的重新组合"（作者自己在 Discussion 承认），且论文最有冲击力的卖点（pan-cancer reversal、脑梯度、cross-organ 排名）在正文中即被逐一降解为"分母驱动/描述性/不可迁移"，留给读者的净结论偏弱。

---

## Major Concerns

### M1. 与现有单细胞差异检测/丰度方法的基准比较不充分（严重度：高）
**位置**：Results "Perturbation-response boundaries"；Discussion "CKI complements rather than replaces existing methods"；Supplementary Note 15。

- 与 MELD、scDist 的比较仅限一个 IFN-β PBMC 数据集，且 scDist 用的是 "Python approximation"（作者自己在 Limitations (iv) 承认需用 R 原版复核）——这是方法学论文不可接受的比较设置。
- DA-seq、Milo/DA、prevalence/perturbation 差异丰度方法（sklearn-da 类、scCODA、Composer 等）完全缺席。CKI 的目标问题（"两个细胞群的功能散度是否超出基线"）与这些工具的目标问题在扰动数据上有大量重叠，仅以"不同问题"为由豁免定量基准不成立。
- 与 Augur 的比较（Supplementary Note 15）n = 10、ρ = 0.442 不显著，被一句话带过。
- housekeeping/内参归一化一脉（qPCR geNorm/Vandesompele、Eisenberg & Levanon）只在 Discussion 被引为思想来源，但 HK 面板选择对结论的影响（HRT Atlas vs Eisenberg panel vs 数据驱动）没有系统消融——作者推荐"pre-specified HRT panel"但未展示更换 panel 的敏感性。

### M2. 循环基因选择：per-pair top-200 by absolute difference 使 k_f 绝对值方案特异、tier 阈值不可迁移（严重度：高）
**位置**：Methods "CKI computation"；Supplementary Note 9；Limitations (ii)。

- k_f 的基因由被比较的两群自身的差异选出，再在差异上度量散度——这是典型的 circular selection。作者自己量化了后果（circular 选择使 k_f 中位膨胀 1.61 倍；grand mean ω 38.55 vs leave-pair-out 26.5 vs fixed 6.5），坦率可嘉，但这意味着论文所有绝对 ω 值、ω < 15/25/35 的 tier 阈值、以及 "mean ω = 7.70" 的校准基线本身都是方案产物。一个"指数"如果其绝对值在换一种合理基因选择方案后变化 6 倍，其作为方法的核心可用性存疑——用户拿到 ω = 20 无法知道意味着什么。
- 虽然排名结论稳健（ρ ≈ 0.92–0.94），但论文的实践指南（Discussion 推荐 (iii)）实质上退化为"只能做同数据集内、同方案的相对比较"——这把 CKI 从一个"指数"降级为一个"数据集内工作流"，削弱了方法学论文的核心主张。

### M3. 真实数据上 ω 相对 k_f 的增量未确立，核心结果多为分母驱动（严重度：高）
**位置**：Results（TCGA、脑图谱、cross-organ 各节）；Discussion 第 2–3 段。

- 作者自己反复证明：脑梯度 k_n 主导（ρ = −0.73 vs k_n，0.09 vs k_f）；cross-organ 排名与 k_f-only 排名仅弱一致（r = 0.23）；IFN-β 中 CD14+ 单核细胞 ω AUC 崩到 0.55 而 k_f 保持 0.98。Discussion 明言 "on real-data orderings the increment is not established, and k_f with a design-matched null remains the default for ordering claims"。
- 那么读者必然问：**如果 ordering claims 应默认用 k_f + design-matched null，CKI（ω）这篇方法学论文的必要性主张到底剩什么？** 作者的回答（calibration/drift rejection）目前只在模拟和 FPR 实验中成立。审稿人认为论文需要正面处理这一"自我拆台"结构：要么找到至少一个真实数据场景中 ω 严格优于 k_f 的可靠结果，要么把论文重新定位为"带内参基线的差异检验框架"而非"新指数"。

### M4. TCGA 部分作为"验证"证据力薄弱，且 HK 锚在癌症中明确失效——与方法的中心假设冲突（严重度：高）
**位置**：Results "A pan-cancer map"；Supplementary Note 10；Introduction "The scope of ω is bounded"。

- 方法核心假设是 HK 表达受约束、可作中性基线；而论文自己在 TCGA 中发现肿瘤 HK 基线升高 1.3–3.3 倍、IFN-β 刺激使 k_n 升 1.2–5.7 倍、模拟中 500 基因漂移使 ω 崩溃（AUC 0.05–0.13）。也就是说，恰恰在生物学最有趣的场景（疾病、强扰动）中 HK 锚最不可靠。
- TCGA 为 bulk 数据，TCGA "normal" 为癌旁组织；pan-cancer reversal 被作者自己归因于 k_n 升高并声明 "do not indicate smaller functional divergence of tumor cells"。那么这一章对"CKI 检测功能散度"的验证价值为零——它更多展示了 CKI 的失效模式。作为占正文约 1/4 篇幅的应用章节，其定位需要重写或大幅压缩。
- TCGA per-cancer 置换检验固定 identity panel，作者承认 anti-conservative；LIHC 结果对 normalization mapping 敏感（1.11 vs 1.29）；GTEx 外部参照 "descriptive only"。单个保留结论（LUAD KRAS 对比经纯度/吸烟调整后存活）有价值但属于 bulk 分析，与单细胞方法学主张距离较远。

### M5. 组合性（compositionality）问题处理不足（严重度：中高）
**位置**：Methods（pseudobulk 构造）；Supplementary Note 10。

- pseudobulk 上的 JS 散度天然受细胞群组成影响；论文用 marker-panel 组成检查（pooled k_n 系数变化 −0.9%，但 LIHC +44%、KIRC +20%）来 bounding，但未与 CLR/ALR 类组成感知方法（如 scCODA、propeller、或简单的 log-ratio 变换）做对照，也未讨论 pseudobulk 内 HK 基因表达被细胞亚群混合稀释的机制。对一篇以"分解基线 vs 功能变异"为卖点的论文，组合性是理论上必须正面处理的一环，而不是一个 robustness check。

### M6. per-pair 筛选的统计功效设计有硬伤：m = 31,764 检验下 B = 1,000 置换根本达不到 FDR 分辨率（严重度：中）
**位置**：Methods "Statistics and reproducibility"；Fig. 5c；Supplementary Note 12–14。

- 作者诚实指出 q < 0.05 需 B ≈ 6×10⁵ 置换、Strong 候选实为 anti-enriched（39 vs 期望 148.3）、无任何候选过 FDR。那么"39 Strong candidates"的整个 catalogue 章节其实是阴性结果，把它包装成 "hypothesis-generating screen" 占据正文一节+多张图（Fig. 5c, d；Supp Fig. 8；Supp Tables 12, 13）不成比例。要么提高 B（或改用解析/半解析 null），要么把该节降级为一段阴性陈述。
- 注意到 raw P < 0.05 有 1,960/31,764（期望 ~1,588），超额仅 ~23%，且对 estimator 敏感（3/39 在 global-k_n 下存活）——进一步支持"无信号"读法。

---

## Minor Concerns

1. **k_n 跨细胞类型不可比却做跨类型排名展示**（Fig. 4/Table 1、Fig. 5b）：作者在表注与 Discussion 反复声明 cross-type gaps "descriptive only"，但图/表形式上仍是排名——形式与声明不匹配，易被二次引用误读。建议改为同类型内的展示或加显著警示。
2. **负相关结果（ω 与四种标准指标 Spearman −0.36~−0.46）的呈现**：作者已解释为分母效应（partial r 转正），但这在摘要层面仍可能被读者误读为"CKI 发现了标准指标看不到的东西"。摘要措辞需更明确。
3. **校准因子 7.70 的传播**：一个由 6 个小鼠群体 split-half 得到的常数（CI [6.38, 9.82]，跨数据集 7.67–9.73）被用于全篇的 ω_cal；虽然附录 3 处理了不确定性传播，"one-significant-digit resolution" 的做法（ω_cal = ω/7.70）过于粗糙，建议直接报告 ω 及其数据集内 split-half 基线。
4. **IFN-β 数据 condition 与 lane 完全混淆**：作者披露了（Supp Note 8）并正确地只做跨指标对比，但该数据集同时是 MELD/scDist 比较与 perturbation 边界分析的载体——混淆设计使这两处的结论强度都受限，应考虑补充一个非混淆的扰动数据集（如 scIPPS/Reyfman 或扰动筛 CRISPR 数据）。
5. **运算窗口窄**（~50–200 cells/group，>500 后 permutation power 消失；FPR 随 group size 增长到 48%）：对现代图谱（普遍 >1,000 cells/群）这是很大的实用限制，正文应更靠前地声明。
6. **聚合顺序不一致**（brain: softmax(log1p(mean))；mouse/human: softmax(mean(log1p))）：两种 pipeline 产生不可互相迁移的校准常数——这属于实现债，建议统一后再比较。
7. **Python 3.14.4**（Methods 环境部分）：极新版本，配合 scanpy 1.12.1 的组合建议补充 conda/docker 锁文件的实际验证记录（Reproducibility Guide 声称有，建议在正文 Methods 注明锁文件路径）。
8. **图 3a 双轴呈现**（NN/TT ω 与 TT/NN k_n 各一轴）易造成视觉夸大，建议改为同一 log-ratio 轴的成对条形。
9. **写作**：正文密度极高、限定语极多（"tentatively" "suggestive only" "descriptive"），虽然诚实，但 NC 读者很难提炼 take-home message；建议每节末加 1–2 句 plain-language 总结。
10. **Ka/Ks 类比**：作者处理得当（明确 heuristic），但标题与摘要仍以 Ka/Ks 为第一卖点，而正文实际证明该类比的"中性基线"前提在转录组不成立——建议标题弱化类比。

---

## 强项

1. **统计自省罕见地高**：anti-conservative 区间的自我修正（two-stage bootstrap 取代 i.i.d. 区间）、置换分辨率 vs FDR 的显式算术、anti-enrichment 阴性结果的如实报告，均超出该领域常规水平。
2. **可复现性工程出色**：GitHub tag v0.5.6 + Zenodo DOI + Dockerfile + Reproducibility Guide（spot-check 值）+ 分析脚本索引（Supplementary Data 1），接近最佳实践。
3. **阴性对照与消融设计完备**：pseudo-region negative control、leave-pair-out panel、span/size-matched controls、barcode audit 剔除 32 个 cell-line 样本、GTEx 外部参照，显示团队对混杂因素的系统性排查。
4. **理论框架（Supp Note 20）**：给出因子模型下的引理/命题链（JS 二阶展开、比率 studentize 使脑 CV 从 1.21 降到 0.148 的"t-statistic 逻辑"论证），为方法提供了超出类比的形式化支撑。
5. **诚实披露失效边界**：HK 锚失效（500 基因漂移 AUC 崩溃）、CD14+ ω 崩溃、cross-species 不成立（r = −0.17）等负面结果全部保留，科学品性好。

---

## 对作者的必答问题

1. **ω 的必要性**：既然你们自己证明 "on real-data orderings the increment [over k_f] is not established, and k_f with a design-matched null remains the default"，请给出至少一个真实（非模拟）数据场景，其中 ω 给出 k_f+design-matched-null 无法给出的可靠结论；若不能，为什么这不应改变论文的定位（从"新指数"到"带 HK 内参的差异检验流程"）？
2. **与 DA 方法的关系**：Milo/DA、scCODA、DA-seq、propeller 等差异丰度方法与 CKI 在扰动分析目标上重叠，为何完全不做定量基准？scDist 的 "Python approximation" 差距有多大，是否可用 R 原版复核？
3. **HK 面板稳健性**：核心结果（AUC、FPR 校准、脑梯度、LUAD KRAS 对比）对 HK 面板选择（HRT Atlas vs Eisenberg & Levanon vs 完全独立的 panel）的敏感性如何？k_n 是否等价于"任何低变异基因集的散度"？若是，HK 的生物学含义（而非仅仅是低方差）在方法中起什么作用？
4. **循环选择**：per-pair top-200 循环选择造成绝对 ω 6 倍量级的方案依赖。是否可以默认发布 leave-pair-out 或 fixed panel 版本作为主结果（circular 版仅作功效上界）？这会改变多少主文结论？
5. **组合性**：pseudobulk JS 散度如何处理细胞亚群组成变化？marker-panel 检查显示 LIHC 组成贡献 +44% 的 k_n 系数变化——在单细胞场景中，两个"同类型"群如果亚群组成不同，ω 度量的是状态差异还是组成差异？
6. **per-pair 筛选的功效设计**：在 B = 1,000 明知无法支撑 m = 31,764 的 FDR 时，为何不设计 B ≈ 10⁵–10⁶ 的近似解析 null 或抽样策略？39 个 Strong 候选 anti-enriched 的 catalogue 是否应整体撤下或压缩为阴性结果陈述？

---

*审稿人声明：本评审基于 nc73 版投稿包（正文、SI、补充表清单）独立完成；未验证 GitHub/Zenodo 代码的实际可运行性，可复现性评价基于声明材料。*
