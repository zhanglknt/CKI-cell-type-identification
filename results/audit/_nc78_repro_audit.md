# CKI 学生第四版（CKI_Submission_NC_fourth）复现性审计报告

日期：2026-11-11 ｜ 任务：#1190–#1193 ｜ 范围：仅审计，不修改任何稿件文件
对象：`results/audit/_nc78_student_fourth/`（学生拷入 RAR 解包，40 文件）
基线：本仓库 nc77 线（commit 67841b0，含 √α 修正）

---

## 0. 总判断（TL;DR）

**主干头条数字绝大多数可溯源至本仓库 results/ 文件（16+ 项精确命中），但学生版新增的多个分析簇缺脚本、缺数据，无法复现；五个图脚本因 104 个 SourceData 依赖全缺而完全无法重跑；文本为全面重写，不可 diff 复现、只能整体替换口径。**

四档分布：

| 档位 | 含义 | 规模 |
|---|---|---|
| A 可复现 | 数字在仓库 results/ 有精确出处 | 16+ 项头条数字（见 §2） |
| B 缺数据 | 脚本在包内、数据不在 | 5 个图脚本 ↔ 104/107 依赖缺失 |
| C 缺脚本缺数据 | 学生新分析，仓库无任何对应产物 | 8 个分析簇（见 §4） |
| D 对不上/待澄清 | 与仓库数字不一致或口径不明 | 2 项（见 §5） |

---

## 1. 审计方法

1. RAR5 用 Windows bsdtar 解包（40 文件）。
2. `_extract_docx.py` 同时提取 `w:t` 与 `m:t`（OMML 数学对象）——学生版把 Ka/Ks、ω、k_f、P 值写成公式对象，只提 w:t 会丢字（标题曾变 "a -inspired index"）。
3. 段落级 diff 失效（全面重写：MS 136KB vs nc77 79KB；Results 63.6KB vs 23.3KB；参考文献 74 vs 58），改用「关键数字计数 + Results 全文定向阅读 + 逐数字溯源」。
4. 图脚本静态依赖扫描（`_deps.py` → `figure_script_deps.txt`，107 个唯一依赖）。
5. Guide 引用文件存在性核验（173 引用，164 存在，9 缺失见 §6）。
6. 学生工作树与本仓库同源：文件命名 v44/v45/nc49–nc52 一脉相承，Guide 引用 95% 命中。

## 2. 档 A：可复现（仓库精确命中）

| 学生版数字 | 仓库出处 | 判定 |
|---|---|---|
| mouse 基线 7.70 [6.38, 9.82]（300 splits，两阶段 bootstrap B=5000） | `results/nc52_stats_baseline_twostage_bootstrap.csv`：7.6958 [6.3798, 9.8184] | ✓ 精确 |
| mouse 300 splits / rep_baseline_mean 7.696 | `results/mouse_splithalf_v44_summary.json` | ✓ |
| brain 基线 9.73 | `results/reviewer_brain_splithalf_summary.txt`：9.7261 | ✓ |
| TS 基线 7.67 | `results/reviewer_ts_splithalf_summary.txt`：7.6708 | ✓ |
| marrow B cell：AUC ω=0.80 vs k_f=0.72 | `results/groundtruth_simulation_metrics.json`：0.8042/0.7159 | ✓ |
| skin keratinocyte：0.91 vs 0.86 | `results/groundtruth_simulation_background2_metrics.json`：0.9076/0.8585 | ✓ |
| Kang 技术重复：ω 0/30、k_f 0/30、raw_js 11/30、cosine 7/30 | `results/nc49_pilot_kang_techrep.csv` | ✓ |
| IFN-β：ω AUC 0.551–0.922 vs k_f 0.743–1.00；CD14+ 0.551/0.984 | `results/nc52_stats_omega_vs_kf_realdata.csv` + `kang_ifnb_demo_summary.json` | ✓ |
| MELD AUC 0.997–1.000 | `results/competitors_v44_kang_pertype.csv`（实现于 `notebooks/101_competitors_v44.py`） | ✓ |
| microglia supercluster：21.83±7.20 vs 1.30±0.36、AUC=1.000 | `results/nc50_brain_atlas_microglia.txt` | ✓ |
| TCGA LUAD：KRAS 136.9/WT 115.4/EGFR 122.2、KW P=7.8e-7 | `results/nc49_tcga_luad_mutation.csv` | ✓ |
| 脑 31,764 对、q_min=0.520、零 FDR 存活 | `results/brain_bs_null_fdr_manifest.json` | ✓ |
| block-shuffle P=0.001/0.014/0.163、SES 7.2；59.3–64.2 vs 24.5；3.66/3.28 [1.92,3.78]；148.3/3.8×/P=1.0 | `results/CKI_Manuscript_NC_fulltext.txt`（nc77）与 SI 全文命中 | ✓ |
| 脑 gradient reps 3.66 | `results/nc52_brain_combined_equaln_spanmatch.csv`（3.63–3.71） | ✓ |
| brain gradient_full 6.10 | `results/brain_v44_run_metadata.json`（6.1046） | ✓ |
| CT 级 ρ(ω,k_f)=0.23 [−0.08, 0.38] | `results/cross_organ_rho_ci_v44.csv`：0.2328 [−0.083, 0.382] | ✓ |
| 5,151 pairs（TS）/ 4,851 pairs（四度量相关） | `phase33_v3_human_pairs.csv` / `phase35_all_metrics_pairs.csv` 行数 | ✓（两口径，非混用） |
| TS 跨器官同细胞型 macrophage：heart–bone marrow 4.50/liver–heart 5.70/heart–lung 5.74 | 仓库 TS 对表精确一致 | ✓ |

**√α 修正继承确认**：学生 SI 含 "The √α factor follows from…"、"λ2Ef > αEb … α appears for the same measure-matching reason"、"0.12–4.76 times"、"10–83% ratio deflation"、"Five of six cell types"——nc77 修正已被学生版完整继承（√ 符号丢失为 OMML 线性化提取伪像，原文有根号）。

**口径升级（非矛盾）**：学生版校准基线 mouse 7.70/brain 9.73/TS 7.67 取代 nc77 的 6.67/14/8.5，系同实验升级统计口径（两阶段 bootstrap + 300 splits），仓库新文件可溯源。

## 3. 档 B：缺数据（脚本在、数据缺）

学生包含 figure2.py（1,705 行）/figure3.py（1,090 行）/figure4.py（534 行）/figure5.py（2,296 行）/figure_export.py（63 行）。

静态扫描得 **107 个唯一依赖，仅 3 个存在（学生自己的输出 Figure3/4/5.png），104 个全部缺失**。全部指向包内不存在的 `SourceData/FigureN/` 目录树，例如：

- `SourceData/Figure2/`（`DATA = PACKAGE/'SourceData/Figure2'`）
- `SourceData/Figure3/` 下 `cna_hk_relation_20261102`、`cna_reconstruction_20261103`、`identity_followup_20261103` 等
- `brain_CKI_J1000_pairs.csv` / `brain_CKI_J1000_summary.csv`
- `LODO_holdout_summary.csv`、`TT_NN_effects.csv`、`cnv_recovery/analysis_summary.json`、`cohort_pooling_20261103/*`

**结论：五张主图全部无法重跑。** 修复路径：向学生索取完整 SourceData 目录树（或其生成脚本）。

## 4. 档 C：缺脚本缺数据（学生新分析簇，仓库无对应产物）

