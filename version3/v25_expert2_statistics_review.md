# 专家2：统计学与数据分析审稿报告 — CKI v25

**Reviewer**: E2 — 统计学与数据分析专家
**Date**: 2026-08-01
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research
**Files reviewed**: CKI_NAR_Submission_v25 (20 files)
**Review baseline**: v22 score: 6.0/10

---

## 1. 总体评估

**v25 评分: 7.0/10** (v22: 6.0/10, +1.0)

v25 解决了 v22 审稿中标记的最高优先级统计学阻塞项 **C1（BH-FDR m值修正）**，并引入了 EVT（极值理论）外推方法来解决 P 值饱和问题。这是从 v22 到 v25 最重要的统计学改进。M5（Cohen's d → SES）和 M20（k_n 变异性）的修复方向正确但存在执行不完整的问题。M7（Bootstrap null 假说澄清）修复充分。

### 评分变化理由

| 改进项 | 评分影响 |
|--------|----------|
| C1 BH-FDR m=31,764 修正 + EVT 外推 | +0.8 |
| M7 Bootstrap null 假说澄清 | +0.2 |
| M20 k_n 变异性分析 (CV=97.35%) | +0.2 |
| M5 Cohen's d → SES (部分修复, 6处残留) | -0.1 |
| 非独立性声明统计不准确 | -0.1 |
| EVT GPD 拟合诊断缺失 | -0.1 |
| 校准 n=6 未扩充 | -0.0 (已标记) |

---

## 2. C1 修复验证：BH-FDR m=31,764 统计学准确性 ✅

### 2.1 核心问题回顾

v22 稿件报告 16/30 Strong 信号 P=9.99e-5, q=2.75e-4，但使用 m=30（仅 Strong 子集）计算 BH-FDR。标准 BH 程序要求 m = 总检验数（31,764），而非子集大小。

### 2.2 v25 修复内容

v25 明确将 BH-FDR 应用于全部 31,764 个 EVT-extrapolated P 值：

> "The EVT-extrapolated P-values for all 31,764 signals were then corrected using BH-FDR across the full set (m = 31,764); within the Strong tier, 16 of 30 candidates reached statistical significance at FDR < 0.05." (Manuscript P34)

### 2.3 统计学验证

我进行了数值模拟验证（m=31,764, α=0.05）：

**BH 阈值分析**：
- 11,541 个信号在经验 P 值下限（9.99×10⁻⁵）
- BH 阈值在 rank 11,541: α × 11,541 / 31,764 = **0.0182**
- 9.99×10⁻⁵ < 0.0182 → **全部 11,541 个下限信号通过 FDR < 0.05** ✓
- 模拟结果：11,562 个信号通过（稿件报告 11,556，一致）✓

**16 个 Strong 信号的 q 值**：
- 16 个 Strong 信号均在 11,541 个饱和信号中（EVT-extrapolated P < 1.0×10⁻⁴）
- 其 rank 约在 1–11,541 之间
- BH-adjusted q 值上界：9.99×10⁻⁵ × 31,764 / 11,541 = **2.75×10⁻⁴ < 0.05** ✓
- 模拟显示前 16 个 sorted q 值均 < 2×10⁻⁴ ✓

**EVT 公式验证**：
- P_EVT = (K/B) × S_GPD(u − observed_residual)
- K/B = 500/10,000 = 0.05（尾部概率）
- S_GPD 为 GPD 生存函数
- 当 observed_residual = u 时，S_GPD(0) = 1，P = K/B = 0.05（阈值处）✓
- 当 observed_residual → −∞ 时，S_GPD → 0，P → 0（更极端→更小 P 值）✓
- 这是标准的 Peaks-Over-Threshold (POT) 方法，公式正确 ✓

### 2.4 结论

**C1 修复在统计学上准确且充分。** m=31,764 正确描述了残差模型的 BH-FDR 程序。16/30 Strong 信号在 m=31,764 下确实通过 FDR < 0.05，脑分析核心结论的统计学基础现在成立。

---

## 3. M5 修复评估：Cohen's d → SES ⚠️ 部分修复

