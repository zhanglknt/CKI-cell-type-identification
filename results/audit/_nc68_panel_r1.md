# Reviewer 1 报告（统计基因组学与方法论）— CKI nc68 投稿包

**稿件**：CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases（Nature Communications 投稿，nc68 版）
**审阅范围**：主文全文；SI Notes 1–20 全部 + Supplementary Methods 1.1–1.7、3.1–3.13、4.1–4.5、5.1–5.14；Cover Letter 未列为重点。以下为独立审稿意见。

---

## 总体评价（3 句）

CKI 提出 ω = k_f/k_n（identity 基因面板的 JS 散度 / housekeeping 面板 JS 散度），以 Ka/Ks 为启发做基线归一化的细胞群体分化度量，思路直观、工程实现与可复现性优异，且对自身局限的披露程度在本领域来稿中罕见地诚实（Note 1 对抗性场景、Note 9 循环性消融、Note 11 类大小混杂、Note 12 阴性对照）。然而 nc68 新增的 Note 20「scoped theoretical framework」是本轮主要弱点：estimand 链在关键环节（选择常数 α 的定义与测量、二次展开在 k_f 尺度的失效、post-selection 面板的估计量身份）上并未闭合，且该 Note 内部存在对自身结果的误引。方法的核心经验性质（drift 排斥、studentization 压缩零分布离散度）有真实价值，但部分头条推断建立在把大量重叠配对当作独立样本的 P 值上，与作者自己倡导的设计匹配零假设原则相抵触。

---

## Major concerns

### M1. Note 20 的 α 诊断量与分裂半基线之间的算术链不闭合（严重度：高）
- **证据**：Note 20 条件 C2 称"the ratio of mean per-gene energy (top-200 versus HK panel) had median 14 (brain; 10–90% 10.3–22.1) and 8.5 (Tabula Sapiens)… remarkably close to the empirical split-half baselines 6.67–9.73"。
- **问题**：(i) "mean per-gene energy"未定义是算术平均还是概率加权平均。由 Lemma 2，k_n ≈ (1/8ln2)·Σ_i∈H δ_i²/p_i，而 Σ_H δ_i²/p_i = E_{p_H}[r²]（以 p_i 为权的相对位移平方的**加权平均**，权重和为 1，不含面板大小因子）；若诊断量是逐基因 e_i = δ_i²/p_i 的**算术**平均，则它与 ω 之间差一个 |I|/|H| ≈ 200/1115 ≈ 0.18 的因子，预测基线 ≈ 2.5，与观测 9.73 差约 4 倍；若诊断量是 r_i² 的未加权平均，则与加权 JS 之比还依赖 r² 与 p 的相关结构。三种读法给出三种不同的 α，Note 未给出从诊断量到基线的恒等式。(ii) 即便按对作者最有利的读法，脑 α = 14 vs 脑基线 9.73 相差 44%，"remarkably close"不成立；且比较区间"6.67–9.73"的下端 6.67 是 Note 3 明确声明已被取代（superseded）的 legacy 估计（现行小鼠基线 7.70），用它展宽区间向 α 值靠拢有修辞之嫌。(iii) α 仅在**零假设**（split-half）下测量；winner's-curse 选择在含真实功能信号的对上会改变 top-200 面板构成，α_signal ≠ α_null 未做任何验证，而该差异直接进入 Proposition 3 的 ε。(iv) 作者自己的数据直接反驳 C2 的"roughly pair-independent"：Section 3.10 六个对照群体的人均基线 5.77–12.44（2.2 倍散布，hepatocyte 明显离群）；Note 8 Kang 各细胞类型 split-half 中位 ω 6.7–18.9（2.8 倍）。α 的逐对/逐群体异质性意味着未校准 ω 的跨对比较部分反映 α 噪声——这正是 Proposition 3 承认 ε 以 α 散布为主项的后果，但主文大量细粒度排序（如 Table 1、Fig. 5）并未传播这一不确定度。
- **要求**：给出 α_diag → ω_baseline 的显式恒等式（含权重定义与面板大小因子），或删除"remarkably close"与"the calibration constant therefore admits a theoretical reading"的断言；在信号情形下验证 α 稳定性；对基于 ω 绝对差的排序结论声明 α 散布的影响。

