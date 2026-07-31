# 写作与期刊适配审稿报告 — CKI v14 NAR Submission

## 评分：7.2 / 10（v12: 6.5/10）

## v12→v14 修复评估

### v12 的 6 个 Critical Writing Issues 修复情况

| 编号 | v12 问题 | v14 状态 | 评估 |
|------|----------|----------|------|
| C1 | JS对数底正文/补充矛盾（natural log vs. base-2） | **已修复** | 正文 P020 统一为 "base-2 logarithm (range [0, 1])"，补充材料 Note 1.1 一致使用 "log2" 和 "base-2 logarithm...bounded in [0, 1]"。全文统一。 |
| C2 | 归一化方式正文/补充矛盾（sum-normalization vs. softmax） | **已修复（但引入新问题）** | 正文 P020 和补充材料 Note 1.1/1.2/Algorithm 1 均统一为 softmax normalization。但 P020 中 softmax 描述被**完整重复了两次**（见新问题 NC1），属于修复过程中引入的新错误。 |
| C3 | TCGA样本数正文/补充矛盾（3,596 vs. 3,358/10,535） | **已修复** | 正文 P027 各癌型数字加和 = 3,596，P057 也写 "totalling 3,596 samples"；补充材料 Note 4.3 同样写 "totaling n = 3,596 samples"。全文一致，算术正确。 |
| C4 | Bootstrap B值正文/补充矛盾（B=500 vs. B=1,000） | **已修复** | 正文 P022 "B = 1,000 for primary analyses, B = 500 for calibration"，P037 一致；补充材料 Note 3.2 "B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"，Algorithm 1 "default 1,000"。全文统一。 |
| C5 | P056语法破碎句和孤立片段 | **已修复** | v12 的 "we applied per-cancer P-values are reported" 破碎句和末尾孤立片段均已消失。v14 对应段落（P057）重写为通顺的完整句子。 |
| C6 | `Cohen's danalysis` 缺失空格 | **已修复** | v14 癌症分析段落（P057-P060）中不再出现 "danalysis"，该句被重写或删除。 |

**小结：v12 的 6 个 Critical Issues 全部修复。** 修复质量整体较好，但 C2 修复过程中引入了新的文本重复问题（NC1）。

### v12 的 10 个 Major Issues 修复情况

| 编号 | v12 问题 | v14 状态 | 评估 |
|------|----------|----------|------|
| M1 | Cover Letter缺推荐审稿人 | **无法评估** | 未提供 v14 Cover Letter 文件，无法判断是否已添加推荐审稿人。**需确认。** |
| M2 | Graphical Abstract占位符 | **未修复** | P008 仍为 "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]"，无实际图片。 |
| M3 | 参考文献格式（et al.过早、期刊缩写缺句点等） | **部分修复** | 期刊缩写句点已添加（如 "*Nat. Methods*"、"*Nucleic Acids Res.*"）；最后作者前 "and" 已添加；卷号加粗已合规。但 **et al. 使用仍过早**——当前列出 6 位作者后即用 et al.，NAR 要求列出全部作者（≤10位时）或前 10 位（>10位时）。约 15 条多作者参考文献受影响。 |
| M4 | HK基因数 1,130 vs. 1,129 | **未修复** | 正文 P019/P026/P046 仍写 "1,130"；补充材料 Note 4.2 仍写 "1,129"。且补充材料 **内部也不一致**：Note 1.2 写 "1,130" 而 Note 4.2 写 "1,129"。 |
| M5 | TPM vs. FPKM | **已修复** | 正文 P026 "TPM values from UCSC Xena" 与补充材料 Note 4.3 "TPM values from UCSC Xena" 一致。 |
| M6 | P054引用括号后缺失空格 | **已修复** | v14 对应段落（P055）不再有此问题，句子已重写。 |
| M7 | P023冗余重复 | **已修复** | P022 不再有冗余括号内容。 |
| M8 | Cell-state vs. Cell-type 命名不一致 | **恶化（新问题）** | v12 仅为 Cell-state vs. Cell-type 的不一致。v14 **新引入了更严重的矛盾**：标题用 "Cell-state **Kinetic** Index" 而摘要用 "Cell-state **Comparative** Index"（见 NC2）。GitHub URL 仍为 "CKI-cell-type-identification"。 |
| M9 | P054 AUC论述重复 | **已修复** | v14 P055 仅讨论一次 AUC 比较，不再重复。 |
| M10 | 候选信号总数 7,844 vs. 7,842 | **未修复** | 正文 P075：30+1,247+6,567=7,844；补充材料 P089 仍写 "7,842 pairs (24.7%)"。差异 2 对。 |

