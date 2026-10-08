# Ontology review — duplication, categorisation and the power structure between roles

**As at:** 2026-10-08 · `main` at `45bebe3` (after PR 26) · snapshot `c490a9927f1a`
**Written by:** an agent, session S026, at the owner's request. **Machine-written and
reviewed by no one.** Every finding names the records it rests on so that a person can
check it, and every judgement in it is the agent's and can be wrong.
**Changed:** nothing. No record, graph, prompt or page was edited by this review.

> **Ruled on and acted on, 2026-10-08.** The owner ruled on every item
> (`review/rulings/2026-10-08-chat-ontology-review.yaml`, ADR-0121) and S026 acted on
> the approved ones the same day — ADR-0120 to ADR-0124 say what changed and the
> ruling file's `applied` block lists it. The text below is the review as written,
> left unchanged: its counts describe the ontology *before* the changes. Not acted on,
> as ruled: B1 (explained), B2, B3, B6 (postponed until B1), C9 (not approved), D7, F4,
> F5 (deferred), and D5's paid re-judging (quoted, not spent).

The owner asked for an in-depth review of the ontology as it stands — having found
duplication and miscategorisation — with each issue and a suggested resolution in a
table, and with particular attention to the power structure between the defined roles.

## What was reviewed, and how

| | |
|---|---|
| Concepts | 167 — 52 signed (`eval/gold/`), 115 machine-written (`authored/`) |
| Concept typings (groups) | 167, all machine-written — 130 by an agent session, 37 by the bulk pipeline |
| Relationships | 608 — 35 signed, 573 machine-written |
| Entity mentions | 55 signed |
| Model | the nine draft modules in `ontology/draft/`, `shapes/`, the built `graph/` |
| Retrieval surface | the label linker (`bulk.links`), `data/derived/search/aliases.yaml` |
| Sources | the Act, the Regulations and the Manual at the pinned snapshot |

Method: the repo's own readers and linker; a label-collision scan over preferred and
alternative labels, folded for case, articles, plurals and hyphens; relationship and
connected-component analysis; a `tmk-shacl` run (0 defects, 0 gaps, 300 notes); a seeded
random sample of 25 machine-written relationships, each judged against the sentence it
quotes; and recognition tests on questions about roles.

## Headline findings

1. **Thirteen ideas exist twice** — once signed, once machine-written. Eleven are the
   same idea, one is a scope split, one is a homonym. 40% of all relationships hang off
   one side of a pair. The repo's own duplicate check sees ten, because it compares
   preferred labels only.
2. **The vocabulary inverts the delegation chain.** It records "the Registrar's
   delegate" as another name for the Registrar, and records that "examiner" is not
   "delegate" and not "decision maker" — the reverse of s 206, of Part 18.2.2.2 and of
   the expert's own corrections (GE-0010, GE-0047), made in the same review round and
   never carried across. No relationship joins examiner and Registrar at all.
3. **Power is flattened to `related`.** 101 of the 120 relationships that touch a role
   are `related`, including sentences that state a power exactly (s 205's Deputy
   Registrar; the ART "stands in the shoes of the original decision maker"). The
   predicate dictionary has no word for delegation, supervision, review, consent or
   control.
4. **One group per concept, from two different axes.** What a thing *is* and what it
   *does* in reasoning share one dropdown, so duplicates land in different groups,
   siblings split (three kinds of application in three groups), and the presumption of
   registrability — the rule the grounds are exceptions *to* — is typed as an exception.
5. **Labels leak across senses.** 21 labels are shared between concepts; signed
   alternative labels such as "made in", "evidence" and "research" link concepts to
   ordinary prose; search aliases contradict 19 of the vocabulary's own not-labels; and
   machine-defined dictionary words match everyday English — all five of *Board*'s
   links are wrong.
6. **Two of the four practice-versus-law mechanisms guard nothing on real data**, and
   SHACL passes with every problem above present.
7. **About 28% of a 25-edge sample of machine-written relationships are wrong** (95%
   interval roughly 14–48%; one judge, and that judge a model), mostly mis-targets
   caused by the shared labels.

---

## The issues and what to do about each

"Who" says who can act: **Agent** — machine-written records and code, no signature
involved; **Expert** — anything inside a signed record; **Owner** — a decision at one of
the gates in `CLAUDE.md` §3a, or a change to the owner's own four groups.

