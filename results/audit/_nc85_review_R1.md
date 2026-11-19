**总分：4.8 / 10**
**建议：Reject**
**判定标签：一份自我审计与复现工程堪称范本、披露异常诚实的稿件，但核心指标的可辨识性依赖被自身数据否证的锚定假设，ground-truth 模拟与分子/分母划分对齐构成循环，且在主流 10x 平台退化为随机、检验 power 随样本量增大归零——方法的核心主张被其自身证据系统性否定，不宜按现稿送外审。**

> 审阅范围声明：本报告仅依据 `_nc85_review_materials/` 内的 `ms.txt`、`si.txt`、`cl.txt`、`guide.txt`、`tables_overview.txt`、`manifest.txt`、`round.txt` 形成判断，未读取任何往轮报告、专家汇总、主编核查、修复报告或记忆文件，未联网检索。引文均为材料内原文（英文），定位采用「文件:行号 / 章节名」，行号以本次提取的纯文本为准。

---

## 评分表

| 维度 | 分数 | 一句理由 |
|---|---|---|
| 新颖性 | 5.5 | Ka/Ks 启发式与 HK 分母 studentization 有一定概念新意，但作者自认是「recombines established ideas」的 heuristic index（`ms.txt:64`），核心运算仅为两块基因集上 JS 散度取比值。 |
| 理论严谨 | 4.5 | Note 20 给出 Lemma/Proposition/条件 C1–C6 的完整 scoped framework，形式化努力罕见地诚实；但可辨识性依赖 A1 与 C5 两个排除性假设，作者明言 C5「not separately verifiable on observed pairs」（`si.txt:271`），A1 被真实扰动否证，且 Prop 4 保证在主要应用场景普遍失效。 |
| 统计严谨 | 4.5 | 置换设计（block-shuffle、逐次重选基因、cluster-robust、wild-cluster、studentized bootstrap-t、配对 DeLong）属上乘；但 power 随 n 增大归零（非一致检验）、TCGA 3/5 癌种置换 P 不可解读、per-pair FDR 被重解释为「置换分辨率」、基线 CI 伪重复且 anti-conservative。 |
| 证据充分 | 4.0 | 数据规模与敏感性分析量极大，但模拟循环、10x 退化、真实扰动与全部竞品 head-to-head 中 ω 落后、核心结论面板不稳健、技术混杂未被移除，且主要验证落在静态细胞类型差异而非所声称的动态状态变化。 |
| 表达清晰 | 6.5 | 文本透明度极高、数字前后高度自洽、局限主动披露；但限定语（descriptive / indicative / upper bound / not a discovery set / group-level only）密度过高，且摘要、投稿信与正文的自我否定之间存在明显主张漂移。 |
| 影响力与 NC 适配度 | 4.0 | 「HK 锚在肿瘤与强扰动下会移动」是有价值且可检验的社区警示；但作为 NC 方法学 Article，指标在主流平台 chance-level、无分类增量、无预后价值、绝对 ω 不可迁移，增量贡献与普适性主张不足。 |

六维均值 4.83，因存在 P0 级阻断性问题（循环论证、主流平台失效、增量价值未确立）整体下调 0.03，取 **4.8**。

---

## 总体评价

稿件提出以管家基因（HK）面板上的 JS 散度作分母，将功能/identity 基因面板上的散度 studentize 为 ω = k_f/k_n，并借 Ka/Ks 类比主张可检测细胞状态变化；作者在五个大规模数据集上做了大量校准、竞品比较、理论形式化与复现工程，且几乎逐条主动披露了方法的边界。这种诚实值得明确肯定，也是本稿最强的一面。然而，作为方法学审稿人，我必须指出其证据结构存在三个无法靠补做若干实验弥合的缺陷：其一，ground-truth 模拟把「功能信号」注入非 HK 面板（k_f 的面板）、把「中性漂移」注入 HK 面板（k_n 的面板），再用 k_f/k_n 去区分二者——结论被写进了设计，作者本人亦承认这些优势「conditional on that assumption rather than evidence for it」（`si.txt:181`）；其二，在当前主流的浅测 10x 数据上 ω 的 AUC 为 0.51–0.53、对扰动强度无单调响应、δ=1 检出率 0.003–0.030，且置换检验 power 随每组细胞数增加单调下降至约 0，恰好与「atlas-scale」这一卖点相冲突；其三，在唯一有真实 ground truth 的扰动实验、MELD/scDist/DE/marker-Jaccard 对照以及作者自设的 k_f-only 对照中，ω 均不优于甚至劣于其自身分子 k_f 与已有方法，因而「比值相对直接报告 k_f、k_n 的增量价值」未被确立。作者随后把主张重定位为「precision-first」与「interpretability」，但这属于更换成功标准，且 `si.txt:151` 明确写下「Precision is not specificity」。综合判断：本稿更接近一份高质量的「阴性/警示性基准研究」，而非一个可推广的新指标；按现稿主张强度不宜送外审。

---

## 主要问题

