# 数据完整性审稿报告 - v11

**审稿人**: data-reviewer
**稿件版本**: v11 (CKI_NAR_Submission_v11)
**审稿日期**: 2026-07-26
**数据完整性评分**: 6/10

---

## 一、评分说明

v11修复了v10的6个Critical错误中的大部分（k_n来源、48对k_n<0.001、93.6%比例、mouse mean ω、Fig5 legend乱码、百分比矛盾），但引入了4个新的Critical问题：稿件与Reproducibility Guide/Supplementary在JS对数底、FDR校正、Bootstrap范围、TCGA normalization方法上存在严重不一致。此外，Cover Letter声称的"mouse orthologs correlation"在稿件中无支持，7个v10 Moderate问题未修复，P61/P63存在文本编辑错误。总体较v10有改善，但可复现性可信度仍受影响。

---

## 二、v10错误修复验证表

| # | v10 Critical问题 | v11状态 | 验证详情 |
|---|-----------------|---------|---------|
| 1 | k_n统计量取自脑区数据（median=0.0086, range=0.0004-0.106） | **部分修复** | v11 P19改为"k_n had a median of 0.0019 (range 0.0006-0.0027)"，此值来自mouse C_control的6个数据点（CSV验证：median=0.001869, range=0.000614-0.002653），不再误用brain数据。但P19的语境"In our datasets"有误导性——此值仅来自mouse的6个control comparisons，不代表所有数据集。Human数据k_n median=0.0341，Brain=0.0086。P45明确标注"control comparisons"更准确。 |
| 2 | 48对k_n<0.001（应为0对） | **已修复** | v11中不再提到"48 pairs"或k_n<0.001的具体数量。Human数据确认：0/5151 pairs k_n<0.001。 |
| 3 | ω<15比例93.6%（应为56.3%） | **已修复** | v11 P20改为"In practice, 56.3% of all ω values were < 15"。CSV验证：2901/5151=56.32%。93.6%在v11中仅出现在P76（brain OPC数据，5310/5671=93.6%），语境正确。 |
| 4 | mouse mean ω=7.07（应为5.27） | **已修复** | v11 P51改为"mouse (median ω = 3.63)"。CSV验证：mouse pilot median=3.6309, mean=5.2665。7.07已不在v11中出现。 |
| 5 | Fig5 legend乱码 | **已修复** | v11 P115只有一个清晰的Figure 5 legend，旧版乱码legend已删除。 |
| 6 | P19/P45百分比矛盾（0.93% vs 0.15%） | **已修复** | v11中"0.93%"和"0.15%"均已删除，不再存在百分比矛盾。 |

**修复总结**: 6个Critical错误中，5个已完全修复，1个部分修复（k_n值不再误用brain数据，但P19语境仍有误导性）。

---

## 三、Critical问题（新发现）

### C1. JS divergence对数底不一致

| 文件 | 描述 | 对数底 |
|------|------|--------|
| 稿件 P20 | "JS divergence uses base-2 logarithm (range [0,1])" | base-2 |
| Supplementary Note 1.1 | "base-2 logarithms...bounded in [0, 1]" | base-2 |
| Reproducibility Guide Sec 2 | "JS(P‖Q) is the Jensen-Shannon divergence (natural log)...KL(P‖M) = Σ P_i * ln(P_i/M_i)" | natural log (ln) |

**影响**: 若使用自然对数，JS divergence值范围为[0, ln2≈0.693]而非[0,1]，直接影响所有k_n、k_f和ω值的数值。这是方法论的核心定义，必须统一。

### C2. FDR校正声明不一致

| 文件 | 描述 |
|------|------|
| 稿件 P22 | "Benjamini-Hochberg false discovery rate (FDR) correction was applied" |
| 稿件 P37 | "Benjamini-Hochberg FDR correction was applied; adjusted q-values are reported" |
| Supplementary Note 1.5 | "Benjamini-Hochberg FDR correction is NOT systematically applied in the current analyses" |
| Supplementary Note 3.3 | "Benjamini-Hochberg FDR correction is NOT systematically applied" |
| Reproducibility Guide Sec 5.2 | "FDR correction...was not systematically implemented in the analysis pipeline. All reported results use raw two-sided bootstrap P-values without FDR adjustment" |

**影响**: 稿件多次声称做了FDR校正并报告q-values，但Supplementary和Reproducibility Guide明确承认未实施。这构成方法论声明与实际分析的不一致。

### C3. Bootstrap范围不一致

