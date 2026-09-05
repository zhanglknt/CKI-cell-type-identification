# v45 交叉验证核销报告 — 单细胞基因组学视角（r-singlecell）

- 基准评审：results/audit/gb_v44_blind_review_singlecell_2026-09-05.md（6.5/10，Major Revision；P1 × 4，P2 × 2）
- 核查对象：version3/CKI_Submission_v45/（正文/补充/复现指南/图 PDF 全文通读关键段）+ 仓库 results/ 下 v45 分析报告（独立复算）
- 日期：2026-09-05
- 核查方式：逐项打开 v45 文件核对（不信摘要）；对可复算数字独立重算；只读，未修改任何投稿文件

## 核销总表

| 条目 | v44 问题 | 判定 | 关键证据 |
|---|---|---|---|
| P1-1 | Figure 1C 旧基线 6.67；SN 3.5 "1.5-fold" 数值错误 | **CLOSED** | figure1.pdf（v45）C 面板重绘："Split-half control ω (n = 300), Median = 7.69, Baseline = 7.70"，E 面板亦标 Baseline = 7.70；CKI_Supplementary Note 3.5 改为 "approximately 1.3-fold higher"（9.73/7.70 = 1.264，正确）；正文与复现指南均一致 |
| P1-2 | 6.10-fold 头条约 70% 为类样本量混杂；equal-n 应为主报告 | **CLOSED**（附 1 条微小残留） | 摘要内联并列："6.10-fold … an upper bound inflated by class-size imbalance (equal-n downsampling: 1.74 [1.64, 1.84])—predominantly k_n-driven (3.21 vs 2.03)"；正文 "co-report 6.10-fold as the full-data estimate and 1.74-fold as the size-balanced estimate throughout"；Bergmann glia 定量主张按 team-lead 所述设计降级为定性（studentized bootstrap-t [5.76, 28.59] 下限 < 类基线 9.08），正文、SN 3.5/3.21 表述一致 |
| P1-3 | 循环 per-pair top-200 选择仍作主方案 | **PARTIAL** | 概念定义、摘要、限制章均前置披露 "Per-pair gene selection inflates k_f (median 1.6-fold) but preserves rankings (ρ ≈ 0.92)"，绝对 ω 明确定位为上界、方案特异估计；但 S0 循环方案仍是全部绝对数字的唯一主方案，leave-pair-out 未升为并列主报。排名结论不受影响，故残留为定位/框架层面而非结论层面 |
| P1-4 | 缺少 Augur/Milo 等细胞类型优先级工具基准 | **CLOSED** | 新增 SN 3.23 + results/augur_comparison_v45_report.md：pyaugur 0.1.0（R Augur v1.0.3 纯 Python 移植，对 R 基准 ρ = 1.0，已诚实标注非官方 augurpy）；主分析用混杂受控的 binary OvR（多分类 AUC 与合格区域数相关 ρ = −0.744，P = 0.014，已识别并降级为敏感性）；vs ω ρ = +0.442、vs k_f +0.564、vs k_n −0.236。我按报告表独立重排秩复算：k_f ρ = 0.564 精确吻合；ω ρ ≈ 0.44–0.47（含并列修正）一致 |
| P2-1 | 伪 bulk 聚合顺序跨管线不一致 | **PARTIAL** | v45 Methods 明确区分 softmax(log1p(mean counts))（脑）与 softmax(mean(log1p))（小鼠/人）并阐明其对校准常数不可迁移的贡献——披露完整，但未做统一化重跑 |
| P2-2 | bulk 来源 HK 集与 snRNA 场景匹配；TCGA 定位 | **PARTIAL**（HK 集）/ **CLOSED**（TCGA，设计决定） | PMI/线粒体 caveat 大幅扩充（线粒体转录本 PMI 降解更快、可能伪装为 k_n 区域结构；donor 级 PMI 协变量不可得；声明候选级主张前需最小敏感性分析）；但未新增 snRNA/数据驱动约束集复算（仍为 v44 的 top-10% 低变异集 r > 0.95 敏感性）。TCGA 严重度按既定设计保留为正文一段式 "exploratory vignette, denominator-dominated"，Results 与 Discussion 表述一致（LIHC/BRCA 在 k_f-only 下反转、LUAD 部分例外均有对应说明） |

