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

# Rerun mode: skip the three _tmp_archive move blocks (safe-delete guard counts
# moves as deletes; a rerun right after a completed build only overwrites the
# same artifacts in place, so archiving adds no protection). The pre-run zip is
# already backed up under _tmp_archive/v49_build_zip_backup by the first run.
NO_ARCHIVE = os.environ.get("CKI_BUILD_NO_ARCHIVE") == "1"

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
    if not NO_ARCHIVE:
        for old in os.listdir(FIGS_NC):
            _arch1.mkdir(parents=True, exist_ok=True)
            shutil.move(str(FIGS_NC / old), str(_arch1 / old))
    # main figures v49.7: 6 main figures (Fig2 5-panel merged)
    #   1 = schematic (unchanged); 2 = merged: top row = mouse calibration
    #       (regenerated at 178 mm, Arial >= 7 pt); bottom row = D TS metric-
    #       correlation heatmap + E change-detection ROC (ground-truth
    #       simulation, omega AUC-first scenario; v49.7 native regen);
    #   3 = drift ladder; 4 = TCGA map; 5 = cross-organ; 6 = brain
    run([PY, str(BASE / "notebooks" / "_regen_fig2_toprow_nc49.py")],
        "Regen Fig2 top row (NC v49.6)")
    run([PY, str(BASE / "notebooks" / "_regen_fig2_bottomrow_v497.py")],
        "Regen Fig2 bottom row (NC v49.7)")
    run([PY, str(BASE / "notebooks" / "_merge_fig2_v497.py")],
        "Merge Fig2 (NC v49.7)")
    shutil.copy2(STAGE / "figure1.pdf", FIGS_NC / "figure1.pdf")
    shutil.copy2(FF / "figure2_merged_nc49.pdf", FIGS_NC / "figure2.pdf")
    shutil.copy2(FF / "nc49_fig_drift_ladder.pdf", FIGS_NC / "figure3.pdf")
    shutil.copy2(FF / "nc49_fig_tcga.pdf", FIGS_NC / "figure4.pdf")
    shutil.copy2(STAGE / "figure5.pdf", FIGS_NC / "figure5.pdf")
    shutil.copy2(STAGE / "figure6.pdf", FIGS_NC / "figure6.pdf")
    for i in range(1, 14):
        shutil.copy2(STAGE / f"figure_S{i}.pdf", FIGS_NC / f"Supplementary_Fig_{i}.pdf")
    run([PY, str(BASE / "notebooks" / "nc50_fig_microglia.py")],
        "Regen Supplementary Fig 14 (NC v50 microglia)")
    shutil.copy2(BASE / "results" / "Supplementary_Fig_14.pdf",
                 FIGS_NC / "Supplementary_Fig_14.pdf")
    shutil.copy2(STAGE / "CKI_graphical_abstract.pdf",
                 FIGS_NC / "CKI_graphical_abstract.pdf")
    n_fig = len(os.listdir(FIGS_NC))
    check(n_fig == 21, f"V49-1 figures staged = 21 (6 main + 14 supp + GA pdf; v50) got {n_fig}")

    # ---- [1] work dir ----
    print("\n[1] Preparing CKI_Submission_v49_NC ...")
    if WORK_DIR.exists():
        if not NO_ARCHIVE:
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
    si_xlsx_src = BASE / "results" / "CKI_Supplementary_Tables_NC.xlsx"
    check(si_xlsx_src.exists() and si_xlsx_src.stat().st_size > 4000,
          "SI Tables xlsx exists")
    shutil.copy2(si_xlsx_src, WORK_DIR / "CKI_Supplementary_Tables_NC.xlsx")

    manifest = ["=" * 60,
                "  CKI Submission Package v49 (Nature Communications)",
                "  MANIFEST_v49.txt",
                "  tag: v0.5.x | GB-rebuttal round: real-data drift calibration + pan-cancer map",
                "=" * 60, ""]
    entries = sorted(e for e in os.listdir(WORK_DIR) if e != "MANIFEST_v49.txt")
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
    if ZIP_PATH.exists() and not NO_ARCHIVE:
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
    check(note_heads == list(range(1, 17)), f"V49-S5 SN Note headings 1..16 (v50) ({note_heads})")
    n_sfig_sn = len(re.findall(r"Supplementary Fig\. \d+", sn))
    check(n_sfig_sn == 9, f"V49-S6 SN Supplementary Fig. refs = 9 (v50: +Fig. 14) ({n_sfig_sn})")
    n_stab_sn = len(re.findall(r"Supplementary Table \d+", sn))
    check(n_stab_sn == 41, f"V49-S7 SN Supplementary Table refs = 41 post-v49.5 ({n_stab_sn})")
    check("3.12 Real-Data Neutral-Drift Calibration" in sn and "3.13 Per-Sample Divergence" in sn, "V49-S8 SN Sections 3.12/3.13 present (renumbered from 3.20/3.21)")
    check("TODO" not in sn, "V49-S9 no TODO in SN")

    # ---- Guide inline checks (v49 caliber) ----
    check("Supplementary Note 13" in gd, "V49-G1 Guide cites Supplementary Note 13")
    check("Section 3.9 of the Supplementary Information" in gd, "V49-G2 Guide Section 3.9 pointer (renumbered from 3.11)")
    check(not re.search(r"Note [345]\.\d", gd), "V49-G3 no decimal Note refs in Guide")
    check("Fig. S" not in gd and "Table S" not in gd, "V49-G4 no S-naming in Guide")

    # ---- CL inline checks (v49.1 new-evidence frame) ----
    check(cl.count("Nature Communications") >= 2, "V49-C1 CL names Nature Communications x2+")
    check("Genome Biology" not in cl, "V49-C2 no Genome Biology in CL")
    check("CKI: a Ka/Ks-inspired index separating functional divergence from baseline variation in cell atlases" in cl,
          "V49-C3 CL carries the NC title")
    check("Two properties" in cl and "Previously raised concerns" not in cl and "5th of 5" not in cl,
          "V49-C4 CL new-evidence frame (no rebuttal-speak, no 5th-of-5)")
    check("0.680" not in cl and "dynamic cell-state changes" in cl,
          "V49-C5 CL change-detection framing (no classification AUC)")
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
        ("1.74-fold size-balanced regional gradient ([1.64, 1.84]", "A3 equal-n gradient"),
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
        ("LIHC 1.10;", "N11 LIHC NN/TT ratio (post-CC, v50 wording)"),
        ("1.3\u20133.3-fold in every cancer type", "N12 k_n fold elevation (v50 wording)"),
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
    # figure legends 1-6 order + new figure identity (v49.6: 6 main figures)
    for i in range(1, 7):
        check(f"Figure {i}." in ms, f"V49-N19 Figure {i} legend present")
    check("drift" in ms[ms.find("Figure 3."):ms.find("Figure 3.") + 400].lower(),
          "V49-N20 Figure 3 legend is drift ladder")
    check("pan-cancer" in ms[ms.find("Figure 4."):ms.find("Figure 4.") + 400].lower(),
          "V49-N21 Figure 4 legend is pan-cancer map")
    check("functional-change detection" in ms[ms.find("Figure 2."):ms.find("Figure 2.") + 300].lower()
          and "(e) ROC curves for discriminating injected functional signal" in ms[ms.find("Figure 2."):ms.find("Figure 3.")],
          "V49-N21b Figure 2 legend: calibration + TS correlation + change-detection ROC (panels a-e)")
    # Abstract word count <= 200 (v49.1: NC abstract limit is 200)
    ai = ms.find("Abstract")
    ab_para = ms[ai:].split("\n")
    ab_text = next((t for t in ab_para[1:] if len(t.split()) > 40), "")
    check(0 < len(ab_text.split()) <= 200,
          f"V49-N22 Abstract words <= 200 ({len(ab_text.split())})")
    # v49.1 post-repair anchors (purity / smoking / EGFR-dissolved)
    check("2.86" in ms, "V49-N25 high-purity LUAD ratio")
    check("fully explained by admixture" in ms, "V49-N27 admixture caveat phrase (v50)")
    # v50: adjusted-delta details migrated to SI 3.13
    check("\u0394\u03c9 +16.8" in sn, "V49-N23 purity-adjusted KRAS omega (v50: SI 3.13)")
    check("+13.6" in sn, "V49-N24 joint-adjusted KRAS omega (v50: SI 3.13)")
    from openpyxl import load_workbook as _lwb
    _si_xlsx = _lwb(str(BASE / "results" / "CKI_Supplementary_Tables_NC.xlsx"))
    _si_caps = "\n".join(str(_si_xlsx[_sn]["A1"].value) for _sn in _si_xlsx.sheetnames)
    check("8.3 \u00d7 10\u207b\u00b9\u2077" in _si_caps,
          "V49-N26 KIRC kn~admix P post-CC (SuppTable 15 xlsx caption)")
    _main_xlsx = _lwb(str(BASE / "results" / "CKI_Tables_NC.xlsx"))
    check(_main_xlsx.sheetnames == ['Table 1']
          and str(_main_xlsx['Table 1']['A1'].value).startswith('Table 1. Cross-organ conservation'),
          "V49-N35 main Tables xlsx = single Table 1 sheet (cross-organ)")
    check('cell-type classification performance' not in ms and '0.680' not in ms
          and 'ranked 5th of 5 methods' not in ms,
          "V49-N36 classification benchmark cut from MS")
    check('(Fig. 5; Table 1; Supplementary Fig. 5)' in ms and 'upper block of Table 1' in ms
          and not re.search(r'(?<!Supplementary )Table 2', ms),
          "V49-N37 main Table 2 renumbered to Table 1")
    check('not to discriminate cell-type identity' in ms
          and 'housekeeping gene sets may differ across cell types' in ms
          and 'expected by design and delineates, rather than limits' in ms,
          "V49-N38 Scope design argument present (HK anchor cell-type-specific)")
    # ---- v49.10 review-panel fixes (A/B classes) ----
    check('Supplementary Tables 1\u201319' in ms
          and ms.count('Supplementary Tables 1\u20134') == 1
          and 'Supplementary Tables 1\u20134 are cited in the main text' in ms,
          "V49-N39 A1 MS availability lists 19 supplementary tables (v49.14: 1-4 pointer sentence)")
    check('concentrate in microglia (16 Strong) and oligodendrocytes (10)' in ms,
          "V49-N40 A5 brain candidate concentration (v50 wording)")
    check('median TT/NN k_n ratio 2.18, 2.53, 2.18, 3.70, and 2.79' in sn,
          "V49-N41 A6 mean/median caliber cross-pointer (v50: SI carries medians)")
    check('in main-text Fig. 3d.' in sn and 'main-text Fig. 3b,c.' in sn,
          "V49-N42 A2 SI main-text figure pointers corrected to Fig. 3")
    check('Fig. 4d' not in sn and 'Fig. 4b,c' not in sn,
          "V49-N42b A2 no stale Fig. 4 panel pointers in SI")
    check('(Table 1 / Fig. 5)' in sn and '(Table 2 / Fig. 5)' not in sn,
          "V49-N43 A3 SI Note 9 points to Table 1")
    check('main-text ref. 37' in sn and 'main-text ref. 56' not in sn,
          "V49-N44 A7 SI Note 14 Augur pointer = ref. 37")
    check('gene-set configuration criterion only' in sn,
          "V49-N45 B1 SI weight-scheme AUC reconciliation clause")
    check('McDonald\u2013Kreitman-style fourth term' in ms
          and '34. McDonald' in ms and 'Adh locus in Drosophila' in ms,
          "V49-N46 B2 MK fourth-term pointer + MK ref [34] (v50)")
    check('descriptive rather than calibrated differences' in ms,
          "V49-N47 B3 Table 1 cross-type caveat")
    check('1.74-fold size-balanced regional gradient ([1.64, 1.84]; 6.10-fold '
          'uncorrected; 3.68-fold span-matched intra-cerebellar)' in ms,
          "V49-N48 B4 Abstract leads with size-balanced gradient")
    check('leaving pair-level nominations subject to donor confounding' in ms,
          "V49-N49 B5 brain screen donor-confounding disclosure")
    check('sample-source code (positions 14\u201315)' in ms
          and 'assigned to LIHC following a barcode audit' in ms,
          "V49-N50 B7 CC provenance disclosure (32 LUSC->LIHC)")
    check('2.5th and 97.5th percentiles of the resampled ratios' in ms,
          "V49-N51 B8 TCGA cluster-bootstrap interval type stated (percentile)")
    check('Supplementary Fig. 7)' in gd and 'Supplementary Fig. 8)' not in gd,
          "V49-N52 A4 Guide estimator-comparison pointer = Fig. 7")
    # ---- v49.12 review-panel leftovers (N1-N5, C2-C7) ----
    check('which used seed 20260903, and the small-cluster studentized bootstrap-t analysis '
          '(notebooks/89_cluster_boot_v45.py), which used seed 20260905' in ms,
          "V49-N56 N1 seed 20260905 declared in MS Methods")
    check('notebook 89 uses seed 20260905' in gd,
          "V49-N56b N1 seed 20260905 in Guide checklist")
    check('supersedes the earlier i.i.d. interval' in ms
          and 'influence-function (multiplier) sandwich standard error' in ms
          and 'Monte Carlo coverage 0.953/0.951 at 6\u20137 clusters' in ms,
          "V49-N57 C6 studentized bootstrap-t pivot/SE described")
    check('attenuates by only \u22121.3% pooled (95% CI [\u22124.8%, +2.0%]; per-cancer \u221216% to +33%)' in ms
          and 'attenuates by \u22120.5% pooled' not in ms
          and 'Spearman \u03c1 = 0.364 pooled; 0.20\u20130.51 per cancer type' in ms
          and '0.387 pooled' not in ms,
          "V49-N58 N2 Discussion composition numbers (v50 wording)")
    check('\u22121.3% pooled, 95% CI \u22124.8% to +2.0%' in ms
          and 'median |Delta z| 1.31-fold higher' in ms,
          "V49-N58b N2 composition caliber (v50 wording)")
    check('softmax caliber; superseded by the linear-normalization update' in sn
          and 'These linear-normalization estimates are the ones cited in the manuscript'
          in sn,
          "V49-N65 N2 SI Note 8 softmax regression labeled superseded")
    check('median |\u0394z| 1.305-fold for the three-panel '
          'composite, P = 3.57 \u00d7 10\u207b\u00b9\u00b3\u2077, and 1.216-fold with '
          'the myeloid panel included, P = 1.28 \u00d7 10\u207b\u2076\u2076' in sn
          and           'pooled four-panel attenuation \u22121.3% (cluster-bootstrap '
          'median \u22121.3%, 95% CI [\u22124.8%, +2.0%])' in sn
          and 'Spearman \u03c1 = 0.364 pooled (n = 10,000 pairs, '
          'P < 10\u207b\u00b3\u2070\u2070; per-cancer 0.196\u20130.513' in sn,
          "V49-N65b A2 SI Note 8 linear update = post-CC caliber")
    check('with four fixed exceptions' in gd and 'three fixed exceptions' not in gd
          and '89_cluster_boot_v45.py (the small-cluster studentized bootstrap-t '
          'analysis) uses the fixed seed 20260905' in gd,
          "V49-N66 N1 Guide seed exceptions cover notebook 89")
    _si_blob = "\n".join(str(_c.value) for _ws in _si_xlsx for _row in _ws.iter_rows()
                         for _c in _row if _c.value is not None)
    check('6.60' in _si_blob and '4.12' in _si_blob,
          "V49-N59 N3 threshold-sweep gradient values (v50: Supp Table 19)")
    check('attenuates it to 1.74 (95% CI [1.64, 1.84])' in ms
          and 'co-report 6.10-fold (full-data) and 1.74-fold (size-balanced)' in ms,
          "V49-N60 C5 Results leads with size-balanced gradient (v50 wording)")
    check('0.850' in sn,
          "V49-N61 C7 class-size Pearson correlation (v50: SI Note 10)")
    check('Fourth, excluding the 32 cell-line-derived LIHC samples' in ms
          and 'NN/TT 1.11, 95% CI [0.93, 1.30]' in ms
          and 'Four controls bound the interpretation' in ms,
          "V49-N62 C4 CC sensitivity analysis (fourth control, v50 wording)")
    check('The ratio earns its increment over k_f under controlled ground truth' in ms,
          "V49-N63 C2 omega-increment honest framing sentence")
    check('cross-type gaps in mean \u03c9 are descriptive rather than calibrated'
          in str(_main_xlsx['Table 1']['A1'].value),
          "V49-N63b C3 caveat in Table 1 xlsx caption")
    check('seaborn:             0.13.2' in gd and 'statsmodels:         0.14.6' in gd
          and 'meld:                1.0.2' in gd and 'pyaugur:             0.1.0' in gd,
          "V49-N64 N5 Guide environment completes seaborn/statsmodels/meld/pyaugur")
    # ---- v49.13 third-review-round fixes (A/B/C groups) ----
    check('span-matched control restricted to the 21 intra-cerebellar region pairs '
          'defining Bergmann glia yields 3.68' in ms
          and 'paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]' in sn,
          "V49-N67 B1 span-matched control (MS headline; SI Note 10 details, v50)")
    check('k_f ratio is 2.09 under equal-n (full-data 2.03)' in ms
          and 'equal-n 1.29, astrocyte higher; full-data 0.31, Bergmann glia higher' in ms
          and '95% CI [2.02, 2.18]' in sn
          and '96_brain_downsample_decomp_v49.py' in sn,
          "V49-N68 B2 equal-n decomposition (MS headline; SI Note 10 details, v50)")
    check('leave-one-population-out baseline range 6.75\u20138.08' in ms
          and 'removing hepatocyte lowers it to 6.75' in sn,
          "V49-N69 B3 calibration leave-one-out (MS pointer; SI 3.10 details, v50)")
    check('whole-tumor label-permutation tests confirmed all three contrasts' in ms
          and '93_luad_group_permutation_v49.py' in sn,
          "V49-N70 B4 LUAD whole-tumor label permutation (MS pointer; SI 3.13, v50)")
    check('adjusted log-\u03c9 ratio 1.19, 95% CI [1.12, 1.26]' in ms,
          "V49-N71 C4b log-omega scale sensitivity (v50 wording)")
    check('high-purity-half 1.17 versus 1.19 excluding CC, 95% CI [1.01, 1.44]' in sn
          and '94_cc_audit_sensitivity_v49.py' in sn,
          "V49-N72 B5/B6 CC exclusion sensitivity + barcode audit (v50: SI 3.13)")
    check('nc49_donor_stratified_table.csv' in sn
          and '4.8 \u00d7 10\u207b\u00b2\u00b3\u00b9' in sn
          and '97_donor_stratified_table_v49.py' in sn,
          "V49-N73 A7 donor-stratified transparency table in SI Note 12")
    check('consistent with, but does not establish, a shared basis in '
          'HK-anchored divergence' in sn
          and 'self-reported benchmark rather than an '
          'independent validation by us' in sn,
          "V49-N74 C3 SI Note 14 Augur variants parallel + pyaugur self-report")
    check('the first per-comparison, design-testable ' in cl,
          "V49-N75 A4 CL priority claim qualified")
    check('5.11 v49.13 Analyses' in gd
          and 'superseded by the linear-normalization recompute of '
          'Section 5.8b' in gd
          and 'Aggregation-order default' in gd,
          "V49-N76 A1/A2 Guide softmax superseded labels + 5.11 + aggregation default")
    for _f in ("results/nc49_brain_region_matched.txt",
               "results/nc49_calib_leave_one_out.txt",
               "results/nc49_tcga_luad_mutation_perm.csv",
               "results/nc49_tcga_luad_logomega_sensitivity.csv",
               "results/nc49_cc_barcode_audit.csv",
               "results/nc49_cc_excl_sensitivity.csv",
               "results/nc49_donor_stratified_table.csv",
               "results/brain_v49_downsample_kfkn_summary.json"):
        check((BASE / _f).exists(), f"V49-N77 B-group output exists: {_f}")
    # ---- v49.14 fourth-round fixes (R1-R6, 2026-09-21) ----
    # A1/B3: NI direction + split-half caveat (MS + SI 1.4)
    check('Section 1.4 of the Supplementary Information' in ms
          and 'never as evidence of positive selection' in ms,
          "V49-N78 A1 MK/NI pointer to SI 1.4 (v50)")
    check('reciprocal of the neutrality index' in sn
          and 'biased upward accordingly' in sn,
          "V49-N79 A1 SI 1.4 NI direction synced")
    # A2/B18: ex-CC CI precision + BRCA CI upper
    check('1.34 [0.997, 1.880]' in sn and 'BRCA 1.57' in ms,
          "V49-N80 A2/B18 CI precision (v50: MS ratio; SI CIs)")
    # B1: sample-count reconciliation
    check('3 do not appear in the assembled pair table' in ms
          and '26 further samples appear only in tumor\u2013normal pairs' in ms
          and 'spans 3,593 unique barcodes' in ms,
          "V49-N81 B1 sample-count reconciliation (3,596/3,593/3,567)")
    # B2: smoking model wording
    check('alone or jointly with admixture, age, and sex' in ms
          and '\u0394\u03c9 +13.3, P = 1.4 \u00d7 10\u207b\u00b3' in ms,
          "V49-N82 B2 smoking covariate wording (v50)")
    # B7: exact P values
    check('all P < 10\u207b\u00b9\u2074\u2075' in ms
          and '7.7 \u00d7 10\u207b\u00b9\u2079' in sn,
          "V49-N83 B7 exact P values (v50: SI Note 8 per-cancer P)")
    # B13: adaptation -> change
    check('functional change rather than neutral drift' in ms
          and 'functional adaptation rather than neutral drift' not in ms,
          "V49-N84 B13 Introduction adaptation wording")
    # B6: Supp Tables pointer
    check('Supplementary Tables 5\u201319 provide the per-analysis numerical tables' in ms,
          "V49-N85 B6 Supp Tables 5-19 pointer in Data availability")
    # C1: composition B=1000 unified (MS Methods + SI Note 8 + Guide 5.8b)
    check('cluster-bootstrap intervals (B = 1,000), the tumor-pair coefficient' in ms
          and 'B = 1,000 for the composition cluster bootstrap' in ms
          and 'B was raised '
          'from 200 to 1,000' in sn
          and 'B = 1,000; raised from 200 in v49.14' in gd,
          "V49-N86 C1 composition bootstrap B unified to 1,000 (MS/SI/Guide)")
    check('LIHC +32.8% [+21.5%, +48.1%], KIRC +19.6% [+14.1%, +25.1%], BRCA '
          '\u221216.1% [\u221224.6%, \u22127.4%], LUAD \u22122.0% [\u22127.8%, +4.2%], LUSC '
          '\u221210.0% [\u221227.8%, +6.8%]' in sn
          and '\u221216% to +33%' in ms,
          "V49-N87 C1 per-cancer attenuation updated (B=1000)")
    # C3: aggregation-order quantification (MS Methods + Guide 5.11h + Section 2)
    check('rank ordering is largely preserved (Spearman \u03c1 = 0.78)' in ms
          and 'mouse Tabula Muris pilot and the human Tabula Sapiens pipelines' in gd
          and 'Aggregation-order same-data quantification (v49.14)' in gd
          and 'control-category median baseline itself moves from 6.46 to 10.94' in gd,
          "V49-N88 C3 aggregation-order quantified + attribution unified")
    # C2: ex-CC Cox (SI + Guide 5.11i)
    check('ex-CC refit excluding all ' in sn
          and 'LIHC ex-CC Cox sensitivity (v49.14)' in gd
          and 'HR/SD 1.08 [0.87, 1.35], P = 0.47' in sn,
          "V49-N89 C2 ex-CC Cox sensitivity (SI + Guide)")
    # C4: log-omega CI archived
    check('bootstrap CI is archived in the output CSV (v49.14)' in gd,
          "V49-N90 C4 log-omega CI archived in CSV (Guide 5.11e)")
    # B9: span-matched decomposition in SI
    check('k_f 1.39 and k_n 0.33' in sn,
          "V49-N91 B9 span-matched k_f/k_n decomposition in SI")
    # B10: ependymal reverse-direction note
    check('0.021 versus 0.058' in sn and 'not nested' in sn,
          "V49-N92 B10 ependymal donor-stratified note (SI Note 12)")
    # B11: Guide 5.9e primary wording aligned
    check('in parallel with the multiclass variant rather than as primary versus secondary' in gd
          and '(confound-controlled, primary)' not in gd,
          "V49-N93 B11 Guide 5.9e parallel wording")
    # B12: ddof note in Supp Table 3 description
    check('all SDs are sample SDs with ' in sn and 'ddof = 1' in sn,
          "V49-N94 B12 ddof = 1 declared for Supp Table 3 SDs")
    # B15: MC resolution note
    check('Monte-Carlo estimates at B = 10,000, resolution 10\u207b\u2074' in sn,
          "V49-N95 B15 permutation MC resolution note (SI 3.13)")
    # B16: descriptive-only note for composition correlation P
    check('these correlation ' in sn and 'descriptive only, ' in sn,
          "V49-N96 B16 composition rho P descriptive note (SI Note 8)")
    # CL ORCID
    check('ORCID (corresponding author): Li Zhang 0000-0002-0698-0754' in cl,
          "V49-N97 B8 CL ORCID line")
    # v49.14 C-group output files exist
    for _f in ("results/nc49_agg_order_sensitivity.csv",
               "results/nc49_agg_order_sensitivity.txt",
               "results/nc49_lihc_cox_excc.csv",
               "results/audit/nc49_lihc_cox_excc_2026-09-21.md"):
        check((BASE / _f).exists(), f"V49-N98 v49.14 C-group output exists: {_f}")
    # v49.14 stale-value purge
    for stale in ('[1.00, 1.88]', 'median \u22121.2%', 'CI [\u22125.0%, +2.3%]',
                  '+31.7% [+21.0%, +45.3%]', '(1.34\u20131.84)'):
        check(stale not in ms and stale not in sn,
              f"V49-N99 stale gone from MS/SI: '{stale}'")
    # ---- v49.15 fifth-round blind-review fixes (5 Minor + 1 optional) ----
    # m2 (R1): span-matched residual decomposition surfaced in MS
    check('residual again k_n-driven: k_f 1.39 versus k_n 0.33'
          in ms and 'Supplementary Note 10' in ms,
          "V49-N100 m2 span-matched residual decomposition in MS (v50 wording)")
    # m3 (R1): ependymal against-direction class noted in MS
    check('ependymal cells (P 0.058 free versus 0.021 stratified)' in ms
          and 'stratified q = 0.052' in ms,
          "V49-N101 m3 ependymal stratified-reversal note in MS")
    # m4 (R6): exact Mann-Whitney P for cross-organ reversal
    check('Mann-Whitney U, P = 5.6 \u00d7 10\u207b\u00b9\u2078' in ms
          and 'Mann-Whitney U, P < 0.001' not in ms,
          "V49-N102 m4 exact cross-organ Mann-Whitney P (5.6e-18)")
    # m5 (R6, optional): CL per-background replicate count
    check('1,750 replicates per background, two backgrounds' in cl,
          "V49-N103 m5 CL per-background replicate count")
    # R5 optional: median qualifier on aggregation-order baseline
    check('split-control median baseline itself moves from 6.46 to 10.94' in ms,
          "V49-N104 R5 median qualifier on agg-order baseline (MS)")
    # m1 (R2): legend word order fixed (asserted in N55, negative here)
    check('constrained counterpart of the synonymous baseline' in ms,
          "V49-N105 m1 legend word order fixed")
    # ---- v49.11 MK substantive correspondence (R2-C1 ruling: analogy substantive) ----
    # v50: MK fourfold correspondence migrated to SI 1.4; MS carries pointer
    check('Section 1.4 of the Supplementary Information' in ms
          and 'synonymous-site divergence (Ks)' in sn
          and 'polymorphism class' in sn
          and 'reciprocal of the neutrality index' in sn
          and 'substantive rather than nominal' not in ms,
          "V49-N53 MK fourfold correspondence migrated to SI 1.4 (v50)")
    check('the correspondence is threefold' in sn
          and 'a species pair to the two cell ' in sn
          and 'constrained rather than neutral reference class' in sn,
          "V49-N54 SI 1.4 threefold correspondence synced")
    check('the constrained counterpart of the synonymous baseline' in ms
          and 'the counterpart of the constrained synonymous baseline' not in ms
          and 'read against the empirical calibration baseline rather than against 1' in ms,
          "V49-N55 Fig 1a legend counterpart mapping + calibration anchor (v49.15 word order)")
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
    check("Supplementary Note 1" in ms and "Supplementary Notes 1\u201316" in ms,
          "V49-SC5 notes cited (v50: 1-16 span)")
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
                 "CKI_Submission_v49_NC/Supplementary_Fig_14.pdf",
                 "CKI_Submission_v49_NC/figure2.pdf",
                 "CKI_Submission_v49_NC/figure3.pdf",
                 "CKI_Submission_v49_NC/figure6.pdf",
                 "CKI_Submission_v49_NC/CKI_graphical_abstract.pdf",
                 "CKI_Submission_v49_NC/CKI_Tables_NC.xlsx",
                 "CKI_Submission_v49_NC/CKI_Supplementary_Tables_NC.xlsx"]:
        check(must in names, f"V49-P2 {must.split('/')[-1]}")
    n_oldname = [n for n in names if "figure_S" in n or "Supplementary_Figure_S" in n]
    check(not n_oldname, f"V49-P3 no old supp figure naming ({n_oldname})")
    check(not any(n.endswith((".png", ".svg", "_fulltext.txt")) for n in names),
          "V49-P4 pdf-only figures + word-only docs (no png/svg/txt)")
    from docx import Document as _DocxCheck
    check(len(_DocxCheck(str(BASE / "results" / "CKI_Manuscript_NC.docx")).tables) == 0,
          "V49-P5 MS docx contains no tables (tables live in CKI_Tables_NC.xlsx)")
    check(len(_DocxCheck(str(BASE / "results" / "CKI_Supplementary_NC.docx")).tables) == 0,
          "V49-P6 SI docx contains no tables (tables live in CKI_Supplementary_Tables_NC.xlsx)")

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
