/* The map — the ontology at three levels of detail.

   1. Kinds   — the nine kinds of idea, and the patterns the connections between
                their members make once rolled up (`kind_links`, computed by
                tmk-explorer from the relationship records).
   2. Ideas   — every concept, clustered round its kind, with its connections.
   3. Text    — one idea opened into the passages that name it and the
                provisions it rests on, the Manual and the legislation apart.

   The same nodes move between levels, so a reader can watch a kind open into its
   ideas and an idea into its text. Nothing here decides which nodes or edges
   exist: that is the records', arranged by Python. */

import { esc, fmt, el, load, kindColour, refChip, refLabel, trustBadge, kindChip, legend, isLaw } from "./app.js";
import { svg, forceLayout, panZoom, tween, curve, arrowDefs, wrapText } from "./graph.js";

export const W = 1000, H = 660;
export const KIND_POS = {
  relevant_factor: { x: 135, y: 215 }, legal_test: { x: 380, y: 215 },
  ground_of_refusal: { x: 380, y: 490 }, exception: { x: 135, y: 490 },
  process_role: { x: 630, y: 185 }, procedural_step: { x: 868, y: 290 },
  subject_matter: { x: 640, y: 435 }, instrument_or_record: { x: 872, y: 535 },
  external_instrument: { x: 655, y: 600 }, none_of_these: { x: 500, y: 598 },
};
export const ZONES = [
  { family: "reasoning", x: 30, y: 80, w: 460, h: 520, label: "Reasoning towards a decision" },
  { family: "process", x: 515, y: 80, w: 460, h: 565, label: "The process it sits inside" },
];
const LOOSE = new Set(["related", "broader"]);

export const kindRadius = (k) => 24 + 7 * Math.sqrt(k.signed + k.machine);
const conceptRadius = (c) => Math.min(11, 3.5 + 1.4 * Math.log2(1 + c.mentions));
export const specificCount = (row) => row.total - (row.predicates.related || 0) - (row.predicates.broader || 0);

let positions = null;

/** Where each concept sits on the ideas level: clustered round its kind. */
export function conceptPositions(ontology) {
  if (positions) return positions;
  const nodes = ontology.concepts.map((c) => {
    const at = KIND_POS[c.kind] || KIND_POS.none_of_these;
    return { id: c.id, r: conceptRadius(c) + 3, ax: at.x, ay: at.y, pull: 0.055 };
  });
  const ids = new Set(nodes.map((n) => n.id));
  const links = ontology.relations.filter((r) => ids.has(r.s) && ids.has(r.o))
    .map((r) => ({ s: r.s, t: r.o, w: LOOSE.has(r.p) ? 0.1 : 0.4 }));
  forceLayout(nodes, links, { width: W, height: H, charge: 110, linkDistance: 40, linkStrength: 0.008, iterations: 420, seed: 23, padding: 3 });
  positions = new Map(nodes.map((n) => [n.id, { x: n.x, y: n.y }]));
  return positions;
}

/** Draw the kinds level into `g`. Used by the map and by the tour. */
export function drawKinds(g, ontology, { strongOnly = true, onKind = null, onLink = null, minimal = false } = {}) {
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  if (!minimal) {
    for (const z of ZONES) {
      svg("rect", { x: z.x, y: z.y, width: z.w, height: z.h, rx: 18, class: "family-zone" }, g);
      svg("text", { x: z.x + 16, y: z.y + 24, class: "family-label" }, g).textContent = z.label;
    }
  }
  const links = svg("g", {}, g);
  const labels = svg("g", {}, g);
  const within = new Map();
  for (const row of ontology.kind_links) {
    if (row.s === row.o) { within.set(row.s, row); continue; }
    const strong = specificCount(row);
    if (strongOnly && strong < 5) continue;
    const a = KIND_POS[row.s], b = KIND_POS[row.o];
    const ka = kinds.get(row.s), kb = kinds.get(row.o);
    const c = curve(a, b, kindRadius(ka) + 4, kindRadius(kb) + 8, 0.12);
    const width = 1 + 1.5 * Math.log2(1 + (strongOnly ? strong : row.total));
    const path = svg("path", { d: c.d, class: "kind-link", "stroke-width": width.toFixed(1), "marker-end": "url(#arrow)", "data-s": row.s, "data-o": row.o }, links);
    const top = Object.entries(row.predicates).find(([p]) => !LOOSE.has(p)) || Object.entries(row.predicates)[0];
    const name = ontology.predicates[top[0]]?.label || top[0];
    svg("title", {}, path).textContent = `${ka.label} → ${kb.label}: ${row.total} connections`;
    if (strong >= 8 || (!strongOnly && !minimal && row.total >= 12)) {
      svg("text", { x: c.mx.toFixed(1), y: (c.my + 4).toFixed(1), class: "kind-link-label" }, labels).textContent = `${name} · ${top[1]}`;
    }
    if (onLink) path.addEventListener("click", () => onLink(row));
  }
  for (const k of ontology.kinds) {
    const at = KIND_POS[k.id];
    const r = kindRadius(k);
    const node = svg("g", { class: "kind-bubble", transform: `translate(${at.x},${at.y})`, style: `--c:${kindColour(k.id)}`, tabindex: 0, role: "button", "aria-label": `${k.label}: ${k.signed + k.machine} ideas`, "data-kind": k.id }, g);
    svg("circle", { r, class: "body" }, node);
    const lines = wrapText(k.label, 12, 2);
    lines.forEach((line, i) => {
      svg("text", { y: (i - (lines.length - 1) / 2) * 16 - 2, class: "name" }, node).textContent = line;
    });
    const inner = within.get(k.id);
    svg("text", { y: r + 15, class: "count" }, node).textContent =
      `${k.signed + k.machine} ideas` + (inner ? ` · ${inner.total} link${inner.total === 1 ? "" : "s"} inside` : "");
    svg("title", {}, node).textContent = `${k.label} — ${k.plain}`;
    if (onKind) {
      node.addEventListener("click", () => onKind(k));
      node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onKind(k); } });
    }
  }
}

