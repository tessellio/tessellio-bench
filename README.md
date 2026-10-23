# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 13 — real cell accounting.** Tessellio now exposes
`changed_cell_indices` in `EncodedUpdate`; the bench feeds real cell indices
into MLP's sender accounting instead of placeholders. Anchor-plan repair
uses actual cells.

Pending: pacing/BWE under congestion, real WebSocket, report (done).

## Methodology

- Scene: 640×360 synthetic surface (~230 400 cells), ~7 fragments on
  DataChannel.
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT + jitter (uniform), independent per-fragment loss.
- Transport: MLP framing (fragments, acks, on_ack) + anchor-plan repair
  (with selective fallback); WebSocket-like (whole frame, resend on loss);
  Raw (no loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resend rounds), throughput (updates/s).

## Results (Phase 13)

### MLP framing (anchor-plan + real cells)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.535 | 813 | 10.8 | 12.4 | 0 |
| good | 50 | 5 | 1% | 1.454 | 813 | 56.2 | 60.1 | 0 |
| bad | 150 | 30 | 10% | 1.436 | 813 | 182.3 | 200.7 | 0 |
| terrible | 300 | 80 | 20% | 1.508 | 813 | 386.7 | 420.7 | 2 |
| jitter | 100 | 60 | 5% | 1.532 | 813 | 157.8 | 196.8 | 0 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.550 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.505 | 727 | 27.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.595 | 727 | 94.6 | 245.2 | 4 |
| terrible | 300 | 80 | 20% | 1.499 | 727 | 194.1 | 509.1 | 3 |
| jitter | 100 | 60 | 5% | 1.589 | 727 | 87.3 | 109.1 | 1 |

### Raw (no loss handling)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.009 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.017 | 727 | 27.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.038 | 727 | 92.1 | 103.1 | 0 |
| terrible | 300 | 80 | 20% | 1.011 | 727 | 194.6 | 225.1 | 0 |
| jitter | 100 | 60 | 5% | 1.020 | 727 | 85.1 | 103.1 | 0 |

### Throughput (5 updates in flight, bad link)

| metric | value |
|---|---|
| total bytes on wire | 1 637 |
| total time | 1 001.5 ms |
| heals (resend rounds) | 0 |
| throughput | 5.0 updates/s |
| pacing sleeps | 188 333 |

Observations:
- With real cell indices, MLP heals dropped to 0–2 on all scenarios —
  anchor-plan repair now has accurate cell data.
- MLP's p95 on "terrible" (420 ms) is much lower than WebSocket's (509 ms).
- Encode cost ~1.5 ms for 640×360 — codec is transport-agnostic.
- Raw does not heal — stale state under loss.

Caveats:
- No pacing/BWE under congestion — pacer not exercised meaningfully.
- Loss is per-fragment but resend accounts bytes approximately.

## Roadmap (remaining)

1. **MLP pacing/BWE under congestion** — sustained load.
2. **WebSocket baseline with real WS** — replace simulation with
   tokio-tungstenite.
3. **Report** — markdown + plots in `results/` (done).

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.