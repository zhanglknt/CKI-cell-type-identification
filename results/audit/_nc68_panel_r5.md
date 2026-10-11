# Reviewer 5（统计学怀疑派）独立审稿报告 — CKI nc68 投稿包

**审阅对象**：`CKI_Submission_NC/CKI_Manuscript_NC.docx`（主文 202 段）+ `CKI_Supplementary_NC.docx`（SI，重点 Note 1, 3, 4, 9, 16, 20 及 Methods 3.10–3.13、5.x）
**立场**：假定统计论证有问题，直到被说服。所有攻击均落到原文句子/数字。

---

## 总体评价（3 句）

这是一篇自我披露文化罕见的论文——几乎所有我能想到的攻击面，作者都已在 SI 某处自己戳破过；但"披露"不等于"解决"，若干头条级统计主张与作者自己的 SI 数字直接冲突，且新加的理论框架（Note 20）存在一处确凿的引用性事实错误。ω 作为启发式索引有其价值（内部基线 + 设计匹配零假设的思路是对的），但 Proposition 3 给出的 estimand 解释在其自身诊断所示的误差尺度（k_f 尺度二阶展开 p90 相对误差最高 103%）下不具备所声称的精度。主文与摘要的若干定量表述（AUC=0.80、P<10⁻³⁰⁰、"approximately ancillary"、"remarkably close"）系统性地强于 SI 实际证据，需要按 SI 自己的口径回写。

---

## Major concerns（按杀伤力排序）

### M1. Note 20 §E(iii) 存在数字张冠李戴：k_f-only 的 FPR 0.81–1.00 实为 raw JS / cosine 的值；"分母的可测错误率增益"这一理论核心卖点在引用层面不成立 【严重度：致命级（事实错误）】

- **原文（SI Note 20, §E(iii)）**："under injected neutral drift, **k_f-only** false-positive rates were **0.81–1.00** versus 0.00–0.067 for ω (Supplementary Notes 1, 6)"。
- **但其所引 Note 1 的原文是**："Under pure HK drift… exceedance rates were: ω 0.000, **k_f 0.007**, k_n 0.813, raw JS 0.553, cosine 0.580"；过弥散噪声下 "ω 0.020, **k_f 0.020**…"。k_f-only 在 HK 锚定漂移下的 FPR 是 0.007，不是 0.81。
- **Note 6 (N1) 的原文是**："ω stays calibrated—FPR 0.067, 0.011, and 0.000…, versus **raw JS 0.067/0.811/1.000 and cosine 0.089/0.878/1.000**"。0.81–1.00 属于 raw JS 和 cosine；Note 6 根本没有报告 N1 情景下 k_f-only 的 FPR。
- 主文相应句子（Results, Ground-truth simulation 段）表述正确（"raw JS and cosine inflated to 0.81–1.00"），说明错误是 Note 20 写作时引入的，不是数据来源如此。
- **雪上加霜**：在真实技术重复上，k_f-only 与 ω 打平——SI 3.12："ω was fully calibrated: no pair exceeded its own null 95th percentile (0 of 30)… **k_f alone was equally calibrated (0 of 30)**"。脑 T1 上 k_f FPR 37.6% vs ω 28.6%，差距仅 9 个百分点。
- **后果**：Note 20 §E 为 HK 分母给出的三层增益中，第 (iii) 层"实测错误率"引用了不属于 k_f 的数字；一旦更正为 k_f-only 在模拟中 0.007–0.020、在真实重复中 0/30，分母相对"配备正确零假设的 k_f"的经验增益就缩减为脑 T1 上的 9 个点，而非一个数量级。主文 Discussion 相应句子（"What ω adds beyond k_f is calibration, not detection power"）的方向正确，但理论 note 的定量支撑是假的。此条必须更正，且更正后 §E 的论证结构需要重写。

### M2. "Studentization / approximately ancillary" 主张被作者自己的真实数据证伪；CV 1.21→0.148 在 ρ(k_f,k_n)=0.92 下是机械预期，不是 ancillary 证据 【严重度：高】

