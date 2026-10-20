/* The customer explanation preview — a layer 1 tool (ADR-0145), shown for transparency.

   The prototype of the customer explanation aid (D4, ADR-0142), drawn from `data/explain.json`:
   the explanation objects `tm_knowledge.explain` builds, with their text equivalents, so this
   page and `tmk-explain --html` cannot say different things. Three explanations: what a legal
   test requires, the application process, and an objection on an invented matter. Nothing is
   evaluated here; every state shown is the explanation object's.

   The owner asked for it on the examiner site as transparency (CHAT-0094, confirmed 2026-10-20).
   It is not shown to customers: testing with customers, real case data and publishing to
   customers stay the owner's gates (CLAUDE.md §3a), and the banner says so. Classes are
   prefixed `cx-` (Q-101). */

import { esc, fmt, load, refChip, srcBadge } from "./app.js";
import { conditionBoxes, stateMark, flowSvg, EFFECT_WORD, STATE } from "./diagrams.js";

const TABS = [["requirements", "What the law requires"], ["process", "The application process"], ["objection", "An objection, explained"]];
const EVIDENCE = { relevance: "What evidence must show to count", sufficiency: "How much is enough" };
const CHECK = { in_australia: "in Australia", before_filing_date: "before the filing date", sign_as_applied: "the sign applied for",
  items_covered: "all the goods or services", dated: "dated" };
const RESULT = { present: "met", missing: "not_met", "cannot tell": "open" };

