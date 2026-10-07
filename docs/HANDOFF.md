# HANDOFF

**Last updated:** 2026-10-07 · S025 (end) · branch `claude/exciting-fermi-wn6hps`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The demonstrator is built (D1–D3 met, D4 drafted), and the published site is for
trade marks examiners.** Everything machine-written is unreviewed. S024's explorer was
merged to `main` (PR 25). S025 acted on four requests the owner made in chat about it:

1. **The Cytoscape map now appears beyond its own page.** `site/js/minimap.js` embeds a
   small map with the map's marks (kind colour, signed filled / machine dashed, solid /
   dashed lines), hover cards, click-to-read the sentence a connection rests on, zoom
   buttons and a link to the full map. It is used in:
   - **Ask the Manual** — "The same ideas on the map": the starting ideas ringed, ideas
     too common to steer greyed, and **every** connection the search followed; when
     more than twelve, the twelve the answer-writer reads are dark, the rest faint;
   - **When the text changes** — "What rests on this page, on the map": the ideas that
     quote the page (ringed) and the connections that quote it. *Simulate a rewrite*
     now flashes those connections and pulses those ideas as the layers light up.
   The owner's words were "the Cytoscape map was added to the front page"; the home
   page actually draws a D3 circle packing. Read as "use the map in more places". If
   they meant the circle packing, that is a small follow-up.
2. **"Every page of the Manual" titles are legible.** The D3 treemap cut Part titles
   to "60 · The Madrid Protoc…" — small Parts cannot hold a title at any font size. It
   is now one row per Part in reading order, title in full (wrapping), pages as tiles
   as wide as the page is long, with an instant hover callout (Part, page title,
   passages, amendments, connections) and a colour key. The ripple panel is sticky on
   wide screens so a click low on the list still shows its result.
3. **The tour's squares (steps 1–2) say what they are.** A key above the grid ("one
   square is one passage…"); a magnifier that pops onto the square under the pointer
   and glides between squares; the square's Part lights up (step 1); a callout with
   the passage number, Part, page, heading and opening words, and in step 2 which
   wording it uses. It opens on a pulsing example so the idea is clear before any
   hover; click opens the passage. Phones get the callout under the grid. The reading
   order is computed in the browser from `passages.json` and matches
   `_display_order` on all 2,460 passages (checked in the browser).
4. **"How the ontology worked on it" now says how it chose.** Under the hop diagram,
   per question: (1) which words in the question matched which idea, and by which name
   (main name / another name / a machine-written everyday phrasing), and which ideas
   were too common to steer (with their passage counts); (2) that **every** connection
   one step out is followed, none weighed against another, signed and machine alike,
   with the real counts — and that the twelve the answer-writer sees are the first
   twelve by identifier, not the most relevant (Q-70); (3) the three ranked lists and
   how they merge. The step list beside the diagram now gives the true number of
   connections followed (it used to report the capped twelve).

Unchanged from S024: `site/` routes (`#/`, `#/tour`, `#/map`, `#/ask`, `#/change`,
`#/about`), vendored libraries with checksums (ADR-0119), streaming live answers,
`tmk-explorer --write` builds `site/data/` from the pinned snapshot (ADR-0117),
`engine.js` = Python search minus vectors (parity-tested). **No Python changed this
session, and no paid call was made.** Spend: US$3.49 of the $6.60 cap.

612 tests pass (`python3 -m pytest`, about ten minutes with the snapshot present).
Checked in Chromium at 1400 px and 390 px, light and dark: no console errors on any
view; mini maps draw (Change, Part 29.3: 21 ideas, 22 lines); clicks reach the drawer.

## Waiting on the owner

1. **Merge this branch** to `main` to publish (no PR opened — not asked for).
2. If not already done: **add the key** as an environment secret (Settings →
   Environments → `github-pages` → `OPENAI_API_KEY`), then run the pages workflow.
   Advised: a dedicated, restricted, budget-limited key — it is recoverable from the page.
3. **OQ-0029 — which results the pitch claims.** Unchanged.

## Next actions

1. Look at the published Ask and Change pages after the merge; if the owner meant the
   home page's circle packing in (1) above, put a packing of the question's ideas on
   Ask, or of a Part's ideas on Change.
2. **An examiner feedback route** is still missing (S024's item): a per-answer
   "wrong / partly / right + note" that composes an email or a file. Expert notes must
   never reach a model (ADR-0088).
3. If abuse of the key shows up: a small proxy holding it (`TMK_LIVE_ENDPOINT`).
4. Carried over: OQ-0029's "test the fix first" option; 12 "same concept" merge
   candidates for a person.

## What to distrust

- **The twelve connections in the prompt are an accident of identifier order** (Q-70).
  The page now says so. Changing it changes the measured prompt: `bulk.cli` and
  `engine.js` together, then re-measure.
- **Concept recognition is label matching**, now spelt out on the Ask page: "register"
  matches *Register of Trade Marks*, "mark" matches *trade mark* (an alternative label).
- **The live configuration was not measured** — keyword + ontology, no vectors.
- **The kinds view is an arrangement**; kind-to-kind arrows count relationship records.
- **The Ask mini map can be dense** — up to 86 connections; the ring staggers labels
  past 22 ideas, but a big neighbourhood still needs the zoom buttons.
- The benchmark is model-written and model-graded (unchanged from S023).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); install with `pip install -e ".[test,rdf]"`.
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, then `tmk-explorer --write`,
  then serve `site/` (e.g. `python3 -m http.server` inside it).
- **`engine.js` and `search/index.py` must change together** — the parity test fails
  otherwise. So must `bulk.jobs._answer_render` and `engine.prompt`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **The main map's positions are computed** (`map.js`). Do not reach for a force layout
  there: fcose overlapped the compound kind boxes. `minimap.js` uses a seeded D3 force
  run only for Change, where there are no boxes. Both Cytoscape instances hang off their
  container (`.cy` / `.mini`) as `.cy` for browser checks.
- **A `data-ref` attribute opens the passage drawer** (app.js listens on the document).
  The Change page's tiles use `data-page` for that reason.
- **Updating a vendored library**: copy the dist file, then update `sha256`, `bytes`,
  `version` in `site/vendor/manifest.json`.
- Vectors are not committed (ADR-0115); flex tier overloads (Q-67); never kill a
  relate run (Q-68).

## Open items (agent-proposed, provisional)

- S025's reading of "the Cytoscape map … elsewhere" (above), and the treemap's
  replacement by Part rows — layout calls, recorded here and in the commits.
- ADR-0117; ADR-0118's and ADR-0119's agent parts; ADR-0113 and ADR-0115.
