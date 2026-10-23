# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

**Phase 2 — MLP framing integrated.** The bench now drives Tessellio updates
through `mlp-core`'s real framing: `MediaSenderMachine` enqueues the update,
`poll_fragment` releases fragments, a simulated link drops them with the
configured probability and delays them by RTT/2, `MediaReceiverMachine`
assembles the object and `note_applied` + `build_ack` close the loop. On a
lost fragment the whole update is re-enqueued (naïve repair on top of MLP
framing). MLP's own anchor-plan repair and pacing/BWE are the next step.

WebSocket baseline and raw baseline are still pending.

## Methodology

- Scene: 320×180 synthetic surface (background + moving block).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT, independent per-fragment loss probability.
- Transport: MLP framing (fragments, acks, on_ack) + naïve resend on loss.
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resends), applied count.

## Results (Phase 2, MLP framing + naïve repair)

| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals (applied) |
|---|---|---|---|---|---|---|---|
| ideal | 10 | 0% | 0.528 | 484 | 10.2 | 11.9 | 0 (20/20) |
| good | 50 | 1% | 0.424 | 484 | 50.2 | 50.2 | 0 (20/20) |
| bad | 150 | 10% | 0.416 | 484 | 150.2 | 150.2 | 5 (20/20) |
| terrible | 300 | 20% | 0.408 | 484 | 300.2 | 300.4 | 5 (20/20) |

Observations:
- MLP framing adds ~86 bytes of overhead per update (484 on wire vs 398
  payload) — fragmentation header, TLVs, ack metadata.
- Encode cost stays ~0.4 ms — codec is transport-agnostic.
- All updates applied in every scenario (naïve repair on loss works).
- Heal count is low because loss is per-fragment and there is only one
  fragment per update in this MVP; multi-fragment updates will stress repair
  more.
- E2E latency still dominated by RTT — MLP pacing/BWE not yet active in
  this bench (single update, no congestion).

## Roadmap

1. **MLP repair** — replace naïve resend with MLP's anchor-plan repair.
2. **MLP pacing/BWE** — multiple updates in flight, measure pacing.
3. **WebSocket baseline** — same scenarios over a WebSocket-shaped transport.
4. **Raw baseline** — direct delivery, no overhead.
5. **Scenarios** — office scene, pointer-1px, loss 0/5/10/20 %, RTT
   20/50/100/150/300 ms, jitter.
6. **Report** — markdown table + per-scenario plots, published in
   `results/`.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.