# CKI NAR 投稿包 v15 — 科学写作与期刊适配审稿报告

**审稿人：** 科学写作与期刊适配专家
**审稿日期：** 2026-07-27
**投稿版本：** v15

---

## 1. 总体评分：7.0 / 10

本稿件概念新颖（Ka/Ks 类比应用于转录组学），验证充分（4个数据集、百万级细胞），逻辑结构清晰，统计报告规范。但在 Cover Letter 完整性、术语一致性、图表引用准确性、参考文献 DOI 等方面存在需修正的问题。以当前状态直投 NAR 风险较高，建议修正以下 Critical 和 Major 问题后投稿。

---

## 2. Critical 问题（投稿阻断）

### C1. Cover Letter 完全缺少推荐审稿人

**位置：** cover_letter.txt 全文

**问题：** NAR 投稿要求提供至少 4–6 位推荐审稿人（附机构邮箱），并可选提供非偏好审稿人。当前 Cover Letter 未包含任何推荐审稿人信息，也未在投稿系统字段中提及。

**影响：** 这将导致编辑无法评估是否有合适的审稿人池，可能被直接退回（desk rejection）。

**建议：** 在 Cover Letter 末尾或投稿系统相应字段中补充 6 位以上推荐审稿人，每位需包含：姓名、机构、邮箱（须为机构邮箱，非 Gmail 等）、专业领域简述。推荐方向：单细胞计算方法学（2位）、分子进化/比较基因组学（1位）、癌症转录组学（1位）、神经发育/胶质细胞生物学（1位）、统计方法学（1位）。

### C2. Cover Letter 中 k_n / k_f 术语与正文不一致

**位置：** cover_letter.txt 第17行

**问题：**
- Cover Letter：k_n = "neutral offset rate"，k_f = "functional conversion rate"
- 正文（manuscript.txt 第15行）：k_n = "baseline divergence rate"，k_f = "functional divergence rate"
- 补充材料（supplementary.txt 1.2/1.3节）：k_n = "baseline divergence rate"（与正文一致），k_f = "functional conversion rate"（与正文不一致）

三处文档中 k_f 的名称出现两种叫法（"divergence rate" vs "conversion rate"），k_n 出现两种叫法（"baseline divergence rate" vs "neutral offset rate"）。编辑在审阅 Cover Letter 与正文时可能产生混淆，影响对方法的理解。

**影响：** 术语不一致是期刊审稿的常见扣分项，尤其在 Cover Letter 这种编辑首先阅读的文件中，若与正文术语不符，会显得稿件准备不严谨。

**建议：** 全文统一为正文的命名：k_n = "baseline divergence rate"，k_f = "functional divergence rate"。Cover Letter 和补充材料均需同步修改。

---

## 3. Major 问题（强烈建议修改）

### M1. 参考文献全部缺少 DOI

**位置：** manuscript.txt 第125–165行（References 全部41篇）

**问题：** NAR 参考文献格式要求 "DOI should be included where available"。当前所有41篇参考文献均未包含 DOI。部分文献（如 Tabula Muris Consortium 2018、Siletti et al. 2023 等）有明确的 DOI，应补充。

**影响：** 虽非硬性阻断，但缺少 DOI 是 NAR 编辑初审时容易注意到的格式缺陷，且影响文献可追溯性。

**建议：** 逐一查询并补充 DOI。NAR 格式为：`Author,A.B. et al. (Year) Title. *Journal*, **Vol**, Pages. doi:10.xxx/xxx`

### M2. 正文引用 "Extended Data Fig. 1" 与 NAR 体例不符

**位置：** manuscript.txt 第44行

**问题：** 正文写 "achieved the best cell-type discrimination (AUC = 0.847, Extended Data Fig. 1)"，但 NAR 不使用 "Extended Data" 概念（这是 Nature 系列期刊的体例）。NAR 使用 "Supplementary" 命名补充材料。对照 Supplementary Figure legends，对应内容应为 Supplementary Figure S1。

**影响：** 体例不符表明作者可能从其他期刊格式转换而来，降低稿件适配度评分。

**建议：** 将 "Extended Data Fig. 1" 改为 "Supplementary Fig. S1"。

### M3. Figure 5 图注与正文结果描述不匹配

**位置：** manuscript.txt 第114行（Figure 5 legend）vs 第61–64行（Results 正文）

**问题：**
- Figure 5 legend (a)："CKI ω ranking of **38 shared cell types between human and mouse**"
- Results 正文（第63行）："The cross-organ ω ranking reveals a broad spectrum of conservation across **17 cell types** (Table 2)"
- Table 2 标题："n=**59** same-cell-type cross-organ pairs"

