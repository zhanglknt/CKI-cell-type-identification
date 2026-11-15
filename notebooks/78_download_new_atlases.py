"""
Download helper for the A/C/D atlas datasets.
============================================================
Direct connection is the default (CELLxGENE reachable at ~5.7 MB/s
without proxy as of 2026-10-09). Use --proxy to route through the
local socks proxy (socks5h://127.0.0.1:10808) — needed for figshare
(api.figshare.com returns 403 direct from this network).

Modes:
  --check   resolve dataset titles/sizes/URLs only (no download)
  A         Siletti per-supercluster Neurons h5ad -> data/brain/neurons/
            (CELLxGENE collection 283d65eb-dd53-496d-adb7-7570c7caa443;
             the 'All neurons' file is 32.9 GB — instead we fetch the
             per-supercluster slices listed in NEURON_SUPERCLUSTERS)
  C         Tabula Muris Senis FACS h5ad -> data/tms/
            (figshare article 8273102; needs --proxy on this network)
  D         SEA-AD (MTG snRNA)     -> data/sea_ad/
            (CELLxGENE collection resolved by title search "SEA-AD")

Usage:
  python notebooks/78_download_new_atlases.py --check
  python notebooks/78_download_new_atlases.py A
  python notebooks/78_download_new_atlases.py C --proxy
"""

import sys, os, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SILETTI_COLLECTION = "283d65eb-dd53-496d-adb7-7570c7caa443"
CXG_API = "https://api.cellxgene.cziscience.com/curation/v1"
TMS_FIGSHARE_ARTICLE = "8273102"

# Neuron superclusters to fetch for task A (excitatory vs inhibitory
# contrast; 'All neurons' would be 32.9 GB — these slices sum to ~10.5 GB)
NEURON_SUPERCLUSTERS = [
    "Upper-layer intratelencephalic",   # 6.58 GB cortex excitatory
    "MGE interneuron",                  # 2.55 GB inhibitory
    "Thalamic excitatory",              # 1.40 GB
]

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

USE_PROXY = False


def _curl_base():
    base = ["curl", "-s", "--max-time", "120"]
    if USE_PROXY:
        base += ["--socks5-hostname", "127.0.0.1:10808"]
    return base


def curl_json(url, timeout=120):
    r = subprocess.run(_curl_base() + [url], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode} for {url} "
                           f"({'proxy down? ' if USE_PROXY else ''}{r.stderr.strip()[:200]})")
    return json.loads(r.stdout)


