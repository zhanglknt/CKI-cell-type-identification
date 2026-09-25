# nc55 盲审：R4 脑图谱/神经科学独立重审（v0.5.2 终稿 @5a5ae6d）

审稿人：R4-brain。本轮为复审轮，基于当前文本独立重评；所有数字/措辞均引自当版
`results/CKI_Manuscript_NC_fulltext.txt` 与 `results/CKI_Supplementary_NC_fulltext.txt`，
关键统计量经 `results/brain_bs_null_results.csv` 等输出文件 ground truth 复核。
已核实当版 commit = 5a5ae6d，摘要实测 196 词。

## 总评分与 verdict

**7.5/10，verdict：accept（proof 阶段完成 3 处一词级文字即可）。**

## 强项

1. **三口径梯度呈现是图谱论文的范本**（第 56 行）："a full-data endpoint gradient of 6.10-fold,
   an uncorrected upper bound"；主口径 "a combined span- and size-matched control yields 3.66
   (donor-level bootstrap [1.92, 3.78]; leave-one-donor-out always > 1)"；
   "The size-only equal-n control (1.74) is not donor-robust (95% CI [0.80, 2.34]; four donors)
   and is relegated to a sensitivity analysis"。6.10/1.74/3.68 三数字的角色（上界/敏感性/对照）
   层次分明，无误导空间。与审计 ground truth（3.660 [3.598,3.705]、donor [1.918,3.779]、
   equal-n [0.804,2.336]、span [1.670,3.973]）逐项一致。
2. **设计匹配推断链完整**：library block-shuffle 零模型 + pseudo-region 阴性对照（127,756 伪对，
   cross-origin 近名义、same-origin 37.6% 示效能）+ donor-stratified null（含 ependymal 逆向案例
   透明披露）+ donor cluster bootstrap（Methods 第 119 行已入正规统计段）。4 供体图谱下这是
   可做到的最严标准。
3. **RNA 质量代理与 PMI 措辞精确**（第 56、80(iii) 行）：(class, region) 层调整后 6.33–6.45；
   Limitations 逐字保留 "these proxies cannot capture PMI-related RNA-degradation deformation,
   which remains unexcluded"。mito 在 ω 比值中抵消（R² 0.300→0.308，SI Note 10）是支持比值
   设计的实质性证据。
4. **阴性筛查的诚实处理**（第 63–67、76 行）：反富集（39 vs 期望 148.3，P=1.0）、
   q_min=0.520 明确标注为置换分辨率陈述（Methods 第 118 行：q<0.05 需 B≈6×10⁵）、
   39→3 估计器敏感性入正文、解剖学叙事以 "shows spatial patterning without establishing
   anatomical themes" 收口。SI Note 13 的 rule-matched null 声明 hit-rate P 值
   "not valid post-selection P values"——统计自律罕见。
5. **区域聚类感知推断**（第 119 行）：region-clustered block bootstrap（B=2,000）为景观量的
   首选不确定度（gradient 6.10 [5.55, 9.63]；Strong count 39 [12, 74]），两阶段 region-clustered
   传播校准分母不确定度（B=5,000），聚类结构处理规范。

## Major 清单

**无。** 此前各轮的 6 条 Major（PMI/RNA 混杂、equal-n 校正链、per-pair ω 的 k_n 噪声主导、
解剖学叙事越界、supercluster 粒度、4 供体结构）经逐轮修复与本轮复核全部关闭，
当版文本未发现可构成 Major 的新问题。

## Minor 清单

1. **【本轮新发现·引用错配】第 60 行 "regionally specialized astrocytes highest 19"**：
   ref 19 为 Tan, Yuan & Tian 2020《Microglial regional heterogeneity and its role in the brain》
   （参考文献表第 146 行）——一篇 microglia 综述，不能支撑星形胶质区域特化的论断。
   同样地，第 67 行 "strictly hypothesis-generating 19" 以该 microglia 综述支撑全目录的
   follow-up 定位，相关性弱。建议：为星形胶质区域特化补一条正确文献（如 Batiuk et al. 2020、
   Bayraktar et al. 2020 或 Siletti 本身的星形胶质区域结果），第 67 行引 19 改为引 microglia
   相关句内或删除。proof 级，不影响结论。
