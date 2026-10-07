/* About — what this is, how it was made, how well it works, and its limits.

   The measurement is reported in both directions and claims nothing: which
   results become claims is the project owner's decision (OQ-0029). */

import { esc, fmt, load, kindColour } from "./app.js";

export async function render(root, { ontology }) {
  const [examples, chat, live] = await Promise.all([load("examples"), load("chat"), load("live").catch(() => ({ enabled: false }))]);
  const c = ontology.counts;
  const s = examples.summary || {};
  const kinds = examples.kinds;
  const pct = (x) => (x == null ? "—" : Math.round(x * 100));
  const diff = (v) => (v ? `${v[0] >= 0 ? "+" : "−"}${Math.abs(v[0] * 100).toFixed(1)} <span class="tiny">[${(v[1] * 100).toFixed(1)}, ${(v[2] * 100).toFixed(1)}]</span>` : "—");
  const row = (key, label) => s[key] ? `<tr><td>${esc(label)}</td><td class="num">${s[key].n}</td><td class="num">${pct(s[key]["ndcg:keyword"])}</td><td class="num">${pct(s[key]["ndcg:hybrid"])}</td><td class="num">${pct(s[key]["ndcg:ontology"])}</td><td class="num">${diff(s[key]["ndcg:ontology-keyword"])}</td><td class="num">${diff(s[key]["ndcg:ontology-hybrid"])}</td></tr>` : "";

  root.innerHTML = `
  <div class="wrap about">
    <h1>About this map</h1>
    <p class="lede">A working demonstration of what an ontology adds to the Trade Marks Manual of Practice and Procedure, built for
    examiners to explore, test and pick holes in.</p>

    <h2>What it is</h2>
    <p>An <b>ontology</b> is a shared, explicit description of a field: the ideas in it, what kind of thing each idea is, and how the ideas
    relate — with each statement tied to the text it comes from. Here the field is Australian trade marks examination, and the text is the
    Manual, the <i>Trade Marks Act 1995</i> and the <i>Trade Marks Regulations 1995</i>, captured at one point in time.</p>
    <table>
      <tr><th></th><th class="num">Signed by an expert</th><th class="num">Machine-written, unreviewed</th></tr>
      <tr><td>Ideas (concepts)</td><td class="num">${c.concepts.signed}</td><td class="num">${c.concepts.machine}</td></tr>
      <tr><td>Connections between ideas</td><td class="num">${c.relations.signed}</td><td class="num">${fmt(c.relations.machine)}</td></tr>
      <tr><td>Places an idea is named in the Manual</td><td class="num" colspan="2">${fmt(c.links)} links across ${fmt(c.passages_linked)} passages — found by matching wordings, not judged</td></tr>
    </table>
    <p class="small muted">"Signed" means a named trade marks expert read the record and put their name and a date to it. Everything else was written
    by a machine reading the Manual, and carries the model's name, the date, the passage it rests on and its reasoning. The two are never
    added together, and an unchecked record never becomes approved by being left alone.</p>

    <h2>The nine kinds</h2>
    <p>Four kinds describe how a decision is reasoned towards; the project owner set them. Five describe the process that reasoning sits inside;
    a machine proposed them. Which kind each idea belongs to was judged by a machine and has not been reviewed.</p>
    <ul class="small" style="padding-left:0;list-style:none">${ontology.kinds.map((k) => `<li style="margin:.25rem 0"><span class="dot" style="--c:${kindColour(k.id)}"></span> <b>${esc(k.label)}</b> — ${esc(k.plain)}</li>`).join("")}</ul>

    <h2>How Ask the Manual works</h2>
    <ol class="small">
      <li><b>Recognise.</b> The question is matched against every idea's wordings, including everyday phrasings a machine wrote for search.</li>
      <li><b>Follow.</b> The connections those ideas hold lead to related ideas.</li>
      <li><b>Gather and rank.</b> Passages naming those ideas, or citing their provisions, are fused with ordinary keyword search over the question's words.</li>
      <li><b>Answer.</b> A model writes an answer from those passages only, citing each claim. Code then checks every quote word for word against the
      passage, and drops any it cannot find. The model is told never to say how an application would be decided, and to keep practice and law apart.</li>
    </ol>
    <p class="small muted">Live answers use <code>${esc(chat.model)}</code> at ${esc(chat.effort)} reasoning effort${live.enabled ? "" : " (switched off on this copy of the site)"}.
    The ${examples.answers.length} prepared answers used the same instructions at ${esc(chat.measured_effort)} effort. Search in your browser runs without the
    meaning-vectors the measured system also used.</p>

    <h2>How well the search works</h2>
    <p>Three ways of searching were fixed before any result was graded, and each question's top ten passages were scored (nDCG@10, out of 100):
    <b>keyword</b> — words only, like a search box; <b>hybrid</b> — keyword plus matching by meaning, good modern search with no ontology;
    <b>ontology</b> — hybrid plus the steps above. Differences are shown with 95% intervals.</p>
    <div style="overflow-x:auto"><table>
      <tr><th>Questions</th><th class="num">n</th><th class="num">Keyword</th><th class="num">Hybrid</th><th class="num">Ontology</th><th class="num">Ontology − keyword</th><th class="num">Ontology − hybrid</th></tr>
      ${row("all", "All")}${Object.entries(kinds).map(([k, label]) => row(k, label)).join("")}
    </table></div>
    <p>Read both ways. Against keyword search, the ontology-assisted search ranked better passages, most clearly for questions in everyday
    words. Against modern search that also matches meaning, it ranked worse, by a small margin that is clearly real. Diagnosed afterwards:
    very common ideas (such as <i>Registrar</i>, named in hundreds of passages) pull loosely related passages into the top ten.</p>
    <p class="small muted">The ${examples.answers.length - (s.signed?.n || 0)} test questions were written by a model, and the passages graded by another model; the only human yardstick is the
    expert's own ${s.signed?.n || 10} questions, too few to establish a difference either way.</p>

    <h2>Limits</h2>
    <ul class="small">
      <li>It explains; it never decides. It does not apply the law to an application's facts and declines when asked to.</li>
      <li>No expert has read the machine's ideas, connections or answers.</li>
      <li>Twelve pairs of ideas were judged to be one idea under two records (for example <i>Registrar</i> and <i>Registrar of Trade Marks</i>) and are flagged for a person, not merged.</li>
      <li>Recognising an idea is matching its wordings: "who has to <i>sign</i>" matches the idea <i>sign</i>.</li>
      <li>One snapshot of the Manual. There is no update loop yet, though every record is anchored so that one can be built.</li>
    </ul>
  </div>`;
}
