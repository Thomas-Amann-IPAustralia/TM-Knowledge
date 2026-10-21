/* A what-if: an invented new right laid over the ontology as it stands (ADR-0149), a layer 2 page.

   Drawn from `data/whatif.json`, which `tm_knowledge.explain.whatif` builds from
   `scenarios/what-if.yaml`: the premise and the questions are a machine's, invented and stamped;
   every idea, connection, legal test, step, provision and passage they point at is a record that
   already exists, read as it is. The picture keeps the two apart by a line across it: above, the
   invented premise and its touch points (dashed, in the machine's colour); below, the ontology,
   drawn exactly as the rest of the site draws it. What would go back to be re-read is counted in
   Python, from the same dependency index Trace a change reads, never here.

   Nothing on this page states the law or how an application would be decided. Classes are
   prefixed `wi-`. */

import { esc, fmt, load, quoteBlock, refChip, refLabel, srcShape, stampIcon, statePill, structureHref, tip, FAMILIES, familyOf } from "./app.js";
import { icon } from "./icons.js";

const W = 1120, H = 640;
const Y = { premise: 52, point: 154, line: 226, idea: 326, idea2: 378, prov: 548 };

export async function render(root, { ontology, params }) {
  const data = await load("whatif");
  const w = data.whatifs[0];
  if (!w) {
    root.innerHTML = `<div class="wrap section"><h2>No what-if was built</h2><p class="muted">${esc((data.left_out || []).join(", "))}</p></div>`;
    return;
  }
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const tests = new Map((ontology.structures?.tests || []).map((t) => [t.id, t]));
  const processes = new Map((ontology.structures?.processes || []).map((p) => [p.id, p]));
  const points = w.touchpoints;
  let current = points.some((p) => p.id === params[1]) ? params[1] : points[0].id;

  // ---- the ideas in the order the touch points first name them, so lines run mostly down
  const ideas = [...new Set(points.flatMap((p) => p.ideas))].filter((id) => byId.has(id));
  const provs = Object.keys(w.rests_on_provision).sort((a, b) => parseInt(a.replace(/\D+/g, " ").trim(), 10) - parseInt(b.replace(/\D+/g, " ").trim(), 10));
  const xs = (n, i, pad = 80) => pad + ((W - 2 * pad) * (i + 0.5)) / n;
  const at = {};
  points.forEach((p, i) => { at[`tp:${p.id}`] = [xs(points.length, i, 70), Y.point]; });
  ideas.forEach((id, i) => { at[id] = [xs(ideas.length, i, 40), i % 2 ? Y.idea2 : Y.idea]; });
  provs.forEach((ref, i) => { at[ref] = [xs(provs.length, i, 110), Y.prov]; });
  const belongs = (pred) => points.filter(pred).map((p) => p.id).join(" ");
  const basisOn = (concept, ref) => (concept.basis || []).some((b) => b === ref || b.startsWith(`${ref}(`) || b.startsWith(`${ref}/`));
  const colour = (id) => FAMILIES[familyOf(ontology, byId.get(id)?.kind)].colour;
  const kindLabel = (id) => ontology.kinds.find((k) => k.id === byId.get(id)?.kind)?.label || "";
  const wrapWords = (text, max) => {
    const lines = [""];
    for (const word of String(text).split(/\s+/)) {
      if ((lines[lines.length - 1] + " " + word).trim().length > max && lines[lines.length - 1]) lines.push(word);
      else lines[lines.length - 1] = (lines[lines.length - 1] + " " + word).trim();
    }
    return lines.length > 2 ? [lines[0], `${lines[1].replace(/\W*$/, "")}…`] : lines;
  };
  const tspans = (lines, x, dy) => lines.map((l, i) => `<tspan x="${x}" dy="${i ? dy : 0}">${esc(l)}</tspan>`).join("");

  function picture() {
    const parts = [`<svg viewBox="0 0 ${W} ${H}" class="wi-svg" role="img" aria-labelledby="wi-svg-title">
      <title id="wi-svg-title">${esc(`${w.title}: an invented premise above the line, ${points.length} touch points, and below the line the ${ideas.length} ideas, ${provs.length} provisions and ${w.totals.tests} legal tests of the ontology they land on, unchanged. The text equivalent follows the picture.`)}</title>`];
    // the line between the invented and the recorded
    parts.push(`<rect x="0" y="0" width="${W}" height="${Y.line}" class="wi-above"/>
      <line x1="16" x2="${W - 16}" y1="${Y.line}" y2="${Y.line}" class="wi-line"/>
      <text x="22" y="${Y.line - 10}" class="wi-band machine">Invented · a machine's premise and questions</text>
      <text x="22" y="${Y.line + 22}" class="wi-band onto">The ontology as it stands · read, not changed</text>`);
    // premise → touch points
    const [px, py] = [W / 2, Y.premise];
    for (const p of points) {
      const [x, y] = at[`tp:${p.id}`];
      parts.push(`<path d="M${px} ${py + 22} C ${px} ${py + 62}, ${x} ${y - 66}, ${x} ${y - 28}" class="wi-edge invented" data-tp="${esc(p.id)}"/>`);
    }
    // touch point → idea, and touch point → provision (shown when its touch point is chosen)
    for (const p of points) {
      const [x, y] = at[`tp:${p.id}`];
      for (const id of p.ideas) {
        if (!at[id]) continue;
        const [ix, iy] = at[id];
        parts.push(`<path d="M${x} ${y + 28} C ${x} ${y + 90}, ${ix} ${iy - 70}, ${ix} ${iy - 11}" class="wi-edge lands" data-tp="${esc(p.id)}"/>`);
      }
      for (const ref of p.provisions) {
        const [vx, vy] = at[ref];
        parts.push(`<path d="M${x} ${y + 28} C ${x} ${y + 200}, ${vx} ${vy - 160}, ${vx} ${vy - 16}" class="wi-edge reach" data-tp="${esc(p.id)}"/>`);
      }
    }
    // the ontology's own connections among these ideas, drawn as arcs under the row
    const seen = new Set();
    for (const r of w.links) {
      const key = [r.s, r.p, r.o].join("|");
      if (seen.has(key) || !at[r.s] || !at[r.o]) continue;
      seen.add(key);
      const [ax, ay] = at[r.s], [bx, by] = at[r.o];
      const sag = Math.max(ay, by) + 34 + Math.abs(ax - bx) * 0.12;
      const label = `${byId.get(r.s).label} ${ontology.predicates[r.p]?.label || r.p} ${byId.get(r.o).label}`;
      parts.push(`<path d="M${ax} ${ay + 10} Q ${(ax + bx) / 2} ${sag}, ${bx} ${by + 10}" class="wi-edge recorded" data-tp="${esc(belongs((p) => p.ideas.includes(r.s) || p.ideas.includes(r.o)))}"
        data-tip="${esc(`<span class="tip-k">A connection already in the ontology · ${esc(r.id)}</span><b>${esc(label)}</b>`)}"/>`);
    }
    // the ideas' recorded basis in the provisions drawn
    for (const id of ideas) {
      const c = byId.get(id);
      for (const ref of provs) {
        if (!basisOn(c, ref)) continue;
        const [ix, iy] = at[id], [vx, vy] = at[ref];
        parts.push(`<path d="M${ix} ${iy + 10} L ${vx} ${vy - 14}" class="wi-edge basis" data-tp="${esc(belongs((p) => p.ideas.includes(id) && p.provisions.includes(ref)))}"
          data-tip="${esc(`<span class="tip-k">Recorded basis</span><b>${esc(c.label)}</b><span class="tip-s">rests on ${esc(refLabel(ref))}, as its record says</span>`)}"/>`);
      }
    }
    // the premise
    parts.push(`<g class="wi-premise" transform="translate(${px},${py})"><rect x="-210" y="-24" width="420" height="48" rx="24"/>
      <text y="-3" text-anchor="middle" class="wi-p1">A register of geographical indications</text>
      <text y="14" text-anchor="middle" class="wi-p2">invented · no such right exists · no draft assumed</text></g>`);
    // touch points
    for (const p of points) {
      const [x, y] = at[`tp:${p.id}`];
      parts.push(`<g class="wi-tp" data-tp="${esc(p.id)}" data-pick="${esc(p.id)}" transform="translate(${x},${y})" tabindex="0" role="button" aria-label="${esc(p.title)}">
        <rect x="-92" y="-28" width="184" height="56" rx="12"/>
        <text text-anchor="middle" y="${wrapWords(p.title, 24).length > 1 ? -3 : 5}" class="wi-tpt">${tspans(wrapWords(p.title, 24), 0, 15)}</text></g>`);
    }
    // ideas
    ideas.forEach((id, i) => {
      const [x, y] = at[id];
      const c = byId.get(id);
      const lines = wrapWords(c.label, 17);
      const below = i % 2 === 0;
      parts.push(`<g class="wi-idea" data-tp="${esc(belongs((p) => p.ideas.includes(id)))}" data-id="${esc(id)}" transform="translate(${x},${y})"
        data-tip="${esc(`<span class="tip-k">${esc(kindLabel(id))} · ${esc(id)}</span><b>${esc(c.label)}</b>${c.definition ? `<span class="tip-s">${esc(c.definition.text.slice(0, 160))}${c.definition.text.length > 160 ? "…" : ""}</span>` : ""}<span class="tip-s">Click to open it on the knowledge map.</span>`)}">
        <circle r="9" style="fill:${colour(id)}"/>
        <text text-anchor="middle" y="${below ? -16 - (lines.length - 1) * 13 : 24}" class="wi-il">${tspans(lines, 0, 13)}</text></g>`);
    });
    // provisions, with what rests on each today, and the legal test written for it
    for (const ref of provs) {
      const [x, y] = at[ref];
      const r = w.rests_on_provision[ref];
      const test = [...tests.values()].find((t) => t.provision === ref && w.touchpoints.some((p) => p.tests.includes(t.id)));
      parts.push(`<g class="wi-prov law act" data-tp="${esc(belongs((p) => p.provisions.includes(ref)))}" data-ref="${esc(ref)}" transform="translate(${x},${y})"
        data-tip="${esc(`<span class="tip-k">Trade Marks Act 1995 · law</span><b>${esc(refLabel(ref))}</b><span class="tip-s">${r ? `${fmt(r.direct)} records name it; ${fmt(r.via_manual)} more rest on the ${fmt(r.passages)} Manual passages citing it` : "No record in the ontology names it or rests on a passage citing it: no recorded dependency, which is not the same as no impact"}. Click to read it.</span>`)}">
        ${srcShape("act", 12)}
        <text y="31" text-anchor="middle" class="wi-pl">${esc(refLabel(ref))}</text>
        <text y="47" text-anchor="middle" class="wi-pc${r ? "" : " none"}">${r ? `${fmt(r.direct + r.via_manual)} rest on it` : "no recorded dependency"}</text>
        ${test ? `<text y="64" text-anchor="middle" class="wi-pt">legal test ${esc(test.id)}</text>` : ""}</g>`);
    }
    parts.push(`</svg>`);
    return parts.join("");
  }

  const ideaChip = (id) => { const c = byId.get(id); return c ? `<a class="chip wi-ic" href="#/map/ideas/${esc(id)}" style="--c:${colour(id)}"><i class="dot"></i>${esc(c.label)}</a>` : ""; };

  function detail(p) {
    const stepNames = p.steps.map((s) => { const step = processes.get(s.process)?.steps.find((x) => x.id === s.step); return step ? `<a class="chip" href="${structureHref(s.process)}">${esc(step.label)} <span class="tiny">${esc(s.process)}</span></a>` : ""; });
    return `
      <div class="wi-detail-head"><span class="eyebrow">Touch point ${points.indexOf(p) + 1} of ${points.length}</span><h2>${esc(p.title)}</h2></div>
      <div class="wi-cols">
        <section class="wi-today">
          <h3>${icon("book")} What practice says today</h3>
          <p class="tiny">The Manual's own words, quoted verbatim from the snapshot. The Manual states practice; it is not the law.</p>
          ${p.today.map((q) => `${quoteBlock(q.ref, q.quote)}<p class="wi-from">${refChip(q.ref)}</p>`).join("")}
        </section>
        <section class="wi-if">
          <h3>${icon("question")} What if <span class="trust machine" title="Written by a machine; no expert has reviewed it">Machine · unreviewed</span></h3>
          <p>${esc(p.what_if)}</p>
          <h4>Questions the new practice would need to answer</h4>
          <ol class="wi-qs">${p.questions.map((q) => `<li>${esc(q)}</li>`).join("")}</ol>
          <p class="tiny">Questions, not answers: the ontology shows where each would land; it does not say how any would be settled.</p>
        </section>
      </div>
      <div class="wi-lands">
        <div class="wi-land-k"><h3>${icon("connect")} Where it lands in the ontology</h3><p class="tiny">Every record here already exists, unchanged.</p></div>
        <div class="wi-land-list">
          <p><span class="wi-lk">Ideas</span>${p.ideas.map(ideaChip).join("")}</p>
          ${p.tests.length ? `<p><span class="wi-lk">Legal tests</span>${p.tests.map((id) => `<a class="chip" href="${structureHref(id)}">${esc(tests.get(id)?.title || id)}</a>`).join("")}</p>` : ""}
          ${stepNames.length ? `<p><span class="wi-lk">Process steps</span>${stepNames.join("")}</p>` : ""}
          <p><span class="wi-lk">Provisions</span>${p.provisions.map((ref) => `${refChip(ref)}<a class="wi-trace" href="#/change/${esc(ref)}">trace ${icon("arrow")}</a>`).join("")}</p>
        </div>
      </div>
      <div class="wi-stats">
        <div class="stat"><b>${fmt(p.recheck.length)}</b><span>records name these provisions or quote these pages, and would go back to be re-read first</span></div>
        <div class="stat"><b>${fmt(p.recheck_via.length)}</b><span>more rest on Manual passages citing the provisions, and would follow</span></div>
        <div class="stat"><b>${fmt(p.connections.length)}</b><span>connections in the ontology touch these ideas</span></div>
        <div class="stat"><b>${fmt(p.pages.length)}</b><span>Manual page${p.pages.length === 1 ? "" : "s"} quoted above</span></div>
      </div>
      ${p.no_recorded_dependency.length ? `<p class="wi-gap">${icon("info")}<span><b>${p.no_recorded_dependency.map((r) => esc(refLabel(r))).join(", ")}: no recorded dependency.</b>
        No record in the ontology names ${p.no_recorded_dependency.length === 1 ? "it" : "them"} yet, so the count above cannot see what rests on ${p.no_recorded_dependency.length === 1 ? "it" : "them"}.
        That is a gap in the ontology the what-if exposes, never a sign of no impact.</span></p>` : ""}`;
  }

  const textEquivalent = () => [
    `${w.title} (${w.id}). Invented; a machine's premise and questions; not reviewed.`,
    `Premise: ${w.premise}`,
    ...points.map((p, i) => [
      `${i + 1}. ${p.title}`,
      ...p.today.map((q) => `   Today (${refLabel(q.ref)}): “${q.quote}”`),
      `   What if: ${p.what_if}`,
      ...p.questions.map((q) => `   Question: ${q}`),
      `   Lands on ideas: ${p.ideas.map((id) => byId.get(id)?.label || id).join("; ")}.`,
      p.tests.length ? `   Legal tests: ${p.tests.map((id) => tests.get(id)?.title || id).join("; ")}.` : "",
      `   Provisions: ${p.provisions.map(refLabel).join(", ")}${p.no_recorded_dependency.length ? ` (no recorded dependency: ${p.no_recorded_dependency.map(refLabel).join(", ")})` : ""}.`,
      `   Would go back to be re-read: ${p.recheck.length} records first, ${p.recheck_via.length} more through the Manual.`,
    ].filter(Boolean).join("\n")),
    `Connections already in the ontology among these ideas: ${[...new Map(w.links.map((r) => [`${r.s}|${r.p}|${r.o}`, r])).values()].map((r) => `${byId.get(r.s)?.label} ${ontology.predicates[r.p]?.label || r.p} ${byId.get(r.o)?.label}`).join("; ")}.`,
    `How applicants or examiners would behave: ${w.behavioural}`,
  ].join("\n\n");

  const t = w.totals;
  root.innerHTML = `
  <div class="wi">
    <header class="wrap page-head">
      <div>
        <span class="eyebrow">For policy · a what-if</span>
        <h1>What if geographical indications became their own right?</h1>
        <p class="lede">A small demonstration of the ontology as a policy aid. Take a right that does not exist, lay it over the ontology without changing it, and see
        where examination practice would need to be read again: which ideas, tests and passages it lands on, and how much guidance rests on them.</p>
      </div>
      <div class="page-head-side">${statePill("prototype", "Demonstration")}<span class="trust machine" title="Written by a machine; no expert has reviewed it">Machine · unreviewed</span></div>
    </header>
    <div class="wrap">
      <div class="wi-banner" role="note">
        <div class="wi-banner-head">${icon("flag")}<p><b>An invented premise. The ontology is not changed. Nothing here is decided.</b></p></div>
        <ul>
          <li>No register of geographical indications for all goods exists in Australia, and no draft law is assumed. The premise and every question are a machine's.</li>
          <li>Every idea, connection, legal test and passage shown is already in the ontology, drawn as every other page draws it. Nothing was added to make this page.</li>
          <li>It shows where practice would need to be read again. It never says what the new practice should be, or how an application would be decided.</li>
          <li>How applicants or examiners would respond is unknown: that needs data nobody here holds.</li>
        </ul>
      </div>
      <p class="wi-premise-text"><span class="eyebrow plain">The premise</span>${esc(w.premise)}</p>

      <div class="card wi-stage">
        <div class="wi-pick" role="group" aria-label="Touch points">${points.map((p, i) => `<button type="button" class="wi-pick-b" data-pick="${esc(p.id)}" aria-pressed="${p.id === current}"><span class="wi-n">${i + 1}</span>${esc(p.title)}</button>`).join("")}</div>
        <div class="wi-pic">${picture()}</div>
        <div class="wi-key">
          <span><i class="k invented"></i>invented: the premise and where it lands</span>
          <span><i class="k recorded"></i>a connection already in the ontology</span>
          <span><i class="k basis"></i>an idea's recorded basis in the Act</span>
          <span class="law act"><i class="mark" aria-hidden="true"></i>a provision of the Act, with what rests on it today</span>
          <span class="tiny wi-fam">Ideas take their family's colour: <b style="color:var(--f-reasoning-ink)">the law's questions</b>, <b style="color:var(--f-examined-ink)">what they are asked about</b>, <b style="color:var(--f-process-ink)">the process around them</b>.</span>
        </div>
        <details class="text-eq"><summary>Text equivalent of the picture</summary><pre>${esc(textEquivalent())}</pre></details>
      </div>

      <div class="card card-pad wi-detail" aria-live="polite"></div>

      <section class="wi-sum">
        <div class="sec-head"><div><span class="eyebrow">What this shows</span><h2>The scope of a new right, before anyone drafts it.</h2></div>
          <p>Because every idea quotes its passage and every connection names its source, an invented right can be traced to the guidance it would touch in one step, and the gaps show up as gaps.</p></div>
        <div class="wi-tiles">
          <div class="stat"><b>${fmt(t.ideas)}</b><span>ideas of ${fmt(ontology.concepts.length)} it lands on</span></div>
          <div class="stat"><b>${fmt(t.tests)}</b><span>legal tests of ${fmt(tests.size)} written as structured data</span></div>
          <div class="stat"><b>${fmt(t.provisions)}</b><span>provisions of the Act</span></div>
          <div class="stat"><b>${fmt(t.recheck)}</b><span>records to re-read first, and ${fmt(t.recheck_via)} after them</span></div>
        </div>
        <div class="wi-three">
          <div><h3>Which guidance would need re-reading?</h3>${statePill("working", "Answered")}<p class="small">Counted from the dependency index, the same one <a href="#/change">Trace a change</a> reads.</p></div>
          <div><h3>What should the new practice say?</h3>${statePill("planned", "Not answered")}<p class="small">The page asks the questions. Answering them is policy work for people, against the law that would create the right.</p></div>
          <div><h3>How would people respond?</h3>${statePill("planned", "Unknown")}<p class="small">${esc(w.behavioural)}</p></div>
        </div>
        <p class="stamp">${stampIcon}<span><b>Written by ${esc(w.written_by)} on ${esc(w.written_date)}, never reviewed.</b> ${esc(w.stamp)}</span></p>
      </section>
    </div>
  </div>`;

  const svg = root.querySelector(".wi-svg");
  const panel = root.querySelector(".wi-detail");
  function select(id) {
    current = id;
    history.replaceState(null, "", `#/whatif/${encodeURIComponent(w.id)}/${encodeURIComponent(id)}`);
    root.querySelectorAll(".wi-pick-b").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.pick === id)));
    svg.querySelectorAll("[data-tp]").forEach((el) => {
      const on = el.dataset.tp.split(" ").includes(id);
      el.classList.toggle("on", on);
      el.classList.toggle("dim", !on);
    });
    panel.innerHTML = detail(points.find((p) => p.id === id));
  }
  root.querySelector(".wi-pick").addEventListener("click", (e) => { const b = e.target.closest("[data-pick]"); if (b) select(b.dataset.pick); });
  svg.addEventListener("click", (e) => {
    const tp = e.target.closest(".wi-tp");
    if (tp) { select(tp.dataset.pick); return; }
    const idea = e.target.closest(".wi-idea");
    if (idea) location.hash = `#/map/ideas/${idea.dataset.id}`;
  });
  svg.addEventListener("keydown", (e) => { const tp = e.target.closest(".wi-tp"); if (tp && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); select(tp.dataset.pick); } });
  svg.addEventListener("mousemove", (e) => { const el = e.target.closest("[data-tip]"); tip(el ? el.dataset.tip : null, e); });
  svg.addEventListener("mouseleave", () => tip(null));
  select(current);
  return () => tip(null);
}
