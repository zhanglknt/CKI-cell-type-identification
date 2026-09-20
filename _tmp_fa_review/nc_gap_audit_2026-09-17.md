# CKI 投稿包 → Nature Communications 格式差距审计

- 审计日期：2026-09-17
- 审计对象（全部只读，未做任何修改）：
  - `version3/CKI_Submission_v47/CKI_Manuscript_fulltext.txt`（260 行，正文全文提取，下称 MS.txt；行号为该 txt 的行号）
  - `version3/CKI_Submission_v47/CKI_Cover_Letter_fulltext.txt`（11 行，下称 CL.txt）
  - `generate_manuscript_gb.py`（767 行，GB 版生成器源码，下称 GEN.py）
- 背景：现投稿包为 Genome Biology v47.3（Methodology article）；目标 Nature Communications（NC, Article）。
- 参考：MANIFEST_v47.txt 记载 v39 曾做过 NAR→GB 机械转换，本次为同级别的 GB→NC 转换。
- **v2 修订（2026-09-17）**：吸收 nc-spec 规范调研（nc_format_spec_2026-09-17.md）三处纠偏——① NC 文献 et al. 规则为 **≥6 位作者即截断**（非 ">10"）；② **Discussion 不允许小标题、Results 不允许二级小标题**（原判"可不动"有误）；③ NC 投稿与发表版均带 "Introduction" 标题（原"发表版不显示"表述有误）。同时补充词数合规审计（见 §1.4，发现正文超限 2.4 倍的重大差距）。

---

## 一、现有文档结构盘点

### 1.1 MS.txt 一级标题清单（按出现顺序）

| 顺序 | 标题 | MS.txt 行号 | GEN.py 行号 | NC 要求 | 动作 |
|---|---|---|---|---|---|
| - | Title | L2 | 302 | ≤15 词（现 12 词✓）；**避免标点（冒号不建议）与缩写**（CKI 为缩写） | **决策点**：建议去冒号前缀，如 "A Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics"（P2） |
| - | Authors/Affiliations/ORCID | L3-7 | 310-383 | 题目页信息；ORCID 在投稿系统作者档案登记（通讯作者必须） | 保留 |
| 1 | Abstract | L8 | 388 | ~150 词非结构化（投稿版保留标题名可） | 保留标题，词数微调（见二） |
| - | Keywords | L10 | 395-399 | NC 不使用关键词行 | **删除** |
| 2 | Background | L11 | 404 | NC **必须**以标题 "Introduction" 开始（投稿与发表版均带标题）；无小标题，≤~1000 词（现 620 词✓）；**末段需以 "In this work"/"Here, we show" 开头（现在时）概括结果与结论**——现末段以 "We evaluated CKI across four scales…" 开头，需改写 | **改名 Introduction + 末段改写为 "Here, we show…" 句式** |
| 3 | Results | L17 | 419 | Results；小节标题 ≤60 字符、不编号、**不允许二级小标题** | 保留 + 见 1.2 |
| 4 | Discussion | L77 | 547 | Discussion；**不允许小标题** | 保留 + 见 1.2 |
| 5 | Conclusions | L97 | 588 | **NC 无独立 Conclusions 节** | **删除节标题，正文并入 Discussion 末尾** |
| 6 | Methods | L99 | 594 | Methods（Discussion 之后、Data availability 之前；小节标题 ≤60 字符，指南 <3000 词，**现 4,437 词超限**） | 保留结构；见 1.4 |
| 6a | Use of large language models（Methods 内 L2） | L134 | 652 | NC 要求 AI 使用声明置于 Methods | 保留（位置已合规） |
| 6b | Statistical reporting（Methods 内 L2） | L130 | 645 | NC 要求 Methods 含 **"Statistics and reproducibility"** 小节 | **改名**；另需随稿新增 Nature Portfolio Reporting Summary（新文件，非本文档） |
| 7 | List of abbreviations | L136 | 658 | Nature 系无此节 | **删除**（17 条缩写可散入正文首现处，多数已定义） |
| 8 | Declarations（8 个子节） | L138-152 | 664-685 | NC 不用 BMC 式 Declarations 总块 | **重组**（见四） |
| 9 | Additional files | L153-155 | 690-692 | → **Supplementary Information** 描述段 | 改写命名（见五） |
| 10 | Figure legends（主图 Fig 1-6） | L156-162 | 697-709 | 图例单列（NC 要求分栏排版时图例随图，投稿版末尾集中可接受） | 保留位置；面板标签改小写（见六） |
| 11 | Additional file 1: Supplementary figure legends（S1-S13） | L163-176 | 714-740 | → Supplementary Fig. 1-13 | 改名（见五） |
| 12 | References | L177-233 | 758-761 | Nature 参考文献风格 | **格式转换**（见三） |

