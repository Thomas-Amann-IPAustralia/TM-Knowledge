/* Ask the Manual — a question, the ideas it finds, the connections it follows,
   the passages it gathers, and a cited answer.

   Retrieval runs in the browser (engine.js, the same ranking Python measured,
   less the vectors). The answer comes from the model only when the site was
   built with live answers on; the 129 prepared answers always work. Every
   answer is stamped unreviewed, keeps the Manual and the legislation apart, and
   declines to say how an application would be decided. */

import { esc, fmt, load, kindColour, refChip, refLabel, md, isLaw, stampIcon, srcBadge } from "./app.js";
import { svg, curve, wrapText, wait } from "./graph.js";
import { Engine, Recogniser } from "./engine.js";
import { answer as callModel, cost } from "./live.js";

let engine = null;
let recogniser = null;

async function getEngine(status) {
  if (engine) return engine;
  status("Loading the Manual's text for searching…");
  const [search, passages] = await Promise.all([load("search"), load("passages")]);
  status("Indexing 2,460 passages…");
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
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const prepared = new Map(examples.answers.map((a) => [a.key, a]));
  let controller = null;

  const featured = pickFeatured(examples);
  root.innerHTML = `
  <div class="wrap wide">
    <div class="ask-top">
      <div>
        <h1 style="margin-bottom:.3rem">Ask the Manual</h1>
        <p class="lede">Ask in your own words. Watch the question find the ideas in it, follow their connections and gather passages —
        then read an answer that cites them, with the Manual and the legislation kept apart.</p>
      </div>
      <form class="ask-form">
        <textarea name="q" maxlength="600" rows="2" placeholder="e.g. Can I register a mark that includes someone's name without their consent?" aria-label="Your question"></textarea>
        <button class="btn primary" type="submit">Ask</button>
      </form>
      <div class="ask-meta">
        <span class="live-status"></span>
        <span class="load-status"></span>
      </div>
      <div>
        <p class="tiny" style="margin:.2rem 0 .4rem">Or open a prepared question — answered in advance, so it works without a live connection:</p>
        <div class="examples">${featured.map((a) => `<button type="button" class="chip" data-key="${esc(a.key)}">${esc(a.question)}</button>`).join("")}</div>
        <details style="margin-top:.6rem"><summary>All ${examples.answers.length} prepared questions</summary>
          ${Object.entries(examples.kinds).map(([kind, label]) => {
            const rows = examples.answers.filter((a) => a.kind === kind);
            return rows.length ? `<h4 style="margin:.8rem 0 .3rem;font-size:.85rem">${esc(label)} · ${rows.length}</h4><div class="examples">${rows.map((a) => `<button type="button" class="chip" data-key="${esc(a.key)}">${esc(a.question)}</button>`).join("")}</div>` : "";
          }).join("")}
        </details>
      </div>
    </div>
    <div class="result"></div>
  </div>`;

  const form = root.querySelector(".ask-form");
  const box = form.querySelector("textarea");
  const result = root.querySelector(".result");
  const loadStatus = (text) => { root.querySelector(".load-status").textContent = text; };

  function liveStatus() {
    const el = root.querySelector(".live-status");
    if (!live.enabled) {
      el.innerHTML = `Live answers are <b>off</b> on this copy of the site — your question will still show the ideas, connections and passages it finds.`;
      return;
    }
    const left = Math.max(0, chat.daily_limit - usedToday());
    el.innerHTML = `Live answers <b>on</b> · <code>${esc(chat.model)}</code> · ${left} of ${chat.daily_limit} questions left today in this browser`;
  }
  liveStatus();

  form.addEventListener("submit", (e) => { e.preventDefault(); askLive(box.value.trim()); });
  box.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
  root.querySelectorAll("[data-key]").forEach((b) => b.addEventListener("click", () => showPrepared(prepared.get(b.dataset.key))));

  // ------------------------------------------------------------ layout of a result

  function frame(question, subtitle) {
    result.innerHTML = `
      <div class="card hop-card">
        <div class="answer-head"><h3 style="margin:0">How the ontology worked on it</h3><span class="tiny">${esc(subtitle)} · click an idea to open it on the map, or a passage to read it</span></div>
        <div class="hop-body"><div class="hop-svg"></div><ol class="hop-steps"></ol></div>
      </div>
      <div class="ask-grid">
        <div class="card answer-card">
          <div class="answer-head"><h3 style="margin:0">Answer</h3><span class="answer-tags"></span></div>
          <p class="small muted" style="margin:-.3rem 0 .8rem"><b>Q.</b> ${esc(question)}</p>
          <div class="answer-body"></div>
        </div>
        <div class="compare"></div>
      </div>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
    return {
      hop: result.querySelector(".hop-svg"), steps: result.querySelector(".hop-steps"),
      compare: result.querySelector(".compare"), body: result.querySelector(".answer-body"), tags: result.querySelector(".answer-tags"),
    };
  }

  // ------------------------------------------------------------ live questions

  async function askLive(question) {
    if (question.length < 4) { box.focus(); return; }
    if (controller) controller.abort();
    controller = new AbortController();
    const signal = controller.signal;
    const eng = await getEngine(loadStatus);
    const prep = eng.prepare(question, chat);
    history.replaceState(null, "", "#/ask");
    const view = frame(question, "live");
    const linkedCount = prep.weight ? prep.weight.size : 0;
    const graph = {
      question,
      recognised: prep.trace.recognised.map((r) => ({ id: r.id, matched: question.slice(r.start, r.end), everyday: r.alias, generic: eng.generic.has(r.id) })),
      paths: prep.paths.map(([s, p, o, record, origin]) => ({ s, p, o, record, origin })),
      passages: prep.passages, legislation: prep.legislation, plain: prep.plain,
    };
    const steps = describe(graph, { linkedCount, live: true });
    renderCompare(view.compare, prep.plain, prep.passages, prep.hits);
    const canAnswer = live.enabled && usedToday() < chat.daily_limit;
    const animation = animate(view, graph, steps);
    if (!live.enabled) {
      await animation;
      view.body.innerHTML = `<p class="muted">Live answers are switched off on this copy of the site, so no answer is written. Everything on the left —
        the ideas recognised, the connections followed and the passages ranked — ran in your browser.</p>
        <p class="muted small">Try a prepared question above to see the answer the same pipeline wrote in advance.</p>`;
      return;
    }
    if (!canAnswer) {
      await animation;
      view.body.innerHTML = `<p class="muted">This browser has asked ${chat.daily_limit} live questions today, the courtesy limit. The prepared questions still work.</p>`;
      return;
    }
    view.body.innerHTML = `<div class="thinking"><span class="spinner"></span><span>Writing a cited answer from the ${prep.passages.length} passages${prep.legislation.length ? ` and ${prep.legislation.length} provisions` : ""}…</span></div>
      <p class="tiny">This usually takes 10 to 40 seconds.</p>`;
    countOne(); liveStatus();
    try {
      const reply = await callModel(live, chat, eng.prompt(prep, chat), signal);
      await animation;
      const checked = eng.verify(reply.parsed.citations, prep);
      showAnswer(view, {
        answer: reply.parsed.answer, citations: checked.kept, dropped: checked.dropped,
        declined: reply.parsed.declined, decline_reason: reply.parsed.decline_reason,
        model: reply.model, when: "just now", live: true, seconds: reply.seconds, cost: cost(reply.usage, chat.prices),
      });
    } catch (error) {
      if (signal.aborted) return;
      view.body.innerHTML = `<p class="err">No answer: ${esc(error.message)}.</p><p class="tiny">The passages on the left are still what the ontology found.</p>`;
    }
  }

  // ------------------------------------------------------------ prepared answers

  async function showPrepared(a) {
    if (!a) return;
    if (controller) controller.abort();
    box.value = a.question;
    const view = frame(a.question, "prepared in advance");
    let mentions = null, matched = new Map();
    try {
      const search = await load("search");
      mentions = search.mentions;
      recogniser = recogniser || new Recogniser(search);
      matched = new Map(recogniser.recognise(a.question).map((r) => [r.id, r]));
    } catch { /* drawn without passage links */ }
    const graph = {
      question: a.question,
      recognised: a.recognised.map((r) => {
        const m = matched.get(r.id);
        return { id: r.id, generic: !!byId.get(r.id)?.generic, matched: m ? a.question.slice(m.start, m.end) : null, everyday: !!m?.alias };
      }),
      paths: a.paths.map((p) => ({ s: p.subject, p: p.predicate, o: p.object, record: p.record, origin: p.origin })),
      passages: a.passages, legislation: a.legislation, plain: a.keyword10?.length ? a.keyword10 : a.plain, mentions,
    };
    renderCompare(view.compare, graph.plain, a.passages, null, true);
    const animation = animate(view, graph, describe(graph, { live: false }));
    await animation;
    showAnswer(view, { ...a, live: false, when: a.date });
  }

  // ------------------------------------------------------------ the hop diagram

  function describe(g, { linkedCount = 0, live }) {
    const rec = g.recognised.filter((r) => !r.generic);
    const generic = g.recognised.filter((r) => r.generic);
    const neighbours = new Set(g.paths.map((p) => (rec.some((r) => r.id === p.s) ? p.o : p.s)));
    const plainSet = new Set((g.plain || []).slice(0, 10));
    const beyond = g.passages.filter((r) => !plainSet.has(r)).length;
    const name = (r) => `<b>${esc(byId.get(r.id)?.label || r.id)}</b>${r.matched && r.matched.toLowerCase() !== (byId.get(r.id)?.label || "").toLowerCase() ? ` <span class="muted">(“${esc(r.matched)}”${r.everyday ? ", an everyday phrasing" : ""})</span>` : ""}`;
    return [
      rec.length ? `Recognised ${rec.length} idea${rec.length > 1 ? "s" : ""} in the question: ${rec.slice(0, 5).map(name).join(", ")}${rec.length > 5 ? "…" : ""}.${generic.length ? ` <span class="muted">(<i>${generic.map((r) => esc(byId.get(r.id)?.label)).join("</i>, <i>")}</i> ${generic.length > 1 ? "are" : "is"} named so often it is not used to steer.)</span>` : ""}`
        : `Recognised no specific idea in the question, so this is plain keyword search.`,
      g.paths.length ? `Followed ${g.paths.length} connection${g.paths.length > 1 ? "s" : ""} to ${neighbours.size} related idea${neighbours.size === 1 ? "" : "s"}.` : `No connections to follow.`,
      live ? `Gathered ${fmt(linkedCount)} passages linked to those ideas${g.legislation.length ? `, and ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""} of the legislation` : ""}.`
        : `Gathered the passages linked to those ideas${g.legislation.length ? `, and ${g.legislation.length} provision${g.legislation.length > 1 ? "s" : ""} of the legislation` : ""}.`,
      `Ranked them with the question's own words${live ? "" : " and meaning"}: ${g.passages.length} passages for the answer${g.plain?.length ? ` — ${beyond} of them outside plain keyword search's top ${Math.min(10, g.plain.length)}` : ""}.`,
      live ? `Wrote an answer citing only those passages, each quote checked against the text.` : `Shows the answer written from them in advance.`,
    ];
  }

  async function animate(view, g, steps) {
    view.steps.innerHTML = steps.map((s) => `<li><span>${s}</span></li>`).join("");
    const items = [...view.steps.children];
    const Wd = 1000, Ht = 540;
    const pic = svg("svg", { viewBox: `0 0 ${Wd} ${Ht}`, role: "img", "aria-label": "How the question was answered: ideas, connections, passages" });
    view.hop.appendChild(pic);
    const defs = svg("defs", {}, pic);
    const m = svg("marker", { id: "harrow", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto" }, defs);
    svg("path", { d: "M0,0 L10,5 L0,10 z", class: "arrowhead" }, m);
    const lines = svg("g", {}, pic), nodes = svg("g", {}, pic);
    const cols = { q: 95, rec: 330, nb: 590, psg: 830 };
    ["Your question", "Ideas recognised", "Connected ideas", "Passages found"].forEach((t, i) =>
      svg("text", { x: [cols.q, cols.rec, cols.nb, cols.psg][i], y: 18, "text-anchor": "middle", class: "family-label" }, pic).textContent = t);
    pic.classList.add("hop");

    // 1. question
    const qText = wrapText(g.question || "", 20, 8);
    const qg = svg("g", { opacity: 0 }, nodes);
    svg("rect", { x: cols.q - 92, y: Ht / 2 - 20 - qText.length * 9, width: 184, height: 26 + qText.length * 18, rx: 12, fill: "var(--panel-2)", stroke: "var(--line)" }, qg);
    qText.forEach((line, i) => svg("text", { x: cols.q, y: Ht / 2 - qText.length * 9 + 4 + i * 18, "text-anchor": "middle", style: "font-size:13.5px;fill:var(--ink)" }, qg).textContent = line);
    const qAnchor = { x: cols.q + 92, y: Ht / 2 };

    // 2. recognised ideas
    const rec = g.recognised.slice(0, 7);
    const recAt = new Map(rec.map((r, i) => [r.id, { x: cols.rec, y: spread(i, rec.length, 60, Ht - 40) }]));
    // 3. neighbours (at most 8)
    const recIds = new Set(rec.map((r) => r.id));
    const nbIds = [];
    for (const p of g.paths) {
      const other = recIds.has(p.s) ? p.o : p.s;
      if (!recIds.has(other) && !nbIds.includes(other)) nbIds.push(other);
    }
    const nbShown = nbIds.slice(0, 8);
    const nbAt = new Map(nbShown.map((id, i) => [id, { x: cols.nb, y: spread(i, nbShown.length, 60, Ht - 40) }]));
    // 4. passages and provisions
    const plainSet = new Set((g.plain || []).slice(0, 10));
    const all = [...g.passages, ...g.legislation];
    const psAt = new Map(all.map((ref, i) => [ref, { x: cols.psg, y: spread(i, all.length, 50, Ht - 20) }]));

    const ideaNode = (id, at, extra) => {
      const concept = byId.get(id);
      const gg = svg("g", { class: `node ${concept?.origin || "machine"}`, style: `--c:${kindColour(concept?.kind)}`, transform: `translate(${at.x},${at.y})`, opacity: 0 }, nodes);
      svg("circle", { r: 9, class: "body" }, gg);
      svg("text", { x: 14, y: 4, style: extra?.generic ? "fill:var(--ink-3)" : "" }, gg).textContent = (concept?.label || id).slice(0, 30);
      if (extra?.matched && extra.matched.toLowerCase() !== (concept?.label || "").toLowerCase()) svg("text", { x: 14, y: 17, style: "font-size:11.5px;fill:var(--ink-3)" }, gg).textContent = `“${extra.matched}”`;
      if (extra?.generic) gg.style.filter = "grayscale(1)";
      gg.addEventListener("click", () => { location.hash = `#/map/ideas/${id}`; });
      svg("title", {}, gg).textContent = `${concept?.label} — open on the map`;
      return gg;
    };

    // draw everything hidden, then reveal in order
    const recEls = rec.map((r) => {
      const at = recAt.get(r.id);
      const line = svg("path", { d: curve(qAnchor, at, 0, 11, 0.05).d, class: "edge", opacity: 0, "stroke-dasharray": r.generic ? "2 3" : null }, lines);
      return [line, ideaNode(r.id, at, r)];
    });
    const pathEls = [];
    for (const p of g.paths) {
      const a = recAt.get(p.s) || nbAt.get(p.s), b = recAt.get(p.o) || nbAt.get(p.o);
      if (!a || !b || (recAt.has(p.s) && recAt.has(p.o) && false)) continue;
      const cv = curve(a, b, 11, 13, recAt.has(p.s) && recAt.has(p.o) ? 0.4 : 0.06);
      const path = svg("path", { d: cv.d, class: `edge ${p.origin === "approved" || p.origin === "signed" ? "signed" : "machine"}`, opacity: 0, "marker-end": "url(#harrow)", "stroke-width": 1.4 }, lines);
      const label = svg("text", { x: cv.mx, y: cv.my - 3, class: "edge-label", "text-anchor": "middle", opacity: 0 }, lines);
      label.textContent = ontology.predicates[p.p]?.label || p.p;
      pathEls.push(path, label);
    }
    const nbEls = nbShown.map((id) => ideaNode(id, nbAt.get(id)));
    if (nbIds.length > nbShown.length) svg("text", { x: cols.nb, y: Ht - 8, "text-anchor": "middle", style: "font-size:12px;fill:var(--ink-3)" }, nodes).textContent = `+ ${nbIds.length - nbShown.length} more`;
    const mentionSets = new Map();
    const mentions = g.mentions || engine?.s.mentions || {};
    const generic = new Set(rec.filter((r) => r.generic).map((r) => r.id));
    for (const id of [...recAt.keys(), ...nbAt.keys()]) if (!generic.has(id)) mentionSets.set(id, new Set(mentions[id] || []));
    const psEls = [];
    const linkEls = [];
    all.forEach((ref, i) => {
      const at = psAt.get(ref);
      const law = isLaw(ref);
      const viaWords = plainSet.has(ref);
      const gg = svg("g", { class: `psg ${law ? "law" : "manual"}${!law && !viaWords ? " found" : ""}`, transform: `translate(${at.x},${at.y})`, opacity: 0, "data-ref": ref }, nodes);
      if (law) svg("path", { d: "M0,-8 L8,0 L0,8 L-8,0 Z", "stroke-width": 1.2 }, gg);
      else svg("rect", { x: -7, y: -7, width: 14, height: 14, rx: 2, "stroke-width": 1.2 }, gg);
      svg("text", { x: 14, y: 4, style: "font-size:12.5px;fill:var(--ink)" }, gg).textContent = `${law ? "" : `${i + 1}. `}${refLabel(ref)}`.slice(0, 26);
      svg("title", {}, gg).textContent = `${refLabel(ref)} — ${law ? "legislation" : viaWords ? "also in plain keyword search's top ten" : "not in plain keyword search's top ten"}. Click to read.`;
      psEls.push(gg);
      // Link a passage to at most two of the ideas it names, recognised ideas first,
      // so the picture shows which hop brought it in without becoming a hairball.
      let linked = false;
      const namers = [...mentionSets.entries()].filter(([, set]) => set.has(ref)).map(([id]) => id)
        .sort((a, b) => (recAt.has(b) - recAt.has(a))).slice(0, 2);
      for (const id of namers) {
        const from = recAt.get(id) || nbAt.get(id);
        linkEls.push(svg("path", { d: curve(from, at, 10, 10, 0.03).d, class: "edge", opacity: 0, "stroke-opacity": 0.32 }, lines));
        linked = true;
      }
      if (!linked && !law) linkEls.push(svg("path", { d: curve(qAnchor, at, 0, 10, -0.12).d, class: "edge machine", opacity: 0, "stroke-opacity": 0.22 }, lines));
    });

    const show = (els) => els.forEach((e) => { e.style.transition = "opacity .45s"; e.setAttribute("opacity", 1); });
    show([qg]);
    await wait(350); items[0]?.classList.add("on"); show(recEls.flat());
    await wait(750); items[1]?.classList.add("on"); show([...pathEls, ...nbEls]);
    await wait(850); items[2]?.classList.add("on"); show(linkEls);
    await wait(700); items[3]?.classList.add("on"); show(psEls);
    await wait(500); items[4]?.classList.add("on");
  }

  function renderCompare(target, plain, guided, hits, prepared = false) {
    const plainTop = (plain || []).slice(0, 10);
    const plainSet = new Set(plainTop);
    const why = new Map((hits || []).map((h) => [h.ref, h.why]));
    target.innerHTML = `
      <div class="card"><h4>Plain keyword search</h4><span class="tiny">top ${plainTop.length}, words only</span>
        <ol>${plainTop.map((ref) => `<li>${refChip(ref)}</li>`).join("") || `<li class="empty">Nothing matched.</li>`}</ol></div>
      <div class="card"><h4>Guided by the ontology</h4><span class="tiny">the ${guided.length} passages the answer was written from</span>
        <ol>${guided.map((ref) => {
          const only = !plainSet.has(ref);
          const w = why.get(ref) || [];
          // Live, the only rankings are keyword, expanded and linked, so a passage outside
          // keyword's top ten came through the ontology. A prepared answer's search also
          // used meaning-vectors, so all that can be said is that keyword search missed it.
          const tag = !only ? "" : prepared
            ? `<span class="via" title="Not in plain keyword search's top ten. The prepared search also used meaning-vectors, so this may have come from them or from the ontology.">beyond keyword top 10</span>`
            : `<span class="via" title="${esc("reached by: " + w.join(", "))}">via the ontology</span>`;
          return `<li class="${only ? "only" : ""}">${refChip(ref)}${tag}</li>`;
        }).join("")}</ol></div>`;
  }

  // ------------------------------------------------------------ the answer

  function showAnswer(view, a) {
    const cites = a.citations || [];
    const manual = cites.filter((x) => !isLaw(x.ref)).length, law = cites.length - manual;
    view.tags.innerHTML = `<span class="trust machine">Machine · unreviewed</span>`;
    view.body.innerHTML = `
      ${a.declined ? `<div class="stamp" style="margin-bottom:.8rem">${stampIcon}<span><b>Part of this question asked how an application would be decided, and the answer declines that part.</b>${a.decline_reason ? " " + esc(a.decline_reason) : ""}</span></div>` : ""}
      <div class="answer">${md(a.answer)}</div>
      <div class="cites">
        <h4 style="margin:.8rem 0 .2rem;font-size:.85rem">Citations · ${cites.length} <span class="tiny">(${manual} Manual · ${law} legislation) — each quote found word for word in the passage</span></h4>
        <ul>${cites.map((x) => `<li>${srcBadge(x.ref)} ${refChip(x.ref)} <span class="muted">“${esc(String(x.quote || "").slice(0, 220))}${String(x.quote || "").length > 220 ? "…" : ""}”</span></li>`).join("")}</ul>
        ${a.dropped?.length ? `<p class="tiny" style="margin-top:.4rem">${a.dropped.length} citation${a.dropped.length > 1 ? "s" : ""} the model gave could not be found word for word in the passage, and ${a.dropped.length > 1 ? "were" : "was"} removed.</p>` : ""}
      </div>
      <div class="stamp" style="margin-top:1rem">${stampIcon}<span>Written by a machine (<code>${esc(a.model || "")}</code>${a.live ? "" : `, ${esc(a.when || "")}`}) from the passages shown, and not reviewed by a trade marks expert.
        The Manual states the Registrar's practice; it is not law. This is not advice and not an examination decision.</span></div>
      <p class="tiny" style="margin-top:.5rem">${a.live ? `Live answer · ${a.seconds ? a.seconds.toFixed(0) + " s" : ""}${a.cost != null ? ` · about US${(a.cost * 100).toFixed(1)}¢` : ""} · ${esc(chat.effort)} reasoning effort (the prepared answers used ${esc(chat.measured_effort)}) · search ran without the meaning-vectors the measured system also used.`
        : `Prepared answer, written ${esc(a.when || "")} with ${esc(chat.measured_effort)} reasoning effort by the same pipeline.`}</p>`;
  }

  if (params[0] && prepared.has(params[0])) showPrepared(prepared.get(params[0]));
}

function spread(i, n, top, bottom) {
  if (n <= 1) return (top + bottom) / 2;
  const gap = Math.min(64, (bottom - top) / (n - 1));
  const mid = (top + bottom) / 2;
  return mid + (i - (n - 1) / 2) * gap;
}

function pickFeatured(examples) {
  // Two of each kind that have a connection to draw, in id order — not chosen by
  // how well the ontology did on them.
  const out = [];
  for (const kind of Object.keys(examples.kinds)) {
    out.push(...examples.answers.filter((a) => a.kind === kind && a.paths.length && !a.declined).slice(0, kind === "signed" ? 1 : 2));
  }
  return out.slice(0, 8);
}
