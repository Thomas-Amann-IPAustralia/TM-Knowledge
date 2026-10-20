/* Drawings of the structured records (ADR-0142), shared by Rules as code and the customer preview.

   Two pictures, each with a text equivalent built from the same data, so the words and the picture
   cannot say different things: a legal test drawn as its conditions (all of them across, any one
   of them stacked), what follows, the exceptions and the routes; and a process drawn as a journey
   from left to right, every way on an arrow. Neither evaluates a condition or computes a date;
   where the customer preview shows a recorded state, it is the explanation object's, read from
   `data/explain.json`. Every class is prefixed `dg-` (Q-101). */

import { esc, refChip, srcBadge } from "./app.js";

export const EFFECT_WORD = { obligation: "must", discretion: "may", bar: "may not" };
export const EFFECT_NAME = { obligation: "an obligation", discretion: "a discretion", bar: "a bar" };
const LEAF = { fact: "Fact", evaluative: "Assessment" };
const LEAF_LONG = { fact: "a fact about the application or the other trade mark", evaluative: "a person's assessment, never computed" };
/** A recorded state, by a mark and a word as well as a colour. */
export const STATE = { met: ["✓", "recorded as met"], not_met: ["✗", "recorded as not met"], open: ["?", "not established from the available facts"] };

const joinOf = (node) => (node.all ? "all" : node.any ? "any" : node.kind === "all" || node.kind === "any" ? node.kind : null);
const childrenOf = (node) => node.all || node.any || node.children || [];

/** A condition tree, drawn so its logic shows: all of a group side by side joined by "and", any
    one of a group stacked and joined by "or". A leaf says whether it is a fact or a person's
    assessment; with `states`, a node also shows the state the explanation records for it. */
export function conditionBoxes(node, { states = false } = {}) {
  if (!node) return "";
  const join = joinOf(node);
  const mark = states && node.state ? stateMark(node.state) : "";
  if (join) {
    const kids = childrenOf(node).map((child) => conditionBoxes(child, { states }));
    return `<div class="dg-group dg-${join}">
      <p class="dg-join">${mark}${join === "all" ? "All of these" : "Any one of these"}${node.text ? ` <span class="dg-gtext">${esc(node.text)}</span>` : ""}</p>
      <div class="dg-kids">${kids.join(`<span class="dg-op" aria-hidden="true">${join === "all" ? "and" : "or"}</span>`)}</div></div>`;
  }
  return `<div class="dg-leaf dg-${esc(node.kind)}${states && node.state ? ` dg-s-${esc(node.state)}` : ""}">
    <span class="dg-kind"><i aria-hidden="true"></i>${esc(LEAF[node.kind] || node.kind)}</span>
    <p>${mark}${esc(node.text)}</p>
    ${states && node.why ? `<p class="dg-why">${esc(STATE[node.state]?.[1] || "")}: ${esc(node.why)}</p>` : ""}
    <p class="dg-ref">${refChip(node.ref)}</p></div>`;
}

export const stateMark = (state) => `<span class="dg-st dg-st-${esc(state)}" title="${esc(STATE[state]?.[1] || state)}"><span aria-hidden="true">${STATE[state]?.[0] || ""}</span><span class="vh">${esc(STATE[state]?.[1] || state)}: </span></span>`;

/** A condition tree as a checklist: each condition on its own line with the state the explanation
    records for it, any-of groups indented under "One of these". The compact view of a matter; the
    full diagram is a click away. */
export function conditionChecklist(node) {
  if (!node) return "";
  const join = joinOf(node);
  if (join) {
    const kids = childrenOf(node).map((child) => `<li>${conditionChecklist(child)}</li>`).join("");
    return `${node.text || join === "any" ? `<p class="dg-cl-g">${node.state ? stateMark(node.state) : ""}${join === "any" ? "One of these" : "All of these"}${node.text ? `: <span>${esc(node.text)}</span>` : ""}</p>` : ""}
      <ul class="dg-cl${join === "any" ? " any" : ""}">${kids}</ul>`;
  }
  return `<div class="dg-cl-row">${node.state ? stateMark(node.state) : ""}<div><p>${esc(node.text)}</p>
    <p class="dg-cl-meta"><span class="dg-kind dg-${esc(node.kind)}"><i aria-hidden="true"></i>${esc(LEAF[node.kind] || node.kind)}</span>${node.why ? `<span>${esc(STATE[node.state]?.[1] || "")}: ${esc(node.why)}</span>` : ""}${refChip(node.ref)}</p></div></div>`;
}

