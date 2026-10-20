/* The ontology — layer 4 of 4 (ADR-0145): the conceptual model the rules are built from.

   The hub for the views that used to lead the site: the four levels of the model (kinds, ideas,
   connections, passages), and the ways in (the tour, the map, at a glance, as a table, the
   glossary). Every number is read from the generated data. */

import { esc, fmt, kindCount, load } from "./app.js";
import { term } from "./glossary.js";

export async function render(root, { ontology }) {
  const stability = await load("stability");
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;
  const passages = stability.pages.reduce((n, p) => n + p.passages, 0);
  const firstYear = Object.keys(stability.by_year)[0];

  root.innerHTML = `
  <div class="wrap model">
    <p class="step-k">Layer 4 of 4</p>
    <h1>The ontology underneath</h1>
    <p class="lede">The rules as code are built from a model of the ideas examiners reason with: an ${term("ontology")}. It names each
    idea once, says what kind of thing it is, connects it to the ideas it bears on, and ties every one of them to the text it comes
    from. It is stored as a ${term("knowledge-graph", "knowledge graph")}, so a program can follow the connections, and it is checked on every build.</p>

    <section class="levels" aria-label="The model at four levels of detail">
      ${rung("circles", kindCount(ontology), "Kinds of idea", "Grounds, tests and principles; what a mark contains and its context; roles, steps, records — and how each kind acts on the others.", 1)}
      ${rung("map/ideas", concepts, "Ideas", "Each sorted into a kind. Most were written by a machine and have not yet been reviewed.", 2)}
      ${rung("table/connections", relations, "Connections", "How one idea bears on another, each pinned to the sentence it rests on.", 3)}
      ${rung("change", passages, "Passages", `The Manual's words, the Act and Regulations kept apart. ${fmt(stability.events)} amendments since ${esc(firstYear)}.`, 4)}
    </section>
    <div class="levels-axis"><span>↑ changes rarely</span><span>changes often →</span></div>

    <section class="doors">
      <a class="door card" href="#/tour"><span class="k">Start here</span><h3>Why an ontology?</h3>
        <p>Seven short steps: the same idea in different words, ideas that connect, kinds of idea, and what happens when the Manual changes.</p><span class="go">Take the tour →</span></a>
      <a class="door card" href="#/map"><span class="k">Look around</span><h3>The map, at any level</h3>
        <p>Open a kind into its ideas, compare two kinds in detail with the rest in outline, and open an idea into the passages it rests on.</p><span class="go">Explore the map →</span></a>
      <a class="door card" href="#/circles"><span class="k">At a glance</span><h3>The whole model in one picture</h3>
        <p>Families of kinds, kinds, then ideas, as circles you can zoom into.</p><span class="go">See it at a glance →</span></a>
      <a class="door card" href="#/table"><span class="k">As tables</span><h3>Every record, listed</h3>
        <p>Kinds, ideas, connections, legal tests and processes, with who wrote each, and a download of every table.</p><span class="go">Open the tables →</span></a>
      <a class="door card" href="#/standards"><span class="k">Under the hood</span><h3>The standards it is written in</h3>
        <p>RDF, identifiers, named graphs, SKOS, SHACL, SPARQL and PROV-O, each in plain words with a real example from this build, and why no OWL profile is claimed.</p><span class="go">See the standards →</span></a>
      <a class="door card" href="#/glossary"><span class="k">Plain words</span><h3>Every term, explained</h3>
        <p>What an ontology, a knowledge graph, RDF, SKOS, SHACL, SPARQL or OWL is, and what each does here.</p><span class="go">Read the glossary →</span></a>
    </section>
  </div>`;
}

function rung(href, n, title, text, level) {
  return `<a class="rung" href="#/${href}" data-level="${level}">
    <span class="n num">${fmt(n)}</span>
    <span class="t"><b>${esc(title)}</b><span>${esc(text)}</span></span>
  </a>`;
}
