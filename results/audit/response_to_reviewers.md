# Response to Reviewers — CKI（Nature Communications 投稿内部专家团三轮）

稿件：CKI（Cell-type Ka/Ks-inspired Index）：ω = k_f/k_n 基线归一化细胞状态差异指数
轮次：nc52 终审轮（v52，@7133b43）→ nc53 修复（@4a7a34c）→ nc53 确认轮（复审+打分）→ nc54 微修（@59a50cb）→ v0.5.2 发布链（@fb782c9 + phase-2）
评分轨迹：nc52 终审均分 **7.28** → nc53 确认轮终分 **8.08**（6/6 accept、零 major、零新增分析要求）
本文件逐条回应三轮全部审稿意见。所有数字均经 ground truth 文件复核（results/ 下 nc52_* 输出），稿面引文以 @fb782c9 为准。

---

## R1 — 统计方法学（7.5 → 8.0，accept）

### nc52 终审五条必须（全部关闭 @4a7a34c）

**R1-1 AUC 的 DeLong CI 在 SI 无方法学记载（可追溯性）。**
回应：SI Note 1 新增 "AUC interval methods" 段：DeLong 95% CI [0.770, 0.838] 与 module-seed cluster bootstrap [0.771, 0.836]（B=5,000, seed 42）并列，明文引用 results/nc52_stats_auc_ci_methods.csv；固定特异度敏感性（0.90/0.95/0.99 下灵敏度 0.42/0.273/0.038）入附表。

**R1-2 TCGA per-cancer 计数与 3,535 总数算术矛盾。**
回应：MS Methods 改为 "3,567 samples, of which 3,535 enter … all 32 excluded cell-line aliquots are LIHC tumors, leaving 366"；SI 4.3 队列层级句统一三口径（3,567 pre-audit / 3,535 ex-CC / 3,596 全矩阵）。

**R1-3 GTEx 比较的 TCGA 队列定义未记录。**
回应：SI Note 8 补队列定义句：GTEx 与 deconv 同用全表达矩阵（LUAD 495/LUSC 535/LIHC 398/KIRC 754/BRCA 1032，合计 3,596），与 pair-level ex-CC 集合（3,535）的关系一句话说明；KIRC 750（pair-level）vs 754（全矩阵）差异已解释。

**R1-4 "P ≈ 0" 规范与 GTEx 重叠对检验标注。**
回应：P≈0 全改有界写法（P ≤ 3.2e-84、JT P < 10⁻¹⁵ 等）；GTEx pair-level 检验补 descriptive 标注；肝组补半句（见确认轮 R1-N1 的最终定稿）。

**R1-5 质量调整梯度 6.33–6.45 层级归属。**
回应：复核 nc52_brain_quality_regression_classlib.csv，两值均出自 (class, region) 层（±mito：6.3276/6.4503）；MS 改为 "(class, region)-level adjustment with and without mitochondrial fraction"，SI 原文本正确未动。

### nc53 确认轮（R1 初评 7.5 → 修后签收 8.0）

**R1-N1（与 R3-m1 联署）肝句 P 值方向错配——确认轮唯一统计事实错误。**
指控：SI Note 8 "liver healthy is marginally above adjacent, one-sided P = 3.8 × 10⁻⁵" 把反方向 P 贴到 "above" 上。
裁定：坐实。nc52_gtex_summary.json 键 p_MWU_GG_lt_NN = 3.814e-05 系 GG<NN 方向；独立复算（results/nc52_gtex_pairs.csv）：MWU alt=less 3.814e-05、alt=greater 0.99996、two-sided 7.63e-05；中位数 GG 1.976e-3 > NN 1.917e-3（1.03×）但 NN 右尾更重（mean 3.77e-3 vs 2.38e-3）。
修复（@59a50cb，采用 R3 建议措辞）："in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, with a heavier adjacent upper tail"。R1 签收，评分升至 8.0。

**R1-N2 GTEx 段 P 值独立性标注位置。**
回应：段末补 "Pair-level P values in this GTEx comparison treat pairs as independent and are descriptive only."（R1 建议指明家族以避免 "in this section" 歧义，采纳）。

**R1-N3 SI 5.3 样本数镜像句式。**
裁定：无需改——当前文本已同段说明 3,567 before / 3,535 after audit。不动。

---

## R2 — 单细胞计算生物学（7.5 → 8.0，accept）

### nc52 终审 A1–A5（全部关闭 @4a7a34c）