### 1.2 Results 小节（11 个 L2 + 3 个 L3）——v2 修正：L3 必须取消

L2 小节（MS.txt 行号 / GEN.py 行号；★ = 标题超 NC 的 60 字符上限，需缩短）：
1. Decomposing transcriptomic variation（L18 / 422）36 字符 ✓
2. Calibration confirms baseline behavior（L24 / 435）38 ✓
3. Correlation structure between CKI and standard metrics（L29 / 446）54 ✓
4. ★ Ground-truth simulation dissociates specificity from sensitivity（L36 / 462）65 字符 ✗
5. Real perturbation demonstration: IFN-β-stimulated PBMCs（L40 / 471）~55 ✓
6. Benchmarking against perturbation-response metrics（L42 / 475）50 ✓
7. ★ Fixed gene-panel ablation: rankings robust, absolute ω scheme-specific（L44 / 479）70 ✗
8. ★ Cancer analysis suggests apparent tumor homogeneity (exploratory)（L47 / 485）66 ✗
9. CKI ranks cell types by cross-organ conservation（L52 / 496）49 ✓
10. ★ Brain regional analysis reveals cell-type divergence gradients（L57 / 506）64 ✗
11. ★ Anomalously similar cell-type/region pairs: a hypothesis-generating screen（L65 / 522）75 ✗

**NC 明确 "Do not use secondary subheadings"（Results 二级小标题）**：3 个 L3 小节（Microglia、Oligodendrocytes、Astrocytes/fibroblasts/ependymal；GEN.py 532/535/538）需**降格**——去掉 L3 标题，改为 L2 小节 11 内的段落（可保留 "Microglia: …" 作段首粗体引导语或过渡句），内容不动。

Discussion 内 L2 小节：When to use CKI versus standard metrics（L86/565）、Practical usage guide（L88/568）、Limitations（L90/571）——**NC 明确 Discussion "No subheadings"**，三处标题**全部去除**，内容保留为连续段落（v2 修正：原判"可不动"有误）。

### 1.4 词数合规审计（v2 新增——发现最大内容级差距）

| 部分 | 现词数 | NC 指南 | 状态 |
|---|---|---|---|
| Introduction（L12-16） | 620 | ≤~1000 | ✓ |
| Results（L18-76） | 6,471 | — | — |
| Discussion（L78-96） | 5,060 | — | — |
| **Intro+Results+Discussion 合计** | **12,151** | **≤5,000** | **✗ 超限 2.4 倍** |
| Methods（L100-133，不含缩写表） | 4,437 | 通常 <3,000 | ✗ 超限 ~1.5 倍 |
| Abstract | 151 | ≤150（上限 200） | 边缘超 1 词 |
| 参考文献 | 56 条 | ≤70 | ✓ |
| 主图图例（最长 Fig 1） | 201 词 | 每条 ≤350 | ✓（Fig 1-6: 201/126/71/74/108/194） |
| Display items | 6 图 + 2 表 = 8 | ≤10 | ✓ |

