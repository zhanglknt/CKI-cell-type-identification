# Genome Biology 盲审报告（计算生物学 / 算法与实现视角）

- **稿件**: CKI: a Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics（投稿包 v44）
- **审稿人角色**: r-computational（算法、统计实现、代码一致性）
- **日期**: 2026-09-05
- **评审材料**: CKI_Manuscript_fulltext.txt、CKI_Supplementary_fulltext.txt、CKI_Reproducibility_Guide_fulltext.txt、Table1-2_fulltext.txt；开源实现 `cki/`（core.py、bootstrap.py、blocknull.py、gene_sets.py、utils.py，v0.4.7）

---

## 总分与判定

**总分：6.8 / 10**
**判定：Major Revision**（偏轻；核心方法无致命错误，但基准设计与软件统计接口存在需要作者实质性回应的问题）

P0 = 0，P1 = 3，P2 = 5。

---

## 主要问题

### P1-1. 仿真实验的"中性漂变"定义与 CKI 的锚定假设同构，特异性优势近同义反复

地面真值仿真中，"中性漂变"被定义为 **housekeeping 基因上的 2^η 偏移**（Methods, Ground-truth simulation；Supplementary Note 3.12）。而 ω 的构造恰恰是用 HK 基因做分母归一化。因此"ω 在 HK 漂写下 FPR = 0.00，而 raw JS / cosine 为 0.55–0.58"这一摘要级结论，在很大程度上是定义的直接后果：任何以 HK 为锚的方法都天然免疫 HK 上的扰动。作者确实在 Results 中披露了这一点（"the neutral-drift null is itself defined on HK genes—the same anchoring assumption CKI makes"），但摘要仍以"rejected neutral housekeeping-gene drift (FPR 0.00 vs 0.55–0.58)"为首要卖点，AUC = 0.80 的头名结论同样完全条件化于该构造。建议：(i) 摘要中明确该优势的构造依赖性；(ii) 补充至少一种**非 HK 锚定的中性漂变定义**（如随机低方差基因集上的漂变、或全转录组组成保持型漂变）下的对照实验，以区分"ω 的特异性是构造产物"与"ω 的特异性对中性模型选择稳健"。

### P1-2. 竞品基准薄弱且不公平：scDist 未真正运行、MELD 饱和、单一混杂数据集

与 MELD/scDist 的对比存在三重缺陷：(i) scDist 是作者自实现的 "Python approximation"（per-PC 固定效应回归 + √Σβ²λ），原 R 包从未运行——以近似实现代表竞品性能，对 scDist 不公平，且无法排除近似误差；(ii) MELD 的 AUC 0.997–0.9998 已饱和，"6/6 方向一致"之外无可比较的梯度；(iii) 整个基准仅基于 Kang IFN-β 一个数据集，且 condition 与 10x lane 完全混杂（作者已披露）。加之 mean-shift 仿真中 CKI 在 500 基因档崩溃（AUC 0.05–0.13）而竞品 sensitivity = 1.00，实际展示的是 CKI 在检测能力上全面劣于竞品、仅在其自定义的 specificity 维度占优。对 Genome Biology 方法学论文，这一基准规模不足以支撑"互补工具"定位之外的任何比较性主张。建议：运行原版 scDist（或明确删除其定量数值仅保留定性陈述），并增加至少一个无 lane 混杂的扰动数据集。

### P1-3. 软件接口统计缺陷：`bootstrap_test` 返回的 `ci_95` 并非置信区间

`cki/bootstrap.py:515-518` 中 `ci_95 = [percentile(null_omega, 2.5), percentile(null_omega, 97.5)]`——这是**置换零分布的分位数范围**，不是观测 ω 的置信区间。零分布的 2.5–97.5% 区间在统计含义上是"零假设下的拒绝域边界"，将其以 `ci_95` 键返回会误导用户把它当作 ω 点估计的不确定度。此外函数名 `bootstrap_test` 执行的是标签置换检验而非 bootstrap，命名与语义不符（文稿 Methods 正确称之为 permutation test）。两个问题都位于用户直接调用的公开 API 上，应重命名/重标注（如 `null_ci_95` / `permutation_test`），避免随论文发表固化进 API。另注：`null_omega` 中若出现 `inf`（k_n ≤ 1e-15 时），`null_mean/null_std` 变为 inf/NaN 导致 SES 失效而无保护（`bootstrap.py:504-513`）。

### P2-1. 补充材料与正文的校准倍数数值不一致

正文（Results, Calibration）与 Supplementary Note 3.5 同述 brain-internal baseline 9.73 相对 mouse-derived 7.70：正文写 "approximately **1.3-fold** higher"，SN 3.5 写 "approximately **1.5-fold** higher"。9.73/7.70 = 1.26，正文正确，补充材料有误。虽为笔误级，但出现在校准这一核心可解释性参数上，需修正。

### P2-2. 数值保护机制的文档与代码表述不符

Supplementary Note 3.11 称 "Pseudocount epsilon = 1e-9: added to avoid log(0) in JS divergence"。实际代码中 JS 散度通过**显式零掩码**（`core.py:77-86` 的 `mask_p = p > 0`）避免 log(0)，`_EPS = 1e-9` 仅加在 softmax 分母上（`utils.py:91`），从不进入 k_n/k_f/ω。代码内注释（`core.py:16-46` 的 guards 块）对此有精确说明，但补充材料的面向读者的描述是错的。同类地，包内存在两套 ω 计算路径（`compute_omega` 用精确 `kn <= 0` 守卫，`blocknull._omega_from_pbs` 用 `1e-15` 容差），虽有文档但增加了双实现漂移风险，建议收敛为单一实现。

