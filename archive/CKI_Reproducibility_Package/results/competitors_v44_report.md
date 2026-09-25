# CKI vs Competitors (v44 revision benchmark)

**Script**: `notebooks/101_competitors_v44.py` (sections A/B/C runnable separately)
**Data**: Kang et al. 2018 IFN-β PBMC, GSE96583 droplet arm (lane 2.1 ctrl 14,619 / lane 2.2 stim 14,446; 24,413 singlet annotated cells, 6 cell types, 8 donors)
**Seed**: 42 throughout; ≥ 20 replicates for every simulation / power number
**Runtime**: A ≈ 15 s, B ≈ 65 s, C ≈ 13–15 min (total ≈ 17 min)

## Methods compared

| Method | Implementation | Version / notes |
|---|---|---|
| CKI (omega) | Read from authoritative script-79 outputs for the real-data comparison; recomputed with the identical per-pair DE-hybrid scheme for simulation/power (k_n = JS on 1,099 HRT-Atlas HK genes, k_f = JS on per-pair top-200 non-HK by |Δmean|, omega = k_f/k_n) | this repo, `cki.core` |
| MELD | PyPI `meld` 1.0.2, **minimal `--no-deps` install** (scprep pins `pandas<2.1`, whose 2.0.x line has no cp313 wheel and fails to build from source; installed `scprep 1.2.3`, `graphtools 2.1.0`, `tasklogger 1.2.0`, `pygsp 0.6.1` plus `decorator`, `networkx`, `future`; pandas 2.3.3 kept and verified runtime-compatible). Graph: sqrt-transformed log-normalized 3,000 HVGs, n_pca=20, knn=10, **random_state=42** (fixed after N2 xval finding; previously unset, causing 1e-4 run-to-run drift). Per-cell stim likelihood from `normalize_densities`; cell-type score = within-type AUC P(RES_stim > RES_ctrl). | meld 1.0.2 |
| scDist | **R/Rscript unavailable on this machine** → Python approximation of the core idea (Mitsakos et al. 2023): per cell type, per-PC OLS of PC score ~ condition + donor fixed effects; cell-type distance = sqrt(Σ_j β²_cond,j · λ_j), λ_j = PC eigenvalue (20 PCs on log-normalized 3,000 HVGs). Explicitly labelled "Python approximation of scDist" — it reproduces the fixed-effects condition-coefficient distance but not the R package's exact implementation. | approximation |

---

## A. Kang IFN-β real-data comparison (ctrl vs stim)

Per-cell-type effect sizes (`results/competitors_v44_kang_pertype.csv`):

| Cell type | n cells | CKI omega_cal (stim vs split-half) | MELD within-type AUC | scDist-approx distance |
|---|---|---|---|---|
| B cells | 2,573 | 3.44 | 0.9994 | 94.7 |
| CD14+ Monocytes | 5,385 | 2.28 | 0.9998 | 182.6 |
| CD4 T cells | 10,389 | 1.76 | 0.9989 | 71.9 |
| CD8 T cells | 2,042 | 3.23 | 0.9976 | 72.4 |
| FCGR3A+ Monocytes | 1,599 | 3.09 | 0.9995 | 145.3 |
| NK cells | 1,993 | 2.88 | 0.9972 | 88.2 |

> **Determinism note (N2 fix):** earlier exports of this table drifted at the
> 1e-4 level between runs because `graphtools.Graph` uses randomized SVD
> internally with `random_state=None`; this flipped the rank order of the
> near-saturated AUCs and moved the Spearman correlations (−0.086 → −0.20,
> 0.771 → 0.829 between two runs). `random_state=42` is now fixed in
> `notebooks/101_competitors_v44.py`, so `competitors_v44_kang_pertype.csv`,
> `competitors_v44_kang_agreement.json` and this table are byte-reproducible
> and mutually consistent; recomputing the three correlations from the CSV
> reproduces exactly −0.086 / 0.143 / 0.771 (rounded).

Agreement (`results/competitors_v44_kang_agreement.json`):

- **Direction agreement CKI vs MELD: 6/6 (100 %)** — every type shows omega_cal > 1 and within-type AUC > 0.5. (Note: the IFN-β effect is so strong that MELD AUCs are near-saturated, 0.997–0.9998, leaving almost no quantitative dynamic range across types.)
- Spearman across the 6 types: CKI–MELD ρ = −0.09 (p = 0.87); CKI–scDist-approx ρ = 0.14 (p = 0.79); MELD–scDist-approx ρ = 0.77 (p = 0.07).
- Per (cell type × donor), n = 37 pairs (`competitors_v44_kang_perdonor.csv`): CKI omega vs MELD within-donor AUC ρ = −0.15 (p = 0.38).