**R2-A1（与 R5-M5 联署）"permuting k_n across the 5,151 human pairs" 疑似笔误（主分析 4,851）。**
裁定：部分反转——非笔误。nc52_stats_omega_kf_math_floor.csv 逐字吻合（n_pairs=5,151、floor 0.524 [0.506, 0.541] vs observed 0.089）；该置换跑在 102-entry 全量 inventory（phase33），与主分析 4,851（99 filtered entries）是不同输入集。
修复：MS 加 "full-inventory" 限定（"5,151 full-inventory human pairs"）；SI Note 9 新增 k_n-permutation floor 小节（human 5,151: floor 0.524 [0.506,0.541] vs 0.089；mouse 703: 0.857 [0.843,0.870] vs 0.821，标注 dataset-dependent）。4,851 主口径不动。

**R2-A2 pair 表口径。** MS Methods 改为 "34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table"；SI 5.12 同口径（34,828/478/35,306）。

**R2-A3 样本计数。** 同 R1-2，三处统一。

**R2-A4 Table 11 表注图号。** Fig. 5a → Fig. 4a。

**R2-A5 KIRC 750 vs 754。** 两种样本集定义（pair-level vs 全表达矩阵），SI 4.3 队列层级句统一说明，不重跑分析。

### nc53 确认轮（R2 = 8.0，条件③④⑤ nc54 关闭，①②协商沿留 proof）

**R2-C2 fold 区间低估。** 坐实：BRCA TT/NN = 2.776 > 2.7（nc52_tcga_pancancer_excc.csv）。MS+SI 同步改 "2.0–2.8-fold"（覆盖 TT/NN 2.08–2.78 与 TT/GG 2.01–2.66 两种读法）。

**R2-C4 "38% misreports" 缺模拟标签。** 补 "under fourfold cell-count imbalance (simulation) k_f misreports 38% of neutral pairs"。

**R2-m1 Table 5 表注引用被取代的 v44 口径。** 坐实：表注（docx 与 xlsx A1 同源）旧文 "−1.3% [−4.8%, +2.0%]" 系 B=200 v44 输出；权威 ex-CC 口径（SI Note 8 与 MS 一致）为 pooled −0.9% / cluster-bootstrap median −0.8% [95% CI −4.3%, +2.5%]。表注已同步。

**R2-m2 ρ 指代不清。** MS 改 "reference-free composition check: non-parenchymal fraction versus k_n, ρ = 0.20–0.26"。

**R2-B1/B2（建议级，审稿人同意沿留 proof）：** 四处 GTEx 断言式措辞（摘要 "argue against"、Intro "confirm as tumor-specific"、Results "tumor-specific rather than"、Discussion "supporting … over"）+ Note 8 跨队列不确定度量化句（GA/GG 1.8–2.3×，候选插入 "(tentative, GTEx cross-cohort discrepancy unresolved)"）；KIRC 句改写。状态：沿留 proof 阶段，已列入清单第四节。

---

## R3 — 肿瘤基因组学（7.2 → 8.0，accept after minor revisions → accept）

### nc52 终审 C1–C3（全部关闭 @4a7a34c）

**R3-C1 35,306 pair 表口径。** 同 R2-A2。
**R3-C2 k_n 括注 "which includes 1" 误导。** 改为 "1.34 [1.02, 1.89] excludes 1 ex-CC, so the k_n elevation is nominally significant"。
**R3-C3 deconv 验证引用。** MS Results 末句改 "pending single-cell validation (reference-free composition check …; Supplementary Note 8)"；Discussion 末改 "the composition check … least certain."；SI Note 8 新增 reference-free composition fallback 段（NNLS、split-half ρ 0.934/0.964、k_n 相关 0.20/0.26、CIBERSORTx/BayesPrism 不可行原因、脚本+输出清单）。

### nc53 确认轮（R3 = 8.0；m1/m2 nc54 已修，修复采用 R3 本人建议措辞）

**R3-m1（与 R1-N1 联署）肝句方向。** 见 R1-N1；另查得脚本 notebooks/nc52_gtex_kn.py line 433 `alternative="less"` 佐证方向归属。
**R3-m2 Fig 4a 图注字面矛盾。** 坐实："which exceeds 1 in all five cancer types while k_f does not" 在 TT/NN 口径下为假（k_f TT/NN 均值比 1.25–2.07，五癌种 CI 全排 1）；作者本意 NN/TT 口径。改 "while the NN/TT ratio of k_f does not"。
**R3-m3/m4（沿留 proof）：** 摘要 GTEx 句补 "in lung, liver, and breast" 限定（与摘要词额统筹——摘要已减重至 196/200 备出余量）；Discussion attenuation 措辞弱化（可选）。

---

## R4 — 脑图谱（7.0 → 7.5，accept）

### nc52 终审三条（关闭 @4a7a34c）