### v12 的 10 个 Minor Issues 修复情况

| 编号 | v12 问题 | v14 状态 |
|------|----------|----------|
| m1 | P044双空格 | **已修复** |
| m2 | TCGA总数10,535算术错误 | **已修复**（改为3,596） |
| m3 | B值不一致 | **已修复**（见C4） |
| m4 | Data/Code availability未分设 | **未修复**（仍合并为单一"Data availability"章节） |
| m5 | Cover Letter跨物种声称缺支撑 | **无法评估** |
| m6 | P021 HVG参数描述混淆 | **部分修复**（P020说top-2,000 HVG，P050说top-200 DE genes，区分更清晰但仍未在同一处明确说明两种方案的使用条件） |
| m7 | 补充材料无换行 | **已修复** |
| m8 | TCGA样本数一致性 | **已修复** |
| m9 | Algorithm 1 B默认值 | **已修复** |
| m10 | P038与P023重复 | **部分修复**（P037仍有部分重复，但已精简） |

---

## 总体评价

CKI v14 相较 v12 在方法学参数一致性方面取得了决定性进步。v12 最严重的 6 个 Critical Issues——正文与补充材料在 JS 对数底、归一化方式、TCGA 样本数、Bootstrap B 值上的系统性矛盾——已全部修复。v12 的 P056 语法破碎句、"danalysis" 缺失空格等写作硬伤也已清除。参考文献格式大幅改善：期刊缩写句点、斜体、卷号加粗、最后作者前 "and" 均已合规。这使得稿件从 v12 的"基本可读但方法描述自相矛盾"状态，提升至 v14 的"方法描述基本自洽、可进入审稿流程"的状态。

然而，v14 在修复过程中引入了若干新的问题，其中最严重的是 CKI 缩写自身的矛盾：标题称 "Cell-state **Kinetic** Index" 而摘要称 "Cell-state **Comparative** Index"——这是一个编辑初审即可发现的致命性命名不一致。此外，P020 中 softmax normalization 描述被完整重复两次，P091 Discussion 中出现 Unicode 编码残留（u03bc/u03c9/u2248 未渲染为希腊字母），以及 P 值计算公式在 Methods/Algorithm 与 Results/Note 1.5 之间存在两种不同公式的混用。这些新问题虽非方法学层面的根本矛盾，但位于审稿人首先接触的标题、摘要和核心方法段落，直接影响第一印象。

从期刊适配角度看，v14 的 NAR 格式合规度较 v12 有明显提升：参考文献格式已接近 NAR 标准（仅 et al. 使用过早这一细节不合规），章节顺序基本合规，摘要合规（约 173 词非结构化单段）。但 Graphical Abstract 仍为占位符，Data/Code availability 仍未分设，HK 基因数不一致和候选信号总数不一致等数据精确性问题仍然存在。总体而言，v14 已接近可投稿状态，但需修复 2 个新引入的 Critical 问题和 5-6 个 Major 问题后方可投稿。

---

## 关键问题（Critical Issues）

### NC1. P020 softmax normalization 描述完整重复两次

**位置**: P020 (Methods, CKI computation)

