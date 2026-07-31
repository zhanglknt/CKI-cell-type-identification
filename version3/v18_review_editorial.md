# v18 Review: NAR Editorial/Formatting Expert

## Overall Score: 7/10
## Readiness: 70%

## Summary

The manuscript "CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling" is a well-structured computational methods paper that addresses most NAR submission requirements. The writing is clear, the four-dataset validation strategy is comprehensive, and the Ka/Ks analogy provides an accessible conceptual frame. The manuscript follows the correct section order (Introduction → Materials and Methods → Results → Discussion), the abstract is unstructured at 177 words (within the 200-word limit), and the reference format largely complies with NAR conventions (numbered citations, italic journal names, bold volumes, year in parentheses, et al. for >10 authors).

However, several critical issues must be resolved before submission. Most urgently, the manuscript contains a direct internal contradiction regarding Benjamini-Hochberg FDR correction: the Methods and Supplementary state FDR is applied, while the Limitations section and the Reproducibility Guide explicitly state it is NOT applied. A second critical inconsistency exists in the calibration ω value: the Abstract and Results report mean ω = 6.67, while the Methods, Discussion, and Limitations all cite ω = 1.54 for the same calibration experiment. Additionally, keywords are entirely absent—a mandatory NAR requirement—and Supplementary Figures S2–S7 are not referenced in the main text.

Beyond these critical issues, the submission package would benefit from resolving a TCGA normalization discrepancy (log2(TPM+1) vs. log2(TPM+0.001)), reconciling Table 1 cell-type/pair counts between the manuscript and the standalone table file, and adding an ethics statement. The cover letter is strong with 6 suggested reviewers, AI declaration, ORCID, and the required "not previously submitted to NAR" statement. Figure legends are complete and panel labels use uppercase A/B/C. The data availability section includes GitHub URL and Zenodo DOI.

## Critical Issues (must fix before submission)

- **[C1] FDR correction contradiction (internal inconsistency).** The manuscript Methods state "Benjamini-Hochberg FDR correction is applied within each dataset" (lines 22, 37, 43), and Supplementary Note 3 §3.3 confirms "Benjamini-Hochberg FDR correction is applied to the bootstrap P-values, and candidates passing FDR < 0.05 are reported as significant discoveries." However, the Limitations section (line 97) states "the 31,764 brain cross-region comparisons yielded 30 Strong candidates **without formal multiple testing correction**," and the Reproducibility Guide §5.2 (line 151) and §8 checklist (line 197) explicitly state: "FDR correction is **not** applied in the current analyses; all reported P-values are raw bootstrap P-values." The MANIFEST claims C6 fix "FDR statement added to manuscript and supplementary text," but the Reproducibility Guide and Limitations were not updated. This is a fundamental contradiction that will immediately erode reviewer confidence. **Action:** Determine whether FDR was actually applied in the code. If yes, update the Reproducibility Guide §5.2/§8 and the Limitations sentence to match. If no, remove all FDR claims from the Methods and Supplementary. All documents must tell the same story.

- **[C2] Calibration ω value inconsistency (6.67 vs. 1.54).** The same six random-split calibration controls are described with two different mean values:
  - Abstract (line 10): "mean ω = 6.67"
  - Results (line 47): "The mean ω was 6.67 (median 6.46, range 1.59–12.16)"
  - Methods/Statistical reporting (line 37): "The empirical calibration mean of ω = 1.54 for split-half equivalent populations"
  - Discussion (line 91): "mean observational ω = 1.54 for equivalent populations"
  - Limitations (line 97): "the calibration controls (random split of the same population, mean ω = 1.54)"

  The Abstract/Results say 6.67; the Methods/Discussion/Limitations say 1.54. One value is correct; the other must be an editing artifact. **Action:** Verify against the actual data (results/mouse_pilot_v2b_key_values.csv) and make all five locations consistent.

- **[C3] Keywords missing.** NAR requires a list of keywords (typically 3–8) after the abstract. The manuscript contains no "Keywords" line anywhere. This is a mandatory submission element. **Action:** Add keywords (e.g., "cell-state comparison; transcriptomic divergence; Jensen-Shannon divergence; housekeeping genes; single-cell genomics; Ka/Ks analogy; cancer transcriptomics; brain atlas").