def curl_download(url, out_path, expected_size=None):
    out_path = str(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cmd = ["curl", "-L", "-C", "-", "--retry", "5", "--retry-delay", "10"]
    if USE_PROXY:
        cmd += ["--socks5-hostname", "127.0.0.1:10808"]
    cmd += ["-o", out_path, url]
    print(f"  downloading -> {out_path}")
    t0 = time.time()
    r = subprocess.run(cmd)
    el = time.time() - t0
    sz = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    print(f"  done: {sz/1e9:.2f} GB in {el/60:.1f} min "
          f"({sz/1e6/max(el,1):.1f} MB/s), exit={r.returncode}")
    if expected_size and abs(sz - expected_size) > 1024:
        print(f"  WARNING: size {sz} != expected {expected_size} "
              f"(partial download? rerun to resume)")
        return False
    return r.returncode == 0


def cxg_collection_datasets(coll_id):
    meta = curl_json(f"{CXG_API}/collections/{coll_id}")
    out = []
    for ds in meta.get("datasets", []):
        title = ds.get("title", "")
        assets = ds.get("assets", [])
        h5 = [a for a in assets if a.get("filetype") == "H5AD"]
        url = h5[0].get("url") if h5 else None
        size = h5[0].get("filesize") if h5 else None
        out.append((title, url, size))
    return out


def do_A(check):
    print("\n=== A: Siletti neuron superclusters (per-supercluster slices) ===")
    ds = cxg_collection_datasets(SILETTI_COLLECTION)
    wanted = {f"Supercluster: {n}": n for n in NEURON_SUPERCLUSTERS}
    for title, url, size in ds:
        if title in wanted or title in ("All neurons", "All non-neuronal cells"):
            print(f"  dataset: {title!r}  size={size and size/1e9:.2f} GB")
    for title, url, size in ds:
        if title not in wanted or url is None:
            continue
        name = wanted[title]
        out = f"data/brain/neurons/{name.replace(' ', '_')}.h5ad"
        if os.path.exists(out) and expected_ok(out, size):
            print(f"  SKIP (exists, size ok): {out}")
            continue
        if check:
            print(f"  WOULD DOWNLOAD: {title!r} ({size and size/1e9:.2f} GB) -> {out}")
            continue
        curl_download(url, out, expected_size=size)


def expected_ok(path, size):
    if not size:
        return os.path.getsize(path) > 1e6
    return abs(os.path.getsize(path) - size) <= 1024


TMS_CXG_COLLECTION = "0b9d8a04-bb9d-44da-aa27-705bb65b54eb"
# TMS FACS = Smart-seq2 assay in CELLxGENE. The 'All ... Smart-seq2' file
# (2.55 GB) contains every tissue/age — the complete ageing ladder.
TMS_CXG_TARGET = ("All - A single-cell transcriptomic atlas characterizes "
                  "ageing tissues in the mouse - Smart-seq2")


def do_C(check):
    print("\n=== C: Tabula Muris Senis (CELLxGENE, Smart-seq2 All) ===")
    ds = cxg_collection_datasets(TMS_CXG_COLLECTION)
    hit = [(t, u, s) for t, u, s in ds if t == TMS_CXG_TARGET]
    if not hit:
        print("  ERROR: target dataset not found; listing 'All' datasets:")
        for t, u, s in ds:
            if t.startswith("All"):
                print(f"    {t!r}: {s and s/1e9:.2f} GB")
        return
    title, url, size = hit[0]
    print(f"  target: {title!r} ({size and size/1e9:.2f} GB)")
    out = "data/tms/TMS_Smart-seq2_All.h5ad"
    if check:
        print(f"  would download -> {out}")
        return
    if os.path.exists(out) and expected_ok(out, size):
        print(f"  SKIP (exists, size ok): {out}")
        return
    curl_download(url, out, expected_size=size)



SEA_AD_COLLECTION = "1ca90a2d-2943-483d-b678-b809bf464c30"
# First-wave D datasets: AD-responsive cell classes in MTG
# (DAM positive control = Microglia-PVM; reactive astrogliosis = Astrocyte)
SEA_AD_FIRST_WAVE = [
    "Microglia-PVM - MTG: Seattle Alzheimer's Disease Atlas (SEA-AD)",
    "Astrocyte - MTG: Seattle Alzheimer's Disease Atlas (SEA-AD)",
]


def do_D(check):
    print("\n=== D: SEA-AD (collection pinned) ===")
    print(f"  collection id: {SEA_AD_COLLECTION}")
    ds = cxg_collection_datasets(SEA_AD_COLLECTION)
    wanted = {t: t for t in SEA_AD_FIRST_WAVE}
    for title, url, size in ds:
        if title in wanted:
            print(f"  target: {title!r}  size={size and size/1e9:.2f} GB")
    if check:
        return
    for title, url, size in ds:
        if title not in wanted or url is None:
            continue
        safe = (title.split(" - ")[0] + "_MTG").replace(" ", "_")
        out = f"data/sea_ad/{safe}.h5ad"
        if os.path.exists(out) and expected_ok(out, size):
            print(f"  SKIP (exists, size ok): {out}")
            continue
        curl_download(url, out, expected_size=size)


if __name__ == "__main__":
    args = sys.argv[1:]
    USE_PROXY = "--proxy" in args
    if USE_PROXY:
        args = [a for a in args if a != "--proxy"]
        print("(using socks5h://127.0.0.1:10808 proxy)")
    if not args or args[0] == "--check":
        check = True
        modes = ["A", "C", "D"]
    else:
        check = "--check" in args
        modes = [a for a in args if a in ("A", "C", "D")] or ["A", "C", "D"]
    for m in modes:
        {"A": do_A, "C": do_C, "D": do_D}[m](check)
    print("\nALL DONE" if not check else "\nCHECK DONE")
