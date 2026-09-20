# -*- coding: utf-8 -*-
import json
clin = json.load(open(r"C:/Users/KnightZ/Desktop/细胞受选择/data/tcga/luad_patient_clinical_cbioportal.json", encoding="utf-8"))
ids = sorted(set(rec.get("patientId", "") for rec in clin))[:10]
smoke = [(rec.get("patientId"), rec.get("value")) for rec in clin
         if rec.get("clinicalAttributeId") == "TOBACCO_SMOKING_HISTORY_INDICATOR"][:5]
open(r"C:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/pid_format.txt", "w").write(
    "sample patientIds: " + repr(ids) + "\nsmoke records: " + repr(smoke))
