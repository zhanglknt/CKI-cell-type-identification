# 单细胞生物学审稿报告 — CKI v12

## 评分: 5.5/10

本稿件提出CKI（Cell-state Kinetic Index），借鉴Ka/Ks比值的思想，将转录组差异分解为中性偏移率（k_n，来自管家基因）和功能转化率（k_f，来自身份基因），以ω = k_f/k_n量化选择性转录组重塑。概念框架有启发性，脑区分析的开发生物学验证具有一定深度。但在数据集代表性、跨物种验证缺失、癌症分析混杂因素控制、多重假设检验校正等方面存在需重大修改的问题，且投稿信与正文之间存在关键性不一致。

---

## 1. Critical Issues（阻断发表的问题）

### 1.1 投稿信声称的"跨物种一致性验证"在正文中完全缺失

投稿信（cover letter）第35行明确声称：

> "cross-species consistency—mouse orthologs show strong correlation with human CKI ω, confirming evolutionary conservation"

然而通读全文，**正文中不存在任何形式的人鼠ω相关性分析**。Figure 3A图例（第227行）仅描述"ω distribution comparison between mouse (n = 15 shared cell types) and human (n = 2000 pairs)"，即分布对比，并非相关性分析。正文未报告任何人鼠ω的Spearman/Pearson相关系数、散点图或进化保守性统计检验。

人鼠中位ω差异巨大（小鼠3.63 vs. 人类13.68，相差约3.8倍），作者将其归因于"更大的细胞类型数量和供体异质性"（第103行），但这是事后解释，缺乏正式的统计验证。

**这是阻断性问题**：投稿信向编辑做出了正文无法支撑的核心声明。要么补充正式的跨物种一致性分析（对共享细胞类型的ω进行相关性检验），要么修改投稿信删除该声明。

### 1.2 TCGA数据归一化方法在正文与补充材料间存在矛盾

正文Methods（第53行）明确记载：

> "TPM values, log2(x+1) transformed."

补充材料Supplementary Note 1.6和Note 4.3则记载：

> "Normalization: FPKM values from GDC, followed by log2(x+1) transformation."

TPM与FPKM是本质上不同的归一化方法：TPM对测序深度做了跨样本归一化（长度归一化后再按总 reads 缩放），而FPKM仅按长度和测序深度归一化但不保证跨样本可比性。CKI的softmax归一化虽然在一定程度上缓解了绝对尺度差异，但两种方法对低表达基因的灵敏度和噪声谱完全不同，直接影响JS散度计算。

此外，正文与补充材料的TCGA样本数也不一致：
- 正文：LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109 = 3,596
- 补充材料：LUAD 515+59, LUSC 501+51, LIHC 371+50, KIRC 533+72, BRCA 1093+113 = 3,358

**必须统一数据来源和归一化方法描述，并确保可复现性。**

### 1.3 归一化策略在正文内部自相矛盾

Methods（第41行）：

> "norm is sum-normalization for non-negative single-cell data (softmax only for TCGA bulk RNA-seq)"

Results（第83行）：

> "We restrict the pseudobulk vectors to housekeeping (HK) gene indices and apply softmax normalization"

补充材料Supplementary Note 1.2和1.3则全部使用softmax。

正文Methods说单细胞数据用sum-normalization、TCGA才用softmax，但Results描述和补充材料却对单细胞数据也用softmax。sum-normalization和softmax对概率向量的构造方式不同（前者直接除以总和，后者通过指数变换），会影响JS散度的数值。**必须明确实际使用的归一化方法并统一描述。**

---

## 2. Major Issues（需要重大修改）

### 2.1 数据集选择的代表性和局限性

**Tabula Muris**：仅使用FACS SmartSeq2数据（15,057 cells），未使用droplet-based数据。SmartSeq2具有更高的基因检测灵敏度但通量低，且FACS分选本身可能引入选择偏差。原版Tabula Muris同时包含FACS和droplet两种协议，仅使用前者可能影响小鼠校准的普适性。建议补充droplet数据的验证，或至少讨论这一选择的局限性。

**Tabula Sapiens**：仅覆盖6个器官（liver, kidney, heart, bone marrow, spleen, lung），而完整Tabula Sapiens包含更多器官。6个器官的覆盖对于"human atlas"的定位偏窄，尤其缺少脑、皮肤、肠道等重要器官。跨器官细胞类型保守性分析（59对）的统计功效因此受限。