**问题**: 同一段落中 softmax normalization 的定义被逐字重复：
```
...each vector is normalized to a probability distribution before JS divergence computation via softmax normalization (p_i = exp(x_i) / Σ exp(x_j)). softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j)). Then k_n = ...
```
两句完全等价，公式完全相同，构成冗余重复。

**影响**: 这是 v12 C2（归一化方式矛盾）修复过程中引入的新错误。在修复 sum-normalization → softmax 时，显然有两处独立的编辑操作未协调，导致重复。位于 Methods 核心段落，审稿人必读。

**修复建议**: 删除第二句 "softmax normalization is applied (p_i = exp(x_i) / Σ exp(x_j))."，保留第一句。

### NC2. CKI 缩写在标题与摘要中不一致

**位置**: P001 (Title) vs. P010 (Abstract)

**问题**:
- 标题 P001: "CKI: A Cell-state **Kinetic** Index for Quantifying Selective Transcriptomic Remodeling"
- 摘要 P010: "we present CKI (Cell-state **Comparative** Index)"
- 补充材料标题 P002: "CKI: A Cell-state **Kinetic** Index for Quantifying Selective **Transcriptional Reprogramming**"

CKI 的 "K" 到底代表 Kinetic 还是 Comparative？标题/补充材料用 "Kinetic"，摘要用 "Comparative"。同时，正文标题用 "Selective Transcriptomic Remodeling" 而补充材料用 "Selective Transcriptional Reprogramming"。

**影响**: 这是 v12 M8（Cell-state vs. Cell-type）问题的恶化。v12 仅存在 state/type 的用词差异，v14 新引入了 Kinetic/Comparative 的根本性矛盾。CKI 是全文核心概念，其缩写定义自相矛盾将使审稿人质疑作者的严谨性。编辑初审即可发现此问题。

**修复建议**: 统一为 "Cell-state Kinetic Index"（与标题一致），将摘要中的 "Comparative" 改为 "Kinetic"。同时统一正文和补充材料的副标题措辞（建议统一为正文版本 "Selective Transcriptomic Remodeling"）。

---

## 主要问题（Major Issues）

### NM1. P 值计算公式存在两种不同表述

**位置**: P022 (Methods) / Algorithm 1 (Supplementary) vs. P043 (Results) / Note 1.5 / P037 (Statistical reporting)

**问题**: 文中存在两种不同的 P 值计算公式：

| 位置 | 公式 | 类型 |
|------|------|------|
| P022 (Methods) | P = 2 × min(proportion of ω_null ≥ ω_obs, proportion of ω_null ≤ ω_obs) | 双侧百分位法 |
| Algorithm 1 | P ← 2 × min(pct_above, pct_below) | 双侧百分位法 |
| Note 3.2 | P = 2 × min(proportion of ω_null ≥ ω_obs, proportion of ω_null ≤ ω_obs) | 双侧百分位法 |
| P043 (Results) | The empirical P-value is the fraction of permuted ω values that exceed the observed ω (with a +1 pseudocount) | 单侧 +1 伪计数法 |
| Note 1.5 | Empirical P-value = (count(omega_null >= omega_obs) + 1)/(B + 1) | 单侧 +1 伪计数法 |
| P037 (Statistical reporting) | "empirical P-values use the +1 pseudocount formula" | 单侧 +1 伪计数法 |

**影响**: 双侧百分位法和单侧 +1 伪计数法在数学上不等价，会产生不同的 P 值。Methods/Algorithm 说双侧，Results/Statistical reporting 说单侧+伪计数。审稿人无法确定实际使用了哪种公式。这是一个方法学描述的根本性不一致。

**修复建议**: 确认代码实际使用的公式，全文统一为一种。如果校准实验使用双侧百分位法（P022 明确说明 "For the calibration experiment"），而主分析使用 +1 伪计数法，则需在每一处明确标注适用场景。

### NM2. LIHC Edmondson grade 样本数不一致

**位置**: P027 (Methods) vs. P033 (Methods) vs. P060 (Results)

