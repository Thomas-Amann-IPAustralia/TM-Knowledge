/* The browser's copy of `tm_knowledge.search.index.Systems`, without vectors.

   - keyword  — BM25 over each passage's heading and text, scored the way
                SQLite FTS5's bm25(passages, 0.5, 1.0) scores them. Those
                weights land on (ref, heading) — `ref` is an unindexed first
                column — so the heading counts in full, not by half (Q-69);
   - ontology — keyword search, plus what the ontology knows about the
                question: recognise concepts, expand the query with their
                labels and their neighbours' labels, and pull in the passages
                linked to them. Fused by reciprocal rank, as in Python.

   The measured "ontology" system also fused a vector ranking. The page never has
   the passage vectors, so the live configuration is keyword + ontology and the
   page says so. `tests/explorer_parity.mjs` runs this under Node so the tests can
   compare its rankings with Python's, question by question. */

const K1 = 1.2;
const B = 0.75;

const unicodeTokens = (text) => text.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
  .split(/[^\p{L}\p{N}]+/u).filter(Boolean);

/** Concept recognition alone — needs only search.json, not the Manual's text. */
export class Recogniser {
  /* The same three rules as `bulk.links.find_mentions` (ADR-0121): the longest
     label wins and consumes its span (C8), a concept's own not-labels veto it (E2),
     and straight and curly apostrophes match each other. The too-general labels
     (E1) never reach here: the patterns arrive already without them. */
  constructor(search) {
    this.patterns = search.patterns.map(([label, owners, alias]) => ({
      label, owners, alias, re: Recogniser.regex(label),
    }));
    this.vetoes = new Map();
    for (const [id, c] of Object.entries(search.concepts || {})) {
      if (c.not && c.not.length) this.vetoes.set(id, c.not.map((n) => Recogniser.regex(n)));
    }
  }

  static regex(label) {
    const body = label.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/['’]/g, "['’]");
    return new RegExp(`(?<![A-Za-z0-9])${body}(?![A-Za-z0-9])`, "gi");
  }

  #vetoed(text, start, end, id) {
    for (const re of this.vetoes.get(id) || []) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(text)) !== null) {
        if (m.index <= start && end <= m.index + m[0].length) return true;
        if (m[0].length === 0) re.lastIndex++;
      }
    }
    return false;
  }

  /** Concepts named in the question, earliest first — `Systems.recognise`. */
  recognise(question) {
    const taken = [];
    const found = new Map();
    for (const p of this.patterns) {
      p.re.lastIndex = 0;
      let m;
      while ((m = p.re.exec(question)) !== null) {
        const start = m.index, end = m.index + m[0].length;
        if (m[0].length === 0) { p.re.lastIndex++; continue; }
        if (taken.some(([s, e]) => start < e && s < end)) continue;
        taken.push([start, end]);
        for (const owner of p.owners) {
          if (this.#vetoed(question, start, end, owner)) continue;
          const current = found.get(owner);
          if (!current || start < current.start) found.set(owner, { start, end, label: p.label, alias: p.alias });
        }
      }
    }
    const order = [...found.keys()].map((id, i) => [id, i]).sort((a, b) => found.get(a[0]).start - found.get(b[0]).start || a[1] - b[1]);
    return order.map(([id]) => ({ id, ...found.get(id) }));
  }
}

export class Engine {
  constructor(search, passages) {
    this.s = search;
    this.chunks = passages.chunks;
    this.legislation = passages.legislation;
    this.pages = passages.pages;
    this.refs = this.chunks.map((c) => c[0]);
    this.row = new Map(this.chunks.map((c, i) => [c[0], i]));
    this.stop = new Set(search.stopwords);
    this.generic = new Set(search.generic);
    this.recogniser = new Recogniser(search);
    this.edges = new Map();
    for (const e of search.relations) {
      for (const end of [e[0], e[2]]) {
        if (!this.edges.has(end)) this.edges.set(end, []);
        this.edges.get(end).push(e);
      }
    }
    this.#index();
  }

