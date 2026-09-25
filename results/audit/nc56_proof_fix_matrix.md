# nc56 proof 沿留清单修复矩阵 — v0.5.2 @c380e19（2026-09-25）

范围：nc53_confirm_round_summary 第四节 6 类 + nc55_review_summary 类 B 12 项（用户指令「3全部解决」）。
来源状态：R2-①②④⑦、R1-m5/m6、R5-③⑥、R4、R6 外观项、nc53-R5 五条 = 原文已落盘（nc55_blind_review_R*.md、nc53_confirm_review_r*.md、nc52_final_review_r*.md）并逐条回查；R1-②–⑥、R2-M3、R3-①②⑤、R6-N3/N4 原始全文未落盘（v51r2 时代 agent 消息，nc51r2_review_panel 自述）→ 以 nc55 汇总描述为权威转述 + 当版文本 ground-truth adjudicate。
行号 = 当版 fulltext 行（构建产物），实际编辑一律在生成器。

## 一、修改项（MS generate_manuscript_nc.py）

### 摘要（196/200 → 净 0 → 196/200）
| # | 当版原文（L8） | 改为 | 词额 | 来源 |
|---|---|---|---|---|
| A1 | Inspired by the Ka/Ks ratio | Inspired by Ka/Ks | −2 | 对冲 |
| A2 | (false-positive rate 0.00 versus | (housekeeping-anchored false-positive rate 0.00 versus | +1 | R2-① |
| A3 | GTEx references argue against a field-effect reading. | GTEx references in lung, liver, and breast are consistent with tumor-specific elevation. | +5 | R2-B1 + R3-m3 + nc52-C7 |
| A4 | CI excluding 1 in four of five cancers | four of five CIs excluding 1 | −2 | 对冲 |
| A5 | components both survived | components survived | −1 | 对冲 |
| A6 | was explained by stromal/immune admixture | reflected stromal/immune admixture | −2 | 对冲 |
| A7 | 3.7-fold regional gradient under span- | 3.7-fold regional gradient (k_n-dominated) under span- | +1 | R4（nc53_confirm_r4 原文确证） |

### MAIN（≈4,998/5,000 → 净 −2 → ≈4,996）
| # | 行 | 当版原文 | 改为 | 词额 | 来源 |
|---|---|---|---|---|---|
| M1 | L14 | 删末句 "Ground-truth simulations complement all five analyses throughout." | （删除） | −7 | 对冲+准确性（模拟并未 complement 全部五个分析） |
| M2 | L26 | we introduce ω_cal = ω_obs / 7.70. | we introduce ω_cal = ω_obs / 7.70 (one-significant-digit resolution). | +2 | R3-②/R1 精度前置 |
| M3 | L28 | 4,851 pairs across six organs) | 4,851 pairs across six organs (largest-donor pseudobulks; Methods)) | +3 | R2-⑦（Methods L97 已有 largest-donor 句，此补 Results 指针） |
| M4 | L30 | (Supplementary Note 9). | (also descriptive; Supplementary Note 9). | +2 | R1-m5（限定重复覆盖 k_f/k_n 分解 P 值） |
| M5 | L32 | ω in none; | ω in none (Clopper–Pearson intervals in Supplementary Note 1); | +6 | R1-m6（区间本体已在 SI Note 1，补正文可见性指针） |
| M6 | L37 | three-tier drift ladder | four-tier drift ladder | 0 | R5-③/R3-①（对齐 Fig 3a 图注 four-tier 与 nc49_brain_ladder 文档 T0 null+T1/T2/T3） |
| M7 | L37 | ; Section 3.12) | ) | −2 | 去重（L38 同节已有 "Section 3.12 of the Supplementary Information" 全式） |
| M8 | L38 | ; raw JS 28.6% to 72.5%) | ; small-stratum raw JS 28.6% to 72.5%) | +1 | R5-⑥（28.6% 双现消歧：L37 ω T1 28.6% vs L38 raw JS 小层 28.6%） |
| M9 | L45 | 删第二个 "(Supplementary Note 7)" | （同段保留首个） | −3 | 去重 |
| M10 | L56 | 删第二个 "(Supplementary Note 10)" | （同段保留首个） | −3 | 去重 |
| M11 | L63 | no candidate survives FDR correction | no candidate survives global FDR correction | +1 | R2-④ |
| M12 | L65 | minimum q = 0.042 | within-family minimum q = 0.042 | +1 | R2-④ |
| M13 | L69 | so ω_cal = ω / 7.70 is the operational scale, with about one significant digit of resolution given the baseline interval (Results; Supplementary Note 3). | so ω_cal = ω / 7.70 is an indicative, dataset-relative scale (Results; Supplementary Note 3). | −10 | 精度前置后降级；兼 R5-⑤ 选项 B |
| M14 | L72 | and caveats are in Section 1.4. | and caveats are in Section 1.4 of the Supplementary Information. | +4 | R5-③ 术语包 |
| M15 | L75 | supporting tumor-specific housekeeping elevation over a field effect | consistent with tumor-specific housekeeping elevation over a field effect within cohorts | +3 | R2-M1 残余（最高优先） |
| M16 | L75 | attenuates the pooled k_n coefficient by only −0.9%, but this masks heterogeneity: attenuation is strongest in LIHC | shifts the pooled k_n coefficient by only −0.9%, but this masks heterogeneity: the shift is largest in LIHC | +1 | R5-⑥ |
| M17 | L78 | (14; Results) | (ref. 14; Results) | +1 | R5-③ |
| M18 | L79 | (i) at least 100–200 cells per group for stable point estimates—noting that permutation-test power already erodes inside this window (Section 3.11 of the Supplementary Information)—below which | (i) at least ~100 cells per group (operating window ~50–200; power already erodes inside this window; Section 3.11 of the Supplementary Information), below which | −2 | R2-②（建议值 ~100+ 与 L80(iv) 操作窗 ~50–200 协调） |

