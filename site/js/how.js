/* How it works, layer 3 of 4 (ADR-0148): one real question followed through the system.

   A scrolling story with a picture that stays in view. Each step is a stage of what happens when
   someone asks a question in plain words: the text, the words, the ideas they name, the
   connections, the guidance those find, the shape of the law, the cited answer, the map of ideas
   underneath, and who wrote it. The question is the test question tmk-explorer chose for showing
   the connections at work most clearly, and the page says so. Every number is read from the data;
   the page's own prose only says what to look at. It replaces the seven-step tour (ADR-0145),
   whose route redirects here. Classes are prefixed `hw-`. */

import { esc, fmt, load, refChip, refLabel, sourceOf, srcClass, FAMILIES, familyOf, tip, openPassage } from "./app.js";
import { conditionBoxes, effectCard } from "./diagrams.js";
import { layoutIdeas } from "./netlayout.js";
import { term } from "./glossary.js";
import { icon } from "./icons.js";
import * as lib from "./lib.js";

const COLS = 60, CELL = 7.6, PITCH = 9, GRID_Y = 186, VH = 590;

export async function render(root, { ontology, params }) {
  const [tour, examples, search, build] = await Promise.all([load("tour"), load("examples"), load("search"), load("build")]);
  const ex = tour.example;
  if (!ex) { root.innerHTML = `<div class="wrap section"><h1>How it works</h1><p class="muted">This version has no example to show.</p></div>`; return; }
  const c = ontology.counts;
  const byId = new Map(ontology.concepts.map((x) => [x.id, x]));
  const answer = examples.answers.find((a) => a.key === ex.key);
  const path = ex.path_focus || ex.paths[0];
  const specific = ex.recognised.filter((r) => !byId.get(r.id)?.generic);
  const idea = specific[0];
  const showcase = tour.showcase.find((s) => s.id === idea?.id) || null;
  const s43 = (ontology.structures?.tests || []).find((t) => path && byId.get(path.object)?.structures?.includes(t.id)) || (ontology.structures?.tests || [])[0];
  const kinds = ontology.kinds.filter((k) => k.family !== "other").length;
  const concepts = c.concepts.signed + c.concepts.machine, relations = c.relations.signed + c.relations.machine;
  const fam = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)] || FAMILIES.other;
  const pill = (id, label) => `<span class="idea-pill" style="--c:${fam(id).colour};--cb:${fam(id).bg};--ci:${fam(id).ink}"><i></i>${esc(label || byId.get(id)?.label || id)}</span>`;
  const only = new Set(ex.only_ontology_relevant);

  const STEPS = [
    { k: "The starting point", h: "What does the tool search?", p: `This version includes ${fmt(tour.passages)} passages from ${fmt(tour.parts.length)} parts of IP Australia’s Trade Marks Manual of Practice and Procedure. The Manual explains examination practice. The <i>Trade Marks Act 1995</i> and <i>Trade Marks Regulations 1995</i> set out the law.`,
      note: "Each square is one passage, in reading order, shaded by Part. Point at one to see which; click to read it." },
    { k: "A question", h: "What does keyword search find?", p: `“${esc(ex.question)}” Keyword search looks for those words and ranks the passages that contain them. Its top ten
      for this question are marked. Keyword search can miss a relevant passage if it uses different words.`,
      note: "We used this question when we tested the search." },
    { k: "Words to ideas", h: "Which words refer to the same idea?", p: showcase
      ? `The map records that “${esc(idea.matched || idea.label)}” names an idea: <b>${esc(idea.label)}</b>. The Manual names that idea in ${fmt(Object.keys(showcase.wordings).length)} ways across
        ${fmt(showcase.total)} passages; a search for the formal term alone misses ${fmt(showcase.missed)}. Each wording is recorded once, on the idea, so every one of those passages is linked to it.`
      : `The map records that “${esc(idea?.matched || idea?.label || "")}” names an idea: <b>${esc(idea?.label || "")}</b>. Every wording of an idea is recorded once, on the idea, so every passage that names it is linked to it, whatever words it uses.`,
      note: "Coloured squares name the idea; the darker ones use its formal name." },
    { k: "Connections", h: "How does one idea lead to another?", p: path ? `Each link describes a relationship and quotes the source sentence. Here,
      <b>${esc(path.subject_label)}</b> <i>${esc(ontology.predicates[path.predicate]?.label || path.predicate)}</i> <b>${esc(path.object_label)}</b>${path.applies_when ? `, but only when ${esc(path.applies_when)}` : ""}.
      The link keeps the condition in the source${path.modality ? ` and its wording (“${esc(path.modality)}”)` : ""}, so a “may” never becomes a “must”.` : "Each link describes a relationship and quotes the source sentence.",
      note: "Machine-written and unreviewed, like most connections; its card says so wherever it is shown." },
    { k: "Guidance the words miss", h: "What did the map add to the results?", p: `Following the connection, the search adds the passages that name the connected ideas, and merges them with the keyword
      results. On this question its top ten held <b>${fmt(only.size)} relevant passages</b> that neither keyword search nor search by meaning had in theirs.`,
      note: `One question, chosen because it shows this most clearly. Across all ${fmt(examples.answers.length)} test questions the picture is mixed: better than keyword search, not better than search by meaning.` },
    { k: "The legal test", h: "What must an examiner consider?", p: s43 ? `The diagram shows the conditions in section 43 and what follows if they apply. Both conditions require a person’s judgement: the system shows them and never makes them. Writing a rule down in a structured form a computer can read is called ${term("rules-as-code", "rules as code")}.` : "",
      note: "It explains what a provision requires; nothing here applies it to an application." },
    { k: "The answer", h: "Where did the answer come from?", p: `AI uses the selected passages to draft an answer. The tool checks whether quotations match the source text and labels law separately from examination guidance. It will not say how an application would be decided.`,
      note: "Written by a machine and not reviewed by a trade marks expert; the answer says so." },
    { k: "Underneath", h: "Where do these ideas fit on the map?", p: `All of this rests on ${fmt(concepts)} ideas in ${fmt(kinds)} kinds and three families, joined by ${fmt(relations)} connections,
      each tied to the text it comes from. That map is the ${term("ontology")}. The ideas from this question are marked on it.`,
      note: "", cta: `<a class="btn primary" href="#/map">Explore the knowledge map ${icon("arrow")}</a>` },
    { k: "Trust", h: "Who wrote and reviewed the records?", p: `Most of the map was written by a machine and has not been reviewed by a trade marks expert. Every record says so wherever it appears,
      and none becomes approved by being left alone. It is stored in open standards (${term("rdf", "RDF")}, ${term("skos", "SKOS")}, ${term("shacl", "SHACL")},
      ${term("sparql", "SPARQL")}, ${term("prov-o", "PROV-O")}), so any compatible tool can read it, check it and query it.`,
      note: "", cta: `<a class="btn primary" href="#/standards">The standards, in plain words ${icon("arrow")}</a><a class="btn" href="#/about">Results and limits</a>` },
  ];

  root.innerHTML = `
  <div class="hw">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">How it works</span>
        <h1>How the tool finds an answer</h1>
        <p class="lede">Follow an example question from the first keyword match to the passages used in the answer. Scroll to see what changes at each step.</p>
      </div>
      <div class="page-head-side"><a class="btn" href="#/map">${icon("connect")} Skip to the knowledge map</a></div>
    </header>
    <div class="wrap hw-story">
      <div class="hw-steps">${STEPS.map((s, i) => `
        <section class="hw-step" data-step="${i}" aria-labelledby="hw-s${i}">
          <div class="hw-text">
            <span class="hw-k"><b>${i + 1}</b>${esc(s.k)}</span>
            <h2 id="hw-s${i}">${esc(s.h)}</h2>
            <p>${s.p}</p>
            ${s.note ? `<p class="hw-note">${s.note}</p>` : ""}
            ${s.cta ? `<div class="hw-cta">${s.cta}</div>` : ""}
          </div>
        </section>`).join("")}</div>
      <div class="hw-sticky">
        <div class="card hw-canvas" data-scene="0">
          <div class="hw-progress">${STEPS.map((_, i) => `<i data-dot="${i}"></i>`).join("")}</div>
          <svg class="L L-grid" viewBox="0 0 640 ${VH}" aria-label="Every passage of the Manual, one square each"></svg>
          <div class="L L-src"><div class="hw-srcs">
            <div class="manual"><span class="hw-sm"><i class="mark"></i></span><b>${fmt(tour.passages)}</b><span>passages of the Manual<br><em>practice</em></span></div>
            <div class="law act"><span class="hw-sm"><i class="mark"></i></span><b>${fmt(search.provisions.filter((r) => r.startsWith("TMA1995/")).length)}</b><span>provisions of the Act<br><em>law</em></span></div>
            <div class="law regs"><span class="hw-sm"><i class="mark"></i></span><b>${fmt(search.provisions.filter((r) => r.startsWith("TMR1995/")).length)}</b><span>provisions of the Regulations<br><em>law</em></span></div>
          </div></div>
          <div class="L L-q"><div class="hw-bubble">${icon("chat")}<p>${questionHtml(ex, specific)}</p></div></div>
          <div class="L L-idea"></div>
          <div class="L L-conn"></div>
          <div class="L L-cmp"></div>
          <div class="L L-test"></div>
          <div class="L L-ans"></div>
          <svg class="L L-net" viewBox="0 0 640 ${VH}" aria-label="The whole map of ideas"></svg>
          <div class="L L-trust"></div>
        </div>
      </div>
    </div>
    <section class="wrap hw-deeper" aria-labelledby="hw-d">
      <div class="sec-head"><div><span class="eyebrow">Go deeper</span><h2 id="hw-d">Explore the records behind this example</h2></div>
        <p>Open the map, tables or technical notes to check a record for yourself.</p></div>
      <div class="grid-3">
        ${door("#/map", "connect", "The knowledge map", `Every idea and connection, drawn. Select one to read its card: its names, definition, connections and the passages it rests on.`)}
        ${door("#/rules", "scale", "Rules as code", `How connections keep their force, how a provision becomes a structured test, and how every rule is checked on each build.`)}
        ${door("#/standards", "layers", "The standards", `RDF, SKOS, SHACL, SPARQL and PROV-O, each in plain words with a real block of this build, and why no OWL profile is claimed.`)}
        ${door("#/glossary", "book", "Glossary", `Every term the site uses, in plain words, what it does here, and what it is called technically.`)}
        ${door("#/table", "grid", "Data tables", `The kinds, ideas, connections, legal tests and processes as tables, with who wrote each row, and a download of each.`)}
        ${door("#/about", "shield", "Results and limits", `The measurement in both directions, the decisions ahead and whose they are, the release manifest and the limits.`)}
      </div>
    </section>
  </div>`;

  const canvas = root.querySelector(".hw-canvas");
  const grid = root.querySelector(".L-grid");

  // ---------------------------------------------------------------- the waffle of passages
  const partAt = [];
  tour.parts.forEach((part, p) => { for (let j = 0; j < part.n; j++) partAt.push(p); });
  const rows = Math.ceil(tour.passages / COLS);
  const offX = (640 - COLS * PITCH) / 2 + 1;
  void rows;
  let cells = "";
  for (let i = 0; i < tour.passages; i++) {
    cells += `<rect class="hw-cell${partAt[i] % 2 ? " alt" : ""}" data-i="${i}" x="${(offX + (i % COLS) * PITCH).toFixed(1)}" y="${(GRID_Y + Math.floor(i / COLS) * PITCH).toFixed(1)}" width="${CELL}" height="${CELL}" rx="1.6"/>`;
  }
  grid.innerHTML = `<g class="hw-cells">${cells}</g><text x="${offX}" y="${GRID_Y - 10}" class="hw-gk">One square = one passage of the Manual · ${fmt(tour.passages)} in all</text>`;
  const cellEls = [...grid.querySelectorAll(".hw-cell")];

  // The passages in reading order, as `explorer.build._display_order` puts them, so a ref can be
  // found on the grid: by Part number, then page, then position.
  let order = null;
  const readingOrder = () => order || (order = load("passages").then((p) => {
    const key = (part) => { const m = /^Part(\d+)(.*)$/.exec(part || ""); return m ? [Number(m[1]), m[2]] : [999, part || ""]; };
    const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
    const list = p.chunks.map((ch, i) => ({ ch, i, k: key(p.pages[ch[1]]?.part) }))
      .sort((a, b) => a.k[0] - b.k[0] || cmp(a.k[1], b.k[1]) || cmp(a.ch[1], b.ch[1]) || a.i - b.i)
      .map(({ ch }) => ({ ref: ch[0], page: p.pages[ch[1]] || {}, heading: ch[2] }));
    return { list, index: new Map(list.map((r, i) => [r.ref, i])) };
  }));
  readingOrder();
  const paint = (cls, indices) => { for (const i of indices) cellEls[i]?.classList.add(cls); };
  const clear = () => cellEls.forEach((el) => el.setAttribute("class", `hw-cell${partAt[el.dataset.i] % 2 ? " alt" : ""}`));

  // ---------------------------------------------------------------- the layers that are not the grid
  const ideaLayer = root.querySelector(".L-idea");
  if (showcase) {
    const words = Object.entries(showcase.wordings);
    ideaLayer.innerHTML = `<div class="hw-ideacard"><div class="hw-arrow">${icon("down")}</div>${pill(idea.id, idea.label)}
      <p class="hw-wordings">${words.map(([w, list]) => `<span class="${w === showcase.label ? "formal" : ""}">${esc(w)} <b>${fmt(list.length)}</b></span>`).join("")}</p></div>`;
  } else if (idea) ideaLayer.innerHTML = `<div class="hw-ideacard">${pill(idea.id, idea.label)}</div>`;

  const conn = root.querySelector(".L-conn");
  if (path) {
    const other = ex.paths.filter((p) => p.record !== path.record).slice(0, 2);
    conn.innerHTML = `<div class="hw-conncard">
      <div class="hw-cn">${pill(path.subject, path.subject_label)}</div>
      <div class="hw-edge"><span>${esc(ontology.predicates[path.predicate]?.label || path.predicate)}</span>${path.modality ? `<b class="hw-modal">${esc(path.modality)}</b>` : ""}</div>
      <div class="hw-cn">${pill(path.object, path.object_label)}</div>
      ${path.applies_when ? `<p class="hw-when"><b>Only when</b> ${esc(path.applies_when)}</p>` : ""}
      <div class="hw-quote">${quoteFor(path.record)}</div>
      ${other.length ? `<p class="hw-more-conn">Also followed: ${other.map((p) => `${esc(p.subject_label)} <i>${esc(ontology.predicates[p.predicate]?.label || p.predicate)}</i> ${esc(p.object_label)}`).join("; ")}</p>` : ""}
    </div>`;
  }
  function quoteFor(record) {
    const r = ontology.relations.find((x) => x.id === record);
    return r?.quote ? `<blockquote class="quote ${srcClass(r.ref)}" data-src="Source sentence">${esc(r.quote)}</blockquote>${refChip(r.ref)} <span class="trust ${r.origin === "signed" ? "reviewed" : "machine"}">${r.origin === "signed" ? "Expert reviewed" : "AI-written · unreviewed"}</span>` : "";
  }

  const cmp = root.querySelector(".L-cmp");
  const squares = (list, mark) => list.map(([ref, g]) => `<button type="button" class="hm-sq g${g ?? 0}${mark && only.has(ref) ? " only" : ""}" data-ref="${esc(ref)}"
    data-tip="${esc(`<b>${esc(refLabel(ref))}</b><span class="tip-s">graded ${["not relevant", "marginal", "relevant", "highly relevant"][g ?? 0]} by a model${mark && only.has(ref) ? "; found through the connection" : ""}</span>`)}" aria-label="${esc(refLabel(ref))}"></button>`).join("");
  cmp.innerHTML = `<div class="hw-cmpcard"><div class="hm-rows">
      <span class="hm-rowlab">Keyword search</span><span class="hm-sqs">${squares(ex.keyword, false)}</span>
      <span class="hm-rowlab"><b>Using the knowledge map</b></span><span class="hm-sqs">${squares(ex.ontology, true)}</span></div>
    <p class="hw-cmpnote"><span class="hm-grades"><i class="hm-sq g3"></i>highly relevant<i class="hm-sq g2"></i>relevant<i class="hm-sq g1"></i>marginal<i class="hm-sq g0"></i>not relevant</span>
      Ranking scores for this question (out of 100): keyword ${Math.round(ex.ndcg.keyword * 100)}, by meaning ${Math.round(ex.ndcg.hybrid * 100)}, map-guided ${Math.round(ex.ndcg.ontology * 100)}.</p>
    <p class="hw-gridkey"><span><i class="c-idea"></i>names ${esc(idea?.label || "the idea")}</span>${path ? `<span><i class="c-conn"></i>names ${esc(path.object_label)}</span>` : ""}<span><i class="c-onto"></i>in the guided top ten</span><span><i class="c-only"></i>found only through the connection</span></p></div>`;

  const test = root.querySelector(".L-test");
  if (s43) test.innerHTML = `<div class="hw-testcard"><p class="hw-t-title"><b>${esc(s43.title)}</b> ${refChip(s43.provision)}</p>
    <div class="hw-t-if"><span class="dg-lab">If</span>${conditionBoxes(s43.condition)}</div>
    <div class="hw-t-if"><span class="dg-lab">Then</span>${effectCard(s43.effect.kind, s43.effect.text, s43.effect.ref)}</div>
    <p class="tiny"><span class="trust machine">AI-written · unreviewed</span> ${esc(s43.id)}: a structured reading of the provision.</p></div>`;

  const ans = root.querySelector(".L-ans");
  if (answer) {
    const claims = (answer.claims || []).filter((x) => x.supported).slice(0, 3);
    const cites = answer.citations || [];
    const n = (src) => cites.filter((x) => sourceOf(x.ref) === src).length;
    ans.innerHTML = `<div class="hw-anscard"><div class="row spread"><b class="hw-a-h">Answer</b><span class="trust machine">AI-written · unreviewed</span></div>
      ${claims.map((cl) => `<div class="hw-claim"><p>${esc(cl.text.length > 190 ? `${cl.text.slice(0, 188).replace(/\s+\S*$/, "")} …` : cl.text)}</p><p>${cl.quotes.slice(0, 2).map((q) => refChip(q.ref)).join(" ")}</p></div>`).join("")}
      <div class="hw-a-foot"><span class="manual"><i class="mark"></i></span>${fmt(n("manual"))} quotes from the Manual · practice <span class="law act"><i class="mark"></i></span>${fmt(n("act"))} from the Act · law
        <a class="link-arrow" href="#/ask/${esc(ex.key)}">The whole answer ${icon("arrow")}</a></div></div>`;
  }

  const trust = root.querySelector(".L-trust");
  const bar = (label, machine, total) => `<div class="hw-bar"><span>${esc(label)}</span><div class="hw-track"><i style="width:${(100 * machine / Math.max(1, total)).toFixed(1)}%"></i></div><b>${fmt(machine)} of ${fmt(total)}</b></div>`;
  const sample = build.samples?.test;
  trust.innerHTML = `<div class="hw-trustcard"><p class="hw-tr-h">Written by a machine, not yet reviewed</p>
    ${bar("Ideas", c.concepts.machine, concepts)}${bar("Connections", c.relations.machine, relations)}${bar("Definitions", c.definitions, c.definitions)}
    ${bar("Tests and processes", c.tests + c.processes, c.tests + c.processes)}${bar("Prepared answers", examples.answers.length, examples.answers.length)}
    <p class="tiny">A trade marks expert reviewed the remaining records.</p>
    ${sample?.lines?.length ? `<p class="hw-tr-h" style="margin-top:18px">The same record, as the graph stores it</p><pre class="hw-turtle">${esc(sample.lines.slice(0, 7).join("\n"))}\n  …</pre>` : ""}</div>`;

  // ---------------------------------------------------------------- the whole map, small
  const net = root.querySelector(".L-net");
  let netDrawn = false;
  async function drawNet() {
    if (netDrawn) return;
    netDrawn = true;
    const d3 = await lib.d3();
    const { at, links } = layoutIdeas(d3, ontology, { width: 640, height: VH - 70, pad: 34 });
    const mine = new Set([...ex.recognised.map((r) => r.id), ...ex.paths.flatMap((p) => [p.subject, p.object])]);
    net.innerHTML = `<g transform="translate(0,20)">${links.map((l) => { const a = at.get(l.s), b = at.get(l.o); return `<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" class="hw-link${mine.has(l.s) && mine.has(l.o) ? " hot" : ""}"/>`; }).join("")}
      ${[...at.entries()].map(([id, p]) => `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${(p.r * 0.8).toFixed(1)}" class="hw-node${mine.has(id) ? " hot" : ""}" style="fill:${FAMILIES[p.family].colour}"
        data-tip="${esc(`<span class="tip-k">${esc(ontology.kinds.find((k) => k.id === p.kind)?.label || "")}</span><b>${esc(byId.get(id)?.label || id)}</b>`)}"/>`).join("")}
      ${[...mine].filter((id) => at.has(id)).map((id) => { const p = at.get(id); return `<text x="${(p.x + 10).toFixed(1)}" y="${(p.y + 4).toFixed(1)}" class="hw-nlab">${esc(byId.get(id)?.label || id)}</text>`; }).join("")}</g>
      <g class="hw-fam" transform="translate(22,${VH - 20})">${Object.entries(FAMILIES).filter(([k]) => k !== "other").map(([, f], i) => `<g transform="translate(${i * 200},0)"><circle r="5" style="fill:${f.colour}"/><text x="10" y="4">${esc(f.label)}</text></g>`).join("")}</g>`;
  }

  // ---------------------------------------------------------------- scenes
  async function scene(i) {
    canvas.dataset.scene = String(i);
    root.querySelectorAll("[data-dot]").forEach((d) => d.classList.toggle("on", Number(d.dataset.dot) <= i));
    root.querySelectorAll(".hw-step").forEach((s) => s.classList.toggle("on", Number(s.dataset.step) === i));
    clear();
    const { index } = await readingOrder();
    if (Number(canvas.dataset.scene) !== i) return;
    const at = (refs) => refs.map((r) => index.get(r)).filter((x) => x !== undefined);
    if (i === 1) paint("kw", at(ex.keyword.map(([r]) => r)));
    if (i === 2 && showcase) {
      for (const [w, list] of Object.entries(showcase.wordings)) paint(w === showcase.label ? "idea-formal" : "idea", list);
    }
    if (i === 4) {
      if (showcase) for (const list of Object.values(showcase.wordings)) paint("idea", list);
      if (path) paint("conn", at(search.mentions[path.object] || []));
      paint("onto", at(ex.ontology.map(([r]) => r)));
      paint("only", at([...only]));
    }
    if (i === 7) drawNet();
  }

  // Scroll: the step crossing the middle of the screen sets the picture.
  const seen = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) scene(Number(e.target.dataset.step));
  }, { rootMargin: "-48% 0px -48% 0px" });
  root.querySelectorAll(".hw-step").forEach((s) => seen.observe(s));
  scene(0);

  // Pointing at a square says which passage it is; clicking opens it.
  grid.addEventListener("mousemove", async (e) => {
    const cell = e.target.closest(".hw-cell");
    if (!cell) { tip(null); return; }
    const { list } = await readingOrder();
    const row = list[Number(cell.dataset.i)];
    if (!row) return;
    const part = tour.parts[partAt[Number(cell.dataset.i)]];
    tip(`<span class="tip-k">${esc(part?.title || "")}</span><b>${esc(row.page.title || "")}</b><span class="tip-s">${esc(String(row.heading || "").split(" > ").pop())}. Click to read it.</span>`, e);
  });
  grid.addEventListener("mouseleave", () => tip(null));
  grid.addEventListener("click", async (e) => {
    const cell = e.target.closest(".hw-cell");
    if (!cell) return;
    const { list } = await readingOrder();
    const row = list[Number(cell.dataset.i)];
    if (row) openPassage(row.ref);
  });
  canvas.addEventListener("mousemove", (e) => { if (e.target.closest(".L-grid")) return; const t = e.target.closest("[data-tip]"); tip(t ? t.dataset.tip : null, e); });
  canvas.addEventListener("mouseleave", () => tip(null));
  if (params[0] && /^\d+$/.test(params[0])) {
    const target = root.querySelector(`.hw-step[data-step="${Math.max(0, Math.min(STEPS.length - 1, Number(params[0]) - 1))}"]`);
    requestAnimationFrame(() => target?.scrollIntoView({ block: "center" }));
  }
  return () => { seen.disconnect(); tip(null); };
}

function questionHtml(ex, specific) {
  let q = esc(ex.question);
  for (const r of specific) if (r.matched) q = q.replace(esc(r.matched), `<mark class="hw-said">${esc(r.matched)}</mark>`);
  return q;
}

function door(href, ic, title, text) {
  return `<a class="card hw-door" href="${href}"><span class="hw-door-i">${icon(ic)}</span><h3>${esc(title)}</h3><p>${text}</p><span class="link-arrow">Open ${icon("arrow")}</span></a>`;
}