### P0-1　模拟 ground truth 与指标分子/分母结构对齐，构成循环论证；作者已自认优势不构成证据
**位置与引文**
- `si.txt:173`（Supplementary Note 1, Ground-Truth Simulation）：「Functional signal: multiplicative shift of 2^delta (delta = 0.125-2) on a fixed module of 200 **non-HK genes** in group B. Neutral perturbations, injected separately: (i) 2^eta shift on **HK genes** in group A (eta = 0.25-1, neutral drift) ... Detection thresholds were the 95th percentile of 200 baseline replicates (**pure cell resampling**) per metric.
- `si.txt:181`（Adversarial circularity scenarios）：「The neutral-drift null above places the null perturbation on HK genes, which is **the same anchoring assumption that CKI itself makes**; the type-I and AUC advantages above are therefore **conditional on that assumption rather than evidence for it**.」以及「ω detected none of these signals (rate 0.000 at every delta, all seeds) ... CKI is thus structurally blind to functional signal located on the anchor genes - ... **the mirror image of its claimed advantage**.」；「its discrimination advantage holds **exactly when** functional signal lies off the anchor and drift on the anchor is neutral」。
- `si.txt:177`：「ROC AUC for separating functional (delta ≥ 0.25) from neutral ... ω 0.804 > k_f 0.716 > raw JS 0.640 ...」；`si.txt:174`：「Under pure HK drift ... ω 0.000, ... raw JS 0.553, cosine 0.580」。
- `ms.txt:14`：「'neutral' denotes variation on the constrained housekeeping panel (**operational, not mechanistic, neutrality**)」；`cl.txt:4`：「false-positive rate 0.00 versus 0.55–0.58 for JS and cosine」。

**为何是问题**：模拟中「功能性」被定义为「非 HK 基因上的变化」，「中性」被定义为「HK 基因上的变化」，而 ω 恰好是「非 HK 面板散度 ÷ HK 面板散度」。因此 AUC=0.804 与 FPR=0.000 衡量的是「指标能否识别它自己的面板划分」，属同义反复，而非检测细胞状态变化的能力。更关键的是阈值在「pure cell resampling（无扰动）」上校准，而测试扰动是 HK 上 2^η 的真实表达漂移——标准距离度量报告 0.55–0.58 是对真实漂移的**正确检出（真阳性）**，把它标为「false-positive rate」是概念误标；作者以「operational, not mechanistic neutrality」把「应被忽略的变化」先验地规定为中性，再奖励能忽略它的统计量，等于把结论写进标签。作者用 S1/S2/N1/N2 做了对抗性对照（值得肯定），但这些对照只是量化了优势成立的狭窄条件，并未提供与面板划分无关的独立 ground truth。此外 `si.txt:199` 亦自述：「the headline specificity (FPR 0.00 versus 0.55–0.58 ...) **could be a construction artifact**」。

**如何修**：引入与 HK/identity 划分无关的独立状态变化标签（已知的时序/谱系/多供体实验扰动，或全基因组随机注入后按独立标准标注），并在「功能信号部分落在锚上、漂移部分落在 identity 面板」的混合场景下重估 ROC 与校准；把「FPR 0.55–0.58」改称「对锚漂移的响应率/检出率」并说明其为真阳性；在独立 ground truth 建立之前，应把 AUC 0.80 / FPR 0.00 明确降级为「面板一致性检验」，不得作为方法优越性的核心证据（`cl.txt:3`、`ms.txt:10, 36` 均以此为主卖点）。

### P0-2　主流 10x 平台退化为随机水平且无剂量响应，检验 power 随样本量增大归零，与普适主张不相容
**位置与引文**
- `si.txt:142`（§3.11, 10x modular operating characteristic）：「The pooled AUC over all injected replicates (δ ≥ 0.25) against the split-half nulls is **0.507–0.534 for ω** ... detection at δ = 1.0 is **0.003–0.030 for ω**, 0.087–0.367 for raw k_total ... ω **straddles the null at 0.343–0.657 with no monotone trend in δ** ... On shallow 10x data at 50–200 cells per group the AUC advantage of ω reported for the two deep SmartSeq2 backgrounds (0.80 marrow, 0.91 skin) therefore **does not transfer (pooled 0.51–0.53)**」。
- `si.txt:137`（§3.11, Power formalization）：「Power at n = 50 cells per condition per donor is 0.67–0.93 ... **it declines as n grows** (n = 100: 0.47–0.76; n = 200: 0.17–0.55; n = 500: 0.09 ... pooled-donor designs at n ≥ 500: **≈ 0**), because the permutation null of ω explodes with pseudobulk size (k_n → 0 in the null while top-200 selection keeps k_f elevated)」。
- `si.txt:136`：「ω = k_f/k_n is **annihilated by its own denominator**」；`ms.txt:10`：「a background-specific precision advantage bought with sensitivity (**35–66% vs 97–100%** of injected 10x modules)」；`ms.txt:43`：「On 10x data the same module is detected in **97–100%** of paired replicates by raw JS but in **35–66%** by ω」。
- `ms.txt:75`：「offers an interpretable complement to standard distance metrics for **developmental biology, drug response and aging**」；`ms.txt:53`：「~3.3 million nuclei, 108 regions」；`ms.txt:31`：「108,136 cells」。

**为何是问题**：10x 是当前主流单细胞平台。在该平台上 AUC≈0.5、δ=1（2 倍表达变化）检出率 0.003–0.030、对 δ 无单调趋势，说明不是「灵敏度略低」而是近乎无检测能力。更根本的是 power 随每组细胞数单调下降并在大样本归零——这是一个非一致（inconsistent）检验，而稿件恰恰把「atlas-scale」（888,263 nuclei、108,136 cells、31,764 脑区对）作为主要应用场景与卖点；换言之，检验在其宣称适用的规模上失效。作者把此框定为「operating regime / boundary」（`si.txt:138`），披露充分且诚实，但**披露不等于解决**：摘要、结论与投稿信仍以「cell atlases」「developmental biology, drug response and aging」等普适口吻陈述（`ms.txt:10, 16, 75`），构成 claims–evidence mismatch。顺带一提，`si.txt:142` 亦承认 10x 上「raw k_total is the better detector」，而 k_total 只是全基因 JS 散度。

