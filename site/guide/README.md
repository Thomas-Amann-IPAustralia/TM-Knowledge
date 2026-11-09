# site/guide/: Tommy Tradecraft, the guide

A chat for the public about trade marks (ADR-0154, on the owner's word, CHAT-0103), published
with Tradecraft at `…/TM-Knowledge/guide/`. Its persona is Tommy Tradecraft (ADR-0155, CHAT-0104):
an AI guide that says it is an AI, and never passes itself off as a person or as IP Australia. A
person asks in their own words about what the law asks of a trade mark, how applying works, or
what an objection means, and gets a short, friendly reply, a picture where one helps, and at most
one clarifying question with its answers as buttons. Where each point comes from opens only when
they ask ("Where this comes from").

It is a prototype on the same footing as the customer explanation preview (ADR-0146): not tested
with customers, not advice, never an outcome. Showing it to customers, testing it with them, and
any real application or report reaching it stay the owner's decisions (`CLAUDE.md` §3a).

## What belongs here

- `index.html`: the page's frame (top bar, the thread, the message box, the source sheet).
- `guide.css`: its own stylesheet, apart from the explorer's. It keeps the explorer's source
  colours and marks (the Manual a blue square, the Act an amber diamond, the Regulations a plum
  hexagon, ADR-0130) and its self-hosted fonts from `../vendor/`. Classes start `gd-`.
- `guide.js`: the conversation. A live turn is the examiner page's pipeline with the guide's
  prompt: the model's reading of the words (ADR-0132), the browser's search (`../js/engine.js`),
  then one call through the proxy (`../js/live.js`'s `guide`) with the instructions and schema
  from `../data/chat.json`'s `guide`, which `tm_knowledge.explain.guide` writes. Every quote is
  checked with `Engine.verify`, as the examiner's are.
- `visuals.js`: the pictures, each an explanation object from `../data/explain.json` named by id
  (a process as a journey, a legal test as what the examiner looks at, a question's options side
  by side), each with its text equivalent and stamp.
- `common.js`: escaping and how to name a source in plain words.

With live answers off (no proxy, the day's limit reached, or an error) the guide walks through
four guided topics built from `explain.json` alone, the clarifying question of the invented
Corner Brew case (FM-0006) included. The page's own words there say what to look at; they state
no law.

## What must not go here

- `../js/app.js` or anything that imports it (`diagrams.js` does): it starts the explorer's
  router. Shared code the guide needs lives in modules with no side effects.
- A legal proposition of the page's own, an outcome, a date worked out, a "may" made a "must", or
  a reply without its stamp.
- A key, a CDN, or a link to the workbench. `tests/unit/test_guide.py` holds these.
- Real customer or case data in a fixture, a starter or an example.
