# R6 独立盲审报告（期刊编辑 / 可复现性与技术初筛）

**总分：7.0 / 10**
**建议：Major Revision**
**初筛结论：可送外审**
**判定标签：Code availability 声明的 GitHub tag v0.6.4 经「重查于发布后」确认真实存在（peeled commit = main 头），初审所列 P0 已闭合为时序问题，现无阻断送审项；剩余为词额、SI 旧 sheet 编号、图号前缀等非阻断修订项。**

> 审稿材料仅限 `_nc85_review_materials/` 下 ms.txt、si.txt、cl.txt、guide.txt、tables_overview.txt、manifest.txt、round.txt；另按授权只读 `CKI_Submission_NC/MANIFEST.txt`，并运行 `git ls-remote --tags origin` 与 `git ls-remote origin refs/heads/main` 核对远端状态。未读取任何其它轮次报告/专家汇总/事实核查/修复报告/他人审稿意见，未联网检索作者身份，未读取记忆文件。本报告为编辑初筛视角，学术新颖性与理论深度以方法学/统计/领域审稿人意见为准。
>
> **远端状态的时序说明（如实注明）**：本报告对远端状态共核验两次。第一次在本轮审稿启动时，第二次为**重查于发布后**（定稿前按编辑协调要求重新执行，且仅以本人实际查到的最终远端状态为准，不采信任何转述数值）。两次结果不同，导致初审所列 P0 阻断项在定稿时已闭合，详见 §3 P0-1 的时序记录。除远端状态外，全部材料判读与学术结论均未改变。

---

## 1. 评分表（6 维，1–10，可 0.5）

| 维度 | 分数 | 理由（基于材料包） |
|---|---|---|
| 新颖性 | 7.0 | 将 Ka/Ks 启发式迁移为 ω = k_f/k_n 的比值分解、并给出 scoped framework（SI Note 20）有新意；但作者自承「heuristic index, not a formal selection measure」（ms.txt:64, 67），核心产出是「denominator-driven caution」与 hypothesis-generating catalogue 而非新方法性能领先，novelty 中上而非突破。 |
| 理论严谨 | 7.0 | SI Note 20 给出 Lemma 1/2、Proposition 3–5，理论边界披露充分且诚实（「approximate at the k_f scale」、「guaranteed only for ω > 2α, failed by 30.3% of pairs」ms.txt:24, 61；残余比值偏倚 −8.3%~+6.5%）；扣分于理论为限定性近似、α 跨人群变化 1.65–2.2 倍为主误差项。 |
| 统计严谨 | 8.0 | 置换检验（B=1,000）、region/donor cluster bootstrap、DeLong、BH FDR、Monte-Carlo 可分辨 P 讨论、wild-cluster bootstrap、Cox/zph 补救齐备；主动标注 anti-conservative null、pseudo-replication、per-pair FDR 不可达（ms.txt:74, 112–114）。扣分于 TCGA fixed-panel null 反保守、两检验家族未联合校正（均已披露）。 |
| 证据充分 | 7.5 | 4 个数据集（Tabula Muris / Tabula Sapiens / TCGA 五癌种 / Siletti 脑图谱）+ 双背景 ground-truth 模拟 + 固定面板消融 + 多锚点敏感性 + GTEx 外部参照，覆盖广；但主结论多为 descriptive / group-level / hypothesis-generating，39 个候选中无一通过全局 FDR，KRAS 关联为组间对比，正向发现偏弱。 |
| 表达清晰 | 6.0 | 结构完整（有 SI Roadmap、Numbering note、Reproducibility Checklist），但主文极端压缩（单段 >400 词，ms.txt:47）、正文逼近/略超词额上限、SI 表注残留旧 sheet 编号、主图/附图引用前缀省略歧义、内部轮次标签（v49–v52、ncXX）泄漏到面向读者文档且未统一解释。 |
| 影响力与 NC 适配度 | 6.5 | 对 HK-anchored normalization 的方法学警示有实用价值，跨癌种与全脑图谱覆盖面适配 NC methods scope；初筛技术项已闭合不影响送审，但卖点自限为「precision-first, not lowest drift」「not a pan-cancer prognostic marker」「hypothesis list, not a discovery set」，正向发现偏弱，限制其 NC 适配上限。 |

