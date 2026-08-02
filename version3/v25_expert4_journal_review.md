# E4 期刊策略与稿件质量审稿报告 — v25

**审稿专家**: E4（稿件质量与期刊策略）
**审稿日期**: 2026-08-01
**审稿对象**: CKI_NAR_Submission_v25（25 文件）
**对比基准**: v22（E4 评分 8.0/10，C6+C7 未解决）
**v25 关键变化**: v23 修复 C6（标题措辞）+C7（NAR 格式）；v24 修复 C4（HK 约束基线）、C5（OPC 一致性）；v25 修复 20 个 Major Issues

---

## 1. 执行摘要

**v25 E4 评分：8.3/10**（v22: 8.0/10, +0.3）

v25 是一个显著改善的版本。C7（NAR 格式补全）已完全修复——Keywords、Running Title、ORCID、OS 字段均已到位。C6（标题"Selective"措辞）在主稿件标题层面已修复，但在 Supplementary 标题、Cover Letter 正文和 Figure 图例中仍残留"selective"措辞，存在不一致。20 个 Major Issues 中的大部分已得到有效处理（Discussion 压缩、参考文献对齐、术语统一等）。

然而，审稿中发现若干新问题：（1）Supplementary 标题仍使用旧标题"Selective Transcriptomic Remodeling"；（2）Table 1 在独立文件与正文中数值不一致（99/4,851 vs 102/5,151）；（3）参考文献编号未按首次引用顺序排列；（4）Python 版本要求在文件间不一致；（5）仅通讯作者提供 ORCID，NAR 要求所有作者提供。

**准备度评估**: ~78%（v22: ~67%, +11%）。修复下述剩余问题后预计 85-88%。

---

## 2. C6+C7 修复验证

### C6：标题"Selective"措辞 — 部分修复 ⚠️

| 位置 | v22 状态 | v25 状态 | 详情 |
|------|----------|----------|------|
| 主稿件标题 (P0) | ❌ "Selective" | ✅ "Baseline-Normalized" | 已修复 |
| Cover Letter 标题 (P13) | ❌ "Selective" | ✅ "Baseline-Normalized" | 已修复 |
| **Supplementary 标题 (P1)** | ❌ "Selective" | ❌ **仍为 "Selective"** | **未修复** |
| Cover Letter 正文 (P16) | "selective" | ❌ **仍为 "selective"** | "a robust, interpretable measure of selective transcriptomic remodeling" |
| Figure 1 图例 (P119) | "selective" | ❌ **仍为 "selective"** | "ω = k_f/k_n > 1 indicates selective transcriptomic remodeling" |
| Supplementary Note 1.4 (P23) | "selective" | ❌ **仍为 "selective"** | "selective reprogramming" + "selective transcriptional reprogramming" |

**评估**: C6 的核心修复（主稿件标题）已正确完成，"Baseline-Normalized"准确反映了方法本质，避免了"selective"暗示达尔文选择的歧义。但修复不彻底——Supplementary 标题直接沿用旧标题，Cover Letter 正文和 Figure 图例中仍使用"selective transcriptomic remodeling"短语。这些不一致会被编辑和审稿人注意到，尤其是 Supplementary 与主稿件的标题矛盾。

**修复建议**:
1. 将 Supplementary P1 标题改为"Baseline-Normalized Transcriptomic Remodeling"
2. Cover Letter P16 "selective transcriptomic remodeling" → "baseline-normalized transcriptomic remodeling"
3. Figure 1 图例 P119 "selective transcriptomic remodeling" → "baseline-normalized transcriptomic remodeling"
4. Supplementary Note 1.4 中"selective reprogramming" → "baseline-normalized reprogramming"

注：正文中"selectively diverged"(P85)和"selectively constrained"(P87)等用法是描述生物学现象的常规科学用语，不需要修改。

### C7：NAR 格式补全 — 完全修复 ✅

| 检查项 | v22 状态 | v25 状态 | 详情 |
|--------|----------|----------|------|
| Keywords | ❌ 缺失 | ✅ 已补全 | P11: "cell-state divergence, housekeeping genes, Jensen-Shannon decomposition, transcriptomic remodeling, single-cell genomics"（5 个，NAR 要求 3-8 个） |
| Running Title | ❌ 缺失 | ✅ 已补全 | P1: "CKI: Baseline-Normalized Divergence Index"（42 字符，NAR 限制 50 字符） |
| ORCID | ❌ 缺失 | ✅ 已补全（通讯作者） | P6: "ORCID: 0000-0002-0698-0754"（Li Zhang） |
| Operating System | ❌ 缺失 | ✅ 已补全 | P107: "runs on Linux, macOS, and Windows"；Cover Letter P18 同述 |

