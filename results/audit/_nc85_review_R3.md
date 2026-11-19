# R3 独立盲审意见（癌症基因组学 / 临床转化）

**总分：6.5 / 10**
**建议：Major Revision**
**判定标签：方法学警示诚实、可复现性极强，但癌症端结论多为描述性/阴性且受 unmeasured-reference 与纯度混杂约束，仍有残留因果措辞与泛化表述需在大修中收敛。**

> 审阅范围声明：仅依据 `_nc85_review_materials/` 内 `ms.txt`、`si.txt`、`cl.txt`、`guide.txt`、`tables_overview.txt`、`manifest.txt`、`round.txt` 七个文件；未读取任何其他轮次审稿报告、专家团汇总、事实核查/修复报告或其他审稿人意见，未联网检索作者身份，未读取记忆文件，亦未读取 `results/` 下 CSV。下文所有引文与数字均出自上述七个文件，引文保持原文（英文），位置以 `文件:行号` 标注。

## 一、评分表（6 维，1–10，可 0.5）

| 维度 | 分数 | 理由 |
| --- | --- | --- |
| 新颖性 | 6.0 | Ka/Ks 类比把 JS 散度拆成 k_f/k_n 并做 studentized 比值，思路有一定新意；但作者自承 “The index recombines established ideas”（`ms.txt:64`），癌症部分是公共数据（TCGA/GTEx）的再分析，核心产出是一条归一化警示而非新癌症生物学。 |
| 理论严谨 | 6.5 | Supplementary Note 20 给出 Lemma 1/2、Proposition 3–5、条件 C1–C6 与排除限制 A1，并明确 “exact at the k_n scale and approximate at the k_f scale”（`ms.txt:74`）、heuristic 而非形式选择度量，披露质量高；但理论前提 A1（φ=0 on HK panel / HK 受约束）恰被作者自己在癌症与 IFN-β 中证伪（TCGA 分母随病程移动 1.3–3.3 倍），C5 “not separately verifiable”，前提与应用对象存在结构性冲突。 |
| 统计严谨 | 7.5 | permutation、sample-level cluster bootstrap、two-way cluster-robust/wild-cluster、paired DeLong、cox.zph + tt(x)/epoch-split、B 分辨率与 Monte-Carlo error、anti-conservative 处自承，披露密度罕见（`si.txt:112`, `si.txt:147–148`, `ms.txt:112–114`）。扣分：per-tumor 值共享 TT pairs 的依赖性使 KW/Dunn 只能作描述、pair-level MWU 描述性、Cox 三个代数相关 exposure 分 family 校正、TCGA 固定面板检验 anti-conservative、CNA share 的 CI 未传播 δ 假设不确定性。 |
| 证据充分 | 6.5 | 数据规模大（3,535 样本、5 癌种、多 atlas、SNP6/RIN/GTEx 多源），稳健性分析极多；但癌症端为 bulk-only、无独立队列、无功能/正交验证（BayesPrism/CIBERSORTx 在锁定环境不可执行）、GTEx 对照分辨力不足、normal CNA 未测量、KRAS–WT 在固定面板下不显著、临床严重度梯度为 denominator-dominated 且在 k_f-only 下反转，核心结论以阴性/边界为主。 |
| 表达清晰 | 7.0 | 结构、claim-to-test map、Reproducibility Guide（SHA-256 + spot_check 46 assertions）非常清楚。扣分：限定语过密稀释主结论、“pan-cancer” 泛化措辞、bulk/pseudobulk 术语自相矛盾、cover letter 与正文披露不对称、跨文件数值口径不一致（见 P2-4）。 |
| 影响力与 NC 适配度 | 6.0 | 对“用 housekeeping panel 归一化 bulk 肿瘤 RNA-seq”有可复现的警示价值；但癌症端无预后/诊断/分型增量（明确 not prognostic、ω 不优于常规 DE），方法在 10x、大 pseudobulk、宽 mean-shift 下失效并弱于 MELD/scDist，五癌种 exploratory。NC Methods 可容纳，但需先收敛声称。 |

## 二、总体评价