三个数字（38 / 17 / 59）含义不同但未在文中澄清：Figure 5a 似乎描述跨物种分析（38 shared cell types between human and mouse），但 Results 正文讨论的是 Tabula Sapiens 人类数据中的跨器官保守性（17 cell types, 59 pairs）。Figure 5a 描述的跨物种分析在 Results 正文中找不到对应描述。

**影响：** 图注与正文不匹配是审稿人常见的质疑点，可能导致要求大修。

**建议：** 需明确 Figure 5 各 panel 与正文的对应关系。若 Figure 5a 确为跨物种分析，需在正文补充相关描述；若图注有误，需修正为与正文一致的 "17 cell types"。

### M4. 补充图表（Supplementary Figs S2–S7）在正文中缺少交叉引用

**位置：** manuscript.txt Results 全文

**问题：** 正文中仅有一处引用 Supplementary Figure（即 M2 中的 "Extended Data Fig. 1" → 实为 Supplementary Fig. S1），但 Supplementary Figures S2–S7 在正文 Results 中均未出现明确的交叉引用（如 "Supplementary Fig. S2"）。Supplementary Tables S1–S4 也仅在补充材料内部提及。

**影响：** NAR 要求正文中须引用所有补充图表。缺少交叉引用会让编辑和审稿人无法判断补充材料的必要性。

**建议：** 在 Results 各相应段落中补充对 Supplementary Figs S2–S7 和 Supplementary Tables S1–S4 的引用。例如：
- 校准段落引用 Supplementary Fig. S1, S2
- TCGA 段落引用 Supplementary Fig. S3
- 脑分析段落引用 Supplementary Figs S6, S7, Supplementary Tables S3, S4

### M5. Cover Letter 称 k_n / k_f 为 "orthogonal components" 缺乏形式证明

**位置：** cover_letter.txt 第17行

**问题：** Cover Letter 写 "decomposes Jensen–Shannon divergence into two orthogonal components"，但正文中仅证明 CKI ω 与标准距离度量负相关（即捕获独立信息维度），并未形式化证明 k_n 与 k_f 是正交的。"orthogonal" 一词在数学上有严格定义，此处使用不准确。

**影响：** 审稿人可能质疑 "orthogonal" 的使用是否严谨。

**建议：** 将 "orthogonal components" 改为 "two complementary components" 或 "two independent components"（基于负相关证据），或删除 "orthogonal" 一词。

### M6. 补充材料脚本文件名暴露先前投稿目标

**位置：** supplementary.txt 第76行

**问题：** 补充材料中提到 "notebooks/30_genome_biology_figures.py (Figure 6)"，脚本文件名包含 "genome_biology"，暗示图件最初为 Genome Biology 投稿准备。虽然不影响科学内容，但提交给 NAR 时暴露先前/平行投稿目标可能引起编辑疑虑。

**影响：** 轻微影响专业形象。

**建议：** 将脚本文件名中的 "genome_biology" 改为中性名称（如 "figure_generation"），或在补充材料中仅引用 GitHub 仓库而非具体脚本路径。

---

## 4. Minor 问题（建议改进）

### m1. Cover Letter 中作者单位顺序与正文不一致

**位置：** cover_letter.txt 第2–6行 vs manuscript.txt 第2–4行

**问题：** 正文 affiliation 编号为 1=CIBR, 2=IBT；Cover Letter 先列 IBT 再列 CIBR，顺序相反。

**建议：** 统一单位排列顺序，建议与正文编号顺序一致（CIBR 在前）。

### m2. tables.txt 仅含标题，无表格数据

**位置：** tables.txt

**问题：** 文件仅含两行表格标题，无实际表格内容（行列数据）。NAR 要求表格以单独文件提交（Word/Excel 格式），但当前审阅无法评估表格内容的完整性和格式合规性。

**建议：** 确认 Table1-2.docx 是否为完整表格文件，并检查表格内文字体（≥7pt, Arial/Helvetica）。

### m3. Graphical Abstract 仍为占位符

**位置：** manuscript.txt 第7–8行

**问题：** "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]" 为占位符。NAR 要求 Graphical Abstract 在投稿时提交。

**建议：** 在投稿前准备实际的 Graphical Abstract 图件（5:2 横版，单页 PDF/EPS/PNG，分辨率 ≥300 dpi）。

### m4. 摘要中 "proving it captures an independent information dimension" 措辞过强

**位置：** manuscript.txt 第10行（Abstract）

**问题：** 摘要使用 "proving" 一词，但负相关（r = −0.38 to −0.57）仅提供相关性证据，不构成形式证明。

**建议：** 改为 "demonstrating" 或 "indicating"。

### m5. 正文中部分数据声明与 Methods 重复

**位置：** manuscript.txt 第97–98行（Data availability）vs 第23–27行（Datasets）

