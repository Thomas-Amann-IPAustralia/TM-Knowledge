/* Explore a legal concept: a working demonstration for examiners (ADR-0151).

   One idea at a time, everything the foundation records about it, in one dense view: the
   connections that lead to it on the left and those that lead from it on the right, each saying
   what it says in its predicate's own words (Q-94), with the strength and the condition its
   sentence states; the idea itself in the middle, with its names, the names it must not be
   confused with, and its definition; then the legal tests and procedures that name it, where the
   Manual discusses it, and what it rests on. Selecting a connection shows the sentence it rests
   on; following one makes its other end the focus, and the trail of ideas visited stays on screen.

   Every connection, name and definition is a record that already exists, with who wrote it shown
   beside it; this page arranges them and decides nothing. Classes are prefixed `ce-`. */

import { esc, fmt, load, refChip, refLabel, quoteBlock, trustBadge, qualifiedLine, definitionBlock, sourceOf, isLaw, structureHref, FAMILIES, familyOf } from "./app.js";
import { icon } from "./icons.js";

/** Where a predicate's group sits in its column: the questions examination turns on first. */
const ORDER = ["mayGiveRiseTo", "qualifies", "statesThresholdFor", "constrainsExaminerTo", "isAnExceptionTo", "doesNotGiveRiseTo",
  "requiresElement", "isOvercomeBy", "isAssessedIn", "appliesTo", "broader"];
/** Concepts an examiner is likely to start from; each is shown only if the data holds it. */
const STARTERS = ["GC-0168", "GC-0154", "GC-0059", "GC-0066", "GC-0064", "GC-0007", "GC-0010", "GC-0040"];
const DEFAULT = "GC-0168";
const SHOW = 6;
const PROCEEDING = { application_and_examination: "application and examination", opposition: "opposition", registration: "registration" };

/** The children of a condition group, whichever way the record joins them. */
const kidsOf = (n) => n.all || n.any || n.children || null;
/** Every leaf condition of a test that names a concept, with the test it is in. */
function rolesIn(structures, id) {
  const out = [];
  const walk = (n, t) => { const kids = kidsOf(n); if (kids) kids.forEach((k) => walk(k, t)); else if ((n.concepts || []).includes(id)) out.push({ test: t, leaf: n }); };
  for (const t of structures) {
    if (t.condition) walk(t.condition, t);
    for (const x of t.exceptions || []) if (x.condition) walk(x.condition, t);
  }
  return out;
}

