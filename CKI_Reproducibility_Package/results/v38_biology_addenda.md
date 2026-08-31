# v38 生物学补充分析（P3-12 / 共识 1 与 6 响应）

日期：2026-08-29　脚本：`notebooks/_v38_biology_addenda.py`　数据：`reviewer_brain_pair_kf_kn.csv`（31,764 脑区对）、`phase33_v3_human_pairs.csv`（5,151 人图谱对）、`phase34_v2_all_pairs.csv`（35,306 TCGA 对）。

每个分析给出：方法一句话、结果数值表、对稿件结论的影响判断（支持 / 需降调 / 需修正）。


## A1. 排除 Bergmann glia 后的脑区梯度

**方法**：从 31,764 对脑区 ω 中剔除 Bergmann glia 的全部 21 对（其比较全部位于小脑内部），重算 9 类 max/min 类均值梯度，并用对级 bootstrap（B=2,000）给 95% CI。


| 指标 | 数值 |
|---|---|
| 全 10 类梯度（Astrocyte / Bergmann glia） | **6.10x** |
| 排除 Bergmann glia（Astrocyte / Vascular） | **6.10x**（bootstrap 95% CI [6.00, 6.21]） |
| 再排除 choroid plexus（8 类） | 6.10x |
| 梯度新低端 Vascular 的 block-shuffle 类级 P | 0.1149（显著） |

完整类均值表见 `_v38_brain_gradient_excl_bergmann.csv`。

**影响判断：支持（结论稳健，但需加限定语）**。排除 Bergmann 后梯度仍 6.10 倍、CI 下限 6.00，远大于 1；全 10 类梯度 6.10x 与排除后 6.10x 一致（Bergmann 与 Vascular 均值并列最低），梯度低端稳健，摘要宜按 R3 建议改为 "6.1-fold excluding Bergmann glia" 或加采样范围限定语。


## A2. k_f-only 与 k_n-only 梯度对照（分量分解）

**方法**：对同一批 31,764 对计算各类 k_f 均值与 k_n 均值，分别给出 k_f-only / k_n-only 梯度倍数、与 ω 类排序的 Spearman ρ，并对 6.10 倍端点（astrocyte vs Bergmann glia）做乘法分解 6.10 ≈ (Δk_f)×(Δk_n)。


| 量 | 数值 |
|---|---|
| ω 梯度（10 类） | 6.10x（Astrocyte→Bergmann glia） |
| k_f-only 梯度 | 4.1x（Committed oligodendrocyte precursor 最高 → Oligodendrocyte precursor 最低） |
| k_n-only 梯度 | 6.7x（Vascular 最高 → Oligodendrocyte precursor 最低） |
| Spearman ρ(ω 类均值, k_f 类均值) | 0.09（P=0.803） |
| Spearman ρ(ω 类均值, k_n 类均值) | -0.73（P=0.02） |
| 端点分解：k_f(astro)/k_f(BG) | 0.1349/0.0666 = **2.03x** |
| 端点分解：k_n(BG)/k_n(astro) | 5.83e-03/1.81e-03 = **3.21x** |
| 乘法预测 ω 比 | 2.03×3.21 = 6.51（实测 6.10） |
| astrocyte 在 k_f-only 排序中的名次 | 第 3/10 |

各类 k_f/k_n/ω 均值全表见 `_v38_brain_kf_only_gradient.csv`。

**影响判断：需修正（证实共识 1）**。6.10 倍梯度的端点对比中 k_f 仅贡献 2.03 倍、k_n 贡献 3.21 倍（乘积 6.51≈6.10）；k_f-only 排序下 astrocyte 仅列第 3，且 ω 类排序与 k_f 类排序无秩相关（ρ=0.09）、与 k_n 类排序呈负相关（ρ=-0.73，k_n 越小 ω 越高）。「星形胶质细胞功能分化最强」的功能基因解读不成立，应改写为「composite divergence gradient，主要由 HK 程序跨区稳定性（k_n）差异驱动」。


## A3. same-organ 反转的分量分解

**A3a 人图谱（Tabula Sapiens，5,151 对）**。**方法**：same-organ 与 different-organ 对的 ω 差按恒等式 log ω = log k_f − log k_n 分解为两个分量均值之差；并对 k_f、k_n 分别做 Mann-Whitney U 检验；另以线性回归检查控制 log k_n 后 same-organ 对 log k_f 是否仍有效应。