| 分析簇 | 学生版关键数字 | 仓库状态 |
|---|---|---|
| GSE31210 / GSE72094 / GSE131907 / A549 外部队列 | ω 增量诚实阴性：GSE72094 AUC 0.538/0.507 | 脚本、结果全缺（Guide 引用 `results/figure3_followup_20261027/tcga_incremental/GSE72094/` 不存在） |
| brain K=1000（J1000） | T1/T2 31.61%/40.63%/92.93%/98.35% | `brain_CKI_J1000_*` 全缺 |
| Lawlor 混合基准 | lawlor_mixture_performance.csv | 缺 |
| 3-module-seed 模拟派生统计 | CI [0.78, 0.83]、ΔAUC 0.088/0.049、DeLong；**单调性 ρ=0.752** | 仓库仅 theory_diagnostics.md 的 ρ=0.688（旧设计）；0.752 无出处（已排除 nonhk_drift_v45.json 0.7526 假命中——那是 cosine FPR 的 CI 上限） |
| CNA（copy-number alteration） | `cna_hk_relation_20261102`、`cna_reconstruction_20261103` | 全缺 |
| identity_followup / matched-subset GM 分解 | 1.73/1.75/1.008 等 | 全缺 |
| Reactome/GO module 分析 | 8,720 tests、0.0534 等 | 全缺 |
| MRR retrieval | 0.304/0.406/0.430 | 全缺 |

## 5. 档 D：对不上 / 待澄清

1. **TS 跨器官同细胞型对数：学生报 59 对，仓库为 60 对**。逐对数值（4.50/5.70/5.74 等）精确一致，差异为学生侧某条过滤口径，需学生澄清。
2. **ρ=0.752 单调性**（见 §4）：仓库仅 0.688，学生新模拟设计的产物缺失，无法判定 0.752 正确性。

## 6. Reproducibility Guide 引用完整性

Guide（130,774 B 提取文本）共引用 **173 个 results/ 文件，164 个存在（~95%）**，9 个缺失：

1. `results/human_bootstrap_results.csv`
2. `results/nc49_pilot_lihc_cox.csv`
3. `results/nc49_tcga_pancancer.csv`
4. `results/nc52_brain_gradient_donor_bootstrap.csv/.json`
5. `results/nc52_stats_baseline_twostage_bootstrap.csv/.json`（注：.csv 实际存在，.json 缺——清单按引用条目计）
6. `results/nc52_tcga_composition_excc.csv/.txt`
7. `results/nc52_tcga_deconv_feasibility.csv/.json`
8. `results/statistical_revision_2026-10-17/tcga_kn_pairs_recovered.csv`
9. `results/statistical_revision_2026-10-17/tcga_publication_changes.json`

## 7. 其他结构性观察

- 附表 `CKI_Supplementary_Tables_NC.xlsx`：37 sheets（Table 1–20 + Table6_a–h、Table9_a–h、Table13_* 细分），nc77 版仅 17 sheets——新增附表的数据来源多数落在档 B/C。
- 学生 docx 19.6MB，内嵌图；无 MANIFEST.txt、无 SourceData、无分析脚本（除 5 个图脚本）。
- 参考文献 74 条（nc77 为 58）——新增引用与外部队列/方法比较对应。

## 8. 结论与待决策项

**复现性结论**：学生第四版 = 在本仓库结果资产之上的全面重写 + 多个新分析簇。老数字（档 A）可复现、且与 nc77 修正兼容；新内容约一半（档 B）有脚本缺数据、一半（档 C）脚本数据全缺。按现状，**我们无法独立复现学生版全部结果**，尤其是五张主图与八个新分析簇。

待用户决策：
1. 是否向学生索取：①完整 SourceData 目录树；②档 C 八簇的分析脚本与中间结果；③59 vs 60 对过滤口径说明；④ρ=0.752 的模拟产物。
2. 合并策略：学生版已自行实施部分 nc78 P0（alt-HK 排除星形胶质细胞、ω 增量诚实阴性、CNA 分析），与 nc77 线的合并/取舍方案待定。
3. nc78 P0 其余项与投稿战略（NC 重构 / Genome Research / 拆分 TCGA）继续搁置待定。

---

附：审计工作目录 `results/audit/_nc78_repro/`（提取文本 8 份、diff、依赖清单、结构对比脚本）。

---

# v2 增补：SourceData.rar 补充后复核（2026-11-13）

学生于 11-13 凌晨拷入 `SourceData.rar`（527MB → 解包 772MB、1,346 文件）。已解包至 `results/audit/_nc78_student_fourth/SourceData/`（与 figure2–5.py 同级，路径自洽）。包内含 `ANALYSIS_TO_FIGURE.json`、`RAW_DATA_INDEX.json`、`FILE_MANIFEST_SHA256.json`、`README_CN.txt`，目录为 Figure2–5、SupplementaryFigure1–10、Shared、Formatting。

## v2.1 依赖重核（原档 B：107 依赖 104 缺）

CRLF 修正后重核：**98 HIT / 9 MISS**。9 个 MISS 全部为非数据资产（`.pending.png`、`figure_geometry.json`、`full_figure.png`、`media/*.png`、`Supplementary_Fig_14/17.png` 等图件中间产物），**数据类依赖 100% 落地**。原档 B 整体升级为可绘图。

## v2.2 档 C 八簇落地核验

| 簇 | v2 结论 | 证据 |
|---|---|---|
| GSE31210/GSE72094/GSE131907/A549 | ✅ 落地 | `Figure3/gse31210`、`gse72094`、`mechanism_20261031/inputs/GSE131907`、A549 扰动 `perturbation/data/GSE112190+GSE269664`（含 analysis_manifest + sha256） |
| J1000 | ✅ 落地 | `Figure2/brain_CKI_J1000_*` 全套（pairs 3,250 行 / T1 2,161 行 + protocol + QA + score_arrays.npz） |
| Lawlor | ✅ 落地 | `lawlor_mixture_performance.csv` + `lawlor_component_folds.csv` + protocol |
| 3-seed 模拟（含 ρ=0.752） | ✅ 落地 | `Shared/controls_20261111/QA.json`：`groundtruth_rho = 0.7522020415602003, n = 950`；协议锁定、2,000 次条件 MC bootstrap（seed 20261026）；皮肤/骨髓 replicate_scores.csv 各 1,750 行 |
| CNA | ✅ 落地 | `cna_hk_relation_20261102` + `cna_reconstruction_20261103` 全套 |
| GM/score 分解 | ✅ 落地 | `Figure5/explanatory_followup_20261103/e_matched_score_decomposition.csv` 等 |
| Reactome/GO | ✅ 落地 | `Figure5/pathway_top200_20261102/all_Reactome_tests.csv.gz` + `Reactome_Pathways_2024.gmt`；`figure3_identity_sources/cytosolic_ribosome_QuickGO.json` |
| MRR | ❌ 仍缺 | SourceData 内无 MRR retrieval 产物（grep 命中均为基因名误配） |

**档 D-2（ρ=0.752 无出处）闭环**。档 D-1（59 vs 60 对）与 J1000 pairs 无关，仍属文稿内部口径矛盾，待学生澄清。

## v2.3 实跑验证（figure2–5.py + SourceData）

| 脚本 | 首跑 | 处理 | 复跑 | 像素级比对（重跑 vs 交付 PNG） |
|---|---|---|---|---|
| figure3.py | ✅ exit 0 | — | — | 同尺寸，99.0% 像素一致（meandiff 0.79） |
| figure4.py | ✅ exit 0 | — | — | 交付为 1.333× DPI；降采样后 98.0% 一致 |
| figure5.py | ❌ PermissionError（`os.replace` 瞬态 Windows 锁） | 重试 | ✅ exit 0 | **逐像素一致**（maxdiff ≤ 2，8,812×6,378） |
| figure2.py | ❌ FileNotFoundError：`Code/SupplementaryNumbering/renumber_supplementary_figures.py` | 打最小桩（恒等映射 + 去重 no-op，仅验证数据侧） | ✅ exit 0 | 交付为 2× DPI；降采样后 96.9% 一致 |

结论：**四张主图从 SourceData 保存结果全部可重跑生成，内容级一致**（Figure5 像素级完全相同；差异仅为 DPI 参数与抗锯齿/字体渲染噪声）。PDF 字节均不同（元数据时间戳 + 打桩跳过后处理），不作判据。

## v2.4 仍然不可复现的部分（结构性）

