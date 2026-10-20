/* The standards: what the graph is written in, for every reader (layer 4, ADR-0145).

   A picture first: how the standards stack up, from the three-part statements at the bottom to the
   files this site reads at the top, with the four compartments drawn to scale from the release
   manifest. Then each standard in the same three parts: a plain sentence, what it does here with a
   real example read from `build.json` (the release manifest, the checks and two blocks of the
   committed graph), and what it is not. No reader is assumed to know a standard's name: an
   executive and a data engineer should finish with the same picture. Every number is read from
   the data. Classes: `sd-`. */

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
  const compartments = Object.entries(GRAPH).filter(([key]) => graphs[key]);

  root.innerHTML = `
  <div class="sd">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">Under the hood · the standards</span>
        <h1>What the graph is written in</h1>
        <p class="lede">The ontology is stored in open standards, so any compatible tool can read it, check it and query it, and nothing
        depends on this site. Each is explained in the same three parts: what it is in plain words, what it does here (with a real example
        from this build), and what it is not. No technical knowledge is assumed.</p>
      </div>
    </header>

    <div class="wrap">
      <figure class="card sd-stack" aria-label="How the standards fit together; select one to read about it">
        <div class="sd-layer top">${block("json", "JSON", "the files this site reads, written from the graph on every publish")}</div>
        <div class="sd-layer two">${block("sparql", "SPARQL", "questions to the graph, and the rules that draw conclusions")}${block("shacl", "SHACL", `${fmt(shapes)} checks every build must pass`)}</div>
        <div class="sd-layer two">${block("skos", "SKOS", "names for ideas, and which is a kind of which")}${block("prov-o", "PROV-O", "who made each record, from what, and when")}</div>
        <div class="sd-layer">
          <button type="button" class="sd-block sd-graphs-block" data-jump="sd-named-graph"><span class="sd-bk">Named graphs</span>
            <span class="sd-bt">four compartments that never mix, drawn to scale</span>
            <span class="sd-split">${compartments.map(([key, [label]]) => `<span class="sd-part ${key}" style="flex:${graphs[key].triples}">
              <b>${esc(label)}</b><span>${fmt(graphs[key].triples)}</span></span>`).join("")}</span></button>
        </div>
        <div class="sd-layer base">${block("rdf", "RDF triples, named by IRIs", `${fmt(triples)} three-part statements: a thing, a relationship, another thing`, "sd-rdf")}</div>
        <div class="sd-aside"><span class="tiny">Set aside, on purpose:</span>${block("owl", "OWL", "no profile claimed")}${block("legalruleml", "LegalRuleML", "deferred")}</div>
      </figure>

      ${standard("rdf", "RDF and triples: facts as three-part statements", {
        here: `<p>Everything is written as ${term("triple", "triples")}: a thing, a relationship, and another thing or a value. This build's
          graph holds <b>${fmt(triples)}</b> of them. Here are the first lines of section 44's legal test as the committed file writes it
          (a format called Turtle; each line ending in “;” is one more statement about the same thing):</p>
          ${turtle(test)}
          <p class="small">Read the first line as “GL-0001 <i>is a</i> structured test”, the next as “its label is …”, and so on: who wrote it,
          when, why, its confidence, the evidence it quotes, and that it is <b>unreviewed</b>.</p>`,
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
        here: `<p>Every statement is filed in one of four compartments, so a question that asks only for what a person approved cannot reach
          what a machine wrote:</p>
          <div class="sd-comps">${compartments.map(([key, [label, text]]) => `<div class="sd-comp ${key}"><i></i><div><b>${esc(label)}</b>
            <span class="tiny"><code>${esc(key)}</code> · ${fmt(graphs[key].triples)} statements${Object.keys(graphs[key].review_status || {}).length
              ? ` · ${Object.entries(graphs[key].review_status).map(([s, n]) => `${fmt(n)} ${esc(s)}`).join(", ")}` : ""}</span>
            <p class="small">${esc(text)}</p></div></div>`).join("")}</div>
          <p class="small">${esc(g.states || "")}</p>`,
        not: "Not a permission system: anyone with the files can read every compartment. What it guarantees is that a statement's origin is never lost or merged.",
      })}

      ${standard("skos", "SKOS: names for ideas, and which is a kind of which", {
        here: `<p>Each idea has one preferred name, the other names it goes by, and its “is a kind of” links, written with ${term("skos")}. The
          idea <i>deceptively similar</i>, as the graph writes those parts:</p>
          ${turtle({ ...concept, lines: skosLines })}
          <p class="small">That is how “objection” and “ground for rejection” can lead to the same idea, and how search recognises everyday words.</p>`,
        not: "Not a dictionary of legal meanings: a SKOS definition here is a machine-written record, stamped as unreviewed, and the Act's own definitions are quoted, never replaced.",
      })}

      ${standard("shacl", "SHACL: checks the graph must pass", {
        here: `<p>Written checks, like a form's validation rules, run on every build. There are <b>${fmt(shapes)}</b>:</p>
          <div class="sd-bars">${Object.entries(checks.shapes).map(([name, n]) => `<div class="sd-barrow"><span>${esc(name)}</span>
            <span class="sd-bar"><i style="width:${(100 * n) / Math.max(...Object.values(checks.shapes))}%"></i></span><b>${fmt(n)}</b></div>`).join("")}</div>
          <p>For example: every machine-written record must name its author, date, evidence and review status; every part of a legal test must
          quote its source and say whether it is law or practice. A single defect fails the build, and every check has a deliberately broken
          example that must fail it.</p>`,
        not: "Not a check that the law has been read correctly. It checks that every record is complete and honest about its origin; whether its reading is right is for an expert.",
      })}

      ${standard("sparql", "SPARQL and rules: asking the graph, and drawing approved conclusions", {
        here: `<p>${term("sparql")} is the graph's query language, as SQL is a table's. It answers the
          ${fmt(approved.CompetencyQuestion || 0)} approved competency questions (questions the ontology must be able to answer), and it runs the
          ${term("inference-rule", "inference rules")}, each a query that writes its conclusions into the “what a rule concluded” compartment:</p>
          <ul class="sd-rules">${checks.rules.map((r) => `<li><span class="pill ${r.approved ? "working" : "planned"}">${r.approved ? "Approved" : "Not approved"}</span>
            <div><b>${esc(r.id)}</b> ${r.approved ? "" : "<span class=\"small muted\">so what it concludes is a candidate.</span>"}
            ${r.limits ? `<p class="small muted">Its own limits: ${esc(r.limits)}</p>` : ""}</div></li>`).join("")}</ul>`,
        not: "Not open-ended reasoning: only rules a person approved produce conclusions that may be relied on, and each states its own limits.",
      })}

      ${standard("prov-o", "PROV-O: who made what, from what, and when", {
        here: `<p>The model's record of origin builds on ${term("prov-o")}: a record is a kind of PROV entity, and “derived from” is PROV's own
          relationship, so a PROV-aware tool understands where each record came from. In the statements themselves this appears as the lines
          above: <code>tmk:authoredBy</code>, <code>tmk:authoredDate</code>, <code>tmk:evidence</code>, <code>tmk:reviewStatus</code>.</p>`,
        not: "Not a log of every edit. It records what each record rests on and who wrote it; the history of changes is in the repository.",
      })}

      ${standard("json", "JSON: how this site reads it", {
        here: `<p>This site does not query the graph directly. On every publish, the same records are written as ${term("json")} files that the
          browser reads: the ontology, the passages, the search index, the prepared answers, the customer preview and a release manifest
          (built ${esc(build.generated || "")} from revision <code>${esc((build.revision || "").slice(0, 12))}</code>). The release manifest names the
          snapshot (<code>${esc((g.upstream?.commit || "").slice(0, 12))}</code>), ${(build.law || []).map((l) => `${esc(l.line)} (compilation ${esc(l.compilation)})`).join(" and ")},
          and ${esc(build.manual?.line || "")}.</p>`,
        not: "Not a second source of truth: every JSON file is regenerated from the repository's records and is never edited by hand.",
      })}

      ${standard("owl", "OWL: why no OWL profile is claimed", {
        here: `<p>${term("owl")} lets a program draw logical conclusions automatically from class definitions. This model deliberately does not
          rely on it. Some OWL words label properties, but no OWL profile is claimed and no automatic OWL reasoning is run, because an unchecked
          machine conclusion about law could be mistaken for a fact. The release manifest says so in its own words:</p>
          <blockquote class="sd-profile">${esc(g.profile || "")}</blockquote>`,
        not: "Not a gap to be filled quietly. Claiming a profile, or running a reasoner, would be a recorded decision with its own checks.",
      })}

      ${standard("legalruleml", "LegalRuleML: deferred", {
        here: `<p>${term("legalruleml")} writes laws as executable rules, including exceptions that override one another. It is deferred: the
          legal tests on <a href="#/rules">Rules as code</a> are structured data that explain what a provision requires, not rules that run to a result.</p>`,
        not: "Not ruled out for ever; ruled out while the system must never state an examination outcome.",
      })}
    </div>
  </div>`;
  root.querySelectorAll("[data-jump]").forEach((b) => b.addEventListener("click", () => {
    const target = root.querySelector(`#${b.dataset.jump}`);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    target.focus({ preventScroll: true });
  }));
}

