# 数据与可复现性审稿报告 — CKI v14 NAR Submission

## 评分：7.0 / 10（v12: 5.5/10）

## v12→v14 修复评估

### 1. TCGA 样本数量（v12 Critical #1）——修复充分 ✅

正文 P057 明确表述"totalling 3,596 samples"，分项数字（LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109）分项之和精确等于 3,596（571+625+422+837+1141 = 3596）。补充材料 Note 4.3 同样表述"totaling n = 3,596 samples"，分项数字完全一致。v12 中补充材料报告的"10,535 samples"和完全不匹配的分项数字已被彻底消除。正文与补充材料现在完全一致。

### 2. TPM vs FPKM（v12 Critical #2）——修复充分 ✅

正文 P027 表述"TPM values from UCSC Xena, log2(x+1) transformed"，补充材料 Note 1.6 表述"TPM normalization is used instead: TPM values from UCSC Xena, followed by log2(x+1) transformation"，Note 4.3 同样表述"TPM values from UCSC Xena, followed by log2(x+1) transformation"。全文已统一为 TPM，且明确标注数据来源为 UCSC Xena（而非 GDC FPKM）。v12 中补充材料的"FPKM values from GDC"表述已彻底删除。

### 3. JS 对数底（v12 Critical #3）——修复充分 ✅

正文 P021 明确表述"JS divergence uses the base-2 logarithm (range [0, 1])"，补充材料 Note 1.1 同样表述"When using the base-2 logarithm, the JS divergence is bounded in [0, 1]"。全文统一为 base-2 logarithm，且值域声明 [0, 1] 与 base-2 一致。v12 中正文"natural logarithm"与补充材料"base-2 logarithm"的矛盾已解决。不过，补充材料 Note 1.1 中的公式 `D(p||q) = Σ p_i log2(p_i/q_i)` 中 log2 的标注也确认了对数底，一致性良好。

### 4. 归一化方法（v12 Major #2）——修复充分 ✅

正文 P020 统一表述为 softmax normalization："each vector is normalized to a probability distribution before JS divergence computation via softmax normalization (p_i = exp(x_i) / Σ exp(x_j))"，且在 P021 重复确认"softmax normalization is applied"。补充材料 Note 1.1、Note 1.2、Algorithm 1 伪代码也统一使用 softmax。v12 中"sum-normalization for single-cell, softmax for TCGA"的双轨描述已完全消除。所有数据类型（单细胞和 bulk）现在统一使用 softmax 归一化，消除了复现歧义。

### 5. Bootstrap B 值（v12 Critical #4）——修复充分 ✅

正文 P022 表述"B = 1,000 for primary analyses, B = 500 for calibration"，P037 重申"Bootstrap inference uses B = 1,000 for primary analyses and B = 500 for calibration"。补充材料 Note 1.5 表述"default B=1,000"，Note 3.2 表述"B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"，Note 3.3 表述"calibration experiment (n = 6 control pairs) reports raw bootstrap P-values"。正文和补充材料对 B=1000（主要分析）和 B=500（校准/参数扫描）的区分一致，且 P023 中 v12 的冗余表述已被删除。Algorithm 1 伪代码第10行标注"default 1,000"也与正文一致。

### 6. FDR 声明（v12 Critical #6 相关）——修复充分 ✅

正文 P037 明确表述"All reported P-values are raw bootstrap P-values without multiple testing correction"。补充材料 Note 3.3 从 v12 的"Benjamini-Hochberg FDR correction is NOT systematically applied"改为更准确的表述："raw bootstrap P-values are reported"，并明确承认不进行系统性的多重检验校正。这一声明现在与正文完全一致，不再存在"声称应用 BH 但实际未应用"的矛盾。

### 7. v12 Major #1（HVG flavor 不一致）——修复充分 ✅

正文 P025 表述"flavor="seurat""，P024 也表述"flavor="seurat""。补充材料 Note 4.4 明确表述"parameters flavor="seurat" and n_top_genes=2,000"。v12 中 P021 和 P043 出现的"Seurat v3 flavor"（`flavor='seurat_v3'`）表述已被删除。全文统一为 `flavor="seurat"`，Tabula Muris 和 Tabula Sapiens 的 HVG 选择策略（全局 vs pairwise）区分清晰。

### 8. v12 Major #3（临床数据样本量不一致）——部分改进 ⚠️

