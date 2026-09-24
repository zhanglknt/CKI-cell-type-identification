# nc53 确认轮终审报告 — R3-cancer（肿瘤基因组学/TCGA）

- 审稿人：R3-cancer（Nature Communications 肿瘤基因组学方向）
- 对象：修复提交 69e3567 后的工作树当前版（远端 main = 4a7a34c，CI success）
- 上轮报告：results/audit/nc52_final_review_r3.md（7.2/10，accept after minor revisions，条件 C1–C7）
- 复核方式：7 项修复逐条对照当前文本原句 + 输出文件 ground truth（nc52_tcga_pancancer_excc.csv、nc52_gtex_summary.json、nc52_gtex_kn_by_grouptype.csv、nc52_lihc_cox_excc_zph.csv、nc52_tcga_luad_adjmodel_permutation.csv、notebooks/nc52_gtex_kn.py 源码、git diff 69e3567）

---

## A. 逐条裁定表

| # | 条件项 | 裁定 | 当前文本原句作证 |
|---|--------|------|------------------|
| 1 | ex-CC 样本口径 | **RESOLVED** | MS Methods（line 94）："(3,567 samples, of which 3,535 enter the pair-level analysis after the barcode-audit exclusion below; all 32 excluded cell-line aliquots are LIHC tumors, leaving 366)"；line 112："34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table"；Results（line 47）："totalling 3,535 samples … All TCGA results exclude 32 cell-line-derived aliquots found by barcode audit"；摘要（line 14）："3,535 samples after excluding cell-line-derived aliquots"。数字自洽：493+76+534+58+398+57+750+82+1,010+109=3,567；35,306−478=34,828；LIHC TT 2,000→1,709（与 nc52_tcga_pancancer_excc.csv n_TT_pairs=1709 一致）；9,709 TT+15,306 NN+9,813 TN=34,828 内部闭合。SI 3.13（line 135）、SI 4.3（"totaling n = 3,567 samples in the pair-level analysis before the barcode audit"）、SI 5.12（line 255）同步。 |
| 2 | deconv fallback 入稿 | **RESOLVED** | SI Note 8 新增整段（line 190）："Reference-free composition fallback (v52)… split-half Spearman ρ = 0.934 LIHC, 0.964 KIRC … tracks k_n only weakly (Spearman ρ = 0.20 LIHC, 0.26 KIRC), so measurable composition shifts explain at most a small share of the per-tumor k_n elevation"，含脚本与输出文件指针。MS Results（line 49）已引用："pending single-cell validation (reference-free composition check: ρ = 0.20–0.26 versus k_n; Supplementary Note 8)"。与 nc52_tcga_deconv_feasibility.json 数值一致。 |
| 3 | k_n ex-CC 括注 | **RESOLVED** | SI 3.13（line 139）："the TT k_n/NN k_n ratio 1.34 [1.02, 1.89] excludes 1 ex-CC, so the k_n elevation is nominally significant"。对照 nc52_tcga_pancancer_excc.csv：LIHC k_n mean ratio 1.337 [1.022, 1.886]——数值吻合，v52 的 "which includes 1" 残留错误已清除（同句保留的 "NN/TT 1.11 [0.94, 1.30], which includes 1" 指的是 ω 的 NN/TT 比，与 CSV [0.943, 1.302] 一致，属正确表述）。 |
| 4 | GTEx 段 | **RESOLVED**（但见 B-m1） | MS Results（line 50）："adjacent-normal k_n is as low as healthy k_n (healthy/adjacent ≈ 1.0–1.2) while tumor k_n is 2.0–2.7-fold higher … Kidney is the exception (GTEx cortex k_n ≈ tumor; n = 28, high variance)"；SI Note 8（line 189）补足 "liver healthy is marginally above adjacent, one-sided P = 3.8 × 10⁻⁵" 与 "TT ≫ NN, P ≤ 3.2 × 10⁻⁸⁴"、"Cross-cohort … (P ≤ 1.4 × 10⁻²⁶)"。ground truth 复核（nc52_gtex_summary.json）：GG/NN 1.031–1.207（→1.0–1.2 ✓）；TT/GG 2.01–2.66（→2.0–2.7 ✓）；p_MWU_TT_gt_NN 最大者 LIHC 3.16e-84（→≤3.2e-84 ✓）；p_MWU_GA_gt_GG 最大者 KIRC 1.38e-26（→≤1.4e-26 ✓）；KIRC GG/NN 3.298、TT/GG 1.09（→"≈ tumor" ✓）；肝 P=3.81e-5 数值吻合但方向表述见 B-m1。 |
| 5 | severity 分级 | **RESOLVED** | MS Results（line 48）："stratifications beyond LUAD are denominator-dominated vignettes (Supplementary Note 9)"；SI Note 9（line 195）："The main text reports only the LUAD driver-mutation contrast as a primary result; the LIHC Edmondson and BRCA PAM50 gradients are reported here as denominator-dominated vignettes (Supplementary Fig. 4b)"；Supp Fig. 4 图注（line 204）："both orderings are denominator-dominated and reverse or largely reverse under k_f alone"。数值复核：Edmondson ω 78.8/75.8/77.6/72.3、JT P < 10⁻¹⁵、k_f JT P = 8.4 × 10⁻¹²，与 nc52_tcga_excc_severity.csv 一致；SI 5.12（line 256）"289 ex-CC tumors with pair coverage" 与 MS Methods "372 patients with calls" 层次清楚。 |
| 6 | Discussion 末段改写 | **RESOLVED** | MS Discussion（line 75）："A marker-panel composition check (Supplementary Note 8) attenuates the pooled k_n coefficient by only −0.9%, but this masks heterogeneity: attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%), so marker-measurable composition likely contributes in those types … The hepatocellular literature motivating this reading 38 concerns the weakest-reversal cancer type, where the mechanism is least certain."——pooled 掩盖异质性、LIHC/KIRC 正向衰减、肝癌文献与数据排序的张力（我 v52 的 M6/C 系列）均已落实；−0.9%、+44%、+20% 与 SI Note 8 line 187（−0.9%、+44.1%、+19.7%）一致。残余措辞小问题见 B-m4。 |
| 7 | Cover Letter 同步 | **RESOLVED** | CKI_NC_Cover_Letter_fulltext.txt（line 3）："across 3,535 TCGA samples in five cancer types … (NN/TT ω ratio 1.11–2.46, bootstrap CIs excluding 1 in four of five)—reflecting a 1.3–3.3-fold elevated housekeeping baseline … A GTEx healthy reference further shows adjacent-normal k_n at healthy-tissue levels in lung, liver, and breast, arguing against a field-effect reading"；AUC 句改为 "at bounded power (AUC = 0.80)"。与 ex-CC CSV（1.112–2.464）及 k_n mean ratio 区间（1.337–3.292）一致。 |

