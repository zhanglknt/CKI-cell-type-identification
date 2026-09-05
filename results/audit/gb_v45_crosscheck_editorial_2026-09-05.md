# v45 交叉验证核销报告（Editorial 视角）

- **任务性质**: 对照本人 v44 盲审报告（`gb_v44_blind_review_editorial_2026-09-05.md`，7.5/10，Minor Revision）逐项核销 v45 投稿包
- **评审对象**: `version3/CKI_Submission_v45/`（GitHub Release v0.4.8，Zenodo version DOI 10.5281/zenodo.22310724）
- **评审日期**: 2026-09-05
- **方法**: 只读核查。正文/封面信/补充材料/指南/MANIFEST 全文提取件逐条 Grep + 精读；字数用脚本独立统计；图表引用编号用脚本穷举核对。PDF 无法在本环境渲染，图形内容核查限于校验和、图注与仓库脚本。

---

## 总体判定

**总分：8.5 / 10**（v44：7.5）
**结论：两项 P1 全部 CLOSED，四个 P2 中两个 CLOSED、一个 PARTIAL、一个 OPEN；另发现 3 个新 P2 级小问题。v45 达到接收的编辑合规线，剩余事项均为机械性收尾。**

---

## 一、v44 P1/P2 逐项核销

### P1-1 Zenodo 版本 DOI 合规 — **CLOSED**
- MS Availability（第 146 行）："The CKI source code (**v0.4.8**) … tag v0.4.8 … (concept DOI: 10.5281/zenodo.20405458; **version DOI for v0.4.8: 10.5281/zenodo.22310724**)"。接收前置条件已消除。
- 陈旧 v0.4.7 全包扫描：仅存在于 MANIFEST 历史变更记录（合理）；MS、封面信、指南、SN 均无 v0.4.7。指南 1.2 节与自检清单均为 0.4.8；封面信第 6 段已更新为 v0.4.8。
- 残余建议（不阻塞）：封面信只引 concept DOI，可与 MS 对齐补上 version DOI。

### P1-2 正文超长/密度 — **CLOSED**
- 独立统计：Results = **6,469 词**（v44：9,022；build 记 6,457，差异为统计口径），处于约定 5,900–6,600 区间；正文主体 21,470 → **19,273 词**。摘要恰为 **250 词**（含 3 个小节标签）。
- 关键披露存活核查：**ddof = 1 声明在 Bergmann 段首句保留**（第 61 行 "all class-level SDs in this paragraph computed with ddof = 1"）；校准双基线（7.70 / 9.73 脑内 / 7.67 Tabula Sapiens）叙述保留且分层清晰。
- 迁移内容指针核查：压缩后 Results 各段均带 "Additional file 1: Note …" 指针；新增 v45 分析对应 SN **Note 3.20–3.23 四个新注节齐全**（SN 第 135–146 行，各附 notebook 88/89/90/91/91b 脚本与 results 报告路径）。正文对 Additional file 1 的交叉引用共 57 处；脚本穷举核对：正文引用了全部 Fig. S1–S14、Table S1–S4、Fig. 1–6，**无孤儿图、无断链**；无 "as noted above" 类悬空回指。
- "Four analyses" 框架（第 63–64 行 First/Second/Third/Fourth）与 v44 错标修复一致。

### P2-1 第一作者 ORCID — **OPEN**
- 标题页第 7 行仍仅 "ORCID: Li Zhang 0000-0002-0698-0754"。全包仅此一个 ORCID。GB 仅强制通讯作者 ORCID，故不阻塞；建议提交系统补 Xianming Wu ORCID。

### P2-2 重复/错标文字 — **CLOSED**
- "legacy six-split estimate 6.67" 由三处近乎逐字重复减为两处简短括注（Results 第 28 行、Discussion 第 80 行），措辞已差异化，属合理的跨节回指。
- "Two analyses … Third/Fourth" 错标已修为 "Four analyses"。
- 摘要 250 词达标。

### P2-3 Additional files 声明与打包一致性 — **PARTIAL**
- 已修：MS Additional files 声明改为 "Format: DOCX"，删除"附 PDF 渲染件"括注（全包无 "PDF rendering" 残留）。
- 未修：v45 目录仍含 5 个 `*_fulltext.txt` 提取件及 `CKI_graphical_abstract.png/.svg`，而 MANIFEST 第 448–452 行仍声称 png/svg "remain in results/figures_final/"、提取件 "excluded from this package"。声明与实物仍矛盾；若该目录即 zip 内容物，打包脚本未执行排除。
- 另发现 MANIFEST Contents 注释陈旧：第 442–444 行仍写 "(SN 3.12, 3.13)"、"(validation point 6)"、"(scripts 44-46)"——SN 已至 3.23、脚本已至 91b（见新发现 N-2）。

### P2-4 图表质检（S11 体积/字体嵌入）— **OPEN**
- Supplementary_Figure_S11.pdf 与 v44 完全相同（sha256 716d75b3…，770,996 bytes），未做任何处理。本环境仍无法渲染 PDF 目检字体嵌入。维持"请作者确认 S11 未意外栅格化"的建议；非阻塞。

---

## 二、team-lead 指定核查项

