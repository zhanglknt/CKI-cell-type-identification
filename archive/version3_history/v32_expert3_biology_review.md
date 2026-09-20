# CKI v32 独立审稿 — E3: 转录组学与单细胞应用

**审稿日期**: 2026-08-02
**审稿人**: E3 (Transcriptomics & Single-cell Applications)
**审稿对象**: version3/CKI_NAR_Submission_v32/ (32 文件)
**对比基准**: v28 审稿 (v28 E3 评分: 7.3/10)
**评分**: 8.2/10 (v28: 7.3/10, Δ: +0.9)

---

## 1. 核心发现概要

v32 在生物学解释合理性方面相较 v28 有显著改善。最核心的进步是：稿件现在清晰区分了统计学支持的发现（16/30 Strong signals 达到 P-value floor）与探索性观察（14/30 阈值通过但不显著），并在 Results、Discussion、Limitations 三处保持一致表述。四个 v28 E3 Major 问题（M-E3-1 脑区非显著信号并列、M-E3-2 TCGA 结论顺序、M-E3-3 神经元排除理由、M-E3-4 校准因子精度）及 6 项 E3 Minor（E3-1~E3-6）均已实质性修复。

残留问题主要集中在：(1) 跨物种验证在正文中的呈现仍过于薄弱（仅 Discussion 末尾一句，无具体 r 值）；(2) TCGA Results 段未提及 k_n floor 对 ω 值的膨胀效应，读者需翻至 Discussion 才能理解 ω≈344.5 的成因；(3) "Strong candidate" 术语本身仍用于描述 14 个 P≥0.76 的非显著信号，虽已加 "threshold-passing" 限定，但术语层面的歧义犹存。这些问题均为 Minor，不影响投稿。

**Critical: 0, Major: 0, Minor: 5**

---

## 2. v28→v32 修复验证

### 2.1 P0-1: Strong candidate 计数修正 — ✅ 已修复

v28 问题：Results L81 计数 8+2+22+22+4=58 ≠ 30（v28 synthesis P0-1）。

v32 状态：Manuscript L81 现表述为：
> "threshold criteria (residual < 0.3, ω < 15) identified 30 (0.09%) threshold-passing candidates: Astrocyte (6), oligodendrocyte (10), microglia (10), fibroblast (1), and vascular cells (3)."

验证：6+10+10+1+3 = **30** ✓。MANIFEST v32 同步确认 "6+10+10+1+3=30"。

**注意**：v28 synthesis 的修复计划建议分为 6 类（Astrocyte 6, Oligo 10, Micro 10, Bergmann 1, Vascular 2, Fibroblast 1），但 v32 实际实施为 5 类（Bergmann glia 0 个 Strong signal，Vascular 调整为 3）。这是合理的修正——L89 明确指出 "Bergmann glia had the lowest global ω (2.37) and no Strong signals"，Bergmann glia 的低 ω 是全局性的而非特定区域对异常，因此不应归入 Strong candidate。MANIFEST 与正文一致。

### 2.2 P1-1: 脑区非显著信号降级 — ✅ 已修复

v28 问题（M-E3-1）：14/30 Strong candidates 完全不显著（P≥0.76）但与显著信号并列呈现。

v32 状态：非显著信号现已独立成节 "Threshold-passing but non-significant signals"（L91），明确表述：
> "These 14 signals are likely dominated by stochastic variation in the high-dimensional ω landscape and should not be interpreted as evidence of biological structure."

此外，Limitation #8（Eighth）进一步强调：
> "14 of 30 Strong threshold-passing signals... did not reach statistical significance (all P ≥ 0.76). These signals should be interpreted with caution as they may reflect stochastic variation rather than robust biological patterns."

Abstract 也同步修正为 "30 cell-type developmental signatures spanning four biological mechanisms (two statistically significant)"，准确反映了只有两个机制有统计学支持。✓

### 2.3 P1-4: TCGA "at bulk RNA-seq resolution" 限定 — ✅ 已修复

v28 问题（M-E3-2）：TCGA 结论表述顺序需调整。

v32 状态：TCGA Results 段（L64）在呈现结论前先声明 caveats：
> "The TCGA analysis is inherently exploratory because bulk RNA-seq cannot distinguish genuine transcriptional convergence of tumor cells from at least three alternative explanations..."

