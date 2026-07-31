# CKI v11 稿件写作质量与期刊推荐审稿报告

**审稿人**: journal-reviewer
**日期**: 2026-07-26
**稿件版本**: v11 (v11_manuscript_fulltext.txt)
**稿件标题**: CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling
**篇幅**: ~11,002词（正文，不含参考文献），170词摘要，6主图 + 5补充图，40篇参考文献
**Cover Letter**: CKI_NAR_Cover_Letter_fulltext.txt（含ORCID、AI使用声明、代码可用性）

---

## 一、总评分: 6.0 / 10

| 维度 | 评分 | 说明 |
|------|------|------|
| 摘要质量 | 8/10 | 非结构化单段，170词（≤200词合规），逻辑清晰：问题→灵感→方法→验证→结论 |
| Introduction逻辑递进 | 8/10 | 五段递进清晰：问题→生物学意义→Ka/Ks类比→CKI方案→验证计划 |
| Methods完整性 | 6.5/10 | 覆盖全面，但P20存在3处冗余重复（base-2 log、Seurat v3、softmax各重复2次） |
| Results叙事流畅性 | 5/10 | 整体结构合理，但4处文本损坏未修复（P55/P56/P61/P63/P91），严重影响可读性 |
| Discussion深度 | 6.5/10 | 局限性讨论诚实充分，Ka/Ks类比讨论有深度；但P91存在断句+不完整句子 |
| 术语一致性 | 5/10 | 标题"Cell-state"（3次）vs 正文"Cell-type"（55次）vs GitHub URL"cell-type"——严重不一致 |
| 图例完整性 | 8/10 | **Fig5 legend已修复**（v10乱码已消除）；其余图例完整清晰 |
| 语法/排版 | 4.5/10 | 3处中文标点未修复；2处单词拼接缺失空格；1处句子断裂不完整 |

### v10 → v11 修复情况对比

| v10问题 | v11状态 | 说明 |
|---------|---------|------|
| Fig5 legend乱码（P114草稿拼接） | ✅ **已修复** | 乱码P114已删除，保留干净P115 |
| 中文逗号 P54 `Fig. 4，` | ❌ **未修复** | P55仍为 `Fig. 4，Supplementary` |
| 中文逗号 P57 `Furthermore，` | ❌ **未修复** | P58仍为 `Furthermore，to determine` |
| 中文括号 P72 `（Supplementary）` | ❌ **未修复** | P73仍为 `（Supplementary Fig. S5）` |
| 文本损坏 P60 `exhibitedthe` | ❌ **未修复** | P61仍为 `[19].exhibitedthe strongest` |
| 文本损坏 P62 `limitedwarranting` | ❌ **未修复** | P63仍为 `types.per cell-type coverage. limitedwarranting` |
| 文本损坏 P90 `classifierCKI` | ❌ **未修复** | P91仍为 `not a classifierCKI answers` |
| Methods P19冗余 | ❌ **未修复** | P20仍有3处重复（base-2 log、Seurat v3、softmax） |
| 标题/URL命名不一致 | ❌ **未修复** | Cell-state（3次）vs Cell-type（55次）vs URL含cell-type |

---

## 二、写作Critical问题（投稿阻断项）

### C1. P91 Discussion段落严重损坏——句子拼接+不完整句
**位置**: P91 (line 183)
**问题**: 两个独立句子被拼接为一，且段落以不完整句结尾：
```
CKI is explicitly designed as a perturbation index, not a classifierCKI answers a complementary question...
```
- `classifierCKI` 之间缺失句号和空格
- 段落末尾 `While cell-type classification from transcriptomes is a mature field,` ——以逗号结尾的不完整句，下文被截断
**影响**: Discussion核心段落无法理解，编辑/审稿人无法评估CKI的定位论述
**修复建议**: 拆分为两句：`...not a classifier. CKI answers a complementary question:...`；补全末尾句子或删除残句

### C2. P61 Results段落文本损坏——双版本拼接+重复内容
**位置**: P61 (line 123)
**问题**: Track Changes接受后的残留，两个版本的文本被拼接：
```
...endothelial cells exhibited the lowest conservation (mean ω = 15.09 ± 6.46, n = 3 pairs), reflecting organ-specific gene programs tailored to local vascular needs [19].exhibitedthe strongest functional constraint, maintaining highly conserved transcriptional programs regardless of anatomical location.
```
- `[19].exhibitedthe` 缺失空格——句号后直接接新句子，无空格
- `exhibitedthe` 缺失空格
- 随后又重复 `In stark contrast, Endothelial cells (mean 15.09 ± 6.46, n = 3)` ——与段首数据完全重复
**影响**: 段落逻辑混乱，读者无法判断哪段是正确版本
**修复建议**: 删除重复版本，保留一个连贯叙述

