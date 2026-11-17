# CKI (Nature Communications) — 专家团盲审与打分报告

- 送审版本：根包 `CKI_Submission_NC/`（commit b5ed24d → squash 5cda8a8；zip 21 条目、14,653,370 B、sha 893045b1）
- 稿件规模：正文 5,000 词 / 摘要 145 词 / 4 主图 / SI Note 1–24、Fig 1–9、Table 1–17 / Methods 5.1–5.14
- 审稿方式：6 位独立审稿人（互不可见，各自读正文并要求按需检索 SI）+ 1 层主编事实核查
- 评分口径：6 维度各 1–10（可 0.5），总分 1–10；建议 Reject / Major / Minor / Accept

---

## 1. 评分总表

| 审稿人 | 身份 | 新颖性 | 理论严谨 | 统计严谨 | 证据充分 | 表达清晰 | 影响力/NC | **总分** | 建议 |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 单细胞方法学与基准测试 | 7.0 | 6.5 | 6.0 | 6.5 | 6.5 | 6.0 | **6.5** | Major Revision |
| R2 | 统计推断 | 7.0 | 7.0 | 6.5 | 6.5 | 7.0 | 6.5 | **6.5** | Major Revision |
| R3 | 癌症基因组学 / 临床转化 | 6.5 | 6.0 | 5.5 | 5.0 | 6.0 | 4.5 | **5.5** | Major Revision |
| R4 | 分子演化（Ka/Ks） | 6.5 | 5.5 | 6.0 | 6.5 | 5.5 | 6.0 | **6.0** | Major Revision |
| R5 | 脑图谱 / 神经科学 | 6.0 | 5.5 | 5.5 | 5.0 | 5.5 | 5.0 | **5.5** | Major Revision |
| R6 | 期刊编辑 / 可复现性 | 6.0 | 8.0 | 8.5 | 6.0 | 5.5 | 6.0 | **6.7** | Major Revision（可送审） |
| **均值** | — | **6.5** | **6.4** | **6.3** | **5.9** | **6.0** | **5.7** | **6.1** | **6/6 Major** |

> 6/6 明确 Major Revision，0 接受，0 拒稿；总分 5.5–6.7，**均值 6.1**。分维度的共识很清楚：**理论与统计是强项（6.3–6.4），证据充分性（5.9）与影响力/NC 契合度（5.7）是短板**——问题不在"做得对不对"，而在"值不值得作为 NC 的卖点"。
> R6 的编辑初筛意见为"可送审，但 data/code 版本必须先纠正"，并给出"P0 修完即可投"的判断。

---

## 2. 主编事实核查（独立复核，11 条硬证据）

