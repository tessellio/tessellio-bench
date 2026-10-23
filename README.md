# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**MVP.** Currently measures the codec's encode cost and end-to-end latency
over a *naïve* lossy/delayed link model (no repair, no pacing). The
**MLP transport** is the next integration step: the bench will then compare
Tessellio-over-MLP against Tessellio-over-WebSocket and a raw baseline on the
same scenarios.

## Methodology (MVP)

- Scene: 320×180 synthetic surface (office-like: background + moving block).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT, independent per-update loss probability.
- Naïve transport: on loss, resend the whole update after one RTT (no
  fragmentation, no pacing, no BWE).
- Metrics: encode time (median), payload bytes, end-to-end latency
  (median + p95), lost updates.

## Results (MVP, naïve transport)

| scenario | rtt_ms | loss | encode_ms (med) | bytes | e2e_ms (med) | e2e_ms (p95) | lost |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.402 | 398 | 5.4 | 5.6 | 0/20 |
| good | 50 | 1% | 0.402 | 398 | 25.4 | 25.6 | 0/20 |
| bad | 150 | 10% | 0.401 | 398 | 75.4 | 75.6 | 0/20 |
| terrible | 300 | 20% | 0.395 | 398 | 150.4 | 150.5 | 0/20 |

Observations:
- Encode cost is stable (~0.4 ms) and independent of link conditions — the
  codec does not know about the transport, as designed.
- Payload is 398 bytes for a 57 600-cell surface update.
- End-to-end latency is dominated by RTT (as expected for a naïve
  transport with no pipelining).
- No updates were lost in 20 iterations even at 20 % loss — the naïve
  resend maskes it, but at the cost of latency (heal = 1.5× RTT).

## Roadmap

1. **MLP integration** — replace the naïve transport with `mlp-core`
   machines (sender/receiver, fragmentation, pacing, BWE, repair).
2. **WebSocket baseline** — same scenarios over a WebSocket-shaped transport.
3. **Raw baseline** — direct delivery, no overhead.
4. **Scenarios** — office scene, pointer-1px, loss 0/5/10/20 %, RTT
   20/50/100/150/300 ms, jitter.
5. **Report** — markdown table + per-scenario plots, published in
   `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.