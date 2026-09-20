# NC v49 增强分析可行性报告：真实数据中的中性漂移对照（对策 C）

日期：2026-09-18　作者：c-drift（只读调研）
目的：把模拟中「ω 对中性漂移免疫」（FPR 0.00 vs raw JS/cosine 0.55–0.58）搬到真实数据：ground truth 为「无功能差异」的漂移场景，展示现有指标误报、ω 保持校准。

---

## 0. 核心结论（先读）

1. **两个干净的真实漂移场景可用且从未被本项目分析过**：
   - **Kang batch1 跨 lane 技术重复**（同 donor、同 ctrl 条件、不同 10x lane）：数据在 `GSE96583_RAW.tar` 中完整可读（`GSM2560245/46/47` 三个 `.mat.gz` 实为 MatrixMarket 格式），barcode 与 `GSE96583_batch1.total.tsne.df.tsv.gz` 逐 lane 对应（仅 93 个 barcode 需按 script 79 的 `-1→-11` 重命名规则处理）。
   - **Brain 同 (roi, donor) 跨 library 技术重复**（同一供体同一脑区的两次独立 10x library）：258/264 个 (roi,donor) 组合有 ≥2 个 library；按每 (细胞类型, library) ≥20 细胞过滤后，**10 个细胞类型共 2,161 个技术重复对**。
2. **既有 null 全部被混杂污染，不能作为「ω 已校准」的证据引用**（详见 §4 坑 1–3）；干净对照从未算过，因此「ω 在真实技术漂移下是否校准」目前是**开放问题**——这是本方向最大的科学风险，必须先用 1 天 pilot 把关。
3. 指标实现基本齐全：ω/k_f/k_n/raw JS/Spearman/cosine 现成，marker Jaccard 需要新的配对级定义（~20 行代码）。
4. **Tabula Sapiens 不适合做漂移对照**（无技术重复结构，donor 与 assay 方法完全混杂）。

---

## 1. 候选场景

### 场景 A（推荐主场景）：Brain library 级技术重复 + 漂移阶梯

- **数据文件**：`data/brain/Nonneurons.h5ad`（4.4 GB；实际为 Siletti 全量非神经元，888,263 nuclei × 59,480 genes——注意并非任务描述的 33k；10 个非神经元类）。
- **关键 obs 列（已实测确认存在）**：
  - `supercluster_term`（细胞类型，10 类：Oligodendrocyte 490k、Astrocyte 155k、OPC 106k、Microglia 92k、Vascular 9.9k、Fibroblast 9.2k、Bergmann glia 8.0k、Choroid plexus 7.7k、Ependymal 5.9k、Committed OPC 4.7k）
  - `roi`（106 个脑区）、`donor_id`（4 个：H18.30.001/002、H19.30.001/002）、`sample_id`（606 个 10x library）、`assay_ontology_term_id`（单一 EFO:0009922）
  - 嵌套结构实测：**每个 sample_id 恰属于 1 个 roi 和 1 个 donor**（这正是 08d block-shuffle 的前提）。
- **漂移阶梯设计（4 层，每层 ground truth 明确）**：
  | Tier | 对比 | 控制了什么 | ground truth |
  |---|---|---|---|
  | T0 | 同 library 内 split-half（n-matched） | — | 校准基线 |
  | T1 | 同 (roi, donor) 不同 library | donor、roi、细胞类型全同 | **纯技术漂移 = 无功能差异** |
  | T2 | 同 roi 不同 donor 的 library | roi、细胞类型同 | 供体间漂移（技术+个体） |
  | T3 | 不同 roi（同 donor 或跨 donor） | 细胞类型同 | 区域生物学（正对照，稿件已有） |
- **可计算规模**（实测）：每 (CT, library) 细胞数中位 46（P10=2, P75=156）；≥20 细胞过滤后 T1 有 1,144 个 (CT,roi,donor) 组合、**2,161 对**（Astrocyte 575、Oligo 591、OPC 575、Microglia 516、Vascular 133、Fibroblast 121、Ependymal 76、COP 25、Bergmann 22、Choroid 10）。
- **预期对照**：raw JS / cosine / Spearman 距离 / k_f 从 T0→T2 单调抬升（把 library/供体漂移误报为分歧）；ω 在 T1（必要时含 T2）保持 ≈T0 校准值，仅在 T3 抬升。FPR 框架：以各指标自身 T0 null 的 95 分位为阈值，报告 T1/T2 误报率。
- **计算量**：复用 08d 的 backed CSR 提取（`extract_csr_from_backed`，HK+top5000 HVG ≈5–6k 基因）。Oligodendrocyte 最大（490k 细胞）08d 曾完整跑过 1000 次 block-shuffle；本次只需 observed + split-half null。估计 **2–4 h**（含全部对比指标）；内存峰值由 08d 方案控制。注意 `n-matched` 基线（见坑 4）。

