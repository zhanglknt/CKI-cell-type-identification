# CKI v17 综合审稿报告 & 期刊推荐

**审稿日期**: 2026-07-26
**审稿团队**: 方法学 + 数据与可复现性 + 统计学 + 写作与期刊适配（4位独立专家）
**审稿对象**: CKI_NAR_Submission_v17.zip (8.6 MB, 21 files)
**对比基准**: v14 综合审稿报告（2026-07-26, v14 综合评分 6.95/10）

---

## 一、综合评分

| 维度 | v17 评分 | v14 评分 | 变化 | Critical | Major | Minor |
|------|---------|---------|------|----------|-------|-------|
| 方法学 | **6.8** | 6.8 | ±0 | 5 | 8 | 8 |
| 数据与可复现性 | **5.5** | 7.0 | **-1.5** | 3 | 6 | 8 |
| 统计学 | **4.8** | 6.8 | **-2.0** | 3 | 5 | 6 |
| 写作与期刊适配 | **7.3** | 7.2 | +0.1 | 5 | 8 | 11 |
| **综合** | **6.10** | **6.95** | **-0.85** | **16** | **27** | **33** |

### 投稿准备度: 55%（v14: 65%, -10个百分点）

### 评分下降原因分析

v17相比v14综合评分下降，核心原因是：v14修复了v12的正文内部矛盾（JS对数底、归一化方式等），但v17暴露出**正文与复现指南之间的系统性矛盾**——这些矛盾在v14审稿时因复现指南未被纳入审稿范围而未被发现。v17将复现指南纳入审稿后，跨文档一致性问题集中爆发。

---

## 二、v14 -> v17 修复总结

### 已修复的v14 issues

| v14编号 | 问题 | v17状态 |
|---------|------|---------|
| C1 | 多重检验校正缺失 | 已透明声明（但未实质解决） |
| C2 | Bootstrap P值公式三方不一致 | 正文+补充材料已统一为单侧绝对偏离+1伪计数 |
| M3 | "proving"过强措辞 | 已改为"demonstrating" |
| — | Strong标准含"pair median omega > 20" | 已删除（3处） |
| — | TS pairs硬编码4,851 | 已改为动态5,151（正文层面） |

### v17新发现的Critical Issues（跨文档矛盾）

v17审稿的核心发现是：**正文（manuscript + supplementary）与复现指南（reproducibility guide）之间存在8项系统性矛盾**，这些矛盾在v14审稿时未被识别，因为v14审稿未覆盖复现指南。

---

## 三、4位专家共识的Critical Issues（按严重度排序）

### C1. Bootstrap范围：正文与复现指南直接矛盾（4/4专家独立发现）

**这是最高优先级问题——4位专家全部独立识别。**

| 文档 | 表述 |
|------|------|
| 正文 P21 (Methods) | "Bootstrap permutation testing was performed only for the mouse pilot study" |
| 正文 P36 (Statistical reporting) | "Bootstrap permutation testing was performed only for the mouse pilot study (B = 500)" |
| 补充材料 P25 (Note 1.5) | "Bootstrap permutation testing was performed only for the mouse pilot study" |
| 补充材料 P62 (Note 3.2) | "Bootstrap was not performed for human, TCGA, or brain atlas analyses" |
| **复现指南 P138** | **"B = 500 mouse, 1000 human, 100 TCGA, 100 brain"** |
| **复现指南 P176-179** | **列出4个数据集的bootstrap输出文件** |
| **复现指南 P187** | **"Verify bootstrap iterations: 500 (mouse), 1000 (human), 100 (TCGA), 100 (brain)"** |
| **补充材料 Algorithm 1 P41** | **"for b = 1 to B (default 1,000)"** |

**矛盾本质**: 正文说bootstrap仅用于mouse（B=500），但复现指南明确列出4个数据集各自的B值和输出文件。Algorithm 1的默认B=1,000又与前两者都不同。三份文档给出了三个互相排斥的bootstrap描述。

**ground truth**: 实际代码中，主分析脚本02c仅对mouse执行bootstrap(B=500)；独立脚本08a/08b/08c分别对TCGA(B=100)、human(B=1000)、brain(B=100)执行bootstrap。因此：
- 复现指南的描述是**事实正确的**
- 正文的表述是**不完整的**（遗漏了独立脚本执行的bootstrap）
- Algorithm 1的B=1,000是**错误的**（应为500）

