# -*- coding: utf-8 -*-
"""
nc78 P0 (cancer reviewer Q2): RIN (RNA Integrity Number) as a competing
explanation for housekeeping divergence.

The reviewer noted that TCGA samples carry RIN / ischemic-time annotations
for a subset of cases, and asked whether per-sample k_n or pair-level k_n
correlates with RIN -- a competition explanation listed in the manuscript's
own Section 3.6 but never tested.

Design:
  1. GDC API (requires the local socks5 proxy, socks5h://127.0.0.1:10808;
     curl exit 7 means the proxy is not running). The RIN field name is
     discovered at runtime from the GDC _mapping endpoint (biospecimen
     layer), so the script does not hardcode a possibly-absent field.
  2. Pull sample-level RIN for all samples of the five cancers
     (BRCA/KIRC/LIHC/LUAD/LUSC), cache the raw JSON under
     data/tcga/gdc_rin_cache.json (re-runs use the cache, no re-download).
  3. Per-sample k_n/k_f/omega: aggregated from the authoritative pair table
     results/tcga_linear_norm_v44_all_pairs.csv (all pair types; each
     sample's mean over the pairs it participates in), split by sample
     class (primary tumor vs solid-tissue normal, barcode positions 14-15).
  4. Tests:
     (a) per-sample Spearman correlation of k_n (and k_f, omega) with RIN,
         within cancer x sample-class strata;
     (b) pair-level: pair k_n ~ min-RIN of the two endpoints (the limiting
         member), Spearman, within cancer x pair_type strata;
     (c) coverage report: fraction of samples with RIN per cancer/class;
         if coverage is low, results are reported for the available subset
         with the coverage caveat stated.
  5. Outputs: results/nc78_gdc_rin.csv / .txt (+ cached JSON).

Seed: none (correlations are deterministic).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
CACHE = ROOT / "data" / "tcga" / "gdc_rin_cache.json"
OUT_CSV = ROOT / "results" / "nc78_gdc_rin.csv"
OUT_TXT = ROOT / "results" / "nc78_gdc_rin.txt"
PROXY = "socks5h://127.0.0.1:10808"
GDC = "https://api.gdc.cancer.gov"
CANCERS = ["TCGA-BRCA", "TCGA-KIRC", "TCGA-LIHC", "TCGA-LUAD", "TCGA-LUSC"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def curl_json(url):
    """curl direct first, socks5 proxy as fallback; abort loudly on failure."""
    for cmd in (["curl", "-sS", "--max-time", "60", url],
                ["curl", "-sS", "--max-time", "60", "-x", PROXY, url]):
        proc = subprocess.run(cmd, capture_output=True, timeout=90)
        if proc.returncode == 0:
            return json.loads(proc.stdout.decode("utf-8"))
    sys.exit(f"curl failed (direct and proxy; exit {proc.returncode}): "
             f"{proc.stderr.decode(errors='replace')}")

# ---- 1. pull RIN from the cases endpoint (nested biospecimen layer) ----
# GDC data model (verified 2026-11-15 via _mapping endpoints): RIN lives at
# cases -> samples -> portions -> analytes -> rna_integrity_number. It is NOT
# a direct property of the samples/aliquots/analytes endpoints.
RIN_FIELD = ("samples.submitter_id,"
             "samples.portions.analytes.rna_integrity_number")

def pull_cancer(ca):
    got = {}
    size, from_ = 1000, 0
    while True:
        q = (f'{GDC}/cases?filters=%7B%22op%22%3A%22and%22%2C%22content'
             f'%22%3A%5B%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field'
             f'%22%3A%22project.project_id%22%2C%22value%22%3A%5B%22{ca}'
             f'%22%5D%7D%7D%5D%7D'
             f'&fields={RIN_FIELD}&format=json&size={size}&from={from_}')
        js = curl_json(q)
        hits = js["data"]["hits"]
        for h in hits:
            for smp in h.get("samples", []) or []:
                sid = smp.get("submitter_id")
                vals = []
                for por in smp.get("portions", []) or []:
                    for ana in por.get("analytes", []) or []:
                        v = ana.get("rna_integrity_number")
                        if v is not None:
                            try:
                                vals.append(float(v))
                            except (TypeError, ValueError):
                                pass
                if vals:
                    # analyte-level replicates: keep the per-sample mean
                    got[sid] = sum(vals) / len(vals)
        if len(hits) < size:
            break
        from_ += size
    return got

if CACHE.exists():
    log(f"using cached RIN pull: {CACHE}")
    rin_rows = json.load(open(CACHE))
else:
    rin_rows = {}
    for ca in CANCERS:
        got = pull_cancer(ca)
        rin_rows[ca] = got
        log(f"{ca}: {len(got)} samples with RIN")
        time.sleep(0.5)
    CACHE.write_text(json.dumps(rin_rows), encoding="utf-8")
    log(f"cached raw pull -> {CACHE}")

rin = {}
for ca, d in rin_rows.items():
    for sid, v in d.items():
        rin[sid] = v
# GDC sample submitter_ids carry the vial letter (16 chars, e.g.
# "TCGA-BC-4072-01A"); the expression-matrix pair table uses 15-char
# sample barcodes without the vial ("TCGA-BC-4072-01"). Match on the
# 15-char stem; multiple vials of one sample are averaged.
_vial = {}
for sid, v in rin.items():
    _vial.setdefault(sid[:15], []).append(v)
rin15 = {k: sum(vs) / len(vs) for k, vs in _vial.items()}
log(f"total samples with RIN: {len(rin)} (15-char stems: {len(rin15)})")

# ---- 2. per-sample stats from the authoritative pair table ----
pairs = pd.read_csv(PAIRS)
pairs = pairs[pairs.cancer.isin(CANCERS)]
long = pd.concat([
    pairs[["cancer", "pair_type", "sample_a", "kn", "kf", "omega_floor"]]
        .rename(columns={"sample_a": "sample", "omega_floor": "omega"}),
    pairs[["cancer", "pair_type", "sample_b", "kn", "kf", "omega_floor"]]
        .rename(columns={"sample_b": "sample", "omega_floor": "omega"}),
], ignore_index=True)
per_s = long.groupby(["cancer", "sample"]).agg(
    kn=("kn", "mean"), kf=("kf", "mean"), omega=("omega", "mean")
).reset_index()
per_s["cls"] = np.where(per_s["sample"].str[13:15] == "01", "tumor",
                np.where(per_s["sample"].str[13:15] == "11", "normal", "other"))
per_s["rin"] = per_s["sample"].str[:15].map(rin15)

# pair-level min-RIN
pairs["rin_a"] = pairs["sample_a"].str[:15].map(rin15)
pairs["rin_b"] = pairs["sample_b"].str[:15].map(rin15)
pairs["rin_min"] = pairs[["rin_a", "rin_b"]].min(axis=1)

# ---- 3. coverage + correlations ----
from scipy.stats import spearmanr

rows = []
cov = (per_s.assign(has=per_s.rin.notna())
       .groupby(["cancer", "cls"]).agg(n=("sample", "size"),
                                       n_rin=("has", "sum")).reset_index())
cov["coverage"] = cov.n_rin / cov.n
log("\ncoverage (expression samples with RIN):")
log(cov.to_string(index=False))
for _, r in cov.iterrows():
    rows.append({"item": "coverage", "cancer": r.cancer, "stratum": r.cls,
                 "metric": "n/n_rin/coverage",
                 "value": f"{r.n}/{r.n_rin}/{r.coverage:.3f}"})

for (ca, cls), d in per_s[per_s.rin.notna()].groupby(["cancer", "cls"]):
    if len(d) < 20:
        continue
    for m in ["kn", "kf", "omega"]:
        rho, p = spearmanr(d["rin"], d[m])
        rows.append({"item": "per_sample", "cancer": ca, "stratum": cls,
                     "metric": f"rho_{m}_vs_RIN",
                     "value": f"{rho:+.3f} (P={p:.3g}, n={len(d)})"})
        log(f"per-sample {ca} {cls}: rho({m}, RIN) = {rho:+.3f} "
            f"P={p:.3g} (n={len(d)})")

for (ca, pt), d in pairs[pairs.rin_min.notna()].groupby(["cancer",
                                                         "pair_type"]):
    if len(d) < 20:
        continue
    for m in ["kn", "kf", "omega_floor"]:
        rho, p = spearmanr(d["rin_min"], d[m])
        rows.append({"item": "pair_minRIN", "cancer": ca, "stratum": pt,
                     "metric": f"rho_{m}_vs_minRIN",
                     "value": f"{rho:+.3f} (P={p:.3g}, n={len(d)})"})
        log(f"pair {ca} {pt}: rho({m}, minRIN) = {rho:+.3f} "
            f"P={p:.3g} (n={len(d)})")

# ---- 4. decisive control: NN/TT k_n reversal within RIN-high pairs ----
# If RNA degradation drove the housekeeping reversal, the TT/NN k_n ratio
# should collapse when both endpoints have high RIN (>= 7, the standard
# RNA-Seq quality threshold).
log("\nRIN-high (both endpoints >= 7) reversal control:")
for ca in CANCERS:
    d = pairs[(pairs.cancer == ca) & pairs.rin_a.notna()
              & pairs.rin_b.notna()]
    hi = d[(d.rin_a >= 7) & (d.rin_b >= 7)]
    nn_hi = hi[hi.pair_type == "NN"]["kn"].mean()
    tt_hi = hi[hi.pair_type == "TT"]["kn"].mean()
    nn_all = d[d.pair_type == "NN"]["kn"].mean()
    tt_all = d[d.pair_type == "TT"]["kn"].mean()
    log(f"  {ca}: RIN-high n_NN={int((hi.pair_type == 'NN').sum())} "
        f"n_TT={int((hi.pair_type == 'TT').sum())}; "
        f"NN/TT k_n ratio all-RIN {nn_all / tt_all:.3f} "
        f"-> RIN-high {nn_hi / tt_hi:.3f}")
    rows.append({"item": "rin_high_reversal", "cancer": ca,
                 "stratum": "NN_over_TT_kn_ratio",
                 "metric": "all_RIN_vs_RIN_high",
                 "value": f"{nn_all / tt_all:.3f} -> {nn_hi / tt_hi:.3f} "
                          f"(n_NN={int((hi.pair_type == 'NN').sum())}, "
                          f"n_TT={int((hi.pair_type == 'TT').sum())})"})

pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
log(f"\nsaved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
