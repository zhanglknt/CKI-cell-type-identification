# -*- coding: utf-8 -*-
"""finalize_v47_release.py 第 3b-5 步续接（钩子拦截后续）：
从已生成的 tmp zip 完成 move + WORK_DIR/主目录同步 + 终检"""
from pathlib import Path
import zipfile, hashlib, shutil, io

BASE = Path(r'C:/Users/KnightZ/Desktop/细胞受选择')
RP_ZIP = BASE / 'CKI_Reproducibility_Package.zip'
V47_ZIP = BASE / 'version3' / 'CKI_Submission_v47.zip'
V47_WD = BASE / 'version3' / 'CKI_Submission_v47'
tmp = BASE / '_tmp_fa_review' / 'CKI_Submission_v47_rezip2.zip'

assert tmp.exists(), 'tmp zip missing'
rp_sha = hashlib.sha256(RP_ZIP.read_bytes()).hexdigest()
rp_size = RP_ZIP.stat().st_size

# move tmp -> version3 zip（目标已归档不存在，不触发覆盖删除）
shutil.move(str(tmp), str(V47_ZIP))
print(f'v47 zip rewritten: {V47_ZIP.stat().st_size:,} B')

# ---- 4) 同步 WORK_DIR + 主目录 ----
manifest_new = None
with zipfile.ZipFile(V47_ZIP) as z:
    manifest_new = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')
shutil.copy2(RP_ZIP, V47_WD / 'CKI_Reproducibility_Package.zip')
(V47_WD / 'MANIFEST_v47.txt').write_text(manifest_new, encoding='utf-8')
main_copy = BASE / 'CKI_Submission_v47.zip'
shutil.copy2(V47_ZIP, main_copy)
print(f'main-dir copy: {main_copy.stat().st_size:,} B')

# ---- 5) 终检（与 finalize_v47_release.py 相同）----
with zipfile.ZipFile(V47_ZIP) as z:
    names = z.namelist()
    assert len(names) == 34, len(names)
    assert 'CKI_Submission_v47/CKI_Reproducibility_Package.zip' in names
    mf = z.read('CKI_Submission_v47/MANIFEST_v47.txt').decode('utf-8')
    assert rp_sha in mf and f'({rp_size:,} bytes)' in mf
    assert '10. CKI_Reproducibility_Package.zip' in mf
    assert 'v47 (Genome Biology' in mf and 'v0.5.0' in mf
    inner = z.read('CKI_Submission_v47/CKI_Reproducibility_Package.zip')
    assert hashlib.sha256(inner).hexdigest() == rp_sha
    with zipfile.ZipFile(io.BytesIO(inner)) as rz:
        rn = rz.namelist()
    assert len(rn) == 297, len(rn)
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
print('v47 entries:', len(names), '| repro nested:', len(rn))
