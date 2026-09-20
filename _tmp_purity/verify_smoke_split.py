# -*- coding: utf-8 -*-
import json
import pandas as pd

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
clin = json.load(open(ROOT + "/data/tcga/luad_patient_clinical_cbioportal.json", encoding="utf-8"))
sm = {}
for rec in clin:
    if rec.get("clinicalAttributeId") == "TOBACCO_SMOKING_HISTORY_INDICATOR":
        pid = rec.get("patientId", "")
        if not pid.startswith("TCGA"):
            pid = "TCGA-" + pid
        sm[pid] = str(rec.get("value"))

mut = json.load(open(ROOT + "/data/tcga/luad_egfr_kras_mutations.json"))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])
pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
lu = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
samples = set(lu.sample_a) | set(lu.sample_b)

def grp(s):
    e, k = s in egfr, s in kras
    return "DOUBLE" if (e and k) else ("EGFR" if e else ("KRAS" if k else "WT"))

rows = []
for s in samples:
    g = grp(s)
    if g == "DOUBLE":
        continue
    v = sm.get(s[:12])
    rows.append((g, v))
n_known = sum(1 for g, v in rows if v is not None)
never = sum(1 for g, v in rows if v == "1")
ever = sum(1 for g, v in rows if v in ("2", "3", "4", "5", "6"))
by_g = {}
for g, v in rows:
    if v is not None:
        by_g.setdefault(g, [0, 0])
        if v == "1":
            by_g[g][0] += 1
        else:
            by_g[g][1] += 1
out = [f"total non-double samples: {len(rows)}",
       f"smoking known: {n_known} (never={never}, ever={ever})",
       f"by group (never, ever): {by_g}"]
open(ROOT + "/_tmp_purity/smoke_split_verify.txt", "w").write("\n".join(out))
