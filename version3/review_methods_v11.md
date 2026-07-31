# CKI 算法方法学审稿报告 (v11)

**审稿人**: methods-reviewer
**审稿版本**: v11 (NAR Manuscript)
**审稿日期**: 2026-07-26
**审阅文件**: v11_manuscript_fulltext.txt, CKI_NAR_Supplementary_fulltext.txt, CKI_NAR_Reproducibility_Guide_fulltext.txt
**对照版本**: v10 (含 review_methods.md, v10_comments.txt, v10_manuscript_fulltext.txt)

---

## 1. 综合评分: 5/10

v11 相比 v10 修复了若干数值错误（k_n 中位数 0.0086→0.0019、ω<15 占比 93.6%→56.3%、小鼠 ω 报告 mean 7.07→median 3.63），这些修正与用户手算结果一致，说明 k_n 统计量的数据来源问题已得到处理。

然而，v11 暴露出一个 v10 审稿未发现的**致命矛盾**：稿件正文声称对人体/TCGA/脑数据进行了 B=1000 的 bootstrap 置换检验并施加了 BH-FDR 校正，但补充材料和复现指南明确记载这些分析**既未执行 bootstrap、也未应用 FDR 校正**。这一矛盾直接动摇了稿件统计学声明的可信度，必须在投稿前解决。

此外，稿件正文与复现指南在 JS 散度对数底数（base-2 vs natural log）、概率分布转换方法（softmax vs sum-normalization auto-switching）上存在根本性矛盾，TCGA 数据样本量在正文与补充材料间完全不一致，这些 Critical 问题叠加使当前版本不具备投稿条件。

---

## 2. Critical 问题（阻断投稿）

### C1. Bootstrap 检验与 FDR 校正：正文与补充材料/复现指南的致命矛盾

**问题描述**：

稿件正文在三个独立位置明确声称对 human/TCGA/brain 主要分析执行了 B=1000 bootstrap 置换检验并施加了 BH-FDR 校正：

- P22 (Materials and Methods): "B = 1,000 for human, TCGA, and brain primary analyses"
- P22: "Benjamini-Hochberg false discovery rate (FDR) correction was applied; adjusted q-values are reported in Supplementary Tables S1-S2 alongside raw P-values"
- P37 (Statistical reporting): "Benjamini-Hochberg FDR correction was applied; adjusted q-values are reported in Supplementary Tables alongside raw P-values"
- P43 (Results): "Bootstrap inference uses B = 1,000 for primary analyses"

但补充材料和复现指南直接否定了这些声明：

- Supplementary Note 1.5: "Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses; all reported P-values are raw bootstrap P-values"
- Supplementary Note 3.3: "Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses. All reported significance judgments are based on raw bootstrap P-values (P < 0.05)"
- Reproducibility Guide Section 5.1: "B is not applicable to human/TCGA/brain analyses which do NOT use bootstrap"
- Reproducibility Guide Section 5.2: "FDR correction (Benjamini-Hochberg, q < 0.05) was intended for multi-pair comparisons but was not systematically implemented in the analysis pipeline. All reported results use raw two-sided bootstrap P-values without FDR adjustment"
- Reproducibility Guide Parameter Summary: "Bootstrap (human): N/A", "Bootstrap (TCGA): N/A", "Bootstrap (brain): N/A"

此外，稿件声称"adjusted q-values are reported in Supplementary Tables S1-S2"，但实际的 Supplementary Table 1 是"Parameter Sweep Results"，Supplementary Table 2 是"Cross-Organ Conservation Data"——两者均非 P 值/q 值表。稿件引用的 Supplementary Tables S1-S2 不存在。

**影响评估**：
- 稿件正文中所有涉及 human/TCGA/brain 的 bootstrap P 值声明（如 P52 "all P < 0.001"、P46 "all P > 0.05"）的来源存疑。部分 P 值可能来自标准统计检验（Spearman、Mann-Whitney U、Kruskal-Wallis），而非 bootstrap，但稿件未做区分。
- Abstract 中"all P > 0.05"和"all P < 0.001"的声明基础不明确。
- 这是一个**学术诚信问题**：稿件声称执行了实际未执行的统计检验。

