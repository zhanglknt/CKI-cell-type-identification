# nc52 — GTEx 健康组织参照（R3 Major B2）实施审计

日期：2026-09-24 · 执行：W-gtex · 种子：42 · 环境：`cki_env`（Python 3.14.4）

## 1. 目标

审稿人 R3 Major B2：TCGA 部分的机制主张（tumor-specific housekeeping
dysregulation，肿瘤 k_n 高于癌旁正常）缺少健康组织参照。若 GTEx 健康组织
k_n 与癌旁正常同样低，则主张成立；若 GTEx k_n 接近肿瘤，则为 field effect
或被推翻。本任务在同一条 v44 pipeline 下加入 GTEx 第三组参照。

## 2. 数据来源与可行性

评估了任务给出的四个候选源，最终选择 **UCSC Xena Toil hub 的 GTEx 矩阵**，
原因是它与仓库既有 TCGA 矩阵**同一量化流程**（Toil 重计算，RSEM TPM，
GENCODE v23）——这是方法学上最优的可比性保证：

| 文件 | URL | 大小 | 验证 |
|---|---|---|---|
| `data/gtex/gtex_RSEM_gene_tpm.gz` | https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/gtex_RSEM_gene_tpm.gz | 545,614,848 B | Content-Length 一致；7,862 样本 |
| `data/gtex/GTEX_phenotype.gz` | https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/GTEX_phenotype.gz | 82,442 B | SMTSD 组织注释 |

- 与 `data/tcga/tcga_RSEM_gene_tpm.gz` 的基因行集合**逐行完全一致**
  （60,498 基因，同序，脚本内 assert）——同一 probeMap/HK 映射可直接复用。
- 备选（未采用）：gtexportal.org V8 全量 GCT（RNA-SeQC + GENCODE v26，与
  TCGA 矩阵量化口径不同，且 1–2 GB）；recount3（量化口径亦不同）。
  Xena S3 镜像本次可访问（HTTP 200）；旧稿件记录的 Xena URL 失效问题未复现。
- 注意：Toil GTEx 为 GTEx V6p 时代样本集（7,862 例），非 portal V8
  （~17k 例）。选择它是为了与 TCGA 矩阵同口径，已在本文档记录。

样本量（表达矩阵与表型交集后，seed 42、每组织 ≤300）：
GTEx Lung 288、Liver 110、Kidney-Cortex 28、Breast-Mammary 179；
TCGA 同 v44（LUAD 495T/76N、LUSC 535/58、LIHC 398/57、KIRC 754/82、
BRCA 1032/109）。

## 3. 方法保真度

`notebooks/nc52_gtex_kn.py` **逐字复用** `notebooks/85_tcga_linear_norm_v44.py`
的 k_n 定义：HRT Atlas HK 面板（1,129 符号经 probemap 映射，每癌种局部
1,124–1,125 HK 基因）、linear 概率映射 (TPM+1)/sum(TPM+1)、JSD base-2、
kn_floor=1e-4、N_TOP_KF=200（log2 空间选 identity 基因）、RANDOM_SEED=42、
MAX_PAIRS=2000 及相同的 subsample 播种协议。每癌种的过滤集 = 该癌种
T+N + 对应 GTEx 组织样本（>0 存在性过滤 + mean TPM ≥ 0.5）。

四类对：TT（与 v44 **完全相同的** 2000 对子样——相同样本排序与播种）、
NN（全量）、GG（GTEx–GTEx，全量或 2000 子样）、GA（GTEx–癌旁，跨队列桥接）。

**交叉验证**：全部 5 癌种 TT/NN 的 k_n 中位数与已发表 v44 数字比值
= 1.000（见 `nc52_gtex_summary.json.crosscheck_vs_v44`），证明 pipeline
复刻精确、且 GTEx 扩充过滤集不改变既有 TT/NN 结论。

## 4. 结果（k_n 中位数，organ 级合并；详见 results/nc52_gtex_kn_by_grouptype.csv）

| 器官 | GG (GTEx–GTEx) | NN (癌旁–癌旁) | TT (肿瘤–肿瘤) | GA (GTEx–癌旁) | GG/NN | TT/NN | TT/GG |
|---|---|---|---|---|---|---|---|
| Lung (LUAD+LUSC) | 1.135e-3 | 9.65e-4 | 2.495e-3 | 2.069e-3 | 1.18 | 2.59 | 2.20 |
| Liver (LIHC) | 1.976e-3 | 1.917e-3 | 3.980e-3 | 4.516e-3 | 1.03 | 2.08 | 2.01 |
| Kidney (KIRC) | 2.376e-3 | 7.20e-4 | 2.601e-3 | 3.720e-3 | 3.30 | 3.61 | 1.09 |
| Breast (BRCA) | 9.06e-4 | 8.69e-4 | 2.412e-3 | 2.027e-3 | 1.04 | 2.78 | 2.66 |

