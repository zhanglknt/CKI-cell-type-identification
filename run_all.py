#!/usr/bin/env python
"""
run_all.py — Complete reproducibility pipeline for the CKI manuscript
(Nature Communications submission, v50; earlier revision rounds targeted
other journals, so some script/file names retain historical "gb"/"nar" tags).

Usage:
    python run_all.py              # Run everything (default)
    python run_all.py --dry-run     # Print execution plan without running
    python run_all.py --skip-tcga   # Skip TCGA (needs controlled-access data)
    python run_all.py --verify-only # Only run spot-check verification

Execution order (independent groups run in parallel):
    Phase 1 (independent, parallel):
        A (Tabula Muris FACS):  01b_hk, 01c_hk, 01_tissue, 02b, 02c, 03_full, 04_sweep
        B (Tabula Sapiens):     05_phase33_fixed
        C (TCGA):               06_phase34_v2, 07_clinical
        D (Brain):              07c_brain_siletti
        F (Method comparison):  13_phase35
    Phase 2 (permutation tests; depend on Phase 1):
        E: 08a_tcga (TCGA permutation), 08b_human_bootstrap_v2 (cell-level
           permutation; supersedes broken 08b_human_bootstrap_csv.py),
           08c_brain_bootstrap_v3 (pseudobulk-level permutation)
        Then, sequentially for brain: 08d_brain_blockshuffle_null ->
           08e_brain_blockshuffle_results (block-shuffle null; the
           authoritative source of all brain per-pair / cell-type statistics)
    Phase 3 (post-processing): precompute_figure_data, spot_check
    Phase 4 (Phase B upgrades):   09_phaseB, 09b_residual
    Phase 5 (Phase C methodological): 09c_phaseC
    Phase 6 (reviewer-fix & v40 statistical analyses; depend on 08d/08e
             and Phase 1 outputs):
        Brain (heavy):   41_within_donor, 42_kn_estimators,
                         46_fixed_panel_ablation, 48_donor_stratified_null
        Brain (CSV):     38_lineage_enrichment, 39_tier_sensitivity,
                         72_brain_setlevel_tests
        Split-half:      43_ts_splithalf, 44_fix_phaseB_cis
        Simulations:     45_groundtruth_simulation, 49_groundtruth_background2
        TCGA:            73_tcga_composition_check
    Phase 6b (v44 analyses): 85/86/87_tcga_*, 86_brain_downsample,
                             87_mouse_splithalf, 101_competitors
    Phase 6c (v45 analyses):  88_ratio_estimator, 89_cluster_boot,
                             90_nonhk_drift, 91_augur, 91b_augur_ovr
    Phase 6d (nc49 analyses): nc49_pilot_kang_techrep, nc49_brain_drift_ladder,
                             nc49_tcga_main, nc49_pilot_lihc_cox,
                             nc49_tcga_purity, nc49_tcga_luad_smoking,
                             nc49_tcga_kf_composition, nc49_agg_order_sensitivity,
                             nc49_lihc_cox_excc, 92-98_*_v49
    Phase 6e (nc50 analyses): nc50_brain_atlas_microglia
    Phase 6f (nc52 analyses, not yet wired into run_all): nc52_tcga_excc_main,
                             nc52_tcga_composition, nc52_lihc_cox_excc (R),
                             nc52_gtex_kn, nc52_tcga_deconv_feasibility,
                             nc52 brain gradient/quality scripts,
                             scripts/nc52_stats_resampling.py; see the
                             Reproducibility Guide Section 5.13 for commands
    Phase 7 (Figures):  30_genome_biology_figures, nc49_fig_drift_ladder (Fig. 3),
                        nc49_fig_tcga (Fig. 4), nc50_fig_microglia (Supp. Fig. 14)
    Phase 8 (Collect):  _collect_submission_figures

Note on verification: scripts/spot_check.py provides a quick numerical
sanity check only; the comprehensive verification of the submission
package is performed by 99_build_nc_v49.py.

Prerequisites:
    1. Install cki: pip install -e .
    2. Raw data in data/ (ts_human/, brain/, tcga/, FACS/, housekeeping/)
    3. Python 3.10+ with dependencies: numpy, scipy, scanpy, pandas, scikit-learn
"""

