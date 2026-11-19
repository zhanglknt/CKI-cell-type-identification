# CKI (Nature Communications) — nc85 修后包专家团盲审与打分报告

- **送审版本**：根包 `CKI_Submission_NC/`（nc84 修后态；`99_build_nc_v49.py` NO_ARCHIVE **240/240** 构建）
- **发布状态**：本轮已发布——远端 `main = d7e45cf`、`tag v0.6.4 = 0d7d0576`（peeled = main），tree `7ac4d980` 与本地逐字节相等
- **包规模**：23 文件 / zip 23 条目 13,634,695 B / sha256 `6e15e10f896c3b40…9879fd`；单文件 max 3.31 MB
- **稿件规模**：MAIN 5,000/5,000、摘要 148/150、Methods 3,228、CL 509/530、图注 max 337/350；SI Notes 1–24、Supplementary Figs. 1–11、Tables 1–17
- **审稿方式**：6 位独立审稿人（互不可见、禁止读取 nc81/nc83/nc84 前轮汇总与彼此报告、禁止联网检索作者身份、禁止读记忆文件），同 nc81/nc83 角色与口径；+ 1 层主编独立事实核查（`_nc85_editor_factcheck.md`，不向审稿人出示）
- **材料包**：`results/audit/_nc85_review_materials/`（ms / si / cl / guide / tables_overview / manifest / round，从**最新** DOCX/XLSX 提取）
- **独立报告**：`results/audit/_nc85_review_R1.md` … `_R6.md`；机械汇总 `_nc85_panel_summarize.py` → `_nc85_panel_scores.json`

---

## 1. 评分总表

| 审稿人 | 身份 | 新颖性 | 理论严谨 | 统计严谨 | 证据充分 | 表达清晰 | 影响力/NC | **总分** | 建议 |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 单细胞方法学与基准测试 | 5.5 | 4.5 | 4.5 | 4.0 | 6.5 | 4.0 | **4.8** | **Reject** |
| R2 | 统计推断 | 6.5 | 7.0 | 7.0 | 6.0 | 6.5 | 6.0 | **6.5** | Major Revision |
| R3 | 癌症基因组学 / 临床转化 | 6.0 | 6.5 | 7.5 | 6.5 | 7.0 | 6.0 | **6.5** | Major Revision |
| R4 | 分子演化（Ka/Ks） | 6.0 | 4.5 | 5.0 | 5.0 | 6.0 | 5.0 | **5.5** | Major Revision |
| R5 | 脑图谱 / 神经科学 | 6.0 | 7.0 | 6.5 | 5.5 | 6.0 | 5.5 | **6.0** | Major Revision |
| R6 | 期刊编辑 / 可复现性 | 7.0 | 7.0 | 8.0 | 7.5 | 6.0 | 6.5 | **7.0** | Major Revision（重查后初筛「可送外审」，见 §2） |
| **nc85 均值** | — | **6.167** | **6.083** | **6.417** | **5.750** | **6.333** | **5.500** | **6.050** | **1 Reject / 5 Major** |
| nc83 均值 | — | 6.25 | 6.08 | **7.25** | 6.08 | 5.67 | 5.58 | **5.92** | 6/6 Major |
| nc81 均值 | — | 6.50 | 6.40 | 6.30 | 5.90 | 6.00 | 5.70 | **6.10** | 6/6 Major |
| **Δ vs nc83** | — | −0.08 | ±0.00 | **−0.83** | −0.33 | **+0.66** | −0.08 | **+0.13** | 首次出现 Reject |

**R6 定稿说明**：初审总分 6.5（因 P0 阻断下调）；定稿前 R6 亲自重查远端、确认 tag v0.6.4 已发布后，把 P0-1 改判为「已闭合的时序问题」、初筛结论改为「可送外审」，并按其 6 维均值回调总分为 **7.0**（6 维分数本身不变）。本表及均值 6.050 采用 R6 定稿值。

> **判定：Major Revision（不 CLOSED）**，均值 **6.050**，较 nc83 的 5.92 回升 +0.13，仍略低于 nc81 的 6.10。
> 表达清晰 5.67 → 6.33（**+0.66**，唯一显著改善）：nc84 清除了图注拼接残留、旧图号、版本串、悬空引用，`Numbering note.` 与 claim-to-test map 被 R2/R6 点名「上乘 / 罕见地完备」。
> 但**统计严谨 7.25 → 6.417（−0.83）**：并非新统计错误，而是 R1/R4 把「10x 平台退化、power 随样本量归零、ω 不优于 k_f」等**已在稿件内自我披露的负面证据**当作方法失效的硬证据。
> 影响力/NC 5.50 仍是六维最低；证据充分 5.75 次之。R1 是三轮以来第一位给出 Reject 的审稿人。

