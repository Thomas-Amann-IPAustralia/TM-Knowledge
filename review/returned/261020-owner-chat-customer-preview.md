# Owner answer: the customer explanation preview goes on the examiner site

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-20, S044, before the agent built `#/customers`.
**Where:** a Claude Code chat session, answering a multiple-choice question the agent asked.
**Relayed by:** the S044 agent, transcribed the same session.
**Status:** acted on in S044. See ADR-0146 and `review/rulings/2026-10-20-chat-customer-preview.yaml`.

## The question, as asked

> The plan's #/customers page would put the prototype explanations (six invented matters, the three
> tests' requirements, and the filing-to-registration process) on the public examiner site, loudly
> labelled as invented, machine-written, unreviewed, not tested with customers and not advice. It
> only goes live when the branch is merged to main. Should I build it?
>
> Options: "Build it (Recommended)": add #/customers to the site, with the loud banner; it deploys
> only when you merge. "Keep it a file": leave the prototype as the tmk-explain --html file; the
> site only describes it.

## The owner's answer

> Build it (Recommended)
