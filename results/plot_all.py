import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

scenarios = ['ideal','good','bad','terrible','jitter']
mlp_med = [10.8,56.2,182.3,386.7,157.8]
ws_med  = [5.1,27.1,94.6,194.1,87.3]
raw_med = [5.1,27.1,92.1,194.6,85.1]
mlp_p95 = [12.4,60.1,200.7,420.7,196.8]
ws_p95  = [5.1,30.1,245.2,509.1,109.1]
mlp_heals = [0,0,0,2,0]
ws_heals  = [0,0,4,3,1]
raw_heals = [0,0,0,0,0]
mlp_bytes = [813]*5
ws_bytes  = [727]*5
mlp_enc = [8.664,8.595,8.603,9.002,8.448]
ws_enc  = [1.550,1.505,1.595,1.499,1.589]

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
ax.bar(['MLP','WebSocket','Raw'], [813,727,727], color=['#4c72b0','#dd8452','#55a868'])
ax.set_ylabel('bytes (lower is better)'); ax.set_title('Bytes on wire per update')
plt.tight_layout(); plt.savefig('results/bytes.png', dpi=120)

print("done")
