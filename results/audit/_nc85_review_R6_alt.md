# Nature Communications 独立审稿意见 — R6（期刊编辑 / 可复现性与技术初筛）

**总分：7.0 / 10**
**建议：Minor Revision**
**初筛结论：技术性退回（Return before review）**
**判定标签：无 P0 诚信/合规阻断、归档诚实与全链验证近乎无瑕；退回仅因送审包内 3 处错误 sheet 指针与 SF9 零规范引用构成引用闭环破损——补齐后即可直送外审。**

> 盲审声明：本意见仅依据 `_nc85_review_materials/` 内 ms.txt、si.txt、cl.txt、guide.txt、tables_overview.txt、manifest.txt、round.txt 七份材料，以及委派时给出的已核验远端状态；未读取任何前轮报告、专家团汇总、事实核查或修复报告，未联网、未执行任何 git/网络命令。下引「远端硬证据」均指该已核验状态。

## 1. 评分表（6 维）

| 维度 | 分数 | 理由 |
|---|---|---|
| 新颖性 | 6.5 | 将 Ka/Ks 启发式迁移为 ω=k_f/k_n、并以 HK 面板作内基线是清晰的再框定，Supplementary Note 20 给出 ω=α+E_f/E_b+ε 的 scoped 框架；但组件（JS 散度 + HK 参考面板 + 比值）均为既有元素，MS 正文自述 "recombines established ideas"（ms.txt:64）、"a heuristic index, not a formal selection measure"（ms.txt:64），核心产出是一个「分母警告」而非新机制。 |
| 理论严谨 | 7.5 | Lemma 1/2、Proposition 3–5、条件 ω>2α 与失效比例（30.3% pairs、全部 39 个 Strong 候选，ms.txt:61）均明示；delta-method 预测偏差 <0.8% 与实测 −8.3%~+6.5%（约 10% 残差）并列披露（ms.txt:24），k_f 尺度二阶展开误差 10–18% 亦自认近似（si.txt:337）。严谨但主动限定，不冒充形式化选择度量。 |
| 统计严谨 | 8.5 | 全稿最扎实处：置换检验 B=1,000、BH 分层 FDR、cluster/两阶段/studentized bootstrap、donor-stratified null、wild-cluster bootstrap、DeLong、配对 McNemar 框架齐备；并主动标注 anti-conservative 来源（TCGA 固定面板、被取代的 i.i.d. 区间）、置换分辨率极限（q<0.05 需 B≈6×10⁵，ms.txt:112）与单/双尾例外。自我审计密度远高于平均水平。 |
| 证据充分 | 7.0 | 数据面广（Tabula Muris / Tabula Sapiens / TCGA 五癌 / Siletti 脑图谱 / Kang IFN-β / GTEx / SEA-AD），含 ground-truth 双背景模拟、10x 移植、fixed-panel、global-k_n、anchor-list、composition、purity、smoking、RIN、CNA 等多重消融。但确证性弱且作者如实收窄：KRAS 仅为 group-level association、生存分析 null、跨物种未建立、cross-organ 排序描述性、39 个 Strong 无 FDR（min q=0.520）、多数结论为 upper bound / vignette。 |
| 表达清晰 | 6.5 | 结构完整、每个数字几乎都随附限定语，可读但极密（MAIN 5,000/5,000 顶格，括号堆叠限定）；交叉引用体例不统一：`Supplementary Fig` 首现序列 [11, 1, 2, 3, 4, 10, 5, 6, 8, 7]、SF9 正文零规范引用、ms.txt:71 裸 `Fig. 9`、SI 补充表索引 3 处错误 sheet 指针（见清单 P1）。属于文案卫生问题，非论证混乱。 |
| 影响力与 NC 适配度 | 6.5 | 对方法学读者有实用价值（HK-anchored normalization 的边界条件、anchor-credibility check、可复现性范本），契合 NC 方法/资源类；但作者自述 "complement rather than replace"（ms.txt:68）、precision-first 以灵敏度为代价（35–66% vs 97–100%）、AUC 0.80 被明确标注 background-specific（10x pooled 0.51–0.53）、ω 非预后标志物。属诚实、有限但可用的增量。 |

