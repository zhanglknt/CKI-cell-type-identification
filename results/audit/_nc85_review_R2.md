**总分：6.5 / 10**
**建议：Major Revision**
**判定标签：统计披露近乎范本级，但核心推断仍锚定在与被检验假设同构的模拟和「未测量的正常参考」之上，且区间聚类层级与有效独立单位不一致——需收紧推断边界后再议。**

# 独立审稿意见 R2（统计推断）

> 审查范围声明：仅依据 `_nc85_review_materials/` 内 `ms.txt`、`si.txt`、`cl.txt`、`guide.txt`、`tables_overview.txt`、`manifest.txt`、`round.txt`；为核对数值自洽另只读 `results/nc80_cna_share_v2.csv`、`results/nc52_stats_auc_ci_methods.csv`（数值产物），未读取任何审稿报告、专家团汇总、主编事实核查或修复报告，未联网。引文位置以 `文件名:行号` 标注；SI 指 `si.txt`，CL 指 `cl.txt`，TO 指 `tables_overview.txt`。

## 评分表

| 维度 | 分数 | 一句理由 |
|---|---|---|
| 新颖性 | 6.5 | Ka/Ks 启发式比值是合理的启发式，但作者自承「recombines established ideas」（ms:64），统计贡献更在精细校准而非新估计量。 |
| 理论严谨 | 7.0 | 补注 20 给出引理、条件 C1–C6、Cauchy–Schwarz 界与可识别性论证（si:260–271），确属认真；但「studentized / t 统计量」类比不成立（k_n 非 k_f 的标准误），C5 明示「not separately verifiable」，估计量又随 post-selection 面板定义而变。 |
| 统计严谨 | 7.0 | claim-to-test map、置换分辨率、two-way cluster-robust + wild-cluster + PSD、bootstrap-t 覆盖率、配对 DeLong + Holm、exceedance≠type-I error 的披露都远超平均水准；残留问题集中在聚类层级、post-selection P 值口径、由未拒绝推出等价、以及表头术语回潮。 |
| 证据充分 | 6.0 | 中心结论的推断依赖一个与 ω 假设同构的模拟（si:181）与未测量的 CNA 正常参考（si:277）；AUC 优势不迁移到 10x（si:142）；TCGA 自述 exploratory（si:120–121）；候选筛零 FDR 发现。 |
| 表达清晰 | 6.5 | 极尽详尽但限定语层层堆叠，且 CL 与摘要/表格/SI 之间存在限定词漂移（如 56% 的「≤」在 CL 丢失）、术语不一致（FPR / exceedance）。 |
| 影响力与 NC 适配度 | 6.0 | 方法/警示类契合 NC methods scope，但结论多为限定性或阴性（非预后标志物、假设清单、固定面板下不稳健、6.10 折为上界），precision-first 且工作窗口窄，影响面受限。 |

## 总体评价

这是一份明显已历经多轮统计修补（v0.6.4 / nc80–nc84）的稿件，其统计透明度在同类方法学中罕见：显式 claim-to-test map、对置换分辨率的正确诊断、two-way 聚类稳健方差加 wild-cluster 与 PSD 校验、小簇 bootstrap-t 覆盖率研究、以及对「exceedance 不是错误率」「Wilson 未建模供者聚类」「CNA 份额是描述性上界」的主动披露，均应肯定。但从统计推断标准看，最要紧的三条结论仍不牢：作为 primary 的 AUC 主张其零假设与待证假设同构且该背景下检出功效近零；CNA「≤56% 上界」的 95% CI 未纳入主导不确定性（δ 与未测量参考），CL 还丢失了限定词；配对 FPR 对比的区间按 597 文库聚类（596 df），而 claim-to-test map 自承有效独立单位是 4 个供者。次要问题是 SI 仍给出正文已声明「无有效 post-selection P 值」的轴富集 P 值、若干由「未拒绝」推出的等价结论、以及表格表头把 exceedance 重新标成 FPR。上述均可通过改写与统一推断口径修正，非致命缺陷（本轮未发现 P0 级错误），但不足以支持接收或 Minor Revision。

