# v52 终审报告（R5：编辑/格式审稿）

- 审查对象（commit 7133b43 工作树）：`results/CKI_Manuscript_NC.docx`（MS）、`results/CKI_Supplementary_NC.docx`（SI）、`results/CKI_Reproducibility_Guide_NC.docx`（Guide）、`results/CKI_NC_Cover_Letter.docx`（CL）
- 审查人：R5-editor（编辑/格式）；审查日期：2026-09-24
- 方法：python-docx 全文提取 + 与任务书权威口径及跨文档 ground truth 逐项对照；xlsx 以 zipfile 读 workbook.xml 核对 sheet 清单

## 一、已核实达标项（ground truth 复核通过）

1. **标题一致性**：MS L1 / SI L2 / CL 首段均为 "…index **decomposing** functional divergence from baseline variation…"（H1 口径 ✓）；Guide 用独立标题（"Supplementary Methods: CKI Computational Reproducibility Guide"），无冲突。
2. **词数**：MAIN（Intro+Results+Discussion，含子标题）按空白切词计 **4,999 词**，与 XV8 口径 4,998/5,000 一致（±1 为切词器差异）✓；Abstract **恰好 200 词**，≤200 ✓（踩线，见 Minor 10）。
3. **引用体系**：文献 1–57 条 ✓；首现顺序抽查单调无乱序（Intro 1–12 → Results 13–28 → Discussion 29–41 → Methods 42–57）✓；多作者条目均 "et al."，未见 >20 作者全列 ✓。
4. **声明区块**：LLM 使用声明、Data availability（GEO/collection ID/GTEx V8/microglia h5ad/MSigDB 镜像）、Code availability 独立节（cki **v0.5.1**、tag **v0.5.1**、concept DOI **10.5281/zenodo.20405458**）、作者贡献、利益冲突、通讯方式齐备 ✓。
5. **已知过渡状态（按要求注明已见，不计缺陷）**：Code availability 中 version DOI 行当前指 v0.5.0 record（10.5281/zenodo.22735744），phase-2 待写回新 v0.5.1 DOI（任务 #47，依赖 #46 release/Zenodo 归档）。其余版本面（v0.5.1、tag、concept DOI、Dockerfile、Python ≥3.10）已就绪。
6. **SI 结构**：Notes 1–16 ✓；**Note 16 已更名** "Human-Brain Sanity Check on the Microglia Supercluster" ✓；Supplementary Methods 5.1–5.14 ✓；SI docx 0 个表格对象（散文+索引指针，符合"全部表格在 xlsx"方针）✓。
7. **新口径数字在 MS/SI/Guide 内一致**：TCGA 3,535、NN/TT 1.11–2.46、基线 7.70 [6.38, 9.82]（two-stage，旧 [7.37, 8.02] 一律标注 superseded）、脑梯度 3.7-fold [1.9, 3.8]（combined span+size 3.66 [1.92, 3.78]）、AUC 0.80 [0.770, 0.838] ✓。
8. **图资产**：主图 figure1–6 的 png/pdf 均存在且单文件 <1MB（≤10MB ✓）。86mm/178mm 栏宽、≥7pt Arial、300DPI 无法从文本层复核，未重新验证（依赖既有构建断言）。
9. **验证计数**（构建 221/221、ms_verify 117、si_verify 109、cl_guide 39、XV8 63/63）以构建日志为准，本轮未重跑。

## 二、Major issues（投稿阻断级，5 项）

