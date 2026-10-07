/* The examination path: a decision tree drawn as a decision tree.

   It renders whatever `src/tm_knowledge/dashboard/views.py` hands it — two
   spines, each a root with children, and one `records` map the nodes point
   into. It decides nothing about which question is asked where, and it cannot:
   every node arrives carrying the rule that put it there, and this file prints
   that rule beside the node rather than paraphrasing it.

   **Why this is a canvas and not a list.** Until now this page was an indented
   outline, and an outline cannot show the one thing a decision tree is for: that
   answering a question *here* takes you *there* and nowhere else. The grounds
   spine is now what the Python builds — a binary tree, one question per node,
   two answers per question — and it is drawn as one: a node box, two edges out,
   **yes** going right into what the section holds and **no** going down to the
   next section. The staircase down the left is the walk through the Act.

   Three things the reader can do that they could not:

   1. **Move a node.** Drag one and its whole subtree travels with it, so a
      branch can be pulled clear of the rest to be read or shown to somebody.
      *Tidy up* puts everything back.
   2. **Open one branch at a time.** Every gate starts closed on its *yes* side,
      so the first thing on screen is the eleven section questions and nothing
      else. The ± on a node opens what is under it.
   3. **Go deeper without leaving the picture.** Clicking a node fills the panel
      with the record behind it — the passage it quotes first, then its
      evidence — and every concept named in the panel is itself a button that
      opens that record. The walk down and the walk sideways are the same
      gesture.

   The layout is deterministic and computed from the node sizes the browser
   reports, so the same records draw the same tree every load. */

import { inline, escape } from "./md.js";

const titleCase = (value) =>
  String(value || "").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

/* Node kind -> the badge it wears. `outcome` is deliberately loud: it is the
   leaf that says the system stops here. */
const KIND_TONE = {
  root: "note",
  gate: "note",
  section: "note",
  step: "note",
  ground_of_refusal: "gap",
  legal_test: "note",
  relevant_factor: "muted",
  exception: "good",
  procedural_step: "note",
  process_role: "muted",
  subject_matter: "muted",
  instrument_or_record: "muted",
  external_instrument: "muted",
  none_of_these: "warn",
  residue: "warn",
  outcome: "warn",
  prohibited: "gap",
  untyped: "warn",
};

/* Geometry, in canvas units. A column is wide enough for a question of about a
   dozen words at the node's own font size; anything narrower wrapped every
   question onto five lines and made the tree twice as tall as it is wide. */
const COLUMN = 300;
const NODE_WIDTH = 236;
const ROW_GAP = 16;
/* The spine gets a wider gap than a fan does, because the word **no** is
   written on the line between two chained questions and there has to be room
   to read it. */
const CHAIN_GAP = 38;

