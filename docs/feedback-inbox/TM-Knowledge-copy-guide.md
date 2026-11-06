# TM-Knowledge plain English copy guide

**Handoff for Claude Code · 7 November 2026**  
**Scope:** The 13 pages of the public explorer and the 12 pages of the separate project workbench. The accompanying patch contains the exact edits to 28 source files and one existing test file. It was prepared against `84b43da8b8c34babb30219abc86ef871c89fc827` on `main`.

## Start here

Give Claude Code this guide and `TM-Knowledge-copy.patch`. The tables below explain the changes and show examples. The patch supplies the complete old and new text, file paths, line locations and surrounding code. This matters for phrases such as “What it rests on”, which refer to a source passage on one screen and to records affected by a change on another.

> Apply the copy in the accompanying patch to TM-Knowledge. Read the repository’s CLAUDE.md first. Run `git apply --check` before applying the patch. If the branch has moved, use the named route, file and surrounding function to place the intended change. Preserve any newer factual corrections. Keep legal quotations, formal concept names, citations, review status and calculated figures intact. Regenerate both sets of site data and run the checks at the end of this guide. Report any text you could not match or any case where the new wording would misdescribe the current feature. Leave publishing to the project owner.

## The first screen

**Search Australian trade mark law and guidance**

Ask a question in your own words. The tool finds passages from the Trade Marks Act 1995 and Trade Marks Regulations 1995, which set out the law. It also searches IP Australia’s Trade Marks Manual of Practice and Procedure, which explains how examiners apply the law. Open a passage to read it for yourself.

**Primary button:** Ask a question  
**Second button:** See how it works  
**Alongside the introduction:** Example question

| What the reader saw | Why it was hard to use | Where the replacement lives |
|---|---|---|
| “From a question in plain words to the law and practice that answer it.” | The reader had to infer what they could do and what they would get back. The new headline names the action and what it searches. | `site/js/home.js`, `render()`, `.hm-title` |
| “It recognises the ideas in a question … the Manual, the Act and the Regulations that bear on it.” | The first sentence assumed readers knew which documents the shortened names referred to. The new introduction names each source and distinguishes law from examination guidance. | `site/js/home.js`, `.hm-copy .lede`. The research page and shared footer also introduce the sources. |
| “One real test question” | “Real” could sound like an actual applicant’s case. “Test” describes the project’s evaluation rather than what the reader is about to see. | `site/js/home.js`, `demo()`, visible caption and accessible figure name |
| “section 43 ground for rejection” | Seeing a section number and the words “ground for rejection” still leaves the reader asking what the examiner is concerned about. | `site/js/app.js`, `section43Note()`, called from the example and related detail views |

### How the section 43 explanation reads

**section 43 ground for rejection**  
**When a trade mark is likely to mislead or confuse buyers**

**What does section 43 require?**  
Think about what the mark, or part of it, suggests to buyers. If using the mark for the goods or services in the application would be likely to mislead or confuse buyers for that reason, the application must be rejected for those goods or services.

The short name is visible immediately. The reader can open the question beneath it for the explanation, the source passage and its AI-written review label. This preserves three details that can get lost in a shorter paraphrase: the impression comes from the mark or part of it, the test concerns its use for the specified goods or services, and the threshold is *likely*. The home example actually connects “plant variety name” to this particular ground.

**Implementation detail.** The formal label comes from `authored/concepts.yaml`, record `GC-0168`. The helper displays the note only for that concept or the exact provision `TMA1995/s43`. It also appears in the worked example, the related legal test, applicant explanations, relevant policy records, the map card and the data tables. The glossary lets a reader look it up independently. Leave the general concept `GC-0006`, formal titles, matching terms and quoted law intact.

