use std::time::Instant;
use mlp_core::media::cells::CellGrid;
use mlp_core::media::pdu::Carrier;
use mlp_core::media::receiver::{MediaReceiverConfig, MediaReceiverMachine};
use mlp_core::media::sender::{MediaSenderConfig, MediaSenderMachine, UpdateRequest};

pub fn try_mlp() {
    let now = Instant::now();
    let grid = CellGrid::with_cell_size(320, 180, 64);
    let mut sender = MediaSenderMachine::new(MediaSenderConfig::new(Carrier::Ws, grid), grid, now);
    let mut receiver = MediaReceiverMachine::new(MediaReceiverConfig::for_carrier(Carrier::Ws), now);

    let payload = vec![0u8; 398];
    let r = sender.enqueue_update(UpdateRequest::delta(payload, vec![0, 1]), now);
    println!("enqueue: {:?}", r);

    // poll all fragments
    let mut frags: Vec<Vec<u8>> = Vec::new();
    while let Some(f) = sender.poll_fragment(now) {
        frags.push(f.bytes);
        if frags.len() > 100 { break; }
    }
    println!("fragments: {}", frags.len());

    // deliver to receiver
    for f in &frags {
        let ev = receiver.on_message(f, now);
        println!("receiver events: {:?}", ev);
    }

    // build ack
    let ack = receiver.build_ack(now);
    println!("ack: {:?}", ack);
    let evs = sender.on_ack(ack, now);
    println!("sender on_ack events: {:?}", evs);
}
