# v49.12 C4: LIHC CC sensitivity - NN/TT ratio excluding the 32 CC (cell-line) samples
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
B = 1000
rng = np.random.default_rng(42)

lihc = pairs[pairs.cancer == "TCGA-LIHC"].copy()
# CC samples: barcode positions 14-15 (0-indexed 13:15)
def is_cc(s):
    s = str(s)
    return len(s) >= 8 and s[5:7] == "CC"

all_samples = sorted(set(lihc.sample_a) | set(lihc.sample_b))
cc_samples = [s for s in all_samples if is_cc(s)]
print("LIHC samples:", len(all_samples), "| CC samples:", len(cc_samples))

kept = lihc[~lihc.sample_a.map(is_cc) & ~lihc.sample_b.map(is_cc)].copy()
tt = kept[kept.pair_type == "TT"]
nn = kept[kept.pair_type == "NN"]
print("pairs full: TT=%d NN=%d | excl-CC: TT=%d NN=%d" % (
    (lihc.pair_type=="TT").sum(), (lihc.pair_type=="NN").sum(), len(tt), len(nn)))

om_nn = nn.omega.mean(); om_tt = tt.omega.mean()
kn_tt = tt.kn.mean(); kn_nn = nn.kn.mean()
print("excl-CC point: NN/TT omega = %.3f | TT/NN kn = %.3f" % (om_nn/om_tt, kn_tt/kn_nn))
print("full point   : NN/TT omega = %.3f" % (lihc[lihc.pair_type=="NN"].omega.mean()/lihc[lihc.pair_type=="TT"].omega.mean()))

# cluster bootstrap (mirror nc49_tcga_main boot_ratio)
def boot_ratio(df_tt, df_nn):
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}
    ia_t = df_tt.sample_a.map(t_idx).to_numpy()
    ib_t = df_tt.sample_b.map(t_idx).to_numpy()
    ia_n = df_nn.sample_a.map(n_idx).to_numpy()
    ib_n = df_nn.sample_b.map(n_idx).to_numpy()
    v_t = df_tt.omega.to_numpy(); v_n = df_nn.omega.to_numpy()
    kt_t = df_tt.kn.to_numpy(); kt_n = df_nn.kn.to_numpy()
    ratios, knratios = [], []
    nT, nN = len(t_samples), len(n_samples)
    for _ in range(B):
        wt = rng.multinomial(nT, np.ones(nT)/nT) / nT
        wn = rng.multinomial(nN, np.ones(nN)/nN) / nN
        ww_t = wt[ia_t]*wt[ib_t]; ww_n = wn[ia_n]*wn[ib_n]
        tt_m = np.sum(v_t*ww_t)/np.sum(ww_t)
        nn_m = np.sum(v_n*ww_n)/np.sum(ww_n)
        ratios.append(nn_m/tt_m)
        ktt = np.sum(kt_t*ww_t)/np.sum(ww_t)
        knn = np.sum(kt_n*ww_n)/np.sum(ww_n)
        knratios.append(ktt/knn)
    return np.percentile(ratios,[2.5,97.5]), np.percentile(knratios,[2.5,97.5])

ci_om, ci_kn = boot_ratio(tt, nn)
print("excl-CC NN/TT omega 95%% CI: [%.2f, %.2f]" % tuple(ci_om))
print("excl-CC TT/NN kn 95%% CI: [%.2f, %.2f]" % tuple(ci_kn))
print("CI excludes 1:", ci_om[0] > 1)
