# NC80 六条 Ground-Truth 裁定（方案 b 前置）

日期：2026-11-16。全部数字实跑核验，未修改任何稿件/生成器/产物文件。

---

## 裁定 1：paired TN 样本量（bio M6 vs SI §3.6）——**bio 对，SI 错，paired 分析可行**

- 底层真实数据（`data/tcga/tcga_RSEM_gene_tpm.gz` 表头直算）：每癌种**同时有肿瘤+正常样本的病人数** = LUAD 75 / LUSC 58 / LIHC 57 / KIRC 82 / BRCA 108（即 distinct normal barcodes 57–109，bio 属实）。
- `results/tcga_linear_norm_v44_all_pairs.csv` 是**抽样表**（`85_tcga_linear_norm_v44.py` MAX_PAIRS_TN=2000，从全枚举无放回抽样）；抽样内同病人 TN 对只剩 2–5/癌种（BRCA 4/KIRC 2/LIHC 2/LUAD 5/LUSC 3）。
- SI §3.6 「the paired tumor-normal analysis (n = 2-5 per cancer type) lacks statistical power」——n=2–5 是**抽样伪影**，把样本量当成了总体。结论错误。
- **行动**：SI §3.6 第四条 caveat 必须改写；paired within-patient TN 分析升级为 P1 最高优先新对照（57–108 对/癌种，min two-sided P 远小于 0.33）。bio 的判断「strongest new control」成立。

## 裁定 2：「admixture can only weaken, not create」（MS L573 锁句 vs Note 10）——**bio 指控成立，锁句需改**

- 原始产物 `results/nc52_tcga_composition_excc.csv`：LIHC TT 系数 +0.5208 → 4-panel 调整后 +0.2912，**吸收 +44.1%**（cluster bootstrap 中位 +43.4% [+29.9, +60.0]）；KIRC +19.7% [+14.5, +25.3]。
- 正衰减 = 组成协变量吸收肿瘤系数 = admixture 是 elevation 的**正向贡献者**（创造其一部分），与「can only weaken, not create」方向矛盾。
- 稿件 L573 的推论只从 high-purity-half 一个对照（纯度分层）泛化到全称命题，与同 SI Note 的 per-cancer 回归冲突。
- **行动**：锁句（NC60-B3 断言）改为限定式——purity-split 自身结论照报（「high-purity halves raise the ratio in all five」），删除全称「can only weaken, not create」；改与 LIHC/KIRC 吸收并存的事实陈述（pooled −0.9% 但 per-cancer 异质 −16% 至 +44%）。同步改 NC60-B3 断言。

## 裁定 3：mouse α CI [4.24, 9.24] vs [4.12, 9.33]（math m2）——**稿件自洽，[4.12,9.33] 仅存历史；实质指控成立**

- 权威值 = **[4.24, 9.24]**：`notebooks/44_fix_phaseB_cis.py` 注释明确记载（任务 #950 裁定）——fresh RandomState(42) 会给 [4.12, 9.33]，committed CSV 的 [4.24, 9.24] 保持权威。math 所说「四件套内无 [4.12, 9.33]」属实。
- 但 math m2 实质指控成立：Note 20 与 Fig 2b 图注用被 superseded 的 6.67 定义 α 操作范围下限（"empirical split-half baselines (6.67–9.73)"）。
- **行动**：范围下限改用现行校准 7.70 [6.38, 9.82]（即写 7.70–9.73 或 7.67–9.73 跨数据集范围），不再让 superseded 值定义符号范围。

## 裁定 4：HRT panel 无经典 HK 基因（bio m1）——**bio 对，属透明度问题非稳健性问题**