### M2. 二次展开恰在功能信号所在尺度失效，estimand 因此只是近似且为 post-selection 量（严重度：高）
- **证据**：Lemma 2 诊断（2,937 真实对）：HK 面板在观测对上的中位相对误差 2.5–4.0%（定量），但 top-200 面板在观测对上 10–18%、脑数据 90 分位达 103%（"per-gene relative displacements exceed 1"）。
- **问题**：(i) Proposition 3 的 ω = α + E_f/E_b + ε 依赖 C1；C1 在 k_n 尺度成立、在 k_f 尺度不成立，而 E_f（功能位移能量）只出现在 k_f 中。也就是说，**该框架对核心估计量 E_f/E_b 的控制在信号最强处最弱**，Note 20 却称"This is the precise biological quantity ω corresponds to within the model class"——"precise"与实际误差结构（尾部 100% 相对误差）不匹配，应明确降级为 order-of-magnitude 陈述。(ii) 估计量是定义在**由观测差值选出的面板**上的（per-pair top-200 by |Δ|）：选择规则使 E_f 的估计本身带有 winner's curse，且面板随数据变化，ω 的 estimand 是一个数据依赖的、post-selection 的泛函，而非固定生物学量。C3 仅以 leave-pair-out 消融（k_f 中位膨胀 1.61 倍）旁证，未把该膨胀纳入 ε 的误差预算（Note 20 列出的 ε 上界只有 Lemma 2 余项、C4 采样项、α 散布三项，**不含选择膨胀**）。(iii) Proposition 4 的比较静态（φ → λφ ⇒ E_f → λ²E_b 不变 ⇒ ∂ω/∂E_f = 1/E_b > 0）假设面板固定；操作上增强 φ 会改变 top-200 成员，E_b 与 α 并非不变，"independently of α"的单调性证明在实际算法路径上不成立，只剩 ρ = 0.688 的经验支持（该值本身只是中等强度）。
- **要求**：在主文与 Note 20 中把 estimand 明确标注为 post-selection、方案依赖的近似量；将选择膨胀纳入误差预算或删除 ε 的"bounded by"断言；重写 Proposition 4 的证明范围或降级为启发式陈述。

### M3. Note 20 第 (iii) 条误引己方结果，夸大 ω 对 k_f 的优势（严重度：高，但易修复）
- **证据**：Note 20 "What the HK denominator adds"第 (iii) 条："under injected neutral drift, k_f-only false-positive rates were 0.81–1.00 versus 0.00–0.067 for ω (Supplementary Notes 1, 6)"。
- **问题**：所引 Notes 中并不存在 k_f 的 0.81–1.00。Note 1 给出纯 HK drift 下 k_f FPR = 0.007、全局过散噪声下 0.020；0.81–1.00 是 Note 6 N1 中 **raw JS（0.811/1.000）与 cosine（0.878/1.000）** 的数字，N1 未报告 k_f。反之，Note 6 N2（基因身份置换）下**包括 ω 在内的所有指标 FPR = 1.00**，而"ω 0.00–0.067"的引用区间恰把 N2 排除在外。该句把未标准化指标的失败安到 k_f 头上、同时对 ω 选择性引用，出现在论证"分母必要性"的关键段落，属于必须更正的实质性误引。
- **附带**：Discussion（主文 Limitations 前一段）称"under fourfold cell-count imbalance (simulation) k_f misreports 38% of neutral pairs, ω none"，我在 Note 1/Note 6 中无法定位该 38%（Note 1 的四倍失衡场景是在 δ = 1 有信号条件下报告 ω −32% / k_f +67% 的偏移，并非中性对误判率）。请指明出处或删除。

### M4. 头条跨类对比使用伪重复 P 值，与作者自己的设计匹配原则冲突（严重度：中高）
- **证据**：摘要与图 7b："regional divergence far exceeds the non-neuronal median (P < 10⁻³⁰⁰)"；Note 18 同一检验 z = 52.6、P ≈ 10⁻⁶⁰²（正态近似），主文却又保守地写成 < 10⁻³⁰⁰（两处精度不一致）。
- **问题**：该 Mann-Whitney 把 2,995 个神经元对 vs 31,764 个非神经元对当作独立样本，而配对高度共享脑区与文库（606 个文库、4 个供体），有效样本量远小于对数，P 值被任意压缩。作者自己在 Note 10 中对同类情形明确标注"treat pairs as independent and are reported as descriptive only, with the cluster bootstrap carrying the inferential weight"，但对这一登上摘要的对比未做同等限定；设计匹配的 block-shuffle 检验实际只支持 3 个 superclass 中的 2 个（thalamic excitatory P = 0.163 不显著，主文 Results 已披露）。同样地，Note 17 的 germ-layer 检验 P = 4.5×10⁻¹⁴⁶、Note 10 组成分检验 P < 10⁻⁹⁰ 等均属对级伪重复（部分已标 descriptive）。摘要与主文应一律以设计匹配统计量（block-shuffle / donor-cluster）领衔，伪重复 P 值只能作为描述性补充并统一标注。

