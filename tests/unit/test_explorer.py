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
    assert set(files) == {"build.json", "ontology.json", "search.json", "passages.json", "stability.json",
                          "tour.json", "examples.json", "chat.json", "live.json", "explain.json"}


@needs_snapshot
def test_the_release_manifest_says_what_was_built(files):
    """A11: one file a downstream consumer reads first, naming the pin, the compilations,
    the Manual's capture, the schemas, the profile and the review states, apart."""
    release = files["build.json"]
    assert release["graph"]["manifest"] == "tmk-release/1"
    assert release["graph"]["upstream"]["commit"].startswith(files["ontology.json"]["build"]["upstream"])
    assert {row["label"] for row in release["graph"]["law"]} == {"Trade Marks Act 1995", "Trade Marks Regulations 1995"}
    assert set(release["graph"]["graphs"]["approved"]["review_status"]) == {"approved"}
    assert set(release["graph"]["graphs"]["authored"]["review_status"]) == {"unreviewed"}
    assert release["manual"]["captured"] == "2026-08-03"
    assert release["answers"] == {"live": "answer-v4", "prepared": "answer-v4"}


@needs_snapshot
def test_the_change_view_reads_every_store_and_starts_from_a_provision(files):
    """R05: definitions and corrections rest on pages too, and a provision has a view."""
    stability = files["stability.json"]
    assert any(page["definitions"] for page in stability["pages"])
    assert any(page["corrections"] for page in stability["pages"])
    s44 = stability["provisions"]["TMA1995/s44"]
    assert s44["direct"] and s44["via_manual"] and set(s44["ambiguous"]) <= set(s44["passages"])
    assert "TMA1995/s44" in stability["held"]


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
def test_every_kind_of_link_a_record_states_reaches_a_page(files):
    """A concept record's own `broader` / `narrower` fields are in the graph as
    `skos:broader`, but no relationship record carries them; until S039 the views
    drew only relationships, and four signed kind-of links were on no page. Each is
    now a connection or on the card at both ends, naming the record that states it."""
    onto = files["ontology.json"]
    by_id = {c["id"]: c for c in onto["concepts"]}
    drawn = {(r["s"], r["o"]) for r in onto["relations"] if r["p"] == "broader"}
    stated = {(c["id"], o) for c in onto["concepts"] for o in c["broader"]}
    stated |= {(o, c["id"]) for c in onto["concepts"] for o in c["narrower"]}
    assert stated, "no concept record states a hierarchy any more; this test has nothing to hold"
    for narrow, broad in stated - drawn:
        up = (by_id[narrow].get("hierarchy") or {}).get("kind_of", [])
        down = (by_id[broad].get("hierarchy") or {}).get("kinds", [])
        assert any(i["id"] == broad for i in up), (narrow, broad)
        assert any(i["id"] == narrow for i in down), (narrow, broad)
        for item in up + down:
            origins = {by_id[r]["origin"] for r in item["records"]}
            assert item["origin"] == ("signed" if origins == {"signed"} else "machine"), item


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
    from tm_knowledge.search.index import KeywordIndex, ProvisionIndex, Systems, relations_from
    from tm_knowledge.search import structured
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
    provision_index = ProvisionIndex(corpus)
    for q in questions:
        js = browser[q["key"]]
        assert js["keyword"] == [h.ref for h in systems.keyword(q["question"], 10)], q["key"]
        assert js["provisions"] == [h.ref for h in provision_index.search(q["question"], 5)], q["key"]
        hits, trace = systems.ontology(q["question"], 10)
        assert js["tests"] == structured.find(q["question"], trace.recognised, files["search.json"]["tests"]), q["key"]
        assert js["ontology"] == [h.ref for h in hits], q["key"]
        assert js["recognised"] == trace.recognised and js["paths"] == [p[3] for p in trace.paths], q["key"]
        if q["prompt"]:
            hits8, trace8 = systems.ontology(q["question"], 8)
            passages = [h.ref for h in hits8]
            legislation = jobs.legislation_refs(corpus, q["question"], trace8.provisions, passages)
            assert js["legislation"] == legislation, q["key"]
            item = jobs.Item(q["key"], {"question": q["question"], "recognised": trace8.recognised,
                                        "paths": [list(p) for p in trace8.paths][:12],
                                        "passages": passages, "legislation": legislation})
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
    assert files["examples.json"]["law"][0]["line"] == "the Act as in force from 19 September 2026"
    ask = (SITE / "js" / "ask.js").read_text(encoding="utf-8")
    assert "lawLine(a.live ? chat.law : examples.law, a.live ? chat.manual : examples.manual)" in ask
    # R10: the Manual's capture date beside them, and the live one says it predates compilation 48.
    assert files["chat.json"]["manual"]["line"] == "the Manual as captured on 3 August 2026"
    assert "may not reflect" in files["chat.json"]["manual"]["note"]
    # The prepared answers read compilation 48 too since ADR-0143, so theirs says the same.
    assert "may not reflect" in files["examples.json"]["manual"]["note"]