LIHC Edmondson：正文 P027 报告"289 tumors"，P034 报告"n = 288 tumors with both grade and expression data"——1例差异仍然存在（可能是1例缺乏表达数据，但未明确解释）。LUAD 突变：P027 报告"497 samples"，P034 报告"n = 492 samples"，分项之和 61+121+312=494 ≠ 497 ≠ 492——三处数字不一致仍未完全解决。BRCA PAM50：各亚型样本数之和 224+123+55+97+7=506，与 BRCA tumor 总数 1,032 的差异（526例）未解释。这些微小的数字不一致虽不影响核心结论，但对精确复现仍构成障碍。

### 9. v12 Major #4（数据版本号和访问日期缺失）——未改进 ❌

v14 仍未标注任何数据集的具体版本号或访问日期：
- CZ CELLxGENE Discover（Tabula Sapiens 和 Siletti 脑图谱）：仍无版本号，无访问日期
- NCI Genomic Data Commons（TCGA）：仍无 data release version，无访问日期
- HRT Atlas v1.0：标注了版本号但仍无访问日期
- GEO GSE109774（Tabula Muris）：仍无访问日期

这是一个直接影响可复现性的问题——不同时间下载的数据可能产生不同结果，尤其是 CZ CELLxGENE 定期更新数据集。

### 10. v12 Major #5（环境规范不足）——部分改进 ⚠️

v14 正文 P035 将 Python 版本从 3.13 改为 3.12，这是一个合理改进（3.12 是更稳定的主流版本）。但仍仅列出最低版本要求（`scanpy >= 1.9.0` 等），未固定确切版本号。未提供 `environment.yml` 或 `Dockerfile`。正文 P098 提到"A complete environment specification (requirements.txt) is provided in the GitHub repository"，但这是 v12 的遗留表述——需要确认 GitHub 仓库是否确实更新了 requirements.txt。

### 11. v12 Major #6（QC 标准不一致）——未改进 ❌

v14 补充材料 Note 4.1 和 4.2 仍保留了 v12 的 QC 阈值差异：
- Tabula Muris：<500 genes, >10% mitochondrial
- Tabula Sapiens：<200 genes, >20% mitochondrial

阈值差异原因仍未解释。脑图谱数据的细胞级 QC 标准仍未描述（仅描述分组阈值 ≥20 nuclei per group 和 ≥50 per region）。TCGA 数据的 QC 过程仍未描述。

### 12. v12 Major #7（脑图谱数据标识不完整）——未改进 ❌

Data availability 部分 P100 仍表述"Human brain atlas: CZ CELLxGENE Discover (collection ID as referenced in (9))"，未直接给出 collection ID。补充材料也未提供具体的 dataset DOI 或文件名。复现者仍需自行从参考文献 [9] 推断数据集标识。

## 总体评价

v14 版本在 v12→v14 修订中取得了实质性进展。最关键的 6 项参数矛盾（TCGA 样本数、TPM vs FPKM、JS 对数底、归一化方法、Bootstrap B 值、FDR 声明）以及 HVG flavor 不一致问题已在生成脚本层面彻底修复，正文与补充材料实现了参数一致性。这一轮修订消除了 v12 中最威胁可复现性的核心障碍——一位研究者现在可以确定应使用 TPM（而非 FPKM）、base-2 logarithm、softmax normalization、B=1000 for primary analyses 等参数，不再面临"两套参数选哪套"的困境。

然而，v14 仍遗留若干影响可复现性的重要问题。数据集版本号和访问日期的完全缺失使得数据不可追溯——这是可复现性的根本前提。批次效应的处理和讨论仍然缺失，尤其对于包含多供体的大规模数据集（Tabula Sapiens 108,136 cells、Siletti 888,263 nuclei），未评估供体间 k_n 的变异是否系统性地偏移 ω 比值。QC 标准在不同数据集间的差异仍未解释。临床数据的小型样本量不一致仍未澄清。这些遗留问题虽不如 v12 的参数矛盾那样"致命"，但持续影响独立研究者对结果的验证和复现。

从 NAR 数据与软件可用性合规角度看，v14 的 Data Availability 声明已覆盖主要数据集来源、GitHub 仓库 URL、Zenodo DOI 和 MIT 许可证，但缺少数据版本号和访问日期，且脑图谱数据标识仍依赖间接引用。Software Availability 声明缺少操作系统标注。

