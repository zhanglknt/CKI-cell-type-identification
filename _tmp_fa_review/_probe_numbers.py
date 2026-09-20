import pandas as pd, json
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
pan = pd.read_csv(ROOT + "/results/nc49_tcga_pancancer.csv")
print("=== pancancer ===")
print(pan.to_string(index=False))
luad = pd.read_csv(ROOT + "/results/nc49_tcga_luad_mutation.csv")
print("\n=== luad mutation ===")
print(luad.to_string(index=False))
cox = pd.read_csv(ROOT + "/results/nc49_pilot_lihc_cox.csv")
print("\n=== cox ===")
print(cox.to_string(index=False))
# check CIs excluding 1
pan["CI_excl_1"] = (pan.NN_TT_ratio_CI95_lower > 1)
pan["kn_CI_excl_1"] = (pan.kn_TT_NN_mean_ratio_CI95_lower > 1)
print("\nNN/TT CI excl 1 count:", int(pan.CI_excl_1.sum()), "/5")
print("kn CI excl 1 count:", int(pan.kn_CI_excl_1.sum()), "/5")
print("\np range:", pan.p_MWU_NN_gt_TT.min(), pan.p_MWU_NN_gt_TT.max())
