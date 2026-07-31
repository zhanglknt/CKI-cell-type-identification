# CKI 算法稿件专家团综合审稿报告

**会议时间**: 2026-07-26
**专家团成员**: methods-reviewer, stats-reviewer, data-reviewer, journal-reviewer
**稿件版本**: v10 (version3/CKI_NAR_Submission_v10.zip)

---

## 一、综合评分

| 维度 | 评分 | 评审专家 |
|------|------|---------|
| 算法方法学 | 6/10 | methods-reviewer |
| 统计严谨性 | 4/10 | stats-reviewer |
| 数据完整性 | 4/10 | data-reviewer |
| 写作质量 | 6.5/10 | journal-reviewer |
| **加权综合** | **5.1/10** | — |

**总体判断**: 稿件概念框架有启发性（Ka/Ks类比思路 + 转录组差异的可分解性），验证广度强（4个数据集、3个物种、~百万细胞），代码实现质量良好。但存在**3个Critical级数据错误**和**多处方法学论证缺口**，需全面修订后可投稿。不建议在修复前投稿。

---

## 二、四维交叉共识——Critical问题（所有审稿人一致）

### C1. k_n统计值brain数据误用为human数据（4/4审稿人确认）

**这是最严重的问题，4位审稿人独立确认。**

| 统计量 | 稿件值（P19/P45） | 实际Human值 | 实际Brain值 | 误用来源 |
|--------|------------------|------------|------------|---------|
| k_n median | 0.0086 | **0.034** | 0.0086 | Brain |
| k_n range | 0.0004–0.106 | **0.0018–0.221** | 0.0004–0.106 | Brain |
| k_n < 0.001 | 48对 | **0对** | 48对 | Brain |
| ω < 15比例 | 93.6% | **56.3%** | 88.7% (OPC 93.6%) | Brain OPC子集 |

**影响范围**: P19 (Methods), P45 (Results) — CKI算法的核心参数被错误描述，直接削弱方法可信度。

### C2. Mouse mean ω = 7.07 来源不明（4/4审稿人确认）

- 稿件P50: "mouse (mean ω = 7.07)"
- Mouse pilot 整体: mean = 5.27 (n=15)
- 7.07 来源: X_cross 类别仅 2对
- Full matrix (703对): mean = 7.62
- **结论**: 用 n=2 的子类均值代表整体 mouse 水平，统计上严重误导

### C3. P45内部不一致: 0.93% vs 0.15%（4/4审稿人确认）

同一稿件内对"48对"给出两个不同百分比：
- P19: "48 of 5,151 pairs (0.93%)" → 48/5151=0.93%（但48来自brain）
- P45: "48 pairs (0.15% of 5,151)" → 48/5151≠0.15%（算术错误；0.15%是brain的48/31764）

---

## 三、方法学Critical问题（methods-reviewer独报）

### C4. Hybrid方案的比值不一致性

k_n全局计算（固定HK基因集~1000+基因）vs k_f逐对计算（每对不同DE基因），分子分母数值尺度不一致：
- ω系统性膨胀
- 不同配对的ω不可直接比较（不同DE基因集）
- 稿件P49的"normalization remains internally valid"论断错误

### C5. Ka/Ks类比过度使用

Discussion中有诚实disclaimer，但Abstract/Introduction/Figure 1A仍作为核心卖点。建议将disclaimer前移到Introduction首次引入类比处。

### C6. k_n下限阈值不一致

稿件 P19: k_n ≥ 0.001；代码 core.py:255: kn_min = 1e-4。10倍差异，直接影响ω数值。

---

## 四、统计Critical问题（stats-reviewer独报）

### C7. Bootstrap分辨率不足以支撑FDR校正

B=1,000时最小P值=0.001，但BH FDR校正（q=0.05，5,151对）的第1个阈值=9.71×10⁻⁶ << 0.001。最显著的~100个检验无法区分P值。

### C8. Human数据CSV缺少bootstrap P值和q值

`phase33_v3_human_pairs.csv` 无p_value列，无法验证显著性声明。

---

## 五、Major问题（多审稿人共识）

### 共同Major（3/4审稿人）

| # | 问题 | 审稿人 |
|---|------|--------|
| M1 | Mouse pilot n=15不足（应使用703对的full matrix） | methods + stats + data |
| M2 | 跨器官保守性分析统计效力不足（n=1-3细胞类型） | methods + stats |
| M3 | Figure 5 legend严重损坏（P114混乱+P115用户重写） | methods + journal + data |

### 方法学Major（methods-reviewer）

| # | 问题 |
|---|------|
| M4 | HK"中性"假设验证不充分（低变异≠中性） |
| M5 | 校准 ω=1.54 偏离理论1.0达54%，未校正 |
| M6 | pairwise_de模式循环性 |

### 统计Major（stats-reviewer）

| # | 问题 |
|---|------|
| M7 | 效应量报告不完整（rank-biserial r、CI等缺失） |
| M8 | Multiplicative residual模型阈值缺乏正式统计推断 |

### 写作Major（journal-reviewer）

| # | 问题 |
|---|------|
| M9 | 4处文本损坏（P60/P62/P90/P52） |
| M10 | 3处中文标点混入英文正文（P54/P57/P72） |
| M11 | 参考文献格式全部不合NAR规范（40篇需重排） |
| M12 | 标题"Cell-state" vs GitHub "cell-type"命名不一致 |