综合来看，v14 相比 v12 有显著改善（参数矛盾从"不可复现"级别降低到"可确定参数"级别），但数据可追溯性和批次效应评估仍是需要解决的缺口。评分从 5.5 提升至 7.0，距离 NAR 发表标准的 8.0+ 还需解决剩余的 Major 级别问题。

## 关键问题（Critical Issues）

**C1. 数据集版本号和访问日期完全缺失——数据不可追溯**

v14 继承了 v12 的这一根本缺陷。稿件使用了 4 个主要公开数据集，但均未标注版本号或访问日期：

- **CZ CELLxGENE Discover**（Tabula Sapiens 和 Siletti 脑图谱）：CZ CELLxGENE 定期更新数据集，不同版本可能包含不同数量的细胞和不同的注释。正文 P025 表述"accessed via CZ CELLxGENE Discover"，但未标注 collection version 或访问日期。P100（Data availability）也仅写"collection ID as referenced in (9)"。
- **NCI Genomic Data Commons**（TCGA）：GDC 定期更新数据处理流程和临床数据。正文 P026 表述数据来源为"NCI Genomic Data Commons, accessed via TCGAbiolinks and cBioPortal APIs"，但无 data release version（如 GDC Data Release 38.0）和访问日期。
- **HRT Atlas**：标注了 v1.0 但无访问日期。
- **GEO GSE109774**（Tabula Muris）：GEO 数据相对稳定，但仍应标注访问日期。

数据版本不可追溯是可复现性的根本障碍。两位在不同日期下载 CZ CELLxGENE 数据的研究者可能得到不同数量的细胞和不同的细胞类型注释，从而产生不同的 ω 值。NAR 要求在 Data Availability 中提供充分的信息使独立研究者能精确复现数据获取过程，缺少版本号和访问日期不符合此要求。

**建议**：在 Data Availability 部分为每个数据集增加：(1) 具体版本号或 release tag；(2) 下载/访问日期；(3) 对于 CZ CELLxGENE，提供明确的 collection ID（如 `c_...` 格式）和 dataset version hash。

**C2. 跨数据集批次效应未处理且未讨论**

v14 继承了 v12 的这一缺陷。稿件使用 Tabula Sapiens（多供体人类数据，6 个 h5ad 文件）和 Siletti 脑图谱（多供体、多脑区）进行跨区域比较，但未提及任何批次效应评估或校正。正文 P013 承认"donor-level and batch-level variation often dominates over cell-type identity"，却未说明 CKI 如何控制这些变异。

批次效应对 CKI 的潜在影响是双重的：
1. **对 k_n 的影响**：如果不同供体的 HK 基因表达因技术批次而系统性偏移，k_n 将包含供体特异性偏差而非仅捕获"技术噪声"，导致 ω = k_f/k_n 的比值被扭曲。
2. **对 ω 可比性的影响**：跨供体的 ω 比较可能被供体间差异而非细胞类型间差异所主导。

正文声称 CKI ω 对标准距离度量呈负相关（Spearman r = -0.38 to -0.57），但这不能排除批次效应贡献——如果批次效应系统性地偏移了 k_n（使所有同供体比较的 k_n 偏低），则 ω 值的分布可能被供体结构而非生物学信号所主导。

**建议**：
- 在方法部分增加"Batch effect assessment"一节，说明各数据集的供体数量和批次结构。
- 至少在补充材料中增加供体间 k_n 变异系数的分析，验证 k_n 是否有效吸收了批次效应。
- 如未进行批次校正，在 Limitations 中明确增加一条并讨论潜在影响。

**C3. 大规模多重比较未进行多重检验校正**

v14 正文 P037 明确表述"All reported P-values are raw bootstrap P-values without multiple testing correction"，补充材料 Note 3.3 也确认不进行系统性 BH 校正。声明的一致性相比 v12 已改善（不再存在"声称应用 BH 但实际未应用"的矛盾），但实质性问题未解决：

- 脑图谱分析涉及 31,764 次跨区域比较，声称发现 30 个 Strong 信号（0.09%）。在 31,764 次检验中，即使采用 Bonferroni 校正（α = 0.05/31764 ≈ 1.6×10⁻⁶），或更宽松的 BH FDR 校正，30 个信号中有多少能存活校正是不确定的。
- Tabula Sapiens 的 4,851 次比较同样缺乏校正。
- 补充材料 Note 3.3 仅以"effect sizes are consistently large"为由进行辩护，未提供 FDR 校正后的结果作为对比。

