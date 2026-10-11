# Note 20 draft (diagnostic numbers marked [[...]])

Heading: 'Supplementary Note 20: A Scoped Theoretical Framework for \u03c9'

P1 (motivation + model):
'This note makes precise what \u03c9 estimates, under which conditions, and with what
error, connecting the operational algorithm (Methods) to the interpretation used
throughout the main text. We work with the brain-order normalization
p = softmax(log1p(c)) of a pseudobulk count vector c over a gene panel, and adopt a
generative factor model for the log-expression of population g:
log x_g = \u03c3_g + \u03b2_g + \u03c6_g, where \u03c3_g is a global scale
(sequencing depth and capture efficiency), \u03b2_g a background factor (technical
variation plus neutral drift, shared across gene panels), and \u03c6_g a functional
factor with \u03c6_{g,i} = 0 outside the genes whose regulation actually differs.
All statements below are scoped to this model class; we make no claim outside it.'

P2 (Lemma 1):
'Lemma 1 (exact cancellation of global scale). Under the log-softmax normalization,
multiplying a population\u2019s counts by any positive constant leaves its probability
vector unchanged: norm(c \u00b7 x) = norm(x), because the additive shift in log space
cancels between numerator and denominator. Global scale factors \u03c3_g therefore
contribute exactly nothing to k_n, k_f, or \u03c9. The implemented log1p transform
deviates from a pure logarithm only by terms of order 1/x per gene, which at
pseudobulk count scales (medians \u226b 10) induces relative deviations below
[[1e-4]]; depth differences between populations are thus removed by construction,
not by approximation, up to this negligible correction (cf. the twofold-depth
robustness scenario of Supplementary Note 1).'

P3 (Lemma 2):
'Lemma 2 (second-order expansion of JS with explicit remainder). Let p and
q = p + \u03b4 be probability vectors on a panel of d genes. Because the Shannon
entropy is coordinate-separable, a third-order Taylor expansion of
JS(p, q) = H((p+q)/2) \u2212 (H(p)+H(q))/2 (base-2) gives
JS(p, q) = (1/(8 ln 2)) \u03a3_i \u03b4_i\u00b2/p_i + R, with the exact Lagrange
remainder |R| \u2264 (5/(48 ln 2)) \u03a3_i |\u03b4_i|\u00b3/(p_i \u2212 |\u03b4_i|)_+\u00b2.
The linear term vanishes pointwise (no \u03a3\u03b4 = 0 assumption is needed).
The quadratic form is the chi-squared-type energy of the displacement \u03b4
weighted by the inverse probability, and the remainder is controlled whenever the
relative displacement |\u03b4_i|/p_i is small (condition C1). Diagnostic
(notebooks/85_theory_diagnostics.py; Supplementary Fig. [[19]]): on [[N]] real
pairs (Tabula Sapiens cross-organ populations and split-half nulls; Siletti brain
cross-region pairs and within-region split-half nulls), the median relative error
|JS \u2212 Q|/JS was [[x]]% for the HK panel (k_n scale) and [[y]]% for the
pair-specific top-200 panel (k_f scale), with 90th percentiles [[x90]]% and
[[y90]]%; the cubic-to-quadratic ratio \u03a3|\u03b4|\u00b3/p\u00b2 / \u03a3\u03b4\u00b2/p
mediated [[z]]. The expansion is therefore quantitative for k_n and [[qualitative/
quantitative]] for k_f, scoping the framework accordingly.'

P4 (conditions + Proposition 3):
'Conditions and estimand. We make four conditions explicit:
C1 (quadratic regime): max_i |\u03b4_i|/p_i is small on both panels, so |R| is
negligible against the quadratic term (Lemma 2; verified above).
C2 (shared background energy): the background factor \u03b2_g is panel-exchangeable,
so the per-gene background energy estimated on the HK panel approximates that on the
functional panel. On split-half null pairs, the per-gene energy
e_i = \u03b4_i\u00b2/p_i on the top-200 panel had median ratio [[r]] (10\u201390%
[[r10\u2013r90]]) to the HK-panel mean energy ([[N]] null pairs; Supplementary
Fig. [[19]]), supporting C2 as an approximation with [[X]]-fold spread.
C3 (stable functional panel): the pair-specific top-200 panel is not noise-driven;
quantified by the leave-pair-out ablation of Supplementary Note 9 (circularity
inflation [[..]]).
C4 (adequate count depth): multinomial sampling contributes
(d \u2212 1)/(4N ln 2) to JS, below the background energy at the pseudobulk depths
used here (Supplementary Note 16; notebooks/84).
Proposition 3 (estimand). Under C1\u2013C4 and the generative model,
k_n \u2248 (1/(8 ln 2)) E_b and k_f \u2248 (1/(8 ln 2)) (E_f + E_b), where
E_b = \u03a3_i \u03b2_i\u00b2/p_i is the background displacement energy and
E_f = \u03a3_i \u03c6_i\u00b2/p_i the functional displacement energy on the panel.
Consequently \u03c9 = k_f/k_n = 1 + E_f/E_b + \u03b5, with
|\u03b5| \u2264 |\u03c1_f| + |\u03c1_n| + higher-order terms, where
\u03c1_\u00b7 = R_\u00b7/Q_\u00b7 is bounded by Lemma 2 (and by C4 for the sampling
contribution). In words: \u03c9 \u2212 1 estimates the ratio of functional to
background displacement energy on the probability simplex\u2014this is the precise
biological quantity \u03c9 corresponds to within the model class. A unit \u03c9 has
no absolute meaning; a doubling of \u03c9 \u2212 1 means a doubling of functional
signal relative to the pair\u2019s own background.'

