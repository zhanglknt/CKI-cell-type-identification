# 数据与可复现性专家审稿报告 — CKI v12 NAR Submission

## 评分：5.5 / 10

## 总体评价

CKI 算法在概念设计上具有创新性，将 Ka/Ks 类比引入转录组比较领域是一个有启发性的思路。稿件在可复现性基础设施方面具备一定基础：代码托管于 GitHub（v0.3.1，MIT 许可证），Zenodo 归档 DOI 已标注，Python 版本和主要依赖版本已声明，随机种子固定为 42，补充材料提供了数学推导、算法伪代码和 QC 标准。这些是值得肯定的良好实践。

然而，从数据质量与可复现性角度深入审查后，发现多处严重的内部一致性问题，直接威胁结果的可复现性。最突出的问题是：正文与补充材料之间在 TCGA 样本数量、归一化方法（TPM vs FPKM）、JS 散度对数底（自然对数 vs 以2为底）、bootstrap 迭代次数（B=500 vs B=1000）等关键参数上存在直接矛盾。这些不是表述差异，而是影响计算结果实质的参数矛盾——一位试图复现该工作的研究者将无法确定应使用哪套参数。此外，跨数据集分析中批次效应的处理完全缺失，对数万次比较未进行多重检验校正，数据集版本号和访问日期均未标注，这些均不符合 NAR 对数据可复现性的要求。

综合来看，稿件的可复现性框架已搭建但关键细节存在实质性缺陷，需要大幅修订后方可达到发表标准。

## 关键问题（Critical Issues）

**1. TCGA 样本数量在正文与补充材料之间存在重大矛盾**

正文（P027）报告的 TCGA 五种癌型样本数为：LUAD 495 tumor + 76 normal、LUSC 567+58、LIHC 365+57、KIRC 755+82、BRCA 1032+109，合计 3,596 例（正文 P056 明确表述"totalling 3,596 samples"）。然而补充材料 Note 4.3 报告的数字完全不同：LUAD 515+59、LUSC 501+51、LIHC 371+50、KIRC 533+72、BRCA 1093+113，且声称"totaling n = 10,535 samples"。补充材料的分项数字之和（3,358）既不等于 10,535，也不等于正文的 3,596。这意味着三种不同的样本总数出现在稿件中，且均未给出解释。这一矛盾使得无法确定实际使用了多少样本，直接阻碍复现。

**2. TCGA 归一化方法矛盾：TPM vs FPKM**

正文 P027 明确表述："TPM values, log2(x+1) transformed。" 而补充材料 Note 1.6 和 Note 4.3 均明确表述："FPKM values from GDC, followed by log2(x+1) transformation。" TPM 和 FPKM 是两种不同的归一化方法，对同一原始计数会产生不同的表达值，进而影响所有下游 CKI 计算（k_n、k_f、ω）。这是一个直接影响计算结果的参数矛盾，必须澄清实际使用了哪种归一化方法。

**3. JS 散度对数底矛盾：自然对数 vs 以2为底**

正文 P021 明确表述："JS divergence uses the natural logarithm。" 而补充材料 Note 1.1 明确表述："When using base-2 logarithms, the JS divergence is bounded in [0, 1]." 这不仅是理论说明差异——JS 散度的值域取决于对数底数（以2为底时值域为 [0,1]，以自然对数为底时值域为 [0, ln2]）。虽然 ω = k_f/k_n 作为比值在理论上不受对数底影响（因为分子分母使用相同底数时比值不变），但 k_n 和 k_f 的绝对值、文中报告的阈值（如 k_n ≥ 0.001 的下限建议、ω cap = 1,000）、以及"JS bounded in [0,1]"的声明都取决于对数底。此外，补充材料 Algorithm 1 伪代码和 Note 1.2 均使用 softmax 但未指明对数底，正文与补充材料的描述必须统一。

**4. Bootstrap 迭代次数矛盾：B=500 vs B=1000**

正文 P023 表述："B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"（此处还存在冗余表述）。P038 和 P044 也确认"B = 500 permutations"。然而补充材料 Note 1.5 表述"default B=1,000"，Note 3.2 表述"Bootstrap iterations: B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"，Algorithm 1 伪代码第10行也标注"default 1,000"。这意味着正文中报告的所有 P 值和置信区间所基于的 bootstrap 迭代次数在正文和补充材料之间存在矛盾。不同 B 值会产生不同的经验 P 值和置信区间宽度，复现者无法确定应使用哪个 B 值。

