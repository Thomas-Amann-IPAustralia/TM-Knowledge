/* For the public: what the foundation could do for IP Australia's customers, with working
   demonstrations on invented applications (ADR-0151).

   The owner's purpose for customers: better understanding of trade mark requirements, the
   application process and objections raised in examination, likely through a conversational
   assistant with clear visuals (ADR-0138). The demonstrations are the customer explanation preview
   (ADR-0146) on invented matters; this page says loudly that they are not tested with customers,
   not advice and never an outcome, and what may be tested with customers and on whose decision
   (moved here from What's next, CHAT-0094). Testing with customers, real case data and publishing
   to customers stay the project owner's decisions (CLAUDE.md §3a). Classes are prefixed `pu-`. */

import { esc, fmt, load } from "./app.js";
import { icon } from "./icons.js";
import { demoCard, possibilityCard, horizonKey, aboutLine } from "./illustrations.js";

export async function render(root, { ontology, params }) {
  const explain = await load("explain");
  const c = ontology.counts;
  const sample = explain.matters.find((m) => m.issues.some((i) => i.test)) || explain.matters[0];

  root.innerHTML = `
  <div class="pu">
    <section class="au-hero aud-pub">
      <div class="wrap au-hero-in">
        <div>
          <span class="eyebrow">For the public</span>
          <h1>Help people understand trade marks, and get the most out of the system</h1>
          <p class="lede">Applying for a trade mark means meeting legal requirements, following a process and sometimes answering an objection. The same foundation that helps examiners can explain each of these in plain language, with pictures and the sources behind them.</p>
          ${aboutLine("The examples here use invented applications. They have not been formally tested with customers, and they are not legal advice.")}
        </div>
        <div class="au-art pu-art">${sample ? miniCase(sample) : ""}</div>
      </div>
    </section>

    <div class="wrap">
      <div class="au-promise">
        <div>${icon("chat")}<span><b>Plain language first, detail on request</b>One step at a time, with the law’s own words and the Manual a click away.</span></div>
        <div>${icon("scale")}<span><b>Clear about who judges what</b>It shows which points are facts a record can settle and which are the examiner’s judgement.</span></div>
        <div>${icon("shield")}<span><b>Never predicts an outcome</b>It asks only for the facts that would change the explanation, and says what it cannot tell.</span></div>
      </div>

      <section class="au-sec" aria-labelledby="pu-now">
        <div class="sec-head"><div><span class="eyebrow">Try it now</span><h2 id="pu-now">Three explanations, built from the same rules</h2></div>
          <p>Each runs on ${fmt(c.fictional_matters)} invented applications, built to show situations that are hard to explain.</p></div>
        <div class="fc-demos three">
          ${demoCard({ href: "#/customers/objection", art: "demo-objection", k: "Explain my objection", title: "Understand an objection",
            text: "Walk through an examiner’s objection one step at a time: what it is about, what the law looks at, what could change things, and where the application is now.",
            go: "Walk through an example" })}
          ${demoCard({ href: "#/customers/requirements", art: "demo-requirements", k: "What the law requires", title: "See what a rule requires",
            text: `What ${fmt(c.tests)} sections of the Act ask, set out as conditions, exceptions and what can be done, with no application needed.`,
            go: "See a rule explained" })}
          ${demoCard({ href: "#/customers/process", art: "demo-journey", k: "Guided application journey", title: "Follow the application journey",
            text: "Each stage from filing to registration, who acts at each one, what moves it on, and the time rules that apply.",
            go: "Follow the journey" })}
        </div>
      </section>

      <section class="pu-testing" id="customers" tabindex="-1" aria-labelledby="pu-t">
        <div class="sec-head"><div><span class="eyebrow">Before customers see it</span><h2 id="pu-t">What we may test with customers</h2></div>
          <p><span class="pill prototype">Not started · no formal testing with customers yet</span></p></div>
        <div class="grid-4 pu-quad">
          <article class="card card-pad"><span class="pu-qi">${icon("question")}</span><h3>What would be tested</h3><ul class="small">
            <li>Whether someone who has received an objection understands what it means, what they could do, and where their application is.</li>
            <li>Whether the pictures, and their text equivalents, make that clearer than words alone.</li>
            <li>Whether it asks only for the facts that change the explanation, and says what it does not know.</li></ul></article>
          <article class="card card-pad"><span class="pu-qi">${icon("route")}</span><h3>How, and in what order</h3><ul class="small">
            <li>Invented applications first: ${fmt(c.fictional_matters)} exist, each built to exercise a hard case (two objections, an unknown date, a discretion, evidence from the wrong period, an objection known only from the customer’s own words).</li>
            <li>No real customer data, real application or real examination report is used until the project owner approves it.</li>
            <li>Before customer testing, review the records and check whether each quotation supports the statement it accompanies.</li>
            <li>The project owner decides when, with whom and how it is tested, and whether it is published to customers at all.</li></ul></article>
          <article class="card card-pad"><span class="pu-qi">${icon("target")}</span><h3>What success would mean</h3><ul class="small">
            <li>A person understands their situation and their options better than before.</li>
            <li>Never that it predicted an outcome: success is understanding, not a decision.</li></ul></article>
          <article class="card card-pad"><span class="pu-qi">${icon("shield")}</span><h3>What it will never do</h3><ul class="small">
            <li>Say how an application will be decided, or give legal advice.</li>
            <li>Turn a “may” into a “must”, or decide a question a person must assess (such as whether two trade marks are deceptively similar).</li>
            <li>Work out a deadline: it explains the time rules and points to the dates the report states.</li></ul></article>
        </div>
      </section>

      <section class="au-sec" aria-labelledby="pu-next">
        <div class="sec-head"><div><span class="eyebrow">Coming next</span><h2 id="pu-next">Helping customers through the whole system</h2></div>
          <p>Possibilities, not commitments. Each says what it would build on and what it would still need.</p></div>
        ${horizonKey()}
        <div class="fc-grid">
          ${possibilityCard({ art: "assistant", horizon: "reach", title: "A guided assistant with clear visuals",
            text: "A conversation that explains requirements, the process and objections, drawing the same pictures as these demonstrations and showing the source for each point.",
            builds: "the explanations and pictures on this site, and the checked, cited answers examiners already get", needs: "testing with customers, and the project owner’s approval before any customer sees it" })}
          ${possibilityCard({ art: "prefiling", horizon: "reach", title: "Pre-filing education",
            text: "Before someone invests in a brand, explain the questions examination asks of a trade mark, such as whether it can distinguish the goods and whether it conflicts with an earlier mark.",
            builds: "the legal tests already set out for sections 41, 43 and 44", needs: "plain-language wording tested with customers, and more of the Act set out as rules" })}
          ${possibilityCard({ art: "personal-journey", horizon: "reach", title: "A journey for your stage",
            text: "Show only the guidance that matters where an application is now, instead of the whole website.",
            builds: "the process from filing to registration, and what follows an examination report", needs: "a connection to an application’s status, with the project owner’s approval" })}
          ${possibilityCard({ art: "non-use", horizon: "reach", title: "Non-use removal guide",
            text: "Explain what is involved in asking for a registered trade mark that has not been used to be removed, and the evidence each side provides.",
            builds: "the Act and the Manual, which the foundation already holds", needs: "the removal provisions set out as a legal test and a procedure" })}
          ${possibilityCard({ art: "own-report", horizon: "data", title: "Explain my own report",
            text: "Select your own examination report and get the same step-by-step explanation for your real application.",
            needs: "a connection to examination reports, and the project owner’s approval to use real case data" })}
          ${possibilityCard({ art: "gs-finder", horizon: "data", title: "Goods and services finder",
            text: "Describe a business in everyday words and find the matching goods and services descriptions and their classes.",
            needs: "IP Australia’s list of goods and services descriptions, connected to the foundation" })}
          ${possibilityCard({ art: "spec-check", horizon: "data", title: "Specification check",
            text: "Flag unclear, very broad or inconsistent wording in a draft list of goods and services before it is filed.",
            needs: "the goods and services list, and the Manual’s guidance on specifications set out as rules" })}
          ${possibilityCard({ art: "readiness", horizon: "data", title: "Readiness check before filing",
            text: "Point out missing information, or issues worth a closer look, before an application is filed.",
            needs: "the details an application form holds, and more of the Act set out as rules" })}
        </div>
      </section>
    </div>
  </div>`;

  if (params[0] === "customers") {
    const target = root.querySelector("#customers");
    requestAnimationFrame(() => { target.scrollIntoView({ block: "start" }); target.focus({ preventScroll: true }); });
  }
}

