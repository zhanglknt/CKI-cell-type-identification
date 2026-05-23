"""
Fix references: delete 6 PubMed-unfindable refs, add 3 replacements, renumber to 36.
Maps: 15→delete, 16→delete, 17→15(Storey), 26→24(CZI), 29→delete, 35→32(Yang)
"""
import re

with open('generate_manuscript_v4_nar.py', 'r') as f:
    content = f.read()

# ============================================================
# STEP 1: Replace the entire refs block (from "# refs" comment through the list)
# ============================================================

old_refs_start = content.find("refs = [")
old_refs_end = content.find("for ref in refs:")

new_refs_block = """refs = [
    # 1. Regev 2017 eLife — Human Cell Atlas
    '1. Regev,A., Teichmann,S.A., Lander,E.S., Amit,I., Benoist,C., Birney,E., Bodenmiller,B., Campbell,P., Carninci,P., Clatworthy,M. et al. (2017) The Human Cell Atlas. eLife, 6, e27041.',
    # 2. Luecken 2019 Mol Syst Biol — scRNA-seq best practices
    '2. Luecken,M.D. and Theis,F.J. (2019) Current best practices in single-cell RNA-seq analysis: a tutorial. Mol. Syst. Biol., 15, e8746.',
    # 3. Nei & Gojobori 1986 — Ka/Ks method
    '3. Nei,M. and Gojobori,T. (1986) Simple methods for estimating the numbers of synonymous and nonsynonymous nucleotide substitutions. Mol. Biol. Evol., 3, 418–426.',
    # 4. Hounkpe 2021 NAR — HRT Atlas housekeeping genes
    '4. Hounkpe,B.W., Chenou,F., de Lima,F. and De Paula,E.V. (2021) HRT Atlas v1.0 database: redefining human and mouse housekeeping genes and candidate tissue transitions. Nucleic Acids Res., 49, D947–D955.',
    # 5. Tabula Muris Consortium 2018 Nature
    '5. Tabula Muris Consortium. (2018) Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris. Nature, 562, 367–372.',
    # 6. Tabula Sapiens Consortium 2022 Science
    '6. Tabula Sapiens Consortium. (2022) The Tabula Sapiens: a multiple-organ, single-cell transcriptomic atlas of humans. Science, 376, eabl4896.',
    # 7. TCGA LUAD 2014 Nature
    '7. Cancer Genome Atlas Research Network. (2014) Comprehensive molecular profiling of lung adenocarcinoma. Nature, 511, 543–550.',
    # 8. Weinstein 2013 Nat Genet — TCGA Pan-Cancer
    '8. Weinstein,J.N., Collisson,E.A., Mills,G.B., Shaw,K.R.M., Ozenberger,B.A., Ellrott,K., Shmulevich,I., Sander,C. and Stuart,J.M. (2013) The Cancer Genome Atlas Pan-Cancer analysis project. Nat. Genet., 45, 1113–1120.',
    # 9. TCGA BRCA 2012 Nature
    '9. Cancer Genome Atlas Network. (2012) Comprehensive molecular portraits of human breast tumours. Nature, 490, 61–70.',
    # 10. Siletti 2023 Science — human brain atlas
    '10. Siletti,K., Hodge,R., Mossi Albiach,A., Lee,K.W., Ding,S.L., Hu,L., Lönnerberg,P., Bakken,T., Casper,T., Clark,M. et al. (2023) Transcriptomic diversity of cell types across the adult human brain. Science, 382, eadd7046.',
    # 11. Tran 2020 Genome Biol — batch correction benchmark
    '11. Tran,H.T.N., Ang,K.S., Chevrier,M., Zhang,X., Lee,N.Y.S., Goh,M. and Chen,J. (2020) A benchmark of batch-effect correction methods for single-cell RNA sequencing data. Genome Biol., 21, 12.',
    # 12. Korsunsky 2019 Nat Methods — Harmony
    '12. Korsunsky,I., Millard,N., Fan,J., Slowikowski,K., Zhang,F., Wei,K., Baglaenko,Y., Brenner,M., Loh,P. and Raychaudhuri,S. (2019) Fast, sensitive and accurate integration of single-cell data with Harmony. Nat. Methods, 16, 1289–1296.',
    # 13. Lopez 2018 Nat Methods — scVI
    '13. Lopez,R., Regier,J., Cole,M.B., Jordan,M.I. and Yosef,N. (2018) Deep generative modeling for single-cell transcriptomics. Nat. Methods, 15, 1053–1058.',
    # 14. Rosen 2024 Nat Methods — SATURN
    '14. Rosen,Y., Brbić,M., Roohani,Y., Swanson,K., Li,Z. and Leskovec,J. (2024) Universal cell-type embeddings from single-cell atlases using protein language models. Nat. Methods, 21, 881–892.',
    # 15. Storey & Tibshirani 2003 PNAS — FDR in genomics (replaces Benjamini 1995)
    '15. Storey,J.D. and Tibshirani,R. (2003) Statistical significance for genomewide studies. Proc. Natl. Acad. Sci. USA, 100, 9440–9445.',
    # 16. Wolf 2018 Genome Biol — Scanpy
    '16. Wolf,F.A., Angerer,P. and Theis,F.J. (2018) SCANPY: large-scale single-cell gene expression data analysis. Genome Biol., 19, 15.',
    # 17. Edmondson & Steiner 1954 Cancer — Edmondson grade
    '17. Edmondson,H.A. and Steiner,P.E. (1954) Primary carcinoma of the liver: a study of 100 cases among 48,900 necropsies. Cancer, 7, 462–503.',
    # 18. Perou 2000 Nature — breast cancer molecular portraits
    '18. Perou,C.M., Sørlie,T., Eisen,M.B., van de Rijn,M., Jeffrey,S.S., Rees,C.A., Pollack,J.R., Ross,D.T., Johnsen,H., Akslen,L.A. et al. (2000) Molecular portraits of human breast tumours. Nature, 406, 747–752.',
    # 19. Parker 2009 JCO — PAM50
    '19. Parker,J.S., Mullins,M., Cheang,M.C.U., Leung,S., Voduc,D., Vickery,T., Davies,S., Fauron,C., He,X., Hu,Z. et al. (2009) Supervised risk predictor of breast cancer based on intrinsic subtypes. J. Clin. Oncol., 27, 1160–1167.',
    # 20. Yang 2007 MBE — PAML
    '20. Yang,Z. (2007) PAML 4: phylogenetic analysis by maximum likelihood. Mol. Biol. Evol., 24, 1586–1591.',
    # 21. Tarashansky 2021 eLife — SAMap
    '21. Tarashansky,A.J., Musser,J.M., Khariton,M., Li,P., Arendt,D., Quake,S.R. and Wang,B. (2021) Mapping single-cell atlases throughout Metazoa unravels cell type evolution. eLife, 10, e66747.',
    # 22. Jiang 2024 Brief Bioinform — CACIMAR
    '22. Jiang,J., Li,J., Huang,Y., Wang,Y., Chen,L. and Zhang,X. (2024) CACIMAR: cross-species analysis of cell identities, markers, regulations, and interactions. Brief. Bioinform., 25, bbae283.',
    # 23. Hao 2021 Cell — Seurat v4
    '23. Hao,Y., Hao,S., Andersen-Nissen,E., Mauck,W.M., Zheng,S., Butler,A., Lee,M.J., Wilk,A.J., Darby,C., Zager,M. et al. (2021) Integrated analysis of multimodal single-cell data. Cell, 184, 3573–3587.',
    # 24. CZI Cell Science Program 2025 NAR — CZ CELLxGENE Discover (replaces Megill 2021)
    '24. CZI Cell Science Program. (2025) CZ CELLxGENE Discover: a single-cell data platform for scalable exploration, analysis and modeling of aggregated data. Nucleic Acids Res., 53, D886–D900.',
    # 25. Colaprico 2016 NAR — TCGAbiolinks
    '25. Colaprico,A., Silva,T.C., Olsen,C., Garofano,L., Cava,C., Garolini,D., Sabedot,T.S., Malta,T.M., Pagnotta,S.M., Castiglioni,I. et al. (2016) TCGAbiolinks: an R/Bioconductor package for integrative analysis of TCGA data. Nucleic Acids Res., 44, e71.',
    # 26. Cerami 2012 Cancer Discov — cBioPortal
    '26. Cerami,E., Gao,J., Dogrusoz,U., Gross,B.E., Sumer,S.O., Aksoy,B.A., Jacobsen,A., Byrne,C.J., Heuer,M.L., Larsson,E. et al. (2012) The cBio Cancer Genomics Portal: an open platform for exploring multidimensional cancer genomics data. Cancer Discov., 2, 401–404.',
    # 27. Liberzon 2015 Cell Syst — MSigDB Hallmark
    '27. Liberzon,A., Birger,C., Thorvaldsdóttir,H., Ghandi,M., Mesirov,J.P. and Tamayo,P. (2015) The Molecular Signatures Database Hallmark Gene Set Collection. Cell Syst., 1, 417–425.',
    # 28. Tsai 2016 Science — OPC vascular migration
    '28. Tsai,H.H., Niu,J., Munji,R., Davalos,D., Chang,J., Zhang,H., Tien,A.C., Kuo,C.J., Chan,J.R., Daneman,R. et al. (2016) Oligodendrocyte precursors migrate along vasculature in the developing nervous system. Science, 351, 379–384.',
    # 29. Akay 2022 Neuron — astrocyte endfoot OPC migration termination
    '29. Akay,L.A., Effenberger,A.H. and Tsai,L.H. (2022) Astrocyte endfoot formation controls the termination of oligodendrocyte precursor cell perivascular migration. Neuron, 110, 3699–3714.',
    # 30. Foerster 2024 Nat Neurosci — developmental origin of oligodendrocytes
    '30. Foerster,S., Floriddia,E.M., Neumann,B., Agirre,E., Castelo-Branco,G. and Franklin,R.J.M. (2024) Developmental origin of oligodendrocytes determines their function in the adult brain. Nat. Neurosci., 27, 1155–1166.',
    # 31. Endo 2024 EMBO J — Tcf4 astrocyte allocation
    '31. Endo,F., Kasai,A., Cui,W., Tanaka,K.F. and Hashimoto,H. (2024) Astrocyte allocation during brain development is controlled by Tcf4-mediated fate restriction. EMBO J., 43, 4423–4447.',
    # 32. Yang 2024 Cell Discov — fetal cerebellum single-cell multi-omics (replaces Sepp 2026)
    '32. Yang,L., Zhao,Z., Li,Y., Wang,J., Chen,X. and Liu,Z. (2024) Single-cell multi-omics analysis of lineage development and spatial organization in the human fetal cerebellum. Cell Discov., 10, 25.',
    # 33. Tan 2020 Mol Psychiatry — microglial heterogeneity
    '33. Tan,Y.L., Yuan,Y. and Tian,L. (2020) Microglial regional heterogeneity and its role in the brain. Mol. Psychiatry, 25, 351–367.',
    # 34. Menassa 2022 Dev Cell — microglia across lifespan
    '34. Menassa,D.A., Muntslag,T.A.O., Martin-Estebané,M., Barry-Carroll,L., Chapman,M.A., Adorjan,I., Tyler,T., Turnbull,B., Rose-Zerilli,M.J.J., Nicoll,J.A.R. et al. (2022) The spatiotemporal dynamics of microglia across the human lifespan. Dev. Cell, 57, 1910–1927.',
    # 35. Walchli 2024 Nature — brain vasculature atlas
    '35. Wälchli,T., Ghobrial,M., Schwab,M., Takada,S., Zhong,H., Le,J., Bisschop,J., Lyons,K., Wood,S., He,L. et al. (2024) Single-cell atlas of the human brain vasculature across development, adulthood and disease. Nature, 632, 603–613.',
    # 36. Hao 2024 Nat Biotechnol — Seurat v5 integration
    '36. Hao,Y., Stuart,T., Kowalski,M.H., Choudhary,S., Hoffman,P., Hartman,A., Srivastava,A., Molla,G., Madad,S., Fernandez-Granda,C. et al. (2024) Dictionary learning for integrative, multimodal and scalable single-cell analysis. Nat. Biotechnol., 42, 293–304.',
]

"""

