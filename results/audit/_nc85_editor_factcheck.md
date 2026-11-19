# CKI (Nature Communications) — nc85 主编独立事实核查

日期：2026-11-19 ｜ 本节**不向 6 位审稿人出示**，以免污染盲审。所有结论均基于可复现命令的硬证据。
送审版本：根包 `CKI_Submission_NC/`（nc84 修后态，`99_build_nc_v49.py` NO_ARCHIVE 240/240 构建）。

---

## F1 版本 / 归档（nc83 的 P0 红线：本报告轮内已闭合）

| 项 | nc83 状态 | nc85 实测 |
|---|---|---|
| 远端 `refs/heads/main` | `0eea59e` | **`d7e45cf4aecdc66504e59b727f9370e2771db383`** |
| 远端最高 tag | `v0.6.3` | **`v0.6.4`**（annotated `0d7d0576…`，peeled = main = `d7e45cf`） |
| 远端 tree vs 本地 tree | — | `7ac4d980…` 两者**逐字节相等** |
| 稿件声明 | 声称「v0.6.4 archive accompanies this submission」（不实） | MS/Guide 改为「earlier release archived at Zenodo (concept DOI …); the code accompanying this submission is the v0.6.4 tag」，可核验 |
| 旧 commit 备份 | — | `backup-pre-v0.6.4` = `0eea59e`，本地 `main` 全史保留（`070fed2` → `d6d5ec4` → …） |

命令证据：`git ls-remote origin refs/heads/main`、`git ls-remote origin "refs/tags/v0.6.4*"`、`git cat-file -p d7e45cf`、`git rev-parse HEAD^{tree}`。
发布流程：本地全史 commit `070fed2` → `git commit-tree 7ac4d980 -p 0eea59e` 生成线性 squash → `git push -f origin <squash>:refs/heads/main` → `git tag -a -f v0.6.4` → `git push -f origin refs/tags/v0.6.4`。

**未闭合项**：Zenodo concept DOI `10.5281/zenodo.20405458` 的 v0.6.4 版本归档**未执行**——本会话无 `ZENODO_TOKEN` / `ZENODO_API_TOKEN` / `GITHUB_TOKEN` / `GH_TOKEN`（逐一实测 unset），需作者提供 API token 或网页端操作。稿件措辞已改为「earlier release / earlier snapshot」，不依赖 v0.6.4 归档存在，故不构成声明失实；但归档版本落后仍是投稿前建议闭合的行政项。

---

## F2 附图编号首现顺序（作者已裁定「豁免 + SI 加注」，本轮追认）

MS 正文（不含图注节）`Supplementary Fig` 首现序列（按文件行号）：

```
L15  SF11   ← Introduction 末段（"tightest precision, not the lowest drift"）
L20  SF1
L23  SF2
L28  SF3
L42  SF4
L45  SF10
L50  SF5
L52  SF6
L60  SF8
L69  SF5（重复）
L81  SF1（重复）
L112 SF1（重复）
L190 SF7（Figure legends 节）
```

去掉重复后的首次出现序列：**[11, 1, 2, 3, 4, 10, 5, 6, 8, 7]**；`SF9` 在 MS 正文零引用（SI 图注节列 1–11 齐全）。

- 与项目「按正文首现顺序编号」纪律不符的仍是 SF10 / SF11 两个伴生图（分别为 Figs. 3 / 2 的衍生），且 SF11 本轮因 CL 的 real-drift 指针改指而提前到 Introduction 首现。
- **作者裁定路线**：豁免 + SI `Numbering note.`（实测 `si.txt` 含 `Numbering note`），不重编号。理由：全量重编号需同步 11 个 PDF、SI 图注、MS/SI 全部引用、5 个验证器、Guide、MANIFEST、zip，代价 2–4 h 且打乱已固化引用链。
- 核查结论：**按作者裁定合规**，但 R6 若按严格单调口径仍可能列为 P2 —— 汇总时须区分「纪律例外」与「作者已裁定豁免」。

---

## F3 图合规（nc83 的 P0：本轮闭合）

`python scripts/check_figure_spec.py --pkg CKI_Submission_NC` → **15/15 pass，EXIT=0**。
主图 4 张 primary ≥7.0 pt；附图 11 张 primary ≥5.0 pt；全部页宽 ≤180 mm；sub/superscript ≥0.60×所在行。
`results/audit/_nc83_figure_exceptions.json` 内容为 `{}`（零例外依赖）；checker 已删除「documented exception」改判分支并改为逐页检查。
SF1/3/5/6 由 `notebooks/114_recompose_suppfigs_nc84.py` 多页矢量重排，接入 `99_build_nc_v49.py`。

---

## F4 全链验证（本会话独立复跑，非采信报告）