const fold = (s) => String(s || "").toLowerCase().normalize("NFKD").replace(/[‘’']/g, "").replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();

export async function render(root, { ontology, params }) {
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const predicates = ontology.predicates;
  const predLabel = (p) => predicates[p]?.label || ontology.retired_predicates?.[p] || p;
  const fam = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)] || FAMILIES.other;
  const kindLabel = (id) => ontology.kinds.find((k) => k.id === byId.get(id)?.kind)?.label || "";
  const allStructures = [...(ontology.structures?.tests || []), ...(ontology.structures?.processes || [])];
  const degree = new Map();
  for (const r of ontology.relations) for (const end of [r.s, r.o]) degree.set(end, (degree.get(end) || 0) + 1);

  let focus = byId.has(params[0]) ? params[0] : DEFAULT;
  let selected = null;
  const trail = [];
  const expanded = new Set();

  const starters = STARTERS.filter((id) => byId.has(id));
  root.innerHTML = `
  <div class="ce">
    <header class="wrap wide ce-head">
      <div>
        <span class="eyebrow">For examiners · working demonstration</span>
        <h1>Explore a legal concept</h1>
        <p class="lede">Pick a concept to see what the foundation records about it: what can give rise to it, what bears on it, what overcomes it, the legal test it belongs to, and the passages behind each part.</p>
      </div>
      <div class="ce-legend">
        <span><span class="ce-mod must">must</span><span class="ce-mod should">should</span><span class="ce-mod may">may</span> the strength its source states</span>
        <span><svg viewBox="0 0 30 10" aria-hidden="true"><path d="M1 5h28" class="ce-key-line cond"/></svg> holds only in some cases: the source states a condition</span>
        <span><span class="trust machine">AI-written · unreviewed</span> <span class="trust reviewed">Expert reviewed</span></span>
      </div>
    </header>
    <div class="wrap wide ce-bar">
      <div class="ce-find">
        <label class="vh" for="ce-q">Find a concept</label>
        <div class="ce-in">${icon("search")}<input id="ce-q" type="text" autocomplete="off" placeholder="Find any of ${fmt(ontology.concepts.length)} concepts, by any of their names" role="combobox" aria-expanded="false" aria-controls="ce-sugg" aria-autocomplete="list"></div>
        <ul class="ce-sugg" id="ce-sugg" role="listbox" hidden></ul>
      </div>
      <div class="ce-starters"><span class="tiny">Start from</span>${starters.map((id) => `<button type="button" class="chip" data-go="${id}"><i class="dot" style="--c:${fam(id).colour}"></i>${esc(byId.get(id).label)}</button>`).join("")}</div>
    </div>
    <nav class="wrap wide ce-trail" aria-label="Your research trail"></nav>
    <div class="wrap wide ce-main">
      <section class="ce-stage" aria-label="The concept and its connections">
        <svg class="ce-wires" aria-hidden="true"></svg>
        <div class="ce-col ce-in-col"></div>
        <div class="ce-focus"></div>
        <div class="ce-col ce-out-col"></div>
      </section>
      <aside class="ce-side card" aria-live="polite"></aside>
    </div>
    <div class="wrap wide ce-lower">
      <section class="card ce-panel ce-tests"></section>
      <section class="card ce-panel ce-where"></section>
      <section class="card ce-panel ce-rests"></section>
    </div>
  </div>`;

  const stage = root.querySelector(".ce-stage");
  const wires = root.querySelector(".ce-wires");
  const inCol = root.querySelector(".ce-in-col");
  const outCol = root.querySelector(".ce-out-col");
  const focusEl = root.querySelector(".ce-focus");
  const side = root.querySelector(".ce-side");
  const trailEl = root.querySelector(".ce-trail");
  const input = root.querySelector("#ce-q");
  const sugg = root.querySelector(".ce-sugg");

  // ---------------------------------------------------------------- one end of a connection
  const endName = (id) => (byId.has(id) ? byId.get(id).label : refLabel(id));
  const endDot = (id) => (byId.has(id) ? `<i class="ce-dot" style="background:${fam(id).colour}"></i>`
    : `<span class="${isLaw(id) ? `law ${sourceOf(id)}` : "manual"} ce-mk"><i class="mark" aria-hidden="true"></i></span>`);

  function groups(side) {
    const rows = ontology.relations.filter((r) => (side === "in" ? r.o === focus : r.s === focus));
    const by = new Map();
    for (const r of rows) {
      if (!by.has(r.p)) by.set(r.p, []);
      by.get(r.p).push(r);
    }
    const rank = (p) => { const i = ORDER.indexOf(p); return i < 0 ? ORDER.length : i; };
    return [...by.entries()].sort((a, b) => rank(a[0]) - rank(b[0]) || predLabel(a[0]).localeCompare(predLabel(b[0])))
      .map(([p, list]) => [p, list.sort((a, b) => endName(side === "in" ? a.s : a.o).localeCompare(endName(side === "in" ? b.s : b.o)))]);
  }

  function column(side) {
    const list = groups(side);
    if (!list.length) return `<p class="ce-none">${side === "in" ? "No recorded connection leads to this concept." : "No recorded connection leads from this concept."} <span class="tiny">That is what the foundation holds, not a finding that none exist.</span></p>`;
    return list.map(([p, rows]) => {
      const key = `${side}:${p}`;
      const shown = expanded.has(key) ? rows : rows.slice(0, SHOW);
      return `<div class="ce-group">
        <p class="ce-gh">${side === "out" ? `<span class="ce-arrow">→</span>` : ""}<b>${esc(predLabel(p))}</b>${side === "in" ? `<span class="ce-arrow">→</span>` : ""}<span class="ce-n">${fmt(rows.length)}</span></p>
        ${shown.map((r) => pill(r, side)).join("")}
        ${rows.length > shown.length ? `<button type="button" class="ce-more" data-more="${esc(key)}">Show ${fmt(rows.length - shown.length)} more</button>` : ""}
      </div>`;
    }).join("");
  }

  function pill(r, side) {
    const other = side === "in" ? r.s : r.o;
    const conditional = !!(r.when || r.hedge || r.condition === "not_assessed");
    const explore = byId.has(other) ? `<button type="button" class="ce-go" data-go="${esc(other)}" aria-label="Explore ${esc(endName(other))}" title="Explore this concept">${icon("arrow")}</button>` : "";
    return `<div class="ce-pill${conditional ? " cond" : ""}${r.origin === "signed" || r.origin === "approved" ? " rev" : ""}${selected === r.id ? " on" : ""}" data-rel="${esc(r.id)}" data-side="${side}">
      <button type="button" class="ce-pick" data-pick="${esc(r.id)}" aria-pressed="${selected === r.id}" title="${esc(`${endName(r.s)} ${predLabel(r.p)} ${endName(r.o)}`)}">
        ${endDot(other)}<span class="ce-pl">${esc(endName(other))}</span>
        ${r.modality ? `<span class="ce-mod ${esc(r.modality)}">${esc(r.modality)}</span>` : ""}${conditional ? `<span class="ce-if" title="The source states a condition or a hedge">if</span>` : ""}
      </button>${explore}</div>`;
  }

  function focusCard() {
    const c = byId.get(focus);
    const f = fam(focus);
    const tests = (c.structures || []).length;
    return `<div class="ce-card" style="--fc:${f.colour};--fb:${f.bg};--fi:${f.ink}">
      <span class="ce-kind"><i style="background:${f.colour}"></i>${esc(kindLabel(focus))}</span>
      <h2>${esc(c.label)}</h2>
      ${c.alt?.length ? `<p class="ce-names"><span>Also called</span>${c.alt.slice(0, 3).map(esc).join(" · ")}${c.alt.length > 3 ? ` <span class="ce-more-names" title="${esc(c.alt.slice(3).join(" · "))}">and ${fmt(c.alt.length - 3)} more</span>` : ""}</p>` : ""}
      ${c.not?.length ? `<p class="ce-names not"><span>Not to be confused with</span>${c.not.map(esc).join(" · ")}</p>` : ""}
      ${roleLine()}
      <div class="ce-fstats"><span><b>${fmt(degree.get(focus) || 0)}</b> connections</span><span><b>${fmt(c.mentions || 0)}</b> passages name it</span>${tests ? `<span><b>${fmt(tests)}</b> legal test${tests === 1 ? "" : "s"} or procedure${tests === 1 ? "" : "s"}</span>` : ""}</div>
      <p class="ce-who">${trustBadge(c.origin)} <a href="#/map/ideas/${esc(focus)}">On the knowledge map</a></p>
    </div>`;
  }

  /** In a legal test, is this concept something a record settles or something a person judges?
      Read from the tests' own conditions, which name the concepts they turn on. */
  function roleLine() {
    const roles = rolesIn(ontology.structures?.tests || [], focus);
    if (!roles.length) return "";
    const seen = new Set();
    const items = roles.filter((r) => { const k = `${r.test.id}:${r.leaf.kind}`; return seen.has(k) ? false : seen.add(k); });
    return `<div class="ce-role">${items.map((r) => `<span class="ce-role-i ${esc(r.leaf.kind)}"><span class="ce-tk ${esc(r.leaf.kind)}">${r.leaf.kind === "evaluative" ? "Assessment" : "Fact"}</span>
      <span>${r.leaf.kind === "evaluative" ? "a judgement a person makes" : "something a record can confirm"}, in ${esc(r.test.title.replace(/\s*\([^)]*\)\s*$/, ""))} ${r.test.provision ? refChip(r.test.provision) : ""}</span></span>`).join("")}</div>`;
  }

  // ---------------------------------------------------------------- the side panel: the concept, or one connection
  function sidePanel() {
    const c = byId.get(focus);
    if (selected) {
      const r = ontology.relations.find((x) => x.id === selected);
      if (r) {
        const other = r.s === focus ? r.o : r.s;
        return `<div class="ce-side-head"><span class="eyebrow">Why the foundation says this</span><button type="button" class="ce-x" data-unpick aria-label="Close the connection">${icon("close")}</button></div>
          <p class="ce-sent">${endDot(r.s)}<b>${esc(endName(r.s))}</b> <span class="ce-pred">${esc(predLabel(r.p))}</span> ${endDot(r.o)}<b>${esc(endName(r.o))}</b></p>
          <p class="ce-meta">${trustBadge(r.origin)}${r.modality ? ` <span class="ce-mod ${esc(r.modality)}">${esc(r.modality)}</span> <span class="tiny">the strength the sentence states</span>` : ""}</p>
          ${qualifiedLine(r)}
          ${r.proceeding && PROCEEDING[r.proceeding] ? `<p class="small"><b>Applies in:</b> ${esc(PROCEEDING[r.proceeding])}</p>` : ""}
          <h4>The sentence it rests on</h4>
          ${quoteBlock(r.ref, r.quote || "")}
          <p class="ce-ref">${refChip(r.ref, ` data-hl="${esc((r.quote || "").slice(0, 120))}"`)} <span class="tiny">${esc(r.id)}</span></p>
          ${byId.has(other) ? `<button type="button" class="btn small primary" data-go="${esc(other)}">Explore ${esc(endName(other))} ${icon("arrow")}</button>` : `<button type="button" class="btn small" data-ref="${esc(other)}">${icon("book")} Read ${esc(refLabel(other))}</button>`}`;
      }
    }
    return `<div class="ce-side-head"><span class="eyebrow">About this concept</span></div>
      ${definitionBlock(c.definition) || `<p class="small muted">No definition is recorded: the sources do not define this concept.</p>`}
      ${c.basis?.length ? `<h4>Rests on, in the legislation</h4><p class="ce-chips">${c.basis.map((ref) => refChip(ref)).join(" ")}</p>` : ""}
      <p class="small muted ce-hint">${icon("info")}<span>Select a connection to see the sentence it rests on, its strength and any condition. The arrow beside it makes the other concept the focus.</span></p>`;
  }

  // ---------------------------------------------------------------- the lower panels
  function testsPanel() {
    const c = byId.get(focus);
    const items = (c.structures || []).map((id) => allStructures.find((s) => s.id === id)).filter(Boolean);
    const leaf = (n) => {
      const kids = kidsOf(n);
      if (kids) return `<li class="ce-tg"><span class="ce-tj">${n.all ? "All of these" : "Any one of these"}</span>${n.text ? ` ${esc(n.text)}` : ""}<ul>${kids.map(leaf).join("")}</ul></li>`;
      const here = (n.concepts || []).includes(focus);
      return `<li class="${here ? "here" : ""}"><span class="ce-tk ${esc(n.kind)}">${n.kind === "evaluative" ? "Assessment" : "Fact"}</span>${esc(n.text)} ${n.ref ? refChip(n.ref) : ""}${here ? `<span class="ce-here">names this concept</span>` : ""}</li>`;
    };
    const test = (t) => `<div class="ce-test">
      <p class="ce-test-h"><b>${esc(t.title)}</b> ${t.provision ? refChip(t.provision) : ""} ${trustBadge(t.origin)}</p>
      ${t.condition ? `<ul class="ce-tree">${leaf(t.condition)}</ul>` : ""}
      ${t.effect ? `<p class="small"><b>Then</b> ${esc(t.effect.text || "")}</p>` : ""}
      ${(t.exceptions || []).length ? `<p class="small"><b>Unless</b> ${t.exceptions.map((x) => esc(x.text)).join("; ")}</p>` : ""}
      <p class="ce-test-go"><a class="link-arrow" href="${structureHref(t.id)}">Set out in full ${icon("arrow")}</a>${t.id.startsWith("GL-") ? `<a class="link-arrow" href="#/customers/requirements/${esc(t.id)}">As explained to applicants ${icon("arrow")}</a>` : ""}</p></div>`;
    const proc = (p) => `<div class="ce-test">
      <p class="ce-test-h"><b>${esc(p.title)}</b> ${trustBadge(p.origin)}</p>
      <ol class="ce-steps">${(p.steps || []).map((s) => `<li>${esc(s.label)}</li>`).join("")}</ol>
      <p class="ce-test-go"><a class="link-arrow" href="${structureHref(p.id)}">Set out in full ${icon("arrow")}</a></p></div>`;
    return `<h3>${icon("scale")}In a legal test or procedure</h3>
      ${items.length ? `<p class="tiny">Each condition says whether it is a <b>fact</b> a record can confirm or an <b>assessment</b> a person must make. Nothing here evaluates either.</p>${items.map((s) => (s.id.startsWith("GP-") ? proc(s) : test(s))).join("")}`
        : `<p class="small muted">No legal test or procedure set out so far names this concept. ${fmt(ontology.counts.tests)} legal tests and ${fmt(ontology.counts.processes)} procedures are set out to date.</p>`}`;
  }

  async function wherePanel(target) {
    target.innerHTML = `<h3>${icon("book")}Where the Manual discusses it</h3><p class="tiny">Loading…</p>`;
    let search, tour;
    const want = focus;
    try { [search, tour] = await Promise.all([load("search"), load("tour")]); } catch { target.innerHTML = `<h3>${icon("book")}Where the Manual discusses it</h3><p class="small muted">Not available in this version.</p>`; return; }
    if (want !== focus) return;

    const refs = search.mentions[focus] || [];
    const parts = new Map();
    for (const ref of refs) {
      const m = /^TMM\/(Part[0-9]+[A-Za-z]*)/.exec(ref);
      const key = m ? m[1] : "Other";
      if (!parts.has(key)) parts.set(key, []);
      parts.get(key).push(ref);
    }
    const titles = new Map((tour.parts || []).map((p) => [p.id, p.title]));
    const rows = [...parts.entries()].sort((a, b) => b[1].length - a[1].length);
    const max = Math.max(1, ...rows.map(([, l]) => l.length));
    const generic = (search.generic || []).includes(focus);
    target.innerHTML = `<h3>${icon("book")}Where the Manual discusses it</h3>
      <p class="tiny">${fmt(refs.length)} passages in ${fmt(rows.length)} Parts name it, by any of its names.${generic ? " It is named so widely that search does not use it to steer." : ""} Select a Part to list its passages.</p>
      <ul class="ce-parts">${rows.slice(0, 10).map(([part, list]) => `<li><button type="button" class="ce-part" data-part="${esc(part)}" aria-expanded="false">
        <span class="ce-part-t">${esc(titles.get(part) || part)}</span><span class="ce-pbar"><i style="width:${((list.length / max) * 100).toFixed(1)}%"></i></span><span class="ce-part-n">${fmt(list.length)}</span></button>
        <div class="ce-part-list" hidden>${list.slice(0, 24).map((ref) => refChip(ref, ` data-hl="${esc([byId.get(focus).label, ...(byId.get(focus).alt || [])].join("|"))}"`)).join(" ")}${list.length > 24 ? ` <span class="tiny">and ${fmt(list.length - 24)} more</span>` : ""}</div></li>`).join("")}</ul>
      ${rows.length > 10 ? `<p class="tiny">and ${fmt(rows.length - 10)} more Parts</p>` : ""}
      ${!rows.length ? `<p class="small muted">No passage names it.</p>` : ""}`;
  }

  function restsPanel() {
    const c = byId.get(focus);
    const sources = c.sources || [];
    return `<h3>${icon("file")}What the record rests on</h3>
      <p class="tiny">The passages the concept's own record cites, and its basis in the legislation.</p>
      ${c.basis?.length ? `<p class="ce-rl">The law</p><p class="ce-chips">${c.basis.map((ref) => refChip(ref)).join(" ")}</p>` : ""}
      ${sources.length ? `<p class="ce-rl">The Manual</p><p class="ce-chips">${sources.map((ref) => refChip(ref)).join(" ")}</p>` : ""}
      ${!sources.length && !c.basis?.length ? `<p class="small muted">The record cites no passage.</p>` : ""}
      <p class="ce-rl">Who wrote it</p><p class="small">${trustBadge(c.origin)} ${c.typed ? `<span class="tiny">Its kind was judged by a machine (${esc(c.typed.by)}, ${esc(c.typed.date)}), unreviewed.</span>` : ""}</p>
      ${(c.hierarchy?.kind_of || []).length || (c.hierarchy?.kinds || []).length ? `<p class="ce-rl">Broader and narrower</p><p class="ce-chips">${[...(c.hierarchy.kind_of || []).map((i) => ["Broader", i]), ...(c.hierarchy.kinds || []).map((i) => ["Narrower", i])]
        .filter(([, i]) => byId.has(i.id)).map(([w, i]) => `<button type="button" class="chip" data-go="${esc(i.id)}"><span class="tiny">${w}</span> ${esc(byId.get(i.id).label)}</button>`).join(" ")}</p>` : ""}`;
  }

  // ---------------------------------------------------------------- drawing and wiring
  function draw() {
    // Measured after layout, never in the first pass (Q-63).
    const box = stage.getBoundingClientRect();
    if (!box.width) return;
    const card = focusEl.querySelector(".ce-card")?.getBoundingClientRect();
    if (!card) return;
    wires.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    // Each side's wires meet the card spread along its edge, in the pills' own order, so they fan
    // out instead of piling into one point.
    const ends = new Map();
    for (const side of ["in", "out"]) {
      const pills = [...stage.querySelectorAll(`.ce-pill[data-side="${side}"]`)];
      const lo = card.top + Math.min(26, card.height / 4), hi = card.bottom - Math.min(26, card.height / 4);
      pills.forEach((el, i) => ends.set(el, (pills.length === 1 ? (lo + hi) / 2 : lo + ((hi - lo) * i) / (pills.length - 1)) - box.top));
    }
    const out = [];
    stage.querySelectorAll(".ce-pill").forEach((el) => {
      const r = el.getBoundingClientRect();
      const y = r.top + r.height / 2 - box.top;
      const cy = ends.get(el);
      const on = el.classList.contains("on");
      const cls = `ce-wire${el.classList.contains("cond") ? " cond" : ""}${on ? " on" : ""}`;
      if (el.dataset.side === "in") {
        const x1 = r.right - box.left, x2 = card.left - box.left;
        const mx = (x1 + x2) / 2;
        out.push(`<path d="M${x1.toFixed(1)} ${y.toFixed(1)} C${mx.toFixed(1)} ${y.toFixed(1)} ${mx.toFixed(1)} ${cy.toFixed(1)} ${x2.toFixed(1)} ${cy.toFixed(1)}" class="${cls}"/>`);
      } else {
        const x1 = card.right - box.left, x2 = r.left - box.left;
        const mx = (x1 + x2) / 2;
        out.push(`<path d="M${x1.toFixed(1)} ${cy.toFixed(1)} C${mx.toFixed(1)} ${cy.toFixed(1)} ${mx.toFixed(1)} ${y.toFixed(1)} ${x2.toFixed(1)} ${y.toFixed(1)}" class="${cls}"/>`);
      }
    });
    wires.innerHTML = out.join("");
  }

  function paintTrail() {
    trailEl.innerHTML = trail.length > 1 ? `<span class="tiny">Your research trail</span><ol>${trail.map((id, i) => `<li>${i === trail.length - 1
      ? `<b aria-current="true">${esc(byId.get(id).label)}</b>` : `<button type="button" class="link" data-go="${esc(id)}">${esc(byId.get(id).label)}</button>`}</li>`).join("")}</ol>` : "";
  }

  function show(id, { push = true } = {}) {
    if (!byId.has(id)) return;
    focus = id;
    selected = null;
    expanded.clear();
    if (push) {
      const at = trail.indexOf(id);
      if (at >= 0) trail.splice(at + 1); else trail.push(id);
      if (trail.length > 9) trail.shift();
    }
    history.replaceState(null, "", `#/concepts/${encodeURIComponent(id)}`);
    paint();
    root.querySelector(".ce-tests").innerHTML = testsPanel();
    root.querySelector(".ce-rests").innerHTML = restsPanel();
    wherePanel(root.querySelector(".ce-where"));
    paintTrail();
  }

  function paint() {
    inCol.innerHTML = column("in");
    outCol.innerHTML = column("out");
    focusEl.innerHTML = focusCard();
    side.innerHTML = sidePanel();
    stage.classList.remove("ce-in-anim"); void stage.offsetWidth; stage.classList.add("ce-in-anim");
    requestAnimationFrame(draw);
  }

  // ---------------------------------------------------------------- finding a concept by any of its names
  const names = ontology.concepts.flatMap((c) => [c.label, ...(c.alt || [])].map((n) => ({ id: c.id, name: n, f: fold(n), main: n === c.label })));
  let active = -1;
  function suggest() {
    const q = fold(input.value);
    if (q.length < 2) { sugg.hidden = true; input.setAttribute("aria-expanded", "false"); return; }
    const seen = new Set();
    const hits = names.filter((n) => n.f.includes(q))
      .sort((a, b) => (b.f.startsWith(q) - a.f.startsWith(q)) || (b.main - a.main) || a.name.length - b.name.length)
      .filter((n) => (seen.has(n.id) ? false : seen.add(n.id))).slice(0, 8);
    active = hits.length ? 0 : -1;
    sugg.innerHTML = hits.length ? hits.map((n, i) => `<li role="option" id="ce-o-${i}" aria-selected="${i === active}" data-go="${esc(n.id)}">
      <i class="ce-dot" style="background:${fam(n.id).colour}"></i><b>${esc(byId.get(n.id).label)}</b>${n.main ? "" : `<span class="tiny">also called “${esc(n.name)}”</span>`}<span class="tiny ce-sk">${esc(kindLabel(n.id))}</span></li>`).join("")
      : `<li class="ce-nohit">No concept goes by that name. Try fewer words.</li>`;
    sugg.hidden = false;
    input.setAttribute("aria-expanded", "true");
    input.setAttribute("aria-activedescendant", active >= 0 ? `ce-o-${active}` : "");
  }
  input.addEventListener("input", suggest);
  input.addEventListener("keydown", (e) => {
    const opts = [...sugg.querySelectorAll("[data-go]")];
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!opts.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + opts.length) % opts.length;
      opts.forEach((o, i) => o.setAttribute("aria-selected", String(i === active)));
      input.setAttribute("aria-activedescendant", `ce-o-${active}`);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (opts[active]) { show(opts[active].dataset.go); input.value = ""; sugg.hidden = true; }
    } else if (e.key === "Escape") { sugg.hidden = true; input.setAttribute("aria-expanded", "false"); }
  });
  input.addEventListener("blur", () => setTimeout(() => { sugg.hidden = true; input.setAttribute("aria-expanded", "false"); }, 150));

  // ---------------------------------------------------------------- one listener for the page
  root.addEventListener("click", (e) => {
    const go = e.target.closest("[data-go]");
    if (go) { e.preventDefault(); input.value = ""; sugg.hidden = true; show(go.dataset.go); window.scrollTo({ top: Math.min(window.scrollY, root.querySelector(".ce-bar").offsetTop - 80), behavior: "smooth" }); return; }
    const pick = e.target.closest("[data-pick]");
    if (pick) {
      selected = selected === pick.dataset.pick ? null : pick.dataset.pick;
      stage.querySelectorAll(".ce-pill").forEach((p) => { p.classList.toggle("on", p.dataset.rel === selected); p.querySelector(".ce-pick").setAttribute("aria-pressed", String(p.dataset.rel === selected)); });
      side.innerHTML = sidePanel();
      draw();
      return;
    }
    if (e.target.closest("[data-unpick]")) { selected = null; stage.querySelectorAll(".ce-pill").forEach((p) => p.classList.remove("on")); side.innerHTML = sidePanel(); draw(); return; }
    const more = e.target.closest("[data-more]");
    if (more) { expanded.add(more.dataset.more); inCol.innerHTML = column("in"); outCol.innerHTML = column("out"); requestAnimationFrame(draw); return; }
    const part = e.target.closest("[data-part]");
    if (part) {
      const list = part.nextElementSibling;
      list.hidden = !list.hidden;
      part.setAttribute("aria-expanded", String(!list.hidden));
    }
  });
  stage.addEventListener("mouseover", (e) => {
    const p = e.target.closest(".ce-pill");
    stage.querySelectorAll(".ce-pill.hot").forEach((x) => x.classList.remove("hot"));
    if (p) p.classList.add("hot");
    const paths = wires.querySelectorAll("path");
    const pills = [...stage.querySelectorAll(".ce-pill")];
    paths.forEach((path, i) => path.classList.toggle("hot", !!p && pills[i] === p));
  });
  const ro = new ResizeObserver(() => draw());
  ro.observe(stage);
  show(focus);
  return () => ro.disconnect();
}

