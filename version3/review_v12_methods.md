# 方法学审稿报告 — CKI v12

**审稿人**：计算生物学/生物信息学方向，专长单细胞分析方法开发与评估
**审稿日期**：2026年7月26日
**审稿范围**：稿件全文、投稿信、补充材料、复现指南

---

## 评分: 6/10

---

## 1. Critical Issues（阻断发表的问题）

### 1.1 归一化策略的文档不一致（Critical）

CKI的核心计算涉及将表达向量转换为概率分布，但三份文档对该步骤的描述相互矛盾：

- **稿件正文（Materials and Methods）**声称：非负单细胞数据使用sum-normalization（`p_i = x_i / Σx_j`），TCGA数据使用softmax。
- **补充材料（Supplementary Note 1.1）**声称："Before CKI computation, **softmax normalization is applied** to convert raw expression vectors into probability distributions: softmax(x)_i = exp(x_i)/Σexp(x_j)." 此处明确说在所有情况下使用softmax。
- **复现指南（Section 2）**才揭示实际实现是"auto mode"：根据数据范围自动选择sum-normalization（非负值）或softmax（负值）。

这是一个严重的方法论文档化问题。审稿人和读者无法仅凭稿件正文确定CKI实际使用的归一化方法。更重要的是，sum-normalization和softmax在数学上不等价——前者保持相对比例但受零值影响大，后者通过指数变换放大表达差异。尽管复现指南声称"auto-switching behavior is an implementation detail that has no substantive effect on the results"，但没有提供分析证明这一点，仅引用了一个未在稿中展示的"Supplementary Figure 1"。

**建议**：必须在Methods中明确说明实际使用的归一化策略（auto-detection机制），并提供不同归一化方法对ω值影响的定量敏感性分析（如Bland-Altman图或归一化方法间ω的相关性分析）。

### 1.2 完全缺乏多重检验校正（Critical）

稿件在 **Statistical Reporting** 部分明确承认："For human, TCGA, and brain primary analyses, standard statistical tests were applied **without multiple-testing correction**; all reported P-values are raw, uncorrected values."

但分析规模极大：
- Tabula Sapiens：4,851对比较
- 人脑区域分析：31,764对比较
- TCGA：最多10,000 × 5对比较

在如此大规模的比较中不进行任何多重检验校正（FDR/Bonferroni），意味着大量报告的"显著"结果极可能是假阳性。稿件声称"Effect sizes (Cohen's d) are consistently large (typically d > 1.0)"作为补充证据——但对于人类和TCGA分析，稿件明确声明"Bootstrap (human) = N/A"、"Bootstrap (TCGA) = N/A"，即根本没有进行bootstrap检验，因此也没有Cohen's d可报告。这是一个前后矛盾的陈述。

具体而言：
- 稿件正文中报告"P < 0.001"却未标注是否经过校正
- 复现指南Section 5.2直言："FDR correction (Benjamini-Hochberg, q < 0.05) was intended for multi-pair comparisons but was **not systematically implemented** in the analysis pipeline"
- 补充材料Section 3.3同样确认："Note: **Benjamini-Hochberg FDR correction is NOT systematically applied** in the current analyses"

**建议**：必须对所有多对比较应用Benjamini-Hochberg FDR校正，并报告经校正后仍然显著的ω结果。如果校正后大部分结果不再显著，稿件的核心结论需要重新评估。

### 1.3 dN/dS类比的核心数学缺陷（Critical）

稿件将CKI与分子进化中的Ka/Ks比值进行类比，声称二者共享"使用内参基线"的逻辑。但稿件自身的Discussion段落（第185行附近）诚实地指出：

> "The Ka/Ks ratio derives its theoretical power from a **shared mutation rate (μ) that cancels in the ratio** (Ka/Ks = f(N_e, s)), leaving a pure signal of selection; CKI **lacks an analogous cancellation mechanism**."

这意味着Ka/Ks的比例解释力来自于分子钟假设下共享的突变率μ在比值中抵消——但CKI的k_n和k_f是在**不同的基因集**（HK基因 vs. 身份基因集）上计算的，二者没有共享的"速率常数"可以抵消。因此：

1. ω = k_f/k_n 的绝对值没有分子进化中的理论含义（ω=1不映射到中性进化）
2. 稿件自身的校准实验显示实测基线ω = 1.54而非理论ω = 1，且TOST等价性检验在n=6的小样本下未能确认严格等价性
3. 稿件承认这是"启发式的"（heuristic），但全文（包括标题、摘要、图形摘要）都在使用进化学术语（"selection"、"neutral"、"constraint"），容易误导读者认为CKI具有进化学机制解释

