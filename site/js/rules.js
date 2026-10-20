/* Rules as code — layer 3 of 4 (ADR-0144): what makes the outcomes possible.

   The rules are written down three ways, each from the records: connections that keep their
   wording's force, structured legal tests, and process templates. Then how they are kept honest.
   Section 44's test is the worked example, every element read from `ontology.structures`; the
   page restates no law of its own. */

import { esc, fmt, refChip, trustBadge, quoteBlock, structureHref } from "./app.js";
import { term } from "./glossary.js";

/** Every leaf of a condition tree, in order. */
function leaves(node, out = []) {
  if (!node) return out;
  if (node.all || node.any) (node.all || node.any).forEach((child) => leaves(child, out));
  else out.push(node);
  return out;
}

const EFFECT = { obligation: "must", discretion: "may", bar: "may not" };

export async function render(root, { ontology }) {
  const c = ontology.counts;
  const tests = ontology.structures?.tests || [];
  const processes = ontology.structures?.processes || [];
  const example = tests.find((t) => t.provision === "TMA1995/s44") || tests[0];
  const modal = ontology.relations.filter((r) => r.modality).length;
  const conditioned = ontology.relations.filter((r) => r.when || r.hedge).length;
  // Two real connections, as the predicate list's own examples phrase them.
  const examples = Object.values(ontology.predicates).filter((p) => p.example && p.label !== "is a kind of").slice(0, 2).map((p) => p.example.text);

  root.innerHTML = `
  <div class="wrap rules">
    <p class="step-k">Layer 3 of 4</p>
    <h1>Rules as code</h1>
    <p class="lede">What makes the outcomes possible is writing down what the Manual and the legislation say in a form a program can
    read, without losing what the words mean: who acts, when a rule applies, what follows, and whether it is a "must" or a "may".
    That is ${term("rules-as-code", "rules as code")}. Each piece quotes the passage or provision it comes from, so a person can always check it.</p>

    <h2 class="section-h">Three ways the rules are written down</h2>
    <section class="futures three">
      <article class="possibility card"><span class="k">1 · Between two ideas</span><h3>Connections</h3>
        <p class="small">For example: ${examples.map((x) => `<i>${esc(x)}</i>`).join("; ")}. ${fmt(ontology.relations.length)} of them,
        each quoting its sentence. ${fmt(modal)} keep their ${term("modality")} ("must", "may"), and ${fmt(conditioned)} carry the condition or hedge
        their sentence states them under.</p>
        <a class="go" href="#/table/connections">Every connection →</a></article>
      <article class="possibility card"><span class="k">2 · One provision, in full</span><h3>Legal tests</h3>
        <p class="small">A provision's effect, its conditions joined by "all of" and "any of", its exceptions, the evidence that bears on a
        condition, and the routes the sources describe. ${fmt(tests.length)} so far: ${tests.map((t) => esc(t.title.replace(/^.*\((section [^)]+)\)$/, "$1"))).join(", ")}.</p>
        <a class="go" href="#/table/tests">Every legal test →</a></article>
      <article class="possibility card"><span class="k">3 · A procedure</span><h3>Process templates</h3>
        <p class="small">The steps of a procedure, what moves it from one step to the next and what must be known to say so, and its time
        rules, explained and never calculated. ${fmt(processes.length)} so far: ${processes.map((p) => esc(p.title)).join("; ")}.</p>
        <a class="go" href="#/table/processes">Every process →</a></article>
    </section>

    ${example ? workedExample(example) : ""}

    <h2 class="section-h">How the rules are kept honest</h2>
    <ul class="honest">
      <li><b>Every part quotes its source,</b> and code checks each quote word for word against the ${term("snapshot")} of the Manual and the
        legislation. The checks fail on any quote that cannot be found there.</li>
      <li><b>A person's judgement is never computed.</b> Whether two marks are deceptively similar is marked as an assessment; the system
        shows what an examiner recorded, never its own view.</li>
      <li><b>Practice and law stay apart.</b> Each part says whether it comes from the Manual (the Registrar's practice) or the Act or the
        Regulations (law).</li>
      <li><b>Every build is checked</b> against written rules about what a record must carry (${term("shacl", "validation shapes")}), and fails on
        any defect.</li>
      <li><b>Who wrote it is always on it.</b> ${fmt(c.tests + c.processes)} structured records, ${fmt(c.relations.machine)} connections and
        ${fmt(c.definitions)} definitions were written by a machine and are labelled ${term("unreviewed")}; only a named expert's recorded decision
        makes a record approved.</li>
      <li><b>Nothing decides.</b> The rules explain what a provision requires; nothing applies them to reach an outcome, and
        ${term("legalruleml", "executable legal rules")} are deliberately not used.</li>
    </ul>
  </div>`;
}

function workedExample(t) {
  const conditions = leaves(t.condition);
  const assessed = conditions.filter((x) => x.kind === "evaluative").length;
  return `<h2 class="section-h">A worked example: ${esc(t.title)}</h2>
    <div class="worked card">
      <div class="meta">${trustBadge(t.origin)}${refChip(t.provision)}<span class="tiny">${esc(t.id)}</span></div>
      <ol class="worked-steps">
        <li><b>The effect.</b> ${esc(t.effect.text)} <span class="chip">${esc(EFFECT[t.effect.kind] || t.effect.kind)}</span>
          ${quoteBlock(t.effect.ref, t.effect.quote)}</li>
        <li><b>When it applies.</b> ${fmt(conditions.length)} conditions, joined by "all of" and "any of": ${fmt(conditions.length - assessed)} are facts
          (a date, whether a mark is registered), and ${fmt(assessed)} are a person's assessment, which is never computed.</li>
        <li><b>The exceptions.</b> ${(t.exceptions || []).map((e) => `${esc(e.text)} <span class="chip">${esc(EFFECT[e.effect?.kind] || e.effect?.kind || "")}</span>`).join("; ") || "None stated."}</li>
        <li><b>What the sources say can be done.</b> ${(t.routes || []).map((r) => esc(r.text)).join(" ")}</li>
      </ol>
      <p class="small"><a href="${structureHref(t.id)}">The whole test, part by part, with every quote →</a></p>
    </div>`;
}
