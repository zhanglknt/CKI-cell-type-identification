**总分：6.0 / 10**
**建议：Major Revision**
**判定标签：脑图谱结论已诚实降级到 housekeeping-anchored class-level，但 4 供体的有效独立单元、k_n 主导下 PMI/ambient/doublet 未建模、以及 Fig 4 图注对 anchor-collapse 与 Thalamic 功效的漏报，使核心梯度与超类 elevation 仍属未定论的假设生成。**

# 独立盲审报告 R5（脑图谱 / 神经科学 / 单细胞脑组织）

审阅对象：CKI 投稿包 v0.6.4（nc85 轮次），仅依据 `_nc85_review_materials/` 内 `ms.txt`、`si.txt`、`cl.txt`、`guide.txt`、`tables_overview.txt`、`manifest.txt`、`round.txt` 判断。未查阅任何其他轮次报告、专家团汇总、事实核查或修复报告，未联网检索作者身份，未读取记忆文件。

---

## 评分表（6 维）

| 维度 | 分数 | 理由 |
|---|---|---|
| 新颖性 | 6.0 | 把 Ka/Ks 启发式迁移为 HK-anchor 的 studentized 比值、并系统给出"分母失效"的 caution，有一定方法新意；但作者自认"recombines established ideas"（`ms.txt:64`，参考基因归一化、HK 方差约束、noise floor 的重组），脑端产出是 hypothesis-generation 框架而非新神经生物学发现。 |
| 理论严谨 | 7.0 | Supplementary Note 20 给出 scoped framework（Lemma 1/1b/2、Proposition 3–5、条件 C1–C6），明确"exact at the k_n scale and approximate at the k_f scale"、C5 不可在观测对上验证、并给出 Cauchy–Schwarz 最坏偏差；但 A1 排除限制（HK 上 φ=0）恰在脑/扰动语境被自己承认可能失效（`si.txt:267`），把 ω 解释为"functional divergence in excess of baseline"的识别依赖一个未验证假设。 |
| 统计严谨 | 6.5 | 置换、bootstrap、FDR 体系异常详尽且多处主动披露缺陷：anti-enrichment、B=1,000 floor、pseudoreplication、两家族未联合校正、4-donor small-cluster 非校准区间。扣分在有效独立单元（4 donors）与 31,764 pairs / 108 regions 的推断层级错配、catalogue-level depletion 检验的 family 归属不明、以及 Fig 4f 仍保留极端伪重复 P 值。 |
| 证据充分 | 5.5 | 负对照体系完整（pseudo-region 127,756 pseudo-pairs、donor-stratified null、span/size-matched、双 anchor 重算、Thalamic 功效定量）。但核心梯度低端锚点 Bergmann glia 仅 3 个供体、4 个 eligible regions、within-donor 10 pairs；PMI/ambient/doublet 无任何定量 bound；换 data-driven anchor 后超类 elevation 与 astrocyte–Bergmann 梯度双双 collapse；跨队列仅单脑区亚阈值信号。 |
| 表达清晰 | 6.0 | 限定语密集、层次分明，结论降级措辞到位。但 Fig 4 图注与正文 / Note 18 / Note 24 的稳健性披露不对称；"primary signal is depletion"与 Fig 4c "candidate detection"、Note 14 "negative-control framing"三处措辞摇摆；TCGA 的 RIN 控制与脑图谱"no PMI or RIN"并列易被误读为已覆盖脑端。 |
| 影响力与 NC 适配度 | 5.5 | 通用 metric + caution 符合 NC 方法学范围；但对神经科学读者的实际交付是"框架 + 假设清单"，无新脑生物学发现、无独立验证，且 headline 数字（6.10/3.66-fold、neuronal elevation）对 anchor 定义与 4-donor 结构敏感。 |

---

## 总体评价

这是一份在统计自我披露方面明显优于平均水平的投稿：作者主动把脑图谱结论限定为 "housekeeping-dominated class-level differences"，明确拒绝 functional specialization、cell-type identity 与 positive-selection 解读，并对候选目录给出 anti-enrichment、floor、estimator-sensitivity 与 pseudoreplication 的完整负对照框架。也正因如此，问题不在"结论写过头"，而在"证据底座与结论的分辨率不匹配"：31,764 个跨区 pair、606 libraries 全部嵌套在 4 个供体内，梯度低端锚点只有 3–4 个供体，而信号又恰恰由最易受尸后降解与 ambient soup 影响的 k_n 主导。此外，正文对神经元超类 elevation 的 anchor 依赖作了充分披露，却把同类的非神经元梯度 collapse 只留在 Supplementary Note 24，Fig 4 图注对此完全沉默，形成披露不对称。这些问题可通过补做去污染/降解敏感性、供体分层对照与图注—正文一致性修订解决，未达到拒稿程度，但远超 Minor Revision 的修订量。

