# Kang batch1 技术重复 pilot — GO/NO-GO 审计（NC v49 对策 C）

日期：2026-09-18　执行：c-drift
脚本：`notebooks/nc49_pilot_kang_techrep.py`
数据：`data/kang_ifnb/_raw/`（自 GSE96583_RAW.tar 解包 GSM2560245/46/47，三 lane MatrixMarket）
逐对结果：`results/nc49_pilot_kang_techrep.csv`（30 对，每对含 B=200 的 n-matched null 摘要）

## 判定：**GO**

## 设计

- batch1（8 供体全部未刺激）：lane A={1079,1154,1249,1598}，lane B={1043,1085,1493,1511}，lane C=全部 8 供体 → 每供体恰好横跨 2 个 lane。同供体同条件跨 lane 对 = 技术重复，ground truth = 无功能差异。
- singlet、注释完整、每组 ≥50 细胞：6 个细胞类型 30 对（B 5、CD14 7、CD4 8、CD8 4、FCGR3A 1、NK 5；Dendritic 无合格组）。
- 指标（伪批量：sum→normalize 1e4→log1p；HRT Atlas HK 1099 基因；per-pair top-200 |Δμ| hybrid）：k_n、k_f、ω（kn_floor=0）、raw JS、cosine。
- **n-matched null**（每对 B=200）：合并两 lane 细胞、打乱、按观测组规模 (na, nb) 划分——n 精确匹配、同供体同类型、无 lane 结构。校准比 = 观测/null 中位；FPR = 观测超过自身 null p95 的对子比例。
- 统计注意：首轮用 min(na,nb)×2 的 null 是错误的（obs 组一侧更大 → 所有指标 cal<1 的 n 伪影），已修正为按 (na,nb) 划分；修正后结果如下。

## 关键数字（30 对，B=200/对）

| 指标 | 观测中位 | null 中位 | 校准比中位 [IQR] | FPR（超自身 null p95） |
|---|---|---|---|---|
| k_n | 0.0139 | 0.0141 | 0.993 [0.949, 1.03] | 1/30 (3.3%) |
| k_f | 0.110 | 0.119 | 0.936 [0.908, 0.977] | 0/30 (0%) |
| **ω** | 8.48 | 8.84 | **0.963 [0.918, 0.998]** | **0/30 (0%)** |
| raw JS | 0.00511 | 0.00509 | 1.019 [0.991, 1.08] | **11/30 (36.7%)** |
| cosine | 0.0515 | 0.0511 | 1.006 [0.993, 1.03] | **7/30 (23.3%)** |

- 每 CT 的 ω 校准比中位 0.90–1.03，全部 FPR=0；raw JS 校准比 0.99–1.05 但在 4/6 类有超 p95 误报（CD4、CD8、FCGR3A、CD14）。
- 判据核对：ω 校准中位 0.963 ≤ 1.5（✓），且 FPR 0% 显著低于 raw JS 36.7% / cosine 23.3%（✓）→ **GO**。

## 解读

- 漂移幅度本身小（raw 指标 cal ≈ 1.02–1.08），但方向系统性向上：raw JS 在 37% 的纯技术重复对上越过自身 null 的 95 分位——真实数据中「漂移被误报为分歧」成立。
- ω 的 FPR 恰为 0%、校准比 IQR 上界 <1：k_n 分母同步吸收了 lane 级基因偏倚，与模拟结论（FPR 0.00 vs 0.55–0.58）在真实数据上定性一致（幅度温和）。
- ω 的额外优点在 n-matched 设计下显式可见：ω 对组规模不敏感（ratio 结构自消），而 raw 指标的 null 必须严格 n 匹配才可解释。

## 限制

- 30 对（lane C 共享、donor 嵌套于 lane-pair）：FPR 点估计区间宽（ω 0% 的 95% CI ≈ 0–12%；raw JS 36.7% ≈ 21–55%）；主结论靠 brain 阶梯（2,161 对）加固。
- marker Jaccard / Spearman 未跑（按 lead 指示随主分析一起做）。

## 环境记录

- Python：`C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（3.13.14；系统 Python312 h5py DLL 损坏）。
- 完整运行日志：`results/audit/_nc49_pilot_kang_stdout.log`；汇总：`results/audit/_nc49_pilot_kang_summary.txt`。

**结论：GO → 进入 brain 四层漂移阶梯主分析。**