### 3.1 MANIFEST 声明

> "M5: 'Cohen's d' → 'standardized effect size (SES)' (all 4 docs)"

### 3.2 实际执行情况

| 文档 | SES 正确实例 | 残留 "Cohen's d" 实例 |
|------|-------------|---------------------|
| Manuscript | 4 (P25, P48, P138, 等) | **1** (P103 Limitations) |
| Supplementary | 2 (P64, P70) | **3** (P25 SN1.5, P31 Algorithm 1, P70 SN3.4) |
| Reproducibility Guide | **0** | **2** (P147, P168) |
| Cover Letter | 0 | 0 |
| **合计** | **6** | **6** |

### 3.3 具体问题

1. **Manuscript P103 (Limitations, 第七条)**: "Consequently, Cohen's d is reported as a descriptive measure of effect size rather than a parametric test statistic." — 应改为 SES。

2. **Supplementary P25 (SN 1.5)**: "Effect size: Cohen's d = (omega_obs - mean(omega_null))/sd(omega_null)" — 定义仍用旧名。

3. **Supplementary P31 (Algorithm 1)**: "Output: omega, P-value, Cohen's d, null distribution" — 算法伪代码输出仍用旧名。

4. **Supplementary P70 (SN 3.4)**: **矛盾句子** — 先定义 "standardized effect size, SES = (ω_obs − μ_null) / σ_null"，紧接着说 "Cohen's d should be interpreted as a non-parametric descriptive statistic"。同一句话中两个术语混用。

5. **Reproducibility Guide P147**: "Effect size: Cohen's d = (omega_obs - mean_null) / std_null" — 完全未更新。

6. **Reproducibility Guide P168**: "Cohen's d reported as descriptive measure" — 完全未更新。

### 3.4 结论

M5 修复**执行不完整**。MANIFEST 声称"all 4 docs"但复现指南完全未更新（0 个 SES 实例），补充材料有 3 处残留，正文 Limitations 有 1 处残留。统计学术语不一致可能引起审稿人困惑：SES 和 Cohen's d 在统计学中有不同含义（Cohen's d 基于两组均值差和合并标准差，而此处定义的 SES 基于观测值与置换 null 均值之差除以 null 标准差，更接近置换 z-score）。

**建议**: 全局替换所有 "Cohen's d" → "standardized effect size (SES)"，特别是复现指南和补充材料。

---

## 4. M7 修复评估：Bootstrap Null 假说澄清 ✅

### 4.1 修复内容

v25 在以下方面澄清了 bootstrap null 假说：

1. **明确 H0**: "the null hypothesis that the two cell populations are drawn from the same distribution" (SN 1.5, P25)

2. **单侧检验论证**: 新增 SN 3.10 (P82) 专门论证 one-sided test 的合理性：
   > "The one-sided formulation is appropriate because our hypothesis is directional: we test whether observed omega exceeds the null expectation (equivalent populations), not whether it differs in either direction."

3. **置换程序详述**: P25 明确描述了 cell label permutation 的完整流程。

4. **B=1,000 充分性论证**: P41 论证了 B=1,000 的最小可解析 P 值（9.99×10⁻⁴）低于各数据集 BH 阈值（brain: 5.0×10⁻³; human: 2.9×10⁻³; mouse: 3.3×10⁻³）。

### 4.2 统计学评价

M7 修复充分。null 假说定义清晰，单侧检验论证合理，B=1,000 的充分性有定量论证。

**次要术语问题**: 稿件使用 "bootstrap permutation test" 一词，但描述的程序是 permutation test（标签置换），不是 bootstrap（有放回重采样）。这是常见但不精确的术语混用。建议在 Methods 中注明 "permutation test (referred to as bootstrap permutation test throughout)"。

---

## 5. M20 修复评估：k_n 变异性分析 ✅

### 5.1 修复内容

v25 新增了 per-pair k_n 变异性分析（Phase C, C-M3）：