这是一份在统计披露与因果克制上明显优于平均水平的稿件：几乎所有 headline claim 都配了检验族、primary/exploratory 标签与自我设限，CNA 归因、纯度、GTEx、生存等边界分析做得系统且方向诚实。但也正因如此，癌症基因组学端的实际增量有限——核心“发现”是 HK-anchored 归一化在 bulk 肿瘤中失效这条 caution，而 CNA 归因依赖未测量的 normal reference，KRAS 组间差异主要由 per-pair gene selection 驱动，GTEx 对照在技术偏移与待检效应量级相当时不能分辨 field effect。主要缺陷不是隐瞒或数据问题，而是若干残留的因果动词、摘要层文件披露不对称，以及 “pan-cancer”“rather than a field effect” 等超出数据分辨力的表述。这些问题都可在大修中通过措辞收敛与主稿/附件一致性修订解决，无需拒稿，也不宜在未收敛前接受。

## 三、主要问题（P0 / P1 / P2）

本轮**未识别 P0 级问题**：未见数据完整性、伦理或使结论整体失效的致命缺陷。以下 5 条 P1、4 条 P2。

### P1-1｜残留因果动词与稿件自身声明直接冲突（相关性被写成驱动效应）

- **位置与引文**：`ms.txt:47` “genomic instability **creates** part of the elevation rather than opposing it”；`si.txt:277` “copy-number divergence **creates** rather than attenuates the TT/NN housekeeping gap”。但同一 `si.txt:277` 末句：“The share is **descriptive, not a causal mediation proportion**.”；`si.txt:121` “These caveats do not invalidate the descriptive findings but **preclude causal inference from bulk-level data alone**”；摘要/引言/cover letter 均用关联措辞：`ms.txt:10` “is **associated with** at most 56%”、`cl.txt:3` “associated with”。
- **问题**：Note 22 的估计是 pair-level 回归（log k_n ~ CNA distance，`si.txt:276`），本质是相关性；“creates” 把同向关联升级为生成性因果，且与同段 “descriptive, not a causal mediation proportion” 自相矛盾。癌症基因组学读者会读成“CNA 驱动 housekeeping 表达分化”的机制结论，而该设计未做中介分析，未控制肿瘤纯度、倍性、segmentation calling 对 CNA 与 k_n 的共同驱动，normal CNA 亦未测量。
- **修法**：正文、Discussion、Note 22 全部改为 “is co-directional with / is associated with”；在 Note 22 首段补一句明确该关联可能由纯度/倍性/CNA 检出率共同驱动、本设计不能区分；保留并突出 “descriptive, not a causal mediation proportion”。

### P1-2｜56% 上界在正文/SI 诚实，但摘要层披露不对称且 pooled CI 弱化了假设不确定性

- **位置与引文**：`ms.txt:10` “copy-number instability is associated with **at most 56% (95% CI 46–66%)** of that k_n gap **under an assumed CNA-free normal reference** (42% with residual signal)”；`ms.txt:47` “CNA is associated with **≤56%** … (an **unmeasured-reference upper bound**), **42% (34–50%) at a residual of 0.05, and 28% at 0.10**, with per-cancer point estimates spanning **42% (KIRC) to 89% (LIHC)** … the normal reference is assumed near zero, **an assumption that dominates the estimate**”；`si.txt:277` “the SNP6 matrices cover tumour aliquots only: **no normal sample matches, so the normal reference is a near-zero assumption rather than a measurement** … the honest reading is **about half**”“LIHC **89% [41, 193]** (the smallest contrast, whose share is **not stably identified**; CI exceeding 1)”“KIRC is the most sensitive to the normal-tissue assumption because **only 871 of its 2,000 sampled tumour pairs carry DNA profiles (44%)**”；`guide.txt:422` “CNA share **0.5555 [0.4578, 0.6635] at delta = 0** and **0.4170 [0.3426, 0.4991] at delta = 0.05**”。相对地，`cl.txt:3` 仅 “**about half** of which is associated with copy-number instability (**56%**, 95% CI 46–66%)”。
- **问题**：就“是否为诚实上界表述”而言，正文/摘要/SI 是**诚实**的（`at most`/`≤`/`upper bound`/`assumed`/`honest reading is about half`/δ 网格 56→42→28%/“descriptive, not causal”）。不足有两点：① `cl.txt` 面向编辑给出一个看似实测的 56% 与较窄 CI，未携带 “assumed CNA-free normal reference / unmeasured-reference upper bound” 限定；② 46–66% 这一 CI 是 “sample-cluster bootstrap B = 2,000”（`si.txt:277`）的结果，只反映抽样波动，**未传播 δ 假设与跨癌种异质性**——而 per-cancer 点估计跨 42%–89%、LIHC CI 上界 193%、KIRC 仅 44% 覆盖，故 pooled 精度的呈现偏乐观。
- **修法**：cover letter、Abstract、Fig 3 / graphical abstract 图注统一加 “under an assumed CNA-free normal reference; unmeasured-reference upper bound”，主值写成 “≈ half (upper bound 56% [46–66] at δ=0; 42% at δ=0.05; 28% at δ=0.10)”；在 SI 明确该 CI 不含 δ 与跨癌种离散，并补报一个把 δ∈[0,0.10] 与 per-cancer 异质性一并传播的区间。