**综合说明**：6 维均值恰为 7.0。初审时因存在 1 项阻断送审的 P0 而暂下调至 6.5；定稿前重查（发布后）确认 P0 已闭合，不再有下调理由，故回调至 **7.0**，与 6 维均值一致。此回调仅反映技术初筛状态的时序变化，不涉及任何学术内容的重新评价。

---

## 2. 总体评价（3–5 句）

本稿把 Ka/Ks 启发的比值指数系统铺到模拟、校准、跨器官、泛癌与脑图谱五个层面，统计口径与局限披露异常透明（主动标注 anti-conservative、permutation resolution、hypothesis-generating），可复现材料（verified environment、逐节脚本/输出、spot_check、29 项 pytest、Reproducibility Checklist、Numbering note）在同类投稿中属上乘，编号体系（主图 1–4 / 附图 1–11 / 附表 1–17 / Notes 1–24）闭环且无悬空引用。初审时最重的技术初筛问题是全文一致声称随稿代码为 `tag v0.6.4` 而当时远端最高仅 v0.6.3；定稿前按编辑协调要求重查于发布后，已亲眼确认 `refs/tags/v0.6.4` 真实存在、其 peeled commit 与 main 头一致，故该阻断项闭合、Code availability 现可核验，**初筛结论改为可送外审**。尚存的非阻断问题为主文正文逼近/略超 5000 词上限、SI 表注残留旧 sheet 编号（Table 4/5/6）、主图/附图引用前缀省略歧义，均可在修订中处理。需要明确肯定的是：Zenodo 措辞诚实（标明为 earlier release，未声称 v0.6.4 archive 随稿，无「always resolves to latest」漂移表述）、scDist 的 R 包替代声明三处一致、2a/2b/2c 子表引用语义同步，这些均为合规项。

---

## 3. 技术初筛清单

### P0（初审列为阻断送审；重查于发布后已闭合，定稿时不再阻断）

**P0-1　Code availability 声明的 GitHub tag v0.6.4 曾不存在，现经重查确认已发布——已闭合的时序问题。**

- **第一次核验（本轮审稿启动时，发布前）**：
  - `git remote -v` → `origin git@github.com:zhanglknt/CKI-cell-type-identification.git`（与稿件声明的 `https://github.com/zhanglknt/CKI-cell-type-identification` 为同一仓库，核对有效）。
  - `git ls-remote --tags origin` → `v0.6.0`、`v0.6.1`、`v0.6.2`、`v0.6.3`、`v0.6.3^{}`；**当时无 `v0.6.4`**。
  - `git ls-remote origin refs/heads/main` → `0eea59efa655a68be936cf5812ba8e926dda4646`（= `v0.6.3^{}` 解引用对象），即 main 当时停留在 v0.6.3。
  - 据此，初审判定为阻断送审项：声明的 tag 不存在，随稿代码不可核验。
- **第二次核验（重查于发布后，定稿前，本人重新执行，以此为准）**：
  - `git ls-remote --tags origin` → 新增 `0d7d057644dfae709dc2fe0cc59730ef48e535eb  refs/tags/v0.6.4`（annotated tag）与 `d7e45cf4aecdc66504e59b727f9370e2771db383  refs/tags/v0.6.4^{}`（peeled）；v0.6.0–v0.6.3 仍在。
  - `git ls-remote origin refs/heads/main` → `d7e45cf4aecdc66504e59b727f9370e2771db383`，与 `v0.6.4^{}` **指向同一 commit**。
  - 结论：`v0.6.4` tag 现真实存在，且打在当前 main 头上；稿件 Code availability 声明的版本串（0.6.4）与远端实际可用版本一致，初审所指「指向不存在的 tag」已消解。