P5 (Proposition 4 monotonicity):
'Proposition 4 (local monotonicity, global saturation). In the quadratic regime,
scaling the functional factor \u03c6 \u2192 \u03bb\u03c6 (\u03bb > 1) with the
background fixed scales E_f \u2192 \u03bb\u00b2E_f while E_b is unchanged, so
\u03c9 \u2212 1 increases strictly and approximately quadratically in \u03bb; the
monotone direction \u2202\u03c9/\u2202E_f > 0 is guaranteed wherever C1 holds.
Globally this cannot persist: JS is bounded above by 1 bit, so \u03c9 saturates and
the mapping \u03c9 \u2212 1 \u2248 E_f/E_b is local, not global. Ground-truth check
(Supplementary Note 1 factorial grid): at zero background drift, \u03c9 increased
monotonically with the injected functional shift \u03b4 over \u03b4 = 0.125\u20132
(Spearman \u03c1 = [[rho]]), and \u03c9 \u2212 1 was approximately linear in
[[2^{2\u03b4} \u2212 1 / \u03b4]] up to \u03b4 = [[..]] before saturating; k_f rose
with \u03b4 but also with background drift \u03b7 (\u03c1 = [[..]]), while \u03c9
stayed flat under pure drift (\u03b4 = 0; \u03c1 = [[..]]), empirically matching
the estimand structure.'

P6 (Proposition 5 calibration):
'Proposition 5 (calibration bias, delta method). The calibrated statistic
\u03c9_cal = \u03c9/\u03c9_0 inherits ratio-estimator bias of order
Var(k_n)/\u03bc_n\u00b2: E[\u03c9] \u2248 (\u03bc_f/\u03bc_n)(1 + CV_n\u00b2
\u2212 \u03c1 CV_f CV_n), with CV the per-pair coefficient of variation and
\u03c1 the k_f\u2013k_n correlation. From the split-half products (Supplementary
Note 3), CV_n \u2248 [[..]] and \u03c1 \u2248 [[..]], so the second-order bias is
[[..]]%\u2014negligible against the effects reported, and dominated by the
between-population spread of the calibration denominator, which the joint bootstrap
of Supplementary Note 3 propagates.'

P7 (§E added value, Q2):
'What the HK denominator adds. Three distinct gains are identifiable.
(i) Identifiability: k_f alone estimates the sum E_f + E_b; functional and
background energy cannot be separated from k_f by any calibration that does not
measure E_b independently. The HK panel supplies that independent measurement,
making the ratio E_f/E_b identifiable.
(ii) Studentization: a valid per-pair null for k_f would have to condition on the
pair\u2019s own background magnitude E_b, which is unobservable; dividing by k_n
yields a statistic whose null is approximately ancillary to E_b, so one global
calibration is legitimate\u2014the same logic by which dividing by the sample
standard deviation turns a mean difference into a t-statistic. Empirically, the
cross-class dispersion of the split-half null is [[..]]-fold wider for k_f than for
\u03c9 (CV [[..]] versus [[..]] across [[..]] classes; max/min [[..]] versus
[[..]]), i.e. the \u03c9 null is substantially more portable across cell classes.
(iii) Measured error rates: under injected neutral drift (Supplementary Notes 1, 6),
k_f-only false-positive rates were 0.81\u20131.00 versus 0.00\u20130.067 for \u03c9,
and the TCGA reversal (Supplementary Note 10) is a k_n phenomenon invisible to any
k_f-only analysis. Dividing by the HK divergence is therefore not cosmetic: it
converts an unidentifiable, background-scale-dependent statistic into an
identifiable, approximately self-normalized one.'

P8 (scope statement):
'Scope. Lemma 1 is exact for the stated normalization; Lemma 2 is exact mathematics
with an explicit remainder; Propositions 3\u20135 are model-relative and conditional
on C1\u2013C4, each of which is checked on real data above or in the referenced
notes. Where a condition is only approximately met (C2 at [[X]]-fold spread; C1 for
the k_f panel at [[y]]% error), the corresponding statements are read as
approximations, and the main-text claims relying on them are phrased accordingly.'