### A. Duplication

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| A1 | **Eleven concepts are held twice with the same meaning**, one signed and one machine-written. | Signed / authored: GC-0007 / GC-0118 *presumption of registrability*; GC-0012 / GC-0129 *specification of goods and services*; GC-0013 / GC-0069 *condition of registration* / *conditions or limitations*; GC-0014 / GC-0100 *endorsement*; GC-0016 / GC-0090 *priority date*; GC-0036 / GC-0125 *plant variety name*; GC-0040 / GC-0102 *opposition*; GC-0041 / GC-0101 *evidence of use*; GC-0042 / GC-0094 *revocation of acceptance*; GC-0043 / GC-0110 *divisional application*; GC-0046 / GC-0115 *Registrar*. The relate run independently judged ten of them `same_concept` (0.70–0.99); the eleventh pair it linked as `broader` (GR-0109). The authored records' own differences are which ground they are used under, not what they are. | Apply ADR-0080 consequence 2 — the signed record wins. Withdraw each authored id into a withdrawal ledger (never reused; `authored/` needs its own, since `eval/gold/` is frozen), re-point its relationships to the signed id, and drop those that then duplicate. Anything the authored record adds — GC-0094's s 38, GC-0110's ss 45–46, GC-0115's s 205 — goes to the expert as a proposed amendment to the signed record, never into it. This supersedes ADR-0101 decision 2 (agent-proposed) for pairs with an identical label and a same-concept judgement, so it needs a new ADR. | Agent, on the owner's go-ahead; Expert signs the amendments |
| A2 | ***Ground for rejection* exists twice with different scope.** | Signed GC-0006 carries the alternative labels "objection" and "s 43 objection" and a s 43 basis: it is the section 43 ground under a general name. Authored GC-0053 is the general class ("The Act and Regulations contain all the grounds…", s 33) and excludes "objection". 63 relationships attach to one or the other (34 and 29). | The expert decides whether GC-0006 is the general concept. Recommended: yes — keep GC-0006 as the class, move "s 43 objection" to a narrower *section 43 ground for rejection*, then retire GC-0053 as in A1. | Expert |
| A3 | ***Reputation* is two concepts under one label.** | Signed GC-0050 (s 43) is a place or person being known for something, and *excludes* "reputation in another trade mark". Authored GC-0130 is exactly that excluded sense — a trade mark's reputation in Australia (s 60, s 185). Edges have crossed: GR-0084 puts the s 60 sense (Part 46) on GC-0050; GR-0315 puts "LYGON STREET has a reputation as a restaurant district" on GC-0130. | Not a merge. Relabel authored GC-0130 *reputation of a trade mark* (alternative "reputation in Australia") so it stops claiming the bare word, and re-point GR-0084 and GR-0315. Signed GR-0056 (*connotation* `excludesBasis` GC-0050, quoting "a reputation in another trade mark") points at the sense GC-0050 excludes — that goes to the expert. | Agent (GC-0130, edges); Expert (GR-0056) |
| A4 | **Labels shared between different senses.** | Signed GC-0035 *owner or authorised user* — the licensee of a phone number, domain name or call sign under s 43 — carries the alternative label "authorised user", which is the preferred label of GC-0083, the s 8 authorised user. GR-0444 and GR-0513 then make the s 8 authorised user and the registered owner *narrower than* the s 43 factor. GC-0018 and GC-0126 share "geographical indication for wine", while GC-0126 excludes "geographical indication"; GC-0126 has no relationships at all. | Expert qualifies or removes "authorised user" on GC-0035. Agent deletes GR-0444 and GR-0513, drops "geographical indication for wine" from GC-0126, and links GC-0126 to GC-0018 if the expert agrees a wine GI is a GI. | Expert; Agent |
| A5 | **The repo's duplicate check under-reports.** | `expertpack.duplicate_labels` compares preferred labels exactly and reports 10 pairs. The folded scan over all labels finds 21 shared labels across 15 concept pairs. ADR-0101 noted that alternative labels were not covered (c3) and that the check was not built (c1). | Extend the check to every label, folded; report each collision as a counted note on the dashboard (ADR-0101's own "middle position"); make a collision disclosed on neither record a defect. | Agent |
| A6 | **One of the twelve merge candidates is wrong.** | The relate run proposed GC-0028 *implied endorsement* = GC-0014 *endorsement* (0.76). Signed GC-0028 excludes "endorsement"; one is an inference consumers draw, the other an entry on the Register. | Mark it rejected when the candidates go to a person (HANDOFF carries "12 merge candidates"). | Agent |