**建议**：降低Ka/Ks类比的语言强度，特别是在摘要和引言中。明确将CKI定位为一个"基线归一化的差异度量"（baseline-normalized divergence metric），而非"选择指数"。删除或修改使用进化学术语的断言性语句。

---

## 2. Major Issues（需要重大修改）

### 2.1 Per-pair身份基因选择破坏了ω的可比性（Major）

CKI的混合方案（hybrid scheme）中：
- k_n使用全局共享的HK基因集
- **k_f使用per-pair的top-200差异表达基因**

这意味着对于不同的细胞类型对(A,B)和(C,D)，ω(A,B)和ω(C,D)的k_f基于完全不同的基因集。这使得跨对比的ω值无法直接比较，因为高ω可能反映：
- （a）真正的功能差异大，或
- （b）被选中的200个基因恰好包含对该对比特别敏感的基因

这是CKI方法设计中一个根本性的内在缺陷。稿件在Discussion中提到："when cosine distance is restricted to the same 200 DE genes, its AUC drops to 0.752"——这恰好说明per-pair基因选择对结果有显著影响。

**建议**：至少提供一种"固定基因集"模式的CKI结果作为敏感性分析（例如对所有比较使用全局HVG集合的k_f），展示固定基因集与per-pair方案的ω值之间的一致性程度。

### 2.2 Bootstrap参数B=500不足（Major）

稿件在Permutation Test部分使用B=500作为bootstrap的迭代次数，且仅在小鼠标定实验中使用。考虑到：
- 经验P值的精度受限于1/(B+1)，B=500时最小可检测的P值为~0.002
- 两阶段检验（two-sided test with H0: ω=1）需要更多的排列来稳定尾部估计
- 现代生物信息学的标准做法是B≥1,000（稿件自身的Algorithm Pseudocode中默认B=1000，但实际使用500）
- 补充材料Section 3.2声称"Bootstrap iterations: B=1,000 for all primary results"——但这与稿件正文和复现指南矛盾，后者明确说人类/TCGA/脑分析不使用bootstrap

**建议**：对所有使用bootstrap的分析统一使用B≥1,000，并确保文档间对bootstrap参数和使用范围描述一致。

### 2.3 k_n的值域稳定性问题（Major）

ω = k_f/k_n 作为比值度量，当k_n非常小时会产生严重的数值不稳定。稿件自身报告：
- 小鼠数据：k_n中位数0.0019，范围0.0006-0.0027
- 人类数据：k_n中位数0.034，范围0.0018-0.221

这意味着某些对比中k_n可以低至0.0006——此时即使k_f的微小波动也会导致ω的巨大变化。例如k_n=0.001，k_f从0.01变为0.02，ω从10变为20。稿件虽然提到"ω capped at 1,000"和"recommend reporting ω with a lower-bound k_n threshold"，但没有系统性地分析k_n < 0.001的对比占多大比例，也没有演示这些极端对比在过滤前后对结论的影响。

**建议**：提供k_n值分布的分位数表和过滤阈值敏感性分析，评估不同k_n截断值对主要结论（如脑区域分析的30个Strong信号）的影响。

### 2.4 乘法残差模型阈值的理论基础薄弱（Major）

脑区域分析的乘法残差模型中，Strong/Moderate/Weak的阈值设定为：
- Strong: residual < 0.3, ω < 15, "lowest ω in the region pair"
- Moderate: residual < 0.5, ω < 25
- Weak: residual < 0.75, ω < 35

这些阈值至少包含三类问题：

1. **阈值是数据驱动的而非理论驱动的**：residual < 0.3对应于经验分布的~1st百分位（剩余值≈0.40），而非来自正式的零分布推导。稿件尝试permutation-based阈值作为敏感性分析，但报告二者"yielded qualitatively consistent but not identical cutoffs"——这意味着permutation验证并不完全支持所选参数。

2. **多条件叠加减少了可解释性**：Strong信号要求同时满足residual < 0.3 AND ω < 15 AND "lowest ω in the region pair" AND "pair median ω > 20"（复现指南额外条件）。这些条件的组合使得模型变成一个存在多个自由度的判别规则，而不是一个单一的统计检验。

3. **判断标准的透明度不足**：Strong信号的最后一个条件（"lowest ω in the region pair"和"pair median ω > 20"）仅在复现指南中出现，未在稿件正文中描述。

**建议**：建立基于排列检验的正式零分布来确定残差阈值；将所有判别条件统一在正文中明确报告；展示不同阈值选择下Strong信号的稳定性。

### 2.5 方法比较不够全面（Major）

稿件将CKI与四种标准距离度量（原始JS散度、Spearman距离、余弦距离、Jaccard距离）进行了比较。这一比较有价值，但存在以下问题：

