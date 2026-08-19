# tests/fixtures/stage0/ — shape fixtures for the record schemas

Two directories, and the difference between them is the whole point.

- `valid/` — one well-formed record per Stage 0 type. Every judgement field
  holds a `«placeholder»`, never a plausible-looking answer. These fixtures
  exercise the schemas; they are not examples of Stage 0 content and must never
  be copied into `eval/gold/`.
- `malformed/` — one record per rule the schemas enforce, each broken in exactly
  one way, with the expected failure named in the filename. A schema that stops
  catching something fails here rather than silently passing everything.

**No legal content, in either directory.** A plausible filled record is worse
than a blank: it anchors the reviewer and it gets copied forward (CLAUDE.md
rule 1, parallel track §3). Refs are real because they must resolve; every
sentence is a placeholder because it must not read as an answer.

**No snapshot files here** (ADR-0004). A fixture that needs the corpus reads it
from `data/upstream/` behind the `snapshot` marker.
