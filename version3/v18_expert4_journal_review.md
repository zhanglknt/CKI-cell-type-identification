# CKI Manuscript Quality Review & Journal Strategy

**Reviewer**: Expert 4 — Manuscript Quality, Scientific Writing & Journal Strategy
**Review date**: 2026-07-27
**Manuscript version**: v18 (current codebase)
**Prior review reference**: v17_review_synthesis.md (2026-07-26)

---

## 1. Overall Manuscript Quality: 7.2 / 10

The manuscript presents a well-conceptualized computational method (CKI) with a clear Ka/Ks analogy, validated across four diverse datasets. The writing is generally clear and the narrative arc is compelling. The v18 version has resolved most of the v17 Critical issues (C1–C5, C7, C8), which is a significant improvement. However, the manuscript still suffers from excessive length in the brain analysis section, incomplete statistical rigor (FDR), and some remaining cross-document inconsistencies. The core idea is novel and timely, but the execution needs polishing before submission to a top-tier journal.

**Comparison to v17**: v17 scored 6.10/10 (composite of 4 experts). The current v18 version resolves 6 of 8 Critical issues, improving the manuscript to ~7.2. The remaining gap to 8.0+ is primarily due to the unaddressed FDR issue (C6) and structural/writing refinements still needed.

---

## 2. Strengths

1. **Novel conceptual framework**: The Ka/Ks analogy for transcriptomics is intuitive and well-motivated. Decomposing JS divergence into baseline (k_n) and functional (k_f) components is an elegant approach that addresses a real gap in the single-cell genomics toolkit.

2. **Comprehensive multi-dataset validation**: Four independent datasets (Tabula Muris, Tabula Sapiens, TCGA, Siletti brain atlas) spanning mouse, human, cancer, and neuroscience — this breadth is above average for a methods paper.

3. **Strong negative control design**: The OPC negative control (0 Strong signals despite highest motility) is a particularly convincing validation of the multiplicative residual model's specificity.

4. **Well-structured cover letter**: Meets all NAR requirements — 6 reviewers with institutional emails, AI declaration, ORCID, non-submission statement. Professional tone.

5. **Detailed reproducibility guide**: Includes exact software versions, random seed, parameter tables, output file listings, and a reproducibility checklist. This is above average for computational biology submissions.

6. **Clear NAR formatting compliance**: Unstructured abstract ≤200 words, correct section order (Introduction → Methods → Results → Discussion), NAR reference format with italic journal and bold volume, Graphical Abstract placeholder present.

7. **Honest limitations section**: The Discussion candidly acknowledges CKI's heuristic nature, the lack of formal phylogenetic framework, and the FDR limitation. This scientific honesty is appreciated.

8. **Open-source availability**: CKI Python package (v0.3.1) on GitHub with MIT License and Zenodo DOI — meets NAR's code availability requirements.

---

## 3. Concerns

### Critical

**C1. FDR correction still not applied (v17 C6, unresolved)**
The brain atlas analysis performs 31,764 cross-region comparisons and identifies 30 "Strong" candidates. The manuscript acknowledges (Discussion, P514) that "at a nominal alpha = 0.05, approximately 1,588 false positives would be expected" and that these are "hypothesis-generating signals." However, no formal FDR correction (BH, Storey q-value, or permutation-based FDR) is applied. The 30 Strong candidates are then extensively interpreted with detailed biological mechanisms across 6 subheadings (OPCs, oligodendrocytes, astrocytes, Bergmann glia, microglia, vascular cells, fibroblast). This level of interpretation goes well beyond "hypothesis-generating" framing and creates a tension between the stated caution and the depth of biological claims. At minimum, BH FDR should be applied to the residual values; ideally, a permutation-based null for the residual model should be established.

