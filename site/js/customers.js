/* The public demonstrations: the customer explanation preview, redesigned for the public
   (ADR-0146, ADR-0151).

   Drawn from `data/explain.json`: the explanation objects `tm_knowledge.explain` builds, with their
   text equivalents, so this page and `tmk-explain --html` cannot say different things. Three
   explanations: an objection on an invented matter, walked through one step at a time beside a
   picture of the case that stays in view and lights the part each step is about; what a legal
   test requires, with no matter; and the application process drawn as a journey. Nothing is
   evaluated here: every state shown is the explanation object's, an assessment is never made, a
   "may" never becomes a "must", and no date is calculated.

   It is not shown to customers: testing with customers, real case data and publishing to customers
   stay the project owner's decisions (CLAUDE.md §3a), and the banner says so. Classes are prefixed
   `cx-`. */

import { esc, fmt, load, refChip, srcBadge, quoteBlock } from "./app.js";
import { STATE, layoutFlow } from "./diagrams.js";
import { icon } from "./icons.js";

const MODES = [["objection", "Understand an objection", "chat"], ["requirements", "What the law requires", "book"], ["process", "The application journey", "route"]];
const HEAD = {
  objection: ["Understand an objection", "After someone applies for a trade mark, an examiner at IP Australia checks the application against the law. If something stands in the way, the examiner raises an objection in a letter called an examination report. Pick an example to walk through one, a step at a time."],
  requirements: ["See what a rule requires", "Some sections of the Trade Marks Act 1995 set out a test an application must meet. Pick one to see what it looks at, what follows if it is met, and the exceptions, in plain terms."],
  process: ["Follow the application journey", "From filing to registration, an application passes through several stages. Select a stage to see what happens there, who acts, and what moves it on."],
};
const EFFECT_WORD = { obligation: "must", discretion: "may", bar: "may not" };
const EFFECT_SAYS = {
  obligation: "The word is “must”: an obligation.",
  discretion: "The word is “may”: a choice the Registrar makes, not an obligation.",
  bar: "The words are “may not”: something the Registrar cannot do.",
};
const STATUS = { raised: "Raised in the report", maintained: "Still raised after the response", withdrawn: "Withdrawn" };
const ACTOR = { registrar: "the Registrar", applicant: "the applicant", any_person: "any person", law: "the Act itself" };
const CHECK = { in_australia: "In Australia", before_filing_date: "Before the filing date", sign_as_applied: "The trade mark applied for", items_covered: "All the goods or services", dated: "Dated" };
const RESULT = { present: "met", missing: "not_met", "cannot tell": "open" };
const EVIDENCE = { relevance: "What makes evidence relevant", sufficiency: "Whether the evidence is enough" };

const textEq = (text, label = "Read it as text") => `<details class="text-eq"><summary>${esc(label)}</summary><pre>${esc(text)}</pre></details>`;
const stamp = (text) => `<p class="cx-stamp"><span class="trust machine">AI-written · unreviewed</span>${esc(text)}</p>`;
const kindIcon = (kind) => (kind === "evaluative"
  ? `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2.5v11M5 13.5h6M3 5h10M3 5l-1.8 4a1.9 1.9 0 0 0 3.6 0zM13 5l-1.8 4a1.9 1.9 0 0 0 3.6 0z"/></svg>`
  : `<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="2.5" y="2.5" width="11" height="11" rx="2"/><path d="m5 8.3 2 2 4-4.4"/></svg>`);
const kindBadge = (kind) => `<span class="cx-kind ${esc(kind)}">${kindIcon(kind)}${kind === "evaluative" ? "Assessment" : "Fact"}</span>`;
const mark = (state) => `<span class="cx-st ${esc(state)}" title="${esc(STATE[state]?.[1] || state)}"><span aria-hidden="true">${STATE[state]?.[0] || "?"}</span><span class="vh">${esc(STATE[state]?.[1] || state)}</span></span>`;
const shortTitle = (t) => String(t || "").replace(/\s*\([^)]*\)\s*$/, "");
const clip = (text, n) => (String(text).length > n ? `${String(text).slice(0, n - 1).replace(/\s+\S*$/, "")}…` : String(text));
const leavesOf = (node) => (node?.children ? node.children.flatMap(leavesOf) : node ? [node] : []);

