# Owner decisions — the nine decisions in the review response

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-17, S037, replying to the nine "Decisions for the owner" at the end of
`docs/ONTOLOGY-REVIEW-RESPONSE.md`, after the agent had explained items 3, 5, 6, 7 and 8 in chat.
**Where:** a Claude Code chat session.
**Relayed by:** the S037 agent, transcribed the same session.
**Status:** recorded, not acted on. The owner asked that none of the approved work start in S037.
See ADR-0136 and `review/rulings/2026-10-17-chat-review-response.yaml`.

The owner's words are below, unedited — spelling, punctuation and line breaks as typed. Each
decision's wording (the agent's, quoted back by the owner) is followed by the owner's response.
The reading of them is in the ruling file and the ADR, never here.

## The owner's words

> Please record my responses. Do not commence any of the work I'm approving in this session. Please provide me with a short prompt to provide a new session with a fresh context window.
>
> Re-capture the legislation upstream and move the pin to the Act's compilation 48. Until then I recommend showing "the Act as in force from 14 October 2024" on every answer.
> Response: Yes Re-capture the upstream legislation. Ensure that shifting to the latest compilation doesn't break anything downstream.
>
> Lift the deferral on definitions (8 October item F4) before the pitch. Recommended.
> Response: Agreed, the defferal may be lifted.
>
> Lift the deferral on the stale documents (item F5). Recommended; about an hour of work.
> Response: Agreed, the defferal may be lifted.
>
> Approve two changes to what the live chatbot is given and told: the modality and condition on each graph path line (F14), and the rule against concluding absence (F19). Recommended.
> Response: Approved.
>
> Remove the masked-key fallback once the proxy serves, and revoke the old key; this reverses part of ADR-0118.
> Response: Approved. The chatbot already now communicates with the Render proxy server so the masked key is not required.
>
> Confirm that the D2 ruling ("correct known defects") covers the GC-0017 and GC-0018 SKOS conflict, which sits inside signed records.
> Response: Yes.
>
> Turn on branch protection for main, requiring the harness checks (a GitHub setting).
> Response: Not at the moment thank you.
>
> Choose which measured results the pitch claims (OQ-0029). On this evidence: the ontology does not beat the best plain search on model-written questions; it does, modestly, on the expert's ten; the reading recovers the loss from names alone; and its clearer value is explanation and traceability, which can be shown but has not been measured.
> Response: Claim the gain over keyword search, and say plainly that modern search ranks better. Then lead with what the ontology uniquely does.
>
> Name an amount for re-measurement, if wanted, after packages 1 and 2.
> Response: I'll defer the re-measurement for now. We'll likely undergo some additional re-work before we re-measure.
