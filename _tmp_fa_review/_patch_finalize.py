import io
p = r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\finalize_v47_release.py'
t = io.open(p, encoding='utf-8').read()

old = """pat = re.compile(
    r'  [0-9a-f]{64}  CKI_Reproducibility_Package\\.zip \\([\\d,]+ bytes\\)')
m = pat.search(manifest)
assert m, 'repro checksum line not found in MANIFEST'
new_line = f'  {rp_sha}  CKI_Reproducibility_Package.zip ({rp_size:,} bytes)'
manifest_new = manifest[:m.start()] + new_line + manifest[m.end():]
print('MANIFEST checksum line updated')

tmp = BASE / '_tmp_fa_review' / 'CKI_Submission_v47_rezip2.zip'
with zipfile.ZipFile(V47_ZIP) as zin, \\
     zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
    for item in zin.infolist():
        if item.filename == 'CKI_Submission_v47/MANIFEST_v47.txt':
            zout.writestr(item, manifest_new)
        elif item.filename == 'CKI_Submission_v47/CKI_Reproducibility_Package.zip':
            with open(RP_ZIP, 'rb') as f:
                zout.writestr(item, f.read())
        else:
            zout.writestr(item, zin.read(item.filename))
shutil.move(str(tmp), str(V47_ZIP))
print(f'v47 zip rewritten: {V47_ZIP.stat().st_size:,} B')"""

new = """pat = re.compile(
    r'  [0-9a-f]{64}  CKI_Reproducibility_Package\\.zip \\([\\d,]+ bytes\\)')
m = pat.search(manifest)
new_line = f'  {rp_sha}  CKI_Reproducibility_Package.zip ({rp_size:,} bytes)'
NL = "\\r\\n"
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
with zipfile.ZipFile(V47_ZIP) as zin, \\
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
print(f'v47 zip rewritten: {V47_ZIP.stat().st_size:,} B')"""

assert t.count(old) == 1, 'anchor count %d' % t.count(old)
t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('finalize script patched')