虽然 CKI 的核心主张不依赖于个别 P 值的显著性（ω 比值的负相关模式是其关键发现），但对于声称检测到"30 Strong migration candidates"和"cancer convergence"等具体生物学结论，未校正的 P 值降低了结论的可信度。

**建议**：
- 对 30 个 Strong 信号至少报告 BH FDR 校正后的 q 值。
- 在补充材料中同时报告未校正和校正后的 P 值对比表。
- 如 FDR 校正后部分信号不再显著，应在 Discussion 中诚实讨论。

## 主要问题（Major Issues）

**M1. 临床数据样本量仍存在微小不一致**

v14 仍保留 v12 的若干临床数据样本量不一致：
- LIHC Edmondson：P027 报告"289 tumors"，P034 报告"n = 288 tumors with both grade and expression data"。1 例差异可能源于表达数据缺失，但未明确解释。
- LUAD 突变：P027 报告"497 samples (61 EGFR, 121 KRAS, 312 WT)"，P034 报告"n = 492 samples"。且 61+121+312 = 494 ≠ 497 ≠ 492——三个不同数字出现在同一稿件中。
- BRCA PAM50：P059 各亚型之和 224+123+55+97+7 = 506，与 BRCA tumor 总数 1,032 的差异（526 例）未解释（可能是 Normal-like 被重新分类或 PAM50 分类失败样本）。

**建议**：在补充材料增加一个表格，逐项列出每个临床变量的原始可用样本数、与表达数据交集后的样本数、进入最终分析的样本数，并解释每处差异的原因。

**M2. QC 标准在不同数据集间不一致且缺乏依据**

v14 补充材料 Note 4.1-4.2 保留了 v12 的 QC 阈值差异：
- Tabula Muris：<500 genes, >10% mitochondrial → 移除
- Tabula Sapiens：<200 genes, >20% mitochondrial → 移除

500 vs 200 基因（2.5倍差异）和 10% vs 20% 线粒体比例（2倍差异）的阈值差异原因未解释。这种差异可能影响跨数据集 ω 值的可比性——更宽松的 QC（Tabula Sapiens）保留了更多低质量细胞，可能增大 k_n（因为更多技术噪声被纳入 pseudobulk）。

此外：
- 脑图谱数据的细胞级 QC 标准仍未描述（仅描述分组阈值 ≥20 nuclei 和 ≥50 per region）
- TCGA 数据的 QC 过程仍未描述（是否移除低质量样本、肿瘤纯度过滤标准等）

**建议**：在方法部分增加一个 QC 参数对比表，列出各数据集的 QC 阈值并解释差异原因。补充脑图谱和 TCGA 的细胞/样本级 QC 描述。

**M3. 环境规范仍不完整**

v14 将 Python 版本从 3.13 改为 3.12（合理改进），但仍仅列出最低版本要求（`scanpy >= 1.9.0` 等），未固定确切版本。不同版本的 scanpy 可能产生不同的 HVG 选择结果（尤其是 flavor="seurat" 的实现细节可能随版本变化）。未提供 `environment.yml` 或 `Dockerfile`。

正文 P098 仍表述"A complete environment specification (requirements.txt) is provided in the GitHub repository"，但需确认 GitHub 仓库（v0.3.2 tag）是否确实包含更新后的 requirements.txt。v12 审稿时 GitHub 为 v0.3.1，v14 审稿时应为 v0.3.2。

**建议**：在 GitHub 仓库中增加 `environment.yml`（Conda）和固定版本的 `requirements.txt`。在正文说明支持的 Python 版本范围和确切依赖版本。

**M4. 脑图谱数据集标识仍不完整**

Data availability P100 表述"Human brain atlas: CZ CELLxGENE Discover (collection ID as referenced in (9))"，未直接给出 collection ID。正文 P028 提到"Nonneurons.h5ad dataset"但未提供具体的文件路径或 DOI。复现者需自行从 Siletti et al. (2023) 的参考文献推断数据集标识，增加了复现难度。

**建议**：在 Data Availability 中直接写出 CZ CELLxGENE collection ID（如 Siletti 数据集的具体 `c_...` ID）和文件名，而非间接引用。

**M5. 补充材料 HK 基因数量仍有微小不一致**

