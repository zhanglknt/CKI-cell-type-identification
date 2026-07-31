# 方法学审稿报告 — CKI v14 NAR Submission

## 评分：6.8 / 10（v12: 5.5/10）

## v12→v14 修复评估

### 1. JS对数底统一为 base-2 ✅ 已解决

P020 明确声明 "JS divergence uses the base-2 logarithm (range [0, 1])"，补充材料 Supplementary Note 1.1 亦使用 "log2"。全文无残留的 "natural log" 描述。与代码 `np.log2` 一致。

### 2. 归一化方法统一为 softmax normalization ⚠️ 部分解决

全文（正文 P020/P041、补充材料 Note 1.1/1.2/1.3、伪代码 Algorithm 1）均统一使用 softmax normalization，消除了 v12 中 softmax vs. sum-normalization 的矛盾。

**但存在两个残留问题：**
- **P020 存在重复文本**："via softmax normalization (p_i = exp(x_i) / Σ exp(x_j)). softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j))." —— 同一公式在同一段落中连续出现两次，显然是编辑遗漏。
- **softmax 用于 log1p 变换后数据的理论合理性未讨论**：log1p 变换后表达值为非负实数，softmax 将其指数化后再归一化，实际上等价于对原始（log1p 前）表达值做带偏移的归一化。这一选择的数学后果（如对低表达基因的放大效应）未在方法中讨论。

### 3. TPM vs. FPKM 统一为 TPM ✅ 已解决

正文 P026 明确 "TPM values from UCSC Xena, log2(x+1) transformed"，补充材料 Note 1.6 和 Note 4.3 均统一为 "TPM values from UCSC Xena"。全文无残留 FPKM 描述。与代码使用 UCSC Xena RSEM gene TPM 一致。

### 4. TCGA 样本数统一为 3,596 ✅ 已解决

正文 P057 "totalling 3,596 samples"，补充材料 Note 4.3 "totaling n = 3,596 samples"。各癌种数字（LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109）在正文和补充材料中一致。v12 中 Supplementary 声称 10,535 样本的错误已修正。

### 5. Bootstrap B 值统一 ✅ 已解决

正文 P022 "B = 1,000 for primary analyses, B = 500 for calibration"，P037 "B = 1,000 for primary analyses and B = 500 for calibration"，P043 "B = 1,000 for primary analyses, B = 500 for calibration"。补充材料 Note 1.5 "default B=1,000"、Note 3.2 "B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"。全文一致。

### 6. HVG flavor 统一为 "Seurat flavor" ✅ 已解决

正文 P024 `flavor="seurat"`，P020/P042 "Seurat flavor"，P046 "Seurat"。全文无残留 "Seurat v3" 描述。与代码 `flavor='seurat'` 一致。

### 7. "three scales" → "four scales" ⚠️ 部分解决

正文 P016 已改为 "We validated CKI across four scales"。但 Abstract（P010）仍使用 "We validated CKI across four datasets"。虽然 "scales" 和 "datasets" 指代相同内容，但术语不一致。更重要的是，这四个验证实际上是四个不同的数据集/应用场景，称其为 "four scales" 略有夸大——除非作者明确定义这四个 "scales" 分别是什么尺度（如：细胞类型尺度、组织尺度、疾病尺度、脑区尺度）。

### 8. 补充材料 FDR 声明 ✅ 已解决

补充材料 Note 1.5 明确声明 "Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses; all reported P-values are raw bootstrap P-values"。Note 3.3 进一步说明 "raw bootstrap P-values are reported"。正文 P037 和 P043 亦声明 "All reported P-values are raw bootstrap P-values without multiple testing correction"。声明已透明化。

### 修复评估小结

8 项修复中：**6 项完全解决**，**2 项部分解决**（归一化方法存在重复文本和理论讨论缺失；"scales" 术语不一致）。v12→v14 的参数矛盾已从生成脚本根源层面得到有效控制，稿件内部一致性显著提升。然而，部分修复引入了新的文本质量问题（如 P020 重复文本），且若干 v12 Critical/Major Issues 的方法学本质问题仍未得到实质性处理（详见下文）。

