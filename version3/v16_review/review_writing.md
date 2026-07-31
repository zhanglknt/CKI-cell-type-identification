# CKI v16 写作与期刊适配审稿报告

**审稿人**: 写作与期刊适配专家
**审稿日期**: 2026-07-27
**版本**: v16

## 评分
- 写作与期刊适配评分: 7.3/10 (v14: 7.2)
- 投稿准备度（写作维度）: 72%
- Critical: 3 | Major: 8 | Minor: 10

---

## v14→v16 改进确认

### 已修复的v14 Critical Issues

| v14编号 | 问题 | v16状态 | 验证 |
|---------|------|---------|------|
| C4 | CKI缩写 Kinetic/Comparative 矛盾 | ✅ 已修复 | 标题、摘要、正文、封面信、补充材料全文统一为 "Cell-state Kinetic Index" |
| C5 | P020 softmax归一化文本重复 | ✅ 已修复 | Methods第19-20行softmax公式仅出现一次，无重复 |
| C2 | Bootstrap P值公式三方不一致 | ✅ 已修复 | Methods(行22)、Results(行43)、Statistical reporting(行37)、Supplementary Note 1.5(行26)均统一为 `P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)), capped at 1.0` |

### 已修复的v14 Major Issues

| v14编号 | 问题 | v16状态 |
|---------|------|---------|
| P0-12 | 标题 Transcriptomic/Transcriptional 不一致 | ✅ 全文统一为 "Transcriptomic" |
| P1-10 | 参考文献et al.格式 | ✅ ≤10位作者全列；>10位列前10 + et al.（如Ref 9 Siletti: 10位+et al.） |
| P0-6 | Graphical Abstract占位符 | ⚠️ 正文仍为占位符 "[A graphical abstract figure...will be provided separately]"，但按NAR惯例图表单独上传，可接受 |
| P0-4 | Unicode编码残留 (u03bc/u03c9/u2248) | ✅ 已修复，μ/ω/≈均正确渲染 |

### 未修复的v14 Issues

| v14编号 | 问题 | v16状态 |
|---------|------|---------|
| M3 | 负相关 "proving" 措辞过强 | ❌ **未修复**。摘要和正文(行52)仍使用 "proving it captures an independent information dimension" |
| C1 | 多重检验校正缺失 | ❌ 未实质解决（透明声明但未实施FDR校正） |
| C6 | k_n/k_f跨维度可比性无理论支撑 | ❌ 仍为断言 "the normalization remains internally valid"（行50），无形式证明 |

---

## NAR格式合规性检查

| 检查项 | NAR要求 | v16状态 | 备注 |
|--------|---------|---------|------|
| 摘要结构 | 非结构化（无小标题） | ✅ 合规 | 无小标题 |
| 摘要字数 | ≤200词 | ✅ 合规 | 约167词 |
| 章节顺序 | Introduction → M&M → Results → Discussion | ✅ 合规 | 顺序正确 |
| 参考文献编号 | 连续编号 (1), (2,3), (4-7) | ⚠️ 部分合规 | 正文引用格式正确，但参考文献列表未显式标注序号 |
| 作者格式 | Author,A.B. et al. (Year) | ✅ 合规 | 所有41条参考文献格式正确 |
| 期刊名斜体 | *Journal* | ✅ 合规 | 均使用 *斜体* 标注 |
| 卷号加粗 | **Vol** | ✅ 合规 | 均使用 **粗体** 标注 |
| 作者列表 | ≤10全列；>10前10+et al. | ✅ 合规 | 逐一核验41条，均符合 |
| Graphical Abstract | 必须包含 | ✅ 合规 | 占位符声明，图表单独上传（NAR惯例） |
| 封面信审稿人 | ≥6位含机构邮箱 | ✅ 合规 | 6位审稿人，均含机构邮箱 |
| AI工具声明 | 必须声明 | ✅ 合规 | "AI tools (LLMs) were used for writing assistance" |
| ORCID | 必须提供 | ✅ 合规 | 0000-0002-0698-0754 |
| 数据可用性声明 | 必须包含 | ✅ 合规 | 有独立Data availability段落 |
| 软件可用性 | 项目名/URL/DOI/OS/语言/许可证 | ✅ 合规 | 均已提供（GitHub + Zenodo DOI + MIT License） |
| 无 prior NAR submission 声明 | 必须声明 | ✅ 合规 | "has not been previously submitted to Nucleic Acids Research" |
| 图片文字大小 | ≥7pt | ❓ 无法验证 | 纯文本投稿，图片未嵌入 |
| 图片字体 | Arial/Helvetica | ❓ 无法验证 | 同上 |
| 图片DPI | 300 | ❓ 无法验证 | 同上 |
| 图片尺寸 | 单栏86mm / 双栏178mm | ❓ 无法验证 | 同上 |
| 图表面板标签 | A, B, C（大写） | ❌ 不合规 | 使用小写 (a), (b), (c)，详见M6 |

