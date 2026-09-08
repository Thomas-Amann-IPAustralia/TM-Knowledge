"""The RULE-0001 review pack says the same number twice, and both are true.

The pack exists because the owner asked to see the passages RULE-0001 flags
before ruling on it, and it opens by correcting the number he was given: 71 was
the count of *triples* the rule writes, quoted at him as a count of flagged
passages (Q-44).

So the one property worth testing is that the pack cannot repeat the mistake it
was written to correct. Every count it prints is derived from the same run that
produces the sections, and these tests check the printed number against the
sections actually rendered — not against a constant, which is what "71" was.
"""

from __future__ import annotations

import re

import pytest

from tm_knowledge.ontology import flags, rules
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import TMK
from tm_knowledge.upstream.loader import load_corpus

pytestmark = [pytest.mark.snapshot, pytest.mark.rdf]


def test_the_stated_count_is_the_number_of_passages_shown():
    text = flags.render(generated="2026-01-01")
    stated = int(re.search(r"\*\*The rule flags (\d+) passages", text).group(1))
    sections = re.findall(r"^### \d+\. `", text, re.MULTILINE)
    assert stated == len(sections) == len(flags.flagged_refs())


def test_every_flagged_passage_is_in_the_snapshot():
    """A flag on a passage the corpus does not hold is a defect, and the pack
    would print a placeholder rather than evidence."""
    corpus = load_corpus()
    for ref in flags.flagged_refs():
        assert ref in corpus.chunks, f"{ref} is flagged and not in the pinned snapshot"


def test_the_pack_shows_both_halves_of_every_flag():
    """The rule fires on a legislation mention *and* a practice mention in one
    passage. A pack showing only one of them would not let anyone check it."""
    text = flags.render(generated="2026-01-01")
    for section in text.split("### ")[1:]:
        assert "quoted legislation" in section
        assert "the Registrar's practice" in section


def test_conclusions_and_triples_are_counted_separately():
    """The fix underneath the pack. `Yield` carries both, and for these rules
    they differ by more than an order of magnitude — which is exactly why one
    could stand in for the other unnoticed."""
    dataset, _ = build()
    _dataset, counts = rules.apply_rules(dataset)
    for rule in rules.load_rules():
        got = counts[rule.rule_id]
        produced = rule.construct(dataset)
        assert got.triples == len(produced)
        assert got.assertions == len(set(produced.subjects(TMK.producedByRule, None)))
        assert got.assertions < got.triples, (
            "if these were ever equal the distinction would be invisible, and the "
            "confusion this guards against would be back"
        )
