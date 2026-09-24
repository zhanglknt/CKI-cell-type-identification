# R1 统计终审 nc53 确认轮（修复后确认，当前 main = 4a7a34c）

审稿人：R1-stats
上轮报告：results/audit/nc52_final_review_r1.md；轮次汇总：results/audit/nc53_final_review_round_2026-09-24.md
权威文本：results/CKI_Manuscript_NC_fulltext.txt（修复后）；SI：results/CKI_Supplementary_NC_fulltext.txt
铁律执行：全部裁定均对照当前文本行号与 results/ 输出文件复核；肝组方向另用 nc52_gtex_pairs.csv 独立重算验证。

## A. 逐条裁定表（上轮 5 必修项 + team-lead 委托复核项）

| # | 上轮条件 | 裁定 | 当前文本证据（引文） |
|---|---|---|---|
| P1 | AUC DeLong CI 入 SI | **RESOLVED** | SI Note 1（line 159）："AUC interval methods (v52). The main-text AUC 95% CI [0.770, 0.838] is the DeLong interval on the 850-replicate ROC … A module-seed cluster bootstrap … gives a near-identical interval [0.771, 0.836] … results/nc52_stats_auc_ci_methods.csv (script scripts/nc52_stats_resampling.py)"。与 CSV 逐项一致（DeLong [0.7703, 0.838]；cluster [0.7706, 0.8363]）。 |
| P2 | TCGA 计数算术 | **RESOLVED** | MS Methods（line 94）："…BRCA 1,010 + 109 (3,567 samples, of which 3,535 enter the pair-level analysis after the barcode-audit exclusion below; all 32 excluded cell-line aliquots are LIHC tumors, leaving 366)"。算术闭合（3,567−32=3,535；398−32=366）。SI 4.3（line 147）给三层级："3,567 … before the barcode audit … The ex-CC default cohort … leaving 3,535 samples (LIHC 366 tumor + 57 normal)"。 |
| P3 | GTEx 队列说明 | **RESOLVED** | SI 4.3 同句："the GTEx comparison and the reference-free composition fallback (Supplementary Note 8) instead use the full expression-matrix cohort (3,596 samples, e.g. KIRC 754 tumors)"。与 nc52_gtex_summary.json（495/535/398/754/1032，合计 3,596）一致。 |
| P4 | P 值规范（P≈0、descriptive、肝句） | **PARTIAL** | 有界化完成：GTEx "P ≤ 3.2 × 10⁻⁸⁴"（line 189；ground truth 最大非零值 LIHC 3.16e-84，界正确）；severity "JT P < 10⁻¹⁵" 两处（line 195）；全文 grep 无残留 "P ≈ 0"（唯一命中为 "P ≈ 0.005"，合法）。MS 侧 descriptive 标注已加（line 30 "Mann-Whitney P = 5.6 × 10⁻¹⁸, descriptive—pairs share cell-type pseudobulks"；line 39 microglia "descriptive—pairs overlap across four donors"）。**但肝组半句方向错误（见 N1），且 GTEx 段 MWU/JT 检验未加重叠对标注（见 N2）**。 |
| P5 | 6.33–6.45 归因 | **RESOLVED** | MS（line 56）："(class, region)-level adjustment for detection depth, UMI counts, and mitochondrial fraction leaves it at 6.33–6.45"。与 nc52_brain_quality_regression_classlib.csv 一致（6.3276 与 ±mito 6.4503 均出自 class_x_region_pair 层）。 |
| T1 | k_n-permutation floor（委托复核） | **RESOLVED（口径正确）** | MS（line 70）："permuting k_n across the 5,151 full-inventory human pairs predicts Spearman 0.524 between ω and k_f, yet the observed value is 0.089"；SI Note 9（line 193）新段："On the full-inventory human pair set (5,151 pairs, the 102-entry inventory before the 99-entry filter that yields the 4,851 analyzed pairs), the floor is 0.524 (95% CI [0.506, 0.541]) while the observed … 0.089 … On the mouse full matrix (703 pairs) the floor is 0.857 [0.843, 0.870] and the observed 0.821 sits essentially at it"。与 nc52_stats_omega_kf_math_floor.csv 逐项一致（human obs 0.0895；mouse obs 0.8206）；5,151 与 4,851 输入集区分写明；human 观测远低于 floor → 真实基线去相关、mouse 贴近 floor → 共享分子强制，解读方向正确、dataset-dependent 结论诚实。 |

