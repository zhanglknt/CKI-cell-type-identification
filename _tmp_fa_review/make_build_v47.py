#!/usr/bin/env python3
"""Transform 99_build_gb_v46.py -> 99_build_gb_v47.py.

v47 = v46 + first-author (Xianming Wu) revision integration:
figure replacement (author redrawn set), supplementary renumbering
S1-S13 (old S3 removed, Kang S13->S12, QQ S14->S13), GA title fix,
D4 anchor-stationarity sentence, Table1-2 title, cki 0.4.9 -> 0.5.0.
Every replacement asserts a unique match; any failure aborts without
writing the target file.
"""
import io, os, sys

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
SRC = os.path.join(BASE, "99_build_gb_v46.py")
DST = os.path.join(BASE, "99_build_gb_v47.py")

R = []  # (old, new) unique-match replacements

# ---- 1. docstring header: insert v47 block before the v46 block ----
R.append((
    '"""Build CKI Submission Package v46 (Genome Biology).\n\nv46 = v45 +',
    '"""Build CKI Submission Package v47 (Genome Biology).\n'
    '\n'
    'v47 = v46 + first-author (Xianming Wu) revision integration\n'
    '(2026-09-05): all 95 tracked revisions adopted; main figures\n'
    'replaced by the first-author redrawn set; supplementary figures\n'
    'renumbered S1-S13 with no gap (old S3 method-comparison removed;\n'
    'Kang IFN-beta S13->S12; QQ S14->S13); Figure S1 regenerated\n'
    'in-house from the authoritative sweep CSVs (k_n decreasing over\n'
    '250-1,000 HK genes; identity-only AUC 0.786 retained); the\n'
    'graphical abstract adopts the first-author layout with the title\n'
    "corrected to 'CKI: a Ka/Ks-inspired index'; Discussion gains the\n"
    'anchor-stationarity sentence (D4, Kang CD14+ monocyte example);\n'
    'SN clarifies Table S3/S4 same-file provenance; Table1-2 title\n'
    "'Supplementary Tables' -> 'Tables'; cki 0.4.9 -> 0.5.0; release\n"
    'tag v0.5.0. MS Availability phase-1 keeps the v0.4.9 Zenodo\n'
    'record DOI (10.5281/zenodo.22333850); phase-2 writes the v0.5.0\n'
    'record DOI after the release.\n'
    '\n'
    'v46 = v45 +'
))

# ---- 2. path constants ----
R.append((
    'V38_ZIP = VERSION3_DIR / "CKI_Submission_v46.zip"\n'
    'WORK_DIR = VERSION3_DIR / "CKI_Submission_v46"\n'
    'FIGURES_SUBMISSION_DIR = RESULTS_DIR / "figures_submission"',
    'V38_ZIP = VERSION3_DIR / "CKI_Submission_v47.zip"\n'
    'WORK_DIR = VERSION3_DIR / "CKI_Submission_v47"\n'
    'FIGURES_SUBMISSION_DIR = RESULTS_DIR / "figures_submission"\n'
    'FIGURES_V47_DIR = RESULTS_DIR / "figures_v47_author"'
))

