/* Research a question (Ask the Manual): a question, the ideas it finds, the connections it
   follows, the passages it gathers, and a cited answer.

   Retrieval runs in the browser (engine.js, the same ranking Python measured, less the vectors).
   The answer comes from the model only when the site was built with live answers on; the 129
   prepared answers always work. Live, the model first reads a typed question against the map, so
   a question in everyday words ("a smell") still starts from ideas on it (ADR-0132). Every answer
   is stamped unreviewed, keeps the Manual and the legislation apart, and declines to say how an
   application would be decided.

   The page leads with the outcome (ADR-0148): the answer and the sources it read, then how the
   ontology found them, then the same question through plain keyword search, then the detail. */

import { esc, fmt, load, refChip, refLabel, isLaw, sourceOf, srcClass, SOURCES, legend, stampIcon, srcBadge, srcShape, FAMILIES, familyOf, tip } from "./app.js";
import { svg, curve, wrapText, wait } from "./graph.js";
import { Engine, Recogniser, authorityFlags, namedProvisions, structuredTests } from "./engine.js";
import { answer as callModel, read as readModel, cost, partialFields, viaProxy, wake } from "./live.js";
import { icon } from "./icons.js";
import * as lib from "./lib.js";

/** Markdown → sanitised HTML, with bracketed refs turned into passage chips. */
async function renderAnswer(text) {
  const markdown = await lib.markdown();
  const refs = [];
  const tokenised = String(text || "").replace(/\[([^\]\n]{3,400})\]/g, (whole, inner) => {
    const parts = inner.split(/\s*[;,]\s*/).map((x) => x.trim()).filter(Boolean);
    if (!parts.length || !parts.every((x) => /^(TMM|TMA1995|TMR1995)\//.test(x))) return whole;
    refs.push(parts);
    return `@@REF${refs.length - 1}@@`;
  });
  return markdown(tokenised).replace(/@@REF(\d+)@@/g, (_, i) => refs[Number(i)].map((ref) => refChip(ref)).join(" "));
}

let engine = null;
let recogniser = null;

async function getEngine(status) {
  if (engine) return engine;
  status("Loading the Manual's text for searching…");
  const [search, passages] = await Promise.all([load("search"), load("passages")]);
  status("Indexing the Manual's passages…");
  await new Promise((r) => setTimeout(r, 20));
  engine = new Engine(search, passages);
  status("");
  return engine;
}

const todayKey = () => `tmk-asks-${new Date().toISOString().slice(0, 10)}`;
const usedToday = () => { try { return Number(localStorage.getItem(todayKey()) || 0); } catch { return 0; } };
const countOne = () => { try { localStorage.setItem(todayKey(), String(usedToday() + 1)); } catch { /* storage blocked */ } };

export async function render(root, { ontology, params }) {
  const [examples, chat, live] = await Promise.all([load("examples"), load("chat"), load("live").catch(() => ({ enabled: false }))]);
  wake(live);
  const answersOn = !!live.enabled; // `live` is shadowed below, where it means "a typed question"
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const prepared = new Map(examples.answers.map((a) => [a.key, a]));
  const fam = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)] || FAMILIES.other;
  let controller = null;

  const featured = pickFeatured(examples);
  root.innerHTML = `
  <div class="rs">
    <header class="wrap page-head rs-head">
      <div>
        <span class="eyebrow">For examiners</span>
        <h1>Research a question</h1>
        <p class="lede">Ask in your own words. It brings back the passages of the Manual, the Act and the Regulations that bear on the
        question, shows how it found each one, and writes an answer whose every claim is cited and marked as the Manual's practice or the law.</p>
      </div>
      <div class="page-head-side">${answersOn ? `<span class="pill working">Live answers on</span>` : `<span class="pill planned">Prepared answers · live answers off</span>`}</div>
    </header>
    <div class="wrap rs-ask">
      <form class="searchbox rs-form" role="search">
        ${icon("search")}
        <textarea name="q" maxlength="600" rows="1" placeholder="e.g. Can I register a mark that includes someone's name without their consent?" aria-label="Your question"></textarea>
        <button class="btn primary" type="submit">Ask ${icon("arrow")}</button>
      </form>
      <div class="rs-meta"><span class="live-status"></span><span class="load-status" role="status"></span></div>
      <div class="rs-try">
        <div class="rs-try-head"><span class="rs-try-k">Or try a prepared question, answered in advance</span>
          <button type="button" class="btn small ghost rs-browse-btn" aria-expanded="false">${icon("list")} Browse all ${fmt(examples.answers.length)}</button></div>
        <div class="rs-cards">${featured.map((a) => `<button type="button" class="rs-qcard" data-key="${esc(a.key)}"><span>${esc(examples.kinds[a.kind] || "")}</span>${esc(a.question)}</button>`).join("")}</div>
      </div>
      <div class="rs-browse card" hidden>
        <div class="rs-browse-head"><input type="search" class="rs-filter" placeholder="Filter the prepared questions" aria-label="Filter the prepared questions">
          <span class="tiny">Answered in advance by the same pipeline, so they work without a live connection.</span></div>
        <div class="rs-browse-body">${Object.entries(examples.kinds).map(([kind, label]) => {
          const rows = examples.answers.filter((a) => a.kind === kind);
          return rows.length ? `<section class="rs-group"><h4>${esc(label)} <span class="tiny">${rows.length}</span></h4>
            <ul>${rows.map((a) => `<li><button type="button" class="link" data-key="${esc(a.key)}">${esc(a.question)}</button></li>`).join("")}</ul></section>` : "";
        }).join("")}</div>
      </div>
    </div>
    <div class="wrap rs-result"></div>
    <div class="wrap rs-preview">
      <div class="rs-pv"><span class="rs-pv-n">1</span><h3>An answer, every claim cited</h3><p>Each claim carries the quotes it rests on, checked word for word against the passage, and the answer is marked as machine-written.</p></div>
      <div class="rs-pv"><span class="rs-pv-n">2</span><h3>What it read, law and practice apart</h3><p>The Manual's passages and the provisions of the Act and the Regulations, listed apart, each saying how it was found.</p></div>
      <div class="rs-pv"><span class="rs-pv-n">3</span><h3>How it found them</h3><p>The ideas it recognised in your words, the connections it followed, and what plain keyword search would have returned instead.</p></div>
    </div>
  </div>`;

  const form = root.querySelector(".rs-form");
  const box = form.querySelector("textarea");
  const result = root.querySelector(".rs-result");
  const loadStatus = (text) => { root.querySelector(".load-status").textContent = text; };
  const browse = root.querySelector(".rs-browse");
  const browseBtn = root.querySelector(".rs-browse-btn");

  function liveStatus() {
    const el = root.querySelector(".live-status");
    if (!live.enabled) { el.innerHTML = `Live answers are off on this copy. A typed question still runs the search in your browser; the prepared questions show their answers.`; return; }
    const left = Math.max(0, chat.daily_limit - usedToday());
    el.innerHTML = `Live answers <b>on</b> · <code>${esc(chat.model)}</code> · ${left} of ${chat.daily_limit} questions left today in this browser`;
  }
  liveStatus();

  const grow = () => { box.style.height = "auto"; box.style.height = `${Math.min(160, box.scrollHeight)}px`; };
  box.addEventListener("input", grow);
  form.addEventListener("submit", (e) => { e.preventDefault(); askLive(box.value.trim()); });
  box.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
  root.querySelectorAll("[data-key]").forEach((b) => b.addEventListener("click", () => {
    browse.hidden = true; browseBtn.setAttribute("aria-expanded", "false");
    showPrepared(prepared.get(b.dataset.key));
  }));
  browseBtn.addEventListener("click", () => {
    browse.hidden = !browse.hidden;
    browseBtn.setAttribute("aria-expanded", String(!browse.hidden));
    if (!browse.hidden) browse.querySelector(".rs-filter").focus();
  });
  browse.querySelector(".rs-filter").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    browse.querySelectorAll("li").forEach((li) => { li.hidden = q.length > 1 && !li.textContent.toLowerCase().includes(q); });
    browse.querySelectorAll(".rs-group").forEach((g) => { g.hidden = ![...g.querySelectorAll("li")].some((li) => !li.hidden); });
  });

  // ------------------------------------------------------------ layout of a result

  function frame(question, subtitle) {
    root.querySelector(".rs-preview")?.remove();
    result.innerHTML = `
      <div class="rs-qline"><span class="eyebrow muted plain">${esc(subtitle)}</span><p class="rs-q">${esc(question)}</p></div>
      <div class="rs-top">
        <article class="card rs-answer">
          <div class="rs-card-head"><h2>Answer</h2><span class="answer-tags"></span></div>
          <div class="answer-body"></div>
        </article>
        <aside class="card rs-sources" aria-label="The sources it read">
          <div class="rs-card-head"><h3>What it read</h3><span class="tiny rs-src-count"></span></div>
          <div class="rs-src-body"></div>
        </aside>
      </div>
      <section class="card rs-how" aria-labelledby="rs-how-h">
        <div class="rs-card-head"><div><span class="eyebrow">How it found them</span><h2 id="rs-how-h">The ideas in the question, and where they led</h2></div>
          <div class="rs-legend">${legend()}<span class="rs-found-key"><i></i>found through the ontology</span></div></div>
        <div class="hop-svg"></div>
        <ol class="hop-steps"></ol>
      </section>
      <section class="card rs-compare" aria-labelledby="rs-cmp-h">
        <div class="rs-card-head"><div><span class="eyebrow">The difference it makes</span><h2 id="rs-cmp-h">The same question, through plain keyword search</h2></div></div>
        <div class="compare"></div>
      </section>
      <div class="rs-more">
        <details class="rs-tests" hidden><summary>The legal test this question reaches</summary><div class="det-body tests"></div></details>
        <details><summary>The Act and the Regulations: provisions named or matched</summary><div class="det-body provisions"></div></details>
        <details><summary>How it chose, in detail</summary><div class="det-body hop-why"></div></details>
      </div>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
    return {
      hop: result.querySelector(".hop-svg"), steps: result.querySelector(".hop-steps"), why: result.querySelector(".hop-why"),
      compare: result.querySelector(".compare"), body: result.querySelector(".answer-body"), tags: result.querySelector(".answer-tags"),
      sources: result.querySelector(".rs-src-body"), count: result.querySelector(".rs-src-count"),
      tests: result.querySelector(".tests"), testsBox: result.querySelector(".rs-tests"), provisions: result.querySelector(".provisions"),
    };
  }

  // ------------------------------------------------------------ live questions

  async function askLive(question) {
    if (question.length < 4) { box.focus(); return; }
    if (controller) controller.abort();
    controller = new AbortController();
    const signal = controller.signal;
    const canAnswer = live.enabled && usedToday() < chat.daily_limit;
    const reads = canAnswer && !!chat.reading;
    if (canAnswer) { countOne(); liveStatus(); }
    // The reading and the Manual's text load side by side: neither needs the other.
    const reading = reads ? readModel(live, chat, question, signal).then((reply) => ({ reply }), (error) => ({ error })) : Promise.resolve(null);
    const eng = await getEngine(loadStatus);
    if (signal.aborted) return;
    history.replaceState(null, "", "#/ask");
    const view = frame(question, canAnswer ? "Your question, answered live" : "Your question, searched in your browser");
    // A proxy that has slept says nothing for up to a minute while it wakes.
    let sleepy = reads && viaProxy(live) ? setTimeout(() => {
      const status = view.steps.querySelector(".reading-status") || view.body.querySelector(".thinking-text");
      if (status) status.textContent = "Waiting for the answer service; after a quiet spell it can take up to a minute to wake…";
    }, 10000) : null;
    const ready = reading.then((outcome) => {
      clearTimeout(sleepy);
      if (signal.aborted) return null;
      const read = outcome?.reply ? {
        ...eng.reading(question, outcome.reply.parsed, chat.reading.max_ideas),
        model: outcome.reply.model, cost: cost(outcome.reply.usage, chat.prices),
      } : outcome?.error ? { kept: [], dropped: [], error: String(outcome.error.message || outcome.error).replace(/\.+$/, "") } : null;
      const prep = eng.prepare(question, chat, read?.kept || []);
      const graph = {
        question, reading: read,
        recognised: prep.trace.recognised.map((r) => ({ id: r.id, matched: question.slice(r.start, r.end), name: r.label, start: r.start, end: r.end, everyday: r.alias, read: !!r.read, why: r.why, generic: eng.generic.has(r.id) })),
        paths: prep.paths.map(([s, p, o, record, origin]) => ({ s, p, o, record, origin })),
        followed: prep.trace.paths.map(([s, p, o, record, origin]) => ({ s, p, o, record, origin })),
        passages: prep.passages, legislation: prep.legislation, plain: prep.plain, mentions: eng.s.mentions,
      };
      explain(view, graph, { live: true });
      renderSources(view, graph, prep.hits, false);
      renderCompare(view.compare, prep.plain, prep.passages, prep.hits);
      renderProvisions(view.provisions, question, prep.legislation, eng);
      renderTests(view, question, prep.trace.recognised.map((r) => r.id), eng.s.tests);
      return { prep, g: graph, steps: describe(graph, { linkedCount: prep.weight ? prep.weight.size : 0, live: true }) };
    });
    const animation = animate(view, question, ready, { reading: reads });
    const built = await ready;
    if (!built) return;
    const { prep, g } = built;
    clearTimeout(sleepy);
    if (!live.enabled) {
      await animation;
      view.tags.innerHTML = `<span class="pill planned">No live answer</span>`;
      view.body.innerHTML = `<div class="rs-empty">${icon("info")}<div><p><b>Live answers are off on this copy, so no answer was written.</b>
        Everything else on this page, the ideas recognised, the connections followed and the passages ranked, ran in your browser.</p>
        <p class="small muted">Try a prepared question above to see the answer the same pipeline wrote in advance.</p></div></div>`;
      return;
    }
    if (!canAnswer) {
      await animation;
      view.body.innerHTML = `<p class="muted">This browser has asked ${chat.daily_limit} live questions today, the courtesy limit. The prepared questions still work.</p>`;
      return;
    }
    view.body.innerHTML = `<div class="thinking"><span class="spinner"></span><span class="thinking-text">Reading the ${prep.passages.length} passages${prep.legislation.length ? ` and ${prep.legislation.length} provisions` : ""}…</span></div>
      <div class="answer streaming"></div>`;
    // Stream: claims arrive one by one, each followed by its quotes. Shown as an unchecked
    // draft until the reply is complete and every quote is checked (A08).
    let lastPaint = 0, painting = false;
    sleepy = viaProxy(live) && !g.reading?.model ? setTimeout(() => {
      const status = view.body.querySelector(".thinking-text");
      if (status) status.textContent = "Waiting for the answer service; after a quiet spell it can take up to a minute to wake…";
    }, 10000) : null;
    const onText = async (text) => {
      clearTimeout(sleepy);
      const now = performance.now();
      if (painting || now - lastPaint < 120) return;
      painting = true; lastPaint = now;
      const sofar = partialFields(text, "text");
      const status = view.body.querySelector(".thinking-text");
      if (!sofar.length) {
        if (status) status.textContent = "Reading the passages…";
      } else {
        const n = (text.match(/"ref"\s*:/g) || []).length;
        if (status) status.textContent = `Writing the answer, an unchecked draft: ${sofar.length} claim${sofar.length > 1 ? "s" : ""}, ${n} quote${n === 1 ? "" : "s"} so far, each checked when the answer is complete…`;
        const holder = view.body.querySelector(".answer.streaming");
        if (holder) holder.innerHTML = `<p class="tiny draft">Unchecked draft</p>` + await renderAnswer(sofar.join("\n\n"));
      }
      painting = false;
    };
    try {
      const reply = await callModel(live, chat, eng.prompt(prep, chat), signal, onText);
      clearTimeout(sleepy);
      await animation;
      const claims = eng.verify(reply.parsed.claims, prep, chat);
      // Every cut is marked on the page as in the prompt (A06).
      const cuts = [...eng.excerpts(prep, chat)].filter(([, e]) => e.cut).map(([ref, e]) => ({ ref, cut: e.cut }));
      const spent = cost(reply.usage, chat.prices);
      showAnswer(view, {
        claims, cuts, answer: claims.map((c) => c.text).join("\n\n"),
        citations: claims.flatMap((c) => c.quotes), dropped: claims.flatMap((c) => c.dropped),
        declined: reply.parsed.declined, decline_reason: reply.parsed.decline_reason,
        model: reply.model, when: "just now", live: true, seconds: reply.seconds,
        cost: spent == null ? null : spent + (g.reading?.cost || 0), readingCost: g.reading?.cost, reading: g.reading,
      });
    } catch (error) {
      clearTimeout(sleepy);
      if (signal.aborted) return;
      view.body.innerHTML = `<p class="err">No answer: ${esc(String(error.message).replace(/\.+$/, ""))}.</p><p class="tiny">The passages beside and below are still what the ontology found, and the prepared questions still work.</p>`;
    }
  }

  // ------------------------------------------------------------ prepared answers

  async function showPrepared(a) {
    if (!a) return;
    if (controller) controller.abort();
    box.value = a.question;
    grow();
    history.replaceState(null, "", `#/ask/${encodeURIComponent(a.key)}`);
    const view = frame(a.question, `A prepared question · ${examples.kinds[a.kind] || ""}`);
    let mentions = null, matched = new Map(), relations = null, tests = null;
    try {
      const search = await load("search");
      mentions = search.mentions;
      relations = search.relations;
      tests = search.tests;
      recogniser = recogniser || new Recogniser(search);
      matched = new Map(recogniser.recognise(a.question).map((r) => [r.id, r]));
    } catch { /* drawn without passage links */ }
    const graph = {
      question: a.question,
      recognised: a.recognised.map((r) => {
        const m = matched.get(r.id);
        return { id: r.id, generic: !!byId.get(r.id)?.generic, matched: m ? a.question.slice(m.start, m.end) : null, name: m?.label, start: m?.start, end: m?.end, everyday: !!m?.alias };
      }),
      paths: a.paths.map((p) => ({ s: p.subject, p: p.predicate, o: p.object, record: p.record, origin: p.origin })),
      passages: a.passages, legislation: a.legislation, plain: a.keyword10?.length ? a.keyword10 : a.plain, mentions,
    };
    // Every connection the search followed, from the same records `Engine.trace` reads (the
    // prepared answers' first twelve match them, question by question).
    const specific = new Set(graph.recognised.filter((r) => !r.generic).map((r) => r.id));
    graph.followed = relations ? [...new Map(relations.filter((e) => specific.has(e[0]) || specific.has(e[2]))
      .map((e) => [e[3], { s: e[0], p: e[1], o: e[2], record: e[3], origin: e[4] }])).values()] : graph.paths;
    renderSources(view, graph, null, true);
    renderCompare(view.compare, graph.plain, a.passages, null, true);
    renderTests(view, a.question, a.recognised.map((r) => r.id), tests);
    view.provisions.innerHTML = a.legislation.length
      ? `<p>Given to the answer with the passages: ${a.legislation.map((ref) => refChip(ref)).join(" ")}</p><p class="tiny">Ask it as your own question to see the provisions it names and those its words match, searched apart from the Manual.</p>`
      : `<p class="muted">No provision of the Act or the Regulations was given to this answer.</p>`;
    explain(view, graph, { live: false });
    showAnswer(view, { ...a, live: false, when: a.date });
    await animate(view, a.question, { g: graph, steps: describe(graph, { live: false }) });
  }

  // ------------------------------------------------------------ the sources it read

  /** The passages the answer was written from, and the provisions given with them, each saying
      how it was found. Live, a passage outside keyword search's top ten came through the
      ontology; a prepared answer's search also matched by meaning, so all that can be said is
      that keyword search did not have it. */
  function renderSources(view, g, hits, preparedAnswer) {
    const plainSet = new Set((g.plain || []).slice(0, 10));
    const why = new Map((hits || []).map((h) => [h.ref, h.why || []]));
    const tag = (ref) => {
      if (plainSet.has(ref)) return `<span class="rs-how-tag words">your words</span>`;
      if (preparedAnswer) return `<span class="rs-how-tag beyond" title="Not in plain keyword search's top ten. The prepared search also matched by meaning, so this may have come from that or from the ontology.">beyond keyword search</span>`;
      const w = why.get(ref) || [];
      return `<span class="rs-how-tag onto" title="${esc(`reached by: ${w.join(", ")}`)}">through the ontology</span>`;
    };
    const row = (ref, i) => `<li class="${srcClass(ref)}"><button type="button" class="rs-src" data-ref="${esc(ref)}">
      <span class="rs-rank">${i + 1}</span><i class="mark" aria-hidden="true"></i>
      <span class="rs-src-t"><b data-title="${esc(ref)}">${esc(refLabel(ref))}</b><span class="tiny">${esc(SOURCES[sourceOf(ref)].short)} · ${esc(SOURCES[sourceOf(ref)].role)}</span></span>
      ${isLaw(ref) ? "" : tag(ref)}</button></li>`;
    view.count.textContent = `${g.passages.length} passages${g.legislation.length ? `, ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""}` : ""}`;
    view.sources.innerHTML = `
      <h4 class="rs-src-h"><span class="manual"><i class="mark"></i></span>The Manual · practice</h4>
      <ol class="rs-src-list">${g.passages.map(row).join("") || `<li class="empty">None.</li>`}</ol>
      ${g.legislation.length ? `<h4 class="rs-src-h"><span class="law act"><i class="mark"></i></span>The Act and the Regulations · law</h4>
      <ol class="rs-src-list">${g.legislation.map(row).join("")}</ol>` : ""}
      <p class="tiny rs-src-note">Click any one to read it. Practice and law are listed apart, as the answer must keep them.</p>`;
    // Titles for the passages, once the Manual's text has loaded (it is shared with the drawer).
    load("passages").then((p) => {
      const rows = new Map(p.chunks.map((c) => [c[0], c]));
      view.sources.querySelectorAll("[data-title]").forEach((b) => {
        const ref = b.dataset.title;
        const law = p.legislation[ref];
        if (law) { b.textContent = `${refLabel(ref)} · ${String(law[2] || "").split(" > ").pop().replace(/^\d+[A-Z]*\s+/, "")}`; return; }
        const c = rows.get(ref);
        if (!c) return;
        const head = String(c[2] || "").split(" > ").pop();
        b.textContent = head.length > 90 ? `${head.slice(0, 88).replace(/\s+\S*$/, "")} …` : head;
        b.title = `${refLabel(ref)}: ${c[2]}`;
      });
    }).catch(() => {});
  }

  // ------------------------------------------------------------ how it found them, drawn

  function describe(g, { linkedCount = 0, live }) {
    const rec = g.recognised.filter((r) => !r.generic);
    const generic = g.recognised.filter((r) => r.generic);
    const recIds = new Set(rec.map((r) => r.id));
    const followed = g.followed || g.paths;
    const neighbours = new Set(followed.map((p) => (recIds.has(p.s) ? p.o : p.s)).filter((id) => !recIds.has(id)));
    const plainSet = new Set((g.plain || []).slice(0, 10));
    const beyond = g.passages.filter((r) => !plainSet.has(r)).length;
    const name = (r) => {
      const label = byId.get(r.id)?.label || r.id;
      const note = r.read ? `“${esc(r.matched)}”, read by the model`
        : r.matched && r.matched.toLowerCase() !== label.toLowerCase() ? `“${esc(r.matched)}”${r.everyday ? ", an everyday phrasing" : ""}` : "";
      return `<b>${esc(label)}</b>${note ? ` <span class="muted">(${note})</span>` : ""}`;
    };
    const read = g.reading;
    const readNote = !live ? "" : read?.error ? ` <span class="muted">(The model could not read the question for ideas in other words, so only names were matched.)</span>`
      : !read && !rec.length && !answersOn ? ` <span class="muted">With live answers on, a model also reads the question for ideas it raises in other words.</span>` : "";
    return [
      ["Recognise", (rec.length ? `Recognised ${rec.length} idea${rec.length > 1 ? "s" : ""} in the question: ${rec.slice(0, 5).map(name).join(", ")}${rec.length > 5 ? "…" : ""}.${generic.length ? ` <span class="muted">(<i>${generic.map((r) => esc(byId.get(r.id)?.label)).join("</i>, <i>")}</i> ${generic.length > 1 ? "are" : "is"} named so often it is not used to steer.)</span>` : ""}`
        : read?.model ? `Found no specific idea in the question, by name or in the model's reading, so this is plain keyword search.`
        : `Recognised no specific idea in the question, so this is plain keyword search.`) + readNote],
      ["Follow", followed.length ? `Followed ${followed.length > 1 ? `all ${followed.length} connections` : "the one connection"} from ${rec.length > 1 ? "them" : "it"}, one step out, to ${neighbours.size} related idea${neighbours.size === 1 ? "" : "s"}${followed.length > g.paths.length ? `; ${g.paths.length} of them go to the answer-writer` : ""}.${(() => { const old = g.paths.filter((p) => ontology.retired_predicates?.[p.p]).length; return old ? ` <span class="muted">Prepared before the ontology was restructured on 9 October 2026: ${old} of the connections drawn said only "is related to" and have since been re-read or withdrawn.</span>` : ""; })()}`
        : rec.length ? `The map records no connections for ${rec.length > 1 ? "these ideas" : "this idea"}, so there were none to follow. That is what the map holds, not a finding that none exist.` : `No connections to follow.`],
      ["Gather", live && !linkedCount ? `Gathered no passages through the map's links, so the passages come from keyword search alone${g.legislation.length ? `, with ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""} of the legislation` : ""}. They may not be all the Manual says.`
        : live ? `Gathered ${fmt(linkedCount)} passages linked to those ideas${g.legislation.length ? `, and ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""} of the legislation` : ""}.`
        : `Gathered the passages linked to those ideas${g.legislation.length ? `, and ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""} of the legislation` : ""}.`],
      ["Rank", `Ranked them with the question's own words${live ? "" : " and meaning"}: ${g.passages.length} passages for the answer${g.plain?.length ? `, ${beyond} of them outside plain keyword search's top ${Math.min(10, g.plain.length)}` : ""}.`],
      ["Answer", !live ? `Shows the answer written from them in advance.` : answersOn ? `Wrote an answer citing only those passages, each quote checked against the text.` : `Wrote no answer: live answers are off on this copy.`],
    ];
  }

  /** Draw the hop diagram. `ready` is the graph and its steps, or a promise of them while the
      model reads the question; the question is drawn at once either way. */
  async function animate(view, question, ready, { reading = false } = {}) {
    const Wd = 1180, Ht = 470;
    const pic = svg("svg", { viewBox: `0 0 ${Wd} ${Ht}`, role: "img", "aria-label": "How the question was answered: ideas, connections, passages", class: "hop" });
    view.hop.appendChild(pic);
    const defs = svg("defs", {}, pic);
    const m = svg("marker", { id: "harrow", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" }, defs);
    svg("path", { d: "M0,0 L10,5 L0,10 z", class: "arrowhead" }, m);
    const lines = svg("g", {}, pic), labels = svg("g", {}, pic), nodes = svg("g", {}, pic);
    const cols = { q: 105, rec: 270, nb: 625, psg: 945 };
    [["Your question", cols.q, "middle"], ["Ideas recognised", cols.rec, "start"], ["Connected ideas", cols.nb, "start"], ["Passages and provisions", cols.psg - 12, "start"]].forEach(([t, x, anchor]) =>
      svg("text", { x, y: 20, "text-anchor": anchor, class: "hop-col" }, pic).textContent = t.toUpperCase());

    // 1. the question
    const qText = wrapText(question || "", 21, 8);
    const qg = svg("g", { opacity: 0 }, nodes);
    const qh = 30 + qText.length * 21;
    svg("rect", { x: cols.q - 95, y: Ht / 2 - qh / 2, width: 190, height: qh, rx: 14, class: "hop-q" }, qg);
    qText.forEach((line, i) => svg("text", { x: cols.q, y: Ht / 2 - qh / 2 + 26 + i * 21, "text-anchor": "middle", class: "hop-qt" }, qg).textContent = line);
    const qAnchor = { x: cols.q + 95, y: Ht / 2 };

    // While the model reads the question against the map, say so, and show the map's ideas as a
    // column of faint dots being looked over.
    let pending = null;
    if (reading) {
      view.steps.innerHTML = `<li class="on"><span class="hop-k">Reading</span><span class="reading-status">Reading your question against the map's ${fmt(ontology.concepts.length)} ideas, for the ones it raises in other words…</span></li>`;
      pending = svg("g", { class: "reading" }, nodes);
      for (let i = 0; i < 9; i++) {
        const y = spread(i, 9, 80, Ht - 60);
        svg("path", { d: curve(qAnchor, { x: cols.rec, y }, 0, 8, 0.05).d, class: "edge", "stroke-opacity": 0.12, "stroke-dasharray": "2 4" }, pending);
        svg("circle", { cx: cols.rec + 8, cy: y, r: 6, style: `animation-delay:${(i * 0.12).toFixed(2)}s` }, pending);
      }
      svg("text", { x: cols.rec + 24, y: Ht / 2 + 4, class: "reading-label" }, pending).textContent = "reading the question…";
    }
    qg.style.transition = "opacity .45s"; qg.setAttribute("opacity", 1);
    const built = await ready;
    pending?.remove();
    if (!built) return;
    const { g, steps } = built;
    view.steps.innerHTML = steps.map(([k, s]) => `<li><span class="hop-k">${esc(k)}</span><span>${s}</span></li>`).join("");
    const items = [...view.steps.children];

    // Ideas are pills: a connection leaves from one's right edge and arrives at the other's left.
    const pillW = (id) => Math.min(236, 40 + 7.1 * Math.min(28, (byId.get(id)?.label || id).length));
    // 2. recognised ideas
    const rec = g.recognised.slice(0, 7);
    const recAt = new Map(rec.map((r, i) => [r.id, { x: cols.rec, y: spread(i, rec.length, 66, Ht - 46), w: pillW(r.id) }]));
    // 3. neighbours (at most 8)
    const recIds = new Set(rec.map((r) => r.id));
    const nbIds = [];
    for (const p of g.paths) {
      const other = recIds.has(p.s) ? p.o : p.s;
      if (!recIds.has(other) && !nbIds.includes(other)) nbIds.push(other);
    }
    const nbShown = nbIds.slice(0, 8);
    const nbAt = new Map(nbShown.map((id, i) => [id, { x: cols.nb, y: spread(i, nbShown.length, 60, Ht - 40), w: pillW(id) }]));
    // 4. passages and provisions
    const plainSet = new Set((g.plain || []).slice(0, 10));
    const all = [...g.passages, ...g.legislation];
    const psAt = new Map(all.map((ref, i) => [ref, { x: cols.psg, y: spread(i, all.length, 46, Ht - 18) }]));
    const left = (at) => ({ x: at.x, y: at.y });
    const right = (at) => ({ x: at.x + at.w, y: at.y });
    const bez = (a, b, pull = 0.45) => { const dx = Math.max(40, (b.x - a.x) * pull); return `M${a.x},${a.y} C${a.x + dx},${a.y} ${b.x - dx},${b.y} ${b.x},${b.y}`; };
    const loop = (a, b) => `M${a.x},${a.y} C${a.x + 70},${a.y} ${b.x + 70},${b.y} ${b.x},${b.y}`;

    const ideaNode = (id, at, extra) => {
      const concept = byId.get(id);
      const f = fam(id);
      const gg = svg("g", { class: `hop-idea${extra?.read ? " read" : ""}${extra?.generic ? " generic" : ""}`, transform: `translate(${at.x},${at.y})`, opacity: 0, tabindex: 0, role: "link", "aria-label": `${concept?.label || id}, open on the map` }, nodes);
      svg("rect", { x: 0, y: -15, width: at.w, height: 30, rx: 15, class: "hop-pill", style: extra?.generic ? "" : `fill:${f.bg};stroke:${f.colour}` }, gg);
      svg("circle", { cx: 15, cy: 0, r: 5.5, style: `fill:${extra?.generic ? "var(--f-other)" : f.colour}` }, gg);
      const name = concept?.label || id;
      svg("text", { x: 27, y: 4.5, class: "hop-il" }, gg).textContent = name.length > 28 ? `${name.slice(0, 27)}…` : name;
      const said = (n) => (extra.matched.length > n ? `“${extra.matched.slice(0, n - 1)}…”` : `“${extra.matched}”`);
      if (extra?.read && extra.matched) svg("text", { x: 14, y: 31, class: "hop-said em" }, gg).textContent = `${said(24)}, read by the model`;
      else if (extra?.matched && extra.matched.toLowerCase() !== name.toLowerCase()) svg("text", { x: 14, y: 31, class: "hop-said" }, gg).textContent = `from ${said(26)}`;
      else if (extra?.generic) svg("text", { x: 14, y: 31, class: "hop-said" }, gg).textContent = "too common to steer";
      const go = () => { location.hash = `#/map/ideas/${id}`; };
      gg.addEventListener("click", go);
      gg.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
      gg.dataset.tip = extra?.read
        ? `<b>${esc(name)}</b><span class="tip-s">The model read “${esc(extra.matched)}” as this idea${extra.why ? `: ${esc(extra.why)}` : ""} (a machine's reading, unreviewed). Click to open it on the map.</span>`
        : `<span class="tip-k">${esc(ontology.kinds.find((k) => k.id === concept?.kind)?.label || "")}</span><b>${esc(name)}</b><span class="tip-s">Click to open it on the map.</span>`;
      return gg;
    };

    // draw everything hidden, then reveal in order
    const recEls = rec.map((r) => {
      const at = recAt.get(r.id);
      const line = svg("path", { d: bez(qAnchor, left(at), 0.5), class: "edge", opacity: 0, "stroke-dasharray": r.generic ? "3 4" : null }, lines);
      return [line, ideaNode(r.id, at, r)];
    });
    const pathEls = [];
    for (const p of g.paths) {
      const a = recAt.get(p.s) || nbAt.get(p.s), b = recAt.get(p.o) || nbAt.get(p.o);
      if (!a || !b) continue;
      const sameCol = (recAt.has(p.s) && recAt.has(p.o)) || (nbAt.has(p.s) && nbAt.has(p.o));
      let d, mid;
      if (sameCol) { const ra = right(a), rb = right(b); d = loop(ra, rb); mid = { x: Math.max(ra.x, rb.x) + 56, y: (ra.y + rb.y) / 2 }; }
      else if (a.x < b.x) { const ra = right(a), lb = left(b); d = bez(ra, lb); mid = { x: (ra.x + lb.x) / 2, y: (ra.y + lb.y) / 2 }; }
      else { const la = left(a), rb = right(b); d = `M${la.x},${la.y} C${la.x - 50},${la.y} ${rb.x + 50},${rb.y} ${rb.x},${rb.y}`; mid = { x: (la.x + rb.x) / 2, y: (la.y + rb.y) / 2 }; }
      const path = svg("path", { d, class: "edge strong", opacity: 0, "marker-end": "url(#harrow)" }, lines);
      const label = svg("text", { x: mid.x, y: mid.y - 6, class: "edge-label", "text-anchor": "middle", opacity: 0 }, labels);
      label.textContent = ontology.predicates[p.p]?.label || ontology.retired_predicates?.[p.p] || p.p;
      pathEls.push(path, label);
    }
    const nbEls = nbShown.map((id) => ideaNode(id, nbAt.get(id)));
    if (nbIds.length > nbShown.length) svg("text", { x: cols.nb + 14, y: Ht - 4, class: "hop-more" }, nodes).textContent = `+ ${nbIds.length - nbShown.length} more`;
    const mentionSets = new Map();
    const mentions = g.mentions || engine?.s.mentions || {};
    const generic = new Set(rec.filter((r) => r.generic).map((r) => r.id));
    for (const id of [...recAt.keys(), ...nbAt.keys()]) if (!generic.has(id)) mentionSets.set(id, new Set(mentions[id] || []));
    const psEls = [];
    const linkEls = [];
    all.forEach((ref, i) => {
      const at = psAt.get(ref);
      const law = isLaw(ref), src = sourceOf(ref);
      const viaWords = plainSet.has(ref);
      const gg = svg("g", { class: `hop-psg ${srcClass(ref)}${!law && !viaWords ? " found" : ""}`, transform: `translate(${at.x},${at.y})`, opacity: 0, "data-ref": ref, tabindex: 0, role: "button" }, nodes);
      // The same marks as everywhere: a square for the Manual, a diamond for the Act, a hexagon for the Regulations.
      if (!law && !viaWords) svg("circle", { r: 15, class: "hop-glow" }, gg);
      gg.insertAdjacentHTML("beforeend", srcShape(src, 8));
      svg("text", { x: 18, y: 5, class: `hop-pl${law ? " law" : ""}` }, gg).textContent = `${law ? "" : `${i + 1}. `}${refLabel(ref)}`.slice(0, 28);
      gg.setAttribute("aria-label", `${refLabel(ref)}, ${SOURCES[src].short}, ${SOURCES[src].role}. Read it.`);
      gg.dataset.tip = `<span class="tip-k">${esc(SOURCES[src].short)} · ${esc(SOURCES[src].role)}</span><b>${esc(refLabel(ref))}</b><span class="tip-s">${law ? "Given to the answer with the passages." : viaWords ? "Also in plain keyword search's top ten." : "Not in plain keyword search's top ten: found through the ontology."} Click to read it.</span>`;
      psEls.push(gg);
      // Link a passage to at most two of the ideas it names, recognised ideas first, so the picture
      // shows which hop brought it in without becoming a hairball.
      let linked = false;
      const namers = [...mentionSets.entries()].filter(([, set]) => set.has(ref)).map(([id]) => id)
        .sort((a, b) => (recAt.has(b) - recAt.has(a))).slice(0, 2);
      for (const id of namers) {
        const from = recAt.get(id) || nbAt.get(id);
        linkEls.push(svg("path", { d: bez(right(from), { x: at.x - 13, y: at.y }, 0.5), class: "edge faint", opacity: 0 }, lines));
        linked = true;
      }
      if (!linked && !law) linkEls.push(svg("path", { d: bez(qAnchor, { x: at.x - 13, y: at.y }, 0.35), class: "edge words", opacity: 0, "stroke-dasharray": "4 4" }, lines));
    });

    // The Manual's own headings, once its text has loaded (shared with the drawer and the list).
    load("passages").then((p) => {
      const rows = new Map(p.chunks.map((c) => [c[0], c]));
      psEls.forEach((gg, i) => {
        const c = rows.get(gg.dataset.ref);
        if (!c) return;
        const head = String(c[2] || "").split(" > ").pop();
        gg.querySelector(".hop-pl").textContent = `${i + 1}. ${head.length > 30 ? `${head.slice(0, 29).replace(/\s+\S*$/, "")}…` : head}`;
      });
    }).catch(() => {});

    // Solid lines draw themselves in; dashed ones fade in.
    const show = (els) => els.forEach((e) => {
      if (e.tagName === "path" && !e.getAttribute("stroke-dasharray") && e.getTotalLength && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
        const length = e.getTotalLength();
        e.style.strokeDasharray = `${length}`;
        e.style.strokeDashoffset = `${length}`;
        e.setAttribute("opacity", 1);
        requestAnimationFrame(() => { e.style.transition = "stroke-dashoffset .7s ease-out"; e.style.strokeDashoffset = "0"; });
        return;
      }
      e.style.transition = "opacity .45s"; e.setAttribute("opacity", 1);
    });
    show([qg]);
    await wait(350); items[0]?.classList.add("on"); show(recEls.flat());
    await wait(750); items[1]?.classList.add("on"); show([...pathEls, ...nbEls]);
    await wait(850); items[2]?.classList.add("on"); show(linkEls);
    await wait(700); items[3]?.classList.add("on"); show(psEls);
    await wait(500); items[4]?.classList.add("on");
  }

  // ------------------------------------------------------------ how it chose, in words

  function explain(view, g, { live }) {
    const rec = g.recognised.filter((r) => !r.generic);
    const generic = g.recognised.filter((r) => r.generic);
    const followed = g.followed || g.paths;
    const recIds = new Set(rec.map((r) => r.id));
    const neighbours = new Set(followed.map((p) => (recIds.has(p.s) ? p.o : p.s)).filter((id) => !recIds.has(id)));
    const machine = followed.filter((p) => p.origin !== "approved" && p.origin !== "signed").length;
    const shown = g.paths.length;
    const label = (id) => byId.get(id)?.label || id;
    const nameKind = (r) => {
      const c = byId.get(r.id);
      if (r.read) return `read by the model${r.why ? `: ${r.why}` : ""}`;
      if (!r.name) return "";
      if (r.everyday) return "an everyday phrasing a machine added to it";
      if (r.name.toLowerCase() === (c?.label || "").toLowerCase()) return "its main name";
      return "another of its names";
    };
    const row = (r) => `<li><span class="said">“${esc(r.matched || label(r.id))}”</span><span class="arrow">→</span>
      <span><a href="#/map/ideas/${esc(r.id)}"><b>${esc(label(r.id))}</b></a>${r.name || r.read ? ` <span class="muted">· ${esc(nameKind(r))}</span>` : ""}
      ${r.generic ? `<br><span class="muted">named in ${fmt((g.mentions?.[r.id] || []).length)} passages, more than one in five, so it is recognised but not used to steer</span>` : ""}</span></li>`;
    // A longer name does not hide a shorter one inside it.
    const nested = g.recognised.filter((a) => !a.read && a.start != null && g.recognised.some((b) => b !== a && !b.read && b.start != null && b.start <= a.start && b.end >= a.end && b.end - b.start > a.end - a.start));
    const reading = g.reading;
    const byModel = rec.filter((r) => r.read).length;
    const readingNote = !reading ? ""
      : reading.error ? `<p class="small">A model was also asked to read the question for ideas it raises in other words, but could not (${esc(reading.error)}), so only names were matched.</p>`
      : `<p>Then, because a question in your own words rarely uses the map's names, a model (<code>${esc(reading.model || chat.model)}</code>) reads it against the list of all
        ${fmt(ontology.concepts.length)} ideas and picks up to ${chat.reading.max_ideas} it is about, each with the words of your question it read as that idea, which the page
        checks are really there. That is a machine's judgement, unreviewed: ${byModel ? `the ${byModel === 1 ? "idea" : `${byModel} ideas`} it found ${byModel === 1 ? "is" : "are"} marked “read by the model”` : "here it found none the names had not already found"}.
        The prepared answers were searched by names alone.</p>
        ${reading.dropped?.length ? `<p class="tiny">Set aside from the model's reading: ${reading.dropped.map((d) => `${esc(byId.get(d.id)?.label || d.id || "an unnamed idea")}${d.words ? ` (“${esc(d.words.slice(0, 60))}”)` : ""}, because ${esc(d.reason)}`).join("; ")}.</p>` : ""}`;
    view.why.innerHTML = `
      <div class="why-step"><span class="n">1</span><div>
        <b>Where it starts: ${reading?.model ? "the ideas in your words" : "names in your words"}</b>
        <p>Your question is compared with the name of every idea in the map: its main name, its other names, and the everyday phrasings a machine
        added. An idea is a starting point when one of its names appears in the question as whole words (capitals ignored; names under four letters
        skipped). It is plain matching: no model, no guessing at what you meant.</p>
        ${readingNote}
        ${g.recognised.length ? `<ul class="said-list">${[...rec, ...generic].map(row).join("")}</ul>` : `<p class="muted">No idea's name appears in this question${reading?.model ? ", and the model found none it raises in other words" : ""}, so nothing on the map steered the search: it ran on your words alone.</p>`}
        ${nested.length ? `<p class="tiny">A longer name does not hide a shorter one inside it: “${esc(nested[0].matched)}” is part of a longer match, and counts as well.</p>` : ""}
      </div></div>
      <div class="why-step"><span class="n">2</span><div>
        <b>Which connections: all of them, one step out</b>
        ${followed.length ? `<p>Every connection the map records for a starting idea is followed: here <b>${fmt(followed.length)}</b>, to <b>${fmt(neighbours.size)}</b> other idea${neighbours.size === 1 ? "" : "s"}
        (${fmt(machine)} of them written by a machine, unreviewed). None is weighed against another, whatever it says or
        whoever wrote it, and none is followed a second step.</p>
        <p>Following a connection does two things: the idea at its far end adds its name to the search, and passages that name that idea gain a point
        (step 3). So no path is taken over another; one counts for more only when the idea it reaches is named in passages that also match your question.</p>
        ${followed.length > shown ? `<p class="small">The answer-writer is also shown ${shown} of them as context, and the diagram draws those (up to eight of their ideas). They are simply the first ${shown}
        when the connections are sorted by the identifiers of the ideas at each end, <b>not</b> the most relevant; the other ${fmt(followed.length - shown)} steered the search
        just the same.</p>`
          : `<p class="small">All ${fmt(followed.length)} are shown to the answer-writer as context.</p>`}`
        : `<p class="muted">${rec.length ? "The map records no connections for the starting ideas, so there was nothing to follow. That is what the map holds, not a finding that none exist." : "With no starting idea, there were no connections to follow."}</p>`}
      </div></div>
      <div class="why-step"><span class="n">3</span><div>
        <b>Which passages: three lists, merged</b>
        <ol class="lists">
          <li>passages ranked by your own words (plain keyword search);</li>
          <li>the same, with the names of the starting and connected ideas added to your words;</li>
          <li>the map's list: a passage scores 2 for each starting idea it names, 1 for each connected idea, and 1 if it cites a provision a starting idea rests on.</li>
        </ol>
        <p>A passage high on several lists rises above one high on only one${live ? "" : "; the prepared answers merged a fourth list too, which matches by meaning"}.
        The top ${chat.passages_k} go to the answer-writer, with up to ${chat.legislation_k} provisions of the Act or Regulations: those the starting ideas rest on, then those the top passages cite.
        The design was fixed before any of it was measured.</p>
      </div></div>
      ${rec.length ? `<p class="small"><a class="link-arrow" href="#/map/ideas/${esc(rec[0].id)}">Open ${esc(label(rec[0].id))} on the knowledge map ${icon("arrow")}</a></p>` : ""}`;
  }

  /** A07: the provisions the question names, and those its words match, apart from the Manual's
      ranking. Not sent to the model; unmeasured. */
  function renderProvisions(target, question, given, eng) {
    const named = namedProvisions(question, eng.legislation);
    const matched = eng.provisionSearch(question, 5).map((h) => h.ref);
    target.innerHTML = `<p class="small">Provisions named in the question, then those its words match, searched apart from the Manual and not yet measured.</p>
      <ol class="rs-plist">${[...new Set([...named, ...matched])].map((ref) => `<li>${refChip(ref)}${named.includes(ref) ? `<span class="via">named in the question</span>` : ""}${given.includes(ref) ? `<span class="via" title="Given to the model with the passages">given to the answer</span>` : ""}</li>`).join("") || `<li class="empty">Nothing matched.</li>`}</ol>`;
  }

  /** A06 step 2: the structured tests the question reaches (`structuredTests`), each with its
      conditions and exceptions and what settles each. Machine-written, unreviewed, and not given
      to the answer: shown so the exceptions are never out of sight. */
  function renderTests(view, question, recognised, tests) {
    const reached = tests ? structuredTests(question, recognised, tests) : [];
    if (!reached.length) return;
    const byTest = new Map(tests.map((t) => [t.id, t]));
    const tree = (n) => n.children
      ? `<span class="tiny">${n.kind === "all" ? "all of these" : "any one of these"}</span>${n.text ? " " + esc(n.text) : ""}<ul>${n.children.map((c) => `<li>${tree(c)}</li>`).join("")}</ul>`
      : `${esc(n.text)} <span class="via">${n.kind === "evaluative" ? "an assessment" : "a fact"}</span> ${refChip(n.ref)}`;
    const why = { named: "named in the question", ground: "its ground recognised" };
    view.testsBox.hidden = false;
    view.testsBox.open = true;
    view.tests.innerHTML = `<p class="small"><span class="trust machine">Machine · unreviewed</span> A structured reading of the provision, not given to the answer and not yet measured.</p>
      ${reached.map(({ id, why: w }) => {
        const t = byTest.get(id);
        return `<div class="rs-test"><p><b>${esc(t.title)}</b> ${refChip(t.provision)} <span class="via">${w.map((k) => why[k]).join(", ")}</span></p>
          <p class="small">${esc(t.effect)}</p><div class="rs-tree">${tree(t.condition)}</div>
          ${t.exceptions.map((x) => `<p class="small"><b>Exception</b> ${refChip(x.ref)} <span class="via">${esc(x.kind)}</span> ${esc(x.text)} ${esc(x.effect)}</p><div class="rs-tree">${tree(x.condition)}</div>`).join("")}
          <p class="small"><a class="link-arrow" href="#/customers/requirements/${esc(t.id)}">See it explained, as a customer would ${icon("arrow")}</a></p></div>`;
      }).join("")}`;
  }

  /** The same question through plain keyword search beside the passages the answer read, each
      joined to itself where both found it, so what the ontology added stands out. */
  function renderCompare(target, plain, guided, hits, preparedAnswer = false) {
    const left = (plain || []).slice(0, 10);
    const right = guided;
    const leftSet = new Set(left), rightSet = new Set(right);
    const why = new Map((hits || []).map((h) => [h.ref, h.why]));
    const ROW = 40, H = Math.max(left.length, right.length) * ROW;
    const added = right.filter((r) => !leftSet.has(r)).length;
    const item = (ref, i, side) => {
      const both = side === "l" ? rightSet.has(ref) : leftSet.has(ref);
      const cls = side === "r" && !both ? " added" : side === "l" && !both ? " dropped" : "";
      const tag = side === "r" && !both ? (preparedAnswer
        ? `<span class="via" title="Not in plain keyword search's top ten. The prepared search also used meaning-vectors, so this may have come from them or from the ontology.">beyond keyword top 10</span>`
        : `<span class="via onto" title="${esc("reached by: " + (why.get(ref) || []).join(", "))}">via the ontology</span>`) : "";
      return `<li class="${srcClass(ref)}${cls}" style="height:${ROW}px"><button type="button" data-ref="${esc(ref)}"><span class="rs-rank">${i + 1}</span><i class="mark" aria-hidden="true"></i><span class="rs-cl" data-title="${esc(ref)}">${esc(refLabel(ref))}</span>${tag}</button></li>`;
    };
    const links = right.map((ref, j) => {
      const i = left.indexOf(ref);
      if (i < 0) return "";
      const y1 = i * ROW + ROW / 2, y2 = j * ROW + ROW / 2;
      return `<path d="M0 ${y1} C60 ${y1} 60 ${y2} 120 ${y2}" class="rs-link${i === j ? " same" : ""}"/>`;
    }).join("");
    target.innerHTML = `
      <p class="rs-cmp-lede">${added
        ? `<b>${fmt(added)} of the ${fmt(right.length)} passages the answer read were not in keyword search's top ten.</b> ${preparedAnswer ? "The prepared search also matched by meaning, so some may have come from that as well as from the ontology." : "Each came in through an idea the question named, or a connection from one."}`
        : `<b>Keyword search had every passage the answer read in its top ten</b>; the ontology changed their order, not the list.`}</p>
      <div class="rs-cmp">
        <div><h4>Keyword search <span class="tiny">words only, top ${left.length}</span></h4><ol class="rs-cl-list">${left.map((r, i) => item(r, i, "l")).join("") || `<li class="empty">Nothing matched.</li>`}</ol></div>
        <svg class="rs-cmp-svg" viewBox="0 0 120 ${H}" preserveAspectRatio="none" style="height:${H}px" aria-hidden="true">${links}</svg>
        <div><h4>Guided by the ontology <span class="tiny">what the answer read</span></h4><ol class="rs-cl-list">${right.map((r, i) => item(r, i, "r")).join("")}</ol></div>
      </div>
      <p class="tiny">A line joins a passage both found. On the right, a highlighted passage is one keyword search did not have; on the left, a faded one is one the guided search left out.</p>`;
    load("passages").then((p) => {
      const rows = new Map(p.chunks.map((c) => [c[0], c]));
      target.querySelectorAll("[data-title]").forEach((b) => {
        const c = rows.get(b.dataset.title);
        if (!c) return;
        const head = String(c[2] || "").split(" > ").pop();
        b.textContent = head.length > 60 ? `${head.slice(0, 58).replace(/\s+\S*$/, "")} …` : head;
        b.parentElement.title = `${refLabel(b.dataset.title)}: ${c[2]}`;
      });
    }).catch(() => {});
  }

  // ------------------------------------------------------------ the answer

  /** An answer-v4 answer, claim by claim: each with the quotes that were found in what the model
      was given, or marked as having none (A08). */
  async function claimsBlock(claims) {
    const parts = [];
    for (const c of claims) {
      const misread = c.authority === "legislation" && c.supported && !c.quotes.some((q) => isLaw(q.ref));
      parts.push(`<div class="claim${c.supported ? "" : " unsupported"}">${await renderAnswer(c.text)}
        <div class="claim-refs">${c.supported ? c.quotes.map((q) => refChip(q.ref)).join(" ")
          : `<span class="nosupport" title="The model gave no quote for this claim that could be found in what it was given.">No checked support</span>`}
        ${misread ? `<span class="nosupport">Said to state the legislation, but every quote kept is from the Manual</span>` : ""}</div></div>`);
    }
    const none = claims.length && !claims.some((c) => c.supported);
    return `${none ? `<div class="stamp" style="margin-bottom:14px">${stampIcon}<span><b>No claim in this answer has a checked quote.</b> Read all of it as unsupported.</span></div>` : ""}
      <div class="answer claims">${parts.join("")}</div>`;
  }

  async function showAnswer(view, a) {
    const cites = a.citations || [];
    const conflated = authorityFlags(a.answer, cites.map((x) => x.ref));
    const bySource = (src) => cites.filter((x) => sourceOf(x.ref) === src).length;
    view.tags.innerHTML = `<span class="trust machine">Machine · unreviewed</span>`;
    view.body.innerHTML = `
      ${a.declined ? `<div class="stamp" style="margin-bottom:14px">${stampIcon}<span><b>Part of this question asked how an application would be decided, and the answer declines that part.</b>${a.decline_reason ? " " + esc(a.decline_reason) : ""}</span></div>` : ""}
      ${a.claims ? await claimsBlock(a.claims) : `<div class="answer">${await renderAnswer(a.answer)}</div>`}
      ${conflated.length ? `<div class="stamp" style="margin-top:14px">${stampIcon}<span><b>Practice or law?</b> ${esc(conflated[0].message)}<ul class="tiny" style="margin:6px 0 0">${conflated.map((f) => `<li>“${esc(f.sentence.slice(0, 220))}${f.sentence.length > 220 ? "…" : ""}”</li>`).join("")}</ul></span></div>` : ""}
      <details class="quiet rs-cites"><summary>Citations · ${cites.length} <span class="tiny">(${bySource("manual")} Manual · ${bySource("act")} Act · ${bySource("regs")} Regulations)</span></summary>
        <div class="det-body"><p class="tiny">Each quote was found word for word in the passage${a.claims ? " as the model was given it. That proves the words are there, not that they support the claim" : ""}.</p>
        <ul class="rs-cite-list">${cites.map((x) => `<li>${srcBadge(x.ref)} ${refChip(x.ref)} <span class="muted">“${esc(String(x.quote || "").slice(0, 220))}${String(x.quote || "").length > 220 ? "…" : ""}”</span></li>`).join("")}</ul>
        ${a.cuts?.length ? `<p class="tiny">Given to the model in part, every cut marked: ${a.cuts.map((x) => `${refChip(x.ref)} <span class="muted">(${esc(x.cut)})</span>`).join("; ")}. What a cut omits exists.</p>` : ""}
        ${a.dropped?.length ? `<p class="tiny">${a.dropped.length} citation${a.dropped.length > 1 ? "s" : ""} the model gave could not be found word for word in the passage, and ${a.dropped.length > 1 ? "were" : "was"} removed.</p>` : ""}</div>
      </details>
      <div class="stamp rs-stamp">${stampIcon}<span>Written by a machine (<code>${esc(a.model || "")}</code>${a.live ? "" : `, ${esc(a.when || "")}`}) from the passages shown, and not reviewed by a trade marks expert.
        The Manual states the Registrar's practice; it is not law. This is not advice and not an examination decision.
        It says what these passages and connections record, and they may not be complete: a requirement, exception or step they do not mention may still exist.
        A "Practice or law?" warning comes from a word check that can miss: no warning does not mean every attribution to the legislation is right.</span></div>
      <p class="tiny rs-provenance">${a.live ? `Live answer · ${a.seconds ? a.seconds.toFixed(0) + " s" : ""}${a.cost != null ? ` · about US${(a.cost * 100).toFixed(1)}¢${a.readingCost ? `, ${(a.readingCost * 100).toFixed(1)}¢ of it reading the question` : ""}` : ""} · ${esc(chat.effort)} reasoning effort (the prepared answers used ${esc(chat.measured_effort)}) · search ran without the meaning-vectors the measured system also used${a.reading?.kept?.length ? `, and started from ${a.reading.kept.length === 1 ? "an idea" : `${a.reading.kept.length} ideas`} the model read in the question, which the measured system did not do` : ""}.`
        : `Prepared answer, written ${esc(a.when || "")} with ${esc(chat.measured_effort)} reasoning effort by the same pipeline (${esc(chat.prepared_prompt_version)}): given complete provisions with every cut marked, as a live answer is, and each claim's quotes checked against what it was given.`}
        Read against ${esc(lawLine(a.live ? chat.law : examples.law, a.live ? chat.manual : examples.manual))}.</p>`;
  }

  // Hover a passage or idea in the diagram for its name; click to open it.
  result.addEventListener("mousemove", (e) => {
    const t = e.target.closest("[data-tip]");
    tip(t ? t.dataset.tip : null, e);
  });
  result.addEventListener("mouseleave", () => tip(null));
  result.addEventListener("keydown", (e) => { const p = e.target.closest(".hop-psg"); if (p && e.key === "Enter") p.dispatchEvent(new MouseEvent("click", { bubbles: true })); });

  if (params[0] && prepared.has(params[0])) showPrepared(prepared.get(params[0]));
  return () => { controller?.abort(); tip(null); };
}

/** "the Manual as captured on 3 August 2026, the Act as in force from 14 October 2024 and the
    Regulations as in force from …": which compilation of each instrument an answer read
    (ADR-0136, F09), and when the Manual was captured (R10). A live answer reads the pinned
    snapshot's; a prepared one, the snapshot it was written against. */
function lawLine(law, manual) {
  const lines = (law || []).map((l) => l.line);
  const read = lines.length ? lines.join(" and ") : "the legislation the snapshot holds";
  // R10: the Manual's capture date beside the compilations, and whether it predates one.
  return manual ? `${manual.line}, ${read}${manual.note ? `. ${manual.note.replace(/\.$/, "")}` : ""}` : read;
}

function spread(i, n, top, bottom) {
  if (n <= 1) return (top + bottom) / 2;
  const gap = Math.min(64, (bottom - top) / (n - 1));
  const mid = (top + bottom) / 2;
  return mid + (i - (n - 1) / 2) * gap;
}

function pickFeatured(examples) {
  // One or two of each kind that have a connection to draw, in id order: not chosen by how well
  // the ontology did on them.
  const out = [];
  for (const kind of Object.keys(examples.kinds)) {
    out.push(...examples.answers.filter((a) => a.kind === kind && a.paths.length && !a.declined).slice(0, 1));
  }
  return out.slice(0, 5);
}
