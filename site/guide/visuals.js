/* The guide's pictures (ADR-0154). Each draws an explanation object `tm_knowledge.explain`
   already builds, from `data/explain.json`: a process walked through as a journey, or one legal
   test's requirements as what the examiner looks at. A reply only names one by id, and the page
   checks the id before drawing it, so a picture never says anything its record does not.

   The rules are the customer preview's (`customers.js`): every element keeps its source; a
   condition is a fact or an assessment, and an assessment is never made here; a "may" stays a
   "may"; nothing works out a date or says what will happen. Every picture has its text
   equivalent, the record's own (`text`), and its stamp. */

import { esc, refButton, ICON } from "./common.js";

const KIND = {
  fact: ["fact", ICON.fact, "Fact"],
  evaluative: ["evaluative", ICON.judge, "Assessment"],
};
const EFFECT_WORD = { obligation: "must", discretion: "may", bar: "may not" };

const textEquivalent = (text, label = "Read this picture as text") =>
  `<details><summary>${esc(label)}</summary><pre>${esc(text)}</pre></details>`;

/** "Section 44 · Conflict with another person's earlier trade mark". */
export function ruleName(r) {
  const section = /\((sections?|regulations?) ([^)]+)\)\s*$/.exec(r.title || "");
  const title = String(r.title || "").replace(/\s*\([^)]*\)\s*$/, "");
  return section ? `${section[1][0].toUpperCase()}${section[1].slice(1)} ${section[2]} · ${title}` : title;
}

// ------------------------------------------------------------------ the journey

/** A process as a timeline, one step lit. `focus` is a step id or "". */
export function journey(w, focus = "") {
  const ends = new Set(w.steps.filter((s) => !s.next.length).map((s) => s.id));
  const step = (s) => {
    const lit = s.id === focus;
    return `<li class="gd-step${lit ? " lit open" : ""}${ends.has(s.id) ? " end" : ""}" data-step="${esc(s.id)}">
      <button type="button" class="gd-step-b" aria-expanded="${lit}"><b>${esc(s.label)}</b><span class="gd-who">${esc(s.actor)}</span>${lit ? `<span class="gd-here">This part</span>` : ""}</button>
      <div class="gd-step-d">
        <p>${esc(s.text)} ${refButton(s.ref, s.quote)}</p>
        ${s.next.length ? `<p class="gd-note">What can come next:</p><ul>${s.next.map((n) => `<li><b>${esc(n.label)}</b>, when ${esc(n.when)}</li>`).join("")}</ul>` : `<p class="gd-note">This is where the journey ends.</p>`}
        ${s.time_rules.map((t) => `<div class="gd-time">${ICON.clock}<span>${esc(t.text)} ${refButton(t.ref, t.quote)}</span></div>`).join("")}
        ${s.continues_in ? `<p class="gd-note"><button type="button" class="gd-link" data-journey="${esc(s.continues_in.process)}">See what can happen after this: ${esc(s.continues_in.title.replace(/\s*\([^)]*\)\s*$/, ""))}</button></p>` : ""}
      </div>
    </li>`;
  };
  return `<figure class="gd-vis" data-vis="journey" data-id="${esc(w.process)}">
    <span class="gd-vis-k">The journey</span>
    <h4>${esc(w.title.replace(/\s*\([^)]*\)\s*$/, ""))}</h4>
    <p class="gd-vis-s">One general path. Tap a stage to see who acts and what can come next. A real application’s path may differ, and no date is worked out here.</p>
    <ol class="gd-steps">${w.steps.map(step).join("")}</ol>
    <div class="gd-vis-foot"><span>${esc(w.note)}</span>${textEquivalent(w.text)}</div>
  </figure>`;
}

// ------------------------------------------------------------------ what the examiner looks at

function condition(n) {
  if (n.children) {
    const join = n.kind === "all" ? "All of these:" : "Any one of these:";
    return `<li class="gd-group">${n.text ? `<p>${esc(n.text)}</p>` : ""}<p>${join}</p><ul class="gd-conds">${n.children.map(condition).join("")}</ul></li>`;
  }
  const [cls, svg, word] = KIND[n.kind] || KIND.fact;
  return `<li class="gd-cond"><span class="gd-kind ${cls}">${svg}${word}</span><span>${esc(n.text)} ${refButton(n.ref, n.quote)}</span></li>`;
}