| 分量 | same-organ (n=1,140) | diff-organ (n=4,011) | 差（same−diff） |
|---|---|---|---|
| ω 均值 | 24.71 | 20.56 | +4.15（**1.20x**，P=1.9e-23） |
| k_f 均值 | 0.2473 | 0.2496 | -0.0023（P=0.60，不显著） |
| k_n 均值 | 0.01295 | 0.01478 | -0.00184（P=3.03e-16，same-organ 显著更低） |

| log 尺度分量贡献 | 数值 |
|---|---|
| Δlog ω（反转总量） | +0.1707（= 1.19x） |
| Δlog k_f（分子贡献） | -0.0053（≈ 0.99x，可忽略且方向相反） |
| −Δlog k_n（分母贡献） | +0.1760（≈ 1.19x，**占全部反转**） |
| 控制 log k_n 后 same-organ 对 log k_f 的偏回归系数 | +0.0741（P=9.8e-10，条件于 k_n 时 k_f 仅高 ~8%，远小于分母贡献） |

**影响判断：需修正（证实 R3-M3）**。same-organ 反转（24.7 vs 20.6）100% 由分母驱动：same-organ 对的 k_f 与 diff-organ 无差异（甚至略低），但 k_n 显著更低（共享微环境压低 HK 基线散度），使 ω 升高。稿件将反转解读为「CKI 检测到共享微环境内功能特化」的证据不成立；应改写为「器官内比较中 HK 基线更稳定，归一化分母更小，ω 灵敏度更高」。

**A3b TCGA NN/TT 反转（5 癌种）**。**方法**：同一分解应用于每癌种 normal-normal（NN）与 tumor-tumor（TT）对：log(ω_NN/ω_TT) = Δlog k_f − Δlog k_n（log 均值差）。


| 癌种 | ω_NN/ω_TT（中位数） | k_f_NN/k_f_TT | k_n_NN/k_n_TT | Δlogω | Δlog k_f | −Δlog k_n | P(k_f NN<TT) | P(k_n NN<TT) |
|---|---|---|---|---|---|---|---|---|
| TCGA-BRCA | 1.51x | 0.54x | 0.36x | +0.298 | -0.702 | +0.999 | <1e-300 | <1e-300 |
| TCGA-KIRC | 2.19x | 0.64x | 0.27x | +0.776 | -0.425 | +1.202 | <1e-300 | <1e-300 |
| TCGA-LIHC | 1.23x | 0.60x | 0.45x | +0.159 | -0.428 | +0.587 | 1.0e-246 | 2.0e-96 |
| TCGA-LUAD | 2.32x | 0.74x | 0.38x | +0.882 | -0.205 | +1.086 | 2.0e-131 | <1e-300 |
| TCGA-LUSC | 1.77x | 0.62x | 0.37x | +0.474 | -0.456 | +0.930 | <1e-300 | 1.2e-227 |

5/5 癌种：k_f 方向与反转**相反**（肿瘤对 k_f 更高，NN/TT k_f 比 0.5–0.7x），而 k_n 一致压低 NN 的分母（NN/TT k_n 比 0.3–0.5x）。「肿瘤比癌旁正常组织更趋同（NN/TT>1）」完全由 k_n 驱动：正常组织对的 HK 程序散度更低，不是肿瘤对的功能基因分化更小。

**影响判断：需修正（证实 R3-M4-2）**。TCGA「趋同」结论须改写为分母效应；分量表（`_v38_tcga_nn_tt_reversal_decomposition.csv`）应随分量分解表一并进入正文/补充。


## A4. TCGA kn_floor 饱和分解

**方法**：在权威对级文件 `phase34_v2_all_pairs.csv`（35,306 对）上，(i) 检验 ω 与 k_f/k_n 的恒等关系以识别 clamp 触发；(ii) 统计各癌种/对型 k_n 低于 floor（1×10⁻⁴）与 2×floor 的对数与占比；(iii) 计算各层 ω 与 k_f 的 Spearman ρ（若 ρ≈1 则 ω 排序实质是 k_f 排序）；(iv) log ω = log k_f − log k_n 的方差分解。


