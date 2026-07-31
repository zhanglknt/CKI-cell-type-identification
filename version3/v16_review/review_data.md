# CKI v16 数据与可复现性审稿报告

**审稿人**: 数据与可复现性专家
**审稿日期**: 2026-07-27
**版本**: v16

## 评分
- 数据与可复现性评分: 7.2/10 (v14: 7.0)
- 投稿准备度（数据维度）: 68%
- Critical: 5 | Major: 15 | Minor: 11

---

## v14→v16 改进确认

### 已修复的 v14 Critical Issues

| v14编号 | 问题 | v16状态 | 说明 |
|---------|------|---------|------|
| C3(数据) | TCGA样本数矛盾 | ✅ 已修复 | 3,596 在三份文档中一致 |
| C4(数据) | Bootstrap B值矛盾 | ⚠️ 部分修复 | 手稿+补充材料一致(B=500 mouse only)，但可复现性指南仍有矛盾(见M4) |
| C5(数据) | P020 softmax文本重复 | ✅ 已修复 | softmax公式在手稿中仅出现一次 |

### 已修复的 v14 Major Issues

| v14编号 | 问题 | v16状态 |
|---------|------|---------|
| — | TCGA log2 transformation | ✅ 已修复：三份文档统一为 log2(TPM + 0.001) |
| — | 软件版本 | ✅ 部分修复：Python 3.13.12 一致，但 scanpy/seaborn 版本在可复现性指南中缺失(见M9) |
| — | CKI缩写 Kinetic/Comparative | ✅ 已修复：全文统一为 "Cell-state Kinetic Index" |
| — | HK基因数 1130/1129 | ✅ 已修复：全文统一为 1,130 |
| — | 脑区机制数量 4/3/3 | ✅ 已修复：Methods/Results/Discussion 均为 4 种 |
| — | Bootstrap scope | ✅ 已修复(手稿+补充材料)：明确 B=500 仅用于 mouse pilot |

### v14 未解决的 Major Issues

| v14编号 | 问题 | v16状态 |
|---------|------|---------|
| M2(数据) | 数据版本号/访问日期缺失 | ❌ 未修复 |
| M6(数据) | QC标准不一致 | ❌ 未修复，且新增矛盾(见M7) |

---

## 跨文档一致性检查

以下表格列出所有发现的不一致参数。**"—"** 表示该文档未提及该参数。

| 参数 | 手稿 | 补充材料 | 可复现性指南 | 状态 |
|------|------|---------|------------|------|
| Tabula Sapiens 细胞类型数 | 99 | 99 | **102** | ❌ 不一致 |
| 跨器官同细胞类型对数 | 59 | 59 (Sup Table S2) | **60** | ❌ 不一致 |
| 脑区数量 | 108 | 108 | **~100** | ❌ 不一致 |
| HK基因选择方法 | 自动检测(+可选HRT) | 自动检测(+可选HRT) | **预指定HRT(非自动检测)** | ❌ 严重矛盾 |
| Tabula Muris k_f 基因 | Top-2,000 HVG | Top-2,000 HVG | **Top-200 DE genes** | ❌ 严重矛盾 |
| 脑图谱归一化流程 | Scanpy normalize→log1p→取均值 | — | **取原始计数均值→normalize→log1p→softmax** | ❌ 严重矛盾 |
| Bootstrap P值公式 | 双侧 2×min(count+1/(B+1)) | 双侧 2×min(count+1/(B+1)) | **单侧 count(\|ω-1\|≥\|ω_obs-1\|)+1/(B+1)** | ❌ 严重矛盾 |
| Bootstrap B值(非mouse) | 未执行 | 未执行 | **1000(隐含)** | ❌ 矛盾 |
| LIHC Edmondson 分级n | G1=39,G2=133,G3=105,G4=11 (总288) | — | **G1=12,G2=118,G3=127,G4=32 (总289)** | ❌ 严重矛盾 |
| BRCA PAM50 分型n | LumA=224,LumB=123,HER2=55,Basal=97,NL=7 (总506) | — | **Basal=181,HER2=78,LumA=562,LumB=207,NL=36 (总1064)** | ❌ 严重矛盾 |
| LUAD 突变n | EGFR=61,KRAS=120,WT=311 (总492) | — | **EGFR=97,KRAS=152,WT=283 (总532)** | ❌ 严重矛盾 |
| TS QC基因阈值 | — | < 200 genes | **< 500 genes** | ❌ 不一致 |
| 脑区过滤条件 | ≥20/组 AND ≥50/region | — | **仅 ≥20/组** | ❌ 不一致 |
| HVG flavor | seurat | seurat | seurat (但checklist写 **"Seurat v3"**) | ❌ 不一致 |
| 迁移候选总数 | 30+1247+6567=7844(隐含) | **7842** | — | ❌ 算术不一致 |
| scanpy版本 | >= 1.9.0 | — | **未列出** | ❌ 缺失 |
| seaborn版本 | >= 0.12.0 | — | **未列出** | ❌ 缺失 |
| python-docx | 未列出 | — | 1.2.0 | ⚠️ 多余依赖 |
| TCGA基因过滤 | — | — | mean > 1 TPM (per-cancer) | ⚠️ 仅指南提及 |
| TCGA配对上限 | — | — | Max 2,000 random TT/TN pairs | ⚠️ 仅指南提及 |
| ω上限 | — | 1,000 | — | ⚠️ 仅补充材料提及 |
| epsilon | — | — | 1e-9 | ⚠️ 仅指南提及 |

