# NC 投稿包 nc68 盲审报告 — Reviewer 4（计算可复现性与数据/代码规范）

审查日期：2026-10-11。审查对象：`CKI_Submission_NC/`（34 条目）与代码库根目录。所有结论附文件/命令证据。

## 总体评价

数据与代码可用性声明完整、可验证：GitHub 仓库公开可达，Zenodo DOI 实际解析，CELLxGENE collection ID 经 API 核实为 Siletti 脑图谱。数字可追溯性在抽查的 5 组关键数字中表现优异——5,151 pairs、基线 7.70（CI [6.38, 9.82]）、数学下界 0.524、Note 20 诊断（2,937 pairs）均能找到生成脚本且产物逐行对得上。主要问题是**引用的归档版本（tag v0.5.5 / Zenodo 23104178）落后于实际投稿内容 32 个提交**，SI Note 20 的核心脚本不在被引归档中，且部分 SI 关键统计量以硬编码字符串存在于文档生成脚本中。

## Major concerns

**M1. 被引代码归档与投稿内容版本脱节（合规性，必须修复）**
- 主文 Code availability 声称 "All analysis notebooks ... are available in the same GitHub repository (tag v0.5.5) and are included in the Zenodo archive (version DOI 10.5281/zenodo.23104178)"。
- 证据：`git describe --tags` = `v0.5.5-32-g73666e6`（投稿包为 nc68，HEAD 领先 v0.5.5 共 32 个提交，HEAD 提交信息即 "nc68: scoped theoretical framework for omega (SI Note 20, Supp Fig 19...)"）。
- `git ls-tree v0.5.5 --name-only notebooks/ | grep 85_theory` 无结果——SI Note 20 明确引用的 `notebooks/85_theory_diagnostics.py` **不在被引 tag 中**。
- Zenodo v0.5.5 记录（已联网核实，2026-10-02 发布）附件为 `CKI_Submission_v50_NC.zip`，发布说明描述补充图为 1–14 重编号方案；本次送审包为 v49/nc68，含 Supplementary_Fig_1–19 与 Note 20。**审稿人按声明 DOI 下载的归档无法复现送审 SI 的最新内容。**
- 修复：投稿/接收前切新 tag（如 v0.5.6）触发 Zenodo 新 version DOI，并在 Code availability 中更新。

**M2. 部分 SI 关键统计量硬编码于文档生成脚本，无独立生成链**
- 例：SI 中 "brain CV 1.21 → 0.148（ω studentization 后 null 离散度）" 是 Note 20/Fig. 19d 的核心论据，但该数字以字符串字面量硬编码在 `notebooks/68_gen_supplementary_nc.py`（"coefficient of variation ... falls from 1.21 (k_f) to 0.148 (ω)"），全库 grep 未找到计算该量的独立脚本与中间产物（`results/` 下无对应 per-class null median CV 文件；`perclass_calibration.csv` 等内容不对应）。
- 对比：同为关键数字的基线 7.70 有完整链（`scripts/nc52_stats_resampling.py` → `results/nc52_stats_baseline_twostage_bootstrap.json`），说明作者具备规范能力，此处属于遗漏。
- 风险：硬编码数字无法被第三方重算验证，也无法被 `tests/test_reference_values.py` 防回归覆盖。

## Minor concerns

1. **图件字号低于规范**：抽查 4 个 PDF（PyMuPDF）：`figure1.pdf` 最小字号 4.0 pt，`figure2.pdf` 与 `Supplementary_Fig_19.pdf` 4.9 pt，`Supplementary_Fig_1.pdf` 6.5 pt——多处低于 NC 要求的 5–7 pt 下限。尺寸方面 figure1 为 170 mm、figure2 为 178×203 mm（宽度合规）；`Supplementary_Fig_1.pdf` 宽 353 mm（SI 可放宽但建议说明）。矢量性良好（figure1/SF19 纯矢量；figure2 含 2 个栅格面板）。
2. **SI 目录编号不一致**：SI 全文第 60 行目录写 "legends for Supplementary Figs. 1-18"，实际图例为 1–19（第 316 行正文写 "1-19"，包内亦有 Supplementary_Fig_19.pdf）。
3. **MANIFEST 版本标签陈旧**：`CKI_Submission_NC/MANIFEST.txt` 抬头为 "Submission Package v49"，而仓库 `run_all.py` 与 Zenodo 附件均为 v50 口径（zip 与目录 34/34 条目一致、MANIFEST 内全部字节数核对无误，仅标签陈旧）。
4. **CI 配置在当前 HEAD 被删除**：`.github/workflows/ci.yml` 存在于 v0.5.5，在 nc68 清理提交中被移除（`git ls-tree HEAD .github/` 为空）。主文 "continuous integration covers Linux" 仅对被引旧 tag 成立；建议在 main 上恢复。
5. **CELLxGENE 数据集未锁定版本**：脑图谱仅引 collection ID（API 核实存在 `collection_version_id: bf0ef473-...`）。CELLxGENE 集合可原位更新，建议在 Data availability 加记 version ID 或下载日期快照（已有 accessed July 2025，可接受）。
6. **notebooks/ 目录信噪比低**：约 200 个脚本含大量 `_tmp`、`_fix`、重复版本（如 6 个 08c、5 个 99_rebuild、3 个 105_md_to_docx）。虽有 SI Data 1 脚本索引与 README 逐条来源指引缓解，仍建议归档目录分层（如 `notebooks/archive/`）。

