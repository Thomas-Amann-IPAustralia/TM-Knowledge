# Owner instruction — new groups for the 53 concepts that fitted nowhere

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-09-09.
**Where:** a Claude Code chat session, not the dashboard form.
**Relayed by:** the S019 agent, transcribed the same session it was given.
**Status:** acted on in S019. See ADR-0098 and ADR-0099.

This is an **instruction file written up from a person's words**, which is the one
exception `review/returned/README.md` allows to the rule that this directory holds
only unmodified artefacts. Nothing here is paraphrased into a decision: the quoted
block is his exact words, and everything outside it is labelled as the agent's
account of what was asked. The route was authorised on 2026-09-08 — *"We can
absolutely make decisions in chat windows. Especially if we're recording the
decisions."*

---

## 1. What he was shown first

He asked what was waiting on him or on the trade marks expert, and whether the
dashboard's decision page said so. He was given, in the same session and before
he decided:

- The ten questions then on his queue, and that none of them blocked agent work.
- That only one question was genuinely waiting on a trade marks expert (OQ-0017,
  parked) — the other four in that theme having been closed on 2026-09-08, three
  of them by him and one withdrawn under ADR-0079.
- That the thing actually waiting on a person was not a question at all: **208
  authored records, none read by anybody, `approved_by` null on every one.**
- Four inaccuracies on the published site, the largest being that the Overview
  page's opening sentence said *"Everything here was signed off by a person
  before it was modelled. Nothing on this page was written by an AI as legal
  content"* while a stat tile two blocks below it read *"Records a machine wrote:
  208."*

## 2. The instruction

His words, in full:

> *"Yes, I would like you to fix the issues you identified.*
>
> *Please create new groups which most effectively capture the 53 unassigned
> concepts these will all be reviewed in one go"*

**What was taken from it.** Two things, and the second is the larger:

1. Fix the four inaccuracies as identified. Recorded as ADR-0099.
2. Add groups that hold the 53 concepts typed `none_of_these`, choosing the
   groups rather than bringing him options — *"most effectively capture"* is an
   instruction to exercise judgement, not a request for a shortlist — and sort
   all 53 in one pass so that the whole set can be reviewed together rather than
   a group at a time. Recorded as ADR-0098.

**What was not taken from it.** He did not say how many groups, what to call
them, or where the boundaries fall. Those are the agent's, they are recorded as
`agent-proposed` inside ADR-0098, and they go back to him as OQ-0026 rather than
being treated as settled by his instruction. He also did not touch the four
groups he ruled on at OQ-0001; they are unchanged, and no concept already sorted
into one of them was moved.

**This answers OQ-0024**, which asked what should happen to the 53 and offered
"add groups for the process" as one of four options. He chose it in words rather
than by ticking it, and added the review condition. OQ-0024 is marked answered
against this file.

## 3. What he was told would still be true afterwards, and did not dispute

Stated to him in the same exchange, and preserved:

- Nothing here becomes approved. All 130 typings — the 53 retyped and the 77
  untouched — stay `unreviewed` with `approved_by` null, and only a named person
  on a date moves one (ADR-0086).
- One of the 53 stays `none_of_these` deliberately. `GC-0051`, *mandatory
  application of the section*, is a rule about how a ground operates and fits
  none of the nine groups; a tenth group built to hold one record would be
  fitting the taxonomy to the data.