- **原文（Note 20 §E(ii)）**："dividing by k_n yields a statistic whose null is **approximately ancillary** to it—the same logic by which dividing by the sample standard deviation turns a mean difference into a t-statistic. Empirically… the coefficient of variation of the class-level null median falls from 1.21 (k_f) to 0.148 (ω)"。主文 Discussion 重复："dividing by k_n studentizes the statistic, collapsing cross-class null dispersion up to eightfold… the logic of a t-statistic"。
- **证伪证据一（作者自己的 Fig. 3 / SI 3.12）**：脑 T1 纯技术漂移上 ω 的 FPR = **28.6%**，名义水平 5%，且随组大小从 14.1%（≤30 核）升至 **48.0%**（>500 核）。一个近似 ancillary 的学生化统计量，其零分布不应系统性地依赖设计协变量（组大小）；FPR 偏离名义值 5.7–9.6 倍且随 n 单调增长，正是非 ancillary 的直接表现。t 统计量类比不成立的根源：t 的分母估计的是产生分子零变异的那个方差，而 k_n（HK 面板 JS）测的是 HK 面板噪声，k_f 的零变异由 top-200 顺序统计量选择（winner's curse）主导——两种不同的噪声源，除法无法学生化后者。
- **证伪证据二（机械性）**：Proposition 5 自己的输入是 ρ(k_f,k_n) = **0.92**（脑 split-half）。两个高度正相关的零统计量相除，跨类离散度必然塌缩——这是代数，不是 ancillary 的发现。且该 CV 只是 **10 个类**的类级零中位数的 CV，无不确定性量化；"up to eightfold" 仅来自脑（mouse 只有 0.436→0.251，1.7 倍），属于挑数据集表述。
- **要求的修正**：§E(ii) 与 Discussion 的 "studentize/ancillary/t-statistic" 表述必须降级为"跨类零中位数的可移植性提高"，并同段引用 T1 FPR 28.6% 与组大小梯度作为该解释的边界。

### M3. C2 的 "α 与校准基线 remarkably close" 不成立：脑 α 中位 14 对脑基线 9.73 差 44%，基线落在 α 分布的 p10 边缘；而 mouse 的 α 从未报告——偏偏 7.70 这个全文校准常数来自 mouse 【严重度：高，含选择性报告嫌疑】

- **原文（Note 20, C2）**："the ratio of mean per-gene energy (top-200 versus HK panel) had median **14 (brain; 10–90% 10.3–22.1)** and 8.5 (Tabula Sapiens; 7.0–14.5)—… **remarkably close to the empirical split-half baselines 6.67–9.73** (Supplementary Note 3), which the calibration constant therefore admits a theoretical reading of"。
- **对账**：脑内部基线 = 9.73，95% CI [9.03, 10.53]（Note 3）。脑 α 的 p10–90 = 10.3–22.1——基线点估计 9.73 低于 α 分布的 p10（10.3），中位差 (14−9.73)/9.73 ≈ **44%**。Tabula Sapiens：α 8.5 对基线 7.67 尚可；mouse：α **根本没有报告**（C2 与 Supp. Fig. 19b 只给脑与 TS 两个数字），而 7.70 偏偏是 mouse 常数。把三个数据基线（mouse 7.70/legacy 6.67、brain 9.73）揉成一个区间 "6.67–9.73" 再与两个数据集的 α 比"同阶"，是修辞而非论证。
- **理论内伤**：在 Proposition 3 自身框架下，split-half（E_f=0）应有 ω₀ ≈ α。脑上 14 vs 9.73 的缺口正是 C1 在 k_f 尺度失效的量化——与作者自己的 Lemma 2 诊断一致（top-200 面板观测对的中位相对误差 10–18%，**p90 最高 103%**，Note 20 Lemma 2 段）。换言之，"校准常数的理论解读"恰好在其最需要成立的尺度上被自己的诊断否决。
- **要求的修正**：补报 mouse α；删除 "remarkably close" 或改为"同数量级但在脑上存在 44% 系统性缺口，该缺口与 k_f 尺度展开误差一致"；明确写出 Prop 3 的 estimand 等式在 k_f 尺度只有定性精度。

### M4. 全文最重要的常数 7.70 的置信区间违反作者自己定下的小簇标准；同一违例出现在 AUC 的 3 簇 cluster bootstrap 上 【严重度：高-中】

