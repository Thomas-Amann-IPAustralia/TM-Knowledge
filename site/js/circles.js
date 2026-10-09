/* At a glance — the ontology as nested circles (D3 circle packing): the whole,
   its three families, the kinds, the ideas. Click to zoom a level down. At every
   level the circles are joined by what joins them: the families by the
   relationships that cross between them, a family's kinds by theirs, an idea (on
   hover) by its own — each line labelled with what it says (ADR-0131). Sizes count
   passages that name each idea; nothing here is a judgement of the page's own.

   Every idea is drawn the same way, whoever wrote it: who wrote a record is on
   its card, not on the picture (ADR-0130). */

import { esc, fmt, kindColour, kindCount, trustBadge, kindChip, quoteBlock, refChip } from "./app.js";
import * as lib from "./lib.js";

// Short, because the four family labels share the top of one picture.
const FAMILY_LABEL = { reasoning: "The law's questions", examined: "What is examined", process: "The process", other: "None of the kinds" };

export async function render(root, { ontology }) {
  const d3 = await lib.d3();
  root.innerHTML = `
  <div class="wrap wide circles-page">
    <h1>Every idea, by what it is</h1>
    <p class="lede">Three families of kinds, ${kindCount(ontology)} kinds, ${fmt(ontology.concepts.length)} ideas, each circle sized by how many
    passages of the Manual name it, and each joined to the others by what the connections between them say. Click a circle to go down a level.</p>
    <div class="circles">
      <div class="pack-card card">
        <div class="pack-crumbs" aria-live="polite"></div>
        <div class="pack"></div>
      </div>
      <aside class="card circles-side">
        <div class="pack-note" aria-live="polite"></div>
        <h4>The kinds</h4>
        <ul class="kind-key">${ontology.kinds.map((k) => `<li><span class="dot" style="--c:${kindColour(k.id)}"></span><span><b>${esc(k.label)}</b> <span class="muted small">— ${esc(k.plain)}</span></span></li>`).join("")}</ul>
      </aside>
    </div>
  </div>`;
  drawPack(root, ontology, d3);
}