- **总体 CV = 97.35%**（mean=0.0141, median=0.0086）
- **Per-cell-type CV**: 37.6% (committed OPCs) 到 81.4% (oligodendrocytes)
- **Per-pair ω vs. global-kn ω**: Spearman ρ = −0.027 (P = 9.96×10⁻⁷)

### 5.2 统计学评价

M20 修复充分且分析深入。

- CV = 97.35% 表明 k_n 在不同脑区对之间变化巨大，支持 per-pair k_n 方案的必要性
- ρ = −0.027 表明 per-pair k_n 与 global k_n 产生的 ω 排名几乎不相关（接近 0，非负相关），确认两种方案产生实质性不同的排名
- P = 9.96×10⁻⁷ 确认相关性显著（虽然效应量极小，但这里关注的是 ρ 接近 0 而非远离 0）

**注意**: ρ = −0.027 的负号表示轻微负相关（per-pair k_n 更高 → ω 更低），但这在实践上意味着排名几乎不相关。稿件描述 "substantially different rankings" 是准确的。

---

## 6. Bootstrap 结果报告完整性检查

### 6.1 四个数据集的 Bootstrap 报告

| 数据集 | B | 测试层级 | m (BH) | 显著结果 | P 值报告 | 评估 |
|--------|---|---------|--------|---------|---------|------|
| Mouse | 1,000 | cell-type pair (15) + calibration (6) | 15 | 8/15 sig; cal. all P>0.05 | 定性 (P>0.05) | ⚠️ 缺具体 P 值 |
| Human | 1,000 | cell-type (17) | 17 | 15/16 sig | 定性 (P<0.001) | ⚠️ 缺具体 P 值 |
| TCGA | 1,000 | per-cancer descriptive | — | descriptive only | 无 P 值 (设计如此) | ✅ |
| Brain | 1,000 | cell-type (10) | 10 | 10/10 sig | 定性 (P<0.01) | ⚠️ 缺具体 P 值 |

### 6.2 残差模型 (B=10,000)

| 指标 | 值 | 报告位置 |
|------|---|---------|
| m | 31,764 | P34, P102 |
| 饱和信号数 | 11,541 (36.3%) | P34, P35 |
| FDR < 0.05 总数 | 11,556 | P67 (Supplementary) |
| Strong 候选 | 30 | P81 |
| Strong 显著 | 16/30 | P81, P102 |
| 非显著 Strong | 14/30 (P≥0.76, q=1.0) | P91, P93, P95 |

### 6.3 评估

**完整性**: 基本充分，但有改进空间。

**问题 1 — Bootstrap P 值未逐个报告**: 稿件在正文中未报告每个 bootstrap 检验的具体 P 值，仅使用定性描述（"all P > 0.05", "all P < 0.001"）。对于方法学论文，建议至少在补充表中列出所有 bootstrap 检验的 P 值、FDR q 值和 SES。

**问题 2 — "10/10 significant" 未在正文出现**: MANIFEST 报告 brain bootstrap "10/10 significant"，但正文中未明确声明。读者需从 Figure 6B 推断。建议在 Results 中补充 "all 10 brain cell types showed significant ω (bootstrap P < 0.01, BH-FDR < 0.05)"。

**问题 3 — "8/15" 和 "15/16" 未在正文出现**: Mouse 和 Human 的 bootstrap 显著比例仅在 MANIFEST 中报告，正文中未提及。建议补充。

---

## 7. P 值报告一致性与多重检验校正

### 7.1 P 值报告一致性 ✅

| 位置 | 检验类型 | P 值报告 | 一致性 |
|------|---------|---------|--------|
| Abstract | calibration | all P > 0.05 | ✓ |
| P52 | calibration | all P > 0.05, one-sided | ✓ |
| P58 | correlations | all P < 0.001 | ✓ |
| P61 | Mann-Whitney | P < 0.001 | ✓ |
| P66 | Jonckheere-Terpstra | P < 0.001 | ✓ |
| P66 | Kruskal-Wallis (PAM50) | P = 0.0002 | ✓ |
| P66 | Kruskal-Wallis (LUAD) | P = 0.017 | ✓ |
| P81 | residual model | P < 1.0×10⁻⁴ (sig), P ≥ 0.76 (n.s.) | ✓ |
| P91 | microglia | all P ≥ 0.76, q = 1.0 | ✓ |
| P93 | vascular | P = 1.0, q = 1.0 | ✓ |
| P95 | fibroblast | P = 1.0, q = 1.0 | ✓ |

