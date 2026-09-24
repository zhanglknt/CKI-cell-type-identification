# CKI v51r2 专家团审稿汇总（Nature Communications 标准）

日期：2026-09-24 ｜ 稿本：v51r2（MAIN 4,964 词，221/221 构建断言、XV8 54/54、三 verify 0-fail）
模式：6 位并行角色化审稿人，各自独立读 MS 全文 + 抽查 SI/复现指南；R1↔R3 就 TCGA 调整模型问题做过一次交叉核实。

---

## 一、评分总表

| 审稿人 | 领域 | soundness | novelty | significance | presentation | overall | 推荐 |
|---|---|---|---|---|---|---|---|
| R1 | 统计方法学 | 7 | 6 | 6 | 8 | **6.5** | minor（偏 major） |
| R2 | 单细胞计算 | — | — | — | — | **5.0** | major |
| R3 | 肿瘤基因组学 | 6 | 6 | 6 | 7 | **5.8** | major |
| R4 | 脑图谱 | — | — | — | — | **6.0** | major |
| R5 | 编辑写作 | — | — | — | — | **7.0** | minor |
| R6 | 可复现性 | 8 | 7 | 6 | 7 | **6.5** | minor |
| **均分** | | | | | | **6.13** | 3 minor / 3 major |

NC 分档：>8 优秀、6–8 小修、4–6 大修、<4 拒稿。整体落在"小修偏大修"区间。

---

## 二、Major issues 归并（按主题，标注提出人）

### A. 头条数字的不确定度被低估（R1，部分 R3 联署）——文字+重采样可修
- **A1** 校准常数 7.70 的 95% CI [7.37, 8.02] 伪重复：300 个 split-half 值嵌套于仅 6 个 FACS 群体，有效 n≈6。作者自己的 5.7/5.14 已用正确的两阶段重采样，headline 常数却没用——自相矛盾。【修：以 6 群体均值为单位或两阶段 bootstrap 重报】
- **A2** 摘要 1.74 [1.64, 1.84] 梯度区间仅含 20 次细胞重采样噪声，未传播 4 个 donor 的变异；span-matched [3.40, 4.95] 同理（对间不独立）。【修：donor-level cluster bootstrap；若 donor 数不足则降级为点估计+定性陈述，摘要删伪精确 CI】
- **A3** Tabula Sapiens 4,851 对的 P 值（P < 10⁻¹⁴⁵ 等）按独立观测计算，但作者对 TCGA 自设了 "treat pairs as independent, descriptive only" 标准——标准不一。【修：entry-clustered bootstrap 或统一降级 descriptive】
- **A4** 模拟 AUC 0.80 的鉴别任务部分由构造保证（neutral 定义为 HK 漂移=ω 分母消去的量）；CI 方法未明、未按 module seed 聚类；摘要 "ranked first for discrimination" 偏强。【修：明 CI 方法+seed 聚类；措辞软化】

### B. TCGA 推断链缺口（R3 主笔，R1 联署一条）——需新增分析
- **B1** 32 个细胞系（CC）样本进入 LIHC 主分析与 Cox/Edmondson 队列（291/2000 LIHC TT 对涉细胞系；ex-CC 后 LIHC k_n 升高 CI 已跨 1）。【修：主分析默认排除 CC，含 CC 降为敏感性】
- **B2** 缺 GTEx 健康组织参照——作者 Discussion 自己承认需要但未做；"肿瘤特异性管家失调" vs field effect 不可判别。【修：加 GTEx 第三组 k_n 排序】
- **B3** 组成校正 pooled −1.3% 掩盖癌种异质性（LIHC +32.8%、KIRC +19.6% 衰减恰在反转最弱癌种最强）；"admixture can only weaken, not create" 在癌种层面不成立。【修：主文报 per-cancer 衰减全范围；正式去卷积复核 LIHC/KIRC】
- **B4**（R1 Major 6 与 R3 M4 归并，单一计数）LUAD 协变量调整 OLS 把重叠配对的 per-tumor 均值当独立观测，无置换/cluster-robust 对应；未调整检验有置换复核而调整模型没有——不对称。摘要 "both survived purity and smoking adjustment" 依赖这些 P。【修：调整模型 whole-tumor 标签置换或混合模型】
- **B5** LIHC 映射口径敏感（linear 1.10 vs softmax 1.31），"四癌种 CI 排除 1" 依赖口径选择。【修：Supplementary Table 给两口径全表】
- **B6** 机制引用自相矛盾：HCC 管家失调文献引为支持，而 LIHC 恰是信号最弱癌种。【修：Discussion 显式讨论张力或弱化借力】
- **B7** kn_floor=1e-4 敏感性缺失（反转机制恰是 k_n 抬高，3/5 癌种 aggregate k_n 触底）。【修：floor ∈ {0,1e-5,1e-4,1e-3} 敏感性表】

### C. 脑部分混杂与粒度（R4）——需新增分析
- **C1** PMI/RNA 降解检验层级错误：应在 (class, library) 水平做回归/敏感性，而非当前层级。
- **C2** equal-n×span-matched 两种对照未组合（各自单独做，未交叉验证）。
- **C3** Supp Fig 7b ρ=0.142 动摇区域候选筛查的效应量叙事。
- **C4** 解剖学主题表述超出统计支持；supercluster 粒度与文献张力；4 供体结构需在正文更显眼地限定。

