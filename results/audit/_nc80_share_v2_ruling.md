# NC80 CNA Share v2 裁定（#1243）

日期：2026-11-16。脚本 `scripts/nc80_cna_share_v2.py`（seed 20261116，B=2000，全部 scope boot_ok=2000）。
产物：`results/nc80_cna_share_v2.csv`（Panel A）、`results/nc80_cna_joint_model.csv`（Panel B）、`results/nc80_cna_share_v2_report.txt`。

---

## Panel A：measured share，全表分母（替代 v1）

**改动**：Δ_obs 从 DNA 子集 gap 改为**全配对表 gap**（稿件反转口径）；IVW 比率合并改为分层 cluster bootstrap 的逐 draw 贡献比合并 ΣC_c/ΣG_c；per-cancer 全披露；δ 网格 0–0.10 步长 0.01。ex-CC 默认口径（Note 10 同源，25,015 对；CC-inclusive 变体另报，仅影响 LIHC）。

### Per-cancer share(δ=0)（全表 gap 分母）

| scope | gap_full | β_CNA^TT | m(cna) | DNA 覆盖 | share [CI] | v1 share |
|---|---|---|---|---|---|---|
| BRCA | 0.993 | 2.505 | 0.246 | 94% | **0.62 [0.46, 0.83]** | 0.62 |
| KIRC | 1.181 | 3.816 | 0.129 | **44%** | **0.42 [0.27, 0.59]** | 0.59 |
| LIHC | 0.521 | 1.934 | 0.240 | 65% | **0.89 [0.41, 1.93]** | 1.04 |
| LUAD | 1.077 | 2.519 | 0.204 | 74% | **0.48 [0.30, 0.68]** | 0.54 |
| LUSC | 0.849 | 2.025 | 0.237 | 66% | **0.57 [0.32, 0.95]** | 0.64 |

### Pooled（贡献比直接合并）

| δ | pooled share [CI] |
|---|---|
| 0 | **0.556 [0.458, 0.664]**（v1 IVW 0.599 [0.483, 0.715]） |
| 0.02 | 0.500 [0.412, 0.598] |
| 0.05 | **0.417 [0.343, 0.499]**（v1 IVW 0.438 [0.352, 0.524]） |
| 0.10 | 0.279 [0.226, 0.334] |

**稿件引用口径（方案 b headline）**：
- δ=0：「CNA accounts for **56% (95% CI 46–66%)** of the TT/NN k_n gap」
- δ=0.05：「or **42% (34–50%)** if normal tissue carries a residual distance of 0.05」
- δ 先验区间 [0, 0.04]（a1 ruling §5）对应 pooled ≈ 0.48–0.56 → 摘要可写「about half」为上限语言、正文报网格。
- KIRC 单列提示：DNA 覆盖仅 44%，份额对 δ 最脆弱（δ=0.10 时 0.09）。
- LIHC 份额 0.89 [0.41, 1.93]：如实写出「does not identify a stable share（CI 上限 >1）」。

## Panel B：joint confounder model（stat M2 修复）

模型 `log k_n ~ is_TT + cna(δ) + d_overall4 (+RIN)`，ex-CC，非 DNA TT 对按癌种均值插补（保持加法分解闭合），NN cna=δ。三份额之和恒等于 1（in-sample 恒等式，逐行验证）。

### δ=0（base variant，无 RIN）

| scope | share_cna [CI] | share_comp [CI] | share_resid | n_pairs |
|---|---|---|---|---|
| BRCA | 0.55 [0.40, 0.75] | **−0.09** [−0.20, −0.01] | 0.54 | 7,886 |
| KIRC | 0.32 [0.18, 0.50] | **+0.15** [+0.10, +0.21] | 0.53 | 5,321 |
| LIHC | 0.79 [0.32, 1.84] | **+0.38** [+0.22, +0.66] | −0.17 | 3,305 |
| LUAD | 0.41 [0.24, 0.62] | +0.04 [−0.03, +0.10] | 0.56 | 4,850 |
| LUSC | 0.39 [0.14, 0.73] | −0.02 [−0.25, +0.11] | 0.63 | 3,653 |
| **pooled** | **0.40 [0.30, 0.51]** | **+0.02 [−0.03, +0.06]** | **0.51** | 25,015 |

+RIN 变体（双端 RIN 可得的子集）：pooled share_cna 0.37 [0.28, 0.47]、share_comp ≈ −0.02、share_resid 0.64——**RIN 不吸收任何份额**，与 Note 23 结论一致。

### 解读要点

1. **组成份额符号异质是真实数据结构**：mean(|Δ4-panel|) 受 NN 重尾驱动，BRCA (−0.23) 与 LUSC (−0.035) 的均值为负（中位数仍 TT>NN）→ 组成协变量在这两癌种不仅不吸收 gap 反而放大残差。方向与 Note 10 的 attenuation 异质性（BRCA −16%/LIHC +44%）一致，互相印证。
2. **联合模型口径下 CNA ≈ 40%、组成 ≈ 2%、残差 ≈ 51%**——直接替换稿件中不相容的三元组「60% CNA / +44% composition / largely intact」。两个口径都要写：measured extrapolation（Panel A，56%）与 joint model（Panel B，40%），说明差异来源（联合模型斜率部分由 TT-vs-NN 对比识别，δ 假设影响更大）。
3. **LIHC 在联合模型下被完全解释**（share_resid −0.17，CNA 0.79 + comp 0.38 > 1）——「over-explained」，与其 gap 最小（1.58×）一致，写法与 a1 ruling §7 相同（不可稳定识别）。

## 方案 b 摘要建议句（供 #1244 改稿）

> In bulk TCGA tumours the same normalization *manufactures* a reversal: tumour–tumour pairs show *higher* housekeeping dispersion than normal–normal pairs in all five cancer types, and copy-number instability is a major driver — genomic distance alone accounts for about half of the gap (56% [46–66%], or 42% [34–50%] allowing residual normal-tissue distance), with composition and RNA quality adding little in a joint model.

（数字全部来自本 v2；「about half」对应 δ 先验区间上限 0.56。）
