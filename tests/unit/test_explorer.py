"""The examiner explorer at `site/` and the data `tmk-explorer` writes for it.

Three things must hold. The site serves nothing from elsewhere. Every record it
shows keeps who wrote it and whether a person signed it. And the browser's
search and answer prompt are the ones Python measured — the same rankings and
the same prompt, question by question — so a live answer on the page is asked
the way the 129 prepared answers were.
"""

from __future__ import annotations

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


def test_live_answers_are_off_without_a_proxy():
    assert explorer.live_payload(None) == {"enabled": False}


def test_a_proxy_endpoint_publishes_no_key():
    payload = explorer.live_payload("https://proxy.example/v1/responses")
    assert payload == {"enabled": True, "endpoint": "https://proxy.example/v1/responses"}


def test_no_build_can_publish_a_key(monkeypatch):
    """The masked-key fallback is removed (ADR-0136, reversing part of ADR-0118):
    the build takes no key, reads none from the environment, and the page has no
    code to unmask one or send it."""
    import inspect

    monkeypatch.setenv("TMK_LIVE_OPENAI_KEY", "sk-proj-abcDEF0123456789")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-abcDEF0123456789")
    monkeypatch.delenv("TMK_LIVE_ENDPOINT", raising=False)
    assert explorer.from_environment() is None
    assert "key" not in inspect.signature(explorer.live_payload).parameters
    assert "key" not in inspect.signature(explorer.build).parameters
    live_js = (SITE / "js" / "live.js").read_text(encoding="utf-8")
    assert "Authorization" not in live_js and "reveal(" not in live_js


