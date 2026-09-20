# Nature Communications 投稿格式规范清单（GB→NC 改造用）

- 调研日期：2026-09-17
- 主要出处（均访问于 2026-09-17）：
  - [A] NC 格式指南（接收后排版要求，2021-05-07 修订）: https://www.nature.com/documents/ncomms-formatting-instructions.pdf
  - [B] NC How to submit: https://www.nature.com/ncomms/submit/how-to-submit
  - [C] NC Brief submission guide (PDF): https://www.nature.com/documents/ncomms-submission-guide.pdf
  - [D] NC Article 类型页: https://www.nature.com/ncomms/submit/article
  - [E] Communications 期刊 life-sciences 接收后 style guide: https://www.nature.com/documents/commsj-life-style-formatting-guide-accept.pdf
  - [F] Nature Portfolio Reporting Summary: https://www.nature.com/documents/nr-reporting-summary-flat.pdf
- GB 现状列引自 nc-gap 审计（nc_gap_audit_2026-09-17.md）。
- **重要纠偏**：team-lead 任务书中"NC 惯例 Introduction 不加标题"**有误**——[A][E] 明确要求标题页后第一节以 "Introduction" 为标题（"Must begin with the heading 'Introduction'"）。Nature 主刊才不用该标题。

---

## 1. Article 结构与顺序

NC 官方章节顺序 [A]（"No other section headings are permitted"）：

```
Title → Authors → Abstract → Introduction → Results → Discussion (optional)
→ Methods (optional) → Data availability → Code availability (if applicable)
→ References → Acknowledgements (optional) → Author contributions → Competing interests
```

- Introduction：无小标题，≤~1000 词；末段以 "In this work"/"Here, we show" 开头概括结果与结论（现在时）[A][E]。
- Results：小标题 ≤60 字符（含空格）、不编号、**不允许二级小标题**（"Do not use secondary subheadings"）[A]。
- Discussion：可选；**不允许小标题**；与 Results 重叠最小化 [A][E]。
- Methods：置于 Discussion 之后（主文档内，不放补充材料），小标题 ≤60 字符，通常 <3000 词 [A][C][D]。

| 项 | GB 现状 | NC 要求 |
|---|---|---|
| 首节标题 | "Background" | "Introduction"（有标题） |
| Conclusions 节 | 有（L97） | 无此节，并入 Discussion 末 |
| Results 二级小标题 | 3 个 L3（Microglia 等） | 不允许，需降格/并入 |
| Discussion 小标题 | 3 个 L2 | 不允许，需去除 |

## 2. Abstract

- 非结构化单段；**≤150 词**（[A][C][E]；[D] 放宽表述为 ≤200 词，按 150 执行最稳）。
- 无引用、无缩写（尽量）；2-3 句背景 → "Here, we show"（或等效）→ 主要结果与结论（现在时）；无 graphical abstract [A][E]。

| GB 现状 | NC 要求 |
|---|---|
| 151 词，非结构化（已合规形式） | ≤150 词，删 1-3 词即可 |
| Keywords 行（5 词） | NC 不用关键词行，删除 |

## 3. 参考文献（Nature 风格）

- 正文引用：**上标阿拉伯数字**，按在正文→图例→表例中出现顺序编号；非方括号 [B]。
- 条数指南 ≤70 [A][C][D]；每条只含一个工作；可含已接受/预印本，不含 "submitted/under review" [A]。
- 条目格式 [A][B]：
  - 作者：姓在前，逗号，名缩写**带点带空格**；作者间逗号分隔、最后两位用 " & "。`Eigler, D. M. & Schweizer, E. K.`
  - **et al. 规则：作者 ≥6 位（six or more）时只列第 1 位 + "et al."；≤5 位全列** [B]。⚠️ nc-gap 审计所写 ">10 才截断" 与 NC 官网不符，以此为准。
  - 标题：罗马体、句首字母大写（sentence case）、以句点结尾。
  - 期刊名：**斜体**、通用缩写带点（`Nat. Commun.`）；卷号及其后逗号**加粗**；页码全区间（或文章号）；年份置于末尾括号内。
  - 期刊文章：`Eigler, D. M. & Schweizer, E. K. Positioning single atoms with a scanning tunnelling microscope. Nature 344, 524-526 (1990).`
  - 文章号：`Cheng, F., Kovács, I. A. & Barabási, A.-L. Network-based prediction of drug combinations. Nat. Commun. 10, 1197 (2019).`
  - 预印本：`Babichev, S. A., Ries, J. & Lvovsky, A. I. Quantum scissors: teleportation of single-mode optical states by means of a nonlocal single photon. Preprint at http://arXiv.org/abs/quant-ph/0208066 (2002).`
  - 数据集：`Hao, Z., AghaKouchak, A., Nakhjiri, N. & Farahmand, A. Global Integrated Drought Monitoring and Prediction System (GIDMaPS) data sets. figshare https://doi.org/10.6084/m9.figshare.853801 (2014).`
  - 书籍：`Jones, R. A. L. Soft Machines: Nanotechnology and Life Ch. 3 (Oxford Univ. Press, Oxford, 2004).`
  - 软件：按数据集格式引用（有 DOI 时），如 Zenodo：`作者. 标题. Zenodo https://doi.org/... (年份).`