**修改建议**：
1. 如果 human/TCGA/brain 分析确实未执行 bootstrap，必须从 M&M 和 Results 中删除所有关于 B=1000 bootstrap 的描述，仅保留 mouse calibration 的 B=500 bootstrap。
2. 明确每个 P 值的来源（标注是 Spearman/Mann-Whitney/Kruskal-Wallis/Jonckheere-Terpstra 的标准 P 值，还是 bootstrap P 值）。
3. 如果 FDR 未应用，删除所有关于 BH-FDR 校正和 q 值的声明。
4. 或者，如果确实需要 bootstrap 和 FDR，必须实际执行这些分析并更新结果——但不能在未执行的情况下声称已执行。

---

### C2. JS 散度对数底数与概率分布转换方法：正文与实现的根本矛盾

**问题描述**：

稿件正文（P20）明确且反复声明：
- "JS divergence uses base-2 logarithm (range [0,1])"
- "The JS divergence implementation uses base-2 logarithm (np.log2 in Python) with range [0, 1]"
- "Expression-to-probability conversion uses softmax normalization as the default mode (via ensure_probability_distribution with mode='softmax')"
- "These implementation details are consistent across all analyses reported in this study"

但复现指南（Section 2）描述的实际实现完全不同：
- JS 散度使用**自然对数**（natural log, ln）："KL(P || M) = sum_i [ P_i * ln(P_i / M_i) ]"，而非 base-2
- 概率分布转换使用 **auto 模式**（非 softmax）："In 'auto' mode (the default), the method is selected based on the data range"
  - 非负值（mouse/human/brain 的 CP10k+log1p 数据）：使用 **sum-normalization**（p_i = x_i / sum_j x_j），而非 softmax
  - 含负值（TCGA 的 log2 数据）：使用 softmax
- "Both methods produce valid probability distributions for JS divergence; the auto-switching behavior is an implementation detail"

**影响评估**：
1. **对数底数**：base-2 log 的 JS 散度范围为 [0,1]，natural log 的范围为 [0, ln2≈0.693]。虽然 ω=k_f/k_n 的比值不受对数底数影响（分子分母同底），但绝对 k_n、k_f 值的数值不同，影响稿中报告的所有绝对数值（如 k_n median 0.0019、k_f≈6.0 等）的可解释性。
2. **概率分布转换**：softmax 和 sum-normalization 产生**形状完全不同**的概率分布。softmax 指数化放大高表达基因权重，使分布更"尖锐"；sum-normalization 保持线性比例。这直接影响 JS 散度的数值和 ω 的计算结果。对 mouse/human/brain 数据（占稿件 3/4 的分析），实际使用的是 sum-normalization 而非 softmax。
3. 稿件声称"consistent across all analyses"，但实际上 TCGA 和其他三个数据集使用了不同的概率分布转换方法。

**修改建议**：
1. 统一正文与实现描述。如果实际使用 natural log + auto-switching，正文必须如实报告。
2. 在 Methods 中明确说明不同数据集使用不同的概率分布转换（sum-normalization vs softmax），并讨论这对结果可比性的影响。
3. 报告 base-2 和 natural log 的转换关系（JS_base2 = JS_ln / ln2），使读者可自行转换。

---

### C3. TCGA 数据：正文与补充材料样本量完全不一致；FPKM/TPM 混淆

**问题描述**：

**(a) 样本量矛盾**：

| 癌种 | 正文 P26 (v11) | 补充材料 Note 4.3 |
|------|----------------|-------------------|
| LUAD | 495 tumor + 76 normal | 515 tumor + 59 normal |
| LUSC | 567 tumor + 58 normal | 501 tumor + 51 normal |
| LIHC | 365 tumor + 57 normal | 371 tumor + 50 normal |
| KIRC | 755 tumor + 82 normal | 533 tumor + 72 normal |
| BRCA | 1032 tumor + 109 normal | 1093 tumor + 113 normal |
| **总计** | **3596** | **3358** |

两组数字完全不同，差异高达 238 个样本。正文 P55 也声称"totalling 3,596 samples"，复现指南也说"10,535 samples available; 3,596 after filtering"，但补充材料的分癌种明细加总为 3358。

**(b) FPKM vs TPM**：

正文 P26 声称"FPKM values, log2(x+1) transformed"。
但复现指南 Section 4.3 明确使用的是 **TPM**（RSEM gene TPM）："tcga_RSEM_gene_tpm.gz" 和 "log2(TPM + 0.001) transformation"。

FPKM 和 TPM 是不同的归一化方法；log2(x+1) 和 log2(TPM+0.001) 的偏移量也不同（+1 vs +0.001），对低表达基因的变换行为差异显著。

**(c) LIHC/LUAD 临床亚组计数不一致**：