  #index() {
    const postings = new Map();
    const lengths = new Float64Array(this.chunks.length);
    let total = 0;
    this.chunks.forEach(([, , heading, text], i) => {
      const freq = new Map();
      const h = unicodeTokens(heading), b = unicodeTokens(text);
      for (const t of h) freq.set(t, (freq.get(t) || 0) + 1.0);
      for (const t of b) freq.set(t, (freq.get(t) || 0) + 1.0);
      lengths[i] = h.length + b.length;
      total += lengths[i];
      for (const [t, f] of freq) {
        if (!postings.has(t)) postings.set(t, []);
        postings.get(t).push([i, f]);
      }
    });
    this.postings = postings;
    this.lengths = lengths;
    this.avgdl = total / this.chunks.length;
  }

  /** The query terms, as `search.index._terms` makes them. */
  terms(text) {
    const out = [];
    for (const t of (text.toLowerCase().match(/[a-z0-9]+/g) || [])) {
      if (t.length > 1 && !this.stop.has(t) && !out.includes(t)) out.push(t);
    }
    return out;
  }

  keywordRanking(query, k) {
    const terms = this.terms(query);
    if (!terms.length) return [];
    const N = this.chunks.length;
    const score = new Map();
    for (const t of terms) {
      const list = this.postings.get(t);
      if (!list) continue;
      let idf = Math.log((N - list.length + 0.5) / (list.length + 0.5));
      if (idf <= 0) idf = 1e-6;
      for (const [i, f] of list) {
        const s = idf * (f * (K1 + 1)) / (f + K1 * (1 - B + (B * this.lengths[i]) / this.avgdl));
        score.set(i, (score.get(i) || 0) + s);
      }
    }
    return [...score.entries()].sort((a, b) => b[1] - a[1] || a[0] - b[0]).slice(0, k).map(([i, s]) => ({ ref: this.refs[i], score: s }));
  }

  keyword(question, k = 10) {
    return this.keywordRanking(question, k).map((h) => ({ ...h, why: ["keyword"] }));
  }

  recognise(question) {
    return this.recogniser.recognise(question);
  }

  trace(question) {
    const recognised = this.recognise(question);
    const ids = recognised.map((r) => r.id);
    const specific = ids.filter((c) => !this.generic.has(c));
    const paths = [];
    for (const c of specific) for (const e of this.edges.get(c) || []) paths.push(e);
    const spec = new Set(specific);
    const neighbours = [...new Set(paths.map((e) => (spec.has(e[0]) ? e[2] : e[0])))].filter((n) => !spec.has(n)).sort(cmp);
    const provisions = [...new Set(specific.flatMap((c) => this.s.concepts[c]?.basis || []))].sort(cmp);
    const unique = new Map(paths.map((e) => [e.join("\u0000"), e]));
    const sortedPaths = [...unique.values()].sort((a, b) => {
      for (let i = 0; i < 5; i++) { const c = cmp(a[i], b[i]); if (c) return c; }
      return 0;
    });
    return { recognised, ids, specific, neighbours, provisions, paths: sortedPaths };
  }

  fuse(rankings, k) {
    const fused = new Map(), why = new Map();
    for (const [name, refs] of rankings) {
      refs.forEach((ref, rank) => {
        fused.set(ref, (fused.get(ref) || 0) + 1 / (this.s.rrf_k + rank + 1));
        if (!why.has(ref)) why.set(ref, []);
        why.get(ref).push(name);
      });
    }
    return [...fused.entries()].sort((a, b) => b[1] - a[1] || cmp(a[0], b[0])).slice(0, k)
      .map(([ref, score]) => ({ ref, score, why: why.get(ref) }));
  }

  ontology(question, k = 10) {
    const trace = this.trace(question);
    const depth = this.s.depth;
    const rankings = [["keyword", this.keywordRanking(question, depth).map((h) => h.ref)]];
    if (!trace.specific.length) return { hits: this.fuse(rankings, k), trace, linked: [] };
    const expansion = [];
    for (const c of trace.specific) expansion.push(...(this.s.concepts[c]?.labels || []));
    for (const n of trace.neighbours) expansion.push(this.s.concepts[n]?.pref || "");
    rankings.push(["expanded", this.keywordRanking(question + " " + expansion.join(" "), depth).map((h) => h.ref)]);
    const weight = new Map();
    const add = (ref, w) => weight.set(ref, (weight.get(ref) || 0) + w);
    for (const c of trace.specific) for (const ref of this.s.mentions[c] || []) add(ref, 2);
    for (const n of trace.neighbours) for (const ref of this.s.mentions[n] || []) add(ref, 1);
    for (const p of trace.provisions) for (const ref of this.s.citing[p] || []) add(ref, 1);
    const linked = [...weight.keys()].sort((a, b) => weight.get(b) - weight.get(a) || cmp(a, b)).slice(0, depth);
    rankings.push(["linked", linked]);
    return { hits: this.fuse(rankings, k), trace, linked, weight };
  }

  /** Everything the answer prompt needs, as `bulk.cli._measurement_items` builds it. */
  prepare(question, chat) {
    const { hits, trace, weight } = this.ontology(question, chat.passages_k);
    const passages = hits.map((h) => h.ref);
    const cited = [];
    for (const ref of passages.slice(0, 3)) for (const id of (this.chunks[this.row.get(ref)]?.[4] || [])) cited.push(id);
    const legislation = [];
    for (const ref of [...trace.provisions, ...cited]) {
      if (!legislation.includes(ref) && this.legislation[ref]) legislation.push(ref);
    }
    const plain = this.keyword(question, 10).map((h) => h.ref);
    return {
      question, hits, trace, weight, passages, legislation: legislation.slice(0, chat.legislation_k),
      paths: trace.paths.slice(0, chat.paths_k), plain, plainTop: plain.slice(0, chat.plain_k),
    };
  }

  text(ref) {
    if (this.legislation[ref]) return this.legislation[ref][3];
    const i = this.row.get(ref);
    return i === undefined ? null : this.chunks[i][3];
  }

  /** The answer prompt's input, in the exact shape `bulk.jobs._answer_render` writes. */
  prompt(prepared, chat) {
    const label = (c) => this.s.concepts[c]?.pref || c;
    const block = (ref) => {
      let text = this.text(ref) || "";
      if (text.length > chat.passage_chars) text = text.slice(0, chat.passage_chars) + "…";
      text = text.replaceAll("<passage", "&lt;passage").replaceAll("</passage", "&lt;/passage");
      return `<passage source="${sourceName(ref)}" ref="${ref}">\n${text}\n</passage>`;
    };
    const lines = ["ONTOLOGY (one line per concept):", chat.ontology_map, "",
      "CONCEPTS RECOGNISED IN THE QUESTION: " + (prepared.trace.ids.map((c) => `${c} ${label(c)}`).join(", ") || "none")];
    if (prepared.paths.length) {
      lines.push("", "GRAPH PATH (relationships the ontology holds for those concepts):");
      for (const [s, p, o, rid, origin] of prepared.paths) lines.push(`- ${label(s)} —${p}→ ${label(o)} (${rid}, ${origin})`);
    }
    lines.push("", `QUESTION: ${prepared.question}`, "", "MANUAL PASSAGES:");
    for (const ref of prepared.passages) if (this.text(ref)) lines.push(block(ref));
    if (prepared.legislation.length) {
      lines.push("", "LEGISLATION:");
      for (const ref of prepared.legislation) lines.push(block(ref));
    }
    return lines.join("\n");
  }

  /** Keep only citations whose quote is really in the passage — `bulk.jobs.evidence`. */
  verify(citations, prepared) {
    const shown = new Set([...prepared.passages, ...prepared.legislation]);
    const kept = [], dropped = [];
    for (const c of citations || []) {
      const ref = String(c.ref || "");
      const text = shown.has(ref) ? this.text(ref) : null;
      const span = text ? locate(text, String(c.quote || "")) : null;
      if (span) kept.push({ ref, quote: text.slice(span[0], span[1]) });
      else dropped.push({ ref, quote: c.quote });
    }
    return { kept, dropped };
  }
}

