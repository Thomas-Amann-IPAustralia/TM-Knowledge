# The live reading — does a model's reading of the question make search better?

Rankings taken on 2026-10-12. 129 benchmark questions, each read once by `gpt-6.1-sol` (prompt `reading-v1`, effort low), the picks checked as the page checks them. Every passage any of the three systems ranks in its top ten is graded 0–3 by `gpt-6.1-sol` (2219 grades). The systems are the page's own, with no vectors: **keyword** (BM25), **names** (the ontology system starting from ideas named in the question) and **reading** (the same, starting also from the ideas the model read). Intervals are paired bootstrap 95%; ✓ means the difference is established, ✗ that it is established the other way. **3 pooled passages have no grade** (BN-0015) and score 0: the judge's answer for them was refused because it also graded passages not in its pool.

## What the reading found

| Questions | n | a specific idea by name | the reading added an idea | of those, none by name | ideas added | set aside |
|---|---|---|---|---|---|---|
| all | 129 | 76 | 101 | 45 | 182 | 0 |
| cross_part | 30 | 20 | 29 | 10 | 58 | 0 |
| impact | 30 | 17 | 23 | 10 | 42 | 0 |
| lookup | 30 | 19 | 22 | 9 | 34 | 0 |
| problem | 29 | 13 | 22 | 13 | 40 | 0 |
| signed | 10 | 7 | 5 | 3 | 8 | 0 |

## nDCG@10 — the quality of the top ten

| Questions | n | keyword | names | reading | reading − names | names − keyword | reading − keyword |
|---|---|---|---|---|---|---|---|
| all | 129 | 0.702 | 0.661 | 0.701 | +0.040 [+0.009, +0.070] ✓ | -0.041 [-0.067, -0.014] ✗ | -0.001 [-0.039, +0.036] |
| cross_part | 30 | 0.694 | 0.633 | 0.676 | +0.043 [-0.023, +0.111] | -0.061 [-0.118, -0.009] ✗ | -0.018 [-0.097, +0.063] |
| impact | 30 | 0.706 | 0.678 | 0.715 | +0.037 [-0.040, +0.113] | -0.028 [-0.090, +0.041] | +0.009 [-0.087, +0.109] |
| lookup | 30 | 0.766 | 0.679 | 0.700 | +0.021 [-0.030, +0.073] | -0.087 [-0.137, -0.041] ✗ | -0.066 [-0.127, -0.007] ✗ |
| problem | 29 | 0.656 | 0.651 | 0.698 | +0.047 [-0.008, +0.107] | -0.005 [-0.050, +0.034] | +0.042 [-0.025, +0.109] |
| signed | 10 | 0.655 | 0.674 | 0.748 | +0.074 [+0.005, +0.161] ✓ | +0.020 [-0.033, +0.075] | +0.094 [+0.003, +0.189] ✓ |

## Recall@10 — the share of relevant passages found in the top ten

| Questions | n | keyword | names | reading | reading − names | names − keyword | reading − keyword |
|---|---|---|---|---|---|---|---|
| all | 128 | 0.585 | 0.519 | 0.568 | +0.049 [-0.004, +0.100] | -0.066 [-0.107, -0.028] ✗ | -0.017 [-0.072, +0.034] |
| cross_part | 30 | 0.516 | 0.449 | 0.507 | +0.058 [-0.028, +0.152] | -0.067 [-0.129, -0.009] ✗ | -0.009 [-0.114, +0.097] |
| impact | 30 | 0.621 | 0.524 | 0.622 | +0.098 [-0.036, +0.226] | -0.097 [-0.194, -0.010] ✗ | +0.001 [-0.123, +0.118] |
| lookup | 30 | 0.696 | 0.562 | 0.536 | -0.026 [-0.155, +0.104] | -0.134 [-0.244, -0.037] ✗ | -0.160 [-0.268, -0.057] ✗ |
| problem | 28 | 0.522 | 0.523 | 0.586 | +0.063 [-0.021, +0.143] | +0.000 [-0.067, +0.059] | +0.064 [-0.042, +0.161] |
| signed | 10 | 0.533 | 0.579 | 0.634 | +0.055 [-0.050, +0.186] | +0.046 [-0.038, +0.152] | +0.101 [-0.048, +0.255] |

## Only the questions the reading changed

On a question where the reading added no idea, *reading* and *names* rank the same passages, so the difference is zero there by construction. Here are the questions where it added one.

| n | names | reading | reading − names (nDCG@10) | reading − names (Recall@10) |
|---|---|---|---|---|
| 101 | 0.638 | 0.689 | +0.051 [+0.012, +0.089] ✓ | +0.062 [-0.006, +0.127] |

## What this does not show

- The page's search has no meaning-vectors; the measured system (`measure.md`) has. These numbers are for the page's configuration and are not comparable with that report's.
- The benchmark questions were written beside the ontology and often use its names, so the reading has less to add here than on a question typed the way a person asks.
- The grades are a model's, and the questions are model-written. `signed` is the expert's ten retrieval questions, run as a cross-check.
- Each question was read once; a second reading could pick differently.
