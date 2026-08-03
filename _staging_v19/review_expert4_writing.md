# Expert Review #4: Writing & Journal Strategy

## Overall Assessment

The manuscript presents a well-motivated computational method (CKI) with extensive multi-dataset validation and a compelling biological narrative. However, the current v19 draft contains several critical defects that would likely trigger immediate editorial concern at NAR: an unfilled Python template variable in the Introduction, a factual error in the human-vs-mouse comparison, empty Tables 1–2, a citation misassignment, and multiple uncited references. The writing is generally of publication quality but requires careful copy-editing before submission. **Score: 6/10.**

## Strengths

- **Strong conceptual framing.** The Ka/Ks analogy is introduced effectively in the Introduction (lines 14–15) and honestly deconstructed in the Discussion (line 93). The manuscript does not overclaim formal equivalence, which is appropriate.
- **Logical Results progression.** The four-dataset arc (mouse calibration → human validation → cancer application → brain regional analysis) builds naturally from method validation to biological discovery.
- **Honest limitations section.** The Discussion (line 97) acknowledges six specific limitations, including pseudobulk-level operation, HVG inflation, and the hypothesis-generating nature of brain signals. This is commendable.
- **Comprehensive statistical reporting.** Most quantitative claims include sample sizes, test types, P-values, and effect sizes (e.g., line 60: Jonckheere-Terpstra P < 0.001 for Edmondson grade; Kruskal-Wallis P = 0.0002 for PAM50).
- **Professional cover letter.** The letter is concise, well-structured, and includes AI disclosure, code availability, and six reviewer suggestions with no declared conflicts.
- **Reproducibility commitment.** The Reproducibility Guide is unusually thorough, with exact package versions, random seeds, file paths, and a checklist.

## Critical Issues (must fix before submission)

### C1. Unfilled Python template variable in Introduction

- **Location:** Manuscript, Introduction, line 16, paragraph 4
- **Problem:** The text reads: "confirming that random splits of the same cell population yield ω above 1 (empirical calibration baseline `{_mc["control_mean"]:.2f}`)." This is an unrendered Python f-string placeholder. It should have been replaced with the actual value (6.67) during manuscript generation. This is the kind of error that immediately signals careless preparation to an editor.
- **Fix:** Replace `{_mc["control_mean"]:.2f}` with `6.67`. Implement a pre-submission checklist that flags all `{...}` patterns in the final text.

### C2. Factual error: human ω described as "substantively higher" than mouse

- **Location:** Manuscript, Results, line 51, paragraph 2 (Tabula Sapiens section)
- **Problem:** The text states: "Human ω values ranged from 1.10 to 58.69 (mean 14.23, median 13.81, n = 5,151 pairs), **substantively higher** than mouse (mean 27.31)." The human mean (14.23) is in fact **lower** than the mouse mean (27.31), not higher. The subsequent sentence ("This difference likely reflects both the larger number of cell types (102 vs. ~32) and greater donor heterogeneity in human data") provides a rationale for higher values, which is internally contradictory with the numbers as written.
- **Fix:** Either (a) correct the direction to "substantively **lower** than mouse" and revise the explanatory sentence accordingly, or (b) verify that 27.31 is the correct mouse overall mean (it is not explicitly stated elsewhere in the Results; it may be conflated with a specific category). If the numbers are swapped, correct both the values and the explanation.

### C3. Tables 1 and 2 are empty placeholders

- **Location:** Manuscript, Results, lines 53–54 (Table 1) and lines 62–63 (Table 2)
- **Problem:** Both table captions appear in the text but no table content follows. Line 53 reads "Table 1. Classification AUC of five metrics on Tabula Sapiens (102 cell types, 5,151 pairs)." followed by a blank line, then the narrative resumes at line 55. The same occurs for Table 2 at line 62. NAR requires tables to be embedded in the manuscript or provided as separate files with clear cross-references. As written, a reader or reviewer cannot evaluate the tabulated data.
- **Fix:** Insert the actual table content (at minimum, column headers and data rows) immediately after each caption. If tables are provided as separate files, add an explicit note: "[Table 1 provided as separate file]" and ensure the submission system includes them.

### C4. Citation misassignment: ref 32 (Tran, batch correction) cited for endothelial cell biology

- **Location:** Manuscript, Results, line 65, last sentence
- **Problem:** The text reads: "Endothelial cells are known to express organ-specific gene programs tailored to local vascular needs (32)." Reference 32 is Tran,H.T.N. et al. (2020) "A benchmark of batch-effect correction methods for single-cell RNA sequencing data" (*Genome Biol.*). This paper is about batch-effect correction benchmarks, not endothelial cell organ-specific gene programs. The intended citation is likely ref 36 (Wälchli et al., 2024, brain vasculature atlas) or ref 39 (Schaffenrath et al., 2024, BBB heterogeneity).
- **Fix:** Replace "(32)" with the correct reference. Based on context, "(36)" (Wälchli et al.) is the most likely intended citation. If ref 32 (Tran) is genuinely uncited after this correction, remove it from the reference list.

