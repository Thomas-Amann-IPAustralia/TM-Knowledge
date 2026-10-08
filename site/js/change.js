/* When the text changes — pick a page of the Manual, see what rests on it.

   The amendment history is the published Manual's own, captured with the
   snapshot (an Observable Plot timeline). Every page is a tile in its Part's row,
   Parts in reading order with their titles in full, tiles as wide as the page is
   long. What rests on a page is computed by tmk-explorer from each record's
   evidence refs: the records whose quoted text sits on that page. The chosen
   page's ideas and connections are drawn on a mini map (Cytoscape). */

import { esc, fmt, load, kindColour, refChip, trustBadge } from "./app.js";
import { wait } from "./graph.js";
import { miniMap } from "./minimap.js";
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
        <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:.4rem">
          <h3 style="margin:0">Every page of the Manual</h3>
          <div class="legend">Colour by
            <button type="button" class="chip on" data-mode="amended">amendments</button>
            <button type="button" class="chip" data-mode="relations">connections resting on it</button>
          </div>
        </div>
        <div class="heat-key"></div>
        <div class="parts" role="list"></div>
        <div class="page-tip" hidden></div>
        <p class="tiny" style="margin-top:.6rem">Each row is a Part of the Manual, in reading order; each tile is one of its pages, as wide as the page is long.
          ${fmt(holding.length)} of ${fmt(pages.length)} pages hold a passage at least one connection quotes. Click a page.</p>
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

  // ---- every page, Part by Part (titles in full; nothing is cut off)
  const holder = root.querySelector(".parts");
  const tip = root.querySelector(".page-tip");
  const partNo = (part) => (stability.parts[part] || part).match(/^Part\s+(\S+)\s*(.*)$/) || [null, part.replace(/^Part/, ""), part];
  const tileWidth = (p) => Math.round(Math.min(30, 7 + 2.2 * Math.sqrt(p.passages)));
  const shade = (p) => {
    const v = mode === "amended" ? p.amended.length / maxAmend : (p.relations.length ? 0.18 + 0.82 * p.relations.length / maxRel : 0);
    return `color-mix(in srgb, ${mode === "amended" ? "var(--warn)" : "var(--k-relevant_factor)"} ${Math.round(v * 100)}%, var(--line-2))`;
  };
  function drawHeat() {
    root.querySelector(".heat-key").innerHTML = `<span>fewer</span><i style="background:linear-gradient(90deg, var(--line-2), ${mode === "amended" ? "var(--warn)" : "var(--k-relevant_factor)"})"></i>
      <span>more ${mode === "amended" ? "amendments recorded" : "connections quote it"}</span>`;
    holder.innerHTML = [...parts.entries()].map(([part, list]) => {
      const [, n, name] = partNo(part);
      return `<div class="part-row" role="listitem" data-part="${esc(part)}">
        <span class="pn"><b>${esc(n)}</b><span>${esc(name)}</span></span>
        <span class="tiles">${list.map((p) => `<button type="button" class="pg${p.ref === current ? " on" : ""}" data-page="${esc(p.ref)}"
          style="width:${tileWidth(p)}px;background:${shade(p)}" aria-label="${esc(`${p.title}: ${p.amended.length} amendments, ${p.relations.length} connections`)}"></button>`).join("")}</span>
      </div>`;
    }).join("");
  }
  holder.addEventListener("click", (e) => { const b = e.target.closest("[data-page]"); if (b) select(b.dataset.page, true); });
  const showTip = (b) => {
    const p = byRef.get(b.dataset.page);
    tip.innerHTML = `<span class="tiny">${esc(stability.parts[p.part] || p.part)}</span><b>${esc(p.title)}</b>
      <span>${fmt(p.passages)} passage${p.passages === 1 ? "" : "s"} · ${fmt(p.amended.length)} amendment${p.amended.length === 1 ? "" : "s"} · ${fmt(p.relations.length)} connection${p.relations.length === 1 ? "" : "s"} rest on it</span>`;
    tip.hidden = false;
    const r = b.getBoundingClientRect(), box = holder.closest(".heat").getBoundingClientRect();
    const w = tip.offsetWidth;
    tip.style.left = `${Math.max(8, Math.min(box.width - w - 8, r.left - box.left + r.width / 2 - w / 2))}px`;
    tip.style.top = `${r.bottom - box.top + 8}px`;
  };
  holder.addEventListener("mouseover", (e) => { const b = e.target.closest("[data-page]"); if (b) showTip(b); });
  holder.addEventListener("focusin", (e) => { const b = e.target.closest("[data-page]"); if (b) showTip(b); });
  holder.addEventListener("mouseleave", () => { tip.hidden = true; });
  holder.addEventListener("focusout", () => { tip.hidden = true; });

  const ripple = root.querySelector(".ripple");
  let mini = null, drawn = 0;
  function select(ref, simulate = false) {
    current = ref;
    history.replaceState(null, "", `#/change/${ref}`);
    holder.querySelectorAll("[data-page]").forEach((b) => b.classList.toggle("on", b.dataset.page === ref));
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
      <div class="ripple-map">
        <h4>What rests on this page, on the map</h4>
        ${relList.length || p.concepts.length ? `<div class="mini-legend">
          <span><i class="ring"></i>its evidence is quoted here</span>
          <span><svg viewBox="0 0 26 12"><line x1="1" y1="6" x2="25" y2="6" stroke="var(--ink-2)" stroke-width="2.2"/></svg>a connection quoting this page, signed</span>
          <span><svg viewBox="0 0 26 12"><line x1="1" y1="6" x2="25" y2="6" stroke="var(--ink-3)" stroke-width="1.4" stroke-dasharray="5 3"/></svg>machine-written</span>
        </div><div class="mini-holder"></div>`
        : `<p class="small muted">Nothing on the map quotes this page. A rewrite would only re-match the ${fmt(p.links)} place${p.links === 1 ? "" : "s"} an idea is named on it — automatically.</p>`}
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
    const token = ++drawn;
    mini?.destroy();
    mini = null;
    const mapHolder = ripple.querySelector(".mini-holder");
    const undrawn = relList.filter((r) => !byId.has(r.s) || !byId.has(r.o)).length;
    const ready = mapHolder ? miniMap(mapHolder, {
      ontology, d3, layout: "force", height: 330, centre: p.concepts, relations: relList,
      help: `Ringed: ideas that quote this page as their evidence. Lines: connections that quote it. Hover an idea; click a line to read the sentence.${
        undrawn ? ` ${undrawn} connection${undrawn > 1 ? "s" : ""} ending at a provision, a case or a passage rather than an idea ${undrawn > 1 ? "are" : "is"} listed below but not drawn.` : ""}`,
    }).then((m) => { if (token === drawn) mini = m; else m.destroy(); }) : Promise.resolve();
    if (simulate) ready.then(() => { if (token === drawn) simulate_(); });
  }

  async function simulate_() {
    const p = byRef.get(current);
    const layers = [...ripple.querySelectorAll(".layer")];
    layers.forEach((l) => l.classList.remove("pulse", "hit"));
    for (const [i, l] of layers.entries()) {
      await wait(i ? 380 : 0);
      l.classList.add("pulse");
      if (i < 4 && Number(l.querySelector(".lnum").textContent.replace(/,/g, "")) > 0) l.classList.add("hit");
      // The map shows the same ripple: the connections to re-check, then the ideas.
      if (i === 2) mini?.flash(p.relations, 0);
      if (i === 3) mini?.pulse(p.concepts);
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
  let timer = null;
  const debounced = () => { clearTimeout(timer); timer = setTimeout(drawTimeline, 150); };
  window.addEventListener("resize", debounced);
  return () => { window.removeEventListener("resize", debounced); drawn++; mini?.destroy(); };
}
