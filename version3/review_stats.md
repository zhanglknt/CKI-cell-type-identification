# CKI 稿件统计分析审稿报告

**审稿人**: stats-reviewer
**稿件版本**: v10
**审稿日期**: 2026-07-26

---

## 1. 统计严谨性评分：4/10

稿件在概念设计上有亮点（bootstrap置换检验、BH校正、效应量报告），但存在多个**Critical级数据错误**——Methods中的关键统计量将brain数据误标为human数据，且存在内部不一致、样本量不足下的过度推断、bootstrap分辨率不足以支撑FDR声明等问题。这些问题直接影响结论的可信度，必须在修稿前彻底修正。

---

## 2. Critical 统计问题

### C1. P19/P45 k_n 统计量将 brain 数据误标为 human 数据

**问题**: 稿件P19（Methods）和P45（Results）报告的k_n描述性统计实际来自brain数据集，而非human数据集。

| 统计量 | 稿件报告值 | Human实际值 | Brain实际值 |
|--------|-----------|------------|------------|
| k_n median | 0.0086 | **0.034** | 0.0086 |
| k_n range | 0.0004–0.106 | **0.0018–0.221** | 0.0004–0.106 |
| k_n < 0.001 对数 | 48 | **0** | 48 |
| ω < 15 比例 | 93.6% | **56.3%** | 88.7% (OPC子集93.6%) |

**验证**:
- Human数据（5,151对）：k_n median = 0.034123, range = 0.001830–0.221360, k_n < 0.001的对数 = 0
- Brain数据（31,764对）：k_n median = 0.008593, range = 0.000351–0.106215, k_n < 0.001的对数 = 48

稿件P19原文："In our datasets, k_n had a median of 0.0086 (range 0.0004–0.106); only 48 of 5,151 pairs (0.93%) had k_n < 0.001." —— 这里的k_n统计量来自brain（31,764对），但分母"5,151 pairs"和百分比"0.93%"是按human数据计算的。两个数据集的统计量被混搭在一起。

**影响**: 这是方法论核心参数的错误报告。k_n是CKI算法的关键参数，其稳定性论证直接建立在正确的描述性统计之上。读者无法判断方法的适用条件。

### C2. P19 "93.6% of all ω values were < 15" 来源错误

**问题**: P19声称"93.6% of all ω values were < 15"，但：
- Human数据实际仅 **56.3%** 的ω值 < 15
- Brain整体为 88.7%
- 93.6% 仅对应brain中Oligodendrocyte precursor（OPC）的子集（5,310/5,671 = 93.6%）

**影响**: 该统计量被用于论证"the method is robust for the vast majority of comparisons"，但56.3%远未达到"vast majority"。这严重夸大了方法的鲁棒性。

### C3. P50 mouse mean ω = 7.07 误导性报告

**问题**: P50称"mouse (mean ω = 7.07)"，但：
- Mouse pilot（n=15）整体mean ω = **5.27**
- 7.07 实际是pilot数据中X_cross类别（仅n=2）的均值
- Mouse full matrix（n=703）mean ω = 7.62

P112 Figure 3A legend明确标注"mouse (n = 15 shared cell types)"，确认使用的是pilot数据。用n=2的子类均值代表整体mouse水平是统计上的严重误导。

用户批注（Comment 18）已指出此问题："由mouse_pilot_v2_results.csv手算：median = 3.63，mean = 5.27"。

### C4. P45 内部不一致：0.15% vs 0.93%

**问题**: 
- P19说"48 of 5,151 pairs (0.93%)" —— 48/5151 = 0.93% ✓（但48这个数字来自brain）
- P45说"Only 48 pairs (0.15% of 5,151)" —— 48/5151 = 0.93%，**非0.15%**
- 0.15%实际对应48/31,764（brain数据）

同一稿件内对同一数字给出两个不同的百分比，且都不正确对应所声称的数据集。

---

## 3. Major 统计问题

### M1. Bootstrap分辨率不足以支撑FDR校正

**问题**: 
- B=1,000时，bootstrap P值的最小可能值为1/(B+1) = 1/1001 ≈ 0.001
- 对5,151对human数据做BH FDR校正（q=0.05），第k小的阈值 = 0.05 × k/5151
- 第1个阈值 = 9.71×10⁻⁶，远小于bootstrap能产生的最小P值（0.001）
- 这意味着**最显著的约100个检验的FDR阈值都低于bootstrap P值的分辨率极限**
- 对31,764对brain数据，问题更严重：第1个阈值 = 1.57×10⁻⁶

**影响**: 声称"BH FDR correction was applied"在技术上是正确的，但对最显著的检验而言，FDR校正形同虚设——无法区分p=0.001和p=0.0001的检验。应增加B至10,000或更多，或改用解析方法。

