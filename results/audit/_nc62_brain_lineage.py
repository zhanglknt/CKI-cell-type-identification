# nc62: brain lineage chain (option B) — same-region x cross-CT CKI vs CL graph distance
# Offline validation, no MS edits.
#
# Conventions replicate notebooks/08c_brain_bootstrap_v3.py (authoritative brain
# pipeline behind brain_bs_null_observed_pairs.csv / MS brain section):
#   HK  = HRT Atlas (data/housekeeping/Human_Mouse_Common.csv, "Human" col)
#         mapped via var["Gene"] symbols
#   k_f gene universe = top-5000 non-HK genes by RAW global mean expression
#   pseudobulk = mean of RAW counts per (roi, supercluster_term) group,
#                then /sum*1e4 over the reduced gene set, then log1p
#   filters: >=20 nuclei per (region, CT) group, >=50 nuclei per region
# Two k_f variants per pair:
#   kf_pp200 = JSD over per-pair top-200 |diff| within the 5000 (08c-native;
#              used for pipeline validation against the bs_null file; expected
#              to saturate for cross-CT comparisons)
#   kf_fixed = JSD over ALL 5000 fixed non-HK genes (non-saturating; primary
#              lineage-signal metric, conceptually matching option A's fixed
#              functional gene set in the TS analysis)
# k_n = JSD over HK genes; omega variants = kf/kn accordingly.
#
# inputs:  data/brain/Nonneurons.h5ad (888,263 nuclei x 59,480 genes, CSR int16)
#          results/audit/cl.obo (CL releases/2026-06-08, reused from nc61)
#          data/housekeeping/Human_Mouse_Common.csv
#          results/brain_bs_null_observed_pairs.csv (validation target)
# outputs: results/nc62_brain_lineage_pairs.csv
#          results/nc62_brain_lineage_stats.json
import sys, os, json, csv, re, time
import numpy as np
import pandas as pd
import h5py
import networkx as nx
from scipy import sparse
from scipy.stats import spearmanr, mannwhitneyu, wilcoxon
from collections import defaultdict

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
sys.path.insert(0, BASE)
from cki.core import js_divergence

H5 = BASE + r"\data\brain\Nonneurons.h5ad"
HK_CSV = BASE + r"\data\housekeeping\Human_Mouse_Common.csv"
MIN_NUCLEI_PER_GROUP = 20
MIN_NUCLEI_PER_REGION = 50
N_TOP_KF = 200
N_HVG = 5000
CHUNK = 50000

# ---------- 1. parse cl.obo (identical to nc61) ----------
terms = {}
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
        elif line.startswith("is_a: "):
            pid = line[6:].split(" ! ")[0].split(" ")[0].strip()
            cur["parents"].add(pid)
        elif line.startswith("relationship: "):
            m = re.match(r"relationship: (\S+) (\S+)", line)
            if m and m.group(1) in ("develops_from",):
                cur["parents"].add(m.group(2))
        elif line.startswith("is_obsolete: true"):
            cur["obsolete"] = True
if cur and cur.get("id") and not cur.get("obsolete"):
    terms[cur["id"]] = cur
print(f"parsed CL terms: {len(terms)}")

G = nx.DiGraph()
for tid in terms:
    G.add_node(tid)
for tid, t in terms.items():
    for p in t["parents"]:
        if p in terms:
            G.add_edge(p, tid)   # parent -> child
depth = {}
for n in nx.topological_sort(G):
    ps = list(G.predecessors(n))
    depth[n] = 0 if not ps else 1 + max(depth[p] for p in ps)

def cl_dist(a, b):
    if a == b:
        return 0, a
    anc_a = nx.ancestors(G, a) | {a}
    anc_b = nx.ancestors(G, b) | {b}
    common = anc_a & anc_b
    if not common:
        return None, None
    lca = max(common, key=lambda x: depth[x])
    return depth[a] + depth[b] - 2 * depth[lca], lca

# ---------- 2. curated CT -> CL mapping (verified against cl.obo names) ----------
CT2CL = {
    "Astrocyte": "CL:0000127",                              # astrocyte
    "Bergmann glia": "CL:0000644",                          # Bergmann glial cell
    "Choroid plexus": "CL:0000706",                         # choroid plexus epithelial cell
    "Committed oligodendrocyte precursor": "CL:4023059",    # committed oligodendrocyte precursor
    "Ependymal": "CL:0000065",                              # ependymal cell
    "Fibroblast": "CL:0000057",                             # fibroblast
    "Microglia": "CL:0000129",                              # microglial cell
    "Oligodendrocyte": "CL:0000128",                        # oligodendrocyte
    "Oligodendrocyte precursor": "CL:0002453",              # oligodendrocyte precursor cell
    # "Vascular" excluded from main: mixes endothelial CL:0000115 / pericyte CL:0000669 / VSM CL:0000359
}
VASCULAR_CL = "CL:0000115"  # sensitivity only (dominant sub-type, 5,165/9,932)
for ct, cid in CT2CL.items():
    assert cid in terms, f"{cid} absent from obo"
    print(f"  {ct} -> {cid} ({terms[cid]['name']})")

