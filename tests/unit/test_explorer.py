"""The examiner explorer at `site/` and the data `tmk-explorer` writes for it.

Three things must hold. The site serves nothing from elsewhere. Every record it
shows keeps who wrote it and whether a person signed it. And the browser's
search and answer prompt are the ones Python measured — the same rankings and
the same prompt, question by question — so a live answer on the page is asked
the way the 129 prepared answers were.
"""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess

import pytest

from tm_knowledge.config import REPO_ROOT, UPSTREAM_DIR
from tm_knowledge.explorer import build as explorer

SITE = REPO_ROOT / "site"

needs_snapshot = pytest.mark.skipif(not UPSTREAM_DIR.exists(), reason="needs the pinned snapshot (tmk-fetch-upstream)")


def test_the_site_is_self_contained():
    """Every byte the explorer serves is in the repository: its own code, and the
    libraries and fonts vendored under site/vendor/ (ADR-0119). Nothing from a CDN."""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    assert "explorer.css" in html and "js/app.js" in html
    assert not re.search(r"""(src|href)=["']https?://""", html)
    sources = sorted((SITE / "js").glob("*.js"))
    assert sources, "the explorer's modules are missing"
    for path in sources:
        text = path.read_text(encoding="utf-8")
        if path.name != "lib.js":
            assert "import(" not in text, f"{path.name}: load libraries through lib.js"
        for host in ("cdn", "unpkg", "jsdelivr", "googleapis", "fonts.g", "http://", "https://"):
            assert host not in text.lower().replace("http://www.w3.org", ""), f"{path.name} names {host}"
    lib = (SITE / "js" / "lib.js").read_text(encoding="utf-8")
    for target in re.findall(r"""import\(["']([^"']+)["']\)""", lib):
        assert target.startswith("../vendor/"), target
    css = (SITE / "explorer.css").read_text(encoding="utf-8")
    assert "@import" not in css and "url(http" not in css
    for font in re.findall(r'url\("([^"]+)"\)', css):
        assert font.startswith("vendor/fonts/") and (SITE / font).exists(), font


def test_every_vendored_file_matches_its_manifest():
    """A vendored library changes only by a commit that also changes its hash."""
    import hashlib

    vendor = SITE / "vendor"
    manifest = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    for name, entry in manifest.items():
        data = (vendor / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], f"{name} differs from its manifest entry"
        assert entry["licence"] and entry["version"], name
    served = {str(p.relative_to(vendor)) for p in vendor.rglob("*")
              if p.is_file() and p.name not in ("manifest.json", "README.md") and not p.name.startswith("LICENSE.")}
    assert served == set(manifest), f"unlisted or missing: {served ^ set(manifest)}"
    for package in {entry["package"] for entry in manifest.values()}:
        licence = vendor / ("LICENSE." + package.replace("/", "_").replace("@", "").lstrip("_"))
        assert licence.exists(), f"no licence beside {package}"


def test_the_workbench_is_kept_but_not_linked():
    """The owner's dashboard moved to site/workbench/ (ADR-0118); nothing an
    examiner opens links to it."""
    assert (SITE / "workbench" / "index.html").exists()
    for path in [SITE / "index.html", *sorted((SITE / "js").glob("*.js"))]:
        assert "workbench" not in path.read_text(encoding="utf-8"), path.name


def test_live_answers_are_off_without_a_key():
    assert explorer.live_payload(None) == {"enabled": False}


def test_a_published_key_is_masked_and_recoverable():
    """The key is published when the owner supplies one (ADR-0118). It must not
    appear as a plain `sk-` string, and the page must be able to recover it."""
    key = "sk-proj-abcDEF0123456789"
    payload = explorer.live_payload(key)
    assert payload["enabled"] and payload["endpoint"] == explorer.OPENAI_RESPONSES
    assert key not in json.dumps(payload) and "sk-" not in json.dumps(payload)
    mask = base64.b64decode(payload["m"])
    mixed = base64.b64decode(payload["x"])[::-1]
    assert bytes(a ^ b for a, b in zip(mixed, mask)).decode() == key


def test_a_proxy_endpoint_publishes_no_key():
    payload = explorer.live_payload(None, "https://proxy.example/answer")
    assert payload == {"enabled": True, "endpoint": "https://proxy.example/answer"}


def test_predicate_labels_come_from_the_relation_list():
    labels = explorer.predicate_labels()
    assert labels["mayGiveRiseTo"] == "may give rise to"
    assert labels["broader"] == "is a kind of"


