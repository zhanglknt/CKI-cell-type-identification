# CKI 稿件写作质量与期刊适配审稿报告

**审稿人**: journal-reviewer  
**日期**: 2026-07-26  
**稿件版本**: v10 (v10_manuscript_fulltext.txt)  
**稿件标题**: CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling  
**篇幅**: ~12,000词, 167段落, 6主图 + 5补充图, 40篇参考文献

---

## 一、写作质量评分

### 总评分: 6.5 / 10

| 维度 | 评分 | 说明 |
|------|------|------|
| 摘要质量 | 8/10 | 非结构化单段，~167词（≤200词合规），逻辑清晰：问题→灵感→方法→验证→结论 |
| Introduction逻辑递进 | 8/10 | 五段递进清晰：问题→生物学意义→Ka/Ks类比→CKI方案→验证计划 |
| Methods完整性 | 7/10 | 覆盖全面（CKI计算、bootstrap、数据集、统计报告），可复现性较好；但P19存在冗余重复 |
| Results叙事流畅性 | 6/10 | 整体结构合理（校准→标准指标比较→癌症→跨器官→脑），但多处文本损坏、语句拼接错误 |
| Discussion深度 | 7.5/10 | 局限性讨论诚实充分，Ka/Ks类比讨论有深度；但P90存在断句错误 |
| 术语一致性 | 5.5/10 | 标题"Cell-state"与GitHub URL"cell-type"不一致；文中"cell type"与"cell state"混用 |
| 图表引用正确性 | 4/10 | Figure 5 legend严重损坏（P114/P115重复），多处图例与正文描述不匹配 |
| 语法/排版 | 5/10 | 多处中文标点混入英文正文；多处单词拼接缺失空格 |

### 关键写作问题清单

#### 1. 文本损坏（严重）
- **P60**: `exhibitedthe strongest` — 缺失空格，且句子结构混乱（两个版本拼接）
- **P62**: `cell types.per cell-type coverage. limitedwarranting cautious interpretation` — 多句无空格拼接，语义断裂
- **P90**: `not a classifierCKI answers` — 缺失句号和空格，两个独立句子被拼接
- **P52**: 末尾 `Although CKI yielded a lower cell-type classification AUC...` 段落以不完整句子开始，且与上文重复

#### 2. 中文标点混入英文正文（必须修复）
- **P54** (line 113): `Fig. 4，Supplementary Fig. S2` — 中文逗号 `，`
- **P57** (line 119): `Furthermore，to determine` — 中文逗号 `，`
- **P72** (line 149): `（Supplementary Fig. S5）` — 中文括号 `（）`

#### 3. Methods冗余（P19）
同一段落内重复说明JS散度使用base-2对数：
- 第一次: `JS divergence uses base-2 logarithm (range [0,1])`
- 第二次: `The JS divergence implementation uses base-2 logarithm (np.log2 in Python) with range [0, 1]`

HVG selection的Seurat v3 flavor也在同段重复说明。

#### 4. Figure 5 Legend问题（严重，用户已标注）
- **P114**: 完全损坏。多个草稿版本被拼接在一起：`Ranking of 38 cell types by mean pairCross-organ ω heatmap for same cell types appearing in multiple organs, showise ω across six organs` — 语义破碎，无法使用
- **P115**: 用户重写的干净版本，内容正确：(A) 38个细胞类型排序，(B) 1,406个ω值分布，(C) 跨器官ω梯度
- **处理建议**: 删除P114，保留P115。用户批注Comment 31明确要求"建议全部删除"

#### 5. 标题/命名不一致
- 标题: "Cell-state Kinetic Index"
- GitHub URL: "CKI-cell-type-identification"（使用"cell-type"）
- 正文: 大量使用"cell type"而非"cell state"
- **建议**: 统一为"Cell-state Kinetic Index"并更新GitHub仓库名，或将标题改为"Cell-type Kinetic Index"

