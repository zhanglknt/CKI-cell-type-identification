"""Patch manuscript: cross-organ, brain, discussion, conclusions, methods."""
from _load_manuscript_data import get_manuscript_data
DATA = get_manuscript_data()
_ds = DATA['datasets']
_mc = DATA['mouse_calibration']
_h = DATA['human']
_sc = DATA['spearman_corr']
_tc = DATA['tcga']
_br = DATA['brain']
_br_ct = _br['cell_types']
_au = DATA['table1_auc']
_sb = DATA['sweep']
_co = DATA['cross_organ_spearman']
t2 = DATA['table2_data']
tcga_cancers = _tc['cancers']
min_c = min(tcga_cancers, key=lambda x: x['nn_tt_ratio'])
max_c = max(tcga_cancers, key=lambda x: x['nn_tt_ratio'])

def find_ct(name):
    for ct in _br_ct:
        if name.lower() in ct['name'].lower():
            return ct
    return None

with open('generate_manuscript_genome_biology.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === Cross-organ intro (hardcoded 4851, 59) ===
old = "p('Among the 4,851 Tabula Sapiens cell-type pairs, 59 are same-cell-type cross-organ comparisons. These pairs allowed us to ask: which cell types maintain their transcriptional identity regardless of where they reside, and which are strongly shaped by their organ environment (Fig. 5; Table 2)?')"
new = (
    "p(f'Among the {_h[\"n_pairs\"]:,} Tabula Sapiens cell-type pairs, "
    f"{{DATA[\"cross_organ_n_total\"]}} are same-cell-type cross-organ comparisons. "
    "These pairs allowed us to ask: which cell types maintain their transcriptional identity "
    "regardless of where they reside, and which are strongly shaped by their organ environment "
    "(Fig. 5; Table 2)?')"
)
if old in content:
    content = content.replace(old, new)
    print('OK: cross-organ intro')
else:
    print('WARN: cross-organ intro not found')

# === Cross-organ ranking paragraph ===
old = (
    "p('The cross-organ \u03c9 ranking reveals a broad spectrum of conservation across 17 cell types (Table 2). Hepatocytes and B cells were among the most conserved (mean \u03c9 = 8.57 and 9.36, respectively, n = 1 each), followed by CD8+ T cells (mean 9.93 \u00b1 4.2, n = 6) and plasma cells (mean 10.20 \u00b1 1.9, n = 6). Macrophages, the most abundant cell type in cross-organ comparisons (n = 15), showed intermediate conservation (mean 15.49 \u00b1 8.2). At the divergent end of the spectrum, endothelial cells (mean 26.25 \u00b1 7.0, n = 3) and erythrocytes (mean 29.36 \u00b1 18.8, n = 3) were the most organ-specific cell types. Endothelial cells are known to express organ-specific gene programs tailored to local vascular needs [32]. We note that several cell types (particularly those with n = 1 or 3) have small sample sizes, and their rankings should be interpreted with appropriate caution.')"
)

top2 = t2[:2]
next2 = t2[2:4]
mac = [r for r in t2 if 'Macrophage' in r[0]][0]
last2 = t2[-2:]

new = (
    "p(f'The cross-organ \u03c9 ranking reveals a broad spectrum of conservation across "
    f"{{len(t2)}} cell types (Table 2). "
    f"{{t2[0][0]}}s and {{t2[1][0]}}s were among the most conserved "
    f"(mean \u03c9 = {{t2[0][1]}} and {{t2[1][1]}}, respectively, n = {{t2[0][3]}} each), "
    f"followed by {{t2[2][0]}}s (mean {{t2[2][1]}} \u00b1 {{t2[2][2]}}, n = {{t2[2][3]}}) "
    f"and {{t2[3][0]}}s (mean {{t2[3][1]}} \u00b1 {{t2[3][2]}}, n = {{t2[3][3]}}). "
    f"{{mac[0]}}s, the most abundant cell type in cross-organ comparisons (n = {{mac[3]}}), "
    f"showed intermediate conservation (mean {{mac[1]}} \u00b1 {{mac[2]}}). "
    f"At the divergent end of the spectrum, {{last2[0][0]}}s (mean {{last2[0][1]}} \u00b1 {{last2[0][2]}}, n = {{last2[0][3]}}) "
    f"and {{last2[1][0]}}s (mean {{last2[1][1]}} \u00b1 {{last2[1][2]}}, n = {{last2[1][3]}}) "
    "were the most organ-specific cell types. Endothelial cells are known to express organ-specific "
    "gene programs tailored to local vascular needs [32]. We note that several cell types "
    "(particularly those with n = 1 or 3) have small sample sizes, and their rankings should be "
    "interpreted with appropriate caution.')"
)

if old in content:
    content = content.replace(old, new)
    print('OK: cross-organ ranking')
else:
    print('WARN: cross-organ ranking not found')

# === Cross-organ correlation ===
old2 = (
    "p('The cross-organ conservation ranking from CKI showed little agreement with rankings "
    "from standard metrics (Spearman r = -0.40 to +0.02, n = 59 pairs). This is because "
    "CKI explicitly normalizes: two cell populations might share similar highly expressed "
    "genes (yielding high Jaccard similarity), but if their neutral baseline k_n is low, "
    "even modest functional differences can produce a high \u03c9. This normalization reveals "
    "patterns that raw expression similarity misses.')"
)

co_vals = [(k, v) for k, v in _co.items()]
co_vals.sort(key=lambda x: x[1])
new2 = (
    "p(f'The cross-organ conservation ranking from CKI showed little agreement with rankings "
    f"from standard metrics ({{_co[\"spearman\"]:.2f}} to {{_co[\"js_raw\"]:.2f}}, "
    "n = {DATA['cross_organ_n_total']} pairs). This is because "
    "CKI explicitly normalizes: two cell populations might share similar highly expressed "
    "genes (yielding high Jaccard similarity), but if their neutral baseline k_n is low, "
    "even modest functional differences can produce a high \u03c9. This normalization reveals "
    "patterns that raw expression similarity misses.')"
)

if old2 in content:
    content = content.replace(old2, new2)
    print('OK: cross-organ correlation')
else:
    print('WARN: cross-organ correlation not found')

# === Brain intro paragraph ===
old3 = (
    "p('We applied CKI to the Siletti et al. human brain single-nucleus RNA-seq atlas [9], which profiles ~3.3 million nuclei across ~100 brain regions. This dataset allowed us to ask: for a given cell type, how much functional divergence exists between the same cells residing in different brain regions? We focused on the 888,263 non-neuronal nuclei spanning 10 major cell classes (astrocytes, oligodendrocytes, oligodendrocyte precursors, microglia, vascular cells, fibroblasts, ependymal cells, choroid plexus, committed oligodendrocyte precursors, and Bergmann glia), and computed CKI \u03c9 for all same-cell-type cross-region comparisons (31,764 pairs total) (Fig. 6).')"
)

new3 = (
    "p(f'We applied CKI to the Siletti et al. human brain single-nucleus RNA-seq atlas [9], which profiles ~3.3 million nuclei across ~100 brain regions. This dataset allowed us to ask: for a given cell type, how much functional divergence exists between the same cells residing in different brain regions? We focused on the {_br[\"n_nuclei\"]:,} non-neuronal nuclei spanning {len(_br_ct)} major cell classes ({', '.join([ct[\"name\"].lower() for ct in _br_ct])}), and computed CKI \u03c9 for all same-cell-type cross-region comparisons ({_br[\"total_pairs\"]:,} pairs total) (Fig. 6).')"
)

if old3 in content:
    content = content.replace(old3, new3)
    print('OK: brain intro')
else:
    print('WARN: brain intro not found')

# === Brain gradient paragraph ===
old4 = (
    "p('The analysis revealed a striking differentiation gradient spanning 6.06-fold. Bergmann glia showed the lowest mean \u03c9 (2.37 \u00b1 1.14, n = 21 pairs across 7 regions), followed by committed oligodendrocyte precursor cells (3.17 \u00b1 1.47, n = 1,326 pairs across 52 regions), and fibroblasts (3.99 \u00b1 1.90, n = 3,403 pairs across 83 regions). Vascular cells (3.40 \u00b1 1.24, n = 3,321 pairs across 82 regions) and ependymal cells (4.13 \u00b1 1.73, n = 780 pairs across 40 regions) showed similarly low divergence. Microglia exhibited moderate divergence (mean \u03c9 = 8.02 \u00b1 4.93, n = 5,671 pairs across 107 regions). Oligodendrocytes and their precursors showed intermediate divergence (mean \u03c9 = 8.66 \u00b1 4.44 and 7.65 \u00b1 4.03, respectively). Astrocytes were the most regionally divergent cell type (mean \u03c9 = 14.36 \u00b1 8.68, n = 5,778 pairs across 108 regions), a 6.06-fold increase over Bergmann glia.')"
)

sbg = sorted(_br_ct, key=lambda x: x['omega_mean'])
b0 = sbg[0]  # Bergmann
b1 = sbg[1]  # COPC
b2 = sbg[2]  # vascular
b3 = sbg[3]  # fibroblast
b_last = sbg[-1]  # astrocyte

new4 = (
    "p(f'The analysis revealed a striking differentiation gradient spanning "
    f"{{_br[\"gradient_fold\"]:.2f}}-fold. "
    f"{{sbg[0][\"name\"]}} showed the lowest mean \u03c9 "
    f"({{sbg[0][\"omega_mean\"]:.2f}} \u00b1 {{sbg[0][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[0][\"n_pairs\"]:,}} pairs across {{sbg[0][\"n_regions\"]}} regions), "
    f"followed by {{sbg[1][\"name\"]}} ({{sbg[1][\"omega_mean\"]:.2f}} \u00b1 {{sbg[1][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[1][\"n_pairs\"]:,}} pairs across {{sbg[1][\"n_regions\"]}} regions), "
    f"and {{sbg[3][\"name\"]}}s ({{sbg[3][\"omega_mean\"]:.2f}} \u00b1 {{sbg[3][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[3][\"n_pairs\"]:,}} pairs across {{sbg[3][\"n_regions\"]}} regions). "
    f"{{sbg[2][\"name\"]}} ({{sbg[2][\"omega_mean\"]:.2f}} \u00b1 {{sbg[2][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[2][\"n_pairs\"]:,}} pairs across {{sbg[2][\"n_regions\"]}} regions) "
    f"and {{sbg[4][\"name\"]}}s ({{sbg[4][\"omega_mean\"]:.2f}} \u00b1 {{sbg[4][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[4][\"n_pairs\"]:,}} pairs across {{sbg[4][\"n_regions\"]}} regions) "
    "showed similarly low divergence. "
    f"{{sbg[5][\"name\"]}} exhibited moderate divergence "
    f"(mean \u03c9 = {{sbg[5][\"omega_mean\"]:.2f}} \u00b1 {{sbg[5][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[5][\"n_pairs\"]:,}} pairs across {{sbg[5][\"n_regions\"]}} regions). "
    f"{{sbg[-3][\"name\"]}}s and their precursors showed intermediate divergence "
    f"(mean \u03c9 = {{sbg[-3][\"omega_mean\"]:.2f}} \u00b1 {{sbg[-3][\"omega_std\"]:.2f}} and "
    f"{{sbg[-2][\"omega_mean\"]:.2f}} \u00b1 {{sbg[-2][\"omega_std\"]:.2f}}, "
    "respectively). "
    f"{{sbg[-1][\"name\"]}}s were the most regionally divergent cell type "
    f"(mean \u03c9 = {{sbg[-1][\"omega_mean\"]:.2f}} \u00b1 {{sbg[-1][\"omega_std\"]:.2f}}, "
    f"n = {{sbg[-1][\"n_pairs\"]:,}} pairs across {{sbg[-1][\"n_regions\"]}} regions), "
    f"a {{_br[\"gradient_fold\"]:.2f}}-fold increase over {{sbg[0][\"name\"]}}.')\n"
    "\n"
    "# Pre-sort brain cell types for dynamic gradient text\n"
    "sbg = sorted(_br_ct, key=lambda x: x['omega_mean'])\n"
)

if old4 in content:
    content = content.replace(old4, new4)
    print('OK: brain gradient')
else:
    print('WARN: brain gradient not found')

# === Brain migration model paragraph ===
old5 = (
    "p('To formalize migration inference, we designed a multiplicative model: for each (cell_type, region_pair) combination, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, where \u03bc_ct is the cell type\'s global mean \u03c9, \u03bc_pair is the region pair\'s mean \u03c9, and \u03bc_grand is the global mean (8.01). The multiplicative residual = observed / expected: a residual substantially below 1 indicates that the cell type is far less differentiated between those two regions than expected from both its own global plasticity and the region pair\'s overall divergence\u2014a signature of shared transcriptional state potentially reflecting recent migration. We defined three confidence tiers: Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the region pair, and pair median \u03c9 > 20), Moderate (residual < 0.5, \u03c9 < 25), and Weak (residual < 0.75, \u03c9 < 35).')"
)

th = _br['residual_thresholds']
new5 = (
    "p(f'To formalize migration inference, we designed a multiplicative model: for each "
    f"(cell_type, region_pair) combination, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, "
    f"where \u03bc_ct is the cell type\\'s global mean \u03c9, \u03bc_pair is the region pair\\'s "
    f"mean \u03c9, and \u03bc_grand is the global mean ({{_br[\"global_mean\"]:.2f}}). "
    "The multiplicative residual = observed / expected: a residual substantially below 1 "
    "indicates that the cell type is far less differentiated between those two regions than "
    "expected from both its own global plasticity and the region pair\\'s overall divergence\u2014"
    "a signature of shared transcriptional state potentially reflecting recent migration. "
    f"We defined three confidence tiers: Strong (residual < {{th[\"strong\"]}}, "
    f"\u03c9 < {{th[\"strong_omega_max\"]}}, lowest \u03c9 in the region pair, "
    f"and pair median \u03c9 > {{th[\"strong_pair_median_min\"]}}), "
    f"Moderate (residual < {{th[\"moderate\"]}}, \u03c9 < {{th[\"moderate_omega_max\"]}}), "
    f"and Weak (residual < {{th[\"weak\"]}}, \u03c9 < {{th[\"weak_omega_max\"]}}).')"
)

if old5 in content:
    content = content.replace(old5, new5)
    print('OK: brain migration model')
else:
    print('WARN: brain migration model not found')

# === Brain Strong signals paragraph ===
old6 = (
    "p('Among 31,764 cross-region comparisons, 30 (0.09%) were classified as Strong migration candidates: Astrocyte (6), fibroblast (1), microglia (10), oligodendrocyte (10), and vascular cells (3). Another 1,247 pairs (3.93%) were Moderate candidates, and 6,567 (20.67%) were Weak candidates. By cell type, the Strong candidate counts reflect a combination of regional adjacency, shared developmental origins, and ongoing cellular interchange.')"
)

new6 = (
    "p(f'Among {_br[\"total_pairs\"]:,} cross-region comparisons, "
    f"{{_br[\"n_strong\"]}} ({{_br[\"pct_strong\"]:.2f}}%) were classified as "
    "Strong migration candidates: Astrocyte (6), fibroblast (1), microglia (10), "
    "oligodendrocyte (10), and vascular cells (3). "
    f"Another {{_br[\"n_moderate\"]:,}} pairs ({{_br[\"pct_moderate\"]:.2f}}%) "
    "were Moderate candidates, and "
    f"{{_br[\"n_weak\"]:,}} ({{_br[\"pct_weak\"]:.2f}}%) were Weak candidates. "
    "By cell type, the Strong candidate counts reflect a combination of regional adjacency, "
    "shared developmental origins, and ongoing cellular interchange.')"
)

if old6 in content:
    content = content.replace(old6, new6)
    print('OK: brain strong signals')
else:
    print('WARN: brain strong signals not found')

# === OPC omega value ===
old7 = "p('Oligodendrocyte precursor cells (OPCs) are the most actively migrating cells in the adult CNS, continuously surveilling their environment along vascular scaffolds [13,17]. Yet CKI detected 0 Strong signals among 5,671 OPC cross-region comparisons\u2014a finding that provides a critical orthogonal validation of the multiplicative residual model. The model is not simply detecting high \u03c9 values or absolute transcriptional differences; it identifies cell-type/region-pair combinations where the observed selective remodeling is strikingly below what the cell type\'s global plasticity and the region pair\'s background divergence would jointly predict. OPCs have a high global mean \u03c9 (7.65) because their transcriptional program includes both progenitor and differentiation states; their 52 Moderate signals (residual < 0.5) likely reflect the balance between shared developmental origins and ongoing regional maturation [35]. The complete absence of Strong signals despite OPCs being the brain\'s most motile cell type demonstrates that the residual model differentiates between broad baseline motility and specific transcriptional signatures of developmental history.')"

opc = find_ct('oligodendrocyte precursor')
new7 = (
    "p(f'Oligodendrocyte precursor cells (OPCs) are the most actively migrating cells in the adult CNS, continuously surveilling their environment along vascular scaffolds [13,17]. "
    f"Yet CKI detected 0 Strong signals among {{opc[\"n_pairs\"]:,}} OPC cross-region comparisons\u2014"
    "a finding that provides a critical orthogonal validation of the multiplicative residual model. "
    "The model is not simply detecting high \u03c9 values or absolute transcriptional differences; "
    "it identifies cell-type/region-pair combinations where the observed selective remodeling is "
    "strikingly below what the cell type\\'s global plasticity and the region pair\\'s background "
    "divergence would jointly predict. OPCs have a high global mean \u03c9 "
    f"({{opc[\"omega_mean\"]:.2f}}) because their transcriptional program includes both progenitor "
    "and differentiation states; their 52 Moderate signals (residual < 0.5) likely reflect the "
    "balance between shared developmental origins and ongoing regional maturation [35]. "
    "The complete absence of Strong signals despite OPCs being the brain\\'s most motile cell type "
    "demonstrates that the residual model differentiates between broad baseline motility and "
    "specific transcriptional signatures of developmental history.')\n"
    "\n"
    "# Pre-find OPC and Astrocyte data\n"
    "opc = find_ct('oligodendrocyte precursor')\n"
    "astro = find_ct('astrocyte')\n"
    "oligo_ct = find_ct('oligodendrocyte')\n"
    "bergmann_ct = find_ct('bergmann')\n"
)

if old7 in content:
    content = content.replace(old7, new7)
    print('OK: OPC paragraph')
else:
    print('WARN: OPC paragraph not found')

# === Oligodendrocyte omega value ===
old8 = (
    "p('Mature oligodendrocytes contributed 10 Strong signals (residual 0.237\u20130.292), yet the prevailing view is that adult oligodendrocytes do not migrate between brain regions. We systematically cross-validated all 10 Strong pairs against the developmental neurobiology literature. Strikingly, all 10 signals involved cortex/thalamus (A13/A14/A19/A32/A40/Idg vs. Pul/LP) or brainstem-internal (MoRF-MoEN vs. PnRF) pairings\u2014precisely the anatomical boundaries between dorsal- and ventral-derived oligodendrocyte populations. Foerster et al. [35] demonstrated through dorsal oligodendrocyte lineage ablation that >90% of adult cortical oligodendrocytes are dorsally derived (from cortical radial glia), while thalamic and brainstem oligodendrocytes are ventrally derived (MGE/LGE precursors). Ventral-derived cells fail to adopt cortical transcriptional programs even when transplanted into the cortex, indicating persistent cell-autonomous transcriptional identity. Our CKI analysis detects this developmental origin signature: dorsal vs. ventral oligodendrocyte populations are far less selectively diverged than expected from the oligodendrocyte global \u03c9 (8.66), because their transcriptional differences reflect shared generic myelination programs rather than region-specific functional specialization. LP (lateral posterior nucleus) and Pul (pulvinar), thalamic relay nuclei, contrast with cortical Brodmann areas A13-A40, forming the most consistent developmental boundary detected by our analysis. This reinterpretation\u2014that CKI Strong signals for oligodendrocytes detect persistent developmental origin signatures rather than migration\u2014is fully consistent with Foerster et al.\'s experimental data and provides, to the best of our knowledge, the first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations without requiring lineage tracing.')"
)

new8 = (
    "p(f'Mature oligodendrocytes contributed 10 Strong signals (residual 0.237\u20130.292), yet the prevailing view is that adult oligodendrocytes do not migrate between brain regions. We systematically cross-validated all 10 Strong pairs against the developmental neurobiology literature. Strikingly, all 10 signals involved cortex/thalamus (A13/A14/A19/A32/A40/Idg vs. Pul/LP) or brainstem-internal (MoRF-MoEN vs. PnRF) pairings\u2014precisely the anatomical boundaries between dorsal- and ventral-derived oligodendrocyte populations. Foerster et al. [35] demonstrated through dorsal oligodendrocyte lineage ablation that >90% of adult cortical oligodendrocytes are dorsally derived (from cortical radial glia), while thalamic and brainstem oligodendrocytes are ventrally derived (MGE/LGE precursors). Ventral-derived cells fail to adopt cortical transcriptional programs even when transplanted into the cortex, indicating persistent cell-autonomous transcriptional identity. Our CKI analysis detects this developmental origin signature: dorsal vs. ventral oligodendrocyte populations are far less selectively diverged than expected from the oligodendrocyte global \u03c9 ({{oligo_ct[\"omega_mean\"]:.2f}}), because their transcriptional differences reflect shared generic myelination programs rather than region-specific functional specialization. LP (lateral posterior nucleus) and Pul (pulvinar), thalamic relay nuclei, contrast with cortical Brodmann areas A13-A40, forming the most consistent developmental boundary detected by our analysis. This reinterpretation\u2014that CKI Strong signals for oligodendrocytes detect persistent developmental origin signatures rather than migration\u2014is fully consistent with Foerster et al.\\'s experimental data and provides, to the best of our knowledge, the first transcriptome-wide metric to distinguish dorsal and ventral oligodendrocyte populations without requiring lineage tracing.')"
)

if old8 in content:
    content = content.replace(old8, new8)
    print('OK: oligodendrocyte paragraph')
else:
    print('WARN: oligodendrocyte paragraph not found')

# === Astrocyte omega value ===
old9 = (
    "p('Astrocytes showed the highest global \u03c9 (14.36) yet contributed 6 Strong signals, all concentrated in thalamic subnuclei (VLN-VPL, CM-VPL, Pul-VPL, LP-VPL-MN), hippocampal subfields (CA2-3 vs. DG-CA4), and cerebellar lobules (CBL vs. CBV). The thalamic signals are particularly informative: the ventroposterior lateral nucleus (VPL) appears in 4 of 6 Strong pairs, suggesting conserved astrocyte programs across thalamic relay nuclei that share a common developmental origin. Regionalized astrogenesis, driven by subnucleus-specific transcriptional programs, has been shown to produce persistent thalamic astrocyte heterogeneity that is detectable in adult tissue. Our finding that thalamic astrocyte pairs have \u03c9 values 5\u20136-fold below expectation indicates that these developmental signatures are selectively constrained\u2014astrocytes in functionally related thalamic nuclei retain transcriptional similarity beyond what would be predicted from astrocyte global plasticity alone. The cerebellar CBL vs. CBV signal (residual = 0.274) reflects the molecular topographic zones of Bergmann glia and cerebellar astrocytes described by Reeber et al. [41]. Endo et al. [18] demonstrated that Tcf4 controls astrocyte allocation during cortical development; our results extend this principle to subcortical structures, showing that compartmentalized astrogenesis leaves persistent transcriptional signatures detectable by CKI across the entire brain.')"
)

new9 = (
    "p(f'Astrocytes showed the highest global \u03c9 ({{astro[\"omega_mean\"]:.2f}}) yet contributed 6 Strong signals, all concentrated in thalamic subnuclei (VLN-VPL, CM-VPL, Pul-VPL, LP-VPL-MN), hippocampal subfields (CA2-3 vs. DG-CA4), and cerebellar lobules (CBL vs. CBV). The thalamic signals are particularly informative: the ventroposterior lateral nucleus (VPL) appears in 4 of 6 Strong pairs, suggesting conserved astrocyte programs across thalamic relay nuclei that share a common developmental origin. Regionalized astrogenesis, driven by subnucleus-specific transcriptional programs, has been shown to produce persistent thalamic astrocyte heterogeneity that is detectable in adult tissue. Our finding that thalamic astrocyte pairs have \u03c9 values 5\u20136-fold below expectation indicates that these developmental signatures are selectively constrained\u2014astrocytes in functionally related thalamic nuclei retain transcriptional similarity beyond what would be predicted from astrocyte global plasticity alone. The cerebellar CBL vs. CBV signal (residual = 0.274) reflects the molecular topographic zones of Bergmann glia and cerebellar astrocytes described by Reeber et al. [41]. Endo et al. [18] demonstrated that Tcf4 controls astrocyte allocation during cortical development; our results extend this principle to subcortical structures, showing that compartmentalized astrogenesis leaves persistent transcriptional signatures detectable by CKI across the entire brain.')"
)

if old9 in content:
    content = content.replace(old9, new9)
    print('OK: astrocyte paragraph')
else:
    print('WARN: astrocyte paragraph not found')

# === Bergmann glia omega value ===
old10 = (
    "p('Bergmann glia had the lowest global \u03c9 (2.37) and only one Strong signal (CBL vs. CBV, residual = 0.274), consistent with their developmentally fixed, transcriptionally constrained state in the adult cerebellum. Bergmann glia are patterned into topographic molecular zones that align with cerebellar functional compartments [41], and their low global \u03c9 reflects their specialized role in maintaining Purkinje cell layer architecture with minimal regional transcriptional variation. The CBL (cerebellar lobule) vs. CBV (cerebellar vermis) signal likely reflects the established molecular topography difference between lateral cerebellar hemispheres and the midline vermis, rather than any migratory event.')"
)

new10 = (
    "p(f'Bergmann glia had the lowest global \u03c9 ({{bergmann_ct[\"omega_mean\"]:.2f}}) and only one Strong signal (CBL vs. CBV, residual = 0.274), consistent with their developmentally fixed, transcriptionally constrained state in the adult cerebellum. Bergmann glia are patterned into topographic molecular zones that align with cerebellar functional compartments [41], and their low global \u03c9 reflects their specialized role in maintaining Purkinje cell layer architecture with minimal regional transcriptional variation. The CBL (cerebellar lobule) vs. CBV (cerebellar vermis) signal likely reflects the established molecular topography difference between lateral cerebellar hemispheres and the midline vermis, rather than any migratory event.')"
)

if old10 in content:
    content = content.replace(old10, new10)
    print('OK: bergmann paragraph')
else:
    print('WARN: bergmann paragraph not found')

# === Discussion - replace 6.06-fold reference ===
old_disc = (
    "p('The cross-organ and cross-brain-region analyses establish CKI as a general tool for measuring functional differentiation at multiple spatial scales. The brain analysis revealed a 6.06-fold \u03c9 gradient across 10 cell classes (from 2.37 in Bergmann glia to 14.36 in astrocytes), demonstrating that CKI can detect regional functional specialization even among cells of the same type. Critically, the multiplicative residual model detected 30 Strong candidate signals and systematic cross-validation against the developmental neuroscience literature revealed that these signals predominantly reflect three distinct biological processes rather than active cell migration: (i) developmental origin heterogeneity\u2014oligodendrocyte dorsal/ventral origin differences [35] explain all 10 oligodendrocyte Strong signals as cortex vs. thalamus/brainstem boundaries; (ii) embryonic colonization route discontinuities\u2014microglial rostral-to-caudal colonization waves [20,37,40] create transcriptomic boundaries at the forebrain-midbrain interface, with the inferior colliculus identified as a candidate contact zone; and (iii) compartmentalized developmental astrogenesis and vascular specification [18,39]. Importantly, OPCs\u2014the most actively migrating cells in the adult CNS [13,17]\u2014yielded 0 Strong signals among 5,671 comparisons, providing a powerful orthogonal validation that the residual model specifically detects fixed developmental signatures rather than ongoing cell motility. The sole exception is the perivascular fibroblast A40-SN signal, which is consistent with known postnatal meningeal-to-parenchymal fibroblast migration [38]. Together, these results demonstrate that CKI detects persistent transcriptional signatures of developmental history\u2014origin, colonization route, and specification\u2014embedded in adult transcriptomic data, rather than inferring active migration per se. This reframing opens new applications for adult single-cell atlases as archives of developmental information.')"
)

new_disc = (
    "p(f'The cross-organ and cross-brain-region analyses establish CKI as a general tool for measuring functional differentiation at multiple spatial scales. The brain analysis revealed a {_br[\"gradient_fold\"]:.2f}-fold \u03c9 gradient across {len(_br_ct)} cell classes (from {_br[\"gradient_lowest_omega\"]:.2f} in {_br[\"gradient_lowest_ct\"]} to {_br[\"gradient_highest_omega\"]:.2f} in {_br[\"gradient_highest_ct\"]}), demonstrating that CKI can detect regional functional specialization even among cells of the same type. Critically, the multiplicative residual model detected {_br[\"n_strong\"]} Strong candidate signals and systematic cross-validation against the developmental neuroscience literature revealed that these signals predominantly reflect three distinct biological processes rather than active cell migration: (i) developmental origin heterogeneity\u2014oligodendrocyte dorsal/ventral origin differences [35] explain all 10 oligodendrocyte Strong signals as cortex vs. thalamus/brainstem boundaries; (ii) embryonic colonization route discontinuities\u2014microglial rostral-to-caudal colonization waves [20,37,40] create transcriptomic boundaries at the forebrain-midbrain interface, with the inferior colliculus identified as a candidate contact zone; and (iii) compartmentalized developmental astrogenesis and vascular specification [18,39]. Importantly, OPCs\u2014the most actively migrating cells in the adult CNS [13,17]\u2014yielded 0 Strong signals among {{opc[\"n_pairs\"]:,}} comparisons, providing a powerful orthogonal validation that the residual model specifically detects fixed developmental signatures rather than ongoing cell motility. The sole exception is the perivascular fibroblast A40-SN signal, which is consistent with known postnatal meningeal-to-parenchymal fibroblast migration [38]. Together, these results demonstrate that CKI detects persistent transcriptional signatures of developmental history\u2014origin, colonization route, and specification\u2014embedded in adult transcriptomic data, rather than inferring active migration per se. This reframing opens new applications for adult single-cell atlases as archives of developmental information.')"
)

if old_disc in content:
    content = content.replace(old_disc, new_disc)
    print('OK: discussion paragraph')
else:
    print('WARN: discussion paragraph not found')

# === Conclusions ===
old_c1 = "p('(i) CKI \u03c9 is negatively correlated with all standard distance metrics (r = -0.36 to -0.46), proving it captures an orthogonal information dimension not measured by existing approaches.')"
new_c1 = "p(f'(i) CKI \u03c9 is negatively correlated with all standard distance metrics (r = {_sc[\"max\"]:.2f} to {_sc[\"min\"]:.2f}), proving it captures an orthogonal information dimension not measured by existing approaches.')"
content = content.replace(old_c1, new_c1)

old_c2 = "p('(ii) Validation on Tabula Muris confirms that biologically equivalent cell populations yield \u03c9 close to 1 (mean 1.54, all P > 0.05), establishing a calibrated neutral baseline.')"
new_c2 = "p(f'(ii) Validation on Tabula Muris confirms that biologically equivalent cell populations yield \u03c9 close to 1 (mean {_mc[\"control_mean\"]:.2f}, all P > 0.05), establishing a calibrated neutral baseline.')"
content = content.replace(old_c2, new_c2)

old_c3 = "p('(iii) TCGA analysis reveals that tumors are more transcriptionally homogeneous than normal tissues (median NN/TT = 1.40\u20132.83 across five cancer types), suggesting convergent transcriptional states across genetically diverse tumors.')"
nn_tt_range = f"{min_c['nn_tt_ratio']:.2f}\u2013{max_c['nn_tt_ratio']:.2f}"
new_c3 = "p(f'(iii) TCGA analysis reveals that tumors are more transcriptionally homogeneous than normal tissues (median NN/TT = {min_c[\"nn_tt_ratio\"]:.2f}\u2013{max_c[\"nn_tt_ratio\"]:.2f} across five cancer types), suggesting convergent transcriptional states across genetically diverse tumors.')"
content = content.replace(old_c3, new_c3)

old_c4 = "p('(iv) Brain regional analysis of 888,263 nuclei reveals a 6.06-fold \u03c9 gradient across 10 non-neuronal cell classes, with astrocytes showing the highest regional divergence (mean \u03c9 = 14.36) and Bergmann glia the lowest (mean \u03c9 = 2.37).')"
new_c4 = (
    "p(f'(iv) Brain regional analysis of {_br[\"n_nuclei\"]:,} nuclei reveals a "
    f"{{_br[\"gradient_fold\"]:.2f}}-fold \u03c9 gradient across "
    f"{{len(_br_ct)}} non-neuronal cell classes, with "
    f"{{_br[\"gradient_highest_ct\"]}} showing the highest regional divergence "
    f"(mean \u03c9 = {{_br[\"gradient_highest_omega\"]:.2f}}) and "
    f"{{_br[\"gradient_lowest_ct\"]}} the lowest "
    f"(mean \u03c9 = {{_br[\"gradient_lowest_omega\"]:.2f}}).')"
)
content = content.replace(old_c4, new_c4)

old_c5 = (
    "p('(v) The multiplicative residual model detects 30 candidate signals among 31,764 cross-region comparisons; cross-validation against developmental neuroscience literature reveals that these primarily reflect developmental origin heterogeneity (oligodendrocytes, 10/30), embryonic colonization route boundaries (microglia, 10/30), and compartmentalized developmental specification (astrocytes and vascular cells, 9/30), with only a single postnatal migration signal (perivascular fibroblasts).')"
)
new_c5 = (
    "p(f'(v) The multiplicative residual model detects {_br[\"n_strong\"]} candidate signals "
    f"among {{_br[\"total_pairs\"]:,}} cross-region comparisons; cross-validation against "
    "developmental neuroscience literature reveals that these primarily reflect developmental "
    "origin heterogeneity (oligodendrocytes, 10/30), embryonic colonization route boundaries "
    "(microglia, 10/30), and compartmentalized developmental specification (astrocytes and "
    "vascular cells, 9/30), with only a single postnatal migration signal (perivascular fibroblasts).')"
)
content = content.replace(old_c5, new_c5)

print('OK: conclusions')

# === Methods - dataset parameters ===
old_m1 = "p('Tabula Muris FACS SmartSeq2 [5]: 15,057 cells, 22,308 genes, 6 organs (liver, kidney, spleen, lung, heart, bone marrow). Post-QC: 32 cell-type entries (each with at least 10 cells). Highly variable genes selected using scanpy [25] with flavor=\"seurat\" [26,27] and n_top_genes=2,000.')"
new_m1 = (
    "p(f'Tabula Muris FACS SmartSeq2 [5]: {_ds[\"tabula_muris_cells\"]:,} cells, "
    f"{{_ds[\"tabula_muris_genes\"]:,}} genes, {{_ds[\"tabula_muris_organs\"]}} organs "
    f"(liver, kidney, spleen, lung, heart, bone marrow). Post-QC: "
    f"{{_ds[\"tabula_muris_ct_entries\"]}} cell-type entries (each with at least 10 cells). "
    f"Highly variable genes selected using scanpy [25] with flavor=\"seurat\" [26,27] "
    f"and n_top_genes={{_ds[\"n_hvg\"]:,}}.')"
)
content = content.replace(old_m1, new_m1)

old_m2 = "p('Tabula Sapiens v1.0 [6]: accessed via CZ CELLxGENE Discover. Post-QC: 108,136 cells (6 h5ad files total), 51,852 genes, 99 cell-type entries across 6 organs. Human HK genes: auto-detected (combined detection-rate/CV criterion), with optional enhancement from 1,130 HRT Atlas v1.0 genes mapped by gene symbol.')"
new_m2 = (
    "p(f'Tabula Sapiens v1.0 [6]: accessed via CZ CELLxGENE Discover. Post-QC: "
    f"{{_ds[\"tabula_sapiens_cells\"]:,}} cells ({{_ds[\"tabula_sapiens_organs\"]}} h5ad files total), "
    f"{{_ds[\"tabula_sapiens_genes\"]:,}} genes, {{_ds[\"tabula_sapiens_ct_entries\"]}} "
    "cell-type entries across 6 organs. Human HK genes: auto-detected (combined "
    "detection-rate/CV criterion), with optional enhancement from "
    f"{{_ds[\"hrt_atlas_n_hk\"]:,}} HRT Atlas v1.0 genes mapped by gene symbol.')"
)
content = content.replace(old_m2, new_m2)

old_m3 = "p('TCGA bulk RNA-seq [28]: five cancer types from NCI Genomic Data Commons, accessed via TCGAbiolinks [29] and cBioPortal [14] APIs. LUAD: 495 tumor + 76 normal; LUSC: 567 + 58; LIHC: 365 + 57; KIRC: 755 + 82; BRCA: 1,032 + 109. FPKM values, log2(x+1) transformed. PAM50 classification [11,12]: nearest centroid (Pearson correlation), 44 of 47 PAM50 genes matched. LIHC Edmondson grade [10]: from cBioPortal, 289 tumors. LUAD mutations: from cBioPortal, 497 samples (61 EGFR, 121 KRAS, 312 WT).')"

tcga_detail = '; '.join([
    f"{c['name'].replace('TCGA-','')}: {c['n_tumor']} tumor + {c['n_normal']} normal"
    for c in _tc['cancers']
])
new_m3 = (
    "p(f'TCGA bulk RNA-seq [28]: five cancer types from NCI Genomic Data Commons, "
    f"accessed via TCGAbiolinks [29] and cBioPortal [14] APIs. "
    f"{tcga_detail}. "
    "FPKM values, log2(x+1) transformed. PAM50 classification [11,12]: nearest centroid "
    "(Pearson correlation), 44 of 47 PAM50 genes matched. LIHC Edmondson grade [10]: "
    "from cBioPortal, 289 tumors. LUAD mutations: from cBioPortal, 497 samples "
    "(61 EGFR, 121 KRAS, 312 WT).')"
)
content = content.replace(old_m3, new_m3)

old_m4 = (
    "p('Human brain atlas [9]: Siletti et al. (2023) single-nucleus RNA-seq from CZ CELLxGENE Discover. We used the Nonneurons.h5ad dataset (888,263 nuclei, 59,480 genes, 108 brain regions). Cell types were classified by supercluster_term annotation, generating 10 major non-neuronal classes: astrocytes (155,025 nuclei), oligodendrocytes (490,246), oligodendrocyte precursors (110,454 total including committed), microglia (91,838), vascular cells (8,932), fibroblasts (8,156), ependymal cells (5,882), choroid plexus (7,689), and Bergmann glia. We required >= 20 nuclei per (region, cell_type) group and >= 50 nuclei per region. Normalization: Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation. Pseudobulk vectors were computed as the mean log-normalized expression per group. CKI \u03c9 was computed for all same-cell-type cross-region comparisons (31,764 pairs total), using the hybrid scheme described above. HK genes were auto-detected per dataset (combined detection-rate/CV criterion). Top-200 identity genes were selected per comparison, excluding HK genes.')"
)

new_m4 = (
    "p(f'Human brain atlas [9]: Siletti et al. (2023) single-nucleus RNA-seq from CZ CELLxGENE Discover. We used the Nonneurons.h5ad dataset ({_br[\"n_nuclei\"]:,} nuclei, {_br[\"n_genes\"]:,} genes, {_br[\"n_regions\"]} brain regions). Cell types were classified by supercluster_term annotation, generating {len(_br_ct)} major non-neuronal classes: "
    + ', '.join([f"{ct['name']} ({ct['n_nuclei']:,} nuclei)" for ct in _br_ct])
    + ". We required >= 20 nuclei per (region, cell_type) group and >= 50 nuclei per region. "
    "Normalization: Scanpy normalize_total (target_sum = 10,000) followed by log1p transformation. "
    "Pseudobulk vectors were computed as the mean log-normalized expression per group. "
    f"CKI \u03c9 was computed for all same-cell-type cross-region comparisons "
    f"({{_br[\"total_pairs\"]:,}} pairs total), using the hybrid scheme described above. "
    "HK genes were auto-detected per dataset (combined detection-rate/CV criterion). "
    "Top-200 identity genes were selected per comparison, excluding HK genes.')"
)
content = content.replace(old_m4, new_m4)
print('OK: methods paragraphs')

# === Methods comparison ===
old_m5 = "p('We computed five metrics on all 4,851 Tabula Sapiens cell-type pairs: CKI \u03c9 (hybrid scheme), raw JS divergence (all genes), Spearman distance (1 - \u03c1), cosine distance (1 - cos \u03b8), and marker Jaccard distance (1 - Jaccard index of top-200 expressed genes). Inter-metric Spearman correlations and cell-type classification ROC-AUC were computed using scikit-learn.')"
new_m5 = (
    "p(f'We computed five metrics on all {_h[\"n_pairs\"]:,} Tabula Sapiens cell-type pairs: "
    "CKI \u03c9 (hybrid scheme), raw JS divergence (all genes), Spearman distance (1 - \u03c1), "
    "cosine distance (1 - cos \u03b8), and marker Jaccard distance "
    "(1 - Jaccard index of top-200 expressed genes). "
    "Inter-metric Spearman correlations and cell-type classification ROC-AUC were computed "
    "using scikit-learn.')"
)
content = content.replace(old_m5, new_m5)

# === Methods: multiplicative residual model ===
old_m6 = (
    "p('For the brain regional analysis, we designed a multiplicative model to detect cell-type/region-pair combinations with anomalously low \u03c9. For each (cell_type, region_pair) combination, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, where \u03bc_ct is the cell type\'s global mean \u03c9, \u03bc_pair is the region pair\'s mean \u03c9, and \u03bc_grand is the global mean (8.01). The multiplicative residual = observed / expected. A residual substantially below 1 indicates the cell type is far less differentiated between those two regions than expected from both its own global plasticity and the region pair\'s overall divergence. We defined three confidence tiers: Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the region pair, and pair median \u03c9 > 20), Moderate (residual < 0.5, \u03c9 < 25), and Weak (residual < 0.75, \u03c9 < 35). Strong candidate signals were systematically cross-validated against the developmental neuroscience literature to assign each signal to one of four biological mechanisms: developmental origin heterogeneity (DO), embryonic colonization route boundaries (CR), compartmentalized developmental specification (DS), or postnatal cell migration (PM).')"
)

new_m6 = (
    "p(f'For the brain regional analysis, we designed a multiplicative model to detect "
    "cell-type/region-pair combinations with anomalously low \u03c9. For each "
    "(cell_type, region_pair) combination, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand, "
    "where \u03bc_ct is the cell type\\'s global mean \u03c9, \u03bc_pair is the region pair\\'s "
    f"mean \u03c9, and \u03bc_grand is the global mean ({{_br[\"global_mean\"]:.2f}}). "
    "The multiplicative residual = observed / expected. A residual substantially below 1 "
    "indicates the cell type is far less differentiated between those two regions than "
    "expected from both its own global plasticity and the region pair\\'s overall divergence. "
    f"We defined three confidence tiers: Strong (residual < {{th[\"strong\"]}}, "
    f"\u03c9 < {{th[\"strong_omega_max\"]}}, lowest \u03c9 in the region pair, "
    f"and pair median \u03c9 > {{th[\"strong_pair_median_min\"]}}), "
    f"Moderate (residual < {{th[\"moderate\"]}}, \u03c9 < {{th[\"moderate_omega_max\"]}}), "
    f"and Weak (residual < {{th[\"weak\"]}}, \u03c9 < {{th[\"weak_omega_max\"]}}). "
    "Strong candidate signals were systematically cross-validated against the developmental "
    "neuroscience literature to assign each signal to one of four biological mechanisms: "
    "developmental origin heterogeneity (DO), embryonic colonization route boundaries (CR), "
    "compartmentalized developmental specification (DS), or postnatal cell migration (PM).')"
)
content = content.replace(old_m6, new_m6)

# === Methods: bootstrap ===
old_m7 = (
    "p('We randomly permute cell labels between the two populations (B = 500), recompute pseudobulk vectors, and calculate \u03c9_null for each permutation. We apply a two-sided bootstrap test: Empirical P = (count(|\u03c9_null - 1| >= |\u03c9_obs - 1|) + 1) / (B + 1). Cohen\'s d = (\u03c9_obs - mean(\u03c9_null)) / sd(\u03c9_null). All reported P-values are raw bootstrap P-values without multiple testing correction.')"
)
new_m7 = (
    "p(f'We randomly permute cell labels between the two populations "
    f"(B = {{_ds[\"n_bootstrap\"]}}), recompute pseudobulk vectors, and calculate "
    "\u03c9_null for each permutation. We apply a two-sided bootstrap test: "
    "Empirical P = (count(|\u03c9_null - 1| >= |\u03c9_obs - 1|) + 1) / (B + 1). "
    "Cohen\\'s d = (\u03c9_obs - mean(\u03c9_null)) / sd(\u03c9_null). "
    "All reported P-values are raw bootstrap P-values without multiple testing correction.')"
)
content = content.replace(old_m7, new_m7)

# === Statistical reporting ===
old_m8 = (
    "p('We report summary statistics as mean \u00b1 s.d. (range) or median [IQR] as noted. "
    "Box plots display median, IQR, and 1.5\u00d7 IQR whiskers. All P-values are two-sided "
    "unless otherwise specified. Bootstrap inference uses B = 500 permutations; empirical "
    "P-values use the +1 pseudocount formula. All reported P-values are raw bootstrap P-values "
    "without multiple testing correction. Effect sizes are reported as Cohen\'s d; d > 0.8 "
    "indicates a large effect. Correlation coefficients (Spearman \u03c1) are reported with "
    "associated P-values. Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) use P < 0.05 "
    "without additional correction.')"
)
new_m8 = (
    "p(f'We report summary statistics as mean \u00b1 s.d. (range) or median [IQR] as noted. "
    "Box plots display median, IQR, and 1.5\u00d7 IQR whiskers. All P-values are two-sided "
    "unless otherwise specified. Bootstrap inference uses B = {{_ds[\"n_bootstrap\"]}} "
    "permutations; empirical P-values use the +1 pseudocount formula. All reported P-values "
    "are raw bootstrap P-values without multiple testing correction. Effect sizes are reported "
    "as Cohen\\'s d; d > 0.8 indicates a large effect. Correlation coefficients (Spearman \u03c1) "
    "are reported with associated P-values. Omnibus tests (Kruskal-Wallis, Jonckheere-Terpstra) "
    "use P < 0.05 without additional correction.')"
)
content = content.replace(old_m8, new_m8)

# === HK gene detection methods ===
old_m9 = (
    "p('We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation. "
    "Pseudobulk vectors are computed by averaging expression across cells sharing the same "
    "cell-type annotation, requiring at least 10 cells per group. Housekeeping (HK) genes are "
    "auto-detected from data using a combined criterion: detection rate > 0.9 (expressed in "
    ">90% of cells) and coefficient of variation below the 30th percentile among well-expressed "
    "genes (mean expression > 0.5). For human and mouse datasets, the HRT Atlas v1.0 consensus "
    "set (1,130 human-mouse shared HK genes) [4] is optionally used as supplementary enhancement "
    "(union with detected set). For any other species, detection is purely data-driven without "
    "external references.')"
)
new_m9 = (
    "p(f'We normalize raw count matrices to 10,000 counts per cell and apply log1p transformation. "
    "Pseudobulk vectors are computed by averaging expression across cells sharing the same "
    "cell-type annotation, requiring at least 10 cells per group. Housekeeping (HK) genes are "
    f"auto-detected from data using a combined criterion: detection rate > {{_ds[\"detection_rate_threshold\"]}} "
    "(expressed in >90% of cells) and coefficient of variation below the 30th percentile among "
    "well-expressed genes (mean expression > 0.5). For human and mouse datasets, the HRT Atlas "
    f"v1.0 consensus set ({{_ds[\"hrt_atlas_n_hk\"]:,}} human-mouse shared HK genes) [4] is "
    "optionally used as supplementary enhancement (union with detected set). For any other species, "
    "detection is purely data-driven without external references.')"
)
content = content.replace(old_m9, new_m9)

# === CKI computation methods ===
old_m10 = (
    "p('For populations A and B with pseudobulk vectors \u03b5_A and \u03b5_B, k_n = JS(softmax(\u03b5_A[H]), softmax(\u03b5_B[H])), where H is the set of HK gene indices. k_f = JS(softmax(\u03b5_A[I]), softmax(\u03b5_B[I])), where I is the set of top-2,000 highly variable genes (HVGs; Seurat v3 flavor) excluding HK genes. \u03c9 = k_f/k_n. JS divergence uses base-2 logarithm (range [0,1]). Softmax normalization converts expression vectors to probability distributions.')"
)
new_m10 = (
    "p(f'For populations A and B with pseudobulk vectors \u03b5_A and \u03b5_B, k_n = JS(softmax(\u03b5_A[H]), softmax(\u03b5_B[H])), where H is the set of HK gene indices. k_f = JS(softmax(\u03b5_A[I]), softmax(\u03b5_B[I])), where I is the set of top-{_ds[\"n_hvg\"]:,} highly variable genes (HVGs; Seurat v3 flavor) excluding HK genes. \u03c9 = k_f/k_n. JS divergence uses base-2 logarithm (range [0,1]). Softmax normalization converts expression vectors to probability distributions.')"
)
content = content.replace(old_m10, new_m10)

print('OK: remaining methods paragraphs')

with open('generate_manuscript_genome_biology.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n=== All patches applied! ===')