### C3. P63 Results段落文本损坏——多句无空格拼接
**位置**: P63 (line 127)
**问题**:
```
...underrepresented organs and cell types.per cell-type coverage. limitedwarranting cautious interpretation of their absolute rankings (Table 2).
```
- `types.per` 缺失空格
- `limitedwarranting` 缺失空格和句号
- `per cell-type coverage.` 是孤立的不完整片段
**影响**: 句子语义断裂，无法理解
**修复建议**: 重写该句为完整通顺的表述

### C4. P55 Results末尾孤立句子片段
**位置**: P55 (line 111)
**问题**: 段落末尾有一孤立句子片段：
```
...Future single-cell cancer atlas studies would enable more precise characterization of cell-type-specific selective remodeling. ω magnitudes, which are not directly comparable to single-cell-derived ω values.
```
最后一句 `ω magnitudes, which are not directly comparable to single-cell-derived ω values.` 是一个不完整的句子片段（无主句），疑似Track Changes残留
**修复建议**: 删除该孤立片段，或将前文相关句子补全

---

## 三、写作Major问题

### M1. 中文标点残留（3处，v10已标注但未修复）
| 位置 | 原文 | 问题字符 | 修复 |
|------|------|----------|------|
| P55 (line 111) | `Fig. 4，Supplementary` | `，`（中文逗号） | → `Fig. 4, Supplementary` |
| P58 (line 117) | `Furthermore，to determine` | `，`（中文逗号） | → `Furthermore, to determine` |
| P73 (line 147) | `（Supplementary Fig. S5）` | `（）`（中文括号） | → `(Supplementary Fig. S5)` |

**影响**: NAR编辑可能直接退稿——中文标点在英文学术论文中是不可接受的排版错误

### M2. P56 缺失空格——`Cohen's danalysis`
**位置**: P56 (line 113)
**问题**: `Bootstrapped Cohen's danalysis revealed` —— `d` 和 `analysis` 之间缺失空格
**应为**: `Bootstrapped Cohen's d analysis revealed`

### M3. Methods P20 冗余重复
**位置**: P20 (line 41)
**问题**: 同一段落内3处关键信息重复说明：
- `base-2 logarithm` 出现2次：`JS divergence uses base-2 logarithm (range [0,1])` + `The JS divergence implementation uses base-2 logarithm (np.log2 in Python) with range [0, 1]`
- `Seurat v3 flavor` 出现2次：`Seurat v3 flavor` 在HVG选择描述中出现2次
- `softmax normalization` 出现2次：`Softmax normalization converts expression vectors to probability distributions` + `Expression-to-probability conversion uses softmax normalization`
**修复建议**: 合并重复描述，每种实现细节只说明一次

### M4. 标题/命名严重不一致
- **标题**: "Cell-state Kinetic Index"（使用"Cell-state"）
- **GitHub URL**: `CKI-cell-type-identification`（使用"cell-type"）
- **正文**: "Cell-state"仅出现3次，"Cell-type"出现55次
- **摘要**: 使用"Cell-state Kinetic Index"但随后用"cell populations"

**影响**: 编辑和审稿人会对概念定义产生困惑——CKI到底量化"cell state"还是"cell type"？
**修复建议**: 统一为"Cell-state Kinetic Index"（因标题已定），正文中的"cell type"在指代CKI概念时应改为"cell state"；或统一改为"Cell-type"并更新标题

### M5. 参考文献格式完全不合规（40/40篇）
**NAR要求格式**: `Author,A.B. and Author,C.D. (Year) Title. *Journal.* **Vol**, Pages.`
**当前格式**: `1.Korsunsky I, Millard N, Fan J et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat Methods 2019;16: 1289-1296. https://doi.org/...`

| 问题 | 当前 | NAR要求 |
|------|------|---------|
| 作者名 | `Korsunsky I` | `Korsunsky,I.` |
| 年份位置 | `Nat Methods 2019;16` | `(2019)` 在作者后 |
| 期刊名 | `Nat Methods` | `*Nat. Methods.*`（斜体缩写带句点） |
| 卷号 | `16` | `**16**`（加粗） |
| 编号 | `1.Korsunsky` | `(1)` 括号编号 |
| DOI | 含 `https://doi.org/` 前缀 | NAR通常使用纯DOI或不含DOI |
| et al. | 3人后即用et al. | NAR允许列出最多20人 |

**影响**: 全部40篇参考文献均需重新格式化——这是系统性工作，但属于投稿阻断项

---

## 四、写作Minor问题

### m1. P53 AUC论述重复
P53在同一段落内3次讨论AUC比较：
1. `CKI showed moderate cell-type classification performance (AUC = 0.716...but below cosine distance at AUC = 0.887...)`
2. `CKI's AUC (0.716) and cosine distance's AUC (0.887) are not directly analogous...`
3. `Although CKI yielded a lower cell-type classification AUC than cosine similarity...`

