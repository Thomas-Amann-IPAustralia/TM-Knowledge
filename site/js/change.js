/* When the text changes — pick a page of the Manual, see what rests on it.

   The amendment history is the published Manual's own, captured with the
   snapshot (an Observable Plot timeline). The Manual is drawn as a D3 treemap:
   Parts, then pages, sized by passages. What rests on a page is computed by
   tmk-explorer from each record's evidence refs: the records whose quoted text
   sits on that page. */

import { esc, fmt, load, kindColour, refChip, trustBadge } from "./app.js";
import { wait } from "./graph.js";
import * as lib from "./lib.js";

export async function render(root, { ontology, params }) {
  const [stability, d3, Plot] = await Promise.all([load("stability"), lib.d3(), lib.plot()]);
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const rels = new Map(ontology.relations.map((r) => [r.id, r]));
  const pages = stability.pages;
  const byRef = new Map(pages.map((p) => [p.ref, p]));
  const maxAmend = Math.max(...pages.map((p) => p.amended.length));
  const maxRel = Math.max(...pages.map((p) => p.relations.length));
  const holding = pages.filter((p) => p.relations.length);
  let mode = "amended";
  let current = params[0] && byRef.has(params.join("/")) ? params.join("/")
    : [...pages].sort((a, b) => b.relations.length - a.relations.length)[0].ref;

  const parts = new Map();
  for (const p of pages) { if (!parts.has(p.part)) parts.set(p.part, []); parts.get(p.part).push(p); }

  root.innerHTML = `
  <div class="wrap wide">
    <h1 style="margin-bottom:.3rem">When the text changes</h1>
    <p class="lede">The Manual is amended constantly — ${fmt(stability.events)} recorded amendments across its ${fmt(pages.length)} pages since
    ${Object.keys(stability.by_year)[0]}. Pick any page to see what in the map rests on it, and what would have to be re-checked if it were rewritten.</p>
    <div class="card timeline"><h3 style="margin:0 0 .2rem">Amendments recorded, month by month</h3><div class="plot"></div>
      <p class="tiny" style="margin:.2rem 0 0">From the amendment notes on each page of the published Manual, as captured on ${esc(stability.snapshot)}. Hover a bar for the month.</p></div>
    <div class="change-shell">
      <div class="card heat">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:.6rem">
          <h3 style="margin:0">Every page of the Manual</h3>
          <div class="legend">Colour by
            <button type="button" class="chip on" data-mode="amended">amendments</button>
            <button type="button" class="chip" data-mode="relations">connections resting on it</button>
          </div>
        </div>
        <div class="treemap"></div>
        <p class="tiny" style="margin-top:.6rem">Each block is a Part, each tile a page, sized by its passages (square root, so one long page does not swamp the rest); darker means more. ${fmt(holding.length)} of ${fmt(pages.length)} pages hold a passage at least one connection quotes. Click a page.</p>
      </div>
      <div class="card ripple" aria-live="polite"></div>
    </div>
  </div>`;

  // ---- the timeline (Observable Plot)
  const months = new Map();
  for (const p of pages) for (const [date] of p.amended) if (date) months.set(date.slice(0, 7), (months.get(date.slice(0, 7)) || 0) + 1);
  const series = [...months.entries()].sort().map(([m, n]) => ({ month: new Date(`${m}-01T00:00:00`), n }));
  function drawTimeline() {
    const holder = root.querySelector(".plot");
    holder.innerHTML = "";
    holder.appendChild(Plot.plot({
      width: Math.max(320, holder.clientWidth), height: 150, marginLeft: 36, marginBottom: 26,
      style: { background: "transparent", color: "var(--ink-2)", fontFamily: "var(--sans)", fontSize: "11px" },
      x: { type: "utc", label: null }, y: { label: "amendments", grid: true },
      marks: [
        Plot.rectY(series, { x: "month", y: "n", interval: "month", fill: "var(--warn)", fillOpacity: 0.75, tip: { format: { x: (d) => d.toLocaleDateString("en-AU", { month: "long", year: "numeric" }) } } }),
        Plot.ruleY([0], { stroke: "var(--line)" }),
      ],
    }));
  }

  // ---- the treemap (D3)
  const holder = root.querySelector(".treemap");
  const tree = { name: "Manual", children: [...parts.entries()].map(([part, list]) => ({ name: part, title: stability.parts[part] || part, children: list.map((p) => ({ page: p, value: 1 + Math.sqrt(p.passages) })) })) };
  function drawHeat() {
    const width = Math.max(320, holder.clientWidth), height = Math.round(Math.min(640, Math.max(420, width * 0.72)));
    const rootNode = d3.treemap().size([width, height]).paddingOuter(2).paddingTop(15).paddingInner(1).round(true)
      .tile(d3.treemapSquarify.ratio(1.2))(d3.hierarchy(tree).sum((d) => d.value || 0).sort((a, b) => b.value - a.value));
    const shade = (p) => {
      const v = mode === "amended" ? p.amended.length / maxAmend : (p.relations.length ? 0.18 + 0.82 * p.relations.length / maxRel : 0);
      return `color-mix(in srgb, ${mode === "amended" ? "var(--warn)" : "var(--k-relevant_factor)"} ${Math.round(v * 100)}%, var(--line-2))`;
    };
    holder.innerHTML = "";
    const svg = d3.select(holder).append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("role", "img")
      .attr("aria-label", "Every page of the Manual, grouped by Part and sized by passages");
    const partG = svg.selectAll("g.part").data(rootNode.children).join("g").attr("class", "tm-part");
    partG.append("rect").attr("x", (d) => d.x0).attr("y", (d) => d.y0).attr("width", (d) => d.x1 - d.x0).attr("height", (d) => d.y1 - d.y0)
      .attr("fill", "var(--panel-2)").attr("stroke", "var(--line)");
    partG.append("text").attr("x", (d) => d.x0 + 4).attr("y", (d) => d.y0 + 11).attr("class", "tm-label")
      .text((d) => {
        const room = (d.x1 - d.x0 - 8) / 5.6;
        const name = d.data.title.replace(/^Part (\S+)\s*/, "$1 · ");
        return room < 4 ? "" : name.length > room ? name.slice(0, Math.max(2, room - 1)) + "…" : name;
      })
      .append("title").text((d) => d.data.title);
    const tiles = svg.selectAll("rect.tm-page").data(rootNode.leaves()).join("rect")
      .attr("class", (d) => `tm-page${d.data.page.ref === current ? " on" : ""}`)
      .attr("x", (d) => d.x0).attr("y", (d) => d.y0).attr("width", (d) => Math.max(0, d.x1 - d.x0)).attr("height", (d) => Math.max(0, d.y1 - d.y0))
      .style("fill", (d) => shade(d.data.page)).attr("tabindex", 0).attr("role", "button")
      .attr("aria-label", (d) => `${d.data.page.title}: ${d.data.page.amended.length} amendments, ${d.data.page.relations.length} connections`)
      .on("click", (event, d) => select(d.data.page.ref, true))
      .on("keydown", (event, d) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); select(d.data.page.ref, true); } });
    tiles.append("title").text((d) => `${d.data.page.title}\n${d.data.page.amended.length} amendments · ${d.data.page.relations.length} connections rest on it · ${d.data.page.passages} passages`);
  }

  const ripple = root.querySelector(".ripple");
  function select(ref, simulate = false) {
    current = ref;
    history.replaceState(null, "", `#/change/${ref}`);
    holder.querySelectorAll("rect.tm-page").forEach((r) => r.classList.toggle("on", r.__data__?.data.page.ref === ref));
    const p = byRef.get(ref);
    const kinds = ontology.kinds.length;
    const relList = p.relations.map((id) => rels.get(id)).filter(Boolean);
    const signedRels = relList.filter((r) => r.origin === "signed").length;
    ripple.innerHTML = `
      <p class="tiny" style="margin:0">${esc(stability.parts[p.part] || p.part)}</p>
      <h2 style="margin:.1rem 0 .3rem">${esc(p.title)}</h2>
      <div class="meta" style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:.4rem">
        <button class="btn primary small" type="button" data-sim>Simulate a rewrite of this page</button>
        ${p.url ? `<a class="btn small" href="${esc(p.url)}" target="_blank" rel="noopener">Open the published page ↗</a>` : ""}
      </div>
      <div class="layer" data-layer="0">
        <span class="lnum num">${p.passages}</span>
        <div><b>Passages of text would change</b><span class="what">The page's own words. Its history, as the Manual records it:</span>
          <ul class="amend">${p.amended.length ? p.amended.map(([d, r]) => `<li><b>${esc(d || "")}</b>${esc(r || "(no reason given)")}</li>`).join("") : "<li>No amendments recorded.</li>"}</ul></div>
      </div>
      <div class="layer" data-layer="1">
        <span class="lnum num">${fmt(p.links)}</span>
        <div><b>Places an idea is named</b><span class="what">${p.mentioned.length} ideas are named on this page. These links are found again by matching each idea's
          wordings against the new text — automatic, and nothing for a person to review.</span></div>
      </div>
      <div class="layer" data-layer="2">
        <span class="lnum num">${relList.length}</span>
        <div><b>Connections to re-check</b><span class="what">Each quotes a sentence on this page and stores a fingerprint of it, so a change is caught
          automatically and the connection goes back for checking against the new words.${signedRels ? ` ${signedRels} of them were signed by an expert.` : ""}</span>
          ${relList.length ? `<details><summary>Show them</summary><ul class="rel-list">${relList.map((r) => `<li><span class="pred">${trustBadge(r.origin)}</span><span>${esc(byId.get(r.s)?.label || r.s)} — ${esc(ontology.predicates[r.p]?.label || r.p)} → ${esc(byId.get(r.o)?.label || r.o)} ${r.ref ? refChip(r.ref) : ""}</span></li>`).join("")}</ul></details>` : ""}</div>
      </div>
      <div class="layer" data-layer="3">
        <span class="lnum num">${p.concepts.length}</span>
        <div><b>Ideas whose evidence is here</b><span class="what">${p.concepts.length ? "They keep their identity, their wordings and their kind; only the quote they rest on is re-checked." : "No idea quotes this page as its evidence."}
          ${p.typings.length ? ` The quote behind ${p.typings.length} idea${p.typings.length > 1 ? "s'" : "'s"} kind is here too.` : ""}</span>
          ${p.concepts.length ? `<div class="meta" style="display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.4rem">${p.concepts.map((id) => byId.get(id)).filter(Boolean).map((c) => `<a class="chip" href="#/map/ideas/${c.id}"><i class="dot${c.origin === "machine" ? " machine" : ""}" style="--c:${kindColour(c.kind)}"></i>${esc(c.label)}</a>`).join("")}</div>` : ""}</div>
      </div>
      <div class="layer safe" data-layer="4">
        <span class="lnum num">0</span>
        <div><b>Kinds of idea affected, of ${kinds}</b><span class="what">No kind rests on a passage. Grounds, tests, factors, exceptions, roles, steps and
          records stay what they are, whatever this page says next.</span></div>
      </div>`;
    ripple.querySelector("[data-sim]").addEventListener("click", () => simulate_());
    if (simulate) simulate_();
  }

  async function simulate_() {
    const layers = [...ripple.querySelectorAll(".layer")];
    layers.forEach((l) => l.classList.remove("pulse", "hit"));
    for (const [i, l] of layers.entries()) {
      await wait(i ? 380 : 0);
      l.classList.add("pulse");
      if (i < 4 && Number(l.querySelector(".lnum").textContent.replace(/,/g, "")) > 0) l.classList.add("hit");
    }
  }

  root.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => {
    mode = b.dataset.mode;
    root.querySelectorAll("[data-mode]").forEach((x) => x.classList.toggle("on", x === b));
    drawHeat();
  }));
  drawTimeline();
  drawHeat();
  select(current);
  const onResize = () => { drawTimeline(); drawHeat(); };
  let timer = null;
  const debounced = () => { clearTimeout(timer); timer = setTimeout(onResize, 150); };
  window.addEventListener("resize", debounced);
  return () => window.removeEventListener("resize", debounced);
}