**评估**: C7 的四项核心要求均已满足，消除了 v22 时"可能被 desk reject"的风险。但存在一个遗留问题：NAR 投稿政策要求**所有作者**提供 ORCID，当前仅通讯作者 Li Zhang 有 ORCID，第一作者 Xianming Wu 的 ORCID 缺失（见 §5 新问题 N1）。

---

## 3. NAR 投稿合规检查清单

### 3.1 必需项检查

| # | 检查项 | 状态 | 备注 |
|---|--------|------|------|
| 1 | 标题（简洁、信息量大） | ✅ | "CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling" |
| 2 | Running Title（≤50 字符） | ✅ | "CKI: Baseline-Normalized Divergence Index"（42 字符） |
| 3 | 作者姓名与单位 | ✅ | Xianming Wu¹, Li Zhang¹²*；两个单位标注清楚 |
| 4 | 通讯作者邮箱 | ✅ | knightz@pumc.edu.cn |
| 5 | ORCID（所有作者） | ⚠️ | 仅 Li Zhang 有 ORCID；Xianming Wu 缺失（N1） |
| 6 | Keywords（3-8 个） | ✅ | 5 个关键词，选择合理 |
| 7 | Abstract（≤250 词） | ✅ | ~250 词，结构完整（背景→方法→结果→结论） |
| 8 | Graphical Abstract | ✅ | 文件提供（PNG/PDF/SVG），正文标注"will be provided separately" |
| 9 | Introduction | ✅ | 逻辑清晰，Ka/Ks 类比引入 |
| 10 | Materials and Methods | ✅ | 完整，含 CKI 计算、统计检验、数据集描述 |
| 11 | Results | ✅ | 四个数据集逐一呈现，结构清晰 |
| 12 | Discussion | ✅ | 已压缩，包含 15 条 Limitations |
| 13 | Data Availability | ✅ | GEO、CELLxGENE、GDC、Zenodo DOI 均提供 |
| 14 | Supplementary Data | ✅ | Supplementary Notes 1-4, Tables 1-4, Data 1 |
| 15 | Acknowledgements | ✅ | 致谢数据提供方 |
| 16 | Author Contributions | ✅ | X.W. 和 L.Z. 贡献明确 |
| 17 | Funding | ✅ | NSFC 32370682 + 国家科技重大专项 2026ZD01910500 |
| 18 | Conflict of Interest | ✅ | "The authors declare no competing interests" |
| 19 | References（NAR 格式） | ⚠️ | 格式正确（作者, 年, 期刊, 卷, 页），但编号顺序有误（N3） |
| 20 | Figure Legends | ✅ | 6 个主图 + 12 个补充图图例完整 |
| 21 | Statistical Conventions | ✅ | P138 统一统计约定段落 |
| 22 | Code Availability | ✅ | GitHub + Zenodo DOI (10.5281/zenodo.15670808), MIT License |

### 3.2 格式合规

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 正文英文 | ✅ | 全英文 |
| 参考文献格式 | ✅ | NAR 风格：作者. (年) 标题. *期刊*, **卷**, 页码 |
| 基因/蛋白质命名 | ✅ | GAPDH、HK、HVG 等格式正确 |
| 统计报告 | ✅ | P 值、效应量、CI 均有报告 |
| 图表引用 | ✅ | 正文引用 Fig. 1-6, Table 1-2, Supplementary Figs S1-S12 |

### 3.3 合规总结

**22/22 必需项中：19 项完全合格，3 项有遗留问题（ORCID、参考文献顺序、Supplementary 标题一致性）。**

v22 时的 desk reject 风险（C7）已消除。当前剩余问题不会导致 desk reject，但会在编辑初审阶段被要求修正。

---

## 4. Cover Letter 审查

### 4.1 六项检查

| # | 检查项 | 状态 | 详情 |
|---|--------|------|------|
| 1 | 推荐审稿人 | ✅ | 6 位审稿人，涵盖相关领域（Theis, Teichmann, Welch, Yanai, Z. Zhang, X. Wang），附邮箱和单位 |
| 2 | 利益冲突声明 | ✅ | "None of the suggested reviewers have recent collaborations or conflicts of interest" |
| 3 | AI 使用声明 | ✅ | "AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors, who take full responsibility" |
| 4 | ORCID | ✅ | 通讯作者 ORCID 提供 |
| 5 | 独创性声明 | ✅ | "This work has not been published elsewhere, is not under consideration by any other journal" |
| 6 | 代码/数据可用性 | ✅ | GitHub + Zenodo DOI + MIT License + OS 兼容性 |

