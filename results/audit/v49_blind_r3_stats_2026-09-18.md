# v49 盲审报告 R3：生物统计学

- **稿件**：CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics（Nature Communications 投稿包 v49）
- **评审人角色**：R3 盲审人，生物统计学（独立评审，未参与 v49 分析与写作）
- **日期**：2026-09-18
- **评审材料**：`results/CKI_Manuscript_NC_fulltext.txt`、`results/CKI_Supplementary_NC_fulltext.txt`（重点 3.20/3.21）、`results/nc49_*.csv`（5 个）、`results/tcga_linear_norm_v44_all_pairs.csv`（35,306 对线性归一化权威对表）、`results/phase34_v2_all_pairs.csv`（35,306 对 softmax 旧口径对表）、`data/tcga/luad_egfr_kras_mutations.json`、`version3/CKI_Submission_v49_NC/figure4.pdf`、`figure5.pdf`
- **复算脚本**：`results/audit/r3_recalc.py`、`r3_recalc2.py`、`r3_recalc3.py`、`r3_recalc4.py`（Python 3.12，pandas 2.3.3 / scipy 1.17.1；只读，未修改任何稿件与数据文件）

---

## 总体评价、评分与判定

**评分：8 / 10。判定：Minor Revision。**

v49 新增的两块统计分析（真实数据中性漂移校准、TCGA 泛癌逐样本统计）在方法学上是健全的：n-matched null 设计正确匹配了每对的供体/细胞类型/组大小；cluster bootstrap 的聚类单元（样本级、按端点重采样权重乘积加权）是配对（dyadic）数据的标准正确做法；Dunn 检验带 tie 校正且 Holm 调整实现无误（本评审用 scipy 独立重写后逐项复现）；LIHC Cox 六模型敏感性全套 NO-GO 的呈现克制、诚实。两块分析的所有 headline 数字我都从权威 csv / 原始对表独立复算通过，精确到 3 位有效数字以上，无一不符——这在盲审经验中属于上游水准。诚实性披露（library 级技术成分、choroid plexus/Bergmann glia 例外、marker Jaccard 的特异性-敏感性权衡、置换分辨率对 FDR 结论的限制）充分。

未发现 P0。两处 P1 均为**报告口径/表述问题而非方法错误**：(1) TCGA 线性 vs softmax 归一化的主从表述自相矛盾，且对 LIHC 而言"quantitatively similar effect sizes"不成立（复算比值 1.31 vs 1.13，MWU P 1.7e-17 vs 9.9e-3）；(2) 摘要/Methods 的样本数（3,596；LUAD 495、KIRC 755、BRCA 1032）与实际进入对表的样本数（3,563；493/746/1010）不一致且未说明损耗原因。另有若干 P2。

---

## 复算节（独立复算，全部通过）

### R-1. Brain 漂移阶梯 T1 层（`nc49_brain_drift_ladder.csv`，4,906 行）

直接从长表重算，逐指标 FPR = mean(exceed_*)，校准比 = cal_* 的中位数。脚本核心片段：

```python
d = pd.read_csv('nc49_brain_drift_ladder.csv')
t1 = d[d.tier == 'T1_techrep']           # n = 2,161
fpr = t1['exceed_omega'].mean()          # 0.2864
cal = t1['cal_omega'].median()           # 1.038
lo, hi = wilson(619, 2161)               # [0.268, 0.306]
```

| 指标 | 复算 T1 FPR | 稿件值 | 复算 T1 校准中位 | 稿件值 | 判定 |
|---|---|---|---|---|---|
| ω | 28.6% (619/2161), Wilson [26.8, 30.6] | 28.6% [26.8, 30.6] | 1.038 | 1.04 | 完全吻合 |
| raw JS | 45.2% | 45.2% | 1.073 | 1.07 | 完全吻合 |
| cosine | 44.1% | 44.1% | 1.041 | — | 完全吻合 |
| Spearman | 40.6% | 40.6% | 1.029 | — | 完全吻合 |
| k_f | 37.6% | 37.6% | 1.055 | — | 完全吻合 |
| k_n | 35.7% | 35.7% | 1.047 | 1.05 | 完全吻合 |
| marker Jaccard | 19.9% | 19.9% | 1.048 | — | 完全吻合 |

