# 专家2：统计学与数据分析审稿报告 — CKI v22

**Reviewer**: E2 — 统计学与数据分析专家
**Date**: 2026-08-01
**Manuscript**: CKI: Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling at Single-cell Resolution
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v22.zip (22 files, 2.5 MB)
**Review baseline**: v20 expert score: 6.0/10

---

## 1. Overall Assessment

**v22 Score: 6.0/10** (无变化)

v22 修复了 v20 的 C2（k_n floor 参数表补全）——这是 E1 标记的算法实现问题。从统计角度看，此修复是中性的：k_n floor = 1e-4 的**行为**在 v20 中已经存在（存在于 `cki/core.py:242`），v22 只是将其**文档化**。因此统计分析结论不受影响。

我在 v20 中标记的 2 个 Critical（C1 BH-FDR 疑误）和所有 3 个 Major Issues 在 v22 中均未变化。

### 评分不变的理由

C2 修复属于"文档透明度"提升，不涉及任何统计方法变更。等待 C1（BH-FDR）验证后统一定量调整。

---

## 2. C2 k_n floor 的统计视角

### 2.1 参数的正确定位

k_n floor = 1e-4 在统计上是一个**截断下限（truncation threshold）**，而非正则化参数。其统计效果如下：

- **触发频率未知**：v22 文档仍未报告 k_n < 1e-4 的频率。若触发频率很高（如 TCGA 某些癌种的稀疏细胞类型），omega 的上界受此 floor 直接控制
- **对 omega 分布的影响**：当 k_n < 1e-4 时，omega = k_f / 1e-4，此时 omega 与 k_f 成正比（k_n floor 成为常数分母）。这意味着 floor-hit 的 omega 值本质上退化为 k_f ranking
- **TCGA 高 omega 值的潜在驱动**：BRCA Luminal A omega=344.5 可能是由接近 floor 的 k_n 驱动。这在 v20 中已标记，v22 仍未量化

### 2.2 建议

在复现指南中补充 k_n floor 的触发统计（至少报告 4 个数据集中 floor-hit 的对数和比例）。

---

## 3. v20 遗留 Critical Issues（统计学相关）

### C1（E1 + E2 独立发现 · **未修复**）：残差模型 BH-FDR q值疑误

这是 v20 审稿中统计层面的最高优先级问题。在 v22 中未变化。

**快速复述**：
- 稿件报告 16/30 Strong 信号 P=9.99e-5，q=2.75e-4
- 标准 BH: q(16) = 9.99e-5 × 31,764 / 16 = 0.198
- 报告 q 值与标准计算差 ~700 倍

**v22 状态**：未修复。v22 稿件和补充材料中的描述未变。

**统计后果**：
- 若 m=31,764：无任何信号在 BH α=0.05 下显著 → 脑分析"16个显著信号"声明无效
- 若 m 为子集：稿件声称的 "across all 31,764 pairs" 具有误导性

---

## 4. v20 遗留 Major Issues（统计学相关）

| v20 Issue | 描述 | v22 状态 |
|-----------|------|----------|
| M1 | 校准 n=6 严重不足（omega CV~60%）| 未修复 |
| M2 | 校准因子跨方案适用性未验证 | 未修复 |
| M5 | "Cohen's d" 术语不当（实际为置换 z-score）| 未修复 |
| M6 | 跨数据集 omega 不可比 | 未修复 |
| M9 | 置换检验中 mu_ct/mu_pair 是否重新计算不明确 | 未修复 |

---

## 5. Bootstrap 验证（统计健全性，从 v21 继承）

与 v21 一致的 bootstrap 状态：
- Mouse: 8/15 显著，B=1000，单侧 + BH FDR ✓
- Human: 15/16 显著，B=1000 ✓
- TCGA: descriptive only，B=1000 ✓
- Brain: 10/10 显著，B=1000，单侧 + BH FDR ✓

Bootstrap 实现本身无变化，统计方法一致。

---

## 6. Recommendations

### 阻塞项 (统计层面)
1. **C1 — BH-FDR 验证**：作为统计学专家，这是我的第一优先级。需要验证：(a) 实际代码中 m 的确切值；(b) 若 m < 31,764，子集选择的标准；(c) 提供完整 BH 计算代码和中间值

### 强烈建议
2. **k_n floor 触发统计**：报告 floor-hit 频率，评估 TCGA 高 omega 值的 floor 驱动程度
3. **M1 — 校准 n=6 扩充**：至少增加到 n≥30 或使用所有数据集的全部 pair 作为校准池

---

## 7. Summary

v22 在统计层面是中性的增量。C2 修复正确但统计含义有限。我要求修复的 C1 仍未解决——这是 v22 向 NAR 投稿的统计学阻塞项。修复 C1 后统计评分可从 6.0 提升至 7.0+。

**v22 评分: 6.0/10** | v20: 6.0/10 | 无变化（C2 为非统计修复）
