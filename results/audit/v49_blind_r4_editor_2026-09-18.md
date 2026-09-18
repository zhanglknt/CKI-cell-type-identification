# R4 盲审报告：学术编辑与 NC 合规 — CKI v49 投稿包

- 评审人角色：R4（学术编辑 / Nature Communications 合规）
- 日期：2026-09-18
- 材料：`version3/CKI_Submission_v49_NC/`（MS / SI / CL / Reproducibility Guide fulltext + MANIFEST）
- 性质：只读评审，未修改任何稿件文件

## 总评

- **评分：6 / 10**
- **判定（编辑视角）：Minor Revision（投稿前必须修的均为机械性修复）→ 修后具备送审资格；按现状直投则 Desk-reject risk：中等（~40–50%），主因不是合规而是 breadth 论证与 2.6× 篇幅。**
- v49 的两个新增分析（真实数据漂移校准、泛癌图谱）选点正确、写法与全文自限式语气一致；CL 的"直接回应"策略方向正确但执行有两处硬伤：一处与正文可核对地矛盾（P0-3），一处框架风险（P1-1）。**投稿前阻断项是复现指南整体停留在 v48 编号体系（P0-1）和缺失 Reporting Summary（P0-2）。**

---

## P0（投稿前必须修复）

### P0-1 复现指南（Additional file）整体未随 v49 更新，与主稿直接矛盾
位置：`CKI_Reproducibility_Guide_NC_fulltext.txt`
- 图号全部沿用旧体系：L109 `TCGA — Result 4 (Fig. 4)`、L125 `Cross-organ conservation (Result 5, Fig. 5)`、L126 `Brain — Result 6 (Fig. 6)`。v49 主稿中 TCGA = Fig. 5、cross-organ = Fig. 6、brain = Fig. 7，Fig. 4 是新增的漂移校准图。审稿人按指南核对会立即发现错位。
- L120 声称 "the manuscript and Fig. 4a report the **median** NN/TT omega ratio"——v49 主稿 Fig. 5a 报的是 **ratio of means**（cluster-bootstrap CI），统计口径直接矛盾。
- 指南对 v49 两个旗舰分析**完全没有条目**：grep 全文无 `nc49`（无 nc49_tcga_main.py / nc49_pilot_lihc_cox.py / 漂移阶梯 / Kang batch-1 复现步骤）。主稿 Methods 明确引用了这些脚本（MS L117–123），SI 3.20/3.21 也引用了，指南却只字未提——恰好是 GB 回应证据无法按指南复现。
- SI 图号同样陈旧：L224 cross-species 标为 `Supplementary Fig. 12`（v49 实为 SF11），L285 Kang demo 标为 `Supplementary Fig. 10`（v49 实为 SF3）。
- 建议：以 v49 图号/SI 号重排指南 4.x 节；为漂移校准（Kang batch-1 + 脑阶梯）与 TCGA per-sample 统计新增两节（脚本、输出、spot-check 值）；将 L120 改为 mean-ratio 口径并与 Fig. 5a 对齐。

### P0-2 缺失 Reporting Summary 与 Editorial Policy Checklist
位置：`MANIFEST_v49.txt`（31 项中无）
- NC 生命科学类投稿在初投即要求 Life Sciences Reporting Summary（与 Editorial Policy Checklist）。主稿已有 `Statistics and reproducibility` 一节（MS L128–131），内容与 Reporting Summary 的 Statistics 栏天然对应，填表工作量小。缺此件在投稿系统中会被卡或留下"材料不全"的第一印象。
- 建议：按 Nature 模板填写 Reporting Summary（Statistics / Data / Code / Materials 各栏均可直接引用 MS 对应节），加入 MANIFEST。

