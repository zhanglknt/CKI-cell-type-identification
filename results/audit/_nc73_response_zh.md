# 关于 Supplementary Note 20 三条理论批评的逐条回复

稿件：CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases（NC 投稿，nc73 修订轮，commit 3a97c49）

日期：2026-10-13

总览：三条批评全部接受并已完成修改——Supplementary Note 20 大幅重写，正文引用 Proposition 4 的句子同步补限定（同长置换，词数净零）。交叉项现已显式入式、可识别性论证已新增、单调性结论已按三层严格区分。验证：build 226/226、MS 129/129、SI 120/120、CL+Guide 44/44、XV8 64/64（MAIN 4,992/5,000 词）、pytest 29/29、fresh-DOCX 交叉核验 15/15。

## 批评 1：平方展开遗漏交叉项 2·Σ b_i f_i/p_i（连带 log→概率位移换算、log1p 尺度不变性、α 定义）

**批评原文：**「背景位移 b_i 与功能位移 f_i 相加后，平方展开包含 2Σ b_i f_i/p_i，其中 p_i 是基准概率。稿件漏掉这个交叉项，也没有给出使它消失的条件。因此，尚不能推出『功能变化越强，ω 必然越大』。log 表达因子转成概率位移、log1p 的尺度不变性，以及 α 的定义，也仍需修正。」

**回复：**批评完全成立，我们逐点接受。旧稿的平方展开确实丢掉了交叉项且未给出消失条件，且把 log 空间因子直接当作概率位移使用。本次修订分四步修复整条链：

**(a) 修正 log 因子 → 概率位移的换算。** 新增 Lemma 1b，给出 softmax 的一阶展开 δ_i = p_i(g_i − ḡ) + O(p_i||g||²)，其中 ḡ = Σ_j p_j g_j 为 p 加权均值；由此 Σ_i δ_i = 0 自动成立，且单纯形上 log 因子的自然能量是 **p 加权方差**，而非旧稿的未加权 Σ g_i²/p_i。新文本摘录：

*“Lemma 1b (from log-factors to probability displacements). … We therefore define energies on a panel as E_b = Var_p(β) and E_f = Var_p(φ), and for the summed displacement β + φ the quadratic form decomposes as Σ_i δ_i²/p_i = E_b + E_f + 2C_bf + O(||β + φ||³), where C_bf = Cov_p(β, φ) = Σ_i p_i (β_i − β̄)(φ_i − φ̄) is the cross term. This decomposition, not the unweighted Σ g_i²/p_i, is the correct probability-scale reading of the log-space factor model.”*

**(b) 交叉项显式进入 estimand，并给出消失条件与最坏情形界。** Proposition 3 重写为 k_f ≈ (1/8 ln 2)(E_f + **2C_bf** + αE_b)；新增条件 **C5**（Cov_p(β, φ) = 0）使交叉项消失；放松 C5 时不再回避，而是显式量化后果：

*“Under C5 it vanishes and ω = α + E_f/E_b + ε … Without C5 the estimand is ω = α + (E_f + 2C_bf)/E_b + ε: functional and background energy no longer separate, and ω picks up 2C_bf/E_b, bounded in magnitude by 2√(E_f/E_b) (Cauchy–Schwarz).”*

即：无 C5 时 ω 最多偏离 2√(E_f/E_b)——功能信号强于背景时偏差自然小，弱功能信号叠加不利负协方差时结论如实标注为可失效。每个引用 C5 的论断都同句携带该界。

**(c) log1p 的尺度不变性由定性一句话升级为显式界。** Lemma 1 旧文仅有「order 1/x per gene, negligible」，现改为：

*“log1p(cx) − log1p(x) = log c + (1/(cx) − 1/x) + O(1/x²), so rescaling leaks a gene-dependent field (1/c − 1)/x rather than an exact constant. The leak is explicitly bounded: for c ∈ [1/2, 2] its p-weighted energy is at most ((1 − c)/c)² Var_p(1/x), which is ≤ 10⁻⁴ ((1 − c)/c)² at pseudobulk count scales … (consistent with the twofold-depth scenario of Supplementary Note 1: c = 2, bound ≤ Var_p(1/x)/4).”*

**(d) α 钉死为精确的操作性定义。** 条件 C2 重写：**α = E_b(top-200)/E_b(HK)**，即 pair 特异 top-200 选择对背景位移总能量的面板换算因子（只乘 E_b，因为选择作用于背景幅度）；在 split-half 零对（构造上 E_f = 0）上以 mean per-gene 背景能量比估计，中位 14（脑）/ 8.5（Tabula Sapiens），数值与此前分析一致。

**修改位置：** Supplementary Note 20 —— Lemma 1、新 Lemma 1b、条件 C2/C5、Proposition 3；Supplementary Fig. 2 图注 (c) 现注明 ground-truth 网格独立注入背景与功能位移，故构造上 C_bf = 0。

## 批评 2：可识别分解——只写 log x = σ+β+φ 不足以唯一确定两部分

