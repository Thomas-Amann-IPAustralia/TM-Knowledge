/* The site's four layers, outcomes first and the ontology last (ADR-0144).

   The deeper a reader goes, the more operational the detail: what the proof of concept does
   today, what it could enable, the rules as code that make those outcomes possible, and the
   conceptual model (the ontology) those rules build. Every route belongs to one layer; the
   depth strip under the header says which, and a card at the foot of each page leads one layer
   deeper. "Where it stands" (#/about) sits across them all. */

import { esc } from "./app.js";

export const LAYERS = [
  { depth: 1, id: "does", label: "What it does", href: "#/", routes: ["", "ask", "change", "customers"],
    question: "What the proof of concept does today, and how well",
    deeper: "See what the same foundations could enable later, what each would still need, and what may be tested with customers." },
  { depth: 2, id: "could", label: "What it could do", href: "#/future", routes: ["future"],
    question: "What it could enable, and what each would need",
    deeper: "See the rules as code that make these outcomes possible: legal tests, conditions and procedures as data a program can read." },
  { depth: 3, id: "rules", label: "Rules as code", href: "#/rules", routes: ["rules"],
    question: "What makes those outcomes possible",
    deeper: "See the conceptual model the rules are built from: the ideas, their kinds and connections, and the standards it is stored in." },
  { depth: 4, id: "model", label: "The ontology", href: "#/model", routes: ["model", "map", "circles", "table", "tour", "standards", "glossary"],
    question: "The conceptual model underneath, and the standards it uses",
    deeper: "" },
];

/** The cross-cutting page: status, measurement, limits and the gates ahead. */
export const ACROSS = { label: "Where it stands", href: "#/about", routes: ["about"] };

export const layerOf = (name) => LAYERS.find((l) => l.routes.includes(name || "")) || null;

/** The strip under the header: four steps, the current one marked, each a link. */
export function depthStrip(name) {
  const here = layerOf(name);
  return `<ol class="depth-steps">${LAYERS.map((l) => `
    <li class="${here && l.depth === here.depth ? "on" : ""}${here && l.depth < here.depth ? " above" : ""}">
      <a href="${l.href}"${here && l.depth === here.depth ? ` aria-current="step"` : ""}>
        <span class="d-n" aria-hidden="true">${l.depth}</span><span class="d-t">${esc(l.label)}</span></a></li>`).join("")}
    </ol>
    <span class="depth-axis" aria-hidden="true">outcomes <i></i> operational detail</span>`;
}

/** The card at the foot of a page: one layer deeper, and the way back up. */
export function goDeeper(name) {
  const here = layerOf(name);
  if (!here) {
    return `<aside class="deeper card"><p class="small">Start from what it does: <a href="#/">the proof of concept's outcomes</a>,
      then go deeper one layer at a time.</p></aside>`;
  }
  const next = LAYERS.find((l) => l.depth === here.depth + 1);
  const up = LAYERS.find((l) => l.depth === here.depth - 1);
  return `<aside class="deeper card" aria-label="Where to go next">
    ${next ? `<a class="deeper-next" href="${next.href}"><span class="k">Go deeper · layer ${next.depth} of ${LAYERS.length}</span>
      <b>${esc(next.label)}</b><span>${esc(here.deeper)}</span><span class="go" aria-hidden="true">→</span></a>`
      : `<div class="deeper-next"><span class="k">The deepest layer</span><b>That is the whole stack.</b>
      <span>For the state of every part, the measurement and the limits, see <a href="${ACROSS.href}">${esc(ACROSS.label)}</a>.</span></div>`}
    ${up ? `<p class="tiny">Or step back up to <a href="${up.href}">${esc(up.label)}</a>.</p>` : ""}
  </aside>`;
}