注：字数上限为 NC 指南性要求（非硬性拒稿线，NC 首次投稿格式宽松），但 12,151/5,000 与 Methods 4,437/3,000 属**编辑性重大差距**，纯格式转换无法解决，需 team-lead 决策：压缩正文（可能伴随内容删减与断言值变化）或按现长度投稿接受编辑风险。建议在改造方案中单列此项。

### 1.5 Methods 小节（15 个 L2，含 LLM 声明）——结构保留，两处改名

CKI computation / Dimensionality invariance / Permutation test / Datasets / Method comparison / Multiplicative residual model / Robustness and calibration / Ground-truth simulation / Perturbation demonstration (IFN-β PBMC) / Fixed gene-panel ablation / Clinical severity analysis / Computational environment / Statistical reporting / Use of large language models（GEN.py 596-652）。
改动：① "Statistical reporting"（GEN.py 645）→ **"Statistics and reproducibility"**（NC 惯例小节名，内容基本可复用：现文已含 n 值、检验名与单双侧、多重比较校正、精确 P 值、误差棒定义等要素）；② 小节标题均 ≤60 字符（最长 "Multiplicative residual model for brain regional analysis" = 58 ✓，无需改）。另：统计声明的"样本量确定/纳入排除标准/随机化/盲法"否定式声明（即使否）需迁入 Reporting Summary 表单而非正文。

---

## 二、Abstract 与 Keywords

- **现状**：非结构化单段，实测 **151 词**（MS.txt L9；GEN.py L390）。形式已符合 NC（非结构化、无小标题）。
- **动作**：NC 摘要上限 ~150 词 → **删 1-3 词**（候选："(TCGA; exploratory)" 可精简，或去 "per donor per condition" 尾注之一）。
- **Keywords 行**（5 个关键词，MS.txt L10 / GEN.py 395-399）：NC 不使用 → **整行删除**。

---

## 三、参考文献（最大工作量项）

### 3.1 现状
- 文献清单：**56 条**，MS.txt L178-233（编号 1-56）。
- 生成器内 `_refs_nar` 列表：**GEN.py L229-286**（56 条字符串，注释在 L226 附近）。
- 当前格式（GB/Vancouver）：`Korsunsky I, Millard N, Fan J, ... et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat Methods. 2019;16:1289-96.`
  特征：作者姓+名缩写**无点无空格**（`Korsunsky I`）、期刊缩写无点（`Nat Methods`）、`年;卷:页`、`et al.` 由 "…, et al." 引出。
- 正文引用：**72 个方括号引用组** `[n]` / `[6,7]` / `[22-24]` 形式；56 条文献**全部被引用，无未引用编号**（已验证 1-56 无缺口）。
- 注意：正文中另有大量 `95% CI [7.37, 8.02]` 式统计区间方括号（约 40+ 处），转换引用时**不得误伤**（v39 转换时曾出现把 "(10)" 计数误转为 "[10]" 的先例，见 MANIFEST L411-414，需保留守卫）。

### 3.2 NC(Nature) 目标格式（v2：et al. 规则按 NC 官网修正）
- 文献条目：`Author, A. B., Author, C. D. et al. Title of paper. Journal Name Vol, pages (year).`
  - 作者名缩写带点带空格（`Korsunsky, I.`）；作者间逗号分隔，仅 2 位作者时用 " & "（`Efron, B. & Tibshirani, R. J.`）。
  - **et al. 规则（NC 官网 how-to-submit 原文）：作者 ≥6 位（six or more）时只列第 1 位 + "et al."；≤5 位全列。**（v2 修正：原写 ">10 才截断" 有误。）
  - **对 56 条现清单的实测影响（v2 重算）**：
    - 27 条已是 "…, et al." 且列出作者 ≥6 位 → **格式合规，仅需标点重排**；
    - 23 条无 et al. 且 ≤5 位作者已全列（#3, 6, 7, 8, 9, 10, 11, 13, 15, 21, 22, 28, 32, 33, 35, 39, 43, 44, 45, 46, 52, 54, 55）→ 合规，仅需标点重排；
    - **6 条无 et al. 且恰好 6 位作者全列（#4 Rosen、#20 Jones、#27 Foerster、#29 Yang L、#37 Jiang、#56 Liberzon）→ 需截断为第 1 作者 + et al.**。
    - **原 "恢复全名单" 的数据缺口不复存在**（v2 修正：NC 的 ≥6 截断规则与现列表的截断风格兼容，无需回溯完整作者名单）。
  - 期刊**缩写带点**（`Nat. Methods`）；**卷号及其后逗号加粗**；页码全区间或文章号；**年份置于末尾括号内**：`Nat. Methods 16, 1289–1296 (2019).`
  - 条数 ≤70（现 56 ✓）；每条只含一个工作。