1. **原始分析层（raw → results）不可复现**：`RAW_DATA_INDEX.json` 列 18 个原始数据集共 ~18.6GB（ts_human 14.4GB、SEA-AD 1.73GB、fivecancer_mechanisms 1.47GB、kang_ifnb 155MB、groundtruth 八指标 399MB 等），`large_data_not_duplicated = true`——包内只有路径与字节数记录，无文件本身。原项目根 `E:/CKI-cell-type-identification-main` 本机不存在（本机仅 C 盘）。脑图谱原始 h5ad `exists: false`。
2. **`Code/` 目录未随包交付**：README 引用的 `Code/rebuild_figures.py`、`Code/Analysis/project_snapshot`（分析脚本快照）、`Code/SupplementaryFigure*/build_*`（附图 1–10 重建）、`Code/FigureTypography`、`Code/ReleaseScope.txt` 均不可见。因此：①figure2 端到端不可直接跑（本次靠打桩验证数据侧）；②**附图 1–10 无法从包内重建**（figure2 仅额外产出 legacy 编号 Supplementary_Fig_11/16/18）；③分析脚本快照缺失，「从原始数据重分析」路线整体断裂。
3. **学生自述未决项 U01–U05**（RAW_DATA_INDEX）：历史 rounded-summary 9.73 未再验证、mouse n=15 桥未解、retained149×37 null draws 未解、历史附表分子/分母输入未解、phase32 CSV 缺。
4. **MRR retrieval** 数据仍缺（见 v2.2）。

## v2.5 总判断（回答「加上数据后能否复现」）

- **图件重建层（saved results → 图）**：✅ 基本可复现。107 项数据依赖 100% 落地，主图 Figure2–5 实跑通过并像素级核验；档 C 八簇中七簇数据落地，ρ=0.752 闭环。两个瑕疵：Code/ 辅助脚本缺失需打桩、figure5 有瞬态文件锁 bug 需重试。
- **原始分析层（raw data → results）**：❌ 不可复现。~18.6GB 原始数据未打包（学生明确选择不重复打包），分析脚本快照（Code/Analysis/project_snapshot）也未交付；脑原始 h5ad 学生自述不可得。
- **建议向学生索取（优先级序）**：①`Code/` 完整目录（含 ReleaseScope.txt 与 project_snapshot）——补上后图件重建层即可「开箱即跑」且附图 1–10 可重建；②MRR retrieval 产物；③59 vs 60 对口径说明；④如需答辩级复现，再谈 18.6GB 原始数据的传输方式（或放弃 raw 层复现，以 SourceData + QA 链作为复现性声明的依据）。

## v2.6 复核工作产物

- 解包：`results/audit/_nc78_student_fourth/SourceData/`（772MB）
- 重跑输出与日志：`results/audit/_nc78_student_fourth/_rebuild_test/`（4 主图 PDF/PNG + legacy 附图 + 6 份 log）
- 打桩脚本（仅为审计验证，非交付物）：`results/audit/_nc78_student_fourth/Code/SupplementaryNumbering/`、`Code/SupplementaryDeduplication/`

---

# v3 增补：Code.rar 到达后端到端复现（2026-11-13 10:25）

学生补拷 `Code.rar`（2.27MB，311 条目）：`Code/rebuild_figures.py`、`ReleaseScope.txt`、`SupplementaryFigure1–10` 构建器（5 号经 FigureTypography/style_pdf.py 排版 staging 产出）、`SupplementaryNumbering/Deduplication`、`Analysis/project_snapshot`（cki 核心 + notebooks 分析脚本快照 + restore_analysis.py）。**v2.4 第 2 条「Code/ 未交付」关闭**。

## v3.1 官方入口端到端重建

```
python Code/rebuild_figures.py --output-dir _rebuild_official   # exit 0, 5m42s
```

- 主图 2–5 + 附图 1–10 **全部 14 张一次重建成功**，内置断言（单页、270mm 宽、600dpi PNG 重渲）全过
- 唯一环境障碍：figure5 的 `os.replace` 被本机杀毒/索引器瞬态锁定（WinError 5），以 PYTHONPATH 注入 sitecustomize 重试钩子解决，**学生源码零改动**；该问题在本机必现、属环境兼容性瑕疵，建议学生在 `figure_export.py` 加重试

## v3.2 重建 vs 交付：三级核验

| 层级 | 结果 |
|---|---|
| PNG 像素 | **6/14 逐位相同**（Figure3、附图 1/2/4/7/9）；7 张 98–99.2% 一致（差异全域弥散 = 渲染器抗锯齿噪声：交付 PNG 走 pypdfium2、rebuild 末步走 PyMuPDF）；附图 10 尺寸 8709→8575（内容改版） |
| PDF 文本层 | **12/14 完全一致**；Figure5/附图4 仅 token 顺序差 |
| **Figure2 文本层真差异** | 交付版 `1.21 / 0.148`（历史 rounded 数组）→ 重建版 `1.20 / 0.146`（= SourceData `split_half_cv_summary.csv` 的 1.2049/0.1465，20261112 表达式级重算链） |

## v3.3 SHA256 清单核验（FILE_MANIFEST_SHA256.json，2026-11-13）

- `files` 1,399 条目（覆盖 Code/ + SourceData/ + 根目录）：**1,391 OK / 0 MISS / 8 DIFF**
- 8 个 DIFF = `figure2.py`、`figure3.py`、3 份 docx（MS/SI/Guide）、`Figure2.pdf/png`、`SourceData/Figure5/regional_redesign_20261103/main_display_values.json`
- `canonical_root_reference_files` 31 条目：26 OK，5 DIFF（Figure2.pdf/png、附图10.pdf/png、Guide.docx）
- **结论：包根目录有 5+ 个文件落后于 11-13 canonical 快照**——学生打包时间早于最终定稿，需重新同步

## v3.4 新发现问题（须学生处理）

1. **文稿数字与最新数据链不一致**：MS（§Results ω 增量段）与 SI（Note 20 等两处）仍引 "brain CV 1.21 → 0.148"，而 20261112 重算链为 **1.20 → 0.146**（比值 8.22，"up to eightfold" 表述仍成立）。ReleaseScope U01 已声明历史 rounded 数组不再验证，即重建版为权威，**MS/SI 文本需改为 1.20/0.146**。
2. **包根 5 文件过期**（见 v3.3）：Figure2.pdf/png、附图10.pdf/png、Guide.docx 需以 canonical 重打包。
3. figure_export.py `os.replace` 无重试，Windows 环境脆弱。

## v3.5 总判断（最终）

| 层 | 状态 |
|---|---|
| 图件重建（saved results → 14 图） | ✅ **完整可复现**：官方单命令、断言自验、文本层 12/14 一致 + Figure2 差异已定位为权威更新 |
| 分析脚本层 | ✅ 快照已交付（`Code/Analysis/project_snapshot`：cki 核心 + notebooks + restore_analysis.py） |
| 原始数据层（raw → results） | ❌ 仍不可复现：18 数据集 ~18.6GB 未打包（`large_data_not_duplicated`），脑 h5ad 不可得，U01–U05 学生自述未决 |

**回答「是不是可以复现了」：图件与脚本层——是（今天 Code.rar 补齐后端到端跑通）；原始数据重分析层——否（结构性，学生已声明不打包大件）。** 投稿级复现性声明可基于「SourceData + Code + QA 链 + SHA256 清单」成立，但须先处理 v3.4 三项（文本 1.21/0.148→1.20/0.146、根目录重打包、os.replace 重试）。

## v3.6 工作产物

- 官方重建输出：`_nc78_student_fourth/_rebuild_official/`（14 图 PDF/PNG + 3 份 rebuild log + 各图 caption）
- 审计钩子：`_nc78_student_fourth/_audit_hook/sitecustomize.py`（os.replace 重试，非交付物）
- QA 数值记录：`results/audit/tmp/current_figure_rebuild/figure2_numerical_records.json`

