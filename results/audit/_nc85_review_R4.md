**总分：5.5 / 10**
**建议：Major Revision**
**判定标签：<Ka/Ks 类比的边界限定堪称模范，但 scoped framework 的 identification 前提在核心实证中被自认违反、estimand 从未被估计，studentization 与单调性保证又被主文夸大——理论更接近事后诠释而非方法学支柱。>**

# R4 独立盲审报告（分子演化 / Ka-Ks 选择压力分析视角）

> 盲审范围声明：本报告仅依据 `_nc85_review_materials/` 下的 `ms.txt`、`si.txt`、`cl.txt`、`guide.txt`、`tables_overview.txt`、`manifest.txt`、`round.txt` 撰写。未读取任何往轮审稿报告、专家团汇总、事实核查或修复报告，未读取其他审稿人报告，未联网检索作者身份，未读取记忆文件，未读取 `results/` 下任何 CSV 数值产物（本报告所引数字全部来自材料包内文字，并已在包内交叉核对）。

---

## 1. 评分表

| 维度 | 分数 | 理由（摘要） |
|---|---|---|
| 新颖性 | 6.0 | 把 dN/dS 的「内部中性基线」逻辑映射为 HK 面板分母、并补出 McDonald–Kreitman 式四象限，有概念新意；但方法本体 `ω = k_f/k_n` 简单，作者自认「recombines established ideas」（ms.txt:L64），且大半结论是分母驱动的描述性发现，新意主要落在诠释而非新统计量。 |
| 理论严谨 | 4.5 | Lemma 1/1b/2 数学表述准确、remainder 与 Cauchy–Schwarz 界写法规范、Scope 段显式区分「exact mathematics」与「model-relative conditional」；但存在 α 三重符号重载、C6 段与 Identification 段对 α「是否可识别」自相矛盾、`ω > 2α` 与 `λ²E_f > αE_b` 的 `i.e.` 等价性只在所需场合之外成立、ε 未定量且主项与信号同阶、identification 前提 A1 被自认失效等硬伤。 |
| 统计严谨 | 5.0 | 仅从理论—统计交界评（细节应由 R2 详评）：delta-method 预测 bias <0.8% 与实测 ~10% 差一个数量级；α 既是「每数据集一次的常数」又是 ε 的 dominant term；ε 靠置换 null 吸收而非理论控制；`ω_cal` 仅一位有效数字、绝对 ω 不 transfer。 |
| 证据充分 | 5.0 | 就「理论—实证对应」而言偏弱：ground-truth grid 只覆盖 `C_bf = 0`（C5 分支），estimand `E_f/E_b` 从未被估计或检验，单调性保证在 30.3% 的脑区 pairs 与全部 39 个 Strong candidates 上不成立且被作者主动弃用；但全稿负结果与边界披露极充分，抵消一部分扣分。 |
| 表达清晰 | 6.0 | SI 的 Roadmap、条件编号（C1–C6、A1）、三层单调性分离都清晰；扣分来自 α 符号重载、`precision not specificity` 与小节标题「specificity versus sensitivity」自相矛盾、`studentized / t-statistic / studentizes the null eightfold` 措辞在主文/摘要/cl 与 SI 之间强度不一。 |
| 影响力与 NC 适配度 | 5.0 | precision-first 的校准指标、泛癌 `k_n` 反转这一 HK-anchor caution、脑图谱描述性目录有实用价值；但理论贡献不足以支撑 NC 的 methods Article，且定位在「检验 / 精度指标 / 描述性比值」之间摇摆。 |

---

## 2. 总体评价

