# upload_release_asset_v48_nc.py — upload CKI_Submission_v48_NC.zip as a NEW asset
# on the v0.5.0 release (keeps the GB v47 asset 565418079 untouched).
import urllib.request, json, os, hashlib, time

BASE = r'C:\Users\KnightZ\Desktop\细胞受选择'
ZIP = os.path.join(BASE, 'version3', 'CKI_Submission_v48_NC.zip')
RELEASE_ID = 387922141
ASSET_NAME = 'CKI_Submission_v48_NC.zip'

tok = None
with open(os.path.expanduser('~/.git-credentials'), encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'github.com' in line:
            tok = line.strip().split('//')[1].split('@')[0].split(':')[1]
H = {'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json',
     'User-Agent': 'cki-v48'}

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

local_sha = sha256(ZIP)
local_size = os.path.getsize(ZIP)
print('local zip: %s B, sha256 %s' % (format(local_size, ','), local_sha))

# 0) guard: no same-name asset already on the release
req = urllib.request.Request(
    'https://api.github.com/repos/zhanglknt/CKI-cell-type-identification/releases/%d/assets' % RELEASE_ID,
    headers=H)
assets = json.loads(urllib.request.urlopen(req, timeout=60).read())
same = [a for a in assets if a['name'] == ASSET_NAME]
assert not same, 'asset %s already exists (id %s) — abort to avoid duplicate' % (ASSET_NAME, same[0]['id'] if same else '?')
print('existing assets:', [(a['name'], a['id']) for a in assets])

# 1) upload
url = ('https://uploads.github.com/repos/zhanglknt/CKI-cell-type-identification/'
       'releases/%d/assets?name=%s' % (RELEASE_ID, ASSET_NAME))
with open(ZIP, 'rb') as f:
    data = f.read()
req = urllib.request.Request(url, data=data, method='POST', headers={
    'Authorization': 'Bearer ' + tok,
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/zip',
    'User-Agent': 'cki-v48'})
t0 = time.time()
resp = json.loads(urllib.request.urlopen(req, timeout=1800).read())
print('uploaded in %.0fs: asset id %s, size %s, state %s' % (
    time.time() - t0, resp['id'], format(resp['size'], ','), resp['state']))
assert resp['size'] == local_size, (resp['size'], local_size)

# 2) readback verify
req = urllib.request.Request(resp['url'], headers={
    'Authorization': 'Bearer ' + tok,
    'Accept': 'application/octet-stream',
    'User-Agent': 'cki-v48'})
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
print('ASSET UPLOAD VERIFIED OK | asset id:', resp['id'])