function drawPack(root, ontology, d3) {
  const holder = root.querySelector(".pack");
  const crumbs = root.querySelector(".pack-crumbs");
  const note = root.querySelector(".pack-note");
  const byId = new Map(ontology.concepts.map((x) => [x.id, x]));
  const neighbours = new Map();
  for (const r of ontology.relations) {
    if (!byId.has(r.s) || !byId.has(r.o)) continue;
    for (const [a, b] of [[r.s, r.o], [r.o, r.s]]) { if (!neighbours.has(a)) neighbours.set(a, []); neighbours.get(a).push({ id: b, r }); }
  }

  const families = ["reasoning", "examined", "process", "other"].map((family) => ({
    name: FAMILY_LABEL[family], type: "family", family,
    children: ontology.kinds.filter((k) => k.family === family).map((k) => ({
      name: k.label, type: "kind", kind: k.id, plain: k.plain,
      children: ontology.concepts.filter((x) => x.kind === k.id).map((x) => ({ name: x.label, type: "idea", id: x.id, kind: x.kind, value: 2 + Math.sqrt(x.mentions) })),
    })).filter((k) => k.children.length),
  })).filter((f) => f.children.length);
  const data = { name: "The ontology", type: "root", children: families };

  const size = 600;
  const hierarchy = d3.hierarchy(data).sum((d) => d.value || 0).sort((a, b) => b.value - a.value);
  // Room between the families and between a family's kinds, for the lines that join them.
  const nodes = d3.pack().size([size, size]).padding((d) => (d.depth === 0 ? 56 : d.depth === 1 ? 22 : 3))(hierarchy);

  const svg = d3.create("svg").attr("viewBox", `-${size / 2} -${size / 2} ${size} ${size}`).attr("role", "img")
    .attr("aria-label", "The ontology as nested circles: families, kinds and ideas. Click to zoom.");
  holder.appendChild(svg.node());
  const fillFor = (d) => {
    if (d.data.type === "family") return "var(--panel-2)";
    if (d.data.type === "kind") return `color-mix(in srgb, ${kindColour(d.data.kind)} 13%, var(--panel))`;
    if (d.data.type === "idea") return `color-mix(in srgb, ${kindColour(d.data.kind)} 70%, var(--panel))`;
    return "transparent";
  };
  const links = svg.append("g").attr("class", "pack-links").attr("pointer-events", "none");
  const circle = svg.append("g").selectAll("circle").data(nodes.descendants().slice(1)).join("circle")
    .attr("class", (d) => `pack-${d.data.type}`)
    .attr("fill", fillFor)
    .attr("stroke", (d) => (d.data.type === "family" ? "var(--line)" : kindColour(d.data.kind)))
    .attr("stroke-width", (d) => (d.data.type === "kind" ? 1.6 : d.data.type === "idea" ? 1.2 : 1))
    .attr("stroke-dasharray", (d) => (d.data.type === "family" ? "3 2" : null))
    .style("cursor", "pointer")
    .on("click", (event, d) => { event.stopPropagation(); if (focus !== d) zoom(d); })
    .on("mouseenter", (event, d) => { if (d.data.type === "idea") showLinks(d); })
    .on("mouseleave", () => links.selectAll("*").remove());
  circle.append("title").text((d) => d.data.name);
  // Above the circles, below their names: the lines run in the gaps between circles.
  const structure = svg.append("g").attr("class", "pack-structure").attr("pointer-events", "none");

  const label = svg.append("g").attr("pointer-events", "none").attr("text-anchor", "middle").selectAll("text")
    .data(nodes.descendants().slice(1)).join("text")
    .attr("class", (d) => `pack-label pack-label-${d.data.type}`)
    .style("display", (d) => (d.parent === nodes && d.data.family !== "other" ? "inline" : "none"))
    .style("fill-opacity", (d) => (d.parent === nodes ? 1 : 0))
    .text((d) => d.data.name);

  svg.on("click", () => zoom(focus.parent || nodes));
  let focus = nodes;
  let view, home;
  const leafAt = new Map(nodes.leaves().map((d) => [d.data.id, d]));

  // What joins the circles at the level in view: undirected pairs, with the
  // predicates the relationships between them use, most used first.
  const predLabel = (p) => ontology.predicates[p]?.label || p;
  const pairs = (rows, keep) => {
    const out = new Map();
    for (const r of rows) {
      if (r.s === r.o || !keep(r)) continue;
      const key = [r.s, r.o].sort().join("|");
      if (!out.has(key)) out.set(key, { a: [r.s, r.o].sort()[0], b: [r.s, r.o].sort()[1], total: 0, predicates: {} });
      const m = out.get(key);
      m.total += r.total;
      for (const [p, n] of Object.entries(r.predicates)) m.predicates[p] = (m.predicates[p] || 0) + n;
    }
    return [...out.values()];
  };
  const topPredicates = (m, n) => Object.entries(m.predicates).sort((x, y) => y[1] - x[1]).slice(0, n).map(([p]) => predLabel(p));
  const familyPairs = pairs(ontology.family_links || [], () => true);
  const kindPairs = pairs(ontology.kind_links || [], () => true);
  const familyNode = new Map(nodes.children.map((n) => [n.data.family, n]));
  const kindNode = new Map(nodes.descendants().filter((n) => n.data.type === "kind").map((n) => [n.data.kind, n]));

  function drawStructure(k) {
    structure.selectAll("*").remove();
    if (!focus || !["root", "family"].includes(focus.data.type)) return;
    const at = (n) => [(n.x - view[0]) * k, (n.y - view[1]) * k];
    let rows;
    if (focus.data.type === "root") {
      rows = familyPairs.map((m) => ({ m, a: familyNode.get(m.a), b: familyNode.get(m.b), label: `${topPredicates(m, 1).join("")} · ${m.total}` }));
    } else {
      const inside = new Set(focus.children.map((n) => n.data.kind));
      rows = kindPairs.filter((m) => inside.has(m.a) && inside.has(m.b))
        .map((m) => ({ m, a: kindNode.get(m.a), b: kindNode.get(m.b), label: String(m.total) }));
    }
    const max = Math.max(1, ...rows.map((r) => r.m.total));
    for (const { m, a, b, label } of rows) {
      if (!a || !b) continue;
      // From edge to edge, across the gap between the two circles.
      const [ax, ay] = at(a), [bx, by] = at(b);
      const len = Math.hypot(bx - ax, by - ay) || 1, ux = (bx - ax) / len, uy = (by - ay) / len;
      const x1 = ax + ux * (a.r * k + 3), y1 = ay + uy * (a.r * k + 3);
      const x2 = bx - ux * (b.r * k + 3), y2 = by - uy * (b.r * k + 3);
      structure.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2)
        .attr("stroke", "var(--ink)").attr("stroke-opacity", 0.5)
        .attr("stroke-width", (1.5 + 6 * Math.sqrt(m.total / max)).toFixed(1)).attr("stroke-linecap", "round")
        .append("title").text(`${a.data.name} — ${b.data.name}: ${m.total} connections (${topPredicates(m, 4).join(", ")})`);
      // Beside the line, on the side away from the picture's centre, clear of the
      // circles' names on their top edges.
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      let nx = -uy, ny = ux;
      if (nx * mx + ny * my < 0) { nx = -nx; ny = -ny; }
      const off = focus.data.type === "root" ? 18 : 10;
      structure.append("text").attr("class", "pack-link-label").attr("x", mx + nx * off).attr("y", my + ny * off + 4)
        .attr("text-anchor", nx > 0.35 ? "start" : nx < -0.35 ? "end" : "middle").text(label);
    }
  }

  function zoomTo(v) {
    const k = size / v[2];
    view = v;
    drawStructure(k);
    // A family's or kind's label sits on its top edge, so the circles inside stay visible.
    label.attr("transform", (d) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k + (d.children ? -d.r * k + 22 : 4)})`);
    circle.attr("transform", (d) => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`).attr("r", (d) => d.r * k);
  }

  function zoom(d) {
    focus = d;
    const target = d.data.type === "idea" ? d.parent : d;
    const transition = svg.transition().duration(matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 650)
      .tween("zoom", () => {
        const i = d3.interpolateZoom(view, target === nodes && home ? home : [target.x, target.y, target.r * 2 + 8]);
        return (t) => zoomTo(i(t));
      });
    label.filter(function (n) { return n.parent === target || this.style.display === "inline"; })
      .transition(transition)
      .style("fill-opacity", (n) => (n.parent === target ? 1 : 0))
      .on("start", function (n) { if (n.parent === target) this.style.display = "inline"; })
      .on("end", function (n) { if (n.parent !== target) this.style.display = "none"; });
    links.selectAll("*").remove();
    circle.classed("sel", (n) => n === d && d.data.type === "idea");
    describe(d);
  }

  function showLinks(d) {
    links.selectAll("*").remove();
    const k = size / view[2];
    const at = (n) => [(n.x - view[0]) * k, (n.y - view[1]) * k];
    for (const { id } of neighbours.get(d.data.id) || []) {
      const other = leafAt.get(id);
      if (!other) continue;
      const [x1, y1] = at(d), [x2, y2] = at(other);
      links.append("path").attr("d", `M${x1},${y1} Q${(x1 + x2) / 2 + (y2 - y1) * 0.15},${(y1 + y2) / 2 - (x2 - x1) * 0.15} ${x2},${y2}`)
        .attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-opacity", 0.55).attr("stroke-width", 1.2);
    }
  }

  function describe(d) {
    const path = d.ancestors().reverse();
    crumbs.innerHTML = path.map((n, i) => i === path.length - 1 ? `<b>${esc(n.data.name)}</b>` : `<button type="button" data-depth="${i}">${esc(n.data.name)}</button>`).join(" › ");
    crumbs.querySelectorAll("[data-depth]").forEach((b) => b.addEventListener("click", () => zoom(path[Number(b.dataset.depth)])));
    const type = d.data.type;
    const familyLine = (r) => `<li><b>${esc(FAMILY_LABEL[r.s])}</b> → <b>${esc(FAMILY_LABEL[r.o].toLowerCase())}</b>:
      ${Object.entries(r.predicates).slice(0, 3).map(([p, n]) => `${esc(predLabel(p))} ${n}`).join(", ")} <span class="muted">(${r.total})</span></li>`;
    if (type === "root") {
      const across = (ontology.family_links || []).filter((r) => r.s !== r.o);
      note.innerHTML = `<b>The whole ontology.</b> Three families of kinds, ${kindCount(ontology)} kinds, ${fmt(ontology.concepts.length)} ideas.
        <h4 style="margin:.6rem 0 .2rem">How the families connect</h4>
        <ul class="small family-links">${across.map(familyLine).join("")}</ul>
        <span class="muted">Each line counts the relationships whose two ideas sit in those families, by what they say. Click a family to go down a level.</span>`;
    } else if (type === "family") {
      const own = (ontology.family_links || []).find((r) => r.s === d.data.family && r.o === d.data.family);
      const out = (ontology.family_links || []).filter((r) => r.s !== r.o && (r.s === d.data.family || r.o === d.data.family));
      note.innerHTML = `<b>${esc(d.data.name)}.</b> ${d.children.length} kinds of idea, joined inside the family by
        ${own ? `${own.total} relationships (${Object.entries(own.predicates).slice(0, 3).map(([p, n]) => `${esc(predLabel(p))} ${n}`).join(", ")})` : "none"}, and to the others by:
        <ul class="small family-links">${out.map(familyLine).join("")}</ul>
        <span class="muted">These rest on no single passage: a rewording of the Manual leaves them as they are. Click a kind.</span>`;
    } else if (type === "kind") {
      note.innerHTML = `<b>${esc(d.data.name)}</b> — ${esc(d.data.plain)}. ${d.leaves().length} ideas. <span class="muted">Click one to read it.</span>
        <a href="#/map/ideas">Open it on the map →</a>`;
    } else {
      const x = byId.get(d.data.id);
      const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
      note.innerHTML = `<div class="pack-idea"><b>${esc(x.label)}</b><div class="meta">${kindChip(x.kind, ontology)}${trustBadge(x.origin)}</div>
        ${first ? `${quoteBlock(first.ref, first.quote.length > 220 ? first.quote.slice(0, 218) + "…" : first.quote)}${refChip(first.ref)}` : ""}
        <p class="small" style="margin:.5rem 0 0">${fmt(x.mentions)} passages name it · ${fmt((neighbours.get(x.id) || []).length)} connection${(neighbours.get(x.id) || []).length === 1 ? "" : "s"} ·
        <a href="#/map/ideas/${x.id}">open it on the map →</a></p></div>`;
      showLinks(d);
    }
  }

  // Open fitted to the families, not to the outer circle round them.
  const kids = nodes.children;
  const x0 = Math.min(...kids.map((n) => n.x - n.r)), x1 = Math.max(...kids.map((n) => n.x + n.r));
  const y0 = Math.min(...kids.map((n) => n.y - n.r)), y1 = Math.max(...kids.map((n) => n.y + n.r));
  home = [(x0 + x1) / 2, (y0 + y1) / 2, Math.max(x1 - x0, y1 - y0) + 16];
  zoomTo(home);
  describe(nodes);
}