## 主要问题

### P1-1　首要推断（claim 4）零假设与待证假设同构；AUC 是排序量而非检出量，headline 未条件化
- 位置与引文：SI claim-to-test map 第 (4) 条：「ω has higher AUC than the comparator metrics in the ground-truth simulation: paired DeLong over 850 replicates, family of five comparator AUCs, Holm within the family, primary」（si:112）；摘要/CL 无条件宣称「AUC = 0.80; 10x pooled 0.51–0.53」（cl:3）、「ω best discriminated ... AUC = 0.80」（ms:36）。但同一 SI 明确承认：「The neutral-drift null above places the null perturbation on HK genes, which is the same anchoring assumption that CKI itself makes; the type-I and AUC advantages above are therefore conditional on that assumption rather than evidence for it」（si:181）；且「delta = 1: ω 0.000 (all three module seeds) ... The ω detection floor is structural」（si:175），即在校准的 5% 阈值下 ω 对 δ≤1 的功能信号几乎不检出。
- 统计上错在哪：把「对注入信号排序较好」当作「能检测细胞状态变化」的证据。ROC 的 signal 类 pooled δ≥0.25（含大量 ω 检出率≈0 的弱信号），neutral 类又 pooled HK 漂移与全局过离散两种零模型（`results/nc52_stats_auc_ci_methods.csv` note 列），AUC 0.8042 只是混合样本上的秩分离；在固定特异度 0.90 时灵敏度仅 0.42、0.95 时 0.2733、0.99 时 0.0383（同 CSV `A4b_sensitivity_at_fixed_specificity`），并非操作性 FPR 下的 TPR。更根本的是 ground truth 的功能模块被放在非 HK 基因、中性漂移放在 HK 基因，恰好复刻 A1 排除约束（si:181），因此「type-I/AUC 优势」是对假设的复述而非对假设的检验；Holm 只控制 5 个 AUC 对比的家族，无法修补设计层面的循环性。
- 怎么修：把 claim (4) 由 primary 降为 assumption-conditional，并在摘要/CL/Fig.2d 同处标注「AUC 为秩判别、非阈值检出；对 δ≤1 检出率≈0；结论条件于 A1」；补一个与 A1 无关的真值设计（如功能信号与漂移都落在非 HK、或真实配对扰动带独立表型标签），否则「ω 检测状态变化」不能作为 primary 主张。10x 数据上应保留 si:142 的「0.507–0.534 pooled AUC / 0.343–0.657 design-matched」双重口径并明确其不可与 SmartSeq2 的 0.80 等同。

### P1-2　CNA「≤56% 上界」的语义与置信区间口径越界
- 位置与引文：ms:47「CNA is associated with ≤56% (95% CI 46–66%) of the TT/NN k_n gap (an unmeasured-reference upper bound), 42% (34–50%) at a residual of 0.05, and 28% at 0.10, with per-cancer point estimates spanning 42% (KIRC) to 89% (LIHC)」；ms:10「at most 56% (95% CI 46–66%) ... under an assumed CNA-free normal reference (42% with residual signal)」；但 CL:3 写成「about half of which is associated with copy-number instability (56%, 95% CI 46–66%)」——「≤ / at most / upper bound / assumed」全部消失。SI:277 更给出「LIHC 89% [41, 193] (the smallest contrast, whose share is not stably identified; CI exceeding 1)」「The share is descriptive, not a causal mediation proportion」「the normal reference is a near-zero assumption rather than a measurement」。数值核对：`results/nc80_cna_share_v2.csv` 中 δ=0 pooled share 0.5555 [0.4578, 0.6635]、δ=0.05 为 0.4170 [0.3426, 0.4991]（与 guide:422 一致），KIRC δ=0 为 0.4165。
- 统计上错在哪：其一，[46,66] 是 sample-cluster bootstrap（B=2000）在 **δ=0 固定** 下的区间，完全没有传播 δ（未测量的正常组织 CNA 距离）与 β_CNA^TT 估计/模型设定的不确定性——而 SI 自承「an assumption that dominates the estimate」（ms:47）。把条件区间当成无条件 95% CI 呈现，精度被系统性高估。其二，「≤56% 上界」并不成立为对真实因果份额的上界：它只是 δ 网格上 pooled 估计在 δ=0 的取值，δ 增大时下降；而单个癌种 LIHC 的点估计 89%、CI [41,193] 已超过 1，说明该「份额」在构造上无上界，把 56% 称为「上界」与自身结果张力明显。其三，措辞从正文的「at most / ≤ / associated with / upper bound / descriptive, not a causal mediation proportion」在 CL 漂移到「about half ... is associated with」，接近点归因，属越界。
- 怎么修：全文（含 CL）统一为「在假设正常 CNA≈0 条件下的描述性贡献比 ≈56%，条件 95% CI 46–66%；δ=0.05 时 42%、δ=0.10 时 28%」，明确该 CI 不含 δ 不确定性；把「upper bound」改述为「δ=0 处的估计值」或给出严格可证明的界；对 LIHC 89%[41,193] 明确说明其 CI 超过 100% 意味着估计不稳定而非「更大份额」；若坚持上界措辞需给出数学定义。

