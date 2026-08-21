# How to correct the seed set

**Audience:** the Trade Mark examiners advising this project.
**Time needed:** an hour is useful. A day is a lot. You will not finish, and
that is expected.

---

## What you have been handed

368 example records over section 43, written by a machine. They look exactly
like the records the project actually needs — same fields, same shapes, same
rules — but the legal content in them is unverified, and some of it is wrong.

**They are not a proposal.** Nobody is asking you to approve them. They exist
because the last round of this work asked you to write these records from an
empty form, and that turned out to be the wrong request: the judgements the form
asks for are things you know and do not routinely put into words. Correcting a
wrong answer is a different job from composing a right one, and it is the job
this set is built for.

Where the machine is wrong, say so. Where it is wrong in a way that reads
plausibly, say so twice — that is the most valuable thing in the exercise,
because a plausible-looking wrong answer is exactly what an automated system
will produce later, and this is the only chance to write down what makes it
wrong.

## Two formats. Use whichever you prefer.

**The review pack** — `data/derived/seed-review-pack.md`. Every record laid out
in reading order, with the Manual passage it rests on quoted underneath and the
exact words in bold. Read it on screen or print it and write on it. Nothing in
it sends you back to the corpus to check something.

**The review workbook** — `data/derived/stage0-seed-review.xlsx`. The same
records as a spreadsheet, one sheet per record type, every value in a cell you
can type over. Three columns at the right-hand end are yours: `seed_id` (leave
it alone), `verdict`, and `correction`.

Marking up the pack and handing it back is completely fine. Somebody will
transcribe it. You do not have to open the spreadsheet.

## The three verdicts

For each record, one of:

- **correct** — the record says something true and useful, as written.
- **amend** — the point is right, the content is not. Say what is wrong. You do
  not have to write the corrected field; saying *"the near-miss here isn't
  'deceptively similar', it's X"* is the part only you can do.
- **reject** — the record should not exist. Either it is about something that
  is not really a thing, or it is the wrong shape for what it is trying to say.

**A rejection is as valuable as a correction.** It tells us the shape was
wrong, not just the wording, and that is a bigger fix. Do not soften a rejection
into an amendment to be helpful.

If you are not sure, leave it blank and move on. A blank is reported as
unreviewed, which is honest. A guess is not.

## Where to spend your time

In this order. Each of these is worth more than a page of individual record
corrections, because each one decides what hundreds of later records look like.

**1. The annotation rule at the top of `entities.seed.yaml`.** It says which
mentions get annotated and which do not — and it deliberately annotates one
chunk (`TMM/Part29/2/2/2`) under a stricter rule than the rest, so you can
compare the two densities and pick. That single choice sets the size and the
shape of the entire entity set.

**2. The candidate predicate list at the top of `relationships.seed.yaml`.**
Fourteen predicates invented by a machine. The input guide says explicitly that
an agent should *not* invent these and then have you fit relationships to them;
this file does it anyway, because a list you can argue with beats a blank page.
Argue with it. If two predicates are really one, or one is missing, say so on
any record that uses it.

**3. `not_labels` in `concepts.seed.yaml`.** The near-miss that shares most of
its words and means something materially different. Everything clusters the
obvious synonyms correctly; systems fail on these. A wrong `not_label` teaches
the system a distinction that does not exist. A missing one leaves a real
distinction untested.

**4. `modality` in `relationships.seed.yaml`.** Whether a "may" is possibility
or permission, and whether a "should" creates an obligation in practice. Every
one of these is a guess, and where the grammar and the reading come apart is
where an extraction system will confidently produce a wrong assertion in a
well-formed shape.

**5. `qualifications_expected` in `retrieval-questions.seed.yaml`.** The things
whose *absence* makes an answer wrong even though every sentence in it is true.
A qualification we have missed is a hole in the test, not a small error.

**6. The relevance grades in `search-questions.seed.yaml`.** Fast to correct,
and they move the numbers directly.

## Things worth knowing before you start

**Do not correct a `span`, a `source_content_hash`, or a ref.** They are
computed from the corpus. If you change the words of a `surface` or a
`supporting_text`, the offsets recompute themselves. You should never have to
type an offset or a hash, and if you find yourself doing so, something is wrong
with the tooling rather than with you.

**Copy, do not retype, when you supply a passage.** The Manual's text contains
typographic quotation marks, en dashes, a term broken across a line as
"International Non- Proprietary Name", and at least one sentence with a word
missing. Those are in the source and the records reproduce them exactly. A
tidied-up version will not match the corpus and the record will fail.

**Some things the corpus genuinely cannot do**, and a record that pretends
otherwise should be rejected:

- *No decision text exists anywhere in this programme.* Only citations. "Which
  cases interpret this test" is answerable; "what did the court hold" is not.
- *The snapshot holds current text only.* "What did the Manual say two years
  ago" cannot be answered from it.
- *Only two instruments are held* — the Trade Marks Act 1995 and the Trade Mark
  Regulations 1995. The Manual's citation to section 114 of the Trade Marks Act
  1905 resolves to nothing at all.

**Confidence figures are the machine's, not a measurement.** A record marked
0.45 is one the machine was unsure about. Those are worth reading first; they
are not more likely to be wrong than the ones marked 0.9, but they are more
likely to be wrong about something that matters.

## Two questions you can answer without reading a single record

Both are in the same directory, both are pure judgement, and both unblock more
work than any number of record corrections:

**`pilot-scope.seed.md`** — a draft of the section 43 boundary, including an
exclusion list. The exclusion list is what stops the pilot growing quietly.
Nobody but you can write it.

**`measures.seed.md`** — draft thresholds. What score is good enough to ship,
and what score means stop. Those numbers encode risk appetite, not statistics.

## When you are done, or done for now

Hand back whatever you have. Partial is fine and expected — a hundred reviewed
records is a hundred more than exist today, and the coverage report will say
exactly which hundred.

What happens next: an agent transcribes your corrections, the harness checks
every ref and every offset, and the records that carry your name become the gold
set. Then a second, much larger set gets generated in the same shapes, and your
next pass is validation rather than correction — which is the same job again,
only cheaper.