#### 6. 数据数值与用户批注不一致
以下数值需与用户核实（来自v10_comments.txt）：
- **k_n统计**: 稿件P19/P45写 `median k_n = 0.0086, range 0.0004–0.106`；用户手算 `k_n median = 0.034, range 0.0018-0.221`
- **ω < 15比例**: 稿件P19写 `93.6%`；用户批注Comment 4认为应为 `56.3%`
- **k_n < 0.001的pair数**: 稿件P19写 `48 of 5,151 pairs (0.93%)`；用户批注Comment 3称手算未发现k_n < 0.001的pair
- **P45**: `0.15% of 5,151` — 48/5151 = 0.93%，但P45写0.15%，数值矛盾

> **注意**: 这些数值矛盾可能涉及核心结果的准确性，建议data-reviewer和stats-reviewer协同核实。

---

## 二、NAR合规性检查

### 合规清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 章节顺序: Intro→Methods→Results→Discussion | ✅ 合规 | P10→P16→P37→P88 |
| 摘要≤200词，非结构化 | ✅ 合规 | ~167词，单段 |
| Graphical Abstract placeholder | ✅ 合规 | P6-P7 |
| 行间距/格式 | ⚠️ 无法从文本验证 | 需检查DOCX |
| 无行号，仅页码 | ⚠️ 无法从文本验证 | 需检查DOCX |
| 参考文献格式 | ❌ 不合规 | 见下文详细分析 |
| 图表字号≥7pt, 300DPI | ⚠️ 无法从文本验证 | 需检查实际图片 |
| 单栏86mm/双栏178mm | ⚠️ 无法从文本验证 | 需检查实际图片 |
| Data availability声明 | ⚠️ 部分合规 | 有数据来源但未单独分出"Code availability"章节 |
| GitHub + Zenodo DOI | ✅ 合规 | P98包含两者 |
| 面板标签大写A/B/C | ✅ 合规 | Figure legends中使用(A)(B)(C) |
| Cover Letter要求 | ⚠️ 不在本文范围 | 需单独检查 |

### 参考文献格式问题（严重不合规）

**NAR要求格式**:  
`Author,A.B., Author,C.D. and Author,E.F. (Year) Title. *Journal.*, **Vol**, Pages.`

**当前格式**（以P126为例）:  
`1.Korsunsky I, Millard N, Fan J et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat Methods 2019;16: 1289-1296. https://doi.org/10.1038/s41592-019-0619-0`

**具体问题**:
1. 作者名格式: `Korsunsky I` → 应为 `Korsunsky,I.`
2. 年份位置: `Nat Methods 2019;16` → 应在作者后括号内 `(2019)`
3. 期刊名: `Nat Methods` → 应斜体缩写带句点 `*Nat. Methods.*`
4. 卷号: `16` → 应加粗 `**16**`
5. 编号格式: `1.Korsunsky` → NAR使用括号编号 `(1)` 而非句点编号
6. DOI: 包含 `https://doi.org/` 前缀，NAR通常使用纯DOI
7. et al.前作者数: 稿件多用3人后et al.，NAR允许最多20人

**影响**: 全部40篇参考文献均需重新格式化。这是一项系统性工作。

### 数据/代码可用性声明

当前P97-P98将数据和代码合并在一个"Data availability"章节中。NAR建议分设：
- **Data availability**: 仅数据来源
- **Code availability**: GitHub URL + Zenodo DOI + 许可证 + 编程语言 + 操作系统

当前缺少：编程语言、操作系统、许可证的独立声明（MEMORY.md要求：项目名称、主页URL、归档版本DOI、操作系统、编程语言、其他要求、许可证）。

---

## 三、期刊推荐排序

### 稿件特征画像
- **类型**: 计算方法学（单细胞转录组分析工具）
- **创新性**: 中等偏高（Ka/Ks类比思路新颖，但底层JS散度非新方法）
- **验证广度**: 强（4个数据集，3个物种/系统，~百万细胞）
- **实用价值**: 中等（Python包开源，但应用场景相对专一）
- **理论深度**: 中等（启发式方法，非严格进化模型）
- **篇幅**: 较长（~12,000词），数据量大

### 期刊推荐排序表

