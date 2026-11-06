/* Overview, layer 1: what the proof of concept does, shown before how (ADR-0145, ADR-0148).

   Outcomes first. The hero replays one real test question through the system, from the words
   to the ideas, the connection and the passages. Each outcome card says what it does today, with
   its figure read from the generated data and its state said plainly: working, measured, a
   prototype, untested. The measurement is stated in both directions. Nothing here is typed in:
   every number comes from the data, so it cannot drift from the build. */

import { esc, fmt, load, refLabel, tip, FAMILIES, familyOf, legend } from "./app.js";
import { icon } from "./icons.js";
import { term } from "./glossary.js";

/** A measured difference in words, from its estimate and 95% interval (× 100). */
export function difference([est, lo, hi], better, worse) {
  const pts = (x) => Math.abs(x * 100).toFixed(1);
  const range = `95% interval ${(lo * 100).toFixed(1)} to ${(hi * 100).toFixed(1)}`;
  if (lo > 0) return `<b>${pts(est)} points ${better}</b> <span class="muted">(${range})</span>`;
  if (hi < 0) return `<b>${pts(est)} points ${worse}</b> <span class="muted">(${range})</span>`;
  return `<b>no clear difference</b> <span class="muted">(${range})</span>`;
}

const GRADE = ["not relevant", "marginal", "relevant", "highly relevant"];

