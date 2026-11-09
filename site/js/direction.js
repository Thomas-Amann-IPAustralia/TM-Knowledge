/* For direction setting: what the foundation could do for the people informing the strategic
   direction of the Australian trade marks system (ADR-0151).

   The owner's framing: help decision makers and policy setters make informed decisions and
   understand the potential consequences. The working demonstrations are Trace a change (what rests
   on a provision or a Manual page, from the dependency index) and the what-if (an invented new
   right laid over the ontology, changing nothing, ADR-0149). The possibilities follow, each with
   how far off it is. A draft amendment's words never reach this site (ADR-0147). Classes are
   prefixed `dr-`. */

import { esc, fmt, load, refLabel, sourceOf } from "./app.js";
import { icon } from "./icons.js";
import { demoCard, possibilityCard, possibilityGrid, horizonKey, aboutLine } from "./illustrations.js";

export async function render(root) {
  const [stability, whatif] = await Promise.all([load("stability"), load("whatif")]);
  const provisions = stability.provisions || {};
  const weight = (ref) => provisions[ref].direct.length + provisions[ref].via_manual.length;
  const top = Object.keys(provisions).sort((a, b) => weight(b) - weight(a)).slice(0, 6);
  const max = Math.max(1, ...top.map(weight));
  const firstYear = Object.keys(stability.by_year)[0];
  const w = whatif.whatifs?.[0];

  root.innerHTML = `
  <div class="dr">
    <section class="au-hero aud-pol">
      <div class="wrap au-hero-in">
        <div>
          <span class="eyebrow">For direction setting · policy and strategy</span>
          <h1>Find what a legal change might affect</h1>
          <p class="lede">The Act, the Regulations and the Manual depend on one another in ways no one can hold in their head. Start with the recorded links between legislation, guidance and legal tests, and see what may need re-reading before you assess a change’s policy consequences.</p>
          ${aboutLine()}
        </div>
        <div class="au-art dr-art">
          <p class="dr-art-k">${icon("ripple")} Provisions with the most recorded links</p>
          <p class="tiny">Records resting on each provision in this snapshot, directly or through Manual passages that cite it, out of ${fmt(Object.keys(provisions).length)} provisions with any. Counts are links, not importance or risk.</p>
          <ol class="dr-bars">${top.map((ref) => `<li><a href="#/change/${esc(ref)}" aria-label="Trace ${esc(refLabel(ref))}: ${fmt(provisions[ref].direct.length)} direct, ${fmt(provisions[ref].via_manual.length)} through the Manual"><span class="dr-bl"><span class="law ${sourceOf(ref)}"><i class="mark" aria-hidden="true"></i></span>${esc(refLabel(ref))}</span>
            <span class="dr-bar"><i class="d" style="width:${((provisions[ref].direct.length / max) * 100).toFixed(1)}%"></i><i class="v" style="width:${((provisions[ref].via_manual.length / max) * 100).toFixed(1)}%"></i></span>
            <span class="dr-bn"><b>${fmt(provisions[ref].direct.length)}</b> + ${fmt(provisions[ref].via_manual.length)}</span></a></li>`).join("")}</ol>
          <p class="dr-key tiny"><span><i class="d"></i>direct: name it</span><span><i class="v"></i>via the Manual: rest on a passage citing it</span><span>Select one to trace it</span></p>
        </div>
      </div>
    </section>

    <div class="wrap">
      <div class="au-promise">
        <div>${icon("quote")}<span><b>Every dependency is traceable</b>Each one comes from a record quoting, or citing, the text it rests on.</span></div>
        <div>${icon("info")}<span><b>An empty answer is not “no impact”</b>Where nothing is recorded, it says “no recorded dependency”, never that a change is safe.</span></div>
        <div>${icon("flag")}<span><b>Scenarios never change the records</b>An invented change is marked as invented and laid over the foundation, never written into it.</span></div>
      </div>

      <section class="au-sec" aria-labelledby="dr-now">
        <div class="sec-head"><div><span class="eyebrow">Working now</span><h2 id="dr-now">Two ways to see what a change might touch</h2></div>
          <p>The Manual has had ${fmt(stability.events)} recorded amendments since ${esc(firstYear)}. Each one could reach guidance, tests and tools that rest on it.</p></div>
        <div class="fc-demos two">
          ${demoCard({ href: "#/change", art: "demo-change", k: "Change impact and dependency mapping", title: "Trace a change",
            text: "Choose a section of the Act, a regulation or a page of the Manual. See every record that rests on it, directly or through the Manual passages that cite it, and the Manual’s own amendment history.",
            points: [`${fmt(Object.keys(provisions).length)} provisions with recorded dependants`, "The counts first, with an optional guess", "Unclear citations are listed, never resolved by guessing"], go: "Trace a change" })}
          ${w ? demoCard({ href: "#/whatif", art: "demo-whatif", k: "New right impact modelling", title: "A new right: what would it touch?",
            text: "An invented register of geographical indications for any goods, laid over today’s examination practice. See the places practice would meet it, the questions each raises, and what would need to be re-read.",
            points: [`${fmt(w.touchpoints.length)} places practice would meet it`, `${fmt(w.totals.recheck)} records to re-read first, ${fmt(w.totals.recheck_via)} more after`, "A gap in the foundation, said out loud"], go: "Explore the scenario", state: "Invented scenario · AI-written · unreviewed" }) : ""}
        </div>
      </section>

      <section class="au-sec" aria-labelledby="dr-next">
        <div class="sec-head"><div><span class="eyebrow">Coming next</span><h2 id="dr-next">From seeing a change to planning it</h2></div>
          <p>Possibilities, not commitments. Each says what it would build on and what it would still need.</p></div>
        ${horizonKey()}
        ${possibilityGrid([
          possibilityCard({ art: "draft-test", horizon: "reach", title: "Test a draft amendment on example cases",
            text: "Apply a draft change to a copy of a legal test and see how invented cases would read under it, beside how they read today.",
            builds: "a command-line prototype that already does this for three invented amendments; drafts are kept off this site", needs: "an earlier version of the Act to compare against, and the project owner’s decision on any real draft" }),
          possibilityCard({ art: "monitoring", horizon: "reach", title: "Regulatory change monitoring",
            text: "Notice when a new version of the Act, the Regulations or the Manual is published, and list what rests on what changed.",
            builds: "the record of what rests on every provision and page, and the Manual’s own amendment history", needs: "regular, automatic capture of new versions" }),
          possibilityCard({ art: "exam-patterns", horizon: "data", title: "Examination consistency analytics",
            text: "Look across teams and years for similar issues handled differently, to find where guidance may need to be clearer.",
            needs: "examination records and decisions, and the project owner’s approval to use real case data" }),
          possibilityCard({ art: "compare-options", horizon: "reach", title: "Compare policy options",
            text: "Lay several options side by side and see which concepts, requirements and procedures each one would touch.",
            builds: "the record of dependencies and the scenario method shown on this site", needs: "a way to describe each option as a change to the records" }),
          possibilityCard({ art: "versions", horizon: "reach", title: "Version-aware legal research",
            text: "Reconstruct which text of the law applied on a given date, and which guidance stood beside it.",
            builds: "explanations that already name the text of the Act they quote, and say when the date that matters is unknown", needs: "earlier versions of the Act and the Manual captured" }),
          possibilityCard({ art: "consistency-guidance", horizon: "reach", title: "Policy consistency checking",
            text: "Find places where different parts of the Manual may say different things about the same question, for a person to look at.",
            builds: "concepts linked to every passage that names them", needs: "a reviewed method for comparing passages" }),
          possibilityCard({ art: "treaties", horizon: "data", title: "International treaty implementation analysis",
            text: "Trace which provisions, practices and procedures an international obligation touches.",
            needs: "the treaty texts, connected to the foundation" }),
        ])}
      </section>
    </div>
  </div>`;
}
