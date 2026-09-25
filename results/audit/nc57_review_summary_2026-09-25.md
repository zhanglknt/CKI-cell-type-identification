# nc57 终审轮汇总（v0.5.3 @ 3d220ac）

日期：2026-09-25 ｜ 对象：v0.5.3（nc55 修复 + nc56 proof 30 编辑后，发布链已闭环）
六审全部收齐，报告各自落盘 results/audit/nc57_r{1_stats,2_sccomp,3_cancer,4_brain,5_editor,6_repro}.md。

## 一、评分表

| 审稿人 | 领域 | 评分 | verdict | Major | 新 Minor |
|---|---|---|---|---|---|
| R1-stats | 统计 | 8.0 | accept | 0 | 2 |
| R2-sccomp | 单细胞计算 | 8.5（↑自 8.0） | accept | 0 | 3 |
| R3-cancer | 肿瘤基因组 | 8.5 | accept | 0 | 1 |
| R4-brain | 脑图谱 | 7.5 | accept | 0 | 1 |
| R5-editor | 编辑/写作 | 9.0 | accept | 0 | 2（+2 观察项） |
| R6-repro | 可复现性 | 8.5 | accept | 0 | 3 |
| **均分** | | **8.33**（nc55 7.92 → +0.41） | **6/6 accept** | **0** | 去重后 9 |

nc55 六审 3 accept + 3 minor revision → nc57 **6/6 accept、0 Major**。上轮各家问题核销率：R1 2R/1P/4U（U 均上轮即标注可选）、R2 7R/2P、R3 4/4R、R4 3R+1 沿留、R5 5R/1 裁定维持、R6 2 Major 全 R + 5R/1 撤回（5.7h 系 R6 自纠误报）。

## 二、新发现问题（去重 9 条 + 2 观察 + 2 条件项，全部经 team-lead ground-truth 复核）

| # | 发现 | 来源 | 复核结论 | 处置建议 |
|---|---|---|---|---|
| F1 | MS §28 括号失衡："…six organs (largest-donor pseudobulks; Methods), using…"（7 开 6 闭，应为 "Methods)),"） | R1（nc56 M3 引入） | **属实**（行级括号计数 7/6） | 修（0 词） |
| F2 | MS §38 "small-stratum raw JS 28.6% to 72.5%" 限定错位（72.5% 系大层端点） | R1+R4 独立命中（nc56 引入） | **属实** | 改 "raw JS 28.6% to 72.5% across strata"（+1 词） |
| F3 | MS L37 + Fig 3(c) "37.6–45.2% for the others" 漏 k_n 35.7%（SI 3.12 自列五度量），应为 "35.7–45.2%" | R2（潜在旧值，X5 复制进图注放大） | **属实**（SI L132 原文核对） | 两处一并改（0 词） |
| F4 | SI Note 8 新句 "ratio ≈ 1.8–2.3×" 未覆盖肾 1.57（源 CSV 复算：肺 1.82/肝 2.29/乳腺 2.24/肾 1.57） | R3 | **属实** | 改 "1.8–2.3× in lung, liver, and breast (kidney 1.6×)" 或放宽 "1.6–2.3×"（SI 免词额） |
| F5 | MS L14 "no candidate survives FDR correction" 未加 global（L63 已加、L65 族内 q=0.042 并存） | R2（m4 残留） | **属实** | 加 "global"（+1 词） |
| F6 | SI L222 "the validation value lies" 未随 Fig 14 同步为 "sanity-check value" | R5（X7 漏同步点） | **属实** | SI 改（0 词） |
| F7 | MS L48 "label-permutation confirmed; Section 3.13)." 裸节号（同行已有全式指针） | R5 | **属实** | 删 "; Section 3.13"（−2 词，对冲 F2+F5） |
| F8 | Fig 2(b) "far smaller variation" 与 L25 "k_n rose only 72–118-fold"（仅小 3.4–5.6×）程度词张力 | R2 | 文本属实，措辞判断 | 可选：删 "far"（图注免词额） |
| F9 | tests/test_reference_values.py:93-100 test_tcga_nn_tt_medians 仍断言退役 median 口径 1.233–2.319（读 legacy phase34_v2_summary.csv；归档上按设计 skip） | R6 | **属实**（读文件核对） | 迁移至 excc mean 口径（LUAD 2.464/KIRC 1.880/LUSC 1.708/BRCA 1.567/LIHC 1.112），与 spot_check Section 1 对齐 |
| O1 | L37 "four-tier" 冒号后只枚举 T1–T3（第四层 per-pair null 仅在 Methods L108） | R5 观察 | 属实（nc56 设计如此） | 可选，沿留 |
| O2 | 摘要 "neutral housekeeping drift (housekeeping-anchored…" 近距离两现 | R5 观察 | 属实（摘要 housekeeping ×4；第二处系 nc56 应 R2-m1 加的限定词） | 可选："neutral drift"（−1 词） |
| C1 | version DOI 10.5281/zenodo.22954782 doi.org 仍 404（DataCite 激活滞后，22949350 同型次日自愈） | R6-N1 | **17:20 复核仍 404** | 投稿前复核，无当前动作 |
| C2 | concept DOI 20405458 重定向传播 | R6-N2 | **17:20 复核已落点 22954782 → 自愈 CLOSED** | 关闭 |

## 三、词额总账（若全修）

MAIN 现 4,999/5,000（余量 1）：F2 +1、F5 +1、F7 −2 → 净 0，仍 4,999/5,000。F1/F3 净 0；F4/F6 SI 免额；F8 图注免额；O2 若做 −1（摘要 196→195）。

## 四、终审结论

v0.5.3 达投稿状态（6/6 accept、0 Major）。9 条 Minor 全部一词/一句级，其中 F1–F3 系 nc56 proof 轮引入或放大的自身瑕疵，建议投稿前一轮修掉（F1/F3/F4/F6/F7 为客观错误，F2/F5 为口径一致，F8/F9 顺手）。修复触及稿面 → main 将越过 tag v0.5.3，是否切 **v0.5.4 发布链** 留用户定夺。