**问题**:
- P027: "LIHC Edmondson grade (10): from cBioPortal, **289** tumors"
- P033: "LIHC Edmondson histological grades (10) were obtained from cBioPortal (n = **288** tumors with both grade and expression data)"
- P060: G1 (n=39) + G2 (n=133) + G3 (n=105) + G4 (n=11) = **288**

**影响**: P027 写 289，但 P033 和 P060 的实际数据加和均为 288。差异 1 个样本。位于 Methods 和 Results 的临床分析段落，审稿人会核对数字。

**修复建议**: 统一为 288（P033 和 P060 的数据一致），修正 P027 的 289。

### NM3. LUAD 突变分层样本数不一致

**位置**: P027 (Methods) vs. P033 (Methods) vs. P060 (Results)

**问题**:
- P027: "LUAD mutations: from cBioPortal, **497** samples (**61** EGFR, **121** KRAS, **312** WT)" — 加和 = 494，与 497 不符
- P033: "LUAD mutation status (EGFR, KRAS, WT) was retrieved from cBioPortal (n = **492** samples)"
- P060: "EGFR-mutant (n = **61**) and KRAS-mutant tumors (n = **120**)...wild-type tumors (n = **311**)" — 加和 = 492

**影响**: 三处数字互相矛盾：P027 总数 497（分项加和仅 494），P033 总数 492，P060 分项加和 492（且 KRAS 120≠121，WT 311≠312）。审稿人会质疑数据处理准确性。

**修复建议**: 以 P060 的实际分析数据为准（n=492: 61 EGFR + 120 KRAS + 311 WT），统一 P027 和 P033。

### NM4. Graphical Abstract 仍为占位符

**位置**: P008

**问题**: "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]" — 仍为纯文字占位符，无实际图片。v12 M2 未修复。

**影响**: NAR 要求 Graphical Abstract 与稿件一同提交。占位符在投稿时会被编辑视为格式不合规。

**修复建议**: 投稿前完成 Graphical Abstract 制作。建议内容：左侧 Ka/Ks 类比（DNA序列→Ka/Ks比值），右侧 CKI 框架（表达矩阵→k_n/k_f→ω），底部四大数据集验证流程图。5:2 横向比例。

### NM5. 补充材料内部 HK 基因数不一致

**位置**: 补充材料 Note 1.2 vs. Note 4.2

**问题**:
- Note 1.2: "1,**130** human-mouse conserved HK genes"
- Note 4.2: "1,**129** genes from HRT Atlas v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog was excluded)"

**影响**: 补充材料自身矛盾。Note 4.2 的解释（1,130 总数中 1 个无人类同源基因被排除 → 实际使用 1,129）更合理，但 Note 1.2 仍写 1,130。此问题从 v12 延续至今（v12 M4）。

**修复建议**: 全文统一为 1,129（补充材料 Note 4.2 的解释更准确），或统一为 1,130 并在首次提及处添加 "(1,129 after ortholog mapping)" 的说明。

### NM6. 候选信号总数 7,844 vs. 7,842 仍未修复

**位置**: 正文 P075 vs. 补充材料 P089

**问题**:
- 正文 P075: 30 Strong + 1,247 Moderate + 6,567 Weak = **7,844** total
- 补充材料 P089: "**7,842** pairs (24.7%)"

**影响**: v12 M10 未修复。差异 2 对。审稿人核对总数时会发现不一致。

**修复建议**: 核实实际数据文件中的总数，统一正文和补充材料。

### NM7. P091 Discussion 中 Unicode 编码残留

**位置**: P091 (Discussion, 第一段)

**问题**: 段落中出现未渲染的 Unicode 编码文本：
```
Unlike Ka/Ks—where a shared mutation rate (u03bc) cancels...
We use u03c9 < 1, u03c9 u2248 1, and u03c9 > 1 as convenient operational thresholds...
```
- `u03bc` 应显示为 μ
- `u03c9` 应显示为 ω
- `u2248` 应显示为 ≈

