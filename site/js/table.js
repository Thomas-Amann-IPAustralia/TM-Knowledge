/* As a table — the ontology without the picture. The map's "Ideas and
   connections" level draws every idea and hundreds of lines at once; this view
   lists the same records in three plain tables, one per level:

   1. Kinds        — the kinds in their families, then how the kinds connect
                     (`kind_links`, counted by tmk-explorer).
   2. Ideas        — one row per idea, grouped by kind. Open a row to read its
                     connections as sentences, each with the passage it rests on.
   3. Connections  — one row per connection: from, what it says, to, the passage.

   Every row is a record, or a count of records, that the map already shows;
   nothing is arranged here. Who wrote each record is in its row: "Machine ·
   unreviewed" on every machine-written one (rule 8), a quiet "Reviewed" on the
   rest (ADR-0130). Each table downloads as a CSV with the same columns, who
   wrote each record, and which text each quote is from (rules 5, 8). */

import { esc, fmt, el, kindColour, kindCount, refChip, refLabel, trustBadge, quoteBlock, sourceOf, SOURCES, legend } from "./app.js";
import { LOOSE, specificCount } from "./kinds.js";

const TABS = [["kinds", "Kinds"], ["ideas", "Ideas"], ["connections", "Connections"]];
const FAMILIES = ["reasoning", "examined", "process", "other"];

export async function render(root, { ontology, params }) {
  const tab = TABS.some(([id]) => id === params[0]) ? params[0] : "kinds";
  const byId = new Map(ontology.concepts.map((x) => [x.id, x]));
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  const relOf = new Map();
  for (const r of ontology.relations) {
    for (const end of new Set([r.s, r.o])) { if (!relOf.has(end)) relOf.set(end, []); relOf.get(end).push(r); }
  }
  const ctx = { ontology, byId, kinds, relOf };
  const counts = { kinds: kindCount(ontology), ideas: ontology.concepts.length, connections: ontology.relations.length };

  root.innerHTML = `
  <div class="wrap wide table-page">
    <h1>The ontology, as tables</h1>
    <p class="lede">The same ideas and connections as the map, listed instead of drawn. Kinds sort the ideas by what they are;
    connections say how one idea bears on another, each resting on a quoted sentence. Click any passage to read it.</p>
    <nav class="tabs" aria-label="Which table">${TABS.map(([id, label]) => `<a href="#/table/${id}"${id === tab ? ` class="on" aria-current="page"` : ""}>${label} <span class="num">${fmt(counts[id])}</span></a>`).join("")}</nav>
    <div class="table-body"></div>
  </div>`;
  const body = root.querySelector(".table-body");
  if (!byId.has(params[1])) window.scrollTo(0, 0);
  if (tab === "kinds") kindsTab(body, ctx);
  else if (tab === "ideas") ideasTab(body, ctx, params[1]);
  else connectionsTab(body, ctx, params[1], params[2]);
}

// ------------------------------------------------------------------ shared

const predLabel = (ontology, p) => ontology.predicates[p]?.label || p;

/** The links the map hides by default (`LOOSE`: hierarchy, since "is related to" was
    retired, ADR-0131), named from the predicate list rather than written here. */
const looseNames = (ontology) => [...LOOSE].map((p) => `"${predLabel(ontology, p)}" links`).join(" and ");

/** One end of a connection: an idea, a passage or provision, or a case. A case is
    neither the Manual nor legislation, so it is never given their marks. */
function endHtml(ctx, id, { link = true } = {}) {
  const x = ctx.byId.get(id);
  if (x) {
    const dot = `<span class="dot" style="--c:${kindColour(x.kind)}"></span>`;
    return link ? `${dot}<a class="idea-link" href="#/table/ideas/${esc(id)}" data-goto="${esc(id)}">${esc(x.label)}</a>` : `${dot}<b>${esc(x.label)}</b>`;
  }
  if (/^TM[MAR]/.test(id)) return refChip(id);
  return `<span class="chip" title="${esc(id)}">case ${esc(ctx.ontology.provisions[id]?.label || id)}</span>`;
}

const endName = (ctx, id) => ctx.byId.get(id)?.label || (/^TM[MAR]/.test(id) ? refLabel(id) : `case ${ctx.ontology.provisions[id]?.label || id}`);

const sourceText = (ref) => { const s = SOURCES[sourceOf(ref)]; return `${s.short} · ${s.role}`; };