### P1-3　区间聚类层级（597 文库 / 596 df）与有效独立单位（4 供者）不一致，wild-cluster 只作符号敏感性
- 位置与引文：ms:102「a wild-cluster bootstrap over the four donors (all 16 Rademacher sign patterns enumerated exactly, plus 9,999 random draws) preserves the sign of every contrast」；SI:147「Intervals are therefore reported instead of exact P values, with both library endpoints of every pair as clusters (two-way cluster-robust variance, V_a + V_b − V_ab, t reference with 596 df)」「Clustering inflates the variance 2.4–2.7-fold relative to the naive pair-level binomial variance」；SI:148「with only 16 distinct sign patterns these are small-cluster sensitivity intervals, not calibrated 95% intervals」；而 claim-to-test map 结尾直言「the effective independent units of the two-way cluster-robust intervals are the four donors」（si:112）。SI:184 又显示 6–7 簇时 wild(Rademacher) 覆盖率仅 0.816/0.806（比 percentile 更差）。具体对比：raw JS 的 library-clustered 区间 [+0.135, +0.196]，wild percentile 区间 [+0.153, +0.179]（si:147–148）——后者反而更窄。
- 统计上错在哪：2,161 个 T1 对来自 597 文库、4 个供者、mean pair degree 7.2（si:147）。以文库为簇给 596 df，隐含独立信息量远大于 4 个供者；若存在供者层相关（脑图谱仅 4 供者，且 94.5% 区域对共享供者，si:304），library-level 方差会低估 SE。作者做的 4 供者 wild-cluster 本应是更保守的口径，但只被用于「保号」，且其 16 个符号模式产生的区间比 library 区间更窄、被作者自述为「not calibrated 95% intervals」——因此没有任何一条**校准到供者层级**的区间支撑「every interval excludes zero」这一表述。同一稿件对梯度量却用了 donor cluster bootstrap（ms:113，给出 [0.80, 2.34] 含 1 与 [1.92, 3.78]），口径不对称。
- 怎么修：明确 T1 对比的主推断是 library-level 还是 donor-level；若有效单位是 4 供者，应以 donor-level（wild-cluster 的合适参考分布或有效簇数校正）区间为主并报告其覆盖率缺陷，library-level 与 wild 区间降为敏感性；不要以「wild 保号」代替校准区间。对梯度量与 FPR 对比采用一致的聚类层级并说明差异理由。

