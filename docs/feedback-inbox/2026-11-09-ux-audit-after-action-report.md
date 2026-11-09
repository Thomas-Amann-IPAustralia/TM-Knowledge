# After-action report: ChatGPT's UX review of the audience rebuild

**Session** S050 · 2026-11-09 · branch `claude/practical-thompson-7l786c` · ADR-0152
**Input** `docs/Nov_rebuild-ref-doc/TM-Knowledge-UX-Audit-2026-11-09.html` (ChatGPT), against `fa4fa10`.
**The owner's instruction** (CHAT-0101): make the changes I agree with, record where I do not, and
keep the overview's "One rule, from words to structure".
**Scope** Presentation only: `site/` and its tests. No record, graph, prompt, explanation object or
generated data file changed, so nothing changes what the system may say.

## Verdict

The review is good. Its two strongest points are right and were fixed first: the site said more than
it can show about checked quotations (F02) and about the consequences of a change (F03), and the
public explainer drew an invented report's assessments with green ticks, which read as the site
endorsing them (F04). Of the 30 findings:

- **Done as proposed, or very nearly: 16** (F02, F03, F04, F11, F12, F13, F14, F15, F16, F17, F18,
  F20, F22, F25, F27, F29).
- **Done in part: 9** (F01, F05, F06, F07, F09, F19, F26, F28, F30). Each says what was not done and
  why.
- **Declined: 5** (F08, F10, F21, F23, F24).

Most of the declines and partial declines have one of three reasons: **the owner already decided
it** (the overview's headline and the section labels are the owner's own words from the sketches;
the owner asked to keep the section 44 example), **the safeguards are required** (the repeated
warnings are pinned by rulings and tests), or **the page is For nerds**, where the owner allowed
technical depth.

## Finding by finding

