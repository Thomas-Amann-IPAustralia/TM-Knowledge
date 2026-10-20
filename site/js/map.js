/* The knowledge map: every idea and connection, drawn, to explore.

   Two views of the same records. Ideas: every idea a dot in its family's colour, sized by how often
   the Manual names it, placed by a seeded layout run to rest before drawing (netlayout.js), so the
   picture never moves under the reader. Hover an idea to see its neighbourhood; select one to
   focus it: its connections say what they mean, the passages and provisions it rests on appear
   round it, and its card says everything its record holds. Kinds: the shape of the model, the
   kinds of idea in their three families and how their members connect, rolled up.

   Names are placed, not piled: the most connected ideas are named first and a name that would
   overlap another waits until the reader zooms in. Text and strokes keep their size at any zoom.

   Nothing here decides which concepts or connections exist; every dot and line is a record. Every
   idea and connection is drawn the same way whoever wrote it; who wrote a record is on its card
   (ADR-0130). The Manual, the Act and the Regulations keep their own marks. Classes: `mp-`. */

import { esc, fmt, load, kindCount, refChip, refLabel, trustBadge, legend, sourceOf, isLaw, quoteBlock, definitionBlock, hierarchyBlock, qualifiedLine, structuresBlock, srcShape, FAMILIES, familyOf, tip } from "./app.js";
import { layoutIdeas, squeezeFor } from "./netlayout.js";
import { icon } from "./icons.js";
import * as lib from "./lib.js";

const LOOSE = new Set(["broader"]);
const FAMS = ["examined", "reasoning", "process"];

