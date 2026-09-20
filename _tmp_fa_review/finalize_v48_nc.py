# -*- coding: utf-8 -*-
"""finalize_v48_nc.py — v48 (NC) 发布链：
1) NC 生成器链镜像入 CKI_Reproducibility_Package/（GB 链保留）
2) 重建复现包 zip
3) 复现包并入 v48 workdir + 重生成 MANIFEST + 重写 v48 zip + 主目录副本
4) 终检
"""
from pathlib import Path
import zipfile, hashlib, shutil, io

BASE = Path(r'C:/Users/KnightZ/Desktop/细胞受选择')
RP = BASE / 'CKI_Reproducibility_Package'
RP_ZIP = BASE / 'CKI_Reproducibility_Package.zip'
V48_WD = BASE / 'version3' / 'CKI_Submission_v48_NC'
V48_ZIP = BASE / 'version3' / 'CKI_Submission_v48_NC.zip'


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# ---- 1) 镜像 NC 生成器链 ----
mirror_nc = [
    'generate_manuscript_nc.py', 'generate_cover_letter_nc.py',
    'notebooks/68_gen_supplementary_nc.py',
    'notebooks/100_gen_reproducibility_nc.js',
    '99_build_nc_v48.py',
]
for rel in mirror_nc:
    src = BASE / rel
    dst = RP / rel
    assert src.exists(), src
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  mirror <- {rel}')

n_files = sum(1 for p in RP.rglob('*') if p.is_file())
print(f'repro package: {n_files} files')

# ---- 2) 重建复现包 zip ----
entries = sorted(p for p in RP.rglob('*') if p.is_file())
with zipfile.ZipFile(RP_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in entries:
        z.write(p, str(p.relative_to(RP)).replace('\\', '/'))
rp_sha, rp_size = sha256(RP_ZIP), RP_ZIP.stat().st_size
print(f'repro zip rebuilt: {rp_size:,} B ({len(entries)} entries), sha {rp_sha[:12]}...')

# ---- 3) 并入 workdir + MANIFEST + zip ----
shutil.copy2(RP_ZIP, V48_WD / 'CKI_Reproducibility_Package.zip')

manifest = ['=' * 60,
            '  CKI Submission Package v48 (Nature Communications)',
            '  MANIFEST_v48.txt',
            '  tag: v0.5.0 | NC format conversion of v47.3',
            '=' * 60, '']
files = sorted(os.listdir(V48_WD)) if False else sorted(p.name for p in V48_WD.iterdir() if p.is_file() and p.name != 'MANIFEST_v48.txt')
for i, e in enumerate(files, 1):
    p = V48_WD / e
    manifest.append(f'{i:2d}. {e}  ({p.stat().st_size:,} bytes)')
manifest.append('')
manifest.append('SHA-256 checksums:')
for e in files:
    manifest.append(f'  {sha256(V48_WD / e)}  {e}')
mtext = '\n'.join(manifest) + '\n'
(V48_WD / 'MANIFEST_v48.txt').write_text(mtext, encoding='utf-8')

with zipfile.ZipFile(V48_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for e in sorted(p.name for p in V48_WD.iterdir() if p.is_file()):
        z.write(V48_WD / e, f'CKI_Submission_v48_NC/{e}')
main_copy = BASE / 'CKI_Submission_v48_NC.zip'
shutil.copy2(V48_ZIP, main_copy)
print(f'v48 zip rewritten: {V48_ZIP.stat().st_size:,} B')
print(f'main-dir copy: {main_copy.stat().st_size:,} B')

# ---- 4) 终检 ----
with zipfile.ZipFile(V48_ZIP) as z:
    names = z.namelist()
    assert len(names) == 32, len(names)
    assert 'CKI_Submission_v48_NC/CKI_Reproducibility_Package.zip' in names
    mf = z.read('CKI_Submission_v48_NC/MANIFEST_v48.txt').decode('utf-8')
    assert rp_sha in mf and f'({rp_size:,} bytes)' in mf
    inner = z.read('CKI_Submission_v48_NC/CKI_Reproducibility_Package.zip')
    assert hashlib.sha256(inner).hexdigest() == rp_sha
    with zipfile.ZipFile(io.BytesIO(inner)) as rz:
        rn = rz.namelist()
    for must in ['generate_manuscript_nc.py', 'generate_cover_letter_nc.py',
                 'notebooks/68_gen_supplementary_nc.py',
                 'notebooks/100_gen_reproducibility_nc.js', '99_build_nc_v48.py',
                 'generate_manuscript_gb.py', '99_build_gb_v47.py',
                 'results/hk_stability_sweep.csv', 'data/kang_ifnb/ensg2sym.tsv']:
        assert must in rn, must
print('ALL FINALIZE CHECKS PASSED')
print('v48 entries:', len(names), '| repro nested:', len(rn))
