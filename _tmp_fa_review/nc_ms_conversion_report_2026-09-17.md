# CKI 文稿 GB→NC 生成器改造报告（nc-ms）

- 日期：2026-09-17
- 实施脚本：`_tmp_fa_review/build_nc_ms.py`（含全部锚点断言）
- 产出生成器：`generate_manuscript_nc.py`（py_compile 通过，运行成功）
- 产出文稿：`results/CKI_Manuscript_NC.docx`
- 验证脚本：`_tmp_fa_review/verify_nc_ms.py`（python-docx 全文提取自检）
- **自检结果：85 项通过，0 项失败**

## 一、各项改造替换计数

| 改造项 | 计数 |
|---|---|
| 结构：Background→Introduction 标题 | 1 |
| 结构：删除 Conclusions 标题行（段落并入 Discussion 末） | 1 |
| 结构：删除 Keywords 块 | 1 |
| 结构：删除 List of abbreviations 块 | 1 |
| 结构：删除 Declarations/Ethics/Consent 块 | 1 |
| 结构：删除 Additional files 块（改写为 SI 描述段） | 1 |
| 结构：删除附图图例标题（附图图注并入 Figure legends 节） | 1 |
| 结构：删除旧 References 循环（移至 Code availability 之后） | 1 |
| 标题页：去冒号新标题（11 词） | 1 |
| Abstract：151→149 词 | 1 |
| Results：删除 L3 小节标题 | 3 |
| Discussion：删除 L2 小节标题 | 3 |
| Methods：Statistical reporting→Statistics and reproducibility（含正文交叉引用 1 处） | 2 |
| 正文残留 'Background' 引用→Introduction | 1 |
| 命名：'Additional file 1: Fig. Sx'→'Supplementary Fig. x' | 17 |
| 命名：裸 'Fig. Sx'→'Supplementary Fig. x' | 1 |
| 命名：图注 'Additional file 1: Figure Sx.'→'Supplementary Fig. x.' | 13 |
| 命名：'Additional file 1: Table Sx'→'Supplementary Table x' | 4 |
| 命名：'Additional file 1: Note x.y'→'Supplementary Note 新号'（前缀式） | 36 |
| 命名：裸 'Note x.y'→'Supplementary Note 新号' | 2 |
| 命名：'in Additional file 1.'→'in the Supplementary Information.' | 3 |
| 命名：Additional file 2→'Additional file 2: Reproducibility Guide' | 1 |
| 面板标签：(A)-(E)→(a)-(e) | 41 |
| 面板标签：Fig. 2A/2B/2C→小写（含 'Fig. 2B, C'→'Fig. 2b, c'） | 3 |
| 面板标签：Panel A/B→panel a/b | 2 |
| 参考文献：56 条 Nature 化（含 6 条六作者截断、书籍/团体作者套新框架） | 56 |
| 正文引用：72 组 [n] → 上标 69 组（3 组随 Data/Code availability 去引用删除） | 69 |
| p() 函数：引用上标化改造（CI 方括号守卫） | 1 |
| ref_p_nar→ref_p_nc：期刊斜体/卷号加粗 run 拆分 | 1 |
| 保存路径→results/CKI_Manuscript_NC.docx | 1 |
| 第二轮：Introduction 末段 'Here, we show' 改写 | 1 |
| 第二轮：Results 超长 L2 标题缩短 ≤60 字符 | 5 |
| 第二轮：悬空交叉引用改写（指向已删小节） | 3 |

Supplementary Note 旧→新映射（引用次数）：3.12→1(5), 3.21→2(4), 3.5→3(2), 3.20→4(1), 3.22→5(2), 3.15→6(2), 3.13→7(2), 5.2→8(2), 3.16→9(6), 3.17→10(2), 3.14→11(2), 4.6→12(3), 5.1→13(3), 3.23→14(1), 3.6→15(1)，合计 38。

## 二、DOCX 自检明细

