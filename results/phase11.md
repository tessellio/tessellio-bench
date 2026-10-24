# Phase 11 results — Tessellio over simulated transports (fair measurement)

Scene: 640×360 office surface (~230 400 cells). 20 iterations per scenario.
e2e_ms now measures **time to first successful delivery** for every transport (apples-to-apples).
full_cycle (med) is reported separately and includes ack + feedback window (MLP only meaningful).

# MLP framing 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 91.460 | 55698 | 25.2 | 29.7 | 280.4 | 0 |
| good | 50 | 1% | 84.753 | 55698 | 48.0 | 50.9 | 326.1 | 0 |
| bad | 150 | 10% | 83.998 | 55698 | 106.9 | 124.8 | 437.9 | 3 |
| terrible | 300 | 20% | 83.046 | 55698 | 209.0 | 248.7 | 654.1 | 4 |
| jitter | 100 | 5% | 83.844 | 55698 | 97.1 | 117.7 | 430.8 | 0 |

# MLP fast (no ack wait) 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 84.230 | 55698 | 24.9 | 25.9 | 25.0 | 0 |
| good | 50 | 1% | 84.712 | 55698 | 47.4 | 51.6 | 47.4 | 0 |
| bad | 150 | 10% | 83.740 | 55698 | 107.6 | 124.8 | 107.6 | 0 |
| terrible | 300 | 20% | 83.294 | 55698 | 199.1 | 226.0 | 199.1 | 0 |
| jitter | 100 | 5% | 82.121 | 55698 | 102.6 | 127.3 | 102.6 | 0 |

# WebSocket-like 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 83.994 | 55612 | 5.1 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 84.358 | 55612 | 27.6 | 30.1 | 27.6 | 0 |
| bad | 150 | 10% | 84.286 | 55612 | 89.6 | 102.1 | 89.6 | 1 |
| terrible | 300 | 20% | 84.798 | 55612 | 204.6 | 544.2 | 204.6 | 6 |
| jitter | 100 | 5% | 85.934 | 55612 | 85.1 | 179.2 | 85.1 | 2 |

# Raw (no loss handling) 

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | full_cycle (med) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 83.317 | 55612 | 5.1 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 83.840 | 55612 | 27.1 | 30.1 | 27.1 | 0 |
| bad | 150 | 10% | 82.651 | 55612 | 88.6 | 102.1 | 88.6 | 0 |
| terrible | 300 | 20% | 83.744 | 55612 | 187.1 | 217.1 | 187.1 | 0 |
| jitter | 100 | 5% | 82.119 | 55612 | 83.6 | 101.1 | 83.6 | 0 |

# Throughput (20 updates in flight, bad link)

| metric | value |
|---|---|
| total bytes on wire | 133025 |
| total time (ms) | 8439.1 |
| heals (resend rounds) | 9 |
| throughput (updates/s) | 5.9 |

## Key findings

1. MLP framing adds ~86 bytes/update overhead (55698 vs 55612) for fragmentation header, TLVs, ack metadata.
2. With fair measurement (time to first delivery), MLP median e2e is now comparable to WebSocket (107 vs 90 ms on bad link) — the protocol no longer looks artificially slower.
3. MLP p95 stays bounded under loss (125-249 ms) vs WebSocket spikes (102-544 ms) — selective fragment repair.
4. MLP full_cycle (438-654 ms) reflects the complete protocol round trip (ack + feedback + repair), reported separately.
5. Encode cost ~84 ms for the 640×360 base frame (transport-independent; codec, not transport).
6. Raw transport is the latency floor but does not heal.
