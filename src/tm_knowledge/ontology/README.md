# src/tm_knowledge/ontology/ — Stages 5, 6 and 9

Everything here is a transformation. It reads the pinned snapshot and the
approved gold set and writes RDF. It authors nothing.

| module | does |
|---|---|
| `namespaces.py` | prefix bindings, read from `refs.PREFIXES` so they cannot drift |
| `tbox.py` | loads `ontology/draft/*.ttl`, rebasing IRIs onto the configured base |
| `relations.py` | generates `relations.ttl` from the approved relationship register |
| `build.py` | the graph: source from the snapshot, approved from `eval/gold/` |
| `validate.py` | the SHACL gate, with the harness's three severities |
| `rules.py` | runs the candidate CONSTRUCT rules into the inferred graph |
| `ask.py` | runs the competency queries and reports query coverage |
| `report.py` | generates `data/derived/reports/ontology.md` |
| `cli.py` | `tmk-graph`, `tmk-shacl`, `tmk-ask`, `tmk-ontology-relations`, `tmk-ontology-report` |

## The three properties these modules exist to keep

1. **Upstream's trust metadata survives.** A citation is a node carrying
   `extraction` and `certainty`, never a bare edge. `tmk:citesProvision` is
   emitted alongside as a shortcut, derived from the node and never the reverse.
2. **A missing judgement stays missing.** Five approved relationships have no
   modality and the graph asserts none for them.
3. **Nothing enters the approved graph that a person did not sign.** Every
   assertion carries `approvedBy` and `approvedDate` off the record, never
   defaulted.

Each has a test that fails if it stops being true — `test_ontology_build.py`.

## Do not

- Construct an IRI by concatenation. `refs.to_iri` and `namespaces.ref_node`,
  because `#` must be escaped in one chunk ref in five (ADR-0023).
- Glob for modules, shapes or rules. All three lists are fixed: a file appearing
  on disk and being picked up silently is how an unreviewed artefact joins the
  gate, and a deleted one stops being noticed.
- Loosen a shape to make a run pass. A failing shape is a finding.
- Add `rdflib` or `pyshacl` to the core dependencies. They are the `[rdf]`
  extra, so the core install stays at three (ADR-0056).
