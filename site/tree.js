/* The examination path: a tree you open one level at a time.

   It renders whatever `src/tm_knowledge/dashboard/views.py` hands it — two
   spines, each a root with children, and one `records` map the nodes point
   into. It decides nothing about which branch a concept belongs to, and it
   cannot: every node arrives carrying the rule that put it there, and this file
   prints that rule beside the node rather than paraphrasing it.

   Everything starts closed. A tree of 130 records opened flat is a wall, and
   the first thing a reader needs is the eleven branches and how big each one
   is — which is what a closed tree shows. */

import { inline, escape } from "./md.js";

const titleCase = (value) =>
  String(value || "").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

/* Node kind -> the badge it wears. `outcome` and `prohibited` are deliberately
   loud: they are the leaf that says the system stops here. */
const KIND_TONE = {
  section: "note",
  band: "muted",
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

export function renderTree(block, context = {}) {
  const data = block.data;
  const root = document.createElement("div");
  root.className = "block viz tree-block";
  root.innerHTML = shell(data);

  const stage = root.querySelector(".tree-stage");
  const panel = root.querySelector(".viz-panel");
  const state = { spine: data.spines[0].id, filter: "all", selected: null };

  /* --------------------------------------------------------------- drawing */

  function spine() {
    return data.spines.find((entry) => entry.id === state.spine);
  }

  function keep(node) {
    if (state.filter === "all") return true;
    if (!node.origin) return true; // structural nodes always stay
    return node.origin === state.filter;
  }

  function branchRow(node, depth) {
    const children = (node.children || []).filter(keep);
    const item = document.createElement("li");
    item.className = `tree-item d-${Math.min(depth, 4)} k-${node.kind}`;

    const head = document.createElement("div");
    head.className = "tree-row";

    const hasChildren = children.length > 0;
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "tree-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.innerHTML = hasChildren ? "<span aria-hidden='true'>▸</span>" : "<span class='leafdot'></span>";
    toggle.setAttribute(
      "aria-label",
      hasChildren ? `Open ${node.label}` : `${node.label}, nothing under it`
    );

    const name = document.createElement("button");
    name.type = "button";
    name.className = "tree-name";
    const tally =
      node.count != null
        ? `${node.count} ${node.count === 1 ? "concept" : "concepts"}`
        : hasChildren
        ? `${children.length}`
        : "";
    name.innerHTML =
      `<span class="tree-label">${escape(node.label)}</span>` +
      (node.record ? `<code>${escape(node.record)}</code>` : "") +
      (node.provision ? `<code>${escape(node.provision)}</code>` : "") +
      `<span class="badge t-${KIND_TONE[node.kind] || "muted"}">${escape(
        node.kind === "band" ? "group" : titleCase(node.kind)
      )}</span>` +
      (node.origin === "authored"
        ? `<span class="badge t-warn">unreviewed</span>`
        : node.origin === "approved"
        ? `<span class="badge t-good">signed</span>`
        : "") +
      (tally ? `<span class="muted">${escape(tally)}</span>` : "") +
      (node.also_under && node.also_under.length
        ? `<span class="badge t-note">also under ${escape(
            node.also_under.length === 1
              ? node.also_under[0]
              : `${node.also_under.length} other sections`
          )}</span>`
        : "");
    name.addEventListener("click", () => open(node));

    head.append(toggle, name);
    item.appendChild(head);

    if (node.gap) {
      const gap = document.createElement("p");
      gap.className = "tree-gap";
      gap.innerHTML = inline(node.gap);
      item.appendChild(gap);
    }
    /* Why a node is on this branch is printed under it — except at the top
       level, where every row would carry the same sentence and the sentence is
       "because it is the spine". The panel still says it for every node. */
    if (node.basis && depth > 0) {
      const why = document.createElement("p");
      why.className = "tree-basis";
      why.innerHTML = `Here because ${inline(node.basis)}.`;
      item.appendChild(why);
    }
    if (node.meaning) {
      const meaning = document.createElement("p");
      meaning.className = "tree-basis";
      meaning.innerHTML = inline(node.meaning);
      item.appendChild(meaning);
    }

    if (hasChildren) {
      const list = document.createElement("ul");
      list.className = "tree-children";
      list.hidden = true;
      children.forEach((child) => list.appendChild(branchRow(child, depth + 1)));
      item.appendChild(list);
      const flip = () => {
        const open = list.hidden;
        list.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        toggle.innerHTML = `<span aria-hidden='true'>${open ? "▾" : "▸"}</span>`;
      };
      toggle.addEventListener("click", flip);
    }
    return item;
  }

  function draw() {
    const current = spine();
    stage.innerHTML = "";
    const lede = document.createElement("p");
    lede.className = "tree-lede";
    lede.innerHTML = inline(current.lede);
    stage.appendChild(lede);

    const list = document.createElement("ul");
    list.className = "tree-root";
    current.root.children.filter(keep).forEach((child) => list.appendChild(branchRow(child, 0)));
    stage.appendChild(list);
    context.decorate?.(stage);
  }

  /* --------------------------------------------------------------- detail */

  function open(node) {
    state.selected = node.id;
    const record = node.record ? data.records[node.record] : null;
    panel.innerHTML = record ? recordPanel(node, record) : structuralPanel(node);
    context.decorate?.(panel);
    panel.scrollTop = 0;
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

  function recordPanel(node, record) {
    const chips = (values, tone) =>
      values && values.length
        ? `<div class="chips">${values
            .map((value) => `<span class="chip${tone ? ` t-${tone}` : ""}">${escape(value)}</span>`)
            .join("")}</div>`
        : "";
    return (
      `<div class="panel-head"><h3>${escape(record.label)}</h3>` +
      `<p class="muted"><code>${escape(record.id)}</code> · ${escape(
        titleCase(record.group || "untyped")
      )}</p>` +
      (record.origin === "approved"
        ? `<span class="badge t-good">signed by ${escape(record.signed?.by || "—")} · ${escape(
            record.signed?.date || "—"
          )}</span>`
        : `<span class="badge t-warn">written by a machine · never reviewed</span>`) +
      `<p class="tree-basis">On this branch because ${inline(node.basis || "—")}.</p>` +
      (node.also_under && node.also_under.length
        ? `<p class="muted">Also shown under ${node.also_under
            .map((ref) => `<code>${escape(ref)}</code>`)
            .join(", ")} — it cites more than one of them.</p>`
        : "") +
      `</div>` +
      chips(record.alt, "muted") +
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

  function structuralPanel(node) {
    return (
      `<div class="panel-head"><h3>${escape(node.label)}</h3>` +
      `<p class="muted">${escape(titleCase(node.kind))}</p></div>` +
      (node.meaning ? `<p>${inline(node.meaning)}</p>` : "") +
      (node.gap ? `<div class="panel-note">${inline(node.gap)}</div>` : "") +
      (node.kind === "prohibited"
        ? `<p class="muted">An approved record. A named reviewer wrote it and it stands as ` +
          `knowledge: the system must not produce this sentence.</p>` +
          (node.notes ? `<p>${escape(node.notes)}</p>` : "")
        : "") +
      (node.children && node.children.length
        ? `<p class="muted">${node.children.length} under it. Open the row to walk them.</p>`
        : "")
    );
  }

  const emptyPanel = () =>
    `<div class="panel-empty"><p><strong>Nothing selected.</strong></p>` +
    `<p>Open a branch, then click a row to see the record behind it — the passages it rests ` +
    `on, why it is on this branch, and, where a machine wrote it, what it expects to have ` +
    `got wrong.</p></div>`;

  /* -------------------------------------------------------------- controls */

  root.querySelectorAll("[data-spine]").forEach((button) => {
    button.addEventListener("click", () => {
      state.spine = button.dataset.spine;
      root.querySelectorAll("[data-spine]").forEach((other) =>
        other.setAttribute("aria-pressed", String(other.dataset.spine === state.spine))
      );
      panel.innerHTML = emptyPanel();
      draw();
    });
  });
  root.querySelector("[data-filter]").addEventListener("change", (event) => {
    state.filter = event.target.value;
    draw();
  });
  root.querySelector("[data-openall]").addEventListener("click", () => {
    stage.querySelectorAll(".tree-children").forEach((list) => { list.hidden = false; });
    stage.querySelectorAll(".tree-toggle[aria-expanded]").forEach((toggle) => {
      if (toggle.querySelector(".leafdot")) return;
      toggle.setAttribute("aria-expanded", "true");
      toggle.innerHTML = "<span aria-hidden='true'>▾</span>";
    });
  });
  root.querySelector("[data-closeall]").addEventListener("click", () => {
    stage.querySelectorAll(".tree-children").forEach((list) => { list.hidden = true; });
    stage.querySelectorAll(".tree-toggle[aria-expanded]").forEach((toggle) => {
      if (toggle.querySelector(".leafdot")) return;
      toggle.setAttribute("aria-expanded", "false");
      toggle.innerHTML = "<span aria-hidden='true'>▸</span>";
    });
  });

  panel.innerHTML = emptyPanel();
  draw();
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

  return `
<div class="viz-controls">
  <span class="key-label">Spine:</span>
  ${tabs}
  <label class="field"><span>Who wrote it</span>
    <select data-filter>
      <option value="all">everything</option>
      <option value="approved">only what a person signed</option>
      <option value="authored">only what a machine wrote</option>
    </select>
  </label>
  <button type="button" class="pressable" data-openall>Open everything</button>
  <button type="button" class="pressable" data-closeall>Close everything</button>
</div>
<div class="viz-stage">
  <div class="tree-stage"></div>
  <aside class="viz-panel" aria-live="polite"></aside>
</div>
<details class="viz-table">
  <summary>How this tree was built — the four rules, in order</summary>
  <ol class="rules">${rules}</ol>
  <p class="note">The rules are applied in <code>src/tm_knowledge/dashboard/views.py</code> on
  every build, and the arrangement is regenerated from the records each time. Nothing here is
  stored, and nothing here has been reviewed.</p>
  ${outside ? `<h4>Fitting neither spine</h4><ul>${outside}</ul>` : ""}
</details>`;
}