---

## Critical Issues

### C1. 参考文献42、43、44缺失（引用但未列入参考文献表）

Discussion第93行引用了三篇不存在的参考文献：

- "may be subject to stabilizing selection on expression levels **(41,42)**" — 参考文献42缺失
- "analogous to Ornstein-Uhlenbeck models **(43,44)**" — 参考文献43和44缺失

当前参考文献表共41条（编号1-41），但正文引用了42、43、44。这是编辑初审即可发现的严重格式错误，将直接导致退稿。需补充关于稳定选择对HK基因表达影响的文献（如Plotkin & Fraser等）和OU模型文献（如Butler & King 2004、Hansen 1997等），或删除这些引用。

### C2. HK基因检测方法在正文与可复现性指南之间直接矛盾

**正文（行19）**：
> "Housekeeping (HK) genes are **auto-detected from data** using a combined criterion: detection rate > 0.9 ... and coefficient of variation below the 30th percentile..."

**正文（行46）**：
> "Housekeeping genes were **auto-detected from data** using a combined criterion (detection rate > 0.9 and CV below the 30th percentile), supplemented with 1,130 human-mouse conserved reference HK genes from the HRT Atlas (4)"

**可复现性指南（行48-50）**：
> "In the analyses reported here, housekeeping (HK) genes were **NOT auto-detected**. Instead, **pre-specified HK gene lists were loaded from the HRT Atlas reference file**"

**可复现性指南（行73-76）**：
> "This auto-detection was **NOT used in the current analyses** (the pre-specified list approach was preferred for reproducibility)"

这是一个根本性矛盾：正文声称使用数据驱动自动检测（联合检测率/CV标准），可复现性指南明确声明未使用自动检测，而是使用预指定的HRT Atlas基因列表。两种方法会产生不同的HK基因集，进而导致不同的k_n和ω值。审稿人或编辑若对照阅读两份文件将立即发现此问题，严重影响方法可信度和可复现性。

**建议**：以实际代码运行为准，统一正文与可复现性指南的描述。如果实际使用的是预指定HRT Atlas列表，需修改正文Methods和Results中的HK基因检测描述。

### C3. TCGA临床分层样本量在正文与可复现性指南之间严重矛盾

| 分析 | 正文样本量 | 可复现性指南样本量 | 差异 |
|------|-----------|-------------------|------|
| LIHC Edmondson | G1=39, G2=133, G3=105, G4=11 (总288) | G1=12, G2=118, G3=127, G4=32 (总289) | 各分组n值完全不同 |
| BRCA PAM50 | LumA=224, LumB=123, HER2=55, Basal=97, Normal=7 (总506) | Basal=181, HER2=78, LumA=562, LumB=207, Normal=36 (总1064) | 总数差2倍以上 |
| LUAD突变 | EGFR=61, KRAS=120, WT=311 (总492) | EGFR=97, KRAS=152, WT=283 (总532) | 各分组n值不同 |

BRCA PAM50分析尤为严重：正文报告总506个样本进行分析，但可复现性指南报告1064个样本，而正文声明BRCA总样本量为1032 tumor。1064 > 1032，这意味着可复现性指南的数字不可能正确（超过了肿瘤样本总数）。

这些矛盾意味着审稿人无法判断哪组数字是实际分析的样本量，直接影响所有统计检验（Kruskal-Wallis P值、Jonckheere-Terpstra趋势检验）的可信度。

