/* The map — the ontology at three levels of detail, drawn with Cytoscape.js.

   1. Kinds  — the kinds of idea as nodes inside their three families. Each
               kind is closed: its ideas are inside it, and every connection
               they make is rolled up into one weighted arrow per pair of kinds.
   2. Ideas  — open a kind (or all of them) and it becomes a box holding its
               ideas; their own connections appear. Open some kinds and not
               others to see a part of the map in detail and the rest in outline.
   3. Text   — open one idea into the Parts of the Manual that name it, a Part
               into its passages, beside the provisions it rests on.

   Nothing here decides which concepts or connections exist; every node and edge
   is a record. The roll-ups count records and say so. Every idea and connection
   is drawn the same way whoever wrote it; who wrote a record is on its card
   (ADR-0130). The text level keeps the Manual, the Act and the Regulations
   apart: a box, a colour and a mark for each. */

import { esc, fmt, el, load, kindColour, kindCount, refChip, refLabel, trustBadge, kindChip, legend, isLaw, sourceOf, quoteBlock, SOURCES, openPassage } from "./app.js";
import { KIND_POS, LOOSE, specificCount } from "./kinds.js";
import * as lib from "./lib.js";

const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const FAMILY_OF = (kinds) => Object.fromEntries(kinds.map((k) => [k.id, k.family]));
// What a thing is sorts it into a family; what it does is an arrow (ruling B1).
const FAMILY_LABELS = [
  ["reasoning", "The questions the law asks"],
  ["examined", "What they are asked about"],
  ["process", "The process around them"],
];
const FAMILY_NAME = { reasoning: "The law's questions", examined: "What is examined", process: "The process" };

