| Model | Published val | Published test | My val | My test | n | Test gap / published std |
|---|---|---|---|---|---|---|
| EdgeBank_inf | 0.527 | 0.495 | 0.5267 ± 0.0000 | 0.4947 ± 0.0000 | 3 | n/a (deterministic) |
| EdgeBank_tw | 0.600 | 0.571 | 0.5997 ± 0.0000 | 0.5710 ± 0.0000 | 3 | n/a (deterministic) |
| TGN | 0.435 ± 0.069 | 0.396 ± 0.060 | 0.3852 ± 0.0086 | 0.3328 ± 0.0124 | 3 | -1.05 |
| DyRep | 0.072 ± 0.009 | 0.050 ± 0.017 | 0.0508 ± 0.0199 | 0.0399 ± 0.0143 | 3 | -0.60 |
| GraphMixer | 0.113 ± 0.003 | 0.118 ± 0.002 | 0.1635 ± 0.0229 | 0.1577 ± 0.0325 | 3 | not comparable (see text) |

Published: TGB paper Table 2a, 5 runs. Mine: official TGB negatives/evaluator; TGN/DyRep n=3, EdgeBank deterministic.
GraphMixer: 4 runs, 1 failed (train ROC AUC < 0.55), epochs_run=5. All runs: test MRR 0.1188 ± 0.0823.
