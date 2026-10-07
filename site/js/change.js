/* When the text changes — pick a page of the Manual, see what rests on it.

   The amendment history is the published Manual's own, captured with the
   snapshot. What rests on a page is computed by tmk-explorer from each record's
   evidence refs: the records whose quoted text sits on that page. */

import { esc, fmt, load, kindColour, refChip, trustBadge } from "./app.js";
import { wait } from "./graph.js";

export async function render(root, { ontology, params }) {
  const stability = await load("stability");
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
    <div class="change-shell">
      <div class="card heat">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:.6rem">
          <h3 style="margin:0">Every page of the Manual</h3>
          <div class="legend">Colour by
            <button type="button" class="chip on" data-mode="amended">amendments</button>
            <button type="button" class="chip" data-mode="relations">connections resting on it</button>
          </div>
        </div>
        <div class="heat-rows"></div>
        <p class="tiny" style="margin-top:.6rem">One square per page; darker means more. ${fmt(holding.length)} of ${fmt(pages.length)} pages hold a passage at least one connection quotes.</p>
      </div>
      <div class="card ripple" aria-live="polite"></div>
    </div>
  </div>`;

  const rows = root.querySelector(".heat-rows");
  function drawHeat() {
    rows.innerHTML = [...parts.entries()].map(([part, list]) => `
      <div class="heat-part"><span class="pn" title="${esc(stability.parts[part] || part)}">${esc((stability.parts[part] || part).replace(/^Part (\S+)\s*/, "$1 · "))}</span>
        <div class="heat-cells">${list.map((p) => {
          const v = mode === "amended" ? p.amended.length / maxAmend : (p.relations.length ? 0.15 + 0.85 * p.relations.length / maxRel : 0);
          const colour = mode === "amended" ? "var(--warn)" : "var(--k-relevant_factor)";
          return `<button type="button" data-page="${esc(p.ref)}" class="${p.ref === current ? "on" : ""}" style="background:color-mix(in srgb, ${colour} ${Math.round(v * 100)}%, var(--line-2))"
            title="${esc(p.title)} — ${p.amended.length} amendments, ${p.relations.length} connections rest on it"></button>`;
        }).join("")}</div></div>`).join("");
    rows.querySelectorAll("[data-page]").forEach((b) => b.addEventListener("click", () => select(b.dataset.page, true)));
  }

  const ripple = root.querySelector(".ripple");
  function select(ref, simulate = false) {
    current = ref;
    history.replaceState(null, "", `#/change/${ref}`);
    rows.querySelectorAll("[data-page]").forEach((b) => b.classList.toggle("on", b.dataset.page === ref));
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
  drawHeat();
  select(current);
}
