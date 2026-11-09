# After-action report: the owner's annotations and ChatGPT's copy brief (S051)

**Date:** 2026-11-09 · **Session:** S051 · **Branch:** `claude/inspiring-carson-s929va` ·
**Decision:** ADR-0153 · **Ruling:** `review/rulings/2026-11-09-chat-annotations.yaml` (CHAT-0102)

**Inputs:** the owner's seven annotated screenshots and ChatGPT's *Strategic language and claims
review* (`docs/Nov_rebuild-ref-doc/annotations/`), with the instruction to change the rose colour to
"a pastel orange/yellow".

**Rule used where they disagree:** the owner's drawing wins over the brief. Three times the brief
would keep something the owner crossed out (the overview's lede, the direction chart, the testing
section); each is marked *Owner's drawing* below.

## Summary

- **Owner's drawings: 7 of 7 applied.** Red removed, blue changed; the reading of each is in
  `review/returned/261109-owner-chat-annotations.md`.
- **Colour:** the examiners' rose is pastel apricot (ADR-0153, decision 1).
- **Copy brief, priority 0: 13 of 13 done** (two adapted).
- **Copy brief, priority 1 and 2:** 28 done or adapted, 3 superseded by the owner's drawings,
  4 kept or left as they were, 3 declined; each with its reason.
- **Unchanged:** every record, the graph, the prompts, the explanation objects, `site/data/` and its
  builder, the overview's headline and section 44 example, the section labels and routes.

## The owner's drawings

| # | Page | What changed |
|---|---|---|
| 01 | Overview | Hero description, both buttons, the "Built from" note and legend removed. The three-audience row S050 put in their place went too (the header and the doors offer the three). The section 44 rule now sits directly under the headline, which breaks over two lines |
| 02 | Overview | The examiners' door is now sources, a lens on one concept, and the concepts it connects to; the public's door is a question, an explanation at the current step, and the journey beneath. Both are single centred emblems, like the direction door |
| 03 | For examiners | Hero card removed (and `preview()` in `concepts.js`, which only it used); about-line sentence removed; rose replaced |
| 04 | For direction setting | Hero chart removed; about-line sentence removed |
| 05 | For the public | "Paris Lantern" card removed; about-line sentence removed |
| 06 | For the public | "What we may test with customers" removed, with the customer preview's link to it; `#/future/customers` now lands on the public overview's top |
| 07 | For nerds | "The contract, in one line" removed (the standards page still states the profile) |

The about-line sentence is the one repeat S050 left to the owner (F10). The status strip on every
page still says "AI wrote most of the research material. Each record shows its review status", and a
new test pins it so that the last statement can never go with a repeat.

## The copy brief, item by item

**Priority 0 (§5)**

