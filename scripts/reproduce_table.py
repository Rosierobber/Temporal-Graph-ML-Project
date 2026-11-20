#!/usr/bin/env python3
import os, csv, statistics as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PUB = {
    "EdgeBank_inf": (0.527, None, 0.495, None),
    "EdgeBank_tw":  (0.600, None, 0.571, None),
    "TGN":          (0.435, 0.069, 0.396, 0.060),
    "DyRep":        (0.072, 0.009, 0.050, 0.017),
    "GraphMixer":   (0.113, 0.003, 0.118, 0.002),
}

def read_rows(p):
    full = os.path.join(REPO_DIR, p)
    return list(csv.DictReader(open(full))) if os.path.exists(full) else []

def ms(v):
    return (st.mean(v), st.stdev(v) if len(v) > 1 else 0.0) if v else (0.0, 0.0)

mine = {}
for name, p in [("TGN", "results/tgn_wiki.csv"), ("DyRep", "results/dyrep_wiki.csv")]:
    r = read_rows(p)
    mine[name] = (*ms([float(x["best_val_mrr"]) for x in r]), *ms([float(x["test_mrr"]) for x in r]), len(r))

eb = read_rows("results/edgebank_wiki.csv")
for tag, key in [("inf", "EdgeBank_inf"), ("tw", "EdgeBank_tw")]:
    r = [x for x in eb if x.get("variant") == tag]
    mine[key] = (*ms([float(x["val_mrr"]) for x in r]), *ms([float(x["test_mrr"]) for x in r]), len(r))

gm = read_rows("results/graphmixer_wiki.csv")
ok = [x for x in gm if x.get("failed", "").lower() == "false"]
mine["GraphMixer"] = (*ms([float(x["val_mrr"]) for x in ok]), *ms([float(x["test_mrr"]) for x in ok]), len(ok))
gm_all_t = ms([float(x["test_mrr"]) for x in gm])

fmt = lambda a, s: f"{a:.4f} ± {s:.4f}"
lines = ["| Model | Published val | Published test | My val | My test | n | Test gap / published std |",
         "|---|---|---|---|---|---|---|"]
for m in ["EdgeBank_inf", "EdgeBank_tw", "TGN", "DyRep", "GraphMixer"]:
    pv, pvs, pt, pts = PUB[m]
    mv, sv, mt, stt, n = mine.get(m, (0.0, 0.0, 0.0, 0.0, 0))
    pub_v = f"{pv:.3f}" if pvs is None else f"{pv:.3f} ± {pvs:.3f}"
    pub_t = f"{pt:.3f}" if pts is None else f"{pt:.3f} ± {pts:.3f}"
    gap = f"{(mt - pt) / pts:+.2f}" if (pts and n > 0) else "n/a (deterministic)"
    label = m + (" *" if m == "GraphMixer" else "")
    lines.append(f"| {label} | {pub_v} | {pub_t} | {fmt(mv, sv)} | {fmt(mt, stt)} | {n} | {gap} |")

table = "\n".join(lines) + f"""\n
Published values: Huang et al., NeurIPS 2023 D&B, Table 2a (tgbl-wiki, 5 runs).
Mine: TGB default settings and official evaluator/negatives. EdgeBank is deterministic (3 seeds, identical results).
TGN and DyRep: seeds 1-3. "My val" for TGN/DyRep is the best validation epoch; for GraphMixer it is the single epoch's validation MRR.
* GraphMixer: fpour/TGB_Baselines (DyGLib-based), 1 epoch per seed (limited budget), seeds 1-5. Seed 2 did not train
  (train ROC AUC 0.50, test MRR 0.002) and is excluded from this row; it is reported in results/graphmixer_wiki.csv.
  All 5 runs: test MRR {gm_all_t[0]:.4f} ± {gm_all_t[1]:.4f}.
"""
print(table)