---

## Critical Issues

### C1. HK基因选择方法根本性矛盾

**位置**: 手稿 line 19, 27, 46; 补充材料 line 20; 可复现性指南 line 48-76

手稿明确描述HK基因为"自动检测"（auto-detected）：
> "Housekeeping (HK) genes are auto-detected from data using a combined criterion: detection rate > 0.9 and coefficient of variation below the 30th percentile" (line 19)
> "HK genes were auto-detected per dataset (combined detection-rate/CV criterion)" (line 27, 脑图谱部分)

补充材料同样描述为自动检测：
> "CKI employs data-driven automatic detection of HK genes (joint criteria: detection rate > 0.9 and CV < 30th percentile)" (line 20)

但可复现性指南明确声明**未使用自动检测**：
> "housekeeping (HK) genes were NOT auto-detected. Instead, pre-specified HK gene lists were loaded from the HRT Atlas reference file" (line 48-50)
> "This auto-detection was NOT used in the current analyses (the pre-specified list approach was preferred for reproducibility)" (line 74-76)

**影响**: 这是方法描述的根本性矛盾。独立研究者无法确定实际使用了哪种HK基因选择方法，而HK基因集直接影响k_n计算和最终ω值。两种方法可能产生不同的结果。

**建议**: 必须核实实际代码使用的方法，统一三份文档的描述。如果确实使用了预指定HRT Atlas列表（如可复现性指南所述），则手稿和补充材料的"auto-detected"描述需要全部修改。

### C2. TCGA临床分层样本数完全不一致

**位置**: 手稿 line 26, 60; 可复现性指南 line 126-128

三个癌症类型的临床分层样本数在手稿和可复现性指南之间完全不同：

| 分层 | 手稿 | 可复现性指南 | 差异 |
|------|------|------------|------|
| LIHC G1 | n=39 | n=12 | -27 |
| LIHC G2 | n=133 | n=118 | -15 |
| LIHC G3 | n=105 | n=127 | +22 |
| LIHC G4 | n=11 | n=32 | +21 |
| LIHC 总计 | 288 | **289** | +1 |
| BRCA LumA | n=224 | n=562 | +338 |
| BRCA LumB | n=123 | n=207 | +84 |
| BRCA HER2 | n=55 | n=78 | +23 |
| BRCA Basal | n=97 | n=181 | +84 |
| BRCA Normal | n=7 | n=36 | +29 |
| BRCA 总计 | 506 | **1064** | +558 |
| LUAD EGFR | n=61 | n=97 | +36 |
| LUAD KRAS | n=120 | n=152 | +32 |
| LUAD WT | n=311 | n=283 | -28 |
| LUAD 总计 | 492 | **532** | +40 |

**影响**: BRCA PAM50分型的样本数差异超过2倍（506 vs 1064），这意味着至少有一份文档使用了完全不同的数据集或过滤标准。这直接影响所有临床严重度分析结果的可靠性。v14曾指出LIHC 289→288的矛盾，v16手稿已改为288，但可复现性指南仍为289，且新增了BRCA和LUAD的严重不一致。

