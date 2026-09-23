#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v51 release chain: replace Release v0.5.0 asset CKI_Submission_v50_NC.zip
with the freshly built zip, then readback-verify sha256.

Method per repo memory: python urllib (curl file-upload broken on Windows);
PAT from ~/.git-credentials (store helper); DELETE via urllib method override.
"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.0"
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

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
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req) as r:
        body = r.read()
        if raw:
            return body
        return json.loads(body) if body.strip() else {}

local_sha = hashlib.sha256(ZIP.read_bytes()).hexdigest()
print(f"local zip: {ZIP.stat().st_size:,} B  sha256 {local_sha}")

# 1. find release + existing asset
rel = api(f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}")
rid = rel["id"]
print(f"release {TAG}: id {rid}")
old = [a for a in rel["assets"] if a["name"] == ASSET_NAME]
for a in old:
    print(f"deleting old asset {a['id']} ({a['size']:,} B, sha unknown)")
    api(f"https://api.github.com/repos/{REPO}/releases/assets/{a['id']}", method="DELETE")

# 2. upload new asset
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
print(f"ASSET_ID={new_id}")
