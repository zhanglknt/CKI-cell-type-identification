# CKI 算法 NAR 投稿包 v15 审稿报告

## 审稿人：数据科学与可复现性专家

**审阅文件**：manuscript.txt、supplementary.txt、reproducibility.txt、cover_letter.txt

**审稿日期**：2026-07-27

---

## 1. 总体评分：5.5 / 10

CKI 方法的概念设计有创新性（将 Ka/Ks 启发式逻辑引入转录组比较），验证范围覆盖四个数据集、多尺度。然而，**正文、补充材料与复现指南之间存在多处关键性数值矛盾**，直接影响结果的可复现性和可信度。在当前状态下，投稿包尚未达到 NAR 的发表标准，需要进行重大修订（Major Revision）后方可重新提交。

**评分依据**：
- 方法学创新性：7/10（Ka/Ks 类比有启发性，但作者已坦诚其数学非等价性）
- 验证充分性：6/10（四数据集覆盖面广，但统计校正缺失）
- 数据一致性：3/10（多处关键数值矛盾）
- 可复现性：5/10（复现指南详细，但与正文矛盾、部分脚本不可复现）
- 期刊适配度：7/10（符合 NAR 方法学定位）

---

## 2. Critical 问题（投稿阻断级）

### C1. JS 散度对数底数矛盾——直接影响所有 ω 值

**正文**（manuscript.txt:20）明确声明：
> "JS divergence uses the **base-2 logarithm** (range [0, 1])."

**补充材料**（supplementary.txt:16）同样声明：
> "When using the **base-2 logarithm**, the JS divergence is bounded in [0, 1]."

**复现指南**（reproducibility.txt:50-53）却使用**自然对数**：
> "JS(P || Q) is the Jensen-Shannon divergence (**natural log**): ... KL(P || M) = sum_i [ P_i * **ln**(P_i / M_i) ]"

**严重影响**：对数底数直接影响 JS 散度的绝对值。base-2 时 JS ∈ [0, 1]；自然对数时 JS ∈ [0, ln(2)] ≈ [0, 0.693]。由于 ω = k_f / k_n，如果 k_n 和 k_f 使用相同的底数，比值在理论上不变（底数因子在分子分母中抵消）。但问题在于：
- 正文声明 range [0, 1]，这意味着读者和审稿人会以 base-2 的尺度理解所有数值
- 如果实现实际使用自然对数，那么所有报告中涉及 k_n、k_f 绝对值的论述（如"k_f increased roughly 1,000-fold"、"k_n increased only about 100-fold"）都受影响
- 补充材料中 "omega is capped at 1,000" 的上限设定也依赖于对数底数的尺度

**建议**：必须统一声明对数底数，并确认实际代码实现与声明一致。如果代码使用 `scipy.spatial.distance.jensenshannon`（默认 base=2），则复现指南中的 `ln` 表述为笔误；如果代码使用 `scipy.special.kl_div` 或手动实现，则需确认底数。这是阻断性错误。

### C2. 归一化方法矛盾——softmax vs sum-normalization

**正文**（manuscript.txt:20）和**补充材料**（supplementary.txt:16）均声明使用 softmax 归一化：
> "each vector is normalized to a probability distribution before JS divergence computation via **softmax normalization** (p_i = exp(x_i) / Σ exp(x_j))"

**复现指南**（reproducibility.txt:56-66）描述的实际实现完全不同：
> "In 'auto' mode (the default), the method is selected based on the data range:
> - **Non-negative values: sum-normalization** (p_i = x_i / sum_j x_j). This is used for all CP10k+log1p-normalized data (mouse, human, brain)
> - **Any negative values: softmax** ... This is automatically selected for log2-transformed data (TCGA)"

**严重影响**：四个数据集中有三个（mouse、human、brain）实际使用 sum-normalization，仅 TCGA 使用 softmax。正文和补充材料统一描述为 softmax，与实际实现不符。softmax 和 sum-normalization 对表达向量的概率分布转换结果差异显著——softmax 对低表达基因施加指数放大效应，而 sum-normalization 保持线性比例。这将影响所有 k_n、k_f 和 ω 的数值。