### 4.2 Cover Letter 内容审查

**优点**:
- 结构规范：称呼→投稿声明→科学摘要→作者声明→审稿人建议→结语
- 科学摘要精炼，突出三个维度（独立信息维度、跨数据集一致性、生物学应用）
- Phase D 修复有效：无"orthogonal"过度声明，使用"empirical baseline"而非"confirmed baseline behavior"
- 推荐审稿人选择合理，领域覆盖充分

**问题**:

| ID | 严重度 | 位置 | 问题 | 建议 |
|----|--------|------|------|------|
| CL1 | Minor | P16 | "selective transcriptomic remodeling"与主稿件标题"Baseline-Normalized"不一致 | 改为"baseline-normalized transcriptomic remodeling" |
| CL2 | Minor | P18 | "Python (≥3.9)"与主稿件"Python 3.8+"不一致 | 统一为"Python 3.9+"或"Python 3.8+" |
| CL3 | Trivial | P17 | "CKI ω captures information that standard metrics miss" — "miss"略显主观 | 可改为"that standard metrics do not capture" |
| CL4 | Trivial | — | 未明确声明无需伦理审批（虽然为纯计算研究，但部分期刊要求显式声明） | 可添加"This study used only publicly available de-identified data; no human subjects or animal experiments were conducted" |

---

## 5. 语言质量检查

### 5.1 不当措辞检查

| 术语 | 出现次数 | 位置 | 评估 |
|------|----------|------|------|
| "striking" | 0 | — | ✅ 未出现（v22 关注点已消除） |
| "selective transcriptomic remodeling" | 4 | Cover Letter P16, Figure 1 图例 P119, Supplementary P1/P23 | ⚠️ 与标题修改不一致 |
| "orthogonal" | 4 | Manuscript P77, P83, P102, Repro Guide（仅描述修复记录） | ⚠️ 正文仍使用，但语境合理（见下） |
| "paradoxically" | 1 | Manuscript P17（Introduction） | ⚠️ 主观措辞，可改为"notably"或直接陈述 |
| "confirmed" | 0 | — | ✅ Cover Letter 中已消除 |
| "robust" | 1 | Cover Letter P16: "a robust, interpretable measure" | ⚠️ 略显自夸，但可接受 |

### 5.2 "orthogonal"使用评估

正文中 4 处"orthogonal"的使用语境：
- P77: "providing an orthogonal transcriptomic readout of migration history" — 描述方法互补性
- P83: "provides a useful orthogonal validation of the multiplicative residual model" — 描述 OPC 验证
- P102: "providing a notable orthogonal validation" — 同上

**评估**: "orthogonal"在计算生物学中广泛使用，意为"互补的/独立的"。Cover Letter 中已移除（Phase D M-W1 修复），正文中保留是可接受的，因为这些用法描述的是具体验证逻辑而非整体方法定位。但建议将 P102 的"notable orthogonal validation"改为"independent validation"以进一步降低措辞强度。

### 5.3 流畅度与可读性

**优点**:
- Introduction 逻辑递进清晰：问题→类比→方法→验证路线
- Methods 结构完整，参数报告详尽
- Results 各节有明确小标题，数据呈现系统
- Discussion 的 15 条 Limitations 展示了充分的自我批判
- 统计约定段落（P138）统一了全文的统计报告标准

**问题**:
- Discussion 的 Limitations 段落（P103）过长（~600 词），15 条限制堆砌在一个段落中，可读性差。建议分组：方法限制→数据限制→统计限制
- P103 中"Seventh"到"Fifteenth"的编号列表在连续段落中呈现，缺乏视觉分隔
- 部分句子过长，如 P34（Methods 中 residual model 描述）约 200 词，建议拆分

### 5.4 术语一致性

| 术语 | 一致性 | 备注 |
|------|--------|------|
| "standardized effect size (SES)" | ✅ | v25 统一替换了"Cohen's d"（M5 修复） |
| "empirical baseline" | ✅ | 替换了"confirmed baseline behavior"（M-W2 修复） |
| "developmental signatures" | ✅ | Cover Letter 中已替换"developmental origin signatures"（M-W3 修复） |
| "constrained baseline" | ✅ | C4 修复，HK 基因描述为"constrained"而非"neutral" |
| "selective transcriptomic remodeling" | ⚠️ | 部分文件已改"baseline-normalized"，部分仍保留"selective" |
| Python 版本 | ⚠️ | "3.8+"（正文）vs "≥3.9"（Cover Letter）vs "3.13.12"（Repro Guide 分析环境） |

