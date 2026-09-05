# v46 终审签署（Editorial 视角）

- **任务**: 核销 v45 交叉验证报告（`gb_v45_crosscheck_editorial_2026-09-05.md`，8.5/10）遗留的 4 项可修复 P2
- **评审对象**: `version3/CKI_Submission_v46/`（build 621/621，Release v0.4.9，Zenodo 10.5281/zenodo.22333850）
- **日期**: 2026-09-05（只读核查）

---

## 终审结论

**总分：9.0 / 10**（v44：7.5 → v45：8.5 → v46：9.0）
**判定：Accept（编辑合规与期刊适配维度）。**

v45 遗留的 6 个 P2 中 4 个可修复项全部 CLOSED；2 个为设计性保留 OPEN（第一作者 ORCID 等用户输入；S11 刷新为建议项）。三轮评审（v44 盲审 → v45 核销 → v46 终审）未发现任何回退。

## 逐项核销

| # | 条目 | 判定 | 证据 |
|---|---|---|---|
| 1 | MANIFEST Contents 注释陈旧（N-3） | **CLOSED** | 第 462–467 行："(SN 3.12, 3.13, **3.20-3.23**)"、"Cover letter (**four-dataset validation summary**)"、"Reproducibility guide (**notebooks 05-101, incl. v45 analyses 88-91b**)"——v41 时代旧注释（"scripts 44-46"、"validation point 6"）已全部替换 |
| 2 | 打包声明与实物矛盾（P2-3） | **CLOSED** | 第 471–476 行：GA png/svg 与 `*_fulltext.txt` 现明确描述为"included for convenience as **review aids** … not part of the journal submission"，声明与包内实物一致（34 文件随 zip 发布），矛盾消除 |
| 3 | 指南缺 v45 专节（N-2） | **CLOSED** | 新增 "**5.9 v45 Analyses**"（第 326 行起），六个条目齐全：notebooks/88_ratio_estimator、89_cluster_boot、90_nonhk_drift、91_augur、91b_augur_ovr、_fig1_clean，各附 Script 路径——指南"reproducing all analyses"使命恢复完整 |
| 4 | N1 幅度表述（N-1） | **CLOSED** | 摘要（第 10 行）与 Results（第 39 行）均已改为 "raw JS and cosine **at moderate-to-strong drift**: 0.81–1.00 / inflated to 0.81–1.00 **at moderate-to-strong drift**"，与 SN Note 3.22 全幅度数据（η=0.25 时 raw JS 0.067、cosine 0.089）不再冲突 |

## 设计性保留 OPEN（不阻塞）

- **第一作者 ORCID**：标题页仍仅通讯作者 ORCID（第 7 行）。等待用户提供 Xianming Wu ORCID；GB 仅强制通讯作者，提交系统补齐即可。
- **S11 刷新（建议项）**：Supplementary_Figure_S11.pdf 维持 771 KB。非缺陷，建议作者择机确认未意外栅格化。

## 版本一致性终检

- MS Availability（第 146 行）：v0.4.9 + tag v0.4.9 + **version DOI 10.5281/zenodo.22333850** + concept DOI，四要素齐全。
- SN（第 59、93 行）、指南自检清单（"Install CKI v0.4.9"）、封面信（"release tag v0.4.9"）全部同步 v0.4.9；全包无 v0.4.8 残留（除 MANIFEST 历史段）。
- 摘要 250 词、Results 6,476 词（MANIFEST 记录；与 v45 口径一致）维持达标。
- 封面信仍仅引 concept DOI（v45 已记录的轻微建议，不阻塞；MS 声明为权威出处）。

## 三轮轨迹

| 轮次 | 分数 | P0 | P1 | 主要动作 |
|---|---|---|---|---|
| v44 盲审 | 7.5 | 0 | 2（Zenodo DOI、篇幅） | Minor Revision |
| v45 核销 | 8.5 | 0 | 2/2 CLOSED | +3 新 P2 |
| v46 终审 | **9.0** | 0 | — | 4/4 残留 CLOSED，**Accept** |

**签署意见**：从 Genome Biology 期刊适配与编辑合规维度，v46 投稿包结构完整、声明一致、可用性合规、文字质量达标，建议接收。剩余两项 OPEN 均不改变此结论。