## v3.7 本机原始数据盘点（对照 RAW_DATA_INDEX 18 数据集）

| 学生索引数据集 | 大小 | 本机状态 |
|---|---|---|
| kang_ifnb | 155MB | ✅ 15/15 全齐，路径一致 |
| ts_human | 14.4GB | ✅ 7 器官 h5ad+zip 全齐；仅缺 Tabula_Sapiens_metadata.csv(67MB)+6 个小 json 清单 |
| tcga/hallmark_2020.gmt | 44KB | ✅ |
| sea_ad_figure5_20261102 | 1.73GB | ✅ 两大 h5ad 在 `data/sea_ad/`（**字节精确一致**），仅路径名不同；缺 3 个小 json |
| groundtruth_eight_metrics_20261026 | 399MB | ✅ annotations_FACS.csv(4.32MB)+Marrow/Skin-counts.csv **字节精确**（在 `data/FACS/FACS/`，且为全 18 组织超集） |
| mouse_matched_20261031 | 85MB | ✅ metadata_FACS.csv+Spleen-counts.csv **字节精确**（同 FACS 目） |
| —（额外自有超集） | — | data/tms/TMS_Smart-seq2_All.h5ad 2.5GB、data/brain/（Siletti 自下载）、gtex、housekeeping |
| figure3 系 8 数据集 | ≈1.1GB | ❌ 全缺（brca_triomics、cna×2、followup、identity、mechanism、pathology、hypotheses） |
| fivecancer×2 | 1.49GB | ❌ |
| figure5_biology_programs(AHBA) | 47MB | ❌ |
| mcf10a_factorial | 3MB | ❌ |
| 脑 Siletti 原始 h5ad（augur recovery） | — | ❌ 双方均无（学生 exists:false）；Figure2A 已改走 SourceData 自包含 retained counts（888,263 nuclei npz + QA 链） |

**结论：学生索引 18 个数据集中 6 个在本机（含全部 16.8GB 大件），缺的 12 个共 ≈3.1GB，全是学生 10-27 后 Figure3/5 新分析簇的原始输入。** 路径差异（data/sea_ad/ vs sea_ad_figure5_20261102/、FACS/FACS/ 嵌套）以符号链接或复制对齐即可；若向学生索取 3.1GB，raw 层复现即可闭合大半（脑 h5ad 除外）。

---

## v4（2026-11-13 下午）：raw 层端到端重放——五癌种臂全链闭环

**链**：Xena/GDC 公共源 → `fivecancer_cnv_recover`（表达+CNV npz）→ `fivecancer_metadata_recovery`（GDC 三件）→ `fivecancer_states --manifest` → `figure3_paired_cohort_components`（freeze+5 癌种+finalize）→ `figure3_cna_reconstruction`（freeze+5 癌种）。全部以学生 Code.rar 快照原码运行（仅审计侧注入 os.replace 重试补丁，零源码改动）。

### 1. 派生矩阵：字节级命中
| 产物 | 核验 | 结果 |
|---|---|---|
| 5× expression npz（60,498 基因，linear TPM） | 对照冻结 `cnv_recovery/expression_recovery_manifest.json` sha256 | **5/5 MATCH（字节不差）** |
| 5× CNV npz（27,146 基因，SNP6） | 同上 cnv_recovery_manifest | **5/5 MATCH** |
| GDC 元数据三件（ABSOLUTE/clinical/quality） | 下载溯源 sha256 记录 | ✅ |

### 2. states 关联分析（720 行）
- `cohort_summary.csv`：**sha256 与冻结清单（cbb42764…）一致**
- `all_state_associations.csv`：720×720 行、键全同、数值差 ≤7.7e-13（CSV 浮点 repr 噪声）
- `corrected_TT_NN_contrasts.csv`：数值差 ≤1.2e-14
- `numeric_QA.json`：实质一致（队列顺序、锁文件数 15 vs 11 系审计自建 metadata 所致；SVD 误差 ~1e-14 量级相当）
- headline 复现：primary 显著计数 CKI 负 19 / kf 正 20 / kn 正 20——与冻结 `interpretation_summary.json` 精确一致（该件无生产脚本，为手工汇总，内容级对账通过）

### 3. paired components（342 患者）
- finalize 内置断言全过：342 患者、NN/TT 各 12,875 对、26,092 总行、输入哈希未变
- `cohort_summary.csv` 与 `paired_patient_identities.csv`：**sha256 与冻结件一致**
- 冻结 `TT_NN_effects.csv` vs 重算 `arithmetic_contrasts.csv`（TT/NN 15 行 × 12 数值列）：**max diff = 0.0**

### 4. cna reconstruction（330 评估患者 + 2,567 训练肿瘤）
- 患者计数逐癌种精确一致（eval 51/49/70/110/50；train 443/432/431/952/309）
- `primary_results.csv` 共享 9 列：max diff ≤2.0e-14；`cohort_summary.csv`：diff = 0；`heldout_prediction_all`：≤1.4e-14；`baseline_panel_comparisons` 共享 20 行 ≤8.9e-16；`matched_nonHK_panels_all` 500 行 ≤4.4e-16；`matched_panel_reference` 分位数 diff = 0
- 冻结 `paired_changes_joint_CI.csv` 口径破解：change = standardized−observed（点估计残差 8.4e-15）；CI = joint 200 轮「每轮 standardized−每轮 observed（joint_eval 重采样下）」的分位数——用存档 `joint_bootstrap.npz`+`observed_scores.npz`+`resampling.npz` 重建，**15 行 worst residual 3.6e-14**
- 冻结 `baseline original_adaptive200` 五行 = contrasts observed 情景 kf 的 JS 均值（恒等 ≤5.6e-16）

### 5. 缺口与审计替身（须回告学生）
| 缺口 | 处理 |
|---|---|
| `figure3_nonhk_size_sensitivity_20261102` 生产脚本不在快照、产物不在 SourceData | 审计替身由冻结 corrected 表逆转置合成（仅供 finalize 描述性 context，无值断言）；README_AUDIT.txt 标注；**建议学生补交付该脚本与产物** |
| `interpretation_summary.json` / cna 打包脚本（_all 聚合）不在快照 | 内容级对账通过；建议补交付 |
| CSHL_final_published.pdf、GSE68465 archive_*、QuickGO ×6 | 未决，低优先（PMC 反爬 / caArray 退役） |
| brca_triomics 11MB 派生 npz | 无消费脚本在快照内，无法本地重算 |

### 6. 总判断更新
**五癌种臂 raw→results 全链可复现，且多个关键节点达字节级一致（10 npz、paired 两表、states cohort_summary）。** 结合 v3 图件层（14 图官方入口跑通 + 文本层 12/14 一致），第四版投稿包复现性主体闭环；剩余缺口均为「脚本/产物未随包交付」性质，非数值不可复现。原 Figure2 脑 CV 文本值修正（v3.4①）与包根 5 文件重打包（v3.4②）建议不变。

### 7. 补遗（同日晚）：cnv 分析三阶段亦闭合
states 落地后重跑此前因缺输入失败的两个脚本 + posthoc 扩展：
- `fivecancer_cnv_analysis_20261031`：`analysis_summary.json` 五癌种全部数值字段一致（差异均 ≤1e-15 浮点 repr 噪声）；protocol 唯一实质差异 = `static_hashes` 中**脚本自身 sha 不同**（冻结 52e7fd54… vs 快照 52509d98…）——学生冻结后改过脚本（疑为加 resume 功能，回放版多了 `resumed_from_complete_CSV` 键）；**数值不受版本差影响**
- `fivecancer_cnv_control_genejs_20261031`：对照冻结 `control_geneJS_comparison.csv`，HK_gene_n/own-panel ρ/参考分位/controls_ge_HK 全字段命中（0 ~ 8.3e-17）
- `fivecancer_cnv_components_posthoc_20261031`：对照冻结 `posthoc_component_associations.csv`，15/15 行 12 数值列 worst diff 3.0e-13（含点估计、CI、Wald P、BH_Q）；五癌种 CKI 对 CNA 距离均显著负相关（BH Q ≤ 1.9e-48 ~ 7.6e-15）精确复现