**建议**：正文必须准确描述实际使用的归一化方法。如果 "auto" 模式是实际行为，应明确说明不同数据集使用不同归一化策略，并讨论其对结果可比性的影响。

### C3. Bootstrap P 值计算公式矛盾

**正文**（manuscript.txt:22）和**补充材料**（supplementary.txt:24）使用的公式：
> "P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)), capped at 1.0"

这是对 ω 值本身的双侧检验。

**复现指南**（reproducibility.txt:407-408）使用的公式完全不同：
> "p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)"

这是对 |ω - 1|（偏离 1 的程度）的单侧检验，且无 ×2 的双侧修正。

**严重影响**：这是两个统计检验力完全不同的检验。前者检验 ω 是否偏离 null 分布的均值；后者检验 ω 是否偏离 1（即 "无选择" 的理论值）。二者的 P 值和统计推断结论可能截然不同，尤其在 calibration 实验中（null 分布的均值可能不等于 1）。

**建议**：必须统一公式。鉴于 calibration 实验报告 mean ω = 1.54（而非 1），两种公式的差异不可忽略。

### C4. 软件版本号三重矛盾

| 来源 | Python 版本 | CKI 版本 |
|------|------------|----------|
| 正文（manuscript.txt:35, 96） | **3.12** | **v0.3.2** |
| 复现指南（reproducibility.txt:14, 22） | **3.13.12** | **v0.3.1** |
| 投稿信（cover_letter.txt:19） | 未指定 | **v0.3.2** |

**严重影响**：CKI v0.3.1 和 v0.3.2 之间存在版本差异，但复现指南基于 v0.3.1，而正文和投稿信声明 v0.3.2。Python 3.12 和 3.13 之间也有数值库行为差异（尤其是 NumPy 2.x 在 Python 3.13 上的行为）。如果审稿人按复现指南安装 v0.3.1，可能无法复现 v0.3.2 的结果。

**建议**：统一为实际分析时使用的版本。如果分析在 v0.3.1 上完成但代码已更新至 v0.3.2，需提供版本变更日志并确认结果一致性。

### C5. 人类数据细胞类型对数矛盾——4,851 vs 5,151

**正文**一致使用 4,851 对（manuscript.txt:29, 50, 52, 53, 62）。

**补充材料**（supplementary.txt:70）也使用 4,851。

**复现指南**内部矛盾：
- 正文部分（reproducibility.txt:223）："Full pairwise omega computed for all **4,851** cell-type pairs"
- 运行时表（reproducibility.txt:460）："Human (05_phase33_v3_fixed.py) **5,151**"

**严重影响**：5,151 vs 4,851 差异为 300 对。这可能源于不同的过滤标准（如 ≥10 cells vs ≥20 cells），但未解释。如果实际计算了 5,151 对但仅报告了 4,851 对，需要说明过滤逻辑；如果 5,151 是笔误，需更正。

**建议**：核实实际输出文件行数，统一报告。

---

## 3. Major 问题（强烈建议修改）

### M1. 批次效应未处理且未讨论

Tabula Sapiens（108,136 cells，多供体）和 Siletti 脑图谱（888,263 nuclei，多供体）均为多供体数据集。正文 Introduction（manuscript.txt:13）提及 Harmony、scVI 等批次校正工具，但：
- **Materials and Methods 中未描述任何批次效应评估或校正步骤**
- **复现指南中无批次校正相关代码或参数**
- 正文（manuscript.txt:51）承认 "greater donor heterogeneity in human data (multiple donors vs. inbred mouse strains)"，但未评估其对 ω 的影响

**影响**：k_n（来自 HK 基因）尤其可能捕获供体间批次效应而非纯技术噪声。如果供体 A 和供体 B 的 HK 基因表达因批次不同而差异较大，k_n 会被人为放大，导致 ω 被压缩。正文声称 k_n 捕获 "technical variation, stochastic transcriptional bursting, and individual-level physiological differences"（manuscript.txt:41），但未提供证据区分这些来源。

**建议**：
1. 增加批次效应评估（如 PC1 vs donor identity 的 R²）
2. 如果不做校正，需讨论其对 k_n 的潜在影响
3. 理想情况下，展示有/无批次校正的 ω 值对比（敏感性分析）

