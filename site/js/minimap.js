/* A small Cytoscape map of one corner of the ontology, for the views that are
   not the map: Ask the Manual (the ideas a question started from and every
   connection it followed) and When the text changes (what rests on a page).

   Same marks as the map: colour is the kind of idea, and every idea and line is
   drawn the same way whoever wrote it — who wrote a record is on its card
   (ADR-0130). Positions are computed — a ring round the ideas
   in the middle, or a seeded D3 force run — never left to chance, so the same
   input always draws the same picture. Every node and line is a record; the
   caller chooses which, and this module only draws them. */

import { esc, fmt, kindChip, trustBadge, quoteBlock, refChip, refLabel } from "./app.js";
import * as lib from "./lib.js";

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * Draw a mini map into `holder`.
 *
 * - `centre`: ids drawn large and ringed (where something starts or rests);
 * - `muted`: ids drawn grey (recognised, but not used);
 * - `relations`: [{ id, s, p, o, origin }] — the lines; their ends are added as nodes;
 * - `strong`: relation ids drawn dark; the rest are drawn faint (when given);
 * - `layout`: "ring" (centre in the middle) or "force" (needs `d3`);
 * - `help`: what the info line says before anything is clicked.
 */
export async function miniMap(holder, { ontology, centre = [], muted = [], relations = [], strong = null, layout = "ring", d3 = null, help = "", height = 420 }) {
  const cytoscape = await lib.cytoscape();
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const relById = new Map(ontology.relations.map((r) => [r.id, r]));
  const centreSet = new Set(centre), mutedSet = new Set(muted);
  const edges = relations.filter((r) => byId.has(r.s) && byId.has(r.o));
  const ids = [...new Set([...centre, ...muted, ...edges.flatMap((r) => [r.s, r.o])])].filter((id) => byId.has(id));

  holder.classList.add("mini");
  holder.innerHTML = `
    <div class="mini-canvas" style="height:min(${height}px, 82vw)">
      <div class="mini-cy" role="img" aria-label="${esc(`A map of ${ids.length} ideas and ${edges.length} connections`)}"></div>
      <div class="hovercard" hidden></div>
      <div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button><button type="button" data-z="fit" aria-label="Fit to view">⤢</button></div>
    </div>
    <div class="mini-info" aria-live="polite"></div>`;
  const container = holder.querySelector(".mini-cy");
  const card = holder.querySelector(".hovercard");
  const info = holder.querySelector(".mini-info");
  const helpHtml = `<span class="tiny">${help || "Hover over an idea to see what it rests on; click a line to read the sentence it rests on."}</span>`;
  info.innerHTML = helpHtml;

  const elements = [];
  for (const id of ids) {
    const x = byId.get(id);
    const cls = ["concept", centreSet.has(id) ? "centre" : "", mutedSet.has(id) ? "muted" : ""].filter(Boolean).join(" ");
    elements.push({ data: { id, label: x.label, col: css(`--k-${x.kind}`), size: centreSet.has(id) ? 30 : Math.min(24, 12 + 2.6 * Math.log2(1 + x.mentions)) }, classes: cls });
  }
  const seen = new Set();
  for (const r of edges) {
    if (seen.has(r.id)) continue;
    seen.add(r.id);
    const faint = strong && !strong.has(r.id);
    elements.push({ data: { id: `r:${r.id}`, source: r.s, target: r.o, rel: r.id, pred: ontology.predicates[r.p]?.label || r.p },
      classes: `rel${faint ? " faint" : ""}` });
  }

  const positions = layout === "force" && d3 ? forcePositions(d3, ids, edges, centreSet) : ringPositions(ids, edges, centre, muted, byId);
  for (const e of elements) {
    const p = positions.get(e.data.id);
    if (!p) continue;
    e.position = { x: p.x, y: p.y };
    if (p.label) e.classes += ` lab-${p.label}`;
  }

  await document.fonts.ready;
  const cy = cytoscape({
    container, elements, style: styles(), layout: { name: "preset", fit: true, padding: 36 },
    minZoom: 0.2, maxZoom: 3, boxSelectionEnabled: false, userZoomingEnabled: false, autoungrabify: false,
  });
  holder.cy = cy; // for browser checks, as on the map
  cy.fit(undefined, 36);

  function styles() {
    const ink = css("--ink"), ink2 = css("--ink-2"), ink3 = css("--ink-3"), bg = css("--bg"), panel = css("--panel"), warn = css("--warn"), glow = css("--glow");
    return [
      { selector: "node", style: { "font-family": css("--sans"), color: ink, "overlay-opacity": 0 } },
      { selector: "node.concept", style: {
        width: "data(size)", height: "data(size)", "background-color": "data(col)", "border-width": 2, "border-color": "data(col)",
        label: "data(label)", "text-valign": "bottom", "text-halign": "center", "text-margin-y": 3, "font-size": 12.5,
        "text-wrap": "wrap", "text-max-width": 130, "text-background-color": bg, "text-background-opacity": 0.8,
        "text-background-padding": 1.5, "text-background-shape": "round-rectangle", "min-zoomed-font-size": 6 } },
      { selector: "node.lab-right", style: { "text-valign": "center", "text-halign": "right", "text-margin-x": 6, "text-margin-y": 0 } },
      { selector: "node.lab-left", style: { "text-valign": "center", "text-halign": "left", "text-margin-x": -6, "text-margin-y": 0 } },
      { selector: "node.lab-top", style: { "text-valign": "top", "text-margin-y": -3 } },
      { selector: "node.centre", style: { "border-width": 4, "font-size": 14.5, "font-weight": 650, "font-family": css("--serif"),
        "underlay-color": "data(col)", "underlay-opacity": 0.18, "underlay-padding": 7, "underlay-shape": "ellipse" } },
      { selector: "node.muted", style: { "background-color": panel, "border-color": ink3, "border-style": "dotted", color: ink3, "underlay-opacity": 0 } },
      { selector: "node.pulse", style: { "underlay-color": glow, "underlay-opacity": 0.55, "underlay-padding": 11,
        "transition-property": "underlay-opacity, underlay-padding", "transition-duration": "0.35s" } },
      { selector: "edge", style: {
        "curve-style": "bezier", width: 1.4, "line-color": ink3, "target-arrow-color": ink3, "target-arrow-shape": "triangle",
        "arrow-scale": 0.8, opacity: 0.7, "overlay-opacity": 0,
        "transition-property": "line-color, target-arrow-color, width, opacity", "transition-duration": "0.4s" } },
      { selector: "edge.faint", style: { opacity: 0.2, width: 1 } },
      { selector: "edge.flash", style: { "line-color": warn, "target-arrow-color": warn, width: 3.4, opacity: 1 } },
      { selector: ".faded", style: { opacity: 0.12, "text-opacity": 0.2 } },
      { selector: "edge.hl", style: { opacity: 1, width: 2.6, "line-color": ink, "target-arrow-color": ink, "z-index": 9,
        label: "data(pred)", "font-size": 11, color: ink2, "text-background-color": bg, "text-background-opacity": 0.9,
        "text-background-padding": 2, "text-rotation": "autorotate" } },
      { selector: "node:selected", style: { "border-color": ink, "border-style": "solid", "border-width": 4 } },
    ];
  }

  // ------------------------------------------------------------ hover and click

  function showCard(node) {
    const x = byId.get(node.id());
    const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
    const quote = first ? String(first.quote) : "";
    card.innerHTML = `<b>${esc(x.label)}</b><div class="meta">${kindChip(x.kind, ontology)}${trustBadge(x.origin)}</div>
      ${quote ? quoteBlock(first.ref, quote.length > 160 ? quote.slice(0, 158) + "…" : quote) : ""}
      <span class="tiny">${fmt(x.mentions)} passages name it · click for more</span>`;
    const p = node.renderedPosition();
    const box = container.getBoundingClientRect();
    card.hidden = false;
    const w = card.offsetWidth, h = card.offsetHeight;
    card.style.left = `${Math.min(box.width - w - 8, Math.max(8, p.x + 18))}px`;
    card.style.top = `${Math.min(box.height - h - 8, Math.max(8, p.y - h / 2))}px`;
  }
  const hideCard = () => { card.hidden = true; };

  function focus(node) {
    cy.elements().removeClass("faded hl");
    const near = node.closedNeighborhood();
    cy.elements().not(near).addClass("faded");
    near.edges().addClass("hl");
  }
  function clear() { cy.elements().removeClass("faded hl"); cy.elements().unselect(); info.innerHTML = helpHtml; }

  cy.on("mouseover", "node", (e) => { showCard(e.target); if (!cy.$(":selected").length) e.target.connectedEdges().addClass("hl"); });
  cy.on("mouseout", "node", (e) => { hideCard(); if (!cy.$(":selected").length) e.target.connectedEdges().removeClass("hl"); });
  cy.on("mouseover", "edge", (e) => e.target.addClass("hl"));
  cy.on("mouseout", "edge", (e) => { if (!e.target.connectedNodes().some((n) => n.selected())) e.target.removeClass("hl"); });
  cy.on("pan zoom drag", hideCard);
  cy.on("tap", "node", (e) => {
    const x = byId.get(e.target.id());
    focus(e.target);
    const first = x.evidence.find((v) => v.for === "concept") || x.evidence[0];
    info.innerHTML = `<div class="mini-row"><b>${esc(x.label)}</b>${kindChip(x.kind, ontology)}${trustBadge(x.origin)}
      <a class="tiny" href="#/map/ideas/${esc(x.id)}">open it on the full map →</a></div>
      ${first ? `${quoteBlock(first.ref, first.quote)}${refChip(first.ref)}` : ""}`;
  });
  cy.on("tap", "edge", (e) => {
    const r = relById.get(e.target.data("rel"));
    cy.elements().removeClass("faded hl");
    e.target.addClass("hl");
    if (!r) return;
    const name = (id) => byId.get(id)?.label || refLabel(id);
    info.innerHTML = `<div class="mini-row">${trustBadge(r.origin)}<span><b>${esc(name(r.s))}</b> <span class="muted">— ${esc(ontology.predicates[r.p]?.label || r.p)} →</span> <b>${esc(name(r.o))}</b></span></div>
      ${r.quote ? quoteBlock(r.ref, r.quote) : ""}${r.ref ? refChip(r.ref) : ""}`;
  });
  cy.on("tap", (e) => { if (e.target === cy) clear(); });

  holder.querySelector(".zoom").addEventListener("click", (e) => {
    const z = e.target.closest("button")?.dataset.z;
    const mid = { x: container.clientWidth / 2, y: container.clientHeight / 2 };
    if (z === "in") cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: mid });
    else if (z === "out") cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: mid });
    else if (z) cy.animate({ fit: { padding: 36 }, duration: reduced() ? 0 : 350 });
  });

  const onTheme = () => {
    cy.batch(() => cy.nodes().forEach((n) => { const x = byId.get(n.id()); if (x) n.data("col", css(`--k-${x.kind}`)); }));
    cy.style(styles());
  };
  window.addEventListener("tmk-theme", onTheme);
  const onResize = () => { cy.resize(); cy.fit(undefined, 36); };
  window.addEventListener("resize", onResize);

  return {
    cy,
    /** Draw these relations in the warning colour for a moment (or until `off`). */
    flash(relIds, ms = 1400) {
      const sel = cy.edges().filter((ed) => relIds.includes(ed.data("rel")));
      sel.addClass("flash");
      if (ms) setTimeout(() => sel.removeClass("flash"), reduced() ? 900 : ms);
    },
    /** Pulse these ideas once. */
    pulse(nodeIds, ms = 1200) {
      const sel = cy.nodes().filter((n) => nodeIds.includes(n.id()));
      sel.addClass("pulse");
      setTimeout(() => sel.removeClass("pulse"), ms);
    },
    destroy() {
      window.removeEventListener("tmk-theme", onTheme);
      window.removeEventListener("resize", onResize);
      cy.destroy();
    },
  };
}