| 核查项 | 结果 |
|---|---|
| (a) Results 压缩至 ~6,100 词且披露不丢失 | ✅ 6,469（约定区间内）；ddof=1 存活；迁移内容均有 SN 指针 |
| (b) 摘要 250 词 | ✅ 恰 250 词（独立统计） |
| (c) v0.4.8 + Zenodo 22310724 一致、无 v0.4.7 残留 | ✅ MS/CL/指南/SN 全部 v0.4.8；v0.4.7 仅在 MANIFEST 历史段 |
| (d) 参考文献 56 条 | ✅ 编号 1–56 连续；新增 [56] Skinnider et al. (Augur)，正文第 84 行 [56] 引用一致 |
| (e) "Four analyses" 框架 | ✅ 第 63 行，与 First–Fourth 对应 |
| (f) Fig 1C 重绘（_fig1_clean.py，median 7.69） | ✅ figure1.pdf 校验和与大小均变（76,557→78,224 bytes）；`notebooks/_fig1_clean.py` 在仓库存在；MANIFEST 记录 Median 7.69 / Baseline 7.70；图 1C 图注表述与新基线一致（无法渲染目检） |

## 三、内部一致性数字抽查

| 数字 | MS | SN | MANIFEST | 判定 |
|---|---|---|---|---|
| Augur OvR ρ = 0.442 / 0.564（vs ω / k_f） | 第 84 行 ✓ | Note 3.23 第 146 行 ✓ | 第 20/45 行 ✓ | 一致 |
| Bergmann [5.76, 28.59]（studentized-t） | 第 30、61 行 ✓ | Note 3.21 第 140 行 ✓ | 第 39 行 ✓ | 一致 |
| equal-n 1.74 [1.64, 1.84] | 摘要、第 61、64 行 ✓ | — | 第 7–8 行 ✓ | 一致 |
| 反富集 148.3 vs 39，P(null ≥ 39) = 1.0 | 第 68、70 行（候选节开头前置）✓ | 第 78、166 行 ✓ | 第 10 行 ✓ | 一致 |
| 梯度 studentized-t [4.43, 7.69] | 第 30、61、86 行 ✓ | Note 3.21 ✓ | 第 16、39 行 ✓ | 一致 |
| N1：ω FPR ≤ 0.067 vs raw JS/cosine | 摘要、第 39 行 | Note 3.22 第 143 行 | 第 18–19 行 | **见 N-1，幅度条件表述有缺口** |

## 四、新发现问题（v45 引入/遗留，均 P2）

- **N-1（表述准确性）**: 摘要与 MS 第 39 行写 "raw JS and cosine: 0.81–1.00 / inflated to 0.81–1.00"，但 SN Note 3.22 的 N1 全数据显示 raw JS 在 η = 0.25 时 FPR = 0.067、cosine = 0.089——0.81–1.00 只是 η = 0.5/1.0 的幅度段。现写法遗漏了弱漂移下标准指标同样不虚报的条件，有轻微选择性呈现之嫌。建议改为 "inflating to 0.81–1.00 at moderate-to-strong drift"。
- **N-2（Additional file 2 完整性）**: Reproducibility Guide 有 5.7（v41）与 5.8（v44）盲审分析专节，但**没有 v45 专节**：notebook 88（比值偏差）、89（studentized-t）、90（N1/N2）、91/91b（Augur）、_fig1_clean（Fig 1C）均未入指南。指南自述使命是"reproducing all analyses"，目前这五项只能经 SN 注节间接定位脚本。建议补 5.9 节（格式可照搬 5.8）。
- **N-3（MANIFEST 陈旧）**: Contents 区注释停留在 v41 时代（"SN 3.12, 3.13"、"scripts 44-46"、"validation point 6"），且第 8/9 条的排除声明与包内实物（png/svg/txt 提取件在场）矛盾。不影响正文，但 MANIFEST 是投稿工程门面，建议同步。

## 五、汇总表

| 条目 | 级别 | 判定 | 证据要点 |
|---|---|---|---|
| P1-1 Zenodo 版本 DOI | P1 | **CLOSED** | MS 引 v0.4.8 + 10.5281/zenodo.22310724；全包无陈旧 v0.4.7 |
| P1-2 篇幅压缩 | P1 | **CLOSED** | Results 9,022→6,469 词；ddof=1 存活；SN 3.20–3.23 承接 |
| P2-1 第一作者 ORCID | P2 | **OPEN** | 标题页仍单 ORCID |
| P2-2 重复/错标 | P2 | **CLOSED** | 6.67 句减为两处异化括注；Four analyses；摘要 250 |
| P2-3 声明/打包一致 | P2 | **PARTIAL** | PDF 括注已删；txt/png/svg 仍在包内与 MANIFEST 矛盾 |
| P2-4 S11 质检 | P2 | **OPEN** | 文件与 v44 逐字节相同，未处理 |
| N-1 N1 幅度表述 | P2 | 新增 | 0.81–1.00 仅为 η≥0.5 段，建议加幅度限定 |
| N-2 指南缺 v45 节 | P2 | 新增 | 5.8 止于 v44；notebook 88–91b/_fig1_clean 无指南条目 |
| N-3 MANIFEST 注释陈旧 | P2 | 新增 | Contents 注释与排除声明未同步 |

**核销结论：P1 2/2 CLOSED；P2 2 CLOSED / 1 PARTIAL / 1 OPEN；新增 3 个 P2。无 P0，无影响科学结论的回退。**

## 六、给 team-lead 的处置建议

剩余 6 个 P2 均可在一个打包回合内机械修复：补第一作者 ORCID、指南加 5.9 节、MANIFEST Contents 同步 + 打包排除提取件/png/svg、N1 表述加幅度限定、S11 体积确认（可选）。完成即可达 Accept 状态。本轮评分 **8.5/10**。