**问题：** Data availability 段落与 Methods 中 Datasets 子节内容有较多重叠（如数据来源、GEO accession 等）。

**建议：** Methods 中仅保留方法学描述（QC 标准、预处理步骤），Data availability 段落集中列出数据来源和访问链接，避免重复。

### m6. 补充材料 Supplementary Note 1.4 中 omega 解释与正文略有出入

**位置：** supplementary.txt 第22行 vs manuscript.txt 第15行

**问题：** 补充材料 1.4 节写 "omega ~ 1: the observed transcriptomic difference is consistent with neutral expectation, with no evidence of selective reprogramming"，使用 "neutral expectation" 和 "selective reprogramming"。正文第15行使用 "baseline expectation" 和 "functional divergence"。措辞虽相近但术语不完全统一。

**建议：** 统一术语，建议正文的 "baseline/functional" 体系贯穿所有文档。

### m7. References 中 consortium/network 作者格式

**位置：** manuscript.txt 第129–132行（refs 5–8, 28）

**问题：** "Tabula Muris Consortium"、"Cancer Genome Atlas Research Network" 等 consortium 名作为作者，格式上无问题，但 NAR 有时要求 consortium 论文同时列出作者列表。建议核查 NAR 最新 author guidelines 是否有此要求。

### m8. Reference 33 (CZI Cell Science Program) 作者名格式

**位置：** manuscript.txt 第157行

**问题：** "CZI Cell Science Program (2025)" 作为作者——"CZI" 是缩写，NAR 格式通常不建议缩写作为作者名。建议核实原始发表格式，可能应为 "Chan Zuckerberg Initiative Cell Science Program" 或按原文献实际作者列表。

---

## 5. 写作质量评价

### 5.1 整体结构（优）

章节顺序完全符合 NAR 要求：Graphical Abstract → Abstract → Introduction → Materials and Methods → Results → Discussion → Data availability → Supplementary Data → Acknowledgements → Author contributions → Funding → Conflict of interest → Figure legends → References。结构完整，无遗漏。

### 5.2 摘要质量（良）

- 词数约 170 词，符合 NAR ≤200 词要求
- 非结构化单段，符合 NAR 要求
- 涵盖：动机 → 方法 → 验证 → 关键发现 → 资源可用性
- 创新点（Ka/Ks 类比）明确突出
- 关键数据（ω = 1.54, r = −0.38 to −0.57, 30 signatures, 31,764 comparisons）具体
- 不足：缺少一句明确的 "意义" 声明（如 "CKI opens new applications for..."），结尾稍显仓促

### 5.3 标题质量（良）

"CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling"

- 优点：包含方法名（CKI）、全称（Cell-state Kinetic Index）、功能描述（Quantifying Selective Transcriptomic Remodeling）
- 关注点："Selective" 一词可能暗示进化选择，但正文明确声明 CKI 是 heuristic index 而非选择度量。可考虑改为 "Differential Transcriptomic Remodeling" 或 "Baseline-Normalized Transcriptomic Divergence" 以避免歧义。但 "Selective" 也可解读为 "选择性的"（部分基因被重塑，部分不被），此解读合理，标题可接受。

### 5.4 逻辑连贯性（优）

- Introduction 从问题（标准度量局限）→ 灵感来源（Ka/Ks）→ 方法概述（CKI）→ 验证路线图（四步），逻辑流畅
- Results 按校准 → 验证 → 应用（癌症）→ 应用（脑）递进，每步回答不同问题
- Discussion 系统讨论了与 Ka/Ks 的异同、局限性和未来方向
- 特别值得肯定：明确区分 "heuristic index" 和 "formal selection measure"，避免过度声称

### 5.5 术语一致性（中）

- "CKI" = "Cell-state Kinetic Index" 全文一致 ✓
- k_n / k_f 命名在正文、Cover Letter、补充材料间不一致（见 C2）
- "housekeeping genes" / "HK genes" 混用但可接受
- "identity genes" / "HVGs" 在不同语境使用，基本可接受

### 5.6 图表引用完整性（中）

- 主图 Fig. 1–6 均在正文引用 ✓
- 表格 Table 1–2 均在正文引用 ✓
- "Extended Data Fig. 1" 应为 "Supplementary Fig. S1"（见 M2）
- Supplementary Figs S2–S7 / Tables S1–S4 缺少正文交叉引用（见 M4）

### 5.7 数据可用性声明（优）

- 所有公共数据集均提供具体来源和 accession number（GEO、CZ CELLxGENE、GDC 等）
- 代码提供 GitHub 仓库 + Zenodo DOI（永久归档）+ MIT License + 版本号（v0.3.2）
- 处理后数据矩阵包含在 Supplementary Data 中
- 这是高质量的可用性声明