- **[C4] Supplementary Figures S2–S7 not referenced in main text.** Only Supplementary Fig. S1 is cited in the main text (line 44: "Supplementary Fig. S1"). Supplementary Figures S2 (cross-species validation), S3 (TCGA per-cancer matrices), S4 (method comparison ROC-AUC), S5 (cross-organ conservation raw data), S6 (brain regional analysis details), and S7 (developmental signature detection) are never cited in the Introduction, Methods, Results, or Discussion. NAR requires all supplementary materials to be explicitly referenced in the main text. **Action:** Add parenthetical citations (e.g., "Supplementary Fig. S3") at appropriate locations in the Results sections for TCGA, brain analysis, and method comparison.

- **[C5] TCGA normalization discrepancy.** The manuscript Methods (line 26) states "TPM values from UCSC Xena, log2(TPM + 1) transformed." The Reproducibility Guide §4.3 (line 105) states "log2(TPM + 0.001) transformation." These are different transformations yielding different expression values and downstream ω results. **Action:** Verify which transformation was actually used in the code and make both documents consistent.

- **[C6] Table 1 cell-type and pair-count discrepancy.** The manuscript Table 1 title (line 53) reads "102 cell types, 5,151 pairs." The standalone Table1-2.txt reads "99 cell types, 4,851 pairs." The Reproducibility Guide (line 98) explains that 4,851 is a subset of 5,151 (300 pairs excluded for lacking shared HK genes or marker overlap), but the 102→99 cell-type reduction is unexplained. **Action:** Align the Table 1 title across all documents. If the method comparison used 4,851 pairs / 99 cell types, state this in the manuscript Table 1 title and explain the exclusion in the Methods.

- **[C7] Supplementary authorship inconsistency.** The Supplementary Materials title page lists only "Li Zhang" (line 3), and the Reproducibility Guide lists only "Li Zhang1,2,*" (line 3). The manuscript lists two authors: "Xianming Wu1, Li Zhang12*". Both supplementary documents should list both authors to match the main manuscript. **Action:** Add Xianming Wu to the Supplementary and Reproducibility Guide author lists.

## Major Issues (should fix)

- **[M1] Ethics statement absent.** NAR requires an ethics statement, even for computational studies using only public data. The manuscript contains no mention of ethics/IRB. **Action:** Add a brief statement, e.g., "Ethics statement: This study used only publicly available de-identified datasets. No new human or animal subjects were involved."

- **[M2] Figure resolution, column width, and font size not documented.** The MANIFEST confirms 300 DPI for the graphical abstract but does not specify resolution for figures 1–6. NAR requires ≥300 DPI for photographic images and ≥600 DPI for line art; single column width 86 mm, double column 178 mm; minimum font size 7 pt. None of these specifications are documented in the manuscript or manifest for the main figures. **Action:** Verify and document that all main figures meet NAR specifications (300+ DPI, correct column widths, ≥7 pt fonts). Add a note in the cover letter or manifest confirming compliance.

- **[M3] Software/Code section not fully structured per NAR format.** The Data Availability section covers project name (CKI), homepage URL (GitHub), archived DOI (Zenodo), programming language (Python), and license (MIT). However, the operating system specification is only in the Reproducibility Guide, not in the manuscript itself. NAR's structured "Software/Code availability" format expects all elements in one place. **Action:** Add a brief OS statement to the manuscript's Data Availability section (e.g., "The package runs on Windows, Linux, and macOS"), or consolidate the software availability information into a single structured paragraph.

- **[M4] Supplementary Tables S1, S3, S4 not referenced in main text.** Supplementary Table S2 is referenced (in Supplementary Fig. S5 legend, line 123), but Supplementary Tables S1 (parameter sweep), S3 (brain regional data), and S4 (migration candidates) are not cited in the main text. **Action:** Add citations in the relevant Results sections, e.g., "(Supplementary Table S1)" in the parameter sweep paragraph, "(Supplementary Table S3)" in the brain analysis section, and "(Supplementary Table S4)" in the migration section.

- **[M5] Abbreviations list absent.** The manuscript uses numerous abbreviations (CKI, HK, HVG, JS, FDR, TCGA, PAM50, NN/TT/TN, OPC, AUC, IQR, MGE/LGE, etc.). NAR does not strictly require a separate abbreviations list for research articles, but it is strongly recommended for methods papers with extensive terminology. **Action:** Consider adding an "Abbreviations" footnote or section listing non-standard abbreviations.

- **[M6] "Without formal multiple testing correction" in Limitations contradicts Methods.** Even if [C1] is resolved in favor of FDR being applied, the Limitations sentence (line 97) stating "30 Strong candidates without formal multiple testing correction" needs to be reconciled. If FDR was applied to bootstrap P-values but the multiplicative residual model's 30 Strong candidates were selected by threshold (residual < 0.3) rather than by FDR-corrected P-values, this distinction should be clarified. **Action:** Reword to distinguish between bootstrap FDR correction (which may have been applied) and multiple testing correction for the 31,764 residual-model comparisons (which was not).

