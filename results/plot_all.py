import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('results/data.json'))
scenarios = data['scenarios']
T = data['transports']
mlp = T['MLP framing']
fast = T['MLP fast (no ack wait)']
ws = T['WebSocket-like']
raw = T['Raw (no loss handling)']

def col(t, k): return [t[s][k] for s in scenarios]

mlp_med = col(mlp, 'e2e_med'); ws_med = col(ws, 'e2e_med'); raw_med = col(raw, 'e2e_med')
mlp_p95 = col(mlp, 'e2e_p95'); ws_p95 = col(ws, 'e2e_p95')
mlp_heals = col(mlp, 'heals'); ws_heals = col(ws, 'heals'); raw_heals = col(raw, 'heals')
mlp_bytes = col(mlp, 'bytes'); ws_bytes = col(ws, 'bytes')
mlp_enc = col(mlp, 'encode_ms'); ws_enc = col(ws, 'encode_ms')

x = range(len(scenarios)); w = 0.25

# 1. latency med
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_med, w, label='MLP')
ax.bar([i for i in x], ws_med, w, label='WebSocket')
ax.bar([i+w for i in x], raw_med, w, label='Raw')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('Median e2e latency (first delivery)')
ax.legend(); plt.tight_layout(); plt.savefig('results/latency_med.png', dpi=120)

# 2. latency p95
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_p95, w, label='MLP')
ax.bar([i for i in x], ws_p95, w, label='WebSocket')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('p95 e2e latency')
ax.legend(); plt.tight_layout(); plt.savefig('results/latency_p95.png', dpi=120)

# 3. heals
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_heals, w, label='MLP')
ax.bar([i for i in x], ws_heals, w, label='WebSocket')
ax.bar([i+w for i in x], raw_heals, w, label='Raw')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('heals (lower is better)'); ax.set_title('Heal count (20 iters)')
ax.legend(); plt.tight_layout(); plt.savefig('results/heals.png', dpi=120)

# 4. encode cost
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_enc, w, label='MLP (office)')
ax.bar([i for i in x], ws_enc, w, label='WebSocket (office)')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('Encode cost')
ax.legend(); plt.tight_layout(); plt.savefig('results/encode.png', dpi=120)

# 5. bytes
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(['MLP','WebSocket','Raw'], [mlp_bytes[0], ws_bytes[0], ws_bytes[0]], color=['#4c72b0','#dd8452','#55a868'])
ax.set_ylabel('bytes (lower is better)'); ax.set_title('Bytes on wire per update')
plt.tight_layout(); plt.savefig('results/bytes.png', dpi=120)

print("done")