| 指标 | 数值 |
|---|---|
| max\|ω − k_f/k_n\|（>0 即存在 clamp） | 5.3e-10（=0，**无任何对被 clamp**） |
| k_n < 1×10⁻⁴ 的对 | 0 / 35306（0.0%） |
| k_n < 2×10⁻⁴（贴地）的对 | 1 / 35306（0.003%） |
| 全体 k_n 最小值 | 1.62e-04（各层最小值见 CSV） |
| Spearman ρ(ω, k_f)（全体） | -0.103 |
| Spearman ρ(ω, k_n)（全体） | -0.868 |
| var(log k_f) / var(log k_n) | 0.214 / 0.770（k_f 占 22%） |
| 恒等式复核 var(log k_f−log k_n) vs var(log ω) | 0.6403 vs 0.6403 |
| 对照：脑区数据（kn_floor=0）k_n<1×10⁻⁴ 对数 | 1 / 31,764（与稿件声明一致） |

各癌种×对型明细（n、k_n min/p05/中位数、饱和计数、ρ(ω,k_f)）见 `_v38_tcga_kn_floor_saturation.csv`。

各癌种×对型 ρ(ω,k_f) 范围：-0.252–0.458。


**影响判断：需修正（对级数据推翻「ω 退化为重标度 k_f」的前提，但稿件表述仍须改写）**。
1. **对级数据中 floor 从未触发**：35,306 对里 0 对 k_n<1×10⁻⁴（最小 1.6×10⁻⁴，仅 1 对低于 2×floor），ω 与 k_f/k_n 严格相等（最大偏差 5×10⁻¹⁰），不存在「饱和对 vs 非饱和对」的对比——饱和对占比 **0%**。
2. 稿件 Limitation 20「aggregate tumor-versus-normal k_n 3.0×10⁻⁵–1.9×10⁻⁴、ω 在 3/5 癌种饱和于 k_f/10⁻⁴」描述的是**聚合层**（全肿瘤均值 pseudobulk vs 全正常均值 pseudobulk 这一个比较，v1 期数值），而非现行权威对级数据（phase34_v2）；且现行临床分析脚本（`07_phase34_clinical.py`）调用 `compute_omega` 时未传 kn_floor（默认 0，不 clamp）。该 Limitation 应改写并明确区分聚合层与对层。
3. **与评审预期相反，对级 ω 并非 k_f 的重标度**：ρ(ω, k_f) 全体仅 -0.10（各癌种×对型 -0.25–0.46），log 方差中 k_n 占 78%（var(log k_n)=0.77 vs var(log k_f)=0.21）——因为 floor 从不生效，分母 k_n 在对级携带了最多的变异。共识 6 / R1-M7 的「TCGA 部分 ω≡排序 k_f」推断建立在对级饱和的假设上，该假设不成立；但这同时意味着 TCGA 的 ω 与脑区一样是 k_n 主导的复合信号，「功能扰动」解读同样需要分量证据。
4. R1-M7 的另一半建议（k_f-only 临床分层对照表）仍值得做，但因对级无饱和，预期结果不是「与 ω 完全一致」而是「k_n 主导」——归因方向与 R1 预期相反。


## 汇总：对稿件四项结论的影响

| # | 分析 | 核心数值 | 判定 |
|---|---|---|---|
| A1 | 排除 Bergmann 梯度 | 6.10x → **6.10x**（95% CI [6.00, 6.21]） | 支持（加限定语） |
| A2 | k_f-only 对照 | 端点 k_f 仅 **2.03x** vs k_n **3.21x**；ρ(ω,k_f)=0.09 | 需修正（共识 1 成立） |
| A3 | same-organ 反转分解 | Δlog k_f=-0.005（不显著） vs −Δlog k_n=+0.176；TCGA 5/5 癌种 k_f 方向相反 | 需修正（分母驱动） |
| A4 | kn_floor 饱和 | 对级饱和 **0 对（0%）**；ρ(ω,k_f)=-0.10，k_n 占 log 方差 78% | 需修正（表述+归因） |

新文件：`results/_v38_brain_gradient_excl_bergmann.csv`、`results/_v38_brain_kf_only_gradient.csv`、`results/_v38_same_organ_reversal_decomposition.csv`、`results/_v38_tcga_nn_tt_reversal_decomposition.csv`、`results/_v38_tcga_kn_floor_saturation.csv`、`results/v38_biology_addenda.md`。
