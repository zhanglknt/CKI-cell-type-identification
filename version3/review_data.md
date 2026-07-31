# 数据完整性审稿报告

**审稿人**: data-reviewer  
**稿件版本**: v10_manuscript_fulltext.txt  
**审稿日期**: 2026-07-26  
**数据完整性评分**: 4/10

---

## 一、评分说明

稿件存在多处将brain数据统计值误用于human数据描述的严重错误，以及mouse mean ω值来源不明的问题。核心数值（k_n统计量、ω<15比例）与源数据不一致，影响了Methods和Results部分的关键结论可信度。

---

## 二、错误数值清单

### 严重错误（Critical）

| # | 位置 | 稿件原文 | 稿件值 | 数据来源文件 | 正确值 | 严重性 |
|---|------|---------|--------|-------------|--------|--------|
| 1 | P19 Methods | "k_n had a median of 0.0086 (range 0.0004–0.106); only 48 of 5,151 pairs (0.93%) had k_n < 0.001" | median=0.0086, range=0.0004–0.106, 48 pairs <0.001 | phase33_v3_human_pairs.csv | median=**0.0341**, range=**0.0018–0.2214**, 0 pairs <0.001 | **Critical** |
| 2 | P19 Methods | "93.6% of all ω values were < 15" | 93.6% | phase33_v3_human_pairs.csv | **56.32%** (2901/5151) | **Critical** |
| 3 | P45 Results | "median k_n = 0.0086, range 0.0004–0.106" | median=0.0086, range=0.0004–0.106 | phase33_v3_human_pairs.csv | median=**0.0341**, range=**0.0018–0.2214** | **Critical** |
| 4 | P45 Results | "99.6% of control pairs had k_n < 0.05" | 99.6% | mouse_pilot_v2_results.csv | **100%** (6/6 C_control pairs) | **Critical** |
| 5 | P45 Results | "Only 48 pairs (0.15% of 5,151) had k_n < 0.001" | 48 pairs, 0.15% | phase33_v3_human_pairs.csv | **0 pairs** (0%) for human; 48/31764=0.15% matches brain | **Critical** |
| 6 | P50 Results | "mouse (mean ω = 7.07)" | 7.07 | mouse_pilot_v2_results.csv / full_matrix_pairs.csv | pilot overall mean=**5.27**; full matrix mean=**7.62**; 7.07仅来自X_cross类别(仅2对) | **Critical** |

### 错误1-5详细分析：brain数据误用为human数据

稿件P19和P45中引用的k_n统计值（median=0.0086, range=0.0004–0.106, 48 pairs <0.001）完全匹配**brain数据**（brain_siletti_omega_pairs_v3.csv），而非human数据：

| 统计量 | 稿件值(P19/P45) | Human数据实际值 | Brain数据实际值 | 匹配 |
|--------|----------------|----------------|----------------|------|
| k_n median | 0.0086 | 0.0341 | 0.0086 | Brain ✓ |
| k_n min | 0.0004 | 0.0018 | 0.0004 | Brain ✓ |
| k_n max | 0.106 | 0.2214 | 0.1062 | Brain ✓ |
| k_n <0.001 count | 48 | 0 | 48 | Brain ✓ |
| k_n <0.001 % | 0.93%(P19) / 0.15%(P45) | 0% | 0.15% | Brain ✓(P45) |

用户批注已确认：*"Comment 0: 手算结果：k_n median = 0.034, range:0.0018-0.221"*

### 错误6详细分析：mouse mean ω来源不明

| 数据来源 | mean ω | n |
|---------|--------|---|
| mouse_pilot_v2_results.csv (全部) | 5.27 | 15 |
| mouse_pilot X_cross类别 | 7.07 | 2 |
| full_matrix_pairs.csv (全部) | 7.62 | 703 |

