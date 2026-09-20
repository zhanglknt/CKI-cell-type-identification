# CKI v32 独立审稿 — E2: 定量生物学与统计

**审稿日期**: 2026-08-02
**评分**: 8.4/10 (v28: 7.6/10, Δ: +0.8)

## 1. 核心发现概要

v32 在统计维度上实现了显著改进。校准因子 95% Bootstrap CI [4.12, 9.33] 在全文 5 处一致报告，Limitations #17 全面重写并量化了跨方案转移的不确定性范围（1.62×/0.71× 偏移因子）；SES 被明确定义为非参数描述性统计量并与 Cohen's d 显式区分；脑区残差模型的描述性 P 值方案（"No formal FDR"）在正文中正确实施；Bootstrap P 值公式 P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) 在全部 6 处文档位置完全一致。

v28 标记的 3 项 P0/P1 级统计问题（P0-2 MANIFEST FDR 声明、P0-3 校准因子 CI、P1-5 SES 非参数替代、P1-6 k_n floor 量化）中，P0-3 和 P1-5 已彻底解决，P0-2 和 P1-6 存在残余 Minor 问题。E2-1~E2-6 全部 6 项 P2 级建议已落实。

剩余问题均为 Minor 级别：校准因子 CV 值存在事实性错误（60% vs 实际 52%）、MANIFEST 残留 "FDR-significant" 术语矛盾、摘要 "statistically significant" 措辞与正文 "descriptive evidence" 不一致、k_n floor 触发比例量化不完整、单侧检验无法检测功能约束方向。

**Critical: 0, Major: 0, Minor: 6**

## 2. v28→v32 修复验证

### 2.1 P0-2: MANIFEST EVT/FDR 声明统一 — 部分修复 (Minor 残留)

v28 问题：MANIFEST 声称 "16/30 significant (FDR<0.05)"，正文明确 "FDR correction is not applicable"。

v32 状态：
- MANIFEST 不再提及 EVT/GPD 外推方法 ✅
- 但 MANIFEST 第 72 行仍使用 "16/30 **FDR-significant** descriptive" — 这一短语内部矛盾。"FDR-significant" 与 "descriptive" 不应并列使用，因为正文明确声明 "formal FDR correction is not applicable"（手稿第 81、100 行）。
- 建议改为 "16/30 P-floor-reaching (descriptive), 14/30 non-significant" 或 "16/30 descriptively significant (P-floor), 14/30 non-significant"。

**评估**：正文方案正确，MANIFEST 术语残留不一致。Minor。

### 2.2 P0-3: 校准因子 ω=6.67, 95% Bootstrap CI [4.12, 9.33] — 基本修复 (CV 错误残留)

v28 问题：校准因子 n=6、CV≈60%，跨方案转移未验证，无不确定性传播。

v32 改进：
- 95% Bootstrap CI [4.12, 9.33] 在 5 处一致报告：Abstract（第 11 行）、Introduction（第 18 行）、Methods/Statistical reporting（第 42 行）、Results（第 52 行）、Discussion（第 93 行）✅
- B=10,000 resamples of 6 control ω values，方法学描述清晰 ✅
- Limitations #17（第 100 行）全面重写：解释 global HVG vs. per-pair DE scheme 差异、量化 CI 范围影响因子偏移（1.62×/0.71×）、论证 rank-based 解释鲁棒性、提供 calibrate_omega 函数 ✅
- 影响因子计算验证：6.67/4.12 = 1.62× ✅；6.67/9.33 = 0.71× ✅

**但存在 CV 事实性错误**：
- 手稿第 52 行："CV ≈ 60%"
- 基于 6 个 control 值 [12.16, 6.57, 6.34, 5.22, 8.15, 1.59] 的实际计算：Mean = 6.67, Sample SD = 3.474, **CV = 52.1%**
- v28 综合报告（第 162 行）已正确标注 "CV≈52%"，但 v32 手稿未修正此错误
- 此错误影响校准因子精度的定性判断：CV≈52% 比 CV≈60% 更有利于校准因子的可靠性

**评估**：CI 和影响因子计算正确，Limitations #17 重写质量高。但 CV 值事实性错误未修正。Minor。

### 2.3 P1-4: TCGA "at bulk RNA-seq resolution" 限定 — 修复 ✅

手稿第 64 行："With these caveats, a notable observation, **at bulk RNA-seq resolution**, was that tumors appeared more transcriptionally homogeneous than normal tissues."

限定语正确放置在 TCGA 核心结论之前，后续讨论（第 97 行）也一致使用 "At bulk RNA-seq resolution"。✅