**裁定汇总：7/7 RESOLVED。** v52 全部条件项落地，数字均通过 ground truth 复核。

---

## B. 新增问题

### Major

无。

### Minor

- **m1（修复引入，建议必改）SI Note 8 肝 GTEx 句 P 值方向与文字方向相反。** line 189："liver healthy is marginally above adjacent, one-sided P = 3.8 × 10⁻⁵"。复核 notebooks/nc52_gtex_kn.py line 433：`p_gg_nn = mannwhitneyu(kn_gg, kn_nn, alternative="less")`——该 P 的备择方向是"healthy 随机**低于** adjacent"，P=3.81e-5 支持的是"低于"。中位数比值 1.031 的"略高"只是中位数口径；pair 级分布上 NN 右尾更重（nc52_gtex_kn_by_grouptype.csv：Liver NN mean 3.77e-3、q75 6.16e-3 vs GG mean 2.38e-3、q75 2.98e-3），MWU 以秩为准故显著于相反方向。建议改为 "liver healthy and adjacent medians coincide (ratio 1.03); the distributions differ (one-sided MWU P = 3.8 × 10⁻⁵, adjacent showing a heavier upper tail)"。不影响 field effect 结论（若反而加强：healthy 绝不高于 adjacent），但当前文字把 P 安在了错误方向上，统计读者会立刻发现。此句为 69e3567 本轮新加（git diff 确认），属修复引入。
- **m2（既有遗留，建议必改）MS Fig. 4a 图注 "while k_f does not" 字面与数据矛盾。** line 197："the amber axis shows the corresponding tumor/normal ratio of the housekeeping baseline k_n (TT/NN, means with 95% CIs), which exceeds 1 in all five cancer types while k_f does not—the reversal is denominator-driven." 按句法 "which/ k_f does not" 均指 TT/NN 口径，而 ex-CC 数据 k_f TT/NN mean ratio 五癌种为 1.25/1.69/1.63/1.55/2.07（95% CI 全部排除 1；中位数口径 1.43–2.07 也全 >1）——k_f 的 TT/NN 同样超过 1。该句亦与正文 line 47 "TT k_f was equal to or higher" 直接冲突。作者本意应为"k_f 无反转（其 NN/TT 不超 1）"，建议改为 "while the NN/TT ratio of k_f does not" 或 "while k_f shows no reversal (TT ≥ NN in all five)"。69e3567 未触及此图注（diff 确认），属既有遗留。
- **m3（既有遗留，可选）摘要 GTEx 句未提肾脏例外。** line 14："an elevated housekeeping baseline that GTEx healthy references confirm as tumor-specific"——正文 line 50 已正确限定 "Kidney is the exception"，摘要 "confirm" 无限定略显过强；建议 "confirm as tumor-specific in lung, liver, and breast" 之类。字数允许范围内的一词修正。
- **m4（既有遗留，低优先）Discussion "attenuation is strongest where the reversal is weakest" 的模式表述略超数据。** line 75 括注 "(LIHC +44%, KIRC +20%)"：LIHC 确为最弱反转（1.11）且衰减最强（+44%），但 KIRC 是第二**强**反转（1.88）且衰减第二强（+20%），"最强衰减↔最弱反转"的对应关系在 n=5 上并不成立。建议弱化为 "attenuation is largest in LIHC (+44%, the weakest reversal) and KIRC (+20%)"。

