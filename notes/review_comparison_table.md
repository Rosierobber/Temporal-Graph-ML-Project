| Model | Published val | Published test | My val | My test | n | Test gap / published std |
|---|---|---|---|---|---|---|
| EdgeBank_inf | 0.0229 | 0.0229 | 0.0229 ± 0.0000 | 0.0229 ± 0.0000 | 1 | n/a (deterministic) |
| EdgeBank_tw | 0.0242 | 0.0253 | 0.0242 ± 0.0000 | 0.0253 ± 0.0000 | 1 | n/a (deterministic) |
| TGN | 0.313 ± 0.012 | 0.349 ± 0.020 | 0.3285 ± 0.0053 | 0.3779 ± 0.0110 | 3 | +1.44 |
| DyRep | 0.216 ± 0.031 | 0.220 ± 0.030 | 0.1942 ± 0.0177 | 0.1733 ± 0.0372 | 3 | -1.56 |
| GraphMixer | 0.428 | 0.521 | not run (compute budget) | | 0 | n/a |
| R-EdgeBank (mine) | | | | 0.0284 | 1 | deterministic |

TGN and DyRep: 5-epoch cap (published setup does not state epochs), seeds 1, 3, 4, Tesla T4.
GraphMixer was not run on review (compute budget). R-EdgeBank: rho tuned on the first 100k validation edges.
