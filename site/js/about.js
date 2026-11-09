/* Where it stands: how well it works, what is still to be decided and by whom, exactly what this
   build is, its limits, and what it is built from.

   The measurement is reported in both directions and claims nothing: which results become claims
   is the project owner's decision (OQ-0029). Each difference is drawn with its 95% interval and
   said in words (better, worse, or not established), so colour is never the only way to read it.
   Classes: `ab-`. */

import { esc, fmt, load } from "./app.js";
import { difference } from "./home.js";
import { term } from "./glossary.js";
import { icon } from "./icons.js";
import { crumb } from "./layers.js";

// The verdict first, then what has not been tested, then authorship, sources and method; the
// project owner's open decisions last (UX review F25).
const SECTIONS = [["ab-measure", "How well the search works"], ["ab-limits", "What has not been tested"], ["ab-records", "Authors and reviewers"],
  ["ab-build", "Which sources this version uses"], ["ab-how", "How the research search works"], ["ab-gates", "Decisions for the project owner"]];

export async function render(root, { ontology }) {
  const [examples, chat, build] = await Promise.all([load("examples"), load("chat"), load("build")]);
  const deps = build.dependencies || {};
  const c = ontology.counts;
  const s = examples.summary || {};
  const groups = [["all", "All questions"], ...Object.entries(examples.kinds)].filter(([k]) => s[k]);
  const stale = Array.isArray(deps.stale) ? deps.stale.length : deps.stale || 0;

  root.innerHTML = `
  <div class="ab">
    <header class="wrap page-head">
      <div>
        ${crumb("nerds", "Results and limits")}
        <h1>What we tested and what we know</h1>
        <p class="lede">See how the search performed, who wrote and reviewed the records, which sources this version uses and what still needs testing.</p>
      </div>
    </header>
    ${s.all ? `<div class="wrap"><div class="ab-verdict-box" role="note">
      <span class="eyebrow">The evidence so far, in one paragraph</span>
      <p>On ${fmt(s.all.n)} test questions, the map-guided search ranked relevant passages ${difference(s.all["ndcg:ontology-keyword"], "higher", "lower")} than keyword search, and ${difference(s.all["ndcg:ontology-hybrid"], "higher", "lower")} than search by meaning.
      That measures how the search ranks passages. It does not show that an answer is right.</p>
      <p class="small"><b>Not yet tested:</b> whether answers are correct, the legal tests, the procedures, the customer explanations and the change tracing. No trade marks expert has reviewed the AI-written records.</p>
    </div></div>` : ""}
    <div class="wrap ab-layout">
      <nav class="ab-nav" aria-label="On this page">${SECTIONS.map(([id, label]) => `<button type="button" data-jump="${id}">${esc(label)}</button>`).join("")}</nav>
      <div class="ab-main">

        <section id="ab-measure" class="ab-sec" tabindex="-1">
          <h2>How well the search works</h2>
          <p class="muted">We tested three methods on the same questions. <b>Keyword search</b> looks for matching words. <b>Search by meaning</b> adds ${term("embedding", "similar meanings")}. <b>Map-guided search</b> also follows links between ideas. A ${term("ndcg", "ranking score")} out of 100 rewards relevant passages near the top of the first 10 results. The ${term("interval", "95% interval")} shows the uncertainty in each comparison.</p>
          <figure class="card ab-chart" aria-label="The ontology-guided search compared with each other search, by kind of question">
            <div class="ab-row ab-head" aria-hidden="true"><span></span><span class="ab-scale"><span>← worse</span><span>no difference</span><span>better →</span></span><span></span><span></span></div>
            ${groups.map(([key, label]) => `<div class="ab-group">
              <p class="ab-gl"><b>${esc(label)}</b> <span class="tiny">${fmt(s[key].n)} questions</span></p>
              ${diffRow("Against keyword search", s[key]["ndcg:ontology-keyword"], scale(groups, s))}
              ${diffRow("Against search by meaning", s[key]["ndcg:ontology-hybrid"], scale(groups, s))}</div>`).join("")}
            <figcaption class="tiny">The chart shows how many points the map-guided search gained or lost against each comparison method. Each bar is a 95% interval. If it includes zero, these questions do not establish which method performed better.</figcaption>
          </figure>
          <details><summary>The same numbers as a table</summary><div class="det-body ab-scroll"><table class="ab-table">
            <thead><tr><th>Questions</th><th class="num">n</th><th class="num">Keyword</th><th class="num">By meaning</th><th class="num">Ontology</th><th class="num">Ontology − keyword</th><th class="num">Ontology − by meaning</th></tr></thead>
            <tbody>${groups.map(([key, label]) => tableRow(s[key], label)).join("")}</tbody></table></div></details>
          <div class="ab-read">
            <p><b>What the tests found.</b> The map ranked relevant passages higher than keywords alone, especially for everyday questions. Across all questions it scored slightly lower than search by meaning, and that small gap is a real one. A later check suggested one reason: common terms such as <i>Registrar</i> can bring less relevant passages into the first 10 results.</p>
            <p class="small muted">AI wrote ${fmt(examples.answers.length - (s.signed?.n || 0))} of the test questions. Another model rated the passages. A person reviewed ${fmt(s.signed?.n || 0)} questions and the passages each should find. That group was too small to establish which method performed better. The project owner decides which findings to publish externally.</p>
          </div>
        </section>
        <section id="ab-limits" class="ab-sec" tabindex="-1">
          <h2>What has not been tested, and other limits</h2>
          <ul class="ab-limits">
            <li>${icon("scale")}<span>It explains; it never decides. It does not apply the law to an application's facts and declines when asked to.</span></li>
            <li>${icon("eye")}<span>No trade marks expert has yet reviewed the AI-written ideas, connections or answers.</span></li>
            <li>${icon("connect")}<span>A model suggested ${fmt((c.merges?.merged || 0) + (c.merges?.kept_apart || 0))} pairs of ideas were one idea under two records.
              On the project owner's rulings, ${fmt(c.merges?.merged || 0)} were merged (for example <i>Registrar of Trade Marks</i> into <i>Registrar</i>) and
              ${fmt(c.merges?.kept_apart || 0)} kept apart as different ideas.</span></li>
            <li>${icon("search")}<span>Matching words can find the wrong idea. For example, “who has to <i>sign</i>” might match a record about a <i>sign</i> used as a trade mark.</span></li>
            <li>${icon("clock")}<span>The site uses one saved copy of the Manual. There is no process yet for updating it.
              <a href="#/change">Trace a change</a> lists records linked to a page or provision.</span></li>
            <li>${icon("info")}<span>The search over the Act and the Regulations, the legal tests, the process templates and the customer explanations have not been measured.</span></li>
          </ul>
        </section>


        <section id="ab-records" class="ab-sec" tabindex="-1">
          <h2>Who wrote and reviewed the records?</h2>
          <p class="muted">Everything above rests on an ${term("ontology")}: a shared, explicit description of a field, the ideas in it, what kind of thing
          each idea is, and how they relate, with each statement tied to the text it comes from. Here the field is Australian trade marks examination,
          and the text is the Manual, the <i>Trade Marks Act 1995</i> and the <i>Trade Marks Regulations 1995</i>, captured at one point in time.</p>
          <div class="card ab-who">
            <div class="ab-who-key"><span><i class="ab-sw reviewed"></i>Reviewed by a trade marks expert</span><span><i class="ab-sw machine"></i>Written by a machine, not reviewed</span></div>
            ${whoRow("Ideas", c.concepts.signed, c.concepts.machine, "#/map")}
            ${whoRow("Connections between ideas", c.relations.signed, c.relations.machine, "#/table/connections")}
            ${whoRow("Definitions of ideas", 0, c.definitions, "#/table/ideas")}
            ${whoRow("Corrections to reviewed records", 0, c.corrections, null)}
            ${whoRow("Structured legal tests", 0, c.tests, "#/table/tests")}
            ${whoRow("Process templates", 0, c.processes, "#/table/processes")}
            <p class="tiny ab-links">And ${fmt(c.links)} places an idea is named in the Manual, across ${fmt(c.passages_linked)} passages: found by matching wordings, not judged.</p>
          </div>
          <p class="small muted">Each AI-written record names the model, date and source and explains its reasoning. It keeps its unreviewed label until an expert reviews it. A correction changes how a record is shown without changing the record itself, and says so. Explore the records:
          <a href="#/rules">rules as code</a>, <a href="#/map/kinds">the kinds of idea</a>, <a href="#/standards">the standards</a>.</p>
        </section>

        <section id="ab-build" class="ab-sec" tabindex="-1">
          <h2>Which sources this version uses</h2>
          <p class="muted">Each release lists the versions of the software, Manual and legislation it used. Use these details to reproduce a result.</p>
          <dl class="card ab-build">
            <dt>Built</dt><dd>${esc(build.generated || "")}, from revision <code>${esc((build.revision || "unknown").slice(0, 12))}</code> of the repository</dd>
            <dt>The Manual</dt><dd>${esc(build.manual?.line || "")}. ${esc(build.manual?.note || "")}</dd>
            ${(build.law || []).map((l) => `<dt>${esc(l.name)}</dt><dd>${esc(l.line)}: compilation ${esc(l.compilation)} (${esc(l.register_id)})</dd>`).join("")}
            <dt>The snapshot</dt><dd><code>${esc((build.graph?.upstream?.commit || "").slice(0, 12))}</code> of the extraction project, read and never edited</dd>
            <dt>Answers</dt><dd>prepared with instructions ${esc(build.answers?.prepared || "")}; live with ${esc(build.answers?.live || "")}</dd>
            <dt>Dependencies</dt><dd>${fmt(deps.dependencies || 0)} recorded dependencies of ${fmt(deps.records || 0)} records on ${fmt(deps.refs || 0)} passages and provisions;
              ${fmt(stale)} whose quoted text has since changed</dd>
          </dl>
        </section>


        <section id="ab-how" class="ab-sec" tabindex="-1">
          <h2>How the research search works</h2>
          <ol class="ab-steps">
            <li><b>Recognise</b><span>The question is matched against every idea's wordings, including everyday phrasings a machine wrote for search.</span></li>
            <li><b>Follow</b><span>The search follows links from matching ideas to related ones.</span></li>
            <li><b>Gather and rank</b><span>Passages naming those ideas, or citing their provisions, are fused with keyword search over the question's words.
              The Act and the Regulations are searched apart and listed in a card of their own.</span></li>
            <li><b>Answer</b><span>A model writes an answer from those passages only, citing each claim. Code checks every quote word for word and drops any
              it cannot find. The model is told never to say how an application would be decided, and to keep practice and law apart.</span></li>
          </ol>
          <p class="small muted">Live answers use <code>${esc(chat.model)}</code> at ${esc(chat.effort)} reasoning effort.
          The ${fmt(examples.answers.length)} prepared answers were written at ${esc(chat.measured_effort)} effort with the same instructions as live answers
          (${esc(chat.prepared_prompt_version)}): each connection's modality and the condition it applies under, complete provisions with every cut marked,
          each claim with its own quotes, and the rule never to conclude that a requirement, exception or step does not exist because the passages or
          connections do not mention it. Search in your browser runs without the meaning-vectors the measured system also used.
          <a href="#/how">Follow one question through the search, step by step</a>.</p>
        </section>
        <section id="ab-gates" class="ab-sec" tabindex="-1">
          <h2>Decisions for the project owner</h2>
          <p class="muted">The following steps need the project owner’s approval.</p>
          <div class="ab-gates">
            ${gate("users", "Testing with customers", `The <a href="#/customers">customer preview</a> is on this site so examiners can see it. Showing it to a customer, testing it with one, or publishing anything to customers needs the owner's approval first.`)}
            ${gate("file", "Real case data", "Every application in the preview is invented. Using a real application or examination report, even in a test, is the owner's decision.")}
            ${gate("chat", "What the AI can use to answer", "A related legal test appears beside the answer. The project owner decides whether the AI can also use that test when drafting its answer.")}
            ${gate("shield", "Expert review", "Nothing machine-written becomes approved until a named expert's decision is recorded; when, and by whom, is the owner's to arrange.")}
            ${gate("scale", "The next measurement", "Who writes and judges the next set of test questions, and which results become claims.")}
          </div>
          <div class="ab-never"><span class="pill never">Never</span><p><b>Deciding an application, or saying how one will be decided,</b> is out of scope, and no decision above changes that.</p></div>
        </section>
      </div>
    </div>
  </div>`;

  // the page's own index scrolls, and marks the section in view
  root.querySelectorAll("[data-jump]").forEach((b) => b.addEventListener("click", () => {
    const target = root.querySelector(`#${b.dataset.jump}`);
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    target.focus({ preventScroll: true });
  }));
  const links = new Map([...root.querySelectorAll("[data-jump]")].map((b) => [b.dataset.jump, b]));
  const seen = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) links.forEach((b, id) => b.classList.toggle("on", id === e.target.id));
  }, { rootMargin: "-30% 0px -60% 0px" });
  root.querySelectorAll(".ab-sec").forEach((sec) => seen.observe(sec));
  links.get(SECTIONS[0][0])?.classList.add("on");
  return () => seen.disconnect();
}