export async function render(root, { params }) {
  const data = await load("explain");
  let tab = TABS.some(([id]) => id === params[0]) ? params[0] : "requirements";
  const pick = { requirements: data.requirements[0]?.test, process: data.walkthroughs[0]?.process, objection: data.matters[0]?.matter };
  if (params[1]) pick[tab] = params[1];

  root.innerHTML = `
  <div class="wrap cx">
    <p class="step-k">Layer 1 of 4 · a preview, not a service</p>
    <h1>Explaining trade marks to customers: a preview</h1>
    <div class="cx-banner" role="note">
      <p><b>Invented matters only. Not tested with customers. Not advice.</b></p>
      <ul>
        <li>Every application, person and trade mark below is invented; ${fmt(data.matters.length)} invented matters exist, each built to exercise a hard case.</li>
        <li>It was written by a machine from legal tests and process templates that no trade marks expert has reviewed.</li>
        <li>It explains what the law and the Manual say; it never says how an application will be decided. Only the Registrar decides.</li>
        <li>Nothing here has been shown to, or tested with, a customer. Whether and how it is, is the project owner's decision.</li>
      </ul>
    </div>
    <p class="lede">This is what the customer explanation aid looks like today, shown here so examiners can see it and pick holes in it.
    It explains three things in plain words, each with a picture and a text equivalent, each statement marked as law or the Manual's
    practice, and each with what it does not know: <a href="#/rules">the rules as code</a> are what it reads.</p>
    <div class="cx-tabs" role="tablist" aria-label="Which explanation">${TABS.map(([id, label]) => `
      <button type="button" role="tab" data-tab="${id}" aria-selected="${id === tab}">${esc(label)}</button>`).join("")}</div>
    <div class="cx-pick" role="group" aria-label="Which one"></div>
    <div class="cx-body"></div>
    <p class="small muted"><a href="#/future/customers">What may be tested with customers, and under which conditions →</a></p>
  </div>`;

  const body = root.querySelector(".cx-body");
  const picker = root.querySelector(".cx-pick");
  const lists = {
    requirements: data.requirements.map((r) => [r.test, r.title]),
    process: data.walkthroughs.map((w) => [w.process, w.title]),
    objection: data.matters.map((m) => [m.matter, `${m.matter} · ${m.title}`]),
  };

  function show() {
    root.querySelectorAll("[data-tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    if (!lists[tab].some(([id]) => id === pick[tab])) pick[tab] = lists[tab][0]?.[0];
    picker.innerHTML = lists[tab].map(([id, label]) => `<button type="button" class="chip${id === pick[tab] ? " on" : ""}" data-pick="${esc(id)}" aria-pressed="${id === pick[tab]}">${esc(label)}</button>`).join("");
    history.replaceState(null, "", `#/customers/${tab}/${encodeURIComponent(pick[tab] || "")}`);
    if (tab === "requirements") body.innerHTML = requirementsView(data.requirements.find((r) => r.test === pick[tab]), data);
    if (tab === "process") body.innerHTML = processView(data.walkthroughs.find((w) => w.process === pick[tab]), data);
    if (tab === "objection") body.innerHTML = matterView(data.matters.find((m) => m.matter === pick[tab]), data);
  }
  root.querySelector(".cx-tabs").addEventListener("click", (event) => {
    const b = event.target.closest("[data-tab]");
    if (b) { tab = b.dataset.tab; show(); }
  });
  picker.addEventListener("click", (event) => {
    const b = event.target.closest("[data-pick]");
    if (b) { pick[tab] = b.dataset.pick; show(); }
  });
  show();
}

const source = (ref) => `<span class="cx-src">${refChip(ref)} ${srcBadge(ref)}</span>`;
const textEq = (text, label = "Text equivalent") => `<details class="text-eq"><summary>${esc(label)}</summary><pre>${esc(text)}</pre></details>`;
const stamp = (text) => `<p class="cx-stamp">${esc(text)}</p>`;
const lowerFirst = (text) => String(text || "").replace(/^./, (c) => c.toLowerCase());

// ------------------------------------------------------------------ what the law requires

function requirementsView(r, data) {
  if (!r) return "";
  return `<article class="card cx-card">
    <h2>${esc(r.title)}</h2>
    <p class="cx-law"><span class="cx-modal">${esc(EFFECT_WORD[r.effect.kind] || r.effect.kind)}</span> ${esc(r.effect.reads)} ${source(r.provision)}</p>
    <p class="small muted">Who acts: ${esc(r.actor)}.${r.scope?.applies_to ? ` It applies to ${esc(r.scope.applies_to)}.` : ""}</p>
    <h3>The conditions, and what settles each</h3>
    <p class="small muted">A <b>fact</b> is something a record can settle, such as a date. An <b>assessment</b> is the Registrar's judgement and is never worked out by this system.</p>
    ${conditionBoxes(r.condition)}
    ${r.exceptions.length ? `<h3>Exceptions</h3><div class="cx-cols">${r.exceptions.map((x) => `<div class="cx-exception">
      <p><b>${esc(x.text)}</b> ${source(x.ref)}</p>
      <p class="cx-effect"><span class="cx-modal">${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</span> ${esc(x.effect.reads)}</p>
      ${conditionBoxes(x.condition)}</div>`).join("")}</div>` : ""}
    ${r.evidence.length ? `<h3>Evidence</h3><ul class="cx-list">${r.evidence.map((e) => `<li><span class="chip">${esc(EVIDENCE[e.kind] || e.kind)}</span>
      ${esc(e.text)} ${source(e.ref)}${e.for.length ? `<br><span class="tiny">For: ${e.for.map(esc).join("; ")}</span>` : ""}</li>`).join("")}</ul>` : ""}
    ${r.routes.length ? `<h3>Ways to respond</h3><ul class="cx-list">${r.routes.map((w) => `<li>${esc(w.text)} ${source(w.ref)}${w.scope ? ` <span class="tiny">(${esc(w.scope)})</span>` : ""}</li>`).join("")}</ul>` : ""}
    ${stamp(r.stamp)}
    ${textEq(r.text)}
  </article>`;
}

// ------------------------------------------------------------------ the application process

function processView(w, data) {
  if (!w) return "";
  const steps = w.steps.map((s) => ({ id: s.id, label: s.label, kind: s.kind,
    more: `${s.actor}${s.continues_in ? ` · continues in ${s.continues_in.process}` : ""}` }));
  const arcs = w.steps.flatMap((s) => s.next.map((n) => ({ from: s.id, to: n.to, needs: n.needs.length > 0 })))
    .filter((a) => steps.some((s) => s.id === a.to));
  return `<article class="card cx-card">
    <h2>${esc(w.title)}</h2>
    ${w.scope ? `<p class="small muted">${esc(w.scope)}</p>` : ""}
    <div class="cx-flow">
      <div class="cx-svg">${flowSvg({ id: `cx-${w.process}`, title: w.title, steps, arcs })}
        <p class="tiny">Each numbered arrow is a way on from a step. A dashed arrow depends on something a particular application must say.</p></div>
      <ol class="cx-steps">${w.steps.map((s) => `<li>
        <p><b>${esc(s.label)}</b> <span class="tiny">· ${esc(s.actor)}</span></p>
        <p class="small">${esc(s.text)} ${source(s.ref)}</p>
        ${s.continues_in ? `<p class="small cx-note">Set out in its own template: <b>${esc(s.continues_in.title)}</b> (${s.continues_in.steps.map(esc).join(" → ")}).</p>` : ""}
        ${s.next.length ? `<ul class="cx-next small">${s.next.map((n) => `<li>Next, possibly: <b>${esc(n.label)}</b>, when ${esc(n.when)}
          ${n.needs.length ? `<br><span class="muted">Depends on:</span> ${n.needs.map(esc).join("; ")}` : ""} ${source(n.ref)}</li>`).join("")}</ul>` : ""}
        ${s.time_rules.length ? `<ul class="cx-time small">${s.time_rules.map((d) => `<li><span class="chip">Time rule</span> ${esc(d.text)} ${source(d.ref)}</li>`).join("")}</ul>` : ""}
      </li>`).join("")}</ol>
    </div>
    <p class="small cx-note">${esc(w.note)}</p>
    ${stamp(w.stamp)}
    ${textEq(w.text)}
  </article>`;
}

// ------------------------------------------------------------------ an objection, on an invented matter

function matterView(e, data) {
  if (!e) return "";
  const roles = e.roles.map((r) => `${esc(r.party)}: ${r.capacities.map(esc).join(" and ")}`).join("; ");
  return `<article class="card cx-card">
    <p class="cx-invented">Invented matter ${esc(e.matter)}</p>
    <h2>${esc(e.title)}</h2>
    <p class="small">Trade mark <b>${esc(e.sign)}</b> · ${roles}</p>
    <h3>1 · The objection${e.issues.length === 1 ? "" : "s"}</h3>
    ${e.issues.map(issueView).join("")}
    <h3>2 · Where the application is</h3>
    ${positionView(e.process)}
    <h3>3 · What remains, and what would change this explanation</h3>
    <div class="cx-panel">
      <p><b>${esc(e.unresolved.reads)}</b></p>
      ${e.asks.length ? `<p>What would change this explanation:</p><ul class="cx-asks">${e.asks.map((a) => `<li>${esc(a.question)}</li>`).join("")}</ul>`
        : `<p class="small">Nothing more is needed to read the objections as recorded.</p>`}
    </div>
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
      <ul class="cx-list">${issue.candidates.map((c) => `<li><b>${esc(c.title)}</b> ${source(c.provision)}<br><span class="small">${esc(c.effect)}</span></li>`).join("")}</ul>
    </section>`;
  }
  const t = issue.test;
  return `<section class="cx-issue">
    <h4>Objection ${esc(issue.objection)}: ${esc(t.title)}</h4>
    <p class="small">${esc(issue.standing)} Goods or services: ${items}</p>
    ${issue.reasons ? `<p><b>The report says:</b> ${esc(issue.reasons)}</p>` : ""}
    <p class="cx-law"><b>The law</b> ${source(t.provision)}: if the conditions below hold, ${esc(lowerFirst(t.effect.text))}</p>
    <div class="cx-legend tiny">${Object.entries(STATE).map(([key, [mark, word]]) => `<span class="dg-st dg-st-${key}" aria-hidden="true">${mark}</span>${esc(word)}`).join(" · ")}</div>
    ${conditionBoxes(t.condition, { states: true })}
    <p class="cx-reads">${stateMark(t.state)}<b>${esc(t.reads)}</b></p>
    ${t.exceptions.length ? `<div class="cx-cols">${t.exceptions.map((x) => `<div class="cx-exception">
      <p><b>Exception:</b> ${esc(x.text)} ${source(x.ref)}</p>
      <p class="cx-effect"><span class="cx-modal">${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</span> ${esc(x.effect.reads)}</p>
      ${conditionBoxes(x.condition, { states: true })}
      <p class="small">${stateMark(x.state)}${esc(x.reads)}</p></div>`).join("")}</div>` : ""}
    ${t.routes.length ? `<p class="small"><b>Ways to respond</b></p><ul class="cx-list">${t.routes.map((r) => `<li>${esc(r.text)} ${source(r.ref)}${r.scope ? ` <span class="tiny">(${esc(r.scope)})</span>` : ""}</li>`).join("")}</ul>` : ""}
    ${issue.evidence ? evidenceView(issue.evidence) : ""}
  </section>`;
}

