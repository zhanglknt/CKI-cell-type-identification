#!/usr/bin/env python3
"""Apply v49.6 figure-renumber edits with hard assertions (idempotent).

For each (file, old, new): require exactly one of
  - old present once  -> replace, count as applied
  - new present and old absent -> already applied, skip
Anything else -> hard failure (no write for that file).
"""
import sys

E = []  # (file, old, new)

MS = 'generate_manuscript_nc.py'
E += [
 (MS, "(human column) (Fig. 3).')", "(human column) (Fig. 2d, e).')"),
 (MS, "as divergence (Fig. 4d).')", "as divergence (Fig. 3d).')"),
 (MS, "k_n; Fig. 4b, c)", "k_n; Fig. 3b, c)"),
 (MS, "preserved (Fig. 4; audit", "preserved (Fig. 3; audit"),
 (MS, "(Fig. 5; Supplementary Fig. 4)", "(Fig. 4; Supplementary Fig. 4)"),
 (MS, "(Fig. 5a).')", "(Fig. 4a).')"),
 (MS, "pair sets; Fig. 5b)", "pair sets; Fig. 4b)"),
 (MS, "mechanistically (Fig. 5c,d)", "mechanistically (Fig. 4c,d)"),
 (MS, "(Fig. 6; Table 2;", "(Fig. 5; Table 2;"),
 # delete old Figure 3 legend (line + trailing blank line)
 (MS,
  'p(f\'Figure 3. Correlation structure between CKI and standard metrics. (a) Spearman correlation heatmap of five metrics on n = {_h["n_pairs_total"]:,} Tabula Sapiens pairs. CKI \\u03c9 is negatively correlated with all four standard metrics; because k_n is itself positively correlated with the standard metrics, this negativity partly reflects the \\u03c9 denominator (see Results). Standard metrics form a positive cluster. (b) ROC curves for cell-type classification across five metrics on Tabula Sapiens data.\')\n\n',
  ''),
 (MS, "p('Figure 4. Real-data", "p('Figure 3. Real-data"),
 (MS, "p('Figure 5. Pan-cancer", "p('Figure 4. Pan-cancer"),
 ('notebooks/68_gen_supplementary_nc.py',
  "_fig6_clean.py (Figure 7).'", "_fig6_clean.py (Figure 6).'"),
 ('generate_cover_letter_nc.py',
  '"readership (Fig. 5).",', '"readership (Fig. 4).",'),
 ('results/audit/_nc49_ms_verify.py',
  "chk('Fig 5a dual-axis note',", "chk('Fig 4a dual-axis note',"),
 ('results/audit/_nc49_ms_verify.py',
  "chk('Figure 5 legend (TCGA)', 'Figure 5. Pan-cancer tissue-level divergence in tumors' in full)",
  "chk('Figure 4 legend (TCGA)', 'Figure 4. Pan-cancer tissue-level divergence in tumors' in full)"),
 ('99_build_nc_v49.py',
  '''    # main figures: 1-3 unchanged; 4 = drift ladder (new); 5 = TCGA map (new);
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
    check(n_fig == 21, f"V49-1 figures staged = 21 (7 main + 13 supp + GA pdf) got {n_fig}")''',
  '''    # main figures v49.6: 6 main figures (Fig2+Fig3 merged per 4-6 panels rule)
    #   1 = schematic (unchanged); 2 = merged calibration+benchmark (regenerated
    #       top row from mouse_pilot data at 178 mm, Arial >= 7 pt; bottom row =
    #       v47 figure3 relabelled d/e); 3 = drift ladder; 4 = TCGA map;
    #   5 = cross-organ (old figure5); 6 = brain (old figure6)
    run([PY, str(BASE / "notebooks" / "_regen_fig2_toprow_nc49.py")],
        "Regen Fig2 top row (NC v49.6)")
    run([PY, str(BASE / "notebooks" / "_merge_fig2_fig3_nc49.py")],
        "Merge Fig2+Fig3 (NC v49.6)")
    shutil.copy2(STAGE / "figure1.pdf", FIGS_NC / "figure1.pdf")
    shutil.copy2(FF / "figure2_merged_nc49.pdf", FIGS_NC / "figure2.pdf")
    shutil.copy2(FF / "nc49_fig_drift_ladder.pdf", FIGS_NC / "figure3.pdf")
    shutil.copy2(FF / "nc49_fig_tcga.pdf", FIGS_NC / "figure4.pdf")
    shutil.copy2(STAGE / "figure5.pdf", FIGS_NC / "figure5.pdf")
    shutil.copy2(STAGE / "figure6.pdf", FIGS_NC / "figure6.pdf")
    for i in range(1, 14):
        shutil.copy2(STAGE / f"figure_S{i}.pdf", FIGS_NC / f"Supplementary_Fig_{i}.pdf")
    shutil.copy2(STAGE / "CKI_graphical_abstract.pdf",
                 FIGS_NC / "CKI_graphical_abstract.pdf")
    n_fig = len(os.listdir(FIGS_NC))
    check(n_fig == 20, f"V49-1 figures staged = 20 (6 main + 13 supp + GA pdf) got {n_fig}")'''),
 ('99_build_nc_v49.py',
  '''    # figure legends 1-7 order + new figure identity
    for i in range(1, 8):
        check(f"Figure {i}." in ms, f"V49-N19 Figure {i} legend present")
    check("drift" in ms[ms.find("Figure 4."):ms.find("Figure 4.") + 400].lower(),
          "V49-N20 Figure 4 legend is drift ladder")
    check("pan-cancer" in ms[ms.find("Figure 5."):ms.find("Figure 5.") + 400].lower(),
          "V49-N21 Figure 5 legend is pan-cancer map")''',
  '''    # figure legends 1-6 order + new figure identity (v49.6: 6 main figures)
    for i in range(1, 7):
        check(f"Figure {i}." in ms, f"V49-N19 Figure {i} legend present")
    check("drift" in ms[ms.find("Figure 3."):ms.find("Figure 3.") + 400].lower(),
          "V49-N20 Figure 3 legend is drift ladder")
    check("pan-cancer" in ms[ms.find("Figure 4."):ms.find("Figure 4.") + 400].lower(),
          "V49-N21 Figure 4 legend is pan-cancer map")
    check("benchmarking" in ms[ms.find("Figure 2."):ms.find("Figure 2.") + 200].lower()
          and "(e) ROC curves" in ms[ms.find("Figure 2."):ms.find("Figure 3.")],
          "V49-N21b Figure 2 legend is merged calibration+benchmark (panels a-e)")'''),
]

# group by file, apply atomically per file
by_file = {}
for fp, old, new in E:
    by_file.setdefault(fp, []).append((old, new))

fails = 0
for fp, items in by_file.items():
    t = open(fp, encoding='utf-8').read()
    applied = skipped = 0
    for old, new in items:
        n_old, n_new = t.count(old), (t.count(new) if new else 0)
        if n_old == 1:
            t = t.replace(old, new, 1)
            applied += 1
        elif n_old == 0 and (new == '' or n_new >= 1):
            skipped += 1
        else:
            print(f'FAIL {fp}: old x{n_old}, new x{n_new} :: {old[:70]!r}')
            fails += 1
    if applied:
        open(fp, 'w', encoding='utf-8', newline='').write(t)
    print(f'{fp}: applied={applied} already={skipped}')

if fails:
    print(f'\n*** {fails} REPLACEMENTS FAILED — nothing guaranteed; review ***')
    sys.exit(1)
print('\nAll replacements settled.')
