#!/usr/bin/env python
"""
run_all.py — Complete reproducibility pipeline for CKI Genome Biology manuscript (v40+).

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
    Phase 7 (Figures):  30_genome_biology_figures
    Phase 8 (Collect):  _collect_submission_figures

Note on verification: scripts/spot_check.py provides a quick numerical
sanity check only; the comprehensive 285-assertion verification of the
submission package is performed by 99_build_gb_v40.py.

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
    print(color("CKI Genome Biology — Reproducibility Pipeline", Color.BOLD))
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

    # Group D: Brain
    # 07c (v3) regenerates the superseded v3 intermediates consumed by
    # 08c; 07d (v4) is the current per-pair source described in the
    # Reproducibility Guide Section 4.4 (both kept in the package).
    group_d = [
        ("Brain Siletti v4",   "07d_brain_siletti_v4.py"),
        ("Brain Siletti v3",   "07c_brain_siletti_v3.py"),
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

    # Spot check (quick sanity check only; full verification: 99_build_gb_v40.py)
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
    # Phase 7: Figure Generation
    # ================================================================
    print(f"\n{color('[Phase 7] Figure Generation', Color.BOLD + Color.CYAN)}")
    print("=" * 60)

    ok, _, _ = run_script("Main + Supp Figures", "notebooks/30_genome_biology_figures.py", 30)
    if not ok:
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
        print("  1. Generate manuscript:     python generate_manuscript_gb.py")
        print("  2. Generate supplementary: python notebooks/68_gen_supplementary_en.py")
        print("  3. Generate cover letter:  python generate_cover_letter_nar.py")
        print("  4. Generate repro guide:   node notebooks/100_gen_reproducibility_docx.js")
        print("  5. Extract tables:         python notebooks/_extract_table1_2.py")
        print("  6. Verify & build package: python 99_build_gb_v40.py  (285-assertion verification)")
    else:
        print(color(f"PIPELINE FAILED — Some steps failed ({mins}m {secs}s)", Color.RED + Color.BOLD))
        print("Check the output above for FAIL markers.")

    print(color("=" * 60, Color.BOLD))

    sys.exit(0 if all_groups_ok else 1)


if __name__ == "__main__":
    main()
