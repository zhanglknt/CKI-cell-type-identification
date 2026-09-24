# nc52 终审报告 — R2（单细胞/细胞组成审稿人）

- 审稿对象：commit 7133b43 工作树；MS `results/CKI_Manuscript_NC.docx`（以 `CKI_Manuscript_NC_fulltext.txt` 为准，时间戳与 docx 同步）、SI `CKI_Supplementary_NC.docx`、附表 `CKI_Supplementary_Tables_NC.xlsx`、Guide `CKI_Reproducibility_Guide_NC.docx`
- 审查重点：细胞组成分析、deconv 可行性、方法学比较、单细胞队列口径
- 日期：2026-09-24

## 一、上轮（v51r2，7.0 minor）条件落实核查 —— 全部对照输出文件 ground truth 复核

| 上轮条件 | 落实情况（ground truth 依据） |
|---|---|
| CC 样本默认排除 | ✅ SI 1.7/3.13：ex-CC 默认链 `nc52_tcga_excc_main.py`，34,828 对（35,306−478 CC-touching）；MS Results 第 47 行声明"All TCGA results exclude 32 cell-line-derived aliquots"；LIHC NN/TT 1.11 [0.94, 1.30]（four of five）与 Table 11 xlsx 渲染值逐项一致 |
| linear vs softmax 两口径 | ✅ Guide 5.13e + Supp Table 5：LIHC linear 1.11 [0.94,1.30] vs softmax 1.29 [1.09,1.53]（five of five），MS 第 49 行如实报告 mapping-sensitive |
| kn_floor 敏感性 | ✅ MS 第 49 行 + Guide 5.13e：floor 0–1e-4 所有比值不变（无 pair-level k_n ∈ (0,1e-4)）；1e-3 才截断 ~50% NN 对——上轮"aggregate k_n 坐地板"疑虑消除 |
| composition 异质性披露 | ✅ Note 8 v52 段：25,015 ex-CC 对，pooled −0.9% [−4.3,+2.5]，LIHC +44.1% [+29.9,+60.0]、KIRC +19.7%、BRCA −15.9%、LUSC −9.0%、LUAD −2.0%，ρ=0.380——与权威口径逐项一致；MS Discussion 第 75 行如实承认"marker-measurable composition likely contributes in those types" |
| 健康参照（field effect） | ✅ 新增 GTEx 第三组（Note 8 v52 段 + Guide 5.13g）：肺/肝/乳腺 adjacent≈healthy（1.0–1.2×）、tumor 2.0–2.7×；肾例外（n=28，自溶）如实披露；`nc52_gtex_kn_by_grouptype.csv` 中位数逐项核对一致 |
| deconv 可行性 | ✅ Guide 5.13f：`nc52_tcga_deconv_feasibility.json` 记录 CIBERSORTx（无 token）与 BayesPrism（锁定环境无依赖链）不可执行的原因，并存档 TS 参考的 marker-NNLS 回退（LIHC n=366=398−32 ✓、KIRC） |
| LUAD 调整模型置换 | ✅ Guide 5.13d：whole-tumor 标签置换 B=10,000 重拟合全模型，KRAS P≤0.001、EGFR-WT P≥0.28；MS 第 48 行已写入 |
| 7.70 基线伪重复 | ✅ SI 3.10/Note 3 + MS 第 24 行：两阶段 bootstrap [6.38, 9.82]，旧 [7.37,8.02] 明确标注 pseudo-replicated and superseded；ω_cal 分辨率降级为约一位有效数字（Discussion 第 69 行） |
| Tabula 相关 P 值独立性 | ✅ SI 5.5 新增段：四条 ω–标准度量相关改为 entry-clustered bootstrap CI（99 entries，B=5,000），全部排除 0；`nc52_stats_tabula_entrycluster.csv` 一致；旧 "P < 10⁻¹⁴⁵" 口径明确退役；MS 第 30 行 Mann-Whitney 标注"descriptive" |
| 脑梯度混杂 | ✅ 组合 span+size 对照 3.66（donor bootstrap [1.92,3.78]，LODO 恒 >1）升为 headline（摘要与第 56 行）；equal-n 1.74 因 donor CI [0.80,2.34]（12.6% 低于 1）降级为敏感性；(class,library)/(class,region) 质量回归（深度/UMI/线粒体）调整后 6.33–6.45，Note 10 v52 段一致；PMI 不可排除保留在 Limitations |
| ω vs k_f 增量 | ✅ Discussion 第 70 行重构为"What ω adds beyond k_f is calibration, not detection power"：`nc52_stats_omega_vs_kf_realdata.csv`（4:1 imbalance k_f 误报 0.38 vs ω 0.00；Kang CD14 k_f 0.98 跟随 drift vs ω 0.55）+ `nc52_stats_omega_kf_math_floor.csv`（TS 观测 0.0895 vs 数学地板 0.5241 [0.5058,0.5412]）；第 71 行保留"on real-data orderings the increment is not established"的诚实表述 |
| 候选筛查效应量 | ✅ 第 67 行："spatial patterning without establishing anatomical themes"+ 估计器敏感性（global-k_n 下 39 个 Strong 仅 3 个存活）；主题叙事保留但全部降级为 hypothesis |
| Microglia "验证" | ✅ 降级为 "sanity check"，Mann-Whitney 标注"descriptive—pairs overlap across four donors" |
| LIHC Cox | ✅ Guide 5.13b：ex-CC n=272/79 events，R survival::coxph，stage 分类变量，cox.zph 报告（M2 GLOBAL P=0.023）；HR 1.08 [0.88,1.33] P=0.467 与 MS 第 49 行一致 |

