# nc68 审稿团汇总（5 人盲审，2026-10-11）

## 概率汇总

| 审稿人 | 视角 | 新颖 | 严谨 | 兴趣 | 复现 | NC 中稿概率 |
|---|---|---|---|---|---|---|
| R1 | 方法论/统计 | 6 | 5 | 6 | 9 | ~20% |
| R2 | 单细胞领域 | 6 | 7 | 4 | 8 | ~15% |
| R3 | NC 编辑 | 6 | 8.5 | 6 | 9 | 送审 55% / 中稿 35%（无条件 ≈19%） |
| R4 | 可复现性 | 7 | 8 | 6 | 8 | 60%（修归档后 70%） |
| R5 | 挑剔统计 | 7 | 5 | 5 | 9 | ~15% |

**共识区间 ~15–25%，中位 ~20%**。R4 的 60% 是工程质量视角（不评新颖性）；内容向审稿人（R1/R2/R5）收敛于 15–20%。与 nc67 期轨迹（15–25%）持平——nc68 理论化未提升概率，因为理论层自身被找出新伤。

## P0 事实性错误（投稿前必修，已 ground-truth 裁定）

1. **Note 20 §E(iii) FPR 张冠李戴**（R1+R5 独立发现，裁定成立）："k_f-only FPR 0.81–1.00" 实为 raw JS/cosine 值（SI para 167/193：HK 漂移 k_f 0.007、ω 0.000；N1 非 HK 漂移 raw JS 0.811/1.000、cosine 0.878/1.000）；N2 swap 下 ω 自身 FPR=1.00。修正方向：k_f-only 在组分漂移下同样特异，分母可测增益改挂「vs raw JS/cosine 0.55–1.00」+ 可识别性/学生化论证。仅此一处（68_gen_supplementary_nc.py:3165）。
2. **SI legends 头 "Figs. 1-18" 过时**（R4 发现，裁定成立）→ 1-19（68_gen:321）。
3. **归档版本脱节**（R4）：Code availability 引 tag v0.5.5，但 notebooks/85 不在其中（HEAD 领先 32 提交）→ 投稿前切新 tag + 新 Zenodo version DOI；CI 配置 HEAD 被删（仅 tag 有）。

## P1 统计口径（major revision 级，多方共识）

4. **摘要 P<10⁻³⁰⁰ 伪重复**（R1+R2+R5）：2,995/31,764 重叠配对池化 MWU；block-shuffle 只支持 3 个 superclass 中的 2 个（Thalamic P=0.163）→ 头条换设计匹配统计量或并列呈现。
5. **α↔基线算术链不闭合**（R1+R5）：脑 α 中位 14 vs 脑基线 9.73 差 44%，缺面板大小因子（~0.18）；α 仅零假设下验证、3.10 数据显示 2.2 倍群体散布 → 补恒等式或降级 "remarkably close" → "same order"。
6. **校准 CI 6 簇 percentile bootstrap**（R1+R5）：落在自家 Note 2 覆盖不足区（0.876）却未用其推荐的 studentized-t；AUC 3 簇同病。
7. **estimand 过度声称**（R1+R5）：E_f/E_b 是 post-selection 近似量，"precise biological quantity" 需降级并纳入选择膨胀。
8. **Prop 5（−0.18%）vs Note 4（−1.8%）数字未调和**（R1）。
9. **TCGA "robust" 偏强**（R1）：全部证据为 bootstrap CI，唯一设计匹配检验 P>0.9；主文置换 P（≤0.001/≥0.28）与 §3.13（0.003/0.21）对不上。

## P2 叙事与生态位

10. R3：真卖点（per-comparison 校准 + design-matched null + studentization 8 倍压缩）埋在 Discussion 第 4 段，应扶正为头条；Results 开篇 Note 20 引导段防御性过重；ω=7.70 正面安放；SI ~3 万词瘦身合并至 ~10 Notes + roadmap。
11. R2：基准不公——缺与 pseudobulk DE 效应量头对头；MELD AUC 0.997+ vs ω 0.55–0.92 且作者自推荐 MELD/scDist；脑区 headline 改用供体级统计（4 供体 P<10⁻³⁰⁰ 是伪重复）。

