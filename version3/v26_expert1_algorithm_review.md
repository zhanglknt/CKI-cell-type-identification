# CKI v26 算法与方法学审稿报告

**审稿人**: E1 (算法与方法学)
**审稿日期**: 2026-08-02
**评分**: 8.0/10

## 1. 总体评价

v26 在 v25 (7.5/10) 基础上进行了 P0+P1 修复，算法核心数学正确、方法学框架自洽。CKI 的核心计算链（softmax 归一化 → JS divergence → ω = k_f/k_n 比值）数学推导无误，permutation test 实现规范，limitation 透明度高。v25→v26 的 N1-N4/N6/N8/N9 修复基本到位，但发现一个 Major 级别的 MANIFEST-正文不一致问题（EVT/FDR 方案描述矛盾），以及图形摘要中残留的术语问题。算法本身无致命缺陷，ω 的可解释性框架在 heuristic 层面成立。

**评分理由**: 8.0/10 反映：(1) 核心数学正确无 Critical；(2) v26 修复提升了文档一致性；(3) MANIFEST 与正文关于 EVT/FDR 方案的矛盾是主要扣分项；(4) per-pair k_f 的循环依赖问题虽已 acknowledge 但仍是根本性方法学隐忧；(5) 校准因子跨方案可迁移性未验证。

## 2. 逐项审查

### 2.1 CKI 数学推导正确性 ✅

**k_n/k_f 定义** (Manuscript L22; Supp SN 1.2-1.3):
- k_n = JS(softmax(μ_A[H]), softmax(μ_B[H])) — HK 基因子集上的 JS divergence，正确
- k_f = JS(softmax(μ_A[I]), softmax(μ_B[I])) — identity 基因子集上的 JS divergence，正确
- HK 基因从 I 中显式排除，保证 k_n/k_f 独立性 — 正确

**JS divergence** (Supp SN 1.1):
- JS(p,q) = ½ D(p||m) + ½ D(q||m)，m = ½(p+q) — 标准公式，正确
- Base-2 对数，range [0,1] — 正确
- ω = k_f/k_n 中对数底数抵消（Supp SN 3.11: "the base does not affect omega since it cancels in the ratio"）— 数学正确

**Softmax 归一化** (Manuscript L22; Supp SN 1.2):
- p_i = exp(x_i) / Σ exp(x_j) — 正确
- 将表达向量转为概率分布，保证非负且归一化 — 合理
- log1p 预变换缓解了 softmax 对高表达基因的饱和敏感性 — 合理

**k_n floor** (Supp SN 1.1; Algorithm 1 Line 7):
- k_n < 1e-4 时设为 1e-4，防止 ω 因近零分母而爆炸 — 实用合理
- **Observation**: 1e-4 的具体值缺乏理论论证或敏感性分析。建议补充 floor 值对 ω 分布影响的敏感性测试（如 1e-3 vs 1e-4 vs 1e-5）。

**ω 比值计算**:
- ω = k_f/k_n — 正确
- ω_cal = ω/6.67 — 经验校准，合理

### 2.2 基因集选择策略 ✅

**HK 基因** (Manuscript L21; Supp SN 1.2; Repro Guide §3.1):
- HRT Atlas v1.0 参考（1,130 human-mouse conserved HK genes）用于所有 reported analyses — 一致
- auto-detect（detection rate > 0.9, CV < 30th percentile）可用但未使用 — 透明声明
- 敏感性分析：最低 10% variance 基因作为替代 constrained set，ω 相关性 r > 0.95 — 良好

**HVG 选择** (Manuscript L22, L28; Supp SN 1.3; Repro Guide §3.2):
- 两种方案清晰区分：
  - Global HVG 2,000（Seurat flavor）：仅用于 Tabula Muris full pairwise matrix（Fig. 2, 703 pairs）
  - Per-pair top-200 DE genes（|μ_A - μ_B| 排序，排除 HK）：用于 mouse pilot、human、TCGA、brain
- 参数扫描（Supp Table 1）验证 N_HVG ∈ {50, 100, 200, 500, 1000, 2000}，global 方案 N=2000 最优，per-pair 方案 N=200 — 有据可依

**HK/HVG 独立性**:
- HK 基因从 HVG/DE 基因中显式排除 — 正确

### 2.3 ω 比值解释框架 ✅（heuristic 层面）