/** A small preview of one invented matter: the trade mark and the conditions its objection turns
    on, each marked as a fact or an assessment with the state the explanation records. */
function miniCase(m) {
  const issue = m.issues.find((i) => i.test);
  // The conditions as the rule joins them at the top: a group of alternatives is one line, with the
  // state the explanation records for the group.
  const leavesOf = (n) => (n.children ? n.children.flatMap(leavesOf) : [n]);
  const top = issue ? (issue.test.condition.children || [issue.test.condition]).map((n) => (n.children
    ? { ...n, kind: new Set(leavesOf(n).map((l) => l.kind)).size === 1 ? leavesOf(n)[0].kind : "fact" } : n)) : [];
  const mark = { met: "✓", not_met: "✗", open: "?" };
  return `<a class="pu-mini" href="#/customers/objection/${esc(m.matter)}" aria-label="Walk through the invented case ${esc(m.sign)}">
    <span class="pu-mini-k">Invented example</span>
    <span class="pu-mini-sign">${esc(m.sign)}</span>
    ${issue ? `<span class="pu-mini-t">${esc(issue.test.title)}</span>
    <ul>${top.slice(0, 4).map((l) => `<li class="${esc(l.kind)}"><span class="pu-mini-st ${esc(l.state || "open")}" aria-hidden="true">${mark[l.state] || "?"}</span><span class="pu-mini-kind">${l.kind === "evaluative" ? "Assessment" : "Fact"}</span><span class="pu-mini-x">${esc(l.text)}</span></li>`).join("")}</ul>` : ""}
    <span class="link-arrow">Walk through it ${icon("arrow")}</span>
  </a>`;
}
