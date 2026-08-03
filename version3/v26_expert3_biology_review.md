# 专家3：生物学与单细胞基因组学审稿报告 — CKI v26

**Reviewer**: E3 — 生物学与单细胞基因组学专家
**Date**: 2026-08-02
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v26 (manuscript + supplementary + cover letter + reproducibility guide + Table1-2)
**Review baseline**: v25 expert score: 7.5/10

---

## 1. 总体评估

**v26 Score: 7.5/10** (v25: 7.5/10, **Δ = 0**)

v26 修复了 v25 的多数 P0/P1 问题（N4 术语清理、N9 PMI 扩展、Table 1 数字统一、Cover Letter 标题统一、Cohen's d 清理），Limitations 从 ~12 条扩展至 15 条且多数内容质量高。然而，v26 引入了一个新的编号错误（N8 未完全修复，详见第 2 节），且 v25 E3 审稿中提出的 TCGA ω 尺度异常未讨论（v25-N3）仍未解决。更关键的是，Abstract 和 Introduction 对脑分析结论的表述存在生物学过度解读——声称"四种生物学机制"和"colonization route boundaries + postnatal migration event"，但其中两种机制的信号在 Results 中被明确标注为统计学不显著（all P ≥ 0.76）。

综合来看，v26 在文档一致性方面有进步，但在生物学结论的严谨性方面出现了新的问题，抵消了 P0/P1 修复带来的提升。

---

## 2. N8 修复验证：Limitations 编号 — 未完全修复（3/10）

### 问题：旧编号残留导致新的重复

v25 的 N8 问题是"两个 Seventh"。v26 的 Limitations 段落（line 103）已扩展为 First 至 Fifteenth 共 15 条，编号连续无重复。然而，**line 104 仍保留了 v25 的旧 Eleventh 和 Twelfth**，内容与 line 103 的 Eleventh/Twelfth 完全不同：

| 位置 | 编号 | 内容 |
|------|------|------|
| Line 103 Eleventh | Eleventh | k_n 和 k_f 基因集大小差异（~1,130 vs 200–2,000） |
| Line 104 Eleventh | Eleventh（**重复**） | 多重残差模型置换检验（B=10,000, P-value floor saturation 36.3%） |
| Line 103 Twelfth | Twelfth | hybrid scheme 中 k_n 全局计算的局限性 |
| Line 104 Twelfth | Twelfth（**重复**） | 校准因子跨方案可迁移性（ω_cal = ω/6.67 从 mouse global HVG 到 per-pair DE） |

**评估**：v25 的"两个 Seventh"问题已被替换为"两个 Eleventh + 两个 Twelfth"问题。虽然原始问题（Seventh 重复）已解决，但新的编号重复同样违反学术写作规范。Line 104 的两条内容部分与 line 103 的 Eighth（置换检验不显著结果）和 Tenth（校准基线局限性）重叠，但各有独特内容（P-value floor saturation 的 FDR 不可适用性、cross-scheme transferability），应被整合为新的 Thirteenth 和 Fourteenth（并相应调整后续编号），或合并入现有条目。

**严重程度**：Medium。不阻塞投稿但会被审稿人指出。

**修复建议**：将 line 104 的两条内容合并入 line 103 的现有条目，或重新编号为 Sixteenth 和 Seventeenth。

---

## 3. N9 修复验证：Brain PMI 讨论 — 充分修复（8.5/10）

### 修复评估

v25 的 N9 问题是 PMI 讨论仅一句话。v26 已扩展为完整段落（Limitation Fifth）：

> "Fifth, the brain analysis uses post-mortem tissue; post-mortem interval (PMI) varies across samples and may differentially affect RNA integrity by brain region and cell type, potentially introducing systematic biases in regional omega comparisons. Neuron-specific RNA degradation signatures (e.g., activity-dependent transcripts with short half-lives) could be disproportionately affected. However, astrocyte and oligodendrocyte signals dominate the residual model results, and these glial cell types tend to be less sensitive to PMI-related degradation than neurons. Developmental time courses with controlled collection conditions would provide stronger evidence for migration inference and help disentangle PMI effects from genuine developmental signatures."

**改进点**：
1. 明确讨论了 PMI 区域异质性对 RNA 完整性的影响 ✅
2. 提出神经元特异性降解标志物（活动依赖转录本、短半衰期）可能受不成比例影响 ✅
3. 论证了胶质细胞（astrocyte/oligodendrocyte）主导的信号对 PMI 较不敏感——这是一个合理的生物学论点 ✅
4. 建议发育时间进程数据以提供更强证据 ✅

