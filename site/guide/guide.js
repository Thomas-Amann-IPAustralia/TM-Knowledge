/* The trade marks guide: a conversation for the public about trade marks (ADR-0154, on the
   owner's word, CHAT-0103).

   One turn, live: the model reads the person's words against the map (the examiner page's
   reading, ADR-0132); the browser's search (`engine.js`, the same as Ask a research question's)
   gathers the Manual passages and the provisions; the guide's prompt (`chat.json`'s `guide`,
   written by `tm_knowledge.explain.guide`) asks for a short, friendly reply in points, each with
   the words it rests on, and at most one clarifying question, one picture and a few follow-ups.
   Every quote is checked against what the model was sent (`Engine.verify`); a point with none is
   counted under the reply and marked in the detail. Calls go through the proxy that holds the key
   (`live-proxy/`), as the examiner's do.

   The screen holds the conversation and nothing else: who wrote a reply is said under it in one
   line, and its sources, the checks and the texts it read open only when the reader asks
   ("Where this comes from"). A clarifying question offers its answers as buttons, in the manner
   of the invented Corner Brew case (FM-0006): ask only for a fact that changes the explanation,
   never guess the ground, never ask for personal details.

   With live answers off (no proxy, the day's limit reached, or an error), the guide still walks
   through four guided topics drawn from `explain.json`, the clarifying question included; the
   page's own words there say what to look at and state no law.

   Never: an outcome, a date worked out, a "may" made a "must", or an answer without its stamp. */

import { Engine, authorityFlags, pathLine, sourceName, locate } from "../js/engine.js";
import { guide as askGuide, read as readModel, cost, partialFields, viaProxy, wake } from "../js/live.js";
import * as lib from "../js/lib.js";
import { esc, isLaw, sourceOf, SOURCE, mark, refLabel, refButton, headingOf, clip, ICON } from "./common.js";
import { journey, requirements, options, ruleName, sourcesOf } from "./visuals.js";

const cache = new Map();
const data = (name) => {
  if (!cache.has(name)) {
    cache.set(name, fetch(`../data/${name}.json`).then((r) => {
      if (!r.ok) throw new Error(`data/${name}.json: ${r.status}`);
      return r.json();
    }));
  }
  return cache.get(name);
};

const $ = (sel) => document.querySelector(sel);
const thread = $(".gd-thread");
const form = $(".gd-form");
const box = $("#gd-box");
const chips = $(".gd-chips");
const sendBtn = $(".gd-send");
const newBtn = $(".gd-new");

const todayKey = () => `tmk-guide-${new Date().toISOString().slice(0, 10)}`;
const usedToday = () => { try { return Number(localStorage.getItem(todayKey()) || 0); } catch { return 0; } };
const countOne = () => { try { localStorage.setItem(todayKey(), String(usedToday() + 1)); } catch { /* storage blocked */ } };

/** What the conversation has said, for the model and for the search. */
let turns = [];
let busy = false;
let controller = null;
let engine = null;
let chat, live, explained, journeys, rules, objection;
/** Each reply's bubble → what builds its "Where this comes from". */
const renderers = new WeakMap();

const AUTH = {
  legislation: ["law", "The law"], manual: ["practice", "IP Australia’s guidance"], both: ["both", "The law and the guidance"], none: ["", ""],
};

// ------------------------------------------------------------------ start

async function start() {
  try {
    [chat, live, explained] = await Promise.all([data("chat"), data("live").catch(() => ({ enabled: false })), data("explain")]);
  } catch (error) {
    thread.innerHTML = `<p class="gd-err">The guide could not load its data (${esc(error.message)}).</p>`;
    return;
  }
  wake(live);
  journeys = new Map(explained.walkthroughs.map((w) => [w.process, w]));
  rules = new Map(explained.requirements.map((r) => [r.test, r]));
  // The invented case whose objection is known only from the customer's words (A12).
  objection = explained.matters.map((m) => m.issues.find((i) => i.test === null && i.candidates)).find(Boolean) || null;
  hello();
}

const STARTERS = [
  { icon: "route", text: "How does applying for a trade mark work?", sub: "From filing to registration", topic: "journey" },
  { icon: "scale", text: "What does the examiner check?", sub: "The questions an application is examined against", topic: "checks" },
  { icon: "letter", text: "I got an objection saying my name is too close to what other people already use. What does that mean?", sub: "An objection, in your words", topic: "objection" },
  { icon: "flag", text: "What happens after my application is accepted?", sub: "Publication, opposition and registration", topic: "after" },
];