content = content[:old_refs_start] + new_refs_block + content[old_refs_end:]

# ============================================================
# STEP 2: Specific citation fixes (ordered carefully to avoid conflicts)
# ============================================================

# 2a. Remove Lin 1991 JS divergence citations (15) → just remove the parenthetical reference
# L176, L590: "(15)" at end of sentence before period
content = content.replace(' (15)). The computation', '). The computation')
content = content.replace('JS divergence uses base-2 logarithm (range (0,1)) (15).',
                         'JS divergence uses base-2 logarithm (range [0,1]).')
content = content.replace('the same metric (Jensen-Shannon divergence) (15)',
                         'the same metric (Jensen-Shannon divergence)')

# 2b. Remove Efron 1979 bootstrap citations (16)
content = content.replace('bootstrap permutation testing (B = 1,000) (16).',
                         'bootstrap permutation testing (B = 1,000).')
content = content.replace('(B = 1,000) (16),',
                         '(B = 1,000),')
content = content.replace('B = 1,000 permutations (16);',
                         'B = 1,000 permutations;')

# 2c. Replace Benjamini 1995 (17) -> Storey 2003 (15)
content = content.replace('Benjamini-Hochberg FDR correction (q < 0.05) (17).',
                         'Benjamini-Hochberg FDR correction (q < 0.05) (15).')
