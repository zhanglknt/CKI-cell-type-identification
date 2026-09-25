# nc55 盲审报告 — R2（单细胞/计算生物学审稿人）

**对象**：终稿 v0.5.2 @ 5a5ae6d；正文 `results/CKI_Manuscript_NC_fulltext.txt`（213 行，含图注）通读；SI 抽查 Note 1/5/6/7/8/9/14/16、Section 3.9–3.13、Supplementary Methods 5.1–5.14；xlsx 直读验证（19 sheets，Table 5 表注）。
**声明**：本报告基于当前文本独立重审，所有数字/措辞均引自当版原文；与本人此前轮次记忆冲突处以当版文本为准。

---

## 一、总评分：**8.0 / 10**　verdict：**minor revision**（仅文字性修订；无需新分析）

子项（NC 口径）：soundness 8 / novelty 6.5 / significance 7 / presentation 8。

**一句话总评**：度量学循环性、基准公平性与"负相关"解释三大上轮焦点均已被量化拆解而非修辞带过，方法边界（锚点可见性、50–200 细胞功效窗、scheme 特异绝对值）披露到近乎自虐的程度，剩余唯一实质问题是 GTEx"否定野效应"的四处措辞超出了其跨队列证据强度。

---

## 二、强项

1. **循环性被正面量化而非回避**。per-pair top-200 身份基因选择的循环性直接给出膨胀倍率与秩稳健度："Circular selection inflated k_f by a median 1.61-fold versus leave-pair-out (grand mean ω 38.55 reported; 26.5 leave-pair-out; 6.5 fixed)"（正文 45 行），且"pair-level ρ = 0.937 leave-pair-out, 0.918–0.931 other panels; class means ρ = 0.90–0.99"（45 行）。Note 7 进一步给出 S0–S3 四方案对照、scheme-matched 块置换（B = 200）下类级显著性保持，以及参考实现逐对复现（max |Δω| = 6.4 × 10⁻¹³）。结论强度被正确限定为"rank-based conclusions are robust, but the tier cutoffs (ω < 15/25/35) do not transfer"（45 行）。
2. **"负相关"解释现在是有证据的分解而非猜测**。正文 29 行给出 k_f/k_n 与四标准度量的分量相关（k_f +0.43~+0.72，k_n +0.69~+0.81，控制 k_n 后偏相关转正 +0.11~+0.54，entry-cluster CI 排除 0）；30 行 same-organ 现象的 k_n 归因（k_f P = 0.60 vs k_n P = 3.0 × 10⁻¹⁶）。 Discussion 70 行的 **k_n 置换地板分析**是本轮最有说服力的单点证据："permuting k_n across the 5,151 full-inventory human pairs predicts Spearman 0.524 between ω and k_f, yet the observed value is 0.089"——数学上可达 0.52 的伪相关被结构化基线压到 0.09，直接否证"ω 只是 k_f 的马甲"。
3. **设计匹配零假设贯穿全文**：脑 block-shuffle 保留 library 结构（99 行/5.6）、donor-stratified 零假设（102 行/5.7）、伪区域阴性对照（127,756 伪对，cross-origin 尾部率 5.79%/6.87% vs 名义 5%，Note 12）、技术复的 per-pair n-matched cell-shuffle 零假设（108 行/5.10）。伪区域对照中 same-origin 37.6% 下尾率同时证明了检验功效——这是少见的"零假设既校准又有功效"的完整论证。
4. **模拟特异性声明已自带对抗性边界**。Note 1 明确"the type-I and AUC advantages above are therefore conditional on that assumption rather than evidence for it"（SI 161 行），并用 S1（功能信号置于 HK 基因上：ω 全漏检，k_n 0.61→1.00 捕获）与 S2（非 HK 漂移：ω 保持 0.007–0.020）划定镜像边界；Note 5 的 N1 表达匹配非 HK 漂移对照（FPR 0.000–0.067 vs raw JS 0.81–1.00）把"FPR 0.00 是构造产物"的指控化解为可检验命题。
5. **基准诚实，包括败绩**。MELD/scDist 基准直接报告 CKI 在 500 基因广移下崩溃（AUC 0.05–0.13，"the anchor responds … and annihilates the ratio"，43 行）并给出适用建议"use MELD, scDist, or CKI's own k_f"；功效窗量化到"power … declines as n grows … pooled-donor designs at n ≥ 500: ≈ 0"（3.11）；Augur 比较自带 pyaugur 端口"self-reported benchmark"警示（Note 14）。
6. **TCGA 链条的口径治理是教科书级**：barcode 审计 ex-CC 默认队列（3,535/34,828 对；112 行"34,828 pairs after dropping the 478 pairs … from the 35,306-pair table"）、两口径映射（linear 权威 + softmax 对照，Table 5）、kn_floor 敏感性、whole-tumor 置换的调整模型（KRAS P ≤ 0.001 / EGFR P ≥ 0.28，48 行）、组成检查双路（marker 面板 + 参考自由 NNLS 回退，"non-parenchymal fraction versus k_n, ρ = 0.20–0.26"，49 行）、GTEx 第三参照。
7. **复现面完整**：包版本与论文方案逐一对齐（"func_method = \"pairwise_absdiff\" in package v0.5.2"、"reselect_identity = True"，86 行/5.1），v0.5.2 version DOI 写回（126 行），Dockerfile + Zenodo 归档。

