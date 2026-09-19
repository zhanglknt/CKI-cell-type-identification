# v49.5 参考文献交叉验证报告（xv-numbers 独立核验）

- 日期：2026-09-19
- 验证者：xv-numbers（独立、只读验证 + 写报告；未修改任何稿件/脚本；未用 git）
- 对象：`results/CKI_Manuscript_NC_fulltext.txt`（及 `results/CKI_Manuscript_NC.docx`，用于引用顺序核验）全部 56 条参考文献
- 重要前提：**未采信** v47 审计结果（`v47_refs_audit_2026-09-14.md`），全部独立重查

## 一、概要

| 维度 | 结果 |
|---|---|
| 参考文献总数 | 56 |
| 字段核验 PASS | 53 |
| **FIX（标题事实错误）** | **2**：[35]、[37] |
| FIX（页码 cosmetic） | 1：[47] 缺 `.e29` 后缀 |
| SUSPECT（无法裁决） | 0 |
| 孤儿引用（列出但正文从未引用） | **1**：[55]（CZI CELLxGENE） |
| 引用编号越界（>56） | 0 |
| 首引顺序单调递增 | **否**（3 处乱序，见第三节） |

结论：56 条文献全部真实存在且期刊/卷/页/年基本准确（无 v47 时代那种卷页级错误）；但有 **2 条标题与发表标题不符**、**1 条页码后缀不全**、**1 条孤儿引用**、**3 处首引顺序违反 NC 数字顺序规则**，投稿前建议全部修复。

## 二、方法

1. **条目提取**：`_xv495_extract_refs.py` 从 txt 第 134 行 References 节提取 56 条；与 docx 逐条比对——文献列表 docx↔txt 完全一致（`_xv495_txtdiff.py`）。
2. **字段核验（CrossRef，urllib 直查，带 User-Agent，限速 0.8s/req）**：
   - Pass 1（`_xv495_crossref.py`）：标题检索 56 条；
   - Pass 2（`_xv495_crossref2.py`）：对 24 条弱匹配用 作者+标题 检索（rows=5，词重叠打分）；
   - Pass 3（`_xv495_crossref3.py`）：对 8 条检索噪声大的用 **DOI 直查** `/works/{doi}` 裁决。
   - 核对字段：第一作者姓、作者数（et al. 规则）、标题（≥90% 模糊匹配）、期刊、年、卷、页/文章号。条目未印 DOI 不算错误（NC 格式本就不印）。
3. **WebSearch 兜底**（CrossRef 记录缺字段时）：[6]（OUP/Europe PMC）、[30]（PubMed+出版社页）、[35]（PubMed PMID 18957198）、[53]（jmlr.org 官方页面）。
4. **引用顺序核验（不采信构建断言，独立重抽）**：`_xv495_citeorder.py` 解析 docx XML 的 `vertAlign=superscript` run（NC 格式引用即上标数字），合并相邻上标为 77 个引用组，定位首引顺序；`_xv495_citectx.py` 抽取上下文段落。

## 三、全局检查（引用列表一致性）

1. **首引顺序**：实际首见序列为
   `1,2,…,14, 56, 18,19,…,54, 16,17,15` —— **非单调递增，3 处违规**：
   - [56]（Liberzon MSigDB）在 Results "Three controls bound the interpretation…"（docx 段 49）首次被引，早于 [15]–[18]；
   - [16]（Perou）、[17]（Parker）直到 Methods TCGA 数据源（docx 段 100）才首引，排在 [54] 之后；
   - [15]（Edmondson & Steiner）在同一段 100 内于 [16][17] 之后首引。
   - 根因：文献编号按旧正文顺序编制，后期正文重排（Results 控制实验提前、Methods 补引经典文献）后未重编号。NC 要求按首引顺序编号，需整体重排并重映射全部上标。
2. **孤儿引用**：[55]（CZI Cell Science Program, CZ CELLxGENE Discover, NAR 53:D886–D900, 2025）在正文中 **0 次被引**（上标提取覆盖 References 前全部 133 段；References 之后无任何上标，图例中亦无）。Data Availability 提到 "CZ CELLxGENE Discover" 处 citation 编号在 NC 转换时丢失（v45/v46 中该处为 [54]）。→ 在该提及处补挂上标 [55]，或删除此条。
3. **越界引用**：无（最大上标编号 = 56）。
4. **txt↔docx 同步**：文献列表一致。注意：今日 12:30 稿件重新生成（3,567 样本新队列），本核验基于该最新版。
5. **DOI 可解析性**：条目未印 DOI；核验中为全部 56 条定位到的 DOI 均可解析（见下表）。