def test_the_page_never_reads_an_empty_map_as_an_absence():
    """F19's matching words on the page where nothing is found (CHAT-0080)."""
    ask = (SITE / "js" / "ask.js").read_text(encoding="utf-8")
    assert ask.count("not a finding that none exist") == 2
    assert "Gathered no passages through the map's links" in ask
    assert "a requirement, exception or step they do not mention may still exist" in ask


@needs_snapshot
def test_a_concept_card_carries_its_definition_stamped_with_its_source(files):
    """ADR-0137: shown as machine-written and unreviewed, and saying where its words
    come from, so the Act's definition and the Manual's practice never blur."""
    from tm_knowledge.authored import definitions

    defined = [c for c in files["ontology.json"]["concepts"] if c.get("definition")]
    assert len(defined) == len(definitions.load().sound)
    for concept in defined:
        d = concept["definition"]
        assert d["review_status"] == "unreviewed" and d["text"] and d["ref"], concept["id"]
        assert d["basis"] in ("statutory_definition", "statutory_provision", "manual")
    app_js = (SITE / "js" / "app.js").read_text(encoding="utf-8")
    assert "export function definitionBlock" in app_js and "which states practice, not law" in app_js
    # Both cards that show an idea's own fields: the map's and the table's (S039).
    for card in ("map.js", "table.js"):
        assert "definitionBlock(x.definition)" in (SITE / "js" / card).read_text(encoding="utf-8"), card


@needs_snapshot
def test_the_structured_tests_and_processes_reach_the_page(files):
    """Package 4's record types (ADR-0142): every sound legal test and process template is
    in the page's data with its stamp, listed on the card of every idea it names, and
    counted among what rests on the pages and provisions it quotes."""
    from tm_knowledge.authored import procedure

    onto = files["ontology.json"]
    structures = onto["structures"]
    assert [r["id"] for r in structures["tests"]] == [e.id for e in procedure.load_tests().sound]
    assert [r["id"] for r in structures["processes"]] == [e.id for e in procedure.load_processes().sound]
    assert onto["counts"]["tests"] == len(structures["tests"]) > 0
    assert onto["counts"]["processes"] == len(structures["processes"]) > 0
    by_id = {c["id"]: c for c in onto["concepts"]}
    for record in structures["tests"] + structures["processes"]:
        assert record["origin"] == "machine" and record["machine"]["review_status"] == "unreviewed", record["id"]
        assert record["machine"]["by"] and record["machine"]["date"], record["id"]
        assert record["concepts"], record["id"]
        for cid in record["concepts"]:
            assert record["id"] in by_id[cid].get("structures", []), (record["id"], cid)
    stability = files["stability.json"]
    assert any(page["structures"] for page in stability["pages"])
    assert {"GL-0001", "GP-0001"} <= set(stability["provisions"]["TMA1995/s44"]["direct"])
    table_js = (SITE / "js" / "table.js").read_text(encoding="utf-8")
    assert '["tests", "Legal tests"]' in table_js and '["processes", "Processes"]' in table_js
    for card in ("map.js", "table.js"):
        assert "structuresBlock(x, ontology)" in (SITE / "js" / card).read_text(encoding="utf-8"), card


@needs_snapshot
def test_the_page_states_the_merge_rulings_as_they_stand(files):
    """The About page once said twelve same-idea pairs were "flagged for a person, not
    merged" after the owner had ruled on all twelve; it now reads the rulings' file."""
    from tm_knowledge.ontology import hygiene

    merges = files["ontology.json"]["counts"]["merges"]
    assert sum(merges.values()) == len(hygiene.merge_candidates())
    about = (SITE / "js" / "about.js").read_text(encoding="utf-8")
    assert "flagged for a person, not merged" not in about and "c.merges" in about


