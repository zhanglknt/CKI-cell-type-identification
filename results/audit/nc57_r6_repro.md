# nc57 终审报告 — R6 可复现性/计算基础设施审稿（v0.5.3）

- **评审对象**：CKI 终稿 v0.5.3（工作树 HEAD `3d220ac`；tag `v0.5.3` → commit `00e3652`；Zenodo record 22954782）
- **评审方式**：全部重新通读当版正文/指南关键段 + 逐项核销上轮问题 + 在 `git archive v0.5.3` 干净归档上实测验证层；所有数字/版本串取自当版文本或本轮实测，未引用旧轮记忆
- **评审日期**：2026-09-25

---

## 总评分：8.5 / 10

## Verdict：**Accept**（小条件：投稿前复核两个 DOI 的解析/指向，见 Minor N1/N2）

上轮 2 条 Major 全部修复并经归档实测验证：验证层（spot_check + pytest）如今在投稿归档工件上端到端可运行，校准源数据入库，追踪策略成文披露，版本面/DOI 面/声明面与仓库实况一致。剩余 3 条 Minor 均为机械确认/清理项。

---

## 一、上轮（nc55）问题逐条核销

### Major 1（spot_check 归档崩溃 + 断言退役口径 + 当前 headline 零覆盖）— **RESOLVED**

- **归档实测**：`git archive v0.5.3` 干净解包上 `python scripts/spot_check.py` 运行到底，**ALL CHECKS PASSED**（上轮同法实测在 L37 立即 FileNotFoundError）。13 个模块级输入经逐文件核验**全部在 tag v0.5.3 中**（上轮 7 个缺失）。
- **口径重写**：Section 1 改读 `results/nc52_tcga_pancancer_excc.csv`，注释 "Manuscript: 1.11-2.46"，期望值 {LUAD 2.464, LUSC 1.708, LIHC 1.112, KIRC 1.880, BRCA 1.567}，与当版 MS L47 "mean NN/TT ω: LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11" 及摘要 "ratio 1.11–2.46" 一致；Section 2 k_n 反转同源改读 excc（2.60/2.53/2.06/3.61/2.78，与 SI L186 主表口径一致）。当前 headline 已有断言覆盖。
- **指南描述同步**：Guide L314 已改为 "TCGA NN/TT **mean ratios (ex-CC linear caliber)**"。
- 说明：作者未采用我建议的双路径 `_find`+skip 方案，而选择了"全部输入入库"方案——等效且更强，认可。

### Major 2（指南 "data: results/..." 指针指向归档缺失文件）— **RESOLVED**

- 上轮逐条核实的缺失文件**均已入 tag v0.5.3**：`mouse_splithalf_v44.csv`（7.70 校准 300 个源 ω 值，+301 行）与 `_summary.json`、`brain_setlevel_tests.csv`、两个 `reviewer_*_splithalf_summary.txt`、`phase33_v3_human_pairs.csv`（+5,152 行）、`kang_ifnb_demo_summary.json`。
- **系统性修复**：Guide L491 新增 "Repository tracking policy" 段，明确披露白名单追踪机制、验证子集覆盖 spot_check/pytest 全部输入、`archive/CKI_Reproducibility_Package/reference_results/` 镜像（并注明 tag 中位于根级 `CKI_Reproducibility_Package/reference_results/`）、未追踪未镜像文件经 Section 5 脚本再生成。历史分析日志节引用的少数退役文件（如 `tcga_composition_v44.txt`）由此获得"再生成路径"的合法地位。

### Minor 逐条

| # | 上轮问题 | 裁定 | 证据 |
|---|---|---|---|
| 1 | Data availability 称 h5ad/gmt "in the companion repository" 但未入库 | **RESOLVED** | `data/tcga/hallmark_2020.gmt` 已在 HEAD 与 tag 追踪；h5ad 句已改写为 "regenerable via notebooks/nc50_brain_atlas_microglia…"（MS L124） |
| 2 | 指南 "Section 5.7h" 悬垂指针 | **撤回（上轮误报）** | 本轮发现 5.7 节子项为缩进字母格式（"  h. "），**5.7h 真实存在**："h. Data-driven verification entry points"，内容即 spot_check.py 与 test_reference_values.py 的文档（Guide L313–316），指针有效。上轮我的 grep 模式未匹配该格式，特此更正 |
| 3 | test_reference_values MIRROR 路径过时 | **RESOLVED** | L19-22 已改 `archive/CKI_Reproducibility_Package/reference_results`，docstring 同步；Guide L491 还额外披露了 tag 与 HEAD 的镜像位置差异 |
| 4 | tag 早于 phase-2 DOI 写回 | **RESOLVED（文档化）** | v0.5.3 仍为 tag=phase-1（00e3652）、写回在 phase-2（cbae40）；但 Zenodo 记录描述已明确写明 "the v0.5.3 version DOI is written back in the phase-2 commit on main"，且 Release 资产为 phase-2 构建，透明度达标 |
| 5 | spot_check L93 自指断言（0.5202 vs 0.5202） | **RESOLVED** | 现 L88-89 实读 `brain_bs_null_results.csv` 计算 `q_fdr.min()` 再断言 0.5202（tol 5e-4） |
| 6 | 文件清单缺可得性标注 | **RESOLVED** | L491 追踪策略段统一覆盖 |