**Ka/Ks 启发的局限性** (Manuscript L16, L97, L99; Supp SN 1.4):
- 明确声明 "CKI is a heuristic index rather than a formal measure of selection" — 透明
- 列出三个关键差异：(1) DNA 序列 vs 连续表达向量；(2) 理论中性参考 vs 经验 HK 基因；(3) 显式进化模型 vs 经验 bootstrap — 全面
- "CKI does not share Ka/Ks's formal mathematical properties (notably the shared mutation rate that cancels in the ratio)" — 准确
- ω < 1, ω ≈ 1, ω > 1 作为 operational thresholds 而非 selection regime claims — 谨慎

**Empirical calibration** (Manuscript L54; Supp SN 3.5):
- ω_cal = ω/6.67，rescale 使 equivalent populations → ω_cal ≈ 1.0 — 合理
- Mouse controls → ω_cal = 1.00, brain global → 1.20, astrocytes → 2.15, Bergmann glia → 0.36 — 可解释
- **Observation**: 校准因子 6.67 来自 mouse split-half（n=6, global HVG for k_f），但应用于 human/TCGA/brain（per-pair DE for k_f）。Manuscript Limitation #12 已 acknowledge: "The calibration factor has not been independently validated for the per-pair DE scheme"。这是合理的方法学透明性，但跨方案校准因子的可迁移性仍是未验证的假设。

**Ratio framework 的数学基础**:
- ω = k_f/k_n 作为 heuristic ratio，分子分母使用相同 metric（JS divergence）和相同 normalization（softmax），internal consistency 成立
- 但缺乏 formal mathematical guarantee（如 Ka/Ks 中 mutation rate cancellation）— 已透明声明

### 2.4 混合方案一致性 ✅

**Global k_n vs per-pair k_n** (Manuscript L56; Supp SN 3.7; Repro Guide §3.2):
- Human/TCGA: global k_n（shared HK set）+ per-pair k_f（top-200 DE）
- Brain: per-pair k_n + per-pair k_f
- Brain per-pair k_n 的合理性：CV = 97.35%, per-pair ω vs global-k_n ω Spearman ρ = -0.027（P = 9.96e-7）— 数据支撑充分

**一致性论证** (Manuscript L56):
- "since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies" — 论证合理
- Supp SN 3.7: "this justifies the per-pair k_n approach used for the brain analysis and highlights a limitation of the hybrid scheme used for human/TCGA data" — 透明

**Observation**: Human/TCGA 使用 global k_n 意味着 ω 实际上退化为 k_f 的 scaled ranking（因 k_n 对所有 pair 是常数）。这不影响 pair-level 比较，但限制了跨 pair 绝对 ω 值的可比性。Manuscript 建议 "compare ω ranks rather than absolute values across datasets" — 合理建议。

### 2.5 Dimensionality invariance 验证 ✅（有 acknowledged limitation）

**JS divergence 维度不变性** (Manuscript L24; Supp SN 3.6):
- Simulation: 2,000 Dirichlet pairs, dimensions 50→5,000
- Mean JS: 0.155-0.159, ratio = 1.001（d=1,130 vs d=2,000）— 充分验证
- 结论：ω = 6.67 的 inflation 来自 HVG selection bias 而非维度不匹配 — 正确

**Acknowledged limitation** (Supp SN 3.6):
- "this simulation addresses dimensionality per se (random probability vectors of different lengths) but does not simulate the variance-based gene selection mechanism that generates the ω inflation"
- "A more complete validation would test whether the inflation magnitude scales with the stringency of variance filtering rather than gene count"
- 这是诚实的自我评估。建议未来补充 variance-filtered Dirichlet simulation。

### 2.6 算法扩展性讨论 ✅

**Pathway embedding/regulon activity 加权方案** (Manuscript L49; Supp SN 1.3; Supp Table 1):
- 扩展配置：k_f = w1*JS(HVG) + w2*JS(pathway) + w3*JS(macro)
- Parameter sweep: identity-only（w1=1.0, w2=w3=0.0）最优（AUC = 0.847, n=703 mouse pairs）
- 结论："CKI does not require external pathway databases to produce biologically meaningful results" — 有数据支撑
- 透明声明扩展配置存在但未被使用 — 良好

### 2.7 Permutation test 实现 ✅