**修复方案**:
1. 正文P21/P36: 改为"Bootstrap permutation testing was performed for the mouse pilot study (B=500, main analysis). Independent bootstrap validation was also performed for human (B=1,000), TCGA (B=100), and brain atlas (B=100) analyses using dedicated scripts (08a/08b/08c)."
2. Algorithm 1: B默认值从1,000改为500
3. 补充材料: 与正文保持一致

---

### C2. HRT Atlas使用：正文说"用了"，复现指南说"没用"（3/4专家发现）

| 文档 | 表述 |
|------|------|
| 正文 P18 (Methods) | "the HRT Atlas v1.0 consensus set is **optionally used as supplementary enhancement** (union with detected set)" |
| 正文 P45 (Results) | "HK genes were auto-detected... **supplemented with 1,130** human-mouse conserved reference HK genes from the HRT Atlas" |
| 补充材料 P19 (Note 1.2) | "**supplemented by** the HRT Atlas v1.0 consensus set as an optional enhancement" |
| 补充材料 P72 (Note 4.2) | "**supplemented with 1,130 genes from HRT Atlas v1.0**" |
| **复现指南 P51** | **"but was NOT used in the reported analyses (use_reference=False)"** |
| **复现指南 P54** | **"use_reference=False"** |
| 正文 P96 (Discussion) | "CKI uses data-driven auto-detection... **with optional HRT Atlas enhancement**" |

**矛盾本质**: 正文和补充材料一致地说HRT Atlas被用作"supplementary enhancement"（union），但复现指南明确声明`use_reference=False`（即未使用）。两者不可能同时为真。

**ground truth**: 实际代码中`use_reference=False`，即纯数据驱动，HRT Atlas未被使用。复现指南是正确的。

**修复方案**: 正文P18/P45/P96和补充材料P19/P72全部改为"Housekeeping genes were auto-detected from data using the combined criterion (detection rate > 0.9 and CV < 30th percentile). The HRT Atlas v1.0 reference set is available as an optional enhancement (use_reference=True) but was not used in the reported analyses."

---

### C3. 补充图S3列出6种癌 vs 正文5种癌（3/4专家发现）

| 文档 | 表述 |
|------|------|
| 正文 P25 | "five cancer types: LUAD, LUSC, LIHC, KIRC, BRCA" |
| 正文 P56 | "five cancer types (LUAD, LUSC, LIHC, KIRC, BRCA)" |
| 补充材料 P74 | "Five cancer types were selected: LUAD, LUSC, LIHC, KIRC, BRCA" |
| **补充图S3图例 P120** | **"six cancer types (BRCA, KIRC, LIHC, LUAD, COAD, HNSC)"** |

**矛盾本质**: 补充图S3图例列出了COAD和HNSC两种正文从未提及的癌症类型。如果S3确实包含这6种癌的数据，正文遗漏了2种；如果S3只有5种癌，图例写错了。

**修复方案**: 确认S3实际内容。如果只有5种癌，修改图例为"five cancer types"；如果有6种，正文需补充COAD/HNSC的说明。

---

### C4. Figure 5图例数字：38 vs 17 vs 59 三个不同数字（3/4专家发现）

| 位置 | 数字 | 含义 |
|------|------|------|
| Figure 5图例 P115 | "38 shared cell types" | 声称38种共有细胞类型 |
| 正文 P64 | "17 cell types" | 描述跨器官排名涵盖17种细胞类型 |
| 正文 P63 | "59 same-cell-type cross-organ comparisons" | 59个跨器官比较对 |
| Table 2 P61 | "n=59 same-cell-type cross-organ pairs" | 59对 |

**矛盾本质**: Figure 5图例说38种细胞类型，正文说17种，Table 2说59对——三个数字互相矛盾。38可能是human-mouse共有细胞类型数，17是实际有跨器官数据的类型数，59是跨器官比较对数。但图例没有解释这些数字的关系。

**修复方案**: 修改Figure 5图例为"CKI omega ranking of 17 cell types with cross-organ comparisons (n = 59 same-cell-type cross-organ pairs)"。

