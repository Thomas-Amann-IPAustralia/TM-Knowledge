# Owner's notes on three parked questions — issue #12, 2026-09-08

**Who wrote it:** Thomas Amann (`@Thomas-Amann-IPAustralia`), the repo owner.
**When:** 2026-09-08, in the body of
[issue #12](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/issues/12).
**Relayed by:** session S012, copied from the issue body unchanged.
**Why it is here and not in `review/rulings/`:** it was typed into the issue by
hand, outside the form's machine-readable block, so `tmk-ruling` neither sees it
nor should. `review/rulings/2026-09-08-issue-12.yaml` is the transcription of the
seven answers the form composed; this file is the three the owner wrote himself.
Both cite the same issue, which is the single artefact.

**What it answers:** OQ-0014, OQ-0015 and OQ-0016 — all three marked
`status: parked`, `needs: expert` in `review/questions/open-questions.yaml`, and
so deliberately given no control on the form. The owner answered them anyway.
That is his to do: they were parked at his own instruction pausing the expert
round, and OQ-0014 and OQ-0016 are scope questions rather than statements of law.
Where a note does turn on trade marks practice, it is recorded and not acted on
— see §"How each was read", below, and ADR-0074.

**The third heading is misnumbered.** The owner labelled two notes `OQ-0015`. The
second of the two carries OQ-0016's title word for word ("Nine role terms with no
definitions — Registrar, Delegate, Examiner and more") and the first points
forward to it (`see "OQ-0016`), so the second is OQ-0016. The owner confirmed
this directly when handing the issue over: *"answering Question 14, 15 and 16
(accidentally recorded as OQ-0015 too)"*. The words below stay exactly as typed;
the reading is recorded here and nowhere else.

---

## The owner's words, verbatim

> - **OQ-0014 — Where exactly does section 43 stop?**
> If we consider section 43 the central node in a network, it's network may reach out by one hop.
> That is to say, if section 43 refers to a specific chunk of another section, that specific chunk is within scope but its parent section is not.
> Similarly, if a court decision is referred to in S43 then it is in scope but any other decisions/information considered in the court decision is not in scope.
> **NOTE:** The relationship between S43 and S41 is more diffuse. As a result, S43 will be required to refer to a number of specific chunks within section 41. Section 43 should only refer to section 41 in that resolving a section 43 grounds for rejection will have no impact on the section 41 grounds for rejection
> -**OQ-0015 — The office's actual bar for the presumption of registrability**
> This may be captured in a glossary (see "OQ-0016). It could also be worth capturing what an individual or process MUST do and what an individual or process MAY do. If you do not believe that the glossary captures the conceptual relationship between an examiner and a registrar, please make a note of this and adopt the Must/May predicate.
> -**OQ-0015 — Nine role terms with no definitions — Registrar, Delegate, Examiner and more**
> The scope for the S43, should include the subjects, objects and predicates necessary to construct the section's ontology. If constructing a glossary enables greater disambiguation, then so be it. Your definitions of subjects objects and predicates must be identified in the TM Manual, TM Legislations/Acts or on the IP First Response Glossary page (https://ipfirstresponse.ipaustralia.gov.au/glossary-terms)

---

## How each was read

This section is a *derivation* from the words above, in the way
`review/decisions/` is a derivation from a returned workbook. The words are the
artefact; this is what a session took them to mean, and it can be argued with.

### OQ-0014 — the boundary is one hop

Read as a rule with three parts, all of them structural rather than legal:

1. **One hop, and the hop lands on what was named.** A passage or provision that
   section 43 material actually cites is in scope. What *that* thing cites is
   not. The boundary is the citation graph at radius one from section 43.
2. **The hop lands on the chunk, not on its parent.** If the citation names
   `s 41(2)`, `s 41(2)` is in scope and section 41 as a whole is not. This is
   the part with teeth: it rules out "in for a penny" expansion into whole
   neighbouring provisions, and it is expressible against `chunk_ref` and
   provision `ref` exactly as upstream already holds them.
3. **Case law inherits the same rule.** A decision cited from section 43 material
   is in scope; what that decision itself discusses is not.

The section 41 carve-out is a fourth part and is **not** structural — it is a
statement about how the two grounds interact, and it is recorded, not acted on.
Recorded as ADR-0072; implemented in `tmk-boundary`.

### OQ-0015 — the presumption of registrability bar

Two instructions and one conditional:

- It *may* be captured in a glossary — permission, not a direction.
- It is *worth capturing* what a person or process MUST do and what it MAY do.
- **The conditional:** *"If you do not believe that the glossary captures the
  conceptual relationship between an examiner and a registrar, please make a note
  of this and adopt the Must/May predicate."*

A session must answer the conditional honestly rather than pick the easier
branch. The finding — that a glossary of nine terms does not capture it, because
the content in question is a relation between two roles and a glossary holds one
entry per term — is recorded in ADR-0073, with the deontic predicates added and
left empty of trade marks content. **No MUST or MAY statement about examiner
conduct is written by this repo.** The predicate is a place for an expert to put
one; the expert content in `260826-expert-feedback.md` stays where it is.

### OQ-0016 — the scope includes what the ontology needs

Read as widening ADR-0022's selection rule, which picks passages that *cite*
section 43 and therefore misses definitions (Q-28). Three parts:

1. Scope includes the subjects, objects and predicates needed to construct the
   section's ontology — so a term the model depends on is in scope even if its
   defining passage cites nothing.
2. A glossary is permitted where it disambiguates.
3. **A closed list of sources, and this is the constraint, not the permission.**
   A definition must be identified in the Manual, in the legislation, or on
   IP Australia's IP First Response glossary
   (<https://ipfirstresponse.ipaustralia.gov.au/glossary-terms>). Nothing else,
   and in particular not an agent's own knowledge — which is CLAUDE.md rule 1
   restated by the owner in his own words.

The third source is outside the pinned snapshot and so outside what this repo may
consume without a decision about acquisition. Recorded as ADR-0074, and the
acquisition question goes back to the owner as OQ-0018.

---

## What must not happen to this file

Nothing in the quoted block changes — not the misnumbered heading, not `it's`
for `its`, not the missing closing quote after `see "OQ-0016`. It is evidence of
what the owner wrote. The reading below it may be corrected by a later session,
and should be if it is wrong.
