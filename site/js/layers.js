/* The site's four layers, outcomes first and the ontology last (ADR-0145, redesigned in ADR-0148).

   The deeper a reader goes, the more operational the detail: what the proof of concept does
   today, what it could enable, how it works (the rules as code and the knowledge map that make
   the outcomes possible), and what it is made of underneath. Every route belongs to one layer,
   and a card at the foot of each page leads one layer deeper. "Where it stands" (#/about) sits
   across them all. */

import { esc } from "./app.js";
import { icon } from "./icons.js";

export const LAYERS = [
  { depth: 1, id: "does", label: "What it does", href: "#/", routes: ["", "ask", "customers", "change"] },
  { depth: 2, id: "could", label: "What it could do", href: "#/future", routes: ["future", "whatif"] },
  { depth: 3, id: "how", label: "How it works", href: "#/how", routes: ["how", "map", "rules"] },
  { depth: 4, id: "under", label: "Technical reference", href: "#/standards", routes: ["standards", "glossary", "table"] },
];

/** The cross-cutting page: status, measurement, limits and the gates ahead. */
export const ACROSS = { label: "Results and limits", href: "#/about", routes: ["about"] };

export const layerOf = (name) => LAYERS.find((l) => l.routes.includes(name || "")) || null;

/** Which header link a route lights up. */
const OWNER = { rules: "how", standards: "how", glossary: "how", table: "map", whatif: "future" };
export const navOwner = (name) => (name in OWNER ? OWNER[name] : name === "about" ? null : name);

/** Where each page leads next: one layer deeper, with what the reader will find there. */
const NEXT = {
  ask: { title: "How did it find those passages?", text: "Follow an example from the words in the question to the passages in the results.",
    links: [["#/how", "See how it works", "primary"], ["#/map", "Explore the knowledge map"]] },
  customers: { title: "How does the tool break down a legal rule?", text: "See who acts, which conditions must be met and which exceptions apply. Each part links to a source.",
    links: [["#/rules", "See the rules as code", "primary"], ["#/how", "How it works"]] },
  change: { title: "How does the tool find records to review?", text: "Each record stores a quotation and a way to detect changes to the source text. Editors can use these links to find records to review.",
    links: [["#/how", "See how it works", "primary"], ["#/map", "Explore the knowledge map"]] },
  future: { title: "What do the tools have in common?", text: "They use the same trade mark terms, links and sources.",
    links: [["#/how", "See how it works", "primary"], ["#/about", "Results and limits"]] },
  whatif: { title: "How do you find guidance for a policy review?", text: "Follow a link from a policy question to the records and source passages it might affect.",
    links: [["#/how", "See how it works", "primary"], ["#/change", "Trace a change"]] },
  how: { title: "Explore the technical details", text: "See how the project stores its records, browse the data tables or look up a term.",
    links: [["#/standards", "The standards", "primary"], ["#/table", "Data tables"], ["#/glossary", "Glossary"]] },
  rules: { title: "Explore the terms used in the rules", text: "Every idea, its kind and its connections, on one interactive map.",
    links: [["#/map", "Explore the knowledge map", "primary"], ["#/standards", "The standards"]] },
  standards: { title: "Look up a technical term", text: "The glossary explains each term and gives an example of how the project uses it.",
    links: [["#/glossary", "Read the glossary", "primary"], ["#/about", "Results and limits"]] },
  glossary: { title: "Results and limits", text: "See the search test results, the limits of the prototype and the decisions still to make.",
    links: [["#/about", "Results and limits", "primary"], ["#/standards", "The standards"]] },
  table: { title: "View these records on the map", text: "The knowledge map draws every idea and connection; select one to read its card.",
    links: [["#/map", "Explore the knowledge map", "primary"], ["#/standards", "The standards"]] },
  about: { title: "Try the tools", text: "Search the Manual and legislation, explore an example application or find records to review after a change.",
    links: [["#/ask", "Research a question", "primary"], ["#/", "Overview"]] },
};

/** The card at the foot of a page: one layer deeper, and the way back up. */
export function goDeeper(name) {
  const next = NEXT[name];
  if (!next) return "";
  const here = layerOf(name);
  const target = layerOf(next.links[0][0].replace(/^#\/?/, "").split("/")[0]);
  const k = target?.label || "Explore another tool";
  return `<aside class="wrap next" aria-label="Where to go next">
    <div class="next-in">
      <div><span class="eyebrow">${esc(k)}</span><h3>${esc(next.title)}</h3><p>${esc(next.text)}</p></div>
      <div class="next-links">${next.links.map(([href, label, kind]) => `<a class="btn ${kind === "primary" ? "lime" : "on-dark"}" href="${href}">${esc(label)} ${icon("arrow")}</a>`).join("")}</div>
    </div>
    ${here && here.depth > 1 ? `<p class="next-up">Or step back to <a href="${LAYERS[here.depth - 2].href}">${esc(LAYERS[here.depth - 2].label.toLowerCase())}</a>.</p>` : ""}
  </aside>`;
}
