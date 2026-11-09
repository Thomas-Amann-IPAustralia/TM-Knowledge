/* The site's sections: an overview, one section for each group the knowledge foundation serves,
   and one for the technically curious (ADR-0151, on the owner's word, replacing the four layers
   of ADR-0145 and ADR-0148).

   Outcomes still come first and the ontology last: each audience section leads with what works
   today and what could come next, and how it works is kept for "For nerds". Every route belongs to
   one section, and a card at the foot of each page says where to go next. */

import { esc } from "./app.js";
import { icon } from "./icons.js";

export const SECTIONS = [
  { id: "home", label: "Overview", href: "#/", routes: [""] },
  { id: "examiners", label: "For examiners", href: "#/examiners", routes: ["examiners", "concepts", "ask"] },
  { id: "public", label: "For the public", href: "#/public", routes: ["public", "customers"] },
  { id: "direction", label: "For direction setting", href: "#/direction", routes: ["direction", "change", "whatif"] },
  { id: "nerds", label: "For nerds", href: "#/nerds", routes: ["nerds", "how", "map", "rules", "standards", "glossary", "table", "about"] },
];

export const sectionOf = (name) => SECTIONS.find((s) => s.routes.includes(name || "")) || SECTIONS[0];

/** Which header link a route lights up: its section's. */
export const navOwner = (name) => { const s = sectionOf(name); return s.id === "home" ? "" : s.id; };

const NERDS = ["#/nerds", "How it works, for nerds"];

/** Where each page leads next. */
const NEXT = {
  examiners: { title: "Curious how it works?", text: "The technical detail is kept in one place: the knowledge map, the rules as code, the standards and the test results.",
    links: [NERDS, ["#/public", "See what it offers the public"], ["#/direction", "See what it offers direction setting"]] },
  concepts: { title: "Ask a question in your own words", text: "The research assistant finds the law and the guidance for a question, then writes a cited answer you can check.",
    links: [["#/ask", "Ask a research question"], ["#/examiners", "Back to the examiners' overview"]] },
  ask: { title: "Explore one concept in depth", text: "See what the foundation records about one idea: what gives rise to it, what qualifies it, which exceptions may be relevant, and the sources for each.",
    links: [["#/concepts", "Explore a legal concept"], ["#/how", "A search, step by step"]] },
  public: { title: "Curious how it works?", text: "The technical detail is kept in one place: how a rule becomes structured data, the knowledge map and the standards behind it.",
    links: [NERDS, ["#/examiners", "See what it offers examiners"], ["#/direction", "See what it offers direction setting"]] },
  customers: { title: "How is a rule broken down?", text: "See how a section of the Act becomes structured data: who acts, which conditions must hold and which exceptions apply.",
    links: [["#/rules", "See the rules as code"], ["#/public", "Back to the public overview"]] },
  direction: { title: "Curious how it works?", text: "The technical detail is kept in one place: how records are linked to their sources, the knowledge map and the standards behind it.",
    links: [NERDS, ["#/examiners", "See what it offers examiners"], ["#/public", "See what it offers the public"]] },
  change: { title: "Try a bigger change", text: "See what an invented new right, a register of geographical indications, would touch in today's examination practice.",
    links: [["#/whatif", "A new right: what would it touch?"], ["#/direction", "Back to direction setting"]] },
  whatif: { title: "Trace one provision", text: "Choose any section of the Act, a regulation or a Manual page, and see the records linked to it.",
    links: [["#/change", "Trace a change"], ["#/direction", "Back to direction setting"]] },
  nerds: { title: "Back to what it does", text: "See what the foundation offers each group, with working demonstrations.",
    links: [["#/examiners", "For examiners"], ["#/public", "For the public"], ["#/direction", "For direction setting"]] },
  how: { title: "Explore the knowledge map", text: "Every idea and connection on one interactive map: select one to read its card.",
    links: [["#/map", "Open the knowledge map"], ["#/standards", "The standards"], ["#/rules", "Rules as code"]] },
  rules: { title: "Explore the ideas the rules use", text: "Every idea, its kind and its connections, on one interactive map.",
    links: [["#/map", "Open the knowledge map"], ["#/standards", "The standards"]] },
  standards: { title: "Look up a technical term", text: "The glossary explains each term and gives an example of how the project uses it.",
    links: [["#/glossary", "Read the glossary"], ["#/about", "Results and limits"]] },
  glossary: { title: "Results and limits", text: "See the search test results, the limits of the prototype and the decisions still to make.",
    links: [["#/about", "Results and limits"], ["#/standards", "The standards"]] },
  table: { title: "View these records on the map", text: "The knowledge map draws every idea and connection; select one to read its card.",
    links: [["#/map", "Open the knowledge map"], ["#/standards", "The standards"]] },
  about: { title: "Try the demonstrations", text: "See what the foundation does for examiners, for the public and for direction setting.",
    links: [["#/examiners", "For examiners"], ["#/public", "For the public"], ["#/direction", "For direction setting"]] },
};

/** A breadcrumb above a deep page's title: its section, linked back, then the page, and what kind
    of page it is (UX review F29). It replaces the eyebrow, so the title area holds no more lines. */
export function crumb(sectionId, here, note = "") {
  const s = SECTIONS.find((x) => x.id === sectionId) || SECTIONS[0];
  return `<nav class="crumb" aria-label="Breadcrumb"><a href="${s.href}">${esc(s.label)}</a><span aria-hidden="true">/</span><span aria-current="page">${esc(here)}</span>${note ? `<span class="crumb-note">${esc(note)}</span>` : ""}</nav>`;
}

/** The card at the foot of a page: where to go next, and the way back to its section. */
export function goDeeper(name) {
  const next = NEXT[name];
  if (!next) return "";
  const here = sectionOf(name);
  return `<aside class="wrap next" aria-label="Where to go next">
    <div class="next-in">
      <div><span class="eyebrow">${esc(here.label)}</span><h3>${esc(next.title)}</h3><p>${esc(next.text)}</p></div>
      <div class="next-links">${next.links.map(([href, label], i) => `<a class="btn ${i === 0 ? "lime" : "on-dark"}" href="${href}">${esc(label)} ${icon("arrow")}</a>`).join("")}</div>
    </div>
  </aside>`;
}