## 2. 总体评价

这是一份技术自律程度罕见的投稿包：版本与归档措辞诚实、可复现性指南与脚本/输出/版本串一致、对局限与阴性结果的披露近乎逐条自我审计，全链验证与图合规均无失败项。科学上，方法被恰当地定位为一个 studentized 的、以 HK 面板为内基线的启发式指标，主要贡献是量化「分母自身会漂移」这一警告，而非宣称新的选择检测能力；大量结论被作者主动降格为 descriptive / upper bound / hypothesis-generating，这既削弱了影响力，也消除了夸大风险。本意见不提出任何科学否定：唯一阻断性判断来自送审包的交叉引用闭环——SI 后段补充表索引仍使用旧 sheet 编号，SF9 在正文未被规范引用——这类缺陷会直接误导外审与复现者，且修复成本极低，故建议在送外审前做一次 Minor 级技术修正。

## 3. 技术初筛清单（逐条 P0 / P1 / P2）

### P0（阻断送审级：诚信、归档、合规、完整性）— 0 项

以下门槛逐条核验，**均通过**，故不存在 P0 阻断；本次「技术性退回」由 P1 引用闭环缺陷触发，不涉及数据、代码或结论诚信。

- **P0-候选 1｜版本/归档声明诚实性 — 通过。** ms.txt:120："The CKI source code (v0.6.4) is publicly available at https://github.com/zhanglknt/CKI-cell-type-identification (tag v0.6.4) ... this tag contains every analysis script cited in the Methods and Supplementary Information. An earlier release is archived at Zenodo (concept DOI: 10.5281/zenodo.20405458); the code accompanying this submission is the v0.6.4 tag."、"an earlier snapshot is mirrored in the Zenodo archive"；guide.txt:26："Archived release: Zenodo concept DOI 10.5281/zenodo.20405458 (an earlier release); the code accompanying this submission is GitHub tag v0.6.4"。远端硬证据：`refs/heads/main = d7e45cf4aecdc66504e59b727f9370e2771db383`、`refs/tags/v0.6.4 = 0d7d057644dfae709dc2fe0cc59730ef48e535eb`（annotated，peeled = `d7e45cf`），tag 真实存在且含 Methods/SI 引用的全部脚本；Zenodo concept DOI 最新归档仍为 v0.5.6。措辞用 "An earlier release is archived" / "an earlier snapshot is mirrored"，**不声称 v0.6.4 已归档**，与远端状态完全相符。**修法：无需修改；建议接收前补一个 v0.6.4 的 Zenodo version DOI（非阻断，见 P2）。**
- **P0-候选 2｜图合规 — 通过。** 远端硬证据：`scripts/check_figure_spec.py` 15/15 pass、退出码 0；`_nc83_figure_exceptions.json` 为空 `{}`。guide.txt:443 印证："All 15 figure PDFs (figure 1-4 plus Supplementary Figs. 1-11) pass with primary >= 7 pt (main) / >= 5 pt (supplementary) and width <= 180 mm."；manifest.txt 列出 figure1–4 与 Supplementary_Fig_1–11 共 15 份 PDF。**修法：无需修改。**
- **P0-候选 3｜包完整性与全链验证 — 通过。** 远端硬证据：包 23 文件、zip 13,634,695 B、单文件最大 3.31 MB；manifest.txt:22 的 `Supplementary_Fig_6.pdf (3,467,869 bytes)` 与 3.31 MB 相符；全链验证 0 failure（build 240/240；7 个验证器全绿；pytest 29；三方逐 sha256 相等），manifest.txt:31–53 逐文件给出 SHA-256。**修法：无需修改。**
- **P0-候选 4｜词额与格式 — 通过。** 远端硬证据：MAIN 5,000/5,000、摘要 148/150、CL 509/530、Methods 3,228/3,300、图注 max 337/350，均在限额内。**修法：无需修改（顶格风险见 P2）。**
- **P0-候选 5｜数据/代码可用性与 AI disclosure — 通过。** ms.txt:117–118 逐项列明 GEO GSE109774 / GSE96583、CELLxGENE（含 collection ID 283d65eb…）、GDC、HRT Atlas、GTEx V8、cBioPortal、MSigDB 镜像，并声明 "All Supplementary Tables (1–17) are provided in CKI_Supplementary_Tables_NC.xlsx"；ms.txt:120 为 Code availability。AI disclosure 有独立小节 ms.txt:115–116 "Use of large language models"，声明用于 computational debugging / statistical code review / language editing 且作者复核并负全责，符合 NC 政策。**修法：无需修改。**
- **P0-候选 6｜R-native scDist 替代声明诚实性 — 通过。** ms.txt:43 "MELD (v1.0.2) and a Python approximation of scDist"；ms.txt:74 Limitations："the scDist comparison uses a Python approximation of the R implementation, which could not be installed in this environment and is labelled as such wherever it is reported"；si.txt:133 小节标题 "Competitor Benchmark: MELD and a Python Approximation of scDist"、si.txt:134 "not the R package's exact implementation and is labelled 'Python approximation of scDist' throughout"；si.txt:242 进一步写明 "An R-native scDist/scCODA benchmark was not run: the R package could not be installed in this environment (R 4.1.3 with base packages only, and the scDist dependencies unavailable from the configured mirror)"，并说明由 covariance-whitened baseline 与 10x modular OC 直接分析补位；tables_overview.txt:30 "scDist (Python approximation)"、guide.txt:300/302/534 均带 approximation 字样。核验全部出现处，标注一致、原因具体、未把近似结果冒充 R 原生结果。**修法：无需修改。**