| 文件 | 描述 |
|------|------|
| 稿件 P22 | "B = 500 for mouse calibration and exploratory analyses; B = 1,000 for human, TCGA, and brain primary analyses" |
| 稿件 P43 | "Bootstrap inference uses B = 1,000 for primary analyses" |
| Supplementary Note 3.2 | "B=1,000 for all primary results" |
| Reproducibility Guide Sec 5.1 | "B is not applicable to human/TCGA/brain analyses which do NOT use bootstrap" |
| Reproducibility Guide Sec 6 | "Bootstrap (human): N/A; Bootstrap (TCGA): N/A; Bootstrap (brain): N/A" |

**影响**: 稿件声称human/TCGA/brain分析使用B=1000 bootstrap，但实际上这些分析根本不做bootstrap。所有报告的P-values来源存疑。

### C4. TCGA normalization方法不一致

| 文件 | 描述 |
|------|------|
| 稿件 P26 | "FPKM values, log2(x+1) transformed" |
| Supplementary Note 1.6 | "FPKM values from GDC, followed by log2(x+1) transformation" |
| Reproducibility Guide Sec 2 | "log2-transformed data (TCGA), where the +0.001 offset still allows small negative values" |
| Reproducibility Guide Sec 6 | "Normalization (TCGA): log2(TPM+0.001)" |

**影响**: 稿件说FPKM，Reproducibility Guide说TPM；稿件说log2(x+1)，Reproducibility Guide说log2(TPM+0.001)。这是完全不同的数据处理流程，直接影响TCGA所有结果的可复现性。

### C5. Cover Letter声称稿件中无支持的数据

Cover Letter: "cross-species consistency—mouse orthologs show strong correlation with human CKI ω, confirming evolutionary conservation"

稿件中未找到任何mouse orthologs与human CKI ω的相关性分析或数据。稿件P51仅提到"Human ω values...substantively higher than mouse (median ω = 3.63)"，未报告任何cross-species correlation。

**影响**: Cover Letter向编辑承诺了稿件中不存在的分析结果。

---

## 四、Major问题

### M1. Supplementary Note 4.3 TCGA样本数与稿件/CSV不一致

| 癌症类型 | 稿件P26 (tumor+normal) | CSV (phase34_v2_summary.csv) | Supplementary Note 4.3 |
|---------|----------------------|---------------------------|----------------------|
| LUAD | 495+76=571 | 495+76=571 | 515+59=574 |
| LUSC | 567+58=625 | 567+58=625 | 501+51=552 |
| LIHC | 365+57=422 | 365+57=422 | 371+50=421 |
| KIRC | 755+82=837 | 755+82=837 | 533+72=605 |
| BRCA | 1032+109=1141 | 1032+109=1141 | 1093+113=1206 |
| **Total** | **3596** | **3596** | **3358 (声称10,535)** |

稿件与CSV一致，但Supplementary的数字完全不同且总数矛盾（实际加总3358，却声称10,535）。

### M2. Normalization方法描述不一致

| 文件 | 描述 |
|------|------|
| 稿件 P20 | "Softmax normalization converts expression vectors to probability distributions" |
| Supplementary Note 1.1 | "softmax normalization is applied to convert raw expression vectors into probability distributions" |
| Reproducibility Guide Sec 2 | "auto mode: Non-negative values: sum-normalization...Any negative values: softmax" |

实际上mouse/human/brain数据（CP10k+log1p，非负）使用sum-normalization，只有TCGA（log2，可能有负值）使用softmax。稿件和Supplementary一律说"softmax"是不准确的。

### M3. "38 cell types"和"1,406 pairwise ω values"无法验证

稿件P115 Figure 5 legend: "Ranking of 38 cell types by mean pairwise ω...Global distribution of 1,406 pairwise ω values"

数据验证:
- phase35_cross_organ_conservation.csv: 17 unique cell types, 59 pairs
- Table 2: 17 cell types, 59 pairs
- 无法从任何源文件推导出"38 cell types"或"1,406 pairs"

### M4. P19 k_n值来源语境误导

P19: "In our datasets, k_n had a median of 0.0019 (range 0.0006-0.0027)"

此值仅来自mouse的6个C_control comparisons（CSV验证匹配），但"In our datasets"暗示这是所有数据集的k_n统计。实际上：
- Mouse C_control: median=0.0019, range=0.0006-0.0027
- Human (all pairs): median=0.0341, range=0.0018-0.2214
- Brain (all pairs): median=0.0086, range=0.0004-0.1062

P45的表述"across control comparisons"更准确，但P19需要修正语境或明确数据来源。

### M5. 未修复的v10 Moderate数值错误

