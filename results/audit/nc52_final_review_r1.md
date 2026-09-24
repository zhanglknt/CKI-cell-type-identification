# R1 统计方法学终审（nc52 final review，commit 7133b43）

审稿人：R1-stats（排列检验、校准、自助法区间、FDR、零模型设计、聚类感知推断）
审查对象：results/CKI_Manuscript_NC.docx、results/CKI_Supplementary_NC.docx、results/CKI_Supplementary_Tables_NC.xlsx（sheet 清单核对）、正文表
方法：所有指控均对照 results/ 下 ground truth 输出文件复核（nc52_stats_*、nc52_tcga_*、nc52_brain_*、nc52_gtex_*）。

## 一、上轮 Major 修复核验（全部通过，附 ground truth 依据）

| 上轮问题 | 修复 | ground truth 核验 |
|---|---|---|
| M1 7.70 CI 伪重复 | two-stage population-resampled bootstrap 95% CI [6.38, 9.82]（B=5,000），旧 [7.37, 8.02] 在 MS（Calibration 段、Statistics 段）与 SI 3.10/Note 3 明文标注 pseudo-replicated 并退役；ω_cal 声明 ~1 位有效数字 | nc52_stats_baseline_twostage_bootstrap.json：two_stage_ci95=[6.3798, 9.8184]，另附 6-群体 t 区间 [5.18, 10.21] 与 LOPO 6.75–8.08，与稿面一致 |
| M2 脑梯度伪精确 CI | 组合对照 3.66 为主口径（donor CI [1.92, 3.78]，LODO 全 >1）；equal-n 1.74 降级为敏感性分析（donor CI [0.80, 2.34]，12.6% 复制品 <1，如实披露） | nc52_brain_gradient_donor_bootstrap.json：combined 3.6597 [3.598, 3.705]、donor CI [1.918, 3.779]、equaln donor CI [0.804, 2.336] frac_below_1=0.126、span 3.28 [1.67, 3.97]，全部一致 |
| M3 AUC CI 方法缺失 | DeLong 95% CI [0.770, 0.838]；摘要措辞改为 "best discrimination at bounded power"；正文新增 rank discrimination 与 thresholded power 分化的披露（marrow δ=1 AUC 0.85 vs 检出 0/150） | nc52_stats_auc_ci_methods.csv：DeLong [0.7703, 0.838]、module-seed cluster bootstrap [0.7706, 0.8363]、固定特异度敏感性（95% 特异度下 ω 灵敏度 0.273）、分背景 δ=1 功率列，数值与稿面一致（但见问题 P1 可追溯性） |
| M4 TCGA 反转推断 | kn_floor {0, 1e-5, 1e-4} 敏感性全同（frac at floor = 0）；正文声明 "floor never reached"；mapping 敏感性仅 LIHC（linear 1.11 [0.94,1.30] vs softmax 1.29 [1.09,1.53]） | nc52_tcga_knfloor_sensitivity.csv：linear/softmax × 5 癌种 × 4 floors，≤1e-4 比值恒等、地板触及率 0；1e-3 才变动（LUAD 2.464→1.494，52.7% NN 触底）——稿面对 1e-3 档未误导，仅未引用，可接受 |
| M5 Tabula P 值独立性 | entry-clustered bootstrap（99 entries，B=5,000）：ω vs JS −0.40 [−0.54,−0.23]、vs Spearman −0.46 [−0.58,−0.34]、vs cosine −0.39 [−0.52,−0.23]、vs Jaccard −0.36 [−0.51,−0.19]；P<1e-145 口径 SI 5.5 明文退役；MW P=5.6e-18 标注 descriptive | nc52_stats_tabula_entrycluster.csv 逐项一致，并附 naive pair bootstrap SE（0.011–0.013 vs cluster 0.06–0.08）对照 |
| M6（R3 联署）调整模型 i.i.d. | whole-tumor 标签置换 B=10,000 重拟合全 OLS：KRAS-WT P=0.0007/0.0010/0.0003（smoke/agesex/admix），EGFR-WT admix P=0.2815；另报 design-effect context（rho_intra 0.22–0.42，DE 2.5–4.0） | nc52_tcga_luad_adjmodel_permutation.csv 逐项一致 |
| R3 m5 四协变量措辞 | 正文改为 "alone or jointly with admixture, or with age and sex"，与 CSV 实际模型一致 | nc49_tcga_luad_smoking.csv（B_smoke_adj / B_smoke_agesex_adj / B_smoke_admix_adj） |
| 新增：候选估计器敏感性 | "only 3 of 39 Strong candidates survive a switch to a global-k_n estimator" 入正文与 Discussion | nc52_brain_candidate_effectsize.csv：persist 3、lost 36、gained 104、frac 0.077，一致 |
| 新增：composition ex-CC | pooled −0.9% [−4.3, +2.5]（B=1,000 cluster bootstrap）；per-cancer 异质性带 CI；myeloid 单独 null（1.001, P=0.982）；相关 P 值标注 descriptive | nc52_tcga_composition_excc.txt 逐项一致 |
| 新增：GTEx 健康参照 | healthy/adjacent ≈ 1.0–1.2、tumor 2.0–2.7×、kidney 例外（n=28）、跨队列 GTEx–adjacent 技术效应披露 | nc52_gtex_summary.json：lung 1.14e-3/9.7e-4/2.50e-3、liver 1.98/1.92/3.98e-3、breast 9.1/8.7/2.41e-3，一致（但见问题 P3/P4） |
| 新增：LIHC Cox ex-CC | n=272、79 events、HR/SD 1.08 [0.88, 1.33] P=0.467、cox.zph GLOBAL P=0.023 一并报告 | nc52_lihc_cox_excc.csv / _zph.csv 一致 |

