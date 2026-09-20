# Expert 4 审稿报告：写作与 NAR 期刊策略审查（v35）

**稿件**：CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**目标期刊**：Nucleic Acids Research（NAR）
**审稿范围**：格式合规、投稿包卫生、图注一致性、引用检查、语言与结构、已知关注点逐一验证
**审稿人**：Expert 4（学术写作 / NAR 期刊策略）
**日期**：2026-08-28

---

## 一、总体评价

**结论倾向：大修（Major Revision）后重新送审。**

科学内核与主稿正文的质量较 v5 有实质提升：softmax 归一化已在主稿 Methods/统计约定中统一（base-2 对数 + softmax + k_n floor），脑区 block-shuffle null（B=1,000、m=31,764、min q=0.949）已在 Methods、Results、Discussion、Limitations、Figure 6、Fig S9 中保持一致，21 条 Limitations 编号连续、脑区结论定位为 hypothesis-generating 也全程自洽。正文层面对上一轮多项关注点（one-sided 检验论证、n<5 跨器官样本警示、TCGA 配对比较去 P 值、图注统计约定段）均落实。

但提交包存在系统性"v35 主稿与配套文档脱节"问题：**补充材料、复现指南、投稿信、MANIFEST 四个文档大量残留 v5 旧方法、旧数字**，与主稿正文直接冲突（脑区候选 30 vs 55、CV 97.35% vs 92.89%、μ_grand 8.01 vs 32.56、人 5,151 vs 4,851 对、AUC 0.847 vs 0.786 等）；另有 FDR 引用错配（BH-FDR 挂靠 Storey & Tibshirani 2003，而 Benjamini & Hochberg 1995 缺失）、Data availability 声明不实（"notebooks and data matrices included in Supplementary Data"但投稿包无任何代码/数据文件）、稿件内缺 AI 使用声明（OUP/NAR 强制要求）等期刊合规硬伤。以上任何一项被编辑或审稿人发现都会显著影响送审印象与通过概率，故定为大修。

---

## 二、Critical（8 项，须修改后方可送审/修回）

### C1. Figure 2B 与 Figure 3D 图注的 S 类别定义与正文直接矛盾，且 Figure 2 内部 C 定义自相矛盾
- **问题**：正文 Results 定义 S = "Same cell type across different organs"（manuscript line 53："Same cell type across different organs (S category: mean ω = 21.31, n = 4 pairs)"；line 57 人类 "same cell type across organs"）；而 Figure 2 legend（line 113）与 Figure 3 legend（line 114）均写 "S (same sub-organ)"。Tabula Muris/Sapiens 均无 "sub-organ" 概念，此定义不可能产生 n=4 的 S 类。此外 Figure 2 自身内部矛盾：panel (A) 写 "C category: random split of same population"（即 control），panel (B) 却写 "C (same cell type)"——同一图两个面板对 C 的定义不同。正文中的四个类别实为 controls、S（同细胞型跨器官）、D（同器官异细胞型）、X（cross-organ），与图注的 C/S/D/X 命名体系不对应。
- **位置**：manuscript `CKI_NAR_Manuscript_full_extract.txt` line 113、114 vs line 51、53、57。
- **建议**：统一四类别命名与定义（建议 C=control/random split，S=same cell type across organs，D=different cell type within same organ，X=different cell type across organs），并同步修改 Fig 2B/Fig 3D 图注；若图内确实使用了不同定义，需说明图所用类别的样本构成。

### C2. Supplementary Figure S7 (B) 图注 "OPCs (0 Strong...)" 与正文 "OPCs contributed 27 Strong candidates" 直接矛盾
- **问题**：Fig S7 图注（manuscript line 125）仍写 "OPCs (0 Strong despite highest motility among the 10 non-neuronal classes) provide a key internal consistency check, supporting that the model detects developmental-origin signatures rather than general motility"；而正文 Results（line 80-82）明确 "OPCs contributed 27 Strong candidates (16 with raw P < 0.05)" 且 OPC 是最大贡献者（27/55，约 2.7 倍于其 pair 占比预期）。这是 v5 旧叙事（OPC 0 Strong）的残留；图注与正文结论相反，且 "internal consistency check" 论证在新结果下已逻辑反转（高运动性的 OPC 贡献最多候选，恰与旧图注的论证相反）。由于 Fig S7B 是按 "current CSV outputs" 重生成的柱状图（MANIFEST 声明），图内柱状数据很可能已显示 OPC=27，图注与图面本身也会冲突。
- **位置**：manuscript line 125；正文对照 line 80-82、87。
- **建议**：将 S7B 图注改写为新结果："OPCs contributed 27 of 55 Strong candidates (16 with raw P < 0.05), consistent with their documented perivascular migration and surveillance behavior"；同时删除/改写 "detects developmental-origin signatures rather than general motility" 这一因果断言（正文 line 78 已明确 mechanism assignment 是 literature-guided interpretation）。