---

### C5. Algorithm 1默认B值=1,000与正文B=500矛盾（2/4专家发现）

| 位置 | B值 |
|------|-----|
| 正文 P21 | B = 500 (mouse pilot) |
| 补充材料 P25 | B = 500 (mouse pilot) |
| **Algorithm 1 P41** | **"default 1,000"** |

**修复方案**: Algorithm 1中"default 1,000"改为"default 500"。

---

### C6. 无FDR校正：31,764个比较的30个Strong候选缺乏统计控制（3/4专家发现）

**问题**: 脑图谱分析在31,764个跨区域比较中识别30个Strong候选信号，但：
- 没有对30个信号做多重检验校正
- 30个信号被逐一深度生物学解读，已超出探索性分析范畴
- 正文P36声明"All reported P-values are raw empirical P-values without multiple testing correction"，但脑分析根本没用P值——用的是残差阈值

**修复方案**:
1. 对30个Strong候选做BH FDR校正（以残差为基础）
2. 或明确声明"Strong候选为探索性发现，需独立队列验证"
3. 补充期望假阳性数计算（在31,764个比较中，随机情况下预期有多少满足residual < 0.3）

---

### C7. P值锚点(omega=1)与校准结果(omega=1.54)不匹配（2/4专家发现）

**问题**:
- P值公式: P = (count(|omega_null - 1| >= |omega_obs - 1|) + 1)/(B + 1) — 锚点在omega=1
- 校准结果: 等价群体的mean omega = 1.54 — 等价群体的omega不在1
- 如果等价群体omega=1.54，那P值应该测试|omega_null - 1.54|而非|omega_null - 1|

**Discussion P90的辩护**: "omega = 1 does not carry population-genetic meaning of neutrality; rather, it is an empirically calibrated operational baseline (mean observational omega = 1.54)"

**问题**: 如果承认omega=1.54是操作基线，P值公式应该以1.54为锚点；如果以1为锚点，则校准实验的omega=1.54就应该被判定为"偏离基线"——自相矛盾。

**修复方案**:
- 方案A: P值公式改为P = (count(|omega_null - 1.54| >= |omega_obs - 1.54|) + 1)/(B + 1)，以校准值为锚点
- 方案B: 保留omega=1锚点，但明确说明"omega=1是理论中性值，omega=1.54是经验观察值；P值测试的是偏离理论中性的程度，而非偏离经验基线"

---

### C8. 补充图S6和S7缺失（2/4专家发现）

**问题**: 正文引用了Supplementary Figure S6和S7（P123-P124），但v17 ZIP包中只有S1-S5。S6和S7完全缺失。

**修复方案**: 生成S6（Brain regional analysis details）和S7（Developmental signature detection）的PDF文件并加入投稿包。

---

## 四、Major Issues（按优先级排序）

### M1. 复现指南P95残留4,851（2/4专家发现）
- 复现指南P95: "all 4,851 pairs"（方法比较）
- 正文P28: "5,151 Tabula Sapiens cell-type pairs"
- 这实际是两个不同数字：5,151=完整omega矩阵，4,851=方法比较子集
- **修复**: 复现指南P95需添加说明"4,851 pairs with complete data for all five metrics (subset of the 5,151 full omega matrix)"

### M2. 负相关可能受比值结构混淆（2/4专家发现）
- omega = k_f/k_n与标准度量的负相关可能受Pearson (1897) spurious correlation of ratios影响
- **修复**: 补做偏相关分析（控制k_n后计算k_f与标准度量的偏相关）

### M3. MANIFEST_v16.txt残留（1/4专家发现）
- v17 ZIP包含MANIFEST_v16.txt（应为v17专属）
- **修复**: 从ZIP中移除MANIFEST_v16.txt

### M4. 跨器官比较样本量过小
- 多个细胞类型n=1（B cells, Smooth muscle cells, Memory B cells），统计效力极低
- 正文P64已添加caution声明，但仍需在Table 2中标注

### M5. TCGA paired analysis样本量过小
- 正文P58: "n = 2-5 per cancer type"，统计效力不足以得出结论
- 已有caution声明，但需更明确地标注为探索性