**建议**：以实际分析代码输出的样本量为准，统一两份文件中的所有数字。

---

## Major Issues

### M1. "proving" 措辞仍未修正（v14 M3遗留）

摘要和正文（行52）均使用：
> "proving it captures an independent information dimension"

v14审稿已指出负相关不能"prove"因果关系或独立性——负相关仅表明CKI与标准度量捕获了不同维度的信息。建议改为：
> "indicating that it captures a largely independent information dimension"

### M2. 参考文献32引用语境错误

正文行65：
> "Endothelial cells are known to express organ-specific gene programs tailored to local vascular needs **(32)**."

参考文献32 = Tran,H.T.N. et al. (2020) A benchmark of batch-effect correction methods for single-cell RNA sequencing data. *Genome Biol.*

该文献是关于批次效应校正方法基准测试的，与内皮细胞器官特异性基因程序完全无关。此处应引用Schaffenrath et al. (39)（BBB异质性）或Wälchli et al. (36)（脑血管单细胞图谱）。这是一个事实性引用错误。

### M3. Tabula Sapiens细胞类型数量不一致

- 正文（行25、50）："99 cell-type entries"
- 可复现性指南（行103）："102 cell-type entries"

同一数据集的细胞类型条目数在两份文件中不一致。需核实实际使用的细胞类型注释版本和过滤标准后统一。

### M4. 参考文献列表中存在未被正文引用的文献

以下参考文献出现在参考文献表中，但未在正文中被引用：

- **Ref 16** (Regev,A. et al. 2017, The Human Cell Atlas) — 未在正文任何位置引用
- **Ref 19** (Yang,L. et al. 2024, human fetal cerebellum) — 未在正文引用
- **Ref 24** (Storey,J.D. & Tibshirani,R. 2003, FDR) — 未在正文引用（鉴于正文讨论了多重检验校正缺失，此文献应有引用位置）
- **Ref 31** (Nei,M. & Gojobori,T. 1986, Ka/Ks方法) — 未在正文引用（鉴于正文大量讨论Ka/Ks类比，此文献应被引用）

未被引用的参考文献应删除或在适当位置加入引用。Ref 31尤其应该在Discussion讨论Ka/Ks类比时引用。

### M5. Algorithm 1中默认B值与实际分析值矛盾，且误导性暗示human/TCGA/brain使用了bootstrap

补充材料Algorithm 1（行42）：
> "for b = 1 to B (default 1,000):"

正文Methods（行22）：
> "B = 500 for the mouse pilot study"

可复现性指南检查表（行199）：
> "Verify bootstrap iterations: 500 (mouse) or 1000 (human/TCGA/brain)."

但正文和补充材料均明确声明human/TCGA/brain分析**未进行**bootstrap置换检验，仅使用描述性统计。可复现性指南检查表暗示这些数据集使用了B=1000的bootstrap，这是误导性的。Algorithm 1的默认值(1000)也与实际使用的B=500不一致。

**建议**：将Algorithm 1默认值改为500；修正可复现性指南检查表，明确"bootstrap仅用于mouse pilot study (B=500)；human/TCGA/brain未进行bootstrap"。

### M6. 图表面板标签使用小写字母，不符合NAR大写惯例

所有Figure legends使用小写面板标签：(a), (b), (c), (d), (e)。NAR要求面板标签使用大写字母：A, B, C, D, E。

例如Figure 1 legend（行112）：
> "(a) Conceptual analogy... (b) Computational pipeline... (c) Bootstrap ω distribution..."

应改为：
> "(A) Conceptual analogy... (B) Computational pipeline... (C) Bootstrap ω distribution..."

此问题存在于全部6个主图和7个补充图的图例中。

### M7. Table 1和Table 2内容缺失

正文仅包含表格标题：
- "Table 1. Classification AUC of five metrics on Tabula Sapiens (99 cell types, 4,851 pairs)."（行53后为空行）
- "Table 2. Cross-organ conservation ranking by cell type (Tabula Sapiens, n=59 same-cell-type cross-organ pairs)."（行62后为空行）

表格数据本身未出现在正文中。虽然表格可能以单独文件上传，但NAR通常要求表格嵌入正文或在稿件末尾集中排列。需确认表格内容是否已通过其他方式提交。