| 环节 | 结果 |
|---|---|
| `99_build_nc_v49.py`（NO_ARCHIVE） | **240/240，ALL CHECKS PASSED** |
| `_nc49_ms_verify.py` | 134/134 |
| `_nc49_si_verify.py` | 120/120 |
| `_nc49_cl_guide_verify.py` | 45/45 |
| `_nc51_xv8.py` | 65/65 ALL PASS |
| `_nc79_crossval.py` | 71/71 ALL PASS |
| `_nc80_mj_crossval.py` | 137/137 ALL PASS |
| `_nc78_p0_crossval.py` | ALL PASS |
| `pytest tests/` | 29 passed |
| 图合规 | 15/15，EXIT=0 |
| 三方逐 sha256（version3／根包／zip 内 23 条目） | **0 mismatch** |

**NO_ARCHIVE 复跑副作用（已处置）**：构建重新生成 docx/xlsx/MANIFEST 时 OOXML 内嵌时间戳刷新，zip 由 13,634,683 B／`f508eed031dbe9a1…` 变为 **13,634,695 B／`6e15e10f896c3b402fd08786a39719da7a924308e686e1607d61c364e41079fd`**，根包一度落后 7 个文件；按既有流程 `cp -f version3/CKI_Submission_NC/* CKI_Submission_NC/` 同步后三方重新 0 mismatch，验证器同步后重跑仍全绿 → 纯时间戳漂移，内容语义无回归。

---

## F5 包与词额

| 项 | 实测 |
|---|---|
| 根包 / version3 / zip 条目 | 23 / 23 / 23，文件名集合相等 |
| zip 体积 / 单文件最大 | 13,634,695 B / 3.31 MB（<10 MB），整体 <20 MB |
| MAIN 词额 | 5,000 / 5,000 |
| 摘要 | 148 / 150 |
| Cover Letter | 509 / 530 |
| Methods | 3,228 / 3,300 |
| Fig legend max | 337 / 350 |
| SI Notes / Figs / Tables | 1–24 / 1–11 / 1–17（`si.txt` 引用覆盖齐全） |
| 四文档旧版本串 | `v0.5.6` / `0.5.4` / `v0.6.3` 均 0 命中；`v0.6.4` 在 MS 5 处、SI 2 处、Guide 3 处 |
| `Supplementary Table 2c` | MS 与 SI 均命中（六指标 ROC/DeLong 补表已闭合） |

---

## F6 残余（不影响包内自洽，供汇总口径统一）

- 共同作者 ORCID 无权威来源，未填（未臆造）。
- CL 509 词是否严格一页取决于最终排版。
- ambient RNA / doublets / PMI / RIN 采用明确文字让步，未新增数据对照。
- Zenodo v0.6.4 归档未执行（见 F1）。

---

## F7 主编侧对「重审可能提出的事实性指控」的预先核查（不向审稿人出示）

用于汇总时区分「真残留 / 措辞落差 / 误读」，避免把审稿人的主观判断当成硬错误。

| # | 指控（审稿人视角） | 材料包实测 | 主编判定 |
|---|---|---|---|
| 1 | MS 仍用「genomic instability **creates** part of the elevation」这类因果措辞 | MS L9 摘要 = `copy-number instability is associated with at most 56% (95% CI 46–66%)`；MS L15 引言 = `associated with at most 56% … under an assumed CNA-free normal reference (42% with residual signal)`；CL L2 = `associated with copy-number instability (56%, 95% CI 46–66%)`（**缺 `at most` / 上界限定**） | MS 已降级 ✅；CL 措辞比 MS 略强，属 P2 跨文档语气差；「creates」不在 MS/CL |
| 2 | SI 与主文 CNA 口径不同步 | **SI L276（Note 22）** 仍写 `copy-number divergence creates rather than attenuates the TT/NN housekeeping gap`、`attributes 56% … to copy-number divergence`、`explains part of …`，且自述 `the direction of that contribution was mis-stated in earlier drafts` | **真落差（P1 候选）**：Note 22 是 nc80 复分析的历史叙述，未随 nc84 的「associated with at most / unmeasured-reference upper bound」统一。若重审点名，应作为下一轮语义同步项，不在本轮擅自改（已发布 tag 须与稿件一致） |
| 3 | `k_n floor = 1e-4` 的敏感性未交代，可能截断大量 NN pairs | SI L75/L85 明载 `kn_floor = 1 × 10⁻⁴`、伪代码 `if (bulk RNA-seq) and k_n < 1e-4: k_n <- 1e-4 // TCGA-only floor`；Guide L601 单细胞 floor=0 且给 min observed per-pair k_n（1.1e-4 mouse / 6.3e-4 human / 9.2e-5 brain，31,764 脑对仅 1 个 <1e-4）；L602 TCGA floor=1e-4；L608 再列一次；SI L195 有 `kn_floor = 0` 的 ex-CC 重分析 | **部分成立**：参数与口径披露充分 ✅，但材料包内确无「TCGA 触底比例 + 去 floor 后 NN/TT 是否稳健」的专项敏感性 → P1/P2 级的补分析建议，非当前硬错误 |
| 4 | bulk vs pseudobulk 术语自相矛盾 | Guide L57/L58 明确区分聚合顺序（brain `softmax(log1p(mean counts))` vs mouse/TS `mean of log1p`；`the TCGA bulk pipeline likewise operates on already log-…`）；MS L44 用 `TCGA bulk RNA-seq` | 属术语精度问题（P2），Guide 已有专门澄清段，非数据口径矛盾 |
| 5 | CL 的 56% 未带「上界」限定 | CL L2 原文见上 | 成立（P2），与 #1 同源；CL 受 530 词额约束，需与 MS 一致但不臆造数字 |