**C2. Cross-document consistency: Supplementary Algorithm 1 B-value**
The v17 review flagged that Algorithm 1 in Supplementary Note 2 stated "default B = 1,000" while the manuscript uses B = 500 for mouse. In the current supplementary file (`68_gen_supplementary_en.py`, line 217), the pseudocode now reads "B = 500 for main mouse analysis; 1,000 for human; 100 for TCGA and brain" — this is **fixed** in the inline comment. However, the Algorithm 1 pseudocode line 10 still reads `for b = 1 to B (B = 500 for main mouse analysis; 1,000 for human; 100 for TCGA and brain; see Methods)` which is correct but unusually verbose for pseudocode. This is now a Minor issue rather than Critical.

### Major

**M1. Brain analysis section is disproportionately long**
The brain regional analysis (Results section, from "Brain regional analysis reveals cell-type differentiation gradients" through "Fibroblast: the sole postnatal migration signal") spans approximately 3,000+ words and 7 sub-subheadings. This level of detail is more appropriate for a neuroscience specialty journal. For NAR, this section should be condensed by ~50%, with the cell-type-specific biological interpretations moved to supplementary materials.

**M2. Statistical reporting paragraph is excessively long**
The "Statistical reporting" paragraph (line 395) is a single ~400-word paragraph that covers bootstrap P-values, effect sizes, the ω = 1 vs. ω = 1.54 anchor justification, FDR transparency, and omnibus tests. This should be broken into shorter paragraphs or partially moved to Supplementary Note 3.

**M3. Negative correlation claim may be confounded by ratio structure**
The claim that CKI ω is "negatively correlated with all four standard metrics" is a central finding. However, since ω = k_f/k_n is a ratio, the negative correlation may be partly driven by spurious correlation of ratios (Pearson 1897). The v17 review flagged this (M2 in v17). The current manuscript does not include a partial correlation analysis controlling for k_n. This is a significant statistical gap that NAR reviewers may raise.

**M4. TCGA paired analysis: extremely small sample sizes**
The paired tumor-normal analysis uses n = 2–5 patients per cancer type. While the manuscript includes a caution statement, the results are still presented with Mann-Whitney P-values (P = 0.024 for LIHC). Drawing any conclusion from n = 2–5 is statistically untenable. These results should either be removed or explicitly labeled as purely exploratory without P-values.

**M5. Cross-organ conservation: several cell types with n = 1**
Table 2 includes cell types with n = 1 pair (e.g., B cells, smooth muscle cells). While noted in the text, presenting these alongside cell types with n = 30+ in the same ranking table is misleading. Consider adding a column for confidence intervals or marking low-n entries.

**M6. Multiplicative residual model thresholds lack formal validation**
The Strong (residual < 0.3), Moderate (< 0.5), and Weak (< 0.75) thresholds are empirical. No permutation null or sensitivity analysis for these specific thresholds is provided. The v17 review flagged this (M6 in v17); it remains unaddressed.

**M7. Data version/access dates missing**
None of the datasets include download dates or version identifiers. NAR reviewers may request this. Each dataset should note "accessed YYYY-MM-DD" at minimum.

### Minor

**m1. Subjective language**: "The most striking finding" (line 441), "Strikingly, all 10 signals..." (line 480), "Critically" (multiple instances). Academic writing should be more neutral.

**m2. Figure 5 legend says "between human and mouse"** (line 567) — but the cross-organ analysis is within Tabula Sapiens (human only). This appears to be a residual error.

**m3. Reference count (37) is low** for an NAR methods paper. Typical NAR methods papers cite 50–80 references. Key missing citations: original JS divergence (Lin 1991), Ka/Ks methodological references beyond Nei & Gojobori (1986), and recent cell-type comparison metrics.

**m4. "6.06-fold" gradient** is mentioned multiple times (lines 462, 569) — this is 14.36/2.37 = 6.06, but the computation should be explicitly stated at first mention.

**m5. Abbreviation definitions**: OPC is used before its first full definition in the brain results section. HVG is used in Methods without full expansion at first use (it is expanded in Supplementary Note 1.3 but not in the main text).

