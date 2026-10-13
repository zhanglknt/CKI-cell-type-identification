# CKI nc73 投稿包审稿意见（reviewer-brain：神经科学/脑单细胞图谱方向盲审）

## 一句话总结

CKI 在 Siletti 全脑图谱上的脑应用部分总体呈现了与其方法定位相符的谨慎、设计匹配的统计框架——神经元超类梯度（MGE 抑制性神经元显著高于 block-shuffle null、丘脑不显著）与既有神经生物学（皮层抑制性/兴奋性神经元区域特化强于丘脑核团、星形胶质细胞高度区域特化）方向一致——但核心结果 k_n 主导、供体仅 4 人、"受选择/functional divergence" 的演化语汇在神经语境下存在被过度解读的结构性风险，需在正文中进一步收紧措辞与因果主张。

## 总体评分：7 / 10

## NC 中稿率估计：~40–50%（大修后可能中；脑应用部分不是主要短板，方法学新颖性与定位才是决定因素）

---

## Major Concerns

**M1. 神经元超类 k_f 梯度（MGE > Upper-layer IT > Thalamic）的生物学解释不够深入，且与 k_n 主导的自陈相矛盾。**
正文与 Note 18 报告 MGE P=0.001（置换下限）、Upper-layer IT P=0.014、Thalamic P=0.163，并在 Fig. 5e/f 中呈现为"regional divergence far exceeds the non-neuronal median"。但：
- 手稿自己承认非神经元梯度"k_n-dominated"（astrocyte ω tracks k_n ρ=−0.73 而非 k_f ρ=0.09）。神经元超类分析没有给出对应的 k_f / k_n 分解——MGE 的 SES=7.2 到底是分子（功能基因分歧）驱动还是分母（housekeeping 基线）驱动？这是审稿人必然追问的问题，Note 18 当前未回答。若同样是 k_n 主导，则"MGE 抑制性神经元区域功能分歧更强"的生物学叙事不能成立，只能退为"转录组分歧更强"。
- 若确为 k_f 主导，其生物学合理性其实是有文献支持的：MGE 来源的 PV/SST 中间神经元具有皮层区域内与层间的高度多样性（Tremblay/Lee/Kepecs 等中间神经元异质性工作）；upper-layer IT 神经元跨皮层区域的投射靶向与基因表达梯度（Yeo/Bakken M1-cortex 保守性分析、Siletti 原文本身）；丘脑核团虽功能各异但转录组在 superclass 层面可能确实更均一。但手稿引用链没有覆盖中间神经元异质性文献（引用 20–24 集中于 microglia/OPC），生物学解释一栏基本空缺。
- 三个超类的供体/核数不平衡（MGE 222k、IT 455k、Thalamic 85k），而手稿已证明 k_n 与 class size 负相关（ρ=−0.648）且 equal-n 控制下梯度从 6.10 崩到 1.74。丘脑 P=0.163 会不会只是 power/size 不足而非真实无信号？建议给出各超类的 null SD 与 size-matched 敏感性。

**M2. Block-shuffle 置换检验是否真正控制了空间与谱系自相关，论证不完整。**
- 设计本身（library→region 置换、保持每 region library-count multiset）控制了 library 层技术结构，pseudo-region 阴性对照（Note 12，尾部率 5.79%/6.87%）也校准良好——这是强项。但 MGE/IT 神经元的区域采样在 Siletti 中高度集中于新皮层，丘脑仅来自丘脑核团；置换保持的是全局 library-count 结构而非"解剖子区内的空间平衡"，相邻解剖区共有的供体-批次-切片结构（四供体、94.5% 区域对共享至少一名供体）在 free shuffle 下仍可跨供体交换。手稿对非神经元做了 donor-stratified null（3/10 存活），但 Note 18 的神经元超类分析未报告 donor-stratified 版本——MGE P=0.001 是否在供体分层下存活必须补上，否则该头条数字的可信度存疑。
- 谱系自相关：MGE 祖细胞的克隆扩张/区域定植模式（手稿引 Barry-Carroll 2023）意味着 library 间相关不只来自 region，也来自克隆结构；block-shuffle 无法建模这一点。至少应在 Limitations 明示。

**M3. SEA-AD 阴性结果的对照价值有限，且表述与统计强度不匹配。**
Note 19 中 pan-reactive/A1/A2 与 DAM 锚定基因集在 High-ADNC 供体中"directionally elevate ω"（P=0.015/0.041），但 minimum q=0.145、homeostatic-microglia 阴性对照位于 null——手稿称其为"positive control"，实际它是一个方向正确但未过 FDR 的弱阳性。作为"CKI 能捕获疾病相关转录程序"的证据太弱；作为阴性对照叙事（pan-reactive/DAM 不在区域梯度中富集）倒是有价值。建议：(i) 明确降格为"sub-threshold directional anchor"并移入补充，或 (ii) 用 SEA-AD 的疾病分期（early/intermediate/late ADNC）做剂量-反应检验，那才是有判别力的设计。42 vs 对照供体、单一脑区（MTG）的 donor-level 设计 power 本就有限，正文 Discussion 引用它时不应写成"behave directionally"就带过。

