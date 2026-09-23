# nc52 TCGA 实现说明（v52 修订，审稿人 B1/B3/B4/B5/B7）

**日期**: 2026-09-24
**执行**: W-tcga
**环境**: 仓库内 venv `cki_env`（Python 3.14.4；本机无 conda，`conda run -n cki_env` 不可用，实际命令为 `./cki_env/Scripts/python.exe <脚本>`）；R 4.1.3（`C:/Program Files/R/R-4.1.3`，仅 30 个 base/recommended 包，用于 Cox PH 检验）
**种子**: 全部 42（B7 与 B3 的可行性检查为确定性计算，无种子）
**ex-CC 规则**: barcode `[5:7] == "CC"`（ILSBio 细胞系，32 个 LIHC 肿瘤；沿袭 94_cc_audit_sensitivity_v49.py）

---

## B1：CC 默认排除 + TCGA 主链重跑

**输入**: `results/tcga_linear_norm_v44_all_pairs.csv`（35,306 pairs；ex-CC 过滤丢 291 对触 CC 的 pair → 35,015）、`results/nc49_tcga_admix_scores.csv`、`data/tcga/lihc_patient_clinical.json`、`data/tcga/luad_egfr_kras_mutations.json`、`results/phase34_pam50_cache.json`
**脚本**: `notebooks/nc52_tcga_excc_main.py`（主链 + severity + admix 组成回归）、`notebooks/nc52_tcga_composition_excc.py`（4-panel 组成回归）、`notebooks/nc52_lihc_cox_excc.py`（Cox）
**方法**: 逐行镜像 nc49_tcga_main.py Module A（multinomial 端点权重 cluster bootstrap，B=1,000，共享 rng 流按癌种顺序）；severity 镜像 85 脚本（raw omega，kn_floor=0 约定；LIHC JT、BRCA/LUAD KW）；组成回归两套（ESTIMATE admix OLS + 86 脚本 4-panel |Δcomposition| 衰减，后者 CC 同时从 z-score 标准化总体中排除）；Cox 用 R survival::coxph + cox.zph（stage 改分类变量 factor(I/II/III/IV)，报 PH 检验，k_f 模型完整报告；z 分数在 ex-CC 队列上标准化）。

### 关键数字（ex-CC 默认；括号为含 CC 旧值）

五癌种 NN/TT ω 比值（linear 口径）：
| 癌种 | NN/TT | 95% CI | 跨 1? | n_tumor |
|---|---|---|---|---|
| LUAD | 2.464 | [2.128, 2.863] | 否（>1） | 493 |
| LUSC | 1.708 | [1.378, 2.087] | 否 | 534 |
| **LIHC** | **1.112** | **[0.943, 1.302]** | **跨 1** | **366**（旧 398） |
| KIRC | 1.880 | [1.638, 2.148] | 否 | 750 |
| BRCA | 1.567 | [1.342, 1.815] | 否 | 1010 |

- **LIHC ex-CC：NN/TT = 1.112 [0.943, 1.302]，CI 跨 1（MWU P=0.113）**；含 CC 旧值 1.104 [0.933, 1.286] 同样跨 1 → LIHC 结论方向不变（该癌种 NN/TT 不显著），"four of five" 叙事在 linear 口径下维持。
- LIHC TT/NN k_n 中位数比 2.06（旧 2.08）；k_n 均值比 1.337，CI [1.022, 1.886] 排除 1。注意：v49.13 敏感性曾报 [0.997, 1.880]（跨 1）——差异完全来自 bootstrap rng 流位置（敏感性脚本对 LIHC 单独起流，本链共享流按 LUAD→LUSC→LIHC 顺序消费）；点估计一致（1.337 vs 1.35），CI 下界贴 1，流依赖已在此记录。
- k_f TT/NN 中位数比：LUAD 1.432、LUSC 1.790、LIHC 1.886、KIRC 1.626、BRCA 2.074。
- LIHC Cox（ex-CC，n=272，79 deaths）：M1 ω 全模型 HR/SD = 1.081 [0.876, 1.335]，P=0.467（含 CC 参考 1.063 [0.880, 1.284]，P=0.526，n=304）；M2（ω+stage+grade）HR=0.999，P=0.993，**其 cox.zph GLOBAL P=0.0226 < 0.05（M2 存在 PH 偏离信号，已报告）**；M1 zph GLOBAL P=0.073；M3 未调整 HR=1.058，P=0.572；M4 k_f 全模型 HR=1.074 [0.845, 1.365]，P=0.560（zph GLOBAL P=0.091）；M5 k_n HR=0.928，P=0.386；M6 TN-ω HR=0.952，P=0.665。ex-CC 默认下 ω 的预后关联依旧不显著。
- Edmondson 分层（ex-CC，LIHC n=289）：G1 78.79 / G2 75.80 / G3 77.61 / G4 72.29（raw ω），JT P<1e-15（ω）、8.4e-12（k_f）、<1e-15（k_n），单调层级检验方向与含 CC 版一致。
- 组成回归（ex-CC）：4-panel LIHC log(k_n) TT 系数 +0.5208 → 调整後 +0.2912，衰减 44.1%（bootstrap median +43.4% [+29.9%, +60.0%]；含 CC 旧值 33.8% [+21.5%, +48.1%]——ex-CC 下 LIHC 组成混杂更强而非更弱）；pooled 衰减 −0.9% [−4.3%, +2.5%]；ESTIMATE admix OLS 的 TT-vs-NN log gap 调整（A1 型）五癌种均保持高度显著（如 LIHC k_f 未调 +0.517 → 调整 +0.514，P=1.8e-208）。