---

## 总体评价

v14 相较 v12 在内部一致性上有实质性进步。8 项参数矛盾中 6 项已彻底解决，剩余 2 项仅为文本层面的小问题。归一化方法（softmax）、对数底（base-2）、TCGA 数据源（TPM）、Bootstrap B 值（1,000/500）、HVG flavor（Seurat）等关键技术参数现在全文统一，可重复性显著提升。补充材料对 FDR 未校正的透明声明也体现了作者的诚实态度。这些改进使稿件从 v12 的"参数自相矛盾、无法评审"状态提升到了"参数一致、可以评审方法学本质"的状态。

然而，从方法学维度审视，v12 提出的若干核心方法学问题并未因参数修复而自动解决。最突出的是：(1) 混合方案中 k_n（~1,000 HK 基因）与 k_f（200 成对 DE 基因）在不同维度 JS divergence 上直接取比值的理论基础仍无数学证明或模拟验证——v14 仅将 v12 的声称重新表述为"the normalization remains internally valid despite the different gene selection strategies"，但这只是断言而非证明；(2) 校准实验仍为 n=6，mean ω = 1.54 的 +54% 偏差未通过扩大样本量或引入校准因子来解决；(3) 31,764 次脑区比较和 4,851 次 Tabula Sapiens 比较均未进行多重检验校正——虽然已透明声明，但方法学上仍是不充分实践。

此外，v14 引入了若干新的文本问题：CKI 缩写在标题（"Kinetic"）和摘要（"Comparative"）中不一致；P020 出现 softmax 公式重复文本；脑区分析的生物学机制数量在 Methods（四种）、Results（三种）和 Discussion（三种但组成不同）之间不一致；P-value 计算公式在校准实验和主要分析之间使用了两种不同形式但 P037 声明为统一公式。这些新问题虽不改变方法本质，但影响了稿件的技术严谨性印象。

---

## 关键问题（Critical Issues）

**C1. CKI 缩写定义矛盾**

稿件标题（P001）为 "CKI: A Cell-state **Kinetic** Index"，但摘要（P010）为 "CKI (Cell-state **Comparative** Index)"。这是一个基础性错误——论文标题中的核心术语缩写与摘要中的展开不一致，在期刊投稿中是不可接受的。需要统一为 "Kinetic" 或 "Comparative" 之一（考虑到 "Kinetic" 暗含时间动态性而 CKI 实际度量的是横向差异，"Comparative" 可能更准确，但作者需自行决定）。

**C2. P-value 计算公式不一致**

稿件在不同位置使用了两种不同的经验 P-value 计算公式：

- **校准实验**（P022）和**伪代码 Algorithm 1 line 15**：P = 2 × min(proportion of ω_null ≥ ω_obs, proportion of ω_null ≤ ω_obs) —— 双侧百分位法，无 +1 伪计数
- **主要分析**（P043）和**补充材料 Note 1.5**：P = (count(ω_null ≥ ω_obs) + 1) / (B + 1) —— 单侧 +1 伪计数法
- **Statistical reporting**（P037）：声称 "empirical P-values use the +1 pseudocount formula" 作为通用声明

这三种描述互相矛盾：P037 声称统一使用 +1 公式，但 P022 和 Algorithm 1 使用的是无 +1 的双侧百分位法。两种公式在 B=500/1000 时给出的 P-value 不同，尤其在小 P-value 区域差异显著。必须统一为一种公式，并确保正文、补充材料和伪代码完全一致。

**C3. 混合方案中 k_n/k_f 跨维度可比性仍无理论证明**

v12 的 C4 问题未获实质性解决。v14 P050 的辩护为："Critically, since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies."

这一断言在数学上仍不成立。JS divergence 的值取决于概率分布的维度（基因数量）和分布形态。在 200 维分布上，两个相似分布的 JS 值与在 1,000 维分布上的 JS 值没有直接的数学可比性——高维空间中分布更容易"分离"（curse of dimensionality），导致 1,000 维 k_n 可能系统性偏高，从而使 ω 系统性偏低。P093 承认"users should compare ω ranks rather than absolute values across datasets"，但脑区分析中又使用了绝对 ω 阈值（Strong: ω < 15），构成逻辑矛盾。

