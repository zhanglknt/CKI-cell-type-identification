# nc55 盲审报告 — R6 可复现性/计算基础设施审稿

- **评审对象**：CKI 方法学论文终稿 v0.5.2（工作树 HEAD `5a5ae6d`，tag `v0.5.2` → commit `fb782c9`）
- **评审人角色**：Nature Communications 可复现性/计算基础设施审稿人（软件打包、流程可复现性、数据/代码可用性、种子与版本钉死）
- **评审方式**：基于当前文本与仓库实况独立重审，所有数字/路径/DOI 均经本轮 ground-truth 复核（含在 `git archive v0.5.2` 干净归档上的实测），未沿用上轮结论
- **评审日期**：2026-09-25

---

## 总评分：7.0 / 10

## Verdict：Minor revision（小修）

论文主体复现基础设施（锁文件、Dockerfile、CI 3.10–3.14、种子披露、pytest、run_all、DOI 发布链）已达到 NC 投稿标准，DOI 链本轮已完全闭合并经实测验证。但本轮在**归档工件（tag v0.5.2 = Zenodo 22949350）上实测发现验证层断裂**：复现指南宣称的头号验证入口 `spot_check.py` 在归档上无法运行，其 TCGA 断言停留在已被取代的退役口径，且指南多处 "data: results/..." 核验指针指向归档中不存在的文件。两个问题均属机械可修（补追踪/镜像文件 + 重定向断言），不涉及科学结论，故定小修。

---

## 强项（本轮实测确认）

1. **DOI 发布链已完全闭环，且经本轮逐项实测**：
   - version DOI `10.5281/zenodo.22949350` 在 doi.org 现返回 **200 可解析**（此前 DataCite 激活滞后问题已消失）；
   - concept DOI `10.5281/zenodo.20405458` 现已 **301 重定向至 `zenodo.org/records/22949350`**（v0.5.2 记录），此前"仍指向 v0.5.0 Genome Biology 记录"的问题已解除；
   - Zenodo API 核验 record 22949350：title 含 "v0.5.2 … (Nature Communications)"、version `v0.5.2`、publication_date 2026-09-25、related_identifier 指向 GitHub tree v0.5.2（isSupplementTo）、conceptdoi 与 MS 所写一致；
   - MS Code availability（`results/CKI_Manuscript_NC_fulltext.txt:126`）双 DOI 写回与远端实况一致。
2. **Release 资产完整性**：GitHub Release v0.5.2（id 396170102）资产 sha256 `1271fc40…218ef` 与本地 zip readback 一致。
3. **版本面全同步 0.5.2**：`pyproject.toml`、`cki/__init__.py`、MS、SI、Guide（L22 "Version: 0.5.2"、L615 "Install CKI v0.5.2"）、Dockerfile（注释 + `docker build -t cki:0.5.2` + `pip install -r requirements-lock.txt`）。
4. **依赖钉死与 CI**：`requirements-lock.txt`（pip-freeze）+ Dockerfile 锁安装；CI matrix Python 3.10–3.14。
5. **测试体系**：`pytest tests/ -q` 本轮实测 **29 passed**（22 smoke + 7 reference-value）；`tests/test_reference_values.py:25-30` 采用 `results/` 与 mirror 双路径查找 + 缺失自动 skip 的健壮设计。
6. **种子与统计口径披露**：MS L116 "seeds fixed at 42 unless noted (Supplementary Methods 5.13)"；L120 完整披露置换/ bootstrap B 值与 MC 误差去向。
7. **Data availability 覆盖全面**（L123-124）：GEO GSE109774 / GSE96583、CELLxGENE collection ID 283d65eb…、GDC、GTEx Portal、cBioPortal、MSigDB/Enrichr，访问日期齐备。
8. **MIT LICENSE 在 tag 中**；MS 当前 TCGA headline（摘要 "3,535 TCGA samples … 1.11–2.46"；L47 "mean NN/TT ω: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11"；L112 "34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table"）与已追踪的 `results/nc52_tcga_pancancer_excc.csv` 抽查一致。

---

## Major 清单（2 条）

### Major 1：指南宣称的头号验证脚本在归档工件上不可运行，且 TCGA 断言停留在已退役口径