### M2. Human数据CSV缺少bootstrap P值

**问题**: `phase33_v3_human_pairs.csv`仅包含pair, omega, kn, kf, same_organ, same_ct列，**没有p_value列**。无法验证：
- 哪些对达到统计显著
- BH FDR校正后的q值
- Cohen's d效应量

稿件称"adjusted q-values are reported in Supplementary Tables S1-S2"，但主数据文件中缺失这些关键统计量，影响可重复性。

### M3. Mouse pilot样本量严重不足（n=15）

**问题**: Mouse pilot仅15对（6 control + 4 S + 3 D + 2 X）：
- X_cross类别仅n=2，无法进行任何有意义的统计推断
- S_same_ct仅n=4，均值估计的95% CI宽度极大
- 校准实验仅n=6 controls，TOST等效检验明确承认"did not confirm strict equivalence at this sample size"
- 但稿件仍基于n=15的pilot数据报告mouse vs human的比较（P50, P112）

**建议**: 应使用full matrix（703对）作为mouse的主分析数据。P112 Figure 3A的mouse vs human比较应基于703对而非15对。

### M4. 跨器官保守性分析统计效力不足

**问题**: P59-63的跨器官保守性分析仅60对same-cell-type cross-organ比较：
- 多个细胞类型仅n=1-3对（B cell n=1, Smooth muscle n=1, Memory B n=1, Endothelial n=3）
- 稿件承认"exploratory due to small sample sizes"但仍报告mean ± SD并做跨细胞类型排序
- P63报告"Spearman r = -0.40 to +0.02, n = 60 pairs"——n=60分散到10+细胞类型后，每个类型的有效n极小

**影响**: Table 2的细胞类型constraint排名缺乏统计效力支撑，尤其是n=1的细胞类型不应报告均值作为代表性指标。

### M5. 效应量报告不完整

**问题**:
- Same-organ vs different-organ比较（P52）报告Mann-Whitney P < 0.001，但未报告效应量。实际计算：rank-biserial r = -0.136，属**小效应量**（|r| < 0.3），与"striking reversal"的叙述不匹配
- Brain ω梯度（2.37–14.36）报告了mean ± SD但无置信区间
- TCGA分析中NN/TT比值的Cohen's d（P55）报告了部分值（BRCA +1.04, LUSC -1.98, LIHC -1.22），但LUAD和KIRC仅说"negligible deviations"未给数值
- P57临床分析中ω随grade变化的Jonckheere-Terpstra趋势检验未报告效应量（如Kendall's τ或ε²）

### M6. Multiplicative residual模型阈值缺乏正式统计推断

**问题**: P30/P72的Strong/Moderate/Weak阈值（residual < 0.3/0.5/0.75）基于经验百分位（第1/5/25百分位），而非正式零分布：
- 稿件承认"these thresholds are calibrated on the observed data rather than a formal null distribution"
- 置换检验敏感性分析仅提及在Supplementary Fig. S5，未在正文报告结果
- 30个Strong候选信号中，无法评估假阳性率

**建议**: 应在正文中报告置换检验的阈值校准结果，并给出Strong候选信号的估计FDR。

---

## 4. Minor 统计问题

### m1. P42 bootstrap B值不一致

P21说"B = 500 for mouse calibration and exploratory analyses; B = 1,000 for human, TCGA, and brain primary analyses"，但P42又说"Bootstrap inference uses B = 500"，P110 Figure 1C legend说"B = 500 permutations"。应统一表述。

### m2. P112 Figure 3A legend标注错误

Figure 3A legend说"human (n = 2000 pairs)"，但human数据实际有5,151对。2,000可能是HVG数量被误标为pair数。

### m3. P50 same-organ/different-organ均值与实际数据有偏差

| 统计量 | 稿件值 | 实际值 |
|--------|--------|--------|
| Same CT cross-organ mean ω | 8.70 | 8.65 |
| Diff CT same-organ mean ω | 16.18 | 16.00 |
| Same-organ mean ω | 16.18 | 16.00 |
| Diff-organ mean ω | 13.77 | 13.58 |

偏差较小，可能是四舍五入或数据版本差异，但应核实。

### m4. Spearman相关性P值报告不精确

稿件称"all P < 0.001"，实际P值范围为1.71×10⁻¹⁸⁰ 到 5.37×10⁻²⁴⁵。建议报告更精确的P值或使用-log10(P)表示。

### m5. 校准CI方法未说明

P46报告"95% bootstrap CI [1.12, 2.08]"但未说明bootstrap次数和CI计算方法（percentile法还是BCa法）。

### m6. TOST等效界限选择缺乏依据

P46的TOST等效界限[0.67, 1.50]未说明选择依据。这些界限应基于生物学或实践考量预先指定。

### m7. 4种距离度量的选择

