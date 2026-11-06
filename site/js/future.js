/* What's next, layer 2 of 4 (ADR-0145, ADR-0148): what the same foundation could do.

   The possibilities the foundation was built for, drawn as uses standing on its layers: pick one
   to see which layers it rests on, what it builds on today, what it would still need, and where it
   stands. Possibilities, never commitments, and nothing here says the system decides, or will
   decide, an application. The section on customer testing says what may be tested and under which
   conditions; testing with customers, and using real customer or case data, are the project
   owner's decisions (CLAUDE.md §3a), and the page says so. */

import { esc, fmt, load } from "./app.js";
import { term } from "./glossary.js";
import { icon } from "./icons.js";

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
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;

  const LAYERS = [
    ["ideas", "Ideas and their kinds", `${fmt(concepts)} ideas in ${fmt(ontology.kinds.filter((k) => k.family !== "other").length)} kinds, each with its names`],
    ["connections", "Connections", `${fmt(relations)} connections, each quoting its sentence`],
    ["rules", "Rules as code", `${fmt(c.tests)} legal tests and ${fmt(c.processes)} process templates`],
    ["sources", "Sources and provenance", `every record tied to the text it rests on, who wrote it, and which version of the law`],
  ];

  const USES = [
    { id: "research", k: "Examiners", title: "Research and decision support", state: ["working", "Working"], height: 3, layers: ["ideas", "connections", "sources"],
      does: "Helps examiners find relevant law and guidance, see why a passage appeared and check the sources behind an answer.",
      builds: [`<a href="#/ask">Research a question</a>: cited answers, the Act and the Regulations kept apart from the Manual`,
        `${fmt(c.tests)} structured legal tests: a question that names a section, or its ground, brings that test's conditions and exceptions to the page`],
      needs: ["Expert review of the records answers rely on most",
        "Tests built from real research tasks, judged by examiners (who writes them is the owner's decision)",
        "Giving that test to the answering model as well, not only showing it beside the answer (the project owner's decision)",
        "Measuring the search over the Act and the Regulations"] },
    { id: "change", k: "Guidance", title: "Tracing a change", state: ["working", "Working"], height: 3, layers: ["sources"],
      does: "Lists records linked to a section, regulation or Manual page so editors know where to start checking after a change.",
      builds: [`<a href="#/change">Trace a change</a>: ${fmt(provisions)} sections and regulations with recorded dependencies`,
        `${fmt(deps.dependencies || 0)} recorded dependencies of ${fmt(deps.records || 0)} records on ${fmt(deps.refs || 0)} passages and provisions, each with a fingerprint of the text it quotes`],
      needs: ["A way to compare versions of the Manual and flag linked records for review",
        "Measuring how often a record a change touches really needed changing"] },
    { id: "customers", k: "Customers", title: "Understanding requirements, the process and objections", state: ["prototype", "Prototype"], height: 2, layers: ["rules", "sources"],
      does: "Explains, in plain language and with visuals, what a requirement means, where an application is in the process, and what an objection is about and what could be done next.",
      builds: [`${fmt(c.tests)} legal tests and ${fmt(c.processes)} process templates, each part quoting its source`,
        "Explanations of what each test requires and of the process from filing to registration, with no application needed",
        "For an invented application, three views of an objection (the objection, the process, the evidence), each with a text equivalent",
        `<a href="#/customers">The preview</a>: all three explanations on this site, on invented matters, for examiners to see`],
      needs: ["More of the law: other grounds, oppositions, and the parts of the process the templates leave out",
        "A check that each quote really supports its claim, not only that the words exist",
        "Plain-language wording checked by people, and the records it uses reviewed by an expert",
        "Testing with customers (below)"] },
    { id: "policy", k: "Policy", title: "Simulating the flow-on effects of an amendment", state: ["prototype", "Two methods demonstrated"], height: 2, layers: ["rules", "sources"],
      does: "A policy team might ask which guidance needs review, how a change affects a fictional case and how applicants might respond.",
      builds: [`The first is working: ${fmt(deps.dependencies || 0)} recorded dependencies of ${fmt(deps.records || 0)} records on the Manual and the legislation`,
        "A separate command-line tool compares three fictional amendments against fictional cases. It shows which conditions change under each amendment. The draft wording is available only outside this site.",
        "Every explanation names the text of the law it quotes, and says when the date that matters is not known",
        `<a href="#/whatif">A what-if</a>: an invented new right, geographical indications, laid over the ontology without changing it, to show which guidance it would touch`],
      needs: ["A saved copy of an earlier version of the Act to compare with draft changes",
        "Evidence about how people respond to changes. The project currently has none."] },
    { id: "chatbot", k: "Customer service", title: "A chatbot with clear visuals", state: ["planned", "Builds on the prototype"], height: 1, layers: ["ideas", "connections", "rules", "sources"],
      does: `A conversational version of the customer explanations, answering through a ${term("llm", "language model")} that cites its sources.`,
      builds: ["Research a question, which already answers claim by claim", "The customer explanation's three views"],
      needs: ["The review and testing listed under applicant explanations", "Instructions for the chatbot to give short answers in everyday language and support each point with a source",
        "The project owner's approval before any customer sees it"] },
    { id: "decisions", k: "Decision support", title: "Explaining a recorded decision, never making one", state: ["planned", "Not started"], height: 1, layers: ["rules", "sources"],
      does: "A recorded decision could be represented with the conditions it rested on and the source of each, so it can be explained and checked.",
      builds: ["Legal tests that keep facts apart from a person's assessments, and never compute an assessment", "Every condition quoting its provision, and practice kept apart from law"],
      needs: ["Expert-reviewed tests", "Recorded decisions as data (real case data: the owner's decision)",
        "This system never makes the decision; a final examination decision is not automated"] },
    { id: "ml", k: "Machine learning", title: "Data for training and testing AI", state: ["planned", "Foundation only"], height: 1, layers: ["ideas", "connections", "rules", "sources"],
      does: "Researchers could use records with named sources and version histories to train or test a future model.",
      builds: ["A release manifest on every build naming the snapshot, the law's compilations and the counts",
        `Stable identifiers, and ${term("provenance")} on every record: who wrote it, when, from what, and whether a person reviewed it`],
      needs: ["Real case data, which is the project owner's decision to use", "Rules for training data: split by matter and by time, no later outcomes in earlier features"] },
  ];

  root.innerHTML = `
  <div class="fu">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">What it could do</span>
        <h1>Current tools and possible next steps</h1>
        <p class="lede">Choose a use below to see what works today, what has been tested and what would still need to happen. Future uses are proposals.</p>
      </div>
    </header>
    <div class="wrap">
      <section class="card fu-stage" aria-label="Uses standing on the foundation">
        <div class="fu-uses" role="tablist" aria-label="Uses">${USES.map((u) => `
          <button type="button" role="tab" class="fu-use ${u.state[0]} h${u.height}" data-use="${u.id}" aria-selected="false">
            <span class="fu-k">${esc(u.k)}</span><b>${esc(u.title)}</b><span class="pill ${u.state[0]}">${esc(u.state[1])}</span></button>`).join("")}</div>
        <svg class="fu-links" aria-hidden="true"></svg>
        <div class="fu-base">
          <div class="fu-base-head">${icon("layers")}<b>What the tools share</b><span>trade mark terms, their sources and the rules that link them</span></div>
          <div class="fu-layers">${LAYERS.map(([id, label, text]) => `<div class="fu-layer" data-layer="${id}"><b>${esc(label)}</b><span>${text}</span></div>`).join("")}</div>
        </div>
      </section>
      <section class="card fu-detail" aria-live="polite"></section>

      <figure class="fu-purpose">
        <blockquote>${esc(PURPOSE)}</blockquote>
        <figcaption>The project's stated purpose, in the project owner's words (October 2026).</figcaption>
      </figure>

      <section class="fu-testing" id="customers" tabindex="-1">
        <div class="sec-head"><div><span class="eyebrow">Customers</span><h2>What we may test with customers</h2></div>
          <p><span class="pill prototype">Not started · no formal testing with customers yet</span></p></div>
        <div class="grid-4 fu-quad">
          <article class="card card-pad"><span class="fu-qi">${icon("question")}</span><h3>What would be tested</h3><ul class="small">
            <li>Whether someone who has received an objection understands what it means, what they could do, and where their application is.</li>
            <li>Whether the three views, and their text equivalents, make that clearer than words alone.</li>
            <li>Whether it asks only for the facts that change the explanation, and says what it does not know.</li></ul></article>
          <article class="card card-pad"><span class="fu-qi">${icon("route")}</span><h3>How, and in what order</h3><ul class="small">
            <li>Invented applications first: ${fmt(c.fictional_matters)} exist, each built to exercise a hard case (two objections, an unknown date, a discretion, evidence from the wrong period, an objection known only from the customer's own words).</li>
            <li>No real customer data, real application or real examination report is used until the project owner approves it.</li>
            <li>Before customer testing, review the records and check whether each quotation supports the statement it accompanies.</li>
            <li>The project owner decides when, with whom and how it is tested, and whether it is published to customers at all.</li></ul></article>
          <article class="card card-pad"><span class="fu-qi">${icon("target")}</span><h3>What success would mean</h3><ul class="small">
            <li>A person understands their situation and their options better than before.</li>
            <li>Never that it predicted an outcome: success is understanding, not a decision.</li></ul></article>
          <article class="card card-pad"><span class="fu-qi">${icon("shield")}</span><h3>What it will never do</h3><ul class="small">
            <li>Say how an application will be decided, or give legal advice.</li>
            <li>Turn a "may" into a "must", or decide a question a person must assess (such as whether two marks are deceptively similar).</li>
            <li>Work out a deadline: it explains the time rules and points to the dates the report states.</li></ul></article>
        </div>
      </section>
    </div>
  </div>`;

  const stage = root.querySelector(".fu-stage");
  const detail = root.querySelector(".fu-detail");
  const svgEl = root.querySelector(".fu-links");
  let chosen = "research";

  function links() {
    // Measured after layout, never in the first pass (Q-63).
    const box = stage.getBoundingClientRect();
    if (!box.width) return;
    const use = USES.find((u) => u.id === chosen);
    const from = stage.querySelector(`[data-use="${chosen}"]`).getBoundingClientRect();
    svgEl.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    svgEl.innerHTML = use.layers.map((id) => {
      const to = stage.querySelector(`[data-layer="${id}"]`).getBoundingClientRect();
      const x1 = from.left + from.width / 2 - box.left, y1 = from.bottom - box.top;
      const x2 = to.left + to.width / 2 - box.left, y2 = to.top - box.top;
      const my = (y1 + y2) / 2;
      return `<path d="M${x1} ${y1} C${x1} ${my} ${x2} ${my} ${x2} ${y2}" class="fu-link"/><circle cx="${x2}" cy="${y2}" r="4" class="fu-dot"/>`;
    }).join("");
  }

  function choose(id) {
    chosen = id;
    const u = USES.find((x) => x.id === id);
    stage.querySelectorAll("[data-use]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.use === id)));
    stage.querySelectorAll("[data-layer]").forEach((l) => l.classList.toggle("on", u.layers.includes(l.dataset.layer)));
    detail.innerHTML = `
      <div class="fu-d-head"><div><span class="eyebrow">${esc(u.k)}</span><h2>${esc(u.title)}</h2></div><span class="pill ${u.state[0]}">${esc(u.state[1])}</span></div>
      <p class="fu-does">${u.does}</p>
      <div class="fu-cols">
        <div><h4>${icon("check")}What we have now</h4><ul>${u.builds.map((b) => `<li>${b}</li>`).join("")}</ul></div>
        <div><h4>${icon("flag")}What we still need</h4><ul>${u.needs.map((n) => `<li>${n}</li>`).join("")}</ul></div>
      </div>`;
    requestAnimationFrame(links);
  }
  stage.addEventListener("click", (e) => { const b = e.target.closest("[data-use]"); if (b) choose(b.dataset.use); });
  const onResize = () => links();
  window.addEventListener("resize", onResize);
  choose(chosen);
  if (params[0] === "customers") {
    const target = root.querySelector("#customers");
    requestAnimationFrame(() => { target.scrollIntoView({ block: "start" }); target.focus({ preventScroll: true }); });
  }
  return () => window.removeEventListener("resize", onResize);
}
