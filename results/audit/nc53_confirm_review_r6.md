# R6 可复现性 nc53 确认轮终审 — HEAD 4a7a34c

审稿人：R6-repro 日期：2026-09-24
依据：results/audit/nc52_final_review_r6.md（我上轮报告）+ nc53_final_review_round_2026-09-24.md（修复汇总），全部条件项已对照当前文本/输出文件/远端记录做 ground truth 复核。

## 本轮亲验记录

- HEAD = 4a7a34c，工作树干净；pyproject.toml / cki/__init__.py = 0.5.1
- `spot_check.py`：46 断言 **ALL CHECKS PASSED**；`pytest`：**29 passed**（在 4a7a34c 上重跑）
- GitHub API（非缓存）：Release v0.5.1 (id 395585738) 资产 id **586271335**，digest `sha256:abbcbc02…73`；本地工作树 zip sha256 = `abbcbc02…73` **逐字节一致**（注：WebFetch 页面缓存仍显示旧资产 c810de27，API 为准，资产确已替换）
- Zenodo record **22938380** 已上线：Version v0.5.1，标题 "…nc52 expert-panel revision (**Nature Communications**)"，发布 2026-09-24，归档 1.6 GB——上轮唯一硬条件闭环
- SI xlsx 实测 19 sheets（'Table 1'…'Table 19'）；SI 表注已带 "CKI_Supplementary_Tables_NC.xlsx (sheet Table N)" 指针（Table 1–4 亲见）；MS "Supplementary Tables 5–19" 口径一致
- MS 口径复核：Methods "3,567 samples, of which 3,535 enter … leaving 366"、"34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table"、"package v0.5.1"；SI 5.12 同口径（34,828/478/35,306）；无 "0.5.0" 遗留引用
- Data availability 已补 GTEx（accessed September 2026）与 Microglia supercluster（含仓库内路径）——我上轮 Minor #7 已解决
- 种子声明链：MS "seeds fixed at 42 unless noted (SM 5.13)" ↔ SI 5.13 ↔ Guide 1.4 例外清单，一致
- SI 引用的 results/tcga_linear_norm_v44_all_pairs.csv 存在（4.38 MB）

## A. 逐条裁定表

| # | 条件项 | 裁定 | 证据（当前文本/记录） |
|---|---|---|---|
| 1 | 版本面全同步（包/MS/SI/Guide/Dockerfile） | **RESOLVED（一处外观残留）** | pyproject:7 `version = "0.5.1"`；__init__:38；MS L86 "package v0.5.1"；SI 三处 v0.5.1（L88/L117/L229）；Guide L22 "Version: 0.5.1" + L615 "Install CKI v0.5.1"；Dockerfile L1 "(v0.5.1)"。残留：Dockerfile L6/L7 build/run 命令仍 `cki:0.5.0`（外观） |
| 2 | Code availability（v0.5.1 + tag + 新 version DOI + Release 资产替换） | **RESOLVED** | MS L126："cki source code (v0.5.1)…(tag v0.5.1)…version DOI for v0.5.1: 10.5281/zenodo.22938380"；Zenodo 22938380 = v0.5.1 且元数据已改 Nature Communications；Release 资产 586271335 digest 与本地 zip 一致 |
| 3 | run_all.py Phase 6f (nc52) 作用域说明 | **RESOLVED** | run_all.py L49–53："Phase 6f (nc52 analyses, not yet wired into run_all): nc52_tcga_excc_main, nc52_tcga_composition, nc52_lihc_cox_excc (R), nc52_gtex_kn, … see the [Guide 5.13]"——按约定的"注明作用域"方案落实 |
| 4 | 沿留 proof 外观项（pyproject description / CI ubuntu-only / Guide 5.6f 6.67） | **RESOLVED（确认沿留）** | 三项均为外观级、不影响数值复现，确认接受留至 proof 阶段处理 |
| 5a | Data/Code availability 可执行性闭环 | **RESOLVED** | GEO GSE109774/GSE96583、CELLxGENE collection ID、GTEx（2026-09）、microglia 数据路径、HRT Atlas、MSigDB 本地镜像均在文；DOI/包版本/种子钉死全链一致 |
| 5b | SI xlsx 19 sheets 与 docx 指针一致 | **RESOLVED** | openpyxl 实测 19 sheets 命名 Table 1–19；SI 各表注补 sheet 指针；MS "Tables 1–4 cited in main text; 5–19 …"一致 |

## B. 新增问题

**Major：无。**

**Minor：**
1. 【修复引入｜发布链时序】tag v0.5.1 仍指 7133b43（nc53 修复前），Zenodo 快照随之封入修复前的 manuscript docx/txt 与 15-sheet xlsx；nc53 修复在 69e3567/95a4cf7/4a7a34c。经 `git diff 7133b43..4a7a34c` 核实：**分析代码（notebooks 分析脚本、cki、scripts、tests）与全部数值结果文件零差异**，差异仅限文档生成器（68_gen_supplementary_nc.py）、两个 xlsx、manuscript 文本与 audit 日志——故"代码/数据可复现"声明在 tag 树上完全成立，Release 资产（投稿 zip）已是修复版。建议（不阻塞）：proof 阶段将 tag 移至 4a7a34c 或切 v0.5.2 使 Zenodo 快照与投稿包逐字节一致。
2. 【修复残留｜外观】Dockerfile L1 已改 (v0.5.1)，但 L6/L7 `docker build/run -t cki:0.5.0` 命令未同步。
3. 【既有遗留｜指针漂移】SI 5.12 写 "(Reproducibility Guide, Section 5.10c)"，而 ex-CC 默认链在 Guide 5.13（5.10c 自身已标注 superseded 并重定向）——读者可循着重定向找到，建议 proof 阶段直引 5.13。

## C. 总分

- soundness 8.5 / novelty 7 / significance 6 / presentation 8.5
- **overall：8.0/10，推荐：accept**
- 一句话理由：上轮全部硬条件（Zenodo v0.5.1 record、DOI 写回、资产替换、版本面、19 sheets 指针）经 ground truth 复核逐条闭环，数值可重算性三轮亲验（spot_check 46 + pytest 29 + sha256 比对）零失配，残留项均为 proof 阶段外观级。