## 二、遗留问题清单（按严重度；均附 ground truth 依据）

### Major：无。

### Minor

**P1（可追溯性，须修）AUC 的 DeLong CI 在 SI 无任何方法学记载。**
MS 三处引用 "DeLong 95% CI [0.770, 0.838]"（摘要、Results 模拟段、图注区），但 SI 全文 grep "DeLong"=0、"0.838"=0，MS/SI 均未引用 results/nc52_stats_auc_ci_methods.csv。该 CSV 还含 module-seed cluster bootstrap 变体 [0.771, 0.836]、固定特异度敏感性表（特异度 0.90/0.95/0.99 下 ω 灵敏度 0.42/0.273/0.038）与分背景功率列——这些正是上轮 M3 要求的材料，却只存在于数据文件、未进入 SI。审稿人无法从稿件追溯该 CI 的计算方式。
→ 修复：SI Note 1 增加 2–3 句 AUC 区间方法（DeLong + module-seed 聚类 bootstrap，B=5,000, seed 42）并引用 nc52_stats_auc_ci_methods.csv；建议将固定特异度敏感性表纳入附表。

**P2（数值不一致，须修）TCGA 样本量算术矛盾。**
MS Methods 与 SI 5.3 列出 "LUAD 493+76; LUSC 534+58; LIHC 398+57; KIRC 750+82; BRCA 1010+109"，合计 = 3,567，但同句括号声明总数为 3,535（ex-CC）。3567 − 3535 = 32 = CC 样本数：即列出的 per-cancer 计数仍是排除前口径（LIHC 应为 366+57），或总数应为 3,567，二者必居其一。另 SI 4.3 仍写 "totaling n = 3,567 samples entering the pair-level analysis" 且不提 ex-CC，与 SI 5.3（3,535 ex-CC default）直接冲突。
→ 修复：统一三处（MS Methods、SI 4.3、SI 5.3）的 per-cancer 计数与总数口径。

**P3（未记录，须修）GTEx 比较的 TCGA 队列定义与主分析不一致。**
nc52_gtex_summary.json 显示 GTEx 脚本使用 LUAD 495 / LUSC 535 / LIHC 398 / KIRC 754 / BRCA 1032（肿瘤侧合计 3,214 + 正常 382 = 3,596，即全表达矩阵），比 pair-level 集合多 29 个样本（+2/+1/0/+4/+22），且未见 ex-CC 排除的记载（LIHC 398 含 CC 与否不明）。GTEx k_n 结论（healthy≈adjacent≪tumor）不太可能因 29 个样本翻转，但队列定义应在 SI Note 8 一句话说明，并说明与 ex-CC default 的关系。
→ 修复：SI Note 8 GTEx 段补队列定义一句；如可行，以 ex-CC 队列重跑确认（预期不变）。

**P4（报告规范，建议修）"P ≈ 0" 与未标注的重叠对检验。**
(a) SI Note 8 GTEx 段 "TT ≫ NN, P ≈ 0" 与 Note 9 severity 段两处 "JT P ≈ 0"：ground truth JSON 中对应值为精确 0.0（浮点下溢），规范写法为 P < 2.2×10⁻¹⁶ 或给出机器精度下界。(b) GTEx 的 MWU/JT 检验作用于重叠 pair 集合（每样本出现在多对中），未像 Tabula/组成相关那样标注 "treat pairs as independent, descriptive only"——同一文档内标准应一致。(c) liver 的 GG vs NN：ratio 1.03 但 p_MWU_GG_lt_NN = 3.8×10⁻⁵（单侧，nc52_gtex_summary.json），即肝中 GTEx 显著低于 adjacent（效应微小）；SI 行文 "adjacent–adjacent at the healthy level" 是效应量陈述，建议加半句注明肝组存在统计学可检出的微小差异。
→ 修复：统一 P 值下界写法；补 descriptive 标注；补肝组半句。