**TCGA**：5种癌症类型对于"pan-cancer"声明偏少，且均为常见实体瘤，缺少血液肿瘤、黑色素瘤等。更关键的是，所有TCGA分析均基于bulk RNA-seq，与CKI的设计初衷（单细胞水平的pseudobulk）存在本质脱节。

**Siletti脑图谱**：仅分析非神经元细胞（888,263 nuclei），排除了神经元（脑中数量最多的细胞类型）。虽然作者可能有意聚焦胶质细胞，但这一选择限制了方法的展示范围，尤其考虑到神经元具有最丰富的区域异质性。

### 2.2 细胞类型跨数据集映射缺乏透明度

正文提到Tabula Sapiens有"99 cell-type entries"，但未详细说明这些细胞类型如何跨器官对应。跨器官分析识别了"59 same-cell-type cross-organ comparisons"（第121行），但映射规则（基于注释文本匹配？基于标记基因？基于层次分类？）未说明。

Figure 3A图例提到"15 shared cell types"用于人鼠分布对比，但未说明人鼠细胞类型如何映射——是手动匹配注释名称？还是基于正交基因？

对于脑图谱，10个非神经元大类基于Siletti原始注释的supercluster_term，这一选择合理。

### 2.3 伪bulk方法对稀疏性和dropout的鲁棒性未充分验证

CKI的pseudobulk取log1p归一化后的均值。虽然pseudobulk聚合可以在一定程度上缓解dropout，但：

1. **SmartSeq2 vs. droplet数据的差异**：小鼠校准用SmartSeq2（dropout低），人类验证用Tabula Sapiens（dropout较高）。两种协议的pseudobulk质量不同，可能系统性影响k_n和k_f的估计。未检验CKI在纯droplet数据（如10X-only数据集）上的表现。

2. **最低细胞数阈值**：要求≥10 cells/group对SmartSeq2数据合理，但对dropout严重的droplet数据可能不足。脑图谱分析要求≥20 nuclei/(region, cell_type)和≥50 nuclei/region，标准更高，但这两种阈值的选择缺乏灵敏度分析。

3. **pseudobulk的信息损失**：作者承认pseudobulk"discards within-population heterogeneity"（第193行），但未正式量化。对于肿瘤内异质性这一癌症生物学的核心问题，pseudobulk可能严重低估真实异质性。

4. **k_f使用per-pair DE基因的可比性**：Tabula Sapiens的hybrid方案中，k_f使用每对细胞类型特异的top-200 DE基因。不同细胞类型对的ω值因此基于完全不同的基因集计算，使得跨对的ω比较缺乏严格的可比性。虽然JS散度本身是归一化的，但不同基因集的信息含量和方差结构不同。

### 2.4 跨物种验证缺失（详见Critical Issue 1.1）

除了投稿信与正文不一致外，即使补充了跨物种分析，还需注意：

- 人鼠ω量级差异约3.8倍，直接比较绝对值意义有限。
- 应使用共享细胞类型的rank-based比较（如Spearman相关），而非绝对值比较。
- HRT Atlas的1,130个人鼠共享HK基因用于k_n，但k_f使用的身份基因在人鼠间可能不同（不同的top-200 DE基因），使得ω的跨物种比较在数学上不对等。

### 2.5 癌症分析的临床意义和混杂因素控制不足

**肿瘤纯度问题**：正文承认"bulk profiles aggregate signals from multiple cell types, tumor purity variations, and stromal infiltration"（第193行），但未进行任何纯度校正。具体缺失：
- 未使用ESTIMATE、CIBERSORT等工具评估肿瘤纯度
- 未将纯度作为协变量纳入分析
- NN/TT > 1的"转录趋同"可能完全由肿瘤微环境（TME）趋同驱动（不同肿瘤类型的间质活化、免疫浸润模式趋同），而非恶性细胞本身的趋同
- 作者在Discussion中承认了这一点（第189行），但正文Results的表述仍然倾向于"common vulnerabilities"的解读

**TCGA ω量级异常**：PAM50分析的ω值（如Luminal A: 344.5 ± 323.4）远高于单细胞数据的中位ω（13.68）。如此大的差异表明CKI在bulk数据上的行为可能与单细胞数据截然不同，直接将两者的生物学解读平行类推是不恰当的。softmax归一化对bulk和单细胞数据的不同行为需要专门讨论。