作者需要：(1) 提供理论推导或模拟实验，证明在不同基因集维度下 JS 值的比值是无偏的；(2) 或使用相同维度的基因集计算 k_n 和 k_f（如同维度但分别从 HK 池和 non-HK 池中选取 top-N）；(3) 或至少在补充材料中报告维度敏感性分析（如 k_n 分别用 200/500/1000 HK 基因时 ω 的变化）。

**C4. 校准实验 n=6 仍未扩展**

v12 的 C3 问题未获解决。校准实验仍为 n=6（P047），mean ω = 1.54（偏差 +54%）。v14 在 Discussion（P091）中将 1.54 重新定义为"empirically calibrated operational baseline"，这是合理的表述调整，但未解决根本问题：

- n=6 无法支撑可靠的等效性检验——在如此小的样本量下，即使存在系统性偏差也难以检测
- P047 声称"This confirms that CKI recognizes biologically equivalent cell populations as having **no functional divergence**"，但 ω = 1.54（而非 1.0）表示功能分歧率为 54%，称其为"no functional divergence"不准确
- 脑区分析中的绝对阈值（ω < 15 for Strong）未根据 1.54 的校准基线进行调整

建议：(1) 扩大校准至至少 50 次随机分裂（Tabula Muris 有 32 个细胞类型，每个做 2-3 次分裂即可达到 64-96 次）；(2) 报告扩大后 ω 的分布和 TOST 等效性检验结果；(3) 考虑引入校准因子 ω' = ω / 1.54，使基线对应 ω' ≈ 1。

**C5. 脑区分析机制数量不一致**

Methods（P031）定义了**四种**生物学机制：developmental origin heterogeneity (DO)、embryonic colonization route boundaries (CR)、compartmentalized developmental specification (DS)、postnatal cell migration (PM)。

Results（P073）则列出**三种**机制：(i) DO、(ii) CR、(iii) PM —— 遗漏了 DS。

Discussion（P096）也列出**三种**机制，但组成不同：(i) DO、(ii) CR、(iii) DS（compartmentalized developmental astrogenesis and vascular specification）—— 遗漏了 PM，并声明"rather than active cell migration"。

三处描述的机制数量和组成互相矛盾。如果 PM（成纤维细胞的 A40-SN 信号）是唯一被归因于出生后迁移的 Strong 信号，那么 Discussion 将其排除在"三种主要过程"之外是可以理解的，但 Methods 定义四种机制时已包含 PM，Results 列出三种时又包含了 PM 而排除了 DS。这种不一致表明作者需要重新梳理机制分类的逻辑：是在 Methods 中定义四种可能性，然后在 Results/Discussion 中根据实际发现报告哪些被观察到？还是统一为三种？

---

## 主要问题（Major Issues）

**M1. 多重检验未校正（v12 M2 未解决）**

虽然 v14 透明声明了未进行 FDR 校正（P037, P043, Supplementary Note 3.3），但方法学上仍不充分：

- 脑区分析进行了 31,764 次比较，在 P < 0.05 阈值下预期 ~1,588 个假阳性
- 30 个 Strong 信号（0.09%）的判定不仅基于 P-value，还基于乘法残差阈值，这在一定程度上控制了假阳性，但残差阈值本身也是经验导出的
- Tabula Sapiens 的 4,851 次比较中所有 P < 0.001 的声明，在 B=1000 下最小可能 P-value 为 1/1001 ≈ 0.001，因此"P < 0.001"实际上意味着 P ≈ 0.001

建议：(1) 对脑区分析的 30 个 Strong 信号报告置换检验 FDR 估计；(2) 对 Tabula Sapiens 的 4,851 比较应用 BH-FDR 并报告校正后仍显著的比例；(3) 在方法中明确讨论为何未校正（如"effect sizes 均较大"）是否可接受。