@pytest.fixture(scope="module")
def files():
    if not UPSTREAM_DIR.exists():
        pytest.skip("needs the pinned snapshot (tmk-fetch-upstream)")
    return explorer.build(generated="2026-01-01")


@needs_snapshot
def test_every_file_is_built(files):
    assert set(files) == {"ontology.json", "search.json", "passages.json", "stability.json",
                          "tour.json", "examples.json", "chat.json", "live.json"}


@needs_snapshot
def test_every_record_says_who_wrote_it(files):
    """Signed and machine-written records stay distinguishable on every record,
    and a machine-written one always carries its unreviewed status (rules 4, 8)."""
    from tm_knowledge.authored import store
    from tm_knowledge.stage0 import goldset

    onto = files["ontology.json"]
    gold, authored = goldset.load(), store.load()
    assert onto["counts"]["concepts"]["signed"] == len(gold["gold_concept"])
    assert onto["counts"]["relations"]["signed"] == len(gold["gold_relationship"])
    for record in onto["concepts"] + onto["relations"]:
        assert record["origin"] in ("signed", "machine")
        if record["origin"] == "machine":
            assert record["machine"]["review_status"] == "unreviewed", record["id"]
            assert "signed" not in record
        else:
            assert record["signed"]["by"], record["id"]
    assert "approved_by" not in json.dumps(onto)


@needs_snapshot
def test_kind_links_add_up_to_the_relationships_between_concepts(files):
    onto = files["ontology.json"]
    concepts = {c["id"] for c in onto["concepts"]}
    between = [r for r in onto["relations"] if r["s"] in concepts and r["o"] in concepts]
    assert sum(row["total"] for row in onto["kind_links"]) == len(between)


@needs_snapshot
def test_the_live_prompt_is_the_measured_one(files):
    from tm_knowledge.bulk import jobs

    chat = files["chat.json"]
    assert chat["instructions"] == jobs._ANSWER_INSTRUCTIONS
    assert chat["schema"] == jobs._ANSWER_SCHEMA
    assert chat["model"] == "gpt-6.1-sol"


@needs_snapshot
@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the browser engine")
def test_the_browser_engine_matches_python(files, tmp_path):
    """Rankings, recognised concepts, graph paths and the answer prompt itself,
    for every benchmark question."""
    import yaml

    from tm_knowledge.bulk import jobs
    from tm_knowledge.bulk import links as links_module
    from tm_knowledge.search.index import KeywordIndex, Systems, relations_from
    from tm_knowledge.upstream.loader import load_corpus

    explorer.write(files, tmp_path)
    answers = yaml.safe_load((jobs.BENCH_DIR / "answers.yaml").read_text(encoding="utf-8"))["answers"]
    questions = [{"key": a["key"], "question": a["question"], "prompt": i < 12} for i, a in enumerate(answers)]
    (tmp_path / "questions.json").write_text(json.dumps(questions), encoding="utf-8")
    result = subprocess.run(["node", str(REPO_ROOT / "tests" / "explorer_parity.mjs"), str(tmp_path),
                             str(tmp_path / "questions.json")], capture_output=True, text=True, check=True)
    browser = json.loads(result.stdout)

    corpus = load_corpus()
    links = links_module.link(corpus)
    ctx = jobs.Context(corpus=corpus, links=links)
    systems = Systems(KeywordIndex(corpus), links, None, jobs.load_aliases(), relations_from(ctx.gold, ctx.authored))
    for q in questions:
        js = browser[q["key"]]
        assert js["keyword"] == [h.ref for h in systems.keyword(q["question"], 10)], q["key"]
        hits, trace = systems.ontology(q["question"], 10)
        assert js["ontology"] == [h.ref for h in hits], q["key"]
        assert js["recognised"] == trace.recognised and js["paths"] == [p[3] for p in trace.paths], q["key"]
        if q["prompt"]:
            hits8, trace8 = systems.ontology(q["question"], 8)
            passages = [h.ref for h in hits8]
            cited = [e.id for ref in passages[:3] for e in corpus.chunks[ref].provisions if not e.needs_a_human]
            legislation: list[str] = []
            for ref in trace8.provisions + cited:
                found = jobs.passage_at(corpus, ref)
                if ref not in legislation and found is not None and found.text:
                    legislation.append(ref)
            item = jobs.Item(q["key"], {"question": q["question"], "recognised": trace8.recognised,
                                        "paths": [list(p) for p in trace8.paths][:12],
                                        "passages": passages, "legislation": legislation[:3]})
            assert js["prompt"] == jobs._answer_render(ctx, item), q["key"]
