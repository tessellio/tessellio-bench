import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

scenarios = ['ideal','good','bad','terrible','jitter']
mlp_med = [15.4, 38.0, 99.5, 197.9, 91.4]
ws_med  = [5.1, 27.6, 98.1, 190.6, 80.1]
raw_med = [5.1, 27.6, 88.1, 173.6, 68.6]
mlp_p95 = [15.5, 39.4, 110.4, 235.4, 116.5]
ws_p95  = [5.1, 30.1, 263.2, 556.2, 196.1]
mlp_heals = [0, 0, 3, 3, 1]
ws_heals  = [0, 0, 5, 8, 2]
raw_heals = [0, 0, 0, 0, 0]
mlp_bytes = [1559, 1559, 1559, 1559, 1559]
ws_bytes  = [1473, 1473, 1473, 1473, 1473]
mlp_enc = [27.084, 27.179, 26.774, 27.399, 26.832]
ws_enc  = [27.275, 27.421, 27.262, 26.709, 27.438]

# 1. latency med
fig, ax = plt.subplots(figsize=(8,4))
x=range(len(scenarios)); w=0.25
ax.bar([i-w for i in x], mlp_med, w, label='MLP')
ax.bar([i for i in x], ws_med, w, label='WebSocket')
ax.bar([i+w for i in x], raw_med, w, label='Raw')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('Median e2e latency')
ax.legend()
plt.tight_layout(); plt.savefig('results/latency_med.png', dpi=120)

# 2. latency p95
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_p95, w, label='MLP')
ax.bar([i for i in x], ws_p95, w, label='WebSocket')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('p95 e2e latency')
ax.legend()
plt.tight_layout(); plt.savefig('results/latency_p95.png', dpi=120)

# 3. heals
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_heals, w, label='MLP')
ax.bar([i for i in x], ws_heals, w, label='WebSocket')
ax.bar([i+w for i in x], raw_heals, w, label='Raw')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('heals (lower is better)'); ax.set_title('Heal count (20 iters)')
ax.legend()
plt.tight_layout(); plt.savefig('results/heals.png', dpi=120)

# 4. encode cost
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([i-w for i in x], mlp_enc, w, label='MLP (office)')
ax.bar([i for i in x], ws_enc, w, label='WebSocket (synthetic)')
ax.set_xticks(x); ax.set_xticklabels(scenarios)
ax.set_ylabel('ms (lower is better)'); ax.set_title('Encode cost')
ax.legend()
plt.tight_layout(); plt.savefig('results/encode.png', dpi=120)

# 5. bytes
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(['MLP','WebSocket','Raw'], [1559,1473,1473], color=['#4c72b0','#dd8452','#55a868'])
ax.set_ylabel('bytes (lower is better)'); ax.set_title('Bytes on wire per update')
plt.tight_layout(); plt.savefig('results/bytes.png', dpi=120)

print("done")