**五癌种臂至此 7/7 阶段全链闭合**（下载→npz→states→numeric_QA→paired→cna reconstruction→cnv 分析×3）。

---

## v5（2026-11-14）：第五版投稿包（CKI_Submission_NC_fourth_20261114.zip，907MB，1,962 条目）复核

学生按 v4/清单回件。结论：**P0 全部核销，图件层 + 结果层防退化全绿，可推进。**

### P0 核销表
| 项 | 状态 | 证据 |
|---|---|---|
| ① requirements-lock.txt + Dockerfile | ✅ | 包根两件齐：lock 53 钉版 + 1,185 条 wheel hash（--require-hashes）；Dockerfile 钉 `python:3.12.14-slim-bookworm@sha256:1aaa…`；`Code/Environment/VALIDATION.json` 记录 Windows 净装通过（pip check 无破损）、Linux 轮解析通过、Docker 未建（学生机无引擎，明示） |
| ② 四类缺失脚本 | ✅ | `figure3_nonhk_size_sensitivity_20261102.py` + 真版 `TT_NN_contrasts.csv`（6 档 × 90 行；setting=200 与审计替身一致至 2.4e-14）；打包脚本 `package_figure3_corrected_20261031.py`/`figure3_cna_reconstruction_report_20261103.py`/`prepare_figure3_cna_artwork_20261103.py`；brca_triomics 8 脚本（prepare/recover/analyze/qa/report/protocol/metadata×2） |
| ③ 脑 CV 1.21/0.148→1.20/0.146 | ✅（独立复算） | 审计脚本 `_nc78_brain_cv_independent_replay.py` 不导入学生代码，从包内 29 个 `sampling_and_counts.npz`（raw_half_A/B + permutations + 记录 panel）全量重放 1,450 split：0 panel 失配，kf/kn 最大误差 1e-16，CV：kf 差 2.2e-16（1 ULP）、kn 差 0、ω 差 2.8e-17 → **Kf=1.2049366、ω=0.1464776 独立证实**；SI 文本 0.148 已消除、1.20/0.146 进文、残留两处 "1.21" 为无关数值；旧值留存于 `comparison_with_previous_summary.csv`（kf −0.42%、ω −1.03%，标注历史件） |
| ④ 包根 8 文件重打包 | ✅ | figure2/3.py 已更新；`verify_release.py` 官方校验 1,961 文件 0 错误；Figure2.pdf/png 与旧 canonical 不同系合法重生成（脑 CV 已改） |
| ⑤ cnv_analysis 版本说明 | ⚠️ 部分 | 快照脚本仍为 52509d98（新版）；RELEASE_NOTES 称"CNV 源与原始 protocol 由两份保留的 implementation-amendment 记录关联"，但未逐字说明脚本 sha 差；残留小项 |

### 新增交付（超预期）
- `SourceData/REPRODUCIBILITY_GAPS.json`：R01–R05 原始输入缺口 + U01–U05 历史未决项全部成文（Lawlor raw、Siletti 神经元 h5ad、GTEx donor 级、3535 历史队列、mouse 校准），每条附 available/limitation
- `Code/Verification/`：verify_release.py（已跑通）、verify_input_manifest.py、replay_brain_cv_full.py（需项目侧 CSR 缓存，未嵌包；我已用包内 populations npz 独立等价复算）
- `Code/Analysis/replay_figure3_gap_checks.py`：326 项有界重放（expression→score 固定行 + interpretation_summary 计数对账）
- 快照内置 results/（fivecancer/figure3 家族 + brca_triomics 结果）

### 防退化
- v1→v2 SourceData 15 个冻结锚点文件 **全部字节一致**（states/paired/cna/cnv 结果未被改动）
- v2 图件重建：14/14 跑通（4m55s）；PNG 6/14 字节一致；PDF 文本层 11/14 全同 + 3 张仅标签提取顺序差（Figure2/Figure5/SFig4，内容零差异）

### 残留项（均非阻塞）
1. ~~326 项检查本机跑通需先跑 brca_triomics_prepare~~ **✅ 已闭合（2026-11-14，见 v6）**
2. U01–U05 按设计保持未决（已成文披露）
3. Figure 4/5 其余臂 raw 层未由我重放（属 P1；v2 已随包 results/ 快照）
4. Docker build 双方均未实跑（无引擎）

---

## v6（2026-11-14）：残留项 #1 闭合——brca 三表补齐 + prepare 重放 + 326 检查全过

**数据源定位**：三表为 Mertins et al. 2016（Nature 534:55, iTRAQ 105 瘤/77 QC-pass）官方补充材料，经 Nature 文章页解析得官方补充包 `41586_2016_BFnature18003_MOESM111_ESM.zip`（Content-Length 138,716,400 B，与学生 RAW_DATA_INDEX 记录的 `publisher_full_supplement.zip` 字节数精确一致）。本机直连下载成功（无需代理），sha256 前 16 位 6dc93f9e1b5c6a0c，落位 `results/audit/_nc78_raw_restore/brca_cptac/`。包内 `nature18003-s2/CPTAC_BC_SupplementaryTable01/02/03.xlsx` 尺寸 27,376 / 18,050 / 36,481,821 B，与 RAW_DATA_INDEX 三表记录**逐字节一致**；sheet 结构命中脚本预期（`CPTAC_Sample_Annotation` / `sheet1`(含 percent_tumor_cells_CPTAC) / `Global-Proteome-G3`）。

**prepare 重放**（快照内 staging：三表 + BRCA 两 npz（v2 raw 恢复字节核验版）+ Reactome gmt）：
- 跑通无 assert 失败：105 瘤 / 77 QC-pass / 77 matched / 19,969 canonical RNA 特征 / 1,126 HK
- 产物 vs 冻结备份：`patient_covariates.csv`、`module_coverage.csv`、`sample_pairing_audit.csv` **字节一致**；`gene_mapping_coverage.csv` / `module_membership.csv` worst |Δ| 3.0e-07 / 1.2e-07（float32 累加序差异，norm_SD 类列；文本列全等、形状全等）；protocol/preflight/clarifications JSON 全键一致；input_lock 差异仅 npz zip 时间戳 + 上述两 CSV sha（预期内）
- npz 产物尺寸：DNA_subset.npz 2,806,025 B、protein_subset.npz 2,988,332 B 与学生索引**精确一致**；canonical_RNA_subset.npz 5,171,259 vs 5,171,256（+3 B zip 元数据）

**326 项 gap 检查**（`replay_figure3_gap_checks.py`，project-root=evidence-root=快照，快照另补齐 10 个 cnv_recovery npz + 10 个 cna_reconstruction npz）：**326/326 passed，最大绝对误差 8.5e-14**。分族：nonHK_size 270 / CNA_reconstruction 45 / BRCA_triomics 11；interpretation_summary 计数、三结局显著性汇总、joint 20 行数值全部命中。输出 `results/audit/_nc78_gap_checks_out_20261114/`（replay_summary.json + fixed_row_replays.csv）。

**残留项余量**：#2 Docker build 实测（无引擎，双方）；#3 Figure 4/5 其余臂 raw 重放（P1 可选）；#4 U01–U05 成文未决（按设计）；cnv_analysis 脚本版本差逐字说明（回告学生）。

---

## v7（2026-11-14）：brca_triomics 下游全链重放——32 项冻结产物全部闭合

**链路**：按产物 README_CN 官方顺序 `protocol → prepare → analyze → qa → report` 在 v2 快照内完整重放（analyze 24s 实跑；QA 影子副本仅拆分末尾联合哈希断言、不改任何数值代码；report 影子副本仅把画布绝对路径 `C:/Users/XJTU/.cursor/...` 重定向到结果目录——该路径是学生机 Cursor IDE 私有路径，TSX 非投稿包交付物）。