### Methods / 图注 / 声明区（免 MAIN 词额）
| # | 行 | 改法 | 来源 |
|---|---|---|---|
| X1 | L108 Methods | "in three tiers—" → "in three tiers (the per-pair null constituting the fourth ladder tier)—" | R5-③ four-tier 口径说明 |
| X2 | L108 Methods | "per-class values in Section 3.12)" → "...Section 3.12 of the Supplementary Information)" | R5-③ |
| X3 | Fig 2(b) L195 | "while k_n remains relatively constrained." → "while k_n shows far smaller variation across categories." | R5-③ |
| X4 | Fig 3(a) L196 | T1/T2/T3 描述各补对数 "(2,161 pairs)"/"(1,089 pairs)"/"(1,656 pairs)" | R6-N3（汇总转述） |
| X5 | Fig 3(c) L196 | "ω misreports least among the continuous divergence metrics at both tiers" 后补 "(T1: 28.6% versus 37.6–45.2% for the others)" | R6-N4（汇总转述） |
| X6 | Fig 5(d) L198 | "Top 5 conservative cell-type pairs" → "Top 5 conserved cell-type pairs" | R5-③ |
| X7 | Fig 14 L214 | "the validation value lies" → "the sanity-check value lies" | R4 |
| X8 | L126 声明区 | "runs on Linux, macOS, and Windows." → "runs on Linux, macOS, and Windows (continuous integration covers Linux; macOS and Windows are verified on local workstations)." | R6-⑤（CI ubuntu-only 事实对齐） |

