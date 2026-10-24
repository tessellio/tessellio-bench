use std::time::Instant;
use tessellio_core::{CapturedFrame, CodecConfig, ScreenStreamEncoder};

fn main() {
    let mut encoder = ScreenStreamEncoder::new(CodecConfig::default());
    let capture = tessellio_core::scene::office(640, 360, 1);
    let t0 = Instant::now();
    let planned = encoder.encode(&capture).unwrap().unwrap();
    let update = encoder.commit(planned, 1);
    println!("encode_ms={:.3} bytes={}", t0.elapsed().as_secs_f64()*1000.0, update.payload_bytes());
}
