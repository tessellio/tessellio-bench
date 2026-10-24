# Benchmark Methodology

## Scene
640×360 office surface (~230 400 cells). All transports encode the same scene.

## Transports
- **MLP framing**: selective fragment repair, pacing, BWE.
- **MLP fast**: fire-and-forget, no ack wait.
- **WebSocket-like**: whole update resend on loss.
- **Raw**: direct delivery, no loss handling.

## Metrics
- **encode_ms**: codec encode time (transport-independent).
- **bytes_on_wire**: total bytes including framing overhead.
- **e2e_ms (med)**: median time to first successful delivery.
- **e2e_ms (p95)**: 95th percentile delivery time.
- **full_cycle (med)**: complete protocol round trip (MLP only).
- **heals**: number of repair rounds.

## Fairness
- All transports encode the same scene (office, phase 2 delta).
- e2e measures time to first delivery for all transports.
- 20 iterations per scenario, 5 scenarios (ideal, good, bad, terrible, jitter).
- Loss is per-fragment, independent of transport.

## Scenarios
| scenario | rtt_ms | jitter | loss |
|---|---|---|---|
| ideal | 10 | 0 | 0% |
| good | 50 | 5 | 1% |
| bad | 150 | 30 | 10% |
| terrible | 300 | 80 | 20% |
| jitter | 100 | 60 | 5% |

## Reproduction
```sh
bash scripts/run_bench.sh
```
