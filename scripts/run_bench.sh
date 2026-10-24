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

echo "== regenerating phase11.md =="
python3 - <<'PY'
text = open('results/benchout.txt').read()
out = []
out.append("# Phase 11 results — Tessellio over simulated transports (fair measurement)\n\n")
out.append("Scene: 640×360 office surface. 20 iterations per scenario.\n")
out.append("Measured frame is a **delta** (phase 2 after a committed base).\n")
out.append("e2e_ms measures **time to first successful delivery** for every transport (apples-to-apples).\n")
out.append("full_cycle (med) reported separately (ack + feedback window, MLP only meaningful).\n\n")
for name in ["MLP framing ", "MLP fast (no ack wait) ", "WebSocket-like ", "Raw (no loss handling) "]:
    idx = text.find("# " + name)
    if idx < 0: continue
    chunk = text[idx:]
    end = chunk.find("\n# ", 1)
    if end > 0: chunk = chunk[:end]
    out.append(chunk.strip() + "\n\n")
idx = text.find("# Throughput")
if idx >= 0:
    chunk = text[idx:]
    end = chunk.find("\n# ", 1)
    if end > 0: chunk = chunk[:end]
    out.append(chunk.strip() + "\n\n")
open('results/phase11.md','w').write(''.join(out))
print("phase11.md updated")
PY

echo "DONE"