## B. 新增问题

### Major：无。

### Minor

**N1（修复引入，必修）肝组 healthy–adjacent 句的 P 值方向错配。**
【位置】SI Note 8 GTEx 段（line 189）："…(healthy/adjacent ≈ 1.0–1.2; liver healthy is marginally above adjacent, one-sided P = 3.8 × 10⁻⁵)…"。
【问题】所引 P = 3.8 × 10⁻⁵ 支持的是**相反方向**。ground truth 复核：(i) nc52_gtex_summary.json 的对应键名为 `p_MWU_GG_lt_NN` = 3.814e-05（LIHC），即单侧 MWU 备择 "GG < NN" 的 P 值；(ii) 我从 nc52_gtex_pairs.csv 独立重算：LIHC GG（n=2,000）vs NN（n=1,596），mannwhitneyu(alternative='less') P = 3.814e-05 完全吻合，alternative='greater' P = 0.99996；(iii) 分布层面：median GG 1.976e-3 > NN 1.917e-3（中位数确实"marginally above"，ratio 1.03），但 NN 右尾远更重（mean 3.77e-3 vs 2.38e-3；q75 6.2e-3 vs 3.0e-3），经验 P(GG<NN) = 0.534，故随机优势检验在 "healthy < adjacent" 方向显著。即："marginally above" 是中位数陈述，而所贴 P 值是中位数方向相反的随机优势检验结果——当前写法使读者误以为该 P 支持"above"。
【建议】改为："liver healthy and adjacent medians are comparable (1.03-fold; the adjacent distribution carries a heavier right tail, so a stochastic-dominance test is significant toward healthy < adjacent, one-sided P = 3.8 × 10⁻⁵)"，或删去 P 值仅保留中位数可比陈述。主结论（tumor ≫ healthy≈adjacent，ratio 2.0–2.7）不受影响。

**N2（修复遗留，建议）GTEx 段检验未加重叠对标注。**
同段 "TT ≫ NN, P ≤ 3.2 × 10⁻⁸⁴"、"P ≤ 1.4 × 10⁻²⁶" 及 N1 的 P=3.8e-5 均为作用于重叠 pair 集合的 MWU/JT（每样本出现在多对中），未按本文已建立的惯例标注 "pairs treated as independent, descriptive only"（对比：SI composition 段、MS line 30/39 均已标注）。P ≤ 10⁻⁸⁴ 量级的结论不受影响，但 3.8e-5 这种边缘显著度对独立性膨胀最敏感——若保留任何 GTEx P 值，应补一句统一标注。

**N3（既有遗留，trivial）SI 5.3 计数句式。**
SI 5.3（line 236）per-cancer 列举（合计 3,567）与括号内总数 3,535 并列，靠 SI 4.3 的层级句消歧；建议镜像 MS "3,567 samples, of which 3,535 …" 句式以免审稿人重复我上轮的算术疑问。

### 上轮建议级可选项状态（不重复计分）

- P6（Kang 0/30 附 Wilson CI）：未做（Fig. 3d 图注仍无 CI；SI 3.12 有 [0.000, 0.114]）。
- P7（Note 10 分解 CI 补 cell-resampling-only 限定）：未做（SI line 201 的 [2.02, 2.18]、[1.21, 1.41] 仍无限定句；1.74 区间有限定）。
- P8（mouse pilot n=2–4 类别均值标 descriptive）：未做（正文单调性陈述未变；MW 对比已有 descriptive 标注覆盖主要风险）。
- P9（TCGA 五比值补 studentized/BCa）：未做。

## C. 总分与推荐

- soundness 8/10、novelty 6/10、significance 6.5/10、presentation 8.5/10
- **overall 7.5/10，推荐：minor revision**
- 一句话理由：上轮 5 必修项中 4 条完整落地且与 ground truth 逐项吻合，但肝组修复句把相反方向的单侧 P 值贴到了"marginally above"上（N1，唯一必修）；修掉 N1（及建议的 N2 标注）后即可 accept。
