/* The overview: what the knowledge foundation is and what it might enable for each group it serves
   (ADR-0151, on the owner's word; the "Can it be trusted?" band was removed at the owner's request).

   The owner's order: one real rule first, then a door for each group (examiners, the public,
   direction setting) and one for the technically curious.
   The hero is the headline and one real rule alone (the owner's annotations, ADR-0153): section 44
   as its structured record holds it, turned from the Act's words into conditions: which are facts
   a record can settle and which are assessments only a person can make. Every number is read from the data; the measurement is
   said in both directions; nothing here says how an application will be decided. */

import { esc, fmt, load, refChip } from "./app.js";
import { icon } from "./icons.js";
import { drawing } from "./illustrations.js";

/** A measured difference in words, from its estimate and 95% interval (× 100). */
export function difference([est, lo, hi], better, worse) {
  const pts = (x) => Math.abs(x * 100).toFixed(1);
  const range = `95% interval ${(lo * 100).toFixed(1)} to ${(hi * 100).toFixed(1)}`;
  if (lo > 0) return `<b>${pts(est)} points ${better}</b> <span class="muted">(${range})</span>`;
  if (hi < 0) return `<b>${pts(est)} points ${worse}</b> <span class="muted">(${range})</span>`;
  return `<b>no clear difference</b> <span class="muted">(${range})</span>`;
}

const KIND = { fact: "Fact", evaluative: "Assessment" };
const EFFECT = { obligation: "must", discretion: "may", bar: "may not" };

/** The kind of a condition, or of a group whose conditions are all of one kind. */
function kindOf(node) {
  if (!node.children) return node.kind;
  const kinds = new Set(node.children.map(kindOf));
  return kinds.size === 1 ? [...kinds][0] : "mixed";
}
const quotesOf = (node) => (node.children ? node.children.flatMap(quotesOf) : node.quote ? [node.quote] : []);

export async function render(root, { ontology }) {
  const [explain, stability] = await Promise.all([load("explain"), load("stability")]);
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;
  const provisions = Object.keys(stability.provisions || {}).length;
  const rule = explain.requirements.find((r) => r.provision === "TMA1995/s44") || explain.requirements[0];

  root.innerHTML = `
  <div class="ld">
    <section class="wrap ld-hero">
      <div class="ld-copy">
        <span class="eyebrow">Australian trade marks · proof of concept</span>
        <h1 class="ld-title">Trade mark law and guidance, turned into rules and code</h1>
      </div>
      ${rule ? hero(rule) : ""}
    </section>

    <section class="ld-doors-band" id="ld-doors" tabindex="-1" aria-labelledby="ld-d">
      <div class="wrap">
        <div class="sec-head"><div><span class="eyebrow">See the demonstrations</span><h2 id="ld-d">Three questions, one shared foundation</h2></div>
          <p>Each path starts with something you can try. It also shows where a similar tool might be useful later, and what would need to be checked or built first.</p></div>
        <div class="ld-doors">
          ${door({ href: "#/examiners", cls: "aud-exam", art: "door-exam", k: "For examiners", title: "Find and connect relevant examination material",
            now: ["Follow a legal idea to related concepts and source passages", "Try an AI-written research answer and check its quotations"],
            next: "Possible later: guided learning, better-managed knowledge, and tools that surface related matters" })}
          ${door({ href: "#/public", cls: "aud-pub", art: "door-pub", k: "For the public", title: "Understand requirements, objections and next steps",
            now: ["Walk through an objection on an invented application", "See what a rule asks, and the path an application takes"],
            next: "Possible later: customer-tested guidance linked to an applicant’s own stage or report" })}
          ${door({ href: "#/direction", cls: "aud-pol", art: "door-pol", k: "For direction setting", sub: "Policy and strategy", title: "See what may need review when the system changes",
            now: ["Trace recorded links from a section of the Act or a page of the Manual", "Explore the questions a fictional new right would raise"],
            next: "Possible later: maintenance workflows, option comparison and broader policy analysis" })}
        </div>
      </div>
    </section>

    <section class="wrap section ld-fdn-sec" aria-labelledby="ld-f">
      <div class="sec-head"><div><span class="eyebrow">Why a foundation</span><h2 id="ld-f">One foundation, several possible uses</h2></div>
        <p>The demonstrations read the same source-linked records, so different tools can draw on the same definitions and relationships while the source and review status travel with them. Reuse across operational services is a possible next step, not something tested here. Select a tool to see what it draws on.</p></div>
      ${foundation(c, concepts, relations, provisions)}
      <div class="ld-xai">
        <span class="ld-xai-i">${icon("shield")}</span>
        <div><h3>Shared records can make a tool’s sources easier to inspect</h3>
          <p>The demonstrations link their outputs to recorded concepts, rules and source passages. A future tool could reuse those links to help a person inspect the material behind an output. That would still need testing for accuracy and completeness.</p></div>
      </div>
    </section>

    <section class="wrap section ld-nerd-sec" aria-labelledby="ld-n">
      <a class="ld-nerd" href="#/nerds">
        <div class="ld-nerd-copy">
          <span class="eyebrow">For nerds</span>
          <h2 id="ld-n">Let’s get technical</h2>
          <p>Take a deep dive into how it works. Fair warning: this part is mostly for the technically minded.</p>
          <ul class="ld-nerd-list">${["The knowledge map", "Rules as code", "The standards", "Data tables", "Current results and limits", "Glossary"].map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
          <span class="btn lime">Go to For nerds ${icon("arrow")}</span>
        </div>
        <div class="ld-nerd-art">${drawing("door-nerd")}</div>
      </a>
    </section>
  </div>`;

  if (rule) startHero(root);
  startFoundation(root);
}