**产物对比（重放 vs 冻结全量备份 `frozen_brca_full_backup/`，32 文件）**：
- **21/32 字节一致**：pair_values.csv.gz（2,926 样本对全量）、control_membership.csv.gz、resampling.npz（500×77 患者多项式重抽样权重——随机种子跨环境字节级复现）、protocol.json/.sha256、publication_before.json、input_lock.json、preflight.json、covariate_QC.json、module_coverage、module_membership、gene_mapping_coverage、sample_pairing_audit、patient_covariates、source_audit、delivery_manifest、analysis_code_lock、browser_QA、README_CN
- **8 CSV 数值噪声**：CV_predictions ≤2.2e-15、CV_summary ≤9.7e-17、patient_disjoint_CV ≤3.1e-16、primary_results ≤1.5e-15、metric_associations ≤3.6e-15、sensitivity_results ≤6.1e-16、matched_controls ≤3.7e-08、gene_cis_results ≤3.0e-07（normal_SD 列 float32 累加序；文本列全等、形状全等）
- **primary_bootstrap.npz**：全部 key 同形同 dtype，max|Δ| 2.7e-15
- **analysis_summary.json / report_data.json**：递归 diff 全部为 float64 末位 ulp 噪声（~1e-15 相对），无键/结构差异

**QA 独立重放（shadow）全过**：分量复算 max err 3.3e-16；archived Figure3 k_n 重叠 45 对命中；9 基因偏相关独立重放命中；12 主检验 CI/BH 独立重算命中；CV 10 模型 555 留出边双端患者隔离验证通过；200 匹配参照面板核验通过；`input_hashes_unchanged=True`（prepare 重放后 14/14 输入锁自洽）；`passed=True`。

**两处环境性失配（预期内，非数值问题）**：
1. `publication_before.json` 9/9 失配：该锁冻结于 2026-11-03 分析前，此后投稿包历经多次重建（Figure3/docx/xlsx 均演进，CKI_Tables_NC.xlsx 已在现包删除）——版本漂移，README 中「分析前哈希一致」的声明在其时成立
2. qa 正式版末尾联合断言因此失败 → 以影子副本拆分两旗标定位，正式 `numerical_QA.json` 未被覆写（冻结原件保留）

**结论**：brca_triomics 臂从原始三表 → 派生 npz → 全部统计产物 → HTML 报告数据**端到端闭合**，可重复性达字节级（21/32）或浮点噪声级（11/32，≤3e-7）。

---

## v8（2026-11-14 下午）：REPRODUCIBILITY_GAPS R01–R05 逐臂闭合——「材料齐备则全部实锤」

**关键发现：R02–R05 缺口输入本机全数在库**（主项目 data/ 树，非随包）。尺寸与官方源逐一比对：

| 臂 | 缺口输入 | 本机尺寸 | 官方源核验 |
|---|---|---|---|
| R02 | brain/neurons/MGE_interneuron.h5ad | 2,548,398,308 | cellxgene `283d65eb-dd53-496d-adb7-7570c7caa443`（Human Brain Cell Atlas v1.0）资产尺寸**精确一致** |
| R02 | Thalamic_excitatory.h5ad | 1,399,531,984 | 同上 ✓ |
| R02 | Upper-layer_intratelencephalic.h5ad | 6,584,209,774 | 同上 ✓ |
| R03 | gtex/gtex_RSEM_gene_tpm.gz | 545,614,848 | Xena toil hub Content-Length 逐字节一致 ✓ |
| R03 | gtex/GTEX_phenotype.gz | 82,442 | 同上 ✓ |
| R04 | tcga/tcga_RSEM_gene_tpm.gz | 740,772,247 | 原 legacy tcga.xenahubs.net bucket 已整体退役（全对象 403 AccessDenied，本机留存为唯一副本） |
| R05 | FACS/FACS/Liver-counts.csv | 48,875,624 | 官方源 = figshare 5829687「Smart-seq2 FACS v2」FACS.zip（303,966,623 B，md5 ef6e44ca…）；figshare 直连 403 需代理，成员级核验待代理 |
| R05 | FACS/FACS/Heart-counts.csv | 350,623,568 | 同上 |

九件输入 sha256 指纹落盘 `results/audit/_nc78_replay_out/gap_inputs_sha256.txt`。

**raw→results 重放（影子脚本仅重定向输出路径，数值代码零改动；产物存 `results/audit/_nc78_replay_out/<arm>/`）**：

| 臂 | 脚本 | 冻结产物 | 结果 |
|---|---|---|---|
| R05 小鼠六群体 | 87_mouse_splithalf_v44 | mouse_splithalf_v44.csv（300 splits）+ summary.json/txt | **CSV 字节一致**；json/txt 仅 runtime 字段差（90.0s→76.3s） |
| R03 GTEx donor 级 | nc52_gtex_kn | nc52_gtex_pairs.csv + kn_by_grouptype.csv + summary.json | **两 CSV 字节一致**；json 6 处差全为 time_s 计时字段 |
| R04 TCGA 3535 历史队列 | nc49_tcga_purity | nc49_tcga_purity.csv + admix_scores.csv | **两 CSV 字节一致**（ESTIMATE 评分 + 低混杂半子集 NN/TT 比值全命中） |
| R02 Siletti 神经元 | 80_brain_neuron_superclass_omega | superclass_omega.csv + subcluster_omega.csv + report.md | **三件全部字节一致**（10.5GB h5ad 全程重算） |
| R02 链接臂 | 83_brain_neuron_blockshuffle | blockshuffle.csv + null_means.npy + report.md | **三件字节一致**（83 消费的是臂1重放产物，链式保真） |

> **验证深度口径（v10 细化，v9 行动项⑦）**：上两表「官方源核验」与「字节一致」分属三个深度等级，读者勿混读——
> - **L1 尺寸级**：本机文件尺寸 vs 官方源 Content-Length/目录记录一致（R02 三 h5ad、R03 两 gz、R05 两 csv 属此级；未下载官方全文重哈希）；
> - **L2 抽样字节级**：对在线源做 Range 分段 GET 并比对字节（R04 tcga_RSEM_gene_tpm.gz 经 v9 补遗三段 Range 命中；figshare FACS.zip 因直连 403 止于成员尺寸级）；
> - **L3 全链重放级**：本机输入经影子脚本 raw→results 重放，产物与冻结件 sha256/字节比对（重放表全部行）。「CSV 字节一致」= sha256 全等；「仅计时字段差」= 除 time_s/runtime_s 等运行元数据外逐字节一致。

**R01（Lawlor 刺激基准）= 唯一真实残留缺口**。订正溯源：此「Lawlor」为 **Lawlor et al. 2021 Front Immunol 12:636720**（CITE-seq PBMC，10 供体，HTO hashing，LPS/CD3-CD28 刺激）——**非** Lawlor 2017 胰岛 GSE86469（本会话早前误下载的 12.7MB GEO 文件已弃置）。原始派生件（lawlor_annotated_raw_counts_cells_by_genes.npz + cells.csv）仅存于已删除的 E:/ 撤回归档，但包内 `SourceData/Figure2/provenance.json` 留存其 **sha256 指纹**（npz `347250f7…6943ba`、cells.csv `da887e50…4d0e1`）——任何未来重建件可据此核验。公共恢复路径：HCA 项目 `efea6426-510a-4b60-9a19-277e52bfa815`（fastq×60 + Rds×3）/ ENA ERP124005 / czi-pbmc-cite-seq.jax.org；重建需 Seurat(R) 提取注释计数矩阵并按消费者脚本契约（基因序须与 Kang GSE96583 基因表逐一相等，cells.csv 需含 Donor_of_Origin/Celltype_Annotation/HTO_Barcodes/stratum 列）重打包。

