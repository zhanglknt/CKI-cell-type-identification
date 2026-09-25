# nc57 终审报告（R1 统计方法学）— v0.5.3 @3d220ac

审稿人：R1-stats。评审依据：当版 `results/CKI_Manuscript_NC_fulltext.txt` 全文重读（摘要至 Supp. Fig. 14 图注）+ `results/CKI_Supplementary_NC_fulltext.txt` 定点核查 + `results/audit/nc56_proof_fix_matrix.md` 逐条对照。所有引用均为当版文本，本轮独立打分。

## 总评分

- Soundness: **8.5/10**
- Novelty: 6/10
- Significance: 6.5/10
- Presentation: 8.5/10
- **Overall: 8.0/10**

## Verdict

**Accept**（仅剩 2 条 proof 轮引入的外观级 minor + 5 条沿留可选 minor，均不构成接收障碍）

## 一、nc55 我所提 7 条 Minor 的逐项核销

| # | 上轮问题 | 裁定 | 当版证据 |
|---|---|---|---|
| m1 | Fig. 4c/d "adjusted P = 0.009 and 0.029" 未标明 OLS 模型口径 | **UNRESOLVED**（沿留可选，proof 矩阵 §四明示"跳过"） | 图注 L197 原文未变，仍以 "All values from the linear-normalization re-computation" 收尾（指映射口径而非 P 值口径）。结论本身已由 §48 全肿瘤置换（P≤0.001）锚定，风险低。 |
| m2 | §48 "adjusted log-ω ratio 1.19, 95% CI [1.12, 1.26]" 区间方法未声明 | **UNRESOLVED**（沿留可选） | §48 原文未变。 |
| m3 | Fig. 1c 展示被废止的 300 值伪重复 bootstrap 分布且无提示 | **UNRESOLVED**（沿留可选） | 图注 L194 原文未变；两阶段 CI [6.38, 9.82] 在图注中已给出，误导风险有限。 |
| m4 | 小 n 相关家族推断口径不统一（§53 r=0.23 CI 方法未注明等） | **PARTIAL** | §74 已有 "descriptive only at n = 10 classes"；§53 "r = 0.23, 95% CI [−0.08, 0.38], n = 17" 的 CI 方法仍未注明，§58/§59 未变。 |
| m5 | §30 分解 P 值（k_f P=0.60、k_n P=3.0×10⁻¹⁶）描述性限定范围含糊 | **RESOLVED** | 当版 §30 句末已为 "…not greater functional specialization **(also descriptive; Supplementary Note 9)**"（矩阵 M4，注明来源 R1-m5）。限定明确覆盖分解 P 值。 |
| m6 | 模拟 FPR（55%/58%/0%）无区间 | **RESOLVED** | §32 新增指针 "ω in none **(Clopper-Pearson intervals in Supplementary Note 1)**"；SI Note 1 本体已核实存在："Exact Clopper-Pearson intervals: ω 0/150 under pure HK drift (one-sided 95% upper bound 0.0198; 2/250 pooled neutral replicates, 95% CI [0.001, 0.029]); raw JS 0.553 (95% CI [0.470, 0.635]); cosine 0.580 (95% CI [0.497, 0.660])"。数值与正文 55%/58% 一致（0.553/0.580）。 |
| m7 | §57 BH 未过关的第 4 个类未点名 | **UNRESOLVED**（琐碎沿留） | §57 原文未变。 |

核销小结：2 RESOLVED、1 PARTIAL、4 UNRESOLVED（均为上轮即标注"可选"且 proof 矩阵明示跳过者）。

## 二、nc56 proof 轮编辑的新问题排查

### 统计口径核对（全部通过）

