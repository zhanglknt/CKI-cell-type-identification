# 写作与期刊适配专家审稿报告 — CKI v12 NAR Submission

## 评分：6.5 / 10

## 总体评价

CKI v12 相较 v11 在写作质量上取得了实质性进步。v11 版本中最严重的4处文本损坏（`exhibitedthe`、`classifierCKI`、`limitedwarranting`、孤立句子片段）中，前3处已在 v12 中修复；3处中文标点（`，`和`（）`）已全部替换为英文标点；40条参考文献已从 Vancouver 格式转换为接近 NAR 格式的结构（作者名逗号分隔、年份括号化、期刊名分离）。这些修复使得稿件从"不可投稿"状态提升至"基本可读但仍有阻塞性问题"的状态。Cover Letter 已包含 ORCID、AI 使用声明、未曾在 NAR 投稿声明、代码可用性等 NAR 必要要素。

然而，v12 仍存在若干不应在投稿版本中出现的问题。最突出的是正文与补充材料之间的系统性不一致——主文与补充材料在 JS 散度对数底（natural log vs. base-2）、归一化方式（sum-normalization vs. softmax）、TCGA 样本数（3,596 vs. 10,535/3,358）、bootstrap 迭代数（B=500 vs. B=1,000）等关键方法学参数上存在直接矛盾。v11→v12 的修复显然仅作用于正文，未同步至补充材料，导致修复引入了新的不一致问题。此外，`Cohen's danalysis`（v11 已标注为 Major 问题 M2）在 v12 中仍未修复，P056 段落存在语法破碎句和孤立句子片段，P054 段落有引用括号后缺失空格。这些问题虽然数量不多，但位于 Results 核心段落，直接影响审稿人的阅读体验。

从期刊适配角度看，稿件在概念定位（novel computational method）、验证规模（4个数据集、百万级细胞）、开源工具（Python包+GitHub+Zenodo DOI）等方面与 NAR 的 "Methods" 类文章定位匹配良好。但 Cover Letter 仍缺少 NAR 要求的6位以上推荐审稿人，Graphical Abstract 仍为占位符，参考文献格式虽已大幅改善但仍未完全合规（et al. 使用过早、期刊缩写缺句点、联合体作者首字母小写）。这些问题虽非致命性，但在 NAR 编辑初审阶段可能触发"格式不合规"退修。

---

## 关键问题（Critical Issues）

### C1. 正文与补充材料在 JS 散度对数底上直接矛盾

**位置**: 正文 P021 (line 21) vs. 补充材料 Supplementary Note 1.1

**问题**:
- 正文 P021: "JS divergence uses the **natural logarithm**"
- 补充材料 Note 1.1: "D(p||q) = Σ p_i **log2**(p_i/q_i). When using **base-2 logarithms**, the JS divergence is bounded in [0, 1]"

**影响**: 对数底直接影响 JS 散度的数值范围和 ω 的绝对大小。正文与补充材料矛盾意味着审稿人无法确定实际实现使用的是哪个对数底。这是 v11→v12 声称已修复的7个 P0 问题之一（"JS对数底"），但修复仅在正文中完成，未同步至补充材料，引入了新的不一致。

**修复建议**: 统一为 natural logarithm（自然对数）。补充材料 Note 1.1 中将 `log2` 改为 `ln` 或 `log_e`，并将 "When using base-2 logarithms, the JS divergence is bounded in [0, 1]" 修改为 "When using natural logarithms, the JS divergence is bounded in [0, ln 2]"。需确认实际代码使用的是哪个对数底，以代码实现为准统一全文。

### C2. 正文与补充材料在归一化方式上直接矛盾

**位置**: 正文 P021 (Methods) vs. P042 (Results) vs. 补充材料 Note 1.1/1.2/1.3/Algorithm 1

**问题**:
- 正文 P021 (Methods): "norm is **sum-normalization** for non-negative single-cell data (**softmax only for TCGA** bulk RNA-seq)"
- 正文 P042 (Results): "We restrict the pseudobulk vectors to housekeeping (HK) gene indices and apply **softmax normalization**, which converts expression values to probabilities" — 此处描述的是单细胞数据的 HK 基因
- 补充材料 Note 1.1: "Before CKI computation, **softmax normalization** is applied to convert raw expression vectors into probability distributions"
- 补充材料 Note 1.2: "k_n = JS(**softmax**(μ_A[H]), **softmax**(μ_B[H]))" — 无条件使用 softmax
- 补充材料 Algorithm 1: "k_n <- JS_divergence(**softmax**(mu_A_H), **softmax**(mu_B_H))" — 无条件使用 softmax

