# Owner instruction — the project is a pitch, and it needs a system that works soon

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-07.
**Where:** a Claude Code chat session, not the dashboard form.
**Relayed by:** the S023 agent, transcribed the same session it was given.
**Status:** recorded in S023 (ADR-0109). The process changes it prompted are a
*proposal* awaiting the owner's choice — `docs/PITCH-PROPOSAL.md`, OQ-0028 — and
none of them is adopted by this file.

This is an **instruction file written up from a person's words**, the exception
`review/returned/README.md` allows, on the route the owner authorised on
2026-09-08 — *"We can absolutely make decisions in chat windows. Especially if
we're recording the decisions."* The quoted block is the owner's exact words,
typing included; everything outside it is the agent's account and is labelled as
such.

---

## 1. Context

The owner had built a second project with Claude Code — a knowledge base for an
agent over a corpus of web articles — and moved from concept to working
prototype quickly. A standard operating procedure distilled from that project
was committed here as `docs/KB-SOP.md` immediately before this session.

## 2. The instruction

The owner's words, in full:

> *"I've been getting frustrated by the slow progress of developing this
> ontology. Since the last few sessions I've created an agent with Claude Code and
> I was quite happy with how quickly we were able to move from concept to working
> prototype. I appreciate that the creating a knowledge base is somewhat different
> to the intellectual work of creating an ontology, however, I think that there
> may be some lessons in the process from that project which we may be able to
> implement in this one. As such, I got Claude Code to write a standard operating
> procedure, describing the process we took.*
>
> *I would like you to consider the approach and come back with some suggestions
> for anything we could/should adopt to speed up the ontology creation.*
>
> *In my opinion, something that may help the project to move more quickly is to
> let you know that this whole project is to merely pitch the concept and
> demonstrate the value of implementing an ontology for the TM Manual. Because of
> this, we don't need to have every single nuance and complication addressed. I
> really just need a system that works (and SOON!)*
>
> *You can find the SOP in the repo "docs/KB-SOP.md""*

## 3. What was taken from it

Two things, and they are different in kind.

1. **A statement of purpose, which is a decision.** The project exists to pitch
   the concept and demonstrate the value of an ontology for the Trade Marks
   Manual. Completeness of nuance is not required; a working system, soon, is.
   That re-ranks everything on the project's to-do list and is recorded as
   ADR-0109, authority `human`.
2. **A request for suggestions, which is not a decision.** The owner asked what
   to adopt from the SOP. The answer is `docs/PITCH-PROPOSAL.md`. Nothing in it
   is adopted until the owner says which parts — OQ-0028 asks, and the same
   question was put in the chat.

## 4. What was not taken from it

- **No rule changed.** `CLAUDE.md`'s hard rules — the unreviewed stamp, never
  filling `approved_by`, the frozen 190, keeping the Act and the Manual apart,
  never stating an examination outcome — are untouched. "Not every nuance" was
  not read as licence to drop provenance, and the proposal argues those rules are
  cheap once a pipeline writes them.
- **The session protocol in `CLAUDE.md` §3 is unchanged.** Slimming it is one of
  the proposals, and changing the rulebook is the owner's call.
- **No money was spent.** One free, read-only call listed the models the Gemini
  credential can reach (QUIRKS Q-64). No corpus text was sent.
