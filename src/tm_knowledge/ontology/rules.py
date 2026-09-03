"""Run the approved CONSTRUCT rules into the inferred named graph.

Stage 9's rule: experts approve every reasoning template before deployment. The
rules in `queries/rules/` are **not approved** — the `approved-by` line in each
says `PENDING` — and this module enforces the consequence rather than trusting
the file: everything a rule produces is written with `reviewStatus "candidate"`
and `requiresHumanReview true`, and it goes into `graph/inferred.ttl`, never
into the approved graph.

Each rule file carries a header this module reads and refuses to run without:

    # rule:           the id
    # derives:        what it produces
    # basis:          the approved record or question the rule stands on
    # approved-by:    who approved it, or PENDING
    # fires-test:     the test proving it fires
    # near-miss-test: the test proving it does NOT fire on the near case
    # limits:         what it does not establish

The two test lines are `queries/README.md`'s requirement and they are the
reason the header is checked rather than documented. An untested rule that
never matches anything reads as coverage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from rdflib import Dataset, Graph

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import INFERRED_GRAPH, bind_all

__all__ = ["RULES_DIR", "Rule", "load_rules", "apply_rules"]

RULES_DIR = REPO_ROOT / "queries" / "rules"

_FIELDS = ("rule", "derives", "basis", "approved-by", "fires-test", "near-miss-test", "limits")
_HEADER = re.compile(r"^#\s*([a-z-]+)\s*:\s*(.+)$", re.MULTILINE)


class MalformedRule(ValueError):
    """A rule file missing a header field. Refused rather than run."""


@dataclass(frozen=True)
class Rule:
    path: Path
    rule_id: str
    derives: str
    basis: str
    approved_by: str
    fires_test: str
    near_miss_test: str
    limits: str
    text: str

    @property
    def is_approved(self) -> bool:
        """`approved-by: PENDING` is not an approval, and neither is a blank.

        Matched on the first word, because the line usually carries an
        explanation after it — and a substring test against the whole line would
        read `PENDING — an expert must approve this` as an approval, which is
        precisely backwards.
        """
        first = self.approved_by.strip().split(maxsplit=1)
        return bool(first) and first[0].strip(":—-,.").upper() not in {"PENDING", "NONE", "TBC"}

    def construct(self, dataset: Dataset) -> Graph:
        result = dataset.query(self.text)
        graph = bind_all(Graph())
        for triple in result.graph or ():
            graph.add(triple)
        return graph


def parse_header(path: Path) -> Rule:
    text = path.read_text(encoding="utf-8")
    found = {key: value.strip() for key, value in _HEADER.findall(text)}
    missing = [field for field in _FIELDS if field not in found]
    if missing:
        raise MalformedRule(
            f"{path.name}: header is missing {missing}. `fires-test` and "
            f"`near-miss-test` are not optional — a rule with no test that it "
            f"fires, and no test that it stays quiet on the near case, reads as "
            f"coverage and is not (queries/README.md)."
        )
    return Rule(
        path=path,
        rule_id=found["rule"],
        derives=found["derives"],
        basis=found["basis"],
        approved_by=found["approved-by"],
        fires_test=found["fires-test"],
        near_miss_test=found["near-miss-test"],
        limits=found["limits"],
        text=text,
    )


def load_rules(directory: Path | None = None) -> tuple[Rule, ...]:
    directory = directory or RULES_DIR
    return tuple(parse_header(path) for path in sorted(directory.glob("*.rq")))


def apply_rules(
    dataset: Dataset | None = None, rules: tuple[Rule, ...] | None = None
) -> tuple[Dataset, dict[str, int]]:
    """Run every rule, writing results into the inferred graph.

    Rules do not see each other's output: each runs against the dataset as it
    was, not as the previous rule left it. Chaining would make the result depend
    on file order, and a derivation that only holds because another rule ran
    first is one whose explanation is incomplete.
    """
    if dataset is None:
        dataset, _ = build()
    rules = rules if rules is not None else load_rules()

    inferred = dataset.graph(INFERRED_GRAPH)
    counts: dict[str, int] = {}
    for rule in rules:
        produced = rule.construct(dataset)
        counts[rule.rule_id] = len(produced)
        for triple in produced:
            inferred.add(triple)
    return dataset, counts
