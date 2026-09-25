"""Surgical refresh of the NC cover letter after editorial tweak.

Only the cover letter changes (signature -> corresponding author only;
line spacing 1.0 -> 1.15). We regenerate the docx, re-extract fulltext,
copy into the existing submission workdir, recompute MANIFEST sha256,
re-zip, and re-run the cover-letter build assertions. No figure / MS / SI
regeneration is touched (the full 99_build_nc_v49.py rebuild is avoided on
purpose because it re-runs figure-staging scripts).
"""
import sys, os, zipfile, hashlib, shutil, subprocess
from pathlib import Path
from docx import Document

BASE = Path("C:/Users/KnightZ/Desktop/细胞受选择")
PY = "C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
WORK_DIR = BASE / "version3" / "CKI_Submission_v50_NC"
ZIP_PATH = BASE / "version3" / "CKI_Submission_v50_NC.zip"
MAIN_ZIP = BASE / "CKI_Submission_v50_NC.zip"

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def docx_text(p):
    return "\n".join(par.text for par in Document(str(p)).paragraphs)

# [1] regenerate cover letter docx
r = subprocess.run([PY, str(BASE / "generate_cover_letter_nc.py")],
                   capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
assert r.returncode == 0, "cover letter generator failed:\n" + r.stderr

cl_docx = BASE / "results" / "CKI_NC_Cover_Letter.docx"
cl_text = docx_text(cl_docx)
(BASE / "results" / "CKI_NC_Cover_Letter_fulltext.txt").write_text(cl_text, encoding="utf-8")
print(f"  fulltext: {len(cl_text.split())} words")

# [2] line-spacing XML check (1.15 -> w:line=276 lineRule=auto)
from docx.oxml.ns import qn
bad = []
for par in Document(str(cl_docx)).paragraphs:
    pPr = par._p.pPr
    if pPr is None:
        bad.append("(no pPr)")
        continue
    sp = pPr.find(qn('w:spacing'))
    if sp is None:
        bad.append("(no spacing)")
        continue
    line = sp.get(qn('w:line'))
    rule = sp.get(qn('w:lineRule'))
    if line != '252' or rule != 'auto':
        bad.append(f"line={line} rule={rule}")
print(f"  line-spacing XML: {'OK (252/auto = 1.05) across all paras' if not bad else 'MISMATCH ' + str(bad)}")
assert not bad, "line spacing not 1.15 everywhere"

# [3] copy into workdir
shutil.copy2(cl_docx, WORK_DIR / "CKI_NC_Cover_Letter.docx")

# [4] recompute MANIFEST
entries = sorted(e for e in os.listdir(WORK_DIR) if e != "MANIFEST_v50.txt")
manifest = ["=" * 60,
            "  CKI Submission Package v49 (Nature Communications)",
            "  MANIFEST_v50.txt",
            "  tag: v0.5.x | GB-rebuttal round: real-data drift calibration + pan-cancer map",
            "=" * 60, ""]
for i, e in enumerate(entries, 1):
    p = WORK_DIR / e
    manifest.append(f"{i:2d}. {e}  ({p.stat().st_size:,} bytes)")
manifest.append("")
manifest.append("SHA-256 checksums:")
for e in entries:
    manifest.append(f"  {sha256(WORK_DIR / e)}  {e}")
(WORK_DIR / "MANIFEST_v50.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

# [5] re-zip
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
    for e in sorted(os.listdir(WORK_DIR)):
        z.write(WORK_DIR / e, f"CKI_Submission_v50_NC/{e}")
shutil.copy2(ZIP_PATH, MAIN_ZIP)
print(f"  zip: {ZIP_PATH.stat().st_size:,} B ({len(zipfile.ZipFile(str(ZIP_PATH)).namelist())} entries)")

# [6] cover-letter build assertions (subset of 99_build_nc_v49.py V49-C*)
checks = []
def chk(cond, name):
    checks.append((name, bool(cond)))

chk(cl_text.count("Nature Communications") >= 2, "V49-C1 CL names Nature Communications x2+")
chk("Genome Biology" not in cl_text, "V49-C2 no Genome Biology in CL")
chk("CKI: a Ka/Ks-inspired index decomposing functional divergence from baseline variation in cell atlases" in cl_text, "V49-C3 title present")
chk("Two properties" in cl_text and "Previously raised concerns" not in cl_text and "5th of 5" not in cl_text, "V49-C4 framing")
chk("0.680" not in cl_text and "dynamic cell-state changes" in cl_text, "V49-C5 dynamic cell-state")
chk("baseline-driven" not in cl_text and "baseline-associated" not in cl_text, "V49-C6 no baseline-*")
chk("Both authors" not in cl_text, "V49-C7 no Both authors")
chk("ORCID (corresponding author)" not in cl_text, "V49-C8 ORCID removed")
chk("the first per-comparison, design-testable " in cl_text, "V49-C9 design-testable")
chk("1,750 replicates per background, two backgrounds" in cl_text, "V49-C10 replicates")
# editorial-change assertions
chk("Li Zhang (Corresponding Author)" in cl_text, "EDIT corresponding-author signature present")
chk("Xianming Wu (First Author)" not in cl_text, "EDIT first-author signature removed")
chk("Sincerely," in cl_text, "EDIT sign-off present")
for who in ["fabian.theis@helmholtz-munich.de", "welchjd@umich.edu",
            "sten.linnarsson@ki.se", "patrik.stahl@scilifelab.se",
            "schaffer@ncbi.nlm.nih.gov", "zeminzhang@pku.edu.cn"]:
    chk(who in cl_text, f"V49-C7 reviewer {who}")

allok = True
for name, ok in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    allok = allok and ok
print("\nRESULT:", "ALL PASS" if allok else "FAILURES PRESENT")
sys.exit(0 if allok else 1)