**建议**: 必须核实实际分析使用的样本数，统一所有文档。考虑到v14 P0修复清单已要求修正LIHC和LUAD数字，可复现性指南显然未被同步更新。

### C3. Bootstrap P值公式三方不一致

**位置**: 手稿 line 22, 37; 补充材料 line 26, 47; 可复现性指南 line 161

手稿和补充材料使用相同的双侧公式：
> P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)), capped at 1.0

但可复现性指南使用完全不同的公式：
> p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)

这是**单侧**公式，基于ω与1的距离，且无2×系数。两种公式在统计学上有本质区别：
- 手稿公式：分别计算ω_null ≥ ω_obs 和 ω_null ≤ ω_obs 的比例，取较小值乘2
- 指南公式：计算|ω_null - 1| ≥ |ω_obs - 1|的比例，不区分方向

**影响**: 这是v14的Critical Issue C2的延续。虽然手稿和补充材料已统一，但可复现性指南仍使用不同公式。由于可复现性指南是独立研究者复现分析的依据，公式不一致将导致不同的P值和显著性判断。

**建议**: 统一所有文档使用相同的P值公式。必须核实代码中实际使用的公式。

### C4. 脑图谱预处理流程根本性矛盾

**位置**: 手稿 line 27; 可复现性指南 line 138

手稿描述的预处理流程：
> "Normalization: Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation. Pseudobulk vectors were computed as the mean log-normalized expression per group."

即：**细胞级归一化 → log1p → 取均值（标准pseudobulk流程）**

可复现性指南描述的流程：
> "Build pseudobulk vectors: raw count means per (ct, region) group. Normalize each pseudobulk: softmax(log1p(pb / sum(pb) * 1e4 + 1e-9))."

即：**取原始计数均值 → pseudobulk级归一化 → log1p → softmax**

**影响**: 这两个流程在数学上不等价。log(mean(x)) ≠ mean(log(x))，且可复现性指南在pseudobulk级别额外应用了softmax和epsilon=1e-9，手稿中未提及此步骤。这将产生不同的k_n、k_f和ω值，直接影响所有31,764个脑区比较结果以及30个Strong迁移候选信号。

**建议**: 必须核实实际代码流程。如果可复现性指南描述的是实际流程，则手稿的方法描述需要完全重写。

### C5. Tabula Muris k_f基因选择矛盾

**位置**: 手稿 line 20, 46; 补充材料 line 77; 可复现性指南 line 95

手稿明确指出Tabula Muris使用top-2,000 HVG作为identity genes：
> "I is the set of top-2,000 highly variable genes (HVGs; Seurat flavor) excluding HK genes" (line 20)
> "Identity genes were the top-2,000 highly variable genes (HVGs; Seurat), excluding HK genes" (line 46, Tabula Muris校准部分)

补充材料同样确认：
> "Tabula Muris: Global HVG selection was performed using scanpy.pp.highly_variable_genes, with parameters flavor='seurat' and n_top_genes=2,000" (line 77)

但可复现性指南在Tabula Muris部分写道：
> "Compute per-pair k_f with top-200 DE genes." (line 95)

**影响**: top-2,000 HVG（全局选择）与top-200 DE genes（配对选择）是根本不同的策略。前者使用所有细胞类型间的高变异基因，后者为每对细胞类型单独选择差异表达基因。这将影响所有Tabula Muris的ω值和校准结果，包括mean ω=1.54的基线值。

此外，可复现性指南line 81声明"hybrid mode is used for Tabula Sapiens and TCGA analyses"（不含Tabula Muris），但line 95又对Tabula Muris使用top-200 DE genes（即hybrid mode），存在自相矛盾。

**建议**: 核实Tabula Muris实际使用的k_f基因选择策略，统一所有文档。

---

## Major Issues

### M1. Tabula Sapiens细胞类型数不一致

**位置**: 手稿 line 25; 补充材料 line 73; 可复现性指南 line 103

手稿和补充材料均记载99个细胞类型条目，但可复现性指南记载102个。差异为3个条目，可能源于过滤标准不同，但未作任何解释。

### M2. 跨器官同细胞类型对数不一致

**位置**: 手稿 line 62, 64; 补充材料 line 83 (Sup Table S2); 可复现性指南 line 141

手稿和补充材料均记载59对，可复现性指南记载60对。

### M3. 脑区数量不一致

