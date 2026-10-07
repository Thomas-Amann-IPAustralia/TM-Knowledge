# site/vendor/ — third-party libraries and fonts, served from this site

The owner lifted the "no libraries" rule on 2026-10-07 (ADR-0119). Libraries are
**vendored here**, not loaded from a CDN: the site keeps working on networks that block
CDNs, every byte it serves is still in this repository, and nothing changes under it
without a commit. Each view loads only what it uses (`site/js/lib.js`).

`manifest.json` records the package, version, licence, purpose and SHA-256 of every file;
`tests/unit/test_explorer.py` fails if a file and its hash disagree. Each package's
licence is beside it as `LICENSE.<package>`.

What belongs here: unmodified distribution files (two have their source-map comment
removed, noted in the manifest), fonts, licences. What must not: our own code, or a
file not listed in the manifest.

To update one: `npm pack <package>@<version>`, copy the same distribution file over,
then regenerate its `sha256`, `bytes` and `version` in the manifest.
