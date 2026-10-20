/* Drawings of the structured records (ADR-0142), shared by Rules as code and the customer preview.

   Two pictures, each with a text equivalent built from the same data, so the words and the
   picture cannot say different things: a legal test drawn as provision → conditions → effect →
   exceptions → routes, and a process drawn as its steps with every way on as an arrow. Neither
   evaluates a condition or computes a date; where the customer preview shows a recorded state, it
   is the explanation object's, read from `data/explain.json`. Every class is prefixed `dg-`
   (Q-101). */

import { esc, refChip, srcBadge } from "./app.js";

export const EFFECT_WORD = { obligation: "must", discretion: "may", bar: "may not" };
export const EFFECT_NAME = { obligation: "an obligation", discretion: "a discretion", bar: "a bar" };
const LEAF = { fact: "Fact", evaluative: "Assessment" };
const LEAF_LONG = { fact: "a fact about the application or the other trade mark", evaluative: "a person's assessment, never computed" };
/** A recorded state, by a mark and a word as well as a colour. */
export const STATE = { met: ["✓", "recorded as met"], not_met: ["✗", "recorded as not met"], open: ["?", "not established from the available facts"] };

const joinOf = (node) => (node.all ? "all" : node.any ? "any" : node.kind === "all" || node.kind === "any" ? node.kind : null);
const childrenOf = (node) => node.all || node.any || node.children || [];
const lower = (text) => String(text || "").replace(/^./, (c) => c.toLowerCase());

/** A condition tree as nested boxes. A leaf says whether it is a fact or a person's assessment;
    with `states`, a node also shows the state the explanation records for it. */
export function conditionBoxes(node, { states = false } = {}) {
  if (!node) return "";
  const join = joinOf(node);
  const mark = states && node.state ? stateMark(node.state) : "";
  if (join) {
    return `<div class="dg-group dg-${join}">
      <p class="dg-join">${mark}${join === "all" ? "All of these" : "Any one of these"}${node.text ? ` <span class="dg-gtext">${esc(node.text)}</span>` : ""}</p>
      <div class="dg-kids">${childrenOf(node).map((child) => conditionBoxes(child, { states })).join("")}</div></div>`;
  }
  return `<div class="dg-leaf dg-${esc(node.kind)}${states && node.state ? ` dg-s-${esc(node.state)}` : ""}">
    <span class="dg-kind"><i aria-hidden="true"></i>${esc(LEAF[node.kind] || node.kind)}</span>
    <p>${mark}${esc(node.text)}</p>
    ${states && node.why ? `<p class="dg-why">${esc(STATE[node.state]?.[1] || "")}: ${esc(node.why)}</p>` : ""}
    <p class="dg-ref">${refChip(node.ref)}</p></div>`;
}

export const stateMark = (state) => `<span class="dg-st dg-st-${esc(state)}" title="${esc(STATE[state]?.[1] || state)}"><span aria-hidden="true">${STATE[state]?.[0] || ""}</span><span class="vh">${esc(STATE[state]?.[1] || state)}: </span></span>`;

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

const flowArrow = (label) => `<div class="dg-arrow" aria-hidden="true"><span>${esc(label)}</span></div>`;

