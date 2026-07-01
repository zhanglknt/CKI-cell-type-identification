#!/usr/bin/env python3
"""Quick scan of TCGA sample composition for ed_fig3 target cancers."""
import gzip
from collections import Counter

TCGA_FILE = "data/tcga/tcga_RSEM_gene_tpm.gz"

header = gzip.open(TCGA_FILE, "rt").readline().strip().split("\t")
sample_ids = header[1:]
print(f"Total samples: {len(sample_ids)}")

# TSS->project mappings
brca_codes = {'A1','A2','A7','A8','AN','AO','AQ','AR','B6','BH','C8','D8','E2','EW','GI','WT','XX','E9','GM','HN','JL','LD','LL','MS','OL','PE','PL','S3','UL','V7','W8','WV'}
luad_codes = {'05','35','38','44','49','50','55','64','67','73','75','78','86','91','93','97','J2','L3','L4','M1','MP','MT','N1','N6','O1','S2','TR','TV','TQ','NJ','KN','LF'}
lusc_codes = {'18','21','22','33','34','37','39','43','51','52','56','60','63','66','68','70','77','85','90','92','94','96','98','CC','L5','N2','NK','Q1','IE','IF','IG'}
lihc_codes = {'BC','DD','ED','EP','ES','FV','FY','G3','GJ','HP','HU','K7','KR','LG','NI','O8','PD','QN','RC','RG','T6','UB','WQ','XR','YA','ZP','ZS','MI','F5'}
kirc_codes = {'A3','AK','AL','AY','B0','B1','B2','B3','B4','B8','BP','BW','CJ','CW','CZ','DV','DX','EU','GK','HE','I6','K6','KL','MM','MW','P4','Q2','UZ','V5','XM','YE'}
coad_codes = {'3L','A6','AA','AD','AF','AG','AH','AM','AY','AZ','BQ','BR','C4','C5','C6','C7','C8','C9','CA','CB','CK','CM','CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ','D5','DB','DC','DD','DM','DN','DT','DY','F4','G4','G5','HA','HC','HD','HF','HG','HI','HJ','HK','HL','HM','HN','HO','HU','HV','HW','HX','HY','HZ','I0','I1','I2','I3','I4','I5','I7','I8','I9','IA','IB','IC','ID','IE','IF','IG','IH','II','IJ','IK','IL','IM','IN','IO','IP','IQ','IR','IS','IT','IU','IV','IW','IX','IY','IZ','J0','J1','J2','J3','J4','J5','J6','J7','J8','J9','JA','JB','JC','JD','JE','JF','JG','JH','JI','JJ','JK','JL','JM','JN','JO','JP','JQ','JR','JS','JT','JU','JV','JW','JX','JY','JZ','K0','K1','K2','K3','K4','K5','K6','K7','K8','K9','KA','KB','KC','KD','KE','KF','KG','KH','KI','KJ','KK','KL','KM','KN','KO','KP','KQ','KR','KS','KT','KU','KV','KW','KX','KY','KZ'}
hnsc_codes = {'4P','BB','BA','C9','CN','CQ','CR','CV','CX','D6','DQ','F7','H7','HD','HL','HQ','HU','I5','IQ','JQ','JU','KD','KR','M2','M7','M9','MC','MD','MF','MH','MJ','ML','MM','MN','MO','MP','MQ','MR','MS','MT','MU','MV','MW','MX','MY','MZ','N0','N1','N2','N3','N4','N5','N6','N7','N8','N9','NA','NB','NC','ND','NE','NF','NG','NH','NI','NJ','NK','NL','NM','NN','NO','NP','NQ','NR','NS','NT','NU','NV','NW','NX','NY','NZ','O0','O1','O2','O3','O4','O5','O6','O7','O8','O9','OA','OB','OC','OD','OE','OF','OG','OH','OI','OJ','OK','OL','OM','ON','OO','OP','OQ','OR','OS','OT','OU','OV','OW','OX','OY','OZ','P0','P1','P2','P3','P4','P5','P6','P7','P8','P9','PA','PB','PC','PD','PE','PF','PG','PH','PI','PJ','PK','PL','PM','PN','PO','PP','PQ','PR','PS','PT','PU','PV','PW','PX','PY','PZ','Q0','Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','QA','QB','QC','QD','QE','QF','QG','QH','QI','QJ','QK','QL','QM','QN','QO','QP','QQ'}

known_mapping = {}
for c in brca_codes: known_mapping[c] = "BRCA"
for c in luad_codes: known_mapping[c] = "LUAD"
for c in lusc_codes: known_mapping[c] = "LUSC"
for c in lihc_codes: known_mapping[c] = "LIHC"
for c in kirc_codes: known_mapping[c] = "KIRC"
for c in coad_codes: known_mapping[c] = "COAD"
for c in hnsc_codes: known_mapping[c] = "HNSC"

# Count by project and sample type
proj_st = {}
unknown_tss = set()

for sid in sample_ids:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    st = parts[3][:2]
    proj = known_mapping.get(tss, None)
    if proj is None:
        unknown_tss.add(tss)
    else:
        key = (proj, st)
        proj_st[key] = proj_st.get(key, 0) + 1

target = ["BRCA", "KIRC", "LIHC", "LUAD", "COAD", "HNSC"]
st_labels = {"01": "Tumor", "02": "Recurr", "06": "Metast", "11": "Normal"}

print("\n=== Sample counts per cancer x sample type ===")
for proj in target:
    row = {st: proj_st.get((proj, st), 0) for st in ["01", "02", "06", "11"]}
    total = sum(row.values())
    parts_str = "  ".join(f"{st_labels[s]}={row[s]}" for s in ["01", "11", "06", "02"])
    print(f"  {proj}: total={total}  {parts_str}")

print(f"\nUnknown TSS codes: {len(unknown_tss)}")
print(f"Mapped samples: {sum(proj_st.values())}")
print(f"Unmapped samples: {len(sample_ids) - sum(proj_st.values())}")

if len(unknown_tss) < 100:
    print(f"  Unknown: {sorted(unknown_tss)}")
