/* Explain to customers: the customer explanation preview, a layer 1 tool (ADR-0145), shown for
   transparency.

   The prototype of the customer explanation aid (D4, ADR-0142), drawn from `data/explain.json`:
   the explanation objects `tm_knowledge.explain` builds, with their text equivalents, so this page
   and `tmk-explain --html` cannot say different things. Three explanations: what a legal test
   requires, the application process, and an objection on an invented matter. Nothing is evaluated
   here; every state shown is the explanation object's.

   The owner asked for it on the examiner site as transparency (CHAT-0094, confirmed 2026-10-20).
   It is not shown to customers: testing with customers, real case data and publishing to customers
   stay the owner's gates (CLAUDE.md §3a), and the banner says so. Classes are prefixed `cx-`. */

import { esc, fmt, load, refChip, srcBadge } from "./app.js";
import { conditionBoxes, conditionChecklist, conditionKey, effectCard, stateMark, flowSvg, STATE } from "./diagrams.js";
import { icon } from "./icons.js";

const TABS = [["requirements", "What the law requires", "book"], ["process", "The application process", "route"], ["objection", "An objection, explained", "chat"]];
const EVIDENCE = { relevance: "What evidence must show to count", sufficiency: "How much is enough" };
const CHECK = { in_australia: "in Australia", before_filing_date: "before the filing date", sign_as_applied: "the sign applied for",
  items_covered: "all the goods or services", dated: "dated" };
const RESULT = { present: "met", missing: "not_met", "cannot tell": "open" };
const ACTOR = { registrar: "the Registrar", applicant: "the applicant", any_person: "any person", law: "the Act itself" };

