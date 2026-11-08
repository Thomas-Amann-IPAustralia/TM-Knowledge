/* For examiners: what the foundation does for trade marks examiners today, and what it could do
   next (ADR-0151).

   The owner's framing: helping examiners with basic information now (training: a concept explorer
   and a research assistant), supercharging experienced examiners later. The working demonstrations
   lead; the possibilities follow, each saying how far off it is and what it would need, never as a
   commitment. Nothing here says how an application will be decided. Classes are prefixed `ex-`;
   the shared cards are `fc-` and the section hero `au-`. */

import { fmt, load } from "./app.js";
import { icon } from "./icons.js";
import { demoCard, possibilityCard, horizonKey, aboutLine } from "./illustrations.js";
import { preview } from "./concepts.js";

export async function render(root, { ontology }) {
  const examples = await load("examples");
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;

  root.innerHTML = `
  <div class="ex">
    <section class="au-hero aud-exam">
      <div class="wrap au-hero-in">
        <div>
          <span class="eyebrow">For examiners</span>
          <h1>Find the law and the guidance faster, and see how it fits together</h1>
          <p class="lede">For a new examiner, the foundation is a way into the Trade Marks Act, the Regulations and the Manual: the concepts, how they connect, and where each is written down. For an experienced examiner, it is the start of tools that could find related matters, keep expert knowledge and flag what has changed.</p>
          ${aboutLine()}
        </div>
        <div class="au-art ex-art">
          <p class="ex-art-k">${icon("connect")} One concept, every recorded connection</p>
          ${preview(ontology)}
          <p class="tiny">From the records as they stand. Select it to explore.</p>
        </div>
      </div>
    </section>

    <div class="wrap">
      <div class="au-promise">
        <div>${icon("book")}<span><b>The source is one click away</b>Every concept, connection and answer opens the passage it rests on, with the Act and the Regulations kept apart from the Manual.</span></div>
        <div>${icon("scale")}<span><b>Facts and assessments are marked</b>Each legal test says which conditions a record can settle and which an examiner must judge.</span></div>
        <div>${icon("shield")}<span><b>Nothing is passed off as expert-made</b>${fmt(c.concepts.machine)} of ${fmt(concepts)} concepts and ${fmt(c.relations.machine)} of ${fmt(relations)} connections were written by AI, and say so.</span></div>
      </div>

      <section class="au-sec" aria-labelledby="ex-now">
        <div class="sec-head"><div><span class="eyebrow">Working now</span><h2 id="ex-now">Helping new examiners find their way</h2></div>
          <p>Two working demonstrations. Both read the same records, and both show where every piece comes from.</p></div>
        <div class="fc-demos two">
          ${demoCard({ href: "#/concepts", art: "demo-concepts", k: "Legal concept explorer", title: "Explore a legal concept",
            text: "Start from a concept such as deceptive similarity, distinctiveness or honest concurrent use, then follow what can give rise to it, what bears on it, what overcomes it, and the legal test it belongs to.",
            points: ["Every connection quotes the sentence it rests on", "Names it goes by, and names it must not be confused with", "Where the Manual discusses it, Part by Part"], go: "Explore a concept" })}
          ${demoCard({ href: "#/ask", art: "demo-ask", k: "Research assistant", title: "Ask a research question",
            text: `Ask in your own words. It finds the relevant provisions and Manual passages, shows the legal test the question reaches, and writes an answer whose every statement is checked against its quotation. ${fmt(examples.answers.length)} example questions have saved answers.`,
            points: ["The law and the guidance listed apart", "Statements without a matching quotation are flagged", "Never says how an application will be decided"], go: "Ask a question", state: "Answers are AI-written and unreviewed" })}
        </div>
      </section>

      <section class="au-sec" aria-labelledby="ex-next">
        <div class="sec-head"><div><span class="eyebrow">Coming next</span><h2 id="ex-next">Supercharging experienced examiners</h2></div>
          <p>Possibilities, not commitments. Each says what it would build on and what it would still need.</p></div>
        ${horizonKey()}
        <div class="fc-grid">
          ${possibilityCard({ art: "evidence", horizon: "reach", title: "Evidence requirement assistant",
            text: "For a ground of rejection, list the kinds of evidence the guidance describes and what each piece must show, such as use in Australia before the filing date.",
            builds: "the section 41 test, which already sets out what evidence of use is meant to show", needs: "the same for the other grounds, and expert review" })}
          ${possibilityCard({ art: "learning", horizon: "reach", title: "Personalised learning and development",
            text: "Learning paths built from the concepts an examiner is working through, with practice cases and the points most often confused.",
            builds: "invented practice cases, legal tests with their facts and assessments marked, and the names each concept must not be confused with", needs: "a record of what each examiner has covered, and a decision on how learning is tracked" })}
          ${possibilityCard({ art: "preservation", horizon: "reach", title: "Expert knowledge preservation",
            text: "Experienced examiners’ readings captured as signed records, so what they know stays when they change roles or leave.",
            builds: "a review process that records who signed what and when, always kept apart from what AI wrote", needs: "examiners’ time to review, and the project owner’s decision to begin" })}
          ${possibilityCard({ art: "change-alerts", horizon: "reach", title: "Knowledge change management",
            text: "When the law or the guidance changes, flag the training material, checklists and templates examiners use that rest on what changed.",
            builds: "the record of what rests on every provision and Manual page", needs: "regular capture of new versions of the Act and the Manual, and a list of the resources to watch" })}
          ${possibilityCard({ art: "related-matters", horizon: "data", title: "Related examination matter discovery",
            text: "Find other matters that raised the same legal issues, for similar goods or services, or on similar facts.",
            needs: "examination records and decisions, connected to the concepts, and the project owner’s approval to use real case data" })}
          ${possibilityCard({ art: "consistency-point", horizon: "data", title: "Examination consistency assistant",
            text: "While an examiner weighs an issue, show how similar issues were approached before and point to the relevant guidance, for the examiner to consider.",
            needs: "examination records and decisions, and the project owner’s approval to use real case data" })}
        </div>
        <p class="ex-never">${icon("info")}<span>None of these would decide an application, or say how one should be decided. They would bring the right material to the examiner, who decides.</span></p>
      </section>
    </div>
  </div>`;
}
