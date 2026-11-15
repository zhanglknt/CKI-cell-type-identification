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

def req(method, url, data=None, headers=None, raw=None):
    r = urllib.request.Request(url, method=method, headers=headers or H,
                               data=data)
    return urllib.request.urlopen(r, raw) if raw else json.load(urllib.request.urlopen(r))

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
new_sec = f"""## CKI_Submission_v49_NC.zip (latest, 2026-09-19, v49.6)

Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application. v49.6: main figures 7 -> 6 under the 4-6-panels-per-figure rule (Fig2+Fig3 merged into one 5-panel figure).

- Figure 2 (merged, panels a-e): top row regenerated from source data (mouse_pilot_v2_results.csv) at native 178 mm with embedded Arial >= 7 pt (Type 42; mathtext in Arial); bottom row = prior Fig3 (metric-correlation heatmap + classification ROC) relabelled d/e in embedded Arial Bold 9 pt; 178.0 x 148.1 mm vector PDF
- Real-data drift calibration: 30 Kang IFN-beta cross-lane technical replicate pairs (omega FPR 0/30) + 4,906-pair brain library drift ladder
- TCGA pan-cancer functional divergence atlas (5 cancer types, 3,567 samples): omega NN/TT 1.10-2.46, 4/5 bootstrap CIs excluding 1; LUAD EGFR/KRAS mutation stratification; purity (ANCOVA) and smoking covariate sensitivity analyses
- References reordered by first appearance (56 refs, 75 superscript citation groups; CZI CELLxGENE orphan now cited as ref 47); 3 field fixes (Raj title, Jiang title, Hao pages .e29)
- Supplementary Tables 5-19 in standalone CKI_Supplementary_Tables_NC.xlsx (SI docx zero tables)
- Build 128/128, ms_verify, si_verify, cl_guide_verify all green; CI success (py3.10-3.13); 27 zip entries

sha256: {sha}"""
start = body.find('## CKI_Submission_v49_NC.zip')
end = body.find('## CKI_Submission_v48_NC.zip')
assert start != -1 and end != -1
body2 = body[:start] + new_sec + '\n\n' + body[end:]
body2 = body2.replace('-> v49.5 (NC enhanced submission, latest)',
                      '-> v49.6 (NC enhanced submission, latest)')
r = urllib.request.Request(f'{REPO}/releases/387922141', method='PATCH',
                           headers=H, data=json.dumps({'body': body2}).encode())
json.load(urllib.request.urlopen(r))
print('release body patched')

# 4. readback verify
rel2 = req('GET', f'{REPO}/releases/387922141')
a2 = [a for a in rel2['assets'] if a['name'] == ZIP][0]
print('readback: asset', a2['id'], a2['size'], 'sha-in-body:', sha in rel2['body'],
      'v49.6-in-body:', 'v49.6' in rel2['body'])
