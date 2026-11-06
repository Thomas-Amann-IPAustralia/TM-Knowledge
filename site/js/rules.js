/* Rules as code: how the Manual's and the legislation's rules are written down so a program can
   read them and a person can check them (layer 3, ADR-0145).

   The rules are written down three ways, each from the records: connections that keep their
   wording's force, structured legal tests, and process templates. Section 44's test is drawn as a
   diagram and the process from filing as a journey, each with its text equivalent and every
   element read from `ontology.structures`; then how the rules are checked, with the counts read
   from `build.json`. The page restates no law of its own. Classes: `rx-`. */

import { esc, fmt, load, refChip, trustBadge, quoteBlock, structureHref, qualifiedLine } from "./app.js";
import { term } from "./glossary.js";
import { testDiagram, testText, flowSvg, conditionKey } from "./diagrams.js";
import { icon } from "./icons.js";

const ACTOR = { registrar: "the Registrar", applicant: "the applicant", any_person: "any person", law: "the Act itself" };
const MODAL = { must: "must", may: "may", should: "should" };
const MODAL_SAYS = { must: "an obligation, or a bar", may: "a discretion, or a possibility", should: "what is expected, not required" };

/** Small drawings of the three forms, so each reads at a glance before its words. */
const PICTURE = {
  connection: `<svg viewBox="0 0 220 92" aria-hidden="true"><circle cx="34" cy="46" r="15" class="rx-p-a"/><circle cx="186" cy="46" r="15" class="rx-p-b"/>
    <path d="M52 46 H164" class="rx-p-line"/><path d="M160 40 L168 46 L160 52" class="rx-p-line"/>
    <rect x="80" y="33" width="60" height="22" rx="11" class="rx-p-chip"/><text x="110" y="48" text-anchor="middle" class="rx-p-t">may</text>
    <path d="M70 76 h80" class="rx-p-quote"/><path d="M80 84 h60" class="rx-p-quote"/></svg>`,
  test: `<svg viewBox="0 0 220 92" aria-hidden="true"><rect x="8" y="8" width="58" height="22" rx="11" class="rx-p-chip"/><text x="37" y="23" text-anchor="middle" class="rx-p-t">if</text>
    <rect x="76" y="6" width="56" height="26" rx="6" class="rx-p-box"/><text x="142" y="23" text-anchor="middle" class="rx-p-s">and</text><rect x="154" y="6" width="56" height="26" rx="6" class="rx-p-box"/>
    <rect x="8" y="38" width="58" height="22" rx="11" class="rx-p-chip"/><text x="37" y="53" text-anchor="middle" class="rx-p-t">then</text>
    <rect x="76" y="36" width="134" height="26" rx="6" class="rx-p-box strong"/>
    <rect x="8" y="68" width="58" height="22" rx="11" class="rx-p-chip"/><text x="37" y="83" text-anchor="middle" class="rx-p-t">unless</text>
    <rect x="76" y="66" width="134" height="24" rx="6" class="rx-p-box"/></svg>`,
  process: `<svg viewBox="0 0 220 92" aria-hidden="true"><rect x="6" y="30" width="54" height="32" rx="9" class="rx-p-box strong"/><rect x="83" y="30" width="54" height="32" rx="9" class="rx-p-box"/><rect x="160" y="30" width="54" height="32" rx="9" class="rx-p-box"/>
    <path d="M60 46 H80" class="rx-p-line"/><path d="M75 41 L81 46 L75 51" class="rx-p-line"/><path d="M137 46 H157" class="rx-p-line"/><path d="M152 41 L158 46 L152 51" class="rx-p-line"/>
    <path d="M110 30 C110 6 187 6 187 27" class="rx-p-line dashed"/><path d="M182 23 L187 29 L191 22" class="rx-p-line"/>
    <path d="M30 76 h22" class="rx-p-quote"/><text x="58" y="80" class="rx-p-s">time rules, explained</text></svg>`,
};

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
  const short = (t) => esc(t.title.replace(/^.*\((section [^)]+)\)$/, "$1"));

  root.innerHTML = `
  <div class="rx">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">How it works · rules as code</span>
        <h1>How the tool represents legal rules</h1>
        <p class="lede">A legal rule can name who acts, when they can or must act, and what follows. The tool records those parts separately and links each to its source. This approach is called ${term("rules-as-code", "rules as code")}.</p>
      </div>
    </header>

    <div class="wrap">
      <section class="rx-forms" aria-label="Three ways the rules are written down">
        ${form("connection", "1 · Between two ideas", "Connections", `${fmt(ontology.relations.length)} of them, each quoting its sentence; ${fmt(modal.length)} keep their ${term("modality")} and ${fmt(conditioned)} the condition or hedge they are stated under.`, "rx-connections", "See an example link")}
        ${form("test", "2 · One provision, in full", "Legal tests", `Its conditions joined by “all of” and “any of”, what follows, its exceptions and the routes the sources describe. ${fmt(tests.length)} so far: ${tests.map(short).join(", ")}.`, "rx-test", "See the section 44 diagram")}
        ${form("process", "3 · A procedure", "Process templates", `The steps, who acts, every possible next step and what must be known to take it, and its time limits, explained and never calculated. ${fmt(processes.length)} so far.`, "rx-process", "See the process diagram")}
      </section>

      <section class="section rx-sec" id="rx-connections" tabindex="-1">
        <div class="rx-split">
          <div>
            <span class="eyebrow plain muted">1 · Connections</span>
            <h2>Why “may” and “must” matter</h2>
            <p class="muted">Each link quotes the sentence that connects two ideas. If the sentence says something “may” happen or depends on a condition, the link keeps that wording. The AI sees the same qualification when it writes an answer.</p>
            <div class="rx-modals">${Object.keys(MODAL).map((m) => `
              <div class="rx-modal-fig"><span class="rx-word">${MODAL[m]}</span><b>${fmt(byModal[m])}</b><span>${MODAL_SAYS[m]}</span></div>`).join("")}</div>
            <p class="tiny">Counts show how many links record each word from the source.</p>
            <a class="link-arrow" href="#/table/connections">Browse links and their conditions ${icon("arrow")}</a>
          </div>
          <div class="rx-examples">${shown.map((r) => connection(r, byId, ontology)).join("")}</div>
        </div>
      </section>

      ${example ? `<section class="section rx-sec" id="rx-test" tabindex="-1">
        <div class="sec-head"><div><span class="eyebrow plain muted">2 · Legal tests</span><h2>Read a legal test step by step</h2></div>
          <p>Read from top to bottom to see when a rule applies, what it requires and which exceptions matter. Select a reference such as ${refChip(example.provision)} to read the law.</p></div>
        <div class="card rx-figure">
          <div class="rx-fig-top">${trustBadge(example.origin)}<span class="tiny">${esc(example.id)}</span></div>
          ${conditionKey()}
          ${testDiagram(example)}
          <details class="text-eq"><summary>Read the diagram as text</summary><pre>${esc(testText(example))}</pre></details>
          ${stamp(example)}
        </div>
        <p class="rx-more"><a class="link-arrow" href="${structureHref(example.id)}">The whole test, part by part, with every quote and its evidence requirements ${icon("arrow")}</a></p>
      </section>` : ""}

      ${filing ? processSection(filing, processes) : ""}

      <section class="section rx-sec">
        <div class="sec-head"><div><span class="eyebrow plain muted">Trust</span><h2>How the rules are checked</h2></div>
          <p>Writing rules down is only useful if a person can trust what was written, or see at once that they cannot yet. Four checks run
          on every build; the build fails if any of the first three finds a defect.</p></div>
        <div class="grid-2 rx-checks">
          ${check("quote", "The quote check", "Every part quotes its source, word for word", `Code looks up each quote in the ${term("snapshot")} of the
            Manual and the legislation and fails on any it cannot find.${anchors ? ` The graph holds ${fmt(anchors)} such evidence anchors, each with its exact span and a fingerprint of the text.` : ""}`)}
          ${check("shield", "Validation shapes", "What every record must carry", `${fmt(shapes)} written checks (${term("shacl", "SHACL shapes")}) in
            ${fmt(Object.keys(checks.shapes).length)} files: ${Object.entries(checks.shapes).map(([name, n]) => `${esc(name)} ${fmt(n)}`).join(", ")}.
            A machine-written record without its author, date, evidence or review status fails the build; so does a legal test whose part quotes nothing.`)}
          ${check("branch", "Inference rules", "Conclusions kept apart from what anyone wrote", `Each ${term("inference-rule", "rule")} adds its conclusions
            to a graph of their own: today ${fmt(inferred.approved || 0)} from an approved rule and ${fmt(inferred.candidate || 0)} candidates from one
            not yet approved.`, `<details class="quiet"><summary>The rules</summary><ul class="small rx-rules">${checks.rules.map((r) => `<li><b>${esc(r.id)}</b>
            ${r.approved ? "(approved)" : "(not approved, so its output is a candidate)"} ${derives(r.derives)}</li>`).join("")}</ul></details>`)}
          ${check("pen", "Provenance", "Who wrote it is always on it", `${fmt(c.tests + c.processes)} structured records, ${fmt(c.relations.machine)}
            connections and ${fmt(c.definitions)} definitions were written by a machine and carry its name, the date, the evidence and the word
            ${term("unreviewed", "unreviewed")} (${term("provenance")}). Only a named expert's recorded decision makes a record approved; being left alone never does.`)}
        </div>
      </section>

      <section class="section rx-sec">
        <div class="sec-head"><div><span class="eyebrow plain muted">Limits</span><h2>What the rules never do</h2></div></div>
        <ul class="rx-never">
          ${never("Decide.", `A legal test says what a provision requires; nothing applies it to reach an outcome, and ${term("legalruleml", "executable legal rules")} are deliberately not used.`)}
          ${never("Compute a person's judgement.", "An assessment is marked as one; where a matter has one, it is what a named person recorded.")}
          ${never("Turn a “may” into a “must”.", "A discretion stays a discretion and a bar a bar, in the record, the diagram and the explanation.")}
          ${never("Work out a date.", "A time rule is explained; the date comes from the Registrar's notice.")}
          ${never("Blur practice and law.", "Each part says whether it is the Manual (the Registrar's practice) or the Act or the Regulations (law).")}
        </ul>
      </section>
    </div>
  </div>`;

  // in-page links scroll, without touching the route
  root.querySelectorAll("[data-goto]").forEach((b) => b.addEventListener("click", () => {
    const target = root.querySelector(`#${b.dataset.goto}`);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    target.focus({ preventScroll: true });
  }));
  // a step of the process opens the list of steps at its own, with its quote
  const showStep = (e) => {
    const step = e.target.closest("[data-step]");
    if (!step || (e.type === "keydown" && e.key !== "Enter" && e.key !== " ")) return;
    e.preventDefault();
    const row = root.querySelector(`.rx-steps [data-s="${CSS.escape(step.dataset.step)}"]`);
    if (!row) return;
    row.closest("details").open = true;
    root.querySelectorAll(".rx-steps li.on").forEach((li) => li.classList.remove("on"));
    row.classList.add("on");
    row.scrollIntoView({ behavior: "smooth", block: "center" });
  };
  root.querySelector(".rx-flow")?.addEventListener("click", showStep);
  root.querySelector(".rx-flow")?.addEventListener("keydown", showStep);
}