**结论**: P 值报告在全文中一致。单侧（permutation）和双侧（non-parametric）检验区分清晰。

### 7.2 多重检验校正描述 ✅

v25 对 BH-FDR 的描述全面且一致：

1. **Cell-type bootstrap**: m = 细胞类型数（brain: 10, human: 17, mouse: 15）— P41 ✓
2. **残差模型**: m = 31,764 (EVT-extrapolated) — P34, P102 ✓
3. **跨数据集不可比性**: 新增 Limitation #13 (P103) ✓
4. **统计约定段**: P138 统一描述所有 P 值和 FDR 程序 ✓

---

## 8. 新发现问题

### N1-S (New, Statistics) — 非独立性声明统计不准确 🟡 中等

**位置**: Manuscript P34

**问题**: 稿件声称：
> "Importantly, the per-signal tests are not independent (the same cell type or region pair appears in multiple comparisons), and the B = 10,000 permutation budget limits the minimum resolvable P-value; both caveats are addressed by the tier-level FDR strategy which restricts formal inference to the 30 predefined Strong candidates rather than the full 31,764 search space."

**统计问题**: "tier-level FDR strategy" 并不解决非独立性问题。BH-FDR 已经应用于全部 31,7644 个 P 值（而非仅 30 个），后续筛选到 30 个 Strong 候选是结果解读层面的过滤，不是统计校正层面的解决方案。

**正确表述**: BH-FDR 在正回归依赖（PRDS）条件下是保守的（Benjamini-Yekutieli 2001）。如果脑区对之间的依赖是正的（同一细胞类型在不同区域对中的残差倾向同向变化），则 BH-FDR 的 FDR 控制仍然有效。稿件应引用此性质或使用 BY（Benjamini-Yekutieli）程序作为保守上限。

**建议**: 修改为 "The per-signal tests are not independent; however, BH-FDR remains valid under positive regression dependence on a subset (PRDS; Benjamini and Yekutieli, 2001), which is expected here because signals sharing cell types or regions tend to be positively correlated. As a conservative check, the tier-level analysis restricts biological interpretation to the 30 predefined Strong candidates."

### N2-S — EVT GPD 拟合诊断缺失 🟡 中等

**位置**: Manuscript P35, Supplementary P68

**问题**: 稿件声称 "All 11,541 saturated signals were successfully resolved by GPD fitting; no signals required fallback to the empirical floor value" 和 "11,541/11,541 GPD fits successful"。但未报告：
- GPD 参数估计（形状参数 ξ、尺度参数 σ）的分布
- 拟合优度统计量（如 Anderson-Darling, Cramér-von Mises）
- K=500 的敏感性分析
- 形状参数 ξ 的置信区间（ξ > 0 表示重尾，ξ < 0 表示有界尾）

**统计关注**: 11,541 次独立 GPD 拟合中，部分可能存在拟合不佳。标准 EVT 实践要求报告拟合诊断。形状参数 ξ 的符号和大小直接影响外推 P 值的数量级。

**建议**: 在补充材料中添加 GPD 拟合诊断表或图（ξ 分布直方图、Q-Q 图抽检、K 敏感性分析）。

### N3-S — "Two-level BH-FDR" 描述框架混淆 🟢 轻微

**位置**: Manuscript P34

**问题**: 稿件描述 BH-FDR "applied at two levels"：
1. First level: empirical P-values (deemed "uninformative")
2. Second level: EVT-extrapolated P-values (primary analysis)

这实际上是**一次** BH-FDR 应用于改进后的 P 值，不是两个独立的校正层级。"Two levels" 的描述容易让审稿人误以为进行了两次独立的 FDR 校正。