| # | 位置 | 问题 | 证据 | 处置 |
|---|---|---|---|---|
| F1 | 摘要 vs SI 3.13 | 摘要称 "the k_f/k_n decomposition separates KRAS-mutant from wild-type tumors after purity adjustment"；SI 明写该对比固定面板下 **Δω +2.6, P = 0.089**，结论 "**not a robust finding**" | SI 3.13；Cover letter 亦自承 fixed-panel P = 0.089 | **摘要必须降级**：仅 KRAS–EGFR 在固定面板存活（+6.1, P = 0.005），KRAS–WT 面板敏感 |
| F2 | Fig. 2e 图注 | 仍写 "paired **McNemar comparisons** in Supplementary Tables 3a and 4"，而正文/SI 已删除全部 exact McNemar P，改为区间口径 | manuscript L196 vs SI 3.12 | 图注改 "paired differences with library-clustered intervals" |
| F3 | Code availability | 正文三处写 **tag v0.5.6**，远端仓库只有 **v0.6.0**（`git ls-remote --tags` 仅 `refs/tags/v0.6.0`）；且 v0.5.6 快照不含 nc78/nc80 脚本 | `git ls-remote --tags origin`；R6 独立核验 | **NC 政策红线**：补 tag 或统一改版本，并确保该 tag 含全部脚本 |
| F4 | Reproducibility Guide | 指南完全未覆盖 nc80 三项新增分析（10x modular TPR、Mahalanobis、library-clustered 区间/CNA share v2），SI 已引用三个脚本 | 三个脚本在 SI 各 1 次、guide 各 **0** 次 | 指南补 3 条链路（脚本→输入→输出→预期值） |
| F5 | Results L48 | 句首小写："…nor uniformly creates the elevation. **under** the authoritative…" | 原文字符串 | 改大写 |
| F6 | 摘要 vs 正文 | 摘要 "about half of **this reversal** is attributable to CNA (56%, 46–66%)"；正文口径是 "56% of the **TT/NN k_n gap**"，正常组织 CNA≈0 假设下为 **42% (34–50%)**；逐癌异质性极大（LIHC 89%、KIRC 42%） | 正文 L49；`results/nc80_cna_share_v2_report.txt` | 摘要改为 "56% of the housekeeping-divergence gap (42% under a conservative normal-CNA assumption)" |
| F7 | Fig. 4f vs Results | Results 用**均值** 63.5–69.3，图注用**中位数** 59.3–64.2，同一 2,995 对两口径并列而未标注 | L56 / L200 | 标注 mean / median |
| F8 | 摘要 "eightfold" | 未标明是小鼠还是脑；Discussion 自承 "mouse only 1.7-fold" | 摘要 vs L66 | 补 "in the brain atlas" |
| F9 | figure3.pdf | 成品宽 **205.7 mm**，超 NC 单页上限 180 mm | MediaBox 582.96 pt | 缩至 ≤180 mm 重排 |
| F10 | figure2 / figure4.pdf | figure2（178 mm）含 4.9/5.6/6.3 pt 字；figure4 MediaBox **441.2 mm** 宽、字号 4.9–9.0 pt ⇒ 按 180 mm 排版有效字号 **2–3.7 pt**，远低于 7 pt 下限 | 逐 PDF 解流统计 `Tf` | figure4 需重制；figure2 小字上调 |
| F11 | Methods L110 | 引用 `SourceData/Figure3/corrected_20261031/cnv_recovery/posthoc_component_associations.csv`，该路径在仓库根**不存在**（仅存于 `results/audit/_nc78_*` 暂存目录与旧 fourth 包） | `find . -name posthoc_component_associations.csv` | 改指仓库内实际产物或补入 SourceData |

**核查通过项**：摘要 145 词、正文 5,000 词整、SI 17 表与 xlsx sheet 数一致、CNA 单模型 56%[46,66] 与联合模型 40%+2% 可复算、HK 面板 1,130 行与 HRT 一致、figure1 170 mm / figure2 178 mm 在版心内、supp fig 全部 178 mm。

---

## 3. 六位审稿人意见（去重前）

### R1 — 单细胞方法学与基准测试：**6.5 / Major Revision**

**Major**
1. **基准胜负不支持"更优"**：10x 上 ω 配对检出率 35–66%（raw JS 97–100%），池化 AUC 0.507–0.534（k_total 0.564–0.634）且无 δ 单调性；Fig. 2d 的 AUC 0.80 来自 SmartSeq2 深测。⇒ 主文须写明"背景特异、以灵敏度换特异度"。
2. **锚点在疾病态失效**：IFN-β 使 k_n 升 1.2–5.7 倍、CD14+ 单核 ω 掉到 0.55；TCGA 的"逆转"本身就是锚点漂移。⇒ 需要一个"锚点是否可信"的前置判据。
3. **k_f 的 per-pair top-200 循环选择**：circularity 使 k_f 中位膨胀 1.61 倍，绝对 ω 是上界、分档阈值不可迁移。⇒ leave-pair-out（ρ = 0.937）应上主文。
**Minor**：pseudobulk 聚合顺序无操作规则；"≥1 CPM"与 per-1e4 归一化关系需写明；补 ambient RNA/doublet 讨论；ROC 未标操作点；marker Jaccard 出现太晚。
**只改三处**：摘要加"背景特异"；补锚点判据；circularity 上主文。