**影响**: 如果这些编码残留存在于 DOCX 中（而非仅文本提取问题），审稿人将看到 "u03c9" 而非 "ω"，严重影响可读性。Discussion 第一段是阐述 CKI 理论定位的关键段落。需确认是 DOCX 内容问题还是文本提取问题。

**修复建议**: 在 DOCX 中将所有 `u03bc` 替换为 μ，`u03c9` 替换为 ω，`u2248` 替换为 ≈。全文搜索确认无其他 Unicode 编码残留。

---

## 次要问题（Minor Issues）

### nm1. 参考文献中 et al. 使用仍过早

**位置**: References (P127-P167)

**问题**: 约 15 条多作者参考文献在列出 6 位作者后即使用 "et al."。NAR 格式要求列出全部作者（≤10 位时）或前 10 位（>10 位时）。例如：
- Ref 1 (Korsunsky et al. 2019): 列出 6 位后 et al.，该文实际有约 8 位作者，应全部列出
- Ref 9 (Siletti et al. 2023): 列出 6 位后 et al.，该文有数十位作者，应列出前 10 位

**修复建议**: 将所有参考文献的作者列表扩展至 NAR 要求（≤10 位全部列出，>10 位列前 10 位后 et al.）。

### nm2. 标题与补充材料标题副标题措辞不一致

**位置**: P001 (正文标题) vs. P002 (补充材料标题)

**问题**:
- 正文: "...for Quantifying Selective **Transcriptomic Remodeling**"
- 补充材料: "...for Quantifying Selective **Transcriptional Reprogramming**"

**影响**: "Transcriptomic Remodeling" 和 "Transcriptional Reprogramming" 含义相近但措辞不同，影响标题一致性。

**修复建议**: 统一为正文版本 "Selective Transcriptomic Remodeling"。

### nm3. Data/Code availability 仍合并为单一章节

**位置**: P099

**问题**: 当前为单一 "Data availability" 章节，同时包含数据来源和代码/GitHub/Zenodo 信息。NAR 建议分设 "Data availability"（数据来源）和 "Code availability"（代码、许可证、DOI）。

**修复建议**: 拆分为两个独立章节。

### nm4. P037 (Statistical reporting) 与 P022 (Bootstrap permutation test) 存在部分重复

**位置**: P037 vs. P022

**问题**: P037 重复了 P022 中关于 B 值（1,000/500）和 "无多重比较校正" 的声明。虽较 v12 已有精简，但仍存在信息冗余。

**修复建议**: P022 保留方法描述（B 值、P 值公式），P037 仅保留报告格式约定（mean ± s.d.、box plot 参数、Cohen's d 阈值等），删除重复的 B 值和校正策略声明。

### nm5. GitHub URL 与标题命名不一致

**位置**: P098/P100 vs. P001

**问题**: GitHub URL 为 `github.com/zhanglknt/CKI-cell-type-identification`（使用 "cell-type"），而标题用 "Cell-state"。v12 M8 的遗留问题。

**修复建议**: GitHub URL 不易更改（会影响 DOI 和引用），建议在 README 中明确说明 "CKI stands for Cell-state Kinetic Index" 并在代码文档中统一用 "cell-state"。

### nm6. 补充材料 Algorithm 1 的 P 值公式与 Note 1.5 不一致

**位置**: Algorithm 1 line 47 vs. Note 1.5

**问题**: Algorithm 1 使用双侧百分位法 "P ← 2 × min(pct_above, pct_below)"，而 Note 1.5 使用单侧+1伪计数法 "Empirical P-value = (count + 1)/(B + 1)"。此为 NM1 的具体表现之一。

**修复建议**: 见 NM1，统一全文 P 值公式。

### nm7. Cover Letter 要素无法评估

**位置**: 无 v14 Cover Letter 文件

**问题**: v12 指出 Cover Letter 缺少推荐审稿人（M1）和跨物种声称缺支撑（m5）。无法确认 v14 是否已修复。