def test_every_view_sits_in_one_layer_and_every_term_is_explained():
    """ADR-0145: outcomes first and the ontology last. Every route the router knows is in one of
    the four layers or is the cross-cutting status page, and every `term()` a page uses has a
    glossary entry, so no standard's name reaches a reader unexplained."""
    js = SITE / "js"
    app = (js / "app.js").read_text(encoding="utf-8")
    views = re.search(r"const VIEWS = \{(.*?)\};", app, re.S).group(1)
    routes = {item.split(":")[0].strip().strip('"') for item in views.split(",")}
    layers = (js / "layers.js").read_text(encoding="utf-8")
    placed = set()
    for group in re.findall(r"routes: \[([^\]]*)\]", layers):
        placed |= set(re.findall(r'"([^"]*)"', group))
    assert routes <= placed, f"routes in no layer: {routes - placed}"
    glossary = (js / "glossary.js").read_text(encoding="utf-8")
    entries = set(re.findall(r'^  "?([\w-]+)"?: \{$', glossary, re.M))
    used = {key for path in js.glob("*.js") for key in re.findall(r'term\("([\w-]+)"', path.read_text(encoding="utf-8"))}
    assert used and used <= entries, f"terms with no entry: {used - entries}"
    for key in ("rdf", "skos", "shacl", "sparql", "owl", "prov-o", "named-graph"):
        assert key in entries, key


@needs_snapshot
def test_the_customer_preview_is_the_engines_own_explanation(files):
    """ADR-0145: the site's customer preview draws the very objects `tmk-explain` builds, with
    their text equivalents, so the page and the prototype cannot say different things. Every
    matter is invented, every view carries its stamp, and the page says loudly what it is not."""
    from tm_knowledge.authored import procedure
    from tm_knowledge.explain import engine, matters

    data = files["explain.json"]
    assert data["fictional"] is True and data["left_out"] == []
    assert [m["matter"] for m in data["matters"]] == [m.id for m in matters.load()]
    tests = {k: v.record for k, v in procedure.load_tests().by_id().items()}
    processes = {k: v.record for k, v in procedure.load_processes().by_id().items()}
    first = matters.load()[0]
    assert data["matters"][0]["text"] == engine.render_text(engine.explain(first, tests, processes[engine.EXAMINATION_PROCESS]))
    assert [r["test"] for r in data["requirements"]] == sorted(tests)
    assert data["walkthroughs"][0]["process"] != engine.EXAMINATION_PROCESS
    for m in data["matters"]:
        assert m["fictional"] is True and m["stamp"] == engine.STAMP and m["text"]
    for view in data["requirements"] + data["walkthroughs"]:
        assert view["stamp"] == engine.GENERAL_STAMP and view["text"]
    page = (SITE / "js" / "customers.js").read_text(encoding="utf-8")
    for words in ("Invented matters only. Not tested with customers. Not advice.",
                  "never says how an application will be decided", "the project owner's decision"):
        assert words in page, words
    assert 'load("explain")' in page and "textEq(" in page


@needs_snapshot
def test_every_clause_a_structured_record_quotes_opens_in_the_drawer(files):
    """A chip on a legal test, a process step or an explanation opens its clause; none reads as
    "not in the snapshot"."""
    passages = files["passages.json"]
    chunks = {row[0] for row in passages["chunks"]}
    named = explorer._refs(files["ontology.json"]["structures"]) | explorer._refs(files["explain.json"])
    missing = {r for r in named if r not in passages["legislation"] and r not in chunks}
    assert not missing, sorted(missing)