export async function render(root, { ontology }) {
  const [stability, examples, live, tour] = await Promise.all([load("stability"), load("examples"), load("live"), load("tour")]);
  const c = ontology.counts;
  const byId = new Map(ontology.concepts.map((x) => [x.id, x]));
  const answers = examples.answers;
  const claims = answers.flatMap((a) => a.claims || []);
  const quoted = claims.filter((x) => x.supported).length;
  const s = examples.summary || {};
  const everyday = s.problem, all = s.all;
  const provisions = Object.keys(stability.provisions || {}).length;
  const firstYear = Object.keys(stability.by_year)[0];
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;
  const ex = tour.example;
  const showcase = tour.showcase.find((x) => x.label === "written permission") || tour.showcase[0];

  root.innerHTML = `
  <div class="hm">
    <section class="wrap hm-hero">
      <div class="hm-copy">
        <span class="eyebrow">Australian trade marks · research prototype</span>
        <h1 class="hm-title">Search Australian trade mark law and guidance</h1>
        <p class="lede">Ask a question in your own words. The tool finds passages from the Trade Marks Act 1995 and Trade Marks Regulations 1995, which set out the law. It also searches IP Australia’s Trade Marks Manual of Practice and Procedure, which explains how examiners apply the law. Open a passage to read it for yourself.</p>
        <div class="hm-cta">
          <a class="btn primary" href="#/ask">Ask a question ${icon("arrow")}</a>
          <a class="btn ghost" href="#/how">See how it works ${icon("chevron")}</a>
        </div>
        <div class="hm-sources">${legend()}</div>
      </div>
      ${ex ? demo(ex, byId, ontology) : ""}
    </section>

    <section class="wrap section hm-outcomes" aria-labelledby="hm-o">
      <div class="sec-head">
        <div><span class="eyebrow">What it does today</span><h2 id="hm-o">What can you do here?</h2></div>
        <p>Choose a tool to search the sources, explore a fictional case or check which records cite a source.</p>
      </div>
      <div class="grid-3">
        ${outcome({
          href: "#/ask", k: "For examiners", title: "Research a trade mark question", visual: miniResearch(),
          text: "Find passages about your question. Open a reference beside an answer to check what the source says.",
          figure: everyday ? `+${(everyday["ndcg:ontology-keyword"][0] * 100).toFixed(1)}` : "", figureText: everyday
            ? `points higher than keyword search on the ranking of the first 10 results for everyday questions (95% interval ${(everyday["ndcg:ontology-keyword"][1] * 100).toFixed(1)} to ${(everyday["ndcg:ontology-keyword"][2] * 100).toFixed(1)})` : "",
          state: ["working", "Working · answers unreviewed"], go: "Ask a question",
        })}
        ${outcome({
          href: "#/customers", k: "Applicant examples", title: "Understand an examiner’s objection", visual: miniExplain(),
          text: "Follow a fictional application to see why an examiner raised an objection, what the law requires and what could happen next.",
          stats: [[fmt(c.tests), "legal tests"], [fmt(c.processes), "example procedures"], [fmt(c.fictional_matters), "fictional cases"]],
          state: ["prototype", "Prototype · not formally tested with customers"], go: "See the preview",
        })}
        ${outcome({
          href: "#/change", k: "Guidance maintenance", title: "Trace a change", visual: miniChange(),
          text: "Choose a section of the Act, a regulation or a Manual page. See which records cite it and may need review if it changes.",
          stats: [[fmt(provisions), "sections and regulations linked to records"], [fmt(stability.events), `amendments to the Manual recorded since ${esc(firstYear)}`]],
          state: ["working", "Working · not measured"], go: "Trace a change",
        })}
      </div>
    </section>

    <section class="hm-band">
      <div class="wrap">
        <div class="hm-band-head">
          <div><span class="eyebrow">How the search works</span><h2>How the search finds related passages</h2></div>
          <p>The tool uses a map of trade mark terms and their connections. The links show where the information came from. The technical name for this model is an ${term("ontology")}.</p>
        </div>
        <div class="hm-why">
          ${why("words", "Different words for the same idea", `The Manual can use several names for one idea. ${fmt(showcase.total)} passages name <i>${esc(showcase.label)}</i>; a search for that term misses ${fmt(showcase.missed)} of them, because they say ${Object.keys(showcase.wordings).filter((w) => w !== showcase.label).slice(0, 2).map((w) => `“${esc(w)}”`).join(" or ")}.`, wordsVisual(showcase))}
          ${why("connect", "Links between ideas", `${fmt(relations)} links connect ${fmt(concepts)} ideas. For example, a link can show what <i>may give rise to</i> an objection. Each link quotes its source.`, connectVisual())}
          ${why("shape", "Conditions and exceptions", `${fmt(c.tests)} legal tests show who acts, when a rule applies and what exceptions it allows. Each test separates facts from the judgements a person must make, and never makes those judgements itself.`, shapeVisual())}
          ${why("show", "Quotations you can check", `${fmt(quoted)} of ${fmt(claims.length)} claims in the prepared answers include a quotation the tool found word for word in the source. Open a reference to see whether it supports the statement.`, showVisual())}
        </div>
        <div class="hm-band-cta"><a class="btn lime" href="#/how">Follow one question through the system ${icon("arrow")}</a><a class="btn on-dark" href="#/map">Explore the knowledge map</a></div>
      </div>
    </section>

    <section class="wrap section hm-measure" aria-labelledby="hm-m">
      <div class="sec-head">
        <div><span class="eyebrow">How well the search works</span><h2 id="hm-m">Better than keyword search. Not better than search by meaning.</h2></div>
        <p>We tried three search methods on the same ${fmt(all?.n || answers.length)} questions. The ${term("ndcg", "ranking score")} gives more weight to relevant passages near the top of the first 10 results. The highest possible score is 100.</p>
      </div>
      ${everyday && all ? `<div class="hm-measure-grid">
        <figure class="card card-pad hm-chart" aria-label="Top-ten quality by search, for everyday-words questions and for all questions">
          ${measureRow("Questions in everyday words", everyday)}
          ${measureRow("All questions", all)}
          <figcaption class="hm-key">
            <span><i class="hm-dot kw"></i>Keyword search: words only</span>
            <span><i class="hm-dot hy"></i>Search by meaning: keyword plus ${term("embedding", "matching by meaning")}, no ontology</span>
            <span><i class="hm-dot on"></i>Guided by the ontology: search by meaning plus the ideas and connections</span>
          </figcaption>
        </figure>
        <div class="hm-read">
          <h3>What the scores tell us</h3>
          <p><b>Map-guided search compared with keywords alone.</b> For everyday questions:
          ${difference(everyday["ndcg:ontology-keyword"], "better", "worse")}. For all questions: ${difference(all["ndcg:ontology-keyword"], "better", "worse")}.</p>
          <p><b>Map-guided search compared with search by meaning.</b> For all questions: ${difference(all["ndcg:ontology-hybrid"], "better", "worse")}.
          For everyday questions: ${difference(everyday["ndcg:ontology-hybrid"], "better", "worse")}.</p>
          <p class="small muted">The map also shows which ideas and links contributed to a result. AI wrote most test questions and graded how relevant the passages were. Only ${fmt(s.signed?.n || 0)} were reviewed by a person.</p>
          <a class="link-arrow" href="#/about">See the test results and their limits ${icon("arrow")}</a>
        </div>
      </div>` : `<p class="muted">Test results are unavailable in this version.</p>`}
    </section>

    <section class="wrap section hm-next" aria-labelledby="hm-n">
      <div class="sec-head">
        <div><span class="eyebrow">Future uses</span><h2 id="hm-n">What else could the tools do?</h2></div>
        <p>The labels show which tools work today and which are proposals.</p>
      </div>
      ${foundation()}
      <p style="margin-top:22px"><a class="link-arrow" href="#/future">Explore the proposed uses ${icon("arrow")}</a></p>
    </section>

    <section class="wrap hm-status" aria-label="Results and limits, in one line each">
      <div class="hm-status-grid">
        ${status("working", "Working", "Search the Manual and legislation, browse example answers, explore the map and check which records cite a source. Live answers depend on availability.")}
        ${status("measured", "Measured", "The tests above compared how well three searches ranked Manual passages. Nothing else has been measured yet.")}
        ${status("prototype", "Built, not tested", "The prototype illustrates legal tests and application steps with fictional cases. It has not been formally tested with customers or measured.")}
        ${status("unreviewed", "Not yet reviewed", `${fmt(c.concepts.machine)} of ${fmt(concepts)} ideas, ${fmt(c.relations.machine)} of ${fmt(relations)} connections, every definition, test and answer: machine-written and labelled ${term("unreviewed", "unreviewed")}.`)}
        ${status("planned", "Possible next", "Possible next steps include testing the explanations with customers (the project owner's decision), exploring policy changes and explaining recorded decisions.")}
        ${status("never", "Never", "Deciding an application, or saying how one will be decided.")}
      </div>
      <p class="hm-status-foot"><a class="link-arrow" href="#/about">See results and limits ${icon("arrow")}</a>${live.enabled ? "" : `<span class="tiny">Live answers are off. The example answers and the search still work.</span>`}</p>
    </section>
  </div>`;

  if (ex) startDemo(root, ex);
}