### P0-3 Cover Letter 第二支柱与正文可核对地矛盾（overclaim）
位置：`CKI_NC_Cover_Letter_fulltext.txt` L3："on 2,161 brain technical-drift pairs, **misreported least of seven metrics** (28.6% versus 44–45%, **lowest in all ten cell classes**)"
- 主稿（MS L40）与 SI 3.20 明确：marker Jaccard 的 T1 FPR = 19.9% **低于** ω 的 28.6%，ω 是"lowest **among divergence metrics** except marker Jaccard"；且"lowest in all ten cell classes"仅对 raw JS 成立（10/10），对 cosine 为 9/10、对 Spearman 为 8/10。
- 这是 CL 中被编辑/审稿人最容易抽查的一句（数字俱全），一旦被对照正文发现夸大，损害的正是 v49 全文苦心经营的"self-honest"信誉——而那条信誉恰恰是 GB 回应的根基。
- 建议改为："on 2,161 brain technical-drift pairs, the lowest false-report rate among divergence metrics (28.6% versus 37.6–45.2% for the other divergence metrics; below raw JS in all ten cell classes)"（marker Jaccard 可在 CL 不提，主稿 Fig. 4 已诚实呈现其 trade-off）。

---

## P1（强烈建议修复）

### P1-1 CL 直接回应段的框架风险：建议"新证据框架"替换"拒稿回应框架"
位置：CL L4（"Previously raised concerns that (i)…(ii)… have been addressed directly."）
- 分析：
  - "Previously raised concerns… have been addressed directly" 是 rebuttal 语态，把首读编辑置于"裁决一场他没见过的争议"的位置，并主动广播"此稿曾被拒"。若经 Springer Nature 内部 transfer 投出，编辑本就能看到 GB 历史，此时回应有理；若是 fresh submission，此句纯属自曝。两种情形下更优的是同一框架：**只陈述新证据及其回答的问题，不提"concerns"**。
  - 段内把全文最弱数字 "AUC = 0.680, 5th of 5" 以括号强调的方式放进 CL，是把 GB 审稿人的武器递到 NC 编辑手上。"5th of 5" 尤其没有必要——by-design 论证只需要 0.680 这个数，不需要排名。
  - by-design 论证本身对未读稿件的编辑**是成立的**（"指标在其设计问题上最优，分类不在其问题域"逻辑清晰，且有 0/30 与阶梯数据支撑），问题只在呈现方式。
- 建议替换段（约 95 词，覆盖同等信息量）：
  > "Two properties of this work are worth stating explicitly. CKI is a specificity-first index: its cell-type classification AUC (0.680) is modest by design, because it down-weights the global-identity signal that classifiers exploit; on the benchmark matched to its question domain—false divergence calls on real technical and donor drift—it misreports least among divergence metrics while retaining sensitivity to biology (Fig. 4). And the pan-cancer divergence map, with the lung adenocarcinoma driver-class decomposition, grounds the method in cancer biology of direct interest to a broad readership (Fig. 5)."
- 若团队最终走 SN transfer 且确认编辑可见 GB 历史，可在段首加半句 "This version adds two analyses (real-data drift calibration; pan-cancer map) that directly answer the two questions a new metric must answer"，仍然不需要 "previously raised concerns" 字样。

### P1-2 Abstract 与 Introduction 未收录 v49 旗舰证据，与 CL 推介错位
位置：MS L8（Abstract）、L14（"Here, we show" 路线图）
- Abstract 144 词覆盖 simulation / TCGA / brain 梯度，**完全没有**真实数据漂移校准（0/30；T1 28.6% 最低 FPR；阶梯 1.04→1.80）。CL 却把它列为第二支柱、GB 意见①的核心回应。首读编辑按 Abstract+Intro 形成的第一印象将与 CL 承诺不符。Introduction 路线图四件事（mouse calibration / TS correlation / TCGA / brain）同样无漂移校准。
- NC Abstract 上限 200 词（nature.com/ncomms/submit/article），144 词有充足空间。建议在 simulation 句后加一句："On real technical replicates (Kang IFN-β PBMC cross-lane pairs; 2,161 brain library pairs), ω misreported drift least among compared divergence metrics while retaining sensitivity to regional biology."；Intro 路线图相应加一项。这是 v49 性价比最高的一处修改。

