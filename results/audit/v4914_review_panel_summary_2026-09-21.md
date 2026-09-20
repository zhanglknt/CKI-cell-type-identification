# 第五轮盲审汇总（v49.14）

日期：2026-09-21
审稿对象：CKI_Submission_v49_NC.zip（12,269,004 B，sha256 32018d04b4d2819cd1040ade416030f4c0f2028ac1b8df6fb50382a440f6b832，27 条目；commit 8c308b3 + 1b26168）

## 评分表

| 审稿人 | 视角 | 第四轮 | 第五轮 | Δ | Major | Minor | 推荐 |
|--------|------|--------|--------|---|-------|-------|------|
| R1 | 方法学 | 8.2 | 8.6 | +0.4 | 0 | 2 | Minor Revision |
| R2 | MK/群体遗传 | 8.5 | 8.8 | +0.3 | 0 | 1 | Minor Revision（修复后支持接收） |
| R3 | 统计 | 8.9 | 9.1 | +0.2 | 0 | 0 | **Accept** |
| R4 | 复现性 | 8.5 | 9.0 | +0.5 | 0 | 0 | **Accept** |
| R5 | 神经生物 | 8.3 | 8.8 | +0.5 | 0 | 0（1 可选） | Minor Revision（实质已达接收） |
| R6 | 编辑规范 | 8.8 | 9.0 | +0.2 | 0 | 2（1 可选不扣分） | **Accept** |
| **均分** | | **8.53** | **8.88** | **+0.35** | **0** | **5** | 3/6 直接收 |

轨迹：4.42 → 5.83 → 7.73 → 8.53 → **8.88**（连续四轮上升，零 Major）

## 数值核验统计

- 六审稿人合计数值抽查 40+ 项全部与 ground truth 一致，**零误报**（上轮 R6 的 ref.15/39 孤儿引用指控经 docx XML run 级解析正式撤销——txt 提取丢上标标记所致）
- C3 聚合顺序量化被 R1/R3/R5 三人独立重算确认（ρ=0.7786、中位 fold 0.955、max 9.752、控制类基线 6.456→10.939）
- C2 ex-CC Cox：304−272=32 恰为 ILSBio CC 数（R3 核对）；C4 CI 与 R3 上轮独立 bootstrap 一致

## 问题清单（去重后 5 项 Minor + 4 条不计分建议）

### Minor（一句话级修改）

| # | 来源 | 问题 | 修法 |
|---|------|------|------|
| m1 | R2 | Fig 1a legend 词序笔误："the counterpart of the constrained synonymous baseline" 把 constrained 安到了 synonymous baseline 上，与同段 "Ks as a neutral baseline" 矛盾 | 一词移位："the constrained counterpart of the synonymous baseline" |
| m2 | R1 | span-matched 3.68-fold 残差分解（k_f 1.39/k_n 0.33，SI 已有）宜在 MS 一句话注明残差仍主要为分母效应 | MS 补一句话 |
| m3 | R1 | ependymal donor-stratified 反向（0.058→0.021，q=0.052 未过校正，SI 已披露）宜在 MS 一句话点明 | MS 补一句话 |
| m4 | R6 | MS Results 一处 "Mann-Whitney U, P < 0.001"（cross-organ reversal）未随本轮 P 值精度升级 | copy-edit 改精确 P |
| m5 | R6（可选不扣分） | CL "1,750 replicates" 系每背景计数，可加 "per background" | 两词补充 |

### 不计分建议

- R5：MS "6.46→10.94" 可补 "(median)"（Guide 5.11h 已注明）
- R4（3 条化妆级）：cox_excc CSV 模型名双后缀 "_full_full"；M5 median k_n ratio 出处标注维持可选；SI 3.13 MC 分辨率声明值得肯定（正面项）

## 结论

v49.14 通过第五轮盲审：均分 8.88（+0.35），6/6 零 Major，3/6 直接 Accept（R3 9.1 / R4 9.0 / R6 9.0）。剩余 5 项 Minor 均为一句话级（1 处词序笔误 + 3 处 MS 透明性补句 + 1 处 copy-edit），无计算、无重跑、无结构性改动。修完即可锁定投稿版。

报告：results/audit/v4914_review_R1–R6_2026-09-21.md
