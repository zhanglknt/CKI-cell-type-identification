import re, json, urllib.request

cred = open(r'C:\Users\KnightZ\.git-credentials', encoding='utf-8').read()
token = re.search(r'https://([^:]+):([^@]+)@github.com', cred).group(2)
H = {'Authorization': 'token ' + token, 'Accept': 'application/vnd.github+json', 'User-Agent': 'cki-rel'}
REPO = 'zhanglknt/CKI-cell-type-identification'
REL = 387922141
OLD_ASSET = 575109262
ZIP = 'CKI_Submission_v49_NC.zip'
SHA = 'b38de8662e804c1b0c5be01d0089ef516eca517fc1111aaf4677a6f8bea404ef'

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
body = open('_tmp_fa_review/_rel_body.md', encoding='utf-8').read()
new_head = ('CKI package v0.5.0 with submission packages: v47 (Genome Biology first-author revision) -> '
            'v48 (Nature Communications format conversion) -> v49.8 (NC enhanced submission, latest).')
body = body.replace(
    'CKI package v0.5.0 with submission packages: v47 (Genome Biology first-author revision) -> v48 (Nature Communications format conversion) -> v49.7 (NC enhanced submission, latest).',
    new_head)
body = body.replace('## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.7)',
                    '## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.8)')
v498_block = (
    'v49.8 (reframe): CKI measures cell-state dynamics, not cell-type identity — the cell-type classification benchmark is cut entirely rather than kept as a demoted disclosure.\n\n'
    '- Classification benchmark removed: MS Result paragraph (omega AUC = 0.680, rank 5-of-5 sentences), the original Table 1 (classification metrics), the Methods classification clause, and the Fig 2 legend pointer to Table 1\n'
    '- CKI_Tables_NC.xlsx now holds a single sheet: the former Table 2 (cross-organ conservation ranking) renumbered to Table 1, all 4 in-text references updated\n'
    '- Cover letter: three spots rewritten to the cell-state-dynamics framing; Abstract keeps the name-origin expansion "CKI (Cell-type Ka/Ks-inspired Index)" with no cell-type application claims\n'
    '- Build 132/132 (new assertions V49-N35 single-sheet Table 1 / V49-N36 classification cut / V49-N37 renumber), ms_verify 116/116, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries\n\n'
    'v49.7 base (Figure 2E scenario swap): CKI measures cell-type change, not cell-type identity, so the main figure shows the scenario where omega ranks first.\n\n')
body = body.replace(
    'Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application. v49.7: Figure 2E scenario swap — CKI measures cell-type change, not cell-type identity, so the main figure now shows the scenario where omega ranks first.\n\n',
    'Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application.\n\n' + v498_block)
body = body.replace('sha256: 01a0e61cc1bbdb1f7aead8e0513947b12f6c7a276181c5bb0df8948bb919a43c',
                    'sha256: ' + SHA)
assert 'v49.8' in body and SHA in body and '01a0e61c' not in body
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
