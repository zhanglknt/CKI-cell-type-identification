# CKI (Nature Communications) — nc84 专家团问题全量核销与交叉验证报告

日期：2026-11-18/19　｜　基于 nc83 专家团盲审（`_nc83_review_expert_panel.md`，均值 5.92、6/6 Major、R6 `Return before review`）
用户指令：`解决所有问题后交叉验证`

---

## 1. 总判定

**本地投稿包已闭合：所有可在本地解决的问题全部修复，全链验证 0 failure。**
仅剩两项需要作者拍板的外部动作（§6），不影响包内自洽性。

| 指标 | nc83 | nc84 |
|---|---|---|
| 专家团均值 | 5.92 | 本轮未重审（结构性修复为主） |
| `check_figure_spec.py` | 12/15，退出码 1 | **15/15，退出码 0** |
| documented exception | SF6 依赖例外表 | **例外表清空，零依赖** |
| 六指标 ROC/DeLong 表 | 无（悬空引用） | **Supplementary Table 2c** |
| 版本/归档声明 | 声称 v0.6.4 Zenodo 归档（不实） | 改为可核验措辞 |
| 构建内联断言 | 232/232 | **240/240** |

---

## 2. P0 逐项核销

| # | 动作 | 落地 |
|---|---|---|
| 1 | 版本/归档红线 | MS「Code availability」两处、Guide 1.2 改为「earlier release / GitHub tag v0.6.4」，删除「v0.6.4 archive accompanies this submission」与「always resolves to latest」的不实表述；MANIFEST 注明 `v49` 是构建批次号。**远端 tag 发布见 §6，仍需裁定。** |
| 2 | SF1/SF3/SF5 重绘到 ≥5 pt | 多页矢量放大重排（`notebooks/114_recompose_suppfigs_nc84.py`），输出 `results/figures_nc84/Supplementary_Fig_{1,3,5,6}.pdf`；每页宽 ≤180 mm、primary ≥5 pt。实测 SF1 6.5 pt/3 页、SF3 5.5 pt/3 页、SF5 5.2 pt/4 页、SF6 5.5 pt/1 页。 |
| 3 | SF6 例外 | 转曲页原位修复 6 个 `_n` 下标（5 个 4.1→5.0 pt、1 个 3.3→5.0 pt），`_nc83_figure_exceptions.json` 置 `{}`，checker 删除例外改判分支。 |
| 4 | AUC 0.648 / 0.841 / −0.193 / P=0.002 归位 | 摘要与引言改为 KRAS–EGFR 判别语境；`P = 0.089` 与 AUC 拆开；KRAS–WT 判别数值（0.661 vs DE 0.736）本就在 SI 3.13。摘要 148 词、MAIN 5,000 词配平。 |
| 5a | 补六指标 ROC 表 + 修 `Supplementary Table 2a` | Table 2 在**同一 sheet 内**扩 `(c)` 块（不新增 sheet，17 sheet 不变）；6 行 AUC/DeLong CI/ΔAUC/SE/CI/z/P/Holm；MS 两处与 SI 两处指针改 `2c`；SI 独立秩和复算 6 个 AUC 与权威 CSV 零偏差。 |
| 5b | residence/migration 悬空引用 | 删除该从句（专家团允许「删句」）；SI 无对应框架，删后不再有悬空 Note 18 指针。 |
| 6 | 附图编号 F2 | **采用豁免 + SI 加注**（专家团推荐路线）：SI「Supplementary Figures」前插入 `Numbering note.`；实测正文首现序列 1–9 单调，SF10/SF11 为 Figs. 3/2 的伴生图保留系列号，跨轮引用稳定。 |
| 7 | 字数配平 | MAIN 5,000/5,000、摘要 148/150、Fig 4 图注 337/350、CL 509/530、Methods 3,228/3,300。 |

---

## 3. P1 逐项核销

