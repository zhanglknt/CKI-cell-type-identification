# nc55 盲审报告 — R3-cancer（肿瘤基因组学 / TCGA）

- 审稿人：R3-cancer（Nature Communications 肿瘤基因组学方向：TCGA 分析、肿瘤纯度/混杂校正、驱动基因分层、bulk 组织转录组）
- 对象：当前终稿 v0.5.2 @5a5ae6d（`results/CKI_Manuscript_NC_fulltext.txt` 全文通读；`results/CKI_Supplementary_NC_fulltext.txt` 抽查 Note 8/9、Section 1.7/3.13、Methods 5.12）
- 复核性质：独立重审；所有数字以当版文本为准并对照输出文件 ground truth（nc52_tcga_pancancer_excc.csv、nc52_gtex_summary.json、nc52_gtex_kn_by_grouptype.csv、nc52_tcga_knfloor_sensitivity.csv、nc52_lihc_cox_excc.csv/_zph.csv、nc52_tcga_luad_adjmodel_permutation.csv、nc52_tcga_deconv_feasibility.json）

---

## 总评分：**8.0 / 10**

## Verdict：**minor revision**（无需新分析；两处事实精确性小修 + 两处措辞弱化）

一句话总评：TCGA 部分的证据链（ex-CC 审计 → 双口径映射 → 组成/纯度/吸烟校正+置换 → GTEx 健康参照 → Cox 阴性如实披露）已达到罕见的多层防御水平，剩余问题均为文字级精确性瑕疵，不影响任何结论方向。

---

## 强项

1. **CC 审计与 ex-CC 默认队列堪称范式**：32 个 ILSBio 细胞系来源 LIHC 样本经 barcode 审计剔除，MS Methods（line 94）"3,567 samples, of which 3,535 enter … all 32 excluded cell-line aliquots are LIHC tumors, leaving 366"、line 112 "34,828 pairs after dropping the 478 pairs … from the 35,306-pair table"，摘要/Results/SI 1.7/3.13/4.3/5.12 全部同步；数字闭合（3,567 加总、34,828=35,306−478、LIHC TT 1,709 与 ex-CC CSV 一致）。
2. **解释链多层设防且每条都如实报告局限**：组成检查（pooled −0.9% [−4.3,+2.5]）明示掩盖 LIHC +44.1%/KIRC +19.7% 异质性（SI line 187）；高纯度半分析五癌种一致增强；reference-free fallback（split-half ρ 0.934/0.964，vs k_n ρ 0.20/0.26）已入 SI Note 8 并在 MS line 49 引用（"non-parenchymal fraction versus k_n, ρ = 0.20–0.26"，nc54 已补指代）。
3. **混杂校正达到可复现的严格度**：ESTIMATE 官方 141+141 基因 rank-based SSE；KRAS–WT 在纯度/吸烟/年龄/性别联合调整下经 whole-tumor 标签置换（B=10,000）确认（KRAS P ≤ 0.001、EGFR P ≥ 0.28，与置换 CSV 一致）；TP53 共突变与组织亚型未校正的残余混杂在 MS line 48 与 SI 3.13 双处明示。
4. **阴性结果表述克制**：Cox ω HR/SD 1.08 [0.88, 1.33] P=0.467、"k_f likewise null"、"tissue-level divergence at bulk resolution, pending single-cell validation"；zph M2 GLOBAL P=0.023（CSV 0.02255）在 SI 3.13/5.12 双处披露——阴性+PH 违背风险均不藏。
5. **映射口径透明**：linear 为权威口径、softmax 全表存档，LIHC 敏感（1.11 [0.94,1.30] vs 1.29 [1.09,1.53]）在 MS line 49 正文披露而非埋藏。
6. **GTEx 第三参照组**填补了 v51 的关键空白，且限定得当：healthy/adjacent ≈ 1.0–1.2（ground truth 1.031–1.207）、fold 区间限定 lung/liver/breast、肾脏例外（n=28、自溶）明示、GA 跨队列技术效应（P ≤ 1.4×10⁻²⁶）明示并据此限定"within-cohort orderings only"、pair-independence 声明（nc54）已补。

---

## Major 清单

无。

---

## Minor 清单

