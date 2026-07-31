# 统计严谨性审稿：CKI v11 稿件

**审稿人**: stats-reviewer
**日期**: 2026-07-26
**稿件**: v11_manuscript_fulltext.txt
**评分**: **7/10**

---

## 1. 评分总结

v11 相比 v10 有显著改进，6 个 Critical 错误中 3 个已正确修复，但 k_n 相关错误（#1、#2）未正确修复——v11 将脑区数据的错误值替换为小鼠对照数据的值，而非正确的人类数据值。此外发现 Strong 候选标准的"pair median ω > 20"条件实际未被应用。大部分核心统计数值（人类 ω 分布、脑区细胞类型 ω、Strong/Moderate/Weak 计数、小鼠校准）验证正确。

---

## 2. v10 错误修复验证表

| # | v10 错误 | v11 值 | 正确值 | 数据来源 | 是否修复 |
|---|---------|--------|--------|---------|---------|
| 1 | k_n median 0.0086（应为0.034） | P20: 0.0019; P46: 0.0019 | 0.034（人类数据） | phase33_v3_human_pairs.csv | ❌ **未正确修复** |
| 2 | k_n range 0.0004-0.106（应为0.0018-0.221） | P20: 0.0006-0.0027; P46: 0.0006-0.0027 | 0.0018-0.221（人类数据） | phase33_v3_human_pairs.csv | ❌ **未正确修复** |
| 3 | 48对 k_n<0.001（应为0对） | 未明确陈述 | 0对（人类数据）；48对（脑区数据） | phase33_v3_human_pairs.csv | ⚠️ 部分修复 |
| 4 | ω<15比例 93.6%（应为56.3%） | P20: 56.3% | 56.3%（人类数据） | phase33_v3_human_pairs.csv | ✅ 已修复 |
| 5 | mouse mean ω=7.07（应为5.27） | 未提及7.07；P51提及median 3.63 | 5.27（mean）; 3.63（median） | mouse_pilot_v2_results.csv | ✅ 已修复 |
| 6 | P19说0.93% vs P45说0.15% | P74: 30 (0.09%) | 30/31,764 = 0.09% | brain_siletti_omega_pairs_v3.csv | ✅ 已修复 |

### 关键说明

**错误 #1 和 #2 详细分析**:
- v10 使用了脑区数据的 k_n 值（median=0.0086, range=0.0004-0.106）——这是错误的上下文
- v11 将值改为小鼠对照数据的 k_n 值（median=0.0019, range=0.0006-0.0027）
- 正确值应来自人类数据（median=0.034, range=0.0018-0.221），因为 P20 的上下文讨论的是人类数据（提及"56.3% of all ω values were < 15"）
- P46（小鼠校准上下文）中的值 0.0019 和 0.0006-0.0027 是**正确的**，因为该段确实讨论小鼠对照实验
- **问题核心**: P20（Methods, 通用上下文）使用了小鼠对照数据（n=6）的 k_n 值来代表"our datasets"，而主要分析使用的是人类数据（n=5,151）

**错误 #3 详细分析**:
- v11 P20 未明确陈述 k_n<0.001 的对数，但推荐了"k_n ≥ 0.001"阈值
- 人类数据中 0 对 k_n<0.001（min=0.0018），该阈值对人类数据无实际意义
- 脑区数据中仍有 48 对 k_n<0.001，小鼠对照中有 2 对 k_n<0.001
- P20 将小鼠对照的 k_n 分布与人类的 ω<15 比例混合在同一段落中，造成上下文混乱

---

## 3. Critical 问题

### C1. P20 k_n 值使用错误数据集（v10 错误 #1、#2 未正确修复）