随后用限定语呈现发现：
> "a notable observation, at bulk RNA-seq resolution, was that tumors appeared more transcriptionally homogeneous than normal tissues."

Discussion（L97）再次强调 "At bulk RNA-seq resolution, the apparent convergence could be driven by..."。Limitation #4 也同步标注 TCGA 的 bulk resolution 限制。✓

### 2.4 P1-7: 神经元排除理由 — ✅ 已修复

v28 问题（M-E3-3）：缺失神经元排除分析的理由说明。

v32 状态：L74 提供了详细的排除理由：
> "Neurons were excluded because the supercluster_term annotation does not resolve the extensive neuronal subtype heterogeneity (glutamatergic, GABAergic, dopaminergic, etc., spanning dozens of transcriptionally distinct populations). Treating neurons as a single cell class would violate the same-cell-type assumption of our cross-region framework, as different brain regions contain fundamentally different neuron subtype compositions."

理由充分，涉及注释分辨率限制和方法论假设一致性两个层面。✓

### 2.5 P1-8: Bergmann glia 归属 — ✅ 已修复

v32 状态：L89 专设 "Bergmann glia: cerebellar molecular topography" 小节：
> "Bergmann glia had the lowest global ω (2.37) and no Strong signals, consistent with their developmentally fixed, transcriptionally constrained state in the adult cerebellum (30)."

明确了 Bergmann glia 的 0 Strong signal 归属，并解释了低 ω 的生物学原因（发育固定、转录约束状态）。✓

### 2.6 E3-1~E3-6 (P2 Minor) 验证

| 编号 | 问题 | v32 状态 | 验证位置 |
|------|------|:---:|------|
| E3-1 | 跨物种 r 值 | ✅ | L98: "ω rankings are moderately conserved"; Supp Fig S2 legend: "Spearman r and P-value" |
| E3-2 | 四机制边界 | ✅ | L79: "These mechanisms are not mutually exclusive; a given cell-type/region-pair signal may involve overlapping processes" |
| E3-3 | Limitations 优先级 | ✅ | L99: 17 项 Limitations 按 First~Seventeenth 排序 |
| E3-4 | Table 1 信息论 | ✅ | L22: "JS divergence (42) uses the base-2 logarithm (range [0, 1])"; Methods 详细描述 JS 为 primary metric |
| E3-5 | OPC sensitivity | ✅ | L83: "0 Strong signals among 5,671 OPC cross-region comparisons—a finding that provides a useful internal consistency check"; L98: "providing a notable orthogonal validation" |
| E3-6 | HK 癌症失调 | ✅ | L99 Limitation #3: "housekeeping gene expression may be dysregulated in cancer (47), potentially affecting the k_n baseline" |

---

## 3. 各数据集生物学评估

### 3.1 Tabula Muris (Mouse) — 校准与验证

**数据代表性**：15,057 cells, 6 organs, 32 cell-type entries。作为 FACS/SmartSeq2 数据集，基因检测深度高，适合 pseudobulk 分析。覆盖 6 个主要器官，对小鼠 atlas 有合理代表性。

**生物学解释**：校准实验（6 个 split-half controls）正确展示了 baseline 行为（ω=6.67, all P>0.05）。S/D/X 分类的 ω 梯度（S=21.31 < D=43.19）符合预期生物学距离层级。k_f 较 k_n 增长 1000-fold vs 100-fold 的论证有效支持了 CKI 度量功能性分歧而非总差异的 claim。

**残留 concern**：n=6 的校准样本量仍然偏小（CV≈60%），但 v32 已通过 95% bootstrap CI [4.12, 9.33] 和 Limitation #17 充分量化了不确定性，且明确说明所有结论依赖 rank-based 解释而非绝对 ω_cal 阈值。此问题已从 Major 降为可接受的 limitation。

### 3.2 Tabula Sapiens (Human) — 跨度量独立性

**数据代表性**：108,136 cells, 102 cell-type entries, 6 organs。覆盖面广泛，但仅含 6 个器官（缺少 brain、skin、intestine 等），对人类 atlas 的代表性有局限。稿件未讨论这一局限。

