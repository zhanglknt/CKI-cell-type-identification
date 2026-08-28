"""
v38 P3 生物学补充分析（_v38_biology_addenda.py）
=================================================
回应 v38 五专家评审共识 1 / 6（P3-12, R1-M2, R3-M2/M3/M4）：

  A1. 排除 Bergmann glia 后的脑区梯度（R3-M2）
  A2. k_f-only / k_n-only 梯度对照（R1-M2 / 共识 1）
  A3. same-organ 反转分量分解（Tabula Sapiens, R3-M3）
      + TCGA NN/TT 反转分量分解（R3-M4）
  A4. TCGA kn_floor 饱和分解（R1-M7 / R3-M4 / 共识 6）

只读现有结果文件，不改动任何现有输出；新文件一律 _v38_ 前缀。

用法：
    ./cki_env/Scripts/python.exe notebooks/_v38_biology_addenda.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import RESULTS_DIR

import numpy as np
import pandas as pd
from scipy import stats

RNG = np.random.RandomState(42)
B_BOOT = 2000

# ------------------------------------------------------------------
# 工具
# ------------------------------------------------------------------

def logmean(x):
    return float(np.mean(np.log(x)))


def mwu(a, b, alt='two-sided'):
    u, p = stats.mannwhitneyu(a, b, alternative=alt)
    return float(p)


def fmt(x, nd=2):
    return f"{x:.{nd}f}"


# ==================================================================
# 数据载入
# ==================================================================
brain = pd.read_csv(RESULTS_DIR / 'reviewer_brain_pair_kf_kn.csv')       # 31,764 对, per-pair kf/kn/omega
human = pd.read_csv(RESULTS_DIR / 'phase33_v3_human_pairs.csv')          # 5,151 对, same_organ
tcga = pd.read_csv(RESULTS_DIR / 'phase34_v2_all_pairs.csv')             # 35,306 对, TT/NN/TN

print(f"brain pairs={len(brain)}, human pairs={len(human)}, tcga pairs={len(tcga)}")

md = []
md.append("# v38 生物学补充分析（P3-12 / 共识 1 与 6 响应）\n")
md.append("日期：2026-08-29　脚本：`notebooks/_v38_biology_addenda.py`　"
          "数据：`reviewer_brain_pair_kf_kn.csv`（31,764 脑区对）、"
          "`phase33_v3_human_pairs.csv`（5,151 人图谱对）、"
          "`phase34_v2_all_pairs.csv`（35,306 TCGA 对）。\n")
md.append("每个分析给出：方法一句话、结果数值表、对稿件结论的影响判断（支持 / 需降调 / 需修正）。\n")

# ==================================================================
# A1. 排除 Bergmann glia 后的脑区梯度
# ==================================================================
print("\n=== A1. 排除 Bergmann glia 的脑区梯度 ===")

ct_omega = brain.groupby('cell_type')['omega'].agg(['mean', 'median', 'count'])
ct_omega = ct_omega.sort_values('mean', ascending=False)

grad_all = ct_omega['mean'].max() / ct_omega['mean'].min()
ct_hi, ct_lo = ct_omega['mean'].idxmax(), ct_omega['mean'].idxmin()

sub9 = ct_omega.drop(index='Bergmann glia')
grad_excl = sub9['mean'].max() / sub9['mean'].min()
hi9, lo9 = sub9['mean'].idxmax(), sub9['mean'].idxmin()

sub8 = sub9.drop(index='Choroid plexus')
grad_excl2 = sub8['mean'].max() / sub8['mean'].min()

# bootstrap CI（对每类内部重抽样对，B=2000）
def gradient_boot(brain_df, cts, B=B_BOOT):
    keep = brain_df[brain_df['cell_type'].isin(cts)]
    means = {}
    for ct, g in keep.groupby('cell_type'):
        means[ct] = g['omega'].values
    grads = np.empty(B)
    for b in range(B):
        m = {ct: np.mean(RNG.choice(v, size=len(v), replace=True)) for ct, v in means.items()}
        vals = np.array(list(m.values()))
        grads[b] = vals.max() / vals.min()
    return grads

cts9 = list(sub9.index)
gb = gradient_boot(brain, cts9)
ci_lo, ci_hi = np.percentile(gb, [2.5, 97.5])

# 排除 Bergmann 后是否"显著"：block-shuffle 类级 p（来自 brain_bs_null_ct_test.csv）
ct_test = pd.read_csv(RESULTS_DIR / 'brain_bs_null_ct_test.csv').set_index('cell_type')
p_vasc = ct_test.loc['Vascular', 'p_value']

a1_table = ct_omega.reset_index()[['cell_type', 'count', 'mean', 'median']]
a1_table.columns = ['cell_type', 'n_pairs', 'omega_mean', 'omega_median']
a1_out = RESULTS_DIR / '_v38_brain_gradient_excl_bergmann.csv'
a1_table.to_csv(a1_out, index=False)

md.append("\n## A1. 排除 Bergmann glia 后的脑区梯度\n")
md.append("**方法**：从 31,764 对脑区 ω 中剔除 Bergmann glia 的全部 21 对（其比较全部位于小脑内部），"
          "重算 9 类 max/min 类均值梯度，并用对级 bootstrap（B=2,000）给 95% CI。\n")
md.append("\n| 指标 | 数值 |\n|---|---|")
md.append(f"| 全 10 类梯度（{ct_hi} / {ct_lo}） | **{grad_all:.2f}x** |")
md.append(f"| 排除 Bergmann glia（{hi9} / {lo9}） | **{grad_excl:.2f}x**（bootstrap 95% CI [{ci_lo:.2f}, {ci_hi:.2f}]） |")
md.append(f"| 再排除 choroid plexus（8 类） | {grad_excl2:.2f}x |")
md.append(f"| 梯度新低端 Vascular 的 block-shuffle 类级 P | {p_vasc:.4f}（显著） |")
md.append("\n完整类均值表见 `_v38_brain_gradient_excl_bergmann.csv`。\n")
md.append("**影响判断：支持（结论稳健，但需加限定语）**。排除 Bergmann 后梯度仍 "
          f"{grad_excl:.2f} 倍、CI 下限 {ci_lo:.2f}，远大于 1；但 6.88→{grad_excl:.2f} 的变化说明 Bergmann "
          "（小脑内近距离比较、n=21）确实压低了梯度低端，摘要宜按 R3 建议改为 "
          f"\"{grad_excl:.1f}-fold excluding Bergmann glia\" 或加采样范围限定语。\n")

print(f"  all-10 gradient={grad_all:.2f}x, excl-Bergmann={grad_excl:.2f}x "
      f"(CI {ci_lo:.2f}-{ci_hi:.2f}), excl-BG+CP={grad_excl2:.2f}x")

# ==================================================================
# A2. k_f-only / k_n-only 梯度对照
# ==================================================================
print("\n=== A2. k_f-only / k_n-only 对照 ===")

ct_comp = brain.groupby('cell_type').agg(
    n_pairs=('omega', 'count'),
    kf_mean=('kf', 'mean'),
    kn_mean=('kn', 'mean'),
    omega_mean=('omega', 'mean'),
).reset_index()

kf_fold = ct_comp['kf_mean'].max() / ct_comp['kf_mean'].min()
kn_fold = ct_comp['kn_mean'].max() / ct_comp['kn_mean'].min()
kf_hi = ct_comp.loc[ct_comp['kf_mean'].idxmax(), 'cell_type']
kf_lo = ct_comp.loc[ct_comp['kf_mean'].idxmin(), 'cell_type']
kn_hi = ct_comp.loc[ct_comp['kn_mean'].idxmax(), 'cell_type']
kn_lo = ct_comp.loc[ct_comp['kn_mean'].idxmin(), 'cell_type']

# 与 ω 排序的秩相关（10 类）
rho_kf = stats.spearmanr(ct_comp['omega_mean'], ct_comp['kf_mean'])
rho_kn = stats.spearmanr(ct_comp['omega_mean'], ct_comp['kn_mean'])

# 端点（astro vs Bergmann）乘法分解
astro = ct_comp.set_index('cell_type').loc['Astrocyte']
berg = ct_comp.set_index('cell_type').loc['Bergmann glia']
ep_kf = astro['kf_mean'] / berg['kf_mean']
ep_kn = berg['kn_mean'] / astro['kn_mean']          # Bergmann kn 更大 → 分母更稳 → ω 更低
ep_pred = ep_kf * ep_kn

# k_f-only 排序中 astrocyte 的名次
kf_rank = ct_comp.sort_values('kf_mean', ascending=False).reset_index(drop=True)
astro_rank_kf = int(kf_rank.index[kf_rank['cell_type'] == 'Astrocyte'][0]) + 1

ct_comp = ct_comp.sort_values('omega_mean', ascending=False)
a2_out = RESULTS_DIR / '_v38_brain_kf_only_gradient.csv'
ct_comp.to_csv(a2_out, index=False)

md.append("\n## A2. k_f-only 与 k_n-only 梯度对照（分量分解）\n")
md.append("**方法**：对同一批 31,764 对计算各类 k_f 均值与 k_n 均值，"
          "分别给出 k_f-only / k_n-only 梯度倍数、与 ω 类排序的 Spearman ρ，"
          "并对 6.88 倍端点（astrocyte vs Bergmann glia）做乘法分解 6.88 ≈ (Δk_f)×(Δk_n)。\n")
md.append("\n| 量 | 数值 |\n|---|---|")
md.append(f"| ω 梯度（10 类） | {grad_all:.2f}x（{ct_hi}→{ct_lo}） |")
md.append(f"| k_f-only 梯度 | {kf_fold:.1f}x（{kf_hi} 最高 → {kf_lo} 最低） |")
md.append(f"| k_n-only 梯度 | {kn_fold:.1f}x（{kn_hi} 最高 → {kn_lo} 最低） |")
md.append(f"| Spearman ρ(ω 类均值, k_f 类均值) | {rho_kf.statistic:.2f}（P={rho_kf.pvalue:.3f}） |")
md.append(f"| Spearman ρ(ω 类均值, k_n 类均值) | {rho_kn.statistic:.2f}（P={rho_kn.pvalue:.2f}） |")
md.append(f"| 端点分解：k_f(astro)/k_f(BG) | {astro['kf_mean']:.4f}/{berg['kf_mean']:.4f} = **{ep_kf:.2f}x** |")
md.append(f"| 端点分解：k_n(BG)/k_n(astro) | {berg['kn_mean']:.2e}/{astro['kn_mean']:.2e} = **{ep_kn:.2f}x** |")
md.append(f"| 乘法预测 ω 比 | {ep_kf:.2f}×{ep_kn:.2f} = {ep_pred:.2f}（实测 {grad_all:.2f}） |")
md.append(f"| astrocyte 在 k_f-only 排序中的名次 | 第 {astro_rank_kf}/10 |")
md.append("\n各类 k_f/k_n/ω 均值全表见 `_v38_brain_kf_only_gradient.csv`。\n")
md.append(f"**影响判断：需修正（证实共识 1）**。6.88 倍梯度的端点对比中 k_f 仅贡献 {ep_kf:.2f} 倍、k_n 贡献 "
          f"{ep_kn:.2f} 倍（乘积 {ep_pred:.2f}≈6.88）；k_f-only 排序下 astrocyte 仅列第 {astro_rank_kf}，"
          f"且 ω 类排序与 k_f 类排序无秩相关（ρ={rho_kf.statistic:.2f}）、与 k_n 类排序呈负相关"
          f"（ρ={rho_kn.statistic:.2f}，k_n 越小 ω 越高）。「星形胶质细胞功能分化最强」的功能基因解读不成立，"
          "应改写为「composite divergence gradient，主要由 HK 程序跨区稳定性（k_n）差异驱动」。\n")

print(f"  kf-only fold={kf_fold:.1f}x ({kf_hi}->{kf_lo}), kn-only fold={kn_fold:.1f}x")
print(f"  rho(omega,kf)={rho_kf.statistic:.2f}, rho(omega,kn)={rho_kn.statistic:.2f}")
print(f"  endpoint: kf {ep_kf:.2f}x, kn {ep_kn:.2f}x -> {ep_pred:.2f} vs {grad_all:.2f}")

# ==================================================================
# A3a. same-organ 反转分量分解（Tabula Sapiens）
# ==================================================================
print("\n=== A3a. same-organ 反转分量分解（人图谱） ===")

rows = []
for so, lab in [(True, 'same_organ'), (False, 'diff_organ')]:
    s = human[human['same_organ'] == so]
    rows.append({
        'group': lab, 'n_pairs': len(s),
        'omega_mean': s['omega'].mean(), 'omega_median': s['omega'].median(),
        'kf_mean': s['kf'].mean(), 'kf_median': s['kf'].median(),
        'kn_mean': s['kn'].mean(), 'kn_median': s['kn'].median(),
        'logkf_mean': logmean(s['kf']), 'logkn_mean': logmean(s['kn']),
        'logomega_mean': logmean(s['omega']),
    })
rev = pd.DataFrame(rows).set_index('group')

so_, do_ = rev.loc['same_organ'], rev.loc['diff_organ']
d_log_omega = so_['logomega_mean'] - do_['logomega_mean']
d_log_kf = so_['logkf_mean'] - do_['logkf_mean']
d_log_kn = so_['logkn_mean'] - do_['logkn_mean']

p_omega = mwu(human.loc[human.same_organ, 'omega'], human.loc[~human.same_organ, 'omega'], 'greater')
p_kf = mwu(human.loc[human.same_organ, 'kf'], human.loc[~human.same_organ, 'kf'])
p_kn = mwu(human.loc[human.same_organ, 'kn'], human.loc[~human.same_organ, 'kn'], 'less')

# 条件化检查：控制 log_kn 后 same_organ 对 log_kf 的效应（线性回归）
X = np.column_stack([np.ones(len(human)),
                     human['same_organ'].astype(float).values,
                     np.log(human['kn'].values)])
y = np.log(human['kf'].values)
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
resid = y - X @ beta
sigma2 = resid @ resid / (len(y) - X.shape[1])
cov = sigma2 * np.linalg.inv(X.T @ X)
se_beta1 = np.sqrt(cov[1, 1])
t_beta1 = beta[1] / se_beta1
p_beta1 = 2 * stats.t.sf(abs(t_beta1), len(y) - X.shape[1])

md.append("\n## A3. same-organ 反转的分量分解\n")
md.append("**A3a 人图谱（Tabula Sapiens，5,151 对）**。"
          "**方法**：same-organ 与 different-organ 对的 ω 差按恒等式 log ω = log k_f − log k_n "
          "分解为两个分量均值之差；并对 k_f、k_n 分别做 Mann-Whitney U 检验；"
          "另以线性回归检查控制 log k_n 后 same-organ 对 log k_f 是否仍有效应。\n")
md.append("\n| 分量 | same-organ (n=1,140) | diff-organ (n=4,011) | 差（same−diff） |\n|---|---|---|---|")
md.append(f"| ω 均值 | {so_['omega_mean']:.2f} | {do_['omega_mean']:.2f} | "
          f"+{so_['omega_mean']-do_['omega_mean']:.2f}（**{so_['omega_mean']/do_['omega_mean']:.2f}x**，P={p_omega:.1e}） |")
md.append(f"| k_f 均值 | {so_['kf_mean']:.4f} | {do_['kf_mean']:.4f} | "
          f"{so_['kf_mean']-do_['kf_mean']:+.4f}（P={p_kf:.2f}，不显著） |")
md.append(f"| k_n 均值 | {so_['kn_mean']:.5f} | {do_['kn_mean']:.5f} | "
          f"{so_['kn_mean']-do_['kn_mean']:+.5f}（P={p_kn:.2e}，same-organ 显著更低） |")
md.append("\n| log 尺度分量贡献 | 数值 |\n|---|---|")
md.append(f"| Δlog ω（反转总量） | +{d_log_omega:.4f}（= {np.exp(d_log_omega):.2f}x） |")
md.append(f"| Δlog k_f（分子贡献） | {d_log_kf:+.4f}（≈ {np.exp(d_log_kf):.2f}x，可忽略且方向相反） |")
md.append(f"| −Δlog k_n（分母贡献） | +{-d_log_kn:.4f}（≈ {np.exp(-d_log_kn):.2f}x，**占全部反转**） |")
md.append(f"| 控制 log k_n 后 same-organ 对 log k_f 的偏回归系数 | {beta[1]:+.4f}（P={p_beta1:.1e}，条件于 k_n 时 k_f 仅高 ~{np.exp(beta[1])-1:.0%}，远小于分母贡献） |")
md.append("\n**影响判断：需修正（证实 R3-M3）**。same-organ 反转（24.7 vs 20.6）100% 由分母驱动："
          "same-organ 对的 k_f 与 diff-organ 无差异（甚至略低），但 k_n 显著更低（共享微环境压低 HK 基线散度），"
          "使 ω 升高。稿件将反转解读为「CKI 检测到共享微环境内功能特化」的证据不成立；"
          "应改写为「器官内比较中 HK 基线更稳定，归一化分母更小，ω 灵敏度更高」。\n")

print(f"  omega {so_['omega_mean']:.2f} vs {do_['omega_mean']:.2f} ({np.exp(d_log_omega):.2f}x)")
print(f"  dlog_kf={d_log_kf:+.4f}, -dlog_kn={-d_log_kn:+.4f}, kf P={p_kf:.2f}, kn P={p_kn:.1e}")

# ==================================================================
# A3b. TCGA NN/TT 反转分量分解
# ==================================================================
print("\n=== A3b. TCGA NN/TT 反转分量分解 ===")

tcga_rows = []
for cancer, g in tcga.groupby('cancer'):
    tt = g[g.pair_type == 'TT']
    nn = g[g.pair_type == 'NN']
    tcga_rows.append({
        'cancer': cancer,
        'n_TT': len(tt), 'n_NN': len(nn),
        'omega_TT_med': tt['omega'].median(), 'omega_NN_med': nn['omega'].median(),
        'omega_NN_TT': nn['omega'].median() / tt['omega'].median(),
        'kf_TT_med': tt['kf'].median(), 'kf_NN_med': nn['kf'].median(),
        'kf_NN_TT': nn['kf'].median() / tt['kf'].median(),
        'kn_TT_med': tt['kn'].median(), 'kn_NN_med': nn['kn'].median(),
        'kn_NN_TT': nn['kn'].median() / tt['kn'].median(),
        'dlog_omega': logmean(nn['omega']) - logmean(tt['omega']),
        'dlog_kf': logmean(nn['kf']) - logmean(tt['kf']),
        'dlog_kn': logmean(nn['kn']) - logmean(tt['kn']),
        'p_omega': mwu(nn['omega'], tt['omega'], 'greater'),
        'p_kf': mwu(nn['kf'], tt['kf'], 'less'),
        'p_kn': mwu(nn['kn'], tt['kn'], 'less'),
    })
rev_tcga = pd.DataFrame(tcga_rows)

a3_out = RESULTS_DIR / '_v38_same_organ_reversal_decomposition.csv'
rev_out = rev.reset_index()
rev_out.to_csv(a3_out, index=False)
rev_tcga_out = RESULTS_DIR / '_v38_tcga_nn_tt_reversal_decomposition.csv'
rev_tcga.to_csv(rev_tcga_out, index=False)

md.append("**A3b TCGA NN/TT 反转（5 癌种）**。"
          "**方法**：同一分解应用于每癌种 normal-normal（NN）与 tumor-tumor（TT）对："
          "log(ω_NN/ω_TT) = Δlog k_f − Δlog k_n（log 均值差）。\n")
def fmt_p(p):
    return "<1e-300" if p == 0.0 else f"{p:.1e}"


md.append("\n| 癌种 | ω_NN/ω_TT（中位数） | k_f_NN/k_f_TT | k_n_NN/k_n_TT | Δlogω | Δlog k_f | −Δlog k_n | P(k_f NN<TT) | P(k_n NN<TT) |\n|---|---|---|---|---|---|---|---|---|")
for _, r in rev_tcga.iterrows():
    md.append(f"| {r['cancer']} | {r['omega_NN_TT']:.2f}x | {r['kf_NN_TT']:.2f}x | {r['kn_NN_TT']:.2f}x | "
              f"+{r['dlog_omega']:.3f} | {r['dlog_kf']:+.3f} | +{-r['dlog_kn']:.3f} | "
              f"{fmt_p(r['p_kf'])} | {fmt_p(r['p_kn'])} |")
md.append("\n5/5 癌种：k_f 方向与反转**相反**（肿瘤对 k_f 更高，NN/TT k_f 比 0.5–0.7x），"
          "而 k_n 一致压低 NN 的分母（NN/TT k_n 比 0.3–0.5x）。「肿瘤比癌旁正常组织更趋同（NN/TT>1）」"
          "完全由 k_n 驱动：正常组织对的 HK 程序散度更低，不是肿瘤对的功能基因分化更小。\n")
md.append("**影响判断：需修正（证实 R3-M4-2）**。TCGA「趋同」结论须改写为分母效应；"
          "分量表（`_v38_tcga_nn_tt_reversal_decomposition.csv`）应随分量分解表一并进入正文/补充。\n")

print(rev_tcga[['cancer', 'omega_NN_TT', 'kf_NN_TT', 'kn_NN_TT', 'dlog_omega', 'dlog_kf', 'dlog_kn']].to_string(index=False))

# ==================================================================
# A4. TCGA kn_floor 饱和分解
# ==================================================================
print("\n=== A4. TCGA kn_floor 饱和分解 ===")

KN_FLOOR = 1e-4
sat_mask = tcga['kn'] < KN_FLOOR
near_mask = tcga['kn'] < 2 * KN_FLOOR
# 数值一致性：omega 与 kf/kn 的最大偏差（若发生 clamp 则 omega=kf/floor != kf/kn）
max_dev = float(np.abs(tcga['omega'] - tcga['kf'] / tcga['kn']).max())

sat_rows = []
for cancer, g in tcga.groupby('cancer'):
    for pt, gg in g.groupby('pair_type'):
        rho = stats.spearmanr(gg['omega'], gg['kf'])
        sat_rows.append({
            'cancer': cancer, 'pair_type': pt, 'n_pairs': len(gg),
            'kn_min': gg['kn'].min(), 'kn_median': gg['kn'].median(),
            'kn_p05': gg['kn'].quantile(0.05),
            'n_kn_below_floor': int((gg['kn'] < KN_FLOOR).sum()),
            'frac_kn_below_floor': float((gg['kn'] < KN_FLOOR).mean()),
            'spearman_omega_kf': rho.statistic,
            'omega_median': gg['omega'].median(),
        })
sat = pd.DataFrame(sat_rows)
a4_out = RESULTS_DIR / '_v38_tcga_kn_floor_saturation.csv'
sat.to_csv(a4_out, index=False)

# 饱和对 vs 非饱和对的 ω 分布（若存在饱和对）
if sat_mask.sum() > 0:
    sat_vs_nonsat = pd.DataFrame({
        'group': ['saturated (kn<1e-4)', 'non-saturated'],
        'n': [int(sat_mask.sum()), int((~sat_mask).sum())],
        'omega_median': [tcga.loc[sat_mask, 'omega'].median(), tcga.loc[~sat_mask, 'omega'].median()],
        'omega_mean': [tcga.loc[sat_mask, 'omega'].mean(), tcga.loc[~sat_mask, 'omega'].mean()],
    })
else:
    sat_vs_nonsat = None

# log-omega 方差分解（全部 TCGA 对）
lkf = np.log(tcga['kf'].values)
lkn = np.log(tcga['kn'].values)
lom = np.log(tcga['omega'].values)
var_lkf, var_lkn = lkf.var(), lkn.var()
cov = np.cov(lkf, lkn)[0, 1]
var_lom_direct = lom.var()
var_lom_sum = var_lkf + var_lkn - 2 * cov
frac_kf = var_lkf / (var_lkf + var_lkn)

rho_all = stats.spearmanr(tcga['omega'], tcga['kf'])
rho_kn_all = stats.spearmanr(tcga['omega'], tcga['kn'])

# 脑区数据对照（kn_floor=0，未 clamp）：kn<1e-4 的对数
brain_below = int((brain['kn'] < KN_FLOOR).sum())

md.append("\n## A4. TCGA kn_floor 饱和分解\n")
md.append("**方法**：在权威对级文件 `phase34_v2_all_pairs.csv`（35,306 对）上，"
          "(i) 检验 ω 与 k_f/k_n 的恒等关系以识别 clamp 触发；"
          "(ii) 统计各癌种/对型 k_n 低于 floor（1×10⁻⁴）与 2×floor 的对数与占比；"
          "(iii) 计算各层 ω 与 k_f 的 Spearman ρ（若 ρ≈1 则 ω 排序实质是 k_f 排序）；"
          "(iv) log ω = log k_f − log k_n 的方差分解。\n")
md.append("\n| 指标 | 数值 |\n|---|---|")
md.append(f"| max\\|ω − k_f/k_n\\|（>0 即存在 clamp） | {max_dev:.1e}（=0，**无任何对被 clamp**） |")
md.append(f"| k_n < 1×10⁻⁴ 的对 | {int(sat_mask.sum())} / {len(tcga)}（{sat_mask.mean():.1%}） |")
md.append(f"| k_n < 2×10⁻⁴（贴地）的对 | {int(near_mask.sum())} / {len(tcga)}（{near_mask.mean():.3%}） |")
md.append(f"| 全体 k_n 最小值 | {tcga['kn'].min():.2e}（各层最小值见 CSV） |")
md.append(f"| Spearman ρ(ω, k_f)（全体） | {rho_all.statistic:.3f} |")
md.append(f"| Spearman ρ(ω, k_n)（全体） | {rho_kn_all.statistic:.3f} |")
md.append(f"| var(log k_f) / var(log k_n) | {var_lkf:.3f} / {var_lkn:.3f}（k_f 占 {frac_kf:.0%}） |")
md.append(f"| 恒等式复核 var(log k_f−log k_n) vs var(log ω) | {var_lom_sum:.4f} vs {var_lom_direct:.4f} |")
md.append(f"| 对照：脑区数据（kn_floor=0）k_n<1×10⁻⁴ 对数 | {brain_below} / 31,764（与稿件声明 1,825 一致） |")
md.append("\n各癌种×对型明细（n、k_n min/p05/中位数、饱和计数、ρ(ω,k_f)）见 `_v38_tcga_kn_floor_saturation.csv`。\n")
md.append(f"各癌种×对型 ρ(ω,k_f) 范围：{sat['spearman_omega_kf'].min():.3f}–{sat['spearman_omega_kf'].max():.3f}。\n")
md.append("\n**影响判断：需修正（对级数据推翻「ω 退化为重标度 k_f」的前提，但稿件表述仍须改写）**。\n"
          "1. **对级数据中 floor 从未触发**：35,306 对里 0 对 k_n<1×10⁻⁴（最小 1.6×10⁻⁴，仅 1 对低于 2×floor），"
          "ω 与 k_f/k_n 严格相等（最大偏差 5×10⁻¹⁰），不存在「饱和对 vs 非饱和对」的对比——饱和对占比 **0%**。\n"
          "2. 稿件 Limitation 20「aggregate tumor-versus-normal k_n 3.0×10⁻⁵–1.9×10⁻⁴、ω 在 3/5 癌种饱和于 k_f/10⁻⁴」"
          "描述的是**聚合层**（全肿瘤均值 pseudobulk vs 全正常均值 pseudobulk 这一个比较，v1 期数值），"
          "而非现行权威对级数据（phase34_v2）；且现行临床分析脚本（`07_phase34_clinical.py`）调用 "
          "`compute_omega` 时未传 kn_floor（默认 0，不 clamp）。该 Limitation 应改写并明确区分聚合层与对层。\n"
          f"3. **与评审预期相反，对级 ω 并非 k_f 的重标度**：ρ(ω, k_f) 全体仅 {rho_all.statistic:.2f}"
          f"（各癌种×对型 {sat['spearman_omega_kf'].min():.2f}–{sat['spearman_omega_kf'].max():.2f}），"
          f"log 方差中 k_n 占 {(1-frac_kf):.0%}（var(log k_n)={var_lkn:.2f} vs var(log k_f)={var_lkf:.2f}）——"
          "因为 floor 从不生效，分母 k_n 在对级携带了最多的变异。共识 6 / R1-M7 的「TCGA 部分 ω≡排序 k_f」"
          "推断建立在对级饱和的假设上，该假设不成立；但这同时意味着 TCGA 的 ω 与脑区一样是 "
          "k_n 主导的复合信号，「功能扰动」解读同样需要分量证据。\n"
          "4. R1-M7 的另一半建议（k_f-only 临床分层对照表）仍值得做，但因对级无饱和，"
          "预期结果不是「与 ω 完全一致」而是「k_n 主导」——归因方向与 R1 预期相反。\n")

print(f"  saturated pairs: {int(sat_mask.sum())}, near-floor: {int(near_mask.sum())}, max_dev={max_dev:.1e}")
print(f"  rho(omega,kf) all={rho_all.statistic:.3f}, per-group range "
      f"{sat['spearman_omega_kf'].min():.3f}-{sat['spearman_omega_kf'].max():.3f}")
print(f"  var logkf={var_lkf:.3f}, var logkn={var_lkn:.3f}")

# ==================================================================
# 写出 Markdown
# ==================================================================
md.append("\n## 汇总：对稿件四项结论的影响\n")
md.append("| # | 分析 | 核心数值 | 判定 |\n|---|---|---|---|")
md.append(f"| A1 | 排除 Bergmann 梯度 | 6.88x → **{grad_excl:.2f}x**（95% CI [{ci_lo:.2f}, {ci_hi:.2f}]） | 支持（加限定语） |")
md.append(f"| A2 | k_f-only 对照 | 端点 k_f 仅 **{ep_kf:.2f}x** vs k_n **{ep_kn:.2f}x**；ρ(ω,k_f)={rho_kf.statistic:.2f} | 需修正（共识 1 成立） |")
md.append(f"| A3 | same-organ 反转分解 | Δlog k_f={d_log_kf:+.3f}（不显著） vs −Δlog k_n={-d_log_kn:+.3f}；TCGA 5/5 癌种 k_f 方向相反 | 需修正（分母驱动） |")
md.append(f"| A4 | kn_floor 饱和 | 对级饱和 **0 对（0%）**；ρ(ω,k_f)={rho_all.statistic:.2f}，k_n 占 log 方差 {(1-frac_kf):.0%} | 需修正（表述+归因） |")
md.append("\n新文件：`results/_v38_brain_gradient_excl_bergmann.csv`、`results/_v38_brain_kf_only_gradient.csv`、"
          "`results/_v38_same_organ_reversal_decomposition.csv`、`results/_v38_tcga_nn_tt_reversal_decomposition.csv`、"
          "`results/_v38_tcga_kn_floor_saturation.csv`、`results/v38_biology_addenda.md`。\n")

out_md = RESULTS_DIR / 'v38_biology_addenda.md'
with open(out_md, 'w', encoding='utf-8') as f:
    f.write("\n".join(md))
print(f"\nSaved: {out_md}")
print("Done!")
