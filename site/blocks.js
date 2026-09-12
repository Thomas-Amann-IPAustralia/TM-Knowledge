/* One renderer per block kind, and nothing else.

   These functions know about `stats`, `prose`, `callout`, `table`, `cards`,
   `bars`, `list`, `report`, `network` and `tree` — the vocabulary in
   `src/tm_knowledge/dashboard/blocks.py` — and nothing about section 43, the
   ontology or the review process. Changing what the dashboard *says* is a
   change to the Python. Changing how a kind *looks* is a change here. Adding an
   eleventh kind is the only thing that needs both.

   The last two are big enough to own a file each. They are still renderers of a
   block and nothing more: the arrangement they draw is computed in
   `views.py`, and neither file decides what belongs where. */

import { render, inline, escape } from "./md.js";
import { renderNetwork } from "./network.js";
import { renderTree } from "./tree.js";

const el = (html) => {
  const wrap = document.createElement("div");
  wrap.innerHTML = html;
  return wrap.firstElementChild;
};

const tone = (value) => (value ? ` t-${value}` : "");

const links = (items = []) =>
  items.length
    ? `<div class="links">${items
        .map((link) => `<a href="${escape(link.href)}">${escape(link.label)} →</a>`)
        .join("")}</div>`
    : "";

const note = (text) => (text ? `<p class="note">${inline(text)}</p>` : "");

/* A table cell is a markdown-lite string, or `{chips: [...]}`. */
function cell(value) {
  if (value && typeof value === "object" && Array.isArray(value.chips)) {
    return `<div class="chips">${value.chips
      .map((chip) => `<span class="chip${tone(chip.tone)}">${escape(chip.label)}</span>`)
      .join("")}</div>`;
  }
  return inline(value == null ? "—" : String(value));
}