- LIHC Edmondson: P26 说"289 tumors"，P33 说"n = 288"，P58 亚组加总 G1(39)+G2(133)+G3(105)+G4(11)=288
- LUAD mutations: P26 说"497 samples (61 EGFR, 121 KRAS, 312 WT)"，P33 说"n = 492"，P58 亚组加总 61+120+311=492

**修改建议**：
1. 核实实际使用的 TCGA 样本量，统一正文和补充材料。
2. 将"FPKM"更正为"TPM (RSEM)"，将"log2(x+1)"更正为"log2(TPM+0.001)"。
3. 统一 LIHC (289 vs 288) 和 LUAD (497 vs 492) 的计数。

---

### C4. Hybrid 方案比值不一致性（v10 遗留问题，v11 未修复）

**问题描述**（v10 review C1，v11 仍然存在）：

Tabula Sapiens 和 brain 分析采用 hybrid scheme：k_n 使用全局共享 HK 基因集（~1000+ 基因），k_f 使用逐对 top-200 DE 基因。P50 声称：

> "since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies."

这个论断存在两个问题：
1. **尺度不一致**：k_n 在 ~1000+ HK 基因上计算（大量低变异基因稀释，JS 值偏小）；k_f 在 200 个差异最大的基因上计算（系统性偏大）。ω = k_f/k_n 的分子分母处于不同数值尺度，导致 ω 系统性膨胀。
2. **跨配对不可比**：不同配对使用不同 DE 基因集计算 k_f，A-B 的 ω=20 和 C-D 的 ω=20 不代表同等程度的功能分化。

v10 review 还指出 pairwise_de 模式的循环性问题（先选差异最大基因，再测量它们有多不同），v11 未对此做任何讨论或修正。

**v11 的新变化**：P20 新增了敏感性分析声明——"varying the HVG count from 1,000 to 4,000 yielded ω correlations r > 0.97"。但这测试的是全局 HVG 数量，而非 hybrid 方案中 per-pair DE 基因选择的影响。实际分析使用的 top-200 DE genes 并未被敏感性分析覆盖。

**修改建议**（与 v10 review 一致）：
1. 明确声明 ω 在 hybrid 方案下仅具相对排序意义，不能跨配对比较绝对数值。
2. 提供全局 HVG（固定基因集）方案的对照结果。
3. 讨论 pairwise_de 的循环性，或采用留一法验证。

---

## 3. Major 问题（需要修改）

### M1. 细胞类型配对数：5,151 vs 4,851

正文在多处（P29, P37, P51, P52）声称 Tabula Sapiens 有"5,151 cell-type pairs"。但：
- Supplementary Note 4.4: "Full pairwise omega computed for all 4,851 cell-type pairs"
- Reproducibility Guide Section 4.2: "all 4,851 cell-type pairs"
- Table 1 (Table1-2_fulltext.txt): "99 cell types, 4,851 pairs"

99 个细胞类型的配对数 = 99×98/2 = 4,851，与补充材料一致。5,151 对应的是 102 个细胞类型（102×101/2=5,151），与正文声称的 99 个细胞类型矛盾。

**修改建议**：核实实际细胞类型数量和配对数，统一为 4,851（若 99 个细胞类型正确）或更新细胞类型数量。

### M2. k_n "global" 计算的歧义

P50 称"k_n was computed once globally (using the full gene-by-cell-type pseudobulk matrix with the shared HK gene set)"。这句话可被理解为：
- (a) 使用全局 HK 基因集为每对计算 k_n（k_n 随配对变化），或
- (b) 从全局矩阵计算单一 k_n 值（所有配对共享同一 k_n）

Supplementary Note 2 (Algorithm 2) 澄清："k_n uses the global HK set (same for all pairs); k_f uses pairwise top-N genes"——即解释 (a)，HK 基因集是全局的，但 k_n 仍逐对计算。

但正文措辞"k_n was computed once globally"强烈暗示解释 (b)。如果 k_n 是单一全局值，则 ω = k_f/k_n 仅是 k_f 的常数缩放，"neutral normalization"失去意义，且 ω 与标准度量的负相关仅反映 k_f 的正比关系。

P52 的关键发现"CKI ω was negatively correlated with all four standard metrics"只有在 k_n 逐对变化时才有意义（否则 ω ∝ k_f，与标准度量正相关）。因此正文必须明确：k_n 逐对计算，仅 HK 基因集是全局共享的。

**修改建议**：将"k_n was computed once globally"改为"k_n was computed for each pair using a globally shared HK gene set"，消除歧义。