| # | 动作 | 落地 |
|---|---|---|
| 8 | 校准「吸收」改条件式 | MS：残差 ~10% 仅在 design-matched permutation 下被吸收；绝对 `ω_cal` 比较继承残差；`ω_cal` 附「indicative, dataset-relative」限定。 |
| 9 | SF11 图注语义 | 补 `library-effect sensitivity statistics, not type-I error rates`、`Wilson intervals do not model donor clustering`、`two-way library-endpoint cluster-robust intervals`、5.5%/4.8%[3.8,6.1]/10.3% 三档 null。 |
| 10 | 核心宣称降级 | CL `specificity-first index`→`precision-first index`；`misreports least`→`tightest precision, not the lowest drift`；SI `specificity-first screen`→`precision-biased screen`（附 10x 0.51–0.53）；CL 四支柱补 10x pooled 限定；MS `misreported least`→`had the lowest exceedance`。 |
| 11 | 理论记号与定位 | CL `theory-backed` / `ω − 1` → `A scoped framework gives ω = α + E_f/E_b + ε`；MS `explicit estimand`→`scoped estimand`、`full correspondence`→`scoped correspondence`；Fig 4 图注改 `housekeeping-anchored class-level differences`。 |
| 12 | CNA 56% 语气 | 摘要/引言/Results/Discussion/CL 全部由 `accounts for / attributable to` 改为 `associated with (at most / ≤)`，并写明「assumed CNA-free normal reference / unmeasured-reference upper bound」；保留 42%、28%、40%、LIHC/KIRC 数字与 build/crossval 断言。 |
| 13 | 脑图谱降级 | 标题级改 housekeeping-anchored class-level differences；Limitations 补 PMI 与 ambient/doublet 让步；3.66 匹配值与 donor-stratified 3/10 本就在 Results。 |
| 14 | pseudobulk 聚合顺序 | SI SF3 图注删掉跨 pipeline 的 `9.73 / 7.70 = 1.26` 比值，改为「calibration constants are pipeline-internal」；MS/SI/Guide 口径一致。 |
| 15 | KRAS 临床价值 | 摘要已写 `group-level contrast only`、`not under a fixed panel`、`discrimination is weak`；Results 已有 `group-level association rather than a confirmed driver effect`。 |
| 16 | claim-to-test map | claim(5) 载体由 MWU 改为 sample-level cluster-bootstrap CI，MWU 明确 `descriptive complement only`；补两家族未联合校正与 4 donors 有效独立单元说明。 |
| 17 | ambient/doublet | 采用专家团允许的「明确让步」路线：MS Limitations 增补「nor were ambient RNA or doublets modelled」；PMI/RIN 原有让步保留。 |
| 18 | Guide 5.15 链路 | 5.14(c) 补 PSD 最小特征值 1.4×10⁻⁵ 与 4-donor wild-cluster（16 个 Rademacher 精确枚举 + 9,999 随机）；`mahalanobis_pairs.csv`→`mahalanobis_raw.csv`。 |

---

## 4. P2 逐项核销

| # | 动作 | 落地 |
|---|---|---|
| 19 | CL real-drift 指针 | `Fig. 2`→`Supplementary Fig. 11`（同时保留 `Fig. 2d` 的 AUC 0.80 与 `Fig. 3`）。 |
| 20 | `main-text Supplementary Fig.` | SI 两处删除；build 内联断言同步加反向检查。 |
| 21 | Guide 旧图号 | `4.2 … (Fig. 2c, d)`→`(Fig. 2c)`；`4.3 … Result 4 (Fig. 2)`→`(Supplementary Fig. 11)`；drift-ladder 三处 `Fig. 2`→`Supplementary Fig. 11`；`Fig. 2d, 2e`→`Section 3.11; Fig. 2d`；两处 `Fig. 2 heatmap` 清除。 |
| 22 | 版本串 | SI `v0.5.6`（2 处）、`0.5.4`（1 处）→`v0.6.4`；四个文档全局无 `v0.5.6 / 0.5.4 / v0.6.3`（XV8 新增断言）。 |
| 23 | 图注拼接残留 | `(f) 14.` / `(d) 6.` / `(d) 10.` 清除。 |
| 24 | CL 一页化 | 530→**509 词**（压缩 NC scope 句、四支柱重复描述、pan-cancer 长句、reviewers 引导句）；仍含 6 位推荐审稿人全名+邮箱，是否严格一页取决于排版，列为残余 minor。 |
| 25 | ORCID / 单位 / MANIFEST | MANIFEST 已注明 v49 是构建批次号；单位写法沿用既有规范；**两位共同作者 ORCID 无权威来源，未臆造，列为残余 minor**。 |
| 26 | 新增验证器断言 | 5 个验证器共新增 20+ 条：AUC 归位、Table 2c、悬空引用、理论记号、ambient 让步、版本唯一性、编号豁免注记、CL/Guide 语义同步、图合规接入 build；`clfull` 纳入 CL 同步检查。 |

---

## 5. 图件专项（独立复核）

- 内容零改动验证：对旧包 vs `results/figures_nc84/` 逐张抽取文字 token 求 Jaccard：SF1 **1.0000**、SF5 **1.0000**、SF3 **0.9794**（仅 `ac`/`bd` 两个被遮盖的旧面板标签碎片消失）；SF6 单页转曲件按构造保持版式不变。
- 配方纠偏：nc70 `figure_S<N>` 文件名与投稿 `Supplementary_Fig_<M>` 编号错位（SF3 实为 `figure_S2`、SF5 实为 `figure_S6`），重排脚本用 token 覆盖率复核后按实测映射取源，避免错换图面。
- checker 升级为逐页检查（取消 `PAGES=N` flag、跨页聚合 min primary/sub），例外依赖删除；`99_build_nc_v49.py` 在验证段调用 checker，对 15 张图验退出码。
- 接入构建：`SF1/3/5/6` 改从 `results/figures_nc84/` 取，`SF2/4/7/8/9` 仍从 STAGE 取；包内文件名、23 条目、zip 结构均不变。

