/* The map: nodes, edges, and a force layout that settles in the browser.

   It knows about `nodes`, `edges`, `groups` and `edgeKinds` — the payload
   `src/tm_knowledge/dashboard/views.py` produces — and nothing about trade
   marks. Which concepts exist, which edges are drawn and what an edge means are
   all decided in the Python; this file decides where a dot goes.

   Two rules it does keep, because they are not presentation:

   1. **Colour carries origin, never the group.** Signed and authored are the one
      distinction the whole repository is built to keep visible, so they get the
      two hues and authored nodes also get a dashed ring — colour alone is never
      the only carrier. The nine groups are a *highlight*, one at a time, with
      the group's name written on the canvas while it is on. Ten simultaneous
      hues could not be told apart by a colour-blind reader and would put the
      least important distinction on the most visible channel.
   2. **Nothing is hidden by default that changes the shape.** Filters exist, but
      the first thing a reader sees is the whole graph, isolated nodes included.

   The layout is deterministic: the same records produce the same picture on
   every load, so two people looking at "the map" are looking at one thing. */

import { inline, escape } from "./md.js";

/* Deterministic pseudo-randomness. A fixed seed is the whole point — an
   unseeded layout is a different diagram every refresh, which makes it useless
   for pointing at something in a meeting. */
const seeded = (seed) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const SVG = "http://www.w3.org/2000/svg";
const make = (name, attrs = {}) => {
  const node = document.createElementNS(SVG, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
};

/* The canvas's own units. Kept close to the width the page actually gives it,
   so the scale factor between the two is near 1 and a 9-unit label renders at
   about 9 pixels. A 1200-unit box was tried first and rendered at 540 pixels,
   which halved every label into mush. */
const WIDTH = 960;
const HEIGHT = 640;

/* Edge kind -> how it is drawn. Weight is meaning: the 35 signed relationships
   are the only edges a person put their name to, so they are the only heavy
   ones. */
const EDGE_STYLE = {
  asserted: { width: 2.4, dash: null, className: "e-asserted" },
  narrower: { width: 1.4, dash: null, className: "e-narrower" },
  related: { width: 1.2, dash: "4 4", className: "e-related" },
  cites: { width: 1.1, dash: "3 3", className: "e-cites" },
};

const titleCase = (value) =>
  String(value || "").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

export function renderNetwork(block, context = {}) {
  const data = block.data;
  const root = document.createElement("div");
  root.className = "block viz";
  root.innerHTML = shell(data);

  const canvas = root.querySelector(".viz-canvas");
  const svg = make("svg", {
    viewBox: `0 0 ${WIDTH} ${HEIGHT}`,
    role: "img",
    "aria-label":
      `A network of ${data.counts.concepts} legal concepts and ` +
      `${data.counts.provisions} provisions, joined by ${data.counts.edges} edges. ` +
      `Type in the search box above to open one, or read the table below the ` +
      `picture — it holds every concept on the canvas.`,
  });
  canvas.appendChild(svg);

  const world = make("g", { class: "world" });
  const edgeLayer = make("g", { class: "edges" });
  const nodeLayer = make("g", { class: "nodes" });
  const labelLayer = make("g", { class: "labels" });
  world.append(edgeLayer, nodeLayer, labelLayer);
  svg.appendChild(world);

  const state = {
    rollUp: false,
    showProvisions: true,
    group: null,
    selected: null,
    depth: 0, // 0 = everything, 1 or 2 = hops from the selection
    zoom: 1,
    panX: 0,
    panY: 0,
  };

  let view = null; // the derived node/edge set currently drawn

  /* ------------------------------------------------------------- deriving */

  /* Rolling subsections up is a *view*, never a change to the data: the record
     cites `TMA1995/s41(3)(a)` and goes on citing it. This merges the drawn
     nodes and says on the merged one what it stands for. */
  function derive() {
    const nodes = [];
    const byId = new Map();
    const merged = new Map(); // original provision id -> drawn id

    for (const node of data.nodes) {
      if (node.kind === "provision") {
        if (!state.showProvisions) continue;
        const id = state.rollUp ? node.root : node.id;
        merged.set(node.id, id);
        if (byId.has(id)) {
          byId.get(id).covers.push(node.id);
          continue;
        }
        const drawn = {
          ...node,
          id,
          label: state.rollUp && node.root !== node.id ? labelOf(node.root) : node.label,
          covers: [node.id],
        };
        byId.set(id, drawn);
        nodes.push(drawn);
      } else {
        byId.set(node.id, node);
        nodes.push(node);
      }
    }

    const edges = [];
    const seen = new Set();
    for (const edge of data.edges) {
      const source = merged.get(edge.source) || edge.source;
      const target = merged.get(edge.target) || edge.target;
      if (!byId.has(source) || !byId.has(target) || source === target) continue;
      const key = `${source}|${target}|${edge.kind}`;
      if (seen.has(key)) continue;
      seen.add(key);
      edges.push({ ...edge, source, target });
    }

    const neighbours = new Map(nodes.map((node) => [node.id, new Set()]));
    for (const edge of edges) {
      neighbours.get(edge.source).add(edge.target);
      neighbours.get(edge.target).add(edge.source);
    }
    return { nodes, byId, edges, neighbours };
  }

  const labelOf = (ref) => {
    const address = String(ref).split("/").slice(1).join("/");
    const lead = /^([a-z]+)(.*)$/.exec(address);
    return lead ? `${lead[1]} ${lead[2]}` : address || ref;
  };

  /* ------------------------------------------------------------- the layout */

  /* The graph is not one thing. It falls into separate islands — 44 of them at
     the time of writing, the largest holding a third of the nodes — because the
     authored half has citations and no relationships. A plain force layout
     scatters islands to the edges and reads as noise; this one lays each island
     out around its own centre and packs the centres by size, so the fragmenting
     is the first thing the picture shows rather than the thing it hides. */
  function islands(nodes, neighbours) {
    const seen = new Set();
    const found = [];
    for (const node of nodes) {
      if (seen.has(node.id)) continue;
      const members = [];
      const stack = [node.id];
      while (stack.length) {
        const id = stack.pop();
        if (seen.has(id)) continue;
        seen.add(id);
        members.push(id);
        for (const next of neighbours.get(id) || []) stack.push(next);
      }
      found.push(members);
    }
    found.sort((a, b) => b.length - a.length);
    return found;
  }

  function layout(nodes, edges, neighbours) {
    const random = seeded(20260912);
    const index = new Map(nodes.map((node) => [node.id, node]));
    const parts = islands(nodes, neighbours);
    const linksOf = new Map(parts.map((_, position) => [position, []]));
    const island = new Map();
    parts.forEach((members, position) => members.forEach((id) => island.set(id, position)));

    for (const edge of edges) {
      const a = index.get(edge.source);
      const b = index.get(edge.target);
      if (!a || !b) continue;
      const pull = 1 / Math.min(neighbours.get(a.id).size, neighbours.get(b.id).size);
      linksOf.get(island.get(a.id)).push({ a, b, kind: edge.kind, pull });
    }

    /* Each island is settled on its own, in its own coordinates. Simulating
       all 250 nodes together makes the islands push each other around the
       canvas, which spends the whole frame on empty space; packing them
       afterwards spends it on the graph. */
    const packed = parts.map((members, position) => {
      const group = members.map((id) => index.get(id));
      const links = linksOf.get(position);
      group.forEach((node, order) => {
        const theta = order * 2.399; // the golden angle — an even disc, no spokes
        const spread = 8 + Math.sqrt(group.length) * 13;
        node.x = Math.cos(theta) * spread * (0.3 + random() * 0.7);
        node.y = Math.sin(theta) * spread * (0.3 + random() * 0.7);
        node.vx = 0;
        node.vy = 0;
        node.r = radius(node);
      });

      /* The constants were tuned against the real graph, not guessed: the
         first set that looked plausible — a stronger spring and a lighter
         damping — **diverged**, and the picture it produced was a diagonal
         streak with everything else scaled to a dot. Divergence in a spring
         model is silent: the maths runs, the numbers grow, and only the
         rendering looks odd. If these are changed, check the bounding box of
         the largest island afterwards and expect it roughly square, with a
         median edge of about sixty units. */
      let alpha = 1;
      const steps = group.length > 2 ? 600 : 1;
      for (let step = 0; step < steps && alpha > 0.002; step += 1) {
        for (let i = 0; i < group.length; i += 1) {
          for (let j = i + 1; j < group.length; j += 1) {
            const a = group[i];
            const b = group[j];
            let dx = b.x - a.x;
            let dy = b.y - a.y;
            let d2 = dx * dx + dy * dy;
            if (d2 === 0) {
              dx = (random() - 0.5) * 0.1;
              dy = (random() - 0.5) * 0.1;
              d2 = 0.01;
            }
            const d = Math.sqrt(d2);
            const force = (3000 * alpha) / Math.max(d2, 100);
            const fx = (dx / d) * force;
            const fy = (dy / d) * force;
            a.vx -= fx;
            a.vy -= fy;
            b.vx += fx;
            b.vy += fy;
          }
        }
        for (const link of links) {
          const rest = link.kind === "cites" ? 44 : 34;
          const dx = link.b.x - link.a.x;
          const dy = link.b.y - link.a.y;
          const d = Math.hypot(dx, dy) || 0.01;
          const force = ((d - rest) / d) * link.pull * 0.25 * alpha;
          link.a.vx += dx * force;
          link.a.vy += dy * force;
          link.b.vx -= dx * force;
          link.b.vy -= dy * force;
        }
        for (const node of group) {
          node.vx -= node.x * 0.016 * alpha;
          node.vy -= node.y * 0.016 * alpha;
          node.x += (node.vx *= 0.75);
          node.y += (node.vy *= 0.75);
        }
        alpha *= 0.995;
      }

      let cx = 0;
      let cy = 0;
      for (const node of group) {
        cx += node.x;
        cy += node.y;
      }
      cx /= group.length;
      cy /= group.length;
      let reach = 0;
      for (const node of group) {
        node.x -= cx;
        node.y -= cy;
        reach = Math.max(reach, Math.hypot(node.x, node.y) + node.r);
      }
      return { group, reach: reach + 9 };
    });

    /* Two regions, because the graph has two populations and mixing them wastes
       the canvas on nothing. Anything joined to anything is packed into the main
       field; a node joined to nothing at all goes to a band along the bottom, in
       a grid, under a caption saying what it is. Scattering the unjoined ones
       through the field is how a picture ends up looking busy and saying
       less. */
    const clusters = packed.filter((part) => part.group.length > 1);
    const singles = packed
      .filter((part) => part.group.length === 1)
      .map((part) => part.group[0])
      .sort((a, b) => a.id.localeCompare(b.id));

    /* Shelf packing: islands in descending size, laid in rows across a target
       width and wrapped when the row is full. A spiral search was tried first
       and is what a force layout usually reaches for; with one island holding
       half the nodes it kept flinging the small ones to a radius that clears
       the big one, and the picture came out as a streak with everything else
       scaled to nothing. Rows have no such failure mode and are easier to read:
       the core, then the fragments, in order of size. */
    const gap = 26;
    const area = clusters.reduce((total, part) => total + (part.reach * 2 + gap) ** 2, 0);
    const widest = clusters.length ? clusters[0].reach * 2 : 0;
    // Biased to the frame's own aspect, so the packed block fills it rather
    // than coming out square and leaving two empty margins.
    const targetWidth = Math.max(widest, Math.sqrt((area * WIDTH) / HEIGHT) * 1.05);
    const rows = [[]];
    let penX = 0;
    for (const part of clusters.sort((a, b) => b.reach - a.reach)) {
      const size = part.reach * 2;
      if (penX > 0 && penX + size > targetWidth) {
        rows.push([]);
        penX = 0;
      }
      rows[rows.length - 1].push(part);
      penX += size + gap;
    }
    let penY = 0;
    for (const row of rows) {
      const rowWidth = row.reduce((total, part) => total + part.reach * 2 + gap, -gap);
      const rowHeight = Math.max(...row.map((part) => part.reach * 2));
      let cursor = (targetWidth - rowWidth) / 2; // rows are centred, not ragged
      for (const part of row) {
        const cx = cursor + part.reach;
        const cy = penY + rowHeight / 2;
        for (const node of part.group) {
          node.x += cx;
          node.y += cy;
        }
        cursor += part.reach * 2 + gap;
      }
      penY += rowHeight + gap;
    }

    const band = singles.length ? 118 : 0;
    fit(clusters.flatMap((part) => part.group), { top: 18, bottom: HEIGHT - band - 18 });

    if (singles.length) {
      const columns = Math.max(1, Math.ceil(singles.length / Math.ceil(singles.length / 34)));
      const gapX = (WIDTH - 60) / columns;
      const rows = Math.ceil(singles.length / columns);
      const gapY = Math.min(26, (band - 20) / Math.max(1, rows));
      singles.forEach((node, order) => {
        node.r = radius(node);
        node.x = 30 + gapX * (0.5 + (order % columns));
        node.y = HEIGHT - band + 24 + gapY * Math.floor(order / columns);
        node.unjoined = true;
      });
    }
    unjoined = singles.length;
    return parts;
  }


  /* Scale and centre whatever came out so it fills the frame. Force constants
     are a means; the picture filling the canvas is the requirement, and this
     makes the second one independent of the first. */
  function fit(nodes, box) {
    if (!nodes.length) return;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const node of nodes) {
      minX = Math.min(minX, node.x - node.r);
      maxX = Math.max(maxX, node.x + node.r);
      minY = Math.min(minY, node.y - node.r);
      maxY = Math.max(maxY, node.y + node.r);
    }
    const pad = 26;
    const top = box ? box.top : pad;
    const bottom = box ? box.bottom : HEIGHT - pad;
    const scale = Math.min(
      (WIDTH - pad * 2) / Math.max(1, maxX - minX),
      (bottom - top) / Math.max(1, maxY - minY)
    );
    const offsetX = (WIDTH - (maxX - minX) * scale) / 2 - minX * scale;
    const offsetY = top + ((bottom - top) - (maxY - minY) * scale) / 2 - minY * scale;
    for (const node of nodes) {
      node.x = node.x * scale + offsetX;
      node.y = node.y * scale + offsetY;
    }
  }
  const radius = (node) =>
    node.kind === "provision"
      ? 3.4 + Math.min(4.5, Math.sqrt(node.degree || 1) * 0.9)
      : 5 + Math.min(8, Math.sqrt(node.degree || 1) * 1.7);

  /* -------------------------------------------------------------- painting */

  let named_always = new Set();
  let unjoined = 0;

  function paint() {
    view = derive();
    const parts = layout(view.nodes, view.edges, view.neighbours);
    const note = root.querySelector(".viz-islands");
    if (note) {
      note.textContent =
        `${parts.length} separate islands are drawn. The largest holds ${parts[0].length} ` +
        `of the ${view.nodes.length} nodes; ${parts.filter((p) => p.length <= 3).length} ` +
        `hold three or fewer` +
        (unjoined
          ? `, and ${unjoined} nodes are joined to nothing at all — they are the row along the bottom.`
          : `.`);
    }
    /* Which labels are drawn when nothing is picked: the twenty best-connected
       concepts, so the canvas is legible at a glance and the choice does not
       swing on a threshold when the data moves. */
    named_always = new Set(
      view.nodes
        .filter((node) => node.kind === "concept")
        .sort((a, b) => b.degree - a.degree || a.id.localeCompare(b.id))
        .slice(0, 20)
        .map((node) => node.id)
    );
    edgeLayer.textContent = "";
    nodeLayer.textContent = "";
    labelLayer.textContent = "";

    for (const edge of view.edges) {
      const style = EDGE_STYLE[edge.kind] || EDGE_STYLE.related;
      const a = view.byId.get(edge.source);
      const b = view.byId.get(edge.target);
      const line = make("line", {
        x1: a.x, y1: a.y, x2: b.x, y2: b.y,
        class: `edge ${style.className}`,
        "stroke-width": style.width,
      });
      if (style.dash) line.setAttribute("stroke-dasharray", style.dash);
      edge.el = line;
      edgeLayer.appendChild(line);
    }

    for (const node of view.nodes) {
      /* Nodes are clickable and deliberately **not** in the tab order. Two
         hundred and fifty tab stops between the controls above and the table
         below is a trap, not access; the keyboard path to any node is the
         search box, which selects on what it matches, and the table under the
         canvas lists every one of them. */
      const circle = make("circle", {
        cx: node.x, cy: node.y, r: node.r,
        class: `node n-${node.kind} o-${node.origin}`,
        tabindex: "-1",
        "aria-hidden": "true",
      });
      circle.appendChild(make("title")).textContent =
        `${node.label} · ${node.id}${node.group ? ` · ${titleCase(node.group)}` : ""}`;
      circle.addEventListener("click", (event) => {
        event.stopPropagation();
        select(node.id);
      });
      node.el = circle;
      nodeLayer.appendChild(circle);

      const label = make("text", {
        x: node.x + node.r + 4,
        y: node.y + 4,
        class: "node-label",
      });
      label.textContent = node.label;
      node.labelEl = label;
      labelLayer.appendChild(label);
    }
    refresh();
  }

  /* What is emphasised, what is dimmed, and which labels are drawn. This is the
     whole of the progressive disclosure: the canvas always holds everything and
     decides only how loudly to say it. */
  function refresh() {
    const selected = state.selected;
    const within = new Set();
    if (selected && state.depth > 0) {
      let ring = new Set([selected]);
      within.add(selected);
      for (let hop = 0; hop < state.depth; hop += 1) {
        const next = new Set();
        for (const id of ring) {
          for (const neighbour of view.neighbours.get(id) || []) {
            if (!within.has(neighbour)) {
              within.add(neighbour);
              next.add(neighbour);
            }
          }
        }
        ring = next;
      }
    }
    const adjacent = selected ? view.neighbours.get(selected) || new Set() : new Set();

    for (const node of view.nodes) {
      const inGroup = !state.group || node.group === state.group;
      const inFocus = !selected || state.depth === 0 || within.has(node.id);
      const isSelected = node.id === selected;
      const isNeighbour = adjacent.has(node.id);
      node.el.classList.toggle("is-dim", !(inGroup && inFocus));
      node.el.classList.toggle("is-on", Boolean(state.group) && node.group === state.group);
      node.el.classList.toggle("is-selected", isSelected);
      node.el.classList.toggle("is-neighbour", isNeighbour);
      const named =
        isSelected ||
        isNeighbour ||
        (state.group && node.group === state.group) ||
        (!state.group && !selected && named_always.has(node.id)) ||
        state.zoom > 1.6;
      node.wantsLabel = Boolean(named && inGroup && inFocus);
      node.labelRank = isSelected ? 3 : isNeighbour ? 2 : node.kind === "concept" ? 1 : 0;
    }
    declutter();
    for (const edge of view.edges) {
      const ends = [view.byId.get(edge.source), view.byId.get(edge.target)];
      const dim = ends.some((end) => end.el.classList.contains("is-dim"));
      const lit = selected && (edge.source === selected || edge.target === selected);
      edge.el.classList.toggle("is-dim", Boolean(dim && !lit));
      edge.el.classList.toggle("is-lit", Boolean(lit));
    }
  }

  /* Labels are dropped, not shrunk, when they would collide. Everything scales
     with the zoom together, so two labels that overlap in the canvas's own
     units overlap at every zoom — which means this can be decided once here
     rather than re-measured per frame. Highest priority wins the spot: what is
     selected, then its neighbours, then concepts, then provisions. */
  function declutter() {
    const taken = [];
    const wanted = view.nodes
      .filter((node) => node.wantsLabel)
      .sort((a, b) => b.labelRank - a.labelRank || b.degree - a.degree || a.id.localeCompare(b.id));
    for (const node of view.nodes) node.labelEl.classList.remove("is-shown");
    for (const node of wanted) {
      const box = {
        x: node.x + node.r + 3,
        y: node.y - 5,
        w: node.label.length * 4.7 + 4,
        h: 11,
      };
      const clash = taken.some(
        (other) =>
          box.x < other.x + other.w &&
          other.x < box.x + box.w &&
          box.y < other.y + other.h &&
          other.y < box.y + box.h
      );
      if (clash) continue;
      taken.push(box);
      node.labelEl.classList.add("is-shown");
    }
  }

  /* ------------------------------------------------------------- selection */

  const panel = root.querySelector(".viz-panel");

  function select(id) {
    state.selected = state.selected === id ? null : id;
    if (!state.selected) {
      panel.innerHTML = emptyPanel();
      refresh();
      return;
    }
    const node = view.byId.get(state.selected);
    panel.innerHTML = node.kind === "provision" ? provisionPanel(node, view) : conceptPanel(node, view);
    panel.querySelectorAll("[data-goto]").forEach((button) => {
      button.addEventListener("click", () => select(button.dataset.goto));
    });
    const deeper = panel.querySelector("[data-expand]");
    if (deeper) {
      deeper.addEventListener("click", () => {
        state.depth = state.depth === 0 ? 1 : Math.min(3, state.depth + 1);
        root.querySelector("[data-depth]").value = String(state.depth);
        refresh();
      });
    }
    context.decorate?.(panel);
    refresh();
    panel.scrollTop = 0;
  }

  function neighbourList(node, current) {
    const rows = [];
    for (const edge of current.edges) {
      if (edge.source !== node.id && edge.target !== node.id) continue;
      const otherId = edge.source === node.id ? edge.target : edge.source;
      const other = current.byId.get(otherId);
      if (!other) continue;
      const kind = data.edgeKinds.find((entry) => entry.id === edge.kind);
      rows.push(
        `<li><button type="button" class="link" data-goto="${escape(otherId)}">` +
          `${escape(other.label)}</button> ` +
          `<span class="muted">${escape(kind ? kind.label : edge.kind)}` +
          (edge.record ? ` · ${escape(edge.record)}` : "") +
          (edge.modality ? ` · “${escape(edge.modality)}”` : "") +
          `</span>` +
          (edge.text ? `<p class="quote">${escape(edge.text)}</p>` : "") +
          `</li>`
      );
    }
    return rows.length
      ? `<ul class="neighbours">${rows.join("")}</ul>`
      : `<p class="muted">Nothing in either store joins this to anything else.</p>`;
  }

  const originBadge = (node) =>
    node.origin === "approved"
      ? `<span class="badge t-good">signed by ${escape(node.signed?.by || "—")} · ${escape(node.signed?.date || "—")}</span>`
      : node.origin === "authored"
      ? `<span class="badge t-warn">written by a machine · never reviewed</span>`
      : `<span class="badge t-muted">cited by a record</span>`;

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
      `<p class="muted">${escape(envelope.authored_by || "—")} · ${escape(envelope.authored_date || "—")} · ` +
      `basis <code>${escape(envelope.authoring_basis || "—")}</code>` +
      (envelope.confidence != null ? ` · confidence ${escape(envelope.confidence)}` : "") +
      ` · <strong>${escape(envelope.review_status || "unknown")}</strong></p>` +
      (envelope.reasoning ? `<p>${escape(envelope.reasoning)}</p>` : "") +
      (evidence ? `<h4>The passages it rests on</h4><ul class="evidence">${evidence}</ul>` : "") +
      (alternatives ? `<h4>Readings it rejected</h4><ul>${alternatives}</ul>` : "") +
      (envelope.expert_should_check
        ? `<h4>What it most expects to have got wrong</h4><p>${escape(envelope.expert_should_check)}</p>`
        : "") +
      `</details>`
    );
  }

  function conceptPanel(node, current) {
    const chips = (values, tone) =>
      values && values.length
        ? `<div class="chips">${values
            .map((value) => `<span class="chip${tone ? ` t-${tone}` : ""}">${escape(value)}</span>`)
            .join("")}</div>`
        : "";
    return (
      `<div class="panel-head"><h3>${escape(node.label)}</h3>` +
      `<p class="muted"><code>${escape(node.id)}</code>` +
      (node.group ? ` · ${escape(titleCase(node.group))}` : "") + `</p>` +
      originBadge(node) +
      (node.typing
        ? `<p class="muted">${escape(titleCase(node.group))} — ${escape(
            node.typing.meaning || ""
          )}. Sorted into that group by a machine (<code>${escape(
            node.typing.record || "—"
          )}</code>), which no person has checked.</p>`
        : "") +
      `</div>` +
      chips(node.alt, "muted") +
      (node.not && node.not.length
        ? `<p class="muted">Must not be confused with:</p>${chips(node.not, "gap")}`
        : "") +
      (node.provisions && node.provisions.length
        ? `<p class="muted">Legislative basis</p><div class="chips">${node.provisions
            .map((ref) => `<span class="chip mono">${escape(ref)}</span>`)
            .join("")}</div>`
        : "") +
      (node.sources && node.sources.length
        ? `<p class="muted">Meaning drawn from</p><div class="chips">${node.sources
            .map((ref) => `<span class="chip mono">${escape(ref)}</span>`)
            .join("")}</div>`
        : "") +
      (node.notes ? `<div class="panel-note">${inline(node.notes)}</div>` : "") +
      `<h4>Joined to ${node.degree} ${node.degree === 1 ? "thing" : "things"}` +
      ` <button type="button" class="link" data-expand>open its neighbourhood</button></h4>` +
      neighbourList(node, current) +
      envelopeBlock(node.authored, "Why the machine wrote this concept") +
      envelopeBlock(node.typing?.authored, "Why the machine sorted it this way")
    );
  }

  function provisionPanel(node, current) {
    const covers = node.covers && node.covers.length > 1
      ? `<p class="muted">Drawn as one node standing for ${node.covers.length} addresses: ` +
        node.covers.map((ref) => `<code>${escape(ref)}</code>`).join(", ") +
        `. The records cite them separately and still do.</p>`
      : "";
    return (
      `<div class="panel-head"><h3>${escape(node.label)}</h3>` +
      `<p class="muted"><code>${escape(node.id)}</code> · ${escape(node.instrument)}</p>` +
      originBadge(node) +
      `</div>` + covers +
      `<h4>Cited by ${node.degree} ${node.degree === 1 ? "record" : "records"}</h4>` +
      neighbourList(node, current)
    );
  }

  const emptyPanel = () =>
    `<div class="panel-empty"><p><strong>Click a node</strong> — or search for one — to read ` +
    `the record behind it.</p></div>`;

  /* --------------------------------------------------------------- controls */

  const transform = () => {
    world.setAttribute(
      "transform",
      `translate(${state.panX} ${state.panY}) scale(${state.zoom})`
    );
  };

  svg.addEventListener("wheel", (event) => {
    event.preventDefault();
    const box = svg.getBoundingClientRect();
    const px = ((event.clientX - box.left) / box.width) * WIDTH;
    const py = ((event.clientY - box.top) / box.height) * HEIGHT;
    const next = Math.min(4, Math.max(0.5, state.zoom * (event.deltaY < 0 ? 1.12 : 0.89)));
    state.panX = px - ((px - state.panX) / state.zoom) * next;
    state.panY = py - ((py - state.panY) / state.zoom) * next;
    state.zoom = next;
    transform();
    refresh();
  }, { passive: false });

  let dragging = null;
  svg.addEventListener("pointerdown", (event) => {
    dragging = { x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY };
    svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const box = svg.getBoundingClientRect();
    const scale = WIDTH / box.width;
    state.panX = dragging.panX + (event.clientX - dragging.x) * scale;
    state.panY = dragging.panY + (event.clientY - dragging.y) * scale;
    transform();
  });
  const release = () => { dragging = null; };
  svg.addEventListener("pointerup", release);
  svg.addEventListener("pointercancel", release);
  svg.addEventListener("click", (event) => {
    if (event.target === svg || event.target === world) select(null);
  });

  root.querySelector("[data-search]").addEventListener("input", (event) => {
    const term = event.target.value.trim().toLowerCase();
    if (term.length < 2) return;
    const hit =
      view.nodes.find((node) => node.label.toLowerCase() === term) ||
      view.nodes.find((node) => node.id.toLowerCase() === term) ||
      view.nodes.find((node) => node.label.toLowerCase().includes(term)) ||
      view.nodes.find((node) => (node.alt || []).some((alt) => alt.toLowerCase().includes(term)));
    if (hit && hit.id !== state.selected) select(hit.id);
  });

  root.querySelector("[data-provisions]").addEventListener("change", (event) => {
    state.showProvisions = event.target.checked;
    state.selected = null;
    panel.innerHTML = emptyPanel();
    paint();
  });
  root.querySelector("[data-rollup]").addEventListener("change", (event) => {
    state.rollUp = event.target.checked;
    state.selected = null;
    panel.innerHTML = emptyPanel();
    paint();
  });
  root.querySelector("[data-depth]").addEventListener("change", (event) => {
    state.depth = Number(event.target.value);
    refresh();
  });
  root.querySelector("[data-reset]").addEventListener("click", () => {
    state.zoom = 1;
    state.panX = 0;
    state.panY = 0;
    state.selected = null;
    state.group = null;
    state.depth = 0;
    root.querySelector("[data-depth]").value = "0";
    root.querySelector("[data-search]").value = "";
    root.querySelector(".viz-group-note").textContent = "";
    root.querySelectorAll("[data-group]").forEach((button) =>
      button.setAttribute("aria-pressed", "false")
    );
    panel.innerHTML = emptyPanel();
    transform();
    refresh();
  });
  root.querySelectorAll("[data-group]").forEach((button) => {
    button.addEventListener("click", () => {
      const value = button.dataset.group;
      state.group = state.group === value ? null : value;
      // Highlighting a kind and holding a one-step focus fight each other: the
      // focus dims most of the kind you just asked to see. The highlight wins.
      if (state.group && state.depth) {
        state.depth = 0;
        root.querySelector("[data-depth]").value = "0";
      }
      root.querySelectorAll("[data-group]").forEach((other) =>
        other.setAttribute("aria-pressed", String(other.dataset.group === state.group))
      );
      root.querySelector(".viz-group-note").textContent = state.group
        ? data.groups.find((group) => group.id === state.group)?.meaning || ""
        : "";
      refresh();
    });
  });

  panel.innerHTML = emptyPanel();
  paint();
  transform();
  return root;
}