- **材料包内位置与原文引文（声明内容未变，仅可核验性变化）**：
  - `ms.txt:120`「The CKI source code (v0.6.4) is publicly available at https://github.com/zhanglknt/CKI-cell-type-identification (tag v0.6.4) under the MIT License; **this tag contains every analysis script cited in the Methods and Supplementary Information**.」「**the code accompanying this submission is the v0.6.4 tag**」「All analysis notebooks and processed data matrices are available in the same GitHub repository (**tag v0.6.4**)」。
  - `guide.txt:24`「Version: 0.6.4 (editable install from project root)」；`guide.txt:26`「**the code accompanying this submission is GitHub tag v0.6.4**」；`guide.txt:557`「[✓] Install CKI v0.6.4: pip install -e .」。
  - `si.txt:289`「provided exactly as func_method = "pairwise_absdiff" in **package version 0.6.4**」；`si.txt:332` 安装路径「pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git」不带 tag——初审时该路径将拉取 main 的 v0.6.3 内容而与声明不符；发布后 main 已推进至 `d7e45cf`（= v0.6.4 peeled），裸 clone 亦对应随稿版本，此项连带闭合。
  - `manifest.txt:4` 与 `CKI_Submission_NC/MANIFEST.txt:4`「tag: v0.6.4」；`round.txt:1`「post-fix blind re-review of the v0.6.4 submission package」。文档内部版本串自始至终统一为 0.6.4，无跨文档不同步。
- **诚实边界（不臆造）**：`git ls-remote` 只能验证 tag 的**存在性与指向**（已验证），无法验证「该 tag 内含全部 Methods/SI 引用脚本」这一**内容级**断言——后者需 clone 后逐文件比对脚本清单，超出本轮授权的工具范围，本报告不予证实亦不予否证，留交编辑部复现环节或外审核对。因此本项由「阻断」降级为「已闭合的时序问题」，而非宣称所有可复现性细节均已逐项核验通过。
- **修法（现仅需收尾确认，不再阻断）**：① 编辑部归档本次核验的 commit SHA（`0d7d057` / `d7e45cf`）作为送审版本凭据；② 建议将 Code availability 的版本化存档由裸 concept DOI 补为指向 v0.6.4 的 **version DOI** 或在声明中附 commit SHA，使「this tag contains every analysis script」可被外部静态锁定（与 P2-1 联动）；③ 送审版本中保留 tag 引用即可，无需改全文版本串。

### P1（送审前应修正，非阻断；均仍成立）

**P1-1　主文正文逼近/略超 NC「MAIN ≤5000 词」上限，需按正式口径复核。**

- 位置与实测（纯文本 `wc`/分词统计，口径见下）：`ms.txt` 第 9–75 行（Abstract + Introduction + Results + Discussion）合计 ≈ **5152 词**；其中第 11–75 行（Intro/Results/Discussion）≈ **5003 词**；摘要单行 `ms.txt:10` = **148 词**（≤150，达标但卡线）；Methods 段（76–116 行）≈ 3229 词另计；图注（187–192 行）≈ 939 词另计；全文 11040 词。
- 说明：这是按空格分词的纯文本统计口径，**不是 Word 官方 word count**；Word 会把 `ω = k_f/k_n`、化学式、带连字符项计作多个词，且是否含小标题/图表引用括号会影响结果，故不臆造精确超标字数。无论按 5003 还是 5152，均已处于或超过团队给定的 5000 词阈值。
- 原文佐证：`ms.txt:47` 单段 >400 词，`ms.txt:74`「Limitations.」整段亦极长，Results 各段密集堆叠括号限定语。
- 修法：出具 NC 正式口径 word count；将 Results 长段中的稳健性细节/数值清单移入 Methods 或 SI，压缩至 ≤5000；Cover letter（509 词，一页化达标）不需改动。

**P1-2　SI 表注残留旧 sheet 编号，与工作簿实际 sheet 名不同步。**

- 位置与原文引文：
  - `si.txt:326`「**Supplementary Table 9**: Cross-Organ Conservation Data ... Table content: CKI_Supplementary_Tables_NC.xlsx (**sheet Table 4**)」。
  - `si.txt:328`「**Supplementary Table 10**: Human Brain Non-neuronal Cell Regional CKI Data ... Table content (per-cell-type summary): ... (**sheet Table 5**)」。
  - `si.txt:330`「**Tables 5 and 6** share the same underlying data file (results/brain_bs_null_observed_pairs.csv): Supplementary Table 10 reports all 31,764 pairs ... whereas Supplementary Table 12 retains the 6,591 ... Table content: ... (**sheet Table 6**)」——同句内既有正确的「Supplementary Table 10 / 12」，又有残留的「Tables 5 and 6」「sheet Table 6」。