**建议**: 修改为 "BH-FDR was first attempted with empirical P-values; however, 36.3% of signals reached the empirical floor, preventing discrimination among highly significant signals. We therefore applied EVT extrapolation to resolve the saturated P-values, and then applied BH-FDR to the combined EVT-empirical P-values (m = 31,764)."

### N4-S — 经验 P 值下限"FDR uninformative"描述不精确 🟢 轻微

**位置**: Manuscript P34

**问题**: 稿件声称 empirical floor "makes per-signal FDR uninformative because the empirical floor precludes proper FDR control"。

**统计问题**: BH-FDR 在经验 P 值下限处仍然有效——所有 11,541 个下限信号都通过 FDR < 0.05（因为 9.99×10⁻⁵ < α×11,541/31,764 = 0.0182）。问题不是 FDR 控制"失败"，而是 P 值缺乏**区分度**（所有饱和信号共享同一 P 值，无法排序）。

**建议**: 改为 "making per-signal FDR non-discriminative, as all 11,541 saturated signals share the same empirical P-value and cannot be ranked."

### N5-S — 校准样本量 n=6 未扩充 🟡 中等（v22 遗留）

**位置**: Manuscript P52, P103 (Limitation #10)

**问题**: v22 标记的 M1（校准 n=6 不足）未修复。v25 增加了 TOST 建议和 CV≈60% 的报告，但未扩充样本量。

**进展**: P52 现在报告了 "range 1.59–12.16, CV ≈ 60%" 和 "formal equivalence testing (e.g., TOST) with a larger calibration sample would provide stronger statistical evidence"。这是正面进展——至少承认了局限性。

**建议**: 至少使用全部 4 个数据集的 split-half 对照作为校准池（Tabula Muris + Tabula Sapiens + TCGA + Brain 的等价群体对照），将 n 从 6 扩充到 ≥20。

### N6-S — 36.4% 发现率的实际意义需讨论 🟢 轻微

**位置**: Supplementary P68

**问题**: 11,556/31,764 (36.4%) 的脑区对通过 FDR < 0.05。这一发现率异常高（典型基因组学应用中通常 <10%）。高发现率可能反映了：
- 统计检验过度有力（每组 ≥20 核，通常数百）
- 零假设（"细胞类型在脑区间无功能分歧"）对大多数细胞类型都不成立

**建议**: 在讨论中简要说明 36.4% 的发现率反映了零假设对大多数脑区比较不成立，因此显著性检验的作用主要是排除随机变异，而非发现新生物学。实际的生物学发现依赖于残差模型的效应量筛选（30 Strong 候选）。

---

## 9. 统计学方法总评

### 9.1 优点

1. **C1 修复正确且充分**: BH-FDR m=31,764 的使用在统计学上准确，EVT 外推方法标准且公式正确
2. **置换检验框架健全**: cell label permutation 构建零分布是标准方法，+1 伪计数避免 P=0
3. **单侧检验论证合理**: 方向性假说论证充分
4. **多重检验校正全面**: BH-FDR 在各数据集内分别应用，跨数据集不可比性已标注
5. **EVT 方法选择恰当**: POT + GPD 是处理置换检验 P 值饱和的标准方法
6. **k_n 变异性分析深入**: CV 和 ρ 分析充分支持 per-pair 方案
7. **非参数检验使用正确**: Mann-Whitney, Kruskal-Wallis, Jonckheere-Terpstra 配对合适

### 9.2 不足

1. **M5 修复不完整**: 6 处 "Cohen's d" 残留，复现指南完全未更新
2. **EVT 诊断缺失**: 11,541 次 GPD 拟合无诊断报告
3. **非独立性论述不准确**: "tier-level FDR" 不解决依赖性
4. **校准 n=6 未扩充**: 虽有局限性声明但未实际改进
5. **Bootstrap P 值未逐个报告**: 仅定性描述

---

## 10. 评分

### 10.1 评分分解

| 维度 | 分数 | 理由 |
|------|------|------|
| BH-FDR 正确性 (C1) | 8.5/10 | m=31,764 正确，EVT 公式准确；非独立性论述和诊断有改进空间 |
| 置换检验设计 (M7) | 8.0/10 | 框架健全，B=1,000 充分性有论证；术语不精确 |
| 效应量报告 (M5) | 6.0/10 | 正文大部分已改 SES，但 6 处残留影响一致性 |
| k_n 变异性 (M20) | 9.0/10 | 分析充分，数据支持结论 |
| Bootstrap 报告 | 7.0/10 | 基本完整但缺逐个 P 值 |
| P 值一致性 | 8.5/10 | 全文一致，单/双侧区分清晰 |
| 多重检验校正描述 | 8.0/10 | 全面但 "two-level" 描述混淆 |
| 校准充分性 | 5.5/10 | n=6 不足，虽有声明但未改进 |
| **加权总分** | **7.0/10** | |

### 10.2 与 v22 对比

| 维度 | v22 | v25 | Δ |
|------|-----|-----|---|
| C1 BH-FDR | 4.0 (未修复) | 8.5 | +4.5 |
| M5 Cohen's d | 5.0 (未修复) | 6.0 | +1.0 |
| M7 Bootstrap null | 6.0 (未澄清) | 8.0 | +2.0 |
| M20 k_n 变异性 | 5.0 (未分析) | 9.0 | +4.0 |
| Bootstrap 报告 | 6.5 | 7.0 | +0.5 |
| 校准 n=6 | 5.5 | 5.5 | 0 |
| **总分** | **6.0** | **7.0** | **+1.0** |

### 10.3 达标评估

| NAR 统计学要求 | 达标? | 说明 |
|---------------|-------|------|
| 多重检验校正正确 | ✅ | C1 修复后 BH-FDR m 值准确 |
| P 值报告规范 | ⚠️ | 定性描述充分，缺逐个 P 值表 |
| 效应量报告 | ⚠️ | SES 已引入但残留 Cohen's d |
| 置换检验设计 | ✅ | 标准方法，B 充分 |
| EVT 方法 | ✅ | 标准方法，公式正确 |
| 非独立性处理 | ⚠️ | 承认但论述不准确 |
| 拟合诊断 | ❌ | GPD 拟合无诊断 |
| 校准充分性 | ⚠️ | n=6 不足，已声明但未改进 |

---

## 11. 建议

### 阻塞项（投稿前必须修复）

无。C1 修复后已无统计学层面的硬性阻塞项。

### 强烈建议（1-2 天）

1. **M5 全局清理**: 全局替换 6 处残留 "Cohen's d" → "SES"（复现指南 2 处、补充材料 3 处、正文 Limitations 1 处）
2. **非独立性论述修正**: 将 "tier-level FDR strategy addresses non-independence" 改为引用 BH 在 PRDS 下的有效性
3. **EVT 拟合诊断**: 在补充材料中添加 GPD 参数分布和 Q-Q 图抽检

### 建议改进（时间允许）

4. **Bootstrap P 值表**: 在补充材料中添加每个 bootstrap 检验的 P 值、q 值、SES 表
5. **"Two-level" 描述简化**: 改为单次 BH-FDR 应用于 EVT-extrapolated P 值
6. **校准扩充**: 使用多数据集 split-half 增加校准 n
7. **K 敏感性**: EVT K=500 的敏感性分析

---

## 12. 总结

v25 在统计学层面实现了关键突破：C1（BH-FDR m 值）的修复使脑分析核心结论的统计学基础从"不成立"变为"成立"。EVT 外推方法的引入是处理置换检验 P 值饱和的标准且正确的方法。M7 和 M20 的修复方向正确且分析充分。

主要残留问题是 M5（Cohen's d → SES）的执行不完整——6 处残留散布在 3 个文档中，复现指南完全未更新。非独立性论述的统计不准确和 EVT 诊断缺失是需要修正的中等问题。

**v25 评分: 7.0/10** (v22: 6.0/10, +1.0)

修复上述建议项后预计可达 7.5-8.0/10。

---

*审稿人: E2 — 统计学与数据分析*
*审稿日期: 2026-08-01*