**影响**: Methods 说单细胞数据用 sum-normalization、softmax 仅用于 TCGA，但 Results 和补充材料在描述单细胞数据时使用了 softmax。归一化方式直接影响 k_n 和 k_f 的数值，审稿人无法确定实际使用的归一化方法。这是一个方法学描述的根本性矛盾。

**修复建议**: 确认代码实际使用的是哪种归一化（根据补充材料的伪代码，softmax 是无条件使用的），然后统一正文 Methods 描述：删除 "sum-normalization for non-negative single-cell data" 的说法，统一为 "softmax normalization for all data types" 或明确区分何时使用 sum-normalization、何时使用 softmax。

### C3. 正文与补充材料在 TCGA 样本数上严重不一致

**位置**: 正文 P027 vs. 补充材料 Note 4.3

**问题**:
- 正文 P027: LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109 = **3,596** total; 正文 P056 也写 "totalling 3,596 samples"
- 补充材料 Note 4.3: LUAD 515+59, LUSC 501+51, LIHC 371+50, KIRC 533+72, BRCA 1093+113 = **3,358** total（但补充材料错误地写为 "totaling n = 10,535 samples"）

**影响**: 每个癌型的肿瘤和正常样本数均不同，总计也不同。3,596 vs. 3,358 差异达 238 个样本。补充材料中的 10,535 总数更是明显错误（实际加和仅 3,358）。审稿人会质疑数据处理的准确性。

**修复建议**: 核实 TCGA 实际使用的样本数（以代码中实际加载的样本为准），统一正文和补充材料的数字。修正补充材料中 "10,535" 的明显算术错误。

### C4. 正文与补充材料在 bootstrap B 值上不一致

**位置**: 正文 P023/P038/P044 vs. 补充材料 Note 3.1/3.2

**问题**:
- 正文 P023: "B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"（此处还包含冗余重复，见 M3）
- 正文 P038: "Bootstrap inference uses B = 500 permutations"
- 正文 P044: "bootstrap permutation testing (B = 500)"
- 补充材料 Note 3.1: "Bootstrap permutation test (B=**1,000**) for CKI omega significance inference"
- 补充材料 Note 3.2: "Bootstrap iterations: B=**1,000** for all primary results (B=500 used for the Phase 3.2 parameter sweep)"

**影响**: 正文统一使用 B=500，补充材料说主分析用 B=1,000、参数扫描用 B=500。审稿人无法确定实际使用的迭代数。这直接影响 P 值的最小可达到值（B=500 时最小 P ≈ 0.002，B=1,000 时最小 P ≈ 0.001）。

**修复建议**: 确认实际代码使用的 B 值，统一全文。如果校准用 500、主分析用 1,000，则需在正文和补充材料中均明确区分；如果统一用 500，则修正补充材料。

### C5. P056 段落存在语法破碎句和孤立句子片段

**位置**: P056 (line 56)

**问题**: 段落中间有一句语法破碎的句子：
```
For analyses spanning multiple cancer types, we applied per-cancer P-values are reported in Supplementary Tables for reference.
```
这句话语义不通——"we applied per-cancer P-values are reported" 是两个句子的片段被错误合并。段落末尾还有一孤立句子片段：
```
...ω magnitudes, which are not directly comparable to single-cell-derived ω values.
```
这是一个无主句的句子片段，没有完整的主谓结构。

**影响**: P056 是癌症分析的第一段（Results 核心段落），语法破碎直接影响审稿人对方法的理解。孤立片段是 v11 的 C4 问题，在 v12 中仍未修复。

**修复建议**: 
1. 将 "For analyses spanning multiple cancer types, we applied per-cancer P-values are reported in Supplementary Tables for reference." 重写为 "For analyses spanning multiple cancer types, per-cancer P-values are reported in Supplementary Tables for reference."
2. 删除末尾的孤立片段 `ω magnitudes, which are not directly comparable to single-cell-derived ω values.`（因为前文已说明 "interpretation focuses on relative patterns (tumor vs. normal) rather than absolute ω magnitudes"，此片段是冗余残留）

