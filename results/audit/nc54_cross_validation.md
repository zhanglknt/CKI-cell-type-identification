# nc54/v0.5.2 交叉验证报告（2026-09-25）

范围：nc54 微修轮全部改动数字 + 决策项 A（v0.5.2 发布链）/ B（摘要减重）落地状态的**独立复算**（不从分析 json 转抄，从原始输出重算）+ 稿面文本状态核验。
脚本：`results/audit/_v054_cross_validation.py`（可重跑，退出码非零即失败）。结果：**CROSS-VALIDATION ALL PASS**。

## 一、nc54 改动数字独立复算

| # | 项 | 复算方法 | 结果 |
|---|---|---|---|
| 1 | GTEx 肝 GG vs NN MWU（R1-N1/R3-m1） | `nc52_gtex_pairs.csv` 原始对级 k_n（GG n=2,000 / NN n=1,596）scipy mannwhitneyu 三方向重算 | alt=less **3.814e-05**（json 键 p_MWU_GG_lt_NN 一致）、alt=greater 0.99996、two-sided 7.628e-05 ✓ |
| 2 | 肝中位数重合 + 右尾 | 同数据直接算 median/mean | median GG 1.976e-3 / NN 1.917e-3 = **1.031**；mean NN 3.77e-3 > GG 2.38e-3（相邻组右尾更重）；empirical P(GG<NN)=0.538；json ratio_GG_NN=1.031 ✓ |
| 3 | fold 2.0–2.8（R2-C2） | `nc52_tcga_pancancer_excc.csv` kn_TT_NN_median_ratio + `nc52_gtex_summary.json` ratio_TT_GG / ratio_TT_NN | **该句稿面限定 lung/liver/breast**（kidney 例外另行披露）：ex-KIRC 四癌种 TT/NN [2.060, 2.778] ⊂ [2.0, 2.8] ✓；TT/GG [2.015, 2.661] ✓；BRCA 2.776 上限锚 ✓；KIRC 3.61 为例外（>2.8，稿面不在此句范围内）✓ |
| 4 | Fig 4a k_f NN/TT 口径（R3-m2） | excc CSV kf_TT_NN_mean_ratio + CI | 五癌种 k_f TT/NN 均值比全 >1 且 CI 下限全 >1（1.25/1.688/1.634/1.547/2.07）→ 原文 "while k_f does not" 字面为假的裁定成立，NN/TT 限定必要且已补 ✓ |
| 5 | ex-CC 组成口径（R2-m1） | `nc52_tcga_composition_excc.txt` 直接核对 | pooled att **−0.9%**；BOOT median **−0.8%** [−4.3%, +2.5%]（B=1,000）✓；xlsx Table 5 A1 表注同口径、旧 −1.3% 无存 ✓ |
| 6 | 38% 模拟标签（R2-C4） | `groundtruth_simulation_raw.csv` 从 baseline 重算 95 分位阈值再算 exceed rate | imbalance（n_b=N/4，脚本 226 行坐实 fourfold）δ=1：k_f **0.38**、ω **0.00**（n=50）✓ |

## 二、稿面文本状态（fresh fulltext，@e836493 工作树）

- MS 新串 11/11 在位（2.0–2.8-fold、NN/TT ratio of k_f、non-parenchymal fraction versus k_n、(simulation)、v0.5.2 ×3、concept-DOI-only 句、bounded-power discrimination、span- and size-matched、is available as）
- MS 旧串 5/5 清除（2.0–2.7-fold、22938380、v0.5.1、freely available、combined span-）
- SI 新串 4/4 在位（heavier adjacent upper tail、pair-independence 句、2.0–2.8-fold、v0.5.2×2+version 0.5.2×1）；旧串 3/3 清除（marginally above adjacent、2.0–2.7-fold、v0.5.1）
- 摘要 **196/200**（余量 4 词，proof 插入空间达成；决策 B 闭环）

## 三、验证矩阵（v0.5.2 phase-1，@fb782c9）

| 项 | 结果 |
|---|---|
| 构建断言 | 221/221（N48 断言同步 v54 措辞后归零失败） |
| ms_verify / si_verify | 127/127、121/121 |
| XV8 | 63/63（MAIN 4,999/5,000；摘要 196/200；Methods 2,918；图注 max 302） |
| pytest tests/ | 29 passed |
| spot_check | ALL PASS |

## 四、发布链状态（决策 A 处置）

| 环节 | 状态 |
|---|---|
| 版本面 | pyproject/__init__/MS/SI/Guide/Dockerfile 全 0.5.2（Dockerfile L6/L7 镜像标签同步，R6 外观项顺手关闭） |
| tag | v0.5.2 = fb782c9（注解提交），ls-remote 核对一致 |
| GitHub Release | id **396170102**；phase-1 资产 587110399 已替换 → phase-2 资产 id **587262273**（12,894,040 B，手稿含 version DOI），readback sha256 **1271fc40… MATCH**；Release body 已补 version DOI |
| Zenodo | webhook 202 Accepted（00:01:50Z）；version record **22949350**（v0.5.2，2026-09-25）已上线，version DOI **10.5281/zenodo.22949350**（轮询 34m41s 于第 18 轮捕获，期间 8 次 502 重试） |
| phase-2 | **已闭环**：MS Code availability 写回 version DOI（镜像 v0.5.1 句式 "concept DOI…; version DOI for v0.5.2: 10.5281/zenodo.22949350"）+ A15 断言恢复新 DOI → 重建 **221/221 + ms 127/127 + si 121/121** → zip 重建（手稿新旧 DOI 在/缺核验）→ Release 资产替换 readback MATCH → 提交推送 → 本报告补终态 |

## 五、结论

nc54 全部七项修复 + 摘要减重 + 版本面切换经独立复算**零失配**；交叉验证发现的问题全部判定为验证脚本自身 bug（肾癌例外适用范围、错列、行提取方式），稿面与数据零缺陷。v0.5.2 发布链四件套（tag / Release 资产 / Zenodo record / DOI 写回 + A15）已全部闭环，零开口。