**M4. 四供体结构对全脑区域梯度的支撑度。**
所有脑区域结论建立在 4 名供体上（median top-donor share 0.61）。donor-level bootstrap 已做（梯度 3.28 [1.92, 3.78]），这是诚实的；但 MGE 置换下限 P=0.001 的 SES=7.2 在四供体下的外部效度无法评估——审稿人无法排除单个供体的区域特异性伪影（post-mortem、PMI、用药史）。建议：leave-one-donor-out 对三个超类的 P 值做敏感性（手稿对梯度做过 ">1"，但超类未做）。

**M5. "受选择"叙事在神经语境下的过度演化解读风险。**
手稿在 Discussion 已明确"never as evidence of positive selection"，处理得比预期好。但题目内嵌 Ka/Ks 类比、Fig. 1a 视觉上直接并列 ω>1=positive selection，而脑部分给出的是 k_n 主导的梯度——"astrocytes are the most regionally divergent"这类句子在神经科学读者眼中会被读成"星形胶质细胞受最强选择"。建议：(i) Fig. 1a 中 Ka/Ks 一侧的 "positive selection" 标签加删除线或淡化，(ii) 脑结果部分每处 ω 排序旁边同步给出 k_f-only 排序（已有数据，committed OPCs 排名反转即是例子），防止读者把复合量当功能量读。

---

## Minor Concerns

1. Neuronal superclass 分析用 5,000 highest-mean non-HK 基因预筛池 + per-pair top-200，与非神经元 pipeline 的 per-file HRT 匹配（1,115 基因）一致，可复述；但 Supplementary Fig. 7b 的 subcluster 层（48,450 对）只在图例出现，正文未讨论——若 subcluster 层削弱 superclass 结论应披露。
2. "non-neuronal screen understates atlas-wide divergence"的因果措辞过强：神经元 median 高也可能反映 superclass 内混合亚型的 composition 效应（pseudobulk 粗粒度），非"divergence 更大"。
3. 星形胶质细胞例外的讨论（median 73.37 高于神经元 median，P=0.41）很好，但应引用 Morel/Wheeler 等区域星形胶质细胞分子特化的系统工作而不仅 Batiuk 2020。
4. 供体数/核数阈值：≥20 nuclei/(region, cell_type)、≥50/region 的下限对 committed OPCs（4,118 核）等稀有类导致 7 个区域的单薄覆盖，Bergmann glia 的 CI 已因此被降级为定性陈述——同类降级声明应对每个稀有类逐一给出。
5. PMI/RIN 相关变量在 Siletti 元数据中可用（post-mortem interval），手稿只调了 detection depth/UMI/mito，建议补 PMI 与 RIN（若可得的 eQTL 质控指标）对 k_n 的回归。
6. Fig. 5e violin 图的 null 分布对 MGE 很窄（SD 2.35），SES=7.2 的可视化会给读者过强印象；建议同时展示 leave-one-donor-out 后的 null。
7. 演化语汇：正文出现 "evolutionary cell biology"（结论段）作为应用方向——在无跨物种验证（r=−0.17）的情况下应删除或限定。

---

## 强项

1. 统计设计匹配度高：block-shuffle + pseudo-region 阴性对照 + donor-stratified null + span/size-matched 控制的组合在同类图谱论文中罕见，且所有否定性结果（39 Strong 候选反富集、无 FDR 显著、Hallmark 弥散）如实报告。
2. 对 k_n 主导、class-size 伪影、tier 阈值不可迁移的自我批判诚实到罕见（equal-n 控制 6.10→1.74 的披露）。
3. 神经元超类的生物学方向与现有文献一致（丘脑转录均一性 vs 皮层神经元区域特化），并非反直觉的伪信号。
4. 复现基建（脚本索引、种子、Zenodo）完备。

---

## 必答问题（作者须在 rebuttal 回应）

1. 神经元三超类的 ω 优势的 k_f / k_n 分解是什么？MGE 的 SES=7.2 由分子还是分母驱动？请给出与 Fig. 5b 等价的组件分解。
2. MGE 与 Upper-layer IT 的显著性是否在 donor-stratified block-shuffle 下存活？leave-one-donor-out 的 P 值范围？
3. 丘脑 P=0.163 是否为 size/power 所限？请给出 size-matched 或功效分析。
4. Note 18 的三个超类核数差异巨大（85k–455k），class-size 与 k_n 的负相关（ρ=−0.648）是否同样作用于超类比较？
5. SEA-AD 分析改为 "positive control" 的依据是什么（q_min=0.145 未过校正）？是否可用 ADNC 分期剂量-反应增强？
6. 请在正文脑结果处删除或限定 "evolutionary cell biology" 及一切可被读作"脑细胞类型受选择"的措辞，并解释为何 ω 排序在 k_n 主导时仍以 ω（而非 k_f）为主报告量。

---

*审稿人：reviewer-brain（神经科学/脑单细胞图谱方向），盲审 nc73 版。*