| GB 现状 | NC 要求 |
|---|---|
| `Nat Methods. 2019;16:1289-96.` | `Nat. Methods 16, 1289–1296 (2019).`（期刊斜体、卷粗、年括号） |
| 作者 `Korsunsky I`（无点无空格） | `Korsunsky, I.` |
| 正文 `[6,7]`/`[22-24]` 方括号 72 组 | 上标数字；区间用 en-dash `22–24` |
| 56 条（≤70 合规） | 保持数量与顺序 |

## 4. Figures

- 面板标签：**小写粗体 a, b, c**（8 pt，正体非斜体，置于面板左上角）；不细分 a1/a2 [E]。
- 字体：全图统一 Arial/Helvetica，成品尺寸下 5–7 pt（最小 5 pt）；希腊字母用 Symbol 字体 [C]。
- 分辨率/格式：RGB；照片 ≥300 dpi（建议 450+）；线图/图表**矢量**（EPS/AI/PDF，直接从源程序导出，不得压平为位图），无法矢量时 1200 dpi；最细线 ≥1 pt。
- 尺寸：单栏 88 mm / 双栏 180 mm；按 210×276 mm 版面设计。
- 图例：每条 ≤350 词 [C][D]；首句为描述整图的短标题（不含面板引用），随后逐面板定义；图例可脱离正文读懂。
- 数量：≤10 个 display items（图+表），与字数匹配；<2000 词时 ≤4 个 [D][E]。

| GB 现状 | NC 要求 |
|---|---|
| 图例大写 `(A)/(B)` 42 处、"Panel A" | 小写 `(a)/(b)`、"panel a" |
| 图 PDF 内面板标签未审计 | 图内标签同样小写粗体（待查 figure1-6.pdf） |

## 5. Supplementary

- 命名（NC 官网示例，**无 "S" 前缀**；S1 式是 Scientific Reports 的惯例）[B]：
  `Supplementary Fig. 1`、`Supplementary Table 1`、`Supplementary Note 1`、`Supplementary Methods`、`Supplementary Discussion`、`Supplementary Data 1`、`Supplementary Movie 1`、`Supplementary Software 1`（句中 "Figure" 缩写为 "Fig."，句首全称）。
- 正文引用必须带 "Supplementary" 字样，逐项引用（避免笼统 "see Supplementary Information"）；不引用补充图的面板 [B]。
- 提交方式：SI 合为**单个 Word（优先）或 PDF** 单独上传（与正文分离）；大表格/数据/视频作为独立 Supplementary Data 等文件；单文件 ≤30 MB，全部 ≤150 MB [B]。
- SI 自包含：若有 Supplementary References 则从 1 独立编号，不引用正文文献列表 [B]。
- SI 不排版不校对，按终稿质量提交 [B]。

| GB 现状 | NC 要求 |
|---|---|
| `Additional file 1: Fig. S1`（18 处） | `Supplementary Fig. 1` |
| `Additional file 1: Table S1`（4 处） | `Supplementary Table 1` |
| `Additional file 1: Note 3.12`（38 处） | `Supplementary Note 3.12`（保层级，仅换前缀） |
| `Additional file 2` | 并入 SI（Supplementary Notes / Guide） |

## 6. Declarations（文末声明）

NC **无 "Declarations" 总标题**；各节为独立一级标题，顺序固定 [A]：Methods → **Data availability** → **Code availability**（如适用）→ References → **Acknowledgements** → **Author contributions** → **Competing interests**。

