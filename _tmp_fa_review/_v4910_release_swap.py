# v49.10 Release asset swap: delete old zip asset, upload new, patch body
import re, json, urllib.request, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

creds = open('C:/Users/KnightZ/.git-credentials').read()
m = re.search(r'https://([^:]+):([^@]+)@github.com', creds)
user, tok = m.group(1), m.group(2)
REPO = 'zhanglknt/CKI-cell-type-identification'
RELEASE_ID = 387922141
OLD_ASSET = 575239545
ZIP = 'CKI_Submission_v49_NC.zip'

def api(url, method='GET', data=None, headers=None, upload=False):
    h = {'Authorization': f'token {tok}', 'User-Agent': 'cki-build'}
    if not upload:
        h['Accept'] = 'application/vnd.github+json'
    if data is not None and not upload:
        h['Content-Type'] = 'application/json'
        data = json.dumps(data).encode()
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    return urllib.request.urlopen(req)

# 1. archive old body
rel = json.load(api(f'https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}'))
body = rel['body']
open('_tmp_fa_review/_rel_body_pre_v4910.md', 'w', encoding='utf-8').write(body)
print('body archived:', len(body), 'chars')
assert 'v49.9' in body and '43256f999d00' in body

# 2. delete old asset
r = api(f'https://api.github.com/repos/{REPO}/releases/assets/{OLD_ASSET}', method='DELETE')
print('delete old asset:', r.status)

# 3. upload new zip
zdata = open(ZIP, 'rb').read()
import hashlib
SHA = hashlib.sha256(zdata).hexdigest()
print('new zip:', len(zdata), 'B sha256', SHA[:16])
r = api(f'https://uploads.github.com/repos/{REPO}/releases/{RELEASE_ID}/assets?name=CKI_Submission_v49_NC.zip',
        method='POST', data=zdata, upload=True,
        headers={'Content-Type': 'application/zip', 'Content-Length': str(len(zdata))})
up = json.load(r)
print('upload asset id:', up['id'], up['state'])
NEW_ASSET = up['id']
assert up['state'] == 'uploaded'

# 4. patch body: prepend v49.10 block, update latest header + sha line
new_block = """**Latest: v49.10 (2026-09-20) — expert-panel review fixes (A1-A7 editorial + B1-B8 conceptual).**
Following a six-reviewer blind panel (mean 4.42/10, Major Revision), all confirmed items fixed: availability line lists Supplementary Tables 1-19; SI main-text figure pointers corrected to Fig. 3d/3b,c; SI Note 9 points to Table 1; Guide estimator-comparison pointer Supp. Fig. 7; brain Strong-candidate enumeration sums to 39 (adds one committed OPC + one OPC); TCGA k_n mean/median calibers cross-linked; SI Augur pointer = main-text ref. 37. Conceptual: SI weight-scheme AUC reconciliation clause; Ka/Ks structural-inversion sentence citing McDonald-Kreitman as new ref [34] (refs 34-56 renumbered to 35-57); Table 1 cross-type caveat; Abstract leads with the 1.74-fold size-balanced gradient; brain screen donor-confounding disclosure; Methods CC provenance (32 LUSC-matrix cell-line samples assigned LIHC per barcode audit); TCGA bootstrap CI type stated (percentile). Build 148/148, ms_verify 117 + si_verify 109 + cl_guide_verify 39 all 0-fail; CI 4/4 green.

"""
assert body.startswith('**Latest')
body_new = new_block + body
body_new = body_new.replace(
    'sha256 43256f999d00…eed3e (v49.9 zip)',
    'sha256 5602c15e…afebd (v49.10 zip)') if '43256f999d00…eed3e' in body_new else body_new
# generic sha replacement fallback
if '43256f999d00' in body_new:
    # replace the v49.9 sha line mention
    body_new = re.sub(r'43256f999d00[0-9a-f\u2026.]*eed3e', '5602c15ee418\u2026afebd', body_new)
    # also update the "Latest" wording of previous head if it claimed latest
body_new = body_new.replace('**Latest: v49.9 (2026-09-20)', '**v49.9 (2026-09-20)', 1)
assert '5602c15e' in body_new
assert body_new.count('Latest:') == 1
r = api(f'https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}', method='PATCH',
        data={'body': body_new})
patched = json.load(r)
open('_tmp_fa_review/_rel_body_new_v4910.md', 'w', encoding='utf-8').write(patched['body'])
print('body patched:', len(patched['body']), 'chars')

# 5. readback
asset = json.load(api(f'https://api.github.com/repos/{REPO}/releases/assets/{NEW_ASSET}'))
print('readback asset:', asset['id'], asset['size'], asset['state'])
assert asset['id'] == NEW_ASSET and asset['size'] == len(zdata)
print('SWAP_OK', NEW_ASSET, SHA)
