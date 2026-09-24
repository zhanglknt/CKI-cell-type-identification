#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v52 release chain step 1: create GitHub Release v0.5.1 with the
freshly built CKI_Submission_v50_NC.zip asset, readback-verify sha256,
then inspect the Zenodo webhook deliveries for the release event.

Method per repo memory: python urllib (curl file-upload broken on Windows);
PAT from ~/.git-credentials (store helper). Retry on transient 502/SSL EOF.
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.1"
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

BODY = """CKI package v0.5.1 with the nc52 expert-panel revision round (fixes #13-#19) on top of the v49/v50 Nature Communications submission lineage.

Highlights of nc52:
- ex-CC default cohort for all TCGA analyses (3,535 samples, 34,828 pairs; 32 ILSBio cell-line aliquots excluded): LIHC NN/TT 1.11 [0.94, 1.30] (four of five), composition pooled -0.9% [-4.3, +2.5], LIHC +44.1%, Spearman rho = 0.380.
- Two-stage population-resampled bootstrap 95% CI for the omega calibration constant: 7.70 [6.38, 9.82] (B = 5,000); legacy pseudo-replicate CI retired.
- LIHC Cox model recomputed with R survival::coxph (stage categorical): HR/SD 1.08 [0.88, 1.33], P = 0.467; cox.zph M2 GLOBAL P = 0.023.
- Tabula Sapiens entry-clustered bootstrap 95% CIs for metric correlations (B = 5,000); P < 1e-145 caliber retired.
- Brain donor-bootstrap combined-control gradient 3.66 promoted to the primary caliber.
- Severity ex-CC: LIHC Edmondson G1-G4 k_f 78.8/75.8/77.6/72.3 (JT P = 8.4e-12).

Validation: build assertions 221/221; manuscript verify 117, SI verify 109, CL+Guide 39; spot_check 46 ALL PASS; pytest 29 passed; XV8 63/63. CI green on Python 3.10-3.14.

Package change since v0.5.0: cki/preprocess.py densify import fix (F821 lint).

Zenodo concept DOI 10.5281/zenodo.20405458 (new version record archives automatically via the GitHub integration).

Attachment: CKI_Submission_v50_NC.zip (nc52 submission package: manuscript, cover letter, reproducibility guide, supplement, tables xlsx, figures; MANIFEST inside)."""

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
                           "name": "v0.5.1: nc52 expert-panel revision (Nature Communications)",
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