### P1-4　由「未拒绝」推出「等价 / 已校准」；中心反转结论缺有效 sharp-null 检验
- 位置与引文：ms:27「No control comparison reached significance (all P > 0.05): biologically equivalent populations are recognized as undiverged.」（配合 si:127「All permutation P-values use a one-sided test」）；ms:38「ω was fully calibrated (0 of 30 above its null 95th percentile ...) whereas raw JS misreported 36.7%」；SI:145「0 of 30, Wilson 95% CI [0.000, 0.114]」。反转主张方面，SI:292 自承 TCGA 每癌置换「the corresponding TCGA P-values (all P > 0.9) ... The aggregate-level permutation test is accordingly uninformative for the reversal claim, which rests on the pair-level cluster bootstrap」，claim-to-test map 第 (5) 条把 primary 检验定为「sample-level cluster-bootstrap 95% CI of the NN/TT k_n ratio」（si:112）。
- 统计上错在哪：单次单侧上尾置换在 α=0.05 未拒绝，不能推出「等价/无偏离」（absence of evidence ≠ evidence of absence）；需等价性/非劣效边距与相应区间。Kang「0 of 30」在 5% 零假设下期望约 1.5 次，Wilson [0, 0.114] 本身包含 0.05，故「fully calibrated」是过度陈述；应表述为「与 5% 名义水平相容」。中心反转（NN/TT）没有任何可用的 sharp-null 检验：聚合置换 P>0.9 被作者判定 uninformative，推断实际由「比值 CI 排除 1」承担——这是估计口径，不是带明确 type-I error 的假设检验；把 claim (5) 标为 primary 时须说明其零假设与错误率定义。
- 怎么修：把「recognized as undiverged / fully calibrated」改为「未拒绝上尾；与名义 5% 相容（Wilson 上限 0.114）」；为等价主张给出等价边距或明确只作描述。对反转结论，要么声明「以 cluster-bootstrap 区间为推断口径、无 sharp-null P 值」，要么补一个具备功效的匹配设计检验（作者已说明固定面板置换反保守且无功效，si:84、si:292）。

### P1-5　post-selection 推断口径自相矛盾：正文声明「无有效 P 值」，SI 仍报轴富集 P 值；claim-to-test map 内部不一致
- 位置与引文：ms:62「a post-hoc, illustrative pattern only (the axis was defined after inspecting the candidates and carries no valid post-selection P value; Supplementary Note 14)」；但 SI:236 给出「the hypergeometric tests (P = 0.005, 2.1 x 10^-5, and 1.3 x 10^-5 respectively)」与「Strong-tier excess is significant under a hypergeometric test (P = 9.6 x 10^-31)」；guide:270 更以置换给出 P = 1.005e-5 / ≤1e-5，并自述 selection-rule-matched null 的结论是「the supported claim is axis concentration of surviving candidates, not an axis excess」。同时 map 第 (7) 条写「family of the ten superclasses」（si:112），而补注 18 实际检验 3 个 neuronal superclasses（si:250–252）；map 总则称「Where no family is entered the statement is descriptive and no P value is claimed for it in the main text」（si:112），但正文印刷了多处 descriptive P 值（ms:33「Mann-Whitney P = 5.6 × 10⁻¹⁸, descriptive」、ms:41「P = 5.5 × 10⁻¹⁴, descriptive」、ms:56、ms:58）。
- 统计上错在哪：轴是在看过候选后定义的（post-selection），SI:236 自己也指出「the tier variable ... and the per-pair permutation P-values are both monotone functions of the same observed and null ω values, so the tier-graded raw-P enrichment is partly guaranteed by construction」。此时 Note 14 报告的未校正超几何 P 值（假设端点独立，且候选共享端点）不具备有效 post-selection 覆盖，与正文「no valid post-selection P value」直接冲突；读者会从 SI 读到正文已撤回的推断。map 的 family 数目与「descriptive 不印 P」通则也与正文不符，削弱这份本应权威的映射表。
- 怎么修：删除或显著标注 Note 14 / guide 5.13e 中未做选择规则匹配的超几何 P 值，仅保留 rule-matched null 的「浓度非超额」结论；统一 map 第 (7) 条家族定义（3 neuronal superclasses / 10 non-neuronal classes）并把「descriptive 不印 P」改为「descriptive，P 值仅作描述且忽略相依性」。