**如何修**：把适用范围严格收窄到已被数据支持的「深测序 SmartSeq2 + 50–200 cells/组」窗口，并在标题/摘要/结论中显式限定或删除普适性措辞；对 power 非一致性给出统计机理说明并在大图谱 pseudobulk 上提供可用的替代推断，或直接承认该指标不适用于 atlas-scale pseudobulk；`ms.txt:73` 的推荐（「at least ~100 cells per group」）与「power 随 n 崩塌」需一并重写，避免给出会把用户导向失效区的操作建议。

### P0-3　唯一真实扰动实验与全部竞品 head-to-head 中 ω 不优于其自身分子 k_f 及现有方法，增量价值未确立
**位置与引文**
- `si.txt:207`（Note 8, Kang IFN-β）：「AUC (perturbation versus donor-drift): **ω 0.551-0.922, k_f 0.743-1.000, raw JS 0.792-1.000** ... in CD14+ monocytes, where the k_n rise is largest (5.7-fold), **the ω AUC falls to 0.551 while k_f retains 0.984** ... **k_f-only with a design-matched null is the more honest statistic in that regime**」。
- `si.txt:138`（§3.11 Summary）：「CKI is **weaker than the competitors** at detecting broad mean-shift perturbations ..., at large-pseudobulk inference (power collapses for per-condition n ≳ 500), and at quantitative per-type ranking on near-ceiling real perturbations.」；`si.txt:136`：「MELD and the scDist approximation achieve **perfect detection at every configuration (sensitivity 1.00, AUC 1.000; per-type FPR 0.033 and 0.050)**, while CKI ω is ... **anti-monotonic at G = 500 (AUC 0.05–0.13)**」。
- `tables_overview.txt` Table 2(a) 第 29–31 行：`MELD | 0.033 | 1.000 ...`、`scDist (Python approximation) | 0.050 | 1.000 ...`、`CKI ω | **0.083** | 0.517 | 0.688 | 0.787 | 0.127 | 0.059 | 0.054`（即 ω 的 FPR/type 高于两个竞品，G500 下 AUC 坍塌）。
- `si.txt:158`（§3.13）：「ω **did not outperform DE**: AUC 0.661 (ω) versus 0.736 (DE) for KRAS versus WT ... **ω offers no classification increment over routine DE in this setting**」。
- `si.txt:270`（Note 20）：「**k_f-only is itself specific under the same drift (0.007–0.020), so false-positive rates alone do not separate ω from a k_f-only analysis**」。
- `tables_overview.txt` Table 3(a) 第 41–45 行：ω `0/30`、k_f `0/30`、k_n `1/30`、raw JS `11/30`、cosine `7/30`（最干净的 30 对技术重复上，k_f 单独已达成与 ω 相同的 FPR）；Table 4 第 54/58 行：ω T1 FPR `28.6%` 对 marker Jaccard `19.9%`，`si.txt:146` 亦承认「Marker Jaccard distance was **lower still** (T1 FPR 19.9%, below ω in 10 of 10 cell classes)」。
- `ms.txt:45`：「Because ω = k_f/k_n is a **deterministic function of the two rates, the ω and k_n contrasts are one finding**」；`ms.txt:15, 66`：「ω must be read alongside its components k_f and k_n」「We report both」。

**为何是问题**：这些是同任务、同数据、设计匹配的对照（相同 replicates、配对 DeLong、library-cluster-robust），结论高度一致：ω 在检测状态变化上不优于 k_f、MELD、scDist、常规 DE，甚至不优于最简单的 marker Jaccard；作者自己在 `si.txt:270` 承认 FPR 无法把 ω 与 k_f-only 区分开。由于 ω 是 k_f、k_n 的确定性函数，且稿件几乎所有实质发现都被归因于分母（「denominator-driven」「k_n-dominated」，`ms.txt:45, 55, 59`；`si.txt:196`），那么「比值相对直接并列报告 k_f 与 k_n 的增量价值」并未被实证确立。作者随后把成功标准改为「precision-first / interpretability / decomposition」（`cl.txt:4`、`ms.txt:65`），这是更换评价标准而非证明优势；`ms.txt:10` 甚至把「35–66% vs 97–100%」的低检出率表述为「precision advantage bought with sensitivity」，把劣势重新包装成设计取舍。另需注意 `tables_overview.txt` Table 2(a) 中 ω 的 FPR 0.083 高于 MELD/scDist，以及 Table 4 中 marker Jaccard 在 T1/T2 的 FPR 更低——这两处在主文「tightest precision among seven metrics」（`ms.txt:10`）与「lowest exceedance among continuous metrics」（`ms.txt:39`）的表述中被口径化地排除，应在主文一并披露。

**如何修**：设定一个预先注册、不由作者事后挑选的成功标准，在该标准上展示 ω 严格优于 k_f-only 与至少一种现有方法；若无法做到，应将论文重定位为「k_f/k_n 分解的诊断性 caution」而非「新指标优越性」。同时把 Table 2(a) 的 FPR 排序、Table 4 的 marker Jaccard 结果、以及 `si.txt:146/151/270` 的自认结论写入主文，而非仅留在补充材料。

