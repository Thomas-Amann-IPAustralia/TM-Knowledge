/* One glossary for the whole site (ADR-0145): no reader is assumed to know a standard's name.

   Each entry says, in three parts, what the term means in plain words, what it does here, and
   (for the technically curious) what it is called and where it comes from. `term(key)` puts an
   inline, keyboard-reachable explanation wherever a page uses the term; `#/glossary` lists them
   all. A page explains a term the first time it uses it. The entries describe this system and
   standard technology; none states the law. */

import { esc } from "./app.js";

export const GLOSSARY = {
  ontology: {
    label: "ontology",
    plain: "A shared, written-down description of a field: the ideas in it, what kind of thing each one is, and how they relate.",
    here: "The ideas examiners reason with (grounds, tests, roles, steps, records), sorted into kinds and connected, each tied to the passage of the Manual or provision it comes from.",
    technical: "A conceptual model, stored here as a knowledge graph. The word comes from philosophy; in computing it means an explicit model a program can read.",
  },
  "knowledge-graph": {
    label: "knowledge graph",
    plain: "Facts stored as things and the links between them, rather than as rows in a table, so a program can follow the links.",
    here: "The ideas, their connections, the passages and provisions, and who wrote each record, all in one linked store that can be queried and checked.",
    technical: "A graph database of statements, here written in RDF and kept in separate named graphs by who wrote them.",
  },
  "rules-as-code": {
    label: "rules as code",
    plain: "Writing what a rule says (who acts, when it applies, what follows) as structured data a program can read, alongside the words.",
    here: "Section 44's test, for example, is stored as its effect, its conditions joined by 'all of' and 'any of', its exceptions, and the evidence and routes the Manual describes, each part quoting its source.",
    technical: "Decision-table style structure (condition trees, effects, procedures) as data; it does not execute a final decision, and assessments a person makes are never computed.",
  },
  concept: {
    label: "idea (concept)",
    plain: "One thing the field has a name for, such as 'honest concurrent use' or 'examination report'.",
    here: "Each idea has a preferred name, other names it goes by, names it must not be confused with, a kind, and the passage it rests on.",
    technical: "A SKOS concept with labels, typed into one of the kinds.",
  },
  kind: {
    label: "kind",
    plain: "What sort of thing an idea is: a ground of refusal, a legal test, a role, a step, a record and so on.",
    here: "Eleven kinds in three families: the questions the law asks, what they are asked about, and the process around them.",
    technical: "A class-like grouping of concepts; what an idea does is a connection, not a kind.",
  },
  connection: {
    label: "connection",
    plain: "A stated link between two ideas that says what the link means, such as 'a role performs a step'.",
    here: "Each connection quotes the sentence it rests on and keeps its wording's force: a 'may' stays a 'may', and a condition stays attached.",
    technical: "A relationship record, reified in the graph so its evidence, modality and condition travel with it.",
  },
  modality: {
    label: "modality",
    plain: "How strongly a sentence says something: must, may, may not, generally.",
    here: "Kept on every connection and legal test, so a discretion is never turned into an obligation.",
    technical: "A field on each relationship and effect (obligation, discretion, bar).",
  },
  provenance: {
    label: "provenance",
    plain: "Where a piece of information came from and who made it.",
    here: "Every record says whether a machine wrote it or an expert reviewed it, when, with what evidence, and its review status.",
    technical: "Stored per record and per assertion, in the spirit of the W3C PROV-O vocabulary.",
  },
  unreviewed: {
    label: "machine-written, unreviewed",
    plain: "Written by an AI model and not yet checked by a trade marks expert.",
    here: "Most records are. They may be used and shown, but are labelled wherever they appear, and never become 'approved' by being left alone.",
    technical: "review_status: unreviewed, with the model, date, confidence and evidence in an envelope on each record.",
  },
  llm: {
    label: "language model (LLM)",
    plain: "An AI system that reads and writes text.",
    here: "Used to draft records and to write cited answers from the passages search finds; every quote it gives is checked word for word by ordinary code.",
    technical: "Large language model, called through a paid API with a spending cap and a cache of every response.",
  },
  embedding: {
    label: "matching by meaning (embeddings)",
    plain: "A way of finding text that means something similar even when it uses different words.",
    here: "The measured search used it alongside keyword search; the search in your browser does not.",
    technical: "Each passage is turned into a list of numbers (a vector) by a model; similar meanings give nearby vectors.",
  },
  "keyword-search": {
    label: "keyword search",
    plain: "Finding text that contains the words you typed, like a search box.",
    here: "The baseline every other search on this site is compared with.",
    technical: "BM25 ranking over the Manual's passages, and separately over the Act and the Regulations.",
  },
  ndcg: {
    label: "top-ten quality (nDCG@10)",
    plain: "A score out of 100 for how good a search's first ten results are, giving more credit for the best passages near the top.",
    here: "Used to compare plain keyword search, search by meaning, and search guided by the ontology on 129 questions.",
    technical: "Normalised discounted cumulative gain at rank 10, against relevance grades from 0 to 3.",
  },
  interval: {
    label: "95% interval",
    plain: "The range a measured difference probably lies in. If the range crosses zero, the difference is not established.",
    here: "Every comparison of searches is reported with one, in both directions.",
    technical: "A bootstrap confidence interval over the benchmark questions.",
  },
  "dependency-index": {
    label: "dependency index",
    plain: "A list of what rests on each passage and provision, so a change can be traced to what it touches.",
    here: "Behind 'When the text changes': pick a page or a section and see every record that names it or quotes it.",
    technical: "An index over every store, keyed by any upstream reference, with recorded content hashes to spot changed text.",
  },
  snapshot: {
    label: "snapshot",
    plain: "A copy of the Manual and the legislation taken at one moment, so results can be repeated exactly.",
    here: "Produced by a separate extraction project; this one reads it and never edits it.",
    technical: "A pinned commit of the upstream extraction repository, with a stable reference for every passage and provision.",
  },
  rdf: {
    label: "RDF",
    plain: "A standard way of writing facts as small three-part statements that any compatible tool can read.",
    here: "The whole graph (passages, provisions, ideas, connections, who wrote what) is written in it.",
    technical: "Resource Description Framework, a W3C standard. Files here are Turtle and N-Quads.",
  },
  triple: {
    label: "triple",
    plain: "One three-part statement: a thing, a relationship, and another thing or a value. For example: 'section 44 test' — 'reads' — 'section 44'.",
    here: "The graph is tens of thousands of these.",
    technical: "Subject, predicate, object: the unit of RDF.",
  },
  iri: {
    label: "IRI (identifier)",
    plain: "A unique, web-address-like name for each thing, so two systems mean the same thing by it.",
    here: "Every idea, record and passage has one built from its stable reference, such as GC-0006 or TMA1995/s44.",
    technical: "Internationalised Resource Identifier; the RDF form of an identifier.",
  },
  "named-graph": {
    label: "named graph",
    plain: "A labelled compartment of the graph, so statements from different sources are never mixed up.",
    here: "Four: the source text, what experts approved, what a machine wrote, and what a rule inferred. A query asking for approved statements cannot reach machine-written ones.",
    technical: "RDF 1.1 datasets: each statement carries the name of the graph it belongs to.",
  },
  skos: {
    label: "SKOS",
    plain: "A standard for vocabularies: preferred names, other names, broader and narrower ideas.",
    here: "Holds each idea's names and its 'is a kind of' links.",
    technical: "Simple Knowledge Organization System, a W3C standard for thesauri and taxonomies.",
  },
  shacl: {
    label: "SHACL",
    plain: "A standard for writing checks a graph must pass, like a form's validation rules.",
    here: "Every build is checked: each machine-written record must carry its author, date, evidence and review status; the build fails on any defect.",
    technical: "Shapes Constraint Language, a W3C standard. Shapes live in shapes/; each has a fixture that must fail.",
  },
  sparql: {
    label: "SPARQL",
    plain: "The standard query language for graphs, as SQL is for tables.",
    here: "Used to answer the competency questions and to run the approved inference rule.",
    technical: "SPARQL 1.1, a W3C standard; a CONSTRUCT query writes new statements.",
  },
  "inference-rule": {
    label: "inference rule",
    plain: "A rule that adds a conclusion to the graph whenever its conditions are found.",
    here: "One approved rule: which expert-approved records rest on a Manual passage. Its conclusions go in their own graph, apart from what anyone wrote.",
    technical: "A SPARQL CONSTRUCT query (RULE-0002), run at build time into the inferred graph.",
  },
  "prov-o": {
    label: "PROV-O",
    plain: "A standard vocabulary for saying who made something, from what, and when.",
    here: "The model's provenance part builds on it: each record is an entity with an origin, an author, a date and its evidence.",
    technical: "The W3C Provenance Ontology.",
  },
  owl: {
    label: "OWL",
    plain: "A standard for describing classes and logic so a program can draw conclusions automatically.",
    here: "Deliberately not relied on: no automatic logical conclusions are drawn from the model, because an unchecked machine conclusion about law could be mistaken for a fact.",
    technical: "Web Ontology Language, a W3C standard. Some OWL terms label properties here, but no OWL profile is claimed and no OWL inference is run (ADR-0134).",
  },
  legalruleml: {
    label: "LegalRuleML",
    plain: "A standard for writing laws as rules that can be executed, including exceptions that override each other.",
    here: "Deferred: legal tests are stored as structured data, not as executable rules that would decide anything.",
    technical: "An OASIS standard for defeasible legal rules (ADR-0009 defers it).",
  },
  json: {
    label: "JSON",
    plain: "A common text format for passing data between programs.",
    here: "The site reads its data as JSON files built from the repository on every publish.",
    technical: "JavaScript Object Notation.",
  },
};

