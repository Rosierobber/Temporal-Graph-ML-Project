"""Regenerates figures 1-5 from the stored CSVs (no training, CPU only)."""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.makedirs(f"{REPO}/figures", exist_ok=True)
rd = lambda p: list(csv.DictReader(open(f"{REPO}/{p}")))
def savefig(name):
    plt.tight_layout(); plt.savefig(f"{REPO}/figures/{name}", dpi=300); plt.close()

# ---- Fig 1: per-seed test MRR on tgbl-wiki
tf = {r["config"]: float(r["test_mrr"]) for r in rd("results/test_final_wiki.csv")}
gm = rd("results/graphmixer_wiki.csv")
data = {"DyRep": [float(r["test_mrr"]) for r in rd("results/dyrep_wiki.csv")],
        "TGN": [float(r["test_mrr"]) for r in rd("results/tgn_wiki.csv")],
        "GraphMixer": [float(r["test_mrr"]) for r in gm if r["failed"] == "False"],
        "EdgeBank (window)": [tf["tw_default_rho0.15"]],
        "R-EdgeBank": [tf["full_R-EdgeBank"]]}
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for i, (k, v) in enumerate(data.items()):
    ax.scatter([i] * len(v), v, s=28, zorder=3)
    if len(v) > 1:
        ax.errorbar(i, np.mean(v), yerr=np.std(v, ddof=1), fmt="_", color="k", capsize=4)
failed = [float(r["test_mrr"]) for r in gm if r["failed"] == "True"]
ax.scatter([2] * len(failed), failed, s=40, facecolors="none", edgecolors="r", zorder=3, label="failed GraphMixer run")
ax.set_xticks(range(len(data))); ax.set_xticklabels(data.keys(), rotation=20)
ax.set_ylabel("Test MRR (tgbl-wiki)"); ax.legend()
savefig("fig1_per_seed_wiki.png")

# ---- Fig 2: recurring vs novel test queries (TGN = mean over seeds)
sl = rd("results/rq2_slices_wiki.csv")
def slice_mrr(prefix, kind):
    return np.mean([float(r["mrr"]) for r in sl if r["model"].startswith(prefix) and r["slice"] == kind])
groups = [("EdgeBank (window)", "tw_default"), ("R-EdgeBank", "full_R-EdgeBank"), ("TGN (mean of seeds)", "TGN_seed")]
fig, ax = plt.subplots(figsize=(5.5, 3.5)); w = 0.35
for j, kind in enumerate(["recurring", "novel"]):
    ax.bar(np.arange(3) + j * w, [slice_mrr(p, kind) for _, p in groups], w, label=kind)
ax.set_xticks(np.arange(3) + w / 2); ax.set_xticklabels([n for n, _ in groups], rotation=15)
ax.set_ylabel("Test MRR (tgbl-wiki)"); ax.legend()
savefig("fig2_slices_wiki.png")

# ---- Fig 3: sensitivity to the window ratio (validation)
sw = rd("results/sweep_val_wiki.csv"); rhos = sorted({float(r["rho"]) for r in sw})
best = lambda mode, a: max(float(r["val_mrr"]) for r in sw if r["mode"] == mode and float(r["rho"]) == a)
fig, ax = plt.subplots(figsize=(5, 3.5))
ax.plot(rhos, [best("tw", a) for a in rhos], marker="o", label="EdgeBank (window)")
ax.plot(rhos, [best("recency", a) for a in rhos], marker="s", label="recency inside window")
ax.axhline(max(float(r["val_mrr"]) for r in sw if r["mode"] == "full"), ls="--", color="k", label="R-EdgeBank (no window)")
ax.set_xlabel("window ratio rho"); ax.set_ylabel("Val MRR (tgbl-wiki)"); ax.legend()
savefig("fig3_sensitivity_wiki.png")

# ---- Fig 4: ablation (test)
ab = [("EdgeBank\n(window)", "tw_default_rho0.15"), ("recency in\nwindow", "recency_only"), ("R-EdgeBank\n(no window)", "full_R-EdgeBank")]
fig, ax = plt.subplots(figsize=(4.8, 3.5)); ax.bar(range(3), [tf[k] for _, k in ab])
ax.set_xticks(range(3)); ax.set_xticklabels([n for n, _ in ab]); ax.set_ylabel("Test MRR (tgbl-wiki)")
savefig("fig4_ablation_wiki.png")

# ---- Fig 5: tgbl-review, per-seed test MRR (5-epoch cap for TGN and DyRep)
rv = rd("results/review_runs_summary.csv"); rt = {r["config"]: float(r["test_mrr"]) for r in rd("results/test_final_review.csv")}
d5 = {"TGN": [float(r["test_mrr"]) for r in rv if r["model"] == "TGN"],
      "DyRep": [float(r["test_mrr"]) for r in rv if r["model"] == "DyRep"],
      "EdgeBank (window)": [0.0253], "R-EdgeBank": [rt["full_R-EdgeBank"]]}
fig, ax = plt.subplots(figsize=(5.5, 3.5))
for i, (k, v) in enumerate(d5.items()):
    ax.scatter([i] * len(v), v, s=28, zorder=3)
    if len(v) > 1:
        ax.errorbar(i, np.mean(v), yerr=np.std(v, ddof=1), fmt="_", color="k", capsize=4)
ax.set_xticks(range(4)); ax.set_xticklabels(d5.keys(), rotation=15); ax.set_ylabel("Test MRR (tgbl-review)")
savefig("fig5_review.png")
print("figures written to", f"{REPO}/figures")
