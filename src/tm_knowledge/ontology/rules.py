"""Run the approved CONSTRUCT rules into the inferred named graph.

Stage 9's rule: a person approves every reasoning template before deployment.
This module enforces the consequence rather than trusting the query text —
**the `approved-by` header is the only thing that decides an output's review
status**, and `construct()` stamps it on. A rule body that set its own
`reviewStatus` would be a query asserting its own approval, and the two could
drift silently: a rule marked approved in the header while still emitting
`candidate`, or the far worse opposite. So the bodies do not set it, and
`_stamp` refuses a body that tries.

Approved or not, output goes into `graph/inferred.ttl` and never into the
approved graph. Approval changes what an inference may be relied on for; it does
not turn a derivation into a signed record.

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

from rdflib import Dataset, Graph, Literal

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import INFERRED_GRAPH, TMK, bind_all

__all__ = ["RULES_DIR", "Rule", "Yield", "MalformedRule", "load_rules", "apply_rules"]

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
        """Run the rule and stamp every inference with the header's verdict."""
        result = dataset.query(self.text)
        graph = bind_all(Graph())
        for triple in result.graph or ():
            graph.add(triple)
        return self._stamp(graph)

    def _stamp(self, graph: Graph) -> Graph:
        """Write the review status onto every inference the rule produced.

        Taken from `approved-by:` and from nowhere else. A body that sets either
        predicate itself is refused rather than overwritten: silently replacing
        it would hide a rule trying to declare its own approval, which is the
        one thing this stamp exists to make impossible.
        """
        for predicate in (TMK.reviewStatus, TMK.requiresHumanReview):
            claimed = {
                subject
                for subject in graph.subjects(TMK.producedByRule, None)
                if (subject, predicate, None) in graph
            }
            if claimed:
                raise MalformedRule(
                    f"{self.path.name}: the query body sets {predicate.split('/')[-1]} "
                    f"on its own output. A rule does not decide whether it is approved — "
                    f"`approved-by:` in the header does, and this module stamps it on. "
                    f"Remove the line from the CONSTRUCT template."
                )
        approved = self.is_approved
        for subject in set(graph.subjects(TMK.producedByRule, None)):
            graph.add((subject, TMK.reviewStatus, Literal("approved" if approved else "candidate")))
            graph.add((subject, TMK.requiresHumanReview, Literal(not approved)))
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


@dataclass(frozen=True)
class Yield:
    """What a rule produced, counted two ways, because they are not the same
    number and confusing them misled the owner.

    `triples` is the size of the graph the rule built. `assertions` is how many
    things it actually concluded — one `InferredAssertion` per derived fact. A
    single conclusion carries eight or so triples of provenance with it, so the
    two differ by more than an order of magnitude: RULE-0001 concludes 5 things
    in 71 triples, RULE-0002 concludes 187 in 2,244.

    S011 read the triple count off the report and wrote it into the owner's
    question as "It produced 71 flags", so he was asked to review 71 passages
    that do not exist, and approved a rule believing it drew 2,244 links when it
    draws 187 (Q-44, ADR-0069). Both numbers stay available; neither is named in
    a way that lets it stand in for the other.
    """

    triples: int
    assertions: int


def apply_rules(
    dataset: Dataset | None = None, rules: tuple[Rule, ...] | None = None
) -> tuple[Dataset, dict[str, Yield]]:
    """Run every rule, writing results into the inferred graph.

    Rules do not see each other's output: each runs against the dataset as it
    was, not as the previous rule left it. Chaining would make the result depend
    on file order, and a derivation that only holds because another rule ran
    first is one whose explanation is incomplete.

    An approved rule and a pending one both land here. What separates them is the
    `reviewStatus` on every triple, stamped from the header by `construct()`.
    """
    if dataset is None:
        dataset, _ = build()
    rules = rules if rules is not None else load_rules()

    inferred = dataset.graph(INFERRED_GRAPH)
    counts: dict[str, Yield] = {}
    for rule in rules:
        produced = rule.construct(dataset)
        counts[rule.rule_id] = Yield(
            triples=len(produced),
            assertions=len(set(produced.subjects(TMK.producedByRule, None))),
        )
        for triple in produced:
            inferred.add(triple)
    return dataset, counts
