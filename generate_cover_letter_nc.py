"""
Generate Nature Communications Cover Letter (v49 repositioning)
CKI Project — Nature Communications submission (Article)

v49 changes (d-tcga, 2026-09-18):
  * Value proposition rewritten: from "a better metric" to the first
    principled separation of functional divergence from background drift
    (Ka/Ks analogy), with real-data misreporting-control evidence and a
    discovery-level pan-cancer application.
  * Reviewer-concern paragraph replaced with a new-evidence framing ("Two
    properties of this work are worth stating explicitly..."), per blind
    review R4 P0-3/P1-1: no rebuttal voice, no "5th of 5".
  * Misreporting claim qualified to the continuous divergence metrics
    (marker Jaccard is lower still on the FPR statistic), per R1 P1-1.
  * Preserved: NC scope, six suggested reviewers, Zenodo DOI, one-page
    format (Arial 11 pt, 1" margins, ~520 words).
Numbers sourced from verified audits only:
  nc49_pilot_kang_2026-09-18.md (Kang 30 pairs: omega 0/30 vs raw JS 36.7%,
  cosine 23.3%), nc49_brain_ladder_2026-09-18.md (T1 2,161 pairs: omega FPR
  28.6% lowest among continuous metrics, below raw JS 10/10 classes; ladder
  1.04->1.76->1.80 vs raw JS 1.07->3.32->2.98),
  nc52_tcga_excc_main_2026-09-24.md (3,535 ex-CC samples; NN/TT
  1.11-2.46, 4/5 CIs exclude 1; k_n 1.3-3.3x; LUAD KRAS retained after
  purity + smoking adjustment, EGFR association dissolved under purity
  adjustment per nc49_purity/nc49_smoking audits),
  simulation change-detection results (FPR 0.00 vs 0.55-0.58; AUC 0.80
  rank 1/6, skin replication 0.91).

v59 changes (nc59, 2026-10-02):
  * Pillar 3 TCGA wording aligned to the revised abstract: range numbers
    (NN/TT ratio, k_n fold) dropped from the letter body; phrasing now
    "tumors appear consistently less divergent ... driven by an elevated
    housekeeping baseline rather than reduced functional divergence".
  * Fourth pillar added: human brain atlas (108 regions) regional
    differentiation gradient + statistically calibrated framework,
    mirroring the revised abstract's closing point.
"""
from pathlib import Path
from docx.shared import Pt, Inches

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR.mkdir(exist_ok=True)


def add_para(text, doc, space_after=4, align=None, bold=False, size=None):
    """Add a paragraph with controlled spacing — no empty-paragraph spacers."""
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = 1.05
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.space_before = Pt(0)
    run = para.add_run(text)
    if bold:
        run.bold = True
    if size:
        run.font.size = Pt(size)
    if align is not None:
        para.alignment = align
    return para


