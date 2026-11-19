# B1–B5 结构性新分析 — 启动路线与证据清单（nc86）

- **日期**：2026-11-19
- **作者裁定**：启动 B1–B5 新分析
- **方法**：独立只读侦察（`Explore` 子代理，未写任何文件、未运行会写 `results/` 的分析脚本），逐项核对磁盘上的真实数据与脚本
- **重要更正**：先前口头概括「B1/B2 需新脚本」不准确。实测 **B1/B2/B3/B5 的结果文件已全部算完，只需写稿**；**只有 B4 按字面不可做**，但已有可行的 proxy 替代。以下以磁盘实测为准。

---

## 1. 汇总判定

| 项 | 判定 | 是否改动稿件数字 | 一句话依据 |
|---|---|---|---|
| **B1** 独立 ground truth | **结果已齐，只需写稿** | 不改（仅新增证据） | Kang 真实扰动 ROC + 校准已有；「功能信号落在锚上 / 漂移落在 identity 面板」混合场景已由 `75_sim_circularity_scenarios.py` 落地 |
| **B2** 适用范围 / power 机理 | **结果已齐，只需写稿** | 不改（除非新增 pseudobulk 替代推断） | `nc80_mj_kang_modular_*` 与 `competitors_v44_power_*` 已含 n 网格与 power/TPR-vs-n 数值 |
| **B3** 增量价值判定 | **结果已齐，只需写稿** | 不改 | ΔAUC / 配对 DeLong / McNemar / 现有方法比较全齐，Table 2c 三份源数据可追溯 |
| **B4** ambient / PMI 敏感性 | **按字面不可做，有 proxy 替代** | **会改**（k_n、3.66/6.10-fold 梯度） | 无 PMI/RIN 元数据、无内含子/外显子矩阵、无 SoupX/CellBender/DecontX；depth/UMI/mito proxy 回归已完成 |
| **B5** k_n floor 敏感性 | **结果已齐，只需写稿** | 不改 | 触底比例 + 去 floor 后 NN/TT 稳健性已算完并存表 |

---

## 2. B1 独立 ground truth

**证据（均在本地）**
- 原始数据：`data/kang_ifnb/GSE96583_RAW.tar`、`GSM2560248_2.1.mtx.gz`、`GSM2560249_2.2.mtx.gz`、`GSE96583_genes.txt.gz`
- 独立标签 ROC：`notebooks/79_kang_ifnb_demo.py:205,299-323` → `results/kang_ifnb_demo_pairs.csv`(64,831 B)、`kang_ifnb_demo_summary.json`
- 校准：`notebooks/nc49_pilot_kang_techrep.py:240,289` → `results/nc49_pilot_kang_techrep.csv`、`nc49_calib_leave_one_out.csv`
- **混合场景已存在**：`notebooks/75_sim_circularity_scenarios.py:12-24` 的 S1 `functional_on_hk`、S2 `neutral_on_nonhk` → `results/sim_circularity_raw.csv`(190,391 B)、`_summary.csv/.json`、`_report.txt`；文字结论在 `68_gen_supplementary_nc.py:2303,2312`
- 时序/疾病阶梯：`results/tms_age_ladder.csv`、`sea_ad_severity_ladder.csv`、`sea_ad_dam_positive_control.csv`

**写稿口径**：把「ground truth 与 HK/identity 划分无关」显式化——Kang 是**真实生物学扰动标签**（stim vs ctrl），不是按面板注入；`sim_circularity_*` 的 S1/S2 正好覆盖 R1 要求的「功能信号在锚上、漂移在 identity 面板」反例。**不需要新模拟**。

**唯一缺口（可选）**：TMS 衰老阶梯 / SEA-AD 严重程度目前只有 ladder（单调性），未做二分类 ROC + 校准。若审稿人强制，需 1 个新脚本，预期 `results/b1_independent_label_roc.csv`、`b1_independent_calibration.csv`，但**不改旧数字**。

---

## 3. B2 适用范围与 power 机理