结论：上轮全部硬性条件已落实，且多处超出要求（GTEx 第三组、质量回归加线粒体、组合对照、donor bootstrap、数学地板分析）。

## 二、本轮新发现问题（分级）

### A. 必须修复（口径/指针同步错误——均有 ground truth 依据，非措辞偏好）

**A1. Discussion 第 70 行 SI 指针落空 + 对集口径未披露。**
MS：「permuting k_n across the 5,151 human pairs predicts Spearman 0.524 between ω and k_f, yet the observed value is 0.089—the structured baseline decorrelates them (Supplementary Note 9)」。
核查：SI 全文 grep `0.524`/`5,151`/`5151` 均为 0 命中——Note 9 不含该分析的任何文字；数据文件存在（`results/nc52_stats_omega_kf_math_floor.csv`：TS 5,151 对、观测 0.0895、地板 0.5241 [0.5058, 0.5412]，B=1,000 seed 42）但 SI 无对应小节。另外 5,151=C(102,2)（phase33 inventory，含未过 filtering 的 3 个 entry），与全文其他所有 TS 分析口径 4,851（99 entries）不同，MS 未披露这一对集差异。
要求：在 Note 9（或 5.5）补写该分析小节（脚本、B、seed、文件指针、5,151 对集口径说明），或把 MS 指针改到实际文档位置。

**A2. MS Methods（Per-sample divergence, 第 112 行）TCGA 对数陈旧。**
写"linear-normalization pair table (35,306 pairs...)"，与 ex-CC 默认口径 34,828（SI 3.13、Guide 5.13a）及 MS Results 第 47 行"All TCGA results exclude..."直接矛盾。
要求：改为 34,828 并注明 478 CC-touching 剔除（与 SI 3.13 同口径）。

**A3. MS Methods（Datasets, 第 94 行）分癌种样本数为剔除前口径。**
LUAD 493+76、LUSC 534+58、LIHC 398+57、KIRC 750+82、BRCA 1010+109 合计 3,567，但同句括号写"3,535 samples entering the pair-level analysis after the barcode-audit exclusion"。读者自加得到 3,567≠3,535。ground truth：ex-CC LIHC 肿瘤 366（`nc52_tcga_deconv_feasibility.csv` n_tumors_excc=366=398−32 ✓）。
要求：分癌种数字改为 ex-CC 口径（至少 LIHC 366+57）或明确标注"per-cancer tallies shown pre-exclusion"。

**A4. Supplementary Table 11 表注图号指针错误。**
xlsx Table 11 表注末句"Ranked by NN/TT effect size (main-text Fig. 5a)"——主文 pan-cancer 为 Fig. 4a（Fig. 5 是 cross-organ）。
要求：改为 Fig. 4a。

**A5. 待核实：KIRC 肿瘤数 750 vs 754。**
MS 第 94 行"KIRC 750 + 82"；`nc52_tcga_deconv_feasibility.csv` n_tumors_excc=754。差 4 例，需核对哪一个是进入 pair-level 分析的权威数（若是"有 pair 覆盖的肿瘤数"差异，请在 Guide 注明）。

### B. 实质性解释问题（建议修，不阻断）