**小缺口**：
- 未讨论供体间变异（年龄、死因、性别）对 ω 的潜在贡献
- 未讨论细胞数量不对称（Bergmann glia n=21 vs astrocytes n=5,778）对 ω 估计精度的直接影响——虽然 Limitation Ninth 一般性地提到了 CI 宽度与配对数的反比关系，但未将此与 PMI 讨论关联

**评估**：从 v25 的 4/10 提升至 8.5/10。修复质量实质性改善，已达到发表标准。

---

## 4. N4 修复验证："Neutral" 术语清理 — 完全修复（9.5/10）

v25 指出 Discussion 已改为 "constrained baseline" 但 Results 和 Figure legends 残留 5+ 处 "neutral"。v26 验证：

| 位置 | v25 措辞 | v26 措辞 | 状态 |
|------|----------|----------|:----:|
| Line 49 (Results) | "neutral and identity gene sets" | "constrained baseline and identity gene sets" | ✅ |
| Line 72 (Results) | "neutral baseline k_n" | "constrained baseline k_n" | ✅ |
| Line 120 (Fig 2 legend) | "neutral baseline behavior" | "constrained baseline behavior" | ✅ |
| Line 121 (Fig 3 legend) | "k_n (neutral rate)" | "k_n (baseline rate)" | ✅ |
| Line 119 (Fig 1 legend) | — | "Ka/Ks uses...as a neutral baseline" | ✅* |

*Line 119 的 "neutral baseline" 指 Ka/Ks 的 synonymous sites，不指 CKI 的 k_n，用法正确。

**残留 "neutral" 用法评估**（3处，均合理）：
- Line 15: "how much is simply neutral drift?" — Introduction 中引入一般概念，合理
- Line 99: "rather than pure neutral drift" — Discussion 中承认 HK 基因可能不完全中性，增强论证严谨性，合理
- Line 119: "Ka/Ks uses...as a neutral baseline" — 描述 Ka/Ks 而非 CKI，合理

**评估**：完全修复。所有指代 CKI k_n/HK 基因的 "neutral" 均已改为 "constrained baseline" 或 "baseline"。

---

## 5. HK 基因选择的生物学基础

### HRT Atlas 1,130 conserved HK genes — 充分（8/10）

**基因集选择**：HRT Atlas v1.0（ref 4, Hounkpel et al. 2021）是经同行评审的 HK 基因数据库，基于大规模 RNA-seq 数据挖掘定义。1,130 个人鼠保守 HK 基因是一个合理的参考集——足够大以提供稳定的 k_n 估计，又足够特异以代表受约束的基线表达。

**敏感性分析**："using the lowest 10% variable genes as a constrained set yielded ω correlations r > 0.95"（Limitation Second）。这一分析支持了 HK 基因集选择对结果的影响有限。但需要注意：
- r > 0.95 表明 ω 排名高度一致，但不排除绝对值有偏移
- 敏感性分析使用的是最低变异基因，而非另一种 HK 基因定义（如 EPD、Housekeeping Gene Database），因此测试的是"低变异基因集"的等效性，而非 HK 基因定义的稳健性

**"Constrained baseline" 概念**：v26 在 Discussion（line 97）中明确表述"HK genes are under stabilizing selection that constrains their expression variance across conditions, making them a practical constrained baseline"。这一表述在生物学上是准确的——HK 基因确实受稳定化选择约束，其表达变异低于组织特异性基因。Limitation Second 也承认"HK genes are defined empirically (high detection rate, low CV) rather than mechanistically"，这一区分恰当。

**缺口**：未引用直接支持 HK 基因受纯化选择/稳定化选择的文献（如群体遗传学证据或启动子结构研究）。v25 的此建议在 v26 中仍未实现。这不阻塞投稿但会令严格的审稿人觉得"constrained baseline"的文献支撑略显单薄。

---

## 6. 细胞类型鉴定的生物学可信度

### Cross-organ conservation ranking（Table 2）— 良好（7.5/10）

**小样本警告**：v26 明确警告"several cell types in this ranking have very few cross-organ pairs (n = 1–3; e.g., Memory B cells n = 1, Smooth muscle n = 1), and their mean ω estimates are correspondingly unreliable. We recommend interpreting the ranking of cell types with n < 5 as suggestive only"。这一警告充分且恰当。

**实际情况**：Table 2 的 17 个细胞类型中，仅 5 个有 n ≥ 5（Neutrophil n=6, Plasma cell n=6, CD8+ T cell n=6, NK cell n=10, Macrophage n=15），其余 12 个均为 n = 1–3。这意味着大部分排名应被视为"suggestive only"——稿件已诚实承认这一点。

