# CKI v34 独立审稿 — E2: 定量生物学与统计

**审稿日期**: 2026-08-03
**评分**: 8.9/10 (v33: 8.7/10, Δ: +0.2)
**审稿文件**: CKI_NAR_Manuscript_fulltext.txt, CKI_NAR_Supplementary_fulltext.txt, CKI_NAR_Cover_Letter_fulltext.txt

---

## 1. 核心发现概要

v34 修复了 v33 的两项统计方法学层面的遗留问题（m8 Introduction 措辞 + m9 Limitation #20），同时确认了 v33 已完成的统计改进保持完好（CV 更正、FDR 术语统一、P-value 精度、SES+CI 互补）。无新增统计方法学问题。

**Critical: 0 | Major: 0 | Minor: 0**

---

## 2. 统计方法学逐项验证

### 2.1 核心统计声明一致性 ✅

| 统计声明 | v33 状态 | v34 状态 |
|----------|---------|---------|
| CV = 52% (ω calibration) | ✅ L52 | ✅ — 同 v33，未变 |
| 95% bootstrap CI [4.12, 9.33] | ✅ L11 | ✅ — 同 v33 |
| SES + bootstrap CI 互补 (v33 E2-2) | ✅ | ✅ — 同 v33 |
| FDR 术语统一 (v33 E2-1) | ✅ | ✅ — FDR separately per dataset |
| P-value 精度 9.99e-4 (v33 E2-5) | ✅ L41 | ✅ — 同 v33 |
| MCSE 声明 (v33 E2-3) | ✅ | ✅ — "MCSE ≈ 0.016 at P = 0.5" |

### 2.2 Abstract 统计措辞 ✅

**v34 L11**: "two with permutation support" — 与 Introduction L18 "both with permutation support" 完全一致。v33 Introduction 残留的 "both statistically significant" 已清除。全文中与 30 个 Strong candidate 相关的统计声明统一使用 "permutation support" / "permutation P-value floor (P = 9.99e-5)" / "descriptive evidence"。

Grep 验证：全文 0 处 "statistically significant"，0 处 "orthogonal"。

### 2.3 Limitations #20（v33 编号跳跃问题）✅

v34 L101 完整的 Limitations 序列：

```
Eighteenth — one-sided permutation test limitations
Nineteenth — P-value floor saturation (36.3%) + alternative null interpretation
Twentieth — k_n floor in TCGA (5 cancer types, inflates ω vs single-cell)
Twenty-first — non-neuronal scope limitation
```

编号连续无跳跃。Twentieth 内容为 k_n floor (1e-4) 在 TCGA 数据集中的影响——"ω values from datasets where k_n saturates at the floor are systematically inflated relative to datasets with higher k_n"。该说明准确反映了 TCGA 与单细胞数据集之间 ω 绝对值的不可比性，且注明了 rank-based 解释不受影响。

### 2.4 "orthogonal" 术语残留 ✅

v33 中 L77 "orthogonal transcriptomic readout" 和 L116 "orthogonal information" 两处残留已全部替换为 "complementary"。从统计角度看，"orthogonal" 表示 r ≈ 0（无相关性），而 CKI ω 与标准距离度量的 Spearman r = −0.38 to −0.57——存在中等负相关。使用 "complementary"（信息层面互补，不要求数学正交）比 "orthogonal" 更准确。

Grep 验证：全文 0 处 "orthogonal"。

### 2.5 Bootstrap / 置换检验配置验证

| 数据集 | B | 检验类型 | m | v34 一致？ |
|--------|---|---------|---|:--:|
| Mouse | 1,000 | 单侧，pair-level | 15 | ✅ |
| Human | 1,000 | 单侧，pair-level | 17 | ✅ |
| TCGA | 1,000 | 单侧，sample-level | 5 cancers | ✅ |
| Brain bootstrap | 1,000 | 单侧，pair-level | 10 cell types | ✅ |
| Brain residual | 10,000 | 单侧，per-signal | 31,764 | ✅ |

Bootstrap CIs 在所有数据集正确标注为 95% 百分位置信区间。

---

## 3. 统计可视化与补充图引用

v34 补充图 S1–S12 全部在正文中有引用点。特别关注统计相关图：

- **S8**: ω 分布直方图+Q-Q图 → L54 引用（Shapiro-Wilk + D'Agostino-Pearson 正态性检验）
- **S9**: 置换零分布 → L81 引用（P-value floor saturation）
- **S10**: JS divergence 维度无关性 → L24 引用（dimension ratio = 1.001）
- **S11**: Per-pair k_n 变异性 → L56 引用（CV = 97.35%, ρ = −0.027）

统计可视化与正文统计报告匹配完整。

---

## 4. 评分说明

**8.9/10**（+0.2 vs v33 8.7）：

- **+0.2**: Introduction "statistically significant" 修复（统计术语一致性）
- **+0.1**: "orthogonal"→"complementary"（统计准确性提升）
- **+0.1**: Limitation #20 补充 k_n floor 影响统计解释
- **−0.2**: 无新增统计方法学改进（如 synthetic benchmark、cross-dataset meta-FDR 等已在 Limitations 中标注为 future work）

v33 的主要统计改进（CV 更正、FDR 统一、P-value 精度、MCSE）在 v34 中完好保持。

---

## 5. 投稿建议

统计方法学层面无阻塞问题。建议投稿 NAR。

**审后建议**（revision 阶段）：
- Limitations #14 提到 "simulation benchmark with injected functional divergence"——如果 revision 期间能补充 synthetic data benchmark，将显著增强方法学的统计说服力
- Cross-dataset unified FDR framework（Limitations #13）属于 future work，不影响当前投稿
