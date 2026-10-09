/* Home — what this is, in one screen, and ways in.

   The hero is the ontology as nested circles (D3 circle packing): the whole, its
   two families, the ten kinds, the ideas. Click to zoom a level down; hover an
   idea to see its connections reach across kinds. Sizes count passages that name
   each idea; nothing here is a judgement of the page's own. */

import { esc, fmt, load, kindColour, trustBadge, kindChip, isLaw, refChip } from "./app.js";
import * as lib from "./lib.js";

const FAMILY_LABEL = { reasoning: "Reasoning towards a decision", process: "The process it sits inside", other: "None of the ten" };

export async function render(root, { ontology }) {
  const [stability, d3] = await Promise.all([load("stability"), lib.d3()]);
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;
  const passages = stability.pages.reduce((n, p) => n + p.passages, 0);
  const firstYear = Object.keys(stability.by_year)[0];

  root.innerHTML = `
  <div class="wrap">
    <section class="hero">
      <div>
        <p class="step-k">A demonstration for trade marks examiners</p>
        <h1>The Manual, as a map of the ideas you reason with</h1>
        <p class="lede">The Trade Marks Manual is written as ${fmt(passages)} passages of practice, beside the Act and the
        Regulations. This map connects them through ${fmt(concepts)} ideas — the grounds, tests, factors, roles and steps
        examiners work with — so a question can follow the connections between ideas, not just the words on the page.</p>
        <div class="actions">
          <a class="btn primary" href="#/tour">Take the tour · 3 minutes</a>
          <a class="btn" href="#/ask">Ask the Manual</a>
          <a class="btn" href="#/map">Explore the map</a>
        </div>
        <p class="tiny">An ontology is this structure: a shared, explicit list of the ideas in a field, what kind of thing each one is,
        and how they relate — each one tied to the text it comes from.</p>
      </div>
      <div class="pack-card card">
        <div class="pack-crumbs" aria-live="polite"></div>
        <div class="pack"></div>
        <div class="pack-note"></div>
      </div>
    </section>

    <section class="levels" aria-label="The map at four levels of detail">
      ${rung("map/kinds", ontology.kinds.length - 1, "Kinds of idea", "Grounds, tests, factors, exceptions; roles, steps, records. They rest on no single passage.", 1)}
      ${rung("map/ideas", concepts, "Ideas", `${c.concepts.signed} signed by an expert, ${c.concepts.machine} written by a machine; each sorted into a kind.`, 2)}
      ${rung("map/ideas", relations, "Connections", "How one idea bears on another, each pinned to the sentence it rests on.", 3)}
      ${rung("change", passages, "Passages", `The Manual's words, the Act and Regulations kept apart. ${fmt(stability.events)} amendments since ${esc(firstYear)}.`, 4)}
    </section>
    <div class="levels-axis"><span>↑ changes rarely</span><span>changes often →</span></div>

    <section class="doors">
      <a class="door card" href="#/tour"><span class="k">Start here</span><h3>Why an ontology?</h3>
        <p>Seven short steps: the same idea in different words, ideas that connect, kinds of idea, and what happens when the Manual changes.</p><span class="go">Take the tour →</span></a>
      <a class="door card" href="#/ask"><span class="k">Try it</span><h3>Ask the Manual</h3>
        <p>Ask in your own words. Watch the question find its ideas, follow their connections and gather the passages — then read a cited answer.</p><span class="go">Ask a question →</span></a>
      <a class="door card" href="#/map"><span class="k">Look around</span><h3>The map, at any level</h3>
        <p>Open a kind into its ideas, compare two kinds in detail with the rest in outline, and open an idea into the passages it rests on.</p><span class="go">Explore →</span></a>
      <a class="door card" href="#/change"><span class="k">The long game</span><h3>When the text changes</h3>
        <p>Pick any page of the Manual and see exactly which connections would need re-checking if it were rewritten — and what would not move.</p><span class="go">See the ripple →</span></a>
    </section>
  </div>`;

  drawPack(root, ontology, d3);
}

function rung(href, n, title, text, level) {
  return `<a class="rung" href="#/${href}" data-level="${level}">
    <span class="n num">${fmt(n)}</span>
    <span class="t"><b>${esc(title)}</b><span>${esc(text)}</span></span>
  </a>`;
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

  const families = ["reasoning", "process", "other"].map((family) => ({
    name: FAMILY_LABEL[family], type: "family", family,
    children: ontology.kinds.filter((k) => k.family === family).map((k) => ({
      name: k.label, type: "kind", kind: k.id, plain: k.plain,
      children: ontology.concepts.filter((x) => x.kind === k.id).map((x) => ({ name: x.label, type: "idea", id: x.id, kind: x.kind, origin: x.origin, value: 2 + Math.sqrt(x.mentions) })),
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
    if (d.data.type === "idea") return d.data.origin === "signed" ? kindColour(d.data.kind) : "var(--panel)";
    return "transparent";
  };
  const links = svg.append("g").attr("class", "pack-links").attr("pointer-events", "none");
  const circle = svg.append("g").selectAll("circle").data(nodes.descendants().slice(1)).join("circle")
    .attr("class", (d) => `pack-${d.data.type}${d.data.origin === "machine" ? " machine" : ""}`)
    .attr("fill", fillFor)
    .attr("stroke", (d) => (d.data.type === "family" ? "var(--line)" : kindColour(d.data.kind)))
    .attr("stroke-width", (d) => (d.data.type === "kind" ? 1.6 : d.data.type === "idea" ? 1.2 : 1))
    .attr("stroke-dasharray", (d) => (d.data.type === "family" || d.data.origin === "machine" ? "3 2" : null))
    .style("cursor", "pointer")
    .on("click", (event, d) => { event.stopPropagation(); if (focus !== d) zoom(d.data.type === "idea" ? d : d); })
    .on("mouseenter", (event, d) => { if (d.data.type === "idea") showLinks(d); })
    .on("mouseleave", () => links.selectAll("*").remove());
  circle.append("title").text((d) => (d.data.type === "idea" ? `${d.data.name} — ${d.data.origin === "signed" ? "signed by an expert" : "machine-written, unreviewed"}` : d.data.name));

  const label = svg.append("g").attr("pointer-events", "none").attr("text-anchor", "middle").selectAll("text")
    .data(nodes.descendants().slice(1)).join("text")
    .attr("class", (d) => `pack-label pack-label-${d.data.type}`)
    .style("display", (d) => (d.parent === nodes ? "inline" : "none"))
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
    for (const { id, r } of neighbours.get(d.data.id) || []) {
      const other = leafAt.get(id);
      if (!other) continue;
      const [x1, y1] = at(d), [x2, y2] = at(other);
      links.append("path").attr("d", `M${x1},${y1} Q${(x1 + x2) / 2 + (y2 - y1) * 0.15},${(y1 + y2) / 2 - (x2 - x1) * 0.15} ${x2},${y2}`)
        .attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-opacity", r.origin === "signed" ? 0.75 : 0.4)
        .attr("stroke-width", r.origin === "signed" ? 1.6 : 1).attr("stroke-dasharray", r.origin === "signed" ? null : "3 2");
    }
  }

  function describe(d) {
    const path = d.ancestors().reverse();
    crumbs.innerHTML = path.map((n, i) => i === path.length - 1 ? `<b>${esc(n.data.name)}</b>` : `<button type="button" data-depth="${i}">${esc(n.data.name)}</button>`).join(" › ");
    crumbs.querySelectorAll("[data-depth]").forEach((b) => b.addEventListener("click", () => zoom(path[Number(b.dataset.depth)])));
    const type = d.data.type;
    if (type === "root") {
      note.innerHTML = `<b>The whole ontology.</b> Two families of kinds, ${ontology.kinds.length - 1} kinds, ${fmt(ontology.concepts.length)} ideas — each circle sized by how many passages name it.
        <span class="muted">Click a family to go down a level; hover an idea to see its connections cross the kinds.</span>`;
    } else if (type === "family") {
      note.innerHTML = `<b>${esc(d.data.name)}.</b> ${d.children.length} kinds of idea. These rest on no single passage: a rewording of the Manual leaves them as they are.
        <span class="muted">Click a kind.</span>`;
    } else if (type === "kind") {
      const signed = d.leaves().filter((n) => n.data.origin === "signed").length;
      note.innerHTML = `<b>${esc(d.data.name)}</b> — ${esc(d.data.plain)}. ${d.leaves().length} ideas, ${signed} signed by an expert (filled) and
        ${d.leaves().length - signed} written by a machine (dashed). <a href="#/map/ideas">Open it on the map →</a>`;
    } else {
      const x = byId.get(d.data.id);
      const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
      note.innerHTML = `<div class="pack-idea"><b>${esc(x.label)}</b><div class="meta">${kindChip(x.kind, ontology)}${trustBadge(x.origin)}</div>
        ${first ? `<blockquote class="quote ${isLaw(first.ref) ? "law" : "manual"}">${esc(first.quote.length > 220 ? first.quote.slice(0, 218) + "…" : first.quote)}</blockquote>${refChip(first.ref)}` : ""}
        <p class="small" style="margin:.5rem 0 0">${fmt(x.mentions)} passages name it · ${(neighbours.get(x.id) || []).length} connections ·
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