### P2-1　「FPR / misreported」与「exceedance 不是错误率」的术语混用回潮到表格表头
- 位置与引文：正文与 SI 处理得正确——ms:39「It is a library-effect sensitivity statistic, not an error rate」、SI:149「its 28.6% ω value is an operational exceedance rate, not a type-I error rate」、SI:150「(the main-text exceedance rate; FPR in the deposited tables)」。但 TO 中 Supplementary Table 2a 表头「Method | FPR/type」、Table 3a「FPR (k/n) | Wilson 95% CI」、Table 4「FPR (observed > own null 95th percentile)」（TO:28、40、49），以及 ms:38「raw JS misreported 36.7% and cosine 23.3%」——在已知 per-pair cell-shuffle null 反保守（library-aware null 下 ω 为 5.5% / 4.8%，si:150）的前提下，把该量称为 FPR / misreported 会重新引入被作者正确排除的混淆。
- 怎么修：表格与存档 CSV 列统一改名「exceedance rate」，并在所有出现处保留「not a type-I error / not an error rate」标注；删去「misreported」等暗含假阳性的措辞。

### P2-2　Wilson 区间未建模聚类，披露只见于 Table 3a
- 位置与引文：TO:37/39 明确「The Wilson intervals treat the 30 pairs as independent (donor-level clustering is not modeled), so they are optimistic for the cohort-level rate」——这是很好的披露。但 Table 4 的 2,161 对、SI:149 的 batch 分层 Wilson CI（n=1,488 [9.8–13.1]、n=673 [63.2–70.3]、n=1,334 [8.8–12.1]）、SI:150 的 library-aware null Wilson CI [4.5–6.8] / [3.8–6.1] 均以对为单位按独立处理，未重复该 caveat。
- 统计上错在哪：这些对同样嵌在 597 文库 / 4 供者内，Wilson 区间过窄；而作者仅在配对对比上给了 two-way 聚类稳健区间，绝对率的不确定性仍是无聚类的。
- 怎么修：对所有绝对 exceedance 率补一句「Wilson 未建模文库/供者聚类，偏乐观」，或改用以文库/供者为重抽样单位的区间。

### P2-3　伪重复下仍印出极端量级的描述性 P 值
- 位置与引文：TO:61（Table 5）「< 10⁻³⁰⁰」「1.4×10⁻²³²」「8.4×10⁻⁵⁹」等，同表自承「The pair-level Mann-Whitney P-values are descriptive only: they ignore the dyadic dependence between pairs sharing a sample」；ms:191「P < 10⁻³⁰⁰, pseudoreplicated at the pair level」；TO:71（Table 6）「Per-tumor means share TT pairs across groups, so the KW/Dunn tests and within-group bootstrap CIs do not model this pair-sharing dependence」。
- 统计上错在哪：在相依单元上算出的 P 值连「描述性」解释都不成立（P 值没有定义良好的零分布参考价值），10⁻³⁰⁰ 量级会误导读者以为证据极强；既然作者已判其为 descriptive，应给效应量而非 P 值。
- 怎么修：Table 5 / Fig.4f / 相关正文改报比值与 cluster-bootstrap CI、rank-biserial 或 fold-change，删除无解释的极端 P 值；与 si:300「the P < 10⁻¹⁴⁵ caliber is retired」的处理保持一致。

### P2-4　KRAS/EGFR 的 DeLong P 值未处理 per-tumor 分数共享 TT pair 的相依性，亦未明确是否配对
- 位置与引文：SI:157「ω scores KRAS- against EGFR-mutant tumours at AUC 0.648 (95% CI 0.568–0.733; n = 120 versus 61), below a leave-one-out DE projection (0.841; ΔAUC −0.193, 95% CI −0.307 to −0.069, DeLong P = 0.002)」；ms:16 同。仿真侧明确用「paired DeLong」（si:179、TO:25），此处只写「DeLong P = 0.002」。而 TO:71 已承认为每肿瘤 ω 是重叠 TT 对的均值、KW/Dunn 忽略该相依性而「read descriptively」；guide:408 对同类 ΔAUC 又用了 bootstrap CI（[−0.126, −0.023]）。
- 统计上错在哪：两个 AUC 在同一批肿瘤上计算，须用配对 DeLong；且 per-tumor 分数因共享 TT 对而相依，普通 DeLong 的独立性假设不成立，P=0.002 未被相依性校正。与 Table 6 的谨慎处理及仿真侧的 paired/cluster 口径不一致。
- 怎么修：注明「paired DeLong」，并用考虑了 pair-sharing 的自举/聚类稳健 ΔAUC 区间与 P 值复核；或比照 Table 6 明确标为 descriptive。