function evidenceView(ev) {
  const checks = [...new Set(ev.exhibits.flatMap((x) => x.checks.map((c) => c.check)))].sort();
  const text = ev.exhibits.map((x) => `Exhibit ${x.id} (${x.description}): ${x.reads}`).join("\n");
  return `<p class="small"><b>The evidence, and what it is offered for</b></p>
    <div class="cx-scroll"><table class="cx-evidence">
      <thead><tr><th scope="col">Exhibit</th>${checks.map((c) => `<th scope="col">${esc(CHECK[c] || c)}</th>`).join("")}</tr></thead>
      <tbody>${ev.exhibits.map((x) => `<tr><th scope="row">${esc(x.id)}: ${esc(x.description)}</th>${checks.map((check) => {
        const found = x.checks.find((c) => c.check === check);
        return found ? `<td>${stateMark(RESULT[found.result])}${esc(found.detail)}</td>` : "<td></td>";
      }).join("")}</tr>`).join("")}</tbody></table></div>
    ${ev.sufficiency.map((s) => `<p class="small muted">${esc(s.text)} ${source(s.ref)}</p>`).join("")}
    ${ev.set_aside.map((s) => `<p class="small muted">Set aside: ${esc(s.text)} ${source(s.ref)} (${esc(s.why)})</p>`).join("")}
    <p class="small">Whether the evidence is enough is the examiner's assessment, never this page's.</p>
    ${textEq(text)}`;
}

