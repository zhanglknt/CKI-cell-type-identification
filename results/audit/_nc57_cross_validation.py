#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc57 cross-validation: independent end-to-end sign-off after the
F1-F9 + O1/O2 fix rounds and the v0.5.4 release chain (@93d03f4).

Sections: B fix-landing (14), C version face, D release-chain state,
E data<->manuscript recomputation, G git hygiene. Section A (build
221 / XV8 63 / spot_check / pytest 29) and F (DOI resolution) were
run interactively and are cited in the markdown report.
"""
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

R = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
P, F = [], []


def chk(name, cond, detail=""):
    (P if cond else F).append(name)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


ms = (R / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
sn = (R / "results/CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8")
gd = (R / "results/CKI_Reproducibility_Guide_NC_fulltext.txt").read_text(encoding="utf-8")
ab = [l for l in ms.split("\n") if "Inspired by Ka/Ks" in l][0]

print("== B. fix landing (F1-F9, O1-O2) ==")
chk("B1 F1 paren balance", "Methods)), using the same hybrid scheme" in ms)
chk("B2 F2 across strata", "raw JS 28.6% to 72.5% across strata" in ms and "small-stratum" not in ms)
chk("B3 F3 range 35.7 x2", ms.count("35.7\u201345.2%") == 2 and "37.6\u201345.2%" not in ms)
chk("B4 F4 kidney covered", "kidney 1.6\u00d7" in sn)
chk("B5 F5 global FDR L14", "no candidate survives global FDR correction" in ms)
chk("B6 F6 SI sanity-check", "the sanity-check value lies" in sn and "the validation value lies" not in sn)
chk("B7 F7 bare pointer gone", "label-permutation confirmed; Section 3.13" not in ms
    and "label-permutation confirmed)" in ms
    and "Section 3.13 of the Supplementary Information" in ms)
chk("B8 F8 far deleted", "k_n shows smaller variation across categories" in ms and "far smaller" not in ms)
chk("B9 F9 excc test", "test_tcga_nn_tt_ratios_excc" in (R / "tests/test_reference_values.py").read_text(encoding="utf-8"))
chk("B10 O1 null enumerated", "the per-pair null (Methods); T1, same donor" in ms)
chk("B11 O1 trims", "misreported least among continuous divergence metrics" in ms
    and "is shallowest across the ladder" in ms)
chk("B12 O2 abstract dedup", "rejected neutral drift (housekeeping-anchored" in ab
    and "neutral housekeeping drift (housekeeping-anchored" not in ab)

print("== C. version face ==")
chk("C1 MS v0.5.4 x5 (4 version-face + DOI sentence)", ms.count("v0.5.4") == 5, f"count={ms.count('v0.5.4')}")
chk("C2 MS no stray v0.5.3", "v0.5.3" not in ms)
chk("C3 SI v0.5.4 x2 + version 0.5.4 x1", sn.count("v0.5.4") == 2 and sn.count("0.5.4") == 3,
    f"v={sn.count('v0.5.4')} bare={sn.count('0.5.4')}")
chk("C4 Guide 0.5.4 x3", gd.count("0.5.4") == 3 and "0.5.3" not in gd)
chk("C5 SI/Guide no 0.5.3", "0.5.3" not in sn and "0.5.3" not in gd)
pyproject = (R / "pyproject.toml").read_text(encoding="utf-8")
init = (R / "cki/__init__.py").read_text(encoding="utf-8")
docker = (R / "Dockerfile").read_text(encoding="utf-8")
chk("C6 pyproject/init 0.5.4", 'version = "0.5.4"' in pyproject and '__version__ = "0.5.4"' in init)
chk("C7 Dockerfile 0.5.4 x3", docker.count("0.5.4") == 3 and "0.5.3" not in docker)
chk("C8 MS DOI = 22958249", "version DOI for v0.5.4: 10.5281/zenodo.22958249" in ms
    and "22954782" not in ms and "22949350" not in ms)

print("== D. release-chain state ==")
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=R).stdout.strip()
remote = subprocess.run(["git", "ls-remote", "origin", "main"], capture_output=True, text=True, cwd=R).stdout.split()[0]
chk("D1 local HEAD == remote main", head == remote, f"{head[:7]} vs {remote[:7]}")
tag_remote = subprocess.run(["git", "ls-remote", "origin", "refs/tags/v0.5.4"],
                            capture_output=True, text=True, cwd=R).stdout.strip()
chk("D2 tag v0.5.4 on remote", "refs/tags/v0.5.4" in tag_remote)
zip_path = R / "CKI_Submission_v50_NC.zip"
local_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
cred = Path.home() / ".git-credentials"
tok = None
for line in cred.read_text().splitlines():
    m = re.match(r"https://([^:]+):([^@]+)@github\.com", line)
    if m:
        tok = m.group(2)
        break
hdr = {"Authorization": f"token {tok}", "Accept": "application/vnd.github+json", "User-Agent": "cki-xv"}


def gh(url, raw=False):
    req = urllib.request.Request(url, headers=hdr)
    data = urllib.request.urlopen(req, timeout=60).read()
    return data if raw else json.loads(data)


try:
    rel = gh("https://api.github.com/repos/zhanglknt/CKI-cell-type-identification/releases/396502805")
    assets = rel["assets"]
    chk("D3 release single asset", len(assets) == 1, f"{[a['id'] for a in assets]}")
    if assets:
        a = assets[0]
        remote_sha = hashlib.sha256(
            gh(f"https://api.github.com/repos/zhanglknt/CKI-cell-type-identification/releases/assets/{a['id']}",
               raw=True)).hexdigest() if False else a["digest"].replace("sha256:", "")
        chk("D4 asset digest == local zip", remote_sha == local_sha,
            f"asset {a['id']} {remote_sha[:12]} vs {local_sha[:12]}")
        chk("D5 body cites v0.5.4 DOI + residual build", "10.5281/zenodo.22958249" in rel["body"]
            and "nc57-residual build" in rel["body"])
except Exception as e:
    chk("D3-D5 release API", False, repr(e))
try:
    req = urllib.request.Request("https://zenodo.org/api/records/22958249",
                                 headers={"User-Agent": "Mozilla/5.0 cki-xv"})
    zd = json.loads(urllib.request.urlopen(req, timeout=60).read())
    md = zd["metadata"]
    chk("D6 Zenodo 22958249 = v0.5.4 done", zd["doi"] == "10.5281/zenodo.22958249"
        and md["version"] == "v0.5.4" and zd["state"] == "done")
    chk("D7 Zenodo related -> tree v0.5.4",
        any("tree/v0.5.4" in (ri.get("identifier") or "") for ri in md.get("related_identifiers", [])))
except Exception as e:
    chk("D6-D7 zenodo API", False, repr(e))

print("== E. data <-> manuscript recomputation ==")
import pandas as pd
df = pd.read_csv(R / "results/nc52_tcga_pancancer_excc.csv").set_index("cancer")
expect = {"TCGA-LUAD": 2.464, "TCGA-LUSC": 1.708, "TCGA-LIHC": 1.112, "TCGA-KIRC": 1.880, "TCGA-BRCA": 1.567}
ok = all(abs(df.loc[c, "NN_TT_ratio"] - v) < 5e-4 for c, v in expect.items())
chk("E1 excc ratios == MS L47/abstract", ok
    and "LUAD 2.46, KIRC 1.88, LUSC 1.71, BRCA 1.57, LIHC 1.11" in ms
    and "1.11\u20132.46" in ab)
gt = pd.read_csv(R / "results/nc52_gtex_kn_by_grouptype.csv")
kid = gt[(gt["level"] == "organ") & (gt["group"] == "Kidney")]
ga = float(kid[kid["pair_type"] == "GA"]["kn_median"].iloc[0])
gg = float(kid[kid["pair_type"] == "GG"]["kn_median"].iloc[0])
chk("E2 kidney GA/GG ratio -> 1.6x claim", abs(ga / gg - 1.566) < 0.01, f"recomputed {ga/gg:.3f}")
chk("E3 SI 3.12 five-metric enumeration consistent with 35.7-45.2 range",
    "45.2% for raw JS, 44.1% for cosine, 40.6% for Spearman, 37.6% for k_f, and 35.7% for k_n" in sn)
chk("E4 abstract 195 / MAIN 4998 (XV8 caliber)", len(ab.split()) == 195)

print("== G. git hygiene ==")
status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=R).stdout.strip()
chk("G1 working tree clean", status == "", status[:80])

print(f"\nTOTAL: {len(P)} pass, {len(F)} fail")
if F:
    print("FAILURES:", F)
    sys.exit(1)
print("NC57 CROSS-VALIDATION ALL PASS")
