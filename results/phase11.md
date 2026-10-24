# Phase 11 results — Tessellio over simulated transports (fair measurement)

Scene: 640×360 office surface. 20 iterations per scenario.
Measured frame is a **delta** (phase 2 after a committed base).
e2e_ms measures **time to first successful delivery** for every transport (apples-to-apples).
full_cycle (med) reported separately (ack + feedback window, MLP only meaningful).

# MLP framing 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 27.064 | 1559 | 15.4 | 15.5 | 270.6 | 0 |
| good | 50 | 1% | 27.795 | 1559 | 38.3 | 40.5 | 315.1 | 0 |
| bad | 150 | 10% | 32.571 | 1559 | 101.1 | 111.4 | 440.9 | 1 |
| terrible | 300 | 20% | 39.663 | 1559 | 181.0 | 234.6 | 641.3 | 4 |
| jitter | 100 | 5% | 26.674 | 1559 | 96.5 | 117.4 | 415.2 | 1 |

# MLP fast (no ack wait) 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 26.906 | 1559 | 15.4 | 15.5 | 15.4 | 0 |
| good | 50 | 1% | 26.681 | 1559 | 37.4 | 40.4 | 37.5 | 0 |
| bad | 150 | 10% | 27.876 | 1559 | 96.4 | 107.4 | 96.4 | 0 |
| terrible | 300 | 20% | 29.197 | 1559 | 185.9 | 218.5 | 185.9 | 0 |
| jitter | 100 | 5% | 28.675 | 1559 | 93.5 | 117.4 | 93.5 | 0 |

# WebSocket-like 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 27.952 | 1473 | 5.1 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 27.884 | 1473 | 27.6 | 30.3 | 27.6 | 1 |
| bad | 150 | 10% | 26.937 | 1473 | 91.6 | 249.2 | 91.6 | 2 |
| terrible | 300 | 20% | 27.372 | 1473 | 219.1 | 573.2 | 219.1 | 7 |
| jitter | 100 | 5% | 26.890 | 1473 | 91.1 | 109.1 | 91.1 | 1 |

# Raw (no loss handling) 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 27.188 | 1473 | 5.1 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 27.155 | 1473 | 27.1 | 29.1 | 27.1 | 0 |
| bad | 150 | 10% | 27.591 | 1473 | 94.6 | 102.1 | 94.6 | 0 |
| terrible | 300 | 20% | 26.827 | 1473 | 182.1 | 225.1 | 182.1 | 0 |
| jitter | 100 | 5% | 26.940 | 1473 | 69.6 | 107.1 | 69.6 | 0 |

# Throughput (20 updates in flight, bad link)

| metric | value |
|---|---|
| total bytes on wire | 133025 |
| total time (ms) | 8391.9 |
| heals (resend rounds) | 9 |
| throughput (updates/s) | 6.0 |