- 正文引用：**上标阿拉伯数字**，按正文→图例→表例出现顺序编号；区间连字符 → en-dash（`22–24`）。投稿期方括号 `[1]` 通常也被接受，但终版必转。72 组引用位点不变。
- 书籍条目（第 54 条 Efron & Tibshirani）：`Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman and Hall/CRC, 1994).`
- 团体作者条目（#8/#9/#10/#11 Tabula/TCGA consortium、#55 CZI）：格式不变，仅套新框架。

### 3.3 转换工作量
- 56 条字符串重排（GEN.py L229-286 整块重写为 `_refs_nc`）：全部条目标点重排 + 6 条六作者条目截断（#4/#20/#27/#29/#37/#56）+ 双作者条目改 " & "。
- 72 个正文引用组改为上标（python-docx 可用 `run.font.superscript = True`；现生成器已有 `set_superscript` helper，GEN.py L123）。
- 引用组解析需处理：`[6,7]` → 上标 `6,7`；`[22-24]` → `22–24`；`[47,48]` → `47,48`。
- 参考文献段落渲染函数 `ref_p_nar`（GEN.py L288-297）重写为 Nature 版 `ref_p_nc`（含期刊斜体 + 卷加粗排版；当前 GB 版是纯文本、无斜体/加粗 run 拆分——Nature 终版要求斜体期刊名、粗体卷号，**需要拆 run**）。

---

## 四、Declarations 重组

### 4.1 现状子节（MS.txt L138-152 / GEN.py L664-685，按序）
1. Ethics approval and consent to participate（L139）
2. Consent for publication（L141）
3. Availability of data and materials（L143）
4. Competing interests（L145）
5. Funding（L147）
6. Authors' contributions（L149）
7. Acknowledgements（L151）

（"Declarations" 总标题 L138；其后 Additional files L153。）

### 4.2 NC 目标后置结构（v2：顺序按 NC 格式指南 [A] 校正，无 "Declarations" 总标题）

NC 官方固定顺序：Methods → **Data availability** → **Code availability**（如适用）→ References → **Acknowledgements** → **Author contributions** → **Competing interests**（"No other section headings are permitted"）。具体动作：

1. **Data availability**（独立节，MANDATORY）——从现 "Availability of data and materials"（L143-144 全部内容：GSE109774、CELLxGENE、GDC、HRT Atlas、collection ID、GSE96583、cBioPortal、MSigDB）迁出，**剔除正文引用 [55]/[56]/[16,17]**（NC 数据声明不带文献引用，相关文献移入正文/Methods）；建议 accession code + 超链接格式 `GSE109774 [https://...]`。位置在 Methods 之后、References **之前**。
2. **Code availability**（独立节，MANDATORY，现**完全缺失**）——从现段落后半拆出：GitHub v0.5.0 + MIT、Zenodo concept/version DOI、Dockerfile、notebooks 与处理数据矩阵。与 Data availability **分设**。
3. **Acknowledgements**——保留现内容（L152）**并将 Funding 内容并入**（"This work was supported by NSFC grant 32370682"）；位置在 References 之后。
4. **Author contributions**——保留现文（L150），标题由 "Authors' contributions" 改为 "Author contributions"。
5. **Competing interests**——保留（L146）；无冲突声明句为 "The authors declare no competing interests."（现文一致）。
6. Ethics approval / Consent to participate / Consent for publication——NC 对不涉及人类/动物材料的计算研究无此节；**删除**（NC 生命科学稿件的人/动物声明放 Methods 内，本研究不适用）。
7. 可选加 "Correspondence and requests for materials should be addressed to L.Z."（通讯行，置于 Competing interests 附近）。