**5. 跨数据集批次效应完全未处理且未讨论**

稿件使用 Tabula Sapiens（多供体人类数据，108,136 cells）和 Siletti 脑图谱（多供体、多脑区，888,263 nuclei）进行跨区域比较，但未提及任何批次效应校正措施（如 Harmony、scVI 等），也未讨论批次效应对 k_n（"中性偏移率"）的潜在影响。正文 P014 提到"donor-level and batch-level variation often dominates over cell-type identity"，却未说明 CKI 如何控制这些变异。k_n 被定义为捕获"技术变异"的基线，但如果不同供体的批次效应系统性地偏移 k_n，则 ω = k_f/k_n 的比值将被扭曲。对于包含多供体数据集的分析，缺乏批次效应评估是一个严重的可复现性缺陷。

**6. 大规模多重比较未进行多重检验校正**

正文明确声明未应用多重检验校正（P023："standard statistical tests were applied without multiple-testing correction; all reported P-values are raw, uncorrected values"；P038 重申此点）。对于脑图谱分析中的 31,764 次跨区域比较和 Tabula Sapiens 中的 4,851 次细胞类型对比较，未校正的 P 值将产生大量假阳性。补充材料 Note 3.3 承认"Benjamini-Hochberg FDR correction is NOT systematically applied"，但仅以"effect sizes are consistently large"为由进行辩护，未提供 FDR 校正后的结果作为对比。这不影响复现本身，但严重影响结果的可复现性和可信度——复现者可能在校正后得到不同的显著性结论。

## 主要问题（Major Issues）

**1. HVG 选择参数不一致：seurat vs seurat_v3**

正文 P025（Tabula Muris 数据描述）表述使用 `flavor="seurat"`，而 P021（方法部分）和 P043（结果部分）均表述使用"Seurat v3 flavor"（`flavor='seurat_v3'`）。补充材料 Note 4.4 也表述 Tabula Muris 使用 `flavor="seurat"`。`seurat` 和 `seurat_v3` 是 Scanpy 中两种不同的 HVG 选择算法，会产生不同的基因集，进而影响 k_f 计算和最终的 ω 值。必须澄清 Tabula Muris 分析实际使用了哪种 flavor。

**2. 归一化策略描述混乱：softmax vs sum-normalization**

正文 P020（方法部分）表述："norm is sum-normalization for non-negative single-cell data (softmax only for TCGA bulk RNA-seq)"。P021 进一步解释："Sum-normalization converts expression vectors to probability distributions for non-negative single-cell data; softmax normalization is used only for TCGA bulk RNA-seq data where negative values may occur from log-transformation。" 然而，正文 P042（结果部分，Step 1）却表述："We restrict the pseudobulk vectors to housekeeping (HK) gene indices and apply softmax normalization, which converts expression values to probabilities." 补充材料 Note 1.2 和 Algorithm 1 伪代码也统一使用 softmax。这意味着方法部分描述的 sum-normalization 与结果部分和伪代码描述的 softmax 相互矛盾。复现者无法确定单细胞数据到底使用了 sum-normalization 还是 softmax。此外，P028 描述脑图谱数据的归一化为"Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation"，这是数据预处理步骤，与 CKI 计算时的归一化（softmax/sum-norm）是不同层面的操作，但稿件未清晰区分这两个层次。

**3. 临床数据样本量不一致**

正文内部存在多处临床数据样本量矛盾：
- LIHC Edmondson 分级：P027 报告"289 tumors"，P034 报告"n = 288 tumors with both grade and expression data"
- LUAD 突变：P027 报告"497 samples (61 EGFR, 121 KRAS, 312 WT)"，但 P034 报告"n = 492 samples"，且 EGFR+KRAS+WT = 61+121+312 = 494 ≠ 497 ≠ 492
- BRCA PAM50：P059 中各亚型样本数之和为 224+123+55+97+7 = 506，但正文未明确说明总样本数是否与 BRCA tumor 总数（1,032）一致，差异部分（1,032 - 506 = 526）未解释

这些不一致使得复现者无法确定各临床分析的确切样本量。

**4. 数据集版本号和访问日期均未标注**