**结论**：REPRODUCIBILITY_GAPS 五臂中 **R02/R03/R04/R05 raw→results 全链闭合（字节级或仅计时字段差）**，R01 留指纹级恢复配方。连同 v7 brca_triomics 下游全链与 v6 三表溯源，学生包全部「材料齐备」的结果现已实锤可重复。

---

## v9（2026-11-14）：五人专家团盲审 v6–v8 + 汇总裁定

**打分**：stat 8/10、source 9.5/10、repro 8/10、editor 7.5/10、redteam 8.5/10 —— 共识 **8.3/10**。全票确认：无数据捏造、无选择性报告、所有「字节一致」声明经独立复算成立；两方独立重放「字节一致→全文件等值」推断。

**对专家声明的逐条裁定（lead 以 ground truth 复核，三件专家声明被推翻）**：
- ❌ stat-M1「prepare publishDir 指向快照」表述错位 + repro「83 PATHS 指向重放目录」：实查 prepare L8 `OUT=ROOT/'results/...'`（ROOT=parents[1]=快照），83 影子无 PATHS 行——两声明的代码行引用均不成立（底层概念关切仍保留见下）
- ❌ stat-M2/M3「83 第 252 行读冻结 superclass_omega 且与冻结 DIFF」：双重错误——影子 83 L252 读的是臂1重放产物（RDIR2），且 cmp 实测冻结 vs 重放**字节一致**；83 三件产物 cmp 全部字节一致
- ❌ source-T5「83 重放无变化」：同上 cmp 证伪（报告文件未落盘，已催补）
- ❌ redteam「83 读冻结 superclass」：方向反了（读的重放件）；但其附带发现成立——83 的 Wilcoxon 参照与 report.md 参照节引用**冻结** brain_bs_null_observed_pairs.csv（08d 产物，影子重定向所致），R02-83 记「部分命中」
- ✅ redteam R01 三处纠错全部成立：①指纹实际在 `lawlor_mixture_protocol.json` frozen_files（非 provenance.json）；②cells.csv 列契约实际为 Donor_of_Origin/donor/stratum/Run_Identifier/Celltype_Annotation/HTO_Barcodes/Demuxlet_Classification/cell_id 并集（双方此前各漏一半）；③误下载的 GSE86469 文件仍在盘上——已删除，「已弃置」陈述现与磁盘一致
- ✅ redteam「qa 影子 passed=True 为无条件写入」：成立——shadow JSON 的 passed 字段是尾随写入物，真实门禁是 input_hashes（True）+formal 旗标（False），v9 起措辞修正
- ✅ repro-M1（R04 标签过强）：成立——nc49 L49 消费冻结 tcga_linear_norm_v44_all_pairs.csv（逐对 k_n/k_f/ω），仅 ESTIMATE 基质/免疫分从 raw TPM 重算；v8 的 R04「raw→results」降级为「raw（纯度评分）+冻结中间件（逐对度量）→results」。同理 R03 的 v44 表仅作元数据参照不进产物
- ✅ repro-M2（流程纪律）：成立——v8 写入时间 13:55:18 早于 83 产物落盘 14:05，结论后被 cmp 证实正确但顺序违规；本节的全部裁定均在验证后落笔

**据此对 v6–v8 的正文修正（不重写旧节，以本节为准）**：
1. v8 R04 行标签改为「raw+冻结中间件→results（ESTIMATE 臂全链，逐对度量臂经冻结输入）」；R03 注明 v44 表仅参照
2. v8 R01 段：指纹出处改 `SourceData/Figure2/lawlor_mixture_protocol.json`；列契约改上述八列并集；GSE86469 文件已实际删除
3. v7 QA 段补注：shadow 的 passed=True 非判定结果，判定以两哈希旗标 + 全量数值检查为准
4. 指纹清单已补全 FACS 六组织（gap_inputs_sha256.txt 现 13 行）

**合并行动清单（去重后回告学生/投稿前处理）**：
- P0：① 清洗包内私有路径与「withdrawn」字样（lawlor_mixture_protocol.json/provenance.json 的 E:/ 路径、brca 报告的 C:/Users/XJTU 路径）② R01 Lawlor 2021 重建+指纹核验，或 Figure 2H/I 面板降级预案
- P1：③ publication_before.json 版本漂移写 README 预释 ④ cnv_analysis 版本差逐字说明 ⑤ Docker CI 实测 ⑥ SourceData 投稿级补 brca 三表出处（官方 394MB zip 或 36.5MB 单表）⑦ 审计报告「验证深度」栏措辞细化
- P2：⑧ tcga_RSEM_gene_tpm.gz Zenodo 镜像（legacy bucket 已退役，本机为唯一副本）⑨ SourceData 补 FACS.md + TCGA_PURITY 注释/校验 ⑩ 脑 h5ad 内部指纹（n_obs/n_vars/列名哈希）入档 ⑪ 审计员红队文档公开

### v9 补遗（同日）：R04「唯一副本」论断被 source-reviewer 证伪并采纳
- source-reviewer 实测：`https://toil.xenahubs.net/download/tcga_RSEM_gene_tpm.gz` 在线，Content-Length **740,772,247 B 与本机精确一致**，三段 Range（首/中/尾）GET 206 字节命中。lead 独立复测时遇 S3 侧 502 瞬断（非 403），未能证伪；采纳其结论
- 修正：v8 表 R04 行与 v9 P2-⑧ 的「官方源已退役/本机唯一副本」应读作「**legacy tcga hub 已退役，但同一文件在 toil hub 在线可得**」；Zenodo 镜像由「建议」降为「可选加固」
- 附带收获：R05 三缺口文件与 figshare 5829687 FACS.zip 成员的**尺寸逐一命中**（Liver 48,875,624 / Heart 350,623,568 / annotations_FACS.csv 6,990,328）；R01 消费者读到的 HTO 标签 {Baseline,CD3_CD28,LPS}、标签集合（CD4T_Naive 等）与 Lawlor 2021 官方注释三端互证

## v10（2026-11-14）：P0-1 私有路径/withdrawn 清洗闭环

**对象**：`results/audit/_nc78_student_fourth_v2/CKI_Submission_NC_fourth/`（第四版 v2 工作副本，1.9GB / 2,002 文件）。**原始包零改动**——全部清洗作用于 robocopy 全量副本 `results/audit/_nc78_v10_cleanup/patched/CKI_Submission_NC_fourth/`。

**枚举（`enumerate_private_paths.py` + `analyze_enum.py`）**：首轮 6 类模式扫出 248 文件命中；人工复核证伪 134 个二进制文件命中（PDF/PNG/npz/jpeg 压缩流字节噪声，如 `E:/p` 类 ASCII85 碎串）与 docx XML 命名空间命中（`http://` 中 `p:/`）。**真实命中 116 文件 + 4 个非文本扩展文件（.tsx/.log/.obo）**，路径宇宙完备枚举：`E:/CKI-cell-type-identification-main`（757 JSON 转义 + 7 其他形态）、`E:/separate_CKI_analysis`（8，含 Repro Guide docx 正文「Run … from E:/separate_CKI_analysis」）、`E:/CKI_rebuilt_figures`、`E:/CKI_analysis`、`e:/cki-…` 小写变体（pip log，首轮漏检、verify 兜底捕获——**教训：清洗规则须大小写双侧覆盖**）、`C:/Users/XJTU`（.cursor/.codex/.cache/pip-temp，6 文件）、`C:/Users/KnightZ`（审计侧 nc49 脚本泄漏进快照，5 文件）、`C:/Users/AREUMJO`（GSE131907 xlsx 内嵌第三方元数据）、`D:/Anaconda3/python.exe`（15）、`withdrawn_additional_analyses_2026-10-19`（6）与 `withdrawn_augur_matched_reanalysis_20261026`（17）。

