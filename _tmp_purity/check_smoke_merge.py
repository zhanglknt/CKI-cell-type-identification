# -*- coding: utf-8 -*-
import json
import pandas as pd

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
clin = json.load(open(ROOT + "/data/tcga/luad_patient_clinical_cbioportal.json", encoding="utf-8"))
pat = {}
for rec in clin:
    key = rec.get("patientId", "")
    if not key.startswith("TCGA"):
        key = "TCGA-" + key
    a = rec.get("clinicalAttributeId")
    if a == "TOBACCO_SMOKING_HISTORY_INDICATOR":
        pat.setdefault(key, {})["smoke"] = rec.get("value")

pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
lu = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
samples = set(lu.sample_a) | set(lu.sample_b)
patients = set(s[:12] for s in samples)

out = [f"LUAD TT unique samples: {len(samples)}, patients: {len(patients)}",
       f"smoking known: {sum(1 for p in patients if p in pat and 'smoke' in pat[p])}"]
vals = {}
for p in patients:
    if p in pat and "smoke" in pat[p]:
        v = str(pat[p]["smoke"])
        vals[v] = vals.get(v, 0) + 1
out.append(f"smoke code distribution among matched: {vals}")
open(ROOT + "/_tmp_purity/smoke_merge_check.txt", "w").write("\n".join(out))