### P2-5　850-replicate ROC 与 10x 的 TPR@FPR / pooled AUC / design-matched TPR 三种口径需更清楚区分
- 位置与引文：TO:25「Six-metric ROC comparison ... (850 replicates: 600 functional, 250 neutral; all metrics scored on the same replicates)」；SI:178「The main-text AUC 95% CI [0.770, 0.838] is the DeLong interval on the 850-replicate ROC」；SI:142「The pooled AUC over all injected replicates (δ ≥ 0.25) against the split-half nulls is 0.507–0.534 for ω ... The design-matched statistic ... has a null value of 0.500 by construction ... ω straddles the null at 0.343–0.657 with no monotone trend in δ」；ms:10「35–66% vs 97–100% of injected 10x modules」。
- 统计上错在哪：稿件确实把三者分开了（值得肯定），但 (a) 850-replicate ROC 与 10x pooled AUC 都把多个 δ 与多种 neutral 机制池化进一条 ROC，DeLong 的独立性假设仅靠 module-seed 聚类自举旁证（si:178–179）；(b) 摘要的「sensitivity 35–66%」是 design-matched、零值由构造为 0.500 的配对检出率，并非 FPR=0.05 下的 TPR，措辞易被读成经典 TPR@FPR；(c) 10x 的 global-q95 held-out 率 0.02–0.10（si:142）与名义 0.05 不齐。
- 怎么修：在摘要/图注对 35–66% 明确标注「design-matched paired detection, null=0.5」；ROC 结果补固定特异度灵敏度（已有 CSV）；说明池化 δ/neutral 对 AUC 可解释性的限制，并把 seed-cluster 自举作为主 DeLong 的相依性校正说明。

### P2-6　「studentized / t 统计量」类比与统一零假设定义不严
- 位置与引文：CL:4「the HK denominator studentizes the null eightfold」、ms:10「ω studentizes divergence (brain null CV 1.20 → 0.146)」、ms:14「ω is a studentized statistic」；SI:270「the same logic by which dividing by the sample standard deviation turns a mean difference into a t-statistic」，并给出 CV 1.21→0.148、max/min 195→1.63；SI:271「C5 ... is not separately verifiable on observed pairs」。零假设则随数据集而变：si:72「group labels are exchangeable」、脑区为 library-to-region block-shuffle（si:93）、技术重复为 per-pair cell-shuffle（si:144）。
- 统计上错在哪：t 统计量除以的是同一估计量自身的标准误；k_n 是**另一套 HK 基因**上的 JS 散度，不是 k_f 的 SE，二者之比不具 studentization 的枢轴性；CV 坍缩是经验现象，SI 自己也只说「approximately ancillary」。此外 ω 没有跨全文统一的 H0/type-I 定义（标签置换 / 块洗牌 / 细胞内洗牌各不同），CL 的「design-testable separation」暗示单一可检验零假设，容易被过度解读。α 与 post-selection 面板相依、绝对 ω 不可迁移（ms:43、si:266）进一步说明估计量不是固定总体参数。
- 怎么修：把「studentized / t-statistic」改为「background-normalized ratio with empirically reduced null dispersion」，保留补注 20 的条件化表述；在 Methods 汇总一张「各数据集零假设—交换单元—检验量」对照表，明确 CK I 作为方法不带单一 type-I error 定义。

### P2-7　两独立家族「pre-specified before analysis」不可核查；跨家族未联合校正的 caveat 未随结果呈现
- 位置与引文：si:112「Families (6) and (7) were pre-specified as two independent families before analysis ... Two pairs of families are consequently unprotected, (6) against (7) and the class-level tests against the pair-level screen」；ms:74「reported without joint cross-family correction」。但 Results 直接报「regional structure significantly raised mean ω for 4 of 10 classes ... 3 of 10 surviving Benjamini-Hochberg correction」（ms:56）而未附该 caveat；且 SI 中大量分析明标 post-hoc（si:222「Three post-hoc controls」、si:235 Note 14 标题「(post-hoc)」、si:196「The k_f-only controls are post-hoc」），材料包又自述经历 nc80/nc82/nc84 多轮修补。

