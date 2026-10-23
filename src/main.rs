//! tessellio-bench — Tessellio over three transports: MLP framing, WebSocket-like, Raw.

use std::thread;
use std::time::{Duration, Instant};

use mlp_core::media::cells::CellGrid;
use mlp_core::media::pdu::Carrier;
use mlp_core::media::receiver::{MediaReceiverConfig, MediaReceiverMachine};
use mlp_core::media::sender::{MediaSenderConfig, MediaSenderMachine, UpdateRequest};
use rand::Rng;
use tessellio_core::{CapturedFrame, CodecConfig, ScreenStreamEncoder};

const WIDTH: u32 = 640;
const HEIGHT: u32 = 360;
const ITERS: u32 = 20;

fn paint(phase: u32) -> CapturedFrame {
    let mut rgba = vec![0_u8; (WIDTH * HEIGHT * 4) as usize];
    for i in (0..rgba.len()).step_by(4) {
        rgba[i] = 18;
        rgba[i + 1] = 20;
        rgba[i + 2] = 26;
        rgba[i + 3] = 255;
    }
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

#[derive(Clone, Copy, PartialEq, Eq)]
enum Transport {
    Mlp,
    Ws,
    Raw,
}

#[derive(Clone, Copy)]
struct Link {
    rtt_ms: u64,
    loss: f64,
    jitter_ms: u64,
}

fn run_one(transport: Transport, link: Link, rng: &mut impl Rng) -> (f64, u64, f64, u32) {
    let mut encoder = ScreenStreamEncoder::new(CodecConfig::default());
    let capture = paint(1);
    let t0 = Instant::now();
    let planned = match encoder.encode(&capture) {
        Ok(Some(p)) => p,
        _ => return (0.0, 0, 0.0, 0),
    };
    let update = encoder.commit(planned, 1);
    let encode_ms = t0.elapsed().as_secs_f64() * 1000.0;
    let tess_bytes = update.payload_bytes();

    let t_start = Instant::now();
    let mut heals = 0u32;
    let mut applied = false;
    let mut bytes_on_wire: u64 = 0;

    match transport {
        Transport::Mlp => {
            let now = Instant::now();
            let grid = CellGrid::with_cell_size(WIDTH, HEIGHT, 64);
            let mut sender = MediaSenderMachine::new(MediaSenderConfig::new(Carrier::DataChannel, grid), grid, now);
            let mut receiver = MediaReceiverMachine::new(MediaReceiverConfig::for_carrier(Carrier::DataChannel), now);

            // First attempt: enqueue + poll all fragments.
            let _ = sender.enqueue_update(UpdateRequest::delta(vec![0u8; tess_bytes], vec![0, 1]), Instant::now());
            let mut all_frags: Vec<Vec<u8>> = Vec::new();
            while let Some(f) = sender.poll_fragment(Instant::now()) {
                all_frags.push(f.bytes);
                if all_frags.len() > 10000 { break; }
            }
            bytes_on_wire += sender.stats().bytes_sent;

            // Deliver with loss.
            let mut pending: Vec<Vec<u8>> = Vec::new();
            let mut got_object = false;
            for f in &all_frags {
                if rng.r#gen::<f64>() < link.loss {
                    pending.push(f.clone());
                    continue;
                }
                let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
                thread::sleep(Duration::from_millis(delay));
                let evs = receiver.on_message(f, Instant::now());
                for ev in evs {
                    if let mlp_core::media::receiver::MediaReceiveEvent::Object(_) = ev {
                        receiver.note_applied(1);
                        got_object = true;
                    }
                }
            }

            // Selective repair: resend only lost fragments, up to 3 rounds.
            for _round in 0..3 {
                if got_object || pending.is_empty() { break; }
                heals += 1;
                let mut still_pending: Vec<Vec<u8>> = Vec::new();
                for f in &pending {
                    if rng.r#gen::<f64>() < link.loss {
                        still_pending.push(f.clone());
                        continue;
                    }
                    let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
                    thread::sleep(Duration::from_millis(delay));
                    let evs = receiver.on_message(f, Instant::now());
                    for ev in evs {
                        if let mlp_core::media::receiver::MediaReceiveEvent::Object(_) = ev {
                            receiver.note_applied(1);
                            got_object = true;
                        }
                    }
                    if !got_object {
                        still_pending.push(f.clone());
                    }
                }
                // account resend bytes (approx: lost fragments re-sent)
                bytes_on_wire += (pending.len() as u64) * 120;
                pending = still_pending;
            }

            if got_object {
                applied = true;
                let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
                thread::sleep(Duration::from_millis(delay));
                let ack = receiver.build_ack(Instant::now());
                let _ = sender.on_ack(ack, Instant::now());
            }
        }
        Transport::Ws => {
            // WebSocket-like: whole update, no fragmentation, RTT/2 delay, resend on loss
            for _attempt in 0..3 {
                bytes_on_wire += tess_bytes as u64; // one frame
                if rng.r#gen::<f64>() < link.loss {
                    heals += 1;
                    let delay = link.rtt_ms + rng.r#gen::<u64>() % (link.jitter_ms + 1);
                    thread::sleep(Duration::from_millis(delay));
                    continue;
                }
                let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
                thread::sleep(Duration::from_millis(delay));
                applied = true;
                break;
            }
        }
        Transport::Raw => {
            // Raw: direct delivery, no overhead, no loss handling
            bytes_on_wire += tess_bytes as u64;
            let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
            thread::sleep(Duration::from_millis(delay));
            applied = true;
        }
    }

    let e2e_ms = if applied {
        t_start.elapsed().as_secs_f64() * 1000.0
    } else {
        t_start.elapsed().as_secs_f64() * 1000.0
    };
    (encode_ms, bytes_on_wire, e2e_ms, heals)
}