**修复建议**: 确认 v14 Cover Letter 包含以下要素：(1) ≥6 位推荐审稿人（含姓名/机构/邮箱/专长理由）；(2) AI 使用声明；(3) ORCID；(4) 未曾在 NAR 投稿声明；(5) 代码可用性声明；(6) 删除或补充"跨物种一致性"声称（正文未报告小鼠-人类 ω 相关性分析）。

### nm8. P027 中 LUAD 突变样本分项加和不等于总数

**位置**: P027

**问题**: "497 samples (61 EGFR, 121 KRAS, 312 WT)" — 61+121+312=494≠497，且与 P060 的 61+120+311=492 矛盾。此为 NM3 的具体表现。

**修复建议**: 见 NM3。

---

## 优点（Strengths）

1. **v12 全部 6 个 Critical Issues 已修复**: JS 对数底、归一化方式、TCGA 样本数、Bootstrap B 值、语法破碎句、"danalysis" 空格——这些 v12 的阻断性问题已全部解决，稿件方法学描述的自洽性有了质的飞跃。

2. **参考文献格式大幅改善**: 相比 v12，期刊缩写句点（*Nat. Methods*、*Nucleic Acids Res.*）、斜体、卷号加粗、最后作者前 "and" 均已合规。40 条参考文献的总体格式质量已接近 NAR 投稿标准，仅 et al. 使用过早这一细节待修。

3. **摘要合规且精炼**: 约 173 词非结构化单段，≤200 词合规。逻辑链清晰（问题→灵感→方法→四数据集验证→结论），准确概括全文核心发现。摘要中负相关性发现（Spearman r = −0.38 to −0.57）和脑区分析（30 个 developmental origin signatures / 31,764 comparisons）的数据准确引用了正文结果。

4. **概念创新性突出**: Ka/Ks 类比的转录组化是一个优雅的跨学科构思。将"中性基线"概念从分子进化引入单细胞转录组比较，提供了现有距离度量无法捕获的信息维度。ω 与 4 种标准度量均负相关的发现是 CKI 最有力的存在价值证据。

5. **验证规模宏大且层次清晰**: 4 个独立数据集（Tabula Muris 15,057 细胞 → Tabula Sapiens 108,136 细胞 → TCGA 3,596 样本 → Siletti 脑图谱 888,263 核），从校准→人体验证→癌症应用→脑区发育分析，呈递进式验证逻辑。Introduction 中 "four scales" 表述准确（v12 的 "three scales" 已修复）。

6. **OPCs 阴性对照设计精妙**: 作为脑内最活跃迁移的细胞，OPCs 在 5,671 对比较中产生 0 个 Strong 信号——这一"零结果"有力验证了倍增残差模型的特异性，是从"检测迁移"到"检测发育起源签名"的范式重定义的关键证据。

7. **局限性讨论诚实充分**: Discussion 包含系统性局限（pseudobulk 层面、HK 基因集选择、TCGA bulk RNA-seq 分辨率、脑区分析为 post-mortem 组织、跨比较绝对值不可比），展现了科学诚实性。Ka/Ks 类比的技术局限性讨论（Discussion P093）尤为深入。

8. **开源工具完整**: Python 包 (v0.3.2, MIT License) + GitHub URL + Zenodo DOI (10.5281/zenodo.15670808) + 完整分析脚本索引，满足 NAR 的数据/代码可用性高标准。版本号从 v12 的 v0.3.1 更新至 v0.3.2，反映持续维护。

9. **补充材料结构清晰**: 相比 v12 的"单一连续文本行"问题（m7），v14 补充材料有正常的段落分隔和层级结构，包含 4 个 Supplementary Notes + 4 个 Supplementary Tables + 1 个 Supplementary Data，组织合理。

10. **正文与补充材料的 TCGA 样本数和归一化方式已完全一致**: 这两个 v12 的 Critical/Major 问题修复后，正文 P027/P026 与补充材料 Note 4.3/Note 1.6 在 TCGA 数据描述上完全对齐，审稿人可以一致地理解数据来源和处理方式。