**R4① 摘要 "(k_n-dominated)" 插入。** 裁定：沿留 proof（摘要词额限制）；v0.5.2 已将摘要减重至 196/200，余量 4 词已备。
**R4② Note 13 指针。** SI 3.3 lower-tail 富集句尾已加 Note 13 rule-matched null 指针。
**R4③ 任务书口径更正。** 脑 Strong 39（非 30）、全局家族无一 FDR 存活 q_min=0.520（brain_bs_null_results.csv q_fdr min=0.5202 实证）——以 ground truth 为准，MEMORY 已更正。

### nc53 确认轮（R4 = 7.5，accept，proof 两处一词级文字）
Fig 14 图注 "validation value lies" → "sanity-check value lies"（沿留 proof，与 R4① 同批处理）。

---

## R5 — 编辑/科学写作（7.0 → 9.0，accept，投稿就绪）

### nc52 终审 M1–M5 投稿阻断（全部关闭 @4a7a34c）

**R5-M1 Table 1 表注缺失。** 新增（复用 xlsx A1 文本）。
**R5-M2 Supplementary Fig. 14 图注缺失。** 新增（microglia ω 21.83±7.20 vs 1.30±0.36、P=5.5e-14、AUC=1.00、k_n AUC=0.89）。
**R5-M3 CL 口径。** 3,567→3,535、1.10→1.11–2.46；"ranked first" → "gave the best functional-versus-neutral discrimination at bounded power (AUC = 0.80)"；新增 GTEx 句。
**R5-M4 Tables 1–4 只见引用不见表。** SI xlsx 15→19 sheets（Table 1 phase32_sweep 5 行、Table 2 phase35_cross_organ 59 行、Table 3 brain_ct_test 10 行、Table 4 6,591 候选含 tier/residual/ω）；docx 四段描述各补 xlsx sheet 指针。
**R5-M5（与 R2-A1 联署）5,151。** 见 R2-A1（ground truth 反转裁定）。

### nc53 确认轮（R5 = 9.0）
期刊合规全绿：标题 13 词、摘要 ≤200 无引用、MAIN ≤5,000、图注 ≤350、文献 57 条、结构 Intro→Results→Discussion→Methods、声明区块齐备。5 条文字级 minor 沿留 proof（见其报告 B 节）。

---

## R6 — 可复现性（7.5 → 8.0，accept）

### nc52 终审唯一硬条件（关闭 @95a4cf7/4a7a34c）
**Zenodo v0.5.1 version record + DOI 写回。** record 22938380 上线（2026-09-24，v0.5.1，标题改 Nature Communications，归档 1.6 GB）；version DOI 10.5281/zenodo.22938380 已写回 MS Code availability（A15 断言同步）；Release v0.5.1 资产替换（id 586271335，digest 与本地 zip 逐字节一致，API 核实）。

### nc53 确认轮（R6 = 8.0）
数值可重算性三轮亲验（spot_check + pytest 29 + sha256 比对）零失配。沿留外观项：pyproject description 命名、CI ubuntu-only vs 跨平台声称、Guide 5.6f 的 6.67、SI 5.12 指针 5.10c→5.13。
**Dockerfile L6/L7（cki:0.5.0→0.5.2）已在 v0.5.2 版本面同步时顺手关闭（@fb782c9）。**

### v0.5.2 发布链（本轮决策 A 处置）
tag v0.5.2 = fb782c9（phase-1：版本面 0.5.1→0.5.2 全同步 + 摘要 196/200）；Release v0.5.2 id 396170102，资产 id 587110399（12,894,059 B，readback sha256 MATCH）；Zenodo webhook 202 Accepted（record 生成后 phase-2 写回 version DOI 并恢复 A15 断言）。MS Code availability 当前为 concept-DOI-only 过渡口径（concept DOI 10.5281/zenodo.20405458 恒解析至最新版），无错误陈述。

---

## 附：验证矩阵（@fb782c9，phase-1）

| 项 | 结果 |
|---|---|
| 构建断言 | 221/221 |
| ms_verify / si_verify | 127/127、121/121 |
| XV8 | 63/63（MAIN 4,999/5,000；摘要 196/200；Methods 2,918；图注 max 302） |
| pytest tests/ | 29 passed |
| spot_check | ALL PASS |
| git | 远端 main = tag v0.5.2 = fb782c9（ls-remote 核对） |
| Release 资产 | 587110399，readback sha256 5b84f2f1… MATCH |

沿留 proof 清单（各审已确认接受）：R2-B1/B2、R3-m3/m4、R4①+Fig 14 措辞、R5 五条、R6 外观项四条。摘要余量 4 词已备（196/200）。