/** An inline explanation of a term: the visible words are `text` (the term's label by default). */
export function term(key, text) {
  const entry = GLOSSARY[key];
  if (!entry) throw new Error(`glossary: no entry for ${key}`);
  return `<button type="button" class="term" data-term="${esc(key)}" aria-expanded="false" aria-haspopup="dialog">${esc(text || entry.label)}</button>`;
}

/** The entry, in its three parts, as a glossary page or a popover shows it. */
export function entryHtml(key) {
  const e = GLOSSARY[key];
  return `<p><b>${esc(e.label)}</b> — ${esc(e.plain)}</p>
    <p class="small"><span class="muted">Here:</span> ${esc(e.here)}</p>
    <p class="tiny"><span class="muted">Technically:</span> ${esc(e.technical)}</p>`;
}

/** One popover for every term on the page: opened by click or Enter, closed by Escape, a click
    elsewhere, or the term again. */
export function initTerms() {
  const pop = document.createElement("div");
  pop.className = "term-pop";
  pop.setAttribute("role", "dialog");
  pop.hidden = true;
  document.body.appendChild(pop);
  let owner = null;
  const close = () => {
    if (!owner) return;
    owner.setAttribute("aria-expanded", "false");
    pop.hidden = true;
    owner = null;
  };
  document.addEventListener("click", (event) => {
    const button = event.target.closest(".term");
    if (!button) { if (!event.target.closest(".term-pop")) close(); return; }
    event.preventDefault();
    if (owner === button) { close(); return; }
    close();
    owner = button;
    button.setAttribute("aria-expanded", "true");
    pop.innerHTML = `${entryHtml(button.dataset.term)}<p class="tiny"><a href="#/glossary">Every term →</a></p>`;
    pop.setAttribute("aria-label", GLOSSARY[button.dataset.term].label);
    pop.hidden = false;
    const r = button.getBoundingClientRect();
    const width = Math.min(340, window.innerWidth - 24);
    pop.style.width = `${width}px`;
    pop.style.left = `${Math.max(12, Math.min(window.innerWidth - width - 12, r.left + window.scrollX))}px`;
    pop.style.top = `${r.bottom + window.scrollY + 6}px`;
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && owner) { const b = owner; close(); b.focus(); } });
  window.addEventListener("hashchange", close);
}
