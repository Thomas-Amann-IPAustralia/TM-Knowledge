/* For nerds: how it works, all the way down (ADR-0151).

   The owner's door for the technically curious: the knowledge map, the standards, the data tables,
   the current results and limits, and the glossary, with How it works and Rules as code beside
   them. Technical words are allowed here, and each is still explained the first time it is used
   (ADR-0145). Every figure is read from the build. Classes are prefixed `nd-`. */

import { esc, fmt, load, legend } from "./app.js";
import { icon } from "./icons.js";
import { term } from "./glossary.js";
import { drawing } from "./illustrations.js";

const DOORS = [
  ["#/how", "n-how", "A search, step by step", "A worked example: one research question followed through the search in nine steps, from the text, to the ideas and connections, to an answer with its quotations and who wrote what."],
  ["#/map", "n-map", "The knowledge map", "Every idea and every connection on one interactive map. Focus an idea to see its labelled connections and the passages it rests on."],
  ["#/rules", "n-rules", "Rules as code", "How a section of the Act becomes structured data: conditions joined by all and any, effects, exceptions, and a process as steps."],
  ["#/standards", "n-standards", "The standards", "What the graph is written in, each standard in plain words with a real block of this build, and why no reasoning profile is claimed."],
  ["#/table", "n-tables", "Data tables", "The same records listed rather than drawn, filterable, each downloadable as CSV with who wrote every row."],
  ["#/about", "n-results", "Current results and limits", "How the search was measured, in both directions, the decisions still ahead and whose they are, and the limits of this build."],
  ["#/glossary", "n-glossary", "Glossary", "Every technical term on the site, in plain words, with what it does here."],
];

export async function render(root, { ontology }) {
  const build = await load("build");
  const g = build.graph || {};
  const graphs = g.graphs || {};
  const triples = Object.values(graphs).reduce((n, x) => n + (x.triples || 0), 0);
  const shapes = Object.values(build.checks?.shapes || {}).reduce((n, x) => n + x, 0);
  const rules = (build.checks?.rules || []).length;
  const deps = build.dependencies || {};
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine, relations = c.relations.signed + c.relations.machine;

  root.innerHTML = `
  <div class="nd">
    <section class="nd-hero">
      <div class="wrap nd-hero-in">
        <div>
          <span class="eyebrow">For nerds</span>
          <h1>How it works, all the way down</h1>
          <p class="lede">Fair warning: this part is mostly for the technically minded. It describes the records and methods behind the demonstrations, along with their known limits.</p>
        </div>
        <dl class="nd-stats">
          <div><dt>${fmt(triples)}</dt><dd>${term("triple", "statements")} in the graph</dd></div>
          <div><dt>${fmt(Object.keys(graphs).length)}</dt><dd>${term("named-graph", "named graphs")}, keeping what a machine wrote apart from what a person signed</dd></div>
          <div><dt>${fmt(shapes)}</dt><dd>${term("shacl", "SHACL")} checks every build must pass, and ${fmt(rules)} ${term("inference-rule", "inference rules")}</dd></div>
          <div><dt>${fmt(deps.dependencies || 0)}</dt><dd>recorded dependencies of ${fmt(deps.records || 0)} records on ${fmt(deps.refs || 0)} passages and provisions</dd></div>
        </dl>
      </div>
    </section>
    <div class="wrap nd-body">
      <section class="nd-how" aria-labelledby="nd-how-h">
        <div class="nd-how-head"><span class="eyebrow">How the foundation works</span>
          <h2 id="nd-how-h">From the law’s words to tools that can explain themselves</h2>
          <p>The foundation turns legislation and examination guidance into linked records that tools can read. Each record keeps its source and its review status. Different tools can then explain, research or trace the same material.</p></div>
        <ol class="nd-flow">
          <li><span class="nd-fn">1</span><h3>Sources</h3><p>The Trade Marks Act 1995 and the Regulations, which are law, and the Trade Marks Manual, which is practice. Each keeps its own mark.</p>${legend()}</li>
          <li><span class="nd-fn">2</span><h3>Ideas, connections and rules</h3><p>${fmt(concepts)} ideas, ${fmt(relations)} connections between them, and ${fmt(c.tests)} legal tests and ${fmt(c.processes)} procedures set out as conditions and steps.</p></li>
          <li><span class="nd-fn">3</span><h3>Traceable records</h3><p>Every record quotes the words it rests on and says who wrote it. ${fmt(deps.dependencies || 0)} recorded dependencies show what rests on each passage.</p></li>
          <li><span class="nd-fn">4</span><h3>Tools</h3><p>Research for examiners, explanations for the public and change tracing for policy, all reading the same records.</p>
            <p class="nd-flow-go"><a href="#/examiners">Examiners</a><a href="#/public">The public</a><a href="#/direction">Policy and strategy</a></p></li>
        </ol>
      </section>
      <div class="nd-grid">${DOORS.map(([href, art, title, text]) => `<a class="nd-door" href="${href}">
        <div class="nd-door-art">${drawing(art)}</div>
        <div class="nd-door-body"><h2>${esc(title)}</h2><p>${esc(text)}</p><span class="link-arrow">Open ${icon("arrow")}</span></div></a>`).join("")}</div>
      <p class="tiny nd-built">Built ${esc(build.generated || "")} from the repository at ${esc(String(build.revision || "").slice(0, 12))} and the Manual snapshot ${esc(String(g.upstream?.commit || "").slice(0, 12))}. ${fmt(ontology.counts.concepts.signed + ontology.counts.concepts.machine)} ideas, ${fmt(ontology.counts.relations.signed + ontology.counts.relations.machine)} connections.</p>
    </div>
  </div>`;
}