| Item | Verdict | Note |
|---|---|---|
| Home: "Build it once, use it for every tool" | Done | "One foundation, several possible uses" |
| Home: "every tool built on them can explain itself" | Done | "Shared records can make a tool's sources easier to inspect" |
| Home: callout paragraph ("can always show") | Done | The brief's three sentences |
| Examiners H1 ("faster") | Done | |
| Examiners future H2 ("Supercharging") | Done | |
| Direction lead ("no one can hold in their head") | Adapted | The brief's four sentences, "can require" as "can mean", "determine" as "work out" |
| Direction promise ("Every dependency is traceable") | Adapted | Plus "Some links are not recorded yet." |
| Direction demo card ("See every record") | Done | Label "Recorded link tracing" |
| Trace a change lead | Done | |
| "New right impact modelling" | Done | "Fictional policy scenario" (it was on the direction page's card) |
| What-if count labels | Done | The tile, the direction card and the text equivalent |
| "Coming next" | Done | "Possible future uses" on all three sections; "Possibilities, not commitments." kept |
| Horizon "Within reach" | Done | "Builds on current work · Would need further development and review"; "Needs more data" kept |

**Priority 1: the audience pages (§6)**

| Item | Verdict | Note |
|---|---|---|
| Overview: keep the H1 and the section 44 rule | Kept | |
| Overview: new hero lede | Owner's drawing | Drawing 01 removes the lede |
| Overview: "See the demonstrations", "Three questions, one shared foundation", the line under it | Done | |
| Overview: door titles and summaries | Adapted | Kept as two bullets each; "Potential:" became "Possible later:" |
| Overview: foundation paragraph | Adapted | Merged with "Select a tool to see what it draws on" |
| Overview: trust headline | Kept | "Not blindly, and it never asks you to" (the brief leaves it to the owner) |
| Overview: "Each statement is linked to its source" | Adapted | "Statements are linked to their sources"; the paragraph already says a quotation is not proof |
| Examiners: lead, working H2, subcopy | Done | "normal research" as "own research" |
| Examiners: concept card | Done | "Which exceptions or other issues may be relevant"; points name what is recorded |
| Examiners: research card | Done | "A related legal test where the records hold one"; "open the sources and check" joined to the pinned caveat |
| Examiners: future order | Done | Evidence, change management, expert knowledge, then the rest |
| Examiners: a Manual governance card | Declined | Optional; "Knowledge change management" and the direction page's "Regulatory change monitoring" already carry it, and the brief asks for no more cards |
| Public: H1, lead | Adapted | The lead's last sentence stays in the about line, which says the same |
| Public: keep "What we may test with customers" | Owner's drawing | Drawing 06 removes it |
| Public: future assistant card | Done | "Still needs" now names expert review, customer testing, operational controls and permission for real data |
| Public: future H2 | Adapted | "Possible help for applicants, before and after filing" (the brief gives none) |
| Direction: lead, working title, description | Done | The Manual's amendment count kept as "For scale" |
| Direction: retain the six-bar chart | Owner's drawing | Drawing 04 removes it; the counts are on Trace a change |
| Direction: future H2 and paragraph | Done | Joined to the pinned "Possibilities, not commitments." |
| Direction: maturity order | Done | Monitoring, compare options, test a draft, then the rest; no new card for "understand outcomes" |

**Priority 1 and 2: detail pages and global (§7)**

| Route | Verdict | Note |
|---|---|---|
| `#/concepts` | Done | Lede says "which recorded exceptions or other issues may be relevant" and that the links are not a complete checklist |
| `#/ask` | Done | "A related legal test where the records contain one" |
| `#/customers/objection` | Done | The public card's label is "Fictional objection walkthrough" |
| `#/customers/requirements` | Adapted | Lede says the representations are AI-written, unreviewed and decide nothing |
| `#/customers/process` | Done | One general path; no deadlines, no outcome |
| `#/change` | Done | Lede. The name-matched count was already labelled apart (S050) |
| `#/whatif` | Done | Labels as linked records; one orienting line above the questions |
| `#/nerds` | Done | "Nothing is hidden" replaced |
| `#/how` | Left | Its lede already says search is one of several tools |
| `#/map` | Done | One sentence in the reading card |
| `#/rules` | Done | "For the rules set out so far" |
| `#/standards` | Done | "Other systems would still need integration and governance work" |
| `#/table` | Left | Its lede already says "browse"; no "authoritative" |
| `#/about` | Adapted | H1 as the brief; the "not examiner time saved ..." sentence joined to the verdict |
| `#/glossary` | Declined | Optional; the new words are plain and need no entry |
| Footer and meta description | Done | The brief's wording; the footer's law and practice note kept |
| `layers.js` next cards | Done | "See everything" and "what rests on it" bounded |
| §8 executive explanation | Declined as a new block | Its point is now the foundation paragraph; the owner is removing blocks, not adding them |

## Also fixed along the way

- The three demo cards on the public overview started their words at three heights; the picture row
  now keeps its own height (Q-111).
- The direction door's label and subtitle wrapped mid-phrase; the subtitle has its own line.

## For the owner

- **The drawings were read without words.** The returned artefact says how each was read. Two to
  check: drawing 01 also took the three-audience row S050 added after your screenshot, and drawing 02
  was read as "redraw these two pictures".
- **The brief's §11 questions are still yours:** the headline (kept), the trust headline (kept), a
  fourth Manual-governance audience (not made), which measured results become claims outside the
  repository, and commissioning tests with examiners, applicants and Manual owners.
- **What to distrust:** this is an editorial pass and an agent's reading of drawings; no reader has
  tested it.
