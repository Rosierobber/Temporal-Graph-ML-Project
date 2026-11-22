import os, csv, statistics as st
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

PUB = {  # Huang et al., NeurIPS 2023 D&B, Table 2a (tgbl-wiki, 5 runs): val, val_std, test, test_std
    "EdgeBank_inf": (0.527, None, 0.495, None), "EdgeBank_tw": (0.600, None, 0.571, None),
    "TGN": (0.435, 0.069, 0.396, 0.060), "DyRep": (0.072, 0.009, 0.050, 0.017),
    "GraphMixer": (0.113, 0.003, 0.118, 0.002)}

def rows(p):
    f = os.path.join(REPO, p)
    return list(csv.DictReader(open(f))) if os.path.exists(f) else []
def ms(v): return (st.mean(v), st.stdev(v) if len(v) > 1 else 0.0) if v else (float("nan"),) * 2
def col(r, c): return [float(x[c]) for x in r]

mine, notes = {}, []
for name, p in [("TGN", "results/tgn_wiki.csv"), ("DyRep", "results/dyrep_wiki.csv")]:
    r = rows(p); mine[name] = (*ms(col(r, "best_val_mrr")), *ms(col(r, "test_mrr")), len(r))
eb = rows("results/edgebank_wiki.csv")
for tag, key in [("inf", "EdgeBank_inf"), ("tw", "EdgeBank_tw")]:
    r = [x for x in eb if x["variant"] == tag]
    mine[key] = (*ms(col(r, "val_mrr")), *ms(col(r, "test_mrr")), len(r))

gm = rows("results/graphmixer_wiki.csv")
failed = [x for x in gm if x.get("failed", "").strip().lower() == "true"]
ok = [x for x in gm if x not in failed]
mine["GraphMixer"] = (*ms(col(ok, "val_mrr")), *ms(col(ok, "test_mrr")), len(ok))
allm, alls = ms(col(gm, "test_mrr"))
if gm and "failed" not in gm[0]:
    notes.append("WARNING: graphmixer_wiki.csv has no 'failed' column; all runs counted as OK.")

fmt = lambda a, s: f"{a:.4f} ± {s:.4f}"
out = ["| Model | Published val | Published test | My val | My test | n | Test gap / published std |",
       "|---|---|---|---|---|---|---|"]
for m in PUB:
    pv, pvs, pt, pts = PUB[m]; mv, sv, mt, stt, n = mine[m]
    pubv = f"{pv:.3f}" if pvs is None else f"{pv:.3f} ± {pvs:.3f}"
    pubt = f"{pt:.3f}" if pts is None else f"{pt:.3f} ± {pts:.3f}"
    gap = "n/a (deterministic)" if pts is None else (f"{(mt - pt) / pts:+.2f}" if n else "n/a")
    out.append(f"| {m} | {pubv} | {pubt} | {fmt(mv, sv)} | {fmt(mt, stt)} | {n} | {gap} |")
out.append("")
out.append(f"Published: TGB paper Table 2a, 5 runs. Mine: official TGB negatives/evaluator; "
           f"TGN/DyRep n={mine['TGN'][4]}, EdgeBank deterministic.")
if gm:
    out.append(f"GraphMixer: {len(gm)} runs, {len(failed)} failed (train ROC AUC < 0.55), "
               f"epochs_run={gm[0].get('epochs_run', '?')}. All runs: test MRR {fmt(allm, alls)}.")
out += notes
text = "\n".join(out); print(text)
os.makedirs(os.path.join(REPO, "notes"), exist_ok=True)
open(os.path.join(REPO, "notes", "baseline_comparison_table.md"), "w").write(text + "\n")