// ------------------------------------------------------------------ the worked example, replayed

function demo(ex, byId, ontology) {
  const fam = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)] || FAMILIES.other;
  const specific = ex.recognised.filter((r) => !byId.get(r.id)?.generic);
  const generic = ex.recognised.filter((r) => byId.get(r.id)?.generic);
  const path = ex.path_focus || ex.paths[0];
  const only = new Set(ex.only_ontology_relevant);
  const pct = (x) => Math.round(x * 100);
  // The question with the words that named an idea marked, so stage 2 can light them up.
  let q = esc(ex.question);
  for (const r of specific) if (r.matched) q = q.replace(esc(r.matched), `<mark class="hm-said">${esc(r.matched)}</mark>`);
  const idea = (id, label) => `<span class="idea-pill" style="--c:${fam(id).colour};--cb:${fam(id).bg};--ci:${fam(id).ink}"><i></i>${esc(label)}</span>`;
  const squares = (rows, mark) => rows.map(([ref, g], i) => `<button type="button" class="hm-sq g${g ?? 0}${mark && only.has(ref) ? " only" : ""}" data-ref="${esc(ref)}"
    data-tip="${esc(`${i + 1}. ${refLabel(ref)} · graded ${GRADE[g ?? 0]}${mark && only.has(ref) ? " · found through the connection" : ""}`)}" aria-label="${esc(`${refLabel(ref)}, graded ${GRADE[g ?? 0]}`)}"></button>`).join("");
  return `<figure class="card hm-demo" aria-label="Example question and search results">
    <div class="hm-demo-top"><span class="eyebrow">Example question</span>
      <button type="button" class="btn small ghost hm-replay" aria-label="Play the example again">${icon("replay")} Replay</button></div>
    <ol class="hm-stages">
      <li class="hm-stage" data-s="1"><span class="hm-n">1</span><div><span class="hm-lab">The example question</span>
        <p class="hm-q">${q}</p></div></li>
      <li class="hm-stage" data-s="2"><span class="hm-n">2</span><div><span class="hm-lab">Terms the search matched</span>
        <p class="hm-ideas">${specific.map((r) => idea(r.id, r.label)).join("")}${generic.map((r) => `<span class="idea-pill quiet" title="Named in so many passages that it does not steer the search"><i></i>${esc(r.label)}</span>`).join("")}</p>
        ${generic.length ? `<span class="hm-note">Too common to narrow this search: ${esc(generic.map((r) => r.label).join(", "))}</span>` : ""}</div></li>
      ${path ? `<li class="hm-stage" data-s="3"><span class="hm-n">3</span><div><span class="hm-lab">How the matched terms relate</span>
        <p class="hm-path">${idea(path.subject, path.subject_label)}<span class="hm-pred">${esc(ontology.predicates[path.predicate]?.label || path.predicate)}</span>${idea(path.object, path.object_label)}</p>
        ${path.applies_when ? `<span class="hm-note">only when ${esc(path.applies_when.length > 120 ? path.applies_when.slice(0, 118).replace(/\s+\S*$/, "") + " …" : path.applies_when)}</span>` : ""}</div></li>` : ""}
      <li class="hm-stage" data-s="4"><span class="hm-n">4</span><div><span class="hm-lab">The first 10 results</span>
        <div class="hm-rows">
          <span class="hm-rowlab">Keyword search</span><span class="hm-sqs">${squares(ex.keyword, false)}</span>
          <span class="hm-rowlab"><b>Using the knowledge map</b></span><span class="hm-sqs">${squares(ex.ontology, true)}</span>
        </div>
        <p class="hm-found">For this question, following the link found <b>${fmt(only.size)} relevant passages</b> that neither of the other searches ranked in its top 10.</p></div></li>
    </ol>
    <figcaption class="hm-demo-foot">
      <span class="hm-grades"><i class="hm-sq g3"></i>highly relevant<i class="hm-sq g2"></i>relevant<i class="hm-sq g1"></i>marginal<i class="hm-sq g0"></i>not relevant (AI ratings)</span>
      <span>Ranking scores for this question (out of 100): keyword ${pct(ex.ndcg.keyword)}, by meaning ${pct(ex.ndcg.hybrid)}, map-guided ${pct(ex.ndcg.ontology)}.
      We chose this example because it shows how a link can help. The results across all questions are below.</span>
    </figcaption>
  </figure>`;
}