**Bootstrap permutation test** (Manuscript L26, L41; Supp SN 1.5; Algorithm 1):
- H0: 两个群体来自相同分布
- B = 1,000（所有4个数据集），cell labels 随机置换
- P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) — one-sided, +1 pseudocount 避免 P=0 — 正确
- SES = (ω_obs - μ_null)/σ_null — 正确
- BH-FDR within each dataset — 正确（where applicable）

**One-sided test justification** (Supp SN 3.10):
- "our hypothesis is directional: we test whether observed omega exceeds the null expectation" — 合理
- 对于 Strong migration candidates（anomalously low ω），使用相反方向 P = (count(null_residual ≤ observed) + 1)/(B+1) — 正确

**Bootstrap CI** (Manuscript L42; Supp SN 3.2):
- B = 10,000 pair-level resampling, 2.5th/97.5th percentiles — 正确
- 明确区分 CI（precision of point estimate）与 permutation test（hypothesis testing）— 良好

### 2.8 Multiplicative residual model ✅

**模型定义** (Manuscript L35, L80; Repro Guide §4.4):
- expected_ω = μ_ct × μ_pair / μ_grand — 乘法 ANOVA-like 分解，合理
- residual = observed / expected — 正确
- 三级置信度：Strong (residual < 0.3, ω < 15), Moderate (< 0.5, ω < 25), Weak (< 0.75, ω < 35) — 实用

**Permutation null** (Manuscript L35; Supp SN 3.3):
- B = 10,000, cell type labels shuffled within region pairs
- P = (count(null_residual ≤ observed) + 1)/(B + 1) — 正确（低尾检验）
- 36.3% signals 达到 P-value floor (9.99e-5) — 诚实报告

## 3. 发现的问题

### Critical: 无

### Major (1项)

| ID | 描述 | 位置 | 影响 |
|----|------|------|------|
| **A-M1** | **MANIFEST 与正文关于 EVT/FDR 方案的矛盾**。MANIFEST 声称 "C1: BH-FDR q-value description (EVT, m=31,764)" 和 "30 Strong candidates, BH-FDR across 31,764 EVT-extrapolated P-values, 16/30 significant (FDR<0.05)"。但正文（Manuscript L35, L81, L104）和 Supplementary SN 3.3 明确声明 "formal Benjamini-Hochberg FDR correction is not applicable" 和 "We therefore report unadjusted permutation P-values and interpret significance descriptively"。正文中无任何 EVT/GPD 内容。这表明 v26 实际上从 v25 的 EVT 外推方案改为了描述性未校正 P 值方案，但 MANIFEST 仍声称使用 EVT。 | MANIFEST_v26.txt L23, L42 vs Manuscript L35/L81/L104, Supp SN 3.3 | 方法论描述不一致。v25 专家团批准了 EVT 方案，v26 改为描述性方案但未在 MANIFEST 中反映。实际正文的描述性方案方法学上合理（更保守、更透明），但 MANIFEST 误导性。 |

### Minor (3项)

| ID | 描述 | 位置 | 建议 |
|----|------|------|------|
| **A-m1** | **N7 修复声称但未实际实现**。MANIFEST 声称 "N7 — Supplementary SN 3.3: EVT GPD fit diagnostics reference added"，但搜索全部文本文件无 GPD/EVT/shape/scale/goodness-of-fit 内容。实际上 v26 移除了 EVT 方案（改为描述性 P 值），使 N7 问题 moot，但 MANIFEST 仍声称添加了 GPD 诊断。 | MANIFEST_v26.txt L15 vs Supp SN 3.3 | 更新 MANIFEST 描述以反映实际方案变更（EVT → descriptive unadjusted P-values），或在 Supplementary 中补充 EVT 方案变更的说明。 |
| **A-m2** | **图形摘要 SVG 残留 "selective" 术语**。Graphical abstract SVG 第 1283 行: "Quantifying selective transcriptomic remodeling from expression distributions"。N1 修复了 Supplementary 标题，C6 修复了主稿件标题，但图形摘要仍使用旧术语 "selective"，与标题 "Baseline-Normalized" 不一致。 | CKI_graphical_abstract.svg L1283 | 将图形摘要中 "selective" → "baseline-normalized" 以保持一致性。 |
| **A-m3** | **图形摘要 SVG 残留 "neutral" 术语**。Graphical abstract SVG 第 5624 行: "ω distinguishes functional remodeling from neutral transcriptomic drift"。虽然这是概念性描述，但在 CKI 上下文中使用 "neutral" 与 N4 修复（CKI 上下文 → "constrained baseline"）的精神不一致。 | CKI_graphical_abstract.svg L5624 | 考虑改为 "ω distinguishes functional remodeling from constrained baseline drift" 或保留（因这里是概念性描述而非直接描述 HK 基因）。 |