以分子演化审稿人的标准看，这份稿件最难得之处是它对 Ka/Ks 类比的诚实限定：SI Section 1.4 明确写下「structurally similar but mathematically non-equivalent」，逐条列出与密码子模型的差异，并主动指出 HK 锚点其实是「最强约束类」而非中性标准——恰是 dN/dS 失去解释力的情形——且把 TCGA 的分母漂移认作该失效模式的实证表现，全文从未把 `ω > 1` 说成正选择证据。然而，Supplementary Note 20 的 scoped framework 更接近事后补上的诠释脚手架：它声称「identified, not merely defined」，但识别所依赖的排除限制 A1 恰在文章两个最重要的实证场景被作者自认失效，被识别的 `E_f/E_b` 在全稿没有任何估计值，唯一数值预测与实测相差一个数量级，单调性保证在核心数据集上被主动弃用。更需修的是主文、摘要与 cover letter 把这一框架的修辞强度整体抬高了——一个 proxy 分母带来的跨类离散压缩被写成「studentizes the statistic / the logic of a t-statistic」，而 `ω = k_f/k_n` 的定义性后果被当作「eightfold」实证优势反复宣传。理论与实证的对应因此被系统性夸大，尽管作者在 SI 内部其实已经诚实地作了一切必要的降级。这些缺陷主要靠重写与补证即可修正，故建议 Major Revision 而非拒稿。

---

## 3. 主要问题

> 分级说明：本审稿**不设 P0**——材料内无数据造假迹象；作者亦主动承认「ω 与 k_n 的对比是同一个发现」（见优点 3），并未把数学恒等式谎称为独立实证发现。下列 P1 各项若不修订，对「以理论框架为方法学支柱」这一投稿定位即为阻断性。

### P1-1　identification 前提与核心实证场景互斥，且被识别的 estimand 从未被估计
- **位置与引文**：`si.txt` Supplementary Note 20「Identification」段（L267）：「A1 (exclusion restriction): the functional factor vanishes on housekeeping genes… **A1 is not guaranteed by construction: IFN-β stimulation lowers ACTB and GAPDH by roughly 40% and raises k_n 1.2-5.7-fold** (Supplementary Note 8), defining the anchor-visibility boundary of A1」；同段结尾「Three unknowns (E_b, α, E_f) meet three measurements in a linear system with a unique solution within the scoped approximation, **so the decomposition is identified, not merely defined**」；`ms.txt`:L15「in disease or strong-perturbation contexts the anchor itself shifts (TCGA and IFN-β below)」；`ms.txt`:L43「ω collapsed to 0.05–0.13 on broad 500-gene shifts, where the anchor responds」；`ms.txt`:L74「ω is structurally insensitive to perturbations that move the anchor itself」。
- **问题**：识别结论唯一依赖 A1（φ 在 HK 面板为零）。而 A1 恰在 IFN-β 扰动与 TCGA 泛癌反转——本稿两个最重要的实证场景——被作者自己判定为失效。于是「identified」只在锚点未移动时成立，而「锚点移动」正是文章的核心发现；理论保证的适用范围与实证卖点的适用范围恰好互补。更实质的是：全稿报告的量只有 ω、k_f、k_n、ω_cal，`E_f`、`E_b`、`C_bf`、`E_f/E_b` 没有任何一个被估计、被给出区间、或与任何生物学结论对照。一个从未被计算的量被宣称「identifiable」，其对实证推断的贡献无法核验。
- **修法**：把「identified, not merely defined」降级为「identifiable under A1 within the scoped approximation；而 A1 在强扰动与肿瘤场景失效，故这些场景仅报告 ω/k_f/k_n 的描述性对比」；并至少在一组数据上给出 `E_b`、`E_f`、`C_bf` 的估计及其对 ω 的贡献分解（含 C5 失效时 `2C_bf/E_b` 的量级），否则删除 Identification 小节的形式化措辞、仅保留为诠释。

