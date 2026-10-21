/* Trace a change: name a section of the Act, a regulation or a page of the Manual, and see what
   rests on it.

   What rests on a provision is the dependency index (R05), computed by tmk-explorer from every
   record's own citations, in both stores: the records that name the provision (or a part of it),
   and those resting on a Manual passage that cites it, as upstream found the citation. What rests
   on a page is the records whose quoted text sits on it. Drawn as a ripple: the source in the
   middle, what names it directly in the first ring, what rests on it through the Manual further
   out, each kind of record in its own labelled sector. What no record names is not shown, so an
   empty answer means no recorded dependency, never no impact. The amendment history is the
   published Manual's own, captured with the snapshot (an Observable Plot timeline). */

import { esc, fmt, load, refChip, refLabel, sourceOf, srcShape, structureHref, tip, FAMILIES, familyOf } from "./app.js";
import { namedProvisions } from "./engine.js";
import { icon } from "./icons.js";
import * as lib from "./lib.js";

/** Kinds of record, in the order the ripple draws them, with plain names. */
const TYPES = [
  ["GC", "Ideas", "an idea"], ["GR", "Connections", "a connection"], ["GD", "Definitions", "a definition"],
  ["GT", "Kind judgements", "which kind an idea is"], ["GL", "Legal tests", "a legal test"], ["GP", "Processes", "a process template"],
  ["GK", "Corrections", "a correction to a reviewed record"], ["Q", "Questions and checks", "a test question or check"],
];
const typeOf = (id) => { const p = String(id).split("-")[0]; return TYPES.some(([k]) => k === p) ? p : "Q"; };