### C6. `Cohen's danalysis` 缺失空格——v11 已标注但 v12 仍未修复

**位置**: P057 (line 57)

**问题**: `Bootstrapped Cohen's danalysis revealed cancer-specific NN–TT contrasts`
- `d` 和 `analysis` 之间缺失空格
- 应为 `Cohen's d analysis`

**影响**: v11 审稿报告将此问题标记为 Major (M2)，v12 声称修复了所有 P0 问题，但此问题仍然存在。这表明 v11→v12 的修复流程存在遗漏。该错误位于 Results 癌症分析段落，是审稿人必读内容。

**修复建议**: 将 `Cohen's danalysis` 改为 `Cohen's d analysis`。

---

## 主要问题（Major Issues）

### M1. Cover Letter 缺少 NAR 要求的6位以上推荐审稿人

**位置**: v12_cover_letter_fulltext.txt

**问题**: NAR 投稿规范要求 Cover Letter 必须包含6位以上推荐审稿人。当前 Cover Letter 包含 ORCID、AI 使用声明、代码可用性声明、未曾在 NAR 投稿声明，但完全没有推荐审稿人信息。v11 审稿报告已标注此问题（m3），v12 未修复。

**修复建议**: 在 Cover Letter 末尾添加 "Suggested Reviewers" 章节，列出至少6位推荐审稿人（含姓名、机构、邮箱、专长理由）。推荐人选可包括：单细胞方法学学者（如 Tabula Sapiens 相关）、Ka/Ks 进化生物学学者、脑区发育生物学学者、TCGA 癌症转录组学学者、HK 基因数据库学者、JS 散度信息论学者。

### M2. Graphical Abstract 仍为占位符

**位置**: P008-P009 (line 8-9)

**问题**: `[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]` — 仅有占位符文字，无实际图片。NAR 要求 Graphical Abstract 与稿件一同提交。

**修复建议**: 投稿前完成 Graphical Abstract 制作。建议内容：左侧展示 Ka/Ks 类比（DNA序列→Ka/Ks），右侧展示 CKI 框架（表达矩阵→k_n/k_f→ω），底部展示四大数据集验证流程。符合 5:2 横向比例。

### M3. 参考文献格式部分不合规

**位置**: References (line 126-165)

**问题汇总**:

| 问题 | 当前格式 | NAR 要求 | 影响范围 |
|------|----------|----------|----------|
| et al. 使用过早 | `Korsunsky,I., Millard,N., Fan,J. et al.` (3人后) | 最多列出20位作者后才用 et al. | 约30/40条多作者参考文献 |
| 期刊缩写缺句点 | `Nat Methods` | `*Nat. Methods.*`（斜体+句点） | 全部40条 |
| 联合体作者首字母小写 | `Overall c, Logistical c` | `Overall, C., Logistical, C.` | Ref 5 (Tabula Muris) |
| DOI 以 URL 形式包含 | `https://doi.org/10.1038/...` | NAR 通常不含 DOI 或仅用纯 DOI | 全部40条 |
| "and" 缺失 | `Author,A., Author,B., Author,C. et al.` | 最后一位作者前用 "and" | 全部多作者参考文献 |

**说明**: v11→v12 的参考文献格式转换是最大的改进之一，从 Vancouver 格式（`1. Author A, Author B. Title. Journal Year;Vol:Pages.`）成功转换为 NAR 框架结构（`Author,A. (Year) Title. Journal, Vol, Pages.`）。年份位置、作者名格式已合规。但上述5个细节仍不合规。

**修复建议**: 
1. 将所有参考文献的 et al. 前作者列表扩展至至少前6位（或全部列出，如不超过20位）
2. 期刊名添加句点并确保 DOCX 中为斜体：`Nat Methods` → `*Nat. Methods*`
3. 修正 Ref 5: `Overall c` → `Overall, C.`、`Logistical c` → `Logistical, C.`
4. 考虑移除 DOI URL 或改为纯 DOI 格式
5. 最后一位作者前用 "and" 替代逗号

### M4. 正文与补充材料在 HK 基因数上不一致

**位置**: 正文 P020/P026/P047 vs. 补充材料 Note 4.2

**问题**:
- 正文: "1,**130** human-mouse shared HK genes"（P020、P026、P047 三处均写 1,130）
- 补充材料 Note 4.2: "1,**129** genes from HRT Atlas v1.0 having human orthologs, mapped via gene symbol (1 gene without human ortholog was excluded)"

