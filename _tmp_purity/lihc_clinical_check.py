# -*- coding: utf-8 -*-
import json
clin = json.load(open(r"C:/Users/KnightZ/Desktop/细胞受选择/data/tcga/lihc_patient_clinical.json"))
pids = sorted(set(rec.get("patientId", "") for rec in clin))
out = [f"LIHC clinical patients: {len(pids)}",
       f"CC-prefix patients in LIHC clinical: {[p for p in pids if p.startswith('TCGA-CC')]}",
       f"RG patients in LIHC clinical: {[p for p in pids if p.startswith('TCGA-RG')]}"]
open(r"C:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/lihc_clinical_check.txt", "w").write("\n".join(out))
