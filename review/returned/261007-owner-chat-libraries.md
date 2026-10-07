# Owner instruction — use whatever libraries make the site best

**Who said it:** Thomas Amann, repo owner.
**When:** 2026-10-07, after the S024 agent rebuilt the front end in plain JavaScript with no
libraries (the rule the old dashboard kept, and its test enforced).
**Where:** a Claude Code chat session.
**Relayed by:** the S024 agent, transcribed the same session it was given.
**Status:** acted on in S024. See ADR-0119.

## The instruction

> *"You can use more than basic JavaScript. Use whatever libraries and things that will help make
> it the best it can be"*

## What was taken from it

1. The explorer may use third-party libraries and fonts. The "no libraries, nothing from
   elsewhere" rule was the dashboard's (its README and a test), not a project rule in CLAUDE.md.
2. How they are served is the agent's call: vendored into `site/vendor/` with a checksum manifest
   rather than loaded from a CDN (ADR-0119).