### P1-3 SI 节号断裂与内部版本标签
位置：`CKI_Supplementary_NC_fulltext.txt`
- "Statistical Testing Details" 下节号为 3.1–3.4 后跳 3.7–3.11，再跳 3.18–3.21（L84–128）：3.5、3.6、3.12–3.17 整体缺失，呈现"删节痕迹"，审稿人必然注意到。v49 新增的 3.20/3.21 接在 3.19 之后，若重排为连续编号（或改为 Note 16/17）可同时解决"Section 3.x 与 Supplementary Note 1–15 双轨引用"问题（MS 对漂移校准引 "Section 3.20"（L41）、对其余内容引 "Supplementary Note X"，体例不一）。
- SI 多个标题带内部版本标签：Notes 2/4/5/14 "(v45)"、Note 10 "(v44)"、3.19 "(v44)"、3.20/3.21 "(v49)"（目录与正文各出现一次，共 14 处）。投稿件不应暴露内部迭代史。
- 建议：全部去除 "(v4x)" 标签；3.x 节号连续化或将 3.18–3.21 迁为 Supplementary Notes（推荐后者，与 MS 引用体系统一，工作量更小：MS 仅 L41、L119 两处 "Section 3.x" 引用需改）。

### P1-4 "Additional file 2" 无 "Additional file 1"
位置：MS L127、L201
- SI 以 "Supplementary Information" 名义存在（不算 additional file），故 Reproducibility Guide 应为 "Additional file 1: Reproducibility Guide"。当前凭空出现 "Additional file 2"，生产编辑会退回改。L201 同时建议删去 "(accompanying CKI_Supplementary document)" 的文件名式表述。

### P1-5 CL 与正文数字一致性（次生于 P0-3 的全面核对）
除 P0-3 外逐项核对通过：FPR 0.00 vs 0.55–0.58（L2 vs MS L8/35）✓；0 of 30 / 36.7% / 23.3% ✓；阶梯 1.04→1.76→1.80 vs 1.07→3.32→2.98 ✓；3,596 / 1.13–2.46 / 2.1–3.6× / P = 7.8×10⁻⁷ ✓。P0-3 修复后 CL 数字面即闭合。

---

## P2（建议修复，不阻断）

1. **SI 标题与主稿标题不一致**（SI L2："CKI: a Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics" vs MS："CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics"）。SI 题名页应与主稿一致。
2. **SI 目录条目名与正文不符**：目录 "Supplementary Data 1: Complete Analysis Script Index"（L32）vs 正文 "Supplementary Data 1: Analysis Script Index"（L209）。统一其一。
3. **标题含斜杠** "Ka/Ks"：NC checklist 建议标题不含标点（逗号、括号除外）。Nature 系刊实践中 "Ka/Ks" 类写法可见，风险低；若想零风险可改为 "Ka/Ks-inspired" 保留（现写法即如此，仅在标题中 "Ka/Ks-inspired" 含一个斜杠，可接受）。不改动亦可。
4. **Results 子标题长度**：v49 加回 level-2 子标题符合 NC 要求（Results/Methods 应有子标题；Discussion 无子标题 ✓ 已核实 Discussion 12 段无子标题）。NC 无字符上限明文，但参照 Communications Biology <60 字符的口径，"A pan-cancer map of tissue-level functional divergence in tumors"（64）、"Real-data neutral-drift calibration on technical replicates"（59）偏长，建议压到 ≤60。含冒号的三个子标题（L34、L42、L46、L66）NC 无禁例，可保留。
5. **作者单位缺邮编**（MS L3–4）：NC checklist 要求通讯地址含 postcode，初投从宽，返修时补。
6. **建议审稿人名单**：Sten Linnarsson 是被重度分析的脑图谱（ref 12）的通讯作者。不构成 NC 意义的 COI，且其数据被正面验证通常是友善审稿人；但若要规避"数据生产者护短/领地"两种极端，可考虑替换其一。无强制。
7. **CL 建议审稿人邮箱直接列在 CL 正文**无问题，但注意投稿系统通常另有入口，避免重复不一致。

---

## 按评审清单逐项结论

### 1. CL 攻防质量
见 P1-1 与 P0-3。结论：**保留"回应两条 GB 意见"的内容，切换为"新证据"框架；删除 "previously raised concerns… addressed directly" 与 "5th of 5"；修复七指标 overclaim。** by-design 论证对陌生编辑有说服力，但只在它不被多余的自我伤害性细节（排名、拒稿史）稀释时成立。另：CL 第一段 "the first framework to make a principled separation" 为强首创性声明，与 Discussion L76 "better described as a recombination of established ideas than a conceptual shift" 存在语气落差——审稿人对照后可能质疑；建议 CL 改为 "to our knowledge, the first index to operationalize a principled separation…" 保持但弱化，或在 CL 保留、接受此张力（团队自定）。

