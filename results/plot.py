import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

scenarios = ['ideal','good','bad','terrible','jitter']
mlp = [25.2,48.0,106.9,209.0,97.1]
ws  = [5.1,27.6,89.6,204.6,85.1]
raw = [5.1,27.1,88.6,187.1,83.6]
mlp_p95 = [29.7,50.9,124.8,248.7,117.7]
ws_p95  = [5.1,30.1,102.1,544.2,179.2]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
x = range(len(scenarios))
w = 0.25
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