/** Who wrote a record, in words — the same facts as the map's "Who wrote this record". */
function provenance(x) {
  const rows = [];
  if (x.signed) rows.push(`Reviewed by a trade marks expert on ${esc(x.signed.date)}.`);
  if (x.corrected) rows.push(`Corrected since it was reviewed (${x.corrected.map(esc).join(", ")}) — a machine-written, unreviewed change; the reviewed record itself is kept unchanged.`);
  if (x.machine) rows.push(`Written by <code>${esc(x.machine.by)}</code> on ${esc(x.machine.date)} · <b>${esc(x.machine.review_status)}</b>.`);
  if (x.typed) rows.push(`Its kind was judged by <code>${esc(x.typed.by)}</code> on ${esc(x.typed.date)} · <b>${esc(x.typed.review_status)}</b>.`);
  return rows.map((r) => `<p class="tiny">${r}</p>`).join("");
}

/** The sentence a connection rests on, with who wrote it — shown when a row is opened. */
function relationDetail(ctx, r) {
  return `
    ${quoteBlock(r.ref, r.quote)}
    <div class="meta">${refChip(r.ref)}${r.modality ? `<span class="chip">${esc(r.modality)}</span>` : ""}<span class="tiny">${esc(r.id)}</span></div>
    ${r.replaces ? `<p class="tiny">A corrected reading of ${esc(r.replaces)}, which is kept unchanged.</p>` : ""}
    ${r.signed ? `<p class="tiny">Reviewed by a trade marks expert on ${esc(r.signed.date)}.</p>` : ""}
    ${r.machine ? `<p class="tiny">Written by <code>${esc(r.machine.by)}</code> on ${esc(r.machine.date)} · <b>${esc(r.machine.review_status)}</b>.</p>` : ""}
    ${r.machine?.reasoning ? `<details><summary>Why the machine wrote this</summary><p class="small muted">${esc(r.machine.reasoning)}</p></details>` : ""}`;
}

function controls(html) {
  return `<div class="tbl-controls">${html}</div>`;
}