**生物学合理性**：
- B cells/Neutrophils 最保守（ω ≈ 2.7）——免疫细胞循环系统分布，跨器官保守，合理 ✅
- Endothelial cells 最器官特异（ω = 15.09）——内皮细胞表达器官特异性基因程序（ref 36），合理 ✅
- Macrophages 中等保守（ω = 9.84, n=15）——组织驻留巨噬细胞有组织特异性，但核心功能保守，合理 ✅

**"Constrained baseline" 术语在生物学上下文中**：使用准确。Line 72 "if their constrained baseline k_n is low, even modest functional differences can produce a high ω" 正确描述了 CKI 的归一化逻辑。

---

## 7. 脑区分析生物学解释

### 7.1 四种生物机制分类 — 概念合理但 Abstract/Introduction 过度解读（6/10）

**机制定义**（line 35, 79）：
- (i) Developmental origin heterogeneity (DO) — 不同胚胎前体池来源的细胞保留不同转录组身份
- (ii) Embryonic colonization route boundaries (CR) — 不同发育进入点的免疫细胞显示残余转录组不连续性
- (iii) Compartmentalized developmental specification (DS) — 发育过程中的区域特异性转录程序产生持久的星形胶质细胞和血管身份差异
- (iv) Postnatal cell migration (PM) — 出生后通过主动运动在区域间物理迁移的细胞

**文献支撑**：
- (i) DO: Foerster et al. (35) — 背侧/腹侧少突胶质细胞起源，Nature Neuroscience 2024，文献支撑强 ✅
- (ii) CR: Shemer & Jung (37) — 微胶质细胞定殖路线，Nat Rev Neurosci 2024，文献支撑充分 ✅
- (iii) DS: Endo et al. (18) — Tcf4 控制皮质星形胶质细胞分配，EMBO J 2024，文献支撑充分但仅限皮质 ✅
- (iv) PM: Jones et al. (38) — 血管周围成纤维细胞脑膜起源，Development 2023，文献支撑充分 ✅

**关键问题：Abstract/Introduction 过度解读**

Abstract（line 11）声称：
> "Brain regional analysis identified 30 cell-type-specific developmental signatures spanning four biological mechanisms among 31,764 comparisons."

Introduction（line 18）声称：
> "demonstrating that CKI can detect persistent developmental signatures—including developmental origin heterogeneity, colonization route boundaries, and a single postnatal migration event—from adult transcriptomic data."

然而，Results（line 81）和 Discussion（line 102）明确指出：
- 仅 16/30 Strong 信号达到统计显著性（P = 9.99 × 10⁻⁵）
- 显著信号仅来自 astrocytes (6/6) 和 oligodendrocytes (10/10)
- 对应机制仅为 (i) DO 和 (iii) DS
- 微胶质细胞 (CR, mechanism ii) 和成纤维细胞 (PM, mechanism iv) 的信号**均不显著**（all P ≥ 0.76）

**具体问题**：
1. Abstract 说"四种生物机制"被识别，但实际上只有 2/4 有统计学支持
2. Introduction 提到"colonization route boundaries"和"single postnatal migration event"——两者均不显著
3. Introduction 遗漏了"compartmentalized developmental specification"——这是有统计支持的机制
4. "a single postnatal migration event"暗示了一个已检测到的迁移事件，但该信号 P = 1.0

**评估**：Abstract 和 Introduction 的表述在严格意义上不算错误（30 个 threshold-passing 信号确实 span 四种机制），但会误导读者认为四种机制均有统计学支持。Results 和 Discussion 中的表述是准确的。这是一个生物学结论表述的严谨性问题。

**建议**：
- Abstract 改为 "spanning four biological mechanisms (two with statistical support)" 或类似限定
- Introduction 将"colonization route boundaries"和"postnatal migration event"标注为 exploratory，并补充"compartmentalized developmental specification"
- 或在 Introduction 中改为"developmental origin heterogeneity and compartmentalized developmental specification"（仅提及有统计支持的机制）

### 7.2 Oligodendrocytes developmental origin (Foerster et al.) — 合理但论证需更清晰（7.5/10）

**生物学解释**：所有 10 个 Strong oligodendrocyte 信号涉及 cortex/thalamus 或 brainstem-internal 配对，与 Foerster et al. (35) 的背侧/腹侧起源边界一致。

**论证逻辑**：
1. Cortex oligodendrocytes 主要为背侧来源（皮质放射状胶质）；thalamus/brainstem 为腹侧来源（MGE/LGE 前体）— 与 Foerster 一致 ✅
2. 背侧 vs. 腹侧 oligodendrocytes 的 ω 低于乘法模型预期 — 说明它们比预期更相似
3. 解释：尽管发育起源不同，共享的髓鞘化程序使它们在 CKI 检测的基因上比预期更相似
4. "CKI detects this developmental origin signature" — 通过低 ω 的空间模式匹配发育边界来推断发育起源

