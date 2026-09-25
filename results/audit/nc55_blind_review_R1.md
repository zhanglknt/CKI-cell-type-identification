# nc55 盲审报告（R1 统计方法学）— v0.5.2 @5a5ae6d

审稿人：R1-stats（排列检验、校准、自助法区间、FDR、零模型设计、聚类感知推断）
评审依据：仅当前文本 `results/CKI_Manuscript_NC_fulltext.txt`（正文+图注全文通读）与 `results/CKI_Supplementary_NC_fulltext.txt`（修复点定点精读）；关键数字对照输出文件与 nc54 交叉验证报告（40b8f22，ALL PASS）。本轮独立打分，不沿用上轮结论。

## 总评分

- Soundness: **8.5/10**
- Novelty: 6/10
- Significance: 6.5/10
- Presentation: 9/10
- **Overall: 8.0/10**

## Verdict

**Accept**（Minor 清单为可选完善项，不构成接收障碍）

## 强项

1. **校准区间的层级化处理是教科书式的**：300 个 split-half 值嵌套于 6 个群体，稿面明确声明 t 区间 [7.37, 8.02] 为伪重复、予以废止，采用两阶段群体重抽样 bootstrap（B=5,000）得 [6.38, 9.82]，并给出 LOPO 敏感性 6.75–8.08（§24、§119、SI 3.10）。伪重复问题的自我披露在方法学稿件中罕见。
2. **聚类感知推断贯穿全文且前后一致**：Tabula Sapiens 相关用 entry-clustered bootstrap（SI：ω vs raw JS −0.40 [−0.54, −0.23]，明确"replace the independence-assuming P-values of earlier versions"）；脑景观量用 region-clustered block bootstrap（6.10 [5.55, 9.63]）；梯度用 donor cluster bootstrap（3.66 [1.92, 3.78]，4 donor），并诚实声明 equal-n 1.74 [0.80, 2.34] 不具 donor 稳健性、降级为敏感性分析（§56）。
3. **FDR 分辨率的诚实声明**：m=31,764 的 BH 阈值 ~1.6×10⁻⁶ 比 B=1,000 最小可分辨 P 低 ~600 倍，"q < 0.05 is unattainable without ~635 floor P-values or B ≈ 6 × 10⁵ permutations... reflects permutation resolution rather than evidence against candidates"（§99/§118）。同时用设计匹配零模型给出期望候选数 148.3 vs 观测 39（P(null count ≥ 39)=1.0）的反富集证据，把"无 FDR 显著"转化为有信息量的上界（§63）。
4. **设计匹配零模型 + 伪区域阴性对照**：block-shuffle 保留 library 结构；127,756 伪区域对的尾率（cross-origin 5.79%/6.87% vs 名义 5%；same-origin 37.6%）同时证明零模型校准与检验功效（Supp. Fig. 10）。SI 还披露早期 per-pair shuffle 实现"produced anti-conservative P-values (36.3% at floor)... superseded by the block-shuffle null"。
5. **TCGA 推断链条完整**：per-tumor 均值的组间检验用全肿瘤标签置换复核（B=10,000：KRAS P≤0.001，EGFR P≥0.28）；NN/TT 比值用 sample-level cluster bootstrap；softmax→linear 映射重做全部分析，仅 LIHC 映射敏感（1.11 [0.94, 1.30] vs 1.29 [1.09, 1.53]）并如实披露；固定 panel 的 per-cancer 置换检验声明 anti-conservative 且仅备查（§90、§80(iii)）。
6. **AUC 区间方法已补齐**：SI Note 1 新增 "AUC interval methods (v52)" 段——DeLong [0.770, 0.838] + module-seed cluster bootstrap [0.771, 0.836]，二者一致说明 DeLong 口径对聚类模拟设计稳健。
7. **ω–k_f 数学必然性检验口径正确**：k_n 置换 floor 明确为 full-inventory 5,151 对（"the 102-entry inventory before the 99-entry filter that yields the 4,851 analyzed pairs"），floor 0.524 [0.506, 0.541] vs 观测 0.089（§70、SI）。

## Major 清单

**无。**

## Minor 清单