### R2 — 统计推断：**6.5 / Major Revision**

**Major**
1. **CNA 的 56%（46–66）只是 δ = 0 抽样误差下的区间**：同一次 bootstrap 下改用 δ = 0.05 时为 **42%（34–50）**、δ = 0.10 时为 **28%**；联合模型为 **40% [30, 51]**；LIHC 单癌区间 **[41, 193]** 不可识别。⇒ 摘要不能写 "about half"，应按区间/上界表述，并明确"normal 组织 CNA 残差距离"这一假设主导了逐癌差异。
2. **比率偏倚残差 ≈ 10% 被低估**：Note 4 写"calibration absorbs ratio bias"，但数据显示 bias 在 null 处为 **−8.3%**、在观测对上为 **+1.5%**；只有当观测对与 null 的 k_n 尺度相当时校准才真正吸收偏倚。⇒ 必须在正文 L30 写入"剩余 ≈10% 比率偏倚，靠经验校准吸收而非理论消除"。
3. **TCGA 聚合层检验不可识别**：5 个癌型中 3 个的聚合 k_n 落在分母下限，聚合 ω 退化为 k_f 的常数缩放；固定面板零分布又是 anti-conservative，故 "P > 0.9" 既不能支持也不能否证。⇒ 删除这些 P 值，全部改走 pair 级 cluster bootstrap（正文 L87）。
4. **AUC 0.80 是背景与 δ 范围特异的**：摘要级数字来自 δ ∈ [0.25, 2]；同文自己在 10x 上得到池化 AUC **0.507–0.534**（k_total 0.564–0.634）、配对检出率 **35–66%**。⇒ 该句必须在 Results 就地加限定，不能只写在 SI 3.11。
5. **Note 14 的轴富集 P 是 post-selection**：ω 已经被该方法筛过再算富集 P，L64/L73 的 "thalamo-temporal orientation" 叙事应删除或标 "illustrative"，除非给出全 27 个检验。
6. **"39 个 Strong vs 期望 148.3，P ≤ 1.0×10⁻³" 的正确解读是"耗竭"**，即数据拒绝"候选集是强随机超集"，而非"筛选发现异常相似配对"。⇒ Fig 4c–d 图例需明写"individual entries have no statistical support"，正文不得同时用 depletion 与 candidate discovery 两种叙事。

**Minor**
- two-way cluster 方差 **V_a+V_b−V_ab 未做半正定检查**（可能为负）；4 名供者 = 4 个 cluster 的 wild-cluster bootstrap 值得补。
- "八倍"未标是小鼠还是脑（小鼠仅 1.7 倍；"IQR/median" 口径是 64 倍）。与 F8 合并处理。
- Note 7 用 global-HVG 方案得到 ω = 1.30，与主文不是同一尺度，引用时需声明。
- α 的 "1.65–2.2 倍" 中 2.2 倍请给出来源；正文只给区间。
- SI 表 2a 用 raw DeLong P = 2.4×10⁻¹⁷，正文未说明是否 Holm（标题写 "Holm-corrected"）。
- Note 4 可补引小 k_n 处的稳健性（原文 6.52）。
- 类级与配对级两个家族应声明为 **pre-specified, independent**，否则 multiplicity map 的说法自相矛盾。
- L29 写 "~400-fold"，实际 k_f 是 **~420 倍**（0.0015 → 0.63–0.68）。

**R2 亲手核对并确认的数字**：`nc80_cna_share_v2.csv` 的 δ = 0/0.05/0.10 份额（55.6/41.7/27.9）；`nc80_cna_joint_model.csv` 的 39.6% CNA + 2.0% composition；600 行 ratio-bias 表的 null −8.3% vs 观测 +1.5%；`nc80_t1_library_null.csv` 的 28.6% / 10.3% / 4.8%；`nc49_brain_drift_ladder.csv` 2,161 T1 对；四个脚本路径与正文引用一致。

**总评**：**披露体系属高标准，统计骨架无致命伤**。Major 1 / 2 / 5 涉及"主张强度 > 证据强度"，改后可收。