### C5. Multiple uncited references in the reference list

- **Location:** Manuscript, References, lines 127–167
- **Problem:** At least six references appear in the reference list but are not cited in the manuscript text:
  - **Ref 16** (Regev et al., 2017, Human Cell Atlas) — not cited
  - **Ref 19** (Yang et al., 2024, human fetal cerebellum) — not cited
  - **Ref 24** (Storey & Tibshirani, 2003, FDR) — not cited, despite FDR being used extensively
  - **Ref 30** (Luecken & Theis, 2019, best practices) — not cited
  - **Ref 31** (Nei & Gojobori, 1986, synonymous substitutions) — not cited, despite Ka/Ks being central
  - **Ref 33** (CZI, 2025, CELLxGENE) — mentioned in Data Availability but not cited as "(33)" in text
  - **Ref 36** (Wälchli et al., 2024, brain vasculature) — not cited (likely the intended ref for line 65, see C4)
- **Fix:** Either cite each reference at the appropriate location in the text, or remove uncited references. Ref 31 (Nei & Gojobori) should definitely be cited in the Introduction where Ka/Ks is introduced (line 14). Ref 24 (Storey) should be cited where BH-FDR is first mentioned. Ref 36 (Wälchli) should replace the erroneous ref 32 at line 65.

## Major Issues (should fix)

### M1. Abstract claim "confirmed baseline behavior" is misleading given ω = 6.67

- **Location:** Manuscript, Abstract, line 10
- **Problem:** The abstract states: "Calibration confirmed baseline behavior for equivalent populations (mean ω = 6.67, all P > 0.05)." A mean ω of 6.67 for split-half controls is 6.67-fold above the theoretical baseline of ω = 1, which the manuscript itself attributes to systematic HVG inflation (Discussion, line 91). Saying this "confirmed baseline behavior" is contradictory. The main text (line 47) is more careful: "We note that while these results are consistent with baseline behavior, formal equivalence testing... would provide stronger statistical evidence."
- **Fix:** Revise the abstract to: "Calibration showed that equivalent populations yield non-significant ω (mean = 6.67, all P > 0.05), establishing an empirical baseline inflated by HVG selection." This is accurate without overclaiming.

### M2. Abstract mischaracterizes 30 Strong candidates as "developmental origin signatures"

- **Location:** Manuscript, Abstract, line 10
- **Problem:** The abstract says "Brain regional analysis identified 30 cell-type-specific developmental origin signatures among 31,764 comparisons." However, the manuscript (lines 73, 96) attributes the 30 Strong candidates to **four distinct mechanisms**: (i) developmental origin heterogeneity, (ii) embryonic colonization route boundaries, (iii) compartmentalized developmental specification, and (iv) postnatal cell migration. Only mechanisms (i) and partially (iii) are "developmental origin" per se. Lumping all four under "developmental origin signatures" is imprecise.
- **Fix:** Revise to: "Brain regional analysis identified 30 cell-type-specific developmental signatures spanning four biological mechanisms among 31,764 comparisons." Or more simply: "30 Strong candidate developmental signals."

### M3. Figure 5 legend incorrectly states "between human and mouse"

- **Location:** Manuscript, Figure legends, line 116, Figure 5A
- **Problem:** The legend reads: "CKI ω ranking of 17 cell types with cross-organ comparisons (n = 59 pairs) **between human and mouse**." However, the Results text (line 64) states these 59 pairs are from Tabula Sapiens (human) only: "Among the 5,151 Tabula Sapiens cell-type pairs, 59 are same-cell-type cross-organ comparisons." The Reproducibility Guide (line 127) also says "Subset of 60 same-cell-type cross-organ pairs from Tabula Sapiens data." There is no mouse data in this analysis.
- **Fix:** Change "between human and mouse" to "within the Tabula Sapiens human atlas" or simply "in human data."

### M4. Cover letter overstates mathematical relationship as "orthogonal"

- **Location:** Cover Letter, line 17
- **Problem:** The cover letter states CKI "decomposes Jensen–Shannon divergence into two **orthogonal** components." The manuscript itself (Discussion, line 93) explicitly disclaims formal mathematical equivalence with Ka/Ks and notes that CKI "lacks an analogous cancellation mechanism." The negative correlation between CKI ω and standard metrics (r = −0.38 to −0.57) indicates statistical independence, not mathematical orthogonality. Using "orthogonal" in the cover letter but then walking it back in the Discussion creates an inconsistency that a sharp editor will notice.
- **Fix:** Replace "orthogonal" with "complementary" or "independent" in the cover letter. For example: "decomposes Jensen–Shannon divergence into two complementary components: a baseline divergence rate... and a functional divergence rate..."