export function renderTree(block, context = {}) {
  const data = block.data;
  const root = document.createElement("div");
  root.className = "block viz tree-block";
  root.innerHTML = shell(data);

  const canvas = root.querySelector(".dtree-canvas");
  const world = root.querySelector(".dtree-world");
  const edgeLayer = root.querySelector(".dtree-edges");
  const nodeLayer = root.querySelector(".dtree-nodes");
  const panel = root.querySelector(".viz-panel");
  const residueBox = root.querySelector(".dtree-residue");

  const state = {
    spine: data.spines[0].id,
    filter: "all",
    selected: null,
    zoom: 1,
    panX: 0,
    panY: 0,
  };

  /* Per spine, so opening a branch and switching tabs does not lose it. */
  const opened = new Map(); // spine id -> Map(node id -> boolean)
  const moved = new Map(); // spine id -> Map(node id -> {x, y})
  let laid = []; // the nodes currently drawn, with their positions

  /* The canvas is fitted once, on the first build, and never again on its own.
     Re-fitting after every expansion would move the picture under the reader
     each time they opened a branch. */
  let fitted = false;

  const spine = () => data.spines.find((entry) => entry.id === state.spine);
  const openState = () => {
    if (!opened.has(state.spine)) opened.set(state.spine, new Map());
    return opened.get(state.spine);
  };
  const offsets = () => {
    if (!moved.has(state.spine)) moved.set(state.spine, new Map());
    return moved.get(state.spine);
  };

  /* A gate's *no* branch is the spine and stays open; its *yes* branch is the
     material and starts closed. That is the whole of the default view: eleven
     questions down the left, and what each one opens still folded away. */
  const defaultOpen = (node) =>
    node.kind === "root" || (node.kind === "gate" && node.gate === "section");

  const isOpen = (node) => {
    const store = openState();
    return store.has(node.id) ? store.get(node.id) : defaultOpen(node);
  };

  const keep = (node) => {
    if (state.filter === "all") return true;
    if (!node.origin) return true; // questions and leaves are structure, always kept
    return node.origin === state.filter;
  };

  /* ------------------------------------------------------------- the layout */

  /* A tidy tree, left to right: the column is the depth, the row is worked out
     from the heights the browser reports for the boxes themselves. Laying out
     against measured heights rather than an assumed one is what stops a
     three-line question from sitting on top of the node beneath it. */
  function build() {
    nodeLayer.textContent = "";
    edgeLayer.textContent = "";
    laid = [];
    const links = [];

    /* The walk down the sections is drawn **down**, not diagonally. A gate's
       *no* is the next section, and giving it a column of its own put the
       eleven sections across eleven columns — three thousand pixels wide, and
       the reader panning sideways to follow a chain that is conceptually one
       line. Keeping it in the same column is the ordinary flowchart
       convention and it is what makes the spine legible at a glance: the
       questions run down the left, and what each one opens runs to the right. */
    const columnOf = (node, parent) => {
      if (!parent) return 0;
      if (node.answer === "no" && parent.node.gate === "section") return parent.depth;
      // The root has one child and nothing to branch between, so it starts the
      // same column rather than spending one on a single arrow.
      if (parent.node.kind === "root" && (parent.node.children || []).length === 1) {
        return parent.depth;
      }
      return parent.depth + 1;
    };

    const place = (node, depth, parent) => {
      const entry = {
        node,
        depth,
        parent,
        children: [],
        el: nodeBox(node, depth),
      };
      nodeLayer.appendChild(entry.el);
      laid.push(entry);
      if (parent) parent.children.push(entry);
      const children = (node.children || []).filter(keep);
      entry.hasChildren = children.length > 0;
      entry.open = entry.hasChildren && isOpen(node);
      if (entry.open) {
        for (const child of children) {
          const kid = place(child, columnOf(child, entry), entry);
          links.push({ from: entry, to: kid, answer: child.answer || null });
        }
      }
      return entry;
    };

    const tree = place(spine().root, 0, null);

    /* Heights come from the DOM, so this has to happen after the boxes are in
       it. Widths do not: every box is one column wide by design, because a
       tree whose columns jump around is a tree nobody can scan down. */
    for (const entry of laid) entry.height = entry.el.offsetHeight || 56;

    let cursor = 0;
    const assign = (entry) => {
      if (!entry.open || !entry.children.length) {
        entry.baseY = cursor;
        cursor += entry.height + ROW_GAP;
        return;
      }
      /* A gate whose *no* stays in this column sits level with its *yes*, the
         way a flowchart draws it — not halfway down its own subtree. Centring
         it on the midpoint floated section 43's question into the middle of the
         forty records it opens, a screen away from the line it is on.

         The chained child is laid out **after** the row has been reserved for
         the gate itself, because the gate box is taller than the single closed
         node beside it and the next section would otherwise be drawn straight
         through its bottom half. */
      const chained = entry.children.find((child) => child.depth === entry.depth);
      const rest = entry.children.filter((child) => child !== chained);
      if (chained) {
        if (rest.length) {
          rest.forEach(assign);
          const first = rest[0];
          entry.baseY = first.baseY + first.height / 2 - entry.height / 2;
        } else {
          // The root, whose single child starts the spine: it takes its own row
          // rather than the midpoint of one child, which would be its child's.
          entry.baseY = cursor;
        }
        cursor = Math.max(cursor, entry.baseY + entry.height + CHAIN_GAP);
        assign(chained);
        return;
      }
      entry.children.forEach(assign);
      const first = entry.children[0];
      const last = entry.children[entry.children.length - 1];
      entry.baseY =
        (first.baseY + first.height / 2 + last.baseY + last.height / 2) / 2 - entry.height / 2;
    };
    assign(tree);

    /* Centring a tall box on a short child can put it above the origin. One
       shift at the end keeps every coordinate positive, which is what the
       canvas size and the pan both assume. */
    const top = Math.min(...laid.map((entry) => entry.baseY));
    if (top < 0) for (const entry of laid) entry.baseY -= top;

    /* A node that has been dragged carries its subtree with it: the offset is
       inherited, so a branch pulled clear stays a branch. */
    const drift = offsets();
    const settle = (entry, dx, dy) => {
      const own = drift.get(entry.node.id);
      const x = dx + (own ? own.x : 0);
      const y = dy + (own ? own.y : 0);
      entry.x = entry.depth * COLUMN + x;
      entry.y = entry.baseY + y;
      entry.el.style.transform = `translate(${entry.x}px, ${entry.y}px)`;
      for (const child of entry.children) settle(child, x, y);
    };
    settle(tree, 0, 0);

    let width = 0;
    let height = 0;
    for (const entry of laid) {
      width = Math.max(width, entry.x + NODE_WIDTH);
      height = Math.max(height, entry.y + entry.height);
    }
    world.style.width = `${width + 40}px`;
    world.style.height = `${height + 40}px`;
    edgeLayer.setAttribute("viewBox", `0 0 ${width + 40} ${height + 40}`);
    edgeLayer.setAttribute("width", width + 40);
    edgeLayer.setAttribute("height", height + 40);

    for (const link of links) drawEdge(link);
    // Only counts as fitted once the canvas actually had a size to fit to: the
    // block is built detached and measures zero until it is in the document.
    if (!fitted) fitted = fitToFrame();
    root.querySelector(".dtree-count").textContent =
      `${laid.length} of the spine's nodes are open. ` +
      (state.filter === "all" ? "" : "A filter is on, so some are hidden. ");
    context.decorate?.(nodeLayer);
    paintSelection();
  }

  function drawEdge({ from, to, answer }) {
    const sameColumn = Math.abs(to.x - from.x) < 1;
    const x1 = sameColumn ? from.x + NODE_WIDTH / 2 : from.x + NODE_WIDTH;
    const y1 = sameColumn ? from.y + from.height : from.y + from.height / 2;
    const x2 = sameColumn ? to.x + NODE_WIDTH / 2 : to.x;
    const y2 = to.y + (sameColumn ? 0 : to.height / 2);
    const mid = (x1 + x2) / 2;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
      "d",
      sameColumn
        ? `M ${x1} ${y1} L ${x2} ${y2}`
        : `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`
    );
    path.setAttribute("class", `dtree-edge${answer ? ` a-${answer}` : ""}`);
    edgeLayer.appendChild(path);
    if (!answer) return;
    /* The word on the edge is the whole grammar of the picture: without it a
       reader cannot tell which way is which, and the two branches of a
       question are not interchangeable. */
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", sameColumn ? x1 + 12 : mid);
    label.setAttribute("y", sameColumn ? (y1 + y2) / 2 + 3 : (y1 + y2) / 2 - 4);
    if (sameColumn) label.setAttribute("text-anchor", "start");
    label.setAttribute("class", `dtree-answer a-${answer}`);
    label.setAttribute("text-anchor", "middle");
    label.textContent = answer;
    edgeLayer.appendChild(label);
  }

  /* --------------------------------------------------------------- the boxes */

  function nodeBox(node, depth) {
    const box = document.createElement("div");
    box.className = `dtree-node n-${node.kind}${node.gate ? ` g-${node.gate}` : ""}`;
    box.dataset.id = node.id;
    box.style.width = `${NODE_WIDTH}px`;

    const children = (node.children || []).filter(keep);
    const record = node.record ? data.records[node.record] : null;

    const head = document.createElement("div");
    head.className = "dtree-head";

    if (children.length) {
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "dtree-toggle";
      const open = isOpen(node);
      toggle.textContent = open ? "−" : "+";
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute(
        "aria-label",
        `${open ? "Close" : "Open"} what follows ${node.question || node.label}`
      );
      toggle.addEventListener("click", (event) => {
        event.stopPropagation();
        openState().set(node.id, !isOpen(node));
        build();
      });
      head.appendChild(toggle);
    }

    const title = document.createElement("div");
    title.className = "dtree-title";
    title.innerHTML =
      (node.position
        ? `<span class="dtree-step">${node.position} of ${node.of}</span>`
        : "") +
      `<span class="dtree-question">${escape(node.question || node.label)}</span>`;
    head.appendChild(title);
    box.appendChild(head);

    const marks = [];
    if (node.provision) marks.push(`<code>${escape(node.provision)}</code>`);
    if (node.record) marks.push(`<code>${escape(node.record)}</code>`);
    if (node.origin === "authored")
      marks.push(`<span class="badge t-warn">unreviewed</span>`);
    else if (node.origin === "approved")
      marks.push(`<span class="badge t-good">signed</span>`);
    if (node.kind === "outcome")
      marks.push(`<span class="badge t-warn">the system stops here</span>`);
    if (marks.length) {
      const meta = document.createElement("div");
      meta.className = "dtree-meta";
      meta.innerHTML = marks.join("");
      box.appendChild(meta);
    }

    /* The concrete line. A label and a group name told a reader nothing they
       did not already know; the corpus's own sentence tells them what the
       question is actually about. */
    const quote = record?.quote || null;
    if (quote) {
      const line = document.createElement("p");
      line.className = "dtree-quote";
      line.innerHTML = `“${escape(clip(quote.text, 96))}”<span class="dtree-ref">${escape(
        quote.ref
      )}</span>`;
      box.appendChild(line);
    }
    /* The outcome leaf stays one line on the canvas. It is drawn thirty-two
       times — once at the end of every path — and repeating the paragraph that
       explains it at each one tripled the height of the tree to say the same
       sentence over and over. The paragraph is in the panel, once. */

    const tallies = [];
    if (node.considerations?.length)
      tallies.push(
        `${node.considerations.length} ${
          node.considerations.length === 1 ? "record" : "records"
        } to read here`
      );
    if (node.count != null && node.kind !== "gate") tallies.push(`${node.count} attached`);
    if (node.kind === "gate" && node.gate === "section") {
      const parts = [];
      if (node.tests) parts.push(`${node.tests} question${node.tests === 1 ? "" : "s"}`);
      if (node.factors) parts.push(`${node.factors} factor${node.factors === 1 ? "" : "s"}`);
      if (node.exceptions)
        parts.push(`${node.exceptions} exception${node.exceptions === 1 ? "" : "s"}`);
      if (parts.length) tallies.push(parts.join(" · "));
    }
    if (tallies.length) {
      const tally = document.createElement("p");
      tally.className = "dtree-tally";
      tally.textContent = tallies.join(" · ");
      box.appendChild(tally);
    }

    if (node.gap) {
      const gap = document.createElement("p");
      gap.className = "dtree-gapmark";
      gap.textContent = "No record names the ground this asks about";
      box.appendChild(gap);
    }

    if (children.length && !isOpen(node)) {
      const folded = document.createElement("p");
      folded.className = "dtree-folded";
      folded.textContent =
        node.kind === "gate"
          ? `${countUnder(node)} nodes folded away — open it`
          : `${children.length} under it`;
      box.appendChild(folded);
    }

    box.addEventListener("click", () => select(node));
    draggable(box, node);
    return box;
  }

  const countUnder = (node) => {
    let total = 0;
    for (const child of (node.children || []).filter(keep)) total += 1 + countUnder(child);
    return total;
  };

  const clip = (text, limit) => {
    const value = String(text || "").trim();
    if (value.length <= limit) return value;
    return `${value.slice(0, limit).replace(/\s+\S*$/, "")}…`;
  };

  /* ------------------------------------------------------------- the dragging */

  function draggable(box, node) {
    let drag = null;
    box.addEventListener("pointerdown", (event) => {
      if (event.target.closest("button") && event.target !== box) return;
      const entry = laid.find((item) => item.node.id === node.id);
      if (!entry) return;
      const own = offsets().get(node.id) || { x: 0, y: 0 };
      drag = {
        id: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        from: { ...own },
        moved: false,
      };
      box.setPointerCapture(event.pointerId);
      event.stopPropagation();
    });
    box.addEventListener("pointermove", (event) => {
      if (!drag) return;
      const dx = (event.clientX - drag.x) / state.zoom;
      const dy = (event.clientY - drag.y) / state.zoom;
      if (!drag.moved && Math.hypot(dx, dy) < 3) return;
      drag.moved = true;
      box.classList.add("is-dragging");
      offsets().set(node.id, { x: drag.from.x + dx, y: drag.from.y + dy });
      reposition();
    });
    const end = (event) => {
      if (!drag) return;
      box.classList.remove("is-dragging");
      /* A drag is not a click. Without this the node you just moved also opens
         in the panel, which is the one thing a reader positioning a branch
         does not want. */
      if (drag.moved) box.dataset.suppressClick = "1";
      drag = null;
      if (box.hasPointerCapture?.(event.pointerId)) box.releasePointerCapture(event.pointerId);
    };
    box.addEventListener("pointerup", end);
    box.addEventListener("pointercancel", end);
    box.addEventListener(
      "click",
      (event) => {
        if (box.dataset.suppressClick) {
          delete box.dataset.suppressClick;
          event.stopPropagation();
        }
      },
      true
    );
  }

  /* Moving a node moves its subtree, and only the geometry changes — no box is
     rebuilt and no state is touched, so a drag stays smooth on the largest
     branch. */
  function reposition() {
    const drift = offsets();
    const tree = laid[0];
    if (!tree) return;
    const walk = (entry, dx, dy) => {
      const own = drift.get(entry.node.id);
      const x = dx + (own ? own.x : 0);
      const y = dy + (own ? own.y : 0);
      entry.x = entry.depth * COLUMN + x;
      entry.y = entry.baseY + y;
      entry.el.style.transform = `translate(${entry.x}px, ${entry.y}px)`;
      for (const child of entry.children) walk(child, x, y);
    };
    walk(tree, 0, 0);
    edgeLayer.textContent = "";
    for (const entry of laid) {
      for (const child of entry.children) {
        drawEdge({ from: entry, to: child, answer: child.node.answer || null });
      }
    }
  }

  /* ------------------------------------------------------------- the panel */

  function select(node) {
    state.selected = node.id;
    const record = node.record ? data.records[node.record] : null;
    panel.innerHTML = record ? recordPanel(node, record) : structuralPanel(node);
    wirePanel();
    paintSelection();
    panel.scrollTop = 0;
  }

  function openRecord(id, fromLabel) {
    const record = data.records[id];
    if (!record) return;
    panel.innerHTML =
      (fromLabel
        ? `<p class="muted"><button type="button" class="link" data-back>← back to ${escape(
            fromLabel
          )}</button></p>`
        : "") + recordPanel({ record: id, basis: null }, record);
    wirePanel();
    panel.scrollTop = 0;
  }

  let lastNode = null;
  function wirePanel() {
    panel.querySelectorAll("[data-open]").forEach((button) => {
      button.addEventListener("click", () => {
        const current = laid.find((entry) => entry.node.id === state.selected);
        lastNode = current ? current.node : lastNode;
        openRecord(button.dataset.open, lastNode?.question || lastNode?.label || null);
      });
    });
    panel.querySelector("[data-back]")?.addEventListener("click", () => {
      if (lastNode) select(lastNode);
    });
    context.decorate?.(panel);
  }

  function paintSelection() {
    nodeLayer.querySelectorAll(".dtree-node").forEach((box) => {
      box.classList.toggle("is-selected", box.dataset.id === state.selected);
    });
  }

  function envelopeBlock(envelope, heading) {
    if (!envelope) return "";
    const evidence = (envelope.evidence || [])
      .map(
        (item) =>
          `<li><code>${escape(item.ref)}</code><p class="quote">${escape(item.quote || "")}</p></li>`
      )
      .join("");
    const alternatives = (envelope.alternatives_considered || [])
      .map((item) => `<li>${escape(item)}</li>`)
      .join("");
    return (
      `<details class="deep"><summary>${escape(heading)}</summary>` +
      `<p class="muted">${escape(envelope.authored_by || "—")} · ${escape(
        envelope.authored_date || "—"
      )} · basis <code>${escape(envelope.authoring_basis || "—")}</code>` +
      (envelope.confidence != null ? ` · confidence ${escape(envelope.confidence)}` : "") +
      ` · <strong>${escape(envelope.review_status || "unknown")}</strong></p>` +
      (envelope.reasoning ? `<p>${escape(envelope.reasoning)}</p>` : "") +
      (evidence ? `<h4>The passages it rests on</h4><ul class="evidence">${evidence}</ul>` : "") +
      (alternatives ? `<h4>Readings it rejected</h4><ul>${alternatives}</ul>` : "") +
      (envelope.expert_should_check
        ? `<h4>What it most expects to have got wrong</h4><p>${escape(
            envelope.expert_should_check
          )}</p>`
        : "") +
      `</details>`
    );
  }

  const chips = (values, tone) =>
    values && values.length
      ? `<div class="chips">${values
          .map((value) => `<span class="chip${tone ? ` t-${tone}` : ""}">${escape(value)}</span>`)
          .join("")}</div>`
      : "";

  /* The passage first, then who wrote the record, then everything else. A
     reader opening a node wants to know what the Manual actually says before
     they want the provenance of the record that quotes it. */
  function quoteBlock(record) {
    if (!record.quote) return "";
    return (
      `<blockquote class="panel-quote">${escape(record.quote.text)}` +
      `<cite><code>${escape(record.quote.ref)}</code> — ${escape(record.quote.from)}</cite>` +
      `</blockquote>`
    );
  }

  function recordPanel(node, record) {
    return (
      `<div class="panel-head"><h3>${escape(record.label)}</h3>` +
      `<p class="muted"><code>${escape(record.id)}</code> · ${escape(
        titleCase(record.group || "untyped")
      )}${record.typing?.meaning ? ` — ${escape(record.typing.meaning)}` : ""}</p>` +
      (record.origin === "approved"
        ? `<span class="badge t-good">signed by ${escape(record.signed?.by || "—")} · ${escape(
            record.signed?.date || "—"
          )}</span>`
        : `<span class="badge t-warn">written by a machine · never reviewed</span>`) +
      (node.basis
        ? `<p class="tree-basis">On this path because ${inline(node.basis)}.</p>`
        : "") +
      (node.also_under && node.also_under.length
        ? `<p class="muted">The same question is asked under ${node.also_under
            .map((ref) => `<code>${escape(ref)}</code>`)
            .join(", ")} — its record cites more than one section.</p>`
        : "") +
      `</div>` +
      quoteBlock(record) +
      chips(record.alt, "muted") +
      (record.not && record.not.length
        ? `<p class="muted">Must not be confused with:</p>${chips(record.not, "gap")}`
        : "") +
      considerationList(node) +
      (record.provisions && record.provisions.length
        ? `<p class="muted">Legislative basis</p><div class="chips">${record.provisions
            .map((ref) => `<span class="chip mono">${escape(ref)}</span>`)
            .join("")}</div>`
        : "") +
      (record.sources && record.sources.length
        ? `<p class="muted">Meaning drawn from</p><div class="chips">${record.sources
            .map((ref) => `<span class="chip mono">${escape(ref)}</span>`)
            .join("")}</div>`
        : "") +
      (record.notes ? `<div class="panel-note">${inline(record.notes)}</div>` : "") +
      envelopeBlock(record.authored, "Why the machine wrote this concept") +
      envelopeBlock(record.typing?.authored, "Why the machine sorted it this way")
    );
  }

  /* What to read at a gate. Each one opens in this same panel, which is how a
     reader gets from a question to the 32 factors under it and back without
     losing the tree. */
  function considerationList(node) {
    const items = node.considerations || node.children || [];
    const usable = items.filter((item) => item.record && data.records[item.record]);
    if (!usable.length) return "";
    const byGroup = new Map();
    for (const item of usable) {
      const group = item.group || item.kind || "other";
      if (!byGroup.has(group)) byGroup.set(group, []);
      byGroup.get(group).push(item);
    }
    let html = `<h4>What the records put here</h4>`;
    for (const [group, members] of byGroup) {
      html +=
        `<p class="muted t-${KIND_TONE[group] || "muted"}">${escape(titleCase(group))} · ${
          members.length
        }</p><ul class="neighbours">` +
        members
          .map((item) => {
            const record = data.records[item.record];
            return (
              `<li><button type="button" class="link" data-open="${escape(item.record)}">` +
              `${escape(record.label)}</button> ` +
              `<span class="badge ${
                record.origin === "approved" ? "t-good" : "t-warn"
              }">${record.origin === "approved" ? "signed" : "unreviewed"}</span>` +
              (record.quote
                ? `<p class="quote">${escape(clip(record.quote.text, 150))}</p>`
                : "") +
              `</li>`
            );
          })
          .join("") +
        `</ul>`;
    }
    return html;
  }

  function structuralPanel(node) {
    if (node.kind === "outcome") {
      return (
        `<div class="panel-head"><h3>${escape(node.label)}</h3>` +
        `<p class="muted">The leaf every path ends on</p></div>` +
        `<p>${escape(data.outcome.meaning)}</p>` +
        `<h4>The signed records that say so</h4><ul class="neighbours">` +
        data.outcome.records
          .map(
            (record) =>
              `<li><strong>${escape(record.label)}</strong> <code>${escape(record.id)}</code>` +
              (record.notes ? `<p class="quote">${escape(record.notes)}</p>` : "") +
              `<span class="badge t-good">signed by ${escape(
                record.signed?.by || "—"
              )}</span></li>`
          )
          .join("") +
        `</ul>`
      );
    }
    return (
      `<div class="panel-head"><h3>${escape(node.question || node.label)}</h3>` +
      `<p class="muted">${escape(
        node.gate ? `${titleCase(node.gate)} question` : titleCase(node.kind)
      )}${node.provision ? ` · ${escape(node.provision)}` : ""}</p></div>` +
      (node.meaning ? `<p>${inline(node.meaning)}</p>` : "") +
      (node.note ? `<p class="muted">${inline(node.note)}</p>` : "") +
      (node.gap ? `<div class="panel-note t-gap">${inline(node.gap)}</div>` : "") +
      considerationList(node) +
      (node.children && node.children.length
        ? `<p class="muted">Answering this takes the walk one of two ways. Open the node to ` +
          `see both.</p>`
        : "")
    );
  }

  const emptyPanel = () =>
    `<div class="panel-empty"><p><strong>Nothing selected.</strong></p>` +
    `<p>Click a question to see the records behind it — the passage each one quotes, why it ` +
    `is on this path, and, where a machine wrote it, what it expects to have got wrong. ` +
    `Drag a node to move its branch; use <strong>+</strong> to open what is under it.</p></div>`;

  /* ------------------------------------------------------ pan, zoom, controls */

  const transform = () => {
    world.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
  };

  canvas.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      const box = canvas.getBoundingClientRect();
      const px = event.clientX - box.left;
      const py = event.clientY - box.top;
      const next = Math.min(2.2, Math.max(0.25, state.zoom * (event.deltaY < 0 ? 1.1 : 0.91)));
      state.panX = px - ((px - state.panX) / state.zoom) * next;
      state.panY = py - ((py - state.panY) / state.zoom) * next;
      state.zoom = next;
      transform();
    },
    { passive: false }
  );

  let pan = null;
  canvas.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".dtree-node")) return;
    pan = { x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY };
    canvas.setPointerCapture(event.pointerId);
    canvas.classList.add("is-panning");
  });
  canvas.addEventListener("pointermove", (event) => {
    if (!pan) return;
    state.panX = pan.panX + (event.clientX - pan.x);
    state.panY = pan.panY + (event.clientY - pan.y);
    transform();
  });
  const stopPan = () => {
    pan = null;
    canvas.classList.remove("is-panning");
  };
  canvas.addEventListener("pointerup", stopPan);
  canvas.addEventListener("pointercancel", stopPan);

  function drawResidue() {
    const current = spine();
    const residue = current.residue;
    if (!residue) {
      residueBox.hidden = true;
      return;
    }
    residueBox.hidden = false;
    residueBox.innerHTML =
      `<h4>${escape(residue.label)} — ${residue.count}</h4>` +
      `<p>${inline(residue.gap)}</p>` +
      `<ul class="neighbours">` +
      residue.children
        .map(
          (item) =>
            `<li><button type="button" class="link" data-open="${escape(item.record)}">` +
            `${escape(item.label)}</button> <code>${escape(item.record)}</code> ` +
            `<span class="badge ${
              item.origin === "approved" ? "t-good" : "t-warn"
            }">${item.origin === "approved" ? "signed" : "unreviewed"}</span></li>`
        )
        .join("") +
      `</ul>`;
    residueBox.querySelectorAll("[data-open]").forEach((button) => {
      button.addEventListener("click", () => {
        lastNode = null;
        openRecord(button.dataset.open, null);
        panel.scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    });
  }

  function redraw() {
    build();
    drawResidue();
  }

  root.querySelectorAll("[data-spine]").forEach((button) => {
    button.addEventListener("click", () => {
      state.spine = button.dataset.spine;
      root.querySelectorAll("[data-spine]").forEach((other) =>
        other.setAttribute("aria-pressed", String(other.dataset.spine === state.spine))
      );
      root.querySelector(".dtree-lede").innerHTML = inline(spine().lede);
      state.selected = null;
      state.panX = 0;
      state.panY = 0;
      state.zoom = 1;
      transform();
      panel.innerHTML = emptyPanel();
      redraw();
    });
  });
  root.querySelector("[data-filter]").addEventListener("change", (event) => {
    state.filter = event.target.value;
    redraw();
  });
  root.querySelector("[data-openall]").addEventListener("click", () => {
    const store = openState();
    const walk = (node) => {
      if ((node.children || []).length) store.set(node.id, true);
      for (const child of node.children || []) walk(child);
    };
    walk(spine().root);
    redraw();
  });
  root.querySelector("[data-closeall]").addEventListener("click", () => {
    const store = openState();
    const walk = (node) => {
      store.set(node.id, node.kind === "root");
      for (const child of node.children || []) walk(child);
    };
    walk(spine().root);
    redraw();
  });
  root.querySelector("[data-tidy]").addEventListener("click", () => {
    offsets().clear();
    state.panX = 0;
    state.panY = 0;
    state.zoom = 1;
    transform();
    redraw();
  });
  function fitToFrame() {
    const width = parseFloat(world.style.width) || 1;
    const height = parseFloat(world.style.height) || 1;
    const box = canvas.getBoundingClientRect();
    if (!box.width) return false;
    /* Never below 0.45: past that the questions stop being readable and the
       picture is a diagram of a diagram. Below it the reader pans instead,
       which is the honest trade. */
    state.zoom = Math.max(
      0.6,
      Math.min(1, Math.min((box.width - 24) / width, (box.height - 24) / height))
    );
    state.panX = 12;
    state.panY = 12;
    transform();
    return true;
  }
  root.querySelector("[data-fit]").addEventListener("click", fitToFrame);

  /* Jumping to a section opens its branch and brings it to the top of the
     canvas: on a spine seventeen questions deep, scrolling to section 44 by
     hand is a chore nobody should have to do twice. */
  root.querySelector("[data-jump]")?.addEventListener("change", (event) => {
    const id = event.target.value;
    if (!id) return;
    const store = openState();
    const path = [];
    const find = (node, trail) => {
      if (node.id === id) {
        path.push(...trail, node);
        return true;
      }
      return (node.children || []).some((child) => find(child, [...trail, node]));
    };
    find(spine().root, []);
    for (const node of path) if ((node.children || []).length) store.set(node.id, true);
    build();
    const entry = laid.find((item) => item.node.id === id);
    if (entry) {
      state.panX = 40 - entry.x * state.zoom;
      state.panY = 40 - entry.y * state.zoom;
      transform();
      select(entry.node);
    }
  });

  panel.innerHTML = emptyPanel();
  redraw();
  transform();
  /* The block is built detached and appended by the router, so at build time
     the canvas measures zero and there is nothing to fit to. One frame later
     there is. */
  requestAnimationFrame(() => {
    if (fitted) return;
    /* Built once more now that the canvas is in the document. Every box
       measured zero while it was detached, so the first pass laid the tree out
       against a guessed height and the rows overlapped. */
    fitted = false;
    build();
  });
  return root;
}

/* ------------------------------------------------------------------ markup */

function shell(data) {
  const tabs = data.spines
    .map(
      (entry, index) =>
        `<button type="button" class="pressable" data-spine="${escape(entry.id)}" ` +
        `aria-pressed="${index === 0}">${escape(entry.label)}</button>`
    )
    .join("");
  const rules = data.rules.map((rule) => `<li>${inline(rule)}</li>`).join("");
  const outside = data.outside
    .map(
      (item) =>
        `<li><strong>${escape(item.label)}</strong> <code>${escape(item.id)}</code> — ` +
        `${escape(item.notes || "")}</li>`
    )
    .join("");

  const sections = (data.spines[0].root.children || []).length
    ? gates(data.spines[0].root)
        .map(
          (node) =>
            `<option value="${escape(node.id)}">${escape(node.label || node.question)}</option>`
        )
        .join("")
    : "";

  return `
<div class="viz-controls">
  <span class="key-label">Spine:</span>
  ${tabs}
  <label class="field"><span>Jump to</span>
    <select data-jump><option value="">a section…</option>${sections}</select>
  </label>
  <label class="field"><span>Who wrote it</span>
    <select data-filter>
      <option value="all">everything</option>
      <option value="approved">only what a person signed</option>
      <option value="authored">only what a machine wrote</option>
    </select>
  </label>
  <button type="button" class="pressable" data-openall>Open everything</button>
  <button type="button" class="pressable" data-closeall>Close everything</button>
  <button type="button" class="pressable" data-fit>Fit to the frame</button>
  <button type="button" class="pressable" data-tidy>Tidy up</button>
</div>
<p class="dtree-lede tree-lede">${inline(data.spines[0].lede)}</p>
<div class="dtree-stage">
  <div class="dtree-canvas">
    <div class="dtree-world">
      <svg class="dtree-edges" aria-hidden="true"></svg>
      <div class="dtree-nodes"></div>
    </div>
  </div>
  <aside class="viz-panel" aria-live="polite"></aside>
</div>
<p class="dtree-hint">Drag the background to pan · scroll to zoom · drag a node to move it and
everything under it · <strong>+</strong> opens a branch, clicking a question opens its
records</p>
<p class="dtree-count note"></p>
<div class="dtree-residue callout c-gap"></div>
<details class="viz-table">
  <summary>How this tree was built — the rules, in order</summary>
  <ol class="rules">${rules}</ol>
  <p class="note">The rules are applied in <code>src/tm_knowledge/dashboard/views.py</code> on
  every build, and the arrangement is regenerated from the records each time. Nothing here is
  stored, and nothing here has been reviewed.</p>
  ${outside ? `<h4>Fitting neither spine</h4><ul>${outside}</ul>` : ""}
</details>`;
}

/* Every section gate on the spine, in the order the walk reaches them. They are
   nested one inside the next — each *no* branch holds the rest of the walk — so
   this is a descent and not a list of children. */
function gates(root) {
  const found = [];
  const walk = (node) => {
    if (node.kind === "gate" && node.gate === "section") found.push(node);
    for (const child of node.children || []) walk(child);
  };
  walk(root);
  return found;
}