逐类符号计数复算：ω 低于 raw JS 10/10 类、低于 cosine 9/10、低于 Spearman 8/10（与稿件完全一致；唯 Committed OPC 类三者并列、Choroid plexus 类 ω 66.7% 高于 Spearman 55.6%，稿件未隐瞒）。逐类 raw-JS/ω FPR 比值复算范围 1.17–2.30（稿件 1.2–2.3 ✓）。规模分层（按 min(n_a,n_b)）：≤30 核 n=199，ω 14.1%、raw JS 28.6%；>500 核 n=269，ω 48.0%、raw JS 72.5%——与稿件逐项吻合（31–500 档复算 27.3%，稿件同）。choroid plexus n=9 中位校准 2.306（稿 2.31 ✓）、Bergmann glia n=27 为 1.161（稿 1.16 ✓）。T1 k_n 校准 1.047（稿 1.05 ✓）。

T2/T3 层（tier 名 `T2_cross_donor`/`T3_cross_roi`）：

| 量 | 复算 | 稿件 | 判定 |
|---|---|---|---|
| T2 ω FPR / 校准 | 90.9% / 1.764 | 90.9% / 1.76 | ✓ |
| T2 raw JS FPR / 校准 | 98.4% / 3.320 | 98.4% / 3.32 | ✓ |
| T2 k_f FPR / 校准 | 98.7% / 3.217 | 98.7% / 3.22 | ✓ |
| T3 ω 校准 | 1.802 | 1.80 | ✓ |
| T3 raw JS 校准 | 2.976 | 2.98 | ✓ |
| T3 marker Jaccard 校准 | 1.405 | 1.41 | ✓ |
| ω 校准梯度 T1→T2→T3 | 1.038→1.764→1.802 | 1.04→1.76→1.80 | ✓ |
| raw JS 梯度 | 1.073→3.320→2.976 | 1.07→3.32→2.98 | ✓ |
| 各层 B | 100/30/30（csv B 列核实） | 100/30/30（Methods、Fig 4a） | ✓ |

### R-2. Kang 技术重复（`nc49_pilot_kang_techrep.csv`，30 对）

| 指标 | 复算 FPR | 复算 Wilson 95% CI | 复算校准中位 [IQR] | 稿件值 | 判定 |
|---|---|---|---|---|---|
| ω | 0/30 | [0.000, 0.114] | 0.963 [0.918, 0.998] | 全部一致 | ✓ |
| k_f | 0/30 | [0.000, 0.114] | 0.936 [0.908, 0.977] | 0/30 | ✓ |
| k_n | 1/30 | [0.006, 0.167] | 0.993 | 1/30 | ✓ |
| raw JS | 11/30 (36.7%) | [0.219, 0.545] | 1.019 | 全部一致 | ✓ |
| cosine | 7/30 (23.3%) | [0.118, 0.409] | 1.006 | 全部一致 | ✓ |

Fig 4d 图内标注（cal 0.96/0.94/0.99/1.02/1.01）与复算五指标一一对应 ✓。

### R-3. TCGA 泛癌表（从 `tcga_linear_norm_v44_all_pairs.csv` 35,306 对全链路重算）

ω 取 `omega_floor`（kn_floor=1e-4 口径）。五癌种 TT/NN 均值、NN/TT 比、单侧 MWU P 全部**精确复现** `nc49_tcga_pancancer.csv`（如 LUAD 121.66/299.76/2.464；LIHC P=9.94e-3；KIRC P=1.25e-238）。k_n 中位比 2.12–3.64（稿 2.1–3.6 ✓）、k_n 均值比与 k_f 均值逐格吻合。kn_floor 触发对复核：全表仅 1 对 kn < 1e-4（KIRC NN 对，kn=8.4064e-5，稿 8.41e-5 ✓）。复合结构复核：Spearman ρ(log ω, log k_f)=+0.038（稿 +0.04 ✓）、ρ(log ω, log k_n)=−0.816（稿 −0.82 ✓）、k_n log 方差占比 71.7%（稿 ≈72% ✓）。"median 4–11 pairs per tumor across cancer types"复核：五癌种中位数 4/5/7/8/11 ✓。

### R-4. LUAD 驱动突变三组分析（全链路独立重算：对表 + cBioPortal 存档突变标签）

