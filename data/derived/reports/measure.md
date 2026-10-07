# The value measurement — does the ontology make search better?

129 questions, every pooled passage graded 0–3 by `gpt-6.1-sol` (2236 grades over 129 pools). Three systems, fixed before any passage was judged: **keyword** (BM25), **hybrid** (keyword + vectors — good search with no ontology) and **ontology** (hybrid + concept recognition, query expansion and concept-linked passages). Intervals are paired bootstrap 95%; ✓ means the difference is established, ✗ that it is established the other way.

## nDCG@10 — the quality of the top ten

| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |
|---|---|---|---|---|---|---|
| all | 129 | 0.726 | 0.845 | 0.795 | -0.050 [-0.079, -0.024] ✗ | +0.069 [+0.031, +0.108] ✓ |
| cross_part | 30 | 0.730 | 0.834 | 0.761 | -0.074 [-0.139, -0.014] ✗ | +0.031 [-0.041, +0.113] |
| impact | 30 | 0.734 | 0.840 | 0.798 | -0.041 [-0.117, +0.021] | +0.065 [-0.027, +0.162] |
| lookup | 30 | 0.774 | 0.896 | 0.828 | -0.067 [-0.112, -0.026] ✗ | +0.054 [+0.000, +0.113] ✓ |
| problem | 29 | 0.677 | 0.849 | 0.810 | -0.039 [-0.094, +0.007] | +0.132 [+0.052, +0.214] ✓ |
| signed | 10 | 0.686 | 0.735 | 0.749 | +0.013 [-0.019, +0.045] | +0.063 [-0.044, +0.166] |

## Recall@10 — the share of relevant passages found in the top ten

| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |
|---|---|---|---|---|---|---|
| all | 128 | 0.651 | 0.801 | 0.740 | -0.061 [-0.106, -0.018] ✗ | +0.089 [+0.035, +0.145] ✓ |
| cross_part | 30 | 0.637 | 0.734 | 0.653 | -0.081 [-0.184, +0.019] | +0.017 [-0.099, +0.137] |
| impact | 30 | 0.675 | 0.803 | 0.734 | -0.069 [-0.176, +0.023] | +0.059 [-0.039, +0.161] |
| lookup | 30 | 0.711 | 0.876 | 0.791 | -0.085 [-0.170, -0.000] ✗ | +0.080 [-0.023, +0.192] |
| problem | 28 | 0.595 | 0.846 | 0.801 | -0.045 [-0.124, +0.027] | +0.205 [+0.081, +0.335] ✓ |
| signed | 10 | 0.594 | 0.642 | 0.694 | +0.052 [-0.055, +0.146] | +0.100 [-0.082, +0.290] |

Recall counts only questions with at least one relevant passage in the pool. `signed` is the expert's ten retrieval questions, run as a cross-check — they were not written for this benchmark and are not in it.

## Where the ontology helped most

| Question | Kind | hybrid | ontology |
|---|---|---|---|
| When two series marks use the same common surname and initial, is that usually the part people focus on to compare them? | cross_part | 0.648 | 0.908 |
| Which Registrar decisions can I take to court, and what happens if there is no appeal right in the Act? | impact | 0.654 | 0.878 |
| Could a name or symbol in my mark be left out if it is likely to confuse people? | problem | 0.693 | 0.869 |
| What do I do if the goods and services wording in my international trade mark application does not fit the usual classification terms? | problem | 0.760 | 0.908 |

## Where it hurt most

| Question | Kind | hybrid | ontology |
|---|---|---|---|
| If the Registrar issues a notice to produce, who gets it and what has to happen next? | impact | 0.897 | 0.120 |
| Can I object if the problem is really about a similar business name, not what’s in the mark itself? | problem | 0.857 | 0.305 |
| Can I file one trade mark application in more than one class? | cross_part | 0.868 | 0.324 |
| Who has to sign the supporting declaration for an application, and what does it need to say about other traders using the mark? | impact | 0.885 | 0.383 |
