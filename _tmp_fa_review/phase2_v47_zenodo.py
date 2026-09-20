# -*- coding: utf-8 -*-
"""v47 phase-2: MS Availability version DOI -> v0.5.0 record 10.5281/zenodo.22735744.
Byte-safe: python utf-8 read/write only. Mirrors synced by file copy."""
import io, os, shutil, sys

ROOT = r"C:\Users\KnightZ\Desktop\细胞受选择"
os.chdir(ROOT)

NEW_DOI = "10.5281/zenodo.22735744"
OLD_DOI = "10.5281/zenodo.22333850"

def edit(path, pairs):
    with io.open(path, encoding="utf-8") as f:
        t = f.read()
    for old, new, cnt in pairs:
        n = t.count(old)
        assert n == cnt, "%s: expected %d of %r, found %d" % (path, cnt, old[:60], n)
        t = t.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(t)
    print("edited:", path)

# ---- 99_build_gb_v47.py (root) ----
build_pairs = [
    # header docstring phase-1 note -> phase-2 DONE
    ("tag v0.5.0. MS Availability phase-1 keeps the v0.4.9 Zenodo\n"
     "record DOI (10.5281/zenodo.22333850); phase-2 writes the v0.5.0\n"
     "record DOI after the release.",
     "tag v0.5.0. MS Availability phase-2 DONE 2026-09-13: cites the\n"
     "v0.5.0 Zenodo record DOI (10.5281/zenodo.22735744).",
     1),
    # V45-2a assertion
    ('    v.check("10.5281/zenodo.22333850" in ms,\n'
     '            "V45-2a MS Zenodo version DOI for v0.4.9 (10.5281/zenodo.22333850)")',
     '    v.check("10.5281/zenodo.22735744" in ms,\n'
     '            "V45-2a MS Zenodo version DOI for v0.5.0 (10.5281/zenodo.22735744)")',
     1),
    # V46-i2 window string + message
    ("    v.check(all('22333850' in ms[h:h + 120]",
     "    v.check(all('22735744' in ms[h:h + 120]", 1),
    ('f"V46-i2 MS v0.4.9 only on phase-1 DOI line ({len(_hits)} hits)")',
     'f"V46-i2 MS v0.4.9 only near Zenodo DOI line, phase-2 ({len(_hits)} hits)")', 1),
    # V47-10c phase-1 -> phase-2 + stale-absence check
    ('    v.check("version DOI for v0.4.9: 10.5281/zenodo.22333850" in ms,\n'
     '            "V47-10c MS phase-1 Zenodo line cites v0.4.9 record")',
     '    v.check("version DOI for v0.5.0: 10.5281/zenodo.22735744" in ms,\n'
     '            "V47-10c MS phase-2 Zenodo line cites v0.5.0 record")\n'
     '    v.check("10.5281/zenodo.22333850" not in ms,\n'
     '            "V47-10c2 stale v0.4.9 record DOI absent from MS")',
     1),
    # trailing docstring
    ("Package released as tag v0.5.0. MS Availability phase-1 cites the\n"
     "v0.4.9 Zenodo record (10.5281/zenodo.22333850); the v0.5.0\n"
     "record DOI is written in phase-2 after the release.",
     "Package released as tag v0.5.0. MS Availability phase-2 cites the\n"
     "v0.5.0 Zenodo record (10.5281/zenodo.22735744). Phase-2 DONE\n"
     "2026-09-13.",
     1),
]
edit("99_build_gb_v47.py", build_pairs)

# ---- generate_manuscript_gb.py (root) ----
ms_pairs = [
    ("version DOI for v0.4.9: 10.5281/zenodo.22333850",
     "version DOI for v0.5.0: 10.5281/zenodo.22735744", 1),
]
edit("generate_manuscript_gb.py", ms_pairs)

# ---- sync mirrors ----
for fn in ["99_build_gb_v47.py", "generate_manuscript_gb.py"]:
    dst = os.path.join("CKI_Reproducibility_Package", fn)
    shutil.copyfile(fn, dst)
    print("mirror synced:", dst)

# ---- verify no stale v47-phase-1 refs remain in the two generators ----
for fn in ["99_build_gb_v47.py", "generate_manuscript_gb.py",
           os.path.join("CKI_Reproducibility_Package", "99_build_gb_v47.py"),
           os.path.join("CKI_Reproducibility_Package", "generate_manuscript_gb.py")]:
    t = io.open(fn, encoding="utf-8").read()
    assert OLD_DOI not in t, fn + " still has old DOI"
    assert NEW_DOI in t, fn + " missing new DOI"
print("ALL PHASE-2 EDITS OK")
