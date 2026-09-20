import json
from collections import Counter
pc = json.load(open(r'C:/Users/KnightZ/Desktop/细胞受选择/data/tcga/lihc_patient_clinical.json'))
for attr in ['AJCC_PATHOLOGIC_TUMOR_STAGE','GRADE','SEX','AGE','OS_STATUS','OS_MONTHS']:
    vals = Counter(r['value'] for r in pc if r['clinicalAttributeId']==attr)
    print(attr, '->', dict(list(vals.most_common(14))))