### M1. 主表 Table 1 在 MS docx 中整体缺失
- 【位置】MS L52 两次引用 "Table 1"（"(Fig. 5; Table 1; Supplementary Fig. 5)"、"(n ≥ 5 pairs; Table 1)"）；但 MS docx **表格对象数 = 0**，图注区（L194–212）亦无 "Table 1." 表注。
- 【证据】`results/CKI_Tables_NC.xlsx` 存在且仅含一个 sheet 'Table 1'——内容在，但未随正文交付。
- 【为何重要】NC 要求主表嵌入正文文件末尾并附表注；当前状态为悬空引用 + 主表缺失，编辑部初检即退。
- 【建议】MS 文末（图注后）补 "Table 1. Cross-organ conservation of cell types (Tabula Sapiens)" 表注 + 表格本体（或随附单独表格文件并在投稿系统登记），并确认 xlsx 是否仅作内部存档。

### M2. Supplementary Fig. 14 图注与图资产双缺失
- 【位置】MS L39 引用 "(Supplementary Note 16; Supplementary Fig. 14)"；L191 SI 清单宣称 "Supplementary Figs. 1–**14**"；SI Note 16 末尾 "(Supplementary Fig. 14.)"。但 MS 图注止于 **Supplementary Fig. 13**（L212），SI docx 不含任何图注。
- 【证据】`results/figures_final/` 及全库 find 均无 microglia 图 png/pdf（仅 `results/audit/_fig14_preview.png` 预览残件）。
- 【为何重要】宣称 14 幅补图却只交付 13 幅图注、第 14 幅连资产都没有，属投稿包完整性硬伤。
- 【建议】生成 nc50 microglia 图（脚本 notebooks/nc50_fig_microglia.py）入 figures_final，并在 MS 图注区补 Supp Fig. 14 图注；或将 L191 改为 Figs. 1–13 并删除 L39 的图引用（不推荐，Note 16 需要该图）。

### M3. Cover Letter 口径陈旧，与 MS 数字冲突
- 【位置】CL 第 2 段："across **3,567** TCGA samples"（MS/Guide 新口径 **3,535**，ex-CC）；"NN/TT ω ratio **1.10–2.46**"（MS 新口径 **1.11**–2.46，LIHC 线性映射后 1.11）；"**ranked first** for functional-versus-neutral discrimination (AUC = 0.80)"（MS 摘要已软化为 "gave the best discrimination **at bounded power** (AUC = 0.80 [0.770, 0.838])"）。
- 【为何重要】CL 是编辑第一眼文件，与正文数字打架直接损害可信度；且 CL 未提及 GTEx 健康参照（v52 支柱三的关键新证据，正好回应 field-effect 质疑）。
- 【建议】CL 全量过一遍新口径（3,535 / 1.11–2.46 / bounded-power 措辞），补一句 GTEx 参照；顺手统一 "28.6% versus 35.7–45.2%"（见 Minor 6）。

### M4. SI 表格 xlsx 缺 Supp Tables 1–4
- 【位置】SI 索引（SI L30–48）列 Tables 1–19；MS L21/L53/L55/L65 引用 Supp Tables 1/2/3/4。但 `results/CKI_Supplementary_Tables_NC.xlsx` 实际 sheet 仅 **Table 5–Table 19**（v50 存档版同样缺，说明非本轮丢失而是从未纳入）。
- 【证据】Supp Table 3 的内容在 SI 散文中以 repo 路径指向（"Raw data file: results/brain_bs_null_observed_pairs.csv"，SI L267）——NC 不接受以仓库路径代替表格资产。
- 【为何重要】主文引用的 4 张补表在提交包中不存在，编辑/审稿人无法查看。
- 【建议】Tables 1–4 补为 xlsx sheet（Table 3 有 31,764 行，未超 xlsx 上限；若坚持文件过大，应重编号为 Supplementary Data 2–5 并在索引和引用处注明文件格式与位置）。

