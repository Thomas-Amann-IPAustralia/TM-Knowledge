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
  { depth: 2, id: "could", label: "What it could do", href: "#/future", routes: ["future"] },
  { depth: 3, id: "how", label: "How it works", href: "#/how", routes: ["how", "map", "rules"] },
  { depth: 4, id: "under", label: "Under the hood", href: "#/standards", routes: ["standards", "glossary", "table"] },
];

/** The cross-cutting page: status, measurement, limits and the gates ahead. */
export const ACROSS = { label: "Where it stands", href: "#/about", routes: ["about"] };

export const layerOf = (name) => LAYERS.find((l) => l.routes.includes(name || "")) || null;

/** Which header link a route lights up. */
const OWNER = { rules: "how", standards: "how", glossary: "how", table: "map" };
export const navOwner = (name) => (name in OWNER ? OWNER[name] : name === "about" ? null : name);

/** Where each page leads next: one layer deeper, with what the reader will find there. */
const NEXT = {
  ask: { title: "How did it find those passages?", text: "Follow one question through the system: the words it recognised, the connections it followed, and the model of ideas underneath.",
    links: [["#/how", "See how it works", "primary"], ["#/map", "Explore the knowledge map"]] },
  customers: { title: "What lets it explain a provision this way?", text: "Each legal test is written as structured data: who acts, the conditions joined by all of and any of, the exceptions, each part quoting its source.",
    links: [["#/rules", "See the rules as code", "primary"], ["#/how", "How it works"]] },
  change: { title: "Why can it trace a change?", text: "Every idea, connection and test quotes the passage it rests on and keeps a fingerprint of it, so a change to the text points straight at what to re-check.",
    links: [["#/how", "See how it works", "primary"], ["#/map", "Explore the knowledge map"]] },
  future: { title: "What would all of this build on?", text: "One knowledge foundation: the ideas examiners reason with, how they connect, and the text each rests on.",
    links: [["#/how", "See how it works", "primary"], ["#/about", "Where it stands"]] },
  how: { title: "Go under the hood", text: "The open standards the graph is written in, each explained in plain words with a real block of this build, and every record as a table.",
    links: [["#/standards", "The standards", "primary"], ["#/table", "Data tables"], ["#/glossary", "Glossary"]] },
  rules: { title: "See the model the rules are built from", text: "Every idea, its kind and its connections, on one interactive map.",
    links: [["#/map", "Explore the knowledge map", "primary"], ["#/standards", "The standards"]] },
  standards: { title: "Every term, in plain words", text: "No standard's name is assumed known: the glossary says what each means, what it does here, and what it is called technically.",
    links: [["#/glossary", "Read the glossary", "primary"], ["#/about", "Where it stands"]] },
  glossary: { title: "Where it stands", text: "The measurement in both directions, what is still to be decided and by whom, and the limits.",
    links: [["#/about", "Where it stands", "primary"], ["#/standards", "The standards"]] },
  table: { title: "See the same records drawn", text: "The knowledge map draws every idea and connection; select one to read its card.",
    links: [["#/map", "Explore the knowledge map", "primary"], ["#/standards", "The standards"]] },
  about: { title: "Back to what it does", text: "Ask the Manual a question, see an explanation for a customer, or trace what a change would touch.",
    links: [["#/ask", "Research a question", "primary"], ["#/", "Overview"]] },
};

/** The card at the foot of a page: one layer deeper, and the way back up. */
export function goDeeper(name) {
  const next = NEXT[name];
  if (!next) return "";
  const here = layerOf(name);
  const target = layerOf(next.links[0][0].replace(/^#\/?/, "").split("/")[0]);
  const k = name === "about" || !target ? "Where to next" : target.depth > (here?.depth || 0)
    ? `Go deeper · layer ${target.depth} of ${LAYERS.length}: ${target.label.toLowerCase()}` : `Layer ${target.depth} of ${LAYERS.length}: ${target.label.toLowerCase()}`;
  return `<aside class="wrap next" aria-label="Where to go next">
    <div class="next-in">
      <div><span class="eyebrow">${esc(k)}</span><h3>${esc(next.title)}</h3><p>${esc(next.text)}</p></div>
      <div class="next-links">${next.links.map(([href, label, kind]) => `<a class="btn ${kind === "primary" ? "lime" : "on-dark"}" href="${href}">${esc(label)} ${icon("arrow")}</a>`).join("")}</div>
    </div>
    ${here && here.depth > 1 ? `<p class="next-up">Or step back to <a href="${LAYERS[here.depth - 2].href}">${esc(LAYERS[here.depth - 2].label.toLowerCase())}</a>.</p>` : ""}
  </aside>`;
}
