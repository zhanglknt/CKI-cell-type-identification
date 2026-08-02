# 专家1：算法与方法学审稿报告 — CKI v25

**Reviewer**: E1 — 算法方法与计算实现专家
**Date**: 2026-08-01
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v25 (25 files)
**Review baseline**: v20→v22→v25. v22 expert score: 6.0/10

---

## 1. 总体评估

**v25 Score: 7.5/10** (v22: 6.0/10, +1.5)

v25 是一次大幅方法学修复。v22 标记的两个算法阻塞项——**C1（残差模型 BH-FDR q值疑误）**和 **C3（Mouse k_n 方案矛盾）**——在 v25 中均已修复。C1 的修复采用了极值理论（EVT/GPD）外推方法，在方法学上是正确的，有效解决了置换检验 P 值饱和问题。C3 的修复通过明确区分 mouse 全成对矩阵（global HVG）和 pilot 分析（hybrid per-pair DE）的 k_f 方案，消除了文档矛盾。

20 个 Major Issues 中，与算法相关的项目大部分已修复，但 **M5（Cohen's d → SES 术语统一）修复不完整**——manuscript 已改用 SES，但 supplementary 和 reproducibility guide 仍保留 "Cohen's d"，且 manuscript 自身 Limitations 段也残留一处。此外发现 **supplementary 标题仍为旧版 "Selective"**（C6 修复遗漏）。

### 评分变动理由

| 维度 | v22 | v25 | 变动原因 |
|------|-----|-----|----------|
| 算法正确性 | 5 | 8 | C1 EVT修复正确，C3 方案统一，C4/C5 修复 |
| 文档完整性 | 6 | 7 | M5 术语统一不完整，supplementary标题遗漏 |
| 代码质量 | 6 | 7 | 算法描述改善，EVT方法学论证充分 |
| 复现性 | 6 | 7.5 | 参数表全面，但 Repro Guide Section 3.2 brain k_n 描述有误 |

---

## 2. Critical Issues 修复验证

### 2.1 C1: 残差模型 BH-FDR q值 [✅ RESOLVED]

**v22 问题**: 稿件报告 q=2.75e-4，但标准 BH 计算使用 m=30（Strong 候选数）而非 m=31,764（总比较数），导致 q 值被严重低估。若使用 m=31,764，则 q ≈ 0.291，远超 0.05 阈值。

**v25 修复**:

v25 采用了一个完全不同的、方法学上正确的方案来解决此问题：

1. **EVT/GPD 外推**: 对 11,541/31,764 (36.3%) 达到经验 P 值下限 (P = 9.99×10⁻⁵, B=10,000) 的信号，使用 Peaks-Over-Threshold (POT) 方法拟合广义帕累托分布 (GPD)
2. **公式正确**: P_EVT = (K/B) × S_GPD(u − observed_residual)，其中 K=500, B=10,000, S_GPD 为 GPD 生存函数。这是标准的 POT 方法公式：
   - K/B = 超过阈值的概率
   - S_GPD(u − observed) = 给定超过阈值后的条件概率
   - 乘积 = 无条件 P 值
3. **BH-FDR 全集校正**: 使用 m = 31,764 对所有 EVT 外推 P 值进行 BH-FDR 校正（而非仅对 30 个 Strong 候选）
4. **结果**: 16/30 Strong 候选达到 FDR < 0.05（6 个 astrocyte + 10 个 oligodendrocyte），其余 14 个未达到显著性 (P ≥ 0.76, q = 1.0)

**方法学评估**: PASS ✓

- EVT/POT 是解决置换检验 P 值饱和的标准方法
- GPD 拟合成功率 100% (11,541/11,541)，无回退
- BH-FDR 使用 m=31,764 是正确的——这是所有脑区跨区域比较的总数
- 非独立性问题已被承认（manuscript Methods: "the per-signal tests are not independent"）
- EVT 外推 P 值范围 (1×10⁻¹⁰ to 9.99×10⁻⁵) 合理

**残留技术关注**（非阻塞）:
- GPD 参数估计（shape ξ, scale σ）和拟合优度统计量未报告
- K=500 的选择未明确论证（常用规则为 top 10% = 1,000，K=500 更保守）
- BH 在正回归依赖下保守有效，但非独立性的影响未被定量评估

### 2.2 C2: k_n floor 参数表 [✅ RESOLVED, inherited from v22]

参数表第 313 行: `k_n floor (minimum) | 1e-4 | all analyses`
与 `cki/core.py:242` (`kn_min = 1e-4`) 一致。Algorithm 1 伪代码第 7 行也包含 floor 逻辑。