## 四、56 行核销表

判定：OK = 全字段一致；FIX = 存在事实错误需改；OK* = 一致但附备注。

| # | 条目（简称） | 核验 DOI | 判定 | 备注 |
|---|---|---|---|---|
| 1 | Regev, Human Cell Atlas, eLife 6:e27041 (2017) | 10.7554/eLife.27041 | OK | 62 作者，et al. 合规 |
| 2 | Korsunsky, Harmony, Nat Methods 16:1289–1296 (2019) | 10.1038/s41592-019-0619-0 | OK | |
| 3 | Lopez, scVI, Nat Methods 15:1053–1058 (2018) | 10.1038/s41592-018-0229-2 | OK | 5 作者全列，合规 |
| 4 | Rosen, SATURN, Nat Methods 21:1492–1500 (2024) | 10.1038/s41592-024-02191-z | OK | |
| 5 | Tran, batch benchmark, Genome Biol 21:12 (2020) | 10.1186/s13059-019-1850-9 | OK | |
| 6 | Nei & Gojobori, MBE 3:418–426 (1986) | 10.1093/oxfordjournals.molbev.a040410 | OK* | CrossRef 记录缺卷/页；OUP+Europe PMC 确认 3(5):418–426 |
| 7 | Yang, PAML 4, MBE 24:1586–1591 (2007) | 10.1093/molbev/msm088 | OK | 单作者 |
| 8 | Tabula Muris Consortium, Nature 562:367–372 (2018) | 10.1038/s41586-018-0590-4 | OK | |
| 9 | Tabula Sapiens Consortium, Science 376:eabl4896 (2022) | 10.1126/science.abl4896 | OK | 检索仅命中预印本，DOI 直查确认 |
| 10 | TCGA Network, LUAD, Nature 511:543–550 (2014) | 10.1038/nature13385 | OK | |
| 11 | TCGA Network, BRCA, Nature 490:61–70 (2012) | 10.1038/nature11412 | OK | |
| 12 | Siletti, adult human brain, Science 382:eadd7046 (2023) | 10.1126/science.add7046 | OK | |
| 13 | Hounkpe, HRT Atlas, NAR 49:D947–D955 (2021) | 10.1093/nar/gkaa609 | OK | 4 作者全列，合规 |
| 14 | Kang, demuxlet, Nat Biotechnol 36:89–94 (2018) | 10.1038/nbt.4042 | OK | |
| 15 | Edmondson & Steiner, Cancer 7:462–503 (1954) | 10.1002/1097-0142(195405)7:3<462::AID-CNCR2820070308>3.0.CO;2-E | OK | |
| 16 | Perou, breast tumour portraits, Nature 406:747–752 (2000) | 10.1038/35021093 | OK | 18 作者；DOI 直查确认 |
| 17 | Parker, PAM50, JCO 27:1160–1167 (2009) | 10.1200/JCO.2008.18.1370 | OK | 20 作者 |
| 18 | Wälchli, brain vasculature atlas, Nature 632:603–613 (2024) | 10.1038/s41586-024-07493-y | OK | 37 作者 |
| 19 | Pfau, BBB heterogeneity, Nat Neurosci 27:1892–1903 (2024) | 10.1038/s41593-024-01732-1 | OK | |
| 20 | Jones, perivascular fibroblast, Development 150:dev201805 (2023) | 10.1242/dev.201805 | OK | 6 作者；DOI 直查确认 |
| 21 | Tan, microglial heterogeneity, Mol Psychiatry 25:351–367 (2020) | 10.1038/s41380-019-0373-9 | OK | 3 作者全列 |
| 22 | Barry-Carroll & Gomez-Nicola, Nat Rev Neurosci 25:414–427 (2024) | 10.1038/s41583-024-00813-0 | OK | 2 作者 |
| 23 | Menassa, microglia lifespan, Dev Cell 57:2127–2139.e6 (2022) | 10.1016/j.devcel.2022.08.006 | OK | |
| 24 | Barry-Carroll, microglia colonize, Cell Rep 42:112425 (2023) | 10.1016/j.celrep.2023.112425 | OK | |
| 25 | Tsai, OPC migration, Science 351:379–384 (2016) | 10.1126/science.aad3839 | OK | |
| 26 | Su, astrocyte endfoot, Neuron 111:190–201.e8 (2023) | 10.1016/j.neuron.2022.10.032 | OK | |
| 27 | Foerster, oligodendrocyte origin, Nat Neurosci 27:1545–1554 (2024) | 10.1038/s41593-024-01666-8 | OK | 30 作者 |
| 28 | Reeber, Bergmann glia, Cerebellum 17:392–403 (2018) | 10.1007/s12311-017-0922-0 | OK | 3 作者全列 |
| 29 | Yang, fetal cerebellum, Cell Discov 10:22 (2024) | 10.1038/s41421-024-00649-1 | OK | |
| 30 | Zhang, astrocyte allocation, EMBO J 43:5114–5140 (2024) | 10.1038/s44318-024-00218-x | OK* | CrossRef 页码字段异常（article-number "15"）；PubMed+出版社页确认 43(21):5114–5140，条目正确 |
| 31 | Vandesompele, geNorm, Genome Biol 3:RESEARCH0034 (2002) | 10.1186/gb-2002-3-7-research0034 | OK* | CrossRef 页码作 "research0034.1"；通用引用形式 RESEARCH0034，条目正确 |
| 32 | Eisenberg & Levanon, HK genes, Trends Genet 29:569–574 (2013) | 10.1016/j.tig.2013.05.010 | OK | 2 作者 |
| 33 | Elowitz, stochastic expression, Science 297:1183–1186 (2002) | 10.1126/science.1070919 | OK | 4 作者全列 |
| 34 | Newman, yeast noise, Nature 441:840–846 (2006) | 10.1038/nature04785 | OK | |
| **35** | Raj & van Oudenaarden, Cell 135:216–226 (2008) | 10.1016/j.cell.2008.09.050 | **FIX** | **标题错误**。条目作 "…stochastic gene expression **variation and its consequences on individual cellular fitness**"；CrossRef 与 PubMed（PMID 18957198）正式标题均为 "Nature, nurture, or chance: stochastic gene expression **and its consequences**"。期刊/卷/页/年/作者均正确 |
| 36 | Tarashansky, Metazoa atlases, eLife 10:e66747 (2021) | 10.7554/eLife.66747 | OK | 7 作者 |
| **37** | Jiang, CACIMAR, Brief Bioinform 25:bbae283 (2024) | 10.1093/bib/bbae283 | **FIX** | **标题被截断**。正式标题结尾还有 "**using single-cell RNA sequencing data**"（条目止于 "…and interactions"）。期刊/卷/文章号/年均正确 |
| 38 | Skinnider, CTAUMS/Augur 类, Nat Biotechnol 39:30–34 (2021) | 10.1038/s41587-020-0605-1 | OK | 14 作者 |
| 39 | Waxman & Wurmbach, HK in HCC, BMC Genomics 8:243 (2007) | 10.1186/1471-2164-8-243 | OK | 2 作者 |
| 40 | Bakken, motor cortex comparative, Nature 598:111–119 (2021) | 10.1038/s41586-021-03465-8 | OK | 106 作者；DOI 直查确认 |
| 41 | Marques, oligodendrocyte heterogeneity, Science 352:1326–1329 (2016) | 10.1126/science.aaf6463 | OK | 23 作者 |
| 42 | Spitzer, OPC ageing, Neuron 101:459–471.e5 (2019) | 10.1016/j.neuron.2018.12.020 | OK | |
| 43 | Luecken & Theis, scRNA best practices, MSB 15:e8746 (2019) | 10.15252/msb.20188746 | OK* | CrossRef 页码字段作 "MSB188746"（=文章号 e8746），条目 e8746 正确；2 作者 |
| 44 | Lin, Jensen–Shannon divergence, IEEE Trans Inf Theory 37:145–151 (1991) | 10.1109/18.61115 | OK | 单作者 |
| 45 | Benjamini & Hochberg, FDR, JRSS-B 57:289–300 (1995) | 10.1111/j.2517-6161.1995.tb02031.x | OK | 2 作者 |
| 46 | Wolf, SCANPY, Genome Biol 19:15 (2018) | 10.1186/s13059-017-1382-0 | OK | 3 作者全列 |
| **47** | Hao, Seurat v5 整合, Cell 184:3573–3587 (2021) | 10.1016/j.cell.2021.04.048 | FIX(cosmetic) | 页码缺电子页后缀，正式页码为 **3573–3587.e29**；且与本稿 [23][26][42] 自带 .eN 后缀的体例不一致。其余字段正确；25 作者 |
| 48 | Hao, dictionary learning, Nat Biotechnol 42:293–304 (2024) | 10.1038/s41587-023-01767-y | OK | |
| 49 | Weinstein, TCGA Pan-Cancer, Nat Genet 45:1113–1120 (2013) | 10.1038/ng.2764 | OK | 第一作者 Weinstein 正确（CrossRef 组作者显示 TCGA Research Network） |
| 50 | Colaprico, TCGAbiolinks, NAR 44:e71 (2016) | 10.1093/nar/gkv1507 | OK | |
| 51 | Cerami, cBioPortal, Cancer Discov 2:401–404 (2012) | 10.1158/2159-8290.CD-12-0095 | OK | |
| 52 | Waskom, seaborn, JOSS 6:3021 (2021) | 10.21105/joss.03021 | OK | 单作者 |
| 53 | Pedregosa, scikit-learn, JMLR 12:2825–2830 (2011) | （JMLR 无 DOI） | OK | CrossRef 无记录；jmlr.org 官方页+scikit-learn 官方引文确认 12:2825–2830 (2011) |
| 54 | Efron & Tibshirani, Bootstrap 专著 (1994) | 10.1201/9780429246593 | OK | 书目型条目，无 DOI 不记错 |
| 55 | CZI, CELLxGENE Discover, NAR 53:D886–D900 (2025) | 10.1093/nar/gkae1021 | OK（字段） | 字段本身正确，但**正文孤儿引用**（见第三节 2） |
| 56 | Liberzon, MSigDB Hallmark, Cell Syst 1:417–425 (2015) | 10.1016/j.cels.2015.12.004 | OK（字段） | 字段正确；但首引位置导致顺序违规（见第三节 1） |