**建议**: 合并为一次完整论述，避免在同段内反复强调同一观点

### m2. P55 句子结构混乱
P55末尾有多处语义重复和断裂：
- `Because TCGA profiles are bulk RNA-seq...interpretation focuses on relative patterns (tumor vs. normal) rather than absolute ω magnitudes.` 
- 紧接 `Additionally, because bulk profiles aggregate signals...`
- 再接 `Without cell-type deconvolution, we cannot fully disentangle these contributions.`
- 然后是 `Future single-cell cancer atlas studies would enable more precise characterization...`
- 最后孤立片段 `ω magnitudes, which are not directly comparable to single-cell-derived ω values.`

三句连续讨论bulk RNA-seq的局限性，表述冗长。建议精简为1-2句。

### m3. Cover Letter缺少推荐审稿人
NAR投稿通常要求在Cover Letter或投稿系统中提供推荐审稿人。当前Cover Letter未包含此信息。
**建议**: 添加3-5位推荐审稿人（含姓名、机构、邮箱、专长理由）

### m4. Data/Code availability未分设
当前P98-P99将数据和代码合并在一个"Data availability"章节。NAR建议分设：
- **Data availability**: 仅数据来源
- **Code availability**: GitHub URL + Zenodo DOI + 许可证 + 编程语言（Python 3.12）+ 操作系统

### m5. Graphical Abstract仅为占位符
P7-P8仅有 `[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]`，实际图片尚未制作。NAR要求Graphical Abstract与稿件一同提交。
**建议**: 投稿前完成Graphical Abstract制作

### m6. 摘要中数值与前文不一致风险
摘要写 `mean ω = 1.54, all P > 0.05`，而P47写 `mean ω was 1.54 (median 1.42, range 1.09–2.10)`。数值一致，但摘要未提及median和range——这属于可接受的摘要精简，非问题。但需确认stats-reviewer验证这些数值的准确性。

---

## 五、NAR合规性检查表

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 章节顺序: Intro→Methods→Results→Discussion | ✅ 合规 | P11→P17→P38→P89 |
| 摘要≤200词，非结构化单段 | ✅ 合规 | 170词，单段 |
| Graphical Abstract | ⚠️ 占位符 | P7-P8仅有占位符，需实际制作 |
| 行间距/格式 | ⚠️ 无法从文本验证 | 需检查DOCX（NAR要求单倍行距） |
| 无行号，仅页码 | ⚠️ 无法从文本验证 | 需检查DOCX |
| 参考文献格式 | ❌ 不合规 | 40/40篇均为Vancouver格式，0篇符合NAR格式 |
| 图表字号≥7pt, 300DPI | ⚠️ 无法从文本验证 | 需检查实际图片 |
| 单栏86mm/双栏178mm | ⚠️ 无法从文本验证 | 需检查实际图片 |
| Data availability声明 | ⚠️ 部分合规 | 有数据来源但未分设Code availability |
| GitHub + Zenodo DOI | ✅ 合规 | P99包含两者 |
| 面板标签大写A/B/C | ✅ 合规 | Figure legends中使用(A)(B)(C) |
| Cover Letter | ⚠️ 基本合规 | 有ORCID、AI声明、代码链接；缺推荐审稿人 |
| Track Changes残留 | ✅ 合规 | 文本中未发现TC标记（0条） |
| 中文标点残留 | ❌ 不合规 | 3处中文标点（P55、P58、P73） |
| 中文标点残留（Cover Letter） | ✅ 合规 | Cover Letter中无中文标点 |
| ORCID | ✅ 合规 | P6和Cover Letter均包含 |
| AI使用声明 | ✅ 合规 | Cover Letter包含 |
| 利益冲突声明 | ✅ 合规 | P108-P109 |
| 资金声明 | ✅ 合规 | P106-P107（NSFC等3项基金） |
| 作者贡献 | ✅ 合规 | P104-P105 |

### 合规性总结
- ✅ 合规: 11项
- ⚠️ 需进一步验证/部分合规: 7项
- ❌ 不合规: 2项（参考文献格式、中文标点）

---

## 六、期刊推荐

### 稿件特征画像
- **类型**: 计算方法学（单细胞转录组分析工具）
- **创新性**: 中等偏高（Ka/Ks类比思路新颖，但底层JS散度非新方法）
- **验证广度**: 强（4个数据集，3个物种/系统，百万级细胞）
- **实用价值**: 中等（Python包开源，但应用场景相对专一）
- **理论深度**: 中等（启发式方法，非严格进化模型；Discussion有诚实的局限性讨论）
- **篇幅**: ~11,000词，数据量大
- **写作质量**: 中等偏下（多处文本损坏未修复，但修复后可达NAR标准）

### 期刊推荐排序

