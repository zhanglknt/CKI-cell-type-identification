# nc57 终审轮：R4 脑图谱复审（v0.5.3，工作树 HEAD 3d220ac）

审稿人：R4-brain。本轮基于当版文本重新独立评审；全部数字亲自核对自
`results/CKI_Manuscript_NC_fulltext.txt`（摘要实测 196 词）与
`results/CKI_Supplementary_NC_fulltext.txt`，修复意图对照 `results/audit/nc56_proof_fix_matrix.md`。
仅评审，未修改任何文件。

## 评分与 verdict

**7.5/10，verdict：accept。**
脑图谱部分的历史 6 条 Major 与上轮 4 项 Minor 中 3 项完全核销、1 项按约定沿留；
proof 轮新发现问题仅 1 处一词级措辞缺陷。声明-证据匹配维持上轮结论。

## 上轮问题核销表

| # | 上轮问题（nc55） | 裁定 | 当版证据 |
|---|---|---|---|
| 1 | 引用错配："regionally specialized astrocytes highest 19"（ref 19 原为 Tan 2020 microglia 综述） | **RESOLVED** | 参考文献表第 146 行 ref 19 已替换为 "Batiuk, M. Y. et al. Identification of region-specific astrocyte subtypes at single cell resolution. Nat. Commun. 11, 1224 (2020)"——正是建议的文献；正文第 60 行引用语境现正确；第 67 行句尾原 "hypothesis-generating 19" 的多余引用已删除。连锁核查：SI 全文 "\[19\]" 出现 0 次、无 Tan 残留引用，编号无断裂。 |
| 2 | 摘要脑句缺 "(k_n-dominated)" | **RESOLVED** | 摘要（第 8 行）："Brain analysis revealed a 3.7-fold regional gradient **(k_n-dominated)** under span- and size-matched control (donor-level 95% CI [1.9, 3.8])"；摘要实测仍 196/200 词（词额对冲成立）。 |
| 3 | Supp Fig. 14 图注 "validation value" 残留 | **RESOLVED** | 第 214 行："the **sanity-check value** lies in ω tracking the functional contrast far above its own neutral baseline"，与 Note 16 更名及第 39 行口径一致。 |
| 4 | supercluster 粒度与 microglia/Bergmann 文献张力协调 | **UNRESOLVED（按约定沿留，不阻断）** | 第 57/60 行维持原文；该项两轮前已约定为可选，编辑未追问则无需处理。 |

## proof 轮（nc56）编辑的新问题排查

**Major：无。**

**minor：**
1. 【proof 引入】第 38 行 "(14.1% below 30 nuclei to 48.0% above 500; **small-stratum** raw JS 28.6% to 72.5%)"：
   修复矩阵 M8 的意图是消除 28.6% 双现歧义（L37 ω T1 FPR 28.6% vs L38 raw JS 小层 28.6%），
   数字本身正确（raw JS 小层 28.6% → 大层 72.5%，与 v51 起口径一致），但 "small-stratum"
   前缀修饰整个区间，读起来像 28.6→72.5% 全是小层值，而 72.5% 是 >500 大层端点——
   修了一个歧义、造了一个歧义。建议 proof 阶段改为 "raw JS 28.6% to 72.5% over the same strata"
   或 "raw JS 28.6% (small stratum) to 72.5%"。一词级，不阻断。
2. 【proof 改善·确认记录】第 63 行 "no candidate survives **global** FDR correction" 与第 65 行
   "**within-family** minimum q = 0.042"——两处家族层级限定词系我 nc53 轮可选建议的落实，
   全局/分层两家族表述现完全无歧义，确认改善。
3. 【proof 改善·确认记录】第 37 行 "four-tier drift ladder" 与 Fig. 3a 图注 "four-tier"
   （n-matched null + T1/T2/T3）协调一致；Fig. 3a 各 tier pair 计数 (2,161)/(1,089)/(1,656)
   与正文第 37 行一致；Fig. 3c "(T1: 28.6% versus 37.6–45.2% for the others)" 与第 37 行一致。
   指针无断裂。

## 数字链复核（当版亲自核对，与 ground truth 一致）

- 梯度链（第 56 行）：6.10（uncorrected upper bound）/ span-matched 3.68 [1.67, 3.97] /
  combined 3.66 [1.92, 3.78]，LODO > 1 / equal-n 1.74 [0.80, 2.34] 降级 / 质量代理 6.33–6.45
  ——与 nc52 审计文档（3.660 [3.598,3.705]、donor [1.918,3.779]、[1.670,3.973]、[0.804,2.336]、
  6.3276/6.4503）逐项一致。
- 筛查（第 63–65 行）：39 (0.12%) Strong / 1,171 Moderate / 5,381 Weak of 31,764；
  期望 148.3、P(≥39)=1.0；全局 q_min=0.520（此前轮次已实算 brain_bs_null_results.csv
  q_fdr min=0.5202）；Bergmann 家族 m=21 within-family q=0.042；microglia fold 0.31 P=0.990。
- Fig. 6 图注（第 199 行）与正文口径一致，无回归。
- k_n 主导表述：摘要 (k_n-dominated)、第 60 行 "it is k_n-dominated and does not by itself
  establish functional specialization"、Fig. 6b 图注 "dominated by the k_n denominator
  (3.21-fold k_n versus 2.03-fold k_f)" 三处一致。
- 非本域但经眼：GTEx 句（第 50 行）tumor k_n 2.0–2.8-fold（nc54 微调），摘要对应句
  "consistent with tumor-specific elevation" 软化匹配；LIHC NN/TT 1.11、3,535 ex-CC 口径一致。

## 结论

脑图谱部分在 v0.5.3 中达到了可投稿状态：三口径梯度呈现、设计匹配零模型链、阴性筛查的
诚实处理、PMI/质量代理措辞均维持此前批准水平；上轮 3 项 proof 承诺全部兑现且引用替换
无连锁断裂。唯一新发现问题为第 38 行一处一词级措辞缺陷（minor，不阻断）。
**7.5/10，accept。**