选择的4种标准度量（Raw JS, Spearman dist, Cosine dist, Marker Jaccard）覆盖了信息论、秩相关、角度、集合论四个维度，基本合理。但缺少：
- Euclidean distance（最基础的度量）
- Pearson correlation distance（与Spearman互补）

建议至少在Supplementary中补充与Euclidean和Pearson的比较，以论证CKI的"独立信息维度"声明不依赖于度量选择。

### m8. 跨器官保守性P63相关性报告

P63称"CKI showed little agreement with standard metrics (Spearman r = -0.40 to +0.02, n = 60 pairs)"，但未提供P值。n=60时r=-0.40对应p≈0.002，具有统计显著性，与"little agreement"的叙述需更精确表述。

---

## 5. 统计方法改进建议

### 建议1：立即修正数据集混淆（Critical）
- P19/P45的k_n统计量必须替换为human数据实际值：median = 0.034, range = 0.0018–0.221, k_n < 0.001 = 0对
- "93.6% < 15"必须修正为human的56.3%，或明确说明该统计量来自brain OPC子集
- P45的"0.15%"必须修正为"0.93%"（如果指human）或改为"48/31,764 (0.15%)"（如果指brain）

### 建议2：增加Bootstrap重采样次数
- 对主分析（human 5,151对, brain 31,764对），B应增至≥10,000
- 或采用半解析方法（如基于Gamma分布拟合null分布）提高P值分辨率
- 对FDR校正后的q值，应报告分辨率极限

### 建议3：以Full Matrix替代Pilot作为Mouse主数据
- 703对的full matrix比15对的pilot具有更大统计效力
- Figure 3A的mouse vs human比较应基于full matrix
- Pilot数据可作为方法开发的历史说明

### 建议4：补充效应量报告
- Same-organ vs different-organ比较应报告rank-biserial r及解读
- Brain ω梯度应补充各细胞类型的95% CI
- 临床分析应补充Jonckheere-Terpstra的效应量（如Kendall's τ）

### 建议5：完善Multiplicative Residual模型的统计推断
- 在正文报告置换检验校准结果
- 给出Strong候选信号的估计FDR
- 考虑使用正式的异常检测框架（如基于beta分布的outlier检测）

### 建议6：补充Human数据的P值和q值
- 主数据CSV应包含bootstrap P值、Cohen's d、BH校正后q值
- 或在Supplementary Table中提供完整统计量

### 建议7：统一bootstrap B值表述
- 在Methods中一次性定义B值策略，正文和Figure legend保持一致

---

## 附录：关键数据验证汇总

| 验证项 | 稿件值 | 实际值 | 数据来源 | 判定 |
|--------|--------|--------|---------|------|
| Human k_n median | 0.0086 | 0.034 | phase33_v3_human_pairs.csv | **错误**（实为brain值） |
| Human k_n range | 0.0004–0.106 | 0.0018–0.221 | phase33_v3_human_pairs.csv | **错误**（实为brain值） |
| Human k_n < 0.001 | 48对 | 0对 | phase33_v3_human_pairs.csv | **错误**（48来自brain） |
| Human ω < 15 比例 | 93.6% | 56.3% | phase33_v3_human_pairs.csv | **错误**（93.6%来自OPC） |
| Mouse mean ω | 7.07 | 5.27 (pilot) / 7.62 (full) | mouse_pilot / full_matrix | **误导**（7.07是X类n=2均值） |
| P45 "0.15% of 5,151" | 0.15% | 0.93% (48/5151) | 计算 | **计算错误** |
| Calibration mean ω | 1.54 | 1.54 | mouse_pilot C_control | ✓ |
| Calibration range | 1.09–2.10 | 1.09–2.10 | mouse_pilot C_control | ✓ |
| Human ω median | 13.68 | 13.68 | phase33_v3_human_pairs.csv | ✓ |
| Human ω mean | 14.12 | 14.12 | phase33_v3_human_pairs.csv | ✓ |
| Brain μ_grand | 8.01 | 8.01 | brain_siletti_omega_pairs_v3.csv | ✓ |
| Brain Astrocyte mean ω | 14.36 | 14.36 | brain_siletti_omega_pairs_v3.csv | ✓ |
| Brain Bergmann glia mean ω | 2.37 | 2.37 | brain_siletti_omega_pairs_v3.csv | ✓ |
| CKI vs Spearman dist r | -0.57 | -0.5677 | phase35_metric_correlation.csv | ✓ |
| CKI vs Marker Jaccard r | -0.38 | -0.3839 | phase35_metric_correlation.csv | ✓ |
| Same CT cross-organ n | 60 | 60 | phase33_v3_human_pairs.csv | ✓ |
| Diff CT same-organ n | 1,140 | 1,140 | phase33_v3_human_pairs.csv | ✓ |