### M5. 校准常数的置信区间落在作者自己证明不可靠的小簇 regime，且未用其推荐的修正（严重度：中）
- **证据**：ω_cal = ω/7.70，7.70 的 95% CI [6.38, 9.82] 来自对 **6 个群体**的两阶段 percentile bootstrap（Section 3.10）。Note 2 的 Monte Carlo 覆盖率研究显示 percentile cluster bootstrap 在 6–7 簇时覆盖率仅 0.873–0.876（名义 0.95），并据此把 Bergmann glia、choroid plexus 的区间全部替换为 studentized bootstrap-t。
- **问题**：校准分母是所有 ω_cal 的根基，其区间却未做同样的 studentized-t 修正——Note 2 的修正逻辑没有被应用到最需要它的量上；区间实际覆盖率可能只有 ~0.88，"±21% half-width、一位有效数字"的声明本身可能被低估。此外 Note 4 报告脑 split-half 的比率估计偏差"pooled −1.8%（中位 +0.2%）"，而 Proposition 5 用 delta 法给出脑 −0.18%——同为 split-half 产物、同称 delta-method 预测，相差 10 倍；Note 4 称偏差被 delta 法"tracked almost exactly（ρ = 0.99）"，那只是跨组相关，不能调和水平差异。两处数字需要调和。

### M6. TCGA 反转的推断层级需要重新表述（严重度：中）
- **证据**：主文 Results："cluster-bootstrap CI excluding 1 in four of five"；Methods/5.2：TCGA 逐癌置换检验（固定面板、反保守）"all P > 0.9 … uninformative … the reversal claim rests on the pair-level cluster bootstrap"。
- **问题**：在唯一的设计匹配假设检验完全无功效（且反保守、P > 0.9）的情况下，"反转"的全部统计证据是 ratio-of-means 的 bootstrap CI 排除 1——这是估计精度陈述而非对状态差异的检验，再叠加 softmax→linear 映射使 LIHC 结论翻转（1.29 [1.09,1.53] → 1.11 [0.94,1.30]）这一敏感性，主文"pan-cancer reversal … robust at tissue level"的措辞偏强。另：主文称全肿瘤置换（B = 10,000）下"KRAS P ≤ 0.001, all EGFR contrasts P ≥ 0.28"，而 Section 3.13 报告的同型置换给出 KRAS–EGFR P = 0.003、EGFR–WT P = 0.21——若前者是调整后模型、后者是未调整，请在两处互相引用时明确标注，否则数字对不上。

---

## Minor concerns