### M6. 乘法残差模型阈值缺乏正式零分布
- Strong (residual < 0.3)、Moderate (< 0.5)、Weak (< 0.75)为经验阈值
- 缺乏置换验证或参数化零分布
- **修复**: 补做置换检验或至少提供阈值敏感性分析

### M7. 数据版本号/访问日期缺失
- 所有数据集均未标注下载日期和版本号
- **修复**: 每个数据集添加"accessed YYYY-MM-DD"

### M8. QC标准不一致
- Tabula Muris: >10% mito removed
- Tabula Sapiens: >20% mito removed
- 未解释阈值差异原因

---

## 五、Minor Issues（摘要）

1. 正文P49 "6 h5ad files total" — 需确认是否始终为6个文件
2. 补充材料P19 "mu_A" vs 正文P19 "epsilon_A" — 符号不一致
3. 参考文献编号不连续（无(30)号引用但正文引用到(41)）
4. Figure 1C legend说"B = 500 permutations, mouse pilot"但Figure 1C可能展示的是不同数据
5. 补充材料Algorithm 1的缩进格式不规范
6. 正文P68 "6.06-fold" — 应明确是14.36/2.37=6.06
7. 多处使用"Strikingly"、"Critically"等主观词——学术写作应更中性
8. Cover Letter存在但未被纳入审稿范围（37KB, 非缺失）
9. 正文P96 "Sensitivity analysis showed... r > 0.95" — 需指明具体补充材料位置
10. 数据可用性声明P99缺少TCGA Xena具体URL
11. 补充材料P88 Top-5最强信号排名第4项"Microglia DTg vs. TF"但正文P84说"DTg vs. SN"

---

## 六、期刊推荐综合排序

### 推荐逻辑

基于4位专家的独立评估，综合考虑以下因素：
- 方法新颖性（CKI概念的创新程度）
- 验证充分性（4个数据集的验证广度）
- 统计严谨性（当前缺陷的可修复性）
- 期刊scope匹配度
- 审稿周期和接受概率

### 期刊排序

| 排名 | 期刊 | IF (2025) | 匹配度 | 可行性 | 核心评估 |
|------|------|-----------|--------|--------|----------|
| **1** | **NAR** | ~16.6 | 高 | 修复Critical后可投 | 方法学+数据专家认为scope高度匹配；统计专家认为需修复FDR+P值锚点；写作专家评分最高(8.0/10) |
| **2** | **Bioinformatics** | ~5.8 | 高 | 推荐备选 | 方法学专家首选；更侧重方法本身；但需简化生物学应用部分 |
| **3** | **Genome Biology** | ~12.3 | 中低 | 需更多实验验证 | 之前已投过(v16)；需补做偏相关分析+FDR；审稿周期长 |
| **4** | **PLOS Comp Biol** | ~3.5 | 中 | 中等可行 | 统计严谨性要求高；需完整FDR+置换验证；但IF较低 |
| **5** | **Briefings in Bioinformatics** | ~9.5 | 中高 | 需转为方法综述 | 适合CKI方法的综述式介绍；但需大幅重构 |

### 各期刊详细评估

#### 1. NAR (Nucleic Acids Research) — 首选推荐

**优势**:
- Scope完美匹配：CKI是核酸/转录组学新方法，NAR Methods栏目理想
- HRT Atlas (ref 4) 已在NAR发表，引用链自然
- 4位专家中3位认为修复Critical issues后适合投稿
- 写作专家评分最高(8.0/10)：稿件结构、参考文献格式、图表规范均符合NAR要求
- OUP审稿周期相对合理（8-12周）

**劣势**:
- 统计专家评分最低(4.8/10)：FDR缺失、P值锚点问题、比值混淆是硬伤
- 需修复8个Critical issues中的至少6个

**投稿条件**:
1. 修复C1-C8全部Critical issues
2. 补做偏相关分析（M2）
3. 对brain 30个Strong候选做FDR校正或充分论证（C6）
4. 补充S6/S7补充图（C8）
5. 确认Cover Letter内容完整（6位审稿人、AI声明、ORCID）

#### 2. Bioinformatics — 推荐备选

**优势**:
- 方法学专家首选：更侧重方法本身而非生物学发现
- 对统计严谨性要求略低于NAR
- 审稿周期较短（6-10周）
- 接受纯计算方法论文

