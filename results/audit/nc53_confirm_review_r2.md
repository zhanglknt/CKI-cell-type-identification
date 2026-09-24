# nc53 确认轮报告 — R2（单细胞/细胞组成审稿人）

- 审稿对象：修复提交 69e3567 工作树；MS/SI fulltext（与 docx 同时间戳）、`CKI_Supplementary_Tables_NC.xlsx`（19 sheets）
- 前轮报告：`results/audit/nc52_final_review_r2.md`；轮次汇总：`results/audit/nc53_final_review_round_2026-09-24.md`
- 日期：2026-09-24；方式：仅评审，所有指控先对当前文本/输出文件做 ground truth 复核

## A. 逐条裁定表

| 条件项 | 裁定 | 引文证据（当前文本原句 / 输出文件） |
|---|---|---|
| A1（5,151 指针落空+口径） | **RESOLVED** | MS Discussion：「permuting k_n across the 5,151 **full-inventory** human pairs predicts Spearman 0.524 … observed value is 0.089 (Supplementary Note 9)」；SI Note 9 新增「k_n-permutation floor (v52)」段：floor 0.524 [0.506, 0.541] vs 0.089（human 5,151）、0.857 [0.843, 0.870] vs 0.821（mouse 703），明示「102-entry inventory before the 99-entry filter that yields the 4,851 analyzed pairs」——与 `nc52_stats_omega_kf_math_floor.csv` 逐字吻合，且两对集口径差异已书面披露。我原指控中"系笔误"的部分经 ground truth 裁定反转，接受此处理 |
| A2（Methods 35,306 陈旧） | **RESOLVED** | MS Methods：「linear-normalization pair table (**34,828 pairs after dropping the 478 pairs** touching the 32 cell-line-derived aliquots from the 35,306-pair table …)」——35,306 仅以历史来源身份出现，正确 |
| A3（分癌种计数 3,567≠3,535） | **RESOLVED** | MS Datasets：「…BRCA 1,010 + 109 (**3,567 samples, of which 3,535 enter** the pair-level analysis after the barcode-audit exclusion below; all 32 excluded cell-line aliquots are LIHC tumors, leaving 366)」——两口径一句话桥接，无歧义 |
| A4（Table 11 表注 Fig. 5a） | **RESOLVED** | xlsx 新 sheet11（Table 11）表注末句：「Ranked by NN/TT effect size (**main-text Fig. 4a**)」；xlsx 已扩至 19 sheets（Tables 1–19），SI 表 1–4 描述段各带「Table content: CKI_Supplementary_Tables_NC.xlsx (sheet Table N)」指针 |
| A5（KIRC 750 vs 754） | **RESOLVED** | SI 4.3 队列层级句：「The ex-CC default cohort excludes the 32 … leaving 3,535 samples (LIHC 366 tumor + 57 normal) …; the GTEx comparison and the reference-free composition fallback … instead use the full expression-matrix cohort (**3,596 samples, e.g. KIRC 754 tumors**)」——pair-level 750 与全矩阵 754 两种样本集定义书面分层，清晰无歧义 |
| B3（deconv 零引用） | **RESOLVED** | MS Results 末句：「pending single-cell validation (**reference-free composition check: ρ = 0.20–0.26 versus k_n**; Supplementary Note 8)」；SI Note 8 新增「Reference-free composition fallback (v52)」段：CIBERSORTx/BayesPrism 不可行原因、NNLS（seed 42、60 markers、全矩阵队列 LIHC 366/KIRC 754）、split-half ρ=0.934/0.964、与 k_n 相关 0.20/0.26、解读句「measurable composition shifts explain at most a small share」——与 `nc52_tcga_deconv_feasibility.csv` 一致 |
| B1（field-effect 措辞强度） | **PARTIAL（接受延期）** | 断言式措辞仍在 4 处：摘要「GTEx references argue against a field-effect reading」、Intro「GTEx healthy references **confirm** as tumor-specific」（语气最强）、Results「tumor-specific rather than a field effect」、Discussion「supporting … over a field effect」。属措辞校准而非事实错误（Note 8 已披露 GA 跨队列效应），且已列入汇总文档遗留清单。接受留待 proof 阶段，**条件：proof 修复须覆盖全部 4 处**，统一降为 "consistent with" 量级，并在 Note 8 GTEx 段补一句跨队列比对不确定度（GA/GG 1.8–2.3×）的量化说明 |
| B2（KIRC 句"strongest where weakest"） | **PARTIAL（接受延期）** | Discussion 仍作「attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)」——KIRC reversal 1.88 为第二强，归类不准确。同列遗留清单，接受 proof 阶段处理 |
| C1（地板分析 dataset-dependent） | **RESOLVED** | Note 9 新段末：「the high mouse ω–k_f correlation is mathematically forced and **dataset-dependent**, not biological coupling」 |
| C2（乳腺 2.77× 超 "2.0–2.7" 上限） | **NOT RESOLVED（遗留 minor）** | MS Results 仍作「tumor k_n is 2.0–2.7-fold higher」；`nc52_gtex_kn_by_grouptype.csv` 乳腺 2.41e-3/8.69e-4=2.77×。可随 B1 一并改 |
| C3（microglia 窗口合规说明） | **RESOLVED** | Note 16 改名「Human-Brain **Sanity Check**」并加「within the recommended 50–200 cell operating window」（注：入组阈为下界，个别大半分裂可超 200，但该处推断为跨对 MWU 而非 per-pair permutation，无实质影响） |
| C4（"38% misreports" 未标注仿真来源） | **NOT RESOLVED（遗留 minor）** | Discussion 仍作「under fourfold cell-count imbalance k_f misreports 38% of neutral pairs, ω none」，无 (simulation) 标注；数据出处确为 `groundtruth_simulation_metrics.json`。一词之改，建议随 proof 处理 |