- **原文（SI 3.10）**：校准常数 mean ω = 7.70，"two-stage bootstrap over the six populations, B = 5,000: 95% CI [6.38, 9.82]"——**6 个群体**。
- **作者自己的标准（Note 2）**：Monte Carlo 覆盖率研究显示 percentile cluster bootstrap 在 7 簇/6 簇时覆盖率仅 0.876/0.873，并明确"the studentized bootstrap-t… is therefore **the recommended replacement for every statistic resting on ≤ 7 region clusters**"。但 7.70 的区间（恰好 6 簇）并未使用 studentized bootstrap-t，也没有按 Note 2 的口径标注覆盖率不足。
- **同一违例**：主文 AUC = 0.80 的稳健性区间来自 "module-seed cluster bootstrap"——只有 **3 个 module-seed 簇**（Note 1, AUC interval methods 段：[0.771, 0.836]）。按 Note 2 自己的逻辑（6–7 簇已 under-cover 7–8 个点），3 簇 cluster bootstrap 的覆盖率无保障；且该 bootstrap 只对 module seed 聚类，600 个 signal replicate 全部重抽样自同一份 1,848 细胞背景，共享背景相关性未入模型，DeLong 区间 [0.770, 0.838] 同样假设独立 replicate。
- **后果**：主文承认 "ω_cal… one-significant-digit resolution"（Results, Calibration confirms baseline behavior 段），但这一位有效数字本身建立在一个按作者自己标准覆盖率约 87% 的区间上；ω_cal 的所有派生表述（如脑 grand mean ω_cal ≈ 4.0–5.0）的误差条应相应加宽并做敏感性声明。

### M5. 摘要与 Fig. 7 的 P < 10⁻³⁰⁰ 是 pair 级伪重复；设计匹配的证据弱得多（3 个 superclass 中 1 个不显著） 【严重度：中-高】

- **原文**：摘要 "regional divergence far exceeds the non-neuronal median (**P < 10⁻³⁰⁰**)"；主文 Fig. 7b "one-sided Mann–Whitney z = 52.6, P < 10⁻³⁰⁰"；Note 18 甚至给出 "P ≈ 10⁻⁶⁰² (normal approximation)"。
- **问题**：2,995 个神经元 pair 与 31,764 个非神经元 pair 共享区域、供体（仅 4 人）、细胞类，pair 间相关性极强；把 3 万余个相关 pair 当独立观测的 Mann-Whitney，其 z = 52.6 不携带对应的证据量。这与作者自己在别处（TS 相关性的 entry-clustered bootstrap，SI 5.5）承认并修正的 "independence-assuming P-values… retired" 口径自相矛盾——同样是 pair 级数据，这里却启用了 naive P。
- **设计匹配的证据**：block-shuffle 零假设下 MGE 达置换地板（P=0.001）、upper-layer P=0.014、**thalamic excitatory P=0.163 不显著**（Note 18）——即 3 个神经元 superclass 中 1 个不能拒绝零假设，与非神经元 10 类中 4 类拒绝的格局一致。且 astrocytes 一类中位 ω（73.37）已高于神经元中位（62.17），"far exceeds" 是混合效应。
- **要求的修正**：摘要与 Fig. 7b 的 P 值必须标注为 pair 级描述性统计（比照主文对 Mann-Whitney P = 5.6 × 10⁻¹⁸ 已标 "descriptive" 的先例），主证据改为 block-shuffle 结果（2/3 superclass 显著）。

### M6. 地面真值模拟的"中性"类结构性偏袒 ratio 设计；摘要头条 AUC = 0.80 未携带同背景 δ=1 检测力 0/150 的信息 【严重度：中】

- **原文（摘要）**："ω achieved the best discrimination of injected functional signal against neutral housekeeping drift among six metrics (AUC = 0.80)"。
- **结构性问题**：基准的中性类 = HK 基因上的乘性漂移（η）+ 全局 Poisson 噪声。前者直接命中 ω 的分母面板——ratio 设计在该中性模型下必然占优，正如作者自己在 Note 1 对抗段承认的："the type-I and AUC advantages above are therefore conditional on that assumption rather than evidence for it"。raw JS/cosine 无内部基线、设计上必然把漂移计为分歧——这场比较的胜负在出题时已定。Note 6 的 N1（expression-matched 非 HK 漂移）部分补救了 HK 锚定循环，但 k_f-only 检验在 N1 下的 FPR 并未报告（见 M1），"ω vs k_f-only" 这一最重要的对照始终缺席。
- **功率地板**：同一背景下 δ = 1 时 ω 阈值化检测 0/150（Note 1），AUC 0.80 完全来自排序区分；主文有披露（"Rank discrimination and thresholded power diverge"），但摘要只保留 AUC。
- **要求的修正**：摘要 AUC 句补充中性模型依赖与功率地板（或降级为"排序区分"）；补报 N1 下 k_f-only 的 FPR。

### M7. "ω_cal − 1 ≈ E_f/(αE_b)" 把 pair 特异的 α 静默替换为常数；ε 自始至终没有数值界 【严重度：中】