### P1（送审前必改；本次 Return before review 的触发项）— 2 项

- **P1-1｜SI 补充表索引的 3 处错误 sheet 指针（且与 SI 自身目录自相矛盾）。**
  - 位置与原文：si.txt:326 "Supplementary Table 9: Cross-Organ Conservation Data ... Table content: CKI_Supplementary_Tables_NC.xlsx (**sheet Table 4**)."；si.txt:328 "Supplementary Table 10 ... Table content (per-cell-type summary): ... (**sheet Table 5**)."；si.txt:330 "Supplementary Table 12 ... **Tables 5 and 6 share the same underlying data file** ... Table content: ... (**sheet Table 6**)."（同句后半又正确写 "Supplementary Table 10 ... Supplementary Table 12"，同句内编号自相矛盾）。
  - 反证：si.txt:58 "sheets Table 1-17 in numeric order"；ms.txt:118 "All Supplementary Tables (1–17)..."；tables_overview.txt:106 `sheet 'Table 9'` = Cross-Organ Conservation、:118 `sheet 'Table 10'` = Siletti 脑区、:142 `sheet 'Table 12'` = inter-regional candidates。而 `sheet 'Table 4'`（tables_overview.txt:48）实为 Brain drift ladder、`Table 5`（:60）为 Pan-cancer NN/TT、`Table 6`（:70）为 LUAD driver-group。读者按 SI 指针打开 sheet Table 4 将看到完全无关的表。
  - 影响：不触及数据或结论，但直接破坏复现路径与外审查表效率，属送审包内部一致性缺陷。
  - **修法**：si.txt:326 `sheet Table 4` → `sheet Table 9`；:328 `sheet Table 5` → `sheet Table 10`；:330 `sheet Table 6` → `sheet Table 12`，并将 "Tables 5 and 6 share..." → "Supplementary Tables 10 and 12 share..."。同时把 si.txt:324 的 `(sheet Table 1)` 作为正确范式保留，全段统一为 "Supplementary Table N ↔ sheet Table N"。