### P1-4　precision / specificity / sensitivity 三层概念混淆，并被用于重构定位；「最紧 precision」被作者自证为基线尺度产物
**位置与引文**
- `cl.txt:4`：「CKI is a **precision-first index**, designed to detect dynamic cell-state changes rather than discriminate static cell types: on technical replicates it shows the **tightest precision**, not the lowest drift ... in the ground-truth simulation it **ranks first of six** at separating functional change from neutral drift (**AUC = 0.80**)」。
- `si.txt:151`（§3.12, Null-hypothesis-free drift gradient）：「**Precision is not specificity, and the two are not interchangeable**: ω also shows the largest T1→T2 rise in exceedance rate of any metric (**+62.3 percentage points**), so its comparatively low T1 value reflects **a lenient null on tightly matched replicates rather than immunity to biological drift** ... ω appears shallowest only when drift is expressed as a relative fold-change ... and that ordering is **set by ω's large baseline (median 8.86 against 0.0017–0.13 for the others) rather than by a smaller absolute displacement**; on the same ratio scale ω ranks **fourth of seven** ... **We therefore make no claim that ω has the shallowest drift gradient**.」；「Its null-free advantage is precision: on T1 pairs the log-scale dispersion of ω is 0.113 decades versus 0.267–0.586」。
- `si.txt:140`（§3.11, Covariance-whitened baselines）：「**Whitening reproduces the precision advantage of a ratio but not its specificity** ... Null dispersion ... falls from **0.213 (ω)** ... to **0.021 (mahal_diag)** ... **on precision alone the diagonal whitened baseline is the tightest of the eight statistics**」。
- `si.txt:175`（Note 1, Power）：「delta = 1: **ω 0.000 (all three module seeds)**, k_f 0.013, raw JS 0.993, cosine 0.667」；`si.txt:177`：「in this deep SmartSeq2 background ω is a **precision-biased screen**」；`ms.txt:36`：「**Rank discrimination and thresholded power diverge**」。

**为何是问题**：（i）术语层：投稿信把「tightest precision」（实为 log-scale MAD 0.113，即重复测量可靠性）与「AUC 0.80 ranks first of six」（判别/特异性）并列为同一「precision-first」定位的两大支柱，但补充材料明言二者不可互换；且 `si.txt:140` 证明对角白化基线的 MAD（0.021）比 ω（0.213）紧一个数量级，若单论 precision，ω 甚至不是最紧的。（ii）尺度层：`si.txt:151` 明确指出 ω 的「最紧」源于其基线中位数 8.86 远大于其他指标 0.0017–0.13，是 log 尺度分母效应，而非更小的绝对离散；在绝对尺度上 ω 排 4/7、在对数尺度上排 7/7。因此「tightest precision」是比值构造的数学副产物，不是方法优势。（iii）power 层：AUC 0.804 几乎完全由「不给中性漂移报警」驱动——δ=1（2 倍变化）时 ω 检出率为 0.000，即一个近乎从不报警的分类器可获得看似不错的 AUC；`ms.txt:36` 自认「rank discrimination and thresholded power diverge」，却仍把 AUC 0.80 作为 Fig. 2d 与投稿信的核心卖点。以「小方差 + 近零检出率」论证「更精确」，是 reliability、specificity、power 三者混淆的典型。

**如何修**：统一术语，明确区分 reliability（MAD）、specificity（对锚漂移不响应）、sensitivity/power（功能信号检出率）；摘要同时报告 AUC 0.80 与 δ=1 检出率 0.000 / 10x 0.51–0.53，避免 AUC 单独呈现造成「高判别力＝好用」的印象；补报固定特异性下的 sensitivity 与 PR-AUC；把「precision-first」改为可操作定义（如「以检测力为代价、对锚漂移不响应的保守比值」），删除「tightest precision」作为方法优势的表述。

### P1-5　验证任务与定位错配：主要证据来自静态细胞类型差异，而方法自称检测动态状态变化
**位置与引文**
- `si.txt:68`（§1.3）：「Parameter sweep (Phase 3.2) showed that the pure identity gene configuration ... achieved **optimal cell type discrimination (AUC = 0.786, n = 703 mouse cell-type pairs)**; this was therefore adopted as the default scheme (**a gene-set configuration criterion only; CKI itself is not designed for cell-type discrimination**—see the main-text Discussion)」。
- `ms.txt:74`（Limitations (i)）：「CKI detects **state changes within a given cell type, not cell-type identity**」；`cl.txt:4`：「designed to detect dynamic cell-state changes **rather than discriminate static cell types**」。
- `ms.txt:26, 28`：「703 pairs」「ω increased monotonically with biological distance ... **same cell type across organs ... different cell types within an organ ... cross-organ cross-type comparisons highest**」；`ms.txt:31`：「4,851 pairs across six organs」；`ms.txt:51`：「Of the 4,851 Tabula Sapiens pairs, **59 are same-cell-type cross-organ comparisons**」（即 98.8% 为跨细胞类型对）。
- `si.txt:206`（Note 8）：「Because all control cells sit in one lane and all stimulated cells in the other, **the condition effect is confounded with lane** ... the design does not separate condition from capture effects」。

**为何是问题**：篇幅最大的验证（Tabula Muris 703 对、Tabula Sapiens 4,851 对、脑图谱 31,764 对的层次/梯度/相关性/排序）几乎全是不同细胞类型或不同脑区之间的**静态**差异，恰是作者声明「不是为此设计」的任务；默认 k_f 面板甚至是按「cell type discrimination AUC」选出来的。真正符合定位的「同一细胞类型内的状态变化」证据只有 Kang IFN-β 与注入模拟，而前者 lane 与条件完全混杂、且 ω 输给 k_f（`si.txt:207`），后者循环且在 10x 退化（P0-1、P0-2）。以静态差异的漂亮单调层级支撑「检测动态 cell-state changes」的主张，属证据–主张错配；`ms.txt:28` 的「CKI measures functional divergence, not total difference」也因此在方法定位上缺乏对应验证。

**如何修**：把 Fig. 2 的跨细胞类型层级明确标注为「construct validation on static differences（内部一致性校验）」而非状态变化检测证据；补充 2–3 个独立的、同一细胞类型内的真实状态变化队列（多供体、条件与 lane 交叉设计、不混杂），在其上以预注册标准评估 ω 与 k_f、MELD；或把主张收窄为「跨群体表达散度分解」，不再特指状态变化。

