/* At a glance — the ontology as nested circles (D3 circle packing): the whole,
   its three families, the ten kinds, the ideas. Click to zoom a level down;
   hover an idea to see its connections reach across kinds. Sizes count passages
   that name each idea; nothing here is a judgement of the page's own.

   Every idea is drawn the same way, whoever wrote it: who wrote a record is on
   its card, not on the picture (ADR-0130). */

import { esc, fmt, kindColour, trustBadge, kindChip, quoteBlock, refChip } from "./app.js";
import * as lib from "./lib.js";

// Short, because the four family labels share the top of one picture.
const FAMILY_LABEL = { reasoning: "The law's questions", examined: "What is examined", process: "The process", other: "None of the ten" };

export async function render(root, { ontology }) {
  const d3 = await lib.d3();
  root.innerHTML = `
  <div class="wrap wide circles-page">
    <h1>Every idea, by what it is</h1>
    <p class="lede">Three families of kinds, ${ontology.kinds.length - 1} kinds, ${fmt(ontology.concepts.length)} ideas, each circle sized by how many
    passages of the Manual name it. Click a circle to go down a level.</p>
    <div class="circles">
      <div class="pack-card card">
        <div class="pack-crumbs" aria-live="polite"></div>
        <div class="pack"></div>
      </div>
      <aside class="card circles-side">
        <div class="pack-note" aria-live="polite"></div>
        <h4>The ten kinds</h4>
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
    if (!byId.has(r.s) || !byId.has(r.o) || r.p === "related") continue;
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
  const nodes = d3.pack().size([size, size]).padding((d) => (d.depth === 0 ? 14 : d.depth === 1 ? 10 : 3))(hierarchy);

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

  function zoomTo(v) {
    const k = size / v[2];
    view = v;
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
    if (type === "root") {
      note.innerHTML = `<b>The whole ontology.</b> Three families of kinds, ${ontology.kinds.length - 1} kinds, ${fmt(ontology.concepts.length)} ideas.
        <span class="muted">Click a family to go down a level; hover an idea to see its connections cross the kinds.</span>`;
    } else if (type === "family") {
      note.innerHTML = `<b>${esc(d.data.name)}.</b> ${d.children.length} kinds of idea. These rest on no single passage: a rewording of the Manual leaves them as they are.
        <span class="muted">Click a kind.</span>`;
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
