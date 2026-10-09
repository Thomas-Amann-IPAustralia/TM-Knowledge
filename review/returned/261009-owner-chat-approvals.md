# Owner approvals — the explained review items, and the D5 spend

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-09, opening a new session (S027) because S026 had run out of context.
**Where:** a Claude Code chat session.
**Relayed by:** the S027 agent, transcribed the same session it was given.
**Status:** acted on in S027. See ADR-0125 to ADR-0127 and
`review/rulings/2026-10-09-chat-approvals.yaml`.

The owner's words are below, unedited — spelling, punctuation and line breaks as typed.
The reading of them is in the ruling file and the ADRs, never here.

## What the owner had been shown

The owner pasted back the S026 agent's closing chat reply as context. The parts the
approvals refer to are reproduced here as pasted; they are the agent's words, not the
owner's.

> **B1 — yes, it aligns, and your version is cleaner than mine.** I proposed one "kind"
> per idea plus optional "function" tags. You propose the node says what a thing *is*,
> and an edge says what it *does*. That's better, because an edge says what it does *to
> which thing*: "written permission → overcomes → the s 43 ground", not a loose
> "remedy" tag. In practice, factor, exception and remedy would become links, while
> grounds, tests, roles, steps, records and schemes stay as kinds. Remedy would move
> first, and it's built so that's easy. Nothing done until you say. B2, B3 and B6 mostly
> fall out of it.
>
> The six below are all free, and each needs a yes or no:
>
> - **A5 — the duplicate check misses things.** It compared only main names, letter for
>   letter, so "Registrar" and "Registrar of Trade Marks" slipped through. It found 10
>   duplicates when there were really 15 pairs. The duplicates are fixed now, but the
>   check is still weak. I'd make it compare every name, ignoring capitals and plurals,
>   and show each clash as a warning.
> - **A6 — one "same idea" suggestion is wrong.** The machine suggested "implied
>   endorsement" and "endorsement" might be one idea. The first is consumers assuming a
>   famous person backs a product; the second is a note on the Register. I'd mark that
>   suggestion rejected so nobody merges them.
> - **B4 — grounds are uneven.** Sections 39, 40, 42 and 44 each have a "ground" idea,
>   but sections 41 and 43 didn't. Section 43 now does (A2). I'd create the section 41
>   ground the same way. I'd also tidy "prohibited sign", which is filed as both a ground
>   and a kind of sign.
> - **D4 — some "is a kind of" links contradict your signed records.** For example, a
>   machine wrote "an endorsement is a kind of condition of registration", but your
>   signed records say each is *not* the other. Two such links are already gone and three
>   remain. I'd remove those three, and add a check that refuses a "kind of" link when
>   either side says it's not the other.
> - **F2 — the automatic rulebook (SHACL) passed despite all this.** None of its rules
>   looked for duplicates or contradictions, so "zero failures" meant less than it
>   sounded. I'd add rules for shared names and for "kind of" against "not this". The rule
>   for an idea that both uses and rejects a word is already done (E4).
> - **F6 — confidence scores aren't comparable across authors.** The bulk model rates
>   itself 0.84–0.99, even for "Board", which it couldn't identify. The agent session
>   rates itself 0.5–0.9. I'd adopt a standing rule: never rank or filter by confidence
>   across authors.
>
> **D5 quote — nothing spent until you approve**
>
> | Step | What it buys | Model | Calls | Estimate (US$) |
> |---|---|---|---|---|
> | 1 | A second model checks all 563 machine-written relationships against their quoted sentence and the new definitions: sound, vague or wrong, with a corrected reading for wrong ones | Gemini 3.8 Flash | ~71 | ~$1.10 (~$0.55 if run in batch) |
> | 2 | Re-run the search measurement, because recognition changed and the current figures are now out of date | Same judge as before, so the numbers stay comparable | up to 130 | up to ~$1.50 |
>
> - **Total:** about $2.60, or about $2.05 if step 1 runs in batch. That fits in the
>   $3.11 left under the current cap.
> - **Alternatives for step 1:** Gemini 3.1 Pro at about $3.40 (stronger), or
>   gpt-5.4-mini at about $1.30.
> - **Basis:** the estimates use the measured cost of earlier relationship calls, plus
>   25% for retries. The Flash price is introductory until 31 December 2026.
> - **Before any spend:** a free Gemini connection has to be added first. I'd then do a
>   three-call trial and read the results before the full run.
> - **Data sent:** only Manual and legislation text goes to the model.

## The words

> With this context in mind, I approve and would like you to action:
>
> - B1
> - A5
> - A6
> - B4
> - D4
> - F2
> - F6
> - D5. Expenditure approved for step 1 and step 2.
> 	Alternative approved for step 1, the use of Gemini 3.1 Pro.
> 	Re-run the search measurement. If it has a measurable positive impact on the results, you are welcome to use a more intelligent model if it keeps overall expenditure of D5 under $6.
> 	To confirm, I'm allowing the expenditure of an additional $2.89 on top of the remaining $3.11, totalling in $6.
> 	I leave the decision of 'measurable positive impact' to your discretion but I expect the decision to be justified either way.
