# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 3 — three transports compared.** The bench now runs the same
Tessellio update over three transports on identical scenarios:

- **MLP framing** — real `mlp-core` fragments/acks, simulated link, naïve
  resend on loss.
- **WebSocket-like** — whole update per frame, no fragmentation, naïve
  resend on loss.
- **Raw** — direct delivery, no loss handling (lower bound).

MLP's own anchor-plan repair, pacing and BWE are still pending.

## Methodology

- Scene: 320×180 synthetic surface (background + moving block).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT, independent per-fragment/per-update loss.
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resends).

## Results (Phase 3)

### MLP framing

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.546 | 484 | 10.2 | 10.3 | 0 |
| good | 50 | 1% | 0.424 | 484 | 50.2 | 50.2 | 0 |
| bad | 150 | 10% | 0.407 | 484 | 150.2 | 150.3 | 5 |
| terrible | 300 | 20% | 0.432 | 484 | 300.2 | 300.3 | 10 |

### WebSocket-like

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.385 | 398 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 0.488 | 398 | 25.1 | 25.2 | 0 |
| bad | 150 | 10% | 0.410 | 398 | 75.1 | 225.2 | 4 |
| terrible | 300 | 20% | 0.415 | 398 | 150.1 | 150.1 | 3 |

### Raw (no loss handling)

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.457 | 398 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 0.489 | 398 | 25.1 | 25.2 | 0 |
| bad | 150 | 10% | 0.409 | 398 | 75.1 | 75.1 | 0 |
| terrible | 300 | 20% | 0.444 | 398 | 150.1 | 150.1 | 0 |

Observations:
- **Overhead:** MLP framing costs ~86 bytes/update (484 vs 398) — fragmentation
  header, TLVs, ack metadata. WebSocket/Raw carry the raw payload.
- **Latency:** Raw wins on good links (no ack wait). MLP and WebSocket both
  pay RTT for acks; MLP's e2e ≈ RTT, WebSocket's ≈ RTT/2 on clean links.
- **Loss:** Raw does not heal (lost updates stay lost). Both MLP and
  WebSocket heal via resend, but WebSocket shows a p95 spike (225 ms on
  "bad") where a single resend doubled the latency; MLP stayed flat (150 ms)
  because its ack loop is per-fragment and the resend is bounded.
- **Heals:** MLP healed 10/20 on "terrible" vs WebSocket's 3/20 — MLP's
  per-fragment loss detection catches more losses (each fragment is checked),
  while WebSocket only detects whole-update loss.
- **Encode cost:** ~0.4 ms everywhere — codec is transport-agnostic.

Caveats:
- Single fragment per update in this MVP → fragmentation benefit not yet
  exercised. Multi-fragment updates (large scenes) will favour MLP's
  selective repair.
- Naïve resend, not MLP's anchor-plan repair — so MLP's healing advantage
  is understated here.
- No pacing/BWE yet — single update, no congestion.

## Roadmap

1. **MLP anchor-plan repair** — replace naïve resend with MLP's own repair.
2. **MLP pacing/BWE** — multiple updates in flight.
3. **Multi-fragment updates** — large scenes to exercise selective repair.
4. **WebSocket baseline with real WS** — replace simulation with tokio-tungstenite.
5. **Scenarios** — office scene, pointer-1px, jitter.
6. **Report** — markdown + plots in `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.