# Genome Biology 盲审报告（Editorial / 期刊适配与编辑合规视角）

- **评审对象**: CKI Submission Package v44（`version3/CKI_Submission_v44/`）
- **稿件标题**: CKI: a Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics
- **评审人角色**: Genome Biology Methodology 资深编辑/审稿人（期刊适配、结构与写作规范、合规声明）
- **评审日期**: 2026-09-05
- **评审依据**: CKI_Manuscript / Supplementary / Reproducibility Guide / Cover Letter / Table1-2 / MANIFEST_v44 纯文本提取件；figure PDF 未能在本环境渲染，图表评估以图注完整性、编号体系与清单校验为准。

---

## 总分与判定

**总分：7.5 / 10**
**判定：Minor Revision**

期刊适配度高、合规框架完整，无 P0；问题集中在代码存档 DOI 合规细节与正文篇幅/文字质量，均可机械性修复，不需要重审科学内容。

---

## 期刊适配评估（摘要）

Genome Biology Methodology 定位清晰：开源工具（cki v0.4.7, MIT）、ground-truth simulation + 四数据集验证、完整可复现管线，符合 GB 对方法学文章"方法+验证+可用性"的三要素传统。结构完全遵循 GB 规范：结构式摘要（Background/Results/Conclusions）→ Background → Results → Discussion → Conclusions → Methods → List of abbreviations → Declarations → Additional files → Figure legends → Vancouver 编号参考文献（55 条，[n] 方括号引用，按首现排序）。LLM 使用声明置于 Methods（"Use of large language models"），符合 GB/施普林格政策；Declarations 区块完整（Ethics / Consent / Availability / Competing interests / Funding / Authors' contributions / Acknowledgements）。封面信质量高：利益冲突声明、未一稿多投声明、AI 使用披露、NSFC 基金号、6 位无冲突推荐审稿人俱全，且与正文的克制表述（6.10-fold 梯度为 k_n 分母效应、无 FDR 存活候选）一致，没有夸大。

## 主要问题

### P1-1：Zenodo 存档与所报告代码版本不一致，版本 DOI 推迟到"接收后"（Availability 合规）
Declarations（"Availability of data and materials"）写道："A permanent archival copy has been deposited at Zenodo (concept DOI: 10.5281/zenodo.20405458; **an archived release DOI for v0.4.7 will be assigned upon acceptance**)"。MANIFEST 显示 concept DOI 于 v0.4.4 时期铸造，而本文全部分析（包括 v44 的 TCGA 线性归一化重跑、k_n 类大小混杂控制、50-replicate 校准）对应包版本 v0.4.7。GB 要求存档副本与稿件所报告版本一致并在投稿/接收时可核验；"接收后分配"意味着当前存档不含 v0.4.7 代码。处理简单：立即将 v0.4.7 推送至 Zenodo、把版本 DOI 写入声明（concept DOI 可保留）。此条不修不能接收。

### P1-2：正文严重超长、段落密度过高，Results 需实质性压缩（可读性/篇幅）
正文主体（Background 至 References 前）约 **21,500 词**：Results ≈ 9,000 词、Discussion ≈ 4,700 词、Methods ≈ 4,500 词。GB 虽无硬性字数上限，但多个段落为 400–600 词的单句群段落（如校准段 Results 第 3 小节，单段内并列 7.70 小鼠基线、9.73 脑内基线、ω_cal 换算的七组数值；Tabula Sapiens 反转段；脑梯度段），读者需在单段内追踪十余个数字。脑梯度稳健性一段内塞入 First/Second/Third/Fourth 四项分析。建议：将部分稳健性/敏感性细节下沉至 Additional file 1（文中已具备完备的注释体系），Results 压缩至 ~6,000 词以内；校准叙述重排为"报告基线 → 数据集内基线 → 可迁移性结论"三步。此问题不影响科学性，但按 GB 编辑标准需要作者做一次认真的文字精简。

