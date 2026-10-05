# nc61: CL ontology graph distance x CKI divergence analysis (option A, offline, no MS edits)
# inputs:  results/audit/cl.obo, results/nc61_label_to_fullct.json, results/phase33_v3_human_pairs.csv
# outputs: results/nc61_lineage_distance.csv, results/nc61_lineage_stats.json
import json, csv, re, sys
import networkx as nx
from collections import defaultdict

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"

# ---------- 1. parse cl.obo ----------
terms = {}       # id -> {name, parents(set), alts(set), synonyms(set)}
cur = None
in_term = False
with open(BASE + r"\results\audit\cl.obo", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if line == "[Term]":
            if cur and not cur.get("obsolete"):
                terms[cur["id"]] = cur
            cur = {"id": None, "name": None, "parents": set(), "alts": set(), "syns": set(), "obsolete": False}
            in_term = True
            continue
        if line.startswith("["):
            if cur and cur.get("id") and not cur.get("obsolete"):
                terms[cur["id"]] = cur
            cur = None
            in_term = False
            continue
        if not in_term or cur is None:
            continue
        if line.startswith("id: "):
            cur["id"] = line[4:].strip()
        elif line.startswith("name: "):
            cur["name"] = line[6:].strip()
        elif line.startswith("alt_id: "):
            cur["alts"].add(line[8:].strip())
        elif line.startswith("is_a: "):
            pid = line[6:].split(" ! ")[0].split(" ")[0].strip()
            cur["parents"].add(pid)
        elif line.startswith("relationship: "):
            m = re.match(r"relationship: (\S+) (\S+)", line)
            if m and m.group(1) in ("develops_from",):
                cur["parents"].add(m.group(2))
        elif line.startswith("synonym: "):
            m = re.match(r'synonym: "(.+?)" (\S+)', line)
            if m and m.group(2) in ("EXACT", "RELATED", "BROAD", "NARROW"):
                cur["syns"].add(m.group(1).lower())
        elif line.startswith("is_obsolete: true"):
            cur["obsolete"] = True
if cur and cur.get("id") and not cur.get("obsolete"):
    terms[cur["id"]] = cur
print(f"parsed CL terms: {len(terms)}")

# name/synonym/alt lookup
name2id = {}
for tid, t in terms.items():
    if t["name"]:
        name2id.setdefault(t["name"].lower(), tid)
    for s in t["syns"]:
        name2id.setdefault(s, tid)
alt2id = {}
for tid, t in terms.items():
    for a in t["alts"]:
        alt2id[a] = tid

# ---------- 2. graph ----------
G = nx.DiGraph()
for tid in terms:
    G.add_node(tid)
for tid, t in terms.items():
    for p in t["parents"]:
        if p in terms:  # keep CL-internal edges only
            G.add_edge(p, tid)   # parent -> child
roots = [n for n in G.nodes if G.in_degree(n) == 0]
print(f"graph nodes={G.number_of_nodes()} edges={G.number_of_edges()} roots={len(roots)}")

depth = {}
for n in nx.topological_sort(G):
    ps = list(G.predecessors(n))
    depth[n] = 0 if not ps else 1 + max(depth[p] for p in ps)

def cl_dist(a, b):
    if a == b:
        return 0, a, depth.get(a, 0)
    anc_a = nx.ancestors(G, a) | {a}
    anc_b = nx.ancestors(G, b) | {b}
    common = anc_a & anc_b
    if not common:
        return None, None, None
    lca = max(common, key=lambda x: depth[x])
    return depth[a] + depth[b] - 2 * depth[lca], lca, depth[lca]

# ---------- 3. map 66 full CT names -> CL ids ----------
rec = json.load(open(BASE + r"\results\nc61_label_to_fullct.json", encoding="utf-8"))
label2full = rec["label_to_full_ct"]
collisions = rec["collisions"]

full_names = sorted(set(label2full.values()))
ct2cl, unmatched = {}, []
for ct in full_names:
    key = ct.lower()
    if key in name2id:
        ct2cl[ct] = name2id[key]
    else:
        unmatched.append(ct)
print(f"CT->CL exact(name/syn) matched: {len(ct2cl)}/{len(full_names)}")
if unmatched:
    print("UNMATCHED:")
    for u in unmatched:
        print("  -", u)

# manual curation for stragglers (verified against CL names in releases/2026-06-08)
MANUAL = {
    "capillary aerocyte": "CL:4028003",                # alveolar capillary type 2 endothelial cell (syn: aerocyte)
    "cd4-positive alpha-beta t cell": "CL:0000624",    # CD4-positive, alpha-beta T cell
    "cd8-positive alpha-beta t cell": "CL:0000625",    # CD8-positive, alpha-beta T cell
    "erythroid progenitor": "CL:0000038",              # erythroid progenitor cell
    "myeloid progenitor": "CL:0000049",                # common myeloid progenitor
    "cd24 neutrophil": "CL:0000775",                   # neutrophil (no finer CL term)
    "nampt neutrophil": "CL:0000775",                  # neutrophil (no finer CL term)
    "bronchial vessel endothelial cell": "CL:0000115", # endothelial cell (no finer CL term)
}
for ct, cid in MANUAL.items():
    if ct in unmatched:
        if cid in terms:
            ct2cl[ct] = cid
            unmatched.remove(ct)
            print(f"manual: {ct} -> {cid} ({terms[cid]['name']})")
        else:
            print(f"manual FAILED (id absent): {ct} -> {cid}")

# ambiguous label candidates -> CL ids
amb_map = {}
for lab, opts in collisions.items():
    amb_map[lab] = []
    for organ, full in opts:
        cid = ct2cl.get(full, name2id.get(full.lower()))
        amb_map[lab].append((full, cid))
    print(f"ambiguous {lab}: {amb_map[lab]}")

# ---------- 4. per-row distances ----------
rows_out = []
n_amb_rows = 0
with open(BASE + r"\results\phase33_v3_human_pairs.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        a, b = row["pair"].split(" vs ")
        amb = (a in amb_map) or (b in amb_map)
        if amb:
            n_amb_rows += 1
        if a in amb_map:
            a_full, a_cid = amb_map[a][0]  # primary = first candidate
        else:
            a_full = label2full[a]
            a_cid = ct2cl.get(a_full)
        if b in amb_map:
            b_full, b_cid = amb_map[b][0]
        else:
            b_full = label2full[b]
            b_cid = ct2cl.get(b_full)
        d = lca = ld = None
        if a_cid and b_cid:
            d, lca, ld = cl_dist(a_cid, b_cid)
        rows_out.append({
            "pair": row["pair"], "a": a, "b": b,
            "ct_a": a_full, "ct_b": b_full,
            "cl_a": a_cid or "", "cl_b": b_cid or "",
            "cl_dist": "" if d is None else d,
            "lca": lca or "", "lca_depth": "" if ld is None else ld,
            "omega": float(row["omega"]), "kn": float(row["kn"]), "kf": float(row["kf"]),
            "same_organ": row["same_organ"] == "True",
            "same_ct": row["same_ct"] == "True",
            "ambiguous": amb,
        })

mapped_rows = [r for r in rows_out if r["cl_dist"] != ""]
print(f"rows total={len(rows_out)}  ambiguous={n_amb_rows}  with CL distance={len(mapped_rows)}")

with open(BASE + r"\results\nc61_lineage_distance.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)
print("wrote results/nc61_lineage_distance.csv")

# ---------- 5. statistics ----------
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu, kendalltau

def spearman(x, y):
    r, p = spearmanr(x, y)
    return float(r), float(p)

stats = {}
main = [r for r in mapped_rows if not r["ambiguous"]]
so_dc = [r for r in main if r["same_organ"] and not r["same_ct"]]
stats["n_main_rows"] = len(main)
stats["n_same_organ_diff_ct"] = len(so_dc)

for name, sub in [("same_organ_diff_ct", so_dc), ("all_main", main)]:
    d = [r["cl_dist"] for r in sub]
    out = {"n": len(sub)}
    for key in ("kf", "omega", "kn"):
        v = [r[key] for r in sub]
        r_, p_ = spearman(d, v)
        out[f"rho_{key}"] = r_
        out[f"p_{key}"] = p_
    stats[name] = out

# partial: omega controlling kn -> use k_f directly (kf is kn-free by construction);
# also residual-based partial spearman for omega ~ dist | kn
def resid(x, z):
    # rank-residual of x on z (linear on ranks)
    rx = np.argsort(np.argsort(x)).astype(float)
    rz = np.argsort(np.argsort(z)).astype(float)
    rz = np.vstack([rz, np.ones_like(rz)]).T
    beta = np.linalg.lstsq(rz, rx, rcond=None)[0]
    return rx - rz @ beta

d = np.array([r["cl_dist"] for r in so_dc], float)
om = np.array([r["omega"] for r in so_dc], float)
kn = np.array([r["kn"] for r in so_dc], float)
kf = np.array([r["kf"] for r in so_dc], float)
rd = np.argsort(np.argsort(d)).astype(float)
r_om_kn = resid(om, kn)
rho_part, p_part = spearman(rd, r_om_kn)
stats["same_organ_diff_ct"]["rho_omega_partial_kn"] = float(rho_part)
stats["same_organ_diff_ct"]["p_omega_partial_kn"] = float(p_part)

# distance bins
bins = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 30)]
bin_stats = []
for lo, hi in bins:
    sub = [r for r in so_dc if lo <= r["cl_dist"] <= hi]
    if not sub:
        continue
    bin_stats.append({
        "bin": f"{lo}-{hi}", "n": len(sub),
        "kf_median": float(np.median([r["kf"] for r in sub])),
        "omega_median": float(np.median([r["omega"] for r in sub])),
        "kn_median": float(np.median([r["kn"] for r in sub])),
    })
stats["same_organ_diff_ct"]["dist_bins"] = bin_stats

# close vs far MWU
close = [r for r in so_dc if r["cl_dist"] <= 4]
far = [r for r in so_dc if r["cl_dist"] >= 7]
if close and far:
    u, p = mannwhitneyu([r["kf"] for r in close], [r["kf"] for r in far], alternative="less")
    stats["close_vs_far"] = {
        "close_n": len(close), "far_n": len(far),
        "close_kf_median": float(np.median([r["kf"] for r in close])),
        "far_kf_median": float(np.median([r["kf"] for r in far])),
        "mwu_p_close_less_far": float(p),
    }

# per-organ spearman
per_organ = {}
for r in so_dc:
    per_organ.setdefault(r["a"].split("|")[0], []).append(r)
for org, sub in sorted(per_organ.items()):
    dd = [r["cl_dist"] for r in sub]
    if len(set(dd)) < 3 or len(sub) < 10:
        continue
    rr, pp = spearman(dd, [r["kf"] for r in sub])
    rr2, pp2 = spearman(dd, [r["omega"] for r in sub])
    per_organ[org] = {"n": len(sub), "rho_kf": rr, "p_kf": pp, "rho_omega": rr2, "p_omega": pp2}
stats["per_organ"] = per_organ

# permutation test (shuffle distances within organ, 10k reps)
rng = np.random.default_rng(42)
obs_rho = stats["same_organ_diff_ct"]["rho_kf"]
organ_groups = defaultdict(list)
for i, r in enumerate(so_dc):
    organ_groups[r["a"].split("|")[0]].append(i)
d_arr = np.array([r["cl_dist"] for r in so_dc], float)
kf_arr = np.array([r["kf"] for r in so_dc], float)
B = 10000
cnt = 0
for _ in range(B):
    dp = d_arr.copy()
    for idxs in organ_groups.values():
        dp[idxs] = rng.permutation(dp[idxs])
    r_p, _ = spearmanr(dp, kf_arr)
    if r_p >= obs_rho:
        cnt += 1
stats["permutation_kf"] = {"B": B, "obs_rho": obs_rho, "p": (cnt + 1) / (B + 1)}

with open(BASE + r"\results\nc61_lineage_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=1)
print(json.dumps(stats, ensure_ascii=False, indent=1))