### R3 — 癌症基因组学 / 临床转化：**5.5 / Major Revision**

**Major**
1. **"逆转"主要是分母 artifact**，把它写成 cautionary finding 贡献偏薄；对癌症读者的可操作价值必须写实（"HK 归一化在肿瘤中不可靠"这一条）。
2. **bulk 上的循环选择**：per-pair top-200 在同一对样本内选基因，k_f 在 bulk 的膨胀可能更大；固定面板敏感性对 KRAS–WT 是致命的（P = 0.089）。
3. **纯度校正是线性加性、ω 是比值**：ESTIMATE 调整方式与 log 比值不匹配；建议补 log-ratio 上的协变量调整或倾向评分分层。
4. **CNA 归因假设 normal ≈ 0**：无正常组织 CNA 谱，56% 应给区间与敏感性（已有 42%），摘要不得只报 56%。
5. **临床价值为负**：预后三癌无效、KIRC 保护、KRAS AUC 0.648 低于简单 DE 投影 0.841（DeLong P = 0.002）。⇒ 癌症部分不应作为摘要卖点，建议降为一节 + 明确"group-level only"。
**Minor**：32 个细胞系样本剔除需给完整 barcode 清单（已在 SI 5.3）；LUAD 吸烟混杂已调整但 pack-year 仅描述性；建议补 CNA-based 归一化对照；PAM50/Edmondson 分层应标注 exploratory。
**最该降级**：KRAS 分层与预后两段；建议从摘要删除 KRAS 句。

### R4 — 分子演化（Ka/Ks）：**6.0 / Major Revision**

**Major**
1. **Ka/Ks 是修辞而非推导**：Ks 近中性、dN/dS = 1 有群体遗传学零假设；HK 不是中性位点，α（7.70）替代理论零点使绝对阈值失效。⇒ 弱化命名或在 Introduction 明写"三处失效"。
2. **理论保证被自己的数据推翻**：Prop 4 仅在 ω > 2α = 19.46 成立，而 30.3% 的脑配对与全部 39 个 Strong 候选都不满足。⇒ 必须承认"筛选落在保证之外"。
3. **α 是主导误差却不可迁移**（跨数据集 1.65–2.2 倍），仍被用作 ω_cal = ω/7.70 的标度。⇒ 给 α 不确定度传导，或取消 ω_cal。
**Minor**：术语需定义；McDonald–Kreitman 第四项只提不用；"绝不解释为正向选择"应上移 Introduction。
**一句话**：命名可保留，但"heuristic"必须进摘要首句。

### R5 — 脑图谱 / 神经科学：**5.5 / Major Revision**

**Major**
1. **梯度被自己的控制削弱**：原始 6.10 → span-matched 3.66–3.68；ρ(ω, k_n) = −0.73 vs ρ(ω, k_f) = 0.09。⇒ 标题级主张应改为"housekeeping-anchored 类间差异"，不用 "differentiation gradient"。
2. **4 名供者 / 31,764 伪配对**：donor-stratified null 只剩 3/10 类存活（ependymal q = 0.052）。⇒ "3/10"必须进 Results。
3. **神经元超类依赖 HK 列表**：data-driven low-CV 面板下 P = 0.95/0.87/0.76 ⇒ 结论强度降为 panel-dependent。
4. **"低于期望"解释过度**：39 vs 148.3 可能是模型/零分布失配，不是 depletion。⇒ 删生物学解读，只保留"无候选过 FDR"。
**Minor**：PMI/RIN 不可得需明写；Fig. 4 六面板过密；residence/migration 阴性结果可移 SI。
**保留/降级**：保留为独立结果，但把"梯度"降级、候选清单整体移 SI。

### R6 — 期刊编辑 / 可复现性：**6.7 / Major Revision（可送审）**

**编辑初筛**：**可送审**——4 张主图、5,000 词正文、Note 1–24 + 17 表 + Reproducibility Guide 的完整度达到 NC Article 的送审门槛；但 **data/code 版本必须先纠正**，否则按政策退修（"declared version ≠ executed version"）。