### P1-2　α 是否「可识别」在两处自相矛盾，且 α 在本稿承载三个正交含义
- **位置与引文**：`si.txt`:L265（Conditions, C6）「**the null ratio alone does not identify a conversion factor without C6**」；`si.txt`:L267（Identification, (ii)）「split-half null pairs, on which E_f = 0 by construction, **identify α = E_b(top-200)/E_b(HK) (C2)**」；`si.txt`:L70（Section 1.4）「ω_cal = ω/7.70 parallels the reciprocal of the neutrality index (**the α-direction of the McDonald–Kreitman contrast**)」；`guide.txt`:L601 参数表「**k_n scaling (alpha) | 1.0 | all analyses**」。另 `ms.txt`:L14 称 α 为「an operationally defined normalizing constant」且「α varies 1.65–2.2-fold across populations—its dominant error term」，`ms.txt`:L24 称「α the split-half selection constant」，`ms.txt`:L188 称「α the identity-panel selection inflation」。
- **问题**：一处明说 null ratio「does not identify」，另一处明说 null pairs「identify α」；Identification 段只列「one exclusion restriction (A1) and three measurements」，未把 C6 列为识别的必要前提，与 C6 段的自我限定不一致。更严重的是符号卫生：α 在本包内同时指 (a) split-half null ratio / 面板转换因子（7.67–9.73，`si.txt`:L265）、(b) 代码里恒为 1.0 的 `k_n scaling` 参数、(c) MK 检验中「由正选择驱动的氨基酸替换比例」这一完全不同的群体遗传量。在 Ka/Ks 与 MK 语境里把 (a) 与 (c) 并列于同一「scoped correspondence」段落，恰恰制造了作者反复声明要避免的「同源」错觉；而 (b) 会让复现者误以为理论框架的 α 是固定常数。
- **修法**：三个量改用不同符号（例如 CKI 的 `a`、代码 scaling `s`、MK 的 `α_MK`），并在首次出现处给出符号表；把 Identification 段「(ii) identify α」改写为「under C6, the null ratio is consistent with α」，与 C6 段措辞对齐，并在 identification 的前提清单中显式补入 C6。

### P1-3　Proposition 4 单调性保证的适用范围与主文陈述错位，且核心数据上被主动弃用
- **位置与引文**：`ms.txt`:L24「increases monotonically along the functional-change ray (Proposition 4; ground-truth ρ = 0.688; **guaranteed only for ω > 2α, i.e. λ²E_f > αE_b**)」；`ms.txt`:L61「The screen rests on the multiplicative residual model, **not Proposition 4, whose guarantee requires ω > 2α = 19.46—failed by 30.3% of pairs and all 39 Strong candidates (ω < 15)**」；`si.txt`:L268（Proposition 4 (a)）「**Under C5 this is strictly positive for all λ > 0**… without C5 … by Cauchy–Schwarz it is **guaranteed once λ²E_f > αE_b**」；同段「Ground-truth check (factorial grid of Supplementary Note 1, **constructed with C_bf = 0 and therefore covering the C5 branch only**)」；`si.txt`:L271（Scope）「C5 … is an exclusion-style assumption … **not separately verifiable on observed pairs**」。
- **问题**：三处错位。其一，`ω > 2α` 与 `λ²E_f > αE_b` 的 `i.e.` 等价仅在 `C_bf = 0`（C5）时成立，而 C5 下 Proposition 4 (a) 已声明对所有 λ>0 严格单调、根本无需该门槛；在真正需要保证的无 C5 场合（含负协方差）二者并不等价——「需要该条件的场合不等价，等价的场合不需要该条件」。其二，唯一被实证检验的 ground-truth grid 明确「covering the C5 branch only」，即恰好只检验了理论上无需检验的平凡分支，C5 失效时的 `2√(αE_f/E_b)` 最坏情形界从未被数据触及。其三，主文 L61 主动承认脑区 screen（30.3% 的 pairs、全部 39 个 Strong candidates）不满足条件并弃用 Proposition 4——诚实的降级，但也等于宣告该理论保证在实证主体上不落地。
- **修法**：删除「guaranteed only for ω > 2α, i.e. λ²E_f > αE_b」的等价写法，改为分别陈述「C5 分支：对 λ>0 无条件严格单调」与「无 C5 分支：充分条件 λ²E_f > αE_b + Cauchy–Schwarz 界 `2√(αE_f/E_b)`」；补充 `C_bf ≠ 0`（含对抗性负协方差）的模拟网格以覆盖失效边界，或把单调性结论明确限定在 C5 分支并相应收敛主文措辞。

