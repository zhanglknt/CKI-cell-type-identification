# -*- coding: utf-8 -*-
"""Final v49 CL paragraphs (v3 tight) — target <=530 words."""

P = {}

P['salut'] = "Dear Editors,"

P['p1'] = (
    "On behalf of my co-author, Dr. Xianming Wu (Chinese Institute for Brain "
    "Research, Beijing), I submit our manuscript, "
    "\u201cCKI is a Ka/Ks-inspired index quantifying functional divergence "
    "in single-cell genomics\u201d, for consideration as an Article in "
    "Nature Communications. CKI (Cell-type Ka/Ks-inspired Index) is, to our "
    "knowledge, the first framework to separate functional divergence from "
    "background drift in transcriptomic comparisons: adapting the Ka/Ks "
    "ratio\u2019s logic, it decomposes divergence into a housekeeping "
    "baseline k_n and an identity-gene rate k_f (\u03c9 = k_f/k_n). The "
    "work fits Nature Communications\u2019 scope of computational methods "
    "validated on large-scale real data."
)

P['p2'] = (
    "The manuscript rests on three pillars. First, in ground-truth "
    "simulation (1,750 replicates), \u03c9 alone did not false-trigger on "
    "neutral housekeeping drift (false-positive rate 0.00 versus "
    "0.55\u20130.58 for JS and cosine) and ranked first for "
    "functional-versus-neutral discrimination (AUC = 0.80). Second, in real-"
    "data drift calibration, \u03c9 misreported none of 30 cross-lane "
    "technical-replicate pairs (Kang IFN-\u03b2 PBMC data; raw JS 36.7%, "
    "cosine 23.3%) and, on 2,161 brain technical-drift pairs, misreported "
    "least of seven metrics (28.6% versus 44\u201345%, lowest in all ten "
    "cell classes), with the shallowest drift-ladder gradient (1.04 \u2192 "
    "1.76 \u2192 1.80 versus 1.07 \u2192 3.32 \u2192 2.98 for raw JS). "
    "Third, across 3,596 TCGA samples in five cancer types, tumor specimens "
    "were consistently less divergent than adjacent non-tumor tissue (NN/TT "
    "\u03c9 ratio 1.13\u20132.46, cluster-bootstrap CIs excluding 1 in four "
    "of five)\u2014an effect of a 2.1\u20133.6-fold elevated housekeeping "
    "baseline, not reduced functional divergence; and in lung adenocarcinoma "
    "the k_f/k_n decomposition separates KRAS-mutant tumors (functional "
    "component, P = 7.8 \u00d7 10\u207b\u2077) from EGFR-mutant tumors "
    "(baseline-driven)."
)

P['p3'] = (
    "Previously raised concerns that (i) the index does not outperform "
    "existing metrics and (ii) the work may hold limited interest for a "
    "broad biological readership have been addressed directly. On (i): the "
    "classification benchmark (AUC = 0.680, 5th of 5) is by design\u2014CKI "
    "trades global-identity sensitivity for identity-gene divergence, and "
    "classification is outside its question domain; on the appropriate "
    "benchmark, misreporting control, \u03c9 misreports technical and donor "
    "drift least among all compared metrics while retaining sensitivity to "
    "biology. On (ii): the pan-cancer divergence map and the LUAD "
    "driver-class decomposition give the work direct cancer-biology "
    "relevance, and the drift-ladder calibration speaks to anyone who has "
    "seen batch effects masquerade as biology."
)

P['p4'] = (
    "We are explicit about limits: the 6.10-fold class-level brain gradient "
    "is predominantly a k_n effect (3.2-fold versus 2.0-fold k_f), no "
    "per-pair candidate survives false-discovery-rate correction (minimum "
    "q = 0.520), and the TCGA findings are framed as tissue-level "
    "functional divergence at bulk resolution with composition and "
    "probability-mapping controls."
)

P['p5'] = (
    "Both authors declare no competing interests. The work is original, not "
    "under consideration elsewhere, and not previously submitted to Nature "
    "Communications. AI tools were used for debugging, code review, and "
    "language editing; all AI-assisted content was reviewed and revised by "
    "the authors, who take full responsibility. This work was supported by "
    "the National Natural Science Foundation of China (grant 32370682). The "
    "CKI Python package (v0.5.0, MIT License) and all analysis code are "
    "available at https://github.com/zhanglknt/CKI-cell-type-identification "
    "(Zenodo DOI 10.5281/zenodo.22735744)."
)

P['p6'] = (
    "We suggest the following reviewers, none with recent collaborations "
    "or conflicts of interest with the authors: "
    "Prof. Fabian Theis, Helmholtz Munich (fabian.theis@helmholtz-munich.de); "
    "Prof. Joshua Welch, University of Michigan (welchjd@umich.edu); "
    "Prof. Sten Linnarsson, Karolinska Institutet (sten.linnarsson@ki.se); "
    "Prof. Patrik St\u00e5hl, KTH / SciLifeLab (patrik.stahl@scilifelab.se); "
    "Dr. Alejandro A. Sch\u00e4ffer, National Cancer Institute, NIH "
    "(schaffer@ncbi.nlm.nih.gov); and Prof. Zemin Zhang, Peking University "
    "(zeminzhang@pku.edu.cn)."
)

P['thanks'] = "Thank you for considering our work."
P['close1'] = "Sincerely,"
P['close2'] = "Li Zhang (Corresponding Author)"
P['close3'] = "Xianming Wu (First Author)"

total = 0
for k, v in P.items():
    n = len(v.split())
    total += n
    print('%-8s %3d' % (k, n))
print('TOTAL: %d' % total)