---

## 6. 全链交叉验证（全部 0 failure）

| 环节 | 结果 |
|---|---|
| `99_build_nc_v49.py`（NO_ARCHIVE） | **240/240** |
| `_nc49_ms_verify.py` | 134/134 |
| `_nc49_si_verify.py` | 120/120 |
| `_nc49_cl_guide_verify.py` | 45/45 |
| `_nc51_xv8.py` | 65/65 |
| `_nc79_crossval.py`（本轮修复 6 条过时断言 + 崩溃锚点） | 71/71 |
| `_nc80_mj_crossval.py` | 137/137 |
| `_nc78_p0_crossval.py` | ALL PASS |
| `pytest tests/` | 29 passed |
| `scripts/check_figure_spec.py`（根包） | **15/15，退出码 0** |
| 三方逐 sha256（version3／根包／zip 内 23 条目） | **全部相等** |
| zip | 23 条目、13,634,695 B、sha256 `6e15e10f896c3b40…9879fd`、单文件最大 3.31 MB（<10 MB）、整体 <20 MB |
| 词额 | MAIN 5,000/5,000；Methods 3,228/3,300；摘要 148/150；CL 509/530；图注 max 337/350 |

**复跑核验注记（2026-11-19）**：本轮在最终交付态上再次独立复跑 `99_build_nc_v49.py`（NO_ARCHIVE，240/240）＋ 7 个验证器 ＋ 图检查 15/15 ＋ pytest 29/29 ＋ 三方逐 sha256，全部 0 failure。构建重新生成 docx/xlsx/MANIFEST 时 OOXML 内嵌时间戳刷新，zip 由 13,634,683 B／`f508eed031dbe9a1…` 变为 13,634,695 B／`6e15e10f896c3b40…`；按既有流程 `cp -f version3/CKI_Submission_NC/* CKI_Submission_NC/` 同步根包后，version3／根包／zip 内 23 条目逐文件 sha256 再次全部相等，内容语义无回归（验证器同步后重跑仍全绿）。上方表格以最新交付态为准。

`_nc79_crossval.py` 本轮修复：摘要锚点 `Inspired by Ka/Ks`→`Standard metrics confound cell-state shifts`（原脚本一启动即 IndexError），以及 6 条随 nc80/nc84 措辞演进而过时的字符串断言。

---

## 7. 仍需作者裁定 / 残余

| 项 | 状态 | 说明 |
|---|---|---|
| **A. 发布 v0.6.4** | **待裁定（P0 #1 的外部动作）** | 远端最高 tag 为 `v0.6.3`、Zenodo concept DOI 最新归档为 `v0.5.6`；MS/Guide 已改为诚实措辞，但仍声明「tag v0.6.4」。需 squash + force-push `main` + `tag -f v0.6.4` 并 force-push tag，声明才与可用版本一致。Zenodo 新建 v0.6.4 版本需 API token，未见凭据。 |
| **B. F2 编号路线** | **已按推荐路线（豁免 + SI 加注）落地，请追认** | 若改走全量重编号，需同步 11 个 PDF、SI 图注、正文/SI 引用、5 个验证器、Guide、MANIFEST、zip，代价 2–4 h 且打乱已固化引用链。 |
| C. 共同作者 ORCID | 残余 minor | 无权威来源，未填。 |
| D. CL 严格一页 | 残余 minor | 509 词，取决于最终排版。 |
| E. ambient RNA / doublet 对照、PMI/RIN 分层 | 采用「明确让步」 | 专家团允许的替代路线；若审稿要求补数据需另开分析。 |

---

## 8. 本轮改动文件清单

**源码**：`generate_manuscript_nc.py`、`notebooks/68_gen_supplementary_nc.py`、`generate_cover_letter_nc.py`、`notebooks/100_gen_reproducibility_nc.js`、`99_build_nc_v49.py`
**验证器**：`results/audit/_nc49_{ms,si,cl_guide}_verify.py`、`_nc51_xv8.py`、`_nc79_crossval.py`
**图件**：`notebooks/114_recompose_suppfigs_nc84.py`、`scripts/check_figure_spec.py`、`results/audit/_nc83_figure_exceptions.json`（清空）、`results/figures_nc84/*.pdf`、`results/audit/_nc84_previews/`
**配置/记录**：`.gitignore`（nc84 白名单）、`results/audit/_nc84_fix_report.md`、`.workbuddy/memory/2026-11-18.md`
**生成物**：`version3/CKI_Submission_NC/`、根 `CKI_Submission_NC/`、`CKI_Submission_NC.zip`