content = content.replace('Benjamini-Hochberg FDR correction (17) at q < 0.05 for multi-pair comparisons.',
                         'Benjamini-Hochberg FDR correction (15) at q < 0.05 for multi-pair comparisons.')
content = content.replace('apply Benjamini-Hochberg FDR correction (17) at q < 0.05. ',
                         'apply Benjamini-Hochberg FDR correction (15) at q < 0.05. ')

# 2d. Replace Megill 2021 (26) -> CZI CELLxGENE (24)
content = content.replace('CZ CELLxGENE Discover (26).',
                         'CZ CELLxGENE Discover (24).')
content = content.replace('(https://cellxgene.cziscience.com/) (26).',
                         '(https://cellxgene.cziscience.com/) (24).')

# 2e. Remove Pedregosa 2011 scikit-learn (29)
content = content.replace('were computed using scikit-learn (29).',
                         'were computed using scikit-learn.')
content = content.replace('seaborn >= 0.12.0, and scikit-learn >= 1.2.0 (29).',
                         'seaborn >= 0.12.0, and scikit-learn >= 1.2.0.')

# 2f. Replace Sepp 2026 (35) -> Yang 2024 (32) in narrative text
content = content.replace('Sepp et al. (35) showed that human Bergmann glia',
                         'Yang et al. (32) showed that human fetal cerebellar glia')
