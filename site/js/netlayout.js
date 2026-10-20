/* Where each idea sits in a picture of the whole ontology, shared by the knowledge map and How it
   works.

   The three families each have a region (the law's questions in the middle, what they are asked
   about to its left, the process to its right), and each kind a spot within its family's region.
   A force layout then lets connected ideas pull together without overlapping. It is seeded and run
   to rest before anything is drawn, so the same data always gives the same picture, and it never
   moves under the reader. Its constants were measured offline against the real data (Q-62): the
   picture's bounding box, the median connection length and the nearest-neighbour distance. */

export const FAMILY_ORDER = ["examined", "reasoning", "process"];

/** Region centres for a unit layout, before fitting: x from 0 to 1000, y from 0 to 640. */
const FAMILY_AT = { examined: [250, 330], reasoning: [520, 300], process: [790, 330], other: [520, 560] };

function hash(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

/** Kind spots: the kinds of a family on a small circle round the family's centre. `squeeze` below
    1 brings the outer families in towards the middle and spreads each family's kinds up and down
    instead, for a frame squarer than the picture's natural one (the map's, at laptop sizes). */
function kindSpots(ontology, squeeze = 1) {
  const spots = new Map();
  for (const family of Object.keys(FAMILY_AT)) {
    const kinds = ontology.kinds.filter((k) => k.family === family);
    const [fx0, fy] = FAMILY_AT[family];
    const fx = FAMILY_AT.reasoning[0] + (fx0 - FAMILY_AT.reasoning[0]) * squeeze;
    const r = kinds.length > 1 ? 70 + 8 * kinds.length : 0;
    kinds.forEach((k, i) => {
      const a = (i / kinds.length) * Math.PI * 2 - Math.PI / 2 + (family === "reasoning" ? Math.PI / kinds.length : 0);
      spots.set(k.id, [fx + r * squeeze * Math.cos(a), fy + (r * 0.8 * Math.sin(a)) / squeeze]);
    });
  }
  return spots;
}

/** The squeeze that makes the picture fill a frame of this shape, names included. Measured
    offline against the real data (Q-62): the picture's width over its height runs from 1.8 at
    no squeeze to about 1.04 at 0.5, near enough in a straight line. */
export const squeezeFor = (width, height) => Math.max(0.55, Math.min(1, ((1.1 * width) / height - 0.28) / 1.52));

/** Positions for every idea, and the size of each node, fitted to `width` × `height` with `pad`. */
export function layoutIdeas(d3, ontology, { width = 1000, height = 640, pad = 40, ticks = 420, squeeze = 1 } = {}) {
  const familyOfKind = new Map(ontology.kinds.map((k) => [k.id, k.family]));
  const spots = kindSpots(ontology, squeeze);
  const ids = new Set(ontology.concepts.map((c) => c.id));
  const nodes = ontology.concepts.map((c) => {
    const [sx, sy] = spots.get(c.kind) || FAMILY_AT.other;
    const h = hash(c.id);
    return { id: c.id, kind: c.kind, family: familyOfKind.get(c.kind) || "other", r: radius(c),
      x: sx + ((h % 1000) / 1000 - 0.5) * 60, y: sy + (((h >>> 10) % 1000) / 1000 - 0.5) * 60, sx, sy };
  });
  const links = ontology.relations.filter((r) => ids.has(r.s) && ids.has(r.o) && r.s !== r.o)
    .map((r) => ({ source: r.s, target: r.o, loose: r.p === "broader" }));
  const sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance((l) => (l.loose ? 46 : 40)).strength((l) => (l.loose ? 0.12 : 0.22)))
    .force("charge", d3.forceManyBody().strength(-46).distanceMax(260))
    .force("collide", d3.forceCollide().radius((d) => d.r + 4).strength(0.9))
    .force("x", d3.forceX((d) => d.sx).strength(0.07))
    .force("y", d3.forceY((d) => d.sy).strength(0.08))
    .alphaDecay(1 - Math.pow(0.001, 1 / ticks))
    .stop();
  for (let i = 0; i < ticks; i++) sim.tick();
  // fit to the frame, keeping the aspect
  const xs = nodes.map((n) => n.x), ys = nodes.map((n) => n.y);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const k = Math.min((width - 2 * pad) / Math.max(1, x1 - x0), (height - 2 * pad) / Math.max(1, y1 - y0));
  const ox = (width - k * (x1 - x0)) / 2, oy = (height - k * (y1 - y0)) / 2;
  const at = new Map(nodes.map((n) => [n.id, { x: ox + (n.x - x0) * k, y: oy + (n.y - y0) * k, r: n.r, family: n.family, kind: n.kind }]));
  return { at, scale: k, links: links.map((l) => ({ s: l.source.id, o: l.target.id, loose: l.loose })) };
}

/** A node's radius grows with how often the Manual names the idea, gently. */
export const radius = (c) => Math.min(13, 4.5 + 1.25 * Math.log2(1 + (c.mentions || 0)));