**Must-fix（R6 原文，6 条）**
1. **Tag 内容不符**：`v0.5.6` 快照不含论文关键脚本（nc78 五癌 Cox、nc80 的 CNA share / library-clustered 区间），Zenodo DOI 也解析到 v0.5.6（2026-10-11）。⇒ 这些分析在声明的归档中不可复现。
2. **Methods 路径失效**：L110 的 `SourceData/Figure3/.../posthoc_component_associations.csv` 在仓库根缺失；同段把 `scripts/nc80_cna_share_v2.py` 写在 `notebooks/` 下。
3. **Guide 与正文/SI 版本不一致**：Guide 写 `notebooks/nc80_cna_share_v2.py`，实际在 `scripts/`。
4. **图 2e 图注仍称 "paired McNemar comparisons"**，而 SI 3.12 已改为库聚类区间。
5. **摘要 overclaim**：(a) "about half of this reversal is attributable to CNA" 的 "reversal" 前后有两种含义（NN/TT 的 ω 比值 vs TT/NN 的 k_n 差距）；(b) "tentatively" 被放到括号里；(c) 单独强调 "56%，95% CI 46–66%" 而不提 42%（34–50%）的敏感性，CI 上界又截在 0.66 而非 0.67。
6. **figure4 441 mm / 4.9–9 pt** 不满足 7 pt。

**可复现性抽查（本轮实测，可复核）**
- Guide 目录结构 1.1–5.14 完整，每节含"脚本 → 输入 → 输出 → 预期值"，`08c_brain_bootstrap_v3.py` 与 `08d/08e` 权威产物在 Guide 中可定位。
- CNA 份额复算：`nc80_cna_share_v2_report.txt` 的 pooled δ = 0 为 **55.55% [45.78, 66.35]**，与正文 56% [46, 66] 一致。
- Kang 技术重复复算：30 对，ω 超限 **0/30**、raw JS **11/30**、cosine **7/30**，cal_omega 中位 **0.963**，与 Fig. 2e 及 SI 3.12 一致。
- 版本快照实测：`v0.5.6`（2026-10-11）树中 nc75–nc80 脚本数 **0**，`v0.6.0`（2026-11-16）为 **25** ⇒ 论文所报的分析确实不在声明版本内。
- 包结构：4 主图 + 9 附图；SI 17 表对应 xlsx **17 个 sheet**，全部对齐。
- 差距：Guide 未覆盖 nc80 三项分析（F4），Methods 的 SourceData 路径失效（F11）。

**Must-fix 文本修正（摘要）**：① "reversal" 二义性；② "tentatively" 位置；③ 56% vs 42% 的双口径；④ CI 上界 0.66→0.67 与下界 0.46→0.45 的四舍五入不一致；⑤ "group means" 措辞（与 AUC/单样本分离度区分开）；⑥ 摘要中"seven metrics"未交代是哪七个。

**一句话结论**：写作与规范达标，问题集中在"声明的版本 ≠ 实际跑的版本"——所有 P0 修完即可投稿。

---

## 4. 去重后行动清单

### P0 — 投稿前必改（不改会被 desk-reject 或首轮即退）

| # | 动作 | 来源 | 工作量 |
|---|---|---|---|
| 1 | 摘要 KRAS 句降级（只留 KRAS–EGFR 固定面板存活 + group-level 限定） | F1 / R3 / R6 | 30 min |
| 2 | 代码可用性：打含 nc78–nc80 脚本的新 tag，更新 Zenodo 与三处版本号；或补推 v0.5.6 | F3 / R6 | 1–2 h |
| 3 | Guide 补 3 条 nc80 链路 | F4 / R6 | 1 h |
| 4 | figure4 重制到 ≤180 mm、≥7 pt；figure3 缩到 180 mm；figure2 小字上调 | F9 / F10 / R6 | 2–4 h |
| 5 | Fig 2e 图注改区间口径 | F2 / R6 | 10 min |
| 6 | 修 Methods 失效 SourceData 路径 + Guide 里 `notebooks/` vs `scripts/` 的版本号错位 | F11 / R6 | 30 min |