function startDemo(root, ex) {
  const fig = root.querySelector(".hm-demo");
  if (!fig) return;
  const stages = [...fig.querySelectorAll(".hm-stage")];
  let timers = [];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const play = () => {
    timers.forEach(clearTimeout);
    timers = [];
    fig.classList.remove("played");
    stages.forEach((s) => s.classList.remove("on"));
    if (reduced) { stages.forEach((s) => s.classList.add("on")); fig.classList.add("played"); return; }
    stages.forEach((s, i) => timers.push(setTimeout(() => s.classList.add("on"), 250 + i * 1100)));
    timers.push(setTimeout(() => fig.classList.add("played"), 250 + stages.length * 1100));
  };
  fig.querySelector(".hm-replay").addEventListener("click", play);
  fig.addEventListener("mouseover", (e) => { const sq = e.target.closest("[data-tip]"); tip(sq ? esc(sq.dataset.tip) : null, e); });
  fig.addEventListener("mouseleave", () => tip(null));
  // Start when it is on screen, so the first beat is seen.
  const seen = new IntersectionObserver((entries) => { if (entries.some((e) => e.isIntersecting)) { seen.disconnect(); play(); } }, { threshold: 0.3 });
  seen.observe(fig);
}

// ------------------------------------------------------------------ outcome cards and their small pictures

function outcome({ href, k, title, visual, text, figure, figureText, stats, state, go }) {
  return `<article class="card hm-out">
    <a class="hm-out-link" href="${href}" aria-label="${esc(go)}: ${esc(title)}"></a>
    <div class="hm-out-vis" aria-hidden="true">${visual}</div>
    <div class="hm-out-body">
      <span class="eyebrow muted plain">${esc(k)}</span>
      <h3>${esc(title)}</h3>
      <p>${text}</p>
      ${figure ? `<div class="stat"><b>${figure}</b><span>${figureText}</span></div>` : ""}
      ${stats ? `<div class="hm-stats">${stats.map(([n, t]) => `<div class="stat"><b>${n}</b><span>${t}</span></div>`).join("")}</div>` : ""}
      <div class="hm-out-foot"><span class="pill ${state[0]}">${esc(state[1])}</span><span class="link-arrow">${esc(go)} ${icon("arrow")}</span></div>
    </div>
  </article>`;
}