**输出**: `results/nc52_tcga_pancancer_excc.csv`、`results/nc52_tcga_excc_severity.csv`、`results/nc52_tcga_excc_composition.csv`（admix OLS）、`results/nc52_tcga_excc_summary.json`、`results/nc52_lihc_cox_excc.csv`、`_zph.csv`、`_cohort.csv`、`results/nc52_tcga_composition_excc.csv/.txt`（4-panel）

### Superseded（含 CC 旧结果，已移 `results/superseded/` 并在文件头标注权威替代）

- `nc49_tcga_pancancer.csv` → `results/nc52_tcga_pancancer_excc.csv`
- `nc49_pilot_lihc_cox.csv` → `results/nc52_lihc_cox_excc.csv`
- `tcga_clinical_severity_v44.csv/.json` → `results/nc52_tcga_excc_severity.csv`
- `tcga_composition_v44.csv/.txt` → `results/nc52_tcga_composition_excc.csv/.txt`
- 未移动但部分被替代：`results/nc49_tcga_kf_composition.csv`（A1/A2 含 CC，其替代为 `nc52_tcga_excc_composition.csv`；Part B LUAD Hallmark 不受 CC 影响仍有效——LUAD 无 CC 样本）；`results/phase34_v2_*_pairs.csv`（softmax 无标签 pair 表，B5 已由 `nc52_tcga_softmax_all_pairs.csv` 取代，但其为主管线原始产物且被大量 verify 引用，保留待后续阶段统一处理）。
- 引用上述被移文件的 verify/生成脚本（后续阶段需同步）：`results/audit/r3_recalc*.py`、`_nc49_si_verify.py`、`_nc49_cl_guide_verify.py`、`_v4914_xv5_check.py`、`_xv491_diag2.py`、`generate_manuscript_nc.py`、`notebooks/68_gen_supplementary_nc.py`、`99_build_nc_v49.py` 系（GB 系 build 引用 severity 数字）等。

---

## B4：LUAD 调整模型 whole-tumor 标签置换

