# queries/rules/ — approved CONSTRUCT rules

**Neither rule here is approved.** Both say `approved-by: PENDING`, and
`tm_knowledge.ontology.rules` enforces the consequence rather than trusting the
line: everything a rule produces is written with `tmk:reviewStatus "candidate"`
and `tmk:requiresHumanReview true`, into `graph/inferred.ttl` and nowhere else.

Stage 9's requirement is that experts approve every reasoning template before
deployment. These are drafted so there is something to approve.

## The header is required

```
# rule:           RULE-0001
# derives:        what it produces
# basis:          the approved record or question it stands on
# approved-by:    a name and a date, or PENDING
# fires-test:     the test proving it fires
# near-miss-test: the test proving it does NOT fire on the near case
# limits:         what it does not establish
```

A file missing any of these is refused rather than run. The two test lines are
the reason the header is checked rather than documented, and
`test_every_rule_names_tests_that_exist` asserts the names resolve — a renamed
test cannot leave a rule pointing at nothing.

**Both tests, always.** A rule that fires on everything passes a fires-test. The
near-miss is what shows it is selective: RULE-0001's is a Manual chunk with
practice mentions and no quoted provision, which is what most of the corpus
looks like.

## Rules do not chain

Each runs against the dataset as it was, not as the previous rule left it.
Chaining would make the result depend on file order, and a derivation that holds
only because another rule ran first is one whose explanation is incomplete.

## What must not go here

A rule that derives an evaluative conclusion. "The evidence establishes acquired
distinctiveness" stays outside automated reasoning scope — a class holding such
propositions is fine, a rule deriving one is not, and
`shapes/inference.ttl`'s `tmk:BoundedReasoningShape` fails the graph if one
appears.