### B. Categorisation — the nine groups

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| B1 | **One group per concept, drawn from two axes.** The groups mix what a thing *is* (role, subject matter, step, record, external scheme) with what it *does* in reasoning (ground, test, factor, exception), and a concept may carry one. ADR-0098 c3 calls this its weakest part. | The duplicates disagree: *presumption of registrability* is `exception` (GT-0007) and `relevant_factor` (GT-0118); *endorsement* `exception` and `instrument_or_record`; *specification* `relevant_factor` and `instrument_or_record`; *condition of registration* `exception` and `instrument_or_record`. | Adopt OQ-0026's "two columns": a required **kind** (exactly one) and an optional **function** (zero or more, each tied to the ground it operates in). Concepts stop being forced to choose, and the same idea stops getting two answers. | Owner (OQ-0026; the four reasoning groups are the owner's) |
| B2 | **Siblings typed differently.** | Applications: *trade mark application* `instrument_or_record`, *divisional application* `procedural_step` (twice), *convention application* `relevant_factor`, *series of trade marks* `subject_matter` (alternative "series application"). Dates: *priority date* and *filing date* `relevant_factor`, *date of registration* `none_of_these`. International registrations: *IRDA* and *protected international trade mark* `subject_matter`, *international registration* `instrument_or_record`, while GR-0564 makes an IRDA a kind of international registration. Parties: registered owner, authorised user, applicant, opponent and holder `process_role`; *predecessor in title* and *owner or authorised user* `relevant_factor`. GT-0111's own check: "This and 'divisional application' are typed differently on similar facts. One of the two is wrong." | Type by kind first (B1), then make siblings agree: every application an instrument; every party a role; dates and statuses either a kind of their own or attributes rather than concepts. | Agent proposes; Owner or Expert confirms |
| B3 | **The presumption of registrability is typed as its own opposite.** | Section 33(1): the Registrar must accept unless satisfied a ground exists, so the presumption is the default rule and the grounds are its exceptions. GT-0007 types it `exception` (0.5) "on what the presumption does rather than on what it is"; GT-0118 types the duplicate `relevant_factor` and calls itself "one of the clearest misfits in the pass". The expert's covering note is entirely about this concept. | If B1 is adopted, a function such as *presumption or standard of decision*, shared with GC-0008 *real and tangible danger* and the "clearly satisfied" threshold. If not, `none_of_these` with the reason, which is more honest than `exception`. | Owner |
| B4 | **Grounds of refusal are typed inconsistently.** | `ground_of_refusal` holds the matter of s 39(1), s 39(2), s 40, s 42(a), s 42(b) and s 44 — but s 41 and s 43, the two most-used grounds, appear only through their tests (GC-0058, GC-0002, both `legal_test`) and the general GC-0006 / GC-0053. *Prohibited sign* and *prescribed sign* are typed as grounds and also made kinds of *sign* (GR-0238, GR-0196). | One `ground_of_refusal` concept per statutory ground, each `requiresElement` its test and `broader` the general ground; the sign itself (*a prescribed sign*) as `subject_matter`. | Agent; Expert reviews |
| B5 | **`exception` holds remedies as well as exceptions.** | GT-0013's own check: four concepts are typed `exception` because they *overcome* a ground already made out (condition of registration, endorsement, limitation of the specification, written permission) and three because the ground *does not arise* (business identifier, deceased person, fanciful reference). | Split *exception* (the ground does not apply) from *remedy* (a step or record that overcomes a ground — the object of `isOvercomeBy`). | Owner (via OQ-0026) |
| B6 | **The residual group is filling with dictionary words.** | `none_of_these` was kept for exactly one concept on purpose (ADR-0098 c1, GC-0051). It now holds seven; the six the define run added — *covering*, *capture*, *personal information*, *pending*, *date of registration*, *repealed Act* — are mostly s 6 / s 9 dictionary entries. *Repealed Act* is an instrument; it belongs in the authority module, not the vocabulary. | Retire the dictionary-only concepts (E3); model the repealed Act as `tmk:Legislation`; give dates and statuses a home (B2). | Agent |
| B7 | **`process_role` is a flat bag.** | It holds a statutory office and its deputy, a functional role (*decision maker*), a delegate position (*examiner*), five parties, an external co-regulator (ACCC), two review bodies (ART, prescribed court), three Madrid bodies (one of them a state), a professional regulator its own record could not identify (*Board*) and a profession (*lawyer*). | Sub-kinds that carry the power structure: office, delegate, advisory role, party, representative, review body, co-regulator, international body — see C5. | Agent (TBox, ADR) |

### C. Roles and the power structure

What the sources say, in brief. **The Registrar** is the office (s 201) in which the
Act's powers sit. **A Deputy Registrar** has all of them except the power to delegate,
subject to the Registrar's directions, and its acts are taken to be the Registrar's
(s 205). **A delegate** is an employee to whom the Registrar has delegated powers by
signed instrument, and may be required to act under the direction or supervision of the
Registrar or a named person (s 206). The Manual names who is currently delegated to
accept — "Hearing Officers, EL1 Examination Team leaders, APS6 Senior Examiners and APS 5
Examiners … referred to below as acceptance officers" (Part 18.2.2.2) — and expects
examiners to consult a team leader, a supervisor, subject matter experts or a hearing
officer in named situations (Parts 10.1.1.2, 14.5.5.1.3, 18.3.3.1.2). **Above the
office**, the ART reviews certain decisions, standing "in the shoes of the original
decision maker", and the prescribed courts hear appeals (ss 35, 56, 190). **Beside it**,
the ACCC holds powers the Registrar does not — a certificate on certification trade mark
rules (s 175) and consent to their assignment (s 180) — and under the Madrid Protocol the
International Bureau's opinion prevails over an Office of origin on classification
(Part 14.2.2.2.2). **Among the parties**, an authorised user uses a mark "under the
control of the owner" (s 8(1)). The expert added the office's practice on top: doubt
about a connotation must be the Registrar's "as a whole", and an examiner is expected to
consult their team leader and the s 43 SMEs before accepting on doubt alone.