@needs_snapshot
def test_the_standards_page_reads_its_examples_and_checks_from_the_build(files):
    """The standards page explains each standard with a real block of the committed graph and the
    checks counted from `shapes/` and `queries/rules/`, never typed in; a sample never names a
    reviewer, whom the site never singles out (ADR-0130)."""
    release = files["build.json"]
    checks = release["checks"]
    assert sum(checks["shapes"].values()) > 0 and set(checks["shapes"]) == {p.stem for p in (REPO_ROOT / "shapes").glob("*.ttl")}
    assert {r["id"]: r["approved"] for r in checks["rules"]} == {"RULE-0001": False, "RULE-0002": True}
    for key, sample in release["samples"].items():
        assert sample["lines"] and sample["lines"][0].startswith(sample["subject"]), key
        assert not any("approvedBy" in line for line in sample["lines"]), key
    page = (SITE / "js" / "standards.js").read_text(encoding="utf-8")
    assert "build.samples" in page and "build.checks" in page and "g.profile" in page
    for typed in ("102,082", "42 ", "29,873"):
        assert typed not in page, typed


def test_the_first_page_leads_with_outcomes_read_from_the_data():
    """The home page states the measurement in both directions and the prototype's untested state,
    with every figure read from the data, never typed in."""
    home = (SITE / "js" / "home.js").read_text(encoding="utf-8")
    assert 'all["ndcg:ontology-hybrid"]' in home and 'all["ndcg:ontology-keyword"]' in home
    assert "not tested with customers" in home and "Never" in home
    for typed in ("129", "810", "729", "164", "357"):
        assert typed not in home, typed
    future = (SITE / "js" / "future.js").read_text(encoding="utf-8")
    assert 'id="customers"' in future and "nothing has been shown to a customer" in future
    assert "until the project owner approves it" in future


# --- answer-v4: what the answer is given of each source (A06, ADR-0139) -------------