---

## 三、Major 清单（1 条）

### M1｜GTEx"否定野效应"的四处措辞超出跨队列证据强度（= 上轮 B1，已沿留 proof，本盲审独立重新导出）

- **现状引文**：
  - 摘要（8 行）："GTEx references argue against a field-effect reading"
  - 引言（14 行）："an elevated housekeeping baseline that GTEx healthy references **confirm** as tumor-specific"
  - 结果（50 行）："adjacent non-tumor resembles healthy tissue, so the housekeeping elevation is tumor-specific **rather than** a field effect. Kidney is the exception"
  - 讨论（75 行）："supporting tumor-specific housekeeping elevation over a field effect"
- **问题**：SI Note 8（189 行）自家数据写明"Cross-cohort GTEx–adjacent pairs show k_n elevated to **tumor levels** in every organ (P ≤ 1.4 × 10⁻²⁶), a cohort-level technical effect; **mechanistic claims therefore rest on within-cohort orderings only**"。即 GTEx↔TCGA 的队列技术位移与待定位的 TT/NN 生物效应同量级（tumor 水平），此时"adjacent ≈ healthy"（GG/NN 中位数比 1.03–1.18）的断言恰恰依赖于一次跨队列绝对值比较——而本文自己规定"comparisons only within the same dataset … absolute ω does not transfer"（79 行）、k_n 同为 pipeline 内部量。两处规则与一处结论互相矛盾：野效应并未被排除，只是与队列效应无法分离。
- **与当版一致性说明**：SI 侧已含必要的警示句（189 行末），问题集中在 MS 四处措辞仍为断言式；"confirm"（14 行）与"rather than"（50 行）是最重的两处。
- **要求**：按已协商的 proof 清单软化四处措辞（如"consistent with a tumor-specific elevation, though the cross-cohort GTEx comparison cannot fully exclude a field contribution"），并在 Note 8 补不确定度句（候选插入"(tentative, GTEx cross-cohort discrepancy unresolved)"已记录在案）。纯文字修复，无需新分析。

---

## 四、Minor 清单（7 条，均附当版引文）

