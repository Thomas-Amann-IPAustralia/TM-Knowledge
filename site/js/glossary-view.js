/* The glossary: every term the site explains, from the one dictionary in glossary.js, grouped
   by what it is about and filterable as you type. `#/glossary/<term>` opens at that term, which
   is where every inline explanation links. Classes: `gv-`. */

import { esc } from "./app.js";
import { GLOSSARY } from "./glossary.js";
import { icon } from "./icons.js";

/** The groups the terms are shown in. A term in none of them is listed under "Other terms". */
const GROUPS = [
  ["The idea", "What the ontology is and what it is made of.", ["ontology", "knowledge-graph", "concept", "kind", "connection", "modality", "rules-as-code"]],
  ["Trust", "How the site says who wrote what, and what it rests on.", ["provenance", "unreviewed", "snapshot", "dependency-index"]],
  ["Search and measurement", "How questions are answered, and how well that was measured.", ["llm", "keyword-search", "embedding", "ndcg", "interval"]],
  ["The standards", "What the graph is written in; each also has a page of its own.", ["rdf", "triple", "iri", "named-graph", "skos", "shacl", "sparql", "inference-rule", "prov-o", "json", "owl", "legalruleml"]],
];

export async function render(root, { params }) {
  const listed = new Set(GROUPS.flatMap(([, , keys]) => keys));
  const rest = Object.keys(GLOSSARY).filter((k) => !listed.has(k)).sort((a, b) => GLOSSARY[a].label.localeCompare(GLOSSARY[b].label));
  const groups = [...GROUPS.map(([title, text, keys]) => [title, text, keys.filter((k) => GLOSSARY[k])]), ...(rest.length ? [["Other terms", "", rest]] : [])];
  const total = Object.keys(GLOSSARY).length;

  root.innerHTML = `
  <div class="gv">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">Under the hood · plain words</span>
        <h1>Glossary</h1>
        <p class="lede">Every term the site uses, in three parts: what it means in plain words, what it does here, and what it is called
        technically. No term is assumed known.</p>
      </div>
    </header>
    <div class="wrap">
      <div class="gv-bar">
        <label class="gv-find">${icon("search")}<input type="search" placeholder="Find a term" aria-label="Find a term" autocomplete="off"></label>
        <nav class="gv-jump" aria-label="Groups">${groups.map(([title], i) => `<button type="button" class="chip" data-g="${i}">${esc(title)}</button>`).join("")}</nav>
        <span class="tiny gv-count" aria-live="polite">${total} terms</span>
      </div>
      ${groups.map(([title, text, keys], i) => `<section class="gv-group" id="gv-g${i}" tabindex="-1">
        <div class="gv-gh"><h2>${esc(title)}</h2>${text ? `<p class="muted small">${esc(text)}</p>` : ""}</div>
        <div class="gv-grid">${keys.map((key) => entry(key)).join("")}</div></section>`).join("")}
      <p class="empty gv-none" hidden>No term matches. Try a shorter word.</p>
    </div>
  </div>`;

  const find = root.querySelector(".gv-find input");
  const cards = [...root.querySelectorAll(".gv-entry")];
  find.addEventListener("input", () => {
    const q = find.value.trim().toLowerCase();
    let n = 0;
    for (const c of cards) { const show = !q || c.dataset.text.includes(q); c.hidden = !show; if (show) n++; }
    root.querySelectorAll(".gv-group").forEach((g) => { g.hidden = !g.querySelector(".gv-entry:not([hidden])"); });
    root.querySelector(".gv-none").hidden = n > 0;
    root.querySelector(".gv-count").textContent = q ? `${n} of ${cards.length} terms` : `${cards.length} terms`;
  });
  root.querySelector(".gv-jump").addEventListener("click", (e) => {
    const b = e.target.closest("[data-g]");
    if (!b) return;
    const target = root.querySelector(`#gv-g${b.dataset.g}`);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    target.focus({ preventScroll: true });
  });
  // opened at a term: scroll to it and mark it
  const at = params[0] && root.querySelector(`#term-${CSS.escape(params[0])}`);
  if (at) requestAnimationFrame(() => { at.scrollIntoView({ block: "center" }); at.classList.add("on"); });
}

function entry(key) {
  const e = GLOSSARY[key];
  return `<article class="gv-entry" id="term-${esc(key)}" data-text="${esc(`${e.label} ${e.plain} ${e.here} ${e.technical}`.toLowerCase())}">
    <h3>${esc(e.label)}</h3>
    <p class="gv-plain">${esc(e.plain)}</p>
    <p class="small"><span class="gv-k">Here</span>${esc(e.here)}</p>
    <p class="tiny"><span class="gv-k">Technically</span>${esc(e.technical)}</p>
  </article>`;
}
