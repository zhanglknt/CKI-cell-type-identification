# nc61 v3: recover full cell_ontology_class names for the 100 pair labels
# replicates 05_phase33_v3_fixed.py label logic (replacements + [:14]+".." truncation)
import h5py, os, json, csv
from collections import defaultdict

TS_DIR = r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human"
FILES = {"Bone_Marrow": "TS_Bone_Marrow.h5ad", "Heart": "TS_Heart.h5ad",
         "Kidney": "TS_Kidney.h5ad", "Liver": "TS_Liver.h5ad",
         "Lung": "TS_Lung.h5ad", "Spleen": "TS_Spleen.h5ad"}

def dec(x):
    return x.decode() if isinstance(x, bytes) else x

REPLACEMENTS = {
    "endothelial cell of hepatic sinusoid": "livEC",
    "cardiac muscle cell": "cardio",
    "natural killer cell": "NK",
    "type II pneumocyte": "pneumoII",
    "type I pneumocyte": "pneumoI",
    "endothelial cell": "EC",
    "epithelial cell": "epi",
}

def shorten(ct):
    s = ct
    for old, new in REPLACEMENTS.items():
        s = s.replace(old, new)
    if len(s) > 16:
        s = s[:14] + ".."
    return s

# build short-label -> full-name candidate map (detect collisions)
cand = defaultdict(list)   # label -> list of (organ, full_ct)
for organ, fn in FILES.items():
    with h5py.File(os.path.join(TS_DIR, fn), "r") as h5:
        cats = [dec(c) for c in h5["obs"]["__categories"]["cell_ontology_class"][:]]
    for ct in cats:
        label = f"{organ[:4]}|{shorten(ct)}"
        cand[label].append((organ, ct))

# collect the 100 labels actually in the pair csv
pair_csv = r"C:\Users\KnightZ\Desktop\细胞受选择\results\phase33_v3_human_pairs.csv"
labels_used = []
seen = set()
rows = []
with open(pair_csv, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)
        for side in row["pair"].split(" vs "):
            if side not in seen:
                seen.add(side)
                labels_used.append(side)
print("distinct labels in pair csv:", len(labels_used))

resolved, unmatched, collisions = {}, [], {}
for lab in labels_used:
    hits = cand.get(lab, [])
    if len(hits) == 1:
        resolved[lab] = hits[0][1]
    elif len(hits) == 0:
        unmatched.append(lab)
    else:
        collisions[lab] = hits

print(f"resolved {len(resolved)}/100  unmatched {len(unmatched)}  collisions {len(collisions)}")
for u in unmatched:
    print("  UNMATCHED:", u)
for k, v in collisions.items():
    print("  COLLISION:", k, "->", v)

out = {"label_to_full_ct": resolved, "unmatched": unmatched,
       "collisions": {k: v for k, v in collisions.items()}}
with open(r"C:\Users\KnightZ\Desktop\细胞受选择\results\nc61_label_to_fullct.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote results/nc61_label_to_fullct.json")