| # | 位置 | v11稿件值 | CSV正确值 | 偏差 |
|---|------|----------|----------|------|
| 1 | P51 same_ct cross-organ mean ω | 8.70 | 8.6510 | +0.05 |
| 2 | P51 diff_ct same-organ mean ω | 16.18 | 16.0009 | +0.18 |
| 3 | P53 same-organ vs diff-organ | 16.18 vs 13.77 | 16.00 vs 13.58 | 均偏高 |
| 4 | P61 neutrophil SD | ±1.15 | ±1.2248 | -0.07 |
| 5 | P62 cross-organ median ω | 6.9 | 8.7083 | -1.81 |
| 6 | P62 Heart mean ω | 24.3 | 5.52(cross-organ) / 16.59(all human) | 无法匹配 |
| 7 | P62 Lung mean ω | 24.0 | 8.44(cross-organ) / 15.41(all human) | 无法匹配 |
| 8 | P62 Kidney mean ω | 19.0 | 8.20(cross-organ) / 13.13(all human) | 无法匹配 |
| 9 | P62 Spleen mean ω | 18.9 | 10.63(cross-organ) / 14.11(all human) | 无法匹配 |
| 10 | P64 cross-organ correlations | r=-0.40 to +0.02, n=60 | r=-0.59 to +0.04, n=59 | 范围和n均错误 |

### M6. 99 cell types与5,151 pairs数学不一致

- 稿件P50: "99 cell-type entries"
- 稿件P52: "5,151 pairs"
- C(99,2) = 4,851 ≠ 5,151
- phase33_v3_human_pairs.csv: 5,151 rows, 100 unique cell types
- phase35_all_metrics_pairs.csv: 4,851 rows, 67 unique cell types
- Table 1: "99 cell types, 4,851 pairs"（数学一致）

5,151 pairs需要102个cell types (C(102,2)=5,151)，但稿件说99。需澄清pairs数量或cell type数量。

---

## 五、Minor问题

### m1. Python版本不一致
- 稿件P35: "Python 3.12"
- Reproducibility Guide: "Python: 3.13.12"

### m2. CKI包版本不一致
- 稿件P97 / Cover Letter: "v0.3.2"
- Reproducibility Guide Sec 1.2: "Version: 0.3.1"

### m3. HVG flavor不一致
- 稿件P20: "Seurat v3 flavor"
- 稿件P24: "flavor='seurat'"
- Supplementary Note 4.4: "flavor='seurat'"
- Reproducibility Guide: "Scanpy flavor='seurat'"

### m4. LIHC Edmondson grade样本数内部不一致
- P26: "289 tumors"
- P32: "n = 288 tumors"
- P58: G1(39)+G2(133)+G3(105)+G4(11) = 288
- P26的289应为288

### m5. LUAD mutations样本数内部不一致
- P26: "497 samples (61 EGFR, 121 KRAS, 312 WT)"（61+121+312=494≠497）
- P32: "n = 492 samples"
- P58: EGFR(61)+KRAS(120)+WT(311) = 492
- P26的497和121/312应改为492和120/311

### m6. P61文本编辑错误
"reflecting organ-specific gene programs tailored to local vascular needs [19].exhibitedthe strongest functional constraint"
- "exhibitedthe"缺少空格
- 逻辑矛盾：前句说endothelial cells是"lowest conservation"，后句紧接着说"exhibited the strongest functional constraint"（主语缺失）
- 疑似编辑过程中文本拼接错误

### m7. P63文本编辑错误
"cell types.per cell-type coverage. limitedwarranting cautious interpretation"
- 标点错误："types.per"缺少空格
- "limitedwarranting"缺少空格
- 句子结构混乱

### m8. .DS_Store文件
投稿包含.DS_Store（macOS系统隐藏文件），不应包含在投稿包中。

### m9. 稿件P43 omega分布描述
"The empirical ω distribution is right-skewed (median 13.68 vs. mean 14.12 for Tabula Sapiens)"
CSV验证: median=13.6753, mean=14.1184，描述正确。但mean > median只表示右偏，"median vs. mean"的措辞可改进。

---

## 六、文件完整性检查表