# ---- 3. FIGURE_MAP ----
_old_map = '''FIGURE_MAP = {
    # Main figures
    "figure1": "figure1_concept_pipeline",
    "figure2": "figure2_calibration_tabula_muris",
    "figure3": "figure3_orthogonal_information",
    "figure4": "figure4_tcga_pancancer",
    "figure5": "figure5_cross_organ_conservation",
    "figure6": "figure6_brain_regional_cki",
    # Supplementary figures (renumbered by first-citation order, P1-6)
    "Supplementary_Figure_S1": "ed_fig1_parameter_sweep_pathway",
    "Supplementary_Figure_S2": "ed_fig12_calibrated_omega",
    "Supplementary_Figure_S3": "ed_fig4_method_comparison_auc",
    "Supplementary_Figure_S4": "ed_fig3_tcga_per_cancer",
    "Supplementary_Figure_S5": "ed_fig5_cross_organ_table",
    "Supplementary_Figure_S6": "Supplementary_Figure_S6",
    "Supplementary_Figure_S7": "ed_fig11_kn_variability",
    "Supplementary_Figure_S8": "Supplementary_Figure_S8",
    "Supplementary_Figure_S9": "ed_fig9_residual_null",
    "Supplementary_Figure_S10": "ed_fig2_cross_species_validation",
    "Supplementary_Figure_S11": "ed_fig8_omega_distribution",
    "Supplementary_Figure_S12": "ed_fig10_dimensionality",
    "Supplementary_Figure_S13": "Supplementary_Figure_S13",
    "Supplementary_Figure_S14": "pseudoregion_control_qq",
}'''
_new_map = '''FIGURE_MAP = {
    # Main figures: first-author redrawn set (v47)
    "figure1": "figure1",
    "figure2": "figure2",
    "figure3": "figure3",
    "figure4": "figure4",
    "figure5": "figure5",
    "figure6": "figure6",
    # Supplementary figures S1-S13 (v47 renumbered, staged in
    # results/figures_v47_author/ by _tmp_fa_review/assemble_figures_v47.py):
    # S1  = our regenerated parameter sweep (ed_fig1, k_n decreasing,
    #       AUC 0.786; supersedes the first-author redraw per D1)
    # S2-S11 = first-author set (his S3-S11 already renumbered after
    #       deleting old S3 method-comparison, comment 56)
    # S12 = first-author Kang IFN-beta (his file figure_S13__.pdf)
    # S13 = v46 QQ (pseudoregion_control_qq; his S14 identical)
    "Supplementary_Figure_S1": "figure_S1",
    "Supplementary_Figure_S2": "figure_S2",
    "Supplementary_Figure_S3": "figure_S3",
    "Supplementary_Figure_S4": "figure_S4",
    "Supplementary_Figure_S5": "figure_S5",
    "Supplementary_Figure_S6": "figure_S6",
    "Supplementary_Figure_S7": "figure_S7",
    "Supplementary_Figure_S8": "figure_S8",
    "Supplementary_Figure_S9": "figure_S9",
    "Supplementary_Figure_S10": "figure_S10",
    "Supplementary_Figure_S11": "figure_S11",
    "Supplementary_Figure_S12": "figure_S12",
    "Supplementary_Figure_S13": "figure_S13",
}'''
R.append((_old_map, _new_map))

# ---- 4. collect_figures source dir ----
R.append((
    '    src_dir = RESULTS_DIR / "figures_final"',
    '    src_dir = FIGURES_V47_DIR'
))

# ---- 5. verify_files supplementary range ----
R.append((
    '    for i in range(1, 15):\n'
    '        v.check((v.wd / f"Supplementary_Figure_S{i}.pdf").exists(), f"Supp Fig S{i}")',
    '    for i in range(1, 14):\n'
    '        v.check((v.wd / f"Supplementary_Figure_S{i}.pdf").exists(), f"Supp Fig S{i}")'
))

# ---- 6. V41 Kang / QQ renumbering ----
R.append((
    """    v.check(bool(re.search(r'Additional file 1: Fig\\. S13', t)),
            "V41-21 MS cites Additional file 1 Fig. S13")""",
    """    v.check(bool(re.search(r'Additional file 1: Fig\\. S12', t)),
            "V41-21 MS cites Additional file 1 Fig. S12 (v47: Kang)")"""
))
R.append((
    """    v.check(bool(re.search(r'Figure S13\\. Real perturbation demonstration', t)),
            "V41-22 S13 caption in MS")""",
    """    v.check(bool(re.search(r'Figure S12\\. Real perturbation demonstration', t)),
            "V41-22 S12 caption in MS (v47: Kang renumbered)")"""
))
R.append((
    """    v.check(bool(re.search(r'\\(Fig\\. S13\\)', s)), "V41-25 SN 3.15 references Fig. S13")""",
    """    v.check(bool(re.search(r'\\(Fig\\. S12\\)', s)), "V41-25 SN 3.15 references Fig. S12 (v47)")"""
))
R.append((
    """    v.check(bool(re.search(r'Additional file 1: Fig\\. S14', t)),
            "V41-29 MS cites Additional file 1 Fig. S14")
    v.check(bool(re.search(r'Figure S14\\. Pseudo-region negative control', t)),
            "V41-30 S14 caption in MS")
    v.check(bool(re.search(r'S1\\\\u2013S14|S1\\u2013S14', t)),
            "V41-31 additional-files figure range updated to S14")""",
    """    v.check(bool(re.search(r'Additional file 1: Fig\\. S13', t)),
            "V41-29 MS cites Additional file 1 Fig. S13 (v47: QQ)")
    v.check(bool(re.search(r'Figure S13\\. Pseudo-region negative control', t)),
            "V41-30 S13 caption in MS (v47: QQ renumbered)")
    v.check(bool(re.search(r'S1\\\\u2013S13|S1\\u2013S13', t)),
            "V41-31 additional-files figure range S1-S13 (v47)")"""
))

