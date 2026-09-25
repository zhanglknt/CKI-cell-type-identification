#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v54 release chain phase-2: Zenodo v0.5.2 record is live
(22949350 / 10.5281/zenodo.22949350), the manuscript Code availability
now cites the version DOI, and the submission zip has been rebuilt.

This script replaces the Release v0.5.2 asset (old id 587110399,
phase-1 state without the version DOI) with the fresh zip, readback-
verifies sha256, and patches the release body to cite the version DOI.
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
RELEASE_ID = 396170102
OLD_ASSET_ID = 587110399
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")
VERSION_DOI = "10.5281/zenodo.22949350"

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

# 1. sanity: release + old asset exist
rel = api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}")
print(f"release {rel['id']} tag={rel['tag_name']} assets={[a['id'] for a in rel['assets']]}")

# 2. delete old asset
api(f"https://api.github.com/repos/{REPO}/releases/assets/{OLD_ASSET_ID}", method="DELETE")
print(f"deleted old asset {OLD_ASSET_ID}")

# 3. upload fresh asset
data = ZIP.read_bytes()
up = api(f"https://uploads.github.com/repos/{REPO}/releases/{RELEASE_ID}/assets?name={ASSET_NAME}",
         method="POST", data=data,
         headers={"Content-Type": "application/zip",
                  "Content-Length": str(len(data))})
new_id = up["id"]
print(f"uploaded asset id {new_id} ({up['size']:,} B)")

# 4. readback verify
body = api(f"https://api.github.com/repos/{REPO}/releases/assets/{new_id}",
           headers={"Accept": "application/octet-stream"}, raw=True)
rb_sha = hashlib.sha256(body).hexdigest()
print(f"readback: {len(body):,} B  sha256 {rb_sha}")
ok = rb_sha == local_sha and len(body) == ZIP.stat().st_size
print("READBACK MATCH" if ok else "READBACK MISMATCH")
if not ok:
    raise SystemExit(1)

# 5. patch release body: cite the version DOI now that phase-2 is done
new_body = rel["body"].replace(
    "the manuscript Code availability section cites the concept DOI, and the v0.5.2 version DOI is written back in the phase-2 commit on main",
    f"the manuscript Code availability section cites the concept DOI and the v0.5.2 version DOI {VERSION_DOI} (phase-2 write-back complete; asset refreshed to the phase-2 build)")
api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}", method="PATCH",
    data=json.dumps({"body": new_body}).encode(),
    headers={"Content-Type": "application/json"})
print("release body patched with version DOI")
print("ASSET_ID", new_id)