### M8. 脑区数量在正文内部不一致

- 正文Methods（行27）："108 brain regions"
- 正文Results（行68）："~100 brain regions"（但同一句中后续给出了各细胞类型的具体region数：astrocytes "108 regions"，与Methods一致）
- 补充材料（行86）："108 regions"
- 可复现性指南（行133）："~100 brain regions"

建议全文统一为"108 brain regions"，删除"~100"的近似表述。

---

## Minor Issues

### m1. 章节标题 "Calibration confirms baseline behavior at baseline" 冗余

行45标题中"baseline"出现两次："baseline behavior at baseline"。建议改为"Calibration confirms correct baseline behavior"或"Calibration validates baseline behavior"。

### m2. "Ka/Ks's" 所有格形式不当

行14："While CKI does not share Ka/Ks's formal mathematical properties" — "Ka/Ks's"双s结尾不规范。建议改为"the formal mathematical properties of Ka/Ks"。

### m3. "Heuristically inspired" 措辞生硬

摘要："Heuristically inspired by the Ka/Ks ratio in molecular evolution" — "Heuristically inspired"不是标准学术英语搭配。建议改为"Inspired by the Ka/Ks ratio"或"Drawing heuristic inspiration from the Ka/Ks ratio"。

### m4. "Critically" 作为句首副词使用频繁

正文中"Critically"作为句首副词出现至少3次（行55、行96两次），语感偏口语化。建议替换为"Importantly"或"Notably"，或直接删除。

### m5. "Supplementary Fig." 与 "Supplementary Figure" 缩写不一致

- 行44："Supplementary Fig. S1"（缩写）
- 行119："Supplementary Figure S1"（全称）

建议全文统一为"Supplementary Figure S1"（NAR偏好全称首次出现后缩写）。

### m6. 部分缩写首次出现时未定义

以下缩写在首次出现时未给出全称定义：
- **AUC**（行44首次出现，未定义Area Under the Curve）
- **ROC**（行29首次出现，未定义Receiver Operating Characteristic）
- **TPM**（行26首次出现，未定义Transcripts Per Million）
- **QC**（行24首次出现，未定义Quality Control）
- **IQR**（行22首次出现，未定义Interquartile Range）

建议在首次出现时给出全称定义。

### m7. Author contributions未使用CRediT分类法

行106的作者贡献使用叙述式描述，NAR推荐使用CRediT（Contributor Roles Taxonomy）分类法，如：
> "Conceptualization, X.W. and L.Z.; Methodology, L.Z.; Software, L.Z.; Validation, X.W.; Formal Analysis, L.Z.; Writing—Original Draft, L.Z.; Writing—Review & Editing, X.W. and L.Z."

### m8. 参考文献未包含DOI

虽然NAR不强制要求DOI，但NAR偏好包含DOI的参考文献。当前41条参考文献均未提供DOI。建议至少为有DOI的文献补充。

### m9. "most striking finding" 和 "key insight" 等主观评价用语

行58："The most striking finding was that..."
行91："The key insight is that..."

这些表达带有主观评价色彩，在NAR的方法学论文中宜更客观。建议改为"The principal finding was that..."和"The central concept is that..."。

### m10. 摘要中 "proving" 一词同时出现在摘要和正文

M1中提到的"proving"同时出现在摘要和正文行52中。摘要中的措辞尤为关键，因为这是编辑和审稿人首先阅读的内容。建议优先修改摘要中的表述。

---

## 优点

1. **CKI缩写全文统一**：v14的Critical命名矛盾（Kinetic vs Comparative）已完全解决，标题、摘要、正文、封面信、补充材料均一致使用"Cell-state Kinetic Index"。

2. **参考文献格式规范**：41条参考文献的作者格式、期刊名斜体、卷号粗体、年份括号等均符合NAR要求。>10作者的文献正确使用"前10+et al."格式（如Ref 9 Siletti、Ref 11 Perou、Ref 12 Parker等）。

3. **封面信要素完整**：6位审稿人（Theis, Teichmann, Welch, Yanai, Zhang, Wang）均含机构邮箱；AI使用声明、ORCID、无prior NAR submission声明、软件版本号均齐备。

