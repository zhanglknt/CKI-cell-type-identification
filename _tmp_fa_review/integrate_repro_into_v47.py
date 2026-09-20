# integrate_repro_into_v47.py
# 1) 补复现包缺件（Q1 三个 sweep/variance CSV + Q2 phase35 CSV + Q3 ensg2sym.tsv）
# 2) 重建 CKI_Reproducibility_Package.zip
# 3) 并入 version3/CKI_Submission_v47.zip（含 MANIFEST_v47.txt 更新）
# 4) 同步 WORK_DIR 与主目录副本
from pathlib import Path
import zipfile, hashlib, shutil

BASE = Path(r'C:/Users/KnightZ/Desktop/细胞受选择')
RP = BASE / 'CKI_Reproducibility_Package'
RP_ZIP = BASE / "CKI_Reproducibility_Package.zip"
V47_ZIP = BASE / 'version3' / 'CKI_Submission_v47.zip'
V47_WD = BASE / 'version3' / 'CKI_Submission_v47'


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# ---- 1) 补缺件 ----
copies = [
    (BASE / 'results' / 'hk_stability_sweep.csv', RP / 'results' / 'hk_stability_sweep.csv'),
    (BASE / 'results' / 'phase32_sweep_results.csv', RP / 'results' / 'phase32_sweep_results.csv'),
    (BASE / 'results' / 'figure_data_module_variance.csv', RP / 'results' / 'figure_data_module_variance.csv'),
    (BASE / 'results' / 'phase35_cross_organ_conservation.csv', RP / 'results' / 'phase35_cross_organ_conservation.csv'),
    (BASE / 'data' / 'kang_ifnb' / 'ensg2sym.tsv', RP / 'data' / 'kang_ifnb' / 'ensg2sym.tsv'),
]
for src, dst in copies:
    assert src.exists(), src
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {dst.relative_to(RP)} ({dst.stat().st_size:,} B)')

n_files = sum(1 for p in RP.rglob('*') if p.is_file())
print(f'repro package now: {n_files} files')

# ---- 2) 重建复现包 zip ----
entries = sorted(p for p in RP.rglob('*') if p.is_file())
tmp_zip = BASE / '_tmp_fa_review' / 'CKI_Reproducibility_Package_rebuild.zip'
with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in entries:
        arc = str(p.relative_to(RP)).replace('\\', '/')
        z.write(p, arc)
old_size = RP_ZIP.stat().st_size
shutil.move(str(tmp_zip), str(RP_ZIP))
print(f'repro zip rebuilt: {old_size:,} -> {RP_ZIP.stat().st_size:,} B ({len(entries)} entries)')

# ---- 3) 并入 v47 投稿包 ----
rp_sha = sha256(RP_ZIP)
rp_size = RP_ZIP.stat().st_size

with zipfile.ZipFile(V47_ZIP) as z:
    manifest = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')
    names = z.namelist()
assert 'CKI_Submission_v47/CKI_Reproducibility_Package.zip' not in names

# MANIFEST: 在 Contents 段追加 item 10（CRLF），在 figure checksums 后追加 repro checksum
NL = "\r\n"
item10 = (
    "  10. CKI_Reproducibility_Package.zip - Full reproducibility package" + NL +
    "     (code + reference results; v47 additions: hk_stability_sweep.csv," + NL +
    "     phase32_sweep_results.csv, figure_data_module_variance.csv," + NL +
    "     phase35_cross_organ_conservation.csv, data/kang_ifnb/ensg2sym.tsv)" + NL +
    "     addressing first-author Q1/Q3. Included as a review aid; the" + NL +
    "     journal receives the GitHub repository + Zenodo DOI instead." + NL
)
anchor = "are not part of the journal submission." + NL
assert manifest.count(anchor) == 1, manifest.count(anchor)
i = manifest.find(anchor)
insert_at = i + len(anchor)
manifest_new = manifest[:insert_at] + item10 + manifest[insert_at:]

ck_anchor = "  c8529c93bc3197f0a8838a7a0d4be6000aff4bb03f906f04d338d59d603c3299  CKI_graphical_abstract.pdf"
assert ck_anchor in manifest_new
manifest_new = manifest_new.replace(
    ck_anchor,
    ck_anchor + NL + f"  {rp_sha}  CKI_Reproducibility_Package.zip ({rp_size:,} bytes)",
    1,
)

# 重写 v47 zip：原条目 + 更新 MANIFEST + 新增 repro zip
tmp_v47 = BASE / '_tmp_fa_review' / 'CKI_Submission_v47_rezip.zip'
with zipfile.ZipFile(V47_ZIP) as zin, \
     zipfile.ZipFile(tmp_v47, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
    for item in zin.infolist():
        if item.filename == 'CKI_Submission_v47/MANIFEST_v47.txt':
            zout.writestr(item, manifest_new)
        else:
            zout.writestr(item, zin.read(item.filename))
    zout.write(RP_ZIP, 'CKI_Submission_v47/CKI_Reproducibility_Package.zip')
old_v47 = V47_ZIP.stat().st_size
shutil.move(str(tmp_v47), str(V47_ZIP))
print(f'v47 zip: {old_v47:,} -> {V47_ZIP.stat().st_size:,} B')

# ---- 4) 同步 WORK_DIR + 主目录副本 ----
shutil.copy2(RP_ZIP, V47_WD / 'CKI_Reproducibility_Package.zip')
(V47_WD / 'MANIFEST_v47.txt').write_text(manifest_new, encoding='utf-8')
main_copy = BASE / 'CKI_Submission_v47.zip'
shutil.copy2(V47_ZIP, main_copy)
print(f'main-dir copy: {main_copy} ({main_copy.stat().st_size:,} B)')

# ---- 5) 终检 ----
with zipfile.ZipFile(V47_ZIP) as z:
    names = z.namelist()
    assert 'CKI_Submission_v47/CKI_Reproducibility_Package.zip' in names
    mf = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')
    assert 'CKI_Reproducibility_Package.zip' in mf and rp_sha in mf
    inner = z.read('CKI_Submission_v47/CKI_Reproducibility_Package.zip')
    assert hashlib.sha256(inner).hexdigest() == rp_sha
    with zipfile.ZipFile(__import__('io').BytesIO(inner)) as rz:
        rn = rz.namelist()
    assert len(rn) == len(entries), (len(rn), len(entries))
    assert 'results/hk_stability_sweep.csv' in rn
    assert 'data/kang_ifnb/ensg2sym.tsv' in rn
    # 原有期刊文件不受影响
    for must in ['CKI_Submission_v47/CKI_Manuscript.docx',
                 'CKI_Submission_v47/figure6.pdf',
                 'CKI_Submission_v47/Supplementary_Figure_S13.pdf']:
        assert must in names
print('ALL INTEGRATION CHECKS PASSED')
print(f'v47 entries: {len(names)} | repro nested entries: {len(rn)}')
