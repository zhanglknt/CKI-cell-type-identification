"""Regression assertions against the manuscript's authoritative result files.

Guards against silent regressions in the key numbers quoted by the paper
(brain class-level statistics, set-level enrichment, internal baselines,
TCGA ratios, mouse calibration). The authoritative files live under
``results/`` (repo root) and are mirrored byte-identically in
``CKI_Reproducibility_Package/reference_results/``; either location
satisfies these tests. Skipped automatically when no results directory
is present (e.g. a fresh clone before running the pipeline).
"""

import json
import re
from pathlib import Path

import pytest

RESULTS = Path(__file__).resolve().parent.parent / "results"
MIRROR = (
    Path(__file__).resolve().parent.parent
    / "CKI_Reproducibility_Package" / "reference_results"
)


def _find(name: str) -> Path:
    for base in (RESULTS, MIRROR):
        p = base / name
        if p.exists():
            return p
    pytest.skip(f"result file not found: {name}")


def test_brain_classlevel_astrocyte():
    """Astrocyte omega_mean 82.75 +/- 44.98, P=9.99e-4, SES=6.49."""
    import pandas as pd

    df = pd.read_csv(_find("brain_bs_null_ct_test.csv"))
    astro = df[df["cell_type"] == "Astrocyte"].iloc[0]
    assert astro["omega_mean"] == pytest.approx(82.75, abs=0.01)
    assert astro["omega_std"] == pytest.approx(44.98, abs=0.01)
    assert astro["p_value"] == pytest.approx(9.99e-4, rel=0.01)
    assert astro["SES"] == pytest.approx(6.49, abs=0.01)
    assert int(astro["n_pairs"]) == 5778


def test_brain_null_summary_tiers():
    """Strong tier n=39 with 31 raw P<0.05; 31,764 total pairs; min q 0.5202."""
    txt = _find("brain_bs_null_summary.txt").read_text()
    m = re.search(r"Strong\s+n=\s*(\d+).*p<0\.05:\s*(\d+)", txt)
    assert int(m.group(1)) == 39
    assert int(m.group(2)) == 31
    assert int(re.search(r"Total pairs = (\d+)", txt).group(1)) == 31764
    assert "q=0.5202" in txt


def test_brain_setlevel_enrichment():
    """S1: 79.5% vs 6.2%, hypergeometric P = 9.57e-31; CA trend z = 61.02."""
    import pandas as pd

    sl = pd.read_csv(_find("brain_setlevel_tests.csv")).set_index("test_id")
    assert sl.loc["S1_global_enrichment", "effect"] == pytest.approx(0.7949, abs=0.0005)
    assert sl.loc["S1_global_enrichment", "p_value"] == pytest.approx(9.57e-31, rel=0.01)
    assert sl.loc["S2_dose_response_CA", "effect"] == pytest.approx(61.02, abs=0.05)


def test_internal_baselines():
    """Brain split-half 9.73; Tabula Sapiens split-half 7.67."""
    brain = _find("reviewer_brain_splithalf_summary.txt").read_text()
    assert float(
        re.search(r"brain_split_half_mean_omega\s+([\d.]+)", brain).group(1)
    ) == pytest.approx(9.73, abs=0.005)
    ts = _find("reviewer_ts_splithalf_summary.txt").read_text()
    assert float(
        re.search(r"ts_split_half_mean_omega\s+([\d.]+)", ts).group(1)
    ) == pytest.approx(7.67, abs=0.005)


def test_mouse_calibration_categories():
    """Control mean 6.67 (n=6); S/D/X means 21.31 / 43.19 / 27.31."""
    import pandas as pd

    df = pd.read_csv(_find("mouse_pilot_v2_results.csv"))
    means = df.groupby("category")["omega"].mean()
    assert means["C_control"] == pytest.approx(6.67, abs=0.01)
    assert means["S_same_ct"] == pytest.approx(21.31, abs=0.01)
    assert means["D_diff_ct"] == pytest.approx(43.19, abs=0.01)
    assert means["X_cross"] == pytest.approx(27.31, abs=0.01)
    assert df["category"].value_counts().to_dict() == {
        "C_control": 6, "S_same_ct": 4, "D_diff_ct": 3, "X_cross": 2,
    }


def test_tcga_nn_tt_medians():
    """Median NN/TT omega ratios 1.23-2.32 across the five cancer types."""
    import pandas as pd

    df = pd.read_csv(_find("phase34_v2_summary.csv"))
    ratios = df["omega_NN_median"] / df["omega_TT_median"]
    assert ratios.min() == pytest.approx(1.233, abs=0.005)
    assert ratios.max() == pytest.approx(2.319, abs=0.005)


def test_kang_ifnb_demo_auc():
    """CD14+ monocytes: omega AUC 0.55 vs k_f AUC 0.98 (anchor boundary)."""
    kang = json.loads(_find("kang_ifnb_demo_summary.json").read_text())["cell_types"]
    cd14 = kang["CD14+ Monocytes"]
    assert cd14["auc_omega"] == pytest.approx(0.55, abs=0.005)
    assert cd14["auc_kf"] == pytest.approx(0.98, abs=0.005)
