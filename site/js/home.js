/* Home — what this is, in one screen, and three ways in. */

import { esc, fmt, load } from "./app.js";

export async function render(root, { ontology }) {
  const stability = await load("stability");
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;
  const kinds = ontology.kinds.filter((k) => k.id !== "none_of_these").length;
  const passages = stability.pages.reduce((n, p) => n + p.passages, 0);
  const firstYear = Object.keys(stability.by_year)[0];

  root.innerHTML = `
  <div class="wrap">
    <section class="hero">
      <div>
        <p class="step-k">A demonstration for trade marks examiners</p>
        <h1>The Manual, as a map of the ideas you reason with</h1>
        <p class="lede">The Trade Marks Manual is written as ${fmt(passages)} passages of practice, beside the Act and the
        Regulations. This map connects them through ${fmt(concepts)} ideas — the grounds, tests, factors, roles and steps
        examiners work with — so a question can follow the connections between ideas, not just the words on the page.</p>
        <div class="actions">
          <a class="btn primary" href="#/tour">Take the tour · 3 minutes</a>
          <a class="btn" href="#/ask">Ask the Manual</a>
          <a class="btn" href="#/map">Explore the map</a>
        </div>
        <p class="tiny">An ontology is this structure: a shared, explicit list of the ideas in a field, what kind of thing each one is,
        and how they relate — each one tied to the text it comes from.</p>
      </div>
      <div>
        <div class="ladder" aria-label="The map at four levels of detail">
          ${rung("map/kinds", kinds, "Kinds of idea", "Grounds, tests, factors and exceptions; roles, steps, records. Rest on no single passage.", 1)}
          ${rung("map/ideas", concepts, "Ideas", `${c.concepts.signed} signed by an expert, ${c.concepts.machine} written by a machine. Each sorted into a kind.`, 2)}
          ${rung("map/ideas", relations, "Connections", "How one idea bears on another — each pinned to the sentence it rests on.", 3)}
          ${rung("map/text", passages, "Passages of text", `The Manual's own words, with the Act and Regulations kept apart. ${fmt(stability.events)} recorded amendments since ${esc(firstYear)}.`, 4)}
        </div>
        <div class="rung-axis"><span>↑ changes rarely</span><span>changes often ↓</span></div>
      </div>
    </section>

    <section class="doors">
      <a class="door card" href="#/tour">
        <span class="k">Start here</span><h3>Why an ontology?</h3>
        <p>Seven short steps: the same idea in different words, ideas that connect, kinds of idea, and what happens when the Manual changes.</p>
        <span class="go">Take the tour →</span>
      </a>
      <a class="door card" href="#/ask">
        <span class="k">Try it</span><h3>Ask the Manual</h3>
        <p>Ask in your own words. Watch the question find its ideas, follow their connections and gather the passages — then read a cited answer.</p>
        <span class="go">Ask a question →</span>
      </a>
      <a class="door card" href="#/map">
        <span class="k">Look around</span><h3>The map, at any level</h3>
        <p>Start from nine kinds of idea, open one into its ideas, and open an idea into the passages and provisions it rests on.</p>
        <span class="go">Explore →</span>
      </a>
      <a class="door card" href="#/change">
        <span class="k">The long game</span><h3>When the text changes</h3>
        <p>Pick any page of the Manual and see exactly which connections would need re-checking if it were rewritten — and what would not move.</p>
        <span class="go">See the ripple →</span>
      </a>
    </section>
  </div>`;
}

function rung(href, n, title, text, level) {
  return `<a class="rung" href="#/${href}" data-level="${level}">
    <span class="n num">${fmt(n)}</span>
    <span class="t"><b>${esc(title)}</b><span>${esc(text)}</span></span>
    <span class="go" aria-hidden="true">→</span>
  </a>`;
}