---

## 主要问题

**未发现 P0 级问题**：材料包内部数字自洽，未把 CKI 结果写成细胞迁移或谱系结论，未把未过 FDR 的候选写成发现，未隐瞒全局家族不可达。以下为 P1 / P2。

### P1-1｜有效独立单元是 4 个供体，与"108 脑区区域梯度"的推断层级不匹配

- **位置与引文**：`si.txt` 5.7（第 304 行）："The brain atlas contains nuclei from **four donors**, and 94.5% of region pairs share at least one donor (median top-donor share within a region: 0.61)… (astrocytes: 11,139 pairs from 261 donor-region blocks; Bergmann glia: **10 pairs**)."`si.txt` 3.12（第 147–148 行）："They come from 597 libraries and **4 donors** (mean pair degree 7.2), so an exact test on 2,161 pairs treats library-level technical replicates as independent and **overstates the evidence**"；"the **donor count is small**"；wild-cluster bootstrap "with only **16 distinct sign patterns** these are small-cluster sensitivity intervals, **not calibrated 95% intervals**." `si.txt` Note 11（第 224 行）："with only **four donors—and Bergmann glia present in three**—the size-only equal-n gradient is not separable from donor composition". `ms.txt:113`：donor cluster bootstrap "four donors resampled with replacement". `si.txt` Note 24（第 283 行）："**Bergmann glia and choroid plexus have only 4 eligible regions (6 pairs) and carry no inferential weight**."
- **问题**：block-shuffle 以 606 个 10x library 为 exchangeability unit（`ms.txt:93`），但 library 嵌套于 4 个供体；`ms.txt:53` 的 31,764 个 same-cell-type cross-region pairs 不是独立观测。作者已用 donor-stratified null（`si.txt:231,305`）、within-donor pairs（`si.txt:232`）、4-donor wild-cluster bootstrap 缓解，并诚实承认 small-cluster，但结论呈现仍以 "108 regions"、"6.10-fold bound / 3.66-fold matched"（`ms.txt:55`、Fig 4b 图注 `ms.txt:191`）为 headline。梯度两端覆盖极端不对称（astrocyte 11,139 within-donor pairs vs Bergmann glia 10 pairs / 3 donors），而 Note 24 明言该端点"carry no inferential weight"。Abstract（`ms.txt:10`）"class-level divergence is housekeeping-dominated and panel-dependent (6.10-fold bound; 3.66-fold matched)" 未标供体数。
- **修法**：在 Abstract、Results 首句与 Fig 4b 图注显著标注 **n = 4 donors**；把脑图谱 headline 明确限定为 exploratory / hypothesis-generating；把 leave-one-donor-out 梯度分布（size-only 控制 `[0.93, 1.76]`、span-matched 全部 >1，`si.txt:224–225`）从 SI 提升进正文，并声明所有 region-level 推断以 donor 为有效独立单元、block-shuffle 的 library 交换性不等价于供体交换性。

### P1-2｜PMI / ambient RNA / doublet 的让步不足以支撑 k_n 主导的脑结论