**多重检验未校正**：PAM50（5组）、Edmondson grade（4组）、LUAD突变（3组）三组分析在同一数据集上进行，正文承认"we note the number of tests performed and interpret significant results with appropriate caution"（第75行），但仅停留在口头提醒，未进行任何定量校正。

**配对样本统计功效不足**：paired tumor-normal比较仅n=2-5 per cancer type（第115行），作者承认"limits statistical power"，但仍在正文中报告了这些结果，可能误导读者。

### 2.6 脑区迁移候选基因的生物学可信度评估

**优势**：
- 30个Strong候选信号的post-hoc文献验证详尽，引用了Foerster et al. (2024)的背腹侧少突胶质细胞起源、Shemer & Jung (2024)的小胶质细胞定植路线等高质量文献。
- OPCs作为阴性对照的逻辑合理：OPCs是成体CNS中最活跃的迁移细胞，0个Strong信号支持模型不是简单检测迁移能力。

**问题**：
1. **Post-hoc解释的确认偏差风险**：作者坦承"our initial analytical framework was designed to detect migration signatures; the developmental origin interpretation emerged from post-hoc cross-validation against the literature"（第157行）。这种先看到信号再找生物学解释的做法存在确认偏差。更严谨的做法是预先注册预测（如基于发育生物学文献列出预期的发育边界区域），然后检验CKI是否检测到这些区域。

2. **乘法残差模型的阈值缺乏正式零分布**：Strong/Moderate/Weak的阈值（0.3/0.5/0.75）基于观测数据的百分位数（第63行），而非正式的零分布。虽然作者提到置换检验的阈值"qualitatively consistent but not identical"（第63行），但补充材料中未见详细的置换检验结果。

3. **部分生物学解释过于推测性**：
   - "we propose that IC represents a contact zone where forebrain-derived and hindbrain-derived microglial colonization waves meet"（第169行）——这一假说缺乏直接证据，仅基于CKI信号推断。
   - 纤维母细胞的"A40 vs. SN"信号归因于"shared meningeal origin"（第177行），但A40（前额叶皮层）和SN（黑质）在血管分支上相距甚远，"shared meningeal origin"的解释需要更强的解剖学证据。

4. **Bergmann glia仅7965个nuclei**：在888,263个非神经元核中，Bergmann glia仅占0.9%，且仅覆盖7个区域（21对比较）。如此小的样本量使得其"最低ω"的排名不太可靠。

### 2.7 HK基因中性假设的根本性问题

CKI的核心假设是HK基因提供"中性基线"。作者多处承认这一假设的局限性（第83行、第185行、第193行），但存在以下未解决的问题：

1. **癌症中的HK基因违反稳态假设**：作者明确提到"Warburg effect upregulation of glycolytic HK genes such as GAPDH"（第193行）。GAPDH是经典HK基因，但在肿瘤中表达大幅变化。如果k_n本身被肿瘤代谢重编程扰动，则ω = k_f/k_n的分子和分母都被扰动，比值的意义不明确。**应在TCGA分析中专门检验HK基因在肿瘤vs.正常间的表达变化幅度。**

2. **HK基因的低方差可能反映稳定化选择而非中性**：作者在Discussion中承认"their low variance could reflect strong functional constraint rather than true neutrality"（第193行）。这是对CKI概念框架的根本挑战：如果HK基因受稳定化选择约束（表达水平有功能意义），则k_n测量的不是"中性漂移"而是"受约束的变异"，与Ka/Ks中 synonymous sites 的机制类比不成立。

3. **灵敏度分析不够**：HK基因集大小（250-1000基因）的灵敏度分析显示CV < 13%，但这只检验了基因数量的稳定性，未检验基因组成的稳定性。使用完全不同的HK定义（如RNL10、EPCAM等不同策略选择的HK集）是否给出一致的ω排名？

### 2.8 多重假设检验全面缺失

- 4,851对Tabula Sapiens细胞类型比较：无FDR校正
- 31,764对脑区比较：无FDR校正
- 30个Strong候选信号从31,764次比较中选出：在5% FDR下，预期约1,588个假阳性。即使残差<0.3的阈值很严格，也需要正式的置换检验来评估假阳性率
- TCGA三种临床分层分析：无FDR校正

作者在Statistical reporting中承认"all reported P-values are raw, uncorrected values"（第45、75行），但对于声明"30 Strong candidate signals"的发现，仅靠原始P值远远不够。