### 2.3 C3: Mouse k_n 方案矛盾 [✅ MOSTLY RESOLVED]

**v22 问题**: 稿件描述 mouse 使用 "per-pair" k_n，复现指南描述 "global" k_n，两者矛盾。

**v25 修复**:

v25 明确区分了 mouse 的两种分析模式：

| 分析 | k_n 方案 | k_f 方案 | 出处 |
|------|---------|---------|------|
| Mouse 全成对矩阵 (Fig.2, 703 pairs) | global | global HVG 2,000 | Repro Guide §4.1 |
| Mouse pilot (calibration + 15 pairs) | global | per-pair top-200 DE | Repro Guide §3.2 |
| Human (Tabula Sapiens) | global | per-pair top-200 DE | Repro Guide §3.2 |
| TCGA | global | per-pair top-200 DE | Repro Guide §3.2 |
| Brain | **per-pair** | per-pair top-200 DE | Manuscript, Param Table |

Manuscript 明确指出: "mouse pilot data (calibration and validation) uses the same hybrid scheme as human (global k_n from shared HK genes, per-pair k_f from top-200 DE genes), while the mouse full pairwise matrix (703 pairs, Fig. 2 heatmap) uses a global HVG 2,000 set for k_f."

Supplementary Note 2 Algorithm 2 也一致: "Unlike the Tabula Muris full pairwise matrix (global HVG set for Fig. 2), Tabula Sapiens and all pilot analyses (mouse calibration, human, TCGA, brain) employ pairwise identity gene selection"

**方法学评估**: PASS ✓（mouse 方案矛盾已消除）

**残留不一致**（Minor）: Reproducibility Guide Section 3.2 将 brain 与 human/TCGA 一并归入 "hybrid mode"，描述为 "keeping all pairs on a common k_n scale"。但 manuscript 和参数表均明确 brain 使用 **per-pair k_n**（CV=97.35%），而非 global k_n。这是文档措辞错误，不影响算法正确性，但会引起复现者困惑。建议在 Section 3.2 中将 brain 单独说明。

### 2.4 C4: HK 基因中性假设 [✅ RESOLVED]

Manuscript Discussion: "housekeeping (HK) genes are under stabilizing selection that constrains their expression variance across conditions, making them a practical **constrained baseline**"（不再使用 "neutral"）。

Discussion 继续指出: "HK genes are defined empirically (high detection rate, low CV) rather than mechanistically (synonymous sites in Ka/Ks), and their expression variance could reflect regulatory constraints rather than pure neutral drift; sensitivity analysis with alternative low-variance gene sets (r > 0.95) partially mitigates this concern."

术语从 "neutral baseline" 转为 "constrained baseline" 是正确的——承认 HK 基因不是严格中性的，而是受稳定化选择约束。

### 2.5 C5: OPC 阴性对照 [✅ RESOLVED]

Manuscript 新增专门小节 "OPCs: internal consistency check":

"The model is not simply detecting high ω values or absolute transcriptional differences; it identifies cell-type/region-pair combinations where the observed functional divergence is substantially below what the cell type's global plasticity and the region pair's background divergence would jointly predict."

"The complete absence of Strong signals despite OPCs being the brain's most motile cell type demonstrates that the residual model differentiates between broad baseline motility and specific transcriptional signatures of developmental history."

这将 OPC 的零 Strong 信号从"可能是模型产物"重新定义为"内部一致性验证"，逻辑成立：如果模型仅检测运动性，OPC 应有最多 Strong 信号；但 OPC 有 0 个，说明模型检测的是发育起源特征而非运动性。

### 2.6 C6: 标题措辞 [⚠️ PARTIALLY RESOLVED]

Manuscript 标题已改为 "Baseline-Normalized Transcriptomic Remodeling" ✓
Cover letter 标题一致 ✓
**但 Supplementary 标题仍为旧版 "Selective Transcriptomic Remodeling"** ✗

这是一个明确的遗漏——C6 修复未覆盖 supplementary 文件。

### 2.7 C7: NAR 格式 [✅ RESOLVED]

- Keywords: ✓ (cell-state divergence, housekeeping genes, Jensen-Shannon decomposition, transcriptomic remodeling, single-cell genomics)
- Running title: ✓ (CKI: Baseline-Normalized Divergence Index)
- ORCID: ✓ (0000-0002-0698-0754)

---