/** The condition tree in words, one line a node, indented. */
export function conditionText(node, depth = 1, { states = false } = {}) {
  const pad = "  ".repeat(depth);
  const join = joinOf(node);
  if (join) {
    return [node.text ? `${pad}- ${node.text}` : null, `${pad}  ${join === "all" ? "All of these" : "Any one of these"}:`,
      ...childrenOf(node).map((child) => conditionText(child, depth + 1, { states }))].filter(Boolean).join("\n");
  }
  const state = states && node.state ? ` [${STATE[node.state][1]}${node.why ? `: ${node.why}` : ""}]` : "";
  return `${pad}- ${node.text} (${LEAF_LONG[node.kind] || node.kind})${state} (${node.ref})`;
}

/** The key to the leaves and the joins, said once above a test. */
export const conditionKey = () => `<div class="dg-keyline">
  <span><span class="dg-kind dg-fact"><i aria-hidden="true"></i>Fact</span> something a record can settle, such as a date</span>
  <span><span class="dg-kind dg-evaluative"><i aria-hidden="true"></i>Assessment</span> a person's judgement, shown and never computed</span>
  <span><b class="dg-op inline">and</b> all must hold <b class="dg-op inline">or</b> any one is enough</span></div>`;

/** The effect of a test or an exception: its modal word, large, then what follows. */
export const effectCard = (kind, text, ref) => `<div class="dg-effect dg-e-${esc(kind)}">
  <span class="dg-modal">${esc(EFFECT_WORD[kind] || kind)}</span>
  <div><p>${esc(text)}</p><p class="dg-ref">${ref ? refChip(ref) : ""} <span class="tiny">${esc(EFFECT_NAME[kind] || "")}</span></p></div></div>`;

/** A structured legal test as a diagram, from its record (`ontology.structures.tests`). */
export function testDiagram(t) {
  const exceptions = t.exceptions || [];
  const routes = t.routes || [];
  return `<div class="dg-test" role="group" aria-label="${esc(t.title)}, drawn as a diagram; its text equivalent follows">
    <div class="dg-head"><span class="dg-k">The provision</span><p class="dg-title">${esc(t.title)}</p>
      <p class="dg-ref">${refChip(t.provision)} ${srcBadge(t.provision)} <span class="tiny">Who acts: ${esc(t.actor)}</span></p></div>
    <div class="dg-flow-v">
      <div class="dg-stage"><span class="dg-lab">If</span><div>${conditionBoxes(t.condition)}</div></div>
      <div class="dg-stage"><span class="dg-lab">Then</span><div>${effectCard(t.effect.kind, t.effect.text, t.effect.ref)}</div></div>
      ${exceptions.length ? `<div class="dg-stage"><span class="dg-lab">Unless</span><div class="dg-excs">${exceptions.map((x) => `
        <div class="dg-exc"><p class="dg-exc-t">${esc(x.text)} ${refChip(x.ref)}</p>${conditionBoxes(x.condition)}${effectCard(x.effect.kind, x.effect.text, null)}</div>`).join("")}</div></div>` : ""}
      ${routes.length ? `<div class="dg-stage"><span class="dg-lab">What can be done</span><ul class="dg-routes">${routes.map((r) => `
        <li>${esc(r.text)} <span class="dg-ref">${refChip(r.ref)} ${srcBadge(r.ref)}</span></li>`).join("")}</ul></div>` : ""}
    </div>
  </div>`;
}