### 2.4 P1-5: SES 补充 Bootstrap CI 作为非参数替代 — 修复 ✅

- 手稿第 26 行："SES is interpreted as a non-parametric descriptive statistic complementing the permutation P-value, **not as a parametric test statistic such as Cohen's d**."
- 手稿第 42 行：重复并扩展上述声明，补充 Shapiro-Wilk/D'Agostino-Pearson 正态性检验结果（all P < 10⁻¹⁵）
- Bootstrap 95% CI（B=10,000, pair-level resampling）为所有关键 ω 估计提供非参数不确定性量化
- Supplementary Note 3.4（第 71 行）："SES should be interpreted as a non-parametric descriptive statistic rather than a parametric test result"

**评估**：SES 非参数定位明确，Cohen's d 仅作为反面对比出现（非同义词使用）。✅

### 2.5 P1-6: k_n floor = 1e-4 触发比例量化 — 部分修复 (Minor 残留)

v32 状态：
- 手稿第 97 行："in all 5 cancer types, the aggregate **tumor-versus-normal** k_n reached the floor value of 1 × 10⁻⁴, compared to mean k_n of 0.048–0.073 in single-cell datasets"
- Reproducibility Guide 第 311 行：参数表记录 "k_n floor (minimum) | 1e-4 | all analyses" ✅
- Supplementary Note 1.1（第 18 行）：floor 机制说明 ✅

**不足**：仅量化了 TN（tumor-normal）比较的 floor 触发率（5/5 cancer types = 100%），但 TT（tumor-tumor）和 NN（normal-normal）比较的 floor 触发比例未报告。TCGA ω 值异常偏高（BRCA Luminal A ω ≈ 344.5）主要由 k_n floor 驱动，因此完整量化 floor 触发比例对解释 TCGA 结果至关重要。

**评估**：机制描述和参数记录完整，但触发比例量化不完整。Minor。

### 2.6 P2 (E2-1~E2-6) 全部修复确认 ✅

| 编号 | v28 问题 | v32 状态 | 验证位置 |
|------|----------|----------|----------|
| E2-1 | 单侧检验理由不充分 | ✅ Methods 第 26 行 + SN 3.10 | 方向性假设理由清晰 |
| E2-2 | Bootstrap CI 定义不明 | ✅ Methods 第 42 行 | B=1,000 (permutation) + B=10,000 (CI) 区分明确 |
| E2-3 | Seed sensitivity 未讨论 | ✅ Methods 第 39 行 | Monte Carlo SE ≈ 0.016 at P=0.5, ≈ 0.001 at P=0.001 |
| E2-4 | n=1 SD 缺失标注 | ✅ Table 2 第 192-208 行 | n=1 的 cell types 标注 "—" |
| E2-5 | P 值精度未声明 | ✅ Methods 第 41 行 | "minimum resolvable P-value is 9.99 × 10⁻⁴" |
| E2-6 | SN 3.11 数据缺失 | ✅ SN 3.11 第 84-85 行 | 参数论证完整，跨物种验证引用 Supp Fig S2 |

## 3. 统计方法逐一评估

### 3.1 Bootstrap P 值公式一致性 — 通过 ✅

公式 P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) 在以下 6 处完全一致：

| 位置 | 文件 | 行号 | B 值 |
|------|------|------|------|
| Methods | Manuscript | 26 | 1,000 |
| Statistical reporting | Manuscript | 41 | 1,000 |
| Results | Manuscript | 48 | 1,000 |
| SN 1.5 | Supplementary | 26 | 1,000 |
| SN 3.1 | Supplementary | 63-65 | 1,000 |
| Repro Guide 5.1 | Reproducibility | 148 | 1,000 |

残差模型使用反向公式 P = (count(null_residual ≤ observed) + 1)/(B + 1)（第 35 行），B=10,000，方向正确（检测异常低残差）。+1 pseudocount 在所有位置一致。✅

### 3.2 单侧检验理由 — 充分但有方向性限制

**理由充分性**：
- Methods 第 26 行："The one-sided test is appropriate because our hypothesis is directional: we test whether observed ω exceeds the null expectation (equivalent populations), not whether it differs in either direction."
- SN 3.10（第 83 行）进一步论证："The biological questions addressed here (functional divergence exceeding baseline, Strong migration candidates showing anomalously low omega) are inherently directional."
- 两个方向的不同检验分别对应不同生物学假设：ω_obs > ω_null 检测功能发散；residual < null 检测异常低分化。逻辑自洽。✅