## 二、修改项（SI notebooks/68_gen_supplementary_nc.py，全免词额）
| # | 行 | 改法 | 来源 |
|---|---|---|---|
| S1 | Note 8 L189 | 在 "Pair-level P values … descriptive only." 与 "mechanistic claims therefore rest on within-cohort orderings only." 之间插："The GTEx–adjacent cross-cohort shift (GA/GG ≈ 1.8–2.3×) bounds the resolution of the healthy–adjacent comparison; the healthy ≈ adjacent similarity should be read within that tolerance (tentative, GTEx cross-cohort discrepancy unresolved)." | R2-B1（量化不确定度 + tentative 声明） |
| S2 | Note 3 L167 | "in **all key results**" → "in **the calibration-relevant results**" | R5-⑤ 选项 A（与 M13 双保险） |
| S3 | Note 14 L215 | "not distributed for Python 3.13" → "not distributed for Python 3.14" | R2-⑤（对齐 MS L116 钉死环境 3.14.4） |
| S4 | L135 | "(Reproducibility Guide, Section 5.10c)" → "(Reproducibility Guide, Section 5.13)" | R6 指针 |

## 三、仓库面
| # | 文件 | 改法 | 来源 |
|---|---|---|---|
| R1 | pyproject.toml | description "Cell-type Identity Index" → "Cell-type Ka/Ks-inspired Index: a framework for quantifying baseline-normalized transcriptomic remodeling"（对齐正文术语；仓库名不改）✅ 已改 | R6-④ |
| R2 | CL 生成器 | ~~"28.6% versus 35.7–45.2%"~~ **已不存在**（当版 CL 全文 grep 无 28.6/35.7/45.2；该句在早前压缩轮已删）→ 不改 | nc53-R5 #5 |
| R3 | CL 生成器 | ~~"principled separation"~~ **已不存在**（当版 CL 无 "separation"，L55 已是 "decomposes Jensen–Shannon divergence"）→ 不改 | nc53-R5 #5 |
| R4 | Guide JS 5.6f | **已覆盖**（L514 已是 "deterministic division by 6.67, a legacy constant superseded by 7.70 in v44"；L321/L448 同有 superseded 注）→ 不改 | R6-⑥ |

## 四、维持不改裁定（adjudicated）
| 项 | 裁定 | 理由 |
|---|---|---|
| R3-⑤ 摘要 1.11–2.46 升序 vs Results 降序 | 维持 | 摘要报区间（升序惯例）；Results/Fig 4a 按效应降序，图注明示 ranked by effect size |
| R2-M3 Bergmann 6.10 [3.16,11.69]↔3.66 桥句 | 维持 | [3.16,11.69] 系更早版本区间，当版不存在；L56 已有 "an uncorrected upper bound. Two controls converge on a robust intermediate value" 桥式结构 + 3.68 [1.67,3.97]/3.66 [1.92,3.78] 双呈现 |
| R1 放置类：DeLong SI-only | 维持 | SI Note 1 "AUC interval methods (v52)" 段已存在（L159），NC 惯例 |
| R1 放置类：脑残差三项 | 维持 | MS L65 + SI Table 4 双载一致 |
| R1 放置类：Bergmann n=21 SM-only | 维持 | 已在 MS L65 "(m = 21; minimum q = 0.042)" |
| R1 放置类：internal pairing 分级 | 覆盖 | 由 M4（L30 also descriptive）实现 |
| R1-m6 区间本体 | 已存在 | SI Note 1 L155 "Exact Clopper-Pearson intervals: ω 0/150 (upper 0.0198; 2/250 [0.001,0.029]); raw JS 0.553 [0.470,0.635]; cosine 0.580 [0.497,0.660]"；仅补 MS 指针（M5） |
| 摘要 "best bounded-power discrimination" | 维持 | nc54 决策 B；R5-② 回退建议属类 C 冲突项，按用户既定决策跳过 |
| R4 minor 4 supercluster 粒度 | 维持 | 两轮约定可选项 |
| nc55 R1 minors 1/2/3/4/7、R2 minor 6、nc52-R3 C5 | 跳过 | 不在 proof 沿留清单内（可选项），记录备查 |

## 五、词额总账
- 摘要：+7 −7 = 0 → 196/200
- MAIN：+25 −27 = −2 → ≈4,996/5,000（XV8 口径，构建后脚本实数复核）
- Methods/图注/声明区/SI：免词额
- 版本号（v0.5.2→v0.5.3）不在本轮，随 #86 统一切换
