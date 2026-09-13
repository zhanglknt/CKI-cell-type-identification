# 一作（吴宪明）v46 稿件修改与问题盘点

日期：2026-09-05
来源：主目录 v46_manuscript.zip（一作回传），解压至 _tmp_fa_review/（临时）
提取：95 处修订（48 ins + 47 del）+ 6 条批注 + 问题文档 7 项 + 22 个图件 + 4 个 Table CSV
方法：extract_revisions.py 提取修订/批注；接受全部修订后的最终文本 fa_final_text.txt 与 v46 包 CKI_Manuscript_fulltext.txt 句子级 diff（无非跟踪编辑，全部差异均可归因于 95 处修订）；图件 sha + 视觉逐一对比。

## 一、文字修订（已确认全部来自修订记录，无暗中改动）

### A1. Results 数字改动（1 项）
- AUC 0.786 → 0.648（Tabula Muris 参数扫描 identity-only），2 处：Results 正文 + Fig S1 图例。依据：他重跑的 phase32_sweep_results.csv（identity_only AUC=0.6482, u=4806, p=0.0119；与我们 results/ 版本 0.7855/u=2930/p=6.6e-6 冲突；两边 omega_mean 几乎一致 5.71 vs 5.73 → AUC 差异来自 pair 集合/标签构成不同，我们 u 反推 same-CT pairs≈5，他的≈11）。
- SN 内另有 2 处 "AUC = 0.786"（参数扫描 Note + Table S1 描述）需同步。

### A2. 主图图例改写（panel 删减）
- Fig 2：删旧 C（ω vs standard metrics 相关性条图），旧 D→新 C；正文 Fig. 2B,D→2B,C（2 处含 Methods/统计段）。
- Fig 3：删旧 B（ω vs k_n 散点）、D（ω by category）、E（AUC vs interpretability），旧 C（ROC）→新 B。
- Fig 4：删旧 C（PAM50）、D（SES）、E（cross-cancer matrix）。正文 PAM50/severity 文字全部保留（11 处 PAM50、7 处 severity 命中），无悬空 panel 引用。
- Fig 5：仅 "Table of top 5"→"Top 5" 措辞。
- Fig 6：删旧 C（astrocyte region×region matrix），旧 D→C、旧 E→D。新 C 图例保留 v46 反富集声明文字版（"null expects 148.3 candidates, observed 39 anti-enriched, P(null count ≥ 39) = 1.0"）——图内注释框在他的重画版中丢失，但图例文字保留 → 可接受。

### A3. 附图重编号（正文引用 ~14 处 + 图例头 + SN 7 处交叉引用）
他的映射：S4→S3, S5→S4, S6→S5, S7→S6, S8→S7, S9→S8, S10→S9, S11→S10, S12→S11；S13/S14 暂留（留 S12 空号，他注明"等 S13 确认后重排"）。
删旧 Fig S3（method comparison ROC bar；批注56：与 Fig 3 重复、mean AUC 无意义）；正文 1 处引用随之删除。
落包建议：直接连续化——Kang S13→S12，QQ S14→S13，最终 S1–S13 无空号。
SN 交叉引用需同步：Figure S11→S10、Figure S9→S8、Figure S12→S11、Figure S7→S6、Fig. S13→S12、Fig. S14→S13。

### A4. 附图图例改写
- S1：HK sweep 段 "showing convergence at ~200-300 HK genes" → "k_n decreases monotonically with increasing HK gene number (250–1,000), indicating that the baseline rate is gene-set-size-dependent; absolute w values are therefore scheme-specific..."（注：有笔误 "absolute w values" 应为 ω，落包时顺手修）
- S2：整段重写 → "Calibrated ω under two baselines"（mouse 7.70 + brain-internal 9.73；1.26-fold overstatement）
- S4：删 "Complete table of 59 same-cell-type cross-organ pairs (Table S2)" 句（批注63：表放在图例不合适）
- S5（脑区详情）：旧 A-E 全删（批注69/71：旧 panel 错误/重复），新 A-C：A 显著性排序条形、B ω vs n_regions（ρ=0.46, P=0.18 不显著——修正旧版"associated with greater divergence"错误表述）、C 残差分布分层
- S6（pair-specific k_n）：整段重写；删旧 "CV = 97.52%"（他的色条 CV 0.37–0.70，旧值错误）
- S7（发育签名）：B/C 重写（B tier 构成按 Strong 数排序+百分比标注；C top-10 + OL inset 声明 12/39 fold 0.77 P=0.92）
- S9（cross-species）：删 B/C panel 描述（批注99：B 是随机数据、C 无逻辑）

