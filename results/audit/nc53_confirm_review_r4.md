# R4 脑图谱 nc53 确认轮终审（commit 4a7a34c，修复提交 69e3567 后）

审稿人：R4-brain。前置阅读：`results/audit/nc52_final_review_r4.md`（本人上轮报告）、
`results/audit/nc53_final_review_round_2026-09-24.md`（轮次汇总）。
复核文本：`results/CKI_Manuscript_NC_fulltext.txt`、`results/CKI_Supplementary_NC_fulltext.txt`；
ground truth：`results/brain_bs_null_results.csv`（31,764 行，q_fdr min 实算）、
`results/CKI_Supplementary_Tables_NC.xlsx`（zip 内 workbook.xml sheet 清单实算）、
`results/audit/nc52_impl_brain.md`。

## A. 逐条裁定表

| # | 条件项 | 裁定 | 引文证据（当前文本原句） |
|---|---|---|---|
| 1 | 脑残差筛查两家族层级（全局 m=31,764 q_min=0.520 vs Bergmann 分层家族 m=21 min q=0.042）无歧义 | **RESOLVED** | MS 第 63 行："no candidate survives FDR correction (minimum q = 0.520)"（全局家族）；第 65 行："the only **sub-nominal stratified family** is intra-cerebellar Bergmann-glia (m = 21; minimum q = 0.042)"（"stratified family" 与 "sub-nominal" 两词把家族层级与显著性层级同时标清）。ground truth 实算：brain_bs_null_results.csv 31,764 行 q_fdr min = **0.5202**，与文中 0.520 一致 ✓。SI 3.3 节（第 107 行）进一步展开两层口径。可选润色：第 65 行 "minimum q = 0.042" 前加 "(family-wise)" 一词可再降读者比对成本，非必需。 |
| 2 | Supplementary Fig. 14 图注新增 | **RESOLVED** | MS 第 214 行图注含全部约定数字："91,838 nuclei; microglial cell 88,494 versus CNS macrophage 3,344 … ω = 21.83 ± 7.20 functional versus 1.30 ± 0.36 neutral; Mann-Whitney P = 5.5 × 10⁻¹⁴; exact rank AUC = 1.00 … k_n … AUC = 0.89"，标题用 "sanity check" 与 Note 16 新名一致 ✓。 |
| 3 | SI 3.3 lower-tail 句尾 rule-matched null caveat 指针 | **RESOLVED** | SI 第 107 行段内实见 "(rule-matched null caveat on reading these tail excesses: Supplementary Note 13)" ✓（位于段中而非句尾，功能等同）。 |
| 4 | xlsx 19 sheets + 四个 docx 描述段补 sheet 指针 | **RESOLVED** | xlsx 实算：workbook.xml 含 **19 个 sheet（Table 1–19）** ✓；SI 指针逐行核实：第 264 行 sheet Table 1、第 267 行 sheet Table 2、第 270 行 "Table content (per-cell-type summary): … (sheet Table 3)"、第 273 行 sheet Table 4 ✓。Table 3 = 10 行类水平检验、Table 4 = 6,591 threshold-passing 候选含 39 Strong（0.12%）/1,171/5,381，与 MS 第 65 行口径一致 ✓。 |
| 5 | 摘要 "(k_n-dominated)" 沿留 proof 阶段 | **RESOLVED（接受安排）** | 摘要现为 197/200 词。"一动就超"的说法略保守——插入 1 词后为 198/200，proof 阶段有空间；鉴于一词改动可能引发重排与三层断言联动，**接受沿留 proof**，条件是 proof 阶段必须执行（1 词即可，无借口）。 |

## B. 新增问题

**Major：无。**

**Minor：**
1. 【修复引入】Supp Fig. 14 图注（MS 第 214 行）末句 "the **validation** value lies in ω tracking…" 残留 "validation" 一词，与 Note 16 更名 "sanity check"、正文第 39 行 "A sanity check on unused data" 的降级口径不一致。建议 proof 阶段改为 "the sanity-check value lies in…"。一词级，不阻断。
2. 【修复引入·改善确认】正文第 39 行 sanity check 句新增 "descriptive—**pairs overlap across four donors**" 限定——这是对 35 个 sample-matched 对跨 4 donor 非独立性的恰当披露，属改善，不计问题；仅记录确认。
3. 【既有遗留·已按约定转可选】supercluster 粒度与文献张力（microglia 区域异质性文献 vs "at or below the null expectation"，MS 第 57 行；Bergmann 分带文献 vs 最低 ω 端点）仍未在 Discussion 协调。按 nc52 轮约定为可选项，维持不阻断；若编辑或审稿人追问，第 60 行加一句即可覆盖。

**脑区数字链复查（防修复引入回归）**：MS 第 56 行 6.10（uncorrected upper bound）/ 3.68 [1.67, 3.97] / 3.66 [1.92, 3.78] / 1.74 [0.80, 2.34] 与审计文档 ground truth（3.660 [3.598,3.705]、donor [1.918,3.779]、span [1.670,3.973]、equal-n [0.804,2.336]）逐一一致 ✓；"(class, region)-level adjustment … 6.33–6.45" 归因修正与 nc52 审计文档（两值均出自 (class,region) 层：6.3276 / 6.4503）一致 ✓；第 60 行 "k_n-dominated … does not by itself establish functional specialization"、第 67 行 39→3 估计器敏感性、第 67 行主题降级句均保持上轮批准文本，无回归 ✓。

## C. 总分与推荐

**7.5/10，推荐：accept（proof 阶段完成两处一词级文字即可）。**
一句话理由：上轮 6 条 Major 与本轮 5 个条件项全部经 ground truth 核实关闭，脑图谱部分的声明-证据匹配已达到该 4 供体死后图谱数据可支持的最严标准，残留仅为 proof 级文字。