- **位置与引文**：`ms.txt:74`（Limitations iii）："the brain atlas is post-mortem—quality proxies do not drive the gradient (Results), but **PMI-related RNA-degradation deformation cannot be excluded, nor were ambient RNA or doublets modelled**." `si.txt` Note 11（第 226 行）："The atlas metadata carries **no PMI or RIN**, so technical variation was proxied by mean detected genes, mean total UMI, and mitochondrial fraction per group… mitochondrial fraction explains parts of k_n and k_f (**R² 0.225→0.271 and 0.442→0.504** when added) but not of ω (0.300→0.308)… **PMI-related RNA-degradation deformation cannot be excluded**." Fig 4b 图注（`ms.txt:191`）："the signal is dominated by the **k_n denominator (3.21-fold k_n versus 2.03-fold k_f)**"; `ms.txt:57`："class-mean ω tracks k_n (ρ = −0.73) but not k_f (ρ = 0.09)". 另 `ms.txt:47,106` 与 `si.txt:279–280`（Note 23）的 RIN 控制取自 GDC **TCGA** 样本（3,244 samples），与脑图谱无关。
- **问题**：脑梯度几乎完全由 k_n 携带，而 k_n 正是 snRNA-seq 中最易受核来源 ambient soup（高表达 HK / 核糖体 / 线粒体转录本）、尸后 RNA 降解与 3′ bias 影响的量。作者用三个"每群平均"proxy 加一句 "the shared technical component cancels in the ratio, as designed"（`si.txt:226`）来排除，但该抵消假设要求降解/ambient 对 HK panel 与 per-pair top-200 identity panel 的影响成比例，未做检验；同段又承认线粒体比例确实解释 k_n、k_f 相当一部分方差。4 供体下供体效应与 PMI / 解剖处理时间高度混淆，无法用 donor-stratified null 分离。TCGA 的 RIN 阴性控制（"NN/TT k_n ratio unchanged at RIN ≥ 7"，`ms.txt:47`）在正文紧邻泛癌段落，极易被误读为也覆盖脑图谱；实际上脑图谱"no PMI or RIN"。整篇对这三类混杂只有"cannot be excluded"的定性让步，无任何定量 bound。
- **修法**：补做 snRNA-seq 特异的 ambient / 降解敏感性——用 SoupX / CellBender / DecontX 或内含子比例、soup profile 作 proxy 重算 k_n 与 3.66-fold 梯度；剔除降解敏感 / 高 ambient 贡献基因后重算；在一个带 PMI / RIN 元数据的独立尸后脑队列检验 k_n–PMI/RIN 相关并报告斜率与 CI；明确声明 Note 23 的 RIN 控制仅适用 TCGA；把 "quality proxies do not drive the gradient" 改为"可观测的深度 / UMI / 线粒体 proxy 不能解释梯度，但 PMI / ambient / doublet 未建模且未定量界定"。

### P1-3｜Fig 4 图注与正文 / Note 18 / Note 24 的稳健性披露不一致：anchor-collapse 与 Thalamic 功效未进入图注

- **位置与引文**：正文 `ms.txt:54`："This elevation is **anchor-type dependent**: it is retained in full under the independent Eisenberg–Levanon (2013) list (MGE P ≤ 0.005, IT P = 0.005, Thalamic P = 0.16) but **vanishes under a matched-size data-driven lowest-CV panel (mean ω ≈ 12 observed and null alike, P = 0.95, 0.87, 0.76)**". `si.txt` Note 18（第 253–254 行）："The **thalamic test is the least powered (20 regions, 84 libraries; null SD 4.4 versus 2.3 for MGE)** and its estimate is the most donor-sensitive (leave-one-out medians 25.4–76.4), so its non-rejection is **read as underpowered rather than negative**"；"the superclass elevation is therefore **anchor-panel dependent**". `si.txt` Note 24（第 283 行）："The astrocyte-versus-Bergmann gradient keeps its direction under EL (2.82-fold versus the 3.66-fold matched control under HRT) and **collapses under DEF-CV (0.86-fold)**"；DEF-CV 下超类 "P = 0.72–0.92"。对照 **Fig 4 图注**（`ms.txt:191`）：(e) 只列 "P = 0.001 … P = 0.014; thalamic excitatory neurons P = 0.163"，(f) 只列 "neuronal medians 59.2–64.2 versus … 24.5"，(b) 只说 "6.10-fold raw gradient is an uncorrected upper bound … 3.66-fold observed … dominated by the k_n denominator"——**三处均未提 anchor 依赖、Thalamic underpowered、或梯度在 data-driven panel 下 collapse**。且 Fig 4f 图注给 "P < 10⁻³⁰⁰"，而 `si.txt:255` 给 "P ≈ 10⁻⁶⁰² (normal approximation)"，两处极端伪重复 P 值不一致（图注已标 "pseudoreplicated at the pair level"，但数值仍不可解释）。
- **问题**：只阅读 Fig 4 及图注的神经科学读者会得到"神经元超类区域分歧稳健高于非神经元、class 梯度 3.66-fold 可靠"的印象，而不知道换一个 data-driven HK anchor 后，超类 elevation 与 astrocyte–Bergmann 梯度**双双消失**。正文只对"brain superclass elevation"披露 anchor 依赖（Limitations ii, `ms.txt:74` 亦仅点名 superclass elevation），对非神经元梯度的同类 collapse 未同等披露；Note 24 的结论句又把它概括为 "the data-driven lowest-CV panel removes the **brain superclass elevation**"，淡化了同段 (4) 的 0.86-fold collapse，属 SI 内部措辞偏乐观。Fig 4 标题含 "region-association inference"，与 "no candidate survives FDR" / "underpowered" 之间亦有张力。
- **修法**：Fig 4b / 4e / 4f 图注补入 anchor-panel dependence（HRT / EL 保留、DEF-CV collapse 的具体 P 与 0.86-fold）与 Thalamic "underpowered rather than negative" 限定；正文 Results 对 class-level gradient 同等披露 Note 24 (4) 结果；统一 Note 24 结论句措辞；删除或统一 Fig 4f 的极端伪重复 P 值，仅保留"descriptive, pseudoreplicated, 不作推断"表述。