### P2-3. 包默认参数不能复现论文流程

`compute()` 默认 `func_method="hvg"`、`n_top_genes=2000`、`use_reference_hk=False`（数据驱动 HK 检测），而论文全部分析使用 `pairwise_absdiff` top-200 + HRT Atlas 参考集。用户以默认参数调用得到的是与论文不同的方案。docstring 和正文 "package parity" 注记有说明，但对一个以可复现性为卖点的工具论文，建议将论文方案设为默认（或提供 `preset="manuscript"`），并在 README 首屏给出与论文逐行对应的调用示例。

### P2-4. 可扩展性：包内实现不可达图集规模，复杂度未分析

`bootstrap_test` 与 `block_shuffle_test` 均将表达矩阵整体稠密化（`bootstrap.py:411-413`、`blocknull.py:260-263`），置换循环为纯 Python 串行（tqdm 进度条），无向量化/并行。31,764 对 × B=1,000 的脑分析依赖包外流式 notebook 实现（72 核时）。文稿未给出形式复杂度（每对每次置换 O(G)，G 为基因数；脑全景观零分布为 O(B × n_pairs × G)）。`densify` 的 800MB 警告是好的实践，但对 GB 读者应明确：包的适用范围是小规模两组比较，图集规模需使用 notebook 流水线——建议在 Methods/包文档中显式分层。

### P2-5. 次要一致性问题（汇总）

- Methods "CKI computation" 写 pseudobulk 要求 "at least 10 cells per group"，而数据集描述均为 ≥20 cells/entry（10 是 donor 级条件），建议统一表述。
- Supplementary Algorithm 1 第 4 步 "norm(x) = (x+1)/sum(x+1) on log1p counts" 记号含混：softmax(log1p(c)) ≡ (c+1)/Σ(c+1) 中的 "+1" 作用于**计数** c 而非 log1p 值 x；按字面在 log1p 值上做 (x+1)/Σ(x+1) 恰是 TCGA 敏感性分析中的"linear normalization"，两者不同。建议改写为显式的 softmax 式。
- `_BootstrapResult` 同时存储 `ses` 与 `cohens_d` 键，但 `dict.get("cohens_d")` 绕过 `__getitem__` 拦截、不触发 DeprecationWarning，弃用机制不完整。

---

## 优点

1. **文稿—代码一致性堪称典范**。抽查 6 个关键点全部吻合：(i) hybrid 方案（k_n 共享 HK 集 + k_f per-pair top-200 |Δ|、HK 先于排序排除）在 `_top_absdiff_genes` / `_detect_by_pairwise_absdiff` 与文稿 Methods、Supplementary Algorithm 2 完全一致；(ii) 经验 P 值公式 (n_extreme+1)/(B+1) 与代码逐字一致（含 NaN 留分母的处理）；(iii) softmax(log1p) ≡ +1 伪计数 + L1 归一化的数学等价成立，且脑（log1p-after-mean）与 mouse/human（mean-of-log1p）两条聚合顺序的差异被主动披露；(iv) `kn_floor=1e-4` 仅用于 TCGA、单细胞仅用 positivity guard，与 `compute_omega` 实现及最小观测 k_n 报告吻合；(v) `reselect_identity=True` 默认使零分布纳入基因重选步骤，与文稿陈述一致；(vi) SES 定义、单侧/双侧 tail 参数与文稿一致。作者甚至主动标注了与论文不一致的遗留选项（`pairwise_de`）。

2. **零假设设计与验证异常严谨**。block-shuffle 以 10x library 为原子块、保持 per-region library 计数结构；per-permutation 重选 k_f 基因使选择与零分布 scheme-matched；尤其 pseudo-region 阴性对照（127,756 伪对，尾率 5.79%/6.87% vs 名义 5%）直接证明了零分布校准良好且检验对库内相似性保持功效（同源性伪对 37.6% 下尾率）——这种"检验自己的检验"的做法在单细胞方法学论文中罕见。对早期反保守实现（36.3% 触地板）的自我纠错也完整披露。

3. **对循环性与分母伪相关的量化坦率且充分**。per-pair top-200 选择的循环性通过 leave-pair-out / 固定面板 / 全 5,000 基因三套消融量化（k_f 中位膨胀 1.61 倍，排序 ρ ≈ 0.92–0.94 保持）；ω 与标准距离的负相关被偏相关分解证认为分母伪相关（conditional r 转正）；B=1,000 下 m=31,764 的 BH 不可达性被预先声明而非事后辩解。校准常数的不可迁移性（brain-internal 9.73 vs mouse 7.70）也被数据集内重校准直接量化。

---

## 总结

CKI 是一个构造简单、诚实记录、实现可靠的启发式比值指标。其核心缺陷不在数学正确性（未发现 P0），而在评价的构造依赖性：最具卖点的特异性优势由与自身假设同构的中性模型产生（P1-1），竞品基准以近似实现与单一混杂数据集支撑（P1-2），软件公开 API 存在会误导用户的统计标注错误（P1-3）。上述问题均可通过补充对照实验、修正基准与 API 重标注解决，故判 Major Revision 而非 Reject；若作者能实质回应 P1-1 与 P1-2，本文可达到 Genome Biology 的发表标准。
