import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('results/data.json'))
scenarios = data['scenarios']
T = data['transports']
mlp = [T['MLP framing'][s]['e2e_med'] for s in scenarios]
ws  = [T['WebSocket-like'][s]['e2e_med'] for s in scenarios]
raw = [T['Raw (no loss handling)'][s]['e2e_med'] for s in scenarios]
mlp_p95 = [T['MLP framing'][s]['e2e_p95'] for s in scenarios]
ws_p95  = [T['WebSocket-like'][s]['e2e_p95'] for s in scenarios]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
x = range(len(scenarios)); w = 0.25
ax1.bar([i-w for i in x], mlp, w, label='MLP (med)')
ax1.bar([i for i in x], ws, w, label='WebSocket (med)')
ax1.bar([i+w for i in x], raw, w, label='Raw (med)')
ax1.set_xticks(x); ax1.set_xticklabels(scenarios)
ax1.set_ylabel('e2e latency (ms)'); ax1.set_title('Median latency')
ax1.legend()

ax2.bar([i-w for i in x], mlp_p95, w, label='MLP (p95)')
ax2.bar([i for i in x], ws_p95, w, label='WebSocket (p95)')
ax2.set_xticks(x); ax2.set_xticklabels(scenarios)
ax2.set_ylabel('e2e latency (ms)'); ax2.set_title('p95 latency')
ax2.legend()

plt.tight_layout()
plt.savefig('results/latency.png', dpi=120)
print("saved results/latency.png")