## Minor Issues (nice to fix)

- **[m1] Reference 1 has a lowercase initial.** "Zhang,f." should be "Zhang,F." (line 127). All other references use uppercase initials correctly.

- **[m2] References not explicitly numbered in the text file.** The reference list (lines 127–167) is not numbered in the .txt representation. This is likely handled in the .docx, but verify that the final submission has numbered references (1)–(41).

- **[m3] Cover letter has exactly 6 reviewers (minimum threshold).** NAR requires ≥5 (or ≥6 per some interpretations). Six is sufficient but adding 1–2 additional suggestions would provide a buffer in case of conflicts.

- **[m4] Running title / short title not provided.** NAR typically requests a running title (≤50 characters). Not present in the manuscript. Consider adding "CKI: Quantifying Selective Transcriptomic Remodeling" or similar.

- **[m5] Corresponding author postal address incomplete.** The manuscript provides email (knightz@pumc.edu.cn) and ORCID but no postal mailing address. NAR may request a full postal address for correspondence.

- **[m6] "Supplementary Data are available at NAR Online" is very terse.** This standard placeholder is acceptable, but consider adding: "Supplementary Materials including Supplementary Notes 1–4, Supplementary Tables S1–S4, Supplementary Figures S1–S7, and Supplementary Data 1 are available at NAR Online."

- **[m7] Brain atlas cell counts: 10 cell classes vs. 9 listed counts.** Methods (line 27) lists 9 cell classes with counts (astrocytes through Bergmann glia) but mentions "committed oligodendrocyte precursors" as included within OPCs (110,454 total). Results (line 68) lists 10 separate classes including "committed oligodendrocyte precursor cells" with separate statistics. Clarify whether committed OPCs are a subset of OPCs or a separate class, and ensure the counts sum to 888,263.

- **[m8] Manuscript line 85 and line 97 are very long paragraphs.** These exceed 2,000 characters and may cause formatting issues in the .docx. Consider splitting into shorter paragraphs for readability.

## Strengths

- Clear, well-motivated Introduction with accessible Ka/Ks analogy and honest acknowledgment of heuristic limitations
- Comprehensive four-dataset validation strategy (mouse atlas, human atlas, TCGA, brain atlas) covering calibration, cross-species, cancer, and neuroscience applications
- Correct section order: Introduction → Materials and Methods → Results → Discussion
- Abstract is unstructured and 177 words (within 200-word limit)
- Reference format largely NAR-compliant: numbered citations, italic journals, bold volumes, year in parentheses, et al. for ≥10 authors
- Cover letter is thorough: 6 suggested reviewers with institutional emails, AI declaration, ORCID, "not previously submitted to NAR" statement, significance statement
- Data availability section includes GitHub URL and Zenodo DOI
- Graphical abstract placeholder present and file confirmed in manifest (300 DPI)
- All 6 main figures and 7 supplementary figures have complete legends with uppercase A/B/C panel labels
- Author contributions, funding, and conflict of interest statements all present
- Word count (~6,600 words Introduction–Discussion) is within NAR's typical range for methods articles
- Reproducibility Guide provides detailed software environment, parameter specifications, and output file listings
- MANIFEST clearly documents all v17→v18 fixes

## NAR Compliance Checklist Results

### Manuscript Structure
- [✓] Abstract: unstructured, ≤200 words (177 words confirmed)
- [✓] Section order: Introduction → Materials and Methods → Results → Discussion
- [✓] No line numbers, only page numbers (text file has no line numbers; verify in .docx)
- [✓] Graphical Abstract placeholder present (line 7–8; file in manifest at 300 DPI)

### Figures
- [✓] 6 main figures (figure1.pdf through figure6.pdf, confirmed in manifest)
- [✓] Supplementary figures S1–S7 (confirmed in manifest)
- [✓] Panel labels: uppercase A/B/C (confirmed in all figure legends)
- [✓] Figure legends present for all figures (Figures 1–6, Supplementary Figures S1–S7)
- [✗] Resolution ≥300 DPI — only graphical abstract confirmed at 300 DPI; main figures not documented
- [✗] Single column 86mm / double column 178mm — not mentioned anywhere
- [✗] Font size ≥7pt in figures — not mentioned anywhere