**B1. GTEx 反 field-effect 论证存在内部张力（组成分析核心问题）。**
论证链的关键一环"adjacent-normal ≈ healthy（healthy/adjacent ≈ 1.0–1.2）"是**跨队列**比较；而作者自己的 GA（GTEx×adjacent）对显示队列间技术位移达 1.8–2.3×（肺 GA 中位 2.07e-3 vs GG 1.14e-3；肝 GA 4.52e-3 甚至超过 TT 3.98e-3；`nc52_gtex_kn_by_grouptype.csv`）——与被定位的效应（TT/NN 2.0–2.7×）同数量级。即跨队列 k_n 可比性的噪声下限恰好覆盖"adjacent vs healthy"这一格，GG≈NN 的相似性可能掩盖 ±2× 的真实差异。作者已披露"mechanistic claims rest on within-cohort orderings only"，但摘要"GTEx references argue against a field-effect reading"与 MS 第 50 行的肯定语气超出了该证据强度。
建议：摘要改为"consistent with tumor-specific housekeeping elevation"类表述；Note 8 GTEx 段增加一句量化说明（GA/GG 比值 1.8–2.3× 给出跨队列比对的不确定度量级，healthy–adjacent 相似性应在此容差内解读）。

**B2. KIRC 是 reversal 第二强（1.88）却同时是 composition attenuation 第二高（+19.7%）且 GTEx 参照失败（n=28 自溶）的癌种。**
Discussion 第 75 行"attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)"对 LIHC 成立，但 KIRC reversal 1.88 并不"weak"——该句对 KIRC 的归类不准确，且 KIRC 恰好是三处不确定性（组成、参照缺失、mapping 不敏感但其 k_n CI [2.54,4.34] 最宽之一）叠加的癌种。
建议：改写该句为仅对 LIHC 的陈述，并单独一句说明 KIRC 的组成贡献与参照缺失。

**B3. deconv 回退分析做了但正文/SI 无任何引用。**
`nc52_tcga_deconv_*.csv`（LIHC/KIRC，TS 参考 NNLS）只在 Guide 5.13f 存档；其非上皮分数与 k_n 相关仅 0.20/0.26、与 ESTIMATE 相关 0.59/0.24——无论结论方向如何，这是读者应看到的证据（哪怕是"回退分析不足以定论"）。MS 目前只说"deconvolution-based validation remains necessary"，读者无从得知已做尝试。
建议：Note 8 增加一段引用回退结果并给出明确解读（支持/不支持/不确定），或明确声明尝试后判定不充分。

### C. Minor

- C1. 数学地板分析仅引用 TS；同一 csv 显示 mouse full matrix 观测 0.82 vs 地板 0.857（无去相关）——建议 Discussion 加半句"dataset-dependent"以免过度推广。
- C2. GTEx 乳腺 TT/NN = 2.41e-3/8.69e-4 = 2.77×，略超 MS 第 50 行"2.0–2.7-fold"上限；改"2.0–2.8"或给逐器官数值。
- C3. MS 第 39 行 microglia 半分裂 neutral 的组入阈（microglia ≥200 细胞、CNS-Mφ ≥100）落在推荐操作窗（50–200）边缘，Guide 5.12 已记录；建议在 Note 16 补一句窗口合规性说明。
- C4. Discussion 第 70 行"under fourfold cell-count imbalance k_f misreports 38% of neutral pairs"来自仿真（groundtruth_simulation_metrics.json），非真实数据——该行上下文夹在两真实数据句之间，建议加"(simulation)"。

## 三、评分与结论

- 方法可靠性 soundness: 7.5/10 —— 上轮全部硬性条件落实且多处超要求；新发现问题均为可即时修复的同步错误，GTEx 论证需降半格语气
- 新颖性 novelty: 6/10
- 意义 significance: 5.5/10 —— GTEx 与分解优先框架提升了实用价值，但操作窗与 k_f-only 回退建议仍限制影响面
- 表达 presentation: 7.5/10 —— caveat 与结论的层次比上版清晰（headline/敏感性分级到位），但 A1–A4 这类指针/口径错位在 NC 送审版不应出现
- **总评 overall: 7.5/10，verdict: minor revision**

### 放行条件清单（全部修复后可转 accept）
1. A1：补齐 Note 9/5.5 的 k_n 置换分析小节 + 5,151 对集口径说明（或修正指针）
2. A2：MS Methods TCGA 对数 35,306→34,828
3. A3：分癌种样本数改 ex-CC 口径或加注
4. A4：Table 11 表注 Fig. 5a→Fig. 4a
5. A5：核实 KIRC 750 vs 754
6. B1：摘要/正文 GTEx 语气降为"consistent with"，Note 8 补跨队列不确定度说明
7. B2：改写"strongest where weakest"句并单独处理 KIRC
8. B3：Note 8 引用 deconv 回退结果或声明其不充分
9. C1–C4 顺手修复
