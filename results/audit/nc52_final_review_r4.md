# R4 脑图谱/神经科学终审（v52 final review round, commit 7133b43）

审稿人：R4-brain。审查对象：`results/CKI_Manuscript_NC.docx`（fulltext txt 为 docx 生成后 6 秒再生，与当版同步）、
`results/CKI_Supplementary_NC.docx`、`results/CKI_Supplementary_Tables_NC.xlsx`（未逐格核，抽查正文引用口径）。
Ground truth 复核：`results/audit/nc52_impl_brain.md`、`results/nc52_brain_gradient_donor_bootstrap.json`（经审计文档转述）、
`results/nc52_brain_combined_equaln_spanmatch.csv`、`results/brain_setlevel_tests.txt`、`results/axis_rule_matched_null.json`。

## 一、上轮三项硬条件逐项核对

### (a) 摘要/正文主口径切换为组合对照 + 1.74 降级 —— 已落实 ✓
- 摘要（fulltext 第 8 行）："Brain analysis revealed a **3.7-fold regional gradient under combined span- and
  size-matched control (donor-level 95% CI [1.9, 3.8])**"——主口径已切换，1.74 不再出现于摘要。
- 引言 roadmap（第 14 行）：同口径 "3.7-fold span- and size-matched, donor-level 95% CI [1.9, 3.8]" ✓。
- Results（第 56 行）：6.10 标注 "an uncorrected upper bound"；span-matched 3.68 [1.67, 3.97]；
  combined 3.66（donor [1.92, 3.78]；LODO 全 >1）；**1.74 明确 "not donor-robust (95% CI [0.80, 2.34];
  four donors) and is relegated to a sensitivity analysis"** ✓。
- Fig. 6b 图注（第 199 行）：同步改写，combined 3.66 为主、1.74 注明不稳健 ✓。
- SI Note 10（第 197–198 行）：donor cluster bootstrap 细节完整（median 1.56 [0.80, 2.34]；LODO [0.93, 1.76]；
  组合对照 observed 3.66 [3.60, 3.71]、donor median 3.28 [1.92, 3.78]、LODO 2.31–3.68）✓。
- 与 ground truth 对账：审计文档 3.660 [3.598, 3.705] / donor [1.918, 3.779]、equal-n [0.804, 2.336]、
  span-matched ratio-of-means [1.670, 3.973]——稿面四舍五入口径全部一致 ✓。

### (b) 39→3 估计器敏感性入正文 —— 已落实 ✓
- Results 第 67 行："only **3 of 39** Strong candidates survive a switch to a global-k_n estimator—so all
  entries are strictly hypothesis-generating"。
- Discussion 第 76 行、Fig. 6c 图注（第 199 行）同步 ✓。
- 与 ground truth 对账：C3 分析 global-k_n 重算 Strong=107、仅 3/39 保留、残差秩相关 0.337 ✓。

### (c) 解剖学主题降级 —— 已落实（可接受水平）✓
- 第 67 行主题句改为 "The catalogue shows spatial patterning **without establishing anatomical themes**"，
  段尾以估计器敏感性与 "strictly hypothesis-generating" 收束。具体的 visual-relay/orbitofrontal 与
  thalamo-temporal 描述仍在，但已置于双重免责声明之下，符合"降级为描述性观察"的要求。
- SI Note 13 新增 rule-matched 零模型（notebooks/82）：hit 计数不极端（6 vs null 6.58, P=0.48；
  9 vs 8.49, P=0.38），per-candidate hit-rate P 值明确标注 "conditional on the selected survivor set
  and are not valid post-selection P values"，且声明结论仅限 "axis concentration of the surviving
  candidates, not an axis excess of candidates"——统计自律到位 ✓。

## 二、Major 1（PMI/RNA 质量混杂）关闭确认