---

## 6. 新发现问题

### N1：Supplementary 标题与主稿件不一致 [Minor-Critical]

**位置**: Supplementary DOCX P1
**问题**: Supplementary 标题为"CKI: A Cell-state Kinetic Index for Quantifying **Selective** Transcriptomic Remodeling"，而主稿件标题已改为"**Baseline-Normalized** Transcriptomic Remodeling"。
**影响**: 投稿包内标题矛盾，编辑初审时会立即发现。
**修复**: 将 Supplementary P1 标题改为与主稿件一致。

### N2：Table 1 数值不一致 [Minor-Critical]

**位置**: Table1-2.docx vs Manuscript P59
**问题**:
- Table1-2.docx P2: "Table 1. Classification AUC of five metrics on Tabula Sapiens (**99** cell types, **4,851** pairs)."
- Manuscript P59: "Table 1. Classification AUC of five metrics on Tabula Sapiens (**102** cell types, **5,151** pairs)."

**影响**: 同一表格在不同文件中描述不同的样本量，将引起审稿人质疑数据准确性。
**修复**: 核实实际使用的细胞类型数和配对数，统一两个文件。正文中多处引用 5,151 对（P27, P57, P58, P70），因此 102/5,151 很可能是正确值，Table1-2.docx 需更新。

### N3：参考文献编号未按首次引用顺序排列 [Minor]

**位置**: Manuscript 全文引用 vs References 列表
**问题**: NAR 要求参考文献按首次引用顺序编号。当前首次引用顺序为：16, 1, 2, 3, 32, 31, 5, 6, 7, 8, 9, 30, 4, 25, 26, 27... 第一条引用是 (16) 而非 (1)。
**影响**: 不符合 NAR 参考文献格式要求，编辑可能要求重新编号。
**修复**: 按首次引用顺序重新编号所有参考文献（41 条），同步更新正文引用和参考列表。
**注**: MANIFEST_v25.txt 声称 M19"Reference numbering alignment"已修复，但实际验证表明编号仍未按首次引用顺序排列。可能是"对齐"指的是引用号与列表号的匹配，而非顺序重排。

### N4：Python 版本要求不一致 [Trivial]

**位置**: Manuscript P107 vs Cover Letter P18 vs Repro Guide P39
**问题**:
- Manuscript P107: "Python 3.8+"
- Cover Letter P18: "Python (≥3.9)"
- Repro Guide P39: "Python 3.13.12"（分析环境）
**修复**: 统一最低版本要求。如果包实际需要 3.9+，则统一为"Python 3.9+"；Repro Guide 中可保留具体分析版本"3.13.12"。

### N5：第一作者 ORCID 缺失 [Minor]

**位置**: Manuscript P2-P6
**问题**: 仅通讯作者 Li Zhang 提供 ORCID (0000-0002-0698-0754)，第一作者 Xianming Wu 无 ORCID。NAR 投稿系统要求所有作者提供 ORCID。
**修复**: 为 Xianming Wu 注册 ORCID 并添加到作者信息中。

### N6：Cover Letter 正文"selective"与标题不一致 [Minor]

**位置**: Cover Letter P16
**问题**: Cover Letter 标题（P13）已改为"Baseline-Normalized"，但正文 P16 仍使用"selective transcriptomic remodeling"。
**修复**: 改为"baseline-normalized transcriptomic remodeling"。

### N7：Figure 1 图例"selective"与标题不一致 [Minor]

**位置**: Manuscript P119 (Figure 1 图例)
**问题**: "ω = k_f/k_n > 1 indicates selective transcriptomic remodeling" 与主稿件标题修改不一致。
**修复**: 改为"indicates baseline-normalized transcriptomic remodeling"。

### N8：Discussion Limitations 段落可读性 [Trivial]

**位置**: Manuscript P103
**问题**: 15 条限制性陈述在一个连续段落中呈现（"First"到"Fifteenth"），约 600 词，可读性差。
**修复**: 建议分组为 3 小段（方法限制 / 数据限制 / 统计限制），或使用编号列表格式。

---

## 7. v20 Major Issues 修复验证（E4 负责）

| ID | 描述 | v25 状态 | 验证 |
|----|------|----------|------|
| M17 | Discussion 重复 | ✅ 已修复 | Discussion 已压缩，核心论点清晰，避免了与 Results 的重复 |
| M19 | 参考文献顺序 | ⚠️ 部分修复 | 引用号与参考列表匹配，但未按首次引用顺序排列（见 N3） |

---