**方向性限制（Minor）**：
- 主 permutation test 固定为上尾检验（ω_null ≥ ω_obs），可检测功能发散（ω > 期望）但**无法检测功能约束**（ω 显著低于期望）
- 手稿第 17 行提及 "ω much less than 1 means strong functional constraint" 作为可能解释，但当前检验框架不支持对此方向进行统计推断
- 建议在 Limitations 中补充说明：当前单侧设计无法检测功能约束方向，如需检测 ω 显著低于 baseline，应使用下尾检验

### 3.3 BH-FDR 校正策略 — 正确实施 ✅

**Bootstrap permutation（B=1,000）**：
- BH-FDR 在每个数据集内单独应用 ✅
- 最小可解析 P 值 9.99×10⁻⁴ 低于每个数据集最显著检验的 BH 阈值（brain: 5.0×10⁻³; human: 2.9×10⁻³; mouse: 3.3×10⁻³）✅
- 检验数由 cell-type 数决定（brain: 10, human: 17, mouse: 15），而非 pair 数 ✅

**残差模型 permutation（B=10,000）**：
- 36.3% 信号达到 P 值下限（9.99×10⁻⁵），BH-FDR 不可用 ✅
- 改用描述性 P 值方案：P-floor-reaching 信号作为 "strong evidence of deviation"，P ≥ 0.50 作为 "little to no evidence" ✅
- 限制生物学解释于 30 个预定义 Strong 候选信号，而非全部 31,764 个搜索空间 ✅
- Limitations #16（第 100 行）明确声明 "formal Benjamini-Hochberg FDR correction is not applicable" ✅

**评估**：FDR 策略在不同分析层面（cell-type 级 bootstrap vs. pair 级残差模型）的区分处理方法学正确。

### 3.4 效应量报告 — 改进显著

**SES 定义与定位**：
- SES = (ω_obs − μ_null) / σ_null，从 permutation null 分布计算 ✅
- 明确标注为 "non-parametric descriptive statistic" 而非 "parametric test statistic such as Cohen's d" ✅
- 非正态性证据充分：Shapiro-Wilk/D'Agostino-Pearson 检验均拒绝正态性（all P < 10⁻¹⁵），右偏（brain skewness = 2.22, mouse 0.98, human 0.73）✅

**Bootstrap CI 覆盖**：
- 所有关键 ω 估计均提供 95% Bootstrap CI（B=10,000, pair-level resampling）✅
- CI 宽度与 pair 数反比：astrocytes（5,778 pairs）[14.14, 14.58] vs. Bergmann glia（21 pairs）[1.95, 2.90] ✅
- Calibration factor CI [4.12, 9.33] 在 5 处一致报告 ✅

**不足**：SES 本身未提供 CI（仅有 ω 的 CI）。考虑到 SES 的描述性定位，这是可接受的，但完整的效应量报告应包含 SES 的不确定性估计。

### 3.5 ω 分布特征化 — 全面 ✅

- Skewness: brain 2.22, mouse 0.98, human 0.73
- Excess kurtosis: brain 7.28（手稿第 99 行提及）
- 正态性检验：Shapiro-Wilk（n ≤ 5,000）和 D'Agostino-Pearson（n > 5,000），all P < 10⁻¹⁵
- Supplementary Figure S8 提供直方图和 Q-Q 图

**评估**：分布特征化充分，为 SES 的非参数定位提供了坚实依据。✅

## 4. 校准因子深度分析

### 4.1 基本参数验证

基于 6 个 control ω 值 [12.16, 6.57, 6.34, 5.22, 8.15, 1.59]：

| 参数 | 手稿报告值 | 实际计算值 | 一致性 |
|------|-----------|-----------|:------:|
| Mean | 6.67 | 6.672 | ✅ |
| Median | 6.46 | 6.455 | ✅ |
| Range | 1.59–12.16 | 1.59–12.16 | ✅ |
| CV | ≈ 60% | **52.1%** | ❌ |
| 95% Bootstrap CI | [4.12, 9.33] | 合理（正态近似 [3.89, 9.45]） | ✅ |

**CV 差异分析**：
- 样本 SD（ddof=1）= 3.474，CV = 52.1%
- 总体 SD（ddof=0）= 3.172，CV = 47.5%
- 无论使用哪种 SD 定义，CV 均不等于 60%
- v28 综合报告（第 162 行）正确标注 "CV≈52%"，但 v32 手稿第 52 行仍写 "CV ≈ 60%"
- 此错误可能源于早期版本使用的不同 control 值集合，在数据更新后 CV 计算未同步修正

### 4.2 CI 范围对 ω_cal 的影响

Limitations #17（第 100 行）的影响因子计算：

