# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 11 — anchor-plan repair attempted.** The bench now calls
`sender.poll_plans()` + `sender.plan_next_update()` to obtain an MLP
repair schedule, and enqueues the result as an anchor (`UpdateKind::Repair`,
`anchor=true`) instead of a naïve resend. Falls back to selective fragment
resend when the plan yields no cells (e.g. empty cell accounting).

Pending: proper cell accounting (Tessellio's real cells), pacing/BWE under
congestion, real WebSocket, report.

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

## Results (Phase 11)

### MLP framing (anchor-plan + selective fallback)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.066 | 813 | 10.2 | 10.2 | 0 |
| good | 50 | 5 | 1% | 1.103 | 813 | 55.2 | 58.2 | 0 |
| bad | 150 | 30 | 10% | 1.289 | 813 | 179.2 | 194.2 | 2 |
| terrible | 300 | 80 | 20% | 1.173 | 813 | 406.2 | 434.2 | 5 |
| jitter | 100 | 60 | 5% | 1.219 | 813 | 157.7 | 188.2 | 2 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 0.984 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.076 | 727 | 28.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.081 | 727 | 91.1 | 270.1 | 5 |
| terrible | 300 | 80 | 20% | 1.114 | 727 | 208.1 | 562.2 | 4 |
| jitter | 100 | 60 | 5% | 1.309 | 727 | 90.1 | 107.1 | 0 |

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
- MLP's p95 on "terrible" (434 ms) is much lower than WebSocket's
  (562 ms) — anchor-plan + selective repair keep latency bounded.
- Heal count dropped to 5 on "terrible" (vs 18 with whole-update resend
  in Phase 6) — anchor-plan repair is more efficient.
- Throughput ~5 updates/s — bottleneck is the ack round trip, not the
  codec.
- Encode cost ~1 ms for 640×360 — codec is transport-agnostic.
- Raw does not heal — stale state under loss.

Caveats:
- Cell accounting uses placeholder cells (vec![0,1]) — real Tessellio cells
  would make anchor plans more accurate.
- No pacing/BWE under congestion — pacer not exercised meaningfully.
- Loss is per-fragment but resend accounts bytes approximately.

## Roadmap

1. **Real cell accounting** — feed Tessellio's actual cell indices into the
   sender's accounting (due/pending/stuck).
2. **MLP pacing/BWE under congestion** — exercise the pacer with sustained
   load.
3. **WebSocket baseline with real WS** — replace simulation with
   tokio-tungstenite.
4. **Report** — markdown + plots in `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.