**位置**: 手稿 line 27, 69; 补充材料 line 86; 可复现性指南 line 133

手稿和补充材料明确记载108个脑区，可复现性指南使用近似值"~100"。在精确的复现性指南中不应使用近似值描述可精确计数的数据集属性。

### M4. Bootstrap B值在可复现性指南中的矛盾

**位置**: 可复现性指南 line 155, 199; 补充材料 line 42

可复现性指南有两处矛盾：
1. Line 199 (Reproducibility Checklist): "Verify bootstrap iterations: 500 (mouse) or 1000 (human/TCGA/brain)" — 这暗示human/TCGA/brain也执行了B=1000的bootstrap，直接与手稿line 22矛盾（"Bootstrap permutation testing was performed only for the mouse pilot study"）。
2. Line 155: "For each of B iterations (B = 500 or 1000)" — 同样暗示两个B值均被使用。
3. 补充材料Algorithm 1 (line 42): "for b = 1 to B (default 1,000)" — 伪代码默认值B=1,000与实际使用的B=500不一致，虽非错误（默认值≠实际使用值），但易引起混淆。

### M5. Bergmann glia Strong信号计数矛盾

**位置**: 手稿 line 75, 83

Line 75: "30 (0.09%) were classified as Strong migration candidates: Astrocyte (6), fibroblast (1), microglia (10), oligodendrocyte (10), and vascular cells (3)." — 总计30，Bergmann glia未列入。

Line 83: "Bergmann glia had the lowest global ω (2.37) and only one Strong signal (CBL vs. CBV, residual = 0.274)" — 声称Bergmann glia有1个Strong信号。

如果Bergmann glia确有1个Strong信号，总数应为31而非30。或者Bergmann glia信号因不满足全部Strong标准（如"pair median ω > 20"）而未被计入30，但手稿明确称之为"Strong signal"，造成逻辑矛盾。

### M6. 迁移候选总数算术不一致

**位置**: 补充材料 line 89

补充材料记载："7,842 pairs (24.7%) were classified as migration candidates"
但 30 (Strong) + 1,247 (Moderate) + 6,567 (Weak) = **7,844**，非7,842。

差异为2对。v14已指出7844/7842的矛盾，v16仍未修复。

### M7. Tabula Sapiens QC基因阈值不一致

**位置**: 补充材料 line 73; 可复现性指南 line 107

补充材料：cells with < 200 detected genes were removed
可复现性指南：filter cells with < 500 genes

阈值差异为300 genes，将影响最终保留的细胞数量和后续分析。

### M8. 脑区过滤条件不一致

**位置**: 手稿 line 27; 可复现性指南 line 137

手稿记载两个过滤条件："≥20 nuclei per (region, cell_type) group AND ≥50 nuclei per region"
可复现性指南仅记载一个："Filter groups with < 20 nuclei"

缺失的≥50 nuclei per region过滤条件将影响保留的脑区数量和比较对数。

### M9. scanpy和seaborn版本在可复现性指南中缺失

**位置**: 可复现性指南 line 9-16

可复现性指南的"verified environment"列出了numpy、scipy、pandas、matplotlib、scikit-learn和python-docx的精确版本，但**遗漏了scanpy和seaborn**。scanpy是核心依赖（用于normalize_total、highly_variable_genes等关键步骤），其版本直接影响HVG选择结果。手稿仅指定"scanpy >= 1.9.0"，但不同scanpy版本的HVG选择算法可能不同。

此外，python-docx（1.2.0）出现在可复现性指南中但不在手稿的依赖列表中，属于多余依赖。

### M10. HVG flavor不一致

**位置**: 手稿 line 24; 补充材料 line 77; 可复现性指南 line 79, 198

手稿和补充材料均使用"seurat" flavor，但可复现性指南checklist (line 198)写为"Seurat v3"。在Scanpy中，"seurat"和"seurat_v3"是不同的HVG选择算法，可能产生不同的基因集。

### M11. Supplementary Figure S3与正文分析不匹配

**位置**: 手稿 line 121

Supplementary Figure S3图注："Pairwise ω matrices for six cancer types (BRCA, KIRC, LIHC, LUAD, COAD, HNSC)"

但正文仅分析了5种癌症（LUAD, LUSC, LIHC, KIRC, BRCA）。S3提到了COAD和HNSC（未分析），却遗漏了LUSC（已分析）。这表明S3可能使用了旧版分析结果，或图注有误。