---

## 2. R6 的 P0-1 时序假阳性：由 R6 本人重查后自行闭合

R6 在**本轮发布完成之前**运行 `git ls-remote`，得到「远端最高 v0.6.3、main = 0eea59e」，据此把「Code availability 声明的 tag v0.6.4 不存在」列为唯一 P0，初审判「技术性退回（Return before review）」。审稿进行期间作者已执行发布。主编向 R6 发出纯客观状态更新（不透露任何其他审稿意见或往轮结论），请其**亲自重查**；R6 重跑后确认：

```
git ls-remote origin refs/heads/main    -> d7e45cf4aecdc66504e59b727f9370e2771db383
git ls-remote origin refs/tags/v0.6.4* -> 0d7d057644dfae709dc2fe0cc59730ef48e535eb (annotated)
                                         d7e45cf4aecdc66504e59b727f9370e2771db383 (v0.6.4^{})
```

**R6 定稿处置（保持盲审独立性，未由主编代改）**：
- P0-1 改判为「**已闭合的时序问题**」，报告内并列记录第一次（发布前）与第二次（发布后）两次核验输出；
- 初筛结论由「技术性退回」改为「**可送外审**」；
- 6 维分数全部不变（7/7/8/7.5/6/6.5，均值恰为 7.0），因「不再有下调理由」，总分由初审 6.5 **回调至 7.0**；
- P1-1/2/3、P2 各项与全部优点保留。

**汇总口径**：
- **P0 计数**：定稿后 R6 **零 P0**；R2/R3/R4/R5 亦均明确「无 P0」或「可以送外审」。**全团唯一持有 P0 的是 R1 的三条结构性判断**（§3.2）。
- 均值按定稿值计 = **6.050**（若按初审 6.5 计为 5.967）。本报告以定稿值为准。
- 主编事实核查 F9 保留完整时序记录，供审计追溯。

> 教训：盲审期间若执行外部发布，技术初筛类审稿人会查到过期状态。正确处置是**向该审稿人提供纯客观状态更新并请其亲自重查**，而非由主编代改报告、也无需启动替代审稿人。

---

## 3. 两类问题必须分开陈述（本轮最重要的结论）

### 3.1 nc84 修复是否闭合了 nc83 的 P0/P1/P2？—— **是，包内全部闭合**

| nc83 问题 | nc85 实测 |
|---|---|
| 图合规 12/15、SF6 靠例外表 | **15/15 pass，EXIT=0**；例外表 `{}`，checker 删改判分支改逐页检查 |
| 声明 v0.6.4 但 tag 不存在（NC 红线） | **tag v0.6.4 已发布并核验**（§2） |
| 六指标 ROC 表缺失、`Supplementary Table 2a` 悬空 | **Table 2c 补齐**，MS/SI 四处指针同步，独立秩和复算零偏差 |
| AUC 0.648 语境错配、CNA 因果语气、理论口径过强 | 全部归位/降级；四文档无旧版本串 |
| 跨文档语义残留（旧图号、图注拼接、版本串） | 清除；R6 复核「编号体系闭环、无悬空引用、无 2a/2c 不同步」 |
| 全链验证 | **0 failure**：build 240/240、7 验证器全绿、pytest 29、三方逐 sha256 0 mismatch |

**R2/R3/R4/R5/R6 五人一致肯定**：claim-to-test map、置换分辨率诊断、two-way cluster-robust + PSD + wild-cluster、Zenodo 诚实措辞、scDist 替代声明、Reproducibility Guide 与 spot-check、限定语密度，被点名为「罕见地完备 / 上乘 / 诚实度极高」。R3 明确「本轮未识别 P0」；R4/R5 明确「可以送外审」；R6 明确「补正后可直接进入外审，无需重新评估科学内容」。

### 3.2 但重审暴露了更根本的结构性问题——**不是「再修一轮文字」能解决**

**R1 的三条 P0（4.8/Reject 的全部依据）**，经主编逐条核对，其数字**全部来自稿件内主动写入的自我披露**（`_nc85_editor_factcheck.md` F7）：