**概念张力**：Foerster et al. 显示背侧和腹侧 oligodendrocytes 有**不同**的转录程序（腹侧来源细胞即使移植到皮质也不能 adopting 皮质转录程序）。但 CKI 发现它们比预期**更相似**（低 ω）。表面上看这是矛盾的。

**解决方案**：CKI 检测的不是发育起源差异本身，而是发育起源边界的**空间模式**。背侧和腹侧 oligodendrocytes 在共享髓鞘化基因上相似（低 k_f），而在发育起源基因上不同——但 top-200 DE genes 可能被共享髓鞘化程序主导，使得 k_f 低于预期。这一解释合理但稿件未明确阐述此区分。

**"first transcriptome-wide metric" 声明**：
> "provides, to the best of our knowledge, the first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations without requiring lineage tracing"

这一声明是可辩护的——Foerster et al. 使用遗传谱系示踪，CKI 仅用转录组数据。但"distinguish"一词可能过于强烈：CKI 检测的是低 ω 的空间模式匹配发育边界，而非直接区分单个细胞的背侧/腹侧身份。建议改为"detect the transcriptional boundary between dorsal and ventral oligodendrocyte populations"。

### 7.3 Astrocytes thalamic subnuclei (VPL 4/6) — 生物学合理但文献支撑间接（7/10）

**发现**：6 个 Strong astrocyte 信号中，VPL（ventroposterior lateral nucleus）出现在 4/6 个配对中。

**生物学解释**：VPL 是丘脑 relay nucleus，参与体感信息传递。稿件推测"conserved astrocyte programs across thalamic relay nuclei that share a common developmental origin"。

**文献支撑**：
- "Regionalized astrogenesis, driven by subnucleus-specific transcriptional programs, has been shown to produce persistent thalamic astrocyte heterogeneity that is detectable in adult tissue" — **此句无具体引用**
- Endo et al. (18) 的 Tcf4 工作限于皮质，不直接涉及丘脑
- Reeber et al. (41) 关于 Bergmann glia 拓扑分区，不直接涉及丘脑星形胶质细胞

**评估**：VPL 信号本身有统计学支持（P = 9.99 × 10⁻⁵），生物学解释方向合理（丘脑 relay nuclei 共享发育起源），但"regionalized astrogenesis...detectable in adult tissue"这一关键论断缺少直接文献支撑。建议引用丘脑星形胶质细胞区域化的具体研究，或明确标注为推断。

### 7.4 Microglia colonization wave hypothesis — 探索性表述恰当（8.5/10）

**表述质量**：
1. Section title 包含 "(not statistically significant)" ✅
2. 统计 caveat 前置（"none reached statistical significance (all P ≥ 0.76)"）✅
3. "exploratory hypothesis rather than a statistically supported finding" ✅
4. 后置警告（"these patterns may reflect stochastic variation"）✅
5. 验证建议（"Validation through independent datasets or lineage tracing experiments would be required"）✅

**生物学内容**：
- 三条侵入路线（pial surface, ventricular zone, vasculature）— Shemer & Jung (37) ✅
- 嘴-尾定殖波 — Barry-Carroll et al. (40) ✅
- 7/10 信号涉及 cortex vs. midbrain/pontine 结构 ✅
- IC（inferior colliculus）作为可能的接触区 — 合理的推测

**评估**：探索性表述模范。所有生物学解释均被明确标注为非统计显著，读者不会误认为这是已验证的发现。

### 7.5 OPC internal consistency check — 论证基本充分但术语仍混用（7.5/10）

**核心论证**：
- OPCs 是成体 CNS 中最活跃迁移的细胞 → 如果模型检测"迁移"，OPCs 应有最多 Strong 信号
- 但 OPCs 有 0 个 Strong 信号 → 模型不检测迁移
- 因此，模型检测的是发育历史签名而非运动性

这一内部一致性检验在逻辑上是有效的。✅

**OPC 高 ω 的生物学解释**：
> "OPCs have a high global mean ω (7.65) because their transcriptional program includes both progenitor and differentiation states"

这一解释合理——OPC 转录组包含前体和分化状态的异质性，导致高全局 ω。✅

**未解决的数学结构问题**（v25 已指出，v26 未修复）：
OPC 全局 ω（7.65）接近总均值（8.01），在乘法残差模型中 expected_ω = μ_ct × μ_pair / μ_grand，当 μ_ct ≈ μ_grand 时，expected_ω ≈ μ_pair，使得残差不易极低。稿件未从数学结构角度讨论这一点。这不是必须修复的（生物学解释已充分），但补充一句数学说明会令论证更完整。

