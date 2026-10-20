/* The standards — layer 4 of 4 (ADR-0145): what the graph is written in, for every reader.

   Each standard in the same three parts: a plain sentence, what it does here with a real example
   read from `build.json` (the release manifest, the checks and two blocks of the committed graph),
   and what it is not. No reader is assumed to know a standard's name: an executive and a data
   engineer should finish with the same picture. Every number is read from the data. */

import { esc, fmt, load } from "./app.js";
import { term, GLOSSARY } from "./glossary.js";

const GRAPH = {
  source: ["The source text", "The Manual's passages and the provisions of the Act and the Regulations, as the snapshot holds them."],
  approved: ["What a person approved", "Records a named expert reviewed and signed."],
  authored: ["What a machine wrote", "Ideas, connections, definitions, legal tests and process templates written by a model, every one unreviewed."],
  inferred: ["What a rule concluded", "Conclusions the inference rules drew, kept apart from what anyone wrote."],
};

export async function render(root) {
  const build = await load("build");
  const g = build.graph || {};
  const graphs = g.graphs || {};
  const triples = Object.values(graphs).reduce((n, x) => n + (x.triples || 0), 0);
  const checks = build.checks || { shapes: {}, rules: [] };
  const shapes = Object.values(checks.shapes).reduce((n, x) => n + x, 0);
  const sample = build.samples || {};
  const test = sample.test || {};
  const concept = sample.concept || {};
  const prefix = (s, p) => (s.prefixes || []).find((line) => line.startsWith(`@prefix ${p}:`))?.split(/\s+/)[2]?.replace(/[<>]/g, "") || "";
  const testIri = `${prefix(test, "tmka")}${(test.subject || "").replace(/^tmka:/, "")}`;
  const conceptIri = `${prefix(concept, "tmkc")}${(concept.subject || "").replace(/^tmkc:/, "")}`;
  const skosLines = (concept.lines || []).filter((line) => /skos:/.test(line));
  const approved = graphs.approved?.classes || {};

  root.innerHTML = `
  <div class="wrap standards">
    <p class="step-k">Layer 4 of 4 · the standards</p>
    <h1>What the graph is written in</h1>
    <p class="lede">The ontology is stored in open standards, so that any compatible tool can read it, check it and query it, and nothing
    depends on this site. Each is explained below in the same three parts: what it is in plain words, what it does here (with a real
    example from this build), and what it is not. No technical knowledge is assumed.</p>

    <nav class="sd-index card" aria-label="The standards on this page">${[["rdf", "RDF and triples"], ["iri", "Identifiers"], ["named-graph", "Named graphs"],
      ["skos", "SKOS"], ["shacl", "SHACL"], ["sparql", "SPARQL and rules"], ["prov-o", "PROV-O"], ["json", "JSON for this site"], ["owl", "OWL: why not"],
      ["legalruleml", "LegalRuleML: deferred"]].map(([id, label]) => `<a href="#sd-${id}" data-jump="sd-${id}">${esc(label)}</a>`).join("")}</nav>

    ${standard("rdf", "RDF and triples: facts as three-part statements", {
      here: `<p>Everything is written as ${term("triple", "triples")}: a thing, a relationship, and another thing or a value. This build's
        graph holds <b>${fmt(triples)}</b> of them. Here are the first lines of section 44's legal test as the committed file writes it
        (a format called Turtle; each line ending in ";" is one more statement about the same thing):</p>
        ${turtle(test)}
        <p class="small">Read the first line as "GL-0001 <i>is a</i> structured test", the next as "its label is …", and so on: who wrote it, when,
        why, its confidence, the evidence it quotes, and that it is <b>unreviewed</b>.</p>`,
      not: "Not a database product or a file format tied to one vendor. It is a W3C standard, and the same statements can be loaded into any RDF tool.",
    })}

    ${standard("iri", "Identifiers: one name for each thing, everywhere", {
      here: `<p>Every passage, provision, idea and record has a stable identifier, written as a web-address-like name. Section 44's test is
        <code>${esc(test.subject || "")}</code> for short, which stands for <code class="sd-wrap">${esc(testIri)}</code>; the idea
        <i>deceptively similar</i> is <code>${esc(concept.subject || "")}</code>, short for <code class="sd-wrap">${esc(conceptIri)}</code>.
        The short ids (GC-, GL-, GP-, TMA1995/s44) are the same ones used everywhere on this site and in the repository.</p>`,
      not: "Not a live web page: nothing is published at those addresses and nothing fetches them. Which address the project may use is still the project owner's decision.",
    })}

    ${standard("named-graph", "Named graphs: four compartments that never mix", {
      here: `<p>Every statement is filed in one of four compartments, so a question that asks only for what a person approved cannot reach what a
        machine wrote:</p>
        <div class="sd-scroll"><table class="sd-graphs"><thead><tr><th>Compartment</th><th>What it holds</th><th class="num">Statements</th><th>Review status</th></tr></thead>
        <tbody>${Object.entries(GRAPH).filter(([key]) => graphs[key]).map(([key, [label, text]]) => `<tr><td><b>${esc(label)}</b><br><code>${esc(key)}</code></td>
          <td class="small">${esc(text)}</td><td class="num">${fmt(graphs[key].triples)}</td>
          <td class="small">${Object.entries(graphs[key].review_status || {}).map(([s, n]) => `${fmt(n)} ${esc(s)}`).join(", ") || `<span class="muted">not applicable</span>`}</td></tr>`).join("")}</tbody></table></div>
        <p class="small">${esc(g.states || "")}</p>`,
      not: "Not a permission system: anyone with the files can read every compartment. What it guarantees is that a statement's origin is never lost or merged.",
    })}

    ${standard("skos", "SKOS: names for ideas, and which is a kind of which", {
      here: `<p>Each idea has one preferred name, the other names it goes by, and its "is a kind of" links, written with ${term("skos")}. The idea
        <i>deceptively similar</i>, as the graph writes those parts:</p>
        ${turtle({ ...concept, lines: skosLines })}
        <p class="small">That is how "objection" and "ground for rejection" can lead to the same idea, and how search recognises everyday words.</p>`,
      not: "Not a dictionary of legal meanings: a SKOS definition here is a machine-written record, stamped as unreviewed, and the Act's own definitions are quoted, never replaced.",
    })}

    ${standard("shacl", "SHACL: checks the graph must pass", {
      here: `<p>Written checks, like a form's validation rules, run on every build. There are <b>${fmt(shapes)}</b>
        (${Object.entries(checks.shapes).map(([name, n]) => `${esc(name)} ${fmt(n)}`).join(", ")}). For example: every machine-written record
        must name its author, date, evidence and review status; every part of a legal test must quote its source and say whether it is law or
        practice. A single defect fails the build, and every check has a deliberately broken example that must fail it.</p>`,
      not: "Not a check that the law has been read correctly. It checks that every record is complete and honest about its origin; whether its reading is right is for an expert.",
    })}

    ${standard("sparql", "SPARQL and rules: asking the graph, and drawing approved conclusions", {
      here: `<p>${term("sparql")} is the graph's query language, as SQL is a table's. It answers the
        ${fmt(approved.CompetencyQuestion || 0)} approved competency questions (questions the ontology must be able to answer), and it runs the
        ${term("inference-rule", "inference rules")}, each a query that writes its conclusions into the "what a rule concluded" compartment:</p>
        <ul class="small">${checks.rules.map((r) => `<li><b>${esc(r.id)}</b> ${r.approved ? "approved" : "not approved, so what it concludes is a candidate"}.
          ${r.limits ? `<span class="muted">Its own limits:</span> ${esc(r.limits)}` : ""}</li>`).join("")}</ul>`,
      not: "Not open-ended reasoning: only rules a person approved produce conclusions that may be relied on, and each states its own limits.",
    })}

    ${standard("prov-o", "PROV-O: who made what, from what, and when", {
      here: `<p>The model's record of origin builds on ${term("prov-o")}: a record is a kind of PROV entity, and "derived from" is PROV's own
        relationship, so a PROV-aware tool understands where each record came from. In the statements themselves this appears as the lines
        above: <code>tmk:authoredBy</code>, <code>tmk:authoredDate</code>, <code>tmk:evidence</code>, <code>tmk:reviewStatus</code>.</p>`,
      not: "Not a log of every edit. It records what each record rests on and who wrote it; the history of changes is in the repository.",
    })}

    ${standard("json", "JSON: how this site reads it", {
      here: `<p>This site does not query the graph directly. On every publish, the same records are written as ${term("json")} files that the browser
        reads: the ontology, the passages, the search index, the prepared answers, the customer preview and a release manifest
        (built ${esc(build.generated || "")} from revision <code>${esc((build.revision || "").slice(0, 12))}</code>). The release manifest names the
        snapshot (<code>${esc((g.upstream?.commit || "").slice(0, 12))}</code>), ${(build.law || []).map((l) => `${esc(l.line)} (compilation ${esc(l.compilation)})`).join(" and ")},
        and ${esc(build.manual?.line || "")}.</p>`,
      not: "Not a second source of truth: every JSON file is regenerated from the repository's records and is never edited by hand.",
    })}

    ${standard("owl", "OWL: why no OWL profile is claimed", {
      here: `<p>${term("owl")} lets a program draw logical conclusions automatically from class definitions. This model deliberately does not rely on
        it. Some OWL words label properties, but no OWL profile is claimed and no automatic OWL reasoning is run, because an unchecked machine
        conclusion about law could be mistaken for a fact. The release manifest says so in its own words:</p>
        <blockquote class="sd-profile">${esc(g.profile || "")}</blockquote>`,
      not: "Not a gap to be filled quietly. Claiming a profile, or running a reasoner, would be a recorded decision with its own checks.",
    })}

    ${standard("legalruleml", "LegalRuleML: deferred", {
      here: `<p>${term("legalruleml")} writes laws as executable rules, including exceptions that override one another. It is deferred: the legal tests
        on <a href="#/rules">Rules as code</a> are structured data that explain what a provision requires, not rules that run to a result.</p>`,
      not: "Not ruled out for ever; ruled out while the system must never state an examination outcome.",
    })}
  </div>`;
  root.querySelectorAll("[data-jump]").forEach((a) => a.addEventListener("click", (event) => {
    event.preventDefault();
    const target = root.querySelector(`#${a.dataset.jump}`);
    target.scrollIntoView({ block: "start" });
    target.focus({ preventScroll: true });
  }));
}

function standard(key, title, { here, not }) {
  const entry = GLOSSARY[key];
  return `<section class="sd card" id="sd-${esc(key)}" tabindex="-1">
    <h2>${esc(title)}</h2>
    <div class="sd-parts">
      <div><h3>In plain words</h3><p>${esc(entry.plain)}</p></div>
      <div class="sd-here"><h3>What it does here</h3>${here}</div>
      <div><h3>What it is not</h3><p>${esc(not)}</p></div>
    </div>
    <p class="tiny">Technically: ${esc(entry.technical)}</p>
  </section>`;
}

/** A block of the committed graph, as the file writes it. */
function turtle(block) {
  if (!block.lines?.length) return `<p class="tiny muted">This build carries no example.</p>`;
  return `<figure class="sd-turtle"><pre>${esc(block.lines.join("\n"))}</pre>
    <figcaption class="tiny">From the <b>${esc(block.graph)}</b> compartment of the committed graph${block.total > block.lines.length ? `, shortened (… marks a cut)` : ""}.</figcaption></figure>`;
}