### P1-6　指标可辨识性/可比性不足：estimand 依赖数据选择的面板，α 跨数据集漂移，理论保证在应用场景普遍不成立
**位置与引文**
- `ms.txt:14`：「ω = α + E_f/E_b + ε, where α is an operationally defined normalizing constant—the split-half null ratio, estimated once per dataset ... **α varies 1.65–2.2-fold across populations—its dominant error term**」；`ms.txt:29`：「ω_cal = ω_obs / 7.70 (**indicative, dataset-relative; one-significant-digit resolution**)」；`ms.txt:73`：「**absolute ω does not transfer**」；`si.txt:131`（§3.10）：「**ω_cal differences below ~0.1–0.2 are not meaningful**」。
- `si.txt:266`（Note 20, Proposition 3）：「an approximation **conditional on the post-selection panel (the pair-specific top-200 set is itself data-selected, so E_f and α are defined relative to that selection rather than to a fixed gene set)**」。
- `si.txt:267`（Identification）：「A1 ... **is not guaranteed by construction: IFN-β stimulation lowers ACTB and GAPDH by roughly 40% and raises k_n 1.2-5.7-fold** ... defining the anchor-visibility boundary of A1」；`si.txt:271`（Scope）：「**C5 ... is an exclusion-style assumption, not an approximation, and is not separately verifiable on observed pairs**」。
- `si.txt:264`（Lemma 2 diagnostic）：「on the pair-specific top-200 panel the error was ... **10–18% on observed pairs (90th percentile up to 103% in brain)**」；`ms.txt:24`：「the expansion is **quantitative at the k_n scale and approximate at the k_f scale**」。
- `ms.txt:61`：「Proposition 4, whose guarantee requires **ω > 2α = 19.46—failed by 30.3% of pairs and all 39 Strong candidates (ω < 15)**」。
- `si.txt:288`（§5.1, aggregation order）：「absolute values shift (**median fold 0.96, up to 9.8-fold per comparison**), and the split-control median baseline itself **moves from 6.46 to 10.94**」；`si.txt:190`（Note 4）：「**a residual differential of order 10% remains** at the null-versus-observed interface: absolute calibrated comparisons ... inherit it」。

**为何是问题**：一个「index」理应具备稳定、可跨研究比较的 estimand。此处 estimand 随每对数据的 top-200 选择而变、α 跨群体变动 1.65–2.2 倍且是主误差项、ω_cal 仅一位有效数字、不同聚合顺序造成最多 9.8 倍差异、绝对 ω 明确不可迁移、绝对值比较继承约 10% 残余偏差。理论可辨识性依赖 A1（真实扰动下被否证）与 C5（作者承认「不可在观测对上单独验证」），二阶展开在 k_f 尺度误差可达 103%，而 Proposition 4 的单调性保证被 30.3% 脑区对与全部 39 个 Strong candidates 违反——即理论框架在其被应用的主要场景内不提供保证。叠加 ω 是 k_f/k_n 的确定性函数（`ms.txt:45`）且作者反复要求「read ω alongside k_f and k_n」（`ms.txt:15, 66`），实际可复用对象退化为两个分量本身。作者把这些写进「scoped framework」并诚实标注，值得肯定，但结论是：该比值不构成一个定义良好、可迁移的指数。

**如何修**：给出与面板选择无关的 estimand（固定面板 + 显式偏差校正）并报告跨数据集可比性；用可验证条件替代 C5 或把其后果量化进每一条结论；把「ω 是 dataset-relative 诊断比值而非可迁移绝对指数」写入标题/摘要；对落在 C1/C5/ω>2α 失效区的结论在结果与图注中逐一标注。

### P1-7　HK 与功能基因面板选择敏感性：核心生物学结论不稳健，作者自认「not a robust finding」
**位置与引文**
- `si.txt:157`（§3.13, fixed-panel sensitivity）：「recomputing all 2,000 authoritative LUAD TT pairs with a pre-specified fixed functional panel ... **attenuated the KRAS − WT contrast to marginal significance (Δω_fixed +2.6, P = 0.089)** ... group means were **51.4 (WT), 48.4 (EGFR), 53.9 (KRAS)** under the fixed panel versus **123.5, 121.0, 137.2** under the circular scheme ... The KRAS elevation is therefore **dominated by pairwise selection rather than by driver biology** ... **so that contrast is not a robust finding**」；`ms.txt:46`：「but **not a fixed gene panel (Δω +2.6, P = 0.089)**」。
- `ms.txt:43`：「**circular selection inflated k_f by a median 1.61-fold, so absolute ω are upper bounds and the tier cutoffs (ω < 15/25/35) do not transfer**」；`ms.txt:61`：「The set is **estimator-sensitive (3 of 39 Strong survive a global-k_n switch)**」。
- `ms.txt:54` / `si.txt:254`（Note 18）：「under an alternative data-driven housekeeping panel of matched size (lowest-CV genes ... 10% overlap with HRT Atlas ...) **mean ω collapsed to ≈12 in both observed and null and the separation vanished (P = 0.95, 0.87, 0.76)** ... the superclass elevation is therefore **anchor-panel dependent**」；`si.txt:283`（Note 24）：「**DEF-CV collapses it** ... The astrocyte-versus-Bergmann gradient keeps its direction under EL (2.82-fold ...) and **collapses under DEF-CV (0.86-fold)**」。
- `si.txt:65–66`（Anchor-panel characterization）：「**none of seventeen classical reference genes** (ACTB, GAPDH, ...) **is a panel member**, so the anchor is not a list of textbook control genes」；「**Excluding the classical genes is deliberate rather than incidental**: in TCGA-LIHC both are higher in tumour than in adjacent normal ... so anchoring on them would **absorb part of the tumour-associated shift that k_n is meant to measure**」；「Used as the anchor panel, those four give a TT/NN k_n ratio of **1.30** ... against **2.10** for the 1,127-gene HRT panel ... and **2.04** for the seventeen-gene classical set」。

