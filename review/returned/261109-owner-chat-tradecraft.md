# Owner direction: name the site Tradecraft, and the public chatbot Tommy Tradecraft

**Who said it:** the owner, in a Claude Code chat session (the session's user; the chat gave no
name).
**When:** 2026-11-09, S052, after reviewing the guide (ADR-0154).
**Where:** a Claude Code chat session.
**Relayed by:** the S052 agent, transcribed the same session.
**Status:** carried out in S052 on `claude/jolly-hawking-5bcaqf`. See ADR-0155 and
`review/rulings/2026-11-09-chat-tradecraft.yaml`.

## The owner's words

> Good please update the site to change it's name to "Tradecraft". I'd like the public facing
> chatbot to have a persona named "Tommy Tradecraft"

## What the owner decided, as the agent reads it

1. **The site is called Tradecraft.** Its title, brand and footer say so. "The foundation", where
   the pages use it for the linked records underneath, is the thing Tradecraft is built on, not its
   name, and stays.
2. **The public chatbot's persona is Tommy Tradecraft.** The page, its links and the model's
   instructions use the name.

## What it does not decide

- That Tommy may pass for a person. The agent added, inside the owner's instruction, that Tommy
  says plainly it is an AI when asked, never claims to be a person, an examiner, a lawyer or an
  attorney, and never claims to speak for IP Australia; the page says the same. This keeps
  `CLAUDE.md` rule 8 (no machine output unlabelled) true of a named persona.
- The repository's name, the package's name or the examiners' tools' names.