- 统计上错在哪：披露 ≠ 校正；在 (6) 与 (7)、(7) 与 pair-level screen 之间未做联合校正，意味着整个脑区分析没有全局 FDR/FWER 控制。「pre-specified before analysis」在一份多轮增补的包内无法核验，读者无法判断家族划分是否事后。
- 怎么修：在 Results/摘要中对「3 of 10 surviving BH」加注跨家族未联合校正；提供预注册/分析计划的时间戳或明确改为「按问题划分的独立家族、非预注册」；如有余力给出跨两家族的联合校正（或说明为何分层控制足够）。

## 优点（统计诚实披露点名）

1. **显式 claim-to-test map**（si:112）：逐条列出 10 个 headline claim 的承载检验、多重性家族、primary/exploratory 与「无家族即描述性」，并主动声明「two independent claim families are reported without joint cross-family correction」「the effective independent units ... are the four donors」。这种映射在方法学投稿中非常少见，值得肯定。
2. **置换分辨率诊断正确且诚实**：B=1,000 → 最小可分辨 P = 9.99×10⁻⁴；BH 阈值 0.05/31,764 ≈ 1.6×10⁻⁶ 低约 600 倍；明确写「min q = 0.520 ... is a statement about permutation resolution rather than evidence against candidates」（ms:112、si:115、si:320），并配 pseudo-region 负对照（si:228–230）与 donor-stratified null（si:231）。没有把「无 FDR 发现」粉饰成发现，也没有把分辨率地板当成证据。
3. **聚类与小簇推断做得扎实**：two-way cluster-robust V_a+V_b−V_ab + PSD 检验（最小特征值 1.4×10⁻⁵，ms:102 / si:148）、4 供者 wild-cluster 精确枚举 16 个 Rademacher 符号（si:148）、小簇覆盖率研究（percentile 0.876/0.873 → bootstrap-t 0.953/0.951，si:184）并据此把 Bergmann-glia「above-baseline」降级为定性（si:185）、以及两阶段 bootstrap 取代伪重复的 [7.37, 8.02]（ms:27、si:131）。主动识别 pseudo-replication 并修正是高水准统计实践。
4. **效应量与 P 值平衡、描述/推断分离总体到位，关键限定语点名**：正文反复标注 descriptive / hypothesis-generating / not a discovery set（ms:61–62）；「not an error rate」（ms:39 / si:149）、「Wilson intervals ... optimistic for the cohort-level rate」（TO:37）、「an unmeasured-reference upper bound」「The share is descriptive, not a causal mediation proportion」（ms:47 / si:277）、「carries no valid post-selection P value」（ms:62）都是应被点名表扬的诚实披露；AUC 侧用「paired DeLong + Holm within five-contrast family + module-seed cluster bootstrap」三口径互证（si:178–179、TO:25），并诚实声明「Rank discrimination and thresholded power diverge」「background-specific」（ms:36）。

## 给编辑的备注（是否可送外审）

该稿明显已历经多轮统计修订（manifest:4「nc84 round: expert-panel P0/P1/P2 fixes」、v0.6.4），核心统计缺陷并非新问题而是「披露充分、口径未收口」。因此**不建议以再送一轮外审代替实质修订**；建议 **Major Revision**，并把修订稿交一位熟悉重抽样/聚类稳健推断的统计审稿人专门复核三点：(i) 能否给出独立于 A1 假设的真值验证以支撑 primary 的 AUC/特异性主张；(ii) 供者层级（4 donors）校准的区间；(iii) CNA 份额的条件 CI 与「上界」措辞。若作者无法就 (i) 提供假设无关的验证、或坚持把 assumption-conditional 的 AUC 与 unmeasured-reference 归因作为 primary 结论，则建议改判 Reject。当前版本不宜接收，也不宜仅作 Minor Revision；P0 级致命错误本轮未发现。