- **P1-2｜SF9 在 MS 正文零规范引用 + 裸 `Fig. 9` 悬空指针 + Numbering note 与实际失配。**
  - 远端硬证据：MS 正文 `Supplementary Fig` 首现序列 [11, 1, 2, 3, 4, 10, 5, 6, 8, 7]，**SF9 在 MS 正文零引用**。
  - 位置与原文：唯一语义指向 SF9（谱系距离验证，si.txt:344 "Supplementary Fig. 9. Lineage-distance validation of k_f across two independent atlases"）的正文位置是 ms.txt:71："k_f also recapitulated Cell Ontology lineage distance in two atlases (both permutation P = 1.0 × 10⁻⁴; **Supplementary Note 17, Fig. 9**)"。主文仅 Fig. 1–4、Table 1，故裸 `Fig. 9` 形式上是悬空/歧义指针；同类简写还有 ms.txt:54 "Supplementary Note 18, **Fig. 7, Table 11**"、ms.txt:61 "**Supplementary Fig. 8, Tables 12, 13**"、ms.txt:71 "Supplementary Note 19, **Fig. 7, Table 14**"，而 ms.txt:38 又用全称 "Supplementary Fig. 11a; Supplementary Table 3a"，体例不统一。
  - 与 SI 说明冲突：si.txt:335 "Numbering note. Supplementary Figs. 1–9 follow the order of first citation in the main text; Supplementary Figs. 10 and 11 are companion figures to main Figs. 3 and 2, respectively, and retain their series numbers so that cross-references remain stable." 伴生图豁免（SF10/SF11）作者已裁定、SF10/SF11 图注（si.txt:345/346）与之一致，此项予以认可；但 SF9 落在 "1–9 按首现顺序" 范围内却未在正文规范引用，该说明与事实失配。
  - **修法**：ms.txt:71 改为 "Supplementary Note 17, **Supplementary Fig. 9**"，并在 SI Numbering note 补一句说明 SF9 的引用位置；同时建议全稿统一 `Supplementary Fig.` / `Supplementary Table` 前缀，消除 ms.txt:54/61/71 的裸 `Fig. 7 / Table 11 / Tables 12, 13 / Table 14` 简写（该体例是首现序列缺口与计数歧义的直接来源）。

### P2（建议修订，不阻断）— 7 项

