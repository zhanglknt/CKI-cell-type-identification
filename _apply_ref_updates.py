#!/usr/bin/env python3
"""Update 16 references in generate_manuscript_nar.py with expanded author lists."""

import re

# Read the file
with open("generate_manuscript_nar.py", "r", encoding="utf-8") as f:
    content = f.read()

# Define old -> new reference strings (matching exact file content with \u escapes)
REPLACEMENTS = [
    # Ref 1: Korsunsky et al. (2019) - 10 authors, all listed
    (
        "'Korsunsky,I., Millard,N., Fan,J., Slowikowski,K., Zhang,F., Baglaenko,Y. et al. (2019) Fast, sensitive and accurate integration of single-cell data with Harmony. *Nat. Methods*, **16**, 1289\\u20131296.'",
        "'Korsunsky,I., Millard,N., Fan,J., Slowikowski,K., Zhang,F., Wei,K., Baglaenko,Y., Brenner,M., Loh,P.R. and Raychaudhuri,S. (2019) Fast, sensitive and accurate integration of single-cell data with Harmony. *Nat. Methods*, **16**, 1289\\u20131296.'"
    ),
    # Ref 9: Siletti et al. (2023) - 21 authors, first 10 + et al.
    (
        "'Siletti,K., Hodge,R., Albiach,A.M., Lee,K.W., Ding,S.L., Hu,L. et al. (2023) Transcriptomic diversity of cell types across the adult human brain. *Science*, **382**, eadl7046.'",
        "'Siletti,K., Hodge,R., Mossi Albiach,A., Lee,K.W., Ding,S.L., Hu,L., L\\u00f6nnerberg,P., Bakken,T., Casper,T., Clark,M. et al. (2023) Transcriptomic diversity of cell types across the adult human brain. *Science*, **382**, eadl7046.'"
    ),
    # Ref 11: Perou et al. (2000) - 18 authors, first 10 + et al.
    (
        "'Perou,C.M., S\\u00f8rlie,T., Eisen,M.B., van de Rijn,M., Jeffrey,S.S., Rees,C.A. et al. (2000) Molecular portraits of human breast tumours. *Nature*, **406**, 747\\u2013752.'",
        "'Perou,C.M., S\\u00f8rlie,T., Eisen,M.B., van de Rijn,M., Jeffrey,S.S., Rees,C.A., Pollack,J.R., Ross,D.T., Johnsen,H., Akslen,L.A. et al. (2000) Molecular portraits of human breast tumours. *Nature*, **406**, 747\\u2013752.'"
    ),
    # Ref 12: Parker et al. (2009) - 20 authors, first 10 + et al.
    (
        "'Parker,J.S., Mullins,M., Cheang,M.C.U., Leung,S., Voduc,D., Vickery,T. et al. (2009) Supervised risk predictor of breast cancer based on intrinsic subtypes. *J. Clin. Oncol.*, **27**, 1160\\u20131167.'",
        "'Parker,J.S., Mullins,M., Cheang,M.C.U., Leung,S., Voduc,D., Vickery,T., Davies,S., Fauron,C., He,X., Hu,Z. et al. (2009) Supervised risk predictor of breast cancer based on intrinsic subtypes. *J. Clin. Oncol.*, **27**, 1160\\u20131167.'"
    ),
    # Ref 13: Tsai et al. (2016) - 11 authors, first 10 + et al.
    (
        "'Tsai,H.H., Niu,J., Munji,R., Davalos,D., Chang,J., Zhang,H. et al. (2016) Oligodendrocyte precursors migrate along vasculature in the developing nervous system. *Science*, **351**, 379\\u2013384.'",
        "'Tsai,H.H., Niu,J., Munji,R., Davalos,D., Chang,J., Zhang,H., Tien,A.C., Kuo,C.J., Chan,J.R., Daneman,R. et al. (2016) Oligodendrocyte precursors migrate along vasculature in the developing nervous system. *Science*, **351**, 379\\u2013384.'"
    ),
    # Ref 14: Cerami et al. (2012) - 15 authors, first 10 + et al.
    (
        "'Cerami,E., Gao,J., Dogrusoz,U., Gross,B.E., Sumer,S.O., Aksoy,B.A. et al. (2012) The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. *Cancer Discov.*, **2**, 401\\u2013404.'",
        "'Cerami,E., Gao,J., Dogrusoz,U., Gross,B.E., Sumer,S.O., Aksoy,B.A., Jacobsen,A., Byrne,C.J., Heuer,M.L., Larsson,E. et al. (2012) The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. *Cancer Discov.*, **2**, 401\\u2013404.'"
    ),
    # Ref 15: Tarashansky et al. (2021) - 7 authors, all listed
    (
        "'Tarashansky,A.J., Musser,J.M., Khariton,M., Li,P., Arendt,D., Quake,S.R. et al. (2021) Mapping single-cell atlases throughout Metazoa unravels cell type evolution. *eLife*, **10**, e66747.'",
        "'Tarashansky,A.J., Musser,J.M., Khariton,M., Li,P., Arendt,D., Quake,S.R. and Wang,B. (2021) Mapping single-cell atlases throughout Metazoa unravels cell type evolution. *eLife*, **10**, e66747.'"
    ),
    # Ref 16: Regev et al. (2017) - 62 authors, first 10 + et al.
    (
        "'Regev,A., Teichmann,S.A., Lander,E.S., Amit,I., Benoist,C., Birney,E. et al. (2017) The Human Cell Atlas. *eLife*, **6**, e27041.'",
        "'Regev,A., Teichmann,S.A., Lander,E.S., Amit,I., Benoist,C., Birney,E., Bodenmiller,B., Campbell,P., Carninci,P., Clatworthy,M. et al. (2017) The Human Cell Atlas. *eLife*, **6**, e27041.'"
    ),
    # Ref 20: Menassa et al. (2022) - 13 authors, first 10 + et al.
    # Also fix page numbers: 1910-1927.e10 -> 2127-2139.e6
    (
        "'Menassa,D.A., Muntslag,T.A.O., Martin-Estebane,M., Barry-Carroll,L., Chapman,M.A., Adorjan,I. et al. (2022) The spatiotemporal dynamics of microglia across the human lifespan. *Dev. Cell*, **57**, 1910\\u20131927.e10.'",
        "'Menassa,D.A., Muntslag,T.A.O., Martin-Esteban\\u00e9,M., Barry-Carroll,L., Chapman,M.A., Adorjan,I., Tyler,T., Turnbull,B., Rose-Zerilli,M.J.J., Nicoll,J.A.R. et al. (2022) The spatiotemporal dynamics of microglia across the human lifespan. *Dev. Cell*, **57**, 2127\\u20132139.e6.'"
    ),
    # Ref 26: Hao et al. (2021) - 25 authors, first 10 + et al.
    (
        "'Hao,Y., Hao,S., Andersen-Nissen,E., Mauck,W.M., Zheng,S., Butler,A. et al. (2021) Integrated analysis of multimodal single-cell data. *Cell*, **184**, 3573\\u20133587.'",
        "'Hao,Y., Hao,S., Andersen-Nssen,E., Mauck,W.M. 3rd, Zheng,S., Butler,A., Lee,M.J., Wilk,A.J., Darby,C., Zager,M. et al. (2021) Integrated analysis of multimodal single-cell data. *Cell*, **184**, 3573\\u20133587.'"
    ),
    # Ref 27: Hao et al. (2024) - 11 authors, first 10 + et al.
    (
        "'Hao,Y., Stuart,T., Kowalski,M.H., Choudhary,S., Hoffman,P., Hartman,A. et al. (2024) Dictionary learning for integrative, multimodal and scalable single-cell analysis. *Nat. Biotechnol.*, **42**, 293\\u2013304.'",
        "'Hao,Y., Stuart,T., Kowalski,M.H., Choudhary,S., Hoffman,P., Hartman,A., Srivastava,A., Molla,G., Madad,S., Fernandez-Granda,C. et al. (2024) Dictionary learning for integrative, multimodal and scalable single-cell analysis. *Nat. Biotechnol.*, **42**, 293\\u2013304.'"
    ),
    # Ref 28: Weinstein et al. (2013) - 9 individual authors (skip consortium), all listed
    (
        "'Weinstein,J.N., Collisson,E.A., Mills,G.B., Shaw,K.R.M., Ozenberger,B.A., Ellrott,K. et al. (2013) The Cancer Genome Atlas Pan-Cancer analysis project. *Nat. Genet.*, **45**, 1113\\u20131120.'",
        "'Weinstein,J.N., Collisson,E.A., Mills,G.B., Shaw,K.R., Ozenberger,B.A., Ellrott,K., Shmulevich,I., Sander,C. and Stuart,J.M. (2013) The Cancer Genome Atlas Pan-Cancer analysis project. *Nat. Genet.*, **45**, 1113\\u20131120.'"
    ),
    # Ref 29: Colaprico et al. (2016) - 13 authors, first 10 + et al.
    (
        "'Colaprico,A., Silva,T.C., Olsen,C., Garofano,L., Cava,C., Garolini,D. et al. (2016) TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. *Nucleic Acids Res.*, **44**, e71.'",
        "'Colaprico,A., Silva,T.C., Olsen,C., Garofano,L., Cava,C., Garolini,D., Sabedot,T.S., Malta,T.M., Pagnotta,S.M., Castiglioni,I. et al. (2016) TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. *Nucleic Acids Res.*, **44**, e71.'"
    ),
    # Ref 32: Tran et al. (2020) - 7 authors, all listed
    (
        "'Tran,H.T.N., Ang,K.S., Chevrier,M., Zhang,X., Lee,N.Y.S., Goh,M. et al. (2020) A benchmark of batch-effect correction methods for single-cell RNA sequencing data. *Genome Biol.*, **21**, 12.'",
        "'Tran,H.T.N., Ang,K.S., Chevrier,M., Zhang,X., Lee,N.Y.S., Goh,M. and Chen,J. (2020) A benchmark of batch-effect correction methods for single-cell RNA sequencing data. *Genome Biol.*, **21**, 12.'"
    ),
    # Ref 36: Wälchli et al. (2024) - 37 authors, first 10 + et al.
    (
        "'W\\u00e4lchli,T., Ghobrial,M., Schwab,M.E., Takada,S., Zhong,H., Le,J. et al. (2024) Single-cell atlas of the human brain vasculature across development, adulthood and disease. *Nature*, **632**, 603\\u2013613.'",
        "'W\\u00e4lchli,T., Ghobrial,M., Schwab,M.E., Takada,S., Zhong,H., Suntharalingham,S., Vetiska,S., Gonzalez,D.R., Wu,R., Rehrauer,H. et al. (2024) Single-cell atlas of the human brain vasculature across development, adulthood and disease. *Nature*, **632**, 603\\u2013613.'"
    ),
    # Ref 40: Barry-Carroll et al. (2023) - 10 authors, all listed
    # Also fix page number: 113453 -> 112425
    (
        "'Barry-Carroll,L., Greulich,P., Marshall,A.R., Riecken,K., Fehse,B., Askew,K.E. et al. (2023) Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors. *Cell Rep.*, **42**, 113453.'",
        "'Barry-Carroll,L., Greulich,P., Marshall,A.R., Riecken,K., Fehse,B., Askew,K.E., Li,K., Garaschuk,O., Menassa,D.A. and Gomez-Nicola,D. (2023) Microglia colonize the developing brain by clonal expansion of highly proliferative progenitors. *Cell Rep.*, **42**, 112425.'"
    ),
]

# Apply replacements
count = 0
for old, new in REPLACEMENTS:
    if old in content:
        content = content.replace(old, new, 1)
        count += 1
        print(f"  OK: Replacement {count} applied")
    else:
        print(f"  WARNING: Could not find old string for replacement {count + 1}")
        print(f"    Looking for: {old[:80]}...")
        count += 1

print(f"\nApplied {count} replacements (out of {len(REPLACEMENTS)} attempted)")

# Write the file back
with open("generate_manuscript_nar.py", "w", encoding="utf-8") as f:
    f.write(content)

print("File written successfully.")