// ------------------------------------------------------------------ the hero: one rule, from words to structure

function hero(r) {
  const parts = r.condition.children || [r.condition];
  const words = (text, max = 92) => (text.length > max ? `${text.slice(0, max - 1).replace(/\s+\S*$/, "")}…` : text);
  const fragments = [
    `<span class="ld-q-frag must" data-n="0">${esc(r.effect.quote)}</span>`,
    ...parts.map((p, i) => quotesOf(p).map((q) => `<span class="ld-q-frag" data-n="${i + 1}"><sup>${i + 1}</sup>${esc(q)}</span>`).join(" … ")),
  ];
  const tiles = parts.map((p, i) => {
    const k = kindOf(p);
    return `<div class="ld-tile ${k}" data-n="${i + 1}">
      <span class="ld-tile-k">${k === "evaluative" ? scaleIcon() : factIcon()}${esc(KIND[k] || "Facts and assessments")}</span>
      <p><sup>${i + 1}</sup>${esc(words(p.text || p.children.map((x) => x.text).join(" or ")))}</p></div>`;
  }).join("");
  return `<figure class="ld-rule card" aria-labelledby="ld-rule-cap">
    <div class="ld-rule-top"><span class="eyebrow">One rule, from words to structure</span>
      <button type="button" class="btn small ghost ld-replay" aria-label="Play the example again">${icon("replay")} Replay</button></div>
    <div class="ld-rule-body">
    <div class="ld-rule-words">
      <p class="ld-rule-src">${refChip(r.provision)} <span class="tiny">The Act’s words, quoted in part</span></p>
      <blockquote class="ld-q">${fragments.join(" … ")}</blockquote>
    </div>
    <div class="ld-rule-arrow" aria-hidden="true"><span>becomes</span>${icon("arrow")}</div>
    <div class="ld-rule-code">
      <p class="ld-rule-src"><span class="tiny">The same rule, as structured data</span></p>
      <div class="ld-row"><span class="ld-lab">If all of these</span><div class="ld-tiles">${tiles}</div></div>
      <div class="ld-row then"><span class="ld-lab">Then</span><div class="ld-effect" data-n="0"><b>${esc(EFFECT[r.effect.kind] || r.effect.kind)}</b><span>${esc(r.effect.text)}</span></div></div>
      ${r.exceptions.length ? `<div class="ld-row unless"><span class="ld-lab">Unless</span><div class="ld-excs">${r.exceptions.map((x) => `<div class="ld-exc"><b>${esc(EFFECT[x.effect.kind] || x.effect.kind)}</b><span>${esc(words(x.text, 70))}</span></div>`).join("")}</div></div>` : ""}
    </div>
    </div>
    <figcaption id="ld-rule-cap" class="ld-rule-cap">
      <span><i class="ld-k fact" aria-hidden="true">${factIcon()}</i><b>Fact:</b> something a record can confirm.</span>
      <span><i class="ld-k evaluative" aria-hidden="true">${scaleIcon()}</i><b>Assessment:</b> a judgement only a person can make. The system never makes it.</span>
      <span class="ld-stamp"><span class="trust machine" title="AI wrote this record. A trade marks expert has yet to review it.">AI-written · unreviewed</span> <a href="#/customers/requirements/${esc(r.test)}">See this rule explained</a></span>
    </figcaption>
  </figure>`;
}