**生物学解释**：CKI ω 与四种标准度量的负相关（Spearman r = −0.38 to −0.57, all P < 0.001）是全文最有力的发现。Same-organ pairs 比 different-organ pairs 有更高 ω（24.87 vs 20.80, P < 0.001）的 "reversal" 现象，合理解释为 CKI 对共享微环境内功能特化的敏感性。

**Cross-organ conservation ranking**（Table 2）：B cells (ω=2.70) 最保守、Endothelial cells (ω=15.09) 最特化的排序与已知生物学一致。但多数细胞类型 n=1-3，稿件已建议 "n < 5 as suggestive only"。这一 caveat 是必要的。

### 3.3 TCGA (Cancer) — 探索性分析

**数据代表性**：3,596 samples, 5 cancer types (LUAD, LUSC, LIHC, KIRC, BRCA)。覆盖主要癌种，但仅 5 种不能代表 pan-cancer。

**生物学解释**：NN/TT > 1.0 的发现（tumors 更同质）在 bulk resolution 下有至少三种替代解释（cell composition shifts, peritumoral inflammation, RNA quality），v32 已充分声明。PAM50 梯度（LumA > LumB > HER2 > Basal-like）的 proliferation-confound 也已讨论。

**关键 concern (Minor)**：TCGA Results 段（L64-66）未提及 k_n floor 对 ω 值的膨胀效应。Discussion（L97）才解释：
> "in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴"

读者在 Results 中看到 BRCA Luminal A ω≈344.5 时可能困惑，直到 Discussion 才理解这是 k_n floor 导致的膨胀。建议在 Results 首次报告 TCGA ω 值时添加括号注释。

### 3.4 Siletti Brain Atlas — 核心生物学发现

**数据代表性**：888,263 non-neuronal nuclei, 108 brain regions, 10 cell classes。这是目前最大规模的人类脑 snRNA-seq atlas 之一，覆盖度优秀。排除神经元后的 10 类非神经元细胞涵盖了主要胶质和结构细胞类型。

**ω gradient 生物学合理性**：Bergmann glia (2.37) → committed OPC (3.17) → fibroblasts (3.99) → ... → astrocytes (14.36) 的 6.06-fold 梯度与已知细胞生物学高度吻合：
- Bergmann glia：发育固定，维持 Purkinje cell 层结构 ✓
- Vascular cells/fibroblasts：通过循环系统持续交换 ✓
- Microglia：核心监视功能共享，区域表型变异 ✓
- Astrocytes：区域特异性离子通道/转运蛋白表达 ✓

**Multiplicative residual model**：30 个 Strong candidates 中 16 个达到 P-value floor（6 astrocytes + 10 oligodendrocytes），14 个 P≥0.76（10 microglia + 1 fibroblast + 3 vascular）。OPC 0/5,671 Strong signals 作为 internal consistency check 有效验证了模型不是简单检测高 ω 值或绝对转录差异。

**Four mechanisms 解释边界**：L79 明确声明 "not mutually exclusive"，并以 astrocyte thalamic signatures 为例说明 developmental origin 和 compartmentalized specification 可共同作用。两个统计学显著机制（oligodendrocyte dorsal/ventral origin, astrocyte compartmentalized specification）有 Foerster et al. (27) 和 Endo et al. (29) 的实验证据支持。两个探索性机制（colonization route boundaries, postnatal migration）明确标注为 exploratory。

---

## 4. 跨物种/跨数据集一致性

### 4.1 Mouse→Human 一致性

L98 Discussion 末尾提到：
> "Preliminary cross-species validation using shared cell types between mouse and human atlases (44; Supplementary Fig. S2) was limited by the small number of directly comparable cell-type pairs, and ω rankings are moderately conserved between mouse and human for shared cell types, though absolute ω values differ due to different computation schemes."

Supplementary Fig. S2 legend 进一步说明 "scatter plot of human vs. mouse ω for shared cell types, with Spearman r and P-value"。

