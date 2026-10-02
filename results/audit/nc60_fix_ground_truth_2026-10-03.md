# nc60 修复轮 — ground-truth 裁定报告（2026-10-03）

裁定方法：六审指控逐条对照生成器源码（generate_manuscript_nc.py / notebooks/68_gen_supplementary_nc.py /
notebooks/100_gen_reproducibility_nc.js / README.md）、fresh docx 提取文本（_nc60_*_fresh.txt）与
results/ 权威输出文件复核；数值类指控一律独立复算。仓库基线 main @c80c3da。

## 一、A 类（机械）裁定

| # | 指控 | 裁定 | 证据 |
|---|------|------|------|
| A1 | SI §3.12 "main-text Fig. 3d" → 应为 3a | **真阳性** | 68_gen L1043；MS Fig. 3 caption 仅 (a)(b)(c) 三面版，Kang replication = panel a，无 (d) |
| A2 | Supp Table 14 caption "Main-text Fig. 5b-d" → 应为 Fig. 4b-d | **真阳性** | 68_gen L1354；Table 14 = LUAD Dunn post-hoc，对应 MS Fig. 4b-d（Fig. 5 为 cross-organ） |
| A3 | MS barcode audit 指针 "Section 1.7" → 应为 Supp Methods 5.3 | **真阳性** | MS Results "found by barcode audit (Section 1.7 of the Supplementary Information)"；SI Section 1.7 = Probability-Mapping Robustness，barcode audit 实在 5.3（MS Methods 自身另一处已正确写 5.3） |
| A4 | SI "v0.5.4" 残留 | **真阳性 ×2** | 68_gen L569、L795（Guide 另有 3 处，见 A8） |
| A5 | "3 of 39 (Supplementary Note 14)" | **数值真、指针假** | 权威复算 results/nc52_brain_candidate_effectsize.csv：n_strong_persist=3（global-k_n 下 107 Strong，存留 3、失 36、增 104，frac 0.077）——数值=3 正确（R2 独立复算一致，本人第三次复算一致）；但 Note 14（set-level enrichment）不含此内容，global-k_n 敏感性实在 SI §3.5（68_gen L742），且 SI 全文无 "3 of 39" 明文 → 须补写入 §3.5 并改 MS 指针 |
| A6 | "four-donor structure (Supplementary Note 13)" | **真阳性** | Note 13 = Region Glossary；four-donor 结构实在 Supp Methods 5.4/5.7 与 Note 11（L2417 donor bootstrap "the four donors resampled"）→ 改指 Note 11；同段 "Microglial … (Supplementary Note 13)" 亦应改指 Note 14（microglia composition null，v50 迁入） |
| A7 | SI docx 附表说明块物理序 1,4,5,6,2,7-14,3,15-19 | **真阳性** | fresh docx 提取首现序实测 = 1,4,5,6,2,7,8,9,10,11,12,13,14,3,15,16,17,18,19（nc59 已重排 xlsx 19 sheet = 1..19 与 Notes 块，但 docx 内嵌表说明块漏排） |
| A8 | Guide "v0.5.4" ×3 + 全文无 Zenodo | **真阳性** | 100_gen：'Version: 0.5.4'、'Install CKI v0.5.4'、'in tag v0.5.4'；无 zenodo 字样 |
| A9 | README 陈旧 | **真阳性 ×5** | '6.67' ×2（现值 7.70）、'docker cki:0.5.0' ×2、'Submitted to Genome Biology' ×2、'manuscript Note 3.19'（不存在该编号） |
| A10 | Guide 误引 notebooks/13_phase35_human_pairs.py | **真阳性** | 真名 13_phase35_method_comparison.py（ls 核对） |
| A11 | 14 个附图 legend 在 MS 末尾、SI 内无图注 | **真阳性** | MS 末尾有 "Supplementary Fig. 1–14." 全套 legend；SI docx 图注式 caption 0 条 → 迁入 SI |
| A12 | Supp Tables 7–19 MS 零引用 + "Supplementary Data 1" 零引用 | **真阳性** | MS 引用计数：Tables 1–6 各 1 次，7–19 各 0 次；"Supplementary Data" 0 次 |

## 二、B 类（实质表述）裁定