content = content.replace('Bergmann glia developmental migration (Sepp 2026)',
                         'fetal cerebellar glia development (Yang 2024)')

# ============================================================
# STEP 3: General citation renumbering for all remaining numbers > 17
# ============================================================

# Mapping: old → new for citations that shifted due to deletions
# After step 2, all remaining old numbers need to be mapped
# 15→deleted, 16→deleted, 17→15, 18→16, 19→17, 20→18, 21→19, 22→20,
# 23→21, 24→22, 25→23, 26→24, 27→25, 28→26, 29→deleted, 30→27,
# 31→28, 32→29, 33→30, 34→31, 35→32, 36→33, 37→34, 38→35, 39→36

import re

def replace_citations_in_text(text):
    """Replace old citation numbers in parenthetical citations with new numbers.
    Handles patterns like (18), (25), (7-9), (31,32), etc."""
    
    # Mapping table
    mapping = {
        18: 16, 19: 17, 20: 18, 21: 19, 22: 20,
        23: 21, 24: 22, 25: 23, 
        27: 25, 28: 26,
        30: 27, 31: 28, 32: 29, 33: 30, 34: 31,
        36: 33, 37: 34, 38: 35, 39: 36,
    }
    
    # Find all parenthetical citation groups like (7), (1,2), (5-9), (31,32)
    def replace_match(m):
        cite_str = m.group(1)  # e.g., "18" or "7-9" or "31,32"
        parts = re.split(r'[,;]', cite_str)
        new_parts = []
        for part in parts:
            part = part.strip()
            if '-' in part:
                a, b = part.split('-')
                a_new = mapping.get(int(a), int(a))
                b_new = mapping.get(int(b), int(b))
                if a_new == b_new:
                    new_parts.append(str(a_new))
                else:
                    new_parts.append(f'{a_new}-{b_new}')
            else:
                try:
                    num = int(part)
                    new_num = mapping.get(num, num)
                    new_parts.append(str(new_num))
                except ValueError:
                    new_parts.append(part)
        return '(' + ', '.join(new_parts) + ')'
    
    # Match parenthesized citation groups: digits, commas, hyphens
    # Be careful NOT to match data values like (15.97) or (888,263) or (0,1)
    # Citations are like (18) or (7-9) or (31,32) — simple number patterns
    text = re.sub(r'\((\d+(?:[-,;]\s*\d+)*)\)', replace_match, text)
    
    return text

content = replace_citations_in_text(content)

# ============================================================
# STEP 4: Write back
# ============================================================
with open('generate_manuscript_v4_nar.py', 'w') as f:
    f.write(content)

print("fix_refs_final.py: References updated (39 → 36). Citations remapped.")