export async function render(root, { params }) {
  const data = await load("explain");
  let tab = TABS.some(([id]) => id === params[0]) ? params[0] : "requirements";
  const pick = { requirements: data.requirements[0]?.test, process: data.walkthroughs[0]?.process, objection: data.matters[0]?.matter };
  if (params[1]) pick[tab] = params[1];

  root.innerHTML = `
  <div class="cx">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">For customers · a preview, not a service</span>
        <h1>Explain trade marks to customers</h1>
        <p class="lede">What the customer explanation aid looks like today: what a provision requires, how an application moves, and what an
        objection means, each in plain words with a picture, its sources, and what it does not know. It is here so examiners can see it and pick holes in it.</p>
      </div>
    </header>
    <div class="wrap">
      <div class="cx-banner" role="note">
        <div class="cx-banner-head">${icon("eye")}<p><b>Invented matters only. Not tested with customers. Not advice.</b></p></div>
        <ul>
          <li>Every application, person and trade mark below is invented; ${fmt(data.matters.length)} invented matters exist, each built to exercise a hard case.</li>
          <li>It was written by a machine from legal tests and process templates that no trade marks expert has reviewed.</li>
          <li>It explains what the law and the Manual say; it never says how an application will be decided. Only the Registrar decides.</li>
          <li>Nothing here has been shown to, or tested with, a customer. Whether and how it is, is the project owner's decision.</li>
        </ul>
      </div>
      <div class="tabs cx-tabs" role="tablist" aria-label="Which explanation">${TABS.map(([id, label, ic]) => `
        <button type="button" role="tab" data-tab="${id}" aria-selected="${id === tab}">${icon(ic)}${esc(label)}</button>`).join("")}</div>
      <div class="cx-pick" role="group" aria-label="Which one"></div>
      <div class="cx-body"></div>
      <p class="small cx-more"><a class="link-arrow" href="#/future/customers">What may be tested with customers, and under which conditions ${icon("arrow")}</a></p>
    </div>
  </div>`;

  const body = root.querySelector(".cx-body");
  const picker = root.querySelector(".cx-pick");
  const processes = new Map(data.walkthroughs.map((w) => [w.process, w]));
  const cards = {
    requirements: data.requirements.map((r) => [r.test, `<span class="cx-pk">${esc(provisionName(r.provision))}</span><b>${esc(r.title.replace(/\s*\([^)]*\)\s*$/, ""))}</b>`]),
    process: data.walkthroughs.map((w) => [w.process, `<span class="cx-pk">${esc(w.process)} · ${fmt(w.steps.length)} steps</span><b>${esc(w.title.replace(/\s*\([^)]*\)\s*$/, ""))}</b>`]),
    objection: data.matters.map((m) => [m.matter, `<span class="cx-pk">Invented · ${esc(m.matter)}</span><span class="cx-sign">${esc(m.sign)}</span><span class="cx-pt">${esc(m.title)}</span>`]),
  };

  function show() {
    root.querySelectorAll("[data-tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    if (!cards[tab].some(([id]) => id === pick[tab])) pick[tab] = cards[tab][0]?.[0];
    picker.className = `cx-pick cx-pick-${tab}`;
    picker.innerHTML = cards[tab].map(([id, html]) => `<button type="button" class="cx-card-pick" data-pick="${esc(id)}" aria-pressed="${id === pick[tab]}">${html}</button>`).join("");
    history.replaceState(null, "", `#/customers/${tab}/${encodeURIComponent(pick[tab] || "")}`);
    if (tab === "requirements") body.innerHTML = requirementsView(data.requirements.find((r) => r.test === pick[tab]));
    if (tab === "process") body.innerHTML = processView(processes.get(pick[tab]));
    if (tab === "objection") body.innerHTML = matterView(data.matters.find((m) => m.matter === pick[tab]), processes);
  }
  root.querySelector(".cx-tabs").addEventListener("click", (event) => {
    const b = event.target.closest("[data-tab]");
    if (b) { tab = b.dataset.tab; show(); }
  });
  picker.addEventListener("click", (event) => {
    const b = event.target.closest("[data-pick]");
    if (b) { pick[tab] = b.dataset.pick; show(); }
  });
  // A step in a flow, clicked, brings its account into view.
  body.addEventListener("click", (event) => {
    const node = event.target.closest(".dg-node[data-step]");
    if (!node) return;
    const row = body.querySelector(`[data-step-row="${node.dataset.step}"]`);
    if (!row) return;
    row.scrollIntoView({ behavior: "smooth", block: "center" });
    row.classList.remove("cx-flash"); void row.offsetWidth; row.classList.add("cx-flash");
  });
  show();
}

const provisionName = (ref) => String(ref || "").replace(/^TMA1995\/s/, "Section ").replace(/^TMR1995\/r/, "Regulation ");
const source = (ref) => `<span class="cx-src">${refChip(ref)}</span>`;
const textEq = (text, label = "Text equivalent") => `<details class="text-eq"><summary>${esc(label)}</summary><pre>${esc(text)}</pre></details>`;
const stamp = (text) => `<p class="cx-stamp"><span class="trust machine">Machine · unreviewed</span>${esc(text)}</p>`;
const lowerFirst = (text) => String(text || "").replace(/^./, (c) => c.toLowerCase());
const stateKey = () => `<div class="cx-statekey tiny">${Object.entries(STATE).map(([key, [mark, word]]) => `<span><span class="dg-st dg-st-${key}" aria-hidden="true">${mark}</span>${esc(word)}</span>`).join("")}</div>`;

// ------------------------------------------------------------------ what the law requires

function requirementsView(r) {
  if (!r) return "";
  return `<article class="card cx-card">
    <div class="cx-card-head">
      <div><span class="eyebrow">What the law requires</span><h2>${esc(r.title)}</h2>
        <p class="small muted">Who acts: ${esc(r.actor)}.${r.scope?.applies_to ? ` It applies to ${esc(r.scope.applies_to)}.` : ""}</p></div>
      <div class="cx-head-src">${refChip(r.provision)} ${srcBadge(r.provision)}</div>
    </div>
    ${conditionKey()}
    <div class="dg-flow-v">
      <div class="dg-stage"><span class="dg-lab">If</span><div>${conditionBoxes(r.condition)}</div></div>
      <div class="dg-stage"><span class="dg-lab">Then</span><div>${effectCard(r.effect.kind, r.effect.reads, r.effect.ref)}</div></div>
      ${r.exceptions.length ? `<div class="dg-stage"><span class="dg-lab">Unless</span><div class="dg-excs">${r.exceptions.map((x) => `<div class="dg-exc">
        <p class="dg-exc-t">${esc(x.text)} ${source(x.ref)}</p>${conditionBoxes(x.condition)}${effectCard(x.effect.kind, x.effect.reads, null)}</div>`).join("")}</div></div>` : ""}
      ${r.evidence.length ? `<div class="dg-stage"><span class="dg-lab">Evidence</span><ul class="dg-routes">${r.evidence.map((e) => `<li><span class="chip">${esc(EVIDENCE[e.kind] || e.kind)}</span>
        ${esc(e.text)} ${source(e.ref)}${e.for.length ? `<br><span class="tiny">For: ${e.for.map(esc).join("; ")}</span>` : ""}</li>`).join("")}</ul></div>` : ""}
      ${r.routes.length ? `<div class="dg-stage"><span class="dg-lab">What can be done</span><ul class="dg-routes">${r.routes.map((w) => `<li>${esc(w.text)} ${source(w.ref)} ${srcBadge(w.ref)}${w.scope ? ` <span class="tiny">(${esc(w.scope)})</span>` : ""}</li>`).join("")}</ul></div>` : ""}
    </div>
    ${stamp(r.stamp)}
    ${textEq(r.text)}
  </article>`;
}

// ------------------------------------------------------------------ the application process

function flowFor(w, opts = {}) {
  const steps = w.steps.map((s) => ({ id: s.id, label: s.label, kind: s.kind, more: ACTOR[s.actor] || s.actor }));
  const arcs = w.steps.flatMap((s) => s.next.map((n) => ({ from: s.id, to: n.to, needs: n.needs.length > 0 })))
    .filter((a) => steps.some((s) => s.id === a.to));
  return flowSvg({ id: `cx-${w.process}${opts.current ? "-m" : ""}`, title: w.title, steps, arcs, ...opts });
}

const flowKey = () => `<div class="cx-flowkey tiny">
  <span><svg viewBox="0 0 30 10"><line x1="1" y1="5" x2="29" y2="5" class="dg-line"/></svg>a way on</span>
  <span><svg viewBox="0 0 30 10"><line x1="1" y1="5" x2="29" y2="5" class="dg-line dashed"/></svg>depends on what a particular application says</span>
  <span><svg viewBox="0 0 30 12"><path d="M2 11 C2 1 28 1 28 11" class="dg-line back"/></svg>back to an earlier step</span>
  <span>Click a step to read it.</span></div>`;

function processView(w) {
  if (!w) return "";
  return `<article class="card cx-card">
    <div class="cx-card-head"><div><span class="eyebrow">The application process</span><h2>${esc(w.title)}</h2>
      ${w.scope ? `<p class="small muted">${esc(w.scope)}</p>` : ""}</div></div>
    <div class="cx-flow">${flowFor(w)}</div>
    ${flowKey()}
    <ol class="cx-steps">${w.steps.map((s, i) => `<li data-step-row="${esc(s.id)}">
      <span class="cx-step-n">${i + 1}</span>
      <div><p class="cx-step-t"><b>${esc(s.label)}</b> <span class="tiny">${esc(ACTOR[s.actor] || s.actor)}</span></p>
        <p class="small">${esc(s.text)} ${source(s.ref)}</p>
        ${s.continues_in ? `<p class="small cx-note">Set out in its own template: <b>${esc(s.continues_in.title)}</b> (${s.continues_in.steps.map(esc).join(" → ")}).</p>` : ""}
        ${s.next.length ? `<ul class="cx-next small">${s.next.map((n) => `<li>Next, possibly: <b>${esc(n.label)}</b>, when ${esc(n.when)}
          ${n.needs.length ? `<br><span class="muted">Depends on:</span> ${n.needs.map(esc).join("; ")}` : ""} ${source(n.ref)}</li>`).join("")}</ul>` : ""}
        ${s.time_rules.length ? `<ul class="cx-time small">${s.time_rules.map((d) => `<li>${icon("clock")}<span><b>Time rule</b> ${esc(d.text)} ${source(d.ref)}</span></li>`).join("")}</ul>` : ""}
      </div></li>`).join("")}</ol>
    <p class="small cx-note">${esc(w.note)}</p>
    ${stamp(w.stamp)}
    ${textEq(w.text)}
  </article>`;
}

// ------------------------------------------------------------------ an objection, on an invented matter

function matterView(e, processes) {
  if (!e) return "";
  const roles = e.roles.map((r) => `<span><b>${esc(r.party)}</b> ${r.capacities.map(esc).join(" and ")}</span>`).join("");
  return `<article class="card cx-card cx-matter">
    <div class="cx-matter-head">
      <div class="cx-mark"><span class="cx-invented">Invented matter ${esc(e.matter)}</span><span class="cx-sign big">${esc(e.sign)}</span></div>
      <div><span class="eyebrow">An objection, explained</span><h2>${esc(e.title)}</h2><p class="cx-roles small">${roles}</p></div>
    </div>
    <section class="cx-view"><h3><span class="cx-vn">1</span>The objection${e.issues.length === 1 ? "" : "s"}</h3>
      ${stateKey()}
      ${e.issues.map(issueView).join("")}</section>
    <section class="cx-view"><h3><span class="cx-vn">2</span>Where the application is</h3>
      ${positionView(e.process, processes.get(e.process.process))}</section>
    <section class="cx-view"><h3><span class="cx-vn">3</span>What remains, and what would change this explanation</h3>
      <div class="cx-panel">
        <p><b>${esc(e.unresolved.reads)}</b></p>
        ${e.asks.length ? `<p>What would change this explanation:</p><ul class="cx-asks">${e.asks.map((a) => `<li>${icon("question")}<span>${esc(a.question)}</span></li>`).join("")}</ul>`
          : `<p class="small">Nothing more is needed to read the objections as recorded.</p>`}
        ${e.versions && e.versions.reads ? `<p class="small muted">Which text of the law: ${esc(e.versions.reads)}</p>` : ""}
      </div></section>
    ${stamp(e.stamp)}
    ${textEq(e.text, "The whole explanation as text")}
  </article>`;
}

function issueView(issue) {
  const items = issue.items.map((i) => `<span class="chip">${esc(i)}</span>`).join(" ");
  if (!issue.test) {
    return `<section class="cx-issue">
      <h4>Objection ${esc(issue.objection)}: the ground is not known</h4>
      <p class="small">${esc(issue.standing)} Goods or services: ${items}</p>
      <p><b>How the customer described it:</b> “${esc(issue.customer_words)}”</p>
      <p>${stateMark("open")}${esc(issue.reads)}</p>
      <p class="small">The grounds explained here, any of which it might be:</p>
      <ul class="dg-routes">${issue.candidates.map((c) => `<li><b>${esc(c.title)}</b> ${source(c.provision)}<br><span class="small">${esc(c.effect)}</span></li>`).join("")}</ul>
    </section>`;
  }
  const t = issue.test;
  return `<section class="cx-issue">
    <div class="cx-issue-head"><h4>Objection ${esc(issue.objection)}: ${esc(t.title)}</h4><span class="pill ${issue.status === "withdrawn" ? "planned" : "unreviewed"} plain">${esc(issue.status || "")}</span></div>
    <p class="small">${esc(issue.standing)} Goods or services: ${items}</p>
    ${issue.reasons ? `<p><b>The report says:</b> ${esc(issue.reasons)}</p>` : ""}
    <p class="cx-law"><b>The law</b> ${source(t.provision)}: if the conditions below hold, ${esc(lowerFirst(t.effect.text))}</p>
    <div class="cx-check">
      <div class="cx-check-col"><p class="cx-check-h">What the law asks, and what the record says</p>${conditionChecklist(t.condition)}
        <div class="cx-reads">${stateMark(t.state)}<b>${esc(t.reads)}</b></div></div>
      <div class="cx-check-col">
        ${t.exceptions.length ? `<p class="cx-check-h">Unless</p><ul class="cx-excs">${t.exceptions.map((x) => `<li>${stateMark(x.state)}<div><p><b>${esc(x.text)}</b> ${source(x.ref)}</p>
          <p class="small">${esc(x.reads)}</p></div></li>`).join("")}</ul>` : ""}
        ${t.routes.length ? `<p class="cx-check-h">What can be done</p><ul class="dg-routes">${t.routes.map((r) => `<li>${esc(r.text)} ${source(r.ref)} ${srcBadge(r.ref)}${r.scope ? ` <span class="tiny">(${esc(r.scope)})</span>` : ""}</li>`).join("")}</ul>` : ""}
      </div>
    </div>
    ${issue.evidence ? evidenceView(issue.evidence) : ""}
    <details class="quiet cx-full"><summary>See the whole test drawn, with every exception's conditions</summary><div class="det-body">
      ${conditionKey()}
      <div class="dg-flow-v">
        <div class="dg-stage"><span class="dg-lab">If</span><div>${conditionBoxes(t.condition, { states: true })}</div></div>
        <div class="dg-stage"><span class="dg-lab">So far</span><div class="cx-reads">${stateMark(t.state)}<b>${esc(t.reads)}</b></div></div>
        ${t.exceptions.length ? `<div class="dg-stage"><span class="dg-lab">Unless</span><div class="dg-excs">${t.exceptions.map((x) => `<div class="dg-exc">
          <p class="dg-exc-t">Exception: ${esc(x.text)} ${source(x.ref)}</p>
          ${effectCard(x.effect.kind, x.effect.reads, null)}
          ${conditionBoxes(x.condition, { states: true })}
          <p class="small">${stateMark(x.state)}${esc(x.reads)}</p></div>`).join("")}</div></div>` : ""}
      </div></div></details>
  </section>`;
}

function evidenceView(ev) {
  const checks = [...new Set(ev.exhibits.flatMap((x) => x.checks.map((c) => c.check)))].sort();
  const text = ev.exhibits.map((x) => `Exhibit ${x.id} (${x.description}): ${x.reads}`).join("\n");
  return `<div class="cx-evidence-box"><p class="small"><b>The evidence, and what it is offered for</b></p>
    <div class="cx-scroll"><table class="cx-evidence">
      <thead><tr><th scope="col">Exhibit</th>${checks.map((c) => `<th scope="col">${esc(CHECK[c] || c)}</th>`).join("")}</tr></thead>
      <tbody>${ev.exhibits.map((x) => `<tr><th scope="row">${esc(x.id)}: ${esc(x.description)}</th>${checks.map((check) => {
        const found = x.checks.find((c) => c.check === check);
        return found ? `<td>${stateMark(RESULT[found.result])}${esc(found.detail)}</td>` : "<td></td>";
      }).join("")}</tr>`).join("")}</tbody></table></div>
    ${ev.sufficiency.map((s) => `<p class="small muted">${esc(s.text)} ${source(s.ref)}</p>`).join("")}
    ${ev.set_aside.map((s) => `<p class="small muted">Set aside: ${esc(s.text)} ${source(s.ref)} (${esc(s.why)})</p>`).join("")}
    <p class="small">Whether the evidence is enough is the examiner's assessment, never this page's.</p>
    ${textEq(text)}</div>`;
}

function positionView(p, w) {
  const text = [`Where the application is: ${p.current_label}.`, ...p.next.map((n) => `Next, possibly: ${n.label}, when ${n.when}`
    + (n.needs.length ? ` (depends on: ${n.needs.join("; ")})` : "")), ...(p.lapse ? [p.lapse] : []),
    ...p.deadlines.map((d) => `Time rule (${d.ref}): ${d.text}`), p.note].join("\n");
  const done = p.history.map((h) => h.step).filter((s) => s !== p.current);
  return `<div class="cx-panel">
    ${w ? `<div class="cx-flow">${flowFor(w, { current: p.current, done })}</div>
      <p class="tiny cx-flow-cap">Ticked: steps the invented record says have happened. Marked “now”: where it is. Lit: what can happen next.</p>` : ""}
    <div class="cx-pos">
      <ol class="cx-timeline" aria-label="Steps so far">
        ${p.history.map((h, i) => `<li class="${i === p.history.length - 1 ? "now" : "done"}"><b>${esc(h.label)}</b><span class="tiny">${esc(h.date || "date not known")}</span>
          ${h.note ? `<span class="tiny">${esc(h.note)}</span>` : ""}</li>`).join("")}
      </ol>
      <div>
        <p class="small">${esc(p.current_text || "")}</p>
        ${p.next.length ? `<p class="cx-next-h">What can happen next</p><ul class="cx-next small">${p.next.map((n) => `<li><b>${esc(n.label)}</b>, when ${esc(n.when)}
          ${n.needs.length ? `<br><span class="tiny">Depends on: ${n.needs.map(esc).join("; ")}</span>` : ""} ${source(n.ref)}</li>`).join("")}</ul>` : ""}
        ${p.lapse ? `<p class="small"><b>${esc(p.lapse)}</b></p>` : ""}
        ${p.deadlines.length ? `<ul class="cx-time small">${p.deadlines.map((d) => `<li>${icon("clock")}<span><b>Time rule</b> ${esc(d.text)} ${source(d.ref)}</span></li>`).join("")}</ul>` : ""}
        <p class="small cx-note">${esc(p.note)}</p>
      </div>
    </div>
    ${textEq(text)}
  </div>`;
}
