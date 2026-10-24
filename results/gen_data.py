import json, re, sys

text = open('results/benchout.txt').read()

def parse_table(name):
    idx = text.find("# " + name)
    if idx < 0:
        return {}
    chunk = text[idx:]
    end = chunk.find("\n# ", 1)
    if end > 0:
        chunk = chunk[:end]
    lines = [l for l in chunk.strip().splitlines()
             if l.startswith("|") and not l.startswith("|---") and not l.startswith("| scenario")]
    rows = {}
    for l in lines:
        cols = [c.strip() for c in l.strip().strip("|").split("|")]
        rows[cols[0]] = {
            "rtt_ms": int(cols[1]),
            "loss_pct": float(cols[2].rstrip("%")),
            "encode_ms": float(cols[3]),
            "bytes": int(cols[4]),
            "e2e_med": float(cols[5]),
            "e2e_p95": float(cols[6]),
            "full_cycle": float(cols[7]),
            "heals": int(cols[8]),
        }
    return rows

scn = ['ideal','good','bad','terrible','jitter']
data = {}
for name in ["MLP framing", "MLP fast (no ack wait)", "WebSocket-like", "Raw (no loss handling)"]:
    data[name] = parse_table(name + " ")

json.dump({"scenarios": scn, "transports": data}, open('results/data.json','w'), indent=2)
print("wrote results/data.json")
