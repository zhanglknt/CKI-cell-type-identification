# 审计：KRAS−WT ω 量级分解（R2-P1-2 收尾）

- 日期：2026-09-18
- 目的：xv-text 发现「KRAS−WT ω 升高大部分来自 k_n 下降」量级句与 Dunn k_f P=0.097 NS 在修复轮被整句删除（评审要求的是补全而非删除）。此处从原始对表重算全精度数字，供 c-drift 补回。
- 数据来源：`results/tcga_linear_norm_v44_all_pairs.csv`（LUAD TT，逐肿瘤均值重算，全精度）+ `results/nc49_tcga_luad_mutation.csv`（Dunn/bootstrap 数字核对）

## 组均值（全精度）

| 组 | n | ω | k_f | k_n |
|---|---|---|---|---|
| WT | 311 | 115.3734 | 0.28136 | 0.003217 |
| EGFR | 61 | 122.2156 | 0.27322 | 0.002800 |
| KRAS | 120 | 136.9436 | 0.29189 | 0.002654 |

## 分解（成分均值口径，与 R2 复算一致）

- 观测 ω 比 KRAS/WT = 1.1870（log 0.1714）
- k_f 比 = 1.0374（log +0.0367）
- k_n 比 = 0.8248（**k_n 下降 17.5%**，log −0.1926）
- 成分均值 log-ω 增量 = 0.2293
- **k_n 贡献份额 = 84.0%**（R2 报告的 ~85% 复核一致）；k_f 贡献份额 = 16.0%
- 注：成分均值积（0.2293）与观测 ω 对数差（0.1714）不一致属正常的均值不可复合性（Jensen），分解按成分均值口径报告，与 R2 相同。

## 显著性口径（与 CSV 逐项核对）

- 未调整：Dunn-Holm k_f **WT vs KRAS P=0.0969（NS）**；bootstrap 均值差 k_f KRAS−WT +0.0105，CI95 [0.0024, 0.0192]（不含 0）；k_n WT vs KRAS P=4.2e-4；k_f 功能成分主要由 KRAS vs EGFR 承载（P=0.0146）。
- **纯度调整后**（nc49_tcga_purity.csv，OLS metric~group+admix_z，n=492）：k_f KRAS−WT +0.0124, **P=0.0092**；k_n KRAS−WT −0.0004, **P=0.0029**；ω KRAS−WT +16.83, P=4.0e-6。
- **吸烟调整后**（nc49_tcga_luad_smoking.csv，n=427）：k_f KRAS−WT +0.0097, P=0.043；联合纯度模型 +0.0099, P=0.029。

## 给 c-drift 的建议文本（两句并存版，量级分解 + 调整后显著性）

> The unadjusted KRAS–wild-type elevation in ω is dominated by the housekeeping baseline: the k_n decrease (0.00322 → 0.00265, −17.5%) accounts for ~84% of the log-ω increment, with the k_f component contributing the remaining ~16% (Dunn–Holm k_f KRAS vs wild-type P = 0.097 unadjusted; bootstrap mean difference +0.0105, 95% CI 0.0024–0.0192). After adjustment for tumour admixture, however, both components of the KRAS association became individually significant (Δk_f = +0.012, P = 0.009; Δk_n = −0.0004, P = 0.003), a result unchanged by further adjustment for smoking status (Δk_f = +0.010, P = 0.029).

要点：第一句如实保留 R2 要求的量级限定（84% 分母主导 + Dunn NS + bootstrap CI 边界）；第二句给出修复轮新结果（调整后双成分显著），两句逻辑兼容——「未调整时分母主导」与「调整后双成分显著」不矛盾，后者正是纯度混杂（EGFR 高混杂伪影）被移除后的更干净估计。

## 判定

量级句按原数字补回即满足 R2-P1-2；建议同时带上调整后句子（比单独补回更强，且不夸大——调整后 P 值均来自正式 CSV）。
