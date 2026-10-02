#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v58 release chain step 1: create GitHub Release v0.5.5 with the
freshly built CKI_Submission_v50_NC.zip asset (phase-1 state),
verify size (+sha256 readback when the proxy allows), then inspect
the Zenodo webhook deliveries.

Adapted from _v057_release_create.py (same urllib+PAT method).
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.5"
ASSET_NAME = "CKI_Submission_v50_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_v50_NC.zip")

BODY = """CKI package v0.5.5 with the nc58 v5 first-author revision round on top of v0.5.4 (nc57 final-review fixes, six-reviewer mean 8.33/10, 6/6 accept) in the v49-v52 Nature Communications submission lineage.

Highlights since v0.5.4 (all first-author v5 suggestions adopted; no substantive errors found):
- MS: all tracked-change text edits accepted (abstract rewritten, 168/200 words; Introduction restructured; the three defensive Results subsections soft-merged into one "Perturbation-response boundaries and fixed-panel ablation" section with zero evidence loss; KRAS/EGFR and candidate-screen clarifications).
- Figures: every panel replaced with the first-author redrawn artwork; figure 4 mechanically patched with the missing C/D panel labels (Arial Bold 9 pt, NC panel-label requirement; [10] cites Fig. 4c, d).
- Supplementary figures: fully monotone renumbering by main-text first-citation order (1-14); the microglia sanity check moves from SF14 to SF3 and gains a UMAP panel (88,494 microglia vs 3,344 CNS macrophages, precomputed embedding) alongside the omega-distribution and per-metric AUC panels.
- Word budget: MAIN 4,994/5,000 (incl subheadings), abstract 168/200, Methods 2,936/3,000 (XV8 caliber).

Validation at tag: build assertions 218/218; manuscript verify 127/127, SI verify 121/121, CL+Guide verify 41/41; XV8 63/63; pytest tests/ 29 passed.

Zenodo concept DOI 10.5281/zenodo.20405458 (new version record archives automatically via the GitHub integration; the manuscript Code availability section cites the concept DOI and the v0.5.4 version DOI 10.5281/zenodo.22958249; the v0.5.5 version DOI is written back in the phase-2 commit on main).

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
                           "name": "v0.5.5: nc58 v5 first-author round (figures replaced, monotone SF renumber, Nature Communications)",
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
size_ok = up["size"] == ZIP.stat().st_size
print("SIZE MATCH" if size_ok else "SIZE MISMATCH")
if not size_ok:
    raise SystemExit(1)

# 3. readback verify (proxy may 502; size match above is the fallback)
try:
    body = api(f"https://api.github.com/repos/{REPO}/releases/assets/{new_id}",
               headers={"Accept": "application/octet-stream"}, raw=True)
    rb_sha = hashlib.sha256(body).hexdigest()
    print(f"readback: {len(body):,} B  sha256 {rb_sha}")
    print("READBACK MATCH" if rb_sha == local_sha else "READBACK MISMATCH")
except Exception as e:
    print(f"readback unavailable ({e}); relying on SIZE MATCH")

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
