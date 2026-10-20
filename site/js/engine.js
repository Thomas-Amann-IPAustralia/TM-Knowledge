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
   compare its rankings with Python's, question by question.

   Live, a model may also read the question against the map (ADR-0132) and name
   ideas it raises in other words. Those arrive as `read`, checked by `reading`,
   and start the search exactly as a name would. Without them every method here
   is the measured one. */

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

/** BM25 postings over [heading, text] documents, as FTS5 weights them here (Q-69). */
function bm25Index(docs) {
  const postings = new Map();
  const lengths = new Float64Array(docs.length);
  let total = 0;
  docs.forEach(([heading, text], i) => {
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
  return { postings, lengths, avgdl: total / Math.max(1, docs.length) };
}

/** [document index, score], best first, ties by index. */
function bm25Rank(index, terms, k) {
  if (!terms.length) return [];
  const N = index.lengths.length;
  const score = new Map();
  for (const t of terms) {
    const list = index.postings.get(t);
    if (!list) continue;
    let idf = Math.log((N - list.length + 0.5) / (list.length + 0.5));
    if (idf <= 0) idf = 1e-6;
    for (const [i, f] of list) {
      const s = idf * (f * (K1 + 1)) / (f + K1 * (1 - B + (B * index.lengths[i]) / index.avgdl));
      score.set(i, (score.get(i) || 0) + s);
    }
  }
  return [...score.entries()].sort((a, b) => b[1] - a[1] || a[0] - b[0]).slice(0, k);
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
    Object.assign(this, bm25Index(this.chunks.map(([, , heading, text]) => [heading, text])));
    // A07: the provisions, by their words, apart from the Manual (`search.index.ProvisionIndex`).
    this.provisionRefs = (this.s.provisions || []).filter((ref) => this.legislation[ref]);
    this.provisionIndex = bm25Index(this.provisionRefs.map((ref) => [this.legislation[ref][2], this.legislation[ref][3]]));
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
    return bm25Rank(this, this.terms(query), k).map(([i, score]) => ({ ref: this.refs[i], score }));
  }

  /** Provisions ranked by the question's words — `ProvisionIndex.search`. Shown apart,
      never sent to the answer prompt. */
  provisionSearch(query, k = 5) {
    return bm25Rank(this.provisionIndex, this.terms(query), k).map(([i, score]) => ({ ref: this.provisionRefs[i], score, why: ["provision"] }));
  }

  keyword(question, k = 10) {
    return this.keywordRanking(question, k).map((h) => ({ ...h, why: ["keyword"] }));
  }

  recognise(question) {
    return this.recogniser.recognise(question);
  }

  /** The model's reading of a typed question, checked: each idea must be on the map,
      specific enough to steer, not already found by name, and its words must be in
      the question. Live only (ADR-0132). */
  reading(question, parsed, max = 4) {
    const named = new Set(this.recognise(question).map((r) => r.id));
    const kept = [], dropped = [];
    for (const pick of Array.isArray(parsed?.concepts) ? parsed.concepts : []) {
      const id = String(pick?.id ?? "").trim(), words = String(pick?.words ?? "").trim(), why = String(pick?.why ?? "").trim();
      if (named.has(id) || kept.some((k) => k.id === id)) continue;
      const span = findWords(question, words);
      const reason = !Object.hasOwn(this.s.concepts, id) ? "it is not an idea on the map"
        : this.generic.has(id) ? "it is named too often to steer"
        : !span ? "its words are not in the question"
        : kept.length >= max ? `only the first ${max} are used` : null;
      if (reason) { dropped.push({ id, words, why, reason }); continue; }
      kept.push({ id, start: span[0], end: span[1], label: question.slice(span[0], span[1]), alias: false, read: true, why });
    }
    return { kept, dropped };
  }

  trace(question, read = []) {
    const recognised = this.recognise(question);
    for (const r of read) if (!recognised.some((x) => x.id === r.id)) recognised.push(r);
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

  ontology(question, k = 10, read = []) {
    const trace = this.trace(question, read);
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
  prepare(question, chat, read = []) {
    const { hits, trace, weight } = this.ontology(question, chat.passages_k, read);
    const passages = hits.map((h) => h.ref);
    const cited = [];
    for (const ref of passages.slice(0, 3)) for (const id of (this.chunks[this.row.get(ref)]?.[4] || [])) cited.push(id);
    const legislation = [];
    for (const ref of [...namedProvisions(question, this.legislation), ...trace.provisions, ...cited]) {
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

  /** What the answer is given of each source — `bulk.jobs.answer_excerpts`, rule for
      rule: legislation whole up to law_chars, a larger provision's matched blocks and any
      block a "Subject to" lead-in names, a Manual chunk cut around the question's words
      (A06). The prompt shows these, and `verify` checks quotes against these. */
  excerpts(prepared, chat) {
    const terms = this.terms(prepared.question);
    const out = new Map();
    for (const ref of [...prepared.passages, ...prepared.legislation]) {
      const text = this.text(ref);
      if (!text) continue;
      out.set(ref, excerpt(ref, text, this.legislation[ref]?.[4] || null, terms, chat));
    }
    return out;
  }

  /** The answer prompt's input, in the exact shape `bulk.jobs._answer_render` writes. */
  prompt(prepared, chat) {
    const label = (c) => this.s.concepts[c]?.pref || c;
    const sent = this.excerpts(prepared, chat);
    const block = (ref) => {
      const { text, cut } = sent.get(ref);
      const body = text.replaceAll("<passage", "&lt;passage").replaceAll("</passage", "&lt;/passage");
      return `<passage source="${sourceName(ref)}" ref="${ref}"${cut ? ` cut="${cut}"` : ""}>\n${body}\n</passage>`;
    };
    const lines = ["ONTOLOGY (one line per concept):", chat.ontology_map, "",
      "CONCEPTS RECOGNISED IN THE QUESTION: " + (prepared.trace.ids.map((c) => `${c} ${label(c)}`).join(", ") || "none")];
    const defined = prepared.trace.ids.filter((c) => chat.definitions?.[c]).map((c) => chat.definitions[c]);
    if (defined.length) lines.push("", "DEFINITIONS (of the concepts recognised; machine-written, unreviewed):", ...defined);
    if (prepared.paths.length) {
      lines.push("", "GRAPH PATH (relationships the ontology holds for those concepts):");
      for (const edge of prepared.paths) lines.push(pathLine(label, edge));
    }
    lines.push("", `QUESTION: ${prepared.question}`, "", "MANUAL PASSAGES:");
    for (const ref of prepared.passages) if (sent.has(ref)) lines.push(block(ref));
    if (prepared.legislation.length) {
      lines.push("", "LEGISLATION:");
      for (const ref of prepared.legislation) if (sent.has(ref)) lines.push(block(ref));
    }
    return lines.join("\n");
  }

  /** Each claim's quotes checked against the excerpt the model was given, not the whole
      text — `bulk.jobs.check_claims` (A08). A claim with no kept quote is unsupported.
      This proves the words are there; it does not prove they support the claim. */
  verify(claims, prepared, chat) {
    const sent = this.excerpts(prepared, chat);
    return (claims || []).filter((c) => c && typeof c === "object").map((c) => {
      const quotes = [], dropped = [];
      for (const q of c.quotes || []) {
        const ref = String(q.ref || ""), shown = sent.get(ref);
        const span = shown ? locate(shown.text, String(q.quote || "")) : null;
        if (span) quotes.push({ ref, quote: shown.text.slice(span[0], span[1]) });
        else dropped.push({ ref, quote: q.quote });
      }
      const authority = AUTHORITIES.includes(c.authority) ? c.authority : "none";
      return { text: String(c.text || ""), authority, quotes, dropped, supported: quotes.length > 0 };
    });
  }
}

/* Exact-reference lookup (A07) — `search.citations.named_provisions`, rule for rule:
   "section 44(3)", "s 41(4)", "reg 4.10" name a provision, resolved at the provision
   level, first mention first, only where it is held. */
const CITATION = /(?<![\w'’])(?<kind>sections?|subsections?|ss?|regulations?|subregulations?|regs?|r)\.?\s?(?<number>\d+[A-Za-z]{0,2}(?:\.\d+[A-Za-z]{0,2})?)(?![\w.]*\d)/gi;
const REGULATION = ["regulation", "regulations", "subregulation", "subregulations", "reg", "regs", "r"];

export function namedProvisions(text, held) {
  const out = [];
  for (const m of String(text || "").matchAll(CITATION)) {
    const ref = (REGULATION.includes(m.groups.kind.toLowerCase()) ? "TMR1995/r" : "TMA1995/s") + m.groups.number.toUpperCase();
    if (held && Object.prototype.hasOwnProperty.call(held, ref) && !out.includes(ref)) out.push(ref);
  }
  return out;
}

/* PU-0004 at answer time — `search.authority.conflations`, rule for rule (review F1,
   ADR-0121). A sentence that says the legislation requires, provides or states
   something, in an answer that cites no provision of it, is flagged — never removed.
   A clause naming the Manual before the verb, or a negated one, is not; only the
   match's own clause is read (R08). A warning, not a guarantee. */
export const AUTHORITY_MESSAGE = "Says the legislation requires this, but the answer cites no provision for it — only " +
  "the Manual, which states practice and does not bind the Registrar's discretion (PU-0004). Check the provision itself.";
const VERB = "(?:requires?|provides?|states?|says|prescribes?|mandates?|obliges?|imposes?)";
const WHOLE = new RegExp(String.raw`\bthe (?<what>Act|Regulations|legislation)\b[^.;:]{0,40}?\b${VERB}\b`, "i");
const PART = new RegExp(String.raw`\b(?<kind>section|s|subsection|regulation|reg|r)\.?\s?(?<number>\d+[A-Z]{0,2}(?:\.\d+[A-Z]{0,2})?)` +
  String.raw`(?:\([0-9a-z]+\))*[^.;:]{0,40}?\b${VERB}\b`, "i");
const SENTENCE_BREAK = /(?<=[.!?])\s+(?=[A-Z"'“‘(])|\n+/;
const MANUAL = /\bManual\b/;
const CLAUSE_BREAK = /;|,\s*(?:and|but|while|whereas|although|though|yet|however)\b|\s(?:but|whereas|although)\s/gi;
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

function clauseOf(sentence, m) {
  let start = 0;
  for (const brk of sentence.slice(0, m.index).matchAll(CLAUSE_BREAK)) start = brk.index + brk[0].length;
  return sentence.slice(start, m.index + m[0].length);
}

export function authorityFlags(answer, cited) {
  const refs = (cited || []).map(String);
  const flags = [];
  for (let sentence of String(answer || "").split(SENTENCE_BREAK)) {
    sentence = sentence.trim();
    if (!sentence) continue;
    const matches = [PART, WHOLE].flatMap((p) => [...sentence.matchAll(new RegExp(p.source, "gi"))]);
    if (matches.some((m) => { const clause = clauseOf(sentence, m);
      return !MANUAL.test(clause) && !NEGATION.test(clause) && !supportedBy(m, refs); })) {
      flags.push({ sentence, message: AUTHORITY_MESSAGE });
    }
  }
  return flags;
}

/** One GRAPH PATH line — `bulk.jobs.path_line`, character for character: the
    relationship, its record and origin, and the modality and condition the record
    states (ADR-0136). A prepared answer's five-field path says it records none. */
export const AUTHORITIES = ["legislation", "manual", "both", "none"];

const BLOCK_START = /^(\([^()]+\)|\/[^()~]+)$/;
const LEAD_IN = /[Ss]ubject to (?:subsections?|subregulations?) ([^.;:]*)/g;

function hits(text, term) {
  const re = new RegExp(`(?<![a-z0-9])${term}(?![a-z0-9])`, "g");
  return [...text.toLowerCase().matchAll(re)].map((m) => m.index);
}

function windowed(text, terms, budget) {
  if (text.length <= budget) return { text, cut: null };
  const found = terms.flatMap((t) => hits(text, t).slice(0, 1));
  const anchor = found.length ? Math.min(...found) : 0;
  const start = Math.max(0, Math.min(anchor - Math.floor(budget / 3), text.length - budget));
  const end = start + budget;
  return { text: (start ? "…" : "") + text.slice(start, end) + (end < text.length ? "…" : ""),
    cut: `characters ${start}-${end} of ${text.length}` };
}

/** `bulk.jobs.excerpt`, character for character (A06). */
export function excerpt(ref, text, units, terms, chat) {
  terms = [...new Set(terms)];
  if (!/^(TMA|TMR)/.test(ref)) return windowed(text, terms, chat.manual_chars);
  if (text.length <= chat.law_chars) return { text, cut: null };
  const blocks = [];
  for (const [uref, utext] of units || []) {
    const suffix = uref.slice(ref.length);
    if (!blocks.length || BLOCK_START.test(suffix)) blocks.push([suffix || uref, utext]);
    else blocks[blocks.length - 1][1] += " " + utext;
  }
  if (blocks.length < 2) return windowed(text, terms, chat.law_chars);
  const score = blocks.map(([, body]) => terms.filter((t) => hits(body, t).length).length);
  const chosen = new Set();
  let used = 0;
  for (const i of blocks.map((_, i) => i).sort((a, b) => score[b] - score[a] || a - b)) {
    if (used + blocks[i][1].length <= chat.law_chars) { chosen.add(i); used += blocks[i][1].length; }
  }
  const labels = new Map(blocks.map(([label], i) => [label, i]));
  for (const i of [...chosen].sort((a, b) => a - b)) {
    for (const m of blocks[i][1].matchAll(LEAD_IN)) {
      for (const label of m[1].match(/\(\w+\)/g) || []) if (labels.has(label)) chosen.add(labels.get(label));
    }
  }
  if (!chosen.size) return windowed(text, terms, chat.law_chars);
  const order = [...chosen].sort((a, b) => a - b);
  const parts = [];
  let previous = -1;
  for (const i of order) {
    if (i !== previous + 1) parts.push("…");
    parts.push(blocks[i][1]);
    previous = i;
  }
  if (previous !== blocks.length - 1) parts.push("…");
  const omitted = blocks.map(([label], i) => (chosen.has(i) ? null : label)).filter((x) => x !== null);
  const named = (xs) => (xs.length <= 12 ? xs.join(", ") : `${xs.slice(0, 12).join(", ")} and ${xs.length - 12} more`);
  return { text: parts.join(" "), cut: `parts shown: ${named(order.map((i) => blocks[i][0]))}; omitted: ${named(omitted)}` };
}

export function pathLine(label, edge) {
  const [s, p, o, rid, origin, modality = "", when = "", hedge = ""] = edge;
  const qualified = (modality ? `modality "${modality}"` : "modality not recorded") + "; " +
    (when ? `applies when "${when}"` : "no condition recorded") + (hedge ? `; hedged "${hedge}"` : "");
  return `- ${label(s)} —${p}→ ${label(o)} (${rid}, ${origin}; ${qualified})`;
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

/** Where the reading's words sit in the question: capitals, curly marks and spacing
    ignored, and any quotation marks or end punctuation the model put round them. */
export function findWords(question, words) {
  const lower = (text) => {
    const [n, index] = normalised(text);
    return [n.split("").map((ch) => ch.toLowerCase()[0] ?? ch).join(""), index];
  };
  const [nq, index] = lower(question);
  const w = lower(String(words || ""))[0].trim().replace(/^["'(\[]+|["').,;:!?\]]+$/g, "").trim();
  if (w.length < 2) return null;
  const at = nq.indexOf(w);
  return at < 0 ? null : [index[at], index[at + w.length - 1] + 1];
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
