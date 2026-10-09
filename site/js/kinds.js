/* The ten kinds of idea as one SVG picture: three family zones, a bubble per
   kind, and the strongest kind-to-kind patterns as arrows. Used by the tour; the
   map draws the same level with Cytoscape. `kind_links` is computed by
   tmk-explorer from the relationship records. */

import { kindColour } from "./app.js";
import { svg, curve, wrapText } from "./graph.js";

export const W = 1000, H = 660;
// A kind says what an idea is; what it does is an arrow (ruling B1, ADR-0126).
export const KIND_POS = {
  legal_test: { x: 150, y: 230 }, ground_of_refusal: { x: 150, y: 470 },
  context: { x: 395, y: 175 }, sign_content: { x: 395, y: 385 },
  subject_matter: { x: 570, y: 265 }, use_in_trade: { x: 575, y: 545 },
  process_role: { x: 770, y: 185 }, procedural_step: { x: 905, y: 300 },
  instrument_or_record: { x: 790, y: 440 }, external_instrument: { x: 905, y: 575 },
  none_of_these: { x: 150, y: 600 },
};
export const ZONES = [
  { family: "reasoning", x: 20, y: 80, w: 265, h: 455, label: "The questions the law asks" },
  { family: "examined", x: 300, y: 80, w: 355, h: 565, label: "What they are asked about" },
  { family: "process", x: 670, y: 80, w: 310, h: 565, label: "The process around them" },
];
export const LOOSE = new Set(["related", "broader"]);

export const kindRadius = (k) => 24 + 7 * Math.sqrt(k.signed + k.machine);
export const specificCount = (row) => row.total - (row.predicates.related || 0) - (row.predicates.broader || 0);

/** Draw the kinds level into `g`. Used by the map and by the tour. */
export function drawKinds(g, ontology, { strongOnly = true, onKind = null, onLink = null, minimal = false } = {}) {
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  if (!minimal) {
    for (const z of ZONES) {
      svg("rect", { x: z.x, y: z.y, width: z.w, height: z.h, rx: 18, class: "family-zone" }, g);
      svg("text", { x: z.x + 16, y: z.y + 24, class: "family-label" }, g).textContent = z.label;
    }
  }
  const links = svg("g", {}, g);
  const labels = svg("g", {}, g);
  const within = new Map();
  for (const row of ontology.kind_links) {
    if (row.s === row.o) { within.set(row.s, row); continue; }
    const strong = specificCount(row);
    if (strongOnly && strong < 5) continue;
    const a = KIND_POS[row.s], b = KIND_POS[row.o];
    const ka = kinds.get(row.s), kb = kinds.get(row.o);
    const c = curve(a, b, kindRadius(ka) + 4, kindRadius(kb) + 8, 0.12);
    const width = 1 + 1.5 * Math.log2(1 + (strongOnly ? strong : row.total));
    const path = svg("path", { d: c.d, class: "kind-link", "stroke-width": width.toFixed(1), "marker-end": "url(#arrow)", "data-s": row.s, "data-o": row.o }, links);
    const top = Object.entries(row.predicates).find(([p]) => !LOOSE.has(p)) || Object.entries(row.predicates)[0];
    const name = ontology.predicates[top[0]]?.label || top[0];
    svg("title", {}, path).textContent = `${ka.label} → ${kb.label}: ${row.total} connections`;
    if (strong >= 8 || (!strongOnly && !minimal && row.total >= 12)) {
      svg("text", { x: c.mx.toFixed(1), y: (c.my + 4).toFixed(1), class: "kind-link-label" }, labels).textContent = `${name} · ${top[1]}`;
    }
    if (onLink) path.addEventListener("click", () => onLink(row));
  }
  for (const k of ontology.kinds) {
    const at = KIND_POS[k.id];
    const r = kindRadius(k);
    const node = svg("g", { class: "kind-bubble", transform: `translate(${at.x},${at.y})`, style: `--c:${kindColour(k.id)}`, tabindex: 0, role: "button", "aria-label": `${k.label}: ${k.signed + k.machine} ideas`, "data-kind": k.id }, g);
    svg("circle", { r, class: "body" }, node);
    const lines = wrapText(k.label, 12, 2);
    lines.forEach((line, i) => {
      svg("text", { y: (i - (lines.length - 1) / 2) * 16 - 2, class: "name" }, node).textContent = line;
    });
    const inner = within.get(k.id);
    svg("text", { y: r + 15, class: "count" }, node).textContent =
      `${k.signed + k.machine} ideas` + (inner ? ` · ${inner.total} link${inner.total === 1 ? "" : "s"} inside` : "");
    svg("title", {}, node).textContent = `${k.label} — ${k.plain}`;
    if (onKind) {
      node.addEventListener("click", () => onKind(k));
      node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onKind(k); } });
    }
  }
}