从 2,000 个 LUAD TT 对派生逐肿瘤 ω/k_f/k_n（每个肿瘤参与对数中位 8，范围 2–17），按 15 字符 barcode 匹配 `luad_egfr_kras_mutations.json`（75 EGFR + 161 KRAS aliquot，2 个双突变；其中 1 个双突变无 TT 对覆盖），得分析集 n=492（WT 311 / EGFR 61 / KRAS 120 ✓）。KW 用 `scipy.stats.kruskal`；Dunn 按 tie 校正秩方差手写实现 + Holm：

| 量 | 复算 | 稿件/csv | 判定 |
|---|---|---|---|
| 组均值 ω (WT/EGFR/KRAS) | 115.37 / 122.22 / 136.94 | 115.4 / 122.2 / 136.9 | ✓ |
| KW ω | H=28.12, P=7.83e-7 | H=28.12, P=7.8e-7 | ✓ |
| Dunn-Holm WT vs KRAS | z=−5.295, P=3.569e-7 | 同 | ✓ |
| Dunn-Holm EGFR vs KRAS | z=−2.860, P=0.008467 | P=0.008 | ✓ |
| Dunn-Holm WT vs EGFR | z=−0.852, P=0.3943 | P=0.39 | ✓ |
| k_f KW / EGFR vs KRAS Dunn-Holm | H=8.386 P=0.0151 / z=−2.817 P=0.01455 | P=0.015 | ✓ |
| k_n KW / WT vs KRAS Dunn-Holm | H=16.002 P=3.35e-4 / z=3.809 P=4.18e-4 | P=4.2e-4 | ✓ |
| bootstrap KRAS−WT k_f 差 | csv 0.0105 [0.0024, 0.0192] | 稿 0.011 [0.002, 0.019] | ✓ |
| bootstrap EGFR−WT ω 差 | csv 6.842 [−2.092, 15.182] | 稿 6.8 [−2.1, 15.2] | ✓ |

KW 的 H→P（χ², df=2）与 Dunn 的 z→正态双侧 P→Holm 三步在 csv 内部完全自洽（另经 r3_recalc2.py 验证）。

### R-5. LIHC Cox 六模型（`nc49_pilot_lihc_cox.csv`）

HR=exp(coef)、CI=exp(coef±1.96·SE)、P=双侧正态(z) 全部内部自洽（0 行不符）。六个暴露（M1 ω 全协变量、M2 ω 分期+分级、M3 ω 未调整、M4 k_f、M5 k_n、M6 TN-ω）的 z 行 P 值 0.302–0.932，全部 ≥ 0.30 ✓；M1 HR 1.061 [0.853, 1.320] P=0.592（稿 1.06 [0.85, 1.32] P=0.59 ✓；n=271、事件 79）。NO-GO 判定适当。

**复算结论：本次抽查的全部数字（>40 个）与稿件/SI/图三方一致，无一不符。**

---

## 统计设计审计

### 1. n-matched null 设计（清单第 1 项）

- **Exchangeability**：T1 对为同（供体、脑区、细胞类型）的两个 10x library；null 将两 library 的细胞核合并、置换、按观测组大小重分。在"无 library 效应"H0 下核间可交换的假设成立；library 级技术效应（捕获效率、深度）对该假设的偏离正是 FPR 所度量的对象，设计自洽。T1 FPR 全面高于名义 5%（ω 28.6%）说明存在真实的 library 级结构，稿件对此的披露（"a real library-level technical component … that the k_n denominator absorbs only partially"）是诚实的。将 28.6% 称为 "misreporting" 而非统计假阳性是恰当措辞，因为地面真值"无功能差异"由设计保证，超出部分来自技术结构。
- **B 的充分性**：Kang B=200 时，p95 阈值的 MC 噪声 ≈ ±1.5 个百分点（√(0.95·0.05/200)），可接受；**但 brain T2/T3 仅 B=30**：p95 由 30 个 draw 的第 ~28.5 次序统计量估计，阈值 MC 噪声 ≈ ±4 个百分点，且每对判定粒度为 1/31（真 null 下期望超出率 ≈ 6.5% 而非 5%）。T2/T3 的 FPR 高达 75–99%，结论不受影响，校准比中位数经 1,089/1,656 对聚合后亦稳健；但稿件应在 Methods 或 SI 3.20 显式说明 B=30 的 MC 含义（目前只披露了 B 值本身）。**P2。**
- **FPR 二值化的功效与稳定性**：以"超自身 null p95"二值化是直观且可复算的；T1 的 n=2,161 使层级 FPR 精度充足（Wilson 半宽 ~1.9pp）。但 Wilson CI 把对视为 iid，而 T1 的 2,161 对聚簇于少数供体/脑区（4 供体）、Kang 的 30 对聚簇于 8 供体——CI 宽度存在轻-中度反保守。建议补一句说明或以供体为聚簇单元的稳健 CI。**P2。**
- Kang 跨指标 FPR 对比（0/30 vs 11/30）是基于**同一批 30 对**的配对比较，描述性呈现可接受，但若做正式检验应使用 McNemar 而非独立比例检验；建议加注。**P2。**