| 排名 | 期刊 | IF | Scope匹配度 | 接受概率 | 投稿建议 |
|------|------|-----|------------|----------|----------|
| 1 | **NAR** | ~16.7 | 4/5 | 15-20% | **当前首选，维持目标**。NAR接受计算方法论文，CKI的"基因组学方法"定位匹配。需修复参考文献格式和写作问题。OUP出版，IF在方法类期刊中优秀。 |
| 2 | **Genome Biology** | ~12.3 | 4/5 | 15-20% | **最佳备选**。单细胞基因组学方法的核心期刊，读者群精准。开放获取，审稿质量高。Tabula Muris/Sapiens相关工作常发表于此。 |
| 3 | **Cell Systems** | ~9 | 4/5 | 12-18% | 系统生物学角度契合CKI的"框架"定位。Cell Press品牌效应好。但偏好更偏机制建模。 |
| 4 | **Bioinformatics** | ~5.8 | 5/5 | 25-30% | **Scope完美匹配，安全选择**。算法方法的标准发表平台。但IF偏低，可能不符合作者期望。审稿快。 |
| 5 | **Cell Reports Methods** | ~7 | 4/5 | 20-25% | Cell Press新刊，方法导向，接受率相对友好。但期刊声誉尚在建立中。 |
| 6 | **Genome Research** | ~7.4 | 4/5 | 15-20% | 基因组方法学老牌期刊。但更偏基因组层面分析，单细胞转录组非核心scope。 |
| 7 | **PLOS Comp Biol** | ~4.3 | 5/5 | 30-40% | **保底选择**。Scope完美，接受率高，开放获取。但IF低。 |
| 8 | **Briefings in Bioinformatics** | ~9.5 | 3/5 | 10-15% | 偏综述类，原创方法发表较少。除非改写为方法综述。 |
| 9 | **Nature Communications** | ~14.7 | 3/5 | 8-12% | 综合性期刊，CKI可能被认为不够广泛。审稿周期长。 |
| 10 | **Nature Methods** | ~48 | 3/5 | 5-8% | **过于冒险**。虽高IF，但CKI的JS散度非新算法，Ka/Ks类比为启发式而非技术突破。除非有更强的benchmarking数据。 |

### 推荐投稿策略

**首选方案: NAR（维持当前目标）**

理由：
1. NAR的"Computational Biology"类别明确接受单细胞分析方法
2. IF 16.7在方法类期刊中属于第一梯队
3. CKI的Ka/Ks类比与NAR的核酸研究scope有概念关联
4. 已有HRT Atlas [4]等HK基因数据库发表在NAR上，读者群重合
5. OUP出版流程规范

**投稿前必须修复**：
1. 参考文献全部重新格式化为NAR格式（最耗时）
2. Figure 5 legend（删除P114，保留P115）
3. 所有中文标点替换为英文标点
4. 文本损坏修复（P60, P62, P90, P52）
5. 数据数值核实（k_n统计量、ω<15比例等）
6. 分设Data/Code availability章节
7. 统一"Cell-state"命名

**备选方案: Genome Biology**

若NAR拒稿，Genome Biology是最佳备选：
1. 单细胞方法学核心期刊
2. 开放获取，影响力强
3. 稿件已按GB格式有过投稿历史（MEMORY.md显示v16投稿包）
4. 审稿速度较快

**保底方案: Bioinformatics 或 PLOS Comp Biol**

若需快速发表，这两个期刊scope完美匹配且接受率较高。

---

## 四、推荐审稿人

以下审稿人按领域分组推荐，需在Cover Letter中提供6位以上。**注意：以下邮箱为机构公开邮箱，投稿前请核实有效性。**

### 单细胞转录组学方法开发

1. **Fabian Theis**  
   机构: Helmholtz Munich & Technical University of Munich  
   邮箱: fabian.theis@helmholtz-munich.de  
   专长: 单细胞计算方法，scVI开发者，scanpy核心贡献者（稿件引用[2][10]）

2. **Sarah Teichmann**  
   机构: Wellcome Sanger Institute  
   邮箱: st1@sanger.ac.uk  
   专长: 单细胞图谱，细胞类型分类学，Tabula Sapiens发起人（稿件引用[6]）

3. **Joshua Welch**  
   机构: University of Michigan, Department of Computational Medicine and Bioinformatics  
   邮箱: welchjd@umich.edu  
   专长: 单细胞轨迹分析，降维方法开发

### 分子进化 / Ka/Ks

