//! tessellio-bench — MVP: Tessellio encode over a simulated transport.
//!
//! Measures the codec's behaviour when its updates travel over a link that
//! loses and delays, compared with an ideal (lossless, instant) link. This is
//! the first step of a larger comparison (MLP vs WebSocket vs QUIC ...); the
//! MLP transport integration is the next step.

use std::time::{Duration, Instant};

use rand::Rng;
use tessellio_core::{CapturedFrame, CodecConfig, ScreenStreamEncoder};

const WIDTH: u32 = 320;
const HEIGHT: u32 = 180;
const ITERS: u32 = 20;

fn paint(phase: u32) -> CapturedFrame {
    let mut rgba = vec![0_u8; (WIDTH * HEIGHT * 4) as usize];
    // background
    for i in (0..rgba.len()).step_by(4) {
        rgba[i] = 18;
        rgba[i + 1] = 20;
        rgba[i + 2] = 26;
        rgba[i + 3] = 255;
    }
    // moving block
    let bx = 100 + (phase as u32 * 7) % 180;
    for y in 80u32..120 {
        for x in bx..bx + 40 {
            if x < WIDTH && y < HEIGHT {
                let o = ((y * WIDTH + x) * 4) as usize;
                rgba[o] = 235;
                rgba[o + 1] = 180;
                rgba[o + 2] = 90;
                rgba[o + 3] = 255;
            }
        }
    }
    CapturedFrame::new(WIDTH, HEIGHT, rgba).unwrap()
}

#[derive(Clone, Copy)]
struct Link {
    rtt_ms: u64,
    loss: f64,
}

#[derive(Default)]
struct Stats {
    encode_ms: Vec<f64>,
    bytes: Vec<u64>,
    e2e_ms: Vec<f64>,
    heals: u32,
    lost: u32,
}

fn run_one(link: Link, rng: &mut impl Rng) -> (f64, u64, f64, bool) {
    // returns (encode_ms, bytes, e2e_ms, lost?)
    let mut encoder = ScreenStreamEncoder::new(CodecConfig::default());
    let capture = paint(1);
    let t0 = Instant::now();
    let planned = match encoder.encode(&capture) {
        Ok(Some(p)) => p,
        _ => return (0.0, 0, 0.0, false),
    };
    let update = encoder.commit(planned, 1);
    let encode_ms = t0.elapsed().as_secs_f64() * 1000.0;
    let bytes = update.payload_bytes() as u64;

    // transport simulation
    let lost = rng.r#gen::<f64>() < link.loss;
    let delay = Duration::from_millis(link.rtt_ms / 2);
    std::thread::sleep(delay);
    let e2e = if lost {
        // naive heal: resend whole update after one RTT
        std::thread::sleep(Duration::from_millis(link.rtt_ms));
        encode_ms + link.rtt_ms as f64 * 1.5
    } else {
        encode_ms + link.rtt_ms as f64 / 2.0
    };
    (encode_ms, bytes, e2e, lost)
}

fn median(v: &[f64]) -> f64 {
    if v.is_empty() {
        return 0.0;
    }
    let mut s = v.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let n = s.len();
    if n % 2 == 1 {
        s[n / 2]
    } else {
        (s[n / 2 - 1] + s[n / 2]) / 2.0
    }
}

fn p95(v: &[f64]) -> f64 {
    if v.is_empty() {
        return 0.0;
    }
    let mut s = v.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let idx = ((s.len() as f64) * 0.95).ceil() as usize;
    s[idx.min(s.len()) - 1]
}

fn main() {
    let mut rng = rand::thread_rng();
    let scenarios = [
        ("ideal", Link { rtt_ms: 10, loss: 0.0 }),
        ("good", Link { rtt_ms: 50, loss: 0.01 }),
        ("bad", Link { rtt_ms: 150, loss: 0.10 }),
        ("terrible", Link { rtt_ms: 300, loss: 0.20 }),
    ];

    println!("# tessellio-bench MVP\n");
    println!("| scenario | rtt_ms | loss | encode_ms (med) | bytes | e2e_ms (med) | e2e_ms (p95) | lost updates |");
    println!("|---|---|---|---|---|---|---|---|");

    for (name, link) in scenarios {
        let mut st = Stats::default();
        for _ in 0..ITERS {
            let (em, b, e2e, lost) = run_one(link, &mut rng);
            st.encode_ms.push(em);
            st.bytes.push(b);
            st.e2e_ms.push(e2e);
            if lost {
                st.lost += 1;
                st.heals += 1;
            }
        }
        let med_encode = median(&st.encode_ms);
        let med_bytes = st.bytes.iter().sum::<u64>() / st.bytes.len() as u64;
        let med_e2e = median(&st.e2e_ms);
        let p95_e2e = p95(&st.e2e_ms);
        println!(
            "| {} | {} | {:.0}% | {:.3} | {} | {:.1} | {:.1} | {}/{} |",
            name, link.rtt_ms, link.loss * 100.0, med_encode, med_bytes, med_e2e, p95_e2e, st.lost, ITERS
        );
    }
}
