# NC 审稿报告 — Reviewer 2（单细胞转录组学与计算生物学应用）

**稿件**: CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases (nc68)
**审阅范围**: 主文全文；SI Notes 3, 6, 9, 10, 11, 17, 18, 19（另浏览 Notes 5, 8, 14, 15, 16, 20）；Cover Letter

---

## 总体评价（3 句）

CKI 将 Ka/Ks 的内部基线思想移植到表达比较：ω = k_f/k_n，k_f 取自细胞身份基因、k_n 取自 housekeeping 基因，两者均为 pseudobulk 上的 JS 散度。作者的自证与自我限定工作异常充分（SI 20 个 Notes 中大量"打脸自己"的对照），这种诚实在方法学论文中罕见且值得肯定；但恰恰由这些对照可知：默认的 per-pair top-200 面板是循环选择（k_f 中位膨胀 1.61×）、k_n 在脑图谱中被证明主要是类大小/采样噪声伪影、且作者在真实扰动场景亲自推荐用 MELD/scDist 或自家 k_f 而非 ω。综合判断：这是一个有启发性但生态位狭窄的工具，其最响亮的生物学标题（脑区"分化梯度"、跨器官保守性排序）都被作者自己的分解分析证明为分母驱动，与 NC 方法学论文所需的"不可替代的发现"存在距离。

---

## Major concerns

### M1. 与单细胞领域现行方法的基准比较不充分，基线多为稻草人
**证据**：方法比较部分（Methods "Method comparison"；Fig. 2d, 2e）的全部定量基准对象是原始距离度量——raw JS、cosine、Spearman、marker Jaccard——这些是任何严肃从业者在有批次/供体结构的图谱数据上都不会直接使用的度量。唯一现代基线是 MELD 和 scDist，且（i）scDist 用的是 **Python 近似实现**，作者自己承认"should be re-verified against the R original"（主文 Limitations (iv)）；（ii）在 IFN-β 数据上 MELD 的类内分离 AUC 达 0.997–0.9998，而 ω 仅 0.55–0.92（主文 "Perturbation-response boundaries"）。作者的回应是"问题不同"（specificity-first），但 CKI 宣称的应用场景——图谱尺度细胞状态变化检测——正是 pseudobulk 差异表达效应量（edgeR/DESeq2/dreamlet 路线）、差异丰度方法（Milo、scCODA）与扰动响应方法（Augur 只做了 n=10 的相关性对照，ρ=0.442 不显著，Note 15）的领地，文中**没有任何与 pseudobulk DE 效应量的头对头比较**，而那是该领域的事实默认做法。此外 AUC = 0.80 的标题成绩是在把 δ ≥ 0.25 的弱信号并入"功能类"的混合任务上取得的，而阈值化检测在 marrow 背景上 δ=1 时 0/150 检出（主文 Results），"retaining biological sensitivity"（Abstract）与此明显张力。
**严重度**：高。当前证据不能说服本领域读者 CKI 在其宣称生态位内优于（或互补于）现有默认工具链。

### M2. 交付工具的默认方案是循环选择，headline 量级被系统性放大
**证据**：k_f 的身份基因是"按同一对 pseudobulk 的绝对差"选出的 top-200（Methods: func_method = "pairwise_absdiff"）。作者自己的固定面板消融（SI Note 9）显示：循环面板使 k_f 相对 leave-pair-out 中位膨胀 **1.61×**（IQR 1.27–2.07），相对固定/未筛选面板膨胀 6.1–7.3×；grand mean ω 从 38.55（S0）跌到 26.5（S2）/6.5（S1）；绝对分层阈值（ω < 15/25/35）不可跨方案迁移。排序结论稳健（ρ = 0.92–0.94）值得肯定，但这挽救的是排序而非工具交付形态：用户拿到的默认输出量级是被观测差异本身选出来的，跨数据集/跨方案不可比——而"图谱间、跨场景比较"正是论文卖点之一。另注意 top-200 按绝对均值差选取，无任何方差加权或检验，小样本 pseudobulk 上噪声基因会主导面板。
**严重度**：高。至少应将 leave-pair-out 或固定面板设为包默认，或在主文明确 CKI 仅限排序用途。

