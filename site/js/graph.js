/* Small SVG helpers for the hand-drawn pictures (the tour, the kinds diagram, the
   hop diagram). The map uses Cytoscape and the circles view D3, both vendored (ADR-0119). */

export const SVG = "http://www.w3.org/2000/svg";

/** Create an SVG element with attributes, optionally appended to a parent. */
export function svg(tag, attrs = {}, parent = null) {
  const node = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}

/** Resolve after `ms`, or at once when the reader prefers reduced motion. */
export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : ms));

/** A gently curved path from a to b, stopping short of each end by ra and rb. */
export function curve(a, b, ra = 0, rb = 0, bend = 0.18) {
  const dx = b.x - a.x, dy = b.y - a.y;
  const d = Math.hypot(dx, dy) || 1;
  const ux = dx / d, uy = dy / d;
  const sx = a.x + ux * ra, sy = a.y + uy * ra;
  const ex = b.x - ux * rb, ey = b.y - uy * rb;
  const mx = (sx + ex) / 2 - uy * d * bend, my = (sy + ey) / 2 + ux * d * bend;
  return { d: `M${sx.toFixed(1)},${sy.toFixed(1)} Q${mx.toFixed(1)},${my.toFixed(1)} ${ex.toFixed(1)},${ey.toFixed(1)}`, mx: (sx + 2 * mx + ex) / 4, my: (sy + 2 * my + ey) / 4 };
}

/** An arrowhead marker, defined once per SVG. */
export function arrowDefs(root, id = "arrow") {
  const defs = svg("defs", {}, root);
  const marker = svg("marker", { id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 9, markerHeight: 9, markerUnits: "userSpaceOnUse", orient: "auto-start-reverse" }, defs);
  svg("path", { d: "M0,0 L10,5 L0,10 z", class: "arrowhead" }, marker);
  return defs;
}

/** Wrap a label onto at most `lines` lines of about `width` characters. */
export function wrapText(text, width = 14, lines = 2) {
  const words = String(text).split(/\s+/);
  const out = [];
  let line = "";
  for (const w of words) {
    if ((line + " " + w).trim().length > width && line) { out.push(line); line = w; } else line = (line + " " + w).trim();
  }
  if (line) out.push(line);
  if (out.length > lines) { out.length = lines; out[lines - 1] = out[lines - 1].replace(/.{0,2}$/, "…"); }
  return out;
}
