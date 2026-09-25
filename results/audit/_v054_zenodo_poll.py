#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v54 release chain step 2: poll Zenodo until the v0.5.2 version record
appears under concept DOI 10.5281/zenodo.20405458 (webhook accepted 202 at
2026-09-25T00:01:50Z; v0.5.1 took ~41 min queue delay).
Prints the new record id + version DOI when found. Timeout ~55 min."""
import json
import time
import urllib.parse
import urllib.request

CONCEPT = "10.5281/zenodo.20405458"
TARGET = "v0.5.2"
DEADLINE = time.time() + 55 * 60


def fetch():
    q = urllib.parse.urlencode({"q": f'conceptdoi:"{CONCEPT}"',
                                "sort": "mostrecent", "size": 10})
    req = urllib.request.Request("https://zenodo.org/api/records?" + q,
                                 headers={"User-Agent": "cki-release"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


n = 0
while time.time() < DEADLINE:
    n += 1
    try:
        d = fetch()
        hits = d.get("hits", {}).get("hits", [])
        versions = [(h["id"], h["metadata"].get("version"),
                     h["metadata"].get("publication_date")) for h in hits]
        print(f"[poll {n}] latest: {versions[:3]}", flush=True)
        for h in hits:
            if h["metadata"].get("version") == TARGET:
                doi = h.get("doi") or h["metadata"].get("doi")
                print("FOUND", h["id"], doi, flush=True)
                raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[poll {n}] fetch failed: {e}", flush=True)
    time.sleep(120)
print("TIMEOUT: v0.5.2 record not visible yet", flush=True)
raise SystemExit(1)