function liveOn() { return !!live?.enabled && !!chat?.guide && usedToday() < chat.daily_limit; }

function hello() {
  turns = [];
  shown.clear();
  newBtn.hidden = true;
  chips.innerHTML = "";
  const mode = !live.enabled ? `<p class="gd-mode"><i></i>Live answers are off on this copy, so I can walk you through the guided topics below, but not answer typed questions.</p>`
    : usedToday() >= chat.daily_limit ? `<p class="gd-mode"><i></i>You’ve reached today’s limit of ${chat.daily_limit} questions in this browser. The guided topics below still work.</p>`
    : `<p class="gd-mode on"><i></i>Live answers on · ${chat.daily_limit - usedToday()} of ${chat.daily_limit} questions left today in this browser</p>`;
  thread.innerHTML = `<section class="gd-hello">
      <h1>Hi! Let’s make sense of trade marks.</h1>
      <p class="gd-lede">Ask me about applying for a trade mark in Australia: what the examiner checks, what happens after you apply, or what an objection in your examination report means. I’ll keep it simple, and you can always see where each answer comes from.</p>
      <div class="gd-starters">${STARTERS.map((s, i) => `<button type="button" class="gd-starter" data-starter="${i}">${ICON[s.icon]}<span><b>${esc(s.text)}</b><span>${esc(s.sub)}</span></span></button>`).join("")}</div>
      ${mode}
    </section>`;
}

// ------------------------------------------------------------------ the thread

function hideHello() {
  thread.querySelector(".gd-hello")?.remove();
  newBtn.hidden = false;
}

function drawMe(text) {
  const el = document.createElement("div");
  el.className = "gd-msg me";
  el.innerHTML = `<div class="gd-me">${esc(text)}</div>`;
  thread.appendChild(el);
}

function drawBot() {
  const el = document.createElement("div");
  el.className = "gd-msg bot";
  el.innerHTML = `<span class="gd-av">${ICON.bubble}</span><div class="gd-bot">
      <div class="gd-typing"><span class="gd-dots"><i></i><i></i><i></i></span><span class="gd-status">Reading your question…</span></div>
      <div class="gd-say"></div><div class="gd-extra"></div><div class="gd-foot" hidden></div><div class="gd-why" hidden></div></div>`;
  thread.appendChild(el);
  scrollDown();
  const bot = {
    el, say: el.querySelector(".gd-say"), extra: el.querySelector(".gd-extra"), foot: el.querySelector(".gd-foot"),
    why: el.querySelector(".gd-why"), typing: el.querySelector(".gd-typing"), render: null,
    status: (t) => { const s = el.querySelector(".gd-status"); if (s) s.textContent = t; },
  };
  // The detail is built when first opened, from what the reply kept (`toggleWhy`).
  renderers.set(el.querySelector(".gd-bot"), () => (bot.render ? bot.render() : ""));
  return bot;
}

function scrollDown() {
  requestAnimationFrame(() => window.scrollTo({ top: document.body.scrollHeight, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }));
}

function setChips(list) {
  chips.innerHTML = list.map((c) => `<button type="button" class="gd-chip" data-send="${esc(c.text)}"${c.topic ? ` data-topic="${esc(c.topic)}"` : ""}>${esc(c.text)}</button>`).join("");
}

/** Model-written text, sanitised, with any stray bracketed ref removed (the sources are shown
    apart, on request). */
async function prose(text) {
  const md = await lib.markdown();
  return md(String(text || "").replace(/\s*\[(?:TMM|TMA1995|TMR1995)\/[^\]\n]*\]/g, ""));
}

// ------------------------------------------------------------------ a turn

async function send(text, { topic = null } = {}) {
  text = String(text || "").trim();
  if (text.length < 2 || busy) return;
  hideHello();
  chips.innerHTML = "";
  box.value = "";
  grow();
  // Answering a clarifying question: the earlier buttons are spent.
  thread.querySelectorAll(".gd-opt, .gd-card").forEach((b) => { b.disabled = true; if (b.dataset.send === text) b.classList.add("picked"); });
  const query = searchQuery(text);
  const history = historyLines();
  turns.push({ role: "me", text });
  drawMe(text);
  const bot = drawBot();
  busy = true;
  sendBtn.disabled = true;
  try {
    if (topic || !liveOn()) await guided(text, topic, bot);
    else await answer(text, query, history, bot);
  } finally {
    busy = false;
    sendBtn.disabled = false;
    scrollDown();
  }
}