稿件引用的7.07仅来自mouse pilot的X_cross类别（仅2对），不能代表mouse整体mean ω。用户批注已确认：*"Comment 18: 手算：median = 3.63，mean=5.27"*

---

### 中等错误（Moderate）

| # | 位置 | 稿件原文 | 稿件值 | 数据来源文件 | 正确值 | 严重性 |
|---|------|---------|--------|-------------|--------|--------|
| 7 | P50 | "same cell type across organs (mean ω = 8.70, n = 60 pairs)" | 8.70 | phase33_v3_human_pairs.csv | **8.65** (n=60) | Moderate |
| 8 | P50 | "different cell types within the same organ (mean ω = 16.18, n = 1,140 pairs)" | 16.18 | phase33_v3_human_pairs.csv | **16.00** (n=1140) | Moderate |
| 9 | P52 | "same-organ pairs had higher values than different-organ pairs (mean ω 16.18 vs. 13.77)" | 16.18 vs 13.77 | phase33_v3_human_pairs.csv | **16.00 vs 13.58** | Moderate |
| 10 | P60 | "Neutrophils (mean ω = 2.72 ± 1.15, n = 6 pairs)" | SD=1.15 | phase35_cross_organ_conservation.csv | SD=**1.22** (mean=2.72 ✓) | Moderate |
| 11 | P61 | "median ω of 6.9" | 6.9 | phase35_cross_organ_conservation.csv | median=**8.71** (cross-organ file); 6.91来自full_matrix(mouse) | Moderate |
| 12 | P61 | "Heart (mean ω = 24.3) and Lung (mean ω = 24.0)" | 24.3, 24.0 | 无法从任何源文件验证 | cross-organ file: Heart=5.52, Lung=8.44; all human: Heart=16.49, Lung=14.94 | Moderate |
| 13 | P61 | "Kidney (mean ω = 19.0) and Spleen (mean ω = 18.9)" | 19.0, 18.9 | 无法从任何源文件验证 | cross-organ file: Kidney=8.20, Spleen=10.63; all human: Kidney=13.06, Spleen=13.94 | Moderate |
| 14 | P63 | "Spearman r = -0.40 to +0.02, n = 60 pairs" | -0.40 to +0.02, n=60 | phase35_cross_organ_conservation.csv | r=**-0.59 to +0.04**, n=**59** | Moderate |

### 轻微错误（Minor）

| # | 位置 | 稿件原文 | 稿件值 | 数据来源文件 | 正确值 | 严重性 |
|---|------|---------|--------|-------------|--------|--------|
| 15 | P45 | "99.6% of control pairs had k_n < 0.05" | 99.6% | mouse_pilot_v2_results.csv | **100%** (6/6 C_control pairs all <0.05) | Minor |
| 16 | P25 vs P57 | LUAD mutations: P25 says n=497, P57 says n=492 | 497 vs 492 | 无独立源文件 | 内部不一致，P57子组求和61+120+311=492 | Minor |
| 17 | P25 vs P32 | LIHC Edmondson: P25 says n=289, P32 says n=288 | 289 vs 288 | 无独立源文件 | 内部不一致，P57子组求和39+133+105+11=288 | Minor |
| 18 | P25 vs P57 | KRAS: P25=121, P57=120; WT: P25=312, P57=311 | 121/312 vs 120/311 | 无独立源文件 | 内部不一致 | Minor |

---

## 三、内部不一致

| # | 位置A | 位置B | 不一致描述 |
|---|-------|-------|-----------|
| A | P19: "48 of 5,151 pairs (0.93%)" | P45: "48 pairs (0.15% of 5,151)" | 同一数据在P19中为0.93%，在P45中变为0.15%，两者均为错误（实际为0%） |
| B | P25: LUAD n=497 | P32: LUAD n=492 | TCGA LUAD突变样本数不一致 |
| C | P25: LIHC n=289 | P32: LIHC n=288 | LIHC Edmondson grade样本数不一致 |
| D | P114: Fig5 legend旧版 | P115: Fig5 legend新版 | 存在两个版本的Figure 5 legend（用户批注确认P114应删除） |
| E | P114/P115: "38 cell types" | phase35_cross_organ_conservation.csv | 文件仅含17个unique cell types，59行数据 |
| F | P114/P115: "1,406 pairwise ω values" | 无法从源文件验证 | full_matrix=703, cross-organ=59 |