| Role | Where its power comes from | What the ontology holds today |
|---|---|---|
| Registrar | s 201 | GC-0046, duplicated as GC-0115; empty `tmk:Registrar` class |
| Deputy Registrar | s 205 — all powers except delegation, subject to direction | GC-0159; `related` to both Registrar records |
| Delegate | s 206 — signed instrument; direction or supervision | no concept; "the Registrar's delegate" is an alternative label *of the Registrar*; *examiner* excludes "delegate" |
| Hearing officer, team leader, senior examiner, examiner | Part 18.2.2.2 — "currently delegated to accept" | *examiner* only; the others absent |
| Decision maker | a role in a decision, played by whoever exercises the power | GC-0045, a peer of examiner and Registrar, excluding "examiner" |
| Team leader, supervisor, SMEs | practice (Parts 10, 14, 18); s 206(2); the expert's note | absent; empty `tmk:TeamLeader` and `tmk:SubjectMatterExpert` |
| ART; prescribed courts | merits review; appeals (ss 35, 56) | GC-0134, GC-0139; `related` |
| ACCC | ss 175, 180 — a veto the Registrar lacks | GC-0133; the one consent power stated three ways |
| International Bureau | Madrid Protocol; prevails over an Office of origin | GC-0138; `dependsOnExternalSource` |
| Registered owner, authorised user | s 8(1) — use under the owner's control | `requiresElement`; both made narrower than a s 43 factor |

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| C1 | **The vocabulary inverts the delegation chain.** | Signed GC-0046 *Registrar* has the alternative label "the Registrar's delegate"; signed GC-0044 *examiner* excludes "delegate", "decision maker" and "Registrar"; signed GC-0045 *decision maker* excludes "examiner"; authored GC-0115 excludes "delegate". So the vocabulary says a delegate *is* the Registrar and an examiner is *not* a delegate. The sources say the reverse: s 206(1); Part 18.2.2.2; and the expert's held corrections — GE-0010 "The decision maker is the examiner", GE-0047 "The decision maker (examiner) operates using delegated authority from the registrar but they are not the same." The expert made those corrections in the same workbook in which they signed the three concepts; the corrections were held as amendments to entity records and never carried across to the concept records. Both signed concepts were seeded to invite exactly this correction — GC-0046's own note: "Holding 'the Registrar's delegate' as an alt label is probably wrong — a delegate exercises the power and is not the Registrar. It is here to be corrected"; GC-0044's: "Deliberately separated from decision maker and delegate" — and both were marked correct. In live recognition, *"Can the Registrar's delegate accept the application?"* is recognised as the Registrar. | Put three amendments to the expert, citing their own corrections: drop "the Registrar's delegate" from GC-0046, as its own note asks; keep "delegate" and "decision maker" as not-synonyms of *examiner* only once C3's edges say that an examiner *is* a delegate and *acts as* the decision maker at examination; the same for GC-0045. Meanwhile an authored *delegate* concept takes the phrase, so recognition stops folding it into the Registrar. | Expert (signed); Agent (*delegate*) |
| C2 | **Role concepts the corpus names are missing.** | No concept for *delegate* (65 passages), *Hearing Officer* (37), *Examination team leader* (6 — with powers of its own, e.g. Part 38.1.1.3), *subject matter expert* (classification and language SMEs, 6), *acceptance officer* (Part 18's collective term), *IP Australia* (120) or *trade mark attorney* (8). Four of the nine terms the expert asked to have defined — Delegate, SME, Office Practice, Adverse Report — have no concept. *"What can a Hearing Officer decide?"* is recognised only as the procedural step *hearing*. | Author them from the corpus — each has a quotable passage — the expert's nine first. | Agent |
| C3 | **There is no vocabulary for authority.** | None of the 14 predicates expresses delegation, direction or supervision, review or appeal, consent or veto, precedence, or control. The only role-aware one, `constrainsExaminerTo`, names one role inside the predicate, so the same constraint on a hearing officer or the Registrar cannot be stated, and GR-0461 misuses it with the examiner as its object. `tmk:decidedBy` and `tmk:constrainsRole` are declared in `examination.ttl` and never used. | A small authority vocabulary, each predicate with a definition, a direction and a statutory anchor: `exercisesPowersOf` (Deputy Registrar → Registrar; s 205(2)–(3)); `holdsDelegationFrom` (delegate → Registrar; s 206(1)); `actsUnderDirectionOf` (s 205(2), s 206(2)); `consults` / `refersTo` (examiner → team leader, SME, supervisor; practice); `reviews` / `hearsAppealsFrom` (ART, prescribed court → the Registrar's decisions; ss 35, 56); `requiresConsentOf` (certification trade mark assignment → ACCC; s 180); `prevailsOver` (International Bureau → Office of origin; Part 14.2.2.2.2); `actsUnderControlOf` (authorised user → owner; s 8(1)). Generalise `constrainsExaminerTo` to `constrainsRole`, with the role as an argument. Every such edge carries its source's authority kind, so statutory delegation (law) and consulting a team leader (practice) stay distinguishable — `CLAUDE.md` rule 5. | Agent proposes (ADR, unreviewed); Expert signs one of each to admit it to the closed list |
| C4 | **Statements of power were recorded as `related`.** | 101 of the 120 relationships touching a role are `related`; so are 13 of the 17 that join two roles. Among them: GR-0343 / GR-0346, quoting s 205 ("a Deputy Registrar has all the powers and functions of the Registrar (except the power of delegation)"); GR-0462 (the ART "stands in the shoes of the original decision maker"); GR-0569 / GR-0596 (ART review of the Registrar's decisions); GR-0593 (appeal to a prescribed court); GR-0594 (ART review of ACCC decisions). GR-0601 (the International Bureau's opinion "stands") became `dependsOnExternalSource`. The single s 180 consent power is stated three ways: GR-0361 `dependsOnExternalSource`, GR-0515 `allocatesTo`, GR-0430 `related`. There is no relationship at all between examiner and Registrar, or examiner and decision maker. | Re-type these with C3's predicates — most can be done deterministically from the quoted sentence and the section it cites; re-judge the remainder in one batch (dry-run estimate first). | Agent |
| C5 | **A role has three disconnected representations.** | (1) `tmk:Role` classes in `examination.ttl` — Registrar, Delegate, Examiner, DecisionMaker, SubjectMatterExpert, TeamLeader — flat siblings, all empty, all still "UNDEFINED — HANDOFF Q17", though Q17 was answered (ADR-0074) and authoring has been allowed since ADR-0079. (2) 18 vocabulary concepts typed `tmk:ProcessRole`, kept apart from `tmk:Role` on purpose (ADR-0098 c2) but with no bridge. (3) One signed entity mention typed `Role`, GE-0062 "Examiners", which resolves to nothing. ADR-0073 rested on roles being "already recorded as entity mentions typed Role" — there is one. | Keep the term/class split ADR-0098 asks for, and bridge it: each role concept `tmk:denotesRole` its class. Restructure the classes as office (Registrar, Deputy Registrar) / delegate (examiner, hearing officer, team leader, senior examiner) / advisory (SME, supervisor) / party / representative / review body / co-regulator / international body. Make *decision maker* a role in a decision — whoever a decision is `decidedBy` — not a peer of *examiner*. Resolve GE-0062 to the examiner concept. | Agent (ADR, agent-proposed) |
| C6 | **The "Registrar as a whole" bar and the consultation expectation are held nowhere.** | The expert's note (`review/returned/260826-expert-feedback.md`): doubt must be the Registrar's "as a whole", and an examiner is expected to consult their team leader and the s 43 SMEs before accepting on doubt alone. OQ-0022 was closed on 2026-09-08 on the basis that "an agent writes the examiner-conduct rule itself, citing the expert's own note" — no such record exists. Signed GR-0011 states only the examiner-level version ("If there is doubt that a connotation exists, then the ground for rejection should not be raised"), through `constrainsExaminerTo`. Most of the rule has corpus support: s 206(2), Part 10.1.1.2 ("consult with your team leader in the first instance"), Part 14.5.5.1.3 (the supervisor decides referral to the Classification SMEs), Part 18.3.3.1.2 (consult the hearing officer or Quality, Practice and Customers). | Write the rule as authored relationships with practice authority and `should` modality — examiner `consults` team leader and s 43 SME before accepting on doubt; acceptance on the presumption `constrainsRole` the Registrar — evidenced from those passages. The s 43-specific part rests only on the expert's note, which the evidence envelope cannot cite (it accepts upstream refs only). Citing it needs an `expert_note` evidence kind, and that is the owner's call because it concerns how an expert's words are used (ADR-0088). Re-open OQ-0022 rather than leaving it marked applied. | Agent (corpus part); Owner (expert-note evidence) |
| C7 | **Decisions of the Registrar's own delegates are classed as judicial authority.** | 95 ATMO decisions — hearing officers, that is, the Registrar acting through a delegate — are `tmk:JudicialDecision` with authority kind `decision`, the same as 19 High Court, 22 Full Federal Court and 85 Federal Court decisions; 16 UK RPC reports likewise. Nothing distinguishes binding from persuasive, court from office, or Australian from foreign, and there is no court hierarchy. An answer citing "[2009] ATMO 68" presents the office's own earlier view on the footing of the Full Federal Court. | Add `tmk:AdministrativeDecision` (ATMO, APO) beside `tmk:JudicialDecision`, and a jurisdiction and court-level attribute derived deterministically from upstream's case id; show it wherever a decision is cited. | Agent (structural, deterministic) |
| C8 | **Recognition folds the subordinate role into the superior one.** | Each label is matched independently, so "Registrar" matches inside "Deputy Registrar", and every Deputy Registrar mention also recognises the Registrar — twice, through the duplicate. | Longest match wins and consumes its span (`bulk.links.find_mentions` and `site/js/engine.js` together, then re-measure). | Agent |
| C9 | **The project's own approval roles are indistinguishable.** | `tmk:approvedBy` is a free string, so the owner's approval of RULE-0002 and the trade marks expert's approvals are the same kind of fact in the graph (the owner chose this on OQ-0010). `ontology/README.md` says approval needs "an ontology specialist *and* a domain expert" — two capacities the model cannot record. | Keep who may approve exactly as ruled, but record the capacity in which a person signed — domain expert, owner, ontology specialist — so a reader can tell legal validation from project sign-off. | Owner |

### D. Relationships and hierarchy

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| D1 | **The predicates have no definitions.** | `relations.ttl` gives each predicate a label and a usage count. The relate prompt's only definition is the first signed example, cut to 160 characters (`bulk.jobs._predicate_examples`), and two of those exemplars are inverted: GR-0032 (`isOvercomeBy`; its own note: "Subject and object are the wrong way round") and GR-0007 (`mayGiveRiseTo`; "A connotation may result from the whole trade mark" recorded as connotation → trade mark as a whole). In the sample (D5), GR-0520 chose `qualifies` because its sentence says "qualifies for registration". | Give each predicate a definition, a direction convention, and one positive and one negative example; choose exemplars deliberately and never one whose note flags it; say which way each reads. Re-run relate only on edges whose predicate changes meaning. | Agent (TBox text, unreviewed) |
| D2 | **Signed relationships with known defects.** | GR-0032 inverted and GR-0008 the wrong predicate — both planted in the seed as traps (their notes say so), both marked correct; GR-0007 inverted; GR-0034's subject is the INN stem where the sentence's subject is the s 43 ground; GR-0056 targets the reputation sense GC-0050 excludes (A3); and GR-0008 (*connotation* `requiresElement` *reputation*) and GR-0056 (*connotation* `excludesBasis` *reputation*) contradict each other. | Put the five records to the expert as one short, specific amendment list in the next expert pack. Until then they stay served, with their notes visible. | Expert |
| D3 | **Duplicate concepts double the relationships.** | 243 of 608 relationships (40%) touch one side of a duplicate pair. Merged, 133 records collapse into 64 triples, and GR-0109 (*condition of registration* ⊂ *conditions or limitations*) becomes a concept narrower than itself. One sentence became two or three records, one per duplicate id (GR-0091 / GR-0395 / GR-0571; GR-0529 / GR-0530). The biggest hubs are split in half: *ground for rejection* 34 + 29, *opposition* 19 + 19, *Registrar* 18 + 17. | Falls out of A1: after re-pointing, de-duplicate on subject, predicate and object, keep the earliest id and withdraw the rest. | Agent |
| D4 | **Hierarchy edges contradict signed records.** | GR-0110 makes *endorsement* a kind of *condition of registration*, though signed GC-0014 and GC-0013 each exclude the other; GR-0407 makes *limitation of the specification* a kind of *conditions or limitations*, though GC-0013 excludes "specification amendment"; GR-0374 makes *CARTOON* a kind of *image of a person*, though its own record excludes that label and says it is wider; GR-0494 makes *written permission* a kind of *other circumstances* from a passage about letters of consent, which GC-0029 excludes; and GR-0444 / GR-0513 (A4). 12 `broader` edges cross groups. | Delete or re-type these (all authored), and add a shape that fails a `broader` edge where either end excludes the other's label. | Agent |
| D5 | **About a quarter of machine-written edges in a sample are wrong.** | A seeded sample of 25 authored relationships, each judged against its quoted sentence: 13 sound, 5 too vague to carry meaning, 7 wrong (28%; 95% interval roughly 14–48%). The wrong ones: label mis-targets (GR-0432 puts the ACCC's consent on the s 43 *written permission* concept; GR-0478 puts s 44 confusion between marks on the s 43 *confusion* concept, which excludes it), a template placeholder taken as evidence (GR-0352, "&lt;123456&gt;"), an edge built on a statement of absence (GR-0278), a modality read off a non-normative "should" (GR-0508), and the lexical predicate choice in D1 (GR-0520). | Before the pitch says anything about edge quality, have a person — or a second, different model — judge a stratified sample. Exclude the Manual's form templates from relate input, and require that both concepts' labels occur in the quoted sentence. | Agent; Owner chooses the judge (`CLAUDE.md` §3a) |
| D6 | **The two most central concepts have no relationships.** | *Trade mark* (GC-0072) and *applicant* (GC-0116) are joined to no other concept, because a concept named in over a fifth of passages is never paired (ADR-0113 c3). Without the vague `related` edges, the largest connected piece falls from 163 to 138 of 167 concepts, with 24 isolated. | Author the structural edges for the hub concepts straight from their definitions — s 17 (a trade mark is a sign), s 6 (registered, certification, collective and defensive trade marks are trade marks), the applicant files the application — with no model call. Report D1-deliverable connectedness both with and without `related`. | Agent |
| D7 | **`related` carries 42% of the machine-written graph.** | 242 of 573 machine-written relationships are `skos:related`, which ADR-0113 allowed so the graph would not stay disconnected. The Ask page counts and follows them like any other connection. | Present `related` as "mentioned together" and weight it below the legal predicates in ontology search; shrink it through the re-typing in C4 and D1. | Agent (search and `engine.js` together; re-measure) |

### E. Labels and recognition

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| E1 | **Signed alternative labels that match ordinary prose.** | GC-0021 *geographical qualifier*: 65 of its 71 passage links come through "made in" ("made in accordance with the Act", "made in writing"). GC-0041 *evidence of use*: 183 of 226 through bare "evidence". GC-0052 *examiner research*: 56 of 60 through bare "research". GC-0006: 35 through "objection". GC-0012: 100 of 109 through bare "specification". GC-0040 *opposition* carries "notice of intention to oppose", which names a document. | The expert prunes them. Until then, the linker skips a short list of labels marked too general, kept beside the records rather than in them. | Expert; Agent (the list) |
| E2 | **Search aliases undo the not-labels.** | `data/derived/search/aliases.yaml` gives 19 concepts an alias that is their own not-label — *priority date* ← "filing date"; *authorised use* ← "authorised user"; *opponent* ← "objector"; *divisional application* ← "parent application"; *trade mark* ← "sign" — and 45 an alias that is another concept's label; *approved form* carries the alias "Registrar". Recognition ignores not-labels instead of letting them veto a match, so the boundary the guide calls "the most valuable field on the record" is erased at the point of use. | Filter the aliases deterministically — drop any that equals the concept's own not-label or another concept's label — and make recognition honour not-labels. | Agent |
| E3 | **Machine-defined concepts that are dictionary words.** | The define job picks s 6 / s 9 defined terms no record covers, whether or not the Manual reasons with them. *Board* (s 6, by reference to the Patents Act) links to 5 passages and all 5 are wrong — an A-frame board, a body board, a painter's board, the "Board of Trade" — and its own record could not identify the body. *Covering* (22 links; its own record says the Manual uses the word "in its ordinary sense"), *label* (14), *capture* (7), *CARTOON* (a Part 5 indexing descriptor) and *personal information* (FOI) are similar. *Decision* (178), *hearing* (97, including every "Hearing Officer"), *holder* (71, including "copyright holder") and *pending* (44) mostly match ordinary uses. | Withdraw the six with no examination role (*Board*, *covering*, *label*, *capture*, *CARTOON*, *personal information*), or keep them as unlinked glossary entries; relabel the four over-matching ones to their legal sense (*Registrar's decision*, *holder of an international registration*); add a minimum count of Manual passages that use the defined sense to define's selection rule. | Agent |
| E4 | **A concept excludes its own label.** | GC-0134 *ART* excludes "art". Matching is case-insensitive; the shape that should catch this is not. | Fix the record; make the self-contradiction shape fold case. | Agent |
| E5 | **117 not-labels name a concept the vocabulary does not hold.** | Among them: *delegate*, *hearing officer*, *IP Australia*, *trade mark attorney*, *adverse report*, *acquired distinctiveness*, *registration*, *rejection*, *device*, *composite trade mark*, *class*, *Paris Convention*. | A ready worklist for define, roles first (C2). | Agent (paid — dry-run first) |

### F. The model, its gates and its documentation

| # | Issue | Evidence | Suggested resolution | Who |
|---|---|---|---|---|
| F1 | **Two of the four practice-versus-law mechanisms guard nothing on real data.** | `ontology/draft/GUIDE.md` §1 names four. `tmk:ManualInstruction` has no instances — it is applied only as an entity mention's `mentionClass`, never as a type — so its disjointness with `tmk:LegislativeProvision`, and the shape that checks it, cannot fire. The PU-0004 shape targets `tmk:LegalProposition` (no instances) through `statedIn` and `attributedTo` (never written). Both fire only on test fixtures. The `authorityKind` string on 1,233 passages and the competency queries carry the whole distinction, and live answers are model text the graph never sees. | Assert a Manual-passage class on every chunk from the same structural rule that sets `authorityKind`, and aim the disjointness and its shape at it; check answers for PU-0004 at answer time (a Manual passage presented as "the Act requires"). Otherwise, stop the guide claiming the two mechanisms. | Agent; Owner if the answer check changes what examiners are told |
| F2 | **SHACL passes with all of the above present.** | 0 defects, 0 gaps, 300 notes — every note the same not-label boundary note. No shape checks label collisions between concepts, case-folded self-contradiction, `broader` against not-labels, or group agreement between duplicates. D1's "0 SHACL defects" test therefore says nothing about duplication or miscategorisation. | Add those shapes (A5, D4, E4) and report collisions as counted notes. | Agent |
| F3 | **`legislative_basis` is the one claim nobody verifies.** | Evidence quotes are checked against the snapshot; legislative bases are not. Three are wrong: GC-0115 *Registrar of Trade Marks* cites s 200 (the office seal; the office is s 201); GC-0159 *Deputy Registrar* cites s 203 (the right to be heard; the office is s 205); GC-0167 *certificate of verification* cites r 2.2 (how months are counted). | Fix the three, and require either an evidence quote from each cited provision or a flag on the basis. | Agent |
| F4 | **Still no definitions.** | `skos:definition` appears nowhere, and the definition record type was never built (`authored/README.md` says what it needs). The 37 concepts the define job wrote carry a definition in `notes` as "Summary, not a definition: Summary: …" (the prefix doubled), so 22% of concepts have a definition in a field not made for it, and the signed 52 have none. Definitions were the expert's first request. | Build the definition record type — schema, id prefix, `RECORD_TYPES` — quoting its source with that source's authority kind (Act, Regulations, Manual; the IP First Response glossary once OQ-0018 settles acquisition). Start with the expert's nine; move the 37 summaries into it. | Agent; Owner (OQ-0018) |
| F5 | **The documentation describes an earlier ontology.** | `authored/README.md`: 78 concepts, 130 typings, no relationships, eight overlaps (now 115, 167, 573 and 13). `data/derived/reports/ontology.md` (2026-09-09): no authored relationships, "52 of 52 concepts are not sorted". `GUIDE.md` §4, §5 and §10: empty classes, 29 not-label pairs (now 300). `legal-concepts.ttl` and `examination.ttl` comments: the repo may not type or define concepts (pre-ADR-0079). `relations.ttl`'s "closed list" omits the SKOS predicates ADR-0113 added. `data/derived/links/mentions.json` covers 130 of 167 concepts. | Regenerate the report and the links; rewrite the comments; add a test that the committed mentions cover every concept. | Agent |
| F6 | **Confidence is not comparable across authors.** | The 37 typings by the bulk pipeline sit at 0.84–0.99 (*Board* 0.86, though its referent is unknown); the 130 by an agent session at 0.5–0.9. | Never rank or threshold on confidence across authors; split by `authored_by`, as `authored/README.md` already requires for measurements. | Agent |

---

## A suggested order of work

1. **Now — agent only, no signature touched, no spend.** A3 (GC-0130 and its edges), the
   authored half of A4, A5, B6, C7, C8, D4, D6, E2, E4, F2, F3, F5. Hygiene that leaves
   every signed record alone; rebuild the graph after (`tmk-graph --write --rules`).
2. **On the owner's go-ahead — the role layer.** A1 with D3 (retire the eleven authored
   duplicates; a new ADR superseding ADR-0101 decision 2), C1's *delegate* concept, C2,
   C3, C4, C5, D1, E3, F4. One relate re-run over the role edges and the re-typed
   predicates, dry-run estimate first (spend so far US$3.49 of the US$6.60 cap).
3. **Owner decisions.** B1, B3 and B5 (OQ-0026's two columns, and the owner's own four
   groups); C6 (whether an expert's note may be cited as evidence); C9 (the capacity in
   which a person signs); D5 (who judges the precision sample); F1's answer-time check, if
   it changes what examiners are told.
4. **To the expert, in one short list.** A2; GR-0056 (A3); GC-0035 (A4); GC-0044,
   GC-0045, GC-0046 (C1, citing GE-0010 and GE-0047); the five in D2; the labels in E1.

## What this review did not do

- Change any record, the graph, a prompt or a page.
- Read all 573 machine-written relationships. D5 is a 25-edge sample judged by one model;
  its interval is wide on purpose.
- Judge whether the 167 concepts are legally right, beyond their labels, groups,
  legislative bases and links.
- Spend anything. No paid call was made.
