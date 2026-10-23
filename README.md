# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 4 — real repair on loss.** The bench now uses MLP's `Repair` kind
(anchor=true) for re-sends instead of a naïve delta re-enqueue. Both MLP
and WebSocket-like heal lost updates; Raw still does not.

Pending: MLP anchor-plan repair (full), pacing/BWE, multi-fragment updates,
WebSocket baseline with real sockets, jitter scenario.

## Methodology

- Scene: 320×180 synthetic surface (background + moving block).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT, independent per-fragment/per-update loss.
- Transport: MLP framing (fragments, acks, on_ack) + Repair re-send on loss;
  WebSocket-like (whole frame, resend on loss); Raw (no loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resends).

## Results (Phase 4)

### MLP framing (Repair on loss)

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.413 | 484 | 10.2 | 10.2 | 0 |
| good | 50 | 1% | 0.457 | 484 | 50.2 | 50.7 | 0 |
| bad | 150 | 10% | 0.424 | 484 | 150.2 | 225.3 | 2 |
| terrible | 300 | 20% | 0.424 | 484 | 300.2 | 450.3 | 4 |

### WebSocket-like (resend on loss)

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.446 | 398 | 5.1 | 5.1 | 0 |
| good | 50 | 1% | 0.449 | 398 | 25.1 | 25.1 | 0 |
| bad | 150 | 10% | 0.558 | 398 | 75.1 | 225.2 | 3 |
| terrible | 300 | 20% | 0.584 | 398 | 154.7 | 451.2 | 5 |

### Raw (no loss handling)

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.683 | 398 | 5.7 | 7.7 | 0 |
| good | 50 | 1% | 0.698 | 398 | 25.2 | 29.8 | 0 |
| bad | 150 | 10% | 0.553 | 398 | 75.1 | 75.1 | 0 |
| terrible | 300 | 20% | 0.441 | 398 | 150.1 | 150.1 | 0 |

Observations:
- Both MLP and WebSocket heal lost updates; Raw does not (lost updates stay
  lost — the application sees stale state).
- MLP's p95 latency degrades gracefully under loss (225/450 ms) because
  each resend is bounded by one RTT and the ack loop is per-fragment.
- WebSocket's p95 is similar but its median is lower on clean links
  (no fragmentation overhead, no ack wait on the fast path).
- MLP pays ~86 bytes/update overhead (484 vs 398) for framing + ack metadata.
- Heal counts are small because each update is a single fragment; loss on
  a single fragment means a whole-update resend. Multi-fragment updates
  would exercise selective repair.
- Encode cost ~0.4 ms everywhere — codec is transport-agnostic.

Caveats:
- Naïve resend (whole update), not MLP's anchor-plan repair — so MLP's
  healing advantage is understated.
- No pacing/BWE yet — single update, no congestion.
- No jitter in the link model yet.

## Roadmap

1. **MLP anchor-plan repair** — replace naïve resend with MLP's own repair.
2. **MLP pacing/BWE** — multiple updates in flight.
3. **Multi-fragment updates** — large scenes to exercise selective repair.
4. **WebSocket baseline with real WS** — replace simulation with tokio-tungstenite.
5. **Jitter scenario** — variable delay.
6. **Report** — markdown + plots in `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.