# Temporal-Graph-ML-Project

Advanced ML term project, Topic 3: do complex temporal graph models beat simple memory?
Benchmark: Temporal Graph Benchmark (TGB; Huang et al., NeurIPS 2023 D&B), datasets tgbl-wiki (small) and tgbl-review (medium), official splits, negatives and MRR evaluator.
Author: [name, roll number]

## Contribution
R-EdgeBank keeps EdgeBank's memory but ranks candidates by how recently the pair was last seen (pairs never seen are ranked last).
It has no trainable parameters and no hyperparameters. Ablation: EdgeBank (window) -> recency inside the window -> recency without a window.

## Results (test MRR, mean +- sample std over seeds)
tgbl-wiki:
    EdgeBank inf / window   0.4947 / 0.5710 (deterministic; published 0.495 / 0.571)
    TGN                     0.3328 +- 0.0124 (n=3); per-query reruns 0.3297 +- 0.0201 (n=3); published 0.396 +- 0.060
    DyRep                   0.0399 +- 0.0143 (n=3); published 0.050 +- 0.017
    GraphMixer (5 epochs)   0.1577 +- 0.0325 (seeds 1,3,4); seed 2 failed twice (0.002); published 0.118 +- 0.002
    R-EdgeBank (mine)       0.7248 (recency inside window: 0.7069)
tgbl-review:
    EdgeBank inf / window   0.0229 / 0.0253 (deterministic; matches the published values)
    TGN (5-epoch cap)       0.3779 +- 0.0110 (n=3); published 0.349 +- 0.020
    DyRep (5-epoch cap)     0.1733 +- 0.0372 (n=3); published 0.220 +- 0.030
    R-EdgeBank (mine)       0.0284
    GraphMixer              not run (compute budget)
Recurring / novel split on tgbl-wiki (query-time definition): see results/rq2_slices_wiki.csv.

## Reproduce the tables
    bash reproduce_main_table.sh
This rebuilds the comparison tables from the stored per-seed CSV files (notes/baseline_comparison_table.md, notes/review_comparison_table.md). It does not retrain.
Training commands (run from third_party/TGB with PYTHONPATH=.):
    python examples/linkproppred/tgbl-wiki/edgebank.py --data tgbl-wiki --seed S [--mem_mode fixed_time_window]
    python examples/linkproppred/tgbl-wiki/tgn.py --data tgbl-wiki --seed S
    python examples/linkproppred/tgbl-review/tgn.py --data tgbl-review --seed S --num_epoch 5 --num_run 1
    python examples/linkproppred/tgbl-review/dyrep.py --data tgbl-review --seed S --num_epoch 5 --num_run 1
GraphMixer: fpour/TGB_Baselines at commit d2022fae4a3311185f611bab733e267938251f42:
    python train_tgb_lpp_original.py --dataset_name tgbl-wiki --model_name GraphMixer --num_epochs 5 --num_runs 1 --seed S --gpu G
Method: scripts/redgebank.py (sweep and test code is in notebooks/main_experiments.ipynb). scripts/tgn_wiki_perquery.py is TGB's tgn.py plus a hook that saves per-query reciprocal ranks.
Seeds: 1-3 (TGN, DyRep, EdgeBank); 1-4 (GraphMixer); 1, 3, 4 (review TGN, DyRep).

## Environment and compute
Kaggle, two Tesla T4 GPUs, two accounts (logs/environment.txt, logs/environment_accountB.txt); Python 3.13, torch 2.11.0, torch_geometric 2.8.1, py-tgb 2.3.0, torch_scatter 2.1.2. Stored wiki TGN/DyRep runs: see logs/versions.txt.
Time per run: GraphMixer wiki about 6.5 h (about 19,000 s train+val, 3,750 s test); TGN wiki 0.5-0.8 h; TGN review about 5.4 h; DyRep review about 4.5-4.7 h; R-EdgeBank about 8 s per wiki test pass on CPU. TGN review epoch 1: 1,203 s training + 2,108 s validation.
Peak GPU memory (review): TGN about 6.1 GB, DyRep about 4.6 GB. Parameter counts: not measured.

## Deviations and limitations
- GraphMixer: 5 epochs (repo default 25; the published setup does not state epochs); seed 2 did not train in two attempts (train ROC AUC 0.50).
- Review TGN/DyRep: 5-epoch cap; GraphMixer not run.
- Logs for review TGN seed 3 and DyRep seeds 3 and 4 were lost when a session ended; values come from console output (notes/review_runs_provenance.md).
- R-EdgeBank on review: window ratio tuned on the first 100,000 validation edges only. EdgeBank and R-EdgeBank are deterministic (no std).
- My surprise-index computations do not reproduce the paper's 0.108 (see the paper).