### P1-4　「studentization / identifies / eightfold」的修辞强度超过框架实际被使用的程度，比值定义性后果被包装成实证优势
- **位置与引文**：`cl.txt`:L4「A scoped framework gives ω = α + E_f/E_b + ε; **the HK denominator studentizes the null eightfold** (Supplementary Note 20)」；`ms.txt`:L10「**ω studentizes divergence** (brain null CV 1.20 → 0.146)」；`ms.txt`:L14「**ω is a studentized statistic** with a scoped estimand」；`ms.txt`:L65「k_f alone cannot separate functional from background energy; **dividing by k_n studentizes the statistic, collapsing the median cross-class null CV up to eightfold (brain 1.20 to 0.146; mouse only 1.7-fold)—cross-class level normalization, the logic of a t-statistic**」；`si.txt`:L270（Note 20 (ii)，较谨慎）「dividing by k_n yields a statistic whose null is **approximately ancillary** to it—**the same logic by which** dividing by the sample standard deviation turns a mean difference into a t-statistic」；`si.txt`:L267「k_f alone estimates the sum … the HK panel supplies that measurement (A1), **making E_f/E_b identifiable under C5**」。
- **问题**：`k_n` 是 HK 面板上的 JS 散度，不是 `k_f` 的标准误估计；ω 的分布也非 pivotal——作者自认 α 是 dataset-relative、`ω_cal` 只一位有效数字（`guide.txt`:L205）、绝对 ω 不 transfer（`ms.txt`:L74）。Note 20 (ii) 给出的证据是「class-level split-half null median 的跨类 CV 从 1.21 降到 0.148」，这是**跨类离散度**的压缩，不是 per-pair 抽样分布被 studentize；「brain 1.20→0.146, mouse only 1.7-fold」本身说明效应是数据集特异的，把最强的「up to eightfold」写进摘要与 cover letter 有选择性呈现之嫌。更重要的是，除以一个与分子相关、且自身也跨类变化的量，其压缩跨类离散本就是 `ω = k_f/k_n` 的算术后果——作者自己在 `ms.txt`:L65 也用「permuting k_n … predicts Spearman 0.524, against an observed 0.089」说明这一点。把它升格为「studentizes the statistic / the logic of a t-statistic」，是把恒等式后果当作独立统计性质与实证发现。同理，「making E_f/E_b identifiable」却又从未报告该量，使「identifiability」成为未被使用的宣称。
- **修法**：主文/摘要/cover letter 统一改用 `si.txt`:L270 的谨慎措辞（「跨类 null 离散压缩，幅度数据集特异」），删去「studentizes / t-statistic / eightfold」的形式化表述；若坚持 studentization 类比，需给出 ω 相对其标准误的正式关系或（近似）pivotal 性论证。同时把「identifiability」的宣称与 `E_f/E_b` 的实际报告绑定，否则降为诠释性说明。

### P2-1　ε 项从未定量，其主项与「信号项」同阶，且理论预测与实测相差一个数量级
- **位置与引文**：`ms.txt`:L14「ε a remainder」；`si.txt`:L266（Proposition 3）「**|ε| bounded by the Lemma-2 remainders, the C4 sampling term, and the pair-to-pair spread of α (C2)—the dominant term, which is exactly why absolute ω is dataset-relative**」；`si.txt`:L264（Lemma 2）「on the pair-specific top-200 panel the error was 1.1–2.1% under nulls but **10–18% on observed pairs (90th percentile up to 103% in brain)**」；`ms.txt`:L24「a **delta-method-predicted calibration bias (< 0.8%)**, while the measured ratio bias … spans **−8.3% to +6.5%** … **a residual of roughly 10% that the empirical calibration absorbs only under design-matched permutation**」；`si.txt`:L269「the two aggregations **bracket the same small effect**」；`si.txt`:L271（Scope）「Where a condition holds only approximately (C1 at the k_f scale; C2 as a stable-but-variable α), the corresponding statements are approximations」。
- **问题**：ε 在全稿没有数值、没有分布、没有与 `E_f/E_b` 的量级对比，只被定性列为三项来源。但 `E_f` 定义在 top-200 面板（k_f 尺度），而该尺度 Lemma-2 二次展开误差达 10–18%（90 分位 103%）——即 ε 完全可能与「信号项」`E_f/E_b` 同阶，`ω = α + E_f/E_b + ε` 在功能尺度上并不构成「信号 + 小残差」的可控分解。此外 α 既被 C2 定义为「estimated once per dataset」的加性常数，又被指为 ε 的 dominant term（逐对波动），二者角色张力未澄清。delta-method 预测 <0.8% 与实测 ~10%（null 处 −8.3%）差一个数量级，「bracket the same small effect」不足以弥合。若 ε 只能「靠设计匹配的置换 null 吸收」，则理论框架相对置换推断并未提供可独立检验的增量。
- **修法**：给出 ε 各分量的经验量级（尤其 α 的 pair-to-pair spread 与 Lemma-2 remainder 相对 `E_f/E_b` 的比值），明确写「在 k_f 尺度 ε 不可忽略，故该式仅作定性诠释」；澄清 α 作为常数与作为误差源的双重记账；调和或撤回 <0.8% 的预测性表述，并说明「经验校准吸收」为何不使理论预测失去可证伪性。

