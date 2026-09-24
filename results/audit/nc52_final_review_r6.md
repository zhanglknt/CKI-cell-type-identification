# R6 可复现性终审报告 — v52 (commit 7133b43, tag v0.5.1)

审稿人：R6-repro（可复现性/计算基础设施） 日期：2026-09-24
对象：results/CKI_Reproducibility_Guide_NC.docx（全文导出核对）、MS Code availability、仓库发布链（tag/Release/CI/Zenodo）

## 本轮亲自执行的验证（ground truth 复核）

| 验证项 | 结果 |
|---|---|
| HEAD / tag | HEAD = 7133b43，`git tag --points-at HEAD` = v0.5.1 ✓ |
| 包版本 | pyproject.toml `version = "0.5.1"`；cki/__init__.py `__version__ = "0.5.1"` ✓ |
| CI 矩阵 | .github/workflows/ci.yml：3.10/3.11/3.12/3.13/**3.14**（3.14 注释标明为验证环境版本）✓ |
| spot_check | `scripts/spot_check.py`（cki_env, Python 3.14.4）：46 断言 **ALL CHECKS PASSED**，含 nc50 microglia（ω 21.83/1.30、MWU P=5.49e-14、AUC=1.00 全部 [OK]）✓ |
| pytest | 29 passed（22 smoke + 7 reference）✓ |
| GitHub Release v0.5.1 | 页面存在，tag = 7133b43，资产 CKI_Submission_v50_NC.zip（11.7 MB）✓ |
| 资产完整性 | 本地工作树 zip 的 sha256 = `c810de27…0e48`，与 Release 资产页面所示 sha256 **完全一致**（git status 的 "M" 为时间戳噪声，内容相同）✓ |
| Zenodo concept DOI 10.5281/zenodo.20405458 | 仍解析到 **v0.5.0** 记录（"v47 submission package for Genome Biology"），**无 v0.5.1 version record**（webhook 卡住，已知项）✗ 待完成 |
| Guide | Version: 0.5.1；新增 5.12 nc50 Analyses 与 5.13 nc52 Analyses（a–k）；checklist 更新（ex-CC n=3,535、nc50 条目、29 tests）；结尾措辞改为 "within Monte-Carlo and floating-point tolerance" ✓ |
| SI 脚本索引 | 已改指 08d/08e（并注明 07c 输出在 superseded/）；13_phase35_method_comparison 修正 ✓ |
| 依赖钉死 | requirements-lock.txt（pip-freeze 锁）存在；Guide 1.2 指向锁文件；Dockerfile `pip install -r requirements-lock.txt` ✓ |

## 上一轮（v51r2）Major issues 处置核对

1. **档案/tag 与稿件不匹配** → 基本解决：tag v0.5.1 = HEAD 已 push、Release v0.5.1 资产 sha256 与本地一致、MS Code availability 已写 "(v0.5.1)…(tag v0.5.1)" 且 version DOI 行明确标注 "for v0.5.0"（过渡态准确）。**残留阻塞项**：Zenodo 无 v0.5.1 record（webhook 卡住，用户正在 zenodo.org 查状态）、元数据 "Genome Biology" 未改、MS version DOI 行待 phase-2 写回。在此之前，"are included in the Zenodo archive (concept DOI…)" 一句对 v0.5.1 尚不成立。
2. **依赖未钉死** → 已解决（requirements-lock.txt + Dockerfile 锁安装 + Guide 措辞）。
3. **nc50 验证缺失** → 已解决（Guide 5.12 + checklist + spot_check 46 含 microglia 断言，亲验通过）。
4. **run_all.py 陈旧** → 部分解决：已更新至 nc49/nc50（Phase 6d/6e、NC 图脚本、99_build_nc_v49 验证链），但 **grep 确认 run_all.py 仍不含 14 个 nc52_ 脚本**——自称 "Complete reproducibility pipeline" 的入口无法重跑 v52 默认 TCGA 主链（ex-CC）、GTEx、脑 donor bootstrap 与统计重采样。降级为 Minor（Guide 5.13 已逐脚本记录）。
5. **SI 脚本索引指向被取代脚本** → 已解决。

## 本轮新发现问题

**Major**：无（唯一阻塞项 Zenodo 写回为 team-lead 已知未完成项，如实注明而非新发现）。

**Minor**：
1. 【run_all.py】未编排 nc52 脚本（nc52_tcga_excc_main 等 14 个），与 "Complete reproducibility pipeline" 自述不符。建议：加 Phase 6f(nc52) 或在头注释明确其作用域为 v44–v50 编排、v52 以 Guide 5.13 为准。
2. 【Dockerfile 第 1/6 行】头注释与镜像标签仍为 `cki:0.5.0`（包已 0.5.1）。纯外观。
3. 【git status】tag 后工作树有 2 个 tracked 修改（results/figures_submission_nc/figure2.pdf、Supplementary_Fig_14.pdf）与未跟踪杂散文件（_tmp_gen_dbg.py、results/audit/_v052_release_create.py）。zip 已证实与 Release 资产逐字节一致；建议提交或确认两个 PDF 为重建同字节产物。
4. 【pyproject.toml description】仍为 "Cell-type Identity Index" vs 正文 "Cell-type Ka/Ks-inspired Index"（沿留）。仓库名 CKI-cell-type-identification 与正文 "not a classifier" 的定位存在命名张力，投稿后改包元数据即可，不阻塞。
5. 【CI ubuntu-only】MS 声称 "runs on Linux, macOS, and Windows"，CI 仅 ubuntu（沿留）。建议在 MS 或 README 注明 macOS/Windows 为本机使用验证、CI 覆盖 Linux。
6. 【Guide 5.6f】phaseC_calibrated_cis.csv 仍为 "deterministic division by 6.67"（legacy 常数）再生——沿留的外观不一致，文件本身已被声明 superseded 链覆盖，风险低。

## 评分（1-10，NC 标准）

- soundness: **8.5/10** — 两轮复审间作者把两位统计审稿人的核心质疑（伪重复 CI、ex-CC 队列、R Cox 重拟合、entry-cluster bootstrap）全部落实为新默认分析链且全部入 Guide/spot_check；数值可重算性我两轮亲验无失。
- novelty: **7/10** — 定位诚实（recombination of established ideas），增量在"design-matched null + 内部基线"的工程化组合。
- significance: **6/10** — 特异性优先筛查工具 + 有界假设生成目录；FDR 零存活、跨种不迁移限制了影响面。
- presentation: **8/10** — 文档体系与发布链已达可提交水准；残留为 run_all/Dockerfile 注释级别漂移。
- **overall: 7.5/10，verdict：accept（条件性）**

## 条件清单（投稿前必须完成）

1. **【阻塞】Zenodo v0.5.1 version record 生成**（webhook 恢复或手动上传 Release 资产），随后：MS Code availability phase-2 写回新 version DOI；Zenodo 元数据 "Genome Biology" → "Nature Communications"。完成前 "included in the Zenodo archive" 声明不成立。
2. **【建议，非阻塞】** run_all.py 增补 nc52 编排或注明作用域；Dockerfile 头注释 0.5.0→0.5.1；处理两个 tag 后修改的 PDF 与杂散文件。
3. **【沿留，可在 proof 阶段处理】** 包元数据命名、macOS/Windows CI 覆盖声明、phaseC 6.67 外观项。

结论：复现基础设施与验证 tooling 远超 NC 常规水平（spot_check 46 + pytest 29 + 构建 221/221 + Release 资产 sha256 一致，均经独立复核）；唯一硬条件是 Zenodo 归档写回，属生产流程事项而非科学修订。条件 1 完成即满足 NC 可复现性政策。