### 5.8 统计报告质量（优）

- 所有 P 值标注双侧检验
- 报告效应量（Cohen's d）
- Bootstrap 参数明确（B = 1,000 / 500）
- 多重检验校正策略透明说明（未系统应用 BH FDR，已声明）
- 非常规范的统计报告

### 5.9 语言质量（良）

- 英文表达流畅，逻辑连接词使用恰当
- Discussion 中的 caveat 处理得当（"heuristic", "not a formal measure", "important technical limitations"）
- 少数措辞可优化（如 m4 中 "proving" → "demonstrating"）

---

## 6. 期刊推荐排序

### 推荐排序：Genome Biology > NAR > Briefings in Bioinformatics > Cell Systems > Bioinformatics

| 排序 | 期刊 | IF (2025) | Scope 匹配度 | 接收概率估计 | 理由 |
|------|------|-----------|-------------|-------------|------|
| 1 | **Genome Biology** | ~12.3 | ★★★★★ | 20–30% | 计算基因组学方法+多数据集验证+生物学应用的组合是 Genome Biology 的核心 scope。该刊对单细胞计算方法接受度高，且论文体量（4 数据集、百万细胞）匹配其要求。补充材料脚本名 "genome_biology_figures" 暗示作者此前也认可此匹配。 |
| 2 | **Nucleic Acids Research** | ~14.9 | ★★★★☆ | 15–25% | NAR 发表计算方法论文，且有 "Computational Biology" 类目。CKI 分析 RNA-seq 数据（核酸研究范畴），scope 勉强匹配。但 NAR 更侧重核酸生物学机制，CKI 作为纯计算方法可能被编辑认为更适合 Bioinformatics 类期刊。IF 最高但接收概率最低。 |
| 3 | **Briefings in Bioinformatics** | ~9.5 | ★★★★☆ | 30–40% | 该刊专注生物信息学方法，scope 匹配良好。但该刊偏重综述类文章，原创研究发表比例较低。CKI 作为新方法+应用的完整论文可投，但需强调方法学创新。 |
| 4 | **Cell Systems** | ~9.0 | ★★★☆☆ | 20–30% | Cell Systems 发表系统生物学和计算生物学，重视概念创新和系统级洞察。CKI 的 Ka/Ks 类比和 "baseline-normalized decomposition" 概念有吸引力，但该刊可能要求更深入的系统建模（如 OU 模型整合）。 |
| 5 | **Bioinformatics** | ~5.8 | ★★★★★ | 40–50% | 生物信息学方法的经典期刊，scope 完美匹配。CKI 有完整算法描述、开源代码、多数据集验证，满足该刊要求。IF 最低但接收概率最高，作为保底选择。 |

### 期刊选择建议

- **首选 Genome Biology**：最佳 scope-IF 平衡，且作者此前可能已有此意向（基于脚本命名）
- **若追求高 IF**：可尝试 NAR，但需做好 desk rejection 的心理准备，且需修正上述所有 Critical/Major 问题
- **若追求确定性**：Bioinformatics 几乎可保证送审，但 IF 较低
- **不建议同时投多个期刊**：建议先投 Genome Biology，被拒后转投 NAR 或 Briefings in Bioinformatics

---

## 7. 修改优先级清单

| 优先级 | 编号 | 问题 | 修改量 |
|--------|------|------|--------|
| 🔴 Critical | C1 | 补充推荐审稿人 | 中 |
| 🔴 Critical | C2 | 统一 k_n/k_f 术语 | 小 |
| 🟠 Major | M1 | 补充参考文献 DOI | 大（41篇） |
| 🟠 Major | M2 | "Extended Data Fig. 1" → "Supplementary Fig. S1" | 小 |
| 🟠 Major | M3 | Figure 5 图注与正文匹配 | 中 |
| 🟠 Major | M4 | 补充图表交叉引用 | 中 |
| 🟠 Major | M5 | Cover Letter "orthogonal" 措辞 | 小 |
| 🟠 Major | M6 | 脚本文件名去 "genome_biology" | 小 |
| 🟡 Minor | m1–m8 | 各项细节修正 | 小 |

---

## 8. 总结

CKI 是一项有概念创新性的转录组学比较方法，验证扎实、代码开源、统计规范。当前 v15 版本的科学内容质量足以支撑高水平期刊投稿，但在投稿包的形式合规性上存在明显短板——尤其是 Cover Letter 缺少推荐审稿人（C1）和术语不一致（C2）这两个 Critical 问题会直接影响编辑初审印象。建议作者花 1–2 天集中修正上述问题后投稿，首选 Genome Biology。

---

*审稿报告结束*