---

## 五、附属材料命名体系（需要全文替换的大项）

### 5.1 现状命名体系
- `Additional file 1: Fig. S1–S13`（附图 13 张）
- `Additional file 1: Table S1–S4`（附表 4 张）
- `Additional file 1: Note X.X`（层级编号：3.5, 3.6, 3.12–3.17, 3.20–3.23, 4.6, 5.1, 5.2 共 **15 个不同 Note**）
- `Additional file 2`（Reproducibility Guide）
- 文件实体已命名 `Supplementary_Figure_S1-13.pdf`、`Table1-2.docx`、`CKI_Supplementary.docx`、`CKI_Reproducibility_Guide.docx`

### 5.2 正文引用计数（References 之前的正文，MS.txt）
| 模式 | 出现次数 |
|---|---|
| `Fig. S\d`（含 "Additional file 1: Fig. S4" 等前缀形式） | **18** |
| `Table S\d` | **4** |
| `Note \d.\d` | **38**（明细：3.12×5, 3.21×4, 4.6×3, 5.1×3, 3.16×6, 3.5×2, 3.13×2, 3.14×2, 3.15×2, 3.17×2, 3.22×2, 5.2×2, 3.6×1, 3.20×1, 3.23×1） |
| `Additional file`（任意） | **77** |
| 主图 `Fig. \d` | 9 |
| 主表 `Table \d` | 7 |

图例区另有 13 处 "Additional file 1: Figure S\d" 图注（MS.txt L164-176）。

### 5.3 NC 目标命名与动作
- `Additional file 1: Fig. S1` → **`Supplementary Fig. 1`**（NC 官方用法，图内标签亦应随 PDF 重排为 "Supplementary Fig. 1"——现有 PDF 面板内标签未审计，但文件名已是 Supplementary_Figure_S1.pdf，正文引用是唯一不一致处）。
- `Additional file 1: Table S1` → **`Supplementary Table 1`**。
- `Additional file 1: Note 3.12` → **`Supplementary Note X`**。**决策点**：NC 惯例是顺序编号 Supplementary Note 1, 2, …；现有层级编号 3.12 与 CKI_Supplementary.docx 内部 Note 结构绑定。两个方案：
  - A（保守）：`Supplementary Note 3.12`，保留层级，只换前缀——改动最小（38 处机械替换），与附注文件内部自引用（"本文件是 Additional file 1" 自指句）兼容；
  - B（彻底）：全部重编号为顺序 Supplementary Note 1-15——需同步改 CKI_Supplementary.docx 全部内部标题与自引用，风险高，不建议本轮做。
  - **建议 A**，附注文件标题行改为 "Supplementary Notes"。
- `Additional file 2`（Reproducibility Guide）→ NC 无 "Additional file 2" 概念；该文档可作为 **Supplementary Information 的一部分**（并入 Supplementary Notes 或作为 "Supplementary Reproducibility Guide"），正文 3 处引用（"Additional file 2" 出现 3 次含 Methods 计算环境节）改为对应新名。
- 末尾 "Additional files" 一节（MS.txt L153-155 / GEN.py 690-692）→ 改为 "Supplementary Information" 描述段，格式改为 NC 式（"Supplementary Information is available for this paper."或列出内容清单）。
- **预计正文替换总量：约 77+38+18+4 ≈ 130+ 处文本位点**（有重叠计数，实际唯一替换 ≈ 100 处）+ 图例区 13 处。

