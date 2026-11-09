/* Small drawings for the cards that say what the foundation does now and could do next
   (ADR-0151), and the shared card shapes that hold them.

   Each drawing is decoration (aria-hidden): the card's words say everything the picture shows.
   They are built from a few shapes in the site's own colours, so every card reads as one system:
   documents, the three families of idea (orange, teal, violet), the three sources and their marks
   (the Manual a blue square, the Act an amber diamond, the Regulations a plum hexagon), people,
   ticks and question marks. A drawing never shows a decision about an application. Classes are
   prefixed `il-` (the drawings) and `fc-` (the cards). */

import { esc } from "./app.js";
import { icon } from "./icons.js";

// ------------------------------------------------------------------ shapes

const doc = (x, y, w = 54, h = 68, lines = 4, cls = "") => `<g class="il-doc ${cls}" transform="translate(${x},${y})"><rect width="${w}" height="${h}" rx="6"/>${
  Array.from({ length: lines }, (_, i) => `<rect class="il-txt" x="9" y="${12 + i * 11}" width="${((w - 18) * (i % 3 === 2 ? 0.62 : 1)).toFixed(1)}" height="4" rx="2"/>`).join("")}</g>`;
const dot = (x, y, r, fam = "re", cls = "") => `<circle class="il-dot ${fam} ${cls}" cx="${x}" cy="${y}" r="${r}"/>`;
const ln = (d, cls = "") => `<path class="il-line ${cls}" d="${d}"/>`;
const person = (x, y, s = 1, cls = "") => `<g class="il-person ${cls}" transform="translate(${x},${y}) scale(${s})"><circle cx="0" cy="-15" r="7.5"/><path d="M-13 9 C-13 -5 13 -5 13 9 Z"/></g>`;
const tick = (x, y, r = 8, cls = "") => `<g class="il-ok ${cls}" transform="translate(${x},${y})"><circle r="${r}"/><path d="M${(-r * 0.42).toFixed(1)} 0.5 l${(r * 0.3).toFixed(1)} ${(r * 0.32).toFixed(1)} ${(r * 0.55).toFixed(1)} ${(-r * 0.62).toFixed(1)}"/></g>`;
const query = (x, y, r = 8, cls = "") => `<g class="il-q ${cls}" transform="translate(${x},${y})"><circle r="${r}"/><text y="${(r * 0.42).toFixed(1)}" text-anchor="middle" style="font-size:${(r * 1.25).toFixed(1)}px">?</text></g>`;
const warn = (x, y, r = 8) => `<g class="il-warn" transform="translate(${x},${y})"><circle r="${r}"/><text y="${(r * 0.42).toFixed(1)}" text-anchor="middle" style="font-size:${(r * 1.25).toFixed(1)}px">!</text></g>`;
const chip = (x, y, w, text, cls = "") => `<g class="il-chip ${cls}" transform="translate(${x},${y})"><rect width="${w}" height="20" rx="10"/><text x="${w / 2}" y="13.8" text-anchor="middle">${esc(text)}</text></g>`;
const label = (x, y, text, cls = "", anchor = "start") => `<text class="il-lab ${cls}" x="${x}" y="${y}" text-anchor="${anchor}">${esc(text)}</text>`;
const arrow = (x1, y1, x2, y2, cls = "") => {
  const a = Math.atan2(y2 - y1, x2 - x1), h = 6;
  const p1 = [x2 - h * Math.cos(a - 0.5), y2 - h * Math.sin(a - 0.5)], p2 = [x2 - h * Math.cos(a + 0.5), y2 - h * Math.sin(a + 0.5)];
  return `<path class="il-line ${cls}" d="M${x1} ${y1} L${x2} ${y2} M${p1[0].toFixed(1)} ${p1[1].toFixed(1)} L${x2} ${y2} L${p2[0].toFixed(1)} ${p2[1].toFixed(1)}"/>`;
};
/** A source's mark: the Manual a square, the Act a diamond, the Regulations a hexagon. */
const mark = (x, y, src = "manual", s = 6) => {
  const d = src === "act" ? `M${x} ${y - s * 1.2}L${x + s * 1.2} ${y}L${x} ${y + s * 1.2}L${x - s * 1.2} ${y}Z`
    : src === "regs" ? `M${x - s * .55} ${y - s}L${x + s * .55} ${y - s}L${x + s * 1.1} ${y}L${x + s * .55} ${y + s}L${x - s * .55} ${y + s}L${x - s * 1.1} ${y}Z`
    : `M${x - s * .85} ${y - s * .85}h${s * 1.7}v${s * 1.7}h${-s * 1.7}Z`;
  return `<path class="il-src ${src}" d="${d}"/>`;
};
const bubble = (x, y, w, h, cls = "", tail = "left") => `<g class="il-bubble ${cls}" transform="translate(${x},${y})"><rect width="${w}" height="${h}" rx="10"/>${
  tail === "left" ? `<path d="M12 ${h} l-4 9 12 -9z"/>` : `<path d="M${w - 12} ${h} l4 9 -12 -9z"/>`}</g>`;
