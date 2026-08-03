# vocab/ — the approved controlled vocabulary

**Roadmap Stage 3.** Empty.

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
- **`skos:broader` is a reasoning commitment.** Under OWL 2 RL it propagates
  relevance: a passage about a narrower concept becomes relevant to the broader
  one. Do not assert a hierarchy edge for filing convenience.
- **Keep the rejected register.** "Why isn't X a concept?" is asked repeatedly,
  and the answer is expensive to reconstruct.
- **Legally distinct concepts with similar language are the hard cases** and the
  reason humans review clusters at all. When two terms differ in legal effect but
  not in wording, record the distinction in an editorial note, not just in the
  labels.

## Australian English

Preferred labels follow the corpus. Spelling variants are `skos:altLabel`, not
corrections — matching against the Manual's own text depends on it.