### P2-1｜"发育起源异质性"与"迁移"的机制引用残留，缺少排除性声明

- **位置与引文**：`ms.txt:60`："Low ω across two regions indicates similarity beyond baseline expectation, with several non-exclusive mechanisms **20–24**." 其中 ref 23 为 "Oligodendrocyte precursors **migrate** along vasculature in the developing nervous system"（`ms.txt:144`）、ref 24 为 "… termination of oligodendrocyte precursor cell perivascular **migration** during development"（`ms.txt:145`）、ref 22 为 "Microglia **colonize** the developing brain by clonal expansion"（`ms.txt:143`）。结论层面已正确降级：`ms.txt:62` "mature-oligodendrocyte candidates (10) show a thalamo-temporal orientation crossing the **dorsoventral origin boundary** 25—**a post-hoc, illustrative pattern only** (the axis was defined after inspecting the candidates and carries no valid post-selection P value)"；`ms.txt:71` "matches **forebrain development** 25 only at axis level (post-hoc, illustrative)… Several signals match prior reports—**literature anchoring, not independent validation**." `si.txt:236`（Note 14）亦说明该轴的超几何 P "assume independence"因候选共享端点而不成立。
- **问题**：**结论层面没有把 CKI 结果写成迁移**，这一点是合格的；但把成年脑跨区 housekeeping-anchored 低 ω（且是 anti-enriched、无 per-pair FDR 支持、仅 3/39 在 global-k_n 下存活的假设清单）与发育期 OPC 迁移 / 小胶质克隆定植文献并列为"possible mechanisms"，容易被误读为 CKI 为细胞迁移或谱系散布提供证据。全文没有一句显式排除性声明。
- **修法**：在 Results 候选段与 Limitations 明确写出"本方法不推断细胞迁移、克隆散布或谱系关系；跨区低 ω 仅反映 HK 锚定的基线相似性"；机制引用限于 developmental-origin / regional-heterogeneity 文献，或删除 refs 22–24 的 migration / colonization 引用。

### P2-2｜39 Strong 候选目录在"检测"与"负对照"之间摇摆；全局家族边界未完全说清

- **位置与引文**：`ms.txt:61`："The **primary signal is depletion**… the expected Strong-candidate count is **148.3**, so the **39 observed lie 3.8-fold below expectation** (one-sided P(null ≤ 39) ≤ 1.0 × 10⁻³, **the floor resolvable at B = 1,000** …)—a catalogue-level depletion signal, **not per-entry discovery (no candidate survives global FDR correction, minimum q = 0.520**; the microglial concentration, 16 of 39, is itself **0.31-fold below expectation, P = 0.990**)". Fig 4c 图注（`ms.txt:191`）标题为 "Region-associated **candidate detection**"，同段又写 "the catalogue is a **hypothesis list, not a discovery set**"；`si.txt:238`（Note 14）称 "an explicit **negative-control framing** rather than a detection claim". `ms.txt:74`（Limitations v）："the class-level upper-tail tests and the pair-level lower-tail screen were pre-specified as **two independent families and are reported without joint cross-family correction**"; `si.txt:236`："the tier variable … and the per-pair permutation P-values are **both monotone functions of the same observed and null ω values**, so the tier-graded raw-P enrichment is **partly guaranteed by construction**; the set-level statistics below quantify the pattern rather than provide independent evidence".
- **问题**：anti-enrichment 与 floor 说明**本身是到位且值得肯定的**（39 vs 148.3、0.31-fold / P=0.990、min q=0.520、B≈6×10⁵ permutations 或 ~635 floor P-values 才可达 q<0.05、`ms.txt:112`）。但 "primary signal is depletion … P ≤ 1.0 × 10⁻³" 把一个 rule-matched 的目录级阴性观察提升为带 P 值的"主信号"，与 Fig 4c "candidate detection"、Note 14 "negative-control framing" 三处措辞不统一；且该 depletion 检验与 class-level family、Note 14 的多个 post-hoc set-level 检验（hypergeometric P = 9.6 × 10⁻³¹、Cochran–Armitage z = 61.0、thalamo-temporal axis P = 0.005 / 2.1 × 10⁻⁵ / 1.3 × 10⁻⁵）并存，其 family 归属、是否预注册、是否校正未明确。
- **修法**：统一为"catalogue-level negative-control observation"，避免 "primary signal / detection" 措辞；明确该检验的 family 归属与是否预注册；对 Note 14 全部 set-level P 值统一标注 post-hoc、描述性、因与 tier 同源而不构成独立证据（`si.txt:236` 已有此意，应在正文体现）。