### 场景 B（推荐复制场景）：Kang batch1 跨 lane 技术重复

- **数据文件**：`data/kang_ifnb/GSE96583_RAW.tar` 内 `GSM2560245_A.mat.gz / GSM2560246_B.mat.gz / GSM2560247_C.mat.gz`（**MatrixMarket 稀疏整数矩阵**，32,738 基因 × 3,639/4,246/6,145 细胞）+ 各自 barcodes.tsv.gz + `GSE96583_batch1.total.tsne.df.tsv.gz` 元数据。
- **分组变量（已实测确认）**：tsne.df 列 `ind`（8 供体：1043/1079/1085/1154/1249/1493/1511/1598）、`batch`（lane A/B/C）、`cell.type`（8 类，注意列名带点）、`multiplets`（singlet 过滤后 11,819 细胞）。**无 stim 列——batch1 全部为未刺激对照**（batch1 供体与 batch2 供体 ID 完全不相交）。
- **结构（实测 crosstab）**：lane A 含供体 {1079,1154,1249,1598}，lane B 含 {1043,1085,1493,1511}，**lane C 含全部 8 个供体**。因此每供体恰好出现在 2 个 lane → 每细胞类型 8 个「同供体同条件跨 lane」技术重复对（4 个 A–C + 4 个 B–C）。
- **ground truth**：同 donor、同 ctrl、仅 lane 不同 → 无功能差异；对比其 batch2（稿件已分析）可加正对照（stim vs ctrl）。
- **预期对照**：同场景 A；额外优点：PBMC、不同组织、不同实验室，与 brain 形成跨组织复制。
- **计算量**：矩阵极小（5.4M nnz 合计），mmread + ENSG→symbol 映射（`ensg2sym.tsv`、`GSE96583_genes.txt.gz`，照抄 script 79）+ 全部指标 + split-half/排列 null：**< 30 分钟**。
- **规模限制**：每类型仅 8 对（Dendritic/Megakaryocytes 细胞太少须剔除，约 6–7 个可用类型 → ~50 对）；可把 lane C 拆成互斥两半分别与 A、B 配对以扩样本量并缓解 lane C 共享问题。

### 场景 C（次级/已有材料，不建议做主场景）：Kang batch2 donor-vs-donor

- 已由 script 79 完整计算（`results/kang_ifnb_demo_pairs.csv`）。但 **donor-vs-donor 不是纯 null**（个体间存在真实功能差异，如单核细胞激活态；实测 ω_cal 中位 0.92–2.68）；且 batch2 中 lane 与刺激条件完全混杂（2.1=ctrl、2.2=stim）。只能作为「供体间漂移」的次级对照或附录，**不能**作为 FPR 的地面真值主张。
- 附带实测证据（对未来写作有用）：stim vs donor-drift 的 AUC——raw JS ≈ 1.000、k_f ≈ 0.98–1.00、ω ≈ 0.55–0.92。即在大效应扰动下 raw JS 分离度也极好；本对策的卖点必须是 **FPR/校准**（漂移误报率），而不是扰动分离 AUC——这正是 GB 拒稿意见①的教训。

### 场景 D（否决）：Tabula Sapiens 技术重复

- 实测 `TS_Liver.h5ad`（5,007×58,870）与 `TS_Spleen.h5ad`（34,004×58,870）obs：仅 `donor`、`method`（10X/smartseq2）、`cell_ontology_class`、`free_annotation` 等列；**无 library/sample/重复结构列**，且 donor 与 method 完全混杂（smartseq2 只出现在 TSP2/TSP6/TSP7，TSP14 只有 10X）。无法构造技术重复对照；donor 对比稿件 phase33 已做。**不推荐**。

---

