#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build CKI Submission Package v49 (Nature Communications, GB-rebuttal round).

v49 = v48 + real-data neutral-drift calibration (Kang + brain ladder) +
pan-cancer tissue-level divergence map (upgrade from exploratory):
- MS: new Results section (drift calibration) + Result 4 rewritten as
  discovery-level pan-cancer section; Figures 4 (drift ladder) & 5 (TCGA)
  new; old Fig 4-6 -> Fig 6-7 (old TCGA fig dropped); Abstract 144 words
- SN: new Sections 3.20 (real-data calibration) & 3.21 (TCGA per-sample
  stats) under themed section 3; Notes 1-15 unchanged
- CL: repositioned (first principled drift/functional-divergence
  separation framework; direct rebuttal of the two GB concerns)
- Guide unchanged from v48

Verification = workers' self-check scripts (results/audit/_nc49_ms_verify.py,
_nc49_si_verify.py) + v48-era guide check + inline SN/CL checks +
package integrity + scientific anchors (v48 subset + v49 additions).
"""
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

BASE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择")
PY = r"C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
NODE = r"C:\Users\KnightZ\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
NODE_ENV = dict(os.environ, NODE_PATH=r"C:\Users\KnightZ\.workbuddy\binaries\node\workspace\node_modules")

STAGE = BASE / "results" / "figures_v47_author"
FIGS_NC = BASE / "results" / "figures_submission_nc"
FF = BASE / "results" / "figures_final"
WORK_DIR = BASE / "version3" / "CKI_Submission_v49_NC"
ZIP_PATH = BASE / "version3" / "CKI_Submission_v49_NC.zip"
FA = BASE / "_tmp_fa_review"
AUD = BASE / "results" / "audit"

FAILS = []
PASSES = []


def check(ok, name):
    if ok:
        PASSES.append(name)
        print(f"  [OK] {name}")
    else:
        FAILS.append(name)
        print(f"  [FAIL] {name}")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, name, env=None, cwd=None):
    print(f"\n--- {name} ---")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=cwd or str(BASE))
    tail = "\n".join(r.stdout.splitlines()[-6:])
    print(tail)
    if r.returncode != 0:
        print(r.stderr[-1500:])
    check(r.returncode == 0, f"run: {name}")


def docx_text(p):
    from docx import Document
    return "\n".join(par.text for par in Document(str(p)).paragraphs)


def main():
    print("=" * 60)
    print("  CKI Submission Package v49 (NC, GB-rebuttal round) Builder")
    print("=" * 60)

    # ---- [0] figures staging -> v49 naming ----
    print("\n[0] Collecting figures into figures_submission_nc ...")
    FIGS_NC.mkdir(parents=True, exist_ok=True)
    _arch1 = BASE / "_tmp_archive" / "v49_build_figs_cleanup"
    for old in os.listdir(FIGS_NC):
        _arch1.mkdir(parents=True, exist_ok=True)
        shutil.move(str(FIGS_NC / old), str(_arch1 / old))
    # main figures: 1-3 unchanged; 4 = drift ladder (new); 5 = TCGA map (new);
    # 6 = old figure5 (cross-organ); 7 = old figure6 (brain); old figure4 dropped
    for i in (1, 2, 3):
        shutil.copy2(STAGE / f"figure{i}.pdf", FIGS_NC / f"figure{i}.pdf")
    shutil.copy2(FF / "nc49_fig_drift_ladder.pdf", FIGS_NC / "figure4.pdf")
    shutil.copy2(FF / "nc49_fig_tcga.pdf", FIGS_NC / "figure5.pdf")
    shutil.copy2(STAGE / "figure5.pdf", FIGS_NC / "figure6.pdf")
    shutil.copy2(STAGE / "figure6.pdf", FIGS_NC / "figure7.pdf")
    for i in range(1, 14):
        shutil.copy2(STAGE / f"figure_S{i}.pdf", FIGS_NC / f"Supplementary_Fig_{i}.pdf")
    shutil.copy2(STAGE / "CKI_graphical_abstract.pdf",
                 FIGS_NC / "CKI_graphical_abstract.pdf")
    n_fig = len(os.listdir(FIGS_NC))
    check(n_fig == 21, f"V49-1 figures staged = 21 (7 main + 13 supp + GA pdf) got {n_fig}")

    # ---- [1] work dir ----
    print("\n[1] Preparing CKI_Submission_v49_NC ...")
    if WORK_DIR.exists():
        _arch2 = BASE / "_tmp_archive" / "v49_build_workdir_cleanup"
        for old in os.listdir(WORK_DIR):
            _arch2.mkdir(parents=True, exist_ok=True)
            shutil.move(str(WORK_DIR / old), str(_arch2 / old))
    else:
        WORK_DIR.mkdir(parents=True)
    for f in os.listdir(FIGS_NC):
        shutil.copy2(FIGS_NC / f, WORK_DIR / f)

    # ---- [2] regenerate DOCX ----
    print("\n[2] Regenerating DOCX files ...")
    run([PY, str(BASE / "generate_manuscript_nc.py")], "Generate Manuscript (NC v49)")
    run([PY, str(BASE / "notebooks" / "68_gen_supplementary_nc.py")], "Generate Supplementary (NC v49)")
    run([PY, str(BASE / "generate_cover_letter_nc.py")], "Generate Cover Letter (NC v49)")
    run([NODE, str(BASE / "notebooks" / "100_gen_reproducibility_nc.js")], "Generate Repro Guide (NC)", env=NODE_ENV)

    docx_files = {
        "CKI_Manuscript_NC.docx": BASE / "results" / "CKI_Manuscript_NC.docx",
        "CKI_Supplementary_NC.docx": BASE / "results" / "CKI_Supplementary_NC.docx",
        "CKI_NC_Cover_Letter.docx": BASE / "results" / "CKI_NC_Cover_Letter.docx",
        "CKI_Reproducibility_Guide_NC.docx": BASE / "results" / "CKI_Reproducibility_Guide_NC.docx",
    }
    for name, p in docx_files.items():
        check(p.exists() and p.stat().st_size > 10000, f"DOCX exists: {name}")

    # ---- [2f] fulltext ----
    print("\n[2f] Extracting fulltext ...")
    texts = {}
    for name, p in docx_files.items():
        t = docx_text(p)
        texts[name] = t
        ft = BASE / "results" / (name.replace(".docx", "_fulltext.txt"))
        ft.write_text(t, encoding="utf-8")
        print(f"  {ft.name}: {ft.stat().st_size:,} bytes")

    # ---- [3] copy DOCX into workdir + MANIFEST ----
    for name, p in docx_files.items():
        shutil.copy2(p, WORK_DIR / name)
    xlsx_src = BASE / "results" / "CKI_Tables_NC.xlsx"
    check(xlsx_src.exists() and xlsx_src.stat().st_size > 4000, "Tables xlsx exists")
    shutil.copy2(xlsx_src, WORK_DIR / "CKI_Tables_NC.xlsx")

    manifest = ["=" * 60,
                "  CKI Submission Package v49 (Nature Communications)",
                "  MANIFEST_v49.txt",
                "  tag: v0.5.x | GB-rebuttal round: real-data drift calibration + pan-cancer map",
                "=" * 60, ""]
    entries = sorted(os.listdir(WORK_DIR))
    for i, e in enumerate(entries, 1):
        p = WORK_DIR / e
        manifest.append(f"{i:2d}. {e}  ({p.stat().st_size:,} bytes)")
    manifest.append("")
    manifest.append("SHA-256 checksums:")
    for e in entries:
        manifest.append(f"  {sha256(WORK_DIR / e)}  {e}")
    mtext = "\n".join(manifest) + "\n"
    (WORK_DIR / "MANIFEST_v49.txt").write_text(mtext, encoding="utf-8")

    # ---- [4] zip ----
    print("\n[4] Creating ZIP ...")
    if ZIP_PATH.exists():
        _arch3 = BASE / "_tmp_archive" / "v49_build_zip_backup"
        _arch3.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ZIP_PATH), str(_arch3 / ZIP_PATH.name))
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for e in sorted(os.listdir(WORK_DIR)):
            z.write(WORK_DIR / e, f"CKI_Submission_v49_NC/{e}")
    main_copy = BASE / "CKI_Submission_v49_NC.zip"
    shutil.copy2(ZIP_PATH, main_copy)
    print(f"  zip: {ZIP_PATH.stat().st_size:,} B ({len(zipfile.ZipFile(ZIP_PATH).namelist())} entries)")

    # ================= VERIFICATION =================
    print("\n" + "=" * 60)
    print("  v49 Verification")
    print("=" * 60)

    ms = texts["CKI_Manuscript_NC.docx"]
    sn = texts["CKI_Supplementary_NC.docx"]
    cl = texts["CKI_NC_Cover_Letter.docx"]
    gd = texts["CKI_Reproducibility_Guide_NC.docx"]

    # ---- workers' self-check scripts (must exit 0) ----
    run([PY, str(AUD / "_nc49_ms_verify.py")], "nc49 MS self-check")
    run([PY, str(AUD / "_nc49_si_verify.py")], "nc49 SI self-check")
    run([PY, str(AUD / "_nc49_cl_guide_verify.py")], "nc49 CL+Guide self-check")

    # ---- SN inline checks ----
    print("\n--- SN (inline) ---")
    check(not re.search(r"Note [345]\.\d", sn), "V49-S1 no decimal Note refs in SN")
    check("Fig. S" not in sn and "Figure S" not in sn, "V49-S2 no Fig. S in SN")
    check("Table S" not in sn, "V49-S3 no Table S in SN")
    check("Additional file" not in sn, "V49-S4 no Additional file in SN")
    note_heads = sorted(set(int(m.group(1)) for m in re.finditer(r"Supplementary Note (\d+):", sn)))
    check(note_heads == list(range(1, 16)), f"V49-S5 SN Note headings 1..15 ({note_heads})")
    n_sfig_sn = len(re.findall(r"Supplementary Fig\. \d+", sn))
    check(n_sfig_sn == 8, f"V49-S6 SN Supplementary Fig. refs = 8 ({n_sfig_sn})")
    n_stab_sn = len(re.findall(r"Supplementary Table \d+", sn))
    check(n_stab_sn == 14, f"V49-S7 SN Supplementary Table refs = 14 ({n_stab_sn})")
    check("Section 3.12" in sn and "Section 3.13" in sn, "V49-S8 SN Sections 3.12/3.13 present (renumbered from 3.20/3.21)")
    check("TODO" not in sn, "V49-S9 no TODO in SN")

    # ---- Guide inline checks (v49 caliber) ----
    check("Supplementary Note 13" in gd, "V49-G1 Guide cites Supplementary Note 13")
    check("Section 3.9 of the Supplementary Information" in gd, "V49-G2 Guide Section 3.9 pointer (renumbered from 3.11)")
    check(not re.search(r"Note [345]\.\d", gd), "V49-G3 no decimal Note refs in Guide")
    check("Fig. S" not in gd and "Table S" not in gd, "V49-G4 no S-naming in Guide")

    # ---- CL inline checks (v49.1 new-evidence frame) ----
    check(cl.count("Nature Communications") >= 2, "V49-C1 CL names Nature Communications x2+")
    check("Genome Biology" not in cl, "V49-C2 no Genome Biology in CL")
    check("CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics" in cl,
          "V49-C3 CL carries the NC title")
    check("Two properties" in cl and "Previously raised concerns" not in cl and "5th of 5" not in cl,
          "V49-C4 CL new-evidence frame (no rebuttal-speak, no 5th-of-5)")
    check("0.680" in cl, "V49-C5 CL cites AUC 0.680 (by-design admission)")
    check("baseline-driven" not in cl and "baseline-associated" not in cl,
          "V49-C5b no baseline-* phrasing in CL (EGFR dissolved)")
    check("Both authors" not in cl, "V49-C6 CL declarations paragraph removed")
    for who in ("Theis", "Welch", "Linnarsson", "Sch", "Zemin Zhang"):
        check(who in cl, f"V49-C7 CL reviewer: {who}")
    n_cl_words = len(cl.split())
    check(420 <= n_cl_words <= 560, f"V49-C8 CL one-page word budget ({n_cl_words})")

    # ---- scientific regression anchors (v48 subset) ----
    print("\n--- scientific anchors (v48 subset) ---")
    anchors = [
        ("[7.37, 8.02]", "A2 calibration CI"),
        ("1.74 [1.64, 1.84]", "A3 equal-n gradient"),
        ("0.442", "A4 Augur OvR vs omega"),
        ("0.564", "A5 Augur OvR vs k_f"),
        ("24,413", "A6 Kang cells"),
        ("4,851", "A7 human pairs (phase35)"),
        ("31,764", "A8 brain pairs"),
        ("148.3", "A9 null expectation"),
        ("AUC = 0.80", "A10 AUC"),
        ("6.10-fold", "A11 regional gradient"),
        ("1.3-fold", "A13 ratio bias"),
        ("7.70", "A14 omega baseline"),
        ("10.5281/zenodo.22735744", "A15 Zenodo v0.5.0 DOI"),
        ("GSE96583", "A16 Kang GEO"),
        ("GSE109774", "A17 TCGA/brain GEO in Data availability"),
    ]
    for pat, name in anchors:
        check(pat in ms, f"V49-{name}")
    check("0.953" in sn and "0.951" in sn, "V49-A12 bootstrap-t coverage (SN)")

    # ---- v49 new-content anchors ----
    print("\n--- v49 new-content anchors ---")
    v49_anchors = [
        # drift calibration (Kang + brain ladder)
        ("0.963", "N1 Kang omega calibration median"),
        ("36.7", "N2 Kang raw-JS FPR"),
        ("23.3", "N3 Kang cosine FPR"),
        ("2,161", "N4 brain T1 pairs"),
        ("28.6", "N5 brain T1 omega FPR"),
        ("90.9", "N6 brain T2 omega FPR"),
        ("1.41", "N7 marker-Jaccard T3 calibration"),
        ("relative-calibration advantage", "N8 relative-calibration phrasing"),
        ("Section 3.12 of the Supplementary Information", "N9 Section 3.12 pointer x2"),
        # pan-cancer map
        ("2.46", "N10 LUAD NN/TT ratio"),
        ("LIHC 1.10 (0.93", "N11 LIHC NN/TT ratio (post-CC)"),
        ("1.3\u20133.3-fold (mean ratios", "N12 k_n fold elevation (mean, post-CC)"),
        ("136.9", "N13 LUAD KRAS mean omega"),
        ("115.4", "N14 LUAD WT mean omega"),
        ("tissue-level functional divergence", "N15 bulk positioning phrase"),
        ("0.88\u20131.31", "N16 Cox HR CI post-CC (NO-GO)"),
    ]
    for pat, name in v49_anchors:
        check(pat in ms, f"V49-{name}")
    check(ms.count("Section 3.12 of the Supplementary Information") == 3,
          "V49-N17 exactly 3 Section 3.12 pointers in MS (post-CC)")
    # old exploratory phrasing must be gone
    for stale in ("TCGA; exploratory", "apparent tumor homogeneity", "TODO-nc49"):
        check(stale not in ms, f"V49-N18 stale gone: '{stale}'")
    # figure legends 1-7 order + new figure identity
    for i in range(1, 8):
        check(f"Figure {i}." in ms, f"V49-N19 Figure {i} legend present")
    check("drift" in ms[ms.find("Figure 4."):ms.find("Figure 4.") + 400].lower(),
          "V49-N20 Figure 4 legend is drift ladder")
    check("pan-cancer" in ms[ms.find("Figure 5."):ms.find("Figure 5.") + 400].lower(),
          "V49-N21 Figure 5 legend is pan-cancer map")
    # Abstract word count <= 200 (v49.1: NC abstract limit is 200)
    ai = ms.find("Abstract")
    ab_para = ms[ai:].split("\n")
    ab_text = next((t for t in ab_para[1:] if len(t.split()) > 40), "")
    check(0 < len(ab_text.split()) <= 200,
          f"V49-N22 Abstract words <= 200 ({len(ab_text.split())})")
    # v49.1 post-repair anchors (purity / smoking / EGFR-dissolved)
    for pat, name in [("16.8", "N23 purity-adjusted KRAS omega"),
                      ("13.6", "N24 joint-adjusted KRAS omega"),
                      ("2.86", "N25 high-purity LUAD ratio"),
                      ("stromal or immune admixture", "N27 admixture caveat phrase")]:
        check(pat in ms, f"V49-{name}")
    check("8.3 \u00d7 10\u207b\u00b9\u2077" in sn, "V49-N26 KIRC kn~admix P post-CC (SN)")
    check("baseline-driven" not in ms and "baseline-associated" not in ms,
          "V49-N28 no baseline-* phrasing in MS (EGFR dissolved)")
    # v49.2 post-CC anchors + stale purge
    for pat, name in [("3,567", "N29 sample total post-CC"),
                      ("1.10\u20132.46", "N30 Abstract ratio range post-CC"),
                      ("P = 0.48", "N31 Cox P post-CC")]:
        check(pat in ms, f"V49-{name}")
    for stale in ("1.822", "1.133", "1.895", "1.13\u20132.46"):
        check(stale not in ms, f"V49-N32 stale gone from MS: '{stale}'")
    check("78.2, 76.8, 77.9, 72.6" in sn and "6.9 \u00d7 10\u207b\u00b9\u2075" in sn,
          "V49-N33 Note 9 LIHC severity post-CC (SN prose)")
    for stale in ("82.4 / 74.7", "1.05 \u00d7 10\u207b\u00b9\u00b2", "about 10-19"):
        check(stale not in sn, f"V49-N34 stale gone from SN: '{stale}'")

    # ---- structural re-checks ----
    print("\n--- structural spot checks ---")
    check("Here, we show" in ms, "V49-SC1 Introduction ends 'Here, we show'")
    check(ms.count("Conclusions") == 0, "V49-SC3 no 'Conclusions' anywhere")
    check("Keywords:" not in ms, "V49-SC4 no Keywords line")
    check("Supplementary Note 1" in ms and "Supplementary Note 15" in ms, "V49-SC5 notes 1/15 cited")
    check("Supplementary Fig. 1" in ms, "V49-SC6 supp fig 1 cited")

    # ---- package integrity ----
    print("\n--- package integrity ---")
    names = zipfile.ZipFile(ZIP_PATH).namelist()
    check(all(n.startswith("CKI_Submission_v49_NC/") for n in names), "V49-P1 zip rooted")
    for must in ["CKI_Submission_v49_NC/CKI_Manuscript_NC.docx",
                 "CKI_Submission_v49_NC/CKI_Supplementary_NC.docx",
                 "CKI_Submission_v49_NC/CKI_NC_Cover_Letter.docx",
                 "CKI_Submission_v49_NC/CKI_Reproducibility_Guide_NC.docx",
                 "CKI_Submission_v49_NC/MANIFEST_v49.txt",
                 "CKI_Submission_v49_NC/Supplementary_Fig_1.pdf",
                 "CKI_Submission_v49_NC/Supplementary_Fig_13.pdf",
                 "CKI_Submission_v49_NC/figure4.pdf",
                 "CKI_Submission_v49_NC/figure5.pdf",
                 "CKI_Submission_v49_NC/figure7.pdf",
                 "CKI_Submission_v49_NC/CKI_graphical_abstract.pdf",
                 "CKI_Submission_v49_NC/CKI_Tables_NC.xlsx"]:
        check(must in names, f"V49-P2 {must.split('/')[-1]}")
    n_oldname = [n for n in names if "figure_S" in n or "Supplementary_Figure_S" in n]
    check(not n_oldname, f"V49-P3 no old supp figure naming ({n_oldname})")
    check(not any(n.endswith((".png", ".svg", "_fulltext.txt")) for n in names),
          "V49-P4 pdf-only figures + word-only docs (no png/svg/txt)")
    from docx import Document as _DocxCheck
    check(len(_DocxCheck(str(BASE / "results" / "CKI_Manuscript_NC.docx")).tables) == 0,
          "V49-P5 MS docx contains no tables (tables live in CKI_Tables_NC.xlsx)")

    print("\n" + "=" * 60)
    print(f"  Passed: {len(PASSES)}  Failed: {len(FAILS)}")
    for f in FAILS:
        print(f"  [FAIL] {f}")
    if FAILS:
        print("\n  *** FAILURES — review above ***")
        sys.exit(1)
    print("\n  *** ALL CHECKS PASSED — v49 (NC GB-rebuttal) FINAL ***")


if __name__ == "__main__":
    main()