const renderers = {
  stats(block) {
    const items = block.items
      .map((item) => {
        const body =
          `<span class="value">${escape(
            typeof item.value === "number" ? item.value.toLocaleString("en-AU") : item.value
          )}</span>` +
          `<span class="label">${inline(item.label)}</span>` +
          (item.note ? `<span class="sub">${inline(item.note)}</span>` : "");
        return item.href
          ? `<a class="stat${tone(item.tone)}" href="${escape(item.href)}">${body}</a>`
          : `<div class="stat${tone(item.tone)}">${body}</div>`;
      })
      .join("");
    return el(`<div class="block"><div class="stats">${items}</div>${note(block.note)}</div>`);
  },

  prose(block) {
    return el(`<div class="block prose">${render(block.text)}</div>`);
  },

  callout(block) {
    return el(
      `<div class="block"><div class="callout c-${escape(block.tone || "note")}">` +
        `<h3>${inline(block.title)}</h3>` +
        `<div class="prose">${render(block.text)}</div>` +
        links(block.links) +
        `</div></div>`
    );
  },

  list(block) {
    const tag = block.ordered ? "ol" : "ul";
    return el(
      `<div class="block prose"><${tag}>${block.items
        .map((item) => `<li>${inline(item)}</li>`)
        .join("")}</${tag}>${note(block.note)}</div>`
    );
  },

  bars(block) {
    const top = Math.max(1, ...block.items.map((item) => item.value));
    return el(
      `<div class="block"><div class="bars">${block.items
        .map(
          (item) =>
            `<div class="bar"><span>${inline(item.label)}</span>` +
            `<span class="track"><span class="fill" style="width:${(item.value / top) * 100}%"></span></span>` +
            `<span class="num">${escape(item.value)}</span></div>`
        )
        .join("")}</div>${note(block.note)}</div>`
    );
  },

  cards(block) {
    return el(
      `<div class="block"><div class="cards">${block.items
        .map(
          (item) =>
            `<div class="card"><h3>${inline(item.title)}</h3>` +
            (item.subtitle ? `<div class="sub">${inline(item.subtitle)}</div>` : "") +
            `<div class="prose">${render(item.text || "")}</div>` +
            (item.badges && item.badges.length
              ? `<div class="chips">${item.badges
                  .filter(Boolean)
                  .map((badge) => `<span class="chip${tone(badge.tone)}">${escape(badge.label)}</span>`)
                  .join("")}</div>`
              : "") +
            links(item.links) +
            `</div>`
        )
        .join("")}</div>${note(block.note)}</div>`
    );
  },

  table(block, context = {}) {
    const node = el(`<div class="block"><div class="tablewrap"></div>${note(block.note)}</div>`);
    const wrap = node.querySelector(".tablewrap");

    if (block.search) {
      wrap.appendChild(
        el(
          `<div class="tabletop">` +
            `<input type="search" placeholder="Filter ${block.rows.length} rows…" aria-label="Filter this table">` +
            `<span class="count"></span></div>`
        )
      );
    }

    const scroll = el('<div class="scroll"><table></table></div>');
    const table = scroll.querySelector("table");
    table.innerHTML =
      `<thead><tr>${block.columns.map((column) => `<th>${escape(column.label)}</th>`).join("")}</tr></thead>` +
      "<tbody></tbody>";
    const body = table.querySelector("tbody");
    wrap.appendChild(scroll);

    const rows = block.rows.map((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = block.columns.map((column) => `<td>${cell(row[column.key])}</td>`).join("");
      const detail = (row.detail || []).filter(Boolean);
      let panel = null;

      if (detail.length) {
        tr.className = "has-detail";
        tr.tabIndex = 0;
        tr.setAttribute("role", "button");
        tr.setAttribute("aria-expanded", "false");
        panel = document.createElement("tr");
        panel.className = "detail";
        panel.hidden = true;
        const td = document.createElement("td");
        td.colSpan = block.columns.length;
        detail.forEach((child) => td.appendChild(renderBlock(child, context)));
        panel.appendChild(td);

        const toggle = () => {
          const open = panel.hidden;
          panel.hidden = !open;
          tr.classList.toggle("open", open);
          tr.setAttribute("aria-expanded", String(open));
        };
        tr.addEventListener("click", (event) => {
          if (event.target.closest("a, button")) return;
          toggle();
        });
        tr.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            toggle();
          }
        });
      }

      const haystack = (row.search || Object.values(row).map((v) => JSON.stringify(v)).join(" ")).toLowerCase();
      return { tr, panel, haystack, anchor: row.anchor };
    });

    rows.forEach(({ tr, panel }) => {
      body.appendChild(tr);
      if (panel) body.appendChild(panel);
    });

    if (!rows.length) wrap.appendChild(el(`<p class="empty">${escape(block.empty || "Nothing here yet.")}</p>`));

    const input = wrap.querySelector("input");
    const count = wrap.querySelector(".count");
    const filter = () => {
      const needle = (input.value || "").trim().toLowerCase();
      let shown = 0;
      rows.forEach(({ tr, panel, haystack }) => {
        const hit = !needle || haystack.includes(needle);
        tr.hidden = !hit;
        if (panel && !hit) {
          panel.hidden = true;
          tr.classList.remove("open");
          tr.setAttribute("aria-expanded", "false");
        }
        if (hit) shown += 1;
      });
      count.textContent = `${shown} of ${rows.length}`;
    };
    if (input) {
      input.addEventListener("input", filter);
      filter();
    }

    /* Deep link: `#/vocabulary?open=GC-0002` opens and scrolls to one row. */
    if (context.open) {
      const match = rows.find((row) => row.anchor === context.open);
      if (match && match.panel) {
        match.panel.hidden = false;
        match.tr.classList.add("open");
        match.tr.setAttribute("aria-expanded", "true");
        requestAnimationFrame(() => match.tr.scrollIntoView({ block: "center", behavior: "smooth" }));
      }
    }

    return node;
  },

  report(block, context = {}) {
    const open = context.open && block.path.includes(context.open);
    const node = el(
      `<div class="block"><details class="report"${open ? " open" : ""}>` +
        `<summary><span class="rt">${escape(block.title)}` +
        (block.lede ? `<small>${inline(block.lede)}</small>` : "") +
        `</span></summary>` +
        `<div class="body prose"><p class="loading">Loading…</p></div>` +
        `</details></div>`
    );
    const details = node.querySelector("details");
    const body = node.querySelector(".body");
    let loaded = false;
    const load = async () => {
      if (loaded) return;
      loaded = true;
      try {
        const response = await fetch(`data/${block.path}`);
        if (!response.ok) throw new Error(response.status);
        body.innerHTML = render(await response.text());
        context.decorate?.(body);
      } catch (error) {
        body.innerHTML =
          `<p class="note">This report could not be loaded (${escape(error.message)}). ` +
          `It is generated by the project's own commands and lives in ` +
          `<code>data/derived/reports/</code>.</p>`;
      }
    };
    details.addEventListener("toggle", () => details.open && load());
    if (open) load();
    return node;
  },

  network(block, context) {
    return renderNetwork(block, context);
  },

  tree(block, context) {
    return renderTree(block, context);
  },
};

export function renderBlock(block, context = {}) {
  const renderer = renderers[block.kind];
  if (!renderer) {
    return el(`<div class="block note">Unknown block kind “${escape(block.kind)}”.</div>`);
  }
  return renderer(block, context);
}

export function renderBlocks(blocks, context = {}) {
  const fragment = document.createDocumentFragment();
  (blocks || []).forEach((block) => fragment.appendChild(renderBlock(block, context)));
  return fragment;
}
