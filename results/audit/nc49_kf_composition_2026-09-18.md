# 审计：k_f 组成校正 + TT 面板 Hallmark 富集（R2-P1-1 收尾）

- 日期：2026-09-18
- 脚本：`notebooks/nc49_tcga_kf_composition.py`（seed 42）
- 输出：`results/nc49_tcga_kf_composition.csv`；日志 `_tmp_fa_review/_nc49_kf_composition_log.txt`
- 问题来源：R2 盲审 P1-1（k_f 未做组成校正 + k_f 面板语义未检验）

## (a) k_f 组成校正（ESTIMATE admix 协变量）

### A1 对级回归：log metric ~ is_TT + admix_mean + |Δadmix|（TT vs NN 合并，逐癌种）

| 癌种 | k_f 未调整 log gap | k_f 调整后 [P] | k_n 未调整 | k_n 调整后 [P] |
|---|---|---|---|---|
| LUAD | +0.238 | **+0.208** [8.2e-80] | +1.077 | +0.991 [~0] |
| LUSC | +0.551 | **+0.534** [1.1e-264] | +0.930 | +0.619 [9.7e-159] |
| LIHC | +0.539 | **+0.530** [3.6e-250] | +0.566 | +0.485 [3.6e-82] |
| KIRC | +0.479 | **+0.599** [2.0e-293]（增大） | +1.188 | +1.303 [~0] |
| BRCA | +0.827 | **+0.824** [~0] | +0.993 | +0.856 [~0] |

**「TT k_f ≥ NN k_f」在 5/5 癌种经 admix 组成校正后保留**（幅度几乎不动；KIRC 反而增大）。该回归与 Discussion L81 的 4-marker 组成回归同族，但用 ESTIMATE admix 作为组成协变量，直接回应「k_f 未做组成校正」。

### A2 逐肿瘤 k_f ~ admix：5/5 癌种显著负相关（r = −0.15 ~ −0.27，P ≤ 1.2e-6）

k_f 统计上受组成影响（混杂多 → k_f 略低），但方向与量级（r² 2–7%）不足以解释组间差。

### A3 LUAD k_f ~ group + admix_z（与纯度审计一致复核）

KRAS−WT +0.0124 (P=0.0092)、KRAS−EGFR +0.0172 (P=0.0129)、EGFR−WT −0.0048 (P=0.44 NS) —— **KRAS k_f 功能成分经组成校正后保留**。

## (b) LUAD KRAS-KRAS TT top-200 面板 Hallmark 富集

- 面板重算：verbatim 镜像 85（单癌种流式载入 LUAD 571 样本 → 36,334 合格基因 → mean≥0.5 过滤 14,178 → HK 排除 1,125 → log2 表示 top-200 |Δ|）。KRAS 肿瘤 121 例（表达矩阵口径），**全部 7,260 个 KRAS-KRAS 对**。
- 面板高度异质：最高频基因仅 49%（RPS4Y1 49%、XIST 48%、GSTM1 47%——性染色体连锁与多态/分泌标志物居前）；≥50% 面板共享基因 <50 个，故按规则回退取频次 top-300 为核心面板。
- 富集（超几何，背景 = 13,031 个非 HK 过滤基因，BH 校正）：

| 排名 | Hallmark 程序 | overlap | P | q(BH) |
|---|---|---|---|---|
| 1 | Estrogen Response Late | 10/165 | 4.9e-3 | 0.24 |
| 2 | KRAS Signaling Down | 5/69 | 0.021 | 0.53 |
| 3 | Myogenesis | 7/141 | 0.045 | 0.74 |
| 4 | Estrogen Response Early | 7/169 | 0.096 | 1.00 |
| 5 | Epithelial Mesenchymal Transition | 7/178 | 0.117 | 1.00 |

**判定：无程序通过 FDR（全部 q ≥ 0.24）。** KRAS TT 面板在 Hallmark 层面不解析为单一肿瘤内在程序；其高频成员以个体间高变/性连锁/分泌型标志物为主——支持「bulk k_f 测量的是广谱组织状态分歧」的语义界定，但**不构成**「k_f 纯由免疫/间质污染驱动」的证据（与 (a) 中 k_f 组间差经组成校正保留一致，两者互补）。

## Hallmark 取舍结论（lead 任务要求二选一）

**走了「做富集」路径**：MSigDB Hallmark 2020 经 Enrichr 镜像成功获取（`data/tcga/hallmark_2020.gmt`，50 集，来源 `maayanlab.cloud/Enrichr MSigDB_Hallmark_2020`，2026-09-18 下载）。**无需删除 Data availability 悬空条目**；建议该条目与文献 [56] 的落点改为「MSigDB Hallmark gene sets (Liberzon et al. 2015), accessed via the Enrichr gene-set library」。

## 给 c-drift 的建议文本（语义界定句，一句版）

> Enrichment of the LUAD KRAS tumour–tumour identity panels (7,260 pairs, top-200 genes per pair) against the 50 MSigDB Hallmark programmes yielded no programme surviving multiple-testing correction (top: Estrogen Response Late, q = 0.24); the recurrent panel members are dominated by individually variable, sex-linked and secreted markers, indicating that bulk k_f measures broad tissue-state divergence rather than a single tumour-intrinsic programme — while the KRAS k_f association itself is not explained by stromal/immune admixture (pair-level composition regression: adjusted log gap +0.21, P = 8 × 10⁻⁸⁰; group ANCOVA: Δk_f = +0.012, P = 0.009).

## 限制

- 面板聚合为「全部 KRAS-KRAS 对」而非 85 的 2000 对种子子样本（后者为计算量的下采样，面板语义不受影响）；KRAS 肿瘤 121 例为表达矩阵口径（对表口径 120，差 1 例为无配对样本）。
- 核心面板阈值采用文档化回退规则（≥50% 共享不足 50 基因 → 频次 top-300）；BH 结论对阈值选择稳健（原始 P 均弱）。
