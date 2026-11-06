# After-action report: the plain-English copy pass

**Session** S048 · 2026-11-06 · branch `claude/busy-thompson-wz43bm` · ADR-0150
**Input** `TM-Knowledge-copy.patch` and `TM-Knowledge-copy-guide.md` (ChatGPT), against `84b43da`.
**Scope** Words only. No layout, component or interaction changes; no record, graph or ontology data.

## Verdict

The translation is fair and much easier to read. **I applied the patch as a whole**, and then:

- **declined one part**: a new section 43 explanation component and glossary entry (§1);
- **changed 45 rewrites** where the plainer wording lost a safeguard the site exists to show, or
  described a feature wrongly (§2);
- **fixed four things the patch missed** (§3).

Everything not listed below went in exactly as ChatGPT wrote it. That is most of the patch: the
new home headline and introduction, the page titles, the "AI-written · unreviewed" label,
"Source passage", "possible next step", "Read the diagram as text", "Fictional case", the map and
table instructions, the workbench introductions, and the generated wording for applicants.

## 1. Declined

| What ChatGPT proposed | Why I did not apply it |
|---|---|
| **`section43Note()`**: a new block, "When a trade mark is likely to mislead or confuse buyers", with an expandable "What does section 43 require?" paraphrase. It was added to nine places (home example, Ask, applicant explanations, map card, tables, what-if, How it works). | **(a) It is new legal content, not copy.** It paraphrases s 43 in code, with no record behind it: no named model and version, no evidence span, no `content_hash`. CLAUDE.md rule 1: "A record that cannot carry those is not written." **(b) It duplicates a record that already exists.** GC-0168 already has a definition, GD-0139, which has the full record details and already shows on the map and table cards. **(c) It changes the law's words.** Section 43 says "likely to deceive or cause confusion". It does not say "buyers". **(d) It is a new UI component**, and you limited this session to copy. |
| **A glossary entry "section 43 ground for rejection"**, and a new glossary group "Trade mark law" to hold it. | Same reasons as (a), (c) and (d). |

