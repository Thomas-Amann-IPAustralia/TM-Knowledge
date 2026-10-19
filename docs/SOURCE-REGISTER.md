# Source register — what each task needs, and what is held

The second review response's A07. One row per task the ontology serves (`CLAUDE.md` §0),
naming the kinds of source it needs and whether this repository holds them. **Machine-written,
unreviewed** (S042). It names kinds of source, not URLs: no page outside the pinned snapshot has
been read here, and a link nobody checked is not a register entry.

Where a source is not held, the rule is the one in `CLAUDE.md` rule 2 and §6: crawling and
extraction belong upstream (`manual-XtrACTor`), and anything captured comes back as its own
source kind, never mixed into the Manual or the legislation. Judgment text needs its licence
terms checked before any capture (Q-11).

| Task | Needs | Held? |
|---|---|---|
| Examiner: find the governing provision | the Act and the Regulations, whole and by unit | **Held**: compilation 48 of the Act, 53 of the Regulations, 763 provisions and 5,821 units; exact references found in a question ("section 44(3)", "reg 4.10", A07) |
| Examiner: find the Manual's practice | the Manual, by passage | **Held**: 2,460 passages captured on 3 August 2026; keyword, ontology and (measured) hybrid search |
| Examiner: read a case the Manual cites | judgment and hearing-decision text | **Citations only** (Q-11): 2,227 citation edges, each classed administrative, judicial or unclassified (`ontology.decisions`); the Manual's account of a case is not the judgment |
| Examiner: what an amendment touches | every record's citations, by provision | **Held**: the dependency index (R05), on the change view and in the ontology report §7 |
| Customer: what a trade mark must be | the Act's requirements, explained | **Held** (the Act); plain-language customer guidance **not held** — raise upstream as its own source kind |
| Customer: the application process | the Regulations' process provisions; the forms and fees | **Held** (Regulations, fee schedule); forms and the customer pages on filing **not held** |
| Customer: understand an objection | the ground, its tests and its ways out; an example report | Grounds and tests **held** as records; an examination report **not held**, and only a fictional one may be used until the owner says otherwise (`CLAUDE.md` §3a) |
| Customer: respond to an objection, give evidence of use | the customer pages on responding and on evidence; ss 41(3)–(4) | ss 41(3)–(4) **held**; the customer pages **not held** — the first two to raise upstream |
| Policy: simulate an amendment | provisions by version; dependants | One version only (compilation 48); versioning is Package 5 (A03) |

**Raise upstream first:** the customer pages on responding to an examination report and on
providing evidence of use, as a source kind distinct from the Manual and the legislation. Nothing
is raised by this file; raising it is the owner's or the next session's to do.
