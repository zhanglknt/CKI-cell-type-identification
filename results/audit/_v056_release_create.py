#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v56 release chain step 1: create GitHub Release v0.5.3 with the
freshly built CKI_Submission_v50_NC.zip asset (phase-1 00e3652 state),
readback-verify sha256, then inspect the Zenodo webhook deliveries.

Adapted from _v054_release_create.py (same urllib+PAT method).
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.3"
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

BODY = """CKI package v0.5.3 with the nc55 blind-review fix round (six-reviewer mean 7.92/10, 3 accept + 3 minor revisions, zero outstanding majors) and the nc56 proof-ledger round (all deferred proof items resolved) on top of the v49-v52 Nature Communications submission lineage.

Highlights since v0.5.2:
- nc55 fix round: ref 19 corrected (Tan -> Batiuk 2020) and citation-group assertions re-based to 72; data-availability single-xlsx pointer; GTEx wording softened (net-zero words); permutation-floor "essentially"; KIRC 754->750 bridge in SI; spot_check reads the ex-CC CSVs; guide pointer refresh.
- nc56 proof round (30 generator edits, word-budget neutral): abstract GTEx sentence softened with organ qualifier ("GTEx references in lung, liver, and breast are consistent with tumor-specific elevation"); housekeeping-anchored FPR qualifier; (k_n-dominated) gradient tag; omega_cal precision moved upfront (one-significant-digit resolution) and downgraded to "indicative, dataset-relative" in Discussion; four-tier drift ladder harmonized with the Fig. 3a legend; global/within-family FDR qualifiers; Fig. 3a pair counts, Fig. 3c T1 28.6% contrast, Fig. 5d "conserved", Fig. 14 "sanity-check value"; SI Note 8 cross-cohort tolerance sentence (1.8-2.3x, tentative); SI Note 3 calibration-relevant wording; Note 14 Python 3.14; Guide 5.13a pointer; pyproject description aligned with the CKI name.
- Package/Dockerfile version face synchronized at v0.5.3.

Validation at tag: build assertions 221/221; manuscript verify 127/127, SI verify 121/121; XV8 63/63 (abstract 196/200 words; MAIN 4,999/5,000 words); pytest tests/ 29 passed; spot_check ALL PASS.

Zenodo concept DOI 10.5281/zenodo.20405458 (new version record archives automatically via the GitHub integration; the manuscript Code availability section cites the concept DOI, and the v0.5.3 version DOI is written back in the phase-2 commit on main).

Attachment: CKI_Submission_v50_NC.zip (submission package: manuscript, cover letter, reproducibility guide, supplement, tables xlsx, figures; MANIFEST inside)."""

cred = Path.home() / ".git-credentials"
token = None
for line in cred.read_text().splitlines():
    m = re.match(r"https://([^:]+):([^@]+)@github\.com", line)
    if m:
        token = m.group(2)
        break
if not token:
    raise SystemExit("no github PAT in ~/.git-credentials")


def api(url, method="GET", data=None, headers=None, raw=False):
    h = {"Authorization": f"token {token}", "User-Agent": "cki-release",
         "Accept": "application/vnd.github+json"}
    if headers:
        h.update(headers)
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers=h, method=method)
            with urllib.request.urlopen(req) as r:
                body = r.read()
                if raw:
                    return body
                return json.loads(body) if body.strip() else {}
        except Exception as e:  # transient 502 / SSL EOF
            last = e
            print(f"  attempt {attempt + 1} failed: {e}; retrying")
            time.sleep(3)
    raise last


local_sha = hashlib.sha256(ZIP.read_bytes()).hexdigest()
print(f"local zip: {ZIP.stat().st_size:,} B  sha256 {local_sha}")

# 1. create release
rel = api(f"https://api.github.com/repos/{REPO}/releases", method="POST",
          data=json.dumps({"tag_name": TAG,
                           "name": "v0.5.3: nc55 blind-review fixes + nc56 proof-ledger closure (Nature Communications)",
                           "body": BODY, "draft": False, "prerelease": False}).encode(),
          headers={"Content-Type": "application/json"})
rid = rel["id"]
print(f"created release id {rid} for tag {TAG}: {rel['html_url']}")

# 2. upload asset
data = ZIP.read_bytes()
up = api(f"https://uploads.github.com/repos/{REPO}/releases/{rid}/assets?name={ASSET_NAME}",
         method="POST", data=data,
         headers={"Content-Type": "application/zip",
                  "Content-Length": str(len(data))})
new_id = up["id"]
print(f"uploaded asset id {new_id} ({up['size']:,} B)")

# 3. readback verify
body = api(f"https://api.github.com/repos/{REPO}/releases/assets/{new_id}",
           headers={"Accept": "application/octet-stream"}, raw=True)
rb_sha = hashlib.sha256(body).hexdigest()
print(f"readback: {len(body):,} B  sha256 {rb_sha}")
ok = rb_sha == local_sha and len(body) == ZIP.stat().st_size
print("READBACK MATCH" if ok else "READBACK MISMATCH")
if not ok:
    raise SystemExit(1)

# 4. inspect repo hooks -> zenodo deliveries
time.sleep(10)
hooks = api(f"https://api.github.com/repos/{REPO}/hooks")
zen = [hk for hk in hooks if "zenodo" in hk.get("config", {}).get("url", "").lower()]
for hk in zen:
    print(f"zenodo hook id {hk['id']} url {hk['config']['url']} active={hk['active']}")
    dels = api(f"https://api.github.com/repos/{REPO}/hooks/{hk['id']}/deliveries?per_page=5")
    for d in dels:
        print(f"  delivery {d['id']} event={d['event']} status={d['status']} code={d['status_code']} at {d['delivered_at']}")
print("RELEASE_ID", rid)
print("ASSET_ID", new_id)