| P0 | 稿件内自认的证据 | 性质 |
|---|---|---|
| ground-truth 模拟循环论证 | SI L173「functional signal = non-HK 200 基因模块」、L181「the same anchoring assumption that CKI itself makes … conditional on that assumption rather than evidence for it」 | 稿件已自认；R1 要求建立与 HK/identity 划分无关的独立状态标签 |
| 10x 平台退化 | SI L142 pooled AUC ω 0.507–0.534、δ=1 检出 0.003–0.030；SI L137 power 随 n 增大归零；MS L10「background-specific precision advantage bought with sensitivity」 | 稿件已自认并写进摘要；R1 要求收窄适用范围到 SmartSeq2 窗口 |
| ω 增量价值未确立 | SI L206 Kang ω 0.551–0.922 < k_f 0.743–1.000；SI L138「CKI is weaker than the competitors」；SI L270「k_f-only is itself specific … FPR alone do not separate ω from k_f」；SI L158 ω 0.661 < DE 0.736 | 稿件已自认；R1 要求预注册成功标准或重定位为「分解的诊断性 caution」 |

**主编判断**：nc84 的「诚实降级」把内生局限显性化，反而给了严格审稿人「方法核心主张被自身证据系统性否定」的完整弹药。这不是修复引入的错误，而是**披露与主张之间的张力被推到极限**：稿件一方面把定位收窄到「precision-first、group-level、housekeeping-anchored caution」，另一方面标题/摘要仍用「cell atlases」「drug response and aging」等普适口吻（R1 P0-2）。同理，R4 的 P1 全部指向「Note 20 的 identification 前提在核心实证中被自认违反、estimand 从未被估计、studentization 修辞强度超过框架实际使用程度」；R3/R5 的 P1 指向「4 供体有效独立单元」「PMI/ambient/doublet 未建模」「GTEx 分辨力不足却用于排除 field effect」。

**结论**：包内自洽性与技术合规已闭合；剩下的争议是**方法定位与证据设计的结构性问题**，需要新分析（独立 ground truth、去 floor 敏感性、ambient/PMI 对照、预注册成功标准）或叙事重定位，不是改文字能关掉的。

---

## 4. 去重后行动清单

### A. 本包内可直接修的机械项（低成本，建议下轮即修）

| # | 来源 | 内容 | 主编复核 |
|---|---|---|---|
| A1 | **R6 P1-2** | SI 表注残留旧 sheet 号：标题 `Supplementary Table 9/10/12` 对应正文 `(sheet Table 4/5/6)`；工作簿实际为 `Table 1–17` | **属实，本轮新发现的真残留**（F8）：`sheet Table 4/5/6` → `9/10/12`；`si L330` 句首 `Tables 5 and 6` → `Supplementary Tables 10 and 12` |
| A2 | **R3 P1-1 + 主编 F7** | SI Note 22（si L276）仍写 `copy-number divergence creates rather than attenuates the TT/NN gap` / `attributes 56% to copy-number divergence`，与主文 `associated with at most 56% / unmeasured-reference upper bound` 不同步 | **真跨文档语义落差**：应统一为关联/上界口径（nc80 复分析的历史叙述需保留但改限定语） |
| A3 | **R3 P2-1 / R6 P2** | CL 的 `56%` 未带 `at most` 上界；Abstract 单独给 AUC 0.648 未带 group-level 限定 | 与 A2 同源；CL 受 530 词额约束，改词不增字数 |
| A4 | **R4 + R3** | Note 20 的 `identified / studentizes / eightfold / identifiability / 单调性保证` 强度超过 `si L270–271` 已有 scoped 措辞；α 在三处承载正交含义；ε 未定量 | 降级为 scoped 措辞、统一 α 符号、定量 ε、补 C5/A1 失效场景 |
| A5 | **R5 P2-1 / P2-4** | 「发育起源异质性」与「迁移」机制引用残留，缺排除性声明；Fig 4 图注未同等披露 Note 24 的 DEF-CV 结果（超类 P 0.72–0.92）与 Note 18 的 Thalamic underpowered | 图注/正文补披露，不改数据 |
| A6 | **R6 P1-3** | 裸 `Fig. 4`（`ms L40` 的 `Supplementary Note 7, Fig. 4`）造成主图首现顺序歧义 | 属表述歧义非编号错误；统一写全 `Supplementary Fig. 4` |
| A7 | **R6 P1-1** | 词额按空格分词 ≈5,152，NC 正式口径 5,000/5,000 | 口径差异非硬超标；投稿前出具 Word 官方计数凭证即可 |
| A8 | R4 格式 | R4 判定标签残留 `<...>` 尖括号占位符 | 纯格式，结论完整 |

