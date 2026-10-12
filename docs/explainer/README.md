# docs/explainer/ — source material for an explainer video

Material for an "explain it like I'm five" video on what an ontology is and why to
build one, made with the Video Overview feature in Gemini Notebook (formerly
NotebookLM). Written 2026-10-12 (S033), from the demonstrator as it then stood.

| File | What it is |
|---|---|
| `ontology-explainer-grounding.md` | **The only source to upload.** Plain English: the problem, the six ingredients of an ontology, five worked examples, the examiner and applicant use cases, the measurement in both directions, limits, a build recipe, FAQ, glossary, fact sheet, storyboard and presenter notes |
| `video-overview-prompt.md` | The settings, a full and a compact steering prompt, variants, and a checklist for reviewing the generated video |

## What belongs here

Text meant to be read by an outside model. It quotes only the published Manual and
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
