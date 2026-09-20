**Latest: v49.11 (2026-09-20) — MK analogy made substantive (author ruling on R2-C1).**

The Discussion now states the threefold correspondence explicitly: synonymous-site divergence (Ks) <-> HK-gene divergence (k_n), nonsynonymous divergence (Ka) <-> functional-gene divergence (k_f), and a species pair <-> the two cell populations compared — the McDonald–Kreitman-style mapping with a constrained (not neutral) reference class; omega is read against the empirical calibration baseline, never as evidence of positive selection. SI 1.4 synced; Fig 1a legend names k_n/k_f counterparts and anchors omega to the calibration baseline. Build 151/151 (+N53-N55), verify suites 117+109+39 all 0-fail; CI 4/4 green; zip 12,259,589 B, 27 entries, sha256 a0f1a58a38cf...389d7.

**Latest: v49.10 (2026-09-20) — expert-panel review fixes (A1-A7 editorial + B1-B8 conceptual).**

Following a six-reviewer blind panel (mean 4.42/10, Major Revision verdict), all confirmed items are fixed. Editorial: availability line lists Supplementary Tables 1-19; SI main-text figure pointers corrected to Fig. 3d/3b,c; SI Note 9 points to Table 1; Guide estimator-comparison pointer Supp. Fig. 7; brain Strong-candidate enumeration now sums to 39 (adds one committed OPC + one OPC, ground-truth strong_by_ct); TCGA k_n mean/median calibers cross-linked; SI Augur pointer = main-text ref. 37. Conceptual: SI weight-scheme AUC reconciliation clause (configuration criterion, not CKI use); Ka/Ks structural-inversion sentence citing McDonald-Kreitman as new ref [34] (refs 34-56 renumbered to 35-57); Table 1 cross-type caveat (descriptive, not calibrated); Abstract leads with the 1.74-fold size-balanced gradient (6.10-fold uncorrected, 199 words); brain screen donor-confounding disclosure; Methods CC provenance (32 LUSC-matrix cell-line samples assigned LIHC per barcode audit); TCGA cluster-bootstrap CI type stated (percentile). Build 148/148, ms_verify 117 + si_verify 109 + cl_guide_verify 39 all 0-fail; CI 4/4 green (py3.10-3.13); zip 12,259,394 B, 27 entries, sha256 a0f1a58a38cf…389d7.

CKI package v0.5.0 with submission packages: v47 (Genome Biology first-author revision) -> v48 (Nature Communications format conversion) -> v49.11 (NC MK-analogy substantive, latest).

## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.11)

Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application.

v49.9 (scope-of-index design argument): limited cross-cell-type discrimination of omega is expected by design, not a performance deficit — the Discussion "Scope of the index" paragraph now states this explicitly.

- Design argument added (Discussion): CKI detects state changes within a given cell type, not cell-type identity; because the housekeeping anchor is cell-type-specific (housekeeping gene sets may differ across cell types), k_n baselines are only directly comparable within the same cell type, so limited cross-type discrimination of omega delineates, rather than limits, the index's scope
- Intended domain stated: the comparison of biologically matched populations — the same cell type across organs, brain regions, or perturbation states (the paradigm of every analysis reported)
- No numbers added; zero conflict with the v49.8 classification-benchmark cut. Build 133/133 (new assertion V49-N38), ms_verify 116/116, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries

v49.8 (reframe): CKI measures cell-state dynamics, not cell-type identity — the cell-type classification benchmark is cut entirely rather than kept as a demoted disclosure.

- Classification benchmark removed: MS Result paragraph (omega AUC = 0.680, rank 5-of-5 sentences), the original Table 1 (classification metrics), the Methods classification clause, and the Fig 2 legend pointer to Table 1
- CKI_Tables_NC.xlsx now holds a single sheet: the former Table 2 (cross-organ conservation ranking) renumbered to Table 1, all 4 in-text references updated
- Cover letter: three spots rewritten to the cell-state-dynamics framing; Abstract keeps the name-origin expansion "CKI (Cell-type Ka/Ks-inspired Index)" with no cell-type application claims
- Build 132/132 (new assertions V49-N35 single-sheet Table 1 / V49-N36 classification cut / V49-N37 renumber), ms_verify 116/116, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries

v49.7 base (Figure 2E scenario swap): CKI measures cell-type change, not cell-type identity, so the main figure shows the scenario where omega ranks first.

- Figure 2E (new): ROC for functional-change vs neutral-drift discrimination in the semi-synthetic ground-truth simulation (600 functional vs 250 neutral replicates, marrow B-cell background). CKI omega AUC = 0.80, rank 1/6 (vs k_f 0.72, raw JS 0.64, cosine 0.58, k_f/k_total 0.44, k_n 0.21); independent replication on skin keratinocyte background AUC = 0.91 (rank 1/6). Panel D (Tabula Sapiens 5-metric correlation heatmap) unchanged; cell-type classification ROC demoted from the main figure — classification performance (omega AUC = 0.680, rank 5/5) at that point retained in Table 1; cut entirely in v49.8 — cross-type discrimination lies outside the index's intended scope (v49.9)
- Bottom row natively regenerated at 178 x 72 mm, embedded Arial >= 7 pt (Type 42), native panel labels D/E (replaces the v47 cutout + relabel); merged Figure 2 geometry unchanged (178.0 x 148.1 mm)
- AUC verification: all 12 values (6 metrics x 2 backgrounds) recomputed from raw replicate CSVs and aligned with metrics.json (definition: signal delta >= 0.25 vs neutral_hk + neutral_global, matching SI)
- MS rewire: Fig 2 legend rewritten; Result 3 anchor narrowed to (Fig. 2d); Result 3b AUC sentences now cite (Fig. 2e); abstract headline "ranked first (AUC = 0.80)" now backed by a main figure
- Build 129/129, ms_verify 112/112, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries

sha256: a0f1a58a38cf…389d7

## CKI_Submission_v48_NC.zip (2026-09-17)

Nature Communications format conversion of v47.3 by the 6-member nc-format panel.
sha256: e450d856ef5ec525d189650f2a519390112962b22675ca0be4d5e41426772200

## CKI_Submission_v47.zip (2026-09-13)

First-author (Xianming Wu) revision integration: all 95 tracked revisions + 6 comments adopted; build 664/664 checks PASS; cki package 0.4.9 -> 0.5.0; Zenodo concept DOI 10.5281/zenodo.20405458 (version DOI 10.5281/zenodo.22735744).
sha256: a8bea7f155295c1c44b48b5a88cd317cc3ed84f4c30c614cb7b57ad7f1539376

## Data availability

nc49 analysis result CSVs (drift ladder, Kang techrep, LIHC Cox, TCGA pancancer/purity/admix/smoking/mutation/kf_composition) are tracked in results/ alongside their generators notebooks/nc49_*.py.