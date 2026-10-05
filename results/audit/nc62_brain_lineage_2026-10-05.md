# nc62 — 选项 B：脑图谱少突谱系链深入验证（离线，全程未动稿件）

**日期**：2026-10-05
**任务**：用户裁定「先把 B 做了看下结果」——在 Siletti 全脑非神经元图谱上检验 CKI 指标 vs CL 谱系距离，重点：OPC→committed OPC→oligodendrocyte 谱系链。
**裁定**：**信号确认（同向），且比选项 A 更锐利地证明 k_f（而非 ω）是谱系距离的可移植载体**；但 k_n 行为在脑设计中反转（随距离上升），分箱阶梯不如选项 A 干净。**全程未动任何稿件文件。**

---

## 1. 设计与数据源

| 项 | 值 |
|---|---|
| 数据 | `data/brain/Nonneurons.h5ad`（Siletti et al. 2023，888,263 核 × 59,480 基因，CSR int16） |
| 分组 | 10 个 supercluster 非神经元 CT × 108 脑区（ROI）；主分析 9 CT（排除混合 Vascular），敏感性 10 CT |
| 对设计 | 同脑区 × 跨 CT：n=1,537（主；≥20 核/组过滤）/ 2,032（含 Vascular 敏感性）；dist-0 锚点=同 CT 跨脑区 31,764 对 |
| 口径 | **严格复刻 MS 权威 08c 管线**（`notebooks/08c_brain_bootstrap_v3.py`）：HRT HK 经 var.Gene symbol 映射（1,115 个）+ top-5,000 非 HK（raw 全局均值）→ 组 raw 均值 pseudobulk → /sum×1e4 → log1p → JSD |
| CL 距离 | 同 nc61：is_a + develops_from 父→子边，LCA 深度法（无向最短路径） |
| CT→CL 策展 | 图谱自带 CL 标注有缺陷（COP 与 Oligo 同标 CL:0000128；Microglia 标 CNS macrophage CL:0000878）→ 人工映射 10 条（OPC=CL:0002453、COP=CL:4023059、Oligo=CL:0000128、Microglia=CL:0000129、Vascular=CL:0000115，余取图谱多数标注） |

**复现认证**：本管线对 MS 权威 `brain_bs_null_observed_pairs.csv`（31,764 对 dist-0）重算 ω：**31,764/31,764 全匹配，median |Δω|=1.28e-6，max 7.0e-5，Pearson=1.0** —— 与 MS 脑区数字完全等价。
**口径教训**：旧版 `07_brain_siletti_analysis.py`（per-cell lognorm + 数据驱动 combined HK）对 888k 异质核只检出 9 个 HK 且 HRT 参考因 Ensembl var_names 静默 0 匹配；per-pair top-200 k_f 在跨 CT 对上饱和（~0.53）。nc62 初版复刻 07 口径失败，鉴别出 brain_bs_null 系列实为 08c 口径后整重写，并引入**双 k_f 变体**（pp200 认证用 / fixed 主指标）。

## 2. 主结果（n=1,537，同脑区跨 CT）

| 指标 | Spearman ρ(vs CL dist) | P | 备注 |
|---|---|---|---|
| **k_f（fixed 5,000 基因）** | **+0.181** | **9.9e-13** | 与选项 A 同向同量级（A：+0.227） |
| k_f（per-pair 200，08c 原生） | +0.181 | 2.3e-12 | 口径稳健 |
| **k_n（HK 1,115 基因）** | **+0.300** | **2.1e-33** | **反转**：脑内 k_n 随谱系距离强上升（A 中平坦 +0.052 NS） |
| ω=k_f/k_n（fixed） | **−0.134** | 1.4e-7 | 因 k_n 上升更快，ω 随距离**下降** |
| ω｜k_n 偏相关 | −0.009 | 0.73 NS | k_n 混杂下 ω 的独立信号消失 |
| **脑区分层置换（B=10,000）** | k_f_fixed **P=1e-4** | — | 区内打乱 dist，观测 ρ 超全部置换 |

敏感性（含 Vascular CL:0000115，n=2,032）：ρ(k_f_fixed)=+0.177（P=9.1e-16）—— 稳健。

**分箱（k_f_fixed 中位数）**：1–2: 0.1378 / 3–4: 0.1361 / 5–6: 0.1361 / 7–8: 0.1412 / 9–40: 0.1262 —— 整体正相关但**非单调阶梯**（选项 A 的六级干净阶梯在脑全局层面未复现；驱动：最远箱含 microglia 对比以外的远缘对噪声）。N  pair 需区分：ρ 显著性来自全样本秩相关，非阶梯。

**dist-0 锚点（同 CT 跨脑区 31,764 对）**：k_f_fixed 中位 0.0059–0.0333（Oligo 最稳定 0.0059，Fibroblast 最高 0.033）—— 比最近缘跨 CT 对（OPC-COP 0.063）**低一个数量级**：类型内空间变异 ≪ 跨类型谱系分化，内部一致性极佳。