| # | Finding | Verdict | What changed, or why not |
|---|---|---|---|
| F01 | Retire the nine-step "How it works" | **In part** | Agreed that a search walkthrough should not be called "How it works": the page is renamed **"A search, step by step"** (title, breadcrumb, footer, For nerds door) and says search is one tool of several. For nerds now opens with a **four-step "How the foundation works"** (sources, ideas and rules, traceable records, tools) using the review's suggested copy. Ask's "Why these sources?" fold links to the walkthrough. **Not retired**: it is a working, tested explanation, it sits under For nerds where depth is welcome, and the problem the review names (search looking like the whole proposition) is a labelling problem, which the rename and the new orientation fix. Old routes (`#/tour`, `#/model`) still reach it. |
| F02 | Quotation matching presented as proof | **Done** | "Every statement shows its source" is now "Each statement is linked to its source", adds that unmatched statements are flagged and that "a matching quotation shows where the words come from, not that the answer is right". The examiners' demo card and Ask's "Check an answer" say the tool checks that a quotation exists, not that the answer is right. The stamp "AI-written · unreviewed" is unchanged. |
| F03 | "See the consequences" overclaims | **Done** | Direction hero: "Find what a legal change might affect", with the review's supporting line. The overview's door: "Helping decision makers find what a change might affect". "would touch" became "might touch". Trace a change now says a count is a starting list for review, not a measure of legal impact, risk or effort. The "no recorded dependency is not no impact" wording is kept. |
| F04 | Green ticks on fictional assessments | **Done** | Every recorded state is now a small **document mark with words** ("recorded: met", "recorded: not met", "not known") in neutral colours, never a tick; "not known" stays amber because it is what a reader most needs to notice. The case board and the public overview's preview each say: "Recorded means the invented report or case record says so. This site restates it; it does not assess whether it is right." I used "recorded", not the review's "Report says", because some states come from the invented case's dates, not its report. |
| F05 | The concept bow-tie is too busy | **In part** | Connections that lead to the same concept under the same predicate are now **one entry marked "3 records"**; selecting it lists every record with its own sentence, strength and condition, so nothing is merged or lost. Four shown per group, not six. Names **wrap instead of being cut** with an ellipsis. The explore arrow is larger and named "Explore *concept*"; the panel hint says selecting never leaves the page. **Not done**: making a list the default with "See as graph" as the alternative. The owner asked for the site to be visual wherever possible (ADR-0148), the bow-tie is the demonstration, and with the duplicates bundled and names readable it reads as a grouped list already. |
| F06 | Rename "For direction setting" and "For nerds" | **In part** | **Not renamed**: both labels are the owner's own words (CHAT-0100 and the owner's sketches). The review allows for this and suggests subtitles instead: the overview's door and the section's hero now say "For direction setting · policy and strategy", and the hero's choice reads "I work in policy or strategy". "For nerds" and its `</>` button are kept as the owner named them. |
| F07 | The headline describes the technology first | **In part** | **Headline kept**: "Trade mark law and guidance, turned into rules and code" is the owner's own wording from the overview sketch, and it names exactly what the section 44 example beneath it shows. **Done**: the button that only scrolled ("Discover what it might enable") is replaced by three audience choices in the first screen, as the review proposes: "I'm an examiner", "I'm applying for a trade mark", "I work in policy or strategy", with "Compare all three" and the For nerds link beside them. |
| F08 | The animated section 44 example is too much | **Declined** | You asked for it to stay, and I agree with you: it is the clearest demonstration of "words to structure" on the site, it already rests on a fully rendered frame (the animation only highlights), and it respects reduced motion. |
| F09 | Eleven selectable tools turn the overview into a catalogue | **In part** | The tools are now in two labelled rows, **Working now** and **Possible next · not built yet**, so the selector cannot be read as a list of tasks or as eleven equal things. **Not replaced** with a smaller diagram: the owner asked for the site to show it is "the FOUNDATION of a plethora of potential tools", and this figure is where that is shown. |
| F10 | Safeguards repeat until unseen | **Declined** | I agree with the diagnosis but not with removing any of them now. The status strip, each section's "about" line, the public explainer's banner and the record stamps are required by rulings (ADR-0082, ADR-0146, ADR-0151: each section must stand on its own) and pinned by tests (Q-107). The owner also asked for enough reassurance to "dull the edge of fear". This pass removed none and added only short, specific lines where a reader could misread output (F02 to F04). If the owner wants fewer, which ones to drop is a decision about what the site says, so it is theirs (CLAUDE.md §3a). |
| F11 | Future lists longer than the demos | **Done** | Each audience page shows **three possibilities** (two within reach, one needing more data) and folds the rest under **"Other possibilities (N)"**. Nothing is removed; horizons are still said in words. |
| F12 | Examiner hero diagram too abstract | **Done** | The preview now says "section 43 ground for rejection: 28 recorded connections", and shows **one real connection at a readable size**, with its sentence, its source and its stamp, and a link to "Explore every connection and read the source behind each one". The counts are read from the data. |
| F13 | Ask starts with too much | **Done** | A two-line introduction with a "How to check an answer" link, **three example questions** (was five) with "Browse all 129" beside them. Choosing an answer already scrolled to it; that is unchanged. |
| F14 | Three decisions before the explanation | **Done** | The objection walkthrough opens straight on one case. The six case cards fold behind **"Change example"**, beside a compact line naming the case and its objections. The objection selector and the six steps are unchanged (they are needed for the two-objection case). |
| F15 | The case picture is also a control panel | **Done in the lighter form** | The board now says "Select a condition to read its exact wording", and each step still lights only its part. A separate "Show the full rule" action was not added: What the law requires already shows the full rule for every test. |
| F16 | The journey's branch reads as certain | **Done** | Stage names wrap to three lines instead of being cut ("Acceptance notified and…" now reads whole). The key says "may proceed to" and "only if the application's facts call for it", and a line under the picture says "One illustrative route through the process, not a prediction for any application." |
| F17 | Top-six provisions need a denominator | **Done** | Retitled "Provisions with the most recorded links", with "out of N provisions with any" and "Counts are links, not importance or risk." Each bar is labelled with its breakdown (direct + via the Manual), and each is a "Trace" link. |
| F18 | "Guess first" is a gate | **Done** | The result shows at once. A line above it offers "Guess before you look"; choosing it veils the result and asks, and the answer then appears as before. The offer returns for each new provision until used. |
| F19 | The ripple and the 500-page grid are disproportionate | **In part** | **Done**: the three exact numbers now lead, above the ripple, with a stacked bar and the note that the citing passages are the route, not more records. **Not done**: hiding the ripple behind "Visualise links" (the owner asked for pictures, and the counts now come first) or moving the page grid into a drawer (it is how a reader picks a Manual page to trace). |
| F20 | The what-if repeats its premise | **Done** | One banner stays visible, with its pinned sentence. The premise and the four caveats fold under "What this example assumes, and what it cannot tell you". The two panels per question were already side by side. |
| F21 | The full graph is the hardest place to start | **Declined** | The map is in For nerds, and the owner asked for it as "a thing that's useful to interact with" (ADR-0148): the whole map is the point of the page. Its side panel already offers six starting ideas. F22's key was added instead. |
| F22 | The map needs an in-place key | **Done** | A key now sits on the map itself: colour is the kind of idea; dot size is how often the Manual names it, **not importance**; shapes are the sources. The side panel says the same about dot size. |
| F23 | The rules page repeats itself | **Declined** | It is a For nerds page, where depth is its purpose, and the overview's section 44 teaser is meant to lead here. The review's point about the three thumbnails looking like placeholders is fair; replacing them with real micro-examples is a reasonable follow-up, not done here. |
| F24 | The standards page reads as a tutorial | **Declined** | It already opens with a clickable picture of the stack (the "browsable reference" the review asks for) and the code samples are short, real blocks of the committed graph that a test pins. For nerds is allowed to be technical. |
| F25 | Results should begin with a verdict | **Done** | A one-paragraph evidence box leads the page: the measurement in both directions, read from the data, then "That measures how the search ranks passages. It does not show that an answer is right", then what has not been tested. Sections reordered: the measurement, **what has not been tested**, authorship, sources, the search method, and the owner's open decisions last. **Kept**: the method section, because it holds facts nothing else on the site gives (the live model, effort and prompt version behind the measurement); it is renamed "How the research search works" and links to the walkthrough. |
| F26 | Icons need a vocabulary and a size floor | **In part** | Stroke raised to 1.8; the two 13 px icons raised to 14 px. The site already reserves the source shapes for sources and never uses them as navigation. A full audit of every icon's meaning was not done. |
| F27 | Secondary text too faint | **Done, at a different value** | `--ink-3` is now `#5b6863`: at least 4.95:1 on every paper and tint the site uses (it was 3.5 to 4.1:1). The review's `#53615b` also passes, but it is darker than the body text's own secondary colour, which would flatten the hierarchy; `#5b6863` passes and keeps it. The old grey is kept as `--ink-faint` for three decorative strokes only. |
| F28 | Test keyboard, focus and zoom | **Verified in part** | Checked in Chromium with Playwright: a connection selected by keyboard announces its pressed state and never navigates; the guess is keyboard-usable and moves focus into the quiz; "Change example" opens by keyboard with focus on the current case; the overview's in-page link scrolls and focuses; a tabbed control shows a focus ring. **Fails, before and after**: at 200% zoom (a 683 px viewport) every page scrolls sideways, because the layouts are built for desktop widths and need about 1,040 px (the same before and after this pass). That is the owner's desktop-only decision (ADR-0148), so it is recorded, not changed. Not done: a screen-reader pass. |
| F29 | Deep pages need a way back | **Done** | Every deep page now has a breadcrumb above its title ("For examiners / Explore a legal concept · Working demonstration"), the section linked back. On the public demonstrations it names the explanation shown. |
| F30 | Readiness, authorship and evidence look alike | **In part** | Readiness is now a dot and a label, not a pill; authorship keeps the rust stamp; Trace a change's "Working · not measured" pill is plain words ("A working demonstration. Not measured."). Other state pills (Ask's "Live answers on", the what-if's) were left as they are. |

## Found along the way

- **The overview's "Discover what it might enable" button never worked as intended.** A link to
  `#ld-doors` went through the hash router, which re-rendered the overview and scrolled to the top.
  Links to a place on the same page are now handled before the router (`app.js`; Q-110).
- The breadcrumb, the possibilities fold and the recorded-state marks are shared helpers
  (`crumb` in `layers.js`, `possibilityGrid` in `illustrations.js`, `STATE_WORD` and `stateGlyph` in
  `diagrams.js`), so a new view uses the same pattern.

## What I would ask the owner

Nothing blocks. Two things are yours if you want them: whether to drop any of the repeated safeguards
(F10), and whether the site should reflow at 200% zoom, which would reverse the desktop-only decision
(F28).