/** One block of the picture at the top: a standard's name and what it does, a click from its section. */
const block = (key, name, text, id = `sd-${key}`) => `<button type="button" class="sd-block ${esc(key)}" data-jump="${id}">
  <span class="sd-bk">${esc(name)}</span><span class="sd-bt">${text}</span></button>`;

function standard(key, title, { here, not }) {
  const entry = GLOSSARY[key];
  return `<section class="sd-sec" id="sd-${esc(key)}" tabindex="-1">
    <div class="sd-left">
      <h2>${esc(title)}</h2>
      <p class="sd-plain">${esc(entry.plain)}</p>
      <div class="sd-not"><span class="sd-k">What it is not</span><p class="small">${esc(not)}</p></div>
      <p class="tiny">Technically: ${esc(entry.technical)}</p>
    </div>
    <div class="sd-here"><span class="sd-k">What it does here</span>${here}</div>
  </section>`;
}

/** A block of the committed graph, as the file writes it. */
function turtle(block) {
  if (!block.lines?.length) return `<p class="tiny muted">This build carries no example.</p>`;
  return `<figure class="sd-turtle"><pre>${esc(block.lines.join("\n"))}</pre>
    <figcaption class="tiny">From the <b>${esc(block.graph)}</b> compartment of the committed graph${block.total > block.lines.length ? `, shortened (… marks a cut)` : ""}.</figcaption></figure>`;
}