### M5. Graphical Abstract is a placeholder

- **Location:** Manuscript, line 7–8
- **Problem:** The text reads: "Graphical Abstract\n[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]" NAR requires the graphical abstract to be submitted as a figure file at the time of submission. A text placeholder in the manuscript is not acceptable.
- **Fix:** Create the graphical abstract figure and submit it as a separate file. The figure should visually communicate: (1) the Ka/Ks → CKI analogy, (2) the k_n/k_f decomposition, (3) the ω = k_f/k_n ratio, and (4) one key result (e.g., the negative correlation with standard metrics or the brain cell-type gradient).

### M6. Discrepancy in cross-organ pair count: 59 vs 60

- **Location:** Manuscript line 64 (59 pairs) vs Reproducibility Guide line 127 (60 pairs)
- **Problem:** The manuscript states "59 are same-cell-type cross-organ comparisons" while the Reproducibility Guide states "Subset of 60 same-cell-type cross-organ pairs." This 1-pair discrepancy, while minor numerically, undermines reproducibility confidence.
- **Fix:** Verify the exact count from the raw data file (results/phase35_cross_organ_conservation.csv) and correct both documents to match.

### M7. Figure legends lack consistent statistical details

- **Location:** Manuscript, Figure legends, lines 112–125
- **Problem:** While some figure legends include statistical details (e.g., Fig 2D: "Stars indicate significance: *** P < 0.001, ** P < 0.01, * P < 0.05"), many panels lack key information:
  - **Fig 1C:** No n or P-value for the bootstrap distribution shown.
  - **Fig 2C:** Mentions "negative correlation" but no Spearman r or P-value.
  - **Fig 3A:** No specific correlation values in the legend (they are in the main text but should be in the legend too for standalone readability).
  - **Fig 4:** No P-values for the NN vs. TT comparisons shown in panels A–B.
  - **Fig 6B–C:** No P-values for the cross-cell-type comparisons or clustering significance.
- **Fix:** Add statistical details (n, test type, P-value or significance threshold) to each panel legend that shows quantitative data. NAR reviewers expect legends to be self-contained.

## Minor Issues (suggestions)

### m1. Informal sentence starts with "But"

- **Location:** Manuscript, Introduction, line 13
- **Problem:** "But after correction, a key question remains" — starting a sentence with "But" is informal for a scientific manuscript.
- **Fix:** Change to "However, after correction, a key question remains."

### m2. "± —" formatting for single-sample cell types

- **Location:** Manuscript, Results, line 65
- **Problem:** "Smooth muscle cells (mean 6.29 ± —, n = 1)" and "Memory B cells (mean 16.83 ± —, n = 1)" use "± —" (em-dash) where standard deviation is undefined. This is awkward.
- **Fix:** For n = 1, report only the mean: "Smooth muscle cells (mean 6.29, n = 1)."

### m3. Inconsistent use of ω vs. "omega"

- **Location:** Throughout manuscript and supplementary
- **Problem:** The manuscript uses "ω" (Greek symbol) in most places but the supplementary materials use "omega" (spelled out). While this is understandable for plain-text supplementary files, consistency within the manuscript is important.
- **Fix:** Use "ω" consistently in the manuscript. In the supplementary, add a note: "ω denotes omega throughout" or use the Unicode symbol if the format allows.

### m4. Broken sentence in Supplementary Note 1

- **Location:** Supplementary, line 18, section 1.1
- **Problem:** The paragraph contains a broken sentence: "...are normalized to probability distributions via softmax normalization (p_i = exp(x_i)/Σexp(x_j))." This appears to be a continuation of a previous sentence that was truncated or merged incorrectly. The preceding text discusses the JS divergence bound and a floor value, then abruptly jumps to normalization.
- **Fix:** Reconstruct the sentence. Likely: "Both pseudobulk vectors ε_A and ε_B are normalized to probability distributions via softmax normalization..."

### m5. Reproducibility Guide lists sole author

- **Location:** Reproducibility Guide, line 3
- **Problem:** The header reads "Li Zhang1,2,*" as the sole author, while the manuscript lists two authors (Xianming Wu and Li Zhang).
- **Fix:** Include both authors: "Xianming Wu1, Li Zhang1,2,*" or note that the guide is authored by the corresponding author on behalf of both.

### m6. P-values reported as thresholds rather than exact values

