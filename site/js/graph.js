/* Drawing helpers: a deterministic force layout, SVG construction, pan and zoom,
   and tweening. No graph library — every byte this site serves is in the repo. */

export const SVG = "http://www.w3.org/2000/svg";

export function svg(tag, attrs = {}, parent = null) {
  const node = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}

/** A seeded random number generator, so the same data always lays out the same way. */
export function rng(seed = 7) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Lay nodes out with springs, repulsion and an optional pull towards an anchor.
 * nodes: [{id, r, ax, ay, pull}]  links: [{s, t, w}]
 * Runs to completion before anything is drawn, so nothing jitters on screen.
 */
export function forceLayout(nodes, links, opts = {}) {
  const {
    width = 1000, height = 700, iterations = 320, seed = 11, charge = 900,
    linkDistance = 60, linkStrength = 0.06, gravity = 0.012, padding = 4,
  } = opts;
  const random = rng(seed);
  const index = new Map(nodes.map((n, i) => [n.id, i]));
  for (const n of nodes) {
    if (n.x === undefined) {
      const cx = n.ax ?? width / 2, cy = n.ay ?? height / 2;
      const angle = random() * Math.PI * 2, d = 10 + random() * 60;
      n.x = cx + Math.cos(angle) * d;
      n.y = cy + Math.sin(angle) * d;
    }
    n.vx = 0; n.vy = 0;
  }
  const L = links.map((l) => [index.get(l.s), index.get(l.t), l.w ?? 1]).filter(([a, b]) => a !== undefined && b !== undefined && a !== b);
  for (let it = 0; it < iterations; it++) {
    const alpha = 1 - it / iterations;
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        let dx = b.x - a.x, dy = b.y - a.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 0.01) { dx = random() - 0.5; dy = random() - 0.5; d2 = dx * dx + dy * dy; }
        const d = Math.sqrt(d2);
        const min = (a.r || 5) + (b.r || 5) + padding;
        let f = (charge * alpha) / d2;
        if (d < min) f += (min - d) * 0.5;
        const fx = (dx / d) * f, fy = (dy / d) * f;
        a.vx -= fx; a.vy -= fy; b.vx += fx; b.vy += fy;
      }
    }
    for (const [i, j, w] of L) {
      const a = nodes[i], b = nodes[j];
      const dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const f = (d - linkDistance) * linkStrength * w * alpha;
      const fx = (dx / d) * f, fy = (dy / d) * f;
      a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy;
    }
    for (const n of nodes) {
      const cx = n.ax ?? width / 2, cy = n.ay ?? height / 2;
      const pull = n.pull ?? gravity;
      n.vx += (cx - n.x) * pull;
      n.vy += (cy - n.y) * pull;
      n.vx *= 0.6; n.vy *= 0.6;
      const cap = 30;
      n.x += Math.max(-cap, Math.min(cap, n.vx));
      n.y += Math.max(-cap, Math.min(cap, n.vy));
    }
  }
  return nodes;
}

/** Pan and zoom a <g> inside an <svg> by dragging, the wheel, pinching and buttons. */
export function panZoom(svgEl, target, { min = 0.3, max = 6, onChange = null } = {}) {
  const state = { k: 1, x: 0, y: 0 };
  const apply = () => {
    target.setAttribute("transform", `translate(${state.x},${state.y}) scale(${state.k})`);
    if (onChange) onChange(state);
  };
  const toLocal = (clientX, clientY) => {
    const pt = svgEl.createSVGPoint();
    pt.x = clientX; pt.y = clientY;
    return pt.matrixTransform(svgEl.getScreenCTM().inverse());
  };
  const zoomAt = (factor, px, py) => {
    const k = Math.max(min, Math.min(max, state.k * factor));
    state.x = px - ((px - state.x) * k) / state.k;
    state.y = py - ((py - state.y) * k) / state.k;
    state.k = k;
    apply();
  };
  let drag = null;
  const pointers = new Map();
  svgEl.addEventListener("wheel", (e) => {
    e.preventDefault();
    const p = toLocal(e.clientX, e.clientY);
    zoomAt(Math.exp(-e.deltaY * 0.0015), p.x, p.y);
  }, { passive: false });
  svgEl.addEventListener("pointerdown", (e) => {
    pointers.set(e.pointerId, toLocal(e.clientX, e.clientY));
    if (e.target.closest(".node, .kind-bubble, .psg, .kind-link")) return;
    drag = { start: toLocal(e.clientX, e.clientY), x: state.x, y: state.y, moved: false };
    svgEl.setPointerCapture(e.pointerId);
    svgEl.classList.add("dragging");
  });
  svgEl.addEventListener("pointermove", (e) => {
    const p = toLocal(e.clientX, e.clientY);
    if (pointers.size === 2 && pointers.has(e.pointerId)) {
      const [a, b] = [...pointers.values()];
      const before = Math.hypot(a.x - b.x, a.y - b.y);
      pointers.set(e.pointerId, p);
      const [c, d] = [...pointers.values()];
      const after = Math.hypot(c.x - d.x, c.y - d.y);
      if (before > 0) zoomAt(after / before, (c.x + d.x) / 2, (c.y + d.y) / 2);
      return;
    }
    if (!drag) return;
    state.x = drag.x + (p.x - drag.start.x);
    state.y = drag.y + (p.y - drag.start.y);
    drag.moved = true;
    apply();
  });
  const end = (e) => {
    pointers.delete(e.pointerId);
    drag = null;
    svgEl.classList.remove("dragging");
  };
  svgEl.addEventListener("pointerup", end);
  svgEl.addEventListener("pointercancel", end);
  return {
    state,
    zoom: (factor) => { const vb = svgEl.viewBox.baseVal; zoomAt(factor, vb.width / 2, vb.height / 2); },
    reset: () => { state.k = 1; state.x = 0; state.y = 0; apply(); },
    focus: (x, y, k = 1.6) => {
      const vb = svgEl.viewBox.baseVal;
      state.k = k; state.x = vb.width / 2 - x * k; state.y = vb.height / 2 - y * k;
      apply();
    },
  };
}

/** Tween a set of numbers from `from` to `to`, calling `step(t)` with eased t. */
export function tween(duration, step, done) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced || duration <= 0) { step(1); if (done) done(); return () => {}; }
  const start = performance.now();
  let frame;
  const tick = (now) => {
    const raw = Math.min(1, (now - start) / duration);
    const t = raw < 0.5 ? 4 * raw * raw * raw : 1 - Math.pow(-2 * raw + 2, 3) / 2;
    step(t);
    if (raw < 1) frame = requestAnimationFrame(tick); else if (done) done();
  };
  frame = requestAnimationFrame(tick);
  return () => cancelAnimationFrame(frame);
}

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