**为何是问题**：功能面板的 per-pair 循环选择使 k_f 中位膨胀 1.61 倍、绝对 ω 成为上界、tier 阈值不可迁移；换固定面板后 KRAS–WT 由显著变 P=0.089 且组均值缩小约 2.4 倍，作者直接判定「not a robust finding」——而该结论仍是 `cl.txt:3`、`ms.txt:46` 的第三支柱。HK 面板换为同属文献定义的 Eisenberg–Levanon 列表时结论保留，但换为同样合理的数据驱动 lowest-CV 面板时脑神经元 superclass 提升与星形胶质–Bergmann 梯度完全消失甚至反向（0.86 倍）；作者把「胜利」归为「literature constitutive-housekeeping lists」、把「失败」归为「anchor-TYPE dependence」（`si.txt:283`），但采用哪种 HK 定义是分析者自由度，这一事后分类不能消除选择性。尤其 `si.txt:65` 明确说明排除 17 个经典 HK 基因是「deliberate」，理由是它们会吸收肿瘤相关位移、削弱待测量的 k_n 差异——即以「是否得到预期结论」为标准构造面板；且不同 HK 面板给出的 TT/NN k_n 比从 1.30 到 2.10（1.6 倍跨度），与声称的「1.3–3.3-fold」效应量级相当，说明面板本身即可解释相当部分的效应大小。

**如何修**：预注册单一 HK 定义，并等价地报告全部候选面板结果，不做事后「文献/数据驱动」二分；把所有绝对值结论改为固定面板结果，或明确标注为 circular-scheme 上界；把 KRAS（P=0.089）与脑神经元 superclass（换面板后消失）的不稳健性写入摘要，而非仅置于补充材料；对 HK 面板的构建给出不依赖「是否保留预期效应」的独立理由。

### P1-8　单细胞技术混杂未被消除，仅被重新表述；跨队列处理效应可移动分母近 2 倍
**位置与引文**
- `si.txt:152`（§3.12, Diagnostics）：「the absolute ω FPR on T1 is **not zero, and it grows with group size: 14.1%** for pairs with at most 30 nuclei ... **48.0% above 500** ... a real library-level technical component (capture efficiency, depth) that grows detectable with power and that **the k_n denominator absorbs only partially**」；「in choroid plexus, two libraries of the same donor, region, and type **differ in k_f by up to 137-fold**」。
- `si.txt:149`（Library-effect stratification）：「replicates sharing an identifier give ω = **11.4%** ... versus **66.9%** across identifiers (χ² P = 2.4 × 10⁻¹⁵³) ... **because both strata are present in T1, no single pooled number describes the tier**」；`si.txt:150`：「the raw 28.6% is a **library-effect statistic, not anti-conservatism**」（library-aware null 下 4.8–5.5%）；`ms.txt:39`：「It is a **library-effect sensitivity statistic, not an error rate**」。
- `tables_overview.txt` Table 4 说明第 49 行：「The 200-per-class subsampling cap makes the cell-class composition of T2/T3 availability-dependent, so **cross-tier comparisons mix class composition with drift tier**」。
- `ms.txt:74`（Limitations (iii)）：「nor were **ambient RNA or doublets modelled**」；`ms.txt:49`：「This cross-cohort reference is descriptive only (**processing shifts k_n 1.8–2.3-fold**)」；`si.txt:142`：「doubling a module that carries 2–3% of counts **raises the library size** of group B, the housekeeping panel is diluted accordingly, k_n falls, and the ratio divides out the change」；`si.txt:206`：「condition and lane are confounded」。

**为何是问题**：作者做了非常细致的技术混杂诊断（值得肯定），但结论是混杂真实存在且分母只部分吸收：批次内 11.4% 对跨批次 66.9%、FPR 随 group size 从 14.1% 升至 48.0%、同供体同区同型两文库 k_f 可差 137 倍。处理方式是把 28.6% 重新定义为「library-effect sensitivity statistic, not an error rate」并用 library-aware null 得到 4.8%——即通过更换参照集使数值「校准」，而非移除混杂；`si.txt:151` 亦自认低 T1 值源于「a lenient null on tightly matched replicates」。更关键的是，GTEx 跨队列**处理流程**即可让 k_n 移动 1.8–2.3 倍，与 pan-cancer 声称的 1.3–3.3 倍同量级，直接威胁「reversal 反映肿瘤生物学」的归因；ambient RNA 与 doublets 明确未建模（对 snRNA-seq 脑图谱尤其相关）；Kang 真实扰动的条件与 lane 完全混杂。此外 T2/T3 分层比较本身混入了 class composition（`tables_overview.txt` Table 4 说明）。

**如何修**：在脑图谱上补 ambient RNA 去污（CellBender/SoupX 类）与 doublet 剔除的敏感性分析；在 pan-cancer 上用同一处理流程的配对队列复现 k_n 抬升，或把「processing shift 1.8–2.3-fold」作为效应量不确定性上界纳入结论；并列报告 T1 的 28.6% 与 library-aware 4.8% 并说明二者回答不同问题，避免「not an error rate」被读作混杂已解决；对 T2/T3 的跨层比较做 class-composition 匹配。