## 3. Major Issues 修复验证（算法相关）

### M1: 校准因子 n=6 不足 + 跨方案适用性 [✅ RESOLVED]

Manuscript 明确讨论 CV ≈ 60% 和 n=6 的限制:
"the current sample size (n = 6) with a coefficient of variation of ~60% limits the power of such tests and the precision of the calibration factor (ω_cal = ω / 6.67)."

Discussion Limitation #7 新增跨方案适用性警告:
"the empirical calibration factor (ω_cal = ω / 6.67) was derived from mouse split-half controls using a global HVG set for k_f, but is applied to human, TCGA, and brain analyses that use per-pair DE gene selection for k_f. The calibration factor has not been independently validated for the per-pair DE scheme, and cross-scheme transferability should be verified through matched calibration experiments in each analysis scheme."

### M2: 方法比较局限性 [✅ RESOLVED]

Discussion 新增: "we did not quantitatively benchmark CKI against these specialized methods, as they address different questions (cross-species alignment vs. within-species functional divergence). A systematic comparison on shared datasets would clarify the complementary strengths of each approach."

### M3: "Global k_n" 歧义 [✅ RESOLVED]

Manuscript 和 Supplementary 现在明确区分 global k_n (human/TCGA) 和 per-pair k_n (brain)。Supplementary Note 3.7 专门讨论 per-pair k_n 变异性 (CV=97.35%)。

### M4: DE gene 循环膨胀 [✅ RESOLVED]

Discussion Limitation #3 新增: "the circular dependency inherent in the per-pair k_f scheme: the top-200 differentially expressed genes are selected by |μ_A − μ_B|, meaning that the genes defining 'functional divergence' are precisely those with the largest expression differences between the two groups under comparison. While the permutation test preserves this selection procedure under the null hypothesis, the circularity means that k_f magnitudes lack independent external validation and should be interpreted as an upper bound on functional divergence."

这是一个准确的统计学描述——循环性在零假设下被置换检验保留，但 k_f 的绝对值缺乏独立验证。

### M5: "Cohen's d" → "standardized effect size (SES)" [⚠️ INCOMPLETE]

**MANIFEST 声称**: "M5: 'Cohen's d' → 'standardized effect size (SES)' (all 4 docs)"

**实际情况**: 修复不完整。以下文档仍保留 "Cohen's d"：

| 文档 | 位置 | 内容 |
|------|------|------|
| Manuscript | Limitations §7 | "Cohen's d is reported as a descriptive measure of effect size" |
| Supplementary | Algorithm 1 Output | "Output: omega, P-value, Cohen's d, null distribution" |
| Supplementary | Note 1.5 | "Effect size: Cohen's d = (omega_obs - mean(omega_null))/sd(omega_null)" |
| Supplementary | Note 3.4 | "Cohen's d should be interpreted as a non-parametric descriptive statistic" |
| Repro Guide | §5.1 | "Effect size: Cohen's d = (omega_obs - mean_null) / std_null" |
| Repro Guide | §5.3c | "Cohen's d reported as descriptive measure" |

Manuscript 正文已改用 SES (5 处)，Supplementary 部分改用 (3 处)，但 Repro Guide 完全未改 (0 处)。术语不统一会影响读者理解——SES 和 Cohen's d 在统计学上有不同内涵（Cohen's d 假设正态分布，SES 是更通用的标准化效应量）。

### M6: 跨数据集 omega 不可比 [✅ RESOLVED]

Discussion: "Users should compare ω ranks rather than absolute values across datasets."
Manuscript 明确解释: "The different k_f gene selection strategies (per-pair DE vs. global HVG) alter the effective ω scale between analyses."

### M9: 置换检验 mu_ct/mu_pair 重计算 [✅ RESOLVED]

Manuscript Methods 明确描述: "cell type labels were shuffled within each region pair (B = 10,000 permutations), and per-signal empirical P-values were computed." 标签在 region pair 内打乱，意味着 mu_ct 和 mu_pair 从置换数据中重新计算。

### M11: 维度不变性模拟 [✅ RESOLVED]

Supplementary Note 3.6 新增限制性讨论: "this simulation addresses dimensionality per se (random probability vectors of different lengths) but does not simulate the variance-based gene selection mechanism that generates the ω inflation. A more complete validation would test whether the inflation magnitude scales with the stringency of variance filtering rather than gene count."

这是一个准确的自我批评——原始模拟测试了维度（基因数量）而非选择机制（方差过滤），后者才是 ω 膨胀的真正来源。