[IP Australia, Trade Marks Manual of Practice and Procedure, Part 29.1](https://manuals.ipaustralia.gov.au/trademark/1.-trade-marks-likely-to-deceive-or-cause-confusion)

## Public explorer copy by page

Each row gives one change a reader will notice. The implementation includes the surrounding paragraphs, controls, captions and relevant interactive states.

| Page | Find in the source | Replace with | Why this helps |
|---|---|---|---|
| Overview `#/` · `home.js` | “One foundation, three uses.” | “What can you do here?” | The cards that follow now answer a visitor’s question. Their descriptions say what to choose and what opens. |
| Research `#/ask` · `ask.js` | “No checked support” | “No matching quotation” | Names exactly what the automated check found. The accompanying text asks readers to check whether a quotation supports the statement. |
| Applicant examples `#/customers` · `customers.js` | “It is here so examiners can see it and pick holes in it.” | “An objection is a concern an examiner raises about an application. Choose an example to see what the examiner is asking, which legal requirements apply and what could happen next. You can also explore the steps in an application.” | A reader can start with an unfamiliar term, then choose requirements, process or objection. |
| Trace a change `#/change` · `change.js` | “no recorded dependency, which is not the same as no impact” | “We found no record that cites this provision directly or through the Manual. A change could still affect other guidance.” | Explains an empty result without giving false reassurance to an editor. |
| Future uses `#/future` · `future.js` | “What the same foundation could do next” | “Current tools and possible next steps” | The introduction separates what someone can use now from what the project might build. Each use has “What we have now” and “What we still need”. |
| Policy example `#/whatif` · `whatif.js` | “What if geographical indications became their own right?” | “What if Australia had a geographical indications register for all goods?” | Names the specific fictional change. The introduction explains a geographical indication before asking what guidance might need review. |
| How it works `#/how` · `how.js` | “The law has a shape, and it is written down” | “What must an examiner consider?” | Gives the reader a question to answer from the next diagram. Earlier steps explain keyword matches and links between ideas. |
| Knowledge map `#/map` · `map.js` | “Every idea, and how they connect” | “Explore trade mark ideas and their connections” | The first instruction now explains what a dot and a line represent, and what selecting an idea reveals. Also covers the categories view and selected-record cards. |
| Rules as code `#/rules` · `rules.js` | “A connection keeps its wording’s force” | “Why ‘may’ and ‘must’ matter” | The example explains the difference between a possible action and a requirement. The diagram retains the source wording, conditions and exceptions. |
| Standards `#/standards` · `standards.js` | “What the graph is written in” | “How the knowledge map stores information” | Readers get the purpose first. Individual sections retain technical names such as SHACL and explain the job each standard does. |
| Glossary `#/glossary` · `glossary-view.js`, `glossary.js` | “Every term the site uses, in three parts …” | “Find a term to see what it means, how this site uses it and its technical name.” | The entries and popovers use the same order. The definition of a 95% interval now explains what it means if the range includes zero. |
| Data tables `#/table` · `table.js` | “The ontology, as tables” | “Browse the knowledge map as tables” | The introduction identifies the five tables, how to read the underlying source and how to download a CSV. Detail cards distinguish a source passage from a legal effect or option. |
| Results and limits `#/about` · `about.js` | “What works, what was measured, and what is still to decide” | “What we tested and what we know” | Explains what the ranking test measured, the comparison methods, who graded the results and the limits of the human-reviewed sample. |

Public JavaScript file names in this table are relative to `site/js/`. The old `#/tour`, `#/model` and `#/circles` links resolve to existing pages through the router.

### Copy that changes after a reader acts

| Reader action or state | Earlier wording | New wording |
|---|---|---|
| Choose a sample instead of typing a question | “Or try a prepared question, answered in advance” | “Try an example question” |
| Enter a question when live answers are off | “Live answers are off on this copy …” | “Live answers are off. Enter a question to find passages, or choose an example to read a saved answer.” |
| Get an answer that attributes a Manual quotation to legislation | “Said to state the legislation, but every quote kept is from the Manual” | “This statement describes the law, but its quotations come only from the Manual.” |
| Open an objection with missing facts | “What remains, and what would change this explanation” | “What is still unclear?” |
| Open a process diagram | “a way on” | “possible next step” |
| Follow a map node to its evidence | “What it rests on” | “Source passage” |
| Inspect a source in the change tool | “What rests on it” | “Records linked to this provision” |
| Open the record behind a diagram | “Text equivalent of the diagram” | “Read the diagram as text” |

### Shared source locations

| Source | Copy it owns |
|---|---|
| `site/index.html` | Browser title and description, navigation, site-wide notice, footer and no-JavaScript message |
| `site/js/app.js` | Source names, common review labels, record detail headings, loading and unavailable passages, the section 43 explanation |
| `site/js/layers.js` | Links and descriptions beneath pages. Their labels say where the reader can go rather than making them interpret “layer 3 of 4”. |
| `site/js/diagrams.js` | The shared keys for facts, personal judgements and missing information |
| `site/js/live.js` | Connection failure when the answer service cannot be reached |
| `src/tm_knowledge/explain/engine.py` | Generated applicant wording also used in text equivalents, including the question about an unidentified objection, recorded conditions and missing dates |
| `src/tm_knowledge/explorer/build.py` | Category-family names used in generated data. The same names appear in map controls and tables. |

## Project workbench

The workbench has a separate entry point at `/workbench/`. These screens are for the project team, so terms such as “signed record”, “provision” and “SKOS” remain where the reader needs them. Each introduction explains the task before asking the reader to use those terms.

The workbench generates its navigation and page introductions in **`src/tm_knowledge/dashboard/build.py`**. Each route below is relative to `/workbench/`.

| Page | Generator | What the revised introduction lets someone do |
|---|---|---|
| `#/overview` | `_overview()` | Identify the sources and read the separate counts of signed and AI-written records. |
| `#/ask` | `_ask()` | Choose a saved answer, compare it with keyword search and understand what quotation matching checks. |
| `#/inbox` | `_inbox()` | See which decisions need their input and which work depends on an answer. |
| `#/map` | `_map()` | Select a dot to read its source or double-click to expand nearby ideas. |
| `#/tree` | `_tree()` | Use the yes/no branches to explore legal questions, with the distinction between a branch and an application outcome clear. |
| `#/vocabulary` | `_vocabulary()` | Look up preferred terms, alternatives and easily confused terms in the reviewed section 43 material. |
| `#/ontology` | `_ontology()` | Understand what the draft modules describe and how a module is approved. |
| `#/graph` | `_graph_page()` | Read a three-part statement and identify its source and review status. |
| `#/questions` | `_questions()` | Compare the questions the system needs to answer with what it can answer today. |
| `#/limits` | `_limits()` | Distinguish gaps in the data from conclusions the system is prohibited from making. |
| `#/decisions` | `_decisions()` | Look up a project decision, who made it and what replaced it. |
| `#/reports` | `_reports()` | Read reports in the context of when the project generated them. |

The patch also updates the workbench shell in `site/workbench/index.html` and `app.js`. For text inside cards, filters, evidence panels and the inbox, see `blocks.js`, `network.js`, `tree.js` and `inbox.js` in the same directory. For example, “What it most expects to have got wrong” becomes “What an expert should check”.

## Applying and checking the copy

From the repository root, pass the actual path to the patch.

```sh
git apply --check /path/to/TM-Knowledge-copy.patch
git apply /path/to/TM-Knowledge-copy.patch
git diff --check
```

Use the repository’s normal environment to regenerate both sites. Generated JSON is an output. Applying edits directly to it would lose them at the next publication.

```sh
tmk-fetch-upstream --verify
tmk-dashboard --write
tmk-explorer --write
python -m pytest -q tests/unit/test_explain.py tests/unit/test_explorer.py tests/unit/test_dashboard.py
```

**Acceptance checks for the next browser preview**

1. Start at the home page. A first-time reader should be able to say what they can search, what the Manual is for and what they get when they select a passage.
2. Replay the plant variety example. Read the section 43 subtitle, expand its explanation and open its source. Open the general ground for rejection and a section 44 card as controls. The section 43 explanation belongs only on the matching concept or test.
3. Try a saved research question and a typed question with live answers off. The copy should distinguish searching for passages from receiving a new AI answer. Compare a matching quotation, a missing quotation and a possible law/practice mix-up.
4. Open all three applicant tabs. In a fictional objection with missing information, check that a reader can distinguish a reported fact, a judgement and an unanswered question. Compare the written version with the diagram.
5. Check a change with several linked records and one with none. In the latter case, the wording should leave open the possibility that other guidance needs review.
6. At a narrow width, check the home example, longer legal heading, chart captions, warnings, map cards and navigation. Use the keyboard to open the section 43 explanation, source passage and glossary popover.

**Editorial boundaries.** This pass covers interface copy and selected reader-facing generated explanations. Source quotations, signed records, evidence spans, canonical names, saved benchmark answers and the project owner’s quoted statement retain their original wording. Dynamically generated live answers depend on their model and sources. Making a source easier to understand here means adding a labelled explanation alongside it.

**Testing language.** Three people gave feedback on the website’s wording. Their roles and test tasks were unspecified. The replacement copy distinguishes that feedback from a formal study of whether applicant explanations improve understanding. The short case labels describe what the reader can see: fictional cases.
 
## What was verified

- Applied the patch to a clean copy of the named commit and compared all 29 resulting files byte for byte with the proposed revisions.
- Generated the explorer data from the pinned Manual and legislation and generated the 12 workbench pages from the project records. Checked JavaScript syntax and compiled the changed Python files.
- Rendered the home example in a JavaScript test harness using the actual generated data. Confirmed it shows the new section 43 heading once and that the existing reference handler opens the saved section 43 passage. The general reason for rejection and the section 44 provision did not trigger that note.
- The existing explanation, explorer and dashboard tests include literal checks for four old copy passages. `tests/unit/test_explorer.py` updates those checks to assert the new wording for the same protections: incomplete search coverage, Manual versus law, fictional examples and the status of applicant testing. Of the 120 targeted tests, 116 passed in the first run. All four copy checks passed when rerun against the revised wording.
- The implementation was reviewed from the repository. Browser layout, a paid live answer and comprehension with new readers still need checking. The published site was not edited.

[Repository at the reviewed revision](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/84b43da8b8c34babb30219abc86ef871c89fc827) · [Public explorer](https://thomas-amann-ipaustralia.github.io/TM-Knowledge/)
