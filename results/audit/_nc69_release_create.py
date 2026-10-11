#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nc69 release chain step 1: create GitHub Release v0.5.6 with the
freshly built CKI_Submission_NC.zip asset, verify size (+sha256
readback when the network allows), then inspect the Zenodo webhook
deliveries.

Adapted from _v058_release_create.py (same urllib+PAT method).
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = "zhanglknt/CKI-cell-type-identification"
TAG = "v0.5.6"
ASSET_NAME = "CKI_Submission_NC.zip"
ZIP = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\CKI_Submission_NC.zip")

BODY = """CKI package v0.5.6 with the nc68 scoped-theory round and the nc69 five-reviewer panel-fix round on top of v0.5.5, in the v49-v52 Nature Communications submission lineage.

Highlights since v0.5.5:
- SI Note 20 (a scoped theoretical framework for omega: generative model, Lemma 1-2, conditions C1-C4, Propositions 3-5, and what the HK denominator adds) plus Supplementary Fig. 19; notebooks/85 theory-diagnostics script (2,937 real pairs) - the script was missing from the v0.5.5 tag, which this release fixes.
- nc69 panel fixes: Note 20 E(iii) FPR misattribution rewritten (denominator gain anchored to raw JS/cosine 0.55-1.00 with honest k_f-only 0.007-0.020 and N2-swap disclosures); SI figure legends header 1-18 -> 1-19; abstract pseudo-replicated P replaced by the design-matched block-shuffle caliber (MGE P = 0.001, upper-layer IT P = 0.014, thalamic P = 0.163); alpha-baseline chain downgraded to same-order with the panel-size factor stated; small-cluster CI coverage caveat; estimand post-selection qualifier; Proposition 5 / Note 4 aggregation reconciliation; TCGA permutation P precision (KRAS-WT <= 0.001, EGFR-WT >= 0.28); SI roadmap paragraph.
- Code availability now cites the Zenodo concept DOI (10.5281/zenodo.20405458, always resolving to the latest archived version) instead of a per-version DOI.
- Word budget: MAIN 4,994/5,000 (incl subheadings), abstract 190/200, Methods 2,942/3,000 (XV8 caliber).

Validation at tag: build assertions 234/234; XV8 64/64; manuscript/SI/CL+Guide verifiers green; pytest 29 passed; 23/23 independent cross-checks of the panel fixes against the fresh DOCX.

Zenodo concept DOI 10.5281/zenodo.20405458 (a new version record archives automatically via the GitHub integration).

Attachment: CKI_Submission_NC.zip (submission package: manuscript, cover letter, reproducibility guide, supplement, tables xlsx, figures; MANIFEST inside)."""

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
                           "name": "v0.5.6: nc68 scoped theory + nc69 panel fixes (Note 20, Supp Fig 19, Nature Communications)",
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

# 3. readback verify (network may fail; size match above is the fallback)
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
