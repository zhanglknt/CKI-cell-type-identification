# CKI v33 独立审稿 — E3: 转录组学与单细胞应用

**审稿日期**: 2026-08-03
**评分**: 8.5/10 (v32: 8.2/10, Δ: +0.3)

---

## 1. 核心发现概要

v33 稿件在 v32 基础上进一步改善了生物学解释的精确性和透明度，17 项 v33 Minor 修复中与 E3 直接相关者（m6, m8, m12, m13, m14, m15, m17）多数得到有效执行。最核心的改进是：(1) 脑区非神经元细胞类型从 9 类扩展为 10 类（committed OPC 独立分类，m6）；(2) 非显著信号术语从 "Strong candidate signals" 修订为 "threshold-passing candidates"，仅将 16 个 P-value-floor 信号称为 "Strong signals"（m14）；(3) Abstract 中 "two statistically significant" 改为更严谨的 "two with permutation support"（m8）；(4) 新增 Limitation #21 明确脑区分析仅覆盖非神经元细胞（m15）；(5) "orthogonal" → "complementary"（m17）。

残留问题集中在两项修复执行不完全：(1) 跨物种 Spearman r 值仍未在正文中给出具体数值（m12 部分完成）；(2) TCGA k_n floor 的说明仍局限于 Discussion，未在 Results 首次报告高 ω 值时添加简注（m13 部分完成）。此外，L31 与 L74 在细胞类型 10 类的表述上存在细节不一致。所有问题均为 Minor，不影响投稿。

**Critical: 0, Major: 0, Minor: 4**

---

## 2. v32→v33 修复验证

### 2.1 v32 E3 Minor 问题追溯

| v32 编号 | 问题 | v33 状态 | v33 修复号 | 验证位置 |
|------|------|:---:|------|------|
| Minor 1 | 跨物种 r 值缺失 | ⚠️ 部分修复 | m12 | L98: 仍仅 "moderately conserved"，未给出具体 r 值 |
| Minor 2 | TCGA Results 缺 k_n floor | ⚠️ 部分修复 | m13 | Discussion L97 有解释，但 Results L64–66 仍无简注 |
| Minor 3 | "Strong candidate" 术语歧义 | ✅ 已修复 | m14 | L91/98: 非显著信号改称 "threshold-passing candidates" |
| Minor 4 | Cover Letter 30 信号表述 | ✅ 可能修复 | m3 | MANIFEST 确认 "30 threshold-passing candidates (16 significant)" |
| Minor 5 | 非神经元 scope limitation | ✅ 已修复 | m15 | L101: Limitation #21 新增 |

### 2.2 m6: 脑区细胞类型 9→10 — ✅ 已修复

**修复位置**: L74。

v32 脑区分析仅 9 类非神经元细胞。v33 将 committed oligodendrocyte precursors 提升为独立类别，使总数达到 10 类：
> "10 major cell classes (astrocytes, oligodendrocytes, oligodendrocyte precursors, microglia, vascular cells, fibroblasts, ependymal cells, choroid plexus, committed oligodendrocyte precursors, and Bergmann glia)."

**生物学意义**: 成熟 OPCs 与 committed OPCs 代表 oligodendrocyte lineage 的两个不同分化阶段（progenitor vs. committed differentiation），其转录程序存在实质性差异（committed OPCs 开始表达成熟髓鞘基因但尚未形成完整髓鞘结构）。独立分类允许读者分别评估两个阶段对 brain regional fidelity 的行为，生物学上更合理。

**残留细节不一致**: L31 对数据集描述仍沿用 "oligodendrocyte precursors (110,454 total including committed)" 的合并表述，与 L74 的 10 类独立分类不一致。建议统一 L31 的计数表述（见 4.2 新发现问题）。

### 2.3 m8: Abstract 措辞修订 — ✅ 已修复

**修复位置**: L11。

Abstract 从 "two statistically significant" 改为：
> "two with permutation support"

**评估**: 这一修订精确反映了实际情况——16 个 Strong signals 达到的是 permutation P-value floor（B=10,000 分辨率下的 9.99 × 10⁻⁵），而非传统意义上的 "statistically significant"（后者隐含 FDR 或 family-wise error rate 校正，但 36.3% 的 P-value floor saturation 使 FDR 不可用）。"With permutation support" 准确传递了证据强度而不夸大。

### 2.4 m14: "Strong candidate" 术语精确化 — ✅ 已修复

**修复位置**: L91、L98。

