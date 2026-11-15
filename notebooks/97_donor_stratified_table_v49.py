"""
v49.13 A7: donor-stratified null transparency table (per-class P values,
shufflable-library counts, and identity-permutation share).
============================================================================
Reviewer: R5-N6. The manuscript reports only "the same 3 of 10 classes survive
the donor-stratified null". This script produces the per-class table:
  (i)   donor-stratified P value (from results/v38_donor_stratified_null.csv);
  (ii)  number of shufflable libraries per class and the per-donor library
        counts with their region spread;
  (iii) the exact probability that a random donor-stratified block shuffle
        returns the identity assignment, computed analytically:
        for donor d with m_d libraries spread over regions as counts
        {n_{d,r}}, the within-donor permutation returns the unchanged label
        array with probability prod_r n_{d,r}! / m_d!; the class-level
        identity share is the product over donors. (The permutation engine
        in notebooks/48_donor_stratified_null.py retains identity draws as
        valid draws, so this share is the exact floor on the attainable
        one-sided P value.)

Input : data/brain/Nonneurons.h5ad (obs only, no matrix access)
        results/v38_donor_stratified_null.csv
Output: results/nc49_donor_stratified_table.csv
Seed  : none (deterministic analytic calculation).
"""
from math import factorial
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
BRAIN = ROOT / "data" / "brain" / "Nonneurons.h5ad"
STRAT = ROOT / "results" / "v38_donor_stratified_null.csv"
OUT = ROOT / "results" / "nc49_donor_stratified_table.csv"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

strat = pd.read_csv(STRAT)

f = h5py.File(BRAIN_FILE := BRAIN, "r")
obs = f["obs"]

def read_codes(name):
    g = obs[name]
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    codes = g["codes"][:]
    return np.array(cats)[codes], np.array(cats)

ct_names, _ = read_codes("supercluster_term")
roi_names, _ = read_codes("roi")
donor_names, _ = read_codes("donor_id")
sample_names, _ = read_codes("sample_id")
f.close()

df = pd.DataFrame({"ct": ct_names, "roi": roi_names,
                   "donor": donor_names, "lib": sample_names})

rows = []
for _, s in strat.iterrows():
    ct = s.cell_type
    sub = df[df.ct == ct]
    # blocks = libraries (sample_id); shufflable = libraries in donors with
    # >1 library (single-library donors are fixed)
    lib_donor = sub.groupby("lib").donor.first()
    donor_counts = lib_donor.value_counts()
    n_libs = len(lib_donor)
    single_lib_donors = int((donor_counts == 1).sum())
    # identity probability
    log_p = 0.0
    for d, m in donor_counts.items():
        regs = sub[sub.donor == d].groupby("lib").roi.first().value_counts()
        # probability that a random permutation of this donor's label array
        # is unchanged = prod_r n_r! / m!
        import math
        log_p += sum(math.log(factorial(int(n))) for n in regs.values)
        log_p -= math.log(factorial(int(m)))
    identity_share = float(np.exp(log_p))
    rows.append({
        "cell_type": ct,
        "n_regions": int(s.n_regions),
        "n_pairs": int(s.n_pairs),
        "n_libraries": n_libs,
        "n_donors": int(s.n_donors),
        "n_shufflable_libraries": int(s.n_shufflable_blocks),
        "n_single_library_donors_fixed": single_lib_donors,
        "donor_library_counts": "; ".join(f"{d}:{m}" for d, m in donor_counts.items()),
        "identity_permutation_share": identity_share,
        "stratified_P": s.strat_p_value,
        "stratified_q_BH": s.strat_q_BH,
        "free_P": s.free_p_value,
        "free_q_BH": s.free_q_BH,
    })

out = pd.DataFrame(rows).sort_values("stratified_P")
out.to_csv(OUT, index=False)
log(out[["cell_type", "n_shufflable_libraries", "n_donors",
         "identity_permutation_share", "stratified_P", "stratified_q_BH"]]
    .to_string(index=False))
log("")
log("identity share is the exact analytic probability that the donor-stratified")
log("shuffle returns the observed assignment; it floors the one-sided P value.")
n_survive = int((out.stratified_q_BH < 0.05).sum())
log(f"classes surviving donor-stratified BH correction: {n_survive}/10")
log("saved: " + str(OUT))
print("DONE")