- **P2-1｜旧图号 `Fig. 2` drift 指针（SI）。** si.txt:100 "Unlike the Tabula Muris full pairwise matrix (**global HVG set for Fig. 2**), Tabula Sapiens ..."。按 ms.txt:21/26，global top-2,000 HVG 的 703-pair full matrix 对应 **Supplementary Fig. 1**，Fig. 2 是 calibration/metric correlation/ground-truth ROC。此处为旧图号残留。**修法**：改为 "global HVG set for Supplementary Fig. 1"（或 "for the full pairwise matrix"）。
- **P2-2｜guide 内节/图错配。** guide.txt:410 "10x modular operating characteristic (**Section 3.11; Fig. 2d**)"：10x modular OC 结果在 si.txt:141–142（SI 3.11 正文），而 Fig. 2d 是 SmartSeq2 marrow-B-cell 六指标 ROC（ms.txt:36、ms.txt:189）。**修法**：改为 "(Section 3.11; Supplementary Fig. 2d 不适用，见 Section 3.11 正文与 Supplementary Note 1)"，或仅保留节号去除图号。
- **P2-3｜`Supplementary Table 2a/2b/2c` 子面板标签映射未显式声明（核验结论：非悬空）。** si.txt:136 引用 "Supplementary Table 2a"、si.txt:137 "Supplementary Table 2b"，ms.txt:36 "Supplementary Table 2c"、ms.txt:73 "Supplementary Table 2b"，manifest.txt:4 提及 "Supplementary Table 2c"；tables_overview.txt:24–25 显示工作簿仅单一 `sheet 'Table 2'`，但其标题内含 (a) Target-detection AUC、(b) Donor-paired power、(c) Six-metric ROC 三个面板，三者均可对应，**不构成悬空引用**。但 si.txt:40 目录只列到 "Supplementary Table 2"，未声明 a/b/c 子面板。**修法**：在 Supplementary Table 2 标题与目录显式标注 "(a)/(b)/(c)" 及对应子面板名，避免读者在单 sheet 中找不到 "2a" 标签。
- **P2-4｜`main-text Supplementary Fig.` 残留 — 核验未发现。** 全目录检索仅在 tables_overview.txt:61 命中 "Ranked by NN/TT effect size (**main-text Fig. 3**)"（Supplementary Table 5 图注指向主文 Fig. 3），属合法用法；未发现 `main-text Supplementary Fig.` / `main text Supplementary Fig` 形式的残留。**修法：无需修改（记录为已清除）。**
- **P2-5｜对外文档残留内部轮次/批次标签。** manifest.txt:2 "CKI Submission Package **v49**"、:4 "tag: v0.6.4 | **nc84 round: expert-panel P0/P1/P2 fixes**, Supplementary Table 2c, multi-page Supplementary Figs. 1/3/5/6"、:6 "Note: 'v49' is the package build-batch label"；guide.txt:375 "The following analyses were added for the **v52 revision (expert-panel round on v51r2)**"、:353 "(v49.14)"、:555 "notebooks/114_recompose_suppfigs_**nc84**.py"；round.txt:1 "Round: nc85 (post-fix blind re-review...)"。ms.txt/si.txt 正文未见此类标签，但 MANIFEST 与 Reproducibility Guide 是编辑部与审稿人可见文件，暴露内部迭代/审稿轮次痕迹不利于送审包洁净度。**修法**：将 "expert-panel round … / P0/P1/P2 fixes" 等改为中性描述或移入内部 CHANGELOG；脚本文件名可保留（属可复现性所需），但在指南正文用功能名叙述。
- **P2-6｜词额顶格 + 安装方式轻微不一致。** 远端硬证据：MAIN 5,000/5,000、Methods 3,228/3,300、摘要 148/150、图注 max 337/350——均无缓冲，任何 P1 修订（如补全 `Supplementary` 前缀）都可能挤出限额，**修法**：P1 修订时同步复核词额，优先用简写替换 elsewhere 而非新增句。另 guide.txt:24/557 "pip install -e ."（本地 editable）与 si.txt:332 "pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git"（未 pin tag）并存，**修法**：统一为 `pip install -e .` 并注明 "at tag v0.6.4 / commit d7e45cf"，与 ms.txt:120 的版本声明闭环。
- **P2-7｜Cover Letter 一页化与推荐审稿人 — 达标，附核验建议。** cl.txt:1–9 为一页篇幅（远端硬证据 CL 509/530 词达标），含投稿声明、四支柱、两点性质、推荐审稿人与落款；cl.txt:5 列 6 位推荐审稿人（Fabian Theis、Joshua Welch、Sten Linnarsson、Patrik Ståhl、Alejandro A. Schäffer、Zemin Zhang），均附机构邮箱并声明 "Suggested reviewers, **none with conflicts**"，格式符合初筛要求。CL 内数字（56% [46–66%]、AUC 0.80、10x 0.51–0.53、36.7%/23.3%、28.6%、11.4%/10.3%/4.8%、MAD 0.113 vs 0.267–0.586、6.10/3.66、P=0.001/0.014/0.163、fixed-panel P=0.089）与 ms.txt 摘要/正文一致，无夸大。**修法**：无需修改；建议编辑部按 NC 政策独立核验推荐人与本文被引方法/数据源的潜在关联（本意见不联网、不臆断具体关系），并建议在接收前为 v0.6.4 补一个 Zenodo version DOI，使 concept DOI 下的最新归档与本稿一致（非阻断）。

## 4. 优点（技术合规做得好的地方，点名）