# ---- 7. R2-4 label ----
R.append((
    '''            "R2-4 Fig S13 caption uses 'consistent with'")''',
    '''            "R2-4 Fig S12 (Kang) caption uses 'consistent with' (v47)")'''
))

# ---- 8. V44-13 manifest figure list ----
R.append((
    '''    v.check("figure1.pdf" in mf and "Supplementary_Figure_S14.pdf" in mf,
            "V44-13 MANIFEST includes figure-PDF SHA-256 checksums")''',
    '''    v.check("figure1.pdf" in mf and "Supplementary_Figure_S13.pdf" in mf,
            "V44-13 MANIFEST includes figure-PDF SHA-256 checksums (v47: S13)")'''
))

# ---- 9. V45 version assertions ----
R.append((
    '''    v.check("(v0.4.9)" in ms and "tag v0.4.9" in ms and "v0.4.7" not in ms,
            "V45-2f MS availability block fully on v0.4.9 (phase-1 DOI line excepted)")''',
    '''    v.check("(v0.5.0)" in ms and "tag v0.5.0" in ms and "v0.4.7" not in ms,
            "V45-2f MS availability block fully on v0.5.0 (phase-1 DOI line excepted)")'''
))
R.append((
    '''    v.check('__version__ = "0.4.9"' in _init, "V45-13a cki __version__ = 0.4.9")''',
    '''    v.check('__version__ = "0.5.0"' in _init, "V45-13a cki __version__ = 0.5.0 (v47)")'''
))
R.append((
    '''    v.check("v46" in mf and "v0.4.9" in mf,
            "V45-14 MANIFEST version banner = v46 / tag v0.4.9")''',
    '''    v.check("v47" in mf and "v0.5.0" in mf,
            "V45-14 MANIFEST version banner = v47 / tag v0.5.0")'''
))

# ---- 10. V46 zip / version assertions ----
R.append((
    '''    with zipfile.ZipFile(V38_ZIP) as _z:
        _names = _z.namelist()
        _f6 = _z.read("CKI_Submission_v46/figure6.pdf")
    v.check("CKI_Submission_v46/CKI_Manuscript_fulltext.txt" in _names,
            "V46-g1 zip ships review-aid fulltext extracts")
    v.check(_hl.sha256(_f6).hexdigest() ==
            "050fe51c7951dd22f992e0062bc1cf4a49d25f9f8901f45fd1306ce5fc071769",
            "V46-g2 zip figure6.pdf = annotated render (sha256 match)")''',
    '''    with zipfile.ZipFile(V38_ZIP) as _z:
        _names = _z.namelist()
        _f6 = _z.read("CKI_Submission_v47/figure6.pdf")
    v.check("CKI_Submission_v47/CKI_Manuscript_fulltext.txt" in _names,
            "V46-g1 zip ships review-aid fulltext extracts (v47)")
    v.check(_hl.sha256(_f6).hexdigest() ==
            "c3699f7238a4f7efded8895474918c4d685f55d1c89b54d514dca1f8f71f04ec",
            "V46-g2 zip figure6.pdf = first-author redrawn render (v47 sha256)")'''
))
R.append((
    '''    v.check("v0.4.9" in ms and "v0.4.9" in sn and "v0.4.9" in cl
            and "0.4.9" in rg,
            "V46-i1 MS/SN/CL/Guide cite v0.4.9")
    _hits = [m.start() for m in re.finditer(r'v0\\.4\\.8', ms)]
    v.check(all('22333850' in ms[h:h + 120]
                or 'version DOI' in ms[max(0, h - 60):h] for h in _hits),
            f"V46-i2 MS v0.4.8 only on phase-1 DOI line ({len(_hits)} hits)")
    v.check("v0.4.8" not in sn and "v0.4.8" not in cl
            and "0.4.8" not in rg,
            "V46-i3 SN/CL/Guide free of stale v0.4.8")''',
    '''    v.check("v0.5.0" in ms and "v0.5.0" in sn and "v0.5.0" in cl
            and "0.5.0" in rg,
            "V46-i1 MS/SN/CL/Guide cite v0.5.0 (v47)")
    _hits = [m.start() for m in re.finditer(r'v0\\.4\\.9', ms)]
    v.check(all('22333850' in ms[h:h + 120]
                or 'version DOI' in ms[max(0, h - 60):h] for h in _hits),
            f"V46-i2 MS v0.4.9 only on phase-1 DOI line ({len(_hits)} hits)")
    v.check("v0.4.8" not in sn and "v0.4.8" not in cl
            and "0.4.8" not in rg and "v0.4.9" not in sn
            and "v0.4.9" not in cl and "0.4.9" not in rg,
            "V46-i3 SN/CL/Guide free of stale v0.4.8/v0.4.9 (v47)")'''
))