const bars = (x, y, values, w = 9, gap = 5, max = 50, cls = "") => values.map((v, i) => `<rect class="il-bar ${cls}" x="${x + i * (w + gap)}" y="${y - (v / 100) * max}" width="${w}" height="${(v / 100) * max}" rx="2"/>`).join("");
/** A fact tile (square corner mark) or an assessment tile (a small scale). */
const tile = (x, y, w, kind = "fact", cls = "") => `<g class="il-tile ${kind} ${cls}" transform="translate(${x},${y})"><rect width="${w}" height="24" rx="6"/>${
  kind === "fact" ? `<rect class="il-tk" x="7" y="8" width="8" height="8" rx="1.5"/>` : `<g class="il-tk-s"><path d="M11 6v12M6 9h10M6 9l-2.5 5h5zM16 9l-2.5 5h5z"/></g>`}<rect class="il-txt" x="22" y="10" width="${w - 32}" height="4" rx="2"/></g>`;

const svg = (body, vb = "0 0 320 150") => `<svg class="il" viewBox="${vb}" aria-hidden="true" focusable="false">${body}</svg>`;

// ------------------------------------------------------------------ the drawings

const DRAWINGS = {
  // ---- the four doors on the overview
  // Examiners: the sources on the left, a lens on one concept, the concepts it connects to on the
  // right. The public: a question, an explanation at the current step, and the journey beneath.
  // Redrawn as single centred emblems like the direction door, on the owner's annotations (ADR-0153).
  "door-exam": () => svg(`${[["act", 42, 44], ["manual", 75, 36], ["regs", 108, 40]].map(([src, y, w]) => `${mark(36, y, src, 6)}<rect class="il-txt" x="48" y="${y - 2.5}" width="${w}" height="5" rx="2.5"/>${ln(`M98 ${y} C 114 ${y} 114 75 128 75`, "faint")}`).join("")}
    ${[[256, 40, "ex"], [274, 75, "pr"], [256, 110, "ex"]].map(([x, y, f]) => `${ln(`M192 75 C 220 75 228 ${y} ${x - 9} ${y}`, "light")}${dot(x, y, 7, f)}`).join("")}
    <g class="il-lens" transform="translate(160,75)"><circle r="31"/><path d="M22 22 l16 16"/></g>${dot(160, 75, 11, "re")}`),
  "door-pub": () => svg(`${ln("M40 120 H280", "track")}${[40, 100, 160, 220, 280].map((x, i) => `<circle class="il-stop${i < 2 ? " done" : i === 2 ? " now" : ""}" cx="${x}" cy="120" r="${i === 2 ? 10 : 7}"/>`).join("")}
    <g class="il-bubble"><rect x="94" y="14" width="132" height="62" rx="12"/><path d="M152 76 l8 11 8 -11z"/></g>${tile(104, 24, 54, "fact")}${tile(162, 24, 54, "assess")}
    <rect class="il-txt" x="106" y="60" width="74" height="5" rx="2.5"/>${mark(198, 62.5, "act", 4.6)}${mark(212, 62.5, "manual", 4.2)}
    ${person(46, 84, 0.9, "accent")}${query(70, 44, 9)}`),
  "door-pol": () => svg(`<g class="il-ripple">${[26, 46, 66].map((r) => `<circle cx="150" cy="78" r="${r}"/>`).join("")}</g>${mark(150, 78, "act", 11)}
    ${[[96, 44, "re"], [204, 46, "ex"], [92, 116, "pr"], [212, 112, "re"], [150, 14, "ex"], [72, 78, "pr"], [230, 80, "ex"]].map(([x, y, f], i) => dot(x, y, i < 4 ? 7 : 5, f)).join("")}
    ${bars(258, 128, [40, 70, 100], 10, 6, 60, "accent")}`),
  "door-nerd": () => svg(`<g class="il-code"><text x="24" y="40">&lt;GL-0001&gt;</text><text x="40" y="62">tmk:condition [ all ]</text><text x="40" y="84">tmk:kind "fact"</text><text x="40" y="106">prov:wasDerivedFrom</text><text x="24" y="128">.</text></g>
    ${dot(250, 50, 9, "re")}${dot(218, 104, 8, "ex")}${dot(282, 106, 8, "pr")}${ln("M250 50 L218 104 M250 50 L282 106 M218 104 L282 106", "light")}`),

  // ---- examiners: working now
  "demo-concepts": () => svg(`${["re", "ex", "ex", "pr"].map((f, i) => `${dot(52, 30 + i * 30, 7, f)}<rect class="il-txt" x="64" y="${27 + i * 30}" width="48" height="5" rx="2.5"/>${ln(`M116 ${30 + i * 30} C 136 ${30 + i * 30} 136 75 152 75`)}`).join("")}
    <g class="il-focus" transform="translate(152,52)"><rect width="76" height="46" rx="10"/><rect class="il-txt" x="12" y="14" width="50" height="6" rx="3"/><rect class="il-txt" x="12" y="27" width="34" height="5" rx="2.5"/></g>
    ${["pr", "ex", "re"].map((f, i) => `${ln(`M228 75 C 244 75 244 ${42 + i * 34} 258 ${42 + i * 34}`)}${dot(266, 42 + i * 34, 7, f)}`).join("")}`),
  "demo-ask": () => svg(`<g class="il-search"><rect x="22" y="18" width="276" height="28" rx="14"/><rect class="il-txt" x="40" y="30" width="150" height="5" rx="2.5"/></g>
    <g class="il-doc"><rect x="22" y="58" width="166" height="76" rx="8"/></g>${[0, 1, 2].map((i) => `<rect class="il-txt" x="34" y="${72 + i * 18}" width="${[120, 132, 96][i]}" height="5" rx="2.5"/>${mark(170, 74 + i * 18, i === 1 ? "act" : "manual", 5)}`).join("")}
    ${[0, 1, 2, 3].map((i) => `${mark(212, 68 + i * 19, i < 1 ? "act" : "manual", 6)}<rect class="il-txt" x="224" y="${66 + i * 19}" width="66" height="5" rx="2.5"/>`).join("")}`),

  // ---- examiners: next
  "related-matters": () => svg(`${doc(132, 38, 56, 72, 4, "accent")}${[[40, 26], [40, 92], [246, 22], [246, 96]].map(([x, y]) => doc(x, y, 40, 50, 3, "small")).join("")}
    ${ln("M132 62 L80 50 M132 88 L80 116 M188 60 L246 46 M188 92 L246 118", "dash")}${dot(160, 124, 6, "re")}${dot(60, 18, 5, "re")}${dot(266, 14, 5, "re")}${dot(60, 84, 5, "ex")}`),
  "consistency-point": () => svg(`${doc(30, 30, 64, 82, 5)}${doc(118, 30, 64, 82, 5)}<text class="il-neq" x="106" y="78" text-anchor="middle">≠</text>
    ${dot(62, 100, 6, "re")}${dot(150, 100, 6, "re")}${arrow(196, 72, 226, 72)}${doc(234, 22, 64, 98, 6, "manualdoc")}${mark(286, 34, "manual", 5)}${person(268, 138, 0.62, "accent")}`),
  learning: () => svg(`${[[34, 112], [94, 90], [154, 98], [214, 70], [272, 46]].map(([x, y], i) => `<ellipse class="il-stone${i < 3 ? " done" : ""}" cx="${x}" cy="${y}" rx="24" ry="9"/>`).join("")}
    ${tick(94, 72, 8)}${tick(154, 80, 8)}${query(214, 52, 8)}${person(36, 96, 0.9, "accent")}${dot(272, 28, 8, "re")}${ln("M34 112 C 60 100 70 96 94 90 C 120 86 130 102 154 98 C 180 94 190 76 214 70 C 238 64 250 52 272 46", "dash")}`),
  preservation: () => svg(`${person(56, 96, 1.2, "accent")}${doc(98, 40, 56, 72, 4)}<g class="il-sign"><path d="M106 100 c8 -10 14 6 22 -4 s 10 -2 16 -6"/></g>
    ${arrow(166, 76, 196, 76)}<g class="il-vault"><rect x="204" y="34" width="96" height="88" rx="10"/><path d="M204 64 h96 M204 94 h96"/><rect class="il-handle" x="240" y="45" width="24" height="7" rx="3.5"/><rect class="il-handle" x="240" y="75" width="24" height="7" rx="3.5"/><rect class="il-handle" x="240" y="105" width="24" height="7" rx="3.5"/></g>${tick(296, 36, 10)}`),
  "change-alerts": () => svg(`${doc(30, 30, 70, 90, 0)}<rect class="il-del" x="40" y="44" width="50" height="6" rx="3"/><rect class="il-ins" x="40" y="58" width="44" height="6" rx="3"/><rect class="il-txt" x="40" y="72" width="50" height="5" rx="2.5"/><rect class="il-txt" x="40" y="84" width="34" height="5" rx="2.5"/>
    ${arrow(108, 74, 140, 74)}<g class="il-bell" transform="translate(172,72)"><path d="M-16 10 h32 l-5 -7 v-12 a11 11 0 0 0 -22 0 v12z"/><circle cy="15" r="3.5"/></g>
    ${ln("M196 72 L238 40 M196 72 L246 78 M196 72 L234 116", "dash")}${dot(246, 38, 8, "re")}${dot(256, 78, 8, "ex")}${dot(244, 118, 8, "pr")}<rect class="il-txt" x="262" y="36" width="34" height="5" rx="2.5"/>`),
  evidence: () => svg(`${doc(30, 22, 92, 110, 0)}${["in Australia", "before filing", "dated"].map((t, i) => `${i < 2 ? tick(48, 46 + i * 30, 7) : query(48, 46 + i * 30, 7)}${label(60, 50 + i * 30, t, "sm")}`).join("")}
    ${tile(150, 40, 132, "fact")}${tile(150, 72, 132, "assess")}${tile(150, 104, 132, "fact")}`),

  // ---- the public: working now
  "demo-objection": () => svg(`<g class="il-letter"><rect x="24" y="24" width="110" height="104" rx="8"/><path d="M24 34 l55 34 55 -34"/></g>${label(40, 104, "SALT & STONE", "mk")}
    ${arrow(146, 76, 172, 76)}${tile(182, 30, 112, "assess")}${tile(182, 60, 112, "fact")}${tile(182, 90, 112, "assess")}${query(288, 72, 7)}${tick(288, 42, 7)}${tick(288, 102, 7)}`),
  "demo-requirements": () => svg(`${label(26, 28, "IF ALL OF", "k")}${tile(26, 36, 82, "assess")}${tile(116, 36, 82, "fact")}${tile(206, 36, 88, "assess")}
    ${label(26, 88, "THEN", "k")}<g class="il-must"><rect x="26" y="96" width="96" height="26" rx="13"/><text x="74" y="113" text-anchor="middle">must</text></g>
    ${label(146, 88, "UNLESS", "k")}<g class="il-may"><rect x="146" y="96" width="70" height="26" rx="13"/><text x="181" y="113" text-anchor="middle">may</text></g><g class="il-maynot"><rect x="224" y="96" width="70" height="26" rx="13"/><text x="259" y="113" text-anchor="middle">may not</text></g>`),
  "demo-journey": () => svg(`${ln("M30 74 H290", "track")}${[30, 92, 154, 216, 290].map((x, i) => `<circle class="il-stop${i < 2 ? " done" : i === 2 ? " now" : ""}" cx="${x}" cy="74" r="${i === 2 ? 11 : 8}"/>`).join("")}
    ${ln("M92 74 C 110 110 136 112 154 112", "branch")}<circle class="il-stop" cx="154" cy="112" r="6"/><g class="il-pin" transform="translate(154,40)"><path d="M0 18 C -12 4 -10 -10 0 -10 C 10 -10 12 4 0 18Z"/><circle cy="-2" r="3.5"/></g>`),

  // ---- the public: next
  assistant: () => svg(`${bubble(150, 16, 146, 30, "user", "right")}<rect class="il-txt" x="164" y="28" width="96" height="5" rx="2.5"/>
    ${bubble(24, 58, 190, 70, "reply")}${tile(36, 68, 80, "fact")}${tile(122, 68, 82, "assess")}<rect class="il-txt" x="38" y="102" width="130" height="5" rx="2.5"/>${mark(184, 104, "act", 5)}${mark(198, 104, "manual", 4.4)}
    ${person(272, 120, 0.9, "accent")}`),
  prefiling: () => svg(`<g class="il-tag"><path d="M28 56 h96 l16 20 -16 20 h-96z"/><circle cx="42" cy="76" r="4"/></g>${label(54, 81, "MY BRAND", "mk")}
    ${[["Does it stand out?", 0], ["Is it like another mark?", 1], ["What does it suggest?", 2]].map(([t, i]) => `${ln(`M144 76 C 170 76 170 ${36 + i * 40} 196 ${36 + i * 40}`)}${query(206, 36 + i * 40, 8)}${label(220, 40 + i * 40, t, "sm")}`).join("")}`),
  "own-report": () => svg(`${doc(28, 22, 80, 108, 7)}<rect class="il-hl" x="34" y="56" width="66" height="9" rx="2"/>${arrow(118, 76, 150, 76)}
    <g class="il-plain"><rect x="158" y="34" width="136" height="84" rx="12"/></g>${tile(170, 46, 112, "assess")}${tile(170, 76, 112, "fact")}<rect class="il-txt" x="172" y="106" width="70" height="5" rx="2.5"/>`),
  "gs-finder": () => svg(`${bubble(22, 30, 128, 40, "user", "right")}${label(36, 54, "“I sell bike parts”", "sm")}${arrow(160, 52, 188, 52)}
    ${["Class 12", "bicycle parts", "Class 35"].map((t, i) => chip(196, 22 + i * 30, i === 1 ? 102 : 70, t, i === 1 ? "hl" : "")).join("")}${person(46, 124, 0.8, "accent")}`),
  "spec-check": () => svg(`${doc(30, 20, 150, 114, 0)}${[0, 1, 2, 3].map((i) => `<rect class="il-txt" x="44" y="${38 + i * 22}" width="${[104, 120, 90, 110][i]}" height="5" rx="2.5"/>`).join("")}
    <path class="il-squiggle" d="M44 72 q5 5 10 0 t10 0 t10 0 t10 0 t10 0 t10 0 t10 0 t10 0 t10 0 t10 0 t10 0"/>${warn(166, 62, 8)}${tick(166, 40, 7)}${tick(166, 106, 7)}
    ${arrow(196, 64, 224, 64)}<g class="il-plain"><rect x="232" y="40" width="64" height="48" rx="10"/></g><rect class="il-txt" x="242" y="56" width="44" height="5" rx="2.5"/><rect class="il-txt" x="242" y="68" width="30" height="5" rx="2.5"/>`),
  readiness: () => svg(`<g class="il-clip"><rect x="94" y="20" width="132" height="116" rx="10"/><rect x="134" y="12" width="52" height="16" rx="5"/></g>
    ${[0, 1, 2, 3].map((i) => `${i === 2 ? warn(116, 48 + i * 22, 7) : tick(116, 48 + i * 22, 7)}<rect class="il-txt" x="130" y="${45 + i * 22}" width="${[70, 80, 60, 74][i]}" height="5" rx="2.5"/>`).join("")}`),
  "non-use": () => svg(`<g class="il-reg"><circle cx="96" cy="72" r="36"/><text x="96" y="84" text-anchor="middle">®</text></g>
    <g class="il-cal" transform="translate(176,34)"><rect width="104" height="82" rx="10"/><path d="M0 22 h104"/>${Array.from({ length: 12 }, (_, i) => `<rect class="il-day" x="${10 + (i % 4) * 23}" y="${30 + Math.floor(i / 4) * 16}" width="16" height="10" rx="2"/>`).join("")}</g>
    <g class="il-dust">${[[60, 30], [130, 34], [140, 112], [52, 114]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2.4"/>`).join("")}</g>`),
  "personal-journey": () => svg(`${ln("M30 92 H290", "track faint")}${[30, 90, 150, 210, 270].map((x, i) => `<circle class="il-stop${i === 2 ? " now" : i === 3 ? " near" : " far"}" cx="${x}" cy="92" r="${i === 2 ? 11 : 7}"/>`).join("")}
    <g class="il-spot"><ellipse cx="180" cy="92" rx="66" ry="30"/></g><g class="il-pin" transform="translate(150,56)"><path d="M0 18 C -12 4 -10 -10 0 -10 C 10 -10 12 4 0 18Z"/><circle cy="-2" r="3.5"/></g>`),

  // ---- direction setting: working now
  "demo-change": () => svg(`<g class="il-ripple">${[30, 52, 72].map((r) => `<circle cx="112" cy="76" r="${r}"/>`).join("")}</g>${mark(112, 76, "act", 10)}
    ${Array.from({ length: 16 }, (_, i) => { const a = (i / 16) * Math.PI * 2, r = i % 2 ? 52 : 72; return dot((112 + r * Math.cos(a)).toFixed(1), (76 + r * Math.sin(a)).toFixed(1), 4, ["re", "ex", "pr"][i % 3]); }).join("")}
    ${bars(222, 128, [100, 72, 54, 40], 12, 8, 86, "accent")}`),
  "demo-whatif": () => svg(`<g class="il-invent"><rect x="86" y="14" width="148" height="30" rx="15"/></g>${label(160, 34, "a new right", "inv", "middle")}
    ${ln("M14 64 H306", "divider")}${ln("M120 44 L74 98 M160 44 L160 98 M200 44 L246 98", "dash")}${dot(74, 104, 8, "re")}${dot(160, 104, 8, "ex")}${dot(246, 104, 8, "pr")}
    ${mark(110, 134, "act", 6)}${mark(210, 134, "act", 6)}${ln("M74 112 L110 128 M160 112 L110 128 M246 112 L210 128", "faint")}`),

  // ---- direction setting: next
  "draft-test": () => svg(`${doc(26, 26, 104, 100, 0)}<rect class="il-txt" x="38" y="42" width="80" height="5" rx="2.5"/><rect class="il-del" x="38" y="56" width="60" height="6" rx="3"/><rect class="il-ins dashed" x="38" y="70" width="74" height="6" rx="3"/><rect class="il-txt" x="38" y="84" width="54" height="5" rx="2.5"/>
    ${arrow(140, 76, 172, 76)}${[0, 1].map((i) => `<g class="il-case"><rect x="180" y="${24 + i * 56}" width="116" height="46" rx="10"/></g>${tile(190, 34 + i * 56, 72, i ? "assess" : "fact")}${i ? query(280, 46 + i * 56, 8) : tick(280, 46, 8)}`).join("")}`),
  "compare-options": () => svg(`${[["Option A", 30], ["Option B", 120], ["Option C", 210]].map(([t, x], i) => `<g class="il-col"><rect x="${x}" y="18" width="80" height="116" rx="10"/></g>${label(x + 40, 38, t, "k", "middle")}${bars(x + 16, 120, [[60, 90, 40], [30, 50, 70], [80, 40, 20]][i], 12, 6, 64, ["", "accent", ""][i])}`).join("")}`),
  monitoring: () => svg(`${ln("M20 104 H300", "track")}${[40, 92, 144, 196].map((x) => `<circle class="il-stop done" cx="${x}" cy="104" r="5"/>`).join("")}
    <g class="il-flag" transform="translate(248,104)"><path d="M0 0 V-52 M0 -52 h30 l-6 9 6 9 h-30"/></g><g class="il-ripple">${[16, 30].map((r) => `<circle cx="248" cy="104" r="${r}"/>`).join("")}</g>${mark(248, 104, "act", 6)}
    ${dot(64, 52, 6, "re")}${dot(110, 40, 6, "ex")}${dot(156, 56, 6, "pr")}${ln("M64 52 L110 40 L156 56", "light")}${warn(196, 40, 8)}`),
  versions: () => svg(`${[0, 1, 2].map((i) => doc(40 + i * 18, 22 + i * 10, 74, 92, 4, i === 2 ? "front" : "back")).join("")}${ln("M170 120 H300", "track")}
    ${[180, 220, 260, 296].map((x) => `<path class="il-tickm" d="M${x} 114 V126"/>`).join("")}<g class="il-pin" transform="translate(240,86)"><path d="M0 18 C -12 4 -10 -10 0 -10 C 10 -10 12 4 0 18Z"/><circle cy="-2" r="3.5"/></g>${label(240, 144, "on this date", "sm", "middle")}`),
  "consistency-guidance": () => svg(`${doc(36, 26, 76, 98, 5, "manualdoc")}${doc(208, 26, 76, 98, 5, "manualdoc")}${mark(100, 38, "manual", 5)}${mark(272, 38, "manual", 5)}
    <rect class="il-hl" x="44" y="72" width="58" height="8" rx="2"/><rect class="il-hl" x="216" y="60" width="58" height="8" rx="2"/>${ln("M104 76 C 150 100 170 40 214 64", "dash")}<text class="il-neq" x="160" y="76" text-anchor="middle">≠</text>${person(160, 136, 0.6, "accent")}`),
  treaties: () => svg(`<g class="il-globe"><circle cx="82" cy="76" r="44"/><ellipse cx="82" cy="76" rx="18" ry="44"/><path d="M38 76 h88 M46 52 h72 M46 100 h72"/></g>
    ${ln("M128 66 C 170 50 190 40 222 40 M128 80 L222 78 M128 92 C 170 104 190 114 222 116", "dash")}${mark(232, 40, "act", 7)}${mark(232, 78, "regs", 7)}${mark(232, 116, "manual", 7)}
    <rect class="il-txt" x="248" y="38" width="44" height="5" rx="2.5"/><rect class="il-txt" x="248" y="76" width="40" height="5" rx="2.5"/><rect class="il-txt" x="248" y="114" width="44" height="5" rx="2.5"/>`),
  "exam-patterns": () => svg(`${[0, 1, 2].map((i) => `<g class="il-col"><rect x="${24 + i * 96}" y="22" width="84" height="108" rx="10"/></g>${label(66 + i * 96, 42, ["Team A", "Team B", "Team C"][i], "k", "middle")}${bars(38 + i * 96, 118, [[50, 60, 55], [40, 90, 30], [52, 58, 50]][i], 14, 6, 64, i === 1 ? "accent" : "")}`).join("")}`),

  // ---- for nerds
  "n-how": () => svg(`${[0, 1, 2, 3, 4].map((i) => `<g class="il-stepbox${i === 2 ? " on" : ""}"><rect x="${22 + i * 58}" y="56" width="46" height="40" rx="9"/></g><text class="il-lab k" x="${45 + i * 58}" y="80" text-anchor="middle">${i + 1}</text>${i < 4 ? arrow(70 + i * 58, 76, 78 + i * 58, 76) : ""}`).join("")}`),
  "n-map": () => svg(`${[[60, 50, "re", 9], [120, 90, "ex", 7], [170, 40, "pr", 8], [220, 100, "re", 6], [262, 54, "ex", 9], [92, 120, "pr", 5], [196, 70, "ex", 5], [140, 60, "re", 5]].map(([x, y, f, r]) => dot(x, y, r, f)).join("")}
    ${ln("M60 50 L120 90 L170 40 L262 54 M120 90 L220 100 L262 54 M60 50 L140 60 L196 70 L220 100 M92 120 L120 90 M196 70 L170 40", "light")}`),
  "n-rules": () => svg(`${label(28, 30, "IF", "k")}${tile(54, 16, 110, "fact")}${tile(172, 16, 120, "assess")}${label(28, 78, "THEN", "k")}<g class="il-must"><rect x="74" y="62" width="110" height="26" rx="13"/><text x="129" y="79" text-anchor="middle">must</text></g>
    ${label(28, 124, "UNLESS", "k")}<g class="il-may"><rect x="90" y="108" width="90" height="26" rx="13"/><text x="135" y="125" text-anchor="middle">may</text></g>`),
  "n-standards": () => svg(`${["JSON", "SPARQL · SHACL", "SKOS · PROV-O", "RDF"].map((t, i) => `<g class="il-layer${i === 3 ? " base" : ""}"><rect x="${60 - i * 8}" y="${16 + i * 30}" width="${200 + i * 16}" height="24" rx="7"/></g>${label(160, 32 + i * 30, t, "k", "middle")}`).join("")}`),
  "n-tables": () => svg(`<g class="il-grid"><rect x="34" y="20" width="252" height="112" rx="10"/>${[0, 1, 2, 3].map((i) => `<path d="M34 ${46 + i * 22} H286"/>`).join("")}<path d="M110 20 V132 M196 20 V132"/></g>
    ${[0, 1, 2, 3].map((i) => `${dot(52, 57 + i * 22, 4, ["re", "ex", "pr", "re"][i])}<rect class="il-txt" x="62" y="${55 + i * 22}" width="38" height="4" rx="2"/><rect class="il-txt" x="120" y="${55 + i * 22}" width="60" height="4" rx="2"/>`).join("")}`),
  "n-results": () => svg(`${ln("M160 20 V130", "zero")}${[[40, 70, 110], [70, 90, 128], [-60, -38, -14]].map(([lo, mid, hi], i) => `<path class="il-ci" d="M${160 + lo} ${46 + i * 34} H${160 + hi}"/><circle class="il-est" cx="${160 + mid}" cy="${46 + i * 34}" r="6"/>`).join("")}${label(150, 144, "worse", "sm", "end")}${label(170, 144, "better", "sm")}`),
  "n-glossary": () => svg(`<g class="il-book"><path d="M160 34 v92 M60 30 c40 -10 70 -2 100 12 c30 -14 60 -22 100 -12 v92 c-40 -10 -70 -2 -100 12 c-30 -14 -60 -22 -100 -12z"/></g><text class="il-aa" x="110" y="90" text-anchor="middle">Aa</text>
    ${[0, 1, 2].map((i) => `<rect class="il-txt" x="178" y="${58 + i * 16}" width="${[60, 48, 54][i]}" height="5" rx="2.5"/>`).join("")}`),
};

export const drawing = (name) => (DRAWINGS[name] ? DRAWINGS[name]() : "");

// ------------------------------------------------------------------ the cards

/** How far off a possibility is, said in words as well as colour. */
export const HORIZON = {
  now: { label: "Working demonstration", cls: "hz-now", note: "A working demonstration on this site." },
  reach: { label: "Builds on current work", cls: "hz-reach", note: "Would need further development and review." },
  data: { label: "Needs more data", cls: "hz-data", note: "Needs information the foundation does not hold yet." },
};

export const horizonPill = (h) => `<span class="hz ${HORIZON[h].cls}">${esc(HORIZON[h].label)}</span>`;

/** A working demonstration: a large card with its drawing, what it does, and a way in. */
export function demoCard({ href, art, k, title, text, points = [], go, state = "", wide = false }) {
  return `<article class="fc-demo${wide ? " wide" : ""}">
    <a class="fc-cover" href="${href}" aria-label="${esc(go)}: ${esc(title)}"></a>
    <div class="fc-art">${drawing(art)}</div>
    <div class="fc-body">
      <div class="fc-top">${horizonPill("now")}${state ? `<span class="fc-state">${esc(state)}</span>` : ""}</div>
      ${k ? `<span class="fc-k">${esc(k)}</span>` : ""}
      <h3>${esc(title)}</h3>
      <p>${text}</p>
      ${points.length ? `<ul class="fc-points">${points.map((p) => `<li>${icon("check")}<span>${p}</span></li>`).join("")}</ul>` : ""}
      <span class="link-arrow fc-go">${esc(go)} ${icon("arrow")}</span>
    </div>
  </article>`;
}

/** A possibility: a smaller card with its drawing, what it would do, what it needs, and its horizon. */
export function possibilityCard({ art, title, text, horizon, needs, builds }) {
  return `<article class="fc-card">
    <div class="fc-art">${drawing(art)}</div>
    <div class="fc-body">
      ${horizonPill(horizon)}
      <h3>${esc(title)}</h3>
      <p>${text}</p>
      ${builds ? `<p class="fc-line"><span>Builds on</span>${builds}</p>` : ""}
      ${needs ? `<p class="fc-line"><span>${horizon === "data" ? "Needs" : "Still needs"}</span>${needs}</p>` : ""}
    </div>
  </article>`;
}

/** A set of possibilities: the first few shown, the rest kept one click away so the working
    demonstrations stay the page's lead (UX review F11). Nothing is dropped. */
export function possibilityGrid(cards, shown = 3) {
  const rest = cards.slice(shown);
  return `<div class="fc-grid">${cards.slice(0, shown).join("")}</div>${rest.length ? `<details class="fc-more">
    <summary>Other possibilities <span class="fc-more-n">${rest.length}</span></summary>
    <div class="fc-grid">${rest.join("")}</div></details>` : ""}`;
}

/** The key to the horizons, said once above a set of possibilities. */
export const horizonKey = (which = ["reach", "data"]) => `<div class="hz-key">${which.map((h) => `<span>${horizonPill(h)}<span>${esc(HORIZON[h].note)}</span></span>`).join("")}</div>`;

/** What the site is, said on every section's first screen so a page can be read on its own. Who
    wrote the records is said by the status strip on every page and by each record's own stamp; the
    owner struck the repeat here (ADR-0153). */
export const aboutLine = (extra = "") => `<p class="au-about">${icon("info")}<span>A proof of concept built from the Trade Marks Act 1995, the Trade Marks Regulations 1995 and IP Australia’s Trade Marks Manual of Practice and Procedure.${extra ? ` ${extra}` : ""}</span></p>`;
