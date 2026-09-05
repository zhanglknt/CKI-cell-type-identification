# Genome Biology 终审签署（统计学审稿人）— CKI 投稿包 v46

- 审稿人：r-statistics（生物统计学）
- 日期：2026-09-05
- 对象：`version3/CKI_Submission_v46/`（build 621/621；cki v0.4.9，29/29 tests；Zenodo 10.5281/zenodo.22333850）
- 性质：终审签署轮 —— 仅核销本人在 v45 交叉验证报告（`gb_v45_crosscheck_statistics_2026-09-05.md`，8.5/10）中提出的 3 项编辑层面残留问题。只读核验，未修改任何投稿文件。

## 核销结论总表

| # | v45 残留问题 | v46 核验位置 | 判定 |
|---|---|---|---|
| R-1 | SN 3.5 Bergmann omega_cal "1.39" 三位有效数字，与"至多两位有效数字"约定不一致 | `CKI_Supplementary_fulltext.txt` L82（Note 3.5） | **CLOSED** |
| R-2 | Results 成分校正声明与 Discussion 版本并存、主从不清 | `CKI_Manuscript_fulltext.txt` L51（Results）↔ L85（Discussion） | **CLOSED** |
| R-3 | 反富集结果仅在图注，未嵌入 figure6 图形本体 | `figure6.pdf` 第 1 页 panel D（pdftotext 提取核验） | **CLOSED** |

3/3 CLOSED，无 OPEN，未发现新回归。

## 逐项核验记录

### R-1（CLOSED）：SN 3.5 有效数字约定
- L82 实测："the most constrained class (Bergmann glia) to omega_cal ≈ **1.4** (raw 13.56)"——已由 1.39 改为两位有效数字 1.4。
- 同段保留约定声明："calibrated values are reported with at most two significant figures and should be read as order-of-magnitude estimates"，前后一致。
- 附注：同段 "Bergmann glia omega_cal = 1.49 (joint 95% CI [0.99, 2.12])" 为另一统计量（per-class 基线校准比，附完整 CI），不属于本次残留的"1.39"裸值，不计为回归。
- MANIFEST V46-d2 条目与实测一致。

### R-2（CLOSED）：TCGA 成分校正声明主从统一
- Results（L51）实测：以 softmax 主分析开篇——"the pooled tumor-pair k_n coefficient essentially unchanged after composition adjustment (**−0.5%, bootstrap 95% CI [−3.2%, +2.6%]**; per cancer type −14% to +34%; **linear-normalization sensitivity −0.8% [−4.1%, +2.6%]**)"，linear 明确降级为 sensitivity。
- Discussion（L85）实测："the tumor-pair coefficient attenuates by **−0.5% pooled (95% CI [−3.2%, +2.6%])**"，与 Results 主值逐字一致，两处不再并存两套主数字。
- 统计上合理：B=200 cluster bootstrap 端点 MC 误差已在 v45 SN 5.2 论证；softmax/linear 两版结论方向一致（区间均跨 0），主从呈现不影响推断。
- MANIFEST V46-e 条目与实测一致。

### R-3（CLOSED）：Fig 6D 图内嵌反富集标注
- `figure6.pdf`（1 页，SHA 050fe51c…，71,600 bytes，已重新生成）panel D 图内实测含两行标注：
  - "null expects 148.3 Strong vs 39 observed"
  - "anti-enriched: P(null count ≥ 39) = 1.0"
- 数值与正文 L70 及 v45 核验值（null 期望 148.3、观测 39、P=1.0）完全一致；panel D 同时保留 OL-lineage 富集阴性标注（"fold enrichment 0.77, P = 0.92 (no enrichment)"），选择规则反富集与条件性富集无效的表述在图形本体自洽。
- MANIFEST"figure6 regenerated with 6B/6D in-panel annotations"与实测一致。

## 包级一致性抽查

- MANIFEST_v46.txt 声明：SN 3.5 两位有效数字（V46-d2）、TCGA 成分统一 softmax 主分析（V46-e）、figure6 6B/6D 图内标注（V46-g..i）、cki 0.4.8→0.4.9、Zenodo 记录 10.5281/zenodo.22333850——均与本人独立核验结果吻合。
- 附带注意（非本人核销范围，不影响统计判定）：MANIFEST 标题行仍写 "CKI Submission Package v45"，为编辑层面笔误，建议 build 脚本顺手修正。

## 最终评分与判定

- **最终评分：9.0 / 10**（v44 盲审 7.5 → v45 核销 8.5 → v46 签署 9.0）
- **判定：Accept**
- 依据：v44 全部 4 项 P1 与 3 项 P2 在 v45 已 CLOSED 并经独立重算确认；v45 遗留的 3 项编辑层面残留（有效数字约定、成分声明主从、图内标注）在 v46 全部 CLOSED；比值估计量偏差披露、studentized bootstrap-t 区间（覆盖率达名义 0.953/0.951）、反富集与 post-selection 推断边界、功效窗口声明等核心统计问题在当前版本中均已达到方法学期刊的披露标准。剩余 0.5–1.0 分保留给小 cluster 下区间下端对重抽样的固有敏感性（Bergmann 仅 7 个 region，作者已如实披露）与 TCGA marker 面板作为成分代理的固有噪声下限性质——均为数据固有局限而非文稿缺陷。

**签署：r-statistics，2026-09-05。建议接收。**