正文 P020 和 P047 表述"HRT Atlas v1.0 consensus set (1,130 human-mouse shared HK genes)"，但补充材料 Note 4.2 表述"supplemented with 1,129 genes from HRT Atlas v1.0 having human orthologs, mapped by gene symbol (1 gene without human ortholog was excluded)"。v14 与 v12 一样保留了 1,130 vs 1,129 的差异。虽然差异仅 1 个基因且已有部分解释（1 个无人类同源基因被排除），但正文的"1,130 shared"与补充材料的"1,129 having human orthologs"仍需统一表述。

**建议**：在正文明确表述"HRT Atlas v1.0 包含 1,130 个 human-mouse 共有 HK 基因，其中 1,129 个在人类基因组中有同源基因映射（1个基因无人类同源映射被排除），实际使用 1,129 个"。

**M6. 正文 P020 中 softmax normalization 重复表述**

P020 中存在一段文本重复："each vector is normalized to a probability distribution before JS divergence computation via softmax normalization (p_i = exp(x_i) / Σ exp(x_j)). softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j))." 同一公式在同一段落中被连续重复两次，存在编辑疏漏。

**建议**：删除重复的 softmax 公式表述，保留一次即可。

## 次要问题（Minor Issues）

**m1. 未提及 doublet 检测**

对于单细胞/单核数据（Tabula Muris、Tabula Sapiens、Siletti 脑图谱），稿件未提及是否进行了 doublet 检测和移除。Doublets 可能影响 pseudobulk 向量的准确性。如果原始数据集的官方处理流程已包含 doublet 移除，应引用说明。

**m2. 未提及环境 RNA（ambient RNA）校正**

单细胞数据的 ambient RNA 污染可能影响低表达基因的检测，进而影响 HK 基因检测和 k_n 计算。未提及是否使用了 SoupX、DecontX 等工具。

**m3. 软件可用性声明不完整**

NAR 要求的 Software Availability 应包含：项目名称、主页 URL、归档 DOI、操作系统、编程语言、许可证。v14 已包含项目名称（CKI）、主页 URL（GitHub）、归档 DOI（Zenodo 10.5281/zenodo.15670808）、编程语言（Python 3.12）和许可证（MIT），但未标注操作系统。

**建议**：增加"Operating system: Platform-independent (tested on Linux/macOS/Windows)"。

**m4. 随机种子验证不充分**

P036 表述"All random seeds were fixed at 42"，但未说明是否验证了跨种子的结果稳定性。对于涉及 bootstrap 和随机排列的分析，建议至少在补充材料中报告 2-3 个不同种子的关键结果变异范围。

**m5. 计算资源需求描述不足**

正文未说明各数据集的分析时间、内存需求和磁盘空间需求。复现者难以预估所需计算资源。

**m6. 未提及测试套件或 CI/CD**

GitHub 仓库（v0.3.2）的代码质量保障措施未描述。建议提及是否包含单元测试或 CI/CD 流水线。

**m7. 图形摘要尚未提供**

P009 注明"A graphical abstract figure will be provided separately"，投稿时应已准备就绪。

**m8. TCGA 数据获取方式描述不够具体**

正文 P026 表述"accessed via TCGAbiolinks and cBioPortal APIs"，但未说明具体使用了哪些 API 函数/参数（如 TCGAbiolinks 的 `GDCquery/GDCdownload/GDCprepare` 流程和查询参数）。补充材料也未提供具体的 API 调用细节。对于独立复现者，仅知道"使用了 TCGAbiolinks"不足以精确复现数据获取步骤。

**建议**：在补充材料或 GitHub notebook 中增加 TCGA 数据获取的代码片段或详细参数描述。

**m9. 脑图谱细胞类型合并策略未详细说明**

正文 P028 表述"Cell types were classified by supercluster_term annotation, generating 10 major non-neuronal classes"，但未说明具体的合并规则（如哪些 supercluster_term 被合并为同一类、committed oligodendrocyte precursors 与 OPCs 的合并逻辑等）。补充材料也未提供合并映射表。

**建议**：在补充材料增加一个表格，列出原始 supercluster_term 到 10 个分析类别的映射关系。

## 优点（Strengths）

**1. v12→v14 参数矛盾修复彻底且系统化**

6 项关键参数矛盾（TCGA 样本数、TPM vs FPKM、JS 对数底、归一化方法、Bootstrap B 值、FDR 声明）和 HVG flavor 不一致问题均在生成脚本层面彻底修复。这一修复策略确保了正文和补充材料由同一脚本生成，从根本上消除了手动编辑导致的矛盾风险。这是非常值得肯定的工程化做法。