- 对照（同一材料包内）：`si.txt:58`「Supplementary Tables 1-17 are provided as a single workbook ... **sheets Table 1-17 in numeric order**」；`tables_overview.txt` 中 `sheet 'Table 9'` = Cross-Organ Conservation Data、`'Table 10'` = brain per-cell-type、`'Table 12'` = region-associated candidates。
- 修法：`sheet Table 4/5/6` → `sheet Table 9/10/12`；`si.txt:330` 句首「Tables 5 and 6」→「Supplementary Tables 10 and 12」。这是本包内确凿的残留旧表号（任务书举例的「2a vs 2c」经核查并不存在，见 §4 优点 3；实际不同步落在此处）。

**P1-3　主图/附图引用前缀省略，造成主图首现顺序歧义。**

- 位置与原文引文：
  - `ms.txt:41`（位于「Real-data neutral-drift calibration」小节，讲 microglia supercluster）「the margin carried by k_f (**Supplementary Note 7, Fig. 4**)」——此处的裸 `Fig. 4` 出现在主文 Figure 3 首现之前。
  - `ms.txt:45`「comparing tumor–tumor (TT), normal–normal (NN), and tumor–normal pairs per type (**Fig. 3; Supplementary Fig. 3**)」为主图 Fig. 3 首现；`ms.txt:53`「ω was computed for all same-cell-type cross-region pairs (31,764; **Fig. 4**; Supplementary Fig. 6, Table 10)」为主图 Fig. 4 明确首现。
  - 若把 `ms.txt:41` 的 `Fig. 4` 读作主图，则主图首现顺序为 1(:14) → 2(:26) → 4(:41) → 3(:45)，**非单调**；若按 SI 的「承前省略 Supplementary」惯例，其语境（microglia sanity check）对应的是 `si.txt:339`「**Supplementary Fig. 4**. Human-brain sanity check on the microglia supercluster ...」，则属**缺 `Supplementary` 前缀**。同理 `ms.txt:54`「(Fig. 4e, f; Supplementary Note 18, Fig. 7, Table 11)」、`ms.txt:71`「(Supplementary Note 17, Fig. 9)」中的裸 `Fig. 7 / Fig. 9 / Table 11` 亦为省略写法。
- 判定：不断言为硬编号错误，而定性为**引用表述歧义**——裸 `Fig. 4` 在 `Fig. 3` 之前出现，会被编号首现顺序核查判为非单调，且读者易误指主图。
- 修法：统一写全「Supplementary Fig. 4 / 7 / 9」「Supplementary Table 11 / 14」；确保主图 1–4 首现顺序为 1→2→3→4。伴生图 Supplementary Fig. 11 在 Introduction（`ms.txt:16`）即首现，已由 `si.txt:335` Numbering note 豁免说明（见优点 3），属可接受，但建议首次引用补注「companion to main Fig. 2」。

### P2（非阻断，建议清理；均仍成立）

**P2-1　Zenodo 使用 concept DOI 指「earlier release」，存在版本漂移张力（但当前措辞诚实、合规）。**

- 位置与原文引文：`ms.txt:120`「**An earlier release** is archived at Zenodo (**concept DOI: 10.5281/zenodo.20405458**); the code accompanying this submission is the v0.6.4 tag.」「**an earlier snapshot** is mirrored in the Zenodo archive (DOI: 10.5281/zenodo.20405458)」；`guide.txt:26`「Archived release: Zenodo **concept DOI** 10.5281/zenodo.20405458 (**an earlier release**); the code accompanying this submission is GitHub tag v0.6.4」。
- 核查结论：措辞**诚实**——明确标注为 earlier release / earlier snapshot，**未**声称「v0.6.4 archive accompanies this submission」；对 si.txt / guide.txt 全文检索 `always resolves|resolves to latest|latest version|accompanies this submission|archive accompanies|v0.6.4 archive` **均无匹配**，无「always resolves to latest」类漂移表述。此项通过初筛。
- 建议修法（非必须）：concept DOI 按定义解析到该记录的最新版本，与静态「an earlier release」指向存在张力；宜改用 **version DOI** 锁定所指存档，或补一句「concept DOI 指向记录最新版本，特定 earlier release 见 version DOI」。与 P0-1 的收尾建议联动：随稿 v0.6.4 版本本身宜另给版本化存档。