### D. ω 相对 k_f 的增量价值未在真实数据建立（R2，根本问题）——需新分析+叙事重构
- 仿真特异性部分同义反复（与 A4 重叠）；真实数据上 ω 的负相关是数学必然（分母消去）；脑梯度由 k_n 主导且受降解混杂；候选筛查是"统计空集上的叙事"（零 FDR 存活）；基准对 scDist 等不公平（Python approximation 而非原始 R 实现）；操作窗（100–200 cells）与 3.11 功率结果自相矛盾。

### E. 标题/摘要/结构（R5）——纯文字，可立即修
- **E1** 标题 "separating" 承诺过强 → "decomposing"。
- **E2** 摘要选择性呈现（只报有利数字）+ 密度失控；疑超 150 词指南（当前 197 词，NC 指南为建议性但 R5 认为应收）。
- **E3** k_n 72–118 倍类别间上升的机制未解释，读者会卡在这里。
- **E4** ω_cal 定位自相矛盾 + SI Note 3 不同步；裸 "(Section 3.x)" 指代残留；three-tier vs four-tier ladder 不一致（+12 Minor）。

### F. 复现档案硬伤（R6）——机械修复，但必须修
- **F1【最严重】** Code availability 引用的 tag v0.5.0 / Zenodo DOI 封存的是 v47 Genome Biology 投稿包（落后 HEAD 36 提交），**不含 nc49_*/nc50_* 任何脚本与结果**——按所引 DOI 跑不出本稿 Fig. 3/4 与 Note 16。NC 可复现性政策直接违反。【修：mint 新 release + 新 Zenodo version DOI，更新 Code availability】
- **F2** 依赖全为 >= 下界，无锁文件；Dockerfile 无锁；"numerically identical" 承诺不可兑现（作者自己证明数值对版本敏感，±9.8×）。【修：锁文件+措辞降级为容差表述】
- **F3** microglia 独立验证（nc50）在复现指南/spot_check/checklist 中完全缺失。
- **F4** run_all.py 停留在 GB v40 时代，编排队不到 nc49/nc50。
- **F5** SI 脚本索引指向已被取代的 07c（输出已入 superseded/）与不存在的 13_phase35_human_pairs.py。

### G. 事实性勘误（R1+R3 交叉核实确认）——纯文字
- 主文 "jointly with admixture, age, and sex" 暗示的四协变量模型在 CSV 中不存在（最多三协变量；n 427→411 未说明）。
- "high-purity-half ... increased the TT k_n elevation (LUAD 2.46 → 2.86)"：2.46/2.86 是 NN/TT ω 比值，非 k_n 升高倍数（标签错误）。
- Note 8 median TT/NN k_n ratio（2.18…）与主 pair 表中位数（2.60…）口径不符。

---

## 三、修复路线分层

**第一层：纯文字/机械修复（无需新分析，可立即执行）**
- E1–E4 全部（R5 明确"四个 major 全部是文字层修订"）
- F1–F5 全部（新 release+Zenodo、锁文件、指南/索引/run_all 更新）
- G 组三条勘误
- A4/B6 措辞软化、B5 对照表（数据已有，仅整理）
- R1/R2/R3/R4/R6 的 Minor 清单大部分

**第二层：重采样机器已有、改参数即可（中等工作量）**
- A1（两阶段 bootstrap 重报 7.70 CI）
- A2（donor-level cluster bootstrap）
- A3（entry-clustered bootstrap 或统一降级）
- B4（调整模型置换化——置换机器作者已有）
- B7（kn_floor 敏感性表——Note 9 已有 kn_floor=0 重跑框架）

**第三层：需新增分析/新数据（用户拍板）**
- B1（CC 默认排除后全链重跑——LIHC 结论方向可能改变）
- B2（GTEx 第三组——新数据下载）
- B3（BayesPrism/CIBERSORTx 去卷积）
- C1（(class,library) 水平 RNA 质量回归）
- C2（span×equal-n 组合校正）
- D（ω vs k_f 真实数据增量、原始 R scDist 重跑、筛查叙事降级重构）

---

## 四、审稿人共识与分歧

- **一致认可**：统计诚实度与披露纪律罕见地高（零模型设计匹配、小簇 bootstrap 自我修正、superseded 治理、种子披露、spot_check 实测通过——R6 亲验 40 断言+29 pytest 全过）。
- **一致担忧**：摘要级数字的精确度表述超出数据所能支持（R1/R2/R3 三条线独立指向同一症结）。
- **分歧**：R5/R6 认为修复后可达 8+（"修 #1–#5 后可达 8+"）；R2 认为 ω vs k_f 增量是根本问题，文字修订不能解决；R3 指出 B1/B2 修复后 LIHC 与机制两处结论方向可能改变。

---

*原始审稿全文存于各审稿 agent 返回消息；本文件为归并版，重复问题已单一计数（R1 Major 6 ≡ R3 M4）。*