### M3. housekeeping 锚点的来源与性质未被验证，且脑图谱 k_n 被证明主要是采样伪影——与标题生物学声称直接冲突
**证据**：(i) HRT Atlas v1.0 由**bulk RNA-seq** 挖掘而来（NAR 2021），将其作为单核转录组的"中性锚"存在域错配，文中无任何在 snRNA-seq 上验证该面板"housekeeping 性"的分析，也无替代 HK 面板（如 Eisenberg & Levanon，仅被引用未被用作消融）的敏感性分析。(ii) SI Note 11：类水平 k_n 与类大小显著负相关（Spearman ρ = −0.648, P = 0.043），equal-n 降采样**完全消除** k_n 排序（ρ = −0.055, P = 0.88），Bergmann glia 的 k_n 升高"largely a class-size artefact"。但主文与 Abstract 仍以"quantified a regional differentiation gradient, largely k_n-driven"为脑图谱的核心发现，主文自己承认梯度是"k_n-dominated"（Discussion）。换言之：标题里的"区域分化梯度"在作者自己的分解下 = 一个被证明主要由采样噪声驱动的分母效应。Abstract 的表述（暗示生物学梯度）与 SI 证据不相容。(iii) Note 17 进一步显示 k_n 的可移植性边界：在脑设计中 k_n 随谱系距离上升（ρ = 0.300），在 Tabula Sapiens 中为零——k_n 追踪的是"该设计恰好固定住的那种基线变异"，不是普适中性基线。
**严重度**：高。这直接削弱论文的生物学发现支柱；需要重新定位（k_n 作为噪声代理的 studentization 是正当的——Note 20 的论证成立——但那就不能同时把 k_n 驱动当作生物学发现来宣传）。

### M4. 头部统计量存在严重伪重复，4 个供体撑不起 P < 10⁻³⁰⁰
**证据**：脑图谱全部推断建立在 **4 个供体**上（作者自述候选目录"inheriting the four-donor structure"；donor bootstrap 重采样 4 个供体；equal-n 对照的 donor 级 CI [0.80, 2.34] 包含 1，Note 11）。但 Abstract 与 Results  headline 使用跨 2,995 对 vs 31,764 对 pseudobulk pair 的 Mann–Whitney P < 10⁻³⁰⁰（z = 52.6，Note 18）——把所有 pair 当独立样本，而有效样本量是供体×区域。作者拥有正确的检验（block-shuffle：MGE 在置换地板 P = 0.001、Upper-layer IT P = 0.014、thalamic P = 0.163），却把描述性的池化 MWU 放在头部位置。同理 TCGA 部分的相关性 P 值（如 ρ = 0.387, P < 10⁻³⁰⁰）被作者自己标注"treat pairs as independent and are reported as descriptive only"——这种双重标准不应出现在 headline。
**严重度**：高（统计校准层面）。必须改为以设计匹配的 block-shuffle/供体级推断作为 headline。

### M5. 对本领域从业者的实际效用有限：生态位被作者自己的结果压缩到很窄
**证据**：作者自己给出的边界包括——操作窗口 ~50–200 细胞/组（超过 ~500 细胞置换检验失效，主文 Limitations (iv)）；对移动 HK 锚的扰动结构性失明（IFN-β CD14+ 单核细胞 ω AUC 0.55 vs k_f 0.98，Note 8；500 基因位移仿真 AUC 崩至 0.05–0.13）；绝对 ω 不可跨数据集迁移（小鼠 7.70 / 脑 9.73 / TS 7.67，Note 3）；跨类比较"k_n anchor is not calibrated across cell types"（Table 1 注）。再叠加作者的建议"for maximal power on broad perturbations use MELD, scDist, or CKI's own k_f"，ω 剩余的正当用途是：**单一数据集内、同方案下的保守、经校准的成对筛查**。这个用途真实存在（技术重复上 FPR 最低、漂移拒绝确实出色），但脑筛查的实际交付物是 39 个 Strong 候选、**无一通过 FDR**（min q = 0.520，且作者承认在 B = 1,000 下 q < 0.05 在原理上不可达）。作为审稿人问自己"我会用吗"：我可能在 pseudobulk DE 之外把它作为辅助描述统计量，但不会作为任何主要结论的依据。
**严重度**：高（对广泛兴趣/意义维度）。

### M6. 四大支柱之一的 TCGA 分析是 bulk 而非单细胞，且在单细胞分辨率未验证
**证据**：泛癌反转（NN > TT）发现本身有趣、对照扎实（Note 10 的组成校正、GTEx 参照），但全部基于 TCGA bulk TPM；作者承认"we report all TCGA findings as tissue-level divergence at bulk resolution, pending single-cell validation"（Results）。一篇以单细胞图谱为框架的方法学论文把 bulk 结果作为封面信四大支柱之二，生物学解释（"肿瘤 housekeeping 基线升高"）在缺乏单细胞验证时也可以是纯度/组成/RNA 质量的残余混杂——作者的 marker 面板回归在 LIHC/KIRC 吸收 20–44% 系数（Note 10），恰说明组成贡献不可忽略且跨癌种异质。
**严重度**：中。不需要删除，但应在 Abstract 中明示 bulk 性质并降格表述。

---

## Minor concerns