# ---------- 3. HK genes (HRT via var.Gene symbols) ----------
hk_df = pd.read_csv(HK_CSV, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"HRT Atlas human HK: {len(hk_human)}")

f = h5py.File(H5, "r")
gene_cats = [c.decode() for c in f["var/Gene/categories"][:]]
gene_codes = f["var/Gene/codes"][:]
gene_syms = np.array([gene_cats[c] if c >= 0 else "" for c in gene_codes])
n_genes = len(gene_syms)
hk_global = np.array(sorted([i for i, s in enumerate(gene_syms) if s in hk_human]), dtype=int)
print(f"HK matched in var: {len(hk_global)}")

# ---------- 4. chunked accumulation: raw gene sums + raw group sums ----------
print("\n=== chunked pass over Nonneurons.h5ad ===")
t0 = time.time()
sc_cats = [c.decode() for c in f["obs/supercluster_term/categories"][:]]
roi_cats = [c.decode() for c in f["obs/roi/categories"][:]]
sc_codes = f["obs/supercluster_term/codes"][:]
roi_codes = f["obs/roi/codes"][:]
n_sc, n_roi = len(sc_cats), len(roi_cats)
X = f["X"]
n_cells = X.attrs["shape"][0]
indptr = X["indptr"][:]
print(f"cells={n_cells:,} genes={n_genes:,} nnz={X['data'].shape[0]:,}")

NG = n_roi * n_sc
gid_all = roi_codes.astype(np.int64) * n_sc + sc_codes.astype(np.int64)
cnt_g = np.bincount(gid_all, minlength=NG)
cnt_roi = np.bincount(roi_codes, minlength=n_roi)

raw_g = np.zeros(n_genes, np.float64)           # raw per-gene sums (HVG means)
S = np.zeros((NG, n_genes), np.float64)         # raw group sums

for s in range(0, n_cells, CHUNK):
    e = min(s + CHUNK, n_cells)
    p0, p1 = int(indptr[s]), int(indptr[e])
    data = X["data"][p0:p1].astype(np.float64)
    idx = X["indices"][p0:p1]
    ip = indptr[s:e + 1].astype(np.int64) - p0
    raw_g += np.bincount(idx, weights=data, minlength=n_genes)
    Xc = sparse.csr_matrix((data, idx, ip), shape=(e - s, n_genes))
    gid_c = gid_all[s:e]
    W = sparse.csr_matrix(
        (np.ones(e - s, np.float64), (gid_c, np.arange(e - s))),
        shape=(NG, e - s))
    S += (W @ Xc).toarray()
    print(f"  rows {s:>7,}-{e:>7,} done ({time.time()-t0:.0f}s)", flush=True)

# ---------- 5. reduced gene set: HK + top-5000 non-HK by raw mean ----------
gene_means = raw_g / n_cells
non_hk_means = gene_means.copy()
non_hk_means[hk_global] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
is_hk_keep = np.isin(keep_global, hk_global)
hk_in_red = np.where(is_hk_keep)[0]
nonhk_in_red = np.where(~is_hk_keep)[0]
print(f"reduced set: {len(keep_global)} genes (HK={len(hk_in_red)} + non-HK={len(nonhk_in_red)})")