稿件使用了多个公开数据库，但均未标注具体版本号或访问日期：
- CZ CELLxGENE Discover（Tabula Sapiens 和 Siletti 脑图谱）：无版本号，无访问日期。CZ CELLxGENE 数据集会定期更新，不同版本可能包含不同数量的细胞和不同的注释。
- NCI Genomic Data Commons（TCGA）：无数据发布版本（data release version），无访问日期。GDC 定期更新数据处理流程和临床数据。
- HRT Atlas：虽然标注了 v1.0，但无访问日期。
- GEO GSE109774（Tabula Muris）：GEO 数据相对稳定，但仍应标注访问日期。

数据集版本不可追溯是可复现性的根本障碍——不同时间下载的数据可能产生不同结果。

**5. 仅提供 requirements.txt，缺少完整环境规范**

正文 P098 提到"A complete environment specification (requirements.txt) is provided in the GitHub repository"。但对于一个涉及多个大规模数据集和复杂依赖的计算方法，仅提供 requirements.txt 是不够的：
- 未提供 `environment.yml`（Conda 环境）或 `Dockerfile`（容器化环境），无法保证依赖冲突不影响复现。
- 虽然列出了主要依赖的最低版本（scanpy >= 1.9.0, scipy >= 1.10.0 等），但未固定确切版本（pinned versions），不同版本的 Scanpy/SciPy可能产生不同的 HVG 选择结果或统计计算结果。
- Python 3.13 于 2024 年 10 月发布，是非常新的版本，部分依赖库可能尚未完全兼容，建议同时测试 Python 3.10-3.12 的兼容性。

**6. QC 标准在不同数据集间不一致且缺乏依据**

Tabula Muris 的 QC 阈值为：检测基因 < 500 移除，线粒体比例 > 10% 移除。Tabula Sapiens 的 QC 阈值为：检测基因 < 200 移除，线粒体比例 > 20% 移除。两个数据集的阈值差异显著（500 vs 200 基因；10% vs 20% 线粒体），但稿件未解释为何使用不同阈值，也未讨论这些差异是否影响跨数据集结果的可比性。脑图谱数据（Siletti）仅描述了 ≥20 nuclei per (region, cell_type) 和 ≥50 nuclei per region 的分组阈值，但未描述细胞水平的 QC 标准（如基因检测数、线粒体比例等）。TCGA 数据未描述任何 QC 过程。

**7. 脑图谱数据集标识不完整**

正文 P028 描述脑图谱数据来源为"Siletti et al. (2023) single-nucleus RNA-seq from CZ CELLxGENE Discover"并提到"We used the Nonneurons.h5ad dataset"，但未提供 CZ CELLxGENE 的具体 collection ID 或 dataset DOI。P100（Data availability）也仅写"collection ID as referenced in [9]"，未直接给出。复现者需要自行从参考文献 [9] 推断具体数据集，这增加了复现难度。

## 次要问题（Minor Issues）

**1. 未提及 doublet 检测**

对于单细胞/单核数据（Tabula Muris、Tabula Sapiens、Siletti 脑图谱），稿件未提及是否进行了 doublet 检测和移除（如使用 Scrublet、DoubletFinder 等）。Doublets 可能影响 pseudobulk 向量的准确性，进而影响 ω 计算。

**2. 未提及环境 RNA（ambient RNA）校正**

单细胞数据的 ambient RNA 污染可能影响低表达基因的检测，进而影响 HK 基因检测和 k_n 计算。稿件未提及是否使用了 SoupX、DecontX 等工具进行校正。

**3. 软件可用性声明不完整**

NAR 要求的 Software Availability 声明应包含：项目名称、主页 URL、归档 DOI、操作系统、编程语言、许可证。稿件已包含项目名称（CKI）、主页 URL（GitHub）、归档 DOI（Zenodo）、编程语言（Python 3.13）和许可证（MIT），但未明确标注支持的操作系统。虽然 Python 跨平台，但建议明确说明。

**4. 随机种子验证不充分**

P036 提到"All random seeds were fixed at 42 for reproducibility"并提到"Stability across random seeds was verified for key results; full multi-seed validation was not performed。"但未说明具体测试了哪些种子、测试了哪些关键结果、以及结果的变化幅度。对于涉及 bootstrap 和随机排列的分析，单一种子的结果缺乏稳健性证据。

**5. 计算资源需求描述不足**

正文 P097（Limitations 第九点）简要提及脑图谱分析涉及 31,764 次比较，需要约 800 万次 ω 计算，"~8 hours on a 32-core workstation"。但未说明内存需求、磁盘空间需求、以及各数据集的分析时间，复现者难以预估所需计算资源。

