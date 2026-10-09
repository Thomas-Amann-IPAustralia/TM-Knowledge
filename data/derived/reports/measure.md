# The value measurement — does the ontology make search better?

Rankings taken on 2026-10-09. 129 questions, every pooled passage graded 0–3 by `gpt-6.1-sol` (2344 grades over 129 pools). Three systems, fixed before any passage was judged: **keyword** (BM25), **hybrid** (keyword + vectors — good search with no ontology) and **ontology** (hybrid + concept recognition, query expansion and concept-linked passages). Intervals are paired bootstrap 95%; ✓ means the difference is established, ✗ that it is established the other way.

## nDCG@10 — the quality of the top ten

| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |
|---|---|---|---|---|---|---|
| all | 129 | 0.725 | 0.844 | 0.803 | -0.041 [-0.067, -0.017] ✗ | +0.079 [+0.042, +0.116] ✓ |
| cross_part | 30 | 0.728 | 0.832 | 0.778 | -0.054 [-0.116, -0.000] ✗ | +0.050 [-0.015, +0.125] |
| impact | 30 | 0.732 | 0.837 | 0.802 | -0.036 [-0.099, +0.017] | +0.070 [-0.023, +0.171] |
| lookup | 30 | 0.773 | 0.894 | 0.820 | -0.075 [-0.129, -0.025] ✗ | +0.046 [-0.015, +0.110] |
| problem | 29 | 0.677 | 0.848 | 0.827 | -0.021 [-0.055, +0.010] | +0.151 [+0.081, +0.228] ✓ |
| signed | 10 | 0.686 | 0.735 | 0.766 | +0.030 [+0.008, +0.055] ✓ | +0.080 [-0.024, +0.177] |

## Recall@10 — the share of relevant passages found in the top ten

| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |
|---|---|---|---|---|---|---|
| all | 128 | 0.644 | 0.791 | 0.738 | -0.053 [-0.096, -0.014] ✗ | +0.094 [+0.043, +0.147] ✓ |
| cross_part | 30 | 0.624 | 0.719 | 0.672 | -0.047 [-0.133, +0.034] | +0.048 [-0.059, +0.158] |
| impact | 30 | 0.668 | 0.796 | 0.721 | -0.075 [-0.178, +0.009] | +0.053 [-0.044, +0.155] |
| lookup | 30 | 0.706 | 0.871 | 0.786 | -0.085 [-0.189, +0.017] | +0.080 [-0.032, +0.200] |
| problem | 28 | 0.591 | 0.832 | 0.791 | -0.041 [-0.099, +0.010] | +0.201 [+0.088, +0.315] ✓ |
| signed | 10 | 0.594 | 0.642 | 0.696 | +0.054 [-0.011, +0.129] | +0.102 [-0.068, +0.282] |

Recall counts only questions with at least one relevant passage in the pool. `signed` is the expert's ten retrieval questions, run as a cross-check — they were not written for this benchmark and are not in it.

## What changed — the ontology system against other rankings, on the same grades

Each row scores another ranking of the same questions against the same grades, so the difference is the change in the system, not in the judge or the pool.

| Ranking | n | nDCG@10 then | now | now − then | Recall@10 now − then |
|---|---|---|---|---|---|
| `ontology_previous` — the ontology system's top ten as last measured (2026-10-07, commit 3c30aca) | 129 | 0.794 | 0.803 | +0.010 [-0.005, +0.026] | +0.010 [-0.010, +0.030] |
| `ontology_unaudited` — the same ontology system over the relationships as they stood before the edge audit was applied (commit e99df13) | 129 | 0.803 | 0.803 | +0.001 [-0.007, +0.009] | -0.003 [-0.017, +0.013] |

By kind of question, `ontology_previous`:

| Questions | n | then | now | now − then |
|---|---|---|---|---|
| all | 129 | 0.794 | 0.803 | +0.010 [-0.005, +0.026] |
| cross_part | 30 | 0.759 | 0.778 | +0.019 [-0.011, +0.053] |
| impact | 30 | 0.796 | 0.802 | +0.006 [-0.025, +0.036] |
| lookup | 30 | 0.827 | 0.820 | -0.007 [-0.034, +0.018] |
| problem | 29 | 0.808 | 0.827 | +0.019 [-0.014, +0.067] |
| signed | 10 | 0.749 | 0.766 | +0.017 [+0.002, +0.034] ✓ |

By kind of question, `ontology_unaudited`:

| Questions | n | then | now | now − then |
|---|---|---|---|---|
| all | 129 | 0.803 | 0.803 | +0.001 [-0.007, +0.009] |
| cross_part | 30 | 0.774 | 0.778 | +0.004 [-0.006, +0.015] |
| impact | 30 | 0.799 | 0.802 | +0.002 [-0.021, +0.023] |
| lookup | 30 | 0.814 | 0.820 | +0.005 [-0.009, +0.020] |
| problem | 29 | 0.834 | 0.827 | -0.007 [-0.027, +0.012] |
| signed | 10 | 0.771 | 0.766 | -0.005 [-0.020, +0.009] |

## Cross-check with no model judge — the expert's own evidence lists

The 10 signed retrieval questions, each system scored against only the passages the expert listed as required (listed = relevant, anything else = not). No model graded anything here; it is coarse, and ten questions are few.

| System | nDCG@10 | Recall@10 |
|---|---|---|
| keyword | 0.517 | 0.583 |
| hybrid | 0.537 | 0.583 |
| ontology | 0.538 | 0.583 |
| ontology_previous | 0.517 | 0.550 |
| ontology_unaudited | 0.553 | 0.667 |

ontology − hybrid +0.001 [-0.105, +0.101]; ontology − keyword +0.021 [-0.109, +0.173] (nDCG@10).

## Where the ontology helped most

| Question | Kind | hybrid | ontology |
|---|---|---|---|
| When two series marks use the same common surname and initial, is that usually the part people focus on to compare them? | cross_part | 0.648 | 0.910 |
| What do I do if the goods and services wording in my international trade mark application does not fit the usual classification terms? | problem | 0.760 | 0.934 |
| How long do I have to notify a provisional refusal if it is based on an opposition? | lookup | 0.691 | 0.857 |
| What happens to the time left on a deferred acceptance date when the reason for the deferment ends? | impact | 0.827 | 0.972 |

## Where it hurt most

| Question | Kind | hybrid | ontology |
|---|---|---|---|
| If the Registrar issues a notice to produce, who gets it and what has to happen next? | impact | 0.897 | 0.239 |
| Can I file one trade mark application in more than one class? | cross_part | 0.868 | 0.281 |
| What happens if a required fee is underpaid and the Registrar does not tell us within 14 working days? | lookup | 0.987 | 0.508 |
| Who has to sign the supporting declaration for an application, and what does it need to say about other traders using the mark? | impact | 0.885 | 0.435 |