### P2-3｜脑图谱与 SEA-AD 跨队列可比性声明不足

- **位置与引文**：`si.txt:258`（Note 19）：SEA-AD 为 "CELLxGENE collection 1ca90a2d; **middle temporal gyrus**; microglia-PVM and astrocyte slices"、"**donor-level design**"、"ADNC 'High' (**42 donors**) versus 'Not AD'/'Reference'"、"pre-registered gene sets … merged into the reduced panel"（与 Siletti 的 per-pair top-200 混合 scheme 不同）；结果 "P = 0.0145 / 0.041 … Benjamini–Hochberg across the 10 tests left nothing significant (**minimum q = 0.145**), so the anchor provides **directional, sub-threshold evidence … not detection**". `si.txt:259`：剂量–反应 "**absent for the pre-registered biology**",名义趋势只出现在 off-target 集合。`ms.txt:71`："Several signals match prior reports—**literature anchoring, not independent validation**"; `ms.txt:73` 有通用规则 "comparisons within the same dataset and scheme only … absolute ω does not transfer".
- **问题**：降级本身到位且诚实（甚至报告了 off-target 名义显著趋势），但 Siletti（108 区、4 donors、non-neuronal、per-pair top-200）与 SEA-AD（单脑区、87 donors、疾病分组、预注册基因集、donor-level pseudobulk）在队列、供体、脑区、测序处理与 k_f 定义上均不同，全文未点名声明"两者绝对 ω 不可直接比较，SEA-AD 亚阈值结果不构成对脑图谱结论的独立验证"，仅有一条泛化规则。
- **修法**：在 Discussion 明确 SEA-AD 仅作 directional anchor、绝对 ω 不跨队列比较、其亚阈值 / 无剂量–反应结果不构成验证；避免任何"跨队列复现"暗示。

### P2-4（次要）｜神经元超类只取 3 个、选择标准不透明；复现指南存在替代 Strong 规则

- **位置与引文**：`si.txt:251`（Note 18）："we analysed **three well-sampled neuronal superclasses** … (MGE interneurons, 222,434 nuclei; thalamic excitatory neurons, 85,546; upper-layer intratelencephalic neurons, 455,006) … regions retained at ≥ 50 nuclei of the superclass"; `ms.txt:54` 与 Fig 4f 图注据此得出 "the non-neuronal screen **understates atlas-wide divergence**"（`ms.txt:191`）。`guide.txt:168`："notebooks/07d_brain_siletti_v4.py … applies a related strong-screen variant (residual < 0.3, omega < 15, and **region-pair mean omega > 20**); the **reported Strong tier follows 08d**（`lowest ω in pair`）".
- **问题**：Siletti `supercluster_term` 的神经元超类远多于 3 个，"well-sampled" 的入选阈值与排除清单未列，由 3 个（可能非随机）超类外推 "atlas-wide" 存在选择性报告风险；此外复现指南披露了与权威 08d 规则不同的 07d Strong 定义，39 Strong 目录的复现依赖脚本选择，虽已声明但两条规则不等价。
- **修法**：列出全部候选超类及各自 region / library 覆盖与排除理由，或把结论限定为 "the three analysed superclasses"；在 guide 与 Methods 明确废弃 07d 的 Strong 定义或给出两规则下目录差异。

---

## 优点

