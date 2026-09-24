# nc52 稿面修复 + 断言三层同步收尾报告（#18/#19）

日期：2026-09-24 ｜ 范围：MS/SI/Guide/CL 稿面残留修复 → 99_build / verify×3 / XV8 全量同步 → 全绿

## 最终状态（全绿）

| 套件 | 结果 | 日志 |
|---|---|---|
| 99_build_nc_v49（含 MS/SI/CL+Guide verify 三 run） | **221/221 PASS, 0 FAIL** | `_v52_build_log6.txt` |
| spot_check.py（46 断言） | **ALL CHECKS PASSED**（R6 条件①） | `_v52_spotcheck_log.txt` |
| pytest tests/（29） | **29 passed**（R6 条件②） | `_v52_pytest_log.txt` |
| XV8（_nc51_xv8.py，63 项） | **63/63 ALL PASS**；MAIN 4,998/5,000、Abstract ≤200、引用 73 组 1..57 | `_v52_xv8_log2.txt` |

## 一、本轮新发现并修复的稿面问题（#18 收尾）

1. **SI 5.12 方法段 v51 旧文**（statsmodels PHReg、ex-CC-as-sensitivity、nc49 脚本名）→ 重写：ex-CC 为默认队列（n=272/79 events）、R survival::coxph + stage 分类 + cox.zph（M2 GLOBAL P=0.023 照报）、新增 whole-tumor 置换调整模型方法（B=10,000；KRAS≤0.001/EGFR≥0.28）、脚本/输出清单全部换 nc52 名。
2. **Note 8 TCGA 段**：pair table 35,306→ex-CC 34,828（478 CC-touching 对剔除）；Cox 段同上重写；脚本清单 nc52 化；Section 1.7 脚本行补 nc52 主链/softmax/mapping-schemes。
3. **composition 口径全线切 ex-CC**（权威 `nc52_tcga_composition_excc.{csv,txt}`，25,015 对）：pooled −0.9%（bootstrap median −0.8% [−4.3,+2.5]）、LIHC **+44.1%** [+29.9,+60.0]、KIRC +19.7%、ρ=0.380（n=9,709）、|Δz| 1.305（P=2.6e-135）/1.216（P=4.7e-68）。**MS 曾混用新旧口径**（Discussion 用新 +44% 而 Results/Discussion pooled 仍写旧 −1.3%）——已统一为 −0.9%。
4. **Table 18 + Note 9 severity**：LIHC G1–G4 78.2/76.8/77.9/72.6 → **78.8/75.8/77.6/72.3**（ex-CC `nc52_tcga_excc_severity.csv`），k_f JT P 6.9e-15 → 8.4e-12；BRCA/LUAD 不变；表注加 ex-CC 与文件名。
5. **LIHC Edmondson 样本量勘误**：旧文「288 tumors」实为陈旧快照；缓存 cBioPortal 拉取 372 患者有 grade、289 ex-CC 肿瘤入分析 → MS Methods (372 patients with calls)、SI 5.3/5.12b 同步。
6. **Cox HR CI 上限四文件不一致**：CSV 1.3348→1.33，MS/SI/Guide/断言误写 1.34 → 统一 **1.08 [0.88, 1.33]**（5 处）。
7. **Note 8 CC 句框架过时**：「Excluding … leaves the null unchanged」（CC 排除=敏感性）→ ex-CC 默认口径（NN/TT 1.11 [0.94, 1.30]；k_n 1.34 [1.02, 1.89]）。
8. **SI Note 16 目录条与正文标题不一致**（Independent Validation vs Sanity Check）→ 目录改 Sanity Check。
9. **MS 方法比较句指针错挂**（Supplementary Note 9 无此内容）→ 改指 **Supplementary Methods 5.5**，并在 5.5 补 entry-cluster CI 段（四条相关 [CI] 全排除 0、P<1e-145 口径退役声明、分解 +0.43~+0.72/+0.69~+0.81/partial +0.11~+0.54）——SI 此前完全缺该内容。
10. **Reproducibility Guide v52 化**：新增 **Section 5.13 nc52 Analyses**（a–k 11 条目：ex-CC 主链、R Cox、composition、adjmodel 置换、mapping/kn_floor、deconv 可行性、GTEx、脑 donor bootstrap+组合对照、质量代理、候选效应量、统计重采样）；5.10c/5.11f/5.11i 标 superseded 指针；7.70 CI 全部换 two-stage [6.38, 9.82]（6 处）+ ω_cal 一位有效数字；样本量 3,535、比值域 1.11–2.46、LIHC grade 39/134/105/11；输出清单 nc52 化。
11. **SI/CL 标题 'separating' 残留** → 'decomposing'（SI 扉页、CL 正文、si_verify/C3 断言同步）。
12. **MAIN 词数 5,008 超限**（XV8 口径）→ 五处零信息损失压缩 −10 词 → **4,998/5,000**。

## 二、断言同步清单（#19）

- **99_build**：13 项 v52 改写（N58/N58b/N65b/N62/N83/N86/N87/N89/N33/N80/C3 + 前序 N16 等），终 221/221。
- **_nc49_ms_verify**：15 项（摘要 3,535/1.11–2.46/新校准句、CC 比值表 LIHC 1.11、mapping 1.11[0.94,1.30]/1.29[1.09,1.53]、G 勘误句、GTEx 分析句、高纯度新措辞、Kang (0 of 30; k_f likewise)、Cox ex-CC 句、Fig 2e DeLong CI 等）。判断性改锚 2 项：batch/center 句 v52 已删→改锚 Limitations (iii)「limited to bulk resolution」；Kang-brain size 句已删→改锚摘要「specificity decays with group size」+ SI Note 10。
- **_nc49_si_verify**：6 项（Table 5 表注 mapping 句、Table 11 ex-CC 全行、k_n 均值比 2.55[2.09,3.31]/1.34[1.02,1.89]、Cox M1 1.08[0.88,1.33]、Cox 表注 ex-CC+cox.zph、Table 18 LIHC 行+JT 8.4e-12、SI 标题）。
- **_nc49_cl_guide_verify**：2 项（Guide 3,535、checklist 3,535/1.11–2.46）。
- **XV8**：H1 'decomposing'、MAIN 描述 v52、5.x 指针 19→20、mig 表 3 项更新 + 新增 10 项 v52 锚点（two-stage CI、组合对照 3.66、R coxph、GTEx、ex-CC severity、entry-cluster、34,828、Guide 5.13、3,535）。

## 三、教训（沉淀）

- **表格不在 docx 里**：SI 全部表格+表注在 xlsx（P6 断言），sn fulltext 锚点必须取 docx 散文；表格值锚点走 cellfull/capfull。
- **xlsx 渲染值才是 ground truth**：f'{x:.2f}' 的浮点舍入（1.3348→1.33、1.815→1.81）必须先查表再写断言，勿手算。
- **verify 脚本与生成器一样混用字面 \uXXXX 与真 unicode**——Edit 前按字节确认（`b.count(b'\\u2013')`）。
- **MultiEdit 原子失败**：任一 old_string 失配整批不落；报错串即失配串，先 grep 实文再重跑。
- MS Methods 不计入 MAIN 词数（XV8 仅 Intro+Results+Discussion），方法段勘误无词数代价。

## 四、剩余事项（#20）

新 release（nc49/nc50/nc52 全量）+ 新 Zenodo version DOI + Code availability version DOI 更新 + Zenodo "Genome Biology" 元数据修正 + CI（含 3.14 runner）验证。