### M2. 多重检验校正缺失

正文和补充材料均承认未进行 FDR 校正：
- manuscript.txt:37："All reported P-values are raw bootstrap P-values without multiple testing correction."
- supplementary.txt:59："raw bootstrap P-values are reported"

在脑图谱分析中涉及 31,764 个比较，人类数据 4,851 个比较。在如此大规模的多重比较中，仅报告原始 P 值会导致极高的假阳性率。

- 30 个 Strong 候选信号从 31,764 个比较中检出（0.09%），即使在没有真实信号的零假设下，仅随机因素也可能产生类似数量的显著结果
- 正文声称 OPCs "0 Strong signals" 是 "关键阴性对照"（manuscript.txt:75），但未评估在多重检验框架下这一结果的统计功效

**建议**：
1. 对大规模比较应用 Benjamini-Hochberg FDR 校正（q < 0.05）
2. 报告校正后的显著性结果
3. 如坚持仅报告原始 P 值，需在 Methods 中明确说明理由，并在 Discussion 中讨论对假阳性率的潜在影响

### M3. Tabula Sapiens 细胞类型数矛盾——99 vs 102

| 来源 | 细胞类型数 |
|------|-----------|
| 正文（manuscript.txt:25, 50） | 99 |
| 补充材料（supplementary.txt:66） | 99 |
| 复现指南（reproducibility.txt:209） | **102** |

差异为 3 个细胞类型。可能源于不同的过滤阈值，但未解释。

### M4. 补充图 S3 提及 6 种癌症，正文仅分析 5 种

**补充图 S3 图注**（manuscript.txt:119）：
> "Pairwise ω matrices for **six cancer types (BRCA, KIRC, LIHC, LUAD, COAD, HNSC)**"

但正文（manuscript.txt:26, 56）仅分析 5 种癌症：LUAD、LUSC、LIHC、KIRC、BRCA。S3 中出现的 **COAD（结肠癌）和 HNSC（头颈鳞癌）在正文中从未提及**，而正文中的 **LUSC（肺鳞癌）未出现在 S3 中**。

**影响**：这可能是遗留的旧版图注，但会给读者造成严重困惑。

### M5. 图 5 图注与正文不一致

**图 5 图注**（manuscript.txt:114）：
> "CKI ω ranking of **38 shared cell types** between human and mouse"

**正文**（manuscript.txt:62-63）：
> "59 are same-cell-type cross-organ comparisons" ... "a broad spectrum of conservation across **17 cell types**"

38（图注）vs 17（正文）vs 59（比较对数）——三者均不一致。需要核实实际分析的细胞类型数量。

### M6. 最小细胞数阈值矛盾

| 数据集 | 正文/补充材料 | 复现指南（实际实现） |
|--------|-------------|-------------------|
| 小鼠 | "at least 10 cells per group"（manuscript.txt:19, supplementary.txt:64） | `MIN_CELLS_PER_CT = 10; main filtering uses MIN_CELLS_PER_CT * 2 = **20**`（reproducibility.txt:173-174） |
| 人 | ">= 10 cells"（supplementary.txt:66） | `MIN_CELLS_PER_CT = 10`（reproducibility.txt:218） |
| 脑 | ">= 20 nuclei per (region, cell_type) group"（manuscript.txt:27） | `< 20 nuclei` 过滤（reproducibility.txt:357） |

小鼠数据的实际阈值为 20（非正文所述的 10），这可能导致小鼠数据集的细胞类型数量和比较对数与正文描述不符。

### M7. ω 上限设定矛盾

**补充材料**（supplementary.txt:16）和**伪代码**（supplementary.txt:36）：
> "omega is capped at 1,000" / "omega <- k_f / k_n // capped at 1,000"

**复现指南**（reproducibility.txt:46, 515）：
> "kn=0 → ω=∞" / "Verify no epsilon in omega ratio; kn=0 returns omega=∞"

实际实现不设上限（∞），但补充材料声明 cap 在 1,000。如果某些比较的 k_n 极小但非零，实际 ω 可能远超 1,000，但补充材料的声明暗示这些值被截断了。