/** The words the search reads: the newest message, with the question it answers if it answers
    one, and the person's two messages before it while they fit. */
function searchQuery(latest) {
  const last = [...turns].reverse().find((t) => t.role === "guide");
  let q = last?.clarify?.ask ? `${last.clarify.question} ${latest}` : latest;
  for (const said of turns.filter((t) => t.role === "me").slice(-2).reverse()) {
    if (said.text.length + q.length + 1 > 600) break;
    q = `${said.text}\n${q}`;
  }
  return q;
}

const defang = (s) => String(s).replaceAll("<passage", "&lt;passage").replaceAll("</passage", "&lt;/passage");

/** The conversation so far, oldest first, for the prompt: the person's words, and the guide's
    replies shortened, with any question it asked and its options. */
function historyLines() {
  const g = chat?.guide;
  if (!g) return [];
  return turns.slice(-g.history_turns).map((t) => (t.role === "me"
    ? `Person: ${defang(clip(t.text, g.history_chars))}`
    : `Guide: ${defang(clip(t.plain || "", g.history_chars))}${t.clarify?.ask ? ` (asked: ${defang(t.clarify.question)} Options: ${t.clarify.options.map((o) => defang(o.label)).join(" | ")})` : ""}`));
}

async function getEngine(bot) {
  if (engine) return engine;
  bot.status("Opening IP Australia’s guidance and the law…");
  const [search, passages] = await Promise.all([data("search"), data("passages")]);
  await new Promise((r) => setTimeout(r, 20));
  engine = new Engine(search, passages);
  return engine;
}

/** The guide's input: the examiner answer's blocks, in the same shapes, with the pictures it may
    ask for after the map and the conversation before the passages. */
function guideInput(eng, prep, history, latest) {
  const label = (c) => eng.s.concepts[c]?.pref || c;
  const sent = eng.excerpts(prep, chat);
  const block = (ref) => {
    const { text, cut } = sent.get(ref);
    return `<passage source="${sourceName(ref)}" ref="${ref}"${cut ? ` cut="${cut}"` : ""}>\n${defang(text)}\n</passage>`;
  };
  const lines = ["ONTOLOGY (one line per concept):", chat.ontology_map, "", "VISUALS YOU CAN SHOW:", chat.guide.visuals, "",
    "CONCEPTS RECOGNISED IN THE CONVERSATION: " + (prep.trace.ids.map((c) => `${c} ${label(c)}`).join(", ") || "none")];
  const defined = prep.trace.ids.filter((c) => chat.definitions?.[c]).map((c) => chat.definitions[c]);
  if (defined.length) lines.push("", "DEFINITIONS (of the concepts recognised; machine-written, unreviewed):", ...defined);
  if (prep.paths.length) {
    lines.push("", "GRAPH PATH (relationships the ontology holds for those concepts):");
    for (const edge of prep.paths) lines.push(pathLine(label, edge));
  }
  lines.push("", "CONVERSATION SO FAR (oldest first; earlier replies shortened):", ...(history.length ? history : ["(none: this is the first message)"]));
  lines.push("", `LATEST MESSAGE: ${defang(latest)}`, "", "MANUAL PASSAGES:");
  for (const ref of prep.passages) if (sent.has(ref)) lines.push(block(ref));
  if (prep.legislation.length) {
    lines.push("", "LEGISLATION:");
    for (const ref of prep.legislation) if (sent.has(ref)) lines.push(block(ref));
  }
  return lines.join("\n");
}