**m6. Author order discrepancy**: The manuscript lists "Xianming Wu" as first author (line 249) and "Li Zhang" as corresponding author (line 263). The cover letter (line 106) says "On behalf of my co-author, Dr. Xianming Wu" and signs as "Li Zhang (Corresponding Author)" then "Xianming Wu (First Author)". This is consistent but the cover letter phrasing "On behalf of my co-author" is unusual when the co-author is the first author — typically the first author writes the cover letter.

**m7. Line spacing**: The manuscript uses `line_spacing = 1.15` (line 72) but NAR requires single-line spacing (1.0). This should be corrected to 1.0 before submission.

**m8. Supplementary Table 3 and 4 descriptions are dynamically generated** with f-strings pulling from data files. If the data files change, the supplementary text will change. Ensure the generated DOCX matches the submitted version.

---

## 4. Structural & Flow Assessment

**Section order**: Introduction → Materials and Methods → Results → Discussion → Data availability → Supplementary Data → Acknowledgements → Author contributions → Funding → Conflict of interest → Figure legends → Supplementary Figure legends → References. This follows NAR requirements.

**Introduction (4 paragraphs, ~800 words)**: Well-structured. Progresses from the problem (standard metrics conflate noise and signal) → analogy (Ka/Ks) → solution (CKI) → validation overview. The fourth paragraph serves as a preview of results, which is effective. **Assessment: Good.**

**Materials and Methods (8 subsections, ~1,800 words)**: Comprehensive. Covers CKI computation, bootstrap test, datasets, method comparison, multiplicative residual model, clinical severity analysis, computational environment, and statistical reporting. The Statistical reporting subsection is too long (see M2). **Assessment: Good but needs trimming.**

**Results (6 major sections, ~3,500 words)**: 
- Results 1–3 (decomposition, calibration, method comparison) are well-paced.
- Result 4 (TCGA) is appropriate length.
- Result 5 (cross-organ) is concise.
- Result 6 (brain) is excessively long — 7 sub-subheadings for a single result section is unusual. **Assessment: Results 1–5 good; Result 6 needs significant condensation.**

**Discussion (7 paragraphs, ~1,400 words)**: Covers conceptual contribution, Ka/Ks limitations, complementarity with existing methods, cancer implications, brain analysis summary, limitations, and future directions. The limitations paragraph is well-constructed. **Assessment: Good.**

**Overall flow**: The narrative arc is logical and engaging. The transition from method development → calibration → validation → biological applications is natural. The main structural issue is the imbalance between the brain analysis and other results.

---

## 5. Writing Quality Assessment

**Overall**: The writing is clear, direct, and generally well-suited for NAR. The prose is accessible to a broad genomics audience. Below are specific examples:

**Good writing examples**:
- Line 350: "Single-cell transcriptomics has transformed how we study cells." — Strong opening, direct and engaging.
- Line 354: "We realized that this question mirrors a problem addressed in molecular evolution." — Clear motivation.
- Line 502: "CKI introduces a conceptual shift in transcriptomic comparison: from measuring absolute distance to quantifying functional divergence relative to an internal baseline." — Excellent topic sentence for Discussion.

**Examples needing improvement**:

1. **Overly long sentences**: Line 395 (Statistical reporting) contains a single sentence of ~80 words: "The P-value is anchored at the theoretical null of ω = 1 (k_f = k_n, i.e., zero functional divergence), which represents the formal null hypothesis that the two populations are functionally identical." This should be split.

2. **Subjective modifiers**: 
   - Line 441: "The most striking finding was that tumors are more transcriptionally homogeneous" → "Tumors were more transcriptionally homogeneous"
   - Line 480: "Strikingly, all 10 signals involved cortex/thalamus" → "All 10 signals involved cortex/thalamus"
   - Line 434: "Critically, CKI was the only metric where..." → "CKI was the only metric where..."

