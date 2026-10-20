# Owner direction: redesign the front end around the outcome

**Who said it:** the owner, in a Claude Code chat session (the session's user; the chat gave no
name).
**When:** 2026-10-20, S046, after the S044 site rework (ADR-0145, ADR-0146) and S045's Package 5 were merged.
**Where:** a Claude Code chat session.
**Relayed by:** the S046 agent, transcribed the same session.
**Status:** carried out in S046 on `claude/trusting-franklin-c1h7wi`. See ADR-0148 and
`review/rulings/2026-10-20-chat-site-redesign.yaml`. The mock-up the owner names was uploaded to the
repository as `docs/tm-knowledge-redesign.html` before the session began.

## The owner's words

> I'd like you to completely re-design the front end of this repo. The primary purpose of the front end is to communicate the value of the underlying ontology. It ought to communicate the outcome first, the ontology isn't the focus its a means to an end, and its the outcome we should focus on. That being said, we still should communicate how it works (and explain it in an easy to understand way). Wherever possible, you should communicate things visually. Interactivity is cool too if it helps the user more intuitively understand what is being communicated. The knowledge graph, for instance, is a thing that's useful to interact with. You must consider progressive disclosure. Try to avoid making things look cluttered. I have asked ChatGPT to have a go at redesigning the front end. (docs/tm-knowledge-redesign.html) I generally like the vibe it's gone for but I'm happy for you to make it your own. You may use whichever libraries will best serve your vision. You do NOT need to consider mobile interactivity. Users will only interact with the interface on a desktop/laptop. This work must not impact or change the shape of the underlying ontology.
