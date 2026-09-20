# create_release_v050.py — GitHub Release v0.5.0 + CKI_Submission_v47.zip 资产
from pathlib import Path
import json, hashlib, urllib.request, sys

BASE = Path(r'C:/Users/KnightZ/Desktop/细胞受选择')
ASSET = BASE / 'CKI_Submission_v47.zip'
REPO_API = 'https://api.github.com/repos/zhanglknt/CKI-cell-type-identification'

tok = None
for l in (Path.home() / '.git-credentials').read_text(encoding='utf-8', errors='replace').splitlines():
    if 'github' in l and '://' in l:
        tok = l.split('://', 1)[1].split('@', 1)[0].split(':', 1)[1]
assert tok, 'no PAT'


def api(method, url, data=None, headers=None, timeout=300):
    hdrs = {'Authorization': f'Bearer {tok}',
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'cki-release'}
    if headers:
        hdrs.update(headers)
    body = json.dumps(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        try:
            return r.status, json.loads(raw)
        except Exception:
            return r.status, raw


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


asset_sha = sha256(ASSET)
asset_size = ASSET.stat().st_size
print(f'asset: {ASSET.name} {asset_size:,} B sha256 {asset_sha}')

body = f"""CKI v47 submission package for Genome Biology (Methodology article).

First-author (Xianming Wu) revision integration: all 95 tracked revisions + 6 comments adopted; build 664/664 checks PASS.

- Main figures replaced by the first-author redrawn set (figure1-6)
- Supplementary renumbered S1-S13 with no gap (old S3 method-comparison removed; Kang IFN-beta -> S12, permutation QQ -> S13); Figure S1 regenerated in-house from corrected sweep CSVs (k_n monotone decreasing over 250-1,000 HK genes; identity-only AUC 0.786 retained)
- Graphical abstract adopts the first-author layout, title corrected to "CKI: a Ka/Ks-inspired index"
- Discussion gains the anchor-stationarity sentence (Kang CD14+ monocytes: omega AUC 0.55 vs k_f 0.98)
- SN clarifies Table S3/S4 same-file provenance (brain_bs_null_observed_pairs.csv full 31,764 rows vs 6,591 threshold-passing rows)
- Reproducibility package embedded in the submission zip (296 files; v47 additions: hk_stability_sweep.csv, phase32_sweep_results.csv, figure_data_module_variance.csv, phase35_cross_organ_conservation.csv, data/kang_ifnb/ensg2sym.tsv)
- cki package 0.4.9 -> 0.5.0; Zenodo concept DOI 10.5281/zenodo.20405458 (new version record archives automatically)

Attachment: CKI_Submission_v47.zip (FINAL; MS Availability phase-1 cites the v0.4.9 record 10.5281/zenodo.22333850; the v0.5.0 record DOI is written in phase-2)
sha256: {asset_sha}
"""

# 1) create release
payload = {
    'tag_name': 'v0.5.0',
    'name': 'v0.5.0: v47 submission package (first-author revision integration)',
    'body': body,
    'draft': False,
    'prerelease': False,
}
st, rel = api('POST', f'{REPO_API}/releases', payload)
assert st == 201, (st, rel)
rel_id = rel['id']
print(f'release created: id={rel_id} tag={rel["tag_name"]} html={rel["html_url"]}')

# 2) upload asset
upload_url = rel['upload_url'].split('{')[0]  # strip params template
st2, asset = api(
    'POST',
    f'{upload_url}?name={ASSET.name}',
    data=ASSET.read_bytes(),
    headers={'Content-Type': 'application/zip'},
    timeout=1800,
)
assert st2 == 201, (st2, asset)
print(f'asset uploaded: id={asset["id"]} name={asset["name"]} size={asset["size"]:,} state={asset["state"]}')

# 3) verify
st3, rel2 = api('GET', f'{REPO_API}/releases/tags/v0.5.0')
print('verify: tag', rel2['tag_name'], '| assets',
      [(a['name'], a['size'], a['state']) for a in rel2['assets']])
assert rel2['assets'][0]['size'] == asset_size
print('RELEASE v0.5.0 COMPLETE')
print('url:', rel2['html_url'])