const factIcon = () => `<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="2.5" y="2.5" width="11" height="11" rx="2"/><path d="m5 8.3 2 2 4-4.4"/></svg>`;
const scaleIcon = () => `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2.5v11M5 13.5h6M3 5h10M3 5l-1.8 4a1.9 1.9 0 0 0 3.6 0zM13 5l-1.8 4a1.9 1.9 0 0 0 3.6 0z"/></svg>`;

function startHero(root) {
  const fig = root.querySelector(".ld-rule");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const steps = [...new Set([...fig.querySelectorAll("[data-n]")].map((x) => Number(x.dataset.n)))].sort((a, b) => a - b);
  const order = [...steps.filter((n) => n > 0), 0];
  let timers = [];
  const light = (n) => fig.querySelectorAll("[data-n]").forEach((x) => x.classList.toggle("lit", Number(x.dataset.n) === n));
  const play = () => {
    timers.forEach(clearTimeout);
    timers = [];
    fig.classList.remove("done");
    if (reduced) { fig.classList.add("done"); return; }
    order.forEach((n, i) => timers.push(setTimeout(() => light(n), 500 + i * 1300)));
    timers.push(setTimeout(() => { light(-1); fig.classList.add("done"); }, 500 + order.length * 1300));
  };
  fig.querySelector(".ld-replay").addEventListener("click", play);
  // A reader can light any pair by hand: a fragment and its condition say the same thing.
  fig.addEventListener("mouseover", (e) => { const t = e.target.closest("[data-n]"); if (t && fig.classList.contains("done")) light(Number(t.dataset.n)); });
  fig.addEventListener("mouseleave", () => { if (fig.classList.contains("done")) light(-1); });
  const seen = new IntersectionObserver((entries) => { if (entries.some((e) => e.isIntersecting)) { seen.disconnect(); play(); } }, { threshold: 0.35 });
  seen.observe(fig);
}

// ------------------------------------------------------------------ the doors

function door({ href, cls, art, k, sub = "", title, now, next }) {
  return `<a class="ld-door ${cls}" href="${href}">
    <div class="ld-door-art">${drawing(art)}</div>
    <div class="ld-door-body">
      <span class="ld-door-k">${esc(k)}</span>${sub ? `<span class="ld-door-sub">${esc(sub)}</span>` : ""}
      <h3>${esc(title)}</h3>
      <ul>${now.map((x) => `<li>${icon("check")}<span>${esc(x)}</span></li>`).join("")}</ul>
      <p class="ld-door-next">${esc(next)}</p>
      <span class="link-arrow">Explore ${esc(k.toLowerCase())} ${icon("arrow")}</span>
    </div>
  </a>`;
}