async function answer(text, query, history, bot) {
  controller?.abort();
  controller = new AbortController();
  const signal = controller.signal;
  countOne();
  const started = performance.now();
  const reading = chat.reading ? readModel(live, chat, query, signal).then((reply) => ({ reply }), (error) => ({ error })) : Promise.resolve(null);
  let sleepy = viaProxy(live) ? setTimeout(() => bot.status("Waking the answer service. This can take up to a minute…"), 10000) : null;
  try {
    const eng = await getEngine(bot);
    if (signal.aborted) return;
    bot.status("Reading your question…");
    const outcome = await reading;
    if (signal.aborted) return;
    const read = outcome?.reply ? { ...eng.reading(query, outcome.reply.parsed, chat.reading.max_ideas), model: outcome.reply.model, cost: cost(outcome.reply.usage, chat.prices) } : null;
    const prep = eng.prepare(query, chat, read?.kept || []);
    bot.status(`Looking through ${prep.passages.length} passages of guidance${prep.legislation.length ? ` and ${prep.legislation.length} of the law` : ""}…`);
    let lastPaint = 0, painting = false;
    const onText = async (json) => {
      clearTimeout(sleepy);
      const now = performance.now();
      if (painting || now - lastPaint < 140) return;
      painting = true; lastPaint = now;
      const sofar = partialFields(json, "text").filter(Boolean);
      if (sofar.length) {
        bot.typing.hidden = true;
        bot.say.classList.add("streaming");
        bot.say.innerHTML = await prose(sofar.join("\n\n"));
        scrollDown();
      } else bot.status("Writing a reply…");
      painting = false;
    };
    const reply = await askGuide(live, chat, guideInput(eng, prep, history, text), signal, onText);
    clearTimeout(sleepy);
    const parsed = reply.parsed || {};
    const claims = eng.verify(parsed.reply, prep, chat);
    const spent = cost(reply.usage, chat.prices);
    const result = {
      claims, prep, read, parsed, model: reply.model, seconds: (performance.now() - started) / 1000,
      cost: spent == null ? null : spent + (read?.cost || 0),
      clarify: cleanClarify(parsed.clarify), visual: cleanVisual(parsed.visual),
      followUps: (Array.isArray(parsed.follow_ups) ? parsed.follow_ups : []).map((s) => String(s).trim()).filter((s) => s.length > 3).slice(0, 3),
    };
    await drawReply(bot, result);
  } catch (error) {
    clearTimeout(sleepy);
    if (signal.aborted) return;
    bot.typing.hidden = true;
    bot.say.classList.remove("streaming");
    bot.say.innerHTML = `<p class="gd-err">Sorry, I couldn’t get an answer just now: ${esc(String(error.message || error).replace(/,? or choose a saved example/i, "").replace(/\.+$/, ""))}.</p><p>You can try again, or pick a guided topic below.</p>`;
    turns.push({ role: "guide", plain: "(no answer: an error)" });
    setChips(STARTERS.map((s) => ({ text: s.text, topic: s.topic })));
  }
}

/** A clarifying question as the page will show it: asked, worded, with two to four options. */
function cleanClarify(c) {
  if (!c?.ask || !String(c.question || "").trim()) return { ask: false, question: "", why: "", options: [] };
  const opts = (Array.isArray(c.options) ? c.options : []).map((o) => ({ label: String(o?.label || "").trim(), rule: String(o?.rule || "").trim() }))
    .filter((o) => o.label).slice(0, 4);
  return { ask: true, question: String(c.question).trim(), why: String(c.why || "").trim(), options: opts };
}

/** A picture the page can draw: a listed journey and one of its steps, or a listed rule. */
function cleanVisual(v) {
  if (v?.kind === "journey" && journeys.has(v.id)) {
    const w = journeys.get(v.id);
    return { kind: "journey", id: v.id, focus: w.steps.some((s) => s.id === v.focus) ? v.focus : "" };
  }
  if (v?.kind === "requirements" && rules.has(v.id)) return { kind: "requirements", id: v.id };
  return null;
}

/** Pictures already drawn in this conversation, so the same one is offered again folded rather
    than repeated in full. */
const shown = new Set();
function drawVisual(v) {
  if (!v) return "";
  const html = v.kind === "journey" ? journey(journeys.get(v.id), v.focus) : requirements(rules.get(v.id));
  const key = `${v.kind}:${v.id}:${v.focus || ""}`;
  if (shown.has(key)) {
    const name = v.kind === "journey" ? "the journey" : `what the examiner looks at under ${ruleName(rules.get(v.id)).split(" · ")[0].toLowerCase()}`;
    return `<details class="gd-again"><summary>Show ${esc(name)} again</summary>${html}</details>`;
  }
  shown.add(key);
  return html;
}

function drawClarify(c) {
  if (!c?.ask) return "";
  return `<div class="gd-ask" role="group" aria-label="A question for you">
    <span class="gd-ask-k">So I can explain the right thing</span>
    <p class="gd-ask-q">${esc(c.question)}</p>
    ${options([...c.options, ...(c.extra || [])], rules)}
    ${c.why ? `<p class="gd-ask-why">Why I’m asking: ${esc(c.why)}</p>` : ""}
  </div>`;
}