### Observation (4项，不阻塞)

| ID | 描述 | 位置 | 说明 |
|----|------|------|------|
| **A-O1** | **Per-pair k_f 的循环依赖**。top-200 DE genes 由 |μ_A - μ_B| 排序选择，即定义 "functional divergence" 的基因恰是两组间表达差异最大的基因。Permutation test 在 null 下保持了这一选择过程，但 k_f 量级缺乏独立外部验证，应视为 functional divergence 的 upper bound。Manuscript Limitation 已 acknowledge 此问题。 | Manuscript L103 (Limitation) | 方法论透明度良好，但循环依赖是 per-pair DE 方案的固有局限。Global HVG 方案不存在此问题。 |
| **A-O2** | **校准因子跨方案可迁移性未验证**。ω_cal = ω/6.67 的 6.67 来自 mouse split-half（global HVG for k_f），但应用于 human/TCGA/brain（per-pair DE for k_f）。不同 k_f 选择策略可能产生不同的 inflation 因子。Manuscript Limitation #12 已 acknowledge。 | Manuscript L104 (Limitation #12) | 建议未来在 per-pair DE 方案下进行 matched calibration experiment。 |
| **A-O3** | **k_n floor (1e-4) 缺乏理论论证**。1e-4 作为 k_n 下限是实用选择，但未提供敏感性分析（如 floor 值对 ω 分布和 significance 判断的影响）。 | Supp SN 1.1; Algorithm 1 L7; Repro Guide §6 | 建议补充 floor 值敏感性测试。 |
| **A-O4** | **Softmax 无 temperature 参数讨论**。对于动态范围较大的表达向量（即使 log1p 后），softmax 可能被少数高表达基因主导。虽然 log1p 变换部分缓解了此问题，但未讨论 softmax temperature 对结果稳健性的影响。 | Supp SN 1.2, SN 3.11 | 建议在 Supplementary 中简要讨论 softmax temperature 的潜在影响。 |

## 4. v25→v26 修复验证

| 修复 ID | 描述 | 验证结果 | 说明 |
|---------|------|:--------:|------|
| **N1** | Supplementary 标题 "Selective" → "Baseline-Normalized" | ✅ | Supplementary L2: "CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling" — 已修复 |
| **N2** | 全局 "Cohen's d" → "SES" | ✅ | 搜索全部 .txt 文件，"Cohen" 仅出现在 MANIFEST 描述中（说明修复内容），正文/Supp/Repro Guide/Cover Letter 均无残留 |
| **N3** | Table 1 "99 cell types, 4,851 pairs" → "102 cell types, 5,151 pairs" | ✅ | Table1-2_fulltext.txt L3: "102 cell types, 5,151 pairs"；Manuscript L59: "102 cell types, 5,151 pairs" — 一致 |
| **N4** | "neutral" → "constrained baseline"（CKI 上下文） | ✅（正文） ⚠️（图形摘要） | 正文和 Figure legends 中的 "neutral" 仅出现在 Ka/Ks 概念性上下文中（L15 "neutral drift", L99 "neutral drift", L119 "neutral baseline" 指 Ka/Ks），CKI 上下文已改为 "constrained baseline"。但图形摘要 SVG 残留 "neutral"（A-m3）。 |
| **N6** | Repro Guide brain k_n 描述修正 | ✅ | Repro Guide §3.2: "The brain atlas analysis also uses per-pair top-200 DE genes for k_f, but unlike the other datasets, uses per-pair k_n (computed separately for each cell-type/region pair from the same HK gene set) rather than a global k_n; this is because brain k_n exhibits substantial cross-pair variability (CV = 97.35%) that is poorly captured by a global mean." — 准确清晰 |
| **N7** | Supplementary EVT GPD 拟合诊断补充 | ❌ 未实现 | MANIFEST 声称已添加，但 Supp SN 3.3 中无任何 GPD/EVT/shape/scale/GOF 内容。实际方案从 EVT 外推改为描述性未校正 P 值，使 N7 问题 moot，但 MANIFEST 描述不准确。（见 A-M1, A-m1） |
| **N8** | Limitations 编号重复修复 | ✅ | Manuscript L104: "Eleventh, the multiplicative residual model..." — 编号正确 |
| **N9** | Brain PMI 讨论扩展 | ✅ | Manuscript L77, L76 扩展了脑区异质性讨论（vascular cells/fibroblasts 的微环境一致性、astrocytes 的区域特化） |