// ------------------------------------------------------------------ one foundation, many tools

const BLOCKS = [
  ["ideas", "Ideas and their names", (c, n) => `${fmt(n.concepts)} ideas, with the other names each goes by`],
  ["links", "Connections", (c, n) => `${fmt(n.relations)} connections, each quoting the sentence it rests on`],
  ["rules", "Rules", (c) => `${fmt(c.tests)} legal tests and ${fmt(c.processes)} procedures, set out as conditions and steps`],
  ["sources", "Sources and authorship", (c, n) => `every record tied to the words it rests on, who wrote it and whether a person reviewed it; ${fmt(n.provisions)} provisions with recorded dependants`],
  ["time", "Versions of the law", () => "which text of the Act each quotation is from, and when that is unknown"],
];

const TOOLS = [
  { id: "concepts", aud: "aud-exam", name: "Explore a legal concept", href: "#/concepts", uses: ["ideas", "links", "rules", "sources"], text: "What this version records about one idea, with a source for each part." },
  { id: "ask", aud: "aud-exam", name: "Ask a research question", href: "#/ask", uses: ["ideas", "links", "rules", "sources", "time"], text: "For newer examiners: the law and the guidance for a question, and an answer that shows what each statement rests on." },
  { id: "objection", aud: "aud-pub", name: "Understand an objection", href: "#/customers/objection", uses: ["rules", "sources", "time"], text: "An objection explained step by step, on invented cases." },
  { id: "journey", aud: "aud-pub", name: "The application journey", href: "#/customers/process", uses: ["rules", "sources"], text: "Each stage from filing to registration, and what moves it on." },
  { id: "chat", aud: "aud-pub", name: "Chat with Tommy Tradecraft", href: "guide/", uses: ["ideas", "links", "rules", "sources", "time"], text: "An AI guide for a friendly chat about requirements, the process and objections, with pictures; it asks when a fact would change the explanation, and shows its sources on request." },
  { id: "change", aud: "aud-pol", name: "Trace a change", href: "#/change", uses: ["ideas", "links", "rules", "sources"], text: "Records linked to a section of the Act or a page of the Manual: a starting list for review." },
  { id: "whatif", aud: "aud-pol", name: "A new right: what would it touch?", href: "#/whatif", uses: ["ideas", "links", "rules", "sources"], text: "A fictional register laid over today's practice, and the questions it raises. The records are not changed." },
  { id: "register", aud: "aud-exam", name: "Searching the register by meaning", future: true, uses: ["ideas", "links"], text: "Finding marks and goods by what they mean, once the register is connected." },
  { id: "aitest", aud: "aud-pol", name: "Checking AI answers", future: true, uses: ["ideas", "rules", "sources"], text: "Testing whether an AI tool named the right ideas, sources and exceptions." },
  { id: "decisions", aud: "aud-pol", name: "Recording a decision’s reasons", future: true, uses: ["rules", "sources", "time"], text: "Setting out what a recorded decision rested on. Never making one." },
  { id: "ml", aud: "aud-pol", name: "Data for machine learning", future: true, uses: ["ideas", "links", "rules", "sources", "time"], text: "Labelled, sourced examples to train and test future models." },
];