const form = (pic, k, title, text, target, go) => `<article class="card rx-form">
  <div class="rx-pic">${PICTURE[pic]}</div>
  <span class="rx-k">${k}</span><h3>${title}</h3><p class="small muted">${text}</p>
  <button type="button" class="link-arrow rx-go" data-goto="${target}">${go} ${icon("down")}</button></article>`;

const check = (ic, k, title, text, more = "") => `<article class="card rx-check"><div class="rx-check-i">${icon(ic)}</div>
  <div><span class="rx-k">${k}</span><h3>${title}</h3><p class="small muted">${text}</p>${more}</div></article>`;

const never = (what, why) => `<li><span class="pill never">Never</span><div><b>${what}</b> <span class="muted">${why}</span></div></li>`;

/** A rule's own "derives" line: the property it writes, then what it means. */
function derives(text) {
  const m = /^(tmk:\w+)\s*(.*)$/s.exec(text || "");
  return m ? `derives <code>${esc(m[1])}</code> ${esc(m[2])}` : esc(text);
}

function connection(r, byId, ontology) {
  const label = ontology.predicates[r.p]?.label || r.p;
  return `<article class="card rx-connection">
    <div class="rx-said"><span class="rx-idea">${esc(byId.get(r.s).label)}</span>
      <span class="rx-arrow"><span class="rx-pred">${esc(label)}</span><span class="rx-modal">${esc(MODAL[r.modality] || r.modality)}</span></span>
      <span class="rx-idea">${esc(byId.get(r.o).label)}</span></div>
    ${qualifiedLine(r)}
    ${quoteBlock(r.ref, r.quote)}
    <p class="row wrap-ok">${refChip(r.ref)}${trustBadge(r.origin)}<span class="tiny">${esc(r.id)}</span></p>
  </article>`;
}

