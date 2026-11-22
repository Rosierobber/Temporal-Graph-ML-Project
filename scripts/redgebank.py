import sys, math, time
import numpy as np

def load(name, tgb_path):
    if tgb_path not in sys.path: sys.path.insert(0, tgb_path)
    from tgb.linkproppred.dataset import LinkPropPredDataset
    from tgb.linkproppred.evaluate import Evaluator
    return LinkPropPredDataset(name=name, root="datasets"), Evaluator(name=name)

class Memory:
    """mode: 'inf' (EdgeBank-inf), 'tw' (EdgeBank-tw), 'recency' (recency inside window only), 'full' (R-EdgeBank)"""
    def __init__(self, rho, kappa, mode):
        self.rho, self.kappa, self.mode, self.M = rho, kappa, mode, {}
    def init(self, s, d, t):
        for a, b, c in zip(s.tolist(), d.tolist(), t.tolist()): self.M[(a, b)] = c
        self.W = self.rho * float(t.max() - t.min()); self.t_c = float(t.max())
    def update(self, s, d, t):
        for a, b, c in zip(s.tolist(), d.tolist(), t.tolist()): self.M[(a, b)] = c
        self.t_c = max(self.t_c, float(t.max()))
    def score(self, s, cands, t):
        M, W, lo = self.M, max(self.W, 1e-12), self.t_c - self.W
        out = np.zeros(len(cands), dtype=np.float64)
        for i, u in enumerate(cands.tolist()):
            lam = M.get((s, u))
            if lam is None: continue
            if self.mode == "inf": out[i] = 1.0
            elif lam >= lo: out[i] = 1.0 if self.mode == "tw" else 1.0 + (lam - lo) / W
            elif self.mode == "full": out[i] = math.exp(-(t - lam) / (self.kappa * W))
        return out

def evaluate(ds, ev, split, rho, kappa, mode, max_edges=None, batch=200):
    d = ds.full_data; S, D, T = d["sources"], d["destinations"], d["timestamps"]
    tr = np.where(ds.train_mask)[0]; va = np.where(ds.val_mask)[0]; te = np.where(ds.test_mask)[0]
    if not getattr(ds, "_ns_" + split, False):
        (ds.load_val_ns if split == "val" else ds.load_test_ns)(); setattr(ds, "_ns_" + split, True)
    mem = Memory(rho, kappa, mode); mem.init(S[tr], D[tr], T[tr])
    if split == "test":                                   # replay validation edges into memory
        for b in range(0, len(va), batch):
            i = va[b:b + batch]; mem.update(S[i], D[i], T[i])
    idx = (te if split == "test" else va)
    if max_edges: idx = idx[:max_edges]
    s_, d_, t_ = S[idx], D[idx], T[idx]
    ns = ds.negative_sampler; rr, seen = [], []; t0 = time.time()
    for b in range(0, len(idx), batch):
        sb, db, tb = s_[b:b + batch], d_[b:b + batch], t_[b:b + batch]
        negs = ns.query_batch(sb, db, tb, split_mode=split)
        for j in range(len(sb)):
            cands = np.concatenate([[db[j]], negs[j]])
            sc = mem.score(int(sb[j]), cands, float(tb[j]))
            seen.append((int(sb[j]), int(db[j])) in mem.M)
            rr.append(ev.eval({"y_pred_pos": np.array([sc[0]]), "y_pred_neg": sc[1:],
                               "eval_metric": ["mrr"]})["mrr"])
        mem.update(sb, db, tb)
    rr = np.array(rr)
    return {"mrr": float(rr.mean()), "rr": rr, "seen": np.array(seen), "secs": time.time() - t0, "n": len(rr)}