**M2. 负相关作为"独立信息维度"的证据仍不充分（v12 M3 未解决）**

P010（摘要）声称 CKI ω 与标准度量负相关"proving it captures an independent information dimension"。P092 重复了"proves"一词。但：

- 负相关仍是一种关联，不等于独立。真正的独立性应通过偏相关或互信息来证明
- v12 提出的关键替代解释——负相关可能由 k_n → 0 时的数值不稳定驱动——在 v14 中仍未被分析
- 当两个群体总体相似时（标准距离低），k_n 接近零，ω = k_f/k_n 可能被放大，产生人为的负相关

建议：(1) 分层分析：将 4,851 对按 k_n 分位数分组，分别计算 ω 与标准度量的相关性；(2) 排除 k_n < 0.01 的对后重新计算相关性；(3) 使用偏相关控制 k_n 的影响；(4) 将摘要中的"proving"改为"indicating"或"suggesting"。

**M3. "同器官 > 跨器官"反转的替代解释未排除（v12 M4 未解决）**

P055 报告 CKI 是唯一一个同器官 ω > 跨器官 ω 的度量，并将其解读为"对共享微环境中功能特化的敏感性"。但 v12 提出的替代解释仍未被排除：

- 混合方案中 k_f 使用每对 top-200 DE 基因，同器官内不同细胞类型可能在器官特异性基因上高度分歧
- k_n 使用全局 HK 基因，同器官细胞对间 HK 基因分歧可能更低（共享微环境），导致分母更小、ω 更大
- 这可能是基因选择策略和基线差异的人为产物，而非"功能特化"信号

建议：使用全局固定基因集（如全局 top-2000 HVG 中 non-HK 部分）重新分析，检验反转是否仍然存在。

**M4. 乘法残差模型阈值仍缺乏正式零分布（v12 M5 未解决）**

P031/P074 的乘法残差模型使用经验阈值（Strong: residual < 0.3, ω < 15, lowest ω in pair, pair median ω > 20）。这些阈值仍"calibrated on the observed data rather than a formal null distribution"。

v12 建议报告置换检验结果，但 v14 仍未提供：
- 每个 tier 的置换 P-value 和 FDR
- 经验阈值与置换阈值的定量比较
- 30 个 Strong 信号中有多少在置换零分布下仍然显著

"pair median ω > 20"这一准则意味着只有高分歧区域对才能产生 Strong 信号，这系统性偏向于高 ω 区域对，可能遗漏低 ω 区域对中的真实信号。

**M5. 与现有方法的比较仍不充分（v12 M7 未解决）**

方法比较仍仅限于四种标准距离度量（raw JS、Spearman、cosine、Jaccard）。缺少：
- **Wasserstein distance**：作为分布度量与 JS divergence 有理论联系，在单细胞领域有广泛应用
- **PCA-based distance**：降维后计算距离是常见做法
- **MAST/DESeq2 差异表达统计**：CKI 的 k_f 基于 DE 基因，应与标准 DE 分析方法比较

AUC 比较的公平性问题也未完全解决：CKI 的 k_f 使用 200 个成对 DE 基因，而标准度量使用全部 ~20,000 基因。v12 提到作者曾限制 cosine 到 200 基因后 AUC 从 0.887 降到 0.752，但 v14 未报告此对比。

**M6. 术语不一致**

- **k_f 名称**：P015 和 P010 称 "functional divergence rate"，P042 和 Supplementary Note 1.3 称 "functional conversion rate"。需统一。
- **"four scales" vs "four datasets"**：P016 称 "four scales"，P010 称 "four datasets"。需统一，并明确定义"尺度"的含义。
- **"migration candidates" vs "developmental signatures"**：主文 P075/P073 使用 "migration candidates"，P096 改为 "developmental signatures"，但补充材料 Table S4 仍全部使用 "migration candidates"。需在补充材料中同步更新术语。

**M7. ω 上限截断（capping at 1,000）未在正文中说明**