4. **写作整体清晰流畅**：正文逻辑结构清晰，Introduction→Methods→Results→Discussion的标准流程完整。Discussion中对Ka/Ks类比的局限性讨论（行93）诚实且深入，体现了学术严谨性。

5. **数据可用性声明完善**：4个数据集均提供了 accession number 或 URL（GSE109774, CZ CELLxGENE, GDC portal, HRT Atlas URL），软件代码提供GitHub链接和Zenodo永久存档DOI。

6. **统计报告透明**：P值公式全文统一（双侧+1伪计数），效应量（Cohen's d）与P值并列报告，明确声明未进行多重检验校正（行37、行97），体现了概念诚实性。

7. **术语统一性改善**：v14中"baseline divergence rate"和"functional divergence rate"的术语在v16中全文一致使用，k_n/k_f/ω符号系统统一。

8. **Limitations段落结构完整**：Discussion中Limitations部分（行97）列出5条具体限制，涵盖pseudobulk分辨率、HK基因选择、HVG选择偏差、TCGA bulk分辨率、死后组织限制。

---

## 期刊推荐

| 排名 | 期刊 | IF | NAR适配度 | 录用概率（修复P0后） | 理由 |
|------|------|-----|----------|---------------------|------|
| **1** | **NAR** | ~16.0 | 7.5/10 | **35-45%** | 首选。HRT Atlas (Ref 4)、TCGAbiolinks (Ref 29)、CZ CELLxGENE (Ref 33)均发表于此。方法+多数据集验证+开源包定位与NAR方法学scope高度匹配。修复3个Critical后可投稿。 |
| 2 | Genome Biology | ~12.3 | 7.5/10 | 25-35% | 最佳备选。单细胞方法学核心期刊，对"方法+生物学发现"综合定位更包容，脑区发育签名发现更契合。 |
| 3 | Briefings in Bioinformatics | ~9.5 | 7.5/10 | 40-50% | CACIMAR (Ref 22)发表于此。完整数学推导+伪代码符合该刊偏好。录用门槛低于NAR。 |
| 4 | Cell Systems | ~9.0 | 7.0/10 | 20-30% | 系统级转录组重塑框架契合，但偏好更强数学建模基础。 |
| 5 | Bioinformatics | ~5.8 | 8.0/10 | 55-65% | 保底选项。纯计算方法学定位匹配度高，但IF偏低。 |

**投稿策略**：NAR → Genome Biology → Briefings in Bioinformatics → Bioinformatics

---

## 总体评价

v16在写作质量和NAR格式合规性方面较v14有实质性改善。v14的三个写作维度Critical issues（CKI缩写矛盾、softmax文本重复、P值公式不一致）已全部修复。参考文献格式（作者列表、期刊名斜体、卷号粗体）经逐条核验均符合NAR要求。封面信要素完整，数据/软件可用性声明规范。正文写作整体清晰，Ka/Ks类比局限性的Discussion讨论体现了学术诚实性。

然而，v16引入了三个新的Critical问题，均属于编辑性疏漏而非方法学缺陷：(1) Discussion引用了参考文献42-44但参考文献表仅有41条，三篇文献完全缺失；(2) HK基因检测方法在正文（auto-detected）与可复现性指南（NOT auto-detected, pre-specified）之间存在直接矛盾；(3) TCGA临床分层样本量在正文与可复现性指南之间严重不一致（BRCA: 506 vs 1064）。此外，参考文献32被错误引用于内皮细胞器官特异性基因程序的语境中（实际为批次效应校正基准测试论文），4篇参考文献（Ref 16, 19, 24, 31）出现在参考文献表但未在正文引用。这些编辑性错误表明v15→v16的修订过程中缺乏跨文件一致性校验。

**建议**：修复3个Critical issues（补充缺失文献/统一HK基因描述/统一TCGA样本量）和M1-M2（修正"proving"措辞/修正Ref 32错误引用）后即可投稿NAR。M6（面板标签大写）和m6（缩写定义）应在最终排版阶段一并处理。预计修复工时4-6小时。修复后NAR录用概率估计35-45%。