import sys
import os
import subprocess
import time
import argparse
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Config ---
ROOT = Path(__file__).resolve().parent
NOTEBOOKS = ROOT / "notebooks"
RESULTS = ROOT / "results"
PYTHON = sys.executable

# Ensure results/ exists
RESULTS.mkdir(exist_ok=True)

# --- Terminal colors ---
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def color(text, c):
    return f"{c}{text}{Color.RESET}"

def run_script(name, path, timeout_mins=30):
    """Run a single Python script and return (success, duration_sec, output)."""
    script = NOTEBOOKS / path
    if not script.exists():
        print(f"  {color('MISSING', Color.RED)}: {path}")
        return False, 0, f"File not found: {script}"

    t0 = time.time()
    try:
        result = subprocess.run(
            [PYTHON, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_mins * 60,
        )
        dt = time.time() - t0
        if result.returncode == 0:
            print(f"  {color('OK', Color.GREEN)}     {dt:.0f}s  {path}")
            return True, dt, result.stdout
        else:
            print(f"  {color('FAIL', Color.RED)}   {dt:.0f}s  {path}")
            if result.stderr:
                # Show last 5 lines of stderr
                lines = result.stderr.strip().split('\n')
                for line in lines[-5:]:
                    print(f"         {color(line, Color.RED)}")
            return False, dt, result.stderr
    except subprocess.TimeoutExpired:
        dt = time.time() - t0
        print(f"  {color('TIMEOUT', Color.YELLOW)} {dt:.0f}s  {path}")
        return False, dt, "Timeout"
    except Exception as e:
        dt = time.time() - t0
        print(f"  {color('ERROR', Color.RED)}   {dt:.0f}s  {path}: {e}")
        return False, dt, str(e)


def run_group(name, scripts, parallel=True, timeout_mins=30):
    """Run a group of scripts, optionally in parallel."""
    if not scripts:
        print(f"\n{color(f'[{name}] SKIPPED (no scripts selected)', Color.YELLOW)}")
        return True
    header = f"[{name}] ({len(scripts)} scripts)"
    print(f"\n{color(header, Color.BOLD + Color.CYAN)}")
    print("-" * 60)

    if parallel and len(scripts) > 1:
        with ThreadPoolExecutor(max_workers=min(len(scripts), 4)) as ex:
            futures = {
                ex.submit(run_script, label, path, timeout_mins): (label, path)
                for label, path in scripts
            }
            results = {}
            for f in as_completed(futures):
                label, path = futures[f]
                success, dt, _ = f.result()
                results[label] = success
        return all(results.values())
    else:
        all_ok = True
        for label, path in scripts:
            ok, _, _ = run_script(label, path, timeout_mins)
            if not ok:
                all_ok = False
        return all_ok


def verify_outputs(expected_files):
    """Check that expected output files exist."""
    missing = []
    for f in expected_files:
        if not (RESULTS / f).exists():
            missing.append(f)
    if missing:
        print(f"\n{color('MISSING OUTPUTS:', Color.YELLOW)}")
        for m in missing:
            print(f"  {m}")
    return len(missing) == 0


def main():
    parser = argparse.ArgumentParser(description="CKI reproducibility pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Print plan only")
    parser.add_argument("--skip-tcga", action="store_true", help="Skip TCGA (controlled-access)")
    parser.add_argument("--skip-brain", action="store_true", help="Skip brain (large file)")
    parser.add_argument("--verify-only", action="store_true", help="Only run spot-check")
    parser.add_argument("--sequential", action="store_true", help="Run all groups sequentially (no parallelism)")
    args = parser.parse_args()

    t_start = time.time()

    print(color("=" * 60, Color.BOLD))
    print(color("CKI — Reproducibility Pipeline (NC v50)", Color.BOLD))
    print(color("=" * 60, Color.BOLD))
    print(f"Root:      {ROOT}")
    print(f"Python:    {PYTHON}")
    print(f"Results:   {RESULTS}")
    print()

    # --- Step 0: Check prerequisites ---
    print(color("[Step 0] Checking prerequisites...", Color.BOLD + Color.CYAN))

    # Check cki package
    try:
        import cki
        print(f"  cki version: {cki.__version__}")
    except ImportError:
        print(f"  {color('ERROR: cki not installed. Run: pip install -e .', Color.RED)}")
        if not args.dry_run:
            sys.exit(1)

    # Check raw data
    data_checks = [
        (ROOT / "data" / "ts_human" / "TS_Liver.h5ad", "Tabula Sapiens Liver"),
        (ROOT / "data" / "brain" / "Nonneurons.h5ad", "Brain Nonneurons"),
        (ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz", "TCGA expression"),
        (ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv", "HK gene list"),
    ]
    missing_data = []
    for path, desc in data_checks:
        if not path.exists():
            status = "MISSING (will skip)" if ("tcga" in str(path) and args.skip_tcga) else "MISSING"
            print(f"  {color(status, Color.RED)}: {desc}")
            missing_data.append(desc)
        else:
            size_mb = path.stat().st_size / 1e6
            print(f"  {color('OK', Color.GREEN)}: {desc} ({size_mb:.1f} MB)")

    if args.dry_run:
        print(f"\n{color('Dry run complete. No scripts executed.', Color.YELLOW)}")
        return

    if args.verify_only:
        run_group("Verify", [("Spot Check", "scripts/spot_check.py")])
        print("\nFor the comprehensive submission-package verification, run:")
        print("  python 99_build_nc_v49.py")
        return

    # ================================================================
    # Phase 1: Independent groups (run in parallel)
    # ================================================================
    print(f"\n{color('[Phase 1] Independent analysis groups', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    # Group A: Tabula Muris FACS
    group_a = [
        ("HK Stability",       "01b_hk_stability.py"),
        ("HK Overlap",         "01c_hk_overlap.py"),
        ("Tissue Omega",       "01_tissue_omega_matrix.py"),
        ("Pilot v2",           "02b_pilot_v2.py"),
        ("Pilot v2b",          "02c_pilot_v2b.py"),
        ("Full Matrix",        "03_full_matrix.py"),
        ("Sweep",              "04_phase32_sweep.py"),
    ]

    # Group B: Tabula Sapiens
    group_b = [
        ("Phase33 Human",      "05_phase33_v3_fixed.py"),
    ]

    # Group C: TCGA
    group_c = [
        ("Phase34 TCGA",       "06_phase34_v2.py"),
        ("Clinical",           "07_phase34_clinical.py"),
    ]

    # Group D: Brain (07d is the current landscape script; the 07c v3 outputs
    # are pre-fix and superseded, see results/superseded/)
    group_d = [
        ("Brain Siletti",      "07d_brain_siletti_v4.py"),
    ]

    # Method comparison (runs independently — reads raw data)
    group_f = [
        ("Method Comparison",  "13_phase35_method_comparison.py"),
    ]

    all_groups_ok = True

    # Run A, B, C, D, F in parallel (each group internally parallel)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            ex.submit(run_group, "A: Tabula Muris", group_a, not args.sequential, 15): "A",
            ex.submit(run_group, "B: Tabula Sapiens", group_b, False, 20): "B",
            ex.submit(run_group, "F: Method Comparison", group_f, False, 15): "F",
        }

        if not args.skip_tcga:
            futures[ex.submit(run_group, "C: TCGA", group_c, False, 30): "C"]
        else:
            print(f"\n{color('[C: TCGA] SKIPPED (--skip-tcga)', Color.YELLOW)}")

        if not args.skip_brain:
            futures[ex.submit(run_group, "D: Brain", group_d, False, 120): "D"]
        else:
            print(f"\n{color('[D: Brain] SKIPPED (--skip-brain)', Color.YELLOW)}")

        for f in as_completed(futures):
            label = futures[f]
            ok = f.result()
            if not ok:
                all_groups_ok = False
            print(f"  {color('Group ' + label + ' COMPLETE', Color.GREEN if ok else Color.RED)}")

    # ================================================================
    # Phase 2: Permutation tests (depends on Phase 1 outputs)
    # ================================================================
    print(f"\n{color('[Phase 2] Permutation tests (08a/08b/08c)', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    group_e_scripts = []
    if not args.skip_tcga:
        group_e_scripts.append(("TCGA Permutation",   "08a_tcga_bootstrap.py"))
    group_e_scripts.append(("Human Permutation",  "08b_human_bootstrap_v2.py"))
    if not args.skip_brain:
        group_e_scripts.append(("Brain Permutation",  "08c_brain_bootstrap_v3.py"))

    if not run_group("E: Permutation", group_e_scripts, not args.sequential, 20):
        all_groups_ok = False

    # Brain block-shuffle null: 08d (heavy) -> 08e (post-processing).
    # This is the authoritative statistical source for all brain per-pair
    # and cell-type results reported in the manuscript.
    if not args.skip_brain:
        print(f"\n{color('[Phase 2b] Brain block-shuffle null (08d -> 08e)', Color.BOLD + Color.CYAN)}")
        print("=" * 60)
        ok, _, _ = run_script("Block-Shuffle Null", "08d_brain_blockshuffle_null.py", 180)
        if not ok:
            all_groups_ok = False
        else:
            ok, _, _ = run_script("Block-Shuffle Results", "08e_brain_blockshuffle_results.py", 10)
            if not ok:
                all_groups_ok = False
    else:
        print(f"\n{color('[Phase 2b] Brain block-shuffle SKIPPED (--skip-brain)', Color.YELLOW)}")

    # ================================================================
    # Phase 3: Post-processing & Verification
    # ================================================================
    print(f"\n{color('[Phase 3] Post-processing & Verification', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    # Precompute figure data (reads all CSVs)
    ok, _, _ = run_script("Figure Data", "notebooks/precompute_figure_data.py", 5)
    if not ok:
        all_groups_ok = False

    # Spot check (quick sanity check only; full verification: 99_build_nc_v49.py)
    spot_check = ROOT / "scripts" / "spot_check.py"
    if spot_check.exists():
        ok, _, _ = run_script("Spot Check", "scripts/spot_check.py", 5)
        if not ok:
            all_groups_ok = False
    else:
        print(f"  {color('SKIP', Color.YELLOW)}: spot_check.py not found")

    # ================================================================
    # Phase 4: Phase B Statistical Upgrades
    # ================================================================
    print(f"\n{color('[Phase 4] Phase B Statistical Upgrades', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    group_phase_b = [
        ("PhaseB Stats",       "09_phaseB_statistical_upgrades.py"),
        ("PhaseB Residual",    "09b_phaseB_residual_pervisign.py"),
    ]
    if not run_group("Phase B", group_phase_b, False, 60):
        all_groups_ok = False

    # ================================================================
    # Phase 5: Phase C Methodological Reinforcement
    # ================================================================
    print(f"\n{color('[Phase 5] Phase C Methodological Reinforcement', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    group_phase_c = [
        ("PhaseC Method",      "09c_phaseC_methodological.py"),
    ]
    if not run_group("Phase C", group_phase_c, False, 30):
        all_groups_ok = False

    # ================================================================
    # Phase 6: Reviewer-fix & v40 statistical analyses
    # (depend on 08d/08e block-shuffle outputs and Phase 1 results)
    # ================================================================
    print(f"\n{color('[Phase 6] Reviewer-fix & v40 statistical analyses', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    if not args.skip_brain:
        # Heavy brain analyses (raw-data-level, need 08d outputs)
        group_rev_brain = [
            ("Within-Donor",      "41_reviewer_fix_within_donor.py"),
            ("k_n Estimators",    "42_reviewer_fix_kn_estimators.py"),
            ("Fixed-Panel Ablation", "46_fixed_panel_ablation.py"),
            ("Donor-Stratified Null", "48_donor_stratified_null.py"),
        ]
        if not run_group("R1: Brain reviewer-fix (heavy)", group_rev_brain, not args.sequential, 120):
            all_groups_ok = False

        # CSV-level analyses (need 08e output brain_bs_null_results.csv)
        group_rev_csv = [
            ("Lineage Enrichment", "38_reviewer_fix_lineage_enrichment.py"),
            ("Tier Sensitivity",   "39_reviewer_fix_tier_sensitivity.py"),
            ("Brain Set-Level",    "72_brain_setlevel_tests.py"),
        ]
        if not run_group("R2: Brain reviewer-fix (CSV)", group_rev_csv, not args.sequential, 15):
            all_groups_ok = False
    else:
        print(f"\n{color('[R1/R2: Brain reviewer-fix] SKIPPED (--skip-brain)', Color.YELLOW)}")

    # Split-half & CI calibration (need 08d + 13 + 02c outputs)
    group_rev_sh = [
        ("TS Split-Half",     "43_reviewer_fix_ts_splithalf.py"),
        ("PhaseB CI Fix",     "44_fix_phaseB_cis.py"),
    ]
    if not run_group("R3: Split-half & CIs", group_rev_sh, not args.sequential, 60):
        all_groups_ok = False

    # Ground-truth simulations (mouse background)
    group_rev_sim = [
        ("Ground-Truth Sim",  "45_groundtruth_simulation.py"),
        ("Ground-Truth BG2",  "49_groundtruth_sim_background2.py"),
    ]
    if not run_group("R4: Ground-truth simulations", group_rev_sim, not args.sequential, 60):
        all_groups_ok = False

    # TCGA composition sanity check
    if not args.skip_tcga:
        if not run_group("R5: TCGA composition", [
            ("TCGA Composition",  "73_tcga_composition_check.py"),
        ], False, 60):
            all_groups_ok = False
    else:
        print(f"\n{color('[R5: TCGA composition] SKIPPED (--skip-tcga)', Color.YELLOW)}")

    # ================================================================
    # Phase 6b: v44 blind-review analyses (see Reproducibility Guide 5.8)
    # ================================================================
    print(f"\n{color('[Phase 6b] v44 blind-review analyses', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    if not args.skip_tcga:
        group_v44_tcga = [
            ("TCGA Linear-Norm",      "notebooks/85_tcga_linear_norm_v44.py"),
            ("TCGA Composition v44",  "notebooks/86_tcga_composition_linear_norm_v44.py"),
            ("Cross-Organ rho CI",    "notebooks/87_cross_organ_rho_ci_v44.py"),
        ]
        if not run_group("V44-TCGA", group_v44_tcga, False, 90):
            all_groups_ok = False
    else:
        print(f"\n{color('[V44-TCGA] SKIPPED (--skip-tcga)', Color.YELLOW)}")

    if not args.skip_brain:
        ok, _, _ = run_script("Brain Downsample+Threshold v44",
                              "notebooks/86_brain_downsample_threshold_v44.py", 120)
        if not ok:
            all_groups_ok = False
    else:
        print(f"\n{color('[V44-Brain] SKIPPED (--skip-brain)', Color.YELLOW)}")

    group_v44_rest = [
        ("Mouse Split-Half 50rep",  "notebooks/87_mouse_splithalf_v44.py"),
        ("Competitor Benchmark",    "notebooks/101_competitors_v44.py"),
    ]
    if not run_group("V44-Calibration+Benchmark", group_v44_rest, not args.sequential, 120):
        all_groups_ok = False

    # ================================================================
    # Phase 6c: v45 analyses (see Reproducibility Guide 5.9)
    # ================================================================
    print(f"\n{color('[Phase 6c] v45 analyses', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    group_v45 = [
        ("Ratio Estimator",     "notebooks/88_ratio_estimator_v45.py"),
        ("Cluster Bootstrap",   "notebooks/89_cluster_boot_v45.py"),
        ("Non-HK Drift",        "notebooks/90_nonhk_drift_v45.py"),
    ]
    if not run_group("V45", group_v45, not args.sequential, 120):
        all_groups_ok = False

    if not args.skip_brain:
        group_v45_brain = [
            ("Augur Multiclass",    "notebooks/91_augur_v45.py"),
            ("Augur OvR",           "notebooks/91b_augur_ovr_v45.py"),
        ]
        if not run_group("V45-Brain", group_v45_brain, not args.sequential, 180):
            all_groups_ok = False
    else:
        print(f"\n{color('[V45-Brain] SKIPPED (--skip-brain)', Color.YELLOW)}")

    # ================================================================
    # Phase 6d: nc49 analyses (see Reproducibility Guide 5.10/5.11)
    # ================================================================
    print(f"\n{color('[Phase 6d] nc49 analyses', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    group_nc49_indep = [
        ("Kang Tech-Replicate",   "notebooks/nc49_pilot_kang_techrep.py"),
        ("Calib Leave-One-Out",   "notebooks/92_calib_leave_one_out_v49.py"),
        ("Agg-Order Sensitivity", "notebooks/nc49_agg_order_sensitivity.py"),
    ]
    if not run_group("NC49-calibration", group_nc49_indep, not args.sequential, 60):
        all_groups_ok = False

    if not args.skip_brain:
        group_nc49_brain = [
            ("Brain Drift Ladder",    "notebooks/nc49_brain_drift_ladder.py"),
            ("Brain Region-Matched",  "notebooks/95_brain_region_matched_v49.py"),
            ("Brain Downsample kfkn", "notebooks/96_brain_downsample_decomp_v49.py"),
            ("Donor-Stratified Table", "notebooks/97_donor_stratified_table_v49.py"),
        ]
        if not run_group("NC49-Brain", group_nc49_brain, not args.sequential, 180):
            all_groups_ok = False
    else:
        print(f"\n{color('[NC49-Brain] SKIPPED (--skip-brain)', Color.YELLOW)}")

    if not args.skip_tcga:
        group_nc49_tcga = [
            ("TCGA Main (nc49)",      "notebooks/nc49_tcga_main.py"),
            ("LIHC Cox",              "notebooks/nc49_pilot_lihc_cox.py"),
            ("TCGA Purity",           "notebooks/nc49_tcga_purity.py"),
            ("LUAD Smoking",          "notebooks/nc49_tcga_luad_smoking.py"),
            ("k_f Composition",       "notebooks/nc49_tcga_kf_composition.py"),
            ("LUAD Group Permutation", "notebooks/93_luad_group_permutation_v49.py"),
            ("LUAD Log-Omega Sens.",  "notebooks/98_luad_logomega_sensitivity_v49.py"),
            ("CC Audit Sensitivity",  "notebooks/94_cc_audit_sensitivity_v49.py"),
            ("LIHC Cox ex-CC",        "notebooks/nc49_lihc_cox_excc.py"),
        ]
        if not run_group("NC49-TCGA", group_nc49_tcga, not args.sequential, 180):
            all_groups_ok = False
    else:
        print(f"\n{color('[NC49-TCGA] SKIPPED (--skip-tcga)', Color.YELLOW)}")

    # ================================================================
    # Phase 6e: nc50 microglia independent validation (Guide 5.12)
    # ================================================================
    print(f"\n{color('[Phase 6e] nc50 microglia validation', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    if (ROOT / "data" / "human_brain_atlas_microglia.h5ad").exists():
        ok, _, _ = run_script("Microglia Validation", "notebooks/nc50_brain_atlas_microglia.py", 120)
        if not ok:
            all_groups_ok = False
    else:
        print(f"  {color('SKIP', Color.YELLOW)}: data/human_brain_atlas_microglia.h5ad not found")

    # ================================================================
    # Phase 7: Figure Generation
    # ================================================================
    print(f"\n{color('[Phase 7] Figure Generation', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    ok, _, _ = run_script("Main + Supp Figures", "notebooks/30_genome_biology_figures.py", 30)
    if not ok:
        all_groups_ok = False

    group_fig_nc = [
        ("Fig. 3 Drift Ladder",  "notebooks/nc49_fig_drift_ladder.py"),
        ("Fig. 4 TCGA",          "notebooks/nc49_fig_tcga.py"),
        ("Supp. Fig. 14",        "notebooks/nc50_fig_microglia.py"),
    ]
    if not run_group("NC Figures", group_fig_nc, not args.sequential, 30):
        all_groups_ok = False

    # ================================================================
    # Phase 8: Collect Submission Figures
    # ================================================================
    print(f"\n{color('[Phase 8] Collect Submission Figures', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    collector = ROOT / "_collect_submission_figures.py"
    if collector.exists():
        ok, _, _ = run_script("Collect Figures", "_collect_submission_figures.py", 2)
        if not ok:
            all_groups_ok = False
    else:
        print(f"  {color('SKIP', Color.YELLOW)}: _collect_submission_figures.py not found")

    # ================================================================
    # Summary
    # ================================================================
    elapsed = time.time() - t_start
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    print(f"\n{color('=' * 60, Color.BOLD)}")
    if all_groups_ok:
        print(color(f"PIPELINE COMPLETE — All steps passed ({mins}m {secs}s)", Color.GREEN + Color.BOLD))
        print()
        print("Next steps:")
        print("  1. Verify & build package: python 99_build_nc_v49.py")
        print("     (regenerates the manuscript, supplementary information,")
        print("      cover letter, reproducibility guide and the submission zip,")
        print("      then runs the full assertion battery)")
    else:
        print(color(f"PIPELINE FAILED — Some steps failed ({mins}m {secs}s)", Color.RED + Color.BOLD))
        print("Check the output above for FAIL markers.")

    print(color("=" * 60, Color.BOLD))

    sys.exit(0 if all_groups_ok else 1)


if __name__ == "__main__":
    main()