### nc56 轮 R6 相关条目复核

- X8：MS L126 已补 "(continuous integration covers Linux; macOS and Windows are verified on local workstations)" ✓
- S4：SI L135 指针 "Section 5.10c" → "Section 5.13a"，目标在 Guide 5.13 真实存在（L385 "Section 5.13a-e"、L596/597 同引）✓
- R1：pyproject description = "Cell-type Ka/Ks-inspired Index: a framework for quantifying baseline-normalized transcriptomic remodeling"（去掉了旧 "Cell-type Identity Index"）✓
- SI Note 14：全文无 "Python 3.13" 残留；L215/L258 均为 Python 3.14 / 3.14.4 ✓

---

## 二、当版版本面 / DOI 面一致性核验（任务书重点）

| 面 | 值 | 核验结果 |
|---|---|---|
| pyproject.toml / cki/__init__.py | 0.5.3 | ✓ L7 / L38 |
| Dockerfile | 注释 v0.5.3 + `docker build -t cki:0.5.3` | ✓ L1/L6-7 |
| MS Code availability (L126) | "(v0.5.3) … (tag v0.5.3) … concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.3: 10.5281/zenodo.22954782" | ✓ 与远端实况一致（记录元数据核符） |
| SI | v0.5.3 ×3（L88/L117/L229） | ✓ |
| Guide | L22 "Version: 0.5.3"、L616 "Install CKI v0.5.3" | ✓ |
| Zenodo record 22954782（API 核验） | title 含 "v0.5.3 … (Nature Communications)"；version v0.5.3；state done / status published；publication_date 2026-09-25；conceptdoi 20405458；is_last=true；related → GitHub tree v0.5.3；MIT；资产 zip 1.57 GB | ✓ |
| GitHub Release v0.5.3 | id 396368672；资产 587973498 `CKI_Submission_v50_NC.zip`，digest sha256:246f1bfa…19ed | ✓（本地 zip 已不在磁盘，与审计提交 3d220ac 自述 readback MATCH 互洽） |

**归档工件端到端实测（本轮决定性验证）**：`git archive v0.5.3` 干净解包 → `spot_check.py` **ALL CHECKS PASSED**；`pytest tests/ -q` **28 passed, 1 skipped**（跳过项见 N3，为设计内 auto-skip）。验证层首次在投稿归档上完整可运行。

---

## 三、本轮新发现问题（全部 Minor）

- **N1【条件项】version DOI 10.5281/zenodo.22954782 当前 doi.org 返回 "DOI Not Found"**（本机 curl 404 + WebFetch 独立链路复现 "The DOI has not been activated yet"）。记录本身 state done / published（今日 08:15 UTC 创建），系 DataCite 激活滞后——与 v0.5.2 的 22949350 完全同型（该 DOI 当日 404、次日 200）。MS 引用串本身正确。**投稿前必须复核可解析**。
- **N2【条件项】concept DOI 10.5281/zenodo.20405458 当前仍落点 v0.5.2 记录 22949350**（WebFetch 实测落页标题 "v0.5.2 … Version v0.5.2"），尽管 22954782 已 is_last=true——Zenodo latest 重定向传播滞后。**投稿前必须复核已重指向 v0.5.3 记录**。
- **N3【残留】`tests/test_reference_values.py:93-100` 仍断言退役口径**：`test_tcga_nn_tt_medians` docstring "Median NN/TT omega ratios 1.23-2.32"，从 legacy `phase34_v2_summary.csv` 断言 min 1.233 / max 2.319——该数字已非稿件声明（spot_check 已迁移，此测试遗漏）。归档上该测试按设计 skip（1 skipped 的来源），无执行风险；但本地它"守护"的是论文不再报告的数字，而当前 headline mean 在 pytest 层无覆盖（仅 spot_check 覆盖）。建议迁移至 excc 表或显式标注 legacy。

---

## 四、具体修改建议

1. N1/N2：投稿前最后一夜重跑 `curl -sI https://doi.org/10.5281/zenodo.22954782` 与 concept DOI 落点检查；若 48h 后仍 404/未重指向，在 Zenodo 记录页手动触发或联系 Zenodo support（有 22949350 的先例话术）。
2. N3：将 `test_tcga_nn_tt_medians` 改为读 `nc52_tcga_pancancer_excc.csv` 断言 mean 口径（LUAD 2.464 / KIRC 1.880 / LUSC 1.708 / BRCA 1.567 / LIHC 1.112；range 1.11–2.46），与 spot_check Section 1 对齐；或将该测试更名 `test_tcga_nn_tt_medians_legacy` 并在 docstring 注明守护的是退役口径。
3. 无需其他动作：版本面、锁文件、CI 3.10–3.14、种子披露（MS L116 + SI L258 例外清单）、MIT 许可、追踪策略披露均已核验到位。

---

## 五、一句话结论

验证层断裂与归档指针断裂两条 Major 已实质性修复并经干净归档实测通过，版本/DOI/声明三面一致，剩余仅两个 DOI 传播滞后的投稿前确认项与一个退役口径测试残留——**8.5/10，Accept（条件：N1/N2 投稿前复核）**。

---

*R6-repro · nc57 终审 · 全部结论基于当版文本与仓库/远端实况复核*