Supplementary Note 1.1 和 Algorithm 1 line 7 提到 "omega is capped at 1,000"，但正文 Methods 部分（P018-P022）从未提及这一截断。截断会影响高 ω 值的统计分布和解读。需在 Methods 中明确说明，并报告有多少比较被截断。v12 的 m2 问题未解决。

---

## 次要问题（Minor Issues）

**m1. 样本数量微小不一致**

P027 声称 "LIHC Edmondson grade: from cBioPortal, 289 tumors" 和 "LUAD mutations: from cBioPortal, 497 samples"，但 P033 声称 "n = 288 tumors with both grade and expression data" 和 "n = 492 samples"。P060 的分层数据（G1 n=39 + G2 n=133 + G3 n=105 + G4 n=11 = 288）与 P033 一致。需将 P027 的数字与 P033/P060 统一。

**m2. HK 基因数量不一致**

正文 P019 和 P025 声称 "1,130 human-mouse shared HK genes"，但补充材料 Note 4.2 声称 "supplemented with 1,129 genes from HRT Atlas v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog was excluded)"。1,130 vs 1,129 的差异需统一或解释（如 1,130 是原始集，1,129 是去掉无人源同源基因后的集）。

**m3. 脑区分析中细胞类型梯度排序错误**

P069 按递增顺序列出 ω：Bergmann glia (2.37) → committed OPCs (3.17) → fibroblasts (3.99) → vascular cells (3.40) → ependymal cells (4.13)。但 fibroblasts (3.99) > vascular cells (3.40)，排序错误。应改为：BG (2.37) → committed OPCs (3.17) → vascular cells (3.40) → fibroblasts (3.99) → ependymal cells (4.13)。

**m4. 跨物种 k_n 不可比未讨论**

Mouse 校准 k_n 中位数 ≈ 0.0019，Human k_n 范围 0.0147–0.0166，相差约 10 倍。P051 提到 human ω 高于 mouse 并给出解释（细胞类型更多、供体异质性更大），但未直接讨论 k_n 的跨物种不可比性及其对 ω 解释的影响。

**m5. 随机种子验证不充分**

P035 仅声明 "All random seeds were fixed at 42"，未进行多种子验证。对于涉及 31,764 次比较的大规模分析，单一种子的结果稳定性需验证。建议至少对关键结果进行 5 个随机种子的验证。

**m6. OPC 阴性对照的逻辑循环风险（v12 m6 未解决）**

P077 声称 OPCs（最活跃迁移细胞）产生 0 个 Strong 信号是方法特异性的验证。但 P077 同时承认 OPCs 的高全局 ω (7.65) 提高了检测阈值。乘法残差模型中 expected_ω = μ_ct × μ_pair / μ_grand，当 μ_ct（OPC 的全局均值）较高时，expected_ω 也较高，使得 residual = observed / expected 更难低于 0.3。因此，高 ω 细胞类型天然不容易产生 Strong 信号——这不是"特异性"而是"敏感性不足"。需要更仔细地区分。

**m7. TCGA bulk RNA-seq 局限未充分讨论**

NN/TT > 1 的发现可能由肿瘤微环境（免疫浸润、基质组成）的趋同变化驱动，而非恶性细胞本身。P056-059 虽提及 bulk 限制，但未进行去卷积分析来排除这一混淆。

**m8. 敏感性分析细节不足**

P097 和 Supplementary Note 1.2 声称 "using the lowest 10% variable genes as a neutral set yielded ω correlations r > 0.95"，但未提供：分析使用的数据集、比较数量、相关方法、具体 ω 值对比。对于方法学论文，敏感性分析应更详细报告。

**m9. "proving" 用词过强**

P010（摘要）和 P092 使用 "proving" 来描述负相关的证据强度。在统计推断中，负相关不能"证明"独立性。建议改为 "indicating" 或 "strongly suggesting"。

**m10. 补充材料 Table S4 术语未更新**

补充材料 Supplementary Table 4 标题仍为 "Inter-regional Cell Migration Candidate Data"，内容仍使用 "migration signals" / "migration candidates"。但主文 P096 已将结论重构为 "developmental signatures" 而非 "migration"。补充材料应同步更新术语，或在标题中加入 "putative" 以反映主文的重构。