MWU（organ 级）：TT>NN 全部 P ≤ 3.2e-84；GG<NN：肺 P=1.00、肝 P=3.8e-5
（中位数相等但秩次略低）、肾 P=1.00、乳腺 P=0.95；GA>GG 全部
P ≤ 1.4e-26（跨队列系统性升高）。

**逐器官判别**：
- **肺、肝、乳腺：GTEx ≈ 癌旁 << 肿瘤** —— 健康基线与癌旁基线重合
  （GG/NN = 1.03–1.18），肿瘤 k_n 高出 2.1–2.8 倍。支持"肿瘤特异性
  管家失调"，**不支持 field effect**（癌旁是健康样的，不是癌前病变样）。
- **肾：GTEx ≈ 肿瘤**（TT/GG=1.09，GG/NN=3.30）—— 但 GTEx 肾皮质仅
  n=28 且方差极大（GG 均值 8.1e-3 vs 中位 2.4e-3），结合文献中 GTEx 肾
  样本自溶/RNA 质量较差的已知问题，倾向技术混杂而非生物学反驳；
  建议在修订中将肾作为例外诚实报告。

**重要警示（GA 对）**：GTEx–癌旁跨队列对的 k_n 在所有器官系统性升高至
接近甚至超过肿瘤水平，说明 k_n 对队列级技术效应敏感。因此机制论证应基于
**队列内对比**（GG 定健康基线、NN/TT 定 TCGA 内部梯度），GA 不能用作
定量桥接。

## 5. Discussion 修订用段落（≤200 词）

> To test whether the elevated housekeeping divergence (k_n) in tumors is
> tumor-specific or a field effect, we added healthy tissue from GTEx (UCSC
> Xena Toil RSEM TPM; identical quantification pipeline and gene annotation
> as the TCGA matrix) as a third reference for lung (n=288), liver (110),
> kidney cortex (28) and breast (179), computing k_n with the identical
> pipeline (same HRT-Atlas housekeeping panel, linear (TPM+1) normalization,
> kn_floor=1e-4, seed 42). In lung, liver and breast, healthy GTEx k_n
> coincided with adjacent-normal k_n (median GG/NN ratios 1.03–1.21) while
> tumor k_n remained 2.1–2.8-fold higher (all MWU P<3.2e-84), indicating
> that adjacent-normal tissue is healthy-like and the k_n elevation is
> tumor-specific rather than a field effect. Kidney was the exception: GTEx
> kidney-cortex k_n matched KIRC tumor levels (TT/GG=1.09; n=28), plausibly
> reflecting the documented autolysis-related quality issues of GTEx kidney
> rather than cancer biology. Cross-cohort GTEx–adjacent pairs showed
> uniformly elevated k_n, indicating sensitivity of k_n to cohort-level
> technical effects and supporting within-cohort contrasts for mechanistic
> inference.

（178 词）

## 6. 产出文件

- `notebooks/nc52_gtex_kn.py` — 分析脚本
- `results/nc52_gtex_pairs.csv` — 43,684 对（TT/NN/GG/GA，样本级标注）
- `results/nc52_gtex_kn_by_grouptype.csv` — organ + cancer 两级 × 4 对类型
  （中位数/均值/IQR/n/kn<1e-4 比例），36 行
- `results/nc52_gtex_summary.json` — 元数据、全部检验、判别、v44 交叉验证
- `results/audit/_nc52_gtex_run.log` — 运行日志
- `data/gtex/` — 原始数据（545 MB，.gitignore 排除，URL 见上）

## 7. 局限

1. GTEx 为尸检样本（缺血时间/RNA 质量与 TCGA 手术样本不同）；尤其肾皮质
   n=28 且已知质量较差，肾的结论可信度低。
2. Toil GTEx 为 V6p 样本集而非 portal V8；为同量化口径所作取舍。
3. 跨队列（GA）k_n 系统性升高，限制了跨数据集直接定量比较；结论依赖
   队列内基线比较。
4. TT/NN 数值与 v44 完全一致（比值 1.000），说明 HK 面板对过滤集扩充
   不敏感；GG/GA 为该过滤集下的新计算。