### M12. 数据版本号和访问日期全面缺失

**位置**: 手稿 line 100 (Data availability)

所有四个数据集（Tabula Muris、Tabula Sapiens、TCGA、Siletti脑图谱）均未提供：
- 数据版本号或release版本
- 访问/下载日期
- 具体的collection ID（脑图谱仅写"collection ID as referenced in (9)"）

CZ CELLxGENE Discover平台的数据会定期更新，不指定版本号将影响可复现性。这是v14 Major Issue M2(数据)的延续。

### M13. TCGA基因过滤和配对上限仅在可复现性指南中提及

**位置**: 可复现性指南 line 118, 121

可复现性指南记载了两项预处理步骤，均未出现在手稿或补充材料中：
1. "Filter: gene-level mean expression > 1 TPM within each cancer type" (line 118)
2. "Maximum 2,000 random TT and TN pairs each" (line 121)

基因过滤阈值和配对数上限直接影响ω分布和统计结果，应在手稿Methods中报告。

### M14. 可复现性指南Parameter Summary部分为空

**位置**: 可复现性指南 line 167-168

Section 6 "Parameter Summary"标题后写着"All parameters used in the reported analyses:"，但**下方无任何参数内容**。这是一个完整的空section，对于可复现性指南而言是重大缺失。虽然参数散布在前面的各节中，但Parameter Summary的本意是提供一站式参考。

### M15. Figure 5图注与可复现性指南描述不匹配

**位置**: 手稿 line 116; 可复现性指南 line 141

Figure 5图注 (line 116)："(a) CKI ω ranking of 38 shared cell types between human and mouse" — 描述的是**跨物种**比较
可复现性指南 (line 141)："Cross-organ conservation (Fig. 5): Subset of 60 same-cell-type cross-organ pairs from Tabula Sapiens data" — 描述的是**人类跨器官**比较

两者指的是不同的分析（跨物种 vs 跨器官），但都指向Figure 5。此外，可复现性指南说60对，手稿Table 2说59对。

---

## Minor Issues

### m1. Microglia和OPC比较对数完全相同

手稿 line 68 记载microglia "n = 5,671 pairs"，line 77 记载OPCs "5,671 comparisons"。两个不同细胞类型有完全相同的比较对数，虽有可能（取决于各自覆盖的脑区数），但建议核实是否为copy-paste错误。

### m2. 脑图谱committed OPCs分类模糊

手稿 Datasets部分 (line 27)： "oligodendrocyte precursors (110,454 total including committed)" — 暗示committed OPCs是OPCs的子集
手稿 Results部分 (line 68)：committed OPCs作为独立的10类之一列出，有独立的1,326对比较

这造成混淆：committed OPCs的nuclei数是否包含在110,454内？如果是，10类的总nuclei数如何计算？

### m3. ω上限(1,000)仅在补充材料中提及

补充材料 line 18, 39 提到"omega is capped at 1,000"，但手稿和可复现性指南均未提及。此上限可能影响极值结果，应在手稿Methods中报告。

### m4. epsilon=1e-9仅在可复现性指南中提及

可复现性指南 line 138, 202 提到"epsilon = 1e-9 in omega computation"，但手稿和补充材料均未提及。此参数影响softmax归一化的数值稳定性，应在Methods中报告。

### m5. MSigDB Hallmark gene sets在Data Availability中列出但未实际使用

手稿 line 100 列出"MSigDB Hallmark gene sets: from Liberzon et al. (34)"，但最终分析选择了identity-only配置（w_pathway=0.0），MSigDB未被使用。建议从Data Availability中移除或在文中说明"considered but not used"。

### m6. Algorithm 1伪代码默认B=1,000

补充材料 line 42 伪代码写"default 1,000"，但实际分析使用B=500。虽非错误（默认值≠实际值），但建议将伪代码默认值改为500以与实际一致，或添加注释说明。

### m7. Tabula Sapiens基因数在可复现性指南中缺失

手稿和补充材料记载51,852 genes (filtered from 58,870)，可复现性指南未提及基因数。

### m8. 脑图谱基因数在可复现性指南中缺失

手稿和补充材料记载59,480 genes，可复现性指南未提及基因数。

### m9. AUC 95%置信区间缺失

