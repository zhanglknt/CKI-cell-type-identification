# v46 终审签署 — 单细胞基因组学视角（r-singlecell）

- 核查对象：version3/CKI_Submission_v46/（build 621/621，Release v0.4.9，Zenodo 10.5281/zenodo.22333850）
- 核查范围：v45 交叉验证报告（results/audit/gb_v45_crosscheck_singlecell_2026-09-05.md）中我提出的 2 项新 P2 残留
- 日期：2026-09-05；只读核查

## 核销结果

| 条目 | v45 残留问题 | 判定 | 证据 |
|---|---|---|---|
| N-1 | Figure 6B 图内标题未标注 equal-n 上界属性 | **CLOSED** | figure6.pdf（v46）B 面板图内标题现为 "6.10-fold omega gradient across 10 cell classes (uncorrected upper bound; equal-n estimate 1.74-fold, 95% CI [1.64, 1.84])"，与摘要/正文/图例的并列报告口径一致（已目视确认渲染图） |
| N-2 | 复现指南 Bergmann glia ω_cal "~1.3" 与正文 "≈ 1.4" 不一致 | **CLOSED** | CKI_Reproducibility_Guide_fulltext.txt 现为 "internal baseline of 9.73 (95% CI [9.03, 10.53]) … under which Bergmann glia corresponds to omega_cal ~ 1.4 (close to the internal baseline)"；13.56/9.73 = 1.394，两位有效数字 1.4，与正文一致 |

附带观察：v46 Figure 6D 面板同时更新了候选富集注释（"12/39 Strong are OL-lineage, fold enrichment 0.77, P = 0.92 (no enrichment)"、"null expects 148.3 Strong vs 39 observed, anti-enriched: P(null count ≥ 39) = 1.0"），与 v45 正文新增的 de-enrichment 表述一致，图面信息无回归。

## 最终评分

**7.8 / 10**（v44：6.5 → v45：7.5 → v46：7.8）

我提出的全部 P1/P2 及 v45 交叉验证残留的处置链：P1-1、P1-2、P1-4 CLOSED；P1-3、P2-1、P2-2 PARTIAL（均为"充分披露 + 补充分析"式缓解，主方案与未重算项属作者明示的设计取舍，不影响排名级结论）；v45 两项图文粒度残留 CLOSED。无未核销的结论级问题。

## 一句话签署意见

v46 消除了最后两处图文不一致，全文头条数字、图面标注、补充材料与复现指南在单细胞视角下已自洽，从本视角签署通过，无进一步 blocking 事项。