### M3. 版本号和软件环境不一致

| 项目 | 正文 | 复现指南 |
|------|------|----------|
| CKI 包版本 | v0.3.2 (P97, P99) | v0.3.1 (Section 1.2) |
| Python 版本 | 3.12 (P35) | 3.13.12 (Section 1.1) |
| scanpy 版本 | >= 1.9.0 (P35) | 未列出（核心包中无 scanpy） |

**修改建议**：统一版本号。注意复现指南的核心包列表中**遗漏了 scanpy**，而 scanpy 是 CKI 的核心依赖。

### M4. HVG flavor 不一致

- P24 (Tabula Muris datasets): "flavor='seurat'"
- P20 (M&M): "Seurat v3 flavor (sc.pp.highly_variable_genes with flavor='seurat_v3')"
- Supplementary Note 4.4: "flavor='seurat' and n_top_genes=2,000" (Tabula Muris)

`flavor='seurat'`（Seurat v4）和 `flavor='seurat_v3'`（Seurat v3）是不同的 HVG 选择算法，产生不同的基因集。正文 M&M 声称全程使用 seurat_v3，但 Tabula Muris 实际使用的是 seurat。

**修改建议**：核实各数据集实际使用的 flavor，在 Methods 中如实报告。

### M5. 跨器官配对数：60 vs 59

- 正文 P60: "60 same-cell-type cross-organ comparisons"
- Supplementary Table 2: "59 same-cell-type cross-organ pairs"
- Reproducibility Guide Section 4.2: "59 same-cell-type cross-organ pairs"
- Table 2 (Table1-2_fulltext.txt): "n=59 same-cell-type cross-organ pairs"

**修改建议**：统一为 59。

### M6. M&M 描述的默认参数与实际使用不符

P20 (M&M) 描述 k_f 使用"top-2,000 highly variable genes (HVGs; Scanpy default, Seurat v3 flavor)"。但实际所有四个分析（mouse pilot, human, TCGA, brain）均使用 hybrid mode 的 **top-200 per-pair DE genes**（Reproducibility Guide Section 3.2, Supplementary Note 2 Algorithm 2）。top-2,000 HVG 仅在 mouse full pairwise analysis（03_full_matrix.py, Fig. 2 heatmap）中使用。

M&M 应描述实际使用的参数，而非默认未使用的参数。

**修改建议**：在 M&M 中明确说明主要分析使用 hybrid mode（top-200 per-pair DE genes），仅 mouse full pairwise heatmap 使用 top-2,000 HVG。

### M7. HK 基因"中性"假设验证不充分（v10 遗留）

v10 review M1 指出 HK 基因的"中性"假设缺乏正交验证。v11 新增了敏感性分析（250-1000 基因，CV<13%），但这仅验证了 ω 对基因集**大小**的稳健性，未验证 HK 基因作为"中性基线"的合理性。如果 HK 基因的低方差源于强功能约束（stabilizing selection）而非中性漂移，则 k_n 度量的是"约束下的低漂移"，ω 的解释需要调整。

**修改建议**：增加随机等大小基因集对照（非 HK 基因的 k_n），验证 HK 基因集的 k_n 是否显著更低。

### M8. 校准 ω=1.54 的系统性偏移未校正

v10 review M2 已指出。v11 仍报告 mean ω=1.54（偏离理论值 1.0 达 54%），且 TOST 等价检验未通过（n=6）。所有后续分析的绝对 ω 阈值（如 Strong candidate 的 ω<15）都包含这个 +54% 的系统性偏移。

**修改建议**：报告校准后的 normalized ω = ω_observed/1.54，或将阈值以校准值为基准表述。增加校准配对数（n=6 过小）。

---

## 4. Minor 问题（建议改进）

### m1. ω 上限未在正文中提及

Supplementary Note 1.1 提到"in practice omega is capped at 1,000"，但正文未提及。这是一个重要的实现细节，影响极端值的解读。

### m2. 迁移候选计数偏差

P74 称 30+1,247+6,567=7,844 个候选；Supplementary Table 4 称"7,842 pairs (24.7%)"。差 2 个，需核实。

### m3. k_n 数值表述误导

P20 称"In our datasets, k_n had a median of 0.0019"，但 0.0019 是小鼠校准值；人类 k_n 为 0.0147-0.0166（高约 10 倍）。将小鼠 k_n 作为"our datasets"的通用值表述具有误导性。

### m4. 文稿文字残损

