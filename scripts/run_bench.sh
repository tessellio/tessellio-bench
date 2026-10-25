#!/usr/bin/env bash
# Run the benchmark and regenerate all plots + report.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== running bench =="
cargo run > results/benchout.txt 2>&1

echo "== generating data.json =="
python3 results/gen_data.py

echo "== regenerating plots =="
python3 results/plot_all.py
python3 results/plot.py

echo "DONE"