**证据**
- `results/nc80_mj_kang_modular_raw.csv`(595,136 B)、`_tpr.csv`(1,573 B)、`_metrics.json`(4,196 B)、`_summary.csv/.txt`；脚本 `notebooks/nc80_mj_kang_modular_tpr.py:33-36,386-416`、`nc80_mj_kang_modular_summary.py:26-54`
- n 网格：`nc80_mj_kang_modular_metrics.json` 的 `n_grid = [50,100,200]`、`delta_grid = [0.25,0.5,1.0]`；ω AUC 0.513→0.507→0.534、TPR@FPR5% 归零
- 更早 power 归零证据：`results/competitors_v44_power.csv`(191,884 B)、`_power_summary.json`（n=50/100/200/500/1000，B 细胞 power 0.842→0.680→0.167），脚本 `notebooks/101_competitors_v44.py`
- 机理已写入 SI：`68_gen_supplementary_nc.py:2178-2238`（Section 3.11）、`:3802-3881`（E_b/C_bf 结构下界）

**写稿口径**：R1 P0-2 要求「收窄适用范围 + 给统计机理」——把已有 n 网格/power 曲线与「HK 面板稀释 → k_n 下降 → 比值把 k_total 看到的变化除掉」的机理**从 SI 提到主文 Results/Limitations 各一句**，并把标题/摘要的普适口吻收窄。零新脚本。

**可选新增**：「大图谱 pseudobulk 替代推断」全库无对应脚本；若做会**新增或可能下调** Section 3.11 的 10x pooled AUC 0.51–0.53 表述，需新脚本。

---

## 4. B3 增量价值判定

**证据**
- `results/nc60_paired_dauc.csv`(1,254 B)：5 组配对 DeLong，`ω − k_f` ΔAUC = **+0.0883**、P = 2.39e-17；`ω − k_total` +0.1640、`ω − cosine` +0.2200
- `results/nc60_mcnemar_t1.csv`(1,078 B)、`nc80_mcnemar_t1_studentized.csv/.json`；生成器 `results/audit/_nc60_paired_stats.py`、`_nc80_mcnemar_library_studentized.py`
- `results/nc52_stats_auc_ci_methods.csv`(8,907 B)、`nc52_stats_omega_vs_kf_realdata.csv`、`kf_only_ordering.csv`、`augur_comparison_v45.json`、`competitors_v44_simulation.csv`
- Table 2c 源数据链：`68_gen_supplementary_nc.py:4536-4635` 读 `groundtruth_simulation_raw.csv`、`nc52_stats_auc_ci_methods.csv`、`nc60_paired_dauc.csv`；DeLong 实现 `scripts/nc52_stats_resampling.py:239-352`

**写稿口径**：R1 P0-3 要「预注册成功标准、展示 ω 严格优于 k_f-only 与至少一种现有方法」。已有配对 DeLong 对 k_f/k_total/cosine/raw JS 全部显著——**「至少一种现有方法」已满足**；但 ω 对 Augur/MELD 只是并列比较而非配对检验。诚实处置有两条：
- (a) 写一段「预注册式成功标准 + 已满足项 + 未满足项（ω 在 10x 浅测不优于 k_f）」，把论文定位为「k_f/k_n 分解的诊断性 caution」；
- (b) 若坚持「新指标优越性」，则必须补做真配对 benchmark（新分析）。

**建议 (a)**，与 nc84 已落地的诚实降级一致，且不需要新数据。

---

## 5. B4 ambient / PMI 敏感性（唯一需要作者定夺）

**按字面为什么不可做**
- 原始 h5ad 在本地：`data/brain/Nonneurons.h5ad` **4.48 GB**、`data/human_brain_atlas_microglia.h5ad`(351 MB)，但**无 .loom / 无内含子-外显子计数矩阵**
- **明确无 PMI/RIN**：`notebooks/nc52_brain_extract.py:17-21` 记 obs 只有 ontology/dissection/donor/roi/sample；唯一 RIN 文件 `results/nc78_gdc_rin.csv` 属 TCGA GDC，非尸后脑队列
- `requirements.txt` / `requirements-lock.txt` 无 SoupX / CellBender / DecontX / scvi / rpy2 / R