---

## 六、图例与面板标签

- 主图图例位置：MS.txt L156-162（Figure legends 节内 Fig 1-6；GEN.py 697-709）。附图图例：MS.txt L163-176（GEN.py 714-740）。
- **面板标签现状**：全文大写 `(A)/(B)/(C)/(D)/(E)` 共 **42 处**（A×15, B×14, C×8, D×3, E×1；其中 1 处 `(X)` 是小鼠类别标签 C/S/D/X 的假阳性）。Fig S5 图例另用 "Panel A/Panel B" 措辞（MS.txt L168）。
- **NC/Nature 要求**：面板字母**小写粗体 a, b, c**（8 pt，正体，面板左上角；不细分 a1/a2；图内标签与图例均小写）。动作：42 处图例文本 `(A)` → `(a)` 等（"Panel A" → "panel a"）；**图 PDF 内的面板标签本身是 first-author 重绘版，需另行检查图内标签大小写**（figure1-6.pdf 未审计，列为待办）。
- 图例句式：NC 要求每条图例 ≤350 词且首句为描述整图的短标题——现 Fig 1-6 图例为 201/126/71/74/108/194 词，全部合规；"Figure 1. The CKI framework. (A) …" 结构可保留。
- Display items：6 图 + 2 表 = 8 ≤ 10 ✓。
- 主图引用形式 "Fig. 1"（9 处）Nature 惯例一致，可保留。

---

## 七、Data / Code availability 现状

- 现状：**无独立标题**。全部内容在 Declarations > "Availability of data and materials"（MS.txt L143-144 / GEN.py 672-673）一个段落里，数据与代码混在一起。
- NC 需要：两个**独立**、**必须**的节，且 Data availability 不带文献引用（该段现在含 [55]、[56]、[16,17] 三个引用组，需剥离）。
- Code availability 素材已齐备（GitHub tag v0.5.0、Zenodo 10.5281/zenodo.20405458 / 22735744、MIT、Dockerfile、notebooks）。
- Discussion 末 L96 也有 GitHub 链接句（"The CKI Python package (v0.5.0) and all analysis notebooks are available at …"），NC 下可保留或收敛到 Code availability 一处。

---

## 八、Cover Letter 现状（CL.txt，11 行，约 549 词）

写给 GB 的证据（CL.txt 行号）：
- **L3**：`for consideration as a Methodology article in Genome Biology`（"Methodology article" 1 处）
- **L3**：`The work fits Genome Biology's tradition of single-cell computational methods…`
- **L6**：`has not previously been submitted to Genome Biology`
- "Genome Biology" 共 **3 处**；"Nature Communications" **0 处**。

其他要素：双作者批准/无竞争利益/未一稿多投声明（L6）、AI 使用披露（L6）、NSFC 资助（L6）、GitHub+Zenodo（L6）、**6 位建议审稿人**（L7，含邮箱）。

**改造动作**：
1. 期刊名 3 处全改 Nature Communications；"Methodology article" → "Article"。
2. "fits Genome Biology's tradition…" 句需改写为 NC 适配语（跨学科读者、单细胞方法学 + 大规模验证的组合定位）。
3. 审稿人建议可保留（NC 投稿系统支持）。
4. 约 549 词偏长，NC 无硬性限制，可保留结构。

---

## 九、生成器改造地图（GEN.py → generate_manuscript_nc.py）

