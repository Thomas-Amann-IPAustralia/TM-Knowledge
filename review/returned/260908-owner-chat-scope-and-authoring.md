# Owner instruction — scope and authoring authority

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-09-08.
**Where:** a Claude Code chat session, not the dashboard form.
**Relayed by:** the S015 agent, transcribed the same session it was given.
**Status:** acted on in S015. See ADR-0079 to ADR-0085.

This is an **instruction file written up from a person's words**, which is the one
exception `review/returned/README.md` allows to the rule that this directory holds
only unmodified artefacts. Nothing here is paraphrased into a decision: the quoted
blocks are his exact words, and everything outside them is labelled as the agent's
account of what was asked.

The owner's standing position on the route, given in the same message:

> *"We don't need to be so formal. We can absolutely make decisions in chat
> windows. Especially if we're recording the decisions."*

---

## 1. Remove the section 43 boundary

His words, in full:

> *"we are deliberately keeping the PoC restricted to s43 on the assumption that
> this will save time and effort. However, creating bounds and exceptions for s43
> has been time consuming and, I suspect will continue to cause confusion with the
> experts. Would the challenge of creating an ontology actually scale so
> drastically by covering the entire Trade Marks Examination Manual?"*

And then, after being shown the numbers:

> *"yes, I would like to completely remove the s43 barrier."*

**Recorded as** ADR-0081.

---

## 2. An agent may make higher-risk calls, if it records them as unreviewed

His words, in full:

> *"I would also like to add another important decision. I would like to alter
> your rule in Claude.md which says you cannot make calls on legal matters. We
> have already identified that Trade Mark Experts are better at identifying and
> correcting information than they are at writing them.*
>
> *To that end, I would like you to update your rule so that you can make higher
> risk decisions AS LONG AS you record it has not been reviewed or approved by an
> expert yet.*
>
> *This will remove the barriers for us in working through the engineering, giving
> us a fully fleshed out ontology and knowledge graph that the experts can then
> interrogate, correct and iterate. Having a working version will motivate them to
> engage with the process because the value will become clear.*
>
> *This does not mean that we're completely off the hook for provenance though
> either. I want to ensure all of the existing rules around references to the Act,
> Regulations and Handbook remain in tact. We're essentially just re-framing when
> a legal decision is being made. In reality, your still not making a decision.
> You're making a best effort attempt given everything you know and have available
> to you which is then validated/invalidated by a subject matter expert. It also
> makes it less burdensome on the experts because then it's a matter of correcting
> problems rather than writing solutions. If something is not corrected, it can be
> assumed that it's valid (though we'll retain a record that it has never been
> validated by an expert)."*

**Recorded as** ADR-0079 (the authority), ADR-0085 (the last sentence, which has
two halves that had to be implemented separately).

---

## 3. Four clarifying questions, and what he chose

Put to him before anything was changed. The question text is the agent's; the
selection is his.

| Question | His answer |
|---|---|
| Where should authored legal content live, relative to the 190 records the expert signed? | **Kept separate, graph reads both.** `eval/gold/` stays frozen as the signed set; authored content sits in a parallel store; the graph reads both and stamps every node. |
| Does unreviewed content stay out of what the finished system tells an examiner, or is labelling enough? | **Labelling is enough.** Unreviewed content may be served, visibly marked as never validated. |
| Does this open the extraction stages (2–4), or only hand-authoring? | **Open Stages 2–4** across the whole Manual. |
| What happens to the 178 seed records and the 10 decisions blocking 168 of them? | **Resolve them all now, marked unreviewed.** |

**Recorded as** ADR-0080, ADR-0082, ADR-0083, ADR-0084 respectively.

---

## 4. What the agent flagged, and he did not countermand

Stated to him in the same exchange, before the changes were written:

> The product-level rule that the system does not state an examination outcome to
> an examiner is being **preserved**. He removed the *review gate*; that limit is a
> *scope* constraint from the roadmap and from his expert's own signed
> prohibited-use records. He was told explicitly that it could be lifted too, on
> his word.

No instruction to lift it was given. It stands. **Recorded as** ADR-0082
consequence 4, and as a rule in `CLAUDE.md` §2 "What is still off limits".