---

## 具体修改建议

### 必须在投稿前修复（P0 — 阻断项）

| 编号 | 问题 | 修复方案 | 预计工作量 |
|------|------|----------|-----------|
| NC1 | P020 softmax描述重复两次 | 删除第二句重复的 softmax 定义 | 1 分钟 |
| NC2 | CKI缩写Kinetic vs. Comparative | 统一为 "Cell-state Kinetic Index"，修正摘要 | 5 分钟 |
| NM1 | P值公式两种表述不一致 | 确认代码实际公式，全文统一为一种 | 1 小时 |
| NM2 | LIHC Edmondson n=289 vs. 288 | 统一为 288，修正 P027 | 5 分钟 |
| NM3 | LUAD突变 n=497/121/312 vs. 492/120/311 | 统一为 492/61/120/311，修正 P027 | 10 分钟 |
| NM4 | Graphical Abstract占位符 | 制作实际图片 | 数小时 |
| NM7 | P091 Unicode编码残留 | 替换 u03bc→μ, u03c9→ω, u2248→≈ | 5 分钟 |

### 强烈建议修复（P1）

| 编号 | 问题 | 修复方案 | 预计工作量 |
|------|------|----------|-----------|
| NM5 | HK基因数 1,130 vs. 1,129 | 统一为 1,129（或加说明），修正正文+补充材料 | 15 分钟 |
| NM6 | 候选信号总数 7,844 vs. 7,842 | 核实数据，统一正文和补充材料 | 15 分钟 |
| nm1 | 参考文献 et al. 使用过早 | 扩展作者列表至 NAR 要求 | 2-3 小时 |
| nm2 | 标题副标题 Transcriptomic vs. Transcriptional | 统一为正文版本 | 2 分钟 |
| nm7 | Cover Letter 要素确认 | 确认推荐审稿人≥6位、AI声明、跨物种声称 | 1 小时 |

### 建议改进（P2）

| 编号 | 问题 | 修复方案 |
|------|------|----------|
| nm3 | Data/Code availability 分设 | 拆分为两个独立章节 |
| nm4 | P037 与 P022 重复 | 精简 P037，删除重复的 B 值和校正声明 |
| nm5 | GitHub URL 命名 | 在 README 中说明命名历史 |
| nm6 | Algorithm 1 P值公式 | 见 NM1 统一 |

---

## 期刊适配度评估

### NAR 适配度：7.5 / 10（v12: 7.0/10）

**适配优势**:
- 概念定位与 NAR "Computational Biology" 类别高度匹配——CKI 是一个新颖的计算方法，有大规模验证
- HRT Atlas [4] 发表于 NAR (Hounkpe et al. 2021)，TCGAbiolinks [16] 也发表于 NAR (Colaprico et al. 2016)，CZ CELLxGENE [31] 同样发表于 NAR (2025)，形成强引用生态链
- 4 个数据集 + 百万级细胞的验证规模满足 NAR 对方法学文章的验证要求
- 开源 Python 包 + GitHub + Zenodo DOI 满足 NAR 的可复现性标准
- 摘要格式合规（约 173 词，非结构化单段，≤200 词）
- 章节顺序基本合规（Introduction → Materials and Methods → Results → Discussion → Data availability → Acknowledgements → ...）
- 参考文献格式已接近 NAR 标准（期刊缩写句点、斜体、卷号加粗、and 连词均合规）
- v14 修复了 v12 的全部 6 个 Critical Issues，方法学描述的自洽性大幅提升

