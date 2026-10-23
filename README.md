# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 10 — interleaved throughput.** 5 updates in flight on a bad link,
interleaved enqueue+poll (respecting in_flight_cap=2): 5 updates/s,
1 637 bytes on wire, 1 002 ms total, 188 333 pacing sleeps.

Pending: MLP anchor-plan repair, real WebSocket, report.

## Methodology

- Scene: 640×360 synthetic surface (~230 400 cells), ~7 fragments on
  DataChannel.
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT + jitter (uniform), independent per-fragment loss.
- Transport: MLP framing (fragments, acks, on_ack) + selective fragment
  repair on loss; WebSocket-like (whole frame, resend on loss); Raw (no
  loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resend rounds), throughput (updates/s), pacing
  sleeps.

## Results (Phase 10)

### MLP framing (selective fragment repair)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.142 | 813 | 10.2 | 10.2 | 0 |
| good | 50 | 5 | 1% | 0.987 | 813 | 56.2 | 60.2 | 0 |
| bad | 150 | 30 | 10% | 1.041 | 813 | 181.7 | 198.2 | 3 |
| terrible | 300 | 80 | 20% | 1.041 | 813 | 368.6 | 415.2 | 18 |
| jitter | 100 | 60 | 5% | 1.000 | 813 | 166.7 | 206.2 | 0 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.012 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.015 | 727 | 27.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.019 | 727 | 92.6 | 101.1 | 0 |
| terrible | 300 | 80 | 20% | 0.990 | 727 | 205.6 | 859.2 | 6 |
| jitter | 100 | 60 | 5% | 0.992 | 727 | 77.6 | 102.1 | 0 |

### Raw (no loss handling)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 0.993 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.021 | 727 | 27.6 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 0.998 | 727 | 92.1 | 105.1 | 0 |
| terrible | 300 | 80 | 20% | 1.016 | 727 | 181.6 | 211.1 | 0 |
| jitter | 100 | 60 | 5% | 1.146 | 727 | 90.1 | 107.1 | 0 |

### Throughput (5 updates in flight, bad link: 150 ms RTT, 10% loss, 30 ms jitter)

| metric | value |
|---|---|
| total bytes on wire | 1 637 |
| total time | 1 002.3 ms |
| heals (resend rounds) | 0 |
| throughput | 5.0 updates/s |
| pacing sleeps | 188 333 |

Observations:
- Interleaved enqueue+poll respects in_flight_cap=2: 5 updates take ~1 s
  (5 × RTT) because each update waits for the previous to leave the
  in-flight window.
- Throughput ~5 updates/s — bottleneck is the ack round trip, not the
  codec (encode ~1 ms).
- Pacer sleep count is high (busy-wait) — a proper driver would use
  poll_timeout to arm a timer instead of spinning.
- MLP's p95 on "terrible" (415 ms) is much lower than WebSocket's (859 ms).
- Encode cost ~1 ms for 640×360 — codec is transport-agnostic.
- Raw does not heal — stale state under loss.

Caveats:
- Resend is simulated (re-deliver lost fragments), not MLP's anchor-plan
  repair.
- No pacing/BWE under congestion — pacer not exercised meaningfully.
- Loss is per-fragment but resend accounts bytes approximately.

## Roadmap

1. **MLP anchor-plan repair** — replace simulated resend with MLP's own
   repair (PlanStarted / plan_next_update).
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