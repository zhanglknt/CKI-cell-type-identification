#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v54 release chain step 1: create GitHub Release v0.5.2 with the
freshly built CKI_Submission_v50_NC.zip asset (phase-1 fb782c9 state),
readback-verify sha256, then inspect the Zenodo webhook deliveries.

Adapted from _v052_release_create.py (same urllib+PAT method).
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.2"
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

BODY = """CKI package v0.5.2 with the nc53 final review round, the nc53 confirmation round (six-reviewer mean 8.08/10, 6/6 accept, zero majors), and the nc54 micro-fix round on top of the v49-v52 Nature Communications submission lineage.

Highlights since v0.5.1:
- nc53 final round closure: 5,151 full-inventory qualifier + SI Note 9 k_n-permutation-floor section; MS Table 1 note + Supplementary Fig. 14 legend (microglia 21.83 vs 1.30, P = 5.5e-14, AUC = 1.00); SI xlsx now 19 sheets (Tables 1-19); SI Note 1 DeLong AUC-interval methods, Note 8 reference-free composition fallback; Zenodo v0.5.1 version DOI written back.
- nc54 micro-fixes (all ground-truth adjudicated): GTEx liver sentence direction repair (P = 3.8e-5 attaches to GG<NN; medians coincide at ratio 1.03 with a heavier adjacent upper tail); tumor fold range 2.0-2.8; Fig. 4a k_f orientation explicit NN/TT; Table 5 caption ex-CC composition caliber -0.9% / -0.8% [-4.3, +2.5]; MS rho referent spelled out (non-parenchymal fraction versus k_n); 38% tagged as simulation; GTEx pair-independence caveat.
- Abstract trimmed to 196/200 words, restoring the proof-stage margin.
- Package/Dockerfile version face synchronized at v0.5.2.

Validation at tag: build assertions 221/221; manuscript verify 127/127, SI verify 121/121; XV8 63/63 (MAIN 4,999/5,000 words); pytest tests/ 29 passed; spot_check ALL PASS.

Zenodo concept DOI 10.5281/zenodo.20405458 (new version record archives automatically via the GitHub integration; the manuscript Code availability section cites the concept DOI, and the v0.5.2 version DOI is written back in the phase-2 commit on main).

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
                           "name": "v0.5.2: nc53 final + confirm rounds, nc54 micro-fixes (Nature Communications)",
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