**适配障碍**:
- CKI 缩写自身矛盾（Kinetic vs. Comparative）——编辑初审即可发现
- Graphical Abstract 仍为占位符
- P 值计算公式存在两种不一致的表述
- 临床数据样本数存在细节不一致（LIHC 288/289、LUAD 492/497）
- HK 基因数 1,130/1,129 和候选信号总数 7,844/7,842 仍未统一
- 参考文献 et al. 使用仍过早
- Data/Code availability 未分设
- 仅有 2 位作者，NAR 方法学文章通常有更大合作团队
- 生物学发现多为已知现象的"再发现"（30 个 Strong 信号中 29/30 可被已知发育生物学解释），创新性集中在方法层面
- Cover Letter 要素无法确认（推荐审稿人、跨物种声称等）

**录用概率估计**: 30-40%（修复剩余 P0 问题后可提升至 35-45%）

### 备选期刊推荐排序

| 排名 | 期刊 | IF | 匹配度 | 录用概率 | 理由 |
|------|------|-----|--------|----------|------|
| 1 | **NAR** | ~16.0 | 7.5/10 | 30-40% | 首选目标。方法+大规模验证+开源工具定位匹配。HRT Atlas、TCGAbiolinks、CZ CELLxGENE 均发表于 NAR，引用生态链强。v14 方法描述自洽性已大幅提升。修复 NC1/NC2/NM1-NM3/NM7 后可投稿。 |
| 2 | **Genome Biology** | ~12.3 | 7.5/10 | 25-35% | 最佳备选。单细胞方法学核心期刊，对"方法+发现"综合定位更包容。参考文献格式要求较 NAR 宽松。脑区发育签名检测的生物学发现深度更契合该刊偏好。 |
| 3 | **Briefings in Bioinformatics** | ~9.5 | 7.5/10 | 40-50% | CACIMAR [22] 发表于此刊，形成引用匹配。方法学推导清晰（4 个 Supplementary Notes 含完整数学推导和伪代码），符合该刊对方法严谨性的要求。录用门槛略低于 NAR。 |
| 4 | **Cell Systems** | ~9.0 | 7.0/10 | 20-30% | "系统级转录组重塑量化"框架与 Cell Systems 理念契合。same-organ > different-organ 的 ω 反转是系统级发现。但偏好更强的数学建模，CKI 的启发式定位可能被认为理论深度不足。 |
| 5 | **Bioinformatics** | ~5.8 | 8.0/10 | 55-65% | 最安全的保底选项。纯计算方法学的理想归宿，录用概率最高。算法伪代码+参数扫描+开源包完整契合该刊要求。但 IF 5.8 对这样体量的工作偏低，"过度合格"风险存在。 |

### 投稿策略建议

```
第1轮 → NAR (IF ~16.0) — 修复 NC1/NC2 + NM1-NM7 + nm1-nm2 后投稿
  ↓ 被拒
第2轮 → Genome Biology (IF ~12.3)
  ↓ 被拒
第3轮 → Briefings in Bioinformatics (IF ~9.5)
  ↓ 被拒
第4轮 → Bioinformatics (IF ~5.8)
```

**投稿前最低限度修复清单**（预计 1-2 天）:
1. 修复 NC1（softmax 重复）和 NC2（CKI 缩写矛盾）—— 5 分钟
2. 修复 NM1（P 值公式统一）—— 1 小时
3. 修复 NM2/NM3（LIHC/LUAD 样本数统一）—— 15 分钟
4. 修复 NM7（Unicode 编码残留）—— 5 分钟
5. 完成 Graphical Abstract 实际制作（NM4）—— 数小时
6. 修复 NM5/NM6（HK 基因数和候选信号总数统一）—— 30 分钟
7. 参考文献作者列表扩展至 NAR 要求（nm1）—— 2-3 小时
8. 确认 Cover Letter 包含 ≥6 位推荐审稿人（nm7）—— 1 小时

完成上述修复后，NAR 录用概率可从 30-40% 提升至 35-45%。

---

*v14 审稿日期: 2026-07-26*
*审稿人: 科学写作与期刊适配专家（AI辅助）*
*稿件版本: v14 (v14_manuscript_fulltext.txt, ~11,800词; v14_Supplementary_fulltext.txt)*
*对比版本: v12 (v12_review_writing.md)*