## 已裁定驳回的指控

- R3「MAIN 5,258 词超限」：口径差异。XV8 口径 Intro→Discussion = 4,994–4,996 ≤5,000 ✓；R3 口径含摘要（5,179–5,258）。NC 惯例主文词额不含摘要/方法/参考文献。
- R4「CV 1.21→0.148 硬编码无产物」：不成立。notebooks/85 产物 results/theory_diagnostics.csv 含全部 CV 值（omega_dispersion js=0.1481411310 等 6 行 summary）；68 硬编码打印值是稿件生成惯例。

## 修复执行记录（2026-10-11，nc69 轮）

**P0（全部落地）**
1. §E(iii) 改写完成（68_gen）：可测误差率增益改挂「vs raw JS/cosine 0.55–1.00」；如实写入 k_f-only 在组分漂移下同样特异（0.007–0.020）与 N2 swap 下全员 FPR=1.00；结论降为「ratio 结构 vs 无锚全局基线」。
2. SI legends 头 1-18→1-19 完成。
3. 新 tag + Zenodo 新 DOI：待重建后随提交执行（Zenodo 需用户开 socks5 代理）。

**P1（全部落地）**
4. 摘要伪重复 P 删除，改为「two of three superclasses above their block-shuffle nulls」；Results 句改为设计匹配口径（P = 0.001, 0.014, 0.163 三值全列，净 −3 词）；Fig 7 图注 Mann–Whitney 标注 descriptive/pseudoreplicated。
5. α↔基线降级完成：「remarkably close」→「same order」+ 面板大小/组成因子与 k_f 尺度展开误差解释缺口，校准常数理论解读限定「only up to these factors」。
6. MS 校准基线 CI 加「slightly anti-conservative at six populations」；SI 小簇校正段补 7.70 基线 CI 同局限声明。
7. estimand 降级：「precise biological quantity」→ post-selection panel 条件近似 + 仅 k_n 尺度定量。
8. Prop 5 vs Note 4 调和：补聚合口径句（pooled 含小分母组 +6.5% vs 类水平均值输入；两种聚合夹出同一小效应）。
9. TCGA：主文置换 P 改精确口径（KRAS–WT ≤0.001、EGFR–WT ≥0.28，与 §3.13 调整模型置换一致；未调整 0.003/0.21 为另一分析，不再混淆）；Intro「robust」→「retained after purity and smoking adjustment」。

**P2 处置**
10. SI roadmap 段已加（TOC 后，按问题导航到 Note 群）。R3 其余叙事项（Discussion 头条重排、Results 引导段减防御、ω=7.70 正面安放）→ **本轮不动**：MAIN 词额 4,999/5,000 无空间，结构性重排风险大于收益，留作返修轮选项。
11. **SI 瘦身（3 万词→~10 Notes）：拒绝**。理由：NC 现刊风格 SI 按 MS 首引排序、全文交叉引用已断言锁定（126 项 SI 断言），合并重排会触发全链重编号且零收益于审稿核心关切；roadmap 已解决导航问题。**pseudobulk DE 头对头基准（R2）与供体级脑区统计：标注为返修轮计划项**——需新计算（MELD/scDist 同条件对比、供体级 meta-analytic P），当前轮次只做口径诚实化（P0-4 已完成伪重复 P 降级）。

## 各报告原文

- results/audit/_nc68_panel_r1.md（方法论）
- results/audit/_nc68_panel_r2.md（单细胞）
- results/audit/_nc68_panel_r3.md（编辑）
- results/audit/_nc68_panel_r4.md（可复现性）
- results/audit/_nc68_panel_r5.md（挑剔统计）
