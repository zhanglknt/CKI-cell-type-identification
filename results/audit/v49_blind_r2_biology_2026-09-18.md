# v49 盲审报告 R2：癌症生物学与转录组学应用

- **评审人**：R2（癌症生物学 / 转录组学应用）
- **日期**：2026-09-18
- **对象**：CKI v49 投稿包（Nature Communications），聚焦 TCGA 升级节（主稿 Results "A pan-cancer map..."、Abstract、Discussion、Fig. 5 图注、SI 3.21）及审计数字（nc49_tcga_main / nc49_pilot_lihc）
- **总体判定**：**Major Revision，评分 6/10**（若两条 P0 完成且结论稳健，可升至 7.5–8）

---

## 一、逐条核查结论

### 核查 1：生物学解读健全性（肿瘤 ω < 正常 ω，k_n 主导）

**稿件未过度解读，这是本节的优点。** 主稿并未把反转归因于「去分化/HK 上调」这类强机制叙事：Results（fulltext L50）只作否定式表述「a more stable housekeeping baseline among adjacent non-tumor specimens, not smaller functional-gene divergence of tumor cells」；Discussion（L81）明确列出 composition shift、peritumoral inflammation、RNA quality 三个竞争解释，并声明 marker panel「bounds rather than settles the question」；L87 单独声明 HK 在癌症中可能失调（anchor failure）。相邻正常组织 ≠ 健康组织（L52）、LIHC 生存 NO-GO 已如实降格。这种克制是加分的。

**但仍有一个更保守且更可信的框架被放在了次要位置**：肿瘤纯度在样本间的**方差**本身就会机械地抬高 TT 对的 HK 分歧——与任何生物学机制无关。normal 样本组成相对均一（如肝=肝细胞、肺=肺泡上皮为主），而肿瘤的纯度跨样本波动大，两两比较时 HK 剖面差异必然更大。这一「纯度方差 → k_n 抬高」通道是反转最 parsimonious 的解释，稿件把它混在 4-marker 组成检查里弱处理了（见 P0-1）。

**「bulk TPM 混合组织 + 纯度混杂」处理不充分**：组成检查只回归了 k_n（Discussion L81：regressions of log k_n on pair type with four composition deltas），**未对 k_f 做同样的组成校正**。而由于 k_f 基因是逐对循环选取的 top-200 |Δ| 基因，bulk 肿瘤对之间差异最大的恰恰就是浸润/纯度相关基因，所以「TT k_f ≥ NN k_f」不能干净地读作「肿瘤细胞功能分歧不小」——它是被组成污染的量。稿件的否定式表述（"do not indicate smaller"）勉强守住了边界，但 Fig. 5a 图注和 Results 中「functional-gene divergence」的措辞仍会让读者过度解读。建议补一句：TT 对 k_f 面板预计富集免疫/间质/增殖标志物，k_f 在 bulk 层面是「组织状态分歧」而非「肿瘤细胞功能分歧」；若能对 top-200 面板做一次 Hallmark 富集（一行分析），把话说实，可引用性大增。

### 核查 2：LUAD KRAS/EGFR 分解的生物学合理性

**方向与已知肿瘤生物学相符**：
- KRAS 突变 LUAD 是公认的异质性类别（STK11/KEAP1 共突变亚型、不同转录亚型），组内 k_f 偏高（KRAS>EGFR，P_Holm=0.015）方向合理；
- EGFR 突变肿瘤是单驱动「成瘾」表型、转录上更同质，k_f 无差异（P>0.09）也合理；
- k_n 排序（WT 0.00322 > EGFR 0.00280 > KRAS 0.00265）**与纯度梯度预期一致**（EGFR 肿瘤 lepidic 生长、纯度偏低 → k_n 应高于 KRAS）——这恰恰说明 k_n 组间差可能仍是纯度，而非「基线生物学」，反而强化了 P0-1 的必要性。

**但「KRAS 走 k_f、EGFR 走 k_n」的干净二分被实际效应量削弱了**（P1-2）：按成分均值粗算，KRAS−WT 的 ω 升高约 85% 来自 k_n 下降（−18% → ω ×1.22），k_f 升高仅贡献 ×1.037；且 Dunn 检验 KRAS vs WT 的 k_f 为 P=0.097（NS），只有 KRAS vs EGFR（P=0.015）和 bootstrap 均值差 CI [0.002, 0.019] 支持 k_f 成分。即：**KRAS−WT 对比同样以分母为主**，「functional component」主要由 KRAS-vs-EGFR 对比承载。Abstract（L8）「with a functional component, the EGFR association baseline-driven」的二分对广泛读者偏强。

**EGFR「baseline-driven」的提法本身站不稳**（P1-3）：EGFR−WT 的 ω 差根本不显著（Dunn–Holm P=0.39，bootstrap CI 含 0），k_n 差也只有 P=0.09（NS）。一个两个臂都不显著的「关联」被称为「baseline-driven」，是过度命名。诚实的说法是：「EGFR 突变组与 WT 在 ω 上无显著差异；KRAS 与 EGFR 的差异部分由 k_f 承载」。稿件正文（L51）确实披露了 P=0.39，但 Abstract 与 Fig. 5d 图注「the EGFR association appears only in the k_n baseline」需要软化。

