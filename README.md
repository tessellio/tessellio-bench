# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 6 — multi-fragment updates.** Scene enlarged to 640×360; MLP now
uses DataChannel carrier (fragment_payload_max 1 150) so each update
spans ~7 fragments. Selective repair (resend only lost fragments) is the
natural next step — currently still whole-update resend.

Pending: MLP anchor-plan repair, pacing/BWE, selective fragment repair,
real WebSocket, jitter variants, report.

## Methodology

- Scene: 640×360 synthetic surface (background + moving block) — ~230 400
  cells.
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT + jitter (uniform), independent per-fragment loss.
- Transport: MLP framing (fragments, acks, on_ack) + Repair re-send on loss;
  WebSocket-like (whole frame, resend on loss); Raw (no loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resends).

## Results (Phase 6)

### MLP framing (Repair on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 2.889 | 813 | 10.3 | 12.4 | 0 |
| good | 50 | 5 | 1% | 2.124 | 813 | 56.1 | 58.5 | 0 |
| bad | 150 | 30 | 10% | 1.355 | 813 | 179.7 | 200.3 | 3 |
| terrible | 300 | 80 | 20% | 1.396 | 813 | 368.6 | 415.2 | 18 |
| jitter | 100 | 60 | 5% | 1.017 | 813 | 141.2 | 202.8 | 0 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.276 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.129 | 727 | 27.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.257 | 727 | 95.1 | 104.1 | 1 |
| terrible | 300 | 80 | 20% | 1.123 | 727 | 200.1 | 545.5 | 4 |
| jitter | 100 | 60 | 5% | 1.093 | 727 | 93.6 | 110.1 | 0 |

### Raw (no loss handling)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 1.037 | 727 | 5.1 | 5.1 | 0 |
| good | 50 | 5 | 1% | 1.007 | 727 | 27.1 | 30.1 | 0 |
| bad | 150 | 30 | 10% | 1.185 | 727 | 88.6 | 103.1 | 0 |
| terrible | 300 | 80 | 20% | 1.252 | 727 | 201.6 | 223.1 | 0 |
| jitter | 100 | 60 | 5% | 2.710 | 727 | 81.7 | 107.1 | 0 |

Observations:
- Larger scene: encode cost ~1–3 ms (vs ~0.4 ms for 320×180) — scales with
  surface size.
- MLP now spans multiple fragments (813 bytes ≈ 7 fragments on DataChannel).
- Heal count jumped (18 on "terrible") because per-fragment loss hits more
  often with 7 fragments; whole-update resend is wasteful here — selective
  fragment repair (MLP's strength) is the next step.
- WebSocket still shows p95 spikes (545 ms on "terrible").
- Raw does not heal — stale state under loss.

Caveats:
- Naïve resend (whole update), not MLP's anchor-plan repair.
- No pacing/BWE yet — single update, no congestion.
- Loss is per-fragment but repair is whole-update — understates MLP's
  selective-repair advantage.

## Roadmap

1. **Selective fragment repair** — resend only lost fragments (MLP strength).
2. **MLP anchor-plan repair** — replace naïve resend with MLP's own repair.
3. **MLP pacing/BWE** — multiple updates in flight.
4. **WebSocket baseline with real WS** — replace simulation with tokio-tungstenite.
5. **Report** — markdown + plots in `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.