/** A structured legal test as a diagram, from its record (`ontology.structures.tests`). */
export function testDiagram(t) {
  const exceptions = t.exceptions || [];
  const routes = t.routes || [];
  return `<div class="dg-test" role="group" aria-label="${esc(t.title)}, drawn as a diagram; its text equivalent follows">
    <div class="dg-band dg-provision"><span class="dg-k">The provision</span>
      <p><b>${esc(t.title)}</b></p><p class="dg-ref">${refChip(t.provision)} ${srcBadge(t.provision)} <span class="tiny">Who acts: ${esc(t.actor)}</span></p></div>
    ${flowArrow("applies when")}
    <div class="dg-band dg-when"><span class="dg-k">The conditions</span>${conditionBoxes(t.condition)}</div>
    ${flowArrow("then")}
    <div class="dg-band dg-effect dg-e-${esc(t.effect.kind)}"><span class="dg-k">The effect</span>
      <p><span class="dg-modal">${esc(EFFECT_WORD[t.effect.kind] || t.effect.kind)}</span> ${esc(t.effect.text)}</p>
      <p class="dg-ref">${refChip(t.effect.ref)} <span class="tiny">${esc(EFFECT_NAME[t.effect.kind] || "")}</span></p></div>
    ${exceptions.length ? `${flowArrow("unless")}
    <div class="dg-band dg-unless"><span class="dg-k">The exceptions</span><div class="dg-cols">${exceptions.map((x) => `
      <div class="dg-exception"><p><b>${esc(x.text)}</b></p>
        ${conditionBoxes(x.condition)}
        <div class="dg-xeffect dg-e-${esc(x.effect.kind)}"><span class="dg-modal">${esc(EFFECT_WORD[x.effect.kind] || x.effect.kind)}</span>
          ${esc(x.effect.text)} <span class="tiny">(${esc(EFFECT_NAME[x.effect.kind] || "")})</span></div>
        <p class="dg-ref">${refChip(x.ref)}</p></div>`).join("")}</div></div>` : ""}
    ${routes.length ? `${flowArrow("what can be done")}
    <div class="dg-band dg-routes"><span class="dg-k">Routes the sources describe</span><ul>${routes.map((r) => `
      <li>${esc(r.text)} <span class="dg-ref">${refChip(r.ref)} ${srcBadge(r.ref)}</span></li>`).join("")}</ul></div>` : ""}
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

/** A process as a column of steps, each way on drawn as a numbered arrow on the right, so a
    branch back reads as plainly as one forward. A dashed arrow depends on something a matter
    must say. `steps`: {id, label, actor, kind, more}; `arcs`: {from, to, needs}. */
export function flowSvg({ id, title, steps, arcs, current = null, done = [] }) {
  const index = new Map(steps.map((s, i) => [s.id, i]));
  const boxW = 270, boxH = 46, gap = 20, left = 8;
  const width = left + boxW + 30 + 16 * arcs.length + 20;
  const height = 12 + steps.length * (boxH + gap);
  const outs = new Map(), ins = new Map();
  const doneSet = new Set(done);
  const desc = `Steps: ${steps.map((s) => s.label).join("; ")}. Ways on: ${arcs.map((a, k) => `${k + 1}. ${steps[index.get(a.from)].label} to ${steps[index.get(a.to)].label}`).join("; ")}.`;
  const parts = [`<svg class="dg-flow" viewBox="0 0 ${width} ${height}" style="max-width:${width}px" role="img" aria-labelledby="${id}-t ${id}-d">
    <title id="${id}-t">${esc(title)}</title><desc id="${id}-d">${esc(desc)}</desc>
    <defs><marker id="${id}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" class="dg-head"/></marker></defs>`];
  steps.forEach((s, i) => {
    const y = 6 + i * (boxH + gap);
    const cls = s.id === current ? "now" : doneSet.has(s.id) ? "done" : s.kind === "start" || s.kind === "end" ? "edge" : "";
    parts.push(`<rect x="${left}" y="${y}" width="${boxW}" height="${boxH}" rx="8" class="dg-box ${cls}"/>`,
      `<text x="${left + 10}" y="${y + 19}" class="dg-t1">${i + 1}. ${esc(s.label.length > 34 ? `${s.label.slice(0, 33)}…` : s.label)}</text>`,
      `<text x="${left + 10}" y="${y + 36}" class="dg-t2">${esc(s.more || "")}</text>`);
  });
  arcs.forEach((a, k) => {
    const o = outs.get(a.from) || 0, n = ins.get(a.to) || 0;
    outs.set(a.from, o + 1); ins.set(a.to, n + 1);
    const y1 = 6 + index.get(a.from) * (boxH + gap) + 9 + 7 * o;
    const y2 = 6 + index.get(a.to) * (boxH + gap) + boxH - 9 - 7 * n;
    const x = left + boxW + 22 + 16 * k;
    parts.push(`<path d="M${left + boxW} ${y1} H${x} V${y2} H${left + boxW + 4}" class="dg-line${a.needs ? " dashed" : ""}" marker-end="url(#${id}-arrow)"/>`,
      `<text x="${x + 3}" y="${(y1 + y2) / 2 + 3}" class="dg-n">${k + 1}</text>`);
  });
  parts.push("</svg>");
  return parts.join("");
}