| CI 边界 | 校准公式 | ω_cal 偏移因子 | 计算验证 |
|---------|---------|:--------------:|:--------:|
| 下限 4.12 | ω / 4.12 | 1.62× 上移 | 6.67/4.12 = 1.619 ✅ |
| 上限 9.33 | ω / 9.33 | 0.71× 下移 | 6.67/9.33 = 0.715 ✅ |

**影响范围评估**：
- 以 brain global mean（ω = 8.01）为例：ω_cal 范围 = [0.86, 1.94]，即从 "略低于 baseline" 到 "接近 2× baseline"
- 以 astrocytes（ω = 14.36）为例：ω_cal 范围 = [1.54, 3.49]，均 > 1，结论方向不变
- 以 Bergmann glia（ω = 2.37）为例：ω_cal 范围 = [0.25, 0.58]，均 < 1，结论方向不变

**评估**：对于 ω 值远离 6.67 的 cell types（如 astrocytes 14.36 或 Bergmann glia 2.37），CI 范围不影响定性结论。但对于 ω 值接近 6.67 的 cell types（如 brain global mean 8.01），ω_cal 是否 > 1 取决于校准因子取值。手稿正确指出 "All CKI conclusions—which rely on rank-based interpretation rather than absolute ω_cal thresholds—are robust to this range." ✅

### 4.3 跨方案转移性

Limitations #17 明确承认：
- 校准因子来自 mouse global HVG scheme
- 应用于 human/TCGA/brain 的 per-pair DE scheme
- "the per-pair scheme produces a more targeted (and potentially larger) k_f than the global scheme, so the mouse-derived calibration factor likely **underestimates** the true baseline inflation in the per-pair setting"

**评估**：方向性判断正确（per-pair DE 选出的基因差异更大，因此 baseline inflation 应更高）。手稿提供了 calibrate_omega 函数供用户自行验证。这是当前框架下的最佳实践，但根本性的跨方案验证仍缺失。考虑到这一局限已被充分声明且 rank-based 结论对此鲁棒，不构成 Major 问题。

### 4.4 Monte Carlo 误差评估

手稿第 39 行："with B = 1,000 permutations, the Monte Carlo standard error of the empirical P-value is approximately 0.016 at P = 0.5 and 0.001 at P = 0.001"

验证：MCSE = sqrt(P(1-P)/B) = sqrt(0.5×0.5/1000) = 0.0158 ≈ 0.016 ✅；sqrt(0.001×0.999/1000) = 0.0010 ≈ 0.001 ✅

**评估**：Monte Carlo 误差计算正确，支持 B=1,000 的充分性论证。✅

## 5. 新发现问题

### 5.1 (Minor) 校准因子 CV 值事实性错误

**位置**：手稿第 52 行
**问题**：手稿报告 "CV ≈ 60%"，但基于 6 个 control 值的实际 CV = 52.1%（样本 SD）或 47.5%（总体 SD）。v28 综合报告已正确标注 CV≈52%，但 v32 未修正。
**影响**：CV 60% vs 52% 不影响结论方向，但影响校准因子精度的定性判断。CV 52% 更有利于校准因子的可靠性。
**建议**：将第 52 行 "CV ≈ 60%" 修改为 "CV ≈ 52%"。

### 5.2 (Minor) MANIFEST "FDR-significant" 术语残留矛盾

**位置**：MANIFEST 第 72 行
**问题**："16/30 FDR-significant descriptive" — "FDR-significant" 与 "descriptive" 并列使用，而正文明确声明 "formal FDR correction is not applicable"。
**影响**：MANIFEST 作为构建清单是审稿人可能首先查阅的文件，术语矛盾会引起混淆。
**建议**：改为 "16/30 P-floor-reaching (descriptive), 14/30 non-significant"。

### 5.3 (Minor) 摘要 "statistically significant" 措辞与正文不一致

**位置**：Abstract 第 11 行 vs. 正文第 81、100 行
**问题**：摘要写 "two statistically significant" mechanisms，正文写 "descriptive evidence rather than FDR-controlled discoveries" 和 "formal FDR correction is not applicable"。"Statistically significant" 在 FDR 不可用的语境下使用，与正文的谨慎措辞不一致。
**影响**：摘要是审稿人和读者首先阅读的部分，措辞不一致可能引起对统计严谨性的质疑。
**建议**：将摘要 "two statistically significant" 改为 "two with permutation support" 或 "two reaching permutation floor"。

### 5.4 (Minor) k_n floor 触发比例量化不完整