### A5. 他版本里遗留、需要落包时修正的小问题
1. cross-species 图例头仍写 "Figure S10"（他忘了改成 S9）——正文引用已是 S9
2. 新 S7 图件 panel 顺序（B=top10, C=tier 构成）与图例顺序（B=tier, C=top10）不一致——改图例字母
3. S4 图例句末双句点 "distribution.."
4. S9 单 panel 图但图例带 "(A)"——可保留
5. S1 图例 "absolute w values" → ω
6. 批注72 为空批注——忽略
7. Table_1-2.docx：数据零改动；标题 "Supplementary Tables"→"Tables"（采用他的）

## 二、图件对比（他的 22 个 PDF vs v46 包）

| 图 | 内容 | 处置建议 |
|---|---|---|
| figure1 | 同 5 panel，视觉升级；panel D 补回 4 类散点（v46 包版只剩 C 类点，是退化）| 采用他的 |
| figure2 | 3 panel（删旧 C）重画 | 采用他的 |
| figure3 | 2 panel（A 热图+B ROC）| 采用他的 |
| figure4 | 2 panel，B 加中位数标注（160/106 等）| 采用他的 |
| figure5 | 同 4 panel 视觉升级 | 采用他的 |
| figure6 | 4 panel，新解剖示意图（明显优于 v46 简笔）；B 保留 equal-n 1.74 注释 | 采用他的 |
| GA | **标题写成 "CKI: A Cell-state Kinetic Index"——与稿件定名 "Ka/Ks-inspired" 不一致**（疑旧文件混入）| **保留 v46 版 GA，不用他的** |
| figure_S1 | 他重跑数据（k_n 递减 0.0151→0.0070；AUC 0.648/0.642/0.608/0.549）| 决策点 D1 |
| figure_S2 | 双 baseline 新版（修正 v46 包版图仍用旧 6.67 基线的滞后问题）| 采用他的 |
| figure_S3–S11 | 重编号对应旧 S4–S12，内容一致或他重画（S5/S6/S7 重画与图例一致）| 采用他的 |
| figure_S12（他包名 S13）| Kang IFN-β，仅格式优化（panel 标签不再撞标题）| 采用他的 |
| figure_S13（他包名 S14）| QQ，视觉与 v46 一致（字节差异为再导出）| 保留 v46 版即可 |

## 三、问题文档 7 项

- Q1 Fig S1 ABC 数据不对、结果文件无对应 → 他用 notes 代码重跑重做。**与 results/ 现有 CSV 冲突**（hk_stability_sweep.csv 递增 vs 他递减；phase32 AUC 0.786 vs 0.648）。注意：复现包 zip 内只有脚本无这些 CSV（他说"没有对应结果"部分属实——指复现包）。决策点 D1。
- Q2 Table S1-S4 映射 + "S3/S4 指向同一文件？" → 属实：SN 中 S3 与 S4 的数据文件都是 brain_bs_null_observed_pairs.csv（S4 为其 6,591/31,764 行 tier 筛选视图）。处置：采用他提供的 4 CSV 映射（S1=phase32_sweep_results、S2=phase35_cross_organ_conservation、S3=brain_bs_null_observed_pairs + ct_test 汇总、S4=同文件筛选视图），SN 文字澄清 S3/S4 关系。
- Q3 Fig S13 无法验证（GEO 下载缺 ensg2sym.tsv）→ 他建议 Discussion 加句（给了具体文本：CD14+ monocytes ω AUC 0.55 vs k_f 0.98；anchor stationarity 假设；cross-metric contrasts）。处置：采纳加句（决策点 D4）；ensg2sym.tsv 链路由我们补进复现包；采用他的格式版 S13。
- Q4 Fig S14 置换重跑一致（他重跑 lower 5.967%/upper 6.842% vs 原 6.0%/6.8%），保留原图 → 无需改动；本文件即验证记录。
- Q6 附图中无 S12 编号，等 S13 确认后全部重排；目前编号↔引用对应正确 → 落包直接连续化（决策点 D2）。
- Q7 参考文献最后统一调整 → 投稿前处理，不阻塞本轮。

## 四、决策点

- D1：Fig S1 数据（他的重跑 vs 我们 results CSV）——a) 采用他的（图+0.648+递减曲线+替换 2 个 CSV+同步 SN）；b) 先独立重跑 01b+04 验证谁对再定；c) 保留我们的
- D2：编号连续化现在做（Kang→S12、QQ→S13）还是保留他留的空号
- D3：GA 保留 v46 版（Ka/Ks-inspired），不用他的（Cell-state Kinetic Index）
- D4：Discussion 是否按他给的具体文本加 Kang IFN-β 句
