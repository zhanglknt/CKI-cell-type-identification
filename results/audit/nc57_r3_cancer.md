# nc57 终审报告 — R3-cancer（肿瘤基因组学 / TCGA）

- 审稿人：R3-cancer（Nature Communications 肿瘤基因组学方向）
- 对象：v0.5.3 终稿（nc56 proof 轮后；`results/CKI_Manuscript_NC_fulltext.txt` 全文通读，SI 抽查 Note 8/9、Section 1.7/3.13、Methods 5.12）
- 上轮报告：results/audit/nc55_blind_review_R3.md（8.0/10，minor revision，N1–N4）
- proof 变更对照：results/audit/nc56_proof_fix_matrix.md
- 数字复核来源：当版文本逐句核对 + nc52_tcga_pancancer_excc.csv、nc52_gtex_summary.json、nc52_gtex_kn_by_grouptype.csv、nc52_tcga_knfloor_sensitivity.csv、nc52_lihc_cox_excc.csv/_zph.csv、nc52_tcga_luad_adjmodel_permutation.csv、nc52_tcga_deconv_feasibility.json

---

## 总评分：**8.5 / 10**

## Verdict：**accept**（唯一新发现为一词级精度瑕疵 N5，可在 proof 顺带修正，无需再见稿）

一句话总评：我上轮 4 条 Minor 全部落地且措辞精准，proof 轮编辑在肿瘤学口径上未引入任何回退或数字矛盾，仅存 SI 一句新增限定句的区间端点未覆盖肾脏的精度瑕疵；TCGA 部分已达可发表状态。

---

## 一、上轮问题逐项核销

| # | 上轮问题 | 裁定 | 当版文本证据 |
|---|----------|------|--------------|
| N1 | SI Note 8 "KIRC 754" 与 MS "KIRC 750" 无调和 | **RESOLVED** | SI line 190 现为 "(LIHC 366 and KIRC 754 tumors, **750 KIRC retained at pair level**; seed 42…)"——矩阵口径与 pair-level 口径一句话调和，与 deconv json（n_tumors_excc=754）及 ex-CC CSV（n_tumor=750）同时对上。 |
| N2 | "floor never reached" 字面不准（KIRC NN 1/3,321 对触及） | **RESOLVED** | MS line 49 现为 "the housekeeping floor (k_n ≥ 10⁻⁴) is **essentially** never reached, leaving ratios identical across floors 0–10⁻⁴"——"essentially" 覆盖 1 对例外（敏感性表 frac 0.0003，比值 1.8804→1.880 不变），表述精确度可接受。 |
| N3 | Discussion "attenuation is strongest where the reversal is weakest" 超数据 | **RESOLVED** | MS line 75 现为 "the shift is largest in LIHC (+44%, the weakest reversal) and KIRC (+20%)"——正是上轮建议措辞；KIRC 不再被纳入"最弱反转"的对应声明。 |
| N4 | Introduction "confirm as tumor-specific" 未 hedge | **RESOLVED** | 摘要 line 8："GTEx references in lung, liver, and breast are consistent with tumor-specific elevation"（限定三器官+consistent）；Introduction line 14："GTEx references support as **largely** tumor-specific"（"largely" 覆盖肾脏例外，Results line 50 随即披露例外）。 |

**核销汇总：4/4 RESOLVED。**

## 二、proof 轮（nc56）编辑的新问题排查

逐条对照 nc56_proof_fix_matrix.md 中与我领域相关的编辑（A3/A4/M15/M16/S1/X 系列），结论：

