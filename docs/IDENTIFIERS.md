# IDENTIFIERS — refs, IRIs and naming

Read before you write any identifier. Identifier mistakes are the most expensive
kind: they are cheap to fix before a graph exists and effectively permanent after.

Governing decision: **ADR-0005** — upstream refs are canonical; IRIs are minted
from them. The roadmap's `tmem:manual/2026-01/chapter-4/section-3/paragraph-12`
form is *not* used; see Q-02 for why.

## 1. Upstream refs — the canonical keys

These come from `manual-XtrACTor` and are stable across releases. This repo does
not invent, reformat or normalise them.

| Kind | Form | Example |
|---|---|---|
| Page | `TMM/Part<NN>/<n>` | `TMM/Part22/1` |
| Chunk | `TMM/Part<NN>/<n>/<n>/<n>` | `TMM/Part22/1/1/2` |
| Provision | `<INSTRUMENT>/<kind><number>` | `TMA1995/s41`, `TMR1995/r3A.3`, `TMR1995/sch2` |
| Unit | provision ref + subdivision | `TMA1995/s41(3)(a)` |

Two invariants upstream enforces, worth knowing because violating them means you
have constructed a ref rather than read one: an instrument must be able to hold
that *kind* of provision (`TMR1995/s224` is not a thing), and to express that
*number* (`TMA1995/s4.7` is not — the Act uses no dots, the Regulations always
do).

The Manual↔legislation join is plain string equality on these. A chunk's
`provisions[].id` **is** a provision `ref`, with no transformation and no lookup
table. Preserve that. Any code path that lowercases, strips, pads or re-splits a
ref has broken the join.

## 2. IRI minting

One rule, applied mechanically and reversibly:

```
IRI  =  <BASE> + "ref/" + <upstream ref verbatim>
```

```
TMM/Part22/1/1/2   →  <BASE>ref/TMM/Part22/1/1/2
TMA1995/s41(3)(a)  →  <BASE>ref/TMA1995/s41(3)(a)
```

- Do **not** percent-encode. `(` and `)` are legal in an IRI path. Some tooling
  will encode them anyway; a round-trip test (`ref → IRI → ref`) belongs in
  `tests/` from the first commit that mints an IRI.
- Do **not** case-fold, slugify or rewrite separators.
- The mapping is a function in one module. Nothing else constructs IRIs by string
  concatenation.

### Base IRI

**Unconfirmed — see HANDOFF Q7.** Proposed production base:

```
https://data.ipaustralia.gov.au/tmk/
```

Persistent IRIs require control of the domain they sit under, which is an
organisational decision, not a technical one. Until it is confirmed, the base
lives in exactly one constant, read from configuration, and no other file
hard-codes it. Changing it later must be a config change and a graph rebuild, not
a find-and-replace across serialised RDF.

### Prefixes

| Prefix | Expands to | For |
|---|---|---|
| `tmk:` | `<BASE>ns/` | Ontology terms defined by this project (classes, properties) |
| `tmkr:` | `<BASE>ref/` | Resources identified by an upstream ref |
| `tmkc:` | `<BASE>concept/` | SKOS concepts |
| `tmkp:` | `<BASE>prop/` | Propositions and candidate rules |
| `tmka:` | `<BASE>assertion/` | Individual assertions with provenance |
| `tmkg:` | `<BASE>graph/` | Named graphs |

Standard prefixes keep their usual bindings: `skos:`, `prov:`, `owl:`, `rdfs:`,
`sh:`, `dcterms:`.

## 3. Identifiers this repo mints

Anything not derived from an upstream ref needs its own identifier. Two patterns,
chosen by whether a human will ever cite the thing.

**Human-facing, allocated once, never reused** — SKOS concepts, ontology terms,
approved rules. Zero-padded sequential within a register file:

```
tmkc:c-0042      a concept, whose skos:prefLabel may change without the id changing
tmkp:rule-0007   an approved rule
```

Never derive these from the preferred label. Labels get revised; identifiers must
not. The register file is the allocator — allocate by appending, and never fill a
gap left by a withdrawn concept.

**Machine-generated candidates, content-addressed** — so that re-running a
pipeline over unchanged input produces the same identifiers and does not litter
`review/` with duplicates:

```
id = first 16 hex of sha256( source_ref | span_start | span_end | method | normalised_value )
tmka:cand-3f9a1c04e7b2d5a8
```

The consequence is the desirable one: a re-run over unchanged input is a no-op,
and any new identifier means something genuinely changed — the source text, the
span, the method, or the extracted value.

> **Under review — do not implement this formula yet. ADR-0020, HANDOFF Q10.**
> ADR-0019 put three keyphrase extractors on the same text, so `method` in the
> hash mints three ids for one span: three `review/` entries for one candidate,
> and the cross-method agreement that the ensemble exists to capture invisible on
> all of them. ADR-0020 proposes dropping `method` from the hash — identity
> becomes `source_ref | span_start | span_end | normalised_value`, and the methods
> that found it become a set-valued field carrying each one's score and model
> version. Parallel-track P3 implements this module; it must wait on Q10.

## 4. Where refs live and where IRIs live

- **Registers, review queues, CSV, JSON, config, test fixtures: store the ref.**
  `TMM/Part22/1/1/2`, not an IRI. Refs are shorter, greppable, diff-readable and
  survive a base-IRI change.
- **RDF only: IRIs.** Minted at serialisation time by the one module in §2.

This keeps the base IRI question (Q7) from blocking work: nothing but the RDF
emitter cares about it.

## 5. Versioning an assertion's source

An assertion records the ref *and* the `source_content_hash` it was made against
(ADR-0011). The ref says which passage; the hash says which state of that passage.
When upstream re-cuts the corpus and a hash changes, every assertion resting on
that passage is stale and returns to review. That check is the whole mechanism for
Stage 10 incremental reprocessing — without the stored hash there is no way to
tell a changed passage from an unchanged one short of re-extracting everything.

Note there is no corpus-level version to record instead (Q-05): pin the upstream
release in `data/upstream/` (ADR-0004) and hash per passage.

## 6. File and directory naming

Lowercase, hyphenated, no spaces (ADR-0012). Where a filename encodes a ref, keep
the ref's own casing and replace `/` with `_`:

```
review/candidates/relations/TMM_Part22_1_1_2.json
```

RDF serialisations use the extension of their format (`.ttl` preferred for
hand-readable files, `.nq` where named graphs must survive the round trip).