| # | 文件名 | 存在 | 格式 | 状态 |
|---|--------|------|------|------|
| 1 | CKI_NAR_Manuscript.docx | Yes | DOCX | OK |
| 2 | CKI_NAR_Cover_Letter.docx | Yes | DOCX | OK |
| 3 | CKI_NAR_Supplementary.docx | Yes | DOCX | OK |
| 4 | CKI_NAR_Reproducibility_Guide.docx | Yes | DOCX | OK |
| 5 | Table1-2.docx | Yes | DOCX | OK |
| 6 | figure1.pdf | Yes | PDF | OK |
| 7 | figure2.pdf | Yes | PDF | OK |
| 8 | figure3.pdf | Yes | PDF | OK |
| 9 | figure4.pdf | Yes | PDF | OK |
| 10 | figure5.pdf | Yes | PDF | OK |
| 11 | figure6.pdf | Yes | PDF | OK |
| 12 | Supplementary_Figure_S1.pdf | Yes | PDF | OK |
| 13 | Supplementary_Figure_S2.pdf | Yes | PDF | OK |
| 14 | Supplementary_Figure_S3.pdf | Yes | PDF | OK |
| 15 | Supplementary_Figure_S4.pdf | Yes | PDF | OK |
| 16 | Supplementary_Figure_S5.pdf | Yes | PDF | OK |
| 17 | CKI_graphical_abstract.pdf | Yes | PDF | OK |
| 18 | CKI_graphical_abstract.png | Yes | PNG | OK |
| 19 | CKI_graphical_abstract.svg | Yes | SVG | OK |
| 20 | .DS_Store | Yes | - | 不应包含 |

**图表引用对应关系**:
- Fig 1-6: 稿件引用figure1-6.pdf OK
- Supplementary Fig S1-S5: 稿件引用Supplementary_Figure_S1-S5.pdf OK
- Table 1-2: 稿件引用Table1-2.docx OK
- Graphical Abstract: 3种格式（PDF/PNG/SVG）均存在 OK

---

## 七、数据可用性声明评估

### 稿件P99 Data Availability声明覆盖的数据源

| 数据源 | 声明中包含 | 可访问性 |
|--------|----------|---------|
| Tabula Muris | GEO GSE109774 | Public |
| Tabula Sapiens | CZ CELLxGENE Discover | Public |
| TCGA | NCI GDC | Public |
| HRT Atlas | housekeeping.unicamp.br | Public |
| Human brain atlas | CZ CELLxGENE Discover | Public |
| PAM50 centroids | Parker et al. [17] | Published |
| MSigDB Hallmark | Liberzon et al. [34] | Published |

### 代码可用性

| 项目 | 声明 | 验证 |
|------|------|------|
| GitHub仓库 | https://github.com/zhanglknt/CKI-cell-type-identification | 声明存在 |
| 版本tag | v0.3.2 | 与Reproducibility Guide的v0.3.1不一致 |
| Zenodo DOI | 10.5281/zenodo.15670808 | 声明存在 |
| License | MIT | OK |
| Requirements | "requirements.txt provided in GitHub" | 未在投稿包中 |

### 评估

**优点**:
- 主要公开数据集均有可用性声明
- 代码仓库和Zenodo归档均有DOI
- MIT License允许自由使用

**不足**:
1. 声明"All analysis notebooks and processed data matrices are included in the Supplementary Data"，但投稿包中未包含notebooks或数据文件——实际上notebooks在GitHub仓库
2. CKI版本号不一致（v0.3.2 vs v0.3.1）
3. Reproducibility Guide提到"Earlier exploratory scripts...have been excluded"，但部分被排除的脚本（如04_phase32_sweep.py）产生的结果仍在稿件中引用（如AUC=0.847），可复现性存疑
4. Reproducibility Guide承认"04_phase32_sweep.py depends on live MSigDB download and cannot be exactly reproduced; ED Fig. 1 uses hard-coded sweep AUC values"——硬编码的AUC值不可复现
5. TCGA数据源在稿件(FPKM)和Reproducibility Guide(TPM)之间不一致，无法确定实际使用了哪种数据

---

## 八、代码可复现性评估

### Reproducibility Guide评估

**优点**:
- 提供了详细的软件环境（Python/包版本）
- 列出了10个分析脚本及其输出文件映射
- 提供了推荐的复现工作流
- 所有参数（random seed=42, HK detection, DE genes等）有明确记录
- 承认了实现细节（如bootstrap null中的epsilon）

**不足**:
1. **脚本排除**: 多个脚本被排除（01_pilot_mouse.py, 05_phase33.py等），部分被排除脚本的结果仍在稿件中引用
2. **硬编码值**: Phase 3.2 sweep的AUC值是硬编码的，"cannot be exactly reproduced"
3. **外部API依赖**: BRCA PAM50数据"cBioPortal API fetched live by script"，跨时间运行可能不一致
4. **FDR未实施**: Reproducibility Guide承认"FDR correction was not systematically implemented"，与稿件声明矛盾
5. **Bootstrap范围**: human/TCGA/brain不做bootstrap，但稿件声称B=1000
6. **跨平台RNG**: "Bootstrap P-values may differ by small amounts (~±0.01) due to...cross-platform RNG implementations may vary"
7. **Python版本**: Guide说3.13.12，稿件说3.12，环境不匹配可能导致结果差异