1. **Fig. 4c/d 图注的 "adjusted P = 0.009 and 0.029" 未标明口径**。这两个是 OLS 模型 P 值；per-tumor 均值由重叠 pair 集合构成（§112，median 4–11 pairs/tumor），组内相关使模型 P 值偏激进。正文 §48 已正确地把结论锚在全肿瘤置换（P≤0.001）上，但图注未注明"模型 P 值，置换确认见 Section 3.13"。建议图注补一句来源说明。
2. **§48 "adjusted log-ω ratio 1.19, 95% CI [1.12, 1.26]" 的区间方法未声明**。若为标准 OLS 区间，同样在 pair-overlap 下偏窄；推断既已主要靠置换，建议注明该 CI 为 model-based，或以 tumor-level bootstrap 给出对应区间。
3. **Fig. 1c 展示的仍是被废止的伪重复 bootstrap 分布**（"B = 10,000 resamples of the 300 ... values"）。图注虽给出两阶段 CI [6.38, 9.82]，但未说明图示分布自身的散布是 anti-conservative、其区间已被 §24 取代。建议图注加一句提示，避免读者从图读出窄区间。
4. **小 n 相关家族的推断口径不统一**：§53 "r = 0.23, 95% CI [−0.08, 0.38], n = 17"（CI 方法未注明，且 17 个类型均值来自重叠 pair 集合）；§58/§59 的 n=10 类级 ρ（−0.73、0.09、−0.648 P=0.043）与 §74 Augur ρ=0.442、§76 跨物种 r=−0.17 散布各处，缺统一的族处理。§80(v) 已披露"without joint cross-family correction"，建议把这些 n=10/17 相关统一声明为描述性。
5. **§30 分解 P 值的描述性限定范围含糊**。"descriptive—pairs share cell-type pseudobulks" 紧跟 ω 的 MWU P=5.6×10⁻¹⁸，同句后续的 k_f P=0.60、k_n P=3.0×10⁻¹⁶ 是否被该限定覆盖不够明确；建议把限定词移到句末或重复一次。
6. **模拟 FPR 未给区间**：检测阈值由 200 个 baseline replicate 的 95 分位校准，55%/58%/0% 这类 FPR 在 n≈200 下二项 SE≈3.5pp（§32/§104）。真实数据 Fig. 3c 给了 Wilson CI，模拟侧没有；建议在 SI Note 1 补 FPR 的 Wilson/CP 区间。
7. **§57 BH 淘汰项未点名**："4 of 10 classes... 3 of 10 surviving Benjamini-Hochberg correction"，正文未说明哪一个类（OPCs/committed OPCs/fibroblasts 之一）未过关；一行即可补全。

## nc53/nc54 处置逐条复核

| 处置项 | 裁定 | 当前文本证据 |
|---|---|---|
| nc54 肝句方向修复 | **成立** | SI Note 8 区域现作："in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, **with a heavier adjacent upper tail**"。P=3.8e-5 归属 GG<NN 方向（即 adjacent/NN 随机更大、上尾更重），与我此前从 `nc52_gtex_pairs.csv` 独立重算（alternative='less' P=3.814e-05；GG、NN 中位数 1.98e-3/1.92e-3）完全一致；错误的 "healthy marginally above adjacent" 表述已删除。 |
| nc54 GTEx pair-independence 限定 | **成立** | SI："**Pair-level P values in this GTEx comparison treat pairs as independent and are descriptive only.**"位置在跨队列句之后，管辖范围覆盖该节全部 pair-level P（含 TT≫NN P≤3.2×10⁻⁸⁴、跨队列 P≤1.4×10⁻²⁶）。充分性可接受：限定为描述性后，机制结论落在 within-cohort 排序与 fold-change 上。 |
| nc54 模拟 38% 标注 | **成立** | §70/Discussion："under fourfold cell-count imbalance **(simulation)** k_f misreports 38% of neutral pairs, ω none"。模拟出处已显式标出。 |
| nc53 k_n-permutation floor 改 full-inventory 口径 | **成立** | §70："permuting k_n across the **5,151 full-inventory human pairs** predicts Spearman 0.524... observed value is 0.089"；SI 同句给出 "the 102-entry inventory before the 99-entry filter that yields the 4,851 analyzed pairs"，floor 0.524 [0.506, 0.541] 与 `nc52_stats_omega_kf_math_floor.csv` 一致。 |
| nc53 AUC 区间方法（SI Note 1 "AUC interval methods (v52)" 段） | **成立** | 原文见强项 6；DeLong 与 module-seed cluster bootstrap 双口径并列，数字与 `nc52_stats_auc_ci_methods.csv` 一致。 |
| nc53 6.33–6.45 归因层级 | **成立** | §56："RNA-quality proxies do not drive the gradient: (class, region)-level adjustment ... leaves it at 6.33–6.45"，主句结论锚在受控估计 3.66 [1.92, 3.78]，6.10 明示为 "an uncorrected upper bound"，层级清晰。 |
| v0.5.2 摘要减重 196/200 | **成立（格式项）** | 摘要数字与正文一致（7.70 [6.38, 9.82]；1.11–2.46 四/五除外；[1.9, 3.8]；38% 未入摘要）。 |
| v0.5.2 Zenodo version DOI 10.5281/zenodo.22949350 | **成立（格式项）** | §126 Code availability 同时给出 concept DOI 与 v0.5.2 version DOI。 |

## 具体修改建议（均为可选）

1. Fig. 4c/d 图注："adjusted P" 后补 "(OLS model P-values; whole-tumor permutation confirmation in Section 3.13)"。
2. §48 为 1.19 [1.12, 1.26] 标注区间方法；若 OLS，加 "model-based"。
3. Fig. 1c 图注注明图示 300 值 bootstrap 散布为伪重复、报告区间以两阶段 [6.38, 9.82] 为准。
4. §53 注明 r 的 CI 方法（如 Fisher z），并与 §58/§59/§74/§76 的小 n 相关统一加 "descriptive"。
5. §30 将 "descriptive" 限定移到句末覆盖 k_f/k_n 两个分解 P 值。
6. SI Note 1 为模拟 FPR（0%、55%、58% 等）补 Wilson 95% CI。
7. §57 点名 BH 未过关的第 4 个类。

## 一句话总评

当前版本的统计推断链条（校准两阶段 bootstrap、entry/region/donor 三级聚类感知区间、全肿瘤置换、设计匹配零模型+FDR 分辨率声明）已无明显漏洞，nc53/nc54 全部处置经原文逐句复核成立，达到接收标准。