**劣势**:
- IF较低（~5.8）
- 需简化脑图谱和TCGA的生物学解读部分
- 稿件需重构为方法导向（原文偏生物学发现导向）

#### 3. Genome Biology — 需大幅修改

**优势**:
- 之前已投过（v16及更早版本），审稿人熟悉CKI
- IF较高（~12.3）
- 接受计算方法+生物学应用的综合论文

**劣势**:
- 之前Major Revision未完全解决审稿人意见
- 需补做大量额外分析（偏相关、FDR、置换验证）
- 审稿周期长（12-16周）
- 可能遇到同一审稿人，对修改质量要求更高

---

## 七、修复优先级清单

### 第一优先级：不可协商的Critical Issues（必须修复才能投稿）

| 编号 | 问题 | 修复工作量 | 涉及文件 |
|------|------|-----------|----------|
| C1 | Bootstrap范围矛盾 | 中 | 正文+补充+复现指南+Algorithm 1 |
| C2 | HRT Atlas使用矛盾 | 低 | 正文+补充材料 |
| C3 | TCGA癌种5 vs 6 | 低 | 补充图S3图例（或正文） |
| C4 | Figure 5数字38/17/59 | 低 | Figure 5图例 |
| C5 | Algorithm 1 B=1,000 | 低 | 补充材料Algorithm 1 |
| C6 | 无FDR校正 | 高 | 正文+补充+可能需重新分析 |
| C7 | P值锚点1 vs 1.54 | 中 | 正文Methods+Discussion |
| C8 | S6/S7补充图缺失 | 中 | 需生成2个PDF |

### 第二优先级：Major Issues（强烈建议修复）

| 编号 | 问题 | 修复工作量 |
|------|------|-----------|
| M1 | 复现指南4,851需说明 | 低 |
| M2 | 偏相关分析 | 高（需重新分析） |
| M3 | MANIFEST_v16残留 | 极低 |
| M6 | 残差模型置换验证 | 高 |

### 第三优先级：Minor Issues（建议修复但不阻碍投稿）

11项Minor issues，修复工作量均为低，可在最终校对阶段批量处理。

---

## 八、4位专家一致结论

**当前v17版本不建议直接投稿。** 必须先修复第一优先级的8个Critical issues。

**修复后预计评分提升**:
- 方法学: 6.8 -> ~7.5（修复C1/C2/C5后跨文档一致性解决）
- 数据与可复现性: 5.5 -> ~7.5（修复C1/C2/C8后复现指南与正文一致）
- 统计学: 4.8 -> ~6.5（修复C6/C7后统计严谨性显著改善）
- 写作与期刊适配: 7.3 -> ~8.0（修复C3/C4后图表/正文一致）
- **综合: 6.10 -> ~7.4（投稿准备度: 55% -> 75%）**

**推荐期刊**: 修复Critical issues后投NAR，Bioinformatics作为备选。

---

## 附录：v17 vs v14问题对比

| 维度 | v14主要问题 | v17状态 |
|------|------------|---------|
| JS对数底矛盾 | 正文/补充不一致 | 已解决 |
| 归一化方式矛盾 | 正文/补充不一致 | 已解决 |
| TCGA样本数矛盾 | 3,596 vs其他 | 已解决 |
| Bootstrap B值矛盾 | 正文内部不一致 | 已解决，但暴露跨文档矛盾 |
| P值公式不一致 | 三方不一致 | 正文+补充已统一，但Algorithm 1仍有B=1,000 |
| "proving"过强 | Discussion | 已改为"demonstrating" |
| **新: Bootstrap跨文档矛盾** | v14未审复现指南 | v17新发现（C1） |
| **新: HRT Atlas跨文档矛盾** | v14未审复现指南 | v17新发现（C2） |
| **新: TCGA癌种5 vs 6** | v14未发现 | v17新发现（C3） |
| **新: Figure 5数字矛盾** | v14未发现 | v17新发现（C4） |
| **新: S6/S7缺失** | v14未发现 | v17新发现（C8） |
| FDR校正缺失 | v14已识别 | v17仍未解决（C6） |
| P值锚点问题 | v14部分识别 | v17明确为Critical（C7） |