### P1-3｜GTEx 跨队列对照分辨力不足，却用于排除 field effect

- **位置与引文**：`ms.txt:49` “adjacent non-tumor resembles healthy tissue, **tentatively consistent with tumor-specific elevation rather than a field effect** … This cross-cohort reference is **descriptive only (processing shifts k_n 1.8–2.3-fold)**”；`ms.txt:69` “**consistent with tumor-specific elevation over a field effect** (kidney is an exception; noisy reference)”；`cl.txt:3` “a field effect of the tested size is **tentatively excluded, but larger shifts are not resolved**”；`si.txt:123` “the cross-cohort comparison is **reported as unresolved for the other four**”“the two GTEx reconstructions differ by **1.6–2.3-fold through processing alone**”“the normal-tissue level is **rank-inverted** with respect to the reported NN/TT ratio (**Spearman ρ = −1.00**, exact two-sided P = 0.0167 over 120 permutations, n = 5) … **part of the reported range reflects the denominator rather than the numerator**”；`si.txt:219` “Kidney is the exception … with only **n = 28** and very high variance”“**A platform sub-cohort sensitivity within GTEx was not computable** … the finest stratification available is the organ level”。
- **问题**：跨队列技术偏移（1.8–2.3 倍）与待检肿瘤升高（2.0–2.8 倍，`ms.txt:49`）量级相当，对照无法分辨；TCGA NN 是同器官相邻正常、GTEx–GTEx 是跨个体健康，配对结构不同，正常组织异质性（取材部位、PMI/自溶、年龄性别构成）未建模且无法做 platform sub-cohort 分层；KIRC 因 n=28 被放弃。`si.txt:123` 自己指出 NN/TT 排序与正常组织水平 ρ=−1.00 反向，即跨癌种幅度部分由分母驱动。在此条件下 “rather than/over a field effect” 是排除性机制推断，超出数据分辨力。
- **修法**：主稿 Results/Discussion 改为 “在本跨队列容差下不能区分 tumor-specific elevation 与 field effect，仅支持 within-cohort 排序描述”，删去 “rather than/over a field effect”；明确正常组织异质性与 PMI 未建模；把 `si.txt:123` 的分母驱动结论（ρ=−1.00）提升到主稿。

### P1-4｜“pan-cancer” 泛化措辞与五癌种 exploratory 自述冲突

- **位置与引文**：`ms.txt:44` 小节标题 “**A pan-cancer map** of tissue-level divergence in tumors”；`ms.txt:190` Figure 3 图注 “**Pan-cancer** tissue-level divergence”；`cl.txt:3` “a **pan-cancer** reversal”；对照 `ms.txt:74` “**five cancer types make the results exploratory**”；`si.txt:121` “The TCGA **pan-cancer** analysis … is **exploratory in nature** due to several inherent limitations of bulk RNA-seq data”；`ms.txt:73` “comparisons within the same dataset and scheme only … **absolute ω does not transfer**”；`guide.txt:59` “absolute omega values are **not comparable across the two orders** - cross-pipeline comparisons should use rank statistics only”。
- **问题**：所选 5 癌种（LUAD/LUSC/LIHC/KIRC/BRCA）均为上皮实体瘤，远不足以支撑 “pan-cancer”；且 LIHC 的 NN/TT ω 为 1.11 [0.94, 1.30]、CI 含 1（`tables_overview.txt:68`），linear 与 softmax 口径下 “four of five” 与 “five of five” 会变化（`tables_overview.txt:97`），跨 pipeline 绝对 ω 不可比。读者易把 “in all five” 泛化为泛癌普适规律。
- **修法**：标题、Abstract、Discussion、图注统一改为 “five-cancer / across five TCGA cancer types”，首次出现注明“本文 pan-cancer 仅指所选五癌种”；明确 LIHC 例外与 probability-mapping 敏感性，不作跨癌种普适性推断。