## 独立复算记录

- Augur OvR 表（results/augur_comparison_v45_report.md）：按 10 类名次重算 Spearman，Augur vs k_f = 0.564（与报告精确一致），Augur vs ω ≈ 0.44–0.47（报告 0.442，差异来自 Bergmann/vascular ω 并列处理），多分类 AUC vs 区域数 ρ = −0.744 的混杂判定与设计叙述自洽。
- 比率估计审计（results/ratio_estimator_biasvar_v45_report.md）：82.75/13.56 = 6.102 ✓；中位梯度 73.37/12.23 = 5.999 ≈ 6.00 ✓；截尾 78.68/12.91 = 6.094 ≈ 6.09 ✓；k_n 分箱 600+402+448 = 1,450 ✓； pooled E[ω] = 9.73 与脑内基线一致 ✓。
- 小簇 bootstrap（results/cluster_boot_v45_report.md）：Monte Carlo 覆盖率 percentile 0.876/0.873 vs studentized-t 0.953/0.951（MC SE ≈ 0.0067，差异显著）；Bergmann [5.76, 28.59] 下限 5.76 < 9.08，降级逻辑成立；choroid [25.93, 76.30] 下限远高于其基线 10.66，定量主张保留——两类处理不对称但各自自洽。
- 非 HK 漂移对照（results/nonhk_drift_v45_report.md）：N1（表达匹配低变异非 HK 集）ω FPR 0.067/0.011/0.000 vs raw JS 0.067/0.811/1.000、cosine 0.089/0.878/1.000——摘要 "≤ 0.067 … raw JS and cosine: 0.81–1.00" 取各档最大不利值，表述准确且偏保守；N0 内对照复现原始模拟（0.000/0.556/0.600 vs 原 0.000/0.553/0.580）✓；N2（基因身份置换）三指标 FPR 均 1.000，已如实披露并给出"身份置换是否算中性"的论证，未隐匿。

## 新引入问题（回归检查）

1. **[P2] Figure 6B 图内标题未更新**：仍为 "6.10-fold omega gradient across 10 cell classes"，未在图内标注 equal-n 上界属性（图例文字已修正为 "uncorrected upper bound … equal-n estimate 1.74-fold"）。与 P1-1 同类性质的图文粒度不一致，建议下轮在图内标题或面板脚注加 "(uncorrected upper bound; equal-n 1.74-fold)"。
2. **[P2] 复现指南舍入不一致**：指南称脑内基线下 Bergmann glia ω_cal "~1.3"，而正文为 "≈ 1.4"（13.56/9.73 = 1.394，两位有效数字应为 1.4）。指南自身 v45 已声明 ω_cal 报两位有效数字，此处应统一。
3. 未发现结论级回归：摘要新增的 anchor-blindness、功率窗口（~50–200 cells/donor/condition）、N1 对照、de-enrichment（148.3 expected vs 39 observed）均与 SN/结果文件一致。

## v45 总体评分

**7.5 / 10**（v44：6.5）

4 个 P1 中 3 个完全核销（P1-1、P1-2、P1-4），P1-3 以充分的前置披露 + 排名稳健性证据达成实质缓解但未改主方案；2 个 P2 均为"披露充分、未做重算"的 PARTIAL。v45 新增的四项分析（比率估计偏倚审计、小簇 studentized bootstrap-t、非 HK 漂移对照、Augur 对比）质量高且全部可由结果文件复算验证，Bergmann glia 降级与 TCGA exploratory 定位在全文中表述一致。剩余可为 Minor 级事项：Figure 6B 图内标题、指南 "~1.3" 舍入、leave-pair-out 并列主报与 snRNA 约束集复算（后两者为可选项）。

## 一句话总评

v45 对我全部 P1/P2 均给出可验证的实质性回应——三类核销、三类以高质量披露与新分析达成部分核销，无结论级回归，稿件已从"诚实但头条失焦"推进到"头条与证据强度匹配"，仅剩图级与可选分析级的收尾。