**样本量**：61/120/311 对中位数水平的组间比较够用；对 k_f 这种小效应（Δ≈0.01，SD 大）则刚好在检出边缘——证据等级与「边际支持的功能成分」相称，不宜再往上抬。

### 核查 3：混杂逐项

| 混杂 | 稿件处理 | 评价 |
|---|---|---|
| 批次/平台/中心 | 未直接检验；癌种内 tumor vs normal 的处理时间/TSS 中心系统性不同，TCGA 已知 | **未覆盖**（P1-4：至少补一句「within-cancer tumor/normal aliquots 的 TSS/批次分布检查」或一句 limitation） |
| 肿瘤纯度 | 4-marker panel 代理 + cluster bootstrap（L52, L81） | **代理过弱，金标准未用**（P0-1） |
| LUAD 组间协变量（吸烟/性别/分期） | 声明「no age, sex, or smoking metadata were available locally」（L51） | **可行性被证伪**：LIHC Cox 从同一 cBioPortal/GDC 拿到了 stage/grade/age/sex（L123, SI 3.21）——LUAD 的吸烟/性别/分期同样可得。「本地没有」是选择不是约束（P0-2） |
| 组成 → k_f | 未校正（仅 k_n） | 见核查 1（P1-1） |
| 相邻正常 ≠ 健康组织 | 已声明（L52） | 充分 |
| 线性归一化敏感性 | softmax→线性重算全保留（L52） | 充分，加分 |
| LIHC 生存混杂 | stage/grade/age/sex 全调整，NO-GO 如实降 SI | 充分，加分 |

**补充统计层面观察（交 r3-stats 主审，此处记录生物学影响）**：L50 的 Mann-Whitney P（1.2e-238 等）是在 2,000+ 共享样本的 pair 上算的，pair 不独立 → 伪重复、P 值严重膨胀；诚实的推断是 sample-level cluster bootstrap CI（稿件已算）。建议正文只引 CI，MWU P 降 SI 或改注为描述性。这不影响方向结论（CI 很稳），但审稿人会抓。

### 核查 4：发现级成色（NC broad interest）

**现状**：5 癌种一致 + CI 稳健 + 机制定位到分母 + 生存阴性如实报告——作为方法论文的一个应用节是合格的；作为「对广泛生物学读者有意义」的独立发现，**机制未定（纯度 vs HK 失调）导致它停留在描述层面**，癌症读者会 shrug：「肿瘤间分歧更大、且 purity 没校正——so what?」

**花最小代价显著提升可引用性的三条**：
1. **用现成纯度数据把 P0-1 做掉**（ABSOLUTE/ESTIMATE/consensus purity 全部公开、TCGAbiolinks 一行可调）：若 purity 校正后 NN/TT 反转保留，这节立刻从「描述」升级为「发现」；若不保留，早发现比被审稿人发现好。
2. **一句话承认并定位 GTEx 缺口**：L52 已说 adjacent normal ≠ healthy，再加半句「以 GTEx 健康组织为外部参照是未来验证方向」即可；若能真的跑一个 GTEx 肺 vs TCGA 正常 vs TCGA LUAD 的三方 k_n 比较，是直接回答「k_n 抬高是肿瘤特异还是 field effect」的杀手级补充（P1-5，可选）。
3. **top-200 k_f 面板富集分析一行结果**（见核查 1）：把「k_f 在 bulk 层面测量什么」说实。

### 核查 5：癌症领域审稿人最可能攻击的 3 个点

1. **纯度/组成**：反转与 k_n 抬高可完全由跨样本纯度方差解释；4-marker 代理在金标准纯度估计唾手可得时不可接受；且 purity 未进 LUAD 突变组比较。
2. **吸烟**：KRAS（吸烟者富集）vs EGFR（从不吸烟者富集）比较不调整吸烟状态，在肺癌领域是硬伤；吸烟本身广泛改变转录组（含代谢/HK 基因），「functional component」与「baseline-driven」的归属都可能在吸烟校正后重排。
3. **k_f 循环选取在 bulk 肿瘤上的语义**：per-pair top-200 DE 面板在 TT 对上被组成差异主导，「functional divergence」名不副实；叠加 adjacent-normal 参照无 GTEx 对照、LIHC CI 含 1（且为单侧 MWU P=0.0099），整条「泛癌反转」链的最弱环节清晰可指。

### 核查 6：评分与判定

**6/10，Major Revision。**

理由：统计执行与诚实度（NO-GO 降 SI、anchor failure 前置声明、线性归一化敏感性、cluster bootstrap）远高于同类稿件平均水平；数字与审计源、Fig. 5、SI 3.21 三方核对**未发现任何不一致**（61/120/311 vs 62/122 条码的差异在 Methods L123 有解释；Abstract「4 of 5 CI excluding 1」准确）。扣分集中在两条**可行但未做**的混杂校正（P0-1 纯度、P0-2 吸烟/协变量）和 EGFR 框架的过度命名（P1-3）。两条 P0 都是「取数 + 重跑现有脚本」级别的工作量，非新实验。