# ---- 11. MANIFEST header + v47 changes block ----
_old_mf_head = '''    manifest = f"""CKI Submission Package v46 (Genome Biology, Methodology article)
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Status: v46 = v45 + reviewer cross-check text fixes (2026-09-05):
the 0.81-1.00 raw JS/cosine FPR range is qualified to
moderate-to-strong drift (eta >= 0.5) in abstract and Results; the
pyaugur fidelity benchmark is attributed to the port's own package
validation; the Reproducibility Guide corrects Bergmann omega_cal
1.3 -> 1.4 (brain-internal baseline) and gains section 5.9
documenting the v45 analyses (notebooks 88, 89, 90, 91, 91b,
_fig1_clean.py); SN 3.5 reports the most-constrained-class
omega_cal at two significant figures (1.4); the TCGA composition
check is unified on the softmax primary (-0.5% pooled, 95% CI
[-3.2%, +2.6%]) with the linear-normalization run (-0.8%) as
sensitivity; MANIFEST Contents annotations are corrected (SN 3.12,
3.13, 3.20-3.23; notebooks 05-101; four-dataset validation
summary); review-aid fulltext extracts and graphical-abstract
renders now ship in the package (not part of the journal
submission); figure6 regenerated with 6B/6D in-panel annotations.
Results 6,476 words; abstract 250 words; cki package v0.4.9
(29/29 tests).
Package released as tag v0.4.9. MS Availability phase-1 cites the
v0.4.9 Zenodo record (10.5281/zenodo.22333850); the v0.4.9
record DOI is written in phase-2 after the release.
Brain candidates remain hypothesis-generating signals: no formal FDR
discovery is claimed.

=== v46 Changes (reviewer cross-check) ==='''
_new_mf_head = '''    manifest = f"""CKI Submission Package v47 (Genome Biology, Methodology article)
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Status: v47 = v46 + first-author (Xianming Wu) revision integration
(2026-09-05). All 95 tracked revisions + 6 comments from the
first-author pass were adopted; the main figures are replaced by
the first-author redrawn set (figure1-6); supplementary figures are
renumbered S1-S13 with no gap (old S3 method-comparison removed per
comment 56; Kang IFN-beta S13->S12; QQ S14->S13); Figure S1 is
regenerated in-house from the authoritative sweep CSVs (k_n
decreasing over 250-1,000 HK genes; identity-only AUC 0.786
retained, D1); the graphical abstract adopts the first-author
layout with the title corrected to 'CKI: a Ka/Ks-inspired index'
(D3); Discussion gains the anchor-stationarity sentence with the
Kang CD14+ monocyte example (omega AUC 0.55 vs k_f 0.98, D4); SN
clarifies Table S3/S4 same-file provenance (Q2); Table1-2.docx
title 'Supplementary Tables' -> 'Tables' (A5-7); cki package
v0.5.0 (29/29 tests).
Package released as tag v0.5.0. MS Availability phase-1 cites the
v0.4.9 Zenodo record (10.5281/zenodo.22333850); the v0.5.0
record DOI is written in phase-2 after the release.
Brain candidates remain hypothesis-generating signals: no formal FDR
discovery is claimed.

=== v47 Changes (first-author revision integration) ===
  - Main text: Fig. 2 panel citation 2B,D -> 2B,C; old Fig. S3
    method-comparison citation removed; all supplementary citations
    renumbered (S4->S3 ... S12->S11, Kang S13->S12, QQ S14->S13);
    additional-files range S1-S14 -> S1-S13 (V47-a..c).
  - Discussion: anchor-stationarity sentence added to the 'When to
    use CKI' paragraph ('...the index presupposes anchor
    stationarity: when the anchor itself moves, cross-metric
    contrasts - not absolute omega values - are the reliable signal
    (Additional file 1: Fig. S12).') with Kang et al. [14]
    attribution (V47-d).
  - Figure legends: Fig 2 old C removed (D->C); Fig 3 old B/D/E
    removed (C->B); Fig 4 old C/D/E removed; Fig 5 'Table of top 5'
    -> 'Top 5'; Fig 6 old C removed (D->C, E->D); S1 panel-A legend
    rewritten to the decreasing-k_n wording (AUC 0.786 retained,
    'w' -> omega typo fixed); S2 two-baseline legend rewritten;
    S4-S13 legends rewritten/renumbered per the first-author final
    text (V47-e).
  - Supplementary Notes: six cross-references renumbered (S11->S10,
    S9->S8, S12->S11, S7->S6, S13->S12, S14->S13); Table S3/S4
    same-file provenance sentence added (V47-f).
  - Figures: main figure1-6 replaced by the first-author redrawn
    PDFs; supplementary S2-S11 adopted from the first-author set
    (his S1 superseded by our regenerated sweep figure per D1; his
    Kang file figure_S13__.pdf -> S12); S13 = v46 QQ
    (pseudoregion_control_qq; his S14 visually identical); GA =
    first-author layout with the title corrected (V47-g).
  - Table1-2.docx: title 'Supplementary Tables' -> 'Tables' (V47-h).
  - Version: cki 0.4.9 -> 0.5.0 across package, pyproject, README,
    MS, SN, CL, Guide; release tag v0.5.0 (V47-i).

=== v46 Changes (reviewer cross-check) ==='''
R.append((_old_mf_head, _new_mf_head))

