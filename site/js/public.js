/* For the public: what the foundation could do for IP Australia's customers, with working
   demonstrations on invented applications (ADR-0151).

   The owner's purpose for customers: better understanding of trade mark requirements, the
   application process and objections raised in examination, likely through a conversational
   assistant with clear visuals (ADR-0138). The demonstrations are the customer explanation preview
   (ADR-0146) on invented matters; this page says that they are not tested with customers, not
   advice and never an outcome. The hero is words alone, and the plan for testing with customers
   left this page, on the owner's annotations (ADR-0153); the customer preview and the overview
   still say that testing, real case data and publishing to customers stay the project owner's
   decisions (CLAUDE.md §3a). Classes are prefixed `pu-`. */

import { fmt } from "./app.js";
import { icon } from "./icons.js";
import { demoCard, possibilityCard, possibilityGrid, horizonKey, aboutLine } from "./illustrations.js";

export function render(root, { ontology }) {
  const c = ontology.counts;

  root.innerHTML = `
  <div class="pu">
    <section class="au-hero aud-pub">
      <div class="wrap au-hero-in solo">
        <div>
          <span class="eyebrow">For the public</span>
          <h1>Understand trade mark requirements and what happens during examination</h1>
          <p class="lede">An applicant may need to understand a legal requirement, an objection from an examiner or the next step in the application process. These examples show how the same source-linked rules can be explained one step at a time, with pictures, and with the facts, judgements and unknowns kept apart.</p>
          ${aboutLine("The examples here use invented applications. They have not been formally tested with customers, and they are not legal advice.")}
        </div>
      </div>
    </section>

    <div class="wrap">
      <div class="au-promise">
        <div>${icon("chat")}<span><b>Plain language first, detail on request</b>One step at a time, with the law’s own words and the Manual a click away.</span></div>
        <div>${icon("scale")}<span><b>Clear about who judges what</b>It shows which points are facts a record can settle and which are the examiner’s judgement.</span></div>
        <div>${icon("shield")}<span><b>Never predicts an outcome</b>It asks only for the facts that would change the explanation, and says what it cannot tell.</span></div>
      </div>

      <section class="au-sec" aria-labelledby="pu-now">
        <div class="sec-head"><div><span class="eyebrow">Working demonstrations</span><h2 id="pu-now">Three explanations, built from the same rules</h2></div>
          <p>Each runs on ${fmt(c.fictional_matters)} invented applications, built to show situations that are hard to explain.</p></div>
        <div class="fc-demos three">
          ${demoCard({ href: "#/customers/objection", art: "demo-objection", k: "Fictional objection walkthrough", title: "Understand an objection",
            text: "Walk through an examiner’s objection on an invented application, one step at a time: what it is about, what the law looks at, what could change things, and where the application is now.",
            go: "Walk through an example" })}
          ${demoCard({ href: "#/customers/requirements", art: "demo-requirements", k: "What the law requires", title: "See what a rule requires",
            text: `What ${fmt(c.tests)} sections of the Act ask, set out as conditions, exceptions and what can be done, with no application needed.`,
            go: "See a rule explained" })}
          ${demoCard({ href: "#/customers/process", art: "demo-journey", k: "Guided application journey", title: "Follow the application journey",
            text: "One general path from filing to registration: who acts at each stage, what moves it on, and the time rules that apply. A real application’s path may differ, and no deadline is worked out.",
            go: "Follow the journey" })}
        </div>
      </section>

      <section class="au-sec" aria-labelledby="pu-next">
        <div class="sec-head"><div><span class="eyebrow">Possible future uses</span><h2 id="pu-next">Possible help for applicants, before and after filing</h2></div>
          <p>Possibilities, not commitments. Each says what it would build on and what it would still need.</p></div>
        ${horizonKey()}
        ${possibilityGrid([
          possibilityCard({ art: "assistant", horizon: "reach", title: "A guided assistant with clear visuals",
            text: "A possible conversational guide that could explain requirements, the process and objections, drawing the same pictures as these demonstrations and showing the source for each point. It would say what it does not know rather than guess.",
            builds: "the explanations and pictures on this site, and the cited answers examiners can already try", needs: "expert review of the records, testing with customers, operational controls, and the project owner’s approval before any customer sees it or any real application data is used" }),
          possibilityCard({ art: "prefiling", horizon: "reach", title: "Pre-filing education",
            text: "Before someone invests in a brand, explain the questions examination asks of a trade mark, such as whether it can distinguish the goods and whether it conflicts with an earlier mark.",
            builds: "the legal tests already set out for sections 41, 43 and 44", needs: "plain-language wording tested with customers, and more of the Act set out as rules" }),
          possibilityCard({ art: "own-report", horizon: "data", title: "Explain my own report",
            text: "Select your own examination report and get the same step-by-step explanation for your real application.",
            needs: "a connection to examination reports, and the project owner’s approval to use real case data" }),
          possibilityCard({ art: "personal-journey", horizon: "reach", title: "A journey for your stage",
            text: "Show only the guidance that matters where an application is now, instead of the whole website.",
            builds: "the process from filing to registration, and what follows an examination report", needs: "a connection to an application’s status, with the project owner’s approval" }),
          possibilityCard({ art: "non-use", horizon: "reach", title: "Non-use removal guide",
            text: "Explain what is involved in asking for a registered trade mark that has not been used to be removed, and the evidence each side provides.",
            builds: "the Act and the Manual, which the foundation already holds", needs: "the removal provisions set out as a legal test and a procedure" }),
          possibilityCard({ art: "gs-finder", horizon: "data", title: "Goods and services finder",
            text: "Describe a business in everyday words and find the matching goods and services descriptions and their classes.",
            needs: "IP Australia’s list of goods and services descriptions, connected to the foundation" }),
          possibilityCard({ art: "spec-check", horizon: "data", title: "Specification check",
            text: "Flag unclear, very broad or inconsistent wording in a draft list of goods and services before it is filed.",
            needs: "the goods and services list, and the Manual’s guidance on specifications set out as rules" }),
          possibilityCard({ art: "readiness", horizon: "data", title: "Readiness check before filing",
            text: "Point out missing information, or issues worth a closer look, before an application is filed.",
            needs: "the details an application form holds, and more of the Act set out as rules" }),
        ])}
      </section>
    </div>
  </div>`;
}