/** A small preview of a concept's connections, for the examiners' overview: the groups on each
    side and their counts, from the same records. */
export function preview(ontology, id = DEFAULT) {
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const c = byId.get(id);
  if (!c) return "";
  const label = (p) => ontology.predicates[p]?.label || p;
  const count = (side) => {
    const m = new Map();
    for (const r of ontology.relations) if ((side === "in" ? r.o : r.s) === id) m.set(r.p, (m.get(r.p) || 0) + 1);
    return [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4);
  };
  const fam = FAMILIES[familyOf(ontology, c.kind)] || FAMILIES.other;
  return `<a class="ce-prev" href="#/concepts/${esc(id)}" aria-label="Explore ${esc(c.label)}">
    <div class="ce-prev-col">${count("in").map(([p, n]) => `<span><b>${fmt(n)}</b> ${esc(label(p))} →</span>`).join("")}</div>
    <div class="ce-prev-mid" style="--fc:${fam.colour};--fb:${fam.bg}"><span class="ce-kind"><i style="background:${fam.colour}"></i>${esc(ontology.kinds.find((k) => k.id === c.kind)?.label || "")}</span><b>${esc(c.label)}</b></div>
    <div class="ce-prev-col out">${count("out").map(([p, n]) => `<span>→ ${esc(label(p))} <b>${fmt(n)}</b></span>`).join("")}</div>
  </a>`;
}