---

## 六、数据错误全部清单（data-reviewer汇总）

### Critical错误（6项）
1. P19 k_n median: 0.0086 → **0.034**
2. P19 ω<15比例: 93.6% → **56.3%**
3. P45 k_n median: 0.0086 → **0.034**
4. P45 "99.6% control pairs k_n<0.05" → **100%**
5. P45 "48 pairs (0.15%)" → **0 pairs (0%)**
6. P50 mouse mean ω: 7.07 → **5.27** (pilot) / 7.62 (full)

### Moderate错误（8项）
7. P50 same_ct cross-organ ω: 8.70 → **8.65**
8. P50 diff_ct same-organ ω: 16.18 → **16.00**
9. P52 same-organ vs diff-organ ω: 16.18 vs 13.77 → **16.00 vs 13.58**
10. P60 Neutrophils SD: ±1.15 → **±1.22**
11. P61 cross-organ median ω: 6.9 → **8.71**
12. P61 organ means: Heart/Lung/Kidney/Spleen值无法从源文件验证
13. P63 Spearman r/n: -0.40~+0.02, n=60 → **-0.59~+0.04, n=59**
14. P25/P32/P57 TCGA数值内部不一致 (LUAD 497vs492, LIHC 289vs288)

### 已验证正确的数值: 38项 ✅
### 无法验证的数值: 9项

---

## 七、期刊推荐策略

| 排名 | 期刊 | IF | Scope | 接受率 | 策略 |
|------|------|-----|-------|--------|------|
| 1 | **NAR** | 16.7 | 4/5 | 15-20% | **首选**，维持当前目标 |
| 2 | **Genome Biology** | 12.3 | 4/5 | 15-20% | **最佳备选**，单细胞方法核心期刊 |
| 3 | **Bioinformatics** | 5.8 | 5/5 | 25-30% | **安全选择**，scope完美匹配 |
| 4 | Cell Systems | 9 | 4/5 | 12-18% | 系统生物学角度契合 |
| 5 | Cell Reports Methods | 7 | 4/5 | 20-25% | 新刊，方法导向 |

**推荐投稿策略**: 修复Critical问题 → NAR → 若拒稿 → Genome Biology → 若再拒 → Bioinformatics

---

## 八、推荐审稿人（6+1位）

Cover Letter建议推荐以下6位（覆盖领域、避免利益冲突）：

1. **Fabian Theis** (Helmholtz Munich) — fabian.theis@helmholtz-munich.de — scVI/scanpy
2. **Sarah Teichmann** (Sanger) — st1@sanger.ac.uk — Tabula Sapiens
3. **Joshua Welch** (U Michigan) — welchjd@umich.edu — 单细胞方法
4. **Jianzhi George Zhang** (U Michigan) — jianzhi@umich.edu — 分子进化/Ka/Ks
5. **Aaron Lun** (CRUK Cambridge) — aaron.lun@cruk.cam.ac.uk — 生信方法
6. **Hongkui Zeng** (Allen Institute) — hongkuiZ@alleninstitute.org — 脑细胞分类学

备选: **Daifeng Wang** (UW-Madison) — 细胞类型注释/脑图谱
避免: Ziheng Yang（稿件大量引用其工作，可能有利益冲突）

---

## 九、修复优先级路线图

### P0 — 投稿阻断项（6项，修复前不可投稿）

1. **修正k_n/ω统计值** (P19/P45): brain数据→human数据，6个统计量全部替换
2. **修正mouse ω=7.07** (P50): → 5.27 或 7.62（需确定上下文）
3. **修正ω<15比例** (P19): 93.6% → 56.3%
4. **修复Figure 5 legend**: 删除P114，接受P115
5. **修复4处文本损坏**: P60/P62/P90/P52
6. **替换3处中文标点**: P54/P57/P72

### P1 — 投稿前应修复（8项）

7. k_n阈值统一 (稿件0.001 vs 代码1e-4)
8. hybrid方案局限性声明
9. Ka/Ks disclaimer前移
10. 参考文献全部重排为NAR格式
11. 统一"Cell-state"命名
12. 分设Data/Code availability章节
13. 补充bootstrap P值和q值到CSV
14. 修正8项Moderate数据错误

### P2 — 建议改进（按时间可选）

15. 增加bootstrap B值或半解析方法
16. Mouse pilot换full matrix（703对）
17. 报告normalized ω
18. 增加效应量报告
19. Softmax vs sum-normalization敏感性分析
20. 删除Methods冗余

---

## 十、专家团总结

**共识**: CKI是一个概念有启发性、工程实现良好、验证广度强的工作，完全可以发表在NAR或同级别期刊上。当前v10版本的主要问题集中在：

1. **数据错误**（brain/human混淆）—— 必须修复，但不影响方法本身的有效性
2. **方法学论证不足**（hybrid方案、阈值、Ka/Ks类比定位）—— 可通过修改和补充分析解决
3. **写作质量问题**（text corruption、参考文献格式）—— 系统性但机械的工作

这些问题的共同特点是：**修复成本可控，不构成拒稿理由**。建议修复P0/P1项后投稿NAR。

---

*报告生成时间: 2026-07-26*
*审稿专家: methods-reviewer, stats-reviewer, data-reviewer, journal-reviewer*
*总评审轮次: 1轮*
