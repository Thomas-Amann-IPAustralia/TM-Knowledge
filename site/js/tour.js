/* The tour — why an ontology, in seven steps, each with its own picture.

   Every number on these steps is read from the generated data; the prose only
   says what to look at. Step order is the argument: text → wordings → connections
   → kinds → change → retrieval → limits. */

import { esc, fmt, load, kindColour, refChip, trustBadge, isLaw, stampIcon } from "./app.js";
import { svg, curve, arrowDefs, wrapText } from "./graph.js";
import { drawKinds, W, H, specificCount } from "./kinds.js";

const WORDING_COLOURS = ["var(--k-relevant_factor)", "var(--k-ground_of_refusal)", "var(--k-legal_test)", "var(--k-process_role)", "var(--k-subject_matter)"];

export async function render(root, { ontology, params }) {
  const [tour, stability] = await Promise.all([load("tour"), load("stability")]);
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const c = ontology.counts;
  let step = Math.max(0, Math.min(6, Number(params[0] || 1) - 1));
  // Open on "written permission" when it is a showcase: consent is the plainest case of one idea in other words.
  let showcase = Math.max(0, tour.showcase.findIndex((x) => x.label === "written permission"));

  root.innerHTML = `
  <div class="wrap wide">
    <div class="tour">
      <div class="tour-text">
        <div class="steps" role="tablist" aria-label="Tour steps">${Array.from({ length: 7 }, (_, i) => `<button type="button" role="tab" aria-label="Step ${i + 1}" data-step="${i}"></button>`).join("")}</div>
        <div class="tour-body" aria-live="polite"></div>
        <div class="tour-nav">
          <button class="btn" type="button" data-move="-1">← Back</button>
          <button class="btn primary" type="button" data-move="1">Next →</button>
        </div>
      </div>
      <div class="stage card"></div>
    </div>
  </div>`;
  const body = root.querySelector(".tour-body");
  const stage = root.querySelector(".stage");

  const STEPS = [stepText, stepWordings, stepConnections, stepKinds, stepChange, stepRetrieval, stepLimits];

  function go(n) {
    step = Math.max(0, Math.min(STEPS.length - 1, n));
    history.replaceState(null, "", `#/tour/${step + 1}`);
    root.querySelectorAll(".steps button").forEach((b, i) => { b.classList.toggle("on", i === step); b.classList.toggle("done", i < step); });
    root.querySelector('[data-move="-1"]').disabled = step === 0;
    const next = root.querySelector('[data-move="1"]');
    next.textContent = step === STEPS.length - 1 ? "Ask the Manual →" : "Next →";
    stage.innerHTML = "";
    STEPS[step]();
  }

  // ------------------------------------------------------------- 1. text

  function waffle(colourFor, titleFor) {
    const cols = 60, cell = 14, gap = 2;
    const rows = Math.ceil(tour.passages / cols);
    const root = svg("svg", { viewBox: `0 0 ${cols * (cell + gap)} ${rows * (cell + gap)}`, role: "img", "aria-label": "Every passage of the Manual, in order, one square each" });
    let i = 0;
    tour.parts.forEach((part, p) => {
      for (let j = 0; j < part.n; j++, i++) {
        const r = svg("rect", { x: (i % cols) * (cell + gap), y: Math.floor(i / cols) * (cell + gap), width: cell, height: cell, rx: 2, class: "cell", fill: colourFor(i, p) }, root);
        if (titleFor) svg("title", {}, r).textContent = titleFor(i, part);
        r.dataset.i = i;
      }
    });
    return root;
  }

  function stepText() {
    const pages = stability.pages.length;
    body.innerHTML = `
      <p class="step-k">1 · The starting point</p>
      <h2>The Manual is written as text</h2>
      <div class="fact"><span class="big num">${fmt(tour.passages)}</span><span>passages of practice</span></div>
      <div class="fact"><span class="big num">${tour.parts.length}</span><span>Parts, over ${fmt(pages)} pages</span></div>
      <p>Each square on the right is one passage, in reading order, shaded by Part. Beside them sit the
      <b>Trade Marks Act 1995</b> and <b>Regulations</b> — law, where the Manual is practice.</p>
      <p>A search box sees only this: words in passages. It finds a passage when the words you type are in it.</p>`;
    stage.appendChild(waffle((i, p) => (p % 2 ? "var(--line)" : "color-mix(in srgb, var(--ink-3) 45%, var(--line))"), (i, part) => `${part.title}`));
    stage.insertAdjacentHTML("beforeend", `<p class="caption">Hover over a square to see its Part.</p>`);
  }

  // ------------------------------------------------------------- 2. wordings

  function stepWordings() {
    const s = tour.showcase[showcase];
    const concept = byId.get(s.id);
    const labels = Object.keys(s.wordings);
    const formal = s.wordings[s.label] || [];
    const owner = new Map();
    labels.forEach((label, li) => { for (const i of s.wordings[label]) if (!owner.has(i)) owner.set(i, li); });
    // Paint the formal term first so its squares show it.
    for (const i of formal) owner.set(i, labels.indexOf(s.label));
    let active = new Set(labels);
    body.innerHTML = `
      <p class="step-k">2 · Words are not ideas</p>
      <h2>One idea, many wordings</h2>
      <p>The Manual names the same idea in different words. Take <b>${esc(s.label)}</b>:</p>
      <div class="fact"><span class="big num">${fmt(formal.length)}</span><span>passages use the term <i>“${esc(s.label)}”</i></span></div>
      <div class="fact"><span class="big num">${fmt(s.total)}</span><span>passages name the idea, in ${labels.length} wordings</span></div>
      <p>A search for the formal term misses <b>${fmt(s.missed)}</b> of them. The ontology records the wordings once, on the idea — so every one of
      those passages is linked to it, whatever words it uses.</p>
      <div class="wordings">${labels.map((label, li) => `<button type="button" class="chip on" data-w="${esc(label)}"><i class="dot" style="--c:${WORDING_COLOURS[li % 5]}"></i>${esc(label)} · ${s.wordings[label].length}</button>`).join("")}</div>
      <p class="tiny">The wordings are the record's own labels${concept?.origin === "signed" ? ", signed by a trade marks expert" : ""}. Try another idea:
      ${tour.showcase.map((x, i) => `<button type="button" class="chip${i === showcase ? " on" : ""}" data-sc="${i}">${esc(x.label)}</button>`).join(" ")}</p>`;
    const pic = waffle(() => "var(--line-2)", (i, part) => part.title);
    stage.appendChild(pic);
    stage.insertAdjacentHTML("beforeend", `<p class="caption">Coloured squares name <b>${esc(s.label)}</b>; the colour is the wording used.</p>`);
    const paint = () => {
      pic.querySelectorAll("rect").forEach((r) => {
        const i = Number(r.dataset.i);
        const li = owner.get(i);
        const label = li === undefined ? null : labels[li];
        r.setAttribute("fill", label && active.has(label) ? WORDING_COLOURS[li % 5] : "var(--line-2)");
      });
    };
    requestAnimationFrame(paint);
    body.querySelectorAll("[data-w]").forEach((b) => b.addEventListener("click", () => {
      const w = b.dataset.w;
      if (active.size === labels.length) active = new Set([w]); else if (active.has(w) && active.size === 1) active = new Set(labels); else active.has(w) ? active.delete(w) : active.add(w);
      body.querySelectorAll("[data-w]").forEach((x) => x.classList.toggle("on", active.has(x.dataset.w)));
      paint();
    }));
    body.querySelectorAll("[data-sc]").forEach((b) => b.addEventListener("click", () => { showcase = Number(b.dataset.sc); go(step); }));
  }

  // ------------------------------------------------------------- 3. connections

  function stepConnections() {
    // The signed idea with the most connections an expert signed.
    const signedDegree = new Map();
    for (const r of ontology.relations) if (r.origin === "signed") for (const e of [r.s, r.o]) if (byId.has(e)) signedDegree.set(e, (signedDegree.get(e) || 0) + 1);
    const centreId = [...signedDegree.entries()].sort((a, b) => b[1] - a[1])[0][0];
    const centre = byId.get(centreId);
    const rels = ontology.relations.filter((r) => (r.s === centreId || r.o === centreId) && byId.has(r.s) && byId.has(r.o) && r.p !== "related")
      .sort((a, b) => (a.origin === "signed" ? -1 : 1) - (b.origin === "signed" ? -1 : 1)).slice(0, 12);
    body.innerHTML = `
      <p class="step-k">3 · Ideas connect</p>
      <h2>Each idea bears on others</h2>
      <p><b>${fmt(c.relations.signed + c.relations.machine)}</b> connections say how one idea bears on another: one <i>may give rise to</i> another,
      <i>qualifies</i> it, <i>is overcome by</i> it. Here is <b>${esc(centre.label)}</b> and its nearest neighbours.</p>
      <p>Every connection is pinned to the sentence it rests on. <b>Click a line</b> to read it.</p>
      <div class="legend" style="margin:.8rem 0">${'<span><svg viewBox="0 0 26 10"><line x1="1" y1="5" x2="25" y2="5" class="ln-signed"/></svg>signed by an expert</span><span><svg viewBox="0 0 26 10"><line x1="1" y1="5" x2="25" y2="5" class="ln-machine"/></svg>written by a machine, unreviewed</span>'}</div>
      <div class="why-box"></div>`;
    const pic = svg("svg", { viewBox: "0 0 900 600", role: "img", "aria-label": `${centre.label} and its connections` });
    arrowDefs(pic);
    const mid = { x: 450, y: 300 };
    const others = [...new Set(rels.map((r) => (r.s === centreId ? r.o : r.s)))];
    const at = new Map(others.map((id, i) => {
      const a = (i / others.length) * Math.PI * 2 - Math.PI / 2;
      return [id, { x: mid.x + Math.cos(a) * 250, y: mid.y + Math.sin(a) * 215 }];
    }));
    const lines = svg("g", {}, pic);
    const labels = svg("g", {}, pic);
    rels.forEach((r, i) => {
      const a = r.s === centreId ? mid : at.get(r.s), b = r.o === centreId ? mid : at.get(r.o);
      const cv = curve(a, b, r.s === centreId ? 34 : 14, r.o === centreId ? 38 : 18, 0.08 * (i % 2 ? 1 : -1));
      const path = svg("path", { d: cv.d, class: `edge ${r.origin}`, "stroke-width": r.origin === "signed" ? 2.4 : 1.6, "marker-end": "url(#arrow)", style: "cursor:pointer;stroke-opacity:.7" }, lines);
      const hit = svg("path", { d: cv.d, stroke: "transparent", "stroke-width": 14, fill: "none", style: "cursor:pointer" }, lines);
      svg("text", { x: cv.mx, y: cv.my, class: "edge-label", "text-anchor": "middle" }, labels).textContent = ontology.predicates[r.p]?.label || r.p;
      const show = () => {
        lines.querySelectorAll(".edge").forEach((e) => e.classList.remove("hot"));
        path.classList.add("hot");
        body.querySelector(".why-box").innerHTML = `<div class="card" style="padding:.8rem .9rem;margin-top:.6rem">
          <div class="meta">${trustBadge(r.origin)}</div>
          <p style="margin:.3rem 0"><b>${esc(byId.get(r.s).label)}</b> — ${esc(ontology.predicates[r.p]?.label || r.p)} → <b>${esc(byId.get(r.o).label)}</b></p>
          ${r.quote ? `<blockquote class="quote ${isLaw(r.ref) ? "law" : "manual"}">${esc(r.quote)}</blockquote>` : ""}${r.ref ? refChip(r.ref) : ""}</div>`;
      };
      path.addEventListener("click", show); hit.addEventListener("click", show);
      if (i === 0) setTimeout(show, 50);
    });
    const node = (concept, p, big) => {
      const g = svg("g", { class: `node ${concept.origin}`, style: `--c:${kindColour(concept.kind)}`, transform: `translate(${p.x},${p.y})` }, pic);
      svg("circle", { r: big ? 30 : 12, class: "body" }, g);
      wrapText(concept.label, big ? 18 : 16, 2).forEach((line, i) => svg("text", { x: 0, y: (big ? 48 : 28) + i * 13, "text-anchor": "middle", style: big ? "font-size:14px;font-weight:600" : "" }, g).textContent = line);
      g.addEventListener("click", () => { location.hash = `#/map/ideas/${concept.id}`; });
    };
    node(centre, mid, true);
    for (const [id, p] of at) node(byId.get(id), p, false);
    stage.appendChild(pic);
    stage.insertAdjacentHTML("beforeend", `<p class="caption">Colours are the kind of each idea (next step). Click an idea to open it on the map.</p>`);
  }

  // ------------------------------------------------------------- 4. kinds

  function stepKinds() {
    const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
    const top = ontology.kind_links.filter((r) => r.s !== r.o).sort((a, b) => specificCount(b) - specificCount(a)).slice(0, 4);
    const say = (r) => {
      const [p, n] = Object.entries(r.predicates).find(([x]) => x !== "related" && x !== "broader");
      return `<li><b>${esc(kinds.get(r.s).label)}</b> ${esc(ontology.predicates[p]?.label || p)} <b>${esc(kinds.get(r.o).label.toLowerCase())}</b> <span class="muted small">(${n} of ${r.total})</span></li>`;
    };
    body.innerHTML = `
      <p class="step-k">4 · Zoom out</p>
      <h2>Every idea is a kind of thing</h2>
      <p>Each idea is sorted into one of nine kinds: four for <b>how a decision is reasoned towards</b>, five for <b>the process it sits inside</b>.
      Zoom out to that level and ${fmt(c.relations.signed + c.relations.machine)} connections become a handful of patterns:</p>
      <ul class="small" style="padding-left:1.1rem">${top.map(say).join("")}</ul>
      <p>That is the shape of examination practice, and it does not rest on any single idea or passage. Add a factor, merge two tests,
      reword a page — the pattern <i>factors feed tests; tests and factors give rise to grounds</i> is still there.</p>
      <p><a class="btn small" href="#/map/kinds">Explore this level on the map →</a></p>`;
    const pic = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "The nine kinds of idea and the patterns between them" });
    arrowDefs(pic);
    const g = svg("g", {}, pic);
    drawKinds(g, ontology, { strongOnly: true, minimal: false, onKind: () => { location.hash = "#/map/kinds"; } });
    stage.appendChild(pic);
    g.querySelectorAll(".kind-bubble").forEach((b, i) => { b.style.opacity = 0; b.style.transition = "opacity .5s"; setTimeout(() => { b.style.opacity = 1; }, 80 * i); });
    g.querySelectorAll(".kind-link, .kind-link-label").forEach((b) => { b.style.opacity = 0; b.style.transition = "opacity .6s"; setTimeout(() => { b.style.opacity = ""; }, 900); });
  }

  // ------------------------------------------------------------- 5. change

  function stepChange() {
    const years = Object.entries(stability.by_year);
    const max = Math.max(...years.map(([, n]) => n));
    const touched = stability.pages.filter((p) => p.relations.length).length;
    body.innerHTML = `
      <p class="step-k">5 · The long game</p>
      <h2>The text changes. The structure holds.</h2>
      <div class="fact"><span class="big num">${fmt(stability.events)}</span><span>amendments recorded on the Manual's pages since ${years[0][0]}</span></div>
      <p>Most update links, rename pages or adjust wording. Each connection in the map is pinned to its passage by reference, and stores a
      fingerprint of the exact text it quotes — so when a page changes, the system lists precisely which connections to re-check, and
      leaves the rest alone.</p>
      <p>The levels above the text change far less: an idea survives a rewording; a kind of idea rests on no passage at all.</p>
      <p><a class="btn small" href="#/change">Try it on any page →</a></p>`;
    stage.innerHTML = `
      <h3 style="margin-top:.2rem">Amendments recorded, by year</h3>
      <div class="bars">${years.map(([y, n]) => `<div><span class="num">${fmt(n)}</span><i style="height:${(n / max) * 100}%"></i><span>${y}</span></div>`).join("")}</div>
      <h3 style="margin-top:1.4rem">The reasons given, most common first</h3>
      <ul class="reasons">${stability.reasons.slice(0, 9).map(([r, n]) => `<li><b>${fmt(n)}</b><span>${esc(r)}</span></li>`).join("")}</ul>
      <p class="caption">From the amendment notes on each page of the published Manual, as captured on ${esc(stability.snapshot)}.
      ${fmt(touched)} of ${fmt(stability.pages.length)} pages hold a passage some connection rests on.</p>`;
  }

  // ------------------------------------------------------------- 6. retrieval

  function stepRetrieval() {
    const ex = tour.example;
    if (!ex) { body.innerHTML = "<p>No example available.</p>"; return; }
    const pct = (x) => Math.round(x * 100);
    const only = new Set(ex.only_ontology_relevant);
    // Two records can share a label (a known duplicate); name each wording once.
    const seen = new Set();
    const via = ex.recognised.filter((r) => !byId.get(r.id)?.generic && !seen.has(r.label) && seen.add(r.label));
    const path = ex.path_focus || ex.paths[0];
    body.innerHTML = `
      <p class="step-k">6 · What it is for</p>
      <h2>Following connections finds what words miss</h2>
      <p>A real test question, written in everyday words:</p>
      <blockquote class="quote">${esc(ex.question)}</blockquote>
      <p class="small">The ontology recognised ${via.map((r) => `<b>${esc(r.label)}</b>${r.matched && r.matched.toLowerCase() !== r.label.toLowerCase() ? ` (from “${esc(r.matched)}”${r.everyday ? ", an everyday phrasing" : ""})` : ""}`).join(", ")}${path ? `, and followed <i>${esc(path.subject_label)} — ${esc(ontology.predicates[path.predicate]?.label || path.predicate)} → ${esc(path.object_label)}</i>` : ""}.</p>
      <p>Its top ten held <b>${only.size}</b> passages a grader rated highly relevant that were in neither keyword search's top ten nor the top ten
      of a search that matches meaning without an ontology. On this question the quality of the top ten was <b>${pct(ex.ndcg.keyword)}</b> for keyword
      search, <b>${pct(ex.ndcg.hybrid)}</b> for meaning-based search and <b>${pct(ex.ndcg.ontology)}</b> with the ontology, out of 100.</p>
      <p class="tiny">One question, chosen because it shows this most clearly among the everyday ones; across all 129 the picture is mixed — see About.
      The grades were given by a model (${esc(ex.grader)}), not a person. Everyday phrasings were written by a machine.</p>
      <p><a class="btn primary small" href="#/ask">Ask your own question →</a></p>`;
    const list = (title, rows, mark) => `<div class="card" style="padding:.8rem .9rem">
      <h4 style="margin:0 0 .4rem">${title}</h4>
      <ol style="margin:0;padding-left:1.3rem">${rows.map(([ref, g]) => `<li class="small${mark && only.has(ref) ? " only" : ""}" style="margin:.3rem 0">
        <span title="Relevance grade ${g ?? "?"} of 3" style="display:inline-flex;gap:2px;vertical-align:middle;margin-right:.35rem">${[1, 2, 3].map((n) => `<i style="width:7px;height:10px;border-radius:2px;background:${(g || 0) >= n ? "var(--ok)" : "var(--line)"}"></i>`).join("")}</span>
        ${refChip(ref)}${mark && only.has(ref) ? ` <span class="via" style="color:var(--glow);font-weight:700;font-size:.72rem">only the ontology found this</span>` : ""}</li>`).join("")}</ol></div>`;
    stage.innerHTML = `<div class="compare" style="margin-top:0">${list("Plain keyword search", ex.keyword, false)}${list("Guided by the ontology", ex.ontology, true)}</div>
      <p class="caption">Green bars: how relevant a grader judged each passage, 0 to 3. Click any passage to read it.</p>`;
  }

  // ------------------------------------------------------------- 7. limits

  function stepLimits() {
    body.innerHTML = `
      <p class="step-k">7 · The honest part</p>
      <h2>What it will never do, and what is not checked yet</h2>
      <p><b>It never decides an application.</b> It explains what the Manual and the legislation say, and declines when asked how a case will come out.</p>
      <p><b>Practice and law stay apart.</b> Every passage is marked as the Manual (practice) or the Act and Regulations (law), including inside answers.</p>
      <p><b>Most of it is unchecked.</b> ${c.concepts.signed} ideas and ${c.relations.signed} connections were signed by a trade marks expert;
      ${c.concepts.machine} ideas and ${fmt(c.relations.machine)} connections were written by a machine from the Manual's text and nobody has reviewed them.
      Each one says which it is, and none becomes "approved" by being left alone.</p>
      <div class="stamp">${stampIcon}<span>That is where you come in: the most useful thing an examiner can do with this map is find what it has wrong.</span></div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-top:1rem"><a class="btn primary" href="#/ask">Ask the Manual</a><a class="btn" href="#/map">Explore the map</a></div>`;
    stage.innerHTML = `
      <h3 style="margin-top:.2rem">Who wrote what</h3>
      <table class="small" style="width:100%;border-collapse:collapse">
        <tr><th style="text-align:left;padding:.4rem 0"></th><th class="num" style="text-align:right">Signed by an expert</th><th class="num" style="text-align:right">Machine-written, unreviewed</th></tr>
        <tr><td style="padding:.4rem 0;border-top:1px solid var(--line-2)">Ideas</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">${c.concepts.signed}</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">${c.concepts.machine}</td></tr>
        <tr><td style="padding:.4rem 0;border-top:1px solid var(--line-2)">Connections</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">${c.relations.signed}</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">${fmt(c.relations.machine)}</td></tr>
        <tr><td style="padding:.4rem 0;border-top:1px solid var(--line-2)">Which kind each idea is</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">0</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">${c.concepts.signed + c.concepts.machine}</td></tr>
        <tr><td style="padding:.4rem 0;border-top:1px solid var(--line-2)">Prepared answers</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">0</td><td class="num" style="text-align:right;border-top:1px solid var(--line-2)">129</td></tr>
      </table>
      <p class="caption">"Signed" means a named trade marks expert read the record and put their name and a date to it. The two are never added together.</p>`;
  }

  root.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => go(Number(b.dataset.step))));
  root.querySelectorAll("[data-move]").forEach((b) => b.addEventListener("click", () => {
    if (step === STEPS.length - 1 && b.dataset.move === "1") { location.hash = "#/ask"; return; }
    go(step + Number(b.dataset.move));
  }));
  const keys = (e) => {
    if (e.target.closest("input, textarea")) return;
    if (e.key === "ArrowRight") go(step + 1);
    if (e.key === "ArrowLeft") go(step - 1);
  };
  document.addEventListener("keydown", keys);
  go(step);
  return () => document.removeEventListener("keydown", keys);
}
