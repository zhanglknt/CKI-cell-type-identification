# replace_release_asset_v050.py — v47 phase-2: replace CKI_Submission_v47.zip asset
import urllib.request, json, os, hashlib, time

BASE = r'C:\Users\KnightZ\Desktop\细胞受选择'
ZIP = os.path.join(BASE, 'version3', 'CKI_Submission_v47.zip')
RELEASE_ID = 387922141
OLD_ASSET_ID = 565377380

tok = None
with open(os.path.expanduser('~/.git-credentials'), encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'github.com' in line:
            tok = line.strip().split('//')[1].split('@')[0].split(':')[1]
H = {'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json',
     'User-Agent': 'cki-phase2'}

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

local_sha = sha256(ZIP)
local_size = os.path.getsize(ZIP)
print('local zip: %s B, sha256 %s' % (format(local_size, ','), local_sha))

# 1) delete old asset
req = urllib.request.Request(
    'https://api.github.com/repos/zhanglknt/CKI-cell-type-identification/releases/assets/%d' % OLD_ASSET_ID,
    headers=H, method='DELETE')
try:
    urllib.request.urlopen(req, timeout=60)
    print('old asset deleted')
except urllib.error.HTTPError as e:
    print('delete old asset HTTP', e.code, '(continuing if 404)')
    if e.code != 404:
        raise

# 2) upload new asset
url = ('https://uploads.github.com/repos/zhanglknt/CKI-cell-type-identification/'
       'releases/%d/assets?name=CKI_Submission_v47.zip' % RELEASE_ID)
with open(ZIP, 'rb') as f:
    data = f.read()
req = urllib.request.Request(url, data=data, method='POST', headers={
    'Authorization': 'Bearer ' + tok,
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/zip',
    'User-Agent': 'cki-phase2'})
t0 = time.time()
resp = json.loads(urllib.request.urlopen(req, timeout=1800).read())
print('uploaded in %.0fs: asset id %s, size %s, state %s' % (
    time.time() - t0, resp['id'], format(resp['size'], ','), resp['state']))
assert resp['size'] == local_size, (resp['size'], local_size)

# 3) readback verify
req = urllib.request.Request(resp['url'], headers={
    'Authorization': 'Bearer ' + tok,
    'Accept': 'application/octet-stream',
    'User-Agent': 'cki-phase2'})
h = hashlib.sha256()
with urllib.request.urlopen(req, timeout=1800) as r:
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        h.update(chunk)
rb_sha = h.hexdigest()
print('readback sha256:', rb_sha)
assert rb_sha == local_sha, 'READBACK MISMATCH'
print('ASSET REPLACEMENT VERIFIED OK | asset id:', resp['id'])