### P1 — 首轮 major 的核心（改叙事为主，多数不需新数据）

| # | 动作 | 来源 |
|---|---|---|
| 6 | 摘要/Results 明确 "ω 的优势是背景特异、以灵敏度换特异度"，写入 10x 与 k_f/raw JS 胜出的数字 | R1 / R3 |
| 7 | 新增"锚点可信性判据"（k_n 是否落在 null 尾部、是否随技术协变量），并入 Discussion 的 practical rules | R1 |
| 8 | 把 leave-pair-out（ρ = 0.937）与 circularity 1.61× 从 Note 9 提到主文；绝对 ω 标注为上界 | R1 / R4 |
| 9 | 脑部："梯度"改为"k_n 主导的类间差异"；"3/10 类存活"进 Results；候选清单移 SI | R5 |
| 10 | CNA 归因写明 normal-CNA≈0 假设 + 逐癌异质性（LIHC 89% / KIRC 42%）+ 42% 敏感性 | F6 / R3 |
| 11 | 明确"39 个 Strong 候选落在 ω > 2α 保证之外"，并说明含义 | R4 / R5 |
| 12 | 图 3b–d（KRAS 分层箱线）移入 SI，正文改为一段文字 + 一个汇总统计 | R3 |
| 13 | 给 "~100 cells / ~50–200 operating window" 的建议补生成假设（median UMI 1,301、六细胞类型），并说明 >500 细胞组外推风险 | R3 / R1 |
| 14 | 删除或标注 TCGA 聚合层不可识别的 P 值（3/5 癌型 k_n 在 floor，P > 0.9），只留 pair 级 cluster bootstrap | R2 |
| 15 | 正文 L30 写明"剩余 ≈10% 比率偏倚由经验校准吸收、非理论消除"（null −8.3% vs 观测 +1.5%） | R2 |
| 16 | 补 two-way cluster 方差的半正定检查；4 供者 = 4 cluster 的 wild-cluster bootstrap 作为对照 | R2 |
| 17 | Note 14 的轴富集 P 是 post-selection：删除 "thalamo-temporal orientation" 叙事或标 illustrative（除非给全 27 个检验） | R2 |
| 18 | Fig 4c–d 图例明写 "individual entries have no statistical support"；正文不得同时用 depletion 与 candidate discovery 两种叙事 | R2 / R5 |
| 19 | 声明类级与配对级两个家族为 pre-specified、independent（否则 m5 的 multiplicity map 说法自相矛盾） | R2 |

### P2 — 表述与一致性

20. 摘要 "eightfold" 标 brain（F8；小鼠仅 1.7 倍，"IQR/median" 口径 64 倍）；21. 神经元 mean/median 标注（F7）；22. 小写句首（F5）；23. 术语定义（neutral / constraint / functional divergence）；24. "heuristic" 进摘要首句；25. "~420-fold" 与 "~400-fold" 统一；26. DeLong P 标 raw 还是 Holm；27. Note 7 的 global-HVG ω = 1.30 引用时声明不同尺度。

---

## 5. 结论

**当前状态不建议直接投 NC。** 六位审稿人一致给 Major Revision（6/6），没有一位接受；总分 5.5–6.7，均值 **6.1**。分维度看，理论与统计是强项（6.4 / 6.3），**证据充分性（5.9）与影响力/NC 契合度（5.7）是短板**——也就是说：方法本身站得住，但"这篇文章该不该在 NC 出现"没有被说服。

核心问题不是数据不足，而是**叙事与自身证据不一致**：SI 已经诚实写下"KRAS–WT 不是稳健发现""梯度是 k_n 主导""锚点会漂移""CNA 份额在 δ = 0.10 时降到 28%"，但摘要与标题仍按"能分离 KRAS""resolves gradients""baseline-normalized index"来写。审稿人不会接受"正文承认、摘要不承认"的组合。R2 的总评最克制：**"披露体系属高标准，统计骨架无致命伤；三条 Major 都是主张强度超过证据强度"**。