**影响**: 差异虽小（1个基因），但反映了正文与补充材料的数据同步问题。审稿人可能质疑数据准确性。

**修复建议**: 统一为 1,129（补充材料的解释更详细：1,130 总数中 1 个无人类同源基因被排除，实际使用 1,129）。在正文首次提及处添加 "(1,129 after ortholog mapping)" 的说明。

### M5. TCGA 归一化方式不一致（TPM vs. FPKM）

**位置**: 正文 P027 vs. 补充材料 Note 4.3

**问题**:
- 正文 P027: "**TPM** values, log2(x+1) transformed"
- 补充材料 Note 4.3: "**FPKM** values from GDC, followed by log2(x+1) transformation"

**影响**: TPM 和 FPKM 是不同的归一化方法，产生不同的表达值，直接影响 CKI ω 的计算结果。审稿人无法确定实际使用了哪种归一化。

**修复建议**: 核实实际代码使用的归一化方式，统一正文和补充材料。如果使用的是 GDC 提供的 TPM 值，则修正补充材料；如果使用的是 FPKM，则修正正文。

### M6. P054 段落引用括号后缺失空格

**位置**: P054 (line 54)

**问题**: `that no standard metric detects. (Fig. 3C)Although CKI yielded a lower cell-type`
- `(Fig. 3C)` 和 `Although` 之间缺失空格
- 应为 `(Fig. 3C) Although` 或将引用移至句末

**影响**: 虽为排版细节，但位于 Results 核心论述段落，影响阅读流畅性。

**修复建议**: 将 `(Fig. 3C)` 移至前一句末尾的正确位置，或在括号后添加空格。

### M7. P023 冗余重复

**位置**: P023 (line 23)

**问题**: `(B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration)` — 同一信息在同一括号内重复两次。

**修复建议**: 删除冗余部分，改为 `(B = 500 for mouse calibration and exploratory analyses)`。

### M8. "Cell-state" vs. "Cell-type" 命名不一致——v11 已标注但 v12 未修复

**位置**: 标题 vs. 正文 vs. GitHub URL

**问题**:
- 标题: "Cell-**state** Kinetic Index"（使用 "Cell-state"）
- GitHub URL: `CKI-cell-**type**-identification`（使用 "cell-type"）
- 正文: "Cell-state" 仅出现3次（标题+摘要），"cell-**type**" 出现55次
- Cover Letter: "Cell-state Kinetic Index" 但随后写 "cell identity" 和 "cell states"

**影响**: v11 审稿报告将此问题标记为 Major (M4)，v12 未修复。CKI 到底量化 "cell state" 还是 "cell type" 的分歧会影响审稿人对概念的理解。GitHub URL 中的 "cell-type" 与标题不一致，影响代码可发现性。

**修复建议**: 两种方案择一：
- **方案A（推荐）**: 统一为 "Cell-state"，正文中指代 CKI 概念时用 "cell state"，仅在指代具体细胞类型标注时用 "cell type"。GitHub URL 不易更改，可在 README 中说明。
- **方案B**: 统一为 "Cell-type"，修改标题为 "Cell-type Kinetic Index"。

### M9. P054 AUC 论述过度重复

**位置**: P054 (line 54)

**问题**: 同一段落内3次讨论 AUC 0.716 vs 0.887 的比较：
1. `CKI showed moderate cell-type classification performance (AUC = 0.716...but below cosine distance at AUC = 0.887...)`
2. `We note that CKI's AUC (0.716) and cosine distance's AUC (0.887) are not directly analogous...`
3. `Although CKI yielded a lower cell-type classification AUC than cosine similarity...`

**影响**: v11 审稿报告标注此问题（m1），v12 未修复。同段内反复强调同一观点显得论证冗余。

**修复建议**: 合并为一次完整论述，删除第2和第3次重复，保留最完整的版本。

### M10. 补充材料 Table 4 候选信号总数与正文不一致

**位置**: 正文 P075 vs. 补充材料 Table 4

**问题**:
- 正文 P075: 30 Strong + 1,247 Moderate + 6,567 Weak = **7,844** total
- 补充材料 Table 4: **7,842** pairs (24.7%)

30 + 1,247 + 6,567 = 7,844，但补充材料总计为 7,842，差异2对。

