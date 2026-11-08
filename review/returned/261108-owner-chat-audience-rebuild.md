# Owner direction: rebuild the front end around the three groups it serves

**Who said it:** the owner, in a Claude Code chat session (the session's user; the chat gave no
name).
**When:** 2026-11-08, S049.
**Where:** a Claude Code chat session.
**Relayed by:** the S049 agent, transcribed the same session.
**Status:** carried out in S049 on `claude/bold-rubin-gvrvea`. See ADR-0151 and
`review/rulings/2026-11-08-chat-audience-rebuild.yaml`.

## The owner's words

> I'd like you to rebuild the front end. You are to focus on providing a very clear user
> experience, catering to each of the 3 groups who stand to benefit from the knowledge graph.
>
> 1. Trade Mark examiners
> 2. The public
> 3. The people informing the strategic direction of the Australian Trade Marks system
>
> You must provide at LEAST one working demo for each of these 3 groups. You are to focus on making
> the experiences for each of these 3 demos EXCEPTIONAL.
> I have asked ChatGPT to conduct an objective analysis of 3 of my favourite interactive experiences
> which communicate complex information in a way that feels intuitive. I would like you to refer to
> these analyses when you are reconstructing the website's front end.
>
> Where there are clearly cross-cutting use cases (for example, interacting with the knowledge graph
> with natural language), you must make the UX clearly bespoke for the particular audience. For
> example, an examiner may accept a more information dense UI if it means they can quickly and
> clearly find the information they're looking for. On the other hand, a member of the public is
> more likely to be easily turned off if they feel overwhelmed with information, so progressive
> disclosure will be imperative. Again, this is simply an example, there are likely other cross
> cutting use cases with other, and, potentially more complex use cases.
>
> I don't want to hide how the system works but I don't want to advertise it. I need to sell the
> audience on what it can do before they'll be interested in how it can do it. They need some level
> of reassurance that it IS trustworthy (or at least will be trustworthy) so they will care about
> what it can do. But as long as we can dull the edge of fear, that will be enough to get them hooked
> on the possibilities.
>
> I'd like the experience to be very clear on what is possible now/in the near future with the
> information and structure we currently have. I want to demonstrate that implementing this system
> will produce immediate results. I also want to make it extremely clear that this is the FOUNDATION
> of a plethora of potential tools, capabilities and services. To that end, I want to try and
> illustrate this future potential, using cards with illustrations like is done on the current
> landing page under "What can you do here" and "How the search finds related pages".
>
> In general the website talks too much about the semantic search. While it is certainly an
> excellent feature, it overshadows the rest of the information.
>
> I'd like the potential future options to be clearly distinct. If there is overlap between
> different options, you should either combine them or make their differences easy to distinguish
> (without explicitly referring to the other to distinguish it).
>
> With the exception of the 'For nerds' section. You must use plain-English prose and assume that
> the user is seeing the page in isolation, as if they have not seen or are aware of other pages.
> That is to say, the user mustn't be required to have read specific previous pages to understand a
> piece of information in front of them (to the extent that is reasonable).
>
> Below is my attempt to describe, at a very high level, the general structure for the new website.
> You are at liberty to exercise your judgement and excellent design acumen. Overall, I am happy with
> the site's general aesthetics.
>
> ---
> # Landing/Overview page
>
> Very high level overview of what the thing is and why its somewhat trustworthy.
>
> ## For examiners
> Helping examiners with basic information now, supercharging them later.
>
> ## For the public
> Help our customers understand the processes to get the most out of the IP system.
>
> ## For direction setting
> Help decision makers and policy setters make informed decisions and understand the potential
> consequences
>
> ## For nerds
> - The knowledge map
> - The standards
> - Data tables
> - Current results and limits
> - Glossary
> ---
>
> Please refer to this long list of potential uses the ontology may provide IP Australia. I would
> like you to consider it while you come up with your own use cases. If you agree with ChatGPT, you
> may feel free to use its suggestion. You are in no way bound to adhere to anything ChatGPT has
> written.
>
> All 4 ChatGPT generated documents can be found in this folder "docs/Nov_rebuild-ref-doc".
>
> I have also attached 4 images to further help elucidate my thinking toward the general 'pitch'
> toward each of the 3 beneficiary groups. By no means am I trying to impart any stylistic
> direction, it is merely a high level information flow, similar to the text description above.

## The four images

Kept as `docs/Nov_rebuild-ref-doc/owner-sketch-1.png` to `-4.png`. In order: the overview ("Trade
Mark law and guidance into rules and code", three coloured doors and a black "For nerds" door, with
the note *"Keep it high level, talk very briefly about what makes it trustworthy (and what parts
still need work). The first thing the user will be is sceptical"*); examiners ("By making the rules
explicit, any subsequent tool, capability or service is inherently explainable", Explainable AI, the
note *"Make it VERY clear, like in the 'Understanding an objection' and 'What the law requires'
sections, that the knowledge graph clearly captures when an assessment is required by an examiner
and when something is 'fact' based"*, then Now: Training and Future: Supercharging); the public; and
direction setting, each with a list of uses.
