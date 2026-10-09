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
        "On behalf of my co-authors, Wenting Liu and Jian Zu (School of "
        "Mathematics and Statistics, Xi'an Jiaotong University), I submit our "
        "manuscript, "
        "\u201cCKI: a Ka/Ks-inspired index decomposing functional divergence "
        "from baseline variation in cell atlases\u201d, for consideration as an Article in "
        "Nature Communications. CKI (Cell-type Ka/Ks-inspired Index) is, to "
        "our knowledge, the first per-comparison, design-testable "
        "implementation of a principled separation of functional divergence "
        "from background drift: adapting the "
        "Ka/Ks ratio\u2019s logic, it decomposes divergence into a "
        "housekeeping baseline k_n and an identity-gene rate k_f "
        "(\u03c9 = k_f/k_n). The work fits Nature Communications\u2019 scope "
        "of computational methods validated on large-scale real data.",
        doc,
    )

    # ── Body: core argument — four pillars (v59: brain-atlas pillar added) ──
    add_para(
        "The manuscript rests on four pillars. First, in ground-truth "
        "simulation (1,750 replicates per background, two backgrounds), \u03c9 alone did not false-trigger on "
        "neutral housekeeping drift (false-positive rate 0.00 versus "
        "0.55\u20130.58 for JS and cosine) and gave the best "
        "functional-versus-neutral discrimination at bounded power (AUC = 0.80). Second, in "
        "real-data drift calibration, \u03c9 raised no false reports on the 30 "
        "cross-lane technical-replicate pairs (Kang IFN-\u03b2 PBMC data; "
        "raw JS 36.7%, cosine 23.3%) and, on 2,161 brain technical-drift "
        "pairs, had the lowest false-report rate among the continuous "
        "divergence metrics (28.6% versus 35.7\u201345.2% for the other "
        "five; below raw JS in all ten cell classes), with the shallowest "
        "drift-ladder gradient (1.04 \u2192 1.76 \u2192 1.80 versus "
        "1.07 \u2192 3.32 \u2192 2.98 for raw JS). Third, across 3,535 TCGA "
        "samples in five cancer types, tumors appear consistently less "
        "divergent than adjacent non-tumor tissue\u2014a pan-cancer "
        "reversal driven by an elevated housekeeping baseline rather "
        "than reduced functional divergence; and in lung adenocarcinoma "
        "the k_f/k_n "
        "decomposition separates KRAS-mutant tumors\u2014retaining both a "
        "functional (k_f) and a baseline (k_n) component after purity and "
        "smoking adjustment\u2014from EGFR-mutant tumors, whose apparent "
        "association dissolved under purity adjustment. A GTEx healthy "
        "reference further shows adjacent-normal k_n at healthy-tissue levels "
        "in lung, liver, and breast, arguing against a field-effect reading "
        "of the pan-cancer reversal. Fourth, in a human brain atlas "
        "spanning 108 regions (non-neuronal nuclei), CKI quantified a "
        "regional differentiation gradient, largely k_n-driven, and "
        "provides a statistically calibrated framework for atlas-scale "
        "hypothesis generation; extending into neuronal superclasses, "
        "divergence far exceeds the non-neuronal median "
        "(P < 10\u207b\u00b3\u2070\u2070).",
        doc,
    )

    # ── Body: two properties stated explicitly (new-evidence framing) ──
    add_para(
        "Two properties of this work are worth stating explicitly. CKI is "
        "a specificity-first index, designed to detect dynamic cell-state "
        "changes rather than to discriminate static cell types: on the "
        "benchmark matched to its question domain\u2014false divergence "
        "calls on real technical and donor drift\u2014it misreports least "
        "among the continuous divergence metrics while retaining "
        "sensitivity to biology (Fig. 3); in the ground-truth simulation "
        "it ranks first of six metrics at separating injected functional "
        "change from neutral drift (AUC = 0.80; Fig. 2e). And the "
        "pan-cancer divergence map, with the "
        "lung adenocarcinoma driver-class decomposition, grounds the "
        "method in cancer biology of direct interest to a broad "
        "readership (Fig. 4).",
        doc,
    )

    # ── Body: suggested reviewers ──
    add_para(
        "We suggest the following reviewers, none with recent collaborations "
        "or conflicts of interest with the authors: "
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