**位置**: P20 (Methods - CKI computation)
**原文**: "In our datasets, k_n had a median of 0.0019 (range 0.0006-0.0027)."
**问题**: 该值来自小鼠对照实验（n=6, mouse_pilot_v2_results.csv 中 category=C_control 的 kn 列），但 P20 的上下文是通用方法描述，且同段提及"56.3% of all ω values were < 15"（人类数据）。
**数据验证**:
| 数据集 | k_n median | k_n range | k_n<0.001 对数 |
|--------|-----------|-----------|---------------|
| 人类 (n=5,151) | 0.0341 | 0.0018-0.2214 | 0 |
| 脑区 (n=31,764) | 0.0086 | 0.0004-0.1062 | 48 |
| 小鼠对照 (n=6) | 0.0019 | 0.0006-0.0027 | 2 |
**建议**: P20 应使用人类数据的 k_n 值（median=0.034, range=0.0018-0.221），因为该段讨论的是主要分析数据集。小鼠对照的 k_n 值仅在 P46（校准部分）使用是正确的。

### C2. Strong 候选标准的"pair median ω > 20"条件实际未被应用

**位置**: P31, P73 (Methods - multiplicative residual model)
**原文**: "Strong (residual < 0.3, ω < 15, lowest ω in the region pair, and pair median ω > 20)"
**问题**: 稿件声称 Strong 候选需要满足 4 个条件，但实际计算中仅使用了前 2 个条件（residual < 0.3, ω < 15）。
**数据验证**:
- 仅用 residual<0.3 AND ω<15: 得到 30 个 Strong 候选 ✓（与稿件一致）
- 加入 pair median ω > 20 条件: 得到 **0 个** Strong 候选
- 30 个 Strong 候选的 pair median ω 分布: mean=9.13, max=16.43, **全部 ≤ 20**
**影响**: 稿件描述的方法学标准与实际实施不符。如果严格执行所有 4 个条件，将没有 Strong 候选，整个脑区迁移分析的结论将不成立。
**建议**: 要么修正方法学描述（移除"pair median ω > 20"条件），要么重新运行分析应用全部条件。

---

## 4. Major 问题

### M1. P31 残差百分位数与实际不符

**位置**: P31 (Methods - multiplicative residual model)
**原文**: "the 1st percentile corresponded to residual ≈ 0.29"
**实际值**: 1st percentile = 0.4025
**问题**: 稿件声称 Strong 阈值 0.3 对应第 1 百分位，但实际第 1 百分位为 0.40，0.3 远低于第 1 百分位。这意味着 0.3 阈值比稿件描述的更为极端。
**同样**: 5th percentile = 0.522（稿件暗示 Moderate 阈值 0.5 对应第 5 百分位，实际 0.5 低于第 5 百分位）; 25th percentile = 0.753（Weak 阈值 0.75 约等于第 25 百分位 ✓）

### M2. P20 混合不同数据集的统计量

**位置**: P20 (Methods - CKI computation)
**问题**: 同一段落中:
- k_n 值（median=0.0019, range=0.0006-0.0027）来自小鼠对照数据（n=6）
- "56.3% of all ω values were < 15"来自人类数据（n=5,151）
- "k_n ≥ 0.001"阈值建议对人类数据无意义（人类 k_n min=0.0018）
**建议**: 明确每个统计量的数据来源，避免跨数据集混合。

---

## 5. Minor 问题

### m1. P51 同细胞类型跨器官 mean ω 值偏差

**原文**: "same cell type across organs (mean ω = 8.70, n = 60 pairs)"
**实际值**: mean ω = 8.651, n = 60
**偏差**: 0.05（8.651 四舍五入应为 8.65，非 8.70）

### m2. P51/P53 不同细胞类型同器官 mean ω 值偏差

**原文 P51**: "different cell types within the same organ (mean ω = 16.18, n = 1,140 pairs)"
**原文 P53**: "same-organ pairs had higher values than different-organ pairs (mean ω 16.18 vs. 13.77)"
**实际值**: same-organ mean ω = 16.001, n = 1,140; diff-organ mean ω = 13.583, n = 4,011
**偏差**: same-organ 偏差 0.18; diff-organ 偏差 0.19

### m3. P67 脑区核数总和与总数不一致

**原文**: "888,263 nuclei" + 各细胞类型核数列表
**实际**: 列出的 9 类细胞核数总和 = 886,187
**差异**: 2,076 核未归类
**建议**: 说明差异来源（如未分类核或 QC 过滤）。

### m4. P26 vs P33 TCGA 样本数不一致