export async function render(root, { ontology, params }) {
  const [d3, Fuse, search] = await Promise.all([lib.d3(), lib.fuse(), load("search")]);
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  const relOf = new Map();
  for (const r of ontology.relations) for (const end of new Set([r.s, r.o])) { if (!relOf.has(end)) relOf.set(end, []); relOf.get(end).push(r); }
  const relById = new Map(ontology.relations.map((r) => [r.id, r]));
  const c = ontology.counts;
  const fam = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)] || FAMILIES.other;
  const pred = (p) => ontology.predicates[p]?.label || ontology.retired_predicates?.[p] || p;
  const name = (id) => byId.get(id)?.label || refLabel(id);

  const state = { mode: params[0] === "kinds" ? "kinds" : "ideas", selected: null, hover: null, kind: null, loose: false, trail: [] };
  const start = params.find((p) => byId.has(p)) || null;

  root.innerHTML = `
  <div class="mp">
    <aside class="mp-rail">
      <div class="mp-rail-head">
        <span class="eyebrow">Knowledge map</span>
        <h1>Every idea, and how they connect</h1>
        <p>${fmt(c.concepts.signed + c.concepts.machine)} ideas and ${fmt(c.relations.signed + c.relations.machine)} connections, each tied to the words it comes from.</p>
      </div>
      <div class="mp-find">
        <label class="mp-in">${icon("search")}<input type="search" placeholder="Find an idea" aria-label="Find an idea" autocomplete="off"></label>
        <div class="mp-results" role="listbox" aria-label="Ideas found"></div>
      </div>
      <div class="seg mp-seg" role="group" aria-label="What to show">
        <button type="button" data-mode="ideas" aria-pressed="${state.mode === "ideas"}">${icon("connect")} Ideas</button>
        <button type="button" data-mode="kinds" aria-pressed="${state.mode === "kinds"}">${icon("layers")} Kinds</button>
      </div>
      <div class="mp-fams">
        <p class="mp-rail-h">Highlight a kind</p>
        ${["reasoning", "examined", "process"].map((f) => `
        <div class="mp-fam"><p class="mp-fam-h"><i style="background:${FAMILIES[f].colour}"></i>${esc(FAMILIES[f].label)}</p>
          <ul>${ontology.kinds.filter((k) => k.family === f).map((k) => `<li><button type="button" class="mp-kind" data-kind="${k.id}" aria-pressed="false"><span>${esc(k.label)}</span><span class="tiny">${fmt(k.signed + k.machine)}</span></button></li>`).join("")}</ul></div>`).join("")}
      </div>
      <label class="mp-opt"><input type="checkbox" data-opt="loose"> Show the “is a kind of” links</label>
      <div class="mp-rail-foot">
        <p class="tiny">A dot's size is how often the Manual names the idea. Round a focused idea, the texts it rests on:</p>
        ${legend()}
        <a class="link-arrow" href="#/table/ideas">The same records as tables ${icon("arrow")}</a>
      </div>
    </aside>
    <div class="mp-canvas">
      <svg class="mp-svg" role="img" aria-label="A map of every idea and connection. Use the search or the kinds on the left, or the card on the right, to move through it by keyboard."></svg>
      <nav class="mp-trail" aria-label="Ideas visited"></nav>
      <div class="mp-zoom" role="group" aria-label="Zoom">
        <button type="button" data-z="in" title="Zoom in" aria-label="Zoom in">${icon("plus")}</button>
        <button type="button" data-z="out" title="Zoom out" aria-label="Zoom out">${icon("minus")}</button>
        <button type="button" data-z="fit" title="Show the whole map" aria-label="Show the whole map">${icon("fit")}</button>
      </div>
      <p class="mp-hint">Scroll to zoom · drag to move · click an idea to focus it</p>
    </div>
    <aside class="mp-card" aria-live="polite"></aside>
  </div>`;

  const canvas = root.querySelector(".mp-canvas");
  const svgEl = root.querySelector(".mp-svg");
  const card = root.querySelector(".mp-card");
  const svg = d3.select(svgEl);
  const size = () => ({ w: canvas.clientWidth || 900, h: canvas.clientHeight || 700 });
  // the picture takes the shape of its frame, so the frame is measured once laid out (Q-63)
  await new Promise((r) => requestAnimationFrame(r));
  const { at } = layoutIdeas(d3, ontology, { width: 1000, height: 640, pad: 30, squeeze: canvas.clientWidth ? squeezeFor(size().w, size().h) : 1 });

  // ---------------------------------------------------------------- the ideas view
  svg.append("defs").html(`<marker id="mp-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="mp-arrowhead"/></marker>
    <marker id="mp-karrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="mp-karrowhead"/></marker>`);
  const zoomLayer = svg.append("g").attr("class", "mp-zoomlayer");
  const gEdges = zoomLayer.append("g").attr("class", "mp-edges");
  const gSat = zoomLayer.append("g").attr("class", "mp-sats");
  const gNodes = zoomLayer.append("g").attr("class", "mp-nodes");
  const gLabels = zoomLayer.append("g").attr("class", "mp-labels");
  const gEdgeLabels = zoomLayer.append("g").attr("class", "mp-elabels");
  const gSatLabels = zoomLayer.append("g").attr("class", "mp-slabels");
  const gKinds = svg.append("g").attr("class", "mp-kindsview").style("display", "none");

  const edges = ontology.relations.filter((r) => at.has(r.s) && at.has(r.o) && r.s !== r.o);
  const edgeSel = gEdges.selectAll("line").data(edges, (r) => r.id).join("line")
    .attr("class", (r) => `mp-edge${LOOSE.has(r.p) ? " loose" : ""}`)
    .each(function (r) {
      // stop a little short of the far node, so a focused connection's arrow is seen
      const a = at.get(r.s), b = at.get(r.o), d = Math.hypot(b.x - a.x, b.y - a.y) || 1;
      d3.select(this).attr("x1", a.x).attr("y1", a.y).attr("x2", b.x - ((b.x - a.x) / d) * (b.r + 1.5)).attr("y2", b.y - ((b.y - a.y) / d) * (b.r + 1.5));
    });
  const degree = new Map(ontology.concepts.map((x) => [x.id, (relOf.get(x.id) || []).length]));
  const nodes = ontology.concepts.filter((x) => at.has(x.id));
  const nodeSel = gNodes.selectAll("circle").data(nodes, (x) => x.id).join("circle")
    .attr("cx", (x) => at.get(x.id).x).attr("cy", (x) => at.get(x.id).y).attr("r", (x) => at.get(x.id).r)
    .attr("class", "mp-node").style("fill", (x) => fam(x.id).colour);
  const labelSel = gLabels.selectAll("text").data(nodes, (x) => x.id).join("text").attr("class", "mp-label").text((x) => x.label);

  // ---------------------------------------------------------------- zoom: text and strokes keep their size
  let t = d3.zoomIdentity;
  const zoom = d3.zoom().scaleExtent([0.3, 8])
    .filter((e) => state.mode === "ideas" && (!e.ctrlKey || e.type === "wheel") && !e.button)
    .on("start", () => svgEl.classList.add("moving"))
    .on("zoom", (e) => {
      t = e.transform;
      zoomLayer.attr("transform", t);
      svgEl.style.setProperty("--inv", String(1 / t.k));
      placeSats();
    })
    .on("end", () => { svgEl.classList.remove("moving"); placeLabels(); });
  svg.call(zoom).on("dblclick.zoom", null);
  function fitTo(points, { pad = 70, max = 2.6, duration = 650 } = {}) {
    const { w, h } = size();
    const xs = points.map((p) => p.x), ys = points.map((p) => p.y);
    const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const s = Math.min(max, (w - 2 * pad) / Math.max(1, x1 - x0), (h - 2 * pad) / Math.max(1, y1 - y0));
    const to = d3.zoomIdentity.translate(w / 2 - s * (x0 + x1) / 2, h / 2 - s * (y0 + y1) / 2).scale(s);
    if (duration) svg.transition().duration(duration).call(zoom.transform, to);
    else { svg.call(zoom.transform, to); placeLabels(); }
  }
  const fitAll = (duration = 0) => fitTo([...at.values()].flatMap((p) => [{ x: p.x - 40, y: p.y - 30 }, { x: p.x + 60, y: p.y + 10 }]), { pad: 20, max: 2, duration });

  // ---------------------------------------------------------------- names, placed so none overlaps another
  const measure = document.createElement("canvas").getContext("2d");
  const widthOf = (text, px, weight = 600) => { measure.font = `${weight} ${px}px "Inter Variable", system-ui, sans-serif`; return measure.measureText(text).width; };
  const labelW = new Map(nodes.map((x) => [x.id, widthOf(x.label, 11.5)]));
  const score = (x) => degree.get(x.id) + x.mentions / 20;
  const byScore = [...nodes].sort((a, b) => score(b) - score(a));
  const neighbours = (id) => new Set((relOf.get(id) || []).flatMap((r) => [r.s, r.o]).filter((x) => x !== id && at.has(x)));
  const overlaps = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];

  function placeLabels() {
    const { w, h } = size();
    const focus = state.selected || state.hover;
    const near = focus ? neighbours(focus) : null;
    const lit = (id) => (focus ? id === focus || near.has(id) : state.kind ? byId.get(id).kind === state.kind : true);
    const order = focus ? [byId.get(focus), ...byScore.filter((x) => near.has(x.id))] : byScore.filter((x) => lit(x.id));
    const inside = (b) => b[0] >= 4 && b[2] <= w - 4 && b[1] >= 4 && b[3] <= h - 4;
    // every lit dot, and every mark round a focused one, is an obstacle a name must not cover;
    // a faded dot may be written over
    const placed = nodes.filter((x) => lit(x.id)).map((x) => {
      const p = at.get(x.id), sx = t.applyX(p.x), sy = t.applyY(p.y), r = p.r * t.k + 1;
      return [sx - r, sy - r, sx + r, sy + r, x.id];
    });
    const satAt = sats.map((d) => { const [x, y] = satPos(d); return [t.applyX(x), t.applyY(y)]; });
    for (const [sx, sy] of satAt) placed.push([sx - 7, sy - 7, sx + 7, sy + 7, null]);
    // and so are the controls floating over the picture
    const frame = canvas.getBoundingClientRect();
    for (const el of canvas.querySelectorAll(".mp-zoom, .mp-hint, .mp-crumb")) {
      const r = el.getBoundingClientRect();
      if (r.width) placed.push([r.left - frame.left - 4, r.top - frame.top - 4, r.right - frame.left + 4, r.bottom - frame.top + 4, null]);
    }
    const free = (b, id) => inside(b) && !placed.some((q) => (id == null || q[4] !== id) && overlaps(q, b));
    // to the right, the left, above, below: the first that is free
    const spots = (sx, sy, gap, wd) => [
      ["start", sx + gap, sy, [sx + gap - 2, sy - 8, sx + gap + wd + 2, sy + 7]],
      ["end", sx - gap, sy, [sx - gap - wd - 2, sy - 8, sx - gap + 2, sy + 7]],
      ["middle", sx, sy - gap - 6, [sx - wd / 2 - 2, sy - gap - 14, sx + wd / 2 + 2, sy - gap + 1]],
      ["middle", sx, sy + gap + 7, [sx - wd / 2 - 2, sy + gap - 1, sx + wd / 2 + 2, sy + gap + 14]],
    ];
    const spot = new Map();
    for (const x of order) {
      const p = at.get(x.id), sx = t.applyX(p.x), sy = t.applyY(p.y);
      const options = spots(sx, sy, p.r * t.k + 4, labelW.get(x.id) * (x.id === state.selected ? 1.15 : 1));
      const pick = options.find((o) => free(o[3], x.id)) || (x.id === focus ? options[0] : null);
      if (!pick) continue;
      placed.push([...pick[3], null]);
      spot.set(x.id, pick);
    }
    labelSel.classed("show", (x) => spot.has(x.id)).classed("sel", (x) => x.id === state.selected)
      .attr("text-anchor", (x) => spot.get(x.id)?.[0] || "start")
      .attr("x", (x) => (spot.has(x.id) ? t.invertX(spot.get(x.id)[1]) : at.get(x.id).x))
      .attr("y", (x) => (spot.has(x.id) ? t.invertY(spot.get(x.id)[2]) : at.get(x.id).y))
      .attr("dy", "0.35em");
    // the texts a focused idea rests on, named beside their marks where there is room
    const named = [];
    sats.forEach((d, i) => {
      const [sx, sy] = satAt[i], text = refLabel(d.ref), wd = widthOf(text, 10.5, 600);
      const pick = spots(sx, sy, 9, wd).slice(0, 2).find((o) => free(o[3]));
      if (!pick) return;
      placed.push([...pick[3], null]);
      named.push({ d, text, anchor: pick[0], x: t.invertX(pick[1]), y: t.invertY(pick[2]) });
    });
    gSatLabels.selectAll("text").data(named, (n) => n.d.ref).join("text")
      .attr("class", (n) => `mp-slabel ${sourceOf(n.d.ref) === "manual" ? "manual" : `law ${sourceOf(n.d.ref)}`}`)
      .attr("x", (n) => n.x).attr("y", (n) => n.y).attr("dy", "0.35em").attr("text-anchor", (n) => n.anchor).text((n) => n.text);
    // what each focused connection says, where there is room for it
    const hot = state.selected ? edges.filter((r) => (r.s === state.selected || r.o === state.selected)) : [];
    const said = [];
    for (const r of hot) {
      const a = at.get(r.s), b = at.get(r.o);
      const mx = t.applyX((a.x + b.x) / 2), my = t.applyY((a.y + b.y) / 2), wd = widthOf(pred(r.p), 10.5, 500);
      const box = [mx - wd / 2 - 3, my - 8, mx + wd / 2 + 3, my + 6];
      if (!free(box)) continue;
      placed.push([...box, null]);
      said.push({ r, x: t.invertX(mx), y: t.invertY(my) });
    }
    gEdgeLabels.selectAll("text").data(said, (d) => d.r.id).join("text").attr("class", "mp-elabel")
      .attr("x", (d) => d.x).attr("y", (d) => d.y).attr("dy", "0.35em").attr("text-anchor", "middle").text((d) => pred(d.r.p));
  }

  // ---------------------------------------------------------------- focus, hover, select
  function paint() {
    const focus = state.selected || state.hover, kind = state.kind;
    const near = focus ? neighbours(focus) : null;
    const lit = (id) => (focus ? id === focus || near.has(id) : kind ? byId.get(id)?.kind === kind : true);
    const touches = (r) => r.s === focus || r.o === focus;
    nodeSel.classed("dim", (x) => !lit(x.id)).classed("sel", (x) => x.id === state.selected).classed("near", (x) => !!state.selected && near.has(x.id));
    edgeSel.classed("hot", (r) => !!focus && touches(r))
      .classed("dim", (r) => (focus ? !touches(r) : kind ? !(lit(r.s) && lit(r.o)) : false))
      .style("display", (r) => (LOOSE.has(r.p) && !state.loose && !(focus && touches(r)) ? "none" : null))
      .attr("marker-end", (r) => (focus && touches(r) ? "url(#mp-arrow)" : null));
    svgEl.classList.toggle("focused", !!focus || !!kind);
    satellites(state.selected);
    placeLabels();
  }

  /** The passages and provisions a selected idea rests on, round it: the Manual's as blue squares,
      the Act's as amber diamonds, the Regulations' as plum hexagons. They fan out on the side
      away from its connections, so they never sit on top of them. */
  let sats = [];
  function satellites(id) {
    sats = [];
    if (id) {
      const x = byId.get(id), p = at.get(id);
      const refs = [...new Set([...(x.sources || []), ...(x.basis || []).filter(isLaw)])].slice(0, 9);
      const others = [...neighbours(id)].map((n) => at.get(n));
      const away = others.length ? Math.atan2(p.y - d3.mean(others, (o) => o.y), p.x - d3.mean(others, (o) => o.x)) : -Math.PI / 2;
      refs.forEach((ref, i) => sats.push({ ref, i, n: refs.length, away, own: (x.sources || []).includes(ref) }));
    }
    gSat.selectAll("line").data(sats, (d) => d.ref).join("line").attr("class", "mp-satline");
    gSat.selectAll("g.mp-sat").data(sats, (d) => d.ref).join((enter) => {
      const g = enter.append("g").attr("class", (d) => `mp-sat ${sourceOf(d.ref) === "manual" ? "manual" : `law ${sourceOf(d.ref)}`}`).attr("data-ref", (d) => d.ref)
        .attr("data-tip", (d) => `<span class="tip-k">${sourceOf(d.ref) === "manual" ? "Manual · practice" : sourceOf(d.ref) === "act" ? "Act · law" : "Regulations · law"}</span><b>${esc(refLabel(d.ref))}</b><span class="tip-s">${d.own ? "A passage this idea rests on" : "A provision this idea rests on"}. Click to read it.</span>`);
      g.append("g").attr("class", "mp-sat-in").html((d) => `<circle r="11" class="mp-sat-hit"/>${srcShape(sourceOf(d.ref), 5.4)}`);
      return g;
    });
    placeSats();
  }
  /** Where a mark sits: a fixed distance from its idea on screen, whatever the zoom. */
  function satPos(d) {
    const p = at.get(state.selected), out = p.r * t.k + 30;
    const a = d.away + (d.i - (d.n - 1) / 2) * Math.min(0.5, 19 / out);
    return [p.x + (out / t.k) * Math.cos(a), p.y + (out / t.k) * Math.sin(a)];
  }
  function placeSats() {
    if (!sats.length) return;
    const p = at.get(state.selected);
    gSat.selectAll("line").attr("x1", p.x).attr("y1", p.y).attr("x2", (d) => satPos(d)[0]).attr("y2", (d) => satPos(d)[1]);
    gSat.selectAll("g.mp-sat").attr("transform", (d) => `translate(${satPos(d)[0]},${satPos(d)[1]})`);
    gSat.selectAll(".mp-sat-in").attr("transform", `scale(${1 / t.k})`);
  }

  function select(id, { pan = true, trail = true } = {}) {
    if (!byId.has(id)) return;
    if (trail && state.selected && state.selected !== id) state.trail = [...state.trail.filter((h) => h !== state.selected && h !== id), state.selected].slice(-4);
    state.selected = id;
    state.hover = null;
    setKind(null);
    history.replaceState(null, "", `#/map/ideas/${id}`);
    showConcept(byId.get(id));
    card.scrollTop = 0;
    drawTrail();
    paint();
    if (pan) fitTo([at.get(id), ...[...neighbours(id)].map((n) => at.get(n))], { pad: 90, max: 2.4 });
  }
  function clearSelection() {
    state.selected = null;
    state.hover = null;
    state.trail = [];
    setKind(null);
    history.replaceState(null, "", "#/map");
    overview();
    drawTrail();
    paint();
  }
  function drawTrail() {
    const list = [...state.trail, state.selected].filter(Boolean);
    root.querySelector(".mp-trail").innerHTML = list.length
      ? `<button type="button" class="mp-crumb all" data-all>${icon("fit")}Whole map</button>${list.map((id) => `<span class="mp-sep" aria-hidden="true">›</span><button type="button" class="mp-crumb${id === state.selected ? " on" : ""}" data-c="${id}"${id === state.selected ? ' aria-current="true"' : ""}><i style="background:${fam(id).colour}"></i>${esc(name(id))}</button>`).join("")}`
      : "";
  }

  const between = (a, b) => (relOf.get(a) || []).filter((r) => (r.s === a && r.o === b) || (r.s === b && r.o === a));
  const nodeTip = (x) => {
    const head = `<span class="tip-k">${esc(kinds.get(x.kind)?.label || "")}</span><b>${esc(x.label)}</b>`;
    if (state.selected && state.selected !== x.id) {
      const rs = between(state.selected, x.id);
      if (rs.length) return `${head}${rs.map((r) => `<span class="tip-s">${esc(name(r.s))} <i>${esc(pred(r.p))}</i> ${esc(name(r.o))}</span>`).join("")}<span class="tip-s">Click to focus it.</span>`;
    }
    return `${head}<span class="tip-s">${fmt(degree.get(x.id))} connection${degree.get(x.id) === 1 ? "" : "s"} · named in ${fmt(x.mentions)} passage${x.mentions === 1 ? "" : "s"}</span>`;
  };
  nodeSel.on("mouseenter", (e, x) => {
    if (!state.selected && state.hover !== x.id) { state.hover = x.id; paint(); }
    tip(nodeTip(x), e);
  }).on("mousemove", (e, x) => tip(nodeTip(x), e))
    .on("mouseleave", () => { tip(null); if (state.hover) { state.hover = null; paint(); } })
    .on("click", (e, x) => { e.stopPropagation(); select(x.id); });
  svg.on("click", (e) => { if (state.mode === "ideas" && (e.target === svgEl || e.target.closest(".mp-famlabels, .mp-edges"))) { if (state.selected || state.kind) clearSelection(); } });
  gSat.on("mousemove", (e) => { const s = e.target.closest("[data-tip]"); tip(s ? s.dataset.tip : null, e); }).on("mouseleave", () => tip(null));

  // ---------------------------------------------------------------- the card
  const legendInline = `<span class="manual"><i class="mark"></i></span> the Manual, <span class="law act"><i class="mark"></i></span> the Act, <span class="law regs"><i class="mark"></i></span> the Regulations`;
  function overview() {
    const busiest = [...nodes].sort((a, b) => degree.get(b.id) - degree.get(a.id)).slice(0, 6);
    card.innerHTML = `
      <span class="eyebrow">How to read it</span>
      <h2>A map of what the Manual means</h2>
      <p>Each dot is an <b>idea</b> examiners reason with. Each line is a <b>connection</b> between two ideas that says what it means and quotes the sentence it rests on.</p>
      <div class="mp-famcards">${["reasoning", "examined", "process"].map((f) => `
        <div class="mp-famcard"><i style="background:${FAMILIES[f].colour}"></i><div><b>${esc(FAMILIES[f].label)}</b>
        <span>${ontology.kinds.filter((k) => k.family === f).map((k) => esc(k.label.toLowerCase())).join(", ")}</span></div></div>`).join("")}</div>
      <h4>Start with one of the most connected</h4>
      <div class="mp-starts">${busiest.map((x) => `<button type="button" class="chip" data-c="${x.id}"><i class="dot" style="--c:${fam(x.id).colour}"></i>${esc(x.label)} <span class="tiny">${fmt(degree.get(x.id))}</span></button>`).join("")}</div>
      <ul class="mp-how">
        <li>${icon("eye")}<span><b>Hover</b> over an idea to see what it connects to.</span></li>
        <li>${icon("target")}<span><b>Click</b> it to focus it: its connections say what they mean, and the texts it rests on gather round it (${legendInline}).</span></li>
        <li>${icon("layers")}<span><b>Kinds</b>, at the top left, shows the shape of the whole model.</span></li>
      </ul>
      <p class="tiny">${fmt(c.concepts.machine)} of the ${fmt(c.concepts.signed + c.concepts.machine)} ideas and ${fmt(c.relations.machine)} of the ${fmt(c.relations.signed + c.relations.machine)} connections were written by a machine and have not been reviewed by an expert. The map draws every record alike, whoever wrote it; each card says which.</p>`;
  }

  // Each author rates itself on its own scale, so a score is shown with its author and never
  // compared, ranked or filtered across authors (review F6, ADR-0125).
  const selfRated = (m) => `<span title="The author's rating of its own record, on its own scale. Not comparable across authors.">self-rated ${esc(m.confidence)} by <code>${esc(m.by || "?")}</code></span>`;

  function relationCard(r) {
    return `<div class="mp-relcard">
      <p class="mp-rel-s"><b>${esc(name(r.s))}</b> <span class="mp-p">${esc(pred(r.p))}</span> <b>${esc(name(r.o))}</b>${r.modality ? ` <span class="chip">${esc(r.modality)}</span>` : ""}</p>
      ${qualifiedLine(r)}
      ${r.quote ? quoteBlock(r.ref, r.quote) : ""}
      <p class="row wrap-ok">${r.ref ? refChip(r.ref) : ""}${trustBadge(r.origin)}<span class="tiny">${esc(r.id)}</span></p>
      ${r.replaces ? `<p class="tiny">A corrected reading of ${esc(r.replaces)}, which is kept unchanged.</p>` : ""}
      ${r.machine?.reasoning ? `<details class="quiet"><summary>Why the machine wrote this</summary><div class="det-body"><p class="small">${esc(r.machine.reasoning)}</p>${r.machine.confidence ? `<p class="tiny">${selfRated(r.machine)}</p>` : ""}</div></details>` : ""}
    </div>`;
  }

  function showConcept(x) {
    const rels = relOf.get(x.id) || [];
    const groups = new Map();
    for (const r of rels) {
      const outgoing = r.s === x.id;
      const key = `${outgoing ? "out" : "in"}:${r.p}`;
      if (!groups.has(key)) groups.set(key, { outgoing, p: r.p, items: [] });
      groups.get(key).items.push({ r, other: outgoing ? r.o : r.s });
    }
    const ordered = [...groups.values()].sort((a, b) => (LOOSE.has(a.p) - LOOSE.has(b.p)) || b.items.length - a.items.length);
    const refs = [...new Set(search.mentions[x.id] || [])];
    const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
    const k = kinds.get(x.kind), f = fam(x.id);
    const law = ["act", "regs"].map((src) => [src, x.basis.filter((r) => sourceOf(r) === src)]).filter(([, list]) => list.length);
    card.innerHTML = `
      <div class="mp-card-top"><span class="mp-kindtag" style="--c:${f.colour};--cb:${f.bg};--ci:${f.ink}"><i></i>${esc(k?.label || x.kind)}</span>${trustBadge(x.origin)}</div>
      <h2>${esc(x.label)}</h2>
      <p class="tiny">${esc(FAMILIES[familyOf(ontology, x.kind)].label)}${k?.plain ? ` · ${esc(k.plain)}` : ""}</p>
      ${x.alt.length ? `<p class="small"><span class="muted">Also called</span> ${x.alt.map(esc).join(" · ")}</p>` : ""}
      ${x.not.length ? `<p class="small"><span class="muted">Not the same as</span> ${x.not.map(esc).join(" · ")}</p>` : ""}
      ${definitionBlock(x.definition)}
      ${first ? `<h4>What it rests on</h4>${quoteBlock(first.ref, first.quote)}<p class="row wrap-ok">${refChip(first.ref)}<span class="tiny">${first.for === "kind" ? "quoted when its kind was judged" : "quoted by the record itself"}</span></p>` : ""}
      ${law.map(([src, list]) => `<h4>In the ${src === "act" ? "Act" : "Regulations"}</h4><p class="row wrap-ok">${list.map((r) => refChip(r)).join("")}</p>`).join("")}
      ${hierarchyBlock(x, (id) => `<button class="link" type="button" data-c="${esc(id)}">${esc(name(id))}</button>`)}
      ${structuresBlock(x, ontology)}
      <h4>Connections · ${fmt(rels.length)}</h4>
      ${ordered.length ? ordered.map((grp) => `
        <div class="mp-group"><p class="mp-gh">${grp.outgoing ? `It <b>${esc(pred(grp.p))}</b>` : `<b>${esc(pred(grp.p))}</b> it`}</p>
        <ul class="mp-rels">${grp.items.map(({ r, other }) => `<li><div class="mp-relrow">
          ${byId.has(other) ? `<button class="mp-other" type="button" data-c="${other}"><i style="background:${fam(other).colour}"></i>${esc(name(other))}</button>` : refChip(other)}
          <button class="mp-why" type="button" data-r="${r.id}" aria-expanded="false">Why?</button></div></li>`).join("")}</ul></div>`).join("")
        : `<p class="empty small">No connections recorded.</p>`}
      <h4>Where the Manual names it</h4>
      <p class="small">${fmt(refs.length)} passage${refs.length === 1 ? "" : "s"}, in ${x.parts.map((p) => esc(p.replace("Part", "Part "))).join(", ")}.</p>
      ${refs.length ? `<details class="quiet"><summary>List the passages</summary><div class="det-body"><p class="row wrap-ok">${refs.slice(0, 60).map((r) => refChip(r, ` data-hl="${esc([x.label, ...x.alt].join("|"))}"`)).join("")}</p>${refs.length > 60 ? `<p class="tiny">and ${fmt(refs.length - 60)} more.</p>` : ""}</div></details>` : ""}
      ${x.notes ? `<h4>Note on the record</h4><p class="small">${esc(x.notes)}</p>` : ""}
      ${provenance(x)}`;
  }

  function provenance(x) {
    const rows = [];
    if (x.signed) rows.push(`<p class="small">Reviewed by a trade marks expert on ${esc(x.signed.date)}.</p>`);
    if (x.corrected) rows.push(`<p class="small"><b>Corrected since it was reviewed</b> (${x.corrected.map(esc).join(", ")}): a machine-written, unreviewed change made on the project owner's instruction. The labels and provisions shown are the corrected ones; the reviewed record itself is kept unchanged.</p>`);
    if (x.machine) {
      rows.push(`<p class="small">Written by <code>${esc(x.machine.by)}</code> on ${esc(x.machine.date)} · <b>${esc(x.machine.review_status)}</b>${x.machine.confidence ? ` · ${selfRated(x.machine)}` : ""}.</p>`);
      if (x.machine.reasoning) rows.push(`<p class="small muted">${esc(x.machine.reasoning)}</p>`);
      if (x.machine.check) rows.push(`<p class="small"><b>What an expert should check:</b> ${esc(x.machine.check)}</p>`);
    }
    if (x.typed) rows.push(`<p class="small">Its kind was judged by <code>${esc(x.typed.by)}</code> on ${esc(x.typed.date)} · <b>${esc(x.typed.review_status)}</b>.</p>`);
    return `<details class="quiet"><summary>Who wrote this record</summary><div class="det-body">${rows.join("")}</div></details>`;
  }

  function showKind(kid) {
    const kd = kinds.get(kid), f = FAMILIES[kd.family];
    const members = ontology.concepts.filter((x) => x.kind === kid).sort((a, b) => b.mentions - a.mentions);
    const strong = (r) => r.total - (r.predicates.broader || 0);
    const says = (r) => Object.entries(r.predicates).filter(([p]) => !LOOSE.has(p)).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([p, n]) => `${esc(pred(p))} (${n})`).join(", ");
    const rows = (list, end) => (list.length ? `<ul class="mp-krows">${list.map((r) => `<li><button type="button" class="link" data-kind="${r[end]}">${esc(kinds.get(r[end]).label)}</button><span class="tiny">${says(r)}</span></li>`).join("")}</ul>` : `<p class="empty small">None.</p>`);
    const out = ontology.kind_links.filter((r) => r.s === kid && r.o !== kid && strong(r) > 0).sort((a, b) => strong(b) - strong(a)).slice(0, 4);
    const inn = ontology.kind_links.filter((r) => r.o === kid && r.s !== kid && strong(r) > 0).sort((a, b) => strong(b) - strong(a)).slice(0, 4);
    card.innerHTML = `
      <div class="mp-card-top"><span class="mp-kindtag" style="--c:${f.colour};--cb:${f.bg};--ci:${f.ink}"><i></i>${esc(f.label)}</span></div>
      <h2>${esc(kd.label)}</h2>
      <p>${esc(kd.plain.charAt(0).toUpperCase() + kd.plain.slice(1))}.</p>
      <p class="tiny">${fmt(members.length)} ideas. Which kind each idea is was judged by a machine and has not been reviewed.</p>
      <h4>Its ideas connect most to</h4>${rows(out, "o")}
      <h4>Ideas that connect most to it</h4>${rows(inn, "s")}
      <h4>Its ideas</h4>
      <div class="mp-starts">${members.map((x) => `<button type="button" class="chip" data-c="${x.id}"><i class="dot" style="--c:${f.colour}"></i>${esc(x.label)}</button>`).join("")}</div>`;
  }

  function setKind(kid) {
    state.kind = kid;
    root.querySelectorAll(".mp-kind").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.kind === kid)));
  }
  function highlightKind(kid) {
    const on = state.kind === kid && state.mode === "ideas" ? null : kid;
    state.selected = null;
    state.hover = null;
    state.trail = [];
    if (state.mode !== "ideas") setMode("ideas", { quiet: true });
    setKind(on);
    drawTrail();
    paint();
    if (on) {
      showKind(on);
      history.replaceState(null, "", "#/map");
      fitTo(nodes.filter((x) => x.kind === on).map((x) => at.get(x.id)), { pad: 110, max: 2.2 });
    } else { overview(); fitAll(500); }
  }

  // ---------------------------------------------------------------- the kinds view
  function drawKinds() {
    const { w, h } = size();
    gKinds.selectAll("*").remove();
    const colX = { examined: w * 0.2, reasoning: w * 0.5, process: w * 0.8 };
    const pos = new Map();
    const rad = (kd) => 30 + 5 * Math.sqrt(kd.signed + kd.machine);
    for (const f of FAMS) {
      const list = ontology.kinds.filter((kd) => kd.family === f);
      const top = 112, span = h - top - 64;
      list.forEach((kd, i) => pos.set(kd.id, { x: colX[f] + (list.length > 2 ? (i % 2 ? 40 : -40) : 0), y: top + (list.length > 1 ? (span * i) / (list.length - 1) : span / 2), r: rad(kd) }));
      gKinds.append("text").attr("x", colX[f]).attr("y", 46).attr("text-anchor", "middle").attr("class", "mp-kfam").text(FAMILIES[f].label.toUpperCase());
    }
    const strong = (r) => r.total - (r.predicates.broader || 0);
    const linksK = ontology.kind_links.filter((r) => r.s !== r.o && pos.has(r.s) && pos.has(r.o) && strong(r) > 0);
    const max = d3.max(linksK, strong) || 1;
    const best = new Map();
    for (const r of linksK) if (!best.has(r.s) || strong(best.get(r.s)) < strong(r)) best.set(r.s, r);
    const top = (r) => Object.entries(r.predicates).filter(([q]) => !LOOSE.has(q)).sort((a, b) => b[1] - a[1]);
    const gl = gKinds.append("g"), gb = gKinds.append("g"), gt = gKinds.append("g");
    const labels = [];
    for (const r of [...linksK].sort((a, b) => strong(a) - strong(b))) {
      const a = pos.get(r.s), b = pos.get(r.o);
      const dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1;
      const sx = a.x + (dx / d) * a.r, sy = a.y + (dy / d) * a.r, ex = b.x - (dx / d) * (b.r + 3), ey = b.y - (dy / d) * (b.r + 3);
      const mx = (sx + ex) / 2 - (dy / d) * 26, my = (sy + ey) / 2 + (dx / d) * 26;
      const lead = best.get(r.s) === r;
      // a single connection between two kinds is drawn faintly; hover over a kind to see all of its own
      gl.append("path").attr("d", `M${sx},${sy} Q${mx},${my} ${ex},${ey}`).attr("class", `mp-klink${lead ? " lead" : ""}${strong(r) < 2 ? " faint" : ""}`)
        .attr("stroke-width", 1 + 6 * (strong(r) / max)).attr("marker-end", "url(#mp-karrow)")
        .attr("data-s", r.s).attr("data-o", r.o)
        .attr("data-tip", `<span class="tip-k">${fmt(strong(r))} connection${strong(r) === 1 ? "" : "s"}</span><b>${esc(kinds.get(r.s).label)} → ${esc(kinds.get(r.o).label)}</b>${top(r).slice(0, 4).map(([p, n]) => `<span class="tip-s">${esc(pred(p))} · ${n}</span>`).join("")}`);
      if (lead && top(r).length) labels.push({ text: pred(top(r)[0][0]), x: (sx + 2 * mx + ex) / 4, y: (sy + 2 * my + ey) / 4 });
    }
    for (const kd of ontology.kinds) {
      const p = pos.get(kd.id);
      if (!p) continue;
      const f = FAMILIES[kd.family];
      const g = gb.append("g").attr("class", "mp-kbubble").attr("transform", `translate(${p.x},${p.y})`).attr("data-kind", kd.id)
        .attr("data-tip", `<span class="tip-k">${esc(f.label)}</span><b>${esc(kd.label)}</b><span class="tip-s">${esc(kd.plain)}. Click to see its ideas on the map.</span>`);
      g.append("circle").attr("r", p.r).style("fill", f.bg).style("stroke", f.colour);
      // a name too wide for its bubble takes two lines, broken at the space nearest its middle
      const words = kd.label.split(" ");
      let lines = [kd.label];
      if (words.length > 1 && widthOf(kd.label, 13, 650) > 1.6 * p.r) {
        const cut = d3.minIndex(words.slice(1), (_, i) => Math.abs(words.slice(0, i + 1).join(" ").length - kd.label.length / 2)) + 1;
        lines = [words.slice(0, cut).join(" "), words.slice(cut).join(" ")];
      }
      lines.forEach((line, i) => g.append("text").attr("y", (lines.length === 2 ? -11 : -3) + i * 15).attr("text-anchor", "middle").attr("class", "mp-kname").text(line));
      g.append("text").attr("y", lines.length === 2 ? 22 : 14).attr("text-anchor", "middle").attr("class", "mp-kn").text(`${kd.signed + kd.machine} ideas`);
    }
    // the labels go on top, and only where they cover no bubble and no other label
    const taken = [...pos.values()].map((p) => [p.x - p.r, p.y - p.r, p.x + p.r, p.y + p.r]);
    for (const l of labels) {
      const wd = widthOf(l.text, 12.5, 500), box = [l.x - wd / 2 - 3, l.y - 9, l.x + wd / 2 + 3, l.y + 8];
      if (taken.some((q) => overlaps(q, box))) continue;
      taken.push(box);
      gt.append("text").attr("x", l.x).attr("y", l.y).attr("dy", "0.35em").attr("text-anchor", "middle").attr("class", "mp-klabel").text(l.text);
    }
    gKinds.on("click", (e) => { const b = e.target.closest("[data-kind]"); if (b) highlightKind(b.dataset.kind); })
      .on("mouseover", (e) => {
        const b = e.target.closest("[data-kind]");
        gKinds.classed("focusing", !!b);
        gKinds.selectAll(".mp-klink").classed("on", function () { return !!b && (this.dataset.s === b.dataset.kind || this.dataset.o === b.dataset.kind); });
      })
      .on("mousemove", (e) => { const s = e.target.closest("[data-tip]"); tip(s ? s.dataset.tip : null, e); })
      .on("mouseleave", () => { tip(null); gKinds.classed("focusing", false); });
  }
  function kindsCard() {
    card.innerHTML = `
      <span class="eyebrow">Kinds</span>
      <h2>The shape of the model</h2>
      <p>Every idea is sorted by <b>what it is</b> into one of ${fmt(kindCount(ontology))} kinds, in three families: the questions the law asks, what those questions are asked about, and the process around them.</p>
      <p><b>What an idea does is a connection, not a kind.</b> Sign content <i>may give rise to</i> a ground; context <i>qualifies</i> a test; a ground <i>is overcome by</i> its remedy; a role <i>performs</i> a step. Each connection names the kinds it may join, so the kinds connect in known ways.</p>
      <p class="small muted">Each arrow rolls up the connections between two kinds' ideas: the thicker, the more. The strongest out of each kind is labelled. Hover over a kind to trace its arrows; click it to see its ideas.</p>
      <h4>The kinds</h4>
      <ul class="mp-klist">${ontology.kinds.filter((kd) => kd.family !== "other").map((kd) => `<li><button type="button" class="link" data-kind="${kd.id}"><i style="background:${FAMILIES[kd.family].colour}"></i>${esc(kd.label)}</button><span class="tiny">${esc(kd.plain)}</span></li>`).join("")}</ul>`;
  }

  function setMode(mode, { quiet = false } = {}) {
    state.mode = mode;
    root.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === mode)));
    zoomLayer.style("display", mode === "ideas" ? null : "none");
    gKinds.style("display", mode === "kinds" ? null : "none");
    canvas.classList.toggle("kinds", mode === "kinds");
    tip(null);
    if (mode === "kinds") {
      drawKinds();
      kindsCard();
      history.replaceState(null, "", "#/map/kinds");
    } else if (!quiet) {
      if (state.selected) select(state.selected, { trail: false });
      else { overview(); history.replaceState(null, "", "#/map"); fitAll(0); paint(); }
    }
  }

  // ---------------------------------------------------------------- the rail, the card's links, search
  root.querySelector(".mp-seg").addEventListener("click", (e) => { const b = e.target.closest("[data-mode]"); if (b && b.dataset.mode !== state.mode) setMode(b.dataset.mode); });
  root.querySelector(".mp-fams").addEventListener("click", (e) => { const b = e.target.closest("[data-kind]"); if (b) highlightKind(b.dataset.kind); });
  root.querySelector("[data-opt=loose]").addEventListener("change", (e) => { state.loose = e.target.checked; paint(); });
  const goTo = (id) => { if (state.mode !== "ideas") setMode("ideas", { quiet: true }); select(id); };
  card.addEventListener("click", (e) => {
    const go = e.target.closest("[data-c]");
    if (go) { goTo(go.dataset.c); return; }
    const kd = e.target.closest("[data-kind]");
    if (kd) { highlightKind(kd.dataset.kind); return; }
    const why = e.target.closest("[data-r]");
    if (why) {
      const li = why.closest("li");
      const open = li.querySelector(".mp-relcard");
      if (open) { open.remove(); why.setAttribute("aria-expanded", "false"); return; }
      li.insertAdjacentHTML("beforeend", relationCard(relById.get(why.dataset.r)));
      why.setAttribute("aria-expanded", "true");
    }
  });
  card.addEventListener("mouseover", (e) => {
    // pointing at a connection in the card lights it on the map
    const row = e.target.closest(".mp-relrow [data-c]");
    nodeSel.classed("pointed", (x) => !!row && x.id === row.dataset.c);
  });
  root.querySelector(".mp-trail").addEventListener("click", (e) => {
    if (e.target.closest("[data-all]")) { clearSelection(); fitAll(600); return; }
    const b = e.target.closest("[data-c]");
    if (b) select(b.dataset.c, { trail: false });
  });
  root.querySelector(".mp-zoom").addEventListener("click", (e) => {
    const z = e.target.closest("button")?.dataset.z;
    if (state.mode !== "ideas") return;
    if (z === "in") svg.transition().duration(300).call(zoom.scaleBy, 1.5);
    else if (z === "out") svg.transition().duration(300).call(zoom.scaleBy, 1 / 1.5);
    else if (z === "fit") fitAll(500);
  });

  const fuse = new Fuse(ontology.concepts.map((x) => ({ id: x.id, label: x.label, alt: x.alt, kind: x.kind })),
    { keys: [{ name: "label", weight: 2 }, "alt"], threshold: 0.38, ignoreLocation: true });
  const find = root.querySelector(".mp-find input");
  const results = root.querySelector(".mp-results");
  find.addEventListener("input", () => {
    const q = find.value.trim();
    if (q.length < 2) { results.innerHTML = ""; return; }
    const hits = fuse.search(q, { limit: 8 }).map((hit) => hit.item);
    results.innerHTML = hits.map((hit) => `<button type="button" data-c="${hit.id}" role="option"><i style="background:${fam(hit.id).colour}"></i><span>${esc(hit.label)}</span><span class="tiny">${esc(kinds.get(hit.kind)?.label || "")}</span></button>`).join("")
      || `<p class="tiny">No idea by that name. Try another word for it, or <a href="#/ask">ask the Manual</a>.</p>`;
  });
  find.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); results.querySelector("[data-c]")?.click(); }
    if (e.key === "ArrowDown") { e.preventDefault(); results.querySelector("[data-c]")?.focus(); }
  });
  results.addEventListener("keydown", (e) => {
    const b = e.target.closest("[data-c]");
    if (!b) return;
    if (e.key === "ArrowDown") { e.preventDefault(); (b.nextElementSibling || b).focus(); }
    if (e.key === "ArrowUp") { e.preventDefault(); (b.previousElementSibling || find).focus(); }
  });
  results.addEventListener("click", (e) => { const b = e.target.closest("[data-c]"); if (b) { goTo(b.dataset.c); results.innerHTML = ""; find.value = ""; } });

  const onResize = () => { if (state.mode === "kinds") drawKinds(); else placeLabels(); };
  window.addEventListener("resize", onResize);
  // Escape steps back out of a focused idea, unless it is closing the passage drawer first
  const onKey = (e) => { if (e.key === "Escape" && !document.getElementById("drawer").classList.contains("open") && (state.selected || state.kind)) clearSelection(); };
  document.addEventListener("keydown", onKey, true);

  // first paint, measured once the page has laid out (Q-63)
  await new Promise((r) => requestAnimationFrame(r));
  fitAll(0);
  if (state.mode === "kinds") setMode("kinds");
  else if (start) select(start, { trail: false });
  else { overview(); paint(); }
  return () => { window.removeEventListener("resize", onResize); document.removeEventListener("keydown", onKey, true); tip(null); svg.interrupt(); };
}