async function drawReply(bot, r) {
  bot.typing.hidden = true;
  bot.say.classList.remove("streaming");
  const parsed = r.parsed;
  const plain = r.claims.map((c) => c.text).filter(Boolean).join("\n\n");
  bot.say.innerHTML = `${parsed.declined ? `<div class="gd-declined">${ICON.info}<span>I can’t say how an application will turn out: only the Registrar decides that.${parsed.decline_reason ? ` ${esc(parsed.decline_reason)}` : ""}</span></div>` : ""}${await prose(plain)}`;
  bot.extra.innerHTML = drawVisual(r.visual) + drawClarify(r.clarify);
  const unsupported = r.claims.filter((c) => c.authority !== "none" && !c.supported).length;
  bot.foot.hidden = false;
  bot.foot.innerHTML = `<span class="gd-stamp"><i></i>Written by AI · not reviewed by an expert</span>
    <button type="button" class="gd-why-btn" aria-expanded="false">Where this comes from</button>
    ${unsupported ? `<span class="gd-warn">${unsupported} point${unsupported > 1 ? "s" : ""} without a matching source</span>` : ""}`;
  bot.render = () => whyPanel(r);
  turns.push({ role: "guide", plain, clarify: r.clarify });
  if (!r.clarify.ask) setChips(r.followUps.map((t) => ({ text: t })));
}

// ------------------------------------------------------------------ where this comes from