### M5. MS L70 "5,151 human pairs" 与全文口径冲突
- 【位置】Discussion L70："permuting k_n across the **5,151** human pairs predicts Spearman 0.524…"。全文及 SI 一致为 **4,851** pairs（99 entries，C(99,2)；MS L28/29/52/93/97、SI L106/145/232）；SI Note 9 通篇无 5,151。
- 【证据】5,151 = C(102,2)，疑为拿未过滤的 102 entries 计算或笔误。
- 【为何重要】Discussion 的关键反相关论证（observed 0.089 vs permuted 0.524）依赖该置换输入；输入规模与既定过滤口径不符会被统计审稿人（R1）追问。
- 【建议】核对 Note 9 置换分析的实际输入对数：若为 4,851 则改字；若确为 102 entries，则需在 Note 9 说明为何绕过了 pairwise-analysis 过滤。

## 三、Minor issues（10 项）

1. **SI 裸节号混用**："Section 3.12"（L37 末）、"Section 3.13"（L48 末）、"Section 1.4"（L72）、"Section 3.11 of the Supplementary Information"（L79，此条已全式）与 L24/L38/L47 的全式 "Section X of the Supplementary Information" 并存——统一为全式。
2. **"three-tier" vs "four-tier" drift ladder**：MS L37 "three-tier" vs Fig 3 图注 L196 "(a) Schematic of the four-tier drift ladder"（null 算一层）。v51r2 已指出，未修。
3. **Fig 5(d) 图注** "Top 5 **conservative** cell-type pairs" → "**conserved**"（v51r2 已指出，未修）。
4. **Fig 2(b) 图注** "k_n remains relatively constrained" 与 L25 "k_n rose only 72–118-fold" 的措辞张力仍在；建议改 "rises less than k_f across categories"。
5. **Data availability 自述不准**（L124）："Supplementary Tables 1–4 are cited in the main text"——主文还引用了 Table 5 与 Table 14（L49），与 M4 联动修正。
6. **CL 与 MS 的 FPR 区间表述**：CL "28.6% versus 35.7–45.2% for the other five"（含 k_n=35.7%）vs MS L37 "37.6–45.2% for the others"（仅四个外部连续度量，k_f=37.6% 最低）。两者各自自洽但集合未定义；MS 处建议写明 "the four standard continuous metrics"。
7. **L78 "(14; Results)"** 引用渲染突兀（他处文献为上标数字）→ "(ref. 14; Results)"。
8. **Fig 2(e) 图注**括号 "0/150 detections at δ = 1 on marrow versus 0.91 on keratinocyte" 将检出数与 AUC 并置，量纲不一；建议 "…versus AUC 0.91 on keratinocyte (where thresholded detection is high)"。
9. **SI Note 3 结尾自述** "Both raw and calibrated ω values are reported in all key results" 与主文 headline 全报原始 ω 的实践不符（跨文档自述冲突，v51r2 已指出）。
10. **摘要踩线**：恰好 200 词，按本任务口径（≤200）达标；建议对照 NC 当期 Guide for Authors 复核摘要上限口径（Nature Portfolio 部分期刊为 150 词），若更严需预留压缩余量。

## 四、总评

- **评分：7.0/10**
- **Verdict：major revision required before submission（修复后可投）**
- 文本本体（标题、摘要、词数、引用、声明、数字口径）已达标或近达标；5 个 Major 全部是**投稿包完整性/跨文档同步**问题，无一需要新增分析，一个修复轮次可清。

### 条件清单（投稿前必须全清）
1. 【M1】MS 文末补 Table 1 表注 + 表格本体；
2. 【M2】补 Supp Fig. 14 图资产 + MS 图注；
3. 【M3】CL 数字与措辞同步至 v52 口径（3,535 / 1.11–2.46 / bounded power），补 GTEx 一句；
4. 【M4】SI xlsx 补 Tables 1–4（或重编号为 Supplementary Data 并加指针）；
5. 【M5】核实并改正 L70 "5,151"；
6. 【已知】phase-2 写回 v0.5.1 新 Zenodo version DOI 后重建 MS（任务 #47，本轮已见过渡状态）；
7. 【Minor】建议同轮打包处理，尤其 #1–#3（均为前轮已指出未修项，累计两轮遗留）。