---

## 优点（Strengths）

1. **参数一致性显著提升**：v12 中最严重的 5 个 Critical 参数矛盾（归一化方法、基因选择策略、TCGA 预处理、Bootstrap B 值、样本数）在 v14 中已基本解决，稿件内部一致性大幅改善，可重复性提高。

2. **FDR 声明透明化**：v14 在正文和补充材料中均明确声明未进行系统性的多重检验校正，并解释了所用统计检验的分布（P037, P043, Supplementary Note 3.3）。这种诚实态度值得肯定，虽然方法学上仍不理想，但至少读者可以自行判断结论的可靠性。

3. **Ka/Ks 类比边界讨论改进**：P014-015 在 Introduction 中即明确声明 "CKI is a heuristic index, not a formal measure of Darwinian selection" 并指出缺少突变率 μ 的抵消机制。P091-093 在 Discussion 中进一步讨论了四个技术局限（序列 vs. 连续表达、机制基础、系统发育框架、跨比较解释力）。这比 v12 的讨论更充分。

4. **OPC 阴性对照设计**：利用 OPCs 作为"最活跃迁移细胞"的阴性对照来验证乘法残差模型的特异性（P077），在方法学上是一个巧妙的验证设计。尽管存在逻辑循环风险（见 m6），但其思路值得提倡。

5. **混合方案的理由说明改善**：P050 明确解释了为何 Tabula Sapiens 使用混合方案（k_n 全局一致 + k_f 成对自适应），以及为何 Tabula Muris 使用全局 HVG。这比 v12 的混乱描述清晰得多。

6. **验证规模宏大**：跨四个大规模数据集（Tabula Muris 15K 细胞、Tabula Sapiens 108K 细胞、TCGA 3,596 样本、Siletti 888K 核）进行验证，数据覆盖范围令人印象深刻。

7. **代码和数据公开**：Python 包（v0.3.2, MIT License）和所有分析脚本在 GitHub 公开，Zenodo 存档（DOI: 10.5281/zenodo.15670808），有利于可重复性。

8. **生物学解读有深度**：脑区分析中将 30 个 Strong 信号系统性交叉验证于发育神经科学文献，区分了发育起源异质性、定植路线边界和发育规格化等机制，这种"计算-实验"交叉验证的思路值得提倡。

---

## 具体修改建议

### 针对 Critical Issues

**C1 修改建议**：
- 统一 CKI 缩写。建议将摘要中的 "Cell-state Comparative Index" 改为与标题一致的 "Cell-state Kinetic Index"，或反过来修改标题。考虑到 CKI 度量的是横向差异而非时间动态，"Comparative" 可能更准确，但需全文统一。

**C2 修改建议**：
- 统一 P-value 公式为一种。建议统一使用 +1 伪计数双侧公式：P = 2 × min((count ≥ + 1)/(B + 1), (count ≤ + 1)/(B + 1))，兼顾双侧检验和避免 P = 0。
- 修正 P037 的通用声明，使其与实际使用的公式一致。
- 确保伪代码 Algorithm 1 与正文公式完全一致。

**C3 修改建议**：
- 在补充材料中提供维度敏感性分析：分别使用 100/200/500/1000 个 HK 基因计算 k_n，报告 ω 的变化和相关系数。
- 进行模拟实验：生成已知差异度的合成数据，在 200 维和 1000 维分布上计算 JS 值的比值，验证比值是否有偏。
- 或修改方法：使用相同维度的基因集计算 k_n 和 k_f（如同为 top-200，分别从 HK 池和 non-HK 池中选取）。

**C4 修改建议**：
- 扩大校准至至少 50-100 次随机分裂，报告 ω 分布和 TOST 结果。
- 将 P047 的 "no functional divergence" 改为 "no statistically significant functional divergence"。
- 考虑引入校准因子或在脑区分析中使用相对阈值（如 residual 分位数而非绝对 ω 阈值）。