/** The scale every difference row shares: symmetric about no difference, in whole fives. */
function scale(groups, s) {
  const ends = groups.flatMap(([k]) => ["ndcg:ontology-keyword", "ndcg:ontology-hybrid"].flatMap((f) => (s[k][f] ? [s[k][f][1], s[k][f][2]] : [])));
  const m = Math.max(5, Math.ceil((Math.max(...ends.map((v) => Math.abs(v * 100))) + 1) / 5) * 5);
  return { m };
}

/** One difference: its interval as a bar, its estimate as a dot, and what it says in words. */
function diffRow(label, v, { m }) {
  if (!v) return "";
  const [est, lo, hi] = v.map((x) => x * 100);
  const W = 400, x = (n) => ((n + m) / (2 * m)) * W;
  const verdict = lo > 0 ? ["better", "Better"] : hi < 0 ? ["worse", "Worse"] : ["open", "Not established"];
  const ticks = [];
  for (let t = -m; t <= m; t += 5) ticks.push(t);
  const sign = (n) => `${n >= 0 ? "+" : "−"}${Math.abs(n).toFixed(1)}`;
  const num = (n) => `${n < 0 ? "−" : ""}${Math.abs(n).toFixed(1)}`;
  return `<div class="ab-row">
    <span class="ab-rl">${esc(label)}</span>
    <span class="ab-trackwrap"><svg viewBox="0 0 ${W} 26" preserveAspectRatio="none" class="ab-track" role="img" aria-label="${esc(`${label}: ${sign(est)} points, 95% interval ${lo.toFixed(1)} to ${hi.toFixed(1)}; ${verdict[1].toLowerCase()}`)}">
      ${ticks.map((t) => `<line x1="${x(t)}" x2="${x(t)}" y1="3" y2="23" class="${t === 0 ? "ab-zero" : "ab-tick"}"/>`).join("")}
      <line x1="${x(lo)}" x2="${x(hi)}" y1="13" y2="13" class="ab-ci ${verdict[0]}"/>
    </svg><i class="ab-dot ${verdict[0]}" style="left:${((x(est) / W) * 100).toFixed(2)}%" aria-hidden="true"></i></span>
    <span class="ab-num"><b>${sign(est)}</b> <span class="tiny">[${num(lo)}, ${num(hi)}]</span></span>
    <span class="ab-verdict ${verdict[0]}">${verdict[1]}</span>
  </div>`;
}