/** Ideas in the middle (one at the centre, or a small circle of them), the rest
    on a wider ring, grouped by the middle idea they connect to, labels outward. */
function ringPositions(ids, edges, centre, muted, byId) {
  const pos = new Map();
  const middle = [...centre.filter((id) => byId.has(id)), ...muted.filter((id) => byId.has(id) && !centre.includes(id))];
  const middleSet = new Set(middle);
  const anchor = new Map();
  for (const r of edges) {
    for (const [a, b] of [[r.s, r.o], [r.o, r.s]]) {
      if (middleSet.has(a) && !middleSet.has(b)) {
        const i = middle.indexOf(a);
        if (!anchor.has(b) || i < anchor.get(b)) anchor.set(b, i);
      }
    }
  }
  const outer = ids.filter((id) => !middleSet.has(id))
    .sort((a, b) => (anchor.get(a) ?? 99) - (anchor.get(b) ?? 99) || byId.get(a).label.localeCompare(byId.get(b).label));
  const n = outer.length;
  const R = Math.max(170, (n * 46) / (2 * Math.PI * 1.15));
  const angleOf = new Map();
  outer.forEach((id, i) => {
    const a = (i / Math.max(1, n)) * Math.PI * 2 - Math.PI / 2 + (n > 1 ? Math.PI / n : 0);
    const stagger = n > 22 && i % 2 ? 1.16 : 1;
    const x = Math.cos(a) * R * 1.45 * stagger, y = Math.sin(a) * R * stagger;
    const c = Math.cos(a);
    pos.set(id, { x, y, label: c > 0.35 ? "right" : c < -0.35 ? "left" : Math.sin(a) < 0 ? "top" : "bottom" });
    angleOf.set(id, a);
  });
  if (middle.length === 1) pos.set(middle[0], { x: 0, y: 0 });
  else {
    const rc = 46 + 26 * middle.length;
    middle.forEach((id, i) => {
      // Sit each middle idea towards the ideas it connects to, if any.
      const mine = outer.filter((o) => anchor.get(o) === i).map((o) => angleOf.get(o));
      const a = mine.length ? Math.atan2(mine.reduce((s, x) => s + Math.sin(x), 0), mine.reduce((s, x) => s + Math.cos(x), 0))
        : (i / middle.length) * Math.PI * 2 + Math.PI / 4;
      pos.set(id, { x: Math.cos(a) * rc * 1.3, y: Math.sin(a) * rc });
    });
    // Two middle ideas pointing the same way would sit on top of each other.
    const placed = [];
    for (const id of middle) {
      const p = pos.get(id);
      while (placed.some((q) => Math.hypot(q.x - p.x, q.y - p.y) < 70)) { p.y += 44; }
      placed.push(p);
    }
  }
  return pos;
}

/** A seeded D3 force run, to rest: same input, same picture. */
function forcePositions(d3, ids, edges, centreSet) {
  const nodes = ids.map((id, i) => ({ id, x: Math.cos(i) * 60 * Math.sqrt(i + 1), y: Math.sin(i) * 60 * Math.sqrt(i + 1) }));
  const links = edges.map((r) => ({ source: r.s, target: r.o }));
  const sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance(78).strength(0.7))
    .force("charge", d3.forceManyBody().strength(-260))
    .force("collide", d3.forceCollide(40))
    .force("x", d3.forceX(0).strength((d) => (centreSet.has(d.id) ? 0.12 : 0.05)))
    .force("y", d3.forceY(0).strength((d) => (centreSet.has(d.id) ? 0.18 : 0.08)))
    .stop();
  for (let i = 0; i < 400; i++) sim.tick();
  return new Map(nodes.map((d) => [d.id, { x: d.x, y: d.y }]));
}