const miniResearch = () => `<svg viewBox="0 0 320 120">
  <rect x="14" y="40" width="74" height="40" rx="10" class="v-bubble"/><text x="51" y="65" class="v-t" text-anchor="middle">“a smell?”</text>
  <path d="M88 60 C110 60 112 30 134 30M88 60H134M88 60 C110 60 112 90 134 90" class="v-line"/>
  <circle cx="142" cy="30" r="8" class="v-n ex"/><circle cx="142" cy="60" r="8" class="v-n re"/><circle cx="142" cy="90" r="8" class="v-n pr"/>
  <path d="M150 30 C190 30 200 22 232 22M150 60 C190 60 200 52 232 52M150 60 C190 60 200 82 232 82M150 90 C190 90 200 98 232 98" class="v-line"/>
  ${[22, 37, 52, 67, 82, 97].map((y, i) => `<rect x="${238 + (i % 2) * 20}" y="${y - 6}" width="12" height="12" rx="2" class="v-sq ${i === 2 ? "hot" : ""}"/>`).join("")}
  <path d="M290 60 l-6 0" class="v-line"/><path d="M286 52 l8 8 -8 8" class="v-line" fill="none"/>
</svg>`;

const miniExplain = () => `<svg viewBox="0 0 320 120">
  <text x="18" y="24" class="v-k">ALL OF THESE</text>
  <rect x="16" y="32" width="84" height="34" rx="8" class="v-box"/><circle cx="30" cy="49" r="5" class="v-assess"/><rect x="40" y="46" width="48" height="6" rx="3" class="v-ln"/>
  <rect x="108" y="32" width="84" height="34" rx="8" class="v-box"/><rect x="117" y="44" width="10" height="10" rx="2" class="v-fact"/><rect x="132" y="46" width="48" height="6" rx="3" class="v-ln"/>
  <rect x="200" y="32" width="84" height="34" rx="8" class="v-box"/><circle cx="214" cy="49" r="5" class="v-assess"/><rect x="224" y="46" width="48" height="6" rx="3" class="v-ln"/>
  <path d="M150 70v14" class="v-line"/><path d="M144 80l6 6 6-6" class="v-line" fill="none"/>
  <rect x="96" y="90" width="110" height="24" rx="12" class="v-must"/><text x="151" y="106" text-anchor="middle" class="v-mt">must · may · may not</text>
</svg>`;

const miniChange = () => `<svg viewBox="0 0 320 120">
  ${[18, 34, 50].map((r, i) => `<circle cx="160" cy="62" r="${r}" class="v-ring" style="animation-delay:${i * .6}s"/>`).join("")}
  <path d="M160 50 L172 62 L160 74 L148 62Z" class="v-act"/>
  ${[[112, 38], [118, 92], [212, 40], [205, 95], [96, 64], [226, 66], [140, 18], [184, 108]].map(([x, y], i) => `<circle cx="${x}" cy="${y}" r="${i < 4 ? 6 : 4.5}" class="v-n ${["ex", "re", "pr", "ex", "pr", "re", "ex", "pr"][i]}"/>`).join("")}
</svg>`;

// ------------------------------------------------------------------ why it works

function why(key, title, text, visual) {
  return `<article class="hm-why-item"><div class="hm-why-vis" aria-hidden="true">${visual}</div><h3>${esc(title)}</h3><p>${text}</p></article>`;
}

function wordsVisual(showcase) {
  const words = Object.keys(showcase.wordings).slice(0, 4);
  const ys = words.map((_, i) => 18 + i * 24);
  return `<svg viewBox="0 0 260 110">${words.map((w, i) => `<text x="8" y="${ys[i] + 4}" class="w-word${w === showcase.label ? " formal" : ""}">${esc(w.length > 22 ? w.slice(0, 21) + "…" : w)}</text>
    <path d="M150 ${ys[i]} C190 ${ys[i]} 190 55 214 55" class="w-line"/>`).join("")}<circle cx="226" cy="55" r="12" class="w-idea"/></svg>`;
}
const connectVisual = () => `<svg viewBox="0 0 260 110"><path d="M40 70 C90 20 150 20 200 46" class="w-line strong"/><path d="M40 70 C100 90 150 96 196 82" class="w-line"/>
  <circle cx="34" cy="72" r="11" class="w-idea ex"/><circle cx="208" cy="44" r="11" class="w-idea re"/><circle cx="204" cy="84" r="9" class="w-idea pr"/>
  <text x="120" y="30" text-anchor="middle" class="w-pred">may give rise to</text></svg>`;