**C5 修改建议**：
- 统一机制分类。建议在 Methods 中定义四种理论可能机制（DO, CR, DS, PM），在 Results 中报告实际观察到的机制（注明 PM 仅 1 例），在 Discussion 中总结主要发现（三种主要过程 + 1 例 PM 例外）。确保三处描述逻辑连贯。

### 针对 Major Issues

**M1 修改建议**：
- 对脑区 30 个 Strong 信号报告置换检验 FDR 估计。
- 对 Tabula Sapiens 4,851 比较应用 BH-FDR 并报告校正后仍显著的比例。
- 在 Discussion 中增加一段讨论未校正的影响及为何 effect sizes 足够大以至于 FDR 校正不会改变结论（如果确实如此）。

**M2 修改建议**：
- 按 k_n 分位数分层分析 ω 与标准度量的相关性。
- 排除 k_n < 0.01 的对后重新计算相关性。
- 使用偏相关控制 k_n。
- 将摘要和正文的 "proving" 改为 "indicating"。

**M3 修改建议**：
- 使用全局固定基因集重新分析 Tabula Sapiens，检验"同器官 > 跨器官"反转是否仍然存在。
- 如果反转消失，在文中明确讨论基因选择策略对这一信号的影响。

**M4 修改建议**：
- 报告置换检验的完整结果：每个 tier 的置换 P-value 和 FDR。
- 报告经验阈值与置换阈值的定量比较。
- 对 30 个 Strong 信号逐一报告置换显著性。
- 讨论 "pair median ω > 20" 准则对低 ω 区域对的系统性排除。

**M5 修改建议**：
- 增加 Wasserstein distance 比较。
- 对所有标准度量在限制到相同 200 DE 基因后重新计算 AUC，进行公平比较。
- 增加 CKI 与 DE 分析（如 Wilcoxon rank-sum test on DE genes）的关系讨论。

**M6 修改建议**：
- 统一 k_f 术语为 "functional divergence rate" 或 "functional conversion rate"。
- 统一 "four scales" / "four datasets"，并明确定义"尺度"。
- 更新补充材料 Table S4 的术语以匹配主文。

**M7 修改建议**：
- 在 Methods P020 中加入 "ω values are capped at 1,000 to prevent numerical instability when k_n approaches zero"。
- 报告有多少比较被截断。

### 针对 Minor Issues

- m1: 统一 P027 与 P033 的样本数（以 P033 为准，因其与分层数据一致）。
- m2: 统一 HK 基因数为 1,130 或解释 1,129 的来源。
- m3: 修正 P069 的梯度排序。
- m4: 在 Discussion 中增加一段讨论跨物种 k_n 不可比性。
- m5: 对关键结果进行至少 5 个随机种子的验证。
- m6: 讨论 OPC 阴性对照中特异性与敏感性的区分。
- m7: 讨论 TCGA bulk RNA-seq 中微环境趋同的可能性。
- m8: 补充敏感性分析的详细参数和结果。
- m9: 将 "proving" 改为 "indicating"。
- m10: 更新补充材料 Table S4 术语。

---

**总结**：v14 相较 v12 在参数一致性上有显著进步，8 项参数矛盾中 6 项已彻底解决，稿件从"参数自相矛盾"状态提升至"可以评审方法学本质"的状态。然而，v12 提出的若干核心方法学问题——混合方案 k_n/k_f 跨维度可比性的数学基础缺失、校准实验样本量不足、多重检验未校正、负相关机制未充分分析——在 v14 中仍未获实质性解决。此外，v14 引入了若干新的文本问题（CKI 缩写矛盾、P-value 公式不一致、机制数量不一致、重复文本等），虽不改变方法本质，但影响技术严谨性印象。建议进行 Minor-to-Moderate Revision，重点解决 C1-C5 和 M1-M7。修订后的稿件如果能够：(1) 统一所有公式和术语，(2) 提供 k_n/k_f 跨维度可比性的模拟或理论证据，(3) 扩大校准实验，(4) 对主要分析进行多重检验校正或提供置换 FDR，(5) 分析负相关是否由 k_n → 0 驱动，则有潜力成为该领域的有价值贡献。