## B. 新增问题

**Major：无。**

**Minor（2 条，均为本轮修复引入）：**

1. 【修复引入】**Table 5 表注引用已被取代的 composition 数字**。xlsx sheet5（Table 5，表头自称 "ex-CC cohort, v52"）表注末段：「composition-sensitivity conclusion is unchanged (pooled tumor-pair coefficient attenuation **−1.3%**, cluster-bootstrap median −1.3% [95% CI **−4.8%, +2.0%**] at B = 1,000)」——这是 v44 排除前口径；ex-CC 权威值为 **−0.9% [−4.3%, +2.5%]**（Note 8 v52 段、MS 第 49 行）。同一张 ex-CC 表里引用排除前数字，构成跨文档数值不一致。建议改为 −0.9% [−4.3, +2.5] 或标注"pre-exclusion sensitivity"。
2. 【修复引入】**MS 第 49 行 deconv 句 ρ 指代不明**。「pending single-cell validation (reference-free composition check: ρ = 0.20–0.26 versus k_n; Supplementary Note 8)」——未说明 ρ 是什么与 k_n 的相关（Note 8 中是"非实质分数 vs per-tumor k_n"），不看 SI 的读者无法解析。建议改为"a reference-free non-parenchymal fraction correlates only weakly with k_n (ρ = 0.20–0.26)"。

**既有遗留（不重复计分）**：C2、C4 两条 minor 未修（见裁定表）；另注一句——Note 8 回退段「explain at most a small share」在 KIRC 上依赖于一个对 ESTIMATE 仅 ρ=0.24 外部效度的估计量，该句强度主要由 marker-panel 主检查承载，无需修改，仅备案。

**修复引入的一致性复查（度量学术语/基准声明/跨器官口径）**：cross-organ 段（4,851/59/n≥5/k_f-only caveats）与上轮一致无新矛盾；基准声明（T1 28.6%、"continuous divergence metrics"限定、scDist Python approximation 披露）未变；术语面「sanity check」已在 MS、Note 16 标题、Fig. 14 图注三处统一；Table 1 表注与 Fig. 14 图注新增后与正文数字（9.93±4.62、21.83±7.20 vs 1.30±0.36、P=5.5×10⁻¹⁴、AUC=1.00、k_n 0.89）逐项吻合；摘要 3.7-fold [1.9, 3.8] 与 Results 3.66 [1.92, 3.78] 一致；摘要"1.3–3.3-fold"与 Table 11 k_n 列（1.34–3.29）一致；JT P 值已规范（P < 10⁻¹⁵），残留 "P ≈ 0.005" 为最小可分辨 P，属正当用法。

## C. 总分

- **8.0 / 10，推荐：accept**（条件性，见下）
- 一句话理由：上轮全部必修项（A1–A5、B3）经 ground truth 复核逐项 RESOLVED 且无返修性错误，遗留仅为 2 条修复引入的数值/指代 micro-fix 与已协商延期的措辞项（B1/B2/C2/C4），证据链与自我限定声明达到 NC 方法学论文标准。

**转无条件 accept 的前置清单**：① B1 四处措辞 + Note 8 不确定度句（proof 阶段，已跟踪）；② B2 KIRC 句改写（proof）；③ 新增 minor 1（Table 5 表注 −1.3%→−0.9%）；④ 新增 minor 2（ρ 指代）；⑤ C2（2.0–2.7→2.0–2.8）、C4（加 "(simulation)"）顺手修复。