3. **Repetitive phrasing**: The phrase "baseline-normalized functional divergence" appears 4+ times. Vary the language.

4. **Jargon without definition**: "Seurat flavor" (line 368) is used without explanation for non-scverse users. "PAM50" is defined but "nearest centroid" classification method is not briefly explained.

5. **Passive voice overuse**: Line 371: "We randomly permute cell labels" (good, active) vs. line 395: "Effect sizes are reported as Cohen's d" (passive). Mix is acceptable but lean toward active voice.

6. **Tense inconsistency**: Results section mixes present and past tense: "CKI takes two cell populations as input" (present, line 405) vs. "We applied CKI to TCGA" (past, line 439). NAR prefers past tense for completed experiments.

**Grammar**: No grammatical errors detected. Spelling is correct throughout.

**Tone**: Appropriately scientific. The caveats about the Ka/Ks analogy (Discussion, line 506) are well-placed and show scientific maturity.

---

## 6. Abstract Review

**NAR requirement**: Unstructured, single paragraph, ≤200 words.

**Current abstract** (lines 325–343):
The abstract is a single unstructured paragraph. I estimate it at approximately **175–185 words** (exact count depends on f-string interpolation values), which is within the 200-word limit.

**Content assessment**:
- ✓ Background/motivation (standard metrics conflate baseline and functional variation)
- ✓ Method description (CKI decomposes divergence into k_n and k_f)
- ✓ Validation summary (four datasets)
- ✓ Key quantitative results (calibration, negative correlation, cancer, brain)
- ✓ Tool availability (open-source Python package)
- ✗ Does not explicitly state the Ka/Ks inspiration (only "heuristically inspired")
- ✗ Could be more specific about the negative correlation finding (currently says "indicating it captures an independent information dimension" — could state the Spearman r range)

**Assessment**: Good. Meets NAR requirements. Minor suggestion: add one clause specifying the Ka/Ks analogy more explicitly, and include the key numerical finding (e.g., "Spearman r = −0.38 to −0.57") to make the abstract more informative.

---

## 7. Cover Letter Review

**File**: `generate_cover_letter_nar.py`

**NAR requirements checklist**:

| Requirement | Status | Notes |
|-------------|--------|-------|
| 6+ recommended reviewers with institutional emails | ✓ | 6 reviewers: Theis, Teichmann, Welch, Yanai, Zhang, Wang — all with institutional emails |
| AI tool usage declaration | ✓ | "AI tools (LLMs) were used for writing assistance; all AI-generated text was reviewed and revised by the authors" |
| ORCID | ✓ | "ORCID: 0000-0002-0698-0754" |
| Statement not previously submitted to NAR | ✓ | "has not been previously submitted to Nucleic Acids Research" |
| No competing interests statement | ✓ | "declare no competing interests" |
| Code availability (GitHub + Zenodo DOI) | ✓ | GitHub URL + Zenodo DOI: 10.5281/zenodo.15670808 |
| Title and author identification | ✓ | Title centered, bold; corresponding + first author |
| Manuscript scope justification | ✓ | Explains CKI aligns with NAR's methods development scope |

**Content quality**: The cover letter is professional, concise (~350 words body), and effectively summarizes the key findings. The three-dimensional validation summary (orthogonal information, cross-dataset consistency, biological applications) is a strong structural choice.

**Issues**:
1. **m6** (Minor): The letter is signed by "Li Zhang (Corresponding Author)" then "Xianming Wu (First Author)" — typically only the corresponding author signs, and the first author is listed in the manuscript, not the cover letter signature.
2. **Reviewer diversity**: All 6 suggested reviewers are well-known, but 4 are from US/Europe and 2 from China. Consider suggesting at least one reviewer from a different computational biology subfield (e.g., information theory or statistical genomics).
3. **Reviewer conflicts**: The letter states "None of the suggested reviewers have recent collaborations or conflicts of interest with the authors." This is good, but NAR may ask for more specific conflict declarations (e.g., no co-authorships in the past 5 years).

