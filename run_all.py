#!/usr/bin/env python
"""
run_all.py — Complete reproducibility pipeline for CKI Genome Biology manuscript.

Usage:
    python run_all.py              # Run everything (default)
    python run_all.py --dry-run     # Print execution plan without running
    python run_all.py --skip-tcga   # Skip TCGA (needs controlled-access data)
    python run_all.py --verify-only # Only run spot-check verification

Execution order (independent groups run in parallel):
    Group A (Tabula Muris FACS):   01b_hk, 01c_hk, 01_tissue, 02b, 02c, 03_full, 04_sweep
    Group B (Tabula Sapiens):      05_phase33_fixed
    Group C (TCGA):                06_phase34_v2, 07_clinical
    Group D (Brain):               07c_brain_siletti
    ── wait for all ──
    Group E (Bootstrap):           08a_tcga, 08b_human, 08c_brain
    Group F (Method comparison):   13_phase35
    ── wait for all ──
    Post:                          precompute_figure_data, spot_check

Prerequisites:
    1. Install cki: pip install -e .
    2. Raw data in data/ (ts_human/, brain/, tcga/, FACS/, housekeeping/)
    3. Python 3.9+ with dependencies: numpy, scipy, scanpy, pandas, scikit-learn
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
        run_group("Verify", [("Spot Check", "scripts/spot_check_v19.py")])
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
    group_d = [
        ("Brain Siletti",      "07c_brain_siletti_v3.py"),
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
    # Phase 2: Bootstrap (depends on Phase 1 outputs)
    # ================================================================
    print(f"\n{color('[Phase 2] Bootstrap analysis', Color.BOLD + Color.CYAN)}")
    print("=" * 60)
    
    group_e_scripts = []
    if not args.skip_tcga:
        group_e_scripts.append(("TCGA Bootstrap",    "08a_tcga_bootstrap.py"))
    group_e_scripts.append(("Human Bootstrap",  "08b_human_bootstrap_csv.py"))
    if not args.skip_brain:
        group_e_scripts.append(("Brain Bootstrap",   "08c_brain_bootstrap_csv.py"))
    
    if not run_group("E: Bootstrap", group_e_scripts, not args.sequential, 15):
        all_groups_ok = False
    
    # ================================================================
    # Phase 3: Post-processing & Verification
    # ================================================================
    print(f"\n{color('[Phase 3] Post-processing & Verification', Color.BOLD + Color.CYAN)}")
    print("=" * 60)
    
    # Precompute figure data (reads all CSVs)
    ok, _, _ = run_script("Figure Data", "notebooks/precompute_figure_data.py", 5)
    if not ok:
        all_groups_ok = False
    
    # Spot check
    spot_check = ROOT / "scripts" / "spot_check_v19.py"
    if spot_check.exists():
        ok, _, _ = run_script("Spot Check", "scripts/spot_check_v19.py", 5)
        if not ok:
            all_groups_ok = False
    else:
        print(f"  {color('SKIP', Color.YELLOW)}: spot_check_v19.py not found")
    
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
        print("  1. Generate figures:      python notebooks/30_genome_biology_figures.py")
        print("  2. Generate manuscript:   python generate_manuscript_genome_biology.py")
        print("  3. Build packages:        python _build_packages.py")
    else:
        print(color(f"PIPELINE FAILED — Some steps failed ({mins}m {secs}s)", Color.RED + Color.BOLD))
        print("Check the output above for FAIL markers.")
    
    print(color("=" * 60, Color.BOLD))
    
    sys.exit(0 if all_groups_ok else 1)


if __name__ == "__main__":
    main()