function tableRow(r, label) {
  const pct = (x) => (x == null ? "–" : Math.round(x * 100));
  const diff = (v) => (v ? `${v[0] >= 0 ? "+" : "−"}${Math.abs(v[0] * 100).toFixed(1)} <span class="tiny">[${(v[1] * 100).toFixed(1)}, ${(v[2] * 100).toFixed(1)}]</span>` : "–");
  return `<tr><td>${esc(label)}</td><td class="num">${r.n}</td><td class="num">${pct(r["ndcg:keyword"])}</td><td class="num">${pct(r["ndcg:hybrid"])}</td>
    <td class="num">${pct(r["ndcg:ontology"])}</td><td class="num">${diff(r["ndcg:ontology-keyword"])}</td><td class="num">${diff(r["ndcg:ontology-hybrid"])}</td></tr>`;
}

const gate = (ic, title, text) => `<article class="ab-gate"><div class="ab-gate-i">${icon(ic)}</div><div><h3>${title}</h3><p class="small muted">${text}</p></div></article>`;

/** Who wrote a set of records, as a bar split between reviewed and machine-written, said in numbers too. */
function whoRow(label, signed, machine, href) {
  const total = signed + machine;
  const name = href ? `<a href="${href}">${esc(label)}</a>` : esc(label);
  return `<div class="ab-whorow"><span class="ab-wl">${name}</span>
    <span class="ab-bar" role="img" aria-label="${esc(`${label}: ${total}, of which ${signed} reviewed by an expert and ${machine} machine-written`)}">
      ${signed ? `<i class="reviewed" style="flex:${signed}"></i>` : ""}${machine ? `<i class="machine" style="flex:${machine}"></i>` : ""}</span>
    <span class="ab-wn"><b>${fmt(total)}</b> <span class="tiny">${signed ? `${fmt(signed)} reviewed · ` : ""}${fmt(machine)} machine</span></span></div>`;
}