**P26**: "LUAD mutations: from cBioPortal, 497 samples (61 EGFR, 121 KRAS, 312 WT)"
- 61+121+312 = 494 ≠ 497
**P33/P58**: "n = 492 samples" (61 EGFR, 120 KRAS, 311 WT)
- 61+120+311 = 492
**问题**: P26 的总数和分组数与 P33/P58 不一致
**建议**: 统一样本数报告。

### m5. P26 vs P33 LIHC Edmondson 样本数不一致

**P26**: "289 tumors"
**P33**: "n = 288 tumors with both grade and expression data"
**问题**: 1 个肿瘤差异未说明
**建议**: 明确说明表达数据缺失导致 1 例排除。

### m6. P68 脑区梯度遗漏 Choroid plexus

**数据**: Choroid plexus: mean ω = 4.80 ± 1.45, n = 15
**稿件**: P68 讨论 9 类细胞类型的 ω 梯度，但遗漏了 Choroid plexus（第 10 类）
**建议**: 补充 Choroid plexus 的 ω 值或说明排除原因。

---

## 6. 数据一致性检查表

### 人类数据 (phase33_v3_human_pairs.csv)

| 统计量 | 稿件值 | 实际值 | 一致? |
|--------|--------|--------|-------|
| n | 5,151 | 5,151 | ✅ |
| ω median | 13.68 | 13.675 | ✅ |
| ω mean | 14.12 | 14.118 | ✅ |
| ω min | 1.10 | 1.098 | ✅ |
| ω max | 58.69 | 58.688 | ✅ |
| ω < 15 比例 | 56.3% | 56.3% | ✅ |
| k_n median (P20) | 0.0019 | 0.0341 | ❌ |
| k_n range (P20) | 0.0006-0.0027 | 0.0018-0.2214 | ❌ |
| k_n < 0.001 对数 | 未陈述 | 0 | ⚠️ |
| same-ct cross-organ mean ω | 8.70 | 8.651 | ❌ (偏差0.05) |
| same-ct cross-organ n | 60 | 60 | ✅ |
| diff-ct same-organ mean ω | 16.18 | 16.001 | ❌ (偏差0.18) |
| diff-ct same-organ n | 1,140 | 1,140 | ✅ |
| diff-organ mean ω | 13.77 | 13.583 | ❌ (偏差0.19) |
| k_f median | 未明确陈述 | 0.498 | — |

### 脑区数据 (brain_siletti_omega_pairs_v3.csv)

| 统计量 | 稿件值 | 实际值 | 一致? |
|--------|--------|--------|-------|
| n | 31,764 | 31,764 | ✅ |
| global mean ω | 8.01 | 8.007 | ✅ |
| Astrocyte mean ω | 14.36 ± 8.68 | 14.363 ± 8.680 | ✅ |
| Astrocyte n | 5,778 | 5,778 | ✅ |
| Bergmann glia mean ω | 2.37 ± 1.14 | 2.372 ± 1.142 | ✅ |
| Bergmann glia n | 21 | 21 | ✅ |
| Committed OPC mean ω | 3.17 ± 1.47 | 3.167 ± 1.472 | ✅ |
| Committed OPC n | 1,326 | 1,326 | ✅ |
| Fibroblast mean ω | 3.99 ± 1.90 | 3.986 ± 1.902 | ✅ |
| Fibroblast n | 3,403 | 3,403 | ✅ |
| Vascular mean ω | 3.40 ± 1.24 | 3.405 ± 1.245 | ✅ |
| Vascular n | 3,321 | 3,321 | ✅ |
| Ependymal mean ω | 4.13 ± 1.73 | 4.133 ± 1.729 | ✅ |
| Ependymal n | 780 | 780 | ✅ |
| Microglia mean ω | 8.02 ± 4.93 | 8.024 ± 4.932 | ✅ |
| Microglia n | 5,671 | 5,671 | ✅ |
| Oligodendrocyte mean ω | 8.66 ± 4.44 | 8.660 ± 4.445 | ✅ |
| Oligodendrocyte n | 5,778 | 5,778 | ✅ |
| OPC mean ω | 7.65 ± 4.03 | 7.649 ± 4.034 | ✅ |
| OPC n | 5,671 | 5,671 | ✅ |
| Strong candidates | 30 (0.09%) | 30 (0.09%) | ✅ |
| Moderate candidates | 1,247 (3.93%) | 1,247 (3.93%) | ✅ |
| Weak candidates | 6,567 (20.67%) | 6,567 (20.67%) | ✅ |
| Strong by cell type | Microglia 10, Oligo 10, Astro 6, Vascular 3, Fibroblast 1 | 完全一致 | ✅ |
| OPC ω<15 | 93.6% (5,310/5,671) | 93.6% (5,310/5,671) | ✅ |
| OPC Strong signals | 0 | 0 | ✅ |
| residual 1st percentile | ≈0.29 | 0.4025 | ❌ |
| 6.06-fold gradient | 14.36/2.37 | 6.059 | ✅ |
| Choroid plexus | 未讨论 | 4.80 ± 1.45, n=15 | ⚠️ 遗漏 |