## 2. 成功风险评级与判据（go/no-go）

### 场景 A（brain）：风险 **中**
- **有利证据**：ω 的 k_n 分母理论上吸收 library 级基因偏倚；Kang batch2 donor-drift 下 ω_cal 仅 0.92–2.68（相对温和）。
- **不利证据（必须正视）**：08d block-shuffle null 的 ω（Oligo ≈38、Microglia ≈25）远高于 region 级 split-half 基线 9.73——说明 library 级结构确实抬升过 ω，尽管该 null 混杂了 donor 组成（见坑 3），不能定性为纯技术效应。**T1 从未计算过，结果未知。**
- **判据（pilot 后检查）**：T1 中位校准 ω（÷ T0 中位）≤ 1.5 且显著低于 raw JS / k_f / cosine 的同口径校准值（例如 competitors ≥ 3×）→ go；若 ω 校准值 > 2 → 主张降级为「相对 FPR 下降」弱叙述或换场景。
- **成本**：低（数据/代码全在）。

### 场景 B（Kang batch1）：风险 **中低**
- 同供体同条件跨 lane，混杂最少；唯一结构限制是 donor 嵌套于 lane-pair（A-donors 只出 A–C 对）且 lane C 共享。
- **判据**：8 供体技术重复对的校准 ω 中位 ≤ 1.5；若 NK/单核等类型出现 >2× 抬升需逐类报告。
- **成本**：极低（< 30 min），**建议作为 pilot 的第一枪**。

### 场景 C：风险 **高**（作为主场景）；仅次级使用。
### 场景 D：否决。

### 换场景触发条件
若 A、B 两个 pilot 中 ω 在纯技术漂移下均 >2× 抬升：本对策方向（漂移免疫实证）不成立，应回到模拟+机理（k_n 分解）路线，或改谈「ω 残余膨胀比 competitors 小一个数量级」的校准比较（需要预先注册该弱主张，避免被审稿人视为 post-hoc）。

---

## 3. 指标实现盘点

| 指标 | 状态 | 位置 |
|---|---|---|
| k_n / k_f / ω（含 manuscript hybrid：top-200 \|Δμ\| per-pair） | **现成** | `cki/core.py`（`compute/compute_omega/js_divergence`）；配对级 hybrid：`notebooks/79_kang_ifnb_demo.py:pair_metrics`、`08d_brain_blockshuffle_null.py:pair_omegas` |
| raw JS（全基因） | **现成** | script 79（`raw` 列）；`13_phase35_method_comparison.py` |
| Spearman 距离（1−ρ，pseudobulk 上） | **现成** | `13_phase35_method_comparison.py:215-218` |
| Cosine 距离（1−cos） | **现成** | `13_phase35_method_comparison.py:220-229` |
| Marker Jaccard 距离（1−J） | **半现成** | `13_phase35:231-241` 是 CT×CT 级（每 CT top-200 markers vs rest）；配对级需新定义：每组 top-k markers vs 共同背景（同 CT 池），再算集合 Jaccard。~20 行新代码 |
| MELD / scDist-approx / Augur（可选现代对手） | **现成但重** | `101_competitors_v44.py`、`91_augur_v45.py`；主图可不用（它们不是「divergence 指标」直接可比物） |

新写代码合计估计 < 100 行（配对级 marker Jaccard + 阶梯对比驱动脚本 + 图）；数据读取与 ω 计算全部照抄 79/08d。

---

## 4. 推荐主场景 + 产出图表草图

**主场景：A（brain 阶梯）为主图，B（Kang batch1）为独立复制面板。** 执行顺序：先跑 B（半小时）作为 go/no-go 第一关，再跑 A pilot（T0/T1 only，~1–2 h），通过后再补全。