function positionView(p) {
  const text = [`Where the application is: ${p.current_label}.`, ...p.next.map((n) => `Next, possibly: ${n.label}, when ${n.when}`
    + (n.needs.length ? ` (depends on: ${n.needs.join("; ")})` : "")), ...(p.lapse ? [p.lapse] : []),
    ...p.deadlines.map((d) => `Time rule (${d.ref}): ${d.text}`), p.note].join("\n");
  return `<div class="cx-panel">
    <ol class="cx-timeline" aria-label="Steps so far, then what can happen next">
      ${p.history.map((h, i) => `<li class="${i === p.history.length - 1 ? "now" : "done"}"><b>${esc(h.label)}</b><span class="tiny">${esc(h.date || "date not known")}</span>
        ${h.note ? `<span class="tiny">${esc(h.note)}</span>` : ""}</li>`).join("")}
      ${p.next.length ? `<li class="next"><b>What can happen next</b><ul>${p.next.map((n) => `<li><b>${esc(n.label)}</b>, when ${esc(n.when)}
        ${n.needs.length ? `<br><span class="tiny">Depends on: ${n.needs.map(esc).join("; ")}</span>` : ""} ${source(n.ref)}</li>`).join("")}</ul></li>` : ""}
    </ol>
    <p class="small">${esc(p.current_text || "")}</p>
    ${p.lapse ? `<p class="small"><b>${esc(p.lapse)}</b></p>` : ""}
    ${p.deadlines.length ? `<ul class="cx-time small">${p.deadlines.map((d) => `<li><span class="chip">Time rule</span> ${esc(d.text)} ${source(d.ref)}</li>`).join("")}</ul>` : ""}
    <p class="small cx-note">${esc(p.note)}</p>
    ${textEq(text)}
  </div>`;
}