1. **比较对象不是同类方法**：CKI声称是一种"选择性重塑指数"，而非距离度量或分类器。将CKI与距离度量在细胞类型AUC上比较是类别错配的。稿件承认"AUC comparison is not strictly like-for-like"并解释"CKI is explicitly designed as a perturbation index, not a classifier"——但如果CKI不应作为分类器评估，那么报告AUC并声称"below cosine distance"有何意义？

2. **未与最相关的方法比较**：SAMap（跨物种对齐）、SATURN（通用细胞嵌入）、CACIMAR（保守性评分）与CKI的生物学问题更为接近，但稿件Discussion中明确说"Quantitative benchmarking against task-specific methods was beyond our scope"。Cover letter声称CKI提供了这些方法没有的功能，但如果不进行定量比较，这一声称缺乏实证支持。

3. **200基因vs全基因集的不公平比较**：CKI仅用200个基因，而余弦距离默认使用~20,000个基因。稿件承认当余弦距离同样限制在200个基因时，AUC下降至0.752（仍高于CKI的0.716），但这一分析仅作为一句话提及，没有系统性地在不同基因集大小下比较。

**建议**：要么将CKI与更相关的方法（如CACIMAR的保守性评分）进行基准比较，要么在讨论中更明确地限定当前比较的局限性，避免让读者误以为CKI已被充分基准化。

---

## 3. Minor Issues（建议修改）

### 3.1 JS散度的对数底数不一致

稿件正文声明"JS divergence uses the **natural logarithm**"，补充材料则讨论"when using **base-2 logarithms**, the JS divergence is bounded in [0, 1]"。如果实际使用自然对数（如复现指南代码所示：`ln(P_i / M_i)`），则JS散度的理论上界为ln(2)≈0.693而非1。补充材料关于JS∈[0,1]的声明与实际实现不匹配，应修正文档或代码。

### 3.2 Bootstrap零分布的epsilon差异

复现指南Section 5.1披露：小鼠bootstrap零分布使用`omega_null = kf_null / (kn_null + 1e-9)`（添加epsilon防止除零），而CKI核心函数使用`omega = kf / kn`（无epsilon，kn=0 → ω=∞）。这一实现细节差异在文档中已诚实披露，但应说明1e-9的实际影响量级（在真实数据中kn_null ≫ 1e-9，影响可忽略）。

### 3.3 被排除的分析脚本需要解释

复现指南Section 3.3列出了多个被排除的脚本：
- `01_pilot_mouse.py`、`02_ct_pilot.py`——"early designs, replaced"
- `04_phase32_sweep.py`——"depends on live MSigDB download and cannot be exactly reproduced"
- `05_phase33_v2.py`、`05_phase33_v3.py`——"early versions, replaced"
- `06_phase34_tcga.py`——"does not reproduce Table S5; replaced"
- `07_brain_siletti_analysis.py`等——"crash on modern hardware (MemoryError) or produce mismatched results; replaced"

第三组尤其值得注意：早期版本产生"Mismatched results"，这暗示了结果的不稳定性。建议在补充材料中报告早期版本与最终版本的关键结果差异，或提供版本演变的简要说明。

### 3.4 参数扫描范围有限

参数扫描（HK基因集大小、HVG数量、pathway weights）仅在小鼠数据上进行（Tabula Muris，703对比）。小鼠数据中细胞类型较少（~32种），跨器官多样性较低。人类数据有99种细胞类型，脑数据有跨108个区域的10个细胞类——参数扫描的结果是否可推广到这些复杂得多的数据集？至少应提供一个人类或脑数据子集上的关键参数敏感性验证。

### 3.5 TCGA分析的批量效应混淆

稿件承认TCGA分析使用bulk RNA-seq，"tumor samples may contain mixed cell populations"，且"observed transcriptional convergence may partially reflect convergent tumor microenvironment remodeling"。这是一个根本性的混淆：肿瘤间转录组的同质性（NN/TT > 1）可能仅仅反映相似的免疫浸润/基质比例，而非恶性细胞的真实转录收敛。稿件将此列在Limitations中，但Discussion中仍做出较强断言（"implications for cancer biology"、"common vulnerabilities"）。建议降低TCGA分析结论的语言强度，直到有单细胞层面的验证。

### 3.6 补充材料中的信息不一致

补充材料Supplementary Note 3.3中写道"Bootstrap iterations: B=1,000 for all primary results"，但稿件正文与复现指南均表明仅小鼠pilot使用B=500，人类/TCGA/脑分析不使用bootstrap。这是一个事实错误，应修正。

---

## 4. 方法学亮点

### 4.1 概念创新性强