### M12: Supplementary 误写 mouse k_f 方案 [✅ RESOLVED]

Supplementary Note 2 Algorithm 2 现在正确区分: "Unlike the Tabula Muris full pairwise matrix (global HVG set for Fig. 2), Tabula Sapiens and all pilot analyses (mouse calibration, human, TCGA, brain) employ pairwise identity gene selection"

### M14: ω 校准因子论证 [✅ RESOLVED]

Manuscript 和 Supplementary Note 3.5 详细解释了校准因子的来源和用途。ω_cal = ω / 6.67 将等价总体的 ω 重标定为 ~1.0。

### M15: Supplementary Algorithm 1 修正 [⚠️ PARTIALLY RESOLVED]

Algorithm 1 伪代码第 7 行已添加 k_n floor 逻辑: "if k_n < 1e-4: k_n <- 1e-4" ✓
但 Output 行仍为 "Cohen's d" 而非 "SES" ✗（与 M5 相同的术语问题）

### M17: Discussion 压缩 [✅ RESOLVED]

Discussion 结构清晰，包含方法比较、TCGA caveats、脑分析总结、限制和未来方向。无明显冗余。

### M19: 参考文献编号 [✅ RESOLVED]

参考文献 1-41 编号连续，正文引用与参考文献列表对应。

### M20: k_n 变异性讨论 [✅ RESOLVED]

Manuscript 新增: "Analysis of per-pair k_n across 31,764 brain comparisons revealed substantial cross-pair variability (CV = 97.35%), and the Spearman correlation between per-pair ω and global-k_n ω was only -0.027 (P = 9.96e-07), confirming that pair-specific k_n is essential for accurate ω ranking."

Supplementary Note 3.7 提供了详细的 per-cell-type k_n CV 数据（37.6% to 81.4%）。

---

## 4. 新发现问题

### N1: Supplementary 标题仍为旧版 "Selective" [Medium]

Supplementary 第 2 行: "CKI: A Cell-state Kinetic Index for Quantifying **Selective** Transcriptomic Remodeling"

Manuscript 和 Cover Letter 均已改为 "Baseline-Normalized"，但 Supplementary 遗漏。这是 C6 修复的遗漏。

### N2: "Cohen's d" 术语残留 [Medium]

详见 M5 分析。Manuscript (1处)、Supplementary (4处)、Repro Guide (2处) 共 7 处残留。MANIFEST 声称 "all 4 docs" 已修复，但实际未完成。

### N3: Repro Guide Section 3.2 Brain k_n 描述矛盾 [Minor]

Repro Guide §3.2: "The hybrid mode (per-pair top-200 DE) is used for ... brain atlas analyses to give each cell-type pair the most informative identity genes while keeping all pairs on a **common k_n scale**."

但 Manuscript 和参数表均明确 brain 使用 **per-pair k_n** (CV=97.35%)，不是 "common k_n scale"。建议将 brain 从 hybrid mode 列表中分出，单独说明其使用 per-pair k_n + per-pair k_f。

### N4: HK 基因匹配数不一致 [Minor]

| 文档 | 数据集 | HK 基因数 |
|------|--------|----------|
| Manuscript | Tabula Sapiens | 1,130 |
| Supplementary | Tabula Sapiens | 1,130 (1,129 matched) |
| Manuscript | Brain (Siletti) | 1,115 matched |
| Supplementary | Brain | 1,130 (未提及匹配数) |
| Repro Guide | Brain | 1,130 (未提及匹配数) |

Manuscript 提到 brain 有 1,115 基因匹配到 Siletti 注释，但 Supplementary 和 Repro Guide 均未提及此匹配数。建议统一报告。

### N5: Supplementary Note 3.3 两层 BH-FDR 描述可能混淆 [Minor]

Supplementary Note 3.3 描述了"两层" BH-FDR：
1. "per-signal BH-FDR across all 31,764 EVT-empirical P-values, yielding 11,556 pairs with FDR < 0.05"
2. "BH-FDR across all 31,764 EVT-extrapolated P-values (m = 31,764), with 16 of 30 Strong-tier candidates passing FDR < 0.05"

第 (1) 层使用 "EVT-empirical P-values"（经验 P 值 + EVT 外推），第 (2) 层使用 "EVT-extrapolated P-values"。两层似乎指向同一分析但从不同角度描述，可能引起读者困惑。建议合并为单一描述。

### N6: GPD 拟合参数未报告 [Minor, technical]