# ---------- 6. group filter + pseudobulks (mean raw -> /sum*1e4 -> log1p) ----------
region_ok = cnt_roi >= MIN_NUCLEI_PER_REGION
group_ok = (cnt_g >= MIN_NUCLEI_PER_GROUP) & region_ok[np.arange(NG) // n_sc]
ok_gids = np.where(group_ok)[0]
Sred = S[np.ix_(ok_gids, keep_global)]                      # (n_groups, n_keep)
PB = Sred / cnt_g[ok_gids][:, None]                          # mean raw counts
totals = PB.sum(axis=1)
PB[totals > 0] = PB[totals > 0] / totals[totals > 0][:, None] * 1e4
PB = np.log1p(PB).astype(np.float32)
print(f"groups ok: {len(ok_gids)} (regions ok: {region_ok.sum()}/{n_roi})")

gid2pos = {g: i for i, g in enumerate(ok_gids)}
region_to_cts = defaultdict(list)
for g in ok_gids:
    r, c = divmod(g, n_sc)
    region_to_cts[r].append(c)

# ---------- 7. pair computation ----------
def pair_cki(pbi, pbj):
    kn = js_divergence(pbi[hk_in_red], pbj[hk_in_red])
    diff = np.abs(pbi - pbj)[nonhk_in_red]
    top = min(N_TOP_KF, len(diff))
    sel = nonhk_in_red[np.argpartition(diff, -top)[-top:]]
    kf_pp = js_divergence(pbi[sel], pbj[sel])
    kf_fx = js_divergence(pbi[nonhk_in_red], pbj[nonhk_in_red])
    return kn, kf_pp, kf_fx

rows = []
rows_vasc = []
for r, cts in sorted(region_to_cts.items()):
    cts = sorted(cts)
    for i in range(len(cts)):
        for j in range(i + 1, len(cts)):
            ca, cb = cts[i], cts[j]
            cta, ctb = sc_cats[ca], sc_cats[cb]
            pbi = PB[gid2pos[r * n_sc + ca]]
            pbj = PB[gid2pos[r * n_sc + cb]]
            kn, kf_pp, kf_fx = pair_cki(pbi, pbj)
            va = cta == "Vascular"
            vb = ctb == "Vascular"
            if va or vb:
                other, other_cl = (ctb, CT2CL.get(ctb)) if va else (cta, CT2CL.get(cta))
                if not other_cl:
                    continue
                d, lca = cl_dist(VASCULAR_CL, other_cl)
                rec = {"region": roi_cats[r],
                       "ct_a": "Vascular" if va else cta, "ct_b": ctb if va else ctb,
                       "cl_a": VASCULAR_CL if va else CT2CL[cta],
                       "cl_b": VASCULAR_CL if vb else CT2CL[ctb],
                       "cl_dist": "" if d is None else d, "lca": lca or "",
                       "kn": kn, "kf_pp200": kf_pp, "kf_fixed": kf_fx,
                       "omega_pp200": kf_pp / kn if kn > 0 else float("inf"),
                       "omega_fixed": kf_fx / kn if kn > 0 else float("inf"),
                       "n_a": int(cnt_g[r * n_sc + ca]), "n_b": int(cnt_g[r * n_sc + cb])}
                rows_vasc.append(rec)
                continue
            cla, clb = CT2CL.get(cta), CT2CL.get(ctb)
            d = lca = None
            if cla and clb:
                d, lca = cl_dist(cla, clb)
            rows.append({"region": roi_cats[r], "ct_a": cta, "ct_b": ctb,
                         "cl_a": cla or "", "cl_b": clb or "",
                         "cl_dist": "" if d is None else d, "lca": lca or "",
                         "kn": kn, "kf_pp200": kf_pp, "kf_fixed": kf_fx,
                         "omega_pp200": kf_pp / kn if kn > 0 else float("inf"),
                         "omega_fixed": kf_fx / kn if kn > 0 else float("inf"),
                         "n_a": int(cnt_g[r * n_sc + ca]), "n_b": int(cnt_g[r * n_sc + cb])})
print(f"cross-CT same-region pairs (9-CT main): {len(rows)}; vascular sens: {len(rows_vasc)}")

with open(BASE + r"\results\nc62_brain_lineage_pairs.csv", "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows + rows_vasc)

# ---------- 8. statistics ----------
def spearman(x, y):
    rr, pp = spearmanr(x, y)
    return float(rr), float(pp)

def resid(x, z):
    rx = np.argsort(np.argsort(x)).astype(float)
    rz = np.argsort(np.argsort(z)).astype(float)
    rz = np.vstack([rz, np.ones_like(rz)]).T
    beta = np.linalg.lstsq(rz, rx, rcond=None)[0]
    return rx - rz @ beta

stats = {}
main = [r for r in rows if r["cl_dist"] != ""]
stats["n_pairs_main"] = len(main)
stats["n_regions"] = len(set(r["region"] for r in main))
stats["n_hk_genes"] = int(len(hk_in_red))
stats["n_reduced_genes"] = int(len(keep_global))

d = np.array([r["cl_dist"] for r in main], float)
arr = {k: np.array([r[k] for r in main]) for k in ("kn", "kf_pp200", "kf_fixed", "omega_pp200", "omega_fixed")}
out = {"dist_values": sorted(set(d.tolist()))}
for key in ("kf_fixed", "omega_fixed", "kf_pp200", "omega_pp200", "kn"):
    rr, pp = spearman(d, arr[key])
    out[f"rho_{key}"] = rr
    out[f"p_{key}"] = pp
rd = np.argsort(np.argsort(d)).astype(float)
rp, pp2 = spearman(rd, resid(arr["omega_fixed"], arr["kn"]))
out["rho_omega_fixed_partial_kn"] = float(rp)
out["p_omega_fixed_partial_kn"] = float(pp2)

bins = []
for lo, hi in [(1, 2), (3, 4), (5, 6), (7, 8), (9, 40)]:
    m = (d >= lo) & (d <= hi)
    if m.sum():
        bins.append({"bin": f"{lo}-{hi}", "n": int(m.sum()),
                     "kf_fixed_median": float(np.median(arr["kf_fixed"][m])),
                     "kf_pp200_median": float(np.median(arr["kf_pp200"][m])),
                     "omega_fixed_median": float(np.median(arr["omega_fixed"][m])),
                     "kn_median": float(np.median(arr["kn"][m]))})
out["dist_bins"] = bins

rng = np.random.default_rng(42)
region_groups = defaultdict(list)
for i, r in enumerate(main):
    region_groups[r["region"]].append(i)
B = 10000
for metric in ("kf_fixed", "omega_fixed"):
    obs_rho = out[f"rho_{metric}"]
    cntb = 0
    for _ in range(B):
        dp = d.copy()
        for idxs in region_groups.values():
            dp[idxs] = rng.permutation(dp[idxs])
        rp_, _ = spearmanr(dp, arr[metric])
        if rp_ >= obs_rho:
            cntb += 1
    out[f"permutation_{metric}"] = {"B": B, "obs_rho": obs_rho, "p": (cntb + 1) / (B + 1)}
stats["same_region_diff_ct"] = out

sens = main + [r for r in rows_vasc if r["cl_dist"] != ""]
ds = [r["cl_dist"] for r in sens]
rr, pp = spearman(ds, [r["kf_fixed"] for r in sens])
rr2, pp2v = spearman(ds, [r["kf_pp200"] for r in sens])
stats["sensitivity_with_vascular"] = {"n": len(sens),
                                      "rho_kf_fixed": float(rr), "p_kf_fixed": float(pp),
                                      "rho_kf_pp200": float(rr2), "p_kf_pp200": float(pp2v)}

# ---------- 9. oligodendrocyte lineage chain ----------
chain = [("Oligodendrocyte precursor", "Committed oligodendrocyte precursor"),
         ("Committed oligodendrocyte precursor", "Oligodendrocyte"),
         ("Oligodendrocyte precursor", "Oligodendrocyte")]
chain_out = {}
for a, b in chain:
    dd, lca = cl_dist(CT2CL[a], CT2CL[b])
    sub, subk = {}, {}
    for r in main:
        if frozenset([r["ct_a"], r["ct_b"]]) == frozenset([a, b]):
            sub[r["region"]] = r["kf_fixed"]
            subk[r["region"]] = r["kn"]
    chain_out[f"{a} <> {b}"] = {
        "cl_dist": dd, "lca": lca, "lca_name": terms[lca]["name"] if lca else None,
        "n_regions": len(sub),
        "kf_fixed_median": float(np.median(list(sub.values()))) if sub else None,
        "kn_median": float(np.median(list(subk.values()))) if subk else None,
        "per_region": sub,
    }
k_opc_cop = chain_out["Oligodendrocyte precursor <> Committed oligodendrocyte precursor"]["per_region"]
k_cop_ol = chain_out["Committed oligodendrocyte precursor <> Oligodendrocyte"]["per_region"]
k_opc_ol = chain_out["Oligodendrocyte precursor <> Oligodendrocyte"]["per_region"]
common_regs = sorted(set(k_opc_cop) & set(k_cop_ol) & set(k_opc_ol))
ct_ = {"n_common_regions": len(common_regs)}
if len(common_regs) >= 8:
    v1 = np.array([k_opc_cop[r] for r in common_regs])
    v2 = np.array([k_cop_ol[r] for r in common_regs])
    vd = np.array([k_opc_ol[r] for r in common_regs])
    _, p1 = wilcoxon(vd, v1, alternative="greater")
    _, p2 = wilcoxon(vd, v2, alternative="greater")
    ct_.update({
        "kf_opc_cop_median": float(np.median(v1)),
        "kf_cop_oligo_median": float(np.median(v2)),
        "kf_opc_oligo_median": float(np.median(vd)),
        "wilcoxon_opcOl_gt_opcCop_p": float(p1),
        "wilcoxon_opcOl_gt_copOl_p": float(p2),
        "frac_regions_opcOl_gt_both": float(np.mean((vd > v1) & (vd > v2))),
    })
chain_out["paired_tests"] = ct_
stats["oligo_chain"] = {k: {kk: vv for kk, vv in v.items() if kk != "per_region"}
                        for k, v in chain_out.items()}

# ---------- 10. microglia (mesoderm) vs macroglia (neuroectoderm) ----------
macro = {"Astrocyte", "Bergmann glia", "Oligodendrocyte", "Oligodendrocyte precursor",
         "Committed oligodendrocyte precursor", "Ependymal"}
mic_kf, mac_kf = [], []
for r in main:
    pair = {r["ct_a"], r["ct_b"]}
    if "Microglia" in pair and len(pair & macro) == 1:
        mic_kf.append(r["kf_fixed"])
    elif pair <= macro:
        mac_kf.append(r["kf_fixed"])
if mic_kf and mac_kf:
    u, p = mannwhitneyu(mic_kf, mac_kf, alternative="greater")
    stats["microglia_vs_macroglia"] = {
        "microglia_pairs_n": len(mic_kf), "macroglia_pairs_n": len(mac_kf),
        "microglia_kf_fixed_median": float(np.median(mic_kf)),
        "macroglia_kf_fixed_median": float(np.median(mac_kf)),
        "mwu_p_microglia_greater": float(p),
    }

# ---------- 11. same-CT cross-region: dist-0 anchor + 08c replication validation ----------
print("\n=== same-CT cross-region (dist-0 anchor + replication validation) ===", flush=True)
ct_to_regions = defaultdict(list)
for g in ok_gids:
    r, c = divmod(g, n_sc)
    ct_to_regions[c].append(r)
same_ct = []
for c, regs in sorted(ct_to_regions.items()):
    regs = sorted(regs)
    for i in range(len(regs)):
        for j in range(i + 1, len(regs)):
            ra, rb = regs[i], regs[j]
            pbi = PB[gid2pos[ra * n_sc + c]]
            pbj = PB[gid2pos[rb * n_sc + c]]
            kn, kf_pp, kf_fx = pair_cki(pbi, pbj)
            same_ct.append({"ct": sc_cats[c], "ra": roi_cats[ra], "rb": roi_cats[rb],
                            "kn": kn, "kf_pp200": kf_pp, "kf_fixed": kf_fx,
                            "omega_pp200": kf_pp / kn if kn > 0 else np.inf,
                            "omega_fixed": kf_fx / kn if kn > 0 else np.inf})
anchor = {}
for c in range(n_sc):
    vals = [x["kf_fixed"] for x in same_ct if x["ct"] == sc_cats[c]]
    if vals:
        anchor[sc_cats[c]] = {"n_pairs": len(vals), "kf_fixed_median": float(np.median(vals))}
stats["dist0_anchor_same_ct_cross_region"] = anchor

obs = {}
with open(BASE + r"\results\brain_bs_null_observed_pairs.csv", newline="", encoding="utf-8") as fo:
    for row in csv.DictReader(fo):
        obs[(row["cell_type"], frozenset([row["region_a"], row["region_b"]]))] = float(row["omega"])
mine = {(x["ct"], frozenset([x["ra"], x["rb"]])): x["omega_pp200"] for x in same_ct}
common_keys = set(obs) & set(mine)
val = {"n_common_pairs": len(common_keys), "n_obs_file": len(obs), "n_mine": len(mine)}
if common_keys:
    diffs = np.array([abs(obs[k] - mine[k]) for k in common_keys])
    ov = np.array([obs[k] for k in common_keys])
    mv = np.array([mine[k] for k in common_keys])
    val.update({"median_abs_diff": float(np.median(diffs)), "max_abs_diff": float(diffs.max()),
                "pearson_omega": float(np.corrcoef(ov, mv)[0, 1])})
stats["replication_validation_vs_brain_bs_null"] = val
print(f"validation: {val}", flush=True)

stats["runtime_sec"] = time.time() - t0
with open(BASE + r"\results\nc62_brain_lineage_stats.json", "w", encoding="utf-8") as fo:
    json.dump(stats, fo, ensure_ascii=False, indent=1)
print(json.dumps(stats, ensure_ascii=False, indent=1, default=str))
print(f"\nDONE in {time.time()-t0:.0f}s")