- Data availability：所有稿件**必须**；含 accession code + 超链接（建议格式 `GSE109774 [https://...]` 即代码后接方括号链接）；若有 Source Data 文件须含 "Source data are provided with this paper."；受限数据说明原因与获取途径。
- Code availability：与 Data availability **分设**；使用核心自定义代码/算法时必须；鼓励 GitHub + Zenodo DOI。
- Acknowledgements：简短；不谢匿名审稿人/编辑；基金号可放此处（GB 的 Funding 节内容并入）。
- Author contributions：标题用 "Author contributions"（非 "Authors' contributions"），以姓名缩写逐人说明。
- Competing interests：必须，每位作者明确声明；无冲突时写 "The authors declare no competing interests."
- 另有 "Correspondence and requests for materials should be addressed to X."（通讯行）。
- Ethics approval：涉及人/动物时在 **Methods** 内声明（批准机构+遵守指南+知情同意），NC 无 BMC 式独立 Ethics/Consent 节。

| GB 现状 | NC 要求 |
|---|---|
| "Declarations" 总块 8 子节 | 拆为独立节，删总标题 |
| "Availability of data and materials"（数据代码混写，含文献引用） | 拆成 Data availability（去文献引用）+ Code availability 两节 |
| "Funding" 独立节 | 并入 Acknowledgements |
| "Authors' contributions" | "Author contributions" |
| Ethics/Consent ×3 节 | 删除（纯计算研究无需） |

## 7. Cover Letter / 标题页 / Running head

- Cover letter：**可选但建议**；简述工作背景、重要性与期刊适配性；不重复摘要；含利益冲突与相关在投稿件声明；**不送审稿人** [C]。
- 标题页 [A][C]：标题 ≤15 词、无标点（逗号/括号可）、无双关、避免缩写与主动动词；作者全名；单位按作者首次出现顺序编号、每单位单一地址；通讯作者标 * 并给邮箱；共同一作/共同通讯仅允许固定两句 "These authors contributed equally: ..." / "These authors jointly supervised this work: ..." 各一次；ORCID 在投稿系统作者档案中登记（通讯作者必须）。
- Running head：NC 为纯在线期刊，**不要求 running head**（指南全文未提及）。

| GB 现状 | NC 要求 |
|---|---|
| CL 中 "Genome Biology"×3、"Methodology article" | 改 "Nature Communications"、"Article" |
| CL ~549 词、含 6 位建议审稿人 | 无字数硬限，审稿人建议可保留 |

## 8. 字数/图表数限制（指南性，非硬性拒稿线）[C][D]

| 元素 | 限制 |
|---|---|
| 标题 | ≤15 词 |
| 摘要 | ≤150 词（目标），上限 200 |
| 正文（Intro+Results+Discussion） | ≤5000 词（不含摘要/Methods/文献/图例） |
| Methods | 通常 <3000 词 |
| 图例 | 每条 ≤350 词 |
| 参考文献 | ≤70 |
| Display items | ≤10（图+表合计，与字数匹配） |
| 脚注 | 不使用 |

## 9. Statistics / Reporting Summary

- 生命科学稿件须随稿提交 **Nature Portfolio Reporting Summary**（nr-reporting-summary-flat.pdf，模板标注 "March 2021"）+ Editorial Policy Checklist；**NC 接受并要求**，发表时与论文一同上线 [F]。
- Methods 须含 **"Statistics and reproducibility"**（或 Statistics）小节。
- 图例（或 Methods）必须给出：每组确切 n（离散数值非区间）、技术/生物学重复说明、检验名称与单双侧、多重比较校正、精确 P 值（尽量）、中心值与误差棒定义（mean/median；s.d./s.e.m./c.i.）。
- 需声明（即使是否定）：样本量如何确定、纳入/排除标准、随机化方法、盲法程度 [F]。

| GB 现状 | NC 要求 |
|---|---|
| Methods 有 "Statistical reporting" 节 | 改名/对齐 "Statistics and reproducibility" |
| 无 Reporting Summary 文件 | 需新增填写提交 |

## 10. 其他易踩点

- "data not shown" 禁止；基因/基因型斜体、蛋白不斜体；物种名斜体 [E]。
- 避免 "new/novel/unprecedented/for the first time" 等措辞 [E]。
- 首次投稿格式宽松（单一 Word/TeX/PDF ≤30 MB，图文可合并）；上述细则在修改/接收阶段强制执行 [C][D]。
- 表：Word/TeX/Excel 可编辑，带短标题句 [C]。
- AI（LLM）使用声明置于 Methods——现状已合规 [E 惯例]。