- Limitations (iii)（第 80 行）措辞与双方约定逐字一致："detection-depth, UMI, and mitochondrial-fraction
  proxies do not drive the regional gradient … but these proxies cannot capture PMI-related RNA-degradation
  deformation, which remains unexcluded" ✓。
- SI Note 10 "RNA-quality proxies (v52)" 段完整报告 mito 结果：mito 解释 k_n/k_f（R² 0.225→0.271、
  0.442→0.504）但对 ω 几乎无增量（0.300→0.308）；T3 ω 系数 0.257→0.202（−21%）保留；
  区域对级调整后梯度 6.33→6.45 ✓。技术分量在比值中抵消的证据链完整。

## 三、任务书口径与稿件的一处不一致（流程提示，非稿件错误）

任务书权威口径写 "残差分析 **30 Strong / 16 FDR 显著** / m=31,764"。当前 MS（第 63/65/76 行）、
SI（3.3 节、Note 13）、全部 ground truth 文件（brain_bs_null_results、brain_setlevel_tests、审计文档）
一致为 **39 Strong / 无一 FDR 存活（minimum q = 0.520）**。fulltext txt 在 docx 之后 6 秒再生，
排除版本错位。结论：任务书数字有误（或来自其它分析的记忆混淆），稿件与地面真值自洽，无需改动；
请 team-lead 知悉并更正内部口径。

## 四、遗留 Minor（不阻断）

1. 摘要脑句未带 k_n 主导警示，而 TCGA 句带（"driven by a 1.3–3.3-fold elevated housekeeping baseline"）。
   建议摘要脑句加 "(k_n-dominated)" 或在引言 roadmap 句补一词；不加亦不构成误导（正文第 56/58 行
   与 Fig. 6b 图注均已披露），属风格一致性建议。
2. 旧 Major 5（supercluster 粒度与文献张力：microglia 区域异质性文献 vs "at or below null expectation"；
   Bergmann aldolase C 分带 vs 最低 ω）在 Discussion 仍未明确协调——上轮已约定降级为可选项，
   维持该约定；若编辑追问，Note 13/正文第 60 行的一句话即可覆盖。
3. SI 3.3 节新增的全局 lower-tail 富集（P=0.011；Bonferroni 0.022）与 Note 13 的构造性警告
   （tier 与 P 值同源）之间存在轻微张力：3.3 节的 "significant excess" 读法比 Note 13 的自审更强。
   建议在 3.3 节句尾加 "（见 Note 13 的构造性警告）" 指针。非阻断。

## 五、评分与定档

- soundness: **8/10**（混杂校正链——span×size 组合对照、donor cluster bootstrap、LODO、mito 协变量、
  rule-matched 零模型——已达到该数据（4 供体死后图谱）可支持的最严标准；表述与证据严格匹配）
- novelty: **6/10**（Ka/Ks 启发式重组定位未变；方法增量在零模型设计与自校准纪律）
- significance: **6/10**（脑图谱部分现有一个 donor 层稳健的 3.7 倍梯度 + 一个诚实的阴性筛查 +
  mito 抵消证据；生物学增量仍有限但无过度声明）
- presentation: **8/10**（三项硬条件逐字落实，免责声明与证据层级匹配；仅剩摘要对称性等风格项）
- **总评 overall: 7.0/10，推荐：minor revision（实际上仅剩文字级润色，可视同 accept 待定）**

条件清单（全部可选/文字级，无新增分析要求）：
1. 【可选】摘要脑句补 k_n 主导一词以与 TCGA 句对称；
2. 【可选】SI 3.3 节全局富集句尾加 Note 13 构造性警告指针；
3. 【流程】更正任务书 "30 Strong / 16 FDR" 为 39 Strong / 无 FDR 存活（q_min=0.520），避免写入
   rebuttal 或 cover letter 时出错。

R4 对脑图谱部分的审查到此结束：上轮 6 条 Major 全部关闭（1/2/3/6 由新分析+稿面落实关闭，
4 由降级措辞关闭，5 按约定转为可选 minor）。
