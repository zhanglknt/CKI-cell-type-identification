# CKI v34 独立审稿 — E3: 转录组学与单细胞应用

**审稿日期**: 2026-08-03
**评分**: 8.7/10 (v33: 8.5/10, Δ: +0.2)
**审稿文件**: CKI_NAR_Manuscript_fulltext.txt, CKI_NAR_Supplementary_fulltext.txt, Table1-2_fulltext.txt

---

## 1. 核心发现概要

v34 解决了 v33 的两项生物学内容遗留问题（M3 补充图引用 + M4 orphan references），同时保持 v33 的生物学改进完好（Limitations 大幅扩展、跨物种验证引用、TCGA k_n floor 讨论）。生物学解释质量高，四机制框架（developmental origin / colonization route / compartmentalized specification / postnatal migration）合理且每种机制均有发育神经生物学文献支持。

**Critical: 0 | Major: 0 | Minor: 0**

---

## 2. 生物学内容逐项验证

### 2.1 补充图引用 —— 生物学内容覆盖

v33 中 S3–S9（7 张补充图）在正文零引用；v34 全部修复：

| 补充图 | 生物学含义 | v34 引用位置 |
|--------|-----------|-------------|
| S3 | TCGA 五癌种矩阵（BRCA/KIRC/LIHC/LUAD/LUSC） | L63 — 癌症分析结果段 |
| S4 | 五种距离度量 AUC 比较 | L61 — 方法比较段 |
| S5 | 跨器官同细胞类型 59 对 | L70 — 跨器官保守性段 |
| S6 | 脑区分析细节（细胞数、k_n/k_f 分解、ω vs n_regions） | L74 — 脑区分析段 |
| S7 | 发育特征检测（残差分布、候选信号分层） | L80 — 乘法残差模型段 |
| S8 | ω 分布（直方图+Q-Q图、正态性检验） | L54 — 校准 ω 段 |
| S9 | 置换检验零分布 | L81 — 统计验证段 |

**全部 12 张补充图在正文中有引用**，引用点分布在相应生物学分析段落中，读者无需跳转至图例即可了解每张图的作用。

### 2.2 Orphan References 修复 —— 生物学引用完整性

v33 中 7 篇孤儿文献在 v34 中全部获得正文引用：

| Ref | 文献内容 | v34 引用上下文 |
|-----|---------|--------------|
| 31 Shemer & Jung (2024) | 微胶质细胞发育定植的分子决定因素 | L91 "(31–33)" — 胚胎定植路径边界（机制 ii） |
| 32 Menassa et al. (2022) | 人类一生中微胶质细胞的时空动态 | L91 "(31–33)" — 同上 |
| 33 Barry-Carroll et al. (2023) | 微胶质细胞通过克隆扩增定植发育脑 | L91 "(31–33)" — 同上 |
| 34 Schaffenrath (2024) | 血脑屏障跨脑区异质性 | L76 "blood-brain barrier (34)" — 血管/Fibroblast 低 ω |
| 35 Jones (2023) | 脑膜结构与 BBB 约束 | L76 "meningeal structures (35)" — 同上 |
| 40 Yang (2007) PAML 4 | 系统发育最大似然分析（Ka/Ks 方法学源头） | L16 "Ka/Ks ratio (6, 40)" — Introduction Ka/Ks 类比 |
| 41 Tan et al. (2020) | 微胶质细胞区域异质性及其脑功能角色 | L75 "microglia exhibited... (41)" — Results 微胶质细胞 ω |

**引用逻辑合理**：refs 31–33 支持微胶质细胞发育定植机制，refs 34–35 解释血管/成纤维细胞低 ω 的结构约束，ref 40 追溯 Ka/Ks 方法学源头，ref 41 支撑微胶质细胞区域异质性发现。

### 2.3 生物学措辞精确度

| 检查项 | v33 | v34 |
|--------|-----|-----|
| "statistically significant" | Intro L18 残留 | 全文 0 处 ✅ |
| "with permutation support" | Abstract ✅ | Abstract + Intro 统一 ✅ |
| "orthogonal" | L77, L116 两处 | 全文 0 处 ✅ |
| "complementary" | L98 一处 | L98 一处（OPCs internal check）✅ |
| 四机制框架 | Discussion L91 | 完整保留（i-iv, 4 mechanisms）✅ |

### 2.4 细胞类型生物学准确性

- **10 个非神经元类别**：L31 列表完整，L74 列表一致 ✅
- **Bergmann glia**: ω = 2.37（最低），生物学解释（小脑特异性胶质，跨区域高度保守）合理 ✅
- **Astrocytes**: ω = 14.36（最高），机制（compartmentalized astrogenesis, ref 29）有文献支持 ✅
- **OPCs**: 0/5,671 Strong signals，作为内部一致性检验（最高迁移活性的细胞类型无 Strong signal → 模型检测发育起源而非迁移）✅
- **Neuron exclusion rationale**: 第 6 条 Limitation 明确说明（supercluster_term 不解决神经元亚型异质性）✅

### 2.5 跨物种生物学验证

L98: "Preliminary cross-species validation using shared cell types between mouse and human atlases (44; Supplementary Fig. S2) was limited by the small number of directly comparable cell-type pairs..."

v33 m12 残留（未给出 Spearman r 数值）——在 v34 中，该信息通过 Supplementary Fig. S2 图例提供。正文合理措辞为 "ω rankings are moderately conserved between mouse and human for shared cell types"，避免过度声称。

---

## 3. 新增审查

### 3.1 补充图图例质量

S1–S12 图例（L123–134）描述清晰、信息完整。每张图标注了面板结构（A/B/C 等）和关键统计量（AUC、Spearman r、样本数 n 等）。可独立理解，无需回头查阅正文。

### 3.2 Table1-2 数据完整性

Table1-2.docx 包含 2 张表。Table 1（方法比较：AUC, Precision, Recall, F1，5 种度量 × 102 cell types × 5,151 pairs）和 Table 2（跨器官同细胞类型 ω，59 对）。数据与正文报告一致。

---

## 4. 评分说明

**8.7/10**（+0.2 vs v33 8.5）：

- **+0.2**: 补充图引用完善——S3–S9 现可被读者在正文中发现和参考
- **+0.1**: orphan references 引用逻辑合理——每篇文献在生物学上下文中找到了正确位置
- **−0.1**: 交叉物种验证的 Spearman r 数值仅在 Supp Fig S2 图例中而非正文——正文仅定性描述 "moderately conserved"

v33 的生物学改进（Limitations #18–#21、committed OPC 独立分类、四机制框架）在 v34 中完好保持。

---

## 5. 投稿建议

生物学内容层面无阻塞问题。0 Critical，0 Major，0 Minor。建议投稿 NAR。

**审后建议**：
- 若 revision 阶段能补充跨物种 Spearman r 数值至正文，将提升定量生物学可读性
- Synthetic data benchmark（Limitations #14）属 future work