Manuscript 报告 GPD 拟合成功率 100%，但未报告：
- Shape parameter (ξ) 和 scale parameter (σ) 的估计值或范围
- 拟合优度统计量（如 Anderson-Darling, Kolmogorov-Smirnov）
- K=500 选择的依据

这些信息对评估 EVT 外推的可靠性很重要。建议在 Supplementary 中添加 GPD 拟合诊断表。

### N7: Cover Letter Python 版本不一致 [Trivial]

Cover Letter: "The CKI package is implemented in Python (≥3.9)"
Manuscript: "Python 3.13.12"
Repro Guide: "Python: 3.13.12"

Cover Letter 说 ≥3.9，但实际测试环境是 3.13.12。这不是错误（≥3.9 是兼容性声明），但建议确认 Python 3.9 是否真的兼容（numpy 2.4.6 等较新依赖可能要求更高版本）。

---

## 5. 参数一致性检查

### 跨文档核心参数

| 参数 | Manuscript | Supplementary | Repro Guide | 一致? |
|------|-----------|--------------|-------------|-------|
| HK 基因来源 | HRT Atlas v1.0 | HRT Atlas v1.0 | HRT Atlas v1.0 | ✓ |
| HK 基因总数 | 1,130 | 1,130 | 1,130 | ✓ |
| Mouse HVG (full matrix) | 2,000 | 2,000 | 2,000 | ✓ |
| Per-pair DE genes | 200 | 200 | 200 | ✓ |
| Bootstrap B (all datasets) | 1,000 | 1,000 | 1,000 | ✓ |
| Permutation B (residual) | 10,000 | 10,000 | 10,000 | ✓ |
| k_n floor | (未在正文提及) | 1e-4 (Algo 1) | 1e-4 (param table) | ✓ |
| Epsilon (JS pseudocount) | (未在正文提及) | 1e-9 (Note 3.11) | 1e-9 (param table) | ✓ |
| Random seed | 42 | (未提及) | 42 | ✓ |
| Min cells (mouse/human) | 10 | 10 | 10 | ✓ |
| Min cells (brain) | 20 | (未提及) | 20 | ✓ |
| Calibration baseline | 6.67 | 6.67 | 6.67 | ✓ |
| Brain grand mean ω | 8.01 | 8.01 | 8.01 | ✓ |
| BH-FDR m | 31,764 | 31,764 | 31,764 | ✓ |
| EVT K | 500 | 500 | 500 | ✓ |
| Python version | 3.13.12 | (未提及) | 3.13.12 | ✓ |
| JS log base | 2 | 2 | 2 | ✓ |
| Normalization | CP10k + log1p | CP10k + log1p | CP10k + log1p | ✓ |

**参数一致性总体评价**: 良好。核心参数在三个文档间一致。主要问题集中在术语（Cohen's d vs SES）和 brain k_n 方案描述。

---

## 6. 算法方法学评估

### 6.1 CKI 核心算法

**ω = k_f / k_n 的数学合理性**:

- k_n = JS(softmax(μ_A[H]), softmax(μ_B[H]))：HK 基因集上的 JS 散度，作为基线 ✓
- k_f = JS(softmax(μ_A[I]), softmax(μ_B[I]))：身份基因集上的 JS 散度，作为功能差异 ✓
- softmax 归一化确保 JS 散度输入为概率分布 ✓
- base-2 对数使 JS ∈ [0,1]，且不影响 ω 比值（对数底在分子分母中抵消）✓

**维度不变性**: Supplementary Fig. S10 的 Dirichlet 模拟 (d=50 to 5,000, mean JS 0.155-0.159) 验证了 JS 散度不受维度系统性影响。但 M11 指出该模拟未捕捉方差选择机制——这是诚实的自我评估。

### 6.2 置换检验

- 零假设: 两个细胞群体来自同一分布（标签可交换）✓
- 统计量: ω = k_f/k_n，在每次置换中重新计算 ✓
- P 值公式: P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) ✓（单侧，+1 伪计数避免 P=0）
- 效应量: SES = (ω_obs - μ_null)/σ_null ✓（但术语未统一）
- 基因选择程序在零假设下保留 ✓（per-pair DE 在每次置换中重新选择）

### 6.3 残差模型 + EVT

- 乘法模型: expected_ω = μ_ct × μ_pair / μ_grand ✓（标准两因素加法模型的乘法版本）
- 残差: observed / expected ✓
- 置换设计: region pair 内打乱 cell type 标签 ✓
- EVT/POT: GPD 拟合 500 个最小 null residual，外推 P 值 ✓
- BH-FDR: m = 31,764（全部信号）✓

