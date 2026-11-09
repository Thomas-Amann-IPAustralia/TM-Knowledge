/* What the guide's views share: escaping, where a ref's words come from, and how to name it in
   plain words. The explorer's `app.js` is not imported: it starts the explorer's router when it
   loads. The marks and colours are the explorer's (ADR-0130): the Manual a blue square, the Act
   an amber diamond, the Regulations a plum hexagon. */

export const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export const isLaw = (ref) => /^TM[AR]1995\//.test(ref || "");

/** "act", "regs" or "manual". */
export function sourceOf(ref) {
  if ((ref || "").startsWith("TMA1995/")) return "act";
  if ((ref || "").startsWith("TMR1995/")) return "regs";
  return "manual";
}

/** What each source is, in the words a member of the public would use. */
export const SOURCE = {
  act: { name: "Trade Marks Act 1995", short: "The Trade Marks Act", role: "law" },
  regs: { name: "Trade Marks Regulations 1995", short: "The Trade Marks Regulations", role: "law" },
  manual: { name: "Trade Marks Manual of Practice and Procedure", short: "IP Australia’s guidance (the Manual)", role: "guidance, not law" },
};

/** A small mark in the source's shape and colour. */
export const mark = (ref) => `<i class="gd-mk ${sourceOf(ref)}" aria-hidden="true"></i>`;

/** "Trade Marks Act, section 44(1)", "Regulations, regulation 4.13(1)", "Manual, Part 27". A
    Manual passage's own heading replaces its Part once the Manual's text has loaded
    (`headingOf`). */
export function refLabel(ref) {
  ref = String(ref || "");
  let m = ref.match(/^TM([AR])1995\/([a-z]+)([^/]*)(?:\/(.+))?$/);
  if (m) {
    const unit = m[2] === "s" ? "section" : m[2] === "r" ? "regulation" : m[2];
    const def = m[4] ? ` (“${m[4].replace(/-/g, " ")}”)` : "";
    return `${m[1] === "A" ? "Trade Marks Act" : "Trade Marks Regulations"}, ${unit} ${m[3]}${def}`;
  }
  m = ref.match(/^TMM\/Part([0-9]+[A-Za-z]*)/);
  if (m) return `Trade Marks Manual, Part ${m[1]}`;
  return ref;
}

/** A source chip: opens the passage when pressed (the guide's sheet). */
export const refButton = (ref, quote = "") =>
  `<button type="button" class="gd-ref ${sourceOf(ref)}" data-ref="${esc(ref)}"${quote ? ` data-quote="${esc(quote)}"` : ""} title="${esc(SOURCE[sourceOf(ref)].name)}">${mark(ref)}${esc(refLabel(ref))}</button>`;

/** A Manual passage's heading, from `passages.json`: the last part of its heading path. */
export function headingOf(passages, ref) {
  if (!passages) return null;
  const law = passages.legislation[ref];
  if (law) return String(law[2] || "").split(" > ").pop().replace(/^\d+[A-Z]*\s+/, "");
  const row = passages.chunks.find((c) => c[0] === ref);
  return row ? String(row[2] || "").split(" > ").pop() : null;
}

export const clip = (text, n) => {
  const s = String(text || "");
  return s.length > n ? `${s.slice(0, n - 1).replace(/\s+\S*$/, "")}…` : s;
};

export const ICON = {
  /** Tommy Tradecraft's mark: a T on a round tile (the tile is the CSS's). */
  tommy: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 5.5h11v3h-4v10h-3v-10h-4z"/></svg>`,
  bubble: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 6h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-7l-4.5 3v-3H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z"/></svg>`,
  route: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8.2 18H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.8"/></svg>`,
  scale: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v16M8 20h8M5 7h14M5 7l-2.5 5.5a2.5 2.5 0 0 0 5 0zM19 7l-2.5 5.5a2.5 2.5 0 0 0 5 0z"/></svg>`,
  letter: `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="m4 7 8 6 8-6"/></svg>`,
  flag: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 21V4M5 4h11l-2 4 2 4H5"/></svg>`,
  clock: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>`,
  info: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>`,
  fact: `<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="2.5" y="2.5" width="11" height="11" rx="2"/><path d="m5 8.3 2 2 4-4.4"/></svg>`,
  judge: `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2.5v11M5 13.5h6M3 5h10M3 5l-1.8 4a1.9 1.9 0 0 0 3.6 0zM13 5l-1.8 4a1.9 1.9 0 0 0 3.6 0z"/></svg>`,
};