**6. 未提及测试套件或 CI/CD**

GitHub 仓库（v0.3.1）的代码质量保障措施未描述。建议提及是否包含单元测试、是否设置了 CI/CD 流水线。

**7. 正文 P023 存在冗余表述**

"B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"——两次重复"B = 500 for mouse calibration"，存在编辑疏漏。

**8. 补充材料中 HK 基因数量不一致**

正文 P020 提到"HRT Atlas v1.0 consensus set (1,130 human-mouse shared HK genes)"，P047 也提到"1,130 human-mouse conserved reference HK genes"。但补充材料 Note 4.2 提到"supplemented with 1,129 genes from HRT Atlas v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog was excluded)"。1,130 vs 1,129 的差异应澄清——是因为排除1个无人类同源基因后变为1,129，还是其他原因。虽然差异微小，但影响复现的精确性。

**9. 图形摘要尚未提供**

P009 注明"[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]"，但投稿时图形摘要应已准备就绪。

## 优点（Strengths）

**1. 代码和数据开放性好**
- GitHub 仓库公开可用（v0.3.1，MIT 许可证）
- Zenodo 永久归档 DOI（10.5281/zenodo.15670808）已标注
- 所有分析脚本路径在补充材料 Data 1 中索引
- `pip install` 安装方式明确

**2. 敏感性分析设计合理**
- HK 基因集大小敏感性分析（250-1000 基因，CV < 13%）
- HVG 数量敏感性分析（1,000-4,000，r > 0.97）
- HK 基因集替代定义敏感性分析（最低10%变异基因，r > 0.95）
- 参数扫描验证最优配置（w_identity=1.0, w_pathway=0.0）
- 置换检验验证阈值校准（Strong < 0.29, Moderate < 0.51, Weak < 0.76 vs 数据驱动 0.3/0.5/0.75）

**3. 补充材料内容丰富**
- 提供了完整的数学推导（Supplementary Note 1）
- 算法伪代码（Supplementary Note 2）
- 统计检验细节（Supplementary Note 3）
- QC 标准和过滤标准（Supplementary Note 4）
- 完整的数据表和分析脚本索引

**4. 计算环境基本规范**
- Python 版本（3.13）和主要依赖版本已声明
- 随机种子固定（42）
- 主要版本要求已列出

**5. 局限性讨论坦诚且全面**
正文 P097 列出了11项局限性，涵盖方法学局限（伪bulk水平、基线基因集选择）、数据局限（bulk RNA-seq、成人单一物种）、统计局限（bootstrap 检验功效、多重比较）、和验证局限（无独立实验验证）。这种坦诚的态度有助于读者正确解读结果。

**6. 负对照设计出色**
OPCs（成人 CNS 中最活跃的迁移细胞）作为负对照产生 0 个 Strong 信号，为 multiplicative residual model 的特异性提供了有力验证。这一设计思路值得肯定。

## 具体修改建议

### 针对关键问题

**C1（TCGA 样本数矛盾）**：
- 统一正文和补充材料中的 TCGA 样本数。建议以实际使用的最终样本数为准，在正文表格和补充材料中给出完全一致的数字。
- 补充材料中的"totaling n = 10,535 samples"明显计算错误（分项之和仅为 3,358），必须修正。如果 10,535 是下载总量，应明确说明"从 10,535 个原始样本中，经过筛选后保留了 X 个样本用于分析"。
- 建议增加一个补充表格，列出每种癌型的原始下载数、QC 后样本数、进入分析的样本数。

**C2（TPM vs FPKM）**：
- 确认实际使用的归一化方法并统一全文描述。
- 如果使用 TPM，应修改补充材料；如果使用 FPKM，应修改正文。
- 建议在方法部分增加一句说明 GDC 数据的获取方式（如通过 GDC API 下载 HTSeq-TPM 还是 HTSeq-FPKM）。

**C3（JS 对数底矛盾）**：
- 统一正文和补充材料的 JS 散度对数底描述。
- 建议统一使用以2为底的对数（使 JS 值域为 [0,1]，便于解释），并在方法和补充材料中一致标注。
- 如使用自然对数，应修改补充材料中"bounded in [0, 1]"的表述（应改为 [0, ln2]）。
- 更新 ω cap = 1,000 的说明以反映正确的值域。

