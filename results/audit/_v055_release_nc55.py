#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc55 release chain: replace the Release v0.5.2 asset (id 587262273,
phase-2 build) with the nc55 review-fix build (main f53a459), readback-
verify sha256, and append a body note recording the tag divergence
(tag v0.5.2 = fb782c9 predates the nc55 mechanical fixes on main).
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
RELEASE_ID = 396170102
OLD_ASSET_ID = 587262273
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

NOTE = (
    "\n\n**Update 2026-09-25 (nc55 blind-review fixes):** asset refreshed to the "
    "nc55 review-fix build (main f53a459): spot_check.py rewritten to the current "
    "ex-CC headline caliber (46/46 PASS, verified on a clean git archive), "
    "reproducibility-guide verification pointers repaired, 8 verification input "
    "files now git-tracked, manuscript wording softened per review (GTEx/floor/"
    "attenuation; ref 19 corrected to Batiuk et al. 2020). Note: tag v0.5.2 "
    "(fb782c9, archived as Zenodo 10.5281/zenodo.22949350) predates these "
    "mechanical fixes; they are candidates for a v0.5.3 tag."
)

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
        except Exception as e:
            last = e
            print(f"  attempt {attempt + 1} failed: {e}; retrying")
            time.sleep(3)
    raise last


local_sha = hashlib.sha256(ZIP.read_bytes()).hexdigest()
print(f"local zip: {ZIP.stat().st_size:,} B  sha256 {local_sha}")

rel = api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}")
print(f"release {rel['id']} tag={rel['tag_name']} assets={[a['id'] for a in rel['assets']]}")

api(f"https://api.github.com/repos/{REPO}/releases/assets/{OLD_ASSET_ID}", method="DELETE")
print(f"deleted old asset {OLD_ASSET_ID}")

data = ZIP.read_bytes()
up = api(f"https://uploads.github.com/repos/{REPO}/releases/{RELEASE_ID}/assets?name={ASSET_NAME}",
         method="POST", data=data,
         headers={"Content-Type": "application/zip",
                  "Content-Length": str(len(data))})
new_id = up["id"]
print(f"uploaded asset id {new_id} ({up['size']:,} B)")

body = api(f"https://api.github.com/repos/{REPO}/releases/assets/{new_id}",
           headers={"Accept": "application/octet-stream"}, raw=True)
rb_sha = hashlib.sha256(body).hexdigest()
print(f"readback: {len(body):,} B  sha256 {rb_sha}")
ok = rb_sha == local_sha and len(body) == ZIP.stat().st_size
print("READBACK MATCH" if ok else "READBACK MISMATCH")
if not ok:
    raise SystemExit(1)

api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}", method="PATCH",
    data=json.dumps({"body": rel["body"] + NOTE}).encode(),
    headers={"Content-Type": "application/json"})
print("release body patched with nc55 note")
print("ASSET_ID", new_id)