**清洗（`clean_private_paths.py`，字节级字面替换 + 有序规则，幂等——第三遍 0 改动）**：116→119 文件（第二轮补 3），19 条规则全部核销。白名单（内容不属私有路径，刻意保留并记录）：go-edit.obo 的「withdrawn」为 GO 本体正常英文；`code_snapshot.zip::Code/ReleaseScope.txt` 的「Withdrawn analyses/remain withdrawn」为学生实质性分析状态披露，**删改即篡改，保留并建议由学生自行决定去留**；compare_lawlor_joint_components 注释「withdrawn scoring configurations」同理。

**哈希保护核验**：lawlor_mixture_protocol.json frozen_files 的 19 个 sha256 **值**原样保留，仅路径键匿名化为 `<PROJECT_ROOT>\…`（原始包键仍含 E:/ 证明原件未动）；两 publication_before.json 各 1 条锁（Repro Guide docx）随内容变化刷新。

**哈希链刷新（`refresh_chains.py`，修补首版只认字符串值的缺陷——实际值为 {bytes, sha256} 字典）**：FILE_MANIFEST 113+2 条、RELEASE_MANIFEST 113+3 条刷新；抽查 5 文件 sha256+bytes 与清单全一致。3 文件天然不在清单（嵌套快照 docx、canvas.tsx、审计影子脚本 `_nc78_report_shadow.py`——**注意：该影子脚本系审计轮写入快照的工件，不在学生原始交付物内，正式交付包应剔除，v10 起在交付建议中显式列出**）。

**零命中复扫（`verify_zero_hit.py`，特异性标记 + zip 成员深扫）**：2,002 文件 0 残留，exit 0。

**交付物**：`_nc78_v10_cleanup/` 下 patched/ 全量净包、enumerate/analyze/clean/refresh/verify 五脚本、PATCH_LOG.json（末次幂等 pass 记录）、CHAIN_REFRESH.json。

## v10 续：P0-2 R01 Lawlor 重建可行性裁定 + 重建套件交付

**探测结论（2026-11-14 实测）**：
- 本机无 R/Seurat 环境 → 不能就地重建，走「交付一键重建套件」分支
- HCA Azul 确认项目 efea6426 寄存 **Rds×3**（RNA 480,584,213 B / HTO 4,759,210 B / ADT 21,609,958 B）；下载端点实测在线（Range GET 206 + gzip magic），HTO Rds 已实际下载且尺寸精确命中
- **实测纠正套件假设**：公开 HTO 矩阵行名为细胞类型哈希抗体（Bcell-/Mono-/Tcell-/control-），**并非** {Baseline, CD3_CD28, LPS} 条件标签——条件标签只存在于作者处理后 Seurat 对象
- 作者处理后对象（`CZI_Fourth_Run_no_doublets_pairwise.*.seurat.output.Rds`）经全源排查（HCA/GitHub/figshare/shiny 数据目录）确认**未公开寄存** → cells.csv 指纹级核验公开不可达；npz 层（16,382×23,503 契约）仅计数矩阵可公开重建
- 细胞条形码实测形态 `<N>-Sample_<barcode>`，契约中 cell_id/Run_Identifier 派生路径确认可行

**交付物 `results/audit/_nc78_r01_rebuild_kit/`**：manifest.json（钉定 uuid/version/size/URL + 契约 + 缺口）、download_sources.sh（尺寸校验）、rebuild_lawlor_inputs.R（含作者对象合并分支，已修正 HTO 假设）、assemble_npz.py（23,503 Kang 序重映射）、verify_fingerprints.py（冻结指纹对照）、README.md（含 Figure 2H/I 三档降级预案 A/B/C）。Python 件 py_compile 通过；下载通道实测。

**裁定**：R01 状态 = 「指纹级恢复配方 + 一键套件已交付；字节级核验依赖作者私有对象，需回告学生提供该对象或采纳降级预案」。

## v10 续二：P2 批量交付（行动项 ⑧⑨⑩⑪）· 2026-11-14

交付目录 `results/audit/_nc78_v10_p2_deliverables/`：

**⑧ Zenodo 镜像处置（`zenodo_mirror_disposition.md`）**：结论「可选加固，暂缓执行，待用户定夺」。实测确认 tcga_RSEM_gene_tpm.gz（741MB）为外部原始输入、按设计不入包（RAW_DATA_INDEX 全文 0 命中 RSEM）；Xena 公开端点 + 脚本钉定文件名已满足常规可用性声明；镜像上传需用户 Zenodo 凭证，审计侧无权代办。

**⑨ SourceData 补遗双文档**：
- `FACS.md`：figshare 5829687（Tabula Muris Senis Smart-seq2 FACS v2）出处 + 本机指纹（FACS.zip 304,170,230 B / md5 95a27f3a…，18 组织成员表）+ 包内 groundtruth_eight_metrics_20261026 链路印证（Marrow-counts.csv 270,049,725 B 与 zip 成员逐字节一致）；指纹存 `facs_fingerprints.json`。
- `TCGA_PURITY_provenance.md`：**核心裁定——项目不消费任何外部 purity 注释文件**，纯度校正为自算 ESTIMATE 式 ssGSEA 混杂分（官方 SI_geneset.gmt 签名硬编码于脚本，blob SHA d5dda04e…钉定）；输入三件套（tcga_RSEM_gene_tpm.gz + probemap.tsv + v44 对表）与输出 nc49_tcga_purity.csv（66 行）契约成文；重放脚本 `notebooks/_nc78_replay_nc49_tcga_purity.py` 存在且 nc78 轮已实际重放（L3 级）。

**⑩ 脑 h5ad 内部指纹入档（`brain_h5ad_internal_fingerprints.json`）**：h5py 只读元数据级扫描（X 矩阵值不加载），五件全录得——

| 文件 | shape (n_obs × n_vars) | nnz | obs/var 列名 sha256 前 12 |
|---|---|---|---:|
| neurons/MGE_interneuron.h5ad | 222,434 × 58,232 | 1,101,052,120 | 2e1a8dc79953 / 2228a214653d |
| neurons/Thalamic_excitatory.h5ad | 85,546 × 58,232 | 585,164,772 | 同上 |
| neurons/Upper-layer_intratelencephalic.h5ad | 455,006 × 58,232 | 2,833,597,491 | 同上 |
| Nonneurons.h5ad | 888,263 × 59,480 | 1,973,759,385 | 86380c872b7e / 869a328b4e7c |
| human_brain_atlas_microglia.h5ad | 91,838 × 58,232 | 144,547,245 | 2e1a8dc79953 / 2228a214653d |

三件 Siletti 神经元 + microglia 共用同一 obs/var 列名指纹（同批构建），Nonneurons 为另一构建批次——指纹差异本身即批次 provenance 证据。神经元三件 n_obs 合计 762,986。

**⑪ 红队文档公开处置（`redteam_docs_disposition.md`）**：结论「不随投稿包公开，无需处置」。红队文档位于 `results/audit/`（工作区），不在投稿包目录树内，随包泄漏面为零；残留风险仅在「未来整仓公开」场景，已建议届时单独立项。

**P2 状态**：⑧⑨⑩⑪ 四项全部闭环（两项成文结论 + 两份出处文档 + 一份指纹档案）。

## v10 末节：交叉验证（终段）· 2026-11-14

全文见 `results/audit/_nc78_v10_crossval_report.md`。四线独立复核全过：
1. **零命中复扫独立重跑**：2,002 文件 0 残留 exit 0；
2. **清单对账**（新代码路径抽样重算）：canonical 20/20 + files 区段 25/25，0 bad/0 miss；
3. **R01 套件 dry-run**：py_compile / bash -n / manifest 契约关键值（efea6426、16,382、23,503）全过；
4. **sha 保护核验**：lawlor 19 冻结指纹值原包=净包；两 publication_before 锁字节级一致（误刷新还原后再确认）。

**v9 行动清单 11/11 闭环，交叉验证 4/4 通过。** 遗留三件均为用户决策/凭证事项（Zenodo 镜像、Lawlor 作者对象、整仓公开时 audit 剔除），非审计缺陷。nc78 复现性审计任务线至此收束。
