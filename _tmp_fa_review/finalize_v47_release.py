# finalize_v47_release.py — 发布链准备：
# 1) 主仓 → CKI_Reproducibility_Package/ 镜像同步（v46 双写模式）
# 2) 重建 CKI_Reproducibility_Package.zip
# 3) 重写 version3/CKI_Submission_v47.zip（替换内嵌 repro zip + MANIFEST sha 行）
# 4) 同步 WORK_DIR 与主目录副本
from pathlib import Path
import zipfile, hashlib, shutil, re, io

BASE = Path(r'C:/Users/KnightZ/Desktop/细胞受选择')
RP = BASE / 'CKI_Reproducibility_Package'
RP_ZIP = BASE / 'CKI_Reproducibility_Package.zip'
V47_ZIP = BASE / 'version3' / 'CKI_Submission_v47.zip'
V47_WD = BASE / 'version3' / 'CKI_Submission_v47'


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# ---- 1) 镜像同步 ----
mirror = [
    'cki/__init__.py', 'pyproject.toml', 'README.md', 'data/README_data.md',
    'generate_manuscript_gb.py', 'generate_cover_letter_nar.py',
    'notebooks/100_gen_reproducibility_docx.js',
    'notebooks/68_gen_supplementary_en.py',
    'notebooks/_extract_table1_2.py',
    '99_build_gb_v47.py',                      # 新增镜像
    'notebooks/_ed_fig1_clean.py',             # 新增（S1 权威重画脚本，两边都补）
]
for rel in mirror:
    src = BASE / rel
    dst = RP / rel
    assert src.exists(), src
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  mirror <- {rel}')
# 主仓补 _ed_fig1_clean.py 留存（已存在，无操作）；确认
assert (BASE / 'notebooks' / '_ed_fig1_clean.py').exists()

n_files = sum(1 for p in RP.rglob('*') if p.is_file())
print(f'repro package: {n_files} files')

# ---- 2) 重建复现包 zip ----
entries = sorted(p for p in RP.rglob('*') if p.is_file())
with zipfile.ZipFile(RP_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in entries:
        z.write(p, str(p.relative_to(RP)).replace('\\', '/'))
rp_sha, rp_size = sha256(RP_ZIP), RP_ZIP.stat().st_size
print(f'repro zip rebuilt: {rp_size:,} B ({len(entries)} entries), sha {rp_sha[:12]}...')

# ---- 3) 重写 v47 投稿包（替换 MANIFEST sha 行 + 内嵌 repro zip）----
with zipfile.ZipFile(V47_ZIP) as z:
    manifest = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')

pat = re.compile(
    r'  [0-9a-f]{64}  CKI_Reproducibility_Package\.zip \([\d,]+ bytes\)')
m = pat.search(manifest)
new_line = f'  {rp_sha}  CKI_Reproducibility_Package.zip ({rp_size:,} bytes)'
NL = "\r\n"
if m:
    manifest_new = manifest[:m.start()] + new_line + manifest[m.end():]
    print('MANIFEST checksum line updated (update mode)')
else:
    # integrate mode: fresh build zip lacks item 10 + repro checksum
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
        ck_anchor + NL + new_line,
        1,
    )
    print('MANIFEST item 10 + checksum inserted (integrate mode)')

tmp = BASE / '_tmp_fa_review' / 'CKI_Submission_v47_rezip2.zip'
with zipfile.ZipFile(V47_ZIP) as zin, \
     zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
    seen_repro = False
    for item in zin.infolist():
        if item.filename == 'CKI_Submission_v47/MANIFEST_v47.txt':
            zout.writestr(item, manifest_new)
        elif item.filename == 'CKI_Submission_v47/CKI_Reproducibility_Package.zip':
            seen_repro = True
            with open(RP_ZIP, 'rb') as f:
                zout.writestr(item, f.read())
        else:
            zout.writestr(item, zin.read(item.filename))
    if not seen_repro:
        zout.write(RP_ZIP, 'CKI_Submission_v47/CKI_Reproducibility_Package.zip')
shutil.move(str(tmp), str(V47_ZIP))
print(f'v47 zip rewritten: {V47_ZIP.stat().st_size:,} B')

# ---- 4) 同步 WORK_DIR + 主目录 ----
shutil.copy2(RP_ZIP, V47_WD / 'CKI_Reproducibility_Package.zip')
(V47_WD / 'MANIFEST_v47.txt').write_text(manifest_new, encoding='utf-8')
main_copy = BASE / 'CKI_Submission_v47.zip'
shutil.copy2(V47_ZIP, main_copy)
print(f'main-dir copy: {main_copy.stat().st_size:,} B')

# ---- 5) 终检 ----
with zipfile.ZipFile(V47_ZIP) as z:
    names = z.namelist()
    assert len(names) == 34, len(names)
    assert 'CKI_Submission_v47/CKI_Reproducibility_Package.zip' in names
    mf = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')
    assert rp_sha in mf and f'({rp_size:,} bytes)' in mf
    assert '10. CKI_Reproducibility_Package.zip' in mf
    assert 'v47 (Genome Biology' in mf and 'v0.5.0' in mf  # banner intact
    inner = z.read('CKI_Submission_v47/CKI_Reproducibility_Package.zip')
    assert hashlib.sha256(inner).hexdigest() == rp_sha
    with zipfile.ZipFile(io.BytesIO(inner)) as rz:
        rn = rz.namelist()
    assert len(rn) == len(entries), (len(rn), len(entries))
    for must in ['results/hk_stability_sweep.csv', 'data/kang_ifnb/ensg2sym.tsv',
                 'notebooks/_ed_fig1_clean.py', '99_build_gb_v47.py',
                 'notebooks/_extract_table1_2.py']:
        assert must in rn, must
    for must in ['CKI_Submission_v47/CKI_Manuscript.docx',
                 'CKI_Submission_v47/figure6.pdf',
                 'CKI_Submission_v47/Supplementary_Figure_S13.pdf',
                 'CKI_Submission_v47/MANIFEST_v47.txt']:
        assert must in names
print('ALL FINALIZE CHECKS PASSED')
print(f'v47 entries: {len(names)} | repro nested: {len(rn)} files')