**可行 proxy（已产出部分结果）**
- `results/nc52_brain_quality_classlib.csv`（`mean_detected`、`mean_total_counts`）
- `nc52_brain_quality_mito_classlib.csv`（`mean_mito_frac`）
- `nc52_brain_quality_regression_classlib.csv`（R² 0.208→0.225、T3 0.4924→0.469、gradient 6.10→6.33/6.45）
- `nc52_brain_gradient_donor_bootstrap.csv`

**代价**：用 depth/UMI/mito 分层或回归重算 k_n 与 **3.66-fold / 6.10-fold 梯度**会改 Abstract、Results、SI Note 11 的数字；`99_build_nc_v49.py:303,471-473,672` 有硬编码校验，必须同步。需 1 个新脚本，预期 `results/b4_ambient_proxy_kn_sensitivity.csv`、`b4_gradient_proxy_adjusted.csv`。

**需作者定夺**：(i) 接受 proxy 路线并接受数字改动（另起 v0.6.6）；(ii) 只以文字让步披露限制、不重算（保持现有数字）；(iii) 寻求外部带 PMI/RIN 的尸后脑队列（本环境不可得）。

---

## 6. B5 k_n floor 敏感性

**证据**
- TCGA pair table：`results/tcga_linear_norm_v44_all_pairs.csv`(4,380,343 B，列 `pair_type,cancer,sample_a,sample_b,kn,kf,omega_floor,omega_raw`)、`nc52_tcga_softmax_all_pairs.csv`(3,705,628 B)、`phase34_v2_all_pairs.csv`
- 实现：`notebooks/06_phase34_v2.py:289,305,324` 三处 `kn_floor=1e-4`；`cki/core.py:293-294`（默认 0，仅 TCGA 启用）
- **敏感性已算完**：`notebooks/nc52_tcga_knfloor_sensitivity.py:39-40,70-101`（`FLOORS=[0,1e-5,1e-4,1e-3]`）→ `results/c52_tcga_knfloor_sensitivity.csv`(2,788 B)

**数值结论**：linear mapping 在 1e-4 下触底比例几乎全 0（仅 KIRC `frac_NN_at_floor = 0.0003`）；floor=0 与 1e-4 的 NN/TT **完全一致**（LUAD 2.464、LUSC 1.7077 …），去 floor 稳健；1e-3 才出现大幅截断（BRCA 反转 0.9095）。

**写稿口径**：R3 P1-5 要「触底比例 + 去 floor 稳健性」——直接引用上表，一段 SI 新增即可，**零新脚本、零数字改动**。注意 `results/c52_stats_omega_kf_math_floor.csv` 是置换相关性下界（数学 floor），与 kn_floor 非同一概念，勿混用。

---

## 7. 建议执行顺序

| 阶段 | 内容 | 版本影响 |
|---|---|---|
| **第 1 步（零新脚本）** | B5 → B3 → B2 → B1：从既有 CSV 取数，写成 SI 新增 Notes + 主文各一句限定 | 仅加文字，词额顶格需压缩；不动任何数字 |
| **第 2 步（可选，1 个新脚本）** | B1 的 TMS/SEA-AD 二分类 ROC + 校准 | 新增证据，不改旧数字 |
| **第 3 步（需裁定，1 个新脚本）** | B4 proxy 重算 k_n 与梯度 | **改数字**，必须另起版本并同步 build 硬编码断言 |

**关键提示**：MAIN 现为 5,151 空格分词（团队声明口径 5,000，顶格）。第 1 步的写稿必须**先做词额配平**或把新增内容全部放进 SI（SI 无硬词额）。第 3 步因改数字，不宜与 A 类 v0.6.5 合并。

---

## 8. 与 nc85 判定的关系

nc85 均值 6.050、1 Reject + 5 Major，主编判定「继续加限定语不会抬分，可能继续压低影响力/证据分」。B 类的价值在于**用独立证据替换自我披露**：B1 把「循环论证」变成真实扰动标签的正面证据，B3 把「ω 不优于 k_f」变成有预注册标准的判定，B5 把「floor 未测」变成已算完的稳健性。B4 是唯一可能实质抬分但需要新数据的项。