- **Location:** Throughout manuscript (e.g., lines 52, 55, 58, 60)
- **Problem:** Many P-values are reported only as "P < 0.001" or "P < 0.05" without exact values. NAR encourages exact P-values where computable.
- **Fix:** Where computable, report exact P-values (e.g., "P = 2.3 × 10⁻⁷" instead of "P < 0.001").

### m7. OPC cross-region pair count identical to microglia

- **Location:** Manuscript, line 77 and line 96
- **Problem:** Both OPCs (line 77: "0 Strong signals among 5,671 OPC cross-region comparisons") and microglia (line 69: "n = 5,671 pairs across 107 regions") are reported with exactly 5,671 pairs. While this could be coincidental, the identical count is suspicious and should be verified.
- **Fix:** Verify the OPC pair count from the raw data. If correct, add a note that the counts happen to coincide. If incorrect, fix the number.

### m8. Reference count mismatch

- **Location:** Manuscript, References section
- **Problem:** The manuscript contains 41 references (lines 127–167), not 37 as stated in the review brief. This is not an error per se, but reviewers should verify the count matches the in-text citations after fixing C5 (uncited references).
- **Fix:** After resolving uncited references (C5), recount and ensure all references are cited and all citations have corresponding entries.

### m9. "We realized" is informal

- **Location:** Manuscript, Introduction, line 14
- **Problem:** "We realized that this question mirrors a problem addressed in molecular evolution" — "We realized" is somewhat informal and focuses on the authors' thought process rather than the scientific content.
- **Fix:** Change to "This question mirrors a problem addressed in molecular evolution."

### m10. Missing "choroid plexus" in brain Results narrative

- **Location:** Manuscript, Results, line 69
- **Problem:** The Results text describes ω values for 9 of 10 cell classes but omits choroid plexus from the narrative. The cell class is listed in the Methods (line 27: "choroid plexus (7,689)") but never discussed in the Results.
- **Fix:** Add a brief mention of choroid plexus ω values, or state explicitly that it was omitted for brevity and refer to Figure 6B.

## Score Breakdown

| Category | Score | Notes |
|---|---|---|
| Narrative Structure | 7/10 | Well-organized arc; minor flow issues in brain section |
| Abstract Quality | 6/10 | Within word limit (~177 words); misleading baseline claim and mechanism mischaracterization |
| Clarity & Precision | 5/10 | Template artifact, factual error, citation errors undermine precision |
| Cover Letter | 7/10 | Professional and concise; "orthogonal" overstates; reviewer list appropriate |
| NAR Compliance | 5/10 | Uncited references, empty tables, placeholder graphical abstract, citation error |
| Language Quality | 7/10 | Generally publication-quality; a few informal constructions and broken sentences |
| Journal Fit | 7/10 | Reasonable NAR fit; method is heuristic but well-validated |
| **OVERALL** | **6/10** | Solid science undermined by preparation errors; fixable |

## Journal Recommendation

- **Primary: Nucleic Acids Research**, likelihood: **30–35%**
  - **Rationale:** CKI is a computational method for transcriptomic analysis with open-source software, which fits NAR's methods scope. The multi-dataset validation (mouse, human, TCGA, brain; millions of cells) and the Ka/Ks conceptual framing are strengths. However, NAR editors may have concerns: (1) the method is heuristic, not theoretically grounded (acknowledged in Discussion); (2) ω = 6.67 for "equivalent" populations undermines the ω = 1 baseline concept; (3) the brain analysis is explicitly hypothesis-generating; (4) the method itself is relatively simple (ratio of two JS divergences on different gene sets). The critical preparation errors (C1–C5) would likely cause desk-reject if not fixed. Once fixed, the paper has a reasonable but not strong chance at NAR.

- **Alternative 1: Bioinformatics**, likelihood: **45–55%**
  - **Rationale:** More methodologically focused journal that values practical computational tools. The CKI Python package and reproducibility guide would be strong assets. The heuristic nature of the method is less of a concern here. However, the biological applications (cancer, brain) may be seen as secondary.

- **Alternative 2: Genome Biology**, likelihood: **25–30%**
  - **Rationale:** Higher impact than NAR for computational genomics, but also more selective. The multi-scale biological applications and conceptual novelty are strengths. The heuristic limitation and lack of formal evolutionary model may be concerns.

- **Alternative 3: Cell Systems**, likelihood: **15–20%**
  - **Rationale:** Would require reframing as a systems biology contribution. The brain developmental signature detection and cancer convergence findings could appeal, but the method's simplicity relative to Cell Systems' typical fare may be a barrier.

**Recommendation:** Fix all critical issues (C1–C5) and major issues M1–M3 before any submission. Submit to NAR as primary target given the methods + genomics fit. If rejected, Bioinformatics is the strongest fallback.