**术语混用**（v25 N6，v26 未修复）：
- Section header (line 83): "internal consistency check"
- 正文 (line 83): "orthogonal validation"
- Discussion (line 102): "orthogonal validation"
- Supplementary Fig S7 legend (line 132): "internal consistency check"

这两个概念有微妙差异：内部一致性检验验证模型结构；正交验证暗示独立证据。建议统一为 "internal consistency check"（与 header 和 Supplementary 一致）。

---

## 8. TCGA 癌症分析

### 8.1 Convergence 解释的 confounder 讨论 — 优秀（9/10）

v26 保持了 v25 的三层 confounder 讨论：

**Results (line 64)**：明确列出三种非排他性替代解释：
- (i) 肿瘤细胞组成偏移（purity, stromal/immune infiltration）
- (ii) 瘤周炎症和促结缔组织增生反应
- (iii) RNA 质量系统差异

**Results (line 66)**：PAM50 增殖分数混杂讨论：
> "the PAM50 gradient may partly reflect proliferative fraction differences across subtypes (Basal-like tumors have the highest proliferation rates and the lowest ω), meaning that the observed convergence could be driven by proliferation programs overriding tissue-specific expression rather than by a shared transcriptional attractor per se"

这一讨论展示了良好的生物学洞察力。Basal-like 肿瘤高增殖率 → 增殖程序覆盖组织特异性表达 → ω 降低。这一替代解释与传统的"趋同"解释对立，稿件诚实呈现了两者。✅

**Discussion (line 101)**：重复并强化警告，明确"single-cell or deconvolution-based validation would be needed"。✅

### 8.2 TCGA ω 尺度异常 — 仍未讨论（4/10）

**问题**（v25 E3 N3，v26 未修复）：

TCGA 的 ω 值远高于单细胞数据：
- BRCA Luminal A: ω = 344.5 ± 323.4
- LUAD EGFR-mutant: ω = 285.3 ± 180.1
- LIHC G1: ω = 101.8 ± 46.8

对比：
- Brain global mean: ω = 8.01
- Human (Tabula Sapiens) mean: ω = 14.23
- Mouse calibration: ω = 6.67

TCGA ω 比单细胞数据高 12-43 倍。稿件讨论了 bulk RNA-seq 的 confounders（组成偏移、炎症、RNA 质量），但**未讨论为什么 ω 值如此之高**。

可能的原因包括：
1. **k_n floor 效应**：bulk RNA-seq 中 HK 基因表达高度一致（因 bulk averaging），k_n 可能接近 floor (ε = 1e-9)，导致 ω = k_f / k_n 被人为放大
2. **bulk averaging 效应**：bulk pseudobulk 平滑了细胞间变异，使 HK 基因差异极小而 DE 基因差异保留
3. **log2(TPM+1) 转换**：与单细胞的 log1p(normalize_total) 不同，可能影响 JS divergence 的动态范围

**评估**：这是一个中等的生物学解释缺口。读者会疑惑为什么 TCGA ω = 344.5 而脑数据 ω = 8.01——这两者在生物学上意味着什么？是否可比？稿件未提供任何解释。

**建议**：在 TCGA Results 或 Limitation Fourth 中增加 1-2 句，例如："The substantially higher ω values in TCGA compared to single-cell datasets likely reflect bulk RNA-seq averaging effects: pseudobulk averaging across millions of cells compresses HK gene variance (low k_n) while preserving tumor-specific DE gene differences (high k_f), inflating ω. Cross-dataset ω comparisons should therefore be interpreted as rank-based rather than absolute."

### 8.3 PAM50 subtype gradient 与 proliferation 混淆 — 充分讨论（8.5/10）

如 8.1 所述，稿件明确讨论了 PAM50 gradient 可能反映增殖分数差异而非真正转录趋同。Basal-like（高增殖、低 ω）vs Luminal A（低增殖、高 ω）的梯度可能由增殖程序覆盖组织特异性表达驱动。

**小样本 caveat**：
> "the smallest subgroups (Normal-like n = 7; Edmondson G4 n = 11) have limited statistical power, and their rankings should be interpreted cautiously"

这一警告恰当。✅

### 8.4 Edmondson grade trend — 生物学合理（7.5/10）

**发现**：G1 (101.8) > G2 (100.2) > G3 (96.8) > G4 (90.0)，Jonckheere-Terpstra P < 0.001。

**生物学解释**： higher-grade tumors show lower ω (more convergence)。这与整体发现（肿瘤比正常组织更同质）一致——更高分级可能意味着更多趋同。

**注意点**：
- G1 到 G4 的差异仅为 ~12 units（101.8 → 90.0），相对于标准差（~50-64）较小
- P < 0.001 可能由大样本量驱动（n = 288）而非强效应
- G4 仅有 n = 11，稿件已警告 ✅
- 稿件未讨论 Edmondson grade 与 proliferation 的潜在混淆（与 PAM50 类似的问题）