### P1-5｜bulk 分辨率下的纯度/组成混杂与 k_n floor 敏感性未充分进入主稿结论；且 bulk/pseudobulk 术语自相矛盾

- **位置与引文**：`ms.txt:47` “Composition adjustment left the pooled k_n coefficient **unchanged** (−0.9% pooled, 95% CI −4.3% to +2.5%) … reference-free composition check: non-parenchymal fraction versus k_n, **ρ = 0.20–0.26**”；但 `si.txt:216` “marker panels are **noisy proxies** for true cellular composition … **neither can a marker-panel regression exclude composition as the driver**”；`guide.txt:393` “reference-based deconvolution (**BayesPrism/CIBERSORTx** is not executable in the locked environment … R 4.1.3 base packages only)”；`si.txt:220` “the non-parenchymal fraction tracks k_n **only weakly** (Spearman ρ = 0.20 LIHC, 0.26 KIRC)”。floor：`si.txt:62` “A small floor value (1e-4) on k_n is applied **only in the TCGA bulk RNA-seq analysis** (where **pseudobulk averaging across millions of cells** compresses HK gene variance and drives aggregate k_n toward zero)”；`tables_overview.txt:95` “while **1 × 10⁻³ truncates ~50% of NN pairs** and attenuates the reversal (**LUAD 2.464 → 1.494; BRCA below 1**), quantifying the floor dependence”；`ms.txt:47` 仅 “the housekeeping floor binds in **one pair only**”。术语冲突：`si.txt:74` “**No pseudobulk step is needed** as each sample is already a bulk expression profile”，而 `guide.txt:135` “**Pseudobulk: mean expression per sample**”。
- **问题**：① 未执行基于参考的反卷积（受环境限制），ESTIMATE + 四 marker panel + reference-free NNLS 均为代理，作者自承无法排除 composition as driver，但主稿 “coefficient unchanged” 与 `ms.txt:69` “Composition contributes heterogeneously” 措辞偏确定。② TCGA ω 依赖 `kn_floor = 1e-4`；抬到 1e-3 即截断约 50% NN pairs 并使 BRCA 反转消失，说明 NN 侧 k_n 分布贴近 floor 量级、reversal 幅度含 denominator-floor 成分；主稿仅以 “binds in one pair only” 一笔带过。③ 同一 `si.txt:62` 把 TCGA bulk 描述为 “pseudobulk averaging across millions of cells”，与 `si.txt:74`、`ms.txt:47` “tissue-level divergence at bulk resolution” 矛盾。
- **修法**：主稿明确“未执行基于参考的反卷积；现有代理不能排除组成混杂作为驱动”；在 Results 给出 floor 敏感性边界并报告 NN/TT k_n 分布相对 1e-4 的位置；统一术语，TCGA 段删除 “pseudobulk” 字样，`guide.txt:135` 改为 “per-sample bulk profile（无 pseudobulk 聚合）”。

### P2-1｜Abstract / cover letter 未把 AUC 0.648 明确限定为 group-level、无个体判别增量