/* PU-0004 at answer time — `search.authority.conflations`, rule for rule (review F1,
   ADR-0121). A sentence that says the legislation requires, provides or states
   something, in an answer that cites no provision of it, is flagged — never removed.
   A sentence naming the Manual, or a negated one, is not. */
export const AUTHORITY_MESSAGE = "Says the legislation requires this, but the answer cites no provision for it — only " +
  "the Manual, which states practice and does not bind the Registrar's discretion (PU-0004). Check the provision itself.";
const VERB = "(?:requires?|provides?|states?|says|prescribes?|mandates?|obliges?|imposes?)";
const WHOLE = new RegExp(String.raw`\bthe (?<what>Act|Regulations|legislation)\b[^.;:]{0,40}?\b${VERB}\b`, "i");
const PART = new RegExp(String.raw`\b(?<kind>section|s|subsection|regulation|reg|r)\.?\s?(?<number>\d+[A-Z]{0,2}(?:\.\d+[A-Z]{0,2})?)` +
  String.raw`(?:\([0-9a-z]+\))*[^.;:]{0,40}?\b${VERB}\b`, "i");
const SENTENCE_BREAK = /(?<=[.!?])\s+(?=[A-Z"'“‘(])|\n+/;
const MANUAL = /\bManual\b/;
const NEGATION = /\b(?:not|no|never|neither|nor)\b|n['’]t\b/i;

function supportedBy(m, cited) {
  const g = m.groups || {};
  if (g.number) {
    const regulation = ["regulation", "reg", "r"].includes(g.kind.toLowerCase());
    const prefix = regulation ? `TMR1995/r${g.number}` : `TMA1995/s${g.number}`;
    return cited.some((ref) => ref === prefix || ref.startsWith(prefix + "(") || ref.startsWith(prefix + "/"));
  }
  const what = (g.what || "").toLowerCase();
  if (what === "act") return cited.some((ref) => ref.startsWith("TMA1995/"));
  if (what === "regulations") return cited.some((ref) => ref.startsWith("TMR1995/"));
  return cited.some((ref) => ref.startsWith("TMA1995/") || ref.startsWith("TMR1995/"));
}

export function authorityFlags(answer, cited) {
  const refs = (cited || []).map(String);
  const flags = [];
  for (let sentence of String(answer || "").split(SENTENCE_BREAK)) {
    sentence = sentence.trim();
    if (!sentence || MANUAL.test(sentence)) continue;
    for (const pattern of [PART, WHOLE]) {
      const m = pattern.exec(sentence);
      if (m && !NEGATION.test(sentence.slice(0, m.index + m[0].length)) && !supportedBy(m, refs)) {
        flags.push({ sentence, message: AUTHORITY_MESSAGE });
        break;
      }
    }
  }
  return flags;
}

export function sourceName(ref) {
  return { TMM: "Manual (practice)", TMA1995: "Trade Marks Act 1995", TMR1995: "Trade Marks Regulations 1995" }[ref.split("/")[0]] || "other";
}

const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

const NORMALISE = { "‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " " };

function normalised(text) {
  const out = [], index = [];
  let previousSpace = false;
  for (let i = 0; i < text.length; i++) {
    let ch = NORMALISE[text[i]] ?? text[i];
    if (/\s/.test(ch)) {
      if (previousSpace) continue;
      ch = " "; previousSpace = true;
    } else previousSpace = false;
    out.push(ch); index.push(i);
  }
  return [out.join(""), index];
}

/** Where a quote sits in a passage, exactly or after normalising spaces and marks. */
export function locate(text, quote) {
  quote = (quote || "").trim().replace(/^…+|…+$/g, "").trim();
  if (quote.length < 8) return null;
  const at = text.indexOf(quote);
  if (at >= 0) return [at, at + quote.length];
  const [nt, index] = normalised(text);
  const [nq] = normalised(quote);
  const q = nq.trim();
  const pos = nt.indexOf(q);
  if (pos < 0) return null;
  return [index[pos], index[pos + q.length - 1] + 1];
}