| 检查项 | 结果 | 细节 |
|---|---|---|
| 一级标题顺序 = NC 固定顺序 | PASS | CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics / Abstract / Introduction / Resu |
| 全文无 'Keywords:' | PASS | count=0 |
| 无 Conclusions 标题 | PASS | headings named Conclusions=0 |
| 全文无 'List of abbreviations' | PASS | count=0 |
| 无 Declarations 标题 | PASS |  |
| 全文无 'Additional file 1' | PASS | count=0 |
| 全文无 'Fig. S' | PASS | count=0 |
| 全文无 'Table S' | PASS | count=0 |
| 全文无 'Additional file 1:' | PASS | count=0 |
| 全文无 'heading('Background'' | PASS | count=0 |
| 全文无 'Statistical reporting' | PASS | count=0 |
| 全文无 'Panel A' | PASS | count=0 |
| 全文无 'Panel B' | PASS | count=0 |
| 全文无 'Fig. 2A' | PASS | count=0 |
| 全文无 'Fig. 2B' | PASS | count=0 |
| 全文无 'Fig. 2C' | PASS | count=0 |
| 全文无 '(A)' | PASS | count=0 |
| 全文无 '(B)' | PASS | count=0 |
| 全文无 '(C)' | PASS | count=0 |
| 全文无 '(D)' | PASS | count=0 |
| 全文无 '(E)' | PASS | count=0 |
| 无 Background 标题 | PASS | headings named Background=0 |
| 无 'Note 3.' / 'Note 4.' / 'Note 5.' 残留 | PASS | matches=[] |
| Abstract <=150 词 | PASS | 149 words |
| 标题无冒号 | PASS | CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics |
| 标题 <=15 词 | PASS | 11 words |
| 'Additional file' 出现 <=3 | PASS | count=2 (expect 2: Methods AF2 + SI paragraph) |
| AF2 统一命名 | PASS | count=2 |
| Supplementary Note 1 出现 | PASS | count=5 |
| Supplementary Note 2 出现 | PASS | count=4 |
| Supplementary Note 3 出现 | PASS | count=2 |
| Supplementary Note 4 出现 | PASS | count=1 |
| Supplementary Note 5 出现 | PASS | count=2 |
| Supplementary Note 6 出现 | PASS | count=2 |
| Supplementary Note 7 出现 | PASS | count=2 |
| Supplementary Note 8 出现 | PASS | count=2 |
| Supplementary Note 9 出现 | PASS | count=6 |
| Supplementary Note 10 出现 | PASS | count=2 |
| Supplementary Note 11 出现 | PASS | count=2 |
| Supplementary Note 12 出现 | PASS | count=3 |
| Supplementary Note 13 出现 | PASS | count=3 |
| Supplementary Note 14 出现 | PASS | count=1 |
| Supplementary Note 15 出现 | PASS | count=1 |
| Supplementary Note 引用总数 = 38 | PASS | count=38 |
| Supplementary Fig. 引用 = 31 (18 正文 + 13 图注) | PASS | count=31 |
| Supplementary Table 引用 = 4 | PASS | count=4 |
| [n] 方括号引用组 = 0 | PASS | citation-like=[] |
| CI 方括号保留 (>0) | PASS | int-bracket groups=2 |
| 上标 run 总数 = 77 (8 标题页 + 69 引用) | PASS | count=77 |
| Data/Code availability 内无 [n] 引用 | PASS | [] |
| Data/Code availability 内无上标 run | PASS | 0 |
| Data availability 含 GSE109774 | PASS |  |
| Code availability 含 Zenodo DOI | PASS |  |
| References 条目 = 56 | PASS | count=56 |
| 条目以 (年份). 结尾 = 55（#54 书籍条目为例外） | PASS | count=55 |
| 条目2 = Korsunsky Nature 格式 | PASS | 2. Korsunsky, I. et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat. Methods 16, 1289 |
| 条目2 期刊斜体 | PASS | italic=['Nat. Methods'] |
| 条目2 卷号加粗 | PASS | bold=['16,'] |
| 条目54 = Efron & Tibshirani 书籍格式 | PASS | 54. Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman and Hall/CRC, 1994). |
| 6 条六作者条目已截断为第 1 作者 + et al. (#4/#20/#27/#29/#37/#56) | PASS |  |
| 无 GB/Vancouver 式 '年;卷:页' 残留 | PASS | count=0 |
| 无 Heading 3 (Results L3 已删) | PASS | count=0 |
| Discussion 内无小节标题 | PASS | count=0 |
| Methods 含 'Statistics and reproducibility' | PASS |  |
| L2 小节总数 = 25 (Results 11 + Methods 14) | PASS | count=25 |
| Funding 并入 Acknowledgements 段首 | PASS | This work was supported by the National Natural Science Foundation of China (NSF |
| Competing interests 声明 | PASS | The authors declare no competing interests. |
| Supplementary Information 描述段 | PASS |  |
| 主图图注 = 6 | PASS | count=6 |
| 附图图注 = 13 | PASS | count=13 |
| 附图图注均为 'Supplementary Fig. n.' 命名 | PASS |  |
| 正文含 'Supplementary Fig. 1' | PASS |  |
| 正文含 'Fig. 2b, c' | PASS |  |
| 正文含 'panel a' | PASS |  |
| 正文引用 '(X)' 保留 | PASS |  |
| Introduction 末段以 'Here, we show' 开头 | PASS | Here, we show that CKI provides a baseline-normalized index of cell-state divergence acros |
| 全部 L2 标题 <=60 字符 | PASS | over=[] |
| 新短标题到位: Ground-truth simulation: specificity versus s | PASS |  |
| 新短标题到位: Fixed-panel ablation: robust rankings, scheme | PASS |  |
| 新短标题到位: Cancer analysis: apparent tumor homogeneity ( | PASS |  |
| 新短标题到位: Brain regional analysis reveals divergence gr | PASS |  |
| 新短标题到位: Anomalously similar pairs: a hypothesis-gener | PASS |  |
| 无悬空 '(Results; Limitations)' | PASS |  |
| 无悬空 '; Limitations)' | PASS |  |
| 'Limitations' 大写残留 = 1（仅 'Limitations replicated too' 概念句） | PASS | count=1 |

## 三、参考文献 56 条新旧对照表

| # | GB (Vancouver) | NC (Nature) |
|---|---|---|
| 1 | Regev A, Teichmann SA, Lander ES, Amit I, Benoist C, Birney E, et al. The Human Cell Atlas. Elife. 2017;6:e27041. | Regev, A. et al. The Human Cell Atlas. *eLife* **6,** e27041 (2017). |
| 2 | Korsunsky I, Millard N, Fan J, Slowikowski K, Zhang F, Wei K, et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat Methods. 2019;16:1289-96. | Korsunsky, I. et al. Fast, sensitive and accurate integration of single-cell data with Harmony. *Nat. Methods* **16,** 1289–1296 (2019). |
| 3 | Lopez R, Regier J, Cole MB, Jordan MI, Yosef N. Deep generative modeling for single-cell transcriptomics. Nat Methods. 2018;15:1053-8. | Lopez, R., Regier, J., Cole, M. B., Jordan, M. I. & Yosef, N. Deep generative modeling for single-cell transcriptomics. *Nat. Methods* **15,** 1053–1058 (2018). |
| 4 | Rosen Y, Brbic M, Roohani Y, Swanson K, Li Z, Leskovec J. Toward universal cell embeddings: integrating single-cell RNA-seq datasets across species with SATURN. Nat Methods. 2024;21:1492-500. | Rosen, Y. et al. Toward universal cell embeddings: integrating single-cell RNA-seq datasets across species with SATURN. *Nat. Methods* **21,** 1492–1500 (2024). |
| 5 | Tran HTN, Ang KS, Chevrier M, Zhang X, Lee NYS, Goh M, et al. A benchmark of batch-effect correction methods for single-cell RNA sequencing data. Genome Biol. 2020;21:12. | Tran, H. T. N. et al. A benchmark of batch-effect correction methods for single-cell RNA sequencing data. *Genome Biol.* **21,** 12 (2020). |
| 6 | Nei M, Gojobori T. Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions. Mol Biol Evol. 1986;3:418-26. | Nei, M. & Gojobori, T. Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions. *Mol. Biol. Evol.* **3,** 418–426 (1986). |
| 7 | Yang Z. PAML 4: phylogenetic analysis by maximum likelihood. Mol Biol Evol. 2007;24:1586-91. | Yang, Z. PAML 4: phylogenetic analysis by maximum likelihood. *Mol. Biol. Evol.* **24,** 1586–1591 (2007). |
| 8 | Tabula Muris Consortium. Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris. Nature. 2018;562:367-72. | Tabula Muris Consortium. Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris. *Nature* **562,** 367–372 (2018). |
| 9 | Tabula Sapiens Consortium. The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. Science. 2022;376:eabl4896. | Tabula Sapiens Consortium. The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. *Science* **376,** eabl4896 (2022). |
| 10 | Cancer Genome Atlas Research Network. Comprehensive molecular profiling of lung adenocarcinoma. Nature. 2014;511:543-50. | Cancer Genome Atlas Research Network. Comprehensive molecular profiling of lung adenocarcinoma. *Nature* **511,** 543–550 (2014). |
| 11 | Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. Nature. 2012;490:61-70. | Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. *Nature* **490,** 61–70 (2012). |
| 12 | Siletti K, Hodge R, Mossi Albiach A, Lee KW, Ding SL, Hu L, et al. Transcriptomic diversity of cell types across the adult human brain. Science. 2023;382:eadd7046. | Siletti, K. et al. Transcriptomic diversity of cell types across the adult human brain. *Science* **382,** eadd7046 (2023). |
| 13 | Hounkpe BW, Chenou F, de Lima F, De Paula EV. HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate reference transcripts by mining massive RNA-seq datasets. Nucleic Acids Res. 2021;49:D947-D955. | Hounkpe, B. W., Chenou, F., de Lima, F. & De Paula, E. V. HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate reference transcripts by mining massive RNA-seq datasets. *Nucleic Acids Res.* **49,** D947–D955 (2021). |
| 14 | Kang HM, Subramaniam M, Targ S, Nguyen M, Maliskova L, McCarthy E, et al. Multiplexed droplet single-cell RNA-sequencing using natural genetic variation. Nat Biotechnol. 2018;36:89-94. | Kang, H. M. et al. Multiplexed droplet single-cell RNA-sequencing using natural genetic variation. *Nat. Biotechnol.* **36,** 89–94 (2018). |
| 15 | Edmondson HA, Steiner PE. Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies. Cancer. 1954;7:462-503. | Edmondson, H. A. & Steiner, P. E. Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies. *Cancer* **7,** 462–503 (1954). |
| 16 | Perou CM, Sørlie T, Eisen MB, van de Rijn M, Jeffrey SS, Rees CA, et al. Molecular portraits of human breast tumours. Nature. 2000;406:747-52. | Perou, C. M. et al. Molecular portraits of human breast tumours. *Nature* **406,** 747–752 (2000). |
| 17 | Parker JS, Mullins M, Cheang MCU, Leung S, Voduc D, Vickery T, et al. Supervised risk predictor of breast cancer based on intrinsic subtypes. J Clin Oncol. 2009;27:1160-7. | Parker, J. S. et al. Supervised risk predictor of breast cancer based on intrinsic subtypes. *J. Clin. Oncol.* **27,** 1160–1167 (2009). |
| 18 | Wälchli T, Ghobrial M, Schwab ME, Takada S, Zhong H, Suntharalingham S, et al. Single-cell atlas of the human brain vasculature across development, adulthood and disease. Nature. 2024;632:603-13. | Wälchli, T. et al. Single-cell atlas of the human brain vasculature across development, adulthood and disease. *Nature* **632,** 603–613 (2024). |
| 19 | Pfau SJ, Langen UH, Fisher TM, Prakash I, Nagpurwala F, Lozoya RA, et al. Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells. Nat Neurosci. 2024;27:1892-903. | Pfau, S. J. et al. Characteristics of blood-brain barrier heterogeneity between brain regions revealed by profiling vascular and perivascular cells. *Nat. Neurosci.* **27,** 1892–1903 (2024). |
| 20 | Jones HE, Coelho-Santos V, Bonney SK, Abrams SR, Shih AY, Siegenthaler JA. Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature. Development. 2023;150:dev201805. | Jones, H. E. et al. Meningeal origins and dynamics of perivascular fibroblast development on the mouse cerebral vasculature. *Development* **150,** dev201805 (2023). |
| 21 | Tan YL, Yuan Y, Tian L. Microglial regional heterogeneity and its role in the brain. Mol Psychiatry. 2020;25:351-67. | Tan, Y. L., Yuan, Y. & Tian, L. Microglial regional heterogeneity and its role in the brain. *Mol. Psychiatry* **25,** 351–367 (2020). |
| 22 | Barry-Carroll L, Gomez-Nicola D. The molecular determinants of microglial developmental dynamics. Nat Rev Neurosci. 2024;25:414-27. | Barry-Carroll, L. & Gomez-Nicola, D. The molecular determinants of microglial developmental dynamics. *Nat. Rev. Neurosci.* **25,** 414–427 (2024). |
| 23 | Menassa DA, Muntslag TAO, Martin-Estebané M, Barry-Carroll L, Chapman MA, Adorjan I, et al. The spatiotemporal dynamics of microglia across the human lifespan. Dev Cell. 2022;57:2127-39.e6. | Menassa, D. A. et al. The spatiotemporal dynamics of microglia across the human lifespan. *Dev. Cell* **57,** 2127–2139.e6 (2022). |
| 24 | Barry-Carroll L, Greulich P, Marshall AR, Riecken K, Fehse B, Askew KE, et al. Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling. Cell Rep. 2023;42:112425. | Barry-Carroll, L. et al. Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors, following allometric scaling. *Cell Rep.* **42,** 112425 (2023). |
| 25 | Tsai HH, Niu J, Munji R, Davalos D, Chang J, Zhang H, et al. Oligodendrocyte precursors migrate along vasculature in the developing nervous system. Science. 2016;351:379-84. | Tsai, H. H. et al. Oligodendrocyte precursors migrate along vasculature in the developing nervous system. *Science* **351,** 379–384 (2016). |
| 26 | Su Y, Wang X, Yang Y, Chen L, Xia W, Hoi KK, et al. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development. Neuron. 2023;111:190-201.e8. | Su, Y. et al. Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration during development. *Neuron* **111,** 190–201.e8 (2023). |
| 27 | Foerster S, Floriddia EM, Neumann B, Agirre E, Castelo-Branco G, Franklin RJM. Developmental origin of oligodendrocytes determines their function in the adult brain. Nat Neurosci. 2024;27:1545-54. | Foerster, S. et al. Developmental origin of oligodendrocytes determines their function in the adult brain. *Nat. Neurosci.* **27,** 1545–1554 (2024). |
| 28 | Reeber SL, Arancillo M, Sillitoe RV. Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum. Cerebellum. 2018;17:392-403. | Reeber, S. L., Arancillo, M. & Sillitoe, R. V. Bergmann glia are patterned into topographic molecular zones in the developing and adult mouse cerebellum. *Cerebellum* **17,** 392–403 (2018). |
| 29 | Yang L, Zhao Z, Li Y, Wang J, Chen X, Liu Z. Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum. Cell Discov. 2024;10:22. | Yang, L. et al. Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum. *Cell Discov.* **10,** 22 (2024). |
| 30 | Zhang Y, Li D, Cai Y, Zou R, Zhang Y, Deng X, et al. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. EMBO J. 2024;43:5114-40. | Zhang, Y. et al. Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. *EMBO J.* **43,** 5114–5140 (2024). |
| 31 | Vandesompele J, De Preter K, Pattyn F, Poppe B, Van Roy N, De Paepe A, et al. Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. Genome Biol. 2002;3:RESEARCH0034. | Vandesompele, J. et al. Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. *Genome Biol.* **3,** RESEARCH0034 (2002). |
| 32 | Eisenberg E, Levanon EY. Human housekeeping genes, revisited. Trends Genet. 2013;29:569-74. | Eisenberg, E. & Levanon, E. Y. Human housekeeping genes, revisited. *Trends Genet.* **29,** 569–574 (2013). |
| 33 | Elowitz MB, Levine AJ, Siggia ED, Swain PS. Stochastic gene expression in a single cell. Science. 2002;297:1183-6. | Elowitz, M. B., Levine, A. J., Siggia, E. D. & Swain, P. S. Stochastic gene expression in a single cell. *Science* **297,** 1183–1186 (2002). |
| 34 | Newman JRS, Ghaemmaghami S, Ihmels J, Breslow DK, Noble M, DeRisi JL, et al. Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise. Nature. 2006;441:840-6. | Newman, J. R. S. et al. Single-cell proteomic analysis of S. cerevisiae reveals the architecture of biological noise. *Nature* **441,** 840–846 (2006). |
| 35 | Raj A, van Oudenaarden A. Nature, nurture, or chance: stochastic gene expression variation and its consequences on individual cellular fitness. Cell. 2008;135:216-26. | Raj, A. & van Oudenaarden, A. Nature, nurture, or chance: stochastic gene expression variation and its consequences on individual cellular fitness. *Cell* **135,** 216–226 (2008). |
| 36 | Tarashansky AJ, Musser JM, Khariton M, Li P, Arendt D, Quake SR, et al. Mapping single-cell atlases throughout Metazoa unravels cell type evolution. Elife. 2021;10:e66747. | Tarashansky, A. J. et al. Mapping single-cell atlases throughout Metazoa unravels cell type evolution. *eLife* **10,** e66747 (2021). |
| 37 | Jiang J, Li J, Huang Y, Wang Y, Chen L, Zhang X. CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions. Brief Bioinform. 2024;25:bbae283. | Jiang, J. et al. CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions. *Brief. Bioinform.* **25,** bbae283 (2024). |
| 38 | Skinnider MA, Squair JW, Kathe C, Anderson MA, Gautier M, Matson KJE, et al. Cell type prioritization in single-cell data. Nat Biotechnol. 2021;39:30-4. | Skinnider, M. A. et al. Cell type prioritization in single-cell data. *Nat. Biotechnol.* **39,** 30–34 (2021). |
| 39 | Waxman S, Wurmbach E. De-regulation of common housekeeping genes in hepatocellular carcinoma. BMC Genomics. 2007;8:243. | Waxman, S. & Wurmbach, E. De-regulation of common housekeeping genes in hepatocellular carcinoma. *BMC Genomics* **8,** 243 (2007). |
| 40 | Bakken TE, Jorstad NL, Hu Q, Lake BB, Tian W, Kalmbach BE, et al. Comparative cellular analysis of motor cortex in human, marmoset and mouse. Nature. 2021;598:111-9. | Bakken, T. E. et al. Comparative cellular analysis of motor cortex in human, marmoset and mouse. *Nature* **598,** 111–119 (2021). |
| 41 | Marques S, Zeisel A, Codeluppi S, van Bruggen D, Mendanha Falcão A, Xiao L, et al. Oligodendrocyte heterogeneity in the mouse juvenile and adult central nervous system. Science. 2016;352:1326-9. | Marques, S. et al. Oligodendrocyte heterogeneity in the mouse juvenile and adult central nervous system. *Science* **352,** 1326–1329 (2016). |
| 42 | Spitzer SO, Sitnikov S, Kamen Y, Evans KA, Kronenberg-Versteeg D, Dietmann S, et al. Oligodendrocyte progenitor cells become regionally diverse and heterogeneous with age. Neuron. 2019;101:459-71.e5. | Spitzer, S. O. et al. Oligodendrocyte progenitor cells become regionally diverse and heterogeneous with age. *Neuron* **101,** 459–471.e5 (2019). |
| 43 | Luecken MD, Theis FJ. Current best practices in single-cell RNA-seq analysis: a tutorial. Mol Syst Biol. 2019;15:e8746. | Luecken, M. D. & Theis, F. J. Current best practices in single-cell RNA-seq analysis: a tutorial. *Mol. Syst. Biol.* **15,** e8746 (2019). |
| 44 | Lin J. Divergence measures based on the Shannon entropy. IEEE Trans Inf Theory. 1991;37:145-51. | Lin, J. Divergence measures based on the Shannon entropy. *IEEE Trans. Inf. Theory* **37,** 145–151 (1991). |
| 45 | Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. J R Stat Soc Series B Stat Methodol. 1995;57:289-300. | Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J. R. Stat. Soc. Series B Stat. Methodol.* **57,** 289–300 (1995). |
| 46 | Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression data analysis. Genome Biol. 2018;19:15. | Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. *Genome Biol.* **19,** 15 (2018). |
| 47 | Hao Y, Hao S, Andersen-Nissen E, Mauck WM 3rd, Zheng S, Butler A, et al. Integrated analysis of multimodal single-cell data. Cell. 2021;184:3573-87. | Hao, Y. et al. Integrated analysis of multimodal single-cell data. *Cell* **184,** 3573–3587 (2021). |
| 48 | Hao Y, Stuart T, Kowalski MH, Choudhary S, Hoffman P, Hartman A, et al. Dictionary learning for integrative, multimodal and scalable single-cell analysis. Nat Biotechnol. 2024;42:293-304. | Hao, Y. et al. Dictionary learning for integrative, multimodal and scalable single-cell analysis. *Nat. Biotechnol.* **42,** 293–304 (2024). |
| 49 | Weinstein JN, Collisson EA, Mills GB, Shaw KR, Ozenberger BA, Ellrott K, et al. The Cancer Genome Atlas Pan-Cancer analysis project. Nat Genet. 2013;45:1113-20. | Weinstein, J. N. et al. The Cancer Genome Atlas Pan-Cancer analysis project. *Nat. Genet.* **45,** 1113–1120 (2013). |
| 50 | Colaprico A, Silva TC, Olsen C, Garofano L, Cava C, Garolini D, et al. TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. Nucleic Acids Res. 2016;44:e71. | Colaprico, A. et al. TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. *Nucleic Acids Res.* **44,** e71 (2016). |
| 51 | Cerami E, Gao J, Dogrusoz U, Gross BE, Sumer SO, Aksoy BA, et al. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. Cancer Discov. 2012;2:401-4. | Cerami, E. et al. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. *Cancer Discov.* **2,** 401–404 (2012). |
| 52 | Waskom ML. seaborn: statistical data visualization. J Open Source Softw. 2021;6:3021. | Waskom, M. L. seaborn: statistical data visualization. *J. Open Source Softw.* **6,** 3021 (2021). |
| 53 | Pedregosa F, Varoquaux G, Gramfort A, Michel V, Thirion B, Grisel O, et al. Scikit-learn: machine learning in Python. J Mach Learn Res. 2011;12:2825-30. | Pedregosa, F. et al. Scikit-learn: machine learning in Python. *J. Mach. Learn. Res.* **12,** 2825–2830 (2011). |
| 54 | Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman and Hall/CRC; 1994. | Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman and Hall/CRC, 1994). |
| 55 | CZI Cell Science Program. CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data. Nucleic Acids Res. 2025;53:D886-D900. | CZI Cell Science Program. CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data. *Nucleic Acids Res.* **53,** D886–D900 (2025). |
| 56 | Liberzon A, Birger C, Thorvaldsdóttir H, Ghandi M, Mesirov JP, Tamayo P. The Molecular Signatures Database Hallmark Gene Set Collection. Cell Syst. 2015;1:417-25. | Liberzon, A. et al. The Molecular Signatures Database Hallmark Gene Set Collection. *Cell Syst.* **1,** 417–425 (2015). |

## 四、第二轮补修（2026-09-17，team-lead 指示）

### 4.1 Introduction 末段改写（NC 惯例 'Here, we show' 开头）

- 旧：`We evaluated CKI across four scales. First, we calibrated CKI on Tabula Muris mouse data …`
- 新：`Here, we show that CKI provides a baseline-normalized index of cell-state divergence across four scales. First, we calibrated CKI on Tabula Muris mouse data …`（其余文本不动）

### 4.2 Results 超长 L2 标题缩短（≤60 字符）新旧对照

| 旧标题（字符数） | 新标题（字符数） |
|---|---|
| Ground-truth simulation dissociates specificity from sensitivity（64） | Ground-truth simulation: specificity versus sensitivity（55） |
| Fixed gene-panel ablation: rankings robust, absolute ω scheme-specific（70） | Fixed-panel ablation: robust rankings, scheme-specific ω（56） |
| Cancer analysis suggests apparent tumor homogeneity (exploratory)（65） | Cancer analysis: apparent tumor homogeneity (exploratory)（57） |
| Brain regional analysis reveals cell-type divergence gradients（62） | Brain regional analysis reveals divergence gradients（52） |
| Anomalously similar cell-type/region pairs: a hypothesis-generating screen（74） | Anomalously similar pairs: a hypothesis-generating screen（57） |

### 4.3 悬空交叉引用改写（指向已删 Discussion 小节）

| 位置 | 旧 | 新 |
|---|---|---|
| Introduction L4 段 | `(Results; Limitations)` | `(Results; limitations are addressed in the Discussion)` |
| Results（benchmarking 段） | `(operating window ~50–200 cells; Limitations)` | `(operating window ~50–200 cells; limitations are addressed in the Discussion)` |
| Discussion（confounder 段） | `RNA quality; Limitations)` | `RNA quality; limitations discussed below)` |

注：Results 模拟段 'Limitations replicated too: …' 为句首概念用法（非交叉引用），保留未动。

## 五、遗留事项（提请 team-lead 决策）

1. 正文 Intro+Results+Discussion 12,151 词、Methods 4,437 词，超 NC 指南值 5,000/3,000（nc-gap §1.4）——team-lead 已决定按现状投。
2. 图 PDF 内面板标签大小写未审计（figure1-6.pdf，nc-gap §六）——本轮不改。
3. Nature Portfolio Reporting Summary 表单——team-lead 另行处理。
4. 断言体系（verify_v40 式）中引用已删标题文本的断言需由 build 工人更新。