**主图草图（大面板，5 个 panel）**：
- **(a) 设计示意**：4 层阶梯 T0→T3（split-half → 跨 library（同 roi+donor）→ 跨 donor（同 roi）→ 跨 roi），brain 嵌套结构示意。
- **(b) 校准分布**（brain，10 CTs 合并 + per-CT 色彩）：x = tier（T0–T3），y = metric ÷ T0 中位（log 轴），6 条 metric 分面（ω, k_f, k_n, raw JS, cosine, Spearman, marker Jaccard）。预期视觉：ω 面板在 T1–T2 平坦、T3 跳升；competitor 面板 T1 起持续抬升。
- **(c) FPR 汇总柱状图**：每 metric 在 T1/T2 的误报率（阈值 = 各自 T0 null 95 分位；误差条 = library-pair cluster bootstrap）。ω 柱 ≈ 5–15%，competitors ≈ 50–90%。
- **(d) Kang batch1 复制**：8 供体 × ~6 类型 lane 对，同 (b) 式小图（T0 vs T1）。
- **(e) 正对照**：brain T3（跨 roi）与 Kang batch2 stim-ctrl 下全部指标抬升——证明 ω 并非「死指标」，漂移免疫 ≠ 灵敏度丧失。

---

## 5. 明确的坑（设计规避清单）

1. **Kang batch2 lane 与条件完全混杂**（lane 2.1=ctrl、2.2=stim）：绝不能拿 batch2 做「batch 漂移」对照；技术重复只能来自 batch1（全 ctrl、供体跨 lane）。稿件 79 号脚本已正确处理 batch2，其排列 null（median ω ≈26 vs split-half 8.6）被条件组成噪声污染，不能引用为技术漂移证据。
2. **Kang batch1 donor 嵌套于 lane-pair**（A-donors 只出现在 A–C 对，lane C 被所有对共享）：统计上以 donor 为单元；或把 lane C 拆成互斥两半分别与 A、B 配对。barcode 冲突按 script 79 的 `-1→-11` 规则（batch1 实测 23+70 个，全部可解）。
3. **Brain library 嵌套于 (roi, donor)**：跨 roi 对必然混杂 donor 与 library（这正是 08d block-shuffle 存在的原因）——T1 必须限定在 (roi, donor) 内；既有 block-shuffle null 与 `reviewer_within_donor_gradient.csv` 都混杂 donor 组成，不能当作技术漂移的校准证据。
4. **组规模不匹配是校准陷阱**：library 组中位仅 ~46 细胞，而既有 brain split-half 基线 9.73 用的是 ≥200 细胞的 region 级拆分。所有指标（尤其 per-pair top-200 选基因的 k_f）都有 n 依赖 → **必须用 n-matched 的 library 内 split-half 作 T0**，并对 n≥50 做敏感性分析。
5. **donor-vs-donor 不是纯 null**：个体间有真实功能差异（实测 ω_cal 至 2.68）；T2 只能作「供体漂移」次级解读，FPR 主张只用 T1。
6. **排列 null 的组成噪声**：跨条件打乱标签会因刺激比例的二项波动注入真实生物差异（Kang batch2 null ≈26 即此效应）——漂移对照一律不用标签排列，用 split-half/构造对。
7. **环境**：系统 `Python312` 的 h5py DLL 损坏；用 `C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（3.13.14, anndata 0.12.16, h5py 3.16）。bash 里 `ls/grep/tail` 部分损坏，一律 `python -c` 直调。读 brain 只用 backed + 08d 的 h5py CSR 提取。
8. **batch1 注释列名带点**（`cell.type`、`ind`），batch2 是 `cell`、`ind`；`.mat.gz` 实为 mtx（mmread 直读），勿用 loadmat。
9. **marker Jaccard 配对级定义需预注册**（每组 top-k vs 共同同型背景），避免被指为针对数据挑定义。

---

## 6. 附：实测数据要点速查

- Kang batch1：14,030 细胞（singlet 11,819），8 供体 × lane crosstab——A:{1079,1154,1249,1598}, B:{1043,1085,1493,1511}, C:全部 8 个；每 (供体,lane) singlet 500–1,070 个，8 个 cell.type。
- Kang batch2（script 79 已有）：donor-drift ω_cal 中位 0.92–2.68；stim ω_cal 1.76–3.44；AUC rawJS/k_f ≈ 1.0 > ω。
- Brain：888,263 × 59,480；606 libraries；4 donors；106 ROIs；258/264 (roi,donor) 有 ≥2 libraries；T1 对数 2,161（≥20 细胞/组）；split-half 基线 9.73 [9.03, 10.53]（region 级，n≥200，勿直接用作 T0）。
- TS：Liver 2 donors（TSP6/TSP14，smartseq2 全在 TSP6）；Spleen 3 donors（smartseq2 全在 TSP2/TSP7）；无 library 列。
