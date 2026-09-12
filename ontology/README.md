# ontology/ — the approved ontology

**Roadmap Stage 5.** Still empty — and no longer for want of a draft.

**The draft is in `ontology/draft/`** (ADR-0057): nine OWL 2 RL modules.
Nothing has been approved, so nothing has moved up here. A module arrives when
a person signs it, one at a time.

## Is this still a section 43 ontology?

It was, in one specific and load-bearing place, until 2026-09-12. This
paragraph replaces the sentence that said the modules were *"nine OWL 2 RL
modules over the section 43 pilot, built from the 190 approved records in
`eval/gold/`"*, which by then was true of part of the draft and false of the
rest. The honest version has three parts.

**The class skeleton was never section 43.** `document.ttl`, `authority.ttl`,
`provenance.ttl`, `time.ttl` and `evaluation.ttl` model upstream's page / chunk
/ provision / unit shapes, the three kinds of authority, and the provenance
fields. They would be the same file for any Part of the Manual.

**The concept layer stopped being section 43 in S018.** ADR-0095 authored 78
concepts from the 53 Parts the boundary had hidden, and ADR-0098 added five
concept groups because 53 of the resulting 130 concepts fitted none of the
original four. `legal-concepts.ttl` carries nine classes for that reason.

**The relational layer was still section 43 until today, and it is the layer
that matters most.** `relations.ttl` is the closed list of predicates
extraction may draw from, and it was generated from `eval/gold/relationships.yaml`
alone — 35 signed records whose 37 source refs *all* point at `TMM/Part29`. So
the ontology's entire relational expressiveness was whatever section 43 had
happened to need: 14 terms, 6 of them used exactly once, with no way to say
that a concept is defined by a provision, that a step is performed by an
office, or that one must occur within a period. Two modules were also empty for
reasons that named the withdrawn boundary out loud — `evidence.ttl` cited
"Part 22 is explicitly out of the pilot scope draft" four days after ADR-0081
withdrew it.

**What changed (ADR-0109, ADR-0110).** `authored/relationships.yaml` now holds
219 relationships extracted deterministically from all 54 Parts, the Act and
the Regulations, and `relations.ttl` is generated from both registers with the
two halves kept apart: `tmk:ApprovedRelation` still means *an expert used this*
and still holds exactly 14 terms; `tmk:AuthoredRelation` means *a machine used
it and nobody has read a single record that does*. **No expert has read any of
the 219.** The counters are never added — `tmk:usageCount` keeps its meaning as
the signed count, and `tmk:authoredUsageCount` sits beside it.

Read `ontology/draft/GUIDE.md` for what it says, and
`data/derived/reports/ontology.md` for what it counts.
`data/derived/reports/relationships.md` is where the 219 come from and what is
weakest about them.

Modular RDF / RDFS / OWL 2 RL. One file per module so that reasoning scope can be
controlled per module:

```
ontology/examination.ttl      TradeMarkApplication, Examination, Examiner, Objection, ExaminationOutcome
ontology/legal-concepts.ttl   GroundOfRefusal, LegalTest, RelevantFactor, Exception, LegalProposition
ontology/evidence.ttl         Evidence, EvidenceCategory, EvidenceSubmission, EvidentiaryProposition
ontology/authority.ttl        Legislation, LegislativeProvision, JudicialDecision, ManualInstruction, Guidance, AuthorityStatus
ontology/document.ttl         Document, DocumentVersion, Chapter, Paragraph, Passage
ontology/time.ttl             effective / superseded / decision dates, version applicability
ontology/provenance.ttl       PROV-O plus the project fields in ADR-0011
ontology/relations.ttl        the approved relationship dictionary — the closed list
ontology/evaluation.ttl       competency questions, prohibited uses, relevance judgements
ontology/GUIDE.md             the human-readable ontology guide
```

`evaluation.ttl` is not in the roadmap's list and the draft adds it. It earns its
place by letting a prohibited output be a node with edges rather than a paragraph
in a YAML file — PU-0004 is only structurally detectable if the prohibition, the
question it attaches to and the passages involved are in one graph.

## Two constraints that come from the corpus, not the roadmap

1. **`ManualInstruction` and `LegislativeProvision` are disjoint**, and the
   distinction must survive all the way into retrieval output. The Manual states
   practice; it is not law and does not bind the Registrar's discretion (Q-12).
2. **The Document module maps onto upstream's actual shapes** — page, chunk,
   provision, unit — not onto an idealised chapter/section/paragraph tree. Manual
   headings are an unreliable structural guarantee (Q-10) and the addressable unit
   is `chunk_ref`, not "paragraph 4.3.12".

## Rules

- **OWL 2 RL, deliberately.** Scalable rule-based reasoning at the cost of
  expressiveness. Do not reach for constructs outside the profile; if you need
  them, that is an ADR, not an edit.
- **`relations.ttl` is a closed list, and since ADR-0109 it has two halves.**
  Extraction may only propose relationships from it. An open predicate set makes
  precision unmeasurable. `tmk:ApprovedRelation` is the expert-built half and a
  term joins it only when an expert approves a relationship that uses it;
  `tmk:AuthoredRelation` is the machine-written half and a term joins it the way
  any authored content arrives — a record with an envelope, stamped unreviewed.
  **A query that reads the term and not the class cannot tell them apart**, which
  is why the class is a class.
- **Domain and range restrictions are reasoning commitments**, not documentation.
  Under RL they license inferences; a careless range assertion silently
  manufactures classifications.
- **Generated, then approved.** Draft modules may be generated by script from
  approved vocabulary and relationship registers (RDFLib). Approval is by an
  ontology specialist *and* a domain expert. Humans review the model, not every
  individual graph record.
- **No LegalRuleML** (ADR-0009).
