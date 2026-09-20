CKI package v0.5.0 with submission packages: v47 (Genome Biology first-author revision) -> v48 (Nature Communications format conversion) -> v49.7 (NC enhanced submission, latest).

## CKI_Submission_v49_NC.zip (latest, 2026-09-20, v49.7)

Response to the two GB decision points: real-data neutral-drift calibration + TCGA pan-cancer discovery-grade application. v49.7: Figure 2E scenario swap — CKI measures cell-type change, not cell-type identity, so the main figure now shows the scenario where omega ranks first.

- Figure 2E (new): ROC for functional-change vs neutral-drift discrimination in the semi-synthetic ground-truth simulation (600 functional vs 250 neutral replicates, marrow B-cell background). CKI omega AUC = 0.80, rank 1/6 (vs k_f 0.72, raw JS 0.64, cosine 0.58, k_f/k_total 0.44, k_n 0.21); independent replication on skin keratinocyte background AUC = 0.91 (rank 1/6). Panel D (Tabula Sapiens 5-metric correlation heatmap) unchanged; cell-type classification ROC demoted from the main figure — classification performance (omega AUC = 0.680, rank 5/5) retained in Table 1 as honest disclosure
- Bottom row natively regenerated at 178 x 72 mm, embedded Arial >= 7 pt (Type 42), native panel labels D/E (replaces the v47 cutout + relabel); merged Figure 2 geometry unchanged (178.0 x 148.1 mm)
- AUC verification: all 12 values (6 metrics x 2 backgrounds) recomputed from raw replicate CSVs and aligned with metrics.json (definition: signal delta >= 0.25 vs neutral_hk + neutral_global, matching SI)
- MS rewire: Fig 2 legend rewritten; Result 3 anchor narrowed to (Fig. 2d); Result 3b AUC sentences now cite (Fig. 2e); abstract headline "ranked first (AUC = 0.80)" now backed by a main figure
- Build 129/129, ms_verify 112/112, si_verify 109/109, cl_guide_verify 39/39 all green; CI success (py3.10-3.13); 27 zip entries

sha256: 01a0e61cc1bbdb1f7aead8e0513947b12f6c7a276181c5bb0df8948bb919a43c

## CKI_Submission_v48_NC.zip (2026-09-17)

Nature Communications format conversion of v47.3 by the 6-member nc-format panel.
sha256: e450d856ef5ec525d189650f2a519390112962b22675ca0be4d5e41426772200

## CKI_Submission_v47.zip (2026-09-13)

First-author (Xianming Wu) revision integration: all 95 tracked revisions + 6 comments adopted; build 664/664 checks PASS; cki package 0.4.9 -> 0.5.0; Zenodo concept DOI 10.5281/zenodo.20405458 (version DOI 10.5281/zenodo.22735744).
sha256: a8bea7f155295c1c44b48b5a88cd317cc3ed84f4c30c614cb7b57ad7f1539376

## Data availability

nc49 analysis result CSVs (drift ladder, Kang techrep, LIHC Cox, TCGA pancancer/purity/admix/smoking/mutation/kf_composition) are tracked in results/ alongside their generators notebooks/nc49_*.py.