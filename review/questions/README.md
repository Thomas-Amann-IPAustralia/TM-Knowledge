# review/questions/ — what is waiting on a person

One file: `open-questions.yaml`. It is the queue the dashboard renders as the
decision form, and it is the only place a session should put something it needs
the owner to settle.

`schema.json` validates it, and `tmk-dashboard` refuses to build if it does not
pass. `tests/unit/test_dashboard.py` runs the same check.

## Writing an entry

The schema enforces what a machine can check. The rest is the actual work:

- **Assume the reader has not read the repository and does not want to.** They
  are a product owner, not a knowledge engineer. If a sentence needs a file path
  to make sense, rewrite the sentence.
- **No acronym survives unexplained.** Not SHACL, not OWL, not TBox, not ADR.
  Say what the thing does.
- **`plain` says what is going on.** Two to five sentences. What exists, what is
  missing, what the choice actually is.
- **`why_you` says why nobody else can settle it.** If an agent could have
  decided it from evidence in the repo, it should have — and recorded a
  `derived` ADR instead of asking.
- **`if_unanswered` says what stays stuck.** Honestly. "Nothing is blocked" is a
  perfectly good answer and appears several times; a queue where everything
  claims to be urgent is a queue nobody triages.
- **Options are answers, not opinions.** Every realistic option belongs on the
  list, including *leave it alone*, *I have no view*, and *show me an example
  first*. An option list that steers towards one answer is an agent deciding.
- **`notes_prompt` is where the real answer usually is.** Ask for the thing that
  would change your mind.

`status` and `needs` together decide what happens:

| | |
|---|---|
| `status: open`, `needs: owner` | reaches the form with a control under it |
| `status: parked` | shown as context, read-only — usually expert content |
| `needs: expert` / `organisation` | never gets a control, whatever its status |
| `status: answered` | a session has acted on a ruling and closed it out |

**Do not delete a question when it is answered.** Set `status: answered`, act on
it, and leave it. The ruling file in `review/rulings/` and the question it
answers should still be readable side by side a year later.

## What must not go in here

A question with a right answer that an agent could find. A question that is
really four questions. Legal content dressed up as an option — asking *should
"connotation" be a legal test or a relevant factor?* is fine, because it puts
the choice to a person; writing an option that says *yes, it is a legal test,
approve this* is not.