- **位置与引文**：`ms.txt:10` “KRAS-versus-EGFR discrimination is **weak (AUC 0.648)**”；对照 `ms.txt:16` “a **group-level contrast only** … (AUC 0.648 versus **0.841** for a leave-one-out DE projection; DeLong P = 0.002)”、`ms.txt:46` “we report it as a **group-level association rather than a confirmed driver effect**”、`si.txt:157` “AUC **0.648 (95% CI 0.568–0.733; n = 120 versus 61)**, below a leave-one-out DE projection (**0.841**; ΔAUC −0.193 … DeLong P = 0.002) and indistinguishable from k_f alone (0.634 …), with k_n alone at 0.459 … at specificity 0.90 sensitivity is **0.175 (0.117–0.253)**. We therefore make **no sample-level discrimination claim** for this contrast; what survives is the **group-level shift**”；`si.txt:158` “a **group-level divergence association, not sample-level driver discrimination**, and ω offers **no classification increment over routine DE**”；`cl.txt:3` “a **group-level contrast only** (fixed-panel sensitivity P = 0.089 …)”。
- **问题**：就“AUC 0.648 / DE 0.841 语境是否被正确限定为 group-level”而言，Intro/Results/SI/cover letter 均**限定正确且反复**；唯 Abstract 单独给出 AUC 数字而未携带“非个体判别/无分类增量”，临床转化读者易把 0.648 读作候选标志物性能。
- **修法**：Abstract 改为 “… is weak (AUC 0.648) and offers no sample-level discrimination or classification increment over routine DE (0.841); the finding is a group-level association only”；cover letter 补 “no classification increment over DE”。

### P2-2｜KRAS 固定面板阴性结果在主稿被一串 “survives” 叙述稀释

- **位置与引文**：`ms.txt:46` “The KRAS elevation … **survives adjustment for purity** (adjusted log-ω ratio 1.19, 95% CI [1.12, 1.26]), smoking, TP53 and proliferation, and whole-tumor label permutation (B = 10,000: KRAS–WT P ≤ 0.001)—**but not a fixed gene panel (Δω +2.6, P = 0.089)**—… so we report it as a group-level association rather than a confirmed driver effect”；`si.txt:157` “under the fixed panel … **Δω +2.6, P = 0.089** … group means were **51.4 (WT), 48.4 (EGFR), 53.9 (KRAS)** under the fixed panel versus **123.5, 121.0, 137.2** under the circular scheme … The KRAS elevation is therefore **dominated by pairwise selection rather than by driver biology** … so that contrast is **not a robust finding**”“Histological-subtype (TRU/PP/PI) classifications were **unavailable for adjustment**”；`ms.txt:43`/`ms.txt:74` per-pair 选择的 “median **1.61-fold** inflation”。
- **问题**：主稿把固定面板失败放在一串肯定性 “survives” 中间的括号里；而 SI 明确该 contrast “not a robust finding”，且 circular selection 是 CKI 固有属性。从癌症基因组学看，这动摇“KRAS 突变肿瘤组织状态分化更高”的生物学解读（可能是 per-pair top-200 选择的产物），且 KRAS 富集的侵袭性黏液腺癌等组织学亚型未校正。
- **修法**：主稿 Results 把 “Δω +2.6, P = 0.089” 与 SI 的 “not a robust finding” 并列到句首显著位置，明确“该组间差异主要反映 pairwise gene selection 而非 driver biology”；把“组织学亚型未校正”写入 `ms.txt:74` Limitations 而非仅留在 SI。

### P2-3｜生存分析的探索性限定与 exposure 多重性未在主稿完整体现

- **位置与引文**：`ms.txt:47` “Per-tumor ω was **not prognostic** (ex-CC LIHC Cox … HR per SD 1.08 [0.88, 1.33], **P = 0.467**) … extended to all five cancers it was null in three, nominal in LUSC and **protective only in KIRC (0.79 [0.67, 0.94], q = 0.037)** … **so ω is not a pan-cancer prognostic marker**”；`si.txt:274` “the single KIRC protective signal is **exploratory and requires independent-cohort validation**”“LUSC … P = 0.048 did not survive five-cancer FDR (**q = 0.12**)”“the KIRC model’s **GLOBAL proportional-hazards violation (cox.zph P = 9.6 × 10⁻⁴)** was driven by stage”；`si.txt:112` “the same construction is used for the ω, k_f and k_n survival exposures with **m = 5 per exposure**, and the **algebraic dependence of the three is disclosed**”；`si.txt:154` “n = 272 tumors with complete covariates, **79 events**”；`tables_overview.txt:95` “No exposure reaches significance (all P ≥ 0.39), so the pan-cancer reversal is a **descriptive property of tissue-state divergence, not a prognostic marker**”。
- **问题**：就“生存/临床价值是否被过度声称”而言，稿件**没有过度声称**，且 KIRC 做了 PH 检查、tt 变换与 epoch-split，处理规范。不足：主稿未写 “exploratory / requires independent-cohort validation”（仅 SI 有），且 ω/k_f/k_n 三者代数相关却按各 exposure family 内 m=5 分别 BH，未说明 15 个 Cox 检验的联合多重性策略；LIHC 79 events 偏少、仅 OS 未做癌种特异生存/DFS。
- **修法**：主稿补 “exploratory, requires independent-cohort validation” 与 GLOBAL PH 违反说明；Statistics 段明确跨 exposure 多重性处理；补事件数与仅 OS 的限制。

