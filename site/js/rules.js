/* Rules as code — layer 3 of 4 (ADR-0145): what makes the outcomes possible.

   The rules are written down three ways, each from the records: connections that keep their
   wording's force, structured legal tests, and process templates. Section 44's test is drawn as a
   diagram and the process from filing as a step flow, each with its text equivalent and every
   element read from `ontology.structures`; then how the rules are checked, with the counts read
   from `build.json`. The page restates no law of its own. */

import { esc, fmt, load, refChip, trustBadge, quoteBlock, structureHref, qualifiedLine } from "./app.js";
import { term } from "./glossary.js";
import { testDiagram, testText, flowSvg } from "./diagrams.js";

const ACTOR = { registrar: "the Registrar", applicant: "the applicant", any_person: "any person", law: "the Act itself" };
const MODAL = { must: "must", may: "may", should: "should" };

export async function render(root, { ontology }) {
  const build = await load("build");
  const c = ontology.counts;
  const tests = ontology.structures?.tests || [];
  const processes = ontology.structures?.processes || [];
  const example = tests.find((t) => t.provision === "TMA1995/s44") || tests[0];
  const filing = processes.find((p) => p.steps?.some((s) => s.kind === "start" && s.id === "filing")) || processes[0];
  const byId = new Map(ontology.concepts.map((x) => [x.id, x]));
  const modal = ontology.relations.filter((r) => r.modality);
  const byModal = Object.fromEntries(Object.keys(MODAL).map((m) => [m, modal.filter((r) => r.modality === m).length]));
  const conditioned = ontology.relations.filter((r) => r.when || r.hedge).length;
  // Two real connections between ideas that keep a "may" and a "must" and the condition their sentence states.
  const shortest = (m) => ontology.relations
    .filter((r) => r.modality === m && r.when && byId.has(r.s) && byId.has(r.o))
    .sort((a, b) => a.when.length - b.when.length || a.id.localeCompare(b.id))[0];
  const shown = ["may", "must"].map(shortest).filter(Boolean);
  const checks = build.checks || { shapes: {}, rules: [] };
  const shapes = Object.values(checks.shapes).reduce((n, x) => n + x, 0);
  const anchors = build.graph?.graphs?.authored?.classes?.EvidenceAnchor;
  const inferred = build.graph?.graphs?.inferred?.review_status || {};

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
        <p class="small">${fmt(ontology.relations.length)} of them, each quoting its sentence. ${fmt(modal.length)} keep their ${term("modality")}
        ("must", "may", "should"), and ${fmt(conditioned)} carry the condition or hedge their sentence states them under.</p>
        <a class="go" href="#connections">How one reads ↓</a></article>
      <article class="possibility card"><span class="k">2 · One provision, in full</span><h3>Legal tests</h3>
        <p class="small">A provision's effect, its conditions joined by "all of" and "any of", its exceptions, the evidence that bears on a
        condition, and the routes the sources describe. ${fmt(tests.length)} so far: ${tests.map((t) => esc(t.title.replace(/^.*\((section [^)]+)\)$/, "$1"))).join(", ")}.</p>
        <a class="go" href="#test">Section 44, drawn ↓</a></article>
      <article class="possibility card"><span class="k">3 · A procedure</span><h3>Process templates</h3>
        <p class="small">The steps of a procedure, what moves it from one step to the next and what must be known to say so, and its time
        rules, explained and never calculated. ${fmt(processes.length)} so far: ${processes.map((p) => esc(p.title)).join("; ")}.</p>
        <a class="go" href="#process">The process, drawn ↓</a></article>
    </section>

    <h2 class="section-h" id="connections" tabindex="-1">1 · A connection keeps its wording's force</h2>
    <p>A connection is the smallest piece: one idea, how it bears on another, and the sentence it rests on. What the sentence says about
    <i>how strongly</i> is kept: of the connections that state it, ${fmt(byModal.must)} say "must", ${fmt(byModal.may)} "may" and
    ${fmt(byModal.should)} "should". A "may" is never stored as a "must", and a condition ("only when …") travels with the connection
    wherever it is shown, including to the answering model.</p>
    <div class="rx-connections">${shown.map((r) => connection(r, byId, ontology)).join("")}</div>
    <p class="small"><a href="#/table/connections">Every connection, with its modality and condition →</a></p>

    ${example ? `<h2 class="section-h" id="test" tabindex="-1">2 · A legal test, drawn: ${esc(example.title)}</h2>
    <p>One provision, read clause by clause. The diagram runs top to bottom: the provision, the conditions under which it applies, what
    follows if they hold, the exceptions that change that, and what the sources say a person can do. Each box quotes the clause it comes
    from; open any chip, such as ${refChip(example.provision)}, to read the clause itself.</p>
    <div class="rx-legend small"><span class="dg-leaf dg-fact dg-mini"><span class="dg-kind"><i aria-hidden="true"></i>Fact</span></span> something a
      record can settle, such as a date or whether a mark is registered
      <span class="dg-leaf dg-evaluative dg-mini"><span class="dg-kind"><i aria-hidden="true"></i>Assessment</span></span> a person's judgement,
      such as whether two marks are deceptively similar: shown, never computed</div>
    <div class="card rx-figure">
      <div class="meta">${trustBadge(example.origin)}<span class="tiny">${esc(example.id)}</span></div>
      ${testDiagram(example)}
      <details class="text-eq"><summary>Text equivalent of the diagram</summary><pre>${esc(testText(example))}</pre></details>
    </div>
    ${stamp(example)}
    <p class="small"><a href="${structureHref(example.id)}">The whole test, part by part, with every quote, its evidence requirements and a CSV →</a></p>` : ""}

    ${filing ? processSection(filing, processes) : ""}

    <h2 class="section-h">How the rules are checked</h2>
    <p>Writing rules down is only useful if a person can trust what was written, or see at once that they cannot yet. Four checks run
    on every build, and the build fails if any of the first three finds a defect.</p>
    <div class="rx-checks">
      <article class="card"><span class="k">The quote check</span><h3>Every part quotes its source, word for word</h3>
        <p class="small">Code looks up each quote in the ${term("snapshot")} of the Manual and the legislation and fails on any it cannot find.
        ${anchors ? `The graph holds ${fmt(anchors)} such evidence anchors, each with its exact span and a fingerprint of the text.` : ""}</p></article>
      <article class="card"><span class="k">Validation shapes</span><h3>What every record must carry</h3>
        <p class="small">${fmt(shapes)} written checks (${term("shacl", "SHACL shapes")}) in ${fmt(Object.keys(checks.shapes).length)} files:
        ${Object.entries(checks.shapes).map(([name, n]) => `${esc(name)} ${fmt(n)}`).join(", ")}. A machine-written record without its
        author, date, evidence or review status fails the build; so does a legal test whose part quotes nothing.</p></article>
      <article class="card"><span class="k">Inference rules</span><h3>Conclusions kept apart from what anyone wrote</h3>
        <p class="small">Each ${term("inference-rule", "rule")} adds conclusions to a graph of their own, apart from what anyone wrote: today
        ${fmt(inferred.approved || 0)} from an approved rule and ${fmt(inferred.candidate || 0)} candidates from one not yet approved.</p>
        <ul class="tiny rx-rules">${checks.rules.map((r) => `<li><b>${esc(r.id)}</b> ${r.approved ? "(approved)" : "(not approved, so its output is a candidate)"}
          ${derives(r.derives)}</li>`).join("")}</ul></article>
      <article class="card"><span class="k">Provenance</span><h3>Who wrote it is always on it</h3>
        <p class="small">${fmt(c.tests + c.processes)} structured records, ${fmt(c.relations.machine)} connections and ${fmt(c.definitions)} definitions
        were written by a machine and carry its name, the date, the evidence and the words ${term("unreviewed", "unreviewed")}
        (${term("provenance")}). Only a named expert's recorded decision makes a record approved; being left alone never does.</p></article>
    </div>

    <h2 class="section-h">What the rules never do</h2>
    <ul class="honest">
      <li><b>Decide.</b> A legal test says what a provision requires; nothing applies it to reach an outcome, and
        ${term("legalruleml", "executable legal rules")} are deliberately not used.</li>
      <li><b>Compute a person's judgement.</b> An assessment is marked as one; where a matter has one, it is what a named person recorded.</li>
      <li><b>Turn a "may" into a "must".</b> A discretion stays a discretion and a bar a bar, in the record, the diagram and the explanation.</li>
      <li><b>Work out a date.</b> A time rule is explained; the date comes from the Registrar's notice.</li>
      <li><b>Blur practice and law.</b> Each part says whether it is the Manual (the Registrar's practice) or the Act or the Regulations (law).</li>
    </ul>
  </div>`;
  root.querySelectorAll('.possibility a[href^="#"]:not([href^="#/"])').forEach((a) => a.addEventListener("click", (event) => {
    event.preventDefault();
    const target = root.querySelector(a.getAttribute("href"));
    target.scrollIntoView({ block: "start" });
    target.focus({ preventScroll: true });
  }));
}

/** A rule's own "derives" line: the property it writes, then what it means. */
function derives(text) {
  const m = /^(tmk:\w+)\s*(.*)$/s.exec(text || "");
  return m ? `derives <code>${esc(m[1])}</code> ${esc(m[2])}` : esc(text);
}

function connection(r, byId, ontology) {
  const label = ontology.predicates[r.p]?.label || r.p;
  return `<article class="card rx-connection">
    <p class="rx-said"><b>${esc(byId.get(r.s).label)}</b> <span class="rx-pred">${esc(label)}</span> <b>${esc(byId.get(r.o).label)}</b>
      <span class="chip rx-modal">${esc(MODAL[r.modality] || r.modality)}</span></p>
    ${qualifiedLine(r)}
    ${quoteBlock(r.ref, r.quote)}
    <p class="tiny">${trustBadge(r.origin)} ${esc(r.id)} ${refChip(r.ref)}</p>
  </article>`;
}

function stamp(r) {
  const m = r.machine || {};
  return `<div class="rx-stamp card"><span class="k">The stamp this record carries</span>
    <dl><dt>Written by</dt><dd><code>${esc(m.by)}</code>, a machine</dd><dt>On</dt><dd>${esc(m.date)}</dd>
      <dt>Review status</dt><dd><b>${esc(m.review_status)}</b>: no trade marks expert has read it</dd>
      ${m.confidence != null ? `<dt>Its own confidence</dt><dd>${esc(m.confidence)}, comparable with nothing else</dd>` : ""}
      ${m.reasoning ? `<dt>Why it read it this way</dt><dd>${esc(m.reasoning)}</dd>` : ""}
      ${m.check ? `<dt>What an expert should check</dt><dd>${esc(m.check)}</dd>` : ""}</dl></div>`;
}

function processSection(p, processes) {
  const labels = new Map(p.steps.map((s) => [s.id, s.label]));
  const others = new Map(processes.map((x) => [x.id, x]));
  const steps = p.steps.map((s) => ({ id: s.id, label: s.label, kind: s.kind,
    more: `${ACTOR[s.actor] || s.actor}${s.continues_in ? ` · set out in ${s.continues_in}` : ""}` }));
  const arcs = p.transitions.map((t) => ({ from: t.from, to: t.to, needs: (t.needs || []).length > 0 }));
  const text = [`${p.title}.`, ...p.steps.map((s, i) => `${i + 1}. ${s.label} (${ACTOR[s.actor] || s.actor}; ${s.ref}): ${s.text}`),
    "Ways on:", ...p.transitions.map((t, k) => `${k + 1}. ${labels.get(t.from)} to ${labels.get(t.to)}, when ${t.when}`
      + ((t.needs || []).length ? ` (depends on: ${t.needs.join("; ")})` : "") + ` (${t.ref})`),
    ...(p.deadlines || []).map((d) => `Time rule (${d.ref}): ${d.text}`)].join("\n");
  return `<h2 class="section-h" id="process" tabindex="-1">3 · A procedure, drawn: ${esc(p.title)}</h2>
    <p>A process template sets out a procedure's steps in order, who acts at each, and every way on from a step with what must be known to
    take it. The numbered arrows on the right are the ways on; a dashed one depends on something a particular application must say.
    Where another template takes over, the step says so.</p>
    <div class="card rx-figure">
      <div class="meta">${trustBadge(p.origin)}<span class="tiny">${esc(p.id)}</span></div>
      <div class="rx-flow">
        <div class="rx-svg">${flowSvg({ id: `rx-${p.id}`, title: p.title, steps, arcs })}</div>
        <ol class="rx-ways small">${p.transitions.map((t) => `<li><b>${esc(labels.get(t.from))} → ${esc(labels.get(t.to))}</b>: when ${esc(t.when)}
          ${(t.needs || []).length ? `<br><span class="muted">Depends on:</span> ${t.needs.map(esc).join("; ")}` : ""}
          ${(t.grounds || []).length ? `<br><span class="muted">Only for grounds under</span> ${t.grounds.map((g) => refChip(g)).join(" ")}` : ""}
          ${refChip(t.ref)}</li>`).join("")}</ol>
      </div>
      ${p.steps.filter((s) => s.continues_in && others.has(s.continues_in)).map((s) => `<p class="small">The <b>${esc(s.label)}</b> step is set out
        in its own template, <a href="${structureHref(s.continues_in)}">${esc(others.get(s.continues_in).title)}</a>.</p>`).join("")}
      ${(p.deadlines || []).length ? `<h4>Time rules, explained and never calculated</h4><ul class="small">${p.deadlines.map((d) => `<li>${esc(d.text)} ${refChip(d.ref)}</li>`).join("")}</ul>` : ""}
      <details class="text-eq"><summary>Text equivalent of the diagram</summary><pre>${esc(text)}</pre></details>
    </div>
    <p class="small"><a href="${structureHref(p.id)}">The whole template, every step and transition with its quote →</a></p>`;
}
