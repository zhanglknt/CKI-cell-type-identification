#!/bin/bash
# v49 cascade driver — reruns all downstream analyses after the P0 extraction fix.
# Waits for the currently running 08d (--resume) and 42 jobs, then runs the rest.
PY="/c/Users/KnightZ/Desktop/细胞受选择/cki_env/Scripts/python.exe"
ROOT="/c/Users/KnightZ/Desktop/细胞受选择"
LOGS="$ROOT/results"

cd "$ROOT/notebooks"

echo "[driver] waiting for 08d..."
while ! grep -q "^EXIT: 0" "$LOGS/v49_08d_full_run.log" 2>/dev/null; do
  if grep -q "^EXIT: [^0]" "$LOGS/v49_08d_full_run.log" 2>/dev/null; then
    echo "[driver] FATAL: 08d exited nonzero"; exit 1
  fi
  sleep 60
done
echo "[driver] 08d done $(date)"

echo "[driver] waiting for 42..."
while ! grep -q "^EXIT: 0" "$LOGS/v49_42_rerun.log" 2>/dev/null; do
  if grep -q "^EXIT: [^0]" "$LOGS/v49_42_rerun.log" 2>/dev/null; then
    echo "[driver] FATAL: 42 exited nonzero"; exit 1
  fi
  sleep 60
done
echo "[driver] 42 done $(date)"

run_nb () {  # notebook scripts (absolute paths via _paths)
  name="$1"
  echo "[driver] running $name $(date)"
  "$PY" "$name.py" > "$LOGS/v49_${name%%_*}_rerun.log" 2>&1
  ec=$?
  echo "EXIT: $ec" >> "$LOGS/v49_${name%%_*}_rerun.log"
  echo "[driver] $name exit=$ec"
  if [ $ec -ne 0 ]; then echo "[driver] FATAL: $name failed"; exit 1; fi
}

run_root () {  # scripts needing CWD=project root (relative paths)
  name="$1"
  echo "[driver] running $name (root) $(date)"
  ( cd "$ROOT" && "$PY" "notebooks/$name.py" > "$LOGS/v49_${name%%_*}_rerun.log" 2>&1 )
  ec=$?
  echo "EXIT: $ec" >> "$LOGS/v49_${name%%_*}_rerun.log"
  echo "[driver] $name exit=$ec"
  if [ $ec -ne 0 ]; then echo "[driver] FATAL: $name failed"; exit 1; fi
}

run_nb 08e_brain_blockshuffle_results
run_nb 08c_brain_bootstrap_v3
run_nb 41_reviewer_fix_within_donor
run_nb 46_fixed_panel_ablation
run_root 38_reviewer_fix_lineage_enrichment
run_root 39_reviewer_fix_tier_sensitivity
run_nb 09_phaseB_statistical_upgrades
run_nb 44_fix_phaseB_cis
run_nb 09c_phaseC_methodological

echo "[driver] ALL DONE $(date)" > "$LOGS/v49_cascade_done.marker"
echo "[driver] ALL DONE $(date)"