**If you want the idea anyway:** the plain heading ChatGPT wanted ("likely to mislead or
confuse") could be added to GC-0168 as an alternative label, or GD-0139 could get a plainer
wording. Either is a change to an authored record, made in that record with its evidence. It is a
small piece of follow-up work, not copy.

## 2. Changed: the intent was kept, the wording restored what was lost

### Lost safeguards (the site's own rules)

| Where | ChatGPT's wording | What went in | Why |
|---|---|---|---|
| Site-wide notice | "Only the Registrar decides applications" · "Customer explanations use fictional cases" | "It never decides an application" · "Not formally tested with customers" | The notice described the Registrar, not the tool. It also dropped "not tested with customers", which ADR-0145/0146 require the site to say. |
| Footer | "Only the Registrar decides applications." | "Nothing here decides an application." | Same reason. |
| Footer note on sources | Named the Act, the Regulations and the Manual | …plus "It describes practice; it is not law. This site keeps the two apart." | CLAUDE.md rule 5. The original footer said this, and the rewrite dropped it. |
| Ask: the answer's stamp | "The Manual describes examination practice. This answer provides general information. Only the Registrar decides an application." | "The Manual describes examination practice; it is not law. This answer is general information, not legal advice or an examination decision." | Restores "not law" (rule 5) and "not advice". |
| Ask: a declined answer | "This answer covers the sources. Only the Registrar can decide the application." | "Part of this question asked how an application would be decided. The answer does not cover that part: only the Registrar decides applications." | ChatGPT's version never told the reader that part of their question went unanswered. |
| Ask: how the search starts | Dropped "It is plain matching: no model, no guessing" | Added "This step is plain matching and uses no AI." | The difference between a lookup and a model's judgement is something the site deliberately shows (rule 7). |
| Definitions (every card) | "based on examination guidance in the Manual" | "written from the Manual, which describes practice, not law" | Rule 5. |
| Applicant page banner | "Fictional cases for review. These examples do not provide legal advice." | "Fictional cases for review. Not formally tested with customers. These examples do not provide legal advice." | ADR-0146 requires the banner to say the page has not been tested with customers. |
| Applicant banner, 4th point | "The project lists formal testing with applicants as a future step…" | "These explanations have not been formally tested with customers; the project lists that as a future step…" | It now states the fact, not only the plan. |
| Home: applicant card status | "Prototype · fictional cases" | "Prototype · not formally tested with customers" | Same reason. |
| Home: status strip | "Measured: the tests above compared…" · "Built, not tested: … Formal testing … is a proposed next step." | Added "Nothing else has been measured yet." · "It has not been formally tested with customers or measured." | Both limits were dropped. |
| Home: "Possible next" | "…helping examiners research decisions." | "…testing the explanations with customers (the project owner's decision), exploring policy changes and explaining recorded decisions." | Brings back the owner gate. "Research decisions" was vague and could suggest the tool helps make them. |
| Home and What's next: decision support | "Explaining past decisions" · "Explaining a recorded decision" | "Explaining decisions, never making them" · "Explaining a recorded decision, never making one" | "Never making one" is the point of that use. The original titles said it. |
| What's next: customer testing pill | "Formal applicant testing is a proposed next step" | "Not started · no formal testing with customers yet" | States where things stand, not only the plan. |
| Home: "Conditions and exceptions" | "Each test identifies the judgements a person must make." | "…separates facts from the judgements a person must make, and never makes those judgements itself." | Restores "never computed" (ADR-0137). |
| How it works: legal test step | "Recording these steps so a computer can display them is called rules as code." | "…the system shows them and never makes them. Writing a rule down in a structured form a computer can read is called rules as code." | The original undersold rules as code (it is not just for display), and the rewrite dropped "never computed". |
| How it works: answer step | "Only the Registrar decides an application." | "It will not say how an application would be decided." | This describes what the tool actually does (it declines). |
| How it works: connections | "The link keeps the condition in the source and its wording." | …"so a "may" never becomes a "must"." | Keeps the one line that says why it matters. |
| Rules as code: time limits | "How time limits work" | "Time limits, explained but never calculated" | The tool never calculates a deadline, on purpose. |
| Data tables: legal tests | "Where a judgement is needed, the tool leaves it to a person." | …plus "Nothing here applies a test to an application." | Restores the original statement. |
| Data tables: processes | "These are general steps." | "These are general steps, not the history of any application." | Restores the original statement. |
| What-if: banner heading | "This example explores a fictional policy change." | "A fictional policy change. The existing records are not changed. Nothing here is decided." | The owner's condition for this page was that it "must not alter the underlying ontology" (CHAT-0098). |
| What-if: first point | Dropped "No register … for all goods exists in Australia" | Restored | Without it, a reader could take the premise for fact. |
| What-if: premise label in the diagram | "fictional all-goods register" | "fictional · no such register exists · no draft assumed" | Same reason. |
| What-if: questions, related records | "These are questions for a policy team to consider." · "Open a record to read its sources." | …"This page does not answer them." · "Every record here already existed and is unchanged." | Both safeguards were dropped. |

### Wording that misdescribed something

| Where | ChatGPT's wording | What went in | Why |
|---|---|---|---|
| Results page | "People reviewed N questions and specified which passages each search should find." | "A person reviewed N questions and the passages each should find." | One person reviewed them, and they did not write the answer key. |
| Results page | "Across all questions it scored slightly lower than search by meaning." | …"and that small gap is a real one." | The original said this gap is statistically real. Dropping that made the result look better than measured. |
| Home: results headline | "Which search ranked relevant passages highest?" | "Better than keyword search. Not better than search by meaning." | The result is now stated, not hidden behind a question (ADR-0145: outcome first). It was already plain. |
| Results page: limits | "AI-written records … marked "unreviewed" have yet to be reviewed…" | "No trade marks expert has yet reviewed the AI-written ideas, connections or answers." | ChatGPT's version is circular (unreviewed records are unreviewed). |
| Results page: limits | "Updates are currently manual." | "There is no process yet for updating it." | Nobody updates it by hand. There is no update process at all. |
| Results page: corrections | "Corrections appear with the record and leave the original available for inspection." | "A correction changes how a record is shown without changing the record itself, and says so." | Closer to how corrections actually work (ADR-0130). |
| What-if: definition | "…whose quality, reputation or another characteristic is linked to their place of origin." | "…is essentially due to that origin (Trade Marks Act 1995, section 6)." | Section 6 says "essentially attributable". "Linked" is weaker than the law. |
| Standards: named graphs | "Named graphs group statements by source" · "four groups of statements, sized by count" | "…keep statements apart by who or what produced them" · "four separate groups of statements that never mix" | The four groups are source text, expert-approved, AI-written and rule-inferred. They are split by origin, not by source. That they never mix is rule 4. |
| Standards: OWL | "How this project uses OWL" · "Standards considered:" | "OWL: why the project does not run automatic reasoning" · "Considered and set aside:" | The project does not use it. The new heading suggested it did. |
| Ask: legal test note | "This diagram explains the provision." | "This outline breaks the provision into its conditions." | It is a nested list, not a diagram. |
| Ask: comparison | "…compare the lists to see where each passage ranked." | "…the map changed only their order." | Restores the finding. The rewrite turned it into an instruction. |
| Change: unclear citations | "Unclear citations are labelled." | "Where the source data marks a citation as unclear, it is listed, not resolved." | Upstream's ambiguity is deliberately not resolved (rule 6). |
| Applicant page: requirement | "Who takes this step:" | "Who applies it:" | A requirement is not a step. |
| Map family name | "Examination steps and roles" | "Roles, steps and documents" | That family also holds records and documents (for example the examination report). |
| Connection-failure message | "Try again or choose a saved example" | …plus "Some work networks and browser extensions block this address. Try another network…" | Keeps the one hint that actually fixes the usual cause. |
| Workbench: graph page | "…and who reviewed it." | "…and who wrote or reviewed it." | Most statements were written by AI and nobody has reviewed them. |
| Workbench: Ask page | "Only the Registrar decides applications." | "The answers never say how a particular application would be decided." | Describes what the tool does. |
| Workbench: limits cards | "Gaps in the classification system" · "Definitions in the expert-reviewed vocabulary" · "Court decision texts in the project data" | "The main categories are empty" · "No reviewed term has an expert-written definition" · "The project holds no court decision texts" | ChatGPT turned findings into topic labels, which is harder to read. The old "No idea has a definition" is also out of date, because AI-written definitions now exist. |
| Workbench: inbox | "Preview the answers to share" | "Preview exactly what will be sent" | Keeps the "nothing hidden" promise before anything is sent. |
| Glossary: ontology | "A model that…" | "A structured description that…" | On a site full of AI models, "model" is ambiguous. |

## 3. Things the patch missed

1. **A typo it introduced**: "Open a row to read Read the source sentence" (data tables). Fixed.
2. **Two tests it did not update** would have failed CI: `test_whatif.py` (the what-if banner and
   "Text equivalent of the picture") and `test_dependencies.py` ("no recorded dependency, which is
   not the same as no impact"). Both now check the new wording for the same protection. The guide's
   claim that the copy checks passed covered only `test_explorer.py`.
3. **Inconsistent names it left behind**: the results page was "Results and limits", "About this
   prototype", "About the prototype" and "Where it stands" in different places. It is now "Results
   and limits" everywhere. "Reviewed" and "Expert reviewed" badges were also mixed; they now match.
   The glossary term "machine-written, unreviewed" now matches the "AI-written · unreviewed" label.
   "with the ontology" in two score captions is now "map-guided", matching the rest of the page.
4. **Leftover old terms** next to new ones: "Time rule" inside the text versions, "Live answers
   are off on this copy; the prepared answers…" on the home page, and "every way on" in rules as
   code. All updated.

## 4. A question for you

ChatGPT changed "not tested with customers" to wording about *formal* testing, because of your
three test users. I kept "not *formally* tested with customers" everywhere. That is true whoever
those three people were. **If any of them were IP Australia customers, I would leave it as it is.
If none were, the original "not tested with customers" is the plainer statement.** Your call.

## Checks run

- `git apply --check` passed on the current branch.
- `tmk-fetch-upstream --verify`, `tmk-dashboard --write` and `tmk-explorer --write` all ran clean.
- `node --check` passed on every changed script. `git diff --check` is clean.
- The targeted tests passed: `test_explain`, `test_explorer`, `test_dashboard`, `test_whatif`,
  `test_hygiene`, `test_dependencies` and `test_scenarios`. The full suite: 957 passed, 4 expected failures (xfail).
- All 15 explorer pages and the workbench were opened in Chromium at 1280 px. There were no script
  errors and no `undefined` or `NaN` in the text. The site-wide notice fits on one line.
- **Not checked:** narrow widths, keyboard paths, a live paid answer, and whether new readers now
  understand the copy. That last one is the real test, and it needs your users.
