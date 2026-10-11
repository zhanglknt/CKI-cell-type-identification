# Reviewer 3 — Handling Editor 编辑评估（Nature Communications 送审前）

**稿件**: CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases（nc68 投稿包）
**评估人**: reviewer3-editor（资深 handling editor 视角，独立评估）
**依据材料**: CKI_Manuscript_NC.docx（MAIN 5,258 词，摘要 184 词）、CKI_Supplementary_NC.docx（约 30,628 词，Notes 1–20 + Methods 5.1–5.14）、Cover Letter、主图 figure1–7（PDF 版面已逐张查看）、SI 结构。

---

## 总体评价（3 句）

这是一篇异常诚实、验证密度极高的方法学论文：把 Ka/Ks 的"内部参照"思想移植到表达比较，ω = k_f/k_n 配合 split-half 经验校准与 design-matched 置换零假设，构成一个"特异性优先"的差异指数，在漂移拒绝这一明确基准上确有可量化的优势。但概念推进是**增量式**的——housekeeping 归一化是成熟思想，真正的贡献是校准框架而非比值本身，而论文的招牌类比（Ka/Ks）恰恰被自己的数据反复削弱（基线 ω ≈ 7.70 ≠ 1、主要发现普遍 k_n 驱动、"绝对 ω 不可跨数据集迁移"），叙事强度与证据强度之间存在张力。作为编辑，我认为该稿达到了 NC 送审的证据门槛，但以当前叙事结构（防御性过重、MAIN 超字数、SI 达 3 万词）送审，审稿体验会放大"类比过度 + 贡献增量"的印象，送审后中稿前景中等偏下。

## 主要问题

1. **「Ka/Ks for expression」叙事的自我瓦解风险。** Ka/Ks 的力量来自 Ks 的近似中性与 ω > 1 的直觉判读；CKI 的对照基线是 7.70（Fig. 1e 明确显示 ω = 1 从未出现），需要 ω_cal = ω/7.70 且该系数 dataset-relative（脑 9.73、Tabula Sapiens 7.67），tier 阈值（<15/25/35）明确不可迁移。论文自己在 Discussion 中承认"heuristic index, not a formal measure of selection"。标题与摘要把类比放在最前，而正文的读者体验是"每出现一个 ω 结论就跟一句 denominator-driven 的限定"。编辑判断：类比作为**引入动机**成立，作为**标题级主张**偏弱；真正的卖点（per-comparison 内校准 + 设计匹配零假设 + studentization 使 null 分散度压缩 8 倍）被埋在 Discussion 第四段，应提为头条。

2. **头部生物学发现多为 k_n 驱动，与"functional divergence"的品牌词冲突。** TCGA pan-cancer reversal 是 k_n（TT k_n 升高 1.3–3.3 倍）驱动；脑区分化梯度 astrocyte↔Bergmann 是 k_n 主导（k_n 3.2 倍 vs k_f 2.0 倍，类均值 ω 与 k_n 相关 ρ = −0.73、与 k_f 仅 0.09）；cross-organ 排序中间段与 k_f-only 排序不一致（r = 0.23）。论文处理得很诚实（处处分解 k_f/k_n），但从广泛读者角度，"CKI 测到了功能分化"这一印象在 Results 内被反复撤销，留给读者的可带走结论主要是"housekeeping baseline 本身随组织/肿瘤状态变化"——这其实是个有趣的观察，但当前叙事没有把它扶正为一个独立卖点。

3. **叙事结构：Results 开篇即放理论段（Note 20 引导段）显得防御性过重。** "Decomposing transcriptomic variation"一节在读者尚未看到任何校准证据前，先给出 Lemma 1/Lemma 2/Proposition 3–5 的摘要，语气是"预先封堵质疑"而非"讲述发现"。建议压缩为 2–3 句并后移（Discussion 或 Methods 前的独立小节），把 Results 首屏留给 split-half 校准这一全文地基。此外全文的限定词密度（"descriptive""hypothesis-generating""tentatively""upper-bound""indicative only"）已高到影响可读性——诚实是优点，但应在正文保留结论性语言、把限定系统性地收进统一位置的"scope statement"。

4. **MAIN 超字数 + 图注过长 + SI 体量失控。** MAIN（摘要+Intro+Results+Discussion，不含 Methods/图注/参考文献）实测 5,258 词，超 NC 5,000 词上限约 5%；摘要 184 词合规。图注普遍是小论文（Figure 6 图注含 4 个统计结果的完整叙述），不符合 NC 图注规范。SI 约 3.06 万词、20 个 Notes、19 张补图、23 张补表外加 Reproducibility Guide——严谨性毋庸置疑，但审稿人负担巨大，且部分 Notes（如 Note 4 ratio-estimator、Note 16 维度不变性）可合并；建议给出 SI roadmap 并将 Notes 合并至 ~10 个。

5. **主图信息密度不均、个别图存在内部不一致。** Figure 2e 标题写"replicated on skin background: AUC = 0.91 (rank 1/6)"，图例却是 marrow 背景的 AUC 值（0.80/0.72/…），读者会困惑该面板展示的是哪个背景；Figure 1/2 中 k_n 标作 "neutral"、k_f 标作 "functional"（Fig. 1d 轴标签 "K_n (neutral)"），与正文反复强调"HK 并非机制中性"自相矛盾；Figure 3b 的 7 指标×3 tier 箱线图在印刷尺寸下不可读，Figure 3c 把 ω 的 T1 FPR = 28.6% 与 nominal 5% 虚线并置，视觉上直接削弱自己的核心卖点（虽正文解释为相对优势）；Figure 5 整体信息密度低（panel b 的 <15 阈值显任意、panel c 的器官对梯度无统计标注）；Figure 6a 的脑示意图风格接近 clip-art，与全刊图面水准有差距。Figure 4 与 Figure 7 质量最好，可作为统一风格的基准。