def test_the_pages_workflow_passes_no_key_to_the_build():
    from tm_knowledge.config import REPO_ROOT

    workflow = (REPO_ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "secrets.OPENAI_API_KEY" not in workflow
    assert "TMK_LIVE_OPENAI_KEY" not in workflow
    assert "vars.TMK_LIVE_ENDPOINT" in workflow


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
    from tm_knowledge.authored import corrections, store

    onto = files["ontology.json"]
    # What serves: a signed relationship replaced by a correction stops serving,
    # and the authored record carrying the corrected triple names it (ADR-0122).
    served, fixes = corrections.served_gold(), corrections.load()
    assert onto["counts"]["concepts"]["signed"] == len(served["gold_concept"])
    assert onto["counts"]["relations"]["signed"] == len(served["gold_relationship"])
    replaced = {r["replaces"] for r in onto["relations"] if r.get("replaces")}
    assert replaced == set(fixes.replacements())
    corrected = {c["id"] for c in onto["concepts"] if c.get("corrected")}
    assert corrected == {t for t in fixes.targets() if t.startswith("GC-")}
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
    systems = Systems(KeywordIndex(corpus), links, None, jobs.load_aliases(corpus, links.concepts),
                      relations_from(ctx.gold, ctx.authored))
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


@needs_snapshot
def test_the_live_reading_prompt_is_the_one_in_bulk_jobs(files):
    from tm_knowledge.bulk import jobs

    reading = files["chat.json"]["reading"]
    assert reading["instructions"] == jobs._READING_INSTRUCTIONS
    assert reading["schema"] == jobs._READING_SCHEMA
    assert reading["max_ideas"] == jobs.READING_MAX_IDEAS


@needs_snapshot
@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the browser engine")
def test_the_page_checks_the_models_reading_before_it_steers(files, tmp_path):
    """ADR-0132: an idea the model reads in a typed question starts the search only
    if it is on the map, specific enough to steer, and its words are in the question.
    Without one, the search is the measured one."""
    from tm_knowledge.bulk import jobs

    explorer.write(files, tmp_path)
    smell = "Can I trade mark a smell?"
    cases = [
        {"question": smell, "reply": {"concepts": [
            {"id": "GC-0078", "words": "“smell”", "why": "a scent"},
            {"id": "GC-9999", "words": "smell", "why": "not on the map"},
            {"id": "GC-0072", "words": "trade mark", "why": "named already, so not a pick"},
            {"id": "GC-0116", "words": "smell", "why": "too general"},
            {"id": "GC-0077", "words": "a jingle", "why": "not in the question"},
            {"id": "GC-0078", "words": "smell", "why": "a repeat"},
        ]}},
        {"question": "Can I protect a jingle?", "reply": {"concepts": [{"id": f"GC-00{n}", "words": "jingle", "why": ""}
                                                                    for n in (74, 75, 76, 77, 78)]}},
        {"question": "What is a divisional application?", "reply": {"concepts": [
            {"id": "GC-0043", "words": "divisional application", "why": "named already"}]}},
        {"question": smell, "reply": {"not": "the expected shape"}},
    ]
    (tmp_path / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
    result = subprocess.run(["node", str(REPO_ROOT / "tests" / "explorer_reading.mjs"), str(tmp_path),
                             str(tmp_path / "cases.json")], capture_output=True, text=True, check=True)
    browser = json.loads(result.stdout)
    smelt, jingle, named, garbled = browser

    # The same check and the same ranking in Python, where the reading is measured (ADR-0133).
    from tm_knowledge.bulk import links as links_module
    from tm_knowledge.search.index import KeywordIndex, Systems, relations_from
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    ctx = jobs.Context(corpus=corpus, links=links_module.link(corpus))
    systems = Systems(KeywordIndex(corpus), ctx.links, None, jobs.load_aliases(corpus, ctx.links.concepts),
                      relations_from(ctx.gold, ctx.authored))
    for case, js in zip(cases, browser):
        kept, dropped = systems.reading(case["question"], case["reply"], jobs.READING_MAX_IDEAS)
        assert [[k["id"], k["words"]] for k in kept] == js["kept"], case["question"]
        assert [[d["id"], d["reason"]] for d in dropped] == js["dropped"], case["question"]
        hits, trace = systems.ontology(case["question"], 10, [k["id"] for k in kept])
        assert [h.ref for h in hits] == js["ontology"] and trace.recognised == js["recognised"], case["question"]

    assert smelt["kept"] == [["GC-0078", "smell"]]
    assert [reason for _, reason in smelt["dropped"]] == [
        "it is not an idea on the map", "it is named too often to steer", "its words are not in the question"]
    assert smelt["recognised"] == ["GC-0072", "GC-0078"] and smelt["paths"] > 0
    assert smelt["passages"] != smelt["plain"], "the idea read in the question steers the search"
    assert smelt["input"] == jobs.reading_input(files["chat.json"]["ontology_map"], smell)

    assert len(jingle["kept"]) == jobs.READING_MAX_IDEAS
    assert jingle["dropped"] == [["GC-0078", f"only the first {jobs.READING_MAX_IDEAS} are used"]]
    assert named["kept"] == [] and named["dropped"] == [] and named["passages"] == named["plain"]
    assert garbled["kept"] == [] and garbled["passages"] == garbled["plain"]


@needs_snapshot
def test_every_answer_names_the_law_it_read(files):
    """ADR-0136 (CHAT-0077): "the Act as in force from …" on every answer. A live
    answer reads the pinned snapshot; the prepared ones, the snapshot they were
    written against, which the pin's next move does not change."""
    from tm_knowledge.upstream.loader import load_corpus

    law = files["chat.json"]["law"]
    assert [row["line"] for row in law] == [i.in_force_line for i in sorted(
        load_corpus().instruments.values(), key=lambda i: i.code)]
    assert law[0]["line"].startswith("the Act as in force from ")
    assert files["examples.json"]["law"][0]["line"] == "the Act as in force from 14 October 2024"
    ask = (SITE / "js" / "ask.js").read_text(encoding="utf-8")
    assert "Read against ${esc(lawLine(a.live ? chat.law : examples.law))}" in ask


def test_the_page_never_reads_an_empty_map_as_an_absence():
    """F19's matching words on the page where nothing is found (CHAT-0080)."""
    ask = (SITE / "js" / "ask.js").read_text(encoding="utf-8")
    assert ask.count("not a finding that none exist") == 2
    assert "Gathered no passages through the map's links" in ask
    assert "a requirement, exception or step they do not mention may still exist" in ask