多处段落存在文字粘连或截断：
- P53: "componen..." 截断（v10 review m4 已指出，v11 仍未修复）
- P55: "ω magnitudes, which are not directly comparable..." 语句断裂
- P61: "exhibitedthe strongest functional constraint" 缺空格
- P63: "per cell-type coverage. limitedwarranting cautious interpretation" 文字粘连
- P90: "not a classifierCKI answers a complementary question" 句子粘连（v10 review m4 已指出，v11 未修复）

### m5. 参考文献引用 [31] PAML 在正文中未出现

参考文献 [31] (Yang Z, PAML 4) 在参考文献列表中，但正文中未被引用（Discussion 提到 PAML 概念但未引用 [31]）。

### m6. 补充材料 Note 1.5 中 P 值公式为单侧

Supplementary Note 1.5 给出的 P 值公式为 P = (count(omega_null >= omega_obs) + 1)/(B + 1)（单侧），但正文 P22 描述的是双侧检验 P = (count(|ω_null - 1| >= |ω_obs - 1|) + 1) / (B + 1)。两者不一致，需统一。

### m7. 复现指南中 HRT Atlas 基因数不一致

- 正文 P19: "1,130 human-mouse shared HK genes"
- Supplementary Note 4.2: "1,129 genes from HRT Atlas v1.0"（1 个无人源同源基因被排除）
- Reproducibility Guide Section 3.1: "1,130 orthologous gene pairs"
- Reproducibility Guide Section 4.4: "1,129 unique human genes after set() deduplication; the 1,130-row file contains 1 duplicate"

需统一表述：1,130 行中含 1 个重复映射，实际 1,129 个唯一人类基因。

---

## 5. v10 问题修复评估

### 5.1 k_n 统计量来源问题

**v10 问题**：k_n 统计量错误地取自脑区数据集而非正确数据集。

**v11 修复情况**：

| 指标 | v10 值 | v11 值 | 用户手算 |
|------|--------|--------|----------|
| k_n median (mouse calibration) | 0.0086 | 0.0019 | 0.034 (Comment 0)* |
| k_n range | 0.0004–0.106 | 0.0006–0.0027 | 0.0018-0.221* |
| ω<15 占比 (all) | 93.6% | 56.3% | 56.3% (Comment 4) |
| Mouse ω | mean 7.07 | median 3.63 | median 3.63, mean 5.27 (Comment 18) |
| Human k_n range | 0.0147-0.0166 | 0.0147-0.0166 | — |

*Comment 0 的手算值（0.034）与 v10/v11 均不匹配，可能来自不同数据集或计算方式。

**评估**：
1. **已修复**：k_n median 从 0.0086 降至 0.0019，range 从 [0.0004, 0.106] 收窄至 [0.0006, 0.0027]。这一变化幅度（median 降低 ~4.5 倍，range 上限降低 ~40 倍）与数据来源更正一致——v10 的高 k_n 值可能来自脑区数据（脑区 HK 基因的群体间分歧更大），v11 改用正确的小鼠校准数据后 k_n 大幅降低且更稳定。
2. **已修复**：ω<15 占比从 93.6% 修正为 56.3%，与用户手算一致。v10 的 93.6% 实际上是 OPC 特异性比例（v11 P76 正确地将 93.6% 限定为"OPC comparisons"），v10 错误地将其报告为全体配对的比例。
3. **已修复**：Mouse ω 从 mean 7.07 改为 median 3.63，与用户手算的 median 一致。
4. **未变化**：Human k_n sensitivity range (0.0147-0.0166) 在 v10 和 v11 中完全相同，说明人体分析的 k_n 数值未改变。这可能意味着：(a) 人体分析一直使用正确的数据源，仅校准部分有误；或 (b) 修复仅涉及报告数值而非分析代码。
5. **无法完全验证**：由于无法访问 v10 和 v11 的实际分析代码，无法 100% 确认 k_n 的数据来源已从脑区改为正确数据集。但数值变化的方向和幅度与修复一致。

**结论**：k_n 统计量来源问题**很可能已修复**，但需作者确认修复的具体范围（仅校准数值 vs. 分析代码）。

### 5.2 v10 review 其他问题的修复状态

