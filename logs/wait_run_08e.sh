#!/bin/bash
cd "c:/Users/KnightZ/Desktop/细胞受选择"
echo "watchdog started $(date)"
while true; do
  if [ -f results/brain_bs_null_manifest.json ]; then
    if grep -q '"B": 1000' results/brain_bs_null_manifest.json 2>/dev/null; then
      n=$(./cki_env/Scripts/python.exe -c "import pandas as pd;print(len(pd.read_csv('results/brain_bs_null_observed_pairs.csv')))" 2>/dev/null)
      if [ "$n" = "31764" ]; then
        echo "08d full DONE at $(date); running 08e..."
        ./cki_env/Scripts/python.exe notebooks/08e_brain_blockshuffle_results.py > logs/08e_run.log 2>&1
        echo "08e DONE at $(date); exit=$?"
        break
      fi
    fi
  fi
  sleep 60
done