---

## 3. Minor Issues（建议修改）

### 3.1 k_f基因选择策略在正文中描述不一致

- Methods（第41行）："the top-200 most differentially expressed genes per cell-type pair (Seurat v3 flavor) excluding HK genes"
- Results（第85行）："identity genes are the top-2,000 highly variable genes (HVGs; Seurat v3 flavor)"
- 补充材料Note 2 Algorithm 2：Tabula Sapiens用pairwise top-200 by |Δexpression|，Tabula Muris用global top-2,000 HVG

三种描述指向不同的基因选择策略。虽然补充材料澄清了Tabula Muris（global 2,000 HVG）与Tabula Sapiens（pairwise 200 DE）的区别，但正文应明确区分两种方案及其适用场景。

### 3.2 Bootstrap迭代次数不一致

- 正文（第45行）："B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration"（重复表述）
- 补充材料Note 3.2："B=1,000 for all primary results (B=500 used for the Phase 3.2 parameter sweep)"

应统一B值并明确哪种分析用了哪个B值。

### 3.3 Table 1和Table 2在正文中被引用但未呈现

- Table 1（AUC比较，第107行）和Table 2（跨器官保守性数据，第127行）在正文中被引用，但正文中未包含表格内容。应确保这些表格在最终版本中呈现。

### 3.4 ω分布的右偏和极端值处理

正文报告ω中位数13.68 vs. 均值14.12（第87行），但PAM50分析中Luminal A的ω高达344.5 ± 323.4（标准差与均值相当），表明极端异常值严重影响均值。建议：
- 所有ω相关的组间比较使用中位数/IQR而非均值±SD
- 对ω进行log变换后再做参数检验，或坚持使用非参数检验（已在部分分析中做到）

### 3.5 "same-organ > different-organ"反转的解释可能不完整

作者将CKI是唯一"same-organ > different-organ"的指标归因于"sensitivity to functional specialization within shared microenvironments"（第107行）。但另一种解释是：per-pair DE基因选择策略在同器官细胞类型对中可能选择到更特异的基因（因为同器官细胞类型的表达谱更接近，top-200 DE基因的信号噪声比更高），从而人为放大了同器官的k_f。这一替代解释需要通过使用固定基因集（而非per-pair DE）的灵敏度分析来排除。

### 3.6 脑图谱中神经元细胞的排除缺少理由说明

Siletti数据集包含大量神经元，但本研究仅分析非神经元细胞。排除神经元的原因（计算限制？生物学聚焦？神经元区域注释的复杂性？）未说明。建议在Methods中补充理由。

### 3.7 补充材料中ω上限设为1,000

补充材料Note 1.1提到"omega is capped at 1,000"。这一截断可能严重影响TCGA分析（PAM50均值达344.5，部分样本可能超过1,000）。应报告有多少比例的ω值被截断，并评估截断对结论的影响。

### 3.8 图注中的模拟数据说明

Figure 1C-D图注明确说明"Bootstrap ω values were simulated from a Gamma distribution"和"k_n and k_f were simulated from Gamma distributions"。这些是概念示意图，使用了模拟数据。应在图注中更突出地标注"illustrative simulation"以避免误解。

### 3.9 引用格式和文献编号

- 正文引用[4]同时用于HRT Atlas和另一处语境，需检查引用编号一致性
- 参考文献列表中[38,39]在正文第29行引用但参考文献列表中编号38对应Kimura (1983)，39对应Yang & Nielsen (2000)，与正文中"synonymous sites as an internal baseline [38,39]"的语境匹配。但第185行引用[38,40]时，40不在参考文献列表中（列表止于39）。需检查。

---

## 4. 数据与生物学亮点

### 4.1 概念框架具有启发性
Ka/Ks类比的转录组学推广是一个有创意的概念。虽然作者诚实地承认了CKI与Ka/Ks的本质区别（第185行："CKI lacks an analogous cancellation mechanism"），但分解为neutral/functional两个组分的思路本身有价值。

### 4.2 脑区分析的发育生物学验证深度
30个Strong候选信号的系统文献交叉验证是本文最扎实的部分。特别是：
- 少突胶质细胞的10个Strong信号全部落在皮层/丘脑边界，与Foerster et al. (2024)的背腹侧起源实验数据高度一致
- 小胶质细胞的10个Strong信号沿前脑-中脑界面分布，与Shemer & Jung (2024)综述的嘴-尾定植梯度吻合
- 这种"计算发现→文献验证→机制归类"的分析路径展示了CKI在发育生物学中的潜在应用价值

