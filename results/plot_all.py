import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

scenarios = ['ideal','good','bad','terrible','jitter']
mlp_med = [25.2,48.0,106.9,209.0,97.1]
ws_med  = [5.1,27.6,89.6,204.6,85.1]
raw_med = [5.1,27.1,88.6,187.1,83.6]
mlp_p95 = [29.7,50.9,124.8,248.7,117.7]
ws_p95  = [5.1,30.1,102.1,544.2,179.2]
mlp_heals = [0,0,3,4,0]
ws_heals  = [0,0,1,6,2]
raw_heals = [0,0,0,0,0]
mlp_bytes = [55698]*5
ws_bytes  = [55612]*5
mlp_enc = [91.460,84.753,83.998,83.046,83.844]
ws_enc  = [83.994,84.358,84.286,84.798,85.934]

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
ax.bar(['MLP','WebSocket','Raw'], [55698,55612,55612], color=['#4c72b0','#dd8452','#55a868'])
ax.set_ylabel('bytes (lower is better)'); ax.set_title('Bytes on wire per update')
plt.tight_layout(); plt.savefig('results/bytes.png', dpi=120)

print("done")