**修复建议**: 核实实际数据文件中的总数，统一正文和补充材料。

---

## 次要问题（Minor Issues）

### m1. P044 双空格

**位置**: P044 (line 44)

**问题**: `without multiple testing.  The empirical` — 两个空格。

**修复建议**: 删除多余空格。

### m2. 补充材料 Note 4.3 中 TCGA 总样本数算术错误

**位置**: 补充材料 Note 4.3

**问题**: "totaling n = 10,535 samples" — 但各项加和仅 3,358（515+59+501+51+371+50+533+72+1093+113）。10,535 是明显错误。

**修复建议**: 修正为正确的总数。如果以正文 P027 的数字为准，应为 3,596。

### m3. 补充材料 Note 3.1 中 B=1,000 与正文 B=500 不一致

此问题已在 C4 中详述，此处不再重复。补充材料的统计测试描述需与正文统一。

### m4. Data/Code availability 未分设

**位置**: P099-P100

**问题**: 当前合并为单一 "Data availability" 章节。NAR 建议分设 "Data availability"（仅数据来源）和 "Code availability"（GitHub URL + Zenodo DOI + 许可证 + 编程语言）。

**修复建议**: 拆分为两个独立章节。

### m5. Cover Letter 中 "cross-species consistency" 声称缺乏正文支撑

**位置**: v12_cover_letter_fulltext.txt

**问题**: Cover Letter 声称 "cross-species consistency—mouse orthologs show strong correlation with human CKI ω, confirming evolutionary conservation"，但正文中未报告小鼠-人类 ω 相关性分析。Cover Letter 中的声称必须由正文数据支撑。

**修复建议**: 要么在正文中补充小鼠-人类 ω 相关性分析（如果已做），要么从 Cover Letter 中删除此声称。

### m6. P021 (Methods) 中 HVG 参数描述混淆

**位置**: P021 (line 21)

**问题**: 段落中先说 `k_f = JS(...), where I is the set of the top-200 most differentially expressed genes per cell-type pair`，随后又说 `The choice of 2,000 HVGs follows the Scanpy default parameter`。200（人成对 DE 基因）和 2,000（小鼠全局 HVG）是不同方案，但在同一段落中未明确区分何时使用哪个。

**修复建议**: 明确说明 "For mouse calibration, identity genes are the top-2,000 global HVGs (Scanpy default). For human pairwise comparisons, identity genes are the top-200 DE genes per pair."

### m7. 补充材料格式为一整行无换行

**位置**: CKI_NAR_Supplementary_fulltext.txt

**问题**: 补充材料全文为单一连续文本行（0个换行符，15,517字符在一行内），不可读。虽然在 DOCX 中可能有正常排版，但从文本提取角度看，这影响自动化检查和审稿人的文本搜索。

**修复建议**: 确认 DOCX 中的排版是否正常。如果是，此问题仅影响文本提取，不影响投稿。但建议在提交前确认 DOCX 排版正确。

### m8. P027 (Methods) 中 TCGA 样本数与 P056 (Results) 的一致性

正文 P027 和 P056 均写 "3,596 samples"——内部一致，但与补充材料矛盾（见 C3）。此处仅提示正文内部一致但需与补充材料同步。

### m9. 补充材料 Algorithm 1 中 B 的默认值

**位置**: 补充材料 Algorithm 1, line 10

**问题**: `for b = 1 to B (default 1,000)` — 与正文 B=500 矛盾（见 C4）。

### m10. P038 (Statistical reporting) 重复信息

**位置**: P038 (line 38)

**问题**: P038 与 P023 在 bootstrap P 值描述和 "无多重比较校正" 声明上存在大量重复。P023 已说明 "For human, TCGA, and brain analyses, standard statistical tests were applied without multiple-testing correction; all reported P-values are raw, uncorrected values"，P038 几乎逐字重复。

**修复建议**: 在 P023 (Bootstrap permutation test) 中保留方法描述，P038 (Statistical reporting) 中仅保留报告格式约定（mean ± s.d.、box plot 参数等），删除重复的统计策略声明。

---

## 优点（Strengths）

1. **概念创新性突出**: Ka/Ks 比类比的转录组化是一个优雅的跨学科构思。将 "中性基线" 概念从分子进化引入单细胞转录组比较，提供了现有距离度量无法捕获的信息维度。负相关性发现（ω 与4种标准度量均负相关，Spearman r = -0.57 到 -0.38）是 CKI 最有力的存在价值证据。