| 排名 | 期刊 | IF | Scope匹配度 | 接受概率 | 投稿建议 |
|------|------|-----|------------|----------|----------|
| **1** | **NAR** | ~16.7 | 4/5 | 12-18% | **维持当前目标**。NAR接受计算方法论文，CKI的"基因组学方法"定位匹配。HRT Atlas [4]已发表在NAR上，读者群重合。但需先修复所有Critical/Major问题。 |
| **2** | **Genome Biology** | ~12.3 | 4/5 | 15-20% | **最佳备选**。单细胞基因组学方法的核心期刊，开放获取，审稿质量高。Tabula Muris/Sapiens相关工作常发表于此。 |
| **3** | **Cell Systems** | ~9 | 4/5 | 12-18% | 系统生物学角度契合CKI的"框架"定位。Cell Press品牌效应好。偏好更偏机制建模。 |

### 首选方案: NAR（维持当前目标）

**理由**:
1. NAR的"Computational Biology"类别明确接受单细胞分析方法
2. IF 16.7在方法类期刊中属于第一梯队
3. CKI的Ka/Ks类比与NAR的核酸研究scope有概念关联
4. HRT Atlas [4]等HK基因数据库已发表在NAR上，读者群重合
5. OUP出版流程规范，审稿周期可预期

**投稿前必须修复**（按优先级）:
1. ❌ 所有Critical文本损坏（C1-C4: P55/P61/P63/P91）
2. ❌ 所有中文标点替换为英文标点（M1: P55/P58/P73）
3. ❌ 参考文献全部重新格式化为NAR格式（M5: 40篇）
4. ❌ P56缺失空格 `danalysis` → `d analysis`（M2）
5. ⚠️ 标题/URL命名统一（M4）
6. ⚠️ Methods P20冗余合并（M3）
7. ⚠️ 完成Graphical Abstract实际制作（m5）
8. ⚠️ Cover Letter添加推荐审稿人（m3）
9. ⚠️ 分设Data/Code availability（m4）

### 备选方案1: Genome Biology (IF ~12.3)

若NAR拒稿，Genome Biology是最佳备选：
1. 单细胞方法学核心期刊，读者群精准
2. 开放获取，影响力强
3. 参考文献格式要求较NAR宽松
4. 审稿速度较快（通常6-8周首审）
5. 对方法创新性的评估更侧重实用价值而非理论严谨性

### 备选方案2: Cell Systems (IF ~9)

适合CKI的"系统生物学框架"定位：
1. Cell Press品牌效应
2. 偏好概念性框架和方法论创新
3. 对Ka/Ks类比的跨学科思路较为开放
4. 但审稿可能要求更强的机制建模或实验验证

---

## 七、投稿准备度评估

### 当前准备度: 55% — 未达到投稿标准

**阻断因素**:
1. 4处Critical文本损坏（P55/P61/P63/P91）使核心段落无法阅读
2. 3处中文标点在英文正文中不可接受
3. 40篇参考文献格式完全不合规
4. Graphical Abstract仅为占位符

**已达标项**:
- ✅ Fig5 legend乱码已修复（v10→v11关键修复）
- ✅ 摘要格式和字数合规
- ✅ 章节结构合规
- ✅ Track Changes残留为0
- ✅ Cover Letter基本要素齐全（ORCID、AI声明、代码链接）
- ✅ 数据/代码可用性声明存在（需分设）
- ✅ 资金、利益冲突、作者贡献声明齐全

### 修复优先级建议

**P0 — 投稿阻断（必须修复）**:
1. 修复4处Critical文本损坏（C1-C4）
2. 替换3处中文标点（M1）
3. 修复P56缺失空格（M2）
4. 参考文献全部重排为NAR格式（M5）
5. 完成Graphical Abstract制作（m5）

**P1 — 强烈建议修复**:
6. 统一"Cell-state"/"Cell-type"命名（M4）
7. 合并Methods P20冗余（M3）
8. Cover Letter添加推荐审稿人（m3）
9. 分设Data/Code availability（m4）

**P2 — 建议改进**:
10. P53 AUC论述去重（m1）
11. P55 bulk RNA-seq局限性论述精简（m2）

### 整体评估

CKI稿件在概念创新性（Ka/Ks类比）和验证广度（4数据集/3系统/百万细胞）方面有亮点，适合NAR投稿。v11版本成功修复了v10最严重的Fig5 legend乱码问题，但其他写作质量问题（4处文本损坏、3处中文标点、参考文献格式）均未修复，且这些问题在NAR投稿中属于阻断项。

**结论**: 稿件当前状态**未达到NAR投稿标准**。预计需要1-2天的文本修复工作（主要是参考文献重排和文本损坏修复）即可达到投稿标准。建议修复上述P0和P1问题后投稿NAR，若拒稿转投Genome Biology。