**评估**：跨物种验证的框架存在，但存在两个不足：
1. **正文缺乏具体数值**：Discussion 仅用 "moderately conserved" 描述，未给出 Spearman r 值或 P 值。读者需查阅 Supplementary Fig. S2 才能获得定量信息。
2. **方案差异未充分讨论**：mouse pilot 使用 per-pair DE scheme，human 使用 hybrid scheme（global k_n + per-pair k_f）。L57 提到了这一差异（"mouse pilot data uses the same hybrid scheme as human... while the mouse full pairwise matrix uses a global HVG 2,000 set for k_f"），但跨物种比较时两套方案的 ω 不可直接比较，仅 rank-based 比较有效。这一点 Limitation #17 已涉及，但跨物种验证段落本身未强调。

### 4.2 Mouse/Brain→TCGA 逻辑链

TCGA 使用 bulk RNA-seq，与单细胞数据集的 ω 值不可直接比较（L97 已说明）。TCGA 的价值在于 within-dataset 的 TT vs NN 比较和 clinical stratification，而非跨数据集 ω 对比。稿件在 Discussion 和 Limitation 中均明确了这一点。

### 4.3 跨数据集 ω 值范围差异

| 数据集 | ω 范围 | 均值 | 方案 |
|--------|--------|------|------|
| Mouse (pilot) | 1.59–43.19 | 6.67 (controls) | per-pair DE (hybrid) |
| Mouse (full matrix) | — | 27.31 | global HVG 2,000 |
| Human | 1.10–58.69 | 14.23 | per-pair DE (hybrid) |
| TCGA | — | ~100–344 | per-pair DE (hybrid, bulk) |
| Brain | 2.37–14.36 | 8.01 | per-pair DE + per-pair k_n |

稿件 L97 明确建议 "Cross-dataset ω comparisons should therefore be interpreted as rank-based rather than absolute"。这一声明是必要的，但也暴露了 CKI 跨数据集可比性的根本局限。

---

## 5. 新发现问题

### Minor 1: 跨物种验证在正文中呈现不足

**位置**：L98 Discussion 末尾。

**问题**：跨物种验证是 CKI 方法泛化性的关键证据，但正文中仅有一句话，且未给出具体 Spearman r 值。Abstract、Introduction、Results 均未提及跨物种结果。Supp Fig S2 legend 提到 "Spearman r and P-value"，但读者必须翻阅 supplementary 才能获得定量信息。

**建议**：在 Discussion 中补充具体 r 值（如 "Spearman r = 0.XX, P = 0.0XX"），或在 Results "CKI captures information that standard metrics miss" 段末添加一句跨物种验证概述。

### Minor 2: TCGA Results 段缺失 k_n floor 说明

**位置**：L64–66 (TCGA Results) vs L97 (Discussion)。

**问题**：TCGA ω 值极高（BRCA Luminal A ω≈344.5），但 k_n floor 导致膨胀的解释仅在 Discussion 出现。Results 段首次报告这些数值时缺乏语境。

**建议**：在 Results L64 首次提及 TCGA ω 值时，添加简短括号注释，如 "(note: bulk RNA-seq averaging compresses k_n toward its floor, inflating ω; see Discussion)"。

### Minor 3: "Strong candidate" 术语对非显著信号的适用性

**位置**：L81, L91。

**问题**：14 个 P≥0.76 的信号仍被称为 "Strong candidate signals"（L91: "Microglia (10), fibroblast (1), and vascular cells (3) produced threshold-passing Strong candidate signals"）。虽然已用 "threshold-passing but non-significant" 限定，且明确声明不应解读为生物学信号，但 "Strong" 一词本身暗示可靠性，可能误导读者。

**建议**：考虑将非显著信号改称 "threshold-passing candidates (not statistically significant)" 或 "Tier-1 threshold candidates (P ≥ 0.76)"，避免 "Strong" 一词的双重含义。

### Minor 4: Cover Letter 对 30 个信号的表述略宽

**位置**：Cover Letter L18。

**问题**：Cover Letter 写道 "brain regional analysis identifying 30 cell-type-specific developmental signatures among 31,764 cross-region comparisons"，但仅 16/30 有统计学支持。Abstract 正确表述为 "30 cell-type developmental signatures... (two statistically significant)"，但 Cover Letter 缺少这一限定。

**建议**：Cover Letter 改为 "30 cell-type developmental signatures (16 statistically supported)" 或类似表述，与 Abstract 一致。