/** The same test in words: the text equivalent of the diagram. */
export function testText(t) {
  const lines = [`${t.title} (${t.provision}, law). Who acts: ${t.actor}.`, "It applies when:", conditionText(t.condition),
    `Then: ${t.effect.text} This is ${EFFECT_NAME[t.effect.kind] || t.effect.kind} ("${EFFECT_WORD[t.effect.kind] || t.effect.kind}"). (${t.effect.ref})`];
  for (const x of t.exceptions || []) {
    lines.push(`Unless (${x.ref}): ${x.text}`, conditionText(x.condition, 2),
      `  Then: ${x.effect.text} This is ${EFFECT_NAME[x.effect.kind] || x.effect.kind} ("${EFFECT_WORD[x.effect.kind] || x.effect.kind}").`);
  }
  for (const r of t.routes || []) lines.push(`What can be done (${r.ref}, ${r.authority || ""}): ${r.text}`);
  return lines.join("\n");
}

// ------------------------------------------------------------------ a process, drawn as a journey

/** Where each step sits: its column is its distance from the start along the arrows that go
    forward; the main line (the shortest way from the start to the first end the template lists)
    runs straight across, and every other step takes the nearest free row beside the step that
    leads to it. An arrow back to an earlier step is drawn as a loop over the top. */
function layoutFlow(steps, arcs) {
  const idx = new Map(steps.map((s, i) => [s.id, i]));
  const forward = arcs.filter((a) => idx.get(a.to) > idx.get(a.from));
  const rank = new Map(steps.map((s) => [s.id, 0]));
  for (const s of steps) for (const a of forward.filter((x) => x.from === s.id)) rank.set(a.to, Math.max(rank.get(a.to), rank.get(s.id) + 1));
  const ends = steps.filter((s) => s.kind === "end");
  const goal = (ends[0] || steps[steps.length - 1]).id;
  const prev = new Map([[steps[0].id, null]]);
  const queue = [steps[0].id];
  while (queue.length) {
    const at = queue.shift();
    if (at === goal) break;
    for (const a of forward.filter((x) => x.from === at)) if (!prev.has(a.to)) { prev.set(a.to, at); queue.push(a.to); }
  }
  const main = [];
  for (let at = prev.has(goal) ? goal : null; at; at = prev.get(at)) main.unshift(at);
  const lane = new Map(main.map((id) => [id, 0]));
  const taken = new Set(main.map((id) => `${rank.get(id)}:0`));
  for (const s of steps) {
    if (lane.has(s.id)) continue;
    const preds = forward.filter((a) => a.to === s.id && lane.has(a.from)).sort((a, b) => rank.get(b.from) - rank.get(a.from));
    const want = preds.length ? lane.get(preds[0].from) : 0;
    for (const d of [0, 1, -1, 2, -2, 3, -3]) {
      const l = want + d;
      if (!taken.has(`${rank.get(s.id)}:${l}`)) { lane.set(s.id, l); taken.add(`${rank.get(s.id)}:${l}`); break; }
    }
  }
  return { rank, lane, idx };
}

/** A process as a journey from left to right: each step a box, each way on an arrow, an arrow
    back to an earlier step a loop over the top. A dashed arrow depends on something a particular
    application must say. `steps`: {id, label, kind, more}; `arcs`: {from, to, needs}; with a
    matter, `done` steps are ticked, `current` is marked, and the arrows out of it are lit. */