v32 将 P≥0.76 的 14 个信号仍称为 "Strong candidate signals"，v32 E3 Minor 3 指出 "Strong" 一词暗示可靠性，可能误导读者。v33 的改进体现在两个层面：

(1) **独立小节标题**保持不变 "Threshold-passing but non-significant signals"（L91）。
(2) **Discussion 综述**（L98）将术语分化为两套：
   - 16 个 P-value-floor 信号 → 保留 "Strong signals"
   - 14 个 P≥0.76 信号 → 改称 "the 14 remaining threshold-passing candidates... were non-significant"

这种分化是精确的：只有 permutation 确认的信号才使用 "Strong"，其余仅标注为阈值通过。相较于 v32 在同一段落中混用 "Strong" 指代全部 30 个信号的做法，v33 实现了术语层面的清晰区分。MANIFEST 中 m3 的 Cover Letter 同步修正 "30 threshold-passing candidates (16 significant)" 与正文一致。

**仍可改进**: L91 段内描述仍存在 "threshold-passing Strong candidate signals" 的混合短语，虽已加 "threshold-passing but non-significant" 限定，但 "Strong" 一词的出现仍不理想。

### 2.5 m15: 非神经元 scope limitation — ✅ 已修复

**修复位置**: L101 (Limitation #21)。

v32 E3 Minor 5 建议在 Limitations 中补充脑区分析仅覆盖非神经元细胞的范围限制。v33 新增 Limitation #21：
> "Twenty-first, the brain analysis was restricted to non-neuronal cell types because the supercluster_term annotation does not resolve neuronal subtype heterogeneity; this limits the generalizability of our brain regional findings to non-neuronal lineages and should be noted when interpreting the scope of our cross-region analysis."

神经元占脑细胞 50% 以上，其区域发育标记模式可能与胶质/结构细胞存在本质差异（如皮层 laminar specification、长程投射 neuron subtype、区域特异性 interneuron）。CKI 框架原则上可应用于神经元（前提是 subtype 注释完整），但当前分析无法提供神经元的发育签名信息。此 limitation 的加入提高了稿件科学诚实度。

### 2.6 m17: "orthogonal" → "complementary" — ✅ 已修复

**修复位置**: L98。

> "providing a notable **complementary** validation that the residual model specifically detects fixed developmental signatures rather than ongoing cell motility."

v32 使用 "orthogonal validation" 描述 OPC 0/5,671 的 internal consistency check。"Orthogonal" 暗示 OPC 行为与已有结论完全独立/无相关，但 OPC 分析实际是对同一 residual model 框架的验证性检查——若模型正确，OPC 应产生 0 Strong signals（因为 OPC 的持续迁移不留下固定发育签名）。"Complementary" 更准确地表达了这种相互印证的逻辑关系。

### 2.7 m2: CV 校准 — ✅ 已修复

**修复位置**: L52。

> "mean ω was 6.67 (median 6.46, range 1.59–12.16, CV ≈ 52%)"

v32 中 CV≈60%，v33 修正为 52%。虽为 Minor，但精确度提升反映了对校准不确定性的诚实量化。

### 2.8 m12: 跨物种 Spearman r 值 — ⚠️ 部分修复

**修复位置**: L98。

v32 E3 Minor 1 是 v32 中 E3 最重要的残留问题——跨物种验证是 CKI 方法泛化性的关键证据，但正文仅用 "moderately conserved" 定性描述，未提供定量 r 值。读者必须查阅 Supplementary Fig. S2 才能获取定量信息。

v33 L98 仍为：
> "ω rankings are moderately conserved between mouse and human for shared cell types, though absolute ω values differ due to different computation schemes."

**未见具体 Spearman r 值**。MANIFEST 标注 m12 为已修复（"Cross-species Spearman r referenced in Discussion"），但从文件证据来看，具体的 r 值（如 "Spearman r = 0.XX, P = 0.0XX"）并未出现在正文 Discussion 或 Results 中。

**建议**: 在 Discussion L98 跨物种验证段添加具体 r 值，或在 Results "CKI captures information that standard metrics miss" 段末概述跨物种结果。这是支持方法泛化性的最简单也最重要的量化证据，不应仅存于 Supplementary。

**评估**: 此问题在 v32 中评为 Minor 1（最高优先级 Minor），v33 未完全修复，但考虑到跨物种验证框架已在 Supplementary Fig. S2 中存在，且 L98 已提及该图引用，不会导致误解——只是使关键定量信息对只看正文的读者不可见。

### 2.9 m13: TCGA k_n floor 在 Results 中的呈现 — ⚠️ 部分修复

v32 E3 Minor 2 要求在 TCGA Results 段（L64–66）首次报告高 ω 值时添加简短 k_n floor 注释。

v33 的 Discussion L97 对 k_n floor 问题有完整解释：
> "in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴, compared to mean k_n of 0.048–0.073 in single-cell datasets"

但 TCGA Results 段（L64–66）的表述仍与 v32 相同，未添加简注。读者在 Results 中看到 BRCA Luminal A ω≈344.5 时，仍需翻到 Discussion 才能理解这是 k_n floor 导致的膨胀。

**建议**: 在 L66 "Luminal A tumors had the highest intratumoral ω (344.5 ± 323.4, n = 224)" 后添加括号注释，如 "(note: bulk-level ω values are upward-shifted by k_n floor effects; see Discussion)"。

**评估**: 与 m12 类似，问题不在结论本身（Discussion 已有完整解释），而在信息呈现顺序——读者在 Results 中缺乏理解 ω 绝对值的必要语境。不影响投稿，但建议 response letter 中完成。

---

## 3. 生物学解释质量评估

### 3.1 16 Strong signals 解释框架

v33 保持了 v32 的四机制框架，在生物学解释上更加精确：

| 机制 | 涉及细胞类型 | Signals | 统计学状态 | 实验证据支持 |
|------|------|:---:|:---:|------|
| Developmental origin heterogeneity | Oligodendrocytes | 10/10 | P-value floor | Foerster et al. (27) 背侧/腹侧 lineage ablation |
| Compartmentalized developmental specification | Astrocytes | 6/6 | P-value floor | Endo et al. (29) Tcf4 astrogenesis |
| Embryonic colonization route boundaries | Microglia | — | 探索性 | 文献支持存在，但当前数据 P≥0.76 |
| Postnatal cell migration | — | — | 探索性 | 无 permutation 支持的信号 |

**评估**: 16 个达到 P-value floor 的信号（6 astrocytes + 10 oligodendrocytes）均映射到前两个机制，且两个机制均有独立的实验文献支持。10 个 oligodendrocyte 信号全部涉及 cortex vs. thalamus/brainstem 配对——这恰好是 Foerster et al. 背侧/腹侧 oligodendrocyte 起源的解剖边界。6 个 astrocyte 信号集中于 thalamic subnuclei（VPL 出现于 4/6）和 hippocampal subfields——这与 Endo et al. 的 compartmentalized astrogenesis 一致。

v33 在技术层面做了重要补充：将所有 10 个 oligodendrocyte cortex→thalamus 配对关联到 LP/Pul 核团，并与 Brodmann 区 A13–A40 形成对比（L85）。这一解剖精度使 dorsal/ventral origin 的生物学论证更有说服力。

**Permutation 检验的局限性已充分声明**: L81 明确 "formal FDR correction is not applicable" 和 "the 16 floor-reaching signals are interpreted as descriptive evidence rather than FDR-controlled discoveries"。L98 Discussion 重复此限定。L100 Limitation #16 和 Limitation #19 进一步讨论 P-value floor saturation 的两种解释（有限的 permutation resolution vs. 真实效应）。这种多层级的 caveat 部署是值得肯定的科学实践。

### 3.2 细胞类型生物学评估

#### Astrocytes (ω=14.36, 最高)
区域差异性最高（6.06-fold over Bergmann glia），符合其在 synaptic microenvironment 中功能性特化的已知生物学。Thalamic subnuclei（VPL 主导）和 hippocampal subfields 的 astrocyte 信号，与 compartmentalized astrogenesis 模型一致。稿件通过 Endo et al. (29) 的 Tcf4 研究建立了机制连接。

#### Oligodendrocytes (ω=8.66, 中等)
所有 10 个 Strong signals 均与成熟 oligodendrocyte 的 dorsal/ventral 发育起源相关——而非 active migration。稿件引用 Foerster et al. (27) 的 lineage ablation 实验有力支持这一重新解释：>90% 皮质 oligodendrocytes 为背侧来源，而丘脑/brainstem oligodendrocytes 为腹侧来源。CKI 捕捉到的低 ω 反映的是 shared generic myelination programs，而非区域特化。

**v33 改进**: 通过将全部 10 对映射到 LP/Pul 丘脑核团，增强了生物学论证的解剖特异性。

#### Oligodendrocyte Precursors (OPC, ω=7.65)
OPC 0/5,671 Strong signals 作为 internal consistency check 的论证在 v33 中更精确——从 "orthogonal validation"（v32）改为 "complementary validation"（v33, L98），更准确地表达了同一框架内的印证关系。

#### Committed Oligodendrocyte Precursors (NEW in v33)
v33 新增的独立类别。ω=3.17 ± 1.47，低分化度仅次于 Bergmann glia。这种低 ω 可能与 committed OPCs 的转录约束状态相符——它们已 commit 到 myelination lineage 但未完成最终成熟，区域间转录差异较小。该类别仅有 1,326 对比较（52 regions），数量有限。

#### Bergmann Glia (ω=2.37, 最低)
发育固定、转录约束、0 Strong signals——与 v32 一致。L89 的小节 "Bergmann glia: cerebellar molecular topography" 继续准确描述其生物学角色。

#### Microglia (ω=8.02, 中等)
10 threshold-passing candidates，全部 P≥0.76。v33 保持 v32 的谨慎立场：这些信号 "should not be interpreted as evidence of biological structure"（L91）。从生物学角度，microglia 的区域表型变异已被广泛描述（Grabert et al., 2016; De Biase et al., 2017），CKI 未检测到 permutation 支持的信号可能反映了 microglial regional heterogeneity 的转录组特征在 adult stage 弱于 astrocyte 的区域特化，或其变异模式不易被 multiplicative residual model 捕获。

#### Vascular Cells / Fibroblasts / Ependymal / Choroid Plexus
低分化度、低 Strong signals，与结构细胞预期一致。Vascular cells (3) 和 fibroblast (1) 的 threshold-passing 信号均不显著（P≥0.76）。

### 3.3 TCGA 生物学解释

v33 保持 v32 的 TCGA 探索性定位，整体评估不变：

**NN/TT > 1.0**: 五癌种一致观察到 normals 比 tumors 更异质（NN/TT 比率 1.40–2.83），但 bulk resolution 的三重 confound（cell composition, peritumoral inflammation, RNA quality）限制了结论的生物学强度。

**PAM50 梯度**: LumA > LumB > HER2 > Basal-like > Normal-like 的 ω 递减（344.5 → 313.6 → 263.0 → 223.4 → 108.0）已被 manuscript 正确警示 "proliferation confound"（L66: "the PAM50 gradient may partly reflect proliferative fraction differences"）。生物学上，增殖信号在 bulk RNA-seq 中的压倒性贡献是已知问题——Basal-like 肿瘤的高增殖率可能导致大量细胞周期基因被视为 "identity genes"，压缩 k_f 敏感性。

**Paired analysis**: 已降级为 descriptive statistics without P-values（L65），v32 的改进在 v33 中保留。

**v33 局限性**: v32 E3 Minor 2 要求的 TCGA Results k_n floor 简注仍未添加（见 2.9）。但 Discussion L97 的完整解释已可满足投稿要求。

### 3.4 跨器官排序生物学合理性

Tabula Sapiens 跨器官排序（Table 2）从 v32 继承，评估不变：

- **高保守性**（低 ω）：B cells (2.70), Neutrophils (2.72), Smooth muscle (6.29) — 符合预期：循环免疫细胞和 contractile 细胞类型的核心程序跨器官保守
- **中等**: Macrophages (9.84, n=15) — 最充足的样本量，macrophage tissue-resident 程序的器官特异性与中等 ω 吻合
- **高器官特异性**（高 ω）：Endothelial cells (15.09), Memory B cells (16.83) — EC 的器官特异性血管程序（如肝脏 fenestrated vs. BBB tight junction）被充分文献化

**样本量 caution**: 多数细胞类型 n=1–3，正确标注为 "suggestive only"。此 caveat 从 v32 继承。

---

## 4. 新发现问题

### Minor N-E3-1: L31 与 L74 细胞类型计数表述不一致

**位置**: L31 vs. L74。

**问题**: L31 对 brain dataset 的描述列出 9 个命名条目：
> "10 major non-neuronal classes: astrocytes, oligodendrocytes, oligodendrocyte precursors (110,454 total including committed), microglia, vascular cells, fibroblasts, ependymal cells, choroid plexus, and Bergmann glia."

"Oligodendrocyte precursors (110,454 total including committed)" 将 OPC 和 committed OPC 合并为一个条目并合并核计数。然而 L74 将二者列为两个独立类别（达到 10 类计数）。读者在 L31 只能数出 9 个命名类别，与 "10 major non-neuronal classes" 矛盾。虽然 "including committed" 括号暗示第二类别，但表述不清晰。

**建议**: L31 修改为 "oligodendrocyte precursors (xxx nuclei) and committed oligodendrocyte precursors (xxx nuclei, included in the total of 110,454)" 或类似清晰表述，使 L31 可直接数出 10 个类别。

### Minor N-E3-2: 跨物种验证框无量化信息（延续 v32 Minor 1）

**位置**: L98。

v33 中 m12 标注为 "Cross-species Spearman r referenced in Discussion"，但正文仍仅用 "moderately conserved" 定性描述。对支持 CKI 方法泛化性最关键的一个数据点——mouse-human ω ranking 的 Spearman r——仍然在正文中不可见。读者需要查阅 Supplementary Fig. S2。

**影响**: 不影响投稿，但使正文中跨物种证据的呈现强度不足。

**建议**: 在 L98 跨物种验证句中补充具体 r 值（如 "Spearman r = 0.XX, P = 0.0XX; Supplementary Fig. S2"），或在 Results 段添加一句跨物种结果概述。

### Minor N-E3-3: TCGA Results k_n floor 解释位置（延续 v32 Minor 2）

**位置**: L64–66 vs. L97。

与 N-E3-2 类似，是 v32 残留问题的延续。TCGA ω 值极高（BRCA Luminal A ω≈344.5）的原因——k_n floor at 1 × 10⁻⁴——在 Discussion L97 有完整解释，但 Results L64–66 首次报告时无简注。

**建议**: 在 Results 首次提及 TCGA ω 绝对值处添加简短括号注。

### Minor N-E3-4: Calibration ω=6.67 CV 准确性

**位置**: L52。

v33 修正了 CV 从 60% 至 52%（m2）。52% 基于 6 个 split-half controls (1.59–12.16, mean 6.67)。CV≈52% 对于 n=6 的校准样本意味着：ω_cal 的 95% 置信区间宽度跨越 ~3.5-fold（[4.12, 9.33]），而非 traditional 95%-CI-for-the-mean 的狭窄范围。L52 的 bootstrap CI [4.12, 9.33] 和 L100 Limitation #17 的详细讨论已充分量化了这种不确定性。

**无 action needed**: 稿件已通过 bootstrap CI 和 Limitation #17 充分处理。

---

## 5. 问题汇总

### 5.1 v32 残留问题（v33 中部分修复）

| 编号 | 严重程度 | 问题 | 位置 | v33 状态 |
|------|:---:|------|------|:---:|
| m12 | Minor | 正文缺跨物种 Spearman r 值 | L98 | 仍仅 "moderately conserved"，无具体 r |
| m13 | Minor | TCGA Results 缺 k_n floor 简注 | L64–66 | Discussion L97 有完整解释，Results 无 |

### 5.2 v33 新发现

| 编号 | 严重程度 | 问题 | 位置 |
|------|:---:|------|------|
| N-E3-1 | Minor | L31 10 类计数表述与 L74 不一致 | L31 vs. L74 |
| N-E3-2 | Minor | 跨物种验证正文无量化（即 m12 残留） | L98 |
| N-E3-3 | Minor | TCGA k_n floor 仍仅见 Discussion（即 m13 残留） | L64–66 |
| N-E3-4 | — | Calibration CV 修正已确认 (52%) | L52 |

### 5.3 v33 确认修复

| 编号 | 修复内容 | 状态 |
|------|------|:---:|
| m2 | CV 60% → 52% | ✅ |
| m3 | Cover Letter 30 signatures 表述 | ✅ (MANIFEST 确认) |
| m6 | 脑区细胞类型 9→10 (committed OPC) | ✅ |
| m8 | Abstract "two with permutation support" | ✅ |
| m14 | "threshold-passing candidates" 术语分化 | ✅ |
| m15 | Limitation #21 非神经元 scope | ✅ |
| m17 | "orthogonal" → "complementary" | ✅ |

---

## 6. 评分理由

### 6.1 评分明细

| 维度 | v32 评分 | v33 评分 | Δ | 说明 |
|------|:---:|:---:|:---:|------|
| 1. 生物学解释合理性 | 8.5 | 8.8 | +0.3 | committed OPC 独立分类提升 lineage 解释精度；非显著信号术语分化提升解释谨慎度；Abstract 措辞更精确 |
| 2. 数据集代表性 | 7.8 | 8.0 | +0.2 | Limitation #21 新增 non-neuronal scope；L31 计数仍有细节不一致但已改善 |
| 3. 跨物种验证 | 7.5 | 7.8 | +0.3 | m12 部分改善（框架已在 Discussion 引用），虽具体 r 值仍缺但引用链完整 |
| 4. 局限性诚实度 | 9.0 | 9.3 | +0.3 | 新增 #18–#21 四项 Limitations；P-value floor dual interpretation；scope limitation |

**综合评分**: (8.8 + 8.0 + 7.8 + 9.3) / 4 = **8.475 → 8.5/10**

### 6.2 评分变化解释

v32→v33 Δ=+0.3 的提升来自三个方面的改进：

1. **细胞类型分类精度提升** (+0.15)：m6 将 committed OPC 独立为第 10 类，使 brain analysis 的 cell-type resolution 更贴近 oligodendrocyte lineage 的生物学实际——成熟 OPC 与 committed precursor 处于不同分化阶段，转录程序不可混淆。这一改进虽小但直接提升了脑区分析的生物学可信度。

2. **统计学语言精确度提升** (+0.10)：m8 ("with permutation support" 替代 "statistically significant")、m14 (非显著信号 "threshold-passing candidates" 替代 "Strong candidate signals")、m17 ("complementary" 替代 "orthogonal") 三项术语修正共同使稿件的统计学解释更加审慎精确。v32 已在此维度表现良好，v33 是渐进性优化。

3. **局限性覆盖度扩展** (+0.05)：Limitation #18 (one-sided test)、#19 (P-value floor alternative)、#20 (circularity concern) 和 #21 (non-neuronal scope) 的加入，使 Limitations 从 v32 的 17 项扩展到 v33 的 21+ 项，体现了在回应审稿过程中的持续自我批评。

### 6.3 为什么只加了 0.3 而非更多

v32 评分 8.2/10 在生物学维度上已是高基准——稿件在 v32 解决了 E3 的 4 个 Major 和 6 个 Minor 问题，v33 的改进空间主要为 Minor 级别的渐进完善。v33 的 17 项 Minor 修复中，与 E3 相关的 7 项多数为术语精确化（m8, m14, m17）和细节完善（m6, m15），不涉及对生物学校心发现的修正。两个部分修复（m12, m13）延续了 v32 的 Minor 问题，限制了提升幅度。此外，跨物种验证——作为方法泛化性的关键证据——仍是全文生物学维度最薄弱的一环，在正文中的呈现质量限制了更高评分。

### 6.4 提交建议

**推荐行动**: v33 已达到 NAR 投稿标准，E3 维度无 Critical 或 Major 问题。4 项 Minor 问题（2 项 v32 残留 + 2 项 v33 新发现）均不阻塞投稿。

**Desk reject 风险（E3 维度）**: 极低。

**Revision 建议（优先级排序）**:
1. (N-E3-2, 即 m12) 在 L98 跨物种验证句中嵌入具体 Spearman r 值
2. (N-E3-3, 即 m13) 在 L64–66 TCGA Results 首次报告高 ω 值处添加 k_n floor 简注
3. (N-E3-1) 统一 L31 细胞类型计数表述，使其可直接数出 10 类
4. (m14 残余) L91 段内 "threshold-passing Strong candidate signals" 可进一步改为 "threshold-passing candidates"

### 6.5 总体评价

v33 稿件在生物学解释方面保持了 v32 的高水准并实现了有限但精准的提升。最值得肯定的是 (1) 非显著信号的 "Strong" 标签撤除——v32 最大的 E3 遗留问题得到了有效解决；(2) committed OPC 独立分类——虽为 Minor 修改但提升了 lineage-specific 解释的精确度；(3) 四项新 Limitations 的加入——Limitation #21（non-neuronal scope）直接回应了 v32 E3 Minor 5，Limitation #20（circularity concern in per-pair k_f）展现了对方法内在限制的深刻理解。

跨物种验证在正文中的呈现不足仍是全文生物学维度最显著的薄弱环节。但 Supplementary Fig. S2 已提供了量化证据框架，此问题不影响投稿决定。

稿件最精彩的生物学论证——OPC 0/5,671 作为 "complementary validation" 证明 residual model 检测 fixed developmental signatures 而非 ongoing motility——在 v33 中得以保留并术语精确化。这一论证是 CKI 脑区分析生物学合理性的核心支柱。

---

**Critical: 0, Major: 0, Minor: 4**