**Assessment**: Meets all NAR requirements. Well-written. Minor formatting issues only.

---

## 8. Reproducibility Assessment

**File**: `notebooks/100_gen_reproducibility_docx.js`

**Strengths**:
1. **Exact software versions**: Python 3.13.12, numpy 2.4.6, scipy 1.17.1, etc. — excellent version control.
2. **Random seed**: Explicitly stated as 42 throughout all analyses.
3. **Parameter table**: Complete table with 17 parameters, their values, and which datasets they apply to.
4. **Output file listing**: Every output file is listed with its path and description.
5. **Reproducibility checklist**: 12-item checklist with all items checked.
6. **Data download URLs**: TCGA TPM, probeMap, and clinical data URLs provided.
7. **Algorithm definition**: Mathematical formulas explicitly written out.

**Weaknesses**:
1. **No containerization**: No Docker/Singularity image or conda environment.yml file is provided. For full reproducibility, a conda environment or Dockerfile should be included.
2. **Data access dates missing**: While URLs are provided, no download dates are specified.
3. **Brain atlas data access**: The Siletti et al. data is described as loaded from "Nonneurons.h5ad" but the exact download path or CZ CELLxGENE collection ID is not specified in the reproducibility guide (it is mentioned in the manuscript Methods).
4. **Hardware requirements**: States ">= 32 GB RAM" but doesn't specify CPU requirements or expected runtime for each analysis.
5. **FDR statement**: Section 5.2 explicitly states "FDR correction is NOT systematically applied" — while transparent, this is a reproducibility concern as it means reported P-values cannot be directly used for inference without correction.
6. **Cross-script dependencies**: The guide lists individual scripts but does not provide a master pipeline script or Makefile that runs all analyses in order.

**Cross-document consistency with manuscript**:
- ✓ Bootstrap B-values now match across all documents (500 mouse, 1000 human, 100 TCGA, 100 brain)
- ✓ HRT Atlas use_reference = False consistently stated
- ✓ Random seed = 42 consistently stated
- ✓ Gene selection parameters (top-2000 HVG for mouse, top-200 DE for human/TCGA/brain) match

**Assessment**: Above average reproducibility documentation. The remaining gaps (containerization, runtime estimates, pipeline orchestration) are common in computational biology submissions and unlikely to be blocking for NAR.

---

## 9. Reference Quality

**Total references**: 37 (numbered 1–41, with some gaps in citation numbering — see m3 from v17)

**Format compliance**: NAR format — `Author,A.B., Author,C.D. (Year) Title. *Journal.*, **Vol**, Pages.` — correctly applied. Journal names italicized, volume numbers bold. Authors listed up to 10, then "et al." (NAR allows up to 20 authors, so this is conservative but acceptable).

**Reference numbering**: The references array (`_refs_nar`) contains 41 entries (lines 181–221), numbered 1–41. However, the v17 review noted that "参考文献编号不连续（无(30)号引用但正文引用到(41)）". The current manuscript text references up to (41) in the figure legends. I do not see obvious gaps in the reference list itself, but the in-text citation continuity should be verified.

**Coverage assessment**:
- ✓ Single-cell methods: Harmony (1), scVI (2), SATURN (3), Scanpy (25), Seurat (26,27)
- ✓ Datasets: Tabula Muris (5), Tabula Sapiens (6), TCGA (7,8,28), Siletti brain atlas (9)
- ✓ HK genes: HRT Atlas (4)
- ✓ Cancer clinical: Edmondson (10), PAM50 (11,12)
- ✓ Brain development: OPC migration (13,17), astrocyte allocation (18), microglia (20,23,37,40), BBB (39), fibroblast (38), Bergmann glia (41)
- ✓ Statistical: Storey & Tibshirani (24)
- ✓ Evolutionary: Nei & Gojobori (31), PAML (21)
- ✗ Missing: Original JS divergence reference (Lin 1991 or Kullback & Leibler 1951)
- ✗ Missing: Original Ka/Ks concept reference (Kimura 1977 or Li 1997)
- ✗ Missing: Recent cell-cell distance metrics (e.g., CellTypist, scArches)
- ✗ Missing: Softmax normalization reference
- ✗ Missing: Benjamini-Hochberg FDR reference (1995)