/* ------------------------------------------------------------------ markup */

function shell(data) {
  const groups = data.groups
    .map(
      (group) =>
        `<button type="button" class="chip pressable" data-group="${escape(group.id)}" ` +
        `aria-pressed="false">${escape(group.label)}</button>`
    )
    .join("");

  const kinds = data.edgeKinds
    .map(
      (kind) =>
        `<li><span class="key-edge k-${escape(kind.id)}"></span>` +
        `<strong>${escape(kind.label)}</strong> — ${inline(kind.meaning)}</li>`
    )
    .join("");

  const rows = data.nodes
    .filter((node) => node.kind === "concept")
    .map(
      (node) =>
        `<tr><td><code>${escape(node.id)}</code></td><td>${escape(node.label)}</td>` +
        `<td>${escape(node.group ? titleCase(node.group) : "—")}</td>` +
        `<td>${node.origin === "approved" ? "signed" : "authored, unreviewed"}</td>` +
        `<td>${node.degree}</td></tr>`
    )
    .join("");

  return `
<div class="viz-controls">
  <label class="field"><span>Find</span>
    <input type="search" data-search placeholder="a label, or an id like GC-0043" list="viz-terms">
  </label>
  <datalist id="viz-terms">${data.nodes
    .map((node) => `<option value="${escape(node.label)}"></option>`)
    .join("")}</datalist>
  <label class="field"><span>Show</span>
    <select data-depth>
      <option value="0">the whole map</option>
      <option value="1">one step from what I pick</option>
      <option value="2">two steps</option>
      <option value="3">three steps</option>
    </select>
  </label>
  <label class="toggle"><input type="checkbox" data-provisions checked> Provisions</label>
  <label class="toggle"><input type="checkbox" data-rollup> Roll subsections up</label>
  <button type="button" class="pressable" data-reset>Reset the view</button>
</div>
<div class="viz-legend">
  <span class="key"><span class="key-dot o-approved"></span> signed by a person</span>
  <span class="key"><span class="key-dot o-authored"></span> written by a machine, unread</span>
  <span class="key"><span class="key-dot o-corpus"></span> a provision</span>
  <span class="key-sep"></span>
  <span class="key-label">Highlight a kind:</span>
  ${groups}
</div>
<p class="viz-group-note"></p>
<p class="viz-islands note"></p>
<div class="viz-stage">
  <div class="viz-canvas"></div>
  <aside class="viz-panel" aria-live="polite"></aside>
</div>
<details class="viz-table">
  <summary>Read this as a table instead</summary>
  <p class="note">Every concept on the canvas, with the group a machine sorted it into and
  how many things it is joined to. The picture adds no information this table lacks.</p>
  <div class="scroll"><table><thead><tr><th>ID</th><th>Label</th><th>Kind</th>
  <th>Who wrote it</th><th>Edges</th></tr></thead><tbody>${rows}</tbody></table></div>
</details>
<details class="viz-table">
  <summary>What each kind of edge means</summary>
  <ul class="key-list">${kinds}</ul>
</details>`;
}