| # | 指控 | 裁定 | 证据 |
|---|------|------|------|
| B1 | 摘要/CL 脑支柱措辞超界 | **真阳性** | 摘要仅 "In a human brain atlas, CKI quantified a regional differentiation gradient and provided a statistically calibrated framework"，未披露非神经元 888,263/~3.3M 核范围、k_n 分母主导、零 FDR 存活 → 加限定（摘要 195/200 仅 5 词余量，须置换式改法） |
| B2 | 抗富集 P(null count ≥39)=1.0 行文方向 | **真阳性（歧义）** | MS Results/Fig 6c caption 现句读作阴性，实为最强证据（期望 148.3 vs 观察 39）→ 补方向性子句 |
| B3 | GTEx field-effect MS 强于 SI tentative | **真阳性** | SI Note 10 有 "(tentative, GTEx cross-cohort discrepancy unresolved)"；MS 两处（intro 末段 + Results four-controls 段）无限定 → MS 补 tentative 限定 |
| B4 | k_n 升高缺 batch/TSS 替代解释排除声明 | **真阳性** | MS/SI 全文无 'TSS'；GTEx 跨队列位移 1.8–2.3× 与信号 1.3–3.3× 同量级 → 加诚实限定：claim 依据同队列 tumor-vs-adjacent 对照，跨队列 healthy 参考仅描述性 |
| B5 | LUAD driver 断言需明确 bulk tissue-state 关联 | **部分真阳性** | MS 已有 "TP53 co-mutation and histological subtype were not adjusted for, so residual confounding remains"；缺 "bulk tissue-state association" 明确定性 → 补短语 |
| B8 | 现代基线边界（marker Jaccard T1 FPR 19.9% < ω 28.6%） | **部分假阳性** | MS Fig. 3c caption 已披露 "marker Jaccard is lower still on the false-positive statistic (T1 19.9%, T2 74.7%) but responds weakest to real regional divergence (T3 calibration 1.41 versus 1.80 …) and offers no k_n/k_f decomposition"；摘要限定 "among continuous divergence metrics"。Discussion 无 prose 呼应 → 若词额允许补一句，否则视为已答 |
| B9 | Augur ρ=0.442/0.564 (n=10) "moderately concordant" 过强 | **真阳性** | MS 现文 "rankings are moderately concordant … descriptive only at n = 10 classes"；n=10 下 P=0.20/0.09 均不显著 → 软化措辞 |
| B10 | tier 与 P 同源单调 caveat 未进正文 | **真阳性** | Note 14 已声明 "partly guaranteed by construction"；MS 无 → 补短句 |
| B11 | donor-bootstrap CI 挂错点估计 | **真阳性** | SI Note 11 权威：span-matched 观察 3.68（ratio of class means），donor bootstrap ratio-of-means **3.28 [1.67,3.97]**；combined 观察 3.66 [3.60,3.71]（cell-resampling），donor-level median **3.28 [1.92,3.78]**。MS 把 [1.67,3.97]/[1.92,3.78] 直接挂在 3.68/3.66 上 → 重新归属 |
| R3-m1 | LIHC "1.10" vs "1.11" 不一致 | **假阳性** | 现行 MS ×2、SI、Guide、CL 全部 1.11（1.10 仅出现于 scipy ≥1.10.0）；Fig 4 生成脚本无 1.10 字样 → 无需动作 |
| R3-m2 | "~84%" 复算仅 ~82% | **真阳性（双方皆不准）** | 独立复算（results/tcga_linear_norm_v44_all_pairs.csv + data/tcga/luad_egfr_kras_mutations.json，ex-CC、61/120/311 与文本一致）：组均值口径 k_n 占比 112%、恒等可加 mean-log 口径 72.7%、median 口径 79.6%——文本 84% 与 R3 的 82% 均不可复现。修复：采用恒等可加 mean-log 口径（log ω = log k_f − log k_n per-pair 恒等）~73%，或降级定性 |
| R3-m3 | §3.13 半括号 CI 归属含糊 | **真阳性（歧义，非数值错）** | SI "high-purity-half 1.17 versus 1.19 excluding CC, 95% CI [1.01, 1.44]"；ground truth：1.167 (full) CI [0.968,1.412]（nc49_tcga_purity.csv D_nntt_highpurity LIHC）、1.188 (ex-CC) CI [1.005,1.435]（Guide 记载一致）→ 两 CI 并列写明归属 |
| R3-m4 | intro 末句语气 | **真阳性（minor）** | 随 B3/B9 一并软化 |

## 三、新增分析需求（任务 #1120）

- R2-M1 配对 ΔAUC：simulation 中 ω AUC 0.80 vs k_f 0.72（摘要口径）需配对比较（per-rep Δ + bootstrap/CI）；数据可得性待查（simulation per-rep 输出）。
- R2-M2 T1 FPR McNemar 式配对检验：2,161 T1 pairs、4 donors 聚类；Supp Table 10 caption 自点 McNemar 未做；数据 nc49_brain_drift_ladder.csv（3.3MB，含 per-pair per-metric FPR 判定）可得。

## 四、词额约束

MS MAIN 4,998/5,000（XV8 口径）——**零余量**。所有 MS 侧 B 类修改必须置换式（删改相当），新增引用（A12）须以最小词数并入既有括号。摘要 195/200，余量 5 词。

## 五、裁定汇总

- A 类 12 项：真阳性 12/12（A5 数值真指针假，计入修复）。
- B 类 11 项：真阳性 9，部分真阳性 1（B5），部分假阳性 1（B8，caption 已披露）。
- R3 minors 4 项：真阳性 2（m2/m3）、假阳性 1（m1）、minor wording 1（m4）。
- 复算底稿：84% 分解（5 口径）、global-k_n 存留（3 口径交叉）、lowest_in_pair 定义（region-pair min-ω，100% 吻合）、purity CI 两值归属——均记录于本报告。
