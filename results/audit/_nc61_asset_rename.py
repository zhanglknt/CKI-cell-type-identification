#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Release v0.5.5 asset rename: CKI_Submission_v50_NC.zip -> CKI_Submission_NC.zip

The submission package dropped its stale v50 label on main (@144e5a6);
this swaps the Release v0.5.5 asset to the fresh, renamed zip with
readback sha256 verification, and patches the release body if it names
the old asset. Same urllib+PAT method as _v058_release_phase2.py.
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
RELEASE_ID = 401857516
ASSET_NAME = "CKI_Submission_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_NC.zip")

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

# 1. sanity: release exists, list assets
rel = api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}")
print(f"release {rel['id']} tag={rel['tag_name']} assets={[(a['id'], a['name']) for a in rel['assets']]}")
print("--- body ---")
print(rel["body"])
print("------------")

# 2. delete old asset(s)
for a in rel["assets"]:
    api(f"https://api.github.com/repos/{REPO}/releases/assets/{a['id']}", method="DELETE")
    print(f"deleted old asset {a['id']} ({a['name']})")

# 3. upload fresh asset under the new name
data = ZIP.read_bytes()
up = api(f"https://uploads.github.com/repos/{REPO}/releases/{RELEASE_ID}/assets?name={ASSET_NAME}",
         method="POST", data=data,
         headers={"Content-Type": "application/zip",
                  "Content-Length": str(len(data))})
new_id = up["id"]
print(f"uploaded asset id {new_id} ({up['name']}, {up['size']:,} B)")
assert up["size"] == ZIP.stat().st_size, "size mismatch on upload"

# 4. readback verify
body = api(f"https://api.github.com/repos/{REPO}/releases/assets/{new_id}",
           headers={"Accept": "application/octet-stream"}, raw=True)
rb_sha = hashlib.sha256(body).hexdigest()
print(f"readback: {len(body):,} B  sha256 {rb_sha}")
ok = rb_sha == local_sha and len(body) == ZIP.stat().st_size
print("READBACK MATCH" if ok else "READBACK MISMATCH")
if not ok:
    raise SystemExit(1)

# 5. patch release body if it names the old asset
if "CKI_Submission_v50_NC.zip" in rel["body"]:
    new_body = rel["body"].replace("CKI_Submission_v50_NC.zip", ASSET_NAME)
    api(f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}", method="PATCH",
        data=json.dumps({"body": new_body}).encode(),
        headers={"Content-Type": "application/json"})
    print("release body patched: asset name updated")
else:
    print("release body does not name the asset; no patch needed")
print("ASSET_ID", new_id)