### References
- [✓] Numbered citation format: (1), (2,3), (4-7) — confirmed throughout manuscript
- [✓] Author format: Author,A.B., Author,C.D. and Author,E.F. (Year) Title. *Journal.*, **Vol**, Pages. — confirmed (one typo: "Zhang,f." in ref 1)
- [✓] ≤20 authors then et al. — all references with >10 authors use "et al."
- [✓] Journal name italic, volume bold — confirmed
- [✓] Year in parentheses after authors — confirmed

### Cover Letter
- [✓] ≥6 suggested reviewers with institutional emails (6 reviewers listed)
- [✓] AI tool usage declaration ("AI tools (LLMs) were used for writing assistance...")
- [✓] ORCID included (0000-0002-0698-0754)
- [✓] Statement that manuscript not previously submitted to NAR ("has not been previously submitted to Nucleic Acids Research")
- [✓] Brief significance statement (paragraph 2 of cover letter)

### Data/Code Availability
- [✓] "Data availability" section present (line 99)
- [✓] GitHub URL included (https://github.com/zhanglknt/CKI-cell-type-identification)
- [✓] Zenodo DOI included (10.5281/zenodo.15670808)
- [△] Software/Code section: project name ✓, homepage URL ✓, archived DOI ✓, OS ✗ (only in Reproducibility Guide, not in manuscript), programming language ✓ (Python), license ✓ (MIT) — partially compliant

### Supplementary
- [✓] Supplementary materials properly formatted (Notes 1–4, Tables 1–4, Data 1)
- [✗] Supplementary figures referenced in main text — only S1 referenced; S2–S7 missing
- [✗] Supplementary tables referenced — only S2 referenced (in supplementary legend); S1, S3, S4 missing

### Additional NAR Requirements
- [✓] Word count appropriate (~6,600 words, within 4,000–8,000 range)
- [✗] Keywords present — **MISSING** (mandatory)
- [✓] Author affiliations complete (two affiliations, both with institution and location)
- [✓] Conflict of interest statement ("The authors declare no competing interests")
- [✓] Funding statement (NSFC 32370682; National Science and Technology Major Project 2026ZD01910500)
- [✗] Ethics statement — **MISSING** (should state public data use only)

## Specific Recommendations

1. **Resolve the FDR contradiction first** [C1]. This is the most damaging issue—a reviewer who notices that the Methods claim FDR correction while the Limitations and Reproducibility Guide say it was not applied will question the rigor of the entire statistical framework. Check the actual code output files (results/*_bootstrap_results.csv) for a q_value column. If q_value exists and is used, FDR was applied—update the Reproducibility Guide and Limitations. If not, remove FDR claims from the Methods and Supplementary.

2. **Resolve the ω = 6.67 vs. 1.54 inconsistency** [C2]. This appears to be a versioning artifact from the v17→v18 update. The v18 MANIFEST mentions "mouse pilot bootstrap re-run with B=1000 (was B=500)," which may have changed the calibration values. Check results/mouse_pilot_v2b_key_values.csv for the actual mean ω of the six control comparisons, then update all five occurrences (Abstract, Results, Methods, Discussion, Limitations) to the correct value.

3. **Add keywords immediately** [C3]. This is a 2-minute fix but a mandatory requirement. Suggested: "cell-state comparison; transcriptomic divergence; Jensen-Shannon divergence; housekeeping genes; single-cell genomics; Ka/Ks analogy; cancer transcriptomics; brain cell atlas."

4. **Add supplementary figure/table citations** [C4, M4]. Go through the Results sections and add parenthetical references to S2–S7 and Supplementary Tables S1/S3/S4 at the appropriate locations. This is essential for NAR compliance.

5. **Reconcile TCGA normalization** [C5]. Check the actual analysis script (notebooks/06_phase34_v2.py) for whether log2(TPM + 1) or log2(TPM + 0.001) was used, then make the manuscript and Reproducibility Guide consistent.

6. **Align Table 1 across documents** [C6]. If the method comparison used 4,851 pairs (excluding 300 without shared HK genes), the manuscript Table 1 title should say "4,851 pairs" not "5,151 pairs," and the 102 vs. 99 cell-type count needs explanation.

7. **Add ethics statement** [M1]. A single sentence suffices: "This study used only publicly available, de-identified datasets. No new human or animal experiments were conducted."

8. **Verify figure specifications** [M2]. Confirm in the cover letter or a separate figure specification document that all main figures are ≥300 DPI, use 86 mm (single column) or 178 mm (double column) widths, and have ≥7 pt font.

9. **Fix the supplementary authorship** [C7]. Add Xianming Wu to the Supplementary Materials and Reproducibility Guide title pages.

10. **Fix reference 1 typo** [m1]. Change "Zhang,f." to "Zhang,F." in the reference list.