### 2. 多重比较与选择性报告（清单第 3 项）

Brain 阶梯 7 指标 × 3 层 × 10 细胞类型的全部数值在 SI Table 3.20b 与权威长表中完整归档，本评审逐项抽核未发现隐瞒不利单元格（如 ω 在 choroid plexus 类高于 Spearman、ω 在 Committed OPC 类与三者并列、marker Jaccard T1 FPR 低于 ω 均被正面披露并给出特异性-敏感性权衡论证）。主分析口径（FPR=超自身 p95；校准比=观测/null 中位）在 Methods"Neutral-drift calibration on technical replicates"节先定义、后呈现，顺序正确；无预注册声明，但全长表归档是最强的反 cherry-pick 保障。正文"10/10、9/10、8/10"类符号计数经复算精确成立。**未发现选择性报告证据。**

### 3. 逐样本 ω 的依赖结构与 cluster bootstrap（清单第 4 项）

- 35,306 对之间确实不独立（LUAD 每肿瘤中位参与 8 对，范围 2–17；BRCA 有肿瘤仅 1 对）。稿件的 cluster bootstrap 以**样本**为聚类单元、肿瘤/正常独立重采样、每对按两个端点重采样权重之积重新加权——这是 dyadic 数据 bootstrap 的标准正确实现，聚类单元选择正确。**该项无缺陷。**
- 一个未被传播的 MC 来源：TT/TN 对为一次性 seeded 抽样子集（2,000/癌种，seed 42），点估计本身含子抽样 MC 误差（粗估 SE ≈ sd/√2000，对比值的影响 ~0.01–0.02），bootstrap CI 在此基础上条件化。影响可忽略，建议一句话披露。**P2。**
- KW/Dunn 将逐样本均值视为独立观测：同样本对不共享（每对恰含两个不同样本），跨样本相关仅经公共配对池弱诱导，且秩检验对每组对数不等（2–17）导致的异方差稳健；标准做法，可接受。
- LIHC CI 包含 1（[0.968, 1.342]）被如实呈现为"four of five"，未粉饰。✓

### 4. 茎叶一致性抽查（清单第 5 项，三方：正文/SI/csv）

抽查 20+ 个数字全部一致，包括：T1 ω FPR 28.6% [26.8,30.6]（正文 ¶40 = SI 3.20 = csv 复算）；raw JS 45.2%；Kang 0/30 [0,0.114]、中位 0.963 [0.918,0.998]（正文 ¶39 = SI 3.20 = csv 复算 = Fig 4d）；Kang raw JS 11/30 [0.219,0.545]；T2 ω 90.9% vs raw JS 98.4%/k_f 98.7%（正文 = SI = csv）；校准梯度 1.04→1.76→1.80 与 1.07→3.32→2.98（三方）；choroid plexus 2.31/Bergmann 1.16（SI = csv）；规模分层 14.1%/48.0% 与 n=199/269（SI = csv）；LUAD KW P=7.8e-7（摘要 = 正文 = Fig 5b = csv 复算）；三组均值 115.4/122.2/136.9（正文 = SI = csv = 本评审全链路重算）；LUAD NN/TT 2.46 [2.13,2.86]（摘要 = 正文 = csv）；LIHC Cox HR 1.06 [0.85,1.32] P=0.59（正文 = SI 3.21d = csv）；k_n 中位比 2.1–3.6（正文 = csv）；kn_floor 1/35,306、8.41e-5 KIRC NN（正文 = 对表复核）。"median 4–11 pairs per tumor"（Methods = 复算 4/5/7/8/11）✓。

