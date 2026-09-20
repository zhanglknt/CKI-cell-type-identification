# -*- coding: utf-8 -*-
"""Fetch TCGA-LUAD patient clinical data (smoking/sex/age/stage) from cBioPortal API."""
import json
import urllib.request

OUT = r"c:/Users/KnightZ/Desktop/细胞受选择/data/tcga/luad_patient_clinical_cbioportal.json"
LOG = r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/cbio_fetch_log.txt"

URL = ("https://www.cbioportal.org/api/studies/luad_tcga/clinical-data"
       "?clinicalDataType=PATIENT&projection=DETAILED")
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
       "Accept": "application/json"}

log = []
try:
    req = urllib.request.Request(URL, headers=hdr)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    log.append(f"OK: {len(data)} clinical-data records -> {OUT}")
    attrs = {}
    for rec in data:
        attrs.setdefault(rec.get("clinicalAttributeId", "?"), 0)
        attrs[rec.get("clinicalAttributeId", "?")] += 1
    for a in ["TOBACCO_SMOKING_HISTORY_INDICATOR", "SMOKING_PACK_YEARS",
              "SEX", "AGE", "AJCC_PATHOLOGIC_TUMOR_STAGE"]:
        log.append(f"attr {a}: {attrs.get(a, 'MISSING')} records")
    # preview smoking values
    vals = sorted(set(str(rec.get("value")) for rec in data
                      if rec.get("clinicalAttributeId") == "TOBACCO_SMOKING_HISTORY_INDICATOR"))
    log.append("smoking indicator distinct values: " + json.dumps(vals[:20]))
except Exception as e:
    log.append(f"FAIL: {e}")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(log))