@needs_snapshot
@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the browser engine")
def test_the_browser_cuts_every_long_source_exactly_as_python_does(files, tmp_path):
    """Every provision past the law budget and every Manual chunk past the Manual one,
    each with a question that matches somewhere in it and one that matches nothing."""
    from tm_knowledge.bulk import jobs
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    explorer.write(files, tmp_path)
    long_law = [r for r, p in corpus.provisions.items() if len(p.text or "") > jobs.LAW_CHARS]
    long_manual = [r for r, c in corpus.chunks.items() if len(c.text) > jobs.MANUAL_CHARS]
    assert long_law and long_manual
    cases = [[ref, q] for ref in long_law + long_manual
             for q in ("What does it say about opposition, registration and a certification trade mark?", "zzz")]
    (tmp_path / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
    result = subprocess.run(["node", str(REPO_ROOT / "tests" / "explorer_excerpt.mjs"), str(tmp_path),
                             str(tmp_path / "cases.json")], capture_output=True, text=True, check=True)
    for (ref, question), js in zip(cases, json.loads(result.stdout)):
        text = jobs.passage_at(corpus, ref).text
        py = jobs.excerpt(ref, text, jobs.provision_units(corpus, ref), question)
        assert (js["text"], js["cut"]) == (py.text, py.cut), (ref, question)


@needs_snapshot
def test_a_section_44_answer_sees_its_exceptions():
    """The regression A06 found: the 1,600 cut removed subsections (3) and (4), the
    exceptions subsection (1) is 'Subject to'. Now s 44 is given whole."""
    from tm_knowledge.bulk import cli, jobs

    ctx = cli._context()
    payload = {"question": "When does honest concurrent use overcome a section 44 ground?", "recognised": [],
               "paths": [], "passages": [], "legislation": ["TMA1995/s44"]}
    prompt = jobs._answer_render(ctx, jobs.Item("s44", payload))
    text = ctx.corpus.provisions["TMA1995/s44"].text
    assert text[text.index("(3)"):text.index("(3)") + 60] in prompt
    assert text[text.index("(4)"):text.index("(4)") + 60] in prompt
    assert 'ref="TMA1995/s44" cut=' not in prompt


def test_a_long_provision_gives_the_matched_parts_and_what_their_lead_in_names():
    """A provision past the budget: the block the question matches, plus the blocks its
    'Subject to subsections ...' lead-in names, whatever the budget; the cut is marked."""
    from tm_knowledge.bulk import jobs

    filler = " ".join(["word"] * 900)
    units = [("TMA1995/s99(1)", "(1) Subject to subsections (3) and (4), an opposition must be filed."),
             ("TMA1995/s99(1)(a)", "(a) on time;"),
             ("TMA1995/s99(2)", "(2) " + filler),
             ("TMA1995/s99(3)", "(3) The first exception."),
             ("TMA1995/s99(4)", "(4) The second exception."),
             ("TMA1995/s99(5)", "(5) " + filler)]
    text = " ".join(u for _, u in units)
    shown = jobs.excerpt("TMA1995/s99", text, units, "When must an opposition be filed?")
    assert "(3) The first exception." in shown.text and "(4) The second exception." in shown.text
    assert "on time" in shown.text, "a block keeps its paragraphs"
    assert shown.cut.startswith("parts shown: (1)") and "omitted: " in shown.cut and "…" in shown.text


def test_a_long_manual_chunk_is_cut_around_the_questions_words():
    from tm_knowledge.bulk import jobs

    text = "x " * 2000 + "honest concurrent use is here " + "y " * 2000
    shown = jobs.excerpt("TMM/Part28/1#1", text, None, "honest concurrent use")
    assert "honest concurrent use is here" in shown.text
    assert shown.text.startswith("…") and shown.text.endswith("…") and shown.cut.startswith("characters ")
    assert jobs.excerpt("TMM/Part28/1#1", "short", None, "anything") == jobs.Excerpt("short")


def test_a_claim_is_supported_only_by_a_quote_from_what_was_sent():
    """A08: the check runs against the excerpt the model was given, so a quote from a
    part that was cut is dropped, and a claim left with none is unsupported."""
    from tm_knowledge.bulk import jobs

    sent = {"TMA1995/s99": jobs.Excerpt("(1) An opposition must be filed on time. …", "parts shown: (1); omitted: (2)")}
    claims = jobs.check_claims([
        {"text": "It must be filed on time.", "authority": "legislation",
         "quotes": [{"ref": "TMA1995/s99", "quote": "An opposition must be filed on time."}]},
        {"text": "The cut part says more.", "authority": "legislation",
         "quotes": [{"ref": "TMA1995/s99", "quote": "words only in the omitted part"},
                    {"ref": "TMM/Part1/1#1", "quote": "a passage that was never sent"}]},
        {"text": "No quote at all.", "authority": "bogus", "quotes": []},
    ], sent)
    assert [c["supported"] for c in claims] == [True, False, False]
    assert len(claims[1]["dropped"]) == 2 and claims[2]["authority"] == "none"


@needs_snapshot
def test_the_prompt_gives_the_recognised_concepts_definitions_with_basis_and_stamp():
    from tm_knowledge.bulk import cli, jobs

    ctx = cli._context()
    payload = {"question": "What is a connotation?", "recognised": ["GC-0001"], "paths": [], "passages": [],
               "legislation": []}
    prompt = jobs._answer_render(ctx, jobs.Item("d", payload))
    line = jobs.definition_lines(ctx)["GC-0001"]
    assert line in prompt and "GD-0001" in line and "machine-written, unreviewed" in line
    assert "written from the Manual, which states practice, not law" in line
    assert "statutory_definition" not in prompt


@needs_snapshot
def test_the_bulk_answer_job_records_claims_and_drops_quotes_from_outside_what_was_sent():
    from tm_knowledge.bulk import cli, jobs

    ctx = cli._context()
    payload = {"question": "When does honest concurrent use overcome a section 44 ground?", "recognised": [],
               "paths": [], "passages": [], "legislation": ["TMA1995/s44"]}
    s44 = ctx.corpus.provisions["TMA1995/s44"].text
    parsed = {"claims": [
        {"text": "Section 44 is subject to its exceptions.", "authority": "legislation",
         "quotes": [{"ref": "TMA1995/s44", "quote": s44[5:60]}]},
        {"text": "Unsupported.", "authority": "legislation",
         "quotes": [{"ref": "TMA1995/s6", "quote": "a provision that was not sent to the model"}]},
    ], "concepts_used": [], "declined": False, "decline_reason": ""}
    outcome = jobs._answer_accept(ctx, jobs.Item("k", payload), parsed, {"model_reported": "m"})
    row = outcome.records["answers"][0]
    assert [c["supported"] for c in row["claims"]] == [True, False] and row["prompt_version"] == "answer-v4"
    assert row["answer"].startswith("Section 44 is subject") and len(row["citations"]) == 1
    assert any("not in what was sent" in r for r in outcome.refused)