---

## 四、一致性检查结果（通过的项）

以下数值经核验与源数据一致：

| 检查项 | 稿件值 | 源数据值 | 状态 |
|--------|--------|---------|------|
| Human pairs总数 | 5,151 | 5,151 | ✅ |
| Brain pairs总数 | 31,764 | 31,764 | ✅ |
| Mouse pilot pairs | 15 | 15 | ✅ |
| Full matrix pairs | 703 | 703 | ✅ |
| Human ω median | 13.68 | 13.6753 | ✅ |
| Human ω mean | 14.12 | 14.1184 | ✅ |
| Human ω range | 1.10–58.69 | 1.0984–58.6883 | ✅ |
| same_ct cross-organ count | 60 | 60 | ✅ |
| diff_ct same_organ count | 1,140 | 1,140 | ✅ |
| C_control mean ω | 1.54 | 1.5367 | ✅ |
| C_control median ω | 1.42 | 1.4226 | ✅ |
| C_control ω range | 1.09–2.10 | 1.0869–2.0983 | ✅ |
| S category mean ω | 4.03 (n=4) | 4.0256 (n=4) | ✅ |
| D category mean ω | 13.18 (n=3) | 13.1792 (n=3) | ✅ |
| Spearman r (human, all pairs) | -0.57 to -0.38 | -0.5677 to -0.3839 | ✅ |
| Standard metrics pairwise r | 0.57–0.95 | 0.5692–0.9536 | ✅ |
| Brain global mean (μ_grand) | 8.01 | 8.0068 | ✅ |
| Brain ω gradient fold | 6.06 | 14.3633/2.3716=6.06 | ✅ |
| Bergmann glia mean ω | 2.37 ± 1.14 (n=21) | 2.3716, 1.1421, 21 | ✅ |
| Committed OPC mean ω | 3.17 ± 1.47 (n=1,326) | 3.1668, 1.4715, 1326 | ✅ |
| Fibroblast mean ω | 3.99 ± 1.90 (n=3,403) | 3.9861, 1.9015, 3403 | ✅ |
| Vascular mean ω | 3.40 ± 1.24 (n=3,321) | 3.4045, 1.2448, 3321 | ✅ |
| Ependymal mean ω | 4.13 ± 1.73 (n=780) | 4.1334, 1.7294, 780 | ✅ |
| Microglia mean ω | 8.02 ± 4.93 (n=5,671) | 8.0241, 4.9321, 5671 | ✅ |
| Oligodendrocyte mean ω | 8.66 ± 4.44 (n=5,778) | 8.6598, 4.4446, 5778 | ✅ |
| OPC mean ω | 7.65 ± 4.03 | 7.6494, 4.0344 | ✅ |
| Astrocyte mean ω | 14.36 ± 8.68 (n=5,778) | 14.3633, 8.6797, 5778 | ✅ |
| OPC ω<15 (brain) | 93.6% (5,310/5,671) | 5310/5671=93.63% | ✅ |
| Strong candidates | 30 (0.09%) | 30/31764=0.094% | ✅ |
| Moderate candidates | 1,247 (3.93%) | 1247/31764=3.93% | ✅ |
| Weak candidates | 6,567 (20.67%) | 6567/31764=20.67% | ✅ |
| B cell cross-organ ω | 2.70 (n=1) | 2.7050 (n=1) | ✅ |
| Endothelial cross-organ ω | 15.09 ± 6.46 (n=3) | 15.0927, 6.4623, 3 | ✅ |
| Smooth muscle cross-organ ω | 6.29 (n=1) | 6.2911 (n=1) | ✅ |
| Plasma cell cross-organ ω | 6.61 ± 3.42 (n=6) | 6.6110, 3.4214, 6 | ✅ |
| Macrophage cross-organ ω | 9.84 ± 6.31 (n=15) | 9.8402, 6.3053, 15 | ✅ |
| Memory B cell cross-organ ω | 16.83 (n=1) | 16.8260 (n=1) | ✅ |
| TCGA total samples | 3,596 | 571+625+422+837+1141=3596 | ✅ |
| 参考文献 | 40 | 1-40 | ✅ |
| 主图 | 6 (Fig 1-6) | 6 | ✅ |
| 补充图 | 5 (S1-S5) | 5 | ✅ |

