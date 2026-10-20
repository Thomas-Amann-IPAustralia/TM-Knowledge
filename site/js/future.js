/* What it could do — layer 2 of 4 (ADR-0145).

   The possibilities the same foundations were built for, each with what it would build on today,
   what it would still need, and where it stands. Possibilities, never commitments, and nothing
   here says the system decides, or will decide, an application. The section on customer testing
   says what may be tested and under which conditions; testing with customers, and using real
   customer or case data, are the project owner's decisions (CLAUDE.md §3a), and the page says so. */

import { esc, fmt, load } from "./app.js";
import { term } from "./glossary.js";

/** The project's stated purpose, in the owner's words (ADR-0138). */
const PURPOSE = `The ontology is being written to operate as a foundational layer for any future machine learning, machine decision making,
customer service delivery or policy writing aid (simulating flow on affects of amendments). In the immediate, for examiners, it must
operate as a research and decision-support tool, helping them quickly identify relevant sections of guidance, legislation and related
material. The immediate use case for IP Australia's 'customers' is about improving understanding of trade mark requirements, the
application process and objections raised during examination (likely an LLM driven chatbot with clear visuals for explainability).`;

export async function render(root, { ontology, params }) {
  const [stability, build] = await Promise.all([load("stability"), load("build")]);
  const c = ontology.counts;
  const provisions = Object.keys(stability.provisions || {}).length;
  const deps = build.dependencies || {};

  root.innerHTML = `
  <div class="wrap future">
    <p class="step-k">Layer 2 of 4</p>
    <h1>What it could do</h1>
    <p class="lede">The same foundations were built for more than this proof of concept. Here is what they could enable, what each
    would build on, what it would still need, and where it stands. These are possibilities, not commitments.</p>

    <figure class="purpose card">
      <blockquote>${esc(PURPOSE)}</blockquote>
      <figcaption class="tiny">The project's stated purpose, in the project owner's words (October 2026).</figcaption>
    </figure>

    <h2 class="section-h">Two people it is for now</h2>
    <section class="futures two">
      ${possibility({
        k: "Examiners", title: "Research and decision support",
        state: ["working", "Working proof of concept"],
        does: "Finds the guidance, legislation and related material that bear on a question, and shows what rests on a passage or a section.",
        builds: [`<a href="#/ask">Ask the Manual</a>: cited answers, the Act and the Regulations kept apart from the Manual`,
          `<a href="#/change">When the text changes</a>: ${fmt(provisions)} sections and regulations with recorded dependencies`,
          `${fmt(c.tests)} structured legal tests: a question that names a section, or its ground, brings that test's conditions and exceptions to the Ask page`],
        needs: ["Expert review of the records answers rely on most",
          "Tests built from real research tasks, judged by examiners (who writes them is the owner's decision)",
          "Giving that test to the answering model as well, not only showing it beside the answer (the project owner's decision)",
          "Measuring the search over the Act and the Regulations"],
      })}
      ${possibility({
        k: "Customers", title: "Understanding requirements, the process and objections",
        state: ["prototype", "Prototype on invented matters"],
        does: "Explains, in plain language and with visuals, what a requirement means, where an application is in the process, and what an objection is about and what could be done next.",
        builds: [`${fmt(c.tests)} legal tests and ${fmt(c.processes)} process templates, each part quoting its source`,
          "Explanations of what each test requires and of the process from filing to registration, with no application needed",
          "For an invented application, three views of an objection (the objection, the process, the evidence), each with a text equivalent",
          `Answers checked claim by claim, the same check a customer chatbot would need`],
        needs: ["More of the law: other grounds, oppositions, and the parts of the process the templates leave out",
          "A check that each quote really supports its claim, not only that the words exist",
          "Plain-language wording checked by people, and the records it uses reviewed by an expert",
          "Testing with customers (below)"],
      })}
    </section>

    <section class="customer-testing card" id="customers" tabindex="-1">
      <h2>What we may test with customers</h2>
      <p class="state prototype">Not started · nothing has been shown to a customer</p>
      <div class="ct-grid">
        <div><h3>What would be tested</h3><ul class="small">
          <li>Whether someone who has received an objection understands what it means, what they could do, and where their application is.</li>
          <li>Whether the three views, and their text equivalents, make that clearer than words alone.</li>
          <li>Whether it asks only for the facts that change the explanation, and says what it does not know.</li></ul></div>
        <div><h3>How, and in what order</h3><ul class="small">
          <li>Invented applications first: ${fmt(c.fictional_matters)} exist, each built to exercise a hard case (two objections, an unknown date, a discretion, evidence from the wrong period, an objection known only from the customer's own words).</li>
          <li>No real customer data, real application or real examination report is used until the project owner approves it.</li>
          <li>Before anything reaches a customer: a check that every claim's quote supports it, and the records it uses reviewed.</li>
          <li>The project owner decides when, with whom and how it is tested, and whether it is published to customers at all.</li></ul></div>
        <div><h3>What success would mean</h3><ul class="small">
          <li>A person understands their situation and their options better than before.</li>
          <li>Never that it predicted an outcome: success is understanding, not a decision.</li></ul></div>
        <div><h3>What it will never do</h3><ul class="small">
          <li>Say how an application will be decided, or give legal advice.</li>
          <li>Turn a "may" into a "must", or decide a question a person must assess (such as whether two marks are deceptively similar).</li>
          <li>Work out a deadline: it explains the time rules and points to the dates the report states.</li></ul></div>
      </div>
    </section>

    <h2 class="section-h">What the same foundation could support later</h2>
    <section class="futures">
      ${possibility({
        k: "Policy", title: "Simulating the flow-on effects of an amendment",
        state: ["prototype", "First layer working"],
        does: "Three different questions, built in order: which guidance would need review; whether a matter would be treated differently; how applicants would behave.",
        builds: [`The first is working: ${fmt(deps.dependencies || 0)} recorded dependencies of ${fmt(deps.records || 0)} records on the Manual and the legislation`,
          "Legal tests that state a provision's conditions, which a scenario would change"],
        needs: ["The law at more than one point in time, so a draft can be compared with what is in force",
          "Scenarios run on invented matters, with draft text kept out of anything operative",
          "For behaviour: data nobody here holds; until then the answer is \"unknown\""],
      })}
      ${possibility({
        k: "Machine learning", title: "A foundation other models can learn from",
        state: ["planned", "Foundation only"],
        does: "Stable, labelled, versioned knowledge that a future model could be trained or evaluated on.",
        builds: ["A release manifest on every build naming the snapshot, the law's compilations and the counts",
          `Stable identifiers, and ${term("provenance")} on every record: who wrote it, when, from what, and whether a person reviewed it`],
        needs: ["Real case data, which is the project owner's decision to use",
          "Rules for training data: split by matter and by time, no later outcomes in earlier features"],
      })}
      ${possibility({
        k: "Decision support", title: "Representing a decision, never making one",
        state: ["planned", "Not started"],
        does: "A recorded decision could be represented with the conditions it rested on and the source of each, so it can be explained and checked.",
        builds: ["Legal tests that keep facts apart from a person's assessments, and never compute an assessment",
          "Every condition quoting its provision, and practice kept apart from law"],
        needs: ["Expert-reviewed tests", "Recorded decisions as data (real case data: the owner's decision)",
          "This system never makes the decision; a final examination decision is not automated"],
      })}
      ${possibility({
        k: "Customer service", title: "A chatbot with clear visuals",
        state: ["planned", "Builds on the customer prototype"],
        does: `A conversational version of the customer explanations, answering through a ${term("llm", "language model")} that cites its sources.`,
        builds: ["The examiner's Ask the Manual, which already answers claim by claim", "The customer explanation's three views"],
        needs: ["Everything in the customer row above", "A customer profile of the model: fewer, better-evidenced statements in plain words",
          "The project owner's approval before any customer sees it"],
      })}
    </section>
  </div>`;
  if (params[0] === "customers") {
    const target = root.querySelector("#customers");
    requestAnimationFrame(() => { target.scrollIntoView({ block: "start" }); target.focus({ preventScroll: true }); });
  }
}

function possibility({ k, title, state, does, builds, needs }) {
  return `<article class="possibility card">
    <span class="k">${esc(k)}</span>
    <h3>${esc(title)}</h3>
    <span class="state ${state[0]}">${esc(state[1])}</span>
    <p class="small">${does}</p>
    <h4>Builds on, today</h4><ul class="small">${builds.map((b) => `<li>${b}</li>`).join("")}</ul>
    <h4>Would still need</h4><ul class="small">${needs.map((n) => `<li>${n}</li>`).join("")}</ul>
  </article>`;
}