**Assessment**: Reference quality is adequate but the count (37–41) is low for an NAR methods paper. Adding 10–15 references (especially foundational statistical and information-theoretic references) would strengthen the manuscript.

---

## 10. Journal Fit Analysis

### NAR Appropriateness: 7.5 / 10

**NAR scope statement**: "Nucleic Acids Research publishes the results of leading-edge research into physical, chemical, biochemical and biological aspects of nucleic acids and proteins involved in nucleic acid metabolism and/or interactions."

**Strengths for NAR**:
1. **Methods development focus**: CKI is a new computational method for transcriptomic analysis — directly aligns with NAR's methods section.
2. **HRT Atlas precedent**: Reference 4 (HRT Atlas v1.0) was published in NAR, creating a natural citation chain.
3. **Nucleic acid relevance**: CKI operates on RNA-seq data (transcriptomes), which falls under "nucleic acids" research.
4. **Multi-omics integration**: CKI bridges single-cell genomics and evolutionary biology concepts — interdisciplinary appeal.
5. **Open-source tool**: NAR encourages methods papers with available software.
6. **Formatting compliance**: The manuscript already follows NAR formatting conventions (abstract, section order, references, figures).

**Weaknesses for NAR**:
1. **Not directly about nucleic acid sequences**: CKI works on expression profiles, not sequences. Some NAR editors may view it as more of a computational biology method than a nucleic acids method.
2. **Brain analysis section depth**: The extensive brain developmental biology interpretation may seem out of scope for NAR's typical readership.
3. **Statistical rigor gaps**: NAR reviewers in the computational biology space are increasingly demanding FDR correction and formal statistical frameworks.
4. **Ka/Ks analogy without formal evolutionary model**: NAR's audience includes many evolutionary biologists who may find the heuristic analogy insufficient without a formal connection.
5. **Reference count**: 37 references is below the typical NAR methods paper (50–80).

**NAR scope fit verdict**: Good fit for NAR's Methods section, particularly if the brain analysis is condensed and the statistical framework is strengthened. The HRT Atlas citation chain and transcriptomic focus make NAR a natural home.

---

## 11. Ranked Journal Recommendations

### Rank 1: Nucleic Acids Research (NAR)

| Attribute | Value |
|-----------|-------|
| **Journal** | Nucleic Acids Research |
| **Publisher** | Oxford University Press |
| **IF (2025)** | ~16.6 |
| **Fit score** | 7.5 / 10 |
| **Estimated acceptance probability** | 25–35% (after revisions) |
| **Review timeline** | 8–12 weeks |

**Rationale**: CKI is a computational method for transcriptomic analysis, directly within NAR's methods scope. The HRT Atlas (ref 4) was published in NAR, creating a natural citation chain. The manuscript already follows NAR formatting. The multi-dataset validation and open-source tool availability are strengths. The main barriers are the FDR issue, the excessive brain analysis length, and the need for ~10 additional references. If the Critical and Major issues are addressed, NAR is the strongest target.

**Conditions for submission**:
1. Apply BH FDR to brain analysis (or establish permutation null for residuals)
2. Condense brain analysis by ~50%, move details to supplementary
3. Add partial correlation analysis controlling for k_n
4. Add 10–15 references (JS divergence, Ka/Ks foundational, FDR method)
5. Fix line spacing to 1.0
6. Remove subjective language

---

### Rank 2: Bioinformatics