export async function render(root, { params }) {
  const data = await load("explain");
  let mode = MODES.some(([id]) => id === params[0]) ? params[0] : "objection";
  const pick = { requirements: data.requirements[0]?.test, process: data.walkthroughs[0]?.process, objection: data.matters[0]?.matter };
  if (params[1]) pick[mode] = params[1];
  const processes = new Map(data.walkthroughs.map((w) => [w.process, w]));
  // the explainer's place in an objection: which issue, which step, which condition is picked
  const at = { issue: 0, step: 0, leaf: null, stop: null };

  root.innerHTML = `
  <div class="cx">
    <header class="wrap cx-head">
      <span class="eyebrow">For the public · working demonstration</span>
      <h1 class="cx-h1"></h1>
      <p class="lede cx-lede"></p>
    </header>
    <div class="wrap">
      <div class="cx-note" role="note">
        <p>${icon("eye")}<b>Fictional cases for review. Not formally tested with customers. These examples do not provide legal advice. Only the Registrar decides an application.</b></p>
        <details><summary>About these examples</summary><ul>
          <li>The ${fmt(data.matters.length)} examples use fictional applicants and trade marks to show situations that can be difficult to explain.</li>
          <li>AI wrote these explanations using legal tests and procedures that a trade marks expert has yet to review.</li>
          <li>The examples explain what an examiner considers. They never say how an application will be decided.</li>
          <li>These explanations have not been formally tested with customers; the project lists that as a future step. The project owner decides when testing or public release can begin.</li>
        </ul></details>
      </div>
      <div class="cx-modes" role="tablist" aria-label="Choose an explanation">${MODES.map(([id, label, ic]) => `
        <button type="button" role="tab" data-mode="${id}" aria-selected="${id === mode}">${icon(ic)}${esc(label)}</button>`).join("")}</div>
      <div class="cx-pick" role="group" aria-label="Choose an example"></div>
      <div class="cx-body"></div>
      <p class="small cx-more"><a class="link-arrow" href="#/public/customers">What we may test with customers ${icon("arrow")}</a></p>
    </div>
  </div>`;

  const body = root.querySelector(".cx-body");
  const picker = root.querySelector(".cx-pick");

  const cards = {
    objection: () => data.matters.map((m) => [m.matter, `<span class="cx-env" aria-hidden="true"></span><span class="cx-pk">Invented case</span><span class="cx-sign">${esc(m.sign)}</span>
      <span class="cx-who">${esc(m.roles[0]?.party || "")}</span><span class="cx-pt">${m.issues.map((i) => (i.test ? esc(shortTitle(i.test.title)) : "Described only in everyday words")).join(" · ")}</span>`]),
    requirements: () => data.requirements.map((r) => [r.test, `<span class="cx-pk">${esc(String(r.provision).replace(/^TMA1995\/s/, "Section ").replace(/^TMR1995\/r/, "Regulation "))}</span><b>${esc(shortTitle(r.title))}</b>`]),
    process: () => data.walkthroughs.map((w) => [w.process, `<span class="cx-pk">${fmt(w.steps.length)} stages</span><b>${esc(shortTitle(w.title))}</b>`]),
  };

  function show() {
    const [h1, lede] = HEAD[mode];
    root.querySelector(".cx-h1").textContent = h1;
    root.querySelector(".cx-lede").textContent = lede;
    root.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.mode === mode)));
    const list = cards[mode]();
    if (!list.some(([id]) => id === pick[mode])) pick[mode] = list[0]?.[0];
    picker.className = `cx-pick cx-pick-${mode}`;
    picker.innerHTML = list.map(([id, html]) => `<button type="button" class="cx-card-pick" data-pick="${esc(id)}" aria-pressed="${id === pick[mode]}">${html}</button>`).join("");
    history.replaceState(null, "", `#/customers/${mode}/${encodeURIComponent(pick[mode] || "")}`);
    if (mode === "objection") { body.innerHTML = matterShell(data.matters.find((m) => m.matter === pick[mode])); paintMatter(); }
    if (mode === "requirements") body.innerHTML = requirementsView(data.requirements.find((r) => r.test === pick[mode]));
    if (mode === "process") paintProcess();
  }

  // ================================================================ an objection, step by step

  const matter = () => data.matters.find((m) => m.matter === pick.objection);
  const issueNow = () => matter().issues[Math.min(at.issue, matter().issues.length - 1)];

  function stepsFor(issue) {
    if (!issue.test) {
      return [["objection", "The objection", ["case"]], ["which", "Which law?", ["candidates"]], ["where", "Where it is now", ["journey"]], ["help", "What would help", ["asks", "candidates"]]];
    }
    return [["objection", "The objection", ["case"]], ["law", "What the law says", ["effect"]], ["looks", "What it looks at", ["conditions"]],
      ...(issue.evidence ? [["evidence", "The evidence", ["conditions"]]] : []),
      ["forward", "Ways forward", ["exceptions"]], ["where", "Where it is now", ["journey"]], ["help", "What would help", ["asks", "conditions", "exceptions"]]];
  }

  function matterShell(m) {
    if (!m) return "";
    return `<article class="cx-x">
      <div class="cx-story card">
        <div class="cx-issues"></div>
        <ol class="cx-steps-nav" aria-label="Steps"></ol>
        <div class="cx-step" aria-live="polite"></div>
        <div class="cx-step-foot"><button type="button" class="btn small" data-move="-1">${icon("back")} Back</button><span class="cx-count tiny"></span><button type="button" class="btn small primary" data-move="1">Next ${icon("arrow")}</button></div>
      </div>
      <aside class="cx-board card" aria-label="The case at a glance"></aside>
    </article>
    <div class="cx-after">
      ${stamp(m.stamp)}
      ${textEq(m.text, "The whole explanation as text")}
    </div>`;
  }

  function paintMatter() {
    const m = matter();
    if (!m) return;
    const issue = issueNow();
    const steps = stepsFor(issue);
    at.step = Math.max(0, Math.min(at.step, steps.length - 1));
    const [stepId, , zones] = steps[at.step];
    const story = body.querySelector(".cx-story");
    story.querySelector(".cx-issues").innerHTML = m.issues.length > 1 ? `<div class="seg" role="group" aria-label="Which objection">${m.issues.map((i, k) => `<button type="button" data-issue="${k}" aria-pressed="${k === at.issue}">Objection ${k + 1}: ${esc(i.test ? shortTitle(i.test.title) : "unclear ground")}</button>`).join("")}</div>` : "";
    story.querySelector(".cx-steps-nav").innerHTML = steps.map(([id, label], k) => `<li><button type="button" data-step="${k}" class="${k === at.step ? "on" : k < at.step ? "seen" : ""}" aria-current="${k === at.step ? "step" : "false"}"><span>${k + 1}</span>${esc(label)}</button></li>`).join("");
    story.querySelector(".cx-step").innerHTML = stepHtml(stepId, m, issue);
    story.querySelector(".cx-count").textContent = `Step ${at.step + 1} of ${steps.length}`;
    story.querySelector('[data-move="-1"]').disabled = at.step === 0;
    const next = story.querySelector('[data-move="1"]');
    next.disabled = at.step === steps.length - 1;
    next.innerHTML = at.step === steps.length - 1 ? "The end" : `Next: ${esc(steps[at.step + 1][1])} ${icon("arrow")}`;
    const board = body.querySelector(".cx-board");
    board.innerHTML = boardHtml(m, issue);
    board.querySelectorAll("[data-zone]").forEach((z) => z.classList.toggle("lit", zones.includes(z.dataset.zone)));
    board.classList.toggle("asking", stepId === "help");
    if (at.leaf) markLeaf(at.leaf);
  }

  /** The case at a glance: the trade mark, the rule its objection turns on with every condition's
      recorded state, the exceptions, and where the application is. Each step lights its part. */
  function boardHtml(m, issue) {
    const t = issue.test;
    const w = processes.get(m.process.process);
    const items = issue.items.map((x) => `<span class="cx-chip">${esc(x)}</span>`).join("");
    const head = `<div class="cx-b-case" data-zone="case">
      <span class="cx-b-k">Invented case ${esc(m.matter)}</span>
      <span class="cx-b-sign">${esc(m.sign)}</span>
      <span class="cx-b-who">${m.roles.map((r) => `${esc(r.party)} <span class="tiny">(${r.capacities.map(esc).join(", ")})</span>`).join(" · ")}</span>
      <span class="cx-b-items"><span class="tiny">For</span> ${items}</span>
      <span class="cx-b-obj"><span class="cx-status ${esc(issue.status || "raised")}">${esc(STATUS[issue.status] || issue.status || "")}</span> ${esc(t ? shortTitle(t.title) : "Ground not yet known")} ${t ? refChip(t.provision) : ""}</span>
    </div>`;
    const journey = `<div class="cx-b-journey" data-zone="journey">
      <span class="cx-b-lab">Where it is</span>
      <div class="cx-b-j">
        <div><span class="tiny">Done</span>${m.process.history.filter((h) => h.step !== m.process.current).map((h) => `<span class="cx-j cx-j-done">${esc(h.label)}</span>`).join("") || `<span class="tiny muted">nothing before this</span>`}</div>
        <div class="now"><span class="tiny">Now</span><span class="cx-j cx-j-now">${esc(m.process.current_label)}</span></div>
        <div><span class="tiny">Could come next</span>${m.process.next.map((n) => `<span class="cx-j cx-j-next">${esc(n.label)}</span>`).join("")}</div>
      </div>${w ? "" : ""}</div>`;
    if (!t) {
      return `${head}
        <div class="cx-b-cands" data-zone="candidates">
          <p class="cx-b-said">“${esc(issue.customer_words || "")}”</p>
          <svg class="cx-b-fan" viewBox="0 0 300 40" aria-hidden="true">${issue.candidates.map((c, k) => `<path d="M150 0 C150 22 ${50 + k * 100} 16 ${50 + k * 100} 40" class="cx-fan"/>`).join("")}</svg>
          <div class="cx-b-cand">${issue.candidates.map((c) => `<div><b>${esc(shortTitle(c.title))}</b>${refChip(c.provision)}<span class="cx-q" aria-hidden="true">?</span></div>`).join("")}</div>
          <p class="tiny" data-zone="asks">Which one does the report cite? The explanation will not guess.</p>
        </div>${journey}`;
    }
    const tiles = (t.condition.children || [t.condition]).map((n) => tileHtml(n)).join("");
    return `${head}
      <div class="cx-b-rule">
        <div class="cx-b-row" data-zone="conditions"><span class="cx-b-lab">${t.condition.kind === "any" ? "If any of these" : "If all of these"}</span><div class="cx-b-tiles">${tiles}</div>
          <p class="cx-b-sum">${mark(t.state)} ${esc(t.reads)}</p></div>
        <div class="cx-b-row" data-zone="effect"><span class="cx-b-lab">Then</span><div class="cx-b-eff ${esc(t.effect.kind)}"><b>${esc(EFFECT_WORD[t.effect.kind] || t.effect.kind)}</b><span>${esc(t.effect.text)}</span></div></div>
        ${t.exceptions.length ? `<div class="cx-b-row" data-zone="exceptions"><span class="cx-b-lab">Unless</span><div class="cx-b-excs">${t.exceptions.map((x) => `<button type="button" class="cx-b-exc" data-goto="forward">
          <span class="cx-b-eff ${esc(x.effect.kind)}"><b>${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</b></span><span class="cx-b-et">${esc(clip(x.text, 74))}</span>${mark(x.state)}</button>`).join("")}</div></div>` : ""}
      </div>${journey}
      <p class="cx-b-key tiny"><span>${kindBadge("fact")} a record can confirm it</span><span>${kindBadge("evaluative")} the examiner judges it</span><span>${mark("met")} met ${mark("open")} not known ${mark("not_met")} not met</span></p>`;
  }

  function tileHtml(n) {
    if (n.children) {
      const kinds = new Set(leavesOf(n).map((l) => l.kind));
      const kind = kinds.size === 1 ? [...kinds][0] : "fact";
      return `<button type="button" class="cx-tile ${esc(kind)} ${esc(n.state || "")}" data-leaf="${esc(n.id || "")}" data-asks="${leavesOf(n).some((l) => l.ask && l.state !== "met") ? 1 : 0}">
        <span class="cx-tile-top">${kindBadge(kind)}${mark(n.state)}</span><span class="cx-tile-t">${esc(clip(n.text || "One of these", 86))}</span><span class="cx-tile-or tiny">one of ${fmt(n.children.length)}</span></button>`;
    }
    return `<button type="button" class="cx-tile ${esc(n.kind)} ${esc(n.state || "")}" data-leaf="${esc(n.id)}" data-asks="${n.ask && n.state !== "met" ? 1 : 0}">
      <span class="cx-tile-top">${kindBadge(n.kind)}${mark(n.state)}</span><span class="cx-tile-t">${esc(clip(n.text, 86))}</span></button>`;
  }

  // ---------------------------------------------------------------- each step's words
  function stepHtml(id, m, issue) {
    const t = issue.test;
    if (id === "objection") {
      return `<h2>${m.issues.length === 1 ? "The examiner raised one objection" : `The examiner raised ${fmt(m.issues.length)} objections`}</h2>
        <p class="cx-p">An objection names a ground: a reason the law gives for an application not to be accepted as it stands. Each ground has its own test.</p>
        ${m.issues.map((i, k) => `<div class="cx-obj${k === at.issue ? " on" : ""}">
          <p class="cx-obj-h"><span class="cx-status ${esc(i.status || "raised")}">${esc(STATUS[i.status] || i.status || "")}</span>${m.issues.length > 1 ? `<span class="tiny">Objection ${k + 1}</span>` : ""}</p>
          <h3>${esc(i.test ? i.test.title : "A ground the words alone cannot settle")}</h3>
          <p class="small">For: ${i.items.map(esc).join(", ")}. ${esc(i.standing)}</p>
          ${i.reasons ? `<p class="cx-said"><span class="tiny">The report says</span>${esc(i.reasons)}</p>` : ""}
          ${i.customer_words ? `<p class="cx-said customer"><span class="tiny">How the applicant described it</span>“${esc(i.customer_words)}”</p>` : ""}
          ${m.issues.length > 1 && k !== at.issue ? `<button type="button" class="link" data-issue="${k}">Walk through this objection instead</button>` : ""}
        </div>`).join("")}`;
    }
    if (id === "which") {
      return `<h2>Which law? These words do not say</h2>
        <p class="cx-p">${esc(issue.reads)}</p>
        <div class="cx-cands">${issue.candidates.map((c) => `<div class="cx-cand"><h3>${esc(c.title)}</h3><p class="small">${esc(c.effect)}</p><p>${refChip(c.provision)} ${srcBadge(c.provision)}</p></div>`).join("")}</div>
        <p class="cx-p small">Everyday words are never matched to a ground: each ground is explained differently, so the report’s own ground is needed first.</p>`;
    }
    if (id === "law") {
      const e = t.effect;
      return `<h2>What happens if the conditions are met</h2>
        <div class="cx-eff ${esc(e.kind)}"><b>${esc(EFFECT_WORD[e.kind] || e.kind)}</b><p>${esc(e.text)}</p></div>
        <p class="cx-p">${esc(EFFECT_SAYS[e.kind] || "")} ${t.scope?.applies_to ? `It applies to ${esc(t.scope.applies_to)}.` : ""}</p>
        <details class="cx-quote"><summary>The Act’s own words ${refChip(e.ref)}</summary>${quoteBlock(e.ref, e.quote)}</details>
        <p class="cx-p small">Whether the conditions are met is for the examiner, on behalf of the Registrar, to decide. The next step shows what they are.</p>`;
    }
    if (id === "looks") {
      const leaves = leavesOf(t.condition);
      const facts = leaves.filter((l) => l.kind === "fact").length;
      const others = data.matters.filter((x) => x.matter !== m.matter && x.issues.some((i) => i.test?.test === t.test));
      return `<h2>What the law looks at</h2>
        <p class="cx-p">There are two kinds of condition. <b>Facts</b> are things a record can confirm, such as a date. <b>Assessments</b> are judgements only the examiner can make. This explanation shows what the report records for each, and never makes an assessment itself.</p>
        <p class="cx-split"><span>${kindBadge("fact")} <b>${fmt(facts)}</b> fact${facts === 1 ? "" : "s"}</span><span>${kindBadge("evaluative")} <b>${fmt(leaves.length - facts)}</b> assessment${leaves.length - facts === 1 ? "" : "s"}</span></p>
        ${condList(t.condition, true)}
        <p class="cx-sofar">${mark(t.state)}<b>${esc(t.reads)}</b></p>
        ${others.length ? contrast(m, t, others[0]) : ""}`;
    }
    if (id === "evidence") return evidenceStep(issue.evidence);
    if (id === "forward") {
      return `<h2>Ways forward</h2>
        ${t.exceptions.length ? `<p class="cx-p">The law sets out exceptions. If the examiner is satisfied one applies, what follows changes. Whether it applies is for the examiner to decide.</p>
        ${t.exceptions.map((x) => `<div class="cx-exc">
          <div class="cx-eff cx-eff-sm ${esc(x.effect.kind)}"><b>${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</b><p>${esc(x.effect.text)}</p></div>
          <h3>Unless: ${esc(x.text)} ${refChip(x.ref)}</h3>
          <p class="small muted">${esc(EFFECT_SAYS[x.effect.kind] || "")}</p>
          ${condList(x.condition, true)}
          <p class="cx-sofar small">${mark(x.state)}${esc(x.reads)}</p></div>`).join("")}` : `<p class="cx-p">This ground has no exception set out in the rule.</p>`}
        ${t.routes.length ? `<h3 class="cx-h3">What can be done</h3><ul class="cx-routes">${t.routes.map((r) => `<li>${icon("route")}<span>${esc(r.text)} ${refChip(r.ref)} ${srcBadge(r.ref)}${r.scope ? ` <span class="tiny">(${esc(r.scope)})</span>` : ""}</span></li>`).join("")}</ul>
          <p class="tiny">A route marked “practice” comes from the Manual, which describes how the law is applied; it is not law.</p>` : ""}`;
    }
    if (id === "where") {
      const p = m.process;
      const w = processes.get(p.process);
      const done = p.history.map((h) => h.step).filter((s) => s !== p.current);
      return `<h2>Where the application is now: ${esc(p.current_label)}</h2>
        <p class="cx-p">${esc(p.current_text || "")}</p>
        ${w ? `<div class="cx-journey">${journeySvg(w, { id: `cx-j-${m.matter}`, current: p.current, done })}</div>` : ""}
        <ol class="cx-hist">${p.history.map((h) => `<li class="${h.step === p.current ? "now" : "done"}"><b>${esc(h.label)}</b><span class="tiny">${esc(h.date || "date not known")}${h.note ? ` · ${esc(h.note)}` : ""}</span></li>`).join("")}</ol>
        ${p.next.length ? `<h3 class="cx-h3">What could come next</h3><ul class="cx-next">${p.next.map((n) => `<li><b>${esc(n.label)}</b>, when ${esc(n.when)}${n.needs.length ? `<span class="tiny">Depends on: ${n.needs.map(esc).join("; ")}</span>` : ""} ${refChip(n.ref)}</li>`).join("")}</ul>` : ""}
        ${p.lapse ? `<p class="cx-lapse">${icon("calendar")}<b>${esc(p.lapse)}</b></p>` : ""}
        ${p.deadlines.length ? `<ul class="cx-time">${p.deadlines.map((d) => `<li>${icon("clock")}<span>${esc(d.text)} ${refChip(d.ref)}</span></li>`).join("")}</ul>` : ""}
        <p class="tiny">${esc(p.note)}</p>`;
    }
    if (id === "help") {
      return `<h2>What would help explain more</h2>
        <p class="cx-p">${esc(m.unresolved.reads)}</p>
        ${m.asks.length ? `<p class="cx-p">Only facts that would change the explanation are asked for. On the picture, they are the conditions marked as not known.</p>
          <ul class="cx-asks">${m.asks.map((a) => `<li data-ask="${esc(a.condition)}">${icon("question")}<span>${esc(a.question)}</span></li>`).join("")}</ul>`
          : `<p class="cx-p">Nothing more is needed to read the objections as recorded.</p>`}
        ${m.versions?.reads ? `<p class="small muted"><b>Which text of the law:</b> ${esc(m.versions.reads)}</p>` : ""}
        <p class="cx-p small">That is the whole explanation. It can be read as text below, with every source.</p>`;
    }
    return "";
  }

  /** A condition tree as a list a person can read: a group says whether all or any one of its
      conditions must hold; each condition says whether it is a fact or an assessment and, with
      `states`, what the report records for it. */
  function condList(node, states) {
    if (node.children) {
      return `<div class="cx-cg"${node.id ? ` data-leaf-row="${esc(node.id)}"` : ""}>${node.text ? `<p class="cx-cg-t">${esc(node.text)}</p>` : ""}<p class="cx-cg-h">${states && node.state ? mark(node.state) : ""}${node.kind === "any" ? "Any one of these is enough" : "All of these must be met"}</p>
        <ul>${node.children.map((c) => `<li>${condList(c, states)}</li>`).join("")}</ul></div>`;
    }
    const st = node.state ? STATE[node.state]?.[1] : "";
    return `<div class="cx-cond ${esc(node.kind)}" data-leaf-row="${esc(node.id)}">
      <div class="cx-cond-top">${kindBadge(node.kind)}${states && node.state ? mark(node.state) : ""}</div>
      <p class="cx-cond-t">${esc(node.text)}</p>
      ${states && node.why ? `<p class="cx-cond-st">${esc(st ? st.charAt(0).toUpperCase() + st.slice(1) : "")}: ${esc(node.why)}</p>` : ""}
      ${states && node.ask && node.state !== "met" ? `<p class="cx-cond-ask">${icon("question")}${esc(node.ask)}</p>` : ""}
      <p class="cx-cond-src">${refChip(node.ref)}</p></div>`;
  }

  /** The same rule on another invented case: which conditions read differently, side by side. */
  function contrast(m, t, other) {
    const oi = other.issues.find((i) => i.test?.test === t.test);
    const mine = new Map(leavesOf(t.condition).map((l) => [l.id, l]));
    const theirs = new Map(leavesOf(oi.test.condition).map((l) => [l.id, l]));
    const rows = [...mine.keys()].filter((id) => theirs.has(id));
    const differ = rows.filter((id) => mine.get(id).state !== theirs.get(id).state).length;
    return `<details class="cx-contrast"><summary>Same law, different facts: compare with ${esc(other.sign)}</summary><div class="det-body">
      <p class="small">The rule does not change between cases; what the records show does. ${differ ? `${fmt(differ)} of ${fmt(rows.length)} conditions read differently.` : "Every condition reads the same."}</p>
      <table class="cx-ct"><thead><tr><th scope="col">Condition</th><th scope="col">${esc(m.sign)}</th><th scope="col">${esc(other.sign)}</th></tr></thead>
      <tbody>${rows.map((id) => { const a = mine.get(id), b = theirs.get(id); return `<tr class="${a.state !== b.state ? "diff" : ""}"><th scope="row">${kindBadge(a.kind)} ${esc(clip(a.text, 90))}</th><td>${mark(a.state)} <span class="tiny">${esc(a.why || "")}</span></td><td>${mark(b.state)} <span class="tiny">${esc(b.why || "")}</span></td></tr>`; }).join("")}</tbody></table>
      <p class="small"><button type="button" class="link" data-pick-matter="${esc(other.matter)}">Walk through ${esc(other.sign)} instead</button></p></div></details>`;
  }

  function evidenceStep(ev) {
    const checks = [...new Set(ev.exhibits.flatMap((x) => x.checks.map((c) => c.check)))].sort();
    const text = ev.exhibits.map((x) => `Exhibit ${x.id} (${x.description}): ${x.reads || ""}`).join("\n");
    return `<h2>The evidence, and what each piece is meant to show</h2>
      <p class="cx-p">The applicant has filed evidence of use. The Manual describes what makes evidence relevant; each exhibit is set against those points. How much is enough is the examiner’s assessment.</p>
      <div class="cx-scroll"><table class="cx-ev">
        <thead><tr><th scope="col">Exhibit</th>${checks.map((c) => `<th scope="col">${esc(CHECK[c] || c)}</th>`).join("")}</tr></thead>
        <tbody>${ev.exhibits.map((x) => `<tr><th scope="row">${esc(x.id)}: ${esc(x.description)}</th>${checks.map((check) => {
          const found = x.checks.find((c) => c.check === check);
          return found ? `<td>${mark(RESULT[found.result])}<span class="tiny">${esc(found.detail)}</span></td>` : "<td></td>";
        }).join("")}</tr>`).join("")}</tbody></table></div>
      ${[...ev.relevance, ...ev.sufficiency].map((s) => `<p class="small cx-evr"><span class="tiny">${esc(EVIDENCE[ev.relevance.includes(s) ? "relevance" : "sufficiency"])}</span>${esc(s.text)} ${refChip(s.ref)} ${srcBadge(s.ref)}</p>`).join("")}
      ${ev.set_aside.map((s) => `<p class="small muted">Set aside: ${esc(s.text)} ${refChip(s.ref)} (${esc(s.why)})</p>`).join("")}
      ${textEq(text)}`;
  }

  /** Light a condition in the words and on the picture together. */
  function markLeaf(id) {
    at.leaf = id;
    body.querySelectorAll("[data-leaf]").forEach((x) => x.classList.toggle("on", x.dataset.leaf === id));
    body.querySelectorAll("[data-leaf-row]").forEach((x) => x.classList.toggle("on", x.dataset.leafRow === id));
    const row = body.querySelector(`[data-leaf-row="${CSS.escape(id)}"]`);
    if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // ================================================================ what the law requires, with no matter

  function requirementsView(r) {
    if (!r) return "";
    const leaves = leavesOf(r.condition);
    const facts = leaves.filter((l) => l.kind === "fact").length;
    return `<article class="card cx-req">
      <div class="cx-req-head">
        <div><span class="eyebrow">What the law requires</span><h2>${esc(r.title)}</h2>
          <p class="small muted">Who applies it: ${esc(r.actor)}.${r.scope?.applies_to ? ` It applies to ${esc(r.scope.applies_to)}.` : ""}</p></div>
        <div class="cx-req-src">${refChip(r.provision)} ${srcBadge(r.provision)}</div>
      </div>
      <div class="cx-req-grid">
        <div class="cx-req-main">
          <section><h3 class="cx-h3">If the conditions are met</h3>
            <div class="cx-eff ${esc(r.effect.kind)}"><b>${esc(EFFECT_WORD[r.effect.kind] || r.effect.kind)}</b><p>${esc(r.effect.text)}</p></div>
            <p class="small muted">${esc(EFFECT_SAYS[r.effect.kind] || "")}</p></section>
          <section><h3 class="cx-h3">What it looks at</h3>
            <p class="cx-split"><span>${kindBadge("fact")} <b>${fmt(facts)}</b> fact${facts === 1 ? "" : "s"} a record can confirm</span><span>${kindBadge("evaluative")} <b>${fmt(leaves.length - facts)}</b> assessment${leaves.length - facts === 1 ? "" : "s"} only a person makes</span></p>
            ${condList(r.condition, false)}</section>
          ${r.exceptions.length ? `<details class="cx-acc"><summary>Unless: the exceptions <span class="tiny">${fmt(r.exceptions.length)}</span></summary><div class="det-body">${r.exceptions.map((x) => `<div class="cx-exc">
            <div class="cx-eff cx-eff-sm ${esc(x.effect.kind)}"><b>${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</b><p>${esc(x.effect.text)}</p></div>
            <h3>${esc(x.text)} ${refChip(x.ref)}</h3>${condList(x.condition, false)}</div>`).join("")}</div></details>` : ""}
          ${r.evidence.length ? `<details class="cx-acc"><summary>The evidence <span class="tiny">${fmt(r.evidence.length)}</span></summary><div class="det-body"><ul class="cx-routes">${r.evidence.map((e) => `<li>${icon("file")}<span><span class="tiny">${esc(EVIDENCE[e.kind] || e.kind)}</span><br>${esc(e.text)} ${refChip(e.ref)} ${srcBadge(e.ref)}</span></li>`).join("")}</ul></div></details>` : ""}
          ${r.routes.length ? `<details class="cx-acc"><summary>What can be done <span class="tiny">${fmt(r.routes.length)}</span></summary><div class="det-body"><ul class="cx-routes">${r.routes.map((w) => `<li>${icon("route")}<span>${esc(w.text)} ${refChip(w.ref)} ${srcBadge(w.ref)}${w.scope ? ` <span class="tiny">(${esc(w.scope)})</span>` : ""}</span></li>`).join("")}</ul></div></details>` : ""}
        </div>
        <aside class="cx-req-pic" aria-hidden="true">
          <span class="cx-b-lab">The rule at a glance</span>
          <div class="cx-b-tiles col">${(r.condition.children || [r.condition]).map((n) => `<div class="cx-tile ${esc(n.children ? (new Set(leavesOf(n).map((l) => l.kind)).size === 1 ? leavesOf(n)[0].kind : "fact") : n.kind)} plain"><span class="cx-tile-top">${kindBadge(n.children ? leavesOf(n)[0].kind : n.kind)}</span><span class="cx-tile-t">${esc(clip(n.text || "One of these", 80))}</span></div>`).join(`<span class="cx-and">${r.condition.kind === "any" ? "or" : "and"}</span>`)}</div>
          <div class="cx-b-eff ${esc(r.effect.kind)}"><b>${esc(EFFECT_WORD[r.effect.kind] || r.effect.kind)}</b><span>${esc(clip(r.effect.text, 90))}</span></div>
          ${r.exceptions.map((x) => `<div class="cx-b-exc static"><span class="cx-b-eff ${esc(x.effect.kind)}"><b>${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</b></span><span class="cx-b-et">${esc(clip(x.text, 70))}</span></div>`).join("")}
        </aside>
      </div>
      ${stamp(r.stamp)}
      ${textEq(r.text)}
    </article>`;
  }

  // ================================================================ the application journey

  /** A record's own words name another procedure by its identifier; a reader is given its title. */
  const named = (text) => String(text || "").replace(/GP-\d{4}/g, (id) => (processes.get(id) ? `“${shortTitle(processes.get(id).title)}”` : id));

  function paintProcess() {
    const w = processes.get(pick.process);
    if (!w) { body.innerHTML = ""; return; }
    if (!w.steps.some((s) => s.id === at.stop)) at.stop = w.steps[0].id;
    const i = w.steps.findIndex((s) => s.id === at.stop);
    const s = w.steps[i];
    body.innerHTML = `<article class="card cx-proc">
      <div class="cx-req-head"><div><span class="eyebrow">The application journey</span><h2>${esc(shortTitle(w.title))}</h2>${w.scope ? `<p class="small muted">${esc(named(w.scope))}</p>` : ""}</div></div>
      <div class="cx-journey big">${journeySvg(w, { id: `cx-p-${w.process}`, selected: s.id, interactive: true })}</div>
      <p class="cx-jkey tiny"><span><svg viewBox="0 0 30 10" aria-hidden="true"><path d="M1 5h28" class="cx-jl"/></svg>can come next</span><span><svg viewBox="0 0 30 10" aria-hidden="true"><path d="M1 5h28" class="cx-jl dashed"/></svg>depends on the facts of the application</span><span>Select a stage, or step through them.</span></p>
      <div class="cx-stop" aria-live="polite">
        <div class="cx-stop-head"><span class="cx-stop-n">${i + 1}</span><div><h3>${esc(s.label)}</h3><p class="tiny">Who acts: ${esc(ACTOR[s.actor] || s.actor)}</p></div>
          <div class="cx-stop-nav"><button type="button" class="btn small" data-stop-move="-1" ${i === 0 ? "disabled" : ""}>${icon("back")} Back</button><button type="button" class="btn small primary" data-stop-move="1" ${i === w.steps.length - 1 ? "disabled" : ""}>Next ${icon("arrow")}</button></div></div>
        <p>${esc(s.text)} ${refChip(s.ref)} ${srcBadge(s.ref)}</p>
        ${s.continues_in ? `<p class="cx-cont">${icon("route")}<span>What happens after an examination report is its own journey: <button type="button" class="link" data-proc="${esc(s.continues_in.process)}">${esc(shortTitle(s.continues_in.title))}</button>.</span></p>` : ""}
        ${s.next.length ? `<h4>What moves it on</h4><ul class="cx-next">${s.next.map((n) => `<li><button type="button" class="link" data-to="${esc(n.to)}">${esc(n.label)}</button>, when ${esc(n.when)}${n.needs.length ? `<span class="tiny">Depends on: ${n.needs.map(esc).join("; ")}</span>` : ""} ${refChip(n.ref)}</li>`).join("")}</ul>` : `<p class="small muted">The journey ends here.</p>`}
        ${s.time_rules.length ? `<h4>Time rules</h4><ul class="cx-time">${s.time_rules.map((d) => `<li>${icon("clock")}<span>${esc(d.text)} ${refChip(d.ref)}</span></li>`).join("")}</ul>` : ""}
      </div>
      <p class="tiny">${esc(w.note)}</p>
      ${stamp(w.stamp)}
      ${textEq(w.text)}
    </article>`;
  }

  /** A process drawn as a journey: each stage a stop on a line, the main way across, the other ways
      branching off it, and a way back to an earlier stage a loop over the top. With a matter, the
      stages done are filled, the current one ringed and the ways out of it lit. */
  function journeySvg(w, { id, current = null, done = [], selected = null, interactive = false }) {
    const steps = w.steps.map((s) => ({ id: s.id, label: s.label, kind: s.kind, actor: s.actor }));
    const arcs = w.steps.flatMap((s) => s.next.map((n) => ({ from: s.id, to: n.to, needs: n.needs.length > 0 }))).filter((a) => steps.some((s) => s.id === a.to));
    const { rank, lane, idx } = layoutFlow(steps, arcs);
    const CW = 132, RH = 86, R = 14;
    const lanes = [...lane.values()];
    const minL = Math.min(0, ...lanes), maxL = Math.max(0, ...lanes);
    const back = arcs.filter((a) => idx.get(a.to) <= idx.get(a.from));
    const top = 34 + (back.length ? 16 + 12 * back.length : 0);
    const cols = Math.max(...rank.values()) + 1;
    const W = 30 + cols * CW, H = top + (maxL - minL) * RH + 66;
    const pos = (sid) => ({ x: 30 + R + rank.get(sid) * CW, y: top + (lane.get(sid) - minL) * RH });
    const doneSet = new Set(done);
    const lit = new Set(current ? arcs.filter((a) => a.from === current).map((a) => a.to) : []);
    const parts = [`<svg class="cx-jsvg" viewBox="0 0 ${W} ${H}" style="max-width:${W}px" role="img" aria-labelledby="${id}-t ${id}-d">
      <title id="${id}-t">${esc(w.title)}</title><desc id="${id}-d">${esc(`Stages: ${steps.map((s) => s.label).join("; ")}.${current ? ` Now: ${steps[idx.get(current)].label}.` : ""}`)}</desc>`];
    let loop = 0;
    for (const a of arcs) {
      const p = pos(a.from), q = pos(a.to);
      const on = current && a.from === current;
      const cls = `cx-jl${a.needs ? " dashed" : ""}${on ? " lit" : ""}`;
      if (idx.get(a.to) <= idx.get(a.from)) {
        const y = top - 22 - 12 * loop++;
        parts.push(`<path d="M${p.x} ${p.y - R} C${p.x} ${y} ${q.x} ${y} ${q.x} ${q.y - R}" class="${cls} back"/>`);
      } else if (p.y === q.y) {
        parts.push(`<path d="M${p.x + R} ${p.y} L${q.x - R} ${q.y}" class="${cls}"/>`);
      } else {
        const mx = (p.x + q.x) / 2;
        parts.push(`<path d="M${p.x + R} ${p.y} C${mx} ${p.y} ${mx} ${q.y} ${q.x - R} ${q.y}" class="${cls}"/>`);
      }
    }
    steps.forEach((s, k) => {
      const { x, y } = pos(s.id);
      const cls = s.id === current ? "is-now" : doneSet.has(s.id) ? "is-done" : lit.has(s.id) ? "is-next" : s.kind === "end" ? "is-end" : "";
      const words = wrapWords(s.label, 16);
      const act = interactive ? ` data-stop="${esc(s.id)}" tabindex="0" role="button" aria-label="${esc(`${s.label}${s.id === selected ? ", selected" : ""}`)}"` : "";
      parts.push(`<g class="cx-js ${cls}${s.id === selected ? " is-sel" : ""}${interactive ? " can" : ""}"${act} transform="translate(${x},${y})">
        ${s.id === current ? `<circle r="${R + 7}" class="cx-js-halo"/><text y="${-R - 12}" text-anchor="middle" class="cx-js-now">now</text>` : ""}
        <circle r="${R}" class="cx-js-dot"/>
        ${doneSet.has(s.id) ? `<path d="M-5 0 l3.5 3.5 6.5 -7" class="cx-js-tick"/>` : `<text y="4.5" text-anchor="middle" class="cx-js-n">${k + 1}</text>`}
        ${words.map((wd, j) => `<text y="${R + 17 + j * 14}" text-anchor="middle" class="cx-js-l">${esc(wd)}</text>`).join("")}
      </g>`);
    });
    parts.push(`</svg>`);
    return parts.join("");
  }

  // ================================================================ events
  root.querySelector(".cx-modes").addEventListener("click", (e) => {
    const b = e.target.closest("[data-mode]");
    if (b) { mode = b.dataset.mode; at.step = 0; at.issue = 0; at.leaf = null; show(); }
  });
  picker.addEventListener("click", (e) => {
    const b = e.target.closest("[data-pick]");
    if (b) { pick[mode] = b.dataset.pick; at.step = 0; at.issue = 0; at.leaf = null; at.stop = null; show(); }
  });
  body.addEventListener("click", (e) => {
    const move = e.target.closest("[data-move]");
    if (move) { at.step += Number(move.dataset.move); at.leaf = null; paintMatter(); body.querySelector(".cx-story").scrollIntoView({ behavior: "smooth", block: "nearest" }); return; }
    const step = e.target.closest("[data-step]");
    if (step) { at.step = Number(step.dataset.step); at.leaf = null; paintMatter(); return; }
    const issue = e.target.closest("[data-issue]");
    if (issue) { at.issue = Number(issue.dataset.issue); at.leaf = null; paintMatter(); return; }
    const other = e.target.closest("[data-pick-matter]");
    if (other) { pick.objection = other.dataset.pickMatter; at.issue = 0; at.leaf = null; show(); return; }
    const exc = e.target.closest("[data-goto]");
    if (exc) { const steps = stepsFor(issueNow()); at.step = Math.max(0, steps.findIndex(([id]) => id === exc.dataset.goto)); paintMatter(); return; }
    const tile = e.target.closest("[data-leaf]");
    if (tile && tile.dataset.leaf) {
      // A condition on the picture opens its account in the words, at the step that explains it.
      const steps = stepsFor(issueNow());
      if (steps[at.step][0] !== "looks") { at.step = Math.max(0, steps.findIndex(([id]) => id === "looks")); paintMatter(); }
      markLeaf(tile.dataset.leaf);
      return;
    }
    const stop = e.target.closest("[data-stop]");
    if (stop && mode === "process") { at.stop = stop.dataset.stop; paintProcess(); return; }
    const to = e.target.closest("[data-to]");
    if (to) { at.stop = to.dataset.to; paintProcess(); return; }
    const sm = e.target.closest("[data-stop-move]");
    if (sm) { const w = processes.get(pick.process); const i = w.steps.findIndex((s) => s.id === at.stop); at.stop = w.steps[Math.max(0, Math.min(w.steps.length - 1, i + Number(sm.dataset.stopMove)))].id; paintProcess(); return; }
    const proc = e.target.closest("[data-proc]");
    if (proc) { pick.process = proc.dataset.proc; at.stop = null; show(); }
  });
  body.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const stop = e.target.closest("[data-stop]");
    if (stop && mode === "process") { e.preventDefault(); at.stop = stop.dataset.stop; paintProcess(); body.querySelector(`[data-stop="${CSS.escape(at.stop)}"]`)?.focus(); }
  });
  show();
}

function wrapWords(text, width) {
  const out = [];
  let line = "";
  for (const w of String(text).split(/\s+/)) {
    if ((line + " " + w).trim().length > width && line) { out.push(line); line = w; } else line = (line + " " + w).trim();
  }
  if (line) out.push(line);
  if (out.length > 2) { out.length = 2; out[1] = `${out[1]}…`; }
  return out;
}