### 口径一致性全文扫描（纯度校正/驱动分层/Cox 阴性表述）

- 纯度校正：MS line 48/49、SI 3.13 line 136–137、Fig. 4 图注（c,d）口径一致（EGFR 消失 all P > 0.4；KRAS 保留，adjusted log-ω 1.19 [1.12, 1.26]）；Fig. 4 图注 "adjusted P = 0.009 and 0.029" 与 SI 3.13（k_f +0.012, P = 0.009）及置换表（B_smoke_admix k_f KRAS−WT P = 0.0299）一致。
- 驱动分层：whole-tumor 置换口径统一（B = 10,000；KRAS P ≤ 0.001、EGFR P ≥ 0.28，与 nc52_tcga_luad_adjmodel_permutation.csv 一致）；TP53/组织亚型残余混杂在 MS line 48 与 SI line 139 均如实披露。
- Cox 阴性表述：MS line 49 "ω HR per SD 1.08 [0.88, 1.33], P = 0.467; k_f likewise null" 与 nc52_lihc_cox_excc.csv 一致；zph 已在 SI 3.13 与 5.12 双处披露 "M2 GLOBAL P = 0.023"（zph CSV 0.02255 ✓），阴性结论措辞克制（"not associated with survival"、"tissue-level divergence at bulk resolution, pending single-cell validation"）。
- 映射口径：line 49 "linear 1.11 [0.94, 1.30] versus softmax 1.29 [1.09, 1.53]" 与两口径全表（1.286 [1.091, 1.533]）一致；kn_floor "never reached" 与敏感性表（floor ≤ 1e-4 比值不变）一致。
- Note 8 line 186 引用的 "main 35,306-pair linear table" 中位数（2.60/2.53/2.08/3.61/2.78）为排除前口径，但已明确标注 pair set 差异（"the difference is the pair set, not the estimator"），且 line 187 给出 ex-CC 更新值（LIHC 2.06），无矛盾。
- 未发现修复在肿瘤学口径上引入的其他不一致。

---

## C. 总分与推荐

- **总分：8.0 / 10**（上轮 7.2 → 本轮 +0.8）
- **推荐：accept after minor revisions（仅需文字级修正，无需新分析）**
- **一句话理由：** 7 项条件全部落实且数字经 ground truth 复核无误，ex-CC 口径、GTEx 参照、Cox 阴性披露与 severity 降级已达可投水平；仅剩两处文字级修正——SI 肝 GTEx 句 P 值方向写反（m1）与 Fig. 4a 图注 "while k_f does not" 字面矛盾（m2）——改完即可接收。