### P2-9　统计推断的若干具体弱点（多数作者已披露，但叠加削弱「calibrated end to end」表述）
**位置与引文**
- `ms.txt:84`：「The TCGA per-cancer test additionally holds the identity panel fixed (anti-conservative; the corresponding P > 0.9 values are uninformative at the aggregate level because **aggregate k_n sits at the denominator floor in 3 of 5 cancer types**, so they are tabulated but not interpreted, **the reversal claim resting on the pair-level cluster bootstrap**」。
- `ms.txt:112`：「the brain per-pair screen (m = 31,764 ... q < 0.05 is unattainable without ... B ≈ 6 × 10⁵ permutations). **The per-pair FDR outcome (minimum q = 0.520) is thus a statement about permutation resolution**」；`ms.txt:61`：「**no candidate survives global FDR correction, minimum q = 0.520**」。
- `ms.txt:27` / `si.txt:131`：「**slightly anti-conservative at six populations**」「intervals treating them as independent ... are **pseudo-replicated and anti-conservative**」；`si.txt:184`（Note 2）：「coverage **0.876 (7 clusters) and 0.873 (6 clusters)** for the percentile interval ... at nominal 95%」。
- `ms.txt:74`（Limitations (v)）：「the class-level upper-tail tests and the pair-level lower-tail screen were pre-specified as two independent families and are **reported without joint cross-family correction**」；`si.txt:196`：「The k_f-only controls are **post-hoc**; the P-values ... are **nominal and carry no multiplicity correction**」。
- `ms.txt:47` / `si.txt:277`（Note 22）：「an **unmeasured-reference upper bound**」「the normal reference is **assumed near zero, an assumption that dominates the estimate**」「per-cancer point estimates spanning 42% (KIRC) to **89% (LIHC)**」「**LIHC 89% [41, 193] ... CI exceeding 1**」；`ms.txt:46`：「**histological subtype remains unadjusted**」。

**为何是问题**：核心 pan-cancer 推断的置换 P 在 3/5 癌种不可解读、改由 cluster bootstrap 单独支撑；per-pair screen 无任何条目通过 FDR 却被解释为「置换分辨率」而非「未发现」；split-half 基线 CI 因伪重复 anti-conservative 且仅 6 个群体；小簇 bootstrap 覆盖不足；跨家族与 post-hoc 校正缺失；CNA 归属比例依赖「normal 参考近零」这一「dominates the estimate」的未测假设，且 LIHC CI 上限 193% 超出 100%。单项多属小修可补，但叠加后使 `ms.txt:16` 的「The index is calibrated end to end」显得过强。

**如何修**：对 reversal 给出不依赖 denominator floor 的推断；把「q = 0.520」明确写为「未发现」，删除「反映置换分辨率」的辩护性措辞或把 B 提到可判定水平；补齐跨家族与 post-hoc 校正；对 CNA 归属补充正常组织实测 CNA 的敏感性并显式报告 CI>1 的情形。

### P2-10　主张漂移与「降级语」过度堆叠，摘要/投稿信与正文自我否定不一致
**位置与引文**：`ms.txt:10`「a background-specific precision advantage bought with sensitivity」、`ms.txt:16`「a **group-level contrast only**」、`ms.txt:51`「should be read **descriptively**」、`ms.txt:61`「a prioritized hypothesis list, **not a discovery set**」、`ms.txt:62`「a **post-hoc, illustrative pattern only**」、`ms.txt:71`「**literature anchoring, not independent validation**」、`si.txt:274`（Note 21）「per-tumour ω is **not a pan-cancer prognostic marker**」、`si.txt:158`「ω offers **no classification increment**」；对照 `ms.txt:75`「offers an interpretable complement ... for **developmental biology, drug response and aging**」、`cl.txt:4`「**precision-first index**」「**ranks first of six**」、`ms.txt:1`（标题「...**in cell atlases**」）。

**为何是问题**：正文与补充材料几乎把每个具体生物学发现降级为 descriptive / indicative / upper bound / hypothesis-generating / not a discovery set，且明确无预后价值、无分类增量、literature anchoring 不算独立验证；但摘要、标题、结论与投稿信仍以「提供可解释的新指标」「用于发育/药物响应/衰老」「ranks first of six」等肯定口吻陈述。这种「正文自我否定、摘要维持主张」的张力使读者难以判断本稿究竟确立了什么，也模糊了可复用的方法学贡献；若按正文限定语严格表述，本文的可证伪结论所剩不多。

**如何修**：统一各级文本的主张强度；在摘要中显式列出适用边界（深测序 SmartSeq2、50–200 cells/组、仅同细胞类型内相对比较、绝对 ω 不可迁移、10x 与竞品上不占优、无分类/预后增量）；把「precision-first」替换为可操作定义；对每一条主结果标注其对应的限定语，避免读者只引用摘要而忽略正文的否定性说明。

---

## 优点

1. **披露与自我审计异常诚实，数字高度自洽。** 作者主动写下「the type-I and AUC advantages ... are conditional on that assumption rather than evidence for it」（`si.txt:181`）、「Precision is not specificity」（`si.txt:151`）、「does not transfer (pooled 0.51–0.53)」（`si.txt:142`）、「so that contrast is not a robust finding」（`si.txt:157`）、「We therefore make no claim that ω has the shallowest drift gradient」（`si.txt:151`）、「not a discovery set」（`ms.txt:61`）等自认结论；`cl.txt`、`ms.txt`、`si.txt`、`tables_overview.txt` 之间的关键数字（7.70、0.80、0.51–0.53、28.6%、4.8%、P=0.089、0.001/0.014/0.163、56% [46–66%]）逐一对得上，未发现内部矛盾。这在方法学稿件中相当罕见，应予肯定。

2. **竞品与消融对照覆盖广、多数为设计匹配的公平比较。** 同时对照了 MELD、scDist（Python 近似，并明确标注）、Mahalanobis（PC 全协方差与对角白化两种）、k_total、raw JS、cosine、Spearman、marker Jaccard、常规 DE 投影与 Augur，并在相同 replicates 上做配对 DeLong、Holm 校正、library 双端 cluster-robust 方差与四供体 wild-cluster bootstrap（`si.txt:139–140, 147–148, 179`；`tables_overview.txt` Table 2–4）。`si.txt:139–140` 关于「白化买到 precision、锚定买到对基线移动的不响应」的拆解是有价值的方法学洞见。

3. **统计工程与复现基础设施扎实。** design-matched permutation、逐次重选 identity 基因、block-shuffle 与 donor-stratified null、pseudo-region 负对照（`si.txt:227`）、小簇欠覆盖的 studentized bootstrap-t 修正（`si.txt:184`）、ratio-estimator 偏差分层（`si.txt:190`）、线性/softmax 双 caliber 复核（`si.txt:76`）；`guide.txt` 提供锁定环境、`requirements-lock.txt`、Dockerfile、脚本索引及「46 assertions」的 `spot_check.py`（`guide.txt:582`），开源 tag v0.6.4（`ms.txt:120`）。这部分可作为复现性实践的正面范例。

4. **实质贡献是一条真实、可检验且对社区有用的警示。** HK 锚在肿瘤与强扰动下本身会移动（TT k_n 1.3–3.3 倍、`ms.txt:45`；IFN-β 使 k_n 升 1.2–5.7 倍、`si.txt:207`；GTEx 处理流程使 k_n 移 1.8–2.3 倍、`ms.txt:49`），因此 HK 锚定归一化在 bulk 肿瘤/强扰动场景需谨慎——这一 caution 数据扎实、可被他人检验。`ms.txt:72` 的「anchor-credibility check」（若 k_n 落在其 design-matched null 尾部或追踪技术协变量，则改报 k_f）是一条真正可用的实践建议；`si.txt:261–271` 的 scoped framework 也是罕见地诚实的形式化尝试。

---

## 给编辑的备注

**是否可送外审：不建议按现稿送外审。** 障碍不在数据规模或复现，而在三处结构性问题：（a）核心 ground-truth 模拟把「功能信号」与「中性漂移」分别注入 k_f、k_n 的面板，使 AUC/FPR 证据不可解释为方法优越性（作者亦自认），属证据设计的循环；（b）主流 10x 平台 AUC 0.51–0.53、无剂量响应、δ=1 检出率 0.003–0.030，且检验 power 随样本量增大归零，而标题/摘要以「cell atlases」「drug response and aging」等普适口吻主张，构成 claims–evidence mismatch；（c）在唯一真实扰动与全部竞品对照中 ω 不优于 k_f / MELD / scDist / DE / marker Jaccard，增量价值未被确立，作者随后改用「precision-first」重定位成功标准。这三点需重做 estimand 定义、重建独立 ground truth、并在新平台/设计上重建证据，实质等同新稿件，非「补充若干实验」可解。另请注意本稿已带大量修订痕迹（`manifest.txt:4`、「v0.6.4 | nc84 round: expert-panel P0/P1/P2 fixes」；`guide.txt:218`「Added caveats ...」），说明上述限制是内生的而非遗漏。

**有无技术性退回风险：有，且建议在送审前先要求作者做一次 claims audit。** 具体风险点：
- **术语误标**：`cl.txt:4` 把标准度量对真实 HK 漂移的检出（0.55–0.58）称为「false-positive rate」，而阈值是在无扰动 baseline 上校准的（`si.txt:173`）；同一句又把 MAD（reliability）与 ROC-AUC（discrimination）混作「precision-first」的两大支柱，与 `si.txt:151`「Precision is not specificity」直接冲突。
- **选择性呈现**：`ms.txt:10`「tightest precision among seven metrics」与 `ms.txt:39`「lowest exceedance among continuous metrics」通过口径限定排除了 `tables_overview.txt` Table 2(a) 中 ω 的 FPR 0.083 高于 MELD 0.033 / scDist 0.050、以及 Table 4 中 marker Jaccard T1 FPR 19.9% 低于 ω 28.6% 这两处不利结果（补充材料已披露，主文未披露）。
- **核心发现不稳健却仍作卖点**：LUAD KRAS 在固定面板下 P=0.089、作者自判「not a robust finding」（`si.txt:157`），脑神经元 superclass 提升在替代 HK 面板下消失（P=0.95/0.87/0.76，`si.txt:254`），但二者仍是 `cl.txt:3` 的支柱；per-pair circular selection 使绝对 ω 成为上界、tier 阈值不可迁移（`ms.txt:43`），却仍以 ω 排名与梯度作为主要结果图表。
- **推断基础被削弱**：`ms.txt:84` 承认 3/5 癌种置换 P 因分母触底而不可解读、reversal 改由 cluster bootstrap 支撑；`ms.txt:112` 把 min q=0.520 解释为「置换分辨率」。

**建设性建议**：本稿最有价值的内核是「HK 锚在肿瘤与强扰动下会移动」这一警示，加上一套高质量的中性漂移/技术重复基准与 k_f/k_n 分解诊断。建议明确鼓励作者把它改写为范围收窄的 Benchmark / Resources 型短文（标题不再宣称新指标或 atlas 普适性，主张限定为「HK 锚定归一化的失效边界与诊断流程」），并保留全部对照与复现材料；这类贡献数据扎实、结论可检验、对单细胞与 bulk 社区都有实用价值。反之，若维持「提出可推广的 CKI 指标」这一 Article 定位，我建议拒稿。

**与其他审稿分工的边界**：本报告仅从方法学与基准测试角度立论，未对 TCGA 临床/癌症生物学解释的领域正确性、以及生存分析与 CNA 归属的流行病学合理性作独立判断，建议由相应专长的审稿人覆盖。

---

*R1（单细胞方法学与基准测试）· nc85 盲审 · 依据 `_nc85_review_materials/` 材料包独立成文*