**输入**: 同 nc49_tcga_luad_smoking.py（cbioportal 临床 + 突变 JSON + v44 pair 表 + admix）
**脚本**: `notebooks/nc52_tcga_luad_adjmodel_permutation.py`
**方法**: 队列构建逐行镜像 smoking 脚本（n：smoke_adj 427、smoke_agesex_adj 411、smoke_admix_adj 427）；置换 mutation 组标签（WT/EGFR/KRAS）跨整个肿瘤，协变量不动；统计量为组对比系数（EGFR−WT、KRAS−WT、KRAS−EGFR）；B=10,000，seed 42；双侧 P=(1+#|T_perm|≥|T_obs|)/(B+1)。design effect = 1+(m−1)ρ，m=每肿瘤 TT pair 中位数=8，ρ 为 pair 级值在肿瘤内的 pairwise 矩估计 ICC。

### 关键数字（ω；perm P vs OLS P）

| 模型 | 对比 | obs 系数 | OLS P | **置换 P** |
|---|---|---|---|---|
| B_smoke_adj | EGFR−WT | −3.08 | 0.561 | 0.555 |
| B_smoke_adj | KRAS−WT | +13.87 | 5.9e-4 | **7.0e-4** |
| B_smoke_agesex_adj | EGFR−WT | −3.52 | 0.524 | 0.518 |
| B_smoke_agesex_adj | KRAS−WT | +13.28 | 1.4e-3 | **1.0e-3** |
| B_smoke_admix_adj | EGFR−WT | −5.33 | 0.285 | 0.282 |
| B_smoke_admix_adj | KRAS−WT | +13.64 | 3.3e-4 | **3.0e-4** |

- **EGFR 调整后不显著的方向在置换后维持**（三模型 perm P 0.28–0.55，均 >0.05）；**KRAS 调整后显著的方向在置换后维持**（perm P 7e-4 / 1e-3 / 3e-4，均 ≤0.001）。OLS 与置换结论一致，i.i.d. 误差不改变方向结论。KRAS−EGFR 对比亦维持显著（perm P 0.0033 / 0.0051 / 4e-4）。
- k_f：KRAS−WT perm P 0.044 / 0.019 / 0.030；k_n：KRAS−WT perm P 0.013 / 0.018 / 0.010（均与 OLS 同向）。
- design effect：ω 3.16（ρ=0.309）、k_f 2.55（ρ=0.221）、k_n 3.97（ρ=0.424）（m=8）——pair 级数据存在实质肿瘤内相关，支持以 per-tumor 聚合 + whole-tumor 置换为默认推断。

**输出**: `results/nc52_tcga_luad_adjmodel_permutation.csv`

---

## B5：linear vs softmax 两口径全表

**输入**: linear = `results/tcga_linear_norm_v44_all_pairs.csv`；softmax = `results/nc52_tcga_softmax_all_pairs.csv`（**新产出**：`notebooks/nc52_tcga_softmax_pairs.py`，06_phase34_v2.py 的逐行镜像 + sample 标签，35,306 pairs 与原 v2 总数一致，kn_floor=1e-4，seed 42，同一 TT 子抽样播种顺序；运行 816s）
**脚本**: `notebooks/nc52_tcga_mapping_schemes.py`
**方法**: ex-CC 默认；两口径均做 sample-level cluster bootstrap（B=1,000，seed 42，共享 rng 流按 linear×癌种 → softmax×癌种 顺序）。

### 关键数字

| 癌种 | linear NN/TT [CI] | softmax NN/TT [CI] |
|---|---|---|
| LUAD | 2.464 [2.128, 2.863] | 2.620 [2.265, 3.042] |
| LUSC | 1.708 [1.378, 2.087] | 1.885 [1.508, 2.294] |
| **LIHC** | 1.112 [0.943, 1.302]（跨 1） | **1.286 [1.091, 1.533]（排除 1）** |
| KIRC | 1.880 [1.638, 2.148] | 2.046 [1.760, 2.335] |
| BRCA | 1.567 [1.342, 1.815] | 1.748 [1.511, 2.009] |

- **CI 排除 1：linear 4/5，softmax 5/5**。softmax（即稿件原口径）下 LIHC CI 排除 1（P_MWU=6.0e-13），"five of five" 成立；linear 口径下 LIHC 跨 1，"four of five"。叙事选择取决于口径：softmax 为原稿口径支持 five-of-five，但 linear 更保守。两口径方向一致（全部 NN/TT>1）。

**输出**: `results/nc52_tcga_mapping_schemes_table.csv`、`results/nc52_tcga_mapping_schemes_summary.json`、`results/nc52_tcga_softmax_all_pairs.csv`

---

## B7：kn_floor 敏感性

**输入**: 同上两个 pair 表（pair 级 kn/kf 直接重算 ω = k_f/max(k_n, floor)，无需重算矩阵）
**脚本**: `notebooks/nc52_tcga_knfloor_sensitivity.py`
**方法**: kn_floor ∈ {0, 1e-5, 1e-4, 1e-3}；floor=0 为 raw 守卫（kn≤0→inf，inf 剔除并计数——实际五癌种两口径均无 inf、无 kn<1e-4 的 pair）；ex-CC 默认；报反转幅度（NN/TT）及相对 1e-4 的变化量。

### 关键数字（NN/TT by floor；linear / softmax）

| 癌种 | 0 / 1e-5 / 1e-4 | 1e-3（linear） | 1e-3（softmax） |
|---|---|---|---|
| LUAD | 2.464（三档相同） | 1.494（Δ−0.97） | 2.155（Δ−0.47） |
| LUSC | 1.708 | 1.099（Δ−0.61） | 1.684（Δ−0.20） |
| LIHC | 1.112 / softmax 1.286 | 1.038（Δ−0.07） | 1.271（Δ−0.02） |
| KIRC | 1.880 / 2.046 | 1.191（Δ−0.69） | 1.740（Δ−0.31） |
| BRCA | 1.567 / 1.748 | **0.909（Δ−0.66，跌穿 1）** | 1.481（Δ−0.27） |

- **趋势**：floor ≤1e-4 时结果完全不敏感（没有任何 pair 的 kn 落在 (0, 1e-4)——1e-4 只截断退化零分母）；floor=1e-3 会截断约 50% 的 NN pair（frac_NN_at_floor≈0.50–0.53）从而系统性压缩反转，linear 口径下 BRCA 甚至跌穿 1。结论：已发表的 1e-4 选择远离敏感区，但 kn_floor 每提高一个数量级都会显著衰减 NN/TT——该依赖已量化成表。

**输出**: `results/nc52_tcga_knfloor_sensitivity.csv`

---

## B3：去卷积可行性评估

**脚本**: `notebooks/nc52_tcga_deconv_feasibility.py`
**运行时验证的可行性结论**：
1. **CIBERSORTx 不可行**：需在线 API + 注册 token；本环境未配置任何凭证（CIBERSORTX_TOKEN/CIBERSORTX_EMAIL 均空），修订环境离线。
2. **BayesPrism 不可行**：R 4.1.3 存在但仅 30 个 base 包，BayesPrism 未安装；其 Bioconductor 依赖链属"大依赖"，按修订约束禁止安装（未尝试）。
3. **参考 scRNA 可得**：本地 Tabula Sapiens Liver（5,007 细胞，4 compartment）与 Kidney（9,641 细胞，3 compartment）h5ad → marker 代理方案可行。

**替代方案（已实现）**：TS compartment 参考谱（CP10k+log1p）→ 每 compartment 检出率 ≥20% 取 top-60 特异性 marker（LIHC 231 / KIRC 174 个可映射基因）→ 每个 ex-CC 肿瘤 rank 变换后 NNLS（rank-SSE）估计 compartment 分数；分半一致性（marker 集随机对半，seed 42）；与 ESTIMATE admix、per-tumor k_n 的 Spearman 相关。

### 关键数字

| 癌种 | n | 分半 ρ | 非实质分数 vs k_n | 非实质分数 vs ESTIMATE | k_n vs ESTIMATE |
|---|---|---|---|---|---|
| LIHC | 366 | 0.934（P=3.8e-179） | +0.200（P=1.2e-4） | +0.586（P=3.6e-35） | −0.226（P=1.2e-5） |
| KIRC | 754 | 0.964（P<1e-300） | +0.262（P=2.9e-13） | +0.238（P=3.3e-11） | −0.377（P=9.7e-27） |

- 代理可靠性高（分半 ρ 0.93–0.96），与独立的 ESTIMATE 分数交叉验证一致（LIHC ρ=0.586）→ 替代证据强度：中等偏高。
- 非实质（免疫/基质/内皮）分数与 k_n 仅弱正相关（ρ 0.20–0.26），且 k_n 与 ESTIMATE admix 呈弱**负**相关 → k_n 的 TT 升高不能被细胞组成解释，与 B1 组成回归 pooled 衰减 ≈0 相互印证；但 LIHC 4-panel 衰减 44% 提示该癌种组成混杂确实偏强，解读 LIHC 时需谨慎（与 LIHC NN/TT CI 跨 1 一致）。

**输出**: `results/nc52_tcga_deconv_feasibility.csv/.json`、`results/nc52_tcga_deconv_lihc_pertumor.csv`、`results/nc52_tcga_deconv_kirc_pertumor.csv`

---

## 输出文件清单（全部 nc52 前缀）

脚本（notebooks/）：nc52_tcga_softmax_pairs.py、nc52_tcga_excc_main.py、nc52_lihc_cox_excc.py、nc52_tcga_luad_adjmodel_permutation.py、nc52_tcga_mapping_schemes.py、nc52_tcga_knfloor_sensitivity.py、nc52_tcga_deconv_feasibility.py、nc52_tcga_composition_excc.py
结果（results/）：nc52_tcga_softmax_all_pairs.csv、nc52_tcga_pancancer_excc.csv、nc52_tcga_excc_severity.csv、nc52_tcga_excc_composition.csv、nc52_tcga_excc_summary.json、nc52_lihc_cox_excc.csv、nc52_lihc_cox_excc_zph.csv、nc52_lihc_cox_excc_cohort.csv、nc52_tcga_luad_adjmodel_permutation.csv、nc52_tcga_mapping_schemes_table.csv、nc52_tcga_mapping_schemes_summary.json、nc52_tcga_knfloor_sensitivity.csv、nc52_tcga_deconv_feasibility.csv/.json、nc52_tcga_deconv_lihc_pertumor.csv、nc52_tcga_deconv_kirc_pertumor.csv、nc52_tcga_composition_excc.csv/.txt
移动（results/superseded/，已标注）：nc49_tcga_pancancer.csv、nc49_pilot_lihc_cox.csv、tcga_clinical_severity_v44.csv/.json、tcga_composition_v44.csv/.txt
