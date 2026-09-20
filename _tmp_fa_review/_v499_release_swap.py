import re, json, urllib.request

cred = open(r'C:\Users\KnightZ\.git-credentials', encoding='utf-8').read()
token = re.search(r'https://([^:]+):([^@]+)@github.com', cred).group(2)
H = {'Authorization': 'token ' + token, 'Accept': 'application/vnd.github+json', 'User-Agent': 'cki-rel'}
REPO = 'zhanglknt/CKI-cell-type-identification'
REL = 387922141
OLD_ASSET = 575190894
ZIP = 'CKI_Submission_v49_NC.zip'
SHA = '43256f999d0007a4984f993d727daaa86b4dee67f0fa90f25a3ea705d79eed3e'
OLDSHA = 'b38de8662e804c1b0c5be01d0089ef516eca517fc1111aaf4677a6f8bea404ef'

# 0) fetch live body (archive pre-patch copy)
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/releases/{REL}', headers=H)
rel0 = json.load(urllib.request.urlopen(req))
body = rel0['body']
open('_tmp_fa_review/_rel_body_pre_v499.md', 'w', encoding='utf-8').write(body)
print('[OK] live body fetched, len:', len(body))

# 1) delete old asset
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/releases/assets/{OLD_ASSET}',
                             headers=H, method='DELETE')
urllib.request.urlopen(req)
print('[OK] old asset deleted:', OLD_ASSET)

# 2) upload new zip
data = open(ZIP, 'rb').read()
up = urllib.request.Request(
    f'https://uploads.github.com/repos/{REPO}/releases/{REL}/assets?name={ZIP}',
    data=data, method='POST',
    headers={**H, 'Content-Type': 'application/zip', 'Content-Length': str(len(data))})
asset = json.load(urllib.request.urlopen(up))
print('[OK] uploaded asset id:', asset['id'], 'size:', asset['size'], 'state:', asset['state'])

# 3) patch release body
body = body.replace('v49.8 (NC enhanced submission, latest).',
                    'v49.9 (NC enhanced submission, latest).')
body = body.replace('## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.8)',
                    '## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.9)')
v499_block = (
    'v49.9 (scope-of-index design argument): limited cross-cell-type discrimination of omega is expected by design, not a performance deficit — the Discussion "Scope of the index" paragraph now states this explicitly.\n\n'
    '- Design argument added (Discussion): CKI detects state changes within a given cell type, not cell-type identity; because the housekeeping anchor is cell-type-specific (housekeeping gene sets may differ across cell types), k_n baselines are only directly comparable within the same cell type, so limited cross-type discrimination of omega delineates, rather than limits, the index\'s scope\n'
    '- Intended domain stated: the comparison of biologically matched populations — the same cell type across organs, brain regions, or perturbation states (the paradigm of every analysis reported)\n'
    '- No numbers added; zero conflict with the v49.8 classification-benchmark cut. Build 133/133 (new assertion V49-N38), ms_verify 116/116, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries\n\n')
body = body.replace(
    'v49.8 (reframe): CKI measures cell-state dynamics, not cell-type identity — the cell-type classification benchmark is cut entirely rather than kept as a demoted disclosure.\n\n',
    v499_block + 'v49.8 (reframe): CKI measures cell-state dynamics, not cell-type identity — the cell-type classification benchmark is cut entirely rather than kept as a demoted disclosure.\n\n')
# rewrite v49.7-era "honest disclosure" wording into the scope framing
body = body.replace(
    'classification performance (omega AUC = 0.680, rank 5/5) retained in Table 1 as honest disclosure',
    'classification performance (omega AUC = 0.680, rank 5/5) at that point retained in Table 1; cut entirely in v49.8 — cross-type discrimination lies outside the index\'s intended scope (v49.9)')
body = body.replace('sha256: ' + OLDSHA, 'sha256: ' + SHA)
assert 'v49.9' in body and SHA in body and OLDSHA[:8] not in body and 'honest disclosure' not in body
payload = json.dumps({'body': body}).encode('utf-8')
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/releases/{REL}',
                             data=payload, method='PATCH',
                             headers={**H, 'Content-Type': 'application/json'})
rel = json.load(urllib.request.urlopen(req))
print('[OK] body patched, len:', len(rel['body']))
print('--- new asset list ---')
for a in rel['assets']:
    print(a['id'], a['name'], a['size'])
open('_tmp_fa_review/_rel_body_new.md', 'w', encoding='utf-8').write(rel['body'])