---

## 9. ω 值的生物学解释

### 9.1 Bergmann glia ω=2.37 (最低) vs Astrocytes ω=14.36 (最高) — 生物学合理（9/10）

**6.06-fold gradient 的生物学论证**：

**Bergmann glia (ω = 2.37)**：
- 发育固定、转录约束状态 ✅
- 拓扑分子分区与 cerebellar functional compartments 对齐 (Reeber et al. 41) ✅
- 维持 Purkinje cell layer 架构，最小区域转录变异 ✅
- 仅 21 pairs across 7 regions（小样本，但 CI 在 Limitation Ninth 中讨论）

**Astrocytes (ω = 14.36)**：
- 表达区域特异性离子通道、神经递质转运蛋白、分泌因子 ✅
- 广泛文献支持星形胶质细胞区域异质性 ✅
- 5,778 pairs across 108 regions（大样本，估计精确）

**内部一致性**：Bergmann glia 是星形胶质细胞的特化亚型。将 Bergmann glia（低 ω）和 astrocytes（高 ω）置于同一梯度两端，展示了即使在星形胶质细胞谱系内，区域特化程度也变化巨大——这是一个有意义的生物学发现。✅

**ω_cal 解释**：
- Bergmann glia: ω_cal = 0.36（低于校准基线，表示强功能约束）
- Astrocytes: ω_cal = 2.15（高于校准基线，表示增强分歧）
- Brain global: ω_cal = 1.20

这一校准后的解释在生物学上合理：Bergmann glia 在脑区间的功能分歧低于基线预期（强约束），而 astrocytes 超过基线预期（增强分歧）。✅

### 9.2 CKI ω 与标准 metrics 负相关的生物学含义 — 解释恰当（8.5/10）

**发现**：CKI ω 与四种标准距离 metrics 负相关（Spearman r = -0.38 to -0.57, all P < 0.001）。

**生物学含义**：标准 metrics 测量绝对转录组距离，CKI 测量相对于基线的功能分歧。当标准 metrics 说两个群体"很远"时（高距离），CKI 可能说它们的功能分歧相对于基线"不高"（低 ω）——因为 k_n 也很高（基线变异大）。

**稿件解释**：
> "by down-weighting shared HK gene patterns, it trades some ability to detect global transcriptional identity for enhanced sensitivity to functional specialization"

这一解释准确。CKI 不是测量"细胞有多不同"，而是测量"功能分歧相对于基线有多大"——这是一个正交的生物学问题。✅

**same-organ > different-organ 的反转**：
> "CKI was the only metric where same-organ pairs had higher values than different-organ pairs (mean ω 24.87 vs. 20.80)"

这一反转反映 CKI 对共享微环境内功能特化的敏感性——同一器官内的不同细胞类型可能在功能基因上分化更多（因为它们在同一微环境中执行不同功能），而跨器官的相同细胞类型可能在功能基因上分化较少（因为它们执行相似功能但处于不同微环境）。这一解释在生物学上合理。✅

### 9.3 CKI AUC=0.716 作为非分类器 — 表述恰当（8.5/10）

**稿件表述**：
> "CKI is a divergence index, not a classifier—and this is by design. Classifying cell types from transcriptomic data is largely a solved problem. CKI answers a complementary question: regardless of cell-type labels, how much functional divergence separates two populations, relative to their shared baseline?"

**AUC = 0.716 的定位**：
- 高于 Spearman distance (0.690)
- 低于 Cosine distance (0.887)、Raw JS (0.836)、Marker Jaccard (0.801)
- 稿件明确承认 CKI "trades some ability to detect global transcriptional identity for enhanced sensitivity to functional specialization"

**评估**：AUC = 0.716 对于一个非分类器指标是可接受的，尤其是它提供了独特的可分解性（k_n 和 k_f 分量）。稿件的自我定位诚实且准确。✅

---

## 10. 方法比较的生物学意义

### 10.1 四种标准 metrics 与 CKI 的信息维度差异

标准 metrics（Cosine, Raw JS, Spearman, Jaccard）形成一个正相关集群（r = 0.57–0.95），CKI 与所有标准 metrics 负相关。这表明 CKI 捕获了一个与现有方法正交的信息维度。

**生物学意义**：标准 metrics 回答"这两个群体有多不同？"CKI 回答"这两个群体的功能分歧是否超出了基线预期？"前者是绝对距离，后者是相对分歧。在生物学上，后者更有意义——因为不是所有的表达差异都有功能意义（HK 基因的差异可能只是噪音）。

