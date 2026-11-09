# Owner direction: only starters Tommy can answer, and a way back out of the guide

**Who said it:** the owner, in a Claude Code chat session (the session's user; the chat gave no
name).
**When:** 2026-11-09, S053, after trying Tommy Tradecraft live (ADR-0154, ADR-0155).
**Where:** a Claude Code chat session.
**Relayed by:** the S053 agent, transcribed the same session.
**Status:** carried out in S053 on `claude/dazzling-cori-zwxqyi`. See ADR-0156 and
`review/rulings/2026-11-09-chat-starters.yaml`.

## The owner's words

> Tommy Tradecraft can't answer the first pre-written question. The other answers are excellent
> though. Please only include pre-written questions the chatbot is equipped to answer.
> Additionally, please add a back button or something so a user can leave the interaction more
> easily

## What the owner decided, as the agent reads it

1. **Every pre-written question (starter) must be one Tommy can answer.** "How does applying for a
   trade mark work?" is not; the other three are kept.
2. **The guide gets a visible way out**, a back control, so a reader can leave the conversation.

## What it does not decide

- Which question replaces the first. The agent chose it (ADR-0156).
- Anything about Tommy's prompt, the search, or what Tommy may say.