---

## 二、问题清单（按优先级）

### P0（阻断级，均可行）

- **P0-1 用共识纯度估计替换/补充 4-marker 代理。**
  位置：Results L52（「marker-panel composition check … bounds rather than settles the question」）、Discussion L81、SI Note 8。
  建议：取 TCGA 共识纯度（ABSOLUTE/ESTIMATE/LUMP，TCGAbiolinks 或已发表表）作逐肿瘤协变量：(a) 检验 per-tumor mean k_n ~ purity 相关；(b) 在 NN/TT 比和 LUAD 突变组比较中以纯度为协变量做敏感性（per-tumor 统计量对纯度回归取残差，或分层）。正文一句报告校正后结论是否保留。
- **P0-2 LUAD 驱动分析补协变量调整（吸烟为首）。**
  位置：Results L51（「no age, sex, or smoking metadata were available locally」）、Methods L123、SI 3.21（L125 同句）。
  建议：从 cBioPortal/GDC 取 LUAD 吸烟状态/性别/分期（与 LIHC 临床数据同源，可行性已被稿件自己的 LIHC Cox 证明），至少做吸烟分层或 ANCOVA 敏感性；若 KRAS vs EGFR 的 k_f 结论在吸烟校正后保留，本节可信度质变。同时把「not available locally」改为诚实表述（「not adjusted here; sensitivity in SI」）。

### P1（重大，显著影响解读或可引用性）

- **P1-1 k_f 未做组成校正 + k_f 面板语义未检验。** 位置：Discussion L81（回归仅及 k_n）、Results L50（「functional-gene divergence of tumor cells」）。建议：k_f 同样过组成回归；对 TT 对 top-200 面板做 Hallmark/免疫标志物富集，正文一句界定 bulk k_f 的语义边界。
- **P1-2 「KRAS 功能成分」需标注量级。** 位置：Abstract L8、Results L51。建议：注明 KRAS−WT 的 ω 升高大部分由 k_n 下降贡献，k_f 成分主要由 KRAS-vs-EGFR 对比承载（Dunn KRAS vs WT k_f P=0.097 NS，应一并报告）。
- **P1-3 EGFR「baseline-driven」过度命名。** 位置：Abstract L8、Results L51、Fig. 5d 图注。EGFR−WT 的 ω（P=0.39）与 k_n（P=0.09）均不显著，建议改为「EGFR-mutant tumors did not differ from wild-type in ω; the KRAS–EGFR difference is partly carried by k_f」。
- **P1-4 批次/中心混杂未提。** 位置：Methods 4.3（SI）、Discussion L88。建议：补一句 within-cancer tumor/normal 的 TSS/批次分布检查或明确列为 limitation。
- **P1-5（可选但高收益）GTEx 健康组织外部参照。** 位置：Results L52（相邻正常声明处）。一句话指明方向；若能补 GTEx vs TCGA-normal vs TCGA-tumor 的 k_n 三方比较，可直接区分「肿瘤特异 HK 失调」与「field effect / 组成」。

### P2（次要）

- **P2-1「wild-type」标签误导。** 位置：Results L51、Fig. 5b。WT = 仅 EGFR/KRAS 两位点野生型，实际含 ALK/ROS1/BRAF/MET 等其他驱动，首次出现处应为「EGFR/KRAS-wild-type」。
- **P1/P2 边界：pair 级 MWU P 值伪重复。** 位置：Results L50。建议正文只引 cluster-bootstrap CI，MWU P 注明为 pair 级描述性或降 SI（统计细节交 r3-stats 裁定）。
- **P2-2 LIHC 单侧 MWU P=0.0099 + CI 含 1 的「4 of 5」框架**可接受，但建议在正文同句给出「方向 5/5 一致」与「CI 4/5」两个口径（稿件已基本做到，保持即可）。
- **P2-3 条码→分析样本的缩减链**（62 EGFR→61 等）已在 Methods L123 解释，建议在 SI 3.21 同样写一句，避免审稿人按 62/122 核对时产生疑问。

---

## 三、数字核对记录

- Abstract「1.13–2.46, CI excluding 1 in four of five, 3,596 samples, 2.1–3.6-fold k_n」与审计表逐项一致；
- Fig. 5（a 森林图顺序 LUAD>KIRC>LUSC>BRCA>LIHC、b KW P=7.8e-7、Dunn 3.6e-7/0.008、c k_f KRAS>EGFR P_Holm=0.015、d k_n WT>KRAS P_Holm=4.2e-4）与审计表、正文 L50-51、图注 L208 一致；
- LIHC Cox NO-GO（HR/SD 1.06 [0.85, 1.32], P=0.59）在正文 L52、SI 3.21d、pilot 审计三处一致，降格处理恰当；
- SI 4.3 样本数（3,214 tumor + 382 normal = 3,596）与 Abstract 一致。
- **未发现数字矛盾。**
