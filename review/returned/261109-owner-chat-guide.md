# Owner direction: Ask a research question for newer examiners, and a conversational guide for the public

**Who said it:** the owner, in a Claude Code chat session (the session's user; the chat gave no
name).
**When:** 2026-11-09, S052.
**Where:** a Claude Code chat session.
**Relayed by:** the S052 agent, transcribed the same session.
**Status:** carried out in S052 on `claude/jolly-hawking-5bcaqf`. See ADR-0154 and
`review/rulings/2026-11-09-chat-guide.yaml`.

## The owner's words

> I'd like you to update the "Ask a research question" to be something like more clearly targeted
> at newer examiners. Experienced examiners will mostly have the entire Act, Manual and Regulations
> memorized. The value is helping new examiners get up to speed faster. The UX should focus on
> reliability and information provenance.
>
> Similarly, I'd like you to build a completely different front end to be targeted towards users.
> They should be able to ask the chatbot questions about the application process and it should
> respond conversationally and with visuals when possible. It can use the same credentials as the
> "research question" thing on the back-end but give it a different system prompt to be more casual
> and friendly. The UX should be clean and uncluttered, only exposing provenance and extra detail if
> the user chooses to further understand the reason they got a particular answer.
>
> Getting the chatbot to ask clarifying questions (similar to the invented case study for the Corner
> Brew coffee (https://thomas-amann-ipaustralia.github.io/TM-Knowledge/#/customers/objection/FM-0006))
> would be an excellent distinction for the customer experience, compared to the examiner experience
> which would be more akin to conversing with the grounding information.

## What the owner decided, as the agent reads it

1. **Ask a research question is for newer examiners**, and its design is about reliability and
   provenance. (The owner's words.)
2. **A separate front end for the public**: a chatbot, conversational, with visuals when possible,
   provenance and detail only on request. (The owner's words.)
3. **The same back end**: the proxy that holds the key, with a different system prompt, "more
   casual and friendly". (The owner's words.) This is the owner's answer to two gates in
   `CLAUDE.md` §3a for this build: what the system may say to a customer (a new prompt for them),
   and the use of the owner's key for a second page.
4. **Clarifying questions** on the pattern of FM-0006: the customer's guide asks; the examiner's
   tool does not.

## What it does not decide

- Showing the guide to customers, testing it with them, or allowing real case data into it. The
  guide is published with the site when the owner merges, on the same footing as the customer
  preview (ADR-0146): a prototype, labelled, not tested with customers. A member of the public who
  finds it could type their own details; the page asks them not to, and the prompt never asks for
  them. Whether to promote it to anyone stays the owner's.
- Any change to the examiner's measured prompt (`answer-v4`): the examiner page's change is in how
  the answer is shown, not in what is asked.
- The spend cap. The guide uses the proxy's existing allowance (30 questions an hour per address,
  300 a day across all readers, now shared by both pages) and the OpenAI project's budget.