- **原文（Note 20, Proposition 3）**："|ε| bounded by the Lemma-2 remainders, the C4 sampling term, and the pair-to-pair spread of α (C2)—**the dominant term**, which is exactly why absolute ω is dataset-relative… the calibrated statistic satisfies ω_cal − 1 ≈ E_f/(αE_b). **This is the precise biological quantity ω corresponds to within the model class.**"
- **问题**：作者承认 ε 的主导项是 α 的 pair 间散布——C2 给出脑上 p10–90 = 10.3–22.1（围绕中位 14，±30–60%）。用一个常数基线（7.70 或 9.73）去除观测 ω，相当于把 pair 特异 α 替换为其边缘均值；于是 ω_cal 作为 E_f/(αE_b) 的估计量，在任何 k_f/k_n 采样噪声之前就携带 ±40% 量级的乘性误差。"precise biological quantity" 的措辞与自身误差预算矛盾，且全 Note 20 没有任何一处给出 |ε| 的具体数值上界——"ε 小"是靠 scoping 措辞断言的。
- **要求的修正**：删除 "precise"；给出 ε 的数值量级（至少由 C2 散布推出 α 项的贡献）；明确 ω_cal 的解释精度为"一位有效数字 + ±40% α 散布"。

---

## Minor concerns

1. **Lemma 1 的 "exact" 过强**。log1p(λx) ≠ log λ + log1p(x)，且 mouse/human 管线的聚合顺序是 softmax(mean(log1p))（SI 1.1：等价于 (1+x) 的几何平均映射，而非算术 pseudobulk +1），全局标度只对纯对数精确抵消。作者承认 "deviates from a pure logarithm by terms of order 1/x"，但 pilot 分析允许 ≥20 细胞的 pseudobulk，低计数基因的 1/x 项不可忽略；"depth differences are removed by construction, not by approximation" 应改为 "approximately, at pseudobulk count scales"。（另：brief 中提示的 softmax"减 max + ε"实现是标准数值稳定技巧，softmax 平移不变，无统计影响——此攻击面不成立，撤回。）
2. **Proposition 5 的 "< 0.8%" 在主文被无条件引用**（Results: "carries second-order-small calibration bias (Proposition 5, < 0.8%)"），但 Note 4 自己的分箱结果显示 k_n < 10⁻⁴ 的小分母 bin 偏差 +6.5%，且明言 "It does not transfer across k_n scales"。主文引述丢了条件。
3. **"50 independent random split-halves"**（SI 3.10 首句）措辞错误：同一群体的 50 个 split 高度重叠、非独立；推断上已用两阶段 bootstrap 处理嵌套，但措辞会误导读者对有效样本量的判断。
4. **校准常数对单一异常群体敏感**：六个群体中 hepatocyte 均值 12.44 ± 5.98，其余五个 5.77–7.36（SI 3.10）——7.70 被近 2 倍的离群群体上拉，LOPO 区间 6.75–8.08 已披露但主文未提这一脆弱性。
5. **GTEx 外部参照的证据力≈零**：跨队列处理效应移动 k_n 1.8–2.3 倍（主文 A GTEx healthy reference 段末），与声称的肿瘤 k_n 升高 2.0–2.8 倍同量级；用同量级混杂支撑的 "tentatively consistent with tumor-specific elevation" 应进一步降级或移出主文。
6. **全篇单侧上尾检验与 S1 结果矛盾**：Note 1 的 S1 显示 HK 锚定的功能信号使 ω **下降**（检测率 0.000 是因为信号走向下尾）——双侧备择真实存在；固定单侧上尾检验系统性放弃 anchor-moving 方向，与论文反复强调的 "ω must be read alongside its components" 不自洽。
7. **T1 的 per-pair shuffle 零假设构造上即 anti-conservative**：pool 两文库的核再重分，假设跨文库可交换——正是文库级批次效应违反的假设（作者在 block-shuffle 设计中明知此点）。于是 Fig. 3b,c 是一群校准不良检验之间的相对排名；摘要 "the lowest false-report rate" 未注明绝对率全在名义值的 5–9 倍。
8. **Note 16 的维度不变性验证与 Methods 的 "thus" 推理**：随机 Dirichlet 模拟自述 "does not simulate the variance-based gene selection mechanism"，故 Methods 中 "the systematic inflation of k_f over k_n thus arises from HVG selection bias" 的 "thus" 是合理推断而非被验证的结论。
9. **S2 leave-pair-out 并非独立面板**（Note 9 自述聚合了同类其他区域对的区域效应基因）；S0–S2 候选保留率 64%、global-k_n 切换仅 3/39 保留——目录的估计量脆弱性已披露，但与 Fig. 6c,d 给予该目录的展示权重不匹配。
10. **Kang IFN-β 的条件与 lane 完全混杂**（Note 8 披露），"the perturbation was visible at the ω level in all six cell types"（主文）不可归因于生物；ACTB/GAPDH 下降 40% 的"锚机制"解读同样不可与 lane 效应分离。
11. **AUC=1.00 的 microglia sanity check**（Note 7）：35 个 functional pair 共享样本（563 个 group 内配对），pair 非独立，Mann-Whitney P = 5.5 × 10⁻¹⁴ 为描述性；且该分析用 global-HVG 方案，与 7.70 校准尺度不可比（作者已注明，但主文引用时未带此限定）。
12. **神经元 superclass 的 SES = 7.2 at permutation floor**（Note 18）：B = 1,000 时 P = 0.001 位于地板，SES 对 Monte Carlo 噪声敏感，不宜与 P 同时作为证据强度引用。

