# docs/explainer/ — explaining the ontology to people new to it

An "explain it like I'm five" account of what an ontology is and why to build one, in two
forms: a source for the Video Overview feature in Gemini Notebook (formerly NotebookLM), and
an interactive, plain-words page made after the video came out thin. Written
2026-10-12 (S033), from the demonstrator as it then stood.

| File | What it is |
|---|---|
| `ontology-explainer-grounding.md` | **The only source to upload.** Plain English: the problem, the six ingredients of an ontology, five worked examples, the examiner and applicant use cases, the measurement in both directions, limits, a build recipe, FAQ, glossary, fact sheet, storyboard and presenter notes |
| `ontology-explainer.html` | **The interactive explainer**: one hand-written, self-contained page (about 70 KB, no external loads) in plain words, with toys: search by words vs by idea, sorting names into jars and ideas onto shelves, building arrows that need a receipt, asking a question, editing a sentence to see what gets flagged, and a quiz. Every quote is the Manual's or the Act's own words; every count is from the demonstrator as at 2026-10-12. Open it in any browser. (A longer, data-heavy version, commit 3c0737e, was replaced at the owner's request for something simpler.) |
| `video-overview-prompt.md` | The settings, a full and a compact steering prompt, variants, and a checklist for reviewing the generated video |

## What belongs here

Text meant for people new to the project, or for an outside model to read. It quotes only the published Manual and
legislation, plus the project's own counts, all regenerable with `tmk-explorer --write`.

## What must not

- An expert's own notes, the owner's own words, a reviewer's name or initials: none of
  these may go into a model prompt (ADR-0088), and an upload to a notebook is one.
- A figure that is not in the generated data or a committed report.
- Any wording that presents machine-written content as reviewed (CLAUDE.md rule 8), or
  the demonstrator as stating an examination outcome.

**The figures date.** When the counts or the measurement change, regenerate the
explorer's data and update the fact sheet (section 18) and every section that repeats
a number. A re-measurement after the S029 restructure is pending.
