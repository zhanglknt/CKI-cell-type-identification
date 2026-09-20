import os, json, hashlib, urllib.request

pat = [l.strip().split('//')[1].split(':')[1].split('@')[0]
       for l in open(os.path.expanduser('~/.git-credentials'), encoding='utf-8')
       if 'github.com' in l][0]
H = {'Authorization': f'token {pat}', 'Accept': 'application/vnd.github+json',
     'User-Agent': 'cki-build'}
REPO = 'https://api.github.com/repos/zhanglknt/CKI-cell-type-identification'
ZIP = 'CKI_Submission_v49_NC.zip'

sha = hashlib.sha256(open(ZIP, 'rb').read()).hexdigest()
size = os.path.getsize(ZIP)
print('new zip:', size, 'sha256:', sha)

def req(method, url, data=None, headers=None):
    r = urllib.request.Request(url, method=method, headers=headers or H, data=data)
    return json.load(urllib.request.urlopen(r))

# 1. delete old v49 asset
rel = req('GET', f'{REPO}/releases/387922141')
old = [a for a in rel['assets'] if a['name'] == ZIP]
for a in old:
    r = urllib.request.Request(f"{REPO}/releases/assets/{a['id']}", method='DELETE', headers=H)
    urllib.request.urlopen(r)
    print('deleted asset', a['id'])

# 2. upload new zip
up = f"https://uploads.github.com/repos/zhanglknt/CKI-cell-type-identification/releases/387922141/assets?name={ZIP}"
headers = dict(H); headers['Content-Type'] = 'application/zip'
r = urllib.request.Request(up, method='POST', headers=headers,
                           data=open(ZIP, 'rb').read())
resp = json.load(urllib.request.urlopen(r))
print('uploaded asset', resp['id'], resp['name'], resp['size'])
assert resp['size'] == size, 'size mismatch after upload'

# 3. patch body
body = rel['body']
new_sec = f"""## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.7)

Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application. v49.7: Figure 2E scenario swap — CKI measures cell-type change, not cell-type identity, so the main figure now shows the scenario where omega ranks first.

- Figure 2E (new): ROC for functional-change vs neutral-drift discrimination in the semi-synthetic ground-truth simulation (600 functional vs 250 neutral replicates, marrow B-cell background). CKI omega AUC = 0.80, rank 1/6 (vs k_f 0.72, raw JS 0.64, cosine 0.58, k_f/k_total 0.44, k_n 0.21); independent replication on skin keratinocyte background AUC = 0.91 (rank 1/6). Panel D (Tabula Sapiens 5-metric correlation heatmap) unchanged; cell-type classification ROC demoted from the main figure — classification performance (omega AUC = 0.680, rank 5/5) retained in Table 1 as honest disclosure
- Bottom row natively regenerated at 178 x 72 mm, embedded Arial >= 7 pt (Type 42), native panel labels D/E (replaces the v47 cutout + relabel); merged Figure 2 geometry unchanged (178.0 x 148.1 mm)
- AUC verification: all 12 values (6 metrics x 2 backgrounds) recomputed from raw replicate CSVs and aligned with metrics.json (definition: signal delta >= 0.25 vs neutral_hk + neutral_global, matching SI)
- MS rewire: Fig 2 legend rewritten; Result 3 anchor narrowed to (Fig. 2d); Result 3b AUC sentences now cite (Fig. 2e); abstract headline "ranked first (AUC = 0.80)" now backed by a main figure
- Build 129/129, ms_verify 112/112, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries

sha256: {sha}"""
start = body.find('## CKI_Submission_v49_NC.zip')
end = body.find('## CKI_Submission_v48_NC.zip')
assert start != -1 and end != -1
body2 = body[:start] + new_sec + '\n\n' + body[end:]
body2 = body2.replace('-> v49.6 (NC enhanced submission, latest)',
                      '-> v49.7 (NC enhanced submission, latest)')
r = urllib.request.Request(f'{REPO}/releases/387922141', method='PATCH',
                           headers=H, data=json.dumps({'body': body2}).encode())
json.load(urllib.request.urlopen(r))
print('release body patched')

# 4. readback verify
rel2 = req('GET', f'{REPO}/releases/387922141')
a2 = [a for a in rel2['assets'] if a['name'] == ZIP][0]
print('readback: asset', a2['id'], a2['size'], 'sha-in-body:', sha in rel2['body'],
      'v49.7-in-body:', 'v49.7' in rel2['body'])