Table 1 报告了5种指标的分类AUC，但未提供95% CI。v12曾有CI，v14移除，v16未恢复。虽不影响结论（AUC差异较大），但提供CI是最佳实践。

### m10. 脑图谱supercluster_term注释在可复现性指南中缺失

手稿 line 27 提到"Cell types were classified by supercluster_term annotation"，可复现性指南未提及此注释字段，仅说"Group by (cell_type, brain_region)"。

### m11. TCGA paired sample数量在手稿与可复现性指南间描述不对齐

手稿 line 59 提到"n = 2–5 per cancer type"的配对样本限制，可复现性指南 line 121 提到"Maximum 2,000 random TT and TN pairs each"。两者描述的是不同概念（配对patient样本 vs 随机配对），但可复现性指南未提及配对patient样本的数量限制。

---

## 优点

1. **可复现性指南的创建本身是重大进步**：v14的可复现性指南"完全未同步"，v16提供了一份结构化的指南，包含软件环境、数据源、处理流程、输出文件列表和复现检查清单，这是朝着可复现性迈出的重要一步。

2. **TCGA log2转换已修正**：三份文档统一为 log2(TPM + 0.001)，解决了v14的Critical Issue。

3. **核心软件版本已更新**：Python 3.13.12 和 CKI v0.3.1 在手稿和可复现性指南间一致。

4. **代码与数据可用性声明完整**：提供了GitHub URL（含tag v0.3.1）、Zenodo DOI (10.5281/zenodo.15670808)、MIT License，满足NAR的基本要求。

5. **分析脚本索引清晰**：补充材料Supplementary Data 1列出了所有关键脚本的路径和用途，可复现性指南列出了所有输出文件路径。

6. **Bootstrap scope在手稿和补充材料中明确**：明确声明B=500仅用于mouse pilot (15 cell-type pairs + 6 calibration controls)，其他数据集使用描述性统计。

7. **随机种子固定**：全部文档一致使用seed=42。

8. **GEO accession号提供**：Tabula Muris的GSE109774已在手稿和补充材料中明确标注。

9. **术语统一性改善**：CKI缩写（Kinetic）、HK基因数（1,130）、机制数量（4种）等在v14中不一致的术语已在v16中统一。

10. **QC标准在补充材料中有专节**：Supplementary Note 4详细列出了各数据集的QC标准（尽管与可复现性指南存在矛盾，但有记载本身是好的）。

---

## 总体评价

v16在数据与可复现性方面相比v14有**适度改善**（7.0→7.2），主要体现在三个方面：(1) 可复现性指南从"完全未同步"变为有结构化的指南文档；(2) TCGA log2转换、软件版本、CKI缩写等v14 Critical问题已修复；(3) 手稿与补充材料之间的一致性显著提升，v14中手稿/补充材料层面的6个核心参数矛盾基本解决。

然而，v16引入了一个**新的系统性问题**：可复现性指南与手稿/补充材料之间存在大量矛盾。在5个Critical Issues中，有4个（C1-C4）是可复现性指南与手稿的直接矛盾。这意味着虽然手稿和补充材料之间更一致了，但新加入的可复现性指南却描述了不同的方法、参数和数据。最严重的是：HK基因选择方法（自动检测 vs 预指定）、脑图谱预处理流程（normalize→mean vs mean→normalize）、Bootstrap P值公式（双侧 vs 单侧）和TCGA临床分层样本数（差异超过2倍）——这些矛盾使得独立研究者无法确定应遵循哪份文档来复现分析。

此外，可复现性指南本身存在内部矛盾（如line 81声明hybrid mode仅用于TS和TCGA，但line 95对Tabula Muris也使用top-200 DE genes）和空section（Parameter Summary完全为空）。数据版本号和访问日期的全面缺失（v14 Major Issue的延续）仍然是可复现性的隐患，尤其是对于CZ CELLxGENE等动态更新平台。

**建议优先修复顺序**：C1-C5（方法描述统一）→ M12（数据版本号）→ M14（Parameter Summary填充）→ M7-M8（QC标准统一）→ 其余Major Issues。在所有Critical Issues修复前，不宜投稿。可复现性指南必须与手稿逐项核对，确保每一项参数、方法和样本数完全一致——可复现性指南与手稿的矛盾比手稿内部的不一致更严重，因为它直接破坏了复现承诺。