**2. 代码和数据开放性良好**

- GitHub 仓库公开可用（v0.3.2，MIT 许可证）
- Zenodo 永久归档 DOI（10.5281/zenodo.15670808）已标注
- 所有分析脚本路径在补充材料 Data 1 中索引
- pip install 安装方式明确

**3. 敏感性分析设计合理**

- HK 基因集大小敏感性分析（r > 0.95）
- HK 基因集替代定义敏感性分析（最低10%变异基因，r > 0.95）
- 参数扫描验证最优配置
- 置换检验验证阈值校准

**4. 补充材料内容丰富**

提供了完整的数学推导（Note 1）、算法伪代码（Note 2）、统计检验细节（Note 3）、QC 标准和过滤标准（Note 4）、以及完整的数据表和分析脚本索引。

**5. 负对照设计出色**

OPCs（成人 CNS 中最活跃的迁移细胞）产生 0 个 Strong 信号，为 multiplicative residual model 的特异性提供了有力验证。

**6. 局限性讨论坦诚**

正文 P097 列出了多项局限性，涵盖方法学、数据和统计维度。

**7. 计算环境基本规范**

Python 3.12（相比 v12 的 3.13 更稳定）和主要依赖版本已声明，随机种子固定（42）。

**8. 统计报告规范改善**

P037 明确表述了所有 P 值为未校正的 raw bootstrap P 值、effect size 为 Cohen's d、检验类型为 two-sided，消除了 v12 中关于统计方法的歧义。

## 具体修改建议

### 针对关键问题

**C1（数据版本和访问日期）**：
- 在 Data Availability 部分为每个数据集增加版本号和访问日期：
  - Tabula Muris: GEO GSE109774, accessed YYYY-MM-DD
  - Tabula Sapiens: CZ CELLxGENE collection ID [具体ID], version [版本], accessed YYYY-MM-DD
  - TCGA: GDC Data Release [版本号], accessed YYYY-MM-DD; UCSC Xena dataset version [版本]
  - Siletti brain atlas: CZ CELLxGENE collection ID [具体ID], version [版本], accessed YYYY-MM-DD
  - HRT Atlas v1.0, accessed YYYY-MM-DD

**C2（批次效应）**：
- 在方法部分增加"Batch effect assessment"一节
- 至少在补充材料中增加供体间 k_n 变异系数分析
- 如未校正，在 Limitations 中增加一条

**C3（多重检验校正）**：
- 对 30 个 Strong 信号报告 BH FDR q 值
- 在补充材料中提供校正前后对比表

### 针对主要问题

**M1（临床样本量）**：
- 补充材料增加样本量明细表，逐项解释差异

**M2（QC 标准）**：
- 方法部分增加 QC 参数对比表
- 补充脑图谱和 TCGA 的 QC 描述

**M3（环境规范）**：
- GitHub 增加 environment.yml 和固定版本 requirements.txt
- 正文说明 Python 版本范围

**M4（脑图谱数据标识）**：
- Data Availability 直接给出 collection ID

**M5（HK 基因数量）**：
- 正文统一表述为"1,130 conserved, 1,129 mapped"

**M6（P020 重复表述）**：
- 删除 softmax 公式的重复段落

### 针对次要问题

- 说明是否进行了 doublet 检测和 ambient RNA 校正（或引用原始数据集的官方处理）
- Software Availability 增加操作系统标注
- 补充 2-3 个不同种子的关键结果稳定性验证
- 增加计算资源需求描述（时间、内存、磁盘）
- 说明 GitHub 仓库是否包含测试套件
- 提交前完成图形摘要
- 补充 TCGA 数据获取的 API 参数细节
- 补充脑图谱 cell type 合并映射表

---

**评分说明**：v14 相比 v12 有实质性改善，核心参数矛盾已从生成脚本层面彻底修复（+1.5分），统计报告规范性改善（+0.5分），Python 版本合理化（+0.5分）。但数据版本可追溯性、批次效应、QC 不一致等遗留 Major 问题仍拖累评分（-1.0分），多重检验校正的实质性问题未解决（-0.5分）。综合评分 7.0/10，如能解决 3 个 Critical 和 6 个 Major 问题，可达到 8.5-9.0 的水平。