# ---- 12. MANIFEST Contents figure range ----
R.append((
    "7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S14.pdf - Supplementary figures",
    "7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S13.pdf - Supplementary figures"
))

# ---- 13. MANIFEST filename + fig sha list ----
R.append((
    '    with open(WORK_DIR / "MANIFEST_v46.txt", "w", encoding="utf-8") as f:',
    '    with open(WORK_DIR / "MANIFEST_v47.txt", "w", encoding="utf-8") as f:'
))
R.append((
    '''                 [f"Supplementary_Figure_S{i}.pdf" for i in range(1, 15)] + \\''',
    '''                 [f"Supplementary_Figure_S{i}.pdf" for i in range(1, 14)] + \\'''
))
R.append((
    '    print(f"\\n[3] Writing MANIFEST_v46.txt...")',
    '    print(f"\\n[3] Writing MANIFEST_v47.txt...")'
))

# ---- 14. zip arcname ----
R.append((
    '                zf.write(fp, f"CKI_Submission_v46/{fn}")',
    '                zf.write(fp, f"CKI_Submission_v47/{fn}")'
))

# ---- 15. banners ----
R.append((
    '    print("  CKI Submission Package v46 (Genome Biology) Builder")\n'
    '    print("  Reviewer cross-check fixes + fresh DOCX rebuild")',
    '    print("  CKI Submission Package v47 (Genome Biology) Builder")\n'
    '    print("  First-author revision integration + fresh DOCX rebuild")'
))
R.append((
    '    print(f"  v46 (GB) Package: {V38_ZIP}")',
    '    print(f"  v47 (GB) Package: {V38_ZIP}")'
))
R.append((
    '    print(f"  v46 Final Verification")',
    '    print(f"  v47 Final Verification")'
))
R.append((
    '    print(f"  v46 Verification Summary")',
    '    print(f"  v47 Verification Summary")'
))
R.append((
    '        print(f"\\n  *** ALL {v.passed} CHECKS PASSED — v46 (GB) FINAL ***")',
    '        print(f"\\n  *** ALL {v.passed} CHECKS PASSED — v47 (GB) FINAL ***")'
))