### 6.4 循环依赖问题

Manuscript 正确识别并讨论了 per-pair k_f 的循环依赖：
- top-200 DE genes 由 |μ_A - μ_B| 选择，而这些差异正是 k_f 所测量的
- 置换检验在零假设下保留了此选择程序，因此 P 值有效
- 但 k_f 绝对值缺乏独立外部验证，应视为功能差异的上界

这是一个准确的统计学评估。循环性不影响显著性检验的有效性（因为置换检验保持了选择程序），但影响效应量的可解释性。

---

## 7. 创新性评估

CKI 的核心算法创新——双基因集 JS 散度归一化（HK 基因作为基线，HVG/DE 基因作为功能集）——仍然成立。v25 的主要改进在于：

1. **EVT 外推**: 首次将极值理论应用于单细胞转录组比较的置换检验 P 值饱和问题，这是一个有价值的统计学贡献。
2. **乘法残差模型**: 用于检测脑区间的发育签名，设计合理。
3. **OPC 内部一致性验证**: 将 OPC 的零信号结果转化为模型特异性的验证，逻辑巧妙。

与现有方法（SAMAP, SATURN, CACIMAR）的区分现在更加明确：CKI 解决的是种内功能差异量化，而非跨物种对齐。

---

## 8. 建议修复清单

### Must-fix (提交前)

1. **N1**: Supplementary 标题改为 "Baseline-Normalized"（1 分钟修复）
2. **M5/N2**: 全文搜索替换 "Cohen's d" → "standardized effect size (SES)"，覆盖所有 4 个文档（10 分钟修复）

### Strongly recommended

3. **N3**: Repro Guide Section 3.2 将 brain 从 hybrid mode 列表中分出，单独说明 per-pair k_n
4. **N6**: Supplementary 添加 GPD 拟合参数表（shape, scale, 拟合优度）
5. **N4**: 统一 HK 基因匹配数报告（brain 1,115, human 1,129）

### Recommended

6. **N5**: Supplementary Note 3.3 合并两层 BH-FDR 描述
7. **N7**: Cover Letter 确认 Python ≥3.9 兼容性或更新最低版本要求
8. K=500 选择依据添加简短论证

---

## 9. 评分汇总

| 维度 | 分数 | 说明 |
|------|------|------|
| 算法正确性 | 8/10 | C1 EVT 修复正确；C3 方案统一；核心算法数学合理；循环依赖已识别 |
| 文档完整性 | 7/10 | M5 术语未统一；Supplementary 标题遗漏；参数表全面 |
| 代码质量 | 7/10 | 算法描述清晰；EVT 方法学论证充分；GPD 诊断信息不足 |
| 复现性 | 7.5/10 | 参数表完整且一致；brain k_n 描述有误；HK 匹配数不统一 |
| **综合** | **7.5/10** | **v22: 6.0 → v25: 7.5 (+1.5)** |

### 评分变动总结

v22 → v25 的 +1.5 分主要来自：
- **C1 修复 (+0.7)**: EVT/GPD 外推 + BH-FDR m=31,764，方法学正确，解决了脑分析核心结论的统计基础
- **C3 修复 (+0.3)**: Mouse k_n 方案统一，校准基线可信度恢复
- **C4/C5 修复 (+0.3)**: HK "constrained" 术语 + OPC 一致性验证
- **Major Issues 修复 (+0.2)**: M1-M20 大部分已处理

扣分项：
- M5 术语不统一 (-0.2)
- Supplementary 标题遗漏 (-0.1)
- Repro Guide brain k_n 描述矛盾 (-0.1)
- GPD 诊断信息不足 (-0.1)

---

## 10. 结论

v25 是一个显著改进的版本。**C1（BH-FDR）的修复是关键突破**——EVT/GPD 外推方法在方法学上正确，使脑分析的统计结论（16/30 Strong 信号显著， exclusively astrocyte + oligodendrocyte）建立在可靠的统计基础上。C3（Mouse k_n 方案）的修复消除了校准基线的文档矛盾。

剩余问题主要是文档一致性（M5 术语、Supplementary 标题、Repro Guide brain k_n 描述），不影响算法正确性。修复这些文档问题后，预计评分可达 8.0/10。

**准备度评估**: ~82%（v22: 67%, +15%）。修复 N1+N2 (M5) 后预计 85%+。

**v25 评分: 7.5/10** | v22: 6.0/10 | +1.5