2. **摘要脑句仍缺 k_n 限定**（第 8 行）："Brain analysis revealed a 3.7-fold regional gradient
   under span- and size-matched control (donor-level 95% CI [1.9, 3.8])"——TCGA 句带
   "driven by a 1.3–3.3-fold elevated housekeeping baseline" 警示而脑句不带，披露标准不对称。
   上轮约定沿留 proof；当版摘要实测 196/200 词，有 4 词余量，插入 "(k_n-dominated)" 1 词
   即可，proof 阶段无执行障碍。
3. **Supp Fig. 14 图注残留 "validation value"**（第 214 行）：与 Note 16 更名
   "Human-Brain Sanity Check"（SI 第 220 行）及正文第 39 行 "A sanity check on unused data"
   的降级口径不一致。改 "the sanity-check value lies in…"，一词级。
4. **【既有遗留·按约定可选】supercluster 粒度与文献张力**：microglia "sit at or below the
   null expectation"（第 57 行）与 microglia 区域异质性文献（作者自引 ref 19–22）、Bergmann
   最低 ω 端点与 aldolase C 分带文献（ref 26）之间的张力未在 Discussion 协调。前两轮已约定
   为可选项，维持不阻断；若编辑追问，第 60 行加一句 supercluster 池化稀释亚型级信号即可。

## 上轮关注复核意见（逐项，引当版原句）

| 上轮关注 | 当版状态 | 证据 |
|---|---|---|
| 组合对照为主口径、1.74 降级 | 保持 | 摘要第 8 行、Results 第 56 行、Fig. 6b 图注（第 199 行）、SI Note 10 四处一致 |
| 39→3 估计器敏感性入正文 | 保持 | 第 67 行 "only 3 of 39 Strong candidates survive a switch to a global-k_n estimator"；第 76 行、Fig. 6c 图注同步 |
| 解剖学主题降级 | 保持 | 第 67 行主题句 "without establishing anatomical themes"；SI Note 13 rule-matched null 免责声明在 |
| 两家族层级（全局 q_min=0.520 vs Bergmann m=21 q=0.042） | 清晰 | 第 63 行 vs 第 65 行 "sub-nominal stratified family"；ground truth 实算 q_fdr min=0.5202 |
| PMI 措辞 | 保持 | 第 80(iii) 行逐字一致 |
| Supp Fig. 14 图注 | 已新增 | 第 214 行，数字全（91,838；21.83±7.20 vs 1.30±0.36；P=5.5×10⁻¹⁴；AUC=1.00；k_n 0.89） |
| sanity check 句非独立性披露 | 已改善 | 第 39 行 "descriptive—pairs overlap across four donors" |
| 数字链防回归 | 无回归 | 6.10/3.68 [1.67,3.97]/3.66 [1.92,3.78]/1.74 [0.80,2.34]/6.33–6.45 与审计文档逐项一致 |

## 具体修改建议（全部 proof 级，不阻断）

1. 第 60 行星形胶质区域特化更换正确引用（Minor 1）；
2. 摘要脑句插入 "(k_n-dominated)"（196→197/200 词）（Minor 2）；
3. Supp Fig. 14 图注 "validation value"→"sanity-check value"（Minor 3）；
4. 【可选】第 60 行或 Discussion 加一句 supercluster 池化对亚型级区域信号的稀释说明，
   一次性覆盖 microglia/Bergmann 与文献的表面张力（Minor 4）。

**一句话总评**：脑图谱部分的三口径梯度呈现、设计匹配零模型与阴性结果处理已达到该方法学论文
可要求的最高披露标准，6 条历史 Major 全部关闭，本轮新发现问题仅为 1 处引用错配与若干 proof 级
文字残留，推荐 accept。