### P2-4｜跨文件数值口径不一致；临床严重度梯度的定位需再降一级

- **位置与引文**：`ms.txt:47` “RIN (GDC) correlated only weakly and sign-inconsistently with k_n (**|ρ| ≤ 0.27**), and the NN/TT k_n ratio was unchanged at both-endpoint RIN ≥ 7 (0.299–0.448 → 0.304–0.440)”；`si.txt:280` “all **|ρ| ≤ 0.21**”“ω showed the same sign heterogeneity (|ρ| ≤ 0.21)”。`ms.txt:49` “tumor k_n is **2.0–2.8-fold** higher”；`guide.txt:396` “tumor k_n is **2.0–2.7-fold** higher”；`si.txt:123` “leaves a **2.0–2.7-fold** elevation”。`ms.txt:47` LIHC Cox “P = 0.467” 对 `si.txt:274` “1.08 [0.88, 1.34], P = 0.461”。临床严重度：`tables_overview.txt:176` “All P-values are **nominal (no multiplicity correction)**; every gradient is **denominator-dominated**, as shown by the parallel k_n trends”；`guide.txt:281` “LIHC Edmondson gradient **reverses under k_f-only** … BRCA PAM50 ordering **largely reverses under k_f-only** — predominantly a k_n baseline effect”；`ms.txt:46` “stratifications beyond LUAD are **denominator-dominated vignettes**”。
- **问题**：RIN 上限 0.27（主稿）与 0.21（SI）、GTEx 倍数 2.0–2.8 与 2.0–2.7、LIHC Cox P=0.467 与 0.461 均未标注口径差异（per-sample vs pair-level min-RIN；adjacent-referenced vs GTEx-re-referenced；published LIHC Cox vs PanCanAtlas continuity）。Edmondson/PAM50 梯度在 k_f-only 下反转、P 为 nominal、denominator-dominated，若被读作“与分级/分型相关”会构成临床声称外溢。
- **修法**：统一数值并在图注/脚注标注口径；在 Table 15 与主稿明确这些梯度是 k_n-baseline 的描述性 vignette，不构成临床分级/分型关联，且不作 multiplicity 校正后的推断。

## 四、优点

1. **统计与可复现性披露极为充分**：`si.txt:112` 的 claim-to-test map 逐条给出检验、检验族与 primary/exploratory；cluster bootstrap、two-way cluster-robust 与 wild-cluster、paired DeLong、cox.zph + tt(x)/epoch-split、B 分辨率与 Monte-Carlo error、anti-conservative 处自承一应俱全；`guide.txt` 提供 SHA-256 manifest、superseded 文件清单、spot_check 46 assertions 与 7 项回归测试，`ms.txt:115–116` 主动披露 LLM 使用。
2. **对核心局限主动、反复、量化地自我设限**：56% 标为 “unmeasured-reference upper bound” 并给 δ 网格（56%→42%→28%）、“honest reading is about half”、“descriptive, not a causal mediation proportion”（`ms.txt:47`, `si.txt:277`）；KRAS 固定面板 “Δω +2.6, P = 0.089” 与 “not a robust finding / dominated by pairwise selection”（`si.txt:157`）；AUC 0.648 < DE 0.841 与 “make no sample-level discrimination claim”（`si.txt:157–158`）；“not a pan-cancer prognostic marker”（`ms.txt:47`, `si.txt:274`）。
3. **混杂控制覆盖面广且方向诚实**：ESTIMATE admixture、四 panel marker composition（并主动补加 myeloid panel）、high-purity-half、reference-free NNLS deconvolution fallback、GDC RIN、GTEx 跨队列、Note 24 的 DEF-EL/DEF-CV 双独立 anchor；同时明确承认 “marker panels are noisy proxies … neither can a marker-panel regression exclude composition as the driver”（`si.txt:216`）、GTEx “unresolved for the other four”、KIRC 不推断。
4. **因果与泛化边界总体克制**：`si.txt:121` “preclude causal inference from bulk-level data alone”、`ms.txt:74` “five cancer types make the results exploratory”、`ms.txt:47` “report all TCGA findings as tissue-level divergence at bulk resolution”；把 ω 定位为 “studentized null model / heuristic index, never as evidence of positive selection”（`ms.txt:66–67`），并把 brain 候选明确为 “hypothesis list, not a discovery set”。