### Minor 5: 脑区分析仅覆盖非神经元细胞的 scope limitation

**位置**：L74。

**问题**：脑区分析排除了神经元（理由充分），但 Limitations 中未将 "仅分析非神经元细胞" 列为一项独立 limitation。神经元占脑细胞约 50% 以上，排除神经元意味着 CKI 的脑区发育签名检测仅适用于胶质/结构细胞，不能推广到所有脑细胞类型。

**建议**：在 Limitations 中补充一项，明确说明 "the brain analysis is restricted to non-neuronal cells; developmental signatures in neuronal populations, which may exhibit distinct regional specification patterns, are not assessed."

---

## 6. 综合评分与建议

### 6.1 评分明细

| 维度 | v28 评分 | v32 评分 | Δ | 说明 |
|------|:---:|:---:|:---:|------|
| 1. 生物学解释合理性（ω 含义、选择性重塑概念、脑区迁移模型） | 7.0 | 8.5 | +1.5 | 四机制边界澄清、非显著信号降级、Bergmann glia 解释均显著改善 |
| 2. 数据集代表性（Tabula Muris/Sapiens/TCGA/Brain 覆盖度） | 7.5 | 7.8 | +0.3 | 数据集未变，但神经元排除理由和 TCGA bulk caveat 改善了表述透明度 |
| 3. 跨物种验证（mouse→human→TCGA 逻辑链） | 7.0 | 7.5 | +0.5 | 跨物种验证在 Discussion 提及，但仍薄弱；TCGA 逻辑链通过 bulk resolution caveat 改善 |
| 4. 局限性诚实度（17 项 Limitations 排序、机制边界） | 7.7 | 9.0 | +1.3 | 17 项 Limitations 全面、有序、诚实；机制边界 "not mutually exclusive" 明确 |

**综合评分**：(8.5 + 7.8 + 7.5 + 9.0) / 4 = **8.2/10**

### 6.2 评分变化解释

v28→v32 Δ=+0.9 的提升主要来自三个方面的实质性改进：

1. **非显著信号处理**（+0.4）：v28 中 14/30 不显著信号与显著信号并列，是 v28 E3 扣分最多的 Major 问题。v32 通过独立小节、Limitation #8、Abstract 限定三层处理，彻底解决了这一问题。

2. **生物学解释边界澄清**（+0.3）：四机制 "not mutually exclusive" 声明、Bergmann glia 专节、OPC 作为 orthogonal validation 的论证，使生物学解释的谨慎度和精确度显著提升。

3. **TCGA 探索性定位**（+0.2）：从 Results 到 Discussion 到 Limitation 的三重 caveats（bulk resolution、cell composition confound、proliferation confound）使 TCGA 分析的定位从 "支持性证据" 转为 "探索性观察"，更符合数据实际能力。

### 6.3 提交建议

**推荐行动**：v32 已达到 NAR 投稿标准。E3 维度无 Critical 或 Major 问题，5 项 Minor 问题均不阻塞投稿，可在 revision 阶段处理。

**Desk reject 风险（E3 维度）**：极低。生物学解释合理、局限性诚实、数据集覆盖充分。

**Revision 优先级建议**（按 E3 维度）：
1. (Minor 1) 补充跨物种验证的具体 r 值到正文
2. (Minor 2) TCGA Results 段添加 k_n floor 简注
3. (Minor 5) Limitations 补充非神经元 scope limitation
4. (Minor 4) Cover Letter 同步 Abstract 的 "two statistically significant" 限定
5. (Minor 3) 考虑调整非显著信号的 "Strong" 术语

### 6.4 总体评价

v32 稿件在生物学解释方面已达到投稿级别的水准。最值得肯定的是作者对 14 个非显著信号的处理方式——没有选择删除或淡化，而是独立呈现、明确标注、在 Limitation 中诚实讨论，这体现了科学诚实性。OPC 0/5,671 作为 internal consistency check 的论证尤为精彩，有效区分了 "broad baseline motility" 和 "specific transcriptional signatures of developmental history"。跨物种验证仍是全文最薄弱的环节，但已通过 supplementary figure 和 Discussion 提及构成了最低限度的支撑。

---

**Critical: 0, Major: 0, Minor: 5**