1. **结论层级降级到位且一致**：标题即 "Housekeeping-dominated **class-level** divergence across brain regions"（`ms.txt:52`），正文 `ms.txt:59` "it is k_n-dominated and **does not establish functional specialization**"，Limitations (`ms.txt:74`) "CKI detects state changes within a given cell type, **not cell-type identity**"，Discussion `ms.txt:67` "never as evidence of positive selection"，`ms.txt:73` "absolute ω does not transfer"。未把 ω 写成区域特化、细胞迁移或谱系结论，符合脑图谱数据的分辨率。
2. **统计诚实度罕见地高**：主动报告 anti-enrichment（39 vs 148.3、3.8-fold below；microglial 0.31-fold below, P = 0.990；`ms.txt:61`）、全局 FDR 不可达且明说原因是置换分辨率而非"无候选"（min q = 0.520；需 B ≈ 6 × 10⁵ 或 ~635 个 floor P；`ms.txt:112`、`si.txt:238`）、Fig 4f 图注自标 "pseudoreplicated at the pair level"、tier 与 per-pair P 同源 "partly guaranteed by construction"（`si.txt:236`）、两家族未联合校正（`ms.txt:74`）、4-donor wild-cluster 只有 16 种符号组合 "not calibrated 95% intervals"（`si.txt:148`）。
3. **负对照与稳健性体系完整**：pseudo-region 阴性对照 127,756 pseudo-pairs（`si.txt:228–230`）、donor-stratified null 及其解析 floor（`si.txt:231`）、span-/size-matched 双重控制与 donor bootstrap（`si.txt:225`）、固定面板 / leave-pair-out ablation（`si.txt:313`）、双 anchor 定义重算（Note 24）、library-aware null 给出 5.5% / 4.8% 严格匹配块（`si.txt:150`）。
4. **Thalamic 功效处理专业**：`si.txt:253–254` 定量说明 "20 regions, 84 libraries; null SD 4.4 versus 2.3 for MGE"、leave-one-out medians 25.4–76.4，并用 size-matched 重采样给出 "MGE-strength 40/40 检出、IT-strength 仅 18/40 (45%)"，明确把 P = 0.163 读作 "underpowered rather than negative"，而非阴性结论或显著性失败——这是神经科学审稿人最希望看到的功效表述。

---

## 给编辑的备注

**脑图谱部分是否可送外审：可以送，但必须补配特定专长。** 当前建议审稿人名单（`cl.txt:5`：Theis、Welch、Linnarsson、Ståhl、Schäffer、Zemin Zhang）覆盖单细胞方法学与计算生物学，但**缺少专攻人脑 post-mortem snRNA-seq 技术混杂（PMI / RNA 降解 / ambient soup / doublet）与尸后供体队列设计的审稿人**。建议至少增补 1 位该方向外审，专门裁定 P1-1 与 P1-2；并请编辑按常规核对建议名单中与原图谱数据的关联，确保独立性。统计方法学可由现有名单覆盖，无需额外增加。

**是否需要补实验 / 补对照：不需要新增湿实验**（本研究为公开图谱的计算复用），但以下重算与对照为 Major Revision 的必要条件：

1. snRNA-seq 特异的 ambient / 降解敏感性分析（SoupX / CellBender / DecontX 或内含子比例、soup profile 作 proxy），重算 k_n 与 3.66-fold 梯度；剔除降解敏感 / 高 ambient 贡献基因后复算；
2. 在带 PMI / RIN 元数据的独立尸后脑队列检验 k_n–PMI/RIN 关系并给出斜率与 CI；明确 Note 23 的 RIN 控制仅适用 TCGA、不外推到脑图谱；
3. 全 donor 分层的梯度与超类 elevation（leave-one-donor-out、per-donor 曲线）进入正文，Abstract 与 Fig 4b 图注标注 n = 4 donors，并把结论限定为 exploratory；
4. 正文 / Fig 4 图注同等披露 Note 24 的 DEF-CV 结果（超类 P = 0.72–0.92、astrocyte–Bergmann 梯度 0.86-fold）与 Note 18 的 Thalamic "underpowered rather than negative"，统一 SI 与图注的伪重复 P 值；
5. 列出全部神经元超类的 region / library 覆盖与 3 个入选标准，或把 "atlas-wide" 结论限定为已分析的 3 个超类；
6. 加入"CKI 不推断细胞迁移 / 克隆散布 / 谱系关系"的排除性声明，并修订 refs 20–24 的机制引用；统一 39 Strong 目录在 "detection / depletion / negative-control" 三处的措辞与该检验的 family 归属。

若上述 1–4 无法完成，建议把脑图谱部分整体降格为 "illustrative application / hypothesis-generation"，删除 6.10-fold / 3.66-fold 作为 headline 量化结论，仅保留 class-level 排序与候选清单的描述性呈现。

---

*审阅人：R5（脑图谱 / 神经科学 / 单细胞脑组织）｜本轮为独立盲审，未参考任何既往审稿意见。*