## 3. 少突谱系链（选项 B 核心命中）

CL 图（is_a+develops_from）：OPC(CL:0002453)→COP(CL:4023059) **无直连边**（develops_into 正向边未捕获，同 nc61 机制），dist=2（LCA=CL:0000123）；COP→Oligo dist=5（LCA=CL:0000095）；OPC→Oligo dist=5。

| 对 | CL dist | k_f_fixed 中位 | n（脑区） |
|---|---|---|---|
| OPC ↔ COP | 2 | 0.0629 | 52（COP 仅 4,720 核，≥20 核过滤后 52 区） |
| COP ↔ Oligo | 5 | 0.0746 | 52 |
| OPC ↔ Oligo | 5 | **0.1296** | 52 |

- 链内中位数**单调递增 0.063→0.075→0.130（2.06×）**；
- **52 个共有脑区逐区配对 Wilcoxon：OPC-Oligo 同时大于两段相邻对，52/52=100% 脑区成立，P=1.75e-10**；
- dist-2→dist-5 两段跨 CT 对仍全部 ≫ dist-0 锚点上界（0.033）。
→ **谱系分化层级（祖细胞→定向祖细胞→终末分化）被 k_f 逐区、逐对、单调地解析**——选项 B 的最强证据。

## 4. Microglia vs macroglia（胚层预测）

Microglia（中胚层/卵黄囊起源）↔ 全部神经外胚层 macroglia：k_f_fixed 中位 **0.163** vs macroglia 互比 **0.123**，MWU **P=4.5e-146** —— 胚层起源差异被 k_f 定量捕获，方向与发育生物学一致。

## 5. 与选项 A（TS 跨器官）对照

| 维度 | 选项 A（TS，跨器官×跨CT） | 选项 B（脑，同区×跨CT） |
|---|---|---|
| ρ(k_f, dist) | +0.227（P=9.5e-14） | +0.181（P=9.9e-13）—— **同向同量级** |
| ρ(k_n, dist) | +0.052 NS（平坦） | **+0.300（P=2.1e-33）—— 反转** |
| ω 行为 | 随距离升（偏相关 +0.265） | **随距离降（−0.134）** |
| 单调阶梯 | 六级干净台阶（0.102→0.271） | 整体正相关但非单调 |
| 谱系链 | — | **OPC→COP→Oligo 100% 脑区单调（P=1.75e-10）** |
| 胚层预测 | — | **microglia 显著更远（P=4.5e-146）** |

**机制解读**：脑内 CT 共享同一器官环境，谱系距离与 housekeeping 程序的保守性耦合（远缘 CT 连基础代谢/结构程序都分化），故 k_n 不再平坦；ω=k_f/k_n 的比值结构在两种设计间不可移植。**k_f 的分子（绝对分化程序距离）才是跨设计稳健的谱系信号载体** —— 这把 nc61 的「k_f 比 ω 干净」结论从「器官基线混杂」推广为普适论断。

## 6. Go / No-Go 裁定

**B 验证 GO（信号确认），但对稿件的增量价值为「强化既有结论」而非「新增独立叙事」**：

| 支撑点 | 强度 |
|---|---|
| k_f–谱系距离正相关跨设计复现（器官间 + 脑内） | 强（两个独立图谱同向） |
| 少突谱系链单调性（100% 脑区） | 强（机制级命中） |
| k_f 而非 ω 是可移植载体 | 强（B 的 k_n 反转提供了反面对照） |
| 干净单调阶梯（A 的卖点） | 弱（脑全局未复现，仅链内成立） |

**对稿件的选项（待用户定夺，本轮不动稿）**：
- **B1（最低成本）**：零新计算成文——SI Note 一节（~150 词）+ 链式图（3 对 k_f + CL dist），作为「k_f captures lineage distance」的脑内佐证；
- **B2（中成本）**：A+B 合并为一个 SI Note「Lineage-distance validation across atlases」（跨器官 + 脑内 + 少突链）；
- **B3（不动稿）**：仅留作 rebuttal 弹药（若审稿人质疑 k_f 生物学意义）。

## 7. 技术备忘

- 分块（50,000 行/块）单次遍历 1.97B nnz + 稀疏 one-hot matmul 聚合：104s 全量；内存峰值 ~2GB（int32 行索引 + 即时 codes 反解）。
- h5ad 新版 anndata 编码：obs/var 每列为 Group；categorical=Group{categories,codes}；X=CSR Group{data,indices,indptr}；`_index`（var）=Ensembl Accession，`Gene`=symbol categorical。
- 脚本：`results/audit/_nc62_brain_lineage.py`；输出 `results/nc62_brain_lineage_pairs.csv`（2,032 行含 Vascular 敏感性）+ `results/nc62_brain_lineage_stats.json`（均 gitignore 不入库）。
- COP 稀有（4,720 核）→ 少突链 Wilcoxon 限于 52 个 COP 达标脑区；结论对 ≥20 核阈值稳健性未系统扫描（如需可补）。