4. **Ziheng Yang**  
   机构: University College London, Department of Genetics, Evolution and Environment  
   邮箱: z.yang@ucl.ac.uk  
   专长: 分子进化，PAML开发者，Ka/Ks方法权威（稿件引用[31][39][40]）  
   ⚠️ 注意：因稿件引用其工作较多，可能存在利益相关，请酌情考虑

5. **Jianzhi George Zhang**  
   机构: University of Michigan, Department of Ecology and Evolutionary Biology  
   邮箱: jianzhi@umich.edu  
   专长: 分子进化，基因表达进化，Ka/Ks方法应用

### 计算生物学 / 生物信息学

6. **Aaron Lun**  
   机构: Cancer Research UK Cambridge Institute  
   邮箱: aaron.lun@cruk.cam.ac.uk  
   专长: 单细胞生物信息学，Bioconductor核心开发者，统计方法审稿经验丰富

7. **Daifeng Wang**  
   机构: University of Wisconsin-Madison, Department of Biostatistics and Medical Informatics  
   邮箱: dwang382@wisc.edu  
   专长: 单细胞基因组学，细胞类型注释方法，脑图谱分析

### 细胞类型分类学 / 脑图谱

8. **Hongkui Zeng**  
   机构: Allen Institute for Brain Science  
   邮箱: hongkuiZ@alleninstitute.org  
   专长: 脑细胞类型分类学，单细胞图谱，Allen Brain Atlas（与稿件脑分析部分高度相关）

### 推荐审稿人选择建议

Cover Letter建议推荐以下6位（兼顾领域覆盖和避免利益冲突）：
1. Fabian Theis（单细胞方法）
2. Sarah Teichmann（单细胞图谱/细胞类型）
3. Joshua Welch（单细胞计算方法）
4. Jianzhi George Zhang（分子进化/Ka/Ks）
5. Aaron Lun（生物信息学方法）
6. Hongkui Zeng（脑细胞分类学）

避免推荐：
- 稿件合作者或同机构研究者
- Ziheng Yang（因稿件大量引用其工作，编辑可能认为存在偏见）
- Tabula Muris/Sapiens/Siletti的通讯作者（数据来源，可能存在利益冲突）

---

## 五、投稿策略建议

### 近期行动清单（按优先级）

**P0 — 投稿阻断项（必须修复）**：
1. 修复Figure 5 legend（删除P114，保留P115）
2. 修复所有文本损坏（P60, P62, P90, P52）
3. 替换所有中文标点为英文标点（P54, P57, P72）
4. 核实并修正数据数值（k_n统计量、ω<15比例、k_n<0.001 pair数）— 需与data-reviewer/stats-reviewer协同
5. 参考文献全部重新格式化为NAR格式

**P1 — 投稿前应修复**：
6. 统一"Cell-state"命名（标题 vs GitHub URL vs 正文用法）
7. 分设Data availability和Code availability章节
8. 删除Methods P19中的冗余重复
9. 补充Code availability中的操作系统、编程语言、许可证信息
10. 检查图表实际规格（字号≥7pt, 300DPI, 尺寸）

**P2 — 建议改进**：
11. 摘要中增加一句 limitations 或 future outlook
12. Discussion中增加与更多现有方法的定量比较
13. 考虑增加一个工作流示意图（已有Graphical Abstract placeholder）

### 投稿时间线建议

1. **数据核实**（协同data-reviewer/stats-reviewer）：确认所有统计数值
2. **文本修复**：修复所有写作问题（预计1-2天工作量）
3. **参考文献重排**：40篇全部改为NAR格式（可脚本辅助，需人工校验）
4. **Cover Letter准备**：包含推荐审稿人、AI使用声明、ORCID
5. **最终检查**：按NAR投稿清单逐项验证

### 整体评估

CKI稿件在概念创新性（Ka/Ks类比）和验证广度（4数据集/3系统）方面有亮点，适合NAR投稿。但当前v10版本存在较多写作质量问题（文本损坏、中文标点、Figure 5 legend问题）和格式合规问题（参考文献格式），需在投稿前系统性修复。数据数值矛盾是最需优先解决的问题，建议与data-reviewer和stats-reviewer协同核实。

**建议**: 修复上述问题后投稿NAR。若NAR拒稿，转投Genome Biology。