## 五、给编辑的备注

**是否可送外审：可送外审，本轮意见即以外审标准给出；不建议 desk reject，也不建议在声称收敛前进入接受流程。** 若组织复审，建议优先邀请（i）癌症基因组学 / bulk RNA-seq 纯度与反卷积混杂、（ii）生物统计（measurement-error、mediation、cluster/dyadic inference）两类背景的审稿人；并明确要求作者把 δ 敏感性主表与 unmeasured-reference 限定移入主稿，而非仅留在 SI。

**临床/转化声称是否需要进一步降级：需要，且是本大修的核心条件。** 具体：(a) cover letter、Abstract、Fig 3/graphical abstract 的 56% 归因统一加 “under an assumed CNA-free normal reference / unmeasured-reference upper bound”，并改成 “≈ half” 与 δ 网格并列；(b) “pan-cancer” 改为限定五癌种并写明 exploratory；(c) GTEx “rather than / over a field effect” 降为 “cannot resolve at this cross-cohort tolerance”，把 “normal-tissue level rank-inverted (ρ = −1.00)” 的分母驱动结论写入主稿；(d) 全文明示无任何预后、诊断或分型增量——ω 不优于常规 DE、`not a pan-cancer prognostic marker`、临床严重度梯度为 denominator-dominated vignette、KRAS 为 group-level association；(e) 删除 “genomic instability creates” 一类因果动词，统一为 “associated with / co-directional with”。稿件自己也把产物定位为 “**a caution** for HK-anchored normalization in bulk tumors”（`cl.txt:3`）与 “a **checkable caution** … at the level of the denominator”（`ms.txt:16`），面向编辑的表述应与这一定位一致。

**附：指定核查点逐项结论**（供编辑/主审快速对照）
1. “at most 56%” 上界表述 — 正文/摘要/SI **诚实**；不足在 cover letter 未携带假设、pooled CI 未传播 δ 与跨癌种异质性（P1-2）。
2. unmeasured-reference 假设 — **已明确披露**且标注 “an assumption that dominates the estimate”；但仅肿瘤 aliquots、LIHC 89% [41,193] 不稳定、KIRC 44% 覆盖，normal CNA 未测量（P1-2 / P1-5）。
3. AUC 0.648 / DE 0.841 的 group-level 限定 — Intro/Results/SI/cover letter **限定正确**；唯 Abstract 未携带（P2-1）。
4. 固定面板与 group-mean only — SI **极其诚实**（“not a robust finding / dominated by pairwise selection”）；主稿位置偏弱（P2-2）。
5. GTEx 跨队列偏移与正常组织异质性 — **已量化并标 descriptive/unresolved**；主稿 “rather than a field effect” 超出分辨力（P1-3）。
6. 生存分析/临床价值 — **无过度声称**（明确 not prognostic、KIRC 标 exploratory + 需独立队列）；主稿未写 exploratory 与跨 exposure 多重性（P2-3）。
7. 肿瘤纯度与组成混杂 — 控制覆盖广且自承代理局限；主稿 “coefficient unchanged” 偏肯定，未明说“不能排除 composition as driver”（P1-5）。
8. bulk vs pseudobulk 口径 — 主稿/SI **明确 bulk resolution / 无 pseudobulk**；但 `guide.txt:135` 与 `si.txt:62` 术语自相矛盾（P1-5 / P2-4）。
9. 五癌种泛化边界 — 自承 exploratory、LIHC CI 含 1、mapping-sensitive、绝对 ω 不跨 pipeline 可比；但通篇 “pan-cancer” 泛化（P1-4）。
10. 相关性写成因果/驱动效应 — **整体极克制**（preclude causal inference、group-level association rather than a confirmed driver effect）；残留 “creates” 与自身 “descriptive, not a causal mediation proportion” 冲突（P1-1）。
