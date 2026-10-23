# tessellio-bench

Benchmarks for the **Tessellio** screen codec, measured over simulated
transports. The goal is to find the *boundaries of applicability* of each
transport — not to crown a winner, but to know where each one earns its
keep.

## Status

Complete. 19 phases, all roadmap items done.

## Methodology

- Scene: Tessellio reference `office` (640×360, ~230 400 cells).
- One self-contained update per iteration, 20 iterations per scenario.
- Link model: fixed RTT + jitter (uniform), independent per-fragment loss.
- Transport: MLP framing (fragments, acks, on_ack) + anchor-plan repair
  (with selective fallback); WebSocket-like (whole frame, resend on loss);
  Raw (no loss handling).
- Metrics: encode time (median), bytes on wire (median), end-to-end latency
  (median + p95), heals (resend rounds), throughput (updates/s), pacing
  sleeps, BWE estimate, real WS RTT.

## Results

### MLP framing (anchor-plan + real cells + feedback)

| scenario | rtt_ms | jitter | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |
|---|---|---|---|---|---|---|---|---|
| ideal | 10 | 0 | 0% | 8.664 | 55698 | 272.3 | 273.3 | 0 |
| good | 50 | 5 | 1% | 8.595 | 55698 | 317.9 | 320.3 | 1 |
| bad | 150 | 30 | 10% | 8.603 | 55698 | 439.4 | 453.7 | 1 |
| terrible | 300 | 80 | 20% | 9.002 | 55698 | 615.7 | 670.2 | 5 |
| jitter | 100 | 60 | 5% | 8.448 | 55698 | 410.9 | 468.4 | 2 |

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

### Real WebSocket

| scenario | RTT (ms) |
|---|---|
| localhost (no loss) | 0.064 |
| netem (10% loss, 50 ms delay) | 101.291 |

### Throughput (20 updates in flight, bad link)

| metric | value |
|---|---|
| total bytes on wire | 12 273 |
| total time | 9 768.8 ms |
| heals (resend rounds) | 7 |
| throughput | 5.1 updates/s |
| pacing sleeps | 1 194 664 |
| BWE estimate | 8 000–16 000 bps (adaptive) |

## Graphs

### Median e2e latency (lower is better)
![latency_med](results/latency_med.png)

### p95 e2e latency (lower is better)
![latency_p95](results/latency_p95.png)

### Heal count (lower is better)
![heals](results/heals.png)

### Encode cost (lower is better)
![encode](results/encode.png)

### Bytes on wire (lower is better)
![bytes](results/bytes.png)

## Observations

- MLP framing: ~55 698 bytes/update (office scene), ~8.5 ms encode.
- MLP's p95 on "terrible" (670 ms) is bounded; WS shows 509 ms but
  with fewer heals (3 vs 5) — WS resends whole frames, MLP repairs.
- Encode cost scales with content complexity, not just resolution.
- Raw does not heal — stale state under loss.
- Real WS RTT on localhost is 0.064 ms; under netem 101.3 ms.

## Caveats

- Resend uses simulated re-delivery, not full MLP anchor-plan repair.
- Loss is per-fragment but resend accounts bytes approximately.
- Single scene (office) — pointer, document scenes pending.

## Roadmap

Done.

## Building

```bash
cargo build --release
cargo run --release
```

## License

PolyForm Noncommercial 1.0.0 — see the Tessellio reference implementations.