// ---------------------------------------------------------------------- the view

export async function render(root, { ontology, params }) {
  const level0 = ["kinds", "ideas", "text"].includes(params[0]) ? params[0] : "kinds";
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  const relOf = new Map();
  for (const r of ontology.relations) {
    for (const end of [r.s, r.o]) { if (!relOf.has(end)) relOf.set(end, []); relOf.get(end).push(r); }
  }
  const stability = await load("stability");
  const state = { level: level0, concept: params[1] && byId.has(params[1]) ? params[1] : null, kind: null,
    signedOnly: false, loose: false, allKindLinks: false };
  const c = ontology.counts;
  const totalPassages = stability.pages.reduce((n, p) => n + p.passages, 0);

  root.innerHTML = `
  <div class="map-shell">
    <div class="map-rail">
      <div class="rail-ladder" role="tablist" aria-label="Level of detail">
        ${lvl("kinds", 1, "Kinds of idea", `${ontology.kinds.length - 1} kinds, and how their members connect`, "Rests on no single passage")}
        ${lvl("ideas", 2, "Ideas and connections", `${fmt(c.concepts.signed + c.concepts.machine)} ideas · ${fmt(c.relations.signed + c.relations.machine)} connections`, "Each pinned to a quoted passage")}
        ${lvl("text", 3, "The text", `${fmt(totalPassages)} Manual passages · the Act and Regulations`, `${fmt(stability.events)} amendments since ${Object.keys(stability.by_year)[0]}`)}
      </div>
      <div class="rail-box">
        <h4>Find an idea</h4>
        <input class="find" type="search" placeholder="e.g. connotation, consent, opposition" aria-label="Find an idea">
        <div class="find-results"></div>
      </div>
      <div class="rail-box filters">
        <h4>Show</h4>
        <label><input type="checkbox" data-f="signedOnly"> Only what an expert signed</label>
        <label><input type="checkbox" data-f="loose"> Loose "is related to" links</label>
        <label class="only-kinds"><input type="checkbox" data-f="allKindLinks"> Every link between kinds</label>
      </div>
      <div class="rail-box">${legend()}</div>
    </div>
    <div class="canvas-wrap">
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="The ontology map"></svg>
      <div class="canvas-title"><b></b><span></span></div>
      <div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button><button type="button" data-z="reset" aria-label="Reset view">⟲</button></div>
    </div>
    <aside class="side" aria-live="polite"></aside>
  </div>`;

  const svgEl = root.querySelector(".canvas-wrap > svg");
  arrowDefs(svgEl);
  const viewport = svg("g", {}, svgEl);
  const side = root.querySelector(".side");
  const title = root.querySelector(".canvas-title");
  let nodeEls = new Map();
  let edgeEls = [];
  let labelEls = new Map();

  const zoomer = panZoom(svgEl, viewport, { onChange: (s) => updateLabels(s.k) });
  root.querySelector(".zoom").addEventListener("click", (e) => {
    const z = e.target.closest("button")?.dataset.z;
    if (z === "in") zoomer.zoom(1.35); else if (z === "out") zoomer.zoom(1 / 1.35); else if (z === "reset") zoomer.reset();
  });

  // --------------------------------------------------------- levels

  function setLevel(level, { animate = true } = {}) {
    if (level === "text" && !state.concept) state.concept = defaultConcept();
    state.level = level;
    root.querySelectorAll(".lvl").forEach((b) => { b.classList.toggle("on", b.dataset.level === level); b.setAttribute("aria-selected", b.dataset.level === level); });
    root.querySelector(".only-kinds").style.display = level === "kinds" ? "" : "none";
    const hash = `#/map/${level}${state.concept && level !== "kinds" ? "/" + state.concept : ""}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
    if (level === "kinds") drawKindsLevel(animate);
    else if (level === "ideas") drawIdeasLevel(animate);
    else drawTextLevel(animate);
  }

  function defaultConcept() {
    return [...ontology.concepts].filter((x) => x.origin === "signed").sort((a, b) => (relOf.get(b.id) || []).length - (relOf.get(a.id) || []).length)[0].id;
  }

  function clear() {
    viewport.innerHTML = "";
    nodeEls = new Map(); edgeEls = []; labelEls = new Map();
  }

  function drawKindsLevel(animate) {
    clear();
    zoomer.reset();
    title.querySelector("b").textContent = "Nine kinds of idea";
    title.querySelector("span").textContent = "Each bubble holds the ideas of one kind. Arrows are the patterns the connections between them make. Click a bubble or an arrow.";
    const g = svg("g", {}, viewport);
    drawKinds(g, filteredOntology(), {
      strongOnly: !state.allKindLinks,
      onKind: (k) => { state.kind = k.id; showKind(k); highlightKind(k.id); },
      onLink: (row) => showKindLink(row),
    });
    if (animate) tween(450, (t) => g.setAttribute("opacity", t));
    if (state.kind) highlightKind(state.kind); else showLevelHelp();
  }

  function highlightKind(kind) {
    viewport.querySelectorAll(".kind-bubble").forEach((n) => n.classList.toggle("hot", n.dataset.kind === kind));
    viewport.querySelectorAll(".kind-link").forEach((p) => p.classList.toggle("hot", p.dataset.s === kind || p.dataset.o === kind));
  }

  function filteredOntology() {
    if (!state.signedOnly) return ontology;
    const keep = new Set(ontology.concepts.filter((x) => x.origin === "signed").map((x) => x.id));
    const rolled = new Map();
    for (const r of ontology.relations) {
      if (r.origin !== "signed" || !keep.has(r.s) || !keep.has(r.o)) continue;
      const a = byId.get(r.s).kind, b = byId.get(r.o).kind;
      const key = a + ">" + b;
      if (!rolled.has(key)) rolled.set(key, { s: a, o: b, total: 0, signed: 0, machine: 0, predicates: {}, examples: [] });
      const row = rolled.get(key);
      row.total++; row.signed++; row.predicates[r.p] = (row.predicates[r.p] || 0) + 1;
      if (row.examples.length < 6) row.examples.push(r.id);
    }
    return { ...ontology, kinds: ontology.kinds.map((k) => ({ ...k, machine: 0 })), kind_links: [...rolled.values()] };
  }

  function drawIdeasLevel(animate) {
    clear();
    const pos = conceptPositions(ontology);
    title.querySelector("b").textContent = state.kind ? `${kinds.get(state.kind).label}: its ideas` : "Ideas and their connections";
    title.querySelector("span").textContent = "Filled circles were signed by an expert; dashed ones were written by a machine. Click an idea to see what it rests on.";
    for (const k of ontology.kinds) {
      const at = KIND_POS[k.id];
      svg("text", { x: at.x, y: at.y - kindRadius(k) - 14, class: "kind-watermark", fill: kindColour(k.id) }, viewport).textContent = k.label;
    }
    const edgeG = svg("g", {}, viewport);
    const nodeG = svg("g", {}, viewport);
    const visible = ontology.concepts.filter((x) => !state.signedOnly || x.origin === "signed");
    const visibleIds = new Set(visible.map((x) => x.id));
    for (const r of ontology.relations) {
      if (!visibleIds.has(r.s) || !visibleIds.has(r.o)) continue;
      if (state.signedOnly && r.origin !== "signed") continue;
      if (LOOSE.has(r.p) && !state.loose) continue;
      const a = pos.get(r.s), b = pos.get(r.o);
      const path = svg("path", { class: `edge ${r.origin}${LOOSE.has(r.p) ? " loose" : ""}`, "stroke-width": r.origin === "signed" ? 1.8 : 0.9 }, edgeG);
      path.dataset.s = r.s; path.dataset.o = r.o; path.dataset.id = r.id;
      edgeEls.push({ el: path, r, a, b });
    }
    const degree = new Map();
    for (const { r } of edgeEls) { degree.set(r.s, (degree.get(r.s) || 0) + 1); degree.set(r.o, (degree.get(r.o) || 0) + 1); }
    // Label only the best-connected few until the reader zooms in.
    const labelled = new Set([...degree.entries()].sort((a, b) => b[1] - a[1]).slice(0, 14).map(([id]) => id));
    for (const concept of visible) {
      const p = pos.get(concept.id);
      const at = KIND_POS[concept.kind] || KIND_POS.none_of_these;
      const g = svg("g", { class: `node ${concept.origin}`, style: `--c:${kindColour(concept.kind)}`, tabindex: 0, role: "button", "aria-label": `${concept.label}, ${kinds.get(concept.kind)?.label}` }, nodeG);
      g.dataset.id = concept.id;
      svg("circle", { r: conceptRadius(concept) + 4, class: "halo", fill: "none" }, g);
      svg("circle", { r: conceptRadius(concept), class: "body" }, g);
      const text = svg("text", { x: conceptRadius(concept) + 3, y: 4 }, g);
      text.textContent = concept.label;
      svg("title", {}, g).textContent = `${concept.label} — ${concept.origin === "signed" ? "signed by an expert" : "machine-written, unreviewed"}`;
      labelEls.set(concept.id, { text, important: labelled.has(concept.id) });
      nodeEls.set(concept.id, { g, p, from: animate ? at : p });
      g.addEventListener("click", () => selectConcept(concept.id));
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectConcept(concept.id); } });
      g.addEventListener("mouseenter", () => hoverConcept(concept.id));
      g.addEventListener("mouseleave", () => hoverConcept(null));
    }
    const place = (t) => {
      for (const { g, p, from } of nodeEls.values()) {
        g.setAttribute("transform", `translate(${(from.x + (p.x - from.x) * t).toFixed(1)},${(from.y + (p.y - from.y) * t).toFixed(1)})`);
      }
      for (const e of edgeEls) {
        const fa = nodeEls.get(e.r.s).from, fb = nodeEls.get(e.r.o).from;
        const a = { x: fa.x + (e.a.x - fa.x) * t, y: fa.y + (e.a.y - fa.y) * t };
        const b = { x: fb.x + (e.b.x - fb.x) * t, y: fb.y + (e.b.y - fb.y) * t };
        e.el.setAttribute("d", curve(a, b, 0, 0, 0.08).d);
        e.el.setAttribute("opacity", t);
      }
    };
    tween(animate ? 900 : 0, place);
    updateLabels(zoomer.state.k);
    if (state.kind && !state.concept) { const at = KIND_POS[state.kind]; zoomer.focus(at.x, at.y, 1.9); }
    else if (state.concept) { const p = pos.get(state.concept); if (p) zoomer.focus(p.x, p.y, 1.5); }
    else zoomer.reset();
    if (state.concept) selectConcept(state.concept, { keepView: true }); else showLevelHelp();
  }

  function updateLabels(k) {
    for (const [id, { text, important }] of labelEls) {
      const show = important || k > 1.7 || id === state.concept;
      text.style.display = show ? "" : "none";
    }
  }

  function hoverConcept(id) {
    if (state.concept && !id) { highlight(state.concept); return; }
    highlight(id);
  }

  function highlight(id) {
    if (!id) {
      nodeEls.forEach(({ g }) => g.classList.remove("dim", "hot", "sel"));
      edgeEls.forEach(({ el: e }) => e.classList.remove("dim", "hot"));
      updateLabels(zoomer.state.k);
      return;
    }
    const near = new Set([id]);
    for (const { el: e, r } of edgeEls) {
      const on = r.s === id || r.o === id;
      e.classList.toggle("hot", on); e.classList.toggle("dim", !on);
      if (on) { near.add(r.s); near.add(r.o); }
    }
    nodeEls.forEach(({ g }, nid) => {
      g.classList.toggle("dim", !near.has(nid));
      g.classList.toggle("hot", near.has(nid));
      g.classList.toggle("sel", nid === state.concept);
    });
    for (const [nid, { text, important }] of labelEls) text.style.display = near.has(nid) || important || zoomer.state.k > 1.7 ? "" : "none";
  }

  function selectConcept(id, { keepView = false } = {}) {
    state.concept = id;
    if (state.level === "kinds") { setLevel("ideas"); return; }
    if (state.level === "ideas") {
      highlight(id);
      if (!keepView) { const p = conceptPositions(ontology).get(id); if (p) zoomer.focus(p.x, p.y, Math.max(zoomer.state.k, 1.5)); }
      history.replaceState(null, "", `#/map/ideas/${id}`);
    }
    if (state.level === "text") drawTextLevel(true);
    showConcept(byId.get(id));
  }

  // --------------------------------------------------------- the text level

  async function drawTextLevel(animate) {
    clear();
    zoomer.reset();
    const concept = byId.get(state.concept);
    history.replaceState(null, "", `#/map/text/${concept.id}`);
    title.querySelector("b").textContent = `${concept.label}: the text it rests on`;
    title.querySelector("span").textContent = "Left, the Manual's passages that name this idea, by Part. Right, the provisions of the Act and Regulations it rests on. Solid squares are passages a record quotes as evidence.";
    const search = await load("search");
    const refs = [...new Set(search.mentions[concept.id] || [])];
    const evidence = new Set([...concept.evidence.map((e) => e.ref), ...concept.sources]);
    for (const r of relOf.get(concept.id) || []) if (r.ref) evidence.add(r.ref);
    const laws = [...new Set([...concept.basis, ...(relOf.get(concept.id) || []).flatMap((r) => [r.s, r.o]).filter(isLaw)])];
    for (const ref of evidence) if (!isLaw(ref) && !refs.includes(ref)) refs.push(ref);

    const centre = { x: 560, y: 330 };
    const hub = svg("g", { class: `node ${concept.origin}`, style: `--c:${kindColour(concept.kind)}`, transform: `translate(${centre.x},${centre.y})` }, viewport);
    svg("circle", { r: 26, class: "body" }, hub);
    wrapText(concept.label, 16, 3).forEach((line, i) => svg("text", { x: 0, y: 44 + i * 14, "text-anchor": "middle", style: "font-size:13px;font-weight:600" }, hub).textContent = line);

    // Manual passages: a block per Part, laid out in columns on the left.
    svg("text", { x: 40, y: 62, class: "family-label" }, viewport).textContent = `Manual — practice · ${refs.length} passages`;
    const byPart = new Map();
    for (const ref of refs) {
      const part = (ref.match(/^TMM\/(Part[0-9]+[A-Za-z]*)/) || [])[1] || "?";
      if (!byPart.has(part)) byPart.set(part, []);
      byPart.get(part).push(ref);
    }
    const parts = [...byPart.entries()].sort((a, b) => b[1].length - a[1].length);
    const cell = 11, gap = 3, cols = 8;
    let x = 40, y = 80, colMax = 0;
    const lines = svg("g", {}, viewport);
    const squares = svg("g", {}, viewport);
    const shown = [];
    for (const [part, list] of parts) {
      const rows = Math.ceil(list.length / cols);
      const blockH = 16 + rows * (cell + gap);
      if (y + blockH > H - 20) { x += cols * (cell + gap) + 26; y = 80; }
      if (x > 470) break;
      svg("text", { x, y: y + 10, class: "kind-link-label", style: "text-anchor:start" }, squares).textContent = `${part.replace("Part", "Part ")} · ${list.length}`;
      list.forEach((ref, i) => {
        const cx = x + (i % cols) * (cell + gap), cy = y + 16 + Math.floor(i / cols) * (cell + gap);
        const g = svg("g", { class: `psg manual${evidence.has(ref) ? " found" : ""}`, "data-ref": ref, "data-hl": [concept.label, ...concept.alt].join("|") }, squares);
        svg("rect", { x: cx, y: cy, width: cell, height: cell, rx: 2, "stroke-width": 1 }, g);
        svg("title", {}, g).textContent = `${refLabel(ref)}${evidence.has(ref) ? " — quoted as evidence" : ""}`;
        shown.push({ g, x: cx + cell / 2, y: cy + cell / 2 });
      });
      svg("path", { d: curve({ x: x + cols * (cell + gap), y: y + blockH / 2 }, centre, 0, 30, 0.1).d, class: "edge machine", "stroke-opacity": 0.25 }, lines);
      colMax = Math.max(colMax, x);
      y += blockH + 12;
    }
    const remaining = parts.reduce((n, [, l]) => n + l.length, 0) - shown.length;
    if (remaining > 0) svg("text", { x: 40, y: H - 12, class: "tiny", fill: "var(--ink-3)", style: "font-size:11px" }, viewport).textContent = `+ ${remaining} more passages, listed in the panel`;

    // Legislation on the right.
    svg("text", { x: 690, y: 62, class: "family-label" }, viewport).textContent = `Act & Regulations — law · ${laws.length}`;
    laws.slice(0, 14).forEach((ref, i) => {
      const ly = 100 + i * 38;
      const g = svg("g", { class: "psg law", "data-ref": ref, transform: `translate(705,${ly})` }, viewport);
      svg("path", { d: "M0,-9 L9,0 L0,9 L-9,0 Z", "stroke-width": 1.2 }, g);
      const label = ontology.provisions[ref];
      svg("text", { x: 16, y: 4, style: "font-size:12px;fill:var(--ink)" }, g).textContent = refLabel(ref) + (label?.title ? ` — ${label.title.length > 30 ? label.title.slice(0, 29) + "…" : label.title}` : "");
      svg("path", { d: curve(centre, { x: 705, y: ly }, 30, 12, -0.08).d, class: "edge", "stroke-opacity": 0.35 }, lines);
    });
    if (!laws.length) svg("text", { x: 690, y: 100, style: "font-size:12px;fill:var(--ink-3)" }, viewport).textContent = "No provision recorded for this idea.";

    if (animate) {
      shown.forEach(({ g }, i) => { g.style.opacity = 0; setTimeout(() => { g.style.opacity = 1; }, 4 * i); });
    }
    showConcept(concept);
  }

  // --------------------------------------------------------- side panel

  function showLevelHelp() {
    const level = state.level;
    const text = {
      kinds: `<h2>Start with the shape</h2>
        <p>Every idea in the map is sorted into one of nine kinds. Four describe <b>how a decision is reasoned towards</b> —
        grounds of refusal, the tests that decide them, the factors that feed those tests, and the exceptions that take a case out.
        Five describe <b>the process that reasoning sits inside</b> — who acts, what is acted on, the steps, the records and the external schemes.</p>
        <p>The arrows roll ${fmt(c.relations.signed + c.relations.machine)} individual connections up into the patterns they make. Read the
        thickest one aloud: <i>factors qualify, or give rise to, tests</i>. That is examination practice in one line — and it stays true
        however many factors are added, merged or reworded underneath.</p>
        <p class="muted small">The four reasoning kinds are the project owner's; the five process kinds were proposed by a machine.
        Which kind each idea belongs to was judged by a machine and has not been reviewed.</p>`,
      ideas: `<h2>The ideas themselves</h2>
        <p>${fmt(c.concepts.signed + c.concepts.machine)} ideas, each sitting with the others of its kind. Lines are connections between two ideas, each
        resting on a sentence in the Manual. Hover over an idea to light up its neighbours; click it to read what it rests on.</p>
        <p class="muted small">${c.concepts.signed} ideas and ${c.relations.signed} connections were signed by a trade marks expert. The rest were written by a machine
        from the Manual's text and are shown dashed — usable, but nobody has checked them yet.</p>`,
    }[level] || "";
    side.innerHTML = text + `<h4>The nine kinds</h4><ul class="rel-list">${ontology.kinds.map((k) => `<li><span class="dot" style="--c:${kindColour(k.id)}"></span><span><b>${esc(k.label)}</b> <span class="muted small">— ${esc(k.plain)}</span></span></li>`).join("")}</ul>`;
  }

  function showKind(k) {
    const members = ontology.concepts.filter((x) => x.kind === k.id).sort((a, b) => (a.origin === b.origin ? b.mentions - a.mentions : a.origin === "signed" ? -1 : 1));
    const out = ontology.kind_links.filter((r) => r.s === k.id && r.o !== k.id).sort((a, b) => specificCount(b) - specificCount(a)).slice(0, 5);
    const inn = ontology.kind_links.filter((r) => r.o === k.id && r.s !== k.id).sort((a, b) => specificCount(b) - specificCount(a)).slice(0, 5);
    side.innerHTML = `
      <h2>${esc(k.label)}</h2>
      <div class="meta">${kindChip(k.id, ontology)}<span class="chip">${k.signed} signed · ${k.machine} machine-written</span></div>
      <p>${esc(capital(k.plain))}.</p>
      <p><button class="btn primary small" type="button" data-open>Open into its ${k.signed + k.machine} ideas →</button></p>
      <h4>Strongest patterns out</h4>${kindRows(out, "o")}
      <h4>Strongest patterns in</h4>${kindRows(inn, "s")}
      <h4>Its ideas</h4>
      <ul class="rel-list">${members.map((m) => `<li><span class="dot${m.origin === "machine" ? " machine" : ""}" style="--c:${kindColour(m.kind)}"></span><button class="link" type="button" data-c="${m.id}">${esc(m.label)}</button></li>`).join("")}</ul>`;
    side.querySelector("[data-open]").addEventListener("click", () => setLevel("ideas"));
    bindSide();
  }

  function kindRows(rows, end) {
    if (!rows.length) return `<p class="empty small">None.</p>`;
    return `<ul class="rel-list">${rows.map((r) => {
      const top = Object.entries(r.predicates).filter(([p]) => !LOOSE.has(p)).slice(0, 2)
        .map(([p, n]) => `${esc(ontology.predicates[p]?.label || p)} ${n}`).join(", ") || "loosely related";
      return `<li><span class="dot" style="--c:${kindColour(r[end])}"></span><span><b>${esc(kinds.get(r[end]).label)}</b> <span class="muted small">— ${r.total} connections: ${top}</span></span></li>`;
    }).join("")}</ul>`;
  }

  function showKindLink(row) {
    const a = kinds.get(row.s), b = kinds.get(row.o);
    const examples = row.examples.map((id) => ontology.relations.find((r) => r.id === id)).filter(Boolean);
    side.innerHTML = `
      <h2>${esc(a.label)} → ${esc(b.label)}</h2>
      <p class="muted">${row.total} connections run from an idea of the first kind to an idea of the second. ${row.signed} were signed by an expert.</p>
      <h4>What they say</h4>
      <ul class="rel-list">${Object.entries(row.predicates).map(([p, n]) => `<li><span class="pred num">${n}×</span><span>${esc(ontology.predicates[p]?.label || p)}</span></li>`).join("")}</ul>
      <h4>Examples, with the sentence each rests on</h4>
      ${examples.map((r) => relationCard(r)).join("")}`;
    bindSide();
  }

  function relationCard(r) {
    const name = (id) => byId.get(id)?.label || refLabel(id);
    return `<div style="margin:.6rem 0 1rem">
      <div class="meta">${trustBadge(r.origin)}${r.modality ? `<span class="chip">${esc(r.modality)}</span>` : ""}</div>
      <div><b>${esc(name(r.s))}</b> <span class="muted">— ${esc(ontology.predicates[r.p]?.label || r.p)} →</span> <b>${esc(name(r.o))}</b></div>
      ${r.quote ? `<blockquote class="quote ${isLaw(r.ref) ? "law" : "manual"}">${esc(r.quote)}</blockquote>` : ""}
      ${r.ref ? refChip(r.ref) : ""}
      ${r.machine?.reasoning ? `<details><summary>Why the machine wrote this${r.machine.confidence ? ` · confidence ${r.machine.confidence}` : ""}</summary><p class="small muted">${esc(r.machine.reasoning)}</p></details>` : ""}
    </div>`;
  }

  async function showConcept(concept) {
    const rels = relOf.get(concept.id) || [];
    const groups = new Map();
    for (const r of rels) {
      const outgoing = r.s === concept.id;
      const other = outgoing ? r.o : r.s;
      const key = `${outgoing ? "out" : "in"}:${r.p}`;
      if (!groups.has(key)) groups.set(key, { outgoing, p: r.p, items: [] });
      groups.get(key).items.push({ r, other });
    }
    const ordered = [...groups.values()].sort((a, b) => (LOOSE.has(a.p) - LOOSE.has(b.p)) || b.items.length - a.items.length);
    const search = await load("search");
    const refs = [...new Set(search.mentions[concept.id] || [])];
    const first = concept.evidence.find((e) => e.for === "concept") || concept.evidence[0];
    side.innerHTML = `
      <h2>${esc(concept.label)}</h2>
      <div class="meta">${kindChip(concept.kind, ontology)}${trustBadge(concept.origin)}</div>
      ${concept.alt.length ? `<p class="small"><span class="muted">Also called</span> ${concept.alt.map(esc).join(" · ")}</p>` : ""}
      ${concept.not.length ? `<p class="small"><span class="muted">Not the same as</span> ${concept.not.map(esc).join(" · ")}</p>` : ""}
      ${first ? `<h4>What it rests on</h4><blockquote class="quote ${isLaw(first.ref) ? "law" : "manual"}">${esc(first.quote)}</blockquote>${refChip(first.ref)}
        <span class="tiny">${first.for === "kind" ? "quoted when the machine sorted it into its kind" : "quoted by the record itself"}</span>` : ""}
      ${concept.basis.length ? `<h4>In the legislation</h4><div class="meta">${concept.basis.map((r) => refChip(r)).join("")}</div>` : ""}
      ${concept.notes ? `<h4>Note on the record</h4><p class="small">${esc(concept.notes)}</p>` : ""}
      <h4>Connections · ${rels.length}</h4>
      ${ordered.length ? ordered.map((grp) => `
        <ul class="rel-list">${grp.items.map(({ r, other }) => `<li>
          <span class="pred">${grp.outgoing ? "" : "← "}${esc(ontology.predicates[r.p]?.label || r.p)}${grp.outgoing ? " →" : ""}</span>
          <span><span class="dot${r.origin === "machine" ? " machine" : ""}" style="--c:${kindColour(byId.get(other)?.kind)}"></span>
          ${byId.has(other) ? `<button class="link" type="button" data-c="${other}">${esc(byId.get(other).label)}</button>` : refChip(other)}
          <button class="link tiny" type="button" data-r="${r.id}" title="Show the sentence this connection rests on">why?</button></span></li>`).join("")}</ul>`).join("")
        : `<p class="empty small">No connections recorded.</p>`}
      <h4>Where it appears · ${fmt(refs.length)} passages</h4>
      <div class="meta">${concept.parts.map((p) => `<span class="chip">${esc(p.replace("Part", "Part "))}</span>`).join("")}</div>
      ${state.level !== "text" ? `<p><button class="btn small" type="button" data-text>Open into its text →</button></p>` : `<ul class="passage-list">${refs.slice(0, 80).map((r) => `<li>${refChip(r, ` data-hl="${esc([concept.label, ...concept.alt].join("|"))}"`)}</li>`).join("")}</ul>${refs.length > 80 ? `<p class="tiny">and ${refs.length - 80} more.</p>` : ""}`}
      ${provenance(concept)}`;
    side.querySelector("[data-text]")?.addEventListener("click", () => setLevel("text"));
    bindSide();
  }

  function provenance(concept) {
    const rows = [];
    if (concept.signed) rows.push(`<p class="small">Signed by <b>${esc(concept.signed.by)}</b>, a trade marks expert, on ${esc(concept.signed.date)}.</p>`);
    if (concept.machine) {
      rows.push(`<p class="small">Written by <code>${esc(concept.machine.by)}</code> on ${esc(concept.machine.date)} · <b>${esc(concept.machine.review_status)}</b>${concept.machine.confidence ? ` · confidence ${esc(concept.machine.confidence)}` : ""}.</p>`);
      if (concept.machine.reasoning) rows.push(`<p class="small muted">${esc(concept.machine.reasoning)}</p>`);
      if (concept.machine.check) rows.push(`<p class="small"><b>What an expert should check:</b> ${esc(concept.machine.check)}</p>`);
    }
    if (concept.typed) rows.push(`<p class="small">Its kind was judged by <code>${esc(concept.typed.by)}</code> on ${esc(concept.typed.date)} · <b>${esc(concept.typed.review_status)}</b>.</p>`);
    return `<details><summary>Who wrote this record</summary>${rows.join("")}</details>`;
  }

  function bindSide() {
    side.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", () => selectConcept(b.dataset.c)));
    side.querySelectorAll("[data-r]").forEach((b) => b.addEventListener("click", () => {
      const r = ontology.relations.find((x) => x.id === b.dataset.r);
      const holder = el(`<div>${relationCard(r)}</div>`);
      const li = b.closest("li");
      if (li.nextElementSibling?.classList.contains("why")) { li.nextElementSibling.remove(); return; }
      const row = el(`<li class="why" style="display:block"></li>`);
      row.appendChild(holder);
      li.after(row);
    }));
  }

  // --------------------------------------------------------- wiring

  root.querySelectorAll(".lvl").forEach((b) => b.addEventListener("click", () => setLevel(b.dataset.level)));
  root.querySelectorAll("[data-f]").forEach((box) => box.addEventListener("change", () => {
    state[box.dataset.f] = box.checked;
    setLevel(state.level, { animate: false });
  }));
  const find = root.querySelector(".find");
  const results = root.querySelector(".find-results");
  find.addEventListener("input", () => {
    const q = find.value.trim().toLowerCase();
    if (q.length < 2) { results.innerHTML = ""; return; }
    const hits = ontology.concepts.filter((x) => [x.label, ...x.alt].some((l) => l.toLowerCase().includes(q))).slice(0, 12);
    results.innerHTML = hits.map((h) => `<button type="button" data-c="${h.id}"><span class="dot${h.origin === "machine" ? " machine" : ""}" style="--c:${kindColour(h.kind)}"></span>${esc(h.label)}</button>`).join("") || `<span class="tiny">No idea by that name.</span>`;
    results.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", () => {
      state.concept = b.dataset.c;
      if (state.level === "kinds") setLevel("ideas"); else selectConcept(b.dataset.c);
    }));
  });
  const onTheme = () => setLevel(state.level, { animate: false });
  window.addEventListener("tmk-theme", onTheme);

  setLevel(state.level, { animate: true });
  return () => window.removeEventListener("tmk-theme", onTheme);
}

function lvl(id, n, title, sub, stab) {
  return `<button class="lvl" type="button" role="tab" data-level="${id}">
    <span class="pip">${n}</span>
    <span><b>${esc(title)}</b><span>${esc(sub)}</span><span class="stab">${esc(stab)}</span></span>
  </button>`;
}

const capital = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);
