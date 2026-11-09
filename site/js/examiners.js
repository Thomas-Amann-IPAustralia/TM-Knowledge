/* For examiners: what the foundation does for trade marks examiners today, and what it could do
   next (ADR-0151).

   The owner's framing: helping examiners with basic information now (training: a concept explorer
   and a research assistant), more complex examination work later. The working demonstrations
   lead; the possibilities follow, each saying how far off it is and what it would need, never as a
   commitment. The hero is words alone, on the owner's annotations (ADR-0153). Nothing here says how
   an application will be decided. Classes are prefixed `ex-`; the shared cards are `fc-` and the
   section hero `au-`. */

import { fmt, load } from "./app.js";
import { icon } from "./icons.js";
import { demoCard, possibilityCard, possibilityGrid, horizonKey, aboutLine } from "./illustrations.js";

export async function render(root, { ontology }) {
  const examples = await load("examples");
  const c = ontology.counts;
  const concepts = c.concepts.signed + c.concepts.machine;
  const relations = c.relations.signed + c.relations.machine;

  root.innerHTML = `
  <div class="ex">
    <section class="au-hero aud-exam">
      <div class="wrap au-hero-in solo">
        <div>
          <span class="eyebrow">For examiners</span>
          <h1>Find relevant law and examination guidance, and see how they connect</h1>
          <p class="lede">Examination often means checking more than one source: what the Act or the Regulations require, what the Manual says about practice, and how the legal issues relate. These demonstrations are aimed first at examiners still building that knowledge: follow a concept to its recorded connections and source passages, or try a research answer that shows what each statement rests on. They are working demonstrations, not an assessed replacement for an examiner’s own research or judgement.</p>
          ${aboutLine()}
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
        <div class="sec-head"><div><span class="eyebrow">Working demonstrations</span><h2 id="ex-now">Explore an issue and check the sources</h2></div>
          <p>Start with a legal concept or a question. Both demonstrations read the same records. The value still to test is whether they make relevant material easier to find and review.</p></div>
        <div class="fc-demos two">
          ${demoCard({ href: "#/concepts", art: "demo-concepts", k: "Legal concept explorer", title: "Explore a legal concept",
            text: "Start from a concept such as deceptive similarity, distinctiveness or honest concurrent use, then follow its recorded connections: what can give rise to it, what bears on it, which exceptions or other issues may be relevant, and the legal test it belongs to.",
            points: ["Each recorded connection quotes the sentence it rests on", "Other names it goes by, and names it must not be confused with", "Where the Manual discusses it, Part by Part"], go: "Explore a concept" })}
          ${demoCard({ href: "#/ask", art: "demo-ask", k: "Research assistant for newer examiners", title: "Ask a research question",
            text: `Ask in your own words. It finds the provisions and the Manual passages, says what each concept in the question means, shows a related legal test where the records hold one, and writes an answer that labels every statement law, practice or unsupported, with the words it quotes beneath it. The tool checks that each quotation exists in the source; it does not check that the answer is right, so open the sources and check that they support each statement. ${fmt(examples.answers.length)} example questions have saved answers.`,
            points: ["Every statement labelled law, practice or no matching quotation", "The quoted words under each statement, one click from the passage", "Never says how an application will be decided"], go: "Ask a question", state: "Answers are AI-written and unreviewed" })}
        </div>
      </section>

      <section class="au-sec" aria-labelledby="ex-next">
        <div class="sec-head"><div><span class="eyebrow">Possible future uses</span><h2 id="ex-next">Possible tools for more complex examination work</h2></div>
          <p>Possibilities, not commitments. Each says what it would build on and what it would still need.</p></div>
        ${horizonKey()}
        ${possibilityGrid([
          possibilityCard({ art: "evidence", horizon: "reach", title: "Evidence requirement assistant",
            text: "For a ground of rejection, list the kinds of evidence the guidance describes and what each piece must show, such as use in Australia before the filing date.",
            builds: "the section 41 test, which already sets out what evidence of use is meant to show", needs: "the same for the other grounds, and expert review" }),
          possibilityCard({ art: "change-alerts", horizon: "reach", title: "Knowledge change management",
            text: "When the law or the guidance changes, flag the training material, checklists and templates examiners use that rest on what changed.",
            builds: "the record of what rests on every provision and Manual page", needs: "regular capture of new versions of the Act and the Manual, and a list of the resources to watch" }),
          possibilityCard({ art: "preservation", horizon: "reach", title: "Expert knowledge preservation",
            text: "Experienced examiners’ readings captured as signed records, so what they know stays when they change roles or leave.",
            builds: "a review process that records who signed what and when, always kept apart from what AI wrote", needs: "examiners’ time to review, and the project owner’s decision to begin" }),
          possibilityCard({ art: "learning", horizon: "reach", title: "Personalised learning and development",
            text: "Learning paths built from the concepts an examiner is working through, with practice cases and the points most often confused.",
            builds: "invented practice cases, legal tests with their facts and assessments marked, and the names each concept must not be confused with", needs: "a record of what each examiner has covered, and a decision on how learning is tracked" }),
          possibilityCard({ art: "related-matters", horizon: "data", title: "Related examination matter discovery",
            text: "Find other matters that raised the same legal issues, for similar goods or services, or on similar facts.",
            needs: "examination records and decisions, connected to the concepts, and the project owner’s approval to use real case data" }),
          possibilityCard({ art: "consistency-point", horizon: "data", title: "Examination consistency assistant",
            text: "While an examiner weighs an issue, show how similar issues were approached before and point to the relevant guidance, for the examiner to consider.",
            needs: "examination records and decisions, and the project owner’s approval to use real case data" }),
        ])}
        <p class="ex-never">${icon("info")}<span>None of these would decide an application, or say how one should be decided. They would bring the right material to the examiner, who decides.</span></p>
      </section>
    </div>
  </div>`;
}