- **A2 摘要 "housekeeping-anchored false-positive rate 0.00"**：与 SI Note 1 的 0/150（纯 HK drift）精确对应；pooled neutral 2/250 属更宽场景，摘要限定词 "housekeeping-anchored" 使表述严格成立。✓
- **A7 摘要 "(k_n-dominated)"**：与 §58/§76 口径一致。✓
- **M2/M13 ω_cal 精度前置+降级**：§26 "(one-significant-digit resolution)" 与 §69 "an indicative, dataset-relative scale" 及 SI Note 3（S2 "calibration-relevant results"）三处自洽，无残留 "operational scale" 强表述。✓
- **M5/M6/X1 four-tier drift ladder**：§37 "four-tier drift ladder"、Fig. 3a 图注、Methods §108 "(the per-pair null constituting the fourth ladder tier)" 三处一致。✓
- **M11/M12 FDR 限定词**：§63 "global FDR correction (minimum q = 0.520)" 与 §65 "within-family minimum q = 0.042" 区分了全族与分层族，消除此前歧义。✓
- **M15/M16 §75 措辞软化**："consistent with … within cohorts" + "the shift is largest in LIHC (+44%…)" 与 SI Note 8 新增 S1 对冲句（"GA/GG ≈ 1.8–2.3× … tentative, GTEx cross-cohort discrepancy unresolved"）方向一致。✓
- **S1 GTEx 不确定性量化**：已核实插入当版 SI（"the healthy ≈ adjacent similarity should be read within that tolerance (tentative, GTEx cross-cohort discrepancy unresolved)"），且 "Pair-level P values … descriptive only" 限定保持完好。✓
- **肝句、5,151 full-inventory、DeLong 段**：当版 SI 逐字复核，与 nc55 核定状态一致，未被 proof 轮触碰。✓

### 新引入问题（2 条，均为外观级 minor）

- **N1（minor，标点）**：§28 括号不配对。当版原文："…the Tabula Sapiens human atlas 9 (108,136 cells; 99 filtered cell-type entries, 4,851 pairs across six organs (largest-donor pseudobulks; Methods), using the same hybrid scheme…"——外层 "(108,136 cells;" 的右括号丢失（矩阵 M3 意图为 "Methods))" 双右括号，构建产物仅一个）。统计内容无误，但必须补回一个 ")"，否则整句结构破损。
- **N2（minor，措辞）**：§38 "small-stratum raw JS 28.6% to 72.5%" 限定词错位。28.6% 是 <30 nuclei 小层取值，72.5% 是 >500 nuclei 大层取值；"small-stratum" 置于区间前使读者误以为两端点皆属小层。建议改为 "raw JS 28.6% to 72.5% across the same strata"（消歧目的已由上下文达成）。

### 数字一致性抽查（当版文本内部）

- §32 "55% and 58%" ↔ SI 0.553/0.580 ✓；§37 T1 2,161/T2 1,089/T3 1,656 ↔ §108 ↔ Fig. 3a ✓；Fig. 3c "(T1: 28.6% versus 37.6–45.2%)" ↔ §37 ✓；§48 KW P=7.8×10⁻⁷ ↔ Fig. 4b ✓；§56 3.66 [1.92, 3.78] ↔ Fig. 6b ↔ 摘要 [1.9, 3.8] ✓；§63 148.3 vs 39 ↔ Fig. 6c ✓；§65 "within-family minimum q = 0.042" 与 §57 分层族口径无冲突 ✓。

## 三、问题清单分级

**Major：无。**

**Minor（proof 轮新引入，建议 proof 阶段顺手修复）：**
1. N1：§28 括号不配对（补一个 ")"）。
2. N2：§38 "small-stratum" 限定词错位。

**Minor（沿留可选项，不修复亦可接收）：**
3. m1：Fig. 4c/d 图注补 "(OLS model P-values; whole-tumor permutation confirmation in Section 3.13)"。
4. m2：§48 为 1.19 [1.12, 1.26] 标注区间方法。
5. m3：Fig. 1c 图注注明图示 300 值分布为伪重复、报告区间以两阶段为准。
6. m4：§53 注明 r 的 CI 方法；§58/§59 n=10 相关统一标 descriptive。
7. m7：§57 点名 BH 未过关的第 4 个类。

## 四、结论

v0.5.3 在统计口径上较 v0.5.2 严格更好：我上轮两条可操作的 minor（m5 分解 P 值限定、m6 模拟 FPR 区间）均已妥善落地且 SI 本体核实无误；proof 轮的 ω_cal 降级、FDR 限定词、four-tier 协调、GTEx tentative 对冲全部自洽，未引入任何统计表述错误。新引入的仅 2 条外观级 minor（§28 缺右括号、§38 small-stratum 措辞），修复成本极低。

**8.0/10，Accept。**
