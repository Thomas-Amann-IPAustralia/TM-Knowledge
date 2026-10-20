/* Home — layer 1 of 4: what the proof of concept does today, and how well (ADR-0144).

   Outcomes first. Each card is something the system does now, with its numbers read from the
   generated data and its state said plainly: working, measured, a prototype, or untested. The
   ontology is named once, as what sits underneath; the deeper layers explain it. */

import { esc, fmt, load } from "./app.js";
import { term } from "./glossary.js";

/** A measured difference in words, from its estimate and 95% interval (× 100). */
export function difference([est, lo, hi], better, worse) {
  const pts = (x) => Math.abs(x * 100).toFixed(1);
  const range = `range ${(lo * 100).toFixed(1)} to ${(hi * 100).toFixed(1)}`;
  if (lo > 0) return `<b>${pts(est)} points ${better}</b> <span class="muted">(${range}: established)</span>`;
  if (hi < 0) return `<b>${pts(est)} points ${worse}</b> <span class="muted">(${range}: established)</span>`;
  return `<b>no established difference</b> <span class="muted">(${range})</span>`;
}

export async function render(root, { ontology }) {
  const [stability, examples, live] = await Promise.all([load("stability"), load("examples"), load("live")]);
  const c = ontology.counts;
  const answers = examples.answers;
  const claims = answers.flatMap((a) => a.claims || []);
  const quoted = claims.filter((x) => x.supported).length;
  const gaps = claims.filter((x) => x.authority === "none").length;
  const declined = answers.filter((a) => a.declined).length;
  const s = examples.summary || {};
  const everyday = s.problem, all = s.all;
  const provisions = Object.keys(stability.provisions || {}).length;
  const firstYear = Object.keys(stability.by_year)[0];
  const concepts = c.concepts.signed + c.concepts.machine;

  root.innerHTML = `
  <div class="wrap">
    <section class="hero">
      <p class="step-k">A proof of concept for the Trade Marks Manual</p>
      <h1>Finding the right guidance faster, and explaining it plainly</h1>
      <p class="lede">This helps a trade marks examiner find the passages of the Manual, the Act and the Regulations that bear on a
      question, shows what a change to any of them would touch, and is the start of plain-language explanations for customers.
      Underneath is a model of the ideas examiners reason with, an ${term("ontology")}, and the ${term("rules-as-code", "rules as code")} built on it.</p>
      <div class="actions">
        <a class="btn primary" href="#/ask">Ask the Manual a question</a>
        <a class="btn" href="#/future">What it could do next</a>
        <a class="btn" href="#/rules">How it works</a>
      </div>
    </section>

    <h2 class="section-h">What it does today</h2>
    <section class="outcomes">
      ${outcome({
        href: "#/ask", k: "For examiners", title: "Research a question, with every claim cited",
        state: ["working", "Working · answers unreviewed"],
        text: `Ask in your own words. It recognises the ideas in the question, follows their connections, gathers the passages, keeps the
          Manual (practice) apart from the Act and the Regulations (law), and writes an answer whose every claim carries its quotes.`,
        facts: [
          `${fmt(answers.length)} prepared questions answered, ${fmt(claims.length)} claims: ${fmt(quoted)} with a quote checked word for word,
           ${fmt(gaps)} saying what the passages do not cover`,
          `${fmt(declined)} decline the part of a question that asks how an application would be decided`,
          live.enabled ? "Live questions are on" : "Live questions are off on this copy; the prepared answers and the search still work",
        ],
        go: "Ask a question",
      })}
      ${outcome({
        href: "#/about", k: "For examiners", title: "Find guidance asked in everyday words",
        state: ["measured", "Measured · mixed"],
        text: `Three searches were compared on the same ${fmt(all?.n || answers.length)} questions, scored on the quality of their first ten results
          (${term("ndcg", "top-ten quality")}, with a ${term("interval", "95% interval")}).`,
        facts: everyday && all ? [
          `Everyday-words questions, ontology-guided search against plain ${term("keyword-search", "keyword search")}: ${difference(everyday["ndcg:ontology-keyword"], "better", "worse")}`,
          `All questions, against keyword search: ${difference(all["ndcg:ontology-keyword"], "better", "worse")}`,
          `All questions, against modern search that ${term("embedding", "matches by meaning")}: ${difference(all["ndcg:ontology-hybrid"], "better", "worse")}`,
        ] : ["The measurement is not in this build."],
        go: "See the measurement and its limits",
      })}
      ${outcome({
        href: "#/change", k: "For maintaining guidance", title: "See what a change would touch",
        state: ["working", "Working · not measured"],
        text: `Pick a page of the Manual, or name a section of the Act or a regulation, and see every record that rests on it and so would
          need re-checking if it were amended, from a ${term("dependency-index")}.`,
        facts: [
          `${fmt(stability.events)} amendments recorded on the Manual's ${fmt(stability.pages.length)} pages since ${esc(firstYear)}`,
          `${fmt(provisions)} sections and regulations have something recorded as resting on them`,
          "An empty answer means no recorded dependency, never no impact",
        ],
        go: "Try it on a page or a section",
      })}
      ${outcome({
        href: "#/future", hash: "customers", k: "For customers, later", title: "Explain an objection in plain words",
        state: ["prototype", "Prototype · invented matters · not tested with customers"],
        text: `A first slice: sections 44, 43 and 41 written as structured legal tests and the examination procedure as a process
          template, explained against invented applications with three views (the objection, where the application is in the
          process, and how evidence bears on it), each with a text equivalent.`,
        facts: [
          `${fmt(c.tests)} legal tests, ${fmt(c.processes)} process template, ${fmt(c.fictional_matters)} invented matters`,
          "Nothing has been shown to, or tested with, a customer; that needs the project owner's approval",
          "It never says how an application will be decided",
        ],
        go: "What may be tested with customers",
      })}
    </section>

    <h2 class="section-h">Where it stands, in one table</h2>
    <div class="status-board card">
      <table>
        <tr><th scope="row"><span class="state working">Working</span></th><td>Asking the Manual (prepared answers, and live ones when switched on); searching the Act and
          the Regulations by section or by words; what rests on a page or a section; the map and tables of the ontology.</td></tr>
        <tr><th scope="row"><span class="state measured">Measured</span></th><td>Search quality on ${fmt(all?.n || answers.length)} test questions, both ways (above). The test
          questions were written by a model and graded by another; only ${fmt(s.signed?.n || 10)} were reviewed by a person.</td></tr>
        <tr><th scope="row"><span class="state prototype">Built, not tested</span></th><td>The legal tests, the process template and the customer explanation prototype;
          the search over the Act and the Regulations. None has been measured or tried with users.</td></tr>
        <tr><th scope="row"><span class="state unreviewed">Not yet reviewed</span></th><td>${fmt(c.concepts.machine)} of ${fmt(concepts)} ideas, ${fmt(c.relations.machine)} of
          ${fmt(c.relations.signed + c.relations.machine)} connections, every definition, legal test and answer: written by a machine and labelled
          ${term("unreviewed", "unreviewed")} wherever they appear.</td></tr>
        <tr><th scope="row"><span class="state planned">Possible next</span></th><td>Customer explanations of requirements and the application process; policy questions about
          amendments; a foundation for future machine learning and decision support. See <a href="#/future">what it could do</a>.</td></tr>
        <tr><th scope="row"><span class="state never">Never</span></th><td>Deciding an application, or saying how one will be decided.</td></tr>
      </table>
    </div>
  </div>`;
}

function outcome({ href, hash, k, title, state, text, facts, go }) {
  return `<article class="outcome card">
    <span class="k">${esc(k)}</span>
    <h3>${esc(title)}</h3>
    <span class="state ${state[0]}">${esc(state[1])}</span>
    <p class="small">${text}</p>
    <ul class="facts small">${facts.map((f) => `<li>${f}</li>`).join("")}</ul>
    <a class="go" href="${href}${hash ? `/${hash}` : ""}">${esc(go)} →</a>
  </article>`;
}
