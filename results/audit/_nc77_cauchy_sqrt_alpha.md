# nc77 — Cauchy–Schwarz 界漏掉 √α 的裁定与修正

## 提问
Supplementary Note 20 的 Cauchy–Schwarz 公式是否漏掉 √α？稿件漏了，代码是否也漏了？

## 裁定：是，稿件与代码都漏了（同一错误的两个推论）

### 推导（按稿件自身定义）

Lemma 1b 末句规定测度分配：**E_b 在 HK panel 上评估，E_f 与 C_bf 在 pair-specific top-200 panel 上评估**（各自面板）。
C2 定义 **α = E_b(top-200)/E_b(HK)**，即 top-200 选择对背景能量的膨胀因子。

Cauchy–Schwarz 必须在**同一内积**（同一 p、同一基因集）下施行。C_bf = Cov_p(β, φ) 与 E_f = Var_p(φ) 都在 top-200 内积下，因此：

```
|C_bf| ≤ √[ Var_200(β) · Var_200(φ) ] = √[ (α E_b) · E_f ] = √α · √(E_b E_f)
```

而 estimand 的交叉项偏差为 2C_bf/E_b（分母的 E_b 来自 k_n，HK 测度），故

```
|2 C_bf / E_b| ≤ 2 √(α E_f / E_b)      ← 正确界（含 √α）
```

稿件写的是 |2C_bf| ≤ 2√(E_b E_f)、偏差界 2√(E_f/E_b) —— **混用了两个测度**，低估 √α 倍
（α 中位 14 脑 / 8.5 TS → √α ≈ 3.7 / 2.9；IFN-β 数据集 α 8.1–18.9 → √α ≈ 2.8–4.3）。

注意：C_bf 不可能改到 HK 测度上定义——A1 规定 φ = 0 on HK panel，HK 上 C_bf ≡ 0。
所以测度不一致是内在的，√α 不可回避。

### 第二个推论（同样漏 α，不是 √α）

Proposition 4(a)：ω(λ) = α + (λ²E_f + 2λC_bf)/E_b，∂ω/∂λ = 2(λE_f + C_bf)/E_b。
最坏 C_bf = −√(α E_b E_f)，故保证 ∂ω/∂λ > 0 的充分条件为

```
λ E_f > √(α E_b E_f)  ⟺  λ² E_f > α E_b      ← 正确条件
```

稿件原写 **λ²E_f > E_b**，漏 α。

### 盲审为何没抓到
`results/audit/_nc75_review_stat.md` 第 20、22 条曾核验"λ²E_f > E_b 精确无误"与"|2C_bf|/E_b ≤ 2√(E_f/E_b) 自洽"——
那是**在稿件内部把 E_b 与 C_bf 当成同测度**判的，没有对照 Lemma 1b 的测度分配句，因此漏检。
本轮由用户直接指出。

## 修正清单

### 稿件（notebooks/68_gen_supplementary_nc.py）
1. **C5 段**：|2C_bf| ≤ 2√(E_b E_f) → 2√(αE_b E_f)；偏差界 → 2√(αE_f/E_b)；新增测度澄清
   （"e_b 在 HK panel 上测量，而 C_bf/E_f 在 pair-specific panel 上，故 Cauchy–Schwarz 在 top-200 内积下施行"）
   并明写 **"The √α factor is not optional"** + √α ≈ 2.9/3.7 的量级。
2. **Proposition 3**：无 C5 的偏差界 → 2√(αE_f/E_b)（附 top-200 内积说明）。
3. **Proposition 4(a)**：保证条件 λ²E_f > E_b → **λ²E_f > αE_b**。
4. **Note 20 收束段**：statements invoking C5 携带的最坏偏差 → 2√(αE_f/E_b)。
5. **Supplementary Note 8（IFN-β A1 定量）**：改写为 √α 版本并换新数字（下表），
   并保留一句"not 2√(E_f/E_b)"的显式澄清，避免读者按旧式复算。

### 代码（notebooks/nc76_ifnb_theory_quant.py）
- `bound = 2 * np.sqrt(Ef / E_b)` → `2 * np.sqrt(alpha * Ef / E_b)`；
- 输出列名 `bound_2sqrtEfEb` → `bound_2sqrt_aEf_Eb`；docstring 补推导与 nc77 说明。
- 重跑（10 s）。

## 数字变化（results/nc76_ifnb_theory_quant.{csv,txt}）

| cell type | α | bias | 旧界 2√(E_f/E_b) | 新界 2√(αE_f/E_b) | 旧判定 | 新判定 |
|---|---|---|---|---|---|---|
| B cells | 9.19 | −9.15 | 10.05 | 30.46 | in | in |
| CD14+ Mono | 12.03 | −78.02 | 19.43 | 67.39 | **out** | **out** |
| CD4 T | 18.88 | −2.10 | 7.88 | 34.22 | in | in |
| CD8 T | 10.39 | −1.48 | 7.55 | 24.34 | in | in |
| FCGR3A+ Mono | 9.34 | −27.97 | 13.47 | 41.17 | **out** | in |
| NK | 8.10 | −2.49 | 7.77 | 22.11 | in | in |

**结论定性不变，定量叙述改**：由"4/6 在界内、两类单核破界"改为"**5/6 在界内，仅 CD14+ 破界（−78.0 vs 67.4，φ/E_b = 4.76）**"。
CD14+ 恰是 anchor 受累最重者（φ/E_b = 4.76、deflation 83%），与"界只覆盖分子交叉项 C_bf、
A1 分母泄漏无界，故 k_n 升高才是操作性警报"的论断方向一致——修正后反而更聚焦。

## 未受影响
- MS（generate_manuscript_nc.py）只引用 C5 下的 estimand ω = α + E_f/E_b + ε，**不含该界**，无需改（已核验 'Cauchy' 不在 MS）。
- Supplementary Fig. 2 legend 处 C_bf = 0 是 grid 构造，无关。
- α 的估计、estimand、bias、deflation、所有其他统计量不变——仅"界"与"保证条件"两处缩放。

## 验证
build 226/226（MS 129 / SI 120 / CL+Guide 44 / XV8 64 全绿）；fresh-DOCX 核验新界 4 处、新数字 6 个全部在版；
SI 中旧式 2√(E_f/E_b) 仅剩 2 处且均为"not ..."的显式澄清；根目录包同步 + zip 22 条目。