### 4.3 OPCs阴性对照的设计逻辑
将成体CNS中最活跃迁移的OPCs作为阴性对照，验证模型不是简单检测迁移能力，这一设计思路巧妙。OPCs的0个Strong信号与少突胶质细胞的10个信号形成鲜明对比，支持"CKI检测的是发育起源签名而非活跃迁移"的结论。

### 4.4 跨器官细胞类型约束谱系的初步发现
B细胞/中性粒细胞（循环细胞）高度保守、内皮细胞高度可塑的排名与经典细胞生物学预期一致。虽然样本量小，但作为hypothesis-generating结果有价值。

### 4.5 诚实的局限性讨论
作者在Discussion中坦率讨论了多个局限性：pseudobulk信息损失、HK基因中性假设、TCGA bulk混杂、缺乏正式理论模型等。这种学术诚实值得肯定。

### 4.6 参数灵敏度分析
HK基因集大小（250-1000）和HVG数量（1000-4000）的灵敏度分析提供了方法鲁棒性的初步证据，虽然覆盖面还不够全面。

---

## 5. 总体建议

### 5.1 必须解决的问题（修订后可重新评审）

1. **投稿信与正文一致性**：投稿信声称的"cross-species consistency"必须在正文中补充对应的分析，或从投稿信中删除。这是诚信问题。

2. **数据一致性**：统一TCGA归一化方法（TPM vs. FPKM）和样本数的描述；统一归一化策略（sum-norm vs. softmax）的描述。

3. **多重检验校正**：至少对脑区31,764次比较和TCGA临床分层分析进行BH-FDR校正，或提供基于置换检验的FDR估计。

4. **TCGA肿瘤纯度控制**：使用ESTIMATE或类似工具评估肿瘤纯度，并将纯度作为协变量纳入NN/TT比较。如不能完成，应大幅弱化"common vulnerabilities"的结论表述。

### 5.2 建议改进的问题

1. **补充droplet-based数据验证**：在至少一个10X droplet数据集上验证CKI的鲁棒性。
2. **预先注册脑区分析预测**：基于发育生物学文献预先列出预期的发育边界区域，然后检验CKI是否检测到这些区域，以减少确认偏差。
3. **正式量化pseudobulk信息损失**：通过模拟（已知细胞亚群结构的合成数据）评估pseudobulk对异质性的低估程度。
4. **跨物种一致性分析**：如果要在投稿信中保留cross-species声明，应对15个共享细胞类型的ω进行rank-based相关性分析。
5. **补充神经元分析或说明排除理由**：Siletti数据集的神经元区域异质性是脑单细胞图谱的核心发现之一，排除神经元需要充分理由。

### 5.3 概念层面的建议

1. **弱化Ka/Ks类比的强度**：虽然作者已在Discussion中做了免责声明，但标题"Cell-state Kinetic Index"和术语"k_n/k_f/ω"仍然暗示了与分子进化速率的类比。建议在Abstract和Introduction中更早、更明确地声明这是"heuristic metaphor"而非正式的进化模型。

2. **重新定位CKI的角色**：CKI的AUC（0.716）低于cosine distance（0.887），作为分类器不具优势。作者正当地将其定位为"perturbation index, not a classifier"。但即使作为扰动指数，也需要与已有方法（如transcriptional drift [37]、scVI latent distance等）进行定量比较，以证明其独特价值。目前的"负相关"证据虽然有趣，但负相关本身不等于"更有信息量"——可能只是测量了不同的（但未必更有用的）维度。

3. **ω的绝对值意义需澄清**：不同数据集的ω量级差异巨大（小鼠3.63、人类13.68、TCGA数百），且k_f使用不同基因集（global 2000 HVG vs. pairwise 200 DE），使得ω的绝对值在跨数据集比较中意义不明。建议明确ω仅适用于同一分析框架内的相对比较。

### 5.4 最终判断

本稿件的概念框架有创新性，脑区发育生物学分析是亮点，但存在投稿信与正文不一致（Critical）、数据描述矛盾（Critical）、跨物种验证缺失（Critical）、多重检验全面缺失（Major）、肿瘤纯度未控制（Major）等问题。建议作者进行Major Revision，重点解决三个Critical Issues后重新提交评审。