export async function render(root, { ontology, params }) {
  const [cytoscape, Fuse, search, stability] = await Promise.all([lib.cytoscape(), lib.fuse(), load("search"), load("stability")]);
  const byId = new Map(ontology.concepts.map((c) => [c.id, c]));
  const kinds = new Map(ontology.kinds.map((k) => [k.id, k]));
  const familyOf = FAMILY_OF(ontology.kinds);
  const relOf = new Map();
  for (const r of ontology.relations) for (const end of [r.s, r.o]) { if (!relOf.has(end)) relOf.set(end, []); relOf.get(end).push(r); }
  const relById = new Map(ontology.relations.map((r) => [r.id, r]));
  const c = ontology.counts;
  const totalPassages = stability.pages.reduce((n, p) => n + p.passages, 0);

  const level0 = ["kinds", "ideas", "text"].includes(params[0]) ? params[0] : "kinds";
  const state = {
    expanded: new Set(level0 === "kinds" ? [] : ontology.kinds.map((k) => k.id)),
    concept: params[1] && byId.has(params[1]) ? params[1] : null,
    text: null,
    parts: new Set(),
    loose: false, allKindLinks: false,
  };

  if (level0 === "text") state.text = state.concept || defaultConcept();
  if (state.text) state.concept = state.text;

  root.innerHTML = `
  <div class="map-shell">
    <div class="map-rail">
      <div class="rail-ladder" role="tablist" aria-label="Level of detail">
        ${lvl("kinds", 1, "Kinds of idea", `${kindCount(ontology)} kinds, and how their members connect`, "Rests on no single passage")}
        ${lvl("ideas", 2, "Ideas and connections", `${fmt(c.concepts.signed + c.concepts.machine)} ideas · ${fmt(c.relations.signed + c.relations.machine)} connections`, "Each pinned to a quoted passage")}
        ${lvl("text", 3, "The text", `${fmt(totalPassages)} Manual passages · the Act and Regulations`, `${fmt(stability.events)} amendments since ${Object.keys(stability.by_year)[0]}`)}
      </div>
      <div class="rail-box">
        <h4>Find an idea</h4>
        <input class="find" type="search" placeholder="e.g. consent, confusing, oppose" aria-label="Find an idea" autocomplete="off">
        <div class="find-results"></div>
      </div>
      <div class="rail-box kind-toggles">
        <h4>Open or close a kind</h4>
        <div class="toggles"></div>
      </div>
      <div class="rail-box filters">
        <h4>Show</h4>
        <label><input type="checkbox" data-f="loose"> "Is a kind of" links</label>
        <label><input type="checkbox" data-f="allKindLinks"> Weak links between closed kinds</label>
      </div>
      <div class="rail-box family-box">
        <h4>How the families connect</h4>
        <ul class="small family-links">${(ontology.family_links || []).filter((r) => r.s !== r.o).map((r) => `<li><b>${esc(FAMILY_NAME[r.s])}</b> → <b>${esc(FAMILY_NAME[r.o].toLowerCase())}</b>:
          ${Object.entries(r.predicates).slice(0, 2).map(([p, n]) => `${esc(ontology.predicates[p]?.label || p)} ${n}`).join(", ")} <span class="muted">(${r.total})</span></li>`).join("")}</ul>
      </div>
      <div class="rail-box"><h4>Where the words come from</h4>${legend()}</div>
    </div>
    <div class="canvas-wrap">
      <div class="cy" role="img" aria-label="The ontology map"></div>
      <div class="canvas-title"><b></b><span></span></div>
      <div class="hovercard" hidden></div>
      <div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button><button type="button" data-z="fit" aria-label="Fit to view">⤢</button></div>
    </div>
    <aside class="side" aria-live="polite"></aside>
  </div>`;

  const container = root.querySelector(".cy");
  const side = root.querySelector(".side");
  const title = root.querySelector(".canvas-title");
  const card = root.querySelector(".hovercard");
  await document.fonts.ready;

  const cy = cytoscape({
    container, style: styles(), layout: { name: "preset" },
    minZoom: 0.15, maxZoom: 4, boxSelectionEnabled: false,
  });
  container.cy = cy; // for the browser checks in the handoff's verification notes
  let layout = null;

  // ------------------------------------------------------------ styles

  function styles() {
    const ink = css("--ink"), ink2 = css("--ink-2"), ink3 = css("--ink-3"), bg = css("--bg"), panel = css("--panel"), line = css("--line");
    const manual = css("--manual"), manualBg = css("--manual-bg"), act = css("--act"), actBg = css("--act-bg"), regs = css("--regs"), regsBg = css("--regs-bg");
    const serif = css("--serif"), sans = css("--sans");
    return [
      { selector: "node", style: { "font-family": sans, color: ink, "text-outline-width": 0, "overlay-opacity": 0 } },
      { selector: "node.family", style: {
        shape: "round-rectangle", "background-color": ink, "background-opacity": 0.025, "border-width": 1, "border-style": "dashed",
        "border-color": line, label: "data(label)", "text-valign": "top", "text-halign": "center", "text-margin-y": -6,
        "font-size": 15, "font-weight": 600, color: ink3, "text-transform": "uppercase", padding: 30 } },
      { selector: "node.kind", style: {
        shape: "ellipse", width: "data(size)", height: "data(size)", "background-color": "data(col)", "background-opacity": 0.16,
        "border-width": 3, "border-color": "data(col)", label: "data(label)", "text-wrap": "wrap", "text-max-width": 130,
        "text-valign": "center", "font-family": serif, "font-size": 17, "font-weight": 600, "line-height": 1.25 } },
      { selector: "node.kind:parent", style: {
        shape: "round-rectangle", "background-opacity": 0.06, "border-width": 1.6, label: "data(name)",
        "text-valign": "top", "text-halign": "center", "text-margin-y": -6, "font-size": 30, padding: 24, "text-wrap": "none",
        "text-max-width": 2000, "text-background-color": bg, "text-background-opacity": 0.6, "text-background-padding": 3 } },
      { selector: "node.region", style: {
        width: 1, height: 1, "background-opacity": 0, "border-width": 0, label: "data(label)", "text-valign": "center", "text-halign": "right",
        "font-size": 30, "font-weight": 600, color: ink3, "text-transform": "uppercase", events: "no" } },
      { selector: "node.concept", style: {
        width: "data(size)", height: "data(size)", "background-color": "data(col)", "border-width": 2, "border-color": "data(col)",
        label: "data(label)", "text-valign": "bottom", "text-margin-y": 4, "font-size": 13, "text-wrap": "wrap", "text-max-width": 140,
        "text-background-color": bg, "text-background-opacity": 0.75, "text-background-padding": 1.5, "text-background-shape": "round-rectangle",
        "min-zoomed-font-size": 7 } },
      { selector: "node.focus", style: { width: 52, height: 52, "font-size": 22, "font-weight": 600, "font-family": serif } },
      { selector: "node.near", style: { "font-size": 17, "min-zoomed-font-size": 5 } },
      // One box per text: the Manual (practice), the Act and the Regulations (law).
      { selector: "node.group", style: {
        shape: "round-rectangle", "background-opacity": 0.35, "border-width": 2, "border-style": "solid", "border-color": line,
        label: "data(label)", "text-valign": "top", "text-halign": "center", "text-margin-y": -5, "font-size": 19, "font-weight": 650,
        color: ink3, padding: 18, "text-wrap": "wrap", "text-max-width": 600, "line-height": 1.25 } },
      { selector: "node.group.manual", style: { "background-color": manualBg, "border-color": manual, color: manual } },
      { selector: "node.group.act", style: { "background-color": actBg, "border-color": act, color: act } },
      { selector: "node.group.regs", style: { "background-color": regsBg, "border-color": regs, color: regs } },
      { selector: "node.part", style: {
        shape: "round-rectangle", width: "data(size)", height: 34, "background-color": manualBg, "border-color": manual, "border-width": 1.5,
        label: "data(label)", "text-valign": "center", "font-size": 14, color: manual } },
      { selector: "node.part:parent", style: { "text-valign": "top", padding: 10, "background-opacity": 0.5 } },
      { selector: "node.psg", style: {
        shape: "rectangle", width: 12, height: 12, "background-color": manualBg, "border-color": manual, "border-width": 1.2, label: "" } },
      { selector: "node.psg.evidence", style: { "background-color": manual } },
      { selector: "node.law", style: {
        width: 24, height: 24, "border-width": 2, label: "data(label)", "text-valign": "center", "text-halign": "right",
        "text-margin-x": 7, "font-size": 15, "font-weight": 600 } },
      { selector: "node.law.act", style: { shape: "diamond", "background-color": actBg, "border-color": act, color: act } },
      { selector: "node.law.regs", style: { shape: "hexagon", width: 26, height: 22, "background-color": regsBg, "border-color": regs, color: regs } },
      { selector: "edge", style: {
        "curve-style": "bezier", width: 1.2, "line-color": ink3, "target-arrow-color": ink3, "target-arrow-shape": "triangle",
        "arrow-scale": 0.75, opacity: 0.55, "overlay-opacity": 0 } },
      { selector: "edge.rel", style: { opacity: 0.35 } },
      { selector: "edge.loose", style: { opacity: 0.22, "target-arrow-shape": "none" } },
      { selector: "edge.meta", style: {
        width: "data(w)", "line-style": "solid", opacity: 0.5, "curve-style": "bezier", "control-point-step-size": 60,
        label: "data(label)", "font-size": 13, color: ink2, "text-background-color": bg, "text-background-opacity": 0.85,
        "text-background-padding": 2, "text-rotation": "autorotate", "min-zoomed-font-size": 6, "arrow-scale": 0.9 } },
      { selector: "edge.cites", style: { "line-color": manual, "target-arrow-shape": "none", opacity: 0.35, width: 1 } },
      { selector: "edge.basis.act", style: { "line-color": act, "target-arrow-shape": "none", opacity: 0.55, width: 1.4 } },
      { selector: "edge.basis.regs", style: { "line-color": regs, "target-arrow-shape": "none", opacity: 0.55, width: 1.4 } },
      { selector: ".faded", style: { opacity: 0.1, "text-opacity": 0.15 } },
      { selector: "node.faded.family, node.faded.kind:parent", style: { opacity: 0.45, "text-opacity": 0.6 } },
      { selector: "edge.hl", style: { opacity: 1, width: 2.4, "line-color": ink, "target-arrow-color": ink, "z-index": 9 } },
      { selector: "edge.hl[pred]", style: { label: "data(pred)", "font-size": 11, color: ink2, "text-background-color": bg,
        "text-background-opacity": 0.85, "text-rotation": "autorotate" } },
      { selector: "node:selected", style: { "border-width": 4, "border-color": ink, "border-style": "solid" } },
    ];
  }

  // ------------------------------------------------------------ elements

  const conceptSize = (x) => Math.min(34, 14 + 3.4 * Math.log2(1 + x.mentions));
  const kindSize = (k) => 74 + 14 * Math.sqrt(k.signed + k.machine);
  const rep = (id) => {
    const x = byId.get(id);
    return state.expanded.has(x.kind) ? id : `kind:${x.kind}`;
  };

  function graphElements() {
    const els = [];
    const colour = (kind) => css(`--k-${kind}`);
    // Family boxes only while every kind is closed: a second level of nesting
    // makes the compound layout overlap boxes once kinds open.
    const families = state.expanded.size === 0;
    for (const [family, label] of FAMILY_LABELS) {
      els.push(families
        ? { data: { id: `fam:${family}`, label }, classes: "family" }
        : { data: { id: `region:${family}`, label }, classes: "region" });
    }
    const members = (kind) => ontology.concepts.filter((x) => x.kind === kind);
    for (const k of ontology.kinds) {
      const list = members(k.id);
      if (!list.length) continue;
      const parent = !families || familyOf[k.id] === "other" ? undefined : `fam:${familyOf[k.id]}`;
      const open = state.expanded.has(k.id);
      els.push({
        data: { id: `kind:${k.id}`, parent, kind: k.id, col: colour(k.id), size: kindSize(k),
          label: `${k.label}\n${list.length} ideas`, name: `${k.label} · ${list.length}` },
        classes: `kind${open ? " open" : ""}`,
      });
      if (open) {
        for (const x of list) {
          els.push({ data: { id: x.id, parent: `kind:${k.id}`, label: x.label, col: colour(x.kind), size: conceptSize(x), kind: x.kind },
            classes: "concept" });
        }
      }
    }
    const meta = new Map();
    for (const r of ontology.relations) {
      const a = byId.get(r.s), b = byId.get(r.o);
      if (!a || !b) continue;
      const ra = rep(r.s), rb = rep(r.o);
      if (ra === rb) continue;
      if (!ra.startsWith("kind:") && !rb.startsWith("kind:")) {
        if (LOOSE.has(r.p) && !state.loose) continue;
        els.push({ data: { id: r.id, source: r.s, target: r.o, pred: ontology.predicates[r.p]?.label || r.p, rel: r.id },
          classes: `rel${LOOSE.has(r.p) ? " loose" : ""}` });
        continue;
      }
      const key = `${ra}>${rb}`;
      if (!meta.has(key)) meta.set(key, { s: ra, o: rb, total: 0, predicates: {}, ids: [] });
      const m = meta.get(key);
      m.total++;
      m.predicates[r.p] = (m.predicates[r.p] || 0) + 1;
      m.ids.push(r.id);
    }
    // Every closed kind keeps at least its strongest link, so none floats free (ADR-0131).
    const best = new Map();
    for (const m of meta.values()) {
      if (!(m.s.startsWith("kind:") && m.o.startsWith("kind:"))) continue;
      const strong = m.total - (m.predicates.broader || 0);
      for (const end of [m.s, m.o]) best.set(end, Math.max(best.get(end) || 0, strong));
    }
    for (const [key, m] of meta) {
      const strong = m.total - (m.predicates.broader || 0);
      const kindToKind = m.s.startsWith("kind:") && m.o.startsWith("kind:");
      const strongest = strong > 0 && (strong === best.get(m.s) || strong === best.get(m.o));
      if (kindToKind && !state.allKindLinks && strong < 5 && !strongest) continue;
      if (!kindToKind && strong < 1 && !state.loose) continue;
      const top = Object.entries(m.predicates).sort((a, b) => b[1] - a[1]).find(([p]) => !LOOSE.has(p)) || Object.entries(m.predicates)[0];
      const name = ontology.predicates[top[0]]?.label || top[0];
      els.push({
        data: { id: `meta:${key}`, source: m.s, target: m.o, w: (1 + 1.6 * Math.log2(1 + m.total)).toFixed(2),
          label: kindToKind && strong < 8 ? "" : `${name} · ${top[1]}`, pred: `${m.total} connections`, meta: m },
        classes: "meta",
      });
    }
    return els;
  }

  function textElements(id) {
    const x = byId.get(id);
    const els = [{ data: { id: x.id, label: x.label, col: css(`--k-${x.kind}`), size: 46 }, classes: "concept focus" }];
    const rels = (relOf.get(id) || []).filter((r) => byId.has(r.s) && byId.has(r.o) && (state.loose || !LOOSE.has(r.p)));
    for (const r of rels) {
      const other = r.s === id ? r.o : r.s;
      const o = byId.get(other);
      if (!els.some((e) => e.data.id === other)) {
        els.push({ data: { id: other, label: o.label, col: css(`--k-${o.kind}`), size: conceptSize(o) }, classes: "concept near" });
      }
      els.push({ data: { id: r.id, source: r.s, target: r.o, pred: ontology.predicates[r.p]?.label || r.p, rel: r.id }, classes: "rel" });
    }
    const refs = [...new Set(search.mentions[id] || [])];
    const evidence = new Set([...x.evidence.map((e) => e.ref), ...x.sources]);
    for (const r of relOf.get(id) || []) if (r.ref) evidence.add(r.ref);
    for (const ref of evidence) if (!isLaw(ref) && !refs.includes(ref)) refs.push(ref);
    const byPart = new Map();
    for (const ref of refs) {
      const part = (ref.match(/^TMM\/(Part[0-9]+[A-Za-z]*)/) || [])[1] || "?";
      if (!byPart.has(part)) byPart.set(part, []);
      byPart.get(part).push(ref);
    }
    els.push({ data: { id: "grp:manual", label: `${SOURCES.manual.name} · practice\n${refs.length} passage${refs.length === 1 ? "" : "s"}` }, classes: "group manual" });
    for (const [part, list] of [...byPart.entries()].sort((a, b) => b[1].length - a[1].length)) {
      const pid = `part:${part}`;
      const quoted = list.filter((r) => evidence.has(r)).length;
      els.push({ data: { id: pid, parent: "grp:manual", label: `${part.replace("Part", "Part ")} · ${list.length}${quoted ? ` · ${quoted} quoted` : ""}`,
        size: 150 + Math.min(40, list.length), part }, classes: "part" });
      els.push({ data: { id: `e:${pid}`, source: id, target: pid }, classes: "cites" });
      if (state.parts.has(part)) {
        for (const ref of list) els.push({ data: { id: `psg:${ref}`, parent: pid, ref, label: refLabel(ref) }, classes: `psg${evidence.has(ref) ? " evidence" : ""}` });
      }
    }
    const laws = [...new Set([...x.basis, ...(relOf.get(id) || []).flatMap((r) => [r.s, r.o]).filter(isLaw)])];
    for (const src of ["act", "regs"]) {
      const list = laws.filter((ref) => sourceOf(ref) === src);
      if (!list.length) continue;
      els.push({ data: { id: `grp:${src}`, label: `${SOURCES[src].name} · law\n${list.length} provision${list.length === 1 ? "" : "s"}` }, classes: `group ${src}` });
      for (const ref of list) {
        els.push({ data: { id: `law:${ref}`, parent: `grp:${src}`, ref, label: refLabel(ref) }, classes: `law ${src}` });
        els.push({ data: { id: `e:law:${ref}`, source: id, target: `law:${ref}` }, classes: `basis ${src}` });
      }
    }
    return els;
  }

  // ------------------------------------------------------------ drawing

  function level() {
    if (state.text) return "text";
    return state.expanded.size ? "ideas" : "kinds";
  }

  // Positions are computed, not simulated: the same state always draws the same
  // picture, boxes never overlap, and Cytoscape animates between states.
  const CELL_W = 140, CELL_H = 80, BOX_PAD = 30, BOX_TOP = 50, GAP = 80;

  function membersOf(kind) {
    return ontology.concepts.filter((x) => x.kind === kind).sort((a, b) => b.mentions - a.mentions);
  }

  function graphPositions() {
    const pos = new Map();
    if (!state.expanded.size) {
      for (const k of ontology.kinds) pos.set(`kind:${k.id}`, { x: KIND_POS[k.id].x * 1.25, y: KIND_POS[k.id].y * 1.25 });
      return pos;
    }
    const boxes = ontology.kinds.map((k) => {
      const list = membersOf(k.id);
      if (!state.expanded.has(k.id) || !list.length) return { k, list, open: false, w: kindSize(k) + 50, h: kindSize(k) + 50 };
      const cols = Math.max(2, Math.ceil(Math.sqrt(list.length * 1.7)));
      return { k, list, open: true, cols, w: cols * CELL_W + BOX_PAD * 2, h: Math.ceil(list.length / cols) * CELL_H + BOX_PAD + BOX_TOP };
    });
    let originX = 0;
    for (const family of ["reasoning", "examined", "process", "other"]) {
      const group = boxes.filter((b) => (b.k.family || familyOf[b.k.id]) === family);
      if (!group.length) continue;
      const maxW = Math.max(820, ...group.map((b) => b.w));
      let x = 0, y = 110, rowH = 0, widest = 0;
      pos.set(`region:${family}`, { x: originX, y: 30 });
      for (const b of group) {
        if (x > 0 && x + b.w > maxW) { x = 0; y += rowH + GAP; rowH = 0; }
        b.left = originX + x; b.top = y;
        x += b.w + GAP; rowH = Math.max(rowH, b.h); widest = Math.max(widest, x - GAP);
      }
      originX += widest + GAP * 2.5;
    }
    for (const b of boxes) {
      if (!b.open) { pos.set(`kind:${b.k.id}`, { x: b.left + b.w / 2, y: b.top + b.h / 2 }); continue; }
      b.list.forEach((x, i) => {
        pos.set(x.id, { x: b.left + BOX_PAD + CELL_W * ((i % b.cols) + 0.5), y: b.top + BOX_TOP + CELL_H * (Math.floor(i / b.cols) + 0.35) });
      });
    }
    return pos;
  }

  function textPositions() {
    const pos = new Map();
    pos.set(state.text, { x: 0, y: 0 });
    const neighbours = cy.nodes(".concept").filter((n) => n.id() !== state.text).map((n) => n.id());
    const perCol = 12;
    neighbours.forEach((id, i) => {
      const col = Math.floor(i / perCol), row = i % perCol, inCol = Math.min(perCol, neighbours.length - col * perCol);
      pos.set(id, { x: -360 - col * 230, y: (row - (inCol - 1) / 2) * 74 });
    });
    const parts = cy.nodes(".part");
    let x = 0, y = 0, rowH = 0;
    const left = 300, maxW = 700;
    parts.forEach((part) => {
      const kids = part.children();
      const cols = kids.length ? Math.min(12, Math.max(4, Math.ceil(Math.sqrt(kids.length * 2)))) : 0;
      const w = kids.length ? cols * 20 + 20 : 210, h = kids.length ? Math.ceil(kids.length / cols) * 20 + 40 : 50;
      if (x > 0 && x + w > maxW) { x = 0; y += rowH + 24; rowH = 0; }
      if (kids.length) kids.forEach((k, i) => pos.set(k.id(), { x: left + x + 20 + (i % cols) * 20, y: y + 30 + Math.floor(i / cols) * 20 }));
      else pos.set(part.id(), { x: left + x + w / 2, y: y + h / 2 });
      x += w + 24; rowH = Math.max(rowH, h);
    });
    const manualH = y + rowH;
    cy.nodes(".part").forEach((part) => {
      if (part.children().length) return;
      const p = pos.get(part.id()); pos.set(part.id(), { x: p.x, y: p.y - manualH / 2 });
    });
    cy.nodes(".psg").forEach((n) => { const p = pos.get(n.id()); pos.set(n.id(), { x: p.x, y: p.y - manualH / 2 }); });
    // The Act and the Regulations below everything else, each in a box of its own,
    // its provisions in rows: the Act first, the Regulations to its right.
    const below = Math.max(120, manualH / 2, ...neighbours.map((id) => pos.get(id).y)) + 150;
    const PER_ROW = 5, STEP = 150;
    let lawX = -150;
    for (const src of ["act", "regs"]) {
      const list = cy.nodes(`.law.${src}`);
      list.forEach((n, i) => pos.set(n.id(), { x: lawX + (i % PER_ROW) * STEP, y: below + Math.floor(i / PER_ROW) * 52 }));
      if (list.length) lawX += Math.min(PER_ROW, list.length) * STEP + 140;
    }
    return pos;
  }

  function draw({ fresh = false } = {}) {
    hideCard();
    const lv = level();
    const old = new Map(cy.nodes().map((n) => [n.id(), { ...n.position() }]));
    cy.batch(() => {
      cy.elements().remove();
      cy.add(lv === "text" ? textElements(state.text) : graphElements());
      cy.style(styles());
    });
    const target = lv === "text" ? textPositions() : graphPositions();
    // Start each node where it was, or where its kind was, so the move reads.
    cy.batch(() => cy.nodes().forEach((n) => {
      if (n.isParent()) return;
      const kind = byId.get(n.id())?.kind;
      const start = old.get(n.id()) || (kind && old.get(`kind:${kind}`)) || target.get(n.id());
      if (start) n.position(start);
    }));
    updateChrome(lv);
    layout = cy.layout({
      name: "preset", positions: (n) => target.get(n.id()) || n.position(),
      animate: !fresh && !reduced(), animationDuration: 650, animationEasing: "ease-in-out-cubic", fit: true, padding: 40,
    });
    layout.one("layoutstop", () => {
      if (lv === "text") { cy.getElementById(state.text).select(); return; }
      if (state.concept && cy.getElementById(state.concept).nonempty()) focusConcept(state.concept);
    });
    layout.run();
  }

  function updateChrome(lv) {
    root.querySelectorAll(".lvl").forEach((b) => { b.classList.toggle("on", b.dataset.level === lv); b.setAttribute("aria-selected", b.dataset.level === lv); });
    const hash = `#/map/${lv}${(lv === "text" ? state.text : state.concept) && lv !== "kinds" ? "/" + (lv === "text" ? state.text : state.concept) : ""}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
    const tb = title.querySelector("b"), ts = title.querySelector("span");
    if (lv === "kinds") {
      tb.textContent = `${kindCount(ontology)} kinds of idea, and what connects them`;
      ts.textContent = "Each circle holds the ideas of one kind; arrows roll their connections up. Click a kind to open it.";
    } else if (lv === "ideas") {
      tb.textContent = state.expanded.size === ontology.kinds.length ? "Every idea and its connections" : `${state.expanded.size} kind${state.expanded.size > 1 ? "s" : ""} open, the rest in outline`;
      ts.textContent = "Colour is the kind of idea. Zoom in to read names; click an idea; double-click a box to close its kind.";
    } else {
      const x = byId.get(state.text);
      tb.textContent = `${x.label}: what it rests on`;
      ts.textContent = "Its connections; the Parts of the Manual that name it (click one to open its passages); and the sections of the Act and the regulations it rests on, each in a box of its own.";
    }
    root.querySelectorAll(".toggles input").forEach((box) => { box.checked = state.expanded.has(box.dataset.kind); box.disabled = lv === "text"; });
  }

  // ------------------------------------------------------------ focus, hover

  function clearFocus() {
    cy.elements().removeClass("faded hl");
  }

  function focusConcept(id, { pan = true } = {}) {
    const node = cy.getElementById(id);
    if (node.empty()) return;
    clearFocus();
    cy.elements().unselect();
    node.select();
    const near = node.closedNeighborhood();
    cy.elements().not(near).not(node.ancestors()).not(near.ancestors()).addClass("faded");
    near.edges().addClass("hl");
    if (pan) cy.animate({ fit: { eles: near, padding: 80 }, duration: reduced() ? 0 : 500, easing: "ease-in-out-cubic" });
  }

  function showCard(node) {
    const x = byId.get(node.id());
    if (!x) { hideCard(); return; }
    const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
    const quote = first ? String(first.quote) : "";
    card.innerHTML = `<b>${esc(x.label)}</b><div class="meta">${kindChip(x.kind, ontology)}${trustBadge(x.origin)}</div>
      ${quote ? quoteBlock(first.ref, quote.length > 170 ? quote.slice(0, 168) + "…" : quote) : ""}
      <span class="tiny">${fmt(x.mentions)} passages · ${(relOf.get(x.id) || []).length} connections</span>`;
    const p = node.renderedPosition();
    const box = container.getBoundingClientRect();
    card.hidden = false;
    const w = card.offsetWidth, h = card.offsetHeight;
    card.style.left = `${Math.min(box.width - w - 8, Math.max(8, p.x + 16))}px`;
    card.style.top = `${Math.min(box.height - h - 8, Math.max(8, p.y - h / 2))}px`;
  }
  function hideCard() { card.hidden = true; }

  // ------------------------------------------------------------ events

  cy.on("mouseover", "node.concept", (e) => { showCard(e.target); if (!state.concept) e.target.closedNeighborhood().edges().addClass("hl"); });
  cy.on("mouseout", "node.concept", (e) => { hideCard(); if (!state.concept) e.target.closedNeighborhood().edges().removeClass("hl"); });
  cy.on("pan zoom", hideCard);

  cy.on("tap", "node.kind", (e) => {
    const kind = e.target.data("kind");
    if (e.target.isParent()) { showKind(kinds.get(kind)); return; }
    state.expanded.add(kind);
    state.concept = null;
    draw();
    showKind(kinds.get(kind));
  });
  cy.on("dbltap", "node.kind", (e) => {
    state.expanded.delete(e.target.data("kind"));
    state.concept = null;
    draw();
  });
  cy.on("tap", "node.concept", (e) => selectConcept(e.target.id()));
  cy.on("tap", "edge.rel", (e) => { side.innerHTML = relationCard(relById.get(e.target.data("rel"))); bindSide(); });
  cy.on("tap", "edge.meta", (e) => showMeta(e.target.data("meta")));
  cy.on("tap", "node.part", (e) => {
    const part = e.target.data("part");
    if (state.parts.has(part)) state.parts.delete(part); else state.parts.add(part);
    draw();
  });
  cy.on("tap", "node.psg, node.law", (e) => {
    const x = byId.get(state.text);
    openPassage(e.target.data("ref"), { highlight: x ? [x.label, ...x.alt] : [] });
  });
  cy.on("tap", (e) => {
    if (e.target !== cy) return;
    state.concept = null;
    clearFocus();
    cy.elements().unselect();
    if (level() !== "text") showLevelHelp();
    updateChrome(level());
  });

  function selectConcept(id) {
    state.concept = id;
    const x = byId.get(id);
    if (level() === "text") {
      if (id !== state.text) { state.text = id; state.parts.clear(); draw(); }
    } else if (!state.expanded.has(x.kind)) {
      state.expanded.add(x.kind);
      draw();
    } else {
      focusConcept(id);
    }
    updateChrome(level());
    showConcept(x);
  }

  function setLevel(lv) {
    if (lv === "kinds") { state.expanded.clear(); state.text = null; state.concept = null; draw(); showLevelHelp(); return; }
    if (lv === "ideas") { ontology.kinds.forEach((k) => state.expanded.add(k.id)); state.text = null; draw(); if (state.concept) showConcept(byId.get(state.concept)); else showLevelHelp(); return; }
    state.text = state.concept || defaultConcept();
    state.concept = state.text;
    state.parts.clear();
    draw();
    showConcept(byId.get(state.text));
  }

  function defaultConcept() {
    return [...ontology.concepts].filter((x) => x.origin === "signed").sort((a, b) => (relOf.get(b.id) || []).length - (relOf.get(a.id) || []).length)[0].id;
  }

  // ------------------------------------------------------------ side panel

  function showLevelHelp() {
    const lv = level();
    side.innerHTML = (lv === "kinds" ? `<h2>Start with the shape</h2>
        <p>Every idea in the map is sorted by <b>what it is</b> into one of ${kindCount(ontology)} kinds. Three are <b>the questions the law asks</b> — grounds of
        refusal, the tests that decide them, and the principles that govern how they are answered. Four are <b>what those questions are asked about</b> —
        the mark, what it contains or conveys, the context outside it, and what people do with it in trade. Four are <b>the process around them</b> — who
        acts, the steps, the records, and the bodies of rules outside the Act.</p>
        <p><b>What an idea does is an arrow, not a kind</b>, and every arrow says what it means. Sign content <i>may give rise to</i> a ground and context
        <i>qualifies</i> a test; a ground <i>is overcome by</i> its remedy and <i>is assessed in</i> a step; a role <i>performs</i> a step, a step
        <i>operates on</i> an application and <i>results in</i> a record, which <i>is recorded in</i> a register. Each relation names the kinds it may join,
        so the kinds connect in known ways. The arrows roll ${fmt(c.relations.signed + c.relations.machine)} individual connections up into the patterns they make;
        every kind keeps at least its strongest.</p>
        <p><b>Click a kind to open it</b>; open several to compare them in detail while the rest stay in outline.</p>`
      : `<h2>The ideas themselves</h2>
        <p>Each open kind is a box of its ideas. Lines are connections between two ideas, each resting on a sentence in the Manual. Where an idea
        connects into a kind that is still closed, the connections are rolled up into one arrow with a count.</p>
        <p>Hover over an idea to see what it rests on; click it to follow its connections.</p>`) +
      `<p><a class="btn small" href="#/table/${lv === "kinds" ? "kinds" : "ideas"}">See it as a table instead →</a></p>` +
      `<p class="muted small">Most ideas and connections were written by a machine from the Manual's text — usable, but not yet reviewed; each says
       so where it is shown. Grounds and tests are the project owner's own kinds, as is the rule that a kind says what an idea is while an arrow says
       what it does; the other nine kinds were proposed by a machine.</p>
      <h4>The kinds</h4><ul class="rel-list">${ontology.kinds.map((k) => `<li><span class="dot" style="--c:${kindColour(k.id)}"></span><span><b>${esc(k.label)}</b> <span class="muted small">— ${esc(k.plain)}</span></span></li>`).join("")}</ul>`;
  }

  function showKind(k) {
    const members = ontology.concepts.filter((x) => x.kind === k.id).sort((a, b) => b.mentions - a.mentions);
    const out = ontology.kind_links.filter((r) => r.s === k.id && r.o !== k.id).sort((a, b) => specificCount(b) - specificCount(a)).slice(0, 5);
    const inn = ontology.kind_links.filter((r) => r.o === k.id && r.s !== k.id).sort((a, b) => specificCount(b) - specificCount(a)).slice(0, 5);
    const open = state.expanded.has(k.id);
    side.innerHTML = `
      <h2>${esc(k.label)}</h2>
      <div class="meta">${kindChip(k.id, ontology)}<span class="chip">${k.signed + k.machine} ideas</span></div>
      <p>${esc(capital(k.plain))}.</p>
      <p><button class="btn ${open ? "" : "primary "}small" type="button" data-toggle>${open ? "Close this kind" : `Open its ${k.signed + k.machine} ideas`}</button></p>
      <h4>Strongest patterns out</h4>${kindRows(out, "o")}
      <h4>Strongest patterns in</h4>${kindRows(inn, "s")}
      <h4>Its ideas</h4>
      <ul class="rel-list">${members.map((m) => `<li><span class="dot" style="--c:${kindColour(m.kind)}"></span><button class="link" type="button" data-c="${m.id}">${esc(m.label)}</button></li>`).join("")}</ul>`;
    side.querySelector("[data-toggle]").addEventListener("click", () => {
      if (state.expanded.has(k.id)) state.expanded.delete(k.id); else state.expanded.add(k.id);
      draw(); showKind(k);
    });
    bindSide();
  }

  function kindRows(rows, end) {
    if (!rows.length) return `<p class="empty small">None.</p>`;
    return `<ul class="rel-list">${rows.map((r) => {
      const top = Object.entries(r.predicates).filter(([p]) => !LOOSE.has(p)).slice(0, 2)
        .map(([p, n]) => `${esc(ontology.predicates[p]?.label || p)} ${n}`).join(", ") || "loosely related";
      return `<li><span class="dot" style="--c:${kindColour(r[end])}"></span><span><b>${esc(kinds.get(r[end]).label)}</b> <span class="muted small">— ${r.total} connections: ${top}</span></span></li>`;
    }).join("")}</ul>`;
  }

  function showMeta(m) {
    const name = (id) => (id.startsWith("kind:") ? `${kinds.get(id.slice(5)).label} (closed)` : byId.get(id)?.label || id);
    const examples = m.ids.map((id) => relById.get(id)).sort((a, b) => (a.origin === "signed" ? -1 : 1) - (b.origin === "signed" ? -1 : 1)).slice(0, 6);
    side.innerHTML = `
      <h2>${esc(name(m.s))} → ${esc(name(m.o))}</h2>
      <p class="muted">${m.total} connection${m.total > 1 ? "s" : ""} rolled up into this arrow. Open a kind to see them one by one.</p>
      <h4>What they say</h4>
      <ul class="rel-list">${Object.entries(m.predicates).sort((a, b) => b[1] - a[1]).map(([p, n]) => `<li><span class="pred num">${n}×</span><span>${esc(ontology.predicates[p]?.label || p)}</span></li>`).join("")}</ul>
      <h4>Examples, with the sentence each rests on</h4>
      ${examples.map((r) => relationCard(r)).join("")}`;
    bindSide();
  }

  // Each author rates itself on its own scale — the bulk model at 0.84–0.99, an agent
  // session at 0.5–0.9 — so a score is shown with its author and never compared,
  // ranked or filtered across authors (review F6, ADR-0125).
  function selfRated(m) {
    return `<span title="The author's rating of its own record, on its own scale. Not comparable across authors.">self-rated ${esc(m.confidence)} by <code>${esc(m.by || "?")}</code></span>`;
  }

  function relationCard(r) {
    const name = (id) => byId.get(id)?.label || refLabel(id);
    return `<div style="margin:.6rem 0 1rem">
      <div class="meta">${trustBadge(r.origin)}${r.modality ? `<span class="chip">${esc(r.modality)}</span>` : ""}</div>
      <div><b>${esc(name(r.s))}</b> <span class="muted">— ${esc(ontology.predicates[r.p]?.label || r.p)} →</span> <b>${esc(name(r.o))}</b></div>
      ${r.quote ? quoteBlock(r.ref, r.quote) : ""}
      ${r.ref ? refChip(r.ref) : ""}
      ${r.replaces ? `<p class="tiny">A corrected reading of ${esc(r.replaces)}, which is kept unchanged.</p>` : ""}
      ${r.machine?.reasoning ? `<details><summary>Why the machine wrote this${r.machine.confidence ? ` · ${selfRated(r.machine)}` : ""}</summary><p class="small muted">${esc(r.machine.reasoning)}</p></details>` : ""}
    </div>`;
  }

  function showConcept(x) {
    const rels = relOf.get(x.id) || [];
    const groups = new Map();
    for (const r of rels) {
      const outgoing = r.s === x.id;
      const other = outgoing ? r.o : r.s;
      const key = `${outgoing ? "out" : "in"}:${r.p}`;
      if (!groups.has(key)) groups.set(key, { outgoing, p: r.p, items: [] });
      groups.get(key).items.push({ r, other });
    }
    const ordered = [...groups.values()].sort((a, b) => (LOOSE.has(a.p) - LOOSE.has(b.p)) || b.items.length - a.items.length);
    const refs = [...new Set(search.mentions[x.id] || [])];
    const first = x.evidence.find((e) => e.for === "concept") || x.evidence[0];
    side.innerHTML = `
      <h2>${esc(x.label)}</h2>
      <div class="meta">${kindChip(x.kind, ontology)}${trustBadge(x.origin)}</div>
      ${x.alt.length ? `<p class="small"><span class="muted">Also called</span> ${x.alt.map(esc).join(" · ")}</p>` : ""}
      ${x.not.length ? `<p class="small"><span class="muted">Not the same as</span> ${x.not.map(esc).join(" · ")}</p>` : ""}
      ${first ? `<h4>What it rests on</h4>${quoteBlock(first.ref, first.quote)}${refChip(first.ref)}
        <span class="tiny">${first.for === "kind" ? "quoted when the machine sorted it into its kind" : "quoted by the record itself"}</span>` : ""}
      ${["act", "regs"].map((src) => {
        const list = x.basis.filter((r) => sourceOf(r) === src);
        return list.length ? `<h4>In the ${src === "act" ? "Act" : "Regulations"}</h4><div class="meta">${list.map((r) => refChip(r)).join("")}</div>` : "";
      }).join("")}
      ${x.notes ? `<h4>Note on the record</h4><p class="small">${esc(x.notes)}</p>` : ""}
      ${level() !== "text" ? `<p style="margin-top:1rem"><button class="btn primary small" type="button" data-text>Open into the text it rests on →</button>
        <a class="btn small" href="#/ask">Ask about it</a></p>` : ""}
      <h4>Connections · ${rels.length}</h4>
      ${ordered.length ? ordered.map((grp) => `
        <ul class="rel-list">${grp.items.map(({ r, other }) => `<li>
          <span class="pred">${grp.outgoing ? "" : "← "}${esc(ontology.predicates[r.p]?.label || r.p)}${grp.outgoing ? " →" : ""}</span>
          <span><span class="dot" style="--c:${kindColour(byId.get(other)?.kind)}"></span>
          ${byId.has(other) ? `<button class="link" type="button" data-c="${other}">${esc(byId.get(other).label)}</button>` : refChip(other)}
          <button class="link tiny" type="button" data-r="${r.id}" title="Show the sentence this connection rests on">why?</button></span></li>`).join("")}</ul>`).join("")
        : `<p class="empty small">No connections recorded.</p>`}
      <h4>Where it appears · ${fmt(refs.length)} passages</h4>
      <div class="meta">${x.parts.map((p) => `<span class="chip">${esc(p.replace("Part", "Part "))}</span>`).join("")}</div>
      ${level() === "text" ? `<ul class="passage-list">${refs.slice(0, 80).map((r) => `<li>${refChip(r, ` data-hl="${esc([x.label, ...x.alt].join("|"))}"`)}</li>`).join("")}</ul>${refs.length > 80 ? `<p class="tiny">and ${refs.length - 80} more.</p>` : ""}` : ""}
      ${provenance(x)}`;
    side.querySelector("[data-text]")?.addEventListener("click", () => setLevel("text"));
    bindSide();
  }

  function provenance(x) {
    const rows = [];
    if (x.signed) rows.push(`<p class="small">Reviewed by a trade marks expert on ${esc(x.signed.date)}.</p>`);
    if (x.corrected) rows.push(`<p class="small"><b>Corrected since it was reviewed</b> (${x.corrected.map(esc).join(", ")}) — a machine-written, unreviewed change made on the project owner's instruction. The labels and provisions shown are the corrected ones; the reviewed record itself is kept unchanged.</p>`);
    if (x.machine) {
      rows.push(`<p class="small">Written by <code>${esc(x.machine.by)}</code> on ${esc(x.machine.date)} · <b>${esc(x.machine.review_status)}</b>${x.machine.confidence ? ` · ${selfRated(x.machine)}` : ""}.</p>`);
      if (x.machine.reasoning) rows.push(`<p class="small muted">${esc(x.machine.reasoning)}</p>`);
      if (x.machine.check) rows.push(`<p class="small"><b>What an expert should check:</b> ${esc(x.machine.check)}</p>`);
    }
    if (x.typed) rows.push(`<p class="small">Its kind was judged by <code>${esc(x.typed.by)}</code> on ${esc(x.typed.date)} · <b>${esc(x.typed.review_status)}</b>.</p>`);
    return `<details><summary>Who wrote this record</summary>${rows.join("")}</details>`;
  }

  function bindSide() {
    side.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", () => selectConcept(b.dataset.c)));
    side.querySelectorAll("[data-r]").forEach((b) => b.addEventListener("click", () => {
      const r = relById.get(b.dataset.r);
      const li = b.closest("li");
      if (li.nextElementSibling?.classList.contains("why")) { li.nextElementSibling.remove(); return; }
      const row = el(`<li class="why" style="display:block"></li>`);
      row.appendChild(el(`<div>${relationCard(r)}</div>`));
      li.after(row);
    }));
  }

  // ------------------------------------------------------------ rail

  const toggles = root.querySelector(".toggles");
  toggles.innerHTML = ontology.kinds.map((k) => `<label><input type="checkbox" data-kind="${k.id}"><span class="dot" style="--c:${kindColour(k.id)}"></span>${esc(k.label)} <span class="tiny">${k.signed + k.machine}</span></label>`).join("");
  toggles.querySelectorAll("input").forEach((box) => box.addEventListener("change", () => {
    if (box.checked) state.expanded.add(box.dataset.kind); else state.expanded.delete(box.dataset.kind);
    state.concept = null;
    draw();
    showKind(kinds.get(box.dataset.kind));
  }));
  root.querySelectorAll(".lvl").forEach((b) => b.addEventListener("click", () => setLevel(b.dataset.level)));
  root.querySelectorAll("[data-f]").forEach((box) => box.addEventListener("change", () => { state[box.dataset.f] = box.checked; draw(); }));
  root.querySelector(".zoom").addEventListener("click", (e) => {
    const z = e.target.closest("button")?.dataset.z;
    const centre = { x: container.clientWidth / 2, y: container.clientHeight / 2 };
    if (z === "in") cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: centre });
    else if (z === "out") cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: centre });
    else cy.animate({ fit: { padding: 40 }, duration: 400 });
  });

  const fuse = new Fuse(ontology.concepts.map((x) => ({ id: x.id, label: x.label, alt: x.alt, kind: x.kind })),
    { keys: [{ name: "label", weight: 2 }, "alt"], threshold: 0.38, ignoreLocation: true });
  const find = root.querySelector(".find");
  const results = root.querySelector(".find-results");
  find.addEventListener("input", () => {
    const q = find.value.trim();
    if (q.length < 2) { results.innerHTML = ""; return; }
    const hits = fuse.search(q, { limit: 10 }).map((h) => h.item);
    results.innerHTML = hits.map((h) => `<button type="button" data-c="${h.id}"><span class="dot" style="--c:${kindColour(h.kind)}"></span>${esc(h.label)}</button>`).join("") || `<span class="tiny">No idea by that name.</span>`;
    results.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", () => selectConcept(b.dataset.c)));
  });
  find.addEventListener("keydown", (e) => { if (e.key === "Enter") results.querySelector("[data-c]")?.click(); });

  const onTheme = () => cy.style(styles());
  window.addEventListener("tmk-theme", onTheme);
  const onResize = () => cy.resize();
  window.addEventListener("resize", onResize);

  draw({ fresh: true });
  if (state.text) showConcept(byId.get(state.text));
  else if (state.concept) showConcept(byId.get(state.concept));
  else showLevelHelp();

  return () => {
    window.removeEventListener("tmk-theme", onTheme);
    window.removeEventListener("resize", onResize);
    layout?.stop();
    cy.destroy();
  };
}

function lvl(id, n, title, sub, stab) {
  return `<button class="lvl" type="button" role="tab" data-level="${id}">
    <span class="pip">${n}</span>
    <span><b>${esc(title)}</b><span>${esc(sub)}</span><span class="stab">${esc(stab)}</span></span>
  </button>`;
}

const capital = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);

function hash(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
