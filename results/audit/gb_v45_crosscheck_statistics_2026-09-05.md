# v45 交叉验证报告（统计学）—— v44 P1/P2 核销

- **核销人**: r-statistics（v44 盲审 7.5/10，Minor Revision；报告 results/audit/gb_v44_blind_review_statistics_2026-09-05.md）
- **核销对象**: version3/CKI_Submission_v45/（对照 results/cluster_boot_v45_report.md、results/ratio_estimator_biasvar_v45_report.md、MANIFEST_v45.txt、本地 cki v0.4.8 源码）
- **日期**: 2026-09-05｜**方式**: 只读独立复核，含独立重算；未修改任何投稿文件

## 核销结论总表

| 条目 | 判定 | 证据要点 |
|---|---|---|
| P1-1 比值估计量偏差-方差 | **CLOSED** | 新增 SN 3.20；分裂半零假设下偏差中位 +0.2%（最差分箱 k_n<1e-4：+6.5%），delta 法预测 ρ=0.99/1.00；稳健摘要 6.10/6.00/6.09；近零 k_n 排除后梯度升至 6.52 |
| P1-2 少 cluster bootstrap 区间 | **CLOSED** | Monte Carlo 覆盖率研究（2,000 模拟 × B=999）：百分位 0.876/0.873（欠覆盖 7-8pp）、wild 0.816/0.806、studentized bootstrap-t 0.953/0.951；替换区间梯度 [4.43, 7.69]、Bergmann [5.76, 28.59]（降级为定性）、choroid [25.93, 76.30]（声明保留） |
| P1-3 反富集提升与条件性 P 值 | **CLOSED**（附观察项） | 反富集（148.3 vs 39，P=1.0）置于候选节开篇（正文 L68）、小结（L78）与 Figure 6D 图注；hit-rate P 值明确标注"not valid post-selection P values"；Results 8,908→6,457 词。观察项：摘要仍只写"no pair survived correction"；figure6.pdf 图形本体未改（sha256 与 v44 完全相同，仅图注更新） |
| P1-4 大 n 功效崩溃呈现层级 | **CLOSED** | 摘要 Conclusions 含"practical window of ~50–200 cells per donor per condition"；Limitations 专段；本地源码 cki/bootstrap.py:481-489 实测存在 n>500 UserWarning（v0.4.8，pyproject 已核实） |
| P2-1 小样本 bootstrap CI | **CLOSED** | 正文改为观测范围（S: 8.8–42.8; D: 30.1–61.7; X: 23.0–31.6），明示"calibration-scale estimates"；figure2 为箱线图无 CI 条（sha 未变，无需改图） |
| P2-2 ω_cal 精度约定 | **CLOSED**（附注） | 正文与 SN 3.5 均声明"at most two significant figures"，数值已统一（≈5/11/1.8/1.4/8.5/8.9）。附注：SN 3.5 同段残留"omega_cal ≈ 1.39"三位有效数字，与自身约定矛盾（正文为 ≈1.4），纯编辑问题 |
| P2-3 成分校正 B=200 | **CLOSED**（接受论证） | B=200 未改，但 SN 5.2 新增端点 Monte Carlo 误差论证（≈1-2pp，远小于区间宽度 6-24pp）并将 pooled 区间解释为"仅排除大的 pooled 衰减，不作精确点估计"；per-cancer 异质性完整呈现。该 MC 误差为断言未展示，但量级合理，作为 P2 接受 |

## 独立重算结果

1. **mouse split-half 基线**（results/mouse_splithalf_v44.csv，omega 列）：n=300，**mean = 7.6958 ≈ 7.70** ✓；原始值中位 7.065——MANIFEST/图 1C 的"Median 7.69"指 bootstrap 均值分布的中位（图注表述正确："Bootstrap distribution of the mean… median… dashed line"），无误读风险。
2. **cluster_boot_v45.json**：报告全部数值逐一吻合——boot_t Bergmann [5.756, 28.592]、choroid [25.929, 76.301]、梯度 [4.430, 7.693]；覆盖率 0.876/0.873（percentile）、0.816/0.806（wild）、0.953/0.951（boot-t），MC SE 0.005–0.009，n_sim=2000、B=999 与报告一致。
3. **ratio_estimator_biasvar_v45.json**：pooled E[ω]=9.726 ↔ 报告 9.73；skew 2.217 ↔ 2.22；excess kurtosis 6.015 ↔ 6.02；min k_n 9.228e-5 ↔ 9.23e-5。9.726/9.90−1 = −1.76% ↔ pooled bias −1.8%，内部自洽。
4. **图形文件**：figure6.pdf 与 figure2.pdf 的 sha256 在 v44/v45 完全相同（c73cda3d…/ad4d92ac…），即修复均为文本/图注层面；图注内容已核实携带反富集与 equal-n 声明。
5. **包级护栏**：cki/bootstrap.py:481-489 实测存在 ">500 cells UserWarning（operating window ~50–200）"；非有限零值护栏警告亦在；pyproject version = 0.4.8。

## v45 新增分析的统计健全性（回归检查，非核销项）

- **N1/N2 非 HK 锚定中性漂移对照（SN 3.22）**：设计合理——N1 用表达匹配的低方差非 HK 集（CV 下半 + 对数均值贪婪匹配），ω FPR ≤ 0.067 vs raw JS/cosine 0.81–1.00，正确区分了"特异性来自比值结构"与"HK 锚定伪影"；N2 全指标 FPR=1.00 的解读（identity reassignment 非中性）措辞审慎。摘要相应表述准确。无回归。
- **Augur 对照（SN 3.23）**：以"多分类 AUC 与 eligible-region 数相关（ρ=−0.744, P=0.014）"为由弃用多分类变体、以 binary OvR 为主分析，混杂控制逻辑正确；n=10 的 ρ=0.442 (P=0.200) 明确标注 descriptive only。无回归。

## 残留次要问题（不影响核销，供下一轮编辑参考）

1. SN 3.5 残留 "omega_cal ≈ 1.39"（三位有效数字）与该 Note 自身"at most two significant figures"约定矛盾；正文为 ≈1.4。
2. 正文 Results（L51.2）引用 v44 线性归一化成分分析（−0.8% [−4.1, +2.6]），Discussion（L85.2）引用旧 softmax 四面板分析（−0.5% [−3.2, +2.6]）——两套数字并存于 SN 5.2（主分析+v44 update），建议统一主分析版本或在 Discussion 括注来源。
3. SN 3.5 的 v45 更正以追加段落形式自我纠偏（先引旧百分位区间再声明过窄），逻辑完整但阅读体验略迂回；可在下一轮直接替换旧区间。

## 总体评分

**8.5 / 10**（v44：7.5 → v45：+1.0）

四条 P1 全部 CLOSED 且修复质量高：P1-2 的 studentized bootstrap-t + 覆盖率验证是教科书级的小 cluster 修正，并用诚实的代价（区间加宽、Bergmann 声明降级）换取了名义覆盖；P1-1 用分裂半零假设干净地分离了纯比值偏差并证明其被校准基线吸收；P1-3/P1-4 的呈现层级修复到位。三条 P2 全部 CLOSED（P2-3 为接受作者的 MC 误差论证）。新增 N1/N2 与 Augur 分析设计健全、无过度声明。残留问题均为编辑层面（有效数字、成分分析版本统一、图形本体未嵌入反富集标注）。**建议判定：Accept（余留纯编辑性微调，无需再审）。**