将转录组比较分解为"基线"（HK基因）和"功能"（身份基因）两个正交分量的思路是优雅且原创的。虽然Ka/Ks类比的数学基础有限（见Critical Issue 1.3），但生物学逻辑清晰，为单细胞领域提供了一个新的思考框架。

### 4.2 全自动数据驱动的基线基因集检测

HK基因的自动检测策略（detection rate > 0.9 AND CV < 30th percentile）不需要外部数据库，适用于任何物种。敏感性分析表明ω对HK基因集组成稳健（CV < 13%，99.2%对比），为方法的跨物种应用提供了良好的可移植性。

### 4.3 乘法残差模型的设计思路

虽然阈值设定存在问题（见Major Issue 2.4），但乘法残差模型（observed/expected using μ_ct × μ_pair / μ_grand）的设计是聪明的：它同时考虑了细胞类型自身的可塑性水平和区域对比的背景差异，避免将高表达变化性细胞类型的所有对比都误报为"异常"。

### 4.4 OPC阴性对照的内置验证

OPCs（少突胶质前体细胞）是成人CNS中迁移最活跃的细胞，但模型在5,671对比较中检测到0个Strong信号。这个阴性对照是对方法特异性的有力验证，且论证了模型检测的是发育起源信号而非活跃的细胞迁移——这一结论的重新框架化在Discussion中处理得诚实而优雅。

### 4.5 跨数据集的规模验证

方法在四个完全不同规模和生物背景的数据集上进行了验证：小鼠图谱（703对）、人类图谱（4,851对）、TCGA泛癌（~20,000对）、人脑单核图谱（31,764对）。这一跨尺度的验证策略增强了方法学声明的可信度。

---

## 5. 与其他方法比较的评估

### 5.1 当前比较的优缺点

**优点**：
- 覆盖了主要的距离度量类型（散度、相关距离、角度距离、集合距离）
- 均在同一数据集（Tabula Sapiens，4,851对）上计算，保证可比性
- 诚实报告了CKI在AUC上不如余弦距离和原始JS散度
- 提供了200基因限制下的余弦距离AUC作为公平比较的参照

**缺点**：
- 比较对象均为"距离度量"而非"基线归一化指数"，类别不匹配
- 未与直接竞争方法比较（SAMap、SATURN、CACIMAR），使得"complementarity"声称缺乏实证支撑
- AUC不适合作为CKI性能评估的指标（CKI不是分类器），但稿件仍然将其作为主要比较指标
- 真正有信息量的比较是图3B的相关性热图（展示CKI与其他度量的信息独立性），但这一点被AUC主导的比较分散了注意力

### 5.2 建议的比较策略

1. 将CKI的ω排名与CACIMAR的保守性评分在相同生物问题上比较（如跨器官细胞类型保守性）
2. 评估CKI是否需要或能够受益于批次校正预处理（如Harmony），因为k_n声称捕获了"中性"变异（包括批次效应）
3. 评估CKI在不同测序深度、不同细胞数、不同稀疏度下的稳健性

---

## 6. 总体建议

### 6.1 发表建议：**Major Revision**

CKI代表了一个有创意、有潜力的计算框架，稿件展示了跨四个数据集的广泛验证。但当前版本存在三个阻断级别的Critical Issues（归一化文档不一致、完全缺乏多重检验校正、Ka/Ks类比的数学基础）和多个需要实质性修改的Major Issues。

### 6.2 修改优先级

**必须修改（修改后重新审稿）**：
1. 统一归一化策略在三份文档中的描述，并提供软性分析和证明
2. 对所有多对比较应用FDR校正，报告校正后的显著性结果
3. 降低Ka/Ks类比的语言强度，明确定位CKI为"基线归一化差异指数"

**应修改（修改即可接受）**：
4. 提供固定基因集k_f模式的结果作为敏感性验证
5. 将bootstrap B增加到至少1,000（对需要使用bootstrap的分析）
6. 为乘法残差模型提供正式的排列零分布阈值
7. 扩大参数扫描到人类或脑数据集

**建议修改（非必需）**：
8. 修正JS对数底数的不一致描述
9. 扩展方法比较至更相关的方法
10. 调整TCGA结论的语言强度

### 6.3 整体评价

CKI是一个设计上优雅、验证上勤勉的方法学工作。其核心概念——将转录组差异分解为基线和功能两个维度——填补了单细胞分析方法学空白。稿件中的关键发现（如负相关于所有标准度量、脑区域的发育起源信号）是新颖且有生物学意义的。

但文档质量（归一化策略描述严重不一致）、统计严谨性（完全缺乏多重检验校正）、和理论框架的诚实性（Ka/Ks类比被自身讨论段落解构）需要在修改中首先解决。如果上述Critical Issues得到充分处理，我认为CKI将成为一个有价值的单细胞分析工具。