2. **验证规模宏大**: 4个独立数据集（Tabula Muris 15,057细胞、Tabula Sapiens 108,136细胞、TCGA 3,596样本、Siletti 脑图谱 888,263核），跨越人鼠两种模式生物，总计数百万个细胞。31,764对脑区比较和4,851对人细胞类型对比较构成扎实的工作量。

3. **OPCs 阴性对照设计精妙**: 作为脑内最活跃迁移的细胞，OPCs 在5,671对比较中产生0个 Strong 信号——这一"零结果"有力验证了倍增残差模型的特异性，是从"检测迁移"到"检测发育起源签名"的范式重定义的关键证据。

4. **局限性讨论诚实充分**: Discussion 包含6条系统性局限（pseudobulk层面、HK基因集选择、TCGA bulk RNA-seq混淆、脑区分析单一物种、候选信号未独立验证、bootstrap 功效不足），展现了科学诚实性。

5. **开源工具完整**: Python 包 (v0.3.1, MIT License) + GitHub URL + Zenodo DOI (10.5281/zenodo.15670808) + 完整分析脚本索引，满足 NAR 的数据/代码可用性高标准。

6. **摘要合规且精炼**: 170词非结构化单段，≤200词合规，逻辑链清晰（问题→灵感→方法→验证→结论），准确概括全文核心发现。

7. **参考文献质量高**: 引用了领域前沿文献（SATURN Nature Methods 2024、Foerster et al. Nature Neuroscience 2024、Schaffenrath et al. Nature Neuroscience 2024、Siletti et al. Science 2023），体现了对领域前沿的准确把握。HRT Atlas [4] 发表于 NAR，形成引用生态链。

8. **v11→v12 修复成效显著**: 3处中文标点全部修复，3处文本损坏（exhibitedthe/classifierCKI/limitedwarranting）修复，参考文献格式大幅改善（从 Vancouver 转为 NAR 框架），Track Changes 清零。

---

## 具体修改建议

### 必须在投稿前修复（P0 — 阻断项）

| 编号 | 问题 | 修复方案 | 预计工作量 |
|------|------|----------|-----------|
| C1 | JS 对数底正文/补充矛盾 | 确认代码实际对数底，统一正文和补充材料 | 30分钟 |
| C2 | 归一化方式正文/补充矛盾 | 确认代码实际归一化，统一 P021/P042/补充材料 | 1小时 |
| C3 | TCGA 样本数正文/补充矛盾 | 核实实际样本数，统一 P027 和补充 Note 4.3 | 30分钟 |
| C4 | Bootstrap B 值正文/补充矛盾 | 确认实际 B 值，统一正文和补充材料 | 30分钟 |
| C5 | P056 语法破碎+孤立片段 | 重写破碎句，删除孤立片段 | 15分钟 |
| C6 | `danalysis` 缺失空格 | 改为 `d analysis` | 1分钟 |
| M1 | Cover Letter 缺推荐审稿人 | 添加6位以上推荐审稿人 | 1小时 |
| M2 | Graphical Abstract 占位符 | 制作实际图片 | 数小时 |
| M5 | TPM vs. FPKM 矛盾 | 核实并统一 | 15分钟 |

### 强烈建议修复（P1）

| 编号 | 问题 | 修复方案 | 预计工作量 |
|------|------|----------|-----------|
| M3 | 参考文献格式细节 | 扩展作者列表、添加期刊缩写句点、修正联合体作者 | 2-3小时 |
| M4 | HK 基因数 1,130 vs 1,129 | 统一为 1,129 并加说明 | 15分钟 |
| M6 | P054 缺失空格 | 添加空格 | 1分钟 |
| M7 | P023 冗余重复 | 删除重复括号内容 | 1分钟 |
| M8 | Cell-state/Cell-type 不一致 | 统一命名 | 30分钟 |
| M9 | P054 AUC 论述重复 | 合并为一次论述 | 15分钟 |
| M10 | 候选信号总数 7,844 vs 7,842 | 核实并统一 | 15分钟 |

### 建议改进（P2）