### B. 需新分析 / 新数据的结构性项（高成本，需作者裁定）

| # | 来源 | 内容 |
|---|---|---|
| B1 | R1 P0-1 | 建立与 HK/identity 面板划分无关的独立状态变化标签（时序/谱系/多供体真实扰动），重估 ROC 与校准；含「功能信号落在锚上、漂移落在 identity 面板」的混合场景 |
| B2 | R1 P0-2 | 把适用范围显式收窄到「深测序 SmartSeq2 + 50–200 cells/组」并删普适性措辞；或对 power 非一致性给出统计机理 + 大图谱 pseudobulk 的可用替代推断 |
| B3 | R1 P0-3 | 预注册成功标准，展示 ω 严格优于 k_f-only 与至少一种现有方法；若无法做到，把论文重定位为「k_f/k_n 分解的诊断性 caution」而非「新指标优越性」 |
| B4 | R5 P1-1/P1-2 | snRNA-seq 特异的 ambient/降解敏感性（SoupX/CellBender/DecontX 或内含子比例 proxy）重算 k_n 与 3.66-fold 梯度；带 PMI/RIN 元数据的独立尸后脑队列给斜率与 CI |
| B5 | R3 P1-5 + 主编 F7 | `k_n floor = 1e-4`（TCGA-only）的触底比例 + 去 floor 后 NN/TT 结论稳健性专项敏感性 |
| B6 | R2 编辑备注 | claim-to-test map 的跨家族未联合校正能否给出独立簇级推断；dyadic/cluster 推断的口径收口 |
| B7 | R4 | 定量 ε、补齐 C5 与 A1 失效场景检验；或降级 Note 20 理论宣称 |
| B8 | 行政 | Zenodo v0.6.4 版本归档（需 API token 或网页端操作）；CL 是否严格一页；共同作者 ORCID 无权威来源 |

### C. 已闭合 / 无需动作

- 图合规 15/15、tag v0.6.4 发布、Table 2c、全链 240/240、三方 sha256、编号豁免（作者已追认）、Zenodo 措辞诚实、scDist 替代声明、Numbering note、claim-to-test map、SI 附图/附表/Note 编号闭环 —— R2/R3/R4/R5/R6 均点名肯定。

---

## 5. 六位审稿人意见（去重前摘要）

**R1（4.8 / Reject）**：三条 P0（循环论证、10x 退化无剂量响应且 power 归零、ω 增量价值未确立）+ 5 条 P1（precision/specificity/sensitivity 混淆、验证任务与定位错配、estimand 依赖数据选择面板、HK 面板敏感性、单细胞技术混杂）+ 2 条 P2。结论「实质等同新稿件，非补充若干实验可解」；但明确肯定「自我审计与复现工程堪称范本、披露异常诚实」。

**R2（6.5 / Major）**：无 P0；5 条 P1 + 7 条 P2，核心是「披露充分、口径未收口」。点名 claim-to-test map、置换分辨率诊断、two-way cluster-robust + PSD + wild-cluster、描述/推断分离为「范本级」；建议交熟悉重抽样/聚类稳健推断的统计审稿人专复核，不建议以再送一轮外审代替实质修订。

**R3（6.5 / Major）**：明确「本轮未识别 P0」；5 条 P1（残留因果动词、56% 上界披露不对称、GTEx 分辨力、pan-cancer 泛化、纯度/组成与 floor 敏感性） + 4 条 P2。逐条核对 10 项限定语后判定「整体极克制、无过度声称」；明确「可送外审，不建议 desk reject」。

**R4（5.5 / Major）**：无 P0；4 条 P1 + 2 条 P2，全部指向 Note 20 的理论口径（identification 前提在核心实证中被自认违反、estimand 从未被估计、α 三重含义、Prop 4 单调性适用范围错位、studentization 修辞过强、ε 未定量）。赞「Ka/Ks 类比的边界限定堪称模范」，判「理论更接近事后诠释而非方法学支柱」；建议至少指定一位理论统计+分子演化背景审稿人专复核 Note 20。

**R5（6.0 / Major）**：无 P0；3 条 P1（4 供体有效独立单元、PMI/ambient/doublet 让步不足、Fig 4 图注漏报 anchor-collapse 与 Thalamic 功效）+ 4 条 P2。肯定脑结论已诚实降级到 housekeeping-anchored class-level；建议增补 1 位人脑 post-mortem snRNA-seq 技术混杂方向的审稿人。

