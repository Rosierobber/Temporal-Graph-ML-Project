import os, re, csv, statistics as st
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PUB = {  # TGB paper Table 2b (tgbl-review): val, val_std, test, test_std. VERIFY these against the paper.
    "EdgeBank_inf": (0.0229, None, 0.0229, None), "EdgeBank_tw": (0.0242, None, 0.0253, None),
    "TGN": (0.313, 0.012, 0.349, 0.020), "DyRep": (0.216, 0.031, 0.220, 0.030),
    "GraphMixer": (0.428, 0.019, 0.521, 0.015)}
rd = lambda p: list(csv.DictReader(open(os.path.join(REPO, p)))) if os.path.exists(os.path.join(REPO, p)) else []
ms = lambda v: (st.mean(v), st.stdev(v) if len(v) > 1 else 0.0)
fmt = lambda a, s: f"{a:.4f} ± {s:.4f}"
mine = {}
for model in ["TGN", "DyRep"]:
    r = [x for x in rd("results/review_runs_summary.csv") if x["model"] == model]
    mine[model] = (*ms([float(x["best_val_mrr"]) for x in r]), *ms([float(x["test_mrr"]) for x in r]), len(r))
for tag, key in [("inf", "EdgeBank_inf"), ("tw", "EdgeBank_tw")]:
    p = os.path.join(REPO, f"logs/edgebank_{tag}_review_seed1.txt")
    t = open(p, errors="ignore").read() if os.path.exists(p) else ""
    v = re.findall(r"val:\s*mrr:\s*([0-9.]+)", t); te = re.findall(r"Test: mrr:\s*([0-9.]+)", t)
    if v and te: mine[key] = (float(v[0]), 0.0, float(te[0]), 0.0, 1)
out = ["| Model | Published val | Published test | My val | My test | n | Test gap / published std |",
       "|---|---|---|---|---|---|---|"]
for m, (pv, pvs, pt, pts) in PUB.items():
    if m not in mine: out.append(f"| {m} | {pv} | {pt} | not run (compute budget) | | 0 | n/a |"); continue
    mv, sv, mt, stt, n = mine[m]
    pubv = f"{pv:.4f}" if pvs is None else f"{pv:.3f} ± {pvs:.3f}"; pubt = f"{pt:.4f}" if pts is None else f"{pt:.3f} ± {pts:.3f}"
    gap = "n/a (deterministic)" if pts is None else f"{(mt - pt) / pts:+.2f}"
    out.append(f"| {m} | {pubv} | {pubt} | {fmt(mv, sv)} | {fmt(mt, stt)} | {n} | {gap} |")
rb = {r["config"]: r for r in rd("results/test_final_review.csv")}
if "full_R-EdgeBank" in rb:
    out.append(f"| R-EdgeBank (mine) | | | | {float(rb['full_R-EdgeBank']['test_mrr']):.4f} | 1 | deterministic |")
out += ["", "TGN and DyRep: 5-epoch cap (published setup does not state epochs), seeds 1, 3, 4, Tesla T4.",
        "GraphMixer was not run on review (compute budget). R-EdgeBank: rho tuned on the first 100k validation edges."]
text = "\n".join(out); print(text)
open(os.path.join(REPO, "notes", "review_comparison_table.md"), "w").write(text + "\n")