| 编号 | 问题 | 修复方案 |
|------|------|----------|
| m1 | P044 双空格 | 删除多余空格 |
| m4 | Data/Code availability 分设 | 拆分为两个章节 |
| m5 | Cover Letter 跨物种声称缺支撑 | 删除或补充正文数据 |
| m6 | P021 HVG 参数描述混淆 | 明确区分200/2,000方案 |
| m10 | P038 与 P023 重复 | 精简 P038 |

---

## 期刊适配度评估

### NAR 适配度：7.0 / 10

**适配优势**:
- 概念定位与 NAR "Computational Biology" 类别高度匹配——CKI 是一个新颖的计算方法，有大规模验证
- HRT Atlas [4] 发表于 NAR (Hounkpe et al. 2021)，形成引用生态链和读者群重合
- TCGAbiolinks [14] 也发表于 NAR (Colaprico et al. 2016)，进一步强化期刊契合度
- 4个数据集+百万细胞的验证规模满足 NAR 对方法学文章的验证要求
- 开源 Python 包 + GitHub + Zenodo DOI 满足 NAR 的可复现性标准
- 摘要格式合规（170词，非结构化单段，≤200词）
- 章节顺序合规（Introduction → Materials and Methods → Results → Discussion）

**适配障碍**:
- Cover Letter 缺推荐审稿人（NAR 必要要素）
- Graphical Abstract 仅为占位符
- 正文与补充材料的方法学参数矛盾（审稿人会质疑方法描述的可靠性）
- 参考文献格式未完全合规（et al. 过早、期刊缩写缺句点）
- 仅有2位作者，NAR 方法学文章通常有更大合作团队
- 生物学发现多为已知现象的"再发现"（脑区30个 Strong 信号中29/30可被已知发育生物学解释），创新性集中在方法层面

**录用概率估计**: 25-35%（修复全部 P0 问题后可提升至 35-45%）

### 备选期刊推荐排序

| 排名 | 期刊 | IF | 匹配度 | 录用概率 | 理由 |
|------|------|-----|--------|----------|------|
| 1 | **NAR** | ~14.9 | 7.0/10 | 25-35% | 首选目标。方法+大规模验证+开源工具定位匹配。HRT Atlas 和 TCGAbiolinks 发表于 NAR，引用生态链强。修复 P0 问题后投稿。 |
| 2 | **Genome Biology** | ~12.3 | 7.5/10 | 25-35% | 最佳备选。单细胞方法学核心期刊，对"方法+发现"综合定位更包容。参考文献格式要求较 NAR 宽松。如果 NAR 审稿人认为"生物学发现深度不足"可转投。 |
| 3 | **Briefings in Bioinformatics** | ~9.5 | 7.5/10 | 40-50% | CACIMAR [33] 发表于此刊，形成引用匹配。方法学推导清晰，符合该刊对方法严谨性的要求。录用门槛略低于 NAR。 |
| 4 | **Cell Systems** | ~9.0 | 7.0/10 | 20-30% | "系统级转录组重塑量化"框架与 Cell Systems 理念契合。same-organ > different-organ 的 ω 反转是系统级发现。但偏好更强的数学建模。 |
| 5 | **Bioinformatics** | ~5.8 | 8.0/10 | 55-65% | 最安全的保底选项。纯计算方法学的理想归宿，录用概率最高。但 IF 5.8 对这样体量的工作偏低，"过度合格"风险存在。 |

### 投稿策略建议

```
第1轮 → NAR (IF 14.9) — 修复全部 P0 + P1 问题后投稿
  ↓ 被拒
第2轮 → Genome Biology (IF 12.3)
  ↓ 被拒
第3轮 → Briefings in Bioinformatics (IF 9.5)
  ↓ 被拒
第4轮 → Bioinformatics (IF 5.8)
```

**投稿前最低限度修复清单**（预计1-2天）:
1. 修复正文-补充材料的6处方法学参数矛盾（C1-C4, M4, M5）
2. 修复 P056 语法破碎和 P057 `danalysis`（C5, C6）
3. Cover Letter 添加6位以上推荐审稿人（M1）
4. 完成 Graphical Abstract 实际制作（M2）
5. 参考文献格式细节修正（M3）

完成上述修复后，NAR 录用概率可从 25-35% 提升至 35-45%。

---

*审稿日期: 2026-07-26*
*审稿人: 科学写作与期刊适配专家（AI辅助）*
*稿件版本: v12 (v12_manuscript_fulltext.txt, ~11,674词)*