function foundation(c, concepts, relations, provisions) {
  const n = { concepts, relations, provisions };
  const tool = (t) => `<button type="button" class="ld-tool ${t.aud}${t.future ? " future" : ""}" data-tool="${t.id}" aria-pressed="false">
    <i class="ld-tool-dot" aria-hidden="true"></i><b>${esc(t.name)}</b><span class="vh">${t.future ? "possible future use" : "working demonstration"}</span></button>`;
  return `<div class="ld-fdn card">
    <div class="ld-fdn-src">
      <span class="ld-fdn-lab">The sources</span>
      <div class="ld-srcs">
        <span class="law act"><i class="mark" aria-hidden="true"></i><b>Trade Marks Act 1995</b> law</span>
        <span class="law regs"><i class="mark" aria-hidden="true"></i><b>Trade Marks Regulations 1995</b> law</span>
        <span class="manual"><i class="mark" aria-hidden="true"></i><b>Trade Marks Manual</b> practice</span>
      </div>
    </div>
    <div class="ld-fdn-slab">
      <span class="ld-fdn-lab">The foundation</span>
      <div class="ld-blocks">${BLOCKS.map(([id, name, text]) => `<div class="ld-block" data-block="${id}"><b>${esc(name)}</b><span>${text(c, n)}</span></div>`).join("")}</div>
    </div>
    <svg class="ld-fdn-links" aria-hidden="true"></svg>
    <div class="ld-fdn-tools">
      <span class="ld-fdn-lab">The tools built on it</span>
      <p class="ld-tools-k">Working demonstrations</p>
      <div class="ld-tools">${TOOLS.filter((t) => !t.future).map(tool).join("")}</div>
      <p class="ld-tools-k">Possible future uses <span>not built yet</span></p>
      <div class="ld-tools">${TOOLS.filter((t) => t.future).map(tool).join("")}</div>
      <p class="ld-tool-say" aria-live="polite"></p>
    </div>
  </div>`;
}

function startFoundation(root) {
  const box = root.querySelector(".ld-fdn");
  const links = box.querySelector(".ld-fdn-links");
  const say = box.querySelector(".ld-tool-say");
  let chosen = "concepts";
  const draw = () => {
    // Measured after layout, never in the first pass (Q-63).
    const b = box.getBoundingClientRect();
    if (!b.width) return;
    const t = TOOLS.find((x) => x.id === chosen);
    const from = box.querySelector(`[data-tool="${chosen}"]`).getBoundingClientRect();
    links.setAttribute("viewBox", `0 0 ${b.width} ${b.height}`);
    links.innerHTML = t.uses.map((id) => {
      const to = box.querySelector(`[data-block="${id}"]`).getBoundingClientRect();
      const x1 = from.left + from.width / 2 - b.left, y1 = from.top - b.top;
      const x2 = to.left + to.width / 2 - b.left, y2 = to.bottom - b.top;
      const my = (y1 + y2) / 2;
      return `<path d="M${x1} ${y1} C${x1} ${my} ${x2} ${my} ${x2} ${y2}" class="ld-link${t.future ? " future" : ""}"/><circle cx="${x2}" cy="${y2}" r="3.5" class="ld-link-dot"/>`;
    }).join("");
  };
  const choose = (id) => {
    chosen = id;
    const t = TOOLS.find((x) => x.id === id);
    box.querySelectorAll("[data-tool]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.tool === id)));
    box.querySelectorAll("[data-block]").forEach((b) => b.classList.toggle("on", t.uses.includes(b.dataset.block)));
    say.innerHTML = `<b>${esc(t.name)}.</b> ${esc(t.text)} ${t.href ? `<a class="link-arrow" href="${t.href}">Try it ${icon("arrow")}</a>` : `<span class="tiny">A possibility, not built yet.</span>`}`;
    requestAnimationFrame(draw);
  };
  box.addEventListener("click", (e) => { const b = e.target.closest("[data-tool]"); if (b) choose(b.dataset.tool); });
  box.addEventListener("mouseover", (e) => { const b = e.target.closest("[data-tool]"); if (b && b.dataset.tool !== chosen) choose(b.dataset.tool); });
  box.addEventListener("focusin", (e) => { const b = e.target.closest("[data-tool]"); if (b && b.dataset.tool !== chosen) choose(b.dataset.tool); });
  const onResize = () => draw();
  window.addEventListener("resize", onResize);
  choose(chosen);
}