**证据 A（归档实测崩溃）**：在 `git archive v0.5.2` 干净解包（即 Zenodo 归档内容）上运行 `python scripts/spot_check.py`，立即在第 37 行崩溃：
`FileNotFoundError: ... results/phase34_v2_summary.csv`。
脚本模块级读取 13 个输入文件、**无任何 missing-file skip 守卫**；其中 **7 个在 tag v0.5.2 中不存在**：`phase34_v2_summary.csv`（L37）、`tcga_composition_check.txt`（L49）、`brain_setlevel_tests.csv`（L100）、`reviewer_brain_splithalf_summary.txt`（L112）、`reviewer_ts_splithalf_summary.txt`（L114）、`phase33_v3_human_pairs.csv`（L126）、`kang_ifnb_demo_summary.json`（L134）。其中 5 个在归档内的 `CKI_Reproducibility_Package/reference_results/` 有镜像，但脚本只读 `results/`；`phase34_v2_summary.csv` 与 `phase33_v3_human_pairs.csv` 在归档中**两处均无**。对照之下，同仓库的 `tests/test_reference_values.py` 已有双路径 + skip 的正确实现，spot_check 未采用。

**证据 B（断言口径脱节）**：`spot_check.py:33-38` Section 1 注释自引 "Manuscript: 1.23-2.32"，硬编码期望值 `{LUAD 2.319, LUSC 1.769, LIHC 1.233, KIRC 2.192, BRCA 1.509}`——这是已被取代的 legacy softmax median 口径（Guide L205 自述 "superseded by the linear-normalization recompute"）；当前 MS headline 为 ex-CC linear mean（1.11–2.46）。脚本**从不读取**已追踪的 `results/nc52_tcga_pancancer_excc.csv`，即论文最重要的单组定量声明（TCGA 五癌 NN/TT 比值）在宣称的 spot-check 中**零断言覆盖**。

**证据 C（指南描述同步失真）**：复现指南 L314 与 L640 均将 spot_check 描述为 "46 assertions recomputing headline numbers directly from the authoritative result files: TCGA NN/TT **median ratios** …"，且 L640 以 "[✓] Data-driven spot-check" 列入投稿前核验清单——该清单项在归档上不可执行、描述口径亦非当前 headline。

### Major 2：复现指南的核验路径大量引用归档中不存在的结果文件

tag v0.5.2 的 `results/` 顶层仅 66 个文件（HEAD 追踪 60 个），而作者工作机磁盘有 354 个；指南以 "data:"/"Output:" 指向的许多文件在归档中缺失，读者无法按指南完成核验（指南全文从未提及 `reference_results/` 镜像的存在，也未披露 .gitignore 白名单追踪策略）。本轮逐条核实的实例：

| 指南引用 | 引用处 | 归档实况 |
|---|---|---|
| `results/mouse_splithalf_v44.csv`（7.70 校准常数 300 个 ω 源值） | L98、L211、L341、L588、L631 均作 "data:" 引用 | **tag 中无、mirror 中亦无**；仅两阶段 bootstrap 汇总 `nc52_stats_baseline_twostage_bootstrap.csv` 在 tag（CI [6.38, 9.82] 可核对，但源数据不可查） |
| `results/mouse_splithalf_v44_summary.json` | L341 "Outputs:" | tag 中无 |
| `results/brain_setlevel_tests.csv` | L205 "Output:"、L631 附近 | tag `results/` 无（mirror 有，但指南未指路） |
| `results/reviewer_brain_splithalf_summary.txt` / `reviewer_ts_splithalf_summary.txt`（内部基线 9.73/7.67） | L263、L631 | tag `results/` 无（mirror 有） |
| `results/phase33_v3_human_pairs.csv`（5,151 行库存表） | L640 附近 checklist | **tag 与 mirror 均无** |
| `results/tcga_composition_v44.txt` | L329 "Outputs:" | tag 中无 |

注：本 Major 不质疑这些数字本身（多数可由已追踪的汇总文件或端到端重跑支撑），而是质疑**指南宣称的"按图索骥"核验路径在归档工件上断裂**——这正是可复现性评审的核心对象。

---

## Minor 清单（6 条）