| v10 问题 | 修复状态 | 说明 |
|-----------|----------|------|
| C1 (hybrid 比值不一致) | **未修复** | v11 仍使用 hybrid scheme，且未增加全局 HVG 对照 |
| C2 (softmax 语义) | **恶化** | v11 正文仍称 softmax，但复现指南揭示实际使用 sum-normalization，矛盾更深 |
| C3 (k_n 阈值不一致) | **部分修复** | v11 正文中 k_n range 为 [0.0006, 0.0027]，复现指南称 kn=0→ω=∞（无阈值），但正文仍建议 k_n≥0.001 |
| C4 (Ka/Ks 过度使用) | **轻微改善** | v11 在 P15 更早引入限定性说明，但 Abstract/Fig 1 仍以类比为核心 |
| M1 (HK 中性验证) | **未修复** | 仅增加基因集大小敏感性，未增加正交验证 |
| M2 (校准偏移) | **未修复** | 仍报告 ω=1.54，未校准 |
| M3 (pairwise_de 循环性) | **未修复** | 未讨论 |
| M4 (bootstrap 基因集固定) | **新问题暴露** | 见 C1（bootstrap 实际未执行） |
| M5 (ω 阈值可解释性) | **未修复** | 阈值仍无生物学校准 |

---

## 6. 方法学亮点

### 6.1 Ka/Ks 类比的诚实定位
Discussion (P92) 对 Ka/Ks 类比的局限性做了出色的诚实讨论：明确指出 CKI 缺乏突变率 μ 的抵消机制、ω=1 无群体遗传学中性含义、HK 基因可能受稳定化选择。v11 相比 v10 在 P15 更早引入了限定性说明（"we use evolutionary terminology as heuristic metaphors"），减轻了过度包装风险。

### 6.2 OPC 阴性对照设计
OPCs 作为成人 CNS 中最活跃的迁移细胞，却在 5,671 个跨区域比较中产生 0 个 Strong 信号——这是一个优雅的阴性对照。关键在于这不是循环论证：残差模型使用 OPC 自身的高全局 ω (7.65) 作为基线，要求特定区域对的 ω 显著低于该基线才能触发信号。这验证了模型检测的是"偏离预期的低分歧"而非"绝对低迁移率"。

### 6.3 敏感性分析框架
v11 新增了两个敏感性分析：(1) HK 基因集大小 250-1000 基因的 ω 稳定性（CV<13% for 99.2% of pairs）；(2) HVG 数量 1000-4000 的 ω 相关性（r>0.97）。虽然这些分析未覆盖实际使用的 hybrid 方案参数（见 C4），但框架本身是好的实践。

### 6.4 乘法残差模型
expected_ω = μ_ct × μ_pair / μ_grand 的乘法模型类比于无交互项的双因素 ANOVA，用于检测细胞类型×区域对的异常低 ω。阈值通过经验分布的百分位数（1st/5th/25th）确定，虽然非正式零分布，但 P31 坦诚说明了这一局限并提供了 permutation-based 阈值的敏感性分析。

### 6.5 负相关发现的方法学意义
CKI ω 与所有四个标准距离度量的负相关（Spearman r = -0.57 to -0.38）是稿件最有力的发现。如果 ω 仅是标准度量的变换，应正相关；负相关意味着 CKI 捕捉了一个正交的信息维度——即"基线归一化后的功能分歧"。特别是"same-organ > different-organ"的反转模式（所有标准度量显示相反方向），提供了 CKI 独特性的有力证据。

---

## 7. 总结与建议

### 当前状态
v11 修复了 v10 的部分数值错误（k_n 来源、ω<15 占比、mouse ω 报告），但暴露出更深层的矛盾：正文声称的统计检验（bootstrap + FDR）在补充材料和复现指南中被明确否定。这一问题在 v10 中已存在但未被 v10 审稿发现（因 v10 审稿缺乏补充材料和复现指南）。

### 投稿建议
**当前版本不建议投稿**。以下问题必须优先解决：

1. **C1（最高优先级）**：核实并如实报告 bootstrap 和 FDR 的执行情况。如果未执行，删除所有相关声明；如需执行，实际运行分析。
2. **C2**：统一 JS 散度对数底数和概率分布转换方法的描述。
3. **C3**：统一 TCGA 样本量和归一化方法描述。
4. **C4**：讨论 hybrid 方案的尺度不一致性，或提供全局 HVG 对照。
5. **M1-M6**：统一所有数值不一致。

### 修订后预期
如果上述 Critical 问题得到妥善解决，CKI 的概念框架（将转录组差异分解为基线和功能分量）仍有发表价值。Ka/Ks 类比虽有局限但作者已诚实讨论。负相关发现和 OPC 阴性对照提供了有力的方法学验证。建议大修后重新评审。