| Attribute | Value |
|-----------|-------|
| **Journal** | Bioinformatics |
| **Publisher** | Oxford University Press |
| **IF (2025)** | ~5.8 |
| **Fit score** | 8.0 / 10 |
| **Estimated acceptance probability** | 40–50% (after revisions) |
| **Review timeline** | 6–10 weeks |

**Rationale**: Bioinformatics is the natural home for computational methods in biology. The journal prioritizes methodological novelty and rigorous validation over biological discovery. CKI's clear methodological contribution (decomposing JS divergence into baseline and functional components) and extensive benchmarking (parameter sweep, method comparison, calibration) are exactly what Bioinformatics reviewers look for. The brain analysis biological interpretations would need to be drastically condensed or moved to supplementary — Bioinformatics reviewers prefer concise method descriptions over extensive biological applications. The lower IF is the main drawback.

**Advantages over NAR**: Higher acceptance probability; reviewers more focused on methodological soundness than biological novelty; shorter review cycle; does not require the brain analysis to be extensive.

**Disadvantages**: Significantly lower IF (5.8 vs 16.6); less prestige for career advancement; may be viewed as "too easy" given CKI's ambition.

---

### Rank 3: Genome Biology

| Attribute | Value |
|-----------|-------|
| **Journal** | Genome Biology |
| **Publisher** | BMC / Springer Nature |
| **IF (2025)** | ~12.3 |
| **Fit score** | 6.5 / 10 |
| **Estimated acceptance probability** | 15–25% |
| **Review timeline** | 12–16 weeks |

**Rationale**: Genome Biology publishes high-impact computational and experimental genomics research. CKI's multi-dataset validation and biological applications (cancer, brain) fit the journal's scope. The journal has previously published CKI-adjacent work (Scanpy, ref 25). However, the v17 review notes that CKI was previously submitted to Genome Biology (v16) and received Major Revision. Resubmitting would likely encounter the same reviewers, who may have higher expectations for the revised version. The FDR issue and partial correlation analysis are likely to be raised again.

**Advantages over NAR**: Higher biological impact emphasis; open access; broader genomics readership.

**Disadvantages**: Previous rejection history; long review cycle; requires more experimental validation than NAR; FDR and statistical rigor demands are high.

---

### Rank 4: Briefings in Bioinformatics

| Attribute | Value |
|-----------|-------|
| **Journal** | Briefings in Bioinformatics |
| **Publisher** | Oxford University Press |
| **IF (2025)** | ~9.5 |
| **Fit score** | 6.0 / 10 |
| **Estimated acceptance probability** | 20–30% (if reframed as methods review) |
| **Review timeline** | 8–12 weeks |

**Rationale**: Briefings in Bioinformatics publishes methodological reviews and novel computational methods with broad applicability. CKI could be framed as a new framework for transcriptomic comparison with a more tutorial-like presentation. However, the current manuscript is structured as a primary research article, not a review/methods guide, and would require significant restructuring. The journal's readership expects more methodological context and comparison with existing approaches than the current manuscript provides.

**Advantages**: OUP (same publisher as NAR, familiar submission system); good IF; less stringent statistical requirements than NAR.

**Disadvantages**: Requires restructuring to methods-review format; less appropriate for primary research findings; brain analysis would still need condensing.

---

### Rank 5: PLOS Computational Biology

| Attribute | Value |
|-----------|-------|
| **Journal** | PLOS Computational Biology |
| **Publisher** | PLOS |
| **IF (2025)** | ~3.5 |
| **Fit score** | 7.0 / 10 |
| **Estimated acceptance probability** | 35–45% (after revisions) |
| **Review timeline** | 8–14 weeks |

**Rationale**: PLOS Comp Biol is a natural home for computational biology methods with biological applications. The journal values methodological rigor and open science. CKI's open-source package, multi-dataset validation, and honest limitations section align well with PLOS values. However, the journal has extremely high standards for statistical rigor — the FDR issue would be a major barrier. The low IF is a significant drawback for the authors' career goals.