### 小鼠数据 (mouse_pilot_v2_results.csv)

| 统计量 | 稿件值 | 实际值 | 一致? |
|--------|--------|--------|-------|
| n | 15 | 15 | ✅ |
| Control mean ω | 1.54 | 1.537 | ✅ |
| Control median ω | 1.42 | 1.423 | ✅ |
| Control range ω | 1.09-2.10 | 1.087-2.098 | ✅ |
| Control all P > 0.05 | Yes | Yes (min P = 0.0998) | ✅ |
| Control k_n median (P46) | 0.0019 | 0.0019 | ✅ |
| Control k_n range (P46) | 0.0006-0.0027 | 0.0006-0.0027 | ✅ |
| S category mean ω | 4.03, n=4 | 4.026, n=4 | ✅ |
| D category mean ω | 13.18, n=3 | 13.179, n=3 | ✅ |
| Mouse median ω | 3.63 | 3.631 | ✅ |
| Mouse mean ω (v10: 7.07) | 未陈述 | 5.266 | ✅ (已移除错误值) |

### 小鼠全矩阵 (full_matrix_pairs.csv)

| 统计量 | 稿件值 | 实际值 | 一致? |
|--------|--------|--------|-------|
| n | 703 | 703 | ✅ |
| median ω | 6.9 | 6.907 | ✅ |
| AUC (identity-only) | 0.847 | 无法验证 | — |

### 无法验证的统计量

| 统计量 | 稿件值 | 验证状态 |
|--------|--------|---------|
| Spearman ρ = -0.57 to -0.38 | P52 | 无法验证（需 5 指标相关矩阵） |
| AUC = 0.716 (CKI) | P53 | 无法验证（需分类结果） |
| AUC = 0.887 (cosine) | P53 | 无法验证 |
| AUC = 0.752 (cosine, 200 DE genes) | P53 | 无法验证 |
| AUC = 0.847 (mouse full matrix) | P44 | 无法验证 |
| TCGA NN/TT ratios | P56 | 无法验证（无 TCGA 数据文件） |
| TCGA clinical ω values | P58 | 无法验证 |
| HK sensitivity CV < 13% for 99.2% | P19 | 无法验证 |
| HVG sensitivity r > 0.97 | P19 | 无法验证 |
| k_n stability 0.0147-0.0166 | P41 | 无法验证（需 HK 敏感性分析数据） |
| Bootstrap CI [1.12, 2.08] | P47 | 无法验证 |

---

## 7. 总结

### 已验证正确的核心统计量（36项）
人类 ω 分布、脑区所有细胞类型 ω 值、Strong/Moderate/Weak 计数、小鼠校准值、全矩阵中位数等核心统计量均验证正确。

### 需要修正的问题
- **2 个 Critical**: P20 k_n 值错误上下文；Strong 标准描述与实施不符
- **2 个 Major**: 残差百分位数不符；P20 数据集混合
- **6 个 Minor**: 小数值偏差、样本数不一致、遗漏

### 建议优先修复顺序
1. **C1**: P20 k_n 值改为人类数据（median=0.034, range=0.0018-0.221）
2. **C2**: 修正 Strong 标准描述或重新分析
3. **M1/M2**: 修正残差百分位数描述和 P20 数据来源标注
4. **m1-m6**: 统一小数值和样本数