**C4（Bootstrap B 值矛盾）**：
- 统一正文和补充材料中的 B 值。
- 明确标注哪些分析使用了 B=500，哪些使用了 B=1000。
- 建议对所有主要分析统一使用 B≥1000，并在补充材料中提供 B=500 和 B=1000 的结果对比。
- 修正 P023 中的冗余表述。

**C5（批次效应）**：
- 在方法部分增加一节"Batch effect assessment"，说明：
  - 各数据集的供体数量和批次结构
  - 是否进行了批次效应检测（如 kBET、LISI）
  - 如果未进行批次校正，需解释理由（如 CKI 的 k_n 已捕获技术变异）
  - 建议增加补充分析：在 Tabula Sapiens 和脑图谱数据中评估供体间 k_n 的变异系数，以验证 k_n 是否有效吸收了批次效应
- 如果确实未处理批次效应，应在 Limitations 中明确增加一条。

**C6（多重检验校正）**：
- 对所有涉及大规模多重比较的分析（脑图谱 31,764 比较、Tabula Sapiens 4,851 比较），提供 Benjamini-Hochberg FDR 校正后的结果。
- 至少在补充材料中同时报告未校正和校正后的 P 值。
- 对于 30 个 Strong 信号，报告 FDR 校正后的 q 值。

### 针对主要问题

**M1（HVG flavor）**：
- 确认 Tabula Muris 实际使用的 HVG flavor 并统一全文。建议在方法部分增加一个表格，明确列出每个数据集使用的关键参数（HVG flavor、HVG/HVG数量、HK基因检测标准等）。

**M2（归一化策略）**：
- 清晰区分两个层次的归一化：(1) 数据预处理（Scanpy normalize_total + log1p）；(2) CKI 计算时的向量归一化（softmax 或 sum-normalization）。
- 统一描述 CKI 计算时使用的归一化方法。建议在方法部分和伪代码中使用一致的术语。
- 如果单细胞数据使用 sum-normalization、TCGA 使用 softmax，则在方法部分明确说明并解释原因。

**M3（临床样本量）**：
- 逐一核对并统一所有临床变量的样本量。
- 增加一个补充表格列出：每个临床变量（PAM50、Edmondson、突变状态）的原始可用样本数、与表达数据交集后的样本数、进入最终分析的样本数。

**M4（数据版本和访问日期）**：
- 在 Data Availability 部分为每个数据集增加：(1) 具体版本号或 release tag；(2) 访问日期。
- 对于 CZ CELLxGENE 数据集，提供 collection ID 和 dataset version。
- 对于 GDC 数据，提供 data release version（如 GDC Data Release 38.0）。
- 对于 HRT Atlas，标注访问日期。

**M5（环境规范）**：
- 在 GitHub 仓库中增加 `environment.yml` 或 `Dockerfile`。
- 在 `requirements.txt` 中固定确切版本号（如 `scanpy==1.9.8` 而非 `scanpy>=1.9.0`）。
- 在正文中说明支持的 Python 版本范围（如 Python 3.10-3.13）。

**M6（QC 标准）**：
- 在方法部分增加一个表格，对比列出各数据集的 QC 阈值，并解释阈值差异的原因。
- 为脑图谱数据补充细胞水平的 QC 标准描述。
- 为 TCGA 数据补充 QC 过程描述（如是否移除低质量样本、肿瘤纯度过滤标准等）。

**M7（脑图谱数据标识）**：
- 在 Data Availability 部分直接写出 CZ CELLxGENE 的 collection ID 和 dataset URL，而非仅引用参考文献。
- 明确说明使用了 Siletti 数据集的哪个版本和哪个具体文件。

### 针对次要问题

**m1-m2（Doublet 和 ambient RNA）**：
- 说明是否进行了 doublet 检测和 ambient RNA 校正。如果原始数据集已包含这些步骤（如 Tabula Muris/Sapiens 的官方处理），应引用说明。

**m3（软件可用性）**：
- 在 Software Availability 部分增加"Operating system: Platform-independent (tested on Linux/macOS/Windows)"。

**m4（随机种子）**：
- 说明具体测试了哪些种子（如 42, 123, 2024）以及关键结果的变异范围。

**m5（计算资源）**：
- 在方法部分或补充材料中增加一个表格，列出各数据集的细胞数、比较次数、计算时间、内存需求。

**m6-m9（其他）**：
- 在 GitHub 仓库增加基本测试用例。
- 修正 P023 的冗余表述。
- 在补充材料中统一 HK 基因数量描述（1,130 或 1,129）。
- 在投稿前提供图形摘要。