- A3（摘要 GTEx 句）："consistent with tumor-specific elevation" 限定 lung/liver/breast，与 Results/SI 口径一致，无过强 ✓
- A4（"four of five CIs excluding 1"）：与 ex-CC CSV（LIHC [0.943,1.302] 跨 1，其余四个排除 1）一致 ✓
- M15（Discussion "…over a field effect **within cohorts**"）：与 SI line 189 "mechanistic claims therefore rest on within-cohort orderings only" 口径一致 ✓
- M16（"attenuates"→"shifts"）：pooled −0.9% 为双向偏移的中性表述，更准确 ✓
- S1（SI Note 8 新增跨队列不确定度句）：**见 N5（唯一新发现）**
- 其余编辑（M1–M14、X1–X8、S2–S4）经通读确认未触及肿瘤学数字与口径；指针无断裂（S4 "Section 5.13a" 已修）；Fig 4 图注（"while the NN/TT ratio of k_f does not"）与 Fig 5(d)（"Top 5 conserved"）保持正确。

### 新问题清单

**Major：无。**

**Minor：**

- **N5（proof 引入，一词级）SI Note 8 跨队列句区间端点未覆盖肾脏。** line 189 新句："The cross-cohort shift (GTEx–adjacent versus GTEx–GTEx pair k_n, ratio ≈ 1.8–2.3×) bounds the resolution of the healthy–adjacent comparison…"。ground truth 复算（nc52_gtex_kn_by_grouptype.csv，organ 级中位数 GA/GG）：lung 1.82、liver 2.29、breast 2.24 均在区间内，但 **kidney 1.57 在区间外**；而前一句 "elevated to tumor levels in every organ (P ≤ 1.4 × 10⁻²⁶)" 的 "every organ" 含肾脏（KIRC P=1.38e-26 正是最弱者）。肾脏已在同段被排除出结论（"no conclusion is drawn for KIRC"），故对结论无影响，但区间写法与 CSV 字面不符。建议改 "ratio ≈ 1.8–2.3× in the three informative organs (kidney 1.6×)" 或径直放宽为 "≈ 1.6–2.3×"。

## 三、当版关键数字复核（全部取自当版文本并对照输出文件）

- 泛癌反转：line 47 "LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11; cluster-bootstrap CI excluding 1 in four of five" —— ex-CC CSV 2.464/1.880/1.708/1.567/1.112，LIHC CI [0.943,1.302] 跨 1 其余排除 ✓
- k_n 倍数：line 47 "1.3–3.3-fold"（mean ratio 1.337–3.292）✓；line 8 摘要同口径 ✓
- ex-CC 样本口径：line 94 "3,567…3,535…leaving 366"、line 112 "34,828…478…35,306" ✓
- LUAD 驱动分层：line 48 KW P=7.8×10⁻⁷、置换 KRAS P≤0.001/EGFR P≥0.28、~84% log-ω gap、残余混杂披露 ✓（与置换 CSV/SI 3.13 一致）
- 映射两口径：line 49 "linear 1.11 [0.94, 1.30] versus softmax 1.29 [1.09, 1.53]" ✓
- Cox：line 49 "ω HR per SD 1.08 [0.88, 1.33], P = 0.467; k_f likewise null" ✓；zph M2 GLOBAL P=0.023 在 SI 3.13/5.12 披露（CSV 0.02255）✓
- GTEx：line 50 "healthy/adjacent ≈ 1.0–1.2"（1.031–1.207）、"2.0–2.8-fold"（TT/NN 中位数 2.06–2.78、TT/GG 2.01–2.66）、肾脏例外 ✓；SI 189 各组中位数、肝 MWU P=3.8×10⁻⁵（方向已正）、TT≫NN P≤3.2×10⁻⁸⁴、GA P≤1.4×10⁻²⁶ 逐一吻合 ✓
- severity：SI Note 9 Edmondson 78.8/75.8/77.6/72.3、JT P<10⁻¹⁵、k_f 8.4×10⁻¹² 与 severity CSV 一致；vignette 定位未回退 ✓

## 四、修改建议

1. （可选，一词级）SI line 189 跨队列句区间按 N5 修正为含肾脏口径或限定三器官。

除此之外无修改要求。TCGA 部分证据链完整、口径一致、阴性披露充分，建议接受。