### P2-2　「选择」语汇残留与「precision not specificity」定位的双重摇摆
- **位置与引文**：`cl.txt`:L4「CKI is a **precision-first** index … it shows the tightest **precision, not the lowest drift**」；`cl.txt`:L3「ω alone **did not false-trigger on neutral housekeeping drift (false-positive rate 0.00 versus 0.55–0.58 for JS and cosine)** and gave the **best functional-versus-neutral discrimination** at bounded power (AUC = 0.80…)」；`ms.txt`:L34 小节标题「Ground-truth simulation: **specificity versus sensitivity**」；`ms.txt`:L40「**neutral-drift immunity** transfers as a relative-calibration advantage」；`ms.txt`:L64「The key assumption—**HK genes under stabilizing selection**—lacks Ka/Ks's mathematical cancellation, so CKI is a heuristic index, not a formal selection measure」；`ms.txt`:L67「never as evidence of positive selection」；`ms.txt`:L72「a significant ω rejects label exchangeability」。
- **问题**：定位句声称「precision not specificity」，但四支柱之一与正文小节标题恰恰以 FPR 0.00、AUC 0.80、「neutral-drift immunity」为卖点——这些是 specificity / 判别力主张，不是 precision（技术重复离散度）。二者被同时当作优势却又在 meta 层互相让渡，读者无法判断 ω 究竟是不是一个「检验」。从本专长看，这种摇摆与 Ka/Ks 类比的核心承诺（能区分功能变化与中性漂移）以及「never as evidence of positive selection」的否定并列，尤其容易造成误读；而「stabilizing selection」把群体遗传学术语移植到管家基因的表达约束（其机制是功能约束，不是群体内的稳定化选择），是残留的演化语汇。还需注意：ω 的低 FPR 主要源于「对锚点内漂移结构性失明」（`ms.txt`:L35「ω is structurally blind to modules on HK genes」、`ms.txt`:L74），属构造性盲区而非判别能力，用「specificity」名之并不准确。
- **修法**：统一术语表——明确 precision = 技术重复离散、specificity = 中性漂移不误报，两者分别报告、不互相让渡；把「stabilizing selection」改为「expression-constrained / 稳定表达约束」等非演化措辞；在摘要与定位句明确 ω 在置换下「rejects label exchangeability」（`ms.txt`:L72 已有此说）而非给出选择检验，并说明低 FPR 来自锚点结构性盲区。

---

## 4. 优点

1. **Ka/Ks 类比的边界限定达到分子演化审稿人期望的水准**。`si.txt`:L70 明写「The Ka/Ks analogy is structurally similar but **mathematically non-equivalent**」，列出四条 Key differences（密码子模型 vs 连续表达向量、中性的机制基础 vs 经验定义、PAML vs 置换推断、全部非同义位点 vs top-200 的「**an ascertainment asymmetry on the Ka side**」）；更关键的是主动指出「in Ka/Ks the denominator (Ks) is a putatively neutral standard, whereas **the HK anchor is itself the most strongly constrained expression class—as if synonymous sites were selected along one lineage, where dN/dS loses its interpretation**」，并把 TCGA 泛癌反转认作这一失效模式的实证表现。作者没有把 `ω > 1` 当作正选择，`ms.txt`:L67「never as evidence of positive selection」与 `ms.txt`:L188「invoked here as a heuristic analogy only, not a formal population-genetic claim」前后一致。这是本稿最值得保留的部分。