**批评原文：**「可识别分解：不能只给 log x = σ+β+φ，还要说明如何从观测中唯一确定两部分。」

**回复：**接受。写下因子模型只是命名了成分，并不能识别它们——观测位移只能识别和 β + φ。Note 20 新增「Identification (how β and φ are separated)」段，给出显式论证：**一条排除约束 + 三个测量**，构成有唯一解的线性系统。新文本摘录：

*“A1 (exclusion restriction): the functional factor vanishes on housekeeping genes, φ = 0 on the HK panel — HK genes are pre-specified for stable expression across conditions (Methods), so condition-driven regulatory change is excluded from that panel by construction. Under A1: (i) k_n on the HK panel identifies E_b (Proposition 3); (ii) split-half null pairs, on which E_f = 0 by construction, identify α = E_b(top-200)/E_b(HK) (C2); (iii) on an observed pair, k_f identifies E_f + 2C_bf + αE_b, and subtracting αk_n identifies E_f + 2C_bf — equal to E_f under C5. Three unknowns (E_b, α, E_f) meet three measurements in a linear system with a unique solution, so the decomposition is identified, not merely defined.”*

两条限制分工明确，读者可看清各自失效时损失什么：**无 A1**，任何校准都无法仅用 (k_f, k_n) 把 E_f 从 αE_b 中分离（这正是 HK 分母存在的理由——「What the HK denominator adds」段 (i) 已与此论证对齐改写）；**无 C5**，被识别的功能量为 E_f + 2C_bf，带 Cauchy–Schwarz 界。post-selection 限定（E_f 与 α 相对于数据选择的面板定义）在该段内重申，避免被误读为固定基因集结论。

**修改位置：** Supplementary Note 20 —— Proposition 3 后新增 Identification 段；「What the HK denominator adds」(i) 对齐改写；Scope 段注明 C5 属排除式假设、无法在观测对上单独实证。

## 批评 3：「近似公式的条件单调性」与「原始 JS 比值的严格单调性」未加区分

**批评原文：**「稿件把『近似公式的条件单调性』和『原始 JS 比值的严格单调性』写得不够区分，且现有推导不足以支持所写的严格增加结论。」

**回复：**接受，并指出这与批评 1 同源：交叉项存在时，φ → λφ 下 ω(λ) = α + (λ²E_f + 2λC_bf)/E_b，∂ω/∂λ = 2(λE_f + C_bf)/E_b 在 C_bf 充分负时可小于零——旧稿「strictly increasing, independently of α」确实越界。Proposition 4 重写为严格区分的三层：

**(a) 近似层（二次型）。** C5 下 ∂ω/∂λ > 0 对所有 λ > 0 成立，近似 estimand 严格单调增；无 C5 时当且仅当 λE_f + C_bf > 0 成立，由 Cauchy–Schwarz，λ²E_f > E_b（功能能量超过背景）时必有保证，弱功能信号叠加不利负协方差时可失效。「independently of α」已删除，并明写：交叉项随 λ（而非 λ²）缩放，故 C5 之外不存在 α 无关的单调性。

**(b) 原始 JS 层。** JS(p, q(λ)) 关于 λ 光滑；由 Lemma 2，其导数等于二次型导数加上阶为 O(Σ_i (|δ_i|/p_i)² |dδ_i/dλ|) 的余项导数，C1 成立处该余项小。因此原始比值在观测 λ 的**邻域内**继承导数符号（同一条件下的局部严格单调），不再仅凭展开式断言全局。

**(c) 全局层。** JS 有 1 bit 上界，全局单调不可能成立；所有结论限于 Lemma 2 诊断的操作区间，并保留 ground-truth 网格（零背景漂移下 Spearman ρ = 0.688；k_n 平坦 ρ = 0.004；纯漂移下降 ρ = −0.821）作为该区间内的实证确认。

正文同步对齐（同长置换，词数净零）：句子现作 *“increases monotonically with functional change under the stated conditions (Proposition 4; ground-truth ρ = 0.688)”*，其中「the stated conditions」即 Note 20 的 C1–C5。Scope 段扩充：凡引用 C5 的论断均携带显式最坏偏差 2√(E_f/E_b)。

**修改位置：** Supplementary Note 20 —— Proposition 4（三层重写）、Scope 段；正文 Proposition 4 引用句；Supplementary Fig. 2 图注 (c)。

## 验证

重写后全验证链复跑：build 226/226；MS 验证器 129/129；SI 验证器 120/120；CL+Guide 验证器 44/44；XV8 词额 64/64（MAIN 4,992/5,000、摘要 190/200、Methods 2,942/3,000）；pytest 29/29；fresh-DOCX 交叉核验 15/15（Lemma 1b、C5、Identification、三层 Proposition 4、「independently of α」与旧未加权能量定义的清除均在重生成 DOCX 中确认）。投稿包 CKI_Submission_NC.zip 22 条目 15,417,512 字节；commit 3a97c49 已推送并经远端核验。