### 10.2 SAMap/SATURN/CACIMAR 比较

稿件明确声明"did not quantitatively benchmark CKI against these specialized methods, as they address different questions (cross-species alignment vs. within-species functional divergence)"。这一解释合理——CKI 的定位是种内功能分歧量化，不是跨物种对齐。✅

---

## 11. 新发现问题

### N1（Medium）: Abstract/Introduction 对脑分析结论过度解读

如第 7.1 节详述：
- Abstract 声称"four biological mechanisms"但仅 2/4 有统计支持
- Introduction 提到非显著的"colonization route boundaries"和"postnatal migration event"作为已检测信号
- Introduction 遗漏了有统计支持的"compartmentalized developmental specification"

**严重程度**：Medium。Results 和 Discussion 中的表述是准确的，但 Abstract/Introduction 是审稿人首先阅读的部分，过度解读会影响第一印象。

### N2（Medium）: Limitations 编号重复（N8 未完全修复）

如第 2 节详述：line 103 (First–Fifteenth) + line 104 (Eleventh, Twelfth 重复)。v25 的"两个 Seventh"变为"两个 Eleventh + 两个 Twelfth"。

### N3（Medium）: TCGA ω 尺度异常未讨论

如第 8.2 节详述：TCGA ω 值比单细胞数据高 12-43 倍，稿件未讨论原因。v25 E3 审稿已提出，v26 未修复。

### N4（Minor）: OPC 术语混用

如第 7.5 节详述："internal consistency check" (header, Supplementary) vs "orthogonal validation" (正文, Discussion)。v25 已指出，v26 未修复。

### N5（Minor）: 跨物种 Spearman r 值未在正文报告

Discussion (line 102) 仅说"moderately conserved"，未给出具体 Spearman r 值和 P 值。Supplementary Fig S2 legend 提到"with Spearman r and P-value"但正文未引用具体数值。v25 P2 建议，v26 未修复。

### N6（Minor）: Oligodendrocyte "distinguish" 措辞过强

Line 85: "the first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations without requiring lineage tracing"。CKI 检测的是低 ω 的空间模式匹配发育边界，而非直接区分单个细胞的背侧/腹侧身份。建议改为"detect the transcriptional boundary between dorsal and ventral oligodendrocyte populations"。

### N7（Minor）: Astrocyte thalamic heterogeneity 缺少直接引用

Line 87: "Regionalized astrogenesis, driven by subnucleus-specific transcriptional programs, has been shown to produce persistent thalamic astrocyte heterogeneity that is detectable in adult tissue" — 此句无具体引用。Endo et al. (18) 限于皮质，不直接支持丘脑。

### N8（Observation）: 四种机制分类为专家判断而非算法输出

机制分配 (DO/CR/DS/PM) 依赖于文献交叉验证而非定量标准。稿件在 Methods (line 35) 提到"Strong candidate signals were systematically cross-validated against the developmental neuroscience literature to assign each signal to one of four biological mechanisms"，但未明确声明这是专家判断。v25 E3 已指出，v26 未修改但 Methods 描述已隐含了这一性质。

---

## 12. v25 → v26 变更追踪