def run():
    from docx import Document

    doc = Document()

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # ── Salutation (letter begins directly at "Dear Editors") ──
    add_para("Dear Editors,", doc, space_after=6)

    # ── Body: opening + NC scope + repositioned value proposition ──
    add_para(
        "On behalf of my co-authors, Wenting Liu and Jian Zu (Xi'an "
        "Jiaotong University), I submit our "
        "manuscript, "
        "\u201cCKI: a Ka/Ks-inspired index decomposing functional divergence "
        "from baseline variation in cell atlases\u201d, for consideration as an Article in "
        "Nature Communications. CKI (Cell-type Ka/Ks-inspired Index) provides a "
        "per-comparison, design-testable "
        "separation of functional divergence "
        "from background drift: it decomposes divergence into a "
        "housekeeping baseline k_n and an identity-gene rate k_f "
        "(\u03c9 = k_f/k_n). The work fits Nature Communications\u2019 scope: "
        "computational methods validated on large-scale real data.",
        doc,
    )

    # ── Body: core argument — four pillars (v59: brain-atlas pillar added) ──
    add_para(
        "The manuscript rests on four pillars. First, in ground-truth "
        "simulation (1,750 replicates per background, two backgrounds), \u03c9 alone did not false-trigger on "
        "neutral housekeeping drift (false-positive rate 0.00 versus "
        "0.55\u20130.58 for JS and cosine) and gave the best "
        "functional-versus-neutral discrimination at bounded power (AUC = 0.80). Second, in "
        "drift calibration, \u03c9 raised no false reports on the 30 "
        "cross-lane technical-replicate pairs (Kang IFN-\u03b2 PBMC; "
        "raw JS 36.7%, cosine 23.3%); on 2,161 brain technical-drift "
        "pairs the permutation rule fires on 28.6% of \u03c9 "
        "comparisons, a library-effect sensitivity statistic, not an "
        "error rate (11.4% within batch, 10.3% strictly "
        "matched, 4.8% under a library-aware null), and on those "
        "replicates \u03c9 shows the tightest dispersion of the seven "
        "metrics (log-scale MAD 0.113 vs 0.267\u20130.586). Third, across 3,535 TCGA "
        "samples in five cancer types, tumors appear consistently less "
        "divergent than adjacent non-tumor tissue\u2014a pan-cancer "
        "reversal driven by an elevated housekeeping baseline rather "
        "than reduced functional divergence, about half of which is "
        "attributable to copy-number instability (56%, 95% CI "
        "46\u201366%), a caution for HK-anchored "
        "normalization in bulk tumors; and in lung adenocarcinoma "
        "CKI "
        "separates KRAS-mutant from wild-type group means after purity and "
        "smoking adjustment\u2014a group-level contrast only (fixed-panel "
        "sensitivity P = 0.089; the apparent EGFR elevation "
        "dissolves under purity adjustment). A GTEx healthy "
        "reference places adjacent-normal k_n below tumour k_n "
        "in lung, liver and breast (kidney excepted; descriptive): a "
        "field effect of the tested size is tentatively excluded, but larger shifts "
        "are not resolved. Fourth, in a human brain atlas "
        "spanning 108 regions (non-neuronal nuclei), CKI quantified a "
        "regional gradient (6.10-fold upper bound, 3.66-fold matched), k_n-dominated, and a "
        "framework for atlas-scale "
        "hypothesis generation; neuronal-superclass "
        "divergence far exceeds the non-neuronal median "
        "(block-shuffle P = 0.001, 0.014, 0.163).",
        doc,
    )

    # ── Body: two properties stated explicitly (new-evidence framing) ──
    add_para(
        "Two properties of this work are worth stating explicitly. CKI is "
        "a specificity-first index, designed to detect dynamic cell-state "
        "changes rather than discriminate static cell types: on "
        "real-drift benchmarks it misreports least "
        "among continuous metrics while retaining "
        "sensitivity (Fig. 2); in the ground-truth simulation "
        "it ranks first of six at separating functional "
        "change from neutral drift (AUC = 0.80; Fig. 2d). And the "
        "pan-cancer divergence map, with the "
        "lung adenocarcinoma driver-class decomposition, grounds the "
        "method in cancer biology (Fig. 3). The ratio "
        "is theory-backed: a scoped framework identifies \u03c9 \u2212 1 "
        "with functional-to-background displacement energy; the HK "
        "denominator studentizes the null eightfold "
        "(Supplementary Note 20).",
        doc,
    )

    # ── Body: suggested reviewers ──
    add_para(
        "We suggest the following reviewers, none with conflicts: "
        "Prof. Fabian Theis, Helmholtz Munich (fabian.theis@helmholtz-munich.de); "
        "Prof. Joshua Welch, University of Michigan (welchjd@umich.edu); "
        "Prof. Sten Linnarsson, Karolinska Institutet (sten.linnarsson@ki.se); "
        "Prof. Patrik St\u00e5hl, KTH / SciLifeLab (patrik.stahl@scilifelab.se); "
        "Dr. Alejandro A. Sch\u00e4ffer, National Cancer Institute, NIH "
        "(schaffer@ncbi.nlm.nih.gov); and Prof. Zemin Zhang, Peking University "
        "(zeminzhang@pku.edu.cn).",
        doc,
    )

    add_para(
        "Thank you for considering our work.",
        doc,
    )

    # ── Closing ──
    add_para("Sincerely,", doc, space_after=12)
    add_para("Li Zhang (Corresponding Author)", doc, space_after=0)

    # Save
    out = str(OUTPUT_DIR / "CKI_NC_Cover_Letter.docx")
    doc.save(out)
    print(f"Saved: {out}")
    return out


if __name__ == "__main__":
    run()