**Advantages**: High acceptance probability; values open science; no strict word limit; welcomes computational methods with biological applications.

**Disadvantages**: Low IF (3.5); very demanding statistical review; less prestige than NAR; publication fees.

---

## 12. Recommendations for Improvement

### Priority 1: Must-fix before any submission

1. **Apply FDR correction to brain analysis**: Use Benjamini-Hochberg on the 31,764 residual values, or establish a permutation-based null for the multiplicative residual model. Report q-values alongside raw P-values. This is the single most important remaining issue.

2. **Conduct partial correlation analysis**: Compute partial Spearman correlations between CKI ω and each standard metric, controlling for k_n. This addresses the spurious ratio correlation concern (M3) and strengthens the "orthogonal information dimension" claim.

3. **Fix line spacing**: Change `line_spacing = 1.15` to `line_spacing = 1.0` in the manuscript generator (line 72) to meet NAR's single-spacing requirement.

4. **Verify Figure 5 legend**: The legend says "between human and mouse" but the analysis is within Tabula Sapiens (human only). Fix to "within Tabula Sapiens (human)".

### Priority 2: Strongly recommended

5. **Condense brain analysis by ~50%**: Move the cell-type-specific biological interpretations (OPCs, oligodendrocytes, astrocytes, Bergmann glia, microglia, vascular cells, fibroblast sub-sections) to supplementary materials. Keep only the gradient overview and the multiplicative residual model description in the main text.

6. **Split Statistical reporting paragraph**: Break the ~400-word paragraph (line 395) into 2–3 shorter paragraphs: (a) bootstrap test description, (b) P-value anchor justification, (c) effect size and omnibus test conventions.

7. **Add 10–15 references**: Include foundational references for JS divergence (Lin 1991), Ka/Ks (Kimura 1977), BH FDR (Benjamini & Hochberg 1995), softmax normalization, and recent cell-type comparison tools.

8. **Remove or de-emphasize TCGA paired analysis**: Given n = 2–5 per cancer type, remove the P-value reporting or explicitly label as "exploratory, not powered for statistical inference."

9. **Add data access dates**: For each dataset, add "accessed YYYY-MM-DD" in the Data availability section.

10. **Remove subjective language**: Replace "striking," "critically," "most striking" with neutral phrasing.

### Priority 3: Minor improvements

11. **Expand abbreviations at first use**: HVG, OPC, and other abbreviations should be fully expanded at first use in the main text.

12. **Consider adding a Dockerfile or conda environment.yml**: This would further strengthen reproducibility.

13. **Add a master pipeline script**: A `run_all.sh` or `Makefile` that executes all analyses in order would improve reproducibility.

14. **Verify reference numbering continuity**: Ensure no gaps in in-text citation numbering.

15. **Consider adding a Graphical Abstract figure**: The current manuscript has a placeholder. NAR requires a graphical abstract for accepted articles, and having one ready at submission strengthens the package.

---

## Summary Assessment

The v18 manuscript represents a significant improvement over v17, with 6 of 8 Critical issues resolved. The remaining Critical issue (FDR correction) and the Major issues (brain analysis length, partial correlation, TCGA paired analysis) are addressable within a reasonable revision cycle. The manuscript is well-written, the conceptual framework is novel and compelling, and the multi-dataset validation is thorough.

**Recommended journal**: NAR remains the best target, contingent on fixing the FDR issue and condensing the brain analysis. Bioinformatics is the strongest backup with higher acceptance probability but lower IF. The manuscript is approximately **70% ready** for NAR submission, with 2–3 weeks of focused revision needed to reach submission-ready status.

**Estimated timeline to submission-ready**: 2–3 weeks of focused work (FDR analysis, partial correlations, brain section condensation, reference expansion, formatting fixes).