注：上表中 [15]、[31] 等条目未逐一在三轮脚本日志中展开 DOI，均在 Pass 1 以 sim=1.0 全字段命中；[2][4][5][8][10][12][13][14][19][21][22][23][24][25][26][28][29][32][34][36][39][42][44][46][48][49][50][51][52][55][56] 同为 Pass 1 精确命中（期刊/卷/页/年全部一致）。所列 DOI 为该命中的 CrossRef 记录 DOI。

## 五、修复建议（按优先级）

1. **[35] 标题**：改为 "Nature, nurture, or chance: stochastic gene expression and its consequences."。
2. **[37] 标题**：改为 "CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions using single-cell RNA sequencing data."。
3. **[47] 页码**：3573–3587 → 3573–3587.e29（与 [23][26][42] 体例统一）。
4. **[55] 孤儿**：在 Data Availability / Methods 提及 "CZ CELLxGENE Discover" 处补引 [55]，或删条。
5. **首引顺序 3 处违规**：[56] 提前至 Results 首引位、[16][17][15] 在 Methods 才首引——需按 NC 规则按首引顺序整体重编号并重映射正文上标（影响面大，建议构建脚本内做 order-check 断言，防止再次静默漂移——v47.2 曾发生 [56] 被静默过滤的同类问题）。

## 六、过程产物（复现用）

- `_xv495_extract_refs.py` / `_xv495_refs_list.txt`：56 条提取
- `_xv495_crossref.py` / `_xv495_crossref_log.txt` / `_xv495_crossref.json`：Pass 1
- `_xv495_crossref2.py` / `_xv495_crossref2_log.txt` / `_xv495_crossref2.json`：Pass 2
- `_xv495_crossref3.py` / `_xv495_crossref3.json`：Pass 3（DOI 直查）
- `_xv495_citeorder.py` / `_xv495_citeorder_out.txt`：首引顺序
- `_xv495_citectx.py` / `_xv495_citectx_out.txt`：引用上下文
- `_xv495_sync.py` / `_xv495_txtdiff.py`：docx↔txt 同步
