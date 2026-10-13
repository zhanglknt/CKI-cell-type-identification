# nc73 理论修订盲审（统计/信息论审稿人，reviewer-stat）

**一句话总结：** 本轮 Note 20 修订对三条理论批评的回应总体扎实且异常诚实——交叉项显式入式、可识别性论证补全、单调性三层拆分在数学上我逐项手工复核均成立（包括 Lemma 2 的二次系数 1/(8 ln 2) 与三阶 Lagrange 余项常数 5/(48 ln 2) 的精确性），但 Identification 段的 A1 "by construction" 表述与其自身 Supplementary Note 8 的实证相矛盾，构成剩余的最大理论软肋。

**Overall score: 7/10**
**NC 中稿率估计：约 25–35%**（理论框架本轮已无明显硬伤，主要风险从"数学不成立"转移为"生物学解释力与 A1 的实证性"）

---

## 逐项数学核验结果（我亲自推导）

### 已确认正确的部分

1. **Lemma 2（Note 20, para 249）——精确无误。** 我从 H(p+t) 的三阶 Taylor 展开（f'''=−1/(ξ² ln2)，Lagrange 余项在 ξ ∈ [p−|δ|, p+|δ|] 上取界）手工推导：JS(p,q) 的二次项系数恰为 (1/(8 ln 2))，三阶余项系数 H(m) 贡献 1/48、−½H(q) 贡献 4/48，合计恰为 **5/(48 ln 2)**——文中常数与我的推导完全一致，且线性项逐点为零（无需 Σδ=0 假设）的说法正确。余项分母 (p_i−|δ_i|)₊² 是保守但正确的取法。

2. **Lemma 1b（para 248）——方向正确。** softmax 一阶展开 δ_i = p_i(g_i−ḡ) 标准成立；二阶项 p_i(g_i²−E_p g²)/2 均值为零，故 Σδ²/p 的主阶恰为 Var_p(g)，余项 O(‖g‖³) 在 p 加权 L2 范数下自洽（交叉项 Σp|g−ḡ|·‖g‖² ≤ ‖g‖³）。旧的未加权 Σg_i²/p_i 口径确实错误，替换正确。

3. **Lemma 1 的 log1p 泄漏界（para 247）——展开式正确。** log1p(cx)−log1p(x) = log c + (1/(cx)−1/x) + O(1/x²) 我逐项核对无误；泄漏场 (1/c−1)/x 及其 p 加权能量界结构合理（依赖 Var_p(1/x) ≤ 10⁻⁴，即 x ≳ 10²，文中有声明）。附带确认：softmax(log1p(x)) ∝ 1+x 与 Methods 1.2/1.3 的"伪计数+1 后 L1 归一化"在数学上是同一个对象（(x+1)/Σ(x+1)），故 Note 20 的 log-softmax 框架与操作管线口径一致，这是一个容易被忽略的一致性亮点。

4. **Proposition 4(a) 的 Cauchy–Schwarz 保证条件（para 253）——正确。** ∂ω/∂λ = 2(λE_f+C_bf)/E_b > 0 在最坏 C_bf = −√(E_bE_f) 下等价于 λ²E_f > E_b，文中"λ²E_f > E_b 时必有保证"精确无误。交叉项随 λ（非 λ²）缩放、故 C5 外不存在 α 无关单调性的论断，是本轮最诚实的一句修正。

5. **C5 的最坏界（para 250）自洽。** |2C_bf|/E_b ≤ 2√(E_f/E_b)，与 Prop 4(a) 的保证条件处于同一"功能能量压倒背景"的 regime——两个结论互不矛盾，口径统一。

---

## Major Concerns

**M1. A1 "excluded by construction" 与自身数据矛盾（Identification 段, para 252；对照 Note 8, para 196）。** A1 声称 HK 面板上 φ=0 是"by construction"——因为 HK 基因是预先指定为跨条件稳定表达的。但这在逻辑上是不严密的：HK 基因列表（HRT Atlas）是按跨细胞类型/组织的表达稳定性遴选的，"预先指定"不等于"条件驱动的调控变化在数学上被排除"。更严重的是，作者自己的 Supplementary Note 8 给出了直接反例：IFN-β 刺激使 ACTB、GAPDH（典型 HK 基因）下降约 40%，k_n 升高 1.2–5.7 倍——即在他们自己的真实扰动数据中 φ ≠ 0 on HK panel。这构成对 A1 的实证证伪。建议：(i) 将 "excluded from that panel by construction" 改为 "excluded by assumption"，(ii) 在 Identification 段显式交叉引用 Note 8 的 anchor-visibility boundary，承认 A1 在"扰动触及锚基因"的 regime 下失效并给出该 regime 的检测信号（k_n 自身大幅抬升）。目前的写法在严格审稿人手里会被视为循环论证（用 HK 的稳定性定义去保证一个依赖 HK 稳定性的识别假设）。

**M2. Prop 4(b) 局部单调性在关键尺度上没有被定量建立（para 253(b)；对照 Lemma 2 诊断, para 249）。** (b) 层的余项导数只给出阶 O(Σ(|δ_i|/p_i)²|dδ_i/dλ|)，无显式常数，且其"small wherever C1 holds"的前提恰恰在 k_f 尺度上被作者自己的诊断削弱：top-200 面板上观测对的展开误差中位 10–18%，脑数据 90 分位高达 103%（|δ_i|/p_i 超过 1）。这意味着在 ω 实际被使用的尺度上，"raw-JS 比值在观测 λ 邻域内严格单调"并没有定量保证——(b) 层实际上退化为一句定性陈述。建议至少给出：在 90 分位误差 ≤ X% 的子集上，余项导数与二次型导数之比的数值界（用 theory_diagnostics 的数据即可算出），否则 (b) 层应如实降格为"经验上在该区间成立"。

**M3. 理论 α 与操作校准常数的断裂未闭合（C2, para 250 vs Note 3, para 175）。** 理论定义 α = E_b(top-200)/E_b(HK)，split-half 估计中位 14（脑）/8.5（TS）；但操作校准用的是 ω 基线 9.73（脑内部）/7.70（小鼠）。文中所给解释（α 是 per-gene 能量比、基线还折叠了面板大小/组成与 k_f 尺度展开误差）方向合理，但量化上未闭合：ω_cal − 1 ≈ E_f/(αE_b) 中的 α 到底取 14 还是 9.73？二者相差约 1.4 倍，直接决定 E_f 的理论读数。建议给出一个数值例子（取一对真实 pair，展示用两个 α 读出的 E_f/E_b 各是多少），或明确声明理论 α 只用于定性结构、绝对校准以经验基线为准。

---

## Minor Concerns

**m1. Lemma 1b 余项范数未定义（para 248）。** O(‖g‖²)、O(‖β+φ‖³) 中的 ‖·‖ 从未指定是哪个范数（p 加权 L2？sup？）。阶数结论依赖范数选择，建议一句脚注钉死为 p 加权 L2 范数并确认各处一致。

**m2. "Σδ_i = 0 to first order" 的表述偏弱（para 248）。** 对 softmax 而言 q 本身是概率向量，Σδ_i = 0 是精确成立的，无需"一阶"限定。无损但可顺手改精确。

**m3. E_f/C_bf 的面板归属有记号歧义（Prop 3, para 251）。** E_b 定义在 HK 面板（测量 (i)），E_f、C_bf 事实上定义在 top-200 面板，但记号上不带面板下标，ω = α + (E_f+2C_bf)/E_b 一式把两个面板的量直接相除。理解无碍但首次阅读容易混淆，建议在 Lemma 1b 末尾加一句"on the respective panels"。

**m4. ρ = 0.688 的证据强度表述（para 253(c) 与正文引用）。** Spearman 0.688 高度显著（P = 5.1×10⁻¹⁶²，n 显然很大）但相关系数本身中等；网格均值 10.2→27.2 单调才是主要证据。正文引用"ground-truth ρ = 0.688"作为单调性支撑，对不读 SI 的读者略显单薄。建议正文同句补网格均值区间，或 SI 中报告各 δ 档内的组内离散度。另外该网格构造上 C_bf = 0（Fig 2c 已注明），故它完全不检验无 C5 分支——作为 (c) 层兜底可以，但应明写它只覆盖 C5 分支。

**m5. Prop 4(a) 中 α 在 φ→λφ 下被固定。** 强化功能因子会改变 top-200 面板的选择，从而 α 原则上随 λ 变化。post-selection caveat 已覆盖此点，但 (a) 层公式未提醒，建议括号内一句。

**m6. Identification "linear system" 的"unique solution"是近似的。** 三个测量中 (i) 和 (iii) 依赖 Prop 3 的近似（C1），且 α 用的是 split-half 群体值而非 per-pair 值（C2 的 pair-to-pair spread 被作者自己列为 ε 主导项）。"identified, not merely defined" 的措辞略强于实际（"identified within the scoped approximation"），Scope 段已有缓冲，但 Identification 段内最好同句带上限定。

---

## 强项

- **余项显式化与诚实 scoping**：Lemma 2 给出精确 Lagrange 常数（我复核无误）+ 真实数据上的展开误差诊断（0.23% vs 103% 都敢写），这在方法论文中罕见。
- **三层单调性拆分**：把"近似层/原始 JS 层/全局层"分开并各自如实限定，删除了旧稿越界的 "independently of α"，直接回应了批评且方向正确。
- **C5 的处理方式是范本级的**：不回避不可检验假设，而是用 Cauchy–Schwarz 给出最坏偏差 2√(E_f/E_b) 并要求每个引用 C5 的论断同句携带该界。
- **正文与 SI 同步**：正文单调性句子已补 "under the stated conditions"，Theory 段落（Note 20 intro 的 normalization 口径 softmax(log1p(c)) 与 Methods 伪计数+L1 归一化数学上同一）一致。
- **自证其反的透明度**：S1 functional-on-HK 场景（Note 1）与 Note 8 的锚基因失效案例都被主动写进 SI，虽然与 A1 的表述产生了 M1 的矛盾，但这种透明度本身是加分项。

## 必答问题（给作者）

1. A1 与 Note 8 的 ACTB/GAPDH 反例如何调和？在 IFN-β 数据中，按你们的口径 E_b 和 φ-on-HK 各是多少——A1 失效时 ω 的偏差是否落在 2√(E_f/E_b) 界内？
2. ω_cal − 1 ≈ E_f/(αE_b) 中的 α，读者应该用理论的 14/8.5 还是操作的 9.73/7.70？能否给一个数值示例？
3. 在 k_f 尺度 90 分位展开误差达 103% 的脑数据子集上，Prop 4(b) 的局部单调性还成立吗？能否用 theory_diagnostics 的数据给出余项导数/二次型导数比的实证分布？
4. Lemma 1b 的 ‖·‖ 是哪个范数？请全文钉死并统一。
