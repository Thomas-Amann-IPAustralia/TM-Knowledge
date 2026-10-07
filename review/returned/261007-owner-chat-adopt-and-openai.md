# Owner instruction — adopt the pitch proposal, use OpenAI, spend at most $1 for a quote

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-07, in reply to `docs/PITCH-PROPOSAL.md` and OQ-0028.
**Where:** a Claude Code chat session, not the dashboard form.
**Relayed by:** the S023 agent, transcribed the same session it was given.
**Status:** acted on in S023. See ADR-0110 and ADR-0111.

An instruction file written up from a person's words, on the route authorised on
2026-09-08. The quoted block is the owner's exact words; everything outside it is
the agent's account and is labelled as such.

---

## 1. What the owner had been shown

`docs/PITCH-PROPOSAL.md` in full, and a chat summary of it: a four-part finish
line, a batch pipeline in place of hand-authoring (proposed on Gemini 3.8 Flash),
measurement of plain against ontology-enhanced search, an "Ask the Manual" page,
lighter session paperwork, and asking the owner only at named gates. Three
decisions were asked for: the finish line, a spend cap, and the process cuts.

## 2. The instruction

> *"Yes, your suggested approach sounds excellent. I approve all of the things
> you've suggested except for the use of Gemini. You should also have access to an
> OpenAI API. I would like you to use Sol 6.1 on medium effort for the bulk
> knowledge work. I'm not ready to give you a precise costing for the full runs
> until you tell me what I'm getting for each spend. For now, you may spend a
> maximum of $1. From that, you should be able to provide me with a quote you'll
> expect the full run to cost."*

## 3. What was taken from it

1. **The proposal is adopted in full** — the finish line (D1–D4), the pipeline,
   the measurement, the "Ask the Manual" page, the process cuts (P5) and the named
   gates (P6) — **except the model**. ADR-0110.
2. **The model is OpenAI's `gpt-6.1-sol` at medium reasoning effort** for the bulk
   knowledge work, replacing Gemini 3.8 Flash. "Sol 6.1" resolved to the API id
   `gpt-6.1-sol`, the only model of that name the credential lists. ADR-0111,
   superseding ADR-0087.
3. **Spend is capped at US$1** until the owner approves a quote, and the quote
   must say what each spend buys. ADR-0111.

## 4. What was not taken from it

- **Model choices for work that is not knowledge work were not assumed.** Writing
  benchmark questions and judging search results are measurement; the quote asks
  the owner which model does them rather than defaulting silently.
- **Gemini was not merely deprioritised.** "Except for the use of Gemini" is read
  as: no Gemini calls, for anything, including embeddings.