/** One legal test's requirements: the effect, the conditions marked fact or assessment, the ways
    it might not apply and the ways people respond. */
export function requirements(r) {
  const top = r.condition.children && r.condition.kind === "all" && !r.condition.text ? r.condition.children : [r.condition];
  const word = EFFECT_WORD[r.effect.kind] || "";
  return `<figure class="gd-vis" data-vis="requirements" data-id="${esc(r.test)}">
    <span class="gd-vis-k">What the examiner looks at</span>
    <h4>${esc(ruleName(r))}</h4>
    <p class="gd-effect">If ${top.length > 1 ? "all of these are so" : "this is so"}, the law says: <b>${esc(r.effect.text)}</b> ${refButton(r.effect.ref, r.effect.quote)}${word ? ` <span class="gd-note">(The word is “${esc(word)}”.)</span>` : ""}</p>
    <div class="gd-keyline"><span><span class="gd-kind fact">${ICON.fact}Fact</span> something records can show, such as a date or a registration</span>
      <span><span class="gd-kind evaluative">${ICON.judge}Assessment</span> for the Registrar to judge, never worked out from facts alone</span></div>
    <ul class="gd-conds">${top.map(condition).join("")}</ul>
    ${r.exceptions.length ? `<p class="gd-sub">Ways it might not apply</p>${r.exceptions.map((x) => `<div class="gd-exc">
      <p>${esc(x.text)} ${refButton(x.ref, x.quote)}</p><p class="gd-note"><span class="gd-may">${esc(EFFECT_WORD[x.effect.kind] || "")}</span> · ${esc(x.effect.reads)}</p></div>`).join("")}` : ""}
    ${r.routes.length ? `<p class="gd-sub">Ways people respond</p><ul class="gd-conds">${r.routes.map((w) => `<li class="gd-cond"><span class="gd-kind plain">${w.authority === "law" ? "The law" : "Guidance"}</span><span>${esc(w.text)} ${refButton(w.ref, w.quote)}</span></li>`).join("")}</ul>` : ""}
    <div class="gd-vis-foot"><span class="gd-stamp"><i></i>${esc(r.stamp)}</span>${textEquivalent(r.text)}</div>
  </figure>`;
}

// ------------------------------------------------------------------ a clarifying question's options

/** The options of a clarifying question: those that lead to a rule drawn as cards with the rule
    named, the rest as plain choices. Each sends its label as the reader's reply. */
export function options(opts, rules) {
  const cards = opts.filter((o) => rules.has(o.rule));
  const plain = opts.filter((o) => !rules.has(o.rule));
  return `${cards.length ? `<div class="gd-cards">${cards.map((o) => {
      const r = rules.get(o.rule);
      const [section, title] = ruleName(r).includes(" · ") ? ruleName(r).split(" · ") : ["", ruleName(r)];
      const same = o.label.toLowerCase().includes(title.toLowerCase());
      return `<button type="button" class="gd-card" data-send="${esc(o.label)}"${o.topic ? ` data-topic="${esc(o.topic)}"` : ""}><b>${esc(o.label)}</b>${same ? "" : `<span class="gd-card-s">${esc(o.label.toLowerCase().startsWith(section.toLowerCase()) ? title : ruleName(r))}</span>`}</button>`;
    }).join("")}</div>` : ""}
    ${plain.length ? `<div class="gd-opts">${plain.map((o) => `<button type="button" class="gd-opt${o.quiet ? " quiet" : ""}" data-send="${esc(o.label)}"${o.topic ? ` data-topic="${esc(o.topic)}"` : ""}>${esc(o.label)}</button>`).join("")}</div>` : ""}`;
}

/** Every source a picture shows, for "Where this comes from" on a guided topic. */
export function sourcesOf(object) {
  return (object?.sources || []).map((s) => s.ref);
}
