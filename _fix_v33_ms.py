"""Fix v33 manuscript issues: m2, m8, m10, m11, m15, m17"""
import re

with open('generate_manuscript_nar.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# m2: CV 60% -> 52%
if 'CV \\u2248 60%' in content:
    content = content.replace('CV \\u2248 60%', 'CV \\u2248 52%')
    changes += 1
    print('m2: CV 60% -> 52%')

# m8: Abstract
if 'two statistically significant' in content:
    content = content.replace('two statistically significant', 'two with permutation support')
    changes += 1
    print('m8: Abstract fixed')

# m17: orthogonal -> complementary
# Current count: 3 (target: <=2)
ortho_count = content.count('orthogonal')
print(f'm17: orthogonal count before = {ortho_count}')
# Replace "orthogonal validation" in cross-organ paragraph
if 'orthogonal validation' in content:
    content = content.replace('orthogonal validation', 'complementary validation')
    changes += 1
    print('m17: orthogonal validation -> complementary validation')

# m10, m11, m15: Add limitations
idx_17th = content.find('Seventeenth,')
if idx_17th >= 0:
    end_17th = content.find("p('Future directions", idx_17th)
    
    # Find the end of the Seventeenth text (before the closing quote)
    # Look for the last period before end_17th
    m10_text = (" Eighteenth, the one-sided permutation test (H1: \\u03c9_obs > \\u03c9_null) "
                "does not detect functional constraint (\\u03c9_obs < \\u03c9_null); "
                "users investigating bidirectional hypotheses should employ two-sided "
                "permutation tests, available via the direction parameter in the CKI package.")
    
    m11_text = (" Nineteenth, the residual model permutation test (B = 10,000) reached "
                "the P-value floor (9.99 \\u00d7 10\\u207b\\u2075) for 36.3% of signals. "
                "An alternative interpretation is that the null distribution, constructed "
                "by shuffling cell-type labels within region pairs, is narrower than the "
                "true null because cell types differ in global plasticity; a null that "
                "accounts for cell-type-specific baseline plasticity could reduce the "
                "saturation rate, though constructing such a null would require modeling "
                "the covariance structure of \\u03c9 across cell types and region pairs.")
    
    m15_text = (" Twenty-first, the brain analysis was restricted to non-neuronal "
                "cell types because the supercluster_term annotation does not resolve "
                "neuronal subtype heterogeneity; this limits the generalizability of "
                "our brain regional findings to non-neuronal lineages and should be "
                "noted when interpreting the scope of our cross-region analysis.")
    
    insert_text = m10_text + m11_text + m15_text
    
    # Find the right insertion point: after "cross-scheme" text in Seventeenth
    before_close = content.rfind('cross-scheme transferability', idx_17th, end_17th)
    if before_close < 0:
        before_close = content.rfind('on their own data.', idx_17th, end_17th)
    
    if before_close > 0:
        # Find the period ending this section
        period_end = content.find('. ', before_close)
        if period_end > 0:
            content = content[:period_end+1] + insert_text + content[period_end+1:]
            changes += 3
            print('m10/m11/m15: Added Eighteenth, Nineteenth, Twenty-first limit')

print(f'Total changes: {changes}')

with open('generate_manuscript_nar.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')