| 区块 | GEN.py 行号 | 内容 | 拆分/复制动作 |
|---|---|---|---|
| 1-14 | 模块 docstring | 描述的还是 NAR（陈旧） | 重写为 NC 说明 |
| 16-24 | imports + `_load_manuscript_data` | 依赖不变 | 原样复制 |
| 27-100 | 数据 shorthand + phaseB/C JSON/CSV 装载 | 不变 | 原样复制 |
| 102-117 | 文档全局设置（Arial 11pt、1.15 倍、2.5cm 边距、页码） | NC 投稿版无排版硬要求 | 可原样复制 |
| 119-158 | helpers：`set_black`(120) `set_superscript`(123) `heading`(130) `p`(145) | 通用 | 复制；`set_superscript` 将被引用上标复用 |
| 159-227 | `add_table_1`(159) `add_table_2`(186) + 表题 | 不变 | 复制（表题 L191 含 "Additional file 1: Note 3.16" → 改 Supplementary Note） |
| **229-286** | **`_refs_nar` 56 条** | GB/Vancouver | **重写为 `_refs_nc`（Nature 格式，含期刊斜体/卷粗的结构化数据或纯文本）** |
| 288-297 | `ref_p_nar` 渲染函数 | 纯文本 10pt | 重写为 Nature 版（拆 run：期刊斜体、卷粗体） |
| 300-383 | Title page（题/作者/单位/通讯/ORCID） | 通用 | 复制 |
| **386-390** | Abstract（heading L388，正文 L390） | 151 词 | 复制 + 删 1-3 词 |
| 392-399 | Keywords | 删除 | **删除整块** |
| **401-414** | Background（heading L404） | 5 段 | heading 文本改 'Introduction'；**末段（L414/GEN 414）改写为 "Here, we show…" 开头（现在时）** |
| 419-546 | Results（11 个 L2 + 3 个 L3 小节 + 两张内嵌表） | 内容不动 | 复制 + 附属材料命名替换；**5 个超 60 字符的 L2 标题缩短（GEN 462/479/485/506/522）；3 个 L3 标题删除、内容降格为段落（GEN 532/535/538）** |
| 547-583 | Discussion（+3 个 L2 小节） | 内容不动 | 复制；**3 个 L2 小节标题删除（GEN 565/568/571），内容连续化**；末尾追加原 Conclusions 段 |
| **585-589** | Conclusions | 1 段 | **删除 heading，段落并入 Discussion 末（约 L583 后）** |
| 591-653 | Methods（15 个 L2，含 LLM 声明 L652-653） | 内容不动 | 复制 + 命名替换；**"Statistical reporting"（L645）改名 "Statistics and reproducibility"** |
| 655-659 | List of abbreviations | **删除** | 删除整块 |
| **661-685** | Declarations 块 | 8 子节 | **重组**（顺序按 NC 固定序）：拆出 Data availability（672-673 前半，去文献引用）与 Code availability（后半）置于 References **前**；References 后依次 Acknowledgements（含 Funding 678-679 并入）、Author contributions（改单数）、Competing interests；删除 Ethics(666-667)/Consent(669-670)/Declarations 总标题 |
| 687-692 | Additional files | 2 条 | 改写为 "Supplementary Information" 段 |
| 694-740 | Figure legends + 附图图例 | 大写面板标签 | (A)→(a) 等 42 处；"Additional file 1: Figure S1" → "Supplementary Fig. 1" |
| 755-761 | References 循环 | `for i, ref in enumerate(_refs_nar, 1)` | 换 `_refs_nc` |
| 763-767 | 保存 | `results/CKI_Manuscript_GB.docx` | 改输出名（如 `CKI_Manuscript_NC.docx`） |

**正文引用转上标**：GEN.py 的 `p(text)` helper（L145）是整段单 run；72 个 `[n]` 组需要新的段落构建函数（按方括号拆 run、数字 run 上标），并保留统计 CI 方括号守卫（v39 教训，MANIFEST L411-414）。

---

## 十、断言/构建校验要更新的项

MANIFEST 显示存在 build-time 全文断言体系（verify_v40_additions 式文本检查，针对 `*_fulltext.txt`）。GB→NC 转换后以下断言值将变化：

