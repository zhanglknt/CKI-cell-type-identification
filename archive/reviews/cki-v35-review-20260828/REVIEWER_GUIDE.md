# CKI v35 专家团交叉审稿指南

## 审稿对象

**CKI v35 投稿包**：`version3/CKI_NAR_Submission_v35/`（2026-08-28 14:54 构建，softmax 统一后修订版）

论文：CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
目标期刊：Nucleic Acids Research (NAR)

## 材料路径（审稿人必读）

审稿材料已提取到本目录 `review_material/`（完整文本，含表格）：
- `CKI_NAR_Manuscript_full_extract.txt` — 主稿件（207 行，含 Table 1/2）
- `CKI_NAR_Supplementary_full_extract.txt` — 补充材料
- `CKI_NAR_Cover_Letter_full_extract.txt` — 投稿信
- `CKI_NAR_Reproducibility_Guide_full_extract.txt` — 复现指南
- `Table1-2_full_extract.txt` — 参数表

原始 DOCX 与图表在 `version3/CKI_NAR_Submission_v35/`（如需要可自行用 python-docx 或阅读 PDF）。

## v35 相对上一版（v5, 2026-08-24 审稿）的重大修订

审稿人应重点验证这些修订是否正确落实、是否引入新矛盾：

1. **softmax 归一化全尺度统一**：`js_divergence` 使用 base-2 对数、softmax 概率归一化（非 L1 normalize）；修复了双重 softmax bug。全部数据集（小鼠/人类/TCGA/脑区）已用 softmax 标准重跑。
2. **脑区 block-shuffle null 重算**（回应 v5 C1）：per-pair 单侧置换 P + BH-FDR（m=31,764）。结果：0 个 FDR q<0.05（min q=0.949），Strong 候选 55 个（37 个 raw P<0.05），脑区定位为 hypothesis-generating。OPC 贡献 27/55 Strong 候选（v5 旧叙事为"OPC 0 Strong"）。
3. **人类 phase35 重跑**：n=4,851 对，ω mean 21.61 / median 19.65；AUC：CKI 0.680（5/5 方法中第 5）、Raw JS 0.849、Cosine 0.887、Jaccard 0.801、Spearman 0.690；CKI 与四标准度量负相关 r=-0.36~-0.46。
4. **phaseB/C 统计升级**：kn CV 92.89%、per-pair vs global-kn Spearman +0.181（v5 旧值 CV 97.35%、ρ −0.027）。
5. **TCGA kn floor 说明**：TCGA 5 癌种 aggregate TN kn = 3.0e-5~1.9e-4（3/5 触及 floor 1e-4），ω 在 floor 处饱和。
6. **cross-organ 新值**：same-CT cross-organ 15.83（n=59）、same-organ diff-CT 24.87（n=1,038）、diff-organ diff-CT 20.80。
7. **v0.3.2 修复**：cki/core.py 恢复 log2 JS + kn_min=1e-4 clamp，与 Methods"base-2 logarithm"一致。

## 审稿重点（各专家按专业方向聚焦）

### 通用核查
- 数字一致性：正文 ↔ 摘要 ↔ 图注 ↔ 表格 ↔ 补充材料 ↔ 复现指南之间的所有数值是否一致
- 图表与正文叙事是否一致（尤其图注中的类别定义、tier 计数、机制叙述）
- 投稿包完整性：MANIFEST_v35.txt 声明与实际文件是否相符

### 已知关注点（请独立验证，不要直接采信）
以下为审稿协调员发现的可疑点，请验证其是否真实存在、影响程度如何，并可补充未列出的新问题：
1. Figure 2B 图注：comparison categories "C (same cell type), S (same sub-organ), D (different cell type within same organ), X (cross-organ)"，但正文 Results 中 S 定义为 "Same cell type across different organs"。类别定义是否矛盾？
2. Supplementary Figure S7 (B) 图注：写 "OPCs (0 Strong despite highest motility among the 10 non-neuronal classes) provide a key internal consistency check"，但正文 Results 写 "OPCs contributed 27 Strong candidates"。图注与正文是否直接矛盾？
3. References 中 BH-FDR 的引用位置：正文 Methods 写 "Benjamini-Hochberg FDR correction ... (23)"，ref 23 是 Storey & Tibshirani 2003（q-value 方法），不是 Benjamini & Hochberg 1995。引用是否错配？
4. 稿件 Data availability 声明 "All analysis notebooks and processed data matrices are included in the Supplementary Data"，但 v35 投稿包内只有 DOCX/PDF/图，无代码或数据文件。声明与实际是否不符？
5. Methods Statistical reporting 段落：FDR 检验数表述为 "determined by the number of cell types (10 for brain, 17 for human per-cell-type, 15 for mouse)"，但脑区 per-pair FDR 是 m=31,764。两处是否矛盾或需要澄清？
6. Results 人类段落：mouse 比较基准 27.31 来自 mouse pilot X 类别（n=2），与 human 4,851 对全均值 21.61 比较是否恰当？
7. 摘要 "a human brain single-nucleus atlas from millions of cells" 与实际分析 888,263 核（atlas 全量 ~3.3M）的表述是否妥当？

## 输出格式

请将审稿报告写入 `output/cki-v35-review-20260828/review_material/expertN_<方向>.md`，并返回 300 字以内的摘要。

报告格式：
- 总体评价（接受/小修/大修/拒稿倾向）
- Critical 问题（逐条：问题描述、文件位置/行号、修改建议）
- Major 问题（同上）
- Minor 问题（同上）
- 遗留可接受项（上一轮问题已妥善解决的可确认项）