1. **归档与版本措辞诚实且跨文档统一。** ms.txt:120 与 guide.txt:26 均以 "an earlier release / earlier snapshot is mirrored" 明确区分「GitHub tag v0.6.4（本稿代码）」与「Zenodo concept DOI 的更早归档」，与远端「tag v0.6.4 真实存在、Zenodo 最新仍 v0.5.6」完全一致；全包版本串统一为 v0.6.4（ms.txt:80/120、si.txt:98/127、guide.txt:24/26/446/557、manifest.txt:4），无 drift；Python 3.14.4 / scanpy 1.12.1 在 ms.txt:110、si.txt:318、guide.txt:11–19 三处一致。这是最容易出错、也最容易被初审抓住的一环，本稿处理得干净。
2. **可复现性指南的脚本—输出—版本闭环。** guide.txt 逐节给出 notebooks/ 脚本、results/ 输出、seed 例外（:47）、超参数（:61）、权威输出与 superseded 归档策略（:445–446）、7 项 checklist（:557–563），并主动标注 "Ten pre-fix output files whose values contradict the manuscript are consolidated under results/superseded/ ... must not be used as numerical sources"（:445）；guide.txt:443 与远端 15/15 pass、`_nc83_figure_exceptions.json = {}` 相互印证。配合远端「全链验证 0 failure（build 240/240、7 验证器全绿、pytest 29、三方逐 sha256 相等）」，构成可核查而非口头的可复现性主张。
3. **替代方法与阴性/边界结果的披露纪律。** scDist 的 Python 近似在 MS、SI、Guide、表格标题四处一致标注，且 si.txt:242 给出 R 环境不可安装的具体原因与两项替代分析；同理 pyaugur 被标注为 "port's self-reported benchmark rather than an independent validation by us"（si.txt:240）、q<0.05 不可达被明确归因为置换分辨率（ms.txt:112）、ω 的 anchor-visibility 边界与 10x 上 AUC 0.51–0.53 的失利被写入摘要与正文。这种「主动交出反证」的写法显著提升可信赖度。
4. **引用主干闭环完整。** SI 图注 1–11 齐备（si.txt:336–346）、Supplementary Notes 1–24 齐备（si.txt:14–37）、Supplementary Tables 1–17 齐备（si.txt:39–55 目录 + tables_overview.txt 逐 sheet）、主文 Table 1 另置 CKI_Tables_NC.xlsx（ms.txt:192、tables_overview.txt:2），数据可用性段落（ms.txt:117–118）逐项可溯源；SI 伴生图编号豁免（si.txt:335）由作者裁定且与 SF10/SF11 图注自洽，予以认可。

## 5. 给编辑的备注（是否可送外审及理由）

**结论：不建议按现状直接送外审；建议以「technical return for pre-review correction」退回，修完 P1-1、P1-2 后立即进入外审。**

理由分三层：
1. **不存在 P0，也不构成科学否定。** 归档真实性（tag v0.6.4 = d7e45cf，Zenodo 措辞诚实）、图合规（15/15 pass、exceptions 为空）、全链验证（0 failure、三方 sha256 相等）、词额、数据/代码可用性、AI disclosure、Cover Letter、推荐审稿人、R-native scDist 替代声明，逐条通过。任何以「诚信 / 缺失文件 / 声称不存在的归档」为由的退回都不成立。
2. **但送审包的交叉引用闭环确有破损，属编辑初筛职责范围。** si.txt:326/328/330 把 Supplementary Tables 9/10/12 指到 sheet Table 4/5/6（实际分别是 Brain drift ladder / Pan-cancer NN/TT / LUAD driver-group），且与 si.txt:58 自身「sheets Table 1-17 in numeric order」矛盾；SF9 在正文零规范引用、ms.txt:71 用裸 `Fig. 9`、si.txt:335 的 Numbering note 因此与事实失配。这些缺陷会让外审与复现者打开错误的表、找不到被引的图，正是应在送审前拦下、且不该消耗外审时间的问题。
3. **修复成本与修订量均为 Minor 级。** 全部为编号/前缀/标签级文案改动，无需新实验、新分析、新数据或重跑流水线，也不改变任何数值与结论；建议 Minor Revision 表示的是「改动量」，而非外审后的科学裁决。P2 七项可并入同一轮，其中词额顶格（MAIN 5,000/5,000）需在补 `Supplementary` 前缀时同步复核。

若编辑部倾向于「带瑕疵送审、由外审一并提」，本意见不反对——P1 两项不触及结果有效性；但从可复现性初筛角度，先花一轮把 sheet 指针与 SF9 引用补齐，对审稿效率更有利。另请按 NC 政策独立核验 6 位推荐审稿人的潜在关联（P2-7），并考虑在接收阶段为 v0.6.4 生成 Zenodo version DOI。
