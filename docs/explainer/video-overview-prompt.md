# Video Overview: settings, steering prompt and review checklist

How to turn `ontology-explainer-grounding.md` into an explainer video with the Video
Overview feature in Gemini Notebook (formerly NotebookLM). As at October 2026, the
feature offers four settings: **Format**, **Language**, **Visual Style** and an
**(Optional) Steering prompt**.

## 1. Set up the notebook

- **Start a new notebook and upload only `ontology-explainer-grounding.md`.** The video
  draws on every source in the notebook. Other files from this repository would pull in
  internal jargon, decision numbers and file paths. Do not upload anything from
  `review/returned/` or `review/decisions/` either: they hold an expert's own notes and
  the owner's own words, which this project keeps out of model prompts (ADR-0088). The
  grounding document contains none of them. It quotes only the published Manual and
  legislation, plus the project's own figures.
- If the upload refuses a `.md` file, open it in any editor and paste it as a "Copied
  text" source. Or save it as PDF first: the tables survive better that way.

## 2. Settings

| Setting | Choose | Why |
|---|---|---|
| Format | **Explainer** | The structured, comprehensive format; right for a tutorial. *Short* (about 60 seconds) works for a teaser, see section 5. *Cinematic* is English only, for users 18 and over, and leans towards storytelling over clarity |
| Language | **English** | Accent and voice cannot be set; the steering prompt asks for Australian spelling and terms |
| Visual Style | **Custom**, with the description below. Fallback: **Whiteboard** | A whiteboard look suits an ELI5 tutorial and diagrams of circles and arrows. Custom lets you ask for the demonstrator's colour code |

**Custom visual style description** (paste as is):

> Clean, friendly whiteboard explainer: hand-drawn marker lines on white, lots of space,
> one idea per frame. Draw ideas as labelled circles and connections as arrows with
> their verb written along them. Show quotes on index cards. Manual passages are small
> blue squares, Act provisions amber diamonds, Regulations plum hexagons.
> Machine-drafted items carry a small orange "unreviewed" tag. No real people's faces,
> no logos, crests or official government branding.

## 3. Steering prompt (full)

Paste this into **(Optional) Steering prompt**:

> Make an "explain it like I'm five" tutorial on what an ontology is and why an
> organisation might build or adopt one, using the Australian Trade Marks Manual as the
> running example. The audience is trade marks examiners, their managers and
> colleagues, and secondly trade mark applicants. Assume no technical background.
> Follow the storyboard in section 19 of the source. Open with the question about using
> a famous person's name in a trade mark. Explain an ontology with the "book of
> directions versus a map" analogy, then introduce its ingredients one at a time:
> ideas, wordings, kinds, named connections, evidence, and who wrote each record. Walk
> through worked example A (a well-known person's name, section 43) arrow by arrow,
> quoting the Manual, then show the four steps of Ask the Manual. Cover two use cases.
> For examiners: a research and decision-support tool that quickly finds and connects
> the relevant Manual passages, legislation and related material. For applicants: a
> possible next step that would help them understand trade mark requirements, the
> application process and objections raised during examination. Make these points
> throughout:
> - It supports people's judgement and never decides or predicts an outcome.
> - The Manual is practice; the Act and Regulations are law; the two are kept apart.
> - Most of the content was drafted by a machine and is labelled unreviewed.
> - It is a prototype, not official guidance or legal advice.
>
> If you mention the search measurement, give both directions. Use Australian English
> and write "trade mark" as two words. Use only examples and numbers from the source.
> End with: "The Manual tells you what. The ontology shows how it all connects, and
> where it says so."

## 4. Steering prompt (compact, under 500 characters)

If the field turns out to have a length limit, use this instead:

> ELI5 tutorial: what an ontology is and why build one, using the Trade Marks Manual.
> Follow section 19's storyboard and the city-map analogy. Use cases: examiners
> (research and decision support) and applicants (understanding requirements, process
> and objections; a possible next step). Always: supports, never decides or predicts;
> Manual is practice, Act is law; most content machine-drafted, unreviewed. Australian
> English; "trade mark" two words; only facts from the source.

## 5. Variants worth generating

Each variant uses the same notebook with a different steering prompt. Generate two or
three and keep the best.

- **Examiner-focused.** Swap the use-case sentence for: *"Spend most of the time on
  examiners: finding guidance by meaning, joining the dots across Parts, seeing the
  route an answer took, practice and law kept apart, and impact analysis when the
  Manual changes (sections 9 and 10). Mention applicants only briefly, as a possible
  next step."*
- **Applicant-focused.** Swap it for: *"Spend most of the time on how the same
  ontology could help applicants understand an objection (worked example B, section
  6) and the process (worked example C, section 7). Say clearly that this is a possible
  next step and not a service that exists, that it would never predict whether a mark
  will be accepted, and that it is not legal advice."* Showing this one outside the
  team describes something not built, so decide who sees it before sharing.
- **Teaser (Format: Short, about 60 seconds):** *"One idea only: words are not ideas.
  Use the specification example (3 passages use the formal term, 109 name the idea) and
  the map analogy, and end on 'it helps people decide; it never decides for them'."*

## 6. Check the video before anyone else sees it

The voices and visuals are AI-generated and can be wrong. Watch the whole video
against this list. To see the prompt a video was made with, choose **View custom
prompt** from the three-dot menu beside the video in the Studio panel.

- [ ] It never says or implies that the system approves, rejects, accepts or refuses
      applications, or predicts whether a particular mark will be registered.
- [ ] It says the Manual is practice and the Act and Regulations are law.
- [ ] It says most of the content was drafted by a machine and has not been reviewed,
      and it does not call the content "expert-checked" beyond the 52 ideas and 20
      connections that were.
- [ ] The applicant use case is presented as a possibility, not a live service.
- [ ] Every number matches the fact sheet (section 18 of the source). Watch for
      invented percentages or rounded-up claims ("doubles accuracy" and the like).
- [ ] Any mention of the search measurement includes both directions: better than
      keyword search, slightly behind good modern search overall.
- [ ] It does not present the demonstrator as an official IP Australia service, and it
      shows no logos, crests or named individuals.
- [ ] On-screen text says "trade mark", not "trademark", and uses Australian spelling.
- [ ] No invented trade marks or case outcomes. Quoted Manual examples (FORGED IN THE
      OUTBACK, ANTARCTIC BERRIES, MOCHA) are fine.

If a check fails, regenerate with one sentence added to the steering prompt that names
the problem, for example: *"Do not say the system rejects applications."*

## 7. Before you share it

Sharing the video beyond yourself publishes the project somewhere new, and the
measured search results are still an open question for the pitch (OQ-0029). The
figures in the source were measured before the 9 October restructure of the
connections, and a re-measurement is pending. Decide whether the numbers belong in
the video, or keep it qualitative by adding *"Do not quote the search scores"* to the
steering prompt.