- **N1（新发现，事实精确性）SI Note 8 与 MS Methods 的 KIRC 肿瘤数未调和。** SI line 190："run on the full expression-matrix cohort (LIHC 366 and **KIRC 754** tumors…)"；MS line 94："KIRC **750** + 82"。ground truth：nc52_tcga_deconv_feasibility.json 记 n_tumors_excc=754（表达矩阵口径），ex-CC 泛癌 CSV n_tumor=750（pair-level 口径）——二者各自正确，但稿面无任何一句说明 754 是矩阵口径、750 是入对口径（SI 4.3 的 3,596/3,567 口径说明在另一节，读者难以自行拼接）。建议在 Note 8 括注 "(754 in the expression matrix, of which 750 enter the pair table)"。
- **N2（新发现，事实精确性）"floor never reached" 字面不准。** MS line 49："the housekeeping floor (k_n ≥ 10⁻⁴) is never reached, leaving every ratio identical across floors 0–10⁻⁴"。ground truth（nc52_tcga_knfloor_sensitivity.csv）：floor=1e-4 时 KIRC frac_NN_at_floor=0.0003（即 3,321 个 NN 对中 1 对触及 floor）；NN/TT 比值 1.8804→1.880，"比值不变"成立，但"never reached"对该 1 对为假。建议改 "reached by a single KIRC NN pair (1/3,321), leaving every group ratio identical to reported precision across floors 0–10⁻⁴"。
- **N3（沿留 nc53-m4，措辞）Discussion 衰减-反转对应表述超数据。** line 75："attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)"——LIHC 确为最弱反转（1.11）且衰减最强，但 KIRC 是第二**强**反转（1.88）且衰减第二强，n=5 上该对应不成立。建议弱化："attenuation is largest in LIHC (+44%, the weakest reversal) and KIRC (+20%)"。
- **N4（沿留 nc53-m3，部分已修）Introduction 的 GTEx 措辞未随摘要同步。** 摘要 line 8 已改为 "GTEx references argue against a field-effect reading"（hedging 到位 ✓），但 line 14 仍为 "an elevated housekeeping baseline that GTEx healthy references **confirm** as tumor-specific"，未提肾脏例外。建议与摘要统一为 "argue against a field-effect reading (lung, liver, breast)" 之类。

---

## nc52 / nc53 / nc54 处置逐条复核意见

| 轮次 | 处置项 | 复核结论 | 证据（当版文本 + ground truth） |
|------|--------|----------|--------------------------------|
| nc52 | GTEx 健康参照第三组 | **成立** | MS line 50："in lung, liver, and breast, adjacent-normal k_n is as low as healthy k_n (healthy/adjacent ≈ 1.0–1.2) while tumor k_n is 2.0–2.8-fold higher … Kidney is the exception (GTEx cortex k_n ≈ tumor; n = 28, high variance)"。复核：GG/NN 1.031/1.043/1.134/1.207→"1.0–1.2"✓；TT/NN 中位数 2.06–2.78 与 TT/GG 2.01–2.66→"2.0–2.8"✓（区间已限定三器官）；KIRC GG/NN 3.298、TT/GG 1.09→例外表述✓；KIRC 3.61 中位数比在 SI Note 8 line 186 披露✓；SI line 189 各组中位数（lung 1.14e-3/9.7e-4/2.50e-3 等）与 CSV 逐一吻合✓。 |
| nc53 | Note 8 reference-free fallback 段 | **成立** | SI line 190 整段在，数值（split-half ρ 0.934/0.964；vs k_n ρ 0.20/0.26）与 deconv json 一致；MS line 49 引用并在 nc54 补足 ρ 指代（"non-parenchymal fraction versus k_n"）。 |
| nc53 | 5,151 full-inventory 口径限定 | **成立** | Discussion line 70："permuting k_n across the 5,151 full-inventory human pairs"；SI Note 9 line 193 同口径。 |
| nc54 | 肝句方向修复（R3-m1） | **成立** | SI line 189："in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, with a heavier adjacent upper tail"——方向现在正确（脚本 alternative="less"，P=3.814e-5；NN mean 3.77e-3/q75 6.16e-3 vs GG 2.38e-3/2.98e-3，"heavier adjacent upper tail" 与分布吻合）。 |
| nc54 | fold 2.0–2.8 + pair-independence 声明 | **成立** | SI line 189 末句 "Pair-level P values in this GTEx comparison treat pairs as independent and are descriptive only." 在；"2.0–2.8" 上限由 BRCA TT/NN 2.776 支撑。 |
| nc54 | Fig. 4a k_f 取向（R3-m2） | **成立** | MS line 197："which exceeds 1 in all five cancer types while the NN/TT ratio of k_f does not"——NN/TT 口径下 k_f 比值 0.48–0.80 均 <1，字面为真，且与正文 line 47 "TT k_f was equal to or higher" 不再冲突。 |
| nc54 | Table 5 表注 ex-CC 组成口径 | **成立**（R2 项，交叉核对） | pooled −0.9%/median −0.8% [−4.3,+2.5] 与 SI line 187、MS line 49/75 三处一致。 |

**复核总结：nc52–nc54 全部处置成立，无回退、无新引入的肿瘤学口径矛盾。**

---

## 具体修改建议（按优先级）

1. SI Note 8 fallback 段 KIRC 754 括注矩阵口径（N1，一句话）。
2. MS line 49 "never reached" 按 N2 改为含 1 对例外的精确表述（一句话）。
3. Discussion line 75 衰减句按 N3 弱化（一词级）。
4. Introduction line 14 "confirm as tumor-specific" 与摘要 hedge 口径统一（N4，一词级）。

四处均为文字级编辑，不改任何数字、不需任何新分析；完成后本人无需再见稿，可由编辑核验。