### C3. BH-FDR 引用错配：Benjamini-Hochberg FDR 挂靠 Storey & Tibshirani 2003，规范的 Benjamini & Hochberg 1995 缺失
- **问题**：Methods "Statistical reporting" 段写 "Benjamini-Hochberg FDR correction is applied within each dataset to control the false discovery rate (23)"，而参考文献 #23 是 Storey & Tibshirani (2003)（q-value 方法，PNAS），并非 BH 方法。全文参考文献列表中无 Benjamini & Hochberg 1995（J. R. Stat. Soc. Ser. B, 57, 289–300）。这是引用与方法错配 + 规范方法学引用缺失，属引用完整性硬伤；BH-FDR 是本文脑区分析（m=31,764）的核心统计步骤，编辑与统计审稿人必查。
- **位置**：manuscript line 41（正文引用点）；line 155（ref 23）；参考文献列表缺 BH 1995。
- **建议**：将 FDR 方法引用改为 Benjamini & Hochberg (1995)（并给出完整条目）；如确需引用 q-value 框架，另文补充，但不可再以 Storey & Tibshirani 支撑 BH 步骤。同时全文检索是否有其他以 (23) 引用的语境需要同步修正。

### C4. Data availability 声明与投稿包实际内容不符（"All analysis notebooks and processed data matrices are included in the Supplementary Data"）
- **问题**：Data availability（manuscript line 100）声明 "All analysis notebooks and processed data matrices are included in the Supplementary Data"；但 v35 投稿包（`version3/CKI_NAR_Submission_v35/`，已逐一核对）仅含 DOCX（Manuscript/Supplementary/Cover Letter/Reproducibility Guide/Table1-2）、figure1-6.pdf、Supplementary_Figure_S1-S12.pdf、graphical abstract 与 *_fulltext.txt，**无任何 .py/.ipynb 脚本、无 results/*.csv 数据矩阵**。补充材料 "Supplementary Data 1" 也只是脚本索引（指回 GitHub），未随包提供文件。NAR 的 "Supplementary Data" 指随稿上传的补充文件；声明与实际不符，若编辑抽查会直接构成 compliance 问题。
- **位置**：manuscript line 100；投稿包目录核对结果（find 输出，30 个文件无代码/数据）；Reproducibility Guide 引用的 `results/phase32_sweep_results.csv`、`results/brain_siletti_omega_pairs_v3.csv` 等（guide line 90、94-96）均不在包内。
- **建议**：（1）将声明改为 "All analysis notebooks and processed data matrices are available in the GitHub repository and Zenodo archive (links)"，删除 "included in the Supplementary Data"；（2）更稳妥的做法是将关键 processed data matrices（如 brain 31,764 pairs、human pairs、phaseC/phaseB 结果 CSV）作为真正的 Supplementary Data 文件随稿上传；（3）Data availability 中 "collection ID as referenced in (11)"（line 100）应直接给出 Methods 中的 collection ID（283d65eb-2f53-46e9-a951-0da342e3d1f2）。

### C5. Methods "Statistical reporting" 与脑区 FDR 检验数表述自相矛盾（10 cell types vs m=31,764；corrected vs unadjusted）
- **问题**：三处表述相互冲突：
  - Methods "Statistical reporting"（line 41）："The number of tests is determined by the number of cell types (10 for brain, 17 for human per-cell-type, 15 for mouse), **not the number of region pairs**"，并称 "minimum resolvable P-value 9.99×10⁻⁴ ... well below the BH threshold ... (brain: 1.0×10⁻³, at the resolution limit)"。
  - Methods "Multiplicative residual model"（line 35）："Benjamini-Hochberg FDR correction was applied across all m = 31,764 pairs. No pair reached q < 0.05 (minimum q = 0.949)"。
  - Results（line 80）与 Discussion（line 94）同样写明跨 m=31,764 校正。
  - 此外 Limitation Sixth（line 95）写 "residual model: m = 31,764 **for unadjusted permutation P-values**"，与 line 35/80 的 "BH applied across m=31,764" 正面冲突。
- 若 line 41 的 "10 for brain" 指 bootstrap 细胞类水平检验（line 74 的 9/10 类显著），line 41 的措辞仍会误导读者认为脑区 FDR 全部基于 m=10；且当 m=31,764 时，B=1,000 的最小可解 P（9.99×10⁻⁴）远高于 BH 临界（约 α/m≈1.6×10⁻⁶），line 41 "provides sufficient resolution for all tests" 的断言对 brain residual model 不成立。
- **位置**：manuscript line 41、35、80、94、95。
- **建议**：将 line 41 的 FDR 表述改写为区分两类检验并各自给出 m：（i）bootstrap 置换（cell-type 水平，m=10/17/15）；（ii）multiplicative residual 模型（per-pair 水平，m=31,764，BH 后 min q=0.949）。删除 "not the number of region pairs" 这一与正文其他部分冲突的句子，并修正 "sufficient resolution" 的论证（仅对 m≤17 的 bootstrap 成立）。Limitation Sixth 中 "m=31,764 for unadjusted permutation P-values" 与正文 "BH across m=31,764" 必须统一口径。

### C6. 补充材料多节仍描述已被正文明确否定的旧方法（B=10,000 per-pair shuffle）并沿用旧数字
- **问题**：
  - Supplementary Note 3.3（supplementary line 62-63）通篇描述 "cell type labels were randomly shuffled **within region pairs**, B = 10,000"，"11,541 signals (36.3%) reached the P-value floor"，"30 Strong-tier candidates，16 signals (6 astrocytes, 10 oligodendrocytes)"——这正是正文 line 87 明确否定的 anti-conservative 早期实现（"An earlier implementation of this test, which shuffled cell-type labels within each region pair (B = 10,000), produced anti-conservative P-values (36.3% of pairs at the P-value floor)"）。补充材料把被否定的方法当作正式方法呈现，与正文 Methods/Results 的方法学与结论（block-shuffle，B=1,000，55 Strong，37 raw P<0.05，min q=0.949）直接矛盾。
  - Supplementary Note 3.5（line 67）：校准后数值仍为旧值 "brain global mean ... ω_cal = 1.20 (raw 8.01)、astrocytes ... 2.15 (raw 14.36)、Bergmann glia ω_cal = 0.36"，与正文 line 54 "ω_cal = 4.88 (raw 32.56)、11.52 (raw 76.83)、1.67 (raw 11.17)" 矛盾。
  - Supplementary Note 3.7（line 71）：k_n CV=97.35%、ρ=-0.027（P=9.96×10⁻⁷），与正文 line 56/129 "CV=92.89%、ρ=0.181 (P=9.38e-232)" 矛盾。
  - Supplementary Note 1.3（line 20）与 Supplementary Table 1（line 90）：参数扫描 AUC=0.847，与正文 line 49 及 Fig S1 图注（line 119）AUC=0.786 矛盾。
  - Supplementary Table 4（line 96）：Top-5 最强候选含 3 条 Microglia（如 A14 vs Pul），而正文 line 80 明确 "microglia ... contributed none"；总数 7,943（25.0%）与其自身分解 55+2,120+6,149=8,324 也不符（8,324/31,764=26.2%）。
- **位置**：supplementary line 62-63、67、71、20、90、96。
- **建议**：将 Note 3.3 整体替换为 block-shuffle null（B=1,000）的正式描述与结果（55 Strong / 37 raw P<0.05 / min q=0.949），并注明早期 per-pair shuffle 实现为 anti-conservative、已弃用；同步更新 Note 3.5、3.7、Note 1.3、Table 1、Table 4 全部数值；Table 4 总数按 8,324 重算或与正文 tier 计数核对。

### C7. 复现指南（Supplementary Methods）关键数字与正文矛盾，无法支撑其"numerically identical results"承诺
- **问题**：复现指南自述按该指南可复现正文所有数值（guide line 266），但其内含 v5 旧值：
  - 人 Tabula Sapiens "all 5,151 cell-type pairs"（guide line 101-102）vs 正文 4,851 对；
  - k_n CV=97.35%、mean=0.0141、Spearman ρ=-0.027（guide line 71、180、259）vs 正文 CV=92.89%、ρ=0.181；
  - μ_grand=8.01（guide line 135）vs 正文 32.56；
  - 校准数值 "8.01→1.20、14.36→2.15、2.37→0.36"（guide line 174）vs 正文 32.56→4.88、76.83→11.52、11.17→1.67；
  - residual null 为 per-pair shuffle、30 Strong/16 signals/36.3% floor（guide line 166）vs 正文 block-shuffle、55/37/0；
  - 指南 §7 复现检查清单同样要求验证 CV=97.35%（guide line 259），与正文数字相反。
- **位置**：guide line 71、101-102、135、166、174、180、259；正文对照 line 56、57、79、80、129。
- **建议**：复现指南必须整体按 v35 softmax 结果重新生成，删除全部 97.35%/-0.027/8.01/14.36/30 Strong/5,151 等旧值；尤其 §7 检查清单中凡与正文冲突的项（CV、候选数、对计数）需逐一核对。指南与主稿数值不一致会被审稿人视为复现性声明不成立。

### C8. 投稿信关键结果数字严重过期，与正文直接冲突
- **问题**：Cover Letter line 18 三处关键数值/结论与正文矛盾：
  - "Spearman r = −0.57 to −0.38" vs 正文/摘要 "−0.36 to −0.46"；
  - "median NN/TT ratio 1.40–2.83" vs 正文 line 63 五癌种范围 1.23（LIHC）–2.32（LUAD）；
  - "brain regional analysis identifying **30 threshold-passing candidates (16 statistically significant)**" vs 正文 line 80 "55 Strong、37 raw P<0.05、BH 后 0 个显著（min q=0.949）"——"16 statistically significant" 与正文核心结论（无候选通过 FDR）正面冲突。
- **位置**：`CKI_NAR_Cover_Letter_full_extract.txt` line 18。
- **建议**：按 v35 正文重写该段：r 范围、NN/TT 范围、脑区 55 Strong / 37 raw P<0.05 / none FDR-significant / hypothesis-generating。投稿信是编辑对稿件的第一印象，与正文矛盾的数值（尤其统计结论方向）会直接触发对稿件严谨性的质疑。

---

## 三、Major（10 项）

### M1. 人类对计数跨文档矛盾，且与 "102 cell types" 算术不自洽
- 正文 Methods/Results/Table 1/Fig 3 图注均写 4,851 对（manuscript line 33、57、58、59、114），但正文自称 102 cell-type entries（line 29），102×101/2=5,151 ≠ 4,851（4,851=99×98/2）。补充材料 Note 3.3、复现指南 §4.2、MANIFEST 均写 5,151。需核对真实对计数：若确实只分析 99 类，则正文 cell-type 数应为 99；若 102 类，则应 5,151。数字高似换位笔误，但涉及关键结果规模，必须查清后全包统一。

### M2. 人类段落 mouse 比较基准 27.31 无来源定义且比较基础不恰当
- Results line 57 "Human ω ... substantively lower than mouse (mean 27.31)"——27.31 在正文/图/表中均未定义其出处与样本构成（依 v5 记录为 mouse pilot X 类别，n=2），用 n=2 的均值与 n=4,851 的均值直接比较并作结论性陈述不妥。建议：明示 27.31 的来源与 n，或改用可比的基准（如 mouse pilot 全部 15 对均值/中位数），并将"substantively lower"弱化为受计算方案差异影响的定性比较（该句后半段已自述方案差异，前半句断言需与之后解释对齐）。

### M3. 摘要 "a human brain single-nucleus atlas from millions of cells" 与实际分析规模不符
- 实际分析为 Nonneurons.h5ad 888,263 核（过滤后 886,808），全图谱 ~3.3M。摘要措辞暗示分析对象为百万级，量级与 0.89M 相差约 3.7 倍。建议改为 "a human brain single-nucleus atlas (888,263 non-neuronal nuclei)"，在 200 词额度内给出实际样本量。

### M4. 稿件内缺 AI 使用声明（OUP/NAR 合规）
- NAR（OUP）政策要求在稿件文本内（Acknowledgements 或独立声明）披露 LLM/AI 写作辅助的使用。本稿 Acknowledgements（line 103-104）无 AI 声明；AI 声明仅出现在投稿信（cover letter line 19）。需在稿件内补入与投稿信一致的声明（"AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors, who take full responsibility"）。

### M5. 正文/复现指南引用的 "Fig. 2 heatmap"（703 pairs 全对矩阵）未出现在 Figure 2 图注面板描述中
- 正文 line 51/57 与指南 §3.2 均称全对矩阵（703 pairs, global HVG 2000）为 "Fig. 2 heatmap"；但 Figure 2 图注（line 113）仅列出 A-D 四个面板（k_n calibration / component decomposition / Spearman correlations / pathway enrichment），无 703-pair heatmap 面板。需在图注中补充该面板说明，或确认热图所在图号并更正正文/指南引用。

### M6. Limitations 编号虽连续（First–Twenty-first），但 Third 与 Fourth 之间插入两条非编号项
- line 95 在 "Third, ..." 后紧跟 "A further concern is the circular dependency..." 与 "Additionally, housekeeping gene expression may be dysregulated in cancer (47)..." 两条未编号内容，再续 "Fourth, ..."。编号本身无跳跃（1–21 连续，Sixteenth–Twenty-first 均在），但并行结构被打断，读者难以判断这两条属于 Third 的延伸还是独立限制。建议将两条并入 Third 的叙述或各自编号。

### M7. 置换检验描述在主稿正文重复 3 次，冗余明显
- 相同内容（B=1,000、one-sided P=(count+1)/(B+1)、SES 公式、BH-FDR within dataset）在 Methods "Bootstrap permutation test"（line 26）、Methods "Statistical reporting"（line 41）、Results Step 3（line 48）三处近乎逐字重复，另在 Statistical conventions（line 131）再次概括。NAR 注重篇幅效率，建议 Results Step 3 仅作一句回指（"as described in Methods"），Statistical reporting 保留完整但删去与 Bootstrap permutation test 段重复的公式推导。

### M8. 作者单位跨文档不一致
- 稿件 title page：Wu=1(CIBR), Zhang=1,2(CIBR, IBT)，且排版为 "Li Zhang12*"（缺逗号，应为 "Li Zhang1,2*"）；投稿信作者块 Zhang 地址先 IBT 后 CIBR；复现指南署名 "Xianming Wu1, Li Zhang1,2,*" 且 1=Institute of Blood Transfusion, 2=CIBR——即指南把 Wu 归入 IBT，稿件/投稿信把 Wu 归入 CIBR，Zhang 的单位顺序也相反。需统一三份文档的署名、单位编号与顺序，并核实 Wu 的真实单位。

### M9. 软件版本号待澄清（v0.3.1 vs v0.3.2）
- 稿件（line 98、100）、投稿信、复现指南（§1.2）均声明 v0.3.1 与 Zenodo DOI 10.5281/zenodo.15670808；但 v35 构建说明提及 v0.3.2 修复 cki/core.py（恢复 log2 JS + kn_min=1e-4 clamp，与 Methods 一致）。若本次所有分析运行于含修复的 v0.3.2，则文中版本号、GitHub tag 与 Zenodo DOI 均须更新并注明具体提交；若运行于 v0.3.1，则需说明 v0.3.2 修复不影响已报告数值。版本声明与实际分析代码不一致会构成复现性问题。

### M10. 摘要 199 词，紧贴 NAR 200 词上限
- 摘要（manuscript line 11）实测 199 词。任何一轮修改（含 M3 建议的样本量补充）都可能超限；建议改稿时预留余量（如精简开头两句），并以目标字数 190–195 为安全区间。

---

## 四、Minor（15 项）

1. **"6.9-fold" vs "6.88-fold" 精度不统一**：摘要（line 11）写 6.9-fold，正文（line 73、94）与 Figure 6B 图注（line 117）写 6.88-fold；另 MANIFEST 写 6.28-fold（见 C7，独立问题）。建议全文统一为 6.88。
2. **参考文献 #41（Tan et al. 2020）悬空**：正文全文无 "(41)" 引用点（已程序化核对），该条目出现在参考文献列表（line 173）。建议在 microglia 段落（line 75）引用之，或删除该条目。
3. **引用编号未严格按出现顺序**：ref 34 首次出现在 line 75，refs 31–33 首次出现在 line 78（晚于 34）；line 86 先出现 "(28,30)" 后出现 "(29)"。NAR 要求按正文首次出现顺序编号，需重排 29–34 之间的编号并全文同步。
4. **ref 47（Butte et al. 2001）支撑 "housekeeping gene expression may be dysregulated in cancer" 不匹配**：Butte 2001 是 HK 基因定义文献，并非癌症中 HK 失调的证据；建议替换为支持 HK 在肿瘤中失调的文献。
5. **ref 24（Wälchli 2024，脑血管图谱）支撑 "endothelial cells express organ-specific gene programs" 较弱**：建议补充或改引更直接支持器官特异性内皮程序的文献。
6. **ref 47 页码连字符**："95-96" 应为 en-dash "95–96"（NAR 格式）。
7. **"OPCs" 缩写先于定义使用**：line 80 首次出现 "OPCs"，line 82 才展开 "Oligodendrocyte precursor cells (OPCs)"；建议在 line 80 首次出现处展开。
8. **脑区缩写未展开/无对照表**：TF、MTG、MN、MoAN、PB、RN、SEP、SI、A13、A19、LEC、PAG、Idg、GPe、GPi、A1C、A24、A5/A7、CA2U-CA3U、MoRF、MoEN/MoSR 等（line 82-86）无全称或映射表；建议在补充材料加一张 region code 对照表。
9. **常见缩写首用未展开**：TCGA（line 30）、ROC（line 33）、AUC（line 49）、CV（line 52）、IQR（line 40）、DE（line 93 单用）、MSigDB（line 100）。TCGA/MSigDB 至少在首次出现时给全称。
10. **"Li Zhang12*" 排版**（line 3）：应为 "Li Zhang1,2*"。
11. **第一作者 Xianming Wu 缺 ORCID**：仅 Li Zhang 提供 ORCID（line 7），NAR 建议所有作者提供 ORCID，至少第一作者应补。
12. **"Graphical Abstract" 段**（line 8-9）：NAR 无 graphical abstract 栏目；该占位行建议删除或与 NAR 编辑确认，避免非标准元素。
13. **Fig 2D "Pathway enrichment in the k_f component" 与正文 w_pathway=0 结论的叙事张力**：正文 line 49 结论为 identity-only 最优（w_pathway=0），图 2D/Fig S1B 展示 pathway 相关结果易使读者困惑；建议图注注明该面板为参数扫描（未采纳配置）的证据。
14. **稿件保留 "confirmed baseline behavior" 强断言**：line 52 "The calibration confirmed correct baseline behavior" 与 Fig 2A "confirming constrained baseline behavior"（line 113）。上一轮已从投稿信删除 "confirmed baseline behavior"（改为 empirical baseline），但稿件/图注未同步弱化；鉴于 n=6、CV≈52%，建议改为 "consistent with baseline behavior"（本段后文已有同等限定，删掉首句强断言即可）。
15. **审稿人邮箱疑似笔误**：cover letter 建议审稿人 Joshua Welch 邮箱写 "jdwlch@umich.edu"（line 20），疑为 "jdwelch@umich.edu"（漏字母 e）；投寄前请核实全部建议审稿人邮箱。

---

## 五、投稿包卫生检查（专项结论）

- **MANIFEST 声明与实际文件一致性**：文件级一致 ✓（30 个文件全部与 MANIFEST Contents 对应，无多余、无缺失；含 *_fulltext.txt 提取件）。
- **脏文件**：无 ~$ 锁文件、无 .DS_Store、无 __MACOSX 目录 ✓。
- **文件名规范**：figure1-6.pdf、Supplementary_Figure_S1–S12.pdf 命名规范、大小写统一 ✓。
- **MANIFEST 描述性内容问题（独立于文件一致性）**：MANIFEST "v35 Changes" 段（line 10-13）内含与最终主稿矛盾的数值——"Human Tabula Sapiens: n = 5,151 pairs, mean omega = 21.48, median = 19.58"（主稿 4,851/21.61/19.65）、"Brain Siletti atlas: 6.28-fold gradient, Bergmann glia = 16.4, astrocyte = 103.1"（主稿 6.88/11.17/76.83）。MANIFEST 非投稿文件，但说明打包管线未做最终一致性校验；建议修包时同步更正 MANIFEST 或注明其数字快照时间，避免未来版本混淆。

---

## 六、引用检查专项小结

- 参考文献 47 条，正文引用点覆盖 1–47 号（缺 41 号悬空，见 Minor 2）；无超出 47 号之外的引用编号。
- 引用顺序违规 2 处（Minor 3）。
- **FDR 相关引用错配 1 处（C3）**：BH-FDR 唯一挂靠点为 ref 23（Storey & Tibshirani 2003），规范文献 Benjamini & Hochberg 1995 全稿缺失。
- **AI 使用声明**：仅投稿信有（cover letter line 19），稿件内缺失（M4）。
- **"All analysis notebooks ... included in the Supplementary Data" 声明**：与投稿包内容不符（C4）。
- 其余引用与内容匹配度总体合格（ref 9/10 仅以 LUAD/BRCA 支撑 "TCGA data" 属可接受范围；ref 44 Bakken 2021 用于 cross-species validation 语境合理）。

---

## 七、已妥善解决的上一轮项（v5→v35 确认落实）

以下项在**主稿正文层**已正确落实，无需再改（但注意 C6/C7 指出配套文档未同步）：

1. **softmax 归一化全尺度统一**：Methods "CKI computation"（line 22）明确 softmax 概率归一化 + base-2 对数（范围 [0,1]）+ k_n floor；Statistical conventions（line 131）统一声明 "All analyses use JS divergence with base-2 logarithm"；正文无残留 L1/L2 旧法描述 ✓。
2. **脑区 block-shuffle null 重算**：Methods（line 35）、Results（line 80）、Discussion（line 94）、Figure 6D 图注（line 117）、Fig S9 图注（line 127）在 55 Strong / 37 raw P<0.05 / min q=0.949 / hypothesis-generating 口径上完全一致；anti-conservative 旧 per-pair shuffle 被明确标注为弃用实现（line 87）✓。
3. **人类 phase35 重跑**：正文 21.61/19.65/4,851、AUC 0.680（第 5）、r −0.36~−0.46，与 Table 1、Fig 3 图注、摘要一致 ✓（跨文档 5,151 问题见 M1）。
4. **phaseB/C 升级**：CV=92.89%、Spearman ρ=0.181 在正文（line 56）、Fig S11 图注（line 129）、Limitation Twelfth（line 95）一致 ✓。
5. **TCGA k_n floor 说明**：Discussion（line 93）与 Limitation Twentieth（line 97）的 3.0×10⁻⁵–1.9×10⁻⁴、3/5 触及 floor 表述一致 ✓。
6. **cross-organ 新值**：15.83/24.87/20.80 在 Results（line 57、60）一致，且与 59 对/1,038 对计数吻合 ✓。
7. **上一轮写作类修改**：one-sided 检验方向论证（Methods line 26）✓；跨器官 n<5 提示（Results line 69）✓；TCGA 配对比较去 P 值（Results line 64）✓；图注统计约定段（line 131）✓；投稿信已移除 "orthogonal" 与 "confirmed baseline behavior" ✓（但稿件内仍残留，见 Minor 14）。
8. **Limitations 编号连续**：First–Twenty-first 无跳跃（C6/M6 涉及的仅是非编号项插入问题）✓。
9. **Limitations 内容与正文统计结果一致**：Sixth/Eighth/Sixteenth 均写 55 Strong、37 raw P<0.05、min q=0.949、BH 跨 m=31,764 ✓（其内部 "unadjusted" 措辞冲突见 C5）。

---

## 八、审稿建议摘要

主稿正文质量已接近 NAR 可送审水平，但配套文档（补充材料、复现指南、投稿信、MANIFEST）的 v5 残留与正文冲突、FDR 引用错配、Data availability 声明不实、稿件内缺 AI 声明，构成系统性 submission-readiness 风险。建议按上述 C1–C8 全部修正、M1–M10 处理后再提交；其中 C3（引用完整性）、C4（数据可用性声明）、C6/C7（文档间矛盾）是 NAR 审稿流程中最可能被编辑直接拦截的项。
