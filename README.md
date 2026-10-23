# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 5 — jitter scenario added.** Five scenarios now: ideal, good, bad,
terrible, jitter. Three transports compared on identical scenarios with
per-fragment/per-update loss and variable delay.

Pending: MLP anchor-plan repair, pacing/BWE, multi-fragment updates, real
WebSocket, jitter scenario variants.

## Methodology

- Scene: 320×180 synthetic surface (background + moving block).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT + jitter (uniform), independent loss.
- Transport: MLP framing (fragments, acks, on_ack) + Repair re-send on loss;
  WebSocket-like (whole frame, resend on loss); Raw (no loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resends).

## Results (Phase 5)

### MLP framing (Repair on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 0.433 | 484 | 10.2 | 10.2 | 0 |
| good | 50 | 5 | 1% | 0.438 | 484 | 55.2 | 60.3 | 1 |
| bad | 150 | 30 | 10% | 0.436 | 484 | 182.2 | 205.2 | 1 |
| terrible | 300 | 80 | 20% | 0.570 | 484 | 370.7 | 543.4 | 6 |
| jitter | 100 | 60 | 5% | 0.416 | 484 | 158.7 | 248.3 | 2 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 0.425 | 398 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 0.431 | 398 | 28.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 0.414 | 398 | 89.6 | 237.2 | 2 |
| terrible | 300 | 80 | 20% | 0.415 | 398 | 210.1 | 563.1 | 5 |
| jitter | 100 | 60 | 5% | 0.436 | 398 | 83.6 | 103.1 | 1 |

### Raw (no loss handling)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 0.405 | 398 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 0.418 | 398 | 27.6 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 0.440 | 398 | 89.1 | 103.1 | 0 |
| terrible | 300 | 80 | 20% | 0.418 | 398 | 206.6 | 224.1 | 0 |
| jitter | 100 | 60 | 5% | 0.411 | 398 | 86.1 | 104.1 | 0 |

Observations:
- Jitter widens p95 for all transports; MLP and WebSocket both show p95 spikes.
- Raw remains the latency floor but does not heal — stale state under loss.
- MLP framing keeps median latency ≈ RTT+jitter/2 and heals more aggressively
  (6 heals on "terrible" vs WebSocket's 5) thanks to per-fragment detection.
- Encode cost ~0.4 ms everywhere — codec is transport-agnostic.

Caveats:
- Naïve resend (whole update), not MLP's anchor-plan repair.
- No pacing/BWE yet — single update, no congestion.
- Single fragment per update — selective repair not exercised.

## Roadmap

1. **MLP anchor-plan repair** — replace naïve resend with MLP's own repair.
2. **MLP pacing/BWE** — multiple updates in flight.
3. **Multi-fragment updates** — large scenes to exercise selective repair.
4. **WebSocket baseline with real WS** — replace simulation with tokio-tungstenite.
5. **Report** — markdown + plots in `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.