## 次要问题

- Figure 2b 的数值标注（1.5e-03 等科学计数法直接叠在柱上）不符合 NC 图面惯例；Fig. 1c 的 bootstrap 直方图与 Fig. 2a 信息重复，可合并。
- TCGA 部分是 bulk RNA-seq，与标题"cell atlases"的定位有轻微错位；作为应用示例可保留，但建议在摘要中明确"tissue-level, bulk resolution"以免读者预期错位（正文已做到，摘要仅隐含）。
- "ω 在 Tabula Sapiens 上与四个标准距离全部负相关"作为亮点写进 Introduction 末段，但 Results 自己分解出这主要是分母伪影（conditional on k_n 全部转正）——亮点段落在后文被自己撤销，建议 Introduction 中弱化。
- KRAS 分层结果（KW P = 7.8×10⁻⁷）有吸引力，但 ω 与生存无关（LIHC Cox HR 1.08, P = 0.467）削弱了临床相关性暗示；Cover Letter 未提这一点（可接受，但审稿人必问）。
- 建议审稿人名单（Theis、Welch、Linnarsson、Ståhl、Schäffer、Zemin Zhang）选择合理、覆盖单细胞方法与脑图谱，无利益冲突迹象；但 Ståhl（空间转录组）与本文主题相关性偏弱。
- LLM 使用声明、数据/代码可用性（GitHub tag + 双 Zenodo DOI + Dockerfile + CI）规范完整，符合 NC 要求。
- SI 中坦承 TCGA softmax 隐含幂变换"earlier versions did not disclose"并全量重算——处理得当，但这类表述在主文 Methods 中以一句话带过即可，当前略啰嗦。

## 评分（1–10）

| 维度 | 分数 | 一句话理由 |
|---|---|---|
| 新颖性 | 6 | 参照思想的移植 + 校准框架是真新意，但 housekeeping 归一化与比值 studentization 均为成熟构件，属增量组合而非范式推进 |
| 严谨性 | 8.5 | 校准、负对照、block-shuffle/donor-stratified 双零假设、消融与估计量敏感性一应俱全，诚实度罕见；扣分项为 per-pair 循环选基因导致的绝对值上偏与 TCGA per-cancer 固定 panel 检验的 anti-conservative 残留 |
| 广泛兴趣 | 6 | 单细胞方法读者会读；泛癌与脑图谱应用提供了跨领域钩子，但头部结论多为"baseline 变化"而非功能发现，对非计算读者的吸引力打折 |
| 可复现性 | 9 | 开源包 + 版本 tag + Zenodo 双 DOI + Docker + Reproducibility Guide + 全部中间表，几乎是教科书级 |

## 送审概率与中稿概率估计

- **送审概率：约 55%。** 验证密度、真实数据规模（3,535 TCGA 样本、88.8 万脑核、3.3M 核图集）与可复现工程足以让编辑愿意送审；风险点是概念增量感强、标题类比可能被资深编辑判定为包装过度，且 MAIN 超字数在初筛即暴露。
- **中稿概率（送审条件下）：约 35%。** 审稿人会认可严谨性与特异性优先的定位，但几乎必然质疑：(i) 基线 ω = 7.70 对 Ka/Ks 直觉的破坏；(ii) 主要发现 k_n 主导；(iii) 绝对值不可迁移限制实际采用。若作者按"必须改进项"重构叙事（把校准框架扶正为头条），中稿概率可升至 ~45–50%。

## 必须改进项（≤5 条）

1. **重构头条叙事**：把"per-comparison 内校准 + design-matched 零假设 + studentization"提为摘要与引言的核心贡献，Ka/Ks 类比降级为动机性引子；考虑修改标题（当前标题把最弱的主张放在最显眼位置）。
2. **压缩 MAIN 至 ≤5,000 词**：理论段移出 Results 开篇（压至 2–3 句或并入 Discussion/Methods 过渡），图注按 NC 规范重写（每条 ≤ ~150 词，统计细节移 SI），系统性降低正文限定词密度。
3. **修图**：统一 k_n = "baseline"（弃用 "neutral"）命名；修复 Figure 2e 标题/图例的背景不一致；放大 Figure 3b/5c/6c-d 字号；Figure 4/7 作为风格基准重绘 Figure 6a。
4. **给 ω = 7.70 一个读者友好的正面安放**：在 Fig. 1 与引言中把"经验基线 ≠ 1"作为方法特征（而非补丁）呈现，明确 ω_cal 的使用规则，删除正文中重复出现的同一限定。
5. **SI 瘦身与导航**：Notes 20 → 合并为 ~10 个（理论、校准、漂移阶梯、TCGA、脑图谱、零假设对照、外部对照各一），卷首加 SI roadmap；将 Note 20 的理论框架与主文的 2–3 句摘要严格对应，避免审稿人在 3 万词中迷路。

---
*评估纪律声明：以上全部判断仅基于投稿包所见文档与图面，未运行代码、未核对原始数据数值。*