### 脚本到结果映射验证

| 脚本 | 输出文件 | 稿件引用 | CSV存在 |
|------|---------|---------|--------|
| 02c_pilot_v2b.py | mouse_pilot_v2b_results.csv | Fig 2, P45-48 | Yes (v2b) |
| 03_full_matrix.py | full_matrix_pairs.csv | Fig 2 | Yes |
| 05_phase33_v3_fixed.py | phase33_v3_human_pairs.csv | P50-53 | Yes |
| 13_phase35_method_comparison.py | phase35_cross_organ_conservation.csv | P60-64, Table 2 | Yes |
| 06_phase34_v2.py | phase34_v2_summary.csv | P55-57 | Yes |
| 07_phase34_clinical.py | phase34_clinical_severity.csv | P58 | Yes |
| 07c_brain_siletti_v3.py | brain_siletti_omega_pairs_v3.csv | P67-88 | Yes |

**注意**: mouse_pilot_v2b_results.csv存在，但稿件引用的可能是mouse_pilot_v2_results.csv（文件名差异）。两个文件内容一致（均为15行），但文件命名不一致。

---

## 九、改进建议

### 必须修改（Critical）

1. **统一JS对数底**: 确定使用base-2还是natural log，并在稿件、Supplementary、Reproducibility Guide中统一。若使用natural log，需修正稿件中"range [0,1]"的描述。

2. **统一FDR声明**: 若FDR未实施，删除稿件中所有"FDR correction was applied"和"adjusted q-values are reported"的声明；若已实施，在Reproducibility Guide中提供实施代码。

3. **统一Bootstrap描述**: 若human/TCGA/brain不做bootstrap，删除稿件中"B = 1,000 for human, TCGA, and brain primary analyses"的声明，并说明这些分析的P-values来源。

4. **统一TCGA normalization**: 确定使用FPKM还是TPM，在稿件和Reproducibility Guide中统一。若使用TPM，需修正稿件P26和Supplementary Note 1.6。

5. **修正Cover Letter**: 删除"mouse orthologs show strong correlation with human CKI ω"的声明，或在稿件中补充相应分析。

### 建议修改（Major）

6. **修正Supplementary Note 4.3**: TCGA样本数应与稿件P26和CSV一致（LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109, total 3596）。

7. **修正Normalization描述**: 将"softmax normalization"改为"auto-normalization (sum-normalization for non-negative data; softmax for data with negative values)"。

8. **修正P19 k_n语境**: 将"In our datasets"改为"In mouse control comparisons"或提供所有数据集的k_n统计。

9. **修正"38 cell types"和"1,406 pairs"**: 核实Figure 5的实际数据来源，或改为"17 cell types"和"59 pairs"（与Table 2和CSV一致）。

10. **修正未修复的v10 Moderate数值**: P51的8.70→8.65, 16.18→16.00; P53的13.77→13.58; P61的neutrophil SD 1.15→1.22; P62的median 6.9→8.71; P62的organ means; P64的r范围和n。

11. **澄清99 cell types与5,151 pairs**: 若5,151 pairs来自102 cell types，需修正"99 cell-type entries"；若99 cell types产生4,851 pairs，需统一pairs数量。

### 建议修改（Minor）

12. 统一Python版本（3.12 vs 3.13.12）
13. 统一CKI包版本（v0.3.2 vs v0.3.1）
14. 统一HVG flavor（seurat vs seurat_v3）
15. 修正P26 LIHC n=289→288, LUAD n=497→492
16. 修正P61文本错误（"exhibitedthe"→"exhibited the"，修复逻辑矛盾）
17. 修正P63文本错误（"limitedwarranting"→"limited, warranting"）
18. 删除.DS_Store文件

---

## 十、总结

v11相比v10有显著改善：6个v10 Critical错误中5个已完全修复，1个部分修复。但v11引入了4个新的Critical问题（C1-C4），主要集中在稿件与Supplementary/Reproducibility Guide之间的方法论描述不一致。这些问题虽不影响已有CSV数据的正确性，但严重影响可复现性——研究者按稿件描述的方法无法复现结果。

未修复的10个v10 Moderate数值错误（特别是P62 organ means完全无法从源文件验证）表明这些数值可能来自未公开的中间计算或存在其他数据源，需作者核实。

**评分**: 6/10（v10为4/10，提升2分；主要扣分来自4个新Critical问题和10个未修复Moderate数值错误）