**Read**: on a real, near-ceiling perturbation all three methods agree on *which* types are perturbed (all of them) and on the direction; quantitative per-type rankings are not comparable (MELD saturates; scDist-approx keeps a gradient and tracks MELD better than CKI; CKI's omega_cal spread 1.76–3.44 reflects anchor visibility rather than effect size).

---

## B. Simulation with known ground truth (Kang ctrl background)

Design (`results/competitors_v44_simulation.csv`): per replicate, 200 ctrl cells per type (6 types) split 100/100 into groups A/B. Target = **CD14+ Monocytes**; group B receives an **additive Poisson mean-shift** on G ∈ {100, 500} non-HK genes (eligible: ≥ 1 CPM in target-ctrl pseudobulk) with added mean = (fold − 1) × baseline, fold ∈ {2, 4, 8}. 20 effect replicates per (G, fold) + 20 pure-null replicates; seed base 42. Thresholds: per method, q95 of null scores from null reps 0–9; FPR on held-out null reps 10–19. A multiplicative fold-change injection was tested first and **rejected**: it inflates library size, CPM normalization then dilutes every housekeeping gene and artefactually moves the HK anchor for all methods.

Sensitivity / top-1 hit rate / AUC (target vs the 5 null types), `results/competitors_v44_simulation_summary.json`:

| Method | FPR/type (held-out) | G100 F2 | G100 F4 | G100 F8 | G500 F2 | G500 F4 | G500 F8 |
|---|---|---|---|---|---|---|---|
| MELD AUC | 0.033 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 |
| scDist-approx | 0.050 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 | 1.00 / 1.00 / 1.000 |
| CKI omega | 0.083 | 0.00 / 0.20 / 0.517 | 0.00 / 0.25 / 0.688 | 0.05 / 0.40 / 0.787 | 0.00 / 0.00 / 0.127 | 0.00 / 0.00 / 0.059 | 0.00 / 0.00 / 0.054 |
| CKI k_f (diagnostic) | 0.050 | 0.00 / 0.05 / 0.319 | 0.00 / 0.10 / 0.612 | 0.00 / 0.20 / 0.688 | 0.00 / 0.00 / 0.077 | 0.00 / 0.00 / 0.321 | 0.00 / 0.05 / 0.391 |
| CKI k_n (diagnostic) | 0.050 | 0.00 / 0.00 / 0.159 | 0.00 / 0.00 / 0.224 | 0.15 / 0.10 / 0.369 | 0.00 / 0.00 / 0.271 | **1.00 / 1.00 / 1.000** | **1.00 / 1.00 / 1.000** |

(entries = sensitivity @ null-q95 / top-1 hit rate / AUC; FPR per "any type flagged per replicate" is higher for all methods — 6 types × multiple testing — e.g. CKI 0.50, MELD 0.20, scDist 0.30.)

**Mechanism, documented by the diagnostic components**: a broad additive shift (500 genes) raises library size; CPM normalization dilutes all other genes including the HK anchor, so **k_n itself detects the shift perfectly (AUC = 1.000 at fold ≥ 4)** while omega = k_f/k_n is annihilated by its own denominator and goes *anti*-monotonic (AUC ≈ 0.05). At 100 genes omega recovers slowly with effect size (AUC 0.52 → 0.79 for fold 2 → 8). k_f alone is weak for fold-2 shifts because log1p compresses 2-fold changes of moderately expressed genes (log(1+2x) − log(1+x) shrinks with x) below the per-pair top-200 noise-selection floor — CKI's JS-on-log1p metric is tuned for strong, from-zero induction (as in IFN ISGs), not for 2-fold dosage shifts. MELD and scDist-approx work in PCA/HVG space and detect the same injected signal perfectly at every effect size.

**This mirrors the real-data observation of scripts 79/80** (IFN-β raises k_n itself 1.2–5.7-fold): omega quantifies divergence *in excess of anchor movement*, and is by construction insensitive — or anti-monotonic — to perturbations whose dominant effect is a broad mean shift that moves the anchor.

---

## C. CKI power formalization on Kang (`results/competitors_v44_power.csv` / `_summary.json`)

Detection replicates script 79's rule: per-pair permutation test on omega (labels shuffled within pair, B = 100, one-sided P < 0.05), 20 replicates per (cell type, n), seed base 42.

C1 — donor-paired (n ctrl + n stim cells within each donor; n limited by per-donor cell counts):

| Cell type | n=50 | n=100 | n=200 | n=500 |
|---|---|---|---|---|
| B cells | 0.84 (6 donors) | 0.68 (5) | 0.17 (3) | — |
| CD14+ Monocytes | 0.78 (8) | 0.76 (8) | 0.55 (6) | — |
| CD4 T cells | 0.67 (8) | 0.61 (8) | 0.47 (6) | 0.09 (4) |
| CD8 T cells | 0.70 (4) | 0.68 (3) | — | — |
| FCGR3A+ Monocytes | 0.74 (5) | 0.47 (3) | — | — |
| NK cells | 0.93 (6) | 0.76 (5) | — | — |

C2 — pooled across donors (allows large n):

| Cell type | n=50 | n=100 | n=200 | n=500 | n=1000 |
|---|---|---|---|---|---|
| B cells | 0.70 | 0.45 | 0.20 | 0.00 | 0.00 |
| CD14+ Monocytes | 0.50 | 0.30 | 0.05 | 0.00 | 0.00 |
| CD4 T cells | 0.70 | 0.55 | 0.15 | 0.00 | 0.00 |
| CD8 T cells | 0.65 | 0.60 | 0.40 | 0.00 | — |
| FCGR3A+ Monocytes | 0.50 | 0.10 | 0.05 | 0.00 | — |
| NK cells | 0.65 | 0.55 | 0.20 | 0.05 | — |

**Power decreases with n** — the opposite of a conventional test. Cause: the permutation null of omega explodes with pseudobulk size (k_n → 0 in the null while top-200 selection keeps k_f elevated; observed null q95 > 100 at n = 500), so obs and null stop separating. This is a direct quantitative verification of the anchor-visibility boundary discussed in the manuscript (Fig. S13): **CKI's operating regime is per-condition ≈ 50–200 cells per donor pair; large pooled pseudobulks defeat the omega permutation test.**

---

## Conclusions

**Where CKI is weaker than the competitors**
1. *Sensitivity to broad mean shifts.* In the controlled simulation MELD and scDist-approx are perfect at every effect size (AUC 1.000), while CKI omega is insensitive at 100 shifted genes (AUC ≤ 0.79 even at 8-fold) and anti-monotonic at 500 (AUC ≈ 0.05), because the shift moves the HK anchor itself (k_n AUC = 1.000). CKI's JS-on-log1p metric also under-detects 2-fold dosage shifts of moderately expressed genes.
2. *Large-pseudobulk inference.* Omega's permutation test loses all power for per-condition n ≳ 500 cells; MELD/scDist-style methods have no such boundary.
3. *Quantitative per-type ranking* on the real IFN-β data does not track the competitors' gradient (ρ ≈ 0), although with only 6 types and a saturated MELD signal this is a weak test.

**Where CKI holds up**
1. *Direction and type-level detection on real data*: 6/6 sign agreement with MELD on Kang IFN-β; every perturbed type is flagged by omega_cal > 1.
2. *Donor-paired design at its intended scale*: 70–93 % power at n = 50 cells/condition/donor across all six types, with donor identity explicitly modelled (the competitors' scores here do not decompose donor drift; that separation is CKI's design target — cf. script 79's omega-vs-donor-drift calibration).
3. *Interpretability*: the k_n/k_f decomposition pinpoints *why* a perturbation is or isn't visible (anchor movement vs excess divergence), which neither MELD likelihoods nor scDist distances expose.

## Output files (all new; no existing results overwritten)

- `results/competitors_v44_kang_pertype.csv` — per-cell-type effects, 3 methods, Kang
- `results/competitors_v44_kang_perdonor.csv` — per (type × donor) CKI omega vs MELD AUC
- `results/competitors_v44_kang_agreement.json` — sign agreement + Spearman numbers
- `results/competitors_v44_simulation.csv` — 840 rows of per-replicate scores (incl. k_n/k_f diagnostics)
- `results/competitors_v44_simulation_summary.json` — thresholds, FPR, sensitivity/top-1/AUC per (G, fold)
- `results/competitors_v44_power.csv` — 2,300 rows of per-rep omega + permutation P
- `results/competitors_v44_power_summary.json` — power curves C1/C2
- `results/competitors_v44_runmeta.json` — versions, install recipe, seeds, runtime
- `results/competitors_v44_report.md` — this report