### M8. 数据来源矛盾

**Tabula Sapiens**：
- 正文（manuscript.txt:25）："accessed via **CZ CELLxGENE Discover**"
- 复现指南（reproducibility.txt:204）："Source: https://github.com/czbiohub-sf/tabula-sapiens"
- 复现指南（reproducibility.txt:236）："Download Tabula Sapiens h5ad files from **Figshare**: https://figshare.com/projects/Tabula_Sapiens/100973"

三个不同来源。需统一为实际使用的下载源。

**Siletti 脑图谱**：
- 正文（manuscript.txt:27）："Siletti et al. (2023) single-nucleus RNA-seq from **CZ CELLxGENE Discover**"
- 复现指南（reproducibility.txt:338-339）："Source: https://github.com/linnarsson-lab/adult-human-brain" / "Data: https://zenodo.org/records/7865491"

**TCGA**：
- 正文（manuscript.txt:26）："accessed via **TCGAbiolinks (29) and cBioPortal (14) APIs**"
- 复现指南（reproducibility.txt:281-284）：TPM 数据实际来自 **UCSC Xena**
- 补充材料（supplementary.txt:26, 68）："TPM values from **UCSC Xena**"

正文 Methods 的 TCGA 数据获取描述与实际不符。TCGAbiolinks 和 cBioPortal 仅用于临床 metadata，表达数据本身来自 UCSC Xena。

### M9. 不可复现的脚本与硬编码值

复现指南（reproducibility.txt:139-148）明确排除多个脚本：
- `04_phase32_sweep.py`："depends on live MSigDB download and **cannot be exactly reproduced**; ED Fig. 1 uses **hard-coded sweep AUC values**"
- `07_brain_siletti_analysis.py`, `07b`, `07d`："crash on modern hardware (MemoryError) or **produce mismatched results**"

**影响**：
1. Extended Data Fig. 1 的参数扫描结果使用硬编码值，意味着读者无法独立验证 AUC = 0.847 的结果
2. 多个脑分析脚本 "produce mismatched results" 暗示分析结果对实现细节高度敏感
3. 最终保留的 `07c_brain_siletti_v3.py` 是否经过独立验证需说明

### M10. 脑图谱细胞计数不完整

正文（manuscript.txt:27）声明 10 个非神经元细胞类别，总计 888,263 nuclei，但仅列出 8 个类别的明确计数（Bergmann glia 无计数，committed OPCs 计数包含在 OPCs 内）：

| 细胞类型 | 核数 |
|---------|------|
| Astrocytes | 155,025 |
| Oligodendrocytes | 490,246 |
| OPCs (including committed) | 110,454 |
| Microglia | 91,838 |
| Vascular cells | 8,932 |
| Fibroblasts | 8,156 |
| Ependymal cells | 5,882 |
| Choroid plexus | 7,689 |
| **小计** | **878,222** |
| **总计应为** | **888,263** |
| **差额** | **10,041** |

差额 10,041 应为 Bergmann glia 的核数，但正文未明确给出。此外，正文说 "10 major non-neuronal classes" 但仅列出 9 个（committed OPCs 被合并入 OPCs）。

### M11. HRT Atlas 基因数细节矛盾

- 正文和补充材料一致声明 "1,130 human-mouse shared HK genes"
- 复现指南（reproducibility.txt:354）："1,129 unique human genes after set() deduplication; the 1,130-row file contains 1 duplicate mapping where mouse genes Hdhd2 and Ier3ip1 both map to human IER3IP1"
- 脑数据集实际匹配："1,115 HK genes were matched"（reproducibility.txt:356）

正文应说明实际匹配的 HK 基因数因数据集而异。

---

## 4. Minor 问题（建议改进）

### m1. Graphical Abstract 仅为占位符

正文（manuscript.txt:8）：
> "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]"

NAR 要求投稿时提供 Graphical Abstract。当前为占位符，需在投稿前准备完成。Graphical Abstract 应准确反映算法三步流程（pseudobulk → k_n/k_f 分解 → ω = k_f/k_n）及四数据集验证框架。