| v25 问题 | v26 状态 | 说明 |
|----------|:--------:|------|
| N1 (Supplementary "Selective") | ✅ 修复 | Cover Letter 使用 "Baseline-Normalized" |
| N2 (Cohen's d 残留) | ✅ 修复 | 全文无 "Cohen" 残留 |
| N3 (Table 1 数字 99/4,851) | ✅ 修复 | Table1-2.txt 为 102/5,151 |
| N4 ("neutral" 术语) | ✅ 修复 | 所有指代 k_n/HK 的 "neutral" 已改 |
| N5 (参考文献顺序) | — | 未在本审稿范围内验证 |
| N6 (Repro Guide brain k_n) | — | 未在本审稿范围内验证 |
| N7 (EVT GPD 诊断) | — | 属于 E1/E2 范围 |
| **N8 (Limitations 编号)** | ⚠️ **部分修复** | "Seventh" 重复消除，但引入新的 "Eleventh/Twelfth" 重复 |
| **N9 (Brain PMI)** | ✅ **修复** | 从 1 句扩展为完整段落 |
| E3-N3 (TCGA ω 尺度) | ❌ 未修复 | 仍无讨论 |
| E3-N6 (OPC 术语混用) | ❌ 未修复 | "internal consistency check" vs "orthogonal validation" |
| E3-N7 (四机制为专家判断) | ❌ 未修复 | 未明确声明 |

---

## 13. 评分明细

| 项目 | v25 评分 | v26 评分 | Δ | 说明 |
|------|----------|----------|---|------|
| N4 (neutral 术语清理) | 7/10 | 9.5/10 | +2.5 | 完全修复 |
| N8 (Limitations 编号) | 4/10 | 3/10 | -1 | 旧问题解决但引入新重复 |
| N9 (Brain PMI) | 4/10 | 8.5/10 | +4.5 | 充分扩展 |
| HK 基因选择 | 7/10 | 7/10 | 0 | 无变化 |
| 细胞类型鉴定可信度 | 7/10 | 7.5/10 | +0.5 | 小样本警告充分 |
| 四机制分类 | 7/10 | 6/10 | -1 | Abstract/Introduction 过度解读 |
| Oligodendrocyte 解释 | 8.5/10 | 7.5/10 | -1 | "distinguish" 措辞过强，概念张力未澄清 |
| Astrocyte VPL 解释 | 7.5/10 | 7/10 | -0.5 | 缺少直接引用 |
| Microglia 探索性表述 | 8.5/10 | 8.5/10 | 0 | 保持质量 |
| OPC internal consistency | 8.5/10 | 7.5/10 | -1 | 术语混用未修复 |
| TCGA confounder 讨论 | 9/10 | 9/10 | 0 | 保持质量 |
| TCGA ω 尺度讨论 | 4/10 | 4/10 | 0 | 仍未讨论 |
| ω gradient 生物学解释 | 8/10 | 9/10 | +1 | ω_cal 解释增强 |
| 方法比较生物学含义 | 8/10 | 8.5/10 | +0.5 | 解释清晰 |
| 新发现问题 | -1.5 | -2 | -0.5 | Abstract/Introduction 过度解读 + N8 新重复 |
| 跨物种比较 | 6/10 | 6/10 | 0 | 无变化 |

**综合评分：7.5/10**

---

## 14. 建议

### 发表前必须修复（P0）

1. **Abstract/Introduction 脑分析结论修正**（N1）：将"four biological mechanisms"限定为"four biological mechanisms (two reaching statistical significance)"；Introduction 中将"colonization route boundaries"和"postnatal migration event"标注为 exploratory，或仅提及有统计支持的机制。

2. **Limitations 编号修正**（N2）：将 line 104 的旧 Eleventh 和 Twelfth 合并入 line 103 现有条目，或重新编号为 Sixteenth 和 Seventeenth。

### 强烈建议修复（P1）

3. **TCGA ω 尺度讨论**（N3）：增加 1-2 句讨论 TCGA 中 ω 值异常高的原因（bulk averaging 压缩 k_n， inflated ω），建议跨数据集比较基于 rank 而非绝对值。

4. **OPC 术语统一**（N4）：统一 "internal consistency check" 和 "orthogonal validation"。

5. **Oligodendrocyte "distinguish" 措辞修正**（N6）：改为 "detect the transcriptional boundary between"。

### 建议改进（P2）

6. **Astrocyte thalamic heterogeneity 引用**（N7）：补充丘脑星形胶质细胞区域化的直接文献，或标注为推断。

7. **跨物种 Spearman r 值**（N5）：在正文中报告具体数值。

8. **HK 基因稳定化选择文献**：引用直接支持 HK 基因受纯化选择的文献。

9. **OPC 数学结构说明**：补充一句关于 ω ≈ grand mean 时残差行为预期的数学说明。

---

## 15. 总结

v26 在文档一致性方面有实质性进步：N4（neutral 术语）完全修复，N9（PMI 讨论）从 1 句扩展为完整段落，Table 1 数字统一，Cover Letter 标题统一，Cohen's d 清理完成。Limitations 从 ~12 条扩展至 15 条，多数内容质量高。

然而，v26 出现了两个抵消性负面发现：

1. **N8（Limitations 编号）未完全修复**：v25 的"两个 Seventh"变为"两个 Eleventh + 两个 Twelfth"，旧条目未整合。
2. **Abstract/Introduction 对脑分析的生物学过度解读**（新发现）：声称"四种生物机制"被识别，但仅 2/4 有统计支持；Introduction 提到非显著的"colonization route boundaries"和"postnatal migration event"作为已检测信号。

此外，v25 E3 审稿中提出的 TCGA ω 尺度异常（v25-N3）仍未讨论。

**与 v25（7.5/10）相比**：P0 修复（N4 术语 + N9 PMI + Table 1 统一）带来 +0.5 提升，但 N8 新重复（-0.5）和 Abstract/Introduction 过度解读（-0.5）抵消了这一提升。综合评分维持 7.5/10。

修复 P0 项（Abstract/Introduction 修正 + Limitations 编号修正）后预计评分可达 8.0/10。P0+P1 全部修复后预计 8.5/10。

**v26 评分：7.5/10** | v25: 7.5/10 | Δ: 0