1. **Marker Jaccard 在 T1 的 FPR（19.9%）低于 ω（28.6%）**（Fig. 3c），"ω misreported least among continuous divergence metrics"的措辞正确但 Abstract 的"the lowest false-report rate"未限定范围，建议 Abstract 加"continuous"限定词。
2. **跨器官"CKI 是唯一把同器官异类型排在异器官之上的度量"**（Results）随后被分解证明是 k_n 效应（同器官 HK 基线更稳，P = 3.0 × 10⁻¹⁶，k_f 无差异 P = 0.60）——该"独特行为"应在同一段落即时标注为分母伪影，而非留给读者自行拼接。
3. **pseudobulk 定义非标准且跨管线不一致**：脑用 softmax(log1p(mean counts))，小鼠/人 pilot 用 softmax(mean(log1p))（Methods）；且均值-of-log 表达而非标准 raw-count 求和 pseudobulk。作者披露了不一致并禁止跨管线迁移校准常数，但一个工具应有唯一规范计算路径。
4. **数据可得性日期疑误**：GTEx "accessed September 2026"与 Tabula Sapiens/脑图谱 "accessed July 2025"并置，建议核对（若为笔误请更正）。
5. N2 基因身份交换中性模型下所有度量 FPR = 1.00（Note 6）——ω 对该类"中性"不优于无锚度量；作者处理诚实，但 Abstract 的特异性声称应限定为"compositional/multiplicative drift"。
6. 跨器官排序 Table 1 中 Endothelial/Erythrocytes 均 n = 3 pairs，主文已标"suggestive only"，但 Fig. 5 叙事仍给出较强语气，建议图注同步降格。
7. SEA-AD 疾病锚（Note 19）方向性但全部 sub-threshold（min q = 0.145），作为正对照合格；建议主文明确其"pipeline responds to known biology"的定位（Discussion 已基本做到），避免被读为 AD 发现。
8. Cover Letter "to our knowledge, the first per-comparison, design-testable implementation..." 为过度声称，差异丰度与 pseudobulk+置换框架已有先例，建议软化。

### 缺失的关键对照/敏感性分析（建议补充）
- **与 pseudobulk DE 效应量的头对头基准**（IFN-β 与脑漂移阶梯上，edgeR/DESeq2 式 pseudobulk |logFC| 或效应量作为基线）——目前最要命的缺口。
- **scDist 用 R 原版重跑**（作者已自认应做）。
- **替代 HK 面板消融**：Eisenberg & Levanon 列表、或数据驱动但留出式的 HK 集，检验 k_n 结论对面板选择的敏感性。
- **k_n 与独立技术噪声度量的相关性验证**（如检测深度/UMI 之外的内标或 spike-in 类参照），否则"基线率"的身份只是假设。
- 神经 superclass 分析（Note 18）类大小 222k–455k vs 非神经元类的大小差异，重复了 M3 的类大小混杂，建议在该对比中做 size-matched 对照。

---

## 评分（1–10）

| 维度 | 分数 | 一句话理由 |
|---|---|---|
| 新颖性 | 6 | Ka/Ks 移植的框架感新鲜，但技术实质是带循环基因选择的 studentized JS 比值；与 studentization/噪声文献的连续性作者自己也承认 |
| 严谨性 | 7 | 自证体系罕见地完备（Note 3/9/11/16/20 等），但头部统计伪重复、默认面板循环、bulk 面板作 snRNA-seq 锚三处硬伤 |
| 广泛兴趣 | 4 | 生态位被作者自己的结果压缩为"单数据集内保守筛查"；发现端全部重度 hedge（脑梯度=分母伪影、跨器官=描述性、TCGA=bulk） |
| 可复现性 | 8 | 包+Docker+Zenodo+固定种子+脚本索引+复查值，高于领域平均；扣分为管线聚合顺序不一致与 scDist 近似实现 |

## NC 中稿概率估计

**约 15%**。理由：验证文化达到甚至超过 NC 方法学论文的水准，但作者自己的对照已证明 headline 生物学声称主要由分母/采样伪影驱动，且在其宣称生态位内缺少对领域默认工具（pseudobulk DE、差异丰度方法）的公平基准，按 NC 对方法学论文"广泛兴趣+不可替代性"的标准，当前版本大概率在审稿阶段被要求大修后仍难以证明增量。

## 必须修复项（≤5 条）

1. **补现代基线**：在 IFN-β 与脑漂移阶梯上与 pseudobulk DE 效应量头对头比较；scDist 用 R 原版重跑；至少讨论 Milo/scCODA 类丰度方法的互补边界。
2. **重新定位 k_n 与脑梯度声称**：调和 Note 11（k_n 排序=类大小伪影）与 Abstract/Results 的"区域分化梯度"叙事——要么在 snRNA-seq 上验证/消融 HK 面板，要么把梯度从生物学发现降格为"经校准的相对描述"，Abstract 同步修改。
3. **消除头部伪重复**：P < 10⁻³⁰⁰ 的池化 Mann–Whitney 不得作为 headline，改为 block-shuffle/供体级推断的数字（Fig. 7a 已存在，提为主位）。
4. **修复默认方案循环性**：leave-pair-out 或固定面板设为包默认并重报绝对量级与分层阈值；或主文明确 CKI 仅支持排序用途、绝对 ω 仅为上界诊断。
5. **Abstract 如实限定生态位**：写明"单数据集内、同方案、保守校准筛查"的适用范围，并限定特异性声称（continuous metrics、compositional drift）与 TCGA 的 bulk 性质。