### m2. Scanpy 版本未在复现指南中声明

正文（manuscript.txt:35）声明 "scanpy >= 1.9.0"，但复现指南 Section 1.1 的 "verified environment" 包列表中**遗漏了 scanpy**。Scanpy 是核心依赖（用于 normalize_total、highly_variable_genes 等），必须锁定版本。

### m3. Seurat 引用但未声明版本

正文多次提及 "Seurat flavor" 用于 HVG 选择（manuscript.txt:20, 46），引用了 Hao et al. 2021/2024（参考文献 26, 27），但：
- 实际使用的是 Scanpy 的 `flavor='seurat'` 实现，而非 Seurat R 包本身
- 未声明 Scanpy 中 seurat flavor 的具体版本行为差异

### m4. 补充图数量与任务描述不符

正文列出 7 个补充图（S1-S7），但任务描述提及 "5补充图"。需确认 NAR 对补充图数量的要求，以及 S6、S7 是否为新增内容。

### m5. 投稿信 AI 使用声明

投稿信（cover_letter.txt:19）声明：
> "AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors."

这符合 NAR 的 AI 使用政策。但建议在 Methods 或 Acknowledgements 中也添加相应声明。

### m6. ω 值跨数据集可比性

正文（manuscript.txt:91）承认 "users should compare ω ranks rather than absolute values across datasets"，但正文多处跨数据集比较 ω 绝对值（如 mouse mean ω = 7.07 vs human mean ω = 14.23, manuscript.txt:51）。建议统一表述。

### m7. 配对样本数过少

正文（manuscript.txt:58）承认 paired tumor-normal 比较的样本量极小：
> "the small number of patients with paired tumor and normal samples (n = 2–5 per cancer type)"

n = 2-5 的统计推断几乎无功效。建议在结果展示中明确标注此限制，或考虑移除该子分析。

### m8. Tabula Muris 原始细胞数

正文报告 15,057 cells（post-QC），复现指南（reproducibility.txt:161）报告原始 17,957 cells → post-QC 15,057 cells。建议在 Methods 中补充原始细胞数和 QC 过滤比例。

### m9. 小鼠参数扫描 AUC 来源

正文（manuscript.txt:44）报告 "AUC = 0.847"，但复现指南承认该参数扫描 "cannot be exactly reproduced" 且使用 "hard-coded sweep AUC values"。应在补充材料中提供原始扫描数据表格，而非仅硬编码值。

### m10. 参考文献格式

参考文献 28（manuscript.txt:152）引用 "Weinstein et al. (2013)"，但正文引用 TCGA 时同时引用了参考文献 7（Cancer Genome Atlas Research Network, 2014）和 8（Cancer Genome Atlas Network, 2012）。参考文献 28 在正文中未见明确引用位置标注。需核对正文中的引用编号。

---

## 5. 可复现性评价

### 5.1 优点

1. **复现指南详尽**：reproducibility.txt 提供了精确到版本的软件环境、参数表、脚本索引、预期输出文件列表和运行时估计，这在同类投稿中属于较高水平
2. **随机种子固定**：全局 seed = 42
3. **Zenodo DOI**：提供永久存档（DOI: 10.5281/zenodo.15670808）
4. **MIT 开源许可**：代码无使用限制
5. **脚本-结果映射**：Section 3.3 提供了脚本到正文结果的映射表

### 5.2 不足

1. **正文与复现指南矛盾**（见 C1-C5）：复现指南描述的实现细节与正文声明的方法在多个关键点上不一致，这意味着按正文理解的方法与按复现指南执行的代码可能产生不同结果
2. **部分结果不可复现**：参数扫描（ED Fig. 1）使用硬编码值，无法独立验证
3. **脚本版本管理混乱**：多个脚本被排除（crash/mismatched results），保留的 `v3` 版本是否经过版本控制标签锁定？GitHub tag v0.3.2 是否包含所有最终脚本？
4. **外部 API 依赖**：cBioPortal API 数据（BRCA PAM50）为实时获取，无快照，未来 API 变更可能导致不可复现
5. **数据下载路径不统一**：同一数据集在不同位置给出不同下载源
6. **跨平台 RNG 警告**：复现指南（reproducibility.txt:535-536）承认 "cross-platform RNG implementations may vary"，导致 bootstrap P 值可能有 ~±0.01 差异。虽然对结论影响小，但对于 borderline 显著的结果可能改变结论