**位置**：手稿第 97 行
**问题**：仅报告 "in all 5 cancer types, the aggregate **tumor-versus-normal** k_n reached the floor value of 1 × 10⁻⁴"。TT 和 NN 比较的 floor 触发率未报告。
**影响**：TCGA ω 值异常偏高（BRCA Luminal A ω ≈ 344.5）主要由 k_n floor 驱动，完整量化 floor 触发比例对解释 TT/NN/TN 三类比较的 ω 差异至关重要。
**建议**：补充 TT 和 NN 比较中 k_n floor 触发的比例，如 "X% of TT pairs and Y% of NN pairs also triggered the k_n floor"。

### 5.5 (Minor) 单侧检验无法检测功能约束方向

**位置**：Methods 第 26 行、SN 3.10 第 83 行
**问题**：主 permutation test 固定为上尾检验（ω_null ≥ ω_obs），可检测功能发散但无法检测功能约束（ω 显著低于 null 期望）。手稿第 17 行将 "ω much less than 1" 列为可能解释，但当前框架不支持对此方向进行统计推断。
**影响**：如研究者希望检验某 cell type 是否处于强功能约束（ω << 1），当前设计无法提供统计支持。
**建议**：在 Limitations 中补充说明此限制，或提供下尾检验选项。

### 5.6 (Minor) 36.3% P 值下限饱和率的替代解释未讨论

**位置**：手稿第 35、81、100 行
**问题**：36.3% 的信号（11,541/31,764）达到 P 值下限（9.99×10⁻⁵），手稿仅解释为 "strong evidence of deviation from the multiplicative null model"。但如此高的比例也可能反映 permutation scheme 的 null 分布过于狭窄（即 null residual 分布的方差被低估），而非所有信号都是真实的强效应。
**影响**：不影响 16 个 Strong 候选信号的结论（这些是预定义的极端候选），但影响对全量 31,764 个比较的 P 值分布解读。
**建议**：在 Limitations 或 Discussion 中简要讨论 null 分布宽度对 P 值下限饱和率的潜在影响。

## 6. 综合评分与建议

### 6.1 评分分解

| 维度 | v28 评分 | v32 评分 | Δ | 评估依据 |
|------|---------|---------|---|---------|
| 统计方法严谨性 | 7.5 | 8.5 | +1.0 | Bootstrap 公式 6 处一致；单侧检验理由充分；FDR 策略分层正确；CV 错误扣 0.3 |
| 效应量报告 | 7.5 | 8.5 | +1.0 | SES 非参数定位明确；Bootstrap CI 覆盖全面；SES 本身无 CI 扣 0.2 |
| 校准因子可靠性 | 7.0 | 8.2 | +1.2 | CI 5 处一致；影响因子计算正确；Limitations #17 重写质量高；CV 事实错误扣 0.3；floor 量化不完整扣 0.3 |
| 数据集间比较 | 8.0 | 8.4 | +0.4 | TCGA bulk 限定到位；跨方案转移性承认；样本量谨慎声明；摘要措辞不一致扣 0.3 |
| **加权综合** | **7.6** | **8.4** | **+0.8** | — |

### 6.2 评分变化理由

+0.8 的提升主要来自：
1. 校准因子 CI 和影响因子的系统性报告（+0.3）
2. SES 非参数定位的明确化和 Cohen's d 的完全清除（+0.2）
3. 脑区残差模型描述性 P 值方案的正确实施（+0.2）
4. E2-1~E2-6 全部 6 项 P2 建议的落实（+0.1）

扣分项（阻止 8.5+ 的因素）：
1. CV 事实性错误未修正（-0.1）— v28 已明确标注正确值
2. MANIFEST 术语残留矛盾（-0.05）— P0-2 修复不彻底
3. 摘要措辞不一致（-0.05）— 影响审稿人第一印象

### 6.3 投稿准备度评估

**统计维度准备度**：~90%。无 Critical 或 Major 问题，6 项 Minor 问题预计 30 分钟内可全部修复。

**修复优先级**：
1. 修正 CV 值 60% → 52%（手稿第 52 行）— 2 分钟
2. 修正 MANIFEST "FDR-significant" 术语（第 72 行）— 1 分钟
3. 修正摘要 "statistically significant" 措辞（第 11 行）— 2 分钟
4. 补充 TT/NN floor 触发比例（第 97 行）— 需查阅数据
5. 补充单侧检验方向性限制说明（Limitations）— 5 分钟
6. 讨论 P 值下限饱和率的替代解释（Discussion/Limitations）— 5 分钟

**推荐行动**：统计维度已达到 NAR 投稿标准。建议修复上述 6 项 Minor 问题后投稿，但即使不修复也不构成 desk reject 或 major revision 的理由。

**Critical: 0, Major: 0, Minor: 6**