### 2. NC 合规复查
| 项目 | 状态 |
|---|---|
| Abstract 144 词 ≤150（NC 现行口径 200），无参考文献 | ✓ |
| 标题 11 词 ≤15，无冒号 | ✓（斜杠见 P2-3） |
| Introduction 带标题；Results/Methods 有子标题；Discussion 无子标题 | ✓ |
| Methods 内含 Statistics and reproducibility 节 | ✓ |
| Data availability 位于 Methods 后、References 前；Code availability 齐备（GitHub tag + Zenodo 双 DOI） | ✓ |
| Declarations 顺序（Methods → Data/Code → Refs → Acknowledgements → Author contributions → Competing interests → Additional info） | ✓ |
| LLM 使用声明（Methods L132–133） | ✓ 符合 Nature 系 AI 政策 |
| 图注 ≤350 词/图（最长 Fig. 4 = 288 词） | ✓ |
| 参考文献 56 条 ≤70 指南 | ✓ |
| 展示项 7 图 + 2 表 = 9 ≤10 | ✓ |
| Reporting Summary / Editorial Policy Checklist | ✗ **P0-2** |
| SI 双轨引用、节号断裂、版本标签 | ✗ P1-3 |

### 3. 稿件内部一致性
- 新增两节与既有节落语气/深度一致（同等的自限式写法；漂移节 L41 的 "Two honest qualifications" 与全文风格吻合）。泛癌节置于 fixed-panel ablation 与 cross-organ 之间，位置可接受。
- 主图 1–7 在正文均有引用且闭合；SF1–13 引用闭合（含 SF11 cross-species 在 Discussion L79 附近被引）；Supplementary Notes 1–15 均被主稿引用；Tables 1–4 闭合。
- SI 3.20/3.21 内容与 MS 对应节数字一致（抽查：T1 FPR 28.6%/45.2%、Kang 0/30、LUAD 组均值 136.9/122.2/115.4、Cox HR 1.06 [0.85,1.32] ✓）。边界问题仅在于双轨编号（P1-3）。
- **不一致集中在复现指南（P0-1）与 CL（P0-3）**，主稿-SI 之间未发现数字矛盾。

### 4. 词数问题（v48"按现状投"决策复核）
当前量级：Introduction 661 / Results 7,191 / Discussion 5,175，**主文合计 13,027 词**（NC 指南 ≤5,000，2.6×）；Methods 5,076（指南 ~3,000，1.7×）。v49 新增两节约 +1,900 词——**恶化了，未被摊薄**。判断：**可辩护（defensible）**——NC 明示初投对 length 灵活（"style and length will not directly influence consideration"），不会因此单独 desk-reject；但注意两点：(a) Discussion 5,175 词单独即超过整篇主文指南，返修时必然被要求压缩，建议现在就备好预案（最优切割候选：Discussion 中 "Scope of the index, parameters…" 与 "Data- and design-specific constraints" 两节约 1,500 词移 SI）；(b) **不建议在 CL 预先声明超篇幅**——NC 政策明确灵活，声明反而把编辑注意力引向篇幅。维持 v48"按现状投"决策，评级由 P1 降为 P2。

### 5. 一页 CL 排版
CL docx 实测：Arial 11pt、1" 四边距、行距 single（w:line=240 auto）、段后距 4–12pt。521 词约 36–40 行 + 段落间隙，估算占高约 7.5"，**稳在一页内（余量 ~1.5"），排版风险低**。无需删减。

### 6. 评分与判定
- **6/10**。扣分点：复现指南陈旧（−1.5）、缺 Reporting Summary（−0.5）、CL overclaim+框架（−1.0）、Abstract/Intro 未收旗舰证据（−0.5）、SI 编号/标签（−0.5）。
- 判定：**投稿前 Minor Revision**（P0×3 + P1×5 全部为 1–2 天工作量的机械修复）。修后按内容本身：编辑送审概率取决于 breadth 论证，CL 改框架后是合格的；Desk-reject risk 由当前的中等降到中低。
