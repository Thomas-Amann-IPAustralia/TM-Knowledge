# vocab/ — the approved controlled vocabulary

**Roadmap Stage 3.** Empty: nothing in the vocabulary is approved yet. The
working vocabulary is built into the graph from `eval/gold/concepts.yaml` (signed)
and `authored/concepts.yaml` (machine-written, unreviewed), and is counted in
`data/derived/reports/ontology.md`.

SKOS concept scheme: preferred labels, alternative labels, broader/narrower/
related, definitions, editorial notes, source references.

```
vocab/scheme.ttl        the concept scheme
vocab/concepts/*.ttl    concepts, grouped by area
vocab/register.yaml     id allocation — sequential, never reused
vocab/rejected.yaml     terms considered and rejected, with the reason
```

## Approved only

Everything here has been through `review/` and has a decision record. Candidate
clusters, YAKE output and LLM synonym proposals do not live here at any
confidence level (ADR-0007).

## Rules

- **Identifiers are opaque and permanent** (`tmkc:c-0042`), never derived from the
  preferred label. Labels get revised; ids must not (`docs/IDENTIFIERS.md` §3).
- **Every concept cites its sources** — the passages that define or delimit it, by
  upstream ref.
- **`skos:broader` is a commitment.** The explorer reads it as "is a kind of" and
  draws graph paths along it, so a passage about a narrower concept is offered for
  the broader one. Do not assert a hierarchy edge for filing convenience. (No OWL
  profile is claimed, ADR-0134.)
- **Keep the rejected register.** "Why isn't X a concept?" is asked repeatedly,
  and the answer is expensive to reconstruct.
- **Legally distinct concepts with similar language are the hard cases** and the
  reason humans review clusters at all. When two terms differ in legal effect but
  not in wording, record the distinction in an editorial note, not just in the
  labels.

## Australian English

Preferred labels follow the corpus. Spelling variants are `skos:altLabel`, not
corrections — matching against the Manual's own text depends on it.