### P2-1：标题页仅列通讯作者一个 ORCID
第 7 行仅 "ORCID: Li Zhang 0000-0002-0698-0754"。GB 强制要求通讯作者 ORCID（已满足），但鼓励全体作者提供；第一作者 Xianming Wu 缺 ORCID。提交系统中补齐即可。

### P2-2：重复与错标文字（copyediting 级）
- "legacy six-split estimate (6.67) is consistent … hepatocyte control … split-level SD ≈ 6.0" 同一解释句在 Results 相邻两段（校准小节两段）几乎逐字重复，Discussion 首段第三次出现。保留一处即可。
- "Two analyses probe the robustness of the gradient. First… Second…" 之后紧接的段落却继续 "Third… Fourth…"——引言句与实际四项分析不符。
- 摘要含小节标签共 252 词，贴着 GB ≤250 词上限，建议顺手删 3–5 词留出余量。

### P2-3：Additional files 声明与投稿包内容不一致
正文 "Additional files" 声明 Additional file 1 和 2 "Format: DOCX (**a PDF rendering is also provided**)"，但 v44 包内只有 DOCX（MANIFEST 亦只列 DOCX 校验和），无任何 PDF 渲染件。要么补交 PDF，要么删去括注。另：MANIFEST 注明纯文本提取件"excluded from this package"却与 DOCX 同目录存放——若该目录即投稿包，应在打包时排除提取件，避免编辑端混淆。

### P2-4：图表交付方式的编辑部核验提示
图表编号体系完整一致（Fig. 1–6、Fig. S1–S14、Table 1–2、Table S1–S4，正文与 Additional file 1 交叉引用齐全，图注普遍写出 n、统计量与阴性限定语，质量高于均值）。但本评审环境无法渲染 PDF 做逐图目检，且 MANIFEST 中 Supplementary_Figure_S11.pdf 达 771 KB（其余均 <150 KB），建议作者确认 S11 矢量图未意外栅格化/嵌图过大，并核对所有 figure PDF 字体已嵌入。

## 优点

1. **合规框架教科书级完整**：GB 结构、Declarations、Additional files 申报、CELLxGENE collection ID、GEO 号、GitHub tag、Dockerfile、种子例外披露、AI 使用双处声明（Methods + 封面信）一应俱全；MANIFEST 的逐版本变更记录与校验和体现了罕见的投稿工程严谨度。
2. **Limitations 诚实且具体到数值**：锚点可见性边界（500 基因位移时 ω AUC 崩至 0.05–0.13）、donor-paired 功效窗口（50–200 cells）、类大小混杂致 6.10→1.74 梯度衰减、scDist 仅为 Python 近似等均直书不讳，且与 Results/封面信口径一致——这是编辑最看重、也最难得的品质。
3. **封面信与正文自洽**：不夸大（明确"no per-pair candidate survives FDR"）、推荐审稿人多元且声明无冲突、主动交代敏感点（灵敏度边界以同等篇幅呈现），显著降低了编辑初审成本。

## 处理建议汇总

| # | 级别 | 事项 | 性质 |
|---|------|------|------|
| P1-1 | P1 | v0.4.7 立即归档 Zenodo 并写入版本 DOI | 合规（接收前置条件） |
| P1-2 | P1 | Results/Discussion 压缩与校准叙述重排 | 文字编辑 |
| P2-1 | P2 | 补第一作者 ORCID | 元数据 |
| P2-2 | P2 | 删除重复句、修正 "Two analyses" 枚举、摘要减词 | 文字编辑 |
| P2-3 | P2 | Additional files PDF 声明与实物对齐；排除提取件 | 打包 |
| P2-4 | P2 | S11 体积核查、字体嵌入确认 | 图表质检 |

P0：0 项；P1：2 项；P2：4 项。两项 P1 均可在一次小修内完成，故判定 **Minor Revision**。