- `data/housekeeping/Human_Mouse_Common.csv` 直查：1,130 基因中 **ACTB/GAPDH/B2M/PPIA/EEF1A1/RPLP0/HPRT1/TBP/UBC/YWHAZ/SDHA 全部不在**（human 与 mouse 侧均无）。Eisenberg–Levanon 稳定表达筛选本就排除经典参考基因。
- SI Note 8（`68_gen_supplementary_nc.py` L2416）用 ACTB/GAPDH 作机制示例（"fall roughly 40% in stimulated cells"）——示例基因不在 anchor panel 内。
- **行动**（bio 自己已定性为 transparency/interpretation）：P0 文字修复——Note 8 示例处注明「经典参考基因（不在 HRT anchor 内），仅作机制示意」或改用 panel 内基因；P1 增加 panel characterization（表达排名分布、功能类组成、与经典 HK 集重叠）。

## 裁定 5：「roughly 40-fold」（stat m3 = math m7）——**指控成立，精确值 150-fold**

- `results/perclass_calibration.json` 直算：split-half k_f floor 类间范围 = Oligodendrocyte **0.000129** → Committed OL precursor **0.019557**，真实比率 = **151.3 倍**。
- 稿件「roughly 40-fold」错误；math 提的 200-fold 是四舍五入端点（0.020/0.0001）的比，同样不精确。
- **行动**：SI Note 3 改为「roughly 150-fold (from 1.3 × 10⁻⁴ in oligodendrocytes to 0.020 in committed oligodendrocyte precursors)」。

## 裁定 6：KIRC gap 0.833 vs 1.181（stat M1）——**两值均真、口径不同，share v2 分母必须统一**

- 0.833 = `scripts/nc79_a1_measured_share.py` 的 Δ_obs，在 **DNA-profiled 肿瘤对子集**上算（KIRC TT n=871/2000）；1.181 = **全配对表** TT−NN mean log k_n gap（2000 TT vs 3321 NN）。稿件读者看到的反转是全表口径。
- 各癌种两口径差距：BRCA 0.990/0.993（几乎相同，DNA 覆盖 94%）、KIRC 0.833/1.181（**差 42%，DNA 覆盖仅 44%**）、LIHC 0.456/0.530、LUAD 0.955/1.077、LUSC 0.754/0.849。
- 用全表 gap 作分母的初步份额（C 不变）：BRCA 0.621 / KIRC **0.417** / LIHC 0.894 / LUAD 0.478 / LUSC 0.566。
- **行动**（#1243 share v2 的核心）：分母统一到全表 Δ_obs（headline 反转的口径）；per-cancer 份额+CI 全披露（LIHC >1 必须写出）；放弃 IVW 比率合并（对称 SE 假设对 LIHC 5.4:1 偏斜 CI 不成立），改直接 bootstrap 合并或联合模型；share(δ) 曲线保留。KIRC 的 DNA 覆盖率 44% 一并披露。

---

## 汇总表

| # | 指控来源 | 指控内容 | 裁定 | 修复层级 |
|---|---|---|---|---|
| 1 | bio M6 | paired TN 57–109 vs SI n=2–5 | **bio 对**（SI 引用抽样伪影） | P0 文字 + P1 新分析（最高价值） |
| 2 | bio M3 | 「only weaken」vs LIHC +44.1% | **成立**（锁句过度泛化） | P0 改锁句 + NC60-B3 断言 |
| 3 | math m2 | mouse α 两 CI + superseded 定义范围 | 数字自洽；**范围下限须改 7.70** | P0 文字 |
| 4 | bio m1 | HRT panel 无经典 HK + Note 8 示例 | **成立**（透明度问题） | P0 注记 + P1 characterization |
| 5 | stat m3/math m7 | 40-fold | **成立，精确值 150-fold** | P0 一词 |
| 6 | stat M1 | KIRC gap 口径错配 | **成立**（0.833=DNA 子集/1.181=全表） | #1243 share v2 核心 |

裁定 1、2、6 直接改变 #1243/#1244 的改稿内容；3、4、5 为 P0 文字修复项，随方案 b 改稿一并落地。