**最小可行修复路径（估计 1–1.5 天）**：先做 P0 六项（tag 内容、figure4、失效路径是政策/生产硬伤），再把 P1 的 6/9/10/14 四条叙事改写落地——把论文重新定位为"一个可检验的、以分母为核心的诊断式指数 + 一份诚实的边界清单"，而不是"优于现有度量的新方法"。代价是标题与摘要语气降一档，收益是 6 位里至少 4 位会转 Minor。

**若目标是先拿一个 accept**：另一条路是把脑图谱部分整体压缩成 SI、把 TCGA 部分做成主结果（"HK 归一化在肿瘤中的失效"是一个干净、可检验、有临床意义的警示），主体从"新指数"转为"归一化陷阱的量化"。R3 认为这条路对癌症读者更有价值，R5 也承认脑部分"k_n 主导"难以支撑标题级主张。

---

## 6. 修复回执（nc81 落地，commit 38c2659 / squash 1d71495 / tag v0.6.1）

### 已完成

| P0 | 状态 | 落地内容 |
|---|---|---|
| 1 摘要 KRAS 降级 | ✅ | 摘要改为 "KRAS-mutant tumors exceed wild-type group means after purity adjustment but not under a fixed panel (P = 0.089; AUC 0.648)"；同时补 CNA 42% 敏感性、"precision, not specificity"、脑梯度 panel-dependent；摘要 **150 词**（限 150） |
| 2 代码版本 | ✅ | 正文三处 + Guide 三处 → **v0.6.1**；新 tag `v0.6.1` 已推送，含 64 个 nc75–nc89 脚本（10x modular、Mahalanobis、library-clustered 区间、CNA share v2 全在内）；Zenodo 文案改为"最新归档版本 + v0.6.1 归档随投稿" |
| 3 Guide 补链 | ✅ | 新增 **Section 5.14 nc80 Analyses**，三条链路（脚本 → 设计 → 输出 → 预期值） |
| 4 图幅 | ⚠️ 未完成 | 建立 `scripts/check_figure_spec.py`；实测 **0/13 通过**：figure1 最小字 4.0 pt、figure2 3.9、figure3 205.7 mm + 4.4、figure4 441 mm + 4.9；9 张附图 2.8–6.0 pt。所有图均需按 ≥7 pt 重绘 |
| 5 图注 McNemar | ✅ | 改为 "paired differences with library-clustered intervals in Supplementary Tables 3a and 4" |
| 6 失效路径 | ✅ | Methods → `results/nc78_posthoc_component_associations.csv`（文件已入库）；"elevation. under" → "Under"；神经元均值/中位数分列 |

### 复核（修复后）

- build **231/231**；ms_verify **130/130**；si_verify **120/120**；cl_guide **45/45**；XV8 **64/64**；_nc80_mj_crossval **137/137**；pytest **29/29**
- 字数：MAIN **4,996**（≤5,000）、摘要 **150**、CL **530**（≤530）
- zip 21 条目 14,654,613 B，与根包 21 个散文件逐 sha256 相等
- 远端：main = `1d71495`，tag `v0.6.1` = 同一提交

### 仍未做的（P0-4 + 部分 P1）

1. **图重绘**：仓库内没有 Figure 1–4 的绘图脚本（v58 图由 `results/audit/_nc70_mainfigs.py` 以矢量带拼合，原始 panel 字号本就 4.9–6.3 pt）。要合规必须回到各 panel 的绘图环节以 ≥7 pt 重出，或用现有的 per-pair 结果 CSV 重建 Fig. 4。
2. **P1 叙事**：锚点可信性判据（R1-2）、leave-pair-out 上主文（R1-3）、CNA 正常组织实测（R3）、two-way cluster PSD 检查（R2）等需新增分析或新增小节，属"第二轮"。

---

## 7. P0-4 图幅：figure 4 重建（nc81b，tag v0.6.2；main 与 tag 为同一提交）

### 病根