1. **摘要 FPR 0.00 缺锚定限定**（8 行）："ω rejected neutral housekeeping drift (false-positive rate 0.00 versus 0.55–0.58 …)"——该 0.00 是 HK 锚定漂移下的构造条件结果，严格 N1 对照为 0.000–0.067（Note 5）。引言 13 行虽有"Functional signal on HK genes is invisible to ω by construction"，但摘要读者看不到。建议在摘要插入"housekeeping-anchored"类限定（摘要 196/200，尚有余量）。
2. **推荐细胞数下界两处不一**：79 行"at least **100–200** cells per group" vs 80 行"bounding the operating window at **~50–200** cells"，Note 16 与 3.11 均为 50–200。建议 79 行改为"at least ~100 cells（operating window ~50–200; Section 3.11）"式表述。
3. **kn_floor 两处表述易造成表观矛盾**：49 行"the housekeeping floor (k_n ≥ 10⁻⁴) is **never reached**"（逐对口径）vs 90 行/5.2"aggregate k_n **sits at the denominator floor** in 3 of 5 cancer types"（聚合级固定面板检验）。两者技术上各自成立，建议分别加"(pair-level)"、"(aggregate-level fixed-panel test)"限定。
4. **FDR 全球/分层口径需明示**：63 行"no candidate survives FDR correction (minimum q = 0.520)"（全球 m = 31,764）vs 65 行"the only sub-nominal stratified family is intra-cerebellar Bergmann-glia (m = 21; **minimum q = 0.042**)"（族内 < 0.05）。建议 63 行加"global"、65 行点明"within-family"，避免读者误读为矛盾。
5. **Note 14 Python 版本过时**："the reference Python port augurpy is not distributed for Python **3.13**"，而 5.13 环境为 Python **3.14.4**。顺手更新。
6. **TCGA 两段超长句影响可读性**：48 行（KRAS/EGFR + 调整 + 置换，约 130 词）与 49 行（四个对照打包，约 150 词）各为单句，NC 读者负担过重，建议各拆 2–3 句。
7. **Tabula Sapiens 相关结构分析的单供体基址宜在结果处点一句**：97 行/5.5"one pseudobulk per cell-type entry from its largest donor … does not capture inter-donor variability"——29–30 行的负相关与 52–53 行的跨器官排名均建立在此基址上；entry-cluster bootstrap 处理了对的嵌套，但不产生供体间变异。方法处有披露即合规，结果处加半句指针更稳。

**沿留 proof 项（复述确认）**：B2 讨论 75 行 KIRC/组成异质性句（"attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)"方向表述缠绕）按清单改写——本盲审复核该句仍在当版（75 行），同意沿留。

**记录在案、不要求行动**：scDist 为 Python 近似实现，限制段（80 行）已承诺"should be re-verified against the original"；当前结论对该近似的依赖仅为"广扰动请用 MELD/scDist"的推荐，方向性不受影响。

---

## 五、nc53/nc54 处置逐条复核（全部基于当版文本直读/直验）