**P2-2　内部构建轮次标签泄漏到面向读者的文档，且仅在 MANIFEST 中解释。**

- 位置与原文引文：`tables_overview.txt:95`「Two-caliber NN/TT ω reversal table (**ex-CC cohort, v52**)」；`si.txt:285`「the full procedural detail compressed out of the main-text Methods **in v51**」；`si.txt:178`「**AUC interval methods (v52)**」；`si.txt:296`「excluded from all **v52** analyses」；`guide.txt:323`「**5.10 v49 Analyses**」、`guide.txt:332`「**Superseded in v52** by the ex-CC default chain」；而 `manifest.txt:6`「Note: '**v49**' is the package build-batch label, **not a software version**」是唯一解释，且仅存在于投稿清单（guide.txt 内检索 `build-batch` / `batch label` / `not a software version` 均为 0）。
- 说明：`v40–v52`、`v49.12/.13/.14`、`nc50/52/60/70/78/79/80/82/83/84` 多为真实脚本名/结果文件名/分析轮次，作为产物标识**不影响可复现性**；软件版本串本身是统一的（ms/si/guide/manifest 全为 0.6.4，另 `v0.5.x` 两处为历史默认行为描述，合法）。问题在于 SI/Guide/表注正文出现 v50/v51/v52 而读者无从区分其与 0.6.4 的关系。
- 修法：在 Guide 开头补一句术语说明（vXX / ncXX 为内部分析轮次与脚本标识，非软件版本）；在不影响脚本定位处（如表注）改用语义描述。

**P2-3　主文图注偏长、Cover letter 信息过密、ORCID 仅通讯作者。**

- 位置与原文引文：`ms.txt:188–191` 主文 Figure 1–4 图注，其中 Figure 4 图注约 400 词；`cl.txt` 共 509 词，第 3 段单段 >300 词；`ms.txt:8`「**ORCID: Li Zhang 0000-0002-0698-0754**」（仅通讯作者 1 位，Wenting Liu、Jian Zu 未列）。
- 修法：精简 Figure 4 图注、Cover letter 分点列四支柱；按 NC 作者信息要求补齐合著者 ORCID（若适用）。

---

## 4. 优点（4 条）