2. **主动降级与负结果披露极为充分**。`si.txt`:L70「ω = 1 is the expectation under a full-matching null (k_f = k_n), **not a theorem**」；`ms.txt`:L61 承认 30.3% pairs 与全部 39 个 Strong candidates 不满足 Proposition 4 条件因而弃用该保证；`ms.txt`:L46 固定面板 KRAS `P = 0.089`、EGFR 在纯度调整后消失；`ms.txt`:L61 脑区 screen「no candidate survives global FDR correction, minimum q = 0.520」；`ms.txt`:L47 生存分析零结果；`guide.txt`:L205 坦承 `ω_cal` 只约一位有效数字。这种自我设限在当前投稿中属上乘。

3. **没有把数学恒等式的后果伪装成独立生物学发现**。`ms.txt`:L45 主动写明「Because **ω = k_f/k_n is a deterministic function of the two rates, the ω and k_n contrasts are one finding**」，并把泛癌反转定性为「a more stable housekeeping baseline among adjacent non-tumor specimens, **not smaller functional-gene divergence of tumor cells**」；`si.txt`:L270 亦称「the TCGA reversal is a k_n phenomenon invisible to any k_f-only analysis」。作者未把「肿瘤散度更低」包装成「选择放松 / 功能演化」之类，规避了本类类比最易犯的错误。

4. **理论框架的条件化管理方式规范**。C1–C6、A1 逐条编号并标注「verified / approximate / exclusion-style」，Lemma 2 写出显式 Lagrange remainder，Proposition 3 给出 C5 失效时的 `2√(αE_f/E_b)` 最坏情形界，`si.txt`:L271 Scope 段明确「Lemma 1 is exact … Lemma 2 is exact mathematics with an explicit remainder; Propositions 3–5 are model-relative and conditional on C1–C5」并承认 C5「is not separately verifiable on observed pairs」。即便我对其宣称强度有批评，其写作形式本身是专业、可核查的。

---

## 5. 给编辑的备注

- **理论部分是否足以支撑投稿：不足以独立支撑，但可作为限定性诠释保留**。Supplementary Note 20 是 post-hoc 补上的框架：其唯一数值预测（delta-method bias <0.8%，`ms.txt`:L24 / `si.txt`:L269）与实测（~10%）相差一个数量级；识别前提 A1 在 IFN-β 与 TCGA 两个核心场景被作者自认失效（P1-1）；被识别的 estimand `E_f/E_b` 全稿从未估计；单调性保证在 30.3% 的脑区 pairs 上不成立且被主动弃用（P1-3）；`si.txt`:L268 的 ground-truth 验证又只覆盖 `C_bf = 0` 的平凡分支。它更适合放在 Discussion / SI 作为「对已定义比值的 scoped 诠释」，而不是作为 NC methods Article 的方法学创新支柱。若作者坚持以该框架为卖点，则 P1-1 至 P1-4 为阻断性，须按其修法逐条落实（尤其补 `E_b/E_f/C_bf` 的实测分解与 `C_bf ≠ 0` 的失效边界检验）。
- **是否可送外审：可以，但建议附带指定复核人**。实证部分（技术重复的 precision/calibration、泛癌 `k_n` 反转这一 HK-anchor caution、脑图谱的描述性目录）有独立价值，且作者诚实度高、可复现性材料（Reproducibility Guide、spot-check 断言）齐全，因此不建议直接拒稿；建议 **Major Revision**，核心要求是：把 Note 20 的强断言（identified / studentizes / identifiability / 单调性）统一降级为 `si.txt`:L270–L271 已有的 scoped 措辞、统一 α 符号、定量 ε、补齐 C5 与 A1 失效场景的检验、校正「precision not specificity」与 studentization 措辞。外审名单中建议至少指定一位兼具理论统计与群体遗传/分子演化背景的审稿人专门复核 Supplementary Note 20（本报告即承担该角色）；若作者不愿降级理论宣称，应重新评估其是否达到 NC 的方法学门槛。