`scripts/check_figure_spec.py` 按"有效字号 = 页面字号 × min(1, 180 mm / 页宽)"度量，
figure 4（旧 v58 figure6 拼接版）画布 **441 × 354 mm**，缩到 180 mm 后
**1,343 / 1,361 个字符落在 5 pt 以下**（2.4–3.3 pt），只有 18 个字符落在 5–7 pt、
**0 个**字符达到 7 pt。这不是"字小一点"，是整页不可读；矢量整体缩放无法修复
（文字相对数据本身就小），只能按数据重绘。

### 处置

新增 `notebooks/110_gen_fig4_nc81.py`，从权威结果表重绘六个 panel：

| panel | 内容 | 数据来源 |
|---|---|---|
| a | 解剖示意图 + 10 类细胞 | 重画（原图内 2–3 pt 解剖名不再带入，区域清单在附表 10–11） |
| b | 10 类平均 ω、6.10 倍梯度 | `results/brain_bs_null_ct_test.csv` |
| c | Strong 39 / Moderate 1,171 / Weak 5,381 | `results/nc79_a5_scheme_tiers.csv`（主方案行） |
| d | 五强候选 observed vs expected（res 0.196–0.213） | `results/brain_bs_null_observed_pairs.csv` |
| e | 三个神经元超类 block-shuffle 零分布（B = 1,000） | `brain_neuron_blockshuffle.csv` + `_null_means.npy` |
| f | 超类 vs 非神经类中位数 | 同上 + `brain_bs_null_ct_test.csv` |

脚本内自带 6 条断言（39/1,171/5,381/31,764、6.105 倍、res₀ = 0.1964），
数字与图注对不上会直接中断。

### 结果

- **180 × 214 mm，最小字号 7.0 pt，0 个 span 低于 7 pt**（原 2.4–3.3 pt）
- 图注同步两处：`59.3–64.2` → **`59.2–64.2`**（三个超类中位数 59.21 / 59.32 / 64.24），
  `a non-neuronal median of 24.5` → **`a pair-level non-neuronal median of 24.5`**
  （24.5 是 pair 级中位数，与 panel f 的"类内中位数的中位数 24.16"不是同一统计量，
  加 `pair-level` 消歧；SI 中 `62.2 / 24.5 / 73.4` 的口径不变）
- 构建改取 `results/figures_nc81/figure4.pdf`；代码版本 **v0.6.1 → v0.6.2**（7 处）
- 复核：build 231/231、ms 130、si 120、cl_guide 45、XV8 64、crossval 137、pytest 29
- zip 21 条目 11,427,171 B，与根包逐 sha256 相等
- 版式修正：面板标题改为单行（两行副标题用 `va='bottom'` 会串到标题上），(b)(d) 的注释语移除（图注已有），行距重排后无重叠

### 仍未完成的 12 张

| 图 | 页宽 mm | <5 pt 字符 | 5–7 pt 字符 | 说明 |
|---|---|---|---|---|
| figure1 | 170.0 | 6 | 115 | 4.0 pt 仅 6 字符，局部可救 |
| figure2 | 178.0 | 228 | 962 | 主体 5.6 pt，NC 5 pt 底线之上 |
| figure3 | 205.7 | 28 | 288 | **超宽 25.7 mm**，需缩到 180 或重排 |
| SF1 | 178.0 | 348 | 818 | 2.8 pt 起 |
| SF3 | 178.0 | 352 | 415 | 3.4 pt 起 |
| SF5 | 178.0 | 51 | 15 | 2.8 pt 起 |
| 其余 6 张 | 178.0 | 3–26 | 6–1,157 | SF8 已全 ≥6 pt |

这 12 张的共同点是"少量标注字过小"，与 figure 4 的"整页不可读"不同性质；
NC 的硬性下限是 5 pt，我们的内控下限是 7 pt。下一步按两个选项推进：
(a) figure3 先解宽度硬违规（205.7 → 180 mm）+ 局部补字；
(b) SF1/SF3 因 <5 pt 字符达 350 量级，需回到各自的 panel 重出。