1. **可复现性材料罕见地完备**：`guide.txt:9–47` 给出 verified environment（Python 3.14.4、numpy 2.4.6、scanpy 1.12.1 等精确版本）、requirements-lock.txt、Dockerfile、逐节数据依赖与脚本/输出；`guide.txt:556–587` 的 Reproducibility Checklist 含 `spot_check.py`（46 条断言）、29 项 pytest、逐项 spot value；`si.txt:331–332` 有 Supplementary Data 1 脚本索引；`ms.txt:117–118` Data availability 列出全部 accession（GSE109774、GSE96583、CELLxGENE collection ID 283d65eb-…、GDC、GTEx、cBioPortal、MSigDB）并声明「All Supplementary Tables (1–17) are provided in CKI_Supplementary_Tables_NC.xlsx」，与 `manifest.txt` 文件清单一致（两份 MANIFEST 经逐字节比对完全相同）。定稿前重查确认 v0.6.4 tag 已发布，使上述可复现链路的入口（Code availability）由「不可核验」转为「可核验」。
2. **统计与局限披露透明、替代声明齐备**：主动标注 anti-conservative null、permutation resolution 限制（q<0.05 不可达）、descriptive / hypothesis-generating 定位；scDist 的 R 原生包不可安装一事在三处一致标注——`ms.txt:74`「the scDist comparison uses a Python approximation of the R implementation, which could not be installed in this environment」、`si.txt:134`「the R package was unavailable in our environment ... is labelled "Python approximation of scDist" throughout」、`tables_overview.txt:30`「scDist (Python approximation)」。AI disclosure（`ms.txt:115–116`）、Competing interests、Author contributions、Acknowledgements、Correspondence 齐全。
3. **编号体系闭环、无悬空引用、无 2a/2c 语义不同步**：主文主图 Figure 1–4 与图注齐全（ms.txt:187–192）；SI 附图图注 1–11 齐全（si.txt:336–346，共 11 条）；附表 1–17 在 SI 目录（si.txt:39–55）与工作簿 sheet（tables_overview.txt: Table 1–17）一一对应；SI Notes 1–24 在目录（14–37）与正文标题（172–281）均单调无跳号/重复；全材料检索未发现 Note>24 / Table>17 / Fig>11 的悬空引用。**特别核查任务书点名的 2a/2c**：`Supplementary Table 2a`（si.txt:136，mean-shift AUC）、`2b`（ms.txt:73、si.txt:137，power）、`2c`（ms.txt:36/189、si.txt:178/179，six-metric ROC）分别对应 `tables_overview.txt:25` caption 的 (a)(b)(c) 三个不同子面板，语义正确且跨文档同步；`8a/8b/8c/8d/8e`（ms.txt:47）亦与 `tables_overview.txt:95` 的 (a)–(e) 子面板一致。`si.txt:335` 有 **Numbering note**：「Supplementary Figs. 1–9 follow the order of first citation in the main text; Supplementary Figs. 10 and 11 are companion figures to main Figs. 3 and 2, respectively, and retain their series numbers so that cross-references remain stable」，与 `si.txt:345`（Fig. 10 = companion to main Fig. 3）、`si.txt:346`（Fig. 11 = companion to main Fig. 2）自洽，伴生图编号豁免有明确说明。
4. **Zenodo 措辞诚实、Cover letter 一页化达标**：明确标为「an earlier release / an earlier snapshot」，未声称 v0.6.4 archive 随投稿，无「always resolves to latest」漂移表述（见 P2-1）；`cl.txt` 509 词单页、含 6 位无冲突 suggested reviewers（含单位与邮箱）及通讯作者署名，符合 NC 一页化要求；摘要 148 词 ≤150，参考文献 1–57 采用 NC 数字编号格式且无跳号。

---

## 5. 给编辑的备注

**初筛结论：可送外审。** 初审曾以「技术性退回」处理，唯一依据是 Code availability 声明的 `tag v0.6.4` 在审稿启动时尚不存在、随稿代码不可核验。定稿前**重查于发布后**（本人重新执行 `git ls-remote --tags origin` 与 `git ls-remote origin refs/heads/main`，不采信转述数值），亲眼确认 `refs/tags/v0.6.4 = 0d7d057644dfae709dc2fe0cc59730ef48e535eb`（annotated）、`v0.6.4^{} = d7e45cf4aecdc66504e59b727f9370e2771db383`、`refs/heads/main = d7e45cf4aecdc66504e59b727f9370e2771db383`——tag 真实存在且 peeled commit 与 main 头一致，全文统一的 0.6.4 版本串现与远端一致，`si.txt:332` 的裸 clone 安装路径亦连带对应随稿版本。阻断项已闭合，**无剩余技术性退回理由**，可进入外审。

**保留的诚实边界**：`ls-remote` 仅能证明 tag 的存在与指向；「该 tag 内含全部 Methods/SI 引用脚本」为内容级断言，需 clone 逐文件比对，超出本轮授权工具范围，本报告未予证实，建议编辑部在送审版本归档时或由外审复现环节核对，并归档 commit SHA 作为版本凭据。

**建议：Major Revision（维持不变）**。初筛通过不等于无需实质修订：学术层面本稿结论多为 descriptive / hypothesis-generating，正向发现偏弱、部分断言需收窄（详见 6 维评分），且仍有 P1 三项（P1-1 出具 word count 并压至 ≤5000；P1-2 旧 sheet 编号 Table 4/5/6 → 9/10/12；P1-3 补全 Supplementary 前缀）与 P2 三项（version DOI、内部轮次标签、图注/ORCID）需在一轮修订中处理。这些均非阻断项，可在外审意见合并后统一修订，无需重投或重新评估科学内容。本报告不代替 R1–R5 的方法学/统计/领域判断。