## 抽查验证通过项（正面证据）

| 主文/SI 数字 | 证据 | 结果 |
|---|---|---|
| 5,151 human full-inventory pairs | `results/phase33_v3_human_pairs.csv` 实数 5,151 行 | ✓ |
| 4,851 analyzed pairs | `results/phase35_all_metrics_pairs.csv` 实数 4,851 行 | ✓ |
| 基线 ω=7.70，两阶段 CI [6.38, 9.82]，LOPO 6.75–8.08 | `results/nc52_stats_baseline_twostage_bootstrap.json`（observed_mean 7.6958，CI [6.3798, 9.8184]，lopo 6.7479–8.0813），生成脚本 `scripts/nc52_stats_resampling.py` | ✓ |
| 数学下界 0.524 [0.506, 0.541] vs 观测 0.089 | `results/nc52_stats_omega_kf_math_floor.csv`（0.5241 [0.5058, 0.5412] / 0.0895，B=1000, seed 42） | ✓ |
| Note 20 诊断 2,937 pairs（1,500+900+37+500） | `results/theory_diagnostics.csv` 按 part/panel 精确分解（1500/900/37/500 每 panel），脚本 `notebooks/85_theory_diagnostics.py:639` 写出 | ✓ |
| k_f-only FPR 0.81–1.00（中性漂移） | `results/nonhk_drift_v45.json` + `notebooks/90_nonhk_drift_v45.py` | ✓ |
| Supp Tables 1–23 | xlsx 实有 23 个 sheet 且按序命名 | ✓ |
| zip 与目录一致性 | python zipfile 核对 34/34，双向无差集 | ✓ |
| MANIFEST 字节数 | 全部 34 条目 size 逐一核对无误 | ✓ |
| GitHub 仓库 | HTTP 200 + API 元数据（public, zhanglknt/CKI-cell-type-identification） | ✓ |
| Zenodo DOI 10.5281/zenodo.23104178 | 解析到 v0.5.5 记录（见 M1 版本问题） | ✓(有保留) |
| CELLxGENE collection 283d65eb-... | curation API 返回 Siletti/BRAIN Initiative 集合 | ✓ |
| 依赖与环境 | `requirements.txt`（宽松）+ `requirements-lock.txt`（pip freeze，Python 3.14.4）+ `Dockerfile`（python:3.14-slim，lock 安装）+ `ENV_SETUP.md` | ✓ |
| 入口与测试 | `run_all.py`（分阶段管线，--dry-run/--verify-only）；`tests/`（smoke + 对 manuscript 权威结果文件的防回归断言） | ✓ |

## 评分（1–10）

- 新颖性：7（Ka/Ks 类比的操作化有新意，但本质是 JS 散度比值 + 经验校准）
- 严谨性：8（置换/块打乱 null、bootstrap CI、诚实的局限性陈述；硬编码数字扣一分）
- 广泛兴趣：6（单细胞图谱社区与方法学读者；TCGA 部分为描述性）
- 可复现性：8（声明完整、抽查全部对上、入口清晰；归档版本脱节与图件字号扣分）

## NC 中稿概率估计：60%

方法学扎实、可复现性基础设施（lock + Docker + 防回归测试 + 脚本索引）高于 NC 平均水平，但期刊竞争激烈且方法的"广泛兴趣"论证偏防御性；若 M1 归档版本问题修复、评审轮次顺利，概率可升至 70%。

## 必须修复项（≤5）

1. 切新 tag（v0.5.6+）并更新 Code availability 的 Zenodo version DOI，使归档包含 nc68 全部内容（尤其 `notebooks/85_theory_diagnostics.py`）。
2. 为 SI 硬编码统计量（至少 CV 1.21→0.148 及其 max/min ratio）补齐独立生成脚本与 `results/` 产物，纳入防回归测试。
3. 将全部图件最小字号提升至 ≥5 pt（当前 figure1 4.0 pt、figure2/SF19 4.9 pt）。
4. 修正 SI 目录 "Figs. 1-18" → "1-19"；同步 MANIFEST 版本标签与实际包版本。
5. 在 main 分支恢复 `.github/workflows/ci.yml`（或修改主文 CI 表述）。