| # | 处置项 | 当版证据 | 结论 |
|---|--------|----------|------|
| nc53-1 | "5,151 full-inventory" 限定 + SI Note 9 新段 | 70 行"permuting k_n across the **5,151 full-inventory** human pairs predicts Spearman **0.524** … observed value is **0.089**"；SI Note 9（193 行）完整段落含地板 0.524 [0.506, 0.541]、鼠 0.857 vs 0.821 | **RESOLVED** |
| nc53-2 | SI xlsx 扩至 19 sheets | 直读 zip 内 19 个 sheet XML；191 行"Supplementary Tables 1–19"、124 行"Tables 5–19"一致 | **RESOLVED** |
| nc53-3 | Note 1 补 DeLong 方法段 | SI 159 行"AUC interval methods (v52) … DeLong interval on the 850-replicate ROC (600 signal, 250 neutral)"，模块种子聚类 bootstrap [0.771, 0.836] 交叉验证 | **RESOLVED** |
| nc54-1 | Fig. 4a 标明 k_f 为 NN/TT 取向 | 197 行图注"the amber axis shows the corresponding tumor/normal ratio of … k_n (TT/NN …), which exceeds 1 in all five … **while the NN/TT ratio of k_f does not**" | **RESOLVED** |
| nc54-2 | GTEx 肝句方向修复 | SI 189 行"in liver the two medians coincide (**ratio 1.03**) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, with a **heavier adjacent upper tail**"；MS 50 行"healthy/adjacent ≈ 1.0–1.2"覆盖 1.03–1.18 | **RESOLVED** |
| nc54-3 | 模拟 38% 标明为模拟结果 | 70 行"under fourfold cell-count imbalance **(simulation)** k_f misreports 38% of neutral pairs, ω none" | **RESOLVED** |
| 我上轮条件③ | Table 5 表注 −1.3%→−0.9% | 直读当版 xlsx sheet5 表注：含"−0.9%"与"[−4.3%, +2.5%]"，旧"−1.3%"已不存在 | **RESOLVED** |
| 我上轮条件④ | 2.0–2.7→2.0–2.8 | 50 行"tumor k_n is **2.0–2.8-fold** higher"（覆盖 TT/NN 2.07–2.77 与 TT/GG 2.01–2.65 两读法） | **RESOLVED** |
| 我上轮条件⑤ | MS 49 行 ρ 指代补全 | 49 行末"reference-free composition check: **non-parenchymal fraction versus k_n**, ρ = 0.20–0.26; Supplementary Note 8" | **RESOLVED** |
| B1 | GTEx 四处措辞 + Note 8 不确定度句 | MS 8/14/50/75 行仍为断言式（见 M1）；SI 189 行已有跨队列警示半句 | **沿留 proof（接受）** |
| B2 | KIRC/组成异质性句改写 | 75 行原句仍在 | **沿留 proof（接受）** |
| v0.5.2 | 摘要 196/200 + 版本面 + DOI | 摘要实测 **196 词**；"gave the best bounded-power discrimination"（8 行）在；126 行"v0.5.2 … version DOI: 10.5281/zenodo.22949350" | **RESOLVED** |

---

## 六、具体修改建议（按优先级）

1. **（M1，proof 已排期）** 软化 8/14/50/75 行四处 GTEx 措辞为"与肿瘤特异升高一致、但跨队列比较不能完全排除野效应贡献"口径，并在 Note 8 GTEx 段末补一句不确定度声明（含候选插入语"(tentative, GTEx cross-cohort discrepancy unresolved)"）。
2. **（Minor 1）** 摘要"rejected neutral housekeeping drift"处加锚定限定词，使 FPR 0.00 的条件性在摘要自明。
3. **（Minor 2/3/4）** 三处口径对齐：79 行 100–200 与 80 行 50–200 的下界调和；49 行 floor 句加"(pair-level)"、90 行加"(aggregate-level)"；63 行 FDR 加"global"、65 行加"within-family"。
4. **（Minor 5/6/7）** Note 14 Python 版本号更新；48/49 行超长句拆分；29 行结果处补半句"largest-donor pseudobulk (Methods)"指针。
5. **（B2，proof 已排期）** 75 行组成异质性句按已协商方案改写。

---

## 七、复审人结语

本版与早期文本相比，方法学主张的每一条都已绑定相应的设计匹配零假设与失效边界：循环性给出膨胀倍率与秩稳健度，"负相关"给出分量分解与数学地板否证，特异性给出对抗性场景与表达匹配对照，泛癌逆转给出 ex-CC/两口径/组成/置换四重控制，脑梯度给出跨度+大小联合对照与供体 bootstrap。ω 相对其分子 k_f 的真实数据增量被作者自己限定为"calibration, not detection power … on real-data orderings the increment is not established"（71 行）——这是本文剩余的核心张力，但披露充分、定位（特异性优先筛查 + 原则性零模型）与之自洽，不构成拒稿理由。落实 M1 的四处措辞软化后即达接收标准。