1. **同一数量两个口径**：主文（Results、Fig. 5、Table 1）反复称 same-cell-type cross-organ 配对 n = 59，Note 17 的 distance-0 锚点却写 n = 69（median k_f 0.106）。若为 CL 映射后口径不同请注明，否则是硬不一致。
2. **基线均值不一致**：Note 1 报告 marrow 基线 ω 均值 11.6（95 分位 20.8），Proposition 4 的因子网格在 δ = 0 处均值 10.2——同一背景同一统计量差 12%，请说明是否为不同重复集。
3. **小鼠 ω–k_f 耦合在数学下限上**：Note 5 显示小鼠全矩阵的 k_n 置换下限 0.857 [0.843, 0.870]，观测 0.821 几乎贴在下限上——即小鼠中 ω 与 k_f 的高相关是被共享分子数学强制的。主文 Fig. 2b,c 的单调层级论证部分建立在小鼠数据上，应在主文一句话披露（现仅见 SI）。
4. **"lowest false-report rate among continuous divergence metrics"**（摘要）：marker Jaccard 在 T1 FPR 19.9% 低于 ω 的 28.6%（McNemar P = 5.6×10⁻²¹），"continuous divergence metrics"这一限定有类别裁剪之嫌；SI 3.12 已诚实披露，建议摘要也加半句限定。
5. **脑 per-pair null 的 5% 名义水平全面失守**（T1 各指标 FPR 19.9–45.2%）：说明 size-matched cell-shuffle null 在存在 library 效应时本身不是有效零假设；ω 的优势是相对的。主文已披露，但 Fig. 3a 的 Kang"0 of 30 fully calibrated"与此并读时，应提示 Kang 结论可能是平台/组织特异的。
6. **功效随样本量坍缩**（3.11：n ≥ 500 细胞/组时置换功效 ≈ 0，操作窗 ~50–200）：这是该统计量的非常规性质（更多数据 → 零分布爆炸 → 更保守），建议在主文 Limitations 中解释机制（现仅一句带过），并说明脑图图谱级分析（每组数千 nuclei）为何不受同一机制支配。
7. **数字表述**：主文 "adjusted log-ω ratio 1.19 [1.12, 1.26]"——log 尺度上的"ratio"表述含糊（是 exp(Δ) 还是 Δ）；Note 18 P ≈ 10⁻⁶⁰² 与主文 P < 10⁻³⁰⁰ 需统一；Note 2 的校准梯度 5.99 [4.43, 7.69] 与主文 raw 梯度 6.10 [5.55, 9.63] 并存，建议在主文注明两个梯度口径（raw vs calibrated）。
8. **Lemma 1 的 log1p 修正项**称"order 1/x per gene, negligible at pseudobulk count scales"——对小计数 HK 基因（pseudobulk 均值可 < 1）该近似未必可忽略，建议给出数值界而非定性一句。
9. **Tabula Sapiens 方法比较**每 entry 只取最大供体（Methods 5.5 自承"does not capture inter-donor variability"），负相关结论（r = −0.36 ~ −0.46）的外部效度受限；entry-clustered bootstrap 已做，但供体维度的缺失无法由重采样修复，建议补一个多供体敏感性或明确限定结论范围。
10. **SE 环境**：Python 3.14.4 为极新版本，requirements-lock 之外的长期可复现性依赖 Docker；建议 CI 增加 Windows/macOS（现仅 Linux CI + 本地验证）。

---

## 评分（1–10）

| 维度 | 分数 | 说明 |
|---|---|---|
| 新颖性 | 6 | Ka/Ks 类比与自归一化双速率对比有概念新意，但实现是两段 JS 散度的比值，方法本身简单；Note 20 的理论包装未增加实质深度 |
| 严谨性 | 5 | 经验诊断与自我证伪异常扎实（加分），但理论框架的 estimand 链不闭合、己方结果误引、伪重复 P 值上摘要（减分） |
| 广泛兴趣 | 6 | 图谱尺度"零假设优先"的筛查理念对单细胞领域有普适价值；TCGA 与脑图谱应用是 bulk/组织级，受众偏方法学 |
| 可复现性 | 9 | 开源包 + Zenodo + Docker + 逐脚本索引 + 大量 superseded 归档与阴性对照，教科书级 |

## NC 中稿概率估计

**约 20%**。理由：方法的诚实披露与可复现性达到 NC 标准，但核心统计量只是 JS 比值、理论层（Note 20）经不起细查且存在误引，头条 P 值伪重复，在竞争激烈的 NC 方法学赛道大概率被要求大改后转向更专业的期刊（如 Nat Methods 的 Brief Communication 或 Genome Biology）。

## 投稿前必须修复项（≤5 条）

1. 更正 Note 20 第 (iii) 条对 k_f FPR 的误引，并全文交叉核对所有 FPR/功效数字的出处（含 Discussion 的"38%"）。
2. 给出 α 诊断量 → 分裂半基线的显式算术恒等式（含权重/面板大小因子），否则删除"remarkably close"与校准常数的理论解读；在含信号情形下验证 α 稳定性。
3. 摘要与主文的跨类对比一律改用设计匹配统计量领衔（block-shuffle / donor-cluster bootstrap），伪重复 P 值统一标注 descriptive；统一 P < 10⁻³⁰⁰ 与 10⁻⁶⁰² 的口径。
4. 对 6 群体的校准常数区间改用 studentized bootstrap-t（与 Note 2 自家建议一致）或声明其覆盖率局限；调和 Note 4（−1.8%）与 Proposition 5（−0.18%）的比率偏差数字。
5. 把 estimand 明确标注为 post-selection、方案依赖的近似量（删除 "precise biological quantity"），将 per-pair 选择膨胀纳入 Proposition 3 的误差预算。

---

*Reviewer 1（统计基因组学与方法论）— 审稿完成。所有引用数字均出自 nc68 投稿包原文（主文段落与 SI Note/Section 编号如上）。*