// CSV, for opening the table in a spreadsheet. A cell that a spreadsheet would
// run as a formula is prefixed with an apostrophe, which the spreadsheet hides.
const cell = (value) => {
  let s = String(value ?? "");
  if (/^[=+\-@\t\r]/.test(s)) s = `'${s}`;
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

function download(name, rows) {
  const text = "﻿" + rows.map((row) => row.map(cell).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Who wrote a record, as CSV columns. The reviewer's name is not given (ADR-0130). */
function whoColumns(x) {
  if (x.origin === "signed") return ["reviewed", "reviewed by a trade marks expert", "", x.signed?.date || ""];
  return ["machine-written", x.machine?.review_status || "unreviewed", x.machine?.by || "", x.machine?.date || ""];
}

// ------------------------------------------------------------------ 1. kinds

function kindsTab(body, ctx) {
  const { ontology, kinds } = ctx;
  const touching = new Map();
  for (const r of ontology.relations) {
    for (const k of new Set([ctx.byId.get(r.s)?.kind, ctx.byId.get(r.o)?.kind])) if (k) touching.set(k, (touching.get(k) || 0) + 1);
  }
  const ideasOf = (k) => ontology.concepts.filter((x) => x.kind === k).length;
  const pairs = [...ontology.kind_links].sort((a, b) => specificCount(b) - specificCount(a) || b.total - a.total);

  body.innerHTML = `
    <section class="tbl-section">
      <h2>The kinds of idea</h2>
      <p class="muted small">Every idea is sorted by <b>what it is</b> into one of ${kindCount(ontology)} kinds, in three families. What an idea <b>does</b> —
      a factor, an exception, a remedy — is a connection, not a kind. Click a kind to list its ideas.</p>
      <table class="tbl kinds-tbl">
        <thead><tr><th>Kind</th><th>What it is</th><th class="num">Ideas</th><th class="num opt">Connections</th></tr></thead>
        <tbody>${FAMILIES.map((family) => {
          const members = ontology.kinds.filter((k) => k.family === family && ideasOf(k.id));
          if (!members.length) return "";
          return `<tr class="group"><th colspan="4">${esc(ontology.families[family] || family)}</th></tr>` + members.map((k) => `
            <tr class="row">
              <td><span class="dot" style="--c:${kindColour(k.id)}"></span><a class="idea-link" href="#/table/ideas/${esc(k.id)}">${esc(k.label)}</a></td>
              <td class="muted">${esc(k.plain)}</td>
              <td class="num">${fmt(ideasOf(k.id))}</td>
              <td class="num opt">${fmt(touching.get(k.id) || 0)}</td>
            </tr>`).join("");
        }).join("")}</tbody>
      </table>
      <p class="tiny">"Connections" counts every connection with at least one end among the kind's ideas.</p>
    </section>

    <section class="tbl-section">
      <h2>How the kinds connect</h2>
      <p class="muted small">Each row counts the connections from ideas of one kind to ideas of another — the patterns the map draws as arrows
      between closed kinds. Click a count to list those connections one by one.</p>
      ${controls(`<label class="check"><input type="checkbox" data-loose> Include pairs joined only by ${looseNames(ontology)}</label>`)}
      <table class="tbl">
        <thead><tr><th>From ideas of this kind</th><th>to ideas of this kind</th><th class="num">Connections</th><th class="opt">What they say</th></tr></thead>
        <tbody>${pairs.map((row) => `
          <tr class="row${specificCount(row) ? "" : " loose-only"}"${specificCount(row) ? "" : " hidden"}>
            <td><span class="dot" style="--c:${kindColour(row.s)}"></span>${esc(kinds.get(row.s)?.label || row.s)}</td>
            <td><span class="dot" style="--c:${kindColour(row.o)}"></span>${row.o === row.s ? `<span class="muted">the same kind</span>` : esc(kinds.get(row.o)?.label || row.o)}</td>
            <td class="num"><a href="#/table/connections/${esc(row.s)}/${esc(row.o)}" title="List these connections">${fmt(row.total)}</a></td>
            <td class="opt small">${Object.entries(row.predicates).sort((a, b) => b[1] - a[1])
              .map(([p, n]) => `<span class="${LOOSE.has(p) ? "muted" : ""}">${esc(predLabel(ontology, p))} <span class="num">${n}</span></span>`).join(" · ")}</td>
          </tr>`).join("")}</tbody>
      </table>
    </section>`;
  body.querySelector("[data-loose]").addEventListener("change", (e) => {
    body.querySelectorAll("tr.loose-only").forEach((tr) => { tr.hidden = !e.target.checked; });
  });
}

// ------------------------------------------------------------------ 2. ideas

function ideasTab(body, ctx, param) {
  const { ontology, byId, relOf } = ctx;
  const startKind = ctx.kinds.has(param) ? param : "";
  const startIdea = byId.has(param) ? param : null;
  const order = FAMILIES.flatMap((f) => ontology.kinds.filter((k) => k.family === f));
  const COLS = 6;

  body.innerHTML = `
    ${controls(`
      <input class="find" type="search" placeholder="Filter by name, e.g. consent" aria-label="Filter ideas" autocomplete="off">
      <select class="pick" aria-label="Kind"><option value="">Every kind</option>${order.map((k) => `<option value="${esc(k.id)}"${k.id === startKind ? " selected" : ""}>${esc(k.label)}</option>`).join("")}</select>
      <span class="tiny shown" aria-live="polite"></span>
      <button class="btn small push" type="button" data-csv>Download all ${fmt(ontology.concepts.length)} ideas (CSV)</button>`)}
    <table class="tbl ideas">
      <thead><tr><th>Idea</th><th class="opt">Also called</th><th class="num">Connections</th><th class="num opt">Passages</th><th class="opt">In the law</th><th>Written by</th></tr></thead>
      <tbody>${order.map((k) => {
        const members = ontology.concepts.filter((x) => x.kind === k.id).sort((a, b) => a.label.localeCompare(b.label));
        if (!members.length) return "";
        return `<tr class="group" data-kind="${esc(k.id)}"><th colspan="${COLS}"><span class="dot" style="--c:${kindColour(k.id)}"></span>${esc(k.label)}
          <span class="tiny">— ${esc(k.plain)} · ${members.length} ideas</span></th></tr>` + members.map((x) => `
          <tr class="row" data-id="${esc(x.id)}" data-kind="${esc(x.kind)}" data-text="${esc([x.label, ...x.alt, x.id].join(" ").toLowerCase())}">
            <td><button type="button" class="disc" aria-expanded="false">${esc(x.label)}</button></td>
            <td class="opt small muted">${x.alt.slice(0, 3).map(esc).join(" · ")}${x.alt.length > 3 ? ` <span class="tiny">+${x.alt.length - 3}</span>` : ""}</td>
            <td class="num">${fmt((relOf.get(x.id) || []).length)}</td>
            <td class="num opt">${fmt(x.mentions)}</td>
            <td class="opt">${x.basis.slice(0, 3).map((r) => refChip(r)).join(" ")}${x.basis.length > 3 ? ` <span class="tiny">+${x.basis.length - 3}</span>` : ""}</td>
            <td>${trustBadge(x.origin)}</td>
          </tr>`).join("");
      }).join("")}</tbody>
    </table>
    <p class="tiny">"Passages" counts the passages of the Manual that name the idea. "In the law" lists the provisions the record rests on.</p>`;

  const find = body.querySelector(".find");
  const pick = body.querySelector(".pick");
  const shown = body.querySelector(".shown");
  const rows = [...body.querySelectorAll("tr.row")];

  function filter() {
    const q = find.value.trim().toLowerCase();
    let n = 0;
    for (const tr of rows) {
      const show = (!pick.value || tr.dataset.kind === pick.value) && (!q || tr.dataset.text.includes(q));
      tr.hidden = !show;
      if (tr.nextElementSibling?.classList.contains("detail")) tr.nextElementSibling.hidden = !show;
      if (show) n++;
    }
    body.querySelectorAll("tr.group").forEach((g) => { g.hidden = !rows.some((tr) => !tr.hidden && tr.dataset.kind === g.dataset.kind); });
    shown.textContent = n === rows.length ? "" : `${fmt(n)} of ${fmt(rows.length)} shown`;
  }

  function toggle(tr, open = tr.querySelector(".disc").getAttribute("aria-expanded") !== "true") {
    const next = tr.nextElementSibling;
    if (next?.classList.contains("detail")) next.remove();
    tr.classList.toggle("open", open);
    tr.querySelector(".disc").setAttribute("aria-expanded", String(open));
    if (open) tr.after(el(`<tr class="detail"><td colspan="${COLS}">${ideaDetail(ctx, byId.get(tr.dataset.id))}</td></tr>`));
  }

  function openIdea(id) {
    const tr = body.querySelector(`tr.row[data-id="${CSS.escape(id)}"]`);
    if (!tr) return;
    if (tr.hidden) { find.value = ""; pick.value = ""; filter(); }
    toggle(tr, true);
    tr.scrollIntoView({ block: "center", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    tr.classList.add("flash");
    setTimeout(() => tr.classList.remove("flash"), 1400);
  }

  find.addEventListener("input", filter);
  pick.addEventListener("change", filter);
  body.addEventListener("click", (e) => {
    const go = e.target.closest("[data-goto]");
    if (go) { e.preventDefault(); openIdea(go.dataset.goto); return; }
    const why = e.target.closest("[data-why]");
    if (why) { e.preventDefault(); toggleWhy(ctx, why); return; }
    const disc = e.target.closest(".disc");
    if (disc) toggle(disc.closest("tr"));
  });
  body.querySelector("[data-csv]").addEventListener("click", () => download("trade-marks-manual-ideas.csv", ideasCsv(ctx)));
  filter();
  if (startIdea) requestAnimationFrame(() => openIdea(startIdea));
}

function ideaDetail(ctx, x) {
  const { ontology } = ctx;
  const rels = ctx.relOf.get(x.id) || [];
  const strong = rels.filter((r) => !LOOSE.has(r.p));
  const loose = rels.filter((r) => LOOSE.has(r.p));
  const sortRels = (list) => list.sort((a, b) => (b.s === x.id) - (a.s === x.id) || predLabel(ontology, a.p).localeCompare(predLabel(ontology, b.p)));
  const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
  const sentence = (r) => `<li>
      <span class="sent">${endHtml(ctx, r.s, { link: r.s !== x.id })} <span class="pred">${esc(predLabel(ontology, r.p))}</span> ${endHtml(ctx, r.o, { link: r.o !== x.id })}</span>
      <span class="sent-meta">${trustBadge(r.origin)}<button type="button" class="link tiny" data-why="${esc(r.id)}" aria-expanded="false">the sentence it rests on</button></span>
    </li>`;
  return `<div class="idea-detail">
    <div class="idea-facts">
      ${x.alt.length ? `<p class="small"><span class="muted">Also called</span> ${x.alt.map(esc).join(" · ")}</p>` : ""}
      ${x.not.length ? `<p class="small"><span class="muted">Not the same as</span> ${x.not.map(esc).join(" · ")}</p>` : ""}
      ${first ? `<h4>What it rests on</h4>${quoteBlock(first.ref, first.quote)}${refChip(first.ref)}
        <span class="tiny">${first.for === "kind" ? "quoted when the machine sorted it into its kind" : "quoted by the record itself"}</span>` : ""}
      ${["act", "regs"].map((src) => {
        const list = x.basis.filter((r) => sourceOf(r) === src);
        return list.length ? `<h4>In the ${src === "act" ? "Act" : "Regulations"}</h4><div class="meta">${list.map((r) => refChip(r)).join("")}</div>` : "";
      }).join("")}
      ${x.notes ? `<h4>Note on the record</h4><p class="small">${esc(x.notes)}</p>` : ""}
      <h4>Who wrote this record</h4>${provenance(x)}
      <p class="actions-row"><a class="btn small" href="#/map/ideas/${esc(x.id)}">Show on the map</a><a class="btn small" href="#/map/text/${esc(x.id)}">Open into its passages</a></p>
    </div>
    <div class="idea-conns">
      <h4>Connections · ${rels.length}</h4>
      ${strong.length ? `<ul class="sent-list">${sortRels(strong).map(sentence).join("")}</ul>` : `<p class="empty small">None beyond hierarchy.</p>`}
      ${loose.length ? `<h4>Hierarchy · ${loose.length}</h4>
        <ul class="sent-list">${sortRels(loose).map(sentence).join("")}</ul>` : ""}
    </div>
  </div>`;
}

function toggleWhy(ctx, button) {
  const li = button.closest("li, tr");
  const open = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!open));
  if (li.tagName === "TR") {
    li.classList.toggle("open", !open);
    if (open) { if (li.nextElementSibling?.classList.contains("detail")) li.nextElementSibling.remove(); return; }
    const r = ctx.ontology.relations.find((x) => x.id === button.dataset.why);
    li.after(el(`<tr class="detail"><td colspan="${li.children.length}">${relationDetail(ctx, r)}</td></tr>`));
    return;
  }
  const existing = li.querySelector(".why");
  if (existing) { existing.remove(); return; }
  const r = ctx.ontology.relations.find((x) => x.id === button.dataset.why);
  li.appendChild(el(`<div class="why">${relationDetail(ctx, r)}</div>`));
}

function ideasCsv(ctx) {
  const { ontology, kinds, relOf } = ctx;
  const head = ["id", "idea", "also_called", "not_the_same_as", "kind", "family", "connections", "passages_naming_it",
    "act_provisions", "regulations_provisions", "rests_on", "rests_on_text", "quote",
    "record", "review_status", "machine_author", "date", "kind_judged_by", "kind_review_status", "corrected_by"];
  return [head, ...ontology.concepts.map((x) => {
    const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
    return [x.id, x.label, x.alt.join("; "), x.not.join("; "), kinds.get(x.kind)?.label || x.kind,
      ontology.families[kinds.get(x.kind)?.family] || "", (relOf.get(x.id) || []).length, x.mentions,
      x.basis.filter((r) => sourceOf(r) === "act").map(refLabel).join("; "),
      x.basis.filter((r) => sourceOf(r) === "regs").map(refLabel).join("; "),
      first?.ref || "", first ? sourceText(first.ref) : "", first?.quote || "",
      ...whoColumns(x), x.typed?.by || "", x.typed?.review_status || "", (x.corrected || []).join("; ")];
  })];
}

// ------------------------------------------------------------------ 3. connections

function connectionsTab(body, ctx, fromKind, toKind) {
  const { ontology, byId, kinds } = ctx;
  if (!kinds.has(fromKind) || !kinds.has(toKind)) fromKind = toKind = null;
  const preds = Object.entries(ontology.relations.reduce((m, r) => ({ ...m, [r.p]: (m[r.p] || 0) + 1 }), {})).sort((a, b) => b[1] - a[1]);
  const list = [...ontology.relations].sort((a, b) => endName(ctx, a.s).localeCompare(endName(ctx, b.s))
    || predLabel(ontology, a.p).localeCompare(predLabel(ontology, b.p)) || endName(ctx, a.o).localeCompare(endName(ctx, b.o)));
  const kindOf = (id) => byId.get(id)?.kind;
  const pairLabel = fromKind ? `${kinds.get(fromKind).label} → ${fromKind === toKind ? "the same kind" : kinds.get(toKind).label}` : "";

  body.innerHTML = `
    ${controls(`
      <input class="find" type="search" placeholder="Filter, e.g. consent or qualifies" aria-label="Filter connections" autocomplete="off">
      <select class="pick" aria-label="What the connection says"><option value="">Every kind of connection</option>${preds.map(([p, n]) => `<option value="${esc(p)}">${esc(predLabel(ontology, p))} · ${n}</option>`).join("")}</select>
      <label class="check"><input type="checkbox" data-loose${fromKind ? " checked" : ""}> Include ${looseNames(ontology)}</label>
      ${fromKind ? `<span class="chip on-filter">${esc(pairLabel)} <a href="#/table/connections" aria-label="Clear this filter">×</a></span>` : ""}
      <span class="tiny shown" aria-live="polite"></span>
      <button class="btn small push" type="button" data-csv>Download all ${fmt(ontology.relations.length)} connections (CSV)</button>`)}
    <p class="tiny">The ${looseNames(ontology)} (${fmt(ontology.relations.filter((r) => LOOSE.has(r.p)).length)} of ${fmt(ontology.relations.length)}) say how ideas nest, not how one acts on another;
    hidden unless you include them or pick one above, as on the map. Open a row to read the sentence it rests on.</p>
    <table class="tbl conns">
      <thead><tr><th>From</th><th>Says</th><th>To</th><th class="opt">Rests on</th><th>Written by</th></tr></thead>
      <tbody>${list.map((r) => `
        <tr class="row" data-p="${esc(r.p)}" data-sk="${esc(kindOf(r.s))}" data-ok="${esc(kindOf(r.o))}" data-text="${esc([endName(ctx, r.s), predLabel(ontology, r.p), endName(ctx, r.o), r.id].join(" ").toLowerCase())}">
          <td>${endHtml(ctx, r.s)}</td>
          <td><button type="button" class="disc pred" data-why="${esc(r.id)}" aria-expanded="false">${esc(predLabel(ontology, r.p))}</button></td>
          <td>${endHtml(ctx, r.o)}</td>
          <td class="opt">${refChip(r.ref)}</td>
          <td>${trustBadge(r.origin)}</td>
        </tr>`).join("")}</tbody>
    </table>
    <div class="legend-row">${legend()}</div>`;

  const find = body.querySelector(".find");
  const pick = body.querySelector(".pick");
  const loose = body.querySelector("[data-loose]");
  const shown = body.querySelector(".shown");
  const rows = [...body.querySelectorAll("tr.row")];

  function filter() {
    const q = find.value.trim().toLowerCase();
    let n = 0;
    for (const tr of rows) {
      const show = (pick.value ? tr.dataset.p === pick.value : loose.checked || !LOOSE.has(tr.dataset.p))
        && (!fromKind || (tr.dataset.sk === fromKind && tr.dataset.ok === toKind))
        && (!q || tr.dataset.text.includes(q));
      tr.hidden = !show;
      if (tr.nextElementSibling?.classList.contains("detail")) tr.nextElementSibling.hidden = !show;
      if (show) n++;
    }
    shown.textContent = `${fmt(n)} of ${fmt(rows.length)} shown`;
  }
  find.addEventListener("input", filter);
  pick.addEventListener("change", filter);
  loose.addEventListener("change", filter);
  body.addEventListener("click", (e) => {
    const why = e.target.closest("[data-why]");
    if (why) { e.preventDefault(); toggleWhy(ctx, why); }
  });
  body.querySelector("[data-csv]").addEventListener("click", () => download("trade-marks-manual-connections.csv", connectionsCsv(ctx)));
  filter();
}

function connectionsCsv(ctx) {
  const { ontology } = ctx;
  const head = ["id", "from_id", "from", "says", "to_id", "to", "modality", "rests_on", "rests_on_text", "quote",
    "record", "review_status", "machine_author", "date", "replaces"];
  return [head, ...ontology.relations.map((r) => [r.id, r.s, endName(ctx, r.s), predLabel(ontology, r.p), r.o, endName(ctx, r.o),
    r.modality || "", r.ref, sourceText(r.ref), r.quote, ...whoColumns(r), r.replaces || ""])];
}