/// Throughput: 5 updates in flight, measure total bytes and time.
fn run_throughput(link: Link, rng: &mut impl Rng) -> (u64, f64, u32) {
    let mut encoder = ScreenStreamEncoder::new(CodecConfig::default());
    let mut total_bytes = 0u64;
    let mut heals = 0u32;
    let t_start = Instant::now();

    let now = Instant::now();
    let grid = CellGrid::with_cell_size(WIDTH, HEIGHT, 64);
    let mut sender = MediaSenderMachine::new(MediaSenderConfig::new(Carrier::DataChannel, grid), grid, now);
    let mut receiver = MediaReceiverMachine::new(MediaReceiverConfig::for_carrier(Carrier::DataChannel), now);

    // Enqueue 5 updates.
    for i in 0..5u64 {
        let capture = paint((i as u32) + 1);
        let planned = match encoder.encode(&capture) {
            Ok(Some(p)) => p,
            _ => continue,
        };
        let update = encoder.commit(planned, i + 1);
        let tess_bytes = update.payload_bytes();
        let _ = sender.enqueue_update(UpdateRequest::delta(vec![0u8; tess_bytes], vec![0, 1]), Instant::now());
    }

    // Poll all fragments.
    let mut all_frags: Vec<Vec<u8>> = Vec::new();
    while let Some(f) = sender.poll_fragment(Instant::now()) {
        all_frags.push(f.bytes);
        if all_frags.len() > 100000 { break; }
    }
    total_bytes += sender.stats().bytes_sent;

    // Deliver with loss.
    let mut pending: Vec<Vec<u8>> = Vec::new();
    for f in &all_frags {
        if rng.r#gen::<f64>() < link.loss {
            pending.push(f.clone());
            continue;
        }
        let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
        thread::sleep(Duration::from_millis(delay));
        let evs = receiver.on_message(f, Instant::now());
        for ev in evs {
            if let mlp_core::media::receiver::MediaReceiveEvent::Object(_) = ev {
                // note applied for each; use update id 1 (simplified)
            }
        }
    }
    // Selective repair for lost fragments.
    for _round in 0..3 {
        if pending.is_empty() { break; }
        heals += 1;
        let mut still_pending: Vec<Vec<u8>> = Vec::new();
        for f in &pending {
            if rng.r#gen::<f64>() < link.loss {
                still_pending.push(f.clone());
                continue;
            }
            let delay = link.rtt_ms / 2 + rng.r#gen::<u64>() % (link.jitter_ms + 1);
            thread::sleep(Duration::from_millis(delay));
            let evs = receiver.on_message(f, Instant::now());
            for ev in evs {
                if let mlp_core::media::receiver::MediaReceiveEvent::Object(_) = ev {}
            }
            // approximate: if not lost, consider delivered
            if rng.r#gen::<f64>() >= link.loss {
                // delivered
            } else {
                still_pending.push(f.clone());
            }
        }
        total_bytes += (pending.len() as u64) * 120;
        pending = still_pending;
    }

    let total_ms = t_start.elapsed().as_secs_f64() * 1000.0;
    (total_bytes, total_ms, heals)
}

fn print_throughput() {
    let mut rng = rand::thread_rng();
    let link = Link { rtt_ms: 100, loss: 0.10, jitter_ms: 30 };
    let (bytes, ms, heals) = run_throughput(link, &mut rng);
    println!();
    println!("# Throughput (5 updates in flight, bad link)");
    println!();
    println!("| metric | value |");
    println!("|---|---|");
    println!("| total bytes on wire | {} |", bytes);
    println!("| total time (ms) | {:.1} |", ms);
    println!("| heals (resend rounds) | {} |", heals);
    println!("| throughput (updates/s) | {:.1} |", 5.0 / (ms / 1000.0));
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
        ("ideal", Link { rtt_ms: 10, loss: 0.0, jitter_ms: 0 }),
        ("good", Link { rtt_ms: 50, loss: 0.01, jitter_ms: 5 }),
        ("bad", Link { rtt_ms: 150, loss: 0.10, jitter_ms: 30 }),
        ("terrible", Link { rtt_ms: 300, loss: 0.20, jitter_ms: 80 }),
        ("jitter", Link { rtt_ms: 100, loss: 0.05, jitter_ms: 60 }),
    ];
    let transports = [Transport::Mlp, Transport::Ws, Transport::Raw];

    for tr in transports {
        let label = match tr {
            Transport::Mlp => "MLP framing",
            Transport::Ws => "WebSocket-like",
            Transport::Raw => "Raw (no loss handling)",
        };
        println!("\n# {} \n", label);
        println!("| scenario | rtt_ms | loss | encode_ms (med) | bytes_on_wire (med) | e2e_ms (med) | e2e_ms (p95) | heals |");
        println!("|---|---|---|---|---|---|---|---|");
        for (name, link) in scenarios {
            let mut encodes = Vec::new();
            let mut bytes = Vec::new();
            let mut e2es = Vec::new();
            let mut heals_total = 0u32;
            for _ in 0..ITERS {
                let (em, bs, e2e, h) = run_one(tr, link, &mut rng);
                encodes.push(em);
                bytes.push(bs as f64);
                e2es.push(e2e);
                heals_total += h;
            }
            // recompute applied count properly
            println!(
                "| {} | {} | {:.0}% | {:.3} | {:.0} | {:.1} | {:.1} | {} |",
                name,
                link.rtt_ms,
                link.loss * 100.0,
                median(&encodes),
                median(&bytes),
                median(&e2es),
                p95(&e2es),
                heals_total
            );
        }
    }
    print_throughput();
}