1. **Data availability 对仓库内容过度声明**（MS L124）："data/human_brain_atlas_microglia.h5ad in the companion repository" 与 "local mirror data/tcga/hallmark_2020.gmt in the companion repository"——经核，两文件在 HEAD 与 tag v0.5.2 中均未追踪（`data/` 仅 16 个 kang_ifnb 文件入库）。建议：小规模 `.gmt` 直接入库；h5ad 改为"经 CELLxGENE collection 下载（见 data/README_data.md）"。
2. **指南 checklist 悬垂指针 "Section 5.7h"**（L640、L641 两处）：指南 5.x 节为 5.1–5.13（5.7 = "v41 Blind-Review Analyses"，无字母子节），"5.7h" 仅在这两处自指出现；SI 全文亦从未提及 spot_check。
3. **`tests/test_reference_values.py` 镜像路径在 HEAD 已过时**：L19-22 `MIRROR = CKI_Reproducibility_Package/reference_results` 在 tag 中成立，但 HEAD（46fa93a root cleanup）已将包迁至 `archive/CKI_Reproducibility_Package/`（294 文件内容一致）；测试靠 `results/` 回退仍通过，但 docstring（L5-9）与路径需同步。建议顺手让 spot_check 复用同一 `_find` 双路径逻辑。
4. **tag 与最终文本的时序差**：tag v0.5.2（fb782c9）早于 phase-2 提交链（HEAD 5a5ae6d：DOI 写回 + Release 资产刷新 + root cleanup + 审计文档；317 文件、873 插入，无分析代码/数值改动）。归档 zip 内的 MS 文本不含 version DOI 自引句，属常见可接受现象，但建议在 Release notes 注明；若期刊要求归档包与投稿稿逐字节一致，需在文本冻结后切 v0.5.3。
5. **`spot_check.py:93` 自指断言零价值**：`check("min q (first Strong row)", 0.5202, 0.5202)` 以字面量对字面量，应实际从 `brain_bs_null_summary.txt` 解析 q 值再断言。
6. **指南文件清单（L487-631 一带）未标注文件在归档中的可得性**：建议对每条 "data:"/"Output:" 引用标注 [in archive] / [regenerate via notebook N]，与 Major 2 的修复一并完成。

---

## 上轮 Major #2–#5 复核意见

- **上轮 Major #2（依赖零钉死）— 维持 RESOLVED**：`requirements-lock.txt` + Dockerfile `pip install -r requirements-lock.txt` + Guide 安装段，本轮复核无异动。
- **上轮 Major #3（nc50 microglia 验证未入复现体系）— 维持 RESOLVED，但附连带警示**：Guide 5.12 nc50 章节、spot_check Section 10（6 断言）、`nc50_brain_atlas_microglia.csv` 在 tag 中均在位；惟 spot_check 在归档上不可运行（本轮 Major 1），nc50 断言的实际可达性受 Major 1 连带影响，修复 Major 1 后自动恢复。
- **上轮 Major #4（run_all.py 停留 GB v40）— 维持 RESOLVED**：`run_all.py:49-53` Phase 6f (nc52) 作用域说明段在位。
- **上轮 Major #5（SI 脚本索引指向废弃/不存在脚本）— 维持 RESOLVED**：SI 索引已修正为 08d/08e，本轮未复发。

**附：上轮 Major #1 现况更新（虽非任务书要求复核项，但此前轮次我持续标记，须如实更新）**：Zenodo 链本轮已完全闭环——version DOI 可解析、concept DOI 已重指向 v0.5.2 NC 记录、MS 写回一致，此前"concept DOI 仍指向 v0.5.0 Genome Biology 记录"与"version DOI doi.org 不可解析"两项观察**均已消失**，不再构成问题。

---

## 具体修改建议（按优先级）

1. **修 Major 1（spot_check）**：
   (a) 将 13 个输入文件的读取改为 `results/` → `CKI_Reproducibility_Package/reference_results/` 双路径查找 + 缺失 skip（直接复用 `tests/test_reference_values.py:_find` 模式）；
   (b) 把 `phase34_v2_summary.csv`、`phase33_v3_human_pairs.csv` 补入追踪（或镜像），使 7 个缺失输入全部可达；
   (c) Section 1–2 断言改读 `results/nc52_tcga_pancancer_excc.csv`，期望值更新为当前 headline（LUAD 2.46 / KIRC 1.88 / LUSC 1.71 / BRCA 1.57 / LIHC 1.11，mean ex-CC；34,828 pairs / 3,535 samples / 478 dropped），退役口径断言移入显式标注 "legacy" 的可选段；
   (d) Guide L314/L640 描述同步改为 mean 口径。
2. **修 Major 2（指南-归档一致性）**：对白名单追踪策略在指南开头加一段说明；将 Major 2 表中缺失文件补追踪或补镜像（尤其 `mouse_splithalf_v44.csv` 及其 summary.json——7.70 是全篇 ω_cal 的锚）；或在每条引用处标注再生成路径。
3. **Minor 打包**：Data availability 两处措辞（commit gmt / h5ad 改为外部下载表述）；删除或修正 "Section 5.7h"；同步 test_reference_values 的 MIRROR 路径与 docstring；修 spot_check L93 自指断言；Release notes 注明 tag 与 phase-2 文本时序。
4. **验证闭环**：修复后在 `git archive v0.5.3 | tar -x` 干净归档上重跑 `spot_check.py` + `pytest` + 指南 Section 6 checklist 全项，确认归档自洽。

---

*R6-repro · nc55 盲审 · 全部结论基于当前文本与仓库实况复核*
