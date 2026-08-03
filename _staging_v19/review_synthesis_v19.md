# CKI v19 NAR 投稿 — 专家团综合审稿报告

**审稿日期**: 2026-07-29
**审稿专家**: 方法学(#1) + 统计学(#2) + 生物学(#3) + 写作/期刊策略(#4)

---

## 总体评分

| 维度 | 评分 | 专家 |
|------|------|------|
| 方法学/算法 | 6.0/10 | #1 |
| 统计学/数据分析 | 5.5/10 | #2 |
| 生物学解释 | 7.0/10 | #3 |
| 写作/期刊策略 | 6.0/10 | #4 |
| **综合** | **6.1/10** | — |

---

## 期刊推荐

| 期刊 | 估中率 | 依据 |
|------|--------|------|
| **NAR** (首选) | 30-35% | 方法+基因组学适配度好；需修复所有Critical问题后投稿 |
| **Bioinformatics** (备选) | 45-55% | 对启发性方法更宽容，CKI包+复现指南是加分项 |
| **Genome Biology** (备选) | 25-30% | 影响因子更高，但对理论严谨性要求也更高 |

---

## Critical Issues 汇总（17项，提交前必须修复）

### 第一优先级：代码/算法变更（5项）

**C-M1. 校准结果破坏核心解释框架** (Methods C1)
- ω=6.67的empirical baseline意味着"ω≈1=基线"这个解释框架在实际中从不成立。同一群体的分裂对照组竟然ω=6.67，那ω=8.0的意义是什么？建议实施校准归一化：ω_cal = ω_obs / ω_baseline，或至少在所有图表中同时报告原始ω和校准ω。

**C-M2. JS散度在不同维度基因集上的不可比性** (Methods C2)
- k_n在1,130维simplex上计算，k_f在200-2,000维上计算，更高维度会更分散概率质量。需要数学证明或模拟验证维度不变性，或使用dimension-matched子采样策略。

**C-M3. 混合方案（global k_n, per-pair k_f）逻辑矛盾** (Methods C3)
- 当k_n为全局常数时，ω退化为k_f的缩放版，失去了"基线归一化"的全部意义。需要报告k_n的跨pair变异性(CV)，并同时报告pair-specific k_n结果。

**C-S1. Bootstrap B=1,000解析度不足以支撑脑图谱FDR校正** (Statistics C1)
- 脑图谱31,764次检验，BH阈值在rank=1时为1.57×10⁻⁶，但最小可解析P≈0.001，差距~635倍。建议B≥10,000（至少），或采用自适应置换策略。

**C-S2. ω点估计全文缺乏置信区间** (Statistics C2)
- 所有主要结果只报告ω的点估计（均值/中位数）。引导重抽样数据已存在，计算百分位CI的边际成本为零。对所有key results报告95% bootstrap CI。

### 第二优先级：文稿文本修复（6项）

**C-W1. Introduction中的未填充Python模板变量** (Writing C1)
- 行16出现 `{_mc["control_mean"]:.2f}` 而非6.67。直接可见的粗心标记，编辑会立刻拒绝。

**C-W2. 事实性错误：人ω"高于"鼠** (Writing C2)
- 行51称人ω(mean 14.23) "substantively higher" than mouse(27.31)——实际上人类更低。修正方向或数值。

**C-W3. Tables 1-2为空占位符** (Writing C3)
- 仅有关注但无表格内容。NAR要求表格嵌入稿件或作为独立文件并清楚交叉引用。

**C-W4. 引用赋值错误** (Writing C4)
- 行65引用ref 32（Tran, batch correction）用于内皮细胞生物学描述。应更正为ref 36（Wälchli, 脑血管图谱）。

**C-W5. 多条参考文献未被引用** (Writing C5)
- Ref 16, 19, 24, 30, 31, 33, 36 在正文中没有任何引用。逐条检查：删除真正不需要的，或为需要的（如Nei & Gojobori在Ka/Ks引入处、Storey在FDR首次提及时）添加引用。

**C-B2. "migration detection"表述误导** (Biology C2)
- 30个Strong信号中有29个反映发育历史/compartmentalization，而非出生后细胞迁移。区分"developmental origin signature"和"postnatal migration"。

### 第三优先级：统计/分析补充（6项）

**C-S3. 乘法残差模型缺乏形式化统计推断** (Statistics C3)
- Strong/Moderate/Weak三级阈值为任意设定(0.3/0.5/0.75)，无empirical null校准。实施标签置换null分布，计算FDR-adjusted P值。OPC阴性对照为定性验证，不能替代形式化统计。

**C-S4. 跨器官保守排序样本量严重不足** (Statistics C4)
- Memory B cells n=1, Smooth muscle n=1, Endothelial n=3却以精确均值参与排名。至少为每个cell-type提供bootstrap CI，或从排名中移除n<5的类型。

**C-S5. ω分布属性未表征** (Statistics C5)
- ω=k_f/k_n为ratio分布，必然右偏重尾。k_n floor=1e-4产生上界效应。Cohen's d默认正态性假设未经检验。补充ω分布的histogram/Q-Q plot，如null非正态则避免使用Cohen's d命名。

**C-S6. TCGA配对分析统计效力极低** (Statistics C6)
- 配对n=2-5/癌种却报Mann-Whitney P值。n=2时最小双边P=0.33，α=0.05无法拒绝。移除形式化假设检验，仅报告描述性统计。

**C-B1. HK基因中性假设缺乏机理基础** (Biology C1)
- HRT Atlas是经验定义，不像同义位点有机制性中性基础。强化讨论此局限，或补充证据表明HK基因表达方差确实不受选择压力。

**C-B3. TCGA"收敛"解释过度** (Biology C3)
- NN/TT>1.0有细胞组成差异、癌周炎症、RNA质量等多种替代解释。将TCGA分析定性为探索性分析，讨论bulk-level的固有局限。

---

## Major Issues 汇总（19项）

### 方法学 (3项)
- M-M1: 缺乏含ground truth的仿真验证
- M-M2: 方法比较不系统（无SAMap/SATURN/CACIMAR量化对比）
- M-M3: 乘法残差模型缺乏统计严谨性（与C-S3重复，独立关注）

### 方法学附加 (2项)
- M-M4: TCGA bulk分析混叠细胞组成与转录差异
- M-M5: 关键参数(ε=1e-9, B=1000, top-200 DE, log底数, softmax温度)缺乏充分理由

### 统计学 (6项)
- M-S1: 单侧检验选择缺乏充分论证
- M-S2: BH-FDR per-dataset界限可能掩盖跨数据集比较
- M-S3: Spearman相关缺乏bootstrap CI
- M-S4: 经验校准基线仅n=6（7.6倍范围）
- M-S5: PAM50 Normal-like (n=7)和Edmondson G4 (n=11)亚组太小
- M-S6: 全局均值ω=8.01与星形胶质细胞均值14.36的表面矛盾

### 生物学 (5项)
- M-B1: 缺乏正式跨物种分析
- M-B2: 仅与通用距离度量比较，未与scVI/SATURN/CACIMAR对比
- M-B3: 乘法残差模型对31,764次检验缺乏形式化FDR控制
- M-B4: PAM50/Edmondson生物学解释过浅（可能仅是增殖效应）
- M-B5: 跨器官分析许多cell type样本量过小(n=1或n=3)

### 写作/策略 (3项)
- M-W1: Abstract "confirmed baseline behavior"夸大——ω=6.67不是"baseline behavior"
- M-W2: Abstract "developmental origin signatures"类别归化不准确
- M-W3: Cover Letter "orthogonal"过度声称（与正文Discussion矛盾）

### 写作/策略附加 (4项)
- M-W4: Figure 5 legend "between human and mouse"错误（应为human only）
- M-W5: Graphical Abstract为占位符
- M-W6: 跨器官pair计数不一致（59 vs 60）
- M-W7: Figure legends缺乏统一统计细节

---

## 四专家交叉共识

以下问题在多份审稿中独立提出，说明是共识性问题：

1. **校准基线问题 ω=6.67** — 方法学C1 + 写作M1 + 统计学C2/M4。三位专家独立指出：ω=6.67 not ≈1 是一个conceptual integrity问题。

2. **Bootstrap分辨率不足 (B=1,000)** — 统计学C1 + 方法学M5。脑图谱31,764个检验无法在B=1000下获得足够的P值解析度。

3. **乘法残差模型无形式化统计推断** — 统计学C3 + 方法学M3 + 生物学M3。阈值任意，无null分布。

4. **Sample size: n=1的cell type参与排名** — 统计学C4 + 生物学M5。Memory B细胞和Smooth muscle仅有1个比较却被赋予精确排名。

5. **缺乏与SAMap/SATURN/CACIMAR的量化对比** — 方法学M2 + 生物学M2。当前仅与通用距离度量比较。

6. **缺乏仿真ground truth验证** — 方法学M1 + 统计学C5。所有结论来自真实数据，无受控仿真基准。

---

## 修复策略与时间估算

| 阶段 | 内容 | 涉及Critical | 估算工时 |
|------|------|------------|---------|
| Phase A: 文本修补 | W-C1~C5 + B-C2等6项文本错误 | 6项 | 1-2小时 |
| Phase B: 统计升级 | S-C1(B值)+S-C2(CI)+S-C3(null分布)+S-C5(分布属性) | 4项 | 4-8小时（重跑bootstrap） |
| Phase C: 方法学加固 | M-C1(校准归一化)+M-C2(维度匹配)+M-C3(混合方案) | 3项 | 8-16小时（代码变更+重算） |
| Phase D: 解释修正 | B-C1(HK中性)+B-C3(TCGA收敛)+S-C4/S-C6(样本量) | 4项 | 2-4小时（文本修订） |

**总计**: 约15-30小时工作量（不含bootstrap计算时间）

---

## 最终建议

**稿件当前状态**: 准备度约50%，不建议以当前状态投稿NAR。修复17项Critical issue后预计准备度可升至70-75%，综合评分6.1→~7.0。

**建议投稿策略**:
1. 完成Phase A（文本修补）→ 可满足内部审阅标准
2. 完成Phase B（统计升级）→ 统计严谨性达标
3. 完成Phase C（方法学加固）→ 核心算法可信度达标
4. 完成Phase D（解释修正）→ 生物学公允性达标
5. 全部完成后重跑全流程 → 投稿NAR

**如果不做Phase C**（方法学加固）: 建议转投Bioinformatics（对启发性方法更宽容），估中率45-55%。

---
*报告由4位独立专家审稿并汇总生成。*
