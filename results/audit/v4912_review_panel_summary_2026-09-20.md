# v49.12 盲审汇总（第三轮，2026-09-20）

**对象**：CKI_Submission_v49_NC.zip v49.12 + XV3 补丁（commit 6a24578，zip 12,260,471B sha256 4c96ac95…，构建 165/165）
**盲审材料**：results/audit/_v4912_review/ 四件套提取文本（MS sha 242abd93 / SI 272afe35 / CL 61670d50 / GUIDE 771dbd91），任务书数字全部取自当版文本
**前轮**：v49.9 4.42（1R+4M+1Minor）→ v49.10 5.83（4M+2Minor）

## 一、评分与推荐

| 审稿人 | 视角 | 评分 | 推荐 | 报告 |
|---|---|---|---|---|
| R1 | 算法与方法学 | 7.2 | Minor | v4912_review_R1_2026-09-20.md |
| R2 | 概念/进化框架 | 8.0 | Minor | v4912_review_R2_2026-09-20.md |
| R3 | 统计学 | 8.3 | Minor（修 N4/N5 后可 Accept） | v4912_review_R3_2026-09-20.md |
| R4 | TCGA/泛癌 | 8.0 | Minor | v4912_review_R4_2026-09-20.md |
| R5 | 脑科学 | 7.5 | Minor | v4912_review_R5_2026-09-20.md |
| R6 | NC 编辑 | 7.4 | Minor | v4912_review_R6_2026-09-20.md |
| **均分** | | **7.73**（上轮 5.83，**+1.90**） | **6/6 Minor Revision，无 Major 无 Reject** | |

## 二、主代理核验（指控 vs ground truth）

| 指控 | 裁定 | 证据 |
|---|---|---|
| R4-N4 "−16%~+37% 区间数字硬伤" | **驳回（审稿人误读）** | tcga_composition_v44.txt：点估计 BRCA −15.9%…LIHC +37.9%；bootstrap median −16.2%…+37.1%——MS 区间与两套口径均吻合；R4 所称 "BRCA −6.2%" 不存在于 ground truth |
| R4-N5 "absorb 措辞与符号矛盾" | **驳回（符号方向读反）** | 正衰减=系数被吸收：LIHC +0.5656→+0.3510（降 37.9%）、KIRC +1.1884→+0.9703（降 18.3%），Note 8 措辞与数字方向一致 |
| R3-N4 "Guide 5.7 softmax 残留" | **确认** | Guide 行 203/285 两处：ρ=0.387×2、"−0.5% pooled (95% CI [−3.2%, +2.6%]; per-cancer BRCA −14.0%…LIHC +33.5%)"×2，无 superseded 标签——三文档口径链断裂 |
| R3-N5 "MS \|Δz\| 数值不可溯源" | **确认** | MS Discussion 的 1.30-fold/1.23-fold、P=8×10⁻¹⁴⁰/3×10⁻⁷⁴ 在 SI（softmax 段 1.33–1.46/1.24 旧值，linear 更新段无 |Δz|）与 Guide 全文均查无——上轮 XV3 补丁只写 MS 未同步 SI |

## 三、确认问题汇总（按修复类型分组）

**A. 文档级口径/溯源（纯文本，无需计算）**
- A1（R3-N4）Guide 5.7 两处 softmax 组成检验数字补 superseded 标签 + linear 权威值
- A2（R3-N5）SI Note 8 linear 更新段补 |Δz| 1.303/1.227-fold、P=7.87×10⁻¹⁴⁰/2.66×10⁻⁷⁴；linear ρ=0.355 补 P
- A3（R2-N1）MK 半格错位：三重对应实为 dN/dS 谱系；修法二选一——(a) 补第四重对应（split-half 校准 ω=7.70=多态类类比，ω_cal≈neutrality index 方向）(b) [34] 降为纯 dN/dS 引用
- A4（R6-N3）CL "the first framework" 与 Discussion "recombination of established ideas" 语调对齐
- A5（R1 次要-实错）Kang 0/30 CI [0.000,0.114] 标注 Wilson 实为 Clopper-Pearson 上界（Wilson≈0.107）；SI 1.6 "min 10 cells" vs 正文 "≥20" 不一致
- A6（R6-N2）正文统计密度下沉 Methods/SI（bootstrap-t 覆盖率、MC 误差界 15-20 处）
- A7（R5-N6）donor-stratified null 逐类 P 值/可打乱文库数/恒等置换占比补表

**B. 低成本计算（现有数据脚本级）**
- B1（R5-N4）region-matched 控制：astrocytes 小脑内子集 vs Bergmann glia（span-balanced）；修前 1.74 标注 "size-balanced but not span-balanced"
- B2（R5-N5）equal-n 降采样上的 k_f/k_n 分量分解（残余 1.74 的归属）
- B3（R1-N1）校准常数 7.70 的 leave-one-out（hepatocyte 12.44±5.98 vs 其余 5.77–7.36，拉高 ~13%）
- B4（R1-N2）LUAD KW/Dunn 二元依赖重算（cluster/permutation）或统一降级 descriptive
- B5（R4-N3）剔 CC 版 admixture 敏感性复算（CC 细胞系纯度高，高纯半区 1.10→1.17 可能部分由其驱动）
- B6（R4-N1/N2）CC 分析报告补全：Methods 实施细节、脚本/输出落盘、五癌种 barcode 源码分布表

**C. 论述级（无需新分析）**
- C1（R6-N1）label-permutation（P>0.9）与 bootstrap CI 并存的调和句（两框架假设不同）
- C2（R2-N2）标题 "quantifying functional divergence" 与 k_f 默认降级的张力（R6 同款观察）
- C3（R1-N3/N4/N5）聚合顺序定包默认；top-200 N 敏感性扫描声明；Augur primary variant post-hoc 披露
- C4（R4-N6）KRAS TP53 共突变/黏液亚型/pack-years 残余混杂披露；OLS ω 尺度 vs log 不一致；Abstract "attributable to" 去因果化
- C5（R2-N3/N4）SI 1.4 key differences 补 ascertainment asymmetry；constrained reference class 后果集中进化语言化

## 四、结论

第三轮盲审均分 **7.73（+1.90）**，六位审稿人**全员 Minor Revision、零 Major 零 Reject**——修复链有效：上轮全部 N1-N5+C2-C7 修复均被各自对口审稿人核实通过（R3 逐数值对照、R5 三处口径统一、R4 CC 核心结论、R2 MK 接受、R1 三处修复+数字三文本互检）。剩余问题无推翻性科学问题：A 组纯文档、B 组脚本级、C 组论述级。R3 判定"修 N4/N5 后可 Accept"。
