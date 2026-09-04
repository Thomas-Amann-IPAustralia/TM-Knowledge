# `tm_knowledge.dashboard`

Generates `site/data/` and transcribes answers coming back. Two commands:

```bash
tmk-dashboard --write     # regenerate the site's data
tmk-dashboard --check     # fail if what is committed has gone stale (CI runs this)
tmk-ruling --body issue.md --issue-number 12 --issue-url … --author … --write
```

| module | does |
|---|---|
| `build.py` | reads the committed artefacts, composes the pages |
| `blocks.py` | the eight block kinds the browser can render |
| `sources.py` | parses `DECISIONS.md`, `ROADMAP-STATUS.md`, `GLOSSARY.md` |
| `questions.py` | reads and validates the question queue and the rulings |
| `ruling.py` | a submitted issue body → a file in `review/rulings/` |
| `cli.py` | the two entry points |

## The rules this package works under

**It reads committed artefacts only.** Never the pinned snapshot. That is what
makes the site deployable from a bare checkout — a page build cannot fail
because upstream was unreachable — and it is why figures that exist only in the
rebuilt source graph are not restated on the site. The generated reports carry
those, and the site renders the reports rather than summarising them.

**It restates; it never derives.** Every number is a count of something a
reviewer signed or a generator produced. Where a count is measured over a subset
— classes populated in the *approved* graph and not the source graph, say — the
page says which subset.

**It refuses rather than guessing.** A document that will not parse, a glossary
marker naming a term that does not exist, a submitted answer naming an option
that is not on the form: all raise. A dashboard is read by people who will not
check it against the data, so a wrong number here is worse than a missing page.

## Adding a page

1. Write `_yourpage(facts)` in `build.py` returning `{id, title, lede, blocks}`.
2. Add it to `PAGES` and to the dict in `build()`.
3. `tmk-dashboard --write` and commit the JSON.

No JavaScript changes unless the page needs a block kind that does not exist.