export async function render(root, { ontology, params }) {
  const [stability, Plot] = await Promise.all([load("stability"), lib.plot()]);
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const rels = new Map(ontology.relations.map((r) => [r.id, r]));
  const defs = new Map(ontology.concepts.filter((c) => c.definition).map((c) => [c.definition.id, c]));
  const structures = new Map([...(ontology.structures?.tests || []), ...(ontology.structures?.processes || [])].map((r) => [r.id, r]));
  const pages = stability.pages;
  const byPage = new Map(pages.map((p) => [p.ref, p]));
  const provisions = stability.provisions || {};
  const held = Object.fromEntries((stability.held || []).map((ref) => [ref, 1]));
  const firstYear = Object.keys(stability.by_year)[0];
  const weight = (ref) => provisions[ref].direct.length + provisions[ref].via_manual.length;
  const top = Object.keys(provisions).sort((a, b) => weight(b) - weight(a)).slice(0, 8);
  const joined = params.join("/");
  let current = byPage.has(joined) || provisions[joined] ? joined : provisions["TMA1995/s44"] ? "TMA1995/s44" : top[0];

  root.innerHTML = `
  <div class="ch">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">For maintaining guidance</span>
        <h1>Trace a change</h1>
        <p class="lede">When a section of the Act, a regulation or a page of the Manual changes, what needs re-checking? Name one and see every
        record that rests on it: those that name it directly, and those resting on the Manual's passages that cite it.</p>
      </div>
      <div class="page-head-side"><span class="pill working">Working · not measured</span></div>
    </header>
    <div class="wrap">
      <div class="card ch-pick">
        <form class="ch-form">
          <label for="ch-input">Start from a provision</label>
          <div class="ch-in">${icon("search")}<input id="ch-input" name="p" type="text" placeholder="e.g. section 44, s 41(4), reg 4.13" autocomplete="off"><button class="btn primary small" type="submit">Trace</button></div>
          <p class="ch-msg tiny" role="status"></p>
        </form>
        <div class="ch-quick"><span class="tiny">Most depended on</span>${top.map((ref) => `<button type="button" class="chip" data-pick="${esc(ref)}"><span class="law ${sourceOf(ref)}"><i class="mark" aria-hidden="true"></i></span>${esc(refLabel(ref))} <span class="tiny">${fmt(weight(ref))}</span></button>`).join("")}</div>
        <p class="tiny ch-or">Or pick a page of the Manual from the grid below.</p>
      </div>
      <div class="ch-main">
        <div class="card ch-ripple-card"><div class="ch-ripple"></div></div>
        <aside class="card ch-side" aria-live="polite"></aside>
      </div>
      <a class="ch-whatif" href="#/whatif">${icon("flag")}<span><b>A what-if:</b> geographical indications as their own right. Lay a right that does not exist over the ontology, without changing it, and see where practice would need to be read again.</span>${icon("arrow")}</a>
      <p class="ch-honest">${icon("info")}<span>From every record's own citations and quotes, in both stores. What no record names is not shown, so an empty answer means
        <b>no recorded dependency, never no impact</b>. Where upstream marked a citation ambiguous, it is listed and never resolved.</span></p>

      <section class="ch-history">
        <div class="sec-head"><div><span class="eyebrow">Why it matters</span><h2>The Manual changes often.</h2></div>
          <p>${fmt(stability.events)} amendments recorded on its ${fmt(pages.length)} pages since ${esc(firstYear)}, from the notes on each page of the published Manual, as captured on ${esc(stability.snapshot)}.</p></div>
        <div class="ch-hist-grid">
          <div class="card card-pad"><h3>Amendments, month by month</h3><div class="ch-plot"></div></div>
          <div class="card card-pad"><h3>The reasons given</h3><ul class="ch-reasons">${stability.reasons.slice(0, 7).map(([r, n]) => `<li><b>${fmt(n)}</b><span>${esc(r)}</span></li>`).join("")}</ul></div>
        </div>
        <div class="card card-pad ch-heat">
          <div class="row spread"><div><h3>Every page of the Manual</h3><p class="tiny">Each row is a Part, in reading order; each tile a page, as wide as the page is long. Click a page to trace it.</p></div>
            <div class="seg" role="group" aria-label="Shade the pages by"><button type="button" data-mode="amended" aria-pressed="true">Amendments</button><button type="button" data-mode="relations" aria-pressed="false">Connections resting on it</button></div></div>
          <div class="ch-key"></div>
          <div class="ch-parts" role="list"></div>
        </div>
      </section>
    </div>
  </div>`;

  const ripple = root.querySelector(".ch-ripple");
  const side = root.querySelector(".ch-side");
  const msg = root.querySelector(".ch-msg");

  // ---- naming a record in words, for the tooltip and the lists
  const named = (id) => {
    const t = typeOf(id);
    if (t === "GC") return byId.get(id)?.label || id;
    if (t === "GR") { const r = rels.get(id); return r ? `${byId.get(r.s)?.label || refLabel(r.s)} ${ontology.predicates[r.p]?.label || r.p} ${byId.get(r.o)?.label || refLabel(r.o)}` : id; }
    if (t === "GD") return defs.has(id) ? `the definition of ${defs.get(id).label}` : id;
    if (t === "GT") { const c = byId.get(id.replace(/^GT-/, "GC-")); return c ? `which kind ${c.label} is` : id; }
    if (t === "GL" || t === "GP") return structures.get(id)?.title || id;
    return id;
  };
  const hrefOf = (id) => {
    const t = typeOf(id);
    if (t === "GC") return `#/map/ideas/${id}`;
    if (t === "GT" && byId.has(id.replace(/^GT-/, "GC-"))) return `#/map/ideas/${id.replace(/^GT-/, "GC-")}`;
    if (t === "GR") { const r = rels.get(id); return r && byId.has(r.s) ? `#/map/ideas/${r.s}` : null; }
    if (t === "GD") return defs.has(id) ? `#/map/ideas/${defs.get(id).id}` : null;
    if (t === "GL" || t === "GP") return structureHref(id);
    return null;
  };
  const colourOf = (id) => {
    const t = typeOf(id);
    const concept = t === "GC" ? byId.get(id) : t === "GT" ? byId.get(id.replace(/^GT-/, "GC-")) : t === "GD" ? defs.get(id) : null;
    return concept ? FAMILIES[familyOf(ontology, concept.kind)].colour : null;
  };

  // ---- the ripple: one sector per kind of record, shared by both rings, so one label serves both
  function draw(center, { direct, passages = [], outer = [], ambiguous = new Set(), outerLabel, directLabel }) {
    const W = 780, H = 660, cx = W / 2, cy = H / 2 + 4;
    const R1 = 104, RP = 170, R2 = 214, STEP = 10.5;
    const cats = TYPES.map(([k, label]) => ({ k, label, d: direct.filter((id) => typeOf(id) === k), o: outer.filter((id) => typeOf(id) === k) }))
      .filter((c) => c.d.length || c.o.length);
    const total = cats.reduce((n, c) => n + Math.max(c.d.length, c.o.length * 0.8), 0) || 1;
    const gap = cats.length > 1 ? 0.1 : 0, span = Math.PI * 2 - gap * cats.length;
    const raw = cats.map((c) => Math.max(0.1, Math.max(c.d.length, c.o.length * 0.8) / total));
    const sum = raw.reduce((n, x) => n + x, 0);
    const parts = [`<svg viewBox="0 0 ${W} ${H}" class="ch-svg" role="img" aria-label="${esc(`What rests on ${center.label}: ${direct.length} ${directLabel}; ${outer.length} ${outerLabel}`)}">`];
    parts.push(`<circle cx="${cx}" cy="${cy}" r="${R1 - 8}" class="ch-ring"/>`);
    if (passages.length) parts.push(`<circle cx="${cx}" cy="${cy}" r="${RP}" class="ch-ring"/>`);
    parts.push(`<circle cx="${cx}" cy="${cy}" r="${R2 - 8}" class="ch-ring outer"/>`);
    // dots for one ring's records in one sector, rows growing outward
    const dots = (ids, r0, a0, a1, cls) => {
      let row = 0, placed = 0, out = "";
      const width = a1 - a0;
      while (placed < ids.length) {
        const r = r0 + row * STEP;
        const cap = Math.max(1, Math.floor((r * width) / STEP));
        for (let k = 0; k < cap && placed < ids.length; k++, placed++) {
          const t = a0 + (width * (k + 0.5)) / cap;
          const id = ids[placed];
          const fill = colourOf(id);
          out += `<circle cx="${(cx + r * Math.cos(t)).toFixed(1)}" cy="${(cy + r * Math.sin(t)).toFixed(1)}" r="4" class="ch-dot ${cls}" ${fill ? `style="fill:${fill}"` : ""} data-id="${esc(id)}"
            data-tip="${esc(`<span class="tip-k">${esc(TYPES.find(([k]) => k === typeOf(id))?.[2] || "a record")} · ${esc(id)}</span><b>${esc(named(id))}</b>${hrefOf(id) ? `<span class="tip-s">Click to open it.</span>` : ""}`)}"/>`;
        }
        row++;
      }
      return { svg: out, rows: row };
    };
    let a = -Math.PI / 2 + gap / 2;
    let outerRows = 0;
    const labels = [];
    cats.forEach((c, i) => {
      const a0 = a, a1 = a + (raw[i] / sum) * span;
      const inner = dots(c.d, R1, a0, a1, "direct");
      const far = dots(c.o, R2, a0, a1, "via");
      parts.push(inner.svg, far.svg);
      outerRows = Math.max(outerRows, far.rows);
      labels.push({ c, mid: (a0 + a1) / 2 });
      a = a1 + gap;
    });
    // the passages that cite a provision, evenly round their own ring
    passages.forEach((ref, i) => {
      const t = -Math.PI / 2 + (Math.PI * 2 * (i + 0.5)) / passages.length;
      parts.push(`<g class="ch-dot ch-psg manual${ambiguous.has(ref) ? " amb" : ""}" transform="translate(${(cx + RP * Math.cos(t)).toFixed(1)},${(cy + RP * Math.sin(t)).toFixed(1)})" data-ref="${esc(ref)}"
        data-tip="${esc(`<span class="tip-k">Manual · practice${ambiguous.has(ref) ? " · citation marked ambiguous upstream" : ""}</span><b>${esc(refLabel(ref))}</b><span class="tip-s">A passage citing it. Click to read it.</span>`)}">${srcShape("manual", 3.4)}</g>`);
    });
    const LR = R2 + Math.max(1, outerRows) * STEP + 14;
    for (const { c, mid } of labels) {
      const lx = cx + LR * Math.cos(mid), ly = cy + LR * Math.sin(mid);
      const anchor = Math.cos(mid) > 0.3 ? "start" : Math.cos(mid) < -0.3 ? "end" : "middle";
      const dy = Math.sin(mid) < -0.5 ? -8 : Math.sin(mid) > 0.5 ? 12 : 2;
      parts.push(`<text x="${lx.toFixed(1)}" y="${(ly + dy).toFixed(1)}" text-anchor="${anchor}" class="ch-lab"><tspan class="n">${esc(c.label)}</tspan>
        <tspan x="${lx.toFixed(1)}" dy="15" class="s">${[c.d.length ? `${fmt(c.d.length)} direct` : "", c.o.length ? `${fmt(c.o.length)} ${center.src === "manual" ? "named" : "via"}` : ""].filter(Boolean).join(" · ")}</tspan></text>`);
    }
    if (!cats.length) parts.push(`<text x="${cx}" y="${cy - R1 - 6}" text-anchor="middle" class="ch-empty">No recorded dependency</text>`);
    // the source in the middle
    parts.push(`<g transform="translate(${cx},${cy})" class="ch-center ${center.src === "manual" ? "manual" : `law ${center.src}`}">
      <circle r="62" class="ch-core"/><g transform="translate(0,-18)">${srcShape(center.src, 11)}</g>
      <text y="14" text-anchor="middle" class="ch-c1">${esc(center.short)}</text><text y="31" text-anchor="middle" class="ch-c2">${esc(center.sub)}</text></g>`);
    parts.push(`</svg>`);
    ripple.innerHTML = parts.join("") + `<div class="ch-ripple-key"><span><i class="k direct"></i>${esc(directLabel)}</span>${passages.length ? `<span><i class="k psg"></i>a Manual passage citing it</span>` : ""}<span><i class="k via"></i>${esc(outerLabel)}</span><span class="tiny">Ideas, their kinds and definitions take their family's colour.</span></div>`;
  }

  const groupsOf = (ids) => TYPES.map(([k, label]) => ({ key: k, label, ids: ids.filter((id) => typeOf(id) === k) }));
  const listBlock = (title, ids, note = "") => {
    if (!ids.length) return "";
    return `<details class="quiet ch-list"><summary>${esc(title)} · ${fmt(ids.length)}</summary><div class="det-body">${note}
      ${groupsOf(ids).filter((g) => g.ids.length).map((g) => `<p class="ch-gh">${esc(g.label)} <span class="tiny">${fmt(g.ids.length)}</span></p>
      <div class="ch-chips">${g.ids.map((id) => { const h = hrefOf(id); return h ? `<a class="chip" href="${h}" title="${esc(id)}">${esc(named(id).slice(0, 60))}</a>` : `<span class="chip" title="${esc(named(id))}">${esc(id)}</span>`; }).join("")}</div>`).join("")}
    </div></details>`;
  };

  function showProvision(ref) {
    const hit = provisions[ref];
    const src = sourceOf(ref);
    const label = refLabel(ref);
    if (!hit) {
      draw({ src, label, short: label, sub: "no recorded dependency" }, { direct: [], directLabel: "names it directly", outerLabel: "rests on a passage citing it" });
      side.innerHTML = `<span class="eyebrow">What rests on it</span><h2>${esc(label)}</h2><p>${refChip(ref)}</p>
        <p class="ch-none">No record names it or rests on a Manual passage citing it: <b>no recorded dependency, which is not the same as no impact</b>.</p>`;
      return;
    }
    const passages = hit.passages || [];
    draw({ src, label, short: label, sub: src === "act" ? "the Act" : "the Regulations" },
      { direct: hit.direct, passages, outer: hit.via_manual, ambiguous: new Set(hit.ambiguous || []), directLabel: "names it directly", outerLabel: "rests on a passage citing it" });
    side.innerHTML = `<span class="eyebrow">What rests on it</span><h2>${esc(label)}</h2>
      <p class="row wrap-ok">${refChip(ref)}<button type="button" class="btn small ghost" data-ref="${esc(ref)}">${icon("book")} Read the provision</button></p>
      <div class="ch-stats">
        <div class="stat"><b>${fmt(hit.direct.length)}</b><span>records name it, or a part of it, directly</span></div>
        <div class="stat"><b>${fmt(passages.length)}</b><span>Manual passages cite it${hit.ambiguous.length ? `; upstream marked ${fmt(hit.ambiguous.length)} of those citations ambiguous: listed, never resolved` : ""}</span></div>
        <div class="stat"><b>${fmt(hit.via_manual.length)}</b><span>more records rest on those passages</span></div>
      </div>
      <p class="small muted">If it were amended, each would go back to be re-read against the new words.</p>
      ${listBlock("Name it directly", hit.direct)}
      ${listBlock("Rest on a passage citing it", hit.via_manual)}
      ${passages.length ? `<details class="quiet ch-list"><summary>The passages citing it · ${fmt(passages.length)}</summary><div class="det-body"><div class="ch-chips">${passages.map((p) => refChip(p)).join("")}</div></div></details>` : ""}`;
  }

  function showPage(ref) {
    const p = byPage.get(ref);
    const records = [...p.concepts, ...p.relations, ...(p.typings || []).map((id) => (String(id).startsWith("GT-") ? id : `GT-${String(id).replace(/^GC-/, "")}`)), ...p.definitions, ...p.corrections, ...(p.structures || [])];
    draw({ src: "manual", label: p.title, short: (stability.parts[p.part] || p.part).replace(/^(Part \S+).*$/, "$1"), sub: `${fmt(p.passages)} passage${p.passages === 1 ? "" : "s"}` },
      { direct: records, outer: p.mentioned, directLabel: "quotes this page", outerLabel: "an idea named on it, re-matched automatically" });
    side.innerHTML = `<span class="eyebrow">What rests on this page</span><h2>${esc(p.title)}</h2>
      <p class="tiny">${esc(stability.parts[p.part] || p.part)}</p>
      <p class="row wrap-ok">${p.url ? `<a class="btn small" href="${esc(p.url)}" target="_blank" rel="noopener">Open the published page ${icon("external")}</a>` : ""}</p>
      <div class="ch-stats">
        <div class="stat"><b>${fmt(records.length)}</b><span>records quote this page and would go back to be re-read</span></div>
        <div class="stat"><b>${fmt(p.mentioned.length)}</b><span>ideas are named on it: found again by matching their wordings, automatically, with nothing for a person to review</span></div>
        <div class="stat"><b>${fmt(p.amended.length)}</b><span>amendments recorded on it</span></div>
      </div>
      ${p.amended.length ? `<details class="quiet ch-list"><summary>Its amendment history</summary><div class="det-body"><ul class="ch-amend">${p.amended.map(([d, r]) => `<li><b>${esc(d || "")}</b> ${esc(r || "(no reason given)")}</li>`).join("")}</ul></div></details>` : ""}
      ${listBlock("Quote this page", records)}
      <p class="small muted">No kind of idea rests on a passage: grounds, tests, roles, steps and records stay what they are, whatever this page says next.</p>`;
  }

  function select(ref) {
    current = ref;
    history.replaceState(null, "", `#/change/${ref}`);
    root.querySelectorAll("[data-pick]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.pick === ref)));
    root.querySelectorAll(".ch-pg").forEach((b) => b.classList.toggle("on", b.dataset.page === ref));
    if (byPage.has(ref)) showPage(ref); else showProvision(ref);
  }

  root.querySelector(".ch-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = e.target.p.value;
    const refs = namedProvisions(text, held);
    if (!refs.length) { msg.textContent = `No section of the Act or regulation this snapshot holds is named in “${text.slice(0, 80)}”. Try “section 44” or “reg 4.13”.`; return; }
    msg.textContent = refs.length > 1 ? `Named ${refs.length}: showing ${refLabel(refs[0])}.` : "";
    select(refs[0]);
  });
  root.querySelector(".ch-quick").addEventListener("click", (e) => { const b = e.target.closest("[data-pick]"); if (b) select(b.dataset.pick); });
  ripple.addEventListener("mousemove", (e) => { const t = e.target.closest("[data-tip]"); tip(t ? t.dataset.tip : null, e); });
  ripple.addEventListener("mouseleave", () => tip(null));
  ripple.addEventListener("click", (e) => {
    const d = e.target.closest("[data-id]");
    if (!d) return;
    const h = hrefOf(d.dataset.id);
    if (h) location.hash = h;
  });

  // ---- the amendments, month by month (Observable Plot)
  const months = new Map();
  for (const p of pages) for (const [date] of p.amended) if (date) months.set(date.slice(0, 7), (months.get(date.slice(0, 7)) || 0) + 1);
  const series = [...months.entries()].sort().map(([m, n]) => ({ month: new Date(`${m}-01T00:00:00`), n }));
  function drawTimeline() {
    const holder = root.querySelector(".ch-plot");
    holder.innerHTML = "";
    holder.appendChild(Plot.plot({
      width: Math.max(320, holder.clientWidth), height: 190, marginLeft: 38, marginBottom: 28,
      style: { background: "transparent", color: "var(--ink-2)", fontFamily: "var(--sans)", fontSize: "11.5px" },
      x: { type: "utc", label: null }, y: { label: "amendments", grid: true },
      marks: [
        Plot.rectY(series, { x: "month", y: "n", interval: "month", fill: "var(--green)", fillOpacity: 0.8, rx: 2, tip: { format: { x: (d) => d.toLocaleDateString("en-AU", { month: "long", year: "numeric" }) } } }),
        Plot.ruleY([0], { stroke: "var(--line)" }),
      ],
    }));
  }

  // ---- every page, Part by Part
  let mode = "amended";
  const maxAmend = Math.max(...pages.map((p) => p.amended.length));
  const maxRel = Math.max(...pages.map((p) => p.relations.length));
  const parts = new Map();
  for (const p of pages) { if (!parts.has(p.part)) parts.set(p.part, []); parts.get(p.part).push(p); }
  const holder = root.querySelector(".ch-parts");
  const partNo = (part) => (stability.parts[part] || part).match(/^Part\s+(\S+)\s*(.*)$/) || [null, part.replace(/^Part/, ""), part];
  const tileWidth = (p) => Math.round(Math.min(30, 7 + 2.2 * Math.sqrt(p.passages)));
  const shade = (p) => {
    const v = mode === "amended" ? p.amended.length / maxAmend : (p.relations.length ? 0.18 + 0.82 * p.relations.length / maxRel : 0);
    return `color-mix(in srgb, ${mode === "amended" ? "var(--green)" : "var(--f-examined)"} ${Math.round(v * 100)}%, var(--line-2))`;
  };
  function drawHeat() {
    root.querySelector(".ch-key").innerHTML = `<span>fewer</span><i style="background:linear-gradient(90deg, var(--line-2), ${mode === "amended" ? "var(--green)" : "var(--f-examined)"})"></i><span>more ${mode === "amended" ? "amendments recorded" : "connections quote it"}</span>`;
    holder.innerHTML = [...parts.entries()].map(([part, list]) => {
      const [, n, name] = partNo(part);
      return `<div class="ch-part" role="listitem"><span class="ch-pn"><b>${esc(n)}</b><span>${esc(name)}</span></span>
        <span class="ch-tiles">${list.map((p) => `<button type="button" class="ch-pg${p.ref === current ? " on" : ""}" data-page="${esc(p.ref)}" style="width:${tileWidth(p)}px;background:${shade(p)}"
          data-tip="${esc(`<span class="tip-k">${esc(stability.parts[p.part] || p.part)}</span><b>${esc(p.title)}</b><span class="tip-s">${fmt(p.amended.length)} amendment${p.amended.length === 1 ? "" : "s"} · ${fmt(p.relations.length)} connection${p.relations.length === 1 ? "" : "s"} rest on it</span>`)}"
          aria-label="${esc(`${p.title}: ${p.amended.length} amendments, ${p.relations.length} connections`)}"></button>`).join("")}</span></div>`;
    }).join("");
  }
  holder.addEventListener("click", (e) => { const b = e.target.closest("[data-page]"); if (b) { select(b.dataset.page); root.querySelector(".ch-main").scrollIntoView({ behavior: "smooth", block: "start" }); } });
  holder.addEventListener("mousemove", (e) => { const t = e.target.closest("[data-tip]"); tip(t ? t.dataset.tip : null, e); });
  holder.addEventListener("mouseleave", () => tip(null));
  root.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => {
    mode = b.dataset.mode;
    root.querySelectorAll("[data-mode]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    drawHeat();
  }));

  drawTimeline();
  drawHeat();
  select(current);
  let timer = null;
  const debounced = () => { clearTimeout(timer); timer = setTimeout(drawTimeline, 150); };
  window.addEventListener("resize", debounced);
  return () => { window.removeEventListener("resize", debounced); tip(null); };
}