## 8. 期刊推荐更新

| 排名 | 期刊 | IF (估) | fit | 接受概率 | v22 → v25 变化 |
|------|------|---------|-----|----------|----------------|
| 1 | **NAR** | ~16.6 | 8.5/10 | 35-45% | ↑ 30-40% → 35-45%（C7 修复消除 desk reject 风险） |
| 2 | **Bioinformatics** | ~5.8 | 8.5/10 | 40-50% | 持平（一直是强备选） |
| 3 | **Cell Reports Methods** | ~3.0 | 8.0/10 | 35-40% | 持平 |
| 4 | **PLOS Computational Biology** | ~3.5 | 7.5/10 | 35-45% | 持平 |

**NAR 接受概率提升依据**:
1. C7 完全修复：格式合规，消除 desk reject 风险（+5-10%）
2. C6 主标题修复：标题措辞更准确（+2-3%）
3. 20 个 Major Issues 大部分修复：Discussion 质量、术语一致性、统计谨慎性显著提升（+3-5%）
4. Phase B/C/D 统计和方法加固：BH-FDR 描述、EVT 外推、校准 omega 等增强了方法学严谨性

**限制因素**:
- Supplementary 标题不一致等格式问题可能延迟初审（-2-3%）
- 参考文献顺序问题可能被编辑要求修正（-1-2%）
- 核心科学问题（C1 BH-FDR、C3 Mouse k_n 方案、C4 HK 假设）的修复质量取决于 E1/E2/E3 评估

---

## 9. 评分与总结

### 9.1 评分明细

| 维度 | v22 | v25 | Δ | 说明 |
|------|-----|-----|---|------|
| C6 修复（标题措辞） | 0/10 | 7/10 | +7 | 主标题修复✓，Supplementary/Cover Letter/Figure 图例未同步✗ |
| C7 修复（NAR 格式） | 0/10 | 9/10 | +9 | 四项核心要求均满足，仅 ORCID 缺第一作者 |
| Major Issues 修复 | 6/10 | 8/10 | +2 | M17 Discussion 压缩✓，M19 参考文献顺序⚠️ |
| Cover Letter 质量 | 7/10 | 8/10 | +1 | 六项检查均通过，"selective"残留扣分 |
| 语言质量 | 7/10 | 8/10 | +1 | "striking"已消除，"paradoxically"可接受 |
| NAR 合规完整性 | 7/10 | 8/10 | +1 | 19/22 完全合格 |
| 新问题 | — | -1 | — | Table 1 数值不一致、Supplementary 标题矛盾 |

### 9.2 综合评分

**v25 E4 评分：8.3/10**（v22: 8.0/10, +0.3）

### 9.3 评分理由

**加分项**:
- C7 完全修复（+0.5）：消除 desk reject 风险，这是 v22 时最大的期刊策略风险
- C6 主标题修复（+0.2）：方向正确，措辞准确
- 20 个 Major Issues 大部分修复（+0.2）：Discussion 压缩、术语统一、统计谨慎性提升
- Phase B/C/D 加固（+0.1）：方法学严谨性显著提升

**减分项**:
- C6 修复不彻底（-0.3）：Supplementary 标题、Cover Letter 正文、Figure 图例仍使用"selective"
- Table 1 数值不一致（-0.2）：99/4,851 vs 102/5,151，明显疏漏
- 参考文献顺序未按首次引用排列（-0.1）：M19 声称修复但实际未完成
- Python 版本不一致（-0.05）：跨文件术语不一致
- 第一作者 ORCID 缺失（-0.05）：NAR 政策要求

### 9.4 投稿建议

**可以投稿 NAR 吗？** 可以。v25 已满足 NAR 的基本投稿要求，不存在 desk reject 级别的障碍。

**投稿前应修复（优先级排序）**:
1. **P0（30 分钟）**: 修复 Supplementary 标题为"Baseline-Normalized"（N1）
2. **P0（15 分钟）**: 统一 Table 1 数值（N2）——核实 102/5,151 vs 99/4,851
3. **P1（30 分钟）**: Cover Letter + Figure 图例中"selective" → "baseline-normalized"（N6, N7）
4. **P1（5 分钟）**: 统一 Python 版本要求（N4）
5. **P2（如时间允许）**: 按首次引用顺序重排参考文献（N3）
6. **P2（如时间允许）**: 为 Xianming Wu 添加 ORCID（N5）

修复 P0+P1 项后，v25 评分预计提升至 **8.6-8.8/10**，准备度达到 ~85%。

---

*审稿报告存档: version3/v25_expert4_journal_review.md*
