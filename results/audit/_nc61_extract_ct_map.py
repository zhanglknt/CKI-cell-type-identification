# nc61 v2: extract unique cell_ontology_class values from TS h5ad (old anndata format)
# obs columns are int8/int16 code datasets; obs/__categories/<col> holds category names
import h5py, os, json, csv

TS_DIR = r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human"
FILES = ["TS_Bone_Marrow.h5ad", "TS_Heart.h5ad", "TS_Kidney.h5ad",
         "TS_Liver.h5ad", "TS_Lung.h5ad", "TS_Spleen.h5ad"]

def dec(x):
    return x.decode() if isinstance(x, bytes) else x

all_cts = set()
per_organ = {}
for fn in FILES:
    path = os.path.join(TS_DIR, fn)
    with h5py.File(path, "r") as h5:
        obs = h5["obs"]
        cats = [dec(c) for c in obs["__categories"]["cell_ontology_class"][:]]
        codes = obs["cell_ontology_class"][:]
        used = sorted({cats[c] for c in codes if c >= 0})
        organ = fn.replace("TS_", "").replace(".h5ad", "")
        per_organ[organ] = used
        all_cts.update(used)
        print(f"[{organ}] cells={len(codes):,}  distinct_ct={len(used)}")
print("union distinct CT names:", len(all_cts))

# pair file CT names
pair_csv = r"C:\Users\KnightZ\Desktop\细胞受选择\results\phase33_v3_human_pairs.csv"
pair_cts = set()
with open(pair_csv, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        for side in row["pair"].split(" vs "):
            pair_cts.add(side.split("|", 1)[1])
print("pair distinct CT names:", len(pair_cts))

# case-insensitive containment check
lower_map = {c.lower(): c for c in all_cts}
missing = sorted(ct for ct in pair_cts if ct.lower() not in lower_map)
print("pair CTs not found in h5ad cell_ontology_class (case-insens):", len(missing))
for m in missing:
    print("  -", m)

out = {
    "pair_cts": sorted(pair_cts),
    "ts_cts": sorted(all_cts),
    "pair_missing_from_ts": missing,
    "per_organ": per_organ,
}
with open(r"C:\Users\KnightZ\Desktop\细胞受选择\results\nc61_ct_names.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote results/nc61_ct_names.json")