---

## 问题清单

### P0（阻断级）
无。

### P1（必须在接收前修正）

1. **TCGA 归一化口径的主从表述自相矛盾，且"quantitatively similar effect sizes"对 LIHC 不成立。** 正文 ¶52 称"all reported TCGA statistics were **recomputed under** a linear probability mapping … survived with quantitatively similar effect sizes"（即 softmax 为主、linear 为敏感性）；但 Fig 5 图注称"**All values from the linear-normalization re-computation**"，且 v49 全部权威表格（nc49_*）与正文数字均为 linear 口径——实际主从已颠倒，句子未更新。更重要的是本评审对同一批 35,306 对（两版对表均在库）的复算表明两种映射在 LIHC 上差异是实质性的：softmax NN/TT 比 1.314、MWU P=1.7e-17，linear 1.133、P=9.9e-3——超出 1 的部分相差约 2.4 倍、P 差 14 个数量级，"quantitatively similar"对 LIHC 是过度表述（其余四癌种确为方向与排序一致、幅度相近）。建议：统一主从表述（linear 为主则改写该句），并将"quantitatively similar"限定为"ranking and direction preserved; LIHC effect size is mapping-sensitive (1.31 vs 1.13)"。
2. **样本计数不一致且损耗未说明。** 摘要与正文称"3,596 TCGA samples"，Methods 给出 LUAD 495、KIRC 755、BRCA 1032；但实际进入对表分析的样本为 3,563（LUAD 493、KIRC 746、BRCA 1010；`nc49_tcga_pancancer.csv` 与 35,306 对表逐样本复核一致）。三种癌各损耗 2/9/22 个肿瘤（推测为 TT  seeded 子抽样或过滤所致）未在 Methods 说明。摘要 headline 数字与 Methods 计数应改为实际分析口径，或显式说明从表达矩阵到对表的损耗原因。

### P2（建议修正）

1. Brain T2/T3 的 per-pair null 仅 B=30：p95 阈值 MC 噪声 ≈ ±4pp、判定粒度 1/31（真 null 下期望超出率 ≈6.5%）；结论不受影响但应在 SI 3.20 显式说明，或增补 B≥100 的稳健性复跑。
2. 阶梯 FPR 的 Wilson CI 假设对间独立；T1 2,161 对聚簇于 4 供体/少数脑区、Kang 30 对聚簇于 8 供体，CI 宽度轻-中度反保守。建议注明或提供供体聚簇稳健 CI。
3. Kang 跨指标 FPR 对比为同一 30 对上的配对比较，正式检验应为 McNemar；目前描述性呈现建议加注。
4. cluster bootstrap CI 未传播 TT/TN 一次性 seeded 子抽样（2,000 对/癌种）的 MC 误差；影响 ~0.01–0.02 比值单位，建议一句话披露。
5. 双突变记账表述（"62 EGFR and 122 KRAS matched the matrix; 2 double mutants excluded" → 61+120）建议澄清：复算显示 2 个双突变中仅 1 个有 TT 对覆盖，分析 n=492 的构成（311 WT + 61 EGFR + 120 KRAS）本身正确，但从 aliquot 计数到分析计数的推导链读者无法不借助数据复现。
6. SI 3.21 引用"35,306 pairs; v44 re-computation"，建议同时给出权威对表文件名（`tcga_linear_norm_v44_all_pairs.csv`）以便复核；`nc49_tcga_luad_mutation.csv` 仅含汇总统计，建议归档逐样本 ω/k_f/k_n 表（当前须从对表+突变 json 重建，本评审已验证可重建且结果一致）。

---

## 评审结论

统计方法正确、实现无误、复算全过、限制披露诚实；两处 P1 均为可快速修正的报告口径问题，不触及任何推断结论。**评分 8/10，建议 Minor Revision。**

---

*附：复算脚本 `results/audit/r3_recalc.py`、`r3_recalc2.py`、`r3_recalc3.py`、`r3_recalc4.py`；运行环境 Python 3.12 + pandas 2.3.3 + scipy 1.17.1。评审过程未修改任何稿件、数据或 git 状态。*