---

## 五、无法验证的数值

以下数值因缺少源数据文件或计算方法不明确而无法核验：

| 位置 | 稿件值 | 说明 |
|------|--------|------|
| P40 | k_n range 0.0147–0.0166 (HK gene set sensitivity) | 无对应输出文件 |
| P18 | CV <13% for 99.2% of pairs | 无对应输出文件 |
| P43 | AUC = 0.847 (mouse parameter sweep) | 无对应输出文件 |
| P52 | AUC = 0.716, 0.690, 0.887, 0.752 | 无对应输出文件 |
| P55 | heart-lung ω = 34.0, spleen-kidney ω = 13.8 | 无TCGA输出文件 |
| P55 | NN/TT ratios: BRCA 1.40, LIHC 2.83等 | 无TCGA输出文件 |
| P57 | 临床分层数值（PAM50, Edmondson grade等） | 无TCGA输出文件 |
| P114/P115 | "38 cell types" | cross-organ文件仅含17个cell types |
| P114/P115 | "1,406 pairwise ω values" | 无法从源文件推导 |

---

## 六、改进建议

### 必须修改

1. **P19/P45 k_n统计值**：将brain数据的k_n统计值替换为human数据的正确值。
   - 正确值：k_n median = 0.034, range = 0.0018–0.221, k_n < 0.001 = 0 pairs
   
2. **P19 ω<15比例**：将"93.6%"改为"56.3%"（基于human数据），或明确说明该比例来自brain OPC数据。

3. **P50 mouse mean ω**：将7.07替换为正确值。若引用mouse pilot整体数据，mean = 5.27, median = 3.63；若引用full matrix，mean = 7.62。若要保留cross-organ比较的语境，应明确说明n=2。

4. **P45 百分比修正**：
   - "99.6% of control pairs had k_n < 0.05" → 应为100%（6/6）
   - "0.15% of 5,151" → 应删除或修正为0%

### 建议修改

5. **P50/P52 ω均值修正**：same_ct cross-organ mean ω从8.70改为8.65；diff_ct same-organ mean ω从16.18改为16.00；different-organ mean从13.77改为13.58。

6. **P60 neutrophil SD**：从±1.15改为±1.22。

7. **P61 organ means**：核实Heart=24.3、Lung=24.0、Kidney=19.0、Spleen=18.9的来源，这些值与任何提供的数据文件都不匹配。

8. **P63 cross-organ correlations**：核实r = -0.40 to +0.02的范围，实际计算结果为-0.59 to +0.04（n=59, not 60）。

9. **P25/P32/P57 TCGA数值统一**：统一LUAD mutations n值（497 vs 492）和LIHC Edmondson n值（289 vs 288）。

10. **P114/P115 Figure 5 legend**：删除旧版P114，保留用户重写的P115。核实"38 cell types"和"1,406 pairwise ω values"的来源。

### 建议补充

11. 在Methods或Supplementary中提供所有k_n和ω统计值的计算脚本，确保可重复性。
12. 对于跨数据集引用的统计值，明确标注数据来源（human/mouse/brain），避免混淆。