### 5.3 可复现性评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码可用性 | 8/10 | GitHub + Zenodo，MIT 许可 |
| 环境锁定 | 7/10 | 详尽，但 scanpy 遗漏、版本矛盾 |
| 数据可用性 | 6/10 | 公共数据集，但来源描述不一致 |
| 参数透明度 | 7/10 | 参数表详尽，但与正文矛盾 |
| 结果可验证性 | 4/10 | 关键结果硬编码，脚本排除 |
| 文档一致性 | 3/10 | 正文/补充/复现指南多处矛盾 |
| **综合** | **5/10** | 指南质量高，但与正文的一致性严重不足 |

---

## 6. 期刊适配度评估

### 6.1 NAR 范围适配

NAR（Nucleic Acids Research）关注核酸研究的各个方面，包括计算方法。CKI 作为一种新的转录组比较方法，符合 NAR 的 "Methods" 类别。Ka/Ks 类比的启发式框架具有跨学科吸引力。

### 6.2 NAR 技术要求适配

| 要求 | 当前状态 | 评估 |
|------|---------|------|
| 代码公开 | GitHub + Zenodo DOI | ✅ 达标 |
| 数据可用性声明 | 包含，但来源不一致 | ⚠️ 需修订 |
| 统计严谨性 | 缺少多重检验校正 | ❌ 需补充 |
| 可复现性 | 指南详尽但与正文矛盾 | ❌ 需修订 |
| 软件版本声明 | 三重矛盾 | ❌ 需统一 |
| Graphical Abstract | 占位符 | ❌ 需准备 |
| 补充材料完整性 | 图注与正文不一致 | ❌ 需修订 |

### 6.3 竞争期刊分析

如果作者考虑其他期刊：
- **Genome Biology**：更注重大规模组学数据分析，CKI 的多数据集验证适合
- **Bioinformatics**：更注重方法学创新和算法性能，但影响因子较低
- **NAR Methods**：当前投稿目标，适配度尚可，但需解决一致性问题
- **Cell Systems**：如果强调系统生物学角度（如发育签名检测），可考虑

### 6.4 建议的修改优先级

**投稿前必须解决（阻断级）**：
1. 统一并验证 JS 对数底数（C1）
2. 统一归一化方法描述（C2）
3. 统一 bootstrap P 值公式（C3）
4. 统一软件版本号（C4）
5. 核实人类数据对数（C5）

**修订期应解决（重大级）**：
6. 增加批次效应评估（M1）
7. 增加多重检验校正或充分讨论（M2）
8. 统一所有数值矛盾（M3-M5, M10）
9. 统一数据来源描述（M8）
10. 解决硬编码值问题（M9）

**修改建议（改进级）**：
11. 准备 Graphical Abstract（m1）
12. 补充 scanpy 版本（m2）
13. 统一补充图注（m4）

---

## 7. 总结

CKI 方法具有概念创新性和实际应用价值，四数据集验证展现了方法的广泛适用性。然而，**当前投稿包存在严重的数据一致性问题**：正文、补充材料和复现指南在多个关键方法学参数（对数底数、归一化方法、P 值公式、软件版本、样本/对数计数）上相互矛盾。这些问题虽可能部分源于文档更新不同步，但直接影响了审稿人对结果可信度的判断。

**推荐决定**：Major Revision

**核心要求**：
1. 对所有数值矛盾进行逐项核实和统一
2. 提供一份 "文档一致性校验表"，确保正文、补充材料、复现指南和代码实现四个层面的完全一致
3. 补充批次效应评估和多重检验校正
4. 准备 Graphical Abstract
5. 确保 GitHub 仓库的 tag 与声明的 CKI 版本一致，且包含所有最终分析脚本

---

*审稿人声明：本报告基于所提供的四个文件进行交叉比对分析，所有矛盾点均附有具体文件和行号引用以便核实。*