function stamp(r) {
  const m = r.machine || {};
  return `<details class="quiet rx-stamp"><summary>The stamp this record carries</summary><div class="det-body">
    <dl><dt>Written by</dt><dd><code>${esc(m.by)}</code>, a machine</dd><dt>On</dt><dd>${esc(m.date)}</dd>
      <dt>Review status</dt><dd><b>${esc(m.review_status)}</b>: no trade marks expert has read it</dd>
      ${m.confidence != null ? `<dt>Its own confidence score</dt><dd>${esc(m.confidence)}, comparable with nothing else</dd>` : ""}
      ${m.reasoning ? `<dt>Why it read it this way</dt><dd>${esc(m.reasoning)}</dd>` : ""}
      ${m.check ? `<dt>What an expert should check</dt><dd>${esc(m.check)}</dd>` : ""}</dl></div></details>`;
}

function processSection(p, processes) {
  const labels = new Map(p.steps.map((s) => [s.id, s.label]));
  const others = new Map(processes.map((x) => [x.id, x]));
  const steps = p.steps.map((s) => ({ id: s.id, label: s.label, kind: s.kind,
    more: ACTOR[s.actor] || s.actor }));
  const arcs = p.transitions.map((t) => ({ from: t.from, to: t.to, needs: (t.needs || []).length > 0 }));
  const text = [`${p.title}.`, ...p.steps.map((s, i) => `${i + 1}. ${s.label} (${ACTOR[s.actor] || s.actor}; ${s.ref}): ${s.text}`),
    "Possible next steps:", ...p.transitions.map((t, k) => `${k + 1}. ${labels.get(t.from)} to ${labels.get(t.to)}, when ${t.when}`
      + ((t.needs || []).length ? ` (depends on: ${t.needs.join("; ")})` : "") + ` (${t.ref})`),
    ...(p.deadlines || []).map((d) => `Time limit (${d.ref}): ${d.text}`)].join("\n");
  return `<section class="section rx-sec" id="rx-process" tabindex="-1">
    <div class="sec-head"><div><span class="eyebrow plain muted">3 · Process templates</span><h2>Follow the steps in a procedure</h2></div>
      <p>${esc(p.title)}: the diagram shows who acts and what can happen next. A dashed arrow marks a step that depends on the facts of the application. A curved arrow can take you back to an earlier step.</p></div>
    <div class="card rx-figure">
      <div class="rx-fig-top">${trustBadge(p.origin)}<span class="tiny">${esc(p.id)}</span></div>
      <div class="rx-flow">${flowSvg({ id: `rx-${p.id}`, title: p.title, steps, arcs })}</div>
      ${p.steps.filter((s) => s.continues_in && others.has(s.continues_in)).map((s) => `<p class="small">The <b>${esc(s.label)}</b> step is set out
        in its own template, <a href="${structureHref(s.continues_in)}">${esc(others.get(s.continues_in).title)}</a>.</p>`).join("")}
      ${(p.deadlines || []).length ? `<div class="rx-time">${icon("clock")}<div><b>Time limits, explained but never calculated</b>
        <ul class="small">${p.deadlines.map((d) => `<li>${esc(d.text)} ${refChip(d.ref)}</li>`).join("")}</ul></div></div>` : ""}
      <details class="quiet"><summary>Read each step and its source</summary><div class="det-body">
        <ol class="rx-steps small">${p.steps.map((s) => `<li data-s="${esc(s.id)}"><b>${esc(s.label)}</b> <span class="muted">· ${esc(ACTOR[s.actor] || s.actor)}</span>
          <br>${esc(s.text)} ${refChip(s.ref)}</li>`).join("")}</ol>
        <h4>Possible next steps</h4>
        <ol class="rx-ways small">${p.transitions.map((t) => `<li><b>${esc(labels.get(t.from))} → ${esc(labels.get(t.to))}</b>: when ${esc(t.when)}
          ${(t.needs || []).length ? `<br><span class="muted">Depends on:</span> ${t.needs.map(esc).join("; ")}` : ""}
          ${(t.grounds || []).length ? `<br><span class="muted">Only for grounds under</span> ${t.grounds.map((g) => refChip(g)).join(" ")}` : ""}
          ${refChip(t.ref)}</li>`).join("")}</ol></div></details>
      <details class="text-eq"><summary>Read the diagram as text</summary><pre>${esc(text)}</pre></details>
    </div>
    <p class="rx-more"><a class="link-arrow" href="${structureHref(p.id)}">View all steps and sources ${icon("arrow")}</a></p>
  </section>`;
}
