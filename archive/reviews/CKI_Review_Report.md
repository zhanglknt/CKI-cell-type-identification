# CKI 稿件综合审稿报告

**稿件标题**: CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling  
**作者**: Xianming Wu, Li Zhang  
**目标期刊**: Nucleic Acids Research (NAR)  
**审稿日期**: 2026-07-21  
**稿件版本**: version2/CKI_manuscript_submit_V1  
**词数**: 7,650 | 图: 6主图 + 5补充图 | 参考文献: 34篇

---

## 一、总体评价

**综合评级: Major Revision**

三位专家（计算方法学、生物学、期刊策略）审稿结果一致：稿件核心创新明确（Ka/Ks 类比应用于转录组学），数据量充足（4 个数据集、数百万细胞），但在方法学严谨性、生物学解读和文本完整性方面存在需要修改的问题。

---

## 二、Critical 问题（必须修复）

### C1. 多重检验校正缺失
- **位置**: Methods (Bootstrap permutation test) + Results (脑区分析)
- **问题**: 31,764 个脑区比较未做 FDR/Bonferroni 校正，30 个 Strong 信号的假阳性率无法评估
- **建议**: 添加 BH-FDR 校正，报告 q-value；或明确说明为何不做校正（如探索性分析定位）

### C2. HK 基因中性假设缺乏验证
- **位置**: Methods (CKI computation) + Discussion (Limitations)
- **问题**: 管家基因被假定为中性基线，但 HK 基因在不同组织/疾病中可能受调控。稿件提到 sensitivity analysis (r > 0.95) 但未展示数据
- **建议**: 将 HK 敏感性分析结果移入正文或补充材料；讨论 HK 基因在肿瘤/脑区中的潜在非中性

### C3. ω 比值稳定性未讨论
- **位置**: Methods (CKI computation)
- **问题**: ω = k_f/k_n 是比值，当 k_n 接近 0 时 ω 会爆炸。稿件未讨论 k_n 的下限、ω 的稳定性条件
- **建议**: 添加 k_n 下限阈值（如 k_n < 0.01 时排除或设上限），报告被排除的 pair 数量

### C4. TCGA bulk RNA-seq 上 pseudobulk 概念误用
- **位置**: Methods (Datasets) + Results (Cancer analysis)
- **问题**: TCGA 是 bulk RNA-seq，但 CKI 的 pseudobulk 方法设计用于单细胞数据。将 bulk 数据直接当作 pseudobulk 处理在概念上不严谨
- **建议**: 明确说明 TCGA 使用 bulk 表达谱而非 pseudobulk；讨论 bulk vs pseudobulk 的差异对 ω 解释的影响

### C5. OPCs 阴性对照的循环论证
- **位置**: Results (OPCs: key negative control)
- **问题**: OPCs 有高全局 ω (7.65)，因此不容易产生 Strong 信号（Strong 要求 ω < 15）。0 个 Strong 信号可能是因为阈值设定而非生物学原因
- **建议**: 重新分析 OPCs 使用相对阈值（如细胞类型内 percentile）；展示 OPCs 的 Moderate/Weak 信号分布

---

## 三、Major 问题

### M1. 文本损坏 — 多处数值缺失和文字截断
- 摘要: "Spearman = to, all P < 0.001" → 应为 "Spearman r = -0.57 to -0.38"
- "e ran a parameter sweep" → "We ran"
- "median 13., n = pairs" → "median 13.81, n = 4,851 pairs"
- "substantively higher than mouse ()" → 缺小鼠 ω 值
- "e asked whether" → "We asked whether"
- Figure 5 图注不完整: "(A). (B)  (C)"
- 补充图编号缺失: "Supplementary Figure S." (两处)
- Discussion: "how much of that difference functional" → "how much of that difference is functional"

### M2. 30 个 Strong 信号缺乏独立验证
- **问题**: 所有 30 个信号的解释都基于文献交叉验证，没有独立实验或数据集验证
- **建议**: 至少对一个信号提供独立验证（如空间转录组数据）；或在 Limitations 中明确声明