**R6（7.0 / Major，重查后初筛「可送外审」）**：初审唯一 P0 为发布时序假阳性，经本人重查后闭合（§2）；3 条 P1（词额口径、SI 旧 sheet 号、裸 `Fig. 4` 前缀）+ 3 条 P2。肯定「可复现性材料罕见地完备、编号体系闭环、无悬空引用、Zenodo 措辞诚实、CL 一页化达标」；明确「问题为可快速修复的行政/技术项，不涉及学术结论造假或数据问题，补正后可直接进入外审，无需重新评估科学内容」。

---

## 6. 主编判定与建议

> **判定：Major Revision — 不 CLOSED。** 均值 6.050（nc83 5.92 / nc81 6.10），1 Reject + 5 Major；**6/6 均认为技术层面可送外审**（R6 重查后初筛明确「可送外审」）。

三点必须向作者讲清楚：

1. **技术层面已可投稿**：图 15/15、tag v0.6.4 已发布、全链 0 failure、三方一致、编号豁免已追认、四文档无悬空引用与旧版本串。nc83 的 P0/P1/P2 全部闭合，R3/R4/R5 明确「可送外审」、R6 重查后初筛「可送外审」，R2 建议 Major 而非 desk reject。
2. **但科学判定没有随修复实质上升**：三轮均值 6.10 → 5.92 → 6.05，回升 +0.13 但仍低于 nc81，且首次出现 Reject。原因不是修坏了，而是「诚实降级」把内生局限（10x 退化、ω 不优于 k_f、4 供体、理论 identification 失效）全部写进稿件，严格审稿人据此认为核心主张被自身证据否定。**继续加限定语不会抬分，可能继续压低影响力/证据分。**
3. **下一步是方向性抉择，不是再修一轮文字**：(a) 按 R1/R4 把论文重定位为「HK 锚定归一化的诊断性 caution / k_f/k_n 分解」并删普适性主张，配 A 类机械修复，预期 5/6 转 Minor/Major 低位；(b) 投入 B1–B5 的新分析重建独立 ground truth 与增量价值，周期长但才可能实质抬分；(c) 维持现稿直接投，接受首轮外审可能 desk reject 的风险（R1 的意见若落到真实 NC 编辑手上权重不低）。

**本轮已执行的用户裁定**：① 完整 GitHub 发布（squash `d7e45cf` + force-push main + `tag -f v0.6.4` + `ls-remote` 核验）；② F2 编号豁免路线追认；③ 专家团重审打分（本报告）。

**残余 minor**：共同作者 ORCID 无权威来源；CL 509 词是否严格一页取决于排版；ambient/doublet/PMI/RIN 采用文字让步；Zenodo v0.6.4 归档未执行（缺 API token，稿件措辞不依赖其存在）。

---

## 7. 补记：迟到的独立技术初筛（r6-alt，不并入均值）

`results/audit/_nc85_review_R6_alt.md` 是在 R6 原审稿人 recovered 之后才落盘的**替代审稿人报告**，独立第七份意见，评分 **7.0 / 10、Minor Revision、P0 = 0 项**，初筛结论为「技术性退回（Return before review）」。

**口径裁定**：
- 该报告**不并入 nc85 六人团均值 6.050**，也不改变「1 Reject / 5 Major」分布；它是**补充技术初筛**，不是第七位正式盲审。
- 其初筛退回**不是**版本/归档问题（P0-候选 1 明确通过：tag v0.6.4 与 `An earlier release is archived` 措辞诚实），也**不是**图合规或全链验证问题（15/15、0 failure 全通过）。退回仅由 2 项 P1 触发：
  1. SI 补充表索引 3 处错误 sheet 指针（`si.txt:326/328/330` 把 Supplementary Tables 9/10/12 指到 `sheet Table 4/5/6`）；
  2. SF9 在 MS 正文零规范引用 + `ms.txt:71` 裸 `Fig. 9` + Numbering note 与实际失配。
- 两项均为**文案级**，「修完即可直送外审」，与本报告 §6 判定（技术层面可送外审）不冲突。

**处置**：r6-alt 的 P1-1/P1-2 及 4 项零成本 P2（旧图号、Guide 节图错配、内部轮次标签、pip 一致性）已全部纳入 nc86 A 类修复并随 **v0.6.5** 重发，逐项核销见 `_nc86_fix_report.md` §2–§3。P2-3/4/7 记录不改（非悬空 / 已清除 / 达标）。词额顶格警告已由 A7 凭证（MAIN 净 −1 词）闭合。