**P5（措辞，建议修）质量调整梯度的层级归属。**
MS："(class, library)- and (class, region)-level adjustment … leaves it at 6.33–6.45"。ground truth：6.3276（class_x_region_pair，无 mito）与 6.4503（class_x_region_pair，含 mito）均来自 (class, region) 层模型；(class, library) 层 CSV 只报告 T3 系数（k_n 0.469、k_f 0.688、ω 0.219→含 mito 后 k_n 0.389 等），未输出梯度值。当前措辞暗示区间两端分别来自两个层级，与实际不符。
→ 修复：改为 "(class, region)-level adjustment with and without mitochondrial fraction leaves it at 6.33–6.45; (class, library)-level T3 coefficients are likewise attenuated only modestly"。

**P6（轻微，可选）Kang 0/30 仍未附 Wilson CI。**
MS "0 of 30 above its null 95th percentile" 无区间；SI 3.12 有 Wilson [0.000, 0.114]。正文加括号即可。

**P7（轻微，可选）Note 10 分解 CI 缺同类 caveat。**
Note 10 对 1.74 [1.64, 1.84] 已加 "propagates only cell-resampling noise at fixed donors"，但同段 k_f 比 2.09 [2.02, 2.18]、k_n 比 1.29 [1.21, 1.41]（同为 20 次细胞重采样百分位区间）未加该限定。

**P8（遗留自上轮，轻微）mouse pilot 单调性 n=2–4。**
Results "increased monotonically with biological distance … (2–4 pairs per category)"：类别均值基于 n=4/3/2–4 且对间共享细胞型，单调性陈述仍是描述性的；one-sided MW（n=15）已标 exploratory。建议给类别均值附区间或明确 "descriptive"。

**P9（可选稳健性）TCGA NN/TT 比值 CI 仍仅有 percentile cluster bootstrap。**
簇数（57–109 normal + 数百 tumor）远大于 Note 2 覆盖研究所示的问题区（6–7 簇），percentile 在此预期表现可接受，且 LIHC 区间本已跨 1；但既然 bootstrap-t 机器已存在，对五个 NN/TT 比值补一组 studentized/BCa 区间作为稳健性列（附表一行）可彻底关闭该问题。

## 三、评分（0–10，NC 标准）

- 方法可靠性 soundness: **8/10**——上轮全部 Major 已修复并经 ground truth 核验；two-stage/entry-cluster/donor bootstrap、whole-tumor 置换、kn_floor 敏感性构成完整且彼此一致的推断体系；遗留问题均为报告与可追溯性层面，非推断错误。
- 新颖性 novelty: **6/10**——HK 锚定 + 比值归一 + 设计匹配零模型的组合增量不变；GTEx 三角验证增强了生物学主张但未改变方法新颖性。
- 意义 significance: **6.5/10**——GTEx 健康参照使 pan-cancer 反转从"组织层观察"向"肿瘤特异性 HK 失调"推进半步（field-effect 反读被排除，肾例外如实披露）；specificity-first 定位与功率边界的诚实披露界定了真实应用场景。
- 表达 presentation: **8.5/10**——旧口径的退役全部明文标注（pseudo-replicated、superseded、descriptive），新增分析（估计器敏感性 3/39、design-effect context）主动暴露弱点；扣分在 P1–P3 的可追溯性/一致性问题。
- **总评 overall: 7.5/10，verdict: minor revision**

## 四、可执行条件清单（minor revision 条件）

1. SI Note 1 补 AUC 区间方法段（DeLong + module-seed cluster bootstrap）并引用 nc52_stats_auc_ci_methods.csv；固定特异度敏感性表入附表。（对应 P1）
2. 统一 MS Methods / SI 4.3 / SI 5.3 的 TCGA per-cancer 计数与 3,535 总数（算术闭合并与 ex-CC 口径一致）。（对应 P2）
3. SI Note 8 补 GTEx 比较所用 TCGA 队列定义一句（全矩阵 3,596 vs pair-level 3,535；ex-CC 状态）。（对应 P3）
4. 全文 "P ≈ 0" 改为有界写法（P < 2.2×10⁻¹⁶ 或实际下界）；GTEx pair-level 检验补 descriptive 标注；肝组 GG<NN 微小显著差异补半句。（对应 P4）
5. 修正质量调整梯度层级归属措辞（6.33–6.45 均出自 (class, region) 层 ±mito）。（对应 P5）
6. 可选：Kang 0/30 附 Wilson CI [0, 0.114]（P6）；Note 10 分解 CI 补 cell-resampling-only 限定（P7）；mouse pilot 类别均值附区间或标 descriptive（P8）；TCGA 五比值补 studentized/BCa 稳健性列（P9）。

条件 1–5 为必须；6 为建议。所有修复均为文字/附表层面，无需新计算（除 P3 可选重跑与 P9 可选补列）。