function whyPanel(r) {
  const { claims, prep } = r;
  const cited = claims.flatMap((c) => c.quotes.map((q) => q.ref));
  const flags = authorityFlags(claims.map((c) => c.text).join("\n\n"), cited);
  const point = (c, i) => {
    const [cls, word] = AUTH[c.authority] || AUTH.none;
    const lawOnly = c.quotes.length && c.quotes.every((q) => isLaw(q.ref));
    const manualOnly = c.quotes.length && !c.quotes.some((q) => isLaw(q.ref));
    const mismatch = c.authority === "legislation" && manualOnly ? "This point is about the law, but its words come only from IP Australia’s guidance."
      : c.authority === "manual" && lawOnly ? "This point is about IP Australia’s guidance, but its words come only from the law." : "";
    const badge = c.authority === "none" ? "" : c.supported ? `<span class="gd-auth ${cls}">${esc(word)}</span>` : `<span class="gd-auth unsup">No matching source</span>`;
    return `<li class="gd-pt${c.authority === "none" ? " none" : ""}"><span class="gd-pt-n">${i + 1}</span><div>
      <div class="gd-pt-t">${badge}${esc(c.text.replace(/\*\*|__|`/g, ""))}</div>
      ${c.quotes.map((q) => `<button type="button" class="gd-quote ${sourceOf(q.ref)}" data-ref="${esc(q.ref)}" data-quote="${esc(q.quote)}"><small>${mark(q.ref)}${esc(refLabel(q.ref))} · ${esc(SOURCE[sourceOf(q.ref)].role)}</small>“${esc(clip(q.quote, 300))}”</button>`).join("")}
      ${c.authority !== "none" && !c.supported ? `<p class="gd-note warn">The AI gave no words for this point that could be found in what it read. Treat it with care.</p>` : ""}
      ${mismatch ? `<p class="gd-note warn">${esc(mismatch)}</p>` : ""}
      ${c.dropped.length ? `<p class="gd-note">${c.dropped.length} quote${c.dropped.length > 1 ? "s" : ""} the AI gave could not be found word for word, and ${c.dropped.length > 1 ? "were" : "was"} left out.</p>` : ""}
    </div></li>`;
  };
  const recognised = prep.trace.recognised.filter((x) => !engine.generic.has(x.id));
  const law = [...(chat.law || []).map((l) => l.line), chat.manual?.line].filter(Boolean).join("; ");
  const all = [...prep.legislation, ...prep.passages];
  return `<h3>Each point, and the words it rests on</h3>
    <ol class="gd-pts">${claims.map(point).join("")}</ol>
    ${flags.length ? `<p class="gd-note warn">Law or guidance? ${esc(flags[0].message)}</p>` : ""}
    <p class="gd-note">A matching quote shows where the words come from. It doesn’t prove the point is right, so open the source to read it in context.</p>
    <h3>What I read</h3>
    <div class="gd-srcs">${all.map((ref) => `<button type="button" class="gd-src ${sourceOf(ref)}" data-ref="${esc(ref)}" data-title="${esc(ref)}">${mark(ref)}${esc(refLabel(ref))}</button>`).join("") || "<span class=\"gd-note\">Nothing matched.</span>"}</div>
    <p class="gd-note">${mark("TMA1995/")} the law (the Act) · ${mark("TMR1995/")} the law (the Regulations) · ${mark("TMM/")} IP Australia’s guidance, which explains how the law is applied and is not law</p>
    ${recognised.length ? `<h3>Ideas I recognised</h3><p>${recognised.map((x) => `${esc(engine.s.concepts[x.id]?.pref || x.id)}${x.read ? ` <span class="gd-note">(read from “${esc(x.label)}”)</span>` : ""}`).join(", ")}</p>` : ""}
    <h3>About this answer</h3>
    <dl class="gd-kv">
      <dt>Written by</dt><dd>AI (<code>${esc(r.model || chat.model)}</code>), from the passages above. No trade marks expert has reviewed it.</dd>
      <dt>Texts read</dt><dd>${esc(law)}</dd>
      <dt>The guide</dt><dd>${esc(chat.guide.prompt_version)}, a prototype not yet measured against test questions</dd>
      <dt>Time</dt><dd>${r.seconds.toFixed(0)} seconds${r.cost != null ? ` · about US${(r.cost * 100).toFixed(1)}¢` : ""}</dd>
    </dl>
    <h3>Keep in mind</h3>
    <ul class="gd-mind">
      <li>The Manual is IP Australia’s guidance on how examiners apply the law. It is not law.</li>
      <li>Only the Registrar decides whether an application is accepted.</li>
      <li>I may have missed a requirement, an exception or a step. For advice about your own situation, contact IP Australia or a registered trade marks attorney.</li>
    </ul>
    <button type="button" class="gd-why-close">Hide the detail</button>`;
}

/** A guided topic's detail: the records behind its picture, each labelled law or guidance. */
function guidedPanel(objects) {
  const refs = [...new Set(objects.flatMap(sourcesOf))].sort((a, b) => isLaw(b) - isLaw(a));
  return `<h3>Where this comes from</h3>
    <p>This topic is drawn from records written by AI from the Trade Marks Act, the Regulations and IP Australia’s guidance (the Manual). No trade marks expert has reviewed them. Every step and condition in the picture names its source: tap one to read it.</p>
    <div class="gd-srcs">${refs.map((ref) => `<button type="button" class="gd-src ${sourceOf(ref)}" data-ref="${esc(ref)}">${mark(ref)}${esc(refLabel(ref))}</button>`).join("")}</div>
    <p class="gd-note">${esc(explained.general_stamp)}</p>
    <button type="button" class="gd-why-close">Hide the detail</button>`;
}

// ------------------------------------------------------------------ guided topics (no model)

/** A reply built from the explanation objects alone: the page's words say what to look at; the
    records say the rest, with their sources. Used for the guided topics and whenever live
    answers are off. */
async function guided(text, topic, bot) {
  await new Promise((r) => setTimeout(r, 350));
  const t = topic || topicFor(text);
  const gp = explained.walkthroughs[0];
  let say = [], visual = "", clarify = null, objects = [], next = [];
  if (t === "journey" || t === "after") {
    visual = journey(gp, t === "after" ? "acceptance_published" : "");
    objects = [gp];
    say = t === "after"
      ? ["Here’s where acceptance sits in the general journey. Tap a stage to see who acts, what can come next and any time rules that apply."]
      : ["Here’s the general path an application takes, from filing to registration.", "Tap any stage to see who acts and what can come next. A real application’s path can differ, and I don’t work out dates: those come from the notices IP Australia sends."];
    next = [{ text: "What does the examiner check?", topic: "checks" }, { text: "What happens after an examination report?", topic: "report" }];
  } else if (t === "report") {
    const gr = journeys.get(gp.steps.find((s) => s.continues_in)?.continues_in?.process) || explained.walkthroughs[1];
    visual = journey(gr, gr.steps[0]?.id || "");
    objects = [gr];
    say = ["Here’s what can happen after an examination report, in general. Tap a stage to see who acts and the time rules that apply."];
    next = [{ text: "I got an objection saying my name is too close to what other people already use. What does that mean?", topic: "objection" }];
  } else if (t === "checks") {
    say = [`I can show you how ${rules.size} parts of the Trade Marks Act are set out, one condition at a time, with the points that are facts kept apart from the points the examiner judges.`];
    clarify = { ask: true, question: "Which would you like to see?", why: "", options: [...rules.values()].map((r) => ({ label: ruleName(r).split(" · ")[0], rule: r.test, topic: `rule:${r.test}` })) };
  } else if (t === "objection" && objection) {
    say = ["Thanks for explaining. Words like that could describe more than one kind of objection, and each one is explained differently, so I won’t guess which it is."];
    clarify = {
      ask: true, question: objection.asks[0]?.question || "Which section does the report give?", why: objection.reads,
      options: objection.candidates.map((c) => ({ label: ruleName(c).split(" · ")[0], rule: c.test, topic: `rule:${c.test}` })),
      extra: [{ label: "I can’t find a section number", topic: "nosection", quiet: true }],
    };
  } else if (t === "nosection" && objection) {
    say = ["That’s okay. The words the report uses can help tell which it is.", liveOn() ? "Tell me, in your own words or the report’s, what it says the problem is, and I’ll take it from there." : "Live answers are off on this copy, so I can’t read the report’s words against the guidance right now. You can still look at what the examiner checks under each of these:"];
    if (!liveOn()) clarify = { ask: true, question: "Which would you like to look at?", why: "", options: objection.candidates.map((c) => ({ label: ruleName(c).split(" · ")[0], rule: c.test, topic: `rule:${c.test}` })) };
  } else if (t?.startsWith("rule:") && rules.has(t.slice(5))) {
    const r = rules.get(t.slice(5));
    visual = requirements(r);
    objects = [r];
    say = [`Here’s how ${ruleName(r).split(" · ")[0].toLowerCase()} is set out: what the examiner looks at, which points are facts and which are for the Registrar to judge, and the ways it might not apply.`, "Tap any source to read the law’s or the guidance’s own words."];
    next = [{ text: "What happens after an examination report?", topic: "report" }, { text: "How does applying for a trade mark work?", topic: "journey" }];
  } else {
    say = [!live.enabled ? "Live answers are off on this copy of the guide, so I can’t answer typed questions yet. Here’s what I can walk you through:"
      : "You’ve reached today’s limit of live questions in this browser. Here’s what I can still walk you through:"];
    next = STARTERS.map((s) => ({ text: s.text, topic: s.topic }));
  }
  bot.typing.hidden = true;
  bot.say.innerHTML = say.map((p) => `<p>${esc(p)}</p>`).join("");
  if (visual) shown.add(objects[0]?.process ? `journey:${objects[0].process}:${t === "after" ? "acceptance_published" : t === "report" ? objects[0].steps[0]?.id || "" : ""}` : `requirements:${objects[0]?.test}:`);
  bot.extra.innerHTML = visual + (clarify ? drawClarify(clarify) : "");
  if (objects.length) {
    bot.foot.hidden = false;
    bot.foot.innerHTML = `<span class="gd-stamp"><i></i>A guided topic · from records written by AI, not reviewed by an expert</span>
      <button type="button" class="gd-why-btn" aria-expanded="false">Where this comes from</button>`;
    bot.render = () => guidedPanel(objects);
  }
  turns.push({ role: "guide", plain: say.join(" "), clarify: clarify ? { ask: true, question: clarify.question, options: clarify.options } : null });
  if (!clarify) setChips(next);
}

/** A starter typed in its own words, or anything else: which guided topic to show. */
function topicFor(text) {
  const s = STARTERS.find((x) => x.text.toLowerCase() === text.toLowerCase());
  return s ? s.topic : null;
}

// ------------------------------------------------------------------ a source, opened

const sheet = $(".gd-sheet");
const veil = $(".gd-veil");
let opener = null;

async function openSource(ref, quote = "") {
  opener = document.activeElement;
  sheet.querySelector(".gd-sheet-title").innerHTML = `<b>Loading…</b>`;
  sheet.querySelector(".gd-sheet-body").textContent = "";
  sheet.classList.add("open");
  sheet.setAttribute("aria-hidden", "false");
  veil.hidden = false;
  sheet.querySelector(".gd-sheet-x").focus();
  let p;
  try { p = await data("passages"); } catch { sheet.querySelector(".gd-sheet-title").innerHTML = `<b>${esc(refLabel(ref))}</b>`; return; }
  const law = p.legislation[ref];
  const row = law ? null : p.chunks.find((c) => c[0] === ref);
  const src = sourceOf(ref);
  const badge = `<span class="gd-badge ${src}">${mark(ref)}${esc(SOURCE[src].short)} · ${esc(SOURCE[src].role)}</span>`;
  if (!law && !row) {
    sheet.querySelector(".gd-sheet-title").innerHTML = `${badge}<b>${esc(refLabel(ref))}</b>`;
    sheet.querySelector(".gd-sheet-body").innerHTML = `<p class="gd-sheet-note">This copy of the guide does not hold this passage.</p>${quote ? `“${esc(quote)}”` : ""}`;
    return;
  }
  const text = law ? law[3] : row[3];
  const page = row ? p.pages[row[1]] || {} : {};
  const heading = law ? headingOf(p, ref) : "";
  const title = law ? `${refLabel(ref)}${heading ? ` · ${heading}` : ""}` : page.title || refLabel(ref);
  let body = esc(text);
  const span = quote ? locate(text, quote) : null;
  if (span) body = `${esc(text.slice(0, span[0]))}<mark>${esc(text.slice(span[0], span[1]))}</mark>${esc(text.slice(span[1]))}`;
  sheet.querySelector(".gd-sheet-title").innerHTML = `${badge}<b>${esc(title)}</b><small>${esc(law ? law[2] : row[2] || "")}</small>`;
  sheet.querySelector(".gd-sheet-body").innerHTML = `${src === "manual" ? `<p class="gd-sheet-note">IP Australia’s guidance on how examiners apply the law. It is not law.</p>` : ""}${body}${page.url ? `<p class="gd-sheet-note" style="margin-top:1.4em"><a href="${esc(page.url)}" target="_blank" rel="noopener">Read this page in IP Australia’s Manual ↗</a></p>` : ""}`;
  if (span) sheet.querySelector("mark")?.scrollIntoView({ block: "center" });
}

function closeSource() {
  if (!sheet.classList.contains("open")) return;
  sheet.classList.remove("open");
  sheet.setAttribute("aria-hidden", "true");
  veil.hidden = true;
  opener?.focus?.();
}

// ------------------------------------------------------------------ wiring

const grow = () => { box.style.height = "auto"; box.style.height = `${Math.min(160, box.scrollHeight)}px`; };
box.addEventListener("input", grow);
box.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
form.addEventListener("submit", (e) => { e.preventDefault(); send(box.value); });

document.addEventListener("click", (e) => {
  const starter = e.target.closest("[data-starter]");
  if (starter) { const s = STARTERS[Number(starter.dataset.starter)]; send(s.text, { topic: liveOn() ? null : s.topic }); return; }
  // A button with a topic belongs to a guided reply (or the fallback after an error) and stays
  // guided; any other is sent as the reader's own words.
  const say = e.target.closest("[data-send]");
  if (say && !say.disabled) { send(say.dataset.send, { topic: say.dataset.topic || null }); return; }
  const ref = e.target.closest("[data-ref]");
  if (ref) { openSource(ref.dataset.ref, ref.dataset.quote || ""); return; }
  const step = e.target.closest(".gd-step-b");
  if (step) { const li = step.parentElement; li.classList.toggle("open"); step.setAttribute("aria-expanded", String(li.classList.contains("open"))); return; }
  const other = e.target.closest("[data-journey]");
  if (other && journeys.has(other.dataset.journey)) { other.closest(".gd-vis").outerHTML = journey(journeys.get(other.dataset.journey), journeys.get(other.dataset.journey).steps[0]?.id || ""); return; }
  const why = e.target.closest(".gd-why-btn");
  if (why) { toggleWhy(why); return; }
  const close = e.target.closest(".gd-why-close");
  if (close) { toggleWhy(close.closest(".gd-bot").querySelector(".gd-why-btn")); return; }
});

function toggleWhy(btn) {
  const bot = btn.closest(".gd-bot");
  const panel = bot.querySelector(".gd-why");
  const open = panel.hidden;
  if (open && !panel.innerHTML) {
    const r = renderers.get(bot);
    panel.innerHTML = r ? r() : "";
    data("passages").then((p) => panel.querySelectorAll("[data-title]").forEach((b) => {
      const h = headingOf(p, b.dataset.title);
      if (h && !isLaw(b.dataset.title)) b.lastChild.textContent = clip(h, 60);
    })).catch(() => {});
  }
  panel.hidden = !open;
  btn.setAttribute("aria-expanded", String(open));
  btn.textContent = open ? "Hide where this comes from" : "Where this comes from";
}

newBtn.addEventListener("click", () => { controller?.abort(); busy = false; sendBtn.disabled = false; hello(); window.scrollTo({ top: 0 }); });
$(".gd-about-btn").addEventListener("click", (e) => {
  const panel = $("#gd-about");
  panel.hidden = !panel.hidden;
  e.currentTarget.setAttribute("aria-expanded", String(!panel.hidden));
});
$(".gd-sheet-x").addEventListener("click", closeSource);
veil.addEventListener("click", closeSource);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSource(); });

start();
