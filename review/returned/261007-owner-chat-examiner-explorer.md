# Owner instruction — rebuild the front end for examiners; a live chatbot on the owner's key

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-07, after an agent listed what remained before the site could go to subject
matter experts (a feedback route, a fresh brief, live questions, the site being built around the owner).
**Where:** a Claude Code chat session.
**Relayed by:** the S024 agent, transcribed the same session it was given.
**Status:** acted on in S024. See ADR-0117 and ADR-0118.

## The instruction

> *"The site is somewhat unintuitive and contains alot of information that is unnessesary for an
> expert reviewing the structure of the system's ontology. I would like to completely reconstruct the
> front end so that a Trade Mark examiner will quickly understand the value and construction of the
> ontology. You should consider creative and interactive methods of progressive disclosure. They
> should be able to view the ontology at different levels of abstraction so they can understand how,
> even if underlying specifics change, much of the hierarchy remains accurate and unaffected.*
>
> *I will include an OpenAI API token either as an Environment secret or Repository secret in Github
> (please direct me which one is best). This will be used to drive the small local app so they can see
> what an Ontology may enable. I wonder if visualising the ontology as a graph, demonstrating the
> chatbots multi-hop search may be a useful method of demonstrating the value? I'll leave it to your
> discretion as to what would best communicate why an ontology is worth spending the time to develop.*
>
> *Please feel free to just bury the existing webpages somewhere on the local site so I can still
> access it but so it would be unlikely for someone from Trade Marks to find. They are my colleagues
> and its not risky for them to see (the repo is public after all), I just don't want it to distract
> them. The chatbot does not need to be password protected. I know random people might be able to
> access it and use my tokens for free but I'm not popular enough to really worry about that."*

## What was taken from it

1. **A new examiner-facing site replaces the dashboard at the site root**, built around progressive
   disclosure and levels of abstraction (kinds → ideas → text), with a guided tour, the map, Ask the
   Manual with the multi-hop path drawn, and a page showing what a change to the Manual's text touches.
2. **The old dashboard moves to `/workbench/`**, unlinked from the new site, still built and working.
3. **A live chatbot answers examiners' own questions with the owner's OpenAI key**, unprotected. The
   owner accepts that anyone can use it. The agent's reading, flagged to the owner in the same reply:
   a key used from a static page is not only *usable* by anyone but *recoverable* by anyone who reads
   the page, so it should be a dedicated, restricted, budget-limited key.
4. **Which secret:** the agent's direction is an environment secret named `OPENAI_API_KEY` on the
   `github-pages` environment (ADR-0118).