---

## 评分（1–10）

| 维度 | 分数 | 一句理由 |
|---|---|---|
| 新颖性 | **7** | Ka/Ks 式内部基线 + 设计匹配零假设的组合在单细胞分歧度量中确有新意，但本质是启发式重组（作者自述 "recombining established ideas"）。 |
| 严谨性 | **5** | 披露文化一流、稳健性分析覆盖面广；但 M1 的事实性引用错误、M2/M3 中理论表述与自身 SI 数据的直接冲突、M4 的自定标准自我违例，拉低到及格线。 |
| 广泛兴趣 | **5** | 方法学受众明确，但唯一的图谱级生物学产出（候选目录）无 FDR 存活项，泛癌发现是分母效应的重述，广泛兴趣受限。 |
| 可复现性 | **9** | 开源包 + Zenodo + Dockerfile + 逐脚本/逐输出文件索引 + Reproducibility Guide，且 SI 给出大量可核对的过程数字，属上乘。 |

## NC 中稿概率估计

**约 15%。** 一句话理由：这是一篇"自我削弱"写得比"主张"更诚实的论文——审稿人会发现头条统计论证（Note 20）存在事实性引用错误且核心理论表述被论文自己的 SI 数据证伪，而没有任何 FDR 存活的生物学发现来兜底，NC 对"启发式索引 + 阴性结果"组合的门槛很难在大修内跨过；修改后转投 Genome Biology / Bioinformatics 一类期刊更为现实。

## 必须修复项（≤5）

1. **更正 Note 20 §E(iii) 的 FPR 归属错误**（0.81–1.00 属于 raw JS/cosine，非 k_f-only），补报 N1 情景下 k_f-only 的真实 FPR，并重写"分母增益"论证——必须纳入 Kang 真实技术重复上 k_f-only 与 ω 同为 0/30 的事实，以及 ρ(k_f,k_n)=0.92 下比率压缩离散度的机械性解释。
2. **补报 mouse 的 α，删除或限定 "remarkably close"**：解释脑 α 中位 14 与脑基线 9.73 的 44% 缺口（基线低于 α 的 p10），并将该缺口与 Lemma 2 诊断的 k_f 尺度展开失效（p90 误差最高 103%）显式关联；Proposition 3 的 estimand 等式标注为 k_n 尺度定量、k_f 尺度定性。
3. **按作者自己的 Note 2 标准重算校准常数区间**：7.70 [6.38, 9.82]（6 簇）与 AUC 稳健性区间（3 簇 module-seed bootstrap）改用 studentized bootstrap-t 或明确标注覆盖率不足，并对 ω_cal 派生结论做区间敏感性声明。
4. **降级 studentization/ancillarity 表述**（Note 20 §E(ii) + 主文 Discussion）：CV 1.21→0.148 只能表述为"跨类零中位数可移植性"，且必须同段引用 T1 FPR 28.6%（名义 5%）及其 14.1%→48.0% 的组大小梯度作为该解释的直接边界；撤回 "approximately ancillary" 与 t-statistic 类比。
5. **摘要与 Fig. 7b 的 P < 10⁻³⁰⁰ 标注为 pair 级描述性统计**，主证据改为 block-shuffle（3 个 superclass 中 2 个显著、thalamic P = 0.163）；同理由 SI 5.5 已退休 naive pair 级 P 值的口径，此处不得双重标准。