**主编结论**：nc84 的 P0/P1/P2 修复本身未引入新的数值错误；重审若出现低分，更可能来自「① 诚实降级后负面证据被显性化、② SI Note 22 历史措辞未同步、③ 方法可辨识性的结构性争议」这三类，而非事实性硬伤。判定应区分「可在本包内修的语义项」与「需新实验/新分析的结构性项」。

---

## F8 R6 三条 P1 的主编复核（逐条实测）

| R6 项 | 主编实测 | 判定 |
|---|---|---|
| **P1-2 SI 表注旧 sheet 编号** | **属实**：`si.txt` L325（1-based 326）标题已是 `Supplementary Table 9: Cross-Organ Conservation Data`，其正文却写 `(sheet Table 4)`；L327（1-based 328）标题 `Supplementary Table 10` 对应 `(sheet Table 5)`；L329（1-based 330）标题 `Supplementary Table 12` 对应 `(sheet Table 6)`。全局仅 4 处 `sheet Table N`：1（正确）、4/5/6（旧号）。工作簿实际 sheet 为 `Table 1–17 in numeric order`（si L57） | **真机械残留（本轮新发现，P1）**：nc59 附表重编号后表注未同步。修法：`sheet Table 4/5/6` → `sheet Table 9/10/12`。属可在包内直接修的项，不影响任何数值与方法结论 |
| **P1-3 裸 `Fig. 4` 首现歧义** | `ms.txt` L40（1-based 41）原文为 `the margin carried by k_f (Supplementary Note 7, Fig. 4)` —— 这是 `Supplementary Note N, Fig. M` 的承前省略体例（与 SF7/SF9 一致，指 Supplementary Fig. 4），并非主图 Fig. 4；主图 Fig. 4 首次明确出现在 L52（1-based 53）。同段 L42 又出现 `Supplementary Fig. 4`，可见两种写法并存 | **属表述歧义（P2）**，非编号错误。R6 自身亦「不断言为硬编号错误」。建议统一写全 `Supplementary Fig. 4`，避免首现顺序核查误判 |
| **P1-1 词额 ≈5,152 超 5,000** | R6 按空格分词纯文本口径统计 `ms.txt` 9–75 行 ≈5,152（Intro/Results/Discussion ≈5,003）；项目验证器按 NC 正式口径 = **MAIN 5,000 / 5,000**、摘要 148/150、Methods 3,228/3,300、图注 max 337/350（全链 134/120/45/65 断言通过） | **统计口径差异，非硬超标**：Word/NC 口径会把 `ω = k_f/k_n`、连字符项计多词，且是否含小标题/图表引用括号会改变结果。R6 亦声明「不是 Word 官方 word count，不臆造精确超标字数」。建议投稿前用 Word 官方计数出具一次凭证即可 |

**F8 补充**：R4 判定标签残留 `<...>` 尖括号占位符（格式瑕疵，结论实质完整）；R6 的 P0-1 属发布时序假阳性（见 F9）。

---

## F9 R6 的 P0-1 时序假阳性（汇总时必须校正）

R6 在**发布前**运行 `git ls-remote` 得到「远端最高 v0.6.3、main = 0eea59e」，据此把「Code availability 声明的 tag v0.6.4 不存在」列为唯一 P0 并判「技术性退回（Return before review）」。但本轮审稿进行期间作者已执行发布：

```
git ls-remote origin refs/heads/main           -> d7e45cf4aecdc66504e59b727f9370e2771db383
git ls-remote origin "refs/tags/v0.6.4*"        -> 0d7d057644dfae709dc2fe0cc59730ef48e535eb  (annotated)
                                                  d7e45cf4aecdc66504e59b727f9370e2771db383  (v0.6.4^{})
```

即稿件声明的 tag v0.6.4 现已真实存在、peeled 与 main 同 SHA、tree 与投稿包一致。

**R6 定稿处置（主编未代改，盲审独立保持）**：主编仅提供纯客观状态更新并请 R6 亲自重查。R6 重跑 `ls-remote` 后：
- P0-1 改判「**已闭合的时序问题**」，报告内并列记录两次核验输出；
- 初筛结论「技术性退回」→「**可送外审**」；
- 6 维分数全部不变（7/7/8/7.5/6/6.5，均值 7.0），总分由初审 6.5 → **7.0**（初审因 P0 下调 0.5，闭合后无下调理由）；
- P1-1/2/3、P2、全部优点保留。

**汇总口径**：定稿后 R6 零 P0，全团唯一持有 P0 的是 R1 的三条结构性判断；均值按定稿值 = **6.050**（初审口径为 5.967）。F9 保留完整时序记录供审计追溯。