const shapeVisual = () => `<svg viewBox="0 0 260 110"><text x="10" y="18" class="w-k">IF ALL OF</text>
  <rect x="10" y="26" width="70" height="26" rx="6" class="w-box"/><rect x="88" y="26" width="70" height="26" rx="6" class="w-box"/><rect x="166" y="26" width="70" height="26" rx="6" class="w-box dashed"/>
  <text x="10" y="76" class="w-k">THEN</text><rect x="10" y="82" width="110" height="22" rx="11" class="w-must"/><text x="130" y="76" class="w-k">UNLESS</text><rect x="130" y="82" width="106" height="22" rx="11" class="w-box dashed"/></svg>`;
const showVisual = () => `<svg viewBox="0 0 260 110"><rect x="10" y="10" width="180" height="8" rx="4" class="w-ln"/><rect x="10" y="26" width="150" height="8" rx="4" class="w-ln"/>
  <rect x="10" y="48" width="64" height="20" rx="5" class="w-chip m"/><rect x="82" y="48" width="58" height="20" rx="5" class="w-chip a"/>
  <rect x="10" y="80" width="150" height="22" rx="11" class="w-stamp"/><path d="M216 30 l10 10 20 -22" class="w-check"/></svg>`;

// ------------------------------------------------------------------ the measurement, drawn

function measureRow(label, row) {
  const v = { kw: row["ndcg:keyword"] * 100, hy: row["ndcg:hybrid"] * 100, on: row["ndcg:ontology"] * 100 };
  const lo = 60, hi = 90, W = 520, x = (n) => 10 + ((n - lo) / (hi - lo)) * (W - 20);
  const ticks = [60, 65, 70, 75, 80, 85, 90];
  const lab = (key, name, above) => `<g class="hm-mk ${key}" transform="translate(${x(v[key]).toFixed(1)},46)">
    <circle r="${key === "on" ? 8 : 6.5}"/><text y="${above ? -16 : 28}" text-anchor="middle"><tspan class="v">${v[key].toFixed(1)}</tspan> <tspan class="n">${name}</tspan></text></g>`;
  return `<div class="hm-mrow"><h4>${esc(label)} <span class="tiny">${fmt(row.n)} questions</span></h4>
    <svg viewBox="0 0 ${W} 86" role="img" aria-label="${esc(`${label}: keyword ${v.kw.toFixed(1)}, by meaning ${v.hy.toFixed(1)}, guided by the ontology ${v.on.toFixed(1)}, out of 100`)}">
      ${ticks.map((t) => `<line x1="${x(t)}" x2="${x(t)}" y1="30" y2="62" class="hm-grid"/><text x="${x(t)}" y="82" text-anchor="middle" class="hm-tick">${t}</text>`).join("")}
      <line x1="${x(Math.min(v.kw, v.hy, v.on))}" x2="${x(Math.max(v.kw, v.hy, v.on))}" y1="46" y2="46" class="hm-span"/>
      ${lab("kw", "keyword", true)}${lab("hy", "by meaning", true)}${lab("on", "ontology", false)}
    </svg></div>`;
}

// ------------------------------------------------------------------ the foundation, drawn

const USES = [
  ["Examiner research", "working", "Working"],
  ["Customer explanations", "prototype", "Prototype"],
  ["Tracing a change", "working", "Working"],
  ["Policy: simulating an amendment", "prototype", "Two methods demonstrated"],
  ["Customer chatbot with visuals", "planned", "Builds on the prototype"],
  ["Explaining decisions, never making them", "planned", "Not started"],
  ["Machine learning", "planned", "Foundation only"],
];

function foundation() {
  return `<a class="hm-fdn card" href="#/future" aria-label="What the foundation could support: see what's next">
    <div class="hm-pillars">${USES.map(([name, state, label]) => `<div class="hm-pillar ${state}"><b>${esc(name)}</b><span class="pill ${state}">${esc(label)}</span></div>`).join("")}</div>
    <div class="hm-slab"><span>${icon("layers")} The tools share the same trade mark terms, links, sources and author details.</span></div>
  </a>`;
}

function status(state, label, text) {
  return `<div class="hm-st"><span class="pill ${state}">${esc(label)}</span><p>${text}</p></div>`;
}