| 断言对象 | GB 现值 | NC 预期值 |
|---|---|---|
| `Background` 标题存在 | 1 | 0（改为 `Introduction` = 1，**投稿版也带标题**，v2 修正） |
| `Conclusions` 标题 | 1 | 0（并入 Discussion） |
| `List of abbreviations` | 1 | 0 |
| `Declarations` 标题 | 1 | 0 |
| `Keywords:` 行 | 1 | 0 |
| Introduction 末段 "Here, we show"/"In this work" 开头 | 0 | ≥1（v2 新增） |
| Results 二级（L3）小节 | 3 | 0（v2 修正：NC 不允许） |
| Discussion 小节（L2） | 3 | 0（v2 修正：NC 不允许） |
| 超过 60 字符的 Results 小节标题 | 5 | 0（v2 新增） |
| Abstract 词数 | 151 | ≤150 |
| `[n]` 方括号引用组（不含 CI） | 72 | 0（上标化后） |
| References 条目样式（`年;卷:页`） | 56 | 0（改为 Nature `卷, 页 (年)` = 56） |
| 无 et al. 且 ≥6 作者的文献条目 | 6（#4/#20/#27/#29/#37/#56） | 0（截断为第 1 作者 + et al.；v2 修正：NC 规则 ≥6 即截断，原 ">10" 有误；**无需补全作者名单**） |
| `Additional file` 出现（正文） | 77 | 0（改为 Supplementary 系） |
| `Fig. S\d` | 18 | 0（→ `Supplementary Fig. \d`） |
| `Table S\d` | 4 | 0 |
| `Note \d.\d` | 38 | 0（→ `Supplementary Note \d.\d`，若选方案 A 则保留 38 计数、仅换前缀） |
| 大写面板标签 `(A)` 等 | 42 | 0（→ 小写 `(a)`） |
| `Data availability` 独立节 | 0 | 1 |
| `Code availability` 独立节 | 0 | 1 |
| `Statistics and reproducibility` 小节 | 0（现为 "Statistical reporting"） | 1 |
| Nature Portfolio Reporting Summary 文件 | 0 | 1（新增表单，非正文断言） |
| Cover Letter "Genome Biology" | 3 | 0（→ Nature Communications ≥1） |
| Intro+Results+Discussion 词数 | 12,151 | ≤5,000（指南性；需编辑决策，v2 新增） |
| Methods 词数 | 4,437 | <3,000（指南性；需编辑决策，v2 新增） |

**不变项**（可作回归锚点）：56 条文献数量与顺序、72 个引用位点数（转上标后位点不变）、主图 6 张/附图 13 张/附表 4 张、15 个 Note 编号集合、所有科学数值。

---

## 十一、优先级汇总（v2 修订）

- **P0（NC 硬性/结构性要求）**：① Data availability + Code availability 独立节（按 NC 固定顺序插位）；② Introduction 改名 + 末段 "Here, we show…" 改写；③ 删 Conclusions/List of abbreviations/Keywords；④ **删 Discussion 3 个小节标题、删 Results 3 个 L3 小节标题、缩短 5 个超 60 字符标题**（v2 新增）；⑤ 附属材料命名换 Supplementary 系（~100+ 位点）；⑥ Cover Letter 期刊改写。
- **P1（格式合规）**：56 条参考文献 Nature 化（27 条 et al. 合规重排 + 23 条 ≤5 作者重排 + 6 条六作者截断）+ 72 组引用上标化；面板标签小写化；Abstract 减至 ≤150 词；"Statistical reporting" → "Statistics and reproducibility"；新增 Nature Portfolio Reporting Summary 表单。
- **P2（可选/编辑决策）**：**正文词数压缩（12,151 → ≤5,000 指南值，Methods 4,437 → <3,000）——这是最大内容级差距，需 team-lead 决策**；标题去冒号/去缩写；图 PDF 内面板标签大小写检查；Note 层级编号是否顺序化（建议保留）。
