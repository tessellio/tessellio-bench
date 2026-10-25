//! The bench's own scenario, once through, as a smoke test: encode the base
//! and the delta, run every transport's link simulation, and require the
//! numbers to exist.

#[path = "../src/main.rs"]
mod bench;

#[test]
fn every_transport_runs_its_scenario_once() {
    let mut rng = rand::thread_rng();
    for transport in [bench::Transport::Mlp, bench::Transport::MlpFast, bench::Transport::Ws, bench::Transport::Raw] {
        let link = bench::Link { rtt_ms: 40, loss: 0.01, jitter_ms: 5 };
        let (encode_ms, bytes, e2e_ms, _cycle_ms, delivered) = bench::run_one(transport, link, &mut rng);
        assert!(encode_ms >= 0.0, "{transport:?}: encode time");
        assert!(bytes > 0, "{transport:?}: the delta is on the wire");
        assert!(e2e_ms >= 0.0, "{transport:?}: end-to-end time");
        assert!(delivered <= 1, "{transport:?}: one iteration, at most one delivery");
    }
}