export function flowSvg({ id, title, steps, arcs, current = null, done = [] }) {
  const { rank, lane, idx } = layoutFlow(steps, arcs);
  const BW = 150, BH = 60, CW = 186, RH = 92;
  const lanes = [...lane.values()];
  const minL = Math.min(0, ...lanes), maxL = Math.max(0, ...lanes);
  const back = arcs.filter((a) => idx.get(a.to) <= idx.get(a.from));
  const top = 34 + (back.length ? 26 + 14 * back.length : 0);
  const cols = Math.max(...rank.values()) + 1;
  const width = 20 + cols * CW;
  const height = top + (maxL - minL + 1) * RH + 10;
  const at = (sid) => ({ x: 14 + rank.get(sid) * CW, y: top + (lane.get(sid) - minL) * RH });
  const doneSet = new Set(done);
  const lit = new Set(current ? arcs.filter((a) => a.from === current).map((a) => a.to) : []);
  const desc = `Steps: ${steps.map((s) => s.label).join("; ")}. Ways on: ${arcs.map((a, k) => `${k + 1}. ${steps[idx.get(a.from)].label} to ${steps[idx.get(a.to)].label}`).join("; ")}.`;
  const parts = [`<svg class="dg-flow" viewBox="0 0 ${width} ${height}" style="max-width:${width}px" role="img" aria-labelledby="${id}-t ${id}-d">
    <title id="${id}-t">${esc(title)}</title><desc id="${id}-d">${esc(desc)}</desc>
    <defs><marker id="${id}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" class="dg-head"/></marker>
    <marker id="${id}-lit" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" class="dg-head lit"/></marker></defs>`];
  // arrows first, under the boxes
  let loop = 0;
  arcs.forEach((a) => {
    const p = at(a.from), q = at(a.to);
    const isLit = current && a.from === current;
    const cls = `dg-line${a.needs ? " dashed" : ""}${isLit ? " lit" : ""}`;
    const marker = `url(#${id}-${isLit ? "lit" : "arrow"})`;
    if (idx.get(a.to) <= idx.get(a.from)) {
      const y = top - 18 - 14 * loop++;
      const x1 = p.x + BW / 2 + 18, x2 = q.x + BW / 2 - 18;
      parts.push(`<path d="M${x1} ${p.y} C${x1} ${y} ${x2} ${y} ${x2} ${q.y - 1}" class="${cls} back" marker-end="${marker}"/>`);
      return;
    }
    const x1 = p.x + BW, y1 = p.y + BH / 2, x2 = q.x - 2, y2 = q.y + BH / 2;
    const skip = rank.get(a.to) - rank.get(a.from) > 1 && lane.get(a.to) === lane.get(a.from);
    if (skip) {
      const lift = lane.get(a.from) <= 0 ? -1 : 1;
      const yy = (lift < 0 ? p.y - 16 : p.y + BH + 16);
      parts.push(`<path d="M${p.x + BW - 30} ${lift < 0 ? p.y : p.y + BH} C${p.x + BW} ${yy} ${q.x} ${yy} ${q.x + 30} ${lift < 0 ? q.y - 1 : q.y + BH + 1}" class="${cls}" marker-end="${marker}"/>`);
      return;
    }
    const mx = (x1 + x2) / 2;
    parts.push(`<path d="M${x1} ${y1} C${mx} ${y1} ${mx} ${y2} ${x2} ${y2}" class="${cls}" marker-end="${marker}"/>`);
  });
  steps.forEach((s) => {
    const { x, y } = at(s.id);
    const cls = s.id === current ? "now" : doneSet.has(s.id) ? "done" : lit.has(s.id) ? "next" : s.kind === "start" || s.kind === "end" ? "edge" : "";
    const words = wrap(s.label, 19);
    parts.push(`<g class="dg-node ${cls}" data-step="${esc(s.id)}" transform="translate(${x},${y})" tabindex="0" role="button" aria-label="${esc(s.label)}">
      <rect width="${BW}" height="${BH}" rx="12" class="dg-box"/>
      ${s.id === current ? `<rect x="-5" y="-5" width="${BW + 10}" height="${BH + 10}" rx="16" class="dg-halo"/>` : ""}
      ${words.map((w, i) => `<text x="14" y="${(words.length === 1 ? 27 : 21) + i * 16}" class="dg-t1">${esc(w)}</text>`).join("")}
      <text x="14" y="${BH - 10}" class="dg-t2">${esc(s.more || "")}</text>
      ${doneSet.has(s.id) ? `<circle cx="${BW - 14}" cy="14" r="8" class="dg-tick"/><path d="M${BW - 18} 14 l3 3 6 -6" class="dg-tickmark"/>` : ""}
      ${s.id === current ? `<text x="${BW - 12}" y="17" text-anchor="end" class="dg-nowt">now</text>` : ""}
    </g>`);
  });
  parts.push("</svg>");
  return parts.join("");
}

function wrap(text, width) {
  const words = String(text).split(/\s+/);
  const out = [];
  let line = "";
  for (const w of words) {
    if ((line + " " + w).trim().length > width && line) { out.push(line); line = w; } else line = (line + " " + w).trim();
  }
  if (line) out.push(line);
  if (out.length > 2) { out.length = 2; out[1] = `${out[1].replace(/.{0,1}$/, "")}…`; }
  return out;
}