## 5. 建议

### 投稿前必须修复 (P0)

1. **A-M1: 更新 MANIFEST 以反映实际 FDR 方案**。MANIFEST 中的 "BH-FDR across 31,764 EVT-extrapolated P-values, 16/30 significant (FDR<0.05)" 应改为 "descriptive unadjusted permutation P-values (B=10,000), 16/30 Strong candidates reached P-value floor (P=9.99e-5), FDR not applicable due to floor saturation"。确保 MANIFEST 与正文一致。（~10 min）

2. **A-m1: 在 MANIFEST 或 Supplementary 中记录方案变更**。明确说明 v25 的 EVT 外推方案在 v26 中被替换为描述性未校正 P 值方案，以及替换原因（P-value floor saturation 导致 EVT 外推不必要/不可靠）。（~15 min）

### 强烈建议 (P1)

3. **A-m2: 更新图形摘要 SVG 中的 "selective"** → "baseline-normalized"。（~5 min）

4. **A-m3: 评估图形摘要 SVG 中 "neutral" 是否需要修改**。建议改为 "constrained baseline drift" 以完全符合 N4 精神。（~5 min）

### 建议改进 (P2)

5. **A-O3: 补充 k_n floor 敏感性分析**。测试 1e-3 / 1e-4 / 1e-5 对 ω 分布和 significance 判断的影响，在 Supplementary 中报告。（~2h）

6. **A-O1: 补充 per-pair k_f 循环依赖的定量评估**。虽然已 acknowledge，但可考虑补充一个简单的验证：比较 per-pair DE k_f 与 random gene set k_f 的分布差异，量化循环依赖对 k_f inflation 的贡献。（~3h，不阻塞投稿）

7. **A-O2: 在 per-pair DE 方案下进行 matched calibration**。用 human/brain 数据做 split-half 实验，直接估计 per-pair DE 方案的校准因子，验证 6.67 的可迁移性。（~4h，不阻塞投稿）

---

## 评分明细

| 维度 | 分数 (0-10) | 说明 |
|------|:-----------:|------|
| 核心数学正确性 | 9.0 | softmax → JS → ω 推导无误，permutation test 规范 |
| 基因集选择策略 | 8.5 | HK/HVG 独立、参数有据，per-pair DE 循环依赖已 acknowledge |
| ω 解释框架 | 8.0 | Ka/Ks 类比局限性透明，calibration 合理但跨方案未验证 |
| 混合方案一致性 | 8.0 | global/per-pair k_n 取舍有数据支撑，human/TCGA 的 global k_n 局限已 acknowledge |
| 统计推断实现 | 7.5 | Permutation test 正确，但 MANIFEST-正文 EVT/FDR 矛盾扣分 |
| 维度不变性验证 | 8.0 | Dirichlet simulation 充分，variance selection limitation 已 acknowledge |
| v25→v26 修复执行 | 7.5 | N1-N4/N6/N8/N9 到位，N7 声称未实现，MANIFEST 不一致 |
| 文档一致性 | 7.0 | 图形摘要残留 "selective"/"neutral"，MANIFEST 矛盾 |
| **加权综合** | **8.0** | 算法核心稳健，扣分主要来自文档不一致而非数学错误 |

---

*审稿人注*: v26 的算法核心（CKI computation chain）在数学上正确且实现规范。主要扣分项是文档层面的一致性问题（MANIFEST-正文矛盾、图形摘要残留），而非算法本身的方法学缺陷。建议修复 P0（MANIFEST 更新）后投稿。P1 的图形摘要修复可同步进行。算法层面的 Observation（循环依赖、校准因子迁移性、k_n floor 论证）已在 manuscript limitations 中透明声明，不阻塞投稿但建议在未来版本中补充验证。