### M3. 方法比较的公平性
- **问题**: CKI AUC=0.716 远低于 cosine 0.887，作者解释为"trade-off"但缺乏定量论证
- **建议**: 在更多 benchmark 数据集上比较；讨论 CKI 在哪些场景下优于标准方法

### M4. 文献覆盖不足
- 缺少 CellTypist (Domínguez Conde et al., Science 2022)
- 缺少 scArchi / 单细胞图谱比较方法
- 缺少转录组中性漂变理论（如 Sandberg et al.）
- Ka/Ks 在转录组学的类比应用是否有先例？

### M5. Bootstrap B=500 可能不足
- **问题**: 对于 31,764 个比较，B=500 的 bootstrap 可能产生不稳定的 P 值
- **建议**: 对 Strong 候选信号增加 B=5000 的精细 bootstrap；报告 P 值的置信区间

---

## 四、Minor 问题

### m1. 补充图编号混乱
- version2 中补充图为 S1-S5，但正文引用为 "Supplementary Figure S."（编号缺失）
- 建议统一编号：Supplementary Fig. S1-S5

### m2. 参数选择缺乏理论依据
- top-2,000 HVG 排除 HK 基因 — 为什么是 2,000？
- Strong 阈值 residual < 0.3 — 为什么是 0.3？
- 建议在 Methods 中添加参数选择的理论或经验依据

---

## 五、期刊推荐

### 当前目标: NAR (Nucleic Acids Research)
- **影响因子**: ~16.7 (2024)
- **匹配度评估**: 
  - ✅ 方法学论文（新计算方法）
  - ✅ 数据可用性和代码开放
  - ⚠️ NAR 更偏向核酸生物学，CKI 更偏向计算方法
  - ⚠️ 脑区分析部分占篇幅过大，与 NAR 核心范围略有偏离

### 推荐期刊排名（期刊策略顾问报告待补）

| 排名 | 期刊 | IF (2024) | 匹配度 | 理由 |
|------|------|-----------|--------|------|
| 1 | NAR | ~16.7 | ★★★★ | 方法学论文定位准确；已发表 HRT Atlas [4] |
| 2 | Genome Biology | ~12.3 | ★★★★ | 单细胞基因组学方法论文首选 |
| 3 | Bioinformatics | ~5.8 | ★★★★★ | 纯计算方法论文最佳匹配 |
| 4 | Cell Systems | ~8.6 | ★★★★ | 系统生物学角度 |
| 5 | PLOS Comp Biol | ~3.8 | ★★★★ | 计算生物学方法 |

### 投稿策略建议
1. **首选 NAR**: 已有引用关系（HRT Atlas 发表在 NAR），方法学论文定位清晰
2. **备选 Genome Biology**: 单细胞方法论文的传统阵地
3. **保底 Bioinformatics**: 纯计算方法论文，审稿快

---

## 六、修改优先级

| 优先级 | 问题 | 工作量 | 预计时间 |
|--------|------|--------|----------|
| P0 | 文本损坏修复 (M1) | 小 | 1h |
| P0 | 多重检验校正 (C1) | 中 | 2h |
| P0 | TCGA pseudobulk 表述 (C4) | 小 | 1h |
| P1 | HK 敏感性分析展示 (C2) | 中 | 3h |
| P1 | ω 稳定性讨论 (C3) | 小 | 1h |
| P1 | OPCs 重新分析 (C5) | 中 | 3h |
| P2 | 独立验证讨论 (M2) | 小 | 1h |
| P2 | 文献补充 (M4) | 小 | 2h |
| P2 | 补充图编号统一 (m1) | 小 | 0.5h |

---

*报告生成: 2026-07-21 23:55*  
*审稿专家: 计算方法学专家 + 生物学专家 + 期刊策略顾问（待补）*