# ---- 16. verify_v47_additions function + call ----
V47_FUNC = '''

def verify_v47_additions(v: Verifier):
    """v47 first-author revision integration: author figure set +
    supplementary renumbering S1-S13 + D1/D3/D4 decisions + version
    bump to 0.5.0."""
    print(f"\\n{'-'.join([''] * 2)}{'=' * 48}")
    print(f"  v47 Additions (first-author revision integration)")
    print(f"{'=' * 50}")

    ms = v.ms_text()
    sn = v.supp_text()
    cl = v.cl_text()
    rg = v.rg_text()
    mf = v.manifest_text()
    tb_p = v.wd / "Table1-2_fulltext.txt"
    tb = tb_p.read_text(encoding="utf-8") if tb_p.exists() else ""

    # ---- V47-1 figure set: S1-S13 present, S14 / old S3 absent ----
    for i in range(1, 14):
        v.check((v.wd / f"Supplementary_Figure_S{i}.pdf").exists(),
                f"V47-1a Supp Fig S{i} present")
    v.check(not (v.wd / "Supplementary_Figure_S14.pdf").exists(),
            "V47-1b old S14 slot absent from package")

    # ---- V47-2 packaged figures byte-identical to the staged set ----
    import hashlib as _hl
    _stg = RESULTS_DIR / "figures_v47_author"
    _ok = True
    for _i in range(1, 7):
        _a = _stg / f"figure{_i}.pdf"
        _b = v.wd / f"figure{_i}.pdf"
        if not (_a.exists() and _b.exists()
                and _hl.sha256(_a.read_bytes()).hexdigest()
                == _hl.sha256(_b.read_bytes()).hexdigest()):
            _ok = False
            print(f"    [mismatch] figure{_i}.pdf")
    for _i in range(1, 14):
        _a = _stg / f"figure_S{_i}.pdf"
        _b = v.wd / f"Supplementary_Figure_S{_i}.pdf"
        if not (_a.exists() and _b.exists()
                and _hl.sha256(_a.read_bytes()).hexdigest()
                == _hl.sha256(_b.read_bytes()).hexdigest()):
            _ok = False
            print(f"    [mismatch] figure_S{_i}.pdf")
    _a = _stg / "CKI_graphical_abstract.pdf"
    _b = v.wd / "CKI_graphical_abstract.pdf"
    if not (_hl.sha256(_a.read_bytes()).hexdigest()
            == _hl.sha256(_b.read_bytes()).hexdigest()):
        _ok = False
        print("    [mismatch] CKI_graphical_abstract.pdf")
    v.check(_ok, "V47-2 all 20 packaged figure PDFs + GA == staged sources")

    # ---- V47-3 renumbering (text level) ----
    v.check("Figure S14" not in ms and "Fig. S14" not in ms,
            "V47-3a MS free of S14 references")
    v.check("Figure S14" not in sn and "Fig. S14" not in sn,
            "V47-3b SN free of S14 references")
    v.check("Figure S3. Method comparison performance" not in ms,
            "V47-3c old S3 method-comparison caption removed")
    v.check("Figure S3. TCGA per-cancer matrices" in ms,
            "V47-3d new S3 caption = TCGA per-cancer (old S4)")
    v.check("Figure S12. Real perturbation demonstration" in ms,
            "V47-3e Kang caption = Figure S12")
    v.check("Figure S13. Pseudo-region negative control" in ms,
            "V47-3f QQ caption = Figure S13")
    _seq = [int(m.group(1)) for m in
            re.finditer(r'Additional file 1: Figure S(\\d+)\\.', ms)]
    v.check(_seq == list(range(1, 14)),
            f"V47-3g MS supp legend sequence S1..S13 (got {_seq})")

    # ---- V47-4 D4 anchor-stationarity sentence ----
    v.check("presupposes anchor stationarity" in ms,
            "V47-4a D4 anchor-stationarity sentence in Discussion")
    v.check("cross-metric contrasts" in ms and "Kang et al. [14]" in ms,
            "V47-4b cross-metric contrasts + Kang [14] attribution")

    # ---- V47-5 S1 legend / 0.786 retained (D1) ----
    v.check("k_n decreases monotonically with increasing HK gene number" in ms,
            "V47-5a S1 legend decreasing-k_n wording")
    v.check("AUC = 0.786" in ms, "V47-5b S1 identity-only AUC 0.786 kept")
    v.check("showing convergence" not in ms,
            "V47-5c old convergence wording gone")
    v.check("AUC = 0.648" not in ms and "AUC 0.648" not in ms,
            "V47-5d first-author 0.648 AUC NOT adopted")
    v.check("0.648" in ms, "V47-5e rho = -0.648 (class-size) retained")

    # ---- V47-6 main-figure legend panel edits ----
    v.check("Fig. 2B, C" in ms and "Fig. 2B, D" not in ms,
            "V47-6a Fig 2 citation 2B,C")
    v.check("Table of top" not in ms, "V47-6b Fig 5 'Top 5' wording")

    # ---- V47-7 SN Table S3/S4 provenance ----
    v.check("share the same underlying data file" in sn,
            "V47-7 SN Table S3/S4 same-file provenance sentence")

    # ---- V47-8 GA title corrected (D3) ----
    v.check("Cell-state Kinetic Index" not in (ms + sn + cl + rg),
            "V47-8a no 'Cell-state Kinetic Index' in any document")
    from PyPDF2 import PdfReader as _PR
    _gatxt = _PR(str(v.wd / "CKI_graphical_abstract.pdf")) \\
        .pages[0].extract_text()
    v.check("Ka/Ks-inspired" in _gatxt,
            "V47-8b GA title = 'CKI: a Ka/Ks-inspired index'")

    # ---- V47-9 Table1-2 title ----
    _tb_lines = [l for l in tb.split("\\n") if l.strip()]
    v.check(len(_tb_lines) > 1 and _tb_lines[1].strip() == "Tables",
            "V47-9a Table1-2 title = 'Tables'")
    v.check("Supplementary Tables" not in tb,
            "V47-9b old 'Supplementary Tables' title gone")

    # ---- V47-10 version bump 0.5.0 ----
    _init = (BASE_DIR / "cki" / "__init__.py").read_text(encoding="utf-8")
    v.check('__version__ = "0.5.0"' in _init, "V47-10a cki __version__ = 0.5.0")
    v.check("(v0.5.0)" in ms and "tag v0.5.0" in ms,
            "V47-10b MS availability on v0.5.0")
    v.check("version DOI for v0.4.9: 10.5281/zenodo.22333850" in ms,
            "V47-10c MS phase-1 Zenodo line cites v0.4.9 record")
    v.check("v0.5.0" in sn and "v0.5.0" in cl and "0.5.0" in rg,
            "V47-10d SN/CL/Guide on v0.5.0")

    # ---- V47-11 zip integrity ----
    with zipfile.ZipFile(V38_ZIP) as _z:
        _names = _z.namelist()
    v.check("CKI_Submission_v47/CKI_Manuscript.docx" in _names,
            "V47-11a zip rooted at CKI_Submission_v47")
    v.check(not any("S14" in n for n in _names),
            "V47-11b zip free of S14 artifacts")
    v.check("CKI_Submission_v47/Supplementary_Figure_S13.pdf" in _names
            and "CKI_Submission_v47/MANIFEST_v47.txt" in _names,
            "V47-11c zip ships S13 + MANIFEST_v47")

    # ---- V47-12 MANIFEST banner ----
    v.check("v47" in mf and "v0.5.0" in mf and "first-author" in mf,
            "V47-12 MANIFEST banner v47 / v0.5.0 / first-author")

'''

R.append((
    'def verify_files(v: Verifier):',
    V47_FUNC.strip() + '\n\n\ndef verify_files(v: Verifier):'
))
R.append((
    '    verify_v46_additions(v)\n\n    print(f"\\n{\'=\'*60}")',
    '    verify_v46_additions(v)\n    verify_v47_additions(v)\n\n    print(f"\\n{\'=\'*60}")'
))


def main():
    src = io.open(SRC, encoding="utf-8", newline="").read()
    out = src
    n_ok = 0
    for idx, (old, new) in enumerate(R, 1):
        n = out.count(old)
        if n != 1:
            print(f"FAIL #{idx}: expected 1 match, got {n}")
            print("  old head:", repr(old[:110]))
            print("ABORT: target not written")
            sys.exit(1)
        out = out.replace(old, new)
        n_ok += 1
    io.open(DST, "w", encoding="utf-8", newline="").write(out)
    print(f"OK: {n_ok}/{len(R)} replacements -> {DST}")
    # syntax check
    import py_compile
    py_compile.compile(DST, doraise=True)
    print("OK: 99_build_gb_v47.py compiles")

if __name__ == "__main__":